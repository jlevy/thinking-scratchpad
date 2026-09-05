#!/usr/bin/env python3
"""The fixed-angle cell, solved exactly, against the float solver that has a floor.

D-021 records the floor: HiGHS will not go tighter than `1e-10`, so a float cell solve
can be wrong by roughly `1e-11` and a post-check written in floats cannot say which
side of a contact it is on.  What follows is that floor measured, and then removed.

**The float LP lands below the truth.**  Solved in `f64` over Trump's cell, HiGHS
returns a side `1.8e-16` *smaller* than the published algebraic value.  A negative gap
is the shape D-021 warns about: read without its tier it says the record was beaten.
The same cell solved over `Q(u)` returns the published side with the difference exactly
zero -- `FieldElement.is_zero`, not a comparison against a tolerance -- and every one of
the twenty-two translation variables exactly zero, so the eleven squares are put back
where the certificate has them and not near where it has them.

**The cell is algebraic, and only just.**  Trump's program carries 25,367 coefficients,
of which 1,842 leave `Q`; `Fraction` cannot express it and a number field must.  The
axis-aligned four-square cell carries 1,609 coefficients and all 1,609 are rational, so
the same solver runs over `Fraction` there with no field at all.  The dividing line is
the angle: multiples of a right angle give corner offsets `+-1/2` and edge normals
`+-1`, and any other tilt does not.

**A float basis is a hint, not an answer.**  Started from the basis HiGHS finds for a
perturbed objective -- a genuine vertex of the same polytope, at side `4.4086` -- the
exact simplex pivots three times and lands on the published value exactly.  So the float
path supplies phase 1 here and the exact path decides the answer;
`test_promote_exact_phase1.py` measures the same cell with no float solver at all.

**The `ambiguous` set is empty on the exact pose and cannot be on the float one.**  The
exact reconstruction has fourteen pair contacts, worst contact margin exactly `0`, and
nothing undecided.  The float reconstruction's worst contact margin is `4.4e-16`, not
zero, and at D-021's own `1e-11` floor three incidences fall in the undecidable band, so
`require_decided` refuses it.  That is the guarantee the float path cannot give: not
that its margins are large, but that zero is a value it can never certify.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

import mpmath as mp
import pytest
from scipy.optimize import linprog

from cases.trump11.packing import build
from sqpack.exact_lp import (
    ExactLP,
    ExactLPError,
    LinearRow,
    certify_vertex,
    coefficient_report,
    fixed_cell_lp,
    independent_rows,
    rational_sign,
    solve,
    translated_squares,
)
from sqpack.field import FieldElement, NumberField
from sqpack.promote.contacts import ContactExtractionError, extract_contacts, require_decided
from sqpack.verify import exact_sign, float_sign, verify_packing

# D-021's measured floor for the float LP, and the tolerance the contact extractor is
# handed when it is asked to classify a pose that came through one.
FLOAT_LP_FLOOR = "1e-11"

# Well past f64's seventeen digits, so nothing measured here is limited by the read-out.
COMPARISON_DIGITS = 40


@dataclass(frozen=True)
class Cell:
    """A pose, its exact program, and the field the two are written over."""

    squares: list
    side: FieldElement
    field: NumberField
    lp: ExactLP


_TRUMP: list[Cell] = []


def trump_cell() -> Cell:
    """Trump's eleven squares and the exact program of the cell they sit in.

    Assembling the cell reads 55 separating axes through exact sign tests, so it is
    cached: every measurement below is about the same program.
    """
    if not _TRUMP:
        squares, side, field = build()
        field.refine_to(60)
        _TRUMP.append(
            Cell(
                squares=squares,
                side=side,
                field=field,
                lp=fixed_cell_lp(squares, exact_sign, zero=field.zero, one=field.one),
            )
        )
    return _TRUMP[0]


def float_vertex(lp, objective=None) -> tuple[list[float], list[int]]:
    """Solve the program in `f64` and report where HiGHS thinks the active set is.

    This is the only floating-point solve in the file, and its answer is never trusted:
    what leaves here is a *list of row indices*, which the exact path either certifies,
    repairs, or refuses.
    """
    cost = [float(value) for value in (lp.objective if objective is None else objective)]
    matrix = [[float(value) for value in row.coefficients] for row in lp.rows]
    bounds = [float(value) for value in lp.rhs]
    result = linprog(
        cost, A_ub=matrix, b_ub=bounds, bounds=[(None, None)] * len(cost), method="highs"
    )
    assert result.status == 0, f"the float LP did not solve the cell: status {result.status}"
    slack = [
        bounds[index] - sum(a * z for a, z in zip(matrix[index], result.x, strict=True))
        for index in range(len(bounds))
    ]
    order = sorted(range(len(slack)), key=lambda index: abs(slack[index]))
    return list(result.x), [index for index in order if abs(slack[index]) < 1e-7]


def rational_grid_cell():
    """Four unit squares in a side-2 container: the axis-aligned cell, over `Fraction`."""

    def unit(x: int, y: int):
        corner = (Fraction(x), Fraction(y))
        return [
            corner,
            (corner[0] + 1, corner[1]),
            (corner[0] + 1, corner[1] + 1),
            (corner[0], corner[1] + 1),
        ]

    grid = [unit(0, 0), unit(1, 0), unit(0, 1), unit(1, 1)]
    return grid, fixed_cell_lp(grid, rational_sign, zero=Fraction(0), one=Fraction(1))


def the_cell_is_algebraic_for_trump_and_rational_for_an_axis_aligned_pose() -> None:
    """Report which cells need a number field and which get by on `Fraction`."""
    lp = trump_cell().lp
    count = 11
    assert len(lp.rows) == 16 * (count + count * (count - 1) // 2) == 1056, (
        f"the exact cell has {len(lp.rows)} rows, not the 16 x (n + C(n, 2)) the "
        f"independent float formulation builds"
    )

    tilted = coefficient_report(lp)
    print(
        f"  trump11 cell:  {tilted.total} coefficients, {tilted.algebraic} outside Q "
        f"-> {tilted.verdict}"
    )
    assert tilted.verdict == "algebraic", (
        "Trump's cell was reported rational, but a 40.18-degree tilt puts its corner "
        "offsets and edge normals outside Q"
    )
    assert tilted.algebraic > 0

    _, grid_lp = rational_grid_cell()
    flat = coefficient_report(grid_lp)
    print(
        f"  axis-aligned:  {flat.total} coefficients, {flat.algebraic} outside Q "
        f"-> {flat.verdict}"
    )
    assert flat.verdict == "rational", (
        f"the axis-aligned cell was reported algebraic with {flat.algebraic} coefficient(s) "
        f"outside Q, but every offset there is +-1/2 and every normal +-1"
    )

    _, solution = solve_rational_grid()
    assert solution.vertex.objective_value == Fraction(2), (
        f"the rational cell's exact optimum is {solution.vertex.objective_value}, not the "
        f"side 2 that four unit squares in a 2x2 container force"
    )


def solve_rational_grid():
    """Solve the axis-aligned cell end to end over `Fraction`, with no field anywhere."""
    grid, lp = rational_grid_cell()
    _, tight = float_vertex(lp)
    return grid, solve(lp, independent_rows(lp, tight), rational_sign)


def the_exact_optimum_is_the_published_side_and_the_float_lp_sits_below_it() -> None:
    """The known-answer comparison: exact against Trump's degree-8 root, and against f64."""
    cell = trump_cell()
    squares, side, field, lp = cell.squares, cell.side, cell.field, cell.lp
    point, tight = float_vertex(lp)
    solution = solve(lp, independent_rows(lp, tight), exact_sign)

    assert (solution.vertex.objective_value - side).is_zero(), (
        "the exact LP optimum is not Trump's published side, so the cell or the pivoting "
        "is wrong"
    )
    moved = [
        index for index, value in enumerate(solution.vertex.point[:-1]) if not value.is_zero()
    ]
    assert moved == [], (
        f"the exact optimum translates {len(moved)} of the 22 centre coordinates, so it is "
        f"a different packing from the certificate's"
    )
    assert solution.pivots == 0, (
        f"the float basis for the true objective needed {solution.pivots} exact pivots, so "
        f"HiGHS did not land on an optimal vertex"
    )

    with mp.workdps(COMPARISON_DIGITS + 10):
        exact = mp.mpf(field.decimal(side, COMPARISON_DIGITS))
        gap = mp.mpf(point[-1]) - exact
    print(f"  float LP - exact = {mp.nstr(gap, 6)}   (exact - published = 0 by is_zero)")
    assert abs(gap) < 1e-14, (
        f"the float LP is {mp.nstr(gap, 6)} from the exact optimum, far outside the f64 "
        f"agreement the cell decomposition was calibrated at"
    )

    reconstructed = translated_squares(squares, solution.vertex.point)
    report = verify_packing(reconstructed, solution.vertex.objective_value, exact_sign)
    assert report.valid, f"the exact reconstruction does not verify: {report}"


def a_float_basis_is_repaired_rather_than_believed() -> None:
    """Start from a vertex the float path found for the wrong objective, and pivot exactly."""
    cell = trump_cell()
    side, field, lp = cell.side, cell.field, cell.lp
    perturbed = list(lp.objective)
    perturbed[0] = -field.one
    point, tight = float_vertex(lp, perturbed)
    assert point[-1] > float(side) + 0.1, (
        f"the perturbed objective returned side {point[-1]}, which is not a different "
        f"vertex from the optimum"
    )

    solution = solve(lp, independent_rows(lp, tight), exact_sign)
    print(f"  repaired a side-{point[-1]:.4f} vertex in {solution.pivots} exact pivots")
    assert solution.pivots > 0, (
        "the suboptimal starting basis was reported already optimal, so the pivot loop is "
        "not running"
    )
    assert not solution.started_optimal
    assert (solution.vertex.objective_value - side).is_zero(), (
        "the exact simplex did not repair the suboptimal float basis back to Trump's "
        "published side"
    )


def the_exact_pose_leaves_no_incidence_undecided() -> None:
    """The `ambiguous` set is empty on the exact path, and cannot be on the float one."""
    cell = trump_cell()
    squares, lp = cell.squares, cell.lp
    point, tight = float_vertex(lp)
    solution = solve(lp, independent_rows(lp, tight), exact_sign)

    exact_structure = extract_contacts(
        translated_squares(squares, solution.vertex.point),
        solution.vertex.objective_value,
        sign=exact_sign,
        floor="0",
    )
    print(
        f"  exact pose:  {len(exact_structure.pair_contacts)} pair contacts, "
        f"{len(exact_structure.ambiguous)} undecided, worst contact margin "
        f"{exact_structure.worst_contact_margin}"
    )
    assert exact_structure.ambiguous == (), (
        f"the exact pose left {len(exact_structure.ambiguous)} incidence(s) undecided, which "
        f"exact arithmetic has no way to do"
    )
    assert require_decided(exact_structure) is exact_structure
    assert mp.mpf(exact_structure.worst_contact_margin) == 0, (
        f"the exact pose's worst contact margin is {exact_structure.worst_contact_margin} "
        f"rather than exactly zero"
    )

    float_squares = [
        [(float(px) + point[index], float(py) + point[11 + index]) for px, py in square]
        for index, square in enumerate(squares)
    ]
    float_structure = extract_contacts(
        float_squares,
        point[-1],
        sign=float_sign(float(FLOAT_LP_FLOOR)),
        floor=FLOAT_LP_FLOOR,
    )
    print(
        f"  float pose:  {len(float_structure.pair_contacts)} pair contacts, "
        f"{len(float_structure.ambiguous)} undecided, worst contact margin "
        f"{float_structure.worst_contact_margin}"
    )
    assert mp.mpf(float_structure.worst_contact_margin) > 0, (
        "the float pose reported a contact margin of exactly zero, which f64 cannot "
        "produce and which would make the comparison vacuous"
    )
    assert float_structure.ambiguous, (
        "the float pose left nothing undecided at D-021's floor, so the contrast this "
        "measurement rests on is not being made"
    )
    with pytest.raises(ContactExtractionError) as undecided:
        require_decided(float_structure)
    assert undecided.value.kind == "undecidable-incidence", (
        f"the float pose was refused for {undecided.value.kind} rather than for the "
        f"incidences D-021's floor cannot classify"
    )


def refusal(action) -> str:
    """Run `action` and name the exact-LP refusal it raised, or `none` if it returned.

    Written this way rather than with `pytest.raises` so that *not* refusing fails with
    a sentence about the guard that went missing, which is what a negative control has
    to read back.
    """
    try:
        action()
    except ExactLPError as error:
        return error.kind
    return "none"


def the_exact_lp_refuses_every_input_it_cannot_decide() -> None:
    """Each refusal the module can raise, raised, and named."""
    cell = trump_cell()
    field, lp = cell.field, cell.lp
    _, tight = float_vertex(lp)
    optimal = independent_rows(lp, tight)

    kind = refusal(lambda: certify_vertex(lp, optimal[:5], exact_sign))
    assert kind == "bad-request", (
        f"an active set of 5 rows was accepted for a {lp.width}-variable program ({kind})"
    )

    duplicated = ExactLP(
        objective=lp.objective,
        rows=(LinearRow("duplicate", lp.rows[optimal[0]].coefficients), *lp.rows[1:]),
        rhs=lp.rhs,
        zero=lp.zero,
        one=lp.one,
    )
    kind = refusal(
        lambda: certify_vertex(
            duplicated, (0, optimal[0], *optimal[1 : lp.width - 1]), exact_sign
        )
    )
    assert kind == "singular-basis", (
        f"a rank-deficient active set was solved rather than refused ({kind})"
    )

    kind = refusal(lambda: independent_rows(lp, tight[:3]))
    assert kind == "no-vertex-basis", (
        f"a candidate set of 3 rows was accepted as a {lp.width}-row vertex basis ({kind})"
    )

    arbitrary = independent_rows(lp, range(len(lp.rows)))
    kind = refusal(lambda: certify_vertex(lp, arbitrary, exact_sign))
    assert kind == "primal-infeasible", (
        f"an active set whose point violates a row was certified as a vertex ({kind})"
    )
    kind = refusal(lambda: solve(lp, arbitrary, exact_sign))
    assert kind == "primal-infeasible", (
        f"the simplex pivoted from a point outside the feasible region ({kind})"
    )

    perturbed = list(lp.objective)
    perturbed[0] = -field.one
    _, elsewhere = float_vertex(lp, perturbed)
    suboptimal = independent_rows(lp, elsewhere)
    kind = refusal(lambda: certify_vertex(lp, suboptimal, exact_sign))
    assert kind == "dual-infeasible", (
        f"a feasible but suboptimal vertex was certified as optimal ({kind})"
    )

    kind = refusal(lambda: solve(lp, suboptimal, exact_sign, pivot_budget=1))
    assert kind == "pivot-budget", f"the exact simplex ran past its pivot budget ({kind})"

    grid, _ = rational_grid_cell()
    overlapped = [grid[0], [(x - Fraction(1, 2), y) for x, y in grid[1]]]
    kind = refusal(
        lambda: fixed_cell_lp(overlapped, rational_sign, zero=Fraction(0), one=Fraction(1))
    )
    assert kind == "no-separating-axis", (
        f"a cell was assembled for an overlapping pair, which has no axis to fix ({kind})"
    )


def main() -> int:
    the_cell_is_algebraic_for_trump_and_rational_for_an_axis_aligned_pose()
    the_exact_optimum_is_the_published_side_and_the_float_lp_sits_below_it()
    a_float_basis_is_repaired_rather_than_believed()
    the_exact_pose_leaves_no_incidence_undecided()
    the_exact_lp_refuses_every_input_it_cannot_decide()
    print("exact LP calibration and refusal contract selftest passed")
    return 0


@pytest.mark.slow
def test_promote_exact_lp() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
