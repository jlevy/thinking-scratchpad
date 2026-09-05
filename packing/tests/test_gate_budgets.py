"""The gate's cost check, held to the standard the gate holds everything else to.

A detector nobody has watched fire is not a detector. `run_negative_controls` makes that
argument for the record checks; these make it for the timing check, and they make it
twice -- once for the declaration, which needs no clock, and once for a finished run.

**No test here writes a number it wants the live check to agree with.** Every figure is
read back out of `devtools/gate-budgets.yaml` and scaled by the policy's own ratios,
because a test that pinned `1369.60` would rot on the day the tier changed -- which is
exactly how the docstring this mechanism replaces came to be wrong. Where a test needs a
declaration the live register does not have, it fabricates a whole one in `tmp_path`, the
way `test_control_anchors` fabricates a control spec.

The one place literal seconds appear is the 2026-08-30 replay, whose numbers are the
incident itself: 499 seconds recorded beside an 1800 second cap.
Those are history and cannot drift.
"""

# Reaching for `_parser`, `_tier_id` and `_render_text` is the point: a test that
# reimplemented any of them would drift from the CLI it checks, which is the failure this
# file exists to prevent. `devtools/check_declared_commands.py` takes the same exemption.
# pyright: reportPrivateUsage=false
from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from devtools.check_gate_budgets import coverage_problems
from sqpack import gate_budgets
from sqpack.cli import validate
from sqpack.gate_budgets import BudgetError, Register, TierBudget

LIVE = gate_budgets.BUDGETS
SLOW_STEP = "a step that got slower"
CHEAP_STEP = "a step that did not"


def live() -> Register:
    return gate_budgets.load(LIVE)


def fabricated(
    tmp_path: Path, *, ceiling: float, measured: str, date: str = "'2026-08-30'"
) -> Path:
    """A whole register in `tmp_path`, so a test can declare what it needs to refuse."""
    spec = tmp_path / "gate-budgets.yaml"
    spec.write_text(
        "policy:\n"
        "  max_headroom: 2.0\n"
        "  drift_ratio: 1.5\n"
        "  stale_ratio: 0.6\n"
        "  min_wall_seconds: 20.0\n"
        "tiers:\n"
        "- id: fast\n"
        "  command: packing-validate --fast\n"
        f"  ceiling_seconds: {ceiling}\n"
        f"  measured_seconds: {measured}\n"
        f"  measured_on: {date}\n"
        "  measured_where: a fabricated register\n"
        "  reference: {jobs: 2, inner_jobs: 1, cpus: 2}\n"
        "  argument: a fabricated register\n",
        encoding="utf-8",
    )
    return spec


def recorded_tier(register: Register) -> TierBudget:
    """A tier with a cost on record, for the rules that need something to compare to.

    The register can legitimately carry none: a tier whose composition just changed has no
    valid record until the next run at its reference shape takes one. When that is the
    case the tier's own ceiling stands in, divided by the loosest headroom the policy
    allows -- still the register's arithmetic, still no figure typed here.
    """
    for tier in register.tiers:
        if tier.measured_seconds is not None:
            return tier
    tier = register.tiers[0]
    return replace(
        tier,
        measured_seconds=tier.ceiling_seconds / register.policy.max_headroom,
        measured_on="(no tier carries a record; synthesised from this tier's ceiling)",
    )


def judge_at_reference(
    register: Register,
    tier: TierBudget,
    steps: tuple[tuple[str, float], ...],
) -> gate_budgets.Verdict:
    """Judge a synthetic run on the tier's own reference shape, so the band is enforced."""
    return gate_budgets.judge(
        with_tier(register, tier),
        tier.id,
        wall_seconds=sum(seconds for _, seconds in steps),
        steps=steps,
        jobs=tier.reference.jobs,
        inner_jobs=tier.reference.inner_jobs,
        cpus=tier.reference.cpus,
    )


def with_tier(register: Register, tier: TierBudget) -> Register:
    """The live register with one tier replaced, so a stand-in record is the one judged."""
    return replace(
        register,
        tiers=tuple(tier if other.id == tier.id else other for other in register.tiers),
    )


def test_the_live_declaration_is_internally_consistent() -> None:
    """Rule 2, against the register as checked in. This is the records-tier step."""
    assert gate_budgets.declaration_problems(live()) == []


def test_every_selectable_tier_declares_a_ceiling() -> None:
    """A tier with no ceiling is a tier that can triple, which is the whole incident."""
    assert set(live().ids) == set(validate.TIER_IDS)


def test_a_tier_without_a_ceiling_is_refused(tmp_path: Path) -> None:
    """The coverage rule has to bite; one that only ever passes proves nothing."""
    head, _, _ = LIVE.read_text(encoding="utf-8").partition("- id: fast")
    spec = tmp_path / "gate-budgets.yaml"
    spec.write_text(head, encoding="utf-8")
    problems = coverage_problems(gate_budgets.load(spec))
    assert any("fast" in problem for problem in problems), problems


def test_the_2026_08_30_declaration_would_have_been_refused(tmp_path: Path) -> None:
    """The incident, replayed.

    On 2026-08-30 `--fast` was measured at 499s and capped at 1800s. Six days later it
    cost 1369.60s and passed, because 1370 is inside 1800. The declaration itself is what
    was wrong: 3.61x of headroom cannot see a 2.65x regression, and no clock is needed to
    notice that.
    """
    register = gate_budgets.load(fabricated(tmp_path, ceiling=1800.0, measured="499.0"))
    problems = gate_budgets.declaration_problems(register)
    assert any("headroom" in problem for problem in problems), problems
    # And the ceiling it prints is one the 1369.60s run of six days later would have failed.
    assert any("998" in problem for problem in problems), problems

    tightened = replace(register.tiers[0], ceiling_seconds=998.0)
    verdict = judge_at_reference(
        replace(register, tiers=(tightened,)),
        tightened,
        (("fast behavioral tests", 1324.0), ("every other fast step", 45.6)),
    )
    assert verdict.failed, verdict
    assert any("fast behavioral tests" in reason for reason in verdict.failures), verdict


def test_a_slowed_step_fails_the_check_and_is_named() -> None:
    """Negative control one: deliberately slow a step, and the run must fail for it.

    The slow step is given the tier's whole ceiling, so the run is over by construction
    whatever the ceiling happens to be, and no seconds figure is written here.
    """
    register = live()
    tier = recorded_tier(register)
    steps = ((SLOW_STEP, tier.ceiling_seconds), (CHEAP_STEP, register.policy.min_wall_seconds))
    verdict = judge_at_reference(register, tier, steps)

    assert verdict.failed, verdict
    assert verdict.enforced
    assert any(SLOW_STEP in reason for reason in verdict.failures), verdict.failures
    assert any("ceiling" in reason for reason in verdict.failures), verdict.failures


def test_a_run_inside_the_band_passes_without_a_figure_in_the_assertion() -> None:
    """Negative control two: the check must not simply always fire.

    The synthetic run costs exactly what the register says the tier costs, split across
    two steps. Every number comes out of the register; none is typed here, so this test
    cannot rot into agreeing with a stale figure.
    """
    register = live()
    tier = recorded_tier(register)
    recorded = tier.measured_seconds
    assert recorded is not None
    steps = ((SLOW_STEP, recorded * 0.9), (CHEAP_STEP, recorded * 0.1))
    verdict = judge_at_reference(register, tier, steps)

    assert verdict.failures == (), verdict.failures
    assert verdict.status == "passed", verdict


def test_the_drift_rule_fires_while_the_run_is_still_inside_the_ceiling() -> None:
    """The rule that catches a regression against a cap the run never reaches.

    A ceiling alone did not catch the incident: 1370s is inside 1800s. Drift against the
    tier's own record is what does. The tier here is given the loosest ceiling the policy
    still allows -- exactly `max_headroom` times its record, the worst declaration that can
    pass the static check -- and the run is then placed between the drift ratio and that
    ceiling, which is where the 2026-09-05 run sat.
    """
    register = live()
    tier = recorded_tier(register)
    recorded = tier.measured_seconds
    assert recorded is not None
    policy = register.policy
    loosest = replace(tier, ceiling_seconds=recorded * policy.max_headroom)
    assert gate_budgets.declaration_problems(with_tier(register, loosest)) == [], (
        "the loosest ceiling the policy allows must still be a legal declaration"
    )

    midpoint = (policy.drift_ratio + policy.max_headroom) / 2
    steps = ((SLOW_STEP, recorded * midpoint),)
    verdict = judge_at_reference(register, loosest, steps)

    assert verdict.wall_seconds < loosest.ceiling_seconds, "the run stayed inside the cap"
    assert verdict.failed, verdict
    assert any("recorded" in reason for reason in verdict.failures), verdict.failures
    assert any(SLOW_STEP in reason for reason in verdict.failures), verdict.failures


def test_a_record_the_tier_has_outgrown_downward_fails_and_prints_the_new_figure() -> None:
    """The other direction, which is how the 499 became prose in the first place.

    A record bounded only from above rots downward: the tier gets faster, nobody updates
    it, and the ratio rules stop meaning anything. So a run far enough under the record
    fails too, and names the value to write.
    """
    register = live()
    tier = recorded_tier(register)
    recorded = tier.measured_seconds
    assert recorded is not None
    wall = recorded * register.policy.stale_ratio / 2
    verdict = judge_at_reference(register, tier, ((SLOW_STEP, wall),))

    assert verdict.failed, verdict
    assert any("stale" in reason for reason in verdict.failures), verdict.failures
    assert any(f"{wall:.1f}" in reason for reason in verdict.failures), verdict.failures


def test_an_unmeasured_tier_prints_the_line_that_would_arm_the_drift_rule() -> None:
    """A tier with no record is the state a composition change leaves behind.

    Nobody has to remember to take the measurement: the first run at the reference shape
    prints the exact line to paste, and until then the absolute ceiling still applies.
    """
    register = live()
    unmeasured = next((tier for tier in register.tiers if tier.measured_seconds is None), None)
    if unmeasured is None:
        pytest.skip("every tier currently carries a record")
    wall = unmeasured.ceiling_seconds / 2
    verdict = judge_at_reference(register, unmeasured, ((CHEAP_STEP, wall),))

    assert not verdict.failed, verdict
    assert any(f"measured_seconds: {wall:.1f}" in note for note in verdict.notes), verdict


def test_a_scoped_run_is_not_judged_against_a_whole_tier() -> None:
    """`--only` is a slice, and a slice finishing fast says nothing about the tier."""
    register = live()
    tier = recorded_tier(register)
    verdict = gate_budgets.judge(
        register,
        None,
        wall_seconds=tier.ceiling_seconds * 2,
        steps=((SLOW_STEP, tier.ceiling_seconds * 2),),
        jobs=tier.reference.jobs,
        inner_jobs=tier.reference.inner_jobs,
        cpus=tier.reference.cpus,
    )
    assert verdict.status == "unknown"
    assert not verdict.failed


def test_a_run_off_the_reference_shape_reports_instead_of_failing() -> None:
    """Wall time is not comparable across machines.

    A check that fails on a slow runner is a check people turn off, so an unmatched shape
    prints the same sentence and does not fail. `--enforce-budget` overrides that for an
    operator who means it.
    """
    register = live()
    tier = recorded_tier(register)
    steps = ((SLOW_STEP, tier.ceiling_seconds * 2),)
    elsewhere = {
        "wall_seconds": steps[0][1],
        "steps": steps,
        "jobs": tier.reference.jobs,
        "inner_jobs": tier.reference.inner_jobs,
        "cpus": tier.reference.cpus + 1,
    }
    reported = gate_budgets.judge(with_tier(register, tier), tier.id, **elsewhere)
    assert reported.status == "reported"
    assert not reported.failed
    assert any(SLOW_STEP in note for note in reported.notes), reported.notes

    forced = gate_budgets.judge(with_tier(register, tier), tier.id, force=True, **elsewhere)
    assert forced.failed, forced


def test_a_register_that_records_a_cost_without_a_date_is_refused(tmp_path: Path) -> None:
    """A measurement nobody can place cannot be re-taken, so it is not a measurement."""
    with pytest.raises(BudgetError, match="date"):
        gate_budgets.load(fabricated(tmp_path, ceiling=1800.0, measured="499.0", date="null"))


def test_every_boolean_flag_is_classified_as_a_tier_or_not() -> None:
    """A new tier flag must not be able to arrive without a ceiling.

    `TIER_IDS` is what `devtools.check_gate_budgets` compares the register against, so a
    tier flag missing from it would run with no declared cost and nothing would say so.
    Every `store_true` option on the parser is therefore either a tier or named here as
    deliberately not one.
    """
    not_a_tier = {"strict", "deep", "list", "budgets", "enforce_budget"}
    # A `store_true` flag is exactly one that defaults to False in the parsed namespace,
    # which reads the real parser without reaching into argparse's internals.
    defaults = vars(validate._parser().parse_args([]))
    booleans = {name for name, value in defaults.items() if value is False}
    unclassified = booleans - set(validate.TIER_FLAGS) - not_a_tier
    assert unclassified == set(), (
        f"{sorted(unclassified)} is neither a tier in TIER_FLAGS nor listed as not one; "
        "a tier with no entry in gate-budgets.yaml runs with no declared ceiling"
    )


def test_the_tier_of_an_invocation_is_always_one_the_register_declares() -> None:
    """Whatever `_tier_id` names, the register must have a ceiling for it."""
    declared = set(live().ids)
    for flags in (
        [],
        ["--records"],
        ["--edit"],
        ["--fast"],
        ["--push"],
        ["--records", "--fast"],
    ):
        namespace = validate._parser().parse_args(flags)
        tier = validate._tier_id(namespace)
        assert tier in declared, (flags, tier)
    scoped = validate._parser().parse_args(["--only", "lint"])
    assert validate._tier_id(scoped) is None


def test_a_run_over_its_ceiling_fails_the_command_even_with_every_step_green(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The seam between the verdict and the process exit code.

    Every step passes and the command still returns 1, because the tier cost more than it
    is allowed to. That is the whole behavioural difference from the docstring this
    replaces: a number the run acts on rather than one a reader might notice.
    """
    register = live()
    tier = recorded_tier(register)
    steps = ((SLOW_STEP, tier.ceiling_seconds), (CHEAP_STEP, register.policy.min_wall_seconds))
    summary = validate.RunSummary(
        results=[
            validate.StepResult(name=name, status="passed", seconds=seconds)
            for name, seconds in steps
        ],
        wall_seconds=sum(seconds for _, seconds in steps),
        selected_count=len(steps),
        total_count=len(steps),
        budget=judge_at_reference(register, tier, steps),
    )
    assert validate._render_text(summary, strict=False) == 1
    printed = capsys.readouterr().out
    assert "THE TIER IS OUTSIDE ITS DECLARED COST BAND" in printed
    assert SLOW_STEP in printed
