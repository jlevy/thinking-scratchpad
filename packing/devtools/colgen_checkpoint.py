"""Column generation with a wall clock, a per-LP-round log, and a checkpoint.

`devtools.run_fractional_colgen` drives one call to
`sqpack.fractional.colgen.generate_adaptive` and reports what it cost. That is
the right shape for a rung that finishes: the library owns the loop, the driver
owns the command line, and nothing in between can change a decision.

It is the wrong shape for a rung that does not finish. `generate_adaptive`
writes its log a *column* round at a time, and at the sides this cell runs -- a
row-generation round at ``L = 5.52`` cost BC-191 14.4 s, so one column round is
a quarter of an hour and more -- a run stopped by a budget in the middle of its
first column round leaves nothing at all: no line in the log, no site set, no
rows, and so nothing the next cell can resume. The rows are the expensive part
(BC-191 measured separation at 76.6 per cent of a round at ``L = 5.52``), and
they are exactly what is lost.

So this module drives the same alternation itself, in chunks:

* the row loop is run through `solve_rows` a few rounds at a time, with
  ``timings=`` for the per-round split and ``deadline=`` for the wall, so every
  LP round reaches the log while the loop is still running;
* between chunks the whole state -- site orbits as exact rationals, the row
  matrix, and the placement each row came from -- is written to a checkpoint a
  later run reloads with ``--resume``;
* the column step is `dual_squares` and `rank_candidates`, unchanged, and the
  finish is the same `rationalise_sites` and freeze.

Chunking is not a change of method. `solve_rows` carries its row set in and
re-solves it on entry, so stopping after ``k`` rounds and calling again returns
the same point the loop was at and continues from it; the only difference is
one extra LP per chunk. `tests/test_colgen_checkpoint.py` holds that equality
against an unchunked run rather than asserting it here.

Nothing here decides a bound. A candidate is frozen only when the row loop
stopped for want of a violated placement, and `devtools.decide_certificate` is
what decides the frozen bytes.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path

import numpy as np

from sqpack.fractional.certificate import Certificate, verify
from sqpack.fractional.colgen import (
    DEFAULT_SCALE,
    Candidate,
    LpSolution,
    Rows,
    SiteSet,
    dual_squares,
    orbit_column,
    rank_candidates,
    rationalise_sites,
    site_counts_for_side,
    site_set_from_grids,
    solve_rows,
)
from sqpack.fractional.generate import net_half_tangents

ANGLE_LIMIT = Fraction(207107, 500000)
DIRECTION_STEPS = 180
SHRINK = Fraction(9977, 10000)


@dataclass(frozen=True, slots=True)
class Settings:
    """Everything the run is, in the units the record quotes."""

    n: int
    outer_side: Fraction
    square_side: Fraction
    grid_counts: tuple[int, ...]
    inset: Fraction
    angle_limit: Fraction
    direction_steps: int
    scale: int
    column_rounds: int
    max_rounds: int
    rows_per_direction: int
    columns_per_round: int
    support_cap: int
    settle: float
    chunk_rounds: int

    def as_dict(self) -> dict[str, object]:
        return {
            "n": self.n,
            "outer_side": str(self.outer_side),
            "square_side": str(self.square_side),
            "grid_counts": list(self.grid_counts),
            "inset": str(self.inset),
            "angle_limit": str(self.angle_limit),
            "direction_steps": self.direction_steps,
            "scale": self.scale,
            "column_rounds": self.column_rounds,
            "max_rounds": self.max_rounds,
            "rows_per_direction": self.rows_per_direction,
            "columns_per_round": self.columns_per_round,
            "support_cap": self.support_cap,
            "settle": self.settle,
            "chunk_rounds": self.chunk_rounds,
        }


@dataclass(slots=True)
class Progress:
    """What has happened so far, in the shape the checkpoint stores."""

    column_index: int = 0
    lp_rounds_done: int = 0
    column_log: list[dict[str, object]] = field(default_factory=list)
    lp_log: list[dict[str, object]] = field(default_factory=list)
    stopped: str = ""
    objective: float = float("inf")
    least_covered: float = float("inf")


# --------------------------------------------------------------------------
# checkpoint
# --------------------------------------------------------------------------


def save_checkpoint(
    path: Path,
    settings: Settings,
    sites: SiteSet,
    rows: Rows,
    progress: Progress,
) -> None:
    """Write the state a later run resumes from, atomically.

    The row matrix is the bulk and its entries are counts of an orbit's members
    a placement covers, so ``uint8`` holds them exactly for any orbit (a D4
    orbit has at most eight points) and stores the 20-thousand-row matrices
    this cell reaches in tens of megabytes rather than hundreds. The dtype is
    asserted on the way out, not assumed.
    """

    matrix = rows.stacked()
    if matrix.size and (matrix.min() < 0 or matrix.max() > 255):
        raise ValueError(f"row coefficients outside uint8: [{matrix.min()}, {matrix.max()}]")
    if matrix.size and not np.array_equal(matrix, np.rint(matrix)):
        raise ValueError("row coefficients are not integral")
    meta = {
        "settings": settings.as_dict(),
        "orbits": [[[str(x), str(y)] for x, y in orbit] for orbit in sites.orbits],
        "progress": {
            "column_index": progress.column_index,
            "lp_rounds_done": progress.lp_rounds_done,
            "column_log": progress.column_log,
            "lp_log": progress.lp_log,
            "stopped": progress.stopped,
            "objective": progress.objective,
            "least_covered": progress.least_covered,
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".partial")
    np.savez_compressed(
        temporary,
        meta=np.array(json.dumps(meta)),
        matrix=matrix.astype(np.uint8),
        directions=np.array(rows.directions, dtype=np.int32),
        centres=np.array(rows.centres, dtype=np.float64).reshape(len(rows.centres), 2),
    )
    temporary.with_suffix(temporary.suffix + ".npz").replace(path)


def load_checkpoint(path: Path) -> tuple[dict[str, object], SiteSet, Rows, Progress]:
    """Read a checkpoint back into the objects the loop runs on."""

    with np.load(path, allow_pickle=False) as data:
        meta = json.loads(str(data["meta"]))
        matrix = np.asarray(data["matrix"], dtype=float)
        directions = [int(value) for value in data["directions"]]
        centres = [(float(u), float(v)) for u, v in data["centres"]]
    outer_side = Fraction(str(meta["settings"]["outer_side"]))
    orbits = tuple(
        tuple((Fraction(x), Fraction(y)) for x, y in orbit) for orbit in meta["orbits"]
    )
    sites = SiteSet(outer_side, orbits)
    rows = Rows(
        directions=directions,
        centres=centres,
        matrix=matrix,
        pending=[],
        keys={row.tobytes() for row in matrix},
    )
    stored = meta["progress"]
    progress = Progress(
        column_index=int(stored["column_index"]),
        lp_rounds_done=int(stored["lp_rounds_done"]),
        column_log=list(stored["column_log"]),
        lp_log=list(stored["lp_log"]),
        stopped=str(stored["stopped"]),
        objective=float(stored["objective"]),
        least_covered=float(stored["least_covered"]),
    )
    return meta["settings"], sites, rows, progress


# --------------------------------------------------------------------------
# the loop
# --------------------------------------------------------------------------


def _emit(handle, text: str) -> None:
    print(text, flush=True)
    if handle is not None:
        handle.write(text + "\n")
        handle.flush()


def row_loop(
    sites: SiteSet,
    settings: Settings,
    half_tangents: tuple[Fraction, ...],
    rows: Rows,
    progress: Progress,
    *,
    deadline: float | None,
    handle,
    checkpoint: Path | None,
):
    """`solve_rows` a chunk at a time, logging and checkpointing between chunks.

    Returns the last `LpSolution` and the number of LP rounds this call spent.
    The round budget ``max_rounds`` is spent across the chunks, not per chunk.
    """

    spent = 0
    solution = None
    while spent < settings.max_rounds:
        if deadline is not None and time.perf_counter() >= deadline:
            break
        allowance = min(settings.chunk_rounds, settings.max_rounds - spent)
        timings: list = []
        solution = solve_rows(
            sites,
            settings.square_side,
            half_tangents,
            rows,
            max_rounds=allowance,
            rows_per_direction=settings.rows_per_direction,
            timings=timings,
            deadline=deadline,
        )
        for timing in timings:
            if timing.index < 0:
                # The warm solve a chunk opens with: it re-solves the rows the
                # previous chunk ended on and does no separation, so it is
                # chunking's whole overhead and is logged as such, never as a
                # round.
                progress.lp_log.append(
                    {
                        "column": progress.column_index,
                        "round": None,
                        "kind": "chunk_warm_lp",
                        "seconds": round(timing.lp_seconds, 3),
                        "rows": timing.rows_held,
                        "objective": timing.objective,
                    }
                )
                continue
            progress.lp_rounds_done += 1
            spent += 1
            progress.lp_log.append(
                {
                    "column": progress.column_index,
                    "round": progress.lp_rounds_done,
                    "kind": "lp_round",
                    "separation_s": round(timing.separation_seconds, 3),
                    "lp_s": round(timing.lp_seconds, 3),
                    "seconds": round(timing.seconds, 3),
                    "rows": timing.rows_held,
                    "added": timing.rows_added,
                    "violated": timing.violated,
                    "support": timing.support,
                    "objective": timing.objective,
                }
            )
        last = [entry for entry in progress.lp_log if entry["kind"] == "lp_round"]
        if last:
            entry = last[-1]
            _emit(
                handle,
                f"  lp {entry['round']:>4}: rows={entry['rows']:>6} "
                f"added={entry['added']:>5} support={entry['support']:>5} "
                f"obj={entry['objective']:.6f} least_covered={solution.least_covered:.6f} "
                f"sep={entry['separation_s']:.2f}s lp={entry['lp_s']:.2f}s",
            )
        progress.objective = solution.objective
        progress.least_covered = solution.least_covered
        if checkpoint is not None:
            save_checkpoint(checkpoint, settings, sites, rows, progress)
        if solution.converged or not solution.stopped.startswith("round limit"):
            # Converged, out of clock, or refused. Only a spent round budget
            # inside the chunk is a reason to go round again.
            break
    return solution, spent


def run(
    settings: Settings,
    *,
    log_path: Path | None,
    checkpoint: Path | None,
    resume: Path | None,
    freeze: Path | None,
    deadline_seconds: float | None,
    verify_serial: bool,
) -> dict[str, object]:
    started = time.perf_counter()
    deadline = None if deadline_seconds is None else started + deadline_seconds
    half_tangents = net_half_tangents(settings.angle_limit, settings.direction_steps)
    if resume is not None:
        _, sites, rows, progress = load_checkpoint(resume)
    else:
        sites = site_set_from_grids(settings.outer_side, settings.grid_counts, settings.inset)
        rows = Rows()
        progress = Progress()
    handle = log_path.open("a") if log_path is not None else None
    solution = None
    # The last column round whose row loop stopped for want of a violated
    # placement, with the site set that round was solved on. A run whose clock
    # runs out between column rounds has still *reached* a converged restricted
    # optimum, and the weights that reached it are the candidate. Keeping only
    # the live `solution` would discard both the moment the deadline landed,
    # which would report a converged point as an unconverged one and freeze
    # nothing -- the whole reason this driver exists is that a budget stop
    # should cost the run its next round and not its last answer.
    settled: tuple[LpSolution, SiteSet, int] | None = None
    try:
        _emit(handle, json.dumps(settings.as_dict()))
        while progress.column_index < settings.column_rounds:
            index = progress.column_index
            column_started = time.perf_counter()
            _emit(
                handle,
                f"column {index}: orbits={len(sites.orbits)} sites={sites.size} "
                f"rows={len(rows)} starting",
            )
            solution, spent = row_loop(
                sites,
                settings,
                half_tangents,
                rows,
                progress,
                deadline=deadline,
                handle=handle,
                checkpoint=checkpoint,
            )
            if solution is None:
                progress.stopped = "no clock for a single row-generation chunk"
                break
            seconds = time.perf_counter() - column_started
            note = solution.stopped
            depth = float("nan")
            cost = float("nan")
            found: list[Candidate] = []
            pricing_seconds = 0.0
            if solution.converged:
                pricing_started = time.perf_counter()
                weighted = dual_squares(
                    rows,
                    solution.duals,
                    half_tangents,
                    settings.outer_side,
                    settings.square_side,
                    support_cap=settings.support_cap,
                )
                found = rank_candidates(sites, weighted, wanted=settings.columns_per_round)
                pricing_seconds = time.perf_counter() - pricing_started
                if found:
                    depth = float(found[0].averaged_depth)
                    cost = float(found[0].cost)
                    note = f"adding {len(found)} orbits, deepest at {found[0].point}"
                else:
                    note = "no candidate orbit has averaged depth above 1"
            progress.column_log.append(
                {
                    "index": index,
                    "rows": len(rows),
                    "orbits": len(sites.orbits),
                    "sites": sites.size,
                    "lp_rounds": spent,
                    "objective": solution.objective,
                    "least_covered": solution.least_covered,
                    "averaged_depth": depth,
                    "reduced_cost": cost,
                    "added": len(found),
                    "seconds": round(seconds, 3),
                    "pricing_seconds": round(pricing_seconds, 3),
                    "note": note,
                }
            )
            _emit(
                handle,
                f"column {index}: rows={len(rows)} orbits={len(sites.orbits)} "
                f"sites={sites.size} lp_rounds={spent} "
                f"objective={solution.objective:.9f} depth={depth:.9f} "
                f"cost={cost:.9f} least_covered={solution.least_covered:.9f} "
                f"seconds={seconds:.1f} pricing={pricing_seconds:.1f} | {note}",
            )
            progress.stopped = solution.stopped
            progress.objective = solution.objective
            progress.least_covered = solution.least_covered
            if solution.converged:
                settled = (solution, sites, index)
            if checkpoint is not None:
                save_checkpoint(checkpoint, settings, sites, rows, progress)
            if (
                not solution.converged
                or not found
                or found[0].averaged_depth <= 1 + settings.settle
                or index + 1 == settings.column_rounds
            ):
                break
            sites = SiteSet(settings.outer_side, (*sites.orbits, *(c.orbit for c in found)))
            for candidate in found:
                rows.add_column(
                    orbit_column(rows, candidate.orbit, half_tangents, settings.square_side)
                )
            progress.column_index = index + 1
            if checkpoint is not None:
                save_checkpoint(checkpoint, settings, sites, rows, progress)

        seconds = time.perf_counter() - started
        # `converged` is a statement about the row loop -- that the restricted
        # optimum reported is the site set's own and not a point the clock
        # stopped at. Whether the *column* loop converged is the separate
        # question of whether the dual still prices an orbit worth adding, and
        # conflating the two is what would let a site set that is still moving
        # be reported as a finished search.
        column_converged = bool(
            settled is not None
            and progress.column_log
            and str(progress.column_log[-1]["note"]).startswith("no candidate orbit")
        )
        # What the *record* knows, as against what this process holds. A resumed
        # leg that runs no round of its own still carries a checkpoint whose
        # column rounds converged, and reporting only ``converged`` would print
        # "False" over a table of converged rounds. It cannot freeze them --
        # the weights are not in the checkpoint, only the rows and the sites --
        # so the two are reported as two things and never as one.
        settled_rounds = [
            entry
            for entry in progress.column_log
            if not str(entry["note"]).startswith(("deadline reached", "round limit"))
        ]
        result: dict[str, object] = {
            "settings": settings.as_dict(),
            "seconds": seconds,
            "stopped": progress.stopped,
            "converged": settled is not None,
            "column_loop_converged": column_converged,
            "converged_at_column": None if settled is None else settled[2],
            "checkpoint_column_rounds": len(settled_rounds),
            "checkpoint_optimum": (
                None if not settled_rounds else settled_rounds[-1]["objective"]
            ),
            "objective": progress.objective,
            "least_covered": progress.least_covered,
            "lp_rounds": progress.lp_rounds_done,
            "rounds": progress.column_log,
            "lp_log": progress.lp_log,
            "checkpoint": str(checkpoint) if checkpoint is not None else None,
            "total_mass": None,
            "total_mass_float": None,
            "atoms": 0,
            "least_cell_mass": None,
            "frozen": None,
        }
        if settled is None:
            return result
        solution, sites, _ = settled
        result["objective"] = solution.objective
        result["least_covered"] = solution.least_covered

        atoms = rationalise_sites(sites, solution.weights, scale=settings.scale)
        if not atoms:
            result["stopped"] = "every site rounded to zero weight"
            return result
        candidate_certificate = Certificate(
            n=settings.n,
            outer_side=settings.outer_side,
            square_side=settings.square_side,
            atoms=atoms,
            half_tangents=half_tangents,
        )
        result["total_mass"] = str(candidate_certificate.total_mass)
        result["total_mass_float"] = float(candidate_certificate.total_mass)
        result["atoms"] = len(atoms)
        _emit(
            handle,
            f"rationalised total {candidate_certificate.total_mass} "
            f"= {float(candidate_certificate.total_mass):.9f} "
            f"against LP optimum {solution.objective:.9f} over {len(atoms)} atoms",
        )
        least_cell_mass: str | None = None
        if verify_serial:
            # One worker, never the pool: a lane holding one core must not
            # start a parallel sweep, and this only fills the declaration.
            verdict = verify(candidate_certificate, workers=1)
            least_cell_mass = str(verdict.minimum_cell_mass)
            result["least_cell_mass"] = least_cell_mass
            result["in_memory_accepted"] = verdict.accepted
            result["in_memory_failures"] = list(verdict.failures)
            _emit(
                handle,
                f"one-worker sweep: accepted={verdict.accepted} "
                f"failures={verdict.failures} least cell mass {least_cell_mass}",
            )
        if freeze is not None:
            freeze.parent.mkdir(parents=True, exist_ok=True)
            freeze.write_text(certificate_json(candidate_certificate, least_cell_mass))
            result["frozen"] = str(freeze)
        return result
    finally:
        if handle is not None:
            handle.close()


def certificate_json(certificate: Certificate, least_cell_mass: str | None) -> str:
    """The retained on-disk shape, byte-identical in structure to `cases/*`.

    ``least_cell_mass`` is a declaration and not a decision: it stays null when
    nothing has computed it, so a frozen candidate never carries a number no
    run produced.
    """

    record: dict[str, object] = {
        "id": f"C-n{certificate.n:03d}-fractional-"
        f"{certificate.outer_side.numerator}-{certificate.outer_side.denominator}",
        "n": certificate.n,
        "claim": f"s({certificate.n}) >= {certificate.bounded_side}",
        "outer_side": str(certificate.outer_side),
        "square_side": str(certificate.square_side),
        "angle_limit": str(certificate.half_tangents[-1]),
        "direction_steps": len(certificate.half_tangents) - 1,
        "total_mass": str(certificate.total_mass),
        "least_cell_mass": least_cell_mass,
        "symmetry": certificate.symmetry,
        "atoms": [[str(atom.x), str(atom.y), str(atom.weight)] for atom in certificate.atoms],
    }
    return json.dumps(record, indent=1) + "\n"


def counts_for(text: str, outer_side: Fraction, square_side: Fraction) -> tuple[int, ...]:
    """``auto`` holds BC-191's site density; anything else is an explicit tuple."""

    if text == "auto":
        return site_counts_for_side(outer_side, square_side)
    return tuple(int(part) for part in text.split(",") if part)


def show(path: Path) -> str:
    """The per-LP-round and per-column-round tables a checkpoint carries.

    A run this long is read while it is still running, and the checkpoint is
    the only place that holds every round: the log carries one line per chunk
    so that tailing it stays cheap. Reading is a separate command from running
    so that watching a run can never perturb it.
    """

    _, sites, rows, progress = load_checkpoint(path)
    lines = [
        f"checkpoint {path}",
        (
            f"  column {progress.column_index}, {len(sites.orbits)} orbits, "
            f"{sites.size} sites, {len(rows)} rows, {progress.lp_rounds_done} lp rounds"
        ),
        f"  objective {progress.objective:.9f}  least covered {progress.least_covered:.9f}",
        "",
        (
            f"{'col':>4} {'lp':>5} {'rows':>7} {'added':>6} {'support':>8} "
            f"{'objective':>13} {'sep_s':>8} {'lp_s':>8}"
        ),
    ]
    for entry in progress.lp_log:
        if entry["kind"] != "lp_round":
            continue
        lines.append(
            f"{entry['column']:>4} {entry['round']:>5} {entry['rows']:>7} "
            f"{entry['added']:>6} {entry['support']:>8} {entry['objective']:>13.6f} "
            f"{entry['separation_s']:>8.2f} {entry['lp_s']:>8.2f}"
        )
    warm = [entry for entry in progress.lp_log if entry["kind"] == "chunk_warm_lp"]
    overhead = sum(float(str(entry["seconds"])) for entry in warm)
    lines.append(f"chunking overhead: {len(warm)} warm solves, {overhead:.1f} s")
    lines.append("")
    lines.extend(cost_lines(progress))
    if progress.column_log:
        lines.append("")
        lines.append(column_table({"rounds": progress.column_log}))
    return "\n".join(lines)


def cost_lines(progress: Progress, *, window: int = 29, tail: int = 8) -> list[str]:
    """Seconds per row-generation round, in the windows a cost model is read on.

    A single mean over a whole row loop is the wrong number to compare against
    BC-191's ``0.0189 * L^3.657``: the cost of a round grows *within* the loop,
    because separation is priced on the support and the LP on the rows held, and
    both grow every round. That law was fitted on runs of a few dozen rounds, so
    the mean over the first ``window`` rounds is what is comparable to it, and
    the mean over the last ``tail`` rounds is what prices the rounds still to
    come. Reporting one mean for the whole loop conflates the two.
    """

    rounds = [entry for entry in progress.lp_log if entry["kind"] == "lp_round"]
    if not rounds:
        return ["cost: no row-generation round has finished"]

    def mean(subset: list[dict[str, object]], key: str) -> float:
        return sum(float(str(entry[key])) for entry in subset) / len(subset)

    out = [
        f"{'window':>18} {'rounds':>7} {'sec/round':>10} {'sep':>8} {'lp':>8} {'sep share':>10}"
    ]
    for name, subset in (
        ("all", rounds),
        (f"first {window}", rounds[:window]),
        (f"last {tail}", rounds[-tail:]),
    ):
        if not subset:
            continue
        separation = mean(subset, "separation_s")
        lp = mean(subset, "lp_s")
        out.append(
            f"{name:>18} {len(subset):>7} {separation + lp:>10.3f} "
            f"{separation:>8.3f} {lp:>8.3f} {separation / (separation + lp):>10.4f}"
        )
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--show",
        type=Path,
        default=None,
        help="print a checkpoint's round tables and exit, running nothing",
    )
    parser.add_argument("--n", type=int)
    parser.add_argument("--side", type=Fraction, help="container side L")
    parser.add_argument("--shrink", type=Fraction, default=SHRINK, help="square side B")
    parser.add_argument("--grid-counts", default="auto")
    parser.add_argument("--inset", type=Fraction, default=Fraction(1, 2))
    parser.add_argument("--angle-limit", type=Fraction, default=ANGLE_LIMIT)
    parser.add_argument("--direction-steps", type=int, default=DIRECTION_STEPS)
    parser.add_argument("--scale", type=int, default=DEFAULT_SCALE)
    parser.add_argument("--column-rounds", type=int, default=8)
    parser.add_argument("--max-rounds", type=int, default=60)
    parser.add_argument("--rows-per-direction", type=int, default=3)
    parser.add_argument("--columns-per-round", type=int, default=1)
    parser.add_argument("--support-cap", type=int, default=32)
    parser.add_argument("--settle", type=float, default=0.0)
    parser.add_argument("--chunk-rounds", type=int, default=8)
    parser.add_argument("--deadline-seconds", type=float, default=None)
    parser.add_argument("--log", type=Path, default=None)
    parser.add_argument("--checkpoint", type=Path, default=None)
    parser.add_argument("--resume", type=Path, default=None)
    parser.add_argument("--freeze", type=Path, default=None)
    parser.add_argument("--json", type=Path, default=None)
    parser.add_argument("--verify-serial", action="store_true")
    args = parser.parse_args(argv)
    if args.show is not None:
        print(show(args.show), flush=True)
        return 0
    if args.n is None or args.side is None:
        parser.error("--n and --side are required unless --show is given")

    settings = Settings(
        n=args.n,
        outer_side=args.side,
        square_side=args.shrink,
        grid_counts=counts_for(args.grid_counts, args.side, args.shrink),
        inset=args.inset,
        angle_limit=args.angle_limit,
        direction_steps=args.direction_steps,
        scale=args.scale,
        column_rounds=args.column_rounds,
        max_rounds=args.max_rounds,
        rows_per_direction=args.rows_per_direction,
        columns_per_round=args.columns_per_round,
        support_cap=args.support_cap,
        settle=args.settle,
        chunk_rounds=args.chunk_rounds,
    )
    result = run(
        settings,
        log_path=args.log,
        checkpoint=args.checkpoint,
        resume=args.resume,
        freeze=args.freeze,
        deadline_seconds=args.deadline_seconds,
        verify_serial=args.verify_serial,
    )
    print(column_table(result), flush=True)
    print(
        f"stopped: {result['stopped']}\n"
        f"converged here: {result['converged']} "
        f"(this process holds the weights and can freeze)\n"
        f"converged column rounds on record: {result['checkpoint_column_rounds']}, "
        f"last restricted optimum {result['checkpoint_optimum']}\n"
        f"column loop converged: {result['column_loop_converged']}\n"
        f"objective: {result['objective']}\n"
        f"least covered mass: {result['least_covered']}\n"
        f"lp rounds: {result['lp_rounds']}\n"
        f"total mass: {result['total_mass']} = {result['total_mass_float']}\n"
        f"least cell mass: {result['least_cell_mass']}\n"
        f"atoms: {result['atoms']}\n"
        f"frozen: {result['frozen']}\n"
        f"checkpoint: {result['checkpoint']}\n"
        f"seconds: {result['seconds']:.1f}",
        flush=True,
    )
    if args.json is not None:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(result, indent=1) + "\n")
    return 0


def column_table(result: dict[str, object]) -> str:
    header = (
        f"{'col':>4} {'rows':>7} {'orbits':>7} {'sites':>7} {'lp':>5} "
        f"{'objective':>13} {'least_covered':>13} {'depth':>10} {'seconds':>9}  note"
    )
    lines = [header, "-" * len(header)]
    rounds = result["rounds"]
    assert isinstance(rounds, list)
    lines.extend(
        f"{entry['index']:>4} {entry['rows']:>7} {entry['orbits']:>7} "
        f"{entry['sites']:>7} {entry['lp_rounds']:>5} {entry['objective']:>13.6f} "
        f"{entry['least_covered']:>13.6f} {entry['averaged_depth']:>10.6f} "
        f"{entry['seconds']:>9.1f}  {entry['note']}"
        for entry in rounds
    )
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
