"""The exact event-cell sweep: least mass any placement of a square can cover.

Coverage is piecewise constant in the placed square's centre, and it can only
change where a site enters or leaves. Those coordinates are the event grid, so
a finite sweep over its open cells decides a continuum of placements exactly.
The placed square is closed, so an event boundary includes every atom covered
by either adjacent cell. With nonnegative weights this can only raise mass;
therefore a minimum occurs in an open cell and the sweep may omit boundaries.
Signed weights reverse that implication, so sweep entry points reject them.
"""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from dataclasses import dataclass
from fractions import Fraction
from itertools import pairwise
from math import lcm

import numpy as np

from sqpack.fractional.model import Atom, Direction, require_nonnegative_atom_weights

#: The dense integer grid holds signed partial sums of weights on the common scale.
#: Every entry is bounded in magnitude by the scaled total mass, and int64 leaves
#: room for a total four billion times larger than any certificate here has; past
#: this the integer route declines rather than risk a wrap, and the caller falls
#: back to ``Fraction`` arithmetic.
_INTEGER_MASS_LIMIT = 2**60


@dataclass(frozen=True, slots=True)
class SpanReduction:
    """The event grid with the reachable cells as one contiguous span per column.

    ``spans[k] = (i, j0, j1)`` says the cells ``(i, j0) .. (i, j1)`` inclusive are
    reachable. This is the same set the independently retained ``reduce_to_cells``
    reference lists one tuple at a time, held here in a form that costs thousands of
    entries where the expansion costs millions.
    """

    u_events: tuple[Fraction, ...]
    v_events: tuple[Fraction, ...]
    rectangles: tuple[tuple[Fraction, Fraction, Fraction, Fraction, Fraction], ...]
    spans: tuple[tuple[int, int, int], ...]


@dataclass(frozen=True, slots=True)
class MassGrid:
    """The dense scaled-mass grid the integer sweep fills, before it takes a minimum.

    ``grid[i, j]`` is the mass of event cell ``(i, j)`` multiplied by ``scale``, so
    every entry is an exact integer and a comparison against a rational threshold is
    decided in integers. Only the cells named by ``reduction.spans`` are reachable;
    the rest of the array is the prefix sum's scaffolding and means nothing on its own.

    This exists so that a readout of the grid -- how many reachable cells sit within a
    margin of one, say -- is the same array the decision was taken on rather than a
    second implementation of it.
    """

    reduction: SpanReduction
    grid: np.ndarray
    scale: int


@dataclass(frozen=True, slots=True)
class Reduction:
    u_events: tuple[Fraction, ...]
    v_events: tuple[Fraction, ...]
    rectangles: tuple[tuple[Fraction, Fraction, Fraction, Fraction, Fraction], ...]
    cells: tuple[tuple[int, int], ...]


def _clip(
    polygon: tuple[tuple[Fraction, Fraction], ...],
    bound: Fraction,
    *,
    keep_greater: bool,
) -> tuple[tuple[Fraction, Fraction], ...]:
    if not polygon:
        return ()
    output: list[tuple[Fraction, Fraction]] = []

    def inside(point: tuple[Fraction, Fraction]) -> bool:
        return point[0] >= bound if keep_greater else point[0] <= bound

    previous = polygon[-1]
    previous_inside = inside(previous)
    for current in polygon:
        current_inside = inside(current)
        if current_inside != previous_inside:
            u1, v1 = previous
            u2, v2 = current
            factor = Fraction(0) if u2 == u1 else (bound - u1) / (u2 - u1)
            output.append((bound, v1 + factor * (v2 - v1)))
        if current_inside:
            output.append(current)
        previous, previous_inside = current, current_inside
    return tuple(output)


def centre_domain(
    outer_side: Fraction, square_side: Fraction, direction: Direction
) -> tuple[tuple[Fraction, Fraction], ...]:
    """Centres at which the rotated square stays inside the container.

    In the rotated frame this is a rotated square, not its bounding box. The
    difference is not cosmetic: the box admits placements that hang outside the
    container, which cover no site and make a feasible program look infeasible.
    """
    cosine, sine = direction.ux, direction.uy
    half_extent = square_side * (cosine + sine) / 2
    low, high = half_extent, outer_side - half_extent
    corners = ((low, low), (high, low), (high, high), (low, high))
    return tuple((cosine * x + sine * y, -sine * x + cosine * y) for x, y in corners)


def _cell_witness(
    domain: tuple[tuple[Fraction, Fraction], ...],
    u_low: Fraction,
    u_high: Fraction,
    v_low: Fraction,
    v_high: Fraction,
) -> tuple[Fraction, Fraction]:
    """An exact point in an open event cell intersected with the centre domain.

    The closed intersection is convex. Its vertex average remains in the centre
    domain, and a strict check against all four cell edges ensures the point is
    also in the open event cell where the sweep's score applies.
    """
    clipped = _clip(_clip(domain, u_low, keep_greater=True), u_high, keep_greater=False)
    transposed = tuple((v, u) for u, v in clipped)
    transposed = _clip(_clip(transposed, v_low, keep_greater=True), v_high, keep_greater=False)
    clipped = tuple((u, v) for v, u in transposed)
    if not clipped:
        raise ValueError("reachable event cell has no feasible witness")
    count = len(clipped)
    witness = (
        sum((u for u, _ in clipped), start=Fraction(0)) / count,
        sum((v for _, v in clipped), start=Fraction(0)) / count,
    )
    if not (u_low < witness[0] < u_high and v_low < witness[1] < v_high):
        raise ValueError("reachable event cell has no interior feasible witness")
    return witness


def reduce_to_cells(
    atoms: tuple[Atom, ...],
    direction: Direction,
    outer_side: Fraction,
    square_side: Fraction,
) -> Reduction:
    """Legacy event-cell reduction, retained independently as a reference.

    This deliberately does not call ``reduce_to_spans``. The integer route and its
    span geometry therefore remain checkable against the cell reduction that decided
    the retained certificates before the optimization.
    """

    require_nonnegative_atom_weights(atoms)
    half = square_side / 2
    domain = centre_domain(outer_side, square_side, direction)
    u_low = min(u for u, _ in domain)
    u_high = max(u for u, _ in domain)
    v_low = min(v for _, v in domain)
    v_high = max(v for _, v in domain)
    rectangles: list[tuple[Fraction, Fraction, Fraction, Fraction, Fraction]] = []
    u_events = {u_low, u_high}
    v_events = {v_low, v_high}
    for atom in atoms:
        u = direction.ux * atom.x + direction.uy * atom.y
        v = direction.vx * atom.x + direction.vy * atom.y
        rectangle = (u - half, u + half, v - half, v + half, atom.weight)
        rectangles.append(rectangle)
        u_events.update(rectangle[:2])
        v_events.update(rectangle[2:4])

    ordered_u = tuple(sorted(u_events))
    ordered_v = tuple(sorted(v_events))
    cells: list[tuple[int, int]] = []
    for i, (u0, u1) in enumerate(pairwise(ordered_u)):
        if u1 <= u_low or u0 >= u_high:
            continue
        slab = _clip(_clip(domain, u0, keep_greater=True), u1, keep_greater=False)
        if not slab:
            continue
        low = min(v for _, v in slab)
        high = max(v for _, v in slab)
        if high <= low:
            continue
        j0 = max(0, bisect_right(ordered_v, low) - 1)
        j1 = min(len(ordered_v) - 2, bisect_left(ordered_v, high) - 1)
        cells.extend((i, j) for j in range(j0, j1 + 1))
    if not cells:
        raise ValueError("the centre domain produced no event cell")
    return Reduction(ordered_u, ordered_v, tuple(rectangles), tuple(cells))


def reduce_to_spans(
    atoms: tuple[Atom, ...],
    direction: Direction,
    outer_side: Fraction,
    square_side: Fraction,
) -> SpanReduction:
    """Event grid, per-site coverage rectangles, and the reachable cells as spans."""

    require_nonnegative_atom_weights(atoms)
    half = square_side / 2
    domain = centre_domain(outer_side, square_side, direction)
    u_low = min(u for u, _ in domain)
    u_high = max(u for u, _ in domain)
    v_low = min(v for _, v in domain)
    v_high = max(v for _, v in domain)
    rectangles: list[tuple[Fraction, Fraction, Fraction, Fraction, Fraction]] = []
    u_events = {u_low, u_high}
    v_events = {v_low, v_high}
    for atom in atoms:
        u = direction.ux * atom.x + direction.uy * atom.y
        v = direction.vx * atom.x + direction.vy * atom.y
        rectangle = (u - half, u + half, v - half, v + half, atom.weight)
        rectangles.append(rectangle)
        u_events.update(rectangle[:2])
        v_events.update(rectangle[2:4])

    ordered_u = tuple(sorted(u_events))
    ordered_v = tuple(sorted(v_events))
    spans: list[tuple[int, int, int]] = []
    for i, (u0, u1) in enumerate(pairwise(ordered_u)):
        if u1 <= u_low or u0 >= u_high:
            continue
        slab = _clip(_clip(domain, u0, keep_greater=True), u1, keep_greater=False)
        if not slab:
            continue
        low = min(v for _, v in slab)
        high = max(v for _, v in slab)
        if high <= low:
            continue
        j0 = max(0, bisect_right(ordered_v, low) - 1)
        j1 = min(len(ordered_v) - 2, bisect_left(ordered_v, high) - 1)
        if j1 >= j0:
            spans.append((i, j0, j1))
    if not spans:
        raise ValueError("the centre domain produced no event cell")
    return SpanReduction(ordered_u, ordered_v, tuple(rectangles), tuple(spans))


def weight_scale(atoms: tuple[Atom, ...]) -> int:
    """The least common denominator of the atom weights.

    Every weight is an integer multiple of ``1 / scale``, so a sum of weights on
    this scale is an integer and the arithmetic below is exact. The generator's
    ``rationalise`` emits weights representable on its configured scale. Reduction
    may cancel factors, so this least common denominator divides that configured scale
    but need not equal it.
    """

    scale = 1
    for atom in atoms:
        scale = lcm(scale, atom.weight.denominator)
    return scale


def minimum_covered_mass(
    atoms: tuple[Atom, ...],
    direction: Direction,
    outer_side: Fraction,
    square_side: Fraction,
) -> tuple[Fraction, tuple[Fraction, Fraction]]:
    """The least mass a reachable placement covers, with a witness centre.

    Decides in integers on the weights' common scale where that scale fits, and
    in ``Fraction`` arithmetic otherwise. Both are exact; the integer route is
    the one that runs, and the ``Fraction`` route is the reference it is tested
    against, cell for cell.
    """

    scale = weight_scale(atoms)
    total = sum(atom.weight for atom in atoms) * scale
    if total < _INTEGER_MASS_LIMIT:
        return minimum_covered_mass_integer(atoms, direction, outer_side, square_side, scale)
    return minimum_covered_mass_fraction(atoms, direction, outer_side, square_side)


def scaled_mass_grid(
    atoms: tuple[Atom, ...],
    direction: Direction,
    outer_side: Fraction,
    square_side: Fraction,
    scale: int,
) -> MassGrid:
    """Fill the dense integer mass grid one direction's sweep decides on.

    This is the first half of ``minimum_covered_mass_integer``, factored out because
    the grid it fills answers more than one question: the sweep takes its minimum, and
    a census reads the whole distribution off the same array. It checks the
    nonnegativity, integrality and overflow preconditions itself, so a reader of the
    grid inherits them rather than restating them.
    """

    require_nonnegative_atom_weights(atoms)
    if not isinstance(scale, int) or isinstance(scale, bool) or scale <= 0:
        raise ValueError("the common weight scale must be a positive integer")
    scaled_weights: list[int] = []
    for atom in atoms:
        scaled = atom.weight * scale
        if scaled.denominator != 1:
            raise ValueError("weights are not integers on the declared common scale")
        scaled_weights.append(int(scaled))
    if sum(scaled_weights) >= _INTEGER_MASS_LIMIT:
        raise ValueError("scaled total mass exceeds the safe int64 limit")

    reduction = reduce_to_spans(atoms, direction, outer_side, square_side)
    u_index = {value: index for index, value in enumerate(reduction.u_events)}
    v_index = {value: index for index, value in enumerate(reduction.v_events)}
    width, height = len(reduction.u_events), len(reduction.v_events)

    count = len(reduction.rectangles)
    left = np.empty(count, dtype=np.intp)
    right = np.empty(count, dtype=np.intp)
    bottom = np.empty(count, dtype=np.intp)
    top = np.empty(count, dtype=np.intp)
    weights = np.empty(count, dtype=np.int64)
    for k, (u1, u2, v1, v2, _weight) in enumerate(reduction.rectangles):
        left[k], right[k] = u_index[u1], u_index[u2]
        bottom[k], top[k] = v_index[v1], v_index[v2]
        weights[k] = scaled_weights[k]

    grid = np.zeros((width, height), dtype=np.int64)
    np.add.at(grid, (left, bottom), weights)
    np.subtract.at(grid, (right, bottom), weights)
    np.subtract.at(grid, (left, top), weights)
    np.add.at(grid, (right, top), weights)
    np.cumsum(grid, axis=1, out=grid)
    np.cumsum(grid, axis=0, out=grid)
    return MassGrid(reduction, grid, scale)


def minimum_covered_mass_integer(
    atoms: tuple[Atom, ...],
    direction: Direction,
    outer_side: Fraction,
    square_side: Fraction,
    scale: int,
) -> tuple[Fraction, tuple[Fraction, Fraction]]:
    """The optimized sweep in ``int64`` on the common weight scale. Exact.

    The difference array holds signed sums of scaled weights, so no entry can
    exceed the scaled total in magnitude. This public entry point checks the
    nonnegativity, integrality, and overflow preconditions itself; callers do not
    have to arrive through ``minimum_covered_mass`` for the result to be sound.
    The two prefix sums are what ``minimum_covered_mass_fraction`` does one
    cell at a time. The minimum is taken column by column over each reachable
    span, first occurrence winning, which is the order the reference walks its
    cells in, so the witness is the same cell and not merely a cell of the same
    mass.
    """

    filled = scaled_mass_grid(atoms, direction, outer_side, square_side, scale)
    reduction, grid = filled.reduction, filled.grid

    best: int | None = None
    witness_cell: tuple[int, int] | None = None
    for i, j0, j1 in reduction.spans:
        column = grid[i, j0 : j1 + 1]
        offset = int(np.argmin(column))
        score = int(column[offset])
        if best is None or score < best:
            best = score
            witness_cell = (i, j0 + offset)
    if best is None or witness_cell is None:  # pragma: no cover - reduce_to_spans raises
        raise ValueError("the sweep produced no reachable cell")
    i, j = witness_cell
    witness = _cell_witness(
        centre_domain(outer_side, square_side, direction),
        reduction.u_events[i],
        reduction.u_events[i + 1],
        reduction.v_events[j],
        reduction.v_events[j + 1],
    )
    return Fraction(best, scale), witness


def minimum_covered_mass_fraction(
    atoms: tuple[Atom, ...],
    direction: Direction,
    outer_side: Fraction,
    square_side: Fraction,
) -> tuple[Fraction, tuple[Fraction, Fraction]]:
    """The reference: the same sweep, one ``Fraction`` per cell.

    Its Fraction difference-array arithmetic and independently implemented cell
    reduction are retained from the version that decided every certificate before the
    optimization. The witness construction now clips to the feasible cell intersection;
    that strengthens the witness without changing the decision value.
    """

    reduction = reduce_to_cells(atoms, direction, outer_side, square_side)
    u_index = {value: index for index, value in enumerate(reduction.u_events)}
    v_index = {value: index for index, value in enumerate(reduction.v_events)}
    width, height = len(reduction.u_events), len(reduction.v_events)
    grid = [[Fraction(0)] * height for _ in range(width)]
    for u1, u2, v1, v2, weight in reduction.rectangles:
        left, right = u_index[u1], u_index[u2]
        bottom, top = v_index[v1], v_index[v2]
        grid[left][bottom] += weight
        grid[right][bottom] -= weight
        grid[left][top] -= weight
        grid[right][top] += weight
    for row in grid:
        for j in range(1, height):
            row[j] += row[j - 1]
    for i in range(1, width):
        previous, current = grid[i - 1], grid[i]
        for j in range(height):
            current[j] += previous[j]

    best: Fraction | None = None
    best_cell: tuple[int, int] | None = None
    for i, j in reduction.cells:
        score = grid[i][j]
        if best is None or score < best:
            best = score
            best_cell = (i, j)
    if best is None or best_cell is None:  # pragma: no cover - reduce_to_cells raises first
        raise ValueError("the sweep produced no reachable cell")
    i, j = best_cell
    witness = _cell_witness(
        centre_domain(outer_side, square_side, direction),
        reduction.u_events[i],
        reduction.u_events[i + 1],
        reduction.v_events[j],
        reduction.v_events[j + 1],
    )
    return best, witness
