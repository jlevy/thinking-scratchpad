#!/usr/bin/env python3
"""Replay and mutation controls for the abstract size-five scaffold atlas."""

from __future__ import annotations

import json
import sys
from copy import deepcopy
from pathlib import Path

import pytest

from devtools.build_contact_scaffold_atlas import (
    OUTPUT,
    RENDERING,
    atlas_errors,
    expected_outputs,
    identity_record,
    iter_atlas_scaffolds,
    main,
    scaffold_by_identity,
    schema_errors,
)

ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.slow
def test_contact_scaffold_atlas_and_house_overview_replay_byte_for_byte() -> None:
    expected, rendering = expected_outputs()
    retained = json.loads(OUTPUT.read_text(encoding="utf-8"))

    assert retained == expected
    assert RENDERING.read_text(encoding="utf-8") == rendering
    atlas = retained["atlas"]
    assert atlas["counts"] == {
        "orbit_action_images": 1_705_312,
        "orbit_count": 11_013,
        "topology_coloring_candidates": 1_533_696,
        "topology_count": 21,
    }
    assert [topology["orbit_count"] for topology in atlas["topologies"]] == [
        8,
        24,
        24,
        50,
        76,
        72,
        76,
        22,
        288,
        89,
        272,
        288,
        73,
        237,
        366,
        1_072,
        560,
        2_144,
        1_156,
        2_893,
        1_223,
    ]
    assert "ABSTRACT · NO GEOMETRY" in rendering
    assert "not realized square packings" in rendering
    assert "No square positions" in rendering
    assert "abstract-diagram-layout; svg-y-down; no-packing-coordinates" in rendering
    assert "mathematical-y-up" not in rendering
    assert atlas["rendering"] == {
        "path": "atlas/enumerated/rendering/contact-scaffolds-size5-overview.svg",
        "semantics": "abstract-topology-count-overview-not-packing-geometry",
    }

    decoded = list(iter_atlas_scaffolds(atlas))
    assert len(decoded) == 11_013
    assert len({identity for identity, _scaffold in decoded}) == 11_013
    assert decoded[0][0] == "T5-01/0000"
    assert decoded[-1][0] == "T5-21/0123230121"


@pytest.mark.slow
def test_contact_scaffold_atlas_cross_field_mutations_fail() -> None:
    atlas = expected_outputs()[0]["atlas"]
    mutations = []

    duplicate = deepcopy(atlas)
    duplicate["topologies"][0]["representatives"][1] = duplicate["topologies"][0][
        "representatives"
    ][0]
    mutations.append(duplicate)

    wrong_width = deepcopy(atlas)
    wrong_width["topologies"][0]["representatives"][0] += "0"
    mutations.append(wrong_width)

    wrong_total = deepcopy(atlas)
    wrong_total["counts"]["orbit_count"] -= 1
    mutations.append(wrong_total)

    reordered = deepcopy(atlas)
    reordered["topologies"][0], reordered["topologies"][1] = (
        reordered["topologies"][1],
        reordered["topologies"][0],
    )
    mutations.append(reordered)

    for mutation in mutations:
        assert atlas_errors(mutation)

    geometry_channel = deepcopy(atlas)
    geometry_channel["coordinates"] = [[0, 0]]
    assert schema_errors(geometry_channel)

    invalid_digit = deepcopy(atlas)
    invalid_digit["topologies"][0]["representatives"][0] = "x000"
    assert schema_errors(invalid_digit)


def test_contact_scaffold_atlas_contains_no_geometry_or_hypothesis_channel() -> None:
    """The retained atlas carries no geometry channel and claims no packing verdict.

    Read from the committed file rather than enumerated. `expected_outputs()` is not
    memoized, so every caller re-runs the size-five isomorph-free enumeration -- 6.04s on
    CI's two-core runner (run for `c1120c44`, job 101371257966), over the pull-request
    surface's per-test ceiling, for a question about what the retained JSON contains.
    Marking it `slow` would be the `BC-218` mistake in a third file: the cost is the
    build's, not this test's, and in the deep surface it is paid by a neighbour first.

    `test_contact_scaffold_atlas_and_house_overview_replay_byte_for_byte` is the pin --
    it asserts the retained document and rendering replay the enumeration exactly -- and
    the full gate's `abstract size-five contact-scaffold atlas` step asserts it again
    through `build_contact_scaffold_atlas --check`.
    """
    atlas = json.loads(OUTPUT.read_text(encoding="utf-8"))["atlas"]
    assert atlas["claim_status"] == (
        "abstract-contact-scaffolds-no-geometry-no-packing-verdict"
    )
    serialized = json.dumps(atlas, sort_keys=True)
    for forbidden in (
        '"coordinates"',
        '"packing"',
        '"witness"',
        '"hypothesis"',
        '"contact_annotation"',
        '"chunk_annotation"',
    ):
        assert forbidden not in serialized
    assert (ROOT / atlas["rendering"]["path"]) == RENDERING


@pytest.mark.slow
def test_contact_scaffold_atlas_supports_direct_stable_identity_lookup() -> None:
    atlas = expected_outputs()[0]["atlas"]

    first = scaffold_by_identity(atlas, "T5-01/0000")
    last = scaffold_by_identity(atlas, "T5-21/0123230121")
    assert len(first.vertex_colors) == len(last.vertex_colors) == 5
    assert [(edge.normal, edge.sign) for edge in first.edges] == [("u", -1)] * 4
    assert len(last.edges) == 10

    for invalid in (
        "",
        "T5-01",
        "T5-01/0000/extra",
        "T5-99/0000",
        "T5-01/3333",
        "T5-01/xxxx",
    ):
        with pytest.raises(ValueError, match=r"identity|topology|representative"):
            scaffold_by_identity(atlas, invalid)


@pytest.mark.slow
def test_contact_scaffold_show_is_read_only_and_explicitly_abstract(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    before = OUTPUT.read_bytes()
    monkeypatch.setattr(sys, "argv", ["build_contact_scaffold_atlas", "--show", "T5-01/0000"])

    assert main() == 0

    assert OUTPUT.read_bytes() == before
    record = json.loads(capsys.readouterr().out)
    assert record == identity_record(expected_outputs()[0]["atlas"], "T5-01/0000")
    assert record["claim_status"] == (
        "abstract-only-no-geometry-no-feasibility-no-packing-verdict"
    )
    assert record["abstract_scaffold"]["vertex_count"] == 5
    assert len(record["abstract_scaffold"]["contact_edges"]) == 4
    serialized = json.dumps(record, sort_keys=True)
    for forbidden in ('"coordinates"', '"square_positions"', '"packing"', '"hypothesis"'):
        assert forbidden not in serialized
