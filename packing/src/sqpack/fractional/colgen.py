"""Dual-driven site column generation for the fractional covering LP.

`sqpack.fractional.generate` fixes the candidate sites before it starts: the
variables are the D4 orbits of one uniform grid, and row generation only
discovers the placements that constrain them. Every optimum it reports is
therefore a statement about that grid, not about the container. At L = 39/10
the difference bites -- grids 21, 23 and 25 all report exactly 12.000 for
n = 12, the number a certificate has to beat, and none of them shows that 12
is anything but the grid's own limit.

This module moves the site set as well. After row generation settles, the LP
dual prices the placements, and an orbit ``O`` is worth adding exactly when its
reduced cost ``|O| - sum_r y_r a_{r,O}`` is negative, where ``a_{r,O}`` counts
the members of ``O`` that placement ``r`` covers. Dividing by ``|O|`` reads
that as a statement about depth: the orbit-averaged depth of the dual has to
exceed 1. Since the primal is D4-symmetric in its columns, a supported
placement's eight images carry the same orbit counts, so the symmetrised dual
has the same value -- and its *pointwise* depth is exactly the orbit-averaged
depth of the original. Coverage is by closed squares, so that depth is upper
semi-continuous and its maximum is attained at a vertex of the arrangement of
the placements' edges: a finite candidate set finds it.

Adding sites can only lower the optimum, so old rows stay valid and only gain
a column. That is what makes the loop cheap enough to run at all.

The same dual, checked pointwise instead of orbit-averaged, is the by-product
in the other direction. If it carries total weight at least ``n`` while
covering no point of the container more than once, weak duality says no atom
measure of mass below ``n`` covers every placement at this ``(L, B, net)``:
sum_r y_r <= sum_r y_r mu(P_r) = integral of depth dmu <= mu(container). That
is a ceiling on the method, not on ``s(n)``, and it is only worth recording
when it is exact, so `check_ceiling` decides it in `Fraction` arithmetic.

Search runs in floating point because it is a search. Nothing here decides a
bound: the finish is the same rationalise-and-verify as `generate`, and the
exact verifier is the only thing that accepts a certificate.
"""

from __future__ import annotations

import logging
import math
import time
from collections.abc import Iterable
from dataclasses import dataclass, field
from fractions import Fraction
from itertools import combinations
from pathlib import Path
from typing import TextIO

import numpy as np
from scipy.optimize import linprog

from sqpack.fractional.certificate import Certificate, d4_images, verify
from sqpack.fractional.generate import (
    LP_FEASIBILITY,
    build_site_grid,
    direction_net,
    net_half_tangents,
    placement_cells,
)
from sqpack.fractional.model import Atom, Direction

# The eight orthogonal maps of the container's D4 group, as matrices acting on
# coordinates measured from the container centre. Written out rather than
# generated so the normals of a half-plane can be transformed by the same
# table: a line ``n . q = c`` maps to ``(G n) . q = c`` for orthogonal ``G``.
_D4_MATRICES: tuple[tuple[int, int, int, int], ...] = (
    (1, 0, 0, 1),
    (-1, 0, 0, 1),
    (1, 0, 0, -1),
    (-1, 0, 0, -1),
    (0, 1, 1, 0),
    (0, -1, 1, 0),
    (0, 1, -1, 0),
    (0, -1, -1, 0),
)


@dataclass(frozen=True, slots=True)
class SiteSet:
    """D4-closed candidate sites, grouped into the orbits that are the columns.

    The LP variable is a weight per orbit, and its objective coefficient is the
    orbit's size, so a column carries ``|O|`` mass and covers a placement with
    multiplicity. Unlike `generate.SiteGrid` the points are stored outright:
    column generation adds orbits that no grid contains.
    """

    outer_side: Fraction
    orbits: tuple[tuple[tuple[Fraction, Fraction], ...], ...]

    @property
    def size(self) -> int:
        return sum(len(orbit) for orbit in self.orbits)

    def sizes(self) -> np.ndarray:
        return np.array([len(orbit) for orbit in self.orbits], dtype=float)

    def positions(self) -> tuple[tuple[Fraction, Fraction], ...]:
        return tuple(point for orbit in self.orbits for point in orbit)

    def membership(self) -> np.ndarray:
        counts = [len(orbit) for orbit in self.orbits]
        return np.repeat(np.arange(len(self.orbits)), counts)

    def points(self) -> np.ndarray:
        return np.array([[float(x), float(y)] for x, y in self.positions()])


def d4_orbit(
    x: Fraction, y: Fraction, outer_side: Fraction
) -> tuple[tuple[Fraction, Fraction], ...]:
    """The point's D4 orbit as a set: a point on a mirror has fewer than eight."""

    return tuple(sorted(set(d4_images(x, y, outer_side))))


def site_set_from_points(
    outer_side: Fraction, points: set[tuple[Fraction, Fraction]]
) -> SiteSet:
    """Close a point set under D4 and group it into orbits."""

    seen: set[tuple[Fraction, Fraction]] = set()
    orbits: list[tuple[tuple[Fraction, Fraction], ...]] = []
    for point in sorted(points):
        if point in seen:
            continue
        orbit = d4_orbit(point[0], point[1], outer_side)
        seen.update(orbit)
        orbits.append(orbit)
    return SiteSet(outer_side, tuple(orbits))


def site_set_from_grids(
    outer_side: Fraction, counts: tuple[int, ...], inset: Fraction
) -> SiteSet:
    """The union of several uniform grids.

    A union is never worse than any of its members -- a site the optimum does
    not want takes weight zero -- so seeding with several resolutions costs
    only solve time, and buys the LP a choice between them.
    """

    points: set[tuple[Fraction, Fraction]] = set()
    for count in counts:
        points.update(build_site_grid(outer_side, count, inset).positions())
    return site_set_from_points(outer_side, points)


#: Site spacing the generator wants, in sites per ``B``-square width.
#:
#: ``generate_adaptive``'s ``grid_counts`` default ``(23, 31, 39)`` was tuned at
#: ``n = 12``'s side ``99/25``, and the counts ``(29, 39, 49)`` that finished a
#: column round at ``n = 20``'s ``24/5`` in ``376 s``, where ``(23, 31, 39)`` had
#: not finished it in ``3300 s``, are the *same density* at the larger side --
#: ``7.35, 9.98, 12.58`` sites per ``B`` against ``7.42, 10.11, 12.81``. So the
#: quantity that transfers across sides is the density, not the count, and
#: holding it is what ``site_counts_for_side`` does.
#:
#: The values here are measured rather than inherited. A five-rung ladder in the
#: production three-grid shape, run at two sides on one core (``BC-191``,
#: ``bench_colgen density``), puts an interior optimum at the same density both
#: times. At ``99/25``, deadline ``110 s``: densities ``5.73/7.75/9.78`` and
#: ``6.40/8.76/11.12`` did not converge and sat on the ``16.000000`` artefact;
#: ``7.42/10.11/12.47`` converged in ``60.8 s`` at ``12.312896``;
#: ``8.43/11.46/14.16`` converged in ``60.8 s`` at ``12.217676``; and
#: ``9.78/13.15/16.52`` did not converge in ``123.1 s``. At ``24/5``, deadline
#: ``140 s``, the objective reached ran ``25.000000`` (artefact), ``20.225314``,
#: ``20.168732``, ``19.339779``, ``19.871826`` over densities ``5.78/7.88/9.98``
#: to ``9.71/12.60/15.75``. Both sides put the minimum at ``8.5/11.5/14.25``,
#: which is where the two mechanisms cross: rounds to converge fall with density
#: (42, 33, 21, 23, 19 at ``99/25``) while seconds per round rise with it
#: (2.74, 3.45, 2.90, 2.64, 6.48), because separation is quadratic in the LP
#: support and a denser site set carries a larger one.
#:
#: The historically tuned grids are the *lower* edge of that band, not its
#: middle: at ``24/5`` the tuned density reached ``20.168732`` where the measured
#: optimum reached ``19.339779`` in comparable wall time.
SITE_DENSITIES: tuple[Fraction, ...] = (Fraction(17, 2), Fraction(23, 2), Fraction(57, 4))


def site_counts_for_side(
    outer_side: Fraction,
    square_side: Fraction,
    *,
    densities: tuple[Fraction, ...] = SITE_DENSITIES,
    inset: Fraction = Fraction(1, 2),
) -> tuple[int, ...]:
    """Grid counts holding the site spacing fixed relative to the ``B``-square.

    ``build_site_grid`` spreads ``count`` coordinates over ``span = L - 2 inset``,
    so its spacing is ``span / (count - 1)`` and grows with the container while
    the ``B``-square that has to cover the sites does not. A placement's covered
    mass is therefore read on a coarser and coarser net as the side rises, and
    the row generator pays for it: it is the one measured ``8.8x`` in the record.

    Fixing ``density = B / spacing`` instead inverts to
    ``count = round(span * density / B) + 1``, which is what this returns, one
    count per density. Counts below two are impossible for a grid and are
    clamped; a container smaller than the inset allows is the caller's error and
    ``build_site_grid`` raises on it.
    """

    span = outer_side - 2 * inset
    if span <= 0:
        raise ValueError("the inset leaves no room for sites")
    return tuple(max(2, round(span * density / square_side) + 1) for density in densities)


@dataclass(frozen=True, slots=True)
class Square:
    """A closed square as two exact slabs, in coordinates from the centre.

    ``|a . q - u| <= half`` and ``|b . q - v| <= half`` with ``b`` the quarter
    turn of ``a``. Centring is what makes the D4 images a table lookup, and
    exactness is what lets `check_ceiling` be a decision rather than a reading.
    """

    ax: Fraction
    ay: Fraction
    u: Fraction
    bx: Fraction
    by: Fraction
    v: Fraction
    half: Fraction

    def covers(self, x: Fraction, y: Fraction) -> bool:
        """Whether the closed square contains a point given in centred coordinates."""

        if abs(self.ax * x + self.ay * y - self.u) > self.half:
            return False
        return abs(self.bx * x + self.by * y - self.v) <= self.half

    def images(self) -> tuple[Square, ...]:
        """The eight D4 images. Duplicates are kept: a square with a nontrivial
        stabiliser repeats, and repeating it is what keeps the total weight of a
        symmetrised dual equal to the weight it started with."""

        return tuple(
            Square(
                m00 * self.ax + m01 * self.ay,
                m10 * self.ax + m11 * self.ay,
                self.u,
                m00 * self.bx + m01 * self.by,
                m10 * self.bx + m11 * self.by,
                self.v,
                self.half,
            )
            for m00, m01, m10, m11 in _D4_MATRICES
        )

    def lines(self) -> tuple[tuple[Fraction, Fraction, Fraction], ...]:
        """The four edge lines ``n . q = c`` bounding the square."""

        return (
            (self.ax, self.ay, self.u - self.half),
            (self.ax, self.ay, self.u + self.half),
            (self.bx, self.by, self.v - self.half),
            (self.bx, self.by, self.v + self.half),
        )


def square_at(
    direction: Direction,
    centre: tuple[Fraction, Fraction],
    outer_side: Fraction,
    square_side: Fraction,
) -> Square:
    """The ``B``-square at one net direction with the given absolute centre."""

    x = centre[0] - outer_side / 2
    y = centre[1] - outer_side / 2
    return Square(
        direction.ux,
        direction.uy,
        direction.ux * x + direction.uy * y,
        direction.vx,
        direction.vy,
        direction.vx * x + direction.vy * y,
        square_side / 2,
    )


def symmetrise(
    weighted: tuple[tuple[Square, Fraction], ...],
) -> tuple[tuple[Square, Fraction], ...]:
    """Spread each dual weight over the placement's eight D4 images.

    Sound because the columns are D4 orbits: an image of a placement covers the
    same number of members of every orbit, so the symmetrised dual satisfies
    the same constraints and has the same total weight.
    """

    return tuple(
        (image, weight / 8) for square, weight in weighted for image in square.images()
    )


def reduced_cost(
    orbit: tuple[tuple[Fraction, Fraction], ...],
    weighted: tuple[tuple[Square, Fraction], ...],
    outer_side: Fraction,
) -> Fraction:
    """``|O| - sum_r y_r a_{r,O}``: what adding this orbit costs the dual.

    Negative means the column improves the primal, which is the same statement
    as orbit-averaged depth above 1 once divided by ``|O|``.
    """

    half = outer_side / 2
    centred = [(x - half, y - half) for x, y in orbit]
    price = Fraction(0)
    for square, weight in weighted:
        covered = sum(1 for x, y in centred if square.covers(x, y))
        price += weight * covered
    return Fraction(len(orbit)) - price


@dataclass(slots=True)
class Rows:
    """Generated placement rows, with the placements that produced them.

    The coefficient matrix alone is not enough: when a site orbit is added,
    every existing row needs the number of that orbit's members it covers, and
    only the placement can say.
    """

    directions: list[int] = field(default_factory=list)
    centres: list[tuple[float, float]] = field(default_factory=list)
    matrix: np.ndarray = field(default_factory=lambda: np.zeros((0, 0)))
    pending: list[np.ndarray] = field(default_factory=list)
    keys: set[bytes] = field(default_factory=set)

    def __len__(self) -> int:
        return len(self.directions)

    def add(self, direction_index: int, centre: tuple[float, float], row: np.ndarray) -> bool:
        """Hold a row unless an identical coefficient vector is already held."""

        key = row.tobytes()
        if key in self.keys:
            return False
        self.keys.add(key)
        self.directions.append(direction_index)
        self.centres.append(centre)
        self.pending.append(row)
        return True

    def stacked(self) -> np.ndarray:
        """The coefficient matrix. Rows are folded in a round at a time: one
        `vstack` per new row would copy the whole matrix per row and turn row
        generation quadratic in a quantity that reaches five figures."""

        if self.pending:
            self.matrix = np.vstack([self.matrix, np.array(self.pending)])
            self.pending = []
        return self.matrix

    def add_column(self, column: np.ndarray) -> None:
        self.matrix = np.hstack([self.stacked(), column[:, None]])
        # A new column changes every row's byte image, so the duplicate index
        # has to be rebuilt or it would reject rows it has never seen.
        self.keys = {row.tobytes() for row in self.matrix}


@dataclass(slots=True)
class RoundTiming:
    """Wall-clock split of one row-generation round, for the benchmark harness.

    ``solve_rows`` appends one of these per round when a caller hands it a list.
    The split is the whole point: BC-191's baseline says row generation is 79 to
    94 per cent of a round, and the only way to keep that honest as the sides
    grow is to have the loop time itself rather than have a harness re-implement
    it. ``index`` is ``-1`` for the warm solve on rows carried in from an
    earlier site set, which does no separation at all.
    """

    index: int
    separation_seconds: float
    lp_seconds: float
    rows_held: int
    rows_added: int
    violated: int
    objective: float
    support: int = 0

    @property
    def seconds(self) -> float:
        return self.separation_seconds + self.lp_seconds


@dataclass(slots=True)
class LpSolution:
    """One row-generation run to convergence, and the dual it ended on."""

    weights: np.ndarray
    duals: np.ndarray
    objective: float = float("inf")
    rounds: int = 0
    rows: int = 0
    stopped: str = ""
    # The least mass any surveyed placement carries at the weights the loop
    # ended on, over every direction and not only the violated ones. A
    # converged loop leaves it at or above 1, and that number is the evidence
    # that the loop stopped for want of a violated placement rather than on a
    # budget -- the distinction a candidate has to show, and one the record
    # could not report before because ``least`` only ever saw violations.
    least_covered: float = float("inf")

    @property
    def converged(self) -> bool:
        return self.stopped.startswith("converged")


def solve_lp(sites: SiteSet, rows: Rows) -> tuple[np.ndarray, np.ndarray, float] | None:
    """Solve the covering LP on the rows held, returning weights, dual and value.

    The dual is what column generation prices with, so it is read out here
    rather than reconstructed later: ``ineqlin.marginals`` are derivatives of
    the objective in ``b_ub`` and so non-positive, and the covering dual is
    their negative.
    """

    result = linprog(
        c=sites.sizes(),
        A_ub=-rows.stacked(),
        b_ub=-np.ones(len(rows)),
        bounds=[(0.0, None)] * len(sites.orbits),
        method="highs",
    )
    if not result.success:
        return None
    duals = np.maximum(-np.asarray(result.ineqlin.marginals, dtype=float), 0.0)
    return np.asarray(result.x, dtype=float), duals, float(result.fun)


def _record(
    timings: list[RoundTiming] | None,
    index: int,
    separation_seconds: float,
    lp_seconds: float,
    *,
    rows_held: int,
    rows_added: int,
    violated: int,
    support: int,
    objective: float,
) -> None:
    """Append one round's split, when a caller asked for the split."""

    if timings is None:
        return
    timings.append(
        RoundTiming(
            index=index,
            separation_seconds=separation_seconds,
            lp_seconds=lp_seconds,
            rows_held=rows_held,
            rows_added=rows_added,
            violated=violated,
            objective=objective,
            support=support,
        )
    )


def solve_rows(
    sites: SiteSet,
    square_side: Fraction,
    half_tangents: tuple[Fraction, ...],
    rows: Rows,
    *,
    max_rounds: int = 60,
    rows_per_direction: int = 3,
    tolerance: float = 1e-9,
    timings: list[RoundTiming] | None = None,
    deadline: float | None = None,
) -> LpSolution:
    """Row-generate on a fixed site set until no placement is short of mass 1.

    ``rows`` is carried in and mutated: rows survive a change of site set, so a
    later call starts from every placement the earlier ones found.

    Pass ``timings`` to have each round append its own separation/LP split. The
    list is the only thing it touches, so a timed run and an untimed one take
    the same decisions on the same numbers.

    ``deadline`` is a ``time.perf_counter`` value past which no further round
    starts. It is a wall and not a convergence criterion: the solution it
    returns is not ``converged``, so nothing downstream can mistake a run that
    ran out of clock for one that ran out of violated placements.
    """

    points = sites.points()
    sizes = sites.sizes()
    membership = sites.membership()
    columns = len(sites.orbits)
    directions = direction_net(half_tangents)
    outer = float(sites.outer_side)
    side = float(square_side)
    if rows.matrix.shape[0] == 0:
        rows.matrix = np.zeros((0, columns))

    # Seed at zero, not at one. Unit weights already cover every placement, so
    # the first separation would find nothing and report a convergence that
    # never solved anything.
    weights = np.zeros(columns)
    duals = np.zeros(len(rows))
    solution = LpSolution(weights, duals, rows=len(rows))
    # Rows carried in from an earlier site set already price the new column, so
    # start from their optimum rather than from zero and spend the first
    # separation pass on placements the previous site set never violated.
    if len(rows) > 0:
        started = time.perf_counter()
        warm = solve_lp(sites, rows)
        elapsed = time.perf_counter() - started
        if warm is not None:
            weights, duals, objective = warm
            solution.weights, solution.duals, solution.objective = weights, duals, objective
        if timings is not None:
            timings.append(
                RoundTiming(
                    index=-1,
                    separation_seconds=0.0,
                    lp_seconds=elapsed,
                    rows_held=len(rows),
                    rows_added=0,
                    violated=0,
                    objective=solution.objective,
                    support=int(np.count_nonzero(weights)),
                )
            )

    for round_index in range(max_rounds):
        if deadline is not None and time.perf_counter() >= deadline:
            solution.stopped = f"deadline reached after {round_index} rounds"
            return solution
        solution.rounds = round_index + 1
        separation_started = time.perf_counter()
        site_weights = weights[membership]
        # The separation grid is built from the sites that carry weight, so the
        # support -- not the site count -- is what makes a round expensive.
        support = int(np.count_nonzero(site_weights))
        # Count violations, not newly held rows. A row set carried in from an
        # earlier site set already holds most of what the oracle finds, so
        # counting additions would read "nothing new" as "nothing violated"
        # and return the seed weights as an optimum of zero. A violated
        # placement yields a row the set does not hold -- a held row is
        # satisfied by LP feasibility, up to the solver's own tolerance, which
        # is the one case the guard below has to close -- so the loop still
        # terminates.
        violated = 0
        added = 0
        least = float("inf")
        least_covered = float("inf")
        for index, direction in enumerate(directions):
            for mass, cu, cv, covers in placement_cells(
                points, site_weights, direction, outer, side, keep=rows_per_direction
            ):
                # Cells arrive in ascending mass, so the first at a direction is
                # that direction's least covered placement whether or not it is
                # violated. Reading it before the break is the only way the
                # converged round reports a number at all.
                least_covered = min(least_covered, mass)
                if mass >= 1 - tolerance:
                    break
                row = np.zeros(columns)
                np.add.at(row, membership[covers], 1.0)
                if row.sum() == 0:
                    solution.stopped = "a placement covers no site: the sites cannot cover"
                    return solution
                violated += 1
                least = min(least, mass)
                added += rows.add(index, (cu, cv), row)
        solution.rows = len(rows)
        solution.least_covered = least_covered
        separation_seconds = time.perf_counter() - separation_started

        if violated == 0 or (added == 0 and least >= 1 - LP_FEASIBILITY):
            # Nothing violated, or every violation is a row already held and
            # missed by no more than the solver's feasibility tolerance, which
            # the rationaliser's bump absorbs. Re-solving the same rows would
            # return the same point, and the loop would spend its rounds on it.
            solution.objective = float(sizes @ weights)
            solution.stopped = "converged: every placement covers mass 1"
            _record(
                timings,
                round_index,
                separation_seconds,
                0.0,
                rows_held=len(rows),
                rows_added=added,
                violated=violated,
                support=support,
                objective=solution.objective,
            )
            return solution
        if added == 0:
            solution.stopped = (
                f"a held row is violated by {1 - least:.3e}: the solver's point is off"
            )
            _record(
                timings,
                round_index,
                separation_seconds,
                0.0,
                rows_held=len(rows),
                rows_added=added,
                violated=violated,
                support=support,
                objective=solution.objective,
            )
            return solution

        lp_started = time.perf_counter()
        solved = solve_lp(sites, rows)
        lp_seconds = time.perf_counter() - lp_started
        if solved is None:
            solution.stopped = "linear program refused the generated rows"
            _record(
                timings,
                round_index,
                separation_seconds,
                lp_seconds,
                rows_held=len(rows),
                rows_added=added,
                violated=violated,
                support=support,
                objective=solution.objective,
            )
            return solution
        weights, duals, objective = solved
        solution.weights = weights
        solution.duals = duals
        solution.objective = objective
        _record(
            timings,
            round_index,
            separation_seconds,
            lp_seconds,
            rows_held=len(rows),
            rows_added=added,
            violated=violated,
            support=support,
            objective=objective,
        )
    solution.stopped = f"round limit {max_rounds} reached"
    return solution


def dual_squares(
    rows: Rows,
    duals: np.ndarray,
    half_tangents: tuple[Fraction, ...],
    outer_side: Fraction,
    square_side: Fraction,
    *,
    support_cap: int,
    denominator: int = 10**6,
) -> tuple[tuple[Square, Fraction], ...]:
    """The dual support as exact reachable squares with exact weights.

    The rows were found in floating point, so both the centre and the weight
    are rationalised here; the centre is then clamped into the exact centre
    domain, because a square whose centre has drifted outside it is not a
    placement and would make any ceiling read from it worthless. Truncating the
    support to the heaviest ``support_cap`` rows only discards weight, which
    weakens both uses of the dual without making either unsound.
    """

    directions = direction_net(half_tangents)
    order = [index for index in np.argsort(-duals) if duals[index] > 1e-9]
    weighted: list[tuple[Square, Fraction]] = []
    for index in order[:support_cap]:
        direction = directions[rows.directions[index]]
        cu, cv = rows.centres[index]
        cosine, sine = float(direction.ux), float(direction.uy)
        x = Fraction(cosine * cu - sine * cv).limit_denominator(denominator)
        y = Fraction(sine * cu + cosine * cv).limit_denominator(denominator)
        extent = square_side * (direction.ux + direction.uy) / 2
        x = min(max(x, extent), outer_side - extent)
        y = min(max(y, extent), outer_side - extent)
        weight = Fraction(float(duals[index])).limit_denominator(denominator)
        if weight <= 0:
            continue
        weighted.append((square_at(direction, (x, y), outer_side, square_side), weight))
    return tuple(weighted)


def _float_squares(
    weighted: tuple[tuple[Square, Fraction], ...],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float]:
    """Axes, offsets and weights of a weighted square family, in floats."""

    axes = np.array(
        [[[float(s.ax), float(s.ay)], [float(s.bx), float(s.by)]] for s, _ in weighted]
    )
    offsets = np.array([[float(s.u), float(s.v)] for s, _ in weighted])
    weights = np.array([float(w) for _, w in weighted])
    half = float(weighted[0][0].half) if weighted else 0.0
    return axes, offsets, weights, half


def _depths(
    query: np.ndarray,
    axes: np.ndarray,
    offsets: np.ndarray,
    weights: np.ndarray,
    half: float,
    *,
    slack: float,
) -> np.ndarray:
    """Weighted depth of every query point, in chunks to bound the memory."""

    depths = np.zeros(query.shape[0])
    chunk = max(1, 4_000_000 // max(1, axes.shape[0]))
    for start in range(0, query.shape[0], chunk):
        block = query[start : start + chunk]
        first = np.abs(block @ axes[:, 0, :].T - offsets[None, :, 0]) <= half + slack
        second = np.abs(block @ axes[:, 1, :].T - offsets[None, :, 1]) <= half + slack
        depths[start : start + chunk] = (first & second) @ weights
    return depths


def _arrangement_lines(
    weighted: tuple[tuple[Square, Fraction], ...], outer_side: Fraction
) -> list[tuple[Fraction, Fraction, Fraction]]:
    """Every edge line of the family, plus the container walls.

    The walls matter: without them the faces that meet the boundary need not
    have a vertex, and a depth maximum sitting in one would go unseen.
    """

    half = outer_side / 2
    lines: list[tuple[Fraction, Fraction, Fraction]] = [
        (Fraction(1), Fraction(0), -half),
        (Fraction(1), Fraction(0), half),
        (Fraction(0), Fraction(1), -half),
        (Fraction(0), Fraction(1), half),
    ]
    seen: set[tuple[Fraction, Fraction, Fraction]] = set(lines)
    for square, _ in weighted:
        for line in square.lines():
            normalised = (
                line
                if line[0] > 0 or (line[0] == 0 and line[1] > 0)
                else (
                    -line[0],
                    -line[1],
                    -line[2],
                )
            )
            if normalised not in seen:
                seen.add(normalised)
                lines.append(normalised)
    return lines


def _vertices(
    lines: list[tuple[Fraction, Fraction, Fraction]], outer_side: Fraction
) -> tuple[np.ndarray, list[tuple[int, int]]]:
    """Pairwise intersections inside the container, in floats with their sources."""

    data = np.array([[float(nx), float(ny), float(c)] for nx, ny, c in lines])
    pairs = list(combinations(range(len(lines)), 2))
    first = np.array([p[0] for p in pairs])
    second = np.array([p[1] for p in pairs])
    a, b, e = data[first, 0], data[first, 1], data[first, 2]
    c, d, f = data[second, 0], data[second, 1], data[second, 2]
    determinant = a * d - b * c
    usable = np.abs(determinant) > 1e-12
    x = np.where(usable, (e * d - f * b) / np.where(usable, determinant, 1.0), 0.0)
    y = np.where(usable, (a * f - c * e) / np.where(usable, determinant, 1.0), 0.0)
    half = float(outer_side) / 2 + 1e-12
    inside = usable & (np.abs(x) <= half) & (np.abs(y) <= half)
    points = np.stack([x[inside], y[inside]], axis=1)
    sources = [pairs[index] for index in np.flatnonzero(inside)]
    return points, sources


def _exact_intersection(
    first: tuple[Fraction, Fraction, Fraction], second: tuple[Fraction, Fraction, Fraction]
) -> tuple[Fraction, Fraction] | None:
    determinant = first[0] * second[1] - first[1] * second[0]
    if determinant == 0:
        return None
    x = (first[2] * second[1] - second[2] * first[1]) / determinant
    y = (first[0] * second[2] - second[0] * first[2]) / determinant
    return x, y


@dataclass(frozen=True, slots=True)
class Candidate:
    """A site orbit worth adding, and what the dual says it is worth."""

    point: tuple[Fraction, Fraction]
    orbit: tuple[tuple[Fraction, Fraction], ...]
    averaged_depth: Fraction
    cost: Fraction


def rank_candidates(
    sites: SiteSet,
    weighted: tuple[tuple[Square, Fraction], ...],
    *,
    survey: int = 96,
    wanted: int = 1,
    simplify: tuple[int, ...] = (10**4, 10**6, 10**8),
) -> list[Candidate]:
    """The container points of greatest orbit-averaged depth, as exact orbits.

    The symmetrised dual's pointwise depth *is* the original dual's
    orbit-averaged depth, so one scan of the arrangement answers the column
    generation question. Floats rank the vertices; the best of them are then
    rebuilt exactly from the two lines that made them, and the reported depth
    is the exact one. A vertex sits on four edges at once, so its coordinates
    are ratios of the net's rationals and can be unusable as an atom site --
    hence the ladder of simplifications, each accepted only if the reduced cost
    survives it.

    Returning more than one is the usual multi-column pricing compromise: only
    the first is priced against the dual that will exist after it is added, but
    a round costs a full row generation and the alternative is paying that for
    a gain of a few hundredths.
    """

    if not weighted:
        return []
    symmetric = symmetrise(weighted)
    axes, offsets, weights, half = _float_squares(symmetric)
    lines = _arrangement_lines(symmetric, sites.outer_side)
    points, sources = _vertices(lines, sites.outer_side)
    if points.shape[0] == 0:
        return []
    depths = _depths(points, axes, offsets, weights, half, slack=1e-9)
    ranked = np.argsort(-depths)[: max(survey, wanted)]

    centre = sites.outer_side / 2
    held = {point for orbit in sites.orbits for point in orbit}
    found: list[Candidate] = []
    for index in ranked:
        exact = _exact_intersection(lines[sources[index][0]], lines[sources[index][1]])
        if exact is None:
            continue
        for denominator in (*simplify, 0):
            x = exact[0] if denominator == 0 else exact[0].limit_denominator(denominator)
            y = exact[1] if denominator == 0 else exact[1].limit_denominator(denominator)
            if abs(x) > centre or abs(y) > centre:
                continue
            site = (x + centre, y + centre)
            if site in held:
                continue
            orbit = d4_orbit(site[0], site[1], sites.outer_side)
            cost = reduced_cost(orbit, weighted, sites.outer_side)
            if cost >= 0:
                continue
            held.update(orbit)
            found.append(Candidate(site, orbit, 1 - cost / len(orbit), cost))
            break
        if len(found) >= wanted:
            break
    found.sort(key=lambda candidate: -candidate.averaged_depth)
    return found


def best_candidate(
    sites: SiteSet,
    weighted: tuple[tuple[Square, Fraction], ...],
    *,
    survey: int = 96,
    simplify: tuple[int, ...] = (10**4, 10**6, 10**8),
) -> Candidate | None:
    """The single deepest orbit worth adding, or ``None`` if the dual has none."""

    found = rank_candidates(sites, weighted, survey=survey, wanted=1, simplify=simplify)
    return found[0] if found else None


@dataclass(frozen=True, slots=True)
class CeilingResult:
    """What the final dual proves about every atom measure, not just this one."""

    proved: bool
    n: int
    total_weight: Fraction
    max_pointwise_depth: Fraction
    feasible_total: Fraction
    squares: int
    vertices: int
    detail: str


def check_ceiling(
    n: int,
    weighted: tuple[tuple[Square, Fraction], ...],
    outer_side: Fraction,
    *,
    screen: float = 1e-7,
) -> CeilingResult:
    """Decide whether a dual bars every atom measure of mass below ``n``.

    The caller passes an already symmetrised family, because symmetry is a
    property of the dual it wants to check rather than something this function
    should assume. Feasibility is pointwise depth at most 1 everywhere, and
    since coverage is by closed squares the depth is upper semi-continuous:
    every face of the arrangement has a vertex in its closure carrying at least
    the face's depth, so the vertices decide it. Floats only screen; every
    vertex that comes near the bound is re-decided in exact arithmetic.

    A dual that exceeds 1 somewhere is not thrown away. Scaling it by the
    reciprocal of its maximum depth restores feasibility exactly, and the
    ceiling it then proves is the scaled total -- which is the honest number
    when the raw total was bought by double-covering part of the container.
    """

    if not weighted:
        return CeilingResult(
            proved=False,
            n=n,
            total_weight=Fraction(0),
            max_pointwise_depth=Fraction(0),
            feasible_total=Fraction(0),
            squares=0,
            vertices=0,
            detail="the dual is empty",
        )
    total = sum((weight for _, weight in weighted), start=Fraction(0))
    axes, offsets, floats, half = _float_squares(weighted)
    lines = _arrangement_lines(weighted, outer_side)
    points, sources = _vertices(lines, outer_side)
    depths = _depths(points, axes, offsets, floats, half, slack=1e-9)
    near = np.flatnonzero(depths >= 1 - screen)

    worst = Fraction(0)
    for index in near:
        exact = _exact_intersection(lines[sources[index][0]], lines[sources[index][1]])
        if exact is None:
            continue
        depth = sum(
            (weight for square, weight in weighted if square.covers(exact[0], exact[1])),
            start=Fraction(0),
        )
        worst = max(worst, depth)
    feasible = total if worst <= 1 else total / worst
    proved = feasible >= n
    detail = (
        f"total {float(total):.6f} over {len(weighted)} squares, "
        f"max pointwise depth {float(worst):.6f} at {points.shape[0]} vertices "
        f"({near.size} decided exactly), feasible total {float(feasible):.6f}"
    )
    return CeilingResult(
        proved=proved,
        n=n,
        total_weight=total,
        max_pointwise_depth=worst,
        feasible_total=feasible,
        squares=len(weighted),
        vertices=int(points.shape[0]),
        detail=detail,
    )


#: Denominator the rationaliser rounds weights up to.
#:
#: Raised from ``200_000`` on the measurement in ``BC-191``. The rounding loss is
#: ``atoms / (2 * scale) + bump * total`` -- the average round-up is half a
#: quantum, and the bump is a floor the scale cannot get under. Measured on one
#: LP point at each of two atom counts, four scales each: at 137 atoms the loss
#: ran ``4.45e-4``, ``8.9e-5``, ``3.2e-5``, ``1.5e-5`` for scales ``2e5``,
#: ``1e6``, ``4e6``, ``2e7``; at 333 atoms ``7.87e-4``, ``1.77e-4``, ``4.9e-5``,
#: ``2.2e-5``. The model reproduces the record's own figure -- ``0.005255``
#: predicted against ``0.005314`` measured at the ``n = 12`` rung's 2097 atoms
#: and scale ``200_000``, where the margin that survived was ``0.001040``.
#:
#: The finer scale is free to verify. The exact sweep builds its grid from atom
#: *coordinates*; the scale enters only as the magnitude of the ``int64``
#: weights. Measured: 2.860 / 2.888 / 2.829 s at 137 atoms and 8.974 / 8.247 /
#: 8.242 s at 333 atoms over scales ``1e6`` to ``2e7``, and the largest scaled
#: total seen was ``225_099_903`` against ``sweep._INTEGER_MASS_LIMIT = 2**60``,
#: a headroom factor of ``5.1e9``.
#:
#: It is also safe independently of the measurement. A held row sits at least
#: ``1 - LP_FEASIBILITY`` (``1e-7``); the bump lifts it to at least
#: ``1 + 9e-7 > 1`` whatever the scale, and rounding up only adds. All eight
#: rationalisations above were accepted by the exact verifier.
#:
#: ``2e7`` was rejected, not on verification cost -- that was flat -- but because
#: the win over ``4e6`` is ``2.1e-4`` at 2097 atoms against a bump floor of
#: ``1.2e-5``, for five times the stored numerator.
DEFAULT_SCALE = 4_000_000


def rationalise_sites(
    sites: SiteSet,
    weights: np.ndarray,
    *,
    scale: int = DEFAULT_SCALE,
    bump: Fraction = Fraction(1000001, 1000000),
) -> tuple[Atom, ...]:
    """Bump, round up to a multiple of ``1/scale``, and drop the empty orbits.

    Rounding up keeps the coverage rows valid after rationalisation and the
    bump absorbs the solver's own slack; both inflate the total, which is the
    quantity that has to stay below ``n``. Rounding down instead is D-433: the
    solver leaves every row tight, so any shaved weight drops a tight cell
    below 1 and the exact verifier refuses a certificate that was there.
    """

    atoms: list[Atom] = []
    for index, orbit in enumerate(sites.orbits):
        raw = Fraction(float(weights[index])).limit_denominator(10**9) * bump
        if raw <= 0:
            continue
        weight = Fraction(max(math.ceil(raw * scale), 1), scale)
        for x, y in orbit:
            atoms.append(Atom(f"{len(atoms):04d}", x, y, weight))
    return tuple(atoms)


@dataclass(slots=True)
class ColumnRound:
    """One pass: solve on the current sites, then price a new orbit."""

    index: int
    rows: int
    orbits: int
    sites: int
    objective: float
    lp_rounds: int
    averaged_depth: float
    cost: float
    added: int
    note: str
    seconds: float = float("nan")
    least_covered: float = float("inf")


@dataclass(slots=True)
class AdaptiveLog:
    rounds: list[ColumnRound] = field(default_factory=list)
    stopped: str = ""
    objective: float = float("inf")
    total_mass: Fraction | None = None
    ceiling: CeilingResult | None = None
    accepted: bool = False
    failures: tuple[str, ...] = ()
    least_cell_mass: Fraction | None = None
    least_covered: float = float("inf")


logger = logging.getLogger(__name__)


def _write(handle: TextIO | None, text: str) -> None:
    """Report one line of the adaptive run: to the log file when one was asked for, and
    to the module logger so a caller that wants a terminal transcript configures logging
    rather than inheriting a print."""
    logger.info("%s", text)
    if handle is not None:
        handle.write(text + "\n")
        handle.flush()


def generate_adaptive(
    n: int,
    outer_side: Fraction,
    square_side: Fraction,
    *,
    grid_counts: tuple[int, ...] = (23, 31, 39),
    inset: Fraction = Fraction(1, 2),
    angle_limit: Fraction,
    direction_steps: int,
    scale: int = DEFAULT_SCALE,
    max_rounds: int = 60,
    column_rounds: int = 8,
    columns_per_round: int = 1,
    rows_per_direction: int = 3,
    support_cap: int = 32,
    settle: float = 0.0,
    log_path: Path | None = None,
    decide: bool = False,
    seed_points: Iterable[tuple[Fraction, Fraction]] = (),
    timings: list[RoundTiming] | None = None,
    deadline: float | None = None,
) -> tuple[Certificate | None, AdaptiveLog]:
    """Row- and column-generate; decide the result exactly only when asked.

    The loop alternates: rows until every placement is covered, then the dual,
    then the one site orbit whose reduced cost is most negative. Sites only
    ever get added, so the optimum is non-increasing across rounds and the row
    set carries over intact. It stops when no orbit is worth adding, when the
    deepest candidate's averaged depth is within ``settle`` of 1 -- the dual
    has settled and a further column buys hundredths -- or at the round cap,
    which is a budget and not a convergence criterion.

    ``decide`` runs the exact verifier on the rationalised candidate in memory. It is
    off by default because the retention boundary is freeze-then-decide: a candidate
    is written to disk first and its bytes are decided by ``devtools.decide_certificate``
    by both routes, so that what is retained is what was decided (D-433, D-441). An
    in-memory decision is convenient for a small exploratory call and proves nothing
    about any file; nothing may be retained on its word.

    ``seed_points`` are extra sites -- a retained certificate's atoms carried
    to this side, say -- unioned with the grids and closed under D4, so a
    second site-set construction can be run through the same loop. A point
    outside the container is refused. ``timings`` is handed to every
    `solve_rows` call, so a caller that wants the per-LP-round split while
    the run is still going gets it; the list is the only thing it touches.
    ``deadline`` is a ``time.perf_counter`` value handed to `solve_rows`: past
    it no row round starts, the loop returns unconverged, and the log carries
    what was reached -- a wall, never a convergence criterion.
    """

    half_tangents = net_half_tangents(angle_limit, direction_steps)
    sites = site_set_from_grids(outer_side, grid_counts, inset)
    extra = set(seed_points)
    if extra:
        for x, y in extra:
            if not (0 <= x <= outer_side and 0 <= y <= outer_side):
                raise ValueError(f"seed site ({x}, {y}) lies outside the container")
        sites = site_set_from_points(outer_side, set(sites.positions()) | extra)
    rows = Rows()
    log = AdaptiveLog()
    handle = log_path.open("a") if log_path is not None else None
    solution = LpSolution(np.zeros(len(sites.orbits)), np.zeros(0))
    try:
        for index in range(column_rounds):
            started = time.perf_counter()
            solution = solve_rows(
                sites,
                square_side,
                half_tangents,
                rows,
                max_rounds=max_rounds,
                rows_per_direction=rows_per_direction,
                timings=timings,
                deadline=deadline,
            )
            seconds = time.perf_counter() - started
            note = solution.stopped
            depth = float("nan")
            cost = float("nan")
            found: list[Candidate] = []
            if solution.converged:
                weighted = dual_squares(
                    rows,
                    solution.duals,
                    half_tangents,
                    outer_side,
                    square_side,
                    support_cap=support_cap,
                )
                found = rank_candidates(sites, weighted, wanted=columns_per_round)
                if found:
                    depth = float(found[0].averaged_depth)
                    cost = float(found[0].cost)
                    note = f"adding {len(found)} orbits, deepest at {found[0].point}"
                else:
                    note = "no candidate orbit has averaged depth above 1"
            log.rounds.append(
                ColumnRound(
                    index=index,
                    rows=len(rows),
                    orbits=len(sites.orbits),
                    sites=sites.size,
                    objective=solution.objective,
                    lp_rounds=solution.rounds,
                    averaged_depth=depth,
                    cost=cost,
                    added=len(found),
                    note=note,
                    seconds=seconds,
                    least_covered=solution.least_covered,
                )
            )
            _write(
                handle,
                f"round {index}: rows={len(rows)} orbits={len(sites.orbits)} "
                f"sites={sites.size} lp_rounds={solution.rounds} "
                f"objective={solution.objective:.9f} depth={depth:.9f} "
                f"cost={cost:.9f} least_covered={solution.least_covered:.9f} "
                f"seconds={seconds:.1f} | {note}",
            )
            # Stop before extending on the last round: the weights that get
            # rationalised below are the ones the LP just returned, and a site
            # set carrying a column those weights do not have is not a solution.
            if (
                not solution.converged
                or not found
                or found[0].averaged_depth <= 1 + settle
                or index + 1 == column_rounds
            ):
                break
            sites = SiteSet(outer_side, (*sites.orbits, *(c.orbit for c in found)))
            for candidate in found:
                rows.add_column(orbit_column(rows, candidate.orbit, half_tangents, square_side))

        log.objective = solution.objective
        log.stopped = solution.stopped
        log.least_covered = solution.least_covered
        if solution.converged:
            weighted = dual_squares(
                rows,
                solution.duals,
                half_tangents,
                outer_side,
                square_side,
                support_cap=support_cap,
            )
            log.ceiling = check_ceiling(n, symmetrise(weighted), outer_side)
            _write(handle, f"ceiling: proved={log.ceiling.proved} {log.ceiling.detail}")
        if not solution.converged:
            return None, log

        atoms = rationalise_sites(sites, solution.weights, scale=scale)
        if not atoms:
            log.stopped = "every site rounded to zero weight"
            return None, log
        candidate_certificate = Certificate(
            n=n,
            outer_side=outer_side,
            square_side=square_side,
            atoms=atoms,
            half_tangents=half_tangents,
        )
        log.total_mass = candidate_certificate.total_mass
        _write(
            handle,
            f"rationalised total {candidate_certificate.total_mass} "
            f"= {float(candidate_certificate.total_mass):.9f} "
            f"against LP optimum {solution.objective:.9f} "
            f"over {len(atoms)} atoms",
        )
        if decide:
            verdict = verify(candidate_certificate)
            log.accepted = verdict.accepted
            log.failures = verdict.failures
            log.least_cell_mass = verdict.minimum_cell_mass
            _write(
                handle,
                f"verdict: accepted={verdict.accepted} failures={verdict.failures} "
                f"least cell mass {verdict.minimum_cell_mass}",
            )
        return candidate_certificate, log
    finally:
        if handle is not None:
            handle.close()


def orbit_column(
    rows: Rows,
    orbit: tuple[tuple[Fraction, Fraction], ...],
    half_tangents: tuple[Fraction, ...],
    square_side: Fraction,
) -> np.ndarray:
    """How many members of a new orbit each held row's placement covers."""

    directions = direction_net(half_tangents)
    half = float(square_side) / 2
    column = np.zeros(len(rows))
    if len(rows) == 0:
        return column
    row_directions = np.array(rows.directions)
    centres = np.array(rows.centres)
    members = np.array([[float(x), float(y)] for x, y in orbit])
    for index, direction in enumerate(directions):
        which = np.flatnonzero(row_directions == index)
        if which.size == 0:
            continue
        cosine, sine = float(direction.ux), float(direction.uy)
        u = members[:, 0] * cosine + members[:, 1] * sine
        v = -members[:, 0] * sine + members[:, 1] * cosine
        near_u = np.abs(u[None, :] - centres[which, 0][:, None]) <= half
        near_v = np.abs(v[None, :] - centres[which, 1][:, None]) <= half
        column[which] = (near_u & near_v).sum(axis=1)
    return column


__all__ = [
    "DEFAULT_SCALE",
    "SITE_DENSITIES",
    "AdaptiveLog",
    "Candidate",
    "CeilingResult",
    "ColumnRound",
    "LpSolution",
    "RoundTiming",
    "Rows",
    "SiteSet",
    "Square",
    "best_candidate",
    "check_ceiling",
    "d4_orbit",
    "dual_squares",
    "generate_adaptive",
    "orbit_column",
    "placement_cells",
    "rank_candidates",
    "rationalise_sites",
    "reduced_cost",
    "site_counts_for_side",
    "site_set_from_grids",
    "site_set_from_points",
    "solve_lp",
    "solve_rows",
    "square_at",
    "symmetrise",
    "verify",
]
