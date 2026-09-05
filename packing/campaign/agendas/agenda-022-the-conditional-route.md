---
title: "agenda-022 — the conditional route: boxed certificates, the n = 13 calibration, and the class theorems"
softschema:
  contract: packing.squares:ExperimentAgenda/v1
  schema: ../schemas/agenda.schema.yaml
  envelope: agenda
  status: enforced
agenda:
  id: agenda-022
  title: "The Conditional Route — Boxed Certificates, the n = 13 Calibration, and the Class Theorems"
  updated: '2026-09-05'
  status: active
  objective: >-
    Block two, and every cell in it is contingent. Agenda-021 measures four numbers and
    its closeout, BC-203, carries three doubling-down rules written before that block
    opened; those rules decide which two of the three lanes below open and which stays
    shut. Nothing here is takeable until BC-203 has run, and that is deliberate: X-014's
    own reading is that the expensive half of the conditioning idea should not be built
    until the cheap half has said whether conditioning buys anything, and that the
    perturbation half should not be built at all if the isolation radius comes out too
    small for a tree to reach.
    What the block would build, if the rules select it, is the conditional route.
    X-014's Lemma 2 is one counting step, but it is the one that needs the admissible
    centre domain generalised in all four places that currently hard-code the rotated
    container square and assume it convex -- sweep.py, generate.py, interval.py and the
    column generator that routes its oracle through the second -- and it needs the net
    doubled to a full quarter turn, because a box breaks the container's D4 symmetry and
    Condition 1 can no longer fold angles onto the shorter arc. That is 180 minutes
    before a single case is closed, which is why it is here rather than in block one and
    why it is calibrated against a case the classical method already closes by hand:
    Bentz's non-adjacent corner-restricted configuration at n = 13, whose kill condition
    is stated in advance as mass at or above thirteen.
    A fourth rule, added with agenda-021's BC-211, can reorder that lane: if the
    zero-build run at n = 13 converges below thirteen, the B = 1 route -- covering over
    the direction continuum at an integer side, BC-212 -- is built first, in BC-204's
    place, and the calibration runs on it at side exactly 4, since the endgame is then
    one certificate's shrink tax rather than a tree.
    Beside it run the two cheaper leads. The class theorems at n = 11 need no geometry at
    all -- two variables and a normalisation row on a program agenda-021's BC-198 already
    froze -- and they are where Gardner's conjecture and the composition count would be
    mechanised with the class widened from two angles to two cells. The ladder lane keeps
    the register moving at m = 4 and takes the reach-table rungs BC-191 has finally
    priced. The exact-cover check sits at whichever wall block one found, and opens only
    if block one found one.
    The research wall is 360 elapsed minutes with the closeout at 300. Retention is
    exactly as strict as it is now, and a conditional certificate is a different object
    that the gate must decide as one.
  items:
  - id: BC-213
    purpose: research
    owner_focus: correctness
    instances: [20, 21]
    state: complete
    priority: 0
    question: >-
      Does the remaining rung of the m = 5 bisection, 973/200 = 4.865, certify or wall --
      and so bring the covering-wall bracket inside the 0.02 H-062 registered?
    hypotheses: [H-062]
    budget: >-
      60 elapsed minutes, Opus at maximum thinking, research-loop. Added by agenda-021's
      closeout as its selected next entry, and the only cell here that no doubling-down
      rule gates.
      The side is the schedule's own: the midpoint of the bracket agenda-021 left,
      [97/20, 39/8], rounded to the nearest 1/200 with ties away from 24/5, which is
      973/200. Either outcome settles H-062. A certificate leaves [973/200, 39/8], width
      0.010; a wall on both constructions leaves [97/20, 973/200], width 0.015; both sit
      inside the registered 0.02.
      Two constructions as H-062 requires, in the order BC-197 measured: the uniform
      grids at BC-191's density rule first, and -- since at 97/20 the grid walled at the
      very side the seeded set certified -- the grids unioned with the 97/20
      certificate's own 1680 atoms scaled by 973/970, which is now the nearer seed. The
      cost is measured rather than modelled: a converged rung at 193/40 took 54 LP rounds
      and 1008.6 s of wall, and the seeded convergence at 97/20 took 1616.5 s, so a rung
      here is half an hour of run inside a one-hour cell.
      Refutation is early and confirmation is convergence, exactly as BC-197 ran it: an
      optimum crossing twenty with placements still violated refutes the rung on that
      construction, and a converged optimum below twenty is frozen, rationalised at the
      default scale and handed to the gate. The soundness alarm does not apply below
      4.885618. Kill: a round costing more than 25 minutes.
    entry: >-
      Agenda-021's BC-197 is terminal with the bracket [97/20, 39/8] and both its
      certificates retained; the drivers, the density rule and the default scale are on
      main behind this block's own branch.
    exit: >-
      The rung decided on both constructions, the bracket it leaves, and H-062 resolved
      or the reason it still is not; a frozen and gated candidate if it certifies.
    bead: think-wufn
    workflows: [research-loop]
    depends_on: []
    artifacts:
    - packing/campaign/series/series-000-smoke-and-calibration/experiments/exp-062-h-062-m5-midpoint-rung.md
    - packing/campaign/series/series-000-smoke-and-calibration/results/bc-213-m5-midpoint-register.txt
    parallel_group: agenda022-lane-a
    program: grid-frontier-exact-values

    outcomes:
    - scope: >-
        The remaining pre-registered rung of H-062's m = 5 bisection, at 973/200 = 4.865,
        decided on both declared constructions.
      classification: achieved
      result: >-
        Both constructions wall. The uniform grids at BC-191's density rule -- counts
        (34, 46, 56), 806 orbits, 6216 sites -- crossed twenty at LP round 16 with
        20.001502 and 543 placements still violated, least covered mass 0.890041. Those
        grids unioned with T-021's 1680 atoms scaled by 973/970 crossed at LP round 34
        with 20.000223 and 213 violated. Each fell to the pre-registered
        early-refutation clause; neither converged, so nothing was frozen and
        cases/n20_fractional_certificate/ is untouched.
        The bracket left is [97/20, 973/200], width 0.015 against the 0.02 H-062
        registered, its lower end T-021's retained certificate and its upper end this
        wall, 0.1235 below the ceiling 9977/2000. H-062 is accepted on its own
        threshold -- the first covering wall this project has pinned to the width its
        hypothesis asked for, and a direct statement that at m = 5 the covering value
        binds and the ceiling never does.
        Two things the record carries rather than smooths over. The seeded crossing
        cleared twenty by 2.23 parts in a hundred thousand, eighteen times tighter than
        the grid's crossing at the rung below, on a loop whose violated count was
        collapsing into it; the rule does not read margins and was applied as written,
        but that rung is where a denser site set would be worth spending. And the
        acceptance clause asks for a converged optimum at or above twenty, which neither
        run produced: the clause is met because rows only raise a restricted optimum, so
        each site set's converged optimum is bounded below by the crossing, and the
        criterion asks for the bound and not the value.
      evidence:
      - packing/campaign/series/series-000-smoke-and-calibration/experiments/exp-062-h-062-m5-midpoint-rung.md
      - packing/campaign/series/series-000-smoke-and-calibration/results/bc-213-m5-midpoint-register.txt
      disposition: retire-success
      follow_up: null
    next_evidence: >-
      Whether the first covering wall this project has bracketed can be pinned to the
      width its hypothesis asked for, which is what tells the reach table's ranking how
      much of a case's runway the covering value actually leaves.
  - id: BC-204
    purpose: tool_validation
    owner_focus: correctness
    instances: [11, 13]
    state: blocked
    priority: 1
    question: >-
      Can the covering program's admissible centre domain be generalised from the
      hard-coded rotated container square to a declared domain -- a container minus an
      excluded core region, which is not convex -- in all four places that assume it,
      with the retention gate unchanged and both routes still agreeing on the value?
    budget: >-
      180 elapsed minutes, Fable at maximum thinking, pipeline-improvement then
      factual-review, on lane core 1.
      What Lemma 2 needs, stated as the change rather than as the lemma. For a box b of
      placements of one unit square, I_b is the region every placement in b occupies and
      Lambda_b is the set of admissible B-square placements at net directions disjoint
      from I_b. A measure of total mass below n giving mass at least one to every member
      of Lambda_b, and to every B-square at a net direction lying inside some placement
      in b, proves no packing has a square in b. The counting is one step; the domain is
      the work.
      Four consumers hard-code the admissible domain as the rotated container square and
      each assumes it convex: sweep.centre_domain, the float mirror in generate.py, the
      four half-planes interval.DirectionSearch propagates, and colgen, which routes its
      oracle through generate. A container minus I_b is not convex, so all four move or
      none does.
      The net doubles. A box breaks the container's D4 symmetry, so Condition 1 can no
      longer fold angles onto the shorter arc and the net must span a quarter turn rather
      than an eighth. The interval route already decides on the doubled net -- 361
      directions where the exact sweep decides 181 -- so this is a factor of two in
      directions and no new idea, and the cost of that factor is measured in this cell
      rather than assumed.
      0--90 the admissible-domain hook: a declared domain object the four consumers read,
      with the current rotated square as its default, rather than a special case threaded
      through four call sites. 90--140 the controls. Every retained certificate -- n = 11
      at 381/100, n = 12 at 99/25, n = 17 at 459/100, n = 20 at 24/5 -- must decide
      through the generalised path to the identical least cell mass and the identical
      witness cell; a conditional program with an empty box must reproduce the
      unconditional program exactly; and the negative controls already in the fractional
      suite must refuse identically under optimized Python. 140--180 the gate: a
      conditional certificate is a different object, so the box and the doubled net go in
      the frozen bytes and devtools.decide_certificate must read them and decide both
      routes on them. Retention does not move.
      Kill: any retained certificate deciding differently through the new path, which
      ends the change outright; or the doubled net's decision cost passing what BC-205
      and BC-207 can afford, recorded as a number rather than as an impression.
    entry: >-
      BC-203 selected this lead under its first doubling-down rule and did not fire its
      third; the four consumers are frozen at agenda-021's terminal revision; X-014's
      Lemma 2 and its proof are in the record.
    exit: >-
      A generalised admissible domain in all four consumers with every retained
      certificate deciding bit-identically through it, the doubled-net decision cost
      measured, and the gate deciding a conditional object; or a typed rejection naming
      which consumer refused and the figure that refused it.
    bead: think-gku0
    workflows: [pipeline-improvement, factual-review]
    depends_on: [BC-203]
    blocked_on: >-
      BC-203's first doubling-down rule, which did not fire: the m = 5 wall is bracketed
      to [97/20, 39/8], far from the 0.02 of five the rule asks for, so the ladder still
      has room at m = 5 and the endgame did not take two of block two's leads. The
      domain generalisation opens when a rule or the operator gives it a lane.
    parallel_group: agenda022-lane-a
    program: grid-frontier-exact-values
    next_evidence: >-
      Whether Lemma 2 is buildable at all under the existing soundness surface, which
      BC-205 and BC-207 both need and neither can start without.
  - id: BC-205
    purpose: measurement_validation
    owner_focus: correctness
    instances: [13]
    state: blocked
    priority: 1
    question: >-
      Does the conditional program close a case the classical method closes by hand --
      Bentz's non-adjacent corner-restricted configuration at n = 13 -- at a rational side
      just below four?
    budget: >-
      110 elapsed minutes, Fable at maximum thinking, research-loop, on lane core 1 after
      BC-204. This is X-014's sixth measurement and it is a calibration, not a target.
      Bentz proved s(13) = 4 by splitting on the two placements of the corner-restricted
      boxes -- non-adjacent, with two critical regions, and adjacent, with four. The calibration boxes the two corner-restricted squares of the
      non-adjacent configuration at side 399/100 = 3.99, takes their forced points as
      cores, and asks the conditional program to close the case.
      The side is tight on purpose and the record should say so. At n = 13 the ceiling is
      4B = 3.9908, so 399/100 sits 0.0008 below the largest side the instrument can reach
      at all. A calibration at a comfortable side would not test the thing that matters,
      which is whether conditioning helps where the unconditional program has no room
      left. If 3.99 proves unreachable for a reason other than the conditional step, fall
      back to 398/100 and record which reason.
      Kill, and it is X-014's own: the boxed case still returning mass at or above
      thirteen. Conditioning cannot then close even a case the classical method closes by
      hand, and the conditional route is not worth the domain generalisation it cost.
      That reading is fixed here, before the run.
      Under BC-203's fourth rule this cell runs instead on BC-212's B = 1 instrument at
      side exactly 4, asking for one unconditional certificate with mass below thirteen
      over the direction continuum; the kill is then a converged mass at or above
      thirteen at side 4, and a pass is a machine reproof of s(13) = 4 in one branch.
      What a pass buys and what it does not, on the conditional route. It is a
      mechanised replay of one case of a published proof and claims S3 at most; it does
      not reprove s(13) = 4, because Bentz's argument has other cases and this one is the
      calibration. On the B = 1 route a pass is the whole theorem, still S3, the theorem
      being Bentz's; the significance is in the instrument, which then points at n = 21.
    entry: >-
      BC-204 or BC-212, whichever BC-203 opened, is terminal with every control passing;
      Bentz's 2010 paper is in the archive and the non-adjacent configuration is read
      from it rather than recalled.
    exit: >-
      Either the conditional program closing the boxed case at 399/100, with the frozen
      bytes accepted by both routes and agreeing on the value, or the mass it returns and
      the kill fired with the number that fired it.
    bead: think-9kuy
    workflows: [research-loop]
    depends_on: [BC-203]
    blocked_on: >-
      BC-204 or BC-212, whichever opens first; neither has, for the reasons each records.
    parallel_group: agenda022-lane-a
    program: grid-frontier-exact-values
    next_evidence: >-
      Whether the conditional route can close a known case, which is the only calibration
      available anywhere before it is pointed at n = 11, where no answer is known.
  - id: BC-212
    purpose: tool_validation
    owner_focus: correctness
    instances: [13, 21, 46]
    state: blocked
    priority: 1
    question: >-
      Can a certificate at shrink B = 1 -- closed unit-square covering with open-box
      counting at an integer container side -- be decided soundly over the whole
      direction continuum rather than on a finite net, so that one certificate at side
      exactly 4 reproves s(13) = 4 and one at side exactly 5 could prove s(21) = 5?
    budget: >-
      180 elapsed minutes, Fable at maximum thinking, pipeline-improvement then
      factual-review, on lane core 1, opened only by BC-203's fourth rule and then in
      BC-204's place. Numbered after the rest of this agenda was drafted; added with
      BC-211 on X-015's stepping-stone pricing.
      What the ceiling proves and what escapes it. On any finite net with largest
      half-gap tangent D, Condition 4 forces B < 1/(1 + D) and no certificate sits above
      ceil(sqrt(n))/(1 + D); a quarter-turn net alone buys nothing here, since boxes of
      side 1 + eta on a net with half-gap D prove only sides at most m/(1 + D). Bentz's
      s(46) = 7 is the model of what does escape: 45 points, closed unit squares covered,
      disjoint open boxes counted, the container side exactly 7, and the nonavoidance
      lemmas direction-free -- cases/bentz46 has audited it exactly. Weighted atoms at
      B = 1 need the covering condition at every angle, not at 181 or 361 of them.
      0--90 the decision: an angle-interval branch and bound over theta in [0, pi/4]
      together with the centre box, propagating the covered mass of a closed unit square
      as an interval in theta on top of the existing interval route -- which today
      branches over centre boxes at fixed doubled-net directions -- refusing any leaf it
      cannot decide, with the exact event-cell sweep at each leaf's endpoint angles as
      the check. 90--135 the controls, fixed before the target run: the positive one is
      Bentz's 45-point set accepted at n = 46 and side exactly 7 with unit weights, the
      known answer; the negative one is a point set with a retained escaping pose from
      sqpack.falsify, which must be refused with the angle interval that refuses it; and
      the retained n = 12 certificate at 99/25, re-read at B = 1, must be decided one way
      or the other with the refusing angle exhibited if it fails, since a certificate
      sound on the net need not be sound on the continuum. 135--180 the gate: B = 1 and
      the continuum decision enter the frozen bytes and devtools.decide_certificate
      refuses the object unless both routes accept it.
      Kill: the angle branch and bound failing to close on the n = 46 control inside the
      budget, or the positive control refused.
    entry: >-
      BC-203 fired its fourth rule; BC-211's converged mass at 399/100 is retained; the
      interval route and the exact sweep are frozen at agenda-021's terminal revision.
    exit: >-
      A decision path at B = 1 over the direction continuum with the n = 46 control
      accepted, the negative control refused with its angle interval, and the gate
      refusing or deciding the new object; then, inside the same budget if it remains,
      the n = 13 run at side exactly 4 that BC-205 consumes; or a typed rejection naming
      the leaf or control that refused.
    bead: think-e65r
    workflows: [pipeline-improvement, factual-review]
    depends_on: [BC-203]
    blocked_on: >-
      BC-203's fourth doubling-down rule, which did not fire: BC-211 never converged at
      399/100, so the n = 13 covering value is unmeasured and the B = 1 route stays shut
      until a converged optimum below thirteen says the m = 4 endgame is one certificate
      away. BC-213's rung does not bear on it either way.
    parallel_group: agenda022-lane-a
    program: grid-frontier-exact-values
    next_evidence: >-
      Whether an exact grid value can be proved by one machine certificate, which is the
      whole of what separates the m = 4 and m = 5 endgames from n = 11's.
  - id: BC-206
    purpose: research
    owner_focus: correctness
    instances: [12, 21]
    state: complete
    priority: 1
    question: >-
      How far above 99/25 does the n = 12 ladder climb before its restricted optimum
      reaches twelve, given that the ceiling forecloses the case at 3.9908 and the
      retained rung already has only 0.001040 of margin?
    budget: >-
      120 elapsed minutes, Opus at maximum thinking, research-loop, on lane core 3.
      The retained rung is 99/25 = 3.96 with 2097 atoms and total 149987/12500 =
      11.998960, a margin of 0.001040 below twelve, which is the tightest margin in the
      register. The ceiling is 4B = 3.9908, so 0.0308 of runway remains and the
      conjectured 4 is foreclosed by the ceiling rather than by the search.
      Pre-registered sides, fixed before any command runs: 397/100 = 3.97, 398/100 = 3.98,
      3985/1000 = 3.985 and 399/100 = 3.99, the last of them 0.0008 below the ceiling.
      Two facts from the record set the expectations. Margin is not monotone in the side:
      the n = 12 ladder itself has margin 0.007175 at 197/50 and 0.029410 at the higher
      79/20, and the n = 17 ladder shows the same shape, so a better site set at a higher
      side can open the margin back up rather than close it. And rationalisation nearly
      cost this case a rung: at scale 200,000 and 2097 atoms the rounding loss was
      0.005314 against a surviving margin of 0.001040. BC-191's decision on the default
      scale applies here and the run states which scale it used before it starts.
      The second leg is contingent and runs only when BC-203 fired its first rule: the
      n = 21 continuation above the n = 20 wall. n = 21's own wall is a higher side than
      n = 20's, because a certificate there needs mass below twenty-one rather than below
      twenty, and the sides are the remaining leaves of agenda-021's pre-registered
      bisection tree above the n = 20 wall. When rule one did not fire, the leg is
      skipped and the cell's whole budget is the n = 12 ladder.
      Kill: a rationalisation loss exceeding the margin at any rung, in which case raise
      the scale and re-run rather than retaining a rung that survived by luck.
    entry: >-
      BC-203 is terminal; T-017's rungs and their margins are retained; BC-191's default
      rationalisation scale is decided and recorded.
    exit: >-
      Per rung, either a retained certificate with both routes agreeing or a refuted rung
      with its restricted optimum and its rationalisation loss; and, when rule one fired,
      the n = 21 continuation's rungs reported on the same terms.
    bead: think-ndp3
    workflows: [research-loop]
    depends_on: [BC-203]
    parallel_group: agenda022-lane-c
    program: grid-frontier-exact-values
    artifacts:
    - packing/campaign/series/series-000-smoke-and-calibration/results/bc-206-n12-ladder-register.txt
    outcomes:
    - scope: >-
        The four pre-registered sides of the n = 12 ladder above 99/25, on two
        constructions each, and how far the ladder reaches below 4B.
      classification: achieved
      result: >-
        The ladder does not climb. All eight pre-registered runs refute and nothing was
        frozen as a candidate: at 397/100 the grid converged at round 26 to 12.364038 and
        the seeded set crossed twelve at round 8; at 398/100, 3985/1000 and 399/100 the
        grid locked at exactly 16.000000 from rounds 5, 6 and 7 while the seeded sets
        crossed at rounds 5, 3 and 3. Each refutes a site set rather than a side.
        The cell's own warning about margin non-monotonicity did not materialise -- the
        crossings arrive strictly earlier as the side rises, 8, 5, 3, 3 -- so whatever
        reopens the margin below 99/25 does not operate above it.
        The 16.000000 is BC-197's 25.000000 one order down and has the same mechanism:
        with delta = 4B - L, a support missing all three windows [L - (4 - k)B, kB]
        admits sixteen dual-feasible unit weights whatever the covering value is, and the
        auto grid places 43 to 44 sites per axis where those windows need 191, 369, 687
        and 4988. The register now carries that artefact signature at two orders, which
        makes it a property of the construction rather than a coincidence at one size.
        Five unregistered follow-up runs at 397/100 answer the question the cell was for.
        A widened column step converged the column loop at 12.314708 over 830 orbits,
        reproduced from a different start to eleven figures; run_fractional_cutting
        converged its row LP at 12.248227 and returned an exact floor of 10.845594. So
        10.845594 <= nu*(3.97) <= 12.248227, and against the retained 11.998960 at 3.96
        the upper end gives a slope of at least 24.9 per unit side. The retained rung's
        0.001040 of margin is spent within 0.000042 of side: the ladder ends at about
        3.96004, and the 0.0308 of runway T-017 recorded under 4B = 3.9908 is not runway.
        The covering value binds and the ceiling never gets the chance, which is the same
        shape BC-197 found at m = 5 and the second time this project has measured that
        difference. Two cases is not a rate and is not offered as one; it is enough to say
        a runway figure computed from the ceiling is an upper bound on an upper bound.
        Twelve lies inside the bracket at 3.97, so that side is undecided rather than
        barred, and every refutation here is of a site set.
        Rationalisation never fired the kill: three freezes lost 0.000091, 0.000088 and
        0.000083 at scale 4,000,000, about 0.58 of the atoms-over-scale bound each. At
        2097 atoms that scale bounds the loss at 0.000524 against 0.001040 of margin,
        where the old 200,000 bounded it at 0.010485 -- ten times the margin, and it would
        have fired on every rung.
        Three instrument findings are in the register. `kill` on a uv wrapper does not
        reach its python child, which let a converged run write a freeze into the case
        package before it was moved out; the ceiling instrument is split so that
        run_fractional_colgen calls check_ceiling without taking --support-cap while
        colgen_checkpoint takes --support-cap and never calls check_ceiling, which is why
        one run reported a floor of 8.50 under an LP holding 12.31 with nothing saying the
        dual had been truncated; and the column loop's stopping rule halted at 12.314708
        where the cutting loop with more sites reached a converged 12.248227 below it.
        No round is registered for this cell and that is a defect in the cell rather than
        in the work: it declares purpose research with no hypotheses, and the experiment
        contract requires at least one, so it could not produce a registrable round. The
        measurements are retained as nine covering-value register rows and the run
        register instead, which is what they are -- data, not a test of a claim made in
        advance. Recorded as D-460.
      evidence:
      - packing/campaign/series/series-000-smoke-and-calibration/results/bc-206-n12-ladder-register.txt
      - packing/frontier/covering-values.yaml
      disposition: retire-success
      follow_up: null
    next_evidence: >-
      How close to the ceiling the ladder actually reaches at m = 4, which is the only
      direct measurement anywhere of the gap between the covering value and the ceiling.
  - id: BC-207
    purpose: research
    owner_focus: insight
    instances: [11]
    state: blocked
    priority: 2
    question: >-
      At the side block one found the n = 11 wall, does an exact cover of the heavy atoms
      by eleven disjoint cores exist -- and if none does, no packing exists there even
      though the mass reaches eleven?
    budget: >-
      140 elapsed minutes, Fable at maximum thinking, research-loop, on lane core 2 after
      BC-208. This is X-014's Corollary 1a and it opens only if block one found a wall.
      The statement. The cores are disjoint closed sets and the atoms outside all of them
      weigh at most epsilon together, so every atom heavier than epsilon lies in exactly
      one core; the heavy atoms are partitioned into eleven groups, each inside a
      B-square at a net direction or a D4 image of one, each core weighing at most
      1 + epsilon in all, and the cores' enclosing unit squares pairwise interior-disjoint
      inside the container. If no such partition exists, no packing exists at that side
      even though the mass reaches eleven -- which is the one configuration T-018 records
      as closable by neither pre-registered route.
      The skeleton is not the whole atom set, and the retained 381/100 certificate gives
      the scale: 1121 atoms with weights from 3/40000 to 917/6250, of which 649 weigh more
      than 1/200 and carry 9.97 of its 10.863675 units, 289 weigh more than 1/100 and
      carry 7.02, and 93 weigh more than 1/50 and carry 4.28. A mass gap of a few
      thousandths -- the size the rationalisation step alone introduces -- forces every
      atom of the heavy skeleton into a core and leaves the light ones free.
      The condition that must be used is the stronger one. Disjointness of the unit
      squares, not of the cores: eleven disjoint cores alone would say only that eleven
      B-squares fit, which at 3.82 gives s(11) at most 3.8288 and is not known to be
      false. Each assignment therefore carries a semialgebraic feasibility check in the
      free centres and angles, so the question is decidable rather than purely
      combinatorial and the cost is the assignment count times that check.
      The measure may be chosen for the purpose, and should be. Lemma 1 holds for any
      measure satisfying the covering condition, not only the one the search minimised, so
      maximise the least slack outside a neighbourhood of the record's own eleven
      placements and their images subject to a total mass of at most 11 + epsilon. That is
      another linear program, and a measure that is tight everywhere constrains nothing.
      Kill: the assignment count passing 1e5 inside this cell's wall, or BC-201's census
      reporting a fat tight set, in which case the cell does not open at all.
    entry: >-
      Block one found a wall at n = 11 -- BC-200 confirmed H-064, or its bracket named a
      side -- and BC-201's census says the tight set is enumerable; BC-208 is terminal so
      the class cuts are available to prune the assignments.
    exit: >-
      Either an exact-cover refutation at the wall side with its assignment count and its
      retained feasibility checks, or the count that turned it into a search and the cell
      stopped with that count recorded.
    bead: think-0mro
    workflows: [research-loop]
    depends_on: [BC-203, BC-208]
    blocked_on: >-
      BC-208's class cuts, and a wall at n = 11 for the cover to sit at. BC-200 found no
      wall: the cutting-plane loop stalled below eleven at both 3.82 and 3.85, so the
      side this cell would work at is still unmeasured.
    parallel_group: agenda022-lane-b
    program: n11-closure
    next_evidence: >-
      Whether the mass gap is a case analysis a computer can finish, which is the last of
      the three unknowns X-014's verdict names.
  - id: BC-208
    purpose: research
    owner_focus: insight
    instances: [11]
    state: blocked
    priority: 1
    question: >-
      Does the class-certificate program deliver two statements about n = 11 that stand on
      their own -- Gardner's conjecture with the class widened, and a composition count?
    hypotheses: [H-063]
    budget: >-
      150 elapsed minutes, Fable at maximum thinking, research-loop, on lane core 2.
      Theorem one, Gardner with margin. The near-{0, 45} class -- the two end half-gap
      cells of the retained net, half-width 0.131848 degrees at the axis-parallel end --
      certified above Trump's 3.877084 for the composition (n0, n1) = (11, 0). Stromquist's
      Theorem 3 settles Gardner at 2 + (4/3)sqrt(2) = 3.885618 for the exact two-direction
      class, by a further box step this program does not have; what a first-party class
      certificate adds is the widening from two angles to two cells, which covers
      strictly more packings than Stromquist's statement does, and the widening rather
      than the number is the result.
      Theorem two, the composition count. Every packing of eleven unit squares at a side
      below Trump's has at least k squares tilted beyond a declared near-axis class. The
      classical nine-point argument gives k = 2 for every near-axis class inside the tilts
      below theta0 -- at 3877/1000 that is the first six cells of the net, upper boundary
      1.450253 degrees, inside theta0 = 1.706162 degrees -- and the class program is asked
      whether it raises k for the wider nineteen-cell class of half-width 4.875441
      degrees. Trump's packing has five squares at 40.181937 degrees, so k is at most five
      for any class not containing that tilt, and [2, 5] is the interval this theorem
      narrows.
      Twelve class LPs, one per composition n1 = 0 through 11, at a rational side just
      above Trump's, using the program BC-198 froze with both its controls passing.
      The gate is inside this cell's budget and is not optional. A class certificate is a
      two-threshold object that devtools.decide_certificate does not yet decide: either
      the gate is extended to read w0 and w1 from the frozen bytes and decide both
      thresholds by both routes, or nothing here is retained and both theorems stay
      unregistered.
      Kill, and it is X-014's own: the n1 = 0 class failing to certify above Trump's side.
      Conditioning on direction then buys too little and the composition step is dropped.
    entry: >-
      BC-203 is terminal and agenda-021's BC-198 delivered a frozen class program with
      the nine-point control returning at most nine and the {0, 45} control certifying at
      or above 3.877084.
    exit: >-
      Either two registered class statements with frozen bytes decided by both routes and
      each claim boundary written -- what the class covers, what it does not, and that no
      class certificate moves s(11) on its own -- or the composition at which the program
      stopped and the value it returned.
    bead: think-7nxe
    workflows: [research-loop]
    depends_on: [BC-203]
    blocked_on: >-
      Agenda-021's BC-198, which never opened: the class-certificate program and its two
      controls are what this cell's twelve LPs run on, and the rate limit that ended
      that block reached BC-198 before any command did.
    parallel_group: agenda022-lane-b
    program: n11-closure
    next_evidence: >-
      How much of the composition tree closes above Trump's side, which is the coarse tier
      of X-014's proof shape and what decides whether the tree is finite in practice
      rather than only in principle.
  - id: BC-209
    purpose: research
    owner_focus: correctness
    instances: [11, 26, 38, 39, 51]
    state: blocked
    priority: 2
    question: >-
      With row generation priced and one point outside the 3.8-to-4.8 band in hand, which
      reach-table sizes are affordable, and does the attainment ratio hold there?
    budget: >-
      170 elapsed minutes, Opus at maximum thinking, research-loop, on lane core 3 after
      BC-206.
      The candidates and their prices, from the reach table and X-013's cost accounting:
      n = 38 at a predicted side of 6.5883, n = 39 at 6.6901 and n = 51 at 7.5644, against
      the n = 26 at 5.5218 that agenda-021's BC-202 attempted. By the area heuristic those
      are 1.88, 1.94 and 2.48 times n = 20's 2260 atoms, so roughly 4260, 4390 and 5610 --
      and the heuristic's own spread across the four retained certificates is 2.4-fold, so
      the numbers are an ordering rather than an estimate.
      Two corrections to X-013's own table are carried here so they are not re-derived.
      Its gate-time column was computed from the Fraction sweep and must be divided by
      roughly a hundred. And the gate was never the dominant cost of a run: row
      generation is 79 to 94 per cent of every measured round, and BC-191 is what priced
      it against the container side.
      Under BC-203's second doubling-down rule this cell is retargeted instead at n = 11
      rungs above 381/100, at the sides BC-200's bracket left open. The sides, either
      way, are registered before any command runs and named in the launch record.
      The stop rule is X-013's own falsifier and it is pre-registered rather than decided
      after the number arrives: a converged run whose attainment ratio lands well below
      the 0.98171-to-0.98270 band -- below 0.90 -- is direct evidence the band does not
      survive outside the narrow window it was measured in, and the recorded response is
      to abandon reach-table climbing in favour of the cases already proven to respond.
    entry: >-
      BC-206 is terminal so the lane core is free; BC-191's cost-per-round rule and
      BC-202's converged or time-limited point are in hand; BC-203's second rule has been
      evaluated one way or the other.
    exit: >-
      Per attempted size, either a retained certificate or a measured negative with the
      restricted optimum reached, the cost per round against the price, and -- only where
      the loop converged -- the attainment ratio against that size's best known packing.
    bead: think-4in0
    workflows: [research-loop]
    depends_on: [BC-203, BC-206]
    blocked_on: >-
      BC-206, and a priced target. BC-202's run at 138/25 reached 26.464317 on its site
      set without converging its column loop, so the reach table's next size is not yet
      costed from a converged point.
    parallel_group: agenda022-lane-c
    program: reach-table-ladder
    next_evidence: >-
      Whether the reach table is a work queue or only a ranking, which is the question
      X-013 raised and deliberately declined to answer.
  - id: BC-210
    purpose: tool_validation
    owner_focus: process
    instances: [11, 12, 13, 21, 26]
    state: blocked
    priority: 3
    question: >-
      What did the conditional route cost and what did it buy, and does the endgame have a
      next block or a written reason that it does not?
    budget: >-
      60 elapsed minutes from minute 300, review-planning-oversight, coordinator only.
      OR-11's four steps as usual, and three questions this closeout owns specifically.
      Whether the domain generalisation earned its 180 minutes, measured against what
      BC-205 and BC-207 actually closed with it rather than against what it enabled in
      principle. Which of BC-203's four doubling-down rules fired and whether the
      allocation they forced was the one the block's outcomes justify in hindsight --
      recorded as a note on the rules themselves, since they were written before block one
      ran and their calibration is now testable. And the exhaustive tier's budget again,
      since a conditional certificate at a doubled net is the largest decision object the
      tier has ever been asked to hold.
      A negative outcome here is a real outcome. If the conditional route is rejected on
      BC-205's kill, the honest closeout says so, retires the lead as a bounded negative,
      and selects from the ladder candidates instead.
    entry: >-
      BC-204 through BC-209 and BC-212 are terminal or explicitly stopped.
    exit: >-
      Per-block outcomes and stop reasons; a measured verdict on the domain
      generalisation; a calibration note on BC-203's three rules; a decision on the
      exhaustive tier; documentation decisions; validation receipts; ranked candidates;
      and one selected next entry, published without being executed here.
    bead: think-u066
    workflows: [review-planning-oversight]
    depends_on: [BC-203, BC-204, BC-205, BC-206, BC-207, BC-208, BC-209, BC-212]
    next_evidence: >-
      Whether the endgame at n = 11 is a research programme or a closed door, which is the
      question X-014 raised and which two blocks of measurement would finally have priced.
---
# Agenda 022 — The Conditional Route

## Workflow Entry Point

This agenda is paused, and every cell in it is `blocked` on one thing:
[agenda-021](agenda-021-three-numbers-and-a-wall.md)’s closeout `BC-203`. Nothing here
is takeable until that closeout has run, evaluated its four doubling-down rules against
block one’s measured numbers, and named which lanes below open — with two exceptions
that depend on no rule and that a ten-hour pass enters as soon as `BC-203` is written:
`BC-206`, the `n = 12` ladder, and `BC-208`, the class theorems, the latter only if
`BC-198`’s controls passed.

That is not caution for its own sake.
Two of the three lanes here are expensive, and both would be built on premises block one
is measuring: the conditional route costs 180 minutes of pipeline work before a single
case is closed, and it is worth nothing if `BC-199`’s isolation radius is too small for
any tree to reach; the class theorems are cheap only because `BC-198` will already have
frozen the program they need.

Every research cell here carries the `program` slug its block-one predecessor carries —
`grid-frontier-exact-values`, `n11-closure` or `reach-table-ladder`, the three programs
[X-015](../explorations/X-015-the-map-and-the-three-programs.md) ranks — so the agenda
map shows each line of work whole across the two agendas rather than leaving its open
frontier to be reconstructed by hand.

## What block one has to deliver

Written as a checklist, because the entry condition of every cell here is a fact block
one either establishes or does not.

| From | What this agenda consumes |
| --- | --- |
| `BC-197` | The `m = 5` wall, bracketed to at most `0.015`, and whether it is the covering value’s or the ceiling’s |
| `BC-198` | A frozen class-certificate program with both controls passing — the near-axis class at or below `9`, the `{0°, 45°}` class at or above `3.877084` |
| `BC-199` | `ρ₀` and `C` as exact rationals, and whether `ρ₀` cleared `10⁻⁶` |
| `BC-200` | Whether the `n = 11` covering value reaches eleven at `3.82` or `3.85`, and where the ladder’s top now sits |
| `BC-201` | The near-tight census, and whether Corollary 1a’s exact cover is a check or a search |
| `BC-202` | A converged or time-limited covering-value point at `138/25`, and the cost per round there |
| `BC-211` | Whether the `n = 13` covering value at `399/100` converges below thirteen, which reorders Lane A |
| `BC-203` | Which two leads open, and whether Lane A builds the conditional route or the `B = 1` route |

## Why the conditional route goes second, and what it costs

`X-014` puts three lemmas on the table and they are not equally priced, which is the
whole reason this block is separate from the last one.

**Lemma 3 is a threshold change.** Two variables, one normalisation row, class
membership decided by which half-gap cell holds a direction.
No geometry moves. That is `BC-198` in block one and `BC-208` here.

**Lemma 2 is a geometry change**, and the inventory `X-014` ran is specific: there is no
admissibility hook in `sqpack.fractional` at all.
The admissible centre domain is hard-coded as the rotated container square in
`sweep.centre_domain`, again in the float mirror in `generate.py`, and again in the four
half-planes `interval.DirectionSearch` propagates; each of the three assumes that domain
is convex, which a container minus an excluded region is not, and the column generator
routes its oracle through the second.
On top of that the net doubles, because a box breaks the container’s `D4` symmetry and
`Condition 1` can no longer fold angles onto the shorter arc.

So the order is forced: test whether conditioning buys anything on the route that costs
nothing structural, and only then pay for the route that does.
`BC-205` is the calibration that decides whether the payment was worth it, and its kill
condition is stated before the run — Bentz’s case still returning mass at or above
thirteen means conditioning cannot close a case the classical method closes by hand.

## The wall accounting

`360` elapsed minutes, three research lanes on three cores, the closeout at `300`. The
lane that stays shut releases its core to the other two, and the closeout records that
reallocation rather than leaving it implicit.

| Clock | Lane A (core 1) | Lane B (core 2) | Lane C (core 3) | Coordinator |
| --- | --- | --- | --- | --- |
| `00:00–00:10` | — | — | — | wall start, continuity trigger armed, dispatch |
| `00:10–02:40` | `BC-204` domain, or `BC-212` under rule four | `BC-208` class theorems | `BC-206` `n = 12` ladder | integration checkpoint at `03:00` |
| `02:40–05:00` | `BC-204` or `BC-212` ends `03:10`; `BC-205` from `03:10` | `BC-207` exact cover from `02:40` | `BC-209` reach rungs from `02:10` | — |
| `05:00–06:00` | freeze | freeze | freeze | `BC-210` closeout |

Cell budgets sum to the lane: `BC-204` 180 (or `BC-212` 180 in its place) and `BC-205`
110; `BC-208` 150 and `BC-207` 140; `BC-206` 120 and `BC-209` 170. The core budget, the
serialised retention gate and the `OR-3` rule about gates are agenda-021’s and carry
over unchanged.

## The three routes and how two get picked

`BC-203`’s rules are conditions on measured outcomes, and they were written before block
one opened so that the closeout reads them rather than argues them.
Restated here as allocations:

1. **The `m = 5` wall lands within `0.02` of five.** The covering value never binds
   before the ceiling does at `m = 5`, so the ladder has nothing left there and the
   endgame is where the work is: `BC-204` and `BC-205` open, with `BC-206` carrying the
   `n = 21` continuation as its second leg.
2. **The `n = 11` covering value is below eleven at `3.85`.** The ladder is not blocked
   where `X-014` assumed, so the cheapest remaining movement of the smallest open case
   is more rungs: `BC-209` retargets at `n = 11` above `381/100`, `BC-206` takes the
   second rung lane, and `BC-207` defers because there is no wall for it to sit at.
3. **`ρ₀` comes out below `10⁻⁶`.** The tree is dropped and the radius is kept as a
   theorem: no conditional lead opens against Trump’s pose, `BC-204` and `BC-207` stay
   shut, the leads go to `BC-206`, `BC-208` and `BC-209`, and the radius goes to
   agenda-018’s `BC-176` and `BC-177` as the packet and its review.
4. **The `n = 13` covering value at `399/100` converges below thirteen.** The `m = 4`
   endgame is one certificate’s shrink tax away, so Lane A builds `BC-212`, the `B = 1`
   route over the direction continuum, in `BC-204`’s place, and `BC-205` calibrates on
   it at side exactly `4`; the conditional route waits for block three.

Rules one and two can both fire.
Rule three overrides the endgame half of rule one, because a conditional certificate
aimed at Trump’s pose has nothing to hand off to when the local box is unreachable.
Rule four reorders Lane A without closing any lead.

## What does not change

**Retention.** Freeze, decide the frozen bytes through `devtools.decide_certificate`,
retain only when both routes accept and agree on the value.
Three cells here extend what the gate reads — `BC-204` adds the box and the doubled net,
`BC-212` adds `B = 1` and the continuum decision, `BC-208` adds the two class thresholds
— and all three extend it in the same direction: more of the object inside the frozen
bytes, decided by both routes.
Neither relaxes the rule, and a cell that cannot extend the gate inside its budget
retains nothing.

**A negative is a result.** `BC-205`’s kill, `BC-207`’s assignment-count cap and
`BC-208`’s `n₁ = 0` failure are each written before the run with the number that would
fire them, and `BC-210` classifies whichever fires as a bounded negative with a
disposition rather than as an unfinished lane.

**A self-declared budget is not a stop condition.** `OR-8` applies to this block exactly
as to the last: minute `360` is the end of an estimate, and the recurring continuity
trigger armed at minute `10` is not deleted without the operator asking.

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
