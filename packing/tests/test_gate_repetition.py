#!/usr/bin/env python3
"""What the repeated-work measurement is allowed to claim, and what it must refuse.

`BC-215`. The number this module produces is an argument for skipping work, so the ways
it can be wrong are the ways coverage gets lost: a step priced at zero repeats for free,
a schedule read as daily when it is not puts the wrong count of runs in the denominator,
and reading `touches` as a skip map rather than a selection map inverts which direction
is safe. Each of those is a refusal in `devtools.measure_gate_repetition`, and each of
them is asserted here.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from devtools.measure_gate_repetition import (
    MeasurementError,
    Trigger,
    attribution_reach,
    changed_between,
    daily_schedule_utc,
    load_prices,
    measure,
    merge_identity,
    repetition_for_changes,
    schedule_triggers,
)
from sqpack.campaign import ledger
from sqpack.cli.validate import STEPS

TRIGGER = Trigger(kind="push", when=datetime(2026, 9, 5, tzinfo=UTC), commit="beef")
#: A short window for the two tests that walk the real graph. `DEFAULT_DAYS` is the
#: reporting window; here the point is that the path works, and each extra day costs
#: git calls that would push these toward the quick lane's per-test ceiling on a
#: slower runner for no extra assurance.
WALK_DAYS = 14


def _summary(
    path: Path,
    prices: dict[str, float],
    *,
    skipped: tuple[str, ...] = (),
    failed: tuple[str, ...] = (),
) -> Path:
    def status(name: str) -> str:
        if name in skipped:
            return "skipped"
        return "failed" if name in failed else "passed"

    path.write_text(
        json.dumps(
            {
                "results": [
                    {"name": name, "status": status(name), "seconds": seconds}
                    for name, seconds in prices.items()
                ],
                "wall_seconds": sum(prices.values()),
            }
        ),
        encoding="utf-8",
    )
    return path


def _unit_prices() -> dict[str, float]:
    return {step.name: 1.0 for step in STEPS}


def test_a_step_the_summary_does_not_price_is_refused(tmp_path: Path) -> None:
    """A missing price is a step that repeats for free, which is the flattering error."""
    prices = _unit_prices()
    dropped = STEPS[0].name
    del prices[dropped]
    path = _summary(tmp_path / "run.json", prices)
    with pytest.raises(MeasurementError, match="prices no step named"):
        load_prices([path])


def test_a_price_for_a_step_that_no_longer_exists_is_refused(tmp_path: Path) -> None:
    """A summary that predates the gate makes every other price in it suspect."""
    prices = _unit_prices() | {"a step this gate has never had": 3.0}
    path = _summary(tmp_path / "run.json", prices)
    with pytest.raises(MeasurementError, match="not a step this gate declares"):
        load_prices([path])


def test_a_skipped_step_is_not_a_price(tmp_path: Path) -> None:
    """A skipped step costs nothing and says nothing about what it costs when it runs."""
    skipped = STEPS[0].name
    path = _summary(tmp_path / "run.json", _unit_prices(), skipped=(skipped,))
    with pytest.raises(MeasurementError, match="recorded seconds are not its cost"):
        load_prices([path])
    assert load_prices([path], allow_unhealthy=True)[skipped] == 1.0


def test_a_failed_step_is_not_a_price_either(tmp_path: Path) -> None:
    """The one this module's own first run needed. A failure can be an early abort: the
    2026-09-05 deep run recorded `negative controls` at 416.95 s where `D-366` measures
    the step at about 1270 s, so taking the recorded figure would have understated by
    fourteen minutes exactly the step being priced."""
    name = STEPS[2].name
    path = _summary(tmp_path / "run.json", _unit_prices(), failed=(name,))
    with pytest.raises(MeasurementError, match=r"records .* as failed"):
        load_prices([path])
    assert load_prices([path], allow_unhealthy=True)[name] == 1.0


def test_a_second_summary_can_price_a_step_the_first_did_not(tmp_path: Path) -> None:
    """The case that produced the option: a step added while a whole-gate run was in
    flight is priced by a narrow second run rather than by a guess."""
    late = STEPS[-1].name
    partial = _unit_prices()
    del partial[late]
    first = _summary(tmp_path / "whole.json", partial)
    second = _summary(tmp_path / "late.json", {late: 7.5})
    prices = load_prices([first, second])
    assert prices[late] == 7.5
    assert set(prices) == {step.name for step in STEPS}


def test_a_skip_recorded_earlier_is_still_a_skip(tmp_path: Path) -> None:
    """Merging summaries must not launder a skip: only a later summary that actually
    ran the step clears it."""
    name = STEPS[0].name
    first = _summary(tmp_path / "one.json", _unit_prices(), skipped=(name,))
    unrelated = _summary(tmp_path / "two.json", {STEPS[1].name: 2.0})
    with pytest.raises(MeasurementError, match="recorded seconds are not its cost"):
        load_prices([first, unrelated])
    rerun = _summary(tmp_path / "three.json", {name: 4.0})
    assert load_prices([first, rerun])[name] == 4.0


def test_a_list_document_is_not_a_run_summary(tmp_path: Path) -> None:
    """`--list --format json` is the document most likely to be passed by mistake."""
    path = tmp_path / "list.json"
    path.write_text(json.dumps([{"name": STEPS[0].name, "tags": "fast"}]), encoding="utf-8")
    with pytest.raises(MeasurementError, match="no `results` key"):
        load_prices([path])


def test_an_unmoved_tree_repeats_the_whole_gate() -> None:
    """The git graph answers "nothing changed", which `--since` cannot, and that answer
    is where the measured repetition actually is."""
    row = repetition_for_changes(TRIGGER, "dead", (), _unit_prices())
    assert row.nothing_changed
    assert row.must_run == ()
    assert len(row.repeated) == len(STEPS)
    assert row.share == pytest.approx(1.0)


def test_an_unclaimed_path_repeats_nothing() -> None:
    """`select_for_paths` widens to the whole gate on a path no step claims, so the
    measurement must record no saving there rather than the steps that happened to
    match."""
    row = repetition_for_changes(
        TRIGGER, "dead", ("a/path/no/step/claims.zzz",), _unit_prices()
    )
    assert row.unattributed == ("a/path/no/step/claims.zzz",)
    assert len(row.must_run) == len(STEPS)
    assert row.repeated == ()
    assert row.repeated_seconds == pytest.approx(0.0)


def test_an_unattributed_step_is_never_counted_as_repeated() -> None:
    """A step with no `touches` is claimed by every change, so no skip rule built on
    `touches` can ever reach it -- which is where this gate's cost lives."""
    row = repetition_for_changes(
        TRIGGER, "dead", ("packing/src/sqpack/verify.py",), _unit_prices()
    )
    unattributed = {step.name for step in STEPS if not step.touches}
    assert unattributed
    assert unattributed.isdisjoint(row.repeated)


def test_the_wall_floor_is_the_longest_step_that_still_runs() -> None:
    """Work saved and wall saved are different numbers, and only one of them is the
    number a scheduling change can deliver."""
    prices = _unit_prices() | {"fast behavioral tests": 400.0}
    row = repetition_for_changes(TRIGGER, "dead", ("packing/src/sqpack/verify.py",), prices)
    assert row.wall_floor_seconds == pytest.approx(400.0)


def test_the_daily_schedule_is_read_from_the_workflow() -> None:
    """The cron is not a constant here: a copy of it would rot the way every other
    copied number in this gate has."""
    hour, minute = daily_schedule_utc()
    assert 0 <= hour < 24
    assert 0 <= minute < 60


def test_a_schedule_this_module_cannot_parse_is_refused(tmp_path: Path) -> None:
    """An hourly cron read as daily would divide the window's repetition by twenty-four."""
    workflow = tmp_path / "packing-validation.yml"
    workflow.write_text('  schedule:\n    - cron: "17 */2 * * *"\n', encoding="utf-8")
    with pytest.raises(MeasurementError, match="not the daily"):
        daily_schedule_utc(workflow)


def test_two_schedules_are_refused_rather_than_guessed(tmp_path: Path) -> None:
    workflow = tmp_path / "packing-validation.yml"
    workflow.write_text(
        '  schedule:\n    - cron: "17 8 * * *"\n    - cron: "17 20 * * *"\n',
        encoding="utf-8",
    )
    with pytest.raises(MeasurementError, match="declares 2 cron schedules"):
        daily_schedule_utc(workflow)


def test_a_scheduled_run_is_priced_against_the_tree_it_had() -> None:
    """A firing runs against whatever `main` held at the time, not the current tip."""
    pushes = [
        Trigger("push", datetime(2026, 9, 1, 12, tzinfo=UTC), "aaa"),
        Trigger("push", datetime(2026, 9, 3, 12, tzinfo=UTC), "bbb"),
    ]
    firings = schedule_triggers(
        pushes,
        hour=8,
        minute=17,
        start=datetime(2026, 9, 1, tzinfo=UTC),
        end=datetime(2026, 9, 4, 12, tzinfo=UTC),
    )
    assert [(firing.when.day, firing.commit) for firing in firings] == [
        (2, "aaa"),
        (3, "aaa"),
        (4, "bbb"),
    ]


def test_a_window_with_no_interval_is_refused() -> None:
    """One commit is no interval, and a share computed over none is a divide by zero."""
    with pytest.raises(MeasurementError, match="no interval to price"):
        measure(prices=_unit_prices(), days=0)


def test_the_measurement_runs_over_this_repository() -> None:
    """The end-to-end path, on the real graph: every row prices the same whole gate."""
    rows = measure(prices=_unit_prices(), days=WALK_DAYS, schedule=False)
    assert rows
    assert all(row.total_seconds == pytest.approx(float(len(STEPS))) for row in rows)
    assert all(row.repeated_seconds <= row.total_seconds for row in rows)


def test_the_escape_hatch_is_measured_and_not_assumed() -> None:
    """`Step.touches` documents the hatch as a backstop for unfamiliar file types. How
    much of the tree can still reach it is a number, and a shrinking one is exactly the
    fact a skip rule must not be built on without knowing."""
    tracked, claimed, unclaimed = attribution_reach()
    assert tracked > 0
    assert claimed + unclaimed == tracked


def test_merge_tree_identity_agrees_with_the_diff() -> None:
    """The exact content address, checked against the other way of asking. A merge whose
    tree equals its pull-request head's must also show an empty diff against it; if those
    two ever disagreed, the tree id would not be the address it is being used as."""
    rows = merge_identity(days=WALK_DAYS)
    assert rows
    for row in rows:
        assert row.identical == (changed_between(row.head, row.merge) == ())


def test_the_campaign_record_verdict_is_not_a_function_of_the_tree_alone() -> None:
    """The counter-example that bounds every unmoved-tree skip rule, checked rather than
    asserted.

    `BC-215` measured that 13 of 70 deep runs in thirty days ran against a tree that had
    not moved, and the obvious rule is to skip them. This is why the rule cannot be
    "skip the run": the `campaign record` step reads the wall clock, and three of its
    refusals are *anti*-monotone in it -- an expired lease, a passed session deadline
    and a passed delegation deadline all become true with time alone. So a tree that
    was green yesterday can be red today with no byte changed, and the scheduled run is
    the only thing that would say so.

    Same input, two clocks, two verdicts. The session here is synthetic so the assertion
    does not depend on which real session happens to be open on the day.
    """
    session = {
        "_path": Path("session-999-synthetic.md"),
        "id": "session-999",
        "status": "in_progress",
        "started_at": "2026-09-05T00:00:00Z",
        "deadline_at": "2026-09-05T04:00:00Z",
        "budget": {"wall_minutes": 240},
        "workflow_phases": [
            {
                "workflow": "efficiency-loop",
                "entered_by": "session_start",
                "status": "in_progress",
            }
        ],
    }

    def verdict(now: datetime) -> list[str]:
        return ledger.check([], [], [], [], [session], agendas=[], now=now, logbook_entries=[])

    passed = "session-999-synthetic.md: in-progress session deadline_at has passed"
    # Naive UTC, because that is what `ledger.main` passes and the comparison it
    # reaches is written against it.
    before = datetime(2026, 9, 5, 1, tzinfo=UTC).replace(tzinfo=None)
    after = datetime(2026, 9, 6, 1, tzinfo=UTC).replace(tzinfo=None)
    assert passed not in verdict(before)
    assert passed in verdict(after)
