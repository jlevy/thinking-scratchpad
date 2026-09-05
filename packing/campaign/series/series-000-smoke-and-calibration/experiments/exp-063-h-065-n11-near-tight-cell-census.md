---
title: exp-063 — the near-tight set on the retained n = 11 certificate (BC-201)
softschema:
  contract: packing.squares:Experiment/v2
  schema: ../../../schemas/experiment.schema.yaml
  envelope: experiment
  status: enforced
experiment:
  id: exp-063
  series: series-000
  title: >-
    Census the reachable event cells within four margins of covered mass one, on the
    retained 381/100 certificate, per direction
  date: '2026-09-05'
  hypotheses:
  - H-065
  tier: exploratory
  subject:
    label: >-
      the reachable event cells of the retained n = 11 certificate at outer side 381/100,
      1121 atoms, B = 9977/10000, over all 181 directions of the retained net, counted at
      covered-mass margins 0, 1/100, 1/20 and 1/10
    engine: >-
      sqpack.fractional.sweep's MassGrid and scaled_mass_grid, read through the new
      devtools.census_tight_cells, this branch at 394a0fee
    assurance: verified
    method: exact-algebraic
    host_system: linux x86_64, 4 cores (one used by the lane), Python 3.14.7
    selftest_passed: true
  instance:
    axis: n
    point: 11
    role: target
  method:
    control: >-
      the certificate's own declared least_cell_mass, 4001/4000, which the census must
      reproduce as the minimum; and sweep.reduce_to_cells, retained independently of the
      span reduction the census expands, as the reference for which cells are reachable
    candidate: >-
      the per-direction counts at the four margins, with connected components, the tight
      set's bounding box in the rotated frame, and the summed epsilon = 1/20 ratio
      H-065 registered a threshold on
    runs_per_condition: 1
    interleaved: false
    operator: Claude (agent), Lane B of agenda-021 BC-201 re-run, bead think-614o, session-087
    entry_point: packing/devtools/census_tight_cells.py
    command: >-
      cd packing && OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 uv run
      --frozen --all-extras --group dev python -m devtools.census_tight_cells
    budget: 60 elapsed minutes on one core, the cell's declared budget
    record: packing/campaign/series/series-000-smoke-and-calibration/results/bc-201-n11-tight-cell-census.json
  effort:
    timebox: 60m
    wall_seconds: 967
    agent_minutes: 16
    stopped_by: criterion
  results:
  - shape: record
    role: outcome
    metric: >-
      reachable event cells within 1/20 of covered mass one, summed over the 181
      directions, as a fraction of reachable cells
    direction: lower
    score: 0.040754
    score_str: '23112904/567130649'
    standing_best: 0.2
    standing_best_source: >-
      H-065's own registered acceptance threshold, packing/campaign/hypotheses/H-065-n11-near-tight-cell-census.md.
      No census of this kind has been taken before, so there is no prior measurement to
      improve on; the number to beat is the one the hypothesis wrote down in advance.
    beat_record: true
    runs: 1
  - shape: determination
    role: guard
    question: >-
      Does the census reproduce the certificate's own declared least cell mass, and does
      it agree with the independently retained reachability reference?
    outcome: criterion_met
    checked_by: >-
      the minimum covered mass is exactly 4001/4000 in every one of the 181 directions --
      one distinct value across the whole net, equal to the declared least_cell_mass --
      and direction 0's reachable-cell count of 173,889 agrees with sweep.reduce_to_cells,
      which is retained separately from the span reduction the census expands
  - shape: determination
    role: mechanism
    question: >-
      Is the near-tight set small enough and localised enough for Corollary 1a's exact
      cover to be a check rather than a search?
    outcome: criterion_missed
    checked_by: >-
      four independent readings, all pointing the same way. Count: the bar in the cell was
      "a few hundred cells", and the median direction carries 78,016 at epsilon = 1/20,
      the smallest 4,752. Measure: the tight set has positive area rather than being a
      finite list of positions -- 7.596 per cent of the centre domain aggregated, up to
      19.77 per cent in one direction, and still 1.519 per cent at epsilon = 1/100.
      Extent: its bounding box equals the centre domain's own bounding box exactly, in all
      181 directions, at every non-empty margin including 1/100. Shape: 22,132 components
      at epsilon = 1/20, median about 554 cells each, largest 30,779 -- extended regions,
      not positions
  verdict:
    decision: accepted
    primary_criterion: >-
      the epsilon = 1/20 ratio, summed over the 181 directions, strictly below 0.20
    reason: >-
      The ratio is 23112904/567130649 = 0.040754, a fifth of the threshold and an eighth
      of the 0.50 kill line, so the hypothesis is accepted on the number it registered.
      That acceptance and the cell's own reading point in different directions and both
      are reported: the tight set is a small fraction of the reachable cells, and it is
      still far too large and far too spread out for the exact cover to be a check. The
      threshold was calibrated to catch a tight set covering most of the domain, and four
      per cent is not most; the operative bar for Corollary 1a was a few hundred cells
      near a few dozen positions, and twenty-three million cells in twenty-two thousand
      components is not that either.
    reopen_when: >-
      the same census is taken at a side where the certificate fails, where epsilon can be
      compared against a real mass gap rather than being a band above a floor; or after a
      site-set change that moves the reachable-cell count, since every ratio here is
      against this certificate's own reachable set
    resume_from: >-
      packing/campaign/series/series-000-smoke-and-calibration/results/bc-201-n11-tight-cell-census.json,
      which carries the full per-direction table and is marked complete
---
# exp-063 — Four Per Cent, and Still a Search

`X-014` asked for this census as its third measurement and named the reading it wanted:
a tight set at `epsilon = 1/20` of a few hundred cells clustered around a few dozen
positions makes Corollary 1a’s exact cover a *check*; a fat one makes it a *search*.

The answer is a search, and the interesting part is that `H-065` is accepted anyway.

## The numbers

Over 567,130,649 reachable cells in 181 directions:

| `epsilon` | tight cells | of reachable | of domain by area | components | largest blob |
| --- | ---: | ---: | ---: | ---: | ---: |
| `0` | 0 | 0.0000% | 0.000% | 0 | 0 |
| `1/100` | 4,320,132 | 0.7618% | 1.519% | 10,908 | 16,447 |
| `1/20` | 23,112,904 | **4.0754%** | 7.596% | 22,132 | 30,779 |
| `1/10` | 50,583,976 | 8.9193% | 14.877% | 22,780 | 38,915 |

`H-065` registered acceptance below `0.20` and its kill line at `0.50`. `0.040754` is a
fifth of the first and an eighth of the second, so the hypothesis is accepted on its own
threshold and the mass gap is not swamped.

`epsilon = 0` is empty in every direction.
No reachable cell carries mass exactly one, so `Condition 5` holds with a uniform margin
of `1/4000` and `epsilon` here is genuinely a band above a floor rather than a
neighbourhood of a boundary the certificate touches.

## Why the reading is still “search”

The threshold `H-065` registered answers one question — is the tight set most of the
domain? — and four per cent answers it *no*. The cell asked a different one, and the
count is the smallest part of the answer.

**It has positive area.** Not a finite list of positions but `7.596` per cent of the
centre domain, up to `19.77` per cent in a single direction, and still `1.519` per cent
at the tenth of that margin.
A positive-measure active set is a continuum of near-active covering constraints, not a
set of them to enumerate.

**It is not localised anywhere.** The tight set’s bounding box equals the centre
domain’s own bounding box, exactly, in all 181 directions, at every non-empty margin —
including `epsilon = 1/100`, where it is a hundredth of the domain by area and still
reaches both extremes of both rotated coordinates.
Nor is it a boundary skin: the deepest tight cell in the directions probed sits at
normalised depth `0.41` to `0.43`, where `0.5` is the centre.

**Its parts are regions.** 22,132 components at `epsilon = 1/20`, median about 554 cells
each.
The component counts per direction — 24 to 348, median 136 — are the only statistic
anywhere near “a few dozen”, and they count blobs rather than positions.

So Corollary 1a’s exact-cover step has a positive-measure region to search per
direction, which is what `BC-207` needed to know and could not start without.

## What this is not evidence of

It is what an integrality gap looks like from the inside, and it is not evidence of one.
The census measures the *LP solution’s* near-active set; the integer optimum is a
different object and nothing here bounds it.
The reading is consistent with a gap and would also be consistent with none.

## The instrument

`OR-1` is why this cell exists at all, and the first attempt at it is why the rule is
worth restating: that attempt left a half-built script, no test and no census, and the
script reached a commit anyway.
What is retained now is `devtools/census_tight_cells.py` with
`tests/test_census_tight_cells.py` behind it, reading through the `MassGrid` /
`scaled_mass_grid` seam so the census and the retention decision read the same `int64`
array rather than two implementations of the same fill.
Every count, component, box and minimum is exact integer or `Fraction` arithmetic; the
only floats in the record are two fields named `approx_*`, and no verdict rests on them.

The test’s synthetic is a side-four container with nine atoms on the integer lattice,
chosen so each event cell holds exactly one atom and the whole census — counts,
components, largest blob and all four boxes — can be written out by hand before the tool
runs. Its second anchor is direction 0 of the retained rung, checked against
`reduce_to_cells` rather than against the span reduction the census expands, so the two
paths have to agree.
A third test pins the margin’s meaning into the emitted record: the bookkeeping point
that `epsilon` is a census margin and not the mass gap `M − n`, which at `381/100` is
negative, is now a field a later reader cannot invert.

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
