#!/usr/bin/env python3
"""Price the column generator: where a round goes, what a site grid costs, what a
rationalisation scale costs.

Three questions, one harness, because all three are the same run with a different
thing held fixed. ``rounds`` splits a row-generation round into separation and LP
so the 79-to-94-per-cent baseline in ``BC-191`` can be rechecked at any side.
``density`` runs the same case at several site grids and reports what each one
buys and what it costs, which is what a site-density rule has to be fitted to.
``scale`` solves once and rationalises the *same* LP point at several scales, so
the rounding loss, the margin and the verification cost are compared on one
solution rather than across runs that would differ for other reasons.

Nothing here decides a bound. ``scale`` calls the exact verifier because
verification cost is the quantity being measured, and its verdicts are about an
in-memory object; retention still goes through ``devtools.decide_certificate``
on frozen bytes.

Usage:
    uv run --frozen python -m devtools.bench_colgen rounds --n 12 --side 99/25
    uv run --frozen python -m devtools.bench_colgen density --n 20 --side 24/5 \
        --grids 23,31,39 --grids 29,39,49
    uv run --frozen python -m devtools.bench_colgen scale --n 12 --side 97/25 \
        --scales 200000,1000000,4000000
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections.abc import Sequence
from dataclasses import asdict, dataclass, field
from fractions import Fraction
from pathlib import Path

import numpy as np

from sqpack.fractional.certificate import Certificate, verify
from sqpack.fractional.colgen import (
    RoundTiming,
    Rows,
    SiteSet,
    dual_squares,
    rank_candidates,
    rationalise_sites,
    site_counts_for_side,
    site_set_from_grids,
    solve_rows,
)
from sqpack.fractional.generate import net_half_tangents
from sqpack.fractional.sweep import weight_scale

#: The net every retained fractional certificate carries. Held as the default so
#: a benchmark run is comparable with the run logs it is being read against.
ANGLE_LIMIT = Fraction(207107, 500000)
DIRECTION_STEPS = 180
SQUARE_SIDE = Fraction(9977, 10000)


@dataclass(slots=True)
class Case:
    """One instance of the covering program, as the generator sees it."""

    n: int
    outer_side: Fraction
    square_side: Fraction = SQUARE_SIDE
    angle_limit: Fraction = ANGLE_LIMIT
    direction_steps: int = DIRECTION_STEPS
    inset: Fraction = Fraction(1, 2)

    def half_tangents(self) -> tuple[Fraction, ...]:
        return net_half_tangents(self.angle_limit, self.direction_steps)

    def label(self) -> str:
        return f"n={self.n} L={self.outer_side}={float(self.outer_side):.4f}"


def density_of(
    outer_side: Fraction, square_side: Fraction, count: int, inset: Fraction
) -> float:
    """Sites per ``B``-square width for one grid count: ``B / spacing``."""

    span = outer_side - 2 * inset
    return float(square_side * (count - 1) / span)


@dataclass(slots=True)
class RowRun:
    """One ``solve_rows`` call, timed."""

    grids: tuple[int, ...]
    densities: tuple[float, ...]
    orbits: int
    sites: int
    rows_per_direction: int
    max_rounds: int
    rounds: int
    rows: int
    objective: float
    stopped: str
    seconds: float
    separation_seconds: float
    lp_seconds: float
    separation_share: float
    peak_support: int = 0
    timings: list[dict[str, float | int]] = field(default_factory=list)


def _row_run(
    case: Case,
    grids: tuple[int, ...],
    *,
    max_rounds: int,
    rows_per_direction: int,
    keep_timings: bool = True,
    deadline_seconds: float | None = None,
) -> tuple[RowRun, SiteSet, Rows, object]:
    """Row-generate once on a fresh site set, returning the run and its state."""

    sites = site_set_from_grids(case.outer_side, grids, case.inset)
    rows = Rows()
    timings: list[RoundTiming] = []
    started = time.perf_counter()
    solution = solve_rows(
        sites,
        case.square_side,
        case.half_tangents(),
        rows,
        max_rounds=max_rounds,
        rows_per_direction=rows_per_direction,
        timings=timings,
        deadline=None if deadline_seconds is None else started + deadline_seconds,
    )
    elapsed = time.perf_counter() - started
    separation = sum(entry.separation_seconds for entry in timings)
    lp = sum(entry.lp_seconds for entry in timings)
    run = RowRun(
        grids=grids,
        densities=tuple(
            round(density_of(case.outer_side, case.square_side, count, case.inset), 3)
            for count in grids
        ),
        orbits=len(sites.orbits),
        sites=sites.size,
        rows_per_direction=rows_per_direction,
        max_rounds=max_rounds,
        rounds=solution.rounds,
        rows=len(rows),
        objective=solution.objective,
        stopped=solution.stopped,
        seconds=round(elapsed, 3),
        separation_seconds=round(separation, 3),
        lp_seconds=round(lp, 3),
        separation_share=round(separation / (separation + lp), 4) if separation + lp else 0.0,
        peak_support=max((entry.support for entry in timings), default=0),
        timings=[
            {
                "index": entry.index,
                "separation_s": round(entry.separation_seconds, 3),
                "lp_s": round(entry.lp_seconds, 3),
                "rows_held": entry.rows_held,
                "rows_added": entry.rows_added,
                "violated": entry.violated,
                "support": entry.support,
                "objective": round(entry.objective, 6),
            }
            for entry in timings
        ]
        if keep_timings
        else [],
    )
    return run, sites, rows, solution


def bench_rounds(
    case: Case,
    grids: tuple[int, ...],
    *,
    max_rounds: int = 60,
    rows_per_direction: int = 3,
    price: bool = True,
    support_cap: int = 32,
    deadline_seconds: float | None = None,
) -> dict[str, object]:
    """Time one row-generation run and, on convergence, the pricing step after it."""

    run, sites, rows, solution = _row_run(
        case,
        grids,
        max_rounds=max_rounds,
        rows_per_direction=rows_per_direction,
        deadline_seconds=deadline_seconds,
    )
    report: dict[str, object] = {"case": case.label(), "row_run": asdict(run)}
    if price and getattr(solution, "converged", False):
        started = time.perf_counter()
        weighted = dual_squares(
            rows,
            solution.duals,  # type: ignore[attr-defined]
            case.half_tangents(),
            case.outer_side,
            case.square_side,
            support_cap=support_cap,
        )
        dual_seconds = time.perf_counter() - started
        started = time.perf_counter()
        found = rank_candidates(sites, weighted, wanted=1)
        rank_seconds = time.perf_counter() - started
        report["pricing"] = {
            "dual_squares_s": round(dual_seconds, 3),
            "rank_candidates_s": round(rank_seconds, 3),
            "total_s": round(dual_seconds + rank_seconds, 3),
            "support": len(weighted),
            "candidates": len(found),
            "best_averaged_depth": float(found[0].averaged_depth) if found else None,
            "share_of_round": round(
                (dual_seconds + rank_seconds) / max(run.seconds, 1e-9),
                4,
            ),
        }
    return report


def bench_density(
    case: Case,
    grid_sets: Sequence[tuple[int, ...]],
    *,
    max_rounds: int = 60,
    rows_per_direction: int = 3,
    deadline_seconds: float | None = None,
) -> dict[str, object]:
    """The same case at several site grids: what each buys and what it costs."""

    runs = []
    for grids in grid_sets:
        run, _sites, _rows, _solution = _row_run(
            case,
            grids,
            max_rounds=max_rounds,
            rows_per_direction=rows_per_direction,
            deadline_seconds=deadline_seconds,
        )
        runs.append(asdict(run))
        print(
            f"  grids={grids} densities={run.densities} orbits={run.orbits} "
            f"rounds={run.rounds} rows={run.rows} support={run.peak_support} "
            f"obj={run.objective:.6f} "
            f"time={run.seconds:.1f}s (sep {run.separation_seconds:.1f}s, "
            f"lp {run.lp_seconds:.1f}s) | {run.stopped}",
            flush=True,
        )
    return {"case": case.label(), "runs": runs}


@dataclass(slots=True)
class ScaleRun:
    """One rationalisation of a fixed LP point, with what it cost to verify."""

    scale: int
    atoms: int
    total_mass: str
    total_mass_float: float
    margin: float
    loss: float
    common_scale: int
    scaled_total: int
    integer_route: bool
    verify_seconds: float
    accepted: bool
    least_cell_mass: str
    failures: tuple[str, ...]


def bench_scale(
    case: Case,
    grids: tuple[int, ...],
    scales: Sequence[int],
    *,
    max_rounds: int = 60,
    rows_per_direction: int = 3,
    verify_scales: Sequence[int] | None = None,
    deadline_seconds: float | None = None,
) -> dict[str, object]:
    """Solve once, rationalise at each scale, and price the verification.

    One LP point for every scale is the whole design: rounding loss, margin and
    verification cost then differ only by the scale, and a difference between two
    rows of the table is caused by the thing the table varies.
    """

    run, sites, _rows, solution = _row_run(
        case,
        grids,
        max_rounds=max_rounds,
        rows_per_direction=rows_per_direction,
        deadline_seconds=deadline_seconds,
    )
    report: dict[str, object] = {"case": case.label(), "row_run": asdict(run)}
    if not getattr(solution, "converged", False):
        report["scales"] = []
        report["note"] = "row generation did not converge: no LP point to rationalise"
        return report
    weights = solution.weights  # type: ignore[attr-defined]
    objective = float(solution.objective)  # type: ignore[attr-defined]
    wanted = set(verify_scales) if verify_scales is not None else set(scales)
    results: list[dict[str, object]] = []
    for scale in scales:
        atoms = rationalise_sites(sites, weights, scale=scale)
        certificate = Certificate(
            n=case.n,
            outer_side=case.outer_side,
            square_side=case.square_side,
            atoms=atoms,
            half_tangents=case.half_tangents(),
        )
        total = certificate.total_mass
        common = weight_scale(atoms)
        scaled_total = int(total * common)
        accepted = False
        least = ""
        failures: tuple[str, ...] = ()
        seconds = float("nan")
        if scale in wanted:
            started = time.perf_counter()
            # One process, always. The parallel schedule would make the timing a
            # statement about the machine's core count rather than about the
            # scale, and a benchmark lane does not get to take cores it was not
            # given.
            verdict = verify(certificate, workers=1)
            seconds = time.perf_counter() - started
            accepted = verdict.accepted
            least = str(verdict.minimum_cell_mass)
            failures = verdict.failures
        entry = ScaleRun(
            scale=scale,
            atoms=len(atoms),
            total_mass=str(total),
            total_mass_float=float(total),
            margin=case.n - float(total),
            loss=float(total) - objective,
            common_scale=common,
            scaled_total=scaled_total,
            integer_route=scaled_total < 2**60,
            verify_seconds=round(seconds, 3),
            accepted=accepted,
            least_cell_mass=least,
            failures=failures,
        )
        results.append(asdict(entry))
        print(
            f"  scale={scale:>9} atoms={entry.atoms} total={entry.total_mass_float:.9f} "
            f"margin={entry.margin:+.6f} loss={entry.loss:.6f} "
            f"common={common} scaled_total={scaled_total} int64={entry.integer_route} "
            f"verify={entry.verify_seconds}s accepted={entry.accepted} "
            f"least={entry.least_cell_mass}",
            flush=True,
        )
    report["lp_objective"] = objective
    report["scales"] = results
    return report


def _power_fit(pairs: list[tuple[float, float]]) -> dict[str, float]:
    """Least squares in logs: ``y = c x^p``, with the worst relative residual."""

    if len(pairs) < 3:
        return {}
    xs = np.array([p[0] for p in pairs])
    ys = np.array([p[1] for p in pairs])
    slope, intercept = np.polyfit(np.log(xs), np.log(ys), 1)
    predicted = np.exp(intercept + slope * np.log(xs))
    return {
        "exponent": round(float(slope), 3),
        "coefficient": float(np.exp(intercept)),
        "points": len(pairs),
        "worst_relative_residual": round(float(np.max(np.abs(predicted / ys - 1))), 3),
    }


def fit_lp(timings: Sequence[dict[str, float | int]]) -> dict[str, float]:
    """Fit ``lp_seconds = c * rows^p``.

    Every round hands HiGHS a matrix it has never seen -- ``solve_lp`` builds a
    fresh ``linprog`` call and scipy's interface exposes no basis to carry over --
    so this is the price of re-solving from scratch, as a function of the row set
    that has to be re-solved.
    """

    return _power_fit(
        [
            (float(entry["rows_held"]), float(entry["lp_s"]))
            for entry in timings
            if int(entry["index"]) >= 1 and float(entry["lp_s"]) > 0
        ]
    )


def fit_separation(timings: Sequence[dict[str, float | int]]) -> dict[str, float]:
    """Fit ``separation = k * support^p`` over the rounds that have a support.

    The separation grid is quadratic in the live site count, so ``p`` near two is
    the model holding and a ``p`` far from it is the model failing. Round 0 is
    excluded: it has no LP support at all and pays the strided fallback in
    ``generate.event_grid`` instead, which is a different cost and is reported
    separately.
    """

    pairs = [
        (float(entry["support"]), float(entry["separation_s"]))
        for entry in timings
        if int(entry["index"]) >= 1
        and float(entry["support"]) > 0
        and float(entry["separation_s"]) > 0
    ]
    if len(pairs) < 3:
        return {}
    return _power_fit(pairs)


def summarise(paths: Sequence[Path]) -> None:
    """Print one line per run in a set of benchmark JSON files, plus the fits."""

    header = (
        f"{'file':<26} {'grids':<14} {'orb':>5} {'sites':>6} {'rnd':>4} {'rows':>6} "
        f"{'sup':>5} {'sec':>8} {'sep':>8} {'lp':>7} {'sep%':>6} "
        f"{'objective':>11}  stopped"
    )
    print(header)
    print("-" * len(header))
    for path in paths:
        report = json.loads(path.read_text())
        runs = report.get("runs") or ([report["row_run"]] if "row_run" in report else [])
        for run in runs:
            print(
                f"{path.name:<26} {tuple(run['grids'])!s:<14} {run['orbits']:>5} "
                f"{run['sites']:>6} {run['rounds']:>4} {run['rows']:>6} "
                f"{run.get('peak_support', 0):>5} {run['seconds']:>8.1f} "
                f"{run['separation_seconds']:>8.1f} {run['lp_seconds']:>7.1f} "
                f"{run['separation_share']:>6.3f} {run['objective']:>11.6f}  {run['stopped']}"
            )
            fit = fit_separation(run.get("timings", []))
            if fit:
                print(
                    f"{'':<26}   fit separation = {fit['coefficient']:.3e} * support^"
                    f"{fit['exponent']} over {fit['points']} rounds, "
                    f"worst residual {fit['worst_relative_residual']:.2f}"
                )
            lp = fit_lp(run.get("timings", []))
            if lp:
                print(
                    f"{'':<26}   fit lp = {lp['coefficient']:.3e} * rows^"
                    f"{lp['exponent']} over {lp['points']} rounds, "
                    f"worst residual {lp['worst_relative_residual']:.2f}"
                )
            cold = [t for t in run.get("timings", []) if int(t["index"]) == 0]
            if cold:
                print(
                    f"{'':<26}   round 0 (strided fallback) {cold[0]['separation_s']:.1f} s "
                    f"= {100 * cold[0]['separation_s'] / max(run['seconds'], 1e-9):.0f}%"
                    " of the run"
                )
        for row in report.get("scales", []):
            print(
                f"{path.name:<26} scale={row['scale']:>9} atoms={row['atoms']:>5} "
                f"total={row['total_mass_float']:.9f} "
                f"margin={row['margin']:+.6f} "
                f"loss={row['loss']:.6f} common={row['common_scale']} "
                f"scaled_total={row['scaled_total']} int64={row['integer_route']} "
                f"verify={row['verify_seconds']}s accepted={row['accepted']} "
                f"least={row['least_cell_mass']}"
            )


def cost_model(paths: Sequence[Path]) -> dict[str, object]:
    """Fit seconds per row-generation round against the container side.

    This is the number ``BC-194`` and ``BC-202`` price their runs with, and the
    one thing the record has never had: the fits inside a run say what a round
    costs as the support and the row set grow, and this says what a round costs
    when the container does. One point per benchmark file, each the mean over
    that run's rounds, so a run stopped on a deadline still contributes.
    """

    points: list[tuple[float, float, str]] = []
    for path in paths:
        report = json.loads(path.read_text())
        runs = report.get("runs") or ([report["row_run"]] if "row_run" in report else [])
        label = str(report["case"])
        side = float(Fraction(label.split("L=")[1].split("=", maxsplit=1)[0]))
        for run in runs:
            if run["rounds"] < 2:
                continue
            points.append((side, run["seconds"] / run["rounds"], path.name))
    fit = _power_fit([(side, seconds) for side, seconds, _ in points])
    for side, seconds, name in sorted(points):
        print(f"  L={side:.4f} {seconds:9.3f} s per round   ({name})")
    if fit:
        print(
            f"  seconds per round = {fit['coefficient']:.4g} * side^{fit['exponent']} "
            f"over {fit['points']} sides, worst relative residual "
            f"{fit['worst_relative_residual']:.2f}"
        )
    return {"points": points, "fit": fit}


def _grids(text: str) -> tuple[int, ...]:
    return tuple(int(part) for part in text.replace(" ", "").split(",") if part)


def _emit(report: dict[str, object], path: Path | None) -> None:
    text = json.dumps(report, indent=2, default=str)
    if path is not None:
        path.write_text(text + "\n")
        print(f"wrote {path}")
    else:
        print(text)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0] if __doc__ else None)
    sub = parser.add_subparsers(dest="command", required=True)

    def common(target: argparse.ArgumentParser) -> None:
        target.add_argument("--n", type=int, required=True)
        target.add_argument("--side", type=Fraction, required=True)
        target.add_argument("--square-side", type=Fraction, default=SQUARE_SIDE)
        target.add_argument("--angle-limit", type=Fraction, default=ANGLE_LIMIT)
        target.add_argument("--direction-steps", type=int, default=DIRECTION_STEPS)
        target.add_argument("--inset", type=Fraction, default=Fraction(1, 2))
        target.add_argument("--max-rounds", type=int, default=60)
        target.add_argument("--rows-per-direction", type=int, default=3)
        target.add_argument(
            "--deadline-seconds",
            type=float,
            default=None,
            help="wall past which no further row-generation round starts",
        )
        target.add_argument("--out", type=Path, default=None)

    rounds = sub.add_parser(
        "rounds", help="split a row-generation round into separation and LP"
    )
    common(rounds)
    rounds.add_argument("--grids", type=_grids, default=None)
    rounds.add_argument("--no-pricing", action="store_true")

    density = sub.add_parser("density", help="the same case at several site grids")
    common(density)
    density.add_argument("--grids", type=_grids, action="append", default=[])
    density.add_argument(
        "--rule",
        action="store_true",
        help="add the grid the site-density rule gives for this side",
    )

    scale = sub.add_parser("scale", help="one LP point rationalised at several scales")
    common(scale)
    scale.add_argument("--grids", type=_grids, default=None)
    scale.add_argument(
        "--scales",
        type=lambda text: tuple(int(p) for p in text.split(",")),
        default=(200_000, 1_000_000, 4_000_000),
    )
    scale.add_argument(
        "--verify-scales", type=lambda text: tuple(int(p) for p in text.split(","))
    )

    table = sub.add_parser("summarise", help="tabulate benchmark JSON files")
    table.add_argument("paths", type=Path, nargs="+")

    model = sub.add_parser("costmodel", help="fit seconds per round against the side")
    model.add_argument("paths", type=Path, nargs="+")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "summarise":
        summarise(args.paths)
        return 0
    if args.command == "costmodel":
        cost_model(args.paths)
        return 0
    case = Case(
        n=args.n,
        outer_side=args.side,
        square_side=args.square_side,
        angle_limit=args.angle_limit,
        direction_steps=args.direction_steps,
        inset=args.inset,
    )
    default_grids = site_counts_for_side(case.outer_side, case.square_side, inset=case.inset)
    print(f"case {case.label()} rule grids {default_grids}", flush=True)

    if args.command == "density":
        grid_sets = list(args.grids)
        if args.rule or not grid_sets:
            grid_sets.append(default_grids)
        report = bench_density(
            case,
            grid_sets,
            max_rounds=args.max_rounds,
            rows_per_direction=args.rows_per_direction,
            deadline_seconds=args.deadline_seconds,
        )
    elif args.command == "rounds":
        report = bench_rounds(
            case,
            args.grids or default_grids,
            max_rounds=args.max_rounds,
            rows_per_direction=args.rows_per_direction,
            price=not args.no_pricing,
            deadline_seconds=args.deadline_seconds,
        )
    else:
        report = bench_scale(
            case,
            args.grids or default_grids,
            args.scales,
            max_rounds=args.max_rounds,
            rows_per_direction=args.rows_per_direction,
            verify_scales=args.verify_scales,
            deadline_seconds=args.deadline_seconds,
        )
    _emit(report, args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
