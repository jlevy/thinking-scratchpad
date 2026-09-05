#!/usr/bin/env python3
"""Price the work a deep-surface run repeats because none of its declared inputs moved.

`BC-215`. The deep surface runs on every push to `main`, on a daily schedule, and on
`workflow_dispatch`; nothing about it is scoped to the change. `Step.touches` already
declares, per step, the repo-relative globs whose change can affect that step's verdict,
and `select_for_paths` already turns a set of changed paths into the steps that change
can reach. What was missing is the arithmetic: over a real window of the git graph, how
many seconds of each deep run went to steps that no path in that window's diff could
have affected.

The answer is a measurement and it is refusable, which is the whole reason this is a
tool rather than a paragraph:

* **Prices come from a real run, never from a guess.** `--timings` takes a
  `packing-validate --format json` summary. A step in `STEPS` the summary does not
  price, a priced step `STEPS` does not have, and a step the summary records as
  anything but *passed* are each a refusal, because a step priced at zero -- or at
  the seconds it reached before aborting -- repeats for free by arithmetic rather
  than by evidence.
* **The trigger points come from the workflow, not from memory.** The daily cron is
  read out of `.github/workflows/packing-validation.yml`; a schedule this module cannot
  parse is a refusal rather than an assumed one.
* **Two questions are kept apart.** Repeated *work* is the sum of the seconds of the
  steps that need not have run. Repeated *wall* is bounded below by the longest step
  that still must run, and on this gate that step is unattributed and therefore never
  skippable -- so the work saved and the wall saved are different numbers and the report
  prints both. Quoting the first as if it were the second is how a scheduling change
  gets sold on a saving it cannot deliver.

One asymmetry with `packing-validate --since` is deliberate and is the reason this
module does its own selection call. For the CLI an empty change set means *nothing was
determined* and selects the whole gate, because it cannot tell a clean tree from a
failed diff. Between two named commits the git graph answers the stronger question, so
an empty diff here means *nothing changed* and every step is repeated work. That is the
case the daily schedule produces whenever `main` does not move for a day, and it is the
largest single source of repetition in the window this was written against.

Three questions are answered, and they are not the same question. `touches` reachability
is the one the cell asked for. The daily schedule's unmoved-tree runs fall out of it.
The third, `merge_identity`, was not asked for and turned out to be the largest of the
three: it counts the pushes to `main` whose git *tree id* -- an exact content address,
not a pattern -- equals that of the pull-request head merged, which means the
pull-request surface has already run against exactly those bytes.

What the module does **not** do is decide whether a repeated step is safe to skip.
`touches` is a conservative *selection* map, tuned so that being too wide costs time and
being too narrow costs a verdict; reading it backwards as a *skip* map inverts which
direction is safe. The attribution summary (`--attribution`) exists to make that risk
visible: it counts how many tracked files reach the escape hatch, which is the only
protection a mis-declared pattern has. And tree identity, exact as it is, addresses only
the tree: a step that also reads the clock, the git graph, the bead worktree or the
network is not a function of what the hash covers, and this module does not classify
which steps those are.

Usage, from `packing/`:

    uv run --frozen --all-extras --group dev packing-validate --format json > run.json
    uv run --frozen --all-extras --group dev python -m devtools.measure_gate_repetition \\
        --timings run.json --days 30
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Literal

from sqpack.cli.validate import STEPS, select_for_paths

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parent
WORKFLOW = REPO / ".github" / "workflows" / "packing-validation.yml"
#: The window the cell's kill condition is stated over: a skip rule may not have skipped
#: a step that caught a real failure in the last thirty days.
DEFAULT_DAYS = 30
#: The branch the deep surface runs on. `push: branches: [main]` in the workflow.
DEFAULT_REF = "origin/main"
#: `M H * * *`, the only cron shape this module claims to understand. Anything else is a
#: refusal: a schedule silently read as daily would put the wrong number of firings into
#: the denominator, and the denominator is the answer.
_DAILY_CRON = re.compile(r"^(\d{1,2})\s+(\d{1,2})\s+\*\s+\*\s+\*$")
_SCHEDULE_BLOCK = re.compile(r"^\s*-\s*cron:\s*[\"']?([^\"'\n]+?)[\"']?\s*$", re.MULTILINE)


class MeasurementError(Exception):
    """The inputs cannot support an answer, so no answer is given."""


@dataclass(frozen=True)
class Trigger:
    """One firing of the deep workflow, and the tree it ran against."""

    kind: Literal["push", "schedule"]
    when: datetime
    commit: str


@dataclass(frozen=True)
class Repetition:
    """What one deep run repeated, against the run before it."""

    trigger: Trigger
    previous: str
    changed: tuple[str, ...]
    must_run: tuple[str, ...]
    repeated: tuple[str, ...]
    unattributed: tuple[str, ...]
    repeated_seconds: float
    total_seconds: float
    wall_floor_seconds: float
    """The longest step that still has to run. No skip rule can take the wall below it."""

    @property
    def share(self) -> float:
        return self.repeated_seconds / self.total_seconds if self.total_seconds else 0.0

    @property
    def nothing_changed(self) -> bool:
        return not self.changed


def _git(*args: str) -> str:
    result = subprocess.run(
        ("git", *args), cwd=REPO, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise MeasurementError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def _read_summary(path: Path) -> tuple[dict[str, float], dict[str, str]]:
    """`(price by step name, non-passing status by step name)` for one run."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        raise MeasurementError(f"{path} is not readable: {error}") from error
    # `packing-validate --format json` prints a banner before the document when the
    # selection takes no gate marker, so the file is not JSON from byte zero. Parse the
    # whole thing first and fall back to the first line that opens an object; a file
    # that is not a document either way is still a refusal.
    for candidate in (text, text[text.find("\n{") + 1 :] if "\n{" in text else ""):
        if not candidate:
            continue
        try:
            payload = json.loads(candidate)
        except ValueError:
            continue
        break
    else:
        raise MeasurementError(f"{path} is not a readable JSON run summary")
    if not isinstance(payload, dict) or "results" not in payload:
        raise MeasurementError(
            f"{path} is not a `packing-validate --format json` summary "
            "(no `results` key); `--list --format json` is a different document"
        )
    results = payload["results"]
    if not isinstance(results, list):
        raise MeasurementError(f"{path} has a `results` key that is not a list")

    prices: dict[str, float] = {}
    unhealthy: dict[str, str] = {}
    for entry in results:
        if not isinstance(entry, dict):
            raise MeasurementError(f"{path} has a result entry that is not an object")
        name = str(entry.get("name", ""))
        prices[name] = float(entry.get("seconds", 0.0))
        status = str(entry.get("status", ""))
        if status != "passed":
            unhealthy[name] = status
    return prices, unhealthy


def load_prices(paths: Sequence[Path], *, allow_unhealthy: bool = False) -> dict[str, float]:
    """Per-step seconds from one or more `packing-validate --format json` summaries.

    More than one is allowed, later summaries winning, for the case that produced the
    option: a step added to the gate while a whole-gate run was in flight is priced by a
    second, narrow run (`--only`) rather than by a guess or by a repeat of the first.
    Every price is still somebody's clock.

    Three refusals over the union, and each of them is a way the arithmetic would
    otherwise lie:

    * a step in `STEPS` no summary prices would be repeated for free;
    * a priced step that is not in `STEPS` means the summary predates the gate it is
      being used to price, so every other price in it is suspect too;
    * a step the summary records as anything but *passed* is not priced by that summary.
      A skip costs about nothing. A failure is worse than that, because it can be an
      early abort: the run this was written against recorded `negative controls` at
      416.95 s where `D-366` measures it at about 1270 s, and taking the smaller figure
      would have understated by fourteen minutes exactly the step whose repetition was
      being priced. `--allow-unhealthy` takes the recorded seconds anyway and says so.

    A later summary that ran the step healthily clears an earlier summary's complaint,
    which is the point of accepting more than one.
    """
    if not paths:
        raise MeasurementError("no run summary was given, so nothing can be priced")
    prices: dict[str, float] = {}
    unhealthy: dict[str, str] = {}
    for path in paths:
        found, sick = _read_summary(path)
        prices.update(found)
        for name in found:
            unhealthy.pop(name, None)
        unhealthy.update(sick)

    declared = {step.name for step in STEPS}
    missing = sorted(declared - set(prices))
    extra = sorted(set(prices) - declared)
    sources = ", ".join(str(path) for path in paths)
    problems = [f"{sources} prices no step named {name!r}" for name in missing]
    problems.extend(
        f"{sources} prices {name!r}, which is not a step this gate declares" for name in extra
    )
    if not allow_unhealthy:
        problems.extend(
            f"{sources} records {name!r} as {status}, so its recorded seconds are not its cost"
            for name, status in sorted(unhealthy.items())
        )
    if problems:
        raise MeasurementError("; ".join(problems))
    return prices


def daily_schedule_utc(workflow: Path = WORKFLOW) -> tuple[int, int]:
    """The deep workflow's daily cron, as `(hour, minute)` UTC, read from the workflow."""
    try:
        text = workflow.read_text(encoding="utf-8")
    except OSError as error:
        raise MeasurementError(f"{workflow} is unreadable: {error}") from error
    crons = _SCHEDULE_BLOCK.findall(text)
    if len(crons) != 1:
        raise MeasurementError(
            f"{workflow.name} declares {len(crons)} cron schedules; this module prices a "
            "single daily one, so pass --no-schedule or teach it the new shape"
        )
    match = _DAILY_CRON.match(crons[0].strip())
    if match is None:
        raise MeasurementError(
            f"{workflow.name} declares the schedule {crons[0]!r}, which is not the daily "
            "`M H * * *` shape this module understands"
        )
    return int(match.group(2)), int(match.group(1))


def push_triggers(ref: str, *, since: datetime) -> list[Trigger]:
    """Every first-parent commit on `ref` at or after `since`, oldest first.

    First-parent because that is the sequence of pushes to `main`: a merge commit is one
    push whatever its branch contained, and the deep surface runs once for it.
    """
    out = _git(
        "log",
        ref,
        "--first-parent",
        f"--since={since.isoformat()}",
        "--format=%H%x00%cI",
    )
    triggers: list[Trigger] = []
    for line in out.splitlines():
        if not line.strip():
            continue
        commit, _, stamp = line.partition("\0")
        triggers.append(
            Trigger(
                kind="push",
                when=datetime.fromisoformat(stamp).astimezone(UTC),
                commit=commit,
            )
        )
    return sorted(triggers, key=lambda trigger: trigger.when)


def schedule_triggers(
    pushes: Sequence[Trigger], *, hour: int, minute: int, start: datetime, end: datetime
) -> list[Trigger]:
    """Every daily firing in the window, each against the tree `main` had at the time.

    A firing before the first push in the window has no tree to name and is dropped: the
    question is what a run repeated against the run before it, and there is no such run.
    """
    if not pushes:
        return []
    firings: list[Trigger] = []
    day = start.astimezone(UTC).replace(hour=hour, minute=minute, second=0, microsecond=0)
    while day <= end:
        if day >= start:
            earlier = [push for push in pushes if push.when <= day]
            if earlier:
                firings.append(Trigger(kind="schedule", when=day, commit=earlier[-1].commit))
        day += timedelta(days=1)
    return firings


def changed_between(base: str, head: str) -> tuple[str, ...]:
    """Repo-relative paths that differ between two commits, renames not collapsed.

    `--no-renames` for the reason `changed_paths` gives: rename detection reports only
    the destination, so a file moved out of an attributed subtree would drop the path
    that named the steps it used to reach.
    """
    if base == head:
        return ()
    out = _git("diff", "--name-only", "--no-renames", "-z", base, head, "--")
    return tuple(sorted(entry for entry in out.split("\0") if entry))


def price_repetition(trigger: Trigger, previous: str, prices: dict[str, float]) -> Repetition:
    """What one run repeats, given the run before it."""
    return repetition_for_changes(
        trigger, previous, changed_between(previous, trigger.commit), prices
    )


def repetition_for_changes(
    trigger: Trigger,
    previous: str,
    changed: Sequence[str],
    prices: dict[str, float],
) -> Repetition:
    """The arithmetic, with the git call already done.

    Separated from `price_repetition` so the rule that decides what repeats can be
    tested against a stated change set rather than against whatever the repository
    happens to contain on the day.
    """
    total = sum(prices[step.name] for step in STEPS)
    if not changed:
        # The git graph answers "nothing changed", which `--since` cannot: for the CLI an
        # empty change set means "nothing was determined" and selects the whole gate.
        return Repetition(
            trigger=trigger,
            previous=previous,
            changed=(),
            must_run=(),
            repeated=tuple(step.name for step in STEPS),
            unattributed=(),
            repeated_seconds=total,
            total_seconds=total,
            wall_floor_seconds=0.0,
        )
    selection = select_for_paths(list(changed))
    must_run = tuple(step.name for step in selection.steps)
    running = set(must_run)
    repeated = tuple(step.name for step in STEPS if step.name not in running)
    return Repetition(
        trigger=trigger,
        previous=previous,
        changed=tuple(changed),
        must_run=must_run,
        repeated=repeated,
        unattributed=selection.unattributed_paths,
        repeated_seconds=sum(prices[name] for name in repeated),
        total_seconds=total,
        wall_floor_seconds=max((prices[name] for name in must_run), default=0.0),
    )


@dataclass(frozen=True)
class MergeIdentity:
    """One push to `main`, and whether its tree had already been validated."""

    merge: str
    head: str
    identical: bool


def merge_identity(ref: str = DEFAULT_REF, *, days: int = DEFAULT_DAYS) -> list[MergeIdentity]:
    """Pushes to `ref` whose tree is byte-identical to the pull-request head merged.

    This is the one exact content address available here, and it is stronger than
    anything `touches` can offer: a git tree id is the hash of the tree, so equal ids
    mean equal bytes for every tracked file, with no pattern to get wrong. When a merge
    commit's tree equals its second parent's, the pull-request surface has already run
    against exactly these bytes and gone green -- that is what let the merge happen.

    What that licenses is bounded and the bound is the whole finding: it licenses
    skipping steps whose verdict is a function of *the tree*. It licenses nothing for a
    step that also reads the clock, the git graph, the bead worktree, or the network,
    because none of those is inside the hash.
    """
    out = _git(
        "log", ref, "--first-parent", "--merges", f"--since={days}.days", "--format=%H %P"
    )
    rows: list[MergeIdentity] = []
    for line in out.splitlines():
        parts = line.split()
        if len(parts) < 3:
            continue
        merge, head = parts[0], parts[2]
        rows.append(
            MergeIdentity(
                merge=merge,
                head=head,
                identical=_git("rev-parse", f"{merge}^{{tree}}").strip()
                == _git("rev-parse", f"{head}^{{tree}}").strip(),
            )
        )
    return rows


def measure(
    *,
    prices: dict[str, float],
    ref: str = DEFAULT_REF,
    days: int = DEFAULT_DAYS,
    schedule: bool = True,
    now: datetime | None = None,
) -> list[Repetition]:
    """Every deep run in the window, priced against the run before it."""
    end = (now or datetime.now(UTC)).astimezone(UTC)
    start = end - timedelta(days=days)
    pushes = push_triggers(ref, since=start)
    if len(pushes) < 2:
        raise MeasurementError(
            f"{ref} has {len(pushes)} first-parent commits in the last {days} days, so "
            "there is no interval to price; widen --days or name another --ref"
        )
    triggers = list(pushes)
    if schedule:
        hour, minute = daily_schedule_utc()
        triggers.extend(
            schedule_triggers(pushes, hour=hour, minute=minute, start=start, end=end)
        )
    triggers.sort(key=lambda trigger: trigger.when)
    return [
        price_repetition(trigger, triggers[index - 1].commit, prices)
        for index, trigger in enumerate(triggers)
        if index > 0
    ]


def attribution_reach() -> tuple[int, int, int]:
    """`(tracked, claimed, unclaimed)` over the tracked files of the repository.

    `claimed` is the count a step with a non-empty `touches` matches. `unclaimed` is what
    can still reach `select_for_paths`'s escape hatch, and it is the only thing standing
    between a mis-declared pattern and a step that silently stops running -- so its size
    is the honest measure of how much protection the escape hatch is actually providing.
    """
    tracked = [entry for entry in _git("ls-files", "-z").split("\0") if entry]
    claimed = sum(
        1
        for path in tracked
        if any(step.touches and step.reachable_from(path) for step in STEPS)
    )
    return len(tracked), claimed, len(tracked) - claimed


def _render_text(
    rows: Sequence[Repetition], *, attribution: bool, merges: Sequence[MergeIdentity]
) -> None:
    total_work = sum(row.total_seconds for row in rows)
    repeated_work = sum(row.repeated_seconds for row in rows)
    idle = [row for row in rows if row.nothing_changed]
    escaped = [row for row in rows if row.unattributed]
    print(f"== {len(rows)} deep runs, each priced against the run before it ==")
    print(f"{'when':17} {'kind':9} {'paths':>6} {'runs':>5} {'repeat s':>9} {'share':>7}")
    for row in rows:
        print(
            f"{row.trigger.when:%Y-%m-%d %H:%M} "
            f"{row.trigger.kind:9} "
            f"{len(row.changed):6} "
            f"{len(row.must_run):5} "
            f"{row.repeated_seconds:9.1f} "
            f"{row.share:6.1%}"
        )
    print()
    print(f"  work in one full run          {rows[0].total_seconds:9.1f}s")
    print(f"  work over the window          {total_work:9.1f}s")
    share = repeated_work / total_work
    print(f"  repeated work over the window {repeated_work:9.1f}s  ({share:.1%})")
    print(f"  runs against an unmoved tree  {len(idle):9} of {len(rows)}")
    print(f"  runs the escape hatch widened {len(escaped):9} of {len(rows)}")
    floors = [row.wall_floor_seconds for row in rows if not row.nothing_changed]
    if floors:
        print(
            f"  wall floor, worst interval    {max(floors):9.1f}s  "
            "(the longest step that still has to run)"
        )
    if merges:
        same = sum(1 for row in merges if row.identical)
        print()
        print("== pushes to main whose tree a pull request had already validated ==")
        print(f"  merges in the window          {len(merges):9}")
        print(
            f"  tree identical to the head    {same:9}  ({same / len(merges):.1%}); the "
            "pull-request surface ran on exactly these bytes"
        )
    if attribution:
        tracked, claimed, unclaimed = attribution_reach()
        print()
        print("== what the patterns claim ==")
        print(f"  tracked files                 {tracked:9}")
        print(f"  claimed by some `touches`     {claimed:9}  ({claimed / tracked:.1%})")
        print(f"  can reach the escape hatch    {unclaimed:9}  ({unclaimed / tracked:.1%})")


def _as_json(rows: Iterable[Repetition]) -> str:
    return json.dumps(
        [
            {
                "when": row.trigger.when.isoformat(),
                "kind": row.trigger.kind,
                "commit": row.trigger.commit,
                "previous": row.previous,
                "changed_paths": len(row.changed),
                "must_run": list(row.must_run),
                "repeated": list(row.repeated),
                "unattributed_paths": list(row.unattributed),
                "repeated_seconds": round(row.repeated_seconds, 3),
                "total_seconds": round(row.total_seconds, 3),
                "wall_floor_seconds": round(row.wall_floor_seconds, 3),
            }
            for row in rows
        ],
        indent=2,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="measure_gate_repetition",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--timings",
        required=True,
        action="append",
        type=Path,
        metavar="FILE",
        default=[],
        help=(
            "a `packing-validate --format json` summary, which is where prices come "
            "from; repeat to price a step added after the whole-gate run"
        ),
    )
    parser.add_argument(
        "--ref", default=DEFAULT_REF, help="the branch the deep surface runs on"
    )
    parser.add_argument(
        "--days", type=int, default=DEFAULT_DAYS, metavar="N", help="window, in days"
    )
    parser.add_argument(
        "--no-schedule",
        action="store_true",
        help="price only pushes, ignoring the workflow's daily cron",
    )
    parser.add_argument(
        "--allow-unhealthy",
        action="store_true",
        help=(
            "price steps the summary recorded as skipped or failed at their recorded "
            "seconds; a failed step's seconds can be an early abort"
        ),
    )
    parser.add_argument(
        "--attribution",
        action="store_true",
        help="also report how many tracked files can still reach the escape hatch",
    )
    parser.add_argument(
        "--no-merge-identity",
        action="store_true",
        help="skip the tree-identity count over merges, which costs two git calls each",
    )
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    namespace = _parser().parse_args(argv)
    try:
        prices = load_prices(namespace.timings, allow_unhealthy=namespace.allow_unhealthy)
        rows = measure(
            prices=prices,
            ref=namespace.ref,
            days=namespace.days,
            schedule=not namespace.no_schedule,
        )
        merges = (
            []
            if namespace.no_merge_identity
            else merge_identity(namespace.ref, days=namespace.days)
        )
    except MeasurementError as error:
        print(f"gate repetition: {error}", file=sys.stderr)
        return 1
    if namespace.format == "json":
        print(_as_json(rows))
    else:
        _render_text(rows, attribution=namespace.attribution, merges=merges)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
