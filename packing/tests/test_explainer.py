"""The explainer renders, and what it renders fetches nothing.

`devtools.render_explainer` was exercised only by the Pages workflow, on the pull
requests whose paths its filters name; nothing in the suite rendered the page. A full
render is under a second, so it runs here, and the two properties the workflow used to
grep for are asserted on the string the renderer returns: no placeholder survived
substitution, and nothing in the page is a reference outside it.
"""

from __future__ import annotations

import re

import pytest

from devtools.render_explainer import (
    CASE,
    COMPOSITE_ASSETS,
    COMPOSITE_PNG,
    MARKDOWN_OUTPUT,
    RESULT_ID,
    SITE_URL,
    WALKTHROUGH,
    assert_self_contained,
    png_size,
    render,
)
from devtools.render_explainer import load_certificate as load


@pytest.fixture(scope="module")
def rendered():
    return render(WALKTHROUGH)


@pytest.fixture(scope="module")
def page(rendered) -> str:
    return rendered.page


@pytest.fixture(scope="module")
def document(rendered) -> str:
    return rendered.markdown


def test_the_page_renders_every_walkthrough_certificate(page: str) -> None:
    """Each certificate's slug is in the page: its switch button and its figure copies."""

    for path in WALKTHROUGH:
        certificate, _ = load(path)
        fragment = f"{certificate.outer_side.numerator}-{certificate.outer_side.denominator}"
        assert f'data-cert="{fragment}"' in page, fragment


def test_no_placeholder_survives_substitution(page: str) -> None:
    assert re.findall(r"\{\{[A-Z_]+\}\}", page) == []


def test_the_page_is_self_contained(page: str) -> None:
    """The renderer's own check passes on its own output; the workflow relies on this.

    The page carries exactly one `<link>`, and it is the canonical URL. That is not a
    fetch -- a browser reads it and does not request it -- but it is the one element in
    the head that could become one, so it is counted rather than merely permitted: a
    second `<link>` arriving here is a stylesheet, an icon or a preload, and the count
    fails before the refusal has to.
    """

    assert_self_contained(page)
    assert re.findall(r"<link[^>]*>", page) == [f'<link rel="canonical" href="{SITE_URL}">']
    assert re.search(r"<script[^>]*\ssrc=", page) is None


@pytest.mark.parametrize(
    "fragment",
    [
        '<script src="https://cdn.example/x.js"></script>',
        '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=X">',
        "<style>@import url(https://example.org/a.css);</style>",
        "<style>body { background: url(https://example.org/a.png) }</style>",
        "<style>body { background: url('//example.org/a.png') }</style>",
        # The canonical exemption is the exact quoted form the shell emits and nothing
        # wider: every other rel is still a fetch, and a rel that merely contains the
        # word does not buy its way past.
        '<link rel="preload" as="font" href="https://example.org/a.woff2">',
        '<link rel="icon" href="https://example.org/favicon.png">',
        '<link rel="canonical stylesheet" href="https://example.org/a.css">',
        "<link rel=canonical href=https://example.org/>",
    ],
)
def test_an_external_reference_is_refused(fragment: str) -> None:
    with pytest.raises(SystemExit, match="not self-contained"):
        assert_self_contained(f"<html><body>{fragment}</body></html>")


@pytest.mark.parametrize(
    "fragment",
    [
        "<style>@font-face { src: url(data:font/woff2;base64,AAAA) }</style>",
        "<style>.a { fill: url(#gradient) }</style>",
        '<style>.b { background: url("data:image/svg+xml,%3Csvg%3E") }</style>',
        # Metadata for a crawler, read off the markup and never requested to display
        # the page. Both forms are outward addresses on purpose: a preview consumer
        # resolves them on its own machine and drops a relative one.
        '<link rel="canonical" href="https://jlevy.github.io/squares/">',
        '<meta property="og:image" content="https://jlevy.github.io/squares/a.png">',
    ],
)
def test_a_data_uri_or_fragment_is_not_a_fetch(fragment: str) -> None:
    assert_self_contained(f"<html><body>{fragment}</body></html>")


def test_the_published_document_is_markdown_and_not_the_template(document: str) -> None:
    """The chip offers this file, so it has to be the article rather than its source.

    The template states no bound: every number in it is a `{{PLACEHOLDER}}`, and the
    chip used to link to it. What is published is the same document with the
    certificate's own values in place, and it has to survive being read as text.
    """
    assert "{{" not in document
    assert "3.81" in document
    assert "1,121" in document
    assert "181" in document
    assert document.startswith("# s(11)")


def test_the_published_document_carries_no_html(document: str) -> None:
    """A canvas, a control panel and a drawn diagram are apparatus, not prose.

    None of them means anything in a text file, and together they were seventy per cent
    of the bytes. What a figure says is in its caption, so a figure here is its caption.
    """
    assert not re.search(r"</?[a-zA-Z][^>]*>", document)
    for number in (1, 3):
        assert f"**Figure {number}." in document


def test_the_published_document_states_each_figure_once(document: str) -> None:
    """The page carries a copy per certificate and switches between them; text cannot.

    Stating the same figure twice, once per certificate, reads as a duplication rather
    than as a choice, so only the certificate the page opens on is kept.
    """
    # A caption's bold lead carries the figure's own subtitle, so it is matched by
    # its number rather than by an exact string.
    for number in range(1, 8):
        assert document.count(f"**Figure {number}.") == 1, number


def test_the_published_document_sets_mathematics_without_typesetting_kerns(
    document: str,
) -> None:
    """`\\mkern1mu` is how KaTeX is told not to set `s` against `(`, and nothing more.

    It is a fact about typesetting, not about the mathematics, and a reader or a model
    taking this file should see `s(11)`.
    """
    assert "mkern" not in document
    assert "$s(11)$" in document or "s(11)" in document


#: Every `og:` and `twitter:` tag in the head, by name. Both vocabularies spell a tag
#: the same way and differ only in the attribute that carries the name -- Open Graph is
#: `property`, the Twitter tags are `name` -- so one pattern reads them together.
CARD_TAG = re.compile(r'<meta (?:property|name)="((?:og|twitter):[^"]+)" content="([^"]*)"')

#: What a card is: the tags without which a consumer shows something worse than the
#: page asked for. `og:image:type` is deliberately not here -- it is a hint, and a
#: consumer that ignores it still renders the card.
REQUIRED_CARD_TAGS = frozenset(
    {
        "og:type",
        "og:site_name",
        "og:title",
        "og:description",
        "og:url",
        "og:image",
        "og:image:width",
        "og:image:height",
        "og:image:alt",
        "twitter:card",
        "twitter:title",
        "twitter:description",
        "twitter:image",
        "twitter:image:alt",
    }
)


def card_tags(page: str) -> dict[str, str]:
    return dict(CARD_TAG.findall(page))


def test_the_link_preview_is_complete_and_its_urls_are_absolute(page: str) -> None:
    """A shared link previews with the atlas, or it previews with nothing.

    The page shipped with four `<meta>` tags, a title and a description and no card at
    all, so every unfurl of it -- X, Slack, Discord, Facebook, iMessage -- was a line of
    text on a blank rectangle. What makes a card is the set together rather than any one
    tag: a consumer that finds `og:image` and no `twitter:card` falls back to a
    thumbnail, and one that finds a relative `og:image` drops the image outright,
    because a crawler resolves it on its own machine and has no base to resolve
    against. Both are pinned here, since neither failure shows up in the page itself:
    a card is only ever seen somewhere else.
    """
    tags = card_tags(page)
    assert tags.keys() >= REQUIRED_CARD_TAGS, sorted(REQUIRED_CARD_TAGS - tags.keys())
    for key in ("og:url", "og:image", "twitter:image"):
        assert tags[key].startswith("https://"), (key, tags[key])
    assert f'<link rel="canonical" href="{SITE_URL}">' in page
    assert tags["og:url"] == SITE_URL


def test_the_card_image_is_one_the_render_serves_beside_the_page(page: str) -> None:
    """The card names a file the deploy actually publishes, at the size it actually is.

    Two ways a card breaks without the page changing at all. The image URL can name
    something the render does not copy into the site directory, which is a 404 a
    consumer answers by showing no image; and the declared width and height can drift
    from the file, which reflows the preview or loses it. So the URL is checked against
    the assets the render copies, and the dimensions against the PNG's own header --
    the same bytes that get served -- rather than against numbers typed here.
    """
    tags = card_tags(page)
    served = {asset.name for asset in COMPOSITE_ASSETS}
    assert tags["og:image"] == SITE_URL + COMPOSITE_PNG.name
    assert tags["og:image"].rsplit("/", 1)[-1] in served
    assert tags["twitter:image"] == tags["og:image"]
    width, height = png_size(COMPOSITE_PNG)
    assert (tags["og:image:width"], tags["og:image:height"]) == (str(width), str(height))
    # Portrait, and every consumer either crops it to a band or scales it down whole;
    # what none of them does is render it at 4800 px, which is why the card names the
    # 1x export and not the committed `@2x`.
    assert width < height
    assert max(width, height) <= 4096


def test_the_card_and_the_page_say_the_same_thing(page: str) -> None:
    """A preview that disagrees with the page it opens is worse than no preview.

    The title and the sentence are built once in the renderer and substituted into
    `<title>`, `<meta name="description">` and both card vocabularies, so there is one
    string and not four. This is what would catch a later edit that retyped one of them
    in the template instead.
    """
    tags = card_tags(page)
    title = re.search(r"<title>(.*?)</title>", page)
    assert title is not None
    described = re.search(r'<meta name="description" content="([^"]*)"', page)
    assert described is not None
    assert tags["og:title"] == tags["twitter:title"] == title.group(1)
    assert tags["og:description"] == tags["twitter:description"] == described.group(1)
    assert tags["og:image:alt"] == tags["twitter:image:alt"]
    # The bound is the certificate's, wherever it is stated.
    for text in (title.group(1), described.group(1)):
        assert "s(11) ≥ 381/100" in text


def test_the_published_document_is_named_for_the_result(document: str) -> None:
    """`conventions.md` names a document for the result and for what it is.

    It was `explainer.md`, which says what the file is and not which result it explains;
    the convention is `t-NNN-explainer.md`, the same name a case-local document would
    take, because what a file is called should not depend on the directory it is served
    from. The id is written once in the renderer and every name is derived from it, so
    what is pinned here is the shape and the sharing: the published document and the
    claim documents beside the certificates carry one id between them, not two.
    """
    assert re.fullmatch(r"t-\d{3}-explainer\.md", MARKDOWN_OUTPUT.name)
    assert MARKDOWN_OUTPUT.name == f"{RESULT_ID}-explainer.md"
    claims = sorted(CASE.glob("*-verifiable-claim-*.md"))
    assert claims, "the case carries no claim document to share an id with"
    for claim in claims:
        assert claim.name.startswith(f"{RESULT_ID}-"), claim.name
    # The document is what it is named after: the article, not the template.
    assert document.startswith("# s(11)")


def test_the_md_chip_offers_the_document_by_its_published_name(page: str) -> None:
    """The chip is a relative link, so it resolves to a file that has to be beside it.

    `SOURCE_URL` is the published document's own filename, so a rename moves both ends
    at once. A chip left pointing at the old name is a 404 on the deployed site and
    nothing in the render notices, which is why it is checked against the constant the
    writer uses rather than against a name spelled out here.
    """
    assert f'href="{MARKDOWN_OUTPUT.name}"' in page
