#!/usr/bin/env python3
"""`verified_upper_bound` is a ceiling, and every reader of it has to be told so.

The name invites reading the field as "the verified exact value of s(n)". It is not.
It is the strongest upper bound this repository can certify from its own evidence, and
for a third of n <= 100 it is WEAKER than the best known construction two fields above
it -- by as much as 0.46, with `exact_form` set to the trivial grid integer. An agent
read "all 100 verified upper bounds carry an exact_form" as "all 100 side lengths are
exact algebraic numbers" and told a user so. The claim is false and the naming is why.

Renaming the field would touch the record generators, renderers and the validation CLI,
which this change does not own. So the relationship is documented instead, in the three
places a reader can actually meet the field, and these tests hold all three in place:

1. the schema, for anyone reading the contract;
2. the body of every record where the ceiling trails the report, for anyone reading one
   case;
3. a declared list of consumers, so no new code or document can name the field without
   someone deciding what it means there.
"""

from __future__ import annotations

import math
import re
from decimal import Decimal, localcontext
from pathlib import Path

import pytest
import yaml

from sqpack.assurance import bounds_agree_at_declared_precision

PROJECT_ROOT = Path(__file__).resolve().parents[1]
# The consumers of this field now span the repository: it is named in SYNOPSIS.md and
# in active plans, which sit above packing/.
REPO = PROJECT_ROOT.parent
FRONTIER = PROJECT_ROOT / "frontier"
SCHEMA = FRONTIER / "square-packing-case.schema.yaml"
CEILING_HEADING = "## The verified upper bound is a ceiling"

# Every file in the project that names `verified_upper_bound`, and what it does with it.
# A new entry is a decision, not a formality: the field is a ceiling, so a consumer that
# wants the best known side length wants `reported_upper_bound` instead, and a consumer
# that wants a proved side length has to check `status` first.
# Trees whose files may name the field without reading it, declared once rather than one
# file at a time. A tree qualifies only when its files are generated, when the field can
# appear in them as incidental identity rather than as a value anything consumes, and when
# a new file arrives on every run so a per-file list would be pure churn.
DECLARED_CONSUMER_TREES = {
    "packing/campaign/agent-sessions/": (
        "session records narrate work, and work touches this field, so every session that "
        "did any names it -- seven were declared one by one before this became a tree. "
        "They make no claim about any bound: a record saying a session moved a "
        "verified_upper_bound is reporting what happened, and the claim itself lives in "
        "the case record that moved. This is D-394's argument at a third level, and the "
        "list it was growing had started to grow for reasons unrelated to its purpose"
    ),
    "packing/campaign/resource-usage/": (
        "derived per-session measurement records. They never read the field: it reaches "
        "them as the name of a tool that ran, such as the test file that guards this very "
        "contract, and a rollup makes no claim about any bound"
    ),
}

DECLARED_CONSUMERS = {
    "packing/devtools/check_basic_bounds.py": (
        "checks the ceiling really is the certifiable grid bound"
    ),
    "packing/tests/test_certificate_citations.py": (
        "names the field in a fixture proving evidence refs are found in every block that "
        "carries one; it asserts nothing about the bound's value"
    ),
    "packing/devtools/render_evidence_inventory.py": (
        "names the field only as one of the case blocks that can carry evidence ids, so "
        "that citations can be counted; it reads no bound and makes no claim about what "
        "any of them is worth"
    ),
    "packing/devtools/price_gobel_family.py": (
        "says in prose that the four family sizes now certify the exact side rather than "
        "the grid ceiling, to keep its own coverage record from reading as a gap; it "
        "computes nothing from the field"
    ),
    "packing/devtools/check_golden_basins.py": (
        "reads the ceiling as an upper limit on a basin side"
    ),
    "packing/devtools/check_synopsis.py": (
        "reads the n = 11 case's ceiling from its front matter only to hold the synopsis's "
        "fact table to it: the table's upper row must be the record's own digits and the gap "
        "row their difference (D-452). It takes the field to mean exactly what the front "
        "matter means and asserts nothing about s(n)"
    ),
    "packing/tests/test_synopsis_handoff.py": (
        "names the field in a fixture standing in for the n = 11 front matter, so that the "
        "fact-table check can be driven on doctored tables; it asserts nothing about the "
        "bound's value"
    ),
    "packing/devtools/check_case_prose.py": (
        "reads the field as the ceiling the case's own front matter declares, only to "
        "hold that case's prose to it: a body that quotes an upper bound must quote the "
        "one its record carries (D-442). It takes the field to mean exactly what the "
        "front matter means and asserts nothing about s(n)"
    ),
    "packing/tests/test_case_prose.py": (
        "names the field in fixtures that give check_case_prose a front matter and a "
        "body to compare; the values are synthetic and prove the detector fires, not "
        "anything about a bound"
    ),
    "packing/campaign/explorations/X-009-where-a-new-packing-is-reachable.md": (
        "sequences the research blocks by how far each could move the ceiling; it treats "
        "the field as the certified ceiling throughout and states that every move of it "
        "is a reviewed change, never s(n)"
    ),
    "packing/devtools/controls.yaml": (
        "corrupts the field on purpose, to prove the checkers fire"
    ),
    "packing/devtools/migrate_frontier_v2.py": "builds the field from the v1 records",
    "packing/devtools/render_research_tables.py": (
        "renders it beside the report, never instead of it"
    ),
    "docs/project/specs/active/plan-2026-08-24-frontier-assurance-and-verification.md": (
        "the plan that introduced the reported/verified split"
    ),
    "packing/defects.yaml": (
        "D-367 cites the consumer contract as the nearest existing guard against the "
        "claim-boundary conflation it records, one level up from it"
    ),
    "packing/frontier/README.md": "documents the field for a reader of the corpus",
    "packing/frontier/evidence.yaml": (
        "names the fields as the certificate the grid bound lives in"
    ),
    "packing/frontier/square-packing-case.schema.yaml": "defines it",
    "packing/src/sqpack/assurance.py": (
        "compares report against ceiling and demands a blocker for any gap"
    ),
    "packing/tests/test_frontier_assurance_contract.py": "exercises those comparisons",
    "packing/tests/test_verified_upper_bound_contract.py": "this file",
    "SYNOPSIS.md": "names the field when describing the reported/verified split",
    "packing/campaign/agendas/agenda-005-symbolic-promotion-and-identity.md": (
        "plans promotion work that reads the ceiling, never as the value"
    ),
    "docs/project/specs/active/plan-2026-08-28-interval-certification.md": (
        "specs certification that would tighten the ceiling toward the report"
    ),
    "packing/campaign/research-loop-logbook/run-002-2026-08-29-overnight-promotion-blocks.md": (
        "reports how far below the ceiling the run's certificate sits, and that the "
        "ceiling did not move"
    ),
    "packing/campaign/ledger.md": (
        "generated: it renders the agenda notes below and inherits whatever they say, so "
        "it is an output of a consumer rather than one itself"
    ),
    "packing/cases/kingbird29/certify_interval.py": (
        "compares its bound against the ceiling and refuses to promote it"
    ),
    "packing/campaign/agendas/agenda-006-overnight-research-blocks.md": (
        "schedules that certification work, and says the ceiling does not move in the run"
    ),
    "packing/devtools/assess_frontier_rigidity.py": (
        "reads the ceiling only together with the floor, and only to confirm they pin the "
        "side at exactly k before making the perfect-square tiling argument; a one-sided "
        "read would not establish a tiling and is never made"
    ),
    "packing/tests/test_frontier_rigidity_assessment.py": (
        "exercises that two-sided pin, including the cases where it must refuse"
    ),
}

# Prose, code and hand-written records. Generated artifacts are excluded because they
# are outputs of the consumers below rather than consumers themselves: the atlas alone
# is 44 MB of them, and nothing hand-written in this project comes close to the cap.
SEARCHED_SUFFIXES = (".py", ".md", ".yaml", ".yml", ".rs")
SKIPPED_PARTS = {
    ".venv",
    "__pycache__",
    "resources",
    "target",
    ".pytest_cache",
    "results",
    "node_modules",
}
OWN_NAME = "test_verified_upper_bound_contract"
"""This file's own stem, which is not a mention of the field and must not read as one.

Citing the guard is not using the thing it guards. `defects.md` renders each defect's
`recorded_in` as a link and `D-392` is recorded here; a session record lists this file as
evidence. Both then "name" `verified_upper_bound` without any claim about a ceiling
anywhere in them, and declaring each one would grow the consumer list by a line every time
someone referred to this test -- churn with no signal, which is the same argument
`DECLARED_CONSUMER_TREES` already makes for generated trees.

Stripping the stem keeps the sweep pointed at what it is for. A document that discusses the
field still matches, because it cannot discuss it without writing the name outside a
filename.
"""

GENERATED_BYTES = 512 * 1024


def cases() -> dict[int, dict]:
    loaded: dict[int, dict] = {}
    for path in sorted(FRONTIER.glob("n-*.md")):
        payload = yaml.safe_load(path.read_text(encoding="utf-8").split("---\n")[1])["packing"]
        loaded[int(payload["n"])] = payload
    return loaded


def trailing_ceilings() -> dict[int, tuple[Decimal, Decimal]]:
    """Cases whose certified ceiling does not agree with the reported best known."""
    trailing: dict[int, tuple[Decimal, Decimal]] = {}
    for n, case in cases().items():
        reported = case["reported_upper_bound"]
        verified = case["verified_upper_bound"]
        if not bounds_agree_at_declared_precision(reported, verified):
            trailing[n] = (Decimal(reported["value"]), Decimal(verified["value"]))
    return trailing


@pytest.mark.slow
def test_a_third_of_the_corpus_certifies_a_weaker_bound_than_it_reports() -> None:
    trailing = trailing_ceilings()
    # Not a target to be held at any number; a measurement, and a loud one. Every one of
    # these is a case where reading `verified_upper_bound` as s(n) overstates the side
    # length. It was 33 until D-398 promoted n = 40, 65 and 89 off the integer grid ceiling
    # onto Goebel's exact family construction, whose certificates had been in the gate for
    # two sessions while the records still declared a mathematical blocker. Moving it down
    # is the point of the measurement, not a break in it: BC-089 took twelve cases off
    # the grid on 2026-08-31 -- n = 82 (the worst trailing gap, 0.464), the strip
    # family's 27, 38, 52, 67 and 84, the off-centre family's 26 and 85, and the lifted
    # witnesses 19 and 66 in Q(sqrt 2) and 18 and 86 in Q(sqrt 7) -- leaving n = 50's
    # 3/7 as the widest.
    assert len(trailing) == 18
    for n, (reported, verified) in trailing.items():
        assert verified > reported, n
    worst = max(verified - reported for reported, verified in trailing.values())
    assert worst > Decimal("0.42")

    # And in those cases `exact_form` is exact about the ceiling and says nothing about
    # s(n): for all but n = 29 it is literally the integer grid bound.
    grids = {
        n
        for n in trailing
        if cases()[n]["verified_upper_bound"]["exact_form"] == str(math.isqrt(n - 1) + 1)
    }
    assert sorted(set(trailing) - grids) == [29]

    # Every case carrying an exact_form on the ceiling, split by whether s(n) is known.
    exact_forms = sum(
        1 for case in cases().values() if case["verified_upper_bound"]["exact_form"]
    )
    proved = sum(1 for case in cases().values() if case["status"] == "proved")
    assert exact_forms == 100
    assert proved < exact_forms


def test_every_trailing_case_says_so_in_the_record_a_reader_opens() -> None:
    trailing = trailing_ceilings()
    for n, (reported, verified) in sorted(trailing.items()):
        body = _body(n)
        assert CEILING_HEADING in body, f"n={n} certifies a weaker ceiling and does not say so"
        section = body.split(CEILING_HEADING, 1)[1].split("\n## ", 1)[0]
        flat = " ".join(section.split())
        assert str(verified) in flat, n
        assert str(reported) in flat, n
        # Pin the precision. The gap is rendered into the record at Python's
        # default 28 digits, but decimal's context is process-global and
        # sqpack.field raises it to digits + 20 while refining an enclosure, so
        # a test running after one of those would otherwise compute a longer
        # rendering of the same number and call the record stale. The record is
        # not stale; the ambient precision moved. See the bead on that global
        # mutation.
        with localcontext() as context:
            context.prec = 28
            gap = str(verified - reported)
        assert gap in flat, n
        assert f"not the value of `s({n})`" in flat, n
        assert "`reported_upper_bound`" in flat, n

    # The section is a statement about this case, so it must not appear where the
    # ceiling does reach the report.
    for n in set(cases()) - set(trailing):
        assert CEILING_HEADING not in _body(n), n


def test_the_schema_states_what_the_field_is_and_is_not() -> None:
    schema = yaml.safe_load(SCHEMA.read_text(encoding="utf-8"))
    assert schema["properties"]["verified_upper_bound"] == {"$ref": "#/$defs/verifiedUpper"}
    definition = schema["$defs"]["verifiedUpper"]
    description = " ".join(definition["description"].split())
    assert "NOT the value of s(n)" in description
    assert "NOT a copy of reported_upper_bound" in description
    assert "status is proved" in description

    exact_form = " ".join(definition["properties"]["exact_form"]["description"].split())
    assert "never of s(n)" in exact_form
    assert "only when status is proved" in exact_form


def test_no_undeclared_consumer_reads_the_field() -> None:
    found: set[str] = set()
    for path in sorted(REPO.rglob("*")):
        if path.is_dir() or path.suffix not in SEARCHED_SUFFIXES:
            continue
        relative = path.relative_to(REPO)
        # Dot-directories hold vendored agent skills and tooling state, not our prose.
        if (
            SKIPPED_PARTS & set(relative.parts)
            or any(part.startswith(".") for part in relative.parts)
            or re.fullmatch(r"n-\d{3}\.md", path.name)
        ):
            continue
        # The size cutoff is a heuristic for generated blobs, and a declared consumer is
        # not a guess -- so it is scanned however large it has grown. `packing/defects.yaml`
        # crossed 512 KiB on 2026-08-30 and silently stopped being read, which is `D-392`.
        if (
            path.stat().st_size > GENERATED_BYTES
            and relative.as_posix() not in DECLARED_CONSUMERS
        ):
            continue
        body = path.read_text(encoding="utf-8", errors="ignore").replace(OWN_NAME, "")
        if "verified_upper_bound" in body:
            found.add(relative.as_posix())
    undeclared = sorted(
        path
        for path in found - set(DECLARED_CONSUMERS)
        if not path.startswith(tuple(DECLARED_CONSUMER_TREES))
    )
    assert undeclared == [], (
        "these name verified_upper_bound without saying what they take it to mean; "
        "it is a ceiling, not s(n) -- add them to DECLARED_CONSUMERS with a reason"
    )
    stale = sorted(set(DECLARED_CONSUMERS) - found)
    assert stale == [], "declared consumers that no longer read the field"


def _body(n: int) -> str:
    return (FRONTIER / f"n-{n:03d}.md").read_text(encoding="utf-8").split("---\n", 2)[2]
