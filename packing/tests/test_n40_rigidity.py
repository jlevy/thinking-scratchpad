"""`n = 40` is infinitesimally flexible, and the witness is what has to be protected.

This is a first-party finding against a source that annotates the packing "Rigid.", so the
assertions are written to fail loudly if the witness ever stops being one. Three things
have to hold together and each is checked from the pose rather than read back from the
record: the motion is nonzero, it has exactly zero gap rate on every contact that holds in
all branches, and every pair that touches at a corner still has an axis that separates
along it. Drop any one and the vector stops being a motion.

The other assertion worth its place is the negative one. An assessor that intersects the
corner disjunctions reports all 120 coordinates pinned -- that is, reports this pose rigid.
`D-391` is therefore a defect with a measured consequence rather than a counterfactual one,
and the test says so, because a future "simplification" that reinstates the intersection
would otherwise look like it agreed with the catalogue.
"""

from __future__ import annotations

import json

import pytest

from devtools.assess_n5_rigidity import (
    DOF,
    active_contacts,
    certify_target,
    constraint_rows,
    contact_axes,
    disjunctive_pairs,
    gap_rate,
    incident_contacts,
    nullspace,
    separating,
    verify_target_weights,
)
from devtools.assess_n40_rigidity import (
    OUT,
    assess,
    axis_groups,
    branch_contacts,
    find_witness,
    load_pose,
    retained_ray,
    single_axis_contacts,
)
from devtools.n40_rays import WIDER_RAYS


def _record() -> dict:
    return json.loads(OUT.read_text(encoding="utf-8"))


@pytest.mark.slow
def test_the_witness_is_a_motion_checked_from_the_pose() -> None:
    """The finding, re-derived. Nothing here trusts the record's copy of it."""
    pose = load_pose()
    contacts = active_contacts(pose)
    found = find_witness(pose, contacts)
    assert found is not None
    motion, selection = found

    assert any(value.sign() != 0 for value in motion)

    single = constraint_rows(pose, single_axis_contacts(pose, contacts))
    assert len(single) == 248
    assert all(gap_rate(row, motion).sign() == 0 for row in single)

    groups = axis_groups(pose, contacts)
    assert len(groups) == 42
    for pair, group in groups.items():
        rows = constraint_rows(pose, group[selection[pair]])
        assert all(gap_rate(row, motion).sign() >= 0 for row in rows), pair


def test_only_the_tilted_block_moves() -> None:
    """Sixteen squares turning together, and no frame square displaced at all.

    The shape of the motion is the reason every earlier instrument missed it: the
    translation-escape screen decides one square translating, and this is sixteen turning.
    """
    witness = _record()["witness"]

    assert witness["squares_that_turn"] == list(range(24, 40))
    assert witness["squares_that_move"] == list(range(24, 40))
    assert witness["frame_squares_move"] == []


def test_intersecting_the_disjunctions_reports_the_pose_rigid() -> None:
    """`D-391`'s cost, measured on this pose rather than argued in the abstract."""
    reported = _record()["what_an_intersecting_assessor_reports"]

    assert reported["coordinates_checked"] == 48
    assert reported["pinned"] == 48
    assert reported["uncertified"] == []
    assert "which is false" in reported["verdict_it_would_report"]

    verification = _record()["witness"]["verification"]
    assert verification["rows_violated_if_the_disjunctions_are_intersected"] == 42
    assert verification["disjunctive_pairs_with_an_admissible_axis"] == 42
    # Two counts that are easy to conflate: 42 rows, spread over 24 pairs, not 42 pairs.
    assert verification["pairs_giving_up_an_axis"] == 24


@pytest.mark.slow
def test_the_null_space_is_what_makes_the_candidate_exact() -> None:
    """No rounding anywhere: a null vector is in the cone by construction.

    A direction proposed by a linear program has to be rationalized before it can be
    checked in the field, and a rationalized vertex generally stops satisfying the system
    it came from -- which is what made the first search for this witness find nothing.
    """
    pose = load_pose()
    contacts = active_contacts(pose)
    rows = constraint_rows(pose, single_axis_contacts(pose, contacts))
    basis = nullspace(pose, rows)

    assert len(basis) == 5
    for vector in basis:
        assert all(gap_rate(row, vector).sign() == 0 for row in rows)


def test_flexibility_is_not_promoted_to_not_rigid() -> None:
    """The distinction the record exists to keep.

    An infinitesimal flex is a first-order object. Along this one the gaps curve shut at
    order `t^2`, so it is not a motion, and moving `n = 40` to `not-rigid` would assert
    something nobody has shown.
    """
    built = _record()

    assert built["verdict"]["infinitesimally_rigid"] is False
    assert "stays undetermined" in built["subject"]["promotes_nothing"]
    assert "not a motion" in built["subject"]["promotes_nothing"]
    assert "local rigidity" in built["verdict"]["what_is_not_claimed"]
    assert "t^2" in built["witness"]["second_order_behaviour"]


def test_the_contact_model_is_measured_not_assumed() -> None:
    """`D-390` and `D-391` in numbers, taken from the pose."""
    pose = load_pose()
    incident = incident_contacts(pose)
    contacts = active_contacts(pose)

    assert len(incident) == 608
    assert len(contacts) == 400
    assert len(disjunctive_pairs(pose, contacts)) == 42
    assert len(contact_axes(pose, contacts)) == 98

    dropped = [one for one in incident if one not in set(contacts)]
    assert len(dropped) == 208
    assert all(one.kind == "pair" for one in dropped), "no wall row is ever dropped"
    for one in dropped:
        assert one.host is not None
        assert one.edge is not None
        assert not separating(pose, one.host, one.edge, one.moving)


@pytest.mark.slow
def test_the_witness_turns_every_block_square_at_the_same_rate() -> None:
    """What the motion is, geometrically: the block's squares counter-rotating in place."""
    pose = load_pose()
    found = find_witness(pose, active_contacts(pose))
    assert found is not None
    motion, _ = found

    spins = {index: motion[index * DOF + 2] for index in range(24, 40)}
    first = spins[24]
    assert first.sign() != 0
    for index, spin in spins.items():
        assert (spin - first).sign() == 0, index
    for index in range(24):
        assert motion[index * DOF + 2].sign() == 0


@pytest.mark.exhaustive_exact
def test_the_record_round_trips() -> None:
    """Minutes: the intersecting-assessor section runs 240 linear programs."""
    assert _record() == assess()


def test_the_witness_is_refused_at_second_order() -> None:
    """The flex is not the start of a motion, and that is a certificate rather than a plot.

    Along the witness 104 of the 283 tight contacts curve into the obstacle. A feasible arc
    would need a second-order correction `y` with `A y >= -q`; a non-negative `w` with
    `w . A = 0` and `w . q < 0` says there is none, because it would give
    `0 = w . A y >= -w . q > 0`. Both halves are decided in the field.
    """
    second = _record()["witness"]["second_order"]

    assert second["obstructed"] is True
    assert second["negative_curvature"] == 104
    assert second["tight_rows"] == 283
    assert second["certificate"]["w_dot_q_is_negative"] is True
    assert second["certificate"]["rows_carrying_weight"] > 0


def test_the_obstruction_is_not_read_as_second_order_rigidity() -> None:
    """One flex refused is not every flex refused, and the record has to keep saying so.

    `n = 5` earns the phrase because its cone is one-dimensional and that one direction is
    obstructed. Here a five-dimensional null space was swept over a short integer range in
    a single branch, so the cone's dimension is not known and the phrase would be a claim
    nobody has evidence for.
    """
    built = _record()

    assert (
        "this witness, and only this one"
        in built["witness"]["second_order"]["what_this_settles"]
    )
    assert (
        "not second-order rigid on this evidence"
        in built["witness"]["second_order"]["what_this_settles"]
    )
    assert "Second-order rigidity" in built["scope"]["not_established"]


@pytest.mark.slow
def test_only_tight_rows_enter_the_obstruction() -> None:
    """The soundness condition on the self-stress, checked against the branch itself.

    A contact whose gap already opens at first order imposes nothing at second order.
    Letting one into the stress would assemble a refusal out of constraints that are not
    binding, which is a certificate for a system nobody is solving.
    """
    pose = load_pose()
    contacts = active_contacts(pose)
    found = find_witness(pose, contacts)
    assert found is not None
    motion, selection = found

    rows = constraint_rows(pose, branch_contacts(pose, contacts, selection))
    tight = [row for row in rows if gap_rate(row, motion).sign() == 0]
    slack = [row for row in rows if gap_rate(row, motion).sign() > 0]

    assert len(tight) == _record()["witness"]["second_order"]["tight_rows"]
    assert len(tight) + len(slack) == len(rows), "no row is violated in this branch"


def test_the_admissible_part_of_the_null_space_is_a_line() -> None:
    """ "A witness exists" and "the flex is one-dimensional" are different claims.

    The second is measured: of the 3124 nonzero integer combinations in `[-2, 2]^5` of the
    null basis, four extend to a branch, and all four are multiples of a single basis
    vector. Inside the subspace where every all-branch contact is tight, the admissible set
    is exactly a line -- the same shape as `n = 5`, two orders of magnitude larger.
    """
    sweep = _record()["admissible_part_of_the_null_space"]

    assert sweep["swept"] == 3124
    assert sweep["extend"] == 4
    assert sweep["basis_directions_used"] == [4]
    assert sweep["is_a_single_line"] is True
    assert "may be larger than this line" in sweep["what_it_does_not_bound"]


def test_the_cone_is_larger_than_the_line() -> None:
    """The sweep's open question, answered: directions outside the null space exist.

    Each retained ray opens at least one all-branch contact strictly, which is exactly what
    the null-space sweep cannot reach -- a null vector holds every one of those rows tight.
    So no argument that refuses a single direction can settle `n = 40`, and the record must
    not read as though one could.
    """
    wider = _record()["outside_the_null_space"]

    assert wider["retained"] == 6
    assert wider["all_verified"] is True
    assert wider["rank"] == 5
    for ray in wider["rays"]:
        assert ray["in_the_cone"] is True
        assert ray["admissible"] is True
        assert ray["all_branch_rows_opened"] > 0


def test_no_frame_square_moves_in_any_admissible_direction() -> None:
    """The sharpest thing measured about this packing.

    Every direction found, by the null-space route and by the sampler alike, turns squares
    of the tilted block and leaves all twenty-four axis-aligned ones exactly where they are.
    That is what makes "n = 40 flexes" too coarse a statement: the frame is held and the
    block is the mechanism.
    """
    wider = _record()["outside_the_null_space"]

    assert wider["frame_squares_that_ever_move"] == []
    assert wider["squares_that_move_in_any"] == list(range(24, 40))
    assert _record()["witness"]["frame_squares_move"] == []


def test_every_retained_ray_is_refused_at_second_order() -> None:
    """Seven refusals, and the record still declines to call it second-order rigidity."""
    wider = _record()["outside_the_null_space"]

    assert wider["all_obstructed"] is True
    for ray in wider["rays"]:
        assert ray["second_order"]["obstructed"] is True
        assert ray["second_order"]["certificate"]["w_dot_q_is_negative"] is True

    assert "not seven of them" in _record()["scope"]["not_established"]
    assert "no argument here" in _record()["scope"]["not_established"]


@pytest.mark.slow
def test_the_retained_rays_are_rebuilt_from_the_pose_not_trusted() -> None:
    """The data module holds coefficients; the field arithmetic is redone here."""
    pose = load_pose()
    contacts = active_contacts(pose)
    single = constraint_rows(pose, single_axis_contacts(pose, contacts))

    assert len(WIDER_RAYS) == 6
    for entries in WIDER_RAYS:
        assert all(index >= 72 for index in entries), "frame coordinates are never carried"
        motion = retained_ray(pose, entries)
        assert all(gap_rate(row, motion).sign() >= 0 for row in single)
        assert any(gap_rate(row, motion).sign() > 0 for row in single)


def test_most_of_the_frame_is_proved_pinned_rather_than_searched() -> None:
    """The half of this that is a proof, kept apart from the half that is a search.

    Every branch's cone sits inside the relaxed cone, so a coordinate the relaxed rows pin
    is pinned however the disjunctions resolve. Fifty-two of the frame's seventy-two go
    that way, each with a Farkas certificate verified in the field. The other twenty do
    not, and no amount of searching turns that into a proof.
    """
    frame = _record()["can_the_frame_move"]

    assert frame["frame_coordinates"] == 72
    assert frame["proved_zero_in_every_branch"] == 52
    assert len(frame["not_proved"]) == 20
    assert "every branch's cone is inside the relaxed cone" in frame["how_that_is_a_proof"]


def test_the_frame_search_reports_coverage_not_a_verdict() -> None:
    """The guard against the count becoming a claim.

    Forty targeted searches, twenty-four of them reaching a direction in the relaxed cone,
    none of them admissible. That is coverage. `n = 40`'s twenty remaining frame
    coordinates are not shown pinned by it, and the record has to keep saying so -- the
    translation-escape screen carries the same registered limitation for the same reason.
    """
    frame = _record()["can_the_frame_move"]

    assert frame["targeted_searches"] == 40
    assert frame["reachable_in_the_relaxed_cone"] == 24
    assert frame["admissible_directions_found"] == 0
    assert "weak evidence by construction" in frame["what_the_search_does_not_show"]
    assert "translation-escape screen" in frame["what_the_search_does_not_show"]


def test_twelve_block_squares_provably_turn_at_one_rate() -> None:
    """An observation about seven vectors, turned into a theorem about every branch.

    `certify_target` pins a linear functional rather than a coordinate, so
    `omega_i - omega_j` and its negative together prove the two squares turn together in
    every branch -- whatever the 42 disjunctions do. Sixty-six pairs certify and
    transitivity connects twelve of the sixteen.
    """
    block = _record()["does_the_block_turn_as_one"]

    assert block["pairs_tested"] == 120
    assert block["pairs_proved_equal"] == 66
    assert block["largest_component"] == 12
    assert "proved by certificates" in block["meaning"]


def test_the_four_left_out_are_the_blocks_interior() -> None:
    """Which four, and why that is the right four to be left with.

    Squares 29, 30, 33 and 34 are the interior cells of the four-by-four block: every
    contact they have is with another block square, so the rows that hold in all branches
    reach them least. An arbitrary four would have been a reason to distrust the search.
    """
    block = _record()["does_the_block_turn_as_one"]

    assert block["left_out"] == [29, 30, 33, 34]
    assert block["they_are_the_interior_cells"] is True
    assert "sound and not complete" in block["what_is_not_proved"]


def test_a_functional_certificate_is_verified_not_proposed() -> None:
    """The relation is re-derived from the pose, and both signs are required.

    One sign alone gives an inequality; the pair gives the equality. A change that dropped
    the second sign would turn a proved relation into a half-proved one silently.
    """
    pose = load_pose()
    rows = constraint_rows(pose, single_axis_contacts(pose, active_contacts(pose)))
    zero, one = pose.field.rational(0), pose.field.rational(1)

    target = [zero] * len(rows[0])
    target[24 * DOF + 2] = one
    target[25 * DOF + 2] = -one
    forward = certify_target(pose, rows, target)
    backward = certify_target(pose, rows, [-value for value in target])

    assert forward is not None
    assert backward is not None
    assert verify_target_weights(pose, rows, forward, target)
    assert all(weight.sign() >= 0 for weight in forward)


def test_the_cone_is_bounded_to_forty_five_dimensions() -> None:
    """A real bound, and nowhere near tight enough to settle anything.

    Seventy-five functionals vanishing on the known span are pinned in every branch, so
    every admissible motion lies in their common kernel: 45 dimensions rather than 120.
    The known directions span six. The factor between those two numbers is what is left,
    and this route cannot reduce it -- the all-branch rows can never bound below the
    relaxed cone's own span, measured at rank 41.
    """
    bound = _record()["how_far_the_cone_is_bounded"]

    assert bound["known_directions"] == 7
    assert bound["their_span"] == 6
    assert bound["annihilator_dimension"] == 114
    assert bound["functionals_proved_zero"] == 75
    assert bound["cone_lies_in_dimension_at_most"] == 45
    assert bound["measured_span_of_the_relaxed_cone"] == 41


def test_the_bound_says_why_the_route_stops() -> None:
    """The guard against 45 reading as an answer rather than as where the method ends."""
    bound = _record()["how_far_the_cone_is_bounded"]

    assert "never bound below that cone's own span" in bound["why_the_route_stops"]
    assert "none becomes vacuous" in bound["why_the_route_stops"]
    assert "still 2^42 and not a route" in _record()["scope"]["not_established"]
