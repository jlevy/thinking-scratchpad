#!/usr/bin/env python3
"""Recompute every mass, atom count, and margin a result's prose quotes, from the certificate.

`D-439`: three durable-record statements described "the top rung" and were left behind
when the ladder advanced past them. Two were in `T-019`: the significance rationale gave
the movement past Massaccesi as `0.0042`, the value of the *first* rung this result
reached (`451/100`) rather than the retained one (`229/50`), whose movement is `0.0742`;
and `next_rung` quoted `451/100`'s own total and margin -- `16.5936` and `0.406` -- as
though they belonged to the retained certificate, whose actual total is
`3393147/200000 = 16.965735` with margin `0.034265`, an order of magnitude smaller. Every
figure in both sentences was exact and real; each was simply about the wrong file. No
existing check re-derives a result's quoted figures from the artifact it names, so nothing
caught either until a line-by-line read did, six hours after the ladder moved
(`docs/project/reviews/review-2026-09-04-t018-thirdparty-package.md` ran twenty-one
attacks and missed its instance, because the sentence was true when it read it).

This is that detector. For every result in `frontier/results.yaml`, it resolves the
weighted fractional certificates the result names, sums each one's atoms in exact
`Fraction` arithmetic (never trusting the file's own stored `total_mass` -- that field is
cross-checked here too, not assumed), and checks two things against the recomputation:

1. **Fraction-equals-decimal.** Any `a/b = d.ddd` in the text -- not only in a result's
   prose, but repository-wide, across `results.yaml`, `evidence.yaml` and `defects.yaml`
   -- must be arithmetically true to the precision written. Mechanical and unambiguous:
   there is no reading of `a/b = d.ddd` where the two sides may differ.
2. **Quoted artifact figures.** Where a result's prose states a total mass, atom count, or
   margin that is anchored to one of *that result's own* named artifacts -- either
   explicitly, by an adjoining rung side (`229/50`, `451/100`, ...), or implicitly, by
   naming no rung at all, which this repository's prose uses to mean the retained
   (`certificate.json`) rung -- the figure must match what that artifact's own atoms give.
   A rung mentioned in passing that is not one of the result's own artifacts (T-019's own
   next_rung cites n = 12's ladder for contrast) is left unchecked rather than guessed at:
   a check that cries wolf on a cross-reference is worse than one that says nothing.

Three narrower checks answer `D-442`, whose residual audit found three more durable
statements about a rung that had since moved, none of them arithmetically wrong:

3. **Ladder length.** `T-017`'s rationale still called its ladder seven rungs after the
   generator retained an eighth. A `"<count>-rung ladder"`, `"<count> rungs are retained
   below it"`, or `"<count> rungs are retained"` phrase is counted against the
   certificate artifacts the result itself declares.
4. **Runway.** `T-017`'s `next_rung` measured the room left under the method's ceiling at
   `79/20`, the rung one below the retained one; the figure was exactly right for the
   file it named. Runway is a property of the top rung, so a runway phrase naming a
   historical rung is refused whatever its arithmetic, and the figure itself is checked
   against `ceil(sqrt(n)) * B - L` recomputed from the certificate's own bytes.
5. **Superseded-by.** `T-015` and `T-016` both said they were superseded by `T-019`
   "which certifies `451/100`" -- a real certificate of `T-019`'s, and one it had already
   climbed past. Only a fraction that is one of the *named* result's own rungs is checked,
   and it must be that result's live `certificate.json` side.

A fourth, narrower check catches the specific shape of D-439's first bug: a result whose
`claim` names exactly two `a/b = d.ddd` figures (the retained side and a displaced prior
value -- every other current result names zero or one) states its own movement between
them somewhere in its prose. Both orderings of the subtraction are accepted, so the check
never depends on an assumption about which side is written first; it only ever fires where
the arithmetic disagrees with both.

Underneath all of them is one requirement, and it is a refusal rather than a fallback: a
result declaring any certificate declares exactly one live `certificate.json`. Unqualified
prose -- "the retained certificate's total", "0.0308 of runway left" -- means that file
and nothing else, so a missing pointer is reported with the path it should be at. Electing
a historical rung in its place would be worse than useless: the immutable file agrees with
the sentence that went stale when the ladder left it, and every figure would pass.

What this does **not** cover: D-439's third instance was a third-party package's claim
that one file is byte-identical to another, checked by a printed SHA-256. That is a claim
about file identity, not a quoted mass, atom count, or margin, and nothing here reads or
compares file hashes. See the module's own test suite for how each instance was checked
against this tool, and the accompanying report for which it catches.

Usage, from `packing/`:
    uv run --frozen --all-extras --group dev python -m devtools.check_rung_figures
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, localcontext
from fractions import Fraction
from pathlib import Path, PurePosixPath

from sqpack.yamlio import safe_load

ROOT = Path(__file__).resolve().parent.parent
# The repository root; artifact and record paths in results.yaml are repository-relative.
REPO = ROOT.parent
RESULTS = ROOT / "frontier" / "results.yaml"
EVIDENCE = ROOT / "frontier" / "evidence.yaml"
DEFECTS = ROOT / "defects.yaml"

#: The result fields this repository's prose puts numeric claims in. Named directly in
#: the defect this module answers and in the task that specified it.
PROSE_FIELDS = ("claim", "significance.rationale", "next_rung", "composition")

#: The moving top-rung pointer's basename. A suffixed `certificate-A-B.json` beside it is
#: an immutable historical rung, and the two are never interchangeable here.
LIVE_CERTIFICATE = "certificate.json"

#: Enough significant figures for any fraction this register carries (the largest
#: denominators seen are in the low millions) with wide headroom; matches the pattern
#: `check_nagamochi_bounds.py` already uses for the same reason.
_DECIMAL_PRECISION = 60

#: `a/b = d.ddd`, anywhere in a text. Bounded on both sides so it cannot match as a
#: sub-token of a larger number (`(?<![\w.])` before the numerator, `(?!\d)` after the
#: decimal's last digit).
_FRACTION_EQUALS_DECIMAL = re.compile(r"(?<![\w.])(\d+)/(\d+)\s*=\s*(-?\d+\.\d+)(?!\d)")

#: Any bare `a/b` token, used to find rung-side references near a candidate figure.
_SIDE_TOKEN = re.compile(r"(\d+)/(\d+)")

#: Sentence boundaries within one folded YAML prose field: a period followed by
#: whitespace, where what precedes it is not itself part of a decimal number and what
#: follows starts a new capitalised sentence. This deliberately does not split inside
#: `16.965735,` or after a mid-sentence abbreviation like `T-002)`.
_SENTENCE_BOUNDARY = re.compile(r"(?<=[a-z0-9)])\.\s+(?=[A-Z])")

#: "The movement is +0.0742" (or "-0.0742", or unsigned).
_MOVEMENT_IS = re.compile(r"\bmovement\s+is\s+([+-]?\d+\.\d+)\b")


def _fraction(numerator: str, denominator: str) -> Fraction:
    return Fraction(int(numerator), int(denominator))


def round_to(value: Fraction, digits: int) -> Decimal:
    """Round an exact `Fraction` to `digits` decimal places, the way prose rounds a number."""
    quantum = Decimal(1).scaleb(-digits)
    with localcontext() as context:
        context.prec = _DECIMAL_PRECISION
        exact = Decimal(value.numerator) / Decimal(value.denominator)
        return exact.quantize(quantum, rounding=ROUND_HALF_UP)


def decimal_matches(value: Fraction, stated: str) -> bool:
    """Does `value` equal the decimal literal `stated`, at the precision `stated` writes?"""
    digits = len(stated.split(".", 1)[1]) if "." in stated else 0
    return round_to(value, digits) == Decimal(stated)


def sentences(text: str) -> list[str]:
    """Split one prose field into sentence-sized chunks for local figure/side anchoring."""
    return _SENTENCE_BOUNDARY.split(text)


def prose_fields(result: dict) -> dict[str, str]:
    """This result's four numeric-claim-bearing fields, by name, defaulting to empty."""
    significance = result.get("significance") or {}
    values = {
        "claim": result.get("claim", ""),
        "significance.rationale": significance.get("rationale", ""),
        "next_rung": result.get("next_rung", ""),
        "composition": result.get("composition") or "",
    }
    return {name: values[name] for name in PROSE_FIELDS}


@dataclass(frozen=True, slots=True)
class CertificateFigures:
    """A weighted fractional certificate's figures, recomputed from its own atom list.

    Deliberately independent of `sqpack.fractional.certificate.Certificate`: a checker
    that shared a code path with the thing it checks could not catch that code's own
    mistake, and the point here is a from-scratch recomputation from the rawest ground
    truth the artifact carries -- the atoms themselves, not the file's own summary line.
    """

    path: str
    """Repository-relative, for citing in a disagreement."""
    n: int
    outer_side: Fraction
    square_side: Fraction | None
    """`B`, the shrunken square side the certificate is stated for; None if the file does
    not carry one, in which case the ceiling and runway are simply not checked."""
    atom_count: int
    mass: Fraction
    stored_mass: Fraction | None
    """What `total_mass` says in the file itself, checked against `mass` but never used
    in place of it."""

    @property
    def margin(self) -> Fraction:
        return self.n - self.mass

    @property
    def ceiling(self) -> Fraction | None:
        """`ceil(sqrt(n)) * B`: the highest side any certificate on these bytes can reach.

        Recomputed here rather than imported from `sqpack.fractional.certificate`, for the
        same reason the mass is: a checker sharing a code path with the thing it checks
        cannot catch that code's own mistake.
        """
        if self.square_side is None:
            return None
        root = math.isqrt(self.n)
        order = root if root * root == self.n else root + 1
        return order * self.square_side

    @property
    def runway(self) -> Fraction | None:
        """How far this certificate's own side sits below that ceiling."""
        ceiling = self.ceiling
        return None if ceiling is None else ceiling - self.outer_side


#: The retained certificate (or None), a side -> certificate index, and every resolved
#: certificate, for one result.
_CertificateIndex = dict[Fraction, "CertificateFigures"]
_CertificateList = list["CertificateFigures"]
ResolvedCertificates = tuple["CertificateFigures | None", _CertificateIndex, _CertificateList]


def _repo_relative_path(artifact: str) -> Path | None:
    """Resolve a declared artifact path inside the repository, or None if it cannot be."""
    pure = PurePosixPath(artifact)
    if pure.is_absolute() or pure.as_posix() != artifact or ".." in pure.parts:
        return None
    target = (REPO / pure).resolve()
    try:
        target.relative_to(REPO.resolve())
    except ValueError:
        return None
    return target


def load_certificate(path: Path) -> CertificateFigures | None:
    """Recompute one artifact's figures, or None if it is not a weighted-certificate JSON.

    Most of a result's `artifacts` are generator or verifier modules, not certificates;
    returning None for those is the expected case; this only reports a positive when the
    file parses as JSON and carries the certificate's own distinctive shape.
    """
    if path.suffix != ".json" or not path.is_file():
        return None
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError, UnicodeDecodeError:
        return None
    if not isinstance(record, dict) or "outer_side" not in record or "atoms" not in record:
        return None
    atoms = record["atoms"]
    if not isinstance(atoms, list) or not atoms:
        return None
    try:
        n = int(record["n"])
        outer_side = Fraction(str(record["outer_side"]))
        mass = sum((Fraction(str(atom[2])) for atom in atoms), start=Fraction(0))
        stored_mass = Fraction(str(record["total_mass"])) if "total_mass" in record else None
        square_side = Fraction(str(record["square_side"])) if "square_side" in record else None
    except KeyError, ValueError, TypeError, IndexError, ZeroDivisionError:
        return None
    try:
        label = path.relative_to(REPO).as_posix()
    except ValueError:
        # Outside the repository: a synthetic fixture in a test's tmp_path, never a real
        # artifact. Fall back to the raw path rather than raising, so the function stays
        # total over any path it is handed.
        label = str(path)
    return CertificateFigures(
        path=label,
        n=n,
        outer_side=outer_side,
        square_side=square_side,
        atom_count=len(atoms),
        mass=mass,
        stored_mass=stored_mass,
    )


def live_pointers(resolved: list[CertificateFigures]) -> list[CertificateFigures]:
    """Every resolved artifact whose basename is the moving top-rung pointer."""
    return [c for c in resolved if Path(c.path).name == LIVE_CERTIFICATE]


def pick_retained(resolved: list[CertificateFigures]) -> CertificateFigures | None:
    """Which resolved certificate is "the retained certificate" prose without a side means.

    `certificate.json` by this repository's own naming convention (D-439's fix:
    `certificate.json` is the moving top-rung pointer, `certificate-A-B.json` an
    immutable historical rung) -- independent of declaration order, so a result listing
    its artifacts in some other sequence still resolves the right one as primary.

    There is deliberately no fallback to a historical rung. Electing one silently is the
    exact failure this module exists to catch: every unqualified figure in the result's
    prose would then be checked against an immutable file that is not the current one,
    and the wrong artifact would agree with the stale prose. `retained_pointer_problems`
    refuses the record instead.
    """
    pointers = live_pointers(resolved)
    return pointers[0] if len(pointers) == 1 else None


def retained_pointer_problems(
    result_id: str,
    resolved: list[CertificateFigures],
    pointers_declared_elsewhere: frozenset[str] = frozenset(),
) -> list[str]:
    """A certificate-bearing result resolves exactly one live `certificate.json`.

    Nothing else can stand in for it. A result that has lost its pointer -- renamed,
    dropped from the artifact list, or deleted -- is refused with the path the pointer
    should be at, and a result declaring two is refused as ambiguous rather than settled
    by declaration order.

    One exception, and it is the case the pointer's own name anticipates: the pointer
    moves. When a later result certifies a higher side in the same package, the earlier
    result's rung is renamed to `certificate-A-B.json` and the successor takes
    `certificate.json`, so the earlier result declares no live pointer and should not.
    Refusing it would force a superseded result to declare an artifact it did not
    produce and whose figures contradict its prose, which is the same failure this
    module exists to catch, one result over. So a result naming only historical rungs is
    accepted exactly when the live pointer beside them is declared by some other result:
    the pointer still exists, still has an owner, and the ownership is checkable rather
    than assumed. A pointer nothing declares is still a refusal.
    """
    if not resolved:
        return []
    pointers = live_pointers(resolved)
    if len(pointers) == 1:
        return []
    if not pointers:
        successors = {
            str(PurePosixPath(c.path).parent / LIVE_CERTIFICATE) for c in resolved
        } & pointers_declared_elsewhere
        if successors:
            return []
    declared = ", ".join(c.path for c in resolved)
    if not pointers:
        expected = ", ".join(
            sorted({str(PurePosixPath(c.path).parent / LIVE_CERTIFICATE) for c in resolved})
        )
        message = (
            f"{result_id}: no live {LIVE_CERTIFICATE} among its certificate artifacts "
            f"({declared}); expected {expected}"
        )
        return [message]
    paths = ", ".join(c.path for c in pointers)
    message = (
        f"{result_id}: declares {len(pointers)} live {LIVE_CERTIFICATE} pointers "
        f"({paths}); exactly one is required"
    )
    return [message]


def resolve_certificates(result: dict) -> ResolvedCertificates:
    """This result's own resolved certificates: the retained one, a side index, and all."""
    resolved = [
        figures
        for artifact in result.get("artifacts", [])
        if isinstance(artifact, str)
        and (path := _repo_relative_path(artifact)) is not None
        and (figures := load_certificate(path)) is not None
    ]
    retained = pick_retained(resolved)
    sides = {c.outer_side: c for c in resolved}
    return retained, sides, resolved


def certificate_consistency_problems(cert: CertificateFigures) -> list[str]:
    """The certificate's own stored `total_mass` must match its atoms, not just its prose."""
    if cert.stored_mass is None or cert.stored_mass == cert.mass:
        return []
    message = (
        f"{cert.path}: stored total_mass {cert.stored_mass} = {float(cert.stored_mass):g} "
        f"disagrees with the atom sum {cert.mass} = {float(cert.mass):g}"
    )
    return [message]


@dataclass(frozen=True, slots=True)
class QuotedFigure:
    """One candidate total-mass, margin, or atom-count claim found in a sentence."""

    kind: str
    """"total", "margin", or "atoms"."""
    text: str
    """The figure exactly as written, e.g. "16.5936" or "1121"."""
    side: Fraction | None
    """The rung side this specific pattern captured alongside the figure, if any."""
    span: tuple[int, int]
    """Character span of the whole match, so the side-token scan can exclude it."""


# Ten deliberately narrow, keyword-anchored patterns rather than one generic
# number-near-a-fraction rule: a bare decimal near a rung reference is often something
# else entirely (T-019's own next_rung sits a "the movement is +0.0742" a few words from
# "451/100" with no relation between them), so the keyword requirement is what keeps this
# from crying wolf. Under-matching a rewording is the safe failure; over-matching is not.
_TOTAL_IS = re.compile(r"\btotal(?:\s+mass)?\s+is\s+(?:\d+/\d+\s*=\s*)?(\d+\.\d+)\b")
_MARGIN_IS = re.compile(r"\bmargin\s+is\s+(\d+\.\d+)\b")
_LEAVING_BELOW = re.compile(r"\bleaving\s+(\d+\.\d+)\s+below\b")
_ATOMS_COUNT = re.compile(r"\b(\d[\d,]*)\s+atoms\b")
_MARGIN_AT_SIDE = re.compile(r"\bmargin\s+(\d+\.\d+)\s+at\s+(\d+)/(\d+)\b")
_MARGIN_BELOW_AT_SIDE_IS = re.compile(
    r"\bmargin\s+below\s+\w+\s+at\s+(\d+)/(\d+)\s+is\s+(?:already\s+)?(\d+\.\d+)"
)
_RUNG_HAS_TOTAL_AND_MARGIN = re.compile(
    r"\b(\d+)/(\d+)\s+rung\b.{0,60}?\bhas\s+total\s+(\d+\.\d+)\s+and\s+margin\s+(\d+\.\d+)",
    re.DOTALL,
)
#: "this certificate's 16.933080 reaching 17, 18 and 19" -- a total mass stated
#: possessively, with no "total" and no "is" anywhere near it. The six patterns above all
#: key on a noun or a verb this form omits, so a figure written this way was invisible to
#: every one of them and a stale one passed (PR 80's F27). The possessive itself is the
#: keyword here: only a certificate has a mass, so `certificate's DECIMAL reaching` is as
#: anchored as `total is DECIMAL` and no more likely to cry wolf.
_CERTIFICATE_REACH_MASS = re.compile(
    r"\b(?:this|the|retained)\s+certificate(?:'s|\u2019s)\s+(\d+\.\d+)\s+reaching\b"
)

# Runway -- how far a side sits below `ceil(sqrt(n)) * B` -- in the three shapes the
# register writes it. The first two name their rung and the third leans on the retained
# one, which is the same anchoring rule the margin patterns above use.
_RUNWAY_AT_SIDE = re.compile(r"\b(\d+)/(\d+)\s+(?:still\s+)?has\s+(\d+\.\d+)\s+of\s+runway\b")
_RUNWAY_ABOVE_SIDE = re.compile(
    r"\bleaving\s+(\d+\.\d+)\s+of\s+runway\s+above\s+(?:the\s+retained\s+)?(\d+)/(\d+)\b"
)
_RUNWAY_TO_CEILING = re.compile(r"\brunway\s+is\s+(\d+\.\d+)\s+to\s+the\s+ceiling\b")

#: Ladders are short and the register spells their lengths, so the vocabulary is bounded
#: rather than general: a thirteenth rung is a reword, and an unrecognised word is left
#: unchecked, which is this module's standing safe failure.
_RUNG_WORDS = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
}
#: `(?<![\w-])` rather than `\b`, so a hyphenated compound ("twenty-one") cannot be read
#: as its tail ("one").
_RUNG_COUNT_TOKEN = rf"(?<![\w-])(?:{'|'.join((*_RUNG_WORDS, r'\d+'))})"
_LADDER_LENGTH = re.compile(rf"({_RUNG_COUNT_TOKEN})-rung\s+ladder\b", re.IGNORECASE)
_RUNGS_BELOW_TOP = re.compile(
    rf"({_RUNG_COUNT_TOKEN})\s+rungs\s+are\s+retained\s+below\s+it\b", re.IGNORECASE
)
_RUNGS_RETAINED = re.compile(
    rf"({_RUNG_COUNT_TOKEN})\s+rungs?\s+(?:is|are)\s+retained\b(?!\s+below)", re.IGNORECASE
)

#: A sentence saying this result was superseded, and by which result. Split so that
#: "a mapped, non-superseded review artifact" and "It supersedes this result at n = 19",
#: neither of which names a superseding result, cannot reach the rung comparison.
_SUPERSEDED = re.compile(r"supersed", re.IGNORECASE)
_SUPERSEDING_RESULT = re.compile(r"\bby\s+(T-\d+)\b")


def _rung_count(token: str) -> int:
    """A ladder length written as digits or as one of the bounded English names above."""
    return int(token) if token.isdigit() else _RUNG_WORDS[token.lower()]


def _side_text(side: Fraction) -> str:
    return f"{side.numerator}/{side.denominator}"


def _rung_pair(sentence: str) -> list[QuotedFigure]:
    """The one pattern that yields two figures (total and margin) from one match."""
    found: list[QuotedFigure] = []
    for match in _RUNG_HAS_TOTAL_AND_MARGIN.finditer(sentence):
        side = _fraction(match.group(1), match.group(2))
        found.append(QuotedFigure("total", match.group(3), side, match.span()))
        found.append(QuotedFigure("margin", match.group(4), side, match.span()))
    return found


def _runway_figures(sentence: str) -> list[QuotedFigure]:
    """The three runway shapes, normalised onto one kind."""
    return (
        [
            QuotedFigure(
                "runway",
                match.group(3),
                _fraction(match.group(1), match.group(2)),
                match.span(),
            )
            for match in _RUNWAY_AT_SIDE.finditer(sentence)
        ]
        + [
            QuotedFigure(
                "runway",
                match.group(1),
                _fraction(match.group(2), match.group(3)),
                match.span(),
            )
            for match in _RUNWAY_ABOVE_SIDE.finditer(sentence)
        ]
        + [
            QuotedFigure("runway", match.group(1), None, match.span())
            for match in _RUNWAY_TO_CEILING.finditer(sentence)
        ]
    )


def quoted_figures(sentence: str) -> list[QuotedFigure]:
    """Every figure one of the ten anchored patterns recognises in `sentence`."""
    return (
        [
            QuotedFigure("total", match.group(1), None, match.span())
            for match in _TOTAL_IS.finditer(sentence)
        ]
        + [
            QuotedFigure("margin", match.group(1), None, match.span())
            for match in _MARGIN_IS.finditer(sentence)
        ]
        + [
            QuotedFigure("margin", match.group(1), None, match.span())
            for match in _LEAVING_BELOW.finditer(sentence)
        ]
        + [
            QuotedFigure("atoms", match.group(1), None, match.span())
            for match in _ATOMS_COUNT.finditer(sentence)
        ]
        + [
            QuotedFigure(
                "margin",
                match.group(1),
                _fraction(match.group(2), match.group(3)),
                match.span(),
            )
            for match in _MARGIN_AT_SIDE.finditer(sentence)
        ]
        + [
            QuotedFigure(
                "margin",
                match.group(3),
                _fraction(match.group(1), match.group(2)),
                match.span(),
            )
            for match in _MARGIN_BELOW_AT_SIDE_IS.finditer(sentence)
        ]
        + [
            QuotedFigure("total", match.group(1), None, match.span())
            for match in _CERTIFICATE_REACH_MASS.finditer(sentence)
        ]
        + _runway_figures(sentence)
        + _rung_pair(sentence)
    )


def resolve_target(
    figure: QuotedFigure,
    sentence: str,
    sides: dict[Fraction, CertificateFigures],
    retained: CertificateFigures,
) -> CertificateFigures | None:
    """Which of this result's own certificates `figure` is a claim about, if any.

    An explicit side beats everything. Failing that, any *other* rung token still in the
    sentence makes the reference ambiguous rather than a vote for the retained rung --
    T-019's own next_rung cites n = 12's ladder (`197/50`, `79/20`) in the same field, and
    neither belongs to T-019's own artifacts, so a figure sitting near them must be left
    unchecked rather than compared to the wrong certificate. Only a sentence naming no
    rung at all defaults to the retained one, matching how this repository's own prose
    reads "the retained certificate's total" or "leaving 0.034265 below seventeen" with no
    side mentioned anywhere in the sentence.
    """
    if figure.side is not None:
        return sides.get(figure.side)
    start, end = figure.span
    others = [
        _fraction(match.group(1), match.group(2))
        for match in _SIDE_TOKEN.finditer(sentence)
        if not (start <= match.start() < end)
    ]
    if not others:
        return retained
    for side in others:
        if side in sides:
            return sides[side]
    return None


def runway_problems(
    figure: QuotedFigure,
    result_id: str,
    field: str,
    artifact: CertificateFigures,
    retained: CertificateFigures,
) -> list[str]:
    """Runway is a claim about the top rung, so the rung it names has to be that one.

    D-442's shape at `T-017`: after the ladder reached `99/25` the sentence still read
    the room under the ceiling at `79/20`, and `0.0408` is the right answer for `79/20`.
    Arithmetic alone cannot catch that, so the rung identity is checked first and the
    figure second.
    """
    if artifact is not retained:
        message = (
            f"{result_id} [{field}]: prose measures runway at "
            f"{_side_text(artifact.outer_side)}, a rung the ladder has climbed past "
            f"({artifact.path}); runway is a property of the retained rung "
            f"{_side_text(retained.outer_side)} ({retained.path})"
        )
        return [message]
    runway = artifact.runway
    if runway is None or decimal_matches(runway, figure.text):
        return []
    digits = len(figure.text.split(".", 1)[1])
    message = (
        f"{result_id} [{field}]: prose says {figure.text} of runway, {artifact.path} "
        f"leaves {round_to(runway, digits)} below ceil(sqrt({artifact.n})) * B "
        f"(exact {runway})"
    )
    return [message]


def figure_problems(
    sentence: str,
    result_id: str,
    field: str,
    sides: dict[Fraction, CertificateFigures],
    retained: CertificateFigures | None,
) -> list[str]:
    if retained is None:
        return []
    problems: list[str] = []
    for figure in quoted_figures(sentence):
        artifact = resolve_target(figure, sentence, sides, retained)
        if artifact is None:
            continue
        label = f"{artifact.path} (side {artifact.outer_side} = {float(artifact.outer_side):g})"
        if figure.kind == "runway":
            problems.extend(runway_problems(figure, result_id, field, artifact, retained))
            continue
        if figure.kind == "atoms":
            stated = int(figure.text.replace(",", ""))
            if stated != artifact.atom_count:
                problems.append(
                    f"{result_id} [{field}]: prose says {stated} atoms, "
                    f"{label} has {artifact.atom_count}"
                )
            continue
        value = artifact.mass if figure.kind == "total" else artifact.margin
        if not decimal_matches(value, figure.text):
            digits = len(figure.text.split(".", 1)[1])
            problems.append(
                f"{result_id} [{field}]: prose says {figure.kind} {figure.text}, "
                f"{label} gives {round_to(value, digits)} (exact {value})"
            )
    return problems


def ladder_problems(
    result_id: str, field: str, text: str, resolved: list[CertificateFigures]
) -> list[str]:
    """A stated ladder length counts the certificate artifacts the result declares.

    D-442's shape at `T-017`: the rationale still said "seven-rung ladder" and listed
    seven sides after the generator retained an eighth, `99/25`, which the same result's
    own artifact list already carried. The ground truth is that artifact list: one live
    `certificate.json` pointer and its immutable historical rungs.
    """
    if not resolved:
        return []
    total = len(resolved)
    problems: list[str] = []
    for pattern, expected, shape in (
        (_LADDER_LENGTH, total, "rungs in the ladder"),
        (_RUNGS_BELOW_TOP, total - 1, "rungs below the retained one"),
        (_RUNGS_RETAINED, total, "retained rungs"),
    ):
        problems.extend(
            f"{result_id} [{field}]: prose says {_rung_count(match.group(1))} {shape}, "
            f"but the result declares {total} certificate artifact(s), so it is {expected}"
            for match in pattern.finditer(text)
            if _rung_count(match.group(1)) != expected
        )
    return problems


def superseded_rung_problems(results: list[dict]) -> list[str]:
    """A "superseded ... by T-XXX" sentence names T-XXX's retained rung, not an old one.

    D-442's second shape: `T-015` and `T-016` both said they were superseded by `T-019`,
    "which certifies 451/100". `451/100` is a real certificate of `T-019`'s and its
    arithmetic is exact, so nothing that recomputes figures can object -- what is wrong is
    which of that result's rungs the sentence points at, and the answer is only visible
    from the other result. The rule is deliberately narrow: a fraction is compared only
    when it is one of the *named* result's own certificate sides, so a published value or
    an unrelated ratio in the same sentence is left alone.
    """
    resolved_by_id = {result["id"]: resolve_certificates(result) for result in results}
    problems: list[str] = []
    for result in results:
        for field, text in prose_fields(result).items():
            for sentence in sentences(text):
                if not _SUPERSEDED.search(sentence):
                    continue
                for named in _SUPERSEDING_RESULT.findall(sentence):
                    entry = resolved_by_id.get(named)
                    if entry is None:
                        problems.append(
                            f"{result['id']} [{field}]: names {named} as superseding it, "
                            "and no result in this register carries that id"
                        )
                        continue
                    retained, sides, _ = entry
                    if retained is None:
                        continue
                    problems.extend(
                        f"{result['id']} [{field}]: says {named} certifies "
                        f"{_side_text(side)}, which is {named}'s {sides[side].path}; "
                        f"{named}'s retained rung is {_side_text(retained.outer_side)}"
                        for match in _SIDE_TOKEN.finditer(sentence)
                        if (side := _fraction(match.group(1), match.group(2))) in sides
                        and side != retained.outer_side
                    )
    return problems


def movement_problems(result: dict) -> list[str]:
    """A result whose claim names exactly two `a/b = d.ddd` figures states their movement.

    Gated on exactly two *distinct* values: every other current result's claim names
    zero (no fraction-equals-decimal figure at all), one (its own side only, with any
    prior value given as an irrational surd this cannot parse, e.g. `2 + 4/sqrt(5)`), or
    the same value twice (a rung restated later in the same claim for an unrelated
    comparison, e.g. against a published packing) -- none of which name two independent
    figures to take a difference between, so the gate does not fire for them regardless
    of what "movement is" phrase they carry elsewhere. It fires for T-019 because its
    claim names both its own side (`229/50`) and a genuinely different displaced prior
    value (`22529/5000`), which is exactly the shape D-439's first instance corrupted.
    """
    result_id = result["id"]
    claim = result.get("claim", "")
    found = list(_FRACTION_EQUALS_DECIMAL.finditer(claim))
    if len(found) != 2:
        return []
    first = _fraction(found[0].group(1), found[0].group(2))
    second = _fraction(found[1].group(1), found[1].group(2))
    if first == second:
        return []
    # Both orderings are accepted so the check never depends on which side the prose
    # names first; only a value matching neither is a disagreement.
    candidates = (first - second, second - first)

    problems: list[str] = []
    for field, text in prose_fields(result).items():
        for match in _MOVEMENT_IS.finditer(text):
            stated = match.group(1)
            digits = len(stated.split(".", 1)[1])
            agrees = any(round_to(c, digits) == Decimal(stated) for c in candidates)
            if not agrees:
                problems.append(
                    f"{result_id} [{field}]: prose says the movement is {stated}, but "
                    f"{found[0].group(0)} vs {found[1].group(0)} gives "
                    f"{round_to(candidates[0], digits)}"
                )
    return problems


def check_result(
    result: dict, pointers_declared_elsewhere: frozenset[str] = frozenset()
) -> tuple[list[str], int]:
    """All figure, movement, and certificate-consistency problems for one result.

    `pointers_declared_elsewhere` carries the live `certificate.json` paths every
    other result declares, which is what lets a superseded result name only the
    historical rung it actually produced.
    """
    result_id = result["id"]
    retained, sides, resolved = resolve_certificates(result)

    problems: list[str] = retained_pointer_problems(
        result_id, resolved, pointers_declared_elsewhere
    )
    for cert in resolved:
        problems.extend(certificate_consistency_problems(cert))

    for field, text in prose_fields(result).items():
        problems.extend(ladder_problems(result_id, field, text, resolved))
        for sentence in sentences(text):
            problems.extend(figure_problems(sentence, result_id, field, sides, retained))

    problems.extend(movement_problems(result))
    return problems, len(resolved)


def evidence_limitation_problems(entry: dict) -> list[str]:
    """One evidence entry's `limitations` prose, read against the certificate it names.

    `D-451`: `E-n012-fractional-certificate` pointed at `certificate.json` and described a
    681-atom certificate at `197/50` -- the file the pointer used to name. Every figure in
    the sentence was exact and real and about a file the entry no longer cites, which is
    `D-439`'s shape at a record `check_result` never opens: it walks `results.yaml`, and an
    evidence entry is a different document with a different schema.

    The anchoring is stricter here than `resolve_target`'s, because an evidence entry
    declares exactly one certificate and its `limitations` is a single folded paragraph
    that ranges freely over others. A sentence is read only when every `a/b` token in it
    is the declared certificate's own side -- including none at all, the unqualified case
    this repository's prose uses to mean "the certificate this entry is about". Anything
    else is left unchecked rather than guessed at. That is what keeps this quiet on
    `E-fractional-interval-decision`, one of whose sentences reports the atom count and
    box count of four different top rungs at once, only one of which it declares.
    """
    declared = entry.get("certificate")
    if not isinstance(declared, str):
        return []
    path = _repo_relative_path(f"packing/{declared}")
    figures = None if path is None else load_certificate(path)
    if figures is None:
        return []
    sides = {figures.outer_side: figures}
    problems: list[str] = []
    for sentence in sentences(entry.get("limitations") or ""):
        named = {
            _fraction(match.group(1), match.group(2))
            for match in _SIDE_TOKEN.finditer(sentence)
        }
        if not named <= {figures.outer_side}:
            continue
        problems.extend(figure_problems(sentence, entry["id"], "limitations", sides, figures))
    return problems


def fraction_decimal_problems(text: str, label: str) -> list[str]:
    """Every `a/b = d.ddd` in `text` must be arithmetically true, repository-wide.

    Generic and reused across `results.yaml`, `evidence.yaml`, and `defects.yaml`: the
    same pattern recurs in all three (D-439's own fix restates the corrected total in
    `defects.yaml`'s prose), and the check is exactly as mechanical wherever it appears.
    """
    problems = []
    for match in _FRACTION_EQUALS_DECIMAL.finditer(text):
        numerator, denominator, stated = match.groups()
        value = _fraction(numerator, denominator)
        if not decimal_matches(value, stated):
            digits = len(stated.split(".", 1)[1])
            problems.append(
                f"{label}: {numerator}/{denominator} = {stated} is wrong; "
                f"{numerator}/{denominator} rounds to {round_to(value, digits)}"
            )
    return problems


def main() -> int:
    document = safe_load(RESULTS.read_text(encoding="utf-8"))
    results = document["results"]

    problems: list[str] = []
    certificates_checked = 0
    declared_pointers = frozenset(
        artifact
        for result in results
        for artifact in result.get("artifacts", [])
        if isinstance(artifact, str) and PurePosixPath(artifact).name == LIVE_CERTIFICATE
    )
    for result in results:
        result_problems, count = check_result(result, declared_pointers)
        problems.extend(result_problems)
        certificates_checked += count

    evidence = safe_load(EVIDENCE.read_text(encoding="utf-8"))["evidence"]
    entries_checked = 0
    for entry in evidence:
        if entry.get("certificate"):
            entries_checked += 1
            problems.extend(evidence_limitation_problems(entry))
    problems.extend(superseded_rung_problems(results))

    for path, label in (
        (RESULTS, "results.yaml"),
        (EVIDENCE, "evidence.yaml"),
        (DEFECTS, "defects.yaml"),
    ):
        problems.extend(fraction_decimal_problems(path.read_text(encoding="utf-8"), label))

    if problems:
        print(f"{len(problems)} rung figure(s) disagree with the artifacts or the arithmetic:")
        for problem in problems:
            print(f"  {problem}")
        return 1
    print(
        f"  {len(results)} results and {entries_checked} certificate-bearing evidence "
        f"entries checked, {certificates_checked} certificate artifacts recomputed from "
        "their own atoms, all quoted figures and fraction-decimal claims agree "
        "(results.yaml, evidence.yaml, defects.yaml)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
