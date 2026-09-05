#!/usr/bin/env python3
"""Drive the packing-side cutting-plane loop at one side and record what it cost.

`sqpack.fractional.cutting` is the loop; this is the command that runs it with
its parameters on the line and a per-iteration table on stdout, so that a
depth-scaled total in the record can be reproduced from a command rather than
from a script that was not kept. It writes a state file every iteration, which
a later run at the same or a larger side warm-starts from with ``--warm``.

Nothing here decides a bound. A family whose exact depth is at most 1 is
scaled and verified in memory by ``verify_ceiling``; ``--freeze`` writes the
best scaled family's bytes, and retention is the coordinator's decision on
those bytes, never on this run's word.

Usage:
    uv run --frozen python -m devtools.run_fractional_cutting --n 11 --side 191/50 \
        --minutes 45 --log run.log --state state-191-50.json --json summary.json
    uv run --frozen python -m devtools.run_fractional_cutting --n 11 --side 77/20 \
        --warm state-191-50.json --minutes 40 --state state-77-20.json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from fractions import Fraction
from pathlib import Path
from typing import TextIO

from sqpack.fractional.ceiling import verify_ceiling
from sqpack.fractional.colgen import Rows
from sqpack.fractional.cutting import (
    cutting_plane_loop,
    family_record,
    initial_sites,
    iteration_table,
    load_state,
    rows_from_exact,
    warm_start,
)
from sqpack.fractional.generate import net_half_tangents

ANGLE_LIMIT = Fraction(207107, 500000)
DIRECTION_STEPS = 180
SHRINK = Fraction(9977, 10000)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").split("\n\n")[0])
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--side", type=Fraction, required=True, help="container side L")
    parser.add_argument("--shrink", type=Fraction, default=SHRINK)
    parser.add_argument("--angle-limit", type=Fraction, default=ANGLE_LIMIT)
    parser.add_argument("--steps", type=int, default=DIRECTION_STEPS)
    parser.add_argument(
        "--grids", type=str, default=None, help="site grid counts, e.g. 25,34,41"
    )
    parser.add_argument("--minutes", type=float, default=30.0, help="wall budget")
    parser.add_argument("--iterations", type=int, default=40)
    parser.add_argument("--cap", type=int, default=120, help="site orbits added per iteration")
    parser.add_argument("--support-cap", type=int, default=96)
    parser.add_argument("--rows-rounds", type=int, default=8)
    parser.add_argument("--rows-per-direction", type=int, default=3)
    parser.add_argument("--warm", type=Path, default=None, help="state file to warm-start from")
    parser.add_argument("--log", type=Path, default=None)
    parser.add_argument("--state", type=Path, default=None)
    parser.add_argument("--freeze", type=Path, default=None, help="write the best family here")
    parser.add_argument("--json", type=Path, default=None, help="write the run summary here")
    args = parser.parse_args(argv)

    half_tangents = net_half_tangents(args.angle_limit, args.steps)
    grids = tuple(int(c) for c in args.grids.split(",")) if args.grids else None
    if args.warm is not None:
        old_side, points, carried = load_state(args.warm)
        sites, exact_rows = warm_start(
            points,
            carried,
            old_side=old_side,
            new_side=args.side,
            square_side=args.shrink,
            half_tangents=half_tangents,
            grid_counts=grids,
        )
        rows = rows_from_exact(exact_rows, sites, half_tangents, args.shrink)
        origin = (
            f"warm from {args.warm} at side {old_side}: "
            f"{len(points)} sites, {len(carried)} rows"
        )
    else:
        sites = initial_sites(args.side, args.shrink, grid_counts=grids)
        rows = Rows()
        exact_rows = []
        origin = "grid seed"
    settings = {
        "n": args.n,
        "outer_side": str(args.side),
        "square_side": str(args.shrink),
        "angle_limit": str(args.angle_limit),
        "direction_steps": args.steps,
        "grids": list(grids) if grids else None,
        "minutes": args.minutes,
        "iterations": args.iterations,
        "cap": args.cap,
        "support_cap": args.support_cap,
        "rows_rounds": args.rows_rounds,
        "rows_per_direction": args.rows_per_direction,
        "origin": origin,
        "initial_sites": sites.size,
        "initial_orbits": len(sites.orbits),
        "initial_rows": len(rows),
    }
    print(json.dumps(settings, indent=1), flush=True)
    # Printing the loop's progress is this tool's interface, so the tool owns the
    # terminal: `cutting_plane_loop` writes to the sinks it is handed and to nothing
    # else. `sys.stdout` is always one of them -- a run of this length is watched
    # while it happens -- and `--log` adds the file alongside it.
    handle = args.log.open("a") if args.log is not None else None
    sinks: tuple[TextIO, ...] = (sys.stdout,) if handle is None else (sys.stdout, handle)
    started = time.perf_counter()
    try:
        log = cutting_plane_loop(
            args.n,
            args.side,
            args.shrink,
            half_tangents,
            sites=sites,
            rows=rows,
            exact_rows=exact_rows,
            support_cap=args.support_cap,
            cap=args.cap,
            max_iterations=args.iterations,
            deadline=started + 60.0 * args.minutes,
            rows_max_rounds=args.rows_rounds,
            rows_per_direction=args.rows_per_direction,
            log_sinks=sinks,
            state_path=args.state,
        )
    finally:
        if handle is not None:
            handle.close()
    seconds = time.perf_counter() - started

    frozen = None
    verdict = log.verdict
    if log.best_family is not None and args.freeze is not None:
        if verdict is None or log.best_iteration != len(log.iterations) - 1:
            verdict = verify_ceiling(log.best_family)
        provenance = {
            "tool": "devtools.run_fractional_cutting",
            "settings": settings,
            "best_iteration": log.best_iteration,
            "stopped": log.stopped,
            "verify_ceiling": {
                "proved": verdict.proved,
                "failures": list(verdict.failures),
                "max_depth": str(verdict.max_depth),
                "vertices": verdict.vertices,
                "decided_exactly": verdict.decided_exactly,
                "regime": verdict.regime,
                "symmetric_only": verdict.symmetric_only,
                "statement": verdict.statement,
            },
        }
        args.freeze.parent.mkdir(parents=True, exist_ok=True)
        args.freeze.write_text(
            json.dumps(family_record(log.best_family, provenance), indent=1) + "\n"
        )
        frozen = str(args.freeze)
    summary = {
        "settings": settings,
        "seconds": seconds,
        "stopped": log.stopped,
        "best_scaled_total": str(log.best_scaled_total),
        "best_scaled_total_float": float(log.best_scaled_total),
        "best_iteration": log.best_iteration,
        "verdict": None
        if verdict is None
        else {
            "proved": verdict.proved,
            "failures": list(verdict.failures),
            "total_weight": str(verdict.total_weight),
            "max_depth": str(verdict.max_depth),
            "vertices": verdict.vertices,
            "decided_exactly": verdict.decided_exactly,
        },
        "iterations": [entry.as_dict() for entry in log.iterations],
        "frozen": frozen,
    }
    print(f"stopped: {log.stopped}")
    print(
        f"best scaled total {log.best_scaled_total} = {float(log.best_scaled_total):.6f} "
        f"at iteration {log.best_iteration}; {seconds:.0f} s"
    )
    if verdict is not None:
        print(f"verify_ceiling: proved={verdict.proved} failures={verdict.failures}")
    print(iteration_table(log.iterations))
    if args.json is not None:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(summary, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
