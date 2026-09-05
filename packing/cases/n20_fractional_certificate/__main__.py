"""Replay the retained n = 20 certificate and report every condition.

Exits non-zero if any condition fails, so the replay is a gate and not a
report. Run as ``python -m cases.n20_fractional_certificate``.
"""

from __future__ import annotations

import sys
from pathlib import Path

from cases.n20_fractional_certificate.replay import CERTIFICATE_PATH, snapshot
from sqpack.fractional.certificate import least_size_certified, verify


def replay(path: Path) -> int:
    certificate, record, source_bytes = snapshot(path)
    verdict = verify(certificate)
    try:
        unchanged = path.read_bytes() == source_bytes
    except OSError:
        unchanged = False
    if not unchanged:
        print("REFUSED: the retained certificate changed during replay")
        return 1
    print(f"claim: {record['claim']}")
    print(f"  n = {certificate.n}, L = {certificate.outer_side}, B = {certificate.square_side}")
    print(f"  {len(certificate.atoms)} atoms, total mass {certificate.total_mass}")
    for condition in verdict.conditions:
        mark = "PASS" if condition.holds else "FAIL"
        print(f"  {mark}  {condition.name} | {condition.detail}")
    if not verdict.accepted:
        print(f"REFUSED: {', '.join(verdict.failures)}")
        return 1
    expected_claim = f"s({certificate.n}) >= {certificate.bounded_side}"
    if record["claim"] != expected_claim:
        print("REFUSED: the retained claim disagrees with the replay")
        return 1
    if str(certificate.total_mass) != record["total_mass"]:
        print("REFUSED: the retained total mass disagrees with the replay")
        return 1
    if str(verdict.minimum_cell_mass) != record["least_cell_mass"]:
        print("REFUSED: the retained least cell mass disagrees with the replay")
        return 1
    least = least_size_certified(certificate.total_mass)
    print(f"VERIFIED: s(m) >= {certificate.bounded_side} for every m >= {least}")
    return 0


def main(argv: list[str] | None = None) -> int:
    """The retained certificate must replay; a named rung replays in its place.

    The package retains more than one rung -- the top at ``certificate.json`` and the
    superseded sides beside it -- and a rung whose evidence entry names it has to be
    replayable by that name rather than only through whichever file is currently the
    top. An argument is that name; without one the top rung replays, which is what
    every existing caller and every declared command does.
    """
    arguments = sys.argv[1:] if argv is None else argv
    if not arguments:
        return replay(CERTIFICATE_PATH)
    if len(arguments) > 1:
        print("REFUSED: replay takes at most one certificate path")
        return 1
    path = Path(arguments[0])
    if not path.is_file():
        print(f"REFUSED: no certificate at {path}")
        return 1
    return replay(path)


if __name__ == "__main__":
    raise SystemExit(main())
