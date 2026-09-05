#!/usr/bin/env python3
"""Check durable-document coverage, lifecycle, footers, links, and generated map."""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote

from devtools.render_document_map import MAP, REPO, SYNOPSIS, expected_synopsis, load_map
from sqpack.yamlio import safe_load

FOOTER = "This document follows common-doc-guidelines.md."
# `site` is the explainer's render output, gitignored and rebuilt by every run. It is
# not durable, so it has nothing to be mapped to; the page and the Markdown document
# beside it are checked by the renderer's own `--check`, which compares them byte for
# byte against a fresh render.
IGNORED_PARTS = {
    ".pytest_cache",
    ".venv",
    "__pycache__",
    "node_modules",
    "attic",
    "site",
}
REPOSITORY_ROOT = REPO
RETIRED_PHRASES = (
    "approximately verified",
    "numerical-arbitrary-precision",
    "numerically verified",
    "verified-construction",
)


def _matches(pattern: str) -> set[str]:
    return {path.relative_to(REPO).as_posix() for path in REPO.glob(pattern) if path.is_file()}


def _frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter")
    return safe_load(text.split("---\n", 2)[1])


def _slugs(text: str) -> set[str]:
    """Approximate GitHub heading ids, including duplicate-heading suffixes."""
    counts: Counter[str] = Counter()
    slugs: set[str] = set(re.findall(r'id="([^"]+)"', text))
    for heading in re.findall(r"^#{1,6}\s+(.+)$", text, re.MULTILINE):
        plain = re.sub(r"<[^>]+>", "", heading)
        plain = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", plain)
        base = re.sub(r"[^a-z0-9 _-]", "", plain.lower()).strip().replace(" ", "-")
        suffix = counts[base]
        counts[base] += 1
        slugs.add(base if suffix == 0 else f"{base}-{suffix}")
    return slugs


def _is_ephemeral_local_target(path: Path) -> bool:
    """Reject links whose apparent validity depends on untracked tbd working state."""
    try:
        relative = path.relative_to(REPOSITORY_ROOT)
    except ValueError:
        return False
    return relative.parts[:2] == (".tbd", "docs")


def _link_problems(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    problems: list[str] = []
    for raw_target in re.findall(r"!?\[[^]]*\]\(([^)]+)\)", text):
        target = raw_target.strip().strip("<>")
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        relative, _, fragment = target.partition("#")
        resolved = path if not relative else (path.parent / unquote(relative)).resolve()
        label = path.relative_to(REPO).as_posix()
        if not resolved.exists():
            problems.append(f"{label}: dead link -> {target}")
        elif _is_ephemeral_local_target(resolved):
            problems.append(f"{label}: ephemeral local-state link -> {target}")
        elif (
            fragment
            and resolved.suffix == ".md"
            and unquote(fragment) not in _slugs(resolved.read_text(encoding="utf-8"))
        ):
            problems.append(f"{label}: dead anchor -> {target}")
    return problems


def check() -> list[str]:
    document_map = load_map()
    problems: list[str] = []
    documents = document_map["documents"]
    document_paths = [item["path"] for item in documents]
    if len(document_paths) != len(set(document_paths)):
        problems.append("document map contains duplicate standalone paths")

    covered = set(document_paths)
    for document in documents:
        path = REPO / document["path"]
        if not path.is_file():
            problems.append(f"mapped document does not exist: {document['path']}")
        replacement = document.get("superseded_by")
        if document["lifecycle"] == "superseded" and not replacement:
            problems.append(f"{document['path']}: superseded without superseded_by")
        if replacement and not (REPO / replacement).is_file():
            problems.append(f"{document['path']}: replacement does not exist: {replacement}")

    for collection in document_map["collections"]:
        matched = _matches(collection["pattern"])
        if not matched:
            problems.append(f"document collection is empty: {collection['pattern']}")
        overlap = covered & matched
        if overlap:
            problems.append(f"document map covers paths more than once: {sorted(overlap)[:3]}")
        covered |= matched
        schema = REPO / collection["schema"]
        if not schema.is_file():
            problems.append(f"collection schema does not exist: {collection['schema']}")
        for relative in sorted(matched):
            try:
                metadata = _frontmatter(REPO / relative)["softschema"]
            except (KeyError, TypeError, ValueError) as error:
                problems.append(f"{relative}: cannot read softschema metadata: {error}")
                continue
            if metadata.get("contract") != collection["contract"]:
                problems.append(
                    f"{relative}: contract {metadata.get('contract')!r} does not match "
                    f"{collection['contract']!r}"
                )

    excluded: set[str] = set()
    for exclusion in document_map["exclusions"]:
        matched = _matches(exclusion["pattern"])
        if not matched:
            problems.append(f"document exclusion is empty: {exclusion['pattern']}")
        excluded |= matched

    actual = {
        path.relative_to(REPO).as_posix()
        for path in REPO.rglob("*.md")
        if path.is_file()
        and not any(
            part in IGNORED_PARTS or part.startswith(".")
            for part in path.relative_to(REPO).parts
        )
    }
    unmapped = actual - covered - excluded
    problems.extend(f"unmapped durable document: {path}" for path in sorted(unmapped))
    problems.extend(
        f"mapped document is also excluded: {path}" for path in sorted(covered & excluded)
    )

    for relative in sorted(covered & actual):
        text = (REPO / relative).read_text(encoding="utf-8")
        if FOOTER not in text:
            problems.append(f"{relative}: common-doc footer is missing")
        problems.extend(_link_problems(REPO / relative))

    current_paths = {
        item["path"]
        for item in documents
        if item["authority"] in {"definitive", "current"} and item["role"] != "plan"
    }
    for relative in sorted(current_paths):
        lowered = (REPO / relative).read_text(encoding="utf-8").lower()
        problems.extend(
            f"{relative}: retired assurance phrase {phrase!r}"
            for phrase in RETIRED_PHRASES
            if phrase in lowered
        )
        if "role: exact_solution" in lowered:
            problems.append(f"{relative}: retired exact_solution resource role")

    current = SYNOPSIS.read_text(encoding="utf-8")
    try:
        if current != expected_synopsis(current, document_map):
            problems.append("SYNOPSIS.md document map is stale")
    except ValueError as error:
        problems.append(str(error))
    if MAP.relative_to(REPO).as_posix() != "docs/project/document-map.yaml":
        problems.append("document-map location drifted from its public contract")
    return problems


def main() -> int:
    problems = check()
    if problems:
        for problem in problems:
            print(f"FAIL {problem}", file=sys.stderr)
        return 1
    document_map = load_map()
    count = len(document_map["documents"]) + sum(
        len(_matches(collection["pattern"])) for collection in document_map["collections"]
    )
    print(f"  documentation map covers {count} durable documents; footers and links resolve")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
