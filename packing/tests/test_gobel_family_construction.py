"""`n = 65` and `n = 89` are Goebel's family, and their retained witnesses always were.

The construction is the general form of the rule `cases/gobel40` uses at `a = 3, b = 4`, so
the assertion that matters most is the control: built at `(3, 4)` the general builder must
reproduce that case corner for corner. Without it the generalization could be wrong at every
other `(a, b)` and still look plausible, since nothing else here builds `n = 65` or `n = 89`.

The second is the identification. Both retained witnesses agree with this construction to
about `5e-33` -- which no independently optimised numeric reaches for a construction it was
not built from. So those `numerical-multiprecision` records are materialisations of this
family, exactly as `n = 40`'s turned out to be, and the test pins the bound that says so.
"""

from __future__ import annotations

import decimal
from decimal import Decimal

import pytest

from cases.gobel40.packing import build as retained_n40
from cases.gobel40.verify_exact import witness_disagreement as gobel40_gap
from cases.gobel_family.packing import admits, build, count
from cases.gobel_family.verify_exact import (
    SUBJECTS,
    WITNESS_ROUNDING,
    verify,
    witness_disagreement,
)
from sqpack.verify import exact_sign, verify_packing


def test_the_general_builder_reproduces_the_retained_n40_case() -> None:
    """The control. Coefficients rather than field elements, since each build makes its own
    `NumberField` and the API refuses to compare across two -- which is the point of it."""
    mine, my_side, _field = build(3, 4)
    theirs, their_side, _other = retained_n40()

    def shape(squares) -> list:
        return sorted(
            sorted((tuple(x.coeffs), tuple(y.coeffs)) for x, y in square) for square in squares
        )

    assert len(mine) == len(theirs) == 40
    assert tuple(my_side.coeffs) == tuple(their_side.coeffs)
    assert shape(mine) == shape(theirs)


@pytest.mark.slow
@pytest.mark.parametrize(("a", "b"), SUBJECTS)
def test_each_new_size_verifies_exactly(a: int, b: int) -> None:
    """Every one of the 2,080 and 3,916 pairs, decided by an exact sign over `Q(sqrt 2)`.

    Deferred at `(4, 7)`, where it measured 5.09s on CI's two-core runner (run for
    `c1120c44`, job 101371257966) against a 5s per-test ceiling: 1.65s locally, of which
    the build is 0.56s and the 3,916 exact pair decisions the rest. Unlike the three
    atlas tests this branch made cheap, the cost here is not a shared build billed to a
    neighbour -- `build` is not memoized, and this test pays only for itself -- so there
    is nothing to substitute and the marker is the honest instrument.

    The pull-request surface does not lose the check. `packing-validate`'s
    `exact verification` step is `fast=True` and runs `python -m
    cases.gobel_family.verify_exact` on every push, whose `main()` makes these same three
    assertions at both subjects before it makes the duplicate and witness ones. What
    moves to the deep surface is a second reading of a decision the fast tier already
    pays for in another process.

    Its sibling `test_a_duplicated_square_is_rejected` is 1.67s locally at `(4, 7)` --
    the same work, one square longer -- and reported under 5s on that run. It stays,
    because OR-13 takes a test off the pull-request surface on its own measured cost and
    nothing else; the number is recorded here so the next reading has something to
    compare against rather than a judgement to repeat.
    """
    n = count(a, b)
    report = verify(a, b)

    assert report.valid is True
    assert report.n == n
    assert report.pairs_tested == n * (n - 1) // 2


@pytest.mark.parametrize(("a", "b"), SUBJECTS)
def test_a_duplicated_square_is_rejected(a: int, b: int) -> None:
    """Without this, "valid" only means the checker returned."""
    squares, side, _field = build(a, b)

    assert verify_packing([*squares, squares[0]], side, sign=exact_sign).valid is False


@pytest.mark.parametrize(("a", "b"), SUBJECTS)
def test_the_witness_is_identified_not_merely_permitted(a: int, b: int) -> None:
    """`5e-33` is the witness's own rounding, not a tolerance chosen to fit."""
    gap = witness_disagreement(a, b)

    assert gap is not None
    assert gap <= WITNESS_ROUNDING
    assert gap < Decimal("1e-32")


def test_the_sizes_are_the_two_that_had_no_construction() -> None:
    assert sorted(count(a, b) for a, b in SUBJECTS) == [65, 89]
    assert all(admits(a, b) for a, b in SUBJECTS)


def test_a_pair_outside_goebels_condition_is_refused() -> None:
    """The rule has a condition and the builder may not quietly ignore it."""
    assert not admits(1, 4)
    with pytest.raises(ValueError, match="does not satisfy"):
        build(1, 4)


def test_measuring_the_gap_leaves_the_global_precision_alone() -> None:
    """`decimal`'s context is process-global, so raising it must be scoped.

    Bead `think-iskp` fixed `sqpack.field` and left "any sibling doing the same" open.
    These were the siblings: both `witness_disagreement` functions set
    `getcontext().prec` and never restored it, and the family one is reachable from the
    fast suite, so every test after it saw precision 60. Nothing was wrong -- every
    consumer that formats a Decimal against a recorded value pins its own context -- but a
    new one that did not would have broken on test ordering alone.
    """
    before = decimal.getcontext().prec
    assert witness_disagreement(4, 5) is not None
    assert decimal.getcontext().prec == before
    assert gobel40_gap() is not None
    assert decimal.getcontext().prec == before
