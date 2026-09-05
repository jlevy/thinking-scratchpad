"""Independent controls for the frozen synthetic n = 54 contract result."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from cases.n54_source_contract import verify as independent
from cases.n54_source_contract.verify import (
    VerificationError,
    canonical_bytes,
    load_result,
    verify_result,
)

PACKING = Path(__file__).resolve().parents[1]
FIXTURE = PACKING / "cases/n54_source_contract/synthetic_fixture.n54"


@pytest.fixture(scope="session")
def author_stdout(tmp_path_factory: pytest.TempPathFactory) -> bytes:
    completed = subprocess.run(
        [sys.executable, "-m", "cases.n54_source_contract.run", "--selftest"],
        cwd=PACKING,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr.decode()
    path = tmp_path_factory.mktemp("n54-independent") / "author-result.json"
    path.write_bytes(completed.stdout)
    return path.read_bytes()


@pytest.fixture
def prospective_result(tmp_path: Path, author_stdout: bytes) -> Path:
    path = tmp_path / "result.json"
    path.write_bytes(author_stdout)
    return path


def _document(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_bytes())
    assert isinstance(value, dict)
    return value


def _write(path: Path, document: dict[str, Any]) -> None:
    path.write_bytes(canonical_bytes(document))


def test_independent_verifier_parser_caps_are_load_bearing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def parse(raw: bytes) -> None:
        fixture = tmp_path / "bounded.n54"
        fixture.write_bytes(raw)
        monkeypatch.setattr(independent, "FIXTURE_SHA256", hashlib.sha256(raw).hexdigest())
        independent.parse_fixture(fixture)

    with pytest.raises(VerificationError, match="fixture byte cap exceeded"):
        parse(b" " * (independent.MAX_INPUT_BYTES + 1))

    with pytest.raises(VerificationError, match="comment byte cap exceeded"):
        parse(b"<!--@n54 " + b"x" * (independent.MAX_COMMENT_BYTES + 1) + b" -->")

    too_many_assignments = b"".join(
        f"<!--@n54 x{index} = 0 -->\n".encode("ascii")
        for index in range(independent.MAX_COMMENTS + 1)
    )
    with pytest.raises(VerificationError, match="comment cap exceeded"):
        parse(too_many_assignments)

    monkeypatch.setattr(independent, "MAX_COMMENTS", independent.MAX_ASSIGNMENTS + 1)
    with pytest.raises(VerificationError, match="assignment cap exceeded"):
        parse(too_many_assignments)

    too_many_tokens = "x = " + "+".join("1" for _ in range(independent.MAX_TOKENS // 2 + 1))
    with pytest.raises(VerificationError, match="formula token cap exceeded"):
        parse(f"<!--@n54 {too_many_tokens} -->".encode("ascii"))

    too_deep = "(" * (independent.MAX_DEPTH + 1) + "1" + ")" * (independent.MAX_DEPTH + 1)
    with pytest.raises(VerificationError, match="formula depth cap exceeded"):
        parse(f"<!--@n54 x = {too_deep} -->".encode("ascii"))

    too_many_digits = "1" * (independent.MAX_INTEGER_DIGITS + 1)
    with pytest.raises(VerificationError, match="integer digit cap exceeded"):
        parse(f"<!--@n54 x = {too_many_digits} -->".encode("ascii"))


def test_independent_verifier_import_closure_excludes_author_and_geometry() -> None:
    script = """
import sys
import cases.n54_source_contract.verify
blocked = {
    'cases.n54_source_contract.contract',
    'cases.n54_source_contract.run',
    'cases.unitsquare_precision.production.verify',
}
blocked_prefixes = ('sqpack.', 'sympy', 'lxml', 'xml.')
loaded = set(sys.modules)
raise SystemExit(
    1 if blocked & loaded or any(
        name == 'sqpack' or name.startswith(blocked_prefixes) for name in loaded
    ) else 0
)
"""
    completed = subprocess.run(
        [sys.executable, "-c", script],
        cwd=PACKING,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr.decode()


def test_independent_verifier_accepts_author_result(prospective_result: Path) -> None:
    receipt = verify_result(FIXTURE, prospective_result)
    assert receipt["verified"] is True
    assert receipt["action"] == "r2"
    assert receipt["assignments"] == 27
    assert receipt["correspondences"] == 54
    assert receipt["mutations"] == {
        "correspondence_swap": {
            "reason": "synthetic structural-tag drift",
            "rejected": True,
        },
        "missing_structural_inventory": {
            "reason": "missing or unexpected synthetic source endpoint",
            "rejected": True,
        },
    }


@pytest.mark.slow
def test_author_and_verifier_are_normal_optimized_byte_identical(
    prospective_result: Path,
) -> None:
    author_base = ["-m", "cases.n54_source_contract.run", "--selftest"]
    author_normal = subprocess.run(
        [sys.executable, *author_base],
        cwd=PACKING,
        capture_output=True,
        check=False,
    )
    author_optimized = subprocess.run(
        [sys.executable, "-O", *author_base],
        cwd=PACKING,
        capture_output=True,
        check=False,
    )
    assert author_normal.returncode == 0, author_normal.stderr.decode()
    assert author_optimized.returncode == 0, author_optimized.stderr.decode()
    assert author_normal.stdout == author_optimized.stdout == prospective_result.read_bytes()

    verifier_base = [
        "-m",
        "cases.n54_source_contract.verify",
        str(FIXTURE),
        str(prospective_result),
    ]
    normal = subprocess.run(
        [sys.executable, *verifier_base],
        cwd=PACKING,
        capture_output=True,
        check=False,
    )
    optimized = subprocess.run(
        [sys.executable, "-O", *verifier_base],
        cwd=PACKING,
        capture_output=True,
        check=False,
    )
    assert normal.returncode == 0, normal.stderr.decode()
    assert optimized.returncode == 0, optimized.stderr.decode()
    assert normal.stdout == optimized.stdout
    assert normal.stdout.endswith(b"\n")


def test_loader_rejects_nested_duplicate_key(prospective_result: Path) -> None:
    raw = prospective_result.read_bytes()
    mutated = raw.replace(
        b'"d4":{"action":"r2",',
        b'"d4":{"action":"r2","action":"r2",',
        1,
    )
    assert mutated != raw
    prospective_result.write_bytes(mutated)
    with pytest.raises(VerificationError, match="duplicate JSON key"):
        load_result(prospective_result)


@pytest.mark.parametrize("number", [b"8.0", b"8e0", b"8E+0"])
def test_loader_rejects_float_and_exponent_forms(
    prospective_result: Path, number: bytes
) -> None:
    raw = prospective_result.read_bytes()
    mutated = raw.replace(b'"elements":8,', b'"elements":' + number + b",", 1)
    assert mutated != raw
    prospective_result.write_bytes(mutated)
    with pytest.raises(VerificationError, match="non-integral JSON number"):
        load_result(prospective_result)


def test_loader_rejects_parse_constant(prospective_result: Path) -> None:
    raw = prospective_result.read_bytes()
    mutated = raw.replace(b'"elements":8,', b'"elements":NaN,', 1)
    assert mutated != raw
    prospective_result.write_bytes(mutated)
    with pytest.raises(VerificationError, match="non-finite JSON number"):
        load_result(prospective_result)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("unknown-top-level", "result field inventory changed"),
        ("schema", "result schema changed"),
        ("fixture-binding", "fixture binding changed"),
        ("field-binding", "field receipt binding changed"),
        ("witness-binding", "witness metadata binding changed"),
        ("d4-schema", "D4 receipt changed"),
        ("assignment-schema", "assignment result fields changed"),
    ],
)
def test_independent_verifier_rejects_schema_and_binding_mutations(
    prospective_result: Path, mutation: str, message: str
) -> None:
    document = _document(prospective_result)
    if mutation == "unknown-top-level":
        document["extra"] = None
    elif mutation == "schema":
        document["schema"] = "packing.squares:n54-source-contract/v2"
    elif mutation == "fixture-binding":
        document["fixture_sha256"] = "0" * 64
    elif mutation == "field-binding":
        document["field_receipt_sha256"] = "0" * 64
    elif mutation == "witness-binding":
        document["witness_sha256"] = "0" * 64
    elif mutation == "d4-schema":
        document["d4"]["products"] = 63
    elif mutation == "assignment-schema":
        document["assignments"][0]["extra"] = None
    else:
        raise AssertionError(f"unknown mutation: {mutation}")
    _write(prospective_result, document)
    with pytest.raises(VerificationError, match=message):
        verify_result(FIXTURE, prospective_result)


def test_independent_verifier_rejects_missing_structural_inventory(
    prospective_result: Path,
) -> None:
    document = _document(prospective_result)
    document["correspondence"].pop()
    _write(prospective_result, document)
    with pytest.raises(VerificationError, match="correspondence result inventory changed"):
        verify_result(FIXTURE, prospective_result)


def test_independent_verifier_rejects_bijective_correspondence_swap(
    prospective_result: Path,
) -> None:
    document = _document(prospective_result)
    first = document["correspondence"][0]
    second = document["correspondence"][1]
    first["row_id"], second["row_id"] = second["row_id"], first["row_id"]
    _write(prospective_result, document)
    with pytest.raises(VerificationError, match="synthetic structural-tag drift"):
        verify_result(FIXTURE, prospective_result)


def test_mutation_receipts_require_boolean_true(prospective_result: Path) -> None:
    document = _document(prospective_result)
    document["mutations"]["correspondence_swap"]["rejected"] = 1
    _write(prospective_result, document)
    with pytest.raises(VerificationError, match="mutation receipts changed"):
        verify_result(FIXTURE, prospective_result)


@pytest.mark.parametrize(
    ("mutation", "replacement"),
    [
        ("missing_structural_inventory", "accepted unexpectedly"),
        ("correspondence_swap", "accepted unexpectedly"),
    ],
)
def test_independent_verifier_rejects_mutation_receipt_drift(
    prospective_result: Path, mutation: str, replacement: str
) -> None:
    document = _document(prospective_result)
    document["mutations"][mutation] = {
        "rejected": False,
        "reason": replacement,
    }
    _write(prospective_result, document)
    with pytest.raises(VerificationError, match="mutation receipts changed"):
        verify_result(FIXTURE, prospective_result)
