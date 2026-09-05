"""The near-tight census counts what the sweep decided on, and counts it by hand.

Two anchors. The synthetic certificate below is built so that every event cell holds
exactly one atom and the whole census -- counts, components and boxes at all four
margins -- can be written out by hand before the tool runs. The second anchor is
direction 0 of the retained n = 11 rung, where the census's own minimum must be the
`least_cell_mass` the certificate declares and its reachable-cell count must be the
one the independently retained `reduce_to_cells` reference lists.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest

from devtools.census_tight_cells import (
    DEFAULT_MARGINS,
    census,
    census_direction,
    components,
    main,
    report,
    scaled_threshold,
)
from devtools.decide_certificate import load
from sqpack.fractional.certificate import Certificate
from sqpack.fractional.model import Atom
from sqpack.fractional.sweep import reduce_to_cells, weight_scale

RETAINED = (
    Path(__file__).resolve().parents[1] / "cases/n11_fractional_certificate/certificate.json"
)

# One atom per event cell, on a 3-by-3 grid of unit cells inside a side-4 container with
# B = 1. At direction 0 the centre domain is [1/2, 7/2]^2 and the event coordinates are
# exactly (1/2, 3/2, 5/2, 7/2) on both axes, so cell (i, j) covers the atom at
# (i + 1, j + 1) and nothing else, and its mass is that atom's weight.
SYNTHETIC_WEIGHTS: tuple[tuple[Fraction, ...], ...] = (
    (Fraction(1), Fraction(101, 100), Fraction(3, 2)),
    (Fraction(3, 2), Fraction(21, 20), Fraction(3, 2)),
    (Fraction(3, 2), Fraction(3, 2), Fraction(11, 10)),
)
# The hand census of the grid above, in the order of DEFAULT_MARGINS.
HAND_COUNTS = (1, 2, 3, 4)
HAND_COMPONENTS = (1, 1, 1, 2)
HAND_LARGEST = (1, 2, 3, 3)
HAND_BOXES = (
    (Fraction(1, 2), Fraction(3, 2), Fraction(1, 2), Fraction(3, 2)),
    (Fraction(1, 2), Fraction(3, 2), Fraction(1, 2), Fraction(5, 2)),
    (Fraction(1, 2), Fraction(5, 2), Fraction(1, 2), Fraction(5, 2)),
    (Fraction(1, 2), Fraction(7, 2), Fraction(1, 2), Fraction(7, 2)),
)


def synthetic_atoms() -> tuple[Atom, ...]:
    return tuple(
        Atom(f"{i}{j}", Fraction(i + 1), Fraction(j + 1), weight)
        for i, row in enumerate(SYNTHETIC_WEIGHTS)
        for j, weight in enumerate(row)
    )


def synthetic_certificate() -> Certificate:
    return Certificate(
        n=12,
        outer_side=Fraction(4),
        square_side=Fraction(1),
        atoms=synthetic_atoms(),
        half_tangents=(Fraction(0), Fraction(1, 10)),
    )


def synthetic_record() -> dict[str, object]:
    """The same object in the on-disk shape `decide_certificate.load` reads."""

    certificate = synthetic_certificate()
    return {
        "id": "C-synthetic-census",
        "n": certificate.n,
        "claim": "s(12) >= 4",
        "outer_side": str(certificate.outer_side),
        "square_side": str(certificate.square_side),
        "angle_limit": "1/10",
        "direction_steps": 1,
        "total_mass": str(certificate.total_mass),
        "least_cell_mass": "1",
        "symmetry": "none",
        "atoms": [[str(atom.x), str(atom.y), str(atom.weight)] for atom in certificate.atoms],
    }


def test_the_threshold_is_the_floor_of_the_scaled_band() -> None:
    assert scaled_threshold(Fraction(0), 100) == 100
    assert scaled_threshold(Fraction(1, 100), 100) == 101
    assert scaled_threshold(Fraction(1, 20), 100) == 105
    assert scaled_threshold(Fraction(1, 10), 100) == 110
    # A margin whose denominator does not divide the scale still decides in integers:
    # a cell of scaled mass 100 * (1 + 1/3) is not an integer, so the floor is exact.
    assert scaled_threshold(Fraction(1, 3), 100) == 133
    with pytest.raises(ValueError, match="nonnegative"):
        scaled_threshold(Fraction(-1, 100), 100)


def test_the_synthetic_census_is_the_one_computed_by_hand() -> None:
    certificate = synthetic_certificate()
    reading = census_direction(
        certificate.atoms,
        certificate.directions[0],
        certificate.outer_side,
        certificate.square_side,
        weight_scale(certificate.atoms),
        margins=DEFAULT_MARGINS,
        index=0,
        half_tangent=Fraction(0),
    )

    assert weight_scale(certificate.atoms) == 100
    assert reading.reachable_cells == 9
    assert reading.columns == 3
    assert reading.minimum_mass == Fraction(1)
    assert tuple(margin.margin for margin in reading.margins) == DEFAULT_MARGINS
    assert tuple(margin.tight_cells for margin in reading.margins) == HAND_COUNTS
    assert tuple(margin.components for margin in reading.margins) == HAND_COMPONENTS
    assert tuple(margin.largest_component for margin in reading.margins) == HAND_LARGEST
    for margin, expected in zip(reading.margins, HAND_BOXES, strict=True):
        assert margin.box is not None
        box = (margin.box.u_low, margin.box.u_high, margin.box.v_low, margin.box.v_high)
        assert box == expected
    # The nine unit cells tile the centre domain exactly, so the tight area is the
    # tight cell count and the reachable area is nine.
    domain = reading.domain_box
    assert (domain.u_low, domain.u_high) == (Fraction(1, 2), Fraction(7, 2))
    assert (domain.v_low, domain.v_high) == (Fraction(1, 2), Fraction(7, 2))
    assert reading.approx_reachable_area == pytest.approx(9.0)
    assert reading.margins[3].approx_tight_area == pytest.approx(4.0)


def test_a_margin_below_the_least_cell_mass_finds_nothing() -> None:
    certificate = synthetic_certificate()
    reading = census_direction(
        certificate.atoms,
        certificate.directions[0],
        certificate.outer_side,
        certificate.square_side,
        weight_scale(certificate.atoms),
        margins=(Fraction(0),),
        index=0,
        half_tangent=Fraction(0),
    )
    # The synthetic grid's floor is exactly one, so margin zero holds one cell. Shift
    # every weight up by a hundredth and the same margin holds none, with no box.
    heavier = tuple(
        Atom(atom.label, atom.x, atom.y, atom.weight + Fraction(1, 100))
        for atom in certificate.atoms
    )
    empty = census_direction(
        heavier,
        certificate.directions[0],
        certificate.outer_side,
        certificate.square_side,
        weight_scale(heavier),
        margins=(Fraction(0),),
        index=0,
        half_tangent=Fraction(0),
    )
    assert reading.margins[0].tight_cells == 1
    assert empty.margins[0].tight_cells == 0
    assert empty.margins[0].components == 0
    assert empty.margins[0].box is None
    assert empty.minimum_mass == Fraction(101, 100)


def test_components_join_across_an_edge_and_not_across_a_corner() -> None:
    def cells(pairs: list[tuple[int, int]]) -> tuple[np.ndarray, np.ndarray]:
        ordered = sorted(pairs)
        return (
            np.array([i for i, _ in ordered], dtype=np.intp),
            np.array([j for _, j in ordered], dtype=np.intp),
        )

    assert components(*cells([(0, 0), (0, 1), (0, 2)])) == (1, 3)
    assert components(*cells([(0, 0), (1, 0)])) == (1, 2)
    assert components(*cells([(0, 0), (1, 1)])) == (2, 1)
    assert components(*cells([(0, 0), (2, 0)])) == (2, 1)
    # A ring closes into one component through both of its arms.
    ring = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)]
    assert components(*cells(ring)) == (1, 8)


def test_the_whole_net_is_censused_direction_by_direction() -> None:
    certificate = synthetic_certificate()
    seen: list[int] = []
    readings = census(certificate, DEFAULT_MARGINS, on_direction=lambda r: seen.append(r.index))

    assert seen == [0, 1]
    assert [reading.index for reading in readings] == [0, 1]
    assert [reading.half_tangent for reading in readings] == [Fraction(0), Fraction(1, 10)]
    assert readings[0].margins[0].tight_cells == HAND_COUNTS[0]
    with pytest.raises(ValueError, match="outside the net"):
        _ = census(certificate, DEFAULT_MARGINS, indices=[2])


def test_the_report_carries_the_census_margin_reading_and_round_trips(tmp_path: Path) -> None:
    path = tmp_path / "synthetic.json"
    path.write_text(json.dumps(synthetic_record(), indent=1) + "\n")
    certificate, record = load(path)
    readings = census(certificate, DEFAULT_MARGINS, indices=[0])
    payload = report(
        path,
        certificate,
        record,
        digest="0" * 64,
        margins=DEFAULT_MARGINS,
        readings=readings,
        complete=True,
    )
    restored = json.loads(json.dumps(payload))

    # The one thing this record must not let a reader invert: epsilon is a band above
    # the Condition 5 floor, not the mass gap M - n.
    assert "census margin" in restored["margin_semantics"]
    assert "not the mass gap" in restored["margin_semantics"]
    assert restored["declared_least_cell_mass"] == "1"
    assert restored["totals"]["matches_declared_least_cell_mass"] is True
    assert restored["totals"]["reachable_cells"] == 9
    assert [block["tight_cells"] for block in restored["totals"]["by_margin"]] == list(
        HAND_COUNTS
    )
    assert restored["totals"]["by_margin"][3]["fraction_of_reachable"] == "4/9"


def test_the_command_writes_a_report_for_the_directions_it_was_given(tmp_path: Path) -> None:
    path = tmp_path / "synthetic.json"
    path.write_text(json.dumps(synthetic_record(), indent=1) + "\n")
    output = tmp_path / "nested" / "census.json"

    code = main([str(path), "--output", str(output), "--directions", "0", "--quiet"])
    written = json.loads(output.read_text())

    assert code == 0
    assert written["complete"] is True
    assert written["directions"] == 2
    assert written["totals"]["directions_censused"] == 1
    assert [entry["index"] for entry in written["by_direction"]] == [0]
    assert written["margins"] == ["0", "1/100", "1/20", "1/10"]
    assert main([str(path), "--margins", "-1/10"]) == 2


def test_the_retained_rung_at_direction_zero() -> None:
    """Direction 0 of the n = 11 rung, against the certificate's own declaration."""

    certificate, record = load(RETAINED)
    reading = census_direction(
        certificate.atoms,
        certificate.directions[0],
        certificate.outer_side,
        certificate.square_side,
        weight_scale(certificate.atoms),
        margins=DEFAULT_MARGINS,
        index=0,
        half_tangent=Fraction(0),
    )

    assert len(certificate.atoms) == 1121
    assert len(certificate.half_tangents) == 181
    # The census reads the sweep's own grid, so its minimum is the declared number.
    declared = record["least_cell_mass"]
    assert isinstance(declared, str)
    assert reading.minimum_mass == Fraction(declared)
    assert reading.minimum_mass == Fraction(4001, 4000)
    # Reachable cells, against the independently retained cell reduction rather than
    # against the span reduction the census itself expands.
    reference = reduce_to_cells(
        certificate.atoms,
        certificate.directions[0],
        certificate.outer_side,
        certificate.square_side,
    )
    assert reading.reachable_cells == len(reference.cells) == 173889
    # A retained certificate has no cell of mass one, so the margin-zero census is
    # empty; the pinned counts above it are the near-tight set this cell measures.
    assert tuple(margin.tight_cells for margin in reading.margins) == (0, 680, 4752, 10652)
    assert tuple(margin.components for margin in reading.margins) == (0, 28, 24, 48)
    # Nested margins give nested tight sets, so the boxes nest too.
    for narrow, wide in zip(reading.margins[1:-1], reading.margins[2:], strict=True):
        assert narrow.box is not None
        assert wide.box is not None
        assert wide.box.u_low <= narrow.box.u_low
        assert narrow.box.u_high <= wide.box.u_high
        assert wide.box.v_low <= narrow.box.v_low
        assert narrow.box.v_high <= wide.box.v_high
