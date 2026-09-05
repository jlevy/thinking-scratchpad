---
title: "agenda-021 — three numbers and a wall: the m = 5 ladder, the n = 11 endgame, and a priced rung"
softschema:
  contract: packing.squares:ExperimentAgenda/v1
  schema: ../schemas/agenda.schema.yaml
  envelope: agenda
  status: enforced
agenda:
  id: agenda-021
  title: "Three Numbers and a Wall — the m = 5 Ladder, the n = 11 Endgame, and a Priced Rung"
  updated: '2026-09-05'
  status: completed
  objective: >-
    X-014 ends with a verdict and a bill. The two mechanisms the owner asked about are
    real -- a certificate that has stopped proving infeasibility still constrains the
    packings that survive it, and the sliver below Trump's value is a computable box --
    and the size of the tree between them is set by three numbers nobody has measured:
    where the covering value crosses eleven, how large the tight-core set is there, and
    how large the isolation radius is at Trump's pose. Two of the three are an
    afternoon's computation each. This block buys all three, and a fourth the ladder
    itself needs.
    The fourth is where the m = 5 ladder stops. n = 20 and n = 21 sit at 24/5 with the
    method's ceiling at 5B = 4.9885 and the trivial grid as their only upper bound, so
    they are the one place in the register where the instrument can be run to its own
    structural limit and the covering value is the only thing that could bind first.
    Four pre-registered rungs bisect that interval and bracket the wall to at most
    0.015. Nobody has ever measured a covering wall; two site sets stopping at exactly
    eleven at 3.82 is the closest the record comes, and T-018 says plainly that reading
    it as tau* would be reading an artefact.
    Three lanes run concurrently on three cores. Lane A opens with a zero-build run of the generator at n = 13 -- the calibration
    X-015's stepping-stone pricing puts first, because the covering value extrapolated
    to the ceiling there sits below thirteen and its answer reorders block two -- then
    climbs the m = 5 ladder, reading the n = 21 criterion at every rung and one rung
    near the ceiling on it first, then builds the class-certificate instrument that
    X-014's Lemma 3 needs, which is a threshold change and nothing geometric. Lane B measures the two n = 11 endgame
    numbers -- the isolation radius at Trump's pose, and the covering value from below by
    an exact-depth fractional packing -- and then reads the near-tight census off a mass
    grid the sweep already fills. Lane C is the background: agenda-019's BC-191, taken as
    registered, and then the first covering-value point outside the 3.82-to-4.80 band.
    The research wall is 450 elapsed minutes with the closeout at 390. Nothing in this
    block promotes a bound except through the retention gate exactly as it stands.
  items:
  - id: BC-197
    purpose: research
    owner_focus: correctness
    instances: [19, 20, 21]
    state: complete
    priority: 0
    question: >-
      Where does the restricted covering optimum at m = 5 reach twenty, and does it reach
      twenty-one below the ceiling at all? That is, how far above the retained 24/5 can
      the ladder climb toward 5B = 4.9885 before no site set yields a total mass below
      twenty -- and, since a rung's optimum M certifies every n > M, whether a rung near
      the ceiling still certifies n = 21 -- and is each wall the covering value's or the
      method's?
    hypotheses: [H-062]
    budget: >-
      200 elapsed minutes, Fable at maximum thinking, research-loop, on lane core 1 after
      BC-211. The first rung is not part of the bisection: 997/200 = 4.985, 0.0035 below the
      ceiling, read on the n = 21 criterion (mass below twenty-one). X-015's
      stepping-stone pricing extrapolates the covering value at the ceiling to 20.4 to
      20.7 by the same finite differences used below, so the n = 21 wall is expected
      above the ceiling rather than below it; a converged optimum below twenty-one at
      4.985 is a certificate s(21) >= 4.985, the first proved member of the k = 4 family
      within 0.015 of its grid value, and a converged optimum at or above twenty-one on
      two independent site sets puts both walls below 4.985 before the bisection starts.
      Every later rung reports its optimum M and the n = 21 reading beside the n = 20
      one. The bisection's sides are pre-registered before any command runs and the
      schedule is a deterministic bisection of [24/5, 9977/2000] whose midpoints are rounded to the
      nearest 1/200 with ties taken away from 24/5. Rung 1 is 979/200 = 4.895. If it
      yields a certificate the bracket rises to [4.895, 4.9885] and rung 2 is
      247/50 = 4.94; if it walls, the bracket falls to [24/5, 4.895] and rung 2 is
      97/20 = 4.85. The third level is 993/200 = 4.965, 123/25 = 4.92, 39/8 = 4.875 and
      193/40 = 4.825, and the fourth is the live bracket's midpoint by the same rule.
      Every leaf of that tree leaves a bracket of at most 0.015, which is what H-062
      registers against 0.02. The four rungs are fixed by the rule, not chosen after a
      reading.
      The cost model is recorded before the run and not after. At 24/5 a tuned round cost
      500 to 1158 s and the run was halted at round 9 on a restricted optimum of
      18.916941; the retained certificate's total is 946131/50000 = 18.922620. From
      X-013's own finite differences across the six reported optima -- about 7.1 mass per
      unit side from 3.82 to 3.96, 8.0 to 4.58, at most 8.9 to 4.80 -- the 1.077 of mass
      between 18.9226 and twenty is 0.12 to 0.135 of side, so the wall is estimated at
      4.92 to 4.94. That estimate is written down so the run can contradict it.
      What makes four rungs affordable inside 180 minutes is an asymmetry, and the budget
      is split on it. Adding rows can only raise a restricted optimum, so a rung is
      refuted as soon as its optimum crosses twenty with violated placements still
      outstanding, and that answer arrives early: 20 minutes. A rung is confirmed only by
      convergence -- the row loop stopping for want of a violated placement -- and then a
      freeze and the gate: 60 minutes. A rung that has done neither at its cap is
      time-limited, its checkpoint carries, and the bracket is reported at whatever width
      the decided rungs support.
      Two readings are refused in advance. A converged optimum at or above twenty on one
      site set says only that no certificate exists on that site set, because adding
      sites can only lower a restricted optimum; a wall claim needs two independent site
      sets, which is the T-018 pattern. And an exactly round value -- 20.000000 -- is the
      known artefact signature in this pipeline, as at n = 17's grid-31 optima and the
      n = 18 run at 117/25, so it is inconclusive and not a wall.
      One soundness alarm, checked at every rung above 4.885618. Wainwright's n = 19
      packing sits there, so a converged optimum below nineteen at a higher side would
      contradict a retained packing and is a bug to chase rather than a rung to bank.
      Every rung above that side must land in [19, 21), and a rung the n = 20 reading
      refutes may still be an n = 21 certificate.
    entry: >-
      BC-211 is terminal (time-limited, continuing under its own bead) so the lane core
      is free; T-020 is retained at 24/5 with total 946131/50000; ceiling_side gives 5B = 4.9885
      for n = 20 and n = 21, the reach table's packing cap coincides with it there
      because the grid packing is axis-parallel and every tilt offset is zero, so one
      number is both structural limits; devtools.decide_certificate is the retention gate
      and the integer sweep is its cost baseline at 38.7 s on 2260 atoms; the bisection
      schedule above is fixed.
    exit: >-
      Per rung, one of three: a retained certificate with both routes accepting the
      frozen bytes and agreeing on the value; a refuted rung with its restricted optimum,
      the round at which it crossed twenty, and whether the row loop had converged; or a
      time-limited rung with its checkpoint. Plus the bracket the decided rungs support,
      the measured cost per round at each side against the model above, the 4.985 rung's
      n = 21 verdict, and an explicit statement of whether each wall found is the
      covering value's or the ceiling's.
    bead: think-g73w
    workflows: [research-loop]
    depends_on: []
    parallel_group: agenda021-lane-a
    program: grid-frontier-exact-values
    artifacts:
    - packing/cases/n20_fractional_certificate/certificate.json
    - packing/cases/n20_fractional_certificate/certificate-193-40.json
    - packing/campaign/series/series-000-smoke-and-calibration/experiments/exp-061-h-062-m5-covering-wall.md
    - packing/campaign/series/series-000-smoke-and-calibration/results/bc-197-ladder-register.txt
    - packing/campaign/series/series-000-smoke-and-calibration/results/bc-197-r2t.json
    - packing/campaign/series/series-000-smoke-and-calibration/results/bc-197-r3.json
    - packing/devtools/declare_least_cell_mass.py
    outcomes:
    - scope: >-
        The m = 5 ladder: one rung at 997/200 read on the n = 21 criterion, then the
        pre-registered bisection of [24/5, 9977/2000] for the n = 20 wall, two site sets
        per rung, inside a 200-minute lane budget on one core.
      classification: achieved
      result: >-
        Five sides decided and a bound moved. The certificate is at 97/20 = 4.85, total
        mass 19848723/1000000 over 1680 atoms, retained through the gate on both routes
        at 200001/200000 and registered as T-021: s(20) >= 97/20 and s(21) >= 97/20, up
        from T-020's 24/5, with n = 19 left where it was because the mass sits above
        nineteen. A second certificate at 193/40 (19.862092 converged, 1076 atoms) is
        retained as a lower rung. The rungs at 39/8, 979/200 and 997/200 crossed their
        threshold on both constructions and wall, so the covering wall lies in
        [97/20, 39/8], width 0.025 against the 0.02 H-062 registered: the hypothesis is
        unresolved and one rung short, and exp-061 records the round. The cell's own exit is met at
        every rung, so it retires; the rung H-062 still wants is BC-213's, which this
        block's closeout selects.
        Two findings beyond the rungs. The 4.85 rung is the seeded construction's, not
        the grid's -- the uniform grid crossed twenty at round 31 of 32 by four parts in
        ten thousand at the very side where the previous rung's atoms, scaled, converged
        below it -- which is the reason H-062 asks for two constructions before a
        crossing reads as a wall. And the exactly round 25.000000 at 997/200 has a
        mechanism rather than a mystery: with 5B - L = 0.0035 the twenty-five
        axis-parallel B-squares overlap only in strips of that width, the restricted dual
        is checked at sites only, and no uniform inset-1/2 grid the lane could afford
        puts a site in every strip, so twenty-five unit weights are dual-feasible
        whatever the covering value is.
      evidence:
      - packing/frontier/results.yaml T-021
      - packing/campaign/series/series-000-smoke-and-calibration/experiments/exp-061-h-062-m5-covering-wall.md
      - 'devtools.decide_certificate on the frozen bytes: RETAINABLE at 200001/200000, sha256 445935cc...'
      - session-086 Lane A delegation, 88 agent-minutes of the 200 budgeted
      disposition: retire-success
      follow_up: null
    next_evidence: >-
      The first measurement of a covering wall above a retained rung, which BC-203's
      first doubling-down rule reads directly and which decides whether block two spends
      its leads on the endgame or on more rungs.
  - id: BC-198
    purpose: tool_validation
    owner_focus: correctness
    instances: [11, 12]
    state: complete
    priority: 1
    question: >-
      Does the two-threshold form of Condition 5 -- per-direction-class thresholds as LP
      variables, classes as unions of the net's half-gap cells -- reproduce the two
      restricted-orientation facts the literature already carries, and what does one
      class LP cost?
    hypotheses: [H-063]
    budget: >-
      110 elapsed minutes, Fable at maximum thinking, pipeline-improvement then
      research-loop, on lane core 1 after BC-197.
      The change is a threshold change and nothing geometric. X-014's Lemma 3 adds two
      variables w0 and w1 and one normalisation row to the covering program, with class
      membership decided by which half-gap cell holds a direction and the composition
      refuted by the sign of M - n0 w0 - n1 w1. The admissible centre domain does not
      move, so sweep.centre_domain, the float mirror in generate.py and the four
      half-planes interval.DirectionSearch propagates are all untouched; generalising
      those to a non-convex domain is block two's BC-204 and is not attempted here.
      The net is read from cases/n11_fractional_certificate/certificate.json and not from
      memory: angle_limit 207107/500000, direction_steps 180, so 181 directions over an
      arc of 0 to 45.000043 degrees with spacing 0.263696 degrees at the axis-parallel
      end, B = 9977/10000, D = 207107/90000000 and B(1 + D) = 0.999996. The half-gap
      cells are the arcs between consecutive midpoints.
      0--40 build the program and its two class constructors. 40--75 control one, the
      nine-point bound. At side 3877/1000 the largest near-axis class inside
      theta0 -- cos theta + sin theta = 4B/s, giving 1.706162 degrees -- is the first six
      cells, upper boundary 1.450253 degrees. Nine atoms of unit weight on the pitch-s/4
      grid are feasible for that class program at w0 = 1, so its optimum must be at most
      nine; nine below eleven closes the composition n1 = 0, and an optimum above nine is
      an instrument defect and not a result. 75--105 control two, Stromquist. The class
      of the two end cells -- around 0 and 45 degrees, half-width 0.131848 degrees at the
      axis end -- must refute the composition (n0, n1) = (11, 0) at a side at or above
      Trump's 3.877084. Stromquist's Theorem 3 reaches 2 + (4/3)sqrt(2) = 3.885618 for
      the exact two-direction class by a further box step this program does not have, so
      3.877084 is the threshold and 3.885618 is not. 105--110 record the per-LP cost,
      which is what prices twelve compositions in block two.
      Floats propose and exact arithmetic confirms, throughout, and no class certificate
      is retained in this cell: devtools.decide_certificate decides a five-condition
      Certificate and does not yet decide a two-threshold object, so registering a class
      theorem waits for BC-208 and the gate work named there.
      Kill: the near-axis class program returning above nine at 3877/1000, or either
      control disagreeing between the float proposal and the exact confirmation.
    entry: >-
      BC-197 is terminal so the lane knows what an LP costs under this block's core
      budget; X-014's Lemma 3 and its proof are in the record; the retained n = 11 net
      and shrink are frozen.
    exit: >-
      A frozen class-certificate program with both controls run and their verdicts
      recorded as numbers, the cost of one class LP at n = 11, and a written statement of
      what the program cannot decide, or the first typed stop naming which control
      refused and the figure that refused it.
    bead: think-m3sx
    workflows: [pipeline-improvement, research-loop]
    depends_on: [BC-197]
    parallel_group: agenda021-lane-a
    program: n11-closure
    outcomes:
    - scope: >-
        The two-threshold class-certificate program and its two controls, the third cell
        of Lane A.
      classification: never-opened
      result: >-
        Never opened. Lane A spent its budget on BC-211 and BC-197, and the pass's
        sub-agents were then ended by an account rate limit at 09:21 UTC, an external
        blocker rather than a decision; no command was run for this cell and nothing was
        built. Its entry condition -- a terminal BC-197 -- is now met, and the cell is
        unchanged and takeable.
      evidence:
      - session-086 stop reason and its Lane A delegation
      disposition: defer-dependency
      follow_up: think-m3sx
    - scope: >-
        The two-threshold class-certificate program and its two controls, opened in
        session-087 once BC-197 was terminal.
      classification: achieved
      result: >-
        Built and both controls run. classcert.py partitions the net's half-gap cells into
        classes with boundaries as exact tangents, adds w0 and w1 as LP variables under one
        normalisation row, and decides the object exactly on the event-cell sweep; nothing
        geometric moved, so the non-convex domain stays BC-204's.
        Control one passes exactly: the near-axis class at 3877/1000 gives 9.000000 in
        floats and exactly 9 in exact arithmetic from nine unit atoms, and the lane closed
        the bound from below as well, so it is exactly nine rather than at most nine. The
        instrument-defect clause does not fire.
        Control two refuses, and the refusal is proved rather than observed. At Trump's
        3.877084 the two-end-cell class gives 11885/1024 = 11.606445 against the eleven a
        refutation needs, and six independent site sets never go below 11.6 -- but the
        figure that settles it mentions no site set: L/B = 969271/249425 = 3.886021850
        exceeds 2 + (4/3)sqrt(2) = 3.885618083, so eleven pairwise disjoint B-squares fit
        and no measure of mass below eleven can cover them. The control's ceiling is
        B(2 + (4/3)sqrt(2)) = 3.876681, 0.000403 below the side it was asked to reach: the
        shrink costs 0.008937 of side against Stromquist's 0.008534 of headroom. It was
        unreachable before the first command ran. H-063 is rejected on its own kill
        condition, that conditioning on direction buys too little.
        What conditioning does buy is measured rather than dismissed: two thresholds
        separate once the site set is fine enough (w0 = 0.093383 against w1 = 0.079777 at
        composition (9, 2)), and X-014's step-1 design point is reachable -- (11, 0) over
        the leading nineteen cells at Trump's side, grid 79, exact 39123/4096 = 9.551514,
        margin -5933/4096, refuted.
        The price, which is what the cell existed to produce: one class LP is 14.4 ms at 78
        orbits and 49.4 ms at 210; a whole class program over 181 directions to convergence
        is 8.57 s at grid 23 and 27.66 s at grid 39, so twelve compositions price at about
        5.5 minutes of one core. The LP is under two per cent of it -- separation is what a
        composition sweep buys, which is the number BC-208 needs.
        Nothing was retained: decide_certificate decides a five-condition Certificate and
        not a two-threshold object.
      evidence:
      - packing/campaign/series/series-000-smoke-and-calibration/experiments/exp-064-h-063-two-threshold-class-program.md
      - packing/campaign/series/series-000-smoke-and-calibration/results/bc-198-class-program-register.txt
      disposition: retire-success
      follow_up: null
    artifacts:
    - packing/src/sqpack/fractional/classcert.py
    - packing/devtools/run_class_program.py
    - packing/tests/test_fractional_classcert.py
    - packing/campaign/series/series-000-smoke-and-calibration/experiments/exp-064-h-063-two-threshold-class-program.md
    - packing/campaign/series/series-000-smoke-and-calibration/results/bc-198-class-program-register.txt
    next_evidence: >-
      Whether conditioning on direction buys anything at all, which is the premise
      BC-208's two class theorems in block two rest on entirely.
  - id: BC-211
    purpose: measurement_validation
    owner_focus: correctness
    instances: [13]
    state: stopped
    priority: 0
    question: >-
      Does the existing generator, run unchanged at n = 13 and side 399/100, converge to a
      restricted covering optimum below thirteen -- so that one unconditional certificate
      reaches within 0.0092 of Bentz's s(13) = 4 and the grid-frontier endgame at m = 4 is
      a single certificate's shrink tax rather than a tree?
    budget: >-
      70 elapsed minutes, Opus at maximum thinking, research-loop, on lane core 1, first
      in the lane. Numbered after agendas 021 and 022 were drafted: it was added on the
      stepping-stone pricing X-015 records, which read Bentz's two proofs in X-014's terms
      and found that the covering value extrapolated to the ceiling 4B = 3.9908 sits near
      12.06 to 12.24 -- an extrapolation from the finite differences over the reported
      optima, labelled as one -- while a certificate needs mass below thirteen. Nothing is
      built: the side is the one X-014's sixth measurement and agenda-018's BC-173 already
      name, 399/100 = 3.99, 0.0008 below the ceiling, and the run is the column generator
      as retained, with the site density BC-191 has by then priced or, if BC-191 has not
      landed, the grid density T-017's 99/25 rung used.
      0--50 the run to convergence, refutation early if the optimum crosses thirteen with
      violated placements outstanding. 50--65 freeze and the gate on a passing run:
      devtools.decide_certificate on frozen bytes, both routes agreeing. 65--70 the
      record, with the converged mass beside the estimate whichever way it fell.
      Two readings are fixed in advance. A converged optimum below thirteen is a
      certificate s(13) >= 399/100, a calibration against a known answer -- S3 at most,
      the theorem being Bentz's -- and it fires BC-203's fourth rule. A converged optimum
      at or above thirteen on two independent site sets says the m = 4 covering wall sits
      below 3.99, the same shape as n = 12's, and the endgame at m = 4 is a tree; one site
      set says only what one site set says, as in H-062.
      Kill: a round costing more than 25 minutes at 3.99 -- the comparison is n = 12's
      2097-atom rung at 99/25 -- in which case the run stops time-limited with its
      checkpoint and BC-203 records the price.
    entry: >-
      Lane core 1 is free at dispatch; T-017's 99/25 rung and its site density are
      retained as the comparison; the estimate above is written down.
    exit: >-
      A converged restricted optimum at 399/100 with the loop's final least covered mass,
      the cost per round against n = 12's, and either a retained certificate or the
      two-site-set refutation; or a time-limited stop with its checkpoint.
    bead: think-2ib0
    workflows: [research-loop]
    depends_on: []
    parallel_group: agenda021-lane-a
    program: grid-frontier-exact-values
    artifacts:
    - packing/campaign/series/series-000-smoke-and-calibration/results/bc-211-run-a-n13-399-100.json
    - packing/campaign/series/series-000-smoke-and-calibration/results/bc-211-run-a-n13-399-100.log
    - packing/campaign/series/series-000-smoke-and-calibration/results/bc-211-run-c-control-n12-99-25.json
    - packing/campaign/series/series-000-smoke-and-calibration/results/bc-211-run-c-control-n12-99-25.log
    - packing/devtools/run_fractional_colgen.py
    outcomes:
    - scope: >-
        The generator unchanged at n = 13, side 399/100, inside a 70-minute lane budget
        on one core, with the n = 12 control at 99/25 the cell's reading rule requires.
      classification: time-limited
      result: >-
        Neither of the cell's two readings was earned: no run at 399/100 converged, so
        there is no restricted optimum there and nothing was frozen. Run A (grids
        23, 31, 38 from the density rule as it stood mid-lane; 2921 sites, 400 orbits)
        hit the 60-round limit at objective 16.000000 with least covered mass 0.929161
        -- not an optimum, and the round number the handoff names as the artefact
        signature; 7.72 s per row round against 3.04 s at n = 12's 99/25 with the same
        seed. Runs B (grids 23, 31, 39, 300: 92989 sites, 11742 orbits) and D (grids
        23, 31, 39, 100) each spent their whole budget inside one un-logged round,
        which fired the cell's 25-minute kill; generate_adaptive writes nothing until
        a column round returns, so both stops left no table and no resumable state.
        The control decides what the readings may mean: at n = 12's own retained side
        99/25 the same seed converged to 12.312896 above twelve, where the retained
        certificate carries 149987/12500 = 11.998960 on atoms that lie on grids
        (23, 31, 39, 297) plus seven column additions -- a seed that cannot reproduce
        a retained rung cannot refute one, so run A does not read as "the m = 4 wall
        sits below 3.99". The price is recorded: at the density the retained rungs
        used, one round at 399/100 costs more than the 25 minutes the cell allows.
      evidence:
      - packing/campaign/series/series-000-smoke-and-calibration/results/bc-211-run-a-n13-399-100.json
      - packing/campaign/series/series-000-smoke-and-calibration/results/bc-211-run-c-control-n12-99-25.json
      - session-086 Lane A delegation, 3982 s platform-measured, 66 of 70 budgeted minutes plus the close-out
      disposition: continue
      follow_up: think-2ib0
    next_evidence: >-
      Whether the first exact grid value by machine is one certificate away, which
      BC-203's fourth rule reads directly and which decides whether block two opens the
      B = 1 route (BC-212) ahead of the conditional route.
  - id: BC-199
    purpose: research
    owner_focus: insight
    instances: [11]
    state: complete
    priority: 0
    question: >-
      What explicit isolation radius and quadratic constant follow from exp-013's 128
      branch certificates at Trump's pose, and is the radius large enough for any tree to
      reach?
    hypotheses: [H-022]
    budget: >-
      120 elapsed minutes, Fable at maximum thinking, research-loop, on lane core 2. This
      is X-014's second measurement and the first half of agenda-018's BC-176; it
      produces the two numbers and not the packet.
      0--35 the modulus. For each of the 128 derivative-distinct 42 x 33 matrices
      exp-013 retains -- 512 raw feature selections reducing to 128, every one of exact
      rank 33 with a strictly positive stress and A-transpose lambda zero -- compute
      kappa_b = min over sup-norm-one v of max_j -(A_b v)_j by 66 small linear programs
      per branch, one per face of the unit cube in the 33 pose variables, floats
      proposing and exact arithmetic confirming, which is the pattern
      cases/trump11/tangent_cones.py already uses.
      35--70 the curvature and the gaps. Every active constraint is a corner coordinate
      against a wall or a corner of one square against an edge of another, so each is a
      polynomial in the centres and in cos and sin of the angles; bound the sum of
      absolute second derivatives on a declared box by coefficient sums to get K, and
      record the least nonzero gap at the pose and a Lipschitz constant of the gaps.
      70--95 the two constants. rho_0 = min over branches of 2 kappa_b / K, capped by the
      gap-to-Lipschitz radius and by half the distance to the nearest distinct D4 image
      or relabelling; C = max over branches of the one-norm of lambda_b times K over
      twice the far-wall stress Lambda_b. The ratio one-norm-over-Lambda may be minimised
      over each branch's stress cone by a further LP, which the retained stresses were
      not chosen for, and whether that is worth the minutes is a decision this cell
      records either way.
      95--120 the claim boundary, written before anything is quoted elsewhere: a lower
      bound on the chart-distance radius in the named anchored chart at fixed side, with
      the side-stability clause; no optimality, no uniqueness, no global statement, and
      nothing about a different arrangement -- Trump's own 2023 note scopes every local
      result here to the same geometrical arrangement of the unit squares.
      Kill: rho_0 below 1e-6 in the chart. X-014 reads that outcome as the local box
      being too small for any tree to reach; acting on that reading is BC-203's, not this
      cell's.
      This cell registers no result and moves no frontier property. H-022 moves on
      BC-176's packet and BC-177's review in agenda-018, neither of which is in this
      block.
    entry: >-
      exp-013's 128 branch certificates and cases/trump11 are frozen by hash; the exact
      field is in the record; X-014's derivation of the modulus and stress lemmas is
      written out with its two cautions.
    exit: >-
      An exact rational lower bound for rho_0 and an exact upper bound for C, with the
      per-branch kappa_b and stress-ratio tables retained, or the first typed proof gap,
      guard refusal or time-limited stop naming what refused.
    bead: think-ljvz
    workflows: [research-loop]
    depends_on: []
    parallel_group: agenda021-lane-b
    program: n11-closure
    artifacts:
    - packing/cases/trump11/isolation_radius.py
    - packing/tests/test_trump_isolation_radius.py
    - packing/campaign/series/series-000-smoke-and-calibration/results/bc-199-trump-isolation-radius.json
    outcomes:
    - scope: >-
        The isolation radius and the quadratic stress constant at Trump's pose, in the
        anchored centre-angle chart at fixed side, from exp-013's 128 branch
        certificates; the numbers, not the packet.
      classification: achieved
      result: >-
        rho_0 >= 288616983/125000000000 = 0.0023089 with the uniform curvature bound
        K = 4972105219/500000000 = 9.944210 on the declared box of sup-radius 1/64, the
        binding cap being the modulus 2 kappa_b / K itself (the per-feature gap cap is
        0.0058755, the symmetry cap 1/16, the box 1/64); with per-row curvature the same
        derivation gives rho_0 >= 808514697/200000000000 = 0.0040426. C <= 22.467763
        with the uniform K and <= 12.873063 per row. kappa_b takes exactly two values,
        0.011480272 on 64 branches and 0.016423845 on the other 64, decided by which
        option of contact (9, 10) the branch takes, with the minimising face theta_10
        = +-1 in every branch. The stress ratio ||lambda_b||_1 / Lambda_b = 4.518763 is
        the same in all 128 branches by an exact identity (1 - rho e_far lies in every
        row space), so the ratio-minimising LP X-014 proposed is empty. The kill
        (rho_0 below 1e-6) did not fire. Four corrections to X-014's sketch are recorded
        in the tool: the g_min/Lip cap is far too weak and is replaced by a per-feature
        cap; the stress bound needs lambda >= 0 and Lambda > 0 rather than strict
        positivity; the ratio LP is empty; K is a supremum over a box that must be
        declared first. Every branch row was matched exactly to the gradient of a tied
        elementary function, so the chart is exp-013's. No result is registered: the
        theorem form is agenda-018's BC-176 and its review BC-177.
      evidence:
      - packing/cases/trump11/isolation_radius.py
      - packing/tests/test_trump_isolation_radius.py (6 tests, 6.9 s)
      - packing/campaign/series/series-000-smoke-and-calibration/results/bc-199-trump-isolation-radius.json (sha256 db124b99...; three independent runs agree)
      - session-086 Lane B delegation, 3107 s platform-measured, 51 of 120 budgeted minutes
      disposition: retire-success
      follow_up: null
    next_evidence: >-
      Whether the local box is reachable by any tree, which BC-203's third doubling-down
      rule reads directly and which decides whether block two opens a conditional lead
      against Trump's pose at all.
  - id: BC-200
    purpose: measurement_validation
    owner_focus: correctness
    instances: [11]
    state: complete
    priority: 1
    question: >-
      Is the covering value at n = 11 already at or above eleven at 3.82 and at 3.85,
      measured from below by an exact-depth fractional packing rather than inferred from
      a search that stopped?
    hypotheses: [H-064]
    budget: >-
      110 elapsed minutes, Fable at maximum thinking, research-loop, on lane core 2 after
      BC-199. This is X-014's first measurement, and X-014 says of it that nothing kills
      the idea: either outcome sets the ladder's top and the tree's working side.
      The object is a finite list of closed B-square placements at net directions with
      non-negative rational weights whose depth is at most one at every vertex of the
      arrangement of their edges and the container boundary, which is exactly what
      sqpack.fractional.ceiling decides. Its total weight is a lower bound on the
      fractional packing value, which weak duality puts below the covering value, so a
      total at or above eleven forecloses the ladder at that side and -- both values
      being monotone in the side -- at every larger one.
      The starting point is in the record and is not enough on its own. At 3.82 the
      converged dual is 76 squares, 608 after the D4 images, raw total exactly eleven;
      ceiling.py checked all 1650944 vertices of their arrangement, 272244 of them in
      exact arithmetic, and found a maximum pointwise depth of 1925/1152 = 1.671007, so
      the depth-scaled total is 1152/175 = 6.5829 against the eleven a ceiling needs.
      Column generation had priced against a grid sample and reported 12/11 = 1.0909,
      which would have given 121/12 = 10.08; the exact maximum is 53 per cent higher
      because depth peaks at vertices no grid samples. A ceiling is judged on the exact
      check and never on the sampled depth.
      0--60 the loop at 191/50 = 3.82: add the violating arrangement vertices as depth
      constraints and re-solve, which is the column generator's site loop run in the
      other direction with ceiling.maximum_depth as the separation oracle and
      scaled_to_unit_depth for the scaling. 60--105 the same at 77/20 = 3.85, warm-started
      from 3.82's family. 105--110 the record.
      Readings, fixed here. A total at or above eleven at 3.85 confirms H-064 and puts
      the ladder's top below 3.85. A retained certificate at 3.85 with mass below eleven
      rejects it, and is a rung rather than a failure. A loop that stalls below eleven is
      a bounded negative for the cutting-plane loop and decides nothing about the
      covering value, because a lower bound that fails to reach a threshold is not an
      upper bound.
      Retention: a ceiling joins the record only when verify_ceiling accepts frozen bytes
      with every arrangement vertex checked exactly. Kill: the vertex count passing what
      the exact check can carry inside this cell's wall, in which case record the count
      and the last exact depth.
    entry: >-
      BC-199 is terminal so the lane core is free; T-018's next_rung carries the 3.82
      dual and its exact depth; sqpack.fractional.ceiling with maximum_depth,
      verify_ceiling and scaled_to_unit_depth is retained and green.
    exit: >-
      For each of 191/50 and 77/20, an exact depth-scaled total with its arrangement
      vertex count and its exact maximum depth, or the loop's last value with the reason
      it stopped; and an explicit statement of where the n = 11 ladder's top now sits.
    bead: think-1qjs
    workflows: [research-loop]
    depends_on: [BC-199]
    parallel_group: agenda021-lane-b
    program: n11-closure
    artifacts:
    - packing/campaign/series/series-000-smoke-and-calibration/experiments/exp-060-h-064-n11-fractional-packing-floor.md
    - packing/campaign/series/series-000-smoke-and-calibration/results/bc-200-family-191-50.json
    - packing/campaign/series/series-000-smoke-and-calibration/results/bc-200-family-77-20.json
    - packing/campaign/series/series-000-smoke-and-calibration/results/bc-200-summary-191-50.json
    - packing/campaign/series/series-000-smoke-and-calibration/results/bc-200-summary-77-20.json
    - packing/campaign/series/series-000-smoke-and-calibration/results/bc-200-state-191-50.json
    - packing/src/sqpack/fractional/cutting.py
    - packing/devtools/run_fractional_cutting.py
    outcomes:
    - scope: >-
        The n = 11 covering value measured from below at 191/50 and 77/20 by an
        exact-depth fractional packing, inside a 110-minute lane budget on one core.
      classification: achieved
      result: >-
        The exit was met and the hypothesis is unresolved in its own words. At 191/50
        nine iterations raised the exact depth-scaled total from the retained 1152/175
        = 6.5829 to 9.907906 (2,769,100 arrangement vertices, exact maximum depth
        1.115838 before scaling), and the row loop converged at iteration 5 to a
        restricted optimum of 11.055617 on 12,761 sites, so 9.907906 <= nu*(3.82) <=
        tau*(3.82) <= 11.055617. At 77/20, warm-started, three iterations reached
        9.049861 (2,419,348 vertices, depth 1.243643) and the row loop did not converge.
        Neither family reached eleven, so nothing was frozen under the case package;
        both loops stopped on the cell's wall with the exact check carrying every
        vertex. The n = 11 ladder's top is unchanged at 381/100 with 3.82 open, and the
        record now holds nu*(3.82) >= 9.907906 and nu*(3.85) >= 9.049861 exactly. The
        loop's bottleneck moved from separation to row generation as the site support
        grew, which a resumed run bounds.
      evidence:
      - packing/campaign/series/series-000-smoke-and-calibration/experiments/exp-060-h-064-n11-fractional-packing-floor.md
      - packing/campaign/series/series-000-smoke-and-calibration/results/bc-200-summary-191-50.json
      - packing/campaign/series/series-000-smoke-and-calibration/results/bc-200-summary-77-20.json
      - session-086 Lane B delegation, 5758 s platform-measured, 96 of 110 budgeted minutes
      disposition: retire-success
      follow_up: null
    next_evidence: >-
      The side every block-two n = 11 cell would have to work at, and BC-203's second
      doubling-down rule reads the 3.85 outcome directly.
  - id: BC-201
    purpose: tool_validation
    owner_focus: insight
    instances: [11]
    state: complete
    priority: 2
    question: >-
      How large is the near-tight set on the retained 381/100 certificate -- the reachable
      event cells whose covered mass is within a declared margin of one -- as a fraction
      of the reachable cells, per direction?
    hypotheses: [H-065]
    budget: >-
      60 elapsed minutes, Opus at maximum thinking, pipeline-improvement, on lane core 2
      after BC-200. This is X-014's third measurement, and it is a readout rather than a
      computation: the sweep already fills the mass grid before it takes the minimum, and
      reduce_to_spans already returns the reachable cells as one span per column.
      OR-1 applies and is the reason this is a cell at all. The output is
      devtools/census_tight_cells.py with a test, not a one-off script: per direction, the
      count of reachable cells with covered mass at most 1 + epsilon for epsilon in
      {0, 1/100, 1/20, 1/10}, the count of reachable cells, and the bounding box of the
      tight set in the rotated frame. The test pins the counts on a small synthetic
      certificate where they can be computed by hand and on one direction of the retained
      rung.
      The certificate is read from cases/n11_fractional_certificate/certificate.json:
      1121 atoms, outer side 381/100, B = 9977/10000, total mass 434547/40000 = 10.863675,
      least cell mass 4001/4000 = 1.00025.
      One bookkeeping point the record must carry, because it is easy to get backwards.
      On a retained certificate every reachable cell has mass at least one, so epsilon
      here is a census margin and not the mass gap M - 11, which at 381/100 is negative.
      The mass gap exists only at a side where a certificate fails, which is BC-200's
      business and not this cell's.
      The reading X-014 asks for: a tight set at epsilon = 1/20 that is a few hundred
      cells clustered around a few dozen positions makes Corollary 1a's exact cover a
      check; a fat one makes it a search, and a fat one is also what an integrality gap
      looks like from the inside, which is worth knowing either way.
    entry: >-
      BC-200 is terminal; sweep.reduce_to_spans and minimum_covered_mass_integer are
      unchanged and green; the retained certificate is frozen.
    exit: >-
      One devtool with a test, the per-direction census table at the four margins, and
      the fraction of reachable cells the epsilon = 1/20 set covers, summed over the 181
      directions.
    bead: think-614o
    workflows: [pipeline-improvement]
    depends_on: [BC-200]
    parallel_group: agenda021-lane-b
    program: n11-closure
    outcomes:
    - scope: >-
        The census of near-tight event cells on the retained 381/100 certificate at four
        margins, as a devtool with a test.
      classification: technical-failure
      result: >-
        Stopped by an external blocker with the tool half-built. The lane had read the
        sweep's mass grid and was refactoring it to expose the per-cell masses the census
        counts when the account's rate limit ended every sub-agent of the pass at 09:21
        UTC. The half-built devtools/census_tight_cells.py was then swept into a commit
        by a broad `git add -A packing/devtools`, which contradicted this outcome and put
        four errors in the type floor; it was removed on 2026-09-05, so nothing is
        retained here and H-065 is untouched. The refactor the cell needs did land on its
        own: sweep.MassGrid and scaled_mass_grid split the integer route's grid out as a
        value, so the seam a census reads through is in place. The cell is otherwise
        unchanged and takeable as written.
      evidence:
      - session-086 stop reason and its Lane B delegation
      disposition: fix-and-rerun
      follow_up: think-614o
    - scope: >-
        The same census, re-run in session-087 with the tool and its test built properly.
      classification: achieved
      result: >-
        Delivered in full: devtools/census_tight_cells.py with
        tests/test_census_tight_cells.py behind it, reading through the MassGrid and
        scaled_mass_grid seam so the census and the retention decision read the same
        int64 array, and the per-direction table at all four margins retained as
        bc-201-n11-tight-cell-census.json.
        Over 567,130,649 reachable cells in 181 directions, the epsilon = 1/20 tight set
        is 23,112,904 cells, a summed ratio of 0.040754 -- a fifth of the 0.20 H-065
        registered and an eighth of its 0.50 kill line, so the hypothesis is accepted.
        The census reproduces the certificate's own least_cell_mass, 4001/4000, as the
        minimum in every direction, and epsilon = 0 is empty everywhere, so Condition 5
        holds with a uniform margin of 1/4000 and epsilon is a band above a floor.
        The cell's own reading goes the other way and both are recorded. Corollary 1a's
        exact cover is a search, not a check: the median direction carries 78,016 tight
        cells against a bar of a few hundred, the set has positive area (7.596 per cent
        of the centre domain, 19.77 per cent in one direction, still 1.519 per cent at
        epsilon = 1/100), its bounding box equals the centre domain's own box in all 181
        directions at every non-empty margin, and its 22,132 components are extended
        regions of median about 554 cells rather than positions. That is what BC-207
        consumes and could not start without.
        The record says plainly what this is not: the census measures the LP solution's
        near-active set, not the integer optimum, so it is consistent with an integrality
        gap and is not evidence of one.
      evidence:
      - packing/campaign/series/series-000-smoke-and-calibration/experiments/exp-063-h-065-n11-near-tight-cell-census.md
      - packing/campaign/series/series-000-smoke-and-calibration/results/bc-201-n11-tight-cell-census.json
      disposition: retire-success
      follow_up: null
    artifacts:
    - packing/devtools/census_tight_cells.py
    - packing/tests/test_census_tight_cells.py
    - packing/campaign/series/series-000-smoke-and-calibration/experiments/exp-063-h-065-n11-near-tight-cell-census.md
    - packing/campaign/series/series-000-smoke-and-calibration/results/bc-201-n11-tight-cell-census.json
    next_evidence: >-
      Whether Corollary 1a's exact-cover step is a check or a search, which BC-207 in
      block two consumes directly and cannot start without.
  - id: BC-202
    purpose: research
    owner_focus: correctness
    instances: [26]
    state: stopped
    priority: 1
    question: >-
      With row generation finally priced against the container side, does a
      column-generation run at n = 26's predicted side reach a restricted optimum below
      twenty-six, and does a converged attainment ratio outside the 3.8-to-4.8 band still
      land in the 0.98171-to-0.98270 band the three retained certificates occupy?
    budget: >-
      170 elapsed minutes, Opus at maximum thinking, research-loop, on the background
      core, after agenda-019's BC-191.
      Lane C's first half is BC-191 itself, bead think-ji0r, taken exactly as registered
      in agenda-019. Its baselines, its three measurements and its exit are not restated
      here and must not be forked; what this agenda adds is a core for it and the rung it
      hands off to.
      The registered side is fixed before any command runs: 138/25 = 5.52, which is
      X-013's predicted 5.5218 rounded down to hundredths. The ceiling for n = 26 is
      6B = 5.9862 and the best known packing is 5.6213, so the packing binds first and
      5.52 leaves 0.1013 below it.
      The cost model is recorded before the run. At 24/5 a tuned round cost 500 to 1158 s;
      the area heuristic makes 5.52 about 1.32 times the atoms of 4.80, and that heuristic
      is itself loose -- atoms per side squared across the four retained certificates runs
      77.2, 133.7, 56.2 and 98.1, a 2.4-fold spread inside a side band 0.99 wide -- so a
      round is estimated at 660 to 1530 s before BC-191's changes, and the estimate is
      written down so the run can contradict it. The retention gate is no longer the cost:
      the integer sweep decided 2260 atoms in 38.7 s.
      The stop rule is not the wall alone, and this is the one place in the block where
      that differs. X-013's third proposal asks specifically for a converged seventh
      point, because a run halted on a clock measures where this project stops rather
      than where the method reaches; so a run that does not converge inside the budget is
      time-limited, its checkpoint carries to block two's BC-209, and its ratio is not
      reported as a ratio.
      If BC-191's pricing says a round at 5.52 costs more than this cell's wall, no run
      opens: the cell records the price and stops. That is a real outcome and it is what
      "if the pricing allows" means.
    entry: >-
      agenda-019's BC-191 is terminal with a site-density rule expressed as a function of
      the container side rather than a constant; the registered side and the cost model
      above are written down; the reach table's n = 26 row is current.
    exit: >-
      Either a retained certificate at 138/25 with both routes accepting the frozen bytes
      and agreeing on the value, or a measured negative with the restricted optimum
      reached, the loop's final least covered mass, the cost per round against the model,
      and whether the loop converged; and, only on a converged run, the attainment ratio
      against 5.6213.
    bead: think-r58z
    workflows: [research-loop]
    depends_on: [BC-191]
    parallel_group: agenda021-lane-c
    program: reach-table-ladder
    artifacts:
    - packing/devtools/colgen_checkpoint.py
    - packing/campaign/series/series-000-smoke-and-calibration/results/bc-202-n26-138-25.json
    outcomes:
    - scope: >-
        The n = 26 column-generation run at the registered side 138/25, carried toward
        convergence rather than a clock, on one core.
      classification: time-limited
      result: >-
        A measured negative at the side, and no ratio. Twenty-two column rounds and 137
        LP rounds over 7983 s brought the restricted optimum to 26.464317 with the row
        loop converged inside the last column round (least covered mass 1.000000) on
        8521 sites; the column loop had not converged -- it was still finding orbits of
        negative reduced cost, the last at averaged depth 1.0712 -- when the run stopped.
        Above twenty-six on this site set means no certificate here, and no more: adding
        sites can only lower a restricted optimum, so the number is an upper bound on the
        covering value and says nothing about whether a certificate exists at 138/25.
        X-013's third proposal asked for a converged seventh covering-value point and
        this is not one, so the attainment ratio is not reported.
        The cost is the reusable part. A cold column round cost 2130.6 s where the model
        priced 580 to 870, not because a round costs more than the law says -- over
        BC-191's own fitting window it cost 14.593 s against the law's 14.07 -- but
        because the cold row loop needed 58 rounds and their cost grows inside the loop;
        warm column rounds then averaged 244.7 s. The checkpoint is resumable and the
        resume path was exercised on the real artifact rather than only in a unit test.
        One thing the lane started and did not finish is deliberately not on the branch:
        a test asserting that a resumed leg which runs no round of its own reports an
        empty round list rather than the checkpoint's. The driver returns the
        checkpoint's, and changing that would change what the fields of this cell's
        already retained summary mean, so it is left to think-4in0 with the checkpoint
        it inherits.
      evidence:
      - packing/campaign/series/series-000-smoke-and-calibration/results/bc-202-n26-138-25.json
      - session-086 Lane C delegation
      disposition: continue
      follow_up: think-4in0
    next_evidence: >-
      The first covering-value point outside the 3.82-to-4.80 band, which is what X-013's
      third proposal asks for and what block two's reach-table rungs are priced against.
  - id: BC-203
    purpose: tool_validation
    owner_focus: process
    instances: [11, 20, 21, 26]
    state: complete
    priority: 2
    question: >-
      What did the three lanes measure, and which two of block two's three leads does
      that buy?
    budget: >-
      60 elapsed minutes from minute 390, review-planning-oversight, coordinator only.
      OR-11's four steps run without waiting for an operator: every item terminal with an
      outcome at its smallest honest scope, a stop-reason classification, evidence, a
      disposition and a named follow-up where one remains; generated views refreshed and
      the root documents each given an explicit update-or-current decision; live tbd
      status and priority reconciled with ranked candidates; and exactly one next entry
      selected and published without being executed here.
      The doubling-down rules are stated now, before the block opens, so the closeout
      reads them rather than argues them. They are conditions on measured outcomes and
      each names the allocation it forces.
      Rule one, the ladder. If BC-197's wall at m = 5 lands within 0.02 of five -- a
      converged restricted optimum at or above twenty on two independent site sets at a
      side of 4.98 or higher, or no wall found anywhere below 5B -- then the covering
      value never binds before the ceiling does at m = 5, the ladder has nothing left
      there, and block two blocks two of its three leads with the endgame: BC-204's
      conditional-certificate instrument and BC-205's n = 13 calibration, with BC-206
      carrying the n = 21 continuation above the n = 20 wall as its second leg.
      Rule two, the n = 11 ladder. If BC-200 finds the covering value below eleven at
      3.85 -- which is H-064's rejection reading, a retained certificate at 77/20 with
      mass below eleven -- then the ladder is not blocked where X-014 assumed, the
      cheapest remaining movement of the smallest open case is more rungs, and block two
      blocks two leads on climbing n = 11 rungs above 381/100: BC-209 retargeted at
      n = 11 and BC-206 taking the second rung lane, with BC-207's exact cover deferred
      because there is no wall for it to sit at.
      Rule three, the radius. If BC-199's rho_0 comes out below 1e-6 in the chart, the
      tree is dropped and the radius is kept as a theorem: block two opens no conditional
      lead against Trump's pose, BC-204 and BC-207 stay closed, the three leads go to
      BC-206, BC-208 and BC-209, and the radius goes to agenda-018's BC-176 and BC-177 as
      the packet and its review rather than being registered here.
      Rule four, the grid frontier. If BC-211's converged optimum at 399/100 is below
      thirteen, the m = 4 endgame is one certificate's shrink tax away and the B = 1 route
      is worth building before the conditional route: block two opens BC-212 in Lane A
      ahead of BC-204, and BC-205's calibration runs on the B = 1 instrument at side
      exactly 4 rather than on the conditional program at 3.99. If BC-211 refutes on two
      site sets, BC-212 stays shut and the conditional route runs as drafted.
      Rules one and two can both fire; rule three overrides the endgame half of rule one;
      rule four reorders Lane A of block two without closing any lead.
      Once this closeout is written, a ten-hour pass does not stop: it continues into
      agenda-022's BC-206 and BC-208, the two cells no rule gates (BC-208 needs BC-198's
      controls passing, which is its own entry condition), and the closeout records
      that continuation as the selected next entry rather than leaving it implicit.
      Where two rules select the same lead, the closeout records the collision and picks
      by the ranked candidate list rather than by recency.
      One question this closeout owns specifically, as agenda-019's did: whether the
      exhaustive tier is still affordable, since a fifth retained certificate at a side
      near 4.9 would be the largest atom set in the tier.
    entry: >-
      BC-197 through BC-202 and BC-211 are terminal or explicitly stopped, and their
      writers have stopped.
    exit: >-
      Per-block outcomes and stop reasons; the four doubling-down rules evaluated
      against the measured numbers with the block-two allocation named; a decision on the
      exhaustive tier's budget; documentation decisions; validation receipts from
      validate_schemas, render_agenda_map --check and check_documentation; ranked
      candidates; and one selected next entry.
    bead: think-jv2d
    workflows: [review-planning-oversight]
    depends_on: [BC-197, BC-198, BC-199, BC-200, BC-201, BC-202, BC-211]
    artifacts:
    - packing/campaign/agent-sessions/session-086-agenda021-overnight-pass.md
    outcomes:
    - scope: >-
        The block's W10 closeout: outcomes on every cell, the four doubling-down rules
        evaluated against the measured numbers, and one next entry selected.
      classification: achieved
      result: >-
        Run at minute 530 rather than 390, after an account rate limit ended every
        sub-agent of the pass at 09:21 UTC and the container was restarted; the
        coordinator resumed, gated the two frozen candidates the lanes had left, and
        closed the block. Every cell carries an outcome at its smallest honest scope.
        None of the four rules fired. Rule one asked whether the m = 5 wall lands within
        0.02 of five: it is bracketed to [97/20, 39/8], so the covering value binds at
        about 4.86 and the ceiling at 4.9885 never becomes the binding limit -- the
        opposite of the rule's condition, and the first direct evidence anywhere in this
        register about where a covering wall sits. Rule two asked whether the n = 11
        covering value is below eleven at 3.85: BC-200 produced no certificate there, so
        it did not fire. Rule three asked whether rho_0 is below 1e-6: it is 0.0023089,
        three orders above, so the local box is reachable and no lead closes. Rule four
        asked whether the n = 13 optimum converges below thirteen at 399/100: BC-211
        never converged, so it did not fire.
        With no rule firing, agenda-022 opens as drafted rather than reordered. What the
        block adds to it is one cell it did not have: BC-213, the remaining rung at
        973/200, the midpoint of the bracket by the schedule's own rule, which settles
        H-062 either way at a cost the ladder has already measured.
      evidence:
      - packing/campaign/agendas/agenda-021-three-numbers-and-a-wall.md closeout
      - packing/campaign/agent-sessions/session-086-agenda021-overnight-pass.md
      disposition: retire-success
      follow_up: null
    next_evidence: >-
      Which of agenda-022's leads open, which is the whole of what every cell in that
      agenda is blocked on.
  closeout:
    documentation_review:
    - path: SYNOPSIS.md
      decision: updated
      reason: >-
        T-021 enters the results headline and the registry aggregate, the round table
        and cost table gain exp-060 and exp-061, the reported covering values go from
        eight sides to fourteen, and the current handoff names this block's selected
        next entry.
    - path: README.md
      decision: checked-current
      reason: >-
        Its bound figures are rendered from the register rather than written by hand,
        and the front door's claims about what the project has proved are unchanged by
        a rung at two sizes it does not name.
    - path: TUTORIAL.md
      decision: checked-current
      reason: >-
        The tutorial teaches the certificate from first principles at n = 11 and quotes
        no n = 20 figure; nothing it explains changed.
    - path: conventions.md
      decision: checked-current
      reason: >-
        No new term, id shape or naming rule was introduced. The one convention this
        block leaned on -- certificate.json is the moving top-rung pointer and
        certificate-A-B.json an immutable rung -- was already written down, and this
        block is the first case of the pointer actually moving.
    - path: operating-rules.md
      decision: checked-current
      reason: >-
        OR-1 through OR-11 governed the block as written and none needed amending; the
        rate limit that ended the lanes is the external blocker OR-8 already names.
    - path: development.md
      decision: checked-current
      reason: >-
        No build, test or validation command changed. The one entry point that gained an
        argument, the n = 20 package replay, keeps its old invocation as the default.
    changes:
    - name: m5-ladder-and-t021
      result: >-
        s(20) and s(21) raised from 24/5 to 97/20 by a certificate retained through the
        gate on both routes, with the 193/40 rung beside it and the m = 5 covering wall
        bracketed to width 0.025.
      paths:
      - packing/cases/n20_fractional_certificate/certificate.json
      - packing/cases/n20_fractional_certificate/certificate-193-40.json
      - packing/cases/n20_fractional_certificate/certificate-24-5.json
      - packing/frontier/results.yaml
      - packing/frontier/evidence.yaml
      - packing/frontier/n-020.md
      - packing/frontier/n-021.md
      - packing/campaign/series/series-000-smoke-and-calibration/experiments/exp-061-h-062-m5-covering-wall.md
    - name: n11-covering-value-from-below
      result: >-
        nu*(3.82) >= 9.907906 and nu*(3.85) >= 9.049861 exactly, up from the retained
        1152/175 = 6.5829, with the cutting-plane loop retained as a module and a driver.
      paths:
      - packing/src/sqpack/fractional/cutting.py
      - packing/devtools/run_fractional_cutting.py
      - packing/tests/test_fractional_cutting.py
      - packing/campaign/series/series-000-smoke-and-calibration/experiments/exp-060-h-064-n11-fractional-packing-floor.md
    - name: trump-isolation-radius
      result: >-
        rho_0 and C at Trump's pose as exact rationals, with four corrections to X-014's
        sketch and the stress-ratio identity that empties the LP it proposed.
      paths:
      - packing/cases/trump11/isolation_radius.py
      - packing/tests/test_trump_isolation_radius.py
      - packing/campaign/series/series-000-smoke-and-calibration/results/bc-199-trump-isolation-radius.json
    - name: generator-cost-model-and-drivers
      result: >-
        Row generation priced against the container side, the site-density rule expressed
        as a function of it, the default rationalisation scale raised at flat
        verification cost, and three drivers the lanes ran their searches through.
      paths:
      - packing/devtools/bench_colgen.py
      - packing/devtools/colgen_checkpoint.py
      - packing/devtools/run_fractional_colgen.py
      - packing/src/sqpack/fractional/colgen.py
      - packing/campaign/agendas/agenda-019-efficiency-first-retarget-and-deep-strategy.md
    - name: moved-pointer-detector
      result: >-
        check_rung_figures accepts a superseded result that names only the rung it
        produced, exactly when the live pointer beside it is declared by its successor.
      paths:
      - packing/devtools/check_rung_figures.py
      - packing/tests/test_rung_figures.py
    validation:
    - scope: records
      status: passed
      evidence: >-
        uv run --frozen --all-extras --group dev packing-validate --records at the
        closeout commit: every record step green, including the results register, the
        rung-figure and case-prose detectors, the covering-value register's schema, the
        synopsis check and every generated view.
    - scope: retention-gate
      status: passed
      evidence: >-
        devtools.decide_certificate on both frozen candidates: 97/20 RETAINABLE at
        200001/200000 (sha256 445935cc...), 193/40 RETAINABLE at 1000003/1000000
        (sha256 085e1392...), each accepted by the exact sweep and the interval route
        with the two routes agreeing on the value.
    - scope: tests
      status: passed
      evidence: >-
        The touched modules: rung figures 37, trump isolation radius 6, fractional
        cutting 8, bench colgen 7, colgen checkpoint 8, run_fractional_colgen 8; ruff
        and ruff format clean repository-wide, basedpyright clean on every file this
        block wrote.
    - scope: push-tier
      status: pending
      evidence: >-
        Not run locally at the closeout: the container was restarted mid-block and the
        remaining budget went to landing the result and the records. Hosted CI runs the
        full gate on the pushed head.
    replanning:
      candidates:
      - bead: think-wufn
        workflow: research-loop
        priority: 0
        rationale: >-
          BC-213, the remaining rung at 973/200. H-062 is one rung from a verdict: the
          bracket is 0.025 against the 0.02 it registered, and the midpoint settles it
          either way. The ladder has measured what the rung costs -- about 17 s per LP
          round at this side, a converged rung in under twenty minutes at 193/40 -- so
          this is the cheapest registered question in the queue.
      - bead: think-m3sx
        workflow: pipeline-improvement
        priority: 1
        rationale: >-
          BC-198, the class-certificate program, never opened. It is the cheap half of
          the conditioning question and block two's BC-208 rests on it entirely.
      - bead: think-614o
        workflow: pipeline-improvement
        priority: 1
        rationale: >-
          BC-201, the near-tight census, stopped with its tool half-built. H-065 is
          untouched and the readout is an hour's work from where the lane left it.
      - bead: think-gku0
        workflow: pipeline-improvement
        priority: 2
        rationale: >-
          BC-204, the admissible-domain generalisation, which no rule reordered and
          which block two's conditional route cannot start without.
      - bead: think-4in0
        workflow: research-loop
        priority: 2
        rationale: >-
          BC-209 inherits BC-202's resumable checkpoint at 138/25 and the cost model
          that now separates a cold column round from a warm one.
      selected:
        bead: think-wufn
        workflow: research-loop
        rationale: >-
          One rung closes a registered hypothesis that four rungs left open by 0.005 of
          bracket width, at a cost this block measured rather than estimated, and it is
          the only candidate whose outcome is a verdict rather than an instrument.
      operator_input:
        status: unavailable
        note: >-
          The operator directed the pass to run autonomously overnight and was not
          consulted at the closeout. The rate limit that ended the lanes at 09:21 UTC and
          the container restart that followed are recorded as the block's stop reason
          rather than as a decision.
---
# Agenda 021 — Three Numbers and a Wall

## Workflow Entry Point

This agenda is paused.
It becomes active when the operator has chosen it over
[Agenda 019](agenda-019-efficiency-first-retarget-and-deep-strategy.md)’s remaining
queue, which it does not replace: `BC-191` is Lane C’s own first half and runs inside
this block, and `BC-190`, `BC-192`, `BC-193`, `BC-194` and `BC-195` stay where they are.

Begin at `BC-211`, `BC-199` and `BC-191` together, on three separate cores.
`BC-211`, the `n = 13` calibration, is numbered after both agendas were drafted and runs
first on Lane A: it is the cheapest cell in the block and the one whose answer reorders
block two, so that answer is in hand before anything else on the lane is spent.
They are the only work that starts takeable — `BC-211` and `BC-199` are `ready` here,
and `BC-191` is `ready` in agenda-019 — and every other cell in this agenda depends on
at least one of the three.
`BC-211` and `BC-199` enter under `research-loop`; `BC-191` enters under
`efficiency-loop`, as it was registered.

**Three programs, and each spans this agenda and the next.** Every research cell here
and in [agenda-022](agenda-022-the-conditional-route.md) carries a `program` slug, which
is what lets the agenda map show one line of work whole rather than split across two
files; the slugs are the three programs
[X-015](../explorations/X-015-the-map-and-the-three-programs.md) ranks.
`grid-frontier-exact-values` is the `m = 5` ladder, the `n = 13` calibration, and in
block two the `n = 12` ladder and whichever of the conditional or `B = 1` routes opens.
`n11-closure` is the radius, the covering value from below, the census, and the class
certificates at `n = 11`. `reach-table-ladder` is the `n = 26` rung and the reach-table
rungs `BC-191` prices.
The closeouts carry no program.

## State at handoff

Written for whoever picks this up cold.

**What is retained, and where the ladder stands.** Seven registered cases carry a
first-party weighted fractional unavoidable-set certificate, each decided twice from
frozen bytes by two routes that fail differently.
Every figure below is read from the retained `certificate.json` files and from
`frontier/results.yaml`, not from prose.

| Case | Side | Atoms | Total mass | Least cell mass | Result |
| --- | --- | ---: | --- | --- | --- |
| `n = 11` | `381/100` | 1121 | `434547/40000 = 10.863675` | `4001/4000` | `T-018` |
| `n = 12` | `99/25` | 2097 | `149987/12500 = 11.998960` | `12501/12500` | `T-017` |
| `n = 17`, `18` | `459/100` | 1184 | `423327/25000 = 16.933080` | `200009/200000` | `T-019` |
| `n = 19`, `20`, `21` | `24/5` | 2260 | `946131/50000 = 18.922620` | `50007/50000` | `T-020` |

All four use the same net and the same shrink: `angle_limit = 207107/500000`,
`direction_steps = 180` — so 181 directions over an arc of `0` to `45.000043°`, spacing
`0.263696°` at the axis-parallel end — with `B = 9977/10000`, `D = 207107/90000000` and
`B(1 + D) = 0.999996`.

**Where the method stops, which is proved.** No certificate for `n` exists above
`⌈√n⌉ · B`, and `CERTIFICATE-REACH.md` now carries a second bound beside it: the same
argument with the case’s best known packing in place of the refuting grid, which is
X-014’s own step at `n = 11` generalised across the register and rendered as the table’s
`cap` column.

| Case | Best packing | `ceiling` | `cap` | `limit` | Limited by | Prize |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
| `n = 11` | `3.8771` | `3.9908` | `3.8690` | `3.8690` | cap | `+0.0590` |
| `n = 12` | `4.0000` | `3.9908` | `3.9908` | `3.9908` | ceiling | `+0.0308` |
| `n = 19` | `4.8856` | `4.9885` | — | `4.9885` | packing | `+0.0856` |
| `n = 20`, `21` | `5.0000` | `4.9885` | `4.9885` | `4.9885` | ceiling | `+0.1885` |
| `n = 26` | `5.6213` | `5.9862` | — | `5.9862` | packing | `+0.4982` |

At `n = 11` the cap is what binds, and it is the arithmetic X-014 did by hand: the
shrink alone caps the instrument at `U · B = 3.868166`, and the net’s `0.012100°` offset
from the record’s `40.181937°` tilt lifts it to `3.868983`, which the table rounds to
`3.8690`. The last `0.0081` below Trump’s value is out of reach at any site set.

**At `m = 5` the cap and the ceiling coincide, and that is why the wall is measurable
there.** The best known packing at `n = 20` and `n = 21` is the axis-parallel grid, so
every tilt offset is zero, the cap collapses onto the ceiling at `4.9885`, and the two
structural limits are one number.
Only the covering value can bind below it, which makes `m = 5` the one place in the
register where a bisection separates a covering wall from a structural one without a
packing record standing in the way.

**What is open with the evidence already gathered.** `n = 11` at `3.82`: two independent
site sets stop at exactly `11.000000`, one converged over twelve rounds and one standing
through twenty-four while its least covered mass climbed from `0.8490` to `0.9997`. The
rejection route is far from closing — the converged dual’s exact maximum pointwise depth
is `1925/1152 = 1.671007` across `1650944` arrangement vertices, so the depth-scaled
total is `1152/175 = 6.5829` against the eleven a ceiling needs.
`n = 18` at `117/25`: three site sets, 538, 578 and 618 orbits, all returning exactly
`18.000000`, the third after 157 rounds and `7056 s`, with the run stopped for its cost
rather than its answer.

**What the last block changed.** The retention gate is no longer the dominant cost.
The exact event-cell sweep now decides in `int64` on the weights’ common scale, holds
reachable cells as spans and runs the 181 directions in parallel: `n = 17` in `21.8 s`
against `1473 s`, `n = 20` in `38.7 s` against `5378 s`, the identical least covered
mass every time, with the `Fraction` route kept unchanged as the reference.
`BC-191` — row generation at 79–94% of every round, site density never expressed as a
function of the container side, an untuned grid costing `8.8×` at `n = 20`’s own side —
is untouched and is what binds a run.

## Why three numbers and a wall

[X-014](../explorations/X-014-closing-from-both-ends.md) answers the owner’s question
with a yes and a no.
The yes: a certificate that has stopped proving infeasibility still constrains the
packings that survive it (Lemma 1), a branch of the configuration space can carry its
own certificate (Lemma 2), a direction class can carry its own thresholds (Lemma 3), and
the first-order certificates at Trump’s pose give a computable box.
The no: none of that is a shortcut past the case analysis, and the size of the tree is
unknown.

Its verdict names the three numbers that set that size — where the covering value
crosses eleven, how large the tight-core set is there, and how large `ρ₀` is at Trump’s
pose — and says two of the three are an afternoon’s computation each.
`BC-200`, `BC-201` and `BC-199` are those three.
None of them needs a new soundness surface: the first is the ceiling instrument run to
convergence, the second is exact linear algebra on retained matrices, the third is a
readout the sweep already computes.
That is why they are this block and not the next one.

The fourth number is the wall the ladder itself is standing next to, and `m = 5` is the
only place in the register where it can be measured cleanly.
At `n = 20` and `n = 21` there is no packing record to interfere — the upper bound is
the trivial grid, so the reach table’s packing cap collapses onto the ceiling and the
two structural limits are the single number `4.9885`. The covering value is then the
only other thing that could bind, and a bisection separates it from the ceiling.
Nobody has ever measured a covering wall.
The closest the record comes is two site sets stopping at exactly eleven at `3.82`, and
`T-018` says plainly that reading that as `τ*` would be reading an artefact: adding
sites can only lower a restricted optimum, so one site set’s converged value is a
statement about that site set.

`BC-211` is the stepping stone the block adds late and runs first.
[X-015](../explorations/X-015-the-map-and-the-three-programs.md) read Bentz’s two proofs
in X-014’s terms — `s(46) = 7` is one unconditional certificate at the grid side with no
case split, and `s(13) = 4` is Lemma 1 used integrally, then a six-leaf tree — and
priced the covering value at the `m = 4` ceiling near `12.06`–`12.24`, below the
thirteen a certificate needs.
If a zero-build run at `399/100` confirms that, the grid frontier’s endgame is one
`B = 1` certificate’s shrink tax rather than a tree, and block two’s Lane A changes
shape; the rule that says so is written into `BC-203` now.

`BC-198` is the cheap half of the conditioning question and is deliberately placed
before the expensive half.
Lemma 3 changes the covering program’s thresholds and objective — two variables and one
normalisation row — and nothing geometric, while Lemma 2 needs the admissible domain
generalised in `sweep.py`, `generate.py`, `interval.py` and `colgen.py`, all three of
which currently assume a convex domain that a container minus an excluded region is not.
Testing whether conditioning buys anything at all costs 110 minutes on the threshold
route; finding out after building the domain generalisation would cost a block.

## The pre-registered rungs

The four `m = 5` sides are fixed by a rule, before the block opens, and not chosen after
a reading. Bisect `[24/5, 9977/2000]`, round each midpoint to the nearest `1/200`, break
ties away from `24/5`. The first three levels are therefore:

| Level | Bracket | Midpoint | Side run |
| ---: | --- | ---: | --- |
| 1 | `[4.800, 4.9885]` | `4.89425` | `979/200 = 4.895` |
| 2, rung 1 passed | `[4.895, 4.9885]` | `4.94175` | `247/50 = 4.940` |
| 2, rung 1 walled | `[4.800, 4.895]` | `4.84750` | `97/20 = 4.850` |
| 3, from `4.940` up | `[4.940, 4.9885]` | `4.96425` | `993/200 = 4.965` |
| 3, from `4.940` down | `[4.895, 4.940]` | `4.91750` | `123/25 = 4.920` |
| 3, from `4.850` up | `[4.850, 4.895]` | `4.87250` | `39/8 = 4.875` |
| 3, from `4.850` down | `[4.800, 4.850]` | `4.82500` | `193/40 = 4.825` |

The fourth rung is the live bracket’s midpoint by the same rule.
Every one of the sixteen leaves leaves a bracket of at most `0.015`, and most leave
`0.010`; `H-062` registers `0.02` and the schedule beats it with room.
Two of the sixteen paths put a rung within a thousandth of Wainwright’s `n = 19` packing
at `4.885618`, which is where the soundness alarm in `BC-197` bites: above that side a
converged optimum below nineteen contradicts a retained packing.

## The wall accounting

`450` elapsed minutes, three research lanes on three cores, the closeout at `390`.

| Clock | Lane A (core 1) | Lane B (core 2) | Lane C (core 3) | Coordinator |
| --- | --- | --- | --- | --- |
| `00:00–00:10` | — | — | — | wall start, continuity trigger armed, dispatch |
| `00:10–01:20` | `BC-211` `n = 13` | `BC-199` radius | `BC-191` (agenda-019) | — |
| `01:20–03:00` | `BC-197` `4.985` rung, then the ladder | `BC-199` ends `02:10`; `BC-200` from `02:10` | `BC-202` `n = 26` from `02:10` | integration checkpoint at `03:00` |
| `03:00–04:40` | `BC-197` | `BC-200` ends `04:00`; `BC-201` from `04:00` | `BC-202` | — |
| `04:40–06:30` | `BC-198` | `BC-201` ends `05:00`, then slack | `BC-202` ends `05:00`, then slack | — |
| `06:30–07:30` | freeze | freeze | freeze | `BC-203` closeout |

Cell budgets sum to the lane: `BC-211` 70, `BC-197` 200 and `BC-198` 110 on Lane A, the
full 380 minutes; `BC-199` 120, `BC-200` 110 and `BC-201` 60 on Lane B; `BC-191`’s
registered 120 and `BC-202`’s 170 on Lane C. Lanes B and C carry 90 minutes of slack
each, which is the coordinator’s to reassign at the `03:00` checkpoint and not a cell’s
to spend.

## The ten-hour pass

A pass that runs this block overnight has about two and a half hours left after `BC-203`
closes, and it does not wait for an operator to spend them.
Two cells of [agenda-022](agenda-022-the-conditional-route.md) depend on no
doubling-down rule: `BC-206`, the `n = 12` ladder toward the ceiling, and `BC-208`, the
two class theorems, which needs only `BC-198`’s controls passing.
The pass continues into both as soon as the closeout is written, `BC-206` on the lane
core `BC-202` released and `BC-208` on `BC-198`’s, and stops on their own kill
conditions or on the operator.
Everything else in agenda-022 waits for the rules the closeout evaluated.

**The core budget is part of the plan, not an afterthought.** Agenda 017 ran four lanes
on four cores at load average `10.6` and everything ran about two and a half times
slower than it needed to.
Three research lanes is the cap here, one core each.
The fourth core is reserved, and it is reserved for a specific thing:
`certificate.verify` decides the 181 directions in a forked process pool, so a run of
`devtools.decide_certificate` takes it.
Gates are therefore serialised through the coordinator — two lanes may not hold the gate
at once — and `OR-3` applies to the lane that is waiting: launch it and keep the next
slice moving, never poll it, and never start one against a tree about to change.

`OR-6` puts an integration checkpoint inside four hours; it is at `03:00`, it is fifteen
minutes, and it belongs to the coordinator rather than to a cell.
It replans forward from measured time and does not reopen a closed slice.

## Stop rules, and the rule about stop rules

Each cell carries its own kill condition and they are in the cells.
Three rules sit above them and apply to the block.

**A self-declared budget is not a stop condition.** `OR-8`. The `450` minutes above is
an estimate this plan wrote for itself.
Under an open-ended mandate only three things end the run: the operator says so, an
external blocker makes progress impossible, or the work is genuinely exhausted.
Reaching minute `450` is none of them; it is the moment to plan the next slice, and
[agenda-022](agenda-022-the-conditional-route.md) is that slice already drafted.

**The continuity trigger is recurring and is not deleted.** A one-shot chain is only as
long as the first turn that decides the work is finished, and `D-395` is a run that had
eleven and three-quarter hours of unbroken pings, wrote itself a note saying the budget
was spent, and then deleted the note.
So the trigger armed at minute `10` fires on its own schedule regardless of what any
turn concluded, and deleting it requires the operator to ask.
It is the only irreversible action in the loop.

**A time-limited rung is an outcome, not a failure.** Every long run in Agenda 017 that
hit its wall cost nothing, because its checkpoint was sound.
A cell that stops on its cap records the checkpoint, the last value, and the reason;
`BC-203` classifies it as time-limited and carries it forward.

## What does not change

**Retention.** Freeze the candidate before deciding it, decide the frozen bytes through
`devtools.decide_certificate`, and retain only when both routes accept **and agree on
the value**. Nothing in this block relaxes that, and nothing in it needs to: `BC-198`
builds a two-threshold program the gate does not yet decide, and the honest consequence
— stated in the cell — is that no class certificate is retained in this block.

**A candidate counts only when its row loop stopped for want of a violated placement**,
and the loop’s final least covered mass is still reported beside the objective.
`BC-197` splits its per-rung budget on exactly that distinction, because the refutation
side of a rung does not need convergence and the confirmation side does.

**Ceilings are judged on the exact check.** `BC-200`’s whole warning is one number: at
`3.82` the sampled depth was `12/11` and the exact maximum was `1925/1152`, 53 per cent
higher, because depth peaks at arrangement vertices no grid samples.

**Read the evidence, not a reconstruction of it.** Every figure in this agenda is from a
retained artifact or a run log.
Five are estimates and each is labelled and written down before its run so the run can
contradict it: the `m = 5` wall at `4.92` to `4.94`, the covering value at the `m = 5`
ceiling near `20.4`–`20.7` and at the `m = 4` ceiling near `12.06`–`12.24`, a round at
`5.52` at `660` to `1530 s`, and `H-065`’s declared accept fraction, which is a
pre-registration and not a prediction.

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
