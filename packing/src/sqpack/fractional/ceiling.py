"""Ceiling certificates: exact duals that bound what the fractional method can prove.

`sqpack.fractional.certificate` proves ``s(n) >= L`` from a measure of mass
below ``n`` that every closed ``B``-square at a net angle inside ``[0, L]^2``
captures at least one unit of. The least mass any such measure can have is the
optimum of a covering linear program, and its dual is a fractional packing:
non-negative weights on placements whose *depth* -- the weighted number of
placements containing a point -- is at most 1 everywhere in the container.
Weak duality is one line. For any covering measure ``mu`` and any such family
``y``::

    sum_P y_P  <=  sum_P y_P mu(P)  =  integral of depth dmu  <=  mu([0, L]^2).

So a family of total weight at least ``n`` shows that *every* covering measure
has mass at least ``n``, and no certificate of the kind `verify` accepts exists
at this ``(L, B, net)`` -- on any site set, at any weights, however it was
searched for. That is a theorem about the method's reach, not about ``s(n)``:
it says nothing about whether ``n`` unit squares fit in side ``L``. It also
transfers upward in ``L`` (a covering measure at a larger side restricts to a
corner sub-container) and to every net containing the angles the family uses;
it does not transfer to a larger ``B`` or to a coarser net.

Two regimes are decided, and the verdict names which applies:

``net``   every placement is a ``B``-square whose angle is in the net. The
          ceiling holds for this ``B`` and every net containing those angles.
``unit``  every placement has side at least 1 and an angle in ``[0, pi/4]``.
          A unit square at any such angle contains a ``B``-square at a net
          angle whenever ``B (1 + D) < 1`` -- condition ``Condition 4`` -- so the
          ceiling holds for *every* ``(B, net)`` the method can use at all.
          This is the rejection route `H-061` registered.

A placement whose angle is the mirror image of an admissible one -- half-tangent
``(1 - t) / (1 + t)`` for an admissible ``t`` -- is admissible only against
D4-symmetric measures, which is what condition ``Condition 1`` demands of a certificate
anyway. The verdict records whether that weaker form was needed.

Depth is a finite sum of indicators of closed convex sets, so it is upper
semi-continuous and constant on the open faces of the arrangement cut by the
placements' edge lines and the container walls. Every face of that arrangement
inside the bounded container has a vertex in its closure, and a closed square
containing a face contains its closure, so the maximum depth over the container
is attained at a vertex: the intersection of two non-parallel lines. Those are
finitely many and every one that matters is decided in exact arithmetic. Floats
only screen: a pair of lines whose float intersection lies outside the container
by more than a fixed margin, or a vertex whose float depth -- computed with
every membership test loosened by that margin -- falls short of 1 by more than
the margin, cannot be a counterexample, because the rounding error of a double
on these quantities is smaller than the margin by four orders of magnitude.
Nearly parallel pairs, where a float intersection is unreliable, are never
screened and always decided exactly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from itertools import pairwise
from typing import Any

import numpy as np

from sqpack.fractional.model import Direction, rotation_from_half_tangent

# Floats screen, and this margin is what makes the screen safe. Coordinates
# here are below 10, direction cosines below 1, and a double carries 53 bits,
# so the rounding error of any projection or intersection with a determinant
# above ``NEAR_PARALLEL`` is below 1e-12. The margin exceeds that by four
# orders of magnitude and the exact decision is made on anything inside it.
SCREEN_MARGIN = 1e-8
NEAR_PARALLEL = 1e-3

Line = tuple[Fraction, Fraction, Fraction]


@dataclass(frozen=True, slots=True)
class Placement:
    """A closed square in the container with a non-negative weight.

    The angle is the half-tangent ``t`` of ``theta / 2``, so the rotation is
    exactly rational; the side is normally the method's ``B`` and may be 1 or
    more for the unit regime. Nothing here is a float.
    """

    half_tangent: Fraction
    centre_x: Fraction
    centre_y: Fraction
    weight: Fraction
    side: Fraction

    def __post_init__(self) -> None:
        if self.weight < 0:
            raise ValueError("placement weights must be non-negative")
        if self.side <= 0:
            raise ValueError("placement sides must be positive")
        if self.half_tangent < 0:
            raise ValueError("half-tangents are non-negative: fold the angle into [0, pi/2)")

    @property
    def direction(self) -> Direction:
        return rotation_from_half_tangent(str(self.half_tangent), self.half_tangent)

    @property
    def reflected_half_tangent(self) -> Fraction:
        """The half-tangent of ``pi/2 - theta``: the square's mirror image."""
        return (1 - self.half_tangent) / (1 + self.half_tangent)

    def slabs(self) -> tuple[Fraction, Fraction, Fraction, Fraction, Fraction, Fraction]:
        """``(ax, ay, u, bx, by, v)``: the square is ``|a.p - u| <= h``, ``|b.p - v| <= h``."""
        d = self.direction
        u = d.ux * self.centre_x + d.uy * self.centre_y
        v = d.vx * self.centre_x + d.vy * self.centre_y
        return d.ux, d.uy, u, d.vx, d.vy, v

    def contains(self, x: Fraction, y: Fraction) -> bool:
        ax, ay, u, bx, by, v = self.slabs()
        half = self.side / 2
        if abs(ax * x + ay * y - u) > half:
            return False
        return abs(bx * x + by * y - v) <= half

    def corners(self) -> tuple[tuple[Fraction, Fraction], ...]:
        d = self.direction
        half = self.side / 2
        return tuple(
            (
                self.centre_x + half * (su * d.ux + sv * d.vx),
                self.centre_y + half * (su * d.uy + sv * d.vy),
            )
            for su, sv in ((1, 1), (-1, 1), (-1, -1), (1, -1))
        )

    def lines(self) -> tuple[Line, ...]:
        ax, ay, u, bx, by, v = self.slabs()
        half = self.side / 2
        return (
            _normalise_line((ax, ay, u - half)),
            _normalise_line((ax, ay, u + half)),
            _normalise_line((bx, by, v - half)),
            _normalise_line((bx, by, v + half)),
        )


def _normalise_line(line: Line) -> Line:
    nx, ny, c = line
    if nx < 0 or (nx == 0 and ny < 0):
        return (-nx, -ny, -c)
    return line


@dataclass(frozen=True, slots=True)
class ConditionReport:
    name: str
    detail: str
    holds: bool = field(kw_only=True)


@dataclass(frozen=True, slots=True)
class CeilingVerdict:
    conditions: tuple[ConditionReport, ...]
    total_weight: Fraction
    max_depth: Fraction
    vertices: int
    decided_exactly: int
    regime: str
    symmetric_only: bool

    @property
    def proved(self) -> bool:
        return all(condition.holds for condition in self.conditions)

    @property
    def failures(self) -> tuple[str, ...]:
        return tuple(c.name for c in self.conditions if not c.holds)

    @property
    def statement(self) -> str:
        """The theorem the verdict entitles its holder to, in one sentence."""
        if not self.proved:
            return "nothing: " + ", ".join(self.failures)
        measures = "D4-symmetric measure" if self.symmetric_only else "measure"
        if self.regime == "unit":
            scope = (
                "for every shrunken side B and direction net satisfying "
                "Condition 3 and Condition 4, "
                "every closed unit square in the container"
            )
        else:
            scope = (
                "for this B and every net containing the angles used, "
                "every closed B-square at a net angle in the container"
            )
        return (
            f"no {measures} of mass below {float(self.total_weight):.6f} captures mass 1 "
            f"in {scope}; the fractional method cannot certify this n at this side or "
            "any larger side, and this says nothing about whether n unit squares fit"
        )


@dataclass(frozen=True, slots=True)
class CeilingCertificate:
    """A candidate ceiling at one ``(n, L, B, net)``.

    ``square_side`` and ``half_tangents`` are the method's ``B`` and net -- the
    instrument being bounded, not a property of the placements, which carry
    their own sides and angles and are checked against them.
    """

    n: int
    outer_side: Fraction
    square_side: Fraction
    half_tangents: tuple[Fraction, ...]
    placements: tuple[Placement, ...]

    def __post_init__(self) -> None:
        if self.n < 1:
            raise ValueError("n must be positive")
        if self.outer_side <= 0 or self.square_side <= 0:
            raise ValueError("sides must be positive")
        if len(self.half_tangents) < 2:
            raise ValueError("the direction net needs at least two directions")
        if list(self.half_tangents) != sorted(set(self.half_tangents)):
            raise ValueError("half-angle tangents must be strictly increasing")
        if self.half_tangents[0] != 0:
            raise ValueError("the direction net must start at angle zero")
        if not self.placements:
            raise ValueError("a ceiling needs at least one placement")

    @property
    def total_weight(self) -> Fraction:
        return sum((p.weight for p in self.placements), start=Fraction(0))

    @property
    def largest_half_gap_tangent(self) -> Fraction:
        return max(
            (right - left) / (1 + left * right) for left, right in pairwise(self.half_tangents)
        )

    def scaled(self, factor: Fraction) -> CeilingCertificate:
        """The same family with every weight multiplied by ``factor``."""
        return CeilingCertificate(
            self.n,
            self.outer_side,
            self.square_side,
            self.half_tangents,
            tuple(
                Placement(p.half_tangent, p.centre_x, p.centre_y, p.weight * factor, p.side)
                for p in self.placements
            ),
        )

    def to_record(self) -> dict[str, Any]:
        return {
            "n": self.n,
            "outer_side": str(self.outer_side),
            "square_side": str(self.square_side),
            "half_tangents": [str(t) for t in self.half_tangents],
            "placements": [
                [
                    str(p.half_tangent),
                    str(p.centre_x),
                    str(p.centre_y),
                    str(p.weight),
                    str(p.side),
                ]
                for p in self.placements
            ],
        }

    @classmethod
    def from_record(cls, record: dict[str, Any]) -> CeilingCertificate:
        return cls(
            int(record["n"]),
            Fraction(record["outer_side"]),
            Fraction(record["square_side"]),
            tuple(Fraction(t) for t in record["half_tangents"]),
            tuple(
                Placement(Fraction(t), Fraction(x), Fraction(y), Fraction(w), Fraction(s))
                for t, x, y, w, s in record["placements"]
            ),
        )


def _admissibility(certificate: CeilingCertificate) -> tuple[ConditionReport, str, bool]:
    """Classify every placement; the regime is the weakest any placement needs."""

    net = set(certificate.half_tangents)
    last = certificate.half_tangents[-1]
    reaches = last * last + 2 * last - 1 >= 0
    containment = certificate.square_side * (1 + certificate.largest_half_gap_tangent) < 1
    needs_net = False
    symmetric_only = False
    for index, p in enumerate(certificate.placements):
        verdict: tuple[str, bool] | None = None
        for tangent, mirrored in ((p.half_tangent, False), (p.reflected_half_tangent, True)):
            if p.side >= 1 and reaches and containment and tangent * tangent + 2 * tangent <= 1:
                verdict = ("unit", mirrored)
                break
            if p.side == certificate.square_side and tangent in net:
                verdict = ("net", mirrored)
                break
        if verdict is None:
            return (
                ConditionReport(
                    "K0 every placement is admissible",
                    f"placement {index} (side {p.side}, half-tangent {p.half_tangent}) is "
                    "neither a B-square at a net angle nor a unit square within pi/4",
                    holds=False,
                ),
                "none",
                symmetric_only,
            )
        needs_net = needs_net or verdict[0] == "net"
        symmetric_only = symmetric_only or verdict[1]
    regime = "net" if needs_net else "unit"
    detail = f"{len(certificate.placements)} placements in the {regime} regime"
    if symmetric_only:
        detail += ", some at mirrored angles (D4-symmetric measures only)"
    return (
        ConditionReport("K0 every placement is admissible", detail, holds=True),
        regime,
        symmetric_only,
    )


def _condition_inside(certificate: CeilingCertificate) -> ConditionReport:
    side = certificate.outer_side
    for index, p in enumerate(certificate.placements):
        for x, y in p.corners():
            if x < 0 or y < 0 or x > side or y > side:
                return ConditionReport(
                    "K1 every placement lies in the container",
                    f"placement {index} has a corner at ({x}, {y}) outside [0, {side}]^2",
                    holds=False,
                )
    return ConditionReport(
        "K1 every placement lies in the container",
        f"all {len(certificate.placements)} placements have every corner in [0, {side}]^2",
        holds=True,
    )


def arrangement_lines(certificate: CeilingCertificate) -> list[Line]:
    """Every edge line of every placement, plus the four container walls."""
    side = certificate.outer_side
    lines: list[Line] = [
        (Fraction(1), Fraction(0), Fraction(0)),
        (Fraction(1), Fraction(0), side),
        (Fraction(0), Fraction(1), Fraction(0)),
        (Fraction(0), Fraction(1), side),
    ]
    seen = set(lines)
    for p in certificate.placements:
        for line in p.lines():
            if line not in seen:
                seen.add(line)
                lines.append(line)
    return lines


def exact_intersection(first: Line, second: Line) -> tuple[Fraction, Fraction] | None:
    """Where two lines meet, exactly, or None when they are parallel."""
    determinant = first[0] * second[1] - first[1] * second[0]
    if determinant == 0:
        return None
    x = (first[2] * second[1] - second[2] * first[1]) / determinant
    y = (first[0] * second[2] - second[0] * first[2]) / determinant
    return x, y


def container_vertices(
    certificate: CeilingCertificate, lines: list[Line]
) -> list[tuple[Fraction, Fraction]]:
    """Every pairwise intersection that lies in the closed container, exactly.

    Pairs are screened in floats and decided exactly: a pair is skipped only
    when its float intersection misses the container by more than the margin
    *and* the pair is far from parallel, so the float point is trustworthy.
    """
    side = certificate.outer_side
    data = np.array([[float(a), float(b), float(c)] for a, b, c in lines])
    count = len(lines)
    high = float(side) + SCREEN_MARGIN
    found: set[tuple[Fraction, Fraction]] = set()
    for i in range(count - 1):
        a, b, e = data[i]
        c, d, f = data[i + 1 :, 0], data[i + 1 :, 1], data[i + 1 :, 2]
        determinant = a * d - b * c
        safe = np.where(np.abs(determinant) > NEAR_PARALLEL, determinant, 1.0)
        x = (e * d - f * b) / safe
        y = (a * f - c * e) / safe
        inside = (x >= -SCREEN_MARGIN) & (x <= high) & (y >= -SCREEN_MARGIN) & (y <= high)
        decide = (np.abs(determinant) <= NEAR_PARALLEL) | inside
        for offset in np.flatnonzero(decide):
            exact = exact_intersection(lines[i], lines[i + 1 + int(offset)])
            if exact is None:
                continue
            if 0 <= exact[0] <= side and 0 <= exact[1] <= side:
                found.add(exact)
    return sorted(found)


def float_family(
    certificate: CeilingCertificate,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Slab normals, offsets, half-sides and weights of the family, as floats."""
    normals = []
    offsets = []
    halves = []
    weights = []
    for p in certificate.placements:
        ax, ay, u, bx, by, v = p.slabs()
        normals.append([[float(ax), float(ay)], [float(bx), float(by)]])
        offsets.append([float(u), float(v)])
        halves.append(float(p.side) / 2)
        weights.append(float(p.weight))
    return np.array(normals), np.array(offsets), np.array(halves), np.array(weights)


def loose_membership(
    points: np.ndarray,
    normals: np.ndarray,
    offsets: np.ndarray,
    halves: np.ndarray,
) -> np.ndarray:
    """Which placements contain which points, every test loosened by the margin.

    Loosening makes the result a superset of the exact membership at the exact
    point, which is the direction the screen needs.
    """
    slack = halves[None, :] + SCREEN_MARGIN
    first = np.abs(points @ normals[:, 0, :].T - offsets[None, :, 0]) <= slack
    second = np.abs(points @ normals[:, 1, :].T - offsets[None, :, 1]) <= slack
    return first & second


def maximum_depth(
    certificate: CeilingCertificate,
    vertices: list[tuple[Fraction, Fraction]],
) -> tuple[Fraction, int, tuple[Fraction, Fraction] | None]:
    """The exact maximum depth over the vertices, and how many were decided exactly.

    A vertex whose loosened float depth is below ``1 - SCREEN_MARGIN`` has exact
    depth below 1 and is not decided; every other vertex is, and the exact
    depth is summed only over the placements the loosened test admits, which
    is a superset of the exact members.
    """
    if not vertices:
        return Fraction(0), 0, None
    normals, offsets, halves, weights = float_family(certificate)
    points = np.array([[float(x), float(y)] for x, y in vertices])
    worst = Fraction(0)
    where: tuple[Fraction, Fraction] | None = None
    decided = 0
    chunk = max(1, 2_000_000 // max(1, len(certificate.placements)))
    for start in range(0, points.shape[0], chunk):
        block = points[start : start + chunk]
        loose = loose_membership(block, normals, offsets, halves)
        depth = loose.astype(float) @ weights
        for local in np.flatnonzero(depth >= 1 - SCREEN_MARGIN):
            x, y = vertices[start + local]
            exact = Fraction(0)
            for member in np.flatnonzero(loose[local]):
                placement = certificate.placements[member]
                if placement.contains(x, y):
                    exact += placement.weight
            decided += 1
            if exact > worst:
                worst, where = exact, (x, y)
    return worst, decided, where


def verify_ceiling(certificate: CeilingCertificate) -> CeilingVerdict:
    """Decide the ceiling exactly. Never short-circuits: every condition is reported."""

    admissible, regime, symmetric_only = _admissibility(certificate)
    conditions = [admissible, _condition_inside(certificate)]
    lines = arrangement_lines(certificate)
    vertices = container_vertices(certificate, lines)
    worst, decided, where = maximum_depth(certificate, vertices)
    conditions.append(
        ConditionReport(
            "K2 depth at most 1 at every arrangement vertex",
            f"maximum depth {worst} = {float(worst):.9f}"
            + (f" at {where}" if where is not None else "")
            + f" over {len(vertices)} vertices, {decided} decided exactly",
            holds=worst <= 1,
        )
    )
    total = certificate.total_weight
    conditions.append(
        ConditionReport(
            "K3 total weight at least n",
            f"total {total} = {float(total):.9f} against n = {certificate.n}",
            holds=total >= certificate.n,
        )
    )
    return CeilingVerdict(
        tuple(conditions),
        total,
        worst,
        len(vertices),
        decided,
        regime,
        symmetric_only,
    )


def scaled_to_unit_depth(
    certificate: CeilingCertificate,
) -> tuple[CeilingCertificate, Fraction]:
    """Divide every weight by the exact maximum depth when that exceeds 1.

    A family found in floating point is rarely feasible to the last digit.
    Scaling restores feasibility exactly and costs only the factor, which is
    returned so the caller can see what the search left on the table.
    """
    lines = arrangement_lines(certificate)
    vertices = container_vertices(certificate, lines)
    worst, _, _ = maximum_depth(certificate, vertices)
    if worst <= 1:
        return certificate, Fraction(1)
    return certificate.scaled(1 / worst), worst


__all__ = [
    "CeilingCertificate",
    "CeilingVerdict",
    "ConditionReport",
    "Placement",
    "arrangement_lines",
    "container_vertices",
    "exact_intersection",
    "float_family",
    "loose_membership",
    "maximum_depth",
    "scaled_to_unit_depth",
    "verify_ceiling",
]
