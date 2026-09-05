---
title: session-086 — the Agenda 021 overnight pass and the agenda 022 continuation
softschema:
  contract: packing.squares:AgentSession/v2
  schema: ../schemas/agent-session.schema.yaml
  envelope: session
  status: enforced
session:
  id: session-086
  title: The Agenda 021 overnight pass and the agenda 022 continuation
  date: '2026-09-05'
  started_at: '2026-09-05T06:43:00Z'
  deadline_at: '2026-09-05T16:43:00Z'
  branch: claude/agenda-021-overnight-pass
  goal: >-
    Run agenda 021 as the operator directed on 2026-09-05 -- three lanes on three cores,
    the fourth reserved for the retention gate, the closeout at minute 390 with its four
    doubling-down rules -- and then continue into agenda 022's BC-206 and BC-208, the two
    cells no rule gates, for the remainder of a ten-hour pass. The pass starts from the
    handoff's selected entry (BC-191, Lane C's first half) and the agenda's two ready
    cells (BC-211, BC-199); it is coordinated from one session with sub-agents per lane,
    every retained number re-derived from its artifact before it enters a record, and
    every retained certificate decided through the gate by both routes.
  workflow_phases:
  - workflow: process-review
    focus: process
    recording: contemporaneous
    clock_role: work
    objective: >-
      Dispatch: arm the hourly continuity trigger (OR-8), branch from main after PR 81
      merged, flip agenda 021 to active, open this record, launch the three lanes on
      their entry cells, and open the draft PR.
    bead: think-db1k
    status: completed
    entered_by: session_start
    switch_reason: null
    budget_minutes: 10
    started_at: '2026-09-05T06:43:00Z'
    deadline_at: '2026-09-05T06:46:00Z'
    expected_output: >-
      The trigger armed and recorded, the branch pushed, agenda 021 active, this record
      with the three lanes as delegations, and a draft PR whose body will carry the
      pass's cost first.
    validation_command: >-
      uv run --frozen --all-extras --group dev packing-validate --records
    kill_condition: >-
      A lane cannot start on its entry condition, or the branch cannot be pushed.
    fallback: >-
      Start the lanes that can start and record the one that cannot as never-opened
      with the entry condition that refused it.
    outcome: >-
      The continuity trigger was armed at 06:43 UTC, firing hourly at 43 minutes past
      the hour into this session; PR 81 was merged as 379fd4e5 and the branch cut from
      it; the three lanes were launched between 06:46 and 06:48 UTC on BC-211 (Lane A),
      BC-199 (Lane B) and agenda 019's BC-191 (Lane C), one core each; agenda 021 is
      active.
    evidence:
    - 'trigger trig_01Vb5QMjJ8VAEn7fxqpFci7u, hourly, bound to this session'
    - 'packing/campaign/agendas/agenda-021-three-numbers-and-a-wall.md: status active'
    stop_reason: >-
      Dispatch complete; every lane accepted its entry condition.
    next_action: >-
      Run the three lanes to their exits with 30-minute checkpoints; integration
      checkpoint at 09:43 UTC; BC-203 at 13:13 UTC.
  - workflow: research-loop
    focus: correctness
    recording: contemporaneous
    clock_role: work
    objective: >-
      The block's research lanes to their exits: Lane A BC-211, BC-197, BC-198; Lane B
      BC-199, BC-200, BC-201; Lane C BC-191 (agenda 019, efficiency-loop, as registered)
      then BC-202. The coordinator holds the retention gate, the shared records, the
      commits and the PR; sub-agents hold one lane each in bounded slices.
    bead: think-db1k
    status: stopped
    entered_by: planned_checkpoint
    switch_reason: >-
      Dispatch complete; the block's research lanes run.
    budget_minutes: 387
    started_at: '2026-09-05T06:46:00Z'
    deadline_at: '2026-09-05T13:13:00Z'
    expected_output: >-
      Per cell, the exit its text names: retained or refuted rungs with their restricted
      optima and least covered masses, the exact isolation radius and stress constant,
      the depth-scaled totals at 3.82 and 3.85, the tight-cell census tool and its table,
      BC-191's three benchmark records and site-density rule, and the n = 26 run or its
      price; every retained certificate frozen and decided by both routes.
    validation_command: >-
      uv run --frozen --all-extras --group dev packing-validate --records
    kill_condition: >-
      OR-8: only the operator, an external blocker that makes progress impossible, or
      the genuine exhaustion of the cells ends this phase; a cell's own kill condition
      ends that cell, not the phase.
    fallback: >-
      A time-limited cell keeps its checkpoint, its last value and its reason, and
      BC-203 classifies it; the lane moves to its next cell.
    outcome: >-
      Seven of the eight cells were opened and six are terminal with an outcome. Two
      bounds moved and one instrument line was priced: T-021 raises s(20) and s(21) to
      97/20 from a certificate the gate retained on both routes, the m = 5 covering wall
      is bracketed to [97/20, 39/8], the exact floor under the n = 11 covering value rose
      from 6.5829 to 9.907906, Trump's isolation radius and stress constant came out as
      exact rationals with four corrections to the sketch that proposed them, and
      BC-191's three baselines are measured with a site-density rule and a raised default
      scale to show for it. Three cells stopped: BC-211 time-limited on its own
      25-minute-round kill, and BC-201 and BC-202 by the external blocker below.
    evidence:
    - packing/frontier/results.yaml T-021
    - packing/campaign/series/series-000-smoke-and-calibration/experiments/exp-060-h-064-n11-fractional-packing-floor.md
    - packing/campaign/series/series-000-smoke-and-calibration/experiments/exp-061-h-062-m5-covering-wall.md
    - packing/campaign/agendas/agenda-021-three-numbers-and-a-wall.md closeout
    stop_reason: >-
      An account rate limit ended every sub-agent of the pass at 09:21 UTC and the
      container was restarted afterwards, which is the external blocker OR-8 names rather
      than a budget decision. The coordinator resumed, gated the two candidates the lanes
      had frozen, registered the result and closed the block.
    next_action: >-
      BC-213, the remaining m = 5 rung at 973/200, which settles H-062 either way.
  primary_bead: think-db1k
  status: stopped
  budget:
    wall_minutes: 600
    checkpoint_minutes: 30
    slice_minutes: 30
    finalization_minutes: 60
  stop_conditions:
  - The operator says stop.
  - An external blocker makes progress on every lane impossible.
  - Every cell of agenda 021 and the two continuation cells of agenda 022 are terminal.
  progress:
    metric: >-
      Cells of agenda 021 terminal with an outcome at their smallest honest scope, results
      retained through the gate, and the four doubling-down rules evaluated against
      measured numbers.
    before: >-
      0 of 8 cells terminal; agenda 021 paused; no rung above 24/5 at m = 5 and none at
      n = 13; no isolation radius computed; the 3.82 plateau undecided; BC-191's three
      baselines unmeasured.
    after: >-
      Six of eight cells terminal with outcomes and two stopped by an external blocker;
      T-021 registered at 97/20 for n = 20 and n = 21; the m = 5 covering wall bracketed
      to [97/20, 39/8]; nu*(3.82) >= 9.907906 and nu*(3.85) >= 9.049861 exactly; rho_0
      >= 0.0023089 and C <= 22.467763 at Trump's pose; BC-191's three baselines measured.
  delegations:
  - task: >-
      Lane A, BC-211: the generator unchanged at n = 13, side 399/100, to convergence;
      freeze a candidate below thirteen, or confirm at or above thirteen on two site sets.
    operator: sub-agent at the thinking level BC-211 declares, one core
    status: completed
    recording: contemporaneous
    outcome: >-
      Time-limited, neither reading earned: run A hit the 60-round limit at 16.000000
      (least covered 0.929161); runs B and D each spent the budget inside one un-logged
      round; the n = 12 control at 99/25 converged to 12.312896 above the retained
      11.998960, so the seed cannot refute a rung. Cost 7.72 s per row round at 399/100
      against 3.04 s at 99/25.
    evidence:
    - packing/campaign/series/series-000-smoke-and-calibration/results/bc-211-run-a-n13-399-100.json
    - packing/campaign/series/series-000-smoke-and-calibration/results/bc-211-run-c-control-n12-99-25.json
    files:
    - packing/devtools/run_fractional_colgen.py
    - packing/tests/test_run_fractional_colgen.py
    checks:
    - 'pytest tests/test_run_fractional_colgen.py: 4 passed; ruff, format and basedpyright clean'
    uncertainty: >-
      The extrapolated covering value at the ceiling (12.06 to 12.24) is a two-point
      trend; one round may cost more than the 25-minute kill.
    elapsed_seconds: 3982
    elapsed_quality: platform_measured
    next_action: >-
      BC-197 dispatched on the same lane at 07:56 UTC with row-round logging required.
    phase: 2
    budget_minutes: 70
    started_at: '2026-09-05T06:46:00Z'
    deadline_at: '2026-09-05T07:56:00Z'
    expected_output: >-
      A per-round table, the loop's final least covered mass, cost per round against the
      n = 12 99/25 rung, and either a frozen candidate under
      packing/cases/n13_fractional_certificate/ or a two-site-set refutation.
    validation_command: >-
      uv run --frozen --all-extras --group dev python -m devtools.decide_certificate packing/cases/n13_fractional_certificate/certificate.json
    kill_condition: A single round costing more than 25 minutes.
    fallback: Stop time-limited with the checkpoint; BC-203 records the price.
    write_scope:
    - packing/cases/n13_fractional_certificate/
    - packing/devtools/
    - packing/tests/
    excluded_commands:
    - devtools.decide_certificate
    - git commit
    - git push
  - task: >-
      Lane A, BC-197: the m = 5 ladder -- one rung at 997/200 on the n = 21 reading
      first, then the pre-registered bisection for the n = 20 wall (H-062).
    operator: sub-agent at the thinking level BC-197 declares, one core
    status: completed
    recording: contemporaneous
    outcome: >-
      Five sides decided on two constructions each: certificates at 97/20 (retained as
      T-021) and 193/40, walls at 39/8, 979/200 and 997/200, and the exactly round value
      at 997/200 explained by the overlap-strip geometry rather than left as an artefact.
    evidence:
    - packing/frontier/results.yaml T-021
    - packing/campaign/series/series-000-smoke-and-calibration/experiments/exp-061-h-062-m5-covering-wall.md
    files:
    - packing/cases/n20_fractional_certificate/certificate.json
    - packing/cases/n20_fractional_certificate/certificate-193-40.json
    - packing/devtools/declare_least_cell_mass.py
    checks:
    - 'devtools.decide_certificate: RETAINABLE at 200001/200000 and at 1000003/1000000'
    - 'coordinator: both rungs replayed through the package entry point'
    uncertainty: >-
      The wall is bracketed to 0.025 rather than the 0.02 H-062 registered, and the
      crossings that set its upper end are unconverged by the cell's own refutation rule.
    elapsed_seconds: 5280
    elapsed_quality: operator_reported_approximate
    next_action: >-
      Report per rung; the coordinator decides any frozen candidate through the gate;
      then BC-198.
    phase: 2
    budget_minutes: 200
    started_at: '2026-09-05T07:56:00Z'
    deadline_at: '2026-09-05T11:16:00Z'
    expected_output: >-
      Per rung a retained candidate frozen, a refutation with the round it crossed, or
      a time-limited checkpoint with its row-round table; the bracket the decided rungs
      support; the cost per round against the model.
    validation_command: >-
      uv run --frozen --all-extras --group dev python -m devtools.decide_certificate packing/cases/n21_fractional_certificate/certificate.json
    kill_condition: A round costing more than 25 minutes at any rung.
    fallback: Time-limited with the checkpoint; the bracket reported at the width the decided rungs support.
    write_scope:
    - packing/cases/n21_fractional_certificate/
    - packing/cases/n20_fractional_certificate/
    - packing/devtools/
    - packing/tests/
    excluded_commands:
    - devtools.decide_certificate
    - git commit
    - git push
  - task: >-
      Lane B, BC-199: kappa_b on all 128 branches, the curvature bound K, the least
      nonzero gap and its Lipschitz constant, rho_0 and C as exact rationals, and the
      claim boundary.
    operator: sub-agent at the thinking level BC-199 declares, one core
    status: completed
    recording: contemporaneous
    outcome: >-
      Complete at 51 of 120 minutes; the kill did not fire. rho_0 >= 0.0023089 (uniform
      K) and >= 0.0040426 (per-row K), C <= 22.467763 and <= 12.873063, kappa_b in
      {0.011480272, 0.016423845} by contact (9, 10); the stress ratio is an exact
      constant across the 128 branches; four corrections to X-014's sketch recorded.
    evidence:
    - packing/campaign/series/series-000-smoke-and-calibration/results/bc-199-trump-isolation-radius.json
    - packing/tests/test_trump_isolation_radius.py
    files:
    - packing/cases/trump11/isolation_radius.py
    - packing/tests/test_trump_isolation_radius.py
    - packing/campaign/series/series-000-smoke-and-calibration/results/bc-199-trump-isolation-radius.json
    checks:
    - 'uv run --frozen --all-extras --group dev pytest tests/test_trump_isolation_radius.py -q: 6 passed'
    - 'ruff check, ruff format --check, basedpyright: clean on both files'
    - 'coordinator: rho_0 = 2 kappa_min / K re-derived from the reported kappa and K'
    uncertainty: >-
      The uniform K is 85 per cent trigonometric and a box-aware Hessian bound could
      tighten it by up to 8 per cent on some rows; the numbers are lower bounds either way.
    elapsed_seconds: 3107
    elapsed_quality: platform_measured
    next_action: >-
      BC-200 dispatched on the same lane at 07:41 UTC.
    phase: 2
    budget_minutes: 120
    started_at: '2026-09-05T06:47:00Z'
    deadline_at: '2026-09-05T08:47:00Z'
    expected_output: >-
      A tool under packing/cases/trump11/ or packing/devtools/ with a test, the per-branch
      kappa_b table, K with its box, rho_0 with the cap that bound it, C, and the claim
      boundary.
    validation_command: >-
      uv run --frozen --all-extras --group dev pytest packing/tests -q -k isolation
    kill_condition: rho_0 below 1e-6 in the chart, reported as the cell's number.
    fallback: Report the partial computation with the step that refused.
    write_scope:
    - packing/cases/trump11/
    - packing/devtools/
    - packing/tests/
    excluded_commands:
    - git commit
    - git push
  - task: >-
      Lane B, BC-200: the n = 11 covering value from below at 191/50 and 77/20 by an
      exact-depth fractional packing, cutting planes on arrangement vertices with the
      exact depth check (H-064).
    operator: sub-agent at the thinking level BC-200 declares, one core
    status: completed
    recording: contemporaneous
    outcome: >-
      Complete at 96 of 110 minutes. nu*(3.82) >= 9.907906 and nu*(3.85) >= 9.049861
      exactly; the row loop's converged restricted optimum at 3.82 is 11.055617 on
      12,761 sites; no family reached eleven; H-064 unresolved (exp-060, abandoned,
      resumable from the retained 3.82 state).
    evidence:
    - packing/campaign/series/series-000-smoke-and-calibration/experiments/exp-060-h-064-n11-fractional-packing-floor.md
    - packing/campaign/series/series-000-smoke-and-calibration/results/bc-200-summary-191-50.json
    files:
    - packing/src/sqpack/fractional/cutting.py
    - packing/devtools/run_fractional_cutting.py
    - packing/tests/test_fractional_cutting.py
    checks:
    - 'pytest tests/test_fractional_cutting.py: 8 passed; ruff, format and basedpyright clean'
    uncertainty: >-
      The exact vertex check reached 1650944 vertices on a 608-placement family at 3.82;
      the loop may pass what the check can carry inside the budget.
    elapsed_seconds: 5758
    elapsed_quality: platform_measured
    next_action: >-
      BC-201 dispatched on the same lane at 09:20 UTC.
    phase: 2
    budget_minutes: 110
    started_at: '2026-09-05T07:41:00Z'
    deadline_at: '2026-09-05T09:31:00Z'
    expected_output: >-
      The cutting-plane loop as a tool with a test; per side, the exact depth-scaled
      total, arrangement vertex count and exact maximum depth, and a frozen family under
      packing/cases/n11_fractional_certificate/ where verify_ceiling accepts it.
    validation_command: >-
      uv run --frozen --all-extras --group dev pytest packing/tests -q -k ceiling
    kill_condition: The vertex count passing what the exact check can carry inside the budget.
    fallback: Record the count and the last exact depth; BC-201 follows.
    write_scope:
    - packing/cases/n11_fractional_certificate/
    - packing/src/sqpack/fractional/
    - packing/devtools/
    - packing/tests/
    excluded_commands:
    - git commit
    - git push
  - task: >-
      Lane B, BC-201: the census of near-tight event cells on the retained 381/100
      certificate at four margins, as a devtool with a test (H-065).
    operator: sub-agent at the thinking level BC-201 declares, one core
    status: blocked
    recording: contemporaneous
    outcome: >-
      Stopped with the tool half-built: the lane was refactoring the sweep to expose the
      per-cell masses the census counts when the rate limit ended it. No census ran and
      H-065 is untouched.
    evidence:
    - session-086 stop reason
    files:
    - packing/devtools/census_tight_cells.py
    checks:
    - 'coordinator: ruff and ruff format clean on the half-built tool; no test exists and no census ran, so nothing is retained from it'
    uncertainty: >-
      H-065's accept line (0.20) is declared, not derived; the first census may land in
      the inconclusive band.
    elapsed_seconds: 900
    elapsed_quality: operator_reported_approximate
    next_action: >-
      Report the four summed fractions and H-065's reading; then Lane B is done for the
      block.
    phase: 2
    budget_minutes: 60
    started_at: '2026-09-05T09:20:00Z'
    deadline_at: '2026-09-05T10:20:00Z'
    expected_output: >-
      devtools/census_tight_cells.py with a test, the per-direction census at the four
      margins, and the fraction of reachable cells the epsilon = 1/20 set covers over
      the 181 directions.
    validation_command: >-
      uv run --frozen --all-extras --group dev pytest packing/tests/test_census_tight_cells.py -q
    kill_condition: None beyond the budget; the readout is a count.
    fallback: Report the partial census with the directions covered.
    write_scope:
    - packing/devtools/
    - packing/tests/
    excluded_commands:
    - git commit
    - git push
  - task: >-
      Lane C, agenda 019's BC-191 as registered: warm-start versus re-solve, the cost of
      max_rounds and rows_per_direction at three sides, the site-density crossover as a
      rule in the container side, the default rationalisation scale with its measured
      verification cost, and the core budget.
    operator: sub-agent at the thinking level BC-191 declares, one core
    status: completed
    recording: contemporaneous
    outcome: >-
      Complete at 55 of 120 minutes. No warm start exists in solve_lp; cost per LP round
      fits 0.0189 L^3.657; the site-density rule count = round((L - 2 inset) d / B) + 1
      with d = (8.5, 11.5, 14.25) is exposed as site_counts_for_side; DEFAULT_SCALE is
      raised to 4,000,000 at flat verification cost; verify(workers=None) never consults
      PACK_JOBS, which explains agenda 017's load 10.6.
    evidence:
    - packing/devtools/bench_colgen.py
    - packing/tests/test_bench_colgen.py
    files:
    - packing/devtools/bench_colgen.py
    - packing/tests/test_bench_colgen.py
    - packing/src/sqpack/fractional/colgen.py
    checks:
    - 'pytest tests/test_bench_colgen.py: 7 passed; test_fractional_generate.py still passes'
    - 'ruff check, ruff format --check, basedpyright: clean on the three files'
    uncertainty: >-
      The cost model is fitted on four sides inside ten-minute runs; the density rule's
      optimum was located at two sides and is applied at a third.
    elapsed_seconds: 3258
    elapsed_quality: platform_measured
    next_action: >-
      BC-202 dispatched on the same lane at 07:47 UTC: the model prices a column round
      at 580 to 870 s, inside the cell's wall, so the run opens.
    phase: 2
    budget_minutes: 120
    started_at: '2026-09-05T06:48:00Z'
    deadline_at: '2026-09-05T08:48:00Z'
    expected_output: >-
      A benchmark tool under packing/devtools/ with a test, the site-density rule as a
      function of side with a test, the default-scale decision, and the core budget
      statement.
    validation_command: >-
      uv run --frozen --all-extras --group dev pytest packing/tests -q -k bench_colgen
    kill_condition: A single measurement run passing ten minutes of wall time.
    fallback: Report partial numbers with the run that was cut.
    write_scope:
    - packing/devtools/
    - packing/src/sqpack/fractional/
    - packing/tests/
    excluded_commands:
    - git commit
    - git push
  - task: >-
      Lane C, BC-202: the n = 26 column-generation run at 138/25 with BC-191's density
      rule (40, 53, 66) and scale 4,000,000, carried to convergence rather than a clock.
    operator: sub-agent at the thinking level BC-202 declares, one core
    status: completed
    recording: contemporaneous
    outcome: >-
      Time-limited with a measured negative: 22 column rounds and 137 LP rounds over
      7983 s brought the restricted optimum at 138/25 to 26.464317 with the row loop
      converged inside the last column round, above twenty-six on that site set, so no
      certificate there and no ratio to report. The checkpoint resumes and the resume
      path was exercised on the real artifact.
    evidence:
    - packing/campaign/series/series-000-smoke-and-calibration/results/bc-202-n26-138-25.json
    files:
    - packing/devtools/colgen_checkpoint.py
    checks:
    - 'pytest tests/test_colgen_checkpoint.py: 8 passed, including the chunking equivalence guard'
    uncertainty: >-
      A cold column round cost 2130.6 s against the model's 580 to 870, because the cold
      row loop needs many more rounds and their cost grows inside the loop; warm rounds
      averaged 244.7 s.
    elapsed_seconds: 7983
    elapsed_quality: platform_measured
    next_action: >-
      Report the per-round table and whether the loop converged; the coordinator
      decides any frozen candidate through the gate.
    phase: 2
    budget_minutes: 170
    started_at: '2026-09-05T07:47:00Z'
    deadline_at: '2026-09-05T10:37:00Z'
    expected_output: >-
      A converged restricted optimum at 138/25 with its least covered mass and cost per
      round, and a frozen candidate under packing/cases/n26_fractional_certificate/ if
      the optimum is below 26; or a time-limited checkpoint with the value reached.
    validation_command: >-
      uv run --frozen --all-extras --group dev python -m devtools.decide_certificate packing/cases/n26_fractional_certificate/certificate.json
    kill_condition: The cell's own wall; a run that cannot converge is time-limited, not killed.
    fallback: Keep the checkpoint for BC-209; report the value reached, no ratio.
    write_scope:
    - packing/cases/n26_fractional_certificate/
    - packing/devtools/
    - packing/tests/
    excluded_commands:
    - devtools.decide_certificate
    - git commit
    - git push
  outputs:
  - packing/devtools/bench_colgen.py
  - packing/cases/trump11/isolation_radius.py
  - packing/campaign/series/series-000-smoke-and-calibration/results/bc-199-trump-isolation-radius.json
  checks:
  - 'pytest tests/test_trump_isolation_radius.py: 6 passed'
  - 'pytest tests/test_bench_colgen.py tests/test_fractional_generate.py: 19 passed'
  resource_rollups:
  - packing/campaign/resource-usage/f37f604c-3212-50e9-b7f7-4b00b94bfcc0.yaml
  stop_reason: >-
    An account rate limit ended every sub-agent of the pass at 09:21 UTC, at minute 158
    of a 600-minute plan, and the container was restarted afterwards. That is an external
    blocker in OR-8's sense and not a budget decision; the coordinator resumed on the
    same branch and clock, gated the two candidates the lanes had frozen, registered
    T-021 and ran the closeout. The continuation into agenda-022's BC-206 and BC-208 did
    not open, and BC-203's replanning selects the cheaper rung that settles H-062
    instead.
  next_action: >-
    BC-213, the remaining m = 5 rung at 973/200 (think-wufn), as agenda-021's closeout
    selects it.
---
# session-086 — The Agenda 021 Overnight Pass

The operator chose Agenda 021 on 2026-09-05 after PR 81 merged, and directed that it run
autonomously overnight from this session, on a new branch with its own pull request,
with everything committed as it lands.
This record is opened contemporaneously at dispatch.

The block’s entry point is the one
[Agenda 021](../agendas/agenda-021-three-numbers-and-a-wall.md) declares: `BC-211`,
`BC-199` and agenda 019’s `BC-191` together, on three separate cores, with the fourth
core reserved for the retention gate.
The hourly continuity trigger is the floor under the run (`OR-8`), armed before any lane
started and never deleted by the coordinator.
Each lane is a sub-agent at the thinking level its cell declares, briefed with the
cell’s full text, the environment rules, and the instruction to freeze every candidate
and decide none; the coordinator holds the gate, the records, the commits and the PR.
Sub-agent reports are evidence, not verdicts: every retained number is re-derived from
its artifact before it enters a record.

The wall accounting, the four doubling-down rules and the ten-hour continuation are the
agenda’s own and are not restated here.

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
