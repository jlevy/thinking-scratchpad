"""The Bentz Theorem 8 cover certificate and its refusal controls (BC-099).

The positive direction replays the whole certificate; the controls prove the checks
can refuse: a threshold above the certified infimum bound, a face removed from the
tiling, and a set point pushed off its row. Per the run's unattended rules the
mathematical verdict stays unresolved with needs_review until reviewed; these tests
pin the machinery, not the promotion.
"""

from __future__ import annotations

from fractions import Fraction

import pytest

from cases.bentz46.packing import EXPECTED_FACES, EXPECTED_POINTS, build
from cases.bentz46.verify_cover import (
    CoverCertificateError,
    build_certificate,
    certify,
    lemma5_threshold_certificate,
    sqrt_upper,
)
from sqpack.cover import validate_square_tiling


@pytest.mark.slow
def test_certificate_builds_and_charges_every_point() -> None:
    certificate = build_certificate()
    assert certificate["cells"] == {"lemma2": 66, "lemma4": 14, "lemma5": 12}
    assert certificate["set_point_count"] == EXPECTED_POINTS
    assert certificate["every_cell_charges_a_set_point"] is True
    tiling = certificate["tiling"]
    assert tiling["face_count"] == EXPECTED_FACES  # type: ignore[index]
    assert tiling["euler_characteristic"] == 1  # type: ignore[index]


def test_threshold_bound_is_comfortable_and_refuses_a_high_b() -> None:
    record = lemma5_threshold_certificate(Fraction(1, 2))
    assert Fraction(record["certified_infimum_lower_bound"]) > Fraction(19, 20)  # type: ignore[arg-type]
    with pytest.raises(CoverCertificateError, match="threshold refused"):
        lemma5_threshold_certificate(Fraction(24, 25))


def test_sqrt_upper_is_an_upper_bound() -> None:
    for value in (Fraction(1, 2), Fraction(3, 4), Fraction(199, 100)):
        bound = sqrt_upper(value)
        assert bound * bound >= value


def test_tiling_refuses_a_missing_face() -> None:
    field, _sqrt2, _sqrt3, _set_points, vertices, plan = build()
    faces = tuple(entry.face for entry in plan.values())[:-1]
    with pytest.raises(ValueError, match="expected"):
        validate_square_tiling(
            vertices, faces, side=field.rational(7), expected_faces=EXPECTED_FACES
        )
    with pytest.raises(ValueError, match="face areas do not sum to the exact container area"):
        validate_square_tiling(
            vertices, faces, side=field.rational(7), expected_faces=EXPECTED_FACES - 1
        )


@pytest.mark.slow
def test_certificate_refuses_a_displaced_point() -> None:
    field, sqrt2, sqrt3, set_points, vertices, plan = build()
    tampered = dict(vertices)
    x, y = tampered["p3_2"]
    tampered["p3_2"] = (x + field.rational(Fraction(1, 100)), y)
    with pytest.raises(CoverCertificateError, match="triangle side is not exactly one"):
        certify(field, sqrt2, sqrt3, set_points=set_points, vertices=tampered, plan=plan)
