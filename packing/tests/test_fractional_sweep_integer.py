"""The integer sweep is the Fraction sweep, cell for cell.

`minimum_covered_mass` decides in ``int64`` on the weights' common scale and
falls back to ``Fraction`` arithmetic when that scale does not fit. The
``Fraction`` route is the one that decided every retained certificate through
2026-09-04 and is kept unchanged as the reference; these tests hold the two to
the same value *and the same witness cell*, direction by direction, and hold
the parallel direction loop to the serial one. Measured on 2026-09-04: one
direction of the 2260-atom n = 20 certificate took 39.35 s by Fraction and
0.86 s by integer; the whole verify took 5378 s and 38.7 s.
"""

# The scheduling bounds are private by design and cheap only as unit contracts; their
# public effect is a machine with more cores than this one.
# ruff: noqa: SLF001
# pyright: reportPrivateUsage=false

from __future__ import annotations

from fractions import Fraction

import pytest

from cases.n11_fractional_certificate.replay import FIRST_RUNG_PATH as N11_FIRST_RUNG
from cases.n11_fractional_certificate.replay import declared as n11_declared
from cases.n11_fractional_certificate.replay import load as n11_load
from cases.n12_fractional_certificate.replay import declared as n12_declared
from cases.n12_fractional_certificate.replay import load as n12_load
from cases.n17_fractional_certificate.replay import declared as n17_declared
from cases.n17_fractional_certificate.replay import load as n17_load
from cases.n20_fractional_certificate.replay import declared as n20_declared
from cases.n20_fractional_certificate.replay import load as n20_load
from sqpack.fractional import certificate as certificate_module
from sqpack.fractional import sweep
from sqpack.fractional.certificate import (
    Certificate,
    sweep_all_directions,
    sweep_direction_minimum,
    verify,
)
from sqpack.fractional.model import Atom, Direction
from sqpack.fractional.sweep import (
    minimum_covered_mass,
    minimum_covered_mass_fraction,
    minimum_covered_mass_integer,
    reduce_to_cells,
    reduce_to_spans,
    weight_scale,
)


def _small_certificate() -> Certificate:
    """A D4-closed handful of atoms at odd weights, so the scale is not a round number."""

    side = Fraction(3)
    centre = side / 2
    seeds = (
        (Fraction(1, 2), Fraction(3, 4), Fraction(3, 7)),
        (Fraction(1), Fraction(5, 4), Fraction(2, 3)),
        (Fraction(3, 2), Fraction(3, 2), Fraction(5, 11)),
    )
    atoms: dict[tuple[Fraction, Fraction], Fraction] = {}
    for x, y, w in seeds:
        dx, dy = x - centre, y - centre
        for px, py in ((dx, dy), (-dy, dx), (-dx, -dy), (dy, -dx)):
            for qx, qy in ((px, py), (-px, py)):
                atoms[(centre + qx, centre + qy)] = w
    limit, steps = Fraction(207107, 500000), 12
    return Certificate(
        n=6,
        outer_side=side,
        square_side=Fraction(9977, 10000),
        atoms=tuple(Atom(f"{k:03d}", x, y, w) for k, ((x, y), w) in enumerate(atoms.items())),
        half_tangents=tuple(limit * k / steps for k in range(steps + 1)),
        symmetry="D4",
    )


def test_the_weight_scale_is_the_common_denominator() -> None:
    certificate = _small_certificate()
    scale = weight_scale(certificate.atoms)
    assert scale == 3 * 7 * 11
    assert all((atom.weight * scale).denominator == 1 for atom in certificate.atoms)


def test_integer_and_fraction_sweeps_agree_on_every_direction_of_a_small_net() -> None:
    """Value and witness, at every direction, on a certificate whose scale is 231."""

    certificate = _small_certificate()
    scale = weight_scale(certificate.atoms)
    for direction in certificate.directions:
        reference = minimum_covered_mass_fraction(
            certificate.atoms, direction, certificate.outer_side, certificate.square_side
        )
        fast = minimum_covered_mass_integer(
            certificate.atoms, direction, certificate.outer_side, certificate.square_side, scale
        )
        assert fast == reference, direction.label


@pytest.mark.parametrize("index", [0, 1, 37, 90, 137, 180])
def test_integer_and_fraction_sweeps_agree_on_a_retained_rung(index: int) -> None:
    """The 373-atom n = 11 rung, at six directions including both ends of the net.

    All 181 directions were run once on 2026-09-04 with no mismatch in 145 s;
    six are enough to keep in the fast tier, and the ends of the net are where
    the rotated frame is furthest from the axis-aligned one.
    """

    certificate = n11_load(N11_FIRST_RUNG)
    direction = certificate.directions[index]
    reference = minimum_covered_mass_fraction(
        certificate.atoms, direction, certificate.outer_side, certificate.square_side
    )
    fast = minimum_covered_mass(
        certificate.atoms, direction, certificate.outer_side, certificate.square_side
    )
    assert fast == reference


def test_the_span_reduction_matches_the_independent_cell_reduction() -> None:
    """The spans expanded are the cells the reference computes on its own.

    Until 2026-09-05 ``reduce_to_cells`` was defined as the spans expanded, so the two
    agreed by construction and a wrong span geometry would have been wrong twice.
    PR 78's adversarial review re-implemented the reference reduction independently;
    this is now a check between two computations, at one direction.
    """

    certificate = n11_load(N11_FIRST_RUNG)
    direction = certificate.directions[53]
    spans = reduce_to_spans(
        certificate.atoms, direction, certificate.outer_side, certificate.square_side
    )
    cells = reduce_to_cells(
        certificate.atoms, direction, certificate.outer_side, certificate.square_side
    )
    assert cells.u_events == spans.u_events
    assert cells.v_events == spans.v_events
    expanded = [(i, j) for i, j0, j1 in spans.spans for j in range(j0, j1 + 1)]
    assert list(cells.cells) == expanded
    assert all(j0 <= j1 for _, j0, j1 in spans.spans)


def _admissible(
    certificate: Certificate, direction: Direction, point: tuple[Fraction, Fraction]
) -> bool:
    """Whether a rotated-frame centre maps back to a placement inside the container.

    ``centre_domain`` sends the container square ``[h, L - h]^2`` through the rotation
    ``(x, y) -> (c x + s y, -s x + c y)``; this applies the inverse and asks the same
    question in container coordinates, exactly.
    """

    u, v = point
    cosine, sine = direction.ux, direction.uy
    x, y = cosine * u - sine * v, sine * u + cosine * v
    half = certificate.square_side * (cosine + sine) / 2
    far = certificate.outer_side - half
    return half <= x <= far and half <= y <= far


@pytest.mark.slow
def test_every_reported_witness_is_an_admissible_centre_on_the_373_atom_rung() -> None:
    """D-449: the witness used to be the midpoint of the attaining event cell.

    Most reachable cells meet the admissible domain only in part, so on 158 of the 181
    directions of the n = 11 top rung the midpoint was a point at which no B-square is
    admissible at all. The value was right; the point was not a witness. The witness is
    now a point of the cell's intersection with the domain, on both routes, and this
    holds it there on every third direction of the first rung in the fast tier; the
    exhaustive walk below takes every direction of every retained certificate.
    """

    certificate = n11_load(N11_FIRST_RUNG)
    for direction in certificate.directions[::3]:
        _, witness = minimum_covered_mass(
            certificate.atoms, direction, certificate.outer_side, certificate.square_side
        )
        assert _admissible(certificate, direction, witness), direction.label


@pytest.mark.exhaustive_exact
def test_every_reported_witness_is_admissible_on_every_retained_certificate() -> None:
    """The strict-inside witness is a new hard-error path, so it is walked in full.

    All 181 directions of every retained top rung on the integer route: the reported
    witness is admissible, and the value is the one that rung's own record declares.

    The declared value is read from each artifact rather than written here. Four of them
    were pinned by hand until 2026-09-05, when T-021 moved the n = 20 pointer to 97/20
    and this test failed on a stale constant -- 50007/50000, the 24/5 rung's least cell
    mass -- while every witness it checked was admissible. A figure kept beside the
    artifact that owns it is the D-439 class, and a pointer that moves is exactly when
    it bites.
    """

    for load, declared_of in (
        (n11_load, n11_declared),
        (n12_load, n12_declared),
        (n17_load, n17_declared),
        (n20_load, n20_declared),
    ):
        certificate = load()
        declared = Fraction(declared_of()["least_cell_mass"])
        least: Fraction | None = None
        for direction in certificate.directions:
            value, witness = sweep_direction_minimum(certificate, direction)
            assert _admissible(certificate, direction, witness), direction.label
            least = value if least is None else min(least, value)
        assert least == declared


def test_the_public_integer_entry_point_refuses_an_overflowing_scaled_total() -> None:
    """A direct call cannot bypass the int64 obligation ``minimum_covered_mass`` checks."""

    atoms = (
        Atom("a", Fraction(1), Fraction(1), Fraction(2**62)),
        Atom("b", Fraction(1), Fraction(1), Fraction(2**62)),
    )
    direction = _small_certificate().directions[0]
    with pytest.raises(ValueError, match="safe int64 limit"):
        minimum_covered_mass_integer(atoms, direction, Fraction(3), Fraction(1), 1)


def test_a_scale_too_large_for_int64_falls_back_to_fractions(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Past the limit the integer route declines and the Fraction route decides.

    The limit is patched down rather than a certificate built up to it: a
    certificate whose scaled mass exceeds 2**60 would not fit in the fast tier.
    """

    certificate = _small_certificate()
    direction = certificate.directions[5]
    args = (certificate.atoms, direction, certificate.outer_side, certificate.square_side)
    expected = minimum_covered_mass_fraction(*args)
    monkeypatch.setattr(sweep, "_INTEGER_MASS_LIMIT", 1)
    calls: list[str] = []
    original = sweep.minimum_covered_mass_integer

    def spy(*a: object, **k: object) -> object:
        calls.append("integer")
        return original(*a, **k)  # type: ignore[arg-type]

    monkeypatch.setattr(sweep, "minimum_covered_mass_integer", spy)
    assert minimum_covered_mass(*args) == expected
    assert calls == [], "the integer route ran past its own limit"


def test_worker_counts_sit_under_the_core_worker_and_grid_caps(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """F38: a many-core host must not allocate one dense grid per core.

    The pool size is the request or the core count, under the worker cap and under the
    grid budget; a single grid over the budget runs one worker rather than refusing.
    """

    certificate = n11_load(N11_FIRST_RUNG)
    one_grid = certificate_module._estimated_grid_bytes(len(certificate.atoms))
    monkeypatch.setattr(certificate_module.os, "process_cpu_count", lambda: 64)
    monkeypatch.setattr(certificate_module, "_MAX_PARALLEL_WORKERS", 8)
    monkeypatch.setattr(certificate_module, "_PARALLEL_GRID_BUDGET_BYTES", 2 * one_grid)
    assert certificate_module._worker_count(certificate, None) == 2
    assert certificate_module._worker_count(certificate, 99) == 2
    assert certificate_module._worker_count(certificate, 1) == 1
    monkeypatch.setattr(certificate_module, "_PARALLEL_GRID_BUDGET_BYTES", one_grid - 1)
    assert certificate_module._worker_count(certificate, 99) == 1
    monkeypatch.setattr(certificate_module, "_PARALLEL_GRID_BUDGET_BYTES", 8 * one_grid)
    assert certificate_module._worker_count(certificate, None) == 8


def test_a_single_threaded_process_forks_and_a_threaded_one_without_a_main_runs_serially(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The pool's start method follows what is safe, not a fixed choice.

    Fork inherits the parent and asks nothing of ``__main__``, which is what a caller
    run from stdin needs; it is unsafe once the parent has other threads. Then the
    platform default stands if a worker can re-import ``__main__``, and otherwise the
    directions run in this process, which is slower and always correct.
    """

    monkeypatch.setattr(certificate_module.sys, "platform", "linux")
    main = certificate_module.sys.modules["__main__"]
    monkeypatch.setattr(main, "__file__", "<stdin>", raising=False)
    monkeypatch.setattr(certificate_module.threading, "active_count", lambda: 1)
    context = certificate_module._pool_context()
    assert context is not None
    assert context.get_start_method() == "fork"
    monkeypatch.setattr(certificate_module.threading, "active_count", lambda: 2)
    assert certificate_module._pool_context() is None
    monkeypatch.setattr(main, "__file__", __file__)
    context = certificate_module._pool_context()
    assert context is not None
    assert context.get_start_method() != "fork"

    class RefusePool:
        def __init__(self, *_args: object, **_kwargs: object) -> None:
            raise AssertionError("a threaded process without an importable main started a pool")

    monkeypatch.setattr(main, "__file__", "<stdin>", raising=False)
    monkeypatch.setattr(certificate_module, "ProcessPoolExecutor", RefusePool)
    small = _small_certificate()
    assert sweep_all_directions(small, workers=3) == sweep_all_directions(small, workers=1)


@pytest.mark.slow
def test_the_parallel_direction_loop_matches_the_serial_one() -> None:
    """Same minima, same order, same first-attaining label, whatever the schedule."""

    certificate = n11_load(N11_FIRST_RUNG)
    serial = sweep_all_directions(certificate, workers=1)
    parallel = sweep_all_directions(certificate, workers=3)
    assert parallel == serial
    assert [label for _, label in serial] == [d.label for d in certificate.directions]


@pytest.mark.slow
def test_the_n17_certificate_verifies_in_the_fast_tier_now() -> None:
    """1473 s by Fraction on 2026-09-04; 21.8 s here on a loaded four-core box.

    The exhaustive tests that decide every retained certificate still exist and
    still run in the full tier. This one is the fast tier's own proof that the
    decision the record cites is the decision the code makes today.
    """

    certificate = n17_load()
    verdict = verify(certificate)
    assert verdict.accepted, verdict.failures
    assert n17_declared()["least_cell_mass"] == str(verdict.minimum_cell_mass)
