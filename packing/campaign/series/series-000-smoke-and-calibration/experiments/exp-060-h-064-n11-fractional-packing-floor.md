---
title: exp-060 — H-064's exact-depth fractional packing at 3.82 and 3.85 (BC-200)
softschema:
  contract: packing.squares:Experiment/v2
  schema: ../../../schemas/experiment.schema.yaml
  envelope: experiment
  status: enforced
experiment:
  id: exp-060
  series: series-000
  title: >-
    Measure the n = 11 covering value from below at 191/50 and 77/20 by a cutting-plane
    loop over exact-depth fractional packings, as H-064 registers it
  date: '2026-09-05'
  hypotheses:
  - H-064
  tier: confirmatory
  subject:
    label: >-
      exact depth-scaled total weight of a D4-symmetric family of closed B-square
      placements at net directions, at n = 11 on the retained 181-direction net with
      B = 9977/10000, at container sides 191/50 and 77/20
    engine: >-
      sqpack.fractional.cutting through devtools.run_fractional_cutting, this branch at
      26e8a6e3 (the loop: row generation on the current sites, the dual read as an exact
      family, every arrangement vertex screened in floats and the maximum depth
      certified in exact rational arithmetic, violating vertices added as site orbits)
    assurance: verified
    method: exact-algebraic
    host_system: linux x86_64, 4 cores (one used), Python 3.14.7
    selftest_passed: true
  instance:
    axis: n
    point: 11
    role: target
  method:
    control: >-
      T-018's retained 3.82 dual statistics (76 squares, 608 after the D4 images, raw
      total exactly 11, exact maximum pointwise depth 1925/1152, depth-scaled total
      1152/175 = 6.5829), held fixed as the floor to beat; the family itself is not
      retained anywhere on disk and was regenerated from the grid site set at BC-191's
      density
    candidate: >-
      the cutting-plane loop with the exact vertex check as its separation oracle:
      36-minute wall at 191/50 (cap 150, support cap 96, 12 row rounds per iteration),
      then a 30-minute wall at 77/20 warm-started from the 191/50 state (cap 400,
      support cap 120, 4 row rounds), default rationalisation scale 4,000,000
    runs_per_condition: 1
    interleaved: false
    operator: Claude (agent), Lane B of agenda-021 BC-200, bead think-1qjs, session-086
    entry_point: packing/devtools/run_fractional_cutting.py
    command: >-
      cd packing && OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 uv run --frozen --all-extras
      --group dev python -m devtools.run_fractional_cutting --n 11 --side 191/50 --minutes
      36 --cap 150 --support-cap 96 --rows-rounds 12 --log L --state S --json J --freeze
      F; then --side 77/20 --warm S --minutes 30 --cap 400 --support-cap 120 --rows-rounds
      4
    budget: 110 elapsed minutes on one core, the cell's declared budget
    record: packing/campaign/series/series-000-smoke-and-calibration/results/bc-200-summary-191-50.json
  effort:
    timebox: 110m
    wall_seconds: 3960
    agent_minutes: 96
    stopped_by: timebox
  results:
  - shape: determination
    role: outcome
    question: >-
      Does an exact-depth family at 77/20 reach total weight at least eleven inside the
      timebox (H-064's accepted reading)?
    outcome: criterion_missed
    checked_by: >-
      sqpack.fractional.ceiling.verify_ceiling on the scaled 728-placement family:
      depth at most one at every arrangement vertex holds (24 vertices decided exactly);
      the total-weight condition fails at 45019185620/4974572153 = 9.049861
  - shape: determination
    role: mechanism
    question: >-
      Does the loop raise the exact floor on the fractional packing value nu*(3.82)
      above the retained 1152/175 = 6.5829?
    outcome: criterion_met
    checked_by: >-
      verify_ceiling on the scaled 760-placement family at 191/50: depth at most one at
      all 2,769,100 arrangement vertices (437,480 decided exactly, the rest screened in
      floats below the exact maximum 1.115838 before scaling); total 9.907906
  verdict:
    decision: abandoned
    primary_criterion: >-
      an exact depth-scaled total of at least eleven at 77/20 (accept) or a retained
      certificate below eleven there (reject); a loop stalling below eleven leaves the
      claim unresolved by the hypothesis's own words
    reason: >-
      Both walls expired with depth still 1.12 to 1.24 rather than one, so the loop
      stalled below eleven at both sides and decides nothing about the covering value;
      what it establishes exactly is nu*(3.82) >= 9.907906 and nu*(3.85) >= 9.049861,
      with the converged row loop's restricted optimum 11.055617 on 12,761 sites as the
      certified upper end of the 3.82 bracket.
    budget_spent: 110 minutes of the cell's 110, of which 66 minutes of wall on the two runs
    best_reached: >-
      nu*(3.82) >= 9.907906 (2,769,100 vertices, exact maximum depth 1.115838 before
      scaling); nu*(3.85) >= 9.049861 (2,419,348 vertices, 1.243643); tau*(3.82) <=
      11.055617 on the 12,761-site set
    reopen_when: >-
      a resumed loop from the retained 191/50 state with row generation bounded to one
      or two rounds per iteration, since the bottleneck moved from separation to the
      row loop (958 s at 77/20) as the site support grew
    resume_from: packing/campaign/series/series-000-smoke-and-calibration/results/bc-200-state-191-50.json
---
# exp-060 — H-064’s Exact-Depth Fractional Packing at 3.82 and 3.85

The round is Lane B’s `BC-200` of Agenda 021, run inside its 110-minute budget on one
core. It measured the `n = 11` covering value from below, as
[H-064](../../../hypotheses/H-064-n11-fractional-packing-floor.md) registers it: a
finite family of closed `B`-square placements at net directions whose depth is at most
one at every vertex of the arrangement of their edges, so that its total weight is a
lower bound on the fractional packing value `ν*(L)` and hence on the covering value
`τ*(L)`.

At `191/50 = 3.82`, nine iterations of the cutting-plane loop raised the exact
depth-scaled total from the retained `1152/175 = 6.5829` to `9.907906`, with the row
loop converging at iteration 5 to a restricted optimum of `11.055617` on 12,761 sites,
so the bracket is `9.907906 ≤ ν*(3.82) ≤ τ*(3.82) ≤ 11.055617`. At `77/20 = 3.85`, three
iterations warm-started from the `3.82` state reached `9.049861`; the row loop never
converged there, so no upper end is certified.
Neither family reached eleven, so nothing was frozen under the case package and the
claim stays unresolved in the hypothesis’s own words; the families, their
`verify_ceiling` verdicts, the summaries, the logs and the resumable `3.82` state are
retained beside this record.

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
