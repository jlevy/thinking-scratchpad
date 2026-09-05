"""Run the two-threshold class program and its two literature controls.

The program is `sqpack.fractional.classcert`; this is the harness that reads a
net from a retained certificate, builds a class, prices a composition, and puts
the float proposal beside the exact confirmation. Nothing it produces is
retained: a class certificate refuses one composition, and the retention gate
decides five-condition `Certificate` objects, which this is not.

Two controls, both facts the literature already carries:

``nine-point``  At side ``3877/1000`` the largest near-axis class inside
        ``theta_0`` -- where ``cos theta + sin theta = 4 B / L`` -- is the net's
        first six cells. Nine unit atoms on the pitch-``L / 4`` grid are feasible
        for that class program at ``w_0 = 1``, so its optimum is at most nine,
        and nine below eleven closes the composition ``(11, 0)``. An optimum
        above nine is an instrument defect and not a result.
``stromquist``  The class of the two end cells -- around ``0`` and ``45``
        degrees -- must refute ``(11, 0)`` at a side at or above Trump's
        ``3.877084``. Stromquist's Theorem 3 reaches ``2 + (4/3) sqrt 2 =
        3.885618`` for the exact two-direction class by a further box step this
        program does not have, so ``3.877084`` is the threshold and
        ``3.885618`` is not.

A third mode, ``price``, times a class program with both classes active over the
whole net, which is the shape a composition sweep would pay for.

Usage, from ``packing/``::

    uv run --frozen --all-extras --group dev python devtools/run_class_program.py all
"""

from __future__ import annotations

import argparse
import json
import math
import time
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

import numpy as np

from sqpack.fractional.classcert import (
    NEAR,
    TILTED,
    ClassProgramLog,
    ClassRoundTiming,
    ClassThresholds,
    ClassVerdict,
    Composition,
    DirectionClasses,
    axis_disjoint_count,
    decide_class_program,
    end_cells,
    largest_half_gap_tangent,
    leading_cells,
    quarter_pitch_sites,
    sign_against_quadratic_surd,
    solve_class_program,
    within_nine_point_tilt,
)
from sqpack.fractional.generate import (
    SiteGrid,
    build_site_grid,
    net_half_tangents,
    rationalise,
)
from sqpack.fractional.model import Atom
from sqpack.project import require_project_root

#: The retained ``n = 11`` certificate, whose net every run here reads.
NET_SOURCE = Path("cases/n11_fractional_certificate/certificate.json")

#: Control one's side, and control two's: Trump's value, the side a class that
#: does not contain his packing has to be refuted at or above.
NINE_POINT_SIDE = Fraction(3877, 1000)
TRUMP_SIDE = Fraction(3877084, 1000000)


def degrees(tangent: Fraction) -> float:
    """The angle of a tangent, in degrees. Display only: no decision reads this."""

    return math.degrees(math.atan(float(tangent)))


@dataclass(frozen=True, slots=True)
class Net:
    half_tangents: tuple[Fraction, ...]
    square_side: Fraction
    steps: int
    limit: Fraction


def load_net(root: Path) -> Net:
    """Read the net from the retained certificate rather than from memory."""

    spec = json.loads((root / NET_SOURCE).read_text())
    limit = Fraction(spec["angle_limit"])
    steps = int(spec["direction_steps"])
    return Net(
        half_tangents=net_half_tangents(limit, steps),
        square_side=Fraction(spec["square_side"]),
        steps=steps,
        limit=limit,
    )


def describe_net(net: Net) -> list[str]:
    gap = largest_half_gap_tangent(net.half_tangents)
    product = net.square_side * (1 + gap)
    return [
        (
            f"net           angle_limit {net.limit} steps {net.steps} "
            f"directions {len(net.half_tangents)}"
        ),
        f"net           arc 0 to {math.degrees(2 * math.atan(float(net.limit))):.6f} deg",
        (
            f"net           spacing at the axis-parallel end "
            f"{math.degrees(2 * math.atan(float(net.half_tangents[1]))):.6f} deg"
        ),
        (
            f"net           B {net.square_side} D {gap} B(1+D) {float(product):.6f} "
            f"< 1: {product < 1}"
        ),
    ]


def describe_class(classes: DirectionClasses, name: str) -> list[str]:
    members = classes.members(NEAR)
    bounds = [classes.cell_bounds(index) for index in members]
    if not bounds:
        raise ValueError("Theta_0 holds no cell to describe")
    lows = f"{degrees(bounds[0][0]):.6f}"
    highs = f"{degrees(bounds[-1][1]):.6f}"
    span = f"{members[0]}..{members[-1]}"
    return [
        (
            f"class         {name}: Theta_0 holds {len(members)} of {classes.cells} cells, "
            f"cells {span}"
        ),
        (
            f"class         {name}: Theta_0 spans {lows} to {highs} deg "
            f"(cell bounds, exact tangents {bounds[0][0]} and {bounds[-1][1]})"
        ),
        f"class         {name}: Theta_1 holds {classes.cells - len(members)} cells",
    ]


def report_verdict(tag: str, verdict: ClassVerdict) -> list[str]:
    lines = [
        f"exact  {tag}  total mass M = {verdict.total_mass} = {float(verdict.total_mass):.6f}",
        (
            f"exact  {tag}  required n0 w0 + n1 w1 = {verdict.required} = "
            f"{float(verdict.required):.6f}"
        ),
        (
            f"exact  {tag}  margin M - n0 w0 - n1 w1 = {verdict.margin} = "
            f"{float(verdict.margin):.6f}"
        ),
    ]
    lines.extend(
        f"exact  {tag}  [{'hold' if c.holds else 'FAIL'}] {c.name}: {c.detail}"
        for c in verdict.conditions
    )
    lines.append(
        f"exact  {tag}  composition ({verdict.composition.near}, "
        f"{verdict.composition.tilted}) refuted: {verdict.refutes}"
    )
    return lines


def report_search(tag: str, log: ClassProgramLog, timings: list[ClassRoundTiming]) -> list[str]:
    lp_seconds = [t.lp_seconds for t in timings if t.lp_seconds > 0]
    separation = [t.separation_seconds for t in timings]
    mean_lp = float(np.mean(lp_seconds)) if lp_seconds else 0.0
    max_lp = max(lp_seconds) if lp_seconds else 0.0
    at_unit = log.objective / log.thresholds[NEAR] if log.thresholds[NEAR] > 0 else float("nan")
    return [
        f"float  {tag}  stopped: {log.stopped}",
        (
            f"float  {tag}  rounds {log.rounds} rows {log.rows} "
            f"w0 {log.thresholds[NEAR]:.9f} w1 {log.thresholds[TILTED]:.9f}"
        ),
        (
            f"float  {tag}  M {log.objective:.9f} required {log.required:.9f} "
            f"margin {log.margin:+.9f}"
        ),
        f"float  {tag}  M rescaled to w0 = 1: {at_unit:.6f}",
        (
            f"float  {tag}  seconds {log.seconds:.3f} total, "
            f"{sum(lp_seconds):.3f} in {len(lp_seconds)} LP solves, "
            f"{sum(separation):.3f} in separation"
        ),
        (f"float  {tag}  per LP solve: mean {mean_lp:.4f} s, max {max_lp:.4f} s"),
    ]


def exact_atoms_at_unit_threshold(
    grid: SiteGrid, weights: np.ndarray, log: ClassProgramLog, *, scale: int
) -> tuple[Atom, ...]:
    """Rationalise the search's point after rescaling its thresholds to ``w_0 = 1``.

    The program is homogeneous, so the normalisation the search runs under is a
    choice of scale and nothing else. Rescaling before rounding *up* is what
    keeps every class row valid at the threshold the exact decision uses.
    """

    if log.thresholds[NEAR] <= 0:
        raise ValueError("the search left no positive near-class threshold to rescale by")
    return rationalise(grid, weights / log.thresholds[NEAR], scale=scale)


def run_nine_point(root: Path, *, grid_count: int, scale: int) -> list[str]:
    """Control one: the nine-point bound at ``3877/1000``."""

    net = load_net(root)
    side, shrink = NINE_POINT_SIDE, net.square_side
    classes = leading_cells(net.half_tangents, 6)
    composition = Composition(near=11, tilted=0)
    limit = 4 * shrink / side
    tilt = math.degrees(math.asin(float(limit) / math.sqrt(2)) - math.pi / 4)
    lines = [
        "",
        "== control one: the nine-point bound ==",
        f"side          L = {side} = {float(side):.6f}",
        (f"tilt limit    4B/L = {limit} = {float(limit):.6f}, theta_0 = {tilt:.6f} deg"),
    ]
    lines.extend(describe_class(classes, "leading six cells"))
    for count in (5, 6, 7):
        candidate = leading_cells(net.half_tangents, count)
        inside = within_nine_point_tilt(candidate, side, shrink)
        lines.append(
            f"tilt limit    leading {count} cells inside theta_0: {inside} "
            f"(upper bound {degrees(candidate.cell_bounds(count - 1)[1]):.6f} deg)"
        )

    # The exact upper bound: the nine-point measure itself, decided on the sweep.
    nine = quarter_pitch_sites(side)
    verdict = decide_class_program(
        nine,
        side,
        shrink,
        classes,
        composition,
        thresholds=ClassThresholds(Fraction(1), Fraction(0)),
    )
    started = time.perf_counter()
    lines.append(f"exact  nine   {len(nine)} unit atoms on the pitch-L/4 grid")
    lines.extend(report_verdict("nine ", verdict))
    lines.append(
        f"exact  nine   sweep over 6 directions: {time.perf_counter() - started:.3f} s"
    )

    # The exact lower bound: disjoint axis-parallel B-squares, each of which the
    # near class contains and each of which must carry w0.
    floor_count = axis_disjoint_count(side, shrink)
    lines.append(
        f"exact  nine   {floor_count} pairwise disjoint axis-parallel B-squares fit, "
        f"so the class optimum at w0 = 1 is at least {floor_count}"
    )

    # The float search, on a grid that contains the nine points, so that its
    # converged optimum is bounded by the same nine.
    grid = build_site_grid(side, grid_count, side / 4)
    timings: list[ClassRoundTiming] = []
    weights, log = solve_class_program(
        grid, shrink, classes, composition, timings=timings, max_rounds=60
    )
    lines.append(
        f"float  nine   site grid {grid_count} x {grid_count} inset L/4, "
        f"{grid.size**2} sites, {len(grid.orbits)} orbits"
    )
    lines.extend(report_search("nine ", log, timings))
    if log.converged:
        atoms = exact_atoms_at_unit_threshold(grid, weights, log, scale=scale)
        confirmed = decide_class_program(
            atoms,
            side,
            shrink,
            classes,
            composition,
            thresholds=ClassThresholds(Fraction(1), Fraction(0)),
        )
        lines.append(f"exact  lp     {len(atoms)} atoms rationalised at 1/{scale}")
        lines.extend(report_verdict("lp   ", confirmed))
    return lines


#: Stromquist's Theorem 3: eleven unit squares at ``0`` or ``45`` degrees need side at
#: least ``2 + (4/3) sqrt 2``. The archive's comparison table carries a packing of that
#: exact side -- Cottingham 1979, the ``n = 11`` entry with minimal rotated squares -- so
#: the bound is attained and the value of the restricted class is that number.
STROMQUIST_RATIONAL = Fraction(2)
STROMQUIST_COEFFICIENT = Fraction(4, 3)
STROMQUIST_RADICAND = 2


def stromquist_ceiling(side: Fraction, square_side: Fraction) -> list[str]:
    """How the shrunken program's reach compares with the restricted-class value.

    A covering program at ``(L, B)`` can only refute eleven cores when eleven
    pairwise disjoint ``B``-squares of the class do not fit in the container,
    that is when ``L / B`` is below the class's own packing value. For the
    ``{0, 45}`` class that value is ``2 + (4/3) sqrt 2``, so the ceiling on the
    side is ``B (2 + (4/3) sqrt 2)`` whatever the site set and however long the
    row loop runs. The comparison is exact: no decimal of the surd is taken.
    """

    ratio = side / square_side
    sign = sign_against_quadratic_surd(
        ratio, STROMQUIST_RATIONAL, STROMQUIST_COEFFICIENT, STROMQUIST_RADICAND
    )
    surd = float(STROMQUIST_RATIONAL) + float(STROMQUIST_COEFFICIENT) * math.sqrt(
        STROMQUIST_RADICAND
    )
    verdict = {
        -1: "below the class value: eleven disjoint cores do not fit, so a refutation is "
        "not excluded here",
        0: "exactly the class value",
        1: "above the class value: eleven disjoint cores fit, so no measure of mass below "
        "eleven can cover this class",
    }[sign]
    return [
        (
            f"ceiling       L/B = {ratio} = {float(ratio):.9f} against "
            f"2 + (4/3) sqrt 2 = {surd:.9f}: {verdict}"
        ),
        (
            f"ceiling       B (2 + (4/3) sqrt 2) = {float(square_side) * surd:.6f} is the "
            f"largest side at which this shrink leaves the class program anything to prove"
        ),
    ]


def run_stromquist(root: Path, *, side: Fraction, grid_count: int, scale: int) -> list[str]:
    """Control two: the two end cells must refute ``(11, 0)`` at or above Trump's side."""

    net = load_net(root)
    shrink = net.square_side
    classes = end_cells(net.half_tangents)
    composition = Composition(near=11, tilted=0)
    lines = [
        "",
        "== control two: Stromquist's two-direction class ==",
        (
            f"side          L = {side} = {float(side):.6f}, threshold 3.877084, "
            f"at or above: {side >= TRUMP_SIDE}"
        ),
    ]
    lines.extend(describe_class(classes, "two end cells"))
    lines.append(
        f"class         end cell half-width at the axis end "
        f"{degrees(classes.cell_bounds(0)[1]):.6f} deg; the 45-degree cell runs "
        f"{degrees(classes.cell_bounds(classes.cells - 1)[0]):.6f} to 45 deg"
    )

    lines.extend(stromquist_ceiling(side, shrink))

    grid = build_site_grid(side, grid_count, Fraction(1, 10))
    timings: list[ClassRoundTiming] = []
    weights, log = solve_class_program(
        grid, shrink, classes, composition, timings=timings, max_rounds=80
    )
    lines.append(
        f"float  strom  site grid {grid_count} x {grid_count} inset 1/10, "
        f"{grid.size**2} sites, {len(grid.orbits)} orbits"
    )
    lines.extend(report_search("strom", log, timings))
    if not log.converged:
        return lines
    atoms = exact_atoms_at_unit_threshold(grid, weights, log, scale=scale)
    started = time.perf_counter()
    confirmed = decide_class_program(
        atoms,
        side,
        shrink,
        classes,
        composition,
        thresholds=ClassThresholds(Fraction(1), Fraction(0)),
    )
    lines.append(f"exact  strom  {len(atoms)} atoms rationalised at 1/{scale}")
    lines.extend(report_verdict("strom", confirmed))
    lines.append(
        f"exact  strom  sweep over 2 directions: {time.perf_counter() - started:.3f} s"
    )
    return lines


def run_price(
    root: Path, *, side: Fraction, grid_count: int, cells: int, rounds: int
) -> list[str]:
    """Price a class program with both classes active over the whole net."""

    net = load_net(root)
    classes = leading_cells(net.half_tangents, cells)
    composition = Composition(near=9, tilted=2)
    grid = build_site_grid(side, grid_count, Fraction(1, 10))
    timings: list[ClassRoundTiming] = []
    _, log = solve_class_program(
        grid, net.square_side, classes, composition, timings=timings, max_rounds=rounds
    )
    lines = [
        "",
        "== price: one class LP with both classes active ==",
        (
            f"price         side {side}, Theta_0 the leading {cells} cells "
            f"(to {degrees(classes.cell_bounds(cells - 1)[1]):.6f} deg), "
            f"composition (9, 2), all {classes.cells} directions separated"
        ),
        (
            f"price         site grid {grid_count} x {grid_count}, {grid.size**2} sites, "
            f"{len(grid.orbits)} orbits, round cap {rounds}"
        ),
    ]
    lines.extend(report_search("price", log, timings))
    lines.extend(
        f"price         round {t.index} separation {t.separation_seconds:.3f} s "
        f"lp {t.lp_seconds:.3f} s rows {t.rows_held} (+{t.rows_added}) M {t.objective:.6f}"
        for t in timings
    )
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "control",
        choices=("nine-point", "stromquist", "price", "all"),
        help="which control to run",
    )
    parser.add_argument("--grid-count", type=int, default=9)
    parser.add_argument("--scale", type=int, default=4096)
    parser.add_argument(
        "--side", type=str, default=None, help="override the side, as a fraction"
    )
    parser.add_argument("--cells", type=int, default=19)
    parser.add_argument("--rounds", type=int, default=3)
    arguments = parser.parse_args()

    root = require_project_root()
    lines: list[str] = []
    if arguments.control in {"nine-point", "all"}:
        lines.extend(describe_net(load_net(root)))
        lines.extend(
            run_nine_point(root, grid_count=arguments.grid_count, scale=arguments.scale)
        )
    if arguments.control in {"stromquist", "all"}:
        side = Fraction(arguments.side) if arguments.side else TRUMP_SIDE
        lines.extend(
            run_stromquist(
                root, side=side, grid_count=arguments.grid_count, scale=arguments.scale
            )
        )
    if arguments.control in {"price", "all"}:
        side = Fraction(arguments.side) if arguments.side else TRUMP_SIDE
        lines.extend(
            run_price(
                root,
                side=side,
                grid_count=arguments.grid_count,
                cells=arguments.cells,
                rounds=arguments.rounds,
            )
        )
    for line in lines:
        print(line)


if __name__ == "__main__":
    main()
