# Feature: Unattended Square-Packing Research Readiness

**Date:** 2026-08-23; rebuilt from the merged baseline on 2026-08-24

**Author:** Codex agents

**Status:** Active agenda; numeric launch is **NO-GO**

## Outcome

There is enough organized work for an autonomous **agent** to make useful progress for
eight or twenty-four hours.
There is not yet enough admissible, executable numerical work for
[`packing-campaign`](../../../../packing/src/sqpack/campaign/runner.py) to run
unattended.

The distinction matters:

- the portable outer work loop controls research, implementation, review, delegation,
  verification, recording, and selection of the next ready bead; a native agent goal or
  watchdog may supervise it but is not its source of truth;
- `runner.py` is only the executor for preregistered numerical cells whose instruments,
  evaluators, budgets, and validity paths already exist.

The runner currently reports one executable recipe, H-017. On the recorded local M1 Pro
rate it is about **2.8 hours** of work, not a night.
More importantly, D-044 and D-046 remain open: the current path trusts producer-reported
validity and does not yet form a closed, checked lifecycle.
The scientifically admissible unattended queue is therefore zero.

This document is the single launch agenda.
It supersedes the earlier “build Half A, then drain the census” schedule and the two
older overlapping overnight epics.
Existing beads retain their history and now sit under `think-ydus`.

## What success means

The goal is not to keep a machine busy.
It is to make the next morning’s state more truthful, more informative, or more capable
without requiring a person to reconstruct what happened.

An eight-hour session is ready when:

1. a persistent agent can drain dependency-ready research and implementation beads,
   committing bounded evidence-backed changes as it goes; and
2. if numerical work is delegated to the runner, its **measured unresolved-cell queue**
   has at least ten hours of useful work on the target host and every cell passes the
   launch gate below.

A twenty-four-hour session raises the second threshold to thirty hours.
The 1.25× reserve absorbs runtime variance and finalization without changing criteria at
night.

## The four focuses

Agents normally own one primary focus at a time.
The handoffs between them are explicit because one dimension cannot substitute for
another, while the other three principles continue to constrain and contribute to every
phase.

| Focus | Governing question | Durable outputs | Veto |
| --- | --- | --- | --- |
| **Correctness** | Is the mathematical or computational claim supported? | primary-source notes, certificates, independent checks, soundness defects | may reject a promotion or result |
| **Process** | Can another agent reconstruct the decision and continue it? | hypothesis, experiment, session and defect artifacts; beads and generated views | may reject an unregistered or irreproducible run |
| **Insight** | Which sharp experiment or proof idea buys the most information? | hypotheses, open questions, mechanism metrics, strategy changes | may reject low-information scaling |
| **Efficiency** | What measured bottleneck limits useful iterations? | timings, budgets, profiles, resumable execution, visualizations | may reject unmeasured infrastructure work |

Visualization belongs to both Insight and Efficiency: the infrastructure must render the
atlas, ambiguity graph, discovery curve, and continuation tree, while the research work
decides which views expose mechanisms rather than decorate a report.

A focus is a quality dimension, not a workflow.
Before taking work, choose W1–W10 from the
[workflow entry contracts](../../../../SYNOPSIS.md#workflow-entry-contracts), then
declare the primary focus inside that phase.
A focus-only change starts another phase under the same workflow; a changed purpose
starts a different workflow.
W7, `pipeline-improvement`, owns reusable packing-pipeline capabilities, targeted
refactors, robustness, visualization infrastructure, and cleanup for named research
consumers. W6 retains only instruments specific to one registered round that freeze
before measurement. `general-improvement` is only for genuine repository maintenance
outside W1–W10 and the packing pipeline.

## Measured checkpoint — 2026-08-24

This table is a dated planning checkpoint, not a generated current-status view.
The campaign ledger owns cumulative round and effort totals.

| Item | Current fact | Consequence |
| --- | --- | --- |
| Scientific registry | 41 artifacts: H-001 through H-041, including seven explicit open questions | The census spine now sits beside local geometry, construction, exact-value, algebraic and asymptotic lanes |
| Recorded campaign | [Generated ledger](../../../../packing/campaign/ledger.md#effort): 36 terminal rounds, 868 agent-minutes, 28.2 wall-minutes at this checkpoint | The loop remains overwhelmingly agent-bound |
| Operational runner queue | one H-017 cell, five seeds, recipe timebox 8h | “Queue nonempty” is not an overnight-readiness test |
| Estimated H-017 runtime | 2.80h at 39.7M moves/s locally; 7.46h at the recorded 14.9M moves/s cloud rate | Target-host calibration is mandatory |
| Fast checks | status 0.22–0.24s; preflight 0.12s; ledger 0.23s; schemas 1.60s; engine selftest 1.43s | Orientation and focused feedback are already cheap |
| Normal gate | 31 steps in 103.91s at the W7 and frozen-queue checkpoint, including 51 pytest contracts and 62 mutation controls | Green checkpoint evidence; not permission to run the red deep producer unattended |
| Canonicalizer | 0.098s at `n=7`, 7.91s at `n=9` in one audit | Likely census bottleneck; confirm under `think-xzew` before redesign |

The existing preflight is useful but not a launch decision.
It proves that its current guards fire and that at least one recipe is visible.
It does not independently verify a pose, price the queue, bind the session deadline, or
rehearse crash persistence.

## Successive-`n` Confidence Ladder

The active, mutable experiment order now lives in the
[basin-map confidence ladder](../../../../packing/campaign/agendas/agenda-001-basin-confidence-ladder.md).
That soft-schema artifact is the handoff surface for one series of loops: every item
states whether it is validating the tools, validating the measurement system, or asking
a genuine research question; it also names the size, budget, entry condition, exit
evidence, bead, and dependencies.

This document continues to own broad launch readiness and the portfolio below.
The ladder owns the frequently revised order of concrete cells.
`SYNOPSIS.md` owns current knowledge, hypotheses own claims, experiments own
measurements, beads own unfinished work, and an escalated agent-session artifact owns
the bounded outer clock when durable supervision or recovery state is needed.
None is a duplicate runner queue.

Outside the dated frozen portfolio below, do not copy the current ready item into this
plan.
The agenda frontmatter and generated ledger own that volatile state; this plan owns
the launch boundary.
The dependency ladder keeps tool validation, measurement validation, and research
distinct, so a clean program execution cannot silently become evidence about the
landscape.

## Frozen Eight-Hour Agent Portfolio

This is the launch queue for `think-3cbq`, the planned `session-010`. It remains frozen
after the dated reconciliation below because raw `tbd ready` is a dependency view, not
an unattended-session agenda.
The coordinator may re-screen this list at a checkpoint, but may not invent another task
merely to keep the session busy.

The outer agent campaign is a **conditional go** from one clean, pushed commit whose
normal gate is green.
PR 26 may be integrated at a bounded phase boundary if its live head is fully reviewed,
mergeable, and green; it does not delay the launch.
PR 25 is outside this session.
The generic numerical runner, `packing-campaign run`, remains a **no-go**. So do
delegated strict or deep gates: D-239 lacks outer validation deadlines, and D-202/D-217
show that a finished delegated command can still lose its terminal receipt.

### Launch-Base Reconciliation — 2026-08-25

The session branch starts from `8136f21`, the merge of PR 28 into `main`. The queue was
reconciled against that tree before the session clock opened:

- `think-l1us` is closed and PR 22’s merge commit `1244634` is an ancestor of the base;
- `think-cns0` is closed and its process-timeout implementation commit `ecf5b29` is an
  ancestor of the base through merged PR 23;
- stopped session-009 owner `think-05hr` is closed without closing its independent child
  work; and
- `think-b3bm` is open and unclaimed rather than inheriting the stopped session’s
  `in_progress` state.

The focused launch gate passed 15 of 31 selected steps in 13.17 wall-seconds.
The normal gate then passed all 31 steps in 121.19 wall-seconds, including 51 behavioral
tests and 62 mutation controls.

Before treating any future branch-ahead implementation as landed, record its commit and
run `git merge-base --is-ancestor <implementation-commit> <session-base>`. Exit zero is
the landed-state evidence; a closed bead or passing branch is not.

Open `session-010` with an offset-aware start and deadline exactly eight hours apart,
`wall_minutes: 480`, `max_cycles: 15`, and `finalization_minutes: 45`. Every ordinary
slice declares `clock_role: work`, ends before the reserve, and retains the runbook’s
ten-minute orientation, twenty-minute evidence checkpoint, and thirty-minute hard stop.
Order 15 is the sole `clock_role: finalization` phase.
No line receives a third consecutive slice.
A continuation closes its old phase and names the new evidence, changed objective, and
fresh clock that earn another attempt.

One coordinator owns the registry freeze, shared campaign artifacts, defect log,
workflow transitions, long commands, integration, commits, and final receipts.
A delegate gets one task and at most thirty minutes.
A task that may cross the twenty-minute checkpoint or run a process receives the full
durable contract: disjoint write scope, exact frozen validation command, kill condition,
fallback, and explicit command exclusions.
A shorter read-only derivation may inherit the phase and return one compact terminal
receipt without first creating a queued row.
It never chooses its own successor, changes branches, allocates an experiment id, edits
the registry during W6 measurement, or runs a strict/deep gate.
Disjoint read-only derivations and code probes may overlap; gates, timing measurements,
and shared-record writes may not.

| Order | Workflow and focus | Bead | Maximum | Durable exit | Kill line and frozen fallback |
| ---: | --- | --- | ---: | --- | --- |
| 1 | W4 `process-review` / Process | `think-k68v`, then `think-3cbq` | 1 slice | Reconciled landed-versus-branch-ahead claims, one active `session-010`, and a clean base receipt from `packing-ledger check` plus `packing-validate --fast` | If ownership is still ambiguous at thirty minutes, freeze writes and allow only the source-bound W1 fallback |
| 2 | W6 `research-loop` / Insight | `think-nm35` | 1 slice | Exact branchwise ray or face inventory for the remaining `n=5` cones modulo exp-034, or a finite unresolved list; validate through `small-n exact models and local geometry` | Stop at thirty minutes without a component, census, or unequal-side claim; fall back to order 8 |
| 3 | W2 `factual-review` / Correctness | `think-nm35` | 1 slice, only after order 2 yields a candidate result | Independent branch-coverage and claim-scope disposition, with mutations or a defect where the checker can flatter | Any omitted branch or non-independent replay keeps BC-010 ready; do not repair inside W2 and continue at order 4 |
| 4 | W7 `pipeline-improvement` / Correctness | `think-nr5w` | 1 slice | Millisecond `n=4`, seed-0 fixture retaining theta, cell, solver inputs, status, and replay—or the exact input still missing | No fixture by twenty minutes means retain the smallest input and stop; never launch a full-golden retry, change tolerance, or update the golden |
| 5 | W2 `factual-review` / Correctness | `think-nr5w` | 1 slice, only after order 4 yields a fixture or repair | Independent diagnosis and a decision whether one more W7 repair is earned; no solver-health claim from one passing retry | A non-replayable or load-dependent diagnosis remains open and routes to order 12 |
| 6 | W7 `pipeline-improvement` / Efficiency | `think-b4jc`, reconciled with `think-krqi` | 1 slice | One exact pair-test counting contract and the smallest counter-to-JSONL vertical slice, or the first unmetered move path | If equal work cannot be defined identically across current paths, retain the interface decision and use order 13; do not substitute moves or wall time |
| 7 | W5 `efficiency-loop` / Efficiency | `think-b4jc` | 1 slice, only if order 6 lands a counter | Seeded-output equivalence, counter equality against independent totals, and measured overhead under an unloaded host | Any seeded drift, unexplained count, or competing load rejects the change; preserve the baseline and continue at order 8 |
| 8 | W3 `insight-iteration` / Insight | `think-kfb4` | 1 slice | One falsifiable successor covering only inclusion-minimal Trump rigidity supports, or an explicit open question if no exact criterion survives | Do not combine the radius, support, and side-stability questions; freeze no experiment until one criterion exists |
| 9 | W6 `research-loop` / Insight | `think-kfb4` | 1 slice, only after order 8 registers a criterion | Exact support-deletion data for every reached branch, complete or explicitly partial, replayed through `Trump exact branchwise linearized cones` | At twenty minutes without exhaustive deletion, retain partial supports and stop unresolved; no interval-radius or global-optimality detour |
| 10 | W2 `factual-review` / Correctness | `think-kfb4` | 1 slice, only after order 9 yields a result | Independent minimality and branch-scope disposition; an `exp-NNN` only if the frozen criterion is actually resolved | One unsupported branch or nonminimal certificate keeps the question unresolved and routes to order 11 |
| 11 | W7 `pipeline-improvement` / Efficiency | `think-tx0b` | 1 slice | One timeout/process-group primitive and focused failure test in `tests/test_validation_cli.py`, or a minimized incompatibility | Do not retrofit every deep step in one slice; stop with the first coherent primitive or blocker |
| 12 | W4 `process-review` / Process | `think-b3bm` | 1 slice | One short parent-owned rehearsal preserving argv, start/end, exit or signal, output paths, timeout, cleanup, and the portable runbook rule | If any receipt field disappears, retain that failure and leave the bead open; no long or deep command |
| 13 | W1 `research-survey` / Insight | `think-ykt7` | 1 slice | Source-bound reproduction of one `O(x^(3/5))` primitive or error balance, with the exact boundary where finite transfer fails | If the local primary source is insufficient, record the gap and stop; no unsupported asymptotic or finite-instance claim |
| 14 | Evidence-earned continuation / owning workflow and focus | One of orders 2, 4, 6, 8–9, 11, or 13 | 1 slice | One bounded successor justified by the predecessor’s retained evidence | No new evidence, no continuation; never become a third consecutive slice |
| 15 | W4 `process-review` / Process | `think-3cbq` | 45 minutes | All writers stopped; artifacts, ledger, defects, beads, commits, push, normal-gate receipt, terminal session report, and exact next action reconciled | The first gate failure gets one focused diagnosis only; otherwise preserve the last green checkpoint and stop at the eight-hour deadline |

Orders are priority, not permission to wait on a blocked predecessor.
At each checkpoint, claim any dependency-ready row while preserving the listed order;
skip a conditional audit when its producer returned no reviewable artifact.
The source-bound W1 row is the universal no-write fallback.
H-017 is not fallback work, and a numeric recipe that is merely executable is not
scientifically admissible.

The portfolio deliberately exercises all four dimensions without imposing equal-time
quotas: W2 may veto claims, W4 makes the night reconstructible, W3/W6 protect creative
mathematical depth, and W5/W7 improve measured throughput and capability.
Parallel delegates increase work completed inside the wall budget; they never extend the
deadline or weaken the finalization reserve.

## The scientific portfolio

The registry artifact is authoritative for each claim’s wording, metric, threshold,
regime, prerequisites, and status.
The table below is a routing view, not a second registry.
The
[mathematical-frontier review](../../reviews/review-2026-08-23-mathematical-frontier-strategy.md)
ranks the full portfolio and defines the basin ontology, visualization ladder, and
fast-first promotion rules.

### First: define and validate the counted object

| Order | Artifact | Question | Why now | Runnable? |
| ---: | --- | --- | --- | --- |
| 1 | [H-023](../../../../packing/campaign/hypotheses/H-023-n5-terminal-connectivity.md) | Are the equal-side `n=5` candidates in one terminal family, and what valid-path bounds connect unequal levels? | Focused ambiguity at the first nontrivial census cell | No; full poses and local geometry study absent |
| 2 | [H-021](../../../../packing/campaign/hypotheses/H-021-endpoint-identifiability.md) | Can the classifier resolve at least 95% of endpoint support through `n=8`? | Measurement-system gate; failure redirects the program | No; classifier and controls absent |
| 3 | [H-011](../../../../packing/campaign/hypotheses/H-011-small-n-census.md) | Does unseen terminal-component mass fall below 0.05 by `n=8`? | Builds the atlas and tests whether census is viable | No; waits on identity, events and estimator |
| 4 | [H-007](../../../../packing/campaign/hypotheses/H-007-saturation-curves.md) | Do preregistered coverage estimates predict held-out discovery? | Makes negative search results quantitative | No; waits on H-011 data |
| 5 | [H-012](../../../../packing/campaign/hypotheses/H-012-record-basins-are-rare.md) | Is the record-to-modal attraction ratio below 0.1 under named `P/Q/E`? | Kills or supports the cartography premise directly | No; waits on H-011 plus `n=11` sampling |

H-009’s raw-to-canonical ratio and H-008’s stronger-verifier rejection rate are
mandatory companion measurements.
H-003’s contact-count predictor comes later and must use held-out data; contact count is
not component identity or a rigidity certificate.

### Search strategies after the measurement spine

| Priority | Artifact | Registered comparison | Gate or kill line |
| ---: | --- | --- | --- |
| 1 | [H-004](../../../../packing/campaign/hypotheses/H-004-neighbor-transfer-seeding.md) | neighbor transfer versus cold starts at `n=11` | median best-side improvement at least 0.01; the old `n=12` side-4 target was vacuous |
| 1 | [H-013](../../../../packing/campaign/hypotheses/H-013-delta-continuation.md) | continuation versus direct starts, `n=10` before `n=11` | retire as a discovery method if it cannot win on the proved gate |
| 1 | [H-001](../../../../packing/campaign/hypotheses/H-001-angle-class-reduction.md) | angle-class proposer versus free-coordinate annealing | pass proved and oblique calibration before interpreting `n=11` |
| 2 | [H-015](../../../../packing/campaign/hypotheses/H-015-map-elites-illumination.md) | quality diversity versus matched restarts | at least 1.5× certified components per pair-test |
| 2 | [H-005](../../../../packing/campaign/hypotheses/H-005-m2-minus-3-construction.md) | analytic 3-4-5-tilt construction at `n=97` | analytic geometry first; no numerical rescue of a failed family |
| 3 | [H-014](../../../../packing/campaign/hypotheses/H-014-superdisk-continuation.md) | circle-to-square continuation versus direct square starts | last because it alone needs a new geometry model |
| 1 | [H-030](../../../../packing/campaign/hypotheses/H-030-public-parent-surgery.md) | held-out UnitSquare parent-to-child construction surgery | recover a hidden known child before any unseen-record budget |
| 2 | [H-031](../../../../packing/campaign/hypotheses/H-031-load-guided-block-moves.md) | LP-load-guided block moves versus coordinate-only moves | at least 2× valid target events per pair-test on paired controls |
| 2 | [H-029](../../../../packing/campaign/hypotheses/H-029-adaptive-splitting.md) | rare-event splitting versus independent restarts | pass exact synthetic coverage and an independent `n=10` reference before a new `n=11` cell |
| 2 | [H-040](../../../../packing/campaign/hypotheses/H-040-active-cell-neighbor-walk.md) | adjacent-cell pivots versus random-coordinate multistart | at least 2× new verified cells per LP solve; cells are not components |

H-024 separately tests the descriptive claim that verified record packings through
`n=30` use at most three orientation classes.
Exp-012 reconstructed and independently screened the primary `n=29` SVG and found six
unambiguous classes, refuting H-024 at its first stop cell.
That neither proves nor is proved by H-001’s algorithmic performance; H-025 now owns the
successor question about effective angular rank or compressibility.

H-017 remains a low-priority scaling fallback after the validity boundary is repaired.
H-016, H-018, H-019, and H-020 are resolved for their registered regimes and should not
be silently rerun as fresh hypotheses.

### Proof lane

| Priority | Artifact | Output | Boundary |
| ---: | --- | --- | --- |
| 1 | [H-010](../../../../packing/campaign/hypotheses/H-010-stromquist-triple.md) / [H-041](../../../../packing/campaign/hypotheses/H-041-repaired-stromquist-point-set.md) | **exp-016/017 complete:** exact rejection of the printed cover plus exact certification of a source-distinct one-coordinate repair | the published proof remains false as printed; only the repaired set proves the numerical inequality here |
| 1 | [H-026](../../../../packing/campaign/hypotheses/H-026-trump-first-order-rigidity.md) / [H-022](../../../../packing/campaign/hypotheses/H-022-trump-local-geometry.md) | **exp-013 complete:** 128/128 exact zero-cone certificates and finite-branch local isolation; next quantify a radius | feature counts and a smooth Jacobian decided neither rigidity nor isolation |
| 2 | [H-006](../../../../packing/campaign/hypotheses/H-006-lp-dual-unavoidable-sets.md) | quantitative, refinement-stable dual support for candidate loci | discretized LP generates proof objects; it proves no bound |
| 1 | [H-039](../../../../packing/campaign/hypotheses/H-039-s12-proof-frontier.md) | checked improvement to the `s(12)` lower bound | exp-016/017 are the calibrated failure and success gates for the forcing architecture |
| 1 | [H-033](../../../../packing/campaign/hypotheses/H-033-m2-minus-3-at-n61.md) | extend Bentz’s `m²−3` method to `m=8` or retain its first blocking pose | the direct 2018 piercing bound is weaker than Nagamochi and does not settle `s(61)` |
| 2 | [H-034](../../../../packing/campaign/hypotheses/H-034-fractional-piercing-ceiling.md) | certified decision whether `τ*(U_s)>10` at Trump’s side | `>10` rules out ten points; `≤10` does not construct an integral set |
| 2 | [H-036](../../../../packing/campaign/hypotheses/H-036-robust-restricted-orientation.md) | extend Stromquist’s exact `0°/45°` exclusion to a fixed neighborhood | reproduce the exact theorem before interval enlargement |
| 2 | [H-032](../../../../packing/campaign/hypotheses/H-032-small-n-optimal-moduli.md) / [H-038](../../../../packing/campaign/hypotheses/H-038-record-number-fields.md) | exp-014/015 solve the exact `n=3,4` quotient cells; next classify `n=5`, alongside exact-field taxonomy | keep the sub-second controls permanent; sampling cannot decide the `n=5` component relation |
| 3 | [H-037](../../../../packing/campaign/hypotheses/H-037-asymptotic-waste-exponent.md) | narrow the `1/2` versus `3/5` exponent gap | separate paper-mathematics lane; finite diagnostics do not decide it |

H-026 completed in exp-013, exp-014/015 completed H-032’s `n=3,4` controls, and
exp-016/017 completed the printed-failure/repaired-success Stromquist calibration.
The next proof rotation is H-039’s first fixed-threshold `n=12` candidate alongside the
first complete `n=5` component analysis.
The slower `s(12)`, `s(61)`, fractional-piercing, restricted-orientation, exact-field
and asymptotic programs remain visible with explicit intermediate artifacts rather than
being forced into the stochastic census queue.

### Basin maps, in order of mathematical honesty

The first view has landed: exp-014’s generated packing glyphs and exact `n=3` quotient
family. Next come fixed-cell angle sheets with active-basis overlays, an `n=5` ambiguity
graph with tangent evidence, and valid-path clearance profiles.
Kernel-conditioned transition networks and discovery curves wait for full event
retention and `P/Q/E`; a global merge tree waits for certified components of a
fixed-side filtration.
Endpoint hashes or continuation-branch dendrograms are never labelled feasible topology.

## The autonomous agent loop

This loop may open after the launch-base reconciliation and the focused plus normal
launch checks pass.
PR 26 is a bounded integration opportunity at a phase boundary, not a
launch prerequisite; do not wait beyond its declared slice.

1. Execute the active session’s frozen portfolio.
   Only the coordinator may reconcile `tbd ready` at a checkpoint, and only after the
   landed-versus-branch-ahead bookkeeping in `think-k68v` is current.
   Choose the workflow whose output matches the item, then one primary focus.
2. Record the bounded objective, intended artifact, and focused check where the work is
   already tracked. Open or renew a versioned session phase only when the work crosses
   the escalation threshold; then add its focus, clock, stopping condition, fallback,
   outcome, and evidence.
3. Delegate bounded mechanical work—formatting, lint repair, data extraction, repeated
   checks—while the primary agent owns mathematical and integration judgment.
   These slices inherit the coordinating phase unless they open independently tracked
   sessions. Each delegation declares a wall budget, exact frozen validation command,
   kill condition, fallback, write scope, deadline, and excluded long commands.
4. Work in the smallest loop that bears on the change: source inspection, focused check,
   then the normal gate only at a real checkpoint.
5. Record any actual error in `defects.yaml` by its substantive class and link an open
   bead when work remains.
6. Update the hypothesis, experiment, or session artifact that owns the result; do not
   leave a conclusion in chat or a bead description alone.
7. Commit and push a bounded checkpoint, then re-screen the frozen portfolio.
   Close the phase before switching workflow or focus when the evidence demands a
   handoff.

Send promoted, novel, disputed, or otherwise high-risk claims through W2 before they
move forward. A routine W6 result whose preregistered guards and independent replay
already decide its stated criterion need not open a ceremonial review phase.

The research cell at `n = 28` and `n = 40` stays open, and know what it costs before
taking it: that slice is not an assessment but an **exact construction**. `X-007`
settled `n = 5` because Göbel’s construction is exact; the other two retain decimal
witnesses of the kind measured `2.4e-30` off the diagonal, which no certificate can rest
on.
It is not the next thing, because a reassessment of what to search is queued in front
of it.

For the next supervised exact-research goal, take `BC-213` in
[Agenda 022](../../../../packing/campaign/agendas/agenda-022-the-conditional-route.md),
bead `think-wufn`: the remaining rung of the `m = 5` bisection at `973/200`, which
settles `H-062` either way and which
[Agenda 021](../../../../packing/campaign/agendas/agenda-021-three-numbers-and-a-wall.md)’s
closeout selected on 2026-09-05 after four rungs bracketed the covering wall to `0.025`
against the `0.02` that hypothesis registered.

## The numeric runner launch gate

No unwatched numeric cell starts until every applicable line is true.

### Scientific admissibility

- [ ] The hypothesis and exact cell are registered before execution.
- [ ] The evaluator is typed for the hypothesis’s criterion; positive and negative
  fixtures have been watched passing and failing.
- [ ] The command archives full poses or stable paths to immutable retained pose
  artifacts.
- [ ] A separate verifier recomputes containment and non-overlap from the archived pose.
- [ ] The actual engine selftest, source revision, dirty state, host, seeds, and budget
  are recorded.
- [x] D-132 distinguishes a settled fixed cell from a rejected transition or iteration
  cap and prevents outer convergence when the inner solve did not settle.
- [ ] Prerequisites are satisfied; an instrument-ready flag changes only with the
  implementation that makes it true.

### Lifecycle and persistence

- [ ] One cell maps to one experiment and one per-cell deadline.
- [ ] The session deadline bounds the round deadline; no fresh full timebox starts after
  most of the session is spent.
- [ ] Claim, execute, record, release, and terminal states enforce legal transitions.
- [ ] Guard failures, command crashes, timeouts, and persistence failures all count
  toward the three-consecutive-failure stop and leave a durable non-scientific outcome.
- [ ] Narrow checked commits persist claims before long compute, checkpoints at each
  seed or thirty minutes, terminal artifacts, releases, and the final report.
- [x] D-035 cannot leave a deliberate negative-control mutation: controls write only
  bounded private source snapshots.
- [x] D-129 bounds each checker, terminates and reaps its process group on timeout or
  interruption, and retains the failure.
  No hostile isolation is required.
- [ ] D-239 gives every outer validation step an appropriate deadline and reaps its
  process group, so strict preflight cannot become an unbounded wait.

### Rehearsal and capacity

- [ ] A cheap known-answer claim → execute → record → commit → report round passes under
  supervision on the shipped code.
- [ ] Invalid-pose, false-overlap, timeout, mid-round kill/release, three guard
  failures, three crashes, short-session budget, and failed-commit rehearsals reach the
  expected refusals.
- [ ] `packing-validate --strict` passes the deep checks with zero skips from a clean
  checkout.
- [ ] Three representative cold/warm target-host calibrations retain p50/p95 runtime and
  the exact binary/toolchain fingerprint.
- [ ] The generated unresolved-cell queue costs at least 10h for an 8h session or 30h
  for a 24h session at p95.

The queue must be materialized by unresolved **cell**, not merely by hypothesis.
A multi-cell universal claim is accepted only after every cell passes and refuted when a
registered counterexample cell fails.
This corrects the current mismatch in which the schema permits several cells while
execution shares one deadline and the artifact names only the first.

## Stop rules

The agent or runner stops and records why when any of these occurs:

- queue empty or session budget exhausted;
- three consecutive guard, execution, or persistence failures;
- a known-answer control or independent verifier disagrees;
- the frontier or acceptance rule moved after preregistration;
- a result requires human mathematical judgment;
- the evidence invalidates the current strategy or counted object.

Thresholds, controls, tolerances, and evaluators do not adapt during an unattended
session. A result that passes mechanical clauses but needs judgment is held unresolved
for review.

## Morning artifacts

The handoff must be unique, durable, and committed.
It leads with:

1. **Needs review** — candidates, ambiguity, or mathematical judgments;
2. **What moved** — metric deltas against the standing baseline;
3. **What died** — rejected hypotheses, guard failures, crashes, or exhausted regimes;
4. **What ran** — exact cells, seeds, budgets, revisions, artifacts, and verdicts;
5. **Queue now** — recomputed after the final transition, priced on the same host;
6. **Health** — recovery, persistence, and gate status;
7. **Next action** — one dependency-ready bead and the evidence it needs.

The numeric runner’s generated `campaign/session-report.md` currently overwrites its
predecessor and is not durable.
It is a batch report, not a versioned `session-NNN` agent-session record; D-071 and
`think-y37w` own that correction.

## Efficiency agenda

The optimization order follows measured leverage:

1. **Make one valuable scientific cell runnable.** An empty admissible queue has
   infinite effective overhead.
2. **Profile the complete agent and numeric loops** under `think-xzew`, including time
   in build, execute, analysis, record, recovery, and gates.
3. **Measure canonicalization scaling.** The observed `n=7` to `n=9` jump may dominate
   `n=10`; optimize only after representative profiles.
4. **Bind pair-test accounting** (`think-krqi`/`think-b4jc`) so proposer comparisons use
   the declared machine-independent currency.
5. **Reduce agent time per recorded round** toward ten minutes through recipes,
   generated views, and delegated mechanical checks.
6. **Then** evaluate sharding, cache reuse, or compiled verification against declared
   speedup and identical-output criteria.

Do not build fleet coordination, per-run worktrees, repository copies, generalized
leases, or caches for a one-item queue.
One runner plus a cooperative activity refusal is the intended architecture until
measured concurrency demand says otherwise.

## Bead map

The canonical readiness epic is `think-ydus`.

| Lane | Beads | Exit evidence |
| --- | --- | --- |
| Portfolio and agenda | `think-1sxv`, `think-isa3` | registry, idea board, exploration source and this spec reconcile |
| Mathematical frontier | `think-7gu0` with `think-jbcm`, `think-1xex`, `think-vvd5`, `think-xbab`, `think-z4m0`; execution continues on `think-chbu`, `think-ykt7` and the existing Insight beads | ranked review, 40-artifact registry, basin ontology, priced rotation and source-correct proof/search lanes |
| Counted object | `think-1s0h` → `think-0yo9`; `think-3szr`, `think-aans` | H-023/H-021 classification evidence and ambiguity bounds |
| Events and evaluator | `think-31k1`, `think-rrht`, `think-apwt`, `think-jxx8` | full observations, named `P/Q/E`, held-out coverage evaluator |
| Validity and lifecycle | `think-ldq2`, `think-cns0`, `think-5zwm`, `think-ouf0`, `think-osyp` | independent pose checks, real selftest, transitions, interruption and control rehearsals |
| Budget and reporting | `think-krqi`, `think-b4jc`, `think-kmn2`, `think-y37w`, `think-xzew` | pair-test budget, priced queue, durable report, measured loop |
| First supervised cell | `think-l4z5` | H-011 instrument and recipe become true together; one complete cell retained |
| Launch and morning | `think-4jnv`, `think-20z4` | all launch checks green, then reviewed morning artifact |

`think-tosv`, `think-z9jq`, and `think-srym` are closed as superseded scheduling
surfaces. Their open implementation children were reparented; no work was discarded.
The new H-024 corpus reconstruction is `think-w5rb` under the Insight focus.

## Revision history

- **2026-08-23:** first plan proposed a watched build half followed by an unattended
  H-011 census.
- **2026-08-24:** rebuilt after PR 15 merged.
  Corrected the historical total from ten rounds/16.4 wall-minutes to eleven rounds/23.0
  wall-minutes; recognized that one nominal eight-hour recipe is about 2.8 hours
  locally; separated the autonomous agent loop from the numeric runner; codified H-003
  through H-015 plus H-021 through H-024; and replaced a premature schedule with the
  explicit scientific, lifecycle, capacity, and morning-artifact gate above.
- **2026-08-24:** deep creativity review expanded the registry from 24 to 40 artifacts,
  corrected the rigidity, LP-dual, topology, tail-model and fractional-piercing claims,
  added the exact-small-`n`, public-parent, `s(12)`, `s(61)`, algebraic-field and
  asymptotic lanes, and adopted the fast-first visualization and successive-halving
  agenda.
- **2026-08-24:** added the soft-schema basin confidence ladder as the mutable
  size-by-size queue. It separates tool validation, measurement validation, and research
  so proved controls can build confidence without being reported as landscape results.

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
