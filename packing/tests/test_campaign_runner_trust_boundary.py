"""The unattended runner's result-validity and lifecycle trust boundary.

Regressions for D-044 (validity and self-test status were assertions made by the thing
under test) and D-046 (the runner was not a closed, checked state machine). Both defects
name `sqpack/campaign/runner.py`, and both are worst exactly when nobody is watching, so
each guard here is fired on purpose rather than assumed.

The adversarial fixtures are the ten the remediation block named: fabricated overlap
zero, a fabricated side, truncated output, a stale self-test, an unmet prerequisite, an
expired or offset lease, a terminal rewrite, a deadline overrun, a process crash, a
persistence failure, and broad staging.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import os
import stat
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from itertools import count
from pathlib import Path
from typing import Any

import pytest

from sqpack.campaign import runner

# The engine stand-in. `runner.engine_path` takes argv[0] of the declared command, so the
# fixture engine has to be a real executable file: a self-test that can pass or fail, and
# a producer whose output shape is chosen by the environment.
ENGINE_SOURCE = """#!{interpreter}
import json, math, os, sys

mode = os.environ.get("RUNNER_FIXTURE_MODE", "ok")

if "--selftest" in sys.argv:
    if mode == "selftest-fail":
        print("SELFTEST FAILED")
        sys.exit(1)
    print("SELFTEST PASSED")
    sys.exit(0)

n = int(sys.argv[sys.argv.index("--n") + 1])
seed = int(sys.argv[sys.argv.index("--seed") + 1])
columns = math.ceil(math.sqrt(n))
rows = math.ceil(n / columns)
x = [0.5 + float(i % columns) for i in range(n)]
y = [0.5 + float(i // columns) for i in range(n)]
t = [0.0] * n
side = float(max(columns, rows))

if mode == "forged-overlap":
    x[1], y[1] = x[0], y[0]
if mode == "forged-side":
    side = 1.5
if mode == "no-pose":
    print(json.dumps({{"n": n, "seed": seed, "best_side": side, "overlap": 0}}))
    sys.exit(0)
if mode == "producer-crash":
    sys.exit(3)
if mode == "slow":
    import time
    time.sleep(5)

print(json.dumps({{"n": n, "seed": seed, "best_side": side, "overlap": 0,
                   "x": x, "y": y, "t": t}}))
"""

SERIES_README = """---
series:
  id: s-fixture
  status: open
---
# fixture series
"""

HYPOTHESIS = """---
hypothesis:
  id: {hid}
  claim: A fixture claim.
  criterion: {{shape: record, metric: best_side, direction: lower, threshold: 1e-4}}
  instrument_ready: true
  priority: 1
  prereqs: [{prereqs}]
  sweep: {{axis: n, points: [{cells}]}}
  runner:
    command: '{command}'
    cells: [{cells}]
    seeds: [{seeds}]
    timebox: {timebox}
---
# {hid}
"""

FRONTIER = """---
packing:
  upper_bound:
    value: {value}
    found_by: [fixture]
    found_year: 2026
---
# n = {n}
"""


@dataclass
class Tree:
    """An isolated campaign checkout with a real git repository behind it."""

    root: Path
    engine: Path
    series: Path

    @property
    def experiments(self) -> Path:
        return self.series / "experiments"

    def round_path(self, eid: str) -> Path:
        return next(self.experiments.glob(f"{eid}-*.md"))

    def archive(self, eid: str) -> Path:
        return runner.archive_of(self.round_path(eid))


def _git(tree: Tree, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=tree.root, capture_output=True, text=True, check=True
    )
    return completed.stdout.strip()


def _write_hypothesis(
    tree: Tree,
    hid: str = "H-900",
    *,
    cells: str = "4",
    seeds: str = "1",
    timebox: str = "5m",
    prereqs: str = "",
    command: str | None = None,
) -> None:
    (tree.root / "campaign" / "hypotheses" / f"{hid}-fixture.md").write_text(
        HYPOTHESIS.format(
            hid=hid,
            cells=cells,
            seeds=seeds,
            timebox=timebox,
            prereqs=prereqs,
            command=command or f"{tree.engine} --n {{n}} --seed {{seed}}",
        )
    )


@pytest.fixture
def tree(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Tree:
    """Point the runner's module paths at a throwaway campaign and git repository."""
    root = tmp_path / "packing"
    campaign = root / "campaign"
    series = campaign / "series" / "s-fixture"
    for directory in (
        series / "experiments",
        series / "results",
        campaign / "hypotheses",
        root / "frontier",
        root / "cases",
        root / "devtools",
    ):
        directory.mkdir(parents=True, exist_ok=True)
    (root / "pyproject.toml").write_text("[project]\nname = 'fixture'\n")
    (series / "README.md").write_text(SERIES_README)
    (campaign / "ledger.md").write_text("# fixture ledger\n")
    for n, value in ((4, 2.0), (9, 3.0)):
        (root / "frontier" / f"n-{n:03d}.md").write_text(FRONTIER.format(n=n, value=value))

    engine = root / "fake-engine"
    engine.write_text(ENGINE_SOURCE.format(interpreter=sys.executable))
    engine.chmod(engine.stat().st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    email = ["git", "config", "user.email", "fixture@example.invalid"]
    subprocess.run(email, cwd=root, check=True)
    subprocess.run(["git", "config", "user.name", "fixture"], cwd=root, check=True)
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    subprocess.run(["git", "commit", "-qm", "fixture", "--no-verify"], cwd=root, check=True)

    monkeypatch.setattr(runner, "ROOT", root)
    monkeypatch.setattr(runner, "CAMPAIGN", campaign)
    monkeypatch.setattr(runner, "SERIES", campaign / "series")
    monkeypatch.setattr(runner, "REPORT", campaign / "session-report.md")
    monkeypatch.setattr(runner, "GATE_MARKER", root / ".gate-running")
    # The ledger is a separate module with its own whole-set checker and its own tests.
    # Here it stands in as a step that either succeeds or fails, so the runner's response
    # to each is what is under test. It rewrites the view on every call, as the real one
    # does, which is what puts `ledger.md` into a round's commit.
    renders = count()

    def render_stub() -> subprocess.CompletedProcess[str]:
        (campaign / "ledger.md").write_text(f"# fixture ledger\nrender {next(renders)}\n")
        return subprocess.CompletedProcess(args=["render"], returncode=0, stdout="", stderr="")

    monkeypatch.setattr(runner, "regenerate", render_stub)
    monkeypatch.setenv("RUNNER_FIXTURE_MODE", "ok")

    built = Tree(root=root, engine=engine, series=series)
    _write_hypothesis(built)
    return built


def _terminal_round(tree: Tree, decision: str = "rejected") -> str:
    """Write a round that has already reached a terminal decision."""
    (tree.experiments / "exp-500-terminal.md").write_text(
        "---\n"
        "experiment:\n"
        "  id: exp-500\n"
        "  series: s-fixture\n"
        "  date: '2026-01-01'\n"
        "  hypotheses: [H-900]\n"
        f"  verdict: {{decision: {decision}, primary_criterion: best_side, reason: done}}\n"
        "---\n# exp-500\n"
    )
    return "exp-500"


# --- the result-line contract (D-044) ---------------------------------------------


def test_a_scored_line_without_a_pose_is_refused() -> None:
    with pytest.raises(runner.GuardError, match="no pose"):
        runner.validated_record('{"n": 11, "seed": 1, "best_side": 3.9, "overlap": 0}')


@pytest.mark.parametrize("field", runner.POSE_FIELDS)
def test_a_pose_array_must_have_exactly_n_entries(field: str) -> None:
    rec = json.loads(runner.grid_result_line(4, 1))
    rec[field] = rec[field][:-1]
    with pytest.raises(runner.GuardError, match=f"pose field '{field}' of length 3"):
        runner.validated_record(json.dumps(rec))


def test_a_non_finite_pose_coordinate_is_refused() -> None:
    rec = json.loads(runner.grid_result_line(4, 1))
    rec["x"][0] = float("inf")
    with pytest.raises(runner.GuardError, match="non-finite"):
        runner.validated_record(json.dumps(rec))


def test_the_pose_digest_moves_when_one_coordinate_moves() -> None:
    rec = json.loads(runner.grid_result_line(4, 1))
    moved = dict(rec, x=[rec["x"][0] + 1e-12, *rec["x"][1:]])

    assert runner.pose_digest(rec) != runner.pose_digest(moved)


def test_the_archive_digest_is_sensitive_to_order_and_content() -> None:
    first = json.loads(runner.grid_result_line(4, 1))
    second = json.loads(runner.grid_result_line(4, 2))

    assert runner.archive_digest([first, second]) != runner.archive_digest([second, first])
    assert runner.archive_digest([first]) != runner.archive_digest([first, second])


@pytest.mark.parametrize("reserved", runner.RESERVED_RECEIPTS)
def test_a_producer_may_not_write_a_reserved_receipt(reserved: str) -> None:
    with pytest.raises(runner.GuardError, match="reserved"):
        runner.validated_record(json.dumps({reserved: {"verified": True}}))


# --- the independent oracle, in another process (D-044) ---------------------------


def test_a_separate_process_verifies_a_genuinely_valid_pose(tmp_path: Path) -> None:
    archive = tmp_path / "honest.jsonl"
    archive.write_text(runner.grid_result_line(9, 1) + "\n")

    report = runner.verify_archive_in_separate_process(archive)

    assert report["verified"] is True
    assert report["poses_checked"] == 1
    assert report["verifier"] == "sqpack.verify.verify_packing"
    assert report["archive_sha256"] == runner.archive_digest(
        [json.loads(runner.grid_result_line(9, 1))]
    )


def test_a_fabricated_zero_overlap_is_refused_by_the_oracle(tmp_path: Path) -> None:
    x, y, t, side = runner.grid_pose(4)
    archive = tmp_path / "forged.jsonl"
    archive.write_text(
        json.dumps(
            {
                "n": 4,
                "seed": 1,
                "best_side": side,
                "overlap": 0,
                "x": [x[0], x[0], x[2], x[3]],
                "y": [y[0], y[0], y[2], y[3]],
                "t": t,
            }
        )
        + "\n"
    )

    with pytest.raises(runner.GuardError, match="overlap"):
        runner.verify_archive_in_separate_process(archive)


def test_a_side_the_pose_cannot_support_is_refused(tmp_path: Path) -> None:
    """The n=17 fabrication D-044 describes: a record-beating side over a 5x5 grid."""
    archive = tmp_path / "fabricated-side.jsonl"
    archive.write_text(runner.grid_result_line(17, 1, 3.7) + "\n")

    with pytest.raises(runner.GuardError, match="the pose needs side 5"):
        runner.verify_archive_in_separate_process(archive)


def test_a_truncated_archive_certifies_nothing(tmp_path: Path) -> None:
    empty = tmp_path / "empty.jsonl"
    empty.write_text("")
    partial = tmp_path / "partial.jsonl"
    partial.write_text(runner.grid_result_line(4, 1)[:-12])

    assert runner.verify_archive_poses(empty)["verified"] is False
    with pytest.raises(runner.GuardError, match="non-JSON line"):
        runner.verify_archive_poses(partial)


def test_the_verify_archive_step_exits_non_zero_on_a_forged_pose(tmp_path: Path) -> None:
    archive = tmp_path / "forged.jsonl"
    archive.write_text(runner.grid_result_line(4, 1, 1.5) + "\n")

    assert runner.main(["verify-archive", str(archive)]) == 1
    good = tmp_path / "good.jsonl"
    good.write_text(runner.grid_result_line(4, 1) + "\n")
    assert runner.main(["verify-archive", str(good)]) == 0


# --- the engine gate is executed, never asserted (D-044) --------------------------


def test_execute_refuses_when_the_engine_selftest_fails(
    tree: Tree, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("RUNNER_FIXTURE_MODE", "selftest-fail")
    eid = runner.claim("H-900", "fixture", 1.0)

    with pytest.raises(runner.GuardError, match="self-test failed with exit 1"):
        runner.execute(eid)

    assert not tree.archive(eid).exists()


def test_execute_refuses_when_the_engine_is_missing(tree: Tree) -> None:
    tree.engine.unlink()
    eid = runner.claim("H-900", "fixture", 1.0)

    with pytest.raises(runner.GuardError, match="does not exist"):
        runner.execute(eid)


def test_record_refuses_when_the_engine_changed_after_its_selftest(tree: Tree) -> None:
    eid = runner.claim("H-900", "fixture", 1.0)
    runner.execute(eid)
    tree.engine.write_text(tree.engine.read_text() + "\n# swapped after the gate ran\n")

    with pytest.raises(runner.RefusalError, match="does not certify the engine"):
        runner.record(eid, operator="fixture")


def test_the_selftest_receipt_binds_the_binary_digest(tree: Tree) -> None:
    eid = runner.claim("H-900", "fixture", 1.0)
    runner.execute(eid)

    receipt = runner.scan_archive(tree.archive(eid))[1][runner.SELFTEST_METADATA]

    assert receipt is not None
    assert receipt["exit_status"] == 0
    assert receipt["engine_sha256"] == runner.file_digest(tree.engine)
    assert receipt["argv"][-1] == "--selftest"


# --- archive digests bind validity to an immutable object (D-044) -----------------


def test_record_refuses_an_archive_edited_after_it_was_verified(tree: Tree) -> None:
    eid = runner.claim("H-900", "fixture", 1.0)
    runner.execute(eid)
    archive = tree.archive(eid)
    runner.append_receipt(
        archive,
        runner.VERIFICATION_METADATA,
        {"verified": True, "archive_sha256": "0" * 64, "poses_checked": 1},
    )

    with pytest.raises(runner.RefusalError, match="changed after it was verified"):
        runner.record(eid, operator="fixture")


def test_record_refuses_a_forged_result_line(
    tree: Tree, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("RUNNER_FIXTURE_MODE", "forged-overlap")
    eid = runner.claim("H-900", "fixture", 1.0)
    runner.execute(eid)

    with pytest.raises(runner.GuardError, match="independent pose verification refused"):
        runner.record(eid, operator="fixture")

    assert runner.front(tree.round_path(eid))["experiment"]["verdict"]["decision"] == (
        "in-progress"
    )


@pytest.mark.usefixtures("tree")
def test_execute_refuses_a_producer_that_prints_no_pose(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("RUNNER_FIXTURE_MODE", "no-pose")
    eid = runner.claim("H-900", "fixture", 1.0)

    with pytest.raises(runner.GuardError, match="no pose"):
        runner.execute(eid)


# --- the lifecycle is closed and checked (D-046) ----------------------------------


def test_execute_refuses_a_terminal_round(tree: Tree) -> None:
    eid = _terminal_round(tree)

    with pytest.raises(runner.RefusalError, match="not in-progress"):
        runner.execute(eid)


def test_record_refuses_a_terminal_round(tree: Tree) -> None:
    eid = _terminal_round(tree, "unresolved")
    before = tree.round_path(eid).read_text()

    with pytest.raises(runner.RefusalError, match="not in-progress"):
        runner.record(eid, operator="fixture")

    assert tree.round_path(eid).read_text() == before


def test_release_refuses_a_terminal_round(tree: Tree) -> None:
    eid = _terminal_round(tree, "abandoned")

    with pytest.raises(runner.RefusalError, match="not in-progress"):
        runner.release(eid, "recovery")


def test_the_queue_skips_a_hypothesis_whose_prereqs_have_not_landed(tree: Tree) -> None:
    _write_hypothesis(tree, "H-901", prereqs="H-011")
    _write_hypothesis(tree, "H-902", prereqs="a verified n = 17 pose")

    runnable, skipped = runner.queue()
    reasons = dict(skipped)

    assert [hid for hid, _ in runnable] == ["H-900"]
    assert "H-011 has not been accepted" in reasons["H-901"]
    assert "not a hypothesis id this runner can check" in reasons["H-902"]


def test_claim_enforces_prereqs_even_when_driven_by_hand(tree: Tree) -> None:
    _write_hypothesis(tree, "H-901", prereqs="H-011")

    with pytest.raises(runner.RefusalError, match="prerequisites that have not landed"):
        runner.claim("H-901", "fixture", 1.0)


def test_a_lease_offset_is_converted_to_utc_not_stripped() -> None:
    west = {"lease": {"expires": "2026-01-01T00:00:00-07:00"}}
    naive = {"lease": {"expires": "2026-01-01T00:00:00"}}

    assert runner.lease_expiry("exp-1", west) == datetime(2026, 1, 1, 7, 0, tzinfo=UTC)
    assert runner.lease_expiry("exp-1", naive) == datetime(2026, 1, 1, 0, 0, tzinfo=UTC)


def test_execute_refuses_an_expired_lease(tree: Tree) -> None:
    eid = runner.claim("H-900", "fixture", 1.0)
    path = tree.round_path(eid)
    stale = (runner.now() - timedelta(minutes=5)).replace(microsecond=0).isoformat()
    # Rewrite the parsed artifact rather than editing the text, so it stays parseable.
    front = runner.front(path)
    front["experiment"]["lease"]["expires"] = stale
    path.write_text("---\n" + json.dumps(front) + "\n---\n# stale\n")

    with pytest.raises(runner.RefusalError, match="lease expired"):
        runner.execute(eid)


def test_execute_caps_the_timebox_at_the_remaining_lease(
    tree: Tree, capsys: pytest.CaptureFixture[str]
) -> None:
    _write_hypothesis(tree, "H-900", timebox="8h")
    eid = runner.claim("H-900", "fixture", 0.05)  # a three-minute lease

    runner.execute(eid)

    assert "lease caps this round" in capsys.readouterr().out


@pytest.mark.slow
def test_each_cell_gets_its_own_share_of_the_timebox(
    tree: Tree, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A slow first cell must not be able to spend the whole round's budget.

    The producer outlives any share it can be given, so the only way the second cell is
    reached at all is the per-cell split. Asserted on that invariant rather than on which
    of the two cut-off messages a loaded machine happens to print, and kept to a two
    second timebox so the guard costs the suite a second per cell rather than four.
    """
    _write_hypothesis(tree, "H-900", cells="4, 9", seeds="1", timebox="3s")
    monkeypatch.setenv("RUNNER_FIXTURE_MODE", "slow")
    eid = runner.claim("H-900", "fixture", 1.0)

    runner.execute(eid)
    out = capsys.readouterr().out

    # The discriminating assertion is that the SECOND cell was actually invoked and cut
    # off at a share of its own. Asserting only that "n=9" appears is a tautology: with
    # one deadline shared across cells, the second cell still prints a line -- it just
    # says the deadline was gone before it started. Mutation-checked against
    # `cell_deadline = round_deadline`, which this now fails on and the weaker form did
    # not.
    assert "n=4: cell share reached mid-seed" in out
    assert "n=9: cell share reached mid-seed" in out
    assert "before the cell started" not in out
    assert runner.scan_archive(tree.archive(eid))[0] == []


# --- failures are durable and non-scientific (D-046) ------------------------------


def test_commit_paths_refuses_when_nothing_was_staged(tree: Tree) -> None:
    with pytest.raises(runner.RefusalError, match="not durably persisted"):
        runner.commit_paths([tree.root / "pyproject.toml"], "no change here")


def test_commit_paths_moves_head_and_stages_only_what_it_was_given(tree: Tree) -> None:
    unrelated = tree.root / "campaign" / "unrelated-lane.md"
    unrelated.write_text("another lane was mid-edit\n")
    mine = tree.root / "campaign" / "ledger.md"
    mine.write_text("# regenerated\n")
    before = _git(tree, "rev-parse", "HEAD")

    runner.commit_paths([mine], "round: narrow")

    assert _git(tree, "rev-parse", "HEAD") != before
    assert _git(tree, "show", "--name-only", "--format=", "HEAD").split() == [
        "campaign/ledger.md"
    ]
    assert "unrelated-lane.md" in _git(tree, "status", "--porcelain")


def test_commit_paths_refuses_a_commit_that_does_not_move_head(
    tree: Tree, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A commit that exits 0 without producing an object is the false success D-046 names.

    The other two persistence branches are reachable with a real repository; this one is
    not, so git is stubbed to report success while `HEAD` stays put. Without the stub the
    guard would be untested code, and untested code is what the defect was.
    """

    def fake_git(*args: str) -> str:
        if args[0] == "rev-parse":
            return "same-sha"
        if args[0] == "diff":
            return "campaign/ledger.md"
        return ""

    monkeypatch.setattr(runner, "git", fake_git)
    monkeypatch.setattr(
        runner.subprocess,
        "run",
        lambda *a, **_k: subprocess.CompletedProcess(
            args=a, returncode=0, stdout="", stderr=""
        ),
    )

    with pytest.raises(runner.RefusalError, match="HEAD did not move"):
        runner.commit_paths([tree.root / "pyproject.toml"], "round: no-op")


@pytest.mark.usefixtures("tree")
def test_record_refuses_when_the_ledger_refuses(monkeypatch: pytest.MonkeyPatch) -> None:
    eid = runner.claim("H-900", "fixture", 1.0)
    runner.execute(eid)
    monkeypatch.setattr(
        runner,
        "regenerate",
        lambda: subprocess.CompletedProcess(
            args=["render"], returncode=1, stdout="FAIL stale\n", stderr=""
        ),
    )

    with pytest.raises(runner.RefusalError, match="campaign ledger refused"):
        runner.record(eid, operator="fixture")


@pytest.mark.usefixtures("tree")
def test_run_releases_the_round_and_still_reports_when_a_step_refuses(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A RefusalError used to escape `run`, leaving a claim and writing no report."""

    def refuse(_eid: str, *, operator: str) -> str:  # noqa: ARG001 - the seam's signature
        raise runner.RefusalError("the ledger would not render")

    monkeypatch.setattr(runner, "record", refuse)

    assert runner.run("fixture", 0.5) == 0

    rounds = [e for _, e in runner.all_rounds()]
    assert [e["verdict"]["decision"] for e in rounds] == ["unresolved"]
    assert rounds[0]["effort"]["stopped_by"] == "error"
    assert runner.REPORT.exists()
    assert "the ledger would not render" in runner.REPORT.read_text()


def test_a_refused_line_never_reaches_the_archive(
    tree: Tree, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`read_lines` validates before it writes, so a refusal leaves no usable evidence."""
    monkeypatch.setenv("RUNNER_FIXTURE_MODE", "no-pose")
    eid = runner.claim("H-900", "fixture", 1.0)

    with pytest.raises(runner.GuardError, match="no pose"):
        runner.execute(eid)

    archived, receipts = runner.scan_archive(tree.archive(eid))
    assert archived == []
    assert receipts[runner.EXECUTION_METADATA] is not None


def test_release_survives_an_archive_it_cannot_read(tree: Tree) -> None:
    """Recovery must not be blocked by the archive it is recovering from."""
    eid = runner.claim("H-900", "fixture", 1.0)
    runner.execute(eid)
    archive = tree.archive(eid)
    # An archive edited on disk after the fact: a scored line with its pose stripped.
    archive.write_text(
        '{"n": 4, "seed": 1, "best_side": 2.0, "overlap": 0}\n' + archive.read_text()
    )
    with pytest.raises(runner.GuardError, match="no pose"):
        runner.execution_metadata(archive)

    runner.release(eid, "the archive was edited under the round")

    experiment = runner.front(tree.round_path(eid))["experiment"]
    assert experiment["verdict"]["decision"] == "unresolved"
    assert experiment["effort"]["wall_seconds"] == 0


def test_run_reports_the_true_state_when_a_step_fails_after_the_verdict(
    tree: Tree, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A failed commit leaves a terminal round; the session must not call it released."""

    def refuse(_paths: list[Path], _message: str) -> str:
        raise runner.RefusalError("git commit failed with exit 128")

    monkeypatch.setattr(runner, "commit_paths", refuse)

    assert runner.run("fixture", 0.5) == 0
    out = capsys.readouterr().out

    assert "is already unresolved: the failure came after the verdict" in out
    assert (
        runner.front(tree.round_path("exp-001"))["experiment"]["verdict"]["decision"]
        == "unresolved"
    )


def test_run_recomputes_the_queue_between_rounds(tree: Tree) -> None:
    _write_hypothesis(tree, "H-901")

    assert runner.run("fixture", 0.5) == 0

    decisions = {e["hypotheses"][0] for _, e in runner.all_rounds()}
    assert decisions == {"H-900", "H-901"}


def test_a_released_round_is_committed(tree: Tree) -> None:
    eid = runner.claim("H-900", "fixture", 1.0)
    before = _git(tree, "rev-parse", "HEAD")

    runner.release(eid, "the operator gave up")

    assert _git(tree, "rev-parse", "HEAD") != before
    assert "released" in _git(tree, "show", "--format=%s", "--name-only", "HEAD")


# --- one supervised successful round ----------------------------------------------


def test_a_supervised_round_records_a_verified_verdict(tree: Tree) -> None:
    """claim, execute, record: end to end, with every new guard in the path."""
    eid = runner.claim("H-900", "fixture", 1.0)
    stub = runner.front(tree.round_path(eid))["experiment"]
    assert stub["verdict"]["decision"] == "in-progress"
    assert stub["subject"]["selftest_passed"] is False
    assert stub["lease"]["pid"] == os.getpid()

    runner.execute(eid)
    decision = runner.record(eid, operator="fixture")

    assert decision == "unresolved"  # within the basin; clause 5 is held for review
    experiment = runner.front(tree.round_path(eid))["experiment"]
    assert experiment["subject"]["selftest_passed"] is True
    assert experiment["subject"]["assurance"] == "numerically-checked"
    assert "lease" not in experiment

    guard = [r for r in experiment["results"] if r["shape"] == "determination"]
    assert len(guard) == 1
    assert guard[0]["role"] == "guard"
    assert "sqpack.verify.verify_packing in a separate process" in guard[0]["checked_by"]

    receipts = runner.scan_archive(tree.archive(eid))[1]
    verification: dict[str, Any] | None = receipts[runner.VERIFICATION_METADATA]
    assert verification is not None
    assert verification["verified"] is True
    assert verification["poses_checked"] == 1
    assert verification["archive_sha256"][:16] in guard[0]["checked_by"]

    committed = _git(tree, "show", "--name-only", "--format=", "HEAD").split()
    assert sorted(committed) == sorted(
        [
            str(tree.round_path(eid).relative_to(tree.root)),
            str(tree.archive(eid).relative_to(tree.root)),
            "campaign/ledger.md",
        ]
    )


@pytest.mark.usefixtures("tree")
def test_recording_the_same_round_twice_is_refused() -> None:
    eid = runner.claim("H-900", "fixture", 1.0)
    runner.execute(eid)
    runner.record(eid, operator="fixture")

    with pytest.raises(runner.RefusalError, match="not in-progress"):
        runner.record(eid, operator="fixture")
    with pytest.raises(runner.RefusalError, match="not in-progress"):
        runner.execute(eid)


def test_a_result_may_not_be_attributed_to_another_cell(tmp_path: Path) -> None:
    """A command run for one declared cell must not score against a different one."""
    sink = tmp_path / "archive.jsonl"
    with sink.open("w") as fh:
        with pytest.raises(runner.GuardError, match="claims n=9 but the command was run"):
            runner.read_lines(runner.grid_result_line(9, 1), fh, expect_n=4, expect_seed=1)
        with pytest.raises(runner.GuardError, match="claims seed=2 but the command was run"):
            runner.read_lines(runner.grid_result_line(4, 2), fh, expect_n=4, expect_seed=1)

    assert sink.read_text() == ""


def test_a_matching_line_is_still_archived(tmp_path: Path) -> None:
    sink = tmp_path / "archive.jsonl"
    with sink.open("w") as fh:
        best = runner.read_lines(runner.grid_result_line(4, 1), fh, expect_n=4, expect_seed=1)

    assert best == 2.0
    assert len(sink.read_text().splitlines()) == 1


def _pose_line(*, overlap_depth: float = 0.0, understate: float = 0.0) -> str:
    """A grid pose, optionally pushed into itself or given a side it cannot support."""
    x, y, t, side = runner.grid_pose(4)
    x = list(x)
    x[1] -= overlap_depth
    return json.dumps(
        {
            "n": 4,
            "seed": 1,
            "best_side": side - understate,
            "overlap": 0,
            "x": x,
            "y": y,
            "t": t,
        }
    )


@pytest.mark.parametrize("depth", [2e-9, 1e-8, 1e-6, 1e-3])
def test_the_oracle_refuses_an_overlap_above_the_declared_tolerance(
    tmp_path: Path, depth: float
) -> None:
    archive = tmp_path / "a.jsonl"
    archive.write_text(_pose_line(overlap_depth=depth) + "\n")

    assert runner.verify_archive_poses(archive)["verified"] is False


@pytest.mark.parametrize("shortfall", [2e-9, 1e-8, 1e-6, 1e-3])
def test_the_oracle_refuses_a_side_understated_above_the_declared_tolerance(
    tmp_path: Path, shortfall: float
) -> None:
    archive = tmp_path / "a.jsonl"
    archive.write_text(_pose_line(understate=shortfall) + "\n")

    assert runner.verify_archive_poses(archive)["verified"] is False


def test_the_detection_floor_is_far_below_the_decision_threshold(tmp_path: Path) -> None:
    """What the tolerance costs, stated as a measurement rather than an assurance.

    A fabrication small enough to slip past the oracle is 1e-9-ish, which currently sits
    five orders of magnitude below the 1e-4 basin gap the campaign actually decides on, so
    no evadable forgery can manufacture a basin hit or a record.

    The assertion below pins the weaker claim, and the gap is worth stating rather than
    rounding off: it holds the tolerance *at least four* orders below the threshold, so a
    tolerance loosened to 1e-8 -- one whole order of protection gone -- still passes, while
    2e-8 fails. Strengthening the divisor to 1e5 would pin the ratio the constants actually
    hold; until then this catches a loosening towards the decision threshold, not every
    loosening.
    """
    below = tmp_path / "below.jsonl"
    below.write_text(_pose_line(overlap_depth=1e-10) + "\n")

    assert runner.verify_archive_poses(below)["verified"] is True
    assert runner.POSE_TOLERANCE <= runner.REACHED_BASIN / 1e4


def test_record_takes_its_verdict_only_from_the_child_process() -> None:
    """The containment, enforced structurally rather than asserted in a comment.

    `verify_archive_poses` is the oracle body and it lives in this same module, so the
    parent process always has it — `preflight` legitimately calls it in-process, and
    where the `sqpack.verify` import sits changes nothing about that. The property that
    actually matters is narrower and checkable: **`record` may reach a verdict only
    through the child process.** If someone ever "optimises" the subprocess away, this
    fails rather than the comment quietly becoming untrue.
    """
    source = Path(runner.__file__).read_text(encoding="utf-8")
    body = next(
        node
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.FunctionDef) and node.name == "record"
    )
    called = {
        node.func.id
        for node in ast.walk(body)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }

    assert "verify_archive_in_separate_process" in called
    assert "verify_archive_poses" not in called
    assert "verify_packing" not in called
    assert "corners_from_poses" not in called


def test_the_child_verifier_is_reached_by_re_entering_this_module() -> None:
    """And the child really is a separate interpreter running this module's own step."""
    source = Path(runner.__file__).read_text(encoding="utf-8")
    spawn = next(
        node
        for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.FunctionDef)
        and node.name == "verify_archive_in_separate_process"
    )
    literals = {
        node.value
        for node in ast.walk(spawn)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }

    assert "verify-archive" in literals
    assert runner.RUNNER_MODULE == "sqpack.campaign.runner"


# --- the guards are load-bearing, checked against an unrepaired copy ---------------
#
# A regression that also passes against the unrepaired runner is not evidence. Each test
# below reverts exactly one repair in a COPY of the module under `tmp_path`, imports the
# copy, and shows it accepts what the repaired module refuses. Nothing here edits the
# module in the working tree: a mutation left in a shared tree is a live safety hole, and
# `ruff`, `ruff format` and `basedpyright` are all clean on a guard short-circuited to
# `if False:` -- a dead branch is syntactically perfect.

MUTATIONS: dict[str, tuple[str, str]] = {
    "pose": ("    validated_pose(rec, int(n))\n    return rec", "    return rec"),
    "attribution": (
        "                if expected is not None and actual != expected:",
        "                if False:",
    ),
    "lease": ("    if left <= 0:", "    if False:"),
    "transition": (
        "    if decision == IN_PROGRESS:\n        return",
        "    if True:\n        return",
    ),
    "prereqs": ("    unmet: list[str] = []", "    return []\n    unmet: list[str] = []"),
}


def _unrepaired(tmp_path: Path, name: str) -> Any:
    """Import a copy of the runner with exactly one repair reverted."""
    old, new = MUTATIONS[name]
    source = Path(runner.__file__).read_text(encoding="utf-8")
    assert old in source, f"mutation anchor for {name!r} no longer matches the source"
    target = tmp_path / f"unrepaired_{name}.py"
    target.write_text(source.replace(old, new, 1), encoding="utf-8")
    spec = importlib.util.spec_from_file_location(f"runner_unrepaired_{name}", target)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # `dataclasses` resolves annotations through `sys.modules[cls.__module__]`, so the
    # copy has to be registered while it executes. It is removed again immediately: the
    # unrepaired module is evidence for one assertion, not something to leave importable.
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(spec.name, None)
    return module


def test_the_pose_requirement_is_load_bearing(tmp_path: Path) -> None:
    poseless = '{"n": 11, "seed": 1, "best_side": 3.9, "overlap": 0}'

    with pytest.raises(runner.GuardError, match="no pose"):
        runner.validated_record(poseless)

    assert _unrepaired(tmp_path, "pose").validated_record(poseless)["best_side"] == 3.9


def test_the_attribution_check_is_load_bearing(tmp_path: Path) -> None:
    foreign = runner.grid_result_line(9, 1)
    sink = tmp_path / "sink.jsonl"

    with sink.open("w") as fh, pytest.raises(runner.GuardError, match="claims n=9"):
        runner.read_lines(foreign, fh, expect_n=4, expect_seed=1)

    with sink.open("w") as fh:
        best = _unrepaired(tmp_path, "attribution").read_lines(
            foreign, fh, expect_n=4, expect_seed=1
        )
    assert best == 3.0


def test_the_lease_expiry_check_is_load_bearing(tmp_path: Path) -> None:
    stale = {"lease": {"expires": (runner.now() - timedelta(minutes=5)).isoformat()}}

    with pytest.raises(runner.RefusalError, match="lease expired"):
        runner.lease_seconds_remaining("exp-1", stale)

    assert _unrepaired(tmp_path, "lease").lease_seconds_remaining("exp-1", stale) < 0


def test_the_terminal_round_guard_is_load_bearing(tmp_path: Path) -> None:
    terminal = {"verdict": {"decision": "rejected"}}

    with pytest.raises(runner.RefusalError, match="not in-progress"):
        runner.require_in_progress("exp-1", terminal, "record")

    assert (
        _unrepaired(tmp_path, "transition").require_in_progress("exp-1", terminal, "record")
        is None
    )


def test_the_prerequisite_gate_is_load_bearing(tmp_path: Path) -> None:
    blocked = {"prereqs": ["H-011"]}

    assert runner.unmet_prereqs(blocked, []) == ["H-011 has not been accepted"]
    assert _unrepaired(tmp_path, "prereqs").unmet_prereqs(blocked, []) == []
