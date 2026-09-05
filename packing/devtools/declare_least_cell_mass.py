"""Fill a frozen candidate's ``least_cell_mass`` declaration with a one-worker sweep.

A candidate frozen by `devtools.run_fractional_colgen` or `devtools.colgen_checkpoint`
without ``--verify-serial`` carries ``"least_cell_mass": null``: a declaration no run
has computed. `devtools.decide_certificate` refuses a null declaration at parse, so
such a candidate cannot be decided until the number is declared -- by a sweep the gate
then repeats on the frozen bytes and compares against both of its routes. This tool
makes that declaration and nothing else.

It runs `sqpack.fractional.certificate.verify` with exactly one worker, because a lane
holding one core never starts the pool (the fourth core is the gate's), rewrites the
record with the sweep's least cell mass, and prints the in-memory verdict for the
operator. It does not decide: an in-memory verdict is not evidence about any file
(D-433, D-441), and the retention boundary stays freeze-then-decide through the gate.
A candidate the sweep does not accept is left untouched and the exit code says so.
"""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path

from sqpack.fractional.certificate import Certificate, verify
from sqpack.fractional.model import Atom


def load_candidate(path: Path) -> tuple[Certificate, dict[str, object]]:
    """The candidate and its record, in the shape ``cases/*/replay.py`` reads."""

    record = json.loads(path.read_text())
    limit = Fraction(record["angle_limit"])
    steps = int(record["direction_steps"])
    certificate = Certificate(
        n=int(record["n"]),
        outer_side=Fraction(record["outer_side"]),
        square_side=Fraction(record["square_side"]),
        atoms=tuple(
            Atom(f"{index:04d}", Fraction(x), Fraction(y), Fraction(weight))
            for index, (x, y, weight) in enumerate(record["atoms"])
        ),
        half_tangents=tuple(limit * k / steps for k in range(steps + 1)),
        symmetry=record["symmetry"],
    )
    return certificate, record


def declare(path: Path, *, overwrite: bool = False) -> tuple[bool, str]:
    """Sweep with one worker and write the declaration; ``(accepted, detail)``.

    Refuses to touch a record that already declares a value unless ``overwrite``
    is given, so a retained file is never rewritten by accident.
    """

    certificate, record = load_candidate(path)
    if record.get("least_cell_mass") is not None and not overwrite:
        return False, f"{path} already declares least_cell_mass {record['least_cell_mass']}"
    verdict = verify(certificate, workers=1)
    detail = (
        f"one-worker sweep: accepted={verdict.accepted} failures={verdict.failures} "
        f"least cell mass {verdict.minimum_cell_mass}"
    )
    if not verdict.accepted or verdict.minimum_cell_mass is None:
        return False, detail
    record["least_cell_mass"] = str(verdict.minimum_cell_mass)
    path.write_text(json.dumps(record, indent=1) + "\n")
    return True, detail


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--overwrite", action="store_true", help="replace an existing value")
    args = parser.parse_args(argv)
    failed = 0
    for path in args.paths:
        accepted, detail = declare(path, overwrite=args.overwrite)
        print(f"{path}: {detail}", flush=True)
        failed += not accepted
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
