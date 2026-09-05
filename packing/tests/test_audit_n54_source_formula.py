from __future__ import annotations

import json
import subprocess
import sys

import pytest

from devtools.audit_n54_source_formula import derive_receipt


@pytest.mark.slow
def test_n54_source_formula_closes_in_one_quartic_field() -> None:
    receipt = derive_receipt()

    assert receipt["field"] == {
        "name": "Q(p)",
        "primitive": "p = sqrt(1 + sqrt(2))",
        "minimal_polynomial_coefficients": [1, 0, -2, 0, -1],
        "embedding": "positive real root p in (1.5537, 1.5538)",
    }
    assert receipt["minimal_polynomials"] == {
        "side": [4, -112, 1164, -5304, 8897],
        "tan_angle": [7, -12, 6, -4, -1],
        "sin_angle": [8, -16, 16, -8, 1],
        "cos_angle": [8, -16, 0, 16, -7],
    }


@pytest.mark.slow
def test_n54_source_formula_cli_agrees_under_optimization() -> None:
    base = ["-m", "devtools.audit_n54_source_formula", "--check"]
    normal = subprocess.run(
        [sys.executable, *base],
        check=True,
        capture_output=True,
        text=True,
    )
    optimized = subprocess.run(
        [sys.executable, "-O", *base],
        check=True,
        capture_output=True,
        text=True,
    )

    assert json.loads(normal.stdout) == json.loads(optimized.stdout)


def test_perturbed_side_basis_is_refused() -> None:
    """A wrong basis coefficient must fail the side identity, not reach a receipt."""
    with pytest.raises(ValueError, match="n=54 source identity failed: side basis"):
        derive_receipt(mutation="perturbed-side-basis")

    refused = subprocess.run(
        [
            sys.executable,
            "-m",
            "devtools.audit_n54_source_formula",
            "--mutate",
            "perturbed-side-basis",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert refused.returncode == 1
    assert refused.stdout == ""
    assert "side basis" in refused.stderr


@pytest.mark.slow
def test_changed_minimal_polynomial_is_refused() -> None:
    """The minimal-polynomial comparison must be a second, independent gate."""
    with pytest.raises(ValueError, match="unexpected n=54 minimal polynomials"):
        derive_receipt(mutation="changed-minimal-polynomial")

    refused = subprocess.run(
        [
            sys.executable,
            "-m",
            "devtools.audit_n54_source_formula",
            "--mutate",
            "changed-minimal-polynomial",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert refused.returncode == 1
    assert refused.stdout == ""
    assert "8896" in refused.stderr


def test_unknown_negative_control_is_refused() -> None:
    with pytest.raises(ValueError, match="unknown n=54 negative control"):
        derive_receipt(mutation="not-a-control")
