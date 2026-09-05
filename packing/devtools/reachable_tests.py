#!/usr/bin/env python3
"""Select the test files a change can reach, erring toward running too many.

`BC-086`. Three red pushes on 2026-08-30 shared one shape: the change was to gate or
tooling code, the break was in a test pinned to that code, and the pre-push floor
(`--edit`, 43s) runs no tests at all while the tier that does (`--fast`) is priced at the
cost of its 499-second test step. The gap between 44s and 568s is where all three
failures lived. This module is the instrument that closes it: given the paths a push
changes, it names the test files that change can reach, so `packing-validate --push` can
run them without paying for the whole suite.

Reachability is computed from evidence, not convention, and every rule errs toward
inclusion:

- **Import closure.** A static import graph over `src/sqpack`, `devtools`, `cases`,
  `benchmarks` and `tests` (AST, relative imports resolved); a test reaches a changed
  module if it imports it transitively. `benchmarks` joined the map in agenda-015
  `BC-142`, after the agenda-014 push tier selected all 1,302 tests for a change whose
  only Python lived there.
- **Text mention.** A test that names a changed module's dotted path, or a changed
  file's basename, is selected even without an import edge. This is what catches the
  `D-381` class: a test pinning a literal string emitted by code it exercises through a
  subprocess rather than an import.
- **Walkers always run.** A test that enumerates the repository (`rglob`, `iterdir`,
  `glob`, `listdir`) or imports dynamically (`importlib`, `__import__`) has the whole
  path space as its input, so it is selected for every change, exactly as unattributed
  steps are.
- **The whole suite on anything unmapped.** An empty change set, a changed `conftest.py`
  or packaging file, a Python file outside the mapped roots, or a parse failure selects
  everything. "Nothing was determined" is not "nothing changed".

The same honesty proviso as `Step.touches` applies and is worth restating: this is a
static over-approximation, not a proof. CI runs the full gate on every push regardless,
so the cost of the residual risk is a CI round trip, never a wrong record -- and the
measured alternative, three times in one day, was running no tests at all.

Usage, from `packing/`:
    uv run --frozen --all-extras --group dev python -m devtools.reachable_tests
"""

from __future__ import annotations

import argparse
import ast
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from sqpack.cli.validate import changed_paths

ROOT = Path(__file__).resolve().parent.parent
TESTS = ROOT / "tests"

#: Package roots the import graph maps, as (top-level package name, directory).
#: `sqpack` is installed from `src/`, the rest resolve via pytest's `pythonpath = ["."]`.
PACKAGE_ROOTS: tuple[tuple[str, Path], ...] = (
    ("sqpack", ROOT / "src" / "sqpack"),
    ("devtools", ROOT / "devtools"),
    ("cases", ROOT / "cases"),
    ("benchmarks", ROOT / "benchmarks"),
    ("tests", ROOT / "tests"),
)

#: A changed path equal to or under any of these selects the whole suite: they configure
#: how every test runs rather than what any one test checks.
SUITE_WIDE = ("pyproject.toml", "uv.lock", "tests/conftest.py", ".python-version")

#: Source markers that give a test the repository's whole path space as its input.
WALKER_MARKERS = ("rglob(", "iterdir(", ".glob(", "listdir(", "importlib", "__import__")


@dataclass(frozen=True)
class TestSelection:
    """The outcome of one reachability question."""

    everything: bool
    reason: str
    """Why `everything` is set, or a summary of the narrow selection."""

    tests: tuple[str, ...] = ()
    """Repo-relative test paths, empty when `everything` is true."""


def _module_name(path: Path) -> str | None:
    """Dotted module name for a file under a mapped package root, else None."""
    for package, directory in PACKAGE_ROOTS:
        try:
            relative = path.relative_to(directory)
        except ValueError:
            continue
        parts = (package, *relative.with_suffix("").parts)
        if parts[-1] == "__init__":
            parts = parts[:-1]
        return ".".join(parts)
    return None


def _imports_of(path: Path) -> set[str] | None:
    """Top-level dotted names this file imports, or None when it cannot be parsed."""
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except OSError, SyntaxError, UnicodeDecodeError:
        return None
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = _module_name(path)
                if base is None:
                    continue
                parts = base.split(".")
                # A module of depth d can climb at most d-1 levels; deeper is a parse-time
                # error left to pytest, treated here as reaching the package root.
                anchor = parts[: max(len(parts) - node.level, 1)]
                prefix = ".".join(anchor)
                found.add(f"{prefix}.{node.module}" if node.module else prefix)
            elif node.module:
                found.add(node.module)
                # `from a.b import c` may bind the submodule a.b.c; include both readings.
                found.update(f"{node.module}.{alias.name}" for alias in node.names)
    return found


def _mapped_files() -> dict[str, Path]:
    """Every mapped module name to its file, packages included via __init__."""
    files: dict[str, Path] = {}
    for _package, directory in PACKAGE_ROOTS:
        for path in sorted(directory.rglob("*.py")):
            name = _module_name(path)
            if name is not None:
                files[name] = path
    return files


def _reaches(imported: set[str], targets: set[str]) -> bool:
    """Does any imported name land on a target module or inside a target package?"""
    for name in imported:
        parts = name.split(".")
        prefixes = {".".join(parts[: index + 1]) for index in range(len(parts))}
        if prefixes & targets:
            return True
    return False


def select_tests(changed: list[str]) -> TestSelection:
    """The test files a change to `changed` (repo-relative paths) can reach."""
    if not changed:
        return TestSelection(everything=True, reason="no changed paths were determined")

    for path in changed:
        if path in SUITE_WIDE or path.startswith(".github/"):
            return TestSelection(everything=True, reason=f"{path} configures the suite")
        resolved = (ROOT.parent / path).resolve()
        if path.endswith(".py") and _module_name(resolved) is None:
            return TestSelection(
                everything=True, reason=f"{path} is Python outside the mapped roots"
            )

    modules = _mapped_files()
    imports: dict[str, set[str]] = {}
    for name, file in modules.items():
        found = _imports_of(file)
        if found is None:
            return TestSelection(everything=True, reason=f"{file.name} did not parse")
        imports[name] = found

    changed_modules: set[str] = set()
    changed_basenames: set[str] = set()
    changed_dotted: set[str] = set()
    for path in changed:
        resolved = (ROOT.parent / path).resolve()
        name = _module_name(resolved) if path.endswith(".py") else None
        if name is not None:
            changed_modules.add(name)
            changed_dotted.add(name)
        else:
            changed_basenames.add(Path(path).name)

    # Transitive closure: grow the changed-module set by everything that imports it.
    grew = True
    while grew:
        grew = False
        for name, found in imports.items():
            if name not in changed_modules and _reaches(found, changed_modules):
                changed_modules.add(name)
                grew = True

    selected: dict[str, str] = {}
    for name, file in modules.items():
        if file.parent != TESTS or not file.name.startswith("test_"):
            continue
        relative = str(file.relative_to(ROOT.parent))
        if name in changed_modules:
            selected.setdefault(relative, "import closure")
            continue
        text = file.read_text(encoding="utf-8")
        if any(marker in text for marker in WALKER_MARKERS):
            selected.setdefault(relative, "walks the repository or imports dynamically")
            continue
        if any(dotted in text for dotted in changed_dotted):
            selected.setdefault(relative, "names a changed module")
            continue
        if any(basename in text for basename in changed_basenames):
            selected.setdefault(relative, "names a changed file")

    tests = tuple(sorted(selected))
    total = sum(1 for _ in TESTS.glob("test_*.py"))
    if len(tests) >= total:
        return TestSelection(everything=True, reason="every test file is reachable")
    reason = f"{len(tests)} of {total} test files reachable"
    return TestSelection(everything=False, reason=reason, tests=tests)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Select the test files a change can reach, erring toward running too many."
    )
    parser.add_argument("--since", metavar="REF", default="origin/main")
    parser.add_argument(
        "--summary",
        action="store_true",
        help="print one machine-readable line: 'everything' or the selected count",
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="run pytest on the selection (the whole non-exhaustive suite when everything)",
    )
    namespace = parser.parse_args(argv)

    selection = select_tests(changed_paths(namespace.since))
    if namespace.summary:
        print("everything" if selection.everything else f"narrow {len(selection.tests)}")
        return 0
    if selection.everything:
        print(f"everything: {selection.reason}")
    else:
        print(selection.reason)
        for test in selection.tests:
            print(f"  {test}")
    if not namespace.run:
        return 0

    targets = (
        ["tests"]
        if selection.everything
        else [str((ROOT.parent / test).relative_to(ROOT)) for test in selection.tests]
    )
    # `not exhaustive_exact`, which keeps the `slow` lane in. That is deliberate and it
    # is the difference between this tier and the pull-request surface: `--fast` defers
    # every test above the per-test ceiling because it pays for them on every pull
    # request, while `--push` pays only for the tests your own change reaches, and a slow
    # test your change reaches is exactly the one worth waiting for.
    command = (
        sys.executable,
        "-m",
        "pytest",
        "-q",
        *targets,
        "-m",
        "not exhaustive_exact",
    )
    return subprocess.run(command, cwd=ROOT, check=False).returncode


if __name__ == "__main__":
    raise SystemExit(main())
