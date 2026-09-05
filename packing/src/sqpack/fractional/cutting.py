"""Cutting planes on the packing side: the column generator's site loop, reversed.

`sqpack.fractional.colgen` searches for a covering measure of mass below ``n``:
it holds a site set, generates placement rows until every placement carries
mass 1, and then adds the one site orbit the dual says is deepest. Its dual --
the weights on the held rows -- is a fractional packing whose depth is at most
1 *at the sites*, and `sqpack.fractional.ceiling` decides whether that packing
is feasible at every vertex of its own arrangement, which is where its depth
actually peaks. At ``n = 11`` and side ``191/50`` the two numbers differed by
53 per cent (T-018's ``next_rung``), because a dual that never saw the
arrangement's vertices was never asked to be feasible there.

This module runs the loop that the gap calls for. Each iteration re-solves the
covering program on the current sites (which is the same linear program as the
packing program on the current rows), reads the dual as an exact D4-symmetric
family of ``B``-square placements, enumerates every vertex of that family's
arrangement exactly, and adds the vertices where the exact depth exceeds 1 as
new site orbits. Adding a site is adding a depth constraint, so the packing
total is non-increasing and the exact maximum depth is driven towards 1; the
quantity that matters, the total divided by the exact maximum depth, is a
lower bound on the fractional packing value ``nu*(L)`` at every iteration and
by weak duality on the covering value ``tau*(L)``.

Floats propose, rationals confirm. The row oracle and the linear program run
in floating point; every row's centre is snapped to a rational with a bounded
denominator the moment it is held, and the coefficient matrix is rebuilt from
those snapped centres so that the program the solver sees and the family the
verifier checks are the same placements. The depth at a vertex is decided in
exact arithmetic, the scaling that restores feasibility is an exact division,
and nothing reported here comes from a sampled depth.
"""

from __future__ import annotations

import json
import math
import time
from collections.abc import Sequence
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any, TextIO

import numpy as np
from scipy import sparse

from sqpack.fractional.ceiling import (
    NEAR_PARALLEL,
    SCREEN_MARGIN,
    CeilingCertificate,
    CeilingVerdict,
    Line,
    Placement,
    arrangement_lines,
    container_vertices,
    exact_intersection,
    float_family,
    loose_membership,
    verify_ceiling,
)
from sqpack.fractional.colgen import (
    Rows,
    SiteSet,
    d4_orbit,
    site_counts_for_side,
    site_set_from_grids,
    site_set_from_points,
    solve_lp,
    solve_rows,
)
from sqpack.fractional.generate import direction_net
from sqpack.fractional.model import Direction

#: A held row as the exact placement it stands for: net direction index and the
#: absolute centre, rationalised to the row denominator and clamped into the
#: centre domain.
ExactRow = tuple[int, Fraction, Fraction]

#: How far outside a snapped placement a site may sit and still be counted as
#: covered in the linear program. This is the safe direction: the program then
#: sees a depth at least the exact depth, so a vertex it has constrained cannot
#: come back violated by a rounding error.
COVER_SLACK = 1e-9

#: Vertices closer than this, in floats, are one site for the purposes of a
#: round: the deepest region of an arrangement is a cluster of near-coincident
#: intersections, and adding all of them buys the program nothing.
CLUSTER_RADIUS = 1e-7


@dataclass(frozen=True, slots=True)
class SupportEntry:
    """One row of the dual support: a placement at a net direction with weight."""

    direction: int
    half_tangent: Fraction
    centre_x: Fraction
    centre_y: Fraction
    weight: Fraction


def snap_centre(
    direction: Direction,
    centre: tuple[float, float],
    outer_side: Fraction,
    square_side: Fraction,
    denominator: int,
) -> tuple[Fraction, Fraction]:
    """The row's absolute centre as a bounded rational inside the centre domain.

    Mirrors `colgen.dual_squares`: the rotated-frame centre is mapped back to
    absolute coordinates, rationalised, and clamped so that the placement it
    names lies in the container.
    """

    cu, cv = centre
    cosine, sine = float(direction.ux), float(direction.uy)
    x = Fraction(cosine * cu - sine * cv).limit_denominator(denominator)
    y = Fraction(sine * cu + cosine * cv).limit_denominator(denominator)
    extent = square_side * (direction.ux + direction.uy) / 2
    x = min(max(x, extent), outer_side - extent)
    y = min(max(y, extent), outer_side - extent)
    return x, y


def symmetric_placements(
    entries: tuple[SupportEntry, ...] | list[SupportEntry],
    outer_side: Fraction,
    square_side: Fraction,
) -> tuple[Placement, ...]:
    """Every entry spread over its eight D4 images at one eighth of the weight.

    The four rotations keep the half-tangent; the four reflections send the
    angle ``theta`` to ``pi/2 - theta``, whose half-tangent is ``(1 - t) / (1 + t)``.
    Duplicates are kept for a placement with a nontrivial stabiliser, which is
    what keeps the symmetrised total equal to the total it started with.
    """

    placements: list[Placement] = []
    for entry in entries:
        x, y = entry.centre_x, entry.centre_y
        if not (0 <= x <= outer_side and 0 <= y <= outer_side):
            raise ValueError(f"placement centre ({x}, {y}) is outside [0, {outer_side}]^2")
        if entry.weight < 0:
            raise ValueError("support weights must be non-negative")
        far_x, far_y = outer_side - x, outer_side - y
        t = entry.half_tangent
        mirrored = (1 - t) / (1 + t)
        share = entry.weight / 8
        for px, py in ((x, y), (far_y, x), (far_x, far_y), (y, far_x)):
            placements.append(Placement(t, px, py, share, square_side))
        for px, py in ((far_x, y), (x, far_y), (y, x), (far_y, far_x)):
            placements.append(Placement(mirrored, px, py, share, square_side))
    return tuple(placements)


def support_entries(
    exact_rows: list[ExactRow],
    duals: np.ndarray,
    half_tangents: tuple[Fraction, ...],
    *,
    support_cap: int,
    weight_denominator: int,
) -> tuple[SupportEntry, ...]:
    """The heaviest ``support_cap`` rows of the dual, with exact weights on a
    common denominator."""

    order = [index for index in np.argsort(-duals) if duals[index] > 1e-9]
    entries: list[SupportEntry] = []
    for index in order[:support_cap]:
        # One common denominator for every weight, so that a depth -- a sum of
        # weights -- stays a small rational instead of an lcm of many.
        weight = Fraction(round(float(duals[index]) * weight_denominator), weight_denominator)
        if weight <= 0:
            continue
        direction, x, y = exact_rows[index]
        entries.append(SupportEntry(direction, half_tangents[direction], x, y, weight))
    return tuple(entries)


def coverage_matrix(
    exact_rows: list[ExactRow],
    sites: SiteSet,
    half_tangents: tuple[Fraction, ...],
    square_side: Fraction,
    *,
    slack: float = COVER_SLACK,
) -> np.ndarray:
    """How many members of each site orbit each snapped placement covers."""

    directions = direction_net(half_tangents)
    points = sites.points()
    membership = sites.membership()
    columns = len(sites.orbits)
    matrix = np.zeros((len(exact_rows), columns))
    if not exact_rows or points.shape[0] == 0:
        return matrix
    onehot = sparse.csr_matrix(
        (np.ones(points.shape[0]), (membership, np.arange(points.shape[0]))),
        shape=(columns, points.shape[0]),
    )
    row_directions = np.array([row[0] for row in exact_rows])
    xs = np.array([float(row[1]) for row in exact_rows])
    ys = np.array([float(row[2]) for row in exact_rows])
    half = float(square_side) / 2 + slack
    for index, direction in enumerate(directions):
        which = np.flatnonzero(row_directions == index)
        if which.size == 0:
            continue
        cosine, sine = float(direction.ux), float(direction.uy)
        u = points[:, 0] * cosine + points[:, 1] * sine
        v = -points[:, 0] * sine + points[:, 1] * cosine
        cu = xs[which] * cosine + ys[which] * sine
        cv = -xs[which] * sine + ys[which] * cosine
        near = (np.abs(u[None, :] - cu[:, None]) <= half) & (
            np.abs(v[None, :] - cv[:, None]) <= half
        )
        matrix[which] = np.asarray((onehot @ near.astype(float).T).T)
    return matrix


def rebuild_rows(
    rows: Rows,
    exact_rows: list[ExactRow],
    sites: SiteSet,
    half_tangents: tuple[Fraction, ...],
    square_side: Fraction,
) -> None:
    """Replace the held coefficient matrix by one read from the snapped centres."""

    rows.stacked()
    if len(rows) != len(exact_rows):
        raise ValueError("every held row needs a snapped centre before the rebuild")
    rows.matrix = coverage_matrix(exact_rows, sites, half_tangents, square_side)
    rows.pending = []
    rows.keys = {row.tobytes() for row in rows.matrix}


def depths_above(
    certificate: CeilingCertificate,
    vertices: list[tuple[Fraction, Fraction]],
    threshold: Fraction = Fraction(1),
) -> tuple[list[tuple[Fraction, Fraction, Fraction]], Fraction, int]:
    """Every vertex whose exact depth exceeds ``threshold``, the exact maximum,
    and how many vertices were decided exactly.

    The screen is `ceiling.maximum_depth`'s: a vertex whose loosened float depth
    is below ``threshold - SCREEN_MARGIN`` cannot exceed the threshold. On the
    vertices that survive, a placement that contains the point with the margin
    to spare is a member and one that misses it by the margin is not, so only
    the placements whose edge passes within the margin of the vertex -- the two
    that made it, typically -- are decided by exact arithmetic.
    """

    if not vertices:
        return [], Fraction(0), 0
    normals, offsets, halves, weights = float_family(certificate)
    points = np.array([[float(x), float(y)] for x, y in vertices])
    placements = certificate.placements
    found: list[tuple[Fraction, Fraction, Fraction]] = []
    worst = Fraction(0)
    decided = 0
    limit = float(threshold) - SCREEN_MARGIN
    chunk = max(1, 2_000_000 // max(1, len(placements)))
    tight = halves[None, :] - SCREEN_MARGIN
    for start in range(0, points.shape[0], chunk):
        block = points[start : start + chunk]
        loose = loose_membership(block, normals, offsets, halves)
        depth = loose.astype(float) @ weights
        candidates = np.flatnonzero(depth >= limit)
        if candidates.size == 0:
            continue
        sub = block[candidates]
        first = np.abs(sub @ normals[:, 0, :].T - offsets[None, :, 0]) <= tight
        second = np.abs(sub @ normals[:, 1, :].T - offsets[None, :, 1]) <= tight
        strict = first & second
        for local, index in enumerate(candidates):
            x, y = vertices[start + int(index)]
            exact = Fraction(0)
            for member in np.flatnonzero(strict[local]):
                exact += placements[member].weight
            for member in np.flatnonzero(loose[index] & ~strict[local]):
                if placements[member].contains(x, y):
                    exact += placements[member].weight
            decided += 1
            worst = max(worst, exact)
            if exact > threshold:
                found.append((exact, x, y))
    found.sort(key=lambda entry: (-entry[0], entry[1], entry[2]))
    return found, worst, decided


def select_site_orbits(
    deep: list[tuple[Fraction, Fraction, Fraction]],
    sites: SiteSet,
    outer_side: Fraction,
    *,
    cap: int,
    cluster_radius: float = CLUSTER_RADIUS,
) -> list[tuple[Fraction, tuple[tuple[Fraction, Fraction], ...]]]:
    """The deepest ``cap`` violating vertices as new D4 site orbits.

    Vertices are taken in order of exact depth; a vertex whose orbit is already
    held, or that lies within the cluster radius of one chosen this round, is
    passed over. The sites are the exact vertices: a rounded site would sit
    off the edges that meet at the vertex and constrain a different point.
    """

    held = {point for orbit in sites.orbits for point in orbit}
    chosen: list[tuple[Fraction, tuple[tuple[Fraction, Fraction], ...]]] = []
    chosen_points: list[tuple[float, float]] = []
    for depth, x, y in deep:
        orbit = d4_orbit(x, y, outer_side)
        if any(point in held for point in orbit):
            continue
        fx, fy = float(x), float(y)
        if any(
            abs(fx - px) <= cluster_radius and abs(fy - py) <= cluster_radius
            for px, py in chosen_points
        ):
            continue
        held.update(orbit)
        chosen.append((depth, orbit))
        chosen_points.extend((float(px), float(py)) for px, py in orbit)
        if len(chosen) >= cap:
            break
    return chosen


def float_vertices(
    certificate: CeilingCertificate, lines: list[Line]
) -> tuple[np.ndarray, np.ndarray, dict[int, tuple[Fraction, Fraction]]]:
    """Every pairwise intersection inside the container, in floats, with its two
    lines; nearly parallel pairs are decided exactly and their exact point kept.

    The float points only screen. A vertex that matters is rebuilt exactly from
    the two lines that made it, which is how `colgen.rank_candidates` reads the
    same arrangement. Float-identical duplicates are dropped; exact duplicates
    that differ in the last float digit survive and cost one extra decision.
    """

    side = certificate.outer_side
    data = np.array([[float(a), float(b), float(c)] for a, b, c in lines])
    count = len(lines)
    high = float(side) + SCREEN_MARGIN
    xs: list[np.ndarray] = []
    ys: list[np.ndarray] = []
    firsts: list[np.ndarray] = []
    seconds: list[np.ndarray] = []
    exact_points: list[tuple[int, int, tuple[Fraction, Fraction]]] = []
    for i in range(count - 1):
        a, b, e = data[i]
        c, d, f = data[i + 1 :, 0], data[i + 1 :, 1], data[i + 1 :, 2]
        determinant = a * d - b * c
        far = np.abs(determinant) > NEAR_PARALLEL
        safe = np.where(far, determinant, 1.0)
        x = (e * d - f * b) / safe
        y = (a * f - c * e) / safe
        inside = far & (x >= -SCREEN_MARGIN) & (x <= high) & (y >= -SCREEN_MARGIN) & (y <= high)
        index = np.flatnonzero(inside)
        xs.append(x[index])
        ys.append(y[index])
        firsts.append(np.full(index.size, i, dtype=np.int64))
        seconds.append(index.astype(np.int64) + i + 1)
        for offset in np.flatnonzero(~far):
            exact = exact_intersection(lines[i], lines[i + 1 + int(offset)])
            if exact is None:
                continue
            if 0 <= exact[0] <= side and 0 <= exact[1] <= side:
                exact_points.append((i, i + 1 + int(offset), exact))
    if xs:
        points = np.stack([np.concatenate(xs), np.concatenate(ys)], axis=1)
        pairs = np.stack([np.concatenate(firsts), np.concatenate(seconds)], axis=1)
    else:
        points = np.zeros((0, 2))
        pairs = np.zeros((0, 2), dtype=np.int64)
    if points.shape[0]:
        _, keep = np.unique(points, axis=0, return_index=True)
        keep.sort()
        points, pairs = points[keep], pairs[keep]
    cache: dict[int, tuple[Fraction, Fraction]] = {}
    for i, j, exact in exact_points:
        cache[points.shape[0]] = exact
        points = np.vstack([points, [[float(exact[0]), float(exact[1])]]])
        pairs = np.vstack([pairs, [[i, j]]])
    return points, pairs, cache


@dataclass(slots=True)
class Separation:
    """What one exact separation found: the maximum, its cost, and the new sites."""

    max_depth: Fraction
    decided: int
    vertices: int
    violating: int
    chosen: list[tuple[Fraction, tuple[tuple[Fraction, Fraction], ...]]]


def screened_separation(
    certificate: CeilingCertificate,
    lines: list[Line],
    sites: SiteSet,
    *,
    cap: int,
    select_above: Fraction,
    cluster_radius: float = CLUSTER_RADIUS,
) -> Separation:
    """The exact maximum depth over the arrangement, and the deepest ``cap``
    violating vertices as new site orbits, deciding exactly only where it matters.

    Every vertex gets a loosened float depth, which exceeds its exact depth up to
    the rounding of a double. Vertices are then visited in descending float
    depth: each is rebuilt exactly and its depth decided exactly, and the walk
    stops once the float depth falls below the best exact depth found less the
    screen margin, because no later vertex can beat it. That certifies the
    maximum on a few hundred exact decisions instead of every vertex near 1,
    and it is the same screen `ceiling.maximum_depth` uses with a bound that
    tightens as the walk proceeds. Sites are chosen from the same walk.
    """

    side = certificate.outer_side
    points, pairs, cache = float_vertices(certificate, lines)
    total = int(points.shape[0])
    if total == 0:
        return Separation(Fraction(0), 0, 0, 0, [])
    normals, offsets, halves, weights = float_family(certificate)
    placements = certificate.placements
    depth = np.zeros(total)
    chunk = max(1, 2_000_000 // max(1, len(placements)))
    for start in range(0, total, chunk):
        block = points[start : start + chunk]
        depth[start : start + chunk] = (
            loose_membership(block, normals, offsets, halves).astype(float) @ weights
        )
    order = np.argsort(-depth, kind="stable")
    floor = float(select_above)
    violating = int(np.count_nonzero(depth > floor))
    held = {point for orbit in sites.orbits for point in orbit}
    best = Fraction(0)
    decided = 0
    chosen: list[tuple[Fraction, tuple[tuple[Fraction, Fraction], ...]]] = []
    cluster = np.zeros((8 * max(cap, 1), 2))
    filled = 0
    tight = halves[None, :] - SCREEN_MARGIN
    finished = False
    for start in range(0, total, 256):
        block_index = order[start : start + 256]
        sub = points[block_index]
        loose = loose_membership(sub, normals, offsets, halves)
        first = np.abs(sub @ normals[:, 0, :].T - offsets[None, :, 0]) <= tight
        second = np.abs(sub @ normals[:, 1, :].T - offsets[None, :, 1]) <= tight
        strict = first & second
        for local, index in enumerate(block_index):
            float_depth = float(depth[index])
            wants_max = float_depth >= float(best) - SCREEN_MARGIN
            wants_site = len(chosen) < cap and float_depth > floor
            if not wants_max and not wants_site:
                finished = True
                break
            fx, fy = float(sub[local, 0]), float(sub[local, 1])
            if (
                wants_site
                and filled
                and bool(
                    np.any(
                        (np.abs(cluster[:filled, 0] - fx) <= cluster_radius)
                        & (np.abs(cluster[:filled, 1] - fy) <= cluster_radius)
                    )
                )
            ):
                wants_site = False
                if not wants_max:
                    continue
            exact = cache.get(int(index))
            if exact is None:
                exact = exact_intersection(
                    lines[int(pairs[index, 0])], lines[int(pairs[index, 1])]
                )
            if exact is None or not (0 <= exact[0] <= side and 0 <= exact[1] <= side):
                continue
            x, y = exact
            value = Fraction(0)
            for member in np.flatnonzero(strict[local]):
                value += placements[member].weight
            for member in np.flatnonzero(loose[local] & ~strict[local]):
                if placements[member].contains(x, y):
                    value += placements[member].weight
            decided += 1
            best = max(best, value)
            if wants_site and value > select_above:
                orbit = d4_orbit(x, y, side)
                if any(point in held for point in orbit):
                    continue
                held.update(orbit)
                chosen.append((value, orbit))
                for px, py in orbit:
                    if filled < cluster.shape[0]:
                        cluster[filled] = (float(px), float(py))
                        filled += 1
        if finished:
            break
    return Separation(best, decided, total, violating, chosen)


@dataclass(slots=True)
class Iteration:
    """One pass of the loop, in the numbers the record quotes."""

    index: int
    sites: int
    orbits: int
    rows: int
    support: int
    rows_converged: bool
    rows_stopped: str
    rows_objective: float
    objective: float
    raw_total: Fraction
    max_depth: Fraction
    scaled_total: Fraction
    vertices: int
    decided: int
    violating: int
    added: int
    seconds_rows: float
    seconds_lp: float
    seconds_separation: float
    note: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "sites": self.sites,
            "orbits": self.orbits,
            "rows": self.rows,
            "support": self.support,
            "rows_converged": self.rows_converged,
            "rows_stopped": self.rows_stopped,
            "rows_objective": self.rows_objective,
            "objective": self.objective,
            "raw_total": str(self.raw_total),
            "raw_total_float": float(self.raw_total),
            "max_depth": str(self.max_depth),
            "max_depth_float": float(self.max_depth),
            "scaled_total": str(self.scaled_total),
            "scaled_total_float": float(self.scaled_total),
            "vertices": self.vertices,
            "decided": self.decided,
            "violating": self.violating,
            "added": self.added,
            "seconds_rows": self.seconds_rows,
            "seconds_lp": self.seconds_lp,
            "seconds_separation": self.seconds_separation,
            "note": self.note,
        }


@dataclass(slots=True)
class CuttingLog:
    iterations: list[Iteration] = field(default_factory=list)
    stopped: str = ""
    best_scaled_total: Fraction = Fraction(0)
    best_iteration: int = -1
    best_family: CeilingCertificate | None = None
    verdict: CeilingVerdict | None = None
    sites: SiteSet | None = None
    exact_rows: list[ExactRow] = field(default_factory=list)
    site_weights: np.ndarray | None = None


def _write(sinks: Sequence[TextIO], text: str) -> None:
    """Report one line of the run to each sink the caller gave, flushing every one.

    A library module does not get to decide that a terminal is watching, so the
    loop writes only where it was told to and is silent when told nowhere. The
    driver that wants a transcript on the terminal passes ``sys.stdout``; a run
    that wants a file passes the file; a caller that wants both passes both.
    Every line is flushed as it is written because the run this reports on can
    last an hour and a reader watching it has to see each iteration as it lands.
    """

    for sink in sinks:
        sink.write(text + "\n")
        sink.flush()


def initial_sites(
    outer_side: Fraction,
    square_side: Fraction,
    *,
    grid_counts: tuple[int, ...] | None = None,
    inset: Fraction = Fraction(1, 2),
) -> SiteSet:
    """The grid seed at BC-191's density, or at the counts given."""

    counts = grid_counts or site_counts_for_side(outer_side, square_side, inset=inset)
    return site_set_from_grids(outer_side, counts, inset)


def rows_from_exact(
    exact_rows: list[ExactRow],
    sites: SiteSet,
    half_tangents: tuple[Fraction, ...],
    square_side: Fraction,
) -> Rows:
    """A row set rebuilt from snapped placements against a (possibly new) site set."""

    directions = direction_net(half_tangents)
    rows = Rows()
    for direction, x, y in exact_rows:
        d = directions[direction]
        cosine, sine = float(d.ux), float(d.uy)
        fx, fy = float(x), float(y)
        rows.directions.append(direction)
        rows.centres.append((fx * cosine + fy * sine, -fx * sine + fy * cosine))
    rows.matrix = coverage_matrix(exact_rows, sites, half_tangents, square_side)
    rows.keys = {row.tobytes() for row in rows.matrix}
    return rows


def cutting_plane_loop(
    n: int,
    outer_side: Fraction,
    square_side: Fraction,
    half_tangents: tuple[Fraction, ...],
    *,
    sites: SiteSet,
    rows: Rows,
    exact_rows: list[ExactRow],
    support_cap: int = 96,
    cap: int = 120,
    max_iterations: int = 40,
    deadline: float | None = None,
    rows_max_rounds: int = 8,
    rows_per_direction: int = 3,
    row_denominator: int = 10**6,
    weight_denominator: int = 10**9,
    select_above: Fraction = Fraction(1000001, 1000000),
    exact_scan: bool = False,
    log_sinks: Sequence[TextIO] = (),
    state_path: Path | None = None,
) -> CuttingLog:
    """Alternate row generation with exact vertex separation until the family is
    feasible, the clock runs out, or no vertex is left to add.

    ``rows`` and ``exact_rows`` are carried in and mutated, aligned index for
    index; ``sites`` is replaced as orbits are added and the final set is on the
    returned log. The family judged each iteration is the heaviest
    ``support_cap`` rows of the dual, symmetrised, and its total divided by its
    exact maximum depth is the iteration's lower bound. The best such family,
    scaled to unit depth exactly, is kept.

    Per-iteration progress goes to every handle in ``log_sinks`` and nowhere
    else; the default is silence, and a caller wanting a terminal transcript
    passes ``sys.stdout`` among them.
    """

    if n < 1:
        raise ValueError("n must be positive")
    if outer_side <= square_side:
        raise ValueError("the container must be larger than the square")
    if len(rows) != len(exact_rows):
        raise ValueError("rows and exact_rows must be aligned")
    directions = direction_net(half_tangents)
    log = CuttingLog(exact_rows=exact_rows)
    threshold = Fraction(1)
    for index in range(max_iterations):
        if deadline is not None and time.perf_counter() >= deadline:
            log.stopped = f"deadline reached before iteration {index}"
            break
        started = time.perf_counter()
        solution = solve_rows(
            sites,
            square_side,
            half_tangents,
            rows,
            max_rounds=rows_max_rounds,
            rows_per_direction=rows_per_direction,
            deadline=deadline,
        )
        for held in range(len(exact_rows), len(rows)):
            direction = rows.directions[held]
            x, y = snap_centre(
                directions[direction],
                rows.centres[held],
                outer_side,
                square_side,
                row_denominator,
            )
            exact_rows.append((direction, x, y))
        rebuild_rows(rows, exact_rows, sites, half_tangents, square_side)
        seconds_rows = time.perf_counter() - started

        started = time.perf_counter()
        solved = solve_lp(sites, rows)
        if solved is None:
            log.stopped = f"the linear program refused the snapped rows at iteration {index}"
            break
        weights, duals, objective = solved
        log.site_weights = weights
        seconds_lp = time.perf_counter() - started

        started = time.perf_counter()
        entries = support_entries(
            exact_rows,
            duals,
            half_tangents,
            support_cap=support_cap,
            weight_denominator=weight_denominator,
        )
        if not entries:
            log.stopped = f"the dual is empty at iteration {index}"
            break
        family = CeilingCertificate(
            n,
            outer_side,
            square_side,
            half_tangents,
            symmetric_placements(entries, outer_side, square_side),
        )
        lines = arrangement_lines(family)
        if exact_scan:
            vertices = container_vertices(family, lines)
            deep, worst, decided = depths_above(family, vertices, threshold)
            separation = Separation(
                worst,
                decided,
                len(vertices),
                len(deep),
                select_site_orbits(
                    [entry for entry in deep if entry[0] > select_above],
                    sites,
                    outer_side,
                    cap=cap,
                ),
            )
        else:
            separation = screened_separation(
                family, lines, sites, cap=cap, select_above=select_above
            )
        worst, decided = separation.max_depth, separation.decided
        seconds_separation = time.perf_counter() - started
        raw_total = family.total_weight
        scaled_total = raw_total if worst <= 1 else raw_total / worst

        record = Iteration(
            index=index,
            sites=sites.size,
            orbits=len(sites.orbits),
            rows=len(rows),
            support=len(entries),
            rows_converged=solution.converged,
            rows_stopped=solution.stopped,
            rows_objective=solution.objective,
            objective=objective,
            raw_total=raw_total,
            max_depth=worst,
            scaled_total=scaled_total,
            vertices=separation.vertices,
            decided=decided,
            violating=separation.violating,
            added=0,
            seconds_rows=seconds_rows,
            seconds_lp=seconds_lp,
            seconds_separation=seconds_separation,
        )
        log.iterations.append(record)
        if scaled_total > log.best_scaled_total:
            log.best_scaled_total = scaled_total
            log.best_iteration = index
            log.best_family = family if worst <= 1 else family.scaled(1 / worst)
        log.sites = sites
        _write(
            log_sinks,
            f"iteration {index}: sites={sites.size} orbits={len(sites.orbits)} "
            f"rows={len(rows)} "
            f"support={len(entries)} rows_objective={solution.objective:.6f} "
            f"converged={solution.converged} objective={objective:.6f} "
            f"raw_total={float(raw_total):.6f} max_depth={worst}={float(worst):.6f} "
            f"scaled_total={float(scaled_total):.6f} vertices={separation.vertices} "
            f"decided={decided} violating={separation.violating} "
            f"seconds rows={seconds_rows:.1f} lp={seconds_lp:.1f} sep={seconds_separation:.1f}",
        )
        if state_path is not None:
            save_state(
                state_path,
                outer_side=outer_side,
                square_side=square_side,
                sites=sites,
                exact_rows=exact_rows,
                log=log,
            )

        if worst <= 1:
            if raw_total >= n:
                log.verdict = verify_ceiling(family)
                record.note = (
                    f"verify_ceiling: proved={log.verdict.proved} {log.verdict.failures}"
                )
                _write(log_sinks, "  " + record.note)
                if log.verdict.proved:
                    log.stopped = f"ceiling proved at iteration {index}"
                    break
            if solution.converged:
                log.stopped = (
                    f"feasible family below n with converged rows at iteration {index}: "
                    "the discretised program is at its optimum on this site set"
                )
                break
        selected = separation.chosen
        if not selected and worst <= select_above:
            log.stopped = f"no vertex exceeds {float(select_above):.7f} at iteration {index}"
            break
        if not selected:
            log.stopped = f"every violating vertex is already a site at iteration {index}"
            break
        new_orbits = tuple(orbit for _, orbit in selected)
        sites = SiteSet(outer_side, (*sites.orbits, *new_orbits))
        addition = coverage_matrix(
            exact_rows, SiteSet(outer_side, new_orbits), half_tangents, square_side
        )
        rows.matrix = np.hstack([rows.stacked(), addition])
        rows.keys = {row.tobytes() for row in rows.matrix}
        record.added = len(new_orbits)
        record.note = (
            f"added {len(new_orbits)} orbits, deepest {float(selected[0][0]):.6f} "
            f"at ({float(selected[0][1][0][0]):.6f}, {float(selected[0][1][0][1]):.6f})"
        )
        _write(log_sinks, "  " + record.note)
        log.sites = sites
    else:
        log.stopped = f"iteration cap {max_iterations} reached"
    if log.sites is None:
        log.sites = sites
    return log


def tidy_family(family: CeilingCertificate, denominator: int = 10**9) -> CeilingCertificate:
    """The same family with every weight rounded *down* to a multiple of ``1/denominator``.

    Scaling by the reciprocal of an exact maximum depth leaves weights whose
    denominators are whatever that depth's was, which after a rationalised dual
    can run to hundreds of digits. Rounding every weight down keeps the family a
    fractional packing -- depth is monotone in the weights, so a depth at most 1
    stays at most 1 -- and costs at most one quantum per placement of total.
    """

    if denominator < 1:
        raise ValueError("the denominator must be positive")
    return CeilingCertificate(
        family.n,
        family.outer_side,
        family.square_side,
        family.half_tangents,
        tuple(
            Placement(
                p.half_tangent,
                p.centre_x,
                p.centre_y,
                Fraction(math.floor(p.weight * denominator), denominator),
                p.side,
            )
            for p in family.placements
        ),
    )


def family_record(
    family: CeilingCertificate, provenance: dict[str, Any] | None = None
) -> dict[str, Any]:
    """The family as `CeilingCertificate.from_record` reads it, plus provenance."""

    record = family.to_record()
    record["total_weight"] = str(family.total_weight)
    record["total_weight_float"] = float(family.total_weight)
    if provenance:
        record["provenance"] = provenance
    return record


def save_state(
    path: Path,
    *,
    outer_side: Fraction,
    square_side: Fraction,
    sites: SiteSet,
    exact_rows: list[ExactRow],
    log: CuttingLog,
) -> None:
    """Everything a later run needs to warm-start, at this or a larger side."""

    state = {
        "outer_side": str(outer_side),
        "square_side": str(square_side),
        "sites": [[str(x), str(y)] for orbit in sites.orbits for x, y in orbit],
        "rows": [[direction, str(x), str(y)] for direction, x, y in exact_rows],
        "best_scaled_total": str(log.best_scaled_total),
        "best_iteration": log.best_iteration,
        "iterations": [entry.as_dict() for entry in log.iterations],
        "stopped": log.stopped,
    }
    if log.best_family is not None:
        state["best_family"] = family_record(log.best_family)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state) + "\n")


def load_state(path: Path) -> tuple[Fraction, list[tuple[Fraction, Fraction]], list[ExactRow]]:
    """The side, the site points and the snapped rows a state file holds."""

    state = json.loads(path.read_text())
    for key in ("outer_side", "sites", "rows"):
        if key not in state:
            raise ValueError(f"state file {path} has no {key!r}")
    outer_side = Fraction(state["outer_side"])
    points = [(Fraction(x), Fraction(y)) for x, y in state["sites"]]
    exact_rows: list[ExactRow] = [
        (int(d), Fraction(x), Fraction(y)) for d, x, y in state["rows"]
    ]
    for direction, x, y in exact_rows:
        if direction < 0 or not (0 <= x <= outer_side and 0 <= y <= outer_side):
            raise ValueError(f"state file {path} holds a row outside the container")
    return outer_side, points, exact_rows


def warm_start(
    points: list[tuple[Fraction, Fraction]],
    exact_rows: list[ExactRow],
    *,
    old_side: Fraction,
    new_side: Fraction,
    square_side: Fraction,
    half_tangents: tuple[Fraction, ...],
    grid_counts: tuple[int, ...] | None = None,
    inset: Fraction = Fraction(1, 2),
) -> tuple[SiteSet, list[ExactRow]]:
    """Recentre a smaller side's sites and rows in the new container.

    Sites and placements are shifted by half the change of side so the D4
    structure carries over, the grid seed for the new side is added, and every
    placement is clamped into the new centre domain (a no-op when the side
    grows). The rows come back as snapped placements ready for `rows_from_exact`.
    """

    if new_side < old_side:
        raise ValueError("warm starts move to a larger side, not a smaller one")
    shift = (new_side - old_side) / 2
    moved = {(x + shift, y + shift) for x, y in points}
    seed = initial_sites(new_side, square_side, grid_counts=grid_counts, inset=inset)
    moved.update(seed.positions())
    sites = site_set_from_points(new_side, moved)
    directions = direction_net(half_tangents)
    carried: list[ExactRow] = []
    for direction, x, y in exact_rows:
        d = directions[direction]
        extent = square_side * (d.ux + d.uy) / 2
        nx = min(max(x + shift, extent), new_side - extent)
        ny = min(max(y + shift, extent), new_side - extent)
        carried.append((direction, nx, ny))
    return sites, carried


def iteration_table(iterations: list[Iteration]) -> str:
    """The per-iteration table as Markdown."""

    header = (
        "| it | sites | orbits | rows | support | objective | raw total | exact max depth "
        "| scaled total | vertices | decided | violating | added | s rows | s lp | s sep |"
    )
    rule = "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"
    lines = [header, rule]
    lines.extend(
        (
            f"| {entry.index} | {entry.sites} | {entry.orbits} | {entry.rows} "
            f"| {entry.support} "
            f"| {entry.objective:.6f} | {float(entry.raw_total):.6f} "
            f"| {entry.max_depth} = {float(entry.max_depth):.6f} "
            f"| {float(entry.scaled_total):.6f} | {entry.vertices} | {entry.decided} "
            f"| {entry.violating} | {entry.added} | {entry.seconds_rows:.1f} "
            f"| {entry.seconds_lp:.1f} | {entry.seconds_separation:.1f} |"
        )
        for entry in iterations
    )
    return "\n".join(lines)


__all__ = [
    "CLUSTER_RADIUS",
    "COVER_SLACK",
    "CuttingLog",
    "ExactRow",
    "Iteration",
    "Separation",
    "SupportEntry",
    "coverage_matrix",
    "cutting_plane_loop",
    "depths_above",
    "family_record",
    "float_vertices",
    "initial_sites",
    "iteration_table",
    "load_state",
    "rebuild_rows",
    "rows_from_exact",
    "save_state",
    "screened_separation",
    "select_site_orbits",
    "snap_centre",
    "support_entries",
    "symmetric_placements",
    "tidy_family",
    "warm_start",
]
