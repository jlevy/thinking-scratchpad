"""Behavioral checks for the derived current-research handoff, and for `check_synopsis`'s
other reconciliations against artifacts the document restates."""

from __future__ import annotations

from pathlib import Path

import pytest

from devtools.check_synopsis import (
    check_case_interval,
    check_covering_value_reports,
    check_experiment_scope_claims,
    check_round_effort_claims,
    check_unprotected_fix_claims,
    load_agenda_items,
    reported_covering_sides,
    select_handoff_cell,
    select_handoff_target,
    select_latest_closeout,
    select_latest_terminal_session,
    session_handoff_key,
    spell,
)


def test_handoff_cell_is_selected_from_the_latest_session_action() -> None:
    items = [
        {"id": "BC-010", "bead": "think-old"},
        {"id": "BC-011", "bead": "think-next"},
    ]

    assert select_handoff_cell(items, "Resume BC-011 under think-next") == items[1]
    with pytest.raises(ValueError, match="exactly one agenda cell"):
        select_handoff_cell(items, "Compare BC-010 with BC-011")


def test_handoff_cells_are_loaded_across_agendas(tmp_path) -> None:
    paths = []
    for number, cell_id in enumerate(("BC-010", "BC-019"), start=1):
        path = tmp_path / f"agenda-{number:03}.md"
        path.write_text(
            f"---\nagenda:\n  items:\n  - id: {cell_id}\n    bead: think-{number}\n---\n",
            encoding="utf-8",
        )
        paths.append(path)

    items = load_agenda_items(reversed(paths))

    assert [item["id"] for item in items] == ["BC-010", "BC-019"]
    assert select_handoff_cell(items, "Continue BC-019") == items[1]


def test_handoff_target_accepts_one_standalone_bead_after_an_agenda() -> None:
    items = [{"id": "BC-019", "bead": "think-old"}]

    assert select_handoff_target(items, "Continue under think-fresh after publication") == (
        None,
        "think-fresh",
    )
    with pytest.raises(ValueError, match="exactly one bead"):
        select_handoff_target(items, "Choose think-first or think-second")


def test_handoff_chronology_uses_terminal_clock_before_start_order() -> None:
    coordinator = {
        "started_at": "2026-09-02T05:03:00Z",
        "deadline_at": "2026-09-02T15:03:00Z",
    }
    later_lane = {
        "started_at": "2026-09-02T08:23:00Z",
        "deadline_at": "2026-09-02T11:23:00Z",
    }

    assert session_handoff_key(coordinator, 78) > session_handoff_key(later_lane, 82)


def test_latest_handoff_ignores_live_session_with_later_deadline() -> None:
    terminal = {
        "status": "stopped",
        "started_at": "2026-09-02T05:03:00Z",
        "deadline_at": "2026-09-02T15:03:00Z",
    }
    live = {
        "status": "in_progress",
        "started_at": "2026-09-02T15:04:00Z",
        "deadline_at": "2026-09-02T20:04:00Z",
    }

    assert select_latest_terminal_session(
        [
            (Path("session-078-terminal.md"), terminal),
            (Path("session-083-live.md"), live),
        ]
    ) == (Path("session-078-terminal.md"), terminal)


def test_latest_closeout_uses_newest_terminal_agenda(tmp_path: Path) -> None:
    for number, status, with_closeout in (
        (14, "completed", True),
        (15, "completed", True),
        (16, "active", True),
    ):
        closeout = (
            "\n  closeout:\n    replanning:\n      selected:\n        bead: think-next"
            if with_closeout
            else ""
        )
        (tmp_path / f"agenda-{number:03}.md").write_text(
            f"---\nagenda:\n  status: {status}{closeout}\n---\n",
            encoding="utf-8",
        )

    selected = select_latest_closeout(tmp_path.glob("agenda-*.md"))

    assert selected is not None
    assert selected[0].name == "agenda-015.md"
    assert selected[1]["replanning"]["selected"]["bead"] == "think-next"


def test_unprotected_fix_claims_rejects_stale_duplicate() -> None:
    current = "108 fixes left no regression check behind."
    stale_duplicate = f"{current} Ninety-eight fixes left no regression check behind."

    assert check_unprotected_fix_claims(current, 108) == []
    problems = check_unprotected_fix_claims(stale_duplicate, 108)
    assert len(problems) == 1
    assert "(108)" in problems[0]


def test_round_effort_claims_reject_stale_duplicate() -> None:
    current = (
        "There are 44 terminal rounds registered in `series-000`. "
        "They record 1061 agent-minutes and 30.7 wall-minutes."
    )
    stale_duplicate = (
        f"{current}\n\nThere are 39 terminal rounds registered in `series-000`. "
        "They record 933 agent-minutes and 28.3 wall-minutes."
    )

    assert check_round_effort_claims(current, "44", "1061", "30.7") == []
    assert check_round_effort_claims(stale_duplicate, "44", "1061", "30.7")


def test_experiment_scope_claims_preserve_h024_prerequisite() -> None:
    current = "Exp-012 leaves H-024 unresolved because its formal prerequisite is unmet."
    promoted = "Exp-012 numerically reconstructs the source and refutes H-024."

    assert check_experiment_scope_claims(current) == []
    assert check_experiment_scope_claims(promoted)


def _quoted(sides: list[str]) -> str:
    if len(sides) == 1:
        return f"`{sides[0]}`"
    return ", ".join(f"`{side}`" for side in sides[:-1]) + f" and `{sides[-1]}`"


def _covering_prose(sides: list[str], count: str, recomputable: list[str]) -> str:
    one = len(recomputable) == 1
    verb = "is" if one else "are"
    tail = "it recomputes is a feasible mass" if one else "they recompute are feasible masses"
    return (
        f"{count} values have been reported for the restricted program, at sides "
        f"{_quoted(sides)}. {spell(len(recomputable)).capitalize()} of them {verb} "
        f"recomputable from a tracked artifact, at sides {_quoted(recomputable)}, "
        f"and what {tail}."
    )


def test_covering_value_reports_are_held_to_the_reach_tables_own_rows() -> None:
    """The synopsis said "only four restricted optima have ever been measured" and named
    four, while the generated reach table listed seven reports and showed one recomputable
    from a tracked artifact -- and that one a feasible mass, not an optimum.

    Both halves are derived from the register here rather than written down, so the
    control moves with the table when a covering value is next reported. It has moved
    twice already: seven sides became fourteen, and the one recomputable row became two
    when `T-021` retained a certificate at the side its own converged optimum reported.
    Neither number is pinned here -- pinning them is what made this control need three
    repairs -- so the premise is only that at least one row recomputes, which is what
    gives the misattribution check below something to be wrong about.
    """
    sides, recomputable = reported_covering_sides()
    assert recomputable, "premise: some row's report is its artifact's own mass"
    assert set(recomputable) <= set(sides)

    current = _covering_prose(sides, spell(len(sides)), recomputable)
    assert check_covering_value_reports(current) == []

    # The defect as it stood: a subset, described as measured optima.
    stale = (
        "only four restricted optima have ever been measured, at sides "
        + ", ".join(f"`{side}`" for side in sides[:3])
        + f" and `{sides[3]}`."
    )
    problems = check_covering_value_reports(stale)
    assert len(problems) == 2
    assert any("does not state the reported-covering-value count" in p for p in problems)
    assert any("no sentence names all" in p for p in problems)

    # A side the table reports nothing at.
    invented = check_covering_value_reports(
        _covering_prose([*sides[:-1], "4.90"], spell(len(sides)), recomputable)
    )
    assert any("4.90" in problem for problem in invented)

    # The recomputable claim is checked against which rows actually recompute.
    other = next(side for side in sides if side not in recomputable)
    misattributed = check_covering_value_reports(
        _covering_prose(sides, spell(len(sides)), [other])
    )
    assert len(misattributed) == 1
    assert "recomputable" in misattributed[0]
    assert other in misattributed[0]
    assert all(side in misattributed[0] for side in recomputable)

    # Naming a real recomputable side but leaving another one out is the same defect:
    # the claim is about which rows recompute, not about naming one that does.
    if len(recomputable) > 1:
        partial = check_covering_value_reports(
            _covering_prose(sides, spell(len(sides)), recomputable[:1])
        )
        assert len(partial) == 1
        assert "recomputable" in partial[0]


#: `n-011.md`'s front matter, as `check_case_interval` reads it.
CASE_FRONT = {
    "verified_upper_bound": {"value": "3.87708359002281417730789706010096"},
    "verified_lower_bound": {"value": "3.81", "exact_form": "381/100"},
}

CURRENT_TABLE = (
    "| Best known packing (upper bound) | `3.87708359002281417730789706010096…` "
    "| Walter Trump, 1979 |\n"
    "| Best certified lower bound | `381/100 = 3.81` | T-018 |\n"
    "| Bound gap | `0.067083590023` | the fourth-smallest open gap |\n"
)


def test_case_interval_accepts_the_table_the_front_matter_supports() -> None:
    assert check_case_interval(CURRENT_TABLE, CASE_FRONT) == []


def test_case_interval_rejects_the_lower_bound_left_at_the_displaced_rung() -> None:
    """D-450's own shape: the row kept Stromquist's value after T-018 displaced it."""
    stale = CURRENT_TABLE.replace("`381/100 = 3.81`", "`2 + 4/√5 = 3.788854382…`")

    problems = check_case_interval(stale, CASE_FRONT)

    assert len(problems) == 1
    assert "381/100" in problems[0]
    assert "3.81" in problems[0]


def test_case_interval_rejects_a_gap_computed_from_the_displaced_rung() -> None:
    stale = CURRENT_TABLE.replace("`0.067083590023`", "`0.088229208023`")

    problems = check_case_interval(stale, CASE_FRONT)

    assert len(problems) == 1
    assert "0.067083590023" in problems[0]


def test_case_interval_rejects_half_a_lower_bound_row() -> None:
    """Exact form current, decimal stale -- the way a two-figure row rots unevenly."""
    half = CURRENT_TABLE.replace("`381/100 = 3.81`", "`381/100 = 3.788854382…`")

    problems = check_case_interval(half, CASE_FRONT)

    assert len(problems) == 1
    assert "3.81" in problems[0]


def test_case_interval_rejects_an_upper_bound_that_is_not_the_records_digits() -> None:
    wrong = CURRENT_TABLE.replace("`3.87708359002281417730789706010096…`", "`3.8770835900229…`")

    problems = check_case_interval(wrong, CASE_FRONT)

    assert len(problems) == 1
    assert "3.87708359002281417730789706010096" in problems[0]


def test_case_interval_reports_a_row_it_cannot_find() -> None:
    renamed = CURRENT_TABLE.replace("| Bound gap |", "| Published gap |")

    assert check_case_interval(renamed, CASE_FRONT) == [
        "SYNOPSIS.md: fact table has no 'Bound gap' row"
    ]
