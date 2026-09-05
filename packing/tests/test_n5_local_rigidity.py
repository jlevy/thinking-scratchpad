"""The half-angle chart is the whole local feasible set, and it carries `T-012` exactly.

`T-012` decides the first two orders at Goebel's `n = 5` pose and cannot decide isolation.
`H-060`'s argument needs one more object before it can: an intrinsic chart in which the
*entire* local feasible set is a finite polynomial system with exactly known margins, so
that the curve-selection and coefficient induction has something exact to run on.

These assertions exist because every one of them is a way the instrument could look right
and be wrong. A count adopted from a plan rather than computed, a denominator whose sign
was never checked, a support feature identified by the wrong criterion, a binding that
compares the chart against a private copy of `T-012` rather than against `T-012` -- each
would produce a clean receipt and a false theorem.
"""

from __future__ import annotations

import dataclasses

import pytest

from cases.gobel5.packing import build
from devtools.assess_n5_rigidity import active_contacts, load_pose
from sqpack.local_rigidity import controls
from sqpack.local_rigidity.binding import (
    FieldMismatchError,
    bind,
    load_t012_system,
    require_same_field,
)
from sqpack.local_rigidity.chart import (
    Chart,
    ChartPreconditionError,
    HalfAngleTransform,
    pose_from_case,
)
from sqpack.local_rigidity.instrument import assess
from sqpack.local_rigidity.polynomial import Poly
from sqpack.local_rigidity.receipt import build_payload, digest, element_algebraic
from sqpack.local_rigidity.system import (
    ActiveMarginError,
    DisjunctiveTouchError,
    build_neighborhood,
    build_system,
    is_feasible,
    require_active_margins_zero,
)

AGENDA_COUNTS = {
    "wall_corner_active": 16,
    "wall_corner_inactive": 64,
    "touching_pairs": 4,
    "noncontact_pairs": 6,
    "active_total": 20,
}


@pytest.fixture(scope="module")
def chart() -> Chart:
    return Chart(pose_from_case("cases.gobel5.packing.build", build()))


@pytest.fixture(scope="module")
def system(chart: Chart):
    return build_system(chart)


@pytest.fixture(scope="module")
def t012():
    return load_t012_system()


@pytest.fixture(scope="module")
def determination(chart: Chart, t012):
    """Built once: the reduction audit evaluates several hundred exact chart points."""
    built, _ = assess(chart, t012)
    return built


# -- the chart's own algebra -------------------------------------------------


def test_the_cleared_denominators_are_squares_plus_one(chart: Chart) -> None:
    """Positivity is an identity, not a sampled radius.

    `D - 1 = u^2` holds on all of `R^15`, so every cleared denominator is at least one
    everywhere and clearing never flips an inequality's sense. A denominator whose sign
    was only observed near the pose would leave the entire receipt conditional on a bound
    nobody wrote down.
    """
    witnesses = chart.denominator_certificate()
    assert len(witnesses) == 5
    assert all(witness.verified for witness in witnesses)
    assert {witness.margin for witness in witnesses} == {"1"}


def test_the_chart_is_injective_with_a_full_neighborhood_as_its_image(chart: Chart) -> None:
    """Four polynomial identities, not an appeal to the shape of `arctan`."""
    checks = chart.injectivity_certificate()
    assert [check.name for check in checks] == [
        "injectivity/equal-cosine-forces-equal-squares",
        "injectivity/equal-sine-at-v-equals-minus-u",
        "image/half-turn-is-the-only-omitted-rotation",
        "image/every-other-rotation-is-attained",
    ]
    assert all(check.holds for check in checks)


def test_the_cleared_matrix_is_a_positive_multiple_of_a_rotation(chart: Chart) -> None:
    """`M^T M = D^2 I` is what makes the constant `1/2` the right constant."""
    assert all(check.holds for check in chart.orthogonality_certificate())
    assert all(check.holds for check in chart.base_normal_certificate())


@pytest.mark.parametrize(
    "transform",
    [controls.WRONG_DENOMINATOR, controls.WRONG_MATRIX, controls.WRONG_ORIENTATION],
)
def test_an_impostor_chart_is_refused_before_any_margin_is_read(
    chart: Chart, transform: HalfAngleTransform
) -> None:
    """A rationalising substitution that is not this one must not be usable.

    `1 - u^2` vanishes at `u = +-1`, so clearing by it flips inequalities; the off-diagonal
    deviations break `M^T M = D^2 I`, so the cleared normal is not a rotation of the base
    normal and the pair gaps are not gaps.
    """
    with pytest.raises(ChartPreconditionError):
        Chart(chart.pose, transform).require_valid()


# -- the accounting ----------------------------------------------------------


def test_the_counts_are_computed_and_agree_with_the_agenda(system) -> None:
    """The agenda's numbers are checked against the pose, never adopted from it."""
    assert system.verify_counts(AGENDA_COUNTS) == {}
    counts = system.counts()
    assert counts["wall_corner_inequalities"] == 80
    assert counts["sat_branches"] == 80
    assert counts["sat_corner_inequalities"] == 320
    assert counts["pairs"] == 10


def test_the_enumeration_is_complete_by_recomputed_cardinality(system) -> None:
    """A dropped branch enlarges the feasible set, so cardinality is a guard not a note."""
    assert system.book.enumeration_is_complete()
    assert system.book.expected_cardinality() == system.book.actual_cardinality()


def test_the_active_system_is_exactly_t012s_contact_list(system, t012) -> None:
    """Twenty inequalities, and the same twenty both instruments call contacts."""
    keys = {key for key, _ in system.active_constraints()}
    assert len(keys) == 20
    assert keys == set(t012.contact_keys)
    assert len(active_contacts(load_pose())) == 20


def test_every_touching_pair_touches_along_exactly_one_support_feature(system) -> None:
    """One zero branch and one zero corner each, or the tangent cone is a union.

    Two zero branches would make local non-overlap a disjunction, and intersecting it
    reports a smaller feasible set -- a more rigid pose than the geometry has.
    """
    assert len(system.touching_pairs) == 4
    for report in system.touching_pairs:
        zero_branches = [
            branch for branch in report.branches if branch.minimum().margin.sign() == 0
        ]
        assert len(zero_branches) == 1
        zeros = [one for one in zero_branches[0].constraints if one.margin.sign() == 0]
        assert len(zeros) == 1
        assert sum(1 for branch in report.branches if branch.minimum().margin.sign() < 0) == 7


def test_the_load_bearing_margins_are_the_ones_the_lane_reported(system) -> None:
    """Two numbers the proof lane depends on, recomputed here from the pose."""
    inactive = system.inactive_walls
    least = inactive[0]
    for constraint in inactive[1:]:
        if (constraint.margin - least.margin).sign() < 0:
            least = constraint
    assert element_algebraic(least.margin) == "1 - 1/4*sqrt(2)"

    negative = [
        condition
        for condition in build_neighborhood(system).conditions
        if condition.sense == "negative"
    ]
    assert len(negative) == 28
    largest = negative[0]
    for condition in negative[1:]:
        if (condition.margin - largest.margin).sign() > 0:
            largest = condition
    assert element_algebraic(largest.margin) == "-1/4*sqrt(2)"


def test_the_neighborhood_is_strict_conditions_and_not_a_radius(system) -> None:
    """A hundred strictly positive and twenty-eight strictly negative, all open."""
    neighborhood = build_neighborhood(system)
    assert neighborhood.valid()
    assert len(neighborhood.conditions) == 128
    positive = [one for one in neighborhood.conditions if one.sense == "positive"]
    assert len(positive) == 100
    assert all(condition.margin.sign() != 0 for condition in neighborhood.conditions)


def test_a_zero_margin_cannot_stand_in_for_a_strict_one(system) -> None:
    """Continuity carries a strict sign into a neighborhood and carries nothing from zero."""
    outcome = controls.zero_margin(system)
    assert outcome.rejected
    assert outcome.findings["neighborhood_valid"] is False


# -- the binding -------------------------------------------------------------


def test_the_chart_jets_are_t012s_rows_and_q_under_the_declared_transform(
    chart: Chart, system, t012
) -> None:
    """The finding this instrument exists to produce, checked row by row.

    `grad G_j` is `T-012`'s row times `diag(1, 1, 2)` per square and one positive scalar;
    the second jet along the free direction is `T-012`'s `q` under the same scalar. The
    comparison is against `devtools.assess_n5_rigidity` itself, because a binding against a
    private copy of the rows would certify agreement with itself.
    """
    certificate = bind(chart, system, t012)
    assert certificate.holds
    assert len(certificate.rows) == 20
    assert certificate.active_key_agreement
    assert certificate.chart_free_variables == ("u4",)
    assert certificate.t012_free_variables == ("w4",)
    assert all(row.scalar_is_positive for row in certificate.rows)
    assert {row.denominator_at_base for row in certificate.rows} == {"poly[1,0]"}


def test_the_second_jet_scales_as_the_square_of_the_chart_direction(
    chart: Chart, system
) -> None:
    """`q` at the chart's own unit rotation is four times `T-012`'s, and that is not a bug.

    `q` is quadratic in the direction and the transform doubles the rotation rate, so the
    chart unit `e_u4` corresponds to `omega = 2` and reports `4 * q`. Recording both
    normalisations keeps a later reader from reading a factor of four as a disagreement.
    """
    field = chart.field
    active = dict(system.active_constraints())
    unit = [field.zero] * chart.arity
    unit[14] = field.one
    half = [field.zero] * chart.arity
    half[14] = field.rational(1) / field.rational(2)
    for key, polynomial in active.items():
        at_unit = polynomial.second_derivative_along(unit)
        at_half = polynomial.second_derivative_along(half)
        assert (at_unit - at_half * field.rational(4)).sign() == 0
        expected = "-2" if key.startswith("pair") else "0"
        assert element_algebraic(at_unit) == expected


def test_two_declarations_of_the_same_field_are_reconciled_and_two_fields_are_not() -> None:
    """Coefficient transport is legitimate only between identically declared fields."""
    left = load_pose().field
    right = build()[2]
    require_same_field(left, right)
    from sqpack.field import NumberField  # noqa: PLC0415 - the counterexample field

    with pytest.raises(FieldMismatchError):
        require_same_field(left, NumberField((1, 0, -3), (1, 2)))


# -- feasibility and the controls -------------------------------------------


def test_the_pose_is_feasible_and_its_axis_neighbours_are_not(chart: Chart, system) -> None:
    """The predicate must accept the pose and reject the obvious escapes.

    Rotating the middle square is refused exactly, which is the same obstruction `T-012`
    certifies at second order, arrived at here by deciding the full non-overlap system.
    """
    assert is_feasible(system.book, chart.origin())
    field = chart.field
    for index in (0, 1, 14):
        for sign in (1, -1):
            point = chart.origin()
            point[index] = field.rational(sign) / field.rational(1000)
            assert not is_feasible(system.book, point)


def test_the_exp034_family_is_real_at_its_own_side_and_absent_at_goebels(
    chart: Chart,
) -> None:
    """`exp-034`'s flex exists, and it is not a flex of this pose. Both parts are computed.

    A predicate that could not find `exp-034`'s certified two-parameter family would be
    too strict to be trusted anywhere; one that found it at Goebel's fixed side would be
    reporting a motion that the sides alone forbid. The container sides differ by
    `3 sqrt(2)/4 - 1 > 0`, so the family is not in `H-060`'s configuration space at all.
    """
    outcome = controls.exp034_angle_and_slide(chart)
    assert outcome.rejected
    findings = outcome.findings
    assert findings["sides_are_equal"] is False
    assert findings["exp034_base_is_feasible"] is True
    assert findings["family_members_feasible_at_own_side"] == findings["family_members_probed"]
    assert findings["family_members_feasible_at_gobel_side"] == 0
    assert findings["family_passes_through_the_optimum"] is False


def test_a_changed_support_feature_is_refused_by_the_instrument_itself(
    chart: Chart, system, t012
) -> None:
    """The control must call the tool, not adjudicate for it.

    `BC-153` found the first version of this control tautological: it compared keys and
    margins inline and never invoked a guard or the binding, so it restated its own
    premises. Every substitution is now applied to a real `ConstraintSystem` and handed
    back, and both refusals are required.

    The finding survives the correction, in its qualified form. Four of the twelve
    siblings have *exactly the same gradient* as the contact they replace, so the gradient
    check catches eight. The restricted second jet separates all twelve, but it is not an
    independent identifier: it is the exact affine function `-2 * (margin + 1)` of the
    support feature's own base margin, so it separates them precisely when their margins
    do. The recomputed base margin is what decides, and that is the statement the receipt
    keeps.
    """
    outcome = controls.changed_feature(chart, system, t012)
    assert outcome.rejected
    findings = outcome.findings
    assert findings["count"] == 12
    assert findings["forgery_gradient_caught"] == 8
    assert findings["second_jet_affine_law_holds"] is True
    assert findings["second_jet_is_an_independent_identifier"] is False
    for entry in findings["substitutions"]:
        assert entry["key_swapped_guard_refused"]
        assert entry["key_swapped_binding_refused"]
        assert entry["forgery_guard_refused"]
        assert entry["second_jet_is_affine_in_the_margin"]
        assert entry["key_swapped_missing_from_t012"] == [entry["substitute"]]


def test_the_restricted_second_jet_is_an_affine_function_of_the_base_margin(
    chart: Chart, system
) -> None:
    """Why the second jet is not a second, independent identifier of a support feature.

    `G = D_h D_k g` with `D(0) = 1`, `D'(0) = 0`, `D''(0) = 2`, and the geometric second
    derivative along a pure host rotation is `-omega^2 (m + 1/2)`. At the chart unit
    `e_u4`, where `omega = 2`, those combine to `G'' = 2m - 4(m + 1/2) = -2(m + 1)`. So the
    jet is an affine reparametrisation of the margin and adds no information the margin
    has not already carried -- checked here on every support feature of every contact
    branch, contacts included.
    """
    field = chart.field
    unit = [field.zero] * chart.arity
    unit[chart.arity - 1] = field.one
    checked = 0
    for report in system.touching_pairs:
        assert report.active_branch is not None
        for constraint in report.active_branch.constraints:
            observed = constraint.polynomial.second_derivative_along(unit)
            predicted = -(constraint.margin + field.one) * field.rational(2)
            assert (observed - predicted).sign() == 0, constraint.key
            checked += 1
    assert checked == 16


def test_an_invented_contact_is_refused_by_the_guard_and_by_the_binding(
    chart: Chart, system, t012
) -> None:
    """Forge a zero margin onto a slack wall and require both refusals to fire.

    The first version of this control compared an enlarged key set against `T-012`'s and
    found it different, which it was by construction. This one mutates the system, so the
    twenty-one-element active set is what the instrument reads.
    """
    outcome = controls.invented_contact(chart, system, t012)
    assert outcome.rejected
    findings = outcome.findings
    assert findings["active_set_size_after_mutation"] == 21
    assert findings["guard_refused"]
    assert findings["binding_holds"] is False
    assert findings["binding_active_key_agreement"] is False
    assert findings["binding_missing_from_t012"] == [findings["invented_key"]]
    assert findings["forged_margin"] == "0"
    assert findings["recomputed_margin"] != "0"


def test_the_active_margin_guard_recomputes_rather_than_trusting_the_record(
    system,
) -> None:
    """A cached margin is not evidence; the guard evaluates the polynomial itself.

    Both mutations the controls use leave a plausible cached margin behind -- one renames
    the contact, the other keeps the name and swaps the polynomial -- and only
    recomputation sees either.
    """
    require_active_margins_zero(system)
    report = system.touching_pairs[0]
    assert report.active_branch is not None
    assert report.active_constraint is not None
    substitute = next(
        one
        for one in report.active_branch.constraints
        if one.key != report.active_constraint.key
    )
    renamed = controls.with_active_pair(system, report, substitute)
    with pytest.raises(ActiveMarginError):
        require_active_margins_zero(renamed)

    forged = controls.with_active_pair(
        system,
        report,
        dataclasses.replace(report.active_constraint, polynomial=substitute.polynomial),
    )
    with pytest.raises(ActiveMarginError):
        require_active_margins_zero(forged)


@pytest.mark.slow
def test_a_declared_count_disagreement_blocks_readiness(chart: Chart, t012) -> None:
    """The receipt printed the comparison; now a verdict reads it."""
    wrong, _ = assess(chart, t012, audit=False, expected_counts={"active_total": 19})
    assert wrong.count_disagreements == {"active_total": (19, 20)}
    assert not wrong.instrument_ready
    assert any("disagree" in reason for reason in wrong.refusals)


def test_the_pose_shape_is_checked_and_not_assumed(chart: Chart) -> None:
    """Counter-clockwise winding, unit edges, right angles, inradius one half.

    `BC-153` found these assumed. The outward-normal formula `(dy, -dx)` needs the winding,
    and the constant `1/2` in every pair inequality is the inradius; a clockwise pose would
    invert every separating-axis test and still produce a full receipt.
    """
    checks = chart.pose_shape_certificate()
    assert len(checks) == 65
    assert all(check.holds for check in checks)
    kinds = {check.name.split("/")[1] for check in checks}
    assert kinds == {"counter-clockwise", "unit-edge", "right-angle", "inradius"}


def test_an_edge_flush_touch_is_refused_rather_than_intersected() -> None:
    """Two unit squares meeting along a whole edge are not this reduction's case."""
    field = build()[2]
    q = field.rational
    one = field.one

    def axis(cx, cy):
        half = one / q(2)
        return [
            (cx - half, cy - half),
            (cx + half, cy - half),
            (cx + half, cy + half),
            (cx - half, cy + half),
        ]

    from sqpack.local_rigidity.chart import BasePose  # noqa: PLC0415 - local fixture

    pose = BasePose(
        label="edge-flush-pair",
        field=field,
        side=q(3),
        centres=((q(1) / q(2), q(1) / q(2)), (q(3) / q(2), q(1) / q(2))),
        corners=(
            tuple(axis(q(1) / q(2), q(1) / q(2))),
            tuple(axis(q(3) / q(2), q(1) / q(2))),
        ),
    )
    with pytest.raises(DisjunctiveTouchError):
        build_system(Chart(pose))


@pytest.mark.slow
def test_every_control_rejects(chart: Chart, system, t012, determination) -> None:
    """A certificate that cannot fail is not evidence. All eight must refuse."""
    outcomes = controls.run_all(chart, system, determination, t012)
    assert [one.name for one in outcomes] == [
        "changed_feature",
        "zero_margin",
        "omitted_constraint",
        "invented_contact",
        "side_release",
        "wrong_chart",
        "certificate_drift",
        "exp034_angle_and_slide",
    ]
    failed = [one.name for one in outcomes if not one.rejected]
    assert not failed, f"controls that failed to reject: {failed}"


def test_the_determination_never_claims_isolation(determination) -> None:
    """The instrument builds the object the proof needs; it does not prove the theorem."""
    assert determination.instrument_ready
    assert determination.isolation_decided is False
    assert determination.probe.tested == 180
    assert not determination.probe.witnesses
    assert "isolation" in determination.probe.probe_is_not_a_proof.lower()


def test_the_receipt_digest_is_stable_and_moves_under_drift(determination, system) -> None:
    """Replayability, as a byte comparison rather than a claim."""
    payload = build_payload(determination, system)
    assert digest(payload) == digest(build_payload(determination, system))
    outcome = controls.certificate_drift(determination, system)
    assert outcome.rejected
    assert outcome.findings["digest"] != outcome.findings["after_margin_mutation"]


@pytest.mark.usefixtures("system")
def test_the_local_reduction_agrees_with_full_feasibility_inside_the_neighborhood(
    determination,
) -> None:
    """The reduction is a statement about `U`, so it is checked as one.

    At every sampled chart point that lies inside `U`, the full eight-branch
    separating-axis predicate and the twenty-inequality local system must return the same
    verdict. One disagreement would mean the reduction as written is false; agreement is
    corroboration of the statement, and the continuity argument remains the proof.
    """
    audit = determination.audit
    assert audit is not None
    assert audit.consistent
    assert audit.counterexamples == ()
    assert audit.points_inside > 0
    assert audit.agreements == audit.points_inside
    assert "corroborates" in audit.audit_is_not_a_proof
    # The inside-U filter must actually exclude something, or it is untested.
    assert audit.points_tested > audit.points_inside
    assert "boundary" in audit.sample_is_not_adversarial


@pytest.mark.usefixtures("determination")
def test_the_mathematical_inputs_are_declared_rather_than_implied() -> None:
    """The boundary between what is computed and what is cited is written down."""
    from sqpack.local_rigidity.instrument import (  # noqa: PLC0415 - record, not behaviour
        DECLARED_MATHEMATICAL_INPUTS,
    )

    names = {entry["name"] for entry in DECLARED_MATHEMATICAL_INPUTS}
    assert "separating-axis theorem for convex polygons" in names
    assert "continuity of polynomials" in names
    assert all(
        set(entry) == {"name", "statement", "used_for", "machine_checked_here"}
        for entry in DECLARED_MATHEMATICAL_INPUTS
    )


# -- the polynomial engine ---------------------------------------------------


def test_the_polynomial_engine_differentiates_and_restricts_exactly() -> None:
    """The three operations the certificates are built from, on a case done by hand."""
    field = build()[2]
    x = Poly.variable(field, 2, 0)
    y = Poly.variable(field, 2, 1)
    polynomial = (x * x).scale(field.rational(3)) + x * y - Poly.constant(field, 2, field.alpha)
    assert polynomial.degree() == 2
    assert polynomial.support() == (0, 1)
    assert (
        element_algebraic(polynomial.evaluate([field.rational(1), field.rational(2)]))
        == "5 - sqrt(2)"
    )
    assert (
        element_algebraic(
            polynomial.derivative(0).evaluate([field.rational(1), field.rational(1)])
        )
        == "7"
    )
    jet = polynomial.restrict_to_line([field.rational(1), field.rational(1)])
    assert element_algebraic(jet[0]) == "-sqrt(2)"
    assert element_algebraic(jet[2]) == "4"
    assert (
        element_algebraic(
            polynomial.second_derivative_along([field.rational(1), field.rational(1)])
        )
        == "8"
    )
