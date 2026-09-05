---
title: "agenda-019 — efficiency first: the decision path, the retarget, and two deep strategy sessions"
softschema:
  contract: packing.squares:ExperimentAgenda/v1
  schema: ../schemas/agenda.schema.yaml
  envelope: agenda
  status: enforced
agenda:
  id: agenda-019
  title: "Efficiency First — the Decision Path, the Retarget, and Two Deep Strategy Sessions"
  updated: '2026-09-04'
  status: paused
  objective: >-
    Agenda 017's block moved seven registered cases and then hit a wall that is not
    mathematical. The exact event-cell sweep grew superlinearly with the atom count until
    a single decision cost hours, one search spent fifty-five minutes failing to finish
    its first round on a parameter that was tuned two container sides ago, and four lanes
    were run on four cores with no budget until the load average reached 10.6. None of
    that is a limit on the method; all of it is a limit on how many rungs a block can
    climb.
    This agenda buys throughput before it buys bounds, in that order, because the reach
    table now says the cases worth attacking are two to three times the container side of
    the ones just climbed, and cost grows with the square of the side or worse. Two
    efficiency-loop commitments carry measured baselines from Agenda 017's own logs and a
    named target each. Two insight-iteration sessions then ask the mathematical questions
    the ceiling proof opened, which is what should choose the next targets rather than
    the ladder's momentum. One research-loop commitment spends the throughput on the
    first high-prize case with a cost model recorded before the run, not after.
    The research wall is 480 elapsed minutes. The efficiency work is first because
    everything after it is measured in units the efficiency work changes.
  items:
  - id: BC-190
    purpose: tool_validation
    owner_focus: efficiency
    instances: [11, 12, 17, 20]
    state: ready
    priority: 0
    question: >-
      The interval route decides more directions on fewer hypotheses than the exact sweep
      and did so 22.7 times faster at 1184 atoms and 44.2 at 2097 on identical frozen
      bytes, the ratio widening because the two scale differently. Can the generator's own
      accept-or-reject decision move to it, keeping the exact sweep for retention and the
      exhaustive tier, and what does that do to the tail of a run?
    budget: >-
      120 elapsed minutes, Opus at maximum thinking, efficiency-loop throughout.
      The baseline is already measured and is the entry condition, not the first task.
      Two runs of devtools.decide_certificate timed both routes back to back on the same
      frozen bytes, which is the only comparison worth quoting: earlier figures taken from
      separate runs hours apart under different loads were wrong by nearly a factor of
      three, and one of them was read off elapsed wall time while four lanes contended for
      four cores rather than measured at all.
      Paired, 1184 atoms took the exact sweep 1473 s against the interval route's 65 s,
      and 2097 atoms took 4866 s against 110 s. That fixes both exponents: the exact sweep
      scales as atoms^2.09 and the interval route as atoms^0.92, quadratic against linear,
      which is why the ratio widens -- 22.7 times at 1184 atoms, 44.2 at 2097.
      0--30 confirm both exponents at two further atom counts, since two points fix a line
      and three test it, and record which phase of the sweep dominates -- event-cell
      construction, the prefix sum, or the per-direction pass -- because an algorithmic
      win is only available if one of them does.
      30--80 change the generator's decision to the interval route and measure the tail
      of a full run end to end against Agenda 017's recorded runs at the same sides.
      The equivalence guard is not optional and is the whole of the correctness argument:
      every certificate the interval decision accepts must still pass
      devtools.decide_certificate before retention, so the exact sweep moves from the
      inner loop to the gate and is never removed. Retention is unchanged.
      80--120 measure what the change buys on a case that could not be afforded before,
      and record the benchmark whether the answer is good or bad.
    entry: >-
      Agenda 017's run logs and the three paired measurements above are in the record,
      devtools.decide_certificate is the retention gate, and the fractional tier is green.
    exit: >-
      A benchmark record with the fitted cost exponent for the exact sweep, a named
      dominant phase, the measured end-to-end delta from moving the generator's decision,
      and either the change with its equivalence guard intact or a written rejection with
      the number that killed it.
    bead: think-jgeg
    workflows: [efficiency-loop]
    depends_on: []
    next_evidence: >-
      Whether the decision path is still the tail of a run, which decides whether BC-194
      is affordable at the side it names.
  - id: BC-191
    purpose: tool_validation
    owner_focus: efficiency
    instances: [12, 17, 18, 20]
    state: complete
    priority: 0
    question: >-
      Row generation is between 79 and 94 per cent of every round, the site grids do not
      scale with the container, and the rationalisation scale cost five times the margin
      that survived at the last rung. Which of the three is worth fixing, measured rather
      than guessed?
    budget: >-
      120 elapsed minutes, Opus at maximum thinking, efficiency-loop, in parallel with
      BC-190 on a separate core.
      Three measured baselines, all from Agenda 017's logs.
      First, round composition: at n = 12 a late round spent 1261 s in row generation
      against 86 s pricing; at n = 17, 472 to 761 s against 87 to 124 s; at n = 20, 500
      to 1158 s against 85 to 106 s. Row generation is the round.
      Second, site density. build_site_grid places a fixed count of points across the
      container, so the spacing grows with the side and the sites thin out relative to the
      B-square that has to cover them. At n = 20, side 24/5, grids (23, 31, 39) spent more
      than 3300 s without completing round 0; (29, 39, 49) completed it in 376 s. At least
      8.8 times, found by accident, on a parameter tuned when the sides were near 3.9.
      Third, rationalisation. The rounding loss is at most atoms/scale, and at n = 12,
      side 99/25, scale 200,000 and 2097 atoms it was 0.005314 -- five times the 0.001040
      margin the certificate ended with. The rung survived by luck. At scale 4,000,000 the
      loss would be about 0.00027 and the atom count does not change with the scale.
      0--40 measure whether solve_rows re-solves from scratch each round or warm-starts,
      and what max_rounds and rows_per_direction actually cost at three sides. 40--80
      measure the site-density trade properly: denser grids buy fewer rows and cost more
      columns, and the crossover has never been located. 80--110 raise the default
      rationalisation scale and measure the verification cost it adds against the margin
      it returns. 110--120 record a core budget: four lanes ran on four cores at load 10.6
      and everything ran about two and a half times slower than it needed to.
    entry: >-
      The run logs for n = 12, 17, 18 and 20 at the sides named, and the two n = 20 runs
      at different grids, are retained and comparable.
    exit: >-
      A benchmark record for each of the three, a site-density rule expressed as a
      function of the container side rather than a constant, a decision on the default
      scale with its measured verification cost, a stated core budget, and every rejected
      change recorded with the measurement that rejected it.
    bead: think-ji0r
    workflows: [efficiency-loop]
    depends_on: []
    artifacts:
    - packing/devtools/bench_colgen.py
    - packing/tests/test_bench_colgen.py
    - packing/src/sqpack/fractional/colgen.py
    outcomes:
    - scope: >-
        Row generation, site density and the rationalisation scale, measured on one
        core at four sides (3.96, 4.59, 4.80, 5.52) inside ten-minute runs.
      classification: achieved
      result: >-
        Round composition: solve_lp builds a fresh HiGHS linprog every round and scipy
        exposes no basis, so no warm start exists; separation is 79 to 94 per cent of
        a round only while the row set is small (at 16168 rows the LP is 67 per cent);
        separation fits 1.19e-5 * support^1.95 and the LP 1.20e-6 * rows^1.62; cost
        per LP round against the side fits 0.0189 * L^3.657 (2.953, 4.569, 6.241 s at
        3.96, 4.59, 4.80, confirmed at 5.52), pricing is 1.6 per cent of a run, and
        round 0's 14.6 to 42.5 s sawtooth is event_grid's live[::N//600] stride.
        Site density: five-rung ladders at 99/25 (n = 12) and 24/5 (n = 20) put the
        interior optimum at the same density, so the rule is count = round((L - 2
        inset) d / B) + 1 with d = (8.5, 11.5, 14.25) sites per B-square, exposed as
        site_counts_for_side -- (26, 35, 44) at 399/100, (33, 45, 55) at 24/5,
        (40, 53, 66) at 138/25; the inherited (23, 31, 39) is the band's lower edge,
        reaching 20.168732 at 24/5 where the optimum reaches 19.339779. Scale: the
        loss is atoms/(2 scale) + 1e-6 total, the verification cost is flat in the
        scale (2.86/2.89/2.83 s and 8.97/8.25/8.24 s across a 20x range) because the
        sweep's grid comes from atom coordinates, the largest scaled total sits 5.1e9
        under 2**60, so DEFAULT_SCALE is raised from 200,000 to 4,000,000, returning
        0.005040 of the 0.005314 lost at n = 12's 99/25. Core budget: verify(workers=
        None) takes up to four processes per certificate and never consults PACK_JOBS,
        which is where agenda 017's load 10.6 came from; three lanes on three cores
        with the fourth for the gate and every in-lane verify at workers=1. Rejected,
        each with its measurement: an LP warm start at n = 12 (LP 11.8 of 62.0 s; the
        top lead at n >= 17 where the LP is 162.4 of 242.1 s), rows_per_direction 1, 2
        or 6 (identical optimum, 3 cheapest), raising max_rounds (never bound), densities
        at or above 9.7 per B-square (123.1 s unconverged at n = 12), scales 1,000,000
        and 20,000,000, and the 600-site stride (about 12 s of 60.8 s, but it changes
        which rows round 0 generates and the equivalence question did not fit).
      evidence:
      - packing/devtools/bench_colgen.py (rounds, density, scale, summarise, costmodel)
      - packing/tests/test_bench_colgen.py (7 tests, including the guard that a timed solve_rows decides identically to an untimed one)
      - session-086 Lane C delegation, 3258 s platform-measured, 55 of 120 budgeted minutes
      disposition: retire-success
      follow_up: null
    next_evidence: >-
      The cost per round as a function of the container side, which is the input BC-194's
      cost model needs and which nobody has yet measured across sides.
  - id: BC-192
    purpose: research
    owner_focus: insight
    instances: [11, 12, 17, 26, 51]
    state: blocked
    priority: 1
    question: >-
      The ceiling proof and the reach table changed the map: the cases this program spent
      itself on rank near the bottom, and eleven cases just above a perfect square are
      worth five to eight times more. Is that ranking the right one to act on, and what
      does the covering value do between here and there?
    budget: >-
      90 elapsed minutes, Opus at maximum thinking, insight-iteration. No experiment runs
      inside this commitment and no hypothesis is certified in it.
      The material is in the record: frontier/CERTIFICATE-REACH.md, the ceiling derivation
      in sqpack.fractional.certificate, and the five restricted optima that are the whole
      of what is known about how the covering value grows -- 11.0000 at 3.82, 11.9706 at
      3.95, 11.9936 at 3.96, 16.9628 at 4.58, 16.9303 at 4.59.
      The session's first duty is to be honest about that curve. Five points fit a
      quadratic in the side; a fit is not a measurement, no rung has ever been claimed
      from one, and the reach table's prize column is what the ceiling allows rather than
      what a search reaches. If the session's conclusion depends on the fit, it must say
      so and name the measurement that would settle it.
      Questions worth the time: whether the covering value's growth has a derivation
      rather than a fit; whether a certificate found at one side transfers to a nearby
      side or to a larger n as a warm start, given that the covering program does not
      contain n at all; whether the cases above a perfect square are genuinely easier or
      merely have looser recorded bounds; and what the retained ladders say about how much
      of the gap between a restricted optimum and the covering value a search actually
      closes.
    entry: >-
      BC-190 and BC-191 are terminal, so the session knows what a run costs, and the reach
      table and ceiling derivation are retained and drift-checked.
    exit: >-
      One X-NNN report with the conclusions and their evidential status separated, any
      H-NNN candidates with mechanism, falsifier and expected information, an explicit
      statement of which conclusions rest on the fitted curve, and a ranked target list
      that BC-194 can take without re-deriving it.
    bead: think-9pfw
    workflows: [insight-iteration]
    depends_on: [BC-190, BC-191]
    next_evidence: >-
      A target ranking that accounts for cost as well as prize, which the reach table
      deliberately does not.
  - id: BC-193
    purpose: research
    owner_focus: insight
    instances: [11, 12]
    state: blocked
    priority: 2
    question: >-
      No certificate of this shape exists above ceil(sqrt(n)) * B, so the method
      approaches the grid bound and never reaches it, and n = 12 is foreclosed against its
      conjectured 4. What would a method that escapes that ceiling have to look like?
    budget: >-
      90 elapsed minutes, Opus at maximum thinking, insight-iteration, after BC-192.
      The ceiling has one mechanism and it is worth attacking directly: above
      ceil(sqrt(n)) * B a grid of ceil(sqrt(n))^2 pairwise disjoint axis-parallel
      B-squares fits inside the container, Condition 5 gives each of them mass at least 1, and the
      total passes n. Every step of that is cheap, which is why the ceiling is sharp.
      Directions worth an hour and a half. The refuting grid is axis-parallel and uses
      direction 0 only; a condition that treated directions unequally would not be refuted
      by it, but Condition 4's containment argument is what forces every direction to be covered,
      so the question is whether a weaker containment step exists. The shrink B is already
      maximal for its net, so raising it needs a finer net and the ceiling rises only as
      fast as D falls, which is about T/K. Whether an unavoidable set of shapes other than
      squares, or a condition on pairs rather than singles, changes the counting argument.
      And whether the foreclosure is worth accepting: n = 12 conjectured at 4 may simply
      not be this instrument's case, and saying so plainly is a legitimate outcome.
      A negative result here is a real result and is recorded as one.
    entry: >-
      BC-192 is terminal and the ceiling derivation with its four tests is retained.
    exit: >-
      One X-NNN report, either a candidate mechanism registered as an H-NNN with a
      falsifier, or a written argument that the ceiling is intrinsic to the counting step
      and the instrument's reach is what the reach table says it is.
    bead: think-z8ck
    workflows: [insight-iteration]
    depends_on: [BC-192]
    next_evidence: >-
      Whether the frontier beyond the ceiling is a research direction or a closed door,
      which decides whether any later agenda spends a block on it.
  - id: BC-194
    purpose: research
    owner_focus: correctness
    instances: [26, 30, 37, 51]
    state: blocked
    priority: 1
    question: >-
      With the decision path and the generator parameters measured, can a certificate be
      found at the first high-prize case -- a size just above a perfect square, where the
      lower bound is Nagamochi's closed form and the gap to the best known packing is near
      half a unit?
    budget: >-
      180 elapsed minutes, Opus at maximum thinking, research-loop, on the target BC-192
      ranks first.
      The cost model is recorded before the run and not after. At side 4.8 a round cost
      between 500 and 1158 s with grids scaled to the container; the sides in question are
      5.1 to 7.2, where the domain is between 1.1 and 2.3 times the area, so a round is
      estimated at 1400 to 3000 s before BC-191's changes and the estimate is written down
      so the run can be judged against it.
      The registered side is fixed before any command runs. The stop rule is the wall, not
      a converged objective: a run that does not close inside the budget is time-limited
      and its checkpoint carries to the next agenda, which is what happened to every long
      run in Agenda 017 and cost nothing because the checkpoints were sound.
      Retention is unchanged and is not negotiable: freeze the candidate before deciding
      it, decide the frozen bytes through devtools.decide_certificate, and retain only
      when both routes accept and agree on the value.
    entry: >-
      BC-190, BC-191 and BC-192 are terminal, a target and a side are registered, and the
      cost model is written down.
    exit: >-
      Either a retained certificate with both routes agreeing, or a measured negative with
      the restricted optimum the run reached, the loop's final least covered mass, and the
      cost per round against the model -- which is the number the next cost model needs.
    bead: think-48p0
    workflows: [research-loop]
    depends_on: [BC-190, BC-191, BC-192]
    next_evidence: >-
      The first measurement of what the generator costs and reaches outside the 3.8 to 4.8
      band every retained rung sits in.
  - id: BC-195
    purpose: tool_validation
    owner_focus: process
    instances: [11, 12, 17, 26]
    state: blocked
    priority: 3
    question: >-
      What did the efficiency work actually buy, which of Agenda 017's lessons are now
      enforced by a check rather than by a paragraph, and what is next?
    budget: >-
      60 elapsed minutes, review-planning-oversight. Classify every block with its stop
      reason, reconcile the benchmark records against the claims made from them, and
      confirm that the efficiency changes preserved every guard they were required to
      preserve -- retention through the gate, both routes agreeing on the value, the
      exhaustive tier still deciding what it decided.
      One question this closeout owns specifically: whether the exhaustive tier is still
      affordable. It held eleven marked nodes at the end of Agenda 017 and a single
      2097-atom certificate would add hours to it. D-438 was the same problem one tier
      down and it hid a real failure for hours.
    entry: >-
      BC-190 through BC-194 are terminal or explicitly stopped.
    exit: >-
      Per-block outcomes and stop reasons, a measured statement of what throughput
      changed, a decision on the exhaustive tier's budget, ranked candidates, and one
      selected next entry.
    bead: think-kibo
    workflows: [review-planning-oversight]
    depends_on: [BC-190, BC-191, BC-192, BC-193, BC-194]
    next_evidence: >-
      Whether the research bottleneck has moved off the decision path, which is what W5's
      contract says decides when it hands back to W6.
---
# Agenda 019 — Efficiency First: the Decision Path, the Retarget, and Two Deep Strategy Sessions

## Workflow Entry Point

This agenda is paused.
It becomes active when the operator has reviewed Agenda 017’s pull request and chosen
between this agenda and
[Agenda 018](agenda-018-ten-hour-continuation-ladders-theorems-and-wave-two.md), which
is also paused on the same review.

Begin at `BC-190` and `BC-191` together, on separate cores, both under
`efficiency-loop`. They are the only two commitments that start `ready`, and everything
else depends on at least one of them.
That ordering is the agenda’s whole argument.

## State at handoff

Written for whoever picks this up cold, so that nothing below has to be reconstructed
from the pull request.

**Retained and closed.** Seven registered cases carry a first-party weighted fractional
unavoidable-set certificate, and every one was decided twice from frozen bytes by two
methods that fail differently and agreed on the least covered mass to the digit.

| Case | Side | Result | `S` |
| --- | --- | --- | --- |
| `n = 11` | `381/100` | `T-018` | `S5` |
| `n = 12` | `99/25` | `T-017` | `S4` |
| `n = 17`, `18` | `459/100` | `T-019` | `S4` |
| `n = 19`, `20`, `21` | `24/5` | `T-020` | `S4` |

**Open, with the evidence already gathered.** Two sides were attacked and neither
settled, both stopped on cost rather than on an answer, and both are cheap to resume
because the checkpoints and the readings are in the record.

- `n = 18` at `117/25 = 4.68`. Three site sets, 538, 578 and 618 orbits, all returned a
  restricted optimum of exactly `18.000000`, the third after 157 row rounds and 7056 s.
  Adding sites can only lower a restricted optimum and it did not move.
  Either the covering value is at or above eighteen, or the optimum sits on a degenerate
  vertex. `T-019`’s `next_rung` carries both readings and the evidence for each.
- `n = 11` at `19/5 + 1/100 = 3.82`. Two independent site sets stop at exactly eleven,
  and the rejection route is far from closing: the exact maximum pointwise depth is
  `1925/1152`, which caps the feasible total at `1152/175` against the eleven a ceiling
  needs. `T-018`’s `next_rung` has the full account.

**Where the method stops, which is now proved rather than guessed.** No certificate for
`n` exists above `ceil(sqrt(n)) * B`. `n = 12` is foreclosed against its conjectured
`4`. `n = 20` and `n = 21` can be brought to within `0.0115` of their upper bound and no
nearer. `n = 11`, `17`, `18` and `19` are limited by their best known packings rather
than by the ceiling.

**What the next block must not skip.** `BC-191` first, and `BC-190` on its measured
premise rather than its original one.
When this agenda was drafted the retention gate was the dominant cost: one exact sweep
was `5378 s` at 2260 atoms and scaled as `atoms^2.00`. That was addressed the same
evening, before the agenda opened, as a W5 slice against that baseline: the sweep now
decides in `int64` on the weights’ common scale (every retained certificate’s weights
are multiples of `1/200000`, so the arithmetic is integer and exact), the reachable
cells are held as one span per column instead of sixteen million tuples, and the 181
directions run in parallel.
Measured on the same box, with the `Fraction` reference still running beside it:
`n = 17` in `21.8 s` against `1473 s`, `n = 20` in `38.7 s` against `5378 s` — `68×` and
`139×` — returning the declared least covered mass in both, with the `Fraction` route
retained unchanged as the reference and held to the integer route cell for cell on 181
directions of the 373-atom rung with no mismatch.
`BC-190`’s question — whether the generator’s inner loop should decide by the interval
route — is therefore no longer a question about the gate’s cost; it is a question about
the inner loop’s, and its entry baseline is now the integer sweep, not the `Fraction`
one. Do not point a run at a larger case before `BC-191` — the reach table says the
prizes are there, and the untuned-grid `8.8×` is the cost law that still stands.

## Why efficiency before bounds

Agenda 017 moved seven registered cases in a day.
It also spent its time like this, and the figures are from its own logs rather than from
recollection:

| Where the time went | Measured |
| --- | --- |
| Exact vs interval, 1184 atoms | `1473 s` against `65 s`, both timed in one run |
| Exact vs interval, 2097 atoms | `4866 s` against `110 s`, both timed in one run |
| Exact vs interval, 2260 atoms | `5378 s` against `173 s`, on a contended machine |
| Exact sweep after the W5 slice, 1184 atoms | `21.8 s`, same box, same verdict — `68×` |
| Exact sweep after the W5 slice, 2260 atoms | `38.7 s`, same box, same verdict — `139×` |
| Fitted exponent, exact sweep | `atoms^2.00` over the full 1184-to-2260 range — quadratic |
| Fitted exponent, interval route | `atoms^0.92` on the one uncontended pair — linear |
| Row generation, share of a round | `79%` to `94%` at every side measured |
| `n = 20` round 0, grids `(23, 31, 39)` | over `3300 s`, did not finish |
| `n = 20` round 0, grids `(29, 39, 49)` | `376 s` |
| Rationalisation loss at `n = 12`, side `99/25` | `0.005314`, against a surviving margin of `0.001040` |
| Load average, four lanes on four cores | `10.6` |

Three of those are not close calls.

The interval route decides **361 directions where the exact sweep decides 181**, needs
one fewer hypothesis — deciding on the doubled net it never invokes the `D4` reflection,
so it does not need `Condition 1` at all — and ran `22.7×` faster at 1184 atoms, `44.2×`
at 2097 and `31×` at 2260. The ratio widens because the two scale differently, quadratic
against linear, and the certificates are growing.
Read the 2260 pair with its caveat.
That certificate is `T-020`, decided after this agenda was drafted; its exact sweep had
the machine largely to itself and its interval run did not, so the `31×` understates the
gap and the exponent it implies for the interval route is not usable.
The exact side is the trustworthy half, and it holds: three points from 1184 to 2260
atoms fit `atoms^2.00`, so the retention gate’s cost is quadratic in the certificate and
the certificates are getting larger every rung.
The one figure to compare across runs is the box count, which is deterministic:
`3,683,951` at 1184 atoms, `4,448,751` at 2097, `5,638,343` at 2260. The exact sweep
belongs at the retention gate, where correctness is the only thing that matters and an
hour is affordable.
Whether it belongs in the generator’s inner loop is a question nobody
has asked, and `BC-190` asks it.

The site grids do not scale with the container.
`build_site_grid` places a fixed *count* of points across the side, so at `4.80` the
coarsest grid spaces sites `0.126` apart against `0.104` at `3.96` — 21% sparser
relative to the `B`-square that has to cover them.
One parameter change bought at least `8.8×` on a single round, and it was found by
accident while diagnosing a run that appeared wedged.

The rationalisation scale nearly cost a rung.
At `n = 12`, side `99/25`, the rounding loss was five times the margin the certificate
ended with.
Raising the scale twentyfold costs nothing measurable and does not change the
atom count.

## Why the retarget needs a strategy session and not a sort

`CERTIFICATE-REACH.md` ranks all 100 cases and puts eleven above `+0.49` against
`+0.0671` at `n = 11`. It would be easy to read that as a work queue.
It is not one, for two reasons the table itself states.

The prize column is what the **ceiling** allows.
The real limit is the covering value at that side, and exactly five restricted optima
have ever been measured.
They fit a quadratic; a fit is not a measurement, and no rung on this branch was ever
claimed from one.

And cost grows with the container.
The high-prize cases sit at sides `5.1` to `7.2` against the `3.8` to `4.8` band every
retained rung occupies.
A round at `4.8` cost up to `1158 s`; nobody has measured a round at `5.5`.

`BC-192` is the session that turns a ranking into a plan, and it runs *after* the two
efficiency commitments precisely so that it can price its candidates.
`BC-193` asks the harder question underneath: the ceiling is sharp and its mechanism is
four cheap steps, so what would a method that escapes it have to change?
A written argument that the ceiling is intrinsic is a real outcome and is recorded as
one.

## What does not change

Agenda 017’s discipline is the reason its results survived contact with four of its own
mistakes, and none of it is on the table here.

Retention still means freezing the candidate before deciding it, deciding the frozen
bytes through `devtools.decide_certificate`, and retaining only when both routes accept
**and agree on the value**. `BC-190` moves the exact sweep out of the generator’s inner
loop and not out of the gate; the equivalence guard is the whole correctness argument
and its absence is a reason to reject the change.

A candidate still counts only when its row loop stopped for want of a violated
placement, and the loop’s final least covered mass is still reported beside the
objective.

And rule seven still holds: read the evidence, not a reconstruction of it.
Every figure in this agenda is from a log or an artifact, and the one estimate — a round
at `5.5` — is labelled as an estimate and written down before the run so the run can
contradict it.

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
