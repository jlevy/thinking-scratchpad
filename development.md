# Packing Development Guide

This is the engineering entry point for `packing/`. Read [`TUTORIAL.md`](TUTORIAL.md)
for the mathematics, [`SYNOPSIS.md`](SYNOPSIS.md) for research status, and
[`campaign/README.md`](packing/campaign/README.md) before operating the research loop.
This guide owns runtime support, code placement, validation, and refactoring practice.

The governing rule is assurance proportional to reuse and consequence.
Shared code and research-state boundaries are designed, typed, tested, and kept easy to
orient around. A retained checker for one value of `n` may stay direct and specialized.
Do not turn a one-off investigation into a framework without a second real consumer.

## Supported Environment

Python **3.14 is the only supported minor version**. Local development and CI pin the
interpreter to **3.14.7** through `.python-version` and the workflow.
Package metadata, Ruff, and BasedPyright express the broader `3.14`-only compatibility
boundary; `uv.lock` pins dependencies, not the interpreter.
macOS and Linux are supported development hosts.
Pull requests run the bounded Linux fast surface; integration events run the ordinary
full gate on both hosts.
The Rust search engine uses the stable Cargo toolchain.

From this directory:

```shell
uv sync --frozen --all-extras --group dev
uv run --frozen --all-extras --group dev python --version
uv run --frozen --all-extras --group dev packing-validate --fast
```

The version command must report Python 3.14.7. Do not run a bare `pip install`, commit a
second requirements file, or rely on packages from a global interpreter.
Use uv 0.12 or newer to bootstrap the pinned interpreter; uv 0.8.17 cannot install
CPython 3.14.7 on Linux and reports `No download found for cpython-3.14.7`. Change
dependencies in `pyproject.toml`, regenerate `uv.lock`, and commit both files together.
Use `uv sync --frozen --all-extras --group dev` in CI and when reproducing the locked
development environment; the explicit development group prevents an ambient uv
configuration from omitting the test and quality tools.

## Code Maturity and Placement

The maturity class says how a module is maintained, not how important its mathematics
is.

| Class | Location | Contract |
| --- | --- | --- |
| **E0 scratch** | Untracked scratch space or the repository `attic/` | Optimize for learning. Do not import it or cite it as evidence. Delete it or promote it when the investigation ends. |
| **E1 retained case code** | `cases/<case>/` | Scope the code to a named `n`, source, theorem, hypothesis, or experiment. State its evidence limits and retain enough input and output for replay. General APIs are optional. |
| **E2 reusable research code** | `src/sqpack/research/` and shared helpers such as `workers.py` | Serve multiple research loops through typed contracts, deterministic tests, explicit errors, and case-free policy. Optimize only from representative measurements. |
| **E3 trust and persistence code** | `src/sqpack/field.py`, `verify.py`, `witness.py`, `src/sqpack/campaign/`, and `src/sqpack/cli/` | Meet E2 expectations plus independent or mutation checks, tested failures, atomic durable writes, and fail-fast persisted-format handling. Campaign and CLI modules are repository applications, not general library APIs. |

Developer infrastructure has its own explicit locations:

- `devtools/` contains repository checks, renderers, schema validation, and negative
  controls. It is not an application API.
- `benchmarks/` contains performance probes whose purpose is measurement, not pass/fail
  correctness.
- `tests/` contains fast behavior, architecture, and CLI contracts.
- `sqsearch/` contains the Rust screening engine.
- `campaign/`, `frontier/`, `atlas/`, and `golden/` contain research state and retained
  evidence, not importable implementation code.

Dependencies flow toward more foundational code:

```text
cases/ and devtools/ ──> sqpack.research ──> sqpack foundations
      campaign app ────> foundations and retained campaign state
           CLI app ────> foundations and named cases/devtools subprocesses
```

`tests/test_module_boundaries.py` enforces the important edges and rejects Python left
in the old top-level, `tools/`, `campaign/`, or `sqpack/` implementation locations.
Reusable foundations, research modules, and campaign code may not import or name a
process dependency on `cases` or `devtools`. The outer validation CLI intentionally
starts named case and developer-tool modules in subprocesses; the architecture test
inventories those string edges as well as Python imports.
A case may consume a maintained API; the maintained API may not grow a Trump-, Göbel-,
checkpoint-, or single-`n` exception to accommodate it.

The four installed commands operate on repository-owned state, so they require a valid
`packing/` checkout.
Source and editable installs locate that checkout directly; a non-editable installation
can use the current checkout or set `PACKING_PROJECT_ROOT` explicitly.
A missing or malformed project root is a hard, actionable error.
Importing reusable `sqpack` modules does not require repository state.

Promote E1 code only after identifying a shared contract and a second real consumer.
Copying ten clear lines twice is often cheaper than inventing an abstraction whose
policy is still changing.
When a supposedly reusable path loses its consumers, demote or remove it instead of
preserving an empty layer.

## Command Surfaces

The installed commands are:

| Command | Purpose |
| --- | --- |
| `packing-validate` | Read-only project validation, focused selection, and machine-readable summaries |
| `packing-campaign` | State-machine operations for preregistered numerical rounds |
| `packing-ledger` | Check campaign invariants and freshness, or atomically render the generated ledger |
| `packing-witness` | Inspect, numerically check, or formally verify a portable packing witness without changing it |

Run `COMMAND --help` before using a command in automation.
A maintained CLI must parse arguments before doing work, keep data on stdout and
diagnostics on stderr, return a nonzero status for partial or complete failure, and
expose JSON or JSONL when its output is a data contract.
Names should say what the command does without directory context.

Use these verbs consistently:

- `check` reads and compares without changing durable state; for a packing witness it
  reports numerical assurance and the actual arithmetic, precision, and tolerance;
- `verify` is reserved for a formal decision from exact arithmetic, a rigorous
  certificate, or a complete proof;
- `replay` validates retained output without rerunning the producer;
- `render` regenerates a derived view atomically;
- `run` performs the declared experiment or workflow;
- `update` replaces a reviewed golden or source-of-truth artifact.

CLI modules adapt typed operations; they do not carry a second implementation of the
algorithm. Use argument-vector subprocess calls, never shell interpolation, for normal
process execution.

## Validation Loops

Choose the smallest loop that protects the change:

```shell
# Discover the available contracts.
uv run --frozen --all-extras --group dev packing-validate --list

# Records loop: registries, generated views and declared contracts, and no solver.
# The cheapest thing that catches what actually breaks; takes no gate marker.
uv run --frozen --all-extras --group dev packing-validate --records

# Edit loop: everything fast except the broad test suite. Seconds, runs during a gate.
uv run --frozen --all-extras --group dev packing-validate --edit

# Pre-push floor: the edit tier plus the behavioral tests reachable from the change
# (against origin/main, or --since REF). About a minute for a code change; never blind.
uv run --frozen --all-extras --group dev packing-validate --push

# The pull-request surface: the edit tier plus every behavioral test under the
# per-test ceiling. This is what CI runs on a pull request.
uv run --frozen --all-extras --group dev packing-validate --fast

# One named component. --only is repeatable and matches displayed step names.
uv run --frozen --all-extras --group dev packing-validate --only "basin identity"

# Full integration checkpoint used locally and in CI.
uv run --frozen --all-extras --group dev packing-validate

# Rebuild expensive mathematical golden producers while comparing read-only.
uv run --frozen --all-extras --group dev packing-validate --deep

# Merge or unattended-session handoff: deep checks and no skipped surface.
uv run --frozen --all-extras --group dev packing-validate --strict

# Structured result for agents and automation.
uv run --frozen --all-extras --group dev packing-validate --format json
```

The default command runs the complete ordinary surface: fast pytest contracts, Python
and Rust quality, exact and differential mathematics, replay, schemas, generated-view
drift, provenance, campaign invariants, and mutation controls.
Pytest is one layer of that gate, not a replacement for proof scripts and independent
implementations.

The validation command builds `sqsearch` only when a selected step needs it.
Checks run concurrently, but their captured output is replayed in declared order.
`--jobs` controls outer check concurrency; `--inner-jobs` caps each check’s internal
workers.
Strict mode cannot be combined with a partial selection and fails on every skip.

`--push` is the pre-push floor (`BC-086`). It selects the edit tier plus a
`reachable behavioral tests` step: `devtools.reachable_tests` computes the test files
the change can reach — import closure over `src/sqpack`, `devtools`, `cases` and
`tests`, text mention of a changed module or file, repository walkers always included —
and errs toward running too many, up to the whole suite when nothing narrower is
defensible. Each of 2026-08-30’s three red pushes broke a test reachable this way from
the changed paths ([D-381, D-393](defects.md)), and the floor would have caught all
three.

The `.gate-running` marker is a load lock protecting calibrated step budgets, not a
correctness lock — no step mutates the working tree.
The floor tiers say so: `--records`, `--edit`, and a `--push` whose test selection is
narrow take no marker and run even while a full gate holds it, because a floor the lock
can refuse is a floor that gets skipped.
Selections containing a broad or full-tier step still take the marker and still refuse a
second gate.

Every validation subprocess has a finite 900-second default deadline.
Override it with `--timeout-seconds SECONDS` or `PACKING_VALIDATE_TIMEOUT_SECONDS`;
values must be positive and finite, and an explicit smaller per-call timeout still wins.
Mutation-control commands retain their 120-second default deadline and may declare a
smaller `timeout_seconds` in `devtools/controls.yaml`. A timeout terminates and reaps
the whole process group, including a child that ignores the first termination signal.
Each command also gets an empty bytecode-cache root, so rapid same-size source mutations
cannot execute a stale control from the preceding snapshot use.

The validation deadline bounds subprocess commands on supported POSIX hosts.
It does not bound pure-Python worker code, the total duration of a step that runs
multiple commands, or detached daemons; Windows process-tree cleanup is not yet
implemented. These limits are why a subprocess timeout is not, by itself, evidence that
D-239 is resolved.

On pull requests, [`packing-validation.yml`](.github/workflows/packing-validation.yml)
runs `packing-validate --fast` on Linux and reports the stable `packing-required`
aggregate.

The behavioral suite runs in three lanes, and they partition it: `QUICK_TESTS`,
`SLOW_TESTS` and `EXHAUSTIVE_TESTS` in `sqpack/cli/validate.py` are marker expressions
over `slow` and `exhaustive_exact`, and every test satisfies exactly one, so a test
cannot be in two lanes and cannot be in none.
`--fast` runs the quick lane; the full gate adds `slow behavioral tests` and
`exhaustive exact behavioral tests`, so nothing the pull-request surface stops running
stops running.

**The boundary is a ceiling the gate enforces, not a list it trusts.**
`fast behavioral tests` passes `QUICK_TEST_CEILING_SECONDS` to pytest as
`--durations-min` and fails, naming the test, when a test it ran reports a `call` phase
at or above it. A test that grows past the ceiling therefore fails the pull-request
surface in the week it grows; the fix is to make it faster, or to mark it `slow` with
its measurement in `test_the_slow_marker_is_declared_only_by_measured_nodes`, which
moves it to the deep surface rather than stopping it running.
The `call` phase and not setup, because a module-scoped fixture bills its whole cost to
whichever test triggers it first, and marking that test would move the cost rather than
remove it. The marker registries are checked the same way for both markers: the declared
set is pinned by a test, so a marker cannot be added without stating what it measured.

Pushes to `main`, manual dispatches, and the daily schedule run the complete locked
command on Linux and macOS. The daily cadence is `BC-214`: it is the schedule that
catches a deferred test breaking on a branch that never reaches `main`, and a weekly one
would leave up to seven days between the break and the run that names it.
The macOS integration job also runs the focused deep-golden step directly.
The default validator runs the 118-test core and 21-test exhaustive exact branches as
separate direct steps.
Negative controls use at most two workers while honoring the `--inner-jobs` cap;
integration CI opts into two inner workers explicitly.
D-203’s temporary expected-failure classifier was removed after the repaired producer
passed on both architectures; the workflow test rejects its return.
Never accept a rebuilt golden to make the probe green, and do not add a second CI-only
implementation of either check.

### What each tier costs, and where its ceiling lives

A contributor runs `--edit` in the loop and `--push` before a push.
CI runs the tier named in
[`packing-validation.yml`](.github/workflows/packing-validation.yml) on a pull request,
and the complete locked command on `main`, on dispatch, and on the daily schedule.

**What each tier is allowed to cost is data the gate reads, not prose in this file.** It
is declared in
[`packing/devtools/gate-budgets.yaml`](packing/devtools/gate-budgets.yaml), one entry
per tier, and every whole-tier run compares its own wall against it:

```shell
uv run --frozen --all-extras --group dev packing-validate --budgets
```

| Tier | Who runs it | Ceiling | Cost when last measured |
| --- | --- | --- | --- |
| `--records` | contributor, before touching a registry | 300 s | 13.6 s, four contended cores, 2026-09-05 |
| `--edit` | contributor, in the edit loop | 240 s | 59.4 s, four contended cores, 2026-09-05 |
| `--push` | contributor, before a push | 1800 s | about a minute for a code change; the whole quick lane when the diff reaches everything |
| `--fast` | CI, on a pull request | 550 s | 409 s on CI’s two-core runner, 2026-09-05, run 33985984585 — the split tier’s own first reading |
| (default) | CI, on `main` and on the daily schedule | 3600 s | not clocked end to end on one runner; CI splits it across jobs |

The ceiling column is enforced and the cost column is not: the register is the
authority, and `packing-validate --budgets` prints it as of now.
Read that command rather than this table.

**A run outside its tier’s band fails and names the step that spent the time**, because
“the tier is slow” is not actionable and “`fast behavioral tests` is 1324 s of a 1370 s
tier” is. The band has more edges than a cap, and they exist because a cap alone did not
catch the 2026-08-30 to 2026-09-05 drift — 499 s to 1369.60 s, entirely inside an 1800 s
cap:

- a run over the ceiling fails;
- a run more than `drift_ratio` above the cost the register records for that tier fails,
  which is the edge a 2.65× regression crosses long before it reaches a generous cap;
- a run far enough *below* the recorded cost also fails, printing the figure to write —
  because a record bounded only from above rots downward, and a stale record makes the
  first two edges meaningless;
- and `python -m devtools.check_gate_budgets`, in the records tier, refuses a ceiling
  more than `max_headroom` above the cost its own tier records, without running anything
  at all. That is the rule that fires on 1800 s declared beside 499 s.

**Wall time is not comparable across machines, so the ratio rules enforce only on the
runner the ceiling was measured for.** Each tier declares a reference — CPU count,
`--jobs` and `--inner-jobs` — and a run whose shape differs is measured, reported, and
never failed; `--enforce-budget` overrides that for an operator who means it.
This is a deliberate trade: it makes the check quiet on a developer’s laptop and on a
contended agent box, and it means a regression is caught by CI rather than before the
push.

### A pull request with no checks at all is a mergeability question

Zero check runs on a pull request does not mean CI has not started yet.
It also means GitHub could not build the pull request’s merge ref, which happens the
moment the branch conflicts with its base — and a `pull_request` workflow has nothing to
check out, so no run is created and no check appears.
The two look identical from the API, and the second one does not heal by waiting.

So when a push produces no check run within a couple of minutes, ask whether the branch
still merges before pushing again:

```bash
git fetch origin main && git merge-tree --write-tree HEAD origin/main >/dev/null \
  && echo "merges cleanly" || echo "CONFLICTS: no run will be created"
```

Measured on 2026-09-05 (`D-459`): five pushes over twenty-five minutes produced no run
and no check on `PR 83` while other branches in the same repository ran normally
throughout, because `main` had moved under it.
Resolving the conflict restored CI on the next push.
The failure mode is quiet in the dangerous direction — an absent check reads as pending
rather than as red — so the absence is what to investigate, not the wait.

### Every pull request carries what it cost

Open or update a pull request and the description leads with the branch’s cost, then
reports the checked agenda closeout when the branch completed one:

```bash
uv run --frozen --all-extras --group dev python -m devtools.render_pr_rollup
```

It prints a markdown block — agent turns, model and thinking level, every tool called,
and the tokens behind them — for the checked-out branch, or for `--branch <name>`. Paste
it at the top of the description.
A reviewer can see what changed and otherwise cannot see what it took, and that number
has existed in `campaign/resource-usage/` the whole time.
For an agenda closeout, pass `--agenda agenda-NNN`; for a Codex session, also pass
`--session session-NNN`. The combined rendering preserves the cost block first, then
adds actual outcomes and stop reasons, dispositions, grouped file changes, validation,
documentation decisions, limits, ranked candidates, and the selected successor.
The final session command performs the generated-view and live-tbd reconciliation before
printing the same description:

```bash
uv run --frozen --all-extras --group dev python -m devtools.close_session \
  --render --session session-NNN --agenda agenda-NNN
```

**The attribution is a bound and the block says so.** `turns.by_branch` is the only
branch-aware field in `ClaudeEfficiencyRollup`, so a log that ran on more than one
branch has an exact turn count here and no way to split its tokens or tool calls.
The block prints three columns — on-branch logs only, prorated by turn share, and every
log that touched the branch — of which the outer two are measurements and the middle is
the estimate to quote.
Do not replace them with a single number: the interval is wide because the measurement
is, and narrowing it needs a branch-aware token count that the harness does not emit.

The gate step `the branch cost rollup renders` runs the renderer over every branch in
the records, including one no rollup mentions, because a division by a turn count fails
on exactly that edge.

## Focused Quality Commands

Use direct tools when their output is the point of the edit:

```shell
uv run --frozen --all-extras --group dev pytest -q
uv run --frozen --all-extras --group dev ruff check .
uv run --frozen --all-extras --group dev ruff format --check .
uv run --frozen --all-extras --group dev basedpyright

cargo test --locked --manifest-path sqsearch/Cargo.toml
cargo clippy --locked --release --all-targets --manifest-path sqsearch/Cargo.toml -- -D warnings
cargo fmt --manifest-path sqsearch/Cargo.toml --check
```

Ruff must be clean. BasedPyright runs in standard mode and must report zero diagnostics
across maintained and retained Python.
Its documented exclusions cover dynamically shaped YAML, JSON, and third-party
scientific-library boundaries; this project does not claim strict-mode coverage.
A per-file exception must name the narrow reason beside the configuration; never exempt
a maintained module from a rule family for convenience.
Use modern Python 3.14 syntax, absolute imports, `Path`, precise public-boundary types,
and exception chaining.
The enabled rule families include the pytest-style, unused-argument, blind-except,
commented-out-code, refurb, f-string and complexity-ratchet families, each argued for
beside its entry in `pyproject.toml`; printing is waived only where the tools live, so a
library module reports through `logging`. The one Python outside `packing/` is the
hand-written skill assets under `.agents/skills`, which the same two floors reach.
Comments explain non-obvious intent, invariants, units, evidence limits, and rejected
alternatives—not a line-by-line translation of the code.

Markdown is owned by Flowmark at repository root.
Durable documentation follows the common documentation guidelines and carries their
footer. Run the repository hook or `make format`; do not introduce a second Markdown
formatter.

### Probing the promotion pipeline

**Reach for these before writing a one-off script.** Both exist because a finding that
overturned something in the record was first made in a throwaway probe, which is the
wrong place for a measurement the next reader has to be able to replay.

```shell
uv run --frozen --all-extras --group dev python -m devtools.probe_contact_system
uv run --frozen --all-extras --group dev python -m devtools.probe_contact_system --case trump11 --walk
uv run --frozen --all-extras --group dev python -m devtools.probe_minimal_polynomial --case trump11
uv run --frozen --all-extras --group dev python -m devtools.probe_system_degree --eliminate-side
```

[`probe_contact_system`](packing/devtools/probe_contact_system.py) reports, per retained
case, what the assembled contact system determines: the typing, the equations against
the unknowns, the Jacobian’s rank and the gap that verdict rests on, the residual at the
pose, `side_leak`, and what `close` does — where `close` supplies conditions, the rank
and residual are re-measured on the closed system, so “it closed” is a measurement
rather than a count of conditions.
`--walk` steps a direction the equations leave free and reads the violation’s **order in
`t`** — `O(t²)` is an ordinary second-order obstruction, `O(t)` means an equation is not
describing its constraint.
That distinction is the whole of `D-361`. Which direction it walked is printed, because
there are two: the steepest side-changing one where the null space contains such a
direction, and the free direction itself where it does not, as at Göbel’s `n = 5`.

[`probe_minimal_polynomial`](packing/devtools/probe_minimal_polynomial.py) runs the
integer-relation search under the promotion spec’s frozen margin rule and reports which
clause decided each degree.
It sweeps to the degree the digits reach rather than to a fixed ceiling.
Clause 3 read backwards at the search’s own coefficient bound puts that at **degree 35**
for the `n = 29` refinement at a thousand digits, where the flag used to stop at twenty
for no reason but the default; `--max-degree` still stops it earlier, which is usually
what you want, because the cost is almost all `pslq` and it climbs steeply with the
degree.

[`probe_system_degree`](packing/devtools/probe_system_degree.py) rationalises the
`n = 29` system by the half-angle substitution and reports what bounds the algebraic
degree of the Kingbird solution, which is what says whether an integer-relation refusal
at a given degree surveyed the space or a corner of it.
`--eliminate-side` also solves the smallest equation for `s` and reports the
five-unknown system that leaves.
The `n = 29` sweep takes about twelve minutes, which is why it is a tool with a recorded
result rather than a test.

Both pin their working precision per case and print it beside the number it bounds.
That is not decoration: a rank verdict is a judgement about a gap between singular
values, and at mpmath’s ambient default the gap a probe can *see* is many decades
narrower than the truth, with nothing in the output to say so.

## Safe Refactoring

Use red-green-refactor for a behavior change and characterize intended behavior before a
structural move:

1. Identify the public behavior, persisted record, or scientific claim at risk.
2. Run its focused check and capture the clean baseline.
3. Add a failing test for corrected behavior, or a characterization test for correct
   behavior that is not yet protected.
4. Make one bounded change and keep structural movement separate from semantic change.
5. Run focused tests, Ruff, formatting, types, and the relevant exact, property, replay,
   or differential check.
6. Run full validation at the integration checkpoint.
7. Review a golden diff as a behavior change.
   Never regenerate a golden merely to make validation green.

Tests should be deterministic and behavior-focused.
Avoid network access, wall-clock assertions, uncontrolled randomness,
implementation-detail mocks, and tests that only prove a mock was called.
Include boundary values and failure paths.
A bug fix gets a test that fails for the old defect.
A new guard gets a negative control showing that the named corruption reaches it.

## Hashes and Repository-Owned Artifacts

Git is the integrity boundary for repository-owned sources, golden files, and retained
results. Compare their complete content or regenerate and compare their semantic model;
do not add SHA-256 fields or checksum controls for files committed beside the checker.

A cryptographic checksum is justified only when it is compared with an independently
supplied value across a real trust boundary.
The nearby code or documentation must name that boundary and the failure the comparison
detects. Compact content identities used for deduplication, append-only event ids, or
cache correctness are not integrity claims and must name that separate function.

Pytest collection is explicit in `pyproject.toml`; `tests/conftest.py` fails if the
configured test directory disappears.
Domain programs are named by what they check, not with `_test.py`, so pytest cannot
silently collect or omit them by accident.

## Durable State and Compatibility

Repository-owned callers are migrated together.
Do not retain an alias, wrapper, old module path, or compatibility branch without a
named external consumer.
There are no known external `sqpack` consumers, server APIs, plugin APIs, or databases
at this time.

Campaign, basin-event, atlas, and certificate formats are real persisted contracts.
Version them, reject unsupported versions clearly, and migrate only when retained older
data must remain readable.
Never reinterpret historical records in place.

Write generated views and complete artifacts through `strif.atomic_output_file` so a
crash cannot expose a partial replacement.
Validate before promotion.
Append-only campaign journals are the deliberate exception: each line is independently
validated, and a partial archive is retained as recovery evidence rather than presented
as a complete result.

Generated files name their producer.
Use:

```shell
uv run --frozen packing-ledger check
uv run --frozen packing-ledger render
uv run --frozen python -m devtools.render_defects --check
uv run --frozen python -m devtools.render_research_tables --check
uv run --frozen python -m devtools.render_document_map
uv run --frozen python -m devtools.render_results_headline
```

**Creating any durable Markdown file is a two-step change.** Register it in
[`docs/project/document-map.yaml`](docs/project/document-map.yaml) with its `role`,
`authority` and `lifecycle`, then run `devtools.render_document_map`, because SYNOPSIS
carries a generated copy of that map.
Skipping either step fails `check_documentation` — first with
`unmapped durable document`, then with `SYNOPSIS.md document map is stale`. This is
listed here because the requirement is not discoverable from the Markdown: the registry
is YAML, so grepping `*.md` for a sibling document finds the *rendered* map and not the
source, which is exactly how it gets missed.

## Shell Policy

There are currently no tracked Bash or shell entry points in the packing project, and
the architecture tests guard that state.
Python is the default when a command parses structured data, owns durable state,
branches meaningfully, coordinates subprocesses, handles timeouts, or needs focused
tests. A tiny transparent launcher may be justified, but adding one requires an explicit
architecture-test exception and an explanation of why direct configuration or Python is
less clear.

## Performance Work

Optimize E2 and E3 code only against a representative research loop.
Record the command, inputs, Python and engine revisions, worker settings, warm or cold
state, and the metric being improved.
Profile first; preserve the behavioral and scientific contract; compare before and after
under the same regime.
One-off E1 code need not be optimized unless it materially blocks the experiment that
owns it.

Gate wall time, solver throughput, pair tests, and time-to-retained-result are useful
metrics. Line count, abstraction count, and test count are not performance measures.

### The gate’s standing cost, which a W5 block reads rather than re-measures

A `W5` `efficiency-loop` block on the gate has a baseline before it starts, and the
baseline is not in anybody’s prose:

```shell
uv run --frozen --all-extras --group dev packing-validate --budgets
```

[`packing/devtools/gate-budgets.yaml`](packing/devtools/gate-budgets.yaml) is the
standing measurement.
It carries, per tier, the ceiling the gate enforces, the cost last measured at that
tier’s reference runner, the date and the CI run that measured it, and the argument for
the number. `W5`’s entry contract asks for a baseline, a profile, a target and a guard;
this file is where the first two live for the gate, and the gate keeps them current
itself — a run outside the band fails and prints the figure to write.

**Do not re-measure the gate by hand and record the result in a comment.** That is the
failure `agenda-023` `BC-216` was opened to close: `validate.py` recorded `--fast` at
499 s on 2026-08-30 in a docstring beside an 1800 s cap, the tier reached 1369.60 s six
days later on CI run `33982455466`, and nothing objected, because 1370 is inside 1800
and because 499 was prose.
A number a machine does not read is a number that drifts.

The profile that block worked from, for the next one to start against rather than
rediscover: the tier was one step — `fast behavioral tests` was 1324 s of the 1369.60 s,
96.7 per cent of wall, and every other step in the tier together was about 45 s.
`--edit`, which is every floor and every record check but not the broad suite, was 59.35
s on a contended four-core box the same day.
The target was the operator’s own: a pull-request-blocking surface of at most four
minutes.

### What a deep run repeats, and what that licenses

The deep surface runs on every push to `main`, on the daily schedule and on dispatch,
and nothing about it is scoped to the change.
How much of it repeats work whose inputs did not move is a measurement, and it has a
tool rather than an opinion:

```shell
uv run --frozen --all-extras --group dev packing-validate --format json > run.json
uv run --frozen --all-extras --group dev python -m devtools.measure_gate_repetition \
    --timings run.json --days 30 --attribution
```

It prices every deep run in a window against the run before it, taking reachability from
`Step.touches` and seconds from a real run summary.
A step the summary does not price, prices twice over, or records as skipped is a
refusal, because a step priced at zero repeats for free by arithmetic rather than by
evidence.

Three of its numbers, measured on 2026-09-05 over thirty days, set the shape of any skip
rule and none of them is about `touches`:

- **13 of 70 deep runs ran against a tree that had not moved** since the run before
  them. Every one of those repeated the whole gate.
- **53 of 55 merges to `main` carried a tree byte-identical to the pull-request head**
  merged, so the pull-request surface had already run against exactly those bytes.
- **8 of the 64 steps declare no `touches` at all**, deliberately, and they are the
  expensive ones — so `touches` cannot prune the deep surface by cost.
  The escape hatch that protects a mis-declared pattern is reachable by 17 of 1,933
  tracked files, 0.9 per cent, which is far less protection than its own docstring
  assumes.

**The exact content address here is the git tree id, not a pattern.** Equal tree ids
mean equal bytes for every tracked file, including the code that does the verifying —
which is strictly stronger than hashing the artifacts a step reads.
**But it addresses only the tree**, and three steps in this gate answer to something
else: `campaign record` reads the wall clock and three of its refusals become true with
time alone (an expired lease, a passed session deadline, a passed delegation deadline),
`bead tree` reads the bead store in `.git/tbd/data-sync-worktree`, which is not in any
tree, and `provenance: recorded commits are reachable` reads the git graph and the clone
depth — `D-226` is the run where CI discarded the history its own provenance gate
needed. A rule that skips on tree identity has to keep running those three.
`tests/test_gate_repetition.py` holds the clock counter-example as an assertion rather
than a paragraph.

### Codex research-loop rollups

Use the recursive JSONL scanner when a clocked research session is slow, after a
material validation-surface change, and as an input to a recurring W5 efficiency sample:

```shell
uv run --frozen python -m devtools.codex_log_rollup \
  --sessions-root ~/.codex/sessions \
  --root-id <codex-task-id> \
  --format markdown
```

Repeat `--root-id` to compare task trees, use `--format json` for the stable
`CodexEfficiencyRollup/v2` contract, and add `--include-turns` only when the full turn
tree is needed. The scanner follows descendant task ids, removes inherited history from
current and legacy subagent logs, correlates command polling with its originating
command when the log permits it, and keeps parent active time, recursive agent-time,
active union, and parallel overlap separate.

Interpret the timing bounds literally.
The response envelope is active client time after explicit tools and compaction; it is
an upper bound that still includes API latency, dispatch, suspension, and uninstrumented
gaps. Explicit `Reasoning` and `AgentMessage` item timing is a lower-bound model stream
and is unavailable in older logs.
Do not call either measure provider-side inference latency.
An incomplete live turn ends at its last event, so its totals are lower bounds.

The scanner excludes prompt, message, and reasoning prose from its output, but the
result is not automatically safe to publish: JSON includes local log paths, task ids,
agent paths, token totals, and shortened normalized command excerpts.
Review and reduce a report before retaining it in the repository.
Store compact dated findings and comparison receipts, not raw Codex JSONL or complete
private command histories.

To retain a publishable AgentSession interval, do not archive the full v2 output.
Build the enforced privacy-reduced delta from two explicit cutoffs instead:

```shell
uv run --frozen python -m devtools.codex_task_tree_delta \
  --sessions-root ~/.codex/sessions --root-id <codex-task-id> \
  --start <AgentSession-started_at> --end <snapshot-at> \
  --out campaign/resource-usage/codex-task-tree-<session-id>.yaml
```

`CodexTaskTreeDelta/v1` keeps only additive aggregate counts, timing categories, model
settings and tokens.
It drops prose, paths, child and turn identifiers, and commands.
The AgentSession must declare both the receipt and its operator-attributed `branch`
because Codex records no Git branch; an in-flight snapshot remains a lower bound until a
later checkpoint replaces it.
Declare the receipt by its exact repository-relative path directly under
`packing/campaign/resource-usage/`; basename-only, absolute, traversal and nested paths
are rejected so the checker and renderers cannot resolve different files.

The session schema continues to represent an efficiency session through
`workflow_phases[].workflow: efficiency-loop` and `focus: efficiency`. Recursive timing
belongs in a linked review or versioned scanner artifact because its cardinality and
privacy boundary do not fit the concise session handoff.

## Governing Guidelines

This guide applies the repository guidelines rather than copying them.
Load the current text on demand with `tbd guidelines <name>`; generated `.tbd/docs`
copies are local working state and are not durable link targets.
The applicable names are:

- `general-eng-agent-principles` and `general-coding-rules`;
- `general-tdd-guidelines` and `general-testing-rules`;
- `python-rules`, `python-modern-guidelines`, and `python-cli-patterns`;
- `error-handling-rules` and `backward-compatibility-rules`;
- `golden-testing-guidelines`; and
- `common-doc-guidelines`.

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
