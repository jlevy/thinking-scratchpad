#!/usr/bin/env python3
"""Refuse a tier ceiling that has drifted slack, and a tier that has no ceiling at all.

This is the static half of the gate's own cost check, and it is the half that would have
caught the 2026-08-30 state on the day. `validate.py` recorded `--fast` at 499s in a
docstring beside an 1800s cap: 3.61x of headroom, which cannot see a regression smaller
than 3.61x. The tier then tripled inside the cap and nothing objected.

Nothing here runs a tier or looks at a clock, so it costs a hundredth of a second, it
sits in the records tier, and it cannot be dismissed as a busy runner. It asserts three
things about `devtools/gate-budgets.yaml`:

* every tier `packing-validate` can select as a whole has a declared ceiling, so a new
  tier cannot arrive without one;
* every declared tier is a tier that exists, so a ceiling cannot outlive its tier; and
* every ceiling is within `policy.max_headroom` of the cost recorded for that tier, so a
  ceiling cannot quietly grow slack while the record stands still; and
* `development.md` names every tier, so the reader-facing statement of which tier runs
  where cannot silently stop covering one.

Usage:
    uv run --frozen --all-extras --group dev python -m devtools.check_gate_budgets
"""

from __future__ import annotations

import sys
from pathlib import Path

from sqpack.cli.validate import TIER_IDS
from sqpack.gate_budgets import BudgetError, Register, declaration_problems, load

ROOT = Path(__file__).resolve().parent.parent
#: Resolved from this file rather than from the installed package, so a negative control
#: that corrupts a snapshot's register is checking the snapshot's register. `sqpack` is
#: installed and resolves to the real checkout wherever it runs; `devtools` resolves to
#: whatever tree it was launched from, which is the tree the control mutated.
REGISTER = ROOT / "devtools" / "gate-budgets.yaml"
#: The contributor-facing statement of which tier runs where and at what cost. A tier
#: this document does not name is a tier nobody knows to run.
GUIDE = ROOT.parent / "development.md"


def coverage_problems(register: Register) -> list[str]:
    """Tiers with no ceiling, and ceilings with no tier."""
    declared = set(register.ids)
    selectable = set(TIER_IDS)
    problems = [
        f"tier {tier!r} can be selected but declares no ceiling in {register.path}"
        for tier in sorted(selectable - declared)
    ]
    problems.extend(
        f"tier {tier!r} declares a ceiling but packing-validate cannot select it"
        for tier in sorted(declared - selectable)
    )
    return problems


def documentation_problems(register: Register) -> list[str]:
    """Tiers `development.md` stops describing.

    The register is the machine's copy and the guide is the reader's, and the two drift in
    one direction: a tier gets added or renamed and the prose keeps describing the old
    shape. Naming is all that is checked -- the costs in the guide are explicitly a
    snapshot, and `packing-validate --budgets` is what it tells the reader to run -- but a
    tier the guide never mentions is one a contributor cannot know to choose.
    """
    try:
        text = GUIDE.read_text(encoding="utf-8")
    except OSError as error:
        return [f"{GUIDE.name} is unreadable: {error}"]
    problems = [
        f"{GUIDE.name} never names `{tier.command}`, so a reader cannot tell the "
        f"{tier.id} tier exists or who runs it"
        for tier in register.tiers
        if tier.command not in text
    ]
    if REGISTER.name not in text:
        problems.append(
            f"{GUIDE.name} does not cite {REGISTER.name}, which is where the ceilings it "
            "describes actually live"
        )
    return problems


def main() -> int:
    try:
        register = load(REGISTER)
    except BudgetError as error:
        print(f"gate budgets: {error}", file=sys.stderr)
        return 1
    problems = (
        coverage_problems(register)
        + declaration_problems(register)
        + documentation_problems(register)
    )
    if problems:
        for problem in problems:
            print(f"gate budgets: {problem}", file=sys.stderr)
        return 1
    recorded = sum(1 for tier in register.tiers if tier.measured_seconds is not None)
    print(
        f"gate budget declaration passed: {len(register.tiers)} tiers, {recorded} with a "
        f"recorded cost, all ceilings within {register.policy.max_headroom:g}x of it, "
        f"all named in {GUIDE.name}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
