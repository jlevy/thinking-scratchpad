---
title: exp-062 — the last rung of H-062's bisection, and the wall it closes on (BC-213)
softschema:
  contract: packing.squares:Experiment/v2
  schema: ../../../schemas/experiment.schema.yaml
  envelope: experiment
  status: enforced
experiment:
  id: exp-062
  series: series-000
  title: >-
    Decide the remaining pre-registered rung of the m = 5 bisection at 973/200 on both
    constructions, and close H-062's bracket
  date: '2026-09-05'
  hypotheses:
  - H-062
  tier: confirmatory
  subject:
    label: >-
      the restricted covering optimum at n = 20 on the retained 181-direction net at
      B = 9977/10000, at the single remaining pre-registered side 973/200, on two
      independently constructed site sets
    engine: >-
      sqpack.fractional.colgen through devtools.colgen_checkpoint (grid construction)
      and devtools.run_fractional_colgen (seeded construction), this branch at ca51821f
    assurance: verified
    method: exact-algebraic
    host_system: linux x86_64, 4 cores (the lane shared the box with two others), Python 3.14.7
    selftest_passed: true
  instance:
    axis: n
    point: 20
    role: target
  method:
    control: >-
      T-021's retained certificate at 97/20 (1680 atoms, mass 19848723/1000000), the
      bracket's lower end and the seed of the second construction; and the side itself,
      which is not chosen here but is the midpoint of the bracket exp-061 left,
      [97/20, 39/8], rounded to the nearest 1/200 with ties away from 24/5 by the
      schedule H-062 fixed before any command of this ladder ran
    candidate: >-
      two site sets at the one side -- the uniform grids at BC-191's density rule, and
      those grids unioned with the 97/20 certificate's 1680 atoms scaled by 973/970 --
      each run until its restricted optimum crossed twenty with placements still
      violated, or until the row loop stopped for want of a violated placement
    runs_per_condition: 1
    interleaved: false
    operator: Claude (agent), Lane A of agenda-022 BC-213, bead think-wufn, session-087
    entry_point: packing/devtools/colgen_checkpoint.py
    command: >-
      cd packing && OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 uv run
      --frozen --all-extras --group dev python -m devtools.colgen_checkpoint --n 20
      --side 973/200 --grid-counts auto --scale 4000000 --column-rounds 1 --max-rounds
      400 --chunk-rounds 4 --deadline-seconds 1500 --log --checkpoint --json --freeze
      (grid construction); and python -m devtools.run_fractional_colgen --n 20 --side
      973/200 --grid-counts auto --scale 4000000 --seed-certificate
      cases/n20_fractional_certificate/certificate.json --seed-map scale
      --deadline-seconds 2400 --log --row-log --json --freeze (seeded construction)
    budget: 60 elapsed minutes on one core, the cell's declared budget
    record: packing/campaign/series/series-000-smoke-and-calibration/results/bc-213-m5-midpoint-register.txt
  effort:
    timebox: 60m
    wall_seconds: 1590
    agent_minutes: 24
    stopped_by: criterion
  results:
  - shape: determination
    role: outcome
    question: >-
      Does the restricted optimum at 973/200 cross twenty with placements still violated
      on both declared constructions, so that the rung walls?
    outcome: criterion_met
    checked_by: >-
      the two runs themselves. The uniform grids at counts (34, 46, 56), 806 orbits and
      6216 sites crossed at LP round 16 with 20.001502 and 543 placements still violated,
      least covered mass 0.890041, after 74.0 s of round time; the grids unioned with the
      97/20 certificate's atoms scaled by 973/970 crossed at LP round 34 with 20.000223
      and 213 placements still violated, after 1072.6 s of round time over 10767 rows.
      Neither loop had completed a column round, so neither site set grew: each optimum
      is a lower bound on that same site set's converged optimum, since adding rows can
      only raise it
  - shape: determination
    role: outcome
    question: >-
      Do the decided rungs leave a bracket of width at most 0.02 around the m = 5
      covering wall, its lower end a retained certificate and its upper end a wall on two
      independent site sets, strictly below the ceiling 9977/2000?
    outcome: criterion_met
    checked_by: >-
      the bracket [97/20, 973/200] itself: width 973/200 - 97/20 = 3/200 = 0.015 against
      the registered 0.02; the lower end is T-021's certificate, retained through
      devtools.decide_certificate with both routes agreeing at 200001/200000; the upper
      end walls on both declared constructions; and 973/200 = 4.865 is strictly below
      9977/2000 = 4.9885 by 0.1235
  - shape: record
    role: mechanism
    metric: margin by which the seeded construction cleared twenty
    direction: lower
    score: 0.0000223
    score_str: '20.000223 - 20'
    standing_best: 0.0004
    standing_best_source: >-
      exp-061, the uniform grid's crossing at 97/20, where the seeded set certified the
      same side
    beat_record: true
    runs: 1
  verdict:
    decision: accepted
    primary_criterion: >-
      a bracket of width at most 0.02 around the m = 5 covering wall, its lower end a
      retained certificate and its upper end a wall on two independent site sets, the
      upper end strictly below 9977/2000
    reason: >-
      Every clause is met. The bracket is [97/20, 973/200], width 0.015. Its lower end
      carries T-021, retained on both routes. Its upper end carries a wall on the two
      independently constructed site sets H-062 declared, and sits 0.1235 below the
      ceiling, so at m = 5 the covering value binds and the ceiling never does. The
      hypothesis is accepted on its own threshold, and this is the first covering wall
      this project has pinned to the width its hypothesis asked for.
    reopen_when: >-
      the wall is wanted to a width the bisection schedule cannot reach -- the schedule's
      leaves are exhausted at 0.015 -- or a site-set rule outside the two H-062 declared
      certifies anywhere inside [97/20, 973/200], which would make the wall a property of
      the declared constructions rather than of the instrument
    resume_from: >-
      packing/campaign/series/series-000-smoke-and-calibration/results/bc-213-m5-midpoint-register.txt,
      with the bracket's lower end at cases/n20_fractional_certificate/certificate.json
---
# exp-062 — The Last Rung, and What “Converged” Had to Mean

`BC-213` had one side to decide.
`exp-061` left the `m = 5` wall inside `[97/20, 39/8]` at width `0.025`, one rung short
of the `0.02` `H-062` registered, and the schedule’s own rule named the next side
without anyone choosing it: the midpoint, rounded to the nearest `1/200` with ties away
from `24/5`, which is `973/200 = 4.865`.

Both constructions walled.
The uniform grids crossed twenty at LP round 16 and the seeded set at round 34, each
with placements still violated, so both fell to the early-refutation clause.
Nothing was frozen, because the cell freezes only on convergence, and
`cases/n20_fractional_certificate/` is untouched by this round.

**The bracket is `[97/20, 973/200]`, width `0.015`.** Its lower end is `T-021`’s
retained certificate and its upper end is this wall.
`H-062` is accepted.

## The clause that needed an argument

`H-062`’s acceptance text asks that the bracket’s upper end “carries a converged
restricted optimum at or above twenty on two independently constructed site sets”.
Neither run here converged.
Read literally that is a miss, and [PR 83](https://github.com/jlevy/squares/pull/83)’s
own limits section had already read it that way about `exp-061`’s crossings.

The reading that holds is the one `H-062`’s `instrument` field states in the same
breath: *adding rows can only raise a restricted optimum.* A site set whose optimum
stands at `20.000223` with `213` placements still violated has a converged optimum of at
least `20.000223`, because every row still to be added can only push it up.
So the converged optimum at or above twenty exists and is bounded below by twenty on
both site sets; what was not computed is its *value*, and the criterion does not ask for
the value. This is exactly the asymmetry the schedule was built to exploit — refutation
early, confirmation only by convergence — and applying it here is applying the rule as
written, not relaxing it.

Both directions were checked against the program rather than against the prose that
describes it. `sqpack.fractional.colgen.solve_lp` minimises the site sizes subject to
`A x >= 1` with `x >= 0`, one row per held placement and one column per site orbit.
A row is a constraint, so adding one shrinks the feasible set and the minimum can only
rise; a site is a column, so adding one enlarges it and the minimum can only fall.
The asymmetry `H-062` built its schedule on is a property of that formulation, not a
convention.

One boundary matters and is worth stating so no one has to re-derive it: the
monotonicity is in **rows**, at a fixed site set.
Adding *sites* lowers a restricted optimum.
Neither run completed a column round, so neither site set grew, and each crossing is a
statement about the site set that produced it — which is what `H-062`’s `regime` section
already says a converged optimum at or above twenty is.
No run in this register has measured the unrestricted covering value, and this one does
not either.

## The closest call in the register

The seeded set cleared twenty by `2.23` parts in a hundred thousand.
The uniform grid at `97/20` — the rung immediately below, where the seeded set went on
to certify — cleared it by four parts in ten thousand, about eighteen times as much.
The approach was a walk rather than a jump: `19.996458`, `19.997545`, `19.998396`,
`19.999167`, `19.999837`, `20.000223` over six rounds, with the violated count
collapsing into it at `480, 363, 381, 279, 213`.

The pre-registered rule does not read margins and was applied as written.
But a wall cleared by `2e-5` on a loop that was running out of violated placements is a
different object from one cleared by `4e-4`, and the register should say so rather than
flatten both into “refuted”.
If any rung in this bracket is worth a second look under a denser site set, it is this
one — and the shape of the doubt is precise: more *sites* would lower the optimum, and
`973/200` is where that has the least room to be irrelevant.

## Two things about the tooling, not the mathematics

`kill` on a `uv run` wrapper does not kill the Python child it spawned.
The lane stopped the grid construction after its crossing and the row loop kept running
for six more minutes, reaching round 24 at `20.095294` with `525` violated.
Those rounds are in the register rather than trimmed out: they only strengthen the
refutation, and a run record that quietly drops the rounds that happened is worse than
one that explains them.

The lane also did not have the core its budget assumed.
`BC-206`’s `n = 12` column generation and a full `pytest` run shared the box throughout,
so the wall seconds here are inflated against `exp-061`’s and should not be compared to
them. LP values are arithmetic and are unaffected; both constructions stopped on a
crossing rather than a deadline, so contention changed neither outcome.
Only the cost column is untrustworthy, and only upward.

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
