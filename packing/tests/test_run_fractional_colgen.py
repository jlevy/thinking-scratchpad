"""Controls for the column-generation driver.

`devtools.run_fractional_colgen` exists because every generator run in the
record before it was made from a script that was not kept, and the covering
values register says so in as many words: for the `n = 12` rung at `99/25`,
"the record names no site set and retains no site, row or round count". A
driver only earns that if two things hold. Its `auto` site density has to be
BC-191's and not a second opinion, and the bytes it freezes have to be the
bytes a retained case package reads back -- otherwise a candidate it writes
cannot be decided by the gate or replayed by anything.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from cases.n12_fractional_certificate.replay import CERTIFICATE_PATH, snapshot
from devtools.run_fractional_colgen import (
    RunSettings,
    certificate_json,
    counts_for,
    round_table_from,
    run,
    seed_points_from,
    window_lattice,
)
from sqpack.fractional.colgen import site_counts_for_side

SIDE = Fraction(399, 100)
SHRINK = Fraction(9977, 10000)


def test_auto_counts_are_bc191s_site_density_and_nothing_else() -> None:
    assert counts_for("auto", SIDE, SHRINK) == site_counts_for_side(SIDE, SHRINK)
    assert counts_for("23,31,39", SIDE, SHRINK) == (23, 31, 39)


def test_frozen_bytes_replay_as_the_certificate_they_came_from() -> None:
    """Re-emitting a retained certificate reproduces the object, key for key.

    The retained file is the contract: a candidate this driver freezes has to
    parse through the same `replay._from_record` and carry the same
    declarations, or the case package's own gate cannot read it.
    """

    certificate, declared, _ = snapshot(CERTIFICATE_PATH)
    emitted = json.loads(certificate_json(certificate, declared["least_cell_mass"]))
    retained = json.loads(CERTIFICATE_PATH.read_text())
    assert set(emitted) == set(retained)
    for key in (
        "n",
        "claim",
        "outer_side",
        "square_side",
        "angle_limit",
        "direction_steps",
        "total_mass",
        "least_cell_mass",
        "symmetry",
    ):
        assert emitted[key] == retained[key], key
    assert emitted["atoms"] == retained["atoms"]


def test_a_candidate_with_no_verdict_declares_no_least_cell_mass() -> None:
    """Freezing is not deciding: the field stays null until something sweeps."""

    certificate, _, _ = snapshot(CERTIFICATE_PATH)
    assert json.loads(certificate_json(certificate, None))["least_cell_mass"] is None


def test_the_run_reports_a_row_per_round_and_freezes_what_it_found(tmp_path: Path) -> None:
    """One small end-to-end pass: the table, the summary and the frozen bytes.

    ``n = 1`` in a container two shrunk squares wide is the cheapest setting the
    loop still does real work at -- one direction, a three-by-three seed -- and
    it is here for the driver's plumbing, not for its arithmetic.
    """

    settings = RunSettings(
        n=1,
        outer_side=Fraction(2),
        square_side=Fraction(1),
        grid_counts=(3,),
        inset=Fraction(1, 2),
        angle_limit=Fraction(1, 10),
        direction_steps=1,
        scale=1000,
        column_rounds=1,
        max_rounds=4,
        rows_per_direction=2,
    )
    freeze = tmp_path / "candidate.json"
    result = run(settings, log_path=tmp_path / "run.log", freeze=freeze, verify_serial=False)

    assert result["settings"] == settings.as_dict()
    rounds = result["rounds"]
    assert isinstance(rounds, list)
    assert rounds
    assert round_table_from(result).count("\n") == len(rounds) + 1
    for entry in rounds:
        assert entry["seconds"] >= 0.0
        assert entry["sites"] >= 3
    if result["converged"]:
        # A converged loop leaves no placement short of mass one, and that is
        # the number the record reports beside the objective.
        least_covered = result["least_covered"]
        assert isinstance(least_covered, float)
        assert least_covered >= 1 - 1e-6
        assert freeze.exists()
        assert json.loads(freeze.read_text())["least_cell_mass"] is None
        assert result["total_mass"] is not None


def test_seed_sites_are_carried_to_the_new_side_by_the_map_named(tmp_path: Path) -> None:
    """``scale`` keeps wall distances in proportion, ``centre`` keeps the shape.

    Both are D4-equivariant about the container centre, so a certificate's
    symmetric atom set stays a union of orbits, and the weights are never read.
    """

    source = tmp_path / "seed.json"
    source.write_text(
        json.dumps(
            {
                "outer_side": "2",
                "atoms": [["1/2", "1/2", "1"], ["3/2", "1/2", "1"], ["1", "1", "7"]],
            }
        )
    )
    scaled = seed_points_from(source, Fraction(4), "scale")
    assert scaled == {
        (Fraction(1), Fraction(1)),
        (Fraction(3), Fraction(1)),
        (Fraction(2), Fraction(2)),
    }
    centred = seed_points_from(source, Fraction(4), "centre")
    assert centred == {
        (Fraction(3, 2), Fraction(3, 2)),
        (Fraction(5, 2), Fraction(3, 2)),
        (Fraction(2), Fraction(2)),
    }
    try:
        seed_points_from(source, Fraction(4), "shear")
    except ValueError as error:
        assert "seed map" in str(error)
    else:
        raise AssertionError("an unknown map was accepted")


def test_window_lattice_sits_inside_the_ceiling_windows_and_hits_every_row() -> None:
    """The lattice is what a sub-``m^2`` solution needs at direction 0.

    Each coordinate lies strictly inside its window ``[L - (m - k) B, k B]``,
    consecutive windows are exactly ``B`` apart, and the set is symmetric under
    ``x -> L - x``, so it is D4-closed. Above the ceiling there is no window.
    """

    side, shrink = Fraction(997, 200), Fraction(9977, 10000)
    m = 5
    delta = m * shrink - side
    assert delta == Fraction(35, 10000)
    lattice = window_lattice(21, side, shrink, 3)
    coordinates = sorted({x for x, _ in lattice})
    assert len(coordinates) == 12
    assert len(lattice) == 144
    for k in range(1, m):
        window = coordinates[3 * (k - 1) : 3 * k]
        low, high = side - (m - k) * shrink, k * shrink
        assert all(low < x < high for x in window), (k, window)
    # Windows are B apart, so the same offset in each hits every interval of
    # length B whose start lies in the container.
    for j in range(3):
        assert coordinates[3 + j] - coordinates[j] == shrink
    assert {side - x for x in coordinates} == set(coordinates)
    assert window_lattice(21, side, shrink, 0) == set()
    assert window_lattice(21, Fraction(9977, 2000), shrink, 3) == set()
    assert window_lattice(20, side, shrink, 1) == window_lattice(21, side, shrink, 1)


def test_the_row_log_holds_one_line_per_lp_round_as_it_lands(tmp_path: Path) -> None:
    """A run stopped inside a column round still leaves its per-round table.

    The log is written on append, so it is complete on disk before the run
    returns; here it is checked against the summary the run returns, which
    counts the same rounds.
    """

    settings = RunSettings(
        n=1,
        outer_side=Fraction(2),
        square_side=Fraction(1),
        grid_counts=(3,),
        inset=Fraction(1, 2),
        angle_limit=Fraction(1, 10),
        direction_steps=1,
        scale=1000,
        column_rounds=1,
        max_rounds=4,
        rows_per_direction=2,
        seed_windows=2,
    )
    row_log = tmp_path / "rows.log"
    result = run(settings, log_path=None, freeze=None, verify_serial=False, row_log=row_log)
    lines = row_log.read_text().splitlines()
    lp_log = result["lp_log"]
    assert isinstance(lp_log, list)
    assert len(lines) == len(lp_log) + 1
    assert lines[0].split()[:2] == ["lp", "rows"]
    rounds = result["rounds"]
    assert isinstance(rounds, list)
    assert sum(entry["lp_rounds"] for entry in rounds) == sum(
        1 for entry in lp_log if entry["index"] >= 0
    )
    # n = 1 in a side-2 container: m = 1, so no window exists and the seed is empty.
    assert result["seed_sites"] == 0
    recorded = result["settings"]
    assert isinstance(recorded, dict)
    assert recorded["seed_windows"] == 2


def test_a_deadline_stop_leaves_the_table_and_no_candidate(tmp_path: Path) -> None:
    """No clock buys no round, and the run says so rather than converging."""

    settings = RunSettings(
        n=1,
        outer_side=Fraction(2),
        square_side=Fraction(1),
        grid_counts=(3,),
        inset=Fraction(1, 2),
        angle_limit=Fraction(1, 10),
        direction_steps=1,
        scale=1000,
        column_rounds=1,
        max_rounds=4,
        rows_per_direction=2,
    )
    result = run(
        settings,
        log_path=None,
        freeze=tmp_path / "never.json",
        verify_serial=False,
        deadline_seconds=-1.0,
    )
    assert result["converged"] is False
    assert result["frozen"] is None
    assert str(result["stopped"]).startswith("deadline reached")
    assert not (tmp_path / "never.json").exists()
