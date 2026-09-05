"""Controls for the weighted fractional unavoidable-set instrument.

The positive control is the published one: Massaccesi's retained n = 17
certificate must be accepted, and the side it bounds must be the 4.5058 the
source reports. That number is the whole point of the control -- an earlier
reading of the theorem divided by the shrunken side and would have claimed
4.51799, overstating a published result.
"""

from __future__ import annotations

import json
import runpy
from collections.abc import Callable
from fractions import Fraction
from pathlib import Path
from types import ModuleType

import numpy as np
import pytest

import cases.n12_fractional_certificate.__main__ as n12_entrypoint
import cases.n17_fractional_certificate.__main__ as n17_entrypoint
import cases.n20_fractional_certificate.__main__ as n20_entrypoint
from cases.n11_fractional_certificate.replay import FIRST_RUNG_PATH as N11_FIRST_RUNG
from cases.n11_fractional_certificate.replay import STROMQUIST_RUNG_PATH
from cases.n11_fractional_certificate.replay import declared as n11_declared
from cases.n11_fractional_certificate.replay import load as n11_load
from cases.n12_fractional_certificate.__main__ import replay as replay_n12
from cases.n12_fractional_certificate.replay import FIRST_RUNG_PATH, declared, load
from cases.n17_fractional_certificate.__main__ import replay as replay_n17
from cases.n17_fractional_certificate.replay import declared as n17_declared
from cases.n17_fractional_certificate.replay import load as n17_load
from cases.n17_weighted_certificate.fixture import load_retained_fixture
from cases.n20_fractional_certificate.__main__ import replay as replay_n20
from cases.n20_fractional_certificate.replay import RUNG_24_5_PATH
from cases.n20_fractional_certificate.replay import declared as n20_declared
from cases.n20_fractional_certificate.replay import load as n20_load
from sqpack.fractional.certificate import (
    Certificate,
    Verdict,
    ceiling_side,
    ceiling_side_for_net,
    grid_refutation_order,
    least_size_certified,
    verify,
)
from sqpack.fractional.generate import build_site_grid, rationalise
from sqpack.fractional.model import Atom, Direction, rotation_from_half_tangent
from sqpack.fractional.sweep import reduce_to_cells

MASSACCESI_LIMIT = Fraction(207107, 500000)


def retained_certificate(steps: int | None = None) -> Certificate:
    """The retained n = 17 data, re-encoded into the first-party types."""
    fixture = load_retained_fixture()
    scale = Fraction(fixture.weight_scale)
    atoms = tuple(
        Atom(atom.label, atom.x, atom.y, atom.weight / scale) for atom in fixture.atoms
    )
    count = fixture.direction_steps if steps is None else steps
    tangents = tuple(fixture.angle_limit * k / count for k in range(count + 1))
    return Certificate(
        n=17,
        outer_side=fixture.outer_side,
        square_side=fixture.square_side,
        atoms=atoms,
        half_tangents=tangents,
    )


def test_the_retained_certificate_bounds_the_side_its_source_reports() -> None:
    certificate = retained_certificate()
    assert certificate.bounded_side == Fraction(22529, 5000)
    assert float(certificate.bounded_side) == pytest.approx(4.5058)
    assert certificate.total_mass == Fraction(203, 12)
    assert certificate.total_mass < 17


def test_a_coarse_net_still_accepts_the_retained_atoms() -> None:
    """Condition 5 on a sub-net of the published one: the atoms cover it too."""
    verdict = verify(retained_certificate(steps=6))
    assert verdict.minimum_cell_mass is not None
    assert verdict.minimum_cell_mass >= 1


@pytest.mark.exhaustive_exact
def test_the_full_retained_certificate_is_accepted() -> None:
    verdict = verify(retained_certificate())
    assert verdict.accepted, verdict.failures
    assert verdict.minimum_cell_mass == 1


def test_mass_reaching_n_is_refused() -> None:
    """Condition 2 is strict: a total that only reaches n proves nothing."""
    base = retained_certificate(steps=6)
    inflated = Fraction(17, len(base.atoms))
    heavy = Certificate(
        n=17,
        outer_side=base.outer_side,
        square_side=base.square_side,
        atoms=tuple(Atom(a.label, a.x, a.y, inflated) for a in base.atoms),
        half_tangents=base.half_tangents,
    )
    assert heavy.total_mass == 17
    assert "Condition 2 total mass below n" in verify(heavy).failures


def small_replay_control() -> dict[str, object]:
    """A two-square certificate small enough for the exact verifier to decide instantly.

    One central atom, one net step: the five conditions all hold, so a replay of it
    reaches the declaration guards instead of stopping at a failed condition.
    """
    return {
        "id": "small-replay-control",
        "n": 2,
        "outer_side": "1",
        "square_side": "3/5",
        "angle_limit": "1/2",
        "direction_steps": 1,
        "symmetry": "D4",
        "claim": "s(2) >= 1",
        "total_mass": "1",
        "least_cell_mass": "1",
        "atoms": [["1/2", "1/2", "1"]],
    }


DECLARED_VALUE_DRIFT = [
    ("claim", "s(2) >= 2", "retained claim disagrees"),
    ("total_mass", "0", "retained total mass disagrees"),
    ("least_cell_mass", "2", "retained least cell mass disagrees"),
]


@pytest.mark.parametrize(("field", "wrong", "message"), DECLARED_VALUE_DRIFT)
def test_n12_replay_refuses_declared_value_drift(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    field: str,
    wrong: str,
    message: str,
) -> None:
    """The moving n = 12 pointer may not verify stale declared figures."""
    record = small_replay_control()
    record[field] = wrong
    path = tmp_path / "certificate.json"
    path.write_text(json.dumps(record), encoding="utf-8")

    assert replay_n12(path) == 1
    assert message in capsys.readouterr().out


@pytest.mark.parametrize("replay", [replay_n17, replay_n20], ids=["n17", "n20"])
@pytest.mark.parametrize("mutation", DECLARED_VALUE_DRIFT)
def test_n17_and_n20_replays_refuse_declared_value_drift(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    replay: Callable[[Path], int],
    mutation: tuple[str, str, str],
) -> None:
    """Every named retained replay binds its reader-visible theorem declarations."""
    field, wrong, message = mutation
    record = small_replay_control()
    record[field] = wrong
    path = tmp_path / "certificate.json"
    path.write_text(json.dumps(record), encoding="utf-8")

    assert replay(path) == 1
    assert message in capsys.readouterr().out


@pytest.mark.parametrize(
    "entrypoint",
    [n12_entrypoint, n17_entrypoint, n20_entrypoint],
    ids=["n12", "n17", "n20"],
)
def test_the_guarded_replays_refuse_a_file_changed_during_verification(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    entrypoint: ModuleType,
) -> None:
    """A long replay may report only on the same bytes it parsed."""
    record = small_replay_control()
    path = tmp_path / "certificate.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    real_verify: Callable[[Certificate], Verdict] = entrypoint.verify

    def mutate_path(certificate: Certificate) -> Verdict:
        verdict = real_verify(certificate)
        changed = record | {"claim": "s(2) >= 2"}
        path.write_text(json.dumps(changed), encoding="utf-8")
        return verdict

    monkeypatch.setattr(entrypoint, "verify", mutate_path)
    assert entrypoint.replay(path) == 1
    assert "changed during replay" in capsys.readouterr().out


def test_a_net_short_of_an_eighth_turn_is_refused() -> None:
    """Condition 3: the D4 reduction needs the arc to reach pi/4, and 0.41 does not."""
    base = retained_certificate(steps=6)
    short = Certificate(
        n=17,
        outer_side=base.outer_side,
        square_side=base.square_side,
        atoms=base.atoms,
        half_tangents=tuple(Fraction(41, 100) * k / 6 for k in range(7)),
    )
    assert "Condition 3 net reaches pi/4" in verify(short).failures


def test_a_net_too_coarse_for_containment_is_refused() -> None:
    """Condition 4: with few directions the angular gap outgrows the shrink."""
    base = retained_certificate(steps=2)
    assert "Condition 4 containment B(1 + D) < 1" in verify(base).failures


def test_a_lightened_atom_breaks_the_covering_condition() -> None:
    """Condition 5 is tight on the retained certificate, so any loss is visible."""
    base = retained_certificate(steps=6)
    lightened = (
        Atom(base.atoms[0].label, base.atoms[0].x, base.atoms[0].y, Fraction(0)),
        *base.atoms[1:],
    )
    thin = Certificate(
        n=17,
        outer_side=base.outer_side,
        square_side=base.square_side,
        atoms=lightened,
        half_tangents=base.half_tangents,
    )
    verdict = verify(thin)
    assert verdict.minimum_cell_mass is not None
    assert verdict.minimum_cell_mass < 1
    assert "Condition 5 every reachable cell carries mass 1" in verdict.failures


def test_the_half_angle_parametrisation_is_exactly_unit_length() -> None:
    for k in range(13):
        direction = rotation_from_half_tangent(str(k), MASSACCESI_LIMIT * k / 12)
        assert direction.ux**2 + direction.uy**2 == 1


def test_a_direction_off_the_unit_circle_is_refused() -> None:
    with pytest.raises(ValueError, match="unit length"):
        Direction("bad", Fraction(1), Fraction(1), Fraction(-1), Fraction(1))


def test_the_largest_half_gap_tangent_is_exact_on_a_uniform_net() -> None:
    """A uniform half-tangent net has its widest angular gap at zero."""
    certificate = retained_certificate(steps=180)
    assert certificate.largest_half_gap_tangent == MASSACCESI_LIMIT / 180


def test_the_retained_n12_certificate_replays() -> None:
    """The n = 12 result, read from its retained file and checked against its record.

    What the certificate claims is checked here; that a verifier accepts it is
    the exhaustive test below, and the coarse-net rung test covers the same
    ladder cheaply.
    """
    certificate = load()
    assert certificate.n == 12
    assert certificate.bounded_side == Fraction(99, 25)
    assert certificate.total_mass == Fraction(149987, 12500)
    assert certificate.total_mass < 12

    record = declared()
    assert record["claim"] == "s(12) >= 99/25"
    assert record["total_mass"] == str(certificate.total_mass)


@pytest.mark.exhaustive_exact
def test_the_retained_n12_certificate_is_accepted() -> None:
    """The 969-atom certificate over 181 directions, decided exactly."""
    certificate = load()
    verdict = verify(certificate)
    assert verdict.accepted, verdict.failures
    assert verdict.minimum_cell_mass is not None
    assert verdict.minimum_cell_mass >= 1
    assert declared()["least_cell_mass"] == str(verdict.minimum_cell_mass)


def test_the_first_rung_at_19_5_still_replays() -> None:
    """The smaller certificate the instrument found first is kept and stays true."""
    certificate = load(FIRST_RUNG_PATH)
    assert certificate.bounded_side == Fraction(19, 5)
    assert certificate.total_mass == Fraction(58, 5)
    assert len(certificate.atoms) == 68
    verdict = verify(certificate)
    assert verdict.accepted, verdict.failures
    assert declared(FIRST_RUNG_PATH)["claim"] == "s(12) >= 19/5"


def test_the_n12_certificate_improves_the_inherited_bound() -> None:
    """79/20 beats 2 + 4/sqrt(5), which n = 12 only held by monotonicity."""
    bound = load().bounded_side
    # L > 2 + 4/sqrt(5) iff (L - 2) > 4/sqrt(5) iff (L - 2)^2 * 5 > 16,
    # both sides being positive. Decided in exact rationals, not in floats.
    assert bound > 2
    assert (bound - 2) ** 2 * 5 > 16


def test_breaking_the_symmetry_of_the_n12_atoms_is_refused() -> None:
    """Condition 1 is not decoration: drop one orbit member and the reduction is void."""
    certificate = load()
    maimed = Certificate(
        n=certificate.n,
        outer_side=certificate.outer_side,
        square_side=certificate.square_side,
        atoms=certificate.atoms[1:],
        half_tangents=certificate.half_tangents[:4],
    )
    assert "Condition 1 atoms carry the declared symmetry" in verify(maimed).failures


def test_the_independent_verifier_agrees_on_the_first_rung() -> None:
    """The reviewer's from-the-theorem verifier, on two directions of the 19/5 rung.

    Kept fast by restricting to the first and last net directions; the full
    181-direction agreement is recorded in the evidence register.
    """
    package = Path(__file__).parents[1] / "cases/n12_fractional_certificate"
    module = runpy.run_path(
        str(package / "independent_verify.py"), run_name="independent_verify"
    )
    certificate = module["load"](str(FIRST_RUNG_PATH))
    accepted, report = module["verify"](certificate, ks=[0, 180], label="19/5")
    assert accepted, report
    assert report["info"]["min_rep"] == Fraction(1)


def test_containment_at_exactly_one_is_refused() -> None:
    """Condition 4 must be strict: equality leaves the shrunken squares able to touch,
    and touching closed squares can share an atom, which breaks the count."""
    base = retained_certificate(steps=180)
    gap = base.largest_half_gap_tangent
    touching = Certificate(
        n=17,
        outer_side=base.outer_side,
        square_side=1 / (1 + gap),
        atoms=base.atoms,
        half_tangents=base.half_tangents,
    )
    assert touching.square_side * (1 + gap) == 1
    assert "Condition 4 containment B(1 + D) < 1" in verify(touching).failures


def test_rationalise_rounds_weights_up_never_down() -> None:
    """D-433: the rounding step floored while its docstring said ceil.

    Every coverage row the solver leaves tight sits exactly at 1, so any downward
    rounding refuses a certificate the program had found. Weights that are not
    multiples of 1/scale must land on the next multiple above, never below.
    """
    grid = build_site_grid(Fraction(4), 3, Fraction(1, 2))
    weights = np.array([5.3 / 576, 0.5 / 576, 1000.001 / 576][: len(grid.orbits)])
    atoms = rationalise(grid, weights, scale=576, bump=Fraction(1))
    by_orbit = {}
    for atom in atoms:
        by_orbit.setdefault(atom.weight, 0)
        by_orbit[atom.weight] += 1
    assert Fraction(6, 576) in by_orbit
    assert Fraction(1, 576) in by_orbit
    assert Fraction(1001, 576) in by_orbit
    assert all(w * 576 >= 1 for w in by_orbit)


def test_the_sweep_scores_every_cell_it_scored_before() -> None:
    """A guard against the verifier being "repaired" by narrowing its cell set.

    Condition 5 is only as strong as the set of placements it quantifies over, and a
    change that drops cells makes every certificate easier to accept while
    every retained certificate still passes -- so the retained ones cannot
    catch it. These counts are the exact cell sets the accepted n = 12
    certificate was decided on. If a change lowers one, the verifier is
    deciding fewer placements than it used to, and the results registered
    against it no longer mean what they said.
    """
    certificate = load(
        Path(__file__).parents[1] / "cases/n12_fractional_certificate/certificate-77-20.json"
    )
    expected = {0: 1225, 1: 36481, 45: 38733, 90: 37733, 180: 36837}
    for index, count in expected.items():
        direction = rotation_from_half_tangent(str(index), certificate.half_tangents[index])
        reduction = reduce_to_cells(
            certificate.atoms,
            direction,
            certificate.outer_side,
            certificate.square_side,
        )
        assert len(reduction.cells) == count, (
            f"direction {index}: {len(reduction.cells)} cells, was {count}"
        )


def test_the_retained_atoms_are_refused_in_a_container_they_cannot_cover() -> None:
    """The must-refuse fixture: same atoms, a container too large for them.

    The independent reviewer measured least covered mass 1/10 here. A verifier
    that accepted this would be accepting a certificate whose squares can be
    placed where no atom reaches, which is the failure a narrowed cell set
    produces.
    """
    certificate = load()
    too_large = Certificate(
        n=certificate.n,
        outer_side=Fraction(4),
        square_side=certificate.square_side,
        atoms=certificate.atoms,
        half_tangents=certificate.half_tangents[:8],
    )
    verdict = verify(too_large)
    assert not verdict.accepted
    assert "Condition 5 every reachable cell carries mass 1" in verdict.failures
    assert verdict.minimum_cell_mass is not None
    assert verdict.minimum_cell_mass < 1


def test_the_n11_certificate_beats_stromquists_2003_bound() -> None:
    """s(11) >= 381/100, read from its own file.

    2 + 4/sqrt(5) = 3.788854 had stood since Stromquist 2003 and was the only
    bound n = 11 had. The comparison is decided in exact rationals: L > 2 +
    4/sqrt(5) iff (L - 2)^2 * 5 > 16, both sides being positive.

    What the certificate claims is checked here; that a verifier accepts it is
    the exhaustive test below.
    """

    certificate = n11_load()
    assert certificate.n == 11
    assert certificate.bounded_side == Fraction(381, 100)
    assert certificate.total_mass == Fraction(434547, 40000)
    assert certificate.total_mass < 11
    assert (certificate.bounded_side - 2) ** 2 * 5 > 16

    record = n11_declared()
    assert record["claim"] == "s(11) >= 381/100"
    assert record["total_mass"] == str(certificate.total_mass)


@pytest.mark.exhaustive_exact
def test_the_n11_certificate_is_accepted() -> None:
    """The 1121-atom certificate over 181 directions, decided exactly."""
    certificate = n11_load()
    verdict = verify(certificate)
    assert verdict.accepted, verdict.failures
    assert verdict.minimum_cell_mass is not None
    assert verdict.minimum_cell_mass >= 1
    assert n11_declared()["least_cell_mass"] == str(verdict.minimum_cell_mass)


def test_the_n11_rung_at_19_5_still_replays() -> None:
    """The value that first passed Stromquist is kept and stays true."""
    certificate = n11_load(STROMQUIST_RUNG_PATH)
    assert certificate.bounded_side == Fraction(19, 5)
    assert certificate.total_mass == Fraction(43391, 4000)
    assert len(certificate.atoms) == 425
    assert n11_declared(STROMQUIST_RUNG_PATH)["claim"] == "s(11) >= 19/5"


def test_the_n11_calibration_rung_below_stromquist_also_verifies() -> None:
    """189/50 proves nothing new, which is exactly why it was run first.

    Decided on a coarse net here. What this rung is evidence for -- that the
    instrument returns sane values below the frontier as well as above it --
    does not need all 181 directions to show, and the full decision is the
    exhaustive test below.
    """

    certificate = n11_load(N11_FIRST_RUNG)
    assert certificate.bounded_side == Fraction(189, 50)
    assert (certificate.bounded_side - 2) ** 2 * 5 < 16
    # Condition 5's value, not the whole verdict: a net this coarse fails Condition 4 by
    # construction, since D grows with the gap and B(1 + D) then exceeds 1.
    # What the coarse decision shows is coverage, which is the claim here.
    coarse = Certificate(
        n=certificate.n,
        outer_side=certificate.outer_side,
        square_side=certificate.square_side,
        atoms=certificate.atoms,
        half_tangents=certificate.half_tangents[::30],
        symmetry=certificate.symmetry,
    )
    verdict = verify(coarse)
    assert verdict.minimum_cell_mass is not None
    assert verdict.minimum_cell_mass >= 1


@pytest.mark.exhaustive_exact
def test_the_n11_calibration_rung_verifies_on_the_full_net() -> None:
    """The 373-atom calibration rung over all 181 directions."""
    assert verify(n11_load(N11_FIRST_RUNG)).accepted


def test_every_retained_n12_rung_still_verifies() -> None:
    """The ladder is evidence, not clutter: each rung must still be true.

    Kept cheap by deciding each rung on a coarse sub-net; the full 181-direction
    decision for the top rung is the exhaustive_exact test above.
    """
    package = Path(__file__).parents[1] / "cases/n12_fractional_certificate"
    rungs = {
        "certificate-19-5.json": Fraction(19, 5),
        "certificate-77-20.json": Fraction(77, 20),
        "certificate-97-25.json": Fraction(97, 25),
        "certificate-39-10.json": Fraction(39, 10),
        "certificate-393-100.json": Fraction(393, 100),
        "certificate-197-50.json": Fraction(197, 50),
    }
    for name, side in rungs.items():
        rung = load(package / name)
        assert rung.bounded_side == side
        assert rung.total_mass < 12
        coarse = Certificate(
            n=rung.n,
            outer_side=rung.outer_side,
            square_side=rung.square_side,
            atoms=rung.atoms,
            half_tangents=rung.half_tangents[::30],
        )
        verdict = verify(coarse)
        assert verdict.minimum_cell_mass is not None
        assert verdict.minimum_cell_mass >= 1, f"{name} lost coverage"


def test_the_n17_certificate_displaces_massaccesis_published_bound() -> None:
    """s(17) >= 451/100 beats the published value, decided from the file.

    22529/5000 = 4.5058 is Massaccesi's published value, adopted here as T-015
    and carried to n = 18 and n = 19 as T-016. This certificate is denser and
    sits at a larger side, so one object moves all three cases. The comparison
    is decided in exact rationals.

    What the certificate claims is checked here; that a verifier accepts it is
    the exhaustive test below, which costs a quarter of an hour.
    """
    certificate = n17_load()
    assert certificate.n == 17
    assert certificate.bounded_side == Fraction(459, 100)
    assert certificate.bounded_side > Fraction(22529, 5000)
    assert certificate.total_mass == Fraction(423327, 25000)
    assert certificate.total_mass < 17

    record = n17_declared()
    assert record["claim"] == "s(17) >= 459/100"
    assert record["total_mass"] == str(certificate.total_mass)


@pytest.mark.exhaustive_exact
def test_the_n17_certificate_is_accepted() -> None:
    """The 1173-atom certificate over 181 directions, decided exactly.

    Marked exhaustive: this is a thirteen-minute sweep, and the fast test above
    already pins every number the record claims about the same file.
    """
    certificate = n17_load()
    verdict = verify(certificate)
    assert verdict.accepted, verdict.failures
    assert verdict.minimum_cell_mass is not None
    assert verdict.minimum_cell_mass >= 1
    assert n17_declared()["least_cell_mass"] == str(verdict.minimum_cell_mass)


def test_the_n17_certificate_does_not_reach_n20() -> None:
    """The scope claim: 459/100 lifts n = 17, 18 and 19, and not n = 20.

    The certificate's own mass carries it upward, so n = 20 does inherit 459/100 --
    but it improved nothing there, because Nagamochi's closed form already gave
    n = 20 the larger 1 + sqrt(13). Decided in integers, on the retained rung:
    1 + sqrt(13) > 459/100 iff 13 * 100^2 > (459 - 100)^2.
    n = 20 has since moved to 24/5 by a different certificate (T-020), which is
    larger again; that does not change what this one reaches.
    """
    assert 13 * 100**2 > (459 - 100) ** 2
    assert n17_load().bounded_side == Fraction(459, 100)
    assert n20_load().bounded_side > Fraction(459, 100)


def test_the_n20_certificate_displaces_nagamochis_closed_form() -> None:
    """s(20) and s(21) >= 97/20, decided from the file.

    Nagamochi's 2005 closed form gave n = 20 and n = 21 their whole lower bound
    until 2026-09-04: 1 + sqrt(13) and 1 + sqrt(14). Both comparisons are decided
    in integers -- 1 + sqrt(k) < 97/20 iff 400k < 77^2 -- so no float square root
    stands between the record and the claim.

    The 24/5 rung this displaced is checked beside it: it is still the retained
    bound at n = 19, which the top rung's mass no longer reaches.

    What the certificate claims is checked here; that a verifier accepts it is
    the exhaustive test below, which costs an hour and a half.
    """
    certificate = n20_load()
    assert certificate.n == 20
    assert certificate.bounded_side == Fraction(97, 20)
    assert certificate.total_mass == Fraction(19848723, 1000000)
    assert len(certificate.atoms) == 1680

    assert 400 * 13 < 77**2, "1 + sqrt(13) < 97/20 at n = 20"
    assert 400 * 14 < 77**2, "1 + sqrt(14) < 97/20 at n = 21"

    record = n20_declared()
    assert record["claim"] == "s(20) >= 97/20"
    assert record["total_mass"] == str(certificate.total_mass)
    assert record["least_cell_mass"] == "200001/200000"

    rung = n20_load(RUNG_24_5_PATH)
    assert rung.bounded_side == Fraction(24, 5)
    assert rung.total_mass == Fraction(946131, 50000)
    assert len(rung.atoms) == 2260
    assert n20_declared(RUNG_24_5_PATH)["least_cell_mass"] == "50007/50000"


@pytest.mark.exhaustive_exact
def test_the_n20_certificate_is_accepted() -> None:
    """The 2260-atom certificate over 181 directions, decided exactly.

    Marked exhaustive: this took 5378 s on the machine that retained it, the
    largest exact decision in the corpus, and the fast tests around it already
    pin every number the record claims about the same file.
    """
    certificate = n20_load()
    verdict = verify(certificate)
    assert verdict.accepted, verdict.failures
    assert verdict.minimum_cell_mass is not None
    assert verdict.minimum_cell_mass >= 1
    assert n20_declared()["least_cell_mass"] == str(verdict.minimum_cell_mass)


def test_the_n20_certificate_carries_20_and_21_and_stops_there() -> None:
    """Two sizes out of Condition 2, and the exact point where the reach runs out.

    The register already holds 5 from n = 22 on, so the certificate is true there
    and weaker. Below, n = 19 is out of reach in the other direction: these atoms
    are heavier than nineteen, so Condition 2 refuses them at that size. That is
    the whole reason the 24/5 rung is still retained rather than deleted -- it is
    lighter, it reaches nineteen, and nothing above it does.
    """
    certificate = n20_load()
    assert least_size_certified(certificate.total_mass) == 20
    for size in (20, 21):
        assert certificate.total_mass < size
    assert certificate.total_mass > 19, "Condition 2 refuses these atoms at n = 19"
    assert certificate.bounded_side < 5, "n >= 22 already holds the trivial 5"

    rung = n20_load(RUNG_24_5_PATH)
    assert least_size_certified(rung.total_mass) == 19
    assert rung.total_mass < 19 < certificate.total_mass


def test_the_n20_rungs_do_not_contradict_the_packings_they_reach() -> None:
    """No certificate can exceed a side an actual packing achieves, at any size it reaches.

    Each rung is checked against the packing for the least size it certifies, since
    that is the tightest one it has to clear. The 24/5 rung reaches n = 19, where
    Wainwright's packing gives s(19) <= 3 + (4/3) sqrt(2); decided in integers,
    24/5 < 3 + 4 sqrt(2) / 3 iff 27 < 20 sqrt(2) iff 729 < 800. The top rung's mass
    stops at n = 20, whose best known packing is the trivial 5.

    If a certificate certified a side above the packing it reaches, one of the two
    would be wrong, so this is a check on the record and not only on the arithmetic.
    """
    rung = n20_load(RUNG_24_5_PATH)
    assert 27**2 < 800, "24/5 sits below the retained n = 19 packing"
    assert rung.bounded_side == Fraction(24, 5)
    assert least_size_certified(rung.total_mass) == 19

    certificate = n20_load()
    assert certificate.bounded_side < 5, "97/20 sits below the retained n = 20 packing"
    assert least_size_certified(certificate.total_mass) == 20


def test_the_grid_refutation_order_is_the_integer_ceiling_of_the_root() -> None:
    """``m`` is decided by integers, never by a float square root."""
    for n in range(1, 200):
        order = grid_refutation_order(n)
        assert order * order >= n
        assert (order - 1) * (order - 1) < n
    assert [grid_refutation_order(n) for n in (11, 12, 16, 17, 25, 26)] == [4, 4, 4, 5, 5, 6]


def test_every_retained_certificate_sits_below_its_own_ceiling() -> None:
    """``L <= ceil(sqrt(n)) B`` is forced by Condition 2 and Condition 5 together.

    A retained certificate above its ceiling would mean one of the two is wrong,
    so this is a check on the record and not only on the arithmetic.
    """
    for certificate in (n11_load(), load(), n17_load(), n20_load()):
        ceiling = ceiling_side(certificate.n, certificate.square_side)
        assert certificate.outer_side <= ceiling, (
            f"n = {certificate.n} claims {certificate.outer_side} above its ceiling {ceiling}"
        )
        assert ceiling < ceiling_side_for_net(certificate.n, certificate.half_tangents)


def test_the_n12_ceiling_is_the_figure_the_record_carries() -> None:
    """3.99082 is ``4 / (1 + D)`` at 181 directions, not a measured quantity."""
    certificate = load()
    assert certificate.n == 12
    over_the_net = ceiling_side_for_net(12, certificate.half_tangents)
    assert float(over_the_net) == pytest.approx(3.990816, abs=5e-7)
    assert ceiling_side(12, certificate.square_side) == Fraction(4) * certificate.square_side
    # The trivial grid packing gives s(12) <= 4, and the ceiling sits below it, so
    # no certificate of this shape can ever settle a case whose value is 4.
    assert over_the_net < 4


def test_the_refuting_grid_fits_and_one_of_its_squares_starves() -> None:
    """The construction behind the ceiling, exhibited on the retained atoms.

    Widen the container just past ``4 B`` and lay the sixteen separated
    ``B``-squares the ceiling argument builds. They must all lie inside the
    container and be pairwise disjoint; and since the certificate carries mass
    11.97, well under sixteen, at least one of them must cover less than 1 --
    which is Condition 5 failing, exactly as the argument says it must.
    """
    certificate = load()
    b = certificate.square_side
    order = grid_refutation_order(certificate.n)
    side = order * b + Fraction(1, 1000)
    gap = (side - order * b) / (order + 1)
    pitch = b + gap

    corners = [(gap + i * pitch, gap + j * pitch) for j in range(order) for i in range(order)]
    assert len(corners) == order * order == 16
    # Inside the container, and separated: the far edge of the last square and
    # the gap between consecutive ones are both decided exactly.
    assert corners[-1][0] + b < side
    assert corners[-1][1] + b < side
    assert pitch - b == gap > 0

    covered = [
        sum(
            (
                atom.weight
                for atom in certificate.atoms
                if x <= atom.x <= x + b and y <= atom.y <= y + b
            ),
            start=Fraction(0),
        )
        for x, y in corners
    ]
    assert sum(covered) <= certificate.total_mass
    assert certificate.total_mass < order * order
    assert min(covered) < 1, (
        "Condition 5 would have to hold on all sixteen for the mass to reach n"
    )


def test_one_atom_set_certifies_every_size_above_its_mass() -> None:
    """``n`` lives only in Condition 2, so a certificate is not tied to the ``n`` it declares.

    The n = 17 record reaches n = 18 and n = 19 through the monotonicity step
    T-016 records, but it does not need it: its own mass is under both, so the
    same atoms decide those cases directly. The operational consequence is the
    one worth pinning -- a run whose covering value lands between 17 and 18
    raises n = 18 and leaves n = 17 where it was.
    """
    certificate = n17_load()
    assert least_size_certified(certificate.total_mass) == 17
    for size in (17, 18, 19):
        assert certificate.total_mass < size
    # Condition 2 is strict, so mass exactly n certifies n + 1 and not n.
    assert least_size_certified(Fraction(17)) == 18
    assert least_size_certified(Fraction(203, 12)) == 17

    # And the two limits agree without being made to. A side above the ceiling
    # forces the mass past n by Condition 5, which is exactly the size this then refuses.
    for n in (11, 12, 17, 20):
        assert grid_refutation_order(n) ** 2 >= n
        assert least_size_certified(Fraction(grid_refutation_order(n) ** 2)) > n


def test_a_signed_weight_is_refused_before_anything_is_decided() -> None:
    """Nonnegative weights are the theorem's precondition, and a forgery shows why.

    Five atoms in a container of side 11/10 with B = 3/5: +2 at the centre and
    -1 at each corner. Total mass -2 < 1, every admissible B-square covers the
    centre and at most one corner, so every placement carries mass at least 1.
    Every one of the five conditions holds, and the object would "prove"
    s(1) >= 11/10, which is false: s(1) = 1. The counting step that turns a
    covering into a bound is monotonicity of the measure, and signed weights
    break it. PR 78's adversarial review found this (its F1); the fixture is
    retained so that the verifier can never accept it again.
    """
    side = Fraction(11, 10)
    atoms = (
        Atom("centre", Fraction(11, 20), Fraction(11, 20), Fraction(2)),
        Atom("c00", Fraction(0), Fraction(0), Fraction(-1)),
        Atom("c01", Fraction(0), side, Fraction(-1)),
        Atom("c10", side, Fraction(0), Fraction(-1)),
        Atom("c11", side, side, Fraction(-1)),
    )
    with pytest.raises(ValueError, match="weight -1 < 0"):
        Certificate(
            n=1,
            outer_side=side,
            square_side=Fraction(3, 5),
            atoms=atoms,
            half_tangents=(Fraction(0), Fraction(1, 2)),
            symmetry="D4",
        )
    # The same atoms with the corners lightened to zero are a legal object and
    # are refused on the theorem's own terms: the total is 2 >= n = 1.
    legal = tuple(
        atom if atom.weight > 0 else Atom(atom.label, atom.x, atom.y, Fraction(0))
        for atom in atoms
    )
    certificate = Certificate(
        n=1,
        outer_side=side,
        square_side=Fraction(3, 5),
        atoms=legal,
        half_tangents=(Fraction(0), Fraction(1, 2)),
        symmetry="D4",
    )
    verdict = verify(certificate)
    assert not verdict.accepted
    assert any("Condition 2" in failure for failure in verdict.failures)
