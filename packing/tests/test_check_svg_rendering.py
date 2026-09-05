"""Controls for the document sweep behind the inline-SVG ownership check.

The check asks a question about this repository's own prose: does every SVG a document
embeds resolve to an artifact this repository builds and retains? The question only makes
sense over documents this repository is answerable for, and the sweep is what decides
that set. Widen it by accident and the check indicts files nobody here wrote.

That is not hypothetical. `vendor/kpress` is an upstream repository checked out as a
submodule, and its own test fixtures embed two SVGs of their own. The sweep excluded
`resources`, `node_modules` and dot-prefixed directories but not `vendor`, so the moment
the submodule landed the check began failing on `main` -- reporting, correctly by its own
lights and uselessly by ours, that an upstream project's fixture is not one of our
artifacts (D-455).

So what is pinned here is the boundary, not the check: the sweep must reach our
documents and must not reach a vendored one. The check's own controls run in the
validation gate; these run in the fast suite, where a regression is cheap to see.
"""

from __future__ import annotations

import pytest

from devtools.check_svg_rendering import (
    FOREIGN_DIRECTORY_NAMES,
    REPO,
    repository_documents,
)

#: A Markdown file inside the vendored submodule that embeds an SVG of its own. Named
#: rather than discovered: a test that searches for its own subject passes when the
#: subject is gone, which is the failure mode this test exists to catch.
VENDORED_DOCUMENT = REPO / "vendor/kpress/tests/e2e/docs/index.md"


def test_the_sweep_reaches_this_repositorys_own_documents() -> None:
    """A sweep that excluded everything would satisfy every other test here."""
    documents = set(repository_documents())
    assert REPO / "README.md" in documents
    assert REPO / "AGENTS.md" in documents


@pytest.mark.skipif(
    not VENDORED_DOCUMENT.is_file(),
    reason="vendor/kpress is not checked out, so there is no vendored document to exclude",
)
def test_the_sweep_does_not_reach_a_vendored_document() -> None:
    """The regression that turned `main` red: upstream fixtures are not our prose."""
    assert VENDORED_DOCUMENT not in set(repository_documents())


@pytest.mark.skipif(
    not (REPO / "vendor").is_dir(),
    reason="vendor/ is not checked out",
)
def test_no_swept_document_lies_under_a_foreign_directory() -> None:
    """Stated over the whole result, so a second vendored tree cannot slip in."""
    trespassers = [
        document.relative_to(REPO).as_posix()
        for document in repository_documents()
        if FOREIGN_DIRECTORY_NAMES & set(document.relative_to(REPO).parts)
    ]
    assert trespassers == []


def test_a_generated_document_under_site_is_not_swept() -> None:
    """The render output is this repository's, but it is not this repository's prose.

    `packing/site/` is written fresh by every explainer render: the page, the published
    Markdown, and copies of the composite placed beside them. The published document
    embeds its neighbouring copy of the atlas, which is not one of the atlas's owned
    artifacts and never will be, so sweeping that directory makes the ownership control
    report a finding about a file the renderer is already responsible for.

    Being gitignored is not what excludes it. This sweep walks files git does not track,
    which is exactly the blind spot D-455 was about; the exclusion has to be stated.
    """
    swept = {document.relative_to(REPO).as_posix() for document in repository_documents()}
    assert not [path for path in swept if path.startswith("packing/site/")]
    assert "site" in FOREIGN_DIRECTORY_NAMES


def test_the_exclusion_set_is_the_one_the_formatter_uses() -> None:
    """`.flowmarkignore` excludes `vendor/` for the same reason, and says so.

    The two lists are maintained by hand in different languages; this holds them to the
    same answer about the vendored tree, which is the entry that has drifted before.
    """
    ignore = (REPO / ".flowmarkignore").read_text(encoding="utf-8")
    assert "vendor/" in ignore
    assert "vendor" in FOREIGN_DIRECTORY_NAMES
