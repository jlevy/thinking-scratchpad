"""Goebel's family is optimal at four sizes and two of them have no construction here.

`D-389` was this project pricing a route to an exact `n = 40` pose while the construction
sat published in a source already transcribed here. The correction was specific to
`n = 40`; the general question is which other sizes the same family already answers, and it
answers two more.

The assertion that earns its place is the near miss. At `n = 28` the family gives a
*valid* packing whose side is `0.004` worse than the best known, at algebraic degree 6 --
so the `n = 40` answer does not carry over, and a future reader who notices `28 = 2(4) + 4
+ 16` and expects it to is stopped here rather than after an afternoon.
"""

from __future__ import annotations

import json
import math

import pytest

from cases.gobel40.packing import build as retained_n40
from devtools.price_gobel_family import OUT, assess, build, parameters
from sqpack.verify import exact_sign, verify_packing


def _record() -> dict:
    return json.loads(OUT.read_text(encoding="utf-8"))


def test_the_family_is_optimal_at_four_sizes() -> None:
    built = _record()

    assert built["reached"] == 12
    assert built["optimal_at"] == [5, 40, 65, 89]
    assert built["already_built_here"] == [5, 40, 65, 89]
    assert built["buildable_and_not_built"] == []


def test_every_optimal_size_verifies_exactly() -> None:
    """Feasibility decided by exact sign, not by the decimals that led here."""
    for row in _record()["family"]:
        if not row["matches_best_known"]:
            assert "verified" not in row
            continue
        assert row["verified"]["valid"] is True
        assert row["verified"]["squares"] == row["n"]
        assert row["verified"]["pairs_tested"] == row["n"] * (row["n"] - 1) // 2


def test_n28_is_a_near_miss_and_the_record_says_why() -> None:
    """The one that stops the obvious next guess."""
    miss = _record()["the_near_miss"]

    assert miss["n"] == 28
    assert 0.003 < miss["worse_by"] < 0.005
    assert "degree 6" in miss["why_it_matters"]
    assert "does not carry over" in miss["why_it_matters"]

    row = next(one for one in _record()["family"] if one["n"] == 28)
    assert row["matches_best_known"] is False
    assert row["best_known_degree"] == 6


def test_the_generalization_reproduces_the_retained_n40_case() -> None:
    """The control: `cases/gobel40` is this builder at `a = 3, b = 4` and must agree.

    Without it the generalization could be wrong everywhere and still look plausible, since
    nothing else in the repository builds `n = 65` or `n = 89` to check against.
    """
    mine, my_side, _field = build(3, 4)
    theirs, their_side, _other = retained_n40()

    # Each builder makes its own `NumberField`, and the field API refuses to compare
    # elements across two of them -- deliberately, since identity is what distinguishes
    # `Q(sqrt 2)` from a lookalike. So the comparison is on coefficients, which are plain
    # rationals and mean the same thing in either field.
    def shape(squares) -> list:
        return sorted(
            sorted((tuple(x.coeffs), tuple(y.coeffs)) for x, y in square) for square in squares
        )

    assert len(mine) == len(theirs) == 40
    assert tuple(my_side.coeffs) == tuple(their_side.coeffs)
    assert shape(mine) == shape(theirs)


@pytest.mark.slow
def test_the_new_sizes_are_built_here_and_not_merely_asserted() -> None:
    """`n = 65` and `n = 89` verified from the pose rather than read from the record."""
    for a, b, n in ((4, 5, 65), (4, 7, 89)):
        squares, side, _field = build(a, b)
        assert len(squares) == n
        report = verify_packing(squares, side, sign=exact_sign)
        assert report.valid
        assert report.n == n


def test_the_parameter_sweep_obeys_goebels_condition() -> None:
    for a, b in parameters():
        assert a - 1 < b / math.sqrt(2) < a + 1
        assert 2 * a * a + 2 * a + b * b <= 100


def test_nothing_here_promotes_anything() -> None:
    subject = _record()["subject"]

    assert "not shown optimal" in subject["promotes_nothing"]
    assert "only makes possible" in subject["promotes_nothing"]


@pytest.mark.slow
def test_the_record_round_trips() -> None:
    assert _record() == assess()
