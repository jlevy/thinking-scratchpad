"""The -W bridge agrees, and it would notice if either side moved.

The bridge check exists because exp-045's certificate and the accepted production
helpers were written independently and had never decided the same question. The
positive test replays the agreement; the controls prove the helpers refuse a doctored
direction rather than accommodating it, which is what makes the agreement evidence.
"""

from __future__ import annotations

import pytest

from cases.n5 import minus_w_owner4, minus_w_scale, tangent_cones, tangent_inventory
from devtools.check_minus_w_bridge import main
from sqpack.field import NumberField


@pytest.mark.slow
def test_the_bridge_agrees() -> None:
    assert main() == 0


@pytest.mark.slow
def test_a_doctored_direction_is_refused() -> None:
    """Perturbing one component of -W must break the helpers, not be absorbed."""
    field = NumberField((1, 0, -2), (1, 2))
    stratum = tangent_cones.STRATA[0]
    minus_w = [
        -component for component in tangent_inventory.geometry_vectors(field, stratum)[0]["W"]
    ]
    minus_w[4] = minus_w[4] + field.rational(1)
    zero = tuple(field.zero for _ in range(tangent_cones.VARIABLE_COUNT))
    with pytest.raises(ValueError, match="source path is not first-order tight"):
        minus_w_owner4.owner4_record(field, stratum, tuple(minus_w), zero)


@pytest.mark.slow
def test_the_scale_constant_actually_measures_the_direction() -> None:
    """The deciding constant is a genuine quadratic in the velocity, not a fixture.

    Two sensitivity controls: doubling the direction must scale the constant by exactly
    four (it is a quadratic form), and bumping a coordinate the active rows read --
    index 2 is one of the seven such coordinates at stratum A -- must move it. A
    constant that survived either would be a stored number, not a measurement.
    """
    field = NumberField((1, 0, -2), (1, 2))
    stratum = tangent_cones.STRATA[0]
    minus_w = tuple(
        -component for component in tangent_inventory.geometry_vectors(field, stratum)[0]["W"]
    )
    zero = tuple(field.zero for _ in range(tangent_cones.VARIABLE_COUNT))
    base = minus_w_scale.scale_records(field, stratum, minus_w, zero)[0].bounded_affine.constant

    doubled = minus_w_scale.scale_records(field, stratum, tuple(c + c for c in minus_w), zero)[
        0
    ].bounded_affine.constant
    assert doubled == base + base + base + base

    bumped_direction = list(minus_w)
    bumped_direction[2] = bumped_direction[2] + field.rational(1)
    try:
        bumped = minus_w_scale.scale_records(field, stratum, tuple(bumped_direction), zero)[
            0
        ].bounded_affine.constant
    except ValueError:
        return  # refused outright, which is the stronger outcome
    assert bumped != base, "a perturbed direction reproduced the certified constant"
