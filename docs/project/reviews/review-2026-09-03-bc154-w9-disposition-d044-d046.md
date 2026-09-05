# BC-154 — independent review of the W9 disposition for D-044 and D-046

## Provenance and installation

This document is the review deliverable of BC-154, the independent review of the W9
disposition for D-044 and D-046, written on 2026-09-03 in the agenda-016 ten-hour run.
Its author wrote only to `scratchpad/bc154-review/` -- a container-local directory
outside the repository, which does not survive the session -- and modified no repository
file.
It is installed here so that the evidence the records cite outlives that directory.

The source was `1299` lines with SHA-256
`513e6431e09a189f23de2dc141875f54ca64249c24b887aabe84ddf5a343f542`, and that hash names
the scratchpad source rather than this file.
The installation added this preface and the closing guidelines footer, and reformatted
the body to house Markdown conventions; it altered no classification, verdict, finding,
number, citation, recommendation or claim boundary, and none may be altered here.
References of the form `scratchpad/...` in the body below are the reviewer’s own record
of what was read and where it was written at review time, and are left as written.

**One premise in the body went stale after the review was written, and the body is still
left as written.** In three places the reviewer records that `sqsearch` is not built in
this environment. That was true for the whole of the review, which began at 08:46Z on
2026-09-03 and took its measurements after the quiet lease released at 09:36Z. A release
binary appeared at `packing/sqsearch/target/release/sqsearch` at 10:30Z the same day --
ELF x86-64, 617,520 bytes, untracked under that package’s own `.gitignore` -- and
nothing has been executed against it.
The conclusion the reviewer draws from the premise is unaffected and rests on its own
evidence: no live round ran, nothing was recorded through the unattended runner, and the
end-to-end coverage uses a fixture engine.
Recorded here, in the installation preface, because the review’s findings may not be
altered.

* * *

Reviewer: independent, no W9 authorship on this lane.
Agenda 016 block BC-154 review obligation.
Branch `claude/squares-pr76-overnight-run-tpc888`; audited at `95e3da47`, re-confirmed
unchanged at `ceff4400`. Date 2026-09-03.

Read-only review. Nothing in the repository was modified, staged, committed or pushed;
all work is under `scratchpad/bc154-review/`. The repository-wide quiet lease was
honoured: the entire code audit was done from file reads alone, with no process run
between 08:58Z and the lease’s early release at 09:36Z. Every measurement was deferred
until after that.

The tree moved during the review (`95e3da47` → `ceff4400`), but not on this surface:
`git diff` over `runner.py`, the trust-boundary tests, `defects.yaml`,
`campaign/README.md` and `hypothesis.schema.yaml` across those commits is empty.
Everything below applies to the current tree.

## Verdict

| Defect | Lane disposition | This review |
| --- | --- | --- |
| D-044 — result validity and self-test status are proposer assertions | fixed-with-regression | **BOUNDED-CAVEAT** |
| D-046 — the unattended runner is not a closed, checked state machine | fixed-with-regression | **BOUNDED-CAVEAT** |

Both repairs are real, and neither is a mechanical refusal dressed as a repair.
The attack each defect names is closed, and I could reproduce that.
What holds each back from PASS:

- **D-044** — three undisclosed residuals sit on the exact boundary the defect names
  (Findings 1-3): `record` never binds the lines it *scores* to the bytes the child
  *verified*; `execute` writes no digest, so the archive-digest refusal is unreachable
  in the unattended loop; and a post-execute edit can manufacture the declared seed
  count over geometry that genuinely verifies.
  All three share one precondition — **write access to the archive between `execute` and
  `record`, which the producer does not have** — and all three close with one receipt
  and one comparison. One live source statement is still false (the test docstring’s
  “five orders … this pins that ratio”; `defects.yaml` has already been corrected).
  The producer-side attack D-044 actually names — a fabricated side, a fabricated zero
  overlap, an untested binary — **is genuinely closed, and I reproduced every refusal.**
- **D-046** — all twelve clauses of the *record* are closed in code, and I read and
  measured each one. But the runner does not honour a declared campaign stop condition
  (Finding 8, control-cell breach: `campaign/README.md:392` says stop, the runner
  continues), `run`’s failure policy does not cover the whole exception class, and the
  timebox semantics are now settled only in the code.

A correction to my own first draft, made by measuring rather than reasoning: I had
argued that the seven guards left without a permanent mutation proof were therefore
unevidenced. **They are not — I reverted all seven in copies and every one turns the
suite red** (Measured check B). The lane’s twelve-guard claim is verified in full.
What the seven lack is protection against a future weakening of the *tests*, which is a
real risk here because two of the twelve were tautologies on the first pass.

**One finding cuts across both and is the reason neither is a PASS.** Both defect
records are summaries of findings F-02 and F-04 in
`docs/project/reviews/review-2026-08-23-square-packing-program-and-pr14.md`, and the
lane repaired against the summaries.
Checked against the source findings, **four required clauses were not carried into
`defects.yaml` and so were never repaired**: F-02’s “exact zero is not required at the
float screen; independently bounded non-overlap is”, and F-04’s pre-run dirtiness,
per-cell timeboxes, and runnable-but-unrun reporting.
All four are conservative in direction — none flatters a result — but a `status: fixed`
should cover them or name them, and it does neither.
Each is named precisely in section 0.

Neither rises to DISCREPANCY at the disposition level.
Twelve individual record statements do, and are listed under Required corrections.

**This is engineering work and it is never a scientific result.** I checked every record
this repair touched for any implication otherwise and found none.
The lane opens with the statement itself; `d45a3269`’s message says “No scientific
criterion, threshold, control or verdict changed”; no accept-rule clause, threshold,
control or hypothesis verdict moved; no round artifact was written to the live campaign;
and `SYNOPSIS.md:87` still carries the runner as **NO-GO** for unattended execution.
The two reader-facing claims `d45a3269` added to `SYNOPSIS.md` are engineering claims
about the boundary, correctly hedged on the scientific question ("No live round has
passed through the repaired boundary, so admitting it unattended is still a review
decision rather than a settled one") — though the word “closed” in one of them
overstates and is listed for correction.
One structural nuance is at Finding 10: the guard row the repair adds to each round
record can only ever read `criterion_met`, so its evidential content is presence, not
value.

## 0. The four unrepaired clauses, named precisely

Both defect records summarise findings in
`docs/project/reviews/review-2026-08-23-square-packing-program-and-pr14.md`. The lane
repaired against the summaries in `defects.yaml`. These four clauses are in the source
findings, are absent from the summaries, and are absent from the code.
Each is stated with its source text, what the code does, and what would close it.

**1. F-02: “Exact zero is not required at the float screen; independently bounded
non-overlap is.”** (review line 442-443)

`validated_record:587` still refuses any line whose `overlap` is not exactly `0.0`. The
repair *added* the independent bound and *kept* the screen F-02 asked to drop.
Measured: an overlap of `1e-18` is refused outright while the identical geometry
verifies. The engine’s own notion of feasible is a bound, not an exact zero — its
self-test accepts `best_overlap <= FEASIBLE_EPS` (`main.rs:502-507`) — so a round in
which `sqsearch` reports a genuinely tiny non-zero overlap is refused before the oracle
that exists to decide it is consulted.
**Close it by:** `overlap` must be finite and `<= POSE_TOLERANCE`, and let the geometric
check decide.
Direction of the current behaviour is conservative, so this is not urgent —
but it is unimplemented, and unrecorded.

**2. F-04: “record pre-run engine dirtiness before campaign writes.”** (review line 504)

`execute:1071` captures `git status --porcelain` *after* `claim` has written the
in-progress stub and re-rendered `campaign/ledger.md`, neither committed.
Measured: from a verifiably clean tree, the recorded `method.dirty` is `True`. The field
is unconditionally `True` on every unattended round and therefore carries no
information, and `artifact_fields_from_execution` copies it into `subject` and `method`.
**Close it by:** capturing dirtiness in `claim`, before the stub write, and carrying it
forward.

**3. F-04: “recipes and the spec describe per-cell timeboxes.”** (review line 483-484)

Three documents, three answers, and the code implements a fourth: the hypothesis schema
and the source review say per-cell; `campaign/README.md:390` says per-round; `execute`
takes the round budget and divides by the cell count.
Latent today — both live recipes declare one cell — but the semantics live only in the
code. **Close it by:** deciding, then writing it in the schema, the runbook and
`defects.yaml`. If per-cell wins, this is a code change, not a doc change.

**4. F-04: “The report can omit runnable-but-unrun work.”** (review line 496)

Half repaired. `safe_release` and the report’s Health section now do the “what moved /
what died” half, which was the substantive part.
But a hypothesis that was runnable and simply not reached — the session budget ran out
before its turn — appears in neither `done` nor `skipped`, because `skipped` holds only
what `queue` filtered out.
**Close it by:** reporting the unattempted runnable remainder alongside `skipped`.

None of the four flatters a result; all four are conservative or merely uninformative.
That is why they are BOUNDED-CAVEAT and not DISCREPANCY. But `status: fixed` is a claim
about the finding, not about the row that summarises it, and on that reading the repair
is **incomplete rather than merely unproven** — which is what the closeout audit
reported and what I confirm.

## 0b. The three questions, answered

**“The W9 write-up’s headline says the gate tier has not run yet, while the same
document later reports it ran and failed five steps.
Which is true?”** — **It ran, and it was red.** The headline is stale; the later section
is correct.
The gate ran 07:35-07:50Z and reported 5 failed steps (`gate.log:651-656`). I
checked the attributions and they hold: the lint failures are the rigidity lane’s
`local_rigidity/binding.py` and `chart.py`; the campaign-record failure is a stale
generated `ledger.md`; the provenance failure is a pre-existing orphaned commit on
`exp-002`; the fast-tests step timed out at 901s with its single `F` being the
repository-wide 64 MiB snapshot budget.
So “red, all five attributed elsewhere” is the true statement, and it is worse-sounding
than the headline. Correct the headline, not the section.
Declining to raise `SNAPSHOT_MAX_BYTES` to turn a negative control green was the right
call.

**“The detection-floor docstring still claims five orders where the assertion pins
four.”** — **Confirmed, and your correction landed in the right place but not
everywhere.** `defects.yaml` now reads “at least four orders of magnitude … where it
currently sits five below”, which is exactly right.
`test_campaign_runner_trust_boundary.py:812` still says “five orders … **This pins that
ratio**”, three lines above the assertion that contradicts it.
Measured: a tolerance of `1e-8` — a whole order looser — still passes.

**“sqsearch is not built, so the real producer was never executed.
Does that limit what a PASS could mean even in principle?”** — **Yes, and it is worth
being exact about how.** It does not limit a PASS on the *guards*: refusals are decided
by the harness and the oracle, both fully exercised, and I re-ran all of it.
What it limits is any claim about the *instrument as a system*. Three things are
inferred rather than executed: that the real producer’s output satisfies the new
contract end to end (I confirmed the pose is interpolated into both the chain and
summary lines at `main.rs:129-161`, and that `selftest()` exits 1 on failure at
`main.rs:537`, and that four retained real archives including `exp-011-h-020-n17.jsonl`
are fully posed — but reading is not running); that the round artifact `record` now
writes validates against the enforced `Experiment/v2` schema, which **no test checks**,
because the fixture stubs `regenerate` (Finding 9); and that the engine gate’s real cost
fits the round budget.
So a PASS here could only ever have meant “the boundary refuses what it should on a
fixture engine”. One supervised live round would convert all three.
Until then `SYNOPSIS.md:87`’s **NO-GO** is the correct posture and should stay.

## 1. Are the regressions load-bearing, and is the harness circular?

**The harness is sound and not circular.** `_unrepaired()`
(`packing/tests/test_campaign_runner_trust_boundary.py:895`) copies `runner.py` into
`tmp_path`, applies one substitution from `MUTATIONS`, imports the copy under a
throwaway module name, and removes it from `sys.modules` in a `finally`. Nothing is
written outside `tmp_path` and the working tree is never touched.
That is the correct shape, and it is the shape the process incident (section 9) makes
necessary.

Two properties make it non-circular:

- The `assert old in source` anchor check means a reverted repair fails the test with an
  anchor error rather than silently passing.
- Each paired test asserts the *real* module refuses before it asserts the copy accepts.
  Revert the repair and the `pytest.raises` half fails on its own.

I checked the second property directly rather than taking it on the shape of the code:
for each of the five, I substituted the mutated module for the test module’s `runner`
and ran the paired test, requiring it to fail.
Results at Measured checks A.

Each mutation genuinely disables the guard it names — I read all five against their
targets:

| Mutation | Target | Genuinely disables? |
| --- | --- | --- |
| `pose` | drops the `validated_pose(rec, int(n))` call in `validated_record` | yes |
| `attribution` | `if expected is not None and actual != expected:` → `if False:` | yes |
| `lease` | `if left <= 0:` → `if False:` in `lease_seconds_remaining` | yes |
| `transition` | `if decision == IN_PROGRESS: return` → `if True: return` | yes |
| `prereqs` | early `return []` at the top of `unmet_prereqs` | yes |

### Which guards are NOT covered, and whether that matters

Seven of the twelve have no permanent mutation proof:

1. independent verification skipped (`if archived:` → `if False:`)
2. archive-digest binding removed
3. `selftest_passed` hard-coded true
4. engine gate never fired in `execute`
5. one deadline shared across cells
6. commit not checked for durability
7. `run` catches only `GuardError`

**I measured all seven rather than argue about them, and the answer corrected my first
draft: every one is load-bearing today.** I wrote the substitutions the record omits and
ran the whole suite against a copy with each repair reverted (Measured check B). Every
mutation turns the suite red.
The lane’s twelve-guard claim is verified, including the seven it left on a one-off.

So the criticism narrows, and it is worth stating precisely rather than dropping:

- **The guards are watched; the tests are not.** A permanent mutation proof protects
  against a *future weakening of the test*, which is a different risk from a guard being
  unwatched today. That risk is not hypothetical here: two of the twelve were tautologies
  on the first pass — the per-cell share and the commit-durability branch — and **both
  are in the un-pinned seven**. The one mechanism that catches that class was applied
  once and then made permanent for five of twelve.
- **The un-pinned set is the D-044 core.** Items 1-4 are the chain that carries D-044’s
  soundness claim: the oracle runs, its verdict binds to the bytes, the gate was
  executed, the binary has not moved.
  The five that *are* pinned are the pose contract, the attribution guard, and three
  D-046 lifecycle guards.
- **The substitutions are cheap.** All seven are one-line, all seven leave the five
  existing anchors intact (I checked), and the file already has the harness.
  Promoting them is a few minutes’ work, and I have supplied the exact text.

The AST test `test_record_takes_its_verdict_only_from_the_child_process` does **not**
cover item 1, contrary to how it reads: `ast.walk` descends into dead branches, so
mutating `if archived:` to `if False:` leaves the call to
`verify_archive_in_separate_process` lexically present and the scan still passes.

I traced which tests do catch it, rather than taking the disposition’s count.
Under that mutation `verification` stays `None`, so no receipt is appended and no guard
row is written, and exactly three tests fail:
`test_a_supervised_round_records_a_verified_verdict` (asserts one guard row and a
non-None verification receipt), `test_record_refuses_a_forged_result_line` (expects a
`GuardError` that no longer raises), and
`test_record_refuses_an_archive_edited_after_it_was_verified` (same).
The disposition’s “3 tests” is right.
It is behavioural coverage; no permanent mutation proof stands behind it.

**Reproducibility of the other seven is weaker than claimed.** The disposition says
“Their recipe is the table above — the exact `old → new` text substitutions”.
The table gives a literal substitution for exactly one of the seven (`if archived:` →
`if False:`). The remaining six are named in prose only, so a reviewer cannot reproduce
six of the seven from the record as written.
I reconstructed them; they are in `scratchpad/bc154-review/check_unpinned.py` and should
be lifted into the record or into `MUTATIONS`.

**Recommendation:** promote all seven, or at minimum items 1-4. The substitutions exist
now; the only work left is pasting them into the dict that already exists.

## 2. Did any criterion change?

Both clauses exist exactly as claimed.
Verified in `packing/campaign/README.md`:

- Clause 3 (accept rule): “Every reported configuration has `overlap == 0` under the
  declared screen arithmetic, **and the engine selftest passed in the same
  invocation**.”
- Clause 4: “… **every stored pose passes an independent geometry check**; and
  deliberately invalid fixtures are rejected in the same instrument build.”
- The metric vector also lists `selftest_passed` with role **guard**, sourced as
  “`sqsearch --selftest` before any run is recorded”.

The pre-repair runner satisfied neither: `selftest_passed` was the literal `True` at two
sites, and no pose was stored to check.
**The repair enforces rather than tightens, with two qualifications a reviewer should
not skip.**

- **Clause 3 is enforced at round granularity, not per invocation.** `execute` runs the
  gate once before the cell/seed loop, not once per `(n, seed)` command.
  Literally read, clause 3 says “in the same invocation”.
  The gap is closed by construction rather than by repetition: `selftest_passed()`
  re-hashes the binary at `record` time and refuses on a mismatch, so the binary that
  ran every measurement is provably the binary that passed the gate.
  For a deterministic binary that is equivalent, and it is the cheaper of the two.
  Faithful enforcement, worth stating plainly in the record because the wording differs
  from the clause.
- **Making a pose mandatory is a new demand on the producer, not a new criterion.**
  Clause 4 says “every *stored* pose” — vacuously satisfied when nothing is stored,
  which is exactly how the pre-repair runner satisfied it.
  Requiring emission is what gives the clause content.
  It is a change to the *harness contract*, not to the accept rule; it runs in the
  refusing direction; it was disclosed (limit 4); and the two contract documents that
  described the old behaviour were corrected in `d45a3269`. The accept rule itself is
  untouched — I diffed the README and the change sits in the “Adding an experiment”
  contract section at lines ~501-517, nowhere near the accept rule at ~347-370.

**No criterion changed.** The claim holds.

Two small things about the edited contract text itself, since it is reader-facing:

- `campaign/README.md:504-506` enumerates four requirements (JSON Lines,
  `best_side`/`n`/ `seed`, zero `overlap`, the pose, exit 0) and does **not** mention
  that the harness runs the engine gate before the round — which the schema’s `command`
  prose does mention and which the runner’s own docstring lists as clause 5. The two
  contract documents now enumerate different contracts.
- `campaign/README.md:509-512` says `record` “re-decides containment and pairwise
  separation in a separate `sqpack.verify` process, over a `sha256` of the result lines
  actually on disk”. True of the child’s report.
  It reads as though the round’s numbers are bound to that `sha256`, which is what
  Finding 1 shows they are not.
  Not false; stronger than the code, in a document a reader will trust.

## 3. D-044 specifically

Every element checked against the code, not the summary.

| Claim | Where | Verdict |
| --- | --- | --- |
| scored lines carry `x`/`y`/`t` of length `n` | `validated_pose` (runner.py:520), called unconditionally from `validated_record:593` | holds; finite, non-bool, non-array and wrong-length all refuse |
| poses content-addressed by sha256 | `pose_digest:597` over canonical `{n,seed,best_side,x,y,t}` | holds |
| archive content-addressed | `archive_digest:616` over ordered pose digests | holds; receipts excluded, so appending one cannot move it |
| `record` re-runs the check in a SEPARATE process | `record:1276` → `verify_archive_in_separate_process:766` | holds |
| enforced by an AST test | `test_record_takes_its_verdict_only_from_the_child_process:824` | holds, **bounded** — see below |
| corners rebuilt and translated to the bbox origin | `verify_archive_poses:705-710` | holds |
| `--selftest` actually executed, binary hashed | `run_engine_selftest:811`, `execute:1066`, `selftest_passed:863` | holds |

**The separate-process claim is real.** `verify_archive_in_separate_process` spawns
`[sys.executable, "-m", "sqpack.campaign.runner", "verify-archive", <path>]`, the child
re-reads the file from disk, and the parent refuses on a non-zero exit, an unparseable
report, or `verified` false.
`main()` routes `verify-archive` before `require_project_root`, so the child does not
need the checkout. Two real child processes are also spawned by `preflight`.

**The AST test is weaker than its docstring.** It collects only `ast.Call` nodes whose
`func` is an `ast.Name`. An attribute call (`verify.verify_packing(...)`) or an aliased
call would pass it unseen.
It catches the naive “optimise the subprocess away” edit, which is the realistic
regression, and it should be described that way rather than as “`record` may reach a
verdict only through the child process … enforced structurally”.

**The translation argument is sound.** `verify_packing` tests containment in
`[0, side]²`. Translating to the bounding-box origin sets `min x = min y = 0`, so
containment reduces to `extent_x ≤ side` and `extent_y ≤ side` — which is the *best case
over all translations*. No translation could do better, so the test never falsely
refuses a configuration that genuinely fits, and a refusal is decisive.
That is the right direction for an anti-forgery oracle.
`required ≤ side + POSE_TOLERANCE` is checked explicitly alongside, making the
containment test redundant but not wrong.

Two further things I checked because the argument invites them:

- **The tolerance is a real distance.** `edge_axes` on a unit square from
  `corners_from_poses` returns unit-length normals, so `float_sign(1e-9)` on projection
  gaps is 1e-9 in length units, not in some scaled axis unit.
  The measured floor (refuses at 2e-9, accepts 1e-10) is consistent with that.
- **Rotation is not searched over.** The oracle checks the axis-aligned bounding box
  only. A configuration that would fit at some rotation but not axis-aligned is refused.
  That is conservative — it can only produce false refusals, never false acceptances —
  so it is safe, but it is a property of the oracle that no shipped test records.
  The disposition asserts “A rotated (45°) valid packing verifies” as a fixture result;
  there is no such test in the file.
  Measured check C settles it.

### Against the required repair as the source review wrote it

Neither defect record is the original report.
Both cite `docs/project/reviews/review-2026-08-23-square-packing-program-and-pr14.md`,
and F-02 there states the required repair in five clauses (lines 437-443). Checked one
by one, because a defect is closed against what was asked, not against what the summary
retained:

| Required (F-02) | Delivered |
| --- | --- |
| “every result row must preserve a full pose or a content-addressed pose reference” | **yes** — both, in fact |
| “A separate `sqpack` process recomputes containment and pair separation from that pose” | **yes** |
| “records its own version and tolerance tier” | **partly** — the receipt records `verifier` (a name, not a version) and `tolerance` (a scalar, not a tier) |
| “signs the accepted row’s digest” | **yes in substance** — `pose_sha256` per row, `archive_sha256` over the archive, both in the receipt and the record |
| “**Exact zero is not required at the float screen; independently bounded non-overlap is**” | **no — and unmentioned** |

The last row is the one that matters.
`validated_record:587` still refuses any line whose `overlap` is not exactly `0.0`. The
repair **added** the independent bound and **kept** the exact-zero screen the source
review asked to drop.
That is a change in the refusing direction, so it is not a soundness risk.
But it is an unmet clause of the defect’s own required repair, it is not named anywhere
in the disposition or in `defects.yaml`, and it has a live consequence:

`sqsearch` prints `"overlap":{:.3e}` of `o.best_overlap` (`main.rs:131`), and its own
self-test accepts a configuration as feasible at `best_overlap <= FEASIBLE_EPS`
(`main.rs:502-507`) — that is, the engine’s notion of feasible is a bound, not an exact
zero. Any round in which the engine reports a genuinely tiny non-zero overlap is refused
outright rather than handed to the oracle that now exists precisely to decide it.
The retained archives suggest the engine does print exact zero in practice; nothing
guarantees it.

Having built the independent geometric check, the runner no longer needs the producer’s
scalar to be exactly zero — which is the point F-02 was making.
Either relax the screen to `overlap <= POSE_TOLERANCE` and let the oracle decide, or
record why the stricter screen was kept.
Right now the record does neither.

**The producer really does satisfy the new contract.** `sqsearch/src/main.rs:47`
(`json_config`) is interpolated into both the `"kind":"chain"` line (129-142) and the
`"kind":"summary"` line (151-161), so every scored line on the ordinary search path
carries `x`/`y`/`t`. `main.rs:64` dispatches `--selftest`, and `selftest()` ends with
`std::process::exit(1)` on any failure (main.rs:537). Both decisive findings confirmed
at source.

## 4. D-046 specifically

All twelve clauses read against the code.
Every one is addressed:

- **Transitions.** `require_in_progress` (876) guards `execute` (1056), `record` (1239)
  and `release` (1483). Terminal rounds refuse.
- **Prerequisites.** `unmet_prereqs` (887) gates both `queue` (305) and `claim` (377).
- **Per-cell deadlines.** `execute:1091` gives cell `i` an equal share of what is left,
  `remaining / (len(cells) - index)`, reclaiming unspent time.
- **Lease clamp.** `budget = min(duration(timebox), lease_seconds_remaining(...))` at
  1077\. The second lease read is after the gate runs, so the gate’s cost comes out of
  the lease-derived budget, as the comment claims.
- **UTC lease parsing.** `lease_expiry:915` — naive → UTC, aware → `astimezone(UTC)`.
- **Durable failures.** `run:1962` catches `(GuardError, RefusalError, OSError)`,
  releases via `safe_release`, counts the failure, and writes the report from a
  `finally`.
- **Narrow checked staging.** `commit_paths:951` — explicit pathspec,
  `git add -- <paths>`, empty-stage refusal, exit-status check, and `HEAD` before/after
  comparison.

**`unmet_prereqs` treats prose prerequisites as UNMET. Confirmed.** Line 902:
`if not re.fullmatch(r"H-\d+", text)` appends
`"{text!r} is not a hypothesis id this runner can check"`. An `H-###` prereq
additionally requires an `accepted` decision among the rounds referencing it.
Both directions are tested
(`test_the_queue_skips_a_hypothesis_whose_prereqs_have_not_landed` asserts both reasons)
and fired in `preflight:1752` with a mixed list.
The empty-list case is also pinned so the gate cannot starve the queue.
This is the conservative reading and it is the right one.

Residuals in this defect’s area, none of them fatal:

- **`run`’s failure policy is not total.** `KeyError`, `TypeError` or a YAML error from
  a malformed recipe or artifact still escapes the `except` clause.
  The `finally` still writes the report, so the session is not silent, but the round is
  neither released nor counted toward `MAX_CONSECUTIVE_FAILURES`. D-046’s clause is
  “process and persistence failures escape the failure policy”; the named ones no longer
  do, but the class is not closed.
- **Exit code — checked and CONFORMING, not a gap.** `abnormal` is set only by
  `GateRunningError` or three consecutive failures, so a session that refused one or two
  rounds exits 0, and the lane’s own test asserts `runner.run("fixture", 0.5) == 0` on a
  refused round. I flagged this and then withdrew it: `campaign/README.md:394` requires
  non-zero only “on an abnormal stop”, and one or two refusals followed by an ordinary
  queue exhaustion is not one.
  The behaviour matches the declared rule.
- **`effort.wall_seconds` excludes the gate.** `started = time.monotonic()` is set after
  `run_engine_selftest`, so the recorded cost understates the machine time the round
  consumed. Harmless — the budget currency is pair-tests, not wall clock — but the field
  now means something slightly different from what it did.
- **`test_each_cell_gets_its_own_share_of_the_timebox` is timing-sensitive.** With a 3s
  round budget over two cells, a loaded machine that overruns the first cell’s 1.5s
  share pushes the second into “before the cell started” and fails the test.
  The stricter assertion that made the test load-bearing also made it more fragile, in a
  suite already at its 900s step budget.

### Against F-04 as the source review wrote it

The disposition’s twelve-clause table follows `defects.yaml`’s `what` field, which is a
*summary* of finding F-04. Checked against F-04 itself
(`review-2026-08-23-square-packing-program-and-pr14.md:475-507`), **three clauses
present in the source finding did not make it into the summary, and so were never
repaired:**

- **“The `dirty` flag is computed after the runner’s own files have been written, so it
  does not describe the engine’s starting tree.”** Required repair: “record pre-run
  engine dirtiness **before campaign writes**.” Still not done.
  `execute:1071` captures `git status --porcelain` *after* `claim` has written the
  in-progress stub and `require_regenerated` has rewritten `campaign/ledger.md`, neither
  of which is committed.
  So `git status` is non-empty on every unattended round and `dirty` is unconditionally
  `True` — a provenance field that now carries no information, propagated into
  `subject`/`method` by `artifact_fields_from_execution`. Capturing it in `claim`,
  before the stub write, would fix it.
- **“although recipes and the spec describe per-cell timeboxes”** — F-04’s own words.
  See section 8: the source review reads the timebox as per-cell, the runbook reads it
  as per-round, and the repair implemented a third thing.
- **“The report can omit runnable-but-unrun work and does not implement the promised
  ‘what moved / what died’ distinction.”** Half done.
  `safe_release` and the report’s Health section now distinguish what died and in which
  state, which is the substantive half.
  But a hypothesis that was *runnable and simply not reached* — the session budget ran
  out before its turn — appears in neither `done` nor `skipped`, because `skipped` only
  holds what `queue` filtered out.
  It is still omitted.

None of the three is a soundness hole and none flatters a result.
All three are clauses of the repair D-046’s own source asked for, closed in the record
without being closed in the code.
A `status: fixed` on D-046 should either cover them or name them.

### One adjacent observation, since the lane’s own decisive finding invites it

The lane’s decisive finding was that “the producer already emits the pose and the runner
threw it away”. The same sentence is still true of the campaign’s declared budget
currency.

`campaign/README.md:414` lists `pair_tests` in the `effort` block as “the
machine-independent budget currency”, and the accept rule’s “Equal budget or no
comparison” paragraph says the currency is pair-tests, “not wall clock and not moves”.
`sqsearch` emits `pair_tests` on every chain and every summary line (`main.rs:131`,
`:155`). `record` writes `effort` as
`{timebox, wall_seconds, agent_minutes, stopped_by}` (runner.py:1371-1373) and **does
not lift `pair_tests` out of the archive**. The experiment schema requires only
`stopped_by`, so this is legal — and it means no runner-produced round can be checked
against “equal budget or no comparison” without re-reading its archive by hand.

Out of scope for D-044 and D-046, and pre-existing.
Named here because it is the identical pattern on the identical archive, one metric
over, and because the repair that lifted the pose was the natural moment to lift this
too.

### The retained `--no-verify`: I accept the trade

`lefthook.yml` formats the **whole repository** and re-stages (`stage_fixed: true`), and
`AGENTS.md` documents that the hook deliberately does not take `{staged_files}` because
`.flowmarkignore` is resolved relative to its target.
Running that hook inside an unattended round would sweep every other writer’s
reformatted Markdown into the round’s commit — which is precisely the broad staging
D-046 asks to remove.
Keeping the bypass with an explicit pathspec is the combination that closes the defect.
The consequence D-046 names by name — success after a failed commit — is closed
independently, by the exit-status check and the `HEAD` comparison.

The residual is that an unattended round’s commits bypass the repository’s only
formatting gate, so round artifacts can land unformatted.
`AGENTS.md` states that format drift deliberately does not fail CI, so nothing breaks.
Accepted, and correctly flagged by the lane for a reviewer to disagree with rather than
discover.

## 5. The unnamed hole: cross-cell attribution

**Verified, and it is a real hole that was really closed.** `read_lines`
(runner.py:1005) now takes `expect_n` and `expect_seed` and refuses any scored line
whose declared `n` or `seed` disagrees with the invocation, **before** the line is
written (1031-1039). `execute:1117` passes both.
Regressions: `test_a_result_may_not_be_attributed_to_another_cell` (both directions),
`test_a_matching_line_is_still_archived`, a `preflight` check at 1635, and a permanent
mutation proof. The archive-side check in `cells_from` (1168) additionally refuses any
`n`/`seed` outside the declared recipe.

Worth stating plainly, because it changes how much the pose contract buys: with the
attribution guard in place, a *producer* can no longer manufacture seeds or cells at
all. The residual attack surface is post-execute archive editing, not the producer.
That is the shape of Findings 1-3 below.

## 6. Are the disclosed limits accurate and complete?

The three named limits are accurate:

- **`sqsearch` is not built here.** Confirmed — the fixture engine in the test file
  implements the same `--selftest` and output contract, and
  `test_a_supervised_round_records_a_verified_verdict` is the only end-to-end round.
  No live round ran. Correctly stated.
- **Float arithmetic with a detection floor pinned by a test.** The floor is real; the
  “pinned” claim is overstated by one order — see Required corrections.
- **`--no-verify` retained deliberately.** Accurate, well-argued, accepted above.

They are **not complete.** Undisclosed limits, in descending order of weight:

### Finding 1 — `record` never binds the lines it SCORES to the bytes the child VERIFIED

`record` reads the archive three times and cross-checks none of them:

1. `scan_archive(archive)` at 1248 → `archived`, `receipts`
2. the child’s own read inside `verify_archive_in_separate_process` at 1276
3. `cells_from(archive, recipe)` at 1288 → the numbers that become the verdict

The parent has `archived` in hand and never computes `archive_digest(archived)` to
compare with the child’s `archive_sha256`. The stored-receipt comparison at 1280 is not
that check: it only fires when a receipt already exists, which in the normal flow means
only on a *second* `record` attempt.
**On the first `record` there is no binding at all between the verified bytes and the
scored bytes.**

The record’s provenance paragraph then says the poses “were rebuilt … over archive
`sha256:X`”. That sentence is true only under the single-writer assumption.
D-044’s own clause 44.6 is “nothing binds a verdict to an immutable digest”; the repair
binds the *certificate* to the digest and leaves the *verdict* bound to an
unsynchronised third read.
The fix is one line — compare `archive_digest(archived)` to
`verification["archive_sha256"]` and refuse on a mismatch.

### Finding 2 — `execute` writes no digest, so the digest-binding branch is nearly unreachable

This is the sharper form of Finding 1, and it is the finding I would most want the
coordinator to see.

`execute` appends a self-test receipt and an execution receipt but **no archive
digest**. The only place a `campaign_runner_verification` receipt is ever written is
`record:1279`. So `stored is not None` at 1277 — the whole archive-digest refusal —
requires a *previous* `record` on the same round that got as far as 1279 and then failed
before 1449.

I traced that window.
It is narrow:

- After `write_atomic` at 1449 the artifact carries a terminal verdict, so
  `require_in_progress` refuses any retry.
  The ledger refusal at 1456 and the commit at 1464 are both *after* the write — which
  is why `test_run_reports_the_true_state_when_a_step_fails_after_the_verdict` exists.
- The only failures between 1279 and 1449 are `cells_from` refusing an `n`/`seed`
  outside the declared recipe, or `standing_best` refusing a missing frontier artifact.
- And under `run`, any of those goes straight to `safe_release`, which makes the round
  terminal. So the retry is reachable only by hand: fix the frontier artifact or the
  recipe, then re-run `record` without releasing.

**In the unattended loop the digest-binding branch never fires.** The guard is real code
with a real test — but the test plants the receipt by hand
(`test_record_refuses_an_archive_edited_after_it_was_verified:394`) precisely because
nothing else puts one there in time.

That matters for how D-044 clause 44.6 ("nothing binds a verdict to an immutable
digest") should be read as closed.
The natural attack — edit the archive between `execute` and `record` — is defended
**only** by the fresh geometric check.
That is a strong defence against forged *geometry* and no defence at all against an edit
that preserves valid geometry, which is exactly Finding 3.

The fix is small and it makes the existing guard load-bearing: have `execute` append the
archive digest of what it produced, and have `record` compare.
One receipt, one comparison, and both Findings 1 and 3 close with it.

**Same family, worth naming:** `artifact_fields_from_execution` (runner.py:506) writes
`engine_commit`, `method_commit`, `verdict_commit`, `dirty` and `wall_seconds` into the
round straight from the execution receipt in the archive.
`validated_execution` checks their *types* and nothing else — no cross-check that the
commit exists in git or is reachable.
So the round’s provenance revision is exactly as rewritable as the archive it sits in.
This is untouched by the repair and is the residue of the same D-044 clause 44.6 that
the frozen contract’s item 6 claims to answer.
The repair’s item 6 binds *validity* to the digest; provenance stayed where it was.

### Finding 3 — a post-execute edit can manufacture the declared seed count

Concretely: take one genuinely valid scored line and duplicate it under the other
declared seeds. Every copy verifies — the geometry is real, five times over.
`cells_from` groups by seed and sees five seeds.
`decide`’s clause-2 check (`any(len(c.sides) < expected for c in cells)`) is satisfied,
so a round that should be `abandoned` becomes `unresolved` — clauses 1-4 passed, held
for review. That fabricates **evidence sufficiency**, which is accept-rule clause 2, in
the flattering direction, and the geometric oracle structurally cannot object.

It needs archive write access between `execute` and `record`; Findings 1 and 2 would
each close it. Measured check E demonstrates it.

**And there is a producer-side form of the same weakness that no guard touches.** The
harness verifies that a line *declares* the seed it was invoked with.
Nothing verifies that the seed was *used*. A producer that echoes `--seed` from argv and
ignores it internally yields five identical results under five seed labels, satisfies
clause 2’s “five seeds per cell minimum”, and reports a spread of exactly zero — which
the metric vector reads as a mechanism signal rather than as a broken instrument.

For the live instrument this is covered, but by the engine rather than the harness:
`sqsearch`’s own self-test checks “chain reproducible from (seed, chain)” and “distinct
chains explore differently” (`main.rs:430-467`), and that gate is now executed — which
is a genuine consequence of this repair worth crediting.
Generically, the harness still takes seed independence on the producer’s word, which is
the same shape as the scalar `overlap` D-044 is about.
Out of scope for these two defects; worth a bead.

### Finding 4 — the AST containment test sees only bare-name calls

Stated at section 3. The guarantee is narrower than the docstring.

### Finding 5 — the shipped engine has a mode the new contract refuses

`sqsearch --basin-entry` prints `"kind":"entry"` lines carrying `best_side` and
`overlap` and **no pose** (`main.rs:303-321`). Under the new contract any recipe using
that mode is refused at `execute`. Limit 4 states this generically as “a future producer
that does not emit `x`/`y`/`t`”, which points outward when the case is inside the same
binary. No live hypothesis is affected — H-018 (the basin-entry hypothesis) is refuted
and carries no `runner` block — so this is latent, not active.
It should be named as such.

### Finding 6 — WITHDRAWN. The lane’s claim about the pose-less archives is correct.

I drafted this as a finding — that `validate.py`’s `_basin_event_archives` would pick up
`exp-005-basin-entry.jsonl` and replay it, contradicting the lane’s “nothing replays
them”. Measuring it refuted me.
Every scored archive’s first line carries **no `contract` field at all**, `exp-005`
included (Measured check C), so the basin-event classifier does not select it, and no
runner path re-reads it either.
I also enumerated every reader of `campaign/series/*/results/*.jsonl` outside the runner
(Measured check C): `check_regressions.py` reads `exp-002` and `check_canonical.py`
reads `exp-003`, both of which are fully posed and would pass the new contract anyway,
and nothing applies `validated_record`.

The lane’s limit 2 is accurate as written.
Recorded here rather than deleted because a reviewer’s withdrawn findings are part of
what the next reader needs.

### Finding 7 — preflight’s “no accepting verdict” check is one exact literal

`preflight:1857` asserts the string `"decision": "accepted"` is absent from the module.
The repair’s new code writes the value as `"accept" + "ed"` (`unmet_prereqs:910`),
following the pre-existing idiom at `TERMINAL_DECISIONS:146`. The check is still true
and `decide` genuinely has no accepting path, so this is not a soundness hole.
But the frozen transition table says “preflight still asserts the string is absent from
the module”, which claims more than a single-literal grep delivers, and the repair added
a new construction the grep cannot see.

### Finding 8 — a control-cell breach does not stop the session

Adjacent to scope: neither defect names it, but it sits on the same boundary the block
is about, and the lane closed one other unnamed hole here (section 5), so the standard
is already set.

`campaign/README.md:392` declares the stop conditions: “Stop, do not adapt, on: budget
exhausted; queue empty; three consecutive guard refusals or crashes; **a control cell
breaching**; any invariant check failing; or a decision that needs a human.”

A control breach reaches `decide` (runner.py:1202), which returns `rejected` with
`stopped_by: "guard"` and the reason “the instrument is suspect rather than the strategy
good … Clause 4 rejects regardless of outcome.”
`record` then returns that decision normally, so back in `run` (1948-1949) `failures` is
**reset to 0** and the loop proceeds to the next hypothesis — on the same instrument the
round just declared suspect.

`queue` will skip the breached hypothesis (its decision is now terminal), but nothing
stops the other queued hypotheses from running against the instrument whose control
failed. The declared rule says stop.
The runner adapts.
That is the unattended failure mode this block exists to close, and it
is one `raise`/`break` away.

### Finding 9 — nothing validates the round artifact `record` now writes against the schema

The disposition says “Every field is inside the existing `Experiment/v2` schema
vocabulary … No schema change was needed and none was made.”
I checked the schema and the claim is **true**: `determination` already carries
`role: guard` and `checked_by` ("The independent checker that makes it real", line 327),
`subject.tolerance` is `{type: string, minLength: 1}` so the new two-clause tolerance
string is legal, and `selftest_passed` is `{type: boolean}` described as “Whether the
engine gate ran and passed” — the exact wording D-044 cites.

But it is checked by *reading*, not by *running*. The test fixture monkeypatches
`runner.regenerate` to a stub that writes a fixed ledger line and returns exit 0
(`test_campaign_runner_trust_boundary.py:203-207`). So the end-to-end round in
`test_a_supervised_round_records_a_verified_verdict` never has its artifact validated
against `experiment.schema.yaml`, and `preflight` never writes a round at all.

`record` gained a whole new `determination` row, a rewritten `subject.tolerance`, and a
new provenance paragraph.
The first thing that would reject a malformed one is `packing-ledger` on a **real**
round — which, per this file’s own docstring, is “code that runs once, at 3am, having
never been exercised”.
The schema is `additionalProperties: false` everywhere and the softschema status is
`enforced`, so a typo does not degrade, it refuses — and it refuses after the
measurement was taken.

One round recorded against the real schema, or one test that runs the real validator
over the artifact the fixture produces, would close this.
It is the cheapest of the gaps here.

### Finding 10 — the guard row in the record can only ever say `criterion_met`

The `determination` row `record` appends carries `outcome: "criterion_met"` as a literal
(runner.py:1325); the failing path refuses the round, so no record is written at all.
The row’s evidential content is its *presence*, not its value.
That is defensible, but a reader scanning records cannot distinguish “checked and
passed” from a row that is always green.
Worth one sentence in the record.

## 7. Confirming the correction already found

**Confirmed, and it is live in the repository.**
`test_the_detection_floor_is_far_below_the_decision_threshold:809` asserts:

```python
assert runner.POSE_TOLERANCE <= runner.REACHED_BASIN / 1e4
```

`REACHED_BASIN / 1e4` is 1e-8. The test therefore pins **at least four orders**. The
actual constants sit five apart (1e-4 / 1e-9 = 1e5). A tolerance loosened to 1e-8 — one
whole order of protection gone — still passes this test.
Any record saying “five orders pinned by a test” is stronger than the test.

Measured (check A):

```
POSE_TOLERANCE = 1e-09   REACHED_BASIN = 0.0001
actual ratio   = 1e+05  (five orders)
test asserts   POSE_TOLERANCE <= REACHED_BASIN/1e4 = 1e-08  (four orders)
  if tolerance were 1e-08: ratio 1e+04, test would PASS
  if tolerance were 2e-08: ratio 5e+03, test would fail
```

Where it stands now, which is better than I first drafted:

- **`packing/defects.yaml` has already been corrected**, before my baseline.
  It now reads “one holds the oracle’s tolerance **at least four orders of magnitude**
  below the 1e-4 basin threshold, where it currently sits five below.”
  That is exactly right, and it is the wording the other places should copy.
- **The test’s own docstring is still wrong**
  (`test_campaign_runner_trust_boundary.py:812`): “five orders of magnitude below the
  1e-4 basin gap … **This pins that ratio**”. It does not pin that ratio; it pins one an
  order looser. Live in the source, three lines above the assertion that contradicts it.
- **Commit `d45a3269`’s message** says “a measured detection floor five orders below the
  basin threshold, pinned by a test”.
  Immutable; correct it in the successor record.

The comment at `runner.py:127-128` is *not* an instance: it says 1e-9 refuses overlaps
five orders below the 1e-4 basin, which is a statement about the constants and is true.

**Both test counts reconcile, and the reconciliation is the finding.** Measured (check
A): 61 (trust boundary) + 32 (campaign tools) + 13 (module boundaries) = **106 passed in
one run**, exactly the disposition’s figure.
And “all 55 of this lane’s” is not a third figure for the same thing — I recovered it:
the trust-boundary file collected **exactly 55 tests at `f8ccd541~1`**, which is its
state during the 07:35-07:50Z gate and the full-suite run.
Both numbers are honest.

What that reconciliation exposes is worse than a bad count.
The 1559-passed full-suite evidence is from a tree in which this file had 55 tests.
Since then it gained six, and **the process incident happened in between**: `f8ccd541`
at 08:10, the dead-guard commit `a9c5fdcc` at 08:13, its restoration `7d24225a` at
08:15, the mutation harness `1e5c116f` at 08:17. So the full-suite figure the
disposition cites as its broadest evidence predates the incident, its two restoration
commits, and six of the current tests.
It cannot vouch for the surface as it now stands, and the disposition presents it as
though it does.

**One more sourcing mismatch.** The disposition quotes the snapshot-budget failure as
`assert 67889012 < 67108864` (780,148 over).
The retained `suite.log` from that run says `assert 67864698 < 67108864` (755,834 over).
Two different measurements presented as one.
The conclusion is unaffected — subtracting this lane’s 69,839 bytes leaves the tree over
the cap under either figure — but the arithmetic in the disposition is built on the
number that is not in the log it cites.

## 8. Contract drift: `runner.timebox`

**Confirmed.** `packing/campaign/schemas/hypothesis.schema.yaml:187-193`:

> `timebox` ... “The give-up bound for **one cell**, declared before the round starts.”

`execute` treats it as the **round** budget:
`budget = min(duration(recipe["timebox"]), lease_seconds_remaining(...))` at 1077, then
splits that budget across cells at 1091. A hypothesis declaring `timebox: 30m` over
three cells gets 10m per cell, where the schema promises 30m per cell — a factor of
`len(cells)` less than declared.

**Severity: MODERATE — higher than a stale doc line, because three sources give three
answers and the repair silently picked a fourth.**

I first read this as one stale line in the schema, because `campaign/README.md:390` says
“**Per round, wall clock** | declare a `timebox` before starting”.
Then I read the source finding, and it settles the other way:

> F-04, `review-2026-08-23-...md:483-484` — “`execute` creates one deadline for an
> entire multi-cell recipe …, **although recipes and the spec describe per-cell
> timeboxes**.”

So the review that *raised* D-046 treats per-cell as the intended semantics and the
shared deadline as the bug.
The schema agrees with the review.
The runbook says per-round.
And the repair implemented neither: it takes the round budget and divides it by the cell
count, so a three-cell recipe declaring `30m` gives each cell 10m — a third less than
the runbook implies and a third of what the schema and the source review promise.

Nothing in `defects.yaml`, the disposition, or either contract document says which
reading is intended.
The code is now the only place the answer lives, and it is a reading no document states.

The mitigating facts, which keep this out of DISCREPANCY:

- **Latent today.** Exactly two hypotheses carry a `runner` recipe — H-020
  (`cells: [17]`, `timebox: 1h`) and H-017 (`cells: [11]`, `timebox: 8h`) — and **both
  declare one cell**, where the per-cell split is the identity.
  Nothing currently behaves differently under either reading.

- **Conservative.** Less budget per cell means fewer completed seeds, which `decide`
  turns into `abandoned` — never an acceptance.
  It cannot flatter. The aggravating facts:

- **`d45a3269` edited this exact file.** The commit rewrote `runner.command`’s prose and
  added a whole new `runner.selftest` property while leaving the `timebox` description
  asserting behaviour the same commit’s code does not have.
  The contract document was open and was left inconsistent with the runbook, the source
  finding, and the code.

- **It propagates into the record.** `record` writes
  `effort.timebox = recipe["timebox"]` verbatim (runner.py:1371), so every round
  artifact carries a field whose meaning three documents disagree about.

**Remedy.** Decide the semantics and write it once.
If per-cell is intended (the schema and the source review), `budget` should be
`duration(timebox)` per cell, still clamped by the lease — which is a small code change,
not a doc change.
If round-and-split is intended (what the code does), say so in both the
schema and the README budget table.
What must not happen is carrying this as a follow-up bead while the code quietly holds
the casting vote.

## 9. The process incident

Disclosed, and the disclosure is materially incomplete in two ways.
I traced the guard through every commit on the branch (Measured check D).

**The commit that shipped the dead guard is the one titled “fix: restore”.** Exactly one
commit carries `if False:` over the archive-verification block:

| commit | time | `if archived:` | subject |
| --- | --- | --- | --- |
| `f8ccd541` | 08:10 | intact | wip: extend the W9 trust-boundary regressions |
| `a9c5fdcc` | 08:13 | **`if False:`** | fix: restore the archive-moved refusal the previous snapshot disabled |
| `7d24225a` | 08:15 | intact | fix: re-enable the archive verification block, **this time completely** |

`a9c5fdcc`’s diff restores the inner `elif stored.get("archive_sha256") != ...` guard
and in the same hunk turns `if archived:` into `if False:`. So the repair commit
disabled a larger guard than the one it restored, and the next commit’s own subject
admits it. The disposition describes this as “the coordinator’s periodic snapshots
captured three of them, and one push briefly carried `if False:`” — which frames it as a
snapshot artifact. It was a hand-written fix that shipped the mutation.

**And the suite would have caught it in eight seconds.** I checked out the `a9c5fdcc`
runner and the `a9c5fdcc` test file and ran them against each other (Measured check D):

```
3 failed, 53 passed in 8.23s
  test_record_refuses_an_archive_edited_after_it_was_verified
  test_record_refuses_a_forged_result_line
  test_a_supervised_round_records_a_verified_verdict
```

That is the same three my mutation analysis predicted, and it is good news about the
regressions: they were load-bearing at the moment it mattered.
It is bad news about the process, and it revises the lane’s stated lesson.
The disposition’s lesson is:

> Worth recording because of what did *not* catch it: `ruff`, `ruff format` and
> `basedpyright` were all clean on a guard short-circuited to `if False:`. A dead branch
> is syntactically perfect.
> It was caught by a person reading the tree.

True, and incidental.
The suite the lane had just written caught it too, in eight seconds, and the commit was
made without running it.
The actionable lesson is not “static tools cannot see dead branches” — it is **“a commit
was pushed red on the one guard the whole block is about, because the 9-second suite was
not run before committing.”** That is a lesson with a fix attached, and the current one
is not.

Both corrections make the incident sound worse, and both are what the record should say.
The mitigation the lane drew from it — mutation testing on copies under `tmp_path` only
— is right, and it is what makes the permanent harness safe to keep.

## 10. Scope of the remediation commit

`d45a3269` is titled “Close D-044 and D-046” and touches six files, of which one —
`packing/src/sqpack/local_rigidity/receipt.py`, +8 lines — belongs to the rigidity lane
and is not mentioned anywhere in the commit message.
BC-154’s write scope is `runner.py` plus tests, and the coordinator’s record edits.
An unrelated module in a remediation commit is scope leakage that a later bisect will
have to untangle. Measured check F shows the hunk.

Note also that `d45a3269` contains **neither** `runner.py` nor the test file — those
landed in the four earlier commits (`f8ccd541`, `a9c5fdcc`, `1e5c116f`, `7d24225a`), two
of which are the incident’s restoration commits.
Anyone reading `d45a3269` alone as “the remediation” gets the record edits and none of
the repair.

## 11. Gate standing

**The required gate tier for this trust boundary has not passed.** It ran 07:35-07:50Z
and reported 5 failed steps (`gate.log:651-656`): lint floor, fast behavioral tests,
synopsis agrees with the artifacts, provenance, campaign record.
I checked what I could of the attribution and it holds up:

- **lint floor** — `gate.log:3-60` names `src/sqpack/local_rigidity/binding.py` and
  `chart.py`, the rigidity lane’s files, mid-edit.
  Not this lane’s surface.
- **campaign record** — `ledger.md is stale` (`gate.log:636-638`), a generated view the
  coordinator owns. This lane never drove a real `claim`/`record`/`release`.
- **provenance** — `exp-002-baseline-n10-positive-control.md` orphaned engine commit
  (`gate.log:633-634`), pre-existing.
- **fast behavioral tests** — timed out at 901s (`gate.log:641`), with the one `F` being
  the repository-wide 64 MiB mutation-snapshot budget.
  This lane is ~9% of the overage; removing it entirely leaves the tree over the cap and
  the step at ~901s.

Two of those five are repository-wide budget exhaustions that no single lane can clear,
and declining to raise `SNAPSHOT_MAX_BYTES` to turn a negative control green is exactly
the right call. But the honest standing is **gate red, attributed elsewhere** — not
gate-confirmed. This review certifies the code and the record; it cannot certify a tier
that has not passed.

One internal inconsistency follows from this.
The disposition’s headline qualification still reads “**the required gate tier has not
run yet.** `packing-validate --fast` refused to start because another lane holds
`packing/.gate-running`” — while its own validation section later reports that the gate
ran at 07:35-07:50Z and returned five failures.
The header was not updated after the evidence arrived.
A reader stopping at the summary gets a materially different picture from one who reads
to the end.

### One corroboration worth recording

The gate’s own pre-existing negative control independently supports the tolerance
argument (`gate.log:503-519`):

```
float64 separating-axis test:
  tol=1e-09  valid packing: accept  1e-6: REJECT  1e-9: REJECT  1e-12: accept  ...
  tol=0      valid packing: REJECT  ...
```

and states the reason in the repository’s own words: “A float verifier that accepts the
true packing also accepts overlaps below its tolerance; one that rejects those overlaps
also rejects the true packing.”
The lane’s `numerically-checked`-and-no-further stance is consistent with a measurement
the repository already had, not with a claim it invented.

## 12. Sequencing: the records were closed before this review existed

BC-154’s own budget orders the block: “300--360 the n = 17 lane author, free after H-052
and with no W9 authorship, performs the complete XHigh review of both dispositions and
every refusal … 390--450 run focused and required gate tiers, **update defects.yaml and
tbd**, and regenerate defects.md.”

What happened instead: `d45a3269` set both defects to `status: fixed` at 08:25Z, and
this review began at 08:46Z. So the record was closed to `fixed` before the independent
review it is supposed to depend on had started, and nothing in `defects.yaml`,
`defects.md` or `SYNOPSIS.md` is conditioned on this review’s outcome.
The coordinator has since identified this as their own sequencing error and undertaken
to reopen both records on a non-PASS classification; this review returns BOUNDED-CAVEAT
for both, so both should be reopened and conditioned on the caveats named here.

That is not a fault of the repair, and it does not change either classification.
It does change what the coordinator has to do with this document: the corrections below
are edits to a record that already says `fixed`, not conditions on a pending close.
Any of them left unapplied leaves `defects.yaml` asserting more than the evidence
supports, which is the exact failure mode D-044 is a record of.

For the avoidance of doubt about what a reopened record should say: **the repair is real
and substantial and should not be reverted or downgraded to “contained”.** The
producer-side attack D-044 names — a fabricated side, a fabricated zero overlap, an
untested binary — is closed, and I reproduced each refusal.
The caveat is that four source clauses were never carried across and three residuals sit
on the same boundary, all of them conservative in direction.
“Fixed, with the following named and tracked residuals” is the honest disposition;
“fixed” unqualified is not.

The disposition itself was scrupulous about not making these edits — it lists them under
“Coordinator-owned record edits this lane deliberately did not make” and left them
alone. The inversion is in the coordination, not in the lane.

## Required corrections

Ordered by whether the record currently says something untrue.

0. **Both `status: fixed` values, against the source findings rather than the
   summaries.** Four required clauses of F-02 and F-04 are neither implemented nor named
   (verdict summary; sections 3, 4, 8). Either close them or record them as carried,
   with the reason. This is the correction I would hold the disposition on: `fixed` is a
   claim about the defect, and the defect is the finding, not the row that summarises
   it.
1. **`test_the_detection_floor_is_far_below_the_decision_threshold` docstring**
   (`test_campaign_runner_trust_boundary.py:812`) — “five orders … **This pins that
   ratio**”. It pins four.
   `defects.yaml` has already been corrected to “at least four orders … where it
   currently sits five below”; copy that wording three lines up to the docstring, or
   strengthen the assertion to `REACHED_BASIN / 1e5`.
2. **Nothing to do in `packing/defects.yaml` for the detection floor** — it is already
   right. Noted so the correction is not applied twice.
3. **The `timebox` semantics, in whichever place is wrong.** The schema
   (`hypothesis.schema.yaml:191`) and the source review both say per-cell; the runbook
   (`campaign/README.md:390`) says per-round; the code does round-divided-by-cells,
   which no document states.
   Pick one and write it in all three.
   See section 8 — this one may be a code change, not a doc change.
4. **The disposition’s “55 of this lane’s”** — both counts are honest (55 then, 61 now),
   but the 1559-passed full-suite run predates the incident, its two restoration commits
   and six of the current tests.
   Say that, rather than citing it as coverage of the current surface.
5. ~~The exp-005 sentence~~ — **withdrawn, the lane is correct.** See Finding 6.
6. **The disposition’s snapshot-budget figures** — it quotes
   `assert 67889012 < 67108864` where the retained `suite.log` says `67864698`. The
   conclusion holds under either; cite the one that matches the log it points at.
7. **The process-incident paragraph** — two corrections, both in the worse direction:
   `a9c5fdcc`, the commit titled “fix: restore …”, is the commit that shipped
   `if False:`; and the suite catches that state in 8.23 seconds, so the lesson is that
   the suite was not run before committing, not that static tools cannot see dead
   branches.
8. **The disposition’s headline gate qualification** — it says the tier “has not run
   yet”; the same document later reports it ran and failed five steps.
   Update the header to “ran, red, all five attributed elsewhere”, which is both
   worse-sounding and true.
9. **The frozen transition table’s preflight sentence** — “preflight still asserts the
   string is absent from the module” describes a single-literal grep that the repair’s
   own new code is written to sidestep.
   State what the check actually checks.
10. **The adversarial-fixture table’s persistence-failure row** — it says the third
    branch (a commit that exits 0 without moving `HEAD`) is “written and reviewed but
    **not covered by a test**”. The same document’s mutation section says that test was
    written, and it exists:
    `test_commit_paths_refuses_a_commit_that_does_not_move_head:560`. Here the record
    understates its own coverage, which is the harmless direction but is still a
    document contradicting itself.
11. **`SYNOPSIS.md`, the two reader-facing claims `d45a3269` added.** Both go beyond
    what this review can certify and both need the same conditioning as `defects.yaml`:
    - “The runner’s full-pose independent verification boundary **is now closed** under
      D-044: a scored line must carry the pose, and `record` re-checks the archived
      geometry in a separate process before writing a round.”
      The mechanism described is accurate.
      “Closed” is not, while Findings 1-3 and clause 1 of section 0 stand.
    - “D-044 — the boundary that made it inadmissible unattended — **is now fixed**”,
      for H-017. The sentence that follows it is already correctly hedged ("No live
      round has passed through the repaired boundary, so admitting it unattended is
      still a review decision rather than a settled one"), and `SYNOPSIS.md:87` still
      carries the runner as **NO-GO**. Keep both of those; condition the “is now fixed”.

## Recommended before the runner is trusted unattended

Not blocking this disposition; blocking any future move off `SYNOPSIS.md`’s **NO-GO**.

1. **Stop the session on a control-cell breach** (Finding 8). This is the one I would
   raise first: it is a declared stop condition the runner does not honour, it is on the
   exact boundary D-046 names, and continuing to run an instrument that just failed its
   own control is the unattended failure this block exists to prevent.
2. Bind the scored lines to the verified digest (Finding 1). One line.
3. Have `execute` append an archive digest, so the first `record` has an
   `execute → record` binding (Finding 2). Closes Finding 3 with it.
4. Promote the four D-044 core guards into `MUTATIONS` (section 1).
5. Give the other three un-pinned mutations literal `old → new` substitutions in the
   record, or promote them too.
6. Validate one `record` output against the real `Experiment/v2` schema, in a test or in
   one supervised live round (Finding 9). Cheapest gap on the list.
7. Widen `run`’s `except` or add a bare terminal handler that still releases and counts.
8. Name Finding 5 (`--basin-entry`) explicitly in the limits.
9. Capture pre-run dirtiness in `claim`, before the stub write, so `subject.dirty` and
   `method.dirty` mean something again (section 4). Currently `True` on every unattended
   round.
10. Relax the exact-zero overlap screen to the declared tolerance and let the oracle
    decide, as F-02 asked — or record why the stricter screen was kept (section 3).

## What this review could not establish

Stated so the next reader does not mistake silence for coverage.

- **No live round.** `sqsearch/target/release/sqsearch` is not built here, so I
  confirmed the producer satisfies the new contract by reading `main.rs` (the pose is
  interpolated into both the chain and summary lines; `--selftest` exits 1 on failure)
  and by counting poses in the retained archives.
  Neither is execution.
  The lane’s limit 1 is accurate and this review does not lift it.
- **The gate tier.** Red, for reasons attributed elsewhere (section 11). I checked the
  attributions I could reach; I did not re-run the gate, and running it would have
  collided with the same lease this review honoured.
- **The historical 55-vs-61 count.** I can count the file as it stands.
  I cannot reconstruct what it held when the 1559-passed suite ran, so I can only say
  the two figures in the disposition do not agree and that the lane should reconcile
  them.
- **The lane’s one-off mutation run, as it was performed.** I did not repeat it in the
  shared tree — that is the process incident of section 9, and it must not happen again.
  Instead I wrote the substitutions the record omits and ran all seven against *copies*
  under a temp directory (`check_unpinned.py`, `mutplug.py`), which is the same evidence
  obtained safely. Results at Measured checks B.

## Measured checks

The lease was released early, at 09:36Z. Everything below ran after that, under
`packing/.venv/bin/python3` (Python 3.14; never bare `python3`, per D-397), read-only on
the repository. Scripts are in `scratchpad/bc154-review/`.

### A. Counts and arithmetic

```
tests/test_campaign_runner_trust_boundary.py  61
tests/test_campaign_tools.py                  32
tests/test_module_boundaries.py               13
all three, run together:              106 passed in 12.56s
trust-boundary file at f8ccd541~1:     55 collected   <- the "55" figure, recovered
preflight against the live campaign:  PREFLIGHT PASSED, 0 FAIL lines
`if False:` / `elif False:` in runner.py:  0

POSE_TOLERANCE = 1e-09   REACHED_BASIN = 1e-04
actual ratio = 1e+05 (five orders); test pins <= 1e-08 (four orders)
a tolerance of 1e-08 would still PASS the test; 2e-08 would fail it
```

### B. The mutation harness, and the seven guards the record left un-pinned

The five permanent pairings, each run with the test module’s `runner` swapped for the
unrepaired copy — every one fails, so every one is load-bearing:

```
pose         failed  (DID NOT RAISE GuardError)
attribution  failed  (DID NOT RAISE GuardError)
lease        failed  (DID NOT RAISE RefusalError)
transition   failed  (DID NOT RAISE RefusalError)
prereqs      failed  (AssertionError on unmet_prereqs)
```

All five anchors occur exactly once in `runner.py`, so `replace(old, new, 1)` cannot
mutate the wrong site.
One asymmetry worth knowing: the `prereqs` mutation *prepends* `return []` and so leaves
its own anchor in place, which means the anchor-presence safety net does not apply to
that one — only its semantic assertion does.

The seven un-pinned guards, each reverted in a copy and the whole suite re-run
(`check_unpinned.py`, `mutplug.py`; baseline 61 passed):

```
verification-skipped          3 failed, 58 passed   LOAD-BEARING
archive-digest-binding        1 failed, 60 passed   LOAD-BEARING
selftest-hardcoded-true       1 failed, 60 passed   LOAD-BEARING
engine-gate-never-fired       2 failed, 59 passed   LOAD-BEARING
one-deadline-across-cells     1 failed, 60 passed   LOAD-BEARING
commit-durability-unchecked   1 failed, 60 passed   LOAD-BEARING
run-catches-only-guarderror   2 failed, 59 passed   LOAD-BEARING
```

None of the seven disturbs any of the five permanent anchors, so every failure above is
attributable to the one reverted repair.
**This refuted my first draft**, which argued the un-pinned guards were unwatched.
They are watched. What they lack is protection against a future weakening of the tests
themselves.

### C. Retained archives and who reads them

```
exp-001-baseline.jsonl                       scored=15   posed=0    contract=None
exp-002-baseline-n10-positive-control.jsonl  scored=45   posed=45   contract=None
exp-003-baseline-n11-target.jsonl            scored=45   posed=45   contract=None
exp-004-baseline-n12-negative-control.jsonl  scored=45   posed=45   contract=None
exp-005-basin-entry.jsonl                    scored=720  posed=0    contract=None
exp-011-h-020-n17.jsonl                      scored=45   posed=45   contract=None
totals: 23 archives, 6 with scored lines, 4 fully posed
```

Exactly the disposition’s figures, including the real n = 17 round.
No first line carries a `contract` field, so `validate.py`’s basin-event classifier
selects none of these, and nothing outside the runner applies `validated_record` to them
— which withdraws my Finding 6 and confirms the lane’s limit 2.

### D. The process incident, traced through the branch

Per-commit guard state and the historical suite run are in section 9. In short:
`a9c5fdcc` is the only commit carrying `if False:`, its own subject claims to be a
restoration, and the then-current suite fails `3 failed, 53 passed in 8.23s` against it.

### E. Residual probes, against the real fixtures

`test_reviewer_probes.py`, **4 passed** — each one is a finding made executable:

- `dirty` is `True` on a round whose engine tree was verifiably clean before `claim`.
- an overlap of `1e-18` is refused by the scalar screen, while the same geometry
  verifies.
- a control breach returns `stopped_by: guard`, and `run`’s body never reads
  `stopped_by`.
- one valid pose duplicated under four other declared seeds turns `abandoned` into
  `unresolved`; the oracle reports `verified=True` on all five.

Structural probes (`check_residuals.py`) confirmed: `record` never calls
`archive_digest`; `execute` writes no digest receipt; only `record` writes a
verification receipt; the AST containment test matches `ast.Name` callees only; `run`
catches `GateRunningError` and `(GuardError, RefusalError, OSError)` and nothing else.

On rotation, the disposition says “A rotated (45°) valid packing verifies”.
Measured, that is true **at its own extent** and false at the upright side:

```
rotated 45 deg: axis-aligned extent needed 2.828427 (upright side 2.0)
  claiming 2.828427 -> verified True
  claiming 2.0      -> verified False
```

The oracle never searches over rotations, so it can only refuse a packing that would fit
at some other orientation, never wrongly accept one.
Safe, and worth a sentence in the record, since “a rotated packing verifies” reads more
broadly than what holds.

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
