"""The column-generator benchmark harness, and the site-density rule it fits.

The harness is a measuring instrument, so what is tested here is that it does not
perturb what it measures: a timed ``solve_rows`` takes the same decisions as an
untimed one, and rationalising one LP point at several scales changes the weights
and nothing else. The density rule is tested against the grids ``BC-191``'s ladder
measured as best at two sides, because returning those from one set of densities
is the whole claim it makes.
"""

from __future__ import annotations

from fractions import Fraction

import pytest

from devtools.bench_colgen import Case, bench_rounds, bench_scale, density_of
from sqpack.fractional.colgen import (
    RoundTiming,
    Rows,
    site_counts_for_side,
    site_set_from_grids,
    solve_rows,
)
from sqpack.fractional.generate import net_half_tangents

B = Fraction(9977, 10000)
INSET = Fraction(1, 2)


def small_case() -> Case:
    """A case small enough for a unit test and shaped like the real ones."""

    return Case(
        n=4,
        outer_side=Fraction(2),
        square_side=Fraction(4, 5),
        angle_limit=Fraction(1, 10),
        direction_steps=3,
        inset=Fraction(1, 4),
    )


def test_site_counts_land_on_the_measured_optimum_at_both_sides() -> None:
    """The rule returns the grid the density ladder measured as best, at each side.

    ``BC-191`` ran a five-rung ladder in the production three-grid shape at
    ``99/25`` and at ``24/5``. The best rung was ``(26, 35, 43)`` at the first --
    converged in 60.8 s at 12.217676, against 60.8 s at 12.312896 one rung
    coarser and no convergence in 123.1 s one rung finer -- and ``(34, 44, 55)``
    at the second, which reached 19.339779 where the coarser rungs reached
    20.168732 and 25.000000. The rule has to give both from one set of
    densities, within the grid step that separates neighbouring counts.
    """

    assert site_counts_for_side(Fraction(99, 25), B, inset=INSET) == (26, 35, 43)
    for got, want in zip(
        site_counts_for_side(Fraction(24, 5), B, inset=INSET), (34, 44, 55), strict=True
    ):
        assert abs(got - want) <= 1


def test_site_counts_are_denser_than_the_inherited_default() -> None:
    """The rule is above the tuned ``(23, 31, 39)`` density, because the ladder is.

    The inherited default is the lower edge of the usable band rather than its
    middle: at ``24/5`` it reached 20.168732 where the measured optimum reached
    19.339779 in comparable wall time. A rule that reproduced it would be
    reproducing the wrong end of the measurement.
    """

    for side in (Fraction(99, 25), Fraction(24, 5), Fraction(138, 25)):
        counts = site_counts_for_side(side, B, inset=INSET)
        inherited = tuple(density_of(side, B, count, INSET) for count in (23, 31, 39))
        measured = tuple(density_of(side, B, count, INSET) for count in counts)
        for got, was in zip(measured, inherited, strict=True):
            assert got > was


def test_site_counts_hold_the_density_as_the_side_grows() -> None:
    """The counts grow with the side so that sites per ``B`` stays put.

    This is the property the fixed default lacks: at ``138/25`` the tuned
    ``(23, 31, 39)`` would read the container on a net ``1.4x`` coarser than the
    one it was tuned on.
    """

    densities = []
    for side in (Fraction(99, 25), Fraction(24, 5), Fraction(138, 25), Fraction(38, 5)):
        counts = site_counts_for_side(side, B, inset=INSET)
        densities.append(tuple(density_of(side, B, count, INSET) for count in counts))
    first = densities[0]
    for row in densities[1:]:
        for got, want in zip(row, first, strict=True):
            assert abs(got - want) < 0.35


def test_site_counts_reject_an_inset_that_leaves_no_room() -> None:
    with pytest.raises(ValueError, match="the inset leaves no room for sites"):
        site_counts_for_side(Fraction(1), B, inset=Fraction(1))


def test_timings_do_not_change_what_solve_rows_decides() -> None:
    """The equivalence guard: the instrument writes to its list and nothing else."""

    case = small_case()
    half_tangents = net_half_tangents(case.angle_limit, case.direction_steps)
    outcomes = []
    for timings in ([], None):
        sites = site_set_from_grids(case.outer_side, (5, 7), case.inset)
        rows = Rows()
        solution = solve_rows(
            sites,
            case.square_side,
            half_tangents,
            rows,
            max_rounds=4,
            timings=timings,
        )
        outcomes.append(
            (solution.rounds, solution.rows, solution.stopped, round(solution.objective, 9))
        )
        if timings is not None:
            assert timings, "a timed run records at least one round"
            assert all(isinstance(entry, RoundTiming) for entry in timings)
            assert all(entry.seconds >= 0 for entry in timings)
            assert max(entry.index for entry in timings) == solution.rounds - 1
    assert outcomes[0] == outcomes[1]


def test_bench_rounds_splits_a_round_into_separation_and_lp() -> None:
    report = bench_rounds(small_case(), (5, 7), max_rounds=3)
    run = report["row_run"]
    assert isinstance(run, dict)
    assert run["rounds"] >= 1
    # The parts cannot exceed the whole -- but all three figures are rounded to
    # milliseconds independently by `bench_rounds`, so the *reported* parts can exceed
    # the *reported* whole by up to three half-millisecond rounding steps: each part can
    # round up by just under 5e-4 while the total rounds down by just under 5e-4. A 1e-6
    # tolerance was therefore three orders of magnitude too tight, and it failed on CI at
    # 0.004 + 0.005 against 0.008 (run 33989527866) -- arithmetic, not a slow runner, and
    # it only surfaces once the case is fast enough for millisecond quantisation to bite.
    assert run["separation_seconds"] + run["lp_seconds"] <= run["seconds"] + 1.5e-3
    assert 0.0 <= run["separation_share"] <= 1.0
    assert len(run["timings"]) >= 1


def test_bench_scale_varies_only_the_weights() -> None:
    """A finer scale keeps the atoms and lowers the rounded total.

    Both halves matter to the decision the cell has to make: the loss shrinks
    like ``1/scale`` while the object being verified is the same size, so the
    margin is bought without paying for it in atoms.
    """

    report = bench_scale(
        small_case(),
        (5, 7),
        (10_000, 200_000, 4_000_000),
        max_rounds=6,
        verify_scales=(),
    )
    rows = report["scales"]
    assert isinstance(rows, list)
    if not rows:  # pragma: no cover - the toy case converges, but do not assert on luck
        pytest.skip("the toy row generation did not converge")
    atoms = {row["atoms"] for row in rows}
    assert len(atoms) == 1, "the atom count does not depend on the scale"
    totals = [row["total_mass_float"] for row in rows]
    assert totals == sorted(totals, reverse=True), "a finer scale rounds up less"
    assert all(row["loss"] >= 0 for row in rows), "rounding up never lowers the total"
    assert all(row["integer_route"] for row in rows), "the sweep stays on its integer route"
