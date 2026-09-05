---
title: exp-061 — H-062's pre-registered bisection of the m = 5 ladder (BC-197)
softschema:
  contract: packing.squares:Experiment/v2
  schema: ../../../schemas/experiment.schema.yaml
  envelope: experiment
  status: enforced
experiment:
  id: exp-061
  series: series-000
  title: >-
    Bracket the m = 5 covering wall by four pre-registered rungs, reading the n = 21
    criterion at the ceiling first, as H-062 registers it
  date: '2026-09-05'
  hypotheses:
  - H-062
  tier: confirmatory
  subject:
    label: >-
      the restricted covering optimum at n = 20 and n = 21 on the retained 181-direction
      net at B = 9977/10000, at the pre-registered sides 997/200, 979/200, 97/20, 193/40
      and 39/8, on two independently constructed site sets per rung
    engine: >-
      sqpack.fractional.colgen through devtools.colgen_checkpoint (grid construction,
      chunked and resumable) and devtools.run_fractional_colgen (seeded construction),
      this branch at 5d07a24a, with devtools.decide_certificate as the retention gate
    assurance: verified
    method: exact-algebraic
    host_system: linux x86_64, 4 cores (one used by the lane), Python 3.14.7
    selftest_passed: true
  instance:
    axis: n
    point: 20
    role: target
  method:
    control: >-
      T-020's retained certificate at 24/5 (2260 atoms, mass 946131/50000), the ladder's
      lower end and the seed of the second construction at every rung; and the
      pre-registered bisection schedule of [24/5, 9977/2000], rounded to the nearest
      1/200 with ties away from 24/5, fixed before any command ran
    candidate: >-
      per rung two site sets -- the uniform grids at BC-191's density rule, and those
      grids unioned with the 24/5 certificate's atoms scaled to the rung's side -- each
      run to convergence or to a crossing of the size threshold, with refutation early
      (rows only raise a restricted optimum) and confirmation only by a converged row
      loop followed by a freeze
    runs_per_condition: 2
    interleaved: false
    operator: Claude (agent), Lane A of agenda-021 BC-197, bead think-g73w, session-086
    entry_point: packing/devtools/colgen_checkpoint.py
    command: >-
      cd packing && OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 uv run
      --frozen --all-extras --group dev python -m devtools.colgen_checkpoint --n 20
      --side <L> --grid-counts auto --scale 4000000 --column-rounds 1 --max-rounds 400
      --chunk-rounds 4 --deadline-seconds 1500 (grid construction); and python -m
      devtools.run_fractional_colgen --n 20 --side <L> --grid-counts auto --scale 4000000
      --seed-certificate cases/n20_fractional_certificate/certificate-24-5.json --seed-map
      scale --deadline-seconds 2400 (seeded construction)
    budget: 200 elapsed minutes on one core, the cell's declared budget
    record: packing/campaign/series/series-000-smoke-and-calibration/results/bc-197-ladder-register.txt
  effort:
    timebox: 200m
    wall_seconds: 5000
    agent_minutes: 88
    stopped_by: guard
  results:
  - shape: determination
    role: outcome
    question: >-
      Do the four decided rungs leave a bracket of width at most 0.02 whose lower end
      carries a certificate retained through the gate and whose upper end walls, below
      the ceiling 9977/2000 (H-062's accepted reading)?
    outcome: criterion_missed
    checked_by: >-
      the decided rungs themselves: a certificate at 97/20 = 4.85 retained through
      devtools.decide_certificate (both routes agreeing at 200001/200000) and crossings
      above twenty on both constructions at 39/8 = 4.875, which bracket the wall to
      width 0.025 against the registered 0.02
  - shape: record
    role: outcome
    metric: certified container side at n = 20 and n = 21
    direction: higher
    score: 4.85
    score_str: '97/20'
    standing_best: 4.8
    standing_best_source: packing/frontier/results.yaml T-020 (24/5)
    beat_record: true
    runs: 1
  - shape: determination
    role: mechanism
    question: >-
      Is the wall at 997/200 = 4.985, just below the ceiling, the covering value's or an
      artefact of the site set?
    outcome: criterion_met
    checked_by: >-
      the geometry, checked against every grid count the lane could afford: with
      delta = 5B - L = 0.0035 the twenty-five axis-parallel B-squares overlap only in
      strips of that width, the restricted dual is checked at sites only, and no uniform
      inset-1/2 grid puts a site in every strip, so twenty-five unit weights are
      dual-feasible and the optimum is exactly 25.000000 whatever the covering value is
  verdict:
    decision: unresolved
    primary_criterion: >-
      a bracket of width at most 0.02 around the m = 5 covering wall, its lower end a
      retained certificate and its upper end a wall on two independent site sets
    reason: >-
      The four decided rungs bracket the wall to [97/20, 39/8], width 0.025 against the
      registered 0.02, so the hypothesis is neither accepted on its own threshold nor
      rejected by either of its two rejection clauses -- no certificate was retained at
      4.98 or above, and optima above twenty were found well below the ceiling.
    reopen_when: >-
      the remaining rung, the midpoint of [97/20, 39/8] by the schedule's own rule, is
      run on both constructions; that rung alone decides the registered threshold
    resume_from: >-
      packing/campaign/series/series-000-smoke-and-calibration/results/bc-197-ladder-register.txt,
      with the retained rungs at cases/n20_fractional_certificate/certificate.json and
      certificate-193-40.json
---
# exp-061 — H-062’s Pre-Registered Bisection of the m = 5 Ladder

The round is Lane A’s `BC-197` of Agenda 021, run unattended by a ladder script that
applied the pre-registered rule: kill a rung on a crossing of the size threshold with
placements still violated, freeze it on convergence, and take the next side by
bisection.

Five sides were decided on two independently constructed site sets each.
`997/200` was read on the `n = 21` criterion first and refuted on three constructions,
for a reason this round explains rather than records: just below the ceiling the
twenty-five axis-parallel `B`-squares overlap only in strips of width `5B − L = 0.0035`,
and a site set with no site in those strips makes twenty-five unit weights
dual-feasible, so the restricted optimum is exactly `25.000000` whatever the covering
value is. The exactly round value this register has learned to distrust has, at `m = 5`,
a mechanism.

Below it the bisection walled at `979/200` and `39/8`, and certified at `193/40` and at
`97/20`, the latter on the seeded construction after the uniform grid crossed twenty by
four parts in ten thousand.
Both certificates were frozen by the lane and decided by the coordinator through the
retention gate; the `97/20` rung is registered as
[T-021](../../../../frontier/RESULTS.md) and the `193/40` rung is retained beside it.
The wall is bracketed to `[4.85, 4.875]`, width `0.025` against the `0.02` the
hypothesis registered, so H-062 is unresolved and one rung short.

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
