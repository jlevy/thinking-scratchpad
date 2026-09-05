"""Behaviour checks for the Trump n = 11 isolation-radius tool (BC-199)."""

from __future__ import annotations

import functools
from fractions import Fraction
from typing import cast

import pytest

from cases.trump11 import isolation_radius as tool
from cases.trump11 import tangent_cones as tc

# Exact kappa_0 in Q(u), low degree first, as the tool pins it on branch 0.  A change here
# is a change in the modulus, the row set, or the field, and none of those is silent.
PINNED_KAPPA_0 = [
    "60680852275/318363336892",
    "-497863772859/636726673784",
    "201047601359/159181668446",
    "-565069686309/636726673784",
    "-328132348833/318363336892",
    "-257180183929/636726673784",
    "94594072305/79590834223",
    "-307238967815/636726673784",
]
PINNED_KAPPA_0_DECIMAL = "0.011480272061506444"


@functools.cache
def witness() -> tool.Witness:
    return tool.load_witness()


def test_branch_zero_modulus_is_pinned_exactly() -> None:
    w = witness()
    rows = w.branches[0]["rows"]
    modulus = tool.branch_modulus(w.field, rows, refine_limit=2)
    assert modulus["exact"] is True
    assert tool.record_element(modulus["kappa_lower"]) == PINNED_KAPPA_0
    assert tool.decimal(w.field, modulus["kappa_lower"]).startswith(PINNED_KAPPA_0_DECIMAL)
    assert modulus["kappa_lower"].sign() > 0
    assert (modulus["kappa_upper"] - modulus["kappa_lower"]).is_zero()


def test_reconstruct_stress_refuses_malformed_certificates() -> None:
    w = witness()
    rows = w.branches[0]["rows"]
    record = tool.load_record()
    certificate = record["branches"]["records"][0]["certificate"]
    stress = tool.reconstruct_stress(rows, certificate, w.field)
    assert len(stress) == tc.EXPECTED_BRANCH_ROWS
    assert all(weight.sign() > 0 for weight in stress)

    wrong_rank = {**certificate, "rank": 32}
    with pytest.raises(tool.IsolationRadiusError, match="rank"):
        tool.reconstruct_stress(rows, wrong_rank, w.field)

    missing_pivot = {**certificate, "pivot_rows": certificate["pivot_rows"][:-1]}
    with pytest.raises(tool.IsolationRadiusError, match="pivot rows"):
        tool.reconstruct_stress(rows, missing_pivot, w.field)

    negative_weight = {
        **certificate,
        "free_weights": {
            key: ("-1" if index == 0 else value)
            for index, (key, value) in enumerate(certificate["free_weights"].items())
        },
    }
    with pytest.raises(tool.IsolationRadiusError, match="strictly positive"):
        tool.reconstruct_stress(rows, negative_weight, w.field)

    with pytest.raises(tool.IsolationRadiusError, match="mapping"):
        tool.reconstruct_stress(rows, cast("dict", None), w.field)


def test_row_weights_must_be_positive_and_one_per_row() -> None:
    w = witness()
    rows = w.branches[0]["rows"]
    with pytest.raises(tool.IsolationRadiusError, match="row weights"):
        tool.branch_modulus(w.field, rows, row_weights=[Fraction(1)] * (len(rows) - 1))
    with pytest.raises(tool.IsolationRadiusError, match="row weights"):
        tool.branch_modulus(w.field, rows, row_weights=[Fraction(0)] * len(rows))


def test_every_branch_row_is_a_tied_elementary_gradient() -> None:
    w = witness()
    functions = tool.elementary_functions(w, Fraction(1, 64))
    assert len(functions) == 176 + 1760
    identification = tool.identify_rows(w, functions)
    assert identification["tied_functions_on_walls_and_contacts"] == 78
    assert identification["distinct_branch_rows"] > tc.EXPECTED_WALL_ROWS
    assert all(value > 0 for value in identification["row_curvature"].values())


def test_gap_and_symmetry_certificates_hold() -> None:
    w = witness()
    functions = tool.elementary_functions(w, Fraction(1, 64))
    gaps = tool.gap_radius(w, functions, Fraction(1, 64))
    assert gaps["active_features"] == tc.EXPECTED_RAW_FEATURES
    assert gaps["cap"].sign() > 0
    assert tool.decimal(w.field, gaps["least_nonzero_gap"]).startswith("0.0041338024")
    symmetry = tool.symmetry_radius(w, Fraction(1, 8))
    assert symmetry["certified_distance_at_least_threshold"] is True
    assert symmetry["radius"] == Fraction(1, 16)
    with pytest.raises(tool.IsolationRadiusError, match="threshold"):
        tool.symmetry_radius(w, Fraction(1))


def test_stress_ratio_identity_holds_on_branch_zero() -> None:
    w = witness()
    branch = w.branches[0]
    record = tool.load_record()
    stress = tool.reconstruct_stress(
        branch["rows"], record["branches"]["records"][0]["certificate"], w.field
    )
    far = tool.far_rows(branch["rows"])
    rho = sum(stress, w.field.zero) / sum((stress[index] for index in far), w.field.zero)
    assert tool.decimal(w.field, rho).startswith("4.51876250763899")
    assert tool.stress_ratio_identity(w, branch, rho)["holds"] is True
    assert tool.stress_ratio_identity(w, branch, rho + w.field.one)["holds"] is False
