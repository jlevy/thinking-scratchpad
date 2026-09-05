"""Class certificates: the two-threshold form of ``Condition 5`` (X-014, Lemma 3).

An unconditional certificate asks every admissible core to carry mass at least
``1`` and its total to fall below ``n``. A *class* certificate conditions on
direction instead. Partition the net's half-gap cells -- the arcs bounded by
the midpoints between consecutive net angles -- into two classes ``Theta_0``
and ``Theta_1``, fix a composition ``n_0 + n_1 = n``, and ask for weights
``w_0, w_1 >= 0`` and a ``D4``-symmetric measure ``mu`` with

``Condition 5'``  every admissible core at a direction in ``Theta_c`` carries
        mass at least ``w_c``, for each class ``c``.
``Condition 2'``  ``M < n_0 w_0 + n_1 w_1`` for ``M`` the total mass.

Conditions 1, 3 and 4 are unchanged, and they are what make the count work:
``Condition 4`` puts a core at the net direction whose *cell* holds the square's
angle, so a square's core is at a direction of the square's own class, and the
``n`` cores are pairwise disjoint. Each contributes at least its class weight,
so ``n_0 w_0 + n_1 w_1 <= M``, which ``Condition 2'`` forbids. No packing of
``n`` unit squares in ``[0, L]^2`` then has exactly ``n_0`` squares with
directions in ``Theta_0`` and ``n_1`` in ``Theta_1``.

The cell boundary is not decoration. A square at an angle between two net
directions lies in the cell of the nearer one and contains no core at the
farther one, so a class cut at a geometric angle rather than at a cell boundary
would count it wrongly. `DirectionClasses` therefore indexes classes by *cell*,
and reports each cell's bounds as exact tangents.

Nothing here is geometric. The admissible centre domain is the one
`sqpack.fractional.sweep.centre_domain` already decides; this module changes
the thresholds a placement is measured against and the quantity the total is
compared with, which is two variables and one normalisation row. Generalising
the domain itself -- what a conditional certificate (X-014, Lemma 2) would need
-- is not attempted here.

The constraints are linear in ``(mu, w_0, w_1)`` and the objective
``M - n_0 w_0 - n_1 w_1`` is homogeneous, so the program is one linear program
per composition under a normalisation, decided by the sign of its optimum.
`solve_class_program` normalises by ``n_0 w_0 + n_1 w_1 = 1`` and searches in
floating point; `decide_class_program` decides the same object exactly, at
thresholds a caller fixes, on the exact event-cell sweep. Floats propose and
exact arithmetic confirms, as everywhere else in this package.

What this module does not do is retain anything. A class certificate refutes
one composition; it is not a `Certificate` and
`devtools.decide_certificate` -- which decides the five unconditional
conditions -- does not decide it. `ClassVerdict` is a measurement, not a
retained object.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from fractions import Fraction
from itertools import pairwise

import numpy as np
from scipy.optimize import linprog

from sqpack.fractional.certificate import d4_images
from sqpack.fractional.generate import LP_FEASIBILITY, SiteGrid, direction_net, placement_cells
from sqpack.fractional.model import Atom, Direction
from sqpack.fractional.sweep import minimum_covered_mass

#: The class index of the near-axis class ``Theta_0``.
NEAR = 0
#: The class index of the complementary class ``Theta_1``.
TILTED = 1

#: Both class indices, in the order their thresholds occupy in the LP.
CLASS_INDICES = (NEAR, TILTED)


def largest_half_gap_tangent(half_tangents: tuple[Fraction, ...]) -> Fraction:
    """``D``: the largest tangent of a half-gap between adjacent net angles.

    With ``t = tan(theta / 2)`` the net angle is ``2 arctan t``, so half the gap
    between adjacent directions is ``arctan(t2) - arctan(t1)``, whose tangent is
    ``(t2 - t1) / (1 + t1 t2)``. Written here for a bare net, which is what a
    class program has before it has any atoms.
    """

    return max((right - left) / (1 + left * right) for left, right in pairwise(half_tangents))


def cell_boundary_tangent(lower: Fraction, upper: Fraction) -> Fraction:
    """``tan`` of the angle midway between two net directions, exactly.

    The net angles are ``2 arctan t``, so the midpoint angle is
    ``arctan t1 + arctan t2`` and its tangent is
    ``(t1 + t2) / (1 - t1 t2)`` -- rational, unlike its half-tangent. Cell
    boundaries are therefore carried as tangents throughout this module, which
    is enough to order them and to compare them against a tilt limit exactly.
    """

    denominator = 1 - lower * upper
    if denominator <= 0:
        raise ValueError("net directions must lie strictly inside a quarter turn")
    return (lower + upper) / denominator


def cos_plus_sin_at_most(tangent: Fraction, bound: Fraction) -> bool:
    """Decide ``cos t + sin t <= bound`` exactly, for ``t = arctan(tangent)``.

    ``cos t + sin t = (1 + T) / sqrt(1 + T^2)`` for ``T = tan t >= 0``, and both
    that and ``bound`` are positive, so squaring is an equivalence and the test
    is a comparison of two rationals. No angle is ever evaluated.
    """

    if tangent < 0:
        raise ValueError("the tilt tangent must be nonnegative")
    if bound <= 0:
        return False
    return (1 + tangent) ** 2 <= bound * bound * (1 + tangent * tangent)


def sign_against_quadratic_surd(
    value: Fraction, rational: Fraction, coefficient: Fraction, radicand: int
) -> int:
    """The sign of ``value - (rational + coefficient sqrt(radicand))``, exactly.

    A restricted-orientation packing value is typically a quadratic surd --
    Stromquist's ``2 + (4/3) sqrt 2`` for the ``{0, 45}`` class at ``n = 11`` --
    and what a class program has to be compared against is such a number, not a
    decimal of it. Both sides are put on one side and squared once, which is an
    equivalence because the square root is taken of a nonnegative rational and
    the coefficient is nonnegative.
    """

    if coefficient < 0 or radicand < 0:
        raise ValueError("the surd must be a nonnegative multiple of a real square root")
    difference = value - rational
    if difference < 0:
        return -1
    square = difference * difference - coefficient * coefficient * radicand
    if square == 0:
        return 0
    return 1 if square > 0 else -1


@dataclass(frozen=True, slots=True)
class Composition:
    """How many of the ``n`` squares sit in each class."""

    near: int
    tilted: int

    def __post_init__(self) -> None:
        if self.near < 0 or self.tilted < 0:
            raise ValueError("a composition counts squares, so neither part may be negative")
        if self.near + self.tilted < 1:
            raise ValueError("a composition must account for at least one square")

    @property
    def total(self) -> int:
        return self.near + self.tilted

    def count(self, label: int) -> int:
        return self.near if label == NEAR else self.tilted

    def active(self) -> tuple[int, ...]:
        """The classes with a positive count.

        A class with count zero enters neither the objective nor the
        normalisation, and its threshold appears only in constraints of the form
        ``mass >= w``, so ``w = 0`` is optimal and those constraints are vacuous.
        Skipping them is an exact simplification, not an approximation.
        """

        return tuple(label for label in CLASS_INDICES if self.count(label) > 0)


@dataclass(frozen=True, slots=True)
class DirectionClasses:
    """A partition of the net's half-gap cells into ``Theta_0`` and ``Theta_1``.

    One cell per net direction: cell ``i`` is the arc between the midpoint of
    directions ``i - 1`` and ``i`` and the midpoint of ``i`` and ``i + 1``,
    with the first cell reaching down to angle ``0`` and the last reaching up to
    the fold at ``pi / 4``. ``near`` names the cells in ``Theta_0``; every other
    cell is in ``Theta_1``.

    The classes are ``D4``-closed by construction, because the net is the folded
    arc: an angle anywhere on the circle reduces into ``[0, pi / 4]`` under the
    container's symmetry before it meets a cell at all.
    """

    half_tangents: tuple[Fraction, ...]
    near: frozenset[int]

    def __post_init__(self) -> None:
        if len(self.half_tangents) < 2:
            raise ValueError("the direction net needs at least two directions")
        if list(self.half_tangents) != sorted(set(self.half_tangents)):
            raise ValueError("half-angle tangents must be strictly increasing")
        if self.half_tangents[0] != 0:
            raise ValueError("the direction net must start at angle zero")
        if not self.near:
            raise ValueError("Theta_0 must hold at least one cell")
        if any(index not in range(len(self.half_tangents)) for index in self.near):
            raise ValueError("every cell of Theta_0 must be a cell of this net")

    @property
    def cells(self) -> int:
        return len(self.half_tangents)

    def label(self, index: int) -> int:
        return NEAR if index in self.near else TILTED

    def labels(self) -> tuple[int, ...]:
        return tuple(self.label(index) for index in range(self.cells))

    def members(self, label: int) -> tuple[int, ...]:
        return tuple(index for index in range(self.cells) if self.label(index) == label)

    def cell_bounds(self, index: int) -> tuple[Fraction, Fraction]:
        """The cell's lower and upper bounds, as tangents of the bounding angles.

        The first cell starts at ``0``; the last ends at the fold, ``tan(pi / 4)
        = 1``. Every interior boundary is a midpoint between adjacent net angles.
        """

        if index not in range(self.cells):
            raise ValueError("no such cell in this net")
        lower = (
            Fraction(0)
            if index == 0
            else cell_boundary_tangent(self.half_tangents[index - 1], self.half_tangents[index])
        )
        upper = (
            Fraction(1)
            if index == self.cells - 1
            else cell_boundary_tangent(self.half_tangents[index], self.half_tangents[index + 1])
        )
        return lower, upper

    def outer_tangent(self, label: int) -> Fraction:
        """The largest bounding tangent any cell of this class reaches."""

        return max(self.cell_bounds(index)[1] for index in self.members(label))


def leading_cells(half_tangents: tuple[Fraction, ...], count: int) -> DirectionClasses:
    """``Theta_0`` is the net's first ``count`` cells: the near-axis class."""

    if count < 1:
        raise ValueError("the near-axis class needs at least one cell")
    if count > len(half_tangents):
        raise ValueError("the net has fewer cells than that")
    return DirectionClasses(half_tangents, frozenset(range(count)))


def end_cells(half_tangents: tuple[Fraction, ...]) -> DirectionClasses:
    """``Theta_0`` is the two end cells: Stromquist's ``{0, pi / 4}`` class.

    The folded arc's ends are the axis-parallel and diagonal directions, so this
    is the class of squares that are nearly aligned with the container or nearly
    at ``45`` degrees to it, and its complement is everything between.
    """

    last = len(half_tangents) - 1
    if last < 1:
        raise ValueError("the net needs two distinct end cells")
    return DirectionClasses(half_tangents, frozenset({0, last}))


def axis_disjoint_count(outer_side: Fraction, square_side: Fraction) -> int:
    """``m^2`` for the largest ``m`` with ``m B < L``: disjoint axis-parallel cores.

    Place ``m`` closed ``B``-squares along each axis on a pitch strictly above
    ``B`` and inside the container; the ``m^2`` of them are pairwise disjoint, so
    with nonnegative weights any measure meeting ``Condition 5'`` at direction
    zero carries at least ``m^2 w`` for that direction's class weight. This is
    `sqpack.fractional.certificate.ceiling_side`'s device read as a lower bound on
    a class program rather than as a ceiling on a side, and it is what makes a
    control two-sided: an optimum below it is an instrument defect.

    Direction zero is always a net direction, so the bound applies to whichever
    class holds cell ``0``.
    """

    if square_side <= 0:
        raise ValueError("the shrunken side must be positive")
    count = 0
    while (count + 1) * square_side < outer_side:
        count += 1
    return count * count


def quarter_pitch_sites(outer_side: Fraction) -> tuple[Atom, ...]:
    """The nine unit-weight atoms on the pitch-``L / 4`` grid.

    Every axis-parallel square of side at least ``L / 4`` inside ``[0, L]^2``
    contains one of these, because a closed interval of that length inside
    ``[0, L]`` contains a multiple of ``L / 4`` other than ``0`` and ``L``. This
    is the classical nine-point bound's witness, and it is a feasible point of
    any class program whose ``Theta_0`` sits inside the tilts a ``B``-square of
    that side survives -- see `within_nine_point_tilt`.
    """

    quarter = outer_side / 4
    return tuple(
        Atom(f"{i}{j}", quarter * i, quarter * j, Fraction(1))
        for i in (1, 2, 3)
        for j in (1, 2, 3)
    )


def within_nine_point_tilt(
    classes: DirectionClasses, outer_side: Fraction, square_side: Fraction, label: int = NEAR
) -> bool:
    """Whether every angle of a class is a tilt the nine points still pierce.

    A ``B``-square tilted by ``theta`` contains an axis-parallel square of side
    ``B / (cos theta + sin theta)`` about its centre, and the pitch-``L / 4``
    grid pierces that whenever the side reaches ``L / 4``. So the condition is
    ``cos theta + sin theta <= 4 B / L`` at the class's outermost cell boundary,
    which `cos_plus_sin_at_most` decides in rationals.
    """

    return cos_plus_sin_at_most(classes.outer_tangent(label), 4 * square_side / outer_side)


@dataclass(frozen=True, slots=True)
class ClassRoundTiming:
    """Wall-clock split of one row-generation round of a class program."""

    index: int
    separation_seconds: float
    lp_seconds: float
    rows_held: int
    rows_added: int
    violated: int
    objective: float

    @property
    def seconds(self) -> float:
        return self.separation_seconds + self.lp_seconds


@dataclass(slots=True)
class ClassProgramLog:
    """One class-program search, and the point it stopped on."""

    rounds: int = 0
    rows: int = 0
    objective: float = float("inf")
    thresholds: tuple[float, float] = (0.0, 0.0)
    #: ``n_0 w_0 + n_1 w_1`` at the point the search stopped on.
    required: float = 0.0
    stopped: str = ""
    least_slack: float = float("inf")
    seconds: float = 0.0

    @property
    def converged(self) -> bool:
        return self.stopped.startswith("converged")

    @property
    def margin(self) -> float:
        """``M - n_0 w_0 - n_1 w_1``: negative refutes the composition."""

        return self.objective - self.required


def _class_lp(
    sizes: np.ndarray,
    matrix: np.ndarray,
    row_labels: np.ndarray,
    composition: Composition,
) -> tuple[np.ndarray, tuple[float, float], float] | None:
    """Solve the two-threshold LP on the rows held: weights, thresholds, ``M``.

    Variables are the orbit weights followed by ``w_0`` and ``w_1``. Each row
    says ``sum_a A[r, a] mu_a >= w_{class(r)}``; the single equality row is the
    normalisation ``n_0 w_0 + n_1 w_1 = 1``, which fixes the scale the
    homogeneous objective leaves free. Minimising ``M`` under it is the same
    program as minimising ``M - n_0 w_0 - n_1 w_1``, shifted by one.
    """

    orbits = sizes.size
    rows = matrix.shape[0]
    threshold_columns = np.zeros((rows, 2))
    threshold_columns[np.arange(rows), row_labels] = 1.0
    equality = np.zeros((1, orbits + 2))
    equality[0, orbits + NEAR] = float(composition.near)
    equality[0, orbits + TILTED] = float(composition.tilted)
    result = linprog(
        c=np.concatenate([sizes, np.zeros(2)]),
        A_ub=np.hstack([-matrix, threshold_columns]),
        b_ub=np.zeros(rows),
        A_eq=equality,
        b_eq=np.ones(1),
        bounds=[(0.0, None)] * (orbits + 2),
        method="highs",
    )
    if not result.success:
        return None
    point = np.asarray(result.x, dtype=float)
    # A class with count zero constrains nothing and is priced at nothing, so the
    # solver may return any nonnegative value for its threshold; zero is the value
    # that makes its (skipped) rows the vacuous constraints they are.
    thresholds = tuple(
        float(point[orbits + label]) if composition.count(label) > 0 else 0.0
        for label in CLASS_INDICES
    )
    return point[:orbits], (thresholds[NEAR], thresholds[TILTED]), float(result.fun)


def solve_class_program(
    grid: SiteGrid,
    square_side: Fraction,
    classes: DirectionClasses,
    composition: Composition,
    *,
    max_rounds: int = 60,
    rows_per_direction: int = 3,
    tolerance: float = 1e-9,
    timings: list[ClassRoundTiming] | None = None,
) -> tuple[np.ndarray, ClassProgramLog]:
    """Row-generate the two-threshold program until no placement is short.

    The float search. It differs from the unconditional covering loop in exactly
    two places: a placement is separated against its own class's threshold rather
    than against ``1``, and the LP carries the two thresholds as variables under
    one normalisation row. Directions whose class has count zero are skipped --
    see `Composition.active`.
    """

    started = time.perf_counter()
    positions = grid.positions()
    points = np.array([[float(x), float(y)] for x, y in positions])
    sizes = np.array([len(orbit) for orbit in grid.orbits], dtype=float)
    membership = np.zeros(len(positions), dtype=int)
    cursor = 0
    for index, orbit in enumerate(grid.orbits):
        membership[cursor : cursor + len(orbit)] = index
        cursor += len(orbit)

    directions = direction_net(classes.half_tangents)
    labels = classes.labels()
    outer, side = float(grid.outer_side), float(square_side)
    rows: list[np.ndarray] = []
    row_labels: list[int] = []
    held: set[bytes] = set()
    # Seed at zero mass and a positive threshold: with the normalisation split
    # evenly every placement is short, so the first round is what seeds the rows.
    # Seeding at a feasible point instead would let the loop report convergence
    # having never solved the program.
    weights = np.zeros(len(grid.orbits))
    thresholds = (1.0 / composition.total, 1.0 / composition.total)
    log = ClassProgramLog(thresholds=thresholds)

    for round_index in range(max_rounds):
        log.rounds = round_index + 1
        site_weights = weights[membership]
        violated = added = 0
        least_slack = float("inf")
        separation_started = time.perf_counter()
        for index, direction in enumerate(directions):
            label = labels[index]
            if composition.count(label) == 0:
                continue
            level = thresholds[label]
            for mass, _, _, covers in placement_cells(
                points, site_weights, direction, outer, side, keep=rows_per_direction
            ):
                if mass >= level - tolerance:
                    break
                row = np.zeros(len(grid.orbits))
                np.add.at(row, membership[covers], 1.0)
                if row.sum() == 0:
                    log.stopped = "a placement covers no site: the grid cannot cover"
                    log.seconds = time.perf_counter() - started
                    return weights, log
                violated += 1
                least_slack = min(least_slack, level - mass)
                key = row.tobytes() + bytes([label])
                if key not in held:
                    held.add(key)
                    rows.append(row)
                    row_labels.append(label)
                    added += 1
        separation_seconds = time.perf_counter() - separation_started
        log.rows = len(rows)
        log.least_slack = least_slack
        if violated == 0 or (added == 0 and least_slack <= LP_FEASIBILITY):
            # Nothing short, or every shortfall is a row the program already holds
            # and misses by no more than the solver's own feasibility tolerance.
            log.objective = float(sizes @ weights)
            log.stopped = "converged: every placement carries its class threshold"
            _record_round(
                timings,
                log,
                index=round_index,
                separation_seconds=separation_seconds,
                lp_seconds=0.0,
                violated=violated,
                added=added,
            )
            log.seconds = time.perf_counter() - started
            return weights, log
        if added == 0:
            log.stopped = f"a held row is short by {least_slack:.3e}: the solver's point is off"
            log.seconds = time.perf_counter() - started
            return weights, log

        lp_started = time.perf_counter()
        solved = _class_lp(sizes, np.vstack(rows), np.array(row_labels), composition)
        lp_seconds = time.perf_counter() - lp_started
        if solved is None:
            log.stopped = "linear program refused"
            log.seconds = time.perf_counter() - started
            return weights, log
        weights, thresholds, objective = solved
        log.thresholds = thresholds
        log.objective = objective
        log.required = (
            composition.near * thresholds[NEAR] + composition.tilted * thresholds[TILTED]
        )
        _record_round(
            timings,
            log,
            index=round_index,
            separation_seconds=separation_seconds,
            lp_seconds=lp_seconds,
            violated=violated,
            added=added,
        )
    log.stopped = f"round limit {max_rounds} reached"
    log.seconds = time.perf_counter() - started
    return weights, log


def _record_round(
    timings: list[ClassRoundTiming] | None,
    log: ClassProgramLog,
    *,
    index: int,
    separation_seconds: float,
    lp_seconds: float,
    violated: int,
    added: int,
) -> None:
    if timings is None:
        return
    timings.append(
        ClassRoundTiming(
            index=index,
            separation_seconds=separation_seconds,
            lp_seconds=lp_seconds,
            rows_held=log.rows,
            rows_added=added,
            violated=violated,
            objective=log.objective,
        )
    )


@dataclass(frozen=True, slots=True)
class ClassThresholds:
    """Exact class weights ``(w_0, w_1)``."""

    near: Fraction
    tilted: Fraction

    def __post_init__(self) -> None:
        if self.near < 0 or self.tilted < 0:
            raise ValueError("class weights must be nonnegative")

    def of(self, label: int) -> Fraction:
        return self.near if label == NEAR else self.tilted

    def required(self, composition: Composition) -> Fraction:
        """``n_0 w_0 + n_1 w_1``: the mass the composition would have to carry."""

        return composition.near * self.near + composition.tilted * self.tilted


@dataclass(frozen=True, slots=True)
class ClassMinimum:
    """The least mass any admissible core of one class carries, exactly."""

    label: int
    cells: int
    mass: Fraction | None
    direction: str | None


@dataclass(frozen=True, slots=True)
class ClassConditionReport:
    """One condition's verdict, with the numbers it was decided on."""

    name: str
    detail: str
    holds: bool = field(kw_only=True)


@dataclass(frozen=True, slots=True)
class ClassVerdict:
    """What the exact arithmetic says about one composition.

    Not a retained object. It refutes one composition of one net at one side;
    the five-condition `sqpack.fractional.certificate.Certificate` is what the
    retention gate decides, and it does not decide this.
    """

    conditions: tuple[ClassConditionReport, ...]
    composition: Composition
    thresholds: ClassThresholds
    total_mass: Fraction
    required: Fraction
    minima: tuple[ClassMinimum, ...]

    @property
    def margin(self) -> Fraction:
        """``M - n_0 w_0 - n_1 w_1``. The composition is refuted when it is negative."""

        return self.total_mass - self.required

    @property
    def refutes(self) -> bool:
        return all(condition.holds for condition in self.conditions)

    @property
    def failures(self) -> tuple[str, ...]:
        return tuple(c.name for c in self.conditions if not c.holds)


def class_minima(
    atoms: tuple[Atom, ...],
    classes: DirectionClasses,
    composition: Composition,
    outer_side: Fraction,
    square_side: Fraction,
) -> tuple[ClassMinimum, ...]:
    """The exact least covered mass over each active class's directions.

    One event-cell sweep per direction, in exact arithmetic, the same sweep the
    unconditional ``Condition 5`` is decided on. A class with count zero is
    reported empty rather than swept: its threshold is zero and its constraints
    are vacuous.
    """

    net = direction_net(classes.half_tangents)
    minima: list[ClassMinimum] = []
    for label in CLASS_INDICES:
        members = classes.members(label)
        if composition.count(label) == 0 or not members:
            minima.append(ClassMinimum(label, len(members), None, None))
            continue
        best: Fraction | None = None
        best_label: str | None = None
        for index in members:
            direction: Direction = net[index]
            mass, _ = minimum_covered_mass(atoms, direction, outer_side, square_side)
            if best is None or mass < best:
                best, best_label = mass, direction.label
        minima.append(ClassMinimum(label, len(members), best, best_label))
    return tuple(minima)


def _symmetry_report(
    atoms: tuple[Atom, ...], outer_side: Fraction, symmetry: str
) -> ClassConditionReport:
    """``Condition 1`` unchanged: the atoms must carry the declared symmetry.

    The class partition is stated on the folded arc, so an angle past ``pi / 4``
    reaches a cell only through a symmetry of both container and atom set.
    Declaring the symmetry without holding it leaves those angles unchecked.
    """

    name = "Condition 1 atoms carry the declared symmetry"
    if symmetry != "D4":
        return ClassConditionReport(
            name, f"only D4 is supported, not {symmetry!r}", holds=False
        )
    weights: dict[tuple[Fraction, Fraction], Fraction] = {}
    for atom in atoms:
        key = (atom.x, atom.y)
        if key in weights:
            return ClassConditionReport(name, f"two atoms share the site {key}", holds=False)
        weights[key] = atom.weight
    for atom in atoms:
        for image in d4_images(atom.x, atom.y, outer_side):
            if weights.get(image) != atom.weight:
                return ClassConditionReport(
                    name, f"site ({atom.x}, {atom.y}) has no image at {image}", holds=False
                )
    return ClassConditionReport(
        name, f"{len(atoms)} atoms closed under D4 about the centre", holds=True
    )


def decide_class_program(
    atoms: tuple[Atom, ...],
    outer_side: Fraction,
    square_side: Fraction,
    classes: DirectionClasses,
    composition: Composition,
    *,
    thresholds: ClassThresholds,
    symmetry: str = "D4",
) -> ClassVerdict:
    """Decide one composition exactly, on the frozen atoms and thresholds.

    Conditions 1, 3 and 4 are the unconditional ones; ``Condition 5'`` is the
    per-class threshold and ``Condition 2'`` the two-threshold mass bound. Every
    quantity is a ``Fraction`` and nothing here rounds or compares against a
    tolerance.
    """

    total = sum((atom.weight for atom in atoms), start=Fraction(0))
    required = thresholds.required(composition)
    minima = class_minima(atoms, classes, composition, outer_side, square_side)
    last = classes.half_tangents[-1]
    slack = last * last + 2 * last - 1
    gap = largest_half_gap_tangent(classes.half_tangents)
    product = square_side * (1 + gap)
    reports = [
        _symmetry_report(atoms, outer_side, symmetry),
        ClassConditionReport(
            "Condition 2' mass below n0 w0 + n1 w1",
            f"total {total} against {composition.near} * {thresholds.near} + "
            f"{composition.tilted} * {thresholds.tilted} = {required}",
            holds=total < required,
        ),
        ClassConditionReport(
            "Condition 3 net reaches pi/4",
            f"final half-tangent {last}, t^2 + 2t - 1 = {slack}",
            holds=slack >= 0,
        ),
        ClassConditionReport(
            "Condition 4 containment B(1 + D) < 1",
            f"B = {square_side}, D = {gap}, B(1 + D) = {product}",
            holds=product < 1,
        ),
    ]
    for minimum in minima:
        level = thresholds.of(minimum.label)
        if composition.count(minimum.label) == 0:
            reports.append(
                ClassConditionReport(
                    f"Condition 5' class {minimum.label} carries w{minimum.label}",
                    f"class holds no square in this composition; {minimum.cells} cells unswept",
                    holds=True,
                )
            )
            continue
        reports.append(
            ClassConditionReport(
                f"Condition 5' class {minimum.label} carries w{minimum.label}",
                f"least cell mass {minimum.mass} at direction {minimum.direction} "
                f"over {minimum.cells} cells, against w{minimum.label} = {level}",
                holds=minimum.mass is not None and minimum.mass >= level,
            )
        )
    return ClassVerdict(
        conditions=tuple(reports),
        composition=composition,
        thresholds=thresholds,
        total_mass=total,
        required=required,
        minima=minima,
    )


__all__ = [
    "CLASS_INDICES",
    "NEAR",
    "TILTED",
    "ClassConditionReport",
    "ClassMinimum",
    "ClassProgramLog",
    "ClassRoundTiming",
    "ClassThresholds",
    "ClassVerdict",
    "Composition",
    "DirectionClasses",
    "axis_disjoint_count",
    "cell_boundary_tangent",
    "class_minima",
    "cos_plus_sin_at_most",
    "decide_class_program",
    "end_cells",
    "largest_half_gap_tangent",
    "leading_cells",
    "quarter_pitch_sites",
    "sign_against_quadratic_surd",
    "solve_class_program",
    "within_nine_point_tilt",
]
