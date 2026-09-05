"""Controls for the interval-certified decision of fractional certificates.

The exact verifier and this one must agree on the retained certificates, but
agreement alone is not the control: two decisions that could only fail the
same way would agree while both wrong. So the tests check the interval
primitives against exact rational arithmetic directly, check the box bounds
against exact covered masses at sampled points, reproduce a published bound the
verifier was not built against, and exercise both refusal paths. The
coincidence test at the end pins down the one thing this method cannot decide
and confirms it is reported as undecided rather than accepted.
"""

from __future__ import annotations

import random
import warnings
from fractions import Fraction

import numpy as np
import pytest

from cases.n11_fractional_certificate.replay import load as load_n11
from cases.n12_fractional_certificate.replay import FIRST_RUNG_PATH
from cases.n12_fractional_certificate.replay import declared as declared_n12
from cases.n12_fractional_certificate.replay import load as load_n12
from cases.n17_fractional_certificate.replay import declared as declared_n17
from cases.n17_fractional_certificate.replay import load as load_n17
from cases.n20_fractional_certificate.replay import declared as declared_n20
from cases.n20_fractional_certificate.replay import load as load_n20
from sqpack.fractional import interval as interval_module
from sqpack.fractional.certificate import Certificate
from sqpack.fractional.interval import (
    BATCH,
    MAX_INTERVAL_ATOMS,
    AtomData,
    DirectionSearch,
    Interval,
    IntervalInputError,
    doubled_net,
    rotation_from_half_tangent,
    searches,
    verify_by_intervals,
)
from sqpack.fractional.model import Atom, Direction
from sqpack.fractional.sweep import minimum_covered_mass
from tests.test_fractional_certificate import retained_certificate

# A sub-net of the doubled net that touches both ends, the middle, and the
# reflected half. It decides a weaker statement than the full net and is used
# only to keep the quick tests quick; the full-net decisions follow below.
SUB_NET = ("0", "1", "45", "90", "135", "180", "1'", "90'", "180'")

CONDITION5 = "Condition 5 every admissible centre covers mass 1"

# The n = 12 case file moves as the ladder climbs; the 393/100 rung this verifier was
# asked to decide is retained under its own name, and both are decided below.
RETAINED_393_100 = FIRST_RUNG_PATH.with_name("certificate-393-100.json")


def _exact_rotation(tangent: Fraction) -> tuple[Fraction, Fraction]:
    denominator = 1 + tangent * tangent
    return (1 - tangent * tangent) / denominator, 2 * tangent / denominator


def _rotated(
    certificate: Certificate, rotation: tuple[Fraction, Fraction]
) -> list[tuple[Fraction, Fraction, Fraction]]:
    """The atoms in the rotated frame, exactly, so many points can be scored."""
    cosine, sine = rotation
    return [
        (cosine * atom.x + sine * atom.y, cosine * atom.y - sine * atom.x, atom.weight)
        for atom in certificate.atoms
    ]


def _exact_mass(
    certificate: Certificate,
    rotation: tuple[Fraction, Fraction],
    point: tuple[Fraction, Fraction],
    rotated: list[tuple[Fraction, Fraction, Fraction]] | None = None,
) -> Fraction:
    """Mass of the closed B-square centred at ``point`` in the rotated frame."""
    u, v = point
    half = certificate.square_side / 2
    atoms = _rotated(certificate, rotation) if rotated is None else rotated
    return sum(
        (weight for au, av, weight in atoms if abs(au - u) <= half and abs(av - v) <= half),
        start=Fraction(0),
    )


def _exactly_admissible(
    certificate: Certificate,
    rotation: tuple[Fraction, Fraction],
    point: tuple[Fraction, Fraction],
) -> bool:
    cosine, sine = rotation
    u, v = point
    x, y = cosine * u - sine * v, sine * u + cosine * v
    h = certificate.square_side * (cosine + sine) / 2
    return h <= x <= certificate.outer_side - h and h <= y <= certificate.outer_side - h


def _search(certificate: Certificate, label: str) -> DirectionSearch:
    for search in searches(certificate, AtomData.of(certificate)):
        if search.label == label:
            return search
    raise KeyError(label)


# --- the arithmetic ---------------------------------------------------------


def test_rational_enclosures_bracket_the_rational_and_dyadics_are_points() -> None:
    for value in (
        Fraction(1, 3),
        Fraction(207107, 500000),
        Fraction(-7, 11),
        Fraction(22529, 5000),
    ):
        enclosure = Interval.of(value)
        assert Fraction(enclosure.lo) <= value <= Fraction(enclosure.hi)
        assert enclosure.lo != enclosure.hi
    assert Interval.of(Fraction(3, 8)).width == 0
    assert Interval.of(5).width == 0


def test_every_operation_rounds_outward_around_the_exact_result() -> None:
    """The one property everything else rests on, checked against Fractions.

    ``Fraction(float)`` is exact, so the exact result of each operation on the
    sampled floats is known and must lie inside the enclosure.
    """
    rng = random.Random(20260904)
    for _ in range(400):
        a = Fraction(rng.uniform(-5, 5)) if rng.random() < 0.5 else Fraction(rng.randint(-9, 9))
        b = Fraction(rng.uniform(0.01, 5))
        ia, ib = Interval.of(a), Interval.of(b)
        for exact, enclosure in (
            (a + b, ia + ib),
            (a - b, ia - ib),
            (a * b, ia * ib),
            (a / b, ia / ib),
        ):
            assert Fraction(enclosure.lo) <= exact <= Fraction(enclosure.hi)


def test_division_refuses_a_divisor_that_may_be_zero() -> None:
    with pytest.raises(ZeroDivisionError):
        _ = Interval(1.0, 2.0) / Interval(0.0, 1.0)


def test_rotation_enclosures_contain_the_exact_rotation() -> None:
    certificate = load_n12()
    for index in (0, 1, 57, 180):
        tangent = certificate.half_tangents[index]
        cosine, sine = _exact_rotation(tangent)
        rotation = rotation_from_half_tangent(str(index), tangent)
        assert Fraction(rotation.cosine.lo) <= cosine <= Fraction(rotation.cosine.hi)
        assert Fraction(rotation.sine.lo) <= sine <= Fraction(rotation.sine.hi)
        assert rotation.cosine.width < 1e-14
    assert rotation_from_half_tangent("0", Fraction(0)).sine.lo == 0


def test_the_doubled_net_reflects_every_direction_but_the_upright_one() -> None:
    tangents = load_n12().half_tangents
    net = doubled_net(tangents)
    assert len(net) == 2 * len(tangents) - 1
    forward = {rotation.label: rotation for rotation in net[: len(tangents)]}
    for rotation in net[len(tangents) :]:
        source = forward[rotation.label.rstrip("'")]
        assert rotation.cosine == source.sine
        assert rotation.sine == source.cosine
    with pytest.raises(ValueError, match=r"outside \[0, 1\)"):
        rotation_from_half_tangent("bad", Fraction(1))


# --- the bounds, against exact arithmetic ----------------------------------


@pytest.mark.slow
def test_box_bounds_bracket_the_exact_mass_at_sampled_centres() -> None:
    """A lower bound over a box and an upper bound at a point, both exact-checked.

    The sampled points are floats, so their exact positions are known and the
    exact covered mass there is a Fraction sum. The interval lower bound of any
    small box around the point must not exceed it, and the point upper bound
    must not fall below it.
    """
    certificate = load_n12()
    rng = np.random.default_rng(17)
    for label, index in (("57", 57), ("57'", 57), ("0", 0)):
        search = _search(certificate, label)
        tangent = certificate.half_tangents[index]
        cosine, sine = _exact_rotation(tangent)
        rotation = (sine, cosine) if label.endswith("'") else (cosine, sine)
        rotated = _rotated(certificate, rotation)
        lo = search.initial[0]
        us = rng.uniform(lo[0], lo[1], 200)
        vs = rng.uniform(lo[2], lo[3], 200)
        radius = rng.uniform(0, 0.01, 200)
        boxes = np.stack([us - radius, us + radius, vs - radius, vs + radius], axis=1)
        lower = search.lower_bound(boxes)
        upper = search.upper_bound_at(us, vs)
        for k in range(200):
            point = (Fraction(us[k]), Fraction(vs[k]))
            exact = _exact_mass(certificate, rotation, point, rotated)
            assert Fraction(int(lower[k]), search.scale) <= exact
            assert exact <= Fraction(int(upper[k]), search.scale)


def test_tightening_never_loses_an_admissible_centre() -> None:
    """The domain step encloses ``box intersect domain``; check it on exact points."""
    certificate = load_n12()
    rng = np.random.default_rng(5)
    for label, index in (("57", 57), ("1'", 1), ("0", 0)):
        search = _search(certificate, label)
        tangent = certificate.half_tangents[index]
        cosine, sine = _exact_rotation(tangent)
        rotation = (sine, cosine) if label.endswith("'") else (cosine, sine)
        lo = search.initial[0]
        kept = 0
        for _ in range(60):
            a, b = sorted(rng.uniform(lo[0], lo[1], 2))
            c, d = sorted(rng.uniform(lo[2], lo[3], 2))
            tight = search.tighten(np.array([[a, b, c, d]]))[0]
            for _ in range(20):
                point = (Fraction(rng.uniform(a, b)), Fraction(rng.uniform(c, d)))
                if not _exactly_admissible(certificate, rotation, point):
                    continue
                kept += 1
                assert Fraction(tight[0]) <= point[0] <= Fraction(tight[1])
                assert Fraction(tight[2]) <= point[1] <= Fraction(tight[3])
        assert kept > 100


def test_a_provably_admissible_centre_is_exactly_admissible() -> None:
    certificate = load_n12()
    rng = np.random.default_rng(3)
    search = _search(certificate, "120")
    cosine, sine = _exact_rotation(certificate.half_tangents[120])
    lo = search.initial[0]
    us = rng.uniform(lo[0], lo[1], 2000)
    vs = rng.uniform(lo[2], lo[3], 2000)
    admissible = search.admissible(us, vs)
    assert 0 < admissible.sum() < 2000
    for k in np.flatnonzero(admissible):
        assert _exactly_admissible(
            certificate, (cosine, sine), (Fraction(us[k]), Fraction(vs[k]))
        )


# --- acceptance ---------------------------------------------------------------


@pytest.mark.slow
def test_both_n12_certificates_certify_every_direction_of_the_sub_net() -> None:
    """A sub-net run certifies its directions and decides nothing about the rest.

    Until PR 78's adversarial review (its F6) an all-certified sample came back
    ``accepted``; a run over one direction of 361 is a control, not a claim, and
    the verdict says so by staying undecided. The per-direction outcomes are
    what a control reads.
    """
    for certificate in (load_n12(RETAINED_393_100), load_n12()):
        verdict = verify_by_intervals(certificate, directions=SUB_NET)
        assert not verdict.accepted
        assert len(verdict.directions) == len(SUB_NET)
        assert all(outcome.status == "certified" for outcome in verdict.directions)
        assert sum(outcome.stalled for outcome in verdict.directions) == 0
        assert verdict.conditions[-1].status == "undecided"


def test_the_retained_n11_certificate_certifies_the_sub_net_without_a_verdict() -> None:
    verdict = verify_by_intervals(load_n11(), directions=SUB_NET)
    assert not verdict.accepted
    assert all(outcome.status == "certified" for outcome in verdict.directions)
    assert verdict.total_mass == Fraction(434547, 40000)


def test_a_one_direction_sample_cannot_accept_a_certificate() -> None:
    """The exact shape of the hole: 1 of 361 directions certified, verdict accepted."""
    verdict = verify_by_intervals(load_n11(), directions=("0",))
    assert len(verdict.directions) == 1
    assert verdict.directions[0].status == "certified"
    assert not verdict.accepted


@pytest.mark.exhaustive_exact
def test_the_393_100_certificate_is_accepted_on_the_full_doubled_net() -> None:
    """The interval-certified decision of s(12) >= 393/100, every direction."""
    certificate = load_n12(RETAINED_393_100)
    verdict = verify_by_intervals(certificate, enclose=True)
    assert verdict.accepted, verdict.failures
    assert not any(o.budget_exhausted for o in verdict.directions)
    assert len(verdict.directions) == 361
    assert sum(outcome.stalled for outcome in verdict.directions) == 0
    assert verdict.enclosure == (Fraction(100003, 100000), Fraction(100003, 100000))
    assert certificate.bounded_side == Fraction(393, 100)


@pytest.mark.exhaustive_exact
def test_the_live_n12_certificate_is_accepted_on_the_full_doubled_net() -> None:
    """Whatever rung certificate.json holds, decided in full against its own record."""
    certificate = load_n12()
    record = declared_n12()
    verdict = verify_by_intervals(certificate, enclose=True)
    assert verdict.accepted, verdict.failures
    assert not any(o.budget_exhausted for o in verdict.directions)
    assert len(verdict.directions) == 361
    assert sum(outcome.stalled for outcome in verdict.directions) == 0
    assert record["claim"] == f"s(12) >= {certificate.bounded_side}"
    enclosure = verdict.enclosure
    assert enclosure is not None
    assert str(enclosure[0]) == str(enclosure[1]) == record["least_cell_mass"]


@pytest.mark.exhaustive_exact
def test_the_retained_n11_certificate_is_accepted_on_the_full_doubled_net() -> None:
    """The interval-certified decision of s(11) >= 381/100, every direction."""
    certificate = load_n11()
    verdict = verify_by_intervals(certificate, enclose=True)
    assert verdict.accepted, verdict.failures
    assert not any(o.budget_exhausted for o in verdict.directions)
    assert len(verdict.directions) == 361
    assert sum(outcome.stalled for outcome in verdict.directions) == 0
    assert verdict.enclosure == (Fraction(4001, 4000), Fraction(4001, 4000))
    assert certificate.bounded_side == Fraction(381, 100)


@pytest.mark.exhaustive_exact
def test_the_retained_n17_certificate_is_accepted_on_the_full_doubled_net() -> None:
    """The interval-certified decision of s(17) >= 459/100, every direction.

    T-019 stands at C4 on the strength of this route, and until this test the
    only n = 17 certificate it decided here was Massaccesi's published control.
    A confirmation rung that no control pins is a claim, not a check.
    """
    certificate = load_n17()
    verdict = verify_by_intervals(certificate, enclose=True)
    assert verdict.accepted, verdict.failures
    assert not any(o.budget_exhausted for o in verdict.directions)
    assert len(verdict.directions) == 361
    assert sum(outcome.stalled for outcome in verdict.directions) == 0
    enclosure = verdict.enclosure
    assert enclosure == (Fraction(200009, 200000), Fraction(200009, 200000))
    assert enclosure is not None
    assert certificate.bounded_side == Fraction(459, 100)
    assert declared_n17()["least_cell_mass"] == str(enclosure[0])


@pytest.mark.exhaustive_exact
def test_the_retained_n20_certificate_is_accepted_on_the_full_doubled_net() -> None:
    """The interval-certified decision of s(19), s(20), s(21) >= 24/5.

    T-020 stands at C4 on the strength of this route. It is the cheap half of
    the pair: the exact event-cell sweep took 5378 s on the same bytes and this
    took 173 s on a contended machine, 167 s on a quiet one. The ratio is the
    order of thirty, and the box count -- 5,638,343 here, the largest in the
    corpus -- is the figure that compares across machines.
    """
    certificate = load_n20()
    verdict = verify_by_intervals(certificate, enclose=True)
    assert verdict.accepted, verdict.failures
    assert not any(o.budget_exhausted for o in verdict.directions)
    assert len(verdict.directions) == 361
    assert sum(outcome.stalled for outcome in verdict.directions) == 0
    enclosure = verdict.enclosure
    assert enclosure == (Fraction(50007, 50000), Fraction(50007, 50000))
    assert enclosure is not None
    assert certificate.bounded_side == Fraction(24, 5)
    assert declared_n20()["least_cell_mass"] == str(enclosure[0])


# --- the published-value control ----------------------------------------------


def test_massaccesi_n17_reproduces_the_published_bound_on_the_sub_net() -> None:
    """A result this verifier was not built against: s(17) >= 4.5058.

    Accepting it is what shows the verifier works, as distinct from agreeing
    with the certificates it was written alongside. The published least covered
    mass is exactly 1, and the enclosure must contain it.
    """
    certificate = retained_certificate()
    verdict = verify_by_intervals(certificate, directions=SUB_NET, enclose=True)
    assert not verdict.accepted, "a sub-net run is a control, not a verdict"
    assert all(outcome.status == "certified" for outcome in verdict.directions)
    assert certificate.bounded_side == Fraction(22529, 5000)
    assert float(certificate.bounded_side) == pytest.approx(4.5058)
    assert verdict.total_mass == Fraction(203, 12)
    enclosure = verdict.enclosure
    assert enclosure is not None
    assert enclosure[0] <= 1 <= enclosure[1]


@pytest.mark.exhaustive_exact
def test_massaccesi_n17_reproduces_the_published_bound_on_the_full_doubled_net() -> None:
    verdict = verify_by_intervals(retained_certificate(), enclose=True)
    assert verdict.accepted, verdict.failures
    assert not any(o.budget_exhausted for o in verdict.directions)
    assert len(verdict.directions) == 361
    assert verdict.enclosure == (Fraction(1), Fraction(1))


# --- agreement with the exact decision ------------------------------------------


def test_the_enclosure_contains_the_exact_minimum_direction_by_direction() -> None:
    """Where both verifiers accept, the interval enclosure must contain the
    exact rational minimum the sweep reports, including at reflected directions.

    Run on the 68-atom first rung, where the exact sweep is quick at oblique
    directions; the retained certificates are held to the exact verifier's
    registered minima by the full-net tests above.
    """
    certificate = load_n12(FIRST_RUNG_PATH)
    assert len(certificate.atoms) == 68
    for label, index in (("0", 0), ("57", 57), ("57'", 57), ("180'", 180)):
        search = _search(certificate, label)
        outcome = search.search(prune_at=None)
        assert outcome.status == "certified"
        assert outcome.lower is not None
        assert outcome.upper is not None
        cosine, sine = _exact_rotation(certificate.half_tangents[index])
        if label.endswith("'"):
            cosine, sine = sine, cosine
        direction = Direction(label, cosine, sine, -sine, cosine)
        exact, _ = minimum_covered_mass(
            certificate.atoms, direction, certificate.outer_side, certificate.square_side
        )
        lower, upper = (
            Fraction(outcome.lower, search.scale),
            Fraction(outcome.upper, search.scale),
        )
        assert lower <= exact <= upper
        assert upper - lower <= Fraction(1, search.scale), (
            "the enclosure should pin the minimum"
        )


# --- refusals -------------------------------------------------------------------


def test_a_scaled_mass_total_that_would_wrap_int64_is_refused_before_numpy_sees_it() -> None:
    """F7 of PR 78's adversarial review: the total was an ``int64`` sum of the masses.

    Two masses of ``2^62`` fit ``int64`` on their own and their sum does not; summed by
    NumPy the total wrapped negative and would have passed ``Condition 2`` for the wrong
    reason. The total is now summed in Python integers and refused at ``2^62``, before
    any array exists, which is the discipline the exact sweep applies at ``2^60``.
    """
    certificate = Certificate(
        n=1,
        outer_side=Fraction(11, 10),
        square_side=Fraction(3, 5),
        atoms=(
            Atom("centre", Fraction(11, 20), Fraction(11, 20), Fraction(1)),
            Atom("near", Fraction(0), Fraction(0), Fraction(2**62)),
            Atom("far", Fraction(11, 10), Fraction(11, 10), Fraction(2**62)),
        ),
        half_tangents=(Fraction(0), Fraction(1, 2)),
    )
    assert certificate.total_mass == 2**63 + 1

    with pytest.raises(IntervalInputError, match="total scaled atom mass"):
        AtomData.of(certificate)
    with pytest.raises(IntervalInputError, match="total scaled atom mass"):
        verify_by_intervals(certificate, directions=("0",))


def test_arithmetic_that_leaves_the_finite_floats_is_a_typed_refusal_not_a_warning() -> None:
    """F29: a container side near the float ceiling used to raise NumPy overflow warnings
    and carry infinities into the search. Infinity encloses nothing, so the run is
    refused, typed, and quiet -- a refusal is not a verdict.
    """
    outer = 10**308
    certificate = Certificate(
        n=(2 * outer) ** 2,
        outer_side=Fraction(outer),
        square_side=Fraction(1, 2),
        atoms=(),
        half_tangents=(Fraction(0), Fraction(207107, 500000)),
    )

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        with pytest.raises(IntervalInputError, match="finite float"):
            verify_by_intervals(certificate, enclose=True, directions=("1",))
    assert not caught


def test_an_exact_seam_exhausts_the_box_budget_and_is_never_accepted(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Regions of side 1/2 on a grid of spacing 1/2 tile the upright domain.

    Every point is covered by mass exactly 1, but each region's leave-edge is another's
    enter-edge to the digit, and no enclosure can close that seam: without a cap the
    search bisects it to the resolution floor along its whole length (F10 of PR 78's
    adversarial review). The direction must exhaust its work budget and say so, with a
    lower bound of zero and no acceptance. The budget is lowered here so the control
    runs in a second; the production value is held by the full-net decisions, which
    assert no direction exhausts it.
    """
    budget = 20_000
    monkeypatch.setattr(interval_module, "BOX_BUDGET", budget)
    verdict = verify_by_intervals(_grid_certificate(Fraction(1, 2)), directions=("0",))
    assert not verdict.accepted
    outcome = verdict.directions[0]
    assert outcome.status == "undecided"
    assert outcome.budget_exhausted
    assert budget <= outcome.boxes <= budget + BATCH
    assert outcome.lower == 0
    assert outcome.upper == 1
    assert "1 budget-exhausted" in verdict.conditions[-1].detail


def test_a_restricted_direction_can_still_refute_condition_5() -> None:
    verdict = verify_by_intervals(_grid_certificate(Fraction(1, 10)), directions=("0",))
    assert verdict.failures == (CONDITION5,)
    assert verdict.directions[0].status == "refuted"


def test_enclosure_mode_refutes_an_exact_minimum_below_one() -> None:
    """Enclosure mode pins the least mass and then asks whether it reaches one (D-435).

    Regions of side 1/10 leave uncovered centres, so the enclosed minimum is exactly
    zero; the direction resolves every box against that minimum and the verdict
    refuses on the value, which is where the D-435 fix put the question.
    """
    verdict = verify_by_intervals(_grid_certificate(Fraction(1, 10)), enclose=True)
    assert not verdict.accepted
    assert verdict.failures == (CONDITION5,)
    assert verdict.enclosure == (Fraction(0), Fraction(0))
    assert all(o.lower == 0 for o in verdict.directions)


def test_more_atoms_than_the_mask_cap_are_refused_before_any_allocation() -> None:
    certificate = load_n11()
    copies = MAX_INTERVAL_ATOMS // len(certificate.atoms) + 1
    oversized = Certificate(
        n=certificate.n,
        outer_side=certificate.outer_side,
        square_side=certificate.square_side,
        atoms=tuple(
            Atom(f"{atom.label}:{copy}", atom.x, atom.y, atom.weight / copies)
            for copy in range(copies)
            for atom in certificate.atoms
        ),
        half_tangents=certificate.half_tangents,
    )
    assert len(oversized.atoms) > MAX_INTERVAL_ATOMS
    with pytest.raises(IntervalInputError, match="supports at most"):
        AtomData.of(oversized)


def test_the_retained_atoms_are_refused_in_a_container_they_cannot_cover() -> None:
    """The must-refuse fixture: the n = 12 atoms in a container of side 4.

    The refutation witness is a concrete centre; its exact covered mass is
    recomputed in rational arithmetic and must be below 1, so the interval
    refusal is not taken on trust either.
    """
    certificate = load_n12(RETAINED_393_100)
    too_large = Certificate(
        n=certificate.n,
        outer_side=Fraction(4),
        square_side=certificate.square_side,
        atoms=certificate.atoms,
        half_tangents=certificate.half_tangents,
    )
    verdict = verify_by_intervals(too_large)
    assert not verdict.accepted
    assert verdict.failures == (CONDITION5,)
    refuted = verdict.directions[-1]
    assert refuted.status == "refuted"
    assert refuted.upper is not None
    assert refuted.upper < verdict.scale
    assert refuted.witness is not None
    index = int(refuted.label.rstrip("'"))
    cosine, sine = _exact_rotation(too_large.half_tangents[index])
    rotation = (sine, cosine) if refuted.label.endswith("'") else (cosine, sine)
    point = (Fraction(refuted.witness[0]), Fraction(refuted.witness[1]))
    assert _exactly_admissible(too_large, rotation, point)
    assert _exact_mass(too_large, rotation, point) < 1


def _lightened_n12() -> Certificate:
    """The 393/100 certificate with one atom over the tightest cell 1/10000 light."""
    certificate = load_n12(RETAINED_393_100)
    upright = Direction("0", Fraction(1), Fraction(0), Fraction(0), Fraction(1))
    _, (u, v) = minimum_covered_mass(
        certificate.atoms, upright, certificate.outer_side, certificate.square_side
    )
    half = certificate.square_side / 2
    index = next(
        i
        for i, atom in enumerate(certificate.atoms)
        if abs(atom.x - u) <= half and abs(atom.y - v) <= half
    )
    atoms = list(certificate.atoms)
    atom = atoms[index]
    atoms[index] = Atom(atom.label, atom.x, atom.y, atom.weight - Fraction(1, 10000))
    return Certificate(
        n=certificate.n,
        outer_side=certificate.outer_side,
        square_side=certificate.square_side,
        atoms=tuple(atoms),
        half_tangents=certificate.half_tangents,
    )


def test_lowering_one_atom_by_a_ten_thousandth_is_refused() -> None:
    """Condition 5 is tight at 1.00003, so a tenth of a thousandth off any atom over the
    tightest cell is visible. Symmetry is not what catches it here: this
    verifier never checks Condition 1, so the refusal has to come from coverage."""
    verdict = verify_by_intervals(_lightened_n12())
    assert verdict.failures == (CONDITION5,)
    assert verdict.directions[-1].status == "refuted"
    upper = verdict.directions[-1].upper
    assert upper is not None
    assert Fraction(upper, verdict.scale) == Fraction(100003, 100000) - Fraction(1, 10000)


def test_an_enclosed_run_refuses_a_minimum_it_pinned_below_one() -> None:
    """Enclosing the minimum is not the same question as whether it reaches 1.

    Under ``enclose`` a box is settled against the best point value seen rather
    than against mass 1, so a search over lightened atoms resolves every box,
    reports a width-zero enclosure at the true 99993/100000, and has decided
    nothing about Condition 5. The verdict must still refuse it (D-435).
    """
    verdict = verify_by_intervals(_lightened_n12(), enclose=True, directions=("0",))
    assert verdict.failures == (CONDITION5,)
    assert not verdict.accepted
    assert verdict.directions[-1].status == "certified"
    assert verdict.enclosure == (
        Fraction(100003, 100000) - Fraction(1, 10000),
        Fraction(100003, 100000) - Fraction(1, 10000),
    )


def test_mass_reaching_n_is_refused() -> None:
    base = retained_certificate(steps=6)
    inflated = Fraction(17, len(base.atoms))
    heavy = Certificate(
        n=17,
        outer_side=base.outer_side,
        square_side=base.square_side,
        atoms=tuple(Atom(a.label, a.x, a.y, inflated) for a in base.atoms),
        half_tangents=base.half_tangents,
    )
    verdict = verify_by_intervals(heavy, directions=("0",))
    assert "Condition 2 total mass below n" in verdict.failures


def test_a_net_short_of_an_eighth_turn_is_refused() -> None:
    base = retained_certificate(steps=6)
    short = Certificate(
        n=17,
        outer_side=base.outer_side,
        square_side=base.square_side,
        atoms=base.atoms,
        half_tangents=tuple(Fraction(41, 100) * k / 6 for k in range(7)),
    )
    verdict = verify_by_intervals(short, directions=("0",))
    assert "Condition 3 net reaches pi/4" in verdict.failures


def test_a_net_too_coarse_for_containment_is_refused() -> None:
    verdict = verify_by_intervals(retained_certificate(steps=2), directions=("0",))
    assert "Condition 4 containment B(1 + D) < 1" in verdict.failures


def test_containment_at_exactly_one_is_undecided_and_therefore_not_accepted() -> None:
    """Strictness, interval-style: an enclosure straddling 1 proves neither side.

    The exact verifier refuses this by equality; this one cannot see equality
    and refuses it by declining to decide, which is the same verdict reached
    for a different reason.
    """
    base = retained_certificate(steps=180)
    gap = base.largest_half_gap_tangent
    touching = Certificate(
        n=17,
        outer_side=base.outer_side,
        square_side=1 / (1 + gap),
        atoms=base.atoms,
        half_tangents=base.half_tangents,
    )
    verdict = verify_by_intervals(touching, directions=("0",))
    containment = next(c for c in verdict.conditions if c.name.startswith("Condition 4"))
    assert containment.status == "undecided"
    assert not verdict.accepted


def test_half_tangents_reaching_one_are_refused_before_any_search() -> None:
    base = retained_certificate(steps=6)
    with pytest.raises(ValueError, match="below 1"):
        verify_by_intervals(
            Certificate(
                n=17,
                outer_side=base.outer_side,
                square_side=base.square_side,
                atoms=base.atoms,
                half_tangents=(Fraction(0), Fraction(1)),
            )
        )


# --- the limit of the method ---------------------------------------------------


def _seams(certificate: Certificate, rotation: tuple[Fraction, Fraction]) -> int:
    """Exact coincidences the interval search cannot close at one direction.

    A leave-edge of one region on the enter-edge of another (``u_j - u_i = B``
    in either axis) or a region edge through a domain corner. Exact arithmetic,
    because this is a census of the data, not a decision of the theorem.
    """
    cosine, sine = rotation
    rotated = _rotated(certificate, rotation)
    side = certificate.square_side
    half = side / 2
    h = side * (cosine + sine) / 2
    far = certificate.outer_side - h
    seams = 0
    for axis in (0, 1):
        positions = {atom[axis] for atom in rotated}
        seams += sum(1 for atom in rotated if atom[axis] + side in positions)
        edges = {atom[axis] + half for atom in rotated} | {
            atom[axis] - half for atom in rotated
        }
        for x, y in ((h, h), (far, h), (h, far), (far, far)):
            corner = cosine * x + sine * y if axis == 0 else cosine * y - sine * x
            seams += corner in edges
    return seams


def test_the_retained_certificates_have_no_seam_the_method_cannot_close() -> None:
    """The precondition for the searches above to terminate, checked on the data.

    The full-net runs report zero stalled boxes; this says why, on a sample of
    directions including reflected ones, and would flag a future certificate
    that happened to land on a seam.
    """
    certificates = (load_n12(RETAINED_393_100), load_n12(), load_n11(), retained_certificate())
    for certificate in certificates:
        for index, reflected in ((0, False), (1, False), (57, True), (90, False), (180, True)):
            cosine, sine = _exact_rotation(certificate.half_tangents[index])
            rotation = (sine, cosine) if reflected else (cosine, sine)
            assert _seams(certificate, rotation) == 0
    assert _seams(_grid_certificate(Fraction(1, 2)), (Fraction(1), Fraction(0))) > 0
    assert _seams(_grid_certificate(Fraction(51, 100)), (Fraction(1), Fraction(0))) == 0


def _grid_certificate(square_side: Fraction) -> Certificate:
    """Unit weights on a half-spaced grid in a side-3 container, one direction."""
    coordinates = [Fraction(k, 2) for k in range(1, 6)]
    atoms = tuple(
        Atom(f"{i},{j}", x, y, Fraction(1))
        for i, x in enumerate(coordinates)
        for j, y in enumerate(coordinates)
    )
    return Certificate(
        n=26,
        outer_side=Fraction(3),
        square_side=square_side,
        atoms=atoms,
        half_tangents=(Fraction(0), Fraction(1, 2)),
    )


def test_an_exact_edge_coincidence_is_reported_undecided_never_accepted() -> None:
    """Regions of side 1/2 on a grid of spacing 1/2 tile the upright domain:
    every point is covered by mass exactly 1, but each region's leave-edge is
    another's enter-edge to the digit, and no enclosure can close that seam.
    The search must reach its floor and say so."""
    verdict = verify_by_intervals(_grid_certificate(Fraction(1, 2)), directions=("0",))
    assert not verdict.accepted
    outcome = verdict.directions[0]
    assert outcome.status == "undecided"
    assert outcome.stalled > 0
    assert outcome.lower == 0
    assert outcome.upper == 1


def test_perturbing_the_coincidence_away_lets_the_same_search_certify() -> None:
    """Widen the regions to 51/100 and the seams become overlaps of width 1/100,
    which the boxes resolve without difficulty."""
    verdict = verify_by_intervals(_grid_certificate(Fraction(51, 100)), directions=("0",))
    outcome = verdict.directions[0]
    assert outcome.status == "certified"
    assert outcome.stalled == 0
    assert not outcome.budget_exhausted
    # One direction certified is the control's answer; the verdict stays
    # undecided, since a sample decides nothing about the other 360 directions.
    assert not verdict.accepted
    assert verdict.conditions[-1].status == "undecided"
