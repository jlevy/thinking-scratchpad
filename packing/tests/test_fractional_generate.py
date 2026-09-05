"""Controls for site column generation on the fractional covering LP.

The instrument under test is `sqpack.fractional.colgen`, which moves the
candidate sites instead of fixing them to a grid. Three things have to hold or
the loop is reporting a number about nothing: the price it puts on a new orbit
has to be the reduced cost it claims to be, adding an orbit must never make the
optimum worse on the rows already held, and the ceiling by-product must refuse
a dual that covers some point of the container twice -- which is the only way
that by-product could ever claim more than weak duality allows.
"""

from __future__ import annotations

from fractions import Fraction

import numpy as np
import pytest

from cases.n12_fractional_certificate.replay import load
from sqpack.fractional import colgen
from sqpack.fractional.certificate import verify
from sqpack.fractional.generate import (
    direction_net,
    event_grid,
    net_half_tangents,
    placement_cells,
)
from sqpack.fractional.model import Atom, Direction, rotation_from_half_tangent
from sqpack.fractional.sweep import minimum_covered_mass, reduce_to_cells

UPRIGHT = rotation_from_half_tangent("0", Fraction(0))


def axis_aligned(
    centre: tuple[Fraction, Fraction], outer_side: Fraction, side: Fraction
) -> colgen.Square:
    return colgen.square_at(UPRIGHT, centre, outer_side, side)


def test_reduced_cost_counts_the_orbit_members_one_placement_covers() -> None:
    """A hand-counted instance: four of eight images sit in the square.

    Container side 4, so the centre is (2, 2). The square has side 1 and centre
    (13/5, 2), covering ``x`` in [21/10, 31/10] and ``y`` in [3/2, 5/2]. The
    orbit of (5/2, 11/5) is the eight points (2 +- 1/2, 2 +- 1/5) and
    (2 +- 1/5, 2 +- 1/2); the four with ``x = 5/2`` or ``x = 11/5`` are inside,
    two of them on the edge, which counts because coverage is by closed squares.
    """
    outer = Fraction(4)
    square = axis_aligned((Fraction(13, 5), Fraction(2)), outer, Fraction(1))
    orbit = colgen.d4_orbit(Fraction(5, 2), Fraction(11, 5), outer)
    assert len(orbit) == 8

    covered = [point for point in orbit if square.covers(*_centred(point, outer))]
    assert len(covered) == 4
    assert colgen.reduced_cost(orbit, ((square, Fraction(3)),), outer) == 8 - 3 * 4


def test_orbit_averaged_depth_is_the_symmetrised_pointwise_depth() -> None:
    """The identity the column generation rests on, on a two-square dual.

    Reduced cost is defined by orbit-averaged depth, but the candidate search
    ranks points by the pointwise depth of the symmetrised dual. Those are the
    same function, and if they ever came apart the search would be maximising
    something the LP does not price.
    """
    outer = Fraction(4)
    weighted = (
        (axis_aligned((Fraction(13, 5), Fraction(2)), outer, Fraction(1)), Fraction(3)),
        (axis_aligned((Fraction(2), Fraction(9, 4)), outer, Fraction(3, 2)), Fraction(1)),
    )
    point = (Fraction(5, 2), Fraction(11, 5))
    orbit = colgen.d4_orbit(point[0], point[1], outer)
    averaged = 1 - colgen.reduced_cost(orbit, weighted, outer) / len(orbit)
    pointwise = sum(
        (
            weight
            for square, weight in colgen.symmetrise(weighted)
            if square.covers(*_centred(point, outer))
        ),
        start=Fraction(0),
    )
    assert averaged == pointwise


def test_symmetrising_preserves_the_total_dual_weight() -> None:
    outer = Fraction(4)
    square = axis_aligned((Fraction(13, 5), Fraction(2)), outer, Fraction(1))
    weighted = ((square, Fraction(3)),)
    assert sum(weight for _, weight in colgen.symmetrise(weighted)) == Fraction(3)


def test_adding_a_site_orbit_never_raises_the_optimum_on_the_rows_held() -> None:
    """Monotonicity, which is what makes the column loop safe to iterate.

    The comparison is on one fixed row set: adding a column only widens the
    feasible region, so the optimum cannot rise. Re-generating rows afterwards
    can raise it, and that is a different statement -- one about the placements
    the new sites expose, not about the sites.
    """
    outer, side = Fraction(11, 5), Fraction(24, 25)
    tangents = net_half_tangents(Fraction(207107, 500000), 12)
    sites = colgen.site_set_from_grids(outer, (7,), Fraction(1, 2))
    rows = colgen.Rows()
    solution = colgen.solve_rows(sites, side, tangents, rows, rows_per_direction=2)
    assert solution.converged, solution.stopped

    weighted = colgen.dual_squares(rows, solution.duals, tangents, outer, side, support_cap=16)
    candidate = colgen.best_candidate(sites, weighted)
    orbit = (
        candidate.orbit
        if candidate is not None
        else colgen.d4_orbit(Fraction(3, 4), Fraction(9, 10), outer)
    )
    rows.add_column(colgen.orbit_column(rows, orbit, tangents, side))
    widened = colgen.SiteSet(outer, (*sites.orbits, orbit))

    solved = colgen.solve_lp(widened, rows)
    assert solved is not None
    assert solved[2] <= solution.objective + 1e-9


def _oracle_against_sweep(
    atoms: tuple[Atom, ...],
    direction: Direction,
    outer: Fraction,
    side: Fraction,
) -> tuple[float, float, int]:
    """The oracle's least mass, the sweep's, and how many sweep cells the oracle lacks.

    A sweep cell is matched by its midpoint: the oracle's events are the same
    rationals in floats, so the float cell holding a midpoint is the same cell
    or, where two exact events fell an ulp apart, the wide half of it.
    """

    exact, _ = minimum_covered_mass(atoms, direction, outer, side)
    reduction = reduce_to_cells(atoms, direction, outer, side)
    points = np.array([[float(atom.x), float(atom.y)] for atom in atoms])
    weights = np.array([float(atom.weight) for atom in atoms])
    grid = event_grid(points, weights, direction, float(outer), float(side))
    found = placement_cells(points, weights, direction, float(outer), float(side), keep=3)
    lacking = 0
    for i, j in reduction.cells:
        u_mid = float((reduction.u_events[i] + reduction.u_events[i + 1]) / 2)
        v_mid = float((reduction.v_events[j] + reduction.v_events[j + 1]) / 2)
        cell = (
            int(np.searchsorted(grid.u_events, u_mid)) - 1,
            int(np.searchsorted(grid.v_events, v_mid)) - 1,
        )
        lacking += not grid.reachable[cell]
    return min(mass for mass, _, _, _ in found), float(exact), lacking


def _patterned_atoms(outer: Fraction, counts: tuple[int, ...]) -> tuple[Atom, ...]:
    positions = colgen.site_set_from_grids(outer, counts, Fraction(1, 2)).positions()
    pattern = [Fraction((index * 5) % 4, 8) for index in range(len(positions))]
    return tuple(
        Atom(str(index), x, y, pattern[index])
        for index, (x, y) in enumerate(positions)
        if pattern[index] > 0
    )


@pytest.mark.slow
def test_the_float_oracle_scores_every_cell_the_exact_sweep_scores() -> None:
    """D-434's regression: the oracle and the verifier must decide one cell set.

    The oracle used to call a cell reachable when its centre lay in the centre
    domain, which misses a cell that straddles the domain's tilted edge with
    its centre outside -- about one cell in ninety away from the axes. The
    sweep's rule is the theorem's: the open cell meets the closed domain. So
    the oracle's cell set has to contain the sweep's, and its least mass can
    never exceed the sweep's; on the small instance it once reported 2.125
    where the sweep found 2. Three configurations, and every one runs the
    diagonal direction, which is where the straddling cells are.
    """

    limit = Fraction(207107, 500000)
    small = Fraction(11, 5), Fraction(24, 25), net_half_tangents(limit, 12)
    wide = Fraction(3), Fraction(49, 50), net_half_tangents(limit, 6)
    configurations = [
        (_patterned_atoms(small[0], (9,)), small[0], small[1], direction_net(small[2])),
        (_patterned_atoms(wide[0], (5, 7)), wide[0], wide[1], direction_net(wide[2])),
    ]
    retained = load()
    configurations.append(
        (
            retained.atoms,
            retained.outer_side,
            retained.square_side,
            tuple(retained.directions[k] for k in (45, 90, 180)),
        )
    )
    for atoms, outer, side, directions in configurations:
        for direction in directions:
            oracle, exact, lacking = _oracle_against_sweep(atoms, direction, outer, side)
            assert lacking == 0, f"direction {direction.label} lacks {lacking} sweep cells"
            assert oracle <= exact + 1e-9, f"direction {direction.label}: {oracle} > {exact}"
            assert oracle >= exact - 1e-9, f"direction {direction.label}: {oracle} < {exact}"


def test_a_row_is_generated_at_a_placement_that_exists() -> None:
    """Every row's centre must lie in the centre domain, or it constrains nothing real.

    With the grid built on the weighted sites only, a reachable cell can be
    wider than the domain's overlap with it, and the cell centre can hang
    outside the container. The row is read at a point of the overlap instead.
    """

    outer, side = Fraction(11, 5), Fraction(24, 25)
    atoms = _patterned_atoms(outer, (9,))
    sites = colgen.site_set_from_grids(outer, (9,), Fraction(1, 2))
    points = sites.points()
    weights = np.zeros(len(points))
    live = {(atom.x, atom.y): float(atom.weight) for atom in atoms}
    for index, position in enumerate(sites.positions()):
        weights[index] = live.get(position, 0.0)
    for direction in direction_net(net_half_tangents(Fraction(207107, 500000), 12)):
        extent = float(side) * (float(direction.ux) + float(direction.uy)) / 2
        for mass, cu, cv, covers in colgen.placement_cells(
            points, weights, direction, float(outer), float(side), keep=3
        ):
            x = cu * float(direction.ux) - cv * float(direction.uy)
            y = cu * float(direction.uy) + cv * float(direction.ux)
            assert extent - 1e-9 <= x <= float(outer) - extent + 1e-9
            assert extent - 1e-9 <= y <= float(outer) - extent + 1e-9
            assert mass == pytest.approx(float(weights[covers].sum()))


def test_the_ceiling_refuses_a_dual_that_covers_a_point_twice() -> None:
    """Pointwise, not orbit-averaged: overlap is what invalidates a ceiling."""
    outer = Fraction(4)
    overlapping = (
        (axis_aligned((Fraction(19, 10), Fraction(2)), outer, Fraction(1)), Fraction(1)),
        (axis_aligned((Fraction(21, 10), Fraction(2)), outer, Fraction(1)), Fraction(1)),
    )
    result = colgen.check_ceiling(2, overlapping, outer)
    assert result.max_pointwise_depth == 2
    assert result.total_weight == 2
    assert result.feasible_total == 1
    assert not result.proved


def test_the_ceiling_accepts_a_dual_of_disjoint_placements() -> None:
    """The positive control: weight 2 spread over squares that never overlap."""
    outer = Fraction(4)
    disjoint = (
        (axis_aligned((Fraction(1), Fraction(1)), outer, Fraction(1)), Fraction(1)),
        (axis_aligned((Fraction(3), Fraction(3)), outer, Fraction(1)), Fraction(1)),
    )
    result = colgen.check_ceiling(2, disjoint, outer)
    assert result.max_pointwise_depth == 1
    assert result.feasible_total == 2
    assert result.proved


def test_the_dual_of_a_converged_solve_matches_its_objective() -> None:
    """Strong duality on the generated rows, which is what prices the columns.

    Compared to a tolerance, not for equality. Strong duality is exact over the
    rationals, but both sides here are float sums the LP solver accumulates in an
    order it chooses, and the two orders need not agree to the last bit. Asserting
    equality made this test fail on roughly half of CI runs at
    `4.000000000000001 == 4.0` -- one ulp -- while passing locally every time.
    A duality gap that mattered would be many orders of magnitude larger than the
    scale-relative tolerance below, so nothing is given up by measuring it this way.
    """
    outer, side = Fraction(11, 5), Fraction(24, 25)
    tangents = net_half_tangents(Fraction(207107, 500000), 12)
    sites = colgen.site_set_from_grids(outer, (7,), Fraction(1, 2))
    rows = colgen.Rows()
    solution = colgen.solve_rows(sites, side, tangents, rows, rows_per_direction=2)
    assert solution.converged, solution.stopped
    dual_total = float(solution.duals.sum())
    objective = float(solution.objective)
    assert abs(dual_total - objective) <= 1e-9 * max(1.0, abs(objective)), (
        f"duality gap {dual_total - objective!r} between {dual_total!r} and {objective!r}"
    )


def test_a_union_of_grids_is_closed_under_d4_and_holds_both_grids() -> None:
    outer = Fraction(11, 5)
    union = colgen.site_set_from_grids(outer, (5, 7), Fraction(1, 2))
    held = set(union.positions())
    for x, y in held:
        assert set(colgen.d4_orbit(x, y, outer)) <= held
    assert len(held) == len(union.positions())
    assert union.size == sum(len(orbit) for orbit in union.orbits)


def test_generate_adaptive_produces_a_certificate_the_exact_verifier_accepts() -> None:
    """End to end on a bound nobody doubts: s(5) >= 11/5, well under 2.7071.

    ``decide=True`` is asked for explicitly: the default no longer decides (below).
    """
    certificate, log = colgen.generate_adaptive(
        5,
        Fraction(11, 5),
        Fraction(24, 25),
        grid_counts=(9,),
        inset=Fraction(1, 2),
        angle_limit=Fraction(207107, 500000),
        direction_steps=12,
        scale=2000,
        column_rounds=2,
        rows_per_direction=2,
        decide=True,
    )
    assert certificate is not None, log.stopped
    assert log.ceiling is not None
    assert log.accepted, log.failures
    verdict = verify(certificate)
    assert verdict.accepted, verdict.failures
    assert certificate.total_mass < 5


def test_generate_adaptive_returns_before_deciding_so_the_candidate_can_be_frozen(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The default is freeze-then-decide: the generator hands back bytes-to-be, undecided.

    D-441 lost a candidate to a kill between its in-memory decision and its write; the
    retention boundary is ``devtools.decide_certificate`` on frozen bytes, by both
    routes, so the default must not decide anything a caller could mistake for that.
    """

    def unexpected_in_memory_decision(_certificate: object) -> None:
        raise AssertionError("the default decided a candidate before its bytes were frozen")

    monkeypatch.setattr(colgen, "verify", unexpected_in_memory_decision)
    certificate, log = colgen.generate_adaptive(
        5,
        Fraction(11, 5),
        Fraction(24, 25),
        grid_counts=(9,),
        inset=Fraction(1, 2),
        angle_limit=Fraction(207107, 500000),
        direction_steps=12,
        scale=2000,
        column_rounds=2,
        rows_per_direction=2,
    )
    assert certificate is not None, log.stopped
    assert log.accepted is False
    assert log.least_cell_mass is None


def _centred(
    point: tuple[Fraction, Fraction], outer_side: Fraction
) -> tuple[Fraction, Fraction]:
    return point[0] - outer_side / 2, point[1] - outer_side / 2
