"""Architecture contracts for the packing project's code-maturity layers."""

from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import cast

import pytest
import yaml

from devtools.check_readme import meaningful_top_level_entries
from sqpack.project import ProjectLayoutError, require_project_root

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = PROJECT_ROOT.parent
SOURCE_ROOT = PROJECT_ROOT / "src" / "sqpack"
VALIDATION_WORKFLOW = REPOSITORY_ROOT / ".github" / "workflows" / "packing-validation.yml"
PYTHON_VERSION = PROJECT_ROOT / ".python-version"


def _mapping(value: object) -> dict[str, object]:
    assert isinstance(value, dict)
    return cast("dict[str, object]", value)


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    return imported


def _assert_imports_exclude(paths: list[Path], forbidden: tuple[str, ...]) -> None:
    violations = [
        f"{path.relative_to(PROJECT_ROOT)} imports {imported}"
        for path in paths
        for imported in sorted(_imports(path))
        if imported.startswith(forbidden)
    ]
    assert violations == []


def _process_module_references(path: Path) -> set[str]:
    """Literal Python modules named across a subprocess boundary."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return {
        value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance((value := node.value), str)
        and re.fullmatch(r"(?:cases|devtools)(?:\.[a-zA-Z_][a-zA-Z0-9_]*)+", value)
    }


def test_code_is_segregated_by_maturity_and_dependencies_flow_one_way() -> None:
    required = [
        SOURCE_ROOT,
        SOURCE_ROOT / "research",
        SOURCE_ROOT / "campaign",
        SOURCE_ROOT / "cli",
        PROJECT_ROOT / "cases",
        PROJECT_ROOT / "devtools",
    ]
    assert [path.relative_to(PROJECT_ROOT) for path in required if not path.is_dir()] == []

    reusable = list(SOURCE_ROOT.glob("*.py"))
    research = list((SOURCE_ROOT / "research").glob("*.py"))
    campaign = list((SOURCE_ROOT / "campaign").glob("*.py"))
    cli = list((SOURCE_ROOT / "cli").glob("*.py"))

    _assert_imports_exclude(
        reusable,
        ("sqpack.research", "sqpack.campaign", "cases", "devtools"),
    )
    _assert_imports_exclude(research, ("sqpack.campaign", "cases", "devtools"))
    _assert_imports_exclude(campaign, ("cases", "devtools"))
    _assert_imports_exclude(cli, ("cases", "devtools"))

    assert {
        reference
        for path in reusable + research + campaign
        for reference in _process_module_references(path)
    } == set()
    cli_process_edges = {
        reference for path in cli for reference in _process_module_references(path)
    }
    assert any(reference.startswith("cases.") for reference in cli_process_edges)
    assert any(reference.startswith("devtools.") for reference in cli_process_edges)


def test_repository_applications_fail_clearly_without_a_project_checkout(
    tmp_path: Path,
) -> None:
    with pytest.raises(ProjectLayoutError, match="PACKING_PROJECT_ROOT"):
        require_project_root(tmp_path)


@pytest.mark.parametrize(
    ("module", "arguments"),
    [
        ("sqpack.cli.validate", ["--list"]),
        ("sqpack.cli.witness", ["inspect", "missing.yaml"]),
        ("sqpack.campaign.runner", ["status"]),
        ("sqpack.campaign.ledger", ["check"]),
    ],
)
def test_repository_application_entrypoints_reject_an_invalid_explicit_root(
    tmp_path: Path, module: str, arguments: list[str]
) -> None:
    environment = os.environ.copy()
    environment["PACKING_PROJECT_ROOT"] = str(tmp_path)

    completed = subprocess.run(
        [sys.executable, "-m", module, *arguments],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "packing project checkout not found" in completed.stderr
    assert "PACKING_PROJECT_ROOT" in completed.stderr


def test_no_python_implementation_remains_in_ambiguous_legacy_locations() -> None:
    legacy = [
        *PROJECT_ROOT.glob("*.py"),
        *(PROJECT_ROOT / "tools").glob("*.py"),
        *(PROJECT_ROOT / "campaign").glob("*.py"),
        *(PROJECT_ROOT / "sqpack").rglob("*.py"),
    ]
    assert [path.relative_to(PROJECT_ROOT) for path in legacy] == []


def test_no_bash_or_shell_entry_points_remain() -> None:
    scripts = [
        path
        for pattern in ("*.sh", "*.bash")
        for path in PROJECT_ROOT.rglob(pattern)
        if not any(part.startswith(".") for part in path.relative_to(PROJECT_ROOT).parts)
    ]
    assert [path.relative_to(PROJECT_ROOT) for path in scripts] == []


def test_readme_inventory_ignores_cache_only_legacy_directories(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    repository.mkdir()
    (repository / "README.md").write_text("# Example\n", encoding="utf-8")
    (repository / "current").mkdir()
    (repository / "current" / "module.py").write_text("", encoding="utf-8")
    cache = repository / "tools" / "__pycache__"
    cache.mkdir(parents=True)
    (cache / "removed.cpython-314.pyc").write_bytes(b"ignored")

    assert meaningful_top_level_entries(repository) == {"README.md", "current"}


def test_ci_jobs_fetch_provenance_history_and_key_the_uv_cache_from_the_lock() -> None:
    document: object = yaml.safe_load(VALIDATION_WORKFLOW.read_text(encoding="utf-8"))
    jobs = _mapping(_mapping(document)["jobs"])

    assert PYTHON_VERSION.read_text(encoding="utf-8").strip() == "3.14.7"

    for job_name in ("validate", "exhaustive", "macos-portability"):
        raw_steps = _mapping(jobs[job_name])["steps"]
        assert isinstance(raw_steps, list)
        steps = [_mapping(step) for step in raw_steps]

        checkout = next(
            step for step in steps if str(step.get("uses", "")).startswith("actions/checkout@")
        )
        depth = _mapping(checkout.get("with") or {}).get("fetch-depth")
        commands = [str(step["run"]) for step in steps if isinstance(step.get("run"), str)]
        # Full history is needed by exactly one thing: the provenance step, which
        # verifies historical engine commits rather than only HEAD. A job that runs the
        # whole gate reaches it; a job restricted with `--only` does not. Tying the
        # requirement to the reason rather than to the job name lets a narrow job clone
        # shallow, and still fails if a full-gate job is made shallow.
        runs_whole_gate = any(
            "packing-validate" in command and "--only" not in command for command in commands
        )
        if runs_whole_gate:
            assert depth == 0, f"{job_name} runs the whole gate and needs full history"
        else:
            assert not any("provenance" in command for command in commands), (
                f"{job_name} is shallow but names the provenance surface"
            )

        setup_uv = next(
            step
            for step in steps
            if str(step.get("uses", "")).startswith("astral-sh/setup-uv@")
        )
        setup_options = _mapping(setup_uv["with"])
        assert setup_options["python-version"] == "3.14.7"
        assert setup_options["working-directory"] == "packing"
        assert setup_options["cache-dependency-glob"] == "uv.lock"

        environment_commands = [
            str(step["run"])
            for step in steps
            if isinstance(step.get("run"), str)
            and str(step["run"]).startswith(("uv sync", "uv run"))
        ]
        assert environment_commands
        assert all("--all-extras" in command for command in environment_commands)

    triggers = _mapping(_mapping(document)["on"])
    assert "workflow_dispatch" in triggers
    assert "schedule" in triggers
    assert triggers["pull_request"] == {}

    validate_steps = _mapping(jobs["validate"])["steps"]
    assert isinstance(validate_steps, list)
    required_step = next(
        _mapping(step)
        for step in validate_steps
        if _mapping(step).get("name") == "Run the required pull-request surface"
    )
    assert required_step["if"] == "github.event_name == 'pull_request'"
    assert " ".join(str(required_step["run"]).split()) == (
        "uv run --frozen --all-extras --group dev packing-validate --fast "
        "--jobs 2 --inner-jobs 1"
    )
    full_step = next(
        _mapping(step)
        for step in validate_steps
        if _mapping(step).get("name") == "Run the complete integration surface"
    )
    assert full_step["if"] == "github.event_name != 'pull_request'"
    # `--skip`, because the exhaustive exact tier is the `exhaustive` job's whole
    # selection and 1943s is not a bill to pay twice. That the two selections still
    # partition `STEPS` is checked against the CLI's own selector in
    # `test_the_post_merge_jobs_partition_the_gate`; what is pinned here is that this
    # command is the one that leaves the tier out.
    assert " ".join(str(full_step["run"]).split()) == (
        'uv run --frozen --all-extras --group dev packing-validate --skip "exhaustive '
        'exact behavioral tests" --jobs 2 --inner-jobs 2'
    )

    # The exhaustive exact tier, split onto its own runner on 2026-09-05 (think-tr2z) so
    # that a step which had been half the complete surface's wall time reports its own
    # verdict against its own budget. D-456 is what that fixes: killed at its budget with
    # its output still in an unflushed pipe, it turned `validate` red on three
    # consecutive merges while saying nothing about the sixty steps beside it.
    exhaustive_job = _mapping(jobs["exhaustive"])
    assert exhaustive_job["if"] == "github.event_name != 'pull_request'"
    assert "continue-on-error" not in exhaustive_job
    exhaustive_steps = exhaustive_job["steps"]
    assert isinstance(exhaustive_steps, list)
    exhaustive_commands = [
        " ".join(str(_mapping(step)["run"]).split())
        for step in exhaustive_steps
        if isinstance(_mapping(step).get("run"), str)
        and "packing-validate" in str(_mapping(step)["run"])
    ]
    assert exhaustive_commands == [
        (
            'uv run --frozen --all-extras --group dev packing-validate --only "exhaustive '
            'exact behavioral tests" --jobs 1 --inner-jobs 2'
        )
    ]

    required_job = _mapping(jobs["packing-required"])
    assert required_job["needs"] == "validate"
    # `!cancelled()`, not `always()`, and the difference is D-380. With `always()` a run
    # superseded by the next push -- routine, since the workflow sets
    # `cancel-in-progress: true` and OR-3 says to push and keep working -- reached this job
    # with `needs.validate.result == 'cancelled'` and reported the required check as a hard
    # failure. A genuine validate failure is not `cancelled()`, so the job still runs and
    # still fails; a cancelled run now reports nothing and the check stays pending, which
    # is the safe direction.
    assert required_job["if"] == ("!cancelled() && github.event_name == 'pull_request'")
    assert "continue-on-error" not in required_job
    required_job_steps = required_job["steps"]
    assert isinstance(required_job_steps, list)
    required_command = " ".join(str(_mapping(required_job_steps[0])["run"]).split())
    assert required_command == 'test "$VALIDATE_RESULT" = "success"'

    # The macOS job is a second-architecture smoke check, not a second full gate.
    # It used to run the whole surface, which reached the composite-PDF step, whose
    # `cairosvg` needs a `libcairo` the runner does not have -- so it failed on every
    # push to main regardless of content. These assertions pin the narrow shape so it
    # cannot quietly grow back into a duplicate of `validate`.
    mac_job = _mapping(jobs["macos-portability"])
    raw_mac_steps = mac_job["steps"]
    assert isinstance(raw_mac_steps, list)
    mac_steps = [_mapping(step) for step in raw_mac_steps]
    assert "if" not in mac_job, (
        "the macOS check is cheap enough to run on pull requests; skipping them is why "
        "the libcairo breakage was only ever visible after a merge"
    )
    assert "continue-on-error" not in mac_job
    assert all("continue-on-error" not in step for step in mac_steps)

    mac_commands = [str(step["run"]) for step in mac_steps if isinstance(step.get("run"), str)]
    gate_commands = [command for command in mac_commands if "packing-validate" in command]
    assert gate_commands, "the macOS job runs no validation at all"
    assert all("--only" in command for command in gate_commands), (
        "every macOS gate command must be restricted with --only; an unrestricted run "
        "reaches the composite-PDF step and its missing libcairo"
    )
    assert not any("--deep" in command for command in gate_commands), (
        "a deep rebuild is not a platform question and belongs on Linux"
    )

    # The surfaces a second architecture could actually disagree about.
    selected = " ".join(gate_commands)
    for surface in (
        "exact verification",
        "verifier perturbation limits",
        "small-n exact models",
        "golden basin maps",
    ):
        assert f'"{surface}"' in selected, f"macOS no longer checks {surface}"

    assert any("import sqpack" in command for command in mac_commands), (
        "the macOS job must prove the package imports on the second architecture"
    )
    assert all(
        "check_known_macos_golden_drift" not in str(step.get("run", "")) for step in mac_steps
    )


def test_exhaustive_exact_marker_is_declared_only_by_measured_slow_nodes() -> None:
    expected = {
        # Full 181-direction exact decisions. Until 2026-09-04 these ran to a quarter
        # of an hour each on the Fraction sweep and together exceeded the CI budget
        # for the fast tier. Agenda 020's integer sweep brought the retained
        # certificates to 14-39 s apiece on four cores (n = 17 in 21.8 s, n = 20 in
        # 38.7 s), which is still above the bar this registry has always applied --
        # Massaccesi's 168-atom fixture at about 25 s -- and together they are still
        # two to four minutes on a two-core runner whose whole fast tier has a
        # 1800 s budget. Re-pricing them into the fast tier is BC-195's call, with
        # the measurement now in hand. Every one has a fast counterpart in the same
        # file that pins what its record claims, or decides it on a coarse net.
        # The witness walk: all 181 directions of all four retained certificates on the
        # integer route, serially, checking the reported centre is admissible (D-449).
        # 282 s on four cores on 2026-09-05, with the push tier running beside it.
        "test_fractional_sweep_integer.py": {
            "test_every_reported_witness_is_admissible_on_every_retained_certificate",
        },
        "test_fractional_certificate.py": {
            "test_the_full_retained_certificate_is_accepted",
            "test_the_retained_n12_certificate_is_accepted",
            "test_the_n11_calibration_rung_verifies_on_the_full_net",
            "test_the_n11_certificate_is_accepted",
            "test_the_n17_certificate_is_accepted",
            "test_the_n20_certificate_is_accepted",
        },
        # The interval route over the doubled net, 361 directions and one to six
        # million boxes each; untouched by the integer sweep, and still minutes each.
        # The sub-net acceptance tests beside them stay fast.
        "test_fractional_interval.py": {
            "test_the_393_100_certificate_is_accepted_on_the_full_doubled_net",
            "test_the_live_n12_certificate_is_accepted_on_the_full_doubled_net",
            "test_the_retained_n11_certificate_is_accepted_on_the_full_doubled_net",
            "test_the_retained_n17_certificate_is_accepted_on_the_full_doubled_net",
            "test_the_retained_n20_certificate_is_accepted_on_the_full_doubled_net",
            "test_massaccesi_n17_reproduces_the_published_bound_on_the_full_doubled_net",
        },
        # The retention gate's own positive control: both routes on a retained rung,
        # which is the exact sweep's cost plus the interval route's. Its refusals run
        # in the fast tier beside it, since a refusal is decided before either sweep.
        # The quick-mode control runs the real interval route on the 19/5 rung: 10.6 s on
        # four cores on 2026-09-05, measured when PR 80's gate tests were ported and it
        # was the one unmarked test that cost the fast tier anything. Its stubbed twin
        # holds the same contract in the fast tier.
        "test_decide_certificate.py": {
            "test_a_retained_rung_passes_both_routes_and_they_agree",
            "test_quick_mode_says_it_cannot_retain",
        },
        # The standalone third-party package deciding its own shipped 19/5 certificate
        # through its own verifier: 425 atoms, 181 directions and 90,546,593 cells in one
        # pure-Python process, with no numpy, no parallelism and two direct-summation
        # audits per direction, because the package's whole point is that it imports
        # nothing. Measured 2026-09-05 at 22.7 s on an idle four-core box, CPython 3.14.
        # Everything else in that file -- the loader refusals, the two degenerate
        # domains, the declaration mismatch and the bounded negative control -- runs in
        # the fast tier beside it in 0.3 s.
        "test_n11_thirdparty_verify.py": {
            "test_the_package_decides_its_own_shipped_certificate",
        },
        # The standalone verifier's own full decision of the retained n = 11 bytes,
        # run as a subprocess. Measured 2026-09-05 at 49.4 s for the node, 47.5 s of it
        # the verifier itself: 181 directions over 567,131,843 reachable cells, in
        # pure-Fraction and integer arithmetic with no numpy and no parallelism to
        # reach for. That is the price of a decision that imports nothing from this
        # repository. Its refusals run in the fast tier beside it, since a refusal is
        # decided before the sweep.
        "test_minimal_verify.py": {
            "test_the_retained_bytes_are_verified_on_the_full_net",
        },
        "test_exact_jets.py": {
            "test_n5_wall_and_contact_gradients_match_authoritative_source_rows",
        },
        "test_minus_w_row_jets.py": {
            "test_owner_rows_match_complete_authoritative_inventory",
            "test_active_rows_expose_both_owner_alternatives",
            "test_sat_row_retains_exact_center_angle_cross_curvature",
        },
        "test_minus_w_row_inventory.py": {
            "test_shared_row_inventory_is_exact_isolated_and_builds_once_per_stratum",
        },
        "test_minus_w_scale.py": {
            "test_positive_w_control_has_exact_three_by_five_inventory",
        },
        "test_minus_w_owner4.py": {
            "test_positive_w_owner4_control_exhausts_three_strata_and_rejects_zero_w",
        },
        "test_minus_w_sheet.py": {
            "test_positive_sheet_path_checks_all_seventeen_rows_for_both_owners",
            "test_bad_center_correction_is_rejected_by_same_row_evaluator",
        },
        "test_minus_w_stress.py": {
            "test_w_curvature_is_even_nonzero_and_quadratically_scaled",
            "test_real_production_weight_perturbation_breaks_cancellation",
            "test_uniform_weight_rescaling_fails_exact_normalization",
        },
        # The unpinned standard-library verifier, verify_claim.py, all in Fraction
        # arithmetic: the 19/5 rung on its full 181-direction net (36 s, measured
        # 2026-09-04) and the ten rows of thirdparty/falsify.py's table, each a full
        # decision, about six minutes together. The fast tier decides the rung's tight
        # direction and a two-atom instance of the theorem beside them.
        "test_verify_claim.py": {
            "test_the_19_5_rung_is_accepted_on_the_full_net",
            "test_every_falsification_is_refused_on_the_expected_condition",
        },
        # Measured 2026-08-30: about three minutes. It re-derives n = 40's whole
        # assessment, whose intersecting-assessor section runs 240 linear programs over
        # 400 rows and re-decides every proposal in the field.
        "test_n40_rigidity.py": {
            "test_the_record_round_trips",
        },
    }
    declared: dict[str, set[str]] = {}
    marker = "pytest.mark.exhaustive_exact"
    for path in (PROJECT_ROOT / "tests").glob("test_*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        marked: set[str] = set()
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and any(
                ast.unparse(decorator) == marker for decorator in node.decorator_list
            ):
                marked.add(node.name)
            if isinstance(
                node, (ast.Assign, ast.AnnAssign)
            ) and "exhaustive_exact" in ast.unparse(node):
                marked.add("<module-level assignment>")
        if marked:
            declared[path.name] = marked

    assert declared == expected


def test_devtools_use_public_package_interfaces() -> None:
    violations: list[str] = []
    path = PROJECT_ROOT / "devtools" / "check_canonical.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or not node.module:
            continue
        if node.module.startswith("sqpack"):
            violations.extend(
                f"{path.relative_to(PROJECT_ROOT)} imports {alias.name}"
                for alias in node.names
                if alias.name.startswith("_")
            )
    assert violations == []


def test_yaml_is_read_only_through_the_project_loader() -> None:
    """PyYAML's pure-Python scanner cannot come back one call site at a time.

    `yaml.safe_load` and a bare `yaml.SafeLoader` use the Python scanner, which cost 67
    seconds to validate a record that parses in a fraction of that through libyaml
    (D-370). `sqpack.yamlio` owns the choice; everything else asks it.
    """
    violations: list[str] = []
    owner = PROJECT_ROOT / "src" / "sqpack" / "yamlio.py"
    for directory in ("src", "devtools", "cases"):
        for path in sorted((PROJECT_ROOT / directory).rglob("*.py")):
            if path == owner:
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Attribute) or node.attr not in {
                    "safe_load",
                    "SafeLoader",
                }:
                    continue
                if isinstance(node.value, ast.Name) and node.value.id == "yaml":
                    violations.append(
                        f"{path.relative_to(PROJECT_ROOT)}:{node.lineno} uses "
                        f"yaml.{node.attr}; import it from sqpack.yamlio instead"
                    )
    assert violations == []
