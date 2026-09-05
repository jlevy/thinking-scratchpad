#!/usr/bin/env python3
"""Census the near-tight event cells of a retained fractional certificate.

Condition 5 asks only that every reachable event cell carry mass at least one. It
says nothing about how many cells sit *just* above one, and that number is what
decides whether the exact-cover step of Corollary 1a is a check or a search: a tight
set of a few hundred cells clustered around a few dozen positions is a list to
verify, while a tight set filling a positive fraction of the centre domain is a
space to search -- which is also what an integrality gap looks like from inside the
covering program.

The census is read off ``sweep.scaled_mass_grid``, the same dense integer array the
sweep takes its minimum from, so the census and the decision cannot disagree about
what a cell weighs. Every comparison here is between integers on the weights' common
scale, so a margin is decided exactly and no tolerance enters. The two float fields,
both named ``approx_``, are diagnostics for a reader and carry no verdict.

**Epsilon here is a census margin, not a mass gap.** On a *retained* certificate every
reachable cell already carries mass at least one, so ``1 + epsilon`` names a declared
band above that floor and the counts below say how crowded the band is. It is not
``M - n``, the amount by which a covering optimum overshoots the size being certified:
that quantity is negative wherever a certificate holds -- the n = 11 rung at 381/100
carries total mass 434547/40000 = 10.8637 against n = 11 -- and it exists as a positive
number only at a side where a certificate *fails*, which is a different measurement.
Reading these counts as a gap inverts both their sign and their subject.

Usage:
    uv run --frozen python -m devtools.census_tight_cells <certificate.json>
    uv run --frozen python -m devtools.census_tight_cells <certificate.json> \
        --output <report.json> --margins 0,1/100,1/20,1/10

``--output`` is rewritten after every direction, so an interrupted run loses at most
the direction it was in the middle of.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

import numpy as np

from devtools.decide_certificate import load
from sqpack.fractional.certificate import Certificate
from sqpack.fractional.model import Atom, Direction
from sqpack.fractional.sweep import MassGrid, centre_domain, scaled_mass_grid, weight_scale

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent

#: The four margins the near-tight question is asked at: the floor itself, then one,
#: five and ten percent above it.
DEFAULT_MARGINS: tuple[Fraction, ...] = (
    Fraction(0),
    Fraction(1, 100),
    Fraction(1, 20),
    Fraction(1, 10),
)

MARGIN_SEMANTICS = (
    "epsilon is a census margin above the Condition 5 floor of one, not the mass gap "
    "M - n; on a retained certificate every reachable cell already carries mass at "
    "least one and the gap is negative."
)


@dataclass(frozen=True, slots=True)
class Box:
    """The smallest closed rectangle in the rotated frame holding a set of cells.

    The frame is the direction's own ``(u, v)``, which is where the sweep's event
    coordinates live; a box in the container's axes would need the cells' corners
    rotated back and would no longer be a rectangle.
    """

    u_low: Fraction
    u_high: Fraction
    v_low: Fraction
    v_high: Fraction


@dataclass(frozen=True, slots=True)
class MarginCensus:
    """One margin's reading in one direction."""

    margin: Fraction
    tight_cells: int
    components: int
    largest_component: int
    approx_tight_area: float
    box: Box | None


@dataclass(frozen=True, slots=True)
class DirectionCensus:
    """One direction's reading: what is reachable, what is tight, and where.

    ``domain_box`` is the centre domain's own bounding rectangle in the same frame, so
    a tight box can be read against the box it sits in rather than in isolation. The
    centre domain is a rotated square, so its bounding box is the larger of the two.
    """

    index: int
    half_tangent: Fraction
    columns: int
    reachable_cells: int
    minimum_mass: Fraction
    approx_reachable_area: float
    domain_box: Box
    margins: tuple[MarginCensus, ...]


def scaled_threshold(margin: Fraction, scale: int) -> int:
    """The integer a cell's scaled mass is compared against for ``1 + margin``.

    ``floor((1 + margin) * scale)`` is exact for the census because a cell's scaled
    mass is an integer: ``mass <= 1 + margin`` and ``scaled <= floor((1 + margin) *
    scale)`` are the same statement about integers, whatever the margin's denominator
    does to the common scale.
    """

    if margin < 0:
        raise ValueError("a census margin must be nonnegative")
    return math.floor((1 + margin) * scale)


def reachable_extent(filled: MassGrid) -> tuple[int, Fraction]:
    """The number of reachable cells and the least mass any of them carries.

    The minimum is the sweep's own decision value, recomputed here from the same
    array, so a census that disagreed with the retained ``least_cell_mass`` would say
    so rather than quietly report a distribution of something else.
    """

    count = 0
    best: int | None = None
    for i, j0, j1 in filled.reduction.spans:
        column = filled.grid[i, j0 : j1 + 1]
        count += int(column.size)
        low = int(column.min())
        if best is None or low < best:
            best = low
    if best is None:  # pragma: no cover - reduce_to_spans raises on an empty domain
        raise ValueError("the sweep produced no reachable cell")
    return count, Fraction(best, filled.scale)


def tight_cells(filled: MassGrid, threshold: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Row indices, column indices and scaled masses of the cells at or below ``threshold``.

    The triple comes back in lexicographic ``(i, j)`` order, which is what the
    component count relies on, and masking it by a smaller threshold preserves that
    order -- so one pass at the widest margin serves every narrower one.
    """

    rows: list[np.ndarray] = []
    columns: list[np.ndarray] = []
    masses: list[np.ndarray] = []
    for i, j0, j1 in filled.reduction.spans:
        column = filled.grid[i, j0 : j1 + 1]
        offsets = np.flatnonzero(column <= threshold)
        if offsets.size:
            rows.append(np.full(offsets.size, i, dtype=np.intp))
            columns.append(offsets.astype(np.intp) + j0)
            masses.append(column[offsets])
    if not rows:
        empty = np.empty(0, dtype=np.intp)
        return empty, empty.copy(), np.empty(0, dtype=np.int64)
    return np.concatenate(rows), np.concatenate(columns), np.concatenate(masses)


Runs = tuple[list[int], list[int], list[int], list[int]]


def _runs(rows: np.ndarray, columns: np.ndarray) -> Runs:
    """Maximal runs of column-adjacent cells: their row, low, high and size."""

    total = int(rows.size)
    same_row = rows[1:] == rows[:-1]
    adjacent = columns[1:] == columns[:-1] + 1
    breaks = np.flatnonzero(~(same_row & adjacent)) + 1
    starts = np.concatenate((np.zeros(1, dtype=np.intp), breaks))
    ends = np.concatenate((breaks, np.array([total], dtype=np.intp)))
    return (
        rows[starts].tolist(),
        columns[starts].tolist(),
        columns[ends - 1].tolist(),
        (ends - starts).tolist(),
    )


def components(rows: np.ndarray, columns: np.ndarray) -> tuple[int, int]:
    """Edge-connected components of a cell set, and the largest one's cell count.

    Two event cells are joined when they share an edge, which in index space is a
    step of one in exactly one coordinate. Counting components is how the reading
    "a few hundred cells clustered around a few dozen positions" is decided: cells
    measure the census, components measure the clustering.

    Runs of adjacent cells within a column are merged first and the union-find then
    runs over runs, so the cost follows the tight set's shape rather than its size.
    """

    if rows.size == 0:
        return 0, 0
    run_row, run_low, run_high, run_size = _runs(rows, columns)
    count = len(run_row)
    parent = list(range(count))

    def find(node: int) -> int:
        root = node
        while parent[root] != root:
            root = parent[root]
        while parent[node] != root:
            parent[node], node = root, parent[node]
        return root

    previous_row: int | None = None
    previous_span = (0, 0)
    index = 0
    while index < count:
        row = run_row[index]
        stop = index
        while stop < count and run_row[stop] == row:
            stop += 1
        if previous_row is not None and previous_row + 1 == row:
            left, right = previous_span[0], index
            while left < previous_span[1] and right < stop:
                if run_high[left] < run_low[right]:
                    left += 1
                elif run_high[right] < run_low[left]:
                    right += 1
                else:
                    a, b = find(left), find(right)
                    if a != b:
                        parent[b] = a
                    if run_high[left] < run_high[right]:
                        left += 1
                    else:
                        right += 1
        previous_row, previous_span, index = row, (index, stop), stop

    sizes: dict[int, int] = {}
    for run in range(count):
        root = find(run)
        sizes[root] = sizes.get(root, 0) + run_size[run]
    return len(sizes), max(sizes.values())


def _extents(filled: MassGrid) -> tuple[np.ndarray, np.ndarray]:
    """Cell widths and heights in the rotated frame, as floats, for the area diagnostic."""

    u = np.array([float(value) for value in filled.reduction.u_events])
    v = np.array([float(value) for value in filled.reduction.v_events])
    return np.diff(u), np.diff(v)


def census_direction(
    atoms: tuple[Atom, ...],
    direction: Direction,
    outer_side: Fraction,
    square_side: Fraction,
    scale: int,
    *,
    margins: Sequence[Fraction],
    index: int,
    half_tangent: Fraction,
) -> DirectionCensus:
    """The near-tight census in one direction, at every margin, from one grid fill."""

    if not margins:
        raise ValueError("a census needs at least one margin")
    filled = scaled_mass_grid(atoms, direction, outer_side, square_side, scale)
    reachable, minimum = reachable_extent(filled)
    widths, heights = _extents(filled)
    approx_reachable = float(
        sum(widths[i] * heights[j0 : j1 + 1].sum() for i, j0, j1 in filled.reduction.spans)
    )

    ordered = sorted(margins)
    rows, columns, masses = tight_cells(filled, scaled_threshold(ordered[-1], scale))
    readings: list[MarginCensus] = []
    for margin in ordered:
        threshold = scaled_threshold(margin, scale)
        keep = masses <= threshold
        selected_rows, selected_columns = rows[keep], columns[keep]
        component_count, largest = components(selected_rows, selected_columns)
        box = None
        if selected_rows.size:
            box = Box(
                filled.reduction.u_events[int(selected_rows.min())],
                filled.reduction.u_events[int(selected_rows.max()) + 1],
                filled.reduction.v_events[int(selected_columns.min())],
                filled.reduction.v_events[int(selected_columns.max()) + 1],
            )
        readings.append(
            MarginCensus(
                margin=margin,
                tight_cells=int(selected_rows.size),
                components=component_count,
                largest_component=largest,
                approx_tight_area=float(
                    np.sum(widths[selected_rows] * heights[selected_columns])
                ),
                box=box,
            )
        )
    domain = centre_domain(outer_side, square_side, direction)
    return DirectionCensus(
        index=index,
        half_tangent=half_tangent,
        columns=len(filled.reduction.spans),
        reachable_cells=reachable,
        minimum_mass=minimum,
        approx_reachable_area=approx_reachable,
        domain_box=Box(
            min(u for u, _ in domain),
            max(u for u, _ in domain),
            min(v for _, v in domain),
            max(v for _, v in domain),
        ),
        margins=tuple(readings),
    )


def census(
    certificate: Certificate,
    margins: Sequence[Fraction] = DEFAULT_MARGINS,
    *,
    indices: Sequence[int] | None = None,
    on_direction: Callable[[DirectionCensus], None] | None = None,
) -> list[DirectionCensus]:
    """The census over a certificate's whole direction net, or a named subset.

    ``on_direction`` is called with each completed ``DirectionCensus`` as it lands,
    which is how the command writes its report one direction at a time.
    """

    scale = weight_scale(certificate.atoms)
    directions = certificate.directions
    wanted = range(len(directions)) if indices is None else indices
    readings: list[DirectionCensus] = []
    for index in wanted:
        if not 0 <= index < len(directions):
            raise ValueError(f"direction index {index} is outside the net")
        reading = census_direction(
            certificate.atoms,
            directions[index],
            certificate.outer_side,
            certificate.square_side,
            scale,
            margins=margins,
            index=index,
            half_tangent=certificate.half_tangents[index],
        )
        readings.append(reading)
        if on_direction is not None:
            on_direction(reading)
    return readings


def _box_record(box: Box | None) -> dict[str, object] | None:
    if box is None:
        return None
    return {
        "u_low": str(box.u_low),
        "u_high": str(box.u_high),
        "v_low": str(box.v_low),
        "v_high": str(box.v_high),
        "approx": [
            float(box.u_low),
            float(box.u_high),
            float(box.v_low),
            float(box.v_high),
        ],
    }


def _direction_record(reading: DirectionCensus) -> dict[str, object]:
    return {
        "index": reading.index,
        "half_tangent": str(reading.half_tangent),
        "columns": reading.columns,
        "reachable_cells": reading.reachable_cells,
        "minimum_mass": str(reading.minimum_mass),
        "approx_reachable_area": reading.approx_reachable_area,
        "domain_box": _box_record(reading.domain_box),
        "margins": [
            {
                "margin": str(margin.margin),
                "tight_cells": margin.tight_cells,
                "components": margin.components,
                "largest_component": margin.largest_component,
                "approx_tight_area": margin.approx_tight_area,
                "box": _box_record(margin.box),
            }
            for margin in reading.margins
        ],
    }


def totals(
    readings: Sequence[DirectionCensus],
    margins: Sequence[Fraction],
    declared_least_cell_mass: Fraction | None,
) -> dict[str, object]:
    """The block the reading is taken from: the census summed over the directions."""

    reachable = sum(reading.reachable_cells for reading in readings)
    area = sum(reading.approx_reachable_area for reading in readings)
    minimum = min((reading.minimum_mass for reading in readings), default=None)
    by_margin: list[dict[str, object]] = []
    for position, margin in enumerate(sorted(margins)):
        tight = sum(reading.margins[position].tight_cells for reading in readings)
        tight_area = sum(reading.margins[position].approx_tight_area for reading in readings)
        by_margin.append(
            {
                "margin": str(margin),
                "tight_cells": tight,
                "fraction_of_reachable": str(Fraction(tight, reachable)) if reachable else None,
                "approx_fraction_of_reachable": tight / reachable if reachable else None,
                "approx_area_fraction": tight_area / area if area else None,
                "components": sum(reading.margins[position].components for reading in readings),
                "max_components_in_a_direction": max(
                    (reading.margins[position].components for reading in readings), default=0
                ),
                "max_tight_cells_in_a_direction": max(
                    (reading.margins[position].tight_cells for reading in readings), default=0
                ),
                "max_largest_component": max(
                    (reading.margins[position].largest_component for reading in readings),
                    default=0,
                ),
            }
        )
    return {
        "directions_censused": len(readings),
        "reachable_cells": reachable,
        "approx_reachable_area": area,
        "minimum_mass": None if minimum is None else str(minimum),
        "approx_minimum_mass": None if minimum is None else float(minimum),
        "matches_declared_least_cell_mass": (
            None
            if minimum is None or declared_least_cell_mass is None
            else minimum == declared_least_cell_mass
        ),
        "by_margin": by_margin,
    }


def report(
    path: Path,
    certificate: Certificate,
    record: dict[str, object],
    *,
    digest: str,
    margins: Sequence[Fraction],
    readings: Sequence[DirectionCensus],
    complete: bool,
) -> dict[str, object]:
    """The whole report as a JSON-ready record, valid at every prefix of the run."""

    declared = record.get("least_cell_mass")
    declared_mass = Fraction(declared) if isinstance(declared, str) else None
    return {
        "tool": "devtools.census_tight_cells",
        "certificate": str(path.resolve().relative_to(REPO))
        if path.resolve().is_relative_to(REPO)
        else str(path),
        "sha256": digest,
        "id": record.get("id"),
        "n": certificate.n,
        "outer_side": str(certificate.outer_side),
        "square_side": str(certificate.square_side),
        "total_mass": str(certificate.total_mass),
        "declared_least_cell_mass": None if declared_mass is None else str(declared_mass),
        "atoms": len(certificate.atoms),
        "directions": len(certificate.half_tangents),
        "weight_scale": weight_scale(certificate.atoms),
        "margins": [str(margin) for margin in sorted(margins)],
        "margin_semantics": MARGIN_SEMANTICS,
        "complete": complete,
        "totals": totals(readings, margins, declared_mass),
        "by_direction": [_direction_record(reading) for reading in readings],
    }


def _parse_margins(text: str) -> tuple[Fraction, ...]:
    values = sorted({Fraction(part.strip()) for part in text.split(",") if part.strip()})
    if not values:
        raise ValueError("no margins given")
    if values[0] < 0:
        raise ValueError("a census margin must be nonnegative")
    return tuple(values)


def _parse_indices(text: str) -> tuple[int, ...]:
    return tuple(int(part.strip()) for part in text.split(",") if part.strip())


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("certificate", type=Path, help="the certificate JSON to census")
    parser.add_argument("--output", type=Path, help="write the report after every direction")
    parser.add_argument(
        "--margins",
        default=",".join(str(margin) for margin in DEFAULT_MARGINS),
        help="comma-separated census margins, as exact rationals",
    )
    parser.add_argument(
        "--directions",
        help="comma-separated direction indices; the whole net by default",
    )
    parser.add_argument("--quiet", action="store_true", help="suppress the per-direction line")
    args = parser.parse_args(argv)

    path: Path = args.certificate
    try:
        margins = _parse_margins(args.margins)
        indices = None if args.directions is None else _parse_indices(args.directions)
    except ValueError as error:
        print(f"{path}: {error}", file=sys.stderr)
        return 2
    certificate, record = load(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    readings: list[DirectionCensus] = []

    def write(*, complete: bool) -> None:
        if args.output is None:
            return
        payload = report(
            path,
            certificate,
            record,
            digest=digest,
            margins=margins,
            readings=readings,
            complete=complete,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=1) + "\n")

    def landed(reading: DirectionCensus) -> None:
        readings.append(reading)
        write(complete=False)
        if not args.quiet:
            counts = " ".join(
                f"{margin.margin}:{margin.tight_cells}/{margin.components}"
                for margin in reading.margins
            )
            print(
                f"direction {reading.index:3d} t={reading.half_tangent} "
                f"reachable {reading.reachable_cells:9d} min {reading.minimum_mass} "
                f"[margin:cells/components] {counts}",
                flush=True,
            )

    _ = census(certificate, margins, indices=indices, on_direction=landed)
    write(complete=True)
    reachable = sum(reading.reachable_cells for reading in readings)
    print(f"{path}: {len(readings)} directions, {reachable} reachable cells")
    for position, margin in enumerate(margins):
        tight = sum(reading.margins[position].tight_cells for reading in readings)
        pieces = sum(reading.margins[position].components for reading in readings)
        share = float(Fraction(tight, reachable)) if reachable else 0.0
        print(
            f"  margin {margin}: {tight} cells "
            f"({share:.6f} of reachable) in {pieces} components"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
