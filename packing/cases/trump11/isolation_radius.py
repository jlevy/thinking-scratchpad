#!/usr/bin/env python3
"""Explicit isolation radius and quadratic stress constant at Trump's n = 11 pose.

Exp-013 retains 128 derivative-distinct branch matrices ``A_b`` (42 rows, 33 pose
variables) at Trump's exact pose, each with a strictly positive stress ``lambda_b`` and
``A_b^T lambda_b = 0``, so every branchwise linearised cone is ``{0}``.  X-014 sketches
the two constants that turn that qualitative isolation into a box: a modulus
``kappa_b = min { max_j -(A_b v)_j : ||v||_inf = 1 }``, a curvature bound ``K`` on the
active elementary functions, and from them ``rho_0 = min_b 2 kappa_b / K`` (capped by the
gap-to-Lipschitz radius, the symmetry radius and the declared box) together with
``C = max_b ||lambda_b||_1 K / (2 Lambda_b)``.  This module computes both.

The chart is the anchored centre-angle chart: the container ``[0, s]^2`` has its corner
at the origin, square ``i`` is ``(x_i, y_i, theta_i)`` with corners
``c_i + R(theta_i) q_m``, ``q_m in {(+-1/2, +-1/2)}``, and the norm is the sup norm over
the 33 coordinates.  The rows exp-013 retains are the theta-derivatives in this chart,
which the identification self-test below checks row by row.

Floats propose, exact arithmetic confirms.  Every face linear program has an exact
lower bound (weak duality with a rationalised dual, ``t >= -s w_k - sum |w_i|`` for
``w = A^T lambda``, ``lambda`` in the simplex) and an exact upper bound (a rationalised
primal point); the minimising face is re-solved as an exact vertex with its exact dual so
that ``kappa_b`` is pinned exactly wherever the vertex is nondegenerate.  Curvature and
Lipschitz constants are rational upper bounds from coefficient sums on a declared box.
The symmetry radius is certified at a rational threshold by an exact no-perfect-matching
argument.  Nothing retained rests on a float.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

from cases.trump11 import packing as trump11
from cases.trump11 import tangent_cones as tc
from sqpack.exact_lp import LinearRow
from sqpack.field import FieldElement, NumberField
from sqpack.verify import edge_axes, exact_sign, verify_packing

ROOT = Path(__file__).resolve().parents[2]
RECORD = (
    ROOT
    / "campaign/series/series-000-smoke-and-calibration/results"
    / "exp-013-h-026-trump-tangent.json"
)
FROZEN_INPUTS = (
    "campaign/series/series-000-smoke-and-calibration/results/exp-013-h-026-trump-tangent.json",
    "cases/trump11/packing.py",
    "cases/trump11/tangent_cones.py",
)

VARIABLES = tc.EXPECTED_VARIABLES
SQUARES = tc.EXPECTED_SQUARES
FACES = 2 * VARIABLES
FAR_WALLS = ("right", "top")
BODY_CORNERS = (
    (Fraction(-1, 2), Fraction(-1, 2)),
    (Fraction(1, 2), Fraction(-1, 2)),
    (Fraction(1, 2), Fraction(1, 2)),
    (Fraction(-1, 2), Fraction(1, 2)),
)
WALLS = ("left", "bottom", "right", "top")

# Rational upper bounds used by the coefficient sums.  Each is checked by
# `rational_bound_selftest` rather than trusted: 14143^2 >= 2 * 10^8 and 7072^2 >= 5 * 10^7.
SQRT2_UP = Fraction(14143, 10000)
INV_SQRT2_UP = Fraction(7072, 10000)
# Archimedes' bracket on pi, from Measurement of a Circle: PI_LO is his lower
# bound of two hundred twenty-three seventy-firsts, PI_HI his upper bound of
# twenty-two sevenths, and every use below takes whichever side it needs.
PI_LO = Fraction(223, 71)
PI_HI = Fraction(22, 7)

DEFAULT_BOX = Fraction(1, 64)
DEFAULT_SYMMETRY_THRESHOLD = Fraction(1, 8)
KILL_RADIUS = Fraction(1, 10**6)

CLAIM_BOUNDARY = (
    "Lower bound on the chart-distance radius, in the anchored centre-angle chart at "
    "fixed side U = Trump's exact side: no chart point within rho_0 of the labelled pose "
    "in the sup norm is a packing in [0, U]^2 other than the pose itself. Side-stability "
    "clause: a packing of side s' <= U embedded in [0, U]^2 is a feasible pose at side U, "
    "so any such packing within rho_0 of the pose is the pose, which touches all four "
    "walls, hence s' = U; on the same ball a packing at side U + sigma satisfies "
    "sigma >= -C ||v||^2 for every branch stress. No optimality, no uniqueness beyond the "
    "ball, no global statement, and nothing about a different geometrical arrangement of "
    "the unit squares."
)


class IsolationRadiusError(ValueError):
    """A typed refusal: malformed input, drifted inventory, or a failed exact check."""


# ----------------------------------------------------------------------------------------
# Exact helpers


def scale(value: FieldElement, factor: Fraction) -> FieldElement:
    """Multiply a field element by a rational without a polynomial product."""
    return value.field.element([coefficient * factor for coefficient in value.coeffs])


def combine(field: NumberField, terms: list[tuple[FieldElement, Fraction]]) -> FieldElement:
    """Exact rational linear combination of field elements, coefficient-wise."""
    if not terms:
        return field.zero
    width = len(terms[0][0].coeffs)
    total = [Fraction(0)] * width
    for value, factor in terms:
        if factor == 0:
            continue
        for index, coefficient in enumerate(value.coeffs):
            if coefficient:
                total[index] += coefficient * factor
    return field.element(total)


def absolute(value: FieldElement) -> FieldElement:
    return value if value.sign() >= 0 else -value


def exact_max(values: list[FieldElement]) -> FieldElement:
    best = values[0]
    for value in values[1:]:
        if (value - best).sign() > 0:
            best = value
    return best


def exact_min(values: list[FieldElement]) -> FieldElement:
    best = values[0]
    for value in values[1:]:
        if (value - best).sign() < 0:
            best = value
    return best


def rational_lower(field: NumberField, value: FieldElement, digits: int = 24) -> Fraction:
    field.refine_to(digits + 8)
    low, _ = field.enclose(value)
    return low


def rational_upper(field: NumberField, value: FieldElement, digits: int = 24) -> Fraction:
    field.refine_to(digits + 8)
    _, high = field.enclose(value)
    return high


def sqrt_upper(value: Fraction, digits: int = 9) -> Fraction:
    """A rational ``r`` with ``r * r >= value``, correct by construction."""
    if value < 0:
        message = f"square root of a negative bound: {value}"
        raise IsolationRadiusError(message)
    unit = Fraction(1, 10**digits)
    guess = Fraction(math.ceil(math.sqrt(float(value)) / float(unit))) * unit
    while guess * guess < value:
        guess += unit
    return guess


def short_lower(value: Fraction, digits: int = 12) -> Fraction:
    """The largest multiple of ``10^-digits`` not above ``value``."""
    unit = Fraction(1, 10**digits)
    return Fraction(math.floor(value / unit)) * unit


def short_upper(value: Fraction, digits: int = 9) -> Fraction:
    unit = Fraction(1, 10**digits)
    return Fraction(math.ceil(value / unit)) * unit


def record_element(value: FieldElement) -> list[str]:
    return [str(coefficient) for coefficient in value.coeffs]


def decimal(field: NumberField, value: FieldElement, digits: int = 20) -> str:
    return field.decimal(value, digits)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rational_bound_selftest() -> dict[str, bool]:
    checks = {
        "sqrt2_upper_bound": SQRT2_UP * SQRT2_UP >= 2,
        "inverse_sqrt2_upper_bound": Fraction(1, 2) <= INV_SQRT2_UP * INV_SQRT2_UP,
        "pi_bounds_ordered": PI_LO < PI_HI,
    }
    if not all(checks.values()):
        message = f"rational bound selftest failed: {checks}"
        raise IsolationRadiusError(message)
    return checks


# ----------------------------------------------------------------------------------------
# The exact witness, its rows, and the retained stresses


@dataclass(frozen=True)
class Witness:
    field: NumberField
    squares: list
    side: FieldElement
    centres: list
    walls: tuple[LinearRow, ...]
    incidences: list[dict]
    contacts: tuple
    branches: list[dict]


def load_witness() -> Witness:
    squares, side, field = trump11.build()
    verification = verify_packing(squares, side, sign=exact_sign)
    if not verification.valid or verification.n != SQUARES:
        message = f"exact Trump witness failed its prerequisite:\n{verification}"
        raise IsolationRadiusError(message)
    walls, incidences, centres = tc.wall_rows(squares, side, field)
    contacts = tc.contact_options(squares, centres, field)
    if len(walls) != tc.EXPECTED_WALL_ROWS or len(contacts) != tc.EXPECTED_CONTACTS:
        message = "active inventory drifted from exp-013"
        raise IsolationRadiusError(message)
    groups = tc.enumerate_branch_groups(walls, contacts)
    if len(groups) != tc.EXPECTED_REDUCED_BRANCHES:
        message = f"expected {tc.EXPECTED_REDUCED_BRANCHES} branches, got {len(groups)}"
        raise IsolationRadiusError(message)
    branches = []
    for index, (_key, group) in enumerate(sorted(groups.items())):
        rows = group["rows"]
        if len(rows) != tc.EXPECTED_BRANCH_ROWS:
            message = f"branch {index} does not have {tc.EXPECTED_BRANCH_ROWS} rows"
            raise IsolationRadiusError(message)
        branches.append(
            {
                "branch": index,
                "rows": rows,
                "raw_selection_count": group["raw_selection_count"],
                "selections": [list(selection) for selection in group["selections"]],
            }
        )
    return Witness(field, squares, side, centres, walls, incidences, contacts, branches)


def reconstruct_stress(
    rows: tuple[LinearRow, ...], certificate: dict, field: NumberField
) -> list[FieldElement]:
    """Rebuild exp-013's exact stress from its retained certificate, or refuse."""
    if not isinstance(certificate, dict):
        message = "certificate must be a mapping"
        raise IsolationRadiusError(message)
    if certificate.get("rank") != VARIABLES:
        message = f"certificate rank is not {VARIABLES}"
        raise IsolationRadiusError(message)
    pivot_rows = certificate.get("pivot_rows")
    free_weights = certificate.get("free_weights")
    if not isinstance(pivot_rows, list) or not isinstance(free_weights, dict):
        message = "certificate lacks pivot_rows or free_weights"
        raise IsolationRadiusError(message)
    pivots = [int(index) for index in pivot_rows]
    weights = {int(index): Fraction(weight) for index, weight in free_weights.items()}
    if len(pivots) != VARIABLES or len(set(pivots)) != VARIABLES:
        message = "certificate pivot rows are not a distinct set of size 33"
        raise IsolationRadiusError(message)
    if set(pivots) | set(weights) != set(range(len(rows))) or set(pivots) & set(weights):
        message = "certificate pivot rows and free weights do not partition the rows"
        raise IsolationRadiusError(message)
    if any(weight <= 0 for weight in weights.values()):
        message = "certificate free weights are not strictly positive"
        raise IsolationRadiusError(message)
    matrix = [
        [rows[pivot].coefficients[coordinate] for pivot in pivots]
        for coordinate in range(VARIABLES)
    ]
    rhs = [
        -combine(
            field,
            [
                (rows[index].coefficients[coordinate], weight)
                for index, weight in weights.items()
            ],
        )
        for coordinate in range(VARIABLES)
    ]
    pivot_weights = tc.exact_solve(matrix, rhs, field)
    if pivot_weights is None:
        message = "certificate pivot system is singular"
        raise IsolationRadiusError(message)
    stress = [field.zero for _ in rows]
    for index, weight in weights.items():
        stress[index] = field.rational(weight)
    for index, weight in zip(pivots, pivot_weights, strict=True):
        stress[index] = weight
    if any(weight.sign() <= 0 for weight in stress):
        message = "reconstructed stress is not strictly positive"
        raise IsolationRadiusError(message)
    for coordinate in range(VARIABLES):
        residual = sum(
            (
                rows[index].coefficients[coordinate] * stress[index]
                for index in range(len(rows))
            ),
            field.zero,
        )
        if not residual.is_zero():
            message = "reconstructed stress leaves a nonzero residual"
            raise IsolationRadiusError(message)
    return stress


def load_record(path: Path = RECORD) -> dict:
    record = json.loads(path.read_text())
    records = record["branches"]["records"]
    if len(records) != tc.EXPECTED_REDUCED_BRANCHES:
        message = "exp-013 record does not carry 128 branches"
        raise IsolationRadiusError(message)
    return record


# ----------------------------------------------------------------------------------------
# The modulus: 66 face linear programs per branch, floats proposing, exact bounds


@dataclass
class FaceResult:
    coordinate: int
    sign: int
    float_value: float
    lower: FieldElement
    upper: FieldElement
    exact: bool
    free_count: int | None = None


def sparse_rows(rows: tuple[LinearRow, ...]) -> list[list[tuple[int, FieldElement]]]:
    return [
        [(index, value) for index, value in enumerate(row.coefficients) if not value.is_zero()]
        for row in rows
    ]


def face_lp(matrix: np.ndarray, coordinate: int, sign: int):
    """min t subject to A v + t >= 0, v_k = sign, -1 <= v <= 1."""
    row_count, variable_count = matrix.shape
    objective = np.zeros(variable_count + 1)
    objective[-1] = 1.0
    a_ub = np.hstack([-matrix, -np.ones((row_count, 1))])
    b_ub = np.zeros(row_count)
    bounds = [(-1.0, 1.0)] * variable_count + [(None, None)]
    bounds[coordinate] = (float(sign), float(sign))
    result = linprog(objective, A_ub=a_ub, b_ub=b_ub, bounds=bounds, method="highs")
    if not result.success or result.x is None:
        message = f"face LP failed on coordinate {coordinate} sign {sign}: {result.message}"
        raise IsolationRadiusError(message)
    return result.x[:variable_count], float(result.x[-1]), -np.asarray(result.ineqlin.marginals)


def rationalise(value: float) -> Fraction:
    return Fraction(format(float(value), ".17g"))


def dual_lower_bound(
    field: NumberField,
    sparse: list[list[tuple[int, FieldElement]]],
    weights: list[Fraction],
    coordinate: int,
    sign: int,
) -> FieldElement:
    """``-s w_k - sum_{i != k} |w_i|`` for ``w = A^T lambda``; valid for any simplex lambda."""
    total = sum(weights)
    if total <= 0:
        message = "dual proposal has no positive weight"
        raise IsolationRadiusError(message)
    columns: list[list[tuple[FieldElement, Fraction]]] = [[] for _ in range(VARIABLES)]
    for row_index, entries in enumerate(sparse):
        weight = weights[row_index] / total
        if weight == 0:
            continue
        for column, value in entries:
            columns[column].append((value, weight))
    w = [combine(field, terms) for terms in columns]
    bound = -scale(w[coordinate], Fraction(sign))
    for index, value in enumerate(w):
        if index != coordinate:
            bound = bound - absolute(value)
    return bound


def primal_upper_bound(
    field: NumberField,
    sparse: list[list[tuple[int, FieldElement]]],
    point: list[Fraction],
) -> FieldElement:
    """``max_j -(A v)_j`` at an exact point of the face."""
    products = [
        combine(field, [(value, point[column]) for column, value in entries])
        for entries in sparse
    ]
    return exact_max([-product for product in products])


def exact_vertex_refinement(
    field: NumberField,
    rows: tuple[LinearRow, ...],
    sparse: list[list[tuple[int, FieldElement]]],
    *,
    coordinate: int,
    sign: int,
    v_float: np.ndarray,
    t_float: float,
    tolerance: float = 1e-6,
) -> tuple[FieldElement, FieldElement, bool, int] | None:
    """Re-solve the face vertex and its dual exactly from the float active set.

    Returns ``(lower, upper, exact, free_count)`` or ``None`` when the float active set does
    not identify a nondegenerate vertex; the caller then keeps the rationalised bounds.
    """
    free = [
        index
        for index in range(VARIABLES)
        if index != coordinate and abs(abs(float(v_float[index])) - 1.0) > tolerance
    ]
    fixed: dict[int, Fraction] = {coordinate: Fraction(sign)}
    for index in range(VARIABLES):
        if index != coordinate and index not in free:
            fixed[index] = Fraction(1 if v_float[index] > 0 else -1)
    products = [
        sum(float(value) * float(v_float[column]) for column, value in entries)
        for entries in sparse
    ]
    active = [
        index
        for index, product in enumerate(products)
        if abs(product + t_float) <= tolerance * (1.0 + abs(t_float))
    ]
    if len(active) < len(free) + 1:
        return None
    system_rows = tuple(
        LinearRow(
            f"active:{index}",
            (*(rows[index].coefficients[column] for column in free), field.one),
        )
        for index in active
    )
    pivots = tc.exact_pivot_rows(system_rows)
    if pivots is None:
        return None
    basis = [active[pivot] for pivot in pivots]
    matrix = [list(system_rows[pivot].coefficients) for pivot in pivots]
    rhs = [
        -combine(
            field,
            [
                (value, fixed[column])
                for column, value in sparse[active[pivot]]
                if column in fixed
            ],
        )
        for pivot in pivots
    ]
    solution = tc.exact_solve(matrix, rhs, field)
    if solution is None:
        return None
    point: list[FieldElement] = [field.zero for _ in range(VARIABLES)]
    for column, value in fixed.items():
        point[column] = field.rational(value)
    for column, value in zip(free, solution[:-1], strict=True):
        point[column] = value
    if any((absolute(point[column]) - field.one).sign() > 0 for column in free):
        return None
    exact_products = [
        sum((value * point[column] for column, value in entries), field.zero)
        for entries in sparse
    ]
    upper = exact_max([-product for product in exact_products])
    # The dual on the same basis: sum_j y_j a_{j,i} = 0 on the free coordinates, sum y = 1.
    size = len(free) + 1
    dual_matrix = [
        [rows[basis[column]].coefficients[free[row]] for column in range(size)]
        for row in range(len(free))
    ]
    dual_matrix.append([field.one for _ in range(size)])
    dual_rhs = [field.zero for _ in range(len(free))] + [field.one]
    dual = tc.exact_solve(dual_matrix, dual_rhs, field)
    if dual is None or any(weight.sign() < 0 for weight in dual):
        return upper, upper, False, len(free)
    w = [
        sum(
            (rows[basis[column]].coefficients[index] * dual[column] for column in range(size)),
            field.zero,
        )
        for index in range(VARIABLES)
    ]
    lower = -scale(w[coordinate], Fraction(sign))
    for index, value in enumerate(w):
        if index != coordinate:
            lower = lower - absolute(value)
    return lower, upper, (lower - upper).is_zero(), len(free)


def branch_modulus(
    field: NumberField,
    rows: tuple[LinearRow, ...],
    *,
    row_weights: list[Fraction] | None = None,
    refine_limit: int = 6,
) -> dict:
    """Exact two-sided bounds on ``kappa_b`` (optionally with per-row positive weights)."""
    if row_weights is not None:
        if len(row_weights) != len(rows) or any(weight <= 0 for weight in row_weights):
            message = "row weights must be positive and one per row"
            raise IsolationRadiusError(message)
        rows = tuple(
            LinearRow(row.label, tuple(scale(value, weight) for value in row.coefficients))
            for row, weight in zip(rows, row_weights, strict=True)
        )
    if any(len(row.coefficients) != VARIABLES for row in rows):
        message = f"every row must have {VARIABLES} coefficients"
        raise IsolationRadiusError(message)
    matrix = tc.as_float_matrix(rows)
    sparse = sparse_rows(rows)
    faces: list[FaceResult] = []
    proposals = {}
    for coordinate in range(VARIABLES):
        for sign in (-1, 1):
            v_float, t_float, lam = face_lp(matrix, coordinate, sign)
            weights = [rationalise(max(value, 0.0)) for value in lam]
            lower = dual_lower_bound(field, sparse, weights, coordinate, sign)
            point = [
                min(Fraction(1), max(Fraction(-1), rationalise(value))) for value in v_float
            ]
            point[coordinate] = Fraction(sign)
            upper = primal_upper_bound(field, sparse, point)
            faces.append(FaceResult(coordinate, sign, t_float, lower, upper, exact=False))
            proposals[(coordinate, sign)] = (v_float, t_float)
    order = sorted(range(len(faces)), key=lambda index: faces[index].float_value)
    refined = 0
    for index in order[:refine_limit]:
        face = faces[index]
        upper_bound = exact_min([item.upper for item in faces])
        if refined and (face.lower - upper_bound).sign() >= 0:
            break
        v_float, t_float = proposals[(face.coordinate, face.sign)]
        result = exact_vertex_refinement(
            field,
            rows,
            sparse,
            coordinate=face.coordinate,
            sign=face.sign,
            v_float=v_float,
            t_float=t_float,
        )
        refined += 1
        if result is None:
            continue
        lower, upper, exact, free_count = result
        if (upper - face.upper).sign() < 0:
            face.upper = upper
        if (lower - face.lower).sign() > 0:
            face.lower = lower
        face.exact = exact and (face.lower - face.upper).is_zero()
        face.free_count = free_count
    kappa_lower = exact_min([face.lower for face in faces])
    kappa_upper = exact_min([face.upper for face in faces])
    best = min(range(len(faces)), key=lambda index: faces[index].float_value)
    return {
        "kappa_lower": kappa_lower,
        "kappa_upper": kappa_upper,
        "exact": (kappa_lower - kappa_upper).is_zero(),
        "argmin_face": {
            "coordinate": faces[best].coordinate,
            "sign": faces[best].sign,
            "free_count": faces[best].free_count,
        },
        "faces": faces,
        "refined_faces": refined,
    }


# ----------------------------------------------------------------------------------------
# The elementary functions: values, gradients, curvature and Lipschitz bounds


@dataclass(frozen=True)
class Elementary:
    kind: str
    label: str
    subject: tuple
    value: FieldElement
    gradient: tuple
    curvature: Fraction
    lipschitz: Fraction

    def lipschitz_on_box(self, box: Fraction) -> FieldElement:
        """``||grad G(z*)||_1 + K rho_box``: each partial moves by at most its Hessian row."""
        field = self.value.field
        total = sum((absolute(value) for value in self.gradient), field.zero)
        return total + field.rational(self.curvature * box)


def rotate_quarter(point):
    return -point[1], point[0]


def dot(left, right):
    return left[0] * right[0] + left[1] * right[1]


def elementary_functions(witness: Witness, box: Fraction) -> list[Elementary]:
    field = witness.field
    squares, centres, side = witness.squares, witness.centres, witness.side
    functions: list[Elementary] = []
    wall_curvature = INV_SQRT2_UP
    wall_lipschitz = 1 + INV_SQRT2_UP
    for square_index, square in enumerate(squares):
        cx, cy = centres[square_index]
        for corner_index, (px, py) in enumerate(square):
            rx, ry = px - cx, py - cy
            for wall in WALLS:
                gradient = [field.zero for _ in range(VARIABLES)]
                if wall == "left":
                    value = px
                    gradient[3 * square_index] = field.one
                    gradient[3 * square_index + 2] = -ry
                elif wall == "right":
                    value = side - px
                    gradient[3 * square_index] = -field.one
                    gradient[3 * square_index + 2] = ry
                elif wall == "bottom":
                    value = py
                    gradient[3 * square_index + 1] = field.one
                    gradient[3 * square_index + 2] = rx
                else:
                    value = side - py
                    gradient[3 * square_index + 1] = -field.one
                    gradient[3 * square_index + 2] = -rx
                functions.append(
                    Elementary(
                        "wall",
                        f"wall:{square_index}:{wall}:corner-{corner_index}",
                        (square_index, wall, corner_index),
                        value,
                        tuple(gradient),
                        wall_curvature,
                        wall_lipschitz,
                    )
                )
    for first in range(SQUARES):
        for second in range(first + 1, SQUARES):
            dx = centres[second][0] - centres[first][0]
            dy = centres[second][1] - centres[first][1]
            distance_upper = sqrt_upper(rational_upper(field, dx * dx + dy * dy))
            reach = distance_upper + 2 * SQRT2_UP * box
            curvature = reach + 6 * SQRT2_UP
            lipschitz = reach + 3 * SQRT2_UP
            for owner in (first, second):
                other = second if owner == first else first
                axes = edge_axes(squares[owner])
                for axis_index, axis in enumerate(axes):
                    normal = rotate_quarter(axis)
                    for order in ("first-before-second", "second-before-first"):
                        positive = second if order == "first-before-second" else first
                        epsilon = 1 if other == positive else -1
                        for corner_index, corner in enumerate(squares[other]):
                            r = (corner[0] - centres[other][0], corner[1] - centres[other][1])
                            d = (
                                centres[other][0] - centres[owner][0],
                                centres[other][1] - centres[owner][1],
                            )
                            # gap = eps * a . (p_w - c_o) - 1/2 for either order: the owner's
                            # own edge projects at a . c_o +- 1/2 exactly.
                            value = scale(
                                dot(axis, (d[0] + r[0], d[1] + r[1])), Fraction(epsilon)
                            ) - field.rational(Fraction(1, 2))
                            gradient = [field.zero for _ in range(VARIABLES)]
                            gradient[3 * other] = scale(axis[0], Fraction(epsilon))
                            gradient[3 * other + 1] = scale(axis[1], Fraction(epsilon))
                            gradient[3 * owner] = scale(axis[0], Fraction(-epsilon))
                            gradient[3 * owner + 1] = scale(axis[1], Fraction(-epsilon))
                            spin = dot(axis, rotate_quarter(r))
                            gradient[3 * other + 2] = scale(spin, Fraction(epsilon))
                            gradient[3 * owner + 2] = scale(
                                dot(normal, d) - spin, Fraction(epsilon)
                            )
                            functions.append(
                                Elementary(
                                    "pair",
                                    f"pair:{first}-{second}:owner-{owner}:axis-{axis_index}:{order}:corner-{other}.{corner_index}",
                                    (first, second, owner, axis_index, order, corner_index),
                                    value,
                                    tuple(gradient),
                                    curvature,
                                    lipschitz,
                                )
                            )
    if len(functions) != 176 + 1760:
        message = f"expected 1936 elementary functions, built {len(functions)}"
        raise IsolationRadiusError(message)
    return functions


def gradient_key(gradient: tuple) -> tuple:
    return tuple(tc.scalar_key(value) for value in gradient)


def identify_rows(witness: Witness, functions: list[Elementary]) -> dict:
    """Match every branch row to a tied elementary function with the same gradient."""
    tied: dict[tuple, list[Elementary]] = {}
    for function in functions:
        if function.value.is_zero():
            tied.setdefault(gradient_key(function.gradient), []).append(function)
    row_curvature: dict[tuple, Fraction] = {}
    row_kind: dict[tuple, str] = {}
    unmatched = []
    all_rows = set()
    for branch in witness.branches:
        for row in branch["rows"]:
            key = tc.row_key(row)
            all_rows.add(key)
            matches = tied.get(key)
            if not matches:
                unmatched.append(row.label)
                continue
            row_curvature[key] = max(function.curvature for function in matches)
            row_kind[key] = matches[0].kind
    if unmatched:
        message = (
            f"{len(unmatched)} branch rows have no tied elementary function: {unmatched[:3]}"
        )
        raise IsolationRadiusError(message)
    contact_pairs = {contact.pair for contact in witness.contacts}
    tied_count = sum(
        1
        for function in functions
        if function.value.is_zero()
        and (function.kind == "wall" or function.subject[:2] in contact_pairs)
    )
    return {
        "distinct_branch_rows": len(all_rows),
        "tied_functions_on_walls_and_contacts": tied_count,
        "row_curvature": row_curvature,
        "row_kind": row_kind,
        "distinct_tied_gradients": len(tied),
    }


def gap_radius(witness: Witness, functions: list[Elementary], box: Fraction) -> dict:
    """The radius on which every contact pair keeps its separating feature among the options.

    Two caps are returned.  ``cap`` uses, for each negative corner gap, the box-aware
    Lipschitz constant ``||grad g(z*)||_1 + K_j rho_box``; ``crude_cap`` uses the
    coefficient-sum constant ``||c_w - c_o||_2 + 2 sqrt2 rho_box + 3 sqrt2``.  Both are exact
    lower bounds on the radius; the first is the sharper one.
    """
    field = witness.field
    contact_pairs = {contact.pair for contact in witness.contacts}
    by_feature: dict[tuple, list[Elementary]] = {}
    for function in functions:
        if function.kind == "pair":
            by_feature.setdefault(function.subject[:5], []).append(function)
    features = []
    cap: FieldElement | None = None
    crude_cap: FieldElement | None = None
    active_features = 0
    for key, members in sorted(by_feature.items()):
        pair = key[:2]
        if pair not in contact_pairs:
            continue
        values = [member.value for member in members]
        feature_gap = exact_min(values)
        if feature_gap.is_zero():
            active_features += 1
            features.append(
                {"feature": key, "gap": decimal(field, feature_gap), "active": True}
            )
            continue
        if feature_gap.sign() > 0:
            message = f"contact pair {pair} has a strictly separating feature {key}"
            raise IsolationRadiusError(message)
        negative = [member for member in members if member.value.sign() < 0]
        crude_radius = exact_max(
            [scale(-member.value, 1 / member.lipschitz) for member in negative]
        )
        radius = exact_max(
            [-member.value / member.lipschitz_on_box(box) for member in negative]
        )
        features.append(
            {
                "feature": key,
                "gap": decimal(field, feature_gap),
                "active": False,
                "radius": decimal(field, radius),
                "crude_radius": decimal(field, crude_radius),
            }
        )
        if cap is None or (radius - cap).sign() < 0:
            cap = radius
        if crude_cap is None or (crude_radius - crude_cap).sign() < 0:
            crude_cap = crude_radius
    if active_features != tc.EXPECTED_RAW_FEATURES:
        message = (
            f"expected {tc.EXPECTED_RAW_FEATURES} active features, found {active_features}"
        )
        raise IsolationRadiusError(message)
    nonzero = [
        absolute(function.value) for function in functions if not function.value.is_zero()
    ]
    least_gap = exact_min(nonzero)
    lipschitz_max = max(function.lipschitz for function in functions)
    contact_lipschitz_max = max(
        function.lipschitz
        for function in functions
        if function.kind == "pair" and function.subject[:2] in contact_pairs
    )
    if cap is None or crude_cap is None:
        message = "no non-active feature on any contact pair"
        raise IsolationRadiusError(message)
    return {
        "cap": cap,
        "crude_cap": crude_cap,
        "least_nonzero_gap": least_gap,
        "lipschitz_max_all": lipschitz_max,
        "lipschitz_max_contacts": contact_lipschitz_max,
        "conservative_cap": scale(least_gap, 1 / lipschitz_max),
        "features": features,
        "active_features": active_features,
    }


# ----------------------------------------------------------------------------------------
# The symmetry radius


def d4_images(witness: Witness):
    side = witness.side
    centres = witness.centres

    def image(name, transform, *, reflect):
        return name, [transform(x, y) for x, y in centres], reflect

    return [
        image("r90", lambda x, y: (side - y, x), reflect=False),
        image("r180", lambda x, y: (side - x, side - y), reflect=False),
        image("r270", lambda x, y: (y, side - x), reflect=False),
        image("mx", lambda x, y: (side - x, y), reflect=True),
        image("my", lambda x, y: (x, side - y), reflect=True),
        image("diag", lambda x, y: (y, x), reflect=True),
        image("anti", lambda x, y: (side - y, side - x), reflect=True),
    ]


def tilted(witness: Witness) -> list[bool]:
    """Which squares are rotated by ``a``: those whose first edge axis is not (0, 1)."""
    flags = []
    for square in witness.squares:
        axis = edge_axes(square)[0]
        flags.append(not axis[0].is_zero())
    return flags


def angle_bounds(witness: Witness) -> dict:
    """Rigorous rational bounds on ``a = 2 arctan u`` and on ``pi/2 - 2a``."""
    field = witness.field
    field.refine_to(12)
    u_lo, u_hi = field.root_bounds()
    if not 0 < u_lo < u_hi < 1:
        message = "root enclosure of u is not inside (0, 1)"
        raise IsolationRadiusError(message)
    a_lo = 2 * (u_lo - u_lo**3 / 3)
    a_hi = 2 * (u_hi - u_hi**3 / 3 + u_hi**5 / 5)
    quarter_lo = PI_LO / 4
    if not a_hi < quarter_lo:
        message = "the tilt is not certified below pi/4"
        raise IsolationRadiusError(message)
    return {
        "a_lo": a_lo,
        "a_hi": a_hi,
        "mixed_lo": a_lo,
        "reflected_lo": PI_LO / 2 - 2 * a_hi,
    }


def perfect_matching(adjacency: list[list[bool]]) -> list[int] | None:
    size = len(adjacency)
    match_to = [-1] * size

    def augment(left: int, seen: list[bool]) -> bool:
        for right in range(size):
            if adjacency[left][right] and not seen[right]:
                seen[right] = True
                if match_to[right] < 0 or augment(match_to[right], seen):
                    match_to[right] = left
                    return True
        return False

    for left in range(size):
        if not augment(left, [False] * size):
            return None
    return match_to


def bottleneck(distances: list[list[float]]) -> float:
    values = sorted({value for row in distances for value in row})
    low, high = 0, len(values) - 1
    while low < high:
        middle = (low + high) // 2
        adjacency = [[value <= values[middle] for value in row] for row in distances]
        if perfect_matching(adjacency) is not None:
            high = middle
        else:
            low = middle + 1
    return values[low]


def symmetry_radius(witness: Witness, threshold: Fraction) -> dict:
    field = witness.field
    flags = tilted(witness)
    bounds = angle_bounds(witness)
    if not (bounds["mixed_lo"] > threshold and bounds["reflected_lo"] > threshold):
        message = "symmetry threshold is not below the certified angle distances"
        raise IsolationRadiusError(message)
    a_float = float(2 * math.atan(field.root_approx()))
    reflected_float = math.pi / 2 - 2 * a_float
    centres = witness.centres
    tolerance = field.rational(threshold)

    def angle_distance(first: int, second: int, *, reflect: bool) -> tuple[str, float]:
        if flags[first] != flags[second]:
            return "mixed", a_float
        if reflect and flags[first]:
            return "reflected", reflected_float
        return "zero", 0.0

    report = []
    certified = True
    nearest = None
    for name, image, reflect in d4_images(witness):
        adjacency = [[False] * SQUARES for _ in range(SQUARES)]
        distances = [[0.0] * SQUARES for _ in range(SQUARES)]
        for first in range(SQUARES):
            for second in range(SQUARES):
                kind, angular = angle_distance(first, second, reflect=reflect)
                dx = absolute(centres[first][0] - image[second][0])
                dy = absolute(centres[first][1] - image[second][1])
                distances[first][second] = max(float(dx), float(dy), angular)
                adjacency[first][second] = (
                    kind == "zero"
                    and (dx - tolerance).sign() < 0
                    and (dy - tolerance).sign() < 0
                )
        matching = perfect_matching(adjacency)
        value = bottleneck(distances)
        report.append(
            {
                "element": name,
                "bottleneck_float": value,
                "below_threshold": matching is not None,
            }
        )
        certified = certified and matching is None
        nearest = value if nearest is None else min(nearest, value)
    relabel = None
    for first in range(SQUARES):
        for second in range(first + 1, SQUARES):
            kind, angular = angle_distance(first, second, reflect=False)
            dx = absolute(centres[first][0] - centres[second][0])
            dy = absolute(centres[first][1] - centres[second][1])
            value = max(float(dx), float(dy), angular)
            relabel = value if relabel is None else min(relabel, value)
            if kind == "zero" and (dx - tolerance).sign() < 0 and (dy - tolerance).sign() < 0:
                certified = False
                report.append(
                    {
                        "element": "identity",
                        "relabelling": [first, second],
                        "below_threshold": True,
                    }
                )
    return {
        "threshold": threshold,
        "certified_distance_at_least_threshold": certified,
        "radius": threshold / 2,
        "nearest_d4_image_float": nearest,
        "nearest_relabelling_float": relabel,
        "angle_bounds": {key: str(value) for key, value in bounds.items()},
        "elements": report,
    }


# ----------------------------------------------------------------------------------------
# Stress constants


def stress_constants(
    witness: Witness,
    branch: dict,
    stress: list[FieldElement],
    curvature: Fraction,
    row_curvature: dict,
) -> dict:
    field = witness.field
    rows = branch["rows"]
    far = far_rows(rows)
    one_norm = sum(stress, field.zero)
    far_stress = sum((stress[index] for index in far), field.zero)
    near_stress = sum((stress[index] for index in near_rows(rows)), field.zero)
    if far_stress.sign() <= 0:
        message = "far-wall stress is not strictly positive"
        raise IsolationRadiusError(message)
    if not (near_stress - far_stress).is_zero():
        message = "near-wall and far-wall stresses differ: translation invariance broken"
        raise IsolationRadiusError(message)
    weighted = sum(
        (
            scale(stress[index], row_curvature[tc.row_key(row)])
            for index, row in enumerate(rows)
        ),
        field.zero,
    )
    ratio = one_norm / far_stress
    uniform = scale(ratio, curvature / 2)
    per_row = weighted / far_stress / 2
    return {
        "one_norm": one_norm,
        "far_wall_stress": far_stress,
        "ratio": ratio,
        "c_uniform": uniform,
        "c_per_row": per_row,
    }


def stress_ratio_identity(witness: Witness, branch: dict, rho: FieldElement) -> dict:
    """Decide exactly whether ``1 - rho e_far`` lies in the column space of ``A_b``.

    When it does, ``lambda^T A_b = 0`` forces ``sum lambda = rho Lambda`` for every stress
    in the branch's cone, so ``||lambda||_1 / Lambda`` is a branch invariant and there is
    nothing for a stress-cone minimisation to improve in the uniform-``K`` constant.
    """
    field = witness.field
    rows = branch["rows"]
    far = far_rows(rows)
    target = [field.one - rho if index in far else field.one for index in range(len(rows))]
    pivots = tc.exact_pivot_rows(rows)
    if pivots is None:
        message = "branch matrix lost full column rank"
        raise IsolationRadiusError(message)
    system = [list(rows[pivot].coefficients) for pivot in pivots]
    direction = tc.exact_solve(system, [target[pivot] for pivot in pivots], field)
    if direction is None:
        message = "pivot system of a full-rank branch is singular"
        raise IsolationRadiusError(message)
    holds = all(
        (
            sum(
                (value * direction[column] for column, value in enumerate(row.coefficients)),
                field.zero,
            )
            - target[index]
        ).is_zero()
        for index, row in enumerate(rows)
    )
    return {"holds": holds, "direction": direction}


def far_rows(rows: tuple[LinearRow, ...]) -> list[int]:
    far = [
        index
        for index, row in enumerate(rows)
        if row.label.startswith("wall:") and row.label.split(":")[2] in FAR_WALLS
    ]
    if len(far) != 9:
        message = f"expected 9 far-wall rows, found {len(far)}"
        raise IsolationRadiusError(message)
    return far


def near_rows(rows: tuple[LinearRow, ...]) -> list[int]:
    return [
        index
        for index, row in enumerate(rows)
        if row.label.startswith("wall:") and row.label.split(":")[2] not in FAR_WALLS
    ]


# ----------------------------------------------------------------------------------------
# Assembly


def deciding_contacts(witness: Witness, branches: list[dict], branch_table: list[dict]) -> list:
    """Which contact's option choice determines the modulus class of a branch."""
    classes = {entry["branch"]: entry["kappa_lower_decimal"] for entry in branch_table}
    result = []
    for position, contact in enumerate(witness.contacts):
        if len(contact.options) < 2:
            continue
        table: dict[int, set[str]] = {}
        for branch in branches:
            for selection in branch["selections"]:
                table.setdefault(selection[position], set()).add(classes[branch["branch"]])
        result.append(
            {
                "pair": list(contact.pair),
                "decides_kappa": all(len(values) == 1 for values in table.values()),
                "options": {
                    contact.options[option].label: sorted(values)
                    for option, values in sorted(table.items())
                },
            }
        )
    return result


def build_result(
    *,
    box: Fraction = DEFAULT_BOX,
    threshold: Fraction = DEFAULT_SYMMETRY_THRESHOLD,
    branch_limit: int | None = None,
    weighted: bool = True,
    identity: bool = True,
    refine_limit: int = 6,
    log=None,
) -> dict:
    started = time.monotonic()
    selftest = rational_bound_selftest()
    witness = load_witness()
    field = witness.field
    record = load_record()
    functions = elementary_functions(witness, box)
    identification = identify_rows(witness, functions)
    row_curvature = identification["row_curvature"]
    curvature = max(row_curvature.values())
    wall_curvature = max(
        value
        for key, value in row_curvature.items()
        if identification["row_kind"][key] == "wall"
    )
    gaps = gap_radius(witness, functions, box)
    symmetry = symmetry_radius(witness, threshold)
    if not symmetry["certified_distance_at_least_threshold"]:
        message = "symmetry threshold certificate failed"
        raise IsolationRadiusError(message)

    branches = witness.branches if branch_limit is None else witness.branches[:branch_limit]
    records_by_branch = {item["branch"]: item for item in record["branches"]["records"]}
    branch_table = []
    kappa_lowers: list[FieldElement] = []
    kappa_uppers: list[FieldElement] = []
    rho_weighteds: list[FieldElement] = []
    c_uniforms: list[FieldElement] = []
    c_per_rows: list[FieldElement] = []
    exact_count = 0
    rho: FieldElement | None = None
    identity_holds = 0
    pair_curvatures = [
        value
        for key, value in row_curvature.items()
        if identification["row_kind"][key] == "pair"
    ]
    for branch in branches:
        stamp = time.monotonic()
        rows = branch["rows"]
        modulus = branch_modulus(field, rows, refine_limit=refine_limit)
        weights = [2 / row_curvature[tc.row_key(row)] for row in rows]
        weighted_modulus = (
            branch_modulus(field, rows, row_weights=weights, refine_limit=refine_limit)
            if weighted
            else None
        )
        stress = reconstruct_stress(
            rows, records_by_branch[branch["branch"]]["certificate"], field
        )
        constants = stress_constants(witness, branch, stress, curvature, row_curvature)
        ratio: FieldElement = constants["ratio"]
        if rho is None:
            rho = ratio
        current_rho: FieldElement = rho
        ratio_matches = (ratio - current_rho).is_zero()
        identity_check = (
            stress_ratio_identity(witness, branch, current_rho) if identity else None
        )
        if identity_check is not None and identity_check["holds"]:
            identity_holds += 1
        entry = {
            "branch": branch["branch"],
            "raw_selection_count": branch["raw_selection_count"],
            "kappa_lower": record_element(modulus["kappa_lower"]),
            "kappa_lower_decimal": decimal(field, modulus["kappa_lower"]),
            "kappa_upper_decimal": decimal(field, modulus["kappa_upper"]),
            "kappa_exact": modulus["exact"],
            "kappa_argmin_face": modulus["argmin_face"],
            "refined_faces": modulus["refined_faces"],
            "stress_one_norm_decimal": decimal(field, constants["one_norm"]),
            "far_wall_stress_decimal": decimal(field, constants["far_wall_stress"]),
            "stress_ratio_decimal": decimal(field, constants["ratio"]),
            "c_uniform_decimal": decimal(field, constants["c_uniform"]),
            "c_per_row_decimal": decimal(field, constants["c_per_row"]),
            "stress_ratio_equals_branch_0": ratio_matches,
            "ratio_identity_in_row_space": (
                identity_check["holds"] if identity_check is not None else None
            ),
            "seconds": round(time.monotonic() - stamp, 3),
        }
        if weighted_modulus is not None:
            entry["rho_weighted_lower_decimal"] = decimal(
                field, weighted_modulus["kappa_lower"]
            )
            entry["rho_weighted_upper_decimal"] = decimal(
                field, weighted_modulus["kappa_upper"]
            )
            entry["rho_weighted_exact"] = weighted_modulus["exact"]
            entry["rho_weighted_argmin_face"] = weighted_modulus["argmin_face"]
        branch_table.append(entry)
        exact_count += int(modulus["exact"])
        kappa_lowers.append(modulus["kappa_lower"])
        kappa_uppers.append(modulus["kappa_upper"])
        if weighted_modulus is not None:
            rho_weighteds.append(weighted_modulus["kappa_lower"])
        c_uniforms.append(constants["c_uniform"])
        c_per_rows.append(constants["c_per_row"])
        if log is not None:
            log(
                f"branch {branch['branch']:3d} kappa [{entry['kappa_lower_decimal'][:14]}, "
                f"{entry['kappa_upper_decimal'][:14]}] exact={modulus['exact']} "
                f"rho_w={entry.get('rho_weighted_lower_decimal', '')[:12]} "
                f"C_u={entry['c_uniform_decimal'][:10]} C_r={entry['c_per_row_decimal'][:10]} "
                f"identity={entry['ratio_identity_in_row_space']} {entry['seconds']}s"
            )
    if rho is None or not kappa_lowers:
        message = "no branch was computed"
        raise IsolationRadiusError(message)
    kappa_lower_all = exact_min(kappa_lowers)
    kappa_upper_all = exact_min(kappa_uppers)
    c_uniform_all = exact_max(c_uniforms)
    c_per_row_all = exact_max(c_per_rows)
    rho_weighted_all = exact_min(rho_weighteds) if rho_weighteds else None
    # With sum lambda = rho Lambda on the cone and near = far wall stress, the pair rows
    # carry exactly (rho - 2) Lambda, so the per-row constant of any stress lies in
    # K_wall + (rho - 2) / 2 * [min K_pair, max K_pair].
    bracket_low = field.rational(wall_curvature) + scale(
        rho - field.rational(2), min(pair_curvatures) / 2
    )
    bracket_high = field.rational(wall_curvature) + scale(
        rho - field.rational(2), max(pair_curvatures) / 2
    )

    kappa_max = max(branch_table, key=lambda item: Fraction(item["kappa_lower_decimal"]))
    kappa_min = min(branch_table, key=lambda item: Fraction(item["kappa_lower_decimal"]))
    modulus_radius = scale(kappa_lower_all, 2 / curvature)
    modulus_radius_rational = rational_lower(field, modulus_radius)
    gap_cap_rational = rational_lower(field, gaps["cap"])
    candidates = {
        "modulus_2kappa_over_K": modulus_radius_rational,
        "gap_to_lipschitz": gap_cap_rational,
        "symmetry_half_distance": symmetry["radius"],
        "declared_box": box,
    }
    rho_0 = min(candidates.values())
    binding = min(candidates, key=lambda name: candidates[name])
    rho_weighted_rational = (
        rational_lower(field, rho_weighted_all) if rho_weighted_all is not None else None
    )
    rho_0_weighted = (
        min(rho_weighted_rational, gap_cap_rational, symmetry["radius"], box)
        if rho_weighted_rational is not None
        else None
    )
    return {
        "schema_version": 1,
        "cell": "BC-199",
        "chart": (
            "anchored centre-angle chart: container [0, s]^2 with a corner at the origin, "
            "square i = (x_i, y_i, theta_i) with corners c_i + R(theta_i) q_m, "
            "q_m in {(+-1/2, +-1/2)}, sup norm over the 33 coordinates, side fixed at U"
        ),
        "claim_boundary": CLAIM_BOUNDARY,
        "inputs": {path: sha256(ROOT / path) for path in FROZEN_INPUTS},
        "box_sup_radius": str(box),
        "branches_computed": len(branches),
        "identification": {
            "distinct_branch_rows": identification["distinct_branch_rows"],
            "distinct_tied_gradients": identification["distinct_tied_gradients"],
            "tied_functions_on_walls_and_contacts": identification[
                "tied_functions_on_walls_and_contacts"
            ],
            "every_branch_row_is_a_tied_elementary_gradient": True,
        },
        "curvature": {
            "K": str(curvature),
            "K_float": float(curvature),
            "K_wall": str(wall_curvature),
            "bound": (
                "K bounds the sum of absolute second derivatives of every active elementary "
                "function on the box: 1/sqrt2 for a wall function, "
                "||c_w - c_o||_2 + 2 sqrt2 rho_box + 6 sqrt2 for a pair function, "
                "with sqrt2 <= 14143/10000 and 1/sqrt2 <= 7072/10000"
            ),
        },
        "gaps": {
            "least_nonzero_gap_decimal": decimal(field, gaps["least_nonzero_gap"]),
            "lipschitz_max_all": str(gaps["lipschitz_max_all"]),
            "lipschitz_max_contacts": str(gaps["lipschitz_max_contacts"]),
            "conservative_cap_decimal": decimal(field, gaps["conservative_cap"]),
            "crude_cap_decimal": decimal(field, gaps["crude_cap"]),
            "cap_decimal": decimal(field, gaps["cap"]),
            "cap_rational_lower": str(gap_cap_rational),
            "cap_rational_lower_short": str(short_lower(gap_cap_rational)),
            "active_features": gaps["active_features"],
            "features": [
                {**item, "feature": list(item["feature"])} for item in gaps["features"]
            ],
        },
        "symmetry": {
            **{
                key: (str(value) if isinstance(value, Fraction) else value)
                for key, value in symmetry.items()
            },
        },
        "modulus": {
            "kappa_min_lower_decimal": decimal(field, kappa_lower_all),
            "kappa_min_upper_decimal": decimal(field, kappa_upper_all),
            "kappa_min_branch": kappa_min["branch"],
            "kappa_max_lower_decimal": kappa_max["kappa_lower_decimal"],
            "kappa_max_branch": kappa_max["branch"],
            "branches_with_exact_kappa": exact_count,
            "two_kappa_over_K_decimal": decimal(field, modulus_radius),
            "two_kappa_over_K_rational_lower": str(modulus_radius_rational),
            "two_kappa_over_K_rational_lower_short": str(short_lower(modulus_radius_rational)),
            "deciding_contacts": deciding_contacts(witness, branches, branch_table),
        },
        "rho_0": {
            "candidates": {key: str(value) for key, value in candidates.items()},
            "candidates_float": {key: float(value) for key, value in candidates.items()},
            "binding": binding,
            "rational_lower_bound": str(rho_0),
            "rational_lower_bound_short": str(short_lower(rho_0)),
            "float": float(rho_0),
            "kill_below_1e-6": rho_0 < KILL_RADIUS,
        },
        "rho_0_weighted": {
            "per_row_K_modulus_rational_lower": str(rho_weighted_rational)
            if rho_weighted_rational is not None
            else None,
            "rational_lower_bound": str(rho_0_weighted) if rho_0_weighted is not None else None,
            "rational_lower_bound_short": (
                str(short_lower(rho_0_weighted)) if rho_0_weighted is not None else None
            ),
            "binding": (
                min(
                    {
                        "modulus_per_row_K": rho_weighted_rational,
                        "gap_to_lipschitz": gap_cap_rational,
                        "symmetry_half_distance": symmetry["radius"],
                        "declared_box": box,
                    }.items(),
                    key=lambda item: item[1],
                )[0]
                if rho_weighted_rational is not None
                else None
            ),
            "float": float(rho_0_weighted) if rho_0_weighted is not None else None,
        },
        "C": {
            "uniform_K_max_decimal": decimal(field, c_uniform_all),
            "uniform_K_rational_upper": str(rational_upper(field, c_uniform_all)),
            "uniform_K_rational_upper_short": str(
                short_upper(rational_upper(field, c_uniform_all))
            ),
            "uniform_K_float": float(c_uniform_all),
            "per_row_K_max_decimal": decimal(field, c_per_row_all),
            "per_row_K_rational_upper": str(rational_upper(field, c_per_row_all)),
            "per_row_K_rational_upper_short": str(
                short_upper(rational_upper(field, c_per_row_all))
            ),
            "per_row_K_float": float(c_per_row_all),
            "stress_cone": {
                "rho_decimal": decimal(field, rho),
                "rho_coefficients_low_degree_first": record_element(rho),
                "ratio_equal_in_every_branch": all(
                    item["stress_ratio_equals_branch_0"] for item in branch_table
                ),
                "identity_checked_branches": identity_holds if identity else 0,
                "identity_holds_in_every_checked_branch": (
                    identity_holds == len(branches) if identity else None
                ),
                "near_equals_far_wall_stress_in_every_branch": True,
                "per_row_bracket_low_decimal": decimal(field, bracket_low),
                "per_row_bracket_high_decimal": decimal(field, bracket_high),
                "decision": (
                    "not minimised: ||lambda||_1 / Lambda = rho is invariant on every branch's "
                    "stress cone (1 - rho e_far lies in the row space), so the uniform-K "
                    "constant cannot move, and the per-row constant of any stress lies in the "
                    "bracket above, so the retained stresses are within its width of the "
                    "minimum"
                ),
            },
        },
        "branches": branch_table,
        "selftests": selftest,
        "elapsed_seconds": round(time.monotonic() - started, 3),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, help="write the JSON record atomically")
    parser.add_argument("--box", default=str(DEFAULT_BOX), help="declared sup-norm box radius")
    parser.add_argument(
        "--threshold", default=str(DEFAULT_SYMMETRY_THRESHOLD), help="symmetry threshold"
    )
    parser.add_argument("--branches", type=int, default=None, help="only the first N branches")
    parser.add_argument(
        "--no-weighted", action="store_true", help="skip the per-row weighted modulus"
    )
    parser.add_argument(
        "--no-identity", action="store_true", help="skip the exact stress-ratio identity"
    )
    parser.add_argument(
        "--refine-limit", type=int, default=6, help="faces re-solved exactly per branch"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = build_result(
        box=Fraction(args.box),
        threshold=Fraction(args.threshold),
        branch_limit=args.branches,
        weighted=not args.no_weighted,
        identity=not args.no_identity,
        refine_limit=args.refine_limit,
        log=lambda line: print(line, flush=True),
    )
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.record:
        args.record.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.record.with_suffix(args.record.suffix + ".tmp")
        temporary.write_text(rendered)
        temporary.replace(args.record)
    summary = {
        key: result[key]
        for key in ("curvature", "gaps", "symmetry", "modulus", "rho_0", "rho_0_weighted", "C")
    }
    summary["gaps"] = {
        key: value for key, value in summary["gaps"].items() if key != "features"
    }
    summary["symmetry"] = {
        key: value for key, value in summary["symmetry"].items() if key != "elements"
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
