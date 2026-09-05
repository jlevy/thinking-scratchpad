# Conventions for `packing/`

**The definitive registry of every convention and naming this project uses.** Where
another document restates an id or naming convention, this one wins.
This page governs the *shape of what is produced*; how a session is conducted is
[`operating-rules.md`](operating-rules.md), and a rule about agent conduct belongs there
rather than here.
Changing program status remains owned by `SYNOPSIS.md`, and schemas and
source artifacts remain authoritative for their own fields and evidence.
Read this before adding an artifact, workflow phase, round, series, or tool.

Each rule is marked **[checked]** when something fails on a violation, or
**[convention]** when it rests on care alone.
The distinction is the point, but it is not a mandate to mechanize every sentence.
A check must protect a named mathematical, reproducibility, navigation, or operational
benefit and must be cheaper to maintain than the failure it prevents.
If that case is not concrete, keep the convention in prose or remove it.
`packing-validate` is the authoritative checking surface.

## 1. Identity

One id per thing, three digits, never reused.
The prefix says what kind of thing it is.

| Layer | Id | Scope | Example |
| --- | --- | --- | --- |
| Campaign | contract namespace | the directory | `packing.squares` |
| Series | `series-NNN` | campaign | `series-000` |
| Experiment | `exp-NNN` | **campaign, not series** | `exp-003` |
| Hypothesis | `H-NNN` | campaign, spans series | `H-016` |
| Exploration report | `X-NNN` | campaign | `X-001` |
| Agent session | `session-NNN` | campaign | `session-001` |
| Agenda | `agenda-NNN` | campaign | `agenda-001` |
| Agenda cell | `AA-NNN`, prefix declared per agenda | its agenda | `BC-001` |
| Frontier case | `n-NNN` | `frontier/`, one artifact per `n ≤ 100` | `n-011` |
| Search/proof strategy | `search:N`, `proof:N` | the frontier catalogues | `search:12` |
| Defect | `D-NNN` | the directory, logged in `defects.yaml` | `D-014` |
| Bead | `think-xxxx` | the repository’s `tbd` queue (prefix set in `.tbd/config.yml`) | `think-1s0h` |
| Theoretical result | `T-NNN` | the results register, [`packing/frontier/results.yaml`](packing/frontier/results.yaml), under [`epistemics.md`](epistemics.md); `SYNOPSIS.md`’s legacy single-digit `T-N` ids remain that document’s declared shorthand | `T-001` |
| Review finding | `R-N`, `F-NN` | the review document that declares them | `R-2`, `F-07` |
| Basin (planned) | canonical key, plus a `B-NNN` alias | campaign, spans series | — |

**Experiment ids do not restart at `exp-001` in each series, and this is deliberate.** A
series is a directory and a field, not a namespace.
`exp-003` names one experiment record forever, wherever it lives, which is what makes
cross-series references work—and they are common: a series’ `carries_forward` names
rounds from an earlier one, a hypothesis aggregates rounds across all of them, and the
atlas will cite the round that discovered a basin.
Per-series numbering would make every one of those a compound key, and a bare `exp-001`
in prose would be ambiguous.

The series is never lost, because the experiment records it in a `series:` field and
lives in that series’ directory.

`series-000` predates strict application of this boundary and now contains heterogeneous
calibration and exact-determination work.
Its
[series note](packing/campaign/series/series-000-smoke-and-calibration/README.md#current-scope-and-safe-reading)
states the safe reading; `think-i08r` owns the all-at-once record migration.
Do not use that legacy container as the template for opening another series.

One experiment artifact records one round of research.
Use **round** for the performed work or its sequence position and **experiment** for the
durable `exp-NNN` record.
A lower-level **run** is one command invocation or seed trial; one experiment may
aggregate many runs.
Agent sessions have their own `session-NNN` ids and may produce zero or many
experiments.

**Cardinality**, so the shape of the record is unambiguous:

| Relation | Cardinality |
| --- | --- |
| experiment → series | exactly one |
| experiment → hypotheses | **exactly one** under the current contract; the field remains an array for format compatibility |
| hypothesis → experiments | zero or more—sweep cells and replications |
| hypothesis → exploration reports | zero or more (`derived_from`) |
| hypothesis → strategies | zero or more (`strategy_refs`) |

So `exp-` does **not** map one-to-one onto `H-`: one hypothesis may aggregate many
experiments. Four experiments currently reference `H-016`: one historical three-cell
round and its three per-cell replacements.
A round does not apply its one verdict to several hypotheses.

**Ids are never reused, and never renumbered except on merge collision.**
[checked: whole-set uniqueness] When two branches collide, the newer campaign renumbers
and the change is recorded as an annotation on the affected artifacts, never as a silent
edit. Sequential defect IDs are branch-provisional: the later branch takes the next free
IDs at merge and updates its references in the same change.
Do not reserve IDs or add a second coordination ledger.

**Reserved ids.** [checked] No hypothesis ids are currently reserved.
A future reservation is declared in a `reserved-ids` comment on the idea board and names
a claim that exists upstream but is not yet codified.
A reserved id may be *named* but not *linked*, and a reservation that has been fulfilled
is flagged stale.

## 2. Naming

**Files and directories carry the full id followed by a kebab-case slug.** [checked]

```
campaign/series/series-000-smoke-and-calibration/
campaign/series/series-000-smoke-and-calibration/experiments/exp-003-baseline-n11-target.md
campaign/hypotheses/H-002-lp-in-cell-polish.md
campaign/explorations/X-001-standing-review-and-search-philosophy.md
campaign/agent-sessions/session-001-pr15-review-reset.md
campaign/series/series-000-smoke-and-calibration/results/exp-003-baseline-n11-target.jsonl
```

The id in the filename must equal the id in the frontmatter.
[checked] Raw run data takes the id of the round that produced it.

Research documents and reviews keep the repository’s dated form:
`research-YYYY-MM-DD-topic.md`, `review-YYYY-MM-DD-topic.md`.

**A case-local document for a registered result is named for the result and for what it
is: the lowercase result id, then a descriptive kebab-case suffix.** [convention]
`t-018-proof-card.md` and `t-018-verifiable-claim-19-5.md` each say which result and
which kind of document; a generic name in capitals such as `VERIFIABLE-CLAIM.md` says
neither, and the second such file would have to fight the first for it.
There will be many proofs and claims, and each needs a unique, self-describing name.
This is a filename convention only: prose and structured records keep the canonical
uppercase id `T-018`. `README.md` remains the exception for a directory’s orientation
page. The kinds in use, each generated from the certificate so its figures cannot drift:
`t-NNN-proof-card.md`, the one-page statement with every constant and the one command
that checks it; `t-NNN-verifiable-claim-<bound>.md`, the self-contained claim with
theorem, proof, verifier and certificate, one per retained bound; and
`t-NNN-proof-visual.svg`, the figure.
A new result takes the same names with its own id.

Use [`repren`](https://github.com/jlevy/repren) for renames—it moves files and rewrites
references in one pass, which is what keeps the two in step.

## 3. Artifacts

**Frontmatter is authoritative; the body is for people.** [checked: schema] A consumer
reads the YAML and must not parse prose for structured values.
The body carries the judgement, the history and the caveats—the things that would be
lies if forced into a field.

**Every artifact declares its schema and is validated against it.** [checked]
`status: enforced` means something fails when the artifact is wrong.
An artifact that declares a schema nothing loads is the exact failure this project keeps
finding in its own sources.

**Promote a value into YAML only when something consumes it**—the accept rule, the
ledger, the checker.
[convention] Everything else is prose.

**Add process only for a named benefit.** [convention] A new field, table, digest, or
gate states the failure it prevents and the artifact or check that demonstrates the
benefit. Repetition and the appearance of formality are not reasons.
Git already tracks repository-owned source bytes; a second checksum beside the file adds
no evidence. [`development.md`](development.md#hashes-and-repository-owned-artifacts)
owns the narrow exceptions for real trust boundaries, deduplication, event identity, and
cache correctness.

**Schemas own local structure; checkers own relationships between fields and
artifacts.** [checked] Put a rule in a checker when it needs a tailored diagnostic,
reads another artifact, or merits a negative control.
Keep required keys, types, enums, and other record-local constraints in the schema.

**A case package’s `certificate.json` is a pointer, not a name.** [checked] It holds the
rung currently in force, and it moves when a better one lands; a rung that has been
displaced keeps its own `certificate-<side>.json` and never moves again.
So a record citing a rung as evidence cites the immutable filename.
Citing the pointer says “whatever is best today”, which is a different claim and becomes
a false one the moment the ladder climbs—`D-458`, where a superseded row quoted its own
successor’s atoms. The check is a round trip: every frozen artifact a register row names
must recompute to that row’s own side, which is the one comparison a moving pointer
cannot survive.

### Workflow, Focus, Phase, and Slice

**Workflow names purpose and output; focus names the primary quality emphasis.**
[checked for agent sessions] The ten numbered workflows and their full contracts live in
[`SYNOPSIS.md`](SYNOPSIS.md#workflow-entry-contracts).
Routine work declares its workflow, objective, artifact, and focused check where the
work is already tracked.
It does not create a session artifact merely to duplicate those facts.
`general-improvement` is reserved for genuine repository maintenance outside W1–W10 and
the packing pipeline, not a label for mixed or ordinary core work.

**Session records are an escalation, not the default.** [checked once present] Use
`AgentSession/v2` for multi-phase work, long autonomous supervision, independently
tracked delegation, expensive experiment or proof supervision, or a consequential
recovery handoff.
Once opened, one phase declares one workflow and one primary focus; the
other principles still constrain and may contribute to the work.
A review document may be committed on its review branch and becomes durable when that PR
merges. Do not create a separate default-branch copy or publication mechanism.

**Implementation stays with its owning workflow.** [convention] Bounded research
corrections stay in W1 or W2, idea probes in W3, process and checker repairs in W4,
measured optimizations in W5, one-round registered instruments in W6 before measurement,
reusable packing-pipeline capabilities, targeted refactors, robustness, visualization
infrastructure, and cleanup in W7, reconciliation of the reader-facing tier in W8,
bounded defect repair in W9, and terminal review, disposition, and replanning in W10.
There is no undefined implementation handoff, and W10 selects but does not execute the
successor.

**A documentation pass reconciles; it does not author.** [convention] W8 may correct,
cut, reorder and clarify the root documents against the artifacts, and may not introduce
a claim the record does not already carry — a document that wants to say something new
is asking for W1 or W6. Where a document and an artifact disagree and the artifact is
not obviously right, the output is a defect rather than a rewrite: a pass that quietly
picks the more readable side is how a wrong claim becomes the tidy one.
Its checklist is the
[documentation-pass runbook](packing/campaign/documentation-pass.md).
Every W10 closeout performs the smaller document-impact review even when it finds
nothing to change; it opens or selects W8 only when the reader-facing tier needs a
substantive reconciliation.

**Remediation is a bounded wave, not a backlog-shaped phase.** [convention] W9 begins
from confirmed defects or issues with risk ordering and owning beads.
It groups only repairs that share a trust surface, preserves the scientific criteria it
touches, and gives every selected item a terminal disposition with evidence.
Its procedure is the [remediation runbook](packing/campaign/remediation-pass.md).

**Agenda closure includes oversight and one next entry.** [checked] W10 classifies each
attempt at the smallest honest scope, gives it an actionable disposition, reconciles
files, validation, documents, and live tbd state, records operator confirmation or
unavailability, ranks the retained candidates, and selects exactly one successor.
Its procedure is the
[review/planning/oversight runbook](packing/campaign/review-planning-oversight.md).

**A registered result is presented, not just recorded.** [checked] Every result whose
significance was scored inside an agenda’s wall appears, with its `V`/`C`/`S` rungs and
the rubric’s own words for that score, in two places a reader meets first: the synopsis
headline block and the pull request, above the commitment-keyed dispositions.
The clause exists because Agenda 016 did the assessment and skipped the presentation --
`T-014`, `T-015` and `T-016` were registered, reviewed and scored `S3`, and the
published synopsis then mentioned no score until 400 lines in while the pull request
carried none at all for two of the three.
Both surfaces are generated from `results.yaml` through `devtools/significance.py`, so
the obligation is discharged by rendering rather than by remembering, and
`devtools.render_results_headline --check` fails when it is not.

**A phase is contiguous; a slice is bounded.** [checked for phase history] Start a new
phase when workflow, focus, or the bounded slice objective changes.
A focus-only change repeats the workflow and is not a workflow switch.
A renewed slice may repeat workflow and focus only after closing the prior phase and
stating a changed objective and renewal reason.
A momentary change of emphasis is not a phase.
A slice is one time-bounded action inside the phase and need not produce an experiment.
Mechanical delegations inherit the coordinating phase unless they open independently
tracked sessions.

**Versioned transitions are recorded before the new work begins.** [checked] A phase
opens with its expected output, validation command, kill condition, fallback, start, and
deadline. Its actual outcome and evidence are terminal fields.
The first phase uses `session_start` and no switch reason; later phases name a planned
checkpoint, evidence checkpoint, or user request, and close the old phase before
entering the new one.
Sessions 001–008 predate this convention.
Their v2 workflows are retrospective reconstructions from retained evidence and are not
preregistration evidence.

## 4. Evidence

**Assurance, method, and arithmetic are separate.**
[checked: schemas and semantic validation]

| Assurance | Meaning | Formal? |
| --- | --- | --- |
| `reported` | A named source states the claim; the frontier has not established it independently | no |
| `numerically-checked` | A finite calculation checked the declared predicates under explicit arithmetic, precision, rounding, and tolerance | no |
| `verified` | An exact check, rigorous certificate, or complete proof decides the claim and its preconditions | yes |

Methods name how the result was obtained: `numerical-f64`, `numerical-multiprecision`,
`interval-certified`, `exact-algebraic`, `published-proof`, `proof-audited`, or
`proof-assistant-checked`. Every numerical result records the precision actually used
and its tolerance. A multiprecision library does not make a result arbitrarily precise,
and a tolerance of `1e-100` is still numerical.

**`beat_record: true` requires `assurance: verified`.** [checked] Campaign semantic
validation rejects a numerical record flag.
A numerically checked candidate may be compared with a reported value in prose, but it
cannot enter the formal frontier lane.
A verified feasible witness proves an upper bound only; optimality requires a matching
verified lower bound.

**Verification origin remains visible.** [checked: evidence contract] External proof,
independent external certificate, repository replay, and repository audit are separate
facts. Running the source generator’s own checker is useful evidence but does not become
an independent implementation.

**Claims are separated by assurance**—reported, numerically checked, or formally
verified—and citations sit near the claims they support.
“Verified” is reserved for the formal level.
[convention]

**The rubric that ranks whole results lives in [`epistemics.md`](epistemics.md), not
here.** [checked: `devtools/check_results.py`] This section defines the recorded
fields—assurance, method, precision, origin, review state—that its verification and
confirmation ladders derive from.
The ladder vocabulary (`V0`–`V5`, `C0`–`C5`, significance, novelty as applied to whole
results) is defined there and only there, and the results register at
`packing/frontier/results.yaml` is where a whole result’s rungs are declared and
re-derived on every validation run.

**Reserve `C0`–`C5` for confirmation levels.** [convention] Numbered hypotheses or
checks inside a proof are written as **Condition 1**, **Condition 2**, and so on, never
with abbreviated letter-C labels.
This keeps local proof notation from colliding with the repository’s result-level
confirmation ladder.
Verbatim source archives and literal third-party machine identifiers may reproduce
external letter-C notation; they are preserved evidence or syntax, not repository
terminology.

**Budgets are in pair-tests**, tiers S/M/L = `1e9`/`1e11`/`1e13`. [convention]
Machine-independent, and comparable across proposers whose move semantics differ.
Wall clock is reported alongside as a courtesy, never as the budget.

**Two things compared at different budgets have not been compared.** [convention]

## 5. Notation and Terminology

**One document owns each vocabulary, and the rest are short forms.** [convention]
[Assurance and method](#4-evidence) above are definitive here, and the schemas enforce
them; the result-level epistemic vocabulary is owned by
[`epistemics.md`](epistemics.md).
Mathematical terminology is defined in [`SYNOPSIS.md`](SYNOPSIS.md#terminology);
[`TUTORIAL.md`](TUTORIAL.md) §9 and [`README.md`](README.md)’s Essential Terms are short
forms that may abbreviate but must not contradict it, and a term either appears in the
synopsis or is marked local where it is used.
Both restatements have drifted from it before.

**Mathematical notation follows four rules.** [convention]

- **A subscript `i` names one square; a bare letter is the whole `n`-vector.** So `θᵢ`
  is one angle and `θ` is all `n` of them, and “fix the angles” means fix every `θᵢ`.
- **`s(n)` is the optimal side and `s` is the decision variable** of a linear program.
  They are not interchangeable: one is the answer, the other is what a solver moves.
- **A `*` marks a distinguished value, not one fixed relation.** `a*` is a minimiser;
  `s*` is the standing best for an `n`, which is *not* known to be a minimum in the open
  cases. Never read `s*` as an optimum.
- **A gap is qualified.** A **bound gap** is the distance between the best upper and
  lower bounds for an `n`, a property of the problem.
  A **search gap** is `best_side − standing_best`, signed, a property of one run.
  Bare *gap* means the search gap, which is the sense the synopsis and the campaign
  artifacts use; write the qualifier wherever both senses are in play.

**The symbol table lives in [`TUTORIAL.md`](TUTORIAL.md) §10**, in the order a reader
meets each symbol, and is the place to look up a letter.
[convention] The rules above are what other documents must not violate; the table is how
a newcomer learns them.

**Neighbouring research reports predate these rules and are not being retrofitted.**
[convention] The `n = 11` report writes `θ` for the shared class angle the tutorial
calls `a`, `u_i` for a per-square half-angle parameter rather than a single primitive
element, and `α` for two quantities unrelated to a field’s primitive element.
Those documents are dated records; the tutorial’s notation card names the collisions so
a reader crossing between them is warned.

## 6. Provenance

**Numbers are lifted from run data, never retyped.**
[convention, spot-checked by review] The tables in a round’s body are derived from its
archive.

**An archive must regenerate what its round claims.** [checked for the current rounds]
Every archived record re-derives its own reported side from its own coordinates.

**A recorded commit must be an ancestor of the branch being merged.** [convention]
`exp-001` violates this—its commit was orphaned by a rebase—and carries an annotation
saying so. The reachability gate requires full Git history.
A shallow checkout that does not contain the recorded commit is uncheckable, not
evidence that the commit was orphaned.

**Guards are recomputed, not remembered.** [checked: selftest] The overlap reported for
a configuration is recomputed from that configuration, never read off an accumulator
maintained across hundreds of millions of updates.

## 7. Corrections

**The record is corrected by addition, never rewritten.** [convention] A defective
artifact gets a dated annotation stating what still stands and what does not.
`exp-001` carries three.

**Views are generated and never hand-edited.** [checked: drift] `campaign/ledger.md` and
the frontier tables inside the research documents rebuild from their artifacts; the gate
fails if a committed view is stale.
Generated files are excluded from formatting, because a formatter and a generator will
fight forever.

**The idea board is the one hand-written link in the chain.**
[checked: two-way reconciliation] It is an *input*, not a view, so it is reconciled
against the registry rather than regenerated: every `H-NNN` it names exists, and every
registered hypothesis appears on it.

## 8. Ownership

**Once codified, the registry artifact is canonical.** [convention] The standing
review’s register entry becomes historical.
Beads track build work, never scientific claims—a bead may say “build the instrument for
H-002”, never “H-002 is confirmed”.

**One series is open at a time.** [checked]

**The runbook is frozen while rounds are running.** [convention] The accept rule, the
tolerances, the metric vector and the control cells do not change mid-series.

## 9. Layers That Must Not Blur

**`sqpack` owns validity.
`sqsearch` owns move-loop energy.** [checked: differential test] `pair_depth` is a
metric shaped for annealing, not a verdict, and a second implementation at that layer is
fine—as long as it never gets to say what is valid.
20,000 near-contact pairs are checked against the oracle on every full validation run.

**Proposers propose and nothing else.** [convention] A proposer never quenches,
canonicalizes, decides validity, or writes the atlas, so a new strategy cannot change
what a basin means.

**The vocabulary is fixed, and controlled collisions are explicit.** [convention]
[`SYNOPSIS.md`](SYNOPSIS.md#terminology) defines every term this directory uses in a
narrow sense—campaign, session, experiment, round, run, quench, basin, polish,
exploration, gap, assurance, method, pair-test and the rest—and those definitions apply
in artifacts, beads and reviews.
Write **packing exploration** for the project directory, **exploration report** for
`X-NNN`, and bare **exploration** for reaching another basin.
Write **cell** alone for a cell of configuration space—a choice of separating axis and
order for each pair—**instance cell**, never bare “cell”, for a position in a sweep, and
**event cell**, never bare “cell”, for a region of centres on which a certificate’s
covered mass is constant.
The three are unrelated objects and the confusion is expensive: one is where the LP is
solved, one is what a round is run on, and one is where a lower-bound certificate’s mass
is decided.

## 10. Code and Docs

**Python first; accelerate what a profile says is slow, not what looks slow.**
[convention] The measurements behind this are in the
[plan spec](docs/project/specs/active/plan-2026-08-22-minimal-packing-toolkit.md#stack-and-boundaries--decided-by-measurement).

**Python 3.14 is the sole supported runtime, and dependencies are locked.** [checked]
`pyproject.toml`, `.python-version`, Ruff, BasedPyright, CI, and `uv.lock` express one
runtime policy. Development commands run through the locked uv environment described in
[`development.md`](development.md).
The one deliberate exception is the standalone verifiers under
`packing/cases/n11_fractional_certificate/`, which a reader runs outside this
environment: they are standard library only and run on CPython 3.12 or later.

**Code is segregated by maturity and consequence.** [checked] Maintained foundations,
reusable research components, case-specific evidence, developer tooling, and tests live
in separate module families.
The dependency rules and E0–E3 expectations are defined in
[`development.md`](development.md#code-maturity-and-placement).

**Markdown is formatted by flowmark**, automatically on commit.
[checked: hook] Exclusions are evidence-based, not precautionary, and each one states
its measured reason in [`.flowmarkignore`](.flowmarkignore).

**Custom formatting in a kpress-rendered document is plain HTML.** [convention] A block
is a `<div class="…">` with a blank line after the opening tag and before the closing
one, so the Markdown inside it still renders; an inline run is a `<span class="…">`; a
figure is `<figure>` with a `<figcaption>`, which kpress decorates itself.
Class names are kpress’s where it styles the block — `hero`, `subtitle`, `boxed-text`,
`shaded-text`, `claim`, `summary`, `key-claims`, `centered-headers` — and the document’s
own only where kpress has none.
No attribute sugar (`{.class}`, `[text]{.class}`) and no `:::` containers: the div and
span pass-through is the one kpress guarantees without configuration, it survives its
sanitized mode, and GitHub renders the same blocks as plain HTML. The explainer template
([`explainer-article.md`](packing/devtools/templates/explainer-article.md)) is the
worked example.

**Relative links must resolve.** [checked] The campaign’s checker walks every relative
Markdown link. This project has needed that twice.

**Docs follow the common documentation guidelines** and carry the footer.
[checked: document map] The map covers every durable project document, distinguishes
current authority from dated records and transient plans, checks local links, and
generates the synopsis view.

## 11. What the Gate Actually Enforces

`packing-validate` runs its registered read-only steps concurrently and replays their
output in declared order.
`packing-validate --list` prints the authoritative names and tiers; the `STEPS` table in
`src/sqpack/cli/validate.py` is the only registration point.
What they enforce, grouped:

**Mathematics, checked exactly where the claim is formal.** Exact verification of the
Trump, Göbel, and retained rational `n = 29` witnesses, including an independent
rational checker; negative controls showing why finite precision cannot certify a
contact; field irreducibility and unique-root isolation; the degree-8 field re-derived
independently (where sympy is installed); the fixed-angle cell rebuilt as a linear
program through independent constraint rows and solved back to Trump’s packing; Trump’s
exact branchwise linearized cones (exp-013); the H-041 repaired-cover exact certificate
and the H-010 printed-cover exact rejection (exp-016, exp-017); the exact `n = 3, 4`
optimal moduli (exp-014, exp-015); the exact terminal-component controls and `n = 5`
local-geometry results through exp-036; and the golden basin maps, whose proved-case
rows are checked against mathematics rather than against a stored snapshot.

**Instruments.** `sqsearch --selftest` (geometry against a naive reference, determinism,
the `s(5)` positive control, the recomputed-overlap guard); the differential test
between search energy and the validity oracle; the basin atlas store invariants; the
basin event record and its replay; basin identity; and the historical regressions each
earlier defect fix left behind.

**The record.** Frontier corpus structure, its reported/formal separation, source
coverage, and soft-schema validation; generated status and research tables in sync with
the frontier data; both strategy catalogues; the document map and local links; the
defect log (schema, contiguous ids, open defects carrying beads, links resolving, the
generated view in sync); `SYNOPSIS.md` and `README.md` reconciled against the artifacts
and the directory; the campaign record (schema validation, id uniqueness, dangling
references, verdict rules, idea-board reconciliation, ledger freshness); provenance
(every round’s recorded engine commit reachable, or annotated); the bead tree; and the
skills mirrored between `.agents` and `.claude`.

**Hygiene.** The lint floor (ruff, ruff-format and basedpyright on the Python; clippy
pedantic and rustfmt on the Rust); the soundness perimeter (every component that emits a
configuration is checked by `sqpack` through code it does not share); and the negative
controls in `devtools/controls.yaml`, each a mutation that must be caught in a private
source snapshot.

A skipped check is recorded and re-listed at the end.
`--strict` enables deep golden regeneration and turns every skip into a failure; failed
or incomplete strict surfaces always return nonzero.

**Run the cheapest loop that answers the current question.** Research rounds remain
separate from edit and validation loops, so a long hypothesis does not set the cost of a
documentation correction:

| Loop | Command or instrument | Use |
| --- | --- | --- |
| Interactive | Targeted pytest, checker, verifier, or engine self-test | Answer one local question while editing |
| Focused | `packing-validate --only TEXT` | Run one named validation surface and its controls |
| Records | `packing-validate --records` | Check registries, generated views, and declared contracts |
| Edit | `packing-validate --edit` | Run the normal low-latency editing floor |
| Pre-push | `packing-validate --push --since origin/main` | Add behavioral tests reachable from the change |
| Full | `packing-validate` | Check a commit, cross-component handoff, or merge checkpoint |
| Strict/deep | `packing-validate --strict` and, when producer output matters, `--deep` | Refuse skips and rebuild expensive producers before an unattended campaign or dependent handoff |
| Research round | A preregistered W6 instrument | Run candidate generation or proof search under its declared timebox |

The split follows what each step detects.
Do not copy measured latencies into durable guidance; use the validator transcript when
cost affects a decision.

Three properties make the split safe rather than merely cheaper, and each is a test:

- **The tiers nest.** `--records` is contained in `--edit`, contained in `--fast`,
  contained in the full run — checked as sets, so swapping two steps between tiers
  cannot pass by keeping the totals equal.
- **Every step is reachable from the full run**, so a step can be deferred to a wider
  tier and never dropped out of all of them.
- **Exclusion is opt-out.** A new step joins `--edit` unless explicitly marked `broad`,
  so forgetting the marker makes the tier slower rather than blinder.

Being outside `--edit` is not being outside the gate.
CI runs the full gate on every push, so the split changes feedback latency rather than
coverage.

A checkpoint merge may retain a known strict/deep failure when the normal gate passes
without skips, the exact failure and its limitation are recorded in the defect log and
PR, and an open bead owns the repair.
That merge preserves reviewed work; it does not certify the failed producer or authorize
an unattended campaign.
The strict gate remains mandatory before the deep handoff or launch that depends on it.

## 12. What This Page Is Not

**A file-system map is [`README.md`](README.md); a procedure is
[`operating-rules.md`](operating-rules.md) or a runbook.** This page carries the
systematic formats that would otherwise be handled inconsistently: ids, naming, artifact
and schema shape, notation, provenance and correction form, layer boundaries, and coding
conventions. Where a family of them is large enough to stand alone it may live in a
nested `conventions.md` that this one references, rather than growing this page.

The W8 checklist is the
[documentation-pass runbook](packing/campaign/documentation-pass.md), because a
checklist for running a pass is a procedure rather than a convention.

## Defect Classes

One taxonomy, used by [`defects.yaml`](packing/defects.yaml), by the beads (as a
`defect-class:` label), and by any review that reports a problem.
They are separated because they cost completely different things, and treating them
alike is how a critical bug gets the same attention as a stale link.

| Class | The system … | Costs |
| --- | --- | --- |
| **soundness** | asserted something false about the mathematics | a wrong published result; the only class that can |
| **validity** | was correct, but the measurement did not bear on the question | an empty experiment, and the budget spent on it |
| **bookkeeping** | recorded something its own evidence contradicts | misdirected future work; an archive nobody can trust |
| **robustness** | did not finish, or finished only by luck | time, and silently censored data if papered over |
| **performance** | worked, but cost far more than it should | throughput, and the experiments not run because of it |

Soundness and validity defects additionally record a **direction**: `flattering` errors
overstate the result and are the dangerous kind, because they look like success;
`conservative` errors understate it and primarily cost effort or opportunity.
Current totals and detector statistics belong in the generated defect log.
[checked]

A soundness defect gets a postmortem, not just a fix—see
[the first one](docs/project/postmortems/postmortem-2026-08-23-soundness-class.md),
whose rules R1–R4 define the defenses required for new soundness-sensitive code.
[convention]

## Defects

Every defect found in this toolchain is recorded in
[`defects.yaml`](packing/defects.yaml) and rendered to [`defects.md`](defects.md).
A defect is a bug, an inefficiency, or a record that disagreed with its evidence—not an
approach tried and rejected on its merits, which belongs in `campaign/ideas.md` under
Dead ends.

Two fields carry most of the value and are worth filling in honestly rather than
generously. `detected_by` says what *actually* caught it, which is how we learn which
detectors to build more of.
`regression` names the check that now prevents recurrence, and the literal `none` is a
legitimate and useful answer—the generated view collects those into the list that
predicts what will come back.
[checked]

Open defects must carry a bead, soundness and validity defects must state whether the
error flattered or understated the result, and every row must point at the artifact
carrying its narrative.
[checked]

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
