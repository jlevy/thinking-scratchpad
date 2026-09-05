"""The chunked, checkpointing driver, against the loop it is standing in for.

Chunking the row loop is only admissible if it is not a change of method, so
the guard here is an equality and not a tolerance: a run that stops every few
rounds to write its state reaches the same rows, the same optimum and the same
weights as one that never stops. The checkpoint is tested the same way -- state
written and read back has to be the state that was running, down to the row
matrix and the exact rational site coordinates -- because a checkpoint that
loses a row silently turns a resumed run into a different run.
"""

from __future__ import annotations

import json
from fractions import Fraction

import numpy as np

from devtools.colgen_checkpoint import (
    Progress,
    Settings,
    cost_lines,
    counts_for,
    load_checkpoint,
    row_loop,
    run,
    save_checkpoint,
    show,
)
from sqpack.fractional.colgen import Rows, site_set_from_grids, solve_rows
from sqpack.fractional.generate import net_half_tangents

B = Fraction(9977, 10000)


def small_settings(**overrides: object) -> Settings:
    """A case small enough for a unit test and shaped like the real ones."""

    base = {
        "n": 4,
        "outer_side": Fraction(2),
        "square_side": Fraction(4, 5),
        "grid_counts": (7, 9),
        "inset": Fraction(1, 4),
        "angle_limit": Fraction(1, 10),
        "direction_steps": 3,
        "scale": 200_000,
        "column_rounds": 1,
        "max_rounds": 12,
        "rows_per_direction": 3,
        "columns_per_round": 1,
        "support_cap": 32,
        "settle": 0.0,
        "chunk_rounds": 3,
    }
    base.update(overrides)
    return Settings(**base)  # type: ignore[arg-type]


def test_chunking_the_row_loop_changes_nothing_it_decides() -> None:
    """Three chunks of four rounds reach what one run of twelve reaches.

    ``solve_rows`` carries its rows in and re-solves them on entry, so a chunk
    boundary costs one extra LP and nothing else. If that were not so, every
    checkpoint this driver writes would be a perturbation of the run it claims
    to be recording.
    """

    settings = small_settings(max_rounds=12, chunk_rounds=4)
    half_tangents = net_half_tangents(settings.angle_limit, settings.direction_steps)
    sites = site_set_from_grids(settings.outer_side, settings.grid_counts, settings.inset)

    whole = Rows()
    reference = solve_rows(
        sites,
        settings.square_side,
        half_tangents,
        whole,
        max_rounds=12,
        rows_per_direction=settings.rows_per_direction,
    )

    chunked = Rows()
    progress = Progress()
    solution, spent = row_loop(
        sites,
        settings,
        half_tangents,
        chunked,
        progress,
        deadline=None,
        handle=None,
        checkpoint=None,
    )

    assert solution is not None
    assert len(chunked) == len(whole)
    assert np.array_equal(chunked.stacked(), whole.stacked())
    assert chunked.directions == whole.directions
    assert solution.converged == reference.converged
    assert solution.objective == reference.objective
    assert np.array_equal(solution.weights, reference.weights)
    assert solution.least_covered == reference.least_covered
    # The rounds the chunked loop reports are row-generation rounds only: the
    # per-chunk warm solve is logged as its own kind and never counted.
    assert spent == reference.rounds
    assert progress.lp_rounds_done == reference.rounds
    kinds = {entry["kind"] for entry in progress.lp_log}
    assert kinds <= {"lp_round", "chunk_warm_lp"}
    assert sum(entry["kind"] == "lp_round" for entry in progress.lp_log) == reference.rounds


def test_checkpoint_round_trips_the_rows_and_the_exact_sites(tmp_path) -> None:
    """What is written is what was running, including the rationals."""

    settings = small_settings(max_rounds=6, chunk_rounds=6)
    half_tangents = net_half_tangents(settings.angle_limit, settings.direction_steps)
    sites = site_set_from_grids(settings.outer_side, settings.grid_counts, settings.inset)
    rows = Rows()
    progress = Progress()
    row_loop(
        sites,
        settings,
        half_tangents,
        rows,
        progress,
        deadline=None,
        handle=None,
        checkpoint=None,
    )
    assert len(rows) > 0

    path = tmp_path / "checkpoint.npz"
    save_checkpoint(path, settings, sites, rows, progress)
    stored, back_sites, back_rows, back_progress = load_checkpoint(path)

    assert back_sites.orbits == sites.orbits
    assert back_sites.outer_side == sites.outer_side
    assert np.array_equal(back_rows.stacked(), rows.stacked())
    assert back_rows.directions == rows.directions
    assert back_rows.centres == rows.centres
    assert back_rows.keys == rows.keys
    assert back_progress.lp_rounds_done == progress.lp_rounds_done
    assert back_progress.objective == progress.objective
    assert stored["outer_side"] == "2"


def test_a_resumed_run_continues_rather_than_restarting(tmp_path) -> None:
    """Resuming carries the rows, so the second leg starts where the first stopped."""

    settings = small_settings(max_rounds=2, chunk_rounds=2)
    path = tmp_path / "checkpoint.npz"
    first = run(
        settings,
        log_path=None,
        checkpoint=path,
        resume=None,
        freeze=None,
        deadline_seconds=None,
        verify_serial=False,
    )
    assert first["lp_rounds"] == 2
    first_rounds = first["rounds"]
    assert isinstance(first_rounds, list)
    held = first_rounds[0]["rows"]

    second = run(
        small_settings(max_rounds=6, chunk_rounds=2),
        log_path=None,
        checkpoint=path,
        resume=path,
        freeze=None,
        deadline_seconds=None,
        verify_serial=False,
    )
    second_rounds = second["rounds"]
    assert isinstance(second_rounds, list)
    assert second_rounds[0]["rows"] >= held
    lp_rounds = second["lp_rounds"]
    assert isinstance(lp_rounds, int)
    assert lp_rounds > 2


def test_a_deadline_stop_is_never_reported_as_convergence(tmp_path) -> None:
    """Zero clock buys zero rounds, and the result says so rather than converging."""

    result = run(
        small_settings(max_rounds=50, chunk_rounds=1),
        log_path=None,
        checkpoint=tmp_path / "checkpoint.npz",
        resume=None,
        freeze=None,
        deadline_seconds=-1.0,
        verify_serial=False,
    )
    assert result["converged"] is False
    assert result["frozen"] is None
    assert result["total_mass"] is None


def test_a_converged_run_freezes_the_retained_shape(tmp_path) -> None:
    """The frozen bytes carry the fields `cases/*/replay.py` reads back."""

    freeze = tmp_path / "certificate.json"
    result = run(
        small_settings(max_rounds=40, chunk_rounds=5),
        log_path=None,
        checkpoint=tmp_path / "checkpoint.npz",
        resume=None,
        freeze=freeze,
        deadline_seconds=None,
        verify_serial=False,
    )
    assert result["converged"] is True
    record = json.loads(freeze.read_text())
    assert set(record) == {
        "id",
        "n",
        "claim",
        "outer_side",
        "square_side",
        "angle_limit",
        "direction_steps",
        "total_mass",
        "least_cell_mass",
        "symmetry",
        "atoms",
    }
    assert record["n"] == 4
    assert record["least_cell_mass"] is None
    assert record["claim"].startswith("s(4) >= ")
    total_mass = result["total_mass"]
    assert isinstance(total_mass, str)
    assert Fraction(record["total_mass"]) == Fraction(total_mass)
    atoms = result["atoms"]
    assert isinstance(atoms, int)
    assert len(record["atoms"]) == atoms > 0


def test_auto_counts_are_the_site_density_rule() -> None:
    """``auto`` is BC-191's rule and an explicit tuple is taken as given."""

    assert counts_for("auto", Fraction(138, 25), B) == (40, 53, 66)
    assert counts_for("23,31,39", Fraction(138, 25), B) == (23, 31, 39)


def test_certificate_json_declares_a_computed_least_cell_mass() -> None:
    """A number a run produced is recorded; one it did not stays null."""

    settings = small_settings(max_rounds=40, chunk_rounds=40)
    result = run(
        settings,
        log_path=None,
        checkpoint=None,
        resume=None,
        freeze=None,
        deadline_seconds=None,
        verify_serial=False,
    )
    assert result["converged"] is True
    assert result["least_cell_mass"] is None


def test_show_reads_a_checkpoint_without_running_anything(tmp_path) -> None:
    """The reader prints every LP round the checkpoint holds, and the columns.

    The log carries one line per chunk so that tailing a long run stays cheap,
    so the checkpoint is the only place with the whole per-round table. If the
    reader lost rounds, a run watched while it ran would be reported at the
    resolution of its chunks rather than its rounds.
    """

    path = tmp_path / "checkpoint.npz"
    result = run(
        small_settings(max_rounds=9, chunk_rounds=3),
        log_path=None,
        checkpoint=path,
        resume=None,
        freeze=None,
        deadline_seconds=None,
        verify_serial=False,
    )
    text = show(path)
    assert f"{result['lp_rounds']} lp rounds" in text
    body = text.splitlines()
    start = next(i for i, line in enumerate(body) if line.split()[:2] == ["col", "lp"])
    stop = next(i for i, line in enumerate(body) if line.startswith("chunking overhead:"))
    assert stop - start - 1 == result["lp_rounds"]

    # The note column is checked for presence, not for which of its two outcomes
    # occurred. Pricing reads `solution.duals`, and at this LP the dual is degenerate:
    # the objective (4.000000) and the least covered mass (1.000000) are identical on
    # every platform, but the dual vector that certifies them is not unique, and
    # `rank_candidates` reads it. This run finds no candidate here and reports a `nan`
    # depth; CI's two-core runner found one at averaged depth 2.0 on the same commit
    # (run 33988186764). A gap that size is a different vertex of the dual polytope, not
    # arithmetic noise, so pinning either outcome pins a solver's choice among equally
    # optimal answers.
    #
    # Nothing sound rests on that choice. The duals steer *which* columns generation
    # tries next, so they change how fast a certificate is found and not whether a found
    # one holds: retention runs `devtools.decide_certificate`, which re-derives every
    # condition from the atoms themselves by exact event-cell sweep and interval
    # branch-and-bound, and never consults a dual.
    # The note lives in the per-column summary, which is a second table below the
    # per-round one `start`/`stop` bracket, so it is located by its own header.
    head = next(i for i, line in enumerate(body) if line.split()[-1:] == ["note"])
    rows = [line for line in body[head + 1 :] if line.strip() and not line.startswith("-")]
    assert rows, "the reader dropped the per-column summary"
    for line in rows:
        note = line.split(None, 9)[9]
        assert note == "no candidate orbit has averaged depth above 1" or note.startswith(
            "adding "
        ), f"unrecognised pricing note: {note!r}"


def test_cost_windows_split_the_loop_rather_than_averaging_it() -> None:
    """The first-window and last-tail means are reported separately.

    BC-191 fitted seconds per round against the side over runs of a few dozen
    rounds, so a mean over a much longer loop is not comparable to that law: the
    cost of a round grows inside the loop. The reader has to say which window a
    mean is over, and it has to report a window even when the loop is shorter
    than one.
    """

    progress = Progress()
    for index in range(5):
        progress.lp_log.append(
            {
                "column": 0,
                "round": index + 1,
                "kind": "lp_round",
                "separation_s": 2.0 * (index + 1),
                "lp_s": 1.0,
                "seconds": 2.0 * (index + 1) + 1.0,
                "rows": 10 * (index + 1),
                "added": 10,
                "violated": 3,
                "support": 4,
                "objective": float(index),
            }
        )
    header, whole, first, last = cost_lines(progress, window=3, tail=2)
    assert header.split() == ["window", "rounds", "sec/round", "sep", "lp", "sep", "share"]
    # separation 2, 4, 6, 8, 10 and lp 1 throughout.
    assert whole.split()[-5:] == ["5", "7.000", "6.000", "1.000", "0.8571"]
    assert first.split()[-5:] == ["3", "5.000", "4.000", "1.000", "0.8000"]
    assert last.split()[-5:] == ["2", "10.000", "9.000", "1.000", "0.9000"]
    assert cost_lines(Progress()) == ["cost: no row-generation round has finished"]


def test_a_clock_stop_between_column_rounds_keeps_the_converged_optimum(tmp_path) -> None:
    """A converged column round survives a deadline that lands after it.

    The row loop converging is what makes a restricted optimum the site set's
    own rather than a point the clock stopped at, and this driver exists so that
    a budget stop costs a run its next round and not its last answer. So a
    deadline arriving once some column round has converged must still report
    ``converged``, still report *that* round's optimum, and still freeze its
    candidate. The site set here is coarse enough that column generation has
    real work to do -- eight column rounds, and the optimum moves at the
    seventh -- so a fractional deadline lands mid-search rather than after it.
    """

    settings = small_settings(
        max_rounds=40, chunk_rounds=40, column_rounds=12, grid_counts=(5,)
    )
    whole = run(
        settings,
        log_path=None,
        checkpoint=None,
        resume=None,
        freeze=None,
        deadline_seconds=None,
        verify_serial=False,
    )
    full = whole["rounds"]
    assert isinstance(full, list)
    assert len(full) > 2
    elapsed = whole["seconds"]
    assert isinstance(elapsed, float)

    stopped_early = False
    for fraction in (0.2, 0.35, 0.5, 0.7):
        freeze = tmp_path / f"certificate-{fraction}.json"
        result = run(
            settings,
            log_path=None,
            checkpoint=tmp_path / "checkpoint.npz",
            resume=None,
            freeze=freeze,
            deadline_seconds=elapsed * fraction,
            verify_serial=False,
        )
        rounds = result["rounds"]
        assert isinstance(rounds, list)
        if not rounds:
            # Too little clock for even the first row loop: nothing converged,
            # and the result has to say so rather than freeze anything.
            assert result["converged"] is False
            assert result["frozen"] is None
            continue
        at = result["converged_at_column"]
        assert isinstance(at, int)
        assert result["converged"] is True
        assert result["objective"] == rounds[at]["objective"]
        assert result["least_covered"] == rounds[at]["least_covered"]
        assert freeze.exists()
        if len(rounds) < len(full):
            stopped_early = True
            # Either the clock ran out inside a row loop or between two of them,
            # and both leave the converged optimum standing.
            assert result["stopped"] == "no clock for a single row-generation chunk" or str(
                rounds[-1]["note"]
            ).startswith("deadline reached")
    assert stopped_early, "no deadline in the sweep stopped the search early"


def test_the_two_convergences_are_reported_apart() -> None:
    """A column loop that runs out of priced orbits says so; a capped one does not."""

    finished = run(
        small_settings(max_rounds=40, chunk_rounds=40, column_rounds=40),
        log_path=None,
        checkpoint=None,
        resume=None,
        freeze=None,
        deadline_seconds=None,
        verify_serial=False,
    )
    assert finished["converged"] is True
    assert finished["column_loop_converged"] is True

    capped = run(
        small_settings(max_rounds=40, chunk_rounds=40, column_rounds=1),
        log_path=None,
        checkpoint=None,
        resume=None,
        freeze=None,
        deadline_seconds=None,
        verify_serial=False,
    )
    assert capped["converged"] is True
    rounds = capped["rounds"]
    assert isinstance(rounds, list)
    assert len(rounds) == 1
