---
title: "agenda-023 — efficiency block: the gate itself"
softschema:
  contract: packing.squares:ExperimentAgenda/v1
  schema: ../schemas/agenda.schema.yaml
  envelope: agenda
  status: enforced
agenda:
  id: agenda-023
  title: "Efficiency Block — the Gate Itself"
  updated: '2026-09-05'
  status: active
  objective: >-
    A W5 efficiency-loop block entered on the operator's direction, on the one instrument
    every change pays for: the gate. CI's pull-request surface costs 22 to 23 minutes and
    taxes every push by that much, which is the operator's objection and the reason this
    block exists.
    All four things W5 asks for at entry are on record before any change is made.
    BASELINE: run 33982455466 on 2026-09-05 ran packing-validate --fast --jobs 2
    --inner-jobs 1 in 1369.60 s of wall, and validate.py's own budget comment records the
    same tier at 499 s measured on 2026-08-30 -- a 2.65x regression in six days against a
    1800 s cap the tier now fills to 76 per cent.
    PROFILE: the tier is one step. `fast behavioral tests` is 1324 s of that 1369.60 s,
    96.7 per cent of wall; every other step in the tier together is about 45 s. The
    --edit tier, which is every floor and every record check but not the broad suite,
    measures 59.35 s on a contended four-core box.
    TARGET: the operator's own figure -- a pull-request-blocking surface of at most four
    minutes, deeper validation moved to a workflow that does not block a pull request,
    and expensive work not re-run when its inputs have not changed.
    GUARD: no check is deleted and none becomes optional. Every step that leaves the
    pull-request surface runs in the deep workflow on main and on a schedule, and the
    `broad` and `touches` fields already on Step, with
    test_the_edit_tier_cannot_under_run behind them, are what keep the split honest
    rather than convenient.
    The block's third cell is the part the operator asked for explicitly and the part
    that outlives it: a declared ceiling the gate itself enforces, so the next tier
    regression is caught by a failing check in the week it lands rather than by someone
    noticing that a wait got long. A block that only fixes today's number would leave the
    same hole open.
  items:
  - id: BC-214
    purpose: tool_validation
    owner_focus: efficiency
    instances: [11, 12, 17, 20]
    state: ready
    priority: 0
    question: >-
      Can the pull-request surface be brought under four minutes without deleting a
      check, by moving the broad behavioural suite and the exhaustive tier into a
      workflow that does not block a pull request?
    budget: >-
      90 elapsed minutes, efficiency-loop. The tiers already exist and are correctly
      shaped -- --records, --edit, --fast, --push scoped by --since, and the full gate --
      so this is a workflow-wiring change and a measurement, not a redesign of
      packing-validate.
      The measured facts to work from: --edit is 59.35 s locally and covers every floor
      and every record check; `fast behavioral tests` is 96.7 per cent of the --fast
      tier's wall; CI's push-to-main job already runs the complete integration surface.
      Report both numbers after the change, on CI's own two-core runner and not locally,
      because the target is stated in CI wall.
      The trade-off is real and is to be stated rather than smoothed over: a
      pull-request surface without the behavioural suite can be green while a behavioural
      test is broken. Today's evidence is exactly that -- CI's behavioural step caught
      eight real failures on this branch that no floor or record check would have found.
      So the cell reports what the split would have missed today, and the operator decides
      whether the deep workflow must also pass before a merge.
      Kill: any change that makes a check optional rather than moving it, or that leaves
      a step in neither surface.
    entry: >-
      The baseline, profile, target and guard above are on record; the tier flags exist
      and are documented in development.md's validation loops.
    exit: >-
      A pull-request surface measured under four minutes on CI's own runner, a deep
      workflow carrying everything that left it, both wired and both green, and a written
      statement of what the pull-request surface can no longer catch.
    bead: think-doar
    workflows: [efficiency-loop]
    depends_on: []
    parallel_group: agenda023-gate
    program: gate-cost
    next_evidence: >-
      What a change actually costs to land, which is the tax every other block in this
      campaign pays and the only one paid on every commit rather than once.
  - id: BC-215
    purpose: tool_validation
    owner_focus: efficiency
    instances: [11, 20]
    state: blocked
    priority: 1
    question: >-
      Which expensive gate steps re-run when nothing they depend on has changed, and what
      does skipping those cost in coverage?
    budget: >-
      90 elapsed minutes, efficiency-loop, after BC-214. Step already carries `touches`,
      a tuple of the paths a step depends on, and --push already selects tests reachable
      from a change against --since. The machinery exists; what is missing is CI using
      it, and a measurement of how often a full run repeats work whose inputs are
      identical to the last green run.
      Two things are in scope and one is not. In scope: skipping a step whose `touches`
      set is untouched since the last green run on the same base, and caching what is
      genuinely content-addressed -- the uv environment, the exhaustive tier's decided
      certificates, which are frozen bytes and cannot change without their sha256
      changing. Not in scope: caching anything whose inputs the record does not pin,
      because a stale cache that reports green is worse than a slow gate, and this
      project has a defect class for exactly that shape.
      Kill: any skip rule that cannot name the inputs it watched, or that would have
      skipped a step which caught a real failure in the last thirty days.
    entry: >-
      BC-214 is terminal, so the two surfaces exist and it is clear which one each step
      belongs to.
    exit: >-
      A measured count of repeated work in the deep workflow, a skip or cache rule for
      each case it is safe for with the inputs it watches named, and the cases where it
      is not safe with the reason.
    bead: think-xejq
    workflows: [efficiency-loop]
    blocked_on: >-
      BC-214, which decides which surface each step belongs to. Skipping work before the
      two surfaces exist would be optimising a shape about to change.
    depends_on: [BC-214]
    parallel_group: agenda023-gate
    program: gate-cost
    next_evidence: >-
      Whether the deep tier can run often enough to be a backstop rather than a nightly
      surprise, which is what decides how much the pull-request surface is allowed to
      miss.
  - id: BC-216
    purpose: tool_validation
    owner_focus: process
    instances: [11]
    state: ready
    priority: 0
    question: >-
      What check would have caught the 499 s to 1370 s regression in the week it
      happened, and does it hold when deliberately regressed?
    budget: >-
      60 elapsed minutes, efficiency-loop, in parallel with BC-214. This is the cell the
      operator asked for by name: the block must define the process so this cannot recur,
      and a fix that only restores today's number leaves the same hole open.
      What went wrong is not that the tier got slow. It is that the tier got slow against
      a baseline written down in a docstring, where nothing reads it -- validate.py
      records 499 s in prose beside a 1800 s cap, and the tier tripled inside the cap
      without any check objecting. A number a machine does not read is a number that
      drifts.
      The shape to build: the declared ceiling for each tier becomes data the gate reads,
      each run records its own wall against it, and a run that exceeds the ceiling fails
      with the step that spent the time named. Two negative controls, since this is a
      detector: a deliberately slowed step must fail the check, and a run inside the
      ceiling must pass without a manual figure anywhere in the assertion.
      Add the standing measurement to the efficiency block's own definition, so the next
      efficiency block starts by reading this number rather than by rediscovering it, and
      say in development.md which tier a contributor and CI each run and what each costs.
      Kill: a ceiling expressed as a hand-written constant that a person must remember to
      update, which is the failure being fixed rather than a fix for it.
    entry: >-
      The baseline and profile above are on record and reproducible from CI's own run
      logs.
    exit: >-
      A ceiling per tier that the gate enforces, both negative controls passing, the
      standing measurement written into the efficiency block's definition, and
      development.md stating which tier runs where and at what cost.
    bead: think-gy30
    workflows: [efficiency-loop, process-review]
    depends_on: []
    parallel_group: agenda023-gate
    program: gate-cost
    next_evidence: >-
      Whether this campaign can hold a cost target it has written down, which every
      efficiency block so far has assumed rather than checked.
  - id: BC-217
    purpose: tool_validation
    owner_focus: process
    instances: [11]
    state: blocked
    priority: 1
    question: >-
      Can the records gate certify that the full gate actually ran on the commit a block
      handed over, so a terminal session that cannot name one is refused?
    budget: >-
      60 elapsed minutes, process-review, after BC-214 has settled what the three
      surfaces are. OR-13 states the rule; this cell is what makes it a rule rather than
      an intention.
      The shape: a terminal AgentSession names its full-gate run in `checks` -- the tier,
      the commit it ran on, and the verdict -- and packing-ledger refuses a terminal
      session that cannot. The commit matters as much as the verdict: a full gate run on
      a tree three commits behind the handover certifies nothing about what was handed
      over, and a check that accepts a bare "full gate: passed" is a check that will
      accept exactly that.
      Two negative controls, since this is a detector: a terminal session with no
      full-gate entry must be refused, and one naming a commit that is not an ancestor of
      the session's own branch head must be refused too.
      The rule applies from its own introduction forward and not retrospectively: the 87
      sessions already terminal were closed under a contract that did not ask for this,
      and rewriting their records to satisfy a later rule would be the record disagreeing
      with what happened. The checker names its start date and says so.
      Kill: any design that makes the entry free-text a person composes, since that is a
      check on prose rather than on whether the gate ran.
    entry: >-
      OR-13 is recorded and mirrored in AGENTS.md; BC-214 is terminal so the tiers the
      entry names are stable.
    exit: >-
      A records-gate check refusing a terminal session that cannot name a full-gate run
      on an ancestor of its own head, both negative controls firing, and the rule's start
      date recorded so the existing corpus is not retrospectively invalid.
    bead: think-cdf0
    workflows: [process-review]
    blocked_on: >-
      BC-214, which decides what the full gate is once the surfaces are split. Certifying
      a tier before its definition settles would pin the wrong name.
    depends_on: [BC-214]
    parallel_group: agenda023-gate
    program: gate-cost
    next_evidence: >-
      Whether a handover can be trusted without re-running the gate to find out, which is
      what every reviewer of every block in this campaign has had to take on faith.
  - id: BC-218
    purpose: tool_validation
    owner_focus: efficiency
    instances: [11, 20]
    state: ready
    priority: 0
    question: >-
      How much of the gate's remaining wall is sequencing rather than work, and what does
      it cost to run the surfaces as parallel GitHub Actions jobs instead of one runner?
    budget: >-
      90 elapsed minutes, efficiency-loop, on the operator's direction: use more
      parallelism on GitHub Actions wherever it would help.
      The measured starting point is BC-214's, and it is the reason this cell is worth
      opening rather than declaring victory at 409 s. That figure is one job on one
      two-core runner running every step in sequence, and the tier is no longer dominated
      by a single step now that the slow lane has left it -- so what remains is a set of
      steps whose costs are comparable and which mostly do not depend on each other. A
      sequential runner pays their sum; parallel jobs pay their maximum plus the setup
      each one repeats.
      Three shapes to price rather than assume, because the trade is real in both
      directions. Separate jobs each repeat checkout, uv install and `uv sync`, which
      measured about 12 s together on the two-core runner, so a job worth splitting out
      has to cost more than that. A matrix over the deep lanes buys the most where the
      exhaustive tier is, since it is the one surface whose steps are genuinely
      independent decisions. And within a job, `--jobs` and `--inner-jobs` are already
      the knobs `packing-validate` exposes; whether a larger runner beats more jobs is a
      measurement nobody here has taken.
      What must not change: `packing-required` stays the single required context, since
      D-380 records what a fan-out of required checks did to this repository once, and
      every step must still land in exactly one surface with `test_every_step_is_reachable_from_some_tier`
      still passing.
      Kill: any split that makes the pull-request surface's *sum* of billed runner
      minutes more than double, since wall time bought with unbounded cost is not a
      trade this project has agreed to.
    entry: >-
      BC-214 has priced the pull-request surface at 409 s on the two-core runner and the
      slow lane has left it, so what remains is comparable steps rather than one dominant
      one.
    exit: >-
      A measured comparison of the sequential surface against at least one parallel
      shape, on CI's own runners and not locally; the billed-minutes cost of each beside
      its wall; and either a wired split with both numbers recorded or a statement of why
      the sequencing was not the cost.
    bead: think-m5ev
    workflows: [efficiency-loop]
    depends_on: []
    parallel_group: agenda023-gate
    program: gate-cost
    next_evidence: >-
      Whether the four-minute target is reachable without deferring anything further,
      which decides whether the coverage policy in OR-13 costs anything at all.
---
# agenda-023 — Efficiency Block: the Gate Itself

Every other block in this campaign measures an instrument that runs when someone asks
for it. This one measures the instrument that runs whether or not anyone asks: the gate,
paid on every push, by every change, forever.

## Why this block exists

The operator’s objection, in their own terms: 21 minutes of CI is a tax on all
development, CI should be two to four minutes, and deeper validation belongs in another
workflow.
Then, sharper: *we should not be rerunning things that have not changed if they
are expensive*. And then the part that makes this a block rather than a fix: *this
should never happen again if we are regularly scheduling efficiency workflow blocks.*

## What actually happened

`validate.py` carries its own baseline in a docstring:

> Measured on 2026-08-30: `--fast` is 499s and `fast behavioral tests` is 499s of it, so
> the other seventeen fast steps together cost about 48 seconds.

Six days later the same tier ran 1369.60 s. Nothing objected, because the cap is 1800 s
and 1370 is inside it, and because 499 is prose.
**A number a machine does not read is a number that drifts** — and the drift is 2.65x on
the one command every contributor and every CI run pays for.

The tiers themselves are not the problem and are not being redesigned.
`--records`, `--edit`, `--fast`, `--push` scoped by `--since`, and the full gate are the
right five, and `Step.broad` with `test_the_edit_tier_cannot_under_run` behind it is the
right mechanism.
What drifted is which tier CI runs on a pull request, and the absence of
anything that would notice.

## The trade this block must not hide

`--edit` is 59 s and catches every floor and every record check.
It catches no behavioural test.
On this branch today, CI’s behavioural step caught eight real failures — a stale
constant in the witness walk, four reach-table controls, three `n = 20` rung tests — and
not one of them would have been caught by a floor or a record check.

So moving the behavioural suite off the pull-request surface is not free, and `BC-214`
reports what the split would have missed today rather than presenting the speed-up
alone. Whether the deep workflow must also pass before a merge is the operator’s
decision, and the cell puts it to them with the number attached.

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
