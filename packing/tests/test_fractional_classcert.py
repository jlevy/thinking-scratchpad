"""The two-threshold class program: cells, thresholds, and the nine-point control.

Every test here runs on the retained ``n = 11`` net, because the cell boundaries
are what the class partition is defined by and a synthetic net would not check
the numbers the record carries.
"""

from __future__ import annotations

import math
from fractions import Fraction

import pytest

from sqpack.fractional.classcert import (
    NEAR,
    TILTED,
    ClassThresholds,
    Composition,
    DirectionClasses,
    axis_disjoint_count,
    cell_boundary_tangent,
    class_minima,
    cos_plus_sin_at_most,
    decide_class_program,
    end_cells,
    largest_half_gap_tangent,
    leading_cells,
    quarter_pitch_sites,
    solve_class_program,
    within_nine_point_tilt,
)
from sqpack.fractional.generate import build_site_grid, net_half_tangents

ANGLE_LIMIT = Fraction(207107, 500000)
DIRECTION_STEPS = 180
SQUARE_SIDE = Fraction(9977, 10000)
NINE_POINT_SIDE = Fraction(3877, 1000)
NET = net_half_tangents(ANGLE_LIMIT, DIRECTION_STEPS)


def degrees(tangent: Fraction) -> float:
    return math.degrees(math.atan(float(tangent)))


def test_net_carries_the_retained_certificate_numbers() -> None:
    assert len(NET) == DIRECTION_STEPS + 1
    assert largest_half_gap_tangent(NET) == Fraction(207107, 90000000)
    assert SQUARE_SIDE * (1 + largest_half_gap_tangent(NET)) < 1


def test_cell_boundary_is_the_midpoint_angle() -> None:
    """The boundary between two cells bisects the angle, not the half-tangent."""

    boundary = cell_boundary_tangent(NET[0], NET[1])
    first = math.degrees(2 * math.atan(float(NET[1])))
    assert degrees(boundary) == pytest.approx(first / 2, abs=1e-9)


def test_leading_six_cells_reach_the_recorded_boundary() -> None:
    classes = leading_cells(NET, 6)
    lower, upper = classes.cell_bounds(5)
    assert lower == cell_boundary_tangent(NET[4], NET[5])
    assert degrees(upper) == pytest.approx(1.450253, abs=1e-6)


def test_end_cells_span_both_ends_of_the_folded_arc() -> None:
    classes = end_cells(NET)
    assert classes.members(NEAR) == (0, DIRECTION_STEPS)
    assert classes.cell_bounds(0)[0] == 0
    assert classes.cell_bounds(DIRECTION_STEPS)[1] == 1
    assert degrees(classes.cell_bounds(0)[1]) == pytest.approx(0.131848, abs=1e-6)


def test_cos_plus_sin_is_decided_in_rationals() -> None:
    assert cos_plus_sin_at_most(Fraction(0), Fraction(1))
    assert not cos_plus_sin_at_most(Fraction(1), Fraction(1))
    # tan t = 3/4 gives cos t + sin t = 7/5 exactly, so 7/5 holds and just under does not.
    assert cos_plus_sin_at_most(Fraction(3, 4), Fraction(7, 5))
    assert not cos_plus_sin_at_most(Fraction(3, 4), Fraction(13999, 10000))


def test_the_first_six_cells_are_the_largest_class_inside_the_tilt_limit() -> None:
    """Control one's class boundary, decided exactly rather than in degrees."""

    assert within_nine_point_tilt(leading_cells(NET, 6), NINE_POINT_SIDE, SQUARE_SIDE)
    assert not within_nine_point_tilt(leading_cells(NET, 7), NINE_POINT_SIDE, SQUARE_SIDE)


def test_axis_disjoint_count_is_the_grid_that_fits() -> None:
    assert axis_disjoint_count(NINE_POINT_SIDE, SQUARE_SIDE) == 9
    assert axis_disjoint_count(4 * SQUARE_SIDE, SQUARE_SIDE) == 9
    assert axis_disjoint_count(5 * SQUARE_SIDE, SQUARE_SIDE) == 16


def test_nine_unit_atoms_refute_eleven_near_axis_squares() -> None:
    """Control one, exactly: nine points close the composition ``(11, 0)``."""

    classes = leading_cells(NET, 6)
    composition = Composition(near=11, tilted=0)
    verdict = decide_class_program(
        quarter_pitch_sites(NINE_POINT_SIDE),
        NINE_POINT_SIDE,
        SQUARE_SIDE,
        classes,
        composition,
        thresholds=ClassThresholds(Fraction(1), Fraction(0)),
    )
    assert verdict.total_mass == 9
    assert verdict.required == 11
    assert verdict.margin == -2
    assert verdict.refutes
    assert verdict.failures == ()


def test_the_nine_point_measure_leaves_no_near_axis_core_short() -> None:
    classes = leading_cells(NET, 6)
    near, tilted = class_minima(
        quarter_pitch_sites(NINE_POINT_SIDE),
        classes,
        Composition(near=11, tilted=0),
        NINE_POINT_SIDE,
        SQUARE_SIDE,
    )
    assert near.mass == 1
    assert near.cells == 6
    assert tilted.mass is None


def test_a_seventh_cell_leaves_the_nine_points_short() -> None:
    """The class boundary is load-bearing: one cell past the tilt limit fails."""

    verdict = decide_class_program(
        quarter_pitch_sites(NINE_POINT_SIDE),
        NINE_POINT_SIDE,
        SQUARE_SIDE,
        leading_cells(NET, 12),
        Composition(near=11, tilted=0),
        thresholds=ClassThresholds(Fraction(1), Fraction(0)),
    )
    assert not verdict.refutes
    assert "Condition 5' class 0 carries w0" in verdict.failures


def test_the_search_finds_the_nine_point_optimum() -> None:
    """The float proposal on a grid holding the nine points: nine at ``w_0 = 1``."""

    grid = build_site_grid(NINE_POINT_SIDE, 3, NINE_POINT_SIDE / 4)
    composition = Composition(near=11, tilted=0)
    weights, log = solve_class_program(
        grid, SQUARE_SIDE, leading_cells(NET, 6), composition, max_rounds=40
    )
    assert log.converged
    assert log.margin < 0
    assert log.objective / log.thresholds[NEAR] == pytest.approx(9.0, abs=1e-6)
    assert float(weights @ [len(orbit) for orbit in grid.orbits]) == pytest.approx(
        log.objective, abs=1e-6
    )


def test_an_empty_class_keeps_its_threshold_at_zero() -> None:
    grid = build_site_grid(NINE_POINT_SIDE, 3, NINE_POINT_SIDE / 4)
    _, log = solve_class_program(
        grid, SQUARE_SIDE, leading_cells(NET, 6), Composition(near=11, tilted=0), max_rounds=40
    )
    assert log.thresholds[TILTED] == 0.0
    assert Composition(near=11, tilted=0).active() == (NEAR,)


def test_a_composition_refuses_a_negative_part() -> None:
    with pytest.raises(ValueError, match="neither part may be negative"):
        Composition(near=12, tilted=-1)


def test_a_class_refuses_a_cell_the_net_does_not_have() -> None:
    with pytest.raises(ValueError, match="must be a cell of this net"):
        DirectionClasses(NET, frozenset({DIRECTION_STEPS + 1}))


def test_a_class_refuses_an_empty_near_set() -> None:
    with pytest.raises(ValueError, match="at least one cell"):
        DirectionClasses(NET, frozenset())
