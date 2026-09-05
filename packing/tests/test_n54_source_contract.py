"""Author controls for BC-141 parsing, field, D4, correspondence, and result bytes.

Result-file publication, independent verification, source and target access, and packing
geometry remain outside this synthetic test surface.
"""

from __future__ import annotations

import copy
import subprocess
import sys
from dataclasses import replace
from fractions import Fraction
from pathlib import Path
from time import monotonic
from typing import Any, cast

import pytest

from cases.n54_source_contract import contract as author
from cases.n54_source_contract.contract import (
    D4_IDENTITY,
    D4_ORDER,
    EXPECTED_FIELD_RECEIPT_SHA256,
    EXPECTED_FIXTURE_SHA256,
    FIELD_ONE,
    FIELD_P,
    FIELD_ZERO,
    FULL_LABELS,
    LOCAL_LABELS,
    WITNESS_ROW_IDS,
    WITNESS_SHA256,
    Assignment,
    CompatibilityEdge,
    ContractError,
    D4Element,
    FieldElement,
    OrientationClass,
    OrientationVector,
    SyntheticEndpoint,
    act_on_orientation,
    bind_field_receipt,
    build_n54_result,
    build_n54_result_bytes,
    canonical_expression,
    canonical_json_bytes,
    evaluate_fixture,
    half_turn_label,
    label_inventory,
    load_canonical_json,
    parse_fixture,
    replay_d4_contract,
    select_synthetic_correspondence,
)
from devtools.audit_n54_source_formula import derive_receipt

FIXTURE = Path("cases/n54_source_contract/synthetic_fixture.n54")


def _comment(payload: str) -> bytes:
    return f"<!--@n54 {payload}-->\n".encode()


def test_synthetic_fixture_is_fully_consumed_in_declared_order() -> None:
    parsed = parse_fixture(FIXTURE.read_bytes())

    expected_names = tuple(label.replace("/", "_") for label in LOCAL_LABELS)
    assert tuple(assignment.name for assignment in parsed.assignments) == expected_names
    assert len(parsed.assignments) == 27


def test_closed_grammar_has_a_canonical_immutable_ast() -> None:
    parsed = parse_fixture(
        _comment("first = 00012") + _comment("second = -(first + Sin[a]) * (Cos[a] - 2) / 3")
    )
    first, second = parsed.assignments

    assert isinstance(first, Assignment)
    assert canonical_expression(first.expression) == ("integer", "12")
    assert canonical_expression(second.expression) == (
        "divide",
        (
            "multiply",
            (
                "negation",
                ("add", ("symbol", "first"), ("symbol", "Sin[a]")),
            ),
            ("subtract", ("symbol", "Cos[a]"), ("integer", "2")),
        ),
        ("integer", "3"),
    )


def test_frozen_labels_form_27_disjoint_half_turn_orbits() -> None:
    inventory = label_inventory()

    assert inventory.local == LOCAL_LABELS
    assert inventory.full == FULL_LABELS
    assert len(inventory.local) == 27
    assert len(inventory.full) == len(set(inventory.full)) == 54
    assert tuple(half_turn_label(label) for label in FULL_LABELS[:27]) == FULL_LABELS[27:]
    assert all(
        half_turn_label(label) != label and half_turn_label(half_turn_label(label)) == label
        for label in FULL_LABELS
    )


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ("x = 1.0", "unsupported formula character"),
        ("x = 2s", "trailing formula token"),
        ("x = s^2", "unsupported formula character"),
        ("x = f(1)", "undefined or forward"),
        ('x = "s"', "unsupported formula character"),
        ("x = s[0]", "unsupported formula character"),
        ("x = s.value", "unsupported formula character"),
        ("x = a", "undefined or forward"),
        ("x = later + 1", "undefined or forward"),
        ("x = 1 extra", "trailing formula token"),
        ("s = 1", "builtin cannot be assigned"),
        ("x = 1 / 0", "denominator is zero"),
        ("x = 1 / (s - s)", "denominator is zero"),
    ],
)
def test_closed_grammar_refuses_every_unfrozen_surface(payload: str, message: str) -> None:
    with pytest.raises(ContractError, match=message):
        parse_fixture(_comment(payload))


def test_identifiers_are_unique_and_backward_only() -> None:
    with pytest.raises(ContractError, match="duplicate assignment"):
        parse_fixture(_comment("x = 1") + _comment("x = 2"))

    with pytest.raises(ContractError, match="undefined or forward"):
        parse_fixture(_comment("x = y") + _comment("y = 1"))

    with pytest.raises(ContractError, match="denominator is zero"):
        parse_fixture(_comment("x = s - s") + _comment("y = 1 / x"))


def test_zero_classification_is_bounded_across_repeated_definitions() -> None:
    nonzero_payloads = (
        "x0 = 1",
        *(f"x{index} = x{index - 1} * x{index - 1}" for index in range(1, 36)),
        "y = 1 / x35",
    )
    content = b"".join(_comment(f"{payload} ") for payload in nonzero_payloads)

    assert len(nonzero_payloads) == 37
    assert len(content) == 1_031
    started = monotonic()
    parsed = parse_fixture(content)
    elapsed = monotonic() - started
    assert len(parsed.assignments) == 37
    assert elapsed < 1.0

    zero_payloads = (
        "z0 = s - s",
        *(f"z{index} = z{index - 1} * z{index - 1}" for index in range(1, 36)),
        "refused = 1 / z35",
    )
    with pytest.raises(ContractError, match="denominator is zero"):
        parse_fixture(b"".join(_comment(payload) for payload in zero_payloads))


@pytest.mark.parametrize(
    ("content", "message"),
    [
        (b"\xff", "valid UTF-8"),
        (_comment("x = 1") + b"\0", "NUL"),
        (b"<!--@n54 x = 1\r-->\n", "carriage return"),
        (b"<!DOCTYPE x>\n" + _comment("x = 1"), "DTD and entity"),
        (b"<!ENTITY x '1'>\n" + _comment("x = 1"), "DTD and entity"),
        (b"<!--@n54 x = <!--@n54 y = 1 -->", "nested comments"),
        (b"<!--@n54 x = 1", "unterminated"),
        ("<!--@n54 x = é -->\n".encode(), "non-ASCII"),
        (b"x = 1\n", "unmarked transport"),
        (b"<!-- x = 1 -->\n", "unmarked transport"),
        (_comment("x = 1") + b"garbage", "unmarked transport"),
    ],
)
def test_transport_refuses_unsafe_or_unconsumed_bytes(content: bytes, message: str) -> None:
    with pytest.raises(ContractError, match=message):
        parse_fixture(content)


def test_all_frozen_parser_caps_are_load_bearing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(ContractError, match="65,536-byte"):
        parse_fixture(b" " * (author.MAX_INPUT_BYTES + 1))

    with pytest.raises(ContractError, match="4,096-byte"):
        parse_fixture(b"<!--@n54 " + b"x" * (author.MAX_COMMENT_BYTES + 1) + b"-->")

    too_many_comments = b"".join(
        _comment(f"x{index} = {index}") for index in range(author.MAX_COMMENTS + 1)
    )
    with pytest.raises(ContractError, match="256-comment"):
        parse_fixture(too_many_comments)

    monkeypatch.setattr(author, "MAX_COMMENTS", author.MAX_ASSIGNMENTS + 1)
    with pytest.raises(ContractError, match="256-assignment"):
        parse_fixture(too_many_comments)

    too_many_tokens = "x = " + "+".join(
        "1" for _ in range(author.MAX_TOKENS_PER_FORMULA // 2 + 1)
    )
    with pytest.raises(ContractError, match="256-token"):
        parse_fixture(_comment(too_many_tokens))

    too_deep = (
        "(" * (author.MAX_EXPRESSION_DEPTH + 1) + "1" + ")" * (author.MAX_EXPRESSION_DEPTH + 1)
    )
    with pytest.raises(ContractError, match="expression-depth"):
        parse_fixture(_comment(f"x = {too_deep}"))

    with pytest.raises(ContractError, match="18-digit"):
        parse_fixture(_comment("x = " + "1" * (author.MAX_INTEGER_DIGITS + 1)))


def test_empty_transport_and_unknown_labels_refuse() -> None:
    with pytest.raises(ContractError, match="no marked assignments"):
        parse_fixture(b" \n\t")
    with pytest.raises(ContractError, match="unknown n = 54"):
        half_turn_label("B/not-a-label")


def test_parser_source_contains_no_forbidden_execution_or_xml_seam() -> None:
    source = Path("cases/n54_source_contract/contract.py").read_text(encoding="utf-8")
    forbidden = (
        "eval(",
        "exec(",
        "compile(",
        "parse_expr",
        "sympify",
        "xml.etree",
        "ElementTree",
        "assert ",
    )
    assert not [token for token in forbidden if token in source]


def test_quartic_arithmetic_reduces_and_inverts_every_tested_nonzero_element() -> None:
    assert FIELD_P * FIELD_P * FIELD_P * FIELD_P == FIELD_ONE + 2 * FIELD_P * FIELD_P

    elements = (
        FIELD_ONE,
        FIELD_P,
        FieldElement.from_values(1, 2, 3, 4),
        FieldElement.from_values(-7, 0, 5, 2),
    )
    for element in elements:
        assert element * element.inverse() == FIELD_ONE
        assert element.inverse() * element == FIELD_ONE
    with pytest.raises(ContractError, match="invert the zero"):
        FIELD_ZERO.inverse()


@pytest.mark.slow
def test_audited_receipt_binds_exact_field_builtins_and_digest() -> None:
    binding = bind_field_receipt()

    assert binding.receipt_sha256 == EXPECTED_FIELD_RECEIPT_SHA256
    assert binding.value("Sec[a]") * binding.value("Cos[a]") == FIELD_ONE
    assert binding.value("Sin[a]") / binding.value("Cos[a]") == binding.value("Tan[a]")
    assert (
        binding.value("Sin[a]") * binding.value("Sin[a]")
        + binding.value("Cos[a]") * binding.value("Cos[a]")
        == FIELD_ONE
    )


@pytest.mark.slow
def test_synthetic_fixture_evaluates_exactly_in_assignment_order() -> None:
    parsed = parse_fixture(FIXTURE.read_bytes())
    evaluated = evaluate_fixture(parsed)

    assert evaluated.field_receipt_sha256 == EXPECTED_FIELD_RECEIPT_SHA256
    assert tuple(item.name for item in evaluated.assignments) == tuple(
        item.name for item in parsed.assignments
    )
    values = {item.name: item.value for item in evaluated.assignments}
    assert values["stair_01"] - values["stair_00"] == FIELD_ONE
    assert values["rot_02"] == bind_field_receipt().value("Sec[a]") - FIELD_ONE


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        ("field-name", "field name"),
        ("field-polynomial", "field polynomial"),
        ("basis", "basis coefficients"),
        ("embedding", "positive embedding"),
        ("minimal-polynomial", "minimal polynomials"),
    ],
)
def test_field_receipt_semantic_drift_is_refused_before_digest(
    mutation: str, message: str
) -> None:
    receipt = cast(dict[str, Any], copy.deepcopy(derive_receipt()))
    if mutation == "field-name":
        receipt["field"]["name"] = "Q(q)"
    elif mutation == "field-polynomial":
        receipt["field"]["minimal_polynomial_coefficients"][-1] = 1
    elif mutation == "basis":
        receipt["basis_coefficients"]["side"][0] = "7"
    elif mutation == "embedding":
        receipt["field"]["embedding"] = "negative real root"
    else:
        receipt["minimal_polynomials"]["side"][-1] = 8896

    with pytest.raises(ContractError, match=message):
        bind_field_receipt(receipt)


@pytest.mark.slow
def test_field_receipt_digest_drift_is_refused() -> None:
    receipt = cast(dict[str, Any], copy.deepcopy(derive_receipt()))
    receipt["scope"] = "mutated unprojected scope"

    with pytest.raises(ContractError, match="SHA-256"):
        bind_field_receipt(receipt)


@pytest.mark.slow
def test_exact_evaluation_refuses_an_algebraically_zero_denominator() -> None:
    parsed = parse_fixture(
        _comment("zero = Sin[a] - Tan[a] * Cos[a]") + _comment("refused = 1 / zero")
    )

    with pytest.raises(ContractError, match="algebraically zero"):
        evaluate_fixture(parsed)


def _orientation() -> OrientationVector:
    return OrientationVector(
        FieldElement.from_values(Fraction(4, 5)),
        FieldElement.from_values(Fraction(3, 5)),
    )


def _synthetic_matching(
    action: D4Element,
    *,
    shared_first_tag: bool = False,
) -> tuple[
    tuple[SyntheticEndpoint, ...],
    tuple[SyntheticEndpoint, ...],
    tuple[CompatibilityEdge, ...],
]:
    tags = tuple(
        "shared-first-two" if shared_first_tag and index < 2 else f"tag-{index:02d}"
        for index in range(54)
    )
    sources = tuple(
        SyntheticEndpoint(label, tags[index]) for index, label in enumerate(FULL_LABELS)
    )
    rows = tuple(
        SyntheticEndpoint(row_id, tags[index]) for index, row_id in enumerate(WITNESS_ROW_IDS)
    )
    edges = tuple(
        CompatibilityEdge(action, label, WITNESS_ROW_IDS[index], tags[index], _orientation())
        for index, label in enumerate(FULL_LABELS)
    )
    return sources, rows, edges


def test_d4_replay_covers_the_frozen_group_action_and_laws() -> None:
    replay = replay_d4_contract()

    assert replay.elements == 8
    assert replay.products == replay.homomorphism_checks == 64
    assert replay.associativity_checks == 512
    assert tuple(element.name for element in D4_ORDER) == (
        "e",
        "r",
        "r2",
        "r3",
        "f",
        "rf",
        "r2f",
        "r3f",
    )
    assert D4Element(0, reflected=True).compose(D4Element(1, reflected=False)) == D4Element(
        3, reflected=True
    )
    assert D4Element(1, reflected=False).compose(D4Element(0, reflected=True)) == D4Element(
        1, reflected=True
    )


def test_orientation_is_quarter_turn_equivalent_and_reflection_negates_class() -> None:
    vector = _orientation()
    orientation = OrientationClass.from_vector(vector)

    assert all(
        OrientationClass.from_vector(vector.quarter_turn(turns)) == orientation
        for turns in range(4)
    )
    reflected = act_on_orientation(D4Element(0, reflected=True), orientation)
    expected = OrientationClass.from_vector(OrientationVector(vector.x, -vector.y))
    assert reflected == expected
    assert reflected != orientation
    assert act_on_orientation(D4Element(1, reflected=False), orientation) == orientation


def test_orientation_refuses_zero_and_nonunit_vectors() -> None:
    with pytest.raises(ContractError, match="vector is zero"):
        OrientationVector(FIELD_ZERO, FIELD_ZERO)
    with pytest.raises(ContractError, match="not exactly unit"):
        OrientationVector(FIELD_ONE, FIELD_ONE)


def test_first_unique_synthetic_correspondence_uses_opaque_rows_and_global_action() -> None:
    action = D4Element(2, reflected=False)
    sources, rows, edges = _synthetic_matching(action)

    selected = select_synthetic_correspondence(sources, rows, edges, declared_action=action)

    assert selected.action == action
    assert selected.witness_sha256 == WITNESS_SHA256
    assert len(selected.pairs) == 54
    assert tuple(pair.source_label for pair in selected.pairs) == FULL_LABELS
    assert tuple(pair.row_id for pair in selected.pairs) == WITNESS_ROW_IDS
    expected_orientation = act_on_orientation(
        action, OrientationClass.from_vector(_orientation())
    )
    assert all(pair.orientation == expected_orientation for pair in selected.pairs)


def test_synthetic_correspondence_refuses_no_or_second_perfect_match() -> None:
    action = D4Element(2, reflected=False)
    sources, rows, edges = _synthetic_matching(action, shared_first_tag=True)
    with pytest.raises(ContractError, match="no synthetic perfect matching"):
        select_synthetic_correspondence(sources, rows, edges[:-1])

    alternatives = (
        CompatibilityEdge(
            action, FULL_LABELS[0], WITNESS_ROW_IDS[1], "shared-first-two", _orientation()
        ),
        CompatibilityEdge(
            action, FULL_LABELS[1], WITNESS_ROW_IDS[0], "shared-first-two", _orientation()
        ),
    )
    with pytest.raises(ContractError, match="second perfect matching"):
        select_synthetic_correspondence(sources, rows, edges + alternatives)


def test_synthetic_correspondence_refuses_nonminimal_declared_action() -> None:
    sources, rows, identity_edges = _synthetic_matching(D4_IDENTITY)
    _, _, later_edges = _synthetic_matching(D4Element(2, reflected=False))

    with pytest.raises(ContractError, match="not the first unique"):
        select_synthetic_correspondence(
            sources,
            rows,
            identity_edges + later_edges,
            declared_action=D4Element(2, reflected=False),
        )


def test_synthetic_correspondence_refuses_endpoint_and_structural_drift() -> None:
    action = D4Element(2, reflected=False)
    sources, rows, edges = _synthetic_matching(action)

    with pytest.raises(ContractError, match="duplicate synthetic source"):
        select_synthetic_correspondence((*sources[:-1], sources[0]), rows, edges)
    with pytest.raises(ContractError, match="missing or unexpected synthetic row"):
        select_synthetic_correspondence(sources, rows[:-1], edges)
    with pytest.raises(ContractError, match="structural-tag drift"):
        select_synthetic_correspondence(
            sources,
            rows,
            (replace(edges[0], structural_tag="drift"), *edges[1:]),
        )
    with pytest.raises(ContractError, match="duplicate synthetic compatibility edge"):
        select_synthetic_correspondence(sources, rows, (*edges, edges[0]))


@pytest.mark.slow
def test_n54_result_has_the_exact_frozen_profile_and_mutation_receipts() -> None:
    fixture_content = FIXTURE.read_bytes()
    result = build_n54_result(fixture_content)

    assert result.keys() == {
        "schema",
        "scope",
        "fixture_sha256",
        "field_receipt_sha256",
        "witness_sha256",
        "d4",
        "assignments",
        "correspondence",
        "mutations",
        "claim_boundary",
    }
    assert result["fixture_sha256"] == EXPECTED_FIXTURE_SHA256
    assert result["field_receipt_sha256"] == EXPECTED_FIELD_RECEIPT_SHA256
    assert result["witness_sha256"] == WITNESS_SHA256
    assert result["d4"] == {
        "action": "r2",
        "elements": 8,
        "products": 64,
        "associativity_checks": 512,
        "homomorphism_checks": 64,
    }
    assignments = cast(list[dict[str, Any]], result["assignments"])
    assert len(assignments) == 27
    assert [item["name"] for item in assignments] == [
        label.replace("/", "_") for label in LOCAL_LABELS
    ]
    assert all(
        len(item["coefficients"]) == 4
        and all(isinstance(coefficient, str) for coefficient in item["coefficients"])
        for item in assignments
    )
    correspondence = cast(list[dict[str, Any]], result["correspondence"])
    assert len(correspondence) == 54
    assert [item["source_label"] for item in correspondence] == list(FULL_LABELS)
    assert [item["row_id"] for item in correspondence] == list(WITNESS_ROW_IDS)
    assert [item["structural_tag"] for item in correspondence] == [
        f"tag-{index:02d}" for index in range(54)
    ]
    assert all(
        item["orientation"] == {"x": ["-4/5", "0", "0", "0"], "y": ["-3/5", "0", "0", "0"]}
        for item in correspondence
    )
    assert result["mutations"] == {
        "missing_structural_inventory": {
            "rejected": True,
            "reason": "missing or unexpected synthetic source endpoint",
        },
        "correspondence_swap": {
            "rejected": True,
            "reason": "synthetic structural-tag drift",
        },
    }


@pytest.mark.parametrize(
    "content",
    [
        b'{"outer":{"key":1,"key":2}}\n',
        b'{"value":1.5}\n',
        b'{"value":1e2}\n',
        b'{"value":NaN}\n',
        b'{"value":Infinity}\n',
        b'{"b":1,"a":2}\n',
        b'{"a":1}\n\n',
    ],
)
def test_canonical_json_loader_refuses_duplicate_float_and_noncanonical_bytes(
    content: bytes,
) -> None:
    with pytest.raises(ContractError):
        load_canonical_json(content)


@pytest.mark.slow
def test_canonical_json_round_trip_and_float_refusal() -> None:
    content = build_n54_result_bytes(FIXTURE.read_bytes())

    assert content.endswith(b"\n")
    assert not content.endswith(b"\n\n")
    assert canonical_json_bytes(load_canonical_json(content)) == content
    with pytest.raises(ContractError, match="floating"):
        canonical_json_bytes({"value": 1.0})


@pytest.mark.slow
def test_author_cli_is_stdout_only_and_identical_under_optimization() -> None:
    expected = build_n54_result_bytes(FIXTURE.read_bytes())
    outputs: list[bytes] = []
    for flags in ((), ("-O",)):
        completed = subprocess.run(
            (
                sys.executable,
                *flags,
                "-m",
                "cases.n54_source_contract.run",
                "--selftest",
            ),
            check=True,
            capture_output=True,
        )
        assert completed.stderr == b""
        outputs.append(completed.stdout)

    assert outputs == [expected, expected]
