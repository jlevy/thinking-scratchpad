#!/usr/bin/env python3
"""Every mass, atom count, and margin a result's prose quotes must match its own certificate.

`D-439`: three durable-record statements described "the top rung" and were left behind
when the ladder advanced past them -- every figure exact and real, each simply about the
wrong file. No existing check re-derives a result's quoted figures from the artifact it
names, so nothing caught any of the three until a line-by-line read did.

These tests reconstruct D-439's two in-scope instances as in-memory perturbations of the
live `T-019` record -- never edits to `results.yaml` itself, which stays a live record
other work is in flight against. The third instance, a third-party package's byte-identity
claim checked by a printed SHA-256, is a claim about file identity rather than a quoted
mass, atom count, or margin; this module reads no file hash and has no test claiming
otherwise, which is the honest account of what it covers.

`D-442` is the same failure one layer out: a ladder length, a runway figure, and a
superseded-by pointer, each describing a rung the ladder had climbed past, none of them
arithmetically wrong. Those reconstructions perturb `T-017` and `T-015` the same way.

Below those, under its own banner, is the *cross-record* contract `D-442` asked for: the
same rung is quoted in `results.yaml`, in `evidence.yaml`, in a case page's front matter,
in the generated reach table and in an agenda's cost prose, and it must agree in all of
them. Every figure in that half is recomputed from the artifact at test time -- a contract
with a rung's figures typed into it is one more record describing that rung, and would go
stale the same way the records it checks do.
"""

from __future__ import annotations

import copy
import json
import re
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from pathlib import Path

from devtools.check_rung_figures import (
    DEFECTS,
    EVIDENCE,
    RESULTS,
    CertificateFigures,
    certificate_consistency_problems,
    check_result,
    evidence_limitation_problems,
    fraction_decimal_problems,
    load_certificate,
    main,
    movement_problems,
    pick_retained,
    resolve_certificates,
    retained_pointer_problems,
    round_to,
    superseded_rung_problems,
)
from devtools.check_synopsis import spell
from devtools.render_certificate_reach import (
    covering_value_register,
    reported_covering_values,
)
from sqpack.yamlio import safe_load


def _result(result_id: str) -> dict:
    document = safe_load(RESULTS.read_text(encoding="utf-8"))
    return next(r for r in document["results"] if r["id"] == result_id)


def test_the_check_passes_on_the_retained_tree() -> None:
    assert main() == 0


def test_t019_control_has_no_disagreement() -> None:
    """The premise every perturbation below edits away from: today's record agrees."""
    problems, checked = check_result(_result("T-019"))
    assert problems == []
    assert checked == 3  # certificate.json (459/100) and the 229/50 and 451/100 rungs


def test_catches_d439_first_instance_the_movement_past_a_displaced_value() -> None:
    """D-439's first instance: the rationale gave the movement past Massaccesi as
    `0.0042` -- that is `451/100 - 22529/5000`, the *first* rung's own movement -- where
    the rung retained at the time (`229/50`) moved by `0.0742`. The live record now
    retains `459/100`, whose movement is `0.0842`, and states that; the reconstruction
    below perturbs whatever the record currently claims.
    """
    corrupted = copy.deepcopy(_result("T-019"))
    rationale = corrupted["significance"]["rationale"]
    assert "0.0842" in rationale, "premise: the live rationale states the retained movement"
    corrupted["significance"]["rationale"] = rationale.replace("0.0842", "0.0042")

    problems, _ = check_result(corrupted)
    assert len(problems) == 1
    assert "T-019 [significance.rationale]" in problems[0]
    assert "0.0042" in problems[0]
    assert "0.0842" in problems[0]


def test_catches_d439_second_instance_a_superseded_rungs_total_and_margin() -> None:
    """D-439's second instance: next_rung quoted the *first* rung's (`451/100`) total and
    margin -- `16.5936` and `0.406` -- as though they belonged to the retained
    certificate. The retained certificate is now `459/100`, total
    `423327/25000 = 16.933080` with margin `0.066920`; the reconstruction plants the
    superseded rung's figures over whatever the record currently states.
    """
    corrupted = copy.deepcopy(_result("T-019"))
    next_rung = corrupted["next_rung"]
    original = (
        "the retained certificate's total is 423327/25000 = 16.933080, "
        "leaving 0.066920 below seventeen"
    )
    assert original in next_rung, "premise: the live next_rung states the retained figures"
    corrupted["next_rung"] = next_rung.replace(
        original,
        "the retained certificate's total is 16.5936, leaving 0.406 below seventeen",
    )

    problems, _ = check_result(corrupted)
    assert len(problems) == 2
    joined = " | ".join(problems)
    assert "T-019 [next_rung]" in joined
    assert "total 16.5936" in joined
    assert "16.9331" in joined
    assert "margin 0.406" in joined
    assert "0.067 (exact" in joined  # 0.066920 rounded to the three places "0.406" states


def test_catches_a_bare_possessive_mass_after_the_top_rung_moves() -> None:
    """PR 80's F27: a total mass written possessively was read by none of the patterns.

    `T-019`'s own `next_rung` states the retained certificate's mass as "this
    certificate's ... reaching 17, 18 and 19 directly" -- no "total", no "is", and so
    invisible to every keyword the other patterns key on. That is D-439's own shape with
    the detector built for it looking straight past: put a superseded rung's mass in that
    slot and the sentence reads as true while describing the wrong file.

    Both figures are recomputed from the artifacts rather than written down, so this test
    cannot itself become the stale literal it exists to catch.
    """
    result = _result("T-019")
    retained, _, resolved = resolve_certificates(result)
    assert retained is not None
    superseded = next(figures for figures in resolved if figures.mass != retained.mass)

    current = f"this certificate's {round_to(retained.mass, 6)} reaching"
    next_rung = result["next_rung"]
    assert current in next_rung, "premise: the live next_rung states the retained mass"

    corrupted = copy.deepcopy(result)
    corrupted["next_rung"] = next_rung.replace(
        current, f"this certificate's {round_to(superseded.mass, 6)} reaching"
    )

    problems, _ = check_result(corrupted)
    assert len(problems) == 1
    assert "T-019 [next_rung]" in problems[0]
    assert f"prose says total {round_to(superseded.mass, 6)}" in problems[0]
    assert f"gives {round_to(retained.mass, 6)}" in problems[0]


def test_ignores_a_cross_referenced_rung_that_is_not_this_results_own() -> None:
    """T-019's own next_rung cites n = 12's ladder (`197/50`, `79/20`) for contrast;
    neither belongs to T-019's own artifacts, and a wrong-looking figure attached to one
    of them must not be compared against T-019's certificates -- a check that cries wolf
    on a cross-reference is worse than one that says nothing.
    """
    modified = copy.deepcopy(_result("T-019"))
    modified["next_rung"] += (
        " The 197/50 rung below this one has total 99.000000 and margin 99.000000."
    )
    problems, _ = check_result(modified)
    assert problems == []


def test_resolves_an_explicitly_named_secondary_rung() -> None:
    """A figure attached to `451/100` -- one of T-019's own three artifacts, not the
    retained one -- is checked against that certificate specifically."""
    t019 = _result("T-019")
    original = "The 451/100 rung two below this one has total 16.593620 and margin 0.406380"
    assert original in t019["next_rung"]
    modified = copy.deepcopy(t019)
    modified["next_rung"] = modified["next_rung"].replace(
        original,
        "The 451/100 rung below this one has total 1.000000 and margin 1.000000",
    )
    problems, _ = check_result(modified)
    assert len(problems) == 2
    assert all("certificate-451-100.json" in problem for problem in problems)


def test_repeating_the_same_rung_twice_does_not_trip_the_movement_gate() -> None:
    """The movement gate requires two *distinct* fraction-equals-decimal figures.

    A claim that restates one rung twice -- once for its own container side, once
    compared against a published packing -- names the same value, not a displaced prior
    one, and must not be read as a movement claim just because a `movement is` phrase
    sits elsewhere in the same result. The fake below is written out rather than lifted
    from a live result, whose claim is rewritten every time the ladder moves (`D-444`).
    """
    fake = {
        "id": "T-000",
        "claim": (
            "at container side 3/2 = 1.5. Separately, 3/2 = 1.5 exceeds a published value."
        ),
        "significance": {
            "rationale": "The movement is +9.000000, which nothing here supports."
        },
        "next_rung": "",
        "composition": "",
        "artifacts": [],
    }
    assert movement_problems(fake) == []


def test_movement_check_accepts_either_subtraction_order() -> None:
    """The check does not assume which of a claim's two figures is written first."""
    reversed_order = {
        "id": "T-000",
        "claim": "at container side 22529/5000 = 4.5058, displacing 229/50 = 4.58.",
        "significance": {"rationale": "The movement is -0.0742 relative to the prior value."},
        "next_rung": "",
        "composition": "",
        "artifacts": [],
    }
    assert movement_problems(reversed_order) == []


def test_catches_d442_a_ladder_that_grew_an_eighth_rung() -> None:
    """`D-442` at `T-017`: the rationale still called the ladder seven rungs and listed
    seven sides after the generator retained an eighth, `99/25`, which the same result's
    own artifact list already carried. The count comes from that list, never the prose."""
    corrupted = copy.deepcopy(_result("T-017"))
    corrupted["significance"]["rationale"] = corrupted["significance"]["rationale"].replace(
        "eight-rung ladder", "seven-rung ladder"
    )

    problems, _ = check_result(corrupted)
    assert len(problems) == 1
    assert "T-017 [significance.rationale]" in problems[0]
    assert "prose says 7 rungs in the ladder" in problems[0]
    assert "so it is 8" in problems[0]


def test_a_count_of_rungs_below_the_top_one_is_read_as_one_less() -> None:
    """The register writes the same fact in two shapes, and the ladder is the top rung
    plus everything under it: `T-017` retains eight and says seven are below."""
    corrupted = copy.deepcopy(_result("T-017"))
    corrupted["claim"] = "Eight rungs are retained below it."

    problems, _ = check_result(corrupted)
    assert len(problems) == 1
    assert "prose says 8 rungs below the retained one" in problems[0]
    assert "so it is 7" in problems[0]


def test_catches_d442_runway_measured_at_a_rung_the_ladder_climbed_past() -> None:
    """The figure that made this invisible: `0.0408` is exactly right for `79/20`, so
    nothing arithmetic objects. Runway is a claim about the top rung, and that is what
    the check holds."""
    corrupted = copy.deepcopy(_result("T-017"))
    corrupted["next_rung"] = "So the retained 79/20 has 0.0408 of runway left."

    problems, _ = check_result(corrupted)
    assert len(problems) == 1
    assert "prose measures runway at 79/20" in problems[0]
    assert "certificate-79-20.json" in problems[0]
    assert "the retained rung 99/25" in problems[0]


def test_runway_is_recomputed_from_the_certificates_own_ceiling() -> None:
    """`ceil(sqrt(n)) * B - L` from the retained certificate's own bytes: at `n = 12`
    the ceiling is `4B = 3.9908` and the retained `99/25` leaves `0.0308` under it."""
    corrupted = copy.deepcopy(_result("T-017"))
    corrupted["next_rung"] = "So the retained 99/25 has 0.0408 of runway left."

    problems, _ = check_result(corrupted)
    assert len(problems) == 1
    assert "prose says 0.0408 of runway" in problems[0]
    assert "leaves 0.0308 below ceil(sqrt(12)) * B" in problems[0]


def test_an_unqualified_runway_phrase_reads_the_retained_rung() -> None:
    """`T-019` writes one runway figure with no side at all, which means the retained
    rung -- the same default the margin patterns already use."""
    corrupted = copy.deepcopy(_result("T-019"))
    corrupted["next_rung"] = "For n = 17 the runway is 0.3000 to the ceiling."

    problems, _ = check_result(corrupted)
    assert len(problems) == 1
    assert "leaves 0.3985 below ceil(sqrt(17)) * B" in problems[0]


def test_catches_d442_a_superseded_by_naming_a_climbed_past_rung() -> None:
    """`D-442`'s cross-record shape: `T-015` and `T-016` both said `T-019` "certifies
    451/100", a real certificate of `T-019`'s and one it had already climbed past. No
    figure is wrong; only the other result's artifacts can settle which rung is meant."""
    corrupted = copy.deepcopy(_result("T-015"))
    corrupted["next_rung"] = corrupted["next_rung"].replace(
        "certifies 459/100", "certifies 451/100"
    )

    problems = superseded_rung_problems([corrupted, _result("T-019")])
    assert len(problems) == 1
    assert "says T-019 certifies 451/100" in problems[0]
    assert "certificate-451-100.json" in problems[0]
    assert "T-019's retained rung is 459/100" in problems[0]


def test_a_superseded_by_sentence_leaves_foreign_fractions_alone() -> None:
    """`22529/5000` is the displaced published value, not one of `T-019`'s rungs, and a
    check that guessed at it would cry wolf on every cross-reference."""
    probe = copy.deepcopy(_result("T-015"))
    probe["next_rung"] = "Superseded by T-019, which displaces 22529/5000 and 203/12."

    assert superseded_rung_problems([probe, _result("T-019")]) == []


def test_a_superseding_result_outside_the_register_is_refused() -> None:
    """A pointer to a result that does not exist is a broken record either way."""
    probe = copy.deepcopy(_result("T-015"))
    probe["next_rung"] = "Superseded as the verified lower bound by T-999."

    problems = superseded_rung_problems([probe])
    assert len(problems) == 1
    assert "names T-999 as superseding it" in problems[0]


def test_certificate_figures_are_recomputed_from_atoms_not_trusted_from_the_file() -> None:
    """The file's own stored `total_mass` is cross-checked, never substituted for the
    atom sum -- the whole point of a checker that re-derives from the rawest ground
    truth an artifact carries."""
    figures = CertificateFigures(
        path="synthetic",
        n=5,
        outer_side=Fraction(7, 2),
        square_side=Fraction(9977, 10000),
        atom_count=2,
        mass=Fraction(3, 2),
        stored_mass=Fraction(999, 100),
    )
    assert certificate_consistency_problems(figures) != []

    agreeing = copy.deepcopy(figures)
    object.__setattr__(agreeing, "stored_mass", Fraction(3, 2))
    assert certificate_consistency_problems(agreeing) == []


def test_a_non_certificate_artifact_is_silently_skipped(tmp_path: Path) -> None:
    """Most of a result's artifacts are generator or verifier modules, not certificates,
    and an unrelated JSON archive (an experiment record, say) must not be mistaken for
    one just because it happens to parse."""
    module = tmp_path / "colgen.py"
    module.write_text("x = 1\n")
    assert load_certificate(module) is None

    stray = tmp_path / "experiment.json"
    stray.write_text(json.dumps({"unrelated": "schema"}))
    assert load_certificate(stray) is None

    malformed = tmp_path / "malformed.json"
    malformed.write_text("{not valid json")
    assert load_certificate(malformed) is None

    assert load_certificate(tmp_path / "missing.json") is None


def test_retained_is_the_file_literally_named_certificate_json() -> None:
    """ "Retained" follows this repository's own naming convention (D-439's fix: the
    moving top-rung pointer is always `certificate.json`; a suffixed name is an
    immutable historical rung) rather than list position, so a result listing its
    artifacts out of order still resolves the right one as primary."""
    historical = CertificateFigures(
        path="cases/x/certificate-1-2.json",
        n=3,
        outer_side=Fraction(1, 2),
        square_side=Fraction(9977, 10000),
        atom_count=1,
        mass=Fraction(1, 2),
        stored_mass=None,
    )
    retained_figures = CertificateFigures(
        path="cases/x/certificate.json",
        n=3,
        outer_side=Fraction(7, 2),
        square_side=Fraction(9977, 10000),
        atom_count=1,
        mass=Fraction(3, 2),
        stored_mass=None,
    )

    # Historical rung listed first: retained must still win on its exact basename.
    assert pick_retained([historical, retained_figures]) is retained_figures
    assert pick_retained([retained_figures, historical]) is retained_figures

    # No file is literally named certificate.json: never read history as the current
    # rung. Two live pointers are ambiguous rather than settled by declaration order.
    assert pick_retained([historical]) is None
    assert pick_retained([]) is None
    assert pick_retained([retained_figures, retained_figures]) is None


def test_a_result_that_has_lost_its_live_pointer_is_refused() -> None:
    """F41: `pick_retained` used to fall back to the first resolved certificate, so a
    result whose `certificate.json` went missing would elect a historical rung as "the
    retained certificate" and check every unqualified figure against it. The immutable
    file agrees with whatever the prose said when the ladder was there, so the whole
    result would pass against the wrong artifact. The refusal names the missing path."""
    probe = copy.deepcopy(_result("T-019"))
    probe["artifacts"] = [
        artifact
        for artifact in probe["artifacts"]
        if not artifact.endswith("/certificate.json")
    ]

    retained, _, resolved = resolve_certificates(probe)
    assert retained is None
    assert len(resolved) == 2

    problems, checked = check_result(probe)
    assert checked == 2
    # The ladder count moves with the artifact list, so it objects too; the pointer
    # refusal is the one under test.
    pointer = [problem for problem in problems if "no live certificate.json" in problem]
    assert len(pointer) == 1
    assert pointer[0].startswith("T-019: no live certificate.json")
    assert "expected packing/cases/n17_fractional_certificate/certificate.json" in pointer[0]


def test_a_result_declaring_two_live_pointers_is_refused() -> None:
    """A second live basename is ambiguous, not a race the first declaration wins."""
    probe = copy.deepcopy(_result("T-021"))
    probe["artifacts"] = [
        artifact
        for artifact in probe["artifacts"]
        if artifact.endswith(("/certificate.json", "-193-40.json"))
    ]
    probe["artifacts"].append("packing/cases/n17_fractional_certificate/certificate.json")

    retained, _, resolved = resolve_certificates(probe)
    assert retained is None
    assert len(resolved) == 3

    problems, checked = check_result(probe)
    assert checked == 3
    pointer = [problem for problem in problems if "live certificate.json pointers" in problem]
    assert len(pointer) == 1
    assert pointer[0].startswith("T-021: declares 2 live certificate.json pointers")
    assert "exactly one is required" in pointer[0]


def _declared_pointers() -> frozenset[str]:
    """Every live `certificate.json` the register declares, as the checker computes it."""
    document = safe_load(RESULTS.read_text(encoding="utf-8"))
    return frozenset(
        artifact
        for result in document["results"]
        for artifact in result.get("artifacts", [])
        if isinstance(artifact, str) and artifact.endswith("/certificate.json")
    )


def test_every_certificate_bearing_result_has_its_live_pointer() -> None:
    """The premise the two refusals above edit away from, read off the live register.

    A result that produced a rung the register has since superseded satisfies it through
    its successor, which is the exception the next test pins.
    """
    document = safe_load(RESULTS.read_text(encoding="utf-8"))
    pointers = _declared_pointers()
    for result in document["results"]:
        _, _, resolved = resolve_certificates(result)
        assert retained_pointer_problems(result["id"], resolved, pointers) == []


def test_a_superseded_result_may_name_only_the_rung_it_produced() -> None:
    """When the pointer moves, the earlier result keeps its own artifact and no other.

    T-021 took `certificate.json` at n = 20 on 2026-09-05 and T-020's 24/5 rung was
    renamed beside it. Forcing T-020 to declare the successor's file would make every
    unqualified figure in its prose resolve against a certificate it did not produce --
    the failure this module exists to catch. The pointer must still have an owner: a
    historical-only result whose successor nobody declares is refused as before.
    """
    superseded = copy.deepcopy(_result("T-020"))
    assert [a for a in superseded["artifacts"] if a.endswith("/certificate.json")] == []
    _, _, resolved = resolve_certificates(superseded)
    assert resolved, "premise: T-020 still resolves the rung it produced"

    successor = "packing/cases/n20_fractional_certificate/certificate.json"
    assert successor in _declared_pointers(), "premise: T-021 declares the moved pointer"
    assert retained_pointer_problems("T-020", resolved, frozenset({successor})) == []

    orphaned = retained_pointer_problems("T-020", resolved, frozenset())
    assert len(orphaned) == 1
    assert orphaned[0].startswith("T-020: no live certificate.json")


def test_resolve_certificates_reads_real_repository_relative_artifacts() -> None:
    """The path-resolution half of certificate lookup, exercised against a real result:
    `resolve_certificates` reads exactly the artifacts a result names, repository-relative,
    and nothing outside the repository."""
    retained, sides, resolved = resolve_certificates(_result("T-019"))
    assert retained is not None
    assert retained.path == "packing/cases/n17_fractional_certificate/certificate.json"
    assert Fraction(451, 100) in sides
    assert len(resolved) == 3


def test_repo_wide_fraction_equals_decimal_catches_wrong_arithmetic() -> None:
    """The mechanical check is generic text scanning, not tied to results.yaml's schema:
    any `a/b = d.ddd` anywhere must be true to the precision written."""
    problems = fraction_decimal_problems("the total is 1/4 = 0.30", "synthetic")
    assert len(problems) == 1
    assert "1/4 = 0.30 is wrong" in problems[0]
    assert fraction_decimal_problems("the total is 1/4 = 0.25", "synthetic") == []


def test_the_repo_wide_scan_covers_evidence_and_defects_too() -> None:
    """This is repository-wide value, not just for results: the same pattern recurs in
    `evidence.yaml` and `defects.yaml` (D-439's own fix restates the corrected total in
    the latter), and the mechanical check applies there identically."""
    for path, label in ((EVIDENCE, "evidence.yaml"), (DEFECTS, "defects.yaml")):
        assert fraction_decimal_problems(path.read_text(encoding="utf-8"), label) == []


# ---------------------------------------------------------------------------------------
# The cross-record contract.
#
# `D-442`: one rung is quoted in many records -- `results.yaml`, `evidence.yaml`, a case's
# front matter, the generated reach table, an agenda's cost prose -- and the detector above
# reads only the first of them. A figure left behind in any of the others is the same
# defect at a surface nothing recomputes.
#
# Every figure below is recomputed here, at test time, from the artifact the record points
# at. That is not a style preference. A contract written with a rung's figures typed into
# it is itself a record describing that rung, and the next time the ladder moves it becomes
# an instance of the defect it was built to catch.
# ---------------------------------------------------------------------------------------

REPO = RESULTS.parents[2]
PACKING = RESULTS.parents[1]
CASES = PACKING / "cases"
REACH = RESULTS.parent / "CERTIFICATE-REACH.md"
AGENDA_019 = (
    PACKING / "campaign/agendas/agenda-019-efficiency-first-retarget-and-deep-strategy.md"
)

#: `spell(7) == "seven"`, inverted, so a count written as a word reads as the number it is.
#: Borrowed from `check_synopsis` rather than retyped: this repository's prose spells its
#: counts one way, and a second table of number words is a second thing to keep in step.
_NUMBER_WORDS = {spell(value).lower(): value for value in range(100)}


def _stated_number(text: str) -> Decimal | None:
    """A count or multiple as prose writes it: `1.8`, `7`, or `seven`."""
    word = _NUMBER_WORDS.get(text.strip().lower())
    if word is not None:
        return Decimal(word)
    try:
        return Decimal(text)
    except InvalidOperation:
        return None


def _places(figure: str) -> int:
    """How many decimal places a figure was written to, which is how it is compared."""
    return len(figure.split(".", 1)[1]) if "." in figure else 0


def _figures(repo_relative: str) -> CertificateFigures:
    """One certificate's figures, recomputed from its own atoms, never a stored summary."""
    figures = load_certificate(REPO / repo_relative)
    assert figures is not None, f"{repo_relative} does not parse as a weighted certificate"
    return figures


def _evidence(evidence_id: str) -> dict:
    document = safe_load(EVIDENCE.read_text(encoding="utf-8"))
    return next(e for e in document["evidence"] if e["id"] == evidence_id)


def _evidence_by_id() -> dict[str, dict]:
    document = safe_load(EVIDENCE.read_text(encoding="utf-8"))
    return {entry["id"]: entry for entry in document["evidence"]}


def _front_matter(path: Path) -> dict:
    """One case page's `packing` block, from the YAML between its first two `---` lines."""
    _, frontmatter, _ = path.read_text(encoding="utf-8").split("---", 2)
    return safe_load(frontmatter)["packing"]


def _retained_certificates() -> dict[str, CertificateFigures]:
    """Every certificate the case packages retain, by repository-relative path.

    Both the moving top-rung pointers and the historical rungs beside them: a rung a
    later result superseded is still retained, still replayable by name, and still the
    artifact whichever record quoted its figures was quoting. Reading only the pointers
    made a durable record go stale the moment the pointer moved -- agenda-020's measured
    "2260 atoms" is the 24/5 rung's, and that rung did not change when T-021 took
    `certificate.json` at n = 20 on 2026-09-05.
    """
    return {
        (relative := path.relative_to(REPO).as_posix()): _figures(relative)
        for path in sorted(CASES.glob("n*_fractional_certificate/certificate*.json"))
    }


def _declared_artifacts() -> set[str]:
    document = safe_load(RESULTS.read_text(encoding="utf-8"))
    return {
        artifact
        for result in document["results"]
        for artifact in result.get("artifacts", [])
        if isinstance(artifact, str)
    }


def test_the_reach_tables_reported_values_carry_their_own_artifacts_figures() -> None:
    """`CERTIFICATE-REACH.md`'s covering-value table, recomputed by a second implementation.

    The renderer already reads each frozen artifact rather than quoting it by hand, and
    `--check` already refuses a stale file. What this adds is the cross-record half: the
    same masses and atom counts come out of `check_rung_figures`'s own independent loader,
    and every artifact the table stands a reported value beside is one that a result in
    `results.yaml` actually declares.
    """
    text = REACH.read_text(encoding="utf-8")
    declared = _declared_artifacts()
    register = covering_value_register()
    rendered = reported_covering_values()
    assert len(rendered) == len(register)

    with_artifacts = 0
    for entry, row in zip(register, rendered, strict=True):
        assert row["side"] == entry["side_decimal"]
        assert (
            f"| {row['n']} | {row['side']} | {row['site_set']} | {row['reported']} | "
            f"{'yes' if row['converged'] else 'no'} | {row['stop_reason']} | "
            f"{row['evidence']} |"
        ) in text
        artifact = entry["frozen_artifact"]
        if artifact is None:
            continue
        with_artifacts += 1
        assert artifact in declared, f"{artifact} is declared by no result"
        figures = _figures(artifact)
        assert f"{figures.atom_count:,}-atom" in row["evidence"]
        assert str(round_to(figures.mass, 6)) in row["evidence"]
    assert with_artifacts, "premise: some reported value has a frozen artifact beside it"


def test_the_reach_table_states_how_many_values_it_lists() -> None:
    """The count its prose spells is the number of rows it renders."""
    text = REACH.read_text(encoding="utf-8")
    rows = [line for line in text.splitlines() if re.match(r"^\| \d+ \| \d+\.\d+ \| ", line)]
    assert len(rows) == len(covering_value_register())
    sides = {row["side"] for row in reported_covering_values()}
    assert re.search(
        rf"\b(?:{len(rows)}|{spell(len(rows))}) restricted optima\s+have been reported at "
        rf"(?:{len(sides)}|{spell(len(sides))}) sides\b",
        text,
        re.IGNORECASE,
    )


def test_every_case_page_binds_the_certificate_its_own_evidence_names() -> None:
    """A case's front-matter bound is the container side of one of its own certificates.

    `D-442`'s surface, contracted rather than spot-checked. For every case page whose
    verified lower bound cites an evidence entry carrying a certificate, exactly one of
    those certificates has that bound as its container side, and that certificate's
    recomputed mass is strictly below this case's own `n` -- which is what makes it a
    certificate *about this case* rather than one quoted from a neighbour.
    """
    evidence = _evidence_by_id()
    interval = _evidence("E-fractional-interval-decision")
    expected = {int(value) for value in interval["scope"]["n_values"]}

    bound: set[int] = set()
    for path in sorted(RESULTS.parent.glob("n-*.md")):
        packing = _front_matter(path)
        lower = packing.get("verified_lower_bound") or {}
        # Keyed by path: two entries may cite the same file (n = 11's own certificate is
        # named by both its primary entry and the interval decision), and one file is one
        # certificate however many records point at it.
        cited = {
            figures.path: figures
            for citation in lower.get("evidence") or []
            if (declared := (evidence.get(citation) or {}).get("certificate"))
            and (figures := load_certificate(PACKING / declared)) is not None
        }
        if not cited:
            continue
        n = int(packing["n"])
        side = Fraction(str(lower["exact_form"]))
        matching = [figures for figures in cited.values() if figures.outer_side == side]
        assert len(matching) == 1, f"n = {n}: {len(matching)} cited certificates at {side}"
        assert matching[0].mass < n, f"n = {n}: {matching[0].path} does not certify it"
        bound.add(n)

    # Non-vacuity, itself derived: every case the interval decision declares in its own
    # scope must be bound this way, so the contract cannot quietly empty out.
    assert bound == expected


def test_t017s_ladder_is_the_ladder_the_case_package_actually_retains() -> None:
    """The rung count and the enumerated sides come from the case directory, not the prose.

    PR 80 wrote "Eight rungs are retained" into the contract as a literal. Eight is the
    number of certificate files `cases/n12_fractional_certificate/` holds, and reading it
    from there is what keeps the contract true after the ninth.
    """
    sides = sorted(
        _figures(path.relative_to(REPO).as_posix()).outer_side
        for path in CASES.glob("n12_fractional_certificate/certificate*.json")
    )
    retained = _figures("packing/cases/n12_fractional_certificate/certificate.json")
    assert sides[-1] == retained.outer_side, "the retained pointer is the ladder's top rung"

    result = _result("T-017")
    ladder = re.search(r"the ladder ((?:\d+/\d+, )+\d+/\d+) was climbed", result["next_rung"])
    assert ladder is not None, "premise: next_rung enumerates the ladder"
    assert [Fraction(token) for token in ladder.group(1).split(", ")] == sides

    below = re.search(
        r"(\w+) rungs are retained below it, (\d+/\d+) through (\d+/\d+)", result["claim"]
    )
    assert below is not None, "premise: the claim counts the rungs below the retained one"
    assert _stated_number(below.group(1)) == Decimal(len(sides) - 1)
    assert Fraction(below.group(2)) == sides[0]
    assert Fraction(below.group(3)) == sides[-2]


def test_t017s_retained_figures_are_the_retained_certificates_own() -> None:
    """The claim, the artifact list and the primary evidence entry all name one file."""
    retained = _figures("packing/cases/n12_fractional_certificate/certificate.json")
    record = json.loads((REPO / retained.path).read_text(encoding="utf-8"))

    result = _result("T-017")
    assert record["claim"] in result["claim"]
    resolved, _, _ = resolve_certificates(result)
    assert resolved is not None
    assert resolved.path == retained.path

    primary = _evidence("E-n012-fractional-certificate")
    assert (PACKING / primary["certificate"]).resolve() == (REPO / retained.path).resolve()
    total = f"{retained.mass.numerator}/{retained.mass.denominator}"
    assert f"{total} = {round_to(retained.mass, 6)}" in result["next_rung"]


def test_t017s_quoted_multiples_are_recomputed_from_the_artifacts_they_compare() -> None:
    """Two "about N times" claims, each derived from the pair of artifacts it is about.

    PR 80 wrote these as "about 6.9 times tighter" and "about 1.77 times" -- figures that
    are neither what the record says nor recoverable from what it says. Both are ratios
    between two retained artifacts, so both are computed here from those artifacts and
    compared to the prose through `round_to`, at the precision the prose itself wrote.
    """
    next_rung = _result("T-017")["next_rung"]
    retained = _figures("packing/cases/n12_fractional_certificate/certificate.json")

    wider = re.search(
        r"next tightest,[^.]*?at (\d+)/(\d+),\s*is about ([\w.]+) times wider", next_rung
    )
    assert wider is not None, "premise: next_rung compares the retained margin to another"
    other = _figures(
        f"packing/cases/n12_fractional_certificate/certificate-{wider[1]}-{wider[2]}.json"
    )
    stated = _stated_number(wider.group(3))
    assert stated is not None, f"unreadable multiple {wider.group(3)!r}"
    assert round_to(other.margin / retained.margin, _places(str(stated))) == stated

    # The second multiple sizes this rung against another retained certificate by atom
    # count. Both counts and the multiple between them are recomputed; the sentence's
    # "next largest" is not, because it ranks the register as it stood when this rung was
    # retained -- n = 20's 2,260-atom rung has since passed it -- and a superlative about
    # a past moment is history rather than a figure an artifact can still settle.
    times = re.search(
        r"(\d[\d,]*) atoms is ([\d.]+) times [^.]*?the (\d[\d,]*)-atom n = (\d+) rung",
        next_rung,
    )
    assert times is not None, "premise: next_rung sizes this rung against another"
    assert int(times.group(1).replace(",", "")) == retained.atom_count
    compared = _figures(
        f"packing/cases/n{int(times.group(4)):02d}_fractional_certificate/certificate.json"
    )
    assert int(times.group(3).replace(",", "")) == compared.atom_count
    ratio = Fraction(retained.atom_count, compared.atom_count)
    assert round_to(ratio, _places(times.group(2))) == Decimal(times.group(2))


def test_the_independent_verifier_entry_names_the_side_it_does_not_decide() -> None:
    """A historical entry's disclaimer moves with the pointer it disclaims.

    `E-n012-independent-verifier` decides two historical rungs, and says so by naming the
    current side it does *not* decide. That side is the retained certificate's, so the
    sentence goes stale the moment the ladder climbs unless it is read against it.
    """
    retained = _figures("packing/cases/n12_fractional_certificate/certificate.json")
    historical = _evidence("E-n012-independent-verifier")
    checked = _figures(f"packing/{historical['certificate']}")
    assert checked.path != retained.path
    assert checked.outer_side < retained.outer_side
    disclaimer = f"does not decide the current {retained.outer_side} bytes"
    assert disclaimer in historical["limitations"]


def test_an_evidence_entrys_limitations_are_read_against_the_certificate_it_names() -> None:
    """`D-451`: the entry pointed at `certificate.json` and described the file it used to.

    The perturbation is the defect exactly as it stood -- 681 atoms, the atom count of the
    `197/50` rung the pointer named before the ladder climbed to `99/25` -- planted over
    whatever the live entry now says, so the control cannot go stale into agreement.
    """
    entry = copy.deepcopy(_evidence("E-n012-fractional-certificate"))
    assert evidence_limitation_problems(entry) == []

    retained = _figures("packing/cases/n12_fractional_certificate/certificate.json")
    superseded = _figures("packing/cases/n12_fractional_certificate/certificate-197-50.json")
    current = f"carries {retained.atom_count:,} atoms"
    assert current in entry["limitations"], "premise: the entry states its own atom count"
    entry["limitations"] = entry["limitations"].replace(
        current, f"carries {superseded.atom_count:,} atoms"
    )

    problems = evidence_limitation_problems(entry)
    assert len(problems) == 1
    assert "E-n012-fractional-certificate [limitations]" in problems[0]
    assert f"{superseded.atom_count} atoms" in problems[0]
    assert str(retained.atom_count) in problems[0]


def test_a_limitations_sentence_ranging_over_other_rungs_is_left_unchecked() -> None:
    """The anchoring rule, at the entry that would otherwise cry wolf four times.

    `E-fractional-interval-decision` declares one certificate and reports the atom counts
    of four different top rungs in a single sentence. Three of them are about files it does
    not declare, and a check that compared them to the one it does would report three
    disagreements where the record is right.
    """
    entry = _evidence("E-fractional-interval-decision")
    declared = _figures(f"packing/{entry['certificate']}")
    others = {
        figures.atom_count
        for figures in _retained_certificates().values()
        if figures.path != declared.path
    }
    quoted = {int(match) for match in re.findall(r"(\d+) atoms\b", entry["limitations"])}
    assert quoted & others, "premise: the entry quotes atom counts of rungs it does not name"
    assert evidence_limitation_problems(entry) == []


def test_the_agenda_quotes_atom_counts_the_retained_certificates_have() -> None:
    """Agenda prose is a durable record too, and it costs its plans in atom counts.

    PR 80 pinned one sentence of it as "2097 atoms took 4866 s". The seconds are a wall
    time from a run whose transcript was never retained, and nothing here can recompute
    them; the atom count is an artifact's, and every atom count the agenda quotes is
    checked here against the certificates the register actually holds.
    """
    counts = {figures.atom_count for figures in _retained_certificates().values()}
    text = AGENDA_019.read_text(encoding="utf-8")
    quoted = {int(match.replace(",", "")) for match in re.findall(r"(\d[\d,]*) atoms\b", text)}
    assert quoted, "premise: the agenda costs its plans in atom counts"
    assert quoted <= counts, f"no retained certificate has {sorted(quoted - counts)} atoms"
