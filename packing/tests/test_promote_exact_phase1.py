#!/usr/bin/env python3
"""Phase 1 of the exact simplex: a starting vertex built from the coefficients alone.

BC-061 shipped the exact cell solver one step short of self-sufficient.  `solve` pivots
to the exact optimum from a feasible vertex, and the vertex came from HiGHS -- fast, and
a dependency on a float solver for the one thing exact arithmetic was brought in to
replace.  D-021's floor then still governed where the search could start.  What follows
is that dependency removed, and the removal measured.

**Trump's cell is solved with no float solver anywhere.**  From its 1,056 rows and 23
variables alone, phase 1 reaches a feasible vertex in 42 pivots -- a genuine corner of
the polytope, at side `6.123390901223`, 2.25 above the answer -- and phase 2 walks that
vertex down in 16 more pivots to the published `3.877083590022`, the difference exactly
zero by `FieldElement.is_zero` and all 22 translation coordinates exactly zero.  The
reconstruction verifies with 14 touching pairs.  Nothing on the path from `build()` to
that number imports a float solver, and an AST scan of those four files and of this one
asserts it.

**It costs about 100 seconds.**  73 s in phase 1 and 27 s in phase 2 on this session's
machine, against 2.6 s for the same cell started from a HiGHS basis -- which lands on an
optimal vertex and spends no exact pivots at all.  A forty-fold speedup is worth having,
and starting from the float basis remains the right first move wherever one exists.
What it is no longer is required.

**Infeasibility is proved rather than guessed at.**  Four unit squares in a container
pinned to side 1 have nowhere to go; phase 1's auxiliary optimum is positive, and it
refuses with kind `infeasible` after 6 pivots instead of returning a point.  So does a
one-variable contradiction.  A refusal here is a proof that the cell is empty, not a
search that gave up.

**One implementation covers both scalar types.**  The axis-aligned four-square cell runs
the same `feasible_basis` over `Fraction` -- 160 rows, 9 variables, 10 phase-1 pivots,
then 0 phase-2 pivots onto the exact optimum 2 -- with no number field constructed
anywhere.
"""

from __future__ import annotations

import ast
import time
from collections.abc import Callable
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

import pytest

from cases.trump11.packing import build
from sqpack.exact_lp import (
    ExactLP,
    ExactLPError,
    LinearRow,
    auxiliary_program,
    feasible_basis,
    fixed_cell_lp,
    rational_sign,
    solve,
    solve_from_scratch,
    translated_squares,
)
from sqpack.field import FieldElement, NumberField
from sqpack.verify import exact_sign, verify_packing

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# The four files an exact cell solve actually executes, from the case's own pose to the
# certified side.  The claim this file makes is about these, not about the suite around
# them: none of them may reach a float solver or a float numeric stack.
EXACT_PATH = (
    PROJECT_ROOT / "src/sqpack/exact_lp.py",
    PROJECT_ROOT / "src/sqpack/field.py",
    PROJECT_ROOT / "src/sqpack/verify.py",
    PROJECT_ROOT / "cases/trump11/packing.py",
)
FLOAT_NUMERICS = frozenset({"cvxpy", "highspy", "mpmath", "numpy", "pulp", "scipy"})

# Enough digits to place the phase-1 vertex against the optimum, and far short of what
# deciding either of them needed: every comparison below is by exact sign, and this is
# only how the two are printed.
READOUT_DIGITS = 12


def outcome[T](action: Callable[[], T]) -> tuple[T | None, str]:
    """Run `action` and report `(value, "none")`, or `(None, kind)` if it refused.

    Written this way rather than with `pytest.raises` so that a refusal where one was
    not wanted fails with a sentence about what the solver would not do, which is what a
    negative control has to read back.
    """
    try:
        return action(), "none"
    except ExactLPError as error:
        return None, error.kind


def refusal(action: Callable[[], object]) -> str:
    """Name the exact-LP refusal `action` raised, or `none` if it returned."""
    return outcome(action)[1]


def read_out(field: NumberField, value: FieldElement) -> str:
    """`value` to `READOUT_DIGITS` decimals, every one of them certain."""
    return field.decimal(value, READOUT_DIGITS)[: READOUT_DIGITS + 2]


def rational_grid_cell() -> tuple[list[list[tuple[Fraction, Fraction]]], ExactLP]:
    """Four unit squares in a side-2 container: the axis-aligned cell, over `Fraction`."""

    def unit(x: int, y: int) -> list[tuple[Fraction, Fraction]]:
        corner = (Fraction(x), Fraction(y))
        return [
            corner,
            (corner[0] + 1, corner[1]),
            (corner[0] + 1, corner[1] + 1),
            (corner[0], corner[1] + 1),
        ]

    grid = [unit(0, 0), unit(1, 0), unit(0, 1), unit(1, 1)]
    return grid, fixed_cell_lp(grid, rational_sign, zero=Fraction(0), one=Fraction(1))


def with_side_capped_at(lp: ExactLP, bound: int) -> ExactLP:
    """The axis-aligned cell with its container side pinned from above, which empties it."""
    cap = [Fraction(0)] * lp.width
    cap[lp.width - 1] = Fraction(1)
    return ExactLP(
        objective=lp.objective,
        rows=(*lp.rows, LinearRow("cap:side", tuple(cap))),
        rhs=(*lp.rhs, Fraction(bound)),
        zero=lp.zero,
        one=lp.one,
    )


def imported_roots(path: Path) -> set[str]:
    """Top-level package names `path` imports, read off its syntax rather than run."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


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

    Cached because assembling it reads 55 separating axes through exact sign tests.
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


def the_phase_1_edge_falls_away_from_every_row_it_must_enter() -> None:
    """The auxiliary program's weights are what make its starting edge enterable."""
    _, lp = rational_grid_cell()
    built, kind = outcome(lambda: auxiliary_program(lp, rational_sign))
    assert kind == "none", (
        f"phase 1 could not build an edge into the axis-aligned cell ({kind}), so its "
        f"artificial column is not weighted heavily enough for the rows to fall away"
    )
    assert built is not None
    program, start = built
    print(f"  grid cell:   {len(lp.rows)} rows, width {lp.width} -> auxiliary {program.width}")
    assert program.width == lp.width + 1, (
        f"the auxiliary program has width {program.width}, not the one artificial "
        f"variable over {lp.width} that phase 1 adds"
    )
    assert len(program.rows) == len(lp.rows) + 1, (
        f"the auxiliary program has {len(program.rows)} rows, so the floor `t >= 0` that "
        f"bounds it below is missing"
    )
    assert len(start) == program.width, (
        f"phase 1 offered {len(start)} active rows for a {program.width}-variable "
        f"auxiliary program"
    )


def the_constructed_start_is_a_feasible_vertex_before_a_single_pivot() -> None:
    """Phase 1 enters its own program at a vertex, not at a point it hopes is one."""
    _, lp = rational_grid_cell()
    program, start = auxiliary_program(lp, rational_sign)
    kind = refusal(lambda: solve(program, start, rational_sign, pivot_budget=0))
    assert kind in {"none", "pivot-budget"}, (
        f"the phase-1 start is not a feasible vertex of the auxiliary program ({kind}), "
        f"so the height it was placed at does not clear every row"
    )
    print(f"  grid cell:   the constructed start is feasible before pivoting ({kind})")


def the_axis_aligned_cell_is_solved_over_the_rationals_with_no_field_anywhere() -> None:
    """`Fraction` in, `Fraction` out: the same phase 1, over a cell that needs no field."""
    _, lp = rational_grid_cell()
    start = feasible_basis(lp, rational_sign)
    solution, kind = outcome(lambda: solve_from_scratch(lp, rational_sign))
    assert kind == "none", (
        f"phase 1 handed phase 2 a start it refused ({kind}), so the active set was not "
        f"read at the point phase 1 actually reached"
    )
    assert solution is not None
    print(
        f"  grid cell:   {start.pivots} phase-1 pivots, {solution.pivots} phase-2 pivots, "
        f"optimum {solution.vertex.objective_value}"
    )
    assert solution.vertex.objective_value == Fraction(2), (
        f"the rational cell's exact optimum is {solution.vertex.objective_value}, not the "
        f"side 2 that four unit squares in a 2x2 container force"
    )
    assert not start.started_feasible, (
        "the crash basis was reported already feasible, so this cell measures nothing "
        "about the search phase 1 has to do"
    )
    scalars = [*solution.vertex.point, *solution.vertex.multipliers]
    assert all(isinstance(value, Fraction) for value in scalars), (
        "a scalar outside Fraction reached the answer, so the rational path is not the "
        "one that ran"
    )


def phase_1_proves_infeasibility_rather_than_failing_to_find_a_point() -> None:
    """An empty cell is refused with a reason, and the reason is the auxiliary optimum."""
    _, lp = rational_grid_cell()
    kind = refusal(lambda: feasible_basis(with_side_capped_at(lp, 1), rational_sign))
    assert kind == "infeasible", (
        f"four unit squares were fitted into a side-1 container rather than refused "
        f"({kind}), so a positive phase-1 optimum is not being read as a proof of "
        f"emptiness"
    )
    print(f"  grid cell:   a side-1 container is refused as {kind}")

    contradiction = ExactLP(
        objective=(Fraction(1),),
        rows=(
            LinearRow("at-most-zero", (Fraction(1),)),
            LinearRow("at-least-one", (Fraction(-1),)),
        ),
        rhs=(Fraction(0), Fraction(-1)),
        zero=Fraction(0),
        one=Fraction(1),
    )
    kind = refusal(lambda: feasible_basis(contradiction, rational_sign))
    assert kind == "infeasible", (
        f"`x <= 0` together with `x >= 1` was answered with a point rather than refused "
        f"({kind})"
    )


def phase_1_refuses_when_it_runs_past_its_pivot_budget() -> None:
    """Bland's rule proves phase 1 terminates; the budget reports it if the proof breaks."""
    _, lp = rational_grid_cell()
    kind = refusal(lambda: feasible_basis(lp, rational_sign, pivot_budget=0))
    assert kind == "pivot-budget", (
        f"phase 1 ran past its pivot budget ({kind}), so a search that never terminated "
        f"would hang rather than report"
    )


def no_float_solver_is_reachable_from_the_exact_path() -> None:
    """The files an exact cell solve executes, and this one, import no float numerics."""
    for path in (*EXACT_PATH, Path(__file__).resolve()):
        leaked = sorted(imported_roots(path) & FLOAT_NUMERICS)
        assert not leaked, (
            f"{path.name} imports {leaked}, so the measurement below is not the "
            f"float-free one this file claims to report"
        )
    print(f"  exact path:  {len(EXACT_PATH) + 1} files, no float numerics imported")


def trumps_cell_is_solved_from_its_own_coefficients_and_lands_on_the_published_side() -> None:
    """The known-answer run: no float solver anywhere, against Trump's degree-8 root."""
    cell = trump_cell()
    squares, side, field, lp = cell.squares, cell.side, cell.field, cell.lp
    began = time.monotonic()
    start = feasible_basis(lp, exact_sign)
    found = time.monotonic()
    solution, kind = outcome(lambda: solve(lp, start.active, exact_sign))
    ended = time.monotonic()
    assert kind == "none", (
        f"phase 2 refused the vertex phase 1 found ({kind}), so what phase 1 returned "
        f"was not a feasible vertex of Trump's cell"
    )
    assert solution is not None
    print(
        f"  trump11:     phase 1 {start.pivots} pivots in {found - began:.0f}s to side "
        f"{read_out(field, start.point[-1])}, then phase 2 {solution.pivots} pivots in "
        f"{ended - found:.0f}s to {read_out(field, solution.vertex.objective_value)} "
        f"(published {read_out(field, side)})"
    )

    no_search = (
        "phase 1 reported Trump's cell already solved by its crash basis, so no search "
        "was measured"
    )
    assert start.pivots > 0, no_search
    assert not start.started_feasible, no_search
    assert solution.pivots > 0, (
        "phase 1 landed on the optimum itself, so phase 2 was never asked to improve the "
        "vertex it was handed"
    )
    assert (solution.vertex.objective_value - side).is_zero(), (
        "the exactly solved cell, started with no float seed, is not Trump's published side"
    )
    moved = [
        index for index, value in enumerate(solution.vertex.point[:-1]) if not value.is_zero()
    ]
    assert moved == [], (
        f"the exact optimum translates {len(moved)} of the 22 centre coordinates, so it is "
        f"a different packing from the certificate's"
    )
    report = verify_packing(
        translated_squares(squares, solution.vertex.point),
        solution.vertex.objective_value,
        exact_sign,
    )
    assert report.valid, f"the float-free reconstruction does not verify: {report}"
    print(f"  trump11:     reconstruction verifies, {report.touching_pairs} touching pairs")


def main() -> int:
    the_phase_1_edge_falls_away_from_every_row_it_must_enter()
    the_constructed_start_is_a_feasible_vertex_before_a_single_pivot()
    the_axis_aligned_cell_is_solved_over_the_rationals_with_no_field_anywhere()
    phase_1_proves_infeasibility_rather_than_failing_to_find_a_point()
    phase_1_refuses_when_it_runs_past_its_pivot_budget()
    no_float_solver_is_reachable_from_the_exact_path()
    trumps_cell_is_solved_from_its_own_coefficients_and_lands_on_the_published_side()
    print("exact LP phase-1 selftest passed")
    return 0


@pytest.mark.slow
def test_promote_exact_phase1() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
