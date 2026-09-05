#!/usr/bin/env python3
"""Every terminal session names the full gate that certified it, on a commit in its history.

`OR-13` says every fast check runs in CI, and the gate is what makes that mean something.
Nothing said that the gate had *run*. Forty-seven of the eighty-six terminal sessions
mention a gate somewhere in `checks`, and seven of those name any commit at all; the rest
are sentences like "the record gate passed on the closed tree", which is a claim about a
tree nobody can now identify.

**The commit matters as much as the verdict.** A full gate run on a tree three commits
behind the handover certifies nothing about what was handed over, and a check that accepts
a bare `full gate: passed` is a check that will accept exactly that. So the declaration
carries three things -- the tier, the commit, and the verdict -- in one canonical line of
`checks`, and this refuses a terminal session that cannot produce one.

The grammar lives in `campaign/schemas/agent-session.schema.yaml` under
`$defs/full_gate_declaration`, and is read from there rather than restated here, so the
record's contract and the check that enforces it cannot drift apart.

What each rule refuses:

* a terminal session at or after `GATE_DECLARED_FROM` with no declaration at all;
* a `checks` item that opens with `full gate:` and then does not parse, so a near miss is
  a failure rather than an item this quietly skips;
* a tier `packing-validate` cannot select, and a tier that is real but smaller than the
  gate (`records`, `edit`, `push`), so a record cannot claim more than it ran;
* a declared commit that exists here and is **not an ancestor of HEAD**.

**Ancestry that cannot be resolved is uncheckable, not false.** `conventions.md` §6 draws
this line for recorded engine commits and it is drawn the same way here: a checkout that
does not contain the commit is not evidence the commit was orphaned. Concretely --

* no Git history reachable at all (the negative-control sandbox is a source snapshot with
  no `.git`, and so is a source tarball): every declaration is reported as unresolved and
  nothing fails on ancestry;
* a **shallow** repository that lacks the commit: reported by name with the remedy, and
  nothing fails, because that is the case `conventions.md` names;
* a **complete** repository that lacks the commit: that is a failure. Shallowness is the
  only innocent explanation for a missing object, and it has been ruled out.

Grammar and presence are checked in every one of those cases. Only the ancestry clause
depends on Git.

Usage, from `packing/`:
    uv run --frozen --all-extras --group dev python -m devtools.check_session_gate
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Literal

from sqpack.cli.validate import TIER_IDS
from sqpack.yamlio import safe_load

ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO = ROOT.parent
SESSIONS = ROOT / "campaign" / "agent-sessions"
SCHEMA = ROOT / "campaign" / "schemas" / "agent-session.schema.yaml"

TERMINAL = {"completed", "stopped"}

GATE_DECLARED_FROM = "session-087"
"""Sessions numbered below this closed before a full-gate declaration was required.

The same device `check_session_rollups` uses for `resource_rollups`, and for the same
reason: a boundary cannot quietly grow into a list of exemptions, because a new session is
above it by construction and moving it is a visible edit. Eighty-six terminal records
predate the rule and are named in the output rather than silently skipped.

It is set *at* the session that introduced the rule, not after it -- `resource_rollups`
was pinned at `session-045`, the session whose twenty-three ungated phases were the
evidence for it. A rule whose first act is to exempt its own author is a rule nobody has
run.
"""

CERTIFYING_TIERS = frozenset({"fast", "full"})
"""The tiers that certify a handover; the others may be declared but do not.

`full` runs every declared step. `fast` is the tier CI makes a required check on every
pull request (`BC-214`), so it is the one that actually stands between a branch and
`main`. `records`, `edit` and `push` are each strictly smaller -- `--records` is six
seconds of record checks, `--edit` is `--fast` minus the broad steps, and `--push` is
`--edit` plus only the tests reachable from the change -- so a session that ran one of
them has not run the gate, and saying so is the whole point of recording the tier.
"""

DECLARATION_PREFIX = "full gate:"
"""What makes a `checks` item a claim about the gate.

Prefix matching rather than keyword sniffing, so that the set of items this adjudicates is
decidable by a reader. The cost is that a session can describe a gate run in prose the
prefix does not claim; that prose is then not a declaration and the session still has to
write one.
"""

GROUPS = ("tier", "commit", "verdict", "note")
"""What the schema's positional capture groups mean, in order."""

type CommitState = Literal["reachable", "orphaned", "absent"]
type HistoryState = Literal["complete", "shallow", "unavailable"]


@dataclass(frozen=True)
class GateRun:
    """One parsed full-gate declaration."""

    tier: str
    commit: str
    verdict: str
    note: str | None

    @property
    def certifies(self) -> bool:
        """Does this run, taken at its word, certify a handover?"""
        return self.tier in CERTIFYING_TIERS and self.verdict == "passed"


def declaration_pattern() -> re.Pattern[str]:
    """The canonical grammar, read from the schema that publishes it.

    Read rather than restated so the record's contract and the check that enforces it have
    one definition between them. The groups are positional, not named: a JSON Schema
    `pattern` is ECMA-262, whose named-group syntax Python's `re` does not accept, and a
    pattern that only one of the two consumers can compile is not a shared definition.
    """
    schema = safe_load(SCHEMA.read_text(encoding="utf-8"))
    definitions = schema.get("$defs", {}) if isinstance(schema, dict) else {}
    declaration = definitions.get("full_gate_declaration", {})
    pattern = declaration.get("pattern") if isinstance(declaration, dict) else None
    if not isinstance(pattern, str):
        message = f"{SCHEMA} declares no $defs/full_gate_declaration/pattern"
        raise TypeError(message)
    compiled = re.compile(pattern)
    if compiled.groups != len(GROUPS):
        message = (
            f"{SCHEMA} declares a full_gate_declaration pattern with {compiled.groups} "
            f"groups; this reads {len(GROUPS)}: {', '.join(GROUPS)}"
        )
        raise ValueError(message)
    return compiled


def parse_declaration(item: str, pattern: re.Pattern[str]) -> GateRun | None:
    """Parse one canonical declaration, or refuse it by returning None."""
    match = pattern.fullmatch(item.strip())
    if match is None:
        return None
    tier, commit, verdict, note = match.groups()
    return GateRun(tier=tier, commit=commit, verdict=verdict, note=note)


def claims_a_gate(item: object) -> bool:
    """Is this `checks` item making a claim this checker has to adjudicate?"""
    return isinstance(item, str) and item.strip().lower().startswith(DECLARATION_PREFIX)


def _git(repository: pathlib.Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ("git", "-C", str(repository), *arguments),
        capture_output=True,
        text=True,
        check=False,
    )


def history_state(repository: pathlib.Path) -> HistoryState:
    """How much of this checkout's history an ancestry question can be asked of."""
    if _git(repository, "rev-parse", "--git-dir").returncode != 0:
        return "unavailable"
    if _git(repository, "rev-parse", "--verify", "HEAD").returncode != 0:
        return "unavailable"
    shallow = _git(repository, "rev-parse", "--is-shallow-repository")
    if shallow.returncode != 0:
        return "unavailable"
    return "shallow" if shallow.stdout.strip() == "true" else "complete"


def commit_state(repository: pathlib.Path, commit: str) -> CommitState:
    """Is this commit in this checkout, and is it behind HEAD?

    Three states, never two. Collapsing `absent` into `orphaned` is the mistake
    `conventions.md` §6 names: not finding an object is a fact about the checkout, and
    being off the current history is a fact about the commit.
    """
    if _git(repository, "cat-file", "-e", f"{commit}^{{commit}}").returncode != 0:
        return "absent"
    ancestry = _git(repository, "merge-base", "--is-ancestor", commit, "HEAD").returncode
    if ancestry not in {0, 1}:
        return "absent"
    return "reachable" if ancestry == 0 else "orphaned"


def sessions(directory: pathlib.Path | None = None) -> list[tuple[pathlib.Path, dict]]:
    """Every session record's frontmatter, in file order."""
    found: list[tuple[pathlib.Path, dict]] = []
    for path in sorted((directory or SESSIONS).glob("session-*.md")):
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            continue
        payload = safe_load(text.split("---\n")[1])
        if isinstance(payload, dict) and isinstance(payload.get("session"), dict):
            found.append((path, payload["session"]))
    return found


def declaration_problems(
    name: str, session: dict, pattern: re.Pattern[str]
) -> tuple[list[str], list[GateRun]]:
    """Refusals arising from the record alone, plus the runs it parsed."""
    problems: list[str] = []
    runs: list[GateRun] = []
    checks = session.get("checks")
    items = checks if isinstance(checks, list) else []
    for item in items:
        if not claims_a_gate(item):
            continue
        run = parse_declaration(str(item), pattern)
        if run is None:
            problems.append(
                f"{name}: a checks item claims a gate run and does not parse: "
                f"{str(item).strip()!r}; the form is "
                "'full gate: <tier> at <commit>: passed|failed'"
            )
            continue
        if run.tier not in TIER_IDS:
            problems.append(
                f"{name}: declares tier {run.tier!r}, which packing-validate cannot "
                f"select; the tiers are {', '.join(sorted(TIER_IDS))}"
            )
            continue
        runs.append(run)
    if not runs:
        return problems, runs
    if not any(run.certifies for run in runs):
        declared = ", ".join(f"{run.tier}:{run.verdict}" for run in runs)
        problems.append(
            f"{name}: declares a gate run ({declared}) but none of them certifies the "
            f"handover; that needs a passed run of {' or '.join(sorted(CERTIFYING_TIERS))}"
        )
    return problems, runs


def ancestry_problems(
    name: str, runs: list[GateRun], history: HistoryState, repository: pathlib.Path
) -> tuple[list[str], list[str]]:
    """Refusals and unresolved declarations arising from the Git graph."""
    problems: list[str] = []
    unresolved: list[str] = []
    certifying = [run for run in runs if run.certifies]
    if not certifying:
        return problems, unresolved
    if history == "unavailable":
        unresolved.extend(f"{name} -> {run.commit} (no Git history here)" for run in certifying)
        return problems, unresolved
    reachable = 0
    for run in certifying:
        state = commit_state(repository, run.commit)
        if state == "reachable":
            reachable += 1
        elif state == "orphaned":
            problems.append(
                f"{name}: declares a {run.tier} gate at {run.commit}, which is in this "
                "history and is not an ancestor of HEAD; a gate run off the handover's "
                "own history certifies nothing about what was handed over"
            )
        elif history == "shallow":
            unresolved.append(f"{name} -> {run.commit} (shallow checkout)")
        else:
            problems.append(
                f"{name}: declares a {run.tier} gate at {run.commit}, which is in no "
                "local history of this complete checkout; shallowness is the only "
                "innocent reading of an absent object and this checkout is not shallow"
            )
    if reachable == 0 and not problems and not unresolved:
        problems.append(f"{name}: no declared gate commit could be resolved")
    return problems, unresolved


def main(argv: list[str] | None = None) -> int:
    """Adjudicate every terminal session's full-gate declaration."""
    _ = argv
    pattern = declaration_pattern()
    history = history_state(REPO)
    problems: list[str] = []
    unresolved: list[str] = []
    grandfathered: list[str] = []
    certified = 0
    unverified = 0

    for path, session in sessions():
        identifier = str(session.get("id", path.stem))
        if str(session.get("status")) not in TERMINAL:
            continue
        record_problems, runs = declaration_problems(path.name, session, pattern)
        if identifier < GATE_DECLARED_FROM and not runs and not record_problems:
            grandfathered.append(identifier)
            continue
        if not runs and not record_problems:
            problems.append(
                f"{path.name}: terminal session names no full-gate run; add one checks "
                "item of the form 'full gate: fast at <commit>: passed', naming the "
                "commit the gate actually ran on"
            )
            continue
        problems.extend(record_problems)
        graph_problems, graph_unresolved = ancestry_problems(path.name, runs, history, REPO)
        problems.extend(graph_problems)
        unresolved.extend(graph_unresolved)
        if record_problems or graph_problems:
            continue
        # Counted apart, because they are different claims. A session is *certified* only
        # where this checkout could resolve its commit and found it behind HEAD; where the
        # checkout could not answer, the record is well formed and nothing more, and
        # rolling the two into one number is how "uncheckable" turns into "checked".
        if graph_unresolved:
            unverified += 1
        else:
            certified += 1

    for line in problems:
        print(f"FAIL {line}", file=sys.stderr)
    if problems:
        return 1
    print(f"  {certified} terminal sessions name a full-gate run on a commit in their history")
    if certified == 0 and unverified == 0:
        print(
            f"    none yet: the rule binds from {GATE_DECLARED_FROM}, which has not closed. "
            "Every terminal record from there on must carry the declaration"
        )
    if unresolved:
        print(
            f"  {unverified} more are well formed and their ancestry is UNCHECKABLE here "
            f"({history} history), which is not evidence against them:"
        )
        for line in unresolved:
            print(f"    {line}")
        print("    `git fetch --unshallow` is what makes these checkable")
    if grandfathered:
        print(
            f"  {len(grandfathered)} closed before the rule existed and are not checked: "
            f"{grandfathered[0]}..{grandfathered[-1]} ({len(grandfathered)} sessions)"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
