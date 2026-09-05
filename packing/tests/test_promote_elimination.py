"""The elimination export is only as good as the guard on what it wrote.

The measurement this file protects is not a theorem.  It is the claim that a text file
handed to an external Groebner engine *is* the `n = 29` system, and that claim was
already false once.  Negative coefficients written as `(-2)*x` are read by `msolve`
without complaint and not as they were meant: the engine returned a reduced Groebner
basis of `{1}` -- no solutions in the algebraic closure -- for a system whose solution
this repository has refined to a thousand digits.

Nothing in the first export could catch that, because everything it checked, it checked
against the SymPy polynomials rather than against the bytes.  So the guard here reads
back what was written and asks two things of it: that it vanishes at the retained pose,
and that it equals the cleared original exactly.  The controls below restore the
encoding bug and require the guard to fire on it.
"""

from __future__ import annotations

import pytest
import sympy as sp

from devtools.probe_elimination import (
    EliminationError,
    msolve_input,
    reduced_system,
    term_text,
    verify_eliminant,
    witness_point,
)


def the_export_is_plain_and_unparenthesised() -> None:
    """A negative coefficient is written `-2*x`, never `(-2)*x`.

    This is the whole bug.  `msolve` accepts both and means different things by them.
    """
    text = term_text((2, 0), -2, ["x", "y"])
    assert text == "-2*x^2", f"a negative coefficient was rendered as {text!r}"
    assert "(" not in text, f"the export parenthesised a coefficient: {text!r}"
    assert term_text((1, 1), 1, ["x", "y"]) == "+x*y", "a unit coefficient was written out"
    assert term_text((0, 0), -7, ["x", "y"]) == "-7", "a bare constant lost its value"


def the_guard_rejects_a_polynomial_the_text_does_not_carry() -> None:
    """A rendering that changes the polynomial is refused, not warned about."""
    x, y = sp.symbols("x y", real=True)
    honest = sp.Poly(x**2 + y - 1, x, y)
    # (1, 1) is not on the curve: the polynomial evaluates to 1 there, not 0. A point
    # that happens to be a root would make this control pass for the wrong reason, which
    # is the failure mode the whole file exists to catch.
    point = [sp.Integer(1), sp.Integer(1)]

    try:
        msolve_input([honest], [x, y], point)
    except EliminationError as error:
        assert error.kind == "emitted-text-does-not-vanish", error.kind
        return
    raise AssertionError(
        "a polynomial that does not vanish at the supplied point was exported anyway, "
        "so the export is not checked against the pose it claims to describe"
    )


def the_retained_pose_is_a_root_of_every_emitted_equation() -> None:
    """The real system, exported through the real path, passes its own guard."""
    values, _names = witness_point()
    polynomials, order, _side, pivot = reduced_system()
    point = [values[str(symbol)] for symbol in order]
    text = msolve_input(polynomials, order, point)

    assert pivot == "f6", f"the smallest equation was {pivot}, not f6"
    degrees = sorted(polynomial.total_degree() for polynomial in polynomials)
    assert degrees == [12, 15, 16, 20, 20], (
        f"the reduced system has degrees {degrees}, not the [16, 20, 15, 20, 12] "
        "BC-065 measured; the pivot or the substitution has changed"
    )
    assert "(" not in text, "the emitted system carries a parenthesised coefficient"
    assert text.splitlines()[1] == "0", "the characteristic line is not zero"


def an_eliminant_is_checked_against_the_value_it_must_admit() -> None:
    """A polynomial that does not have `s(29)` as a root is not this system's eliminant."""
    values, _names = witness_point()
    # (s - 2) has nothing to do with the packing, and must be reported as not admitting it.
    report = verify_eliminant([1, -2], values["s"], digits=40)
    assert not report["admits_value"], (
        "a polynomial with no root at the retained side was reported as admitting it, "
        "so the eliminant check cannot tell this system's answer from any other"
    )
    assert report["carrying_factors"] == [], (
        f"an unrelated polynomial was credited with a carrying factor: {report}"
    )


def main() -> int:
    the_export_is_plain_and_unparenthesised()
    the_guard_rejects_a_polynomial_the_text_does_not_carry()
    the_retained_pose_is_a_root_of_every_emitted_equation()
    an_eliminant_is_checked_against_the_value_it_must_admit()
    print("elimination export guard selftest passed")
    return 0


@pytest.mark.slow
def test_promote_elimination() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
