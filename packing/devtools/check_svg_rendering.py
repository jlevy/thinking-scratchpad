#!/usr/bin/env python3
"""Exercise the deterministic SVG renderer and replay its retained artifacts."""

from __future__ import annotations

import argparse
import math
import os
import re
import subprocess
import sys
from collections.abc import Iterator
from dataclasses import replace
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# The repository root. Document surfaces (TUTORIAL.md, SYNOPSIS.md, README.md) live
# there; the rendered artifacts they embed live under packing/.
REPO = ROOT.parent
#: Directories whose Markdown is not this repository's to police. `resources` is the
#: literature archive, whose transcriptions are archived source rather than our prose;
#: `vendor` holds upstream repositories checked out as submodules, the exclusion
#: `.flowmarkignore` states for the same reason; `node_modules` is installed. A
#: dot-prefixed directory is tool-owned. Stated here rather than at each sweep: the two
#: controls below must agree about which documents count, because a target that one
#: sweep calls unowned and the other cannot see is a contradiction, not a finding.
#:
#: `site` is the explainer's render output. It is this repository's, unlike the rest,
#: but it is generated: rebuilt by every run, gitignored, and already guaranteed by the
#: renderer's own `--check`, which compares each artifact byte for byte against a fresh
#: render. The published document there embeds the copy of the composite that the
#: renderer places beside it, which is not one of the atlas's owned artifacts and never
#: will be. Being gitignored is not what excludes it: this sweep walks files git does
#: not track, which is the blind spot D-455 was about.
FOREIGN_DIRECTORY_NAMES = frozenset({"resources", "vendor", "node_modules", "site"})


def repository_documents() -> Iterator[Path]:
    """Every Markdown document this repository is answerable for."""
    for document_path in REPO.rglob("*.md"):
        parts = document_path.relative_to(REPO).parts
        if FOREIGN_DIRECTORY_NAMES & set(parts) or any(part.startswith(".") for part in parts):
            continue
        yield document_path


def _rejects(function, *args, **kwargs) -> bool:
    try:
        function(*args, **kwargs)
    except TypeError, ValueError:
        return True
    return False


def run_model_controls() -> dict[str, bool]:
    from sqpack.render.model import (
        CheckKind,
        CheckSummary,
        ContactFeature,
        ContainerWall,
        EvidenceTier,
        PackingFrame,
        Point2,
        RigidPose,
        SquareGeometry,
        validate_frame,
    )
    from sqpack.render.numbers import scalar_from_exact, scalar_from_float

    scalar = scalar_from_float(1.0)
    corners = tuple(
        Point2(scalar_from_float(x), scalar_from_float(y))
        for x, y in ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))
    )
    square = SquareGeometry("square-0", corners, RigidPose(corners[0], scalar_from_float(0.0)))
    numerical_check = CheckSummary(
        passed=True,
        kind=CheckKind.NUMERICAL,
        method="numerical-f64",
        arithmetic="IEEE 754 binary64",
        precision="53 binary bits",
        rounding="nearest ties-to-even",
        tolerance="1e-12",
        detail="known-answer",
    )
    frame = PackingFrame(
        scalar,
        (square,),
        EvidenceTier.NUMERICALLY_CHECKED,
        numerical_check,
    )
    validate_frame(frame)
    exact_zero = scalar_from_exact("0", Decimal(0))
    exact_one = scalar_from_exact("1", Decimal(1))
    exact_corners = tuple(
        Point2(
            exact_one if x else exact_zero,
            exact_one if y else exact_zero,
        )
        for x, y in ((0, 0), (1, 0), (1, 1), (0, 1))
    )
    exact_square = SquareGeometry("square-0", exact_corners)
    formal_check = CheckSummary(
        passed=True,
        kind=CheckKind.FORMAL,
        method="exact-algebraic",
        detail="known-answer",
    )
    exact_point = Point2(exact_zero, exact_one)
    wall_contact = ContactFeature(
        "contact-wall-square-0-left",
        exact_point,
        ("square-0",),
        wall=ContainerWall.LEFT,
    )
    contact_frame = PackingFrame(
        exact_one,
        (exact_square,),
        EvidenceTier.CERTIFIED_UPPER_BOUND,
        formal_check,
        features=(wall_contact,),
    )
    validate_frame(contact_frame)
    return {
        "duplicate_ids_rejected": _rejects(
            validate_frame, replace(frame, squares=(square, square))
        ),
        "unstable_order_rejected": _rejects(
            validate_frame,
            replace(frame, squares=(replace(square, square_id="square-1"), square)),
        ),
        "failed_check_rejected": _rejects(
            validate_frame, replace(frame, check=replace(numerical_check, passed=False))
        ),
        "numerical_check_cannot_support_formal_evidence": _rejects(
            validate_frame,
            replace(frame, evidence=EvidenceTier.CERTIFIED_UPPER_BOUND),
        ),
        "binary64_contact_rejected": _rejects(
            validate_frame,
            replace(
                frame,
                features=(
                    replace(
                        wall_contact,
                        start=Point2(scalar_from_float(0.0), scalar_from_float(1.0)),
                    ),
                ),
            ),
        ),
        "degenerate_contact_segment_rejected": _rejects(
            validate_frame,
            replace(contact_frame, features=(replace(wall_contact, end=exact_point),)),
        ),
        "bad_wall_participants_rejected": _rejects(
            validate_frame,
            replace(
                contact_frame,
                features=(replace(wall_contact, square_ids=("square-0", "square-1")),),
            ),
        ),
        "uncertified_contact_rejected": _rejects(
            validate_frame,
            replace(contact_frame, evidence=EvidenceTier.CANDIDATE, check=None),
        ),
    }


def run_number_controls() -> dict[str, bool]:
    from sqpack.render.model import EvidenceTier, ScalarKind
    from sqpack.render.numbers import (
        format_svg_number,
        format_visible_number,
        project_decimal,
        scalar_from_exact,
        scalar_from_float,
        scalar_from_fraction,
    )

    precise = Decimal("3.87708359002281417730789706010096")
    exact_bound = scalar_from_exact("trump-side", precise)
    return {
        "negative_zero_normalized": format_svg_number(Decimal("-0")) == "0",
        "fraction_preserved": scalar_from_fraction(Fraction(1, 3)).source == "1/3",
        "binary64_identified": scalar_from_float(0.1).kind is ScalarKind.BINARY64,
        "exact_source_required": _rejects(scalar_from_exact, "", precise),
        "nonfinite_rejected": _rejects(scalar_from_float, math.inf),
        "precision_is_local": project_decimal(precise, 24)
        == Decimal("3.87708359002281417730790"),
        "abbreviated_certified_bound_is_marked_approximate": format_visible_number(
            exact_bound, EvidenceTier.CERTIFIED_UPPER_BOUND
        )
        == ("~", "3.87708359"),
    }


def run_contact_controls() -> dict[str, bool]:
    from cases.n5.face_model import build_equal_side_face
    from cases.trump11 import packing as trump11
    from devtools.packing_render_adapters import frame_from_gobel10, frame_from_trump11
    from sqpack.render.contacts import contact_features_from_exact
    from sqpack.render.model import ContactFeature, ContainerWall
    from sqpack.render.numbers import scalar_from_exact
    from sqpack.verify import Report, exact_sign, verify_packing

    face = build_equal_side_face()
    q, root = face.field.rational, face.field.alpha

    def project(value):
        return scalar_from_exact(repr(value), Decimal(repr(float(value))))

    def contacts(squares, side):
        report = verify_packing(squares, side, sign=exact_sign)
        if not report.valid:
            raise ValueError("contact control fixture is not a valid packing")
        return contact_features_from_exact(
            squares,
            side,
            square_ids=tuple(f"square-{index:02d}" for index in range(len(squares))),
            scalar=project,
            report=report,
        )

    edge_a = ((q(0), q(0)), (q(1), q(0)), (q(1), q(1)), (q(0), q(1)))
    edge_b = ((q(1), q(0)), (q(2), q(0)), (q(2), q(1)), (q(1), q(1)))
    edge_features = contacts((edge_a, edge_b), q(2))
    edge_pairs = [feature for feature in edge_features if feature.wall is None]

    point_a = ((q(0), q(1)), (q(1), q(1)), (q(1), q(2)), (q(0), q(2)))
    point_b = (
        (q(1), q(3) / 2),
        (q(1) + root / 2, q(3) / 2 - root / 2),
        (q(1) + root, q(3) / 2),
        (q(1) + root / 2, q(3) / 2 + root / 2),
    )
    point_features = contacts((point_a, point_b), q(3))
    point_pairs = [feature for feature in point_features if feature.wall is None]

    wall_point_square = (
        (q(0), q(3) / 2),
        (root / 2, q(3) / 2 - root / 2),
        (root, q(3) / 2),
        (root / 2, q(3) / 2 + root / 2),
    )
    wall_point_features = contacts((wall_point_square,), q(3))

    strict_b = ((q(2), q(0)), (q(3), q(0)), (q(3), q(1)), (q(2), q(1)))
    strict_features = contacts((edge_a, strict_b), q(3))
    inconsistent_report = Report(
        valid=True,
        n=2,
        container_contacts=8,
        touching_pairs=1,
        pairs_tested=1,
        touching_pair_indices=[(0, 1)],
    )

    exact_squares, side, _field = trump11.build()
    trump_report = verify_packing(exact_squares, side, sign=exact_sign)
    trump = frame_from_trump11()
    trump_pairs = [
        feature
        for feature in trump.features
        if isinstance(feature, ContactFeature) and feature.wall is None
    ]
    return {
        "wall_edge_is_one_segment": sum(
            feature.wall is ContainerWall.LEFT and feature.end is not None
            for feature in edge_features
        )
        == 1,
        "square_edge_is_one_segment": len(edge_pairs) == 1 and edge_pairs[0].end is not None,
        "point_to_edge_is_one_dot": len(point_pairs) == 1 and point_pairs[0].end is None,
        "wall_point_is_one_dot": len(wall_point_features) == 1
        and wall_point_features[0].wall is ContainerWall.LEFT
        and wall_point_features[0].end is None,
        "strict_pair_has_no_contact": not any(
            feature.wall is None for feature in strict_features
        ),
        "shared_edge_endpoints_are_deduplicated": len(edge_pairs) == 1,
        "inconsistent_pair_geometry_rejected": _rejects(
            contact_features_from_exact,
            (edge_a, strict_b),
            q(3),
            square_ids=("square-00", "square-01"),
            scalar=project,
            report=inconsistent_report,
        ),
        "contact_ids_are_stable": [feature.feature_id for feature in edge_features]
        == sorted(feature.feature_id for feature in edge_features),
        "trump_pair_contacts_match_verifier": len(trump_pairs) == trump_report.touching_pairs,
        "candidate_pose_arrays_have_no_contacts": frame_from_gobel10().features == (),
    }


def build_fixtures():
    from devtools.render_packing_gallery import build_gallery_sources

    sources = build_gallery_sources()
    return {
        "trump11-overview.svg": sources.trump11,
        "gobel10-source-return-comparison.svg": (
            sources.gobel10_start,
            sources.gobel10_final,
        ),
        "n5-exact-face-trajectory.svg": sources.n5_trajectory,
    }


def run_xml_controls() -> dict[str, bool]:
    from xml.etree import ElementTree as ET

    from sqpack.render.svg import (
        MOTION_MARKER,
        append_exact_comment,
        append_local_use,
        element,
        serialize_svg,
        sub,
        validate_safe_tree,
    )

    root = element("svg")
    append_exact_comment(root, "x = 1/3")
    text = serialize_svg(root)
    bad = element("svg")
    ET.SubElement(bad, "script")
    duplicate = element("svg")
    ET.SubElement(duplicate, "rect", {"id": "same"})
    ET.SubElement(duplicate, "circle", {"id": "same"})
    foreign_namespace = element("svg")
    ET.SubElement(foreign_namespace, "{https://example.com/evil}rect")
    arbitrary_css = element("svg")
    sub(
        arbitrary_css,
        "style",
        {"data-sqpack-style": MOTION_MARKER},
    ).text = "@media (prefers-reduced-motion: no-preference){rect{fill:none}}"
    external_clip = element("svg")
    sub(external_clip, "rect", {"clip-path": "url(https://example.com/shape.svg#clip)"})
    return {
        "comment_round_trip": "<!--x = 1/3-->" in text,
        "invalid_comment_rejected": _rejects(append_exact_comment, root, "bad -- comment"),
        "script_rejected": _rejects(validate_safe_tree, bad),
        "duplicate_xml_ids_rejected": _rejects(validate_safe_tree, duplicate),
        "external_use_rejected": _rejects(append_local_use, root, "https://example.com/x"),
        "local_use_accepted": append_local_use(root, "#shape").attrib["href"] == "#shape",
        "foreign_namespace_rejected": _rejects(validate_safe_tree, foreign_namespace),
        "arbitrary_marked_css_rejected": _rejects(validate_safe_tree, arbitrary_css),
        "external_presentation_url_rejected": _rejects(validate_safe_tree, external_clip),
    }


def run_geometry_controls() -> dict[str, bool]:
    from xml.etree import ElementTree as ET

    from devtools.packing_render_adapters import frame_from_gobel10, frame_from_trump11
    from sqpack.render import (
        AnnotationLevel,
        Overlay,
        RenderSpec,
        ViewLevel,
        render_packing_svg,
    )
    from sqpack.render.color import ANGLE_CLASS_CONTRACT, assign_square_colors
    from sqpack.render.model import ActiveFeature
    from sqpack.render.style import (
        CONTACT_CLIP_POLICY,
        CONTACT_HIGHLIGHT_COLOR,
        CONTACT_HIGHLIGHT_OPACITY,
        CONTACT_HIGHLIGHT_POINT_RADIUS,
        CONTACT_HIGHLIGHT_STROKE_WIDTH,
        LAYOUT,
        PACKING_BOUNDARY_COLOR,
        PACKING_BOUNDARY_WIDTH,
        PAPER_THEME,
        SQUARE_HUE_PALETTE,
        evidence_style,
    )

    overview = render_packing_svg(frame_from_trump11(), spec=RenderSpec())
    trump = frame_from_trump11()
    start = frame_from_gobel10()
    comparison = render_packing_svg(
        start,
        start=start,
        spec=RenderSpec(view=ViewLevel.COMPARISON),
    )
    comparison_root = ET.fromstring(comparison)
    _min_x, _min_y, viewport_width, viewport_height = (
        Decimal(value) for value in comparison_root.attrib["viewBox"].split()
    )
    panel_containers = [
        next(
            child
            for child in panel.iter()
            if child.attrib.get("data-feature") == "container-outline"
        )
        for panel in comparison_root.iter()
        if "data-panel" in panel.attrib
    ]
    overview_root = ET.fromstring(overview)
    overview_metadata = {
        node.attrib["name"]: node.text or ""
        for node in overview_root.iter()
        if node.tag.endswith("}value") and "name" in node.attrib
    }
    overview_panel = next(
        node for node in overview_root.iter() if node.attrib.get("data-panel") == "Trump n=11"
    )
    overview_layers = [
        child for child in overview_panel if child.attrib.get("data-layer") is not None
    ]
    overview_fills = next(
        child for child in overview_layers if child.attrib["data-layer"] == "fills"
    )
    overview_contacts = next(
        child for child in overview_layers if child.attrib["data-layer"] == "contacts"
    )
    overview_outlines = next(
        child for child in overview_layers if child.attrib["data-layer"] == "outlines"
    )
    overview_container = next(
        child
        for child in overview_outlines
        if child.attrib.get("data-feature") == "container-outline"
    )
    overview_squares = [
        child for child in overview_fills if child.attrib.get("data-feature") == "square-fill"
    ]
    overview_square_outlines = [
        child
        for child in overview_outlines
        if child.attrib.get("data-feature") == "square-outline"
    ]
    overview_contact_marks = [
        child
        for child in overview_contacts
        if child.attrib.get("data-feature", "").startswith("contact-")
    ]
    overview_contact_clips = {
        child.attrib["id"]: child
        for child in overview_panel.iter()
        if child.attrib.get("data-feature") == "contact-clip"
    }
    overview_contact_clip_shapes = {
        child.attrib["id"]: child
        for child in overview_panel.iter()
        if child.attrib.get("data-feature") == "contact-clip-shape"
    }
    overview_fills_by_id = {square.attrib["data-square"]: square for square in overview_squares}
    expected_colors = assign_square_colors(trump, RenderSpec())

    def contact_clip_matches_participants(mark) -> bool:
        reference = mark.attrib.get("clip-path", "")
        if not reference.startswith("url(#") or not reference.endswith(")"):
            return False
        clip = overview_contact_clips.get(reference[5:-1])
        if clip is None or clip.attrib.get("clipPathUnits") != "userSpaceOnUse":
            return False
        participants = tuple(mark.attrib["data-squares"].split())
        uses = tuple(clip)
        return (
            clip.attrib.get("data-squares") == mark.attrib["data-squares"]
            and tuple(use.attrib.get("data-clip-square") for use in uses) == participants
            and all(
                overview_contact_clip_shapes[use.attrib["href"][1:]].attrib.get("points")
                == overview_fills_by_id[square_id].attrib["points"]
                and overview_contact_clip_shapes[use.attrib["href"][1:]].attrib.get(
                    "data-square"
                )
                == square_id
                for square_id, use in zip(participants, uses, strict=True)
            )
        )

    point = trump.squares[0].corners[0]
    featured = replace(
        trump,
        features=(
            ActiveFeature("active-feature-0", point, "active wall", "square-00"),
            *trump.features,
        ),
    )
    overlay = render_packing_svg(
        featured,
        spec=RenderSpec(overlays=frozenset({Overlay.CONTACTS, Overlay.ACTIVE_FEATURES})),
    )
    event_start, _event_final = build_fixtures()["gobel10-source-return-comparison.svg"]
    exact_text = render_packing_svg(
        event_start, spec=RenderSpec(annotations=AnnotationLevel.EXACT)
    )
    exact_contact_text = render_packing_svg(
        trump, spec=RenderSpec(annotations=AnnotationLevel.EXACT)
    )
    hidden_exact_contact_text = render_packing_svg(
        trump,
        spec=RenderSpec(
            annotations=AnnotationLevel.EXACT,
            overlays=frozenset(),
        ),
    )
    event_pose = event_start.squares[0].pose
    if event_pose is None:
        raise ValueError("BasinEvent fixture lost its pose")
    source_x = event_pose.centre.x.source
    return {
        "overview_is_svg": overview.startswith("<?xml") and "<polygon" in overview,
        "comparison_has_two_panels": comparison.count('data-panel="') == 2,
        "comparison_panels_fit_viewport": all(
            Decimal(container.attrib["x"]) >= 0
            and Decimal(container.attrib["y"]) >= 0
            and Decimal(container.attrib["x"]) + Decimal(container.attrib["width"])
            <= viewport_width
            and Decimal(container.attrib["y"]) + Decimal(container.attrib["height"])
            <= viewport_height
            for container in panel_containers
        ),
        "rendered_square_fills_match_angle_contact_scheme": all(
            square.attrib["fill"] == expected_colors[square.attrib["data-square"]].fill
            and square.attrib["data-hue-index"]
            == str(expected_colors[square.attrib["data-square"]].hue_index)
            and square.attrib["data-shade-index"]
            == str(expected_colors[square.attrib["data-square"]].shade_index)
            and square.attrib["data-contact-sides"]
            == str(expected_colors[square.attrib["data-square"]].contact_sides)
            and square.attrib["data-orientation-radians"]
            == str(expected_colors[square.attrib["data-square"]].orientation_radians)
            and square.attrib["data-angle-class-residual-radians"]
            == str(expected_colors[square.attrib["data-square"]].angle_class_residual_radians)
            and square.attrib["data-full-side-contacts"]
            == " ".join(expected_colors[square.attrib["data-square"]].full_side_contacts)
            and square.attrib.get("data-maximum-contact-residual")
            == (
                str(expected_colors[square.attrib["data-square"]].maximum_contact_residual)
                if expected_colors[square.attrib["data-square"]].maximum_contact_residual
                is not None
                else None
            )
            for square in overview_squares
        ),
        "color_measurement_metadata_is_complete": overview_metadata.get(
            "color-angle-class-contract"
        )
        == ANGLE_CLASS_CONTRACT
        and overview_metadata.get("color-angle-tolerance-radians")
        == str(RenderSpec().angle_tolerance_radians)
        and overview_metadata.get("color-full-side-contact-tolerance")
        == str(RenderSpec().full_side_contact_tolerance),
        "packing_outlines_are_thin_opaque_pure_black": PAPER_THEME.container
        == PACKING_BOUNDARY_COLOR
        == "#000000"
        and LAYOUT.stroke_width == PACKING_BOUNDARY_WIDTH == 1.25
        and overview_container.attrib["stroke"] == PACKING_BOUNDARY_COLOR
        and overview_container.attrib["fill"] == "none"
        and len(overview_square_outlines) == len(overview_squares)
        and all(
            square.attrib["stroke"] == PACKING_BOUNDARY_COLOR
            and square.attrib["fill"] == "none"
            and square.attrib["stroke-width"]
            == overview_container.attrib["stroke-width"]
            == str(LAYOUT.stroke_width)
            for square in overview_square_outlines
        ),
        "contact_highlight_is_reserved_tempered_yellow": PAPER_THEME.contact
        == CONTACT_HIGHLIGHT_COLOR
        == "#e3c64a"
        and PAPER_THEME.contact not in SQUARE_HUE_PALETTE
        and all(
            mark.attrib.get("fill") == PAPER_THEME.contact
            or mark.attrib.get("stroke") == PAPER_THEME.contact
            for mark in overview_contact_marks
        ),
        "contact_highlights_use_selected_opacity_and_size": CONTACT_HIGHLIGHT_OPACITY == 0.6
        and LAYOUT.contact_stroke_width == CONTACT_HIGHLIGHT_STROKE_WIDTH == 9
        and LAYOUT.contact_point_radius == CONTACT_HIGHLIGHT_POINT_RADIUS == 5.5
        and all(
            (
                mark.attrib.get("stroke-opacity") == str(CONTACT_HIGHLIGHT_OPACITY)
                and mark.attrib.get("stroke-width") == str(CONTACT_HIGHLIGHT_STROKE_WIDTH)
            )
            if mark.attrib["data-feature"] == "contact-segment"
            else (
                mark.attrib.get("fill-opacity") == str(CONTACT_HIGHLIGHT_OPACITY)
                and mark.attrib.get("r") == str(CONTACT_HIGHLIGHT_POINT_RADIUS)
            )
            for mark in overview_contact_marks
        ),
        "contact_highlights_are_clipped_to_participating_squares": CONTACT_CLIP_POLICY
        == "participating-square-union"
        and len(overview_contact_clips) == len(overview_contact_marks)
        and all(contact_clip_matches_participants(mark) for mark in overview_contact_marks),
        "contact_highlights_are_between_fills_and_outlines": [
            layer.attrib["data-layer"] for layer in overview_layers
        ]
        == ["fills", "contacts", "outlines"]
        and all(square.attrib["stroke"] == "none" for square in overview_squares),
        "certified_contacts_render_by_default": 'data-feature="contact-segment"' in overview
        and 'data-feature="contact-point"' in overview,
        "contact_overlay_can_be_removed": 'data-feature="contact-'
        not in render_packing_svg(trump, spec=RenderSpec(overlays=frozenset())),
        "typed_overlays_render": 'data-feature="active-feature"' in overlay
        and 'data-feature="contact-' in overlay,
        "evidence_tokens_are_distinct": len(
            {evidence_style(tier) for tier in type(start.evidence)}
        )
        == 3,
        "decimal_source_round_trips": source_x in exact_text,
        "exact_contact_comments_round_trip": "<!--contact-pair-" in exact_contact_text
        and " to (" in exact_contact_text,
        "hidden_contact_annotations_are_retained": "<!--contact-pair-"
        in hidden_exact_contact_text
        and 'data-feature="contact-' not in hidden_exact_contact_text,
        "exact_projection_is_high_precision": str(trump.container_side.projected).startswith(
            "3.877083590022814177307897"
        ),
    }


def run_animation_controls() -> dict[str, bool]:
    from devtools.packing_render_adapters import trajectory_from_n5_equal_side_face
    from sqpack.render import RenderSpec, ViewLevel, render_packing_svg
    from sqpack.render.numbers import scalar_from_float

    trajectory = trajectory_from_n5_equal_side_face()
    text = render_packing_svg(
        trajectory.frames[-1],
        trajectory=trajectory,
        spec=RenderSpec(view=ViewLevel.TRAJECTORY),
    )
    changed_square = replace(trajectory.frames[0].squares[0], square_id="square-X")
    mismatched = replace(
        trajectory,
        frames=(
            replace(
                trajectory.frames[0],
                squares=(changed_square, *trajectory.frames[0].squares[1:]),
            ),
            *trajectory.frames[1:],
        ),
    )
    first_pose = trajectory.frames[0].squares[0].pose
    if first_pose is None:
        raise ValueError("animation control requires a posed square")
    rotating_square = replace(
        trajectory.frames[0].squares[0],
        pose=replace(first_pose, angle=scalar_from_float(0.1)),
    )
    rotating = replace(
        trajectory,
        frames=(
            replace(
                trajectory.frames[0],
                squares=(rotating_square, *trajectory.frames[0].squares[1:]),
            ),
            *trajectory.frames[1:],
        ),
    )
    changing_container = replace(
        trajectory,
        frames=(
            replace(trajectory.frames[0], container_side=scalar_from_float(3.0)),
            *trajectory.frames[1:],
        ),
    )
    return {
        "motion_is_reduced_motion_scoped": "prefers-reduced-motion: no-preference" in text,
        "no_smil": "<animate" not in text,
        "final_state_is_underlying": 'data-static-fallback="final"' in text,
        "final_contacts_reveal_at_trajectory_end": 'class="motion-final-overlay"' in text
        and "opacity:0" in text
        and "step-end" in text,
        "mismatched_tracks_rejected": _rejects(
            render_packing_svg,
            trajectory.frames[-1],
            trajectory=mismatched,
            spec=RenderSpec(view=ViewLevel.TRAJECTORY),
        ),
        "invalid_duration_rejected": _rejects(
            render_packing_svg,
            trajectory.frames[-1],
            trajectory=trajectory,
            spec=RenderSpec(view=ViewLevel.TRAJECTORY, duration_seconds=Decimal(0)),
        ),
        "unsupported_rotation_is_rejected": _rejects(
            render_packing_svg,
            trajectory.frames[-1],
            trajectory=rotating,
            spec=RenderSpec(view=ViewLevel.TRAJECTORY),
        ),
        "unsupported_container_change_is_rejected": _rejects(
            render_packing_svg,
            trajectory.frames[-1],
            trajectory=changing_container,
            spec=RenderSpec(view=ViewLevel.TRAJECTORY),
        ),
    }


def _rendered_fixtures() -> dict[str, str]:
    from devtools.render_packing_gallery import render_gallery
    from devtools.render_t018_proof_visual import ARTIFACT, render_visual

    rendered = render_gallery()
    rendered[ARTIFACT.name] = render_visual()
    return rendered


def run_determinism_matrix() -> dict[str, bool]:
    expected = _rendered_fixtures()
    controls = {}
    environments = (
        {"PYTHONHASHSEED": "1", "TZ": "UTC", "LC_ALL": "C"},
        {"PYTHONHASHSEED": "8675309", "TZ": "America/Los_Angeles", "LC_ALL": "C"},
    )
    for name, text in expected.items():
        probes = []
        for overrides in environments:
            environment = os.environ.copy()
            environment.update(overrides)
            probes.append(
                subprocess.check_output(
                    [sys.executable, "-m", "devtools.check_svg_rendering", "--probe", name],
                    cwd=ROOT,
                    env=environment,
                    text=True,
                )
            )
        controls[name] = all(probe == text for probe in probes)
    return controls


def run_portability_controls() -> dict[str, bool]:
    texts = _rendered_fixtures().values()
    return {
        "self_contained": all(
            "http://" not in text.replace("http://www.w3.org/2000/svg", "") for text in texts
        ),
        "no_external_features": all(
            token not in text
            for text in texts
            for token in ("<!DOCTYPE", "<script", "foreignObject", "xlink:", "@import")
        ),
        "presentation_urls_are_local_fragments": all(
            re.search(r"url\((?!#[A-Za-z][A-Za-z0-9_.-]*\))", text) is None for text in texts
        ),
    }


def run_gallery_controls() -> dict[str, bool]:
    from xml.etree import ElementTree as ET

    from devtools.build_known_best_atlas import SUMMARY_SVG
    from devtools.map_prospective_sources import COVERAGE_OUTPUT
    from devtools.packing_render_adapters import frame_from_kingbird29
    from devtools.render_packing_gallery import build_gallery_manifest
    from devtools.render_t018_proof_visual import ARTIFACT as T018_PROOF_VISUAL
    from sqpack.render import RenderSpec
    from sqpack.render.color import assign_square_colors

    manifest = build_gallery_manifest()
    examples = manifest["examples"]
    ids = [example["id"] for example in examples]
    cases = [ROOT / example["frontier_case"] for example in examples]
    artifacts = [ROOT / example["artifact"] for example in examples]

    def embeds(document: str, artifact: str) -> bool:
        document_path = REPO / document
        relative = os.path.relpath(ROOT / artifact, document_path.parent)
        text = document_path.read_text(encoding="utf-8")
        pattern = rf"!\[[^\]]+\]\({re.escape(relative)}\)"
        return re.search(pattern, text) is not None

    def references(document: str, target: str) -> bool:
        document_path = REPO / document
        relative = os.path.relpath(ROOT / target, document_path.parent)
        text = document_path.read_text(encoding="utf-8")
        pattern = rf"!?\[[^\]]+\]\({re.escape(relative)}(?:#[^)]+)?\)"
        return re.search(pattern, text) is not None

    by_id = {example["id"]: example for example in examples}
    surface_expectations = {
        "TUTORIAL.md": (
            "n3-optimal-moduli",
            "n11-trump-overview",
            "n29-kingbird-overview",
        ),
        "SYNOPSIS.md": (
            "n5-exact-face-trajectory",
            "n11-trump-overview",
            "n29-kingbird-overview",
        ),
    }

    inline_svg_targets = []
    for document_path in repository_documents():
        inline_svg_targets.extend(
            (document_path.parent / target).resolve()
            for target in re.findall(
                r"!\[[^\]]*\]\(([^)]+\.svg)\)",
                document_path.read_text(encoding="utf-8"),
            )
        )

    kingbird_root = ET.fromstring(
        (ROOT / by_id["n29-kingbird-overview"]["artifact"]).read_text(encoding="utf-8")
    )
    kingbird_fills = [
        node.attrib["fill"]
        for node in kingbird_root.iter()
        if node.attrib.get("data-feature") == "square-fill"
    ]
    kingbird_metadata = {
        node.attrib["name"]: node.text or ""
        for node in kingbird_root.iter()
        if node.tag.endswith("}value") and "name" in node.attrib
    }
    kingbird_manifest = by_id["n29-kingbird-overview"]
    kingbird_expected = assign_square_colors(frame_from_kingbird29(), RenderSpec())
    gallery_artifacts = {path.resolve() for path in artifacts}
    document_svg_artifacts = gallery_artifacts | {
        SUMMARY_SVG.resolve(),
        COVERAGE_OUTPUT.resolve(),
        T018_PROOF_VISUAL.resolve(),
    }
    comparison_artifact = by_id["n10-source-return-comparison"]["artifact"]
    comparison_embeds = {
        document_path.relative_to(REPO).as_posix()
        for document_path in repository_documents()
        if embeds(document_path.relative_to(REPO).as_posix(), comparison_artifact)
    }
    return {
        "gallery_has_five_known_answers": len(examples) == 5,
        "gallery_ids_are_unique": len(ids) == len(set(ids)),
        "gallery_covers_expected_n": [example["n"] for example in examples]
        == [3, 5, 10, 11, 29],
        "frontier_cases_exist": all(path.is_file() for path in cases),
        "gallery_artifacts_exist": all(path.is_file() for path in artifacts),
        "gallery_alt_text_is_nonempty": all(example["alt"].strip() for example in examples),
        "gallery_commands_are_explicit": all(
            example["generator"].startswith(
                "uv run --frozen --all-extras --group dev python -m "
            )
            for example in examples
        ),
        "gallery_contact_flags_match_exact_sources": {
            example["id"]: example["contacts"] for example in examples
        }
        == {
            "n3-optimal-moduli": False,
            "n5-exact-face-trajectory": True,
            "n10-source-return-comparison": False,
            "n11-trump-overview": True,
            "n29-kingbird-overview": False,
        },
        "kingbird_uses_angle_contact_colors_in_stable_square_order": len(kingbird_fills) == 29
        and kingbird_fills == [color.fill for color in kingbird_expected.values()],
        "kingbird_is_numerically_checked_not_verified": (
            kingbird_manifest["evidence"] == "numerically-checked"
            and "verified" not in kingbird_manifest["caption"].lower()
            and kingbird_metadata.get("evidence") == "numerically-checked"
        ),
        "kingbird_numerical_check_metadata_is_complete": all(
            kingbird_metadata.get(field)
            for field in (
                "check-method",
                "check-arithmetic",
                "check-precision",
                "check-rounding",
                "check-tolerance",
            )
        )
        and kingbird_metadata.get("check-kind") == "numerical"
        and kingbird_metadata.get("check-result") == "passed",
        "all_inline_svg_targets_exist": bool(inline_svg_targets)
        and all(path.is_file() for path in inline_svg_targets),
        "all_inline_svg_targets_are_owned_artifacts": set(inline_svg_targets)
        <= document_svg_artifacts,
        "frontier_cases_reference_gallery_artifacts_or_guide": all(
            embeds(f"packing/{example['frontier_case']}", example["artifact"])
            or references(f"packing/{example['frontier_case']}", "atlas/rendering/README.md")
            for example in examples
        ),
        "gallery_readme_embeds_every_artifact": all(
            embeds("packing/atlas/rendering/README.md", example["artifact"])
            for example in examples
        ),
        "comparison_is_embedded_only_in_focused_gallery": comparison_embeds
        == {"packing/atlas/rendering/README.md"},
        "exposition_surfaces_embed_expected_examples": all(
            embeds(document, by_id[example_id]["artifact"])
            for document, example_ids in surface_expectations.items()
            for example_id in example_ids
        ),
        "atlas_documents_manifest": "[`manifest.json`](rendering/manifest.json)"
        in (ROOT / "atlas/README.md").read_text(encoding="utf-8"),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--update", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--model-numbers", action="store_true")
    parser.add_argument("--probe", choices=tuple(_rendered_fixtures()))
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.probe:
        sys.stdout.write(_rendered_fixtures()[args.probe])
        return 0
    controls = {**run_model_controls(), **run_number_controls(), **run_contact_controls()}
    if not args.model_numbers:
        controls |= run_xml_controls()
        controls |= run_geometry_controls()
        controls |= run_animation_controls()
        controls |= run_determinism_matrix()
        controls |= run_portability_controls()
        controls |= run_gallery_controls()
        if args.update:
            from devtools.render_packing_gallery import write_gallery
            from devtools.render_t018_proof_visual import write_artifact

            write_gallery()
            write_artifact()
        elif args.check:
            from devtools.render_packing_gallery import check_gallery
            from devtools.render_t018_proof_visual import check_artifact

            check_gallery()
            check_artifact()
    failed = [name for name, passed in controls.items() if not passed]
    if failed:
        raise ValueError(f"SVG rendering controls failed: {failed}")
    print(f"SVG RENDERING CHECKS PASSED: {len(controls)} controls")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
