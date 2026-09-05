#!/usr/bin/env python3
"""Contract for the rationalised `n = 29` system and the degree bound it supports.

This exists because the number it produces is cited: the integer-relation route refused
`s(29)` through degree twenty, and whether that refusal surveyed the space or a corner of
it depends on the system's actual degree.  A bound quoted from a script nobody can re-run
is not evidence, and a bound computed wrongly is worse than none.

**Two ways to get it wrong, both of which happened while writing this.**

*Leaving combined angles in.*  Composing rotations adds angles, so the raw equations
contain `cos(b - i)` and similar.  Substituting only `sin(a)` and `cos(a)` leaves those
alone, `Poly` then treats each as an opaque generator or constant, and the degrees come
out **wrong** -- the first run of this computation reported `[11, 20, 23, 22, 19, 6]` for
a Bezout bound of `12,690,480` where the truth is `[11, 15, 10, 15, 7, 6]` and
`1,039,500`.  So the decisive assertion here is that no trigonometric function survives
into the polynomials at all.

*Leaving the coefficients as floats.*  The transcription writes its constants as
`mp.mpf(1)` because its first two routes are numeric, and a Groebner basis or resultant
over SymPy `Float`s is not an exact computation.  The domain is asserted to be `QQ`.
"""

from __future__ import annotations

import pytest
import sympy as sp

from devtools.probe_system_degree import half_angle_system, reduce_by_side

#: Measured, and pinned so a change to the transcription cannot move them silently.
EXPECTED_DEGREES = (11, 15, 10, 15, 7, 6)
EXPECTED_BEZOUT = 1_039_500


def the_system_rationalises_to_polynomials() -> None:
    """Six polynomials in six unknowns, with nothing transcendental left in them."""
    polynomials, unknowns = half_angle_system()
    assert len(polynomials) == 6
    assert [str(symbol) for symbol in unknowns] == [
        "s",
        "u_a",
        "u_b",
        "u_c",
        "u_d",
        "u_i",
    ]
    for index, poly in enumerate(polynomials, 1):
        expression = poly.as_expr()
        leftover = expression.atoms(sp.sin, sp.cos, sp.tan)
        assert not leftover, (
            f"f{index} still contains {leftover}; a combined angle survived the "
            "half-angle substitution, so every degree below is measured against an "
            "opaque generator rather than the real system"
        )
        assert poly.domain == sp.QQ, (
            f"f{index} has coefficients over {poly.domain}, not QQ; an elimination over "
            "floats is a numerically unstable computation wearing an exact answer's "
            "clothes"
        )


def the_degrees_are_the_measured_ones() -> None:
    """The bound is cited, so it is pinned."""
    polynomials, unknowns = half_angle_system()
    degrees = tuple(poly.total_degree() for poly in polynomials)
    assert degrees == EXPECTED_DEGREES, (
        f"the rationalised degrees moved to {degrees}; the Bezout bound quoted in "
        "session-043 and the synopsis is computed from these"
    )
    bezout = 1
    for degree in degrees:
        bezout *= degree
    assert bezout == EXPECTED_BEZOUT, bezout

    side = unknowns[0]
    for index, poly in enumerate(polynomials, 1):
        assert poly.degree(side) == 1, (
            f"f{index} is degree {poly.degree(side)} in s, not 1; the elimination below "
            "starts from every equation being linear in the side"
        )


def eliminating_the_side_leaves_five_in_five() -> None:
    """`s` comes out of the smallest equation, and out of only two of the half-angles."""
    polynomials, unknowns = half_angle_system()
    reduction = reduce_by_side(polynomials, unknowns)
    assert reduction["pivot"] == "f6", reduction["pivot"]
    assert reduction["side_depends_on"] == ["u_b", "u_c"], (
        f"s now depends on {reduction['side_depends_on']}; that it involves only two of "
        "the five half-angles is the structure an elimination would exploit"
    )
    assert len(reduction["reduced"]) == 5
    for entry in reduction["reduced"]:
        assert entry["total_degree"] > 0
        assert entry["terms"] > 0


def main() -> int:
    the_system_rationalises_to_polynomials()
    the_degrees_are_the_measured_ones()
    eliminating_the_side_leaves_five_in_five()
    print("rationalised n=29 system and degree bound contract selftest passed")
    return 0


@pytest.mark.slow
def test_promote_system_degree() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
