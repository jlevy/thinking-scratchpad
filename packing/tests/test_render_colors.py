"""Behavioral checks for deterministic packing color assignment."""

from __future__ import annotations

from decimal import Decimal
from math import sqrt
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from devtools.build_known_best_atlas import frame_from_witness
from sqpack.render.color import assign_square_colors, hex_oklch, square_fill_palette
from sqpack.render.model import (
    HueScheme,
    PackingFrame,
    Point2,
    RenderSpec,
    RigidPose,
    ShadeScheme,
    SquareGeometry,
)
from sqpack.render.numbers import scalar_from_decimal
from sqpack.render.style import SQUARE_FILL_PALETTE, SQUARE_HUE_PALETTE
from sqpack.witness import load_witness

ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "atlas"
# Separation is measured in OkLCh, not HSL. HSL hue degrees are not
# perceptually uniform, so they misreport how far apart two bases look: the
# closest pair here sits 7.0 deg apart in HSL but 16.6 deg apart in OkLCh, with
# an OkLab distance of 0.062. OkLab distance is the binding guard; the hue gap
# additionally stops two families reading as shades of one colour.
MINIMUM_BASE_HUE_SEPARATION_DEGREES = 14
MINIMUM_BASE_OKLAB_DISTANCE = 0.035
# A shade may drift in hue from its base: lightening in HSL is not hue-preserving
# in OkLCh, and the drift grows at the light end of the ramp, reaching 5.7 deg
# for the sky blue. The bound exists to catch a shade derived from the WRONG
# base, which would be tens of degrees out, not to police this few-degree walk.
MAXIMUM_SHADE_HUE_DRIFT_DEGREES = 7.0


def _point(x: Decimal | int | str, y: Decimal | int | str) -> Point2:
    return Point2(scalar_from_decimal(x), scalar_from_decimal(y))


def _oklab(fill: str) -> tuple[float, float, float]:
    channels = tuple(int(fill[offset : offset + 2], 16) / 255 for offset in (1, 3, 5))
    red, green, blue = (
        channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    )
    light = 0.4122214708 * red + 0.5363325363 * green + 0.0514459929 * blue
    medium = 0.2119034982 * red + 0.6806995451 * green + 0.1073969566 * blue
    short = 0.0883024619 * red + 0.2817188376 * green + 0.6299787005 * blue
    light, medium, short = light ** (1 / 3), medium ** (1 / 3), short ** (1 / 3)
    return (
        0.2104542553 * light + 0.793617785 * medium - 0.0040720468 * short,
        1.9779984951 * light - 2.428592205 * medium + 0.4505937099 * short,
        0.0259040371 * light + 0.7827717662 * medium - 0.808675766 * short,
    )


def _axis_square(
    square_id: str, x: Decimal | int | str, y: Decimal | int | str
) -> SquareGeometry:
    left = Decimal(str(x))
    bottom = Decimal(str(y))
    return SquareGeometry(
        square_id,
        (
            _point(left, bottom),
            _point(left + 1, bottom),
            _point(left + 1, bottom + 1),
            _point(left, bottom + 1),
        ),
    )


def _grid_frame() -> PackingFrame:
    return PackingFrame(
        scalar_from_decimal(2),
        (
            _axis_square("square-01", 0, 0),
            _axis_square("square-02", 0, 1),
            _axis_square("square-03", 1, 0),
            _axis_square("square-04", 1, 1),
        ),
    )


def _contact_level_frame() -> PackingFrame:
    squares = (
        _axis_square("square-01", 3, 3),
        _axis_square("square-02", 0, 8),
        _axis_square("square-03", 0, 0),
        _axis_square("square-04", 0, 12),
        _axis_square("square-05", 1, 12),
        _axis_square("square-06", 0, 13),
        _axis_square("square-07", 10, 10),
        _axis_square("square-08", 9, 10),
        _axis_square("square-09", 11, 10),
        _axis_square("square-10", 10, 9),
        _axis_square("square-11", 10, 11),
    )
    return PackingFrame(scalar_from_decimal(20), squares)


def test_default_contact_shading_maps_zero_through_four_flush_sides() -> None:
    colors = assign_square_colors(_contact_level_frame(), RenderSpec())

    assert {color.hue_index for color in colors.values()} == {0}
    assert colors["square-01"].contact_sides == 0
    assert colors["square-02"].contact_sides == 1
    assert colors["square-03"].contact_sides == 2
    assert colors["square-04"].contact_sides == 3
    assert colors["square-07"].contact_sides == 4
    assert colors["square-07"].full_side_contacts == (
        "square-10",
        "square-09",
        "square-11",
        "square-08",
    )
    assert colors["square-07"].maximum_contact_residual == 0
    assert [colors[f"square-0{index}"].shade_index for index in range(1, 5)] == [
        4,
        3,
        2,
        1,
    ]
    assert colors["square-07"].shade_index == 0


def test_partial_edge_overlap_does_not_count_as_a_flush_side() -> None:
    frame = PackingFrame(
        scalar_from_decimal(20),
        (
            _axis_square("square-01", 5, 5),
            _axis_square("square-02", 6, "5.25"),
        ),
    )

    colors = assign_square_colors(frame, RenderSpec())

    assert {color.contact_sides for color in colors.values()} == {0}


def test_n68_near_wall_rotations_are_not_full_side_contacts() -> None:
    witness = load_witness(
        ROOT / "witnesses/known-best/n-068.yaml",
        fallback_schema=ROOT / "witness.schema.yaml",
    )
    spec = RenderSpec()
    colors = assign_square_colors(frame_from_witness(witness), spec)

    quarter_turn = Decimal("1.57079632679489661923132169163975144209858469968755291048747")
    near_axis_offsets = tuple(
        min(
            colors[square_id].orientation_radians,
            quarter_turn - colors[square_id].orientation_radians,
        )
        for square_id in ("square-019", "square-049", "square-050")
    )
    assert min(near_axis_offsets) > spec.angle_tolerance_radians * 100
    assert max(near_axis_offsets) < Decimal("0.002")

    assert colors["square-019"].hue_index != colors["square-001"].hue_index
    assert colors["square-049"].hue_index != colors["square-050"].hue_index
    assert colors["square-019"].contact_sides == 0
    assert colors["square-049"].contact_sides == 0
    assert colors["square-050"].contact_sides == 0
    assert colors["square-019"].full_side_contacts == ()
    assert colors["square-049"].full_side_contacts == ()
    assert colors["square-050"].full_side_contacts == ()


def test_full_side_contacts_join_numerically_split_angle_classes() -> None:
    witness = load_witness(
        ROOT / "witnesses/prospective/n-105.yaml",
        fallback_schema=ROOT / "witness.schema.yaml",
    )
    colors = assign_square_colors(frame_from_witness(witness), RenderSpec())

    assert "square-101" in colors["square-094"].full_side_contacts
    assert "square-094" in colors["square-101"].full_side_contacts
    assert colors["square-094"].angle_class == colors["square-101"].angle_class
    assert colors["square-094"].hue_index == colors["square-101"].hue_index


def test_contact_shading_scales_to_a_custom_shade_count() -> None:
    colors = assign_square_colors(_contact_level_frame(), RenderSpec(shades_per_hue=3))

    assert colors["square-01"].shade_index == 2
    assert colors["square-07"].shade_index == 0


def test_contrast_coloring_remains_available_for_edge_neighbors() -> None:
    colors = assign_square_colors(
        _grid_frame(),
        RenderSpec(shade_scheme=ShadeScheme.CONTRAST, shades_per_hue=2),
    )

    assert {color.hue_index for color in colors.values()} == {0}
    assert colors["square-01"].shade_index != colors["square-02"].shade_index
    assert colors["square-01"].shade_index != colors["square-03"].shade_index
    assert colors["square-01"].shade_index == colors["square-04"].shade_index


def test_angle_hues_use_pose_precision_and_fold_quarter_turns() -> None:
    zero = scalar_from_decimal(0)
    quarter_turn = scalar_from_decimal("1.5707963267948966192313216916397514420985846996876")
    diagonal = scalar_from_decimal("0.78539816339744830961566084581987572104929234984378")
    squares = (
        SquareGeometry(
            "square-01",
            _axis_square("unused-01", 0, 0).corners,
            RigidPose(_point(0, 0), zero),
        ),
        SquareGeometry(
            "square-02",
            _axis_square("unused-02", 1, 0).corners,
            RigidPose(_point(1, 0), quarter_turn),
        ),
        SquareGeometry(
            "square-03",
            _axis_square("unused-03", 2, 0).corners,
            RigidPose(_point(2, 0), diagonal),
        ),
    )
    frame = PackingFrame(scalar_from_decimal(3), squares)

    colors = assign_square_colors(frame, RenderSpec(shades_per_hue=1))

    assert colors["square-01"].hue_index == colors["square-02"].hue_index
    assert colors["square-03"].hue_index != colors["square-01"].hue_index
    assert colors["square-03"].angle_class_residual_radians == 0
    assert {color.shade_index for color in colors.values()} == {0}


def test_default_angle_tolerance_absorbs_source_rounding_not_distinct_angles() -> None:
    squares = tuple(
        SquareGeometry(
            f"square-0{index}",
            _axis_square(f"unused-0{index}", index - 1, 0).corners,
            RigidPose(_point(index - 1, 0), scalar_from_decimal(angle)),
        )
        for index, angle in enumerate(("0", "5e-7", "2e-6"), start=1)
    )
    frame = PackingFrame(scalar_from_decimal(3), squares)

    colors = assign_square_colors(frame, RenderSpec(shades_per_hue=1))

    assert colors["square-01"].hue_index == colors["square-02"].hue_index
    assert colors["square-03"].hue_index != colors["square-01"].hue_index


def test_index_sequence_scheme_remains_available() -> None:
    spec = RenderSpec(
        hue_scheme=HueScheme.INDEX,
        shade_scheme=ShadeScheme.SEQUENCE,
        hue_count=3,
        shades_per_hue=2,
    )

    colors = assign_square_colors(_grid_frame(), spec)

    assert [colors[f"square-0{index}"].hue_index for index in range(1, 5)] == [0, 1, 2, 0]
    assert [colors[f"square-0{index}"].shade_index for index in range(1, 5)] == [0, 0, 0, 1]


def test_requested_palette_dimensions_are_unique_and_configurable() -> None:
    palette = square_fill_palette(hue_count=20, shades_per_hue=5)

    assert len(palette) == 20
    assert all(len(family) == 5 for family in palette)
    assert len({fill for family in palette for fill in family}) == 100
    assert set(SQUARE_HUE_PALETTE) == set(SQUARE_FILL_PALETTE)
    assert SQUARE_HUE_PALETTE[:4] == (
        "#1faa8e",
        "#c3c45f",
        "#aa5585",
        "#166eac",
    )
    # The base no longer sits mid-ramp: lightness is compressed toward the mid
    # band and saturation climbs across the family, and the two pinned families
    # are built in OkLCh. What must hold is that every shade still carries its
    # base's hue.
    for base, family in zip(SQUARE_HUE_PALETTE, palette, strict=True):
        base_hue = hex_oklch(base)[2]
        for fill in family:
            drift = abs(hex_oklch(fill)[2] - base_hue)
            assert min(drift, 360 - drift) <= MAXIMUM_SHADE_HUE_DRIFT_DEGREES, (base, fill)
    hues = tuple(hex_oklch(fill)[2] for fill in SQUARE_HUE_PALETTE)
    assert (
        min(
            min(abs(left - right), 360 - abs(left - right))
            for index, left in enumerate(hues)
            for right in hues[index + 1 :]
        )
        >= MINIMUM_BASE_HUE_SEPARATION_DEGREES
    )
    oklab = tuple(_oklab(fill) for fill in SQUARE_HUE_PALETTE)
    assert (
        min(
            sqrt(sum((left[channel] - right[channel]) ** 2 for channel in range(3)))
            for index, left in enumerate(oklab)
            for right in oklab[index + 1 :]
        )
        >= MINIMUM_BASE_OKLAB_DISTANCE
    )
    assert square_fill_palette(hue_count=7, shades_per_hue=3) != palette


def test_every_indexed_atlas_fill_matches_its_declared_color_contract() -> None:
    indexed_files = 0
    indexed_fills = 0
    palettes: dict[tuple[int, int, Decimal], tuple[tuple[str, ...], ...]] = {}
    for path in sorted(ATLAS.rglob("*.svg")):
        root = ET.fromstring(path.read_text(encoding="utf-8"))
        fills = [
            node for node in root.iter() if node.attrib.get("data-feature") == "square-fill"
        ]
        if not fills:
            continue
        indexed_files += 1
        metadata = {
            node.attrib["name"]: node.text or ""
            for node in root.iter()
            if node.tag.endswith("}value") and "name" in node.attrib
        }
        contract = (
            int(metadata["color-hue-count"]),
            int(metadata["color-shades-per-hue"]),
            Decimal(metadata["color-shade-lightness-span"]),
        )
        palette = palettes.setdefault(
            contract,
            square_fill_palette(
                hue_count=contract[0],
                shades_per_hue=contract[1],
                lightness_span=contract[2],
            ),
        )
        for fill in fills:
            hue_index = int(fill.attrib["data-hue-index"])
            shade_index = int(fill.attrib["data-shade-index"])
            assert fill.attrib["fill"] == palette[hue_index][shade_index], path
        indexed_fills += len(fills)

    assert indexed_files == 211
    assert indexed_fills == 32017


def test_color_parameters_reject_nonpositive_values() -> None:
    for spec in (
        RenderSpec(hue_count=0),
        RenderSpec(shades_per_hue=0),
        RenderSpec(full_side_contact_tolerance=Decimal(0)),
    ):
        try:
            assign_square_colors(_grid_frame(), spec)
        except ValueError as error:
            assert "positive" in str(error)
        else:
            raise AssertionError("nonpositive color parameter was accepted")

    try:
        assign_square_colors(_grid_frame(), RenderSpec(shade_lightness_span=Decimal("0.31")))
    except ValueError as error:
        assert "between 0 and 0.3" in str(error)
    else:
        raise AssertionError("excessive shade lightness span was accepted")


def test_default_scheme_is_angle_with_contacts_and_five_shades() -> None:
    spec = RenderSpec()

    assert spec.hue_scheme is HueScheme.ANGLE
    assert spec.shade_scheme is ShadeScheme.CONTACTS
    assert spec.hue_count == 20
    assert spec.shades_per_hue == 5
    assert spec.shade_lightness_span == Decimal("0.2")
    assert spec.angle_tolerance_radians == Decimal("1e-6")
    assert spec.full_side_contact_tolerance == Decimal("2e-6")


def _atlas_frames() -> list[PackingFrame]:
    witnesses = sorted((ROOT / "witnesses/known-best").glob("n-*.yaml"))
    return [frame_from_witness(load_witness(path)) for path in witnesses]


@pytest.mark.slow
def test_right_angles_and_diagonals_are_pinned_across_the_atlas() -> None:
    """Right angles always take hue 0 and 45 degree tilts always take hue 1.

    Orientation is stored modulo a quarter turn, so an axis-aligned class can be
    represented just under 90 degrees rather than at 0; n=69's 42-square class is
    exactly that case. The pin therefore compares modulo the seam.
    """
    spec = RenderSpec(overlays=frozenset())
    right_angle_hues: set[int] = set()
    diagonal_hues: set[int] = set()
    for frame in _atlas_frames():
        for color in assign_square_colors(frame, spec).values():
            degrees = float(color.orientation_radians) * 180 / 3.141592653589793
            offset = min(degrees, 90 - degrees)
            if offset < 1e-4:
                right_angle_hues.add(color.hue_index)
            elif abs(degrees - 45) < 1e-4:
                diagonal_hues.add(color.hue_index)
    assert right_angle_hues == {0}
    assert diagonal_hues == {1}


def test_unpinned_classes_take_hues_by_descending_class_size() -> None:
    """Everything past the two pinned angles is ordered by how many squares it holds."""
    spec = RenderSpec(overlays=frozenset())
    frame = frame_from_witness(load_witness(ROOT / "witnesses/known-best/n-068.yaml"))
    colors = assign_square_colors(frame, spec)
    sizes: dict[int, int] = {}
    for color in colors.values():
        sizes[color.hue_index] = sizes.get(color.hue_index, 0) + 1
    unpinned = sorted((hue, count) for hue, count in sizes.items() if hue >= 2)
    counts = [count for _hue, count in unpinned]
    assert counts == sorted(counts, reverse=True), unpinned
    assert min(hue for hue, _count in unpinned) == 2
