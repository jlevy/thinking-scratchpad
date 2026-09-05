#!/usr/bin/env python3
"""Render the standalone explainer page for a retained fractional certificate.

The page carries one article per retained certificate and a picker to choose
between them, and every quantity each article states is read or derived from
its certificate file, so the page cannot drift from the bounds it explains.
When a rung moves, rerunning this is the whole update: no number is typed twice.

The prose is Markdown, in `templates/explainer-article.md`, and kpress renders it:
headings, lists, math and footnotes are the system's to emit, so the page cannot
hand-roll a footnote or a heading level that the design system would set
differently. The HTML template beside it is only the shell — head, the body
wrapper, and the scripts — and the figures are raw HTML blocks inside the
Markdown, because a canvas, an SVG and a control panel are not things Markdown
expresses. `{{PLACEHOLDERS}}` are substituted before the Markdown is parsed,
which is what keeps a link destination a link destination.

The page is one self-contained file. Typography follows the kpress design
system, and the kpress distribution also supplies the reading faces, KaTeX and
the client behaviors, all inlined. Nothing is fetched at view time, which
is what lets the same artifact serve from GitHub Pages, from a file:// URL, and
from an artifact host with a strict content-security policy.

Usage, from `packing/`:

    uv run --frozen --all-extras --group dev python -m devtools.render_explainer
    uv run --frozen --all-extras --group dev python -m devtools.render_explainer --check
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import shutil
import struct
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from fractions import Fraction
from math import isqrt
from pathlib import Path
from typing import NamedTuple, TypedDict

from strif import atomic_output_file

from devtools.build_composite_figure_data import load_record as load_figure_record
from devtools.measure_net_coarsening import largest_admissible_side
from sqpack.fractional.certificate import (
    Certificate,
    closed_form_conditions,
    d4_images,
    verify,
)
from sqpack.fractional.model import Atom
from sqpack.fractional.sweep import minimum_covered_mass, weight_scale
from sqpack.release import PUBLICATION_DATE, PUBLICATION_EDITION, PUBLICATION_REVISION
from sqpack.render.style import SQUARE_HUE_PALETTE
from sqpack.yamlio import safe_load

PACKING = Path(__file__).resolve().parents[1]
REPO = PACKING.parent
CASE = PACKING / "cases" / "n11_fractional_certificate"
# The registered result these certificates belong to, lowercased as a filename
# stem. `conventions.md` builds every document name for a result from this id --
# `t-018-proof-card.md`, `t-018-verifiable-claim-<bound>.md`, `t-018-explainer.md` --
# and says the published form takes the same name as the case-local one, so the
# id is written once here and the names are derived rather than typed.
RESULT_ID = "t-018"
TEMPLATES = Path(__file__).with_name("templates")
TEMPLATE = TEMPLATES / "explainer-shell.html"
MARKDOWN = TEMPLATES / "explainer-article.md"
VERIFIER_CLAIM = CASE / "verify_claim.py"
OUTPUT = PACKING / "site" / "index.html"

# Four colors have to stay apart in the prover: the mass comfortably above the
# threshold, the mass near it, the mass below it (a region that never occurs
# inside the domain at a net direction), and the square the reader drags,
# which is an instrument rather than a measurement. All three data colors
# come from the project's own square-hue palette, asserted rather than indexed
# so a reordered palette fails here instead of quietly restyling the figure.
BELOW_ONE = "#e26e82"
NEAR_LIMIT = "#c9a13a"
for _colour in (BELOW_ONE, NEAR_LIMIT):
    assert _colour in SQUARE_HUE_PALETTE, f"{_colour} is no longer in the square-hue palette"

# ---------------------------------------------------------------------------
# Printing numbers.
#
# One rule, and the page keeps it everywhere: a value that has an exact decimal
# is printed in full, and a value that has none is marked as approximate where
# it stands. There is no third case, so there is no unmarked rounding, and a
# reader never has to guess whether a digit is the certificate's or the
# formatter's.
# ---------------------------------------------------------------------------

# The widest exact decimal the page prints before showing the rational instead.
# Every weight on both certificates is a whole multiple of 1/200000, so six
# places is what these values actually need; eight leaves a future certificate
# room without letting a long expansion through as a wall of digits.
MAX_EXACT_PLACES = 8

# How far a value with no exact decimal is carried before it is cut off. Seven
# keeps the two irrational bounds one digit past the six-place forms the
# literature quotes, so a reader can see which way the sixth place rounds.
APPROX_PLACES = 7

#: A covered mass this close to 1 is drawn as tight in Figure 5: the legend's percentage
#: and the heat map's threshold are both this one number.
TIGHT = Fraction(112, 100)


def terminating_places(value: Fraction) -> int | None:
    """The number of decimal places `value` needs written out, or None if it never ends.

    A fraction in lowest terms terminates exactly when its denominator is
    2^a * 5^b, and then it needs max(a, b) places and no fewer.
    """
    denominator = value.denominator
    twos = fives = 0
    while denominator % 2 == 0:
        denominator //= 2
        twos += 1
    while denominator % 5 == 0:
        denominator //= 5
        fives += 1
    return max(twos, fives) if denominator == 1 else None


def digits(value: Fraction, places: int) -> str:
    """`value` cut off after `places`, in integer arithmetic so nothing rounds."""
    scaled = abs(value.numerator) * 10**places // value.denominator
    body = str(scaled).rjust(places + 1, "0")
    text = body if places == 0 else f"{body[:-places]}.{body[-places:]}"
    return f"-{text}" if value < 0 else text


def exact_decimal(value: Fraction) -> str | None:
    """`value` written out in full, or None where no decimal of it is exact.

    None covers both a decimal that never terminates and one that terminates
    past `MAX_EXACT_PLACES`. Callers treat the two the same, because the
    rational form serves for both.
    """
    places = terminating_places(value)
    if places is None or places > MAX_EXACT_PLACES:
        return None
    return digits(value, places)


def decimal(value: Fraction) -> str:
    """`value` in full, or a refusal to render: this one never rounds.

    For the places the page asserts an equality — `s(11) >= 19/5 = 3.8` — where
    a rounded decimal would put a false statement on the page. A certificate
    whose bound or mass has no exact decimal fails the build here rather than
    being quietly shortened.
    """
    text = exact_decimal(value)
    if text is None:
        raise SystemExit(
            f"{value} has no exact decimal within {MAX_EXACT_PLACES} places, and the "
            "page states it as an equality; it cannot be printed as a decimal at all"
        )
    return text


def decimal_or_rational(value: Fraction) -> str:
    """`value` in full where it terminates, and as `n/d` where it does not.

    Both forms are exact, so neither carries a mark. The slash is the project's
    inline fraction; stacked fractions are for display math and the mass readout.
    """
    text = exact_decimal(value)
    return text if text is not None else f"{value.numerator}/{value.denominator}"


def truncated(value: Fraction, *, places: int = APPROX_PLACES, tex: bool = False) -> str:
    """`value` cut off after `places` and marked as cut off: `3.8770835…`.

    Cut off rather than rounded, which is what earns the ellipsis: every digit
    shown is a digit of the value, and the value goes on past the last of them.
    """
    return digits(value, places) + ("\\ldots" if tex else "…")


def nearly(text: str, *, tex: bool = False) -> str:
    """Mark an already-rounded number as approximate: `≈0.23%`.

    For a number no truncation can be claimed for: a percentage, cut to two
    figures because two figures are the point of one, and a value that reaches
    the page already rounded, which no formatter here can undo.
    """
    return f"\\approx {text}" if tex else f"≈{text}"


# The prior state of the case, which the page reports next to the new bound.
# Neither number is rational, so neither has an exact decimal and neither is
# ever printed bare. Both are carried to far more digits than the page shows,
# so that a difference of two of them is truncated once, where it is printed,
# rather than inheriting a rounding from a constant.
#
# Stromquist's bound is 2 + 4/sqrt(5), derived here from that closed form —
# which the page's own footer states — rather than typed: 4/sqrt(5) is
# sqrt(3.2), and 3.2 * 10^(2p) is a whole number, so an integer square root
# gives its first p digits exactly.
CARRIED_PLACES = 32
PRIOR_LOWER = 2 + Fraction(isqrt(32 * 10 ** (2 * CARRIED_PLACES - 1)), 10**CARRIED_PLACES)
PRIOR_SOURCE = "Stromquist 2003"

# Trump's packing is an algebraic number, the root in this interval of the
# minimal polynomial the record cites (resources/web/kingbird-squares-in-squares.md).
# The digits come from the retained witness, witnesses/known-best/n-011.yaml,
# and are checked against that polynomial rather than trusted, because the page
# prints them and claims with an ellipsis that they are the root's own: the
# root lies between the constant and one unit in its last place above it.
BEST_PACKING = Fraction("3.87708359002281417730789706010096")
BEST_PACKING_POLYNOMIAL = (1, -20, 178, -842, 1923, -496, -6754, 12420, -6865)
BEST_SOURCE = "Trump 1979 packing"


def _polynomial(x: Fraction) -> Fraction:
    value = Fraction(0)
    for coefficient in BEST_PACKING_POLYNOMIAL:
        value = value * x + coefficient
    return value


_ULP = Fraction(1, 10**CARRIED_PLACES)
assert _polynomial(BEST_PACKING) < 0 < _polynomial(BEST_PACKING + _ULP), (
    "the best-packing constant is no longer a truncation of its own root"
)

PRIOR_YEAR = 2003
RESULT_YEAR = 2026

# Where the page sends a reader for more: the sources the n = 11 record cites
# (frontier/n-011.md, keys [Friedman DS7], [Kingbird] and [Stromquist 2003]) and
# the repository files behind the words, linked on `main`, which is what the
# page deploys from.
PROBLEM_URL = "https://erich-friedman.github.io/papers/squares/squares.html"
BEST_URL = "https://kingbird.myphotos.cc/packing/squares_in_squares.html"
PRIOR_URL = "https://www.combinatorics.org/ojs/index.php/eljc/article/view/v10i1r8"
REPO_URL = "https://github.com/jlevy/squares"
# Where the deploy serves this page: the GitHub Pages site for the repository, at
# the project subpath, with the trailing slash the directory URL actually resolves
# to. A link preview is the one part of the page that cannot be relative -- a
# crawler resolves `og:image` and `og:url` on its own machine, not against the
# document -- so the deployment's own address has to be stated somewhere, and this
# is that one place.
SITE_URL = "https://jlevy.github.io/squares/"
SITE_NAME = "Squares"
BEST_RENDERING = PACKING / "atlas" / "known-best" / "rendering" / "n-011.svg"
# The atlas composite of every known-best packing, shown as Figure 1 and served
# beside the page rather than inlined: the PNG is the image, the PDF the link.
#: The composite travels with the page: the SVG the figure shows, the PDF it links for
#: print, and the PNG for a reader whose context cannot render the vector.
COMPOSITE_STEM = PACKING / "atlas" / "known-best" / "known-best-1-100"
COMPOSITE_ASSETS = tuple(COMPOSITE_STEM.with_suffix(f".{ext}") for ext in ("svg", "png", "pdf"))
#: The one of the three a link preview shows. No unfurler renders SVG and none follows a
#: PDF, so the card names the raster, and it names the 1x rather than the committed
#: `@2x`: 2400x2896 is inside the 4096x4096 ceiling X applies to a card image and
#: 4800x5792 is outside it on both axes, while every consumer downscales to 600px or
#: less anyway. The 1x is also already copied beside the page; the 2x is not, and adding
#: it would put another 1.2 MiB in every deploy for resolution nothing displays.
COMPOSITE_PNG = COMPOSITE_STEM.with_suffix(".png")
#: What Figure 1 and the link preview are both a picture of, written once. The figure
#: shows the SVG and the card the PNG, but they are the same drawing, so a reader on a
#: screen reader and a reader seeing an unfurl get the same sentence.
COMPOSITE_ALT = (
    "The best known packings of one through one hundred unit squares, in a ten-by-ten "
    "grid, each labelled with its best known upper bound and, where the value is still "
    "open, the best proved lower bound"
)
VERIFIER = PACKING / "src" / "sqpack" / "fractional" / "certificate.py"
GENERATOR = PACKING / "src" / "sqpack" / "fractional" / "generate.py"
THIRDPARTY = CASE / "thirdparty" / "README.md"


def repo_file(path: Path) -> str:
    """The file's URL on main; a path outside the repository has no such URL."""
    try:
        relative = path.resolve().relative_to(REPO)
    except ValueError:
        raise SystemExit(
            f"{path} is outside the repository and cannot be linked on main"
        ) from None
    return f"{REPO_URL}/blob/main/{relative.as_posix()}"


def site_file(path: Path) -> str:
    """The asset's absolute URL on the deployed site, for a consumer off the page.

    Everything the page itself points at is relative, because the page has to open
    the same way from a file, from Pages and from an artifact host. A link preview
    cannot: the crawler that reads `og:image` has no base to resolve against and
    drops a relative one, so the card states the deployed address in full.
    """
    return SITE_URL + path.name


def png_size(path: Path) -> tuple[int, int]:
    """The pixel dimensions in a PNG's IHDR, read from the file the render publishes.

    `og:image:width` and `og:image:height` let a consumer reserve the card's box
    before it has fetched the image, and a pair that disagrees with the file is worse
    than none: the preview reflows, or is dropped. Reading them from the bytes that
    are copied beside the page means a re-exported atlas moves the tags with it and
    no dimension is typed twice.
    """
    with path.open("rb") as handle:
        header = handle.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
        raise SystemExit(f"{path} is not a PNG; the link preview cannot state its size")
    width, height = struct.unpack(">II", header[16:24])
    return width, height


# The certificates the page walks through, in tab order. The first is shown by
# default because it is the smaller one and its numbers are easier to follow;
# the headline bound is the largest outer side among them, whichever that is.
WALKTHROUGH = (CASE / "certificate-19-5.json", CASE / "certificate.json")

# Only the KaTeX faces this page can reach. The rest of the distribution's
# @font-face blocks are dropped rather than inlined; every one costs 30-40 KB.
KATEX_FACES = frozenset(
    {
        "KaTeX_AMS-Regular",
        "KaTeX_Caligraphic-Regular",
        "KaTeX_Main-Bold",
        "KaTeX_Main-Italic",
        "KaTeX_Main-Regular",
        "KaTeX_Math-Italic",
        "KaTeX_Size1-Regular",
        "KaTeX_Size2-Regular",
        "KaTeX_Size3-Regular",
        "KaTeX_Size4-Regular",
    }
)


# `page-reset.css` is not in kpress's DEFAULT_CSS_ASSETS: kpress inlines it
# separately, render-blocking, because it owns html/body for a standalone shell
# and an embedded fragment must not carry it. This page is standalone, so it
# goes first. The rest of the order is kpress's own, imported rather than
# copied, so a stylesheet added upstream is picked up here without an edit.
PAGE_RESET = "css/page-reset.css"


def kpress_static() -> Path:
    """The kpress distribution's static asset root.

    Imported inside the function rather than at module scope: this renderer is
    the only devtool that needs kpress, and a module-level import would make
    every other entry point in this package fail if it were ever absent.
    """
    try:
        import kpress.format as kpress_format  # noqa: PLC0415
    except ModuleNotFoundError:  # pragma: no cover - a dependency-group failure
        raise SystemExit(
            "kpress is not installed. Run with `--group dev`, which pins it."
        ) from None
    static = Path(kpress_format.__file__).parent / "static"
    if not (static / "katex" / "katex.min.js").is_file():
        raise SystemExit(f"kpress static assets are missing under {static}")
    return static


def data_uri(path: Path) -> str:
    return f"data:font/woff2;base64,{base64.b64encode(path.read_bytes()).decode()}"


def inline_font_urls(css: str, fonts: Path) -> str:
    """Rewrite `url("../fonts/x.woff2")` to a data URI, so the page fetches nothing."""

    def rewrite(match: re.Match[str]) -> str:
        name = match.group(1)
        return f'url("{data_uri(fonts / name)}")'

    return re.sub(r'url\("\.\./fonts/([A-Za-z0-9_.-]+)"\)', rewrite, css)


def kpress_css(static: Path) -> str:
    """The kpress design system as one stylesheet, its webfonts inlined.

    Taken whole rather than reimplemented: the reading measure, the type ramp,
    the heading and list treatments, the color roles and both themes are the
    system's to define, and a page that re-declared a subset of them would drift
    from it silently. This page adds only what kpress has no component for.
    """
    from kpress.format.assets import DEFAULT_CSS_ASSETS  # noqa: PLC0415

    parts = []
    for name in (PAGE_RESET, *DEFAULT_CSS_ASSETS):
        parts.append(f"/* kpress: {name} */")
        parts.append((static / name).read_text(encoding="utf-8"))
    return inline_font_urls("\n".join(parts), static / "fonts")


def theme_bootstrap(static: Path) -> str:
    """kpress's pre-paint theme resolution, so light and dark match the system."""
    return (static / "js" / "theme-bootstrap.js").read_text(encoding="utf-8")


# The two kpress behaviors this page borrows — hover previews for footnotes and
# the copy button on a code block — live in six ES modules, listed here in
# dependency order: each may import only from the ones before it. The page
# cannot load them as modules — an inline `<script type="module">` would fetch
# `./viewport.js` and its siblings at view time, which is the one thing this
# page refuses — so they are flattened into a single classic script sharing one
# function scope. The flattening is checked rather than assumed: every rule
# below fails the render, so a kpress upgrade that reshapes these modules
# breaks the build instead of quietly shipping previews that never appear.
KPRESS_MODULES = (
    "icons.js",
    "viewport.js",
    "overlay.js",
    "runtime.js",
    "tooltips.js",
    "code-copy.js",
)

# The only two module forms the flattener can rewrite: a named import from a
# sibling in that list, and an `export` prefixed to a declaration. Everything
# else — `export default`, `export { a, b }`, `export *`, a default or namespace
# import, an aliased binding — fails to match, and a failure to match is a build
# error rather than a silent drop.
_IMPORT_STATEMENT = re.compile(r"^import\b[^;]*;", re.MULTILINE)
_NAMED_IMPORT = re.compile(r'import \{ ?([^}]*?) ?\} from "\./([A-Za-z0-9_.-]+)";')
_JS_NAME = re.compile(r"[A-Za-z_$][\w$]*")
_EXPORT_LINE = re.compile(r"^export\b.*$", re.MULTILINE)
_EXPORT_DECLARATION = re.compile(
    rf"export (?:async )?(?:function|const|let|var|class) ({_JS_NAME.pattern})\b"
)
_EXPORT_PREFIX = re.compile(
    r"^export (?=(?:async )?(?:function|const|let|var|class) )", re.MULTILINE
)
_TOP_LEVEL_DECLARATION = re.compile(
    rf"^(?:async )?(?:function|const|let|var|class) ({_JS_NAME.pattern})\b", re.MULTILINE
)
# Module-only constructs a flat classic script cannot carry. Top-level `await`
# is the sharp one: inside the wrapper's plain arrow function it is a syntax
# error, so the page would die at parse rather than degrade. A dynamic
# `import()` parses but would fetch at view time, against the page's own URL.
# These are textual scans over comments as well as code, so they are written
# literally — `import\s*\(` matched the phrase "register at import (no DOM
# work)" in runtime.js's header comment.
_MODULE_ONLY = (
    (re.compile(r"\bimport\.meta\b"), "import.meta"),
    (re.compile(r"\bimport\("), "a dynamic import()"),
    (
        re.compile(r"^(?:await\b|(?:const|let|var) [^;]*?\bawait\b)", re.MULTILINE),
        "top-level await",
    ),
)

# The three names the epilogue below reaches for, and the module each is
# kpress's public API from. Checked against what that module exports rather than
# against what it happens to declare: an upstream that stops exporting one of
# these is retiring it, whatever the flattened scope would still resolve.
KPRESS_API = {
    "runtime.js": "behaviors",
    "tooltips.js": "initKpressTooltips",
    "code-copy.js": "initKpressCodeCopy",
}

# What the flattened script hands the page, and why it hands over only half of
# what kpress registers. Overriding a behavior with a no-op bind is kpress's own
# seam (`behaviors.override`), and running it here — at script evaluation, before
# the runtime's ready pass — is what keeps the built-in link previews from ever
# binding.
KPRESS_EPILOGUE = """
/* This page wants footnote previews and nothing else. kpress's tooltips module
   registers two behaviors at import — hover previews for internal links, and
   footnote previews — and the runtime binds both once the document is ready,
   which here would hang a preview reading "1" off every footnote's back-arrow.
   The link behavior is overridden with a no-op bind before that pass runs; the
   footnote one is left alone, and the page boots it explicitly as well. The
   copy button is kpress's own too: its behavior binds itself at the runtime's
   ready pass, and the boot below runs it earlier so the control is there before
   the reader can reach the block. */
behaviors.override("tooltip", () => undefined);
window.kpressInitTooltips = initKpressTooltips;
window.kpressInitCodeCopy = initKpressCodeCopy;
"""


def kpress_client_js(static: Path) -> str:
    """kpress's client modules as one classic script, exposing the two boots.

    Concatenates `KPRESS_MODULES` in order into one IIFE, dropping the imports
    (every name they bind is already in scope by the time it is used) and the
    `export` keyword. Refuses to produce a bundle it cannot vouch for: an import
    or export form it does not rewrite, an imported name the source module no
    longer exports, a module-only construct, a `KPRESS_API` name that is gone,
    or two modules declaring the same top-level name — which sharing one scope
    would silently resolve to whichever came last.
    """
    exported: dict[str, set[str]] = {}
    declared: dict[str, str] = {}
    parts: list[str] = []

    for name in KPRESS_MODULES:
        path = static / "js" / name
        if not path.is_file():
            raise SystemExit(f"kpress has no js/{name}; the client modules have moved")
        source = path.read_text(encoding="utf-8")

        names: set[str] = set()
        for line in _EXPORT_LINE.findall(source):
            match = _EXPORT_DECLARATION.match(line)
            if match is None:
                raise SystemExit(
                    f"js/{name}: cannot flatten `{line[:60]}`; "
                    "only `export <declaration>` is rewritten"
                )
            names.add(match.group(1))
        if not names:
            raise SystemExit(f"js/{name} exports nothing; the module shape has changed")
        exported[name] = names

        for statement in _IMPORT_STATEMENT.findall(source):
            flat = " ".join(statement.split())
            match = _NAMED_IMPORT.fullmatch(flat)
            if match is None:
                raise SystemExit(
                    f"js/{name}: cannot flatten `{flat[:60]}`; "
                    'only `import {…} from "./sibling.js"` is rewritten'
                )
            origin = match.group(2)
            if origin not in exported:
                raise SystemExit(
                    f"js/{name} imports from {origin}, which is not bundled before it"
                )
            for binding in match.group(1).rstrip(",").split(","):
                symbol = binding.strip()
                if not _JS_NAME.fullmatch(symbol):
                    raise SystemExit(f"js/{name}: cannot flatten the import binding `{symbol}`")
                if symbol not in exported[origin]:
                    raise SystemExit(f"js/{name} imports {symbol}, which js/{origin} lost")

        body = _EXPORT_PREFIX.sub("", _IMPORT_STATEMENT.sub("", source))
        stray = _EXPORT_LINE.search(body)
        if stray is not None:
            raise SystemExit(f"js/{name}: `{stray.group()[:60]}` survived the export rewrite")
        for pattern, label in _MODULE_ONLY:
            if pattern.search(body):
                raise SystemExit(
                    f"js/{name} uses {label}, which a flattened script cannot carry"
                )

        for match in _TOP_LEVEL_DECLARATION.finditer(body):
            symbol = match.group(1)
            owner = declared.setdefault(symbol, name)
            if owner != name:
                raise SystemExit(
                    f"js/{name} declares `{symbol}`, which js/{owner} also declares; "
                    "one scope cannot hold both"
                )
        parts.append(f"/* kpress: js/{name} */\n{body.strip()}\n")

    for module, wanted in KPRESS_API.items():
        if wanted not in exported.get(module, frozenset()):
            raise SystemExit(
                f"js/{module} no longer exports `{wanted}`; the page cannot boot it"
            )

    modules = ", ".join(f"js/{name}" for name in KPRESS_MODULES)
    bundle = f"/* kpress client behaviors, flattened from {modules} */\n(() => {{\n"
    bundle += '"use strict";\n' + "\n".join(parts) + KPRESS_EPILOGUE + "})();\n"
    if re.search(r"</script", bundle, re.IGNORECASE):
        raise SystemExit("a kpress client module carries `</script`; it cannot be inlined")
    return bundle


def icon_sprite(static: Path) -> str:
    """kpress's icon sprite, which its chrome references by fragment.

    The copy button's glyph is a `<use href="#kpress-icon-copy">`, so the sprite
    has to be in the document for the control to have a face at all; kpress's own
    renderer inlines it once per document and this does the same. It is hidden,
    costs 5 KB, and referencing a fragment rather than a file is what keeps the
    button drawn under a strict content-security policy.
    """
    sprite = (static / "icons" / "icons.svg").read_text(encoding="utf-8")
    if "kpress-icon-copy" not in sprite:
        raise SystemExit("kpress's icon sprite has no copy glyph; the button would be blank")
    return sprite


def katex_css(static: Path) -> str:
    """KaTeX's stylesheet with the reachable faces inlined and the rest dropped."""
    css = (static / "katex" / "katex.min.css").read_text(encoding="utf-8")

    def rewrite(match: re.Match[str]) -> str:
        block = match.group(0)
        ref = re.search(r"fonts/([A-Za-z0-9_-]+)\.woff2", block)
        if ref is None:
            return block
        if ref.group(1) not in KATEX_FACES:
            return ""
        uri = data_uri(static / "katex" / "fonts" / f"{ref.group(1)}.woff2")
        return block.replace(f"url(fonts/{ref.group(1)}.woff2)", f'url("{uri}")')

    return re.sub(r"@font-face\{[^}]*\}", rewrite, css)


class CoarseningRow(TypedDict):
    """One row of the retained net-coarsening measurement."""

    K: int
    D: str
    B: str
    least_mass: str
    least_mass_exact: str
    passes: bool
    seconds: float


@dataclass(frozen=True, slots=True)
class Facts:
    """Everything the page states about one certificate, derived from its file."""

    identifier: str
    source: Path
    n: int
    outer_side: Fraction
    square_side: Fraction
    steps: int
    angle_limit: Fraction
    atoms: tuple[Atom, ...]
    total_mass: Fraction
    least_mass: Fraction
    witness: tuple[Fraction, Fraction]
    orbits: int
    distinct_weights: int
    weight_scale: int
    # `D`, the tangent of the net's widest half-gap, and the largest side on the
    # shrink figure's grid that Condition 4 admits for it: what Figure 6 shows.
    half_gap: Fraction
    admitted_side: Fraction


def load_certificate(path: Path) -> tuple[Certificate, dict[str, str]]:
    record = json.loads(path.read_text(encoding="utf-8"))
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


def derive(path: Path, *, full_sweep: bool = False) -> Facts:
    """Read a certificate and compute what the page reports, deciding it first.

    Conditions 1 through 4 are re-decided on every render: they are exact rational
    comparisons costing microseconds, and a page explaining a proof should not be
    renderable from a file those conditions refuse. Condition 5 is the expensive one, a
    sweep over every direction and minutes at this atom count, and the case
    already owns a replay gate that decides it, so re-deciding it here would buy
    a second copy of one verdict at the price of the build. The upright direction
    is swept regardless: the page marks its witness, and the record's declared
    least covered mass has to be exactly what that sweep finds, since the prose
    says the least cell lies at direction 0; a certificate whose least cell lies
    elsewhere is refused rather than described wrongly. `--verify-condition-5`
    runs the whole sweep and holds it to the same value.
    """
    certificate, record = load_certificate(path)
    refused = [report for report in closed_form_conditions(certificate) if not report.holds]
    if refused:
        raise SystemExit(
            f"{path.name} fails {', '.join(r.name for r in refused)}; refusing to render"
        )
    upright = certificate.directions[0]
    least, witness = minimum_covered_mass(
        certificate.atoms, upright, certificate.outer_side, certificate.square_side
    )
    if full_sweep:
        verdict = verify(certificate)
        if not verdict.accepted:
            raise SystemExit(
                f"{path.name} fails {', '.join(verdict.failures)}; refusing to render"
            )
        if verdict.minimum_cell_mass != least:
            raise SystemExit(
                f"{path.name}: the least cell lies at direction {verdict.worst_direction} "
                f"({verdict.minimum_cell_mass}), not at the upright one the page describes "
                f"({least})"
            )

    seen: set[frozenset[tuple[Fraction, Fraction]]] = set()
    for atom in certificate.atoms:
        seen.add(frozenset(d4_images(atom.x, atom.y, certificate.outer_side)))

    scale = weight_scale(certificate.atoms)
    # The prover's readout prints its integer count of 1/scale units as a
    # six-place decimal, and that is exact only because the scale divides a
    # million. A certificate with a finer unit would make `= 1.000060` a
    # rounding, which is the one thing the page does not do.
    if 10**6 % scale:
        raise SystemExit(
            f"{path.name} carries weights in units of 1/{scale}, which does not divide "
            "10^6; the page's six-place mass readout would round rather than report"
        )

    declared_total = Fraction(record["total_mass"])
    if declared_total != certificate.total_mass:
        raise SystemExit(
            f"{path.name} declares total mass {declared_total}, "
            f"carries {certificate.total_mass}"
        )
    declared_least = Fraction(record["least_cell_mass"])
    if least != declared_least:
        raise SystemExit(
            f"{path.name} declares least cell mass {declared_least}, and the upright "
            f"direction's is {least}; the page says the least cell is at direction 0"
        )
    gap, admitted = largest_admissible_side(certificate.half_tangents)

    return Facts(
        identifier=record["id"],
        source=path,
        n=certificate.n,
        outer_side=certificate.outer_side,
        square_side=certificate.square_side,
        steps=int(record["direction_steps"]),
        angle_limit=Fraction(record["angle_limit"]),
        atoms=certificate.atoms,
        total_mass=certificate.total_mass,
        least_mass=least,
        witness=witness,
        orbits=len(seen),
        distinct_weights=len({atom.weight for atom in certificate.atoms}),
        weight_scale=scale,
        half_gap=gap,
        admitted_side=admitted,
    )


def frac_tex(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"\\frac{{{value.numerator}}}{{{value.denominator}}}"


def atom_array(facts: Facts) -> str:
    """The atoms as exact integers: numerator and denominator per coordinate.

    The page sums weights as integer multiples of `1 / weight_scale`, so the
    covered mass it reports is exact rather than a float total. Coordinates go
    the same way so a hovered atom can name the rational the certificate holds
    rather than a rounding of it; the float pair every draw call needs is
    derived once at load.
    """
    rows = []
    for atom in facts.atoms:
        weight = atom.weight * facts.weight_scale
        assert weight.denominator == 1
        rows.append(
            f"[{atom.x.numerator},{atom.x.denominator},"
            f"{atom.y.numerator},{atom.y.denominator},{weight.numerator}]"
        )
    return (
        "const ATOM_Q=[" + ",".join(rows) + "];\n"
        "const ATOMS=ATOM_Q.map(([xn,xd,yn,yd,w])=>[xn/xd,yn/yd,w]);"
    )


def best_packing_svg() -> str:
    """The atlas rendering of the best packing known, cropped to the container.

    Inlined rather than linked so the page stays self-contained. The prolog and
    the provenance metadata go, and the viewBox is cut to the container's
    outline plus a margin; the file's own caption and ground are restyled by
    the page's CSS rather than edited here.
    """
    svg = BEST_RENDERING.read_text(encoding="utf-8")
    svg = re.sub(r"<\?xml[^>]*\?>\s*", "", svg)
    svg = re.sub(r"<metadata>.*?</metadata>\s*", "", svg, flags=re.DOTALL)
    outline = re.search(
        r'data-feature="container-outline" x="([\d.]+)" y="([\d.]+)" width="([\d.]+)"', svg
    )
    if outline is None:
        raise SystemExit(f"{BEST_RENDERING.name} has no container outline to crop to")
    x, y, side = (round(float(v)) for v in outline.groups())
    margin = 12
    box = f'viewBox="{x - margin} {y - margin} {side + 2 * margin} {side + 2 * margin}"'
    svg, count = re.subn(r'width="\d+" height="\d+" viewBox="[^"]*"', box, svg, count=1)
    if count != 1:
        raise SystemExit(f"{BEST_RENDERING.name} root has no width/height/viewBox to replace")
    # The figure that carries this is a raw HTML block in the Markdown, and a
    # Markdown HTML block ends at the first blank line: one inside the drawing
    # would hand the rest of the file to the paragraph parser.
    if any(not line.strip() for line in svg.splitlines()):
        raise SystemExit(
            f"{BEST_RENDERING.name} has a blank line; it would end the figure's HTML block"
        )
    return svg


def coarsening_path(facts: Facts) -> Path:
    """The certificate's retained net-coarsening measurement, named for its bound."""
    return CASE / f"net-coarsening-{slug(facts)}.json"


def coarsening_rows(facts: Facts) -> list[CoarseningRow] | None:
    """The retained net-coarsening measurement for this certificate, or None.

    The measurement belongs to one certificate and is retained in a file named
    for its bound, so a certificate that has not been measured yet renders
    without that figure rather than blocking on it or borrowing another
    certificate's numbers. A file that is there is held to the certificate it
    names: its id, its path, nets in order ending at the certificate's own, and
    a pass flag that agrees with the mass beside it.
    """
    path = coarsening_path(facts)
    if not path.is_file():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("certificate_id") != facts.identifier:
        raise SystemExit(
            f"{path.name} measures {payload.get('certificate_id')}, not {facts.identifier}"
        )
    source = facts.source.resolve()
    if source.is_relative_to(REPO) and payload.get("certificate") != (
        source.relative_to(REPO).as_posix()
    ):
        raise SystemExit(f"{path.name} names {payload.get('certificate')} as its certificate")
    rows: list[CoarseningRow] = payload["rows"]
    nets = [int(row["K"]) for row in rows]
    if nets != sorted(nets) or nets[-1] != facts.steps:
        raise SystemExit(
            f"{path.name} runs nets {nets}; the page expects them ascending and ending at "
            f"the certificate's own K = {facts.steps}"
        )
    for row in rows:
        if bool(row["passes"]) != (row_mass(row) >= 1):
            raise SystemExit(f"{path.name} row K={row['K']} declares passes={row['passes']}")
    return rows


def row_mass(row: CoarseningRow) -> Fraction:
    """One row's least covered mass, exactly, checked against its rounded twin.

    The measurement records both, and the figure prints the exact one; a file
    whose two fields are not the same number is a stale record rather than a
    rounding to reconcile, so it fails the render instead of being averaged over.
    """
    exact = Fraction(row["least_mass_exact"])
    if abs(exact - Fraction(row["least_mass"])) > Fraction(1, 2 * 10**6):
        raise SystemExit(
            f"net-coarsening row K={row['K']} declares {row['least_mass']} and "
            f"{row['least_mass_exact']}; those are not the same measurement"
        )
    return exact


def coarsening_svg(rows: list[CoarseningRow]) -> tuple[str, str, str]:
    """Bars, value labels and axis labels for the net-coarsening figure."""
    left, width, gap = 100.0, 66.0, 50.0
    top, base = 30.0, 190.0
    bars, values, labels = [], [], []
    for index, row in enumerate(rows):
        x = left + index * (width + gap)
        mass = row_mass(row)
        height = min(float(mass), 1.0) * (base - top)
        passes = bool(row["passes"])
        accent = 'fill="var(--kpress-doc-accent)"'
        fill = accent if passes else f'{accent} opacity=".3"'
        bars.append(
            f'<rect x="{x:.0f}" y="{base - height:.0f}" width="{width:.0f}" '
            f'height="{height:.0f}" {fill}/>'
        )
        emphasis = ' fill="var(--kpress-doc-accent)" font-weight="650"' if passes else ""
        # The label is the measurement itself, in full: these five all
        # terminate inside the cap, and one that did not would be labelled with
        # its rational rather than with a rounding of it.
        values.append(
            f'<text x="{x + width / 2:.0f}" y="{base - height - 6:.0f}"{emphasis}>'
            f"{decimal_or_rational(mass)}</text>"
        )
        tone = ' fill="var(--kpress-doc-text)"' if passes else ""
        # The B each net admits is a whole multiple of 10^-7, and the
        # measurement records it rounded to six places rather than exactly, so
        # the label says as much. The mass above the bar is the exact one.
        labels.append(
            f'<text x="{x + width / 2:.0f}" y="210"{tone}>K = {row["K"]}</text>'
            f'<text x="{x + width / 2:.0f}" y="226" font-size="9.5">'
            f"B {nearly(row['B'])}</text>"
        )
    return "\n        ".join(bars), "\n        ".join(values), "\n        ".join(labels)


def halving_cost(rows: list[CoarseningRow]) -> tuple[str, str]:
    """What halving the finest net costs, as percentages, from the measurement.

    Stated in the figure's caption, so it is derived rather than written:
    the same sentence carried a figure from an earlier certificate for one
    render, and the two nets it compares are exactly the ones the rows hold.
    """
    by_net = {int(row["K"]): row for row in rows}
    finest = max(by_net)
    half = finest // 2
    if half not in by_net:
        raise SystemExit(
            f"the net-coarsening rows run to K = {finest} with no K = {half} row; the "
            "caption compares those two and cannot be stated"
        )
    fine, coarse = by_net[finest], by_net[half]
    b_drop = 1 - Fraction(coarse["B"]) / Fraction(fine["B"])
    mass_drop = 1 - row_mass(coarse) / row_mass(fine)
    # Each is an exact rational and each is printed to a couple of figures,
    # because a couple of figures is the whole point of a percentage. That is a
    # rounding, so both go out marked.
    return nearly(f"{float(b_drop) * 100:.2f}%"), nearly(f"{float(mass_drop) * 100:.0f}%")


# The bounds figure's axis, in the pixels of its own 700-wide viewBox. These are
# pixels, not quantities: a rounded coordinate is a rounded coordinate and not a
# rounded bound.
LINE_LOW, LINE_HIGH, LINE_X0, LINE_X1 = 3.75, 3.90, 20.0, 680.0
# The axis sits at y = 51.5; a certificate's mark hangs below it, one row per
# certificate, the headline bound deepest so no label crosses the mark under it.
LINE_AXIS_Y = 51.5
LINE_FIRST_ROW = 62.0
LINE_ROW = 22.0
# The viewBox height the figure declares. A certificate count that would not fit
# under the axis fails the render rather than drawing off the bottom of the box.
LINE_HEIGHT = 92.0


def line_x(value: float) -> float:
    """Where a bound falls on the axis, in the figure's own pixels."""
    return LINE_X0 + (value - LINE_LOW) / (LINE_HIGH - LINE_LOW) * (LINE_X1 - LINE_X0)


def number_line_marks(facts: list[Facts], headline: Facts) -> str:
    """Every certificate's mark on the shared axis: a tick, a dot and a label.

    The figure states all of the bounds at once, so the marks are generated here
    the way the coarsening bars are, rather than written once and stamped per
    certificate. Rows go by bound, smallest first and the headline last and
    deepest: a label runs to the right of its own mark, so the mark below it is
    always the further one along the axis and the two cannot collide.
    """
    ordered = sorted(facts, key=lambda f: f.outer_side)
    if ordered[-1] is not headline:
        raise SystemExit("the headline bound is not the largest; the marks would stack wrong")
    depth = LINE_FIRST_ROW + LINE_ROW * (len(ordered) - 1)
    if depth + 4 > LINE_HEIGHT:
        raise SystemExit(
            f"{len(ordered)} certificates need {depth + 4:.0f} pixels of axis and the "
            f"figure's viewBox is {LINE_HEIGHT:.0f} tall; raise it in the Markdown"
        )
    marks = []
    for index, f in enumerate(ordered):
        x = line_x(float(f.outer_side))
        y = LINE_FIRST_ROW + LINE_ROW * index
        lead = f is headline
        colour = "var(--cert-probe)" if lead else "var(--kpress-doc-muted)"
        emphasis = ' font-weight="550"' if lead else ""
        label = f"{f.outer_side.numerator}/{f.outer_side.denominator} = {decimal(f.outer_side)}"
        if lead:
            label += ", proved below"
        marks.append(
            f'<line x1="{x:.0f}" y1="{LINE_AXIS_Y}" x2="{x:.0f}" y2="{y:.0f}" '
            f'stroke="{colour}" stroke-width="{2 if lead else 1.25}"/>'
            f'<circle cx="{x:.0f}" cy="{LINE_AXIS_Y}" r="{4.4 if lead else 3.2}" '
            f'fill="{colour}"/>'
            f'<text x="{x:.0f}" y="{y + 4:.0f}" dx="11" font-size="11"{emphasis} '
            f'fill="{colour}">{label}</text>'
        )
    return "\n    ".join(marks)


def starred_lower_bounds() -> int:
    """How many atlas cells carry a lower bound this project proved.

    The composite counts them in its own legend from the figure record; the caption
    beside the image reads the same total, so the two cannot disagree.
    """
    return int(load_figure_record()["totals"]["lower_bound_first_proved_here"])


def registered_results() -> int:
    """How many results the frontier register holds, counted rather than typed.

    The opening says this bound is one of several the program has registered; the
    register is the only place that number lives, so the page reads it there.
    """
    register = PACKING / "frontier" / "results.yaml"
    entries = safe_load(register.read_text(encoding="utf-8"))["results"]
    if not entries:
        raise SystemExit(f"{register.name} lists no results; the opening states a count")
    return len(entries)


def bound_substitutions() -> dict[str, str]:
    """The two irrational bounds, in the forms the page is allowed to print them.

    Neither has a bare form, and that is the point: a template that reaches for
    `{{BEST_PACKING}}` fails the render rather than printing six digits that
    look exact. `_DEC` is what prose, an aria-label and an SVG label carry;
    `_TEX` is the same truncation with KaTeX's ellipsis, so it can stand on
    either side of a relation without claiming to be the whole number.
    """
    return {
        "PRIOR_LOWER_DEC": truncated(PRIOR_LOWER),
        "BEST_PACKING_DEC": truncated(BEST_PACKING),
        "BEST_PACKING_TEX": truncated(BEST_PACKING, tex=True),
    }


def shrink_peak_tex(facts: Facts, side: Fraction) -> str:
    """The largest value Figure 6's readout reaches on the certificate's own net.

    The readout is `B (cos d + sin d)` for a side `B` and a mismatch `d` up to the
    widest half-gap, whose tangent is `D`; `cos d + sin d` grows with `d` below an
    eighth turn, so the peak is `B (1 + D) / sqrt(1 + D^2)`. The caption states it
    twice, for the side the figure uses (`facts.admitted_side`, one grid step below
    the largest the net admits) and for the certificate's own `square_side`, since
    the two differ in the sixth place. Irrational, so it is cut off by an integer
    square root and marked as cut off.
    """
    scaled = side * (1 + facts.half_gap) * 10**APPROX_PLACES
    cut = isqrt(int(scaled * scaled / (1 + facts.half_gap**2)))
    return truncated(Fraction(cut, 10**APPROX_PLACES), tex=True)


def ceiled(value: Fraction, places: int) -> str:
    """`value` rounded up to `places` decimals, as a bound that is safe to state."""
    scale = 10**places
    return f"{-((-value * scale) // 1) / scale:.{places}f}"


def k3_limit_tex(facts: Facts) -> str:
    """The side Condition 4 admits on the three-step net Figure 6 opens at, as a bound.

    Figure 6 says the coarsest net it offers admits only `B` below this; the value is
    `1/(1 + D_3)` for that net's widest half-gap, rounded up so that `B` below the stated
    figure is what the reader needs and no more.
    """
    tangents = tuple(facts.angle_limit * k / 3 for k in range(4))
    gap, _ = largest_admissible_side(tangents)
    return ceiled(1 / (1 + gap), 4)


def coarsening_verdict(rows: list[CoarseningRow] | None) -> str:
    """The sentence under Figure 7's bars, read off the rows' own pass flags."""
    if not rows:
        return ""
    passing = [index for index, row in enumerate(rows) if bool(row["passes"])]
    if passing == [len(rows) - 1]:
        return "Only the last bar clears the threshold."
    if passing == list(range(len(rows))):
        return "Every bar clears the threshold."
    if passing and passing == list(range(passing[0], len(rows))):
        return f"The bars from K = {rows[passing[0]]['K']} on clear the threshold."
    raise SystemExit("the net-coarsening rows pass in no order the figure's sentence can state")


# The check is about fetches, not about outward addresses, and the two came apart
# when the page gained a link preview. `rel="canonical"` is the only `<link>` a
# browser does not act on: it is a statement to a crawler about which URL this
# document is, read from the markup and never resolved or requested while the page
# is being viewed, so a page carrying one still opens from a file with the network
# off. Every other `<link ... href=>` -- a stylesheet, an icon, a preload, a
# manifest -- is a fetch and is still refused, and the exemption is written as the
# exact quoted form the shell emits so nothing broader slips through it. The
# `og:*` and `twitter:*` URLs need no exemption: they are `<meta content=>`, which
# this pattern has never matched, and are likewise read rather than fetched.
EXTERNAL_REFERENCE = re.compile(
    r"<script[^>]*\ssrc="
    r'|<link(?![^>]*\srel="canonical")[^>]*\shref='
    r"|@import\b"
    r"|url\((?!\s*[\"']?(?:data:|#))",
    re.IGNORECASE,
)


def assert_self_contained(page: str) -> None:
    """Refuse a page that would fetch anything at view time.

    The page inlines kpress's faces and the KaTeX distribution as data URIs and is
    meant to open from a file with the network off. A script or stylesheet element
    with a source, a CSS import, or a `url()` that is not a data URI or a fragment
    is a fetch, so the render refuses it rather than leaving it to a grep in CI.

    Metadata is not a fetch. The canonical link and the link-preview `<meta>` tags
    carry absolute URLs on purpose -- a crawler has no base to resolve a relative one
    against -- and no browser requests any of them to display the page.
    """
    hit = EXTERNAL_REFERENCE.search(page)
    if hit:
        start = max(hit.start() - 40, 0)
        excerpt = page[start : hit.end() + 60]
        raise SystemExit(f"the page is not self-contained: ...{excerpt}...")


def slug(facts: Facts) -> str:
    """The certificate's outer side as an id fragment and hash: `19-5`, `381-100`."""
    return f"{facts.outer_side.numerator}-{facts.outer_side.denominator}"


def claim_path(facts: Facts) -> Path:
    """The certificate's verifiable-claim document, one self-contained file beside it."""
    return CASE / f"{RESULT_ID}-verifiable-claim-{slug(facts)}.md"


# The claim verifier's whole decision, `python verify_claim.py <certificate>`,
# timed on 2026-09-04 on an Apple Silicon laptop under CPython 3.14: what the claim
# documents and the page promise a reader. A certificate not measured here gets no
# promise, and the page drops its list of claims rather than guess one.
MEASURED_SECONDS = {"19-5": 36, "381-100": 175}


def runtime_phrase(facts: Facts) -> str:
    """How long the claim verifier takes, said loosely.

    'about half a minute', 'about 3 minutes': loose on purpose, since the reader's
    machine is not this one.
    """
    seconds = MEASURED_SECONDS.get(slug(facts))
    if seconds is None:
        raise SystemExit(f"{facts.source.name}: the minimal verifier has not been timed on it")
    if seconds < 45:
        return "about half a minute"
    if seconds < 90:
        return "about a minute"
    return f"about {round(seconds / 60)} minutes"


def claim_substitutions(headline: Facts, default: Facts) -> dict[str, str]:
    """What each certificate is, named by the role it plays rather than by its bound.

    The page states the size of a certificate in two places that are not inside its own
    article -- the opening summary, which describes the headline proof before either
    article begins, and the list of claim documents, which states both at once. Neither
    can use the per-certificate values, so both read these; the counts are the same
    quantities `certificate_substitutions` derives, taken from the same facts.
    """
    values = {}
    for role, f in (("DEFAULT", default), ("HEADLINE", headline)):
        values[f"{role}_CLAIM_NAME"] = claim_path(f).name
        values[f"{role}_CLAIM_URL"] = repo_file(claim_path(f))
        values[f"{role}_N_ATOMS"] = f"{len(f.atoms):,}"
        values[f"{role}_N_DIRECTIONS"] = str(f.steps + 1)
        values[f"{role}_RUNTIME"] = runtime_phrase(f)
    return values


#: The deck, which the hero sets under the title and the card repeats after it.
SUBTITLE = "A New Lower Bound on the Square Packing Problem"


def card_substitutions(headline: Facts, headline_frac: str) -> dict[str, str]:
    """What a link preview shows: the title, the sentence, the canonical URL, the image.

    Every one of these is a string the page already states somewhere -- the title in
    `<title>`, the sentence in `<meta name="description">`, the picture in Figure 1 --
    and each is built here once and substituted into both places, so a shared link and
    the page it opens cannot say different things. The bound in the title and in the
    sentence is the headline certificate's own, like every other number on the page.

    The card names the composite because that is the picture of the result: a portrait
    at 150:181. X and Facebook centre-crop it to their landscape card and show the
    middle four rows of the grid; Slack, Discord and iMessage scale the whole thing and
    show all hundred packings with the title on it. Both readings are of the atlas, so
    the aspect is left alone rather than a landscape variant being derived for the
    croppers at the cost of the ones that do not crop.
    """
    width, height = png_size(COMPOSITE_PNG)
    title = f"s({headline.n}) ≥ {headline_frac}: {SUBTITLE}"
    description = (
        f"How a weighted point set and a pigeonhole prove s({headline.n}) ≥ "
        f"{headline_frac}, apparently the first improvement in "
        f"{RESULT_YEAR - PRIOR_YEAR} years on the smallest open case of the "
        "square packing problem."
    )
    return {
        "PAGE_TITLE": title,
        "PAGE_DESCRIPTION": description,
        "CANONICAL_URL": SITE_URL,
        "SITE_NAME": SITE_NAME,
        "CARD_IMAGE_URL": site_file(COMPOSITE_PNG),
        "CARD_IMAGE_WIDTH": str(width),
        "CARD_IMAGE_HEIGHT": str(height),
        "COMPOSITE_ALT": COMPOSITE_ALT,
    }


def shared_substitutions(facts: list[Facts], headline: Facts, default: Facts) -> dict[str, str]:
    """Values the whole page states: the headline bound, the deck, the shared axis.

    The axis positions are here rather than in `certificate_substitutions`
    because the bounds figure states every certificate at once and stands outside
    the stamped article; the band it shades runs from the headline bound to the
    best packing known, which is what remains unknown after all of them.
    """
    headline_frac = f"{headline.outer_side.numerator}/{headline.outer_side.denominator}"
    return {
        "BELOW_ONE": BELOW_ONE,
        "NEAR_LIMIT": NEAR_LIMIT,
        "N": str(headline.n),
        "HEADLINE_L_FRAC": headline_frac,
        "HEADLINE_L_DEC": decimal(headline.outer_side),
        "SUBTITLE": SUBTITLE,
        **card_substitutions(headline, headline_frac),
        "DEFAULT_L_FRAC": f"{default.outer_side.numerator}/{default.outer_side.denominator}",
        "DEFAULT_ID": default.identifier,
        # Print shows one certificate deterministically, and this names which.
        "DEFAULT_SLUG": slug(default),
        "DEFAULT_CERT_URL": repo_file(default.source),
        "YEARS_SINCE_PRIOR": str(RESULT_YEAR - PRIOR_YEAR),
        "N_RESULTS": str(registered_results()),
        "N_STARRED": str(starred_lower_bounds()),
        "SOURCE_URL": MARKDOWN_OUTPUT.name,
        "REPO_URL": REPO_URL,
        "PUBLISHED": PUBLICATION_DATE,
        "EDITION": PUBLICATION_EDITION,
        "REVISION": PUBLICATION_REVISION,
        "PRIOR_YEAR": str(PRIOR_YEAR),
        **bound_substitutions(),
        "PRIOR_SOURCE": PRIOR_SOURCE,
        "PRIOR_URL": PRIOR_URL,
        "PROBLEM_URL": PROBLEM_URL,
        "BEST_URL": BEST_URL,
        "BEST_SOURCE": BEST_SOURCE,
        "BEST_RENDER_URL": repo_file(BEST_RENDERING),
        "TRUMP_SVG": best_packing_svg(),
        "NUMBER_LINE_MARKS": number_line_marks(facts, headline),
        "PRIOR_X": f"{line_x(float(PRIOR_LOWER)):.0f}",
        "BEST_X": f"{line_x(float(BEST_PACKING)):.0f}",
        "BAND_X": f"{line_x(float(headline.outer_side)):.0f}",
        "BAND_W": f"{line_x(float(BEST_PACKING)) - line_x(float(headline.outer_side)):.0f}",
    }


def shell_substitutions(static: Path, shared: dict[str, str], body: str) -> dict[str, str]:
    """Values for the page shell: the inlined assets and the rendered body.

    `BODY_HTML` goes in last, after every other value: it is already substituted
    through, and a later key must not reach inside it.
    """
    return {
        "KPRESS_CSS": kpress_css(static) + katex_css(static),
        "THEME_BOOTSTRAP": theme_bootstrap(static),
        "KATEX_JS": (static / "katex" / "katex.min.js").read_text(encoding="utf-8"),
        "KPRESS_CLIENT_JS": kpress_client_js(static),
        **shared,
        "BODY_HTML": body,
    }


def certificate_switch(facts: list[Facts], headline: Facts) -> str:
    """The switch every figure head carries: one button per certificate."""
    buttons = []
    for f in facts:
        rank = "Tighter" if f is headline else "Looser"
        bound = f"{f.outer_side.numerator}/{f.outer_side.denominator}"
        buttons.append(
            f'<button type="button" data-cert="{slug(f)}" aria-pressed="false">'
            f"{rank}: s({f.n}) ≥ {bound}</button>"
        )
    return (
        '<span class="cert-toggle" role="group" aria-label="Certificate">'
        + "".join(buttons)
        + "</span>"
    )


def certificate_substitutions(facts: Facts, *, default: Facts, toggle: str) -> dict[str, str]:
    """Values for one certificate's article, switch and script."""
    n = facts.n
    total = facts.total_mass
    shortfall = n - total
    # Each of these two is a distance from an irrational, so each is a
    # truncation of one and goes out with the ellipsis that says so.
    gap_now = BEST_PACKING - facts.outer_side
    gap_before = BEST_PACKING - PRIOR_LOWER
    margin = facts.least_mass - 1
    rows = coarsening_rows(facts)
    verdict = coarsening_verdict(rows)
    if rows:
        bars, values, labels = coarsening_svg(rows)
        alt = "Least covered mass against net size: " + ", ".join(
            f"K={row['K']} gives {decimal_or_rational(row_mass(row))}" for row in rows
        )
        halving_b, halving_mass = halving_cost(rows)
    else:
        bars = values = labels = alt = ""
        halving_b = halving_mass = ""
    return {
        "SLUG": slug(facts),
        "CERT_TOGGLE": toggle,
        "ATOMS": atom_array(facts),
        "ID": facts.identifier,
        "N": str(n),
        "N_ATOMS": f"{len(facts.atoms):,}",
        "N_ORBITS": str(facts.orbits),
        "N_DIRECTIONS": str(facts.steps + 1),
        "N_DIRECTIONS_MAX": str(facts.steps),
        "LIMIT_NUM": str(facts.angle_limit.numerator),
        "LIMIT_DEN": str(facts.angle_limit.denominator),
        "N_WEIGHTS": str(facts.distinct_weights),
        "L_FRAC": f"{facts.outer_side.numerator}/{facts.outer_side.denominator}",
        "L_DEC": decimal(facts.outer_side),
        "L_JS": repr(float(facts.outer_side)),
        "SHRINK_PEAK_TEX": shrink_peak_tex(facts, facts.admitted_side),
        "SHRINK_PEAK_CERT_TEX": shrink_peak_tex(facts, facts.square_side),
        "K3_LIMIT_TEX": k3_limit_tex(facts),
        "TIGHT_PERCENT": str((TIGHT - 1) * 100),
        "TIGHT_JS": decimal(TIGHT),
        "B_JS": repr(float(facts.square_side)),
        "TOTAL_TEX": frac_tex(total),
        "TOTAL_DEC": decimal(total),
        "TOTAL_PLAIN": f"{total.numerator}/{total.denominator}",
        "SHORTFALL": decimal(shortfall),
        "LEAST_TEX": frac_tex(facts.least_mass),
        "LEAST_TEX_PLAIN": f"{facts.least_mass.numerator}/{facts.least_mass.denominator}",
        "LEAST_DEC": decimal(facts.least_mass),
        "LEAST_MARGIN": f"{(margin * facts.weight_scale).numerator:,}",
        "SCALE": f"1/{facts.weight_scale}",
        "SCALE_JS": str(facts.weight_scale),
        # Weights are whole multiples of 1/weight_scale, so they terminate; the
        # narrowest one on the 381/100 certificate needs all six places, and
        # the five the page used to print made it 0.00008.
        "WEIGHT_MIN": decimal_or_rational(min(a.weight for a in facts.atoms)),
        "WEIGHT_MAX": decimal_or_rational(max(a.weight for a in facts.atoms)),
        "WITNESS_X_JS": f"{facts.witness[0].numerator}/{facts.witness[0].denominator}",
        "WITNESS_Y_JS": f"{facts.witness[1].numerator}/{facts.witness[1].denominator}",
        **bound_substitutions(),
        "PRIOR_SOURCE": PRIOR_SOURCE,
        "PRIOR_URL": PRIOR_URL,
        "BEST_SOURCE": BEST_SOURCE,
        "BEST_URL": BEST_URL,
        "DEFAULT_L_FRAC": f"{default.outer_side.numerator}/{default.outer_side.denominator}",
        "CERT_URL": repo_file(facts.source),
        "RENDERER_URL": repo_file(Path(__file__).resolve()),
        "VERIFIER_URL": repo_file(VERIFIER),
        "GENERATOR_URL": repo_file(GENERATOR),
        "THIRDPARTY_URL": repo_file(THIRDPARTY),
        "GAP_NOW": truncated(gap_now, tex=True),
        "GAP_BEFORE": truncated(gap_before, tex=True),
        "HALVING_B_DROP": halving_b,
        "HALVING_MASS_DROP": halving_mass,
        "COARSEN_ALT": alt,
        "COARSEN_BARS": bars,
        "COARSEN_VALUES": values,
        "COARSEN_LABELS": labels,
        "COARSEN_VERDICT": verdict,
    }


def fill(block: str, values: dict[str, str], *, where: str) -> str:
    """Substitute every placeholder in a block, refusing one that has no value."""
    missing = {m.group(1) for m in re.finditer(r"\{\{([A-Z_]+)\}\}", block)} - values.keys()
    if missing:
        raise SystemExit(f"{where}: template placeholders with no value: {sorted(missing)}")
    for key, value in values.items():
        block = block.replace(f"{{{{{key}}}}}", value)
    left = sorted({m.group(1) for m in re.finditer(r"\{\{([A-Z_]+)\}\}", block)})
    if left:
        raise SystemExit(f"{where}: a value carried placeholders into the page: {left}")
    return block


def drop_block(text: str, name: str) -> str:
    """Remove a marked block and its markers, wherever it stands; a no-op if absent."""
    return re.sub(rf"<!--BEGIN:{name}-->.*?<!--END:{name}-->", "", text, flags=re.DOTALL)


def wrap_figure(body: str, cert: str) -> str:
    """One certificate's copy of a figure, in a wrapper the switch can hide.

    The blank line on each side of the two wrapper tags is load-bearing: a
    Markdown HTML block runs to the next blank line, so a wrapper pressed
    against a paragraph would swallow it into the raw block and leave its
    Markdown unrendered.
    """
    return (
        f'\n<div class="cert-figure" data-cert="{cert}" hidden>\n\n{body.strip()}\n\n</div>\n\n'
    )


def expand(
    source: str, name: str, per_certificate: list[dict[str, str]], *, article: bool
) -> str:
    """Repeat a marked block once per certificate, in order, filled for each.

    The article and its script are each one block, written once with `{{SLUG}}`
    in every id, and this stamps them out: the article into the Markdown source,
    the script into the shell. A certificate with no matching net-coarsening
    measurement loses that figure rather than borrowing another's numbers.
    """
    pattern = re.compile(rf"<!--BEGIN:{name}-->(.*?)<!--END:{name}-->", re.DOTALL)
    if pattern.search(source) is None:
        raise SystemExit(f"there is no {name} block to stamp")

    def stamp(match: re.Match[str]) -> str:
        block = match.group(1)
        copies = []
        for values in per_certificate:
            # The coarsening figure belongs to a measured certificate; a
            # certificate without a measurement has no copy of it.
            if "{{COARSEN_BARS}}" in block and not values["COARSEN_BARS"]:
                continue
            copy = fill(block, values, where=f"{name} {values['SLUG']}")
            copies.append(wrap_figure(copy, values["SLUG"]) if article else copy)
        return "".join(copies)

    return pattern.sub(stamp, source)


# Comments in the Markdown source — the contract note at its head, the block
# markers this file reads, any working annotation — belong to the source and not
# to the reader, so none of them reach the page.
_HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


#: A function name set in italic leans into the parenthesis that follows it, so `s(n)`
#: sets the bracket against the letter's terminal. One mu, a thousandth of an em quad,
#: is the smallest space TeX offers and is what the drawn figures use as an offset.
#: Applied wherever the page sets mathematics so the spacing is the same in the prose,
#: the captions and the drawings.
_FUNCTION_APPLICATION = re.compile(r"(?<![A-Za-z\\])([a-z])\(")


def kerned_math(source: str) -> str:
    """Put a thin space between a one-letter function name and its parenthesis."""
    return _FUNCTION_APPLICATION.sub(r"\1\\mkern1mu(", source)


def kerned_math_spans(source: str) -> str:
    """Apply that spacing inside every `$...$` span, and nowhere else.

    Markdown prose is full of parentheses that follow a letter; only the maths is
    typeset, so only the maths is touched.
    """
    return re.sub(
        r"(?<!\\)(\$\$?)(.+?)(?<!\\)\1",
        lambda m: f"{m.group(1)}{kerned_math(m.group(2))}{m.group(1)}",
        source,
        flags=re.DOTALL,
    )


#: Where the published Markdown is written, beside the page it is the source of. Named
#: for the result the way a case-local document is: what a file is called does not
#: depend on which directory it is served from.
MARKDOWN_OUTPUT = PACKING / "site" / f"{RESULT_ID}-explainer.md"


def _balanced(source: str, start: int, tag: str) -> int:
    """The index just past the `</tag>` that closes the `<tag` opening at `start`."""
    depth = 0
    position = start
    opening = f"<{tag}"
    closing = f"</{tag}>"
    while position < len(source):
        next_open = source.find(opening, position)
        next_close = source.find(closing, position)
        if next_close == -1:
            raise SystemExit(f"{MARKDOWN.name}: an unclosed <{tag}> reached the publisher")
        if next_open != -1 and next_open < next_close:
            depth += 1
            position = next_open + len(opening)
            continue
        depth -= 1
        position = next_close + len(closing)
        if depth == 0:
            return position
    raise SystemExit(f"{MARKDOWN.name}: an unclosed <{tag}> reached the publisher")


_TEX_SPAN = re.compile(r'<span class="tex">(.*?)</span>', re.DOTALL)
_SCREEN_ONLY = re.compile(r'<span class="screen-only">.*?</span>', re.DOTALL)
_ANCHOR = re.compile(r'<a\s[^>]*?href="([^"]*)"[^>]*>(.*?)</a>', re.DOTALL)
_IMG = re.compile(r"<img\s[^>]*>")
_ATTRIBUTE = re.compile(r'(\w[\w-]*)="([^"]*)"')
_SIMPLE_TAG = re.compile(r"</?(?:strong|b|em|i|code|span|br)\b[^>]*>")


def _inline_markdown(fragment: str) -> str:
    """Inline HTML the article uses inside a caption, written as Markdown instead."""
    fragment = _SCREEN_ONLY.sub("", fragment)
    fragment = _TEX_SPAN.sub(lambda m: f"${m.group(1).strip()}$", fragment)
    fragment = _ANCHOR.sub(
        lambda m: f"[{_inline_markdown(m.group(2))}]({m.group(1)})", fragment
    )
    for opening, closing, mark in (("<strong>", "</strong>", "**"), ("<b>", "</b>", "**")):
        fragment = fragment.replace(opening, mark).replace(closing, mark)
    for opening, closing, mark in (("<em>", "</em>", "*"), ("<i>", "</i>", "*")):
        fragment = fragment.replace(opening, mark).replace(closing, mark)
    fragment = fragment.replace("<code>", "`").replace("</code>", "`")
    fragment = _SIMPLE_TAG.sub("", fragment)
    return re.sub(r"[ \t]*\n[ \t]*", " ", fragment).strip()


def _image_markdown(tag: str) -> str:
    attributes = dict(_ATTRIBUTE.findall(tag))
    return f"![{attributes.get('alt', '').strip()}]({attributes.get('src', '')})"


def published_markdown(source: str, *, default_slug: str) -> str:
    """The article as a document, for a reader or a model rather than for a browser.

    The page and this file say the same things; they differ in what they can do. A
    canvas the reader drags, a panel of controls, a chooser between certificates and a
    drawn diagram are all apparatus, and none of it survives as text. What the figures
    mean is in their captions, so a figure here is its caption, plus its image where the
    image is a file rather than markup.

    Two reductions beyond that. The page carries one copy of every figure per retained
    certificate and switches between them, which as text would read as the same figure
    stated twice; only the certificate the page opens on is kept. And the chip row is
    navigation, whose one purpose is to offer this file.
    """
    kept = f'<div class="cert-figure" data-cert="{default_slug}"'
    while (start := source.find('<div class="cert-figure"')) != -1:
        end = _balanced(source, start, "div")
        block = source[start:end]
        if not block.startswith(kept):
            source = source[:start] + source[end:]
            continue
        inner = block[block.index(">") + 1 : -len("</div>")]
        source = source[:start] + inner + source[end:]

    for opening in ('<div class="doc-links', '<div class="fig-choose"'):
        while (start := source.find(opening)) != -1:
            source = source[:start] + source[_balanced(source, start, "div") :]

    out: list[str] = []
    position = 0
    while (start := source.find("<figure", position)) != -1:
        end = _balanced(source, start, "figure")
        block = source[start:end]
        out.append(source[position:start])
        images = [_image_markdown(tag) for tag in _IMG.findall(block)]
        caption = re.search(r"<figcaption>(.*?)</figcaption>", block, re.DOTALL)
        parts = [*images]
        if caption:
            parts.append(_inline_markdown(caption.group(1)))
        out.append("\n\n".join(part for part in parts if part))
        position = end
    out.append(source[position:])
    source = "".join(out)

    source = _IMG.sub(lambda m: _image_markdown(m.group(0)), source)

    # The credits are one span per line inside a div. As a list they survive the
    # formatter, which would otherwise run four separate facts into one paragraph.
    def _credits(match: re.Match[str]) -> str:
        items = re.findall(r"<span>(.*?)</span>", match.group(1), re.DOTALL)
        return "\n".join(f"- {_inline_markdown(item)}" for item in items)

    source = re.sub(r'<div class="credits">(.*?)</div>', _credits, source, flags=re.DOTALL)
    # Every remaining div is a named block whose name is a style. The content is the
    # document; the box around it is the page's.
    source = re.sub(r"</?div\b[^>]*>", "", source)
    source = re.sub(r"</?p\b[^>]*>", "", source)
    source = _inline_markdown_document(source)
    source = re.sub(r"\n{3,}", "\n\n", source).strip() + "\n"

    # Formatted by the same tool that owns every other Markdown file here, so the
    # published document wraps the way the repository's prose does. It has to run in
    # process: the Makefile drives the Rust build through `uvx`, and a network fetch
    # inside the page build would make the deploy depend on an index being reachable.
    # `flowmark` is the Python build of the same formatter, pinned in the dev group.
    from flowmark import reformat_text  # noqa: PLC0415

    return reformat_text(source, semantic=True, cleanups=True)


def _inline_markdown_document(source: str) -> str:
    """`_inline_markdown` over a whole document, line structure intact.

    The caption form collapses its input to one line, which is right for a caption and
    wrong for prose, so the paragraph shape is preserved by running the conversion
    within each line rather than over the whole string.
    """
    return "\n".join(
        _inline_markdown(line) if line.strip() else "" for line in source.split("\n")
    )


def markdown_source(
    per_certificate: list[dict[str, str]],
    headline_values: dict[str, str],
    shared: dict[str, str],
    *,
    claimed: bool,
) -> str:
    """The article's Markdown with every value filled in: what the page is made of.

    Split out from the render because it is an artifact in its own right, not just an
    intermediate. The template is not publishable -- it carries `{{PLACEHOLDERS}}`, so
    it states no bound and names no number -- and this is the same document with the
    certificate's own values in it.

    The maths is left unkerned here. `kerned_math_spans` inserts `\\mkern1mu` so KaTeX
    does not set an italic function name against its parenthesis, which is a fact about
    typesetting and not about the mathematics; a reader, or a model, reading this file
    should see `s(11)`.
    """
    source = MARKDOWN.read_text(encoding="utf-8")
    if not claimed:
        source = drop_block(source, "CLAIM")
    unmeasured = [v["SLUG"] for v in per_certificate if not v["COARSEN_BARS"]]
    if unmeasured:
        # Figure 7 is stamped per certificate and switched with the others, so a
        # page where one certificate lacks its measurement would show a figure
        # that vanishes on a switch; the section waits for the measurement.
        print(f"no net-coarsening measurement for {', '.join(unmeasured)}; dropping Figure 7")
        source = drop_block(source, "COARSENING")
    source = expand(source, "FIGURE", per_certificate, article=True)
    source = fill(
        _HTML_COMMENT.sub("", source), {**headline_values, **shared}, where=MARKDOWN.name
    )
    left = {m.group(1) for m in re.finditer(r"\{\{([A-Z_]+)\}\}", source)}
    if left:
        raise SystemExit(f"{MARKDOWN.name}: a substituted value carried {sorted(left)} into it")
    return source


def markdown_body(source: str, *, title: str) -> str:
    """The page body: the Markdown source assembled, then rendered once by kpress.

    Order matters twice. The figures are stamped before anything is
    substituted, so each copy is filled with its own certificate's values, and
    the pass that follows fills the prose once, with the headline certificate's
    values and the shared ones. And every placeholder is
    substituted before the Markdown is parsed, because markdown-it
    percent-encodes a link destination: `[computed]({{RENDERER_URL}})` parsed
    first would leave `href="%7B%7B..."` behind.
    """
    source = kerned_math_spans(source)

    from kpress.format.markdown import parse_markdown  # noqa: PLC0415

    document = parse_markdown(
        source,
        title=title,
        trust_mode="trusted",
        math="auto",
    )
    refused = [d for d in document.diagnostics if d.severity == "error"]
    for diagnostic in document.diagnostics:
        print(f"{MARKDOWN.name}: {diagnostic.severity}: {diagnostic.message}", file=sys.stderr)
    if refused:
        raise SystemExit(f"{MARKDOWN.name} did not render cleanly; refusing to write the page")
    return document.html


class Render(NamedTuple):
    """What one render produces: the page, and the document it is made of."""

    page: str
    markdown: str


def render(certificate_paths: tuple[Path, ...], *, full_sweep: bool = False) -> Render:
    """One page for every certificate given, the first shown by default."""
    if not certificate_paths:
        raise SystemExit("no certificate to render")
    facts = [derive(path, full_sweep=full_sweep) for path in certificate_paths]
    if len({f.n for f in facts}) != 1:
        raise SystemExit("the certificates on one page must all be for the same n")
    if len({slug(f) for f in facts}) != len(facts):
        raise SystemExit("two certificates share an outer side; their ids would collide")
    headline = max(facts, key=lambda f: f.outer_side)
    toggle = certificate_switch(facts, headline)
    per_certificate = [
        certificate_substitutions(f, default=facts[0], toggle=toggle) for f in facts
    ]

    shared = shared_substitutions(facts, headline, facts[0])
    claimed = all(claim_path(f).is_file() and slug(f) in MEASURED_SECONDS for f in facts)
    if claimed:
        shared.update(claim_substitutions(headline, facts[0]))
    else:
        print("a certificate lacks a claim document or a timing; the page drops that section")
    static = kpress_static()
    headline_values = per_certificate[facts.index(headline)]
    source = markdown_source(per_certificate, headline_values, shared, claimed=claimed)
    prose = markdown_body(source, title=f"s({shared['N']}) >= {shared['HEADLINE_L_FRAC']}")
    # The sprite leads the body the way kpress's own renderer places it: the copy
    # button on a code block draws its glyph from a fragment of it.
    body = f"{icon_sprite(static)}\n{prose}"
    shell = expand(
        TEMPLATE.read_text(encoding="utf-8"), "SCRIPT", per_certificate, article=False
    )
    page = fill(shell, shell_substitutions(static, shared, body), where=TEMPLATE.name)
    assert_self_contained(page)
    return Render(page=page, markdown=published_markdown(source, default_slug=slug(facts[0])))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--certificate",
        type=Path,
        action="append",
        help="a certificate to explain; repeatable, first is shown by default "
        "(default: the retained 19/5 and 381/100 certificates for n = 11)",
    )
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero if the committed page differs from a fresh render",
    )
    parser.add_argument(
        "--verify-condition-5",
        action="store_true",
        help="sweep every direction before rendering; the case replay gate decides the same "
        "condition, so this is for a release build rather than an edit loop",
    )
    args = parser.parse_args(argv)

    # Paths are resolved here, once: a relative `--certificate` or `--output`
    # used to render the whole page and then fail on `relative_to`.
    output = args.output.resolve()
    label = output.relative_to(REPO).as_posix() if output.is_relative_to(REPO) else str(output)
    certificates = (
        tuple(path.resolve() for path in args.certificate) if args.certificate else WALKTHROUGH
    )
    rendered = render(certificates, full_sweep=args.verify_condition_5)
    document = output.parent / MARKDOWN_OUTPUT.name
    written = ((output, rendered.page), (document, rendered.markdown))
    if args.check:
        for path, content in written:
            name = path.relative_to(REPO).as_posix() if path.is_relative_to(REPO) else str(path)
            if not path.is_file():
                print(f"{name} has not been rendered", file=sys.stderr)
                return 1
            if path.read_bytes() != content.encode("utf-8"):
                print(f"{name} is stale; rerender it", file=sys.stderr)
                return 1
        print(f"{label} is current")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    for path, content in written:
        with atomic_output_file(path) as temporary:
            temporary.write_text(content, encoding="utf-8")
    for asset in COMPOSITE_ASSETS:
        shutil.copyfile(asset, output.parent / asset.name)
    print(f"wrote {label} ({len(rendered.page) / 1024:.0f} KB)")
    name = document.relative_to(REPO).as_posix()
    print(f"wrote {name} ({len(rendered.markdown) / 1024:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
