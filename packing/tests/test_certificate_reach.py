"""Controls for the certificate-reach renderer's caps and measured-attainment arithmetic.

Three retained certificates -- n = 11, n = 17 and n = 19 -- have each landed within a
narrow band of the same fraction of their case's best known packing. The renderer
derives that band from the live corpus rather than carrying the numbers as constants,
so the control that matters is a round trip: recompute the ratios from
`frontier/n-*.md` and the retained `certificate.json` files, and check the band and
the arithmetic built on it, rather than pinning values by hand.

The packing-side cap is controlled the same way: its one hand-checked figure is X-014's
`3.868983` at n = 11, and everything else -- the grid identity, the fold, the null
inventory, the ordering against the ceiling -- is recomputed from the record.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

import devtools.render_certificate_reach as reach
from devtools.render_certificate_reach import (
    CASES,
    COVERING_VALUES,
    NET,
    OUT,
    REPO,
    cases,
    covering_value_register,
    load_certificate,
    mean_packing_ratio,
    measured_attainment,
    packing_side_cap,
    predicted_reach,
    render,
    reported_covering_values,
    retained_certificates,
)
from devtools.validate_schemas import check as validate_artifact

BAND = 0.001


def test_committed_file_matches_the_renderer() -> None:
    """The checked-in CERTIFICATE-REACH.md is never hand-edited; a drift is a bug."""
    assert OUT.read_text() == render(cases())


def test_retained_certificates_are_found_by_globbing_the_case_packages() -> None:
    """Four packages exist today, each keyed by the least size its own mass certifies.

    The key is computed, never read off the package name, and the n = 20 package is
    the case that shows why: while its retained rung was the 24/5 one, mass
    18.922620 keyed it to n = 19; T-021's 97/20 rung has mass 19.848723 and keys it
    to n = 20. That the four keys agree with their package names today is a fact
    about the current corpus, not a property of the glob.
    """
    retained = retained_certificates()
    keyed_n = {row["package"]: row["n"] for row in retained}
    assert keyed_n == {
        "n11_fractional_certificate": 11,
        "n12_fractional_certificate": 12,
        "n17_fractional_certificate": 17,
        "n20_fractional_certificate": 20,
    }


def test_retained_certificate_mass_is_recomputed_from_its_atoms(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A stale declared mass cannot silently key a certificate to the wrong case."""
    package = tmp_path / "n2_fractional_certificate"
    package.mkdir()
    (package / "certificate.json").write_text(
        json.dumps({"outer_side": "1", "total_mass": "1", "atoms": [["0", "0", "2"]]}),
        encoding="utf-8",
    )
    monkeypatch.setattr(reach, "CASES", tmp_path)
    with pytest.raises(ValueError, match="declared total_mass 1 does not equal atom sum 2"):
        reach.retained_certificates()


def test_reported_rows_quote_the_mass_their_own_artifact_recomputes() -> None:
    """The evidence column is a retention claim: every artifact it names must resolve.

    Checked row by row against the register rather than against a list of sides
    written here. The list-of-sides form of this control passed for months and then
    missed the thing it existed to catch: when T-021 landed, a register row still
    named the n = 20 package's moving `certificate.json` pointer, so the 24/5 row
    quoted the 97/20 rung's mass. Deriving the expectation from the same register the
    renderer reads is what makes the round trip a check rather than a restatement.
    """
    register = covering_value_register()
    reported = reported_covering_values()
    assert len(reported) == len(register)

    frozen = 0
    for row, source in zip(reported, register, strict=True):
        artifact = source["frozen_artifact"]
        if artifact is None:
            # A side with no artifact says so rather than borrowing a neighbour's figure.
            assert "nothing frozen here" in row["evidence"]
            assert row["mass"] is None
            continue
        frozen += 1
        _, mass = load_certificate(REPO / artifact)
        assert row["mass"] == mass
        assert f"feasible mass {float(mass):.6f}" in row["evidence"]
    assert frozen, "no register row names a frozen artifact; the corpus changed shape"


def test_covering_value_register_validates_against_its_schema() -> None:
    """The register is an enforced soft-schema artifact, checked by the gate's own validator.

    Beyond the schema: `(n, side, site_set)` is the key, so it is unique, and the
    decimal side the prose quotes is exactly the rational the run used.
    """
    assert validate_artifact(COVERING_VALUES) == []
    rows = covering_value_register()
    keys = [(row["n"], row["side"], row["site_set"]) for row in rows]
    assert len(keys) == len(set(keys))
    for row in rows:
        assert Fraction(row["side"]) == Fraction(row["side_decimal"])


def test_every_frozen_artifact_in_the_register_recomputes_its_mass() -> None:
    """A frozen artifact must exist, sum to its declared mass, and sit at the row's side."""
    frozen = [row for row in covering_value_register() if row["frozen_artifact"] is not None]
    assert frozen, "no register row names a frozen artifact; the corpus changed shape"
    for row in frozen:
        path = REPO / row["frozen_artifact"]
        assert path.is_file(), row["frozen_artifact"]
        record, _ = load_certificate(path)
        assert Fraction(str(record["outer_side"])) == Fraction(row["side"])
        assert record["n"] == row["n"]


def test_every_recorded_in_path_exists() -> None:
    """A register row cites only documents that are in the repository."""
    for row in covering_value_register():
        for cited in row["recorded_in"]:
            assert (REPO / cited).is_file(), cited


def test_rendered_table_lists_every_register_row_with_its_convergence() -> None:
    """Each row renders once, keyed by n, side and site set, with `converged` as yes/no."""
    text = render(cases())
    rows = covering_value_register()
    for row in rows:
        verdict = "yes" if row["converged"] else "no"
        prefix = (
            f"| {row['n']} | {row['side_decimal']} | {row['site_set']} | "
            f"{row['objective']} | {verdict} |"
        )
        assert text.count(prefix) == 1, prefix
    # Both answers occur, so the column is doing work rather than repeating one word.
    assert any(row["converged"] for row in rows)
    assert any(not row["converged"] for row in rows)


def test_prizes_are_nonnegative_and_never_render_negative_zero() -> None:
    """Independent float parsing cannot turn an equal endpoint into `-0.0000`."""
    rows = cases()
    assert all(row["prize"] >= 0.0 for row in rows)
    assert all(f"{row['prize']:+.4f}" != "-0.0000" for row in rows)


def test_axis_parallel_grid_packings_cap_exactly_at_the_ceiling() -> None:
    """An inventory of `[0]` has factor 1, so the cap is `U / (1 + D)`.

    Where `U` is the grid side `ceil(sqrt(n))` that is the ceiling's own rational,
    and the renderer keeps the product exact until the last step, so the two floats
    are equal bit for bit and the tie reads `ceiling`, as it did before the cap.
    """
    rows = cases()
    grid = [row for row in rows if row["tilts"] == [0.0] and row["upper"] == row["order"]]
    assert {12, 20, 21, 61} <= {row["n"] for row in grid}
    for row in grid:
        assert row["cap"] == row["ceiling"]
        assert row["limit"] == row["ceiling"]
        assert row["bound"] == "ceiling"
        assert row["verdict"] != "cap"


def test_n11_cap_reproduces_x014_at_the_retained_shrink() -> None:
    """X-014's arithmetic: `U * B * (cos d + sin d)` is 3.868983 at `B = 9977/10000`.

    The shrink is read from the retained certificate rather than typed here, and the
    net-level cap must sit at or above the shrink-level one -- `1 / (1 + D)` exceeds
    the retained `B` -- and strictly below the packing.
    """
    row = next(row for row in cases() if row["n"] == 11)
    record, _ = load_certificate(CASES / "n11_fractional_certificate" / "certificate.json")
    shrink = Fraction(str(record["square_side"]))
    assert shrink == Fraction(9977, 10000)
    at_shrink = packing_side_cap(row["upper"], row["tilts"], NET, shrink)
    assert f"{at_shrink:.6f}" == "3.868983"
    assert at_shrink <= row["cap"] < row["upper"]
    assert row["bound"] == "cap"
    assert row["verdict"] == "cap"


def test_every_symmetric_image_of_a_tilt_folds_to_the_same_cap() -> None:
    """A tilt, its diagonal reflection, its sign and a quarter turn cap alike.

    The fold is exact, so three of the four images give the same float; the fourth
    is `90 + t` as a float, which is not exactly `t` plus ninety, hence the tolerance.
    """
    row = next(row for row in cases() if row["n"] == 11)
    tilt = row["tilts"][1]
    reference = packing_side_cap(row["upper"], [0.0, tilt], NET)
    for image in (tilt, 90 - tilt, -tilt, 90 + tilt):
        assert packing_side_cap(row["upper"], [0.0, image], NET) == pytest.approx(
            reference, abs=1e-12
        )


def test_a_case_without_a_tilt_inventory_has_no_cap() -> None:
    """`tilt_angles_deg: null` means no geometry was imported: no cap is invented."""
    rows = {row["n"]: row for row in cases()}
    assert rows[19]["tilts"] is None
    assert rows[19]["cap"] is None
    assert rows[19]["limit"] == rows[19]["ceiling"]
    assert rows[19]["verdict"] == "packing"
    for row in rows.values():
        if row["tilts"] is None:
            assert row["cap"] is None
            assert row["limit"] == row["ceiling"]
            assert row["bound"] == "ceiling"


def test_the_limit_never_exceeds_the_ceiling() -> None:
    """`limit = min(ceiling, cap)`, a cap always sits below its packing, prizes are >= 0."""
    for row in cases():
        assert row["limit"] <= row["ceiling"]
        assert row["prize"] >= 0.0
        if row["cap"] is not None:
            assert row["cap"] < row["upper"]
            assert row["limit"] == min(row["ceiling"], row["cap"])
            assert row["verdict"] != "packing"


def test_the_cap_forecloses_the_solved_tilted_cases() -> None:
    """n = 5 and n = 10 are solved and their packings carry a 45-degree tilt.

    The cap sits strictly below the proved value, so nothing was ever on offer there,
    and the table now says so instead of listing a `+0.0000` prize.
    """
    rows = cases()
    by_cap = {
        row["n"] for row in rows if row["verdict"] == "foreclosed" and row["bound"] == "cap"
    }
    assert by_cap == {5, 10}
    for row in rows:
        if row["n"] in by_cap:
            assert row["lower"] == pytest.approx(row["upper"])
            assert row["cap"] < row["lower"]


def test_an_empty_tilt_inventory_is_refused() -> None:
    """Every square has a tilt; an empty list is a record defect, not a null inventory."""
    with pytest.raises(ValueError, match="cannot be empty"):
        packing_side_cap(4.0, [], NET)


def test_the_packing_limited_ratios_sit_inside_a_tight_band() -> None:
    """The packing-limited rows land within 0.001 of each other, however many there are.

    n = 11 and n = 17 are the two today. It was three until T-021: the n = 20 package
    keyed to n = 19, where the best packing bound it, and the 97/20 rung moved it to
    n = 20, where the ceiling 4.9885 sits below the best packing 5.0000 and so binds
    instead. The band is the regularity worth guarding; which cases sit inside it is
    a fact about the corpus and is read from it.
    """
    measured = measured_attainment(cases())
    packing_limited = {row["n"]: row for row in measured if row["binds"] == "packing"}
    assert set(packing_limited) == {11, 17}
    ratios = [row["ratio"] for row in packing_limited.values()]
    assert max(ratios) - min(ratios) <= BAND
    # Each ratio is close to the ~0.982 the record has settled on -- checked loosely,
    # since the tight assertion above is what actually pins the regularity.
    assert all(0.97 < ratio < 0.99 for ratio in ratios)


def test_ceiling_limited_certificate_is_excluded_from_the_mean() -> None:
    """n = 12's ceiling sits below its best packing, so its ratio measures the ceiling."""
    measured = measured_attainment(cases())
    n12 = next(row for row in measured if row["n"] == 12)
    assert n12["binds"] == "ceiling"

    mean_with_n12 = mean_packing_ratio([*measured, {**n12, "binds": "packing"}])
    mean_without = mean_packing_ratio(measured)
    assert mean_with_n12 != mean_without


def test_predicted_never_exceeds_the_limit() -> None:
    """`predicted` is `min(ratio * best_packing, limit)`; it crosses neither cap."""
    rows = cases()
    measured = measured_attainment(rows)
    ratio = mean_packing_ratio(measured)
    live = [row for row in rows if row["verdict"] != "foreclosed"]
    for row in predicted_reach(live, ratio):
        assert row["predicted"] <= row["limit"] + 1e-12
        assert row["predicted"] <= row["ceiling"] + 1e-12
        assert row["predicted_gain"] >= 0.0


def test_predicted_gain_is_clamped_at_zero() -> None:
    """A row whose prediction sits at or below its lower bound gets no negative gain."""
    rows = cases()
    measured = measured_attainment(rows)
    ratio = mean_packing_ratio(measured)
    live = [row for row in rows if row["verdict"] != "foreclosed"]
    predicted = predicted_reach(live, ratio)
    assert predicted, "no live rows carried a best packing; the corpus changed shape"
    for row in predicted:
        assert row["predicted_gain"] == max(row["predicted"] - row["lower"], 0.0)
