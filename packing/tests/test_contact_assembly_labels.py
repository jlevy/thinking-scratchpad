#!/usr/bin/env python3
"""Exhaustive small-graph controls for contact-scaffold canonicalization."""

from __future__ import annotations

import math
from collections.abc import Iterator
from itertools import combinations, islice, permutations

import pytest

from sqpack.contact_assembly import (
    D4_TRANSFORMS,
    Axis,
    CanonicalizationLimit,
    CanonicalScaffold,
    ContactEdge,
    ContactScaffold,
    OrbitWitness,
    ScaffoldError,
    ScaffoldLimits,
    canonicalize_scaffold,
    connected_topology_representatives,
    enumerate_canonical_scaffolds,
    enumerate_isomorph_free_scaffolds,
    replay_orbit_witness,
    scaffold_label,
    scaffold_orbit,
    transform_scaffold,
)


def _connected_graphs(size: int) -> Iterator[ContactScaffold]:
    pairs = tuple(combinations(range(size), 2))
    for mask in range(1 << len(pairs)):
        edges = tuple(
            ContactEdge(left, right, "u", 1)
            for bit, (left, right) in enumerate(pairs)
            if mask & (1 << bit)
        )
        try:
            yield ContactScaffold(
                ("angle-a",) * size,
                edges,
                ((),) * size,
            )
        except ScaffoldError:
            continue


def _signed_uniform_scaffolds(size: int) -> Iterator[ContactScaffold]:
    pairs = tuple(combinations(range(size), 2))
    colors: tuple[tuple[Axis, int], ...] = (
        ("u", 1),
        ("u", -1),
        ("v", 1),
        ("v", -1),
    )
    for encoded in range(5 ** len(pairs)):
        remainder = encoded
        edges = []
        for left, right in pairs:
            state = remainder % 5
            remainder //= 5
            if state:
                normal, sign = colors[state - 1]
                edges.append(ContactEdge(left, right, normal, sign))
        try:
            yield ContactScaffold(("angle-a",) * size, tuple(edges), ((),) * size)
        except ScaffoldError:
            continue


def _legacy_canonicalization(
    scaffold: ContactScaffold,
) -> tuple[str, ContactScaffold, OrbitWitness, int, int]:
    best: tuple[str, ContactScaffold, OrbitWitness] | None = None
    labels: set[str] = set()
    examined = 0
    for witness, image in scaffold_orbit(scaffold):
        examined += 1
        label = scaffold_label(image)
        labels.add(label)
        if best is None or label < best[0]:
            best = label, image, witness
    assert best is not None
    return best[0], best[1], best[2], examined, len(labels)


def _topology_label(scaffold: ContactScaffold) -> tuple[tuple[int, int], ...]:
    """Independent ordinary-graph quotient used as a coarser differential oracle."""
    size = len(scaffold.vertex_colors)

    def mapped_pair(edge: ContactEdge, old_to_new: tuple[int, ...]) -> tuple[int, int]:
        left = old_to_new[edge.left]
        right = old_to_new[edge.right]
        return (left, right) if left < right else (right, left)

    return min(
        tuple(sorted(mapped_pair(edge, old_to_new) for edge in scaffold.edges))
        for old_to_new in permutations(range(size))
    )


def _rich_scaffold() -> ContactScaffold:
    return ContactScaffold(
        ("angle-a", "angle-a", "angle-b", "angle-b", "angle-c"),
        (
            ContactEdge(0, 1, "u", 1),
            ContactEdge(1, 2, "v", -1),
            ContactEdge(2, 3, "u", -1),
            ContactEdge(3, 4, "v", 1),
            ContactEdge(0, 4, "u", -1),
        ),
        (("left", "bottom"), (), ("top",), ("right",), ("bottom",)),
    )


def test_exhaustive_connected_graph_quotient_through_five_vertices() -> None:
    labeled_counts = []
    topology_counts = []
    contact_orbit_counts = []
    for size in range(1, 6):
        topology_labels = set()
        contact_to_topology: dict[str, tuple[tuple[int, int], ...]] = {}
        labeled = 0
        for scaffold in _connected_graphs(size):
            result = canonicalize_scaffold(scaffold)
            assert isinstance(result, CanonicalScaffold)
            topology = _topology_label(scaffold)
            topology_labels.add(topology)
            assert contact_to_topology.setdefault(result.canonical_label, topology) == topology
            labeled += 1
        labeled_counts.append(labeled)
        topology_counts.append(len(topology_labels))
        contact_orbit_counts.append(len(contact_to_topology))

    assert labeled_counts == [1, 1, 4, 38, 728]
    assert topology_counts == [1, 1, 2, 6, 21]
    # Signed normal directions deliberately refine the ordinary topology quotient.
    assert contact_orbit_counts == [1, 1, 3, 16, 149]


def test_isomorph_free_uniform_slice_has_exact_small_counts_and_typed_caps() -> None:
    batches = [
        enumerate_isomorph_free_scaffolds(
            size,
            maximum_colorings=2_000_000,
            maximum_emitted_scaffolds=100_000,
        )
        for size in range(1, 6)
    ]

    assert [batch.status for batch in batches] == ["completed"] * 5
    assert [batch.topology_count for batch in batches] == [1, 1, 2, 6, 21]
    assert [batch.required_colorings for batch in batches] == [1, 4, 80, 5_760, 1_533_696]
    assert [len(batch.scaffolds) for batch in batches] == [1, 1, 7, 124, 11_013]
    assert [len(connected_topology_representatives(size)) for size in range(1, 6)] == [
        1,
        1,
        2,
        6,
        21,
    ]

    coloring_limited = enumerate_isomorph_free_scaffolds(
        5,
        maximum_colorings=1_533_695,
        maximum_emitted_scaffolds=100_000,
    )
    assert coloring_limited.status == "limit"
    assert coloring_limited.limit_kind == "coloring-space-cap"
    assert coloring_limited.examined_colorings == 0
    assert coloring_limited.scaffolds == ()

    emission_limited = enumerate_isomorph_free_scaffolds(
        3,
        maximum_colorings=80,
        maximum_emitted_scaffolds=1,
    )
    assert emission_limited.status == "limit"
    assert emission_limited.limit_kind == "emitted-scaffold-cap"
    assert len(emission_limited.scaffolds) == 1

    for malformed in (0, True):
        with pytest.raises(ScaffoldError, match="positive integers"):
            enumerate_isomorph_free_scaffolds(
                3,
                maximum_colorings=malformed,
                maximum_emitted_scaffolds=10,
            )


@pytest.mark.slow
def test_every_rich_d4_and_relabeling_image_has_one_label() -> None:
    source = _rich_scaffold()
    expected = canonicalize_scaffold(source)
    assert isinstance(expected, CanonicalScaffold)
    assert replay_orbit_witness(source, expected.witness) == expected.scaffold
    assert scaffold_label(expected.scaffold) == expected.canonical_label

    for _witness, image in scaffold_orbit(source):
        replay = canonicalize_scaffold(image)
        assert isinstance(replay, CanonicalScaffold)
        assert replay.canonical_label == expected.canonical_label


def test_uniform_wall_free_fast_path_matches_the_full_orbit_oracle() -> None:
    sources = [scaffold for size in range(1, 4) for scaffold in _signed_uniform_scaffolds(size)]
    for size in range(1, 5):
        batch = enumerate_isomorph_free_scaffolds(
            size,
            maximum_colorings=2_000_000,
            maximum_emitted_scaffolds=100_000,
        )
        assert batch.status == "completed"
        sources.extend(batch.scaffolds)
    assert len(sources) == 250

    compared = 0
    for source in sources:
        reverse = tuple(reversed(range(len(source.vertex_colors))))
        transformed = transform_scaffold(
            source,
            symmetry=D4_TRANSFORMS[1],
            old_to_new=reverse,
        )
        for candidate in (source, transformed):
            expected = _legacy_canonicalization(candidate)
            actual = canonicalize_scaffold(candidate)
            assert isinstance(actual, CanonicalScaffold)
            assert (
                actual.canonical_label,
                actual.scaffold,
                actual.witness,
                actual.raw_image_count,
                actual.unique_image_count,
            ) == expected
            assert replay_orbit_witness(candidate, actual.witness) == actual.scaffold
            compared += 1
    assert compared == 500


def test_uniform_wall_free_partial_orbit_keeps_the_typed_legacy_boundary() -> None:
    batch = enumerate_isomorph_free_scaffolds(
        4,
        maximum_colorings=5_760,
        maximum_emitted_scaffolds=124,
    )
    source = batch.scaffolds[-1]
    required = len(D4_TRANSFORMS) * math.factorial(4)
    partial_labels = [
        scaffold_label(image)
        for _witness, image in islice(scaffold_orbit(source), required - 1)
    ]

    limited = canonicalize_scaffold(source, maximum_orbit_images=required - 1)
    assert isinstance(limited, CanonicalizationLimit)
    assert limited.required_images == required
    assert limited.examined_images == required - 1
    assert limited.partial_best_label == min(partial_labels)

    complete = canonicalize_scaffold(source, maximum_orbit_images=required)
    assert isinstance(complete, CanonicalScaffold)


def test_d4_and_relabeling_actions_compose_independently() -> None:
    source = _rich_scaffold()
    identity = tuple(range(5))
    by_matrix = {(item.xx, item.xy, item.yx, item.yy): item for item in D4_TRANSFORMS}
    first_permutation = (2, 4, 1, 0, 3)
    second_permutation = (4, 2, 0, 3, 1)
    composed_permutation = tuple(second_permutation[first_permutation[old]] for old in range(5))

    for first in D4_TRANSFORMS:
        for second in D4_TRANSFORMS:
            matrix = (
                second.xx * first.xx + second.xy * first.yx,
                second.xx * first.xy + second.xy * first.yy,
                second.yx * first.xx + second.yy * first.yx,
                second.yx * first.xy + second.yy * first.yy,
            )
            composed = by_matrix[matrix]
            sequential = transform_scaffold(
                transform_scaffold(
                    source,
                    symmetry=first,
                    old_to_new=first_permutation,
                ),
                symmetry=second,
                old_to_new=second_permutation,
            )
            direct = transform_scaffold(
                source,
                symmetry=composed,
                old_to_new=composed_permutation,
            )
            assert sequential == direct
            assert (
                transform_scaffold(source, symmetry=composed, old_to_new=identity).wall_contacts
                == transform_scaffold(
                    transform_scaffold(source, symmetry=first, old_to_new=identity),
                    symmetry=second,
                    old_to_new=identity,
                ).wall_contacts
            )


def test_endpoint_normalization_colors_and_malformed_inputs_are_explicit() -> None:
    normalized = ContactScaffold(
        ("angle-a", "angle-a"),
        (ContactEdge(1, 0, "u", -1),),
        (("left",), ("right",)),
    )
    assert normalized.edges == (ContactEdge(0, 1, "u", 1),)

    source = _rich_scaffold()
    changed_color = ContactScaffold(
        (*source.vertex_colors[:-1], "angle-d"), source.edges, source.wall_contacts
    )
    source_result = canonicalize_scaffold(source)
    changed_result = canonicalize_scaffold(changed_color)
    assert isinstance(source_result, CanonicalScaffold)
    assert isinstance(changed_result, CanonicalScaffold)
    assert source_result.canonical_label != changed_result.canonical_label

    with pytest.raises(ScaffoldError, match="connected"):
        ContactScaffold(("a", "a"), (), ((), ()))
    with pytest.raises(ScaffoldError, match="more than one"):
        ContactScaffold(
            ("a", "a"),
            (ContactEdge(0, 1, "u", 1), ContactEdge(1, 0, "v", 1)),
            ((), ()),
        )
    with pytest.raises(ScaffoldError, match="unique"):
        ContactScaffold(("a",), (), (("left", "left"),))
    with pytest.raises(ScaffoldError, match="permutation"):
        transform_scaffold(source, symmetry=D4_TRANSFORMS[0], old_to_new=(0, 0, 1, 2, 3))
    with pytest.raises(ScaffoldError, match="unknown D4"):
        replay_orbit_witness(source, OrbitWitness("not-a-symmetry", tuple(range(5))))


def test_orbit_and_stream_caps_return_typed_partial_coverage() -> None:
    source = _rich_scaffold()
    limited = canonicalize_scaffold(source, maximum_orbit_images=7)
    assert isinstance(limited, CanonicalizationLimit)
    assert limited.kind == "orbit-image-cap"
    assert limited.examined_images == 7
    assert limited.required_images == 960

    transformed = next(iter(scaffold_orbit(source)))[1]
    complete = enumerate_canonical_scaffolds(
        (source, transformed),
        limits=ScaffoldLimits(maximum_candidates=2, maximum_emitted_labels=2),
    )
    assert complete.status == "completed"
    assert len(complete.canonical_labels) == 1
    assert complete.duplicate_candidates == 1

    candidate_limited = enumerate_canonical_scaffolds(
        (source, transformed),
        limits=ScaffoldLimits(maximum_candidates=1, maximum_emitted_labels=2),
    )
    assert candidate_limited.status == "limit"
    assert candidate_limited.limit_kind == "candidate-cap"
    assert candidate_limited.examined_candidates == 1
    assert candidate_limited.encountered_candidates == 2

    orbit_limited = enumerate_canonical_scaffolds(
        (source,),
        limits=ScaffoldLimits(
            maximum_candidates=1,
            maximum_emitted_labels=1,
            maximum_orbit_images=7,
        ),
    )
    assert orbit_limited.status == "limit"
    assert orbit_limited.limit_kind == "orbit-image-cap"


def test_emitted_label_cap_does_not_silently_drop_a_new_orbit() -> None:
    source = _rich_scaffold()
    distinct = ContactScaffold(
        ("angle-a",) * 5,
        (
            ContactEdge(0, 1, "u", 1),
            ContactEdge(1, 2, "u", 1),
            ContactEdge(2, 3, "u", 1),
            ContactEdge(3, 4, "u", 1),
        ),
        ((),) * 5,
    )

    result = enumerate_canonical_scaffolds(
        (source, distinct),
        limits=ScaffoldLimits(maximum_candidates=2, maximum_emitted_labels=1),
    )

    assert result.status == "limit"
    assert result.limit_kind == "emitted-label-cap"
    assert result.examined_candidates == 2
    assert len(result.canonical_labels) == 1
