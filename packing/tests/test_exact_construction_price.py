"""The decimal route reproduces neither known contact structure, so it prices nothing.

`BC-049`'s remaining instances, `n = 28` and `n = 40`, retain decimal witnesses, and
`X-007` says their next slice is producing an exact pose rather than assessing again. The
obvious way to start is to extract a contact structure from the decimals. This is the
measurement showing that does not work, and the measurement is only worth anything because
it was run at the two sizes whose answers are already known.

`n = 11`'s structure is exact — 14 pair and 20 wall contacts at floor `0` — and the
decimal route decides at no floor at all. `n = 29`'s is 52 pair and 37 wall at floor
`1e-80`, extracted from a 160-digit materialisation of a provenance SVG, and the route
reports different numbers from the 99-digit witness.

The assertion that matters is the negative one. A future change that made these
"reproduce" would most likely have loosened the comparison rather than fixed the route,
and the windows the route reports sit *below* the retained precision, which is what tells
you they are windows on padding.
"""

from __future__ import annotations

import json

import pytest

from devtools.price_exact_construction import (
    RECORD,
    SUBJECTS,
    digit_reach,
    price,
    retained_structure,
    serialized,
)


def _record() -> dict:
    return json.loads(RECORD.read_text(encoding="utf-8"))


def test_the_route_reproduces_neither_known_structure() -> None:
    """The calibration, and the reason nothing else here is evidence."""
    calibration = _record()["calibration"]

    assert sorted(calibration) == ["11", "29"]
    for n, row in calibration.items():
        assert row["reproduced"] is False, (n, row)

    assert calibration["11"]["retained"] == {
        "pair_contacts": 14,
        "wall_contacts": 20,
        "floor": "0",
    }
    assert calibration["29"]["retained"]["pair_contacts"] == 52
    assert calibration["29"]["retained"]["wall_contacts"] == 37


def test_the_retained_structures_are_read_not_assumed() -> None:
    """The comparison is against the atlas, so it moves if the atlas does."""
    assert retained_structure(11) is not None
    assert retained_structure(29) is not None
    assert retained_structure(28) is None
    assert retained_structure(40) is None


def test_reach_is_zero_at_the_retained_precision_everywhere() -> None:
    """Including `n = 11`, whose minimal polynomial the repository did recover.

    That recovery used four hundred digits manufactured from a closed system. The witness
    carries 32. So the retained decimals are not the input to the promotion route at any
    size, which is why "does n = 28 have enough digits" is the wrong question.
    """
    for n in SUBJECTS:
        stage = digit_reach(n)
        assert stage["reach_degree"] == 0, (n, stage)
    assert digit_reach(11)["retained_digits"] == 32
    assert digit_reach(40)["retained_digits"] == 29


def test_the_deciding_windows_sit_below_the_retained_precision() -> None:
    """What makes them padding rather than structure.

    A contact residual cannot be resolved below the last digit the witness carries. Every
    window the route reports starts finer than that, so what it is separating is the zeros
    the materialisation appended.
    """
    built = _record()
    for n, stage in built["stages"].items():
        window = stage["stage_2_contact_structure"]
        if not window["decided_at_any_swept_floor"]:
            continue
        carried = stage["stage_1_digits"]["retained_digits"]
        start = int(window["window"].split(" to ")[0].removeprefix("1e-"))
        assert start > carried, (n, window["window"], carried)


def test_the_price_is_a_source_and_the_record_says_so() -> None:
    """`BC-049`'s exit accepts a typed refusal. This is the type."""
    verdict = _record()["verdict"]

    assert "higher-precision source" in verdict["the_price"]
    assert "typed refusal" in verdict["the_price"]
    assert "n = 28" in verdict["the_price"]
    # And the correction: n=40 never needed this route.
    assert "published" in verdict["n40_did_not_need_this_route_at_all"]
    assert "not one whose" in verdict["so_the_measured_windows_are_not_evidence"]
    assert "the input, not the extractor" in verdict["why_it_fails"]


def test_nothing_here_promotes_anything() -> None:
    subject = _record()["subject"]

    assert "no frontier record moves" in subject["promotes_nothing"]
    assert subject["instances"] == [28, 40]


@pytest.mark.slow
def test_the_record_round_trips() -> None:
    assert RECORD.read_text(encoding="utf-8") == serialized(price())
