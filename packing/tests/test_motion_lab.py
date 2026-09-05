"""Semantic and artifact contracts for the interactive packing motion spike."""

from __future__ import annotations

import json
import math
import os
import re
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path
from typing import cast

import pytest
from nodejs_wheel import node

from cases.n5 import equal_side_face as face
from cases.n5 import rotating_release_paths as release
from devtools.packing_motion_studies import (
    CONTACTS,
    ROOT,
    build_motion_lab_manifest,
    contact_state,
    project_scene,
)
from devtools.render_packing_motion_lab import MOTION_MODEL_JAVASCRIPT, render_motion_lab
from sqpack.field import FieldElement


@pytest.fixture(scope="module")
def manifest() -> dict[str, object]:
    return build_motion_lab_manifest()


def _scenes(manifest: dict[str, object]) -> Iterator[dict[str, object]]:
    scenes = manifest["scenes"]
    assert isinstance(scenes, list)
    yield from scenes


def _scene(manifest: dict[str, object], scene_id: str) -> dict[str, object]:
    return next(scene for scene in _scenes(manifest) if scene["id"] == scene_id)


def test_manifest_covers_six_paths_and_three_obstruction_views(
    manifest: dict[str, object],
) -> None:
    assert manifest["contract"] == "packing.squares:MotionLab/v1"
    assert manifest["schema_version"] == 1
    assert manifest["default_scene"] == "R4:A"
    assert [scene["id"] for scene in _scenes(manifest)] == [
        "R4:A",
        "R4:interior",
        "R4:B",
        "R5:A",
        "R5:interior",
        "R5:B",
        "plus-W:A",
        "plus-W:interior",
        "plus-W:B",
    ]


@pytest.mark.parametrize(("class_name", "sigma"), release.SIGNS)
@pytest.mark.parametrize("stratum", release.STRATA)
def test_release_projection_reproduces_exact_case_functions(
    manifest: dict[str, object], class_name: str, sigma: int, stratum: str
) -> None:
    scene = _scene(manifest, f"{class_name}:{stratum}")
    field = face.make_field()
    direction = release.position_direction(field, stratum, release.ProofInputs())
    interval_end = cast(FieldElement, face.exact_data(field)["delta"]) / 2
    for progress in (0.0, 0.5, 1.0):
        u = interval_end * field.rational(round(progress * 2)) / 2
        exact_centres = release.centres_at(field, stratum, direction, u)
        projected = project_scene(scene, progress)
        for pose, centre in zip(projected, exact_centres, strict=True):
            assert pose.centre_x == pytest.approx(float(field.decimal(centre[0], 18)))
            assert pose.centre_y == pytest.approx(float(field.decimal(centre[1], 18)))
        assert projected[1].angle_radians == pytest.approx(
            2 * math.atan(sigma * float(field.decimal(u, 18)) / 2)
        )
        assert projected[0].angle_radians == 0
        assert projected[3].angle_radians == pytest.approx(math.pi / 4)


def test_embedded_javascript_model_matches_python_projection_and_controls(
    manifest: dict[str, object],
) -> None:
    probe = (
        MOTION_MODEL_JAVASCRIPT
        + r"""
const fs = require("fs");
const manifest = JSON.parse(fs.readFileSync(0, "utf8"));
const progressValues = [0, 0.5, 1];
const result = {};
for (const scene of manifest.scenes) {
  const useTangent = scene.mode === "second-order-obstruction";
  result[scene.id] = {
    projected: progressValues.map((progress) => posesAt(scene, progress, useTangent)),
    predictor: progressValues.map((progress) => posesAt(scene, progress, true)),
    phases: progressValues.map((progress) => phaseAt(scene, progress)),
    controls: sceneControlState(scene),
    parameterValueText: progressValues.map((progress) => parameterValueText(scene, progress)),
    stageDescriptions: progressValues.map((progress) => stageDescriptionText(scene, progress)),
  };
}
process.stdout.write(JSON.stringify(result));
"""
    )
    completed = node(
        ["-e", probe],
        return_completed_process=True,
        input=json.dumps(manifest, sort_keys=True),
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stderr
    result = cast(dict[str, dict[str, object]], json.loads(completed.stdout))
    progress_values = (0.0, 0.5, 1.0)

    for scene in _scenes(manifest):
        scene_id = cast(str, scene["id"])
        record = result[scene_id]
        projected_records = cast(list[list[dict[str, float | int]]], record["projected"])
        for progress, projected_record in zip(progress_values, projected_records, strict=True):
            expected = project_scene(scene, progress)
            assert [value["id"] for value in projected_record] == [
                pose.square_id for pose in expected
            ]
            for value, pose in zip(projected_record, expected, strict=True):
                assert value["x"] == pytest.approx(pose.centre_x)
                assert value["y"] == pytest.approx(pose.centre_y)
                assert value["angle"] == pytest.approx(pose.angle_radians)

        obstruction = scene["mode"] == "second-order-obstruction"
        assert record["phases"] == (
            ["base", "base", "base"] if obstruction else ["base", "open_interval", "endpoint"]
        )
        assert record["controls"] == {
            "ownerDisabled": not obstruction,
            "playDisabled": obstruction,
            "branchHidden": not obstruction,
        }
        parameter = cast(dict[str, object], scene["parameter"])
        parameter_name = cast(str, parameter["name"])
        value_text = cast(list[str], record["parameterValueText"])
        assert value_text[0] == f"0% of interval; {parameter_name} = 0.0000000"
        assert value_text[1].startswith(f"50% of interval; {parameter_name} = ")
        assert value_text[2].startswith(f"100% of interval; {parameter_name} = ")

        descriptions = cast(list[str], record["stageDescriptions"])
        contact_dash = "\N{EN DASH}"
        pair_03 = f"0{contact_dash}3"
        pair_14 = f"1{contact_dash}4"
        assert all(cast(str, scene["stratum"]) in value for value in descriptions)
        described_progress = zip((0, 50, 100), descriptions, strict=True)
        assert all(f"{percent}%" in value for percent, value in described_progress)
        if obstruction:
            assert all(
                "solid packing stays at its base pose" in value for value in descriptions
            )
            assert all("obstructed at second order" in value for value in descriptions)
            base_contacts = (
                f"Base contact pairs: 0{contact_dash}4, 1{contact_dash}4, "
                f"2{contact_dash}4, 3{contact_dash}4"
            )
            assert all(base_contacts in value for value in descriptions)
        else:
            assert all("certified path" in value for value in descriptions)
            assert pair_14 in descriptions[0]
            assert pair_03 not in descriptions[0]
            assert pair_14 not in descriptions[1]
            assert pair_03 not in descriptions[1]
            assert pair_03 in descriptions[2]
            assert pair_14 not in descriptions[2]

        if not obstruction:
            upper = cast(dict[str, object], parameter["upper"])
            extent = float(cast(str, upper["decimal"]))
            sigma = cast(int, scene["sigma"])
            predictors = cast(list[list[dict[str, float | int]]], record["predictor"])
            for progress, values in zip(progress_values, predictors, strict=True):
                assert values[1]["angle"] == pytest.approx(sigma * extent * progress)


def test_release_rotation_signs_and_contact_events_are_source_declared(
    manifest: dict[str, object],
) -> None:
    r4 = _scene(manifest, "R4:interior")
    r5 = _scene(manifest, "R5:interior")
    assert project_scene(r4, 1)[1].angle_radians < 0
    assert project_scene(r5, 1)[1].angle_radians > 0
    assert contact_state(r4, 0) == CONTACTS["base"]
    assert contact_state(r4, 0.5) == CONTACTS["open_interval"]
    assert contact_state(r4, 1) == CONTACTS["endpoint"]
    assert (1, 4) not in contact_state(r4, 0.5)
    assert (0, 3) not in contact_state(r4, 0.5)


def test_w_is_an_obstruction_ghost_with_both_quadratic_branches(
    manifest: dict[str, object],
) -> None:
    scene = _scene(manifest, "plus-W:A")
    assert scene["mode"] == "second-order-obstruction"
    evidence = cast(dict[str, object], scene["evidence"])
    parameter = cast(dict[str, object], scene["parameter"])
    branches = cast(dict[str, dict[str, object]], scene["branches"])
    assert evidence["status"] == "branch-exhaustive-second-order-obstruction"
    assert "not a feasible path interval" in cast(str, parameter["meaning"])
    owner4 = cast(dict[str, object], branches["owner-4"]["coefficient"])
    owner3 = cast(dict[str, object], branches["owner-3"]["coefficient"])
    assert owner4["coefficients_low_degree_first"] == [
        "0",
        "1/8",
    ]
    assert owner3["coefficients_low_degree_first"] == [
        "-1/4",
        "0",
    ]
    assert contact_state(scene, 0) == CONTACTS["base"]
    assert contact_state(scene, 1) == CONTACTS["base"]
    contacts = cast(dict[str, object], scene["contacts"])
    assert contacts["meaning"] == (
        "base graph only; no feasible contact evolution is certified"
    )


@pytest.mark.slow
def test_rendered_lab_is_deterministic_retained_and_offline(
    manifest: dict[str, object],
) -> None:
    del manifest  # build the fixture first so source validation is part of this contract
    first = render_motion_lab()
    second = render_motion_lab()
    retained = (ROOT / "atlas/rendering/n5-motion-lab.html").read_text(encoding="utf-8")
    assert first == second == retained
    assert "requestAnimationFrame" in first
    assert 'type="range"' in first
    assert 'type="application/json"' in first
    assert "Content-Security-Policy" in first
    assert "connect-src 'none'" in first
    assert "prefers-reduced-motion: reduce" in first
    assert "Play" in first
    assert "Restart" in first
    assert "aria-pressed" not in first
    assert 'aria-valuetext="0% of interval; u = 0.0000000"' in first
    assert 'role="group" aria-labelledby="overlays-label"' in first
    assert "fetch(" not in first
    assert "eval(" not in first
    assert "innerHTML" not in first
    assert "http://" not in first
    assert "https://" not in first
    assert not re.search(r"\son[a-z]+\s*=", first, flags=re.IGNORECASE)


def test_static_fallback_and_epistemic_labels_are_structural() -> None:
    rendered = render_motion_lab()
    notice = '<noscript><p class="noscript-notice">JavaScript is disabled.'
    assert notice in rendered
    assert rendered.index(notice) < rendered.index('<section class="controls"')
    assert ".controls, .readout, #live-region { display: none !important; }" in rendered
    assert 'aria-labelledby="stage-title stage-description"' in rendered
    assert '<span id="overlays-label" class="control-label">Overlays</span>' in rendered
    assert rendered.count('class="square"') == 5
    assert "source-backed pose" in rendered
    assert "first-order predictor" in rendered
    assert "contact-graph relation" in rendered
    assert "not a feasible path" in rendered
    assert "not a global-optimality claim" in rendered
    assert "no feasible contact evolution is certified" in rendered

    for pair in ("0-4", "1-4", "2-4", "3-4"):
        match = re.search(rf'<line id="contact-{pair}"[^>]+>', rendered)
        assert match is not None
        assert 'display="none"' not in match.group()
    closing = re.search(r'<line id="contact-0-3"[^>]+>', rendered)
    assert closing is not None
    assert 'display="none"' in closing.group()


@pytest.mark.slow
def test_motion_lab_is_environment_independent(tmp_path: Path) -> None:
    outputs = [tmp_path / "first.html", tmp_path / "second.html"]
    environments = (
        {"PYTHONHASHSEED": "7", "TZ": "UTC", "LC_ALL": "C"},
        {
            "PYTHONHASHSEED": "913",
            "TZ": "America/Los_Angeles",
            "LC_ALL": "C",
        },
    )
    for output, overrides in zip(outputs, environments, strict=True):
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "devtools.render_packing_motion_lab",
                "--output",
                str(output),
            ],
            cwd=ROOT,
            env=os.environ | overrides,
            capture_output=True,
            text=True,
            check=False,
        )
        assert completed.returncode == 0, completed.stderr
    assert outputs[0].read_bytes() == outputs[1].read_bytes()
