"""The declaration tool writes the sweep's number and touches nothing else."""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from devtools.declare_least_cell_mass import declare, load_candidate
from devtools.run_fractional_colgen import RunSettings, run

RETAINED = (
    Path(__file__).resolve().parents[1]
    / "cases/n12_fractional_certificate/certificate-19-5.json"
)


def blanked_copy(tmp_path: Path) -> tuple[Path, str]:
    """The smallest retained certificate with its declaration removed."""

    record = json.loads(RETAINED.read_text())
    declared = record["least_cell_mass"]
    record["least_cell_mass"] = None
    path = tmp_path / "candidate.json"
    path.write_text(json.dumps(record, indent=1) + "\n")
    return path, declared


def test_the_declaration_is_the_retained_value_and_nothing_else_moves(tmp_path: Path) -> None:
    path, declared = blanked_copy(tmp_path)
    before = json.loads(path.read_text())
    certificate, _ = load_candidate(path)
    assert certificate.total_mass == Fraction(before["total_mass"])

    accepted, detail = declare(path)
    after = json.loads(path.read_text())

    assert accepted
    assert "accepted=True" in detail
    assert Fraction(after["least_cell_mass"]) == Fraction(declared)
    assert {k: v for k, v in after.items() if k != "least_cell_mass"} == {
        k: v for k, v in before.items() if k != "least_cell_mass"
    }


def test_an_existing_declaration_is_kept_unless_overwrite_is_asked(tmp_path: Path) -> None:
    path, declared = blanked_copy(tmp_path)
    record = json.loads(path.read_text())
    record["least_cell_mass"] = "1/7"
    path.write_text(json.dumps(record, indent=1) + "\n")

    accepted, detail = declare(path)
    assert not accepted
    assert "already declares" in detail
    assert json.loads(path.read_text())["least_cell_mass"] == "1/7"

    assert declare(path, overwrite=True)[0]
    assert json.loads(path.read_text())["least_cell_mass"] == declared


def test_a_candidate_the_sweep_refuses_is_left_untouched(tmp_path: Path) -> None:
    """``n = 1`` with mass above one fails Condition 2: no number is written."""

    settings = RunSettings(
        n=1,
        outer_side=Fraction(2),
        square_side=Fraction(1),
        grid_counts=(3,),
        inset=Fraction(1, 2),
        angle_limit=Fraction(1, 10),
        direction_steps=1,
        scale=1000,
        column_rounds=1,
        max_rounds=8,
        rows_per_direction=2,
    )
    freeze = tmp_path / "refused.json"
    result = run(settings, log_path=None, freeze=freeze, verify_serial=False)
    assert result["converged"] is True
    before = freeze.read_bytes()

    accepted, detail = declare(freeze)
    assert not accepted
    assert "accepted=False" in detail
    assert freeze.read_bytes() == before
