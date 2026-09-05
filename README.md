# Square Packing

Three things here:

- **[New results](#new-results).** The lower bound on `s(11)` has moved.
  It appears to be the first improvement in 23 years on the smallest open case; the
  previous bound, `3.7888543…`, was Stromquist’s in 2003. With it come the first bounds
  located in the public record for twelve, twenty and twenty-one squares, and values
  from `n = 17` through `n = 21` that displace what was in print.
- **[A survey of the whole problem](#survey).** Every case `n = 1…100`, the primary
  literature retained and transcribed, and the bound a source *reports* kept apart from
  the bound this repository has *verified*. Seven of the lower bounds it shows were
  proved here.
- **[An automated research workflow](#autonomous-research-process).** The results and
  the survey are produced and checked by AI agents running a recorded process:
  hypotheses registered before measurement, every claim graded, every defect logged.

The [**explainer page**](https://jlevy.github.io/squares/) is the best introduction to
the proof: the `s(11)` bound and its five conditions in one page, with every figure
drawn from the certificate it explains.

[![One hundred known-best square packings arranged from n equals one through one hundred, each labelled with its best known upper bound and, where the value is still open, the best proved lower bound.](packing/atlas/known-best/known-best-1-100.png)](https://jlevy.github.io/squares/known-best-1-100.pdf)

*The retained `n = 1…100` atlas, with each packing normalized to its own container and
labeled by its best known side upper bound and, where `s(n)` is still open, the best
proved lower bound beneath it.
A crimson star marks a lower bound proved here.
The image is available in [**SVG**](packing/atlas/known-best/known-best-1-100.svg),
[**PDF**](https://jlevy.github.io/squares/known-best-1-100.pdf), and
[**high-rez PNG**](packing/atlas/known-best/known-best-1-100@2x.png).*

`s(n)` is the side of the smallest square that holds `n` non-overlapping unit squares.
The problem is elementary to state and remains open even at small `n`.

[New Results](#new-results) · [Survey](#survey) · [What Is Here](#what-is-here) ·
[Getting Started](#getting-started) · [Reports](#reports) ·
[Autonomous Research Process](#autonomous-research-process) ·
[Conventions](#conventions) · [Layout](#layout)

## New Results

The [results register](packing/frontier/RESULTS.md) collects first-party and
load-bearing whole results.
Each result has a `T-NNN` id and the classifications defined in
[`epistemics.md`](epistemics.md): **V**, the highest verification rung supported by its
cited evidence, and **C**, what this repository has recorded or performed itself.
The gate checks the structural support for both classifications.
`apparently-novel` means a recorded source search did not find the named contribution;
it is not a claim of priority.

Each result also carries **S**, a significance score from `1` to `5` against the same
file’s rubric. The two groups below are split on it rather than on taste: `S4` is its
anchor for a reusable technique, bound family or resolved disputed value, and `S5` for
movement on a central open case.

Results first established here, as far as the recorded source searches show:

### Notable results (`S4`–`S5`)

- **[T-018](packing/frontier/RESULTS.md): `s(11) ≥ 381/100`, the first located public
  movement of the smallest open case since 2003 (`S5`).**
  [`s(11)`](packing/frontier/n-011.md) is the case this project exists for, and the
  recorded public search found no stronger lower bound after Stromquist published
  `2 + 4/√5 = 3.788854` in 2003. A first-party
  [weighted fractional unavoidable-set certificate](packing/cases/n11_fractional_certificate/)
  —1121 weighted atoms, total mass `434547/40000`, every placement of a shrunken square
  covering mass at least `1`—proves that eleven unit squares do not fit in a container
  of side `3.81`. The interval narrows from `0.088230` to `0.067084`; the gap is not
  closed. Two rungs are retained below it: `19/5`, the value that first passed
  Stromquist, and `189/50`, the calibration rung below him that was run first on purpose
  and proves nothing new.
  Scored `S5`, the rubric’s anchor for movement on a central open case.
  The shortest complete statement of the proof, with the certificate’s hash and the one
  command that checks it from the standard library alone, is the
  [proof card](packing/cases/n11_fractional_certificate/t-018-proof-card.md).
  A
  [self-contained package for third-party checking](packing/cases/n11_fractional_certificate/thirdparty/)
  ships with it, so the `19/5` rung can be decided without trusting anything else here.
- **T-019: `s(17), s(18), s(19) ≥ 459/100`, displacing the published value (`S4`).** The
  adopted bound for [these](packing/frontier/n-017.md) three cases was Massaccesi’s
  `4.5058`, taken from a source rather than proved here.
  The same generator returns `4.59`, on 1184 atoms with total mass
  `423327/25000 = 16.9331` against `n = 17` and least covered mass `200009/200000`, so
  the repository now carries a first-party certificate `0.0842` above the number it had
  adopted, with the `229/50` and `451/100` rungs it climbed through retained below.
  One certificate covers all three sizes without a monotonicity step: only `Condition 2`
  mentions `n`, so an atom set certifies its side for every integer above its own mass.
  `T-020` has since carried `n = 19` past it; `n = 17` and `n = 18` are this result’s
  alone, being too small for the heavier atom set that moved the other three.
- **T-020: `s(19), s(20), s(21) ≥ 24/5`, displacing a closed form that stood for twenty
  years (`S4`).** Twenty and twenty-one squares had never had a bound of their own: both
  carried Nagamochi’s 2005 general formula, `1 + √13 = 4.6055…` and `1 + √14 = 4.7416…`,
  and nothing else. A [certificate at `4.80`](packing/cases/n20_fractional_certificate/)
  —2260 atoms, total mass `946131/50000`, least covered mass `50007/50000`—moves
  [`n = 20`](packing/frontier/n-020.md) by `0.194449`, `n = 21` by `0.058343`, and
  `n = 19` by `0.21`, the largest single-case movement in the register.
  The three sizes again come out of `Condition 2` alone.
  Above them the method has `0.1885` of room at `n = 20` and `n = 21` before
  [its own ceiling](packing/frontier/CERTIFICATE-REACH.md), and `0.0856` at `n = 19`
  before it would contradict the best known packing.
- **T-017: `s(12) ≥ 99/25`, from nothing case-specific at all (`S4`).**
  [`n = 12`](packing/frontier/n-012.md) had only the `n = 11` bound inherited by
  monotonicity; the frontier record said in as many words that nothing specific to
  `n = 12` had ever been proved.
  An eight-rung ladder—`19/5`, `77/20`, `97/25`, `39/10`, `393/100`, `197/50`, `79/20`,
  `99/25`—is retained, all from one generator that applies at every `n`, which is why
  this is scored `S4` as a bound family rather than a case result.
  At `99/25 = 3.96` it also separates the cases: `s(12) > s(11)`, since Trump’s 1979
  packing puts `s(11) ≤ 3.877084`. That did not follow from anything on record before.
  The case is now `0.04` from its conjectured optimum of `4`, and no single certificate
  of this shape can close it: none for twelve squares can exist above `3.990816`, which
  is proved here and is below the conjectured value.
  A family of certificates approaching `4` is not ruled out; whether one exists is a
  question about the covering value.
- **T-010: `s(11) ≥ 2 + 4/√5`, repaired (`S4`).** The printed 2003 Figure 14
  unavoidability claim has a strict counterexample, so the literature’s standing `s(11)`
  bound rested on a broken step.
  The
  [case report](docs/project/research/research-2026-08-22-packing-11-unit-squares.md)
  walks through what survived it.
  A preregistered, source-distinct replacement point set restores the full lower-bound
  argument and certifies exactly.
  `T-018` has since passed the repaired value, but the repair is what made it a value
  worth passing.

### Further results (`S2`–`S3`)

Sound and checked, and smaller in reach: a single case, a refinement of one catalogue
annotation, or an erratum.

- **T-001 / T-002: `s(17) ≥ 4.426213` and `s(18) ≥ 4.426213`.** A sixteen-point
  unavoidable set is certified by exact rational cover verification and an independent
  interval branch-and-bound over the full pose space.
  Both are superseded as the verified lower bound: first by the source-backed `4.5058`
  adopted on 2026-09-03, and now by `T-019`, which proves more than either.
- **T-009: `s(29) ≤ 5.93383346267692918974379895098`.** A Krawczyk interval certificate
  encloses a unique exact solution around a rational witness.
- **T-012 / T-013: exact rigidity determinations.** The retained `n = 5` optimum is not
  infinitesimally rigid but is second-order rigid.
  The retained `n = 40` packing is infinitesimally flexible, with every recorded
  first-order flex refused at second order.
  Both refine catalogue annotations that say only “Rigid.”
- **T-014: Goebel’s `n = 5` optimum is locally rigid at fixed side.** At the exact side
  `2 + √2/2` the labeled pose is an isolated point of the feasible set: no nonconstant
  continuous feasible path leaves it and no sequence of distinct feasible poses
  converges to it. Proved exactly over `Q(√2)` from a complete accounting of all 400
  local inequalities, by curve selection and an order-`2m` coefficient induction, and
  independently reviewed.
  The side is fixed throughout; nothing is claimed about an isolation radius, about any
  other `n = 5` optimum, or about global uniqueness, and nothing follows for the side as
  a variable: with the side free the obstruction fails, which X-007 measured.
- **T-005: an erratum in Bentz 2010.** Lemma 10’s middle replacement point is transposed
  in print. An exact escape certificate refutes the printed point, and the corrected
  reading certifies exactly against the journal page image.

### Machine audits of published work

The theorem is the source’s in each of these; the exact machine check is what this
repository adds.

- **T-004 / T-008:** Bentz 2010, Theorem 8, including both halves of `s(46) = 7`.
- **T-011:** exact verification of Trump’s 1979 `n = 11` record witness over its
  degree-eight field, including the zero-gap contacts that finite precision cannot
  certify.

The complete statements, scopes, evidence, limitations, classifications, and next
actions live in the register.
Results that still rest on a source read rather than a machine check are labeled there
accordingly.

## Survey

The survey records the best known packing and best proved lower bound for every
`n ≤ 100`, with provenance and separate reported and formally verified lanes.
Its source is one schema-validated case file under
[`packing/frontier/`](packing/frontier/README.md); the generated
[status table](packing/frontier/STATUS.md) is the reader view, and the atlas above
renders every retained known-best packing.

The [literature archive](packing/resources/README.md) retains each primary source, a
cleaned Markdown transcription, and the unedited extraction used to check it.
The generated [evidence inventory](packing/frontier/INVENTORY.md) shows what each
recorded claim rests on, who performed the work, and how far it has been checked.

The survey audits rather than merely transcribes.
For example, the earliest published proof of `s(7) = 3` carries four recorded defects in
its printed route, so the case’s proved status rests on independent later proofs.
The [`n = 7` case](packing/frontier/n-007.md) states that disposition and links the
relevant source audit.

## What Is Here

| Where | What |
| --- | --- |
| [**Tutorial**](TUTORIAL.md) | First-principles introduction to the objects, bounds, cells, search, and proof obligations |
| [**Synopsis**](SYNOPSIS.md) | Current technical state, established results, terminology, experiment roll-up, and handoff |
| [**Results register**](packing/frontier/RESULTS.md) | Whole-result bounds, audits, structural theorems, and errata graded under [`epistemics.md`](epistemics.md) |
| [**Frontier**](packing/frontier/STATUS.md) | One record per case for `n = 1…100`, with reported and verified bounds kept separate |
| [**Atlas**](packing/atlas/README.md) | Known-best and prospective packings, contact-scaffold enumeration, and deterministic renderings |
| [**Literature**](packing/resources/README.md) | Retained primary sources, cleaned transcriptions, and raw extractions |
| [**Reports**](#reports) | Six research reports on the mathematics, algorithms, infrastructure, formal proof, and search strategy |
| [**Code and development guide**](development.md) | Exact verification, search, promotion, testing, and validation commands |
| [**Campaign record**](packing/campaign/README.md) | Hypotheses, preregistered experiments, session records, agendas, and generated ledger |
| [**Defect log**](defects.md) | Generated record of defects, detection methods, fixes, and regressions |

[`SYNOPSIS.md`](SYNOPSIS.md) is the technical root and current-state document.
The generated day-to-day views are the frontier
[status table](packing/frontier/STATUS.md),
[results register](packing/frontier/RESULTS.md),
[campaign ledger](packing/campaign/ledger.md), and
[agenda map](packing/campaign/agenda-map.md).
To resume work, use the synopsis’s [current handoff](SYNOPSIS.md#current-handoff), which
names the owning work item and next bounded slice.

## Getting Started

Read [`TUTORIAL.md`](TUTORIAL.md) once for the mathematical orientation, then
[`SYNOPSIS.md`](SYNOPSIS.md) for current results and open work.
Run commands from `packing/`; the project uses Python 3.14 through `uv`.

### Essential Terminology

These are the terms a reader encounters most often.
The [synopsis terminology](SYNOPSIS.md#terminology) gives the full definitions.

| Term | Meaning |
| --- | --- |
| **configuration** | A placement of all `n` squares plus the container side: `3n + 1` coordinates |
| **cell** | A separating axis and order for every pair of squares; with angles fixed, one cell is one linear program |
| **quench** | Deterministic refinement from a configuration to a local optimum |
| **basin** | The preimage of one returned pose under a fixed deterministic quench; one connected terminal component may contain several point-basins |
| **polish** | Refinement within the current basin |
| **exploration** | Work intended to reach a different basin; the term implies no assurance level |
| **standing best** | The best published side for that `n`, hence an upper bound rather than known optimality in open cases |
| **gap** | `best_side − standing_best`, always signed |
| **assurance** | `reported`, `numerically-checked`, or `verified`; method, arithmetic, origin, limitations, and novelty are recorded separately |

### Essential Conventions

One id names one durable thing, and ids are not reused.
The prefix identifies the record’s layer; [`conventions.md`](conventions.md#1-identity)
is the definitive registry.

| Id | Names |
| --- | --- |
| `n-NNN` | One frontier case, such as `n-011` |
| `T-NNN` | One whole result in the results register; the synopsis also has older local `T-N` shorthand |
| `X-NNN` | One exploration report from which hypotheses may be derived |
| `H-NNN` | One falsifiable hypothesis or open question |
| `exp-NNN` | One durable experiment record; a lower-level run is one command invocation or seed trial |
| `series-NNN` | One campaign-wide tooling and comparability regime |
| `agenda-NNN` | One ordered queue of bounded commitments |
| `BC-NNN` | One bounded commitment in an agenda; other agendas may declare another two-letter prefix |
| `session-NNN` | One escalated agent-session record containing ordered workflow phases |
| `D-NNN` | One defect and its detection, consequence, fix, and regression |
| `think-xxxx` | One git-native `tbd` bead: durable work and dependency state |
| `W1`–`W10` | A workflow entry point, not a durable artifact id |

Other rules needed to read the repository:

- Structured values live in YAML or frontmatter; prose supplies explanation and
  judgment. A consumer does not scrape prose for fields.
- Declared paths are repository-relative.
  Generated views are regenerated from their source records and are not edited by hand.
- Evidence assurance, method, origin, precision, limitations, and novelty are separate
  facts. Whole-result V/C classifications do not replace evidence-level fields.
- Source-faithful archive material is not cleaned up as project prose.
  Reconstructed source text is marked and counted.
- Corrections preserve the original record and add a dated statement of what remains
  valid. Ids and scientific outcomes are not silently rewritten.

### Technical Stack

The project keeps numerical exploration, symbolic reconstruction, exact verification,
and research records as separate layers.

| Layer | Tools | Role here |
| --- | --- | --- |
| Work and issue state | [`tbd`](https://github.com/jlevy/tbd) | Git-native beads, dependencies, specs, guidelines, and handoffs |
| Structured research records | [`softschema`](https://github.com/jlevy/softschema), [PyYAML](https://github.com/yaml/pyyaml), [Python `jsonschema`](https://github.com/python-jsonschema/jsonschema), and [`jsonschema-rs`](https://github.com/Stranger6667/jsonschema) | Mixed prose-and-data artifacts, JSON Schema contracts, in-process checks, and fast repository-wide validation |
| Documentation | [Flowmark](https://github.com/jlevy/flowmark) and [Practical Prose](https://github.com/jlevy/practical-prose) | Semantic Markdown formatting and the common documentation guidelines |
| High-precision numerics | [mpmath](https://github.com/mpmath/mpmath) | Arbitrary-precision refinement, interval endpoints, and decimal-to-exact promotion |
| Arrays and optimization | [NumPy](https://github.com/numpy/numpy) and [SciPy](https://github.com/scipy/scipy) | Geometry arrays, nonlinear refinement, and fixed-cell linear programs |
| Symbolic mathematics | [SymPy](https://github.com/sympy/sympy) | Contact-system assembly, elimination probes, minimal-polynomial recovery, and independent symbolic checks |
| Exact mathematics | `sqpack.field`, `sqpack.verify`, and the case-specific certifiers | Rational and algebraic sign decisions, unavoidable-set certificates, Krawczyk enclosures, and proof replay |
| Parallel search | The local `sqsearch` crate, [Rayon](https://github.com/rayon-rs/rayon), and the [Rust toolchain](https://github.com/rust-lang/rust) | Multicore `f64` screening and annealing; formal promotion remains on the Python side |
| Python environment and QA | [uv](https://github.com/astral-sh/uv), [Ruff](https://github.com/astral-sh/ruff), [BasedPyright](https://github.com/DetachHead/basedpyright), and [pytest](https://github.com/pytest-dev/pytest) | Locked environments, linting, formatting, type checking, and behavioral tests |
| Git hooks | [lefthook](https://github.com/evilmartians/lefthook) | Runs the pinned Markdown formatter and re-stages its changes before commit |

The dependency and tool versions are owned by
[`packing/pyproject.toml`](packing/pyproject.toml),
[`packing/uv.lock`](packing/uv.lock),
[`packing/sqsearch/Cargo.toml`](packing/sqsearch/Cargo.toml), and the root `Makefile`
and hook configuration.
[`development.md`](development.md) explains how the layers interact.

### Core Commands

```shell
uv sync --frozen --all-extras --group dev
uv run --frozen packing-witness inspect witnesses/schadt-n029-2025-decimal.yaml
uv run --frozen packing-witness check witnesses/schadt-n029-2025-decimal.yaml \
  --method numerical-multiprecision --precision 300 --tolerance 1e-100
uv run --frozen packing-witness verify witnesses/schadt-n029-2025-rational.yaml
uv run --frozen python -m cases.trump11.verify_exact
uv run --frozen --all-extras --group dev packing-validate --edit
```

[`Witness/v2`](packing/witnesses/witness.schema.yaml) is the interchange format for
supported rational, algebraic, and decimal witnesses.
Exact verification covers rational witnesses and algebraic witnesses whose field
preconditions the tool can certify.
Recovering exact geometry from arbitrary decimal input remains the hard step;
[`development.md`](development.md) and the module docstrings under
[`packing/src/sqpack/`](packing/src/sqpack/) define the supported APIs and limits.

[`sqpack.render`](packing/atlas/rendering/README.md) creates deterministic,
self-contained SVG figures while preserving the input’s evidence tier in captions and
metadata. The rendering guide owns the CLI, gallery, contact annotations, portability
contract, and Motion Lab.
The Motion Lab is an exploratory instrument, not a citable research result.

## Reports

These six research reports are the durable topical syntheses:

| Report | Scope |
| --- | --- |
| [Packing 11 Unit Squares in a Square](docs/project/research/research-2026-08-22-packing-11-unit-squares.md) | What is proved for `s(11)`, what remains conjectural, and why the available proof techniques do not close the gap |
| [Algorithms and Tooling for Square Packing](docs/project/research/research-2026-08-22-square-packing-algorithms-and-tooling.md) | Search, numerical-to-exact promotion, verification, and the record landscape |
| [FrankenSim as a Rust Toolkit for Square Packing](docs/project/research/research-2026-08-22-frankensim-rust-toolkit-for-square-packing.md) | Assessment of certified-arithmetic and determinism components in a larger Rust framework |
| [Infrastructure for Square-Packing Exploration](docs/project/research/research-2026-08-22-infrastructure-for-packing-exploration.md) | Build order, latency tiers, language boundaries, and symbolic tooling |
| [Lean for Square-Packing Proofs and Validation](docs/project/research/research-2026-08-22-lean-for-packing-proofs-and-validation.md) | Where proof assistants fit and which certificate layers are suitable first targets |
| [A Search Philosophy for Square Packing](docs/project/research/research-2026-08-23-search-philosophy-and-landscape-cartography.md) | Basin cartography, structural diversity, relaxation ladders, and search strategy |

The reports distinguish formal proof, finite numerical checks, and source reports.
The [document map](SYNOPSIS.md#document-map) identifies every maintained guide, dated
record, generated view, and superseded document.

## Autonomous Research Process

The repository supports autonomous research without making process a substitute for
evidence. This section gives the operating model at a glance.
The [operating rules](operating-rules.md),
[workflow contracts](SYNOPSIS.md#workflow-entry-contracts), and
[campaign runbook](packing/campaign/README.md) own the full rules.

### Assurance and Verification

Evidence uses three assurance labels:

- **reported** for a named source claim not checked here;
- **numerically-checked** for finite-precision calculations with their precision,
  rounding, and tolerance recorded; and
- **verified** for an exact check, rigorous interval certificate, or complete proof that
  covers the claim and its preconditions.

Whole results use the separate V/C classifications in [`epistemics.md`](epistemics.md).
A verified feasible witness proves an upper bound; it does not prove global optimality
without a matching verified lower bound.

Finite precision is not enough for a packing with exact contacts.
Floating-point arithmetic can establish a strict positive gap, but a tolerance that
accepts a true zero-gap contact also accepts a smaller overlap.
Exact algebraic signs or outward-rounded intervals are therefore required before a
contact-heavy witness becomes formally verified.
The synopsis explains the full argument in
[Why Exactness Is Not Optional](SYNOPSIS.md#why-exactness-is-not-optional).

Two retained examples show the boundary.
The Schadt `n = 29` decimal pose passes its declared 300-digit numerical check, while
the separately promoted interval witness establishes a slightly weaker side rigorously.
Trump’s `n = 11` witness is verified exactly over a degree-eight number field, including
fourteen zero-gap contacts.
The per-case records ([`n = 29`](packing/frontier/n-029.md),
[`n = 11`](packing/frontier/n-011.md)) state exactly which bound each artifact proves.

Verification answers whether a proposed packing is valid.
Proving it optimal is a different problem and requires a matching lower bound.
The synopsis’s [capability ladder](SYNOPSIS.md#verification-capability-ladder)
distinguishes what is built, what is ordinary engineering, and what remains
mathematically contingent.

### Operating Principles

| Principle | Focus | Goal |
| --- | --- | --- |
| **Correctness** | Soundness | Formal validation that third parties can inspect, plus cross-validation of claims and source summaries |
| **Process** | Discipline | The minimum effective structure that keeps consequential decisions, evidence, and handoffs reconstructible |
| **Insight** | Creativity | Freedom to understand the problem, form varied hypotheses, and use all available information and tools |
| **Efficiency** | Infrastructure | Faster iteration through measured improvement of algorithms, systems, tools, and research surfaces |

Correctness is the veto: no result advances beyond its evidence, however costly the
required check may be.
Process is proportional infrastructure, not a second mathematical standard; missing
evidence can block promotion, while a preferred form or checkpoint cannot block useful
work merely because it looks more disciplined.
Insight remains free to propose.
Efficiency may simplify process but cannot lower the assurance bar.

### Layers of Work

The system separates the kind of effort, the lens used to judge it, and the bounded
action being executed:

| Layer | Question | Recorded as |
| --- | --- | --- |
| Operating principle / focus | What quality dimension is preeminent for this phase? | `correctness`, `process`, `insight`, or `efficiency` |
| Workflow | What durable result is this phase meant to produce? | One of W1–W10, or the narrow maintenance fallback |
| Slice | What bounded action is being performed now, and how will it be checked? | Objective, intended artifact, focused validation, and stop condition |

Focus and workflow are independent.
A W6 experiment may emphasize correctness, insight, or efficiency without changing its
promise to execute a preregistered measurement; an efficiency-focused phase does not
become W5 unless its durable result is a measured performance decision.
A slice is smaller than either: it is one action inside the declared phase.

The durable work objects also have different lifetimes:

| Unit | Lifetime and role |
| --- | --- |
| Packing exploration | The self-contained repository: sources, research, code, records, and tools |
| Campaign | The multi-session research program and its shared record contract |
| Series | A campaign-wide tooling regime and comparability boundary |
| Bead (`think-xxxx`) | A durable work item and dependency node, open until the work is settled |
| Bounded commitment (`BC-NNN`) | A planned attempt with entry conditions, acceptable exits, owner, and budget |
| Agent session | An escalated interval of coordinated work containing one or more workflow phases |
| Workflow phase | One declared purpose and focus within a session |
| Slice | One bounded, immediately checkable action within a phase |
| Exploration / hypothesis | A recorded source of ideas / one falsifiable claim with its criterion fixed before measurement |
| Experiment / run | One durable measured round / one lower-level invocation or seed trial |
| Result / ledger | One typed observation or whole-result claim / a generated view over source records |

A bead says what needs doing.
A bounded commitment says what would count as settling one attempt.
A workflow phase says what kind of move is being executed now.
One bead may require several commitments, one commitment may span several phases, and
one phase may produce zero or several scientific records.
The [work-unit definitions](SYNOPSIS.md#work-units-and-records),
[campaign runbook](packing/campaign/README.md), and
[agent-session guide](packing/campaign/agent-sessions/README.md) own the exact
contracts.

### Workflow Entry Points

Choose the workflow whose durable result matches the task.
The [synopsis](SYNOPSIS.md#workflow-entry-contracts) owns the complete entry, exit, and
transition contracts.

| ID | Workflow | Enter when | Durable result | Usual handoff |
| --- | --- | --- | --- | --- |
| W1 | `research-survey` | The sourced state of knowledge is incomplete | A sourced survey, source notes, conflicts, and explicit gaps | W2 |
| W2 | `factual-review` | Existing claims need a correctness-only audit | Findings, authorized bounded corrections, or defects; no new theory smuggled into the review | W3 or W4 |
| W3 | `insight-iteration` | Current evidence needs new explanations or hypotheses | Candidate `X-NNN`/`H-NNN` items with mechanisms, falsifiers, and information value | W6 |
| W4 | `process-review` | Work is hard to reconstruct or the discipline itself needs review | Process findings, beads, and narrowly scoped contract or check changes | W5 or the next owning workflow |
| W5 | `efficiency-loop` | A measured bottleneck limits useful iterations | A baseline, profile, equivalence-safe change, and measured decision | W6 |
| W6 | `research-loop` | A registered hypothesis has a fixed criterion, regime, budget, and instrument contract | A frozen instrument and one or more `exp-NNN` records, raw evidence, verdicts, and a current ledger | W2 for promoted or high-risk claims; otherwise W3 or another W6 slice |
| W7 | `pipeline-improvement` | A named packing-pipeline surface or research consumer needs a new, stronger, simpler, or repaired capability | A bounded implementation or refactor, executable controls, explicit evidence limits, cost receipt, and readiness decision; no scientific verdict | W2 before a materially changed trust boundary reaches W6; otherwise W5 or W6 |
| W8 | `documentation-pass` | A period of research has left the reader-facing documents behind what the record now says | Reconciled root documents—README, tutorial, synopsis—checked against the artifacts and against each other, with every drift either fixed or logged as a defect; no new claim introduced | W2 for any claim the pass could not verify; otherwise the next owning workflow |
| W9 | `remediation` | Confirmed defects or issue backlogs need a systematic repair wave | Risk-ranked dispositions, bounded repairs, regression checks, updated defect records, and rerouted blockers; no scientific verdict | W10 |
| W10 | `review-planning-oversight` | An agenda or consequential session has ended and its results must change the plan | Result and stop-reason classifications, actionable dispositions, reader-document review, a reprioritized candidate set, and one selected next entry | The selected workflow; W9 or W8 when remediation or documentation work wins |

Use `general-improvement` only for repository maintenance that fits none of W1–W10.
Routine work records a workflow, bounded objective, intended artifact, and focused
check. Use a versioned [agent-session record](packing/campaign/agent-sessions/README.md)
only when work crosses multiple workflow phases, coordinates independent delegates, or
needs durable recovery state.

### Defects and Corrections

[`defects.md`](defects.md) is generated from
[`packing/defects.yaml`](packing/defects.yaml).
It records every known defect in this toolchain, what caught it, the consequence, the
correction, and the regression that now guards it.
Two lessons govern review:

- Results that look unusually good receive the strongest challenge because many
  soundness defects have pointed in that direction.
- The automated gate checks only rules someone encoded.
  No soundness defect in the log was caught by it.

Current counts and detector statistics belong only in the generated defect log and the
[synopsis defect section](SYNOPSIS.md#the-defect-record).
Corrections follow [`conventions.md` §7](conventions.md#7-corrections): preserve the
original record, add a dated correction that states what remains valid, and route any
changed conclusion to the artifact that owns it.

### The Autonomous Work Loop

W6 is the measured experiment loop rather than an umbrella for every session:

```text
W3 insight iteration → registered hypothesis → W6 measured round → evidence and verdict
          ↑                                                        │
          └──────── successor questions ← W2 factual review ←──────┘
```

The hypothesis, criterion, regime, budget, and stop rule are fixed before measurement.
The round records every outcome and stops at the criterion or clock.
Promoted, novel, disputed, or otherwise high-risk claims receive an independent W2 pass
before they move forward; routine rounds whose recorded guards already decide the
criterion may return directly to W3 or another W6 slice.

The `tbd` queue owns durable work and dependencies.
Campaign agendas order bounded commitments; hypothesis and experiment records own
scientific claims and measurements; commits own code; escalated agent-session records
own phase and recovery state.
The key record ids are `X-NNN` for explorations, `H-NNN` for hypotheses, `exp-NNN` for
experiments, `BC-NNN` for bounded commitments, `T-NNN` for registered results, and
`D-NNN` for defects.
[`conventions.md`](conventions.md#1-identity) owns the complete id registry.

The campaign’s
[bounded research cycle](packing/campaign/README.md#the-bounded-research-cycle) defines
clocks, result routing, budgets, and stop rules.
Changing agents changes the driver, not the record or the evidence required for a claim.

### Where the Contracts Live

| Document | Definitive responsibility |
| --- | --- |
| This README | High-level orientation and the relationship among the layers |
| [`SYNOPSIS.md`](SYNOPSIS.md) | Current technical state, full workflow contracts, work-unit vocabulary, and handoff |
| [`epistemics.md`](epistemics.md) | Whole-result V/C/S/N classifications and their executable boundary |
| [`conventions.md`](conventions.md) | Ids, filenames, artifact shape, evidence fields, provenance, and corrections |
| [`operating-rules.md`](operating-rules.md) | How sessions choose, divide, validate, and hand off work |
| [Campaign runbook](packing/campaign/README.md) | Hypothesis and experiment mechanics, clocks, budgets, verdicts, and routing |
| [W9 remediation pass](packing/campaign/remediation-pass.md) | Systematic defect and issue-backlog triage, repair waves, and terminal dispositions |
| [W10 review, planning, and oversight](packing/campaign/review-planning-oversight.md) | Post-agenda result classification, document review, reprioritization, and next-entry selection |
| [Agent-session guide](packing/campaign/agent-sessions/README.md) | Escalation threshold, workflow phases, recovery state, and session closeout |
| [Agendas](packing/campaign/agendas/) | Mutable ordering and readiness of bounded commitments |
| [`development.md`](development.md) | Engineering boundaries, commands, tests, and validation tiers |

## Conventions

[`conventions.md`](conventions.md) owns identifiers, filenames, artifact discipline,
evidence fields, provenance, corrections, and the boundary between machine checks and
review. [`epistemics.md`](epistemics.md) owns whole-result classifications.
[`operating-rules.md`](operating-rules.md) owns how sessions are conducted, and
[`development.md`](development.md) owns the engineering and validation workflow.

## Layout

```
.
├── TUTORIAL.md             First-principles orientation for a newcomer
├── SYNOPSIS.md             Current technical state, results, terminology, and handoff
├── conventions.md          Artifact, identifier, evidence, and correction rules
├── epistemics.md           Whole-result verification and confirmation rubric
├── operating-rules.md      Session conduct and workflow rules
├── development.md          Python setup, engineering boundaries, and validation
├── defects.md              Generated view of packing/defects.yaml
├── docs/project/           Reports, reviews, specs, postmortems, and dated handoffs
├── docs/project/research/  The six research reports listed above
├── packing/                Code, data, and the research record
│   ├── campaign/           Hypotheses, experiments, sessions, agendas, and ledger
│   ├── frontier/           Per-case claims, evidence, generated views, and results
│   ├── witnesses/          Witness/v2 interchange and retained examples
│   ├── golden/             Calibration endpoint snapshots
│   ├── atlas/              Known-best, prospective, enumerated, and rendering artifacts
│   ├── resources/          Retained literature and source-faithful transcriptions
│   ├── src/                Maintained sqpack package
│   ├── cases/              Case- and theorem-specific retained code
│   ├── devtools/           Checkers, adapters, generators, and mutation controls
│   ├── benchmarks/         Explicit performance probes
│   ├── tests/              Behavior, command, and architecture contracts
│   ├── sqsearch/           Rust screening annealer
│   ├── defects.yaml        Structured defect log
│   ├── defects.schema.yaml Defect-log contract
│   └── frankensim-probe/   Focused experiments against FrankenSim
├── vendor/kpress/          Vendored kpress submodule: the page's rendering layer
├── AGENTS.md               Project instructions for agents
├── CLAUDE.md               Bridge to AGENTS.md
├── Makefile                Markdown formatting, hooks, and skill mirroring
├── lefthook.yml            Pre-commit Markdown formatter hook
├── package.json            Tooling-only lefthook package
└── package-lock.json       Tooling lockfile
```

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
