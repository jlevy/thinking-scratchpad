"""Load the retained n = 20 certificate and hand it to the exact verifier.

Three certificates are retained. The top, ``certificate.json``, sits at container
side 97/20 with total mass 19848723/1000000; ``certificate-193-40.json`` is the
lower rung the same ladder froze at 193/40, and ``certificate-24-5.json`` is the
24/5 certificate that was the top until 2026-09-05. Their atoms carry more than one
registered case each: only Condition 2 mentions n among the five conditions, so a set
of total mass M certifies its side for every integer strictly above M. The top rung's
mass lies in [19, 20), so it certifies n = 20 and n = 21 and says nothing about
n = 19, where the 24/5 rung's mass of 946131/50000 still gives the register its
bound; from n = 22 on the register already holds 5, so every rung is true there and
weaker.

The JSON carries exact rationals as strings, so a replay reconstructs the same
object the generator proposed.
Nothing here decides anything: the verdict comes from
`sqpack.fractional.certificate.verify`, and this module only feeds it.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

from sqpack.fractional.certificate import Certificate
from sqpack.fractional.model import Atom

CERTIFICATE_PATH = Path(__file__).with_name("certificate.json")
#: The rung that was the top until 2026-09-05, and the only one of the three whose
#: mass reaches below nineteen. It is what keeps n = 19 at 24/5 now that the pointer
#: above has moved to a heavier set, so it is named rather than globbed for.
RUNG_24_5_PATH = Path(__file__).with_name("certificate-24-5.json")
#: The lower rung the same ladder froze at 193/40, retained as the ladder's evidence.
RUNG_193_40_PATH = Path(__file__).with_name("certificate-193-40.json")


def _from_record(record: dict) -> Certificate:
    limit = Fraction(record["angle_limit"])
    steps = int(record["direction_steps"])
    return Certificate(
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


def snapshot(path: Path = CERTIFICATE_PATH) -> tuple[Certificate, dict[str, str], bytes]:
    """Parse one byte snapshot into the certificate and its declarations."""

    data = path.read_bytes()
    record = json.loads(data)
    declarations = {key: str(record[key]) for key in ("claim", "total_mass", "least_cell_mass")}
    return _from_record(record), declarations, data


def load(path: Path = CERTIFICATE_PATH) -> Certificate:
    """Rebuild the retained certificate exactly as it was accepted."""

    return snapshot(path)[0]


def declared(path: Path = CERTIFICATE_PATH) -> dict[str, str]:
    """What the record claims, for a replay to compare against."""

    return snapshot(path)[1]
