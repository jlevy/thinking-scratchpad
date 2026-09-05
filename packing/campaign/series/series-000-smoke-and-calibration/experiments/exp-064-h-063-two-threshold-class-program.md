---
title: exp-064 — the two-threshold class program, and the control that could not be reached (BC-198)
softschema:
  contract: packing.squares:Experiment/v2
  schema: ../../../schemas/experiment.schema.yaml
  envelope: experiment
  status: enforced
experiment:
  id: exp-064
  series: series-000
  title: >-
    Build X-014's Lemma 3 as per-direction-class thresholds and run its two controls at
    n = 11
  date: '2026-09-05'
  hypotheses:
  - H-063
  tier: confirmatory
  subject:
    label: >-
      the two-threshold covering program at n = 11 on the retained 181-direction net at
      B = 9977/10000, with direction classes as unions of half-gap cells and w0, w1 as LP
      variables under one normalisation row
    engine: >-
      sqpack.fractional.classcert through devtools.run_class_program, this branch at
      07155377, deciding on the same event-cell sweep the retention gate uses
    assurance: verified
    method: exact-algebraic
    host_system: linux x86_64, 4 cores shared with two other lanes, Python 3.14.7
    selftest_passed: true
  instance:
    axis: n
    point: 11
    role: target
  method:
    control: >-
      two controls fixed by the cell before any command ran -- the nine-point bound, where
      nine unit atoms on the pitch-s/4 grid are feasible for the near-axis class program
      by construction so its optimum must be at most nine; and Stromquist, where the class
      of the net's two end half-gap cells must refute the composition (11, 0) at a side at
      or above Trump's 3877084/1000000
    candidate: >-
      the class program itself: DirectionClasses partitioning the net's half-gap cells
      with boundaries carried as exact tangents, solve_class_program separating each
      placement against its own class's threshold, and decide_class_program deciding the
      same object exactly on the event-cell sweep
    runs_per_condition: 1
    interleaved: false
    operator: Claude (agent), Lane A of agenda-021 BC-198, bead think-m3sx, session-087
    entry_point: packing/devtools/run_class_program.py
    command: >-
      cd packing && OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 uv run
      --frozen --all-extras --group dev python -m devtools.run_class_program nine-point;
      then stromquist; then price
    budget: 110 elapsed minutes, the cell's declared budget
    record: packing/campaign/series/series-000-smoke-and-calibration/results/bc-198-class-program-register.txt
  effort:
    timebox: 110m
    wall_seconds: 1665
    agent_minutes: 25
    stopped_by: criterion
  results:
  - shape: determination
    role: guard
    question: >-
      Does the near-axis class program at 3877/1000 return an optimum of at most nine, as
      the nine-point measure makes it must?
    outcome: criterion_met
    checked_by: >-
      exactly nine, decided both ways. The float LP converged to 9.000000 in five rounds
      and the exact decision returns 9 from nine unit atoms with least cell mass exactly
      one over the six leading cells; the rationalised LP point gives 36873/4096 =
      9.002197 with margin -8183/4096, refuted. The lane added the other side of the
      bound, that nine pairwise disjoint axis-parallel B-squares fit, so the optimum is
      exactly nine rather than merely at most nine. The instrument is not defective and
      the cell's suspension clause does not fire
  - shape: determination
    role: outcome
    question: >-
      Does the two-end-cell class program refute the composition (11, 0) at a side at or
      above Trump's 3877084/1000000?
    outcome: criterion_missed
    checked_by: >-
      it cannot, and the figure that says so is exact and independent of every site set.
      At that side the class gives 11885/1024 = 11.606445 over 72 atoms, least cell mass
      2049/2048, margin +621/1024 against the eleven a refutation needs, with float and
      exact agreeing so the disagreement kill does not fire; six independently built site
      sets, counts 23 to 95 and insets 1/5 to 1/20, never go below 11.6. The program
      refutes at 3755/1000 and not at 3760/1000, both below the threshold
  - shape: record
    role: mechanism
    metric: the highest side at which the two-end-cell class program can refute (11, 0)
    direction: higher
    score: 3.876681
    score_str: 'B(2 + (4/3)sqrt(2))'
    standing_best: 3.877084
    standing_best_source: >-
      Trump's n = 11 packing, the side H-063 set as the threshold this control had to reach
    beat_record: false
    runs: 1
  - shape: record
    role: cost
    metric: seconds for one class program over 181 directions to convergence at grid 39
    direction: lower
    score: 27.66
    score_str: '27.66 s, 18 rounds, against 8.57 s and 14 rounds at grid 23'
    standing_best: 330.0
    standing_best_source: >-
      the cell's own budget line, which priced twelve compositions as the quantity to
      measure; at grid 39 they come to about 5.5 minutes of one core
    beat_record: true
    runs: 2
  verdict:
    decision: rejected
    primary_criterion: >-
      the two-end-cell class program refuting (11, 0) at a side at or above 3877084/1000000,
      with the near-axis class program at that side returning at most nine
    reason: >-
      The second clause holds exactly and the first cannot, so H-063 falls to its own
      rejection clause -- X-014's kill condition, that conditioning on direction buys too
      little. What makes this a strong negative rather than a failed search is that the
      refusal is proved rather than observed. At Trump's side L/B = 969271/249425 =
      3.886021850 exceeds 2 + (4/3)sqrt(2) = 3.885618083, decided against the surd, so
      eleven pairwise disjoint B-squares of the class fit inside the container and no
      measure of total mass below eleven can cover them -- whatever site set is used and
      however long the row loop runs. The control's own ceiling is
      B(2 + (4/3)sqrt(2)) = 3.876681, which is 0.000403 below the side it was asked to
      reach: the shrink costs 0.008937 of side and Stromquist's headroom above Trump is
      only 0.008534. The control was unreachable before the first command ran, and no
      amount of instrument work would have changed that.
      Conditioning is not worthless, and the round reports what it does buy rather than
      only what it does not. On one site set at Trump's side a single threshold gives
      margin +0.082256 where two thresholds at composition (9, 2) give +0.072368, with
      the LP separating them once the site set is fine enough. And X-014's own step-1
      design point is reachable: composition (11, 0) over the leading nineteen cells at
      Trump's side and grid 79 gives exact 39123/4096 = 9.551514, margin -5933/4096,
      every condition holding, refuted. What the program cannot do is reach the side
      Stromquist's Theorem 3 reaches, because that theorem gets there by a further box
      step this program does not have.
    reopen_when: >-
      the non-convex admissible domain BC-204 owns exists, since the box step that
      separates Stromquist's 3.885618 from this program's 3.876681 is a conditional
      certificate over a domain the sweep cannot currently express; or a class shape
      other than the two end cells is proposed for the same composition
    resume_from: >-
      packing/campaign/series/series-000-smoke-and-calibration/results/bc-198-class-program-register.txt,
      219 lines, with the six items the program cannot decide written out verbatim
---
# exp-064 — A Control That Could Not Be Reached

`BC-198` built `X-014`’s Lemma 3 and ran its two pre-registered controls.
One passed exactly. The other refused, and the interesting part is that it could never
have done anything else.

## What was built

`classcert.py` partitions the net’s half-gap cells into direction classes, carrying the
boundaries as exact tangents — the midpoint angle’s tangent is rational even where its
half-tangent is not.
`solve_class_program` adds `w0` and `w1` as LP variables under the single normalisation
row `n0·w0 + n1·w1 = 1` and separates each placement against its own class’s threshold;
`decide_class_program` decides the same object exactly on the event-cell sweep,
reporting Conditions 1, 3 and 4 unchanged, `Condition 5'` per class and `Condition 2'`
as `M < n0w0 + n1w1`.

Nothing geometric moved.
`sweep.centre_domain`, the float mirror in `generate.py` and the four half-planes
`interval.DirectionSearch` propagates are untouched, which is what kept this a threshold
change and left the non-convex domain to `BC-204`.

## Control one: exactly nine

The near-axis class at `3877/1000` returns `9.000000` in floats, converged in five
rounds, and exactly `9` from nine unit atoms with least cell mass exactly one over the
six leading cells. The lane then closed the bound from below as well — nine pairwise
disjoint axis-parallel `B`-squares fit — so the optimum is *exactly* nine, not merely at
most nine. The cell’s suspension clause, which treats an optimum above nine as an
instrument defect, does not fire.

## Control two: `0.000403` short, and not by accident

At Trump’s `3.877084` the two-end-cell class gives `11885/1024 = 11.606445` against the
eleven a refutation needs.
Six independently built site sets never go below `11.6`.

That is not a search that ran out of budget.
The figure that refuses it is exact and does not mention a site set:

`L/B = 969271/249425 = 3.886021850` exceeds `2 + (4/3)√2 = 3.885618083`.

So eleven pairwise disjoint `B`-squares of the class fit inside the container at that
side, and no measure of total mass below eleven can cover them — whatever sites are
chosen, however long the row loop runs.
The control’s ceiling is `B(2 + (4/3)√2) = 3.876681`, which sits **`0.000403` below the
side the cell asked it to reach**. The shrink costs `0.008937` of side; Stromquist’s
headroom above Trump is `0.008534`. The control was unreachable before the first command
ran.

`H-063`’s own text anticipated the shape without noticing the arithmetic: it says
Stromquist’s Theorem 3 reaches `3.885618` “by a further box step this program does not
have”, and sets the threshold at `3.877084` precisely because the program should not be
credited with reach it lacks.
What nobody computed in advance is that removing the box step also removes `0.000403`
more than the margin between the two sides.

## What conditioning does buy

The round reports this rather than only the refusal, because “conditioning buys too
little” is the kill condition and the amount matters.

Two thresholds do separate.
On one site set at Trump’s side a single threshold gives margin `+0.082256`; two at
composition `(9, 2)` give `+0.072368`, with the LP pulling `w0 = 0.093383` above
`w1 = 0.079777` once the site set is fine enough.
And `X-014`’s own step-1 design point is reachable: composition `(11, 0)` over the
leading nineteen cells at Trump’s side, grid 79, exact `39123/4096 = 9.551514`, margin
`−5933/4096`, every condition holding, refuted.
The `11.000000` readings at grids 39 and 95 are the round-number artefact this register
now recognises at three orders, not a wall.

Nothing was retained.
`decide_certificate` decides a five-condition `Certificate` and not a two-threshold
object; registering a class theorem is `BC-208`’s gate work.

## The price, which is what the cell existed to produce

One class LP solve is `14.4 ms` mean and `22.3 ms` max at 78 orbits plus two thresholds
and 1191 rows; `49.4 ms` and `82.2 ms` at 210 orbits and 1554 rows.
A whole class program over all 181 directions with both classes active, run to
convergence, is `8.57 s` at grid 23 and `27.66 s` at grid 39. Twelve compositions at
grid 39 price at about five and a half minutes of one core.

**The LP is under two per cent of that.** Separation, not the LP, is what a composition
sweep buys — which is the number `BC-208` needs and the reason this cell was worth its
budget even though its headline control refused.

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
