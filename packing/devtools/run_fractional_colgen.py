"""Run the dual-driven column generator at one setting and record what it cost.

The generator is a library call with a dozen parameters, and every run of it
in the record so far was made from a one-off script that was not kept. The
covering-values register carries the consequence in plain words: for the
`n = 12` rung at `99/25`, "the record names no site set and retains no site,
row or round count". This module is the driver, so the next run is a command
with its parameters on the line and a per-round table on its stdout.

It only drives. `generate_adaptive` makes every search decision, the
rationaliser makes the candidate, and nothing here decides a bound: freezing
is the last thing it does, and `devtools.decide_certificate` is what turns a
frozen candidate into a retained one.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

from sqpack.fractional.certificate import Certificate, verify
from sqpack.fractional.colgen import (
    AdaptiveLog,
    RoundTiming,
    generate_adaptive,
    site_counts_for_side,
)

# The net every retained fractional certificate carries, and the shrink they
# are all built at. Defaults rather than constants: a run that changes them is
# a different instrument and has to say so on the command line.
ANGLE_LIMIT = Fraction(207107, 500000)
DIRECTION_STEPS = 180
SHRINK = Fraction(9977, 10000)
SCALE = 200_000


@dataclass(frozen=True, slots=True)
class RunSettings:
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
    # A second site-set construction: a retained certificate whose atoms are
    # carried to this side and unioned with the grids. ``None`` is the grids
    # alone, which is what every run before BC-197 was.
    seed_certificate: Path | None = None
    seed_map: str = "scale"
    # Sites per ceiling window, see ``window_lattice``; 0 adds none.
    seed_windows: int = 0

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
            "seed_certificate": (
                None if self.seed_certificate is None else str(self.seed_certificate)
            ),
            "seed_map": self.seed_map,
            "seed_windows": self.seed_windows,
        }


def summary(
    settings: RunSettings,
    log: AdaptiveLog,
    candidate: Certificate | None,
    seconds: float,
    frozen: Path | None,
) -> dict[str, object]:
    return {
        "settings": settings.as_dict(),
        "seconds": seconds,
        "stopped": log.stopped,
        "converged": log.stopped.startswith("converged"),
        "objective": log.objective,
        "least_covered": log.least_covered,
        "rounds": [
            {
                "index": entry.index,
                "rows": entry.rows,
                "orbits": entry.orbits,
                "sites": entry.sites,
                "lp_rounds": entry.lp_rounds,
                "objective": entry.objective,
                "least_covered": entry.least_covered,
                "averaged_depth": entry.averaged_depth,
                "reduced_cost": entry.cost,
                "added": entry.added,
                "seconds": entry.seconds,
                "note": entry.note,
            }
            for entry in log.rounds
        ],
        "total_mass": str(log.total_mass) if log.total_mass is not None else None,
        "total_mass_float": float(log.total_mass) if log.total_mass is not None else None,
        "atoms": len(candidate.atoms) if candidate is not None else 0,
        "ceiling_proved": None if log.ceiling is None else log.ceiling.proved,
        "ceiling_detail": None if log.ceiling is None else log.ceiling.detail,
        "frozen": str(frozen) if frozen is not None else None,
    }


SEED_MAPS = ("scale", "centre")


def seed_points_from(
    path: Path, outer_side: Fraction, mapping: str
) -> set[tuple[Fraction, Fraction]]:
    """A retained certificate's atom sites, carried to ``outer_side``.

    Two maps, both D4-equivariant about the container centre so the seed
    stays a union of orbits: ``scale`` multiplies every coordinate by the
    ratio of the sides, which keeps each atom's distance to its nearest wall
    in proportion; ``centre`` translates by half the difference of the sides,
    which keeps the atoms' mutual distances and moves them off the walls.
    The weights are not read: a seed is a site set, and the LP sets the mass.
    """

    if mapping not in SEED_MAPS:
        raise ValueError(f"seed map must be one of {SEED_MAPS}, not {mapping!r}")
    record = json.loads(path.read_text())
    source_side = Fraction(record["outer_side"])
    ratio = outer_side / source_side
    shift = (outer_side - source_side) / 2
    points: set[tuple[Fraction, Fraction]] = set()
    for x, y, _weight in record["atoms"]:
        fx, fy = Fraction(x), Fraction(y)
        if mapping == "scale":
            points.add((fx * ratio, fy * ratio))
        else:
            points.add((fx + shift, fy + shift))
    return points


def window_lattice(
    n: int, outer_side: Fraction, square_side: Fraction, per_window: int
) -> set[tuple[Fraction, Fraction]]:
    """Sites inside the ceiling windows, where a sub-``m^2`` solution has to sit.

    Write ``m = ceil(sqrt(n))`` and ``delta = m B - L > 0``. Along one axis, ``m``
    axis-parallel ``B``-squares in a row overlap by ``delta`` in total, and the
    restricted dual only has to keep its depth at most 1 *at the sites*: if no
    site lies in any overlap strip, ``m`` unit weights per row are dual-feasible
    and the restricted optimum is ``m^2`` however small the covering value is.
    That is the exactly round value this pipeline has met at ``n = 13``,
    ``n = 17``, ``n = 18`` and BC-191's coarsest density, read mechanically.

    The remedy is the ``m - 1`` coordinates a hitting set needs: ``x_k`` in
    ``[L - (m - k) B, k B]`` for ``k = 1 .. m - 1``, windows of width ``delta``
    spaced ``B`` apart. Their products form a D4-symmetric lattice, and this
    returns it with ``per_window`` equally spaced sites inside each window (the
    ends excluded), so the LP can choose within the window and a placement
    tilted by the net's first step still finds mass. Direction 0 is what the
    lattice serves; the tilted directions are left to the grids and to column
    generation. Empty when ``per_window`` is 0 or the side is at or above the
    ceiling, where no window exists.
    """

    if per_window <= 0:
        return set()
    m = math.isqrt(n - 1) + 1
    delta = m * square_side - outer_side
    if delta <= 0:
        return set()
    coordinates: list[Fraction] = []
    for k in range(1, m):
        low = outer_side - (m - k) * square_side
        coordinates.extend(low + delta * j / (per_window + 1) for j in range(1, per_window + 1))
    return {(x, y) for x in coordinates for y in coordinates}


class RowLog(list[RoundTiming]):
    """A timings list that writes each LP round to a file as it lands.

    `generate_adaptive` logs a column round at a time, so a run stopped inside
    its first column round used to leave nothing (BC-211's runs B and D). The
    loop appends one `RoundTiming` per LP round to whatever list it is given;
    this one echoes the round to disk on append, so the table exists while
    the run is still going and survives a kill. Index ``-1`` is the warm
    solve a carried row set opens with and does no separation.
    """

    HEADER = (
        f"{'lp':>5} {'rows':>7} {'added':>6} {'violated':>8} {'support':>8} "
        f"{'objective':>13} {'sep_s':>8} {'lp_s':>8}"
    )

    def __init__(self, path: Path) -> None:
        super().__init__()
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self.handle = path.open("a")
        self.handle.write(self.HEADER + "\n")
        self.handle.flush()

    def append(self, timing: RoundTiming) -> None:
        super().append(timing)
        self.handle.write(
            f"{timing.index:>5} {timing.rows_held:>7} {timing.rows_added:>6} "
            f"{timing.violated:>8} {timing.support:>8} {timing.objective:>13.6f} "
            f"{timing.separation_seconds:>8.2f} {timing.lp_seconds:>8.2f}\n"
        )
        self.handle.flush()

    def close(self) -> None:
        self.handle.close()


def run(
    settings: RunSettings,
    *,
    log_path: Path | None,
    freeze: Path | None,
    verify_serial: bool = False,
    row_log: Path | None = None,
    deadline_seconds: float | None = None,
) -> dict[str, object]:
    started = time.perf_counter()
    deadline = None if deadline_seconds is None else started + deadline_seconds
    seed: set[tuple[Fraction, Fraction]] = set()
    if settings.seed_certificate is not None:
        seed = seed_points_from(
            settings.seed_certificate, settings.outer_side, settings.seed_map
        )
    seed |= window_lattice(
        settings.n, settings.outer_side, settings.square_side, settings.seed_windows
    )
    timings: RowLog | list[RoundTiming] = RowLog(row_log) if row_log is not None else []
    candidate, log = generate_adaptive(
        settings.n,
        settings.outer_side,
        settings.square_side,
        grid_counts=settings.grid_counts,
        inset=settings.inset,
        angle_limit=settings.angle_limit,
        direction_steps=settings.direction_steps,
        scale=settings.scale,
        max_rounds=settings.max_rounds,
        column_rounds=settings.column_rounds,
        rows_per_direction=settings.rows_per_direction,
        log_path=log_path,
        # Never here. The retention boundary is freeze-then-decide, and an
        # in-memory verdict is not evidence about any file (D-433, D-441).
        decide=False,
        seed_points=seed,
        timings=timings,
        deadline=deadline,
    )
    seconds = time.perf_counter() - started
    if isinstance(timings, RowLog):
        timings.close()
    frozen: Path | None = None
    least_cell_mass: str | None = None
    if candidate is not None and freeze is not None:
        if verify_serial:
            # One worker, never the pool: a lane holding one core must not
            # start a parallel sweep, and this only fills the declaration.
            least_cell_mass = str(verify(candidate, workers=1).minimum_cell_mass)
        freeze.parent.mkdir(parents=True, exist_ok=True)
        freeze.write_text(certificate_json(candidate, least_cell_mass))
        frozen = freeze
    result = summary(settings, log, candidate, seconds, frozen)
    result["least_cell_mass"] = least_cell_mass
    result["seed_sites"] = len(seed)
    result["lp_log"] = [
        {
            "index": timing.index,
            "rows": timing.rows_held,
            "added": timing.rows_added,
            "violated": timing.violated,
            "support": timing.support,
            "objective": timing.objective,
            "separation_s": round(timing.separation_seconds, 3),
            "lp_s": round(timing.lp_seconds, 3),
        }
        for timing in timings
    ]
    return result


def certificate_json(certificate: Certificate, least_cell_mass: str | None) -> str:
    """The retained on-disk shape, which `cases/*/replay.py` reads back.

    ``least_cell_mass`` is a declaration and not a decision: it is left null
    when nothing has computed it, so a frozen candidate never carries a number
    no run produced. `devtools.decide_certificate` is what decides the bytes.
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--side", type=Fraction, required=True, help="container side L")
    parser.add_argument("--shrink", type=Fraction, default=SHRINK, help="square side B")
    parser.add_argument(
        "--grid-counts",
        default="auto",
        help="comma-separated seed grid counts, or 'auto' for BC-191's site density",
    )
    parser.add_argument("--inset", type=Fraction, default=Fraction(1, 2))
    parser.add_argument("--angle-limit", type=Fraction, default=ANGLE_LIMIT)
    parser.add_argument("--direction-steps", type=int, default=DIRECTION_STEPS)
    parser.add_argument("--scale", type=int, default=SCALE)
    parser.add_argument("--column-rounds", type=int, default=8)
    parser.add_argument("--max-rounds", type=int, default=60)
    parser.add_argument("--rows-per-direction", type=int, default=3)
    parser.add_argument("--log", type=Path, default=None, help="append the round lines here")
    parser.add_argument("--freeze", type=Path, default=None, help="write the candidate here")
    parser.add_argument("--json", type=Path, default=None, help="write the run summary here")
    parser.add_argument(
        "--verify-serial",
        action="store_true",
        help="fill least_cell_mass with a one-worker sweep before freezing",
    )
    parser.add_argument(
        "--seed-certificate",
        type=Path,
        default=None,
        help="union the grids with a retained certificate's atom sites carried to this side",
    )
    parser.add_argument(
        "--seed-map",
        choices=SEED_MAPS,
        default="scale",
        help="how the seed atoms are carried: scale the coordinates, or centre them",
    )
    parser.add_argument(
        "--seed-windows",
        type=int,
        default=0,
        help="sites per ceiling window to seed (the centred pitch-B lattice); 0 for none",
    )
    parser.add_argument(
        "--deadline-seconds",
        type=float,
        default=None,
        help="wall clock after which no row round starts; the run returns unconverged",
    )
    parser.add_argument(
        "--row-log",
        type=Path,
        default=None,
        help="append one line per LP round here as it lands, so a killed run leaves a table",
    )
    args = parser.parse_args(argv)

    settings = RunSettings(
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
        seed_certificate=args.seed_certificate,
        seed_map=args.seed_map,
        seed_windows=args.seed_windows,
    )
    print(json.dumps(settings.as_dict(), indent=1), flush=True)
    result = run(
        settings,
        log_path=args.log,
        freeze=args.freeze,
        verify_serial=args.verify_serial,
        row_log=args.row_log,
        deadline_seconds=args.deadline_seconds,
    )
    print(round_table_from(result), flush=True)
    print(
        f"stopped: {result['stopped']}\n"
        f"objective: {result['objective']}\n"
        f"least covered mass: {result['least_covered']}\n"
        f"total mass: {result['total_mass']} = {result['total_mass_float']}\n"
        f"least cell mass: {result.get('least_cell_mass')}\n"
        f"atoms: {result['atoms']}\n"
        f"seed sites: {result['seed_sites']}\n"
        f"frozen: {result['frozen']}\n"
        f"seconds: {result['seconds']:.1f}",
        flush=True,
    )
    if args.json is not None:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(result, indent=1) + "\n")
    return 0


def round_table_from(result: dict[str, object]) -> str:
    """The same table as `round_table`, from the summary a run returns."""

    header = (
        f"{'round':>5} {'rows':>7} {'orbits':>7} {'sites':>7} {'lp_rounds':>9} "
        f"{'objective':>13} {'least_covered':>13} {'depth':>10} {'seconds':>9}  note"
    )
    lines = [header, "-" * len(header)]
    rounds = result["rounds"]
    assert isinstance(rounds, list)
    lines.extend(
        f"{entry['index']:>5} {entry['rows']:>7} {entry['orbits']:>7} "
        f"{entry['sites']:>7} {entry['lp_rounds']:>9} {entry['objective']:>13.6f} "
        f"{entry['least_covered']:>13.6f} {entry['averaged_depth']:>10.6f} "
        f"{entry['seconds']:>9.1f}  {entry['note']}"
        for entry in rounds
    )
    return "\n".join(lines)


if __name__ == "__main__":
    sys.exit(main())
