#!/usr/bin/env python3
"""Coverage and source-adapter checks for the retained known-best atlas."""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

import cairosvg
import jsonschema
import pytest
import yaml

from devtools import build_known_best_atlas as known_best_builder
from devtools import render_composite_pdf
from sqpack.known_best import (
    SourceGeometryError,
    catalogue_source_map,
    parse_kingbird_svg,
    parse_unitsquare_svg,
)
from sqpack.render.color import ANGLE_CLASS_CONTRACT
from sqpack.render.model import RenderSpec
from sqpack.render.style import FIRST_PARTY_ACCENT_COLOR
from sqpack.witness import load_witness

ROOT = Path(__file__).resolve().parent.parent
ATLAS = ROOT / "atlas/known-best"
SOURCES = ROOT / "resources/web/known-best-packings"
WITNESSES = ROOT / "witnesses/known-best"
SCHEMA = ROOT / "witnesses/witness.schema.yaml"
UNITSQUARE_RESULTS = ROOT / "resources/web/unitsquare-release1-2026/results.json"
SVG = {"svg": "http://www.w3.org/2000/svg"}


@pytest.fixture
def isolated_atlas_build_cache():
    """For tests that repoint a source root.

    The builder memoizes the hundred cases so one process builds them once.
    A test that points UNITSQUARE_ROOT at a corrupted copy must neither read a
    memo built against the real root nor leave its own behind. Only those tests
    need this; clearing for every test would rebuild repeatedly and cost more
    than the memo saves.
    """
    known_best_builder.clear_build_caches()
    yield
    known_best_builder.clear_build_caches()


def test_catalogue_map_and_retained_unitsquare_geometry() -> None:
    source_page = ROOT / "resources/web/kingbird-squares-in-squares.html"
    catalogue = catalogue_source_map(source_page)
    assert catalogue[11] == ("square-11.svg", 11, (11,))
    assert catalogue[47] == ("square-48.svg", 48, (47, 48))

    prospective = catalogue_source_map(source_page, first_n=101, last_n=324)
    assert len(prospective) == 127
    assert len({record[0] for record in prospective.values()}) == 114
    assert prospective[119] == ("square-120.svg", 120, (119, 120))
    assert 111 not in prospective

    with pytest.raises(ValueError, match="nonempty and positive"):
        catalogue_source_map(source_page, first_n=324, last_n=101)

    release = json.loads(UNITSQUARE_RESULTS.read_text(encoding="utf-8"))
    release_by_n = {record["n"]: record for record in release["results"]}
    for n in (68, 69):
        geometry = parse_unitsquare_svg(
            (SOURCES / "unitsquare" / f"n{n:03d}.svg").read_text(encoding="utf-8"),
            expected_n=n,
        )
        assert len(geometry.squares) == n
        assert (
            geometry.upstream_declared_parent_content_sha256 == release_by_n[n]["record_sha256"]
        )


def test_kingbird_sources_are_metadata_only_derived_facts() -> None:
    assert not (SOURCES / "kingbird").exists()

    source_index = json.loads((SOURCES / "sources.json").read_text(encoding="utf-8"))
    assert source_index["contract"] == "packing.squares:KnownBestSourceInventory/v1"
    kingbird = [
        record
        for record in source_index["sources"]
        if record["kind"] == "kingbird-derived-facts"
    ]
    expected_n = {
        5,
        10,
        11,
        17,
        18,
        19,
        26,
        27,
        28,
        29,
        37,
        38,
        39,
        40,
        41,
        50,
        51,
        52,
        53,
        54,
        55,
        65,
        66,
        67,
        70,
        71,
        82,
        83,
        84,
        85,
        86,
        87,
        88,
        89,
    }
    assert {record["n"] for record in kingbird} == expected_n
    assert len(kingbird) == len(expected_n)
    for record in kingbird:
        assert record["attribution"].startswith("SVG and high-precision updates")
        assert record["source_n"] == record["n"]
        assert record["listed_n"] == [record["n"]]
        assert record["raw_asset_retained"] is False
        assert record["license_status"] == "no-express-reuse-terms-found"
        assert record["retention_policy"] == "metadata-and-derived-numerical-facts-only"
        assert {"bytes", "path", "sha256"}.isdisjoint(record)

    unitsquare = [
        record for record in source_index["sources"] if record["kind"] == "unitsquare-rendering"
    ]
    release = json.loads(UNITSQUARE_RESULTS.read_text(encoding="utf-8"))
    release_by_n = {record["n"]: record for record in release["results"]}
    assert {record["n"] for record in unitsquare} == {68, 69}
    for record in unitsquare:
        assert record["raw_asset_retained"] is True
        assert record["bytes"] > 0
        assert record["upstream_declared_sha256"] == release_by_n[record["n"]]["svg_sha256"]
        assert "sha256" not in record
        path = ROOT / record["path"]
        assert path.is_file()
        assert (
            hashlib.sha256(path.read_bytes()).hexdigest() == record["upstream_declared_sha256"]
        )


@pytest.mark.usefixtures("isolated_atlas_build_cache")
def test_known_best_rejects_corrupted_retained_unitsquare_svg(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = SOURCES / "unitsquare/n068.svg"
    monkeypatch.setattr(known_best_builder, "UNITSQUARE_ROOT", tmp_path)
    (tmp_path / "n068.svg").write_bytes(source.read_bytes() + b"\n")

    with pytest.raises(ValueError, match="upstream-declared SVG SHA-256"):
        known_best_builder.expected_outputs()


@pytest.mark.parametrize(
    ("svg", "kind"),
    [
        (
            (
                '<svg xmlns="http://www.w3.org/2000/svg">'
                '<rect id="outer" width="2" height="3" fill="none"/>'
                "</svg>"
            ),
            "outer-frame-not-square",
        ),
        (
            (
                '<svg xmlns="http://www.w3.org/2000/svg">'
                '<rect id="outer" width="2" height="2" fill="none"/>'
                '<path d="M0 0 C0 1 1 1 1 0 Z"/>'
                "</svg>"
            ),
            "unsupported-path",
        ),
    ],
)
def test_kingbird_adapter_rejects_unsupported_source_geometry(svg: str, kind: str) -> None:
    with pytest.raises(SourceGeometryError) as captured:
        parse_kingbird_svg(svg)

    assert captured.value.kind == kind


def test_kingbird_adapter_uses_first_duplicate_id_in_tree_order() -> None:
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg">'
        '<defs><rect id="outer" width="3" height="3" fill="none"/>'
        '<rect id="one" width="1" height="1"/>'
        '<g id="two"><rect id="one" width="2" height="1"/></g></defs>'
        '<use href="#one"/><use href="#one" x="1"/><use href="#one" x="2"/>'
        "</svg>"
    )

    geometry = parse_kingbird_svg(svg, expected_n=3)

    assert len(geometry.poses) == 3


@pytest.mark.parametrize(
    "href", ["missing", "#missing", "packing.svg#one", "https://example/one"]
)
def test_kingbird_adapter_rejects_nonlocal_or_unresolved_use(href: str) -> None:
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg">'
        '<defs><rect id="outer" width="2" height="2" fill="none"/>'
        '<rect id="one" width="1" height="1"/></defs>'
        f'<use href="{href}"/>'
        "</svg>"
    )

    with pytest.raises(SourceGeometryError) as captured:
        parse_kingbird_svg(svg)

    assert captured.value.kind == "broken-reference"


def test_kingbird_adapter_ignores_bare_local_use_only_after_count_reconciliation() -> None:
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg">'
        '<defs><rect id="outer" width="2" height="2" fill="none"/></defs>'
        '<g id="corner"><rect width="2" height="1"/></g>'
        '<use href="corner" y="1"/>'
        "</svg>"
    )

    with pytest.raises(SourceGeometryError) as missing_count:
        parse_kingbird_svg(svg)
    with pytest.raises(SourceGeometryError) as wrong_count:
        parse_kingbird_svg(svg, expected_n=4)
    geometry = parse_kingbird_svg(svg, expected_n=2)

    assert missing_count.value.kind == "broken-reference"
    assert wrong_count.value.kind == "broken-reference"
    assert len(geometry.poses) == 2


def test_known_best_atlas_covers_every_frontier_case() -> None:
    document = json.loads((ATLAS / "manifest.json").read_text(encoding="utf-8"))
    release = json.loads(UNITSQUARE_RESULTS.read_text(encoding="utf-8"))
    release_by_n = {record["n"]: record for record in release["results"]}
    assert document["softschema"]["contract"] == "packing.squares:KnownBestAtlas/v1"
    entries = document["atlas"]["entries"]
    assert document["atlas"]["composite"] == {
        "layout": "10 by 10, row-major n=1..100",
        "png_high_resolution": {
            "derived_from": "atlas/known-best/known-best-1-100.svg",
            "height": 5792,
            "path": "atlas/known-best/known-best-1-100@2x.png",
            "scale": 2,
            "width": 4800,
        },
        "png_preview": {
            "derived_from": "atlas/known-best/known-best-1-100.svg",
            "height": 2896,
            "path": "atlas/known-best/known-best-1-100.png",
            "scale": 1,
            "width": 2400,
        },
        "renderer": "sqpack deterministic composite renderer",
        "square_count": 5050,
        "svg": {
            "height": 2896,
            "path": "atlas/known-best/known-best-1-100.svg",
            "width": 2400,
        },
    }
    assert [entry["n"] for entry in entries] == list(range(1, 101))
    assert Counter(entry["source"]["kind"] for entry in entries) == {
        "exact-grid": 64,
        "kingbird-derived-facts": 34,
        "unitsquare-rendering": 2,
    }

    for entry in entries:
        n = entry["n"]
        witness_path = ROOT / entry["witness"]["path"]
        witness = load_witness(witness_path, fallback_schema=SCHEMA)
        assert witness["n"] == n
        assert witness["id"] == entry["witness"]["id"]
        assert len(witness["squares"]) == n
        if entry["source"]["kind"] == "kingbird-derived-facts":
            assert entry["source"]["path"] == ("resources/web/known-best-packings/sources.json")
            assert witness["source"]["key"] == "Kingbird derived numerical facts"
            assert witness["source"]["path"] == entry["source"]["path"]
            assert "not a legal conclusion" in witness["claim"]["limitations"]
        elif entry["source"]["kind"] == "unitsquare-rendering":
            assert witness["source"]["revision"] == (
                f"upstream-declared parent-content SHA-256 {release_by_n[n]['record_sha256']}"
            )
        assert (ROOT / entry["rendering"]["path"]).is_file()
        frontier = (ROOT / entry["frontier_path"]).read_text(encoding="utf-8")
        assert f"    - {witness['id']}\n" in frontier

    n29_frontier = (ROOT / "frontier/n-029.md").read_text(encoding="utf-8")
    assert "    - W-n029-kingbird\n" in n29_frontier


def test_known_best_v1_schema_accepts_a_manifest_without_the_new_composite() -> None:
    atlas = json.loads((ATLAS / "manifest.json").read_text(encoding="utf-8"))["atlas"]
    atlas.pop("composite")
    schema = yaml.safe_load(
        (ATLAS / "known-best-atlas.schema.yaml").read_text(encoding="utf-8")
    )

    jsonschema.validate(atlas, schema)


def _committed_composite_svg() -> str:
    """The retained composite vector, read the way its drift checks compare it.

    Four tests below ask what the composite *contains* or what an export was drawn
    *from*, and a valid composite answers both; none of them needs a freshly built one.
    Building it costs about 80s on CI's two-core runner and was billed to whichever of
    them ran first in each xdist worker, which is why two of them reported 82.00s and
    78.78s against a 5s per-test ceiling (run for `c1120c44`, job 101371257966). `BC-214`
    deferred the neighbour that used to pay it; `BC-218` measured that the cost belongs
    to the build rather than to any test, so no marker can place it.

    `read_text(encoding="utf-8")` rather than the bytes, deliberately: it is what
    `test_known_best_composite_contains_every_case_and_square` compares below and what
    `build_known_best_atlas.check()` compares in the full gate, so what those two pin is
    exactly the string these tests read, and the substitution composes rather than
    nearly composes.
    """
    return (ATLAS / "known-best-1-100.svg").read_text(encoding="utf-8")


@pytest.mark.slow
def test_known_best_composite_contains_every_case_and_square() -> None:
    outputs, _manifest = known_best_builder.expected_outputs()
    composite_path = ATLAS / "known-best-1-100.svg"

    # The pin the quick lane's four composite tests stand on: they read the retained
    # vector, and this is where "retained" and "built" are made one thing inside pytest.
    # Free here -- the build above is already paid -- and checked again from the other
    # side by the full gate's `known-best n=1..100 atlas` step.
    assert composite_path.read_text(encoding="utf-8") == outputs[composite_path]

    root = ET.fromstring(outputs[composite_path])
    metadata = {
        node.attrib["name"]: node.text or ""
        for node in root.iter()
        if node.tag.endswith("}value") and "name" in node.attrib
    }
    spec = RenderSpec()
    expected_color_metadata = {
        "angle-class-contract": ANGLE_CLASS_CONTRACT,
        "color-angle-tolerance-radians": str(spec.angle_tolerance_radians),
        "color-full-side-contact-tolerance": str(spec.full_side_contact_tolerance),
        "color-hue-count": str(spec.hue_count),
        "color-hue-scheme": spec.hue_scheme.value,
        "color-shade-lightness-span": str(spec.shade_lightness_span),
        "color-shade-scheme": spec.shade_scheme.value,
        "color-shades-per-hue": str(spec.shades_per_hue),
    }
    assert expected_color_metadata.items() <= metadata.items()
    cards = root.findall(".//svg:g[@data-n]", SVG)
    assert [int(card.attrib["data-n"]) for card in cards] == list(range(1, 101))
    assert len(root.findall(".//svg:polygon[@data-feature='square-fill']", SVG)) == 5050
    assert [card.attrib["data-row"] for card in cards[:10]] == ["0"] * 10
    assert [card.attrib["data-column"] for card in cards[:10]] == [
        str(column) for column in range(10)
    ]

    labels = [
        node.text for node in root.findall(".//svg:text[@data-feature='packing-label']", SVG)
    ]
    # The bound is split into tspans so the variable s can be italic, so join
    # the runs rather than reading the element's own text.
    bounds = [
        "".join(node.itertext())
        for node in root.findall(".//svg:text[@data-feature='side-bound']", SVG)
    ]
    assert labels == [str(n) for n in range(1, 101)]
    assert len(bounds) == 100
    # A proved optimum is stated as an equality, a best-known bound as <=.
    assert all(re.fullmatch(r"s\(\d+\) [=≤] .+", bound) for bound in bounds)
    assert sum(" = " in bound for bound in bounds) == 35


def test_known_best_composite_png_is_derived_from_current_svg() -> None:
    svg_text = _committed_composite_svg()
    png = (ATLAS / "known-best-1-100.png").read_bytes()

    assert known_best_builder.png_summary_receipt(png) == (
        2400,
        2896,
        hashlib.sha256(svg_text.encode("utf-8")).hexdigest(),
    )


def test_known_best_composite_high_resolution_png_is_derived_from_current_svg() -> None:
    """The 2x export is pinned to the same canvas and the same source as the preview.

    It exists so the atlas can be attached or downscaled without going back to the
    vector, which means it is the copy most likely to be handed to someone who cannot
    check it. Pinning the exact pixel count matters as much as pinning the receipt:
    4800 by 5792 is twice 2400 by 2896, and the whole-number scale is what keeps the
    file small. A fractional scale puts every edge on a fractional pixel boundary, and
    the antialiasing shades the rasteriser then invents cost more bytes than the extra
    pixels do -- a 4096-wide export of this drawing is 11% larger than this one while
    carrying 27% fewer pixels.
    """
    svg_text = _committed_composite_svg()
    png = (ATLAS / "known-best-1-100@2x.png").read_bytes()

    assert known_best_builder.png_summary_receipt(png) == (
        4800,
        5792,
        hashlib.sha256(svg_text.encode("utf-8")).hexdigest(),
    )


def test_known_best_composite_exports_all_carry_one_source_receipt() -> None:
    """Every export of the composite names the same SVG, so they cannot disagree.

    The vector, both rasters and the PDF are one family drawn in one `--update` run.
    What makes "the PNG matches the PDF" checkable rather than asserted is that all
    four receipts are the digest of the same source: two rasterisers of one drawing
    differ only in how they antialias an edge, whereas two drawings differ in what
    they show. This is the pin that would fail if an export were refreshed alone.
    """
    svg_text = _committed_composite_svg()
    expected = hashlib.sha256(svg_text.encode("utf-8")).hexdigest()

    receipts = {
        export.path.name: known_best_builder.png_summary_receipt(export.path.read_bytes())[2]
        for export in known_best_builder.SUMMARY_RASTERS
    }
    receipts["known-best-1-100.pdf"] = render_composite_pdf.pdf_receipt(
        (ATLAS / "known-best-1-100.pdf").read_bytes()
    )

    assert set(receipts) == {
        "known-best-1-100.png",
        "known-best-1-100@2x.png",
        "known-best-1-100.pdf",
    }
    assert set(receipts.values()) == {expected}


def test_known_best_composite_rasters_scale_the_one_canvas_by_whole_numbers() -> None:
    """Every raster is a whole multiple of the canvas, and the preview is the 1x one.

    The dimensions are derived from `SUMMARY_WIDTH` and `SUMMARY_HEIGHT` rather than
    stored, so a resized canvas moves every export together. This pins the two facts
    that derivation relies on: the scales are integers, and no two exports collide on
    one path.
    """
    exports = known_best_builder.SUMMARY_RASTERS

    assert [export.scale for export in exports] == [1, 2]
    assert len({export.path for export in exports}) == len(exports)
    for export in exports:
        assert export.width == known_best_builder.SUMMARY_WIDTH * export.scale
        assert export.height == known_best_builder.SUMMARY_HEIGHT * export.scale


@pytest.mark.parametrize("scale", [1, 2])
def test_known_best_composite_png_refuses_a_raster_of_the_wrong_size(
    scale: int, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The receipt names the canvas, so a raster drawn at another size cannot be written.

    The rasters and the PDF are drawn from the same SVG by the same rasteriser, and the
    only thing standing between a resized canvas and a stale export is this check. It
    runs for both scales because the guard compares against the export's own size, and
    a guard that only ever saw the 1x canvas would pass a 2x export that ignored it.
    """
    export = known_best_builder.RasterExport(
        path=tmp_path / f"summary-{scale}x.png", scale=scale, role="preview"
    )
    monkeypatch.setattr(known_best_builder, "SUMMARY_WIDTH", 64)
    monkeypatch.setattr(known_best_builder, "SUMMARY_HEIGHT", 64)
    wrong_size = cairosvg.svg2png(
        bytestring=b'<svg xmlns="http://www.w3.org/2000/svg" width="8" height="8"/>',
        output_width=8,
        output_height=8,
        background_color="white",
    )
    assert isinstance(wrong_size, bytes)
    monkeypatch.setattr(known_best_builder.cairosvg, "svg2png", lambda **_kwargs: wrong_size)

    with pytest.raises(ValueError, match="PNG preview dimensions are 8x8"):
        known_best_builder._update_png_export(export, "<svg/>\n")  # pyright: ignore[reportPrivateUsage]  # noqa: SLF001
    assert not export.path.exists()


def test_known_best_atlas_check_reports_the_pdf_export_too(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """One `--check` covers the whole composite family, the PDF included.

    `render_composite_pdf` owns the page and keeps its own check, but a reader who
    runs the atlas check should not be told three of four exports are current and
    left to discover the fourth by running a second command. The three states that
    matter are pinned here: absent, present with a receipt naming another SVG, and
    present with the right one.
    """
    svg_text = "<svg/>\n"
    digest = hashlib.sha256(svg_text.encode("utf-8")).hexdigest()
    pdf = tmp_path / "known-best-1-100.pdf"
    monkeypatch.setattr(render_composite_pdf, "SUMMARY_PDF", pdf)
    problems = known_best_builder._composite_pdf_problems  # pyright: ignore[reportPrivateUsage]  # noqa: SLF001

    assert problems(svg_text) == ["missing atlas/known-best/known-best-1-100.pdf"]

    pdf.write_bytes(
        b"%PDF-1.5\n%%EOF\n%" + render_composite_pdf.PDF_SOURCE_KEY + b": " + b"0" * 64 + b"\n"
    )
    assert problems(svg_text) == [
        "missing or stale atlas/known-best/known-best-1-100.pdf export receipt"
    ]

    pdf.write_bytes(
        b"%PDF-1.5\n%%EOF\n%"
        + render_composite_pdf.PDF_SOURCE_KEY
        + b": "
        + digest.encode("ascii")
        + b"\n"
    )
    assert problems(svg_text) == []


def _figure_entries() -> dict[int, dict]:
    record = json.loads(
        (ROOT / "atlas/known-best/composite-figure.json").read_text(encoding="utf-8")
    )
    return {entry["n"]: entry for entry in record["figure"]["entries"]}


def _frontier_rigidity(n: int) -> dict | None:
    text = (ROOT / f"frontier/n-{n:03d}.md").read_text(encoding="utf-8")
    return yaml.safe_load(text.split("---", 2)[1])["packing"]["rigidity"]


def test_the_figure_never_claims_a_rigidity_its_record_does_not_carry() -> None:
    """`D-385`: the figure decided this from `n` and never opened the record.

    A module-level set of the four packings the catalogue annotates "Rigid." earned the
    same solid glyph as the ten derived from an exact tiling, so a source's word and a
    first-party argument rendered identically. This is `D-354`'s split failing to reach
    the figure lane, and the assertion below is the line that was missing.
    """
    for n, entry in _figure_entries().items():
        established = entry["rigidity"]["state"] == "established"
        block = _frontier_rigidity(n)
        carried = block is not None and block["property"] == "locally-rigid"
        assert established == carried, (
            f"n={n}: figure says {entry['rigidity']['state']} while the frontier record "
            f"says {None if block is None else block['property']}"
        )


def test_a_catalogue_annotation_is_shown_but_never_counted() -> None:
    """Dropping the annotation would lose a fact; merging it was the defect.

    The figure keeps it, as a muted badge on a `not-established` entry, and the totals
    count the two separately. `n = 5` was the case that made this earn its keep, because
    `X-007` established more about it than the catalogue ever said and still not local
    rigidity. It left the annotated set on 2026-09-03, when `T-014` proved local rigidity
    at fixed side and moved the entry to a first-party basis, which is the transition
    this separation exists to make visible: the catalogue's claim is still carried on the
    entry, and it is still not what the total counts.
    """
    record = json.loads(
        (ROOT / "atlas/known-best/composite-figure.json").read_text(encoding="utf-8")
    )
    entries = {entry["n"]: entry for entry in record["figure"]["entries"]}
    annotated = sorted(
        n for n, e in entries.items() if e["rigidity"]["basis"] == "catalogue-annotation"
    )

    assert annotated == [28, 40]
    assert record["figure"]["totals"]["rigidity_catalogue_annotated"] == len(annotated)
    assert record["figure"]["totals"]["rigidity_established"] == 12
    for n in annotated:
        entry = entries[n]
        assert entry["rigidity"]["state"] == "not-established"
        rigid_badges = [badge for badge in entry["badges"] if badge["glyph"] == "R"]
        assert [badge["style"] for badge in rigid_badges] == ["muted"]

    # n=11 is the case the old rule under-credited: its rigidity is ours, not Kingbird's.
    assert entries[11]["rigidity"]["basis"] == "first-party-argument"
    assert [b["style"] for b in entries[11]["badges"] if b["glyph"] == "R"] == ["solid"]


def test_only_the_bound_numeral_carries_the_new_result_accent() -> None:
    """The star marks the case; the accent marks what is new about it.

    A first-party lower bound is new in the number it reaches, not in the function it
    bounds, so `s(n) >=` keeps the caption colour every other card sets it in and the
    numeral alone takes the accent that matches the star in the badge row above. The
    record decides which cases are starred; this decides how a starred one is set, and
    reads it off the drawing rather than the record so the two must agree.

    The separating space is asserted too. It is the one part of the line that a split
    into coloured runs can silently drop, and losing it would leave the drawing right
    and every reader that takes the text rather than the ink wrong.
    """
    root = ET.fromstring(_committed_composite_svg())
    record = json.loads((ATLAS / "composite-figure.json").read_text(encoding="utf-8"))

    accented: list[str] = []
    plain: list[str] = []
    for node in root.findall(".//svg:text[@data-feature='lower-bound']", SVG):
        assert node.attrib["fill"] == known_best_builder.SUMMARY_SMALL_FILL
        marked = [
            span
            for span in node.findall("svg:tspan", SVG)
            if span.attrib.get("fill") == FIRST_PARTY_ACCENT_COLOR
        ]
        assert len(marked) <= 1
        line = "".join(node.itertext())
        assert re.fullmatch(r"s\(\d+\) \u2265 [0-9.]+", line), line
        if not marked:
            plain.append(line)
            continue
        accented.append(line)
        value = marked[0].text or ""
        assert re.fullmatch(r"[0-9.]+", value), value
        assert line.endswith(" " + value), line

    assert len(accented) == record["figure"]["totals"]["lower_bound_first_proved_here"]
    assert len(plain) > len(accented)
