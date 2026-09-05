# Operating Rules

**How the work is done here**, as against `conventions.md`, which governs the shape of
what is produced. Each rule below is here because it was broken and cost something; the
citation is the argument.
[`AGENTS.md`](AGENTS.md) carries a generated one-line summary, since it is the only file
guaranteed to be in context before the first tool call.
Add a rule here, then run `devtools.render_operating_rules`.

## OR-1: Build the tool; never leave a measurement in one-off code

A `python -c`, a heredoc, or a throwaway script means the tool is missing.
Write it into `devtools/` with the guard that makes its answer refusable; if it needs a
design, open a [W7 pipeline-improvement](README.md#workflow-entry-points) session rather
than improvising inside a research slice.

The cost is wrong numbers, not untidiness.
A heredoc control in [D-023](defects.md) restored its mutation with `git checkout`,
discarding an uncommitted backfill and invalidating two probes.
A script in
[session-043](packing/campaign/agent-sessions/session-043-block9-degree-bound.md)
reported a Bézout bound of `12,690,480` where the answer is `1,039,500`, and it was said
out loud before the guarded tool that refused it existed.

**The rate is measured and nobody reads it.** `ClaudeEfficiencyRollup/v1` has always
counted `one_off_code`, and session-047 is the first to look: 954 of 3416 tool calls,
27.9%, three hours of wall time, 718 of them Python heredocs — in the session that wrote
this paragraph. That number is not a gate and should not become one.
The rule forbids *leaving* a measurement in one-off code, not exploring with it, and a
threshold on heredocs would fail the exploration this repository depends on while
catching none of the actual defect, which is a retained number whose tool does not
exist. It is here because a rule with a number attached is harder to feel exempt from
than one without, and because the rollup can answer this question for any session that
asks.

Three shapes keep recurring, kept here as instances so a W7 session can generalise the
tool from them:

- **Anchored prose replacement:** swapping a multi-paragraph section of `AGENTS.md` for
  another, by `str.index` slicing inside a heredoc.
  An editor tool with a uniqueness guarantee does this directly.
- **Anchored insertion into a structured record:** putting `BC-076` before
  `- id: BC-075` in the agenda, and three control definitions before a named anchor in
  `controls.yaml`. `run_negative_controls` already has the guard this wants, since an
  anchor matching other than exactly once is a refusal rather than a mutation.
- **Coordinated edit under one invariant:** `operating-rules` had to reach the
  document-map schema enum, the map, and `ROLE_LABELS` together or the renderer raises,
  and `count:` in `defects.yaml` has to move with three aggregates in `SYNOPSIS.md`.
  Both were multi-file heredocs whose only check was a later gate step.

## OR-2: Run three to five sub-agents, at a thinking level matched to the task

Read-only investigation and disjoint writes parallelise; shared records, integration,
commits, and external updates stay with the coordinator.
Below three is usually serial work that could have been handed out; above five,
reconciliation costs more than it buys.

Pick the thinking level by difficulty: **extra** for anything carrying a proof
obligation, **max** for the hardest mathematics and review findings.

A sub-agent’s report is evidence, not a verdict.
One in
[session-044](packing/campaign/agent-sessions/session-044-agenda006-continuation.md)
reported that `contacts.py` does not parse; it parses under the project’s Python 3.14,
where [PEP 758](https://peps.python.org/pep-0758/) makes `except A, B:` valid.

**That exact error recurred twice more**, in two independent sub-agents run at maximum
effort on unrelated tasks during
[session-045](packing/campaign/agent-sessions/session-045-agenda008-queue-and-identity.md).
One called it “a hard `SyntaxError` under Python 3.14”, the other “a `SyntaxError` on
every Python 3” across ten named files.
All ten parse. Three for three is not bad luck: `except A, B:` reads as a Python 2 tell
strongly enough to survive being checked, so verify a parse claim by parsing rather than
by reading. The same reports were otherwise excellent, which is the point — a report can
be right about five real defects and confidently wrong about a sixth.

## OR-3: Never wait on a gate with nothing else in flight

Launch it in the background and keep the next slice moving.
Never poll it, and never start one against a tree you are about to change: a gate whose
inputs move underneath it has to be run again, so it spends the eight minutes and buys
nothing.

**Run `packing-validate --records` before a push, and push before the slower checks
finish** so CI runs concurrently with them rather than after them.
The record checks take about four seconds and are the ones that break
([D-369](defects.md)); the behavioural tests take eight minutes and have never broken
here. Serialising local tests and CI pays the longer of the two costs twice.

Four seconds rather than the seventy this rule first recorded, since `BC-077` swapped
the schema validator and moved exact geometry out of the step named for schemas
([D-370](defects.md)). That changes how the rule reads: at seventy seconds running the
record checks was a judgement call, and at four there is no argument for skipping them.

**Use `--edit` while editing.** `BC-079` split it out of `--fast`, which had stopped
being fast at `499s` with one step 94% of it.
`--edit` is 33 seconds and runs everything except that step.
`--fast` is what a block boundary is for, and CI runs the full gate on every push
regardless, so the split moves feedback latency and not coverage.

**The waste this rule names is measured now, and it is the coordinator’s, not the
gate’s.** The evidence is the retained rollup
[`5cd11e53`](packing/campaign/resource-usage/5cd11e53-fb82-4a28-ab2a-0c26f16fe7e5.yaml),
quoted from its own fields: `345.1s` across **four** `.gate-running` polling calls, plus
`245.6s` across three that waited on a test run, against `3187.6s` of wall — **18.5%**
of the session spent watching a gate that was going to finish either way.
Twice the gate was started against a tree that then changed underneath it, and both runs
had to be discarded.

The first version of this paragraph said `233.6s` across three calls and “about 17%”,
read off the transcript rather than the rollup ([D-379](defects.md)). Understating the
waste in the rule that exists to stop it is the wrong direction to be wrong in, and the
rollup is one field lookup away.

## OR-4: Take the next slice from the handoff, not from the backlog

The [current handoff](SYNOPSIS.md#current-handoff) names the active agenda, the next
bounded slice, and the owning bead, and that agenda’s queue owns priority ordering.
`tbd ready` mixes in the historical backlog, so it informs a coordinator checkpoint but
is never the queue.

## OR-5: Declare the workflow entry point before beginning

Independently tracked work picks W1–W10 from
[`README.md`](README.md#workflow-entry-points) before the session or phase starts, with
`general-improvement` reserved for maintenance outside those workflows.
Bounded delegated work inherits the parent phase unless it opens its own tracked
session. [`SYNOPSIS.md`](SYNOPSIS.md#workflow-entry-contracts) owns the full contracts.

## OR-6: Plan multi-hour work in slices before starting it

Unless the user sets another cadence, target an integration checkpoint within about four
hours and cap each slice at 30 minutes, per the
[bounded research cycle](packing/campaign/README.md#the-bounded-research-cycle).
Thirty minutes is a ceiling, not a quota: close a slice as soon as its bounded output is
complete. Replan at each boundary from measured time, and only forward.

## OR-7: Run the documentation guidelines pass at block boundaries

A block that produced a new document, a substantial rewrite, or a long block comment
closes with a `pprose-common-edit` pass; `tbd guidelines common-doc-guidelines` is the
text it applies. The commit hook already handles formatting, so this is the structure,
footer, and de-slop pass, which is the one that never happens on its own.

Once per block, not per file: per file it re-reads the same guidelines for every edit
and churns text that was already conformant, and a block that only touched records or
code has nothing for it to do.

## OR-8: A self-declared budget is not a stop condition

Under an open-ended mandate — “don’t stop”, “run through the night”, “until it is done”
— only three things end a run: the user says so, an external blocker makes progress
impossible, or the work is genuinely exhausted.
Reaching the end of a plan is none of these.
A plan is an estimate the run wrote for itself, and the end of an estimate means it is
time to plan the next slice, not time to stop.

Two devices keep this from being a matter of memory, because memory is what failed.

**The continuity trigger does not depend on being re-armed.** `send_later` is one-shot,
so a chain of re-arms is only as long as the first turn that decides the work is
finished. A recurring trigger fires on its own schedule regardless of what the previous
turn concluded, so a wrong “we are done” is corrected at the next firing rather than
being final. Keep the one-shot chain for fine-grained pings if it helps; the recurring
one is the floor under it.

**Deleting that trigger requires the user to ask.** It is the only irreversible action
in the loop — every other bad call gets another turn to be reconsidered, and this one
does not. Treat it the way any other irreversible action is treated here.

[D-395](defects.md) is a run that had eleven and three-quarter hours of unbroken
20-minute pings, wrote itself a reminder saying “the wall budget is spent … do not start
new work”, and then deleted it.
The clocks were right; the authority was wrong.
[D-358](defects.md) is the same stop, reached by a misread clock instead — which is why
the rule is about what may end a run, not about how to measure time.

## OR-9: A pull request leads with what the branch cost

The reviewer can see what changed.
Nothing on the page said what it took, though harness telemetry existed: Claude records
branch-aware per-log rollups, and Codex can now retain a privacy-reduced additive
task-tree interval declared by an AgentSession.
It was simply never put where the merge decision is made.

So the description of an end-to-end session’s pull request opens with that block, and it
is generated rather than written:

```shell
uv run --frozen --all-extras --group dev python -m devtools.render_pr_rollup
```

For Codex, pass `--session session-NNN`. Codex exposes no Git-branch field, so the
AgentSession declares the interval’s association with the PR and the renderer labels it
operator-recorded rather than harness-observed.
Never render a Codex receipt without that explicit declaration.

**Close the session first.** The block is a function of the rollups, so it is wrong
until they are written — which is why `close_session --render` prints it as its last act
rather than leaving it to a second command.
Close, then paste, then open.

**Never collapse it to one number.** In a Claude record, `turns.by_branch` is the only
branch-aware field, so a log that ran on more than one branch has an exact turn count
and no way to split its tokens or tool calls.
The block prints three columns — on-branch logs only, prorated by turn share, and every
log that touched the branch — of which the outer two are measurements and the middle is
the estimate to quote.
On the branch that introduced this rule the straddling logs carried 5,486 of 8,423
turns, so the interval is not a rounding matter and a single figure would be a guess
wearing a measurement’s clothes.
Codex intervals render in a separate section: their model responses are not Claude
turns, and adding the two harnesses could count the same work twice.
A live Codex snapshot is explicitly a lower bound.

**A multi-block session keeps the pull request current, not just open.** The owner
reviews as the work lands, so a session that runs more than one block opens the pull
request at its first completed block — with a mid-session rollup snapshot standing in
for the terminal one — and refreshes the description and cost block at each block
boundary rather than saving both for the end.
Added 2026-08-31 at the owner’s request, during the session that opened
[PR #64](https://github.com/jlevy/squares/pull/64) this way.

This is `OR-1` applied to the reviewer rather than to the researcher: a measurement that
exists and is not reported is the same waste as one taken and thrown away.

**Cost is the opening, not the whole account.** After the generated cost block, an
agenda PR reports actual results at their honest scope, including an explicit statement
when no mathematical result was obtained.
Every stopped or incomplete block says whether it was a completed bounded-negative
search, time-limited work, a correct guard refusal, a technical failure, never opened,
or inconclusive. It then gives the actionable disposition — continue, fix and rerun,
retire as success, retire as a bounded negative, or defer to a named dependency — and
groups concrete file and interface changes by purpose.
Validation, documentation decisions, limitations, ranked follow-up candidates, and the
one selected next entry follow.
Agenda chronology may support that account; it may not stand in for it.

## OR-10: Treat matched agent and host handoffs as continuation, not a reset

An interrupted session may move between Claude and Codex, or between Linux and macOS,
without invalidating the work merely because the operator or host label changed.
Carry the existing agenda, session, experiment id, checkpoint chain, and wall clock
forward when the frozen scientific inputs, instrument bytes, acceptance criteria, and
guard receipts still match.
Record the handoff honestly; do not manufacture a new round or discard exact work just
to keep a provenance label unchanged.

Match judgment effort across harnesses by task, not by similarly named settings:

- for the hardest mathematics or careful review, Codex **Max** corresponds to Claude
  **Fable**;
- for mechanical work requiring substantial care, Codex **High** or **Extra High**
  corresponds to Claude **Opus Extra High** or **Opus Max**.

This equivalence does not make host-sensitive measurements portable.
Timing, floating-point last bits, nondeterministic search trajectories, or any method
whose criterion names the machine or operator still needs the preregistered regime or a
fresh prospective one.
Exact-algebraic work with a verified hash chain and identical controls may resume across
the bridge; a result whose meaning depends on the bridge may not.

The cost was paid in
[session-078](packing/campaign/agent-sessions/session-078-agenda015-ten-hour-coordinator.md):
an interrupted Linux/Claude exact process was provisionally stopped after recovery on
macOS/Codex even though the parent binding, executable package, checkpoint chain, and
all exact guards still matched.
The owner had to clarify that the matched handoff was part of the same autonomous
session. The rule makes that continuity the default and keeps the exception where it
belongs: in the measurement contract, not in the harness name.

## OR-11: Close an agenda through disposition and reprioritization

A terminal clock does not finish the follow-up work.
Before another candidate agenda starts, W10
[review/planning/oversight](packing/campaign/review-planning-oversight.md) closes the
one that just ran:

1. every agenda item is terminal and every attempted scope has an outcome, stop-reason
   classification, evidence, disposition, and named follow-up when one remains;
2. generated views are refreshed, `SYNOPSIS.md` is reconciled, and README, tutorial,
   conventions, operating rules, and development guidance each receive an explicit
   update-or-current decision;
3. live tbd status and priority are reconciled, retained candidates are ranked, and
   operator input is recorded as confirmed, revised, or unavailable; and
4. exactly one next entry is selected and published without being executed inside the
   closeout.

The mechanical steps run without waiting for an operator.
Operator input can change the ranking or contribute new candidates before execution, but
its absence does not excuse stale views, undocumented files, missing dispositions, or an
unselected handoff. If the review exposes a defect backlog, W9 owns bounded remediation
waves; if it exposes substantive reader-facing drift, W8 owns the documentation pass.

[Agenda 015](packing/campaign/agendas/agenda-015-ten-hour-earned-routes-and-guard-repairs.md)
paid for the rule. Its ten-hour wall closed with useful tools and reviews, one
time-limited exact search, several correct guard refusals, a never-opened fallback, and
a technical publication failure, but the PR initially reduced that outcome to cost and
agenda completion.
The operator then had to ask what actually changed, why the scientific
work did not complete, whether each block should continue, and what had been
reprioritized. Those are not optional questions after the run; W10 makes them the
closeout product.

## OR-12: One block in four to eight is an efficiency block, and the record says which

The cadence is counted in blocks, not in days.
A wall-clock schedule fires when nothing has run and stays silent through a burst, and
this campaign’s activity is bursty by construction — an overnight pass can close six
cells while a quiet week closes none.
So the rule is a ratio: **at least one W5 efficiency block in every four to eight blocks
of any other kind.** Under four is usually too little accumulated change to be worth
measuring; over eight is where regressions start hiding.

**Nothing schedules this, and nothing can.** There is no cron here, no unattended
runner, and no session that lives long enough to remember.
What there is instead is the record: `OR-11`’s closeout publishes the count — blocks
terminal since the last block whose cells declared `efficiency-loop`, and whether one is
now due — into the `SYNOPSIS.md` handoff beside the selected next entry.
**An agent that wakes up reads what has been done and what comes next, because both are
written down**, and that is the whole mechanism.

The count is derived, not remembered.
The ledger already records every agenda and the workflows its cells declared, so the
closeout computes the number rather than recalling it.
At eight the closeout selects a W5 regardless of what else is ranked; between four and
eight it may select one and must say why it did not.

Every efficiency block opens by measuring the gate — the one instrument that runs on
every change whether or not anyone asks for it — against the ceilings its predecessors
declared, before it takes any queued candidate.
A tier over its ceiling makes a block due regardless of the count and becomes its first
cell.

The rule was paid for in a single afternoon.
`validate.py` recorded its own baseline in a docstring — “Measured on 2026-08-30:
`--fast` is 499s” — beside an 1800 s cap.
Six days later the same tier ran 1369.60 s. Nothing objected: the number was inside the
cap, and 499 was prose.
Twenty-three minutes of CI on every push, for six days, found by an operator noticing
that a wait had got long.
The measurement that would have caught it costs about a minute
([`agenda-023`](packing/campaign/agendas/agenda-023-efficiency-block-the-gate-itself.md)),
and the reason it was not taken is that nothing wrote down that it was due.

## OR-13: Every fast check runs in CI; only the unavoidably slow ones leave

The policy is a floor on coverage, not a budget on time.
**A check goes in the pull-request surface unless it is unavoidably slow.** Speed is
bought by moving the few checks that are expensive, never by thinning the many that are
cheap, and a check that leaves the pull-request surface has to earn its exit by its own
measured cost.

The evidence says this is nearly free, which is why the policy can be this strict.
Measured on 2026-09-05 over the 2,080 tests of the non-exhaustive suite: one test costs
268.73 s, the next three cost 94.12 s, 83.30 s and 66.14 s, and about twenty tests carry
roughly seventy per cent of the tier.
The remaining two thousand share the rest.
Deferring twenty tests buys most of the time back; deferring the tier buys the same time
and throws away everything else with it.

And the cheap checks are where the catching happens.
All eight failures CI found on the `T-021` branch that day were record-to-artifact
consistency checks — does a register row match the certificate it names, does the
synopsis match the ledger, does the reach table match the corpus — and all eight
together cost 0.46 s. The expensive tests re-derive mathematics already decided and
frozen. **A check that compares two artifacts is cheap and catches drift; a check that
re-derives a frozen result is expensive and catches almost nothing between one release
of the code and the next.** That is the boundary, and it is a property of what a check
does rather than a list of which tests are slow today.

Three surfaces follow from it.
**The pull-request surface** is every check that is not unavoidably slow, priced to be
paid on every push. **The deep surface** carries the ones that are, and runs where it
does not block a pull request.
**The full gate** is everything, and it is what a block ends with — the `OR-11`
closeout, the end of a research block, and before a pull request is marked ready.

A terminal session names its full-gate run in its `checks`: the tier, the commit it ran
on, and the verdict.
A session that cannot name one has not finished, whatever its cells say.
The commit matters as much as the verdict, because a gate run on a tree three commits
behind the handover certifies nothing about what was handed over.

The boundary is enforced, never curated.
A hand-maintained list of slow tests rots exactly the way the 499-second docstring
rotted; the split has to be something the gate computes and can refuse.

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
