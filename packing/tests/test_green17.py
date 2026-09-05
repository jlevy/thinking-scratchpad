"""The 4426213/10^6 sixteen-point certificate, its controls, and both companions.

The positive direction replays the whole cell certificate at the module side;
the falsifier cross-check saturates on a coarse grid (its caveat stands:
saturation is corroboration, the certificate is the argument); the controls
prove the checks refuse a displaced point and a side pushed past the top
strips' Lemma 4 ceiling `753/250 + sqrt 2` -- in the cell certifier and in the
independent interval audit alike. The interval audit's positive direction runs
at a comfortably interior side here to stay fast; the full-side replay is the
evidence entry's replay command.
"""

from __future__ import annotations

from fractions import Fraction

import pytest

from cases.bentz13.verify_cover import certify
from cases.green17.interval_audit import IntervalAuditError
from cases.green17.interval_audit import certify as interval_certify
from cases.green17.packing import EXPECTED_POINTS, SIDE, Rat, build
from cases.green17.verify_cover import build_certificate
from sqpack.falsify import SaturationReport, search_escape


def test_certificate_builds_and_charges_every_point() -> None:
    certificate = build_certificate()
    assert certificate["cells"] == {
        "lemma4": 13,
        "lemma5": 3,
        "lemma2": 18,
    }
    assert certificate["set_point_count"] == EXPECTED_POINTS
    thresholds = certificate["lemma5_thresholds"]
    assert len(thresholds) == 3  # type: ignore[arg-type]
    for record in thresholds:  # type: ignore[union-attr]
        assert Fraction(record["certified_infimum_lower_bound"]) > Fraction(1, 2)


def test_falsifier_saturates_on_the_set() -> None:
    set_points, _vertices, _plan, _boundary = build()
    points = [(name, float(x.value), float(y.value)) for name, (x, y) in set_points.items()]
    report = search_escape(
        points, float(SIDE), 1.0001, theta_steps=24, xy_steps=24, refine_top=4
    )
    assert isinstance(report, SaturationReport)
    assert report.best_margin < 0
    assert "not a proof" in report.caveat


def test_certificate_refuses_a_displaced_point() -> None:
    set_points, vertices, plan, boundary = build()
    tampered_points = dict(set_points)
    tampered_vertices = dict(vertices)
    displaced = (Rat.of(Fraction(3)), Rat.of(Fraction(9, 10)))
    tampered_points["p0_2"] = displaced
    tampered_vertices["p0_2"] = displaced
    with pytest.raises(ValueError, match="outs do not match the rectangle's inner corners"):
        certify(
            set_points=tampered_points,
            vertices=tampered_vertices,
            plan=plan,
            expected_faces=len(plan),
            boundary=boundary,
            container_side=SIDE,
        )


def test_cell_certifier_refuses_a_side_past_the_lemma4_ceiling() -> None:
    past_ceiling = Fraction(4427, 1000)
    set_points, vertices, plan, boundary = build(side=past_ceiling)
    with pytest.raises(ValueError, match=r"\(a \+ 2b\)\^2 exceeds 8"):
        certify(
            set_points=set_points,
            vertices=vertices,
            plan=plan,
            expected_faces=len(plan),
            boundary=boundary,
            container_side=past_ceiling,
        )


@pytest.mark.slow
def test_interval_audit_certifies_an_interior_side() -> None:
    stats = interval_certify(side=Fraction(22, 5), max_boxes=2_000_000)
    assert stats.boxes > 10_000
    # All four discharge rules are load-bearing on this geometry.
    assert stats.near_point > 0
    assert stats.oriented > 0
    assert stats.pair > 0
    assert stats.no_fit > 0


def test_interval_audit_refutes_past_the_ceiling() -> None:
    with pytest.raises(IntervalAuditError, match="refuted"):
        interval_certify(side=Fraction(4427, 1000), max_boxes=60_000_000)


def test_interval_audit_refutes_a_tampered_set() -> None:
    set_points = build()[0]
    points = [(p[0].value, p[1].value) for p in set_points.values()]
    with pytest.raises(IntervalAuditError, match="refuted"):
        interval_certify(points=points[:15], max_boxes=10_000_000)
