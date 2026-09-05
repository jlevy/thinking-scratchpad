# Project Instructions for AI Agents

This file provides instructions and context for AI coding agents working on this
project.

<!-- BEGIN TBD INTEGRATION format=f08 surface=agents-md -->
## tbd

This repository uses **tbd** for git-native issue tracking (beads), spec-driven
planning, and on-demand engineering guidelines.
As the agent, you operate tbd on the user’s behalf: translate their requests into tbd
actions rather than telling them to run commands.

- Run `tbd prime` to load current project state and the full tbd workflow.
- Run `tbd skill` for the complete reusable tbd skill instructions.
- Run `tbd shortcut --list` and `tbd guidelines --list` for on-demand resources.
- Track all work as beads: `tbd create`, `tbd ready`, `tbd close`, and `tbd sync`.

<!-- END TBD INTEGRATION -->

## Operating Rules

Generated from [`operating-rules.md`](operating-rules.md), which carries the evidence
for each rule. Edit there, not here.

<!-- BEGIN OPERATING RULES SUMMARY -->

- **OR-1:** Build the tool; never leave a measurement in one-off code.
- **OR-2:** Run three to five sub-agents, at a thinking level matched to the task.
- **OR-3:** Never wait on a gate with nothing else in flight.
- **OR-4:** Take the next slice from the handoff, not from the backlog.
- **OR-5:** Declare the workflow entry point before beginning.
- **OR-6:** Plan multi-hour work in slices before starting it.
- **OR-7:** Run the documentation guidelines pass at block boundaries.
- **OR-8:** A self-declared budget is not a stop condition.
- **OR-9:** A pull request leads with what the branch cost.
- **OR-10:** Treat matched agent and host handoffs as continuation, not a reset.
- **OR-11:** Close an agenda through disposition and reprioritization.
- **OR-12:** One block in four to eight is an efficiency block, and the record says
  which.
- **OR-13:** Every fast check runs in CI; only the unavoidably slow ones leave.

<!-- END OPERATING RULES SUMMARY -->

## Build & Test

**This project runs Python 3.14. Never invoke the `python3` on `PATH`** — it is older,
and the two interpreters disagree about what parses.
Run `uv run --frozen ...` from `packing/`, or `packing/.venv/bin/python3` directly.

The trap this closes is specific and has caught four sub-agents:
[PEP 758](https://peps.python.org/pep-0758/) makes `except A, B:` valid without
parentheses, so files using it parse under the project interpreter and are reported as
syntax errors by anything older.
`sqpack/assurance.py` and `sqpack/contacts.py` both contain the construct and both are
correct. A report that they do not parse is a report that the wrong interpreter was used
— see [`D-397`](defects.md), and `OR-2` for the three occurrences before it.

The repository is mostly prose.
The only repo-wide tooling is Markdown formatting.

```bash
make hooks-install   # once after cloning: installs the lefthook pre-commit hook
make format          # format all Markdown
make format-check    # report drift without writing
```

Ruff and BasedPyright run at zero findings over every tracked Python file, the
hand-written skill assets at the repository root included; `print` is allowed only in
the tools (`devtools`, `cases`, `tests`, `benchmarks`, the console scripts), and the two
standalone verifiers under `packing/cases/n11_fractional_certificate/` run on any
CPython 3.12 or later by design.
Python, Rust, and research validation are documented in
[`development.md`](development.md).
Run them from `packing/`, which is where the project’s `pyproject.toml` and lockfile
live: `uv run --frozen --all-extras --group dev packing-validate --edit` while editing,
`packing-validate --push` before any push (the edit tier plus the tests reachable from
the change), and the full `packing-validate` at a research or merge checkpoint.

### Markdown formatting

**Flowmark owns all Markdown here.** Do not add Prettier, Biome, or dprint Markdown
handling alongside it — two Markdown formatters churn each other’s output and make hooks
nondeterministic.

Formatting is applied **automatically on commit** by a lefthook `pre-commit` hook, which
formats and re-stages the result (`stage_fixed: true`). You should never need to format
by hand, and unformatted Markdown is not something you can commit by accident.

Formatting drift deliberately **does not fail CI**. It is fixed at commit time instead,
so style never blocks a build.
`make format-check` exists for ad-hoc checking, not as a gate.

Two rules worth knowing before changing any of this:

- **Exclusions are evidence-based, not precautionary.** The policy is to format the
  whole repository and exclude only what we have a tested reason to leave raw.
  The exclusions, each with its reason in `.flowmarkignore`: the literature archive
  under `packing/resources/`; generated files, from the `SKILL.md` files to the rendered
  registers and the claim documents, whose own renderers drift-check them; two dated
  reviews whose quoted sources the formatter would retype; and the vendored submodules.
  The archive is excluded for two measured reasons: the `.raw.md` extractions are
  byte-level ground truth and the formatter rewrites them (about 2,600 lines across two
  files), and formatting the transcriptions would change transcribed characters — smart
  quotes, ellipses — against the rule that archived source is never edited to look tidy.
  Math is not a reason: the pinned `flowmark-rs==0.4.0` keeps every one of the archive’s
  7,618 `$...$` spans whole, and
  `uv run --frozen --group dev python -m devtools.check_math_spans FILE...` from
  `packing/` re-measures that on a copy of any file with the `Makefile`’s pinned
  command, reporting every span that changed, gained a newline, or went missing.
  Do not drop or narrow the exclusion without re-measuring.
- **The hook formats the whole repository, not the staged files.** Flowmark reads
  `.flowmarkignore` relative to its target argument, so passing explicit paths silently
  bypasses the exclusion list.
  That matters here: `.flowmarkignore` protects `packing/resources/`, where the
  `.raw.md` extractions are byte-level ground truth used to check the model-assisted
  transcriptions against.
  Reflowing them would void that guarantee.
  Do not “optimise” the hook to `{staged_files}`.
- **The flowmark version is pinned** in the `Makefile` (currently the latest Rust build,
  `flowmark-rs==0.4.0` — the Rust port is the fast one).
  Pinned rather than floating so it is not an unpinned zero-install runner, which
  `tbd guidelines supply-chain-hardening` rule 6 warns against.
  Bumping the pin is a deliberate, reviewable change.

Emergency bypass: `git commit --no-verify` (avoid in PRs).

## Architecture Overview

The repository is split by audience rather than by topic.

**The root holds what a reader wants**, where it is visible on arrival:
[`README.md`](README.md) as the front door, then [`TUTORIAL.md`](TUTORIAL.md),
[`SYNOPSIS.md`](SYNOPSIS.md), [`conventions.md`](conventions.md),
[`development.md`](development.md), the generated [`defects.md`](defects.md), and
`docs/project/` for reports, reviews, specs and postmortems.

**[`packing/`](packing/) holds everything that is code, data, or research record**: the
`sqpack` package and its tests, the developer tools, the Rust search engine, the
literature archive, the frontier register, the atlas, the witnesses, and the campaign.
Keeping that one level down is what stops the root from becoming unreadable, and it is
also the build root — `pyproject.toml`, `uv.lock` and `.python-version` live there.

Two rules follow from the split, and both exist because a path now has two plausible
meanings:

- **Every declared path in the record is repository-relative.** That covers
  `recorded_in` in `packing/defects.yaml`, the document map, the logbook’s
  pipeline-change paths, and the verified-upper-bound consumer contract.
  One root, one meaning, and a path that reads the same wherever it appears.
  A packing-relative path in any of those places is a bug.
- **Python path constants name which root they mean.** `ROOT` (also `PROJECT_ROOT`,
  `PACKING`) is `packing/`; `REPO` is the repository root.
  A constant pointing at a document that lives at the root resolves from `REPO`.
  `sqpack` itself finds the project by marker discovery rather than a fixed depth, so it
  does not care where the checkout sits.

The standalone research reports this repository once carried, on topics unrelated to
packing, live in [jlevy/thinking](https://github.com/jlevy/thinking).

## Conventions & Patterns

- **The project is self-contained.** Its documents, sources, and code live in this
  repository and link to each other with relative paths.
  Reader-facing prose belongs at the root; code, data, and the research record belong
  under `packing/`. Do not add a third top-level tree for either.
- **Reports separate claims by evidential status** — proved, computationally verified,
  best known, or asserted-but-unverified — and cite primary sources near the claims they
  support.
- **How work is conducted is not in this file.** Workflow entry points, session slicing,
  sub-agent use, and the rest are [`operating-rules.md`](operating-rules.md); the
  summary above is the whole of what belongs here.
- **Archived source material is never edited to look tidy.** Where a transcription
  reconstructs damaged text, it is flagged inline and counted in the archive README.

<!-- BEGIN FLOWMARK INTEGRATION format=f03 surface=agents-md -->
## flowmark

Auto-format Markdown with `flowmark` for clean, semantic git diffs.

- Run `flowmark --auto <files>` on Markdown you create or edit.
- Run `flowmark --docs` for full usage and `flowmark --skill` for the skill.
- If `flowmark` is not on `PATH`, use a pinned `uvx` runner (never `@latest`).
- Fast Rust port (recommended): `uvx --from flowmark-rs==0.4.0 flowmark`.
- Python build (library / newest patch): `uvx --from flowmark==0.8.0 flowmark`.

<!-- END FLOWMARK INTEGRATION -->

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->

<!-- BEGIN PPROSE INTEGRATION format=f02 -->
## Practical Prose (pprose)

Practical Prose: an evaluation toolkit and editorial workflows for practical documents.
Use when the user asks to improve, audit, score, or compare practical documents.

For durable Markdown documentation, use `pprose-common-edit` whenever creating, editing,
reviewing, or reorganizing it, unless the task is explicitly read-only.
Keep the required guideline footer intact.

Apply AI-slop reduction whenever drafting or editing prose, not only on request: use
`pprose-de-slop` to remove AI-writing tells and formulaic LLM prose, applying its
bundled catalog contextually and preserving meaning and voice.

Discover the tool from the CLI itself: `pprose --help` for commands, `pprose about` for
the project narrative, `pprose skill` for the workflow skills, and `pprose list` for
every on-demand guideline, shortcut, and runbook
(`pprose guidelines|shortcut|runbook <name>` prints one).

Run pprose as `pprose <command>` if on PATH, else `uvx pprose@0.4.0 <command>`
(zero-install via uv).

<!-- END PPROSE INTEGRATION -->
