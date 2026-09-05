"""Controls for the declared-bound check.

The positive control is the `n = 68` XML depth guard, which must stay named by
`test_selected_path_scan_enforces_depth_before_python_recursion` -- a test that never
writes `MAX_XML_DEPTH` and reaches the guard by its refusal message instead. If the
matching ever silently narrows to literal constant names, that control disappears and
this test says so. The negative control is a synthetic tree whose bound no test reaches
and whose allowlist is empty.
"""

from __future__ import annotations

import pathlib
import textwrap

import pytest

from devtools import check_declared_bounds as declared
from devtools.check_declared_bounds import BoundEntry, BoundsReport

DEPTH_BOUND = "cases/unitsquare_precision/production/adapter.py::MAX_XML_DEPTH"
DEPTH_TEST = "test_selected_path_scan_enforces_depth_before_python_recursion"

FIXTURE_CASE = textwrap.dedent(
    '''
    """A synthetic bounded parser with one guarded and one unguarded bound."""

    from typing import Final

    MAX_FIXTURE_DEPTH: Final = 8
    MAX_FIXTURE_WIDTH: Final = 4


    def parse(depth: int) -> int:
        if depth > MAX_FIXTURE_DEPTH:
            raise ValueError("fixture structure exceeds the synthetic depth bound")
        return depth
    '''
).strip()

FIXTURE_TEST = textwrap.dedent(
    """
    import pytest

    from cases.fixture_case.parser import parse


    def test_depth_bound_refuses() -> None:
        with pytest.raises(ValueError, match="synthetic depth bound"):
            parse(9)
    """
).strip()

COLLISION_ALPHA = textwrap.dedent(
    '''
    """One of two modules declaring the same bound name."""

    from typing import Final

    MAX_SHARED: Final = 8


    def parse(depth: int) -> int:
        if depth > MAX_SHARED:
            raise ValueError("alpha parser exceeds its depth bound")
        return depth
    '''
).strip()

COLLISION_BETA = textwrap.dedent(
    '''
    """The untested module in the duplicate-name control."""

    from typing import Final

    MAX_SHARED: Final = 4


    def width() -> range:
        return range(MAX_SHARED)
    '''
).strip()

COLLISION_TEST = textwrap.dedent(
    """
    import pytest

    from cases.alpha import parser as alpha


    def test_alpha_depth_bound_refuses() -> None:
        with pytest.raises(ValueError, match="alpha parser exceeds its depth bound"):
            alpha.parse(alpha.MAX_SHARED + 1)
    """
).strip()


def _fixture(root: pathlib.Path) -> None:
    case = root / "cases" / "fixture_case"
    case.mkdir(parents=True)
    (case / "parser.py").write_text(FIXTURE_CASE + "\n", encoding="utf-8")
    tests = root / "tests"
    tests.mkdir(parents=True)
    (tests / "test_fixture_case.py").write_text(FIXTURE_TEST + "\n", encoding="utf-8")


def _collision_fixture(root: pathlib.Path) -> None:
    for name, source in (("alpha", COLLISION_ALPHA), ("beta", COLLISION_BETA)):
        case = root / "cases" / name
        case.mkdir(parents=True)
        (case / "parser.py").write_text(source + "\n", encoding="utf-8")
    tests = root / "tests"
    tests.mkdir(parents=True)
    (tests / "test_alpha.py").write_text(COLLISION_TEST + "\n", encoding="utf-8")


def _entry(receipt: BoundsReport, key: str) -> BoundEntry:
    matches = [
        entry for entry in receipt["bounds"] if f"{entry['module']}::{entry['name']}" == key
    ]
    assert len(matches) == 1, f"expected exactly one {key}, found {len(matches)}"
    return matches[0]


@pytest.mark.slow
def test_n68_depth_bound_is_named_by_its_refusal_test() -> None:
    """Positive control: the real repository's declared bounds are all accounted for."""
    receipt = declared.report(declared.ROOT)

    depth = _entry(receipt, DEPTH_BOUND)
    assert depth["status"] == "named"
    named_by = depth["named_by"]
    assert [reference["function"] for reference in named_by] == [DEPTH_TEST]
    evidence = named_by[0]
    assert evidence["path"] == "tests/test_unitsquare_precision_production.py"
    assert evidence["kind"] == "guard-message"
    assert "bounded parser limits" in str(evidence["detail"])
    assert depth["guard_messages"] == ["SVG structure exceeds the bounded parser limits"]

    assert receipt["violations"] == []
    assert receipt["ok"] is True
    assert declared.main([]) == 0


def test_unnamed_bound_is_refused(tmp_path: pathlib.Path) -> None:
    """Negative control: a declared bound no test reaches must be refused."""
    _fixture(tmp_path)

    receipt = declared.report(tmp_path, allowlist={})

    guarded = _entry(receipt, "cases/fixture_case/parser.py::MAX_FIXTURE_DEPTH")
    unguarded = _entry(receipt, "cases/fixture_case/parser.py::MAX_FIXTURE_WIDTH")
    assert guarded["status"] == "named"
    assert unguarded["status"] == "unnamed"
    assert [entry["name"] for entry in receipt["violations"]] == ["MAX_FIXTURE_WIDTH"]
    assert receipt["ok"] is False
    assert declared.main(["--root", str(tmp_path)]) == 1
    assert declared.main(["--root", str(tmp_path), "--json"]) == 1


def test_duplicate_bound_name_does_not_cross_module_boundary(
    tmp_path: pathlib.Path,
) -> None:
    """A test of one module cannot name a same-spelled bound in another module."""
    _collision_fixture(tmp_path)

    receipt = declared.report(tmp_path, allowlist={})

    alpha = _entry(receipt, "cases/alpha/parser.py::MAX_SHARED")
    beta = _entry(receipt, "cases/beta/parser.py::MAX_SHARED")
    assert alpha["status"] == "named"
    assert [item["function"] for item in alpha["named_by"]] == [
        "test_alpha_depth_bound_refuses"
    ]
    assert alpha["named_by"][0]["detail"] == "cases/alpha/parser.py::MAX_SHARED"
    assert beta["status"] == "unnamed"
    assert [entry["module"] for entry in receipt["violations"]] == ["cases/beta/parser.py"]


def test_allowlist_entry_registers_a_bound_with_a_reason(tmp_path: pathlib.Path) -> None:
    """An allowlisted bound passes, and its reason travels with the report."""
    _fixture(tmp_path)
    reason = "pre-existing; registered by BC-140"

    receipt = declared.report(
        tmp_path,
        allowlist={"cases/fixture_case/parser.py::MAX_FIXTURE_WIDTH": reason},
    )

    entry = _entry(receipt, "cases/fixture_case/parser.py::MAX_FIXTURE_WIDTH")
    assert entry["status"] == "allowlisted"
    assert entry["named_by"] == []
    assert entry["allowlist_reason"] == reason
    assert receipt["ok"] is True


def test_every_allowlist_entry_names_a_bound_that_exists() -> None:
    """A registration that no longer matches a declared bound is stale, not silent."""
    receipt = declared.report(declared.ROOT)
    declared_keys = {f"{entry['module']}::{entry['name']}" for entry in receipt["bounds"]}

    assert set(declared.ALLOWLIST) <= declared_keys
    for key, reason in declared.ALLOWLIST.items():
        assert reason.startswith("pre-existing; registered by BC-140"), key

    own_path = __file__.rsplit("/packing/", 1)[1]
    assert own_path in declared.EXCLUDED_REFERENCES
