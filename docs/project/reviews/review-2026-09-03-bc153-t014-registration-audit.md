# BC-153 — Audit of the T-014 registration against the review that authorised it

## Provenance and installation

This document is the deliverable of the independent audit of the `T-014` registration,
dispatched under BC-153 in the agenda-016 ten-hour run on 2026-09-03. It is not the
review of the proof — that is
[`review-2026-09-03-bc153-h060-proof-independent-review.md`](review-2026-09-03-bc153-h060-proof-independent-review.md),
a different object.
This one checks only whether the registry entry claims more than that
review authorised.

It exists because the first dispatch did not.
That attempt was terminated by an infrastructure rate limit at about 10:45Z, left only
regenerated comparison outputs and no verdict, and was recorded in the closeout as a
reduction in scope rather than a check that passed.
The audit was redispatched during the BC-155 closeout window and completed at 14:24Z;
this file replaces that gap with the report it was owed.

Its author wrote only to `scratchpad/t014-audit/` -- a container-local directory outside
the repository, which does not survive the session -- and modified no repository file.
It is installed here so that the check outlives that directory, and so that the outcome
row citing it names something a reader can open.

The source was `266` lines with SHA-256
`07cccf33a942048e7383bf18d9647a5e09768dd4a5252e9df089014cd1b4b303`, and that hash names
the scratchpad source rather than this file.
The installation added this preface and the closing guidelines footer; it altered no
verdict, finding, ranking, number, citation or claim boundary, and none may be altered
here.
The audit read the branch at `ee42c371`; `SYNOPSIS.md` line numbers in the body are
that revision’s, and Finding 1 was fixed in `51724b8e` after this report was written.

* * *

# T-014 registration audit — against BC-153

Auditor: independent read-only audit, closing the `never-opened` gap from the prior
terminated dispatch.
Repo `/home/user/squares`, branch `claude/squares-pr76-overnight-run-tpc888`, HEAD
`ee42c371`. No repository file was modified; no command with write effect was run.
This report and all working notes live under `scratchpad/t014-audit/` only.

## Verdict: REGISTRATION FAITHFUL

No claim in the T-014 registration exceeds what
`docs/project/reviews/review-2026-09-03-bc153-h060-proof-independent-review.md`
authorised. The theorem text, the “not established” list, the S3 novelty framing (with
its “first is relative to the search performed” qualification), the V3/C5 classification
and its structural basis, and all six of the review’s named gaps are carried into the
registry without addition or loss.
Two consumer-side issues were found; neither overclaims and neither is load-bearing, but
both are worth fixing.

- Consumers checked and agreeing: `results.yaml`, `RESULTS.md`, `n-005.md`,
  `evidence.yaml`, `INVENTORY.md`, `README.md`, `document-map.yaml`,
  `packing/campaign/ledger.md`, and `devtools.check_results` /
  `packing-validate --records`’s “results rungs are earned” and “inventory agrees with
  the register” steps (both pass).
- Consumer that disagrees: **`SYNOPSIS.md`**, internally, at line 1974 (Finding 1
  below).

## 1. Scope fidelity — word-by-word

**Authorised** (review §7, and quoted verbatim by `packing/campaign/ledger.md` line 532,
the `exp-058` accepted-scope sentence):

> For s = 2 + sqrt(2)/2 and Goebel’s labeled pose P^0 in C = (R^2 x S^1)^5, P^0 is an
> isolated point of Feas(s) (closed unit squares in [0,s]^2, pairwise disjoint
> interiors); equivalently there is no nonconstant continuous feasible path from P^0 and
> no sequence of distinct feasible poses converging to it; hence Kingbird-rigid at fixed
> side.

**Registered** (`packing/frontier/results.yaml`, T-014 `claim`, and reproduced in
`RESULTS.md` and `README.md`):

> For s = 2 + sqrt(2)/2 and Goebel’s labeled pose P0 in C = (R^2 x S^1)^5, P0 is an
> isolated point of Feas(s) -- closed unit squares in [0, s]^2, pairwise disjoint
> interiors -- equivalently there is no nonconstant continuous feasible path from P0 and
> no sequence of distinct feasible poses converging to it; hence the n = 5 optimum is
> rigid at fixed side in the catalogue’s sense.
> Proved exactly over Q(sqrt 2) in one intrinsic half-angle chart, from a complete exact
> accounting of all 400 elementary inequalities, by semialgebraic curve selection on the
> punctured feasible set and an induction on a putative arc’s Taylor coefficients
> through order 2m that T-012’s non-negative self-stress contradicts.

The theorem sentence is identical up to punctuation.
The one substitution — “Kingbird-rigid” → “rigid … in the catalogue’s sense” — is not
drift: `[Kingbird]` is this repository’s `role: record-catalogue` resource key
(`n-005.md` `resources:`), so “the catalogue’s sense” and “Kingbird’s sense” name the
same thing, and the review’s own §7 uses both ("Kingbird-rigid" in the boxed theorem,
“Kingbird’s fixed-side sense” in the following sentence).
`packing/campaign/ledger.md` line 532 carries the review’s exact wording,
“Kingbird-rigid,” unchanged, so the authorising sentence is preserved verbatim at least
once in the record and paraphrased consistently elsewhere.

The appended proof-method sentence restates review §2’s own findings (the chart, the
400-inequality accounting, curve selection on the punctured set, the order-`2m`
induction against T-012’s self-stress) and claims no method novelty — consistent with
`significance.rationale` and `notes` explicitly disclaiming novelty of method.

**Explicitly-not-claimed items**, checked against `results.yaml` `notes` and
`evidence.yaml`/`n-005.md` limitations, all present and none broadened:

| Excluded by review | Registered `notes` (T-014) / `n-005.md` scope |
| --- | --- |
| isolation radius | “any numerical isolation radius” — present |
| side-free rigidity (false, X-007) | “rigidity when the container side is a variable, which X-007 measured to be false” — present |
| global uniqueness | “global uniqueness of the n = 5 optimum” — present |
| other n = 5 optima | “rigidity of any other n = 5 optimal packing” — present |
| Connelly–Whiteley as stated | “applicability of the Connelly-Whiteley tensegrity theorems as stated, whose hypotheses are distance members and none of which was invoked” — present |
| method novelty | “any novelty of method -- the closing principle is classical and the … CW96 Theorem 4.3.1 proof shape is not new” — present |

No place in `results.yaml`, `n-005.md`, `evidence.yaml`, `RESULTS.md`, `README.md`, or
the `ledger.md` H-060/exp-058 entries implies an isolation radius, side-free rigidity,
uniqueness, or method novelty.
**No drift found on scope fidelity.**

## 2. The V/C/S rungs

`epistemics.md` definitions applied:

- **V3** = `method: published-proof` or `proof-audited`, with a `proof` block.
  `evidence.yaml` `E-n005-fixed-side-local-rigidity` has `method: proof-audited` and a
  full `proof:` block (`source`, `theorem`, `scope`, `pinpoints`, `assumptions`,
  `audit_record`). Matches structurally; `devtools.check_results` confirms ("every
  declared rung passes its structural checks").
- **C5** = C3 or C4, plus an existing `review_artifact` mapped as a non-superseded
  review. `results.yaml` T-014 declares
  `review_artifact: docs/project/reviews/review-2026-09-03-bc153-h060-proof-independent-review.md`.
  That path is mapped in `docs/project/document-map.yaml` (line 180) with
  `lifecycle: retained` — not `superseded`, which is exactly the checker’s test
  (`packing/devtools/check_results.py` line 178:
  `review_entry.get("lifecycle") != "superseded"`). T-014’s second cited evidence entry,
  `E-n005-second-order-rigidity`, is `method: exact-algebraic`, `origin: replayed-here`,
  with a certificate and `replay_status: passed` — the structural basis for the C3 half
  of C3-or-C4. `C4` is claimed **nowhere** for T-014: grepped `results.yaml`,
  `n-005.md`, `evidence.yaml`, `INVENTORY.md`, `RESULTS.md`, `SYNOPSIS.md`, `README.md`
  for `C4` near T-014/n=5 — the only `C4` occurrences in `results.yaml` belong to T-001,
  T-002, and `next_rung` targets for other T-ids, none of them T-014.
- **S3** anchor: “A substantive case result or machine audit.”
  T-014’s `significance.rationale` reproduces the review’s own S3 framing near-verbatim
  ("the closing principle is the classical second-order sufficient optimality condition
  and the induction has the shape of Connelly-Whiteley 1996 Theorem 4.3.1, neither
  claimed as new; what is new is the exact accounting …"), matching review §4’s “Score
  S3 (a case result), not S4.” The “first” qualifier’s review-mandated caveat ("relative
  to the literature searched … Connelly 2008 was not read in print and Kingbird’s method
  is unknown") is carried into `evidence.yaml`’s `novelty_basis.gaps`. Not dropped.

**T-012 vs. T-014, distinguishable and non-duplicative.** T-012 (`confirmation: C3`)
claims second-order rigidity only — a nonnegative self-stress refusing the one
first-order flex direction, explicitly **not** local rigidity (its own `claim` says “not
infinitesimally rigid but is second-order rigid”). T-014 (`confirmation: C5`) claims the
stronger, different statement — actual isolation in the full (not just
first/second-order) feasible set, closed by curve selection plus the order-`2m`
induction. Both are scored S3 for different reasons (T-012: “no source names the
machinery for deciding it”; T-014: “first exact proof … at the smallest case where
tilting beats the grid”); neither restates the other’s justification.
Not duplicative.

## 3. Consumer agreement

Ran, read-only, from `packing/`:

- `uv run --frozen --all-extras --group dev python -m devtools.check_results` → **pass**
  ("16 registered results: every declared rung passes its structural checks, every path
  resolves, every reader-tier mention exists").
- `uv run --frozen --all-extras --group dev packing-validate --records` → the two
  T-014-relevant steps pass: **“results rungs are earned and the view agrees”**
  (`RESULTS.md` agrees with `results.yaml`) and **“the inventory agrees with the
  register”** (43 evidence records).
  **“n=5 rigidity certificates still verify”** also passes independently (14 pinned
  coordinates, 1 free direction obstructed at second order) — the T-012 substrate T-014
  builds on is not stale.
- Five unrelated steps fail (`synopsis agrees with the artifacts` — a stale
  Current-Handoff pointer to session-084; `agenda map`; `session clocks`;
  `every session's cost is attributed`; `campaign record` —
  BC-149/session-083/session-084 bookkeeping).
  All are about the in-flight closeout, not about T-014’s content, and three of the
  implicated files are the ones this audit was told not to touch because another agent
  is writing them now.
  Not audited further; noted only so the failing steps aren’t mistaken for T-014
  findings.

Manually checked, all agree with `results.yaml`:

- `n-005.md` — `rigidity.property: locally-rigid`, `assurance: verified`,
  `method: proof-audited`, and a `scope` field that reproduces the theorem, the proof
  route, the “NOT established” list, and “Registered as T-014” — word-consistent with
  the review.
- `evidence.yaml` — both cited entries (`E-n005-fixed-side-local-rigidity`,
  `E-n005-second-order-rigidity`) carry limitations, `novelty_basis`, and an
  `audit_record` that match the review’s own description of what BC-153 did.
- `INVENTORY.md` — both evidence rows present, one reference count each, `verified`.
- `RESULTS.md` — T-014 row and `next_rung` note reproduce `results.yaml` verbatim
  (machine-generated and checker-verified above).
- `README.md` — the T-014 bullet states the theorem and the fixed-side/no-radius/
  no-uniqueness caveats faithfully, no more.
- `STATUS.md` — tracks bound status, not rigidity; no n=5 rigidity content is expected
  or present there. Not a gap.
- No other `n-*.md` file references T-014 or duplicates its evidence; the other
  `locally-rigid` hits (`n-001`, `n-004`, `n-009`, `n-016`, `n-025`, `n-036`, `n-049`,
  `n-064`, `n-081`, `n-100`) are unrelated perfect-square grid cases with their own
  independent findings.
- `packing/campaign/ledger.md` line 532 (`exp-058`) reproduces the review’s authorised
  theorem sentence **verbatim**, including “hence Kingbird-rigid at fixed side,” and
  lists the same six not-claimed items and “none of them is closed by this acceptance.”

### Finding 1 (minor — internal inconsistency, understatement not overclaim)

`SYNOPSIS.md` states T-014’s classification twice, and the two disagree:

- Line 1974 (under “Results established here,” describing
  `T-014, the newest whole result`): *“It is registered at `V3`/`C3`…”*
- Line 3016 (later in the same document, same section type): *“Registered as `T-014` at
  `V3`/`C5`, apparently-novel at `S3`…”* — correct, matches `results.yaml`.

`results.yaml`, `RESULTS.md`, `README.md`, `n-005.md`, and the correct `SYNOPSIS.md`
passage all agree on **C5**. The `V3`/`C3` line is stale prose (C5 was reached by
installing the review as a mapped document; the sentence around it — “the two steps that
close the argument are an audited proof … and no instrument decides isolation” — is the
V3 rationale, not a C3 justification, so C3 there reads as a drafting leftover from
before the C5 upgrade rather than a considered restatement).
This understates rather than overclaims, and no automated checker catches it
(`check_synopsis` and `check_results` validate T-id mentions and structural rungs, not
free-text rung prose).
It should be corrected to `C5` for consistency, but it does not mislead a reader about
what was proved.

### Finding 2 (minor — completeness, not overclaim)

Two of the review’s six gaps — the instrument binding only the restricted second jet
along `e_{u4}` (gap 4), and its reduction audit sampling only the neighbourhood interior
(gap 5) — are fully and accurately recorded in `exp-058`’s round record (cited directly
in T-014’s `artifacts` list:
`packing/campaign/series/series-000-smoke-and-calibration/results/exp-058-h-060-n5-chart-and-proof.json`,
and its companion `.md`), but are **not restated** in the frontier-layer prose a reader
would meet first — `results.yaml`, `evidence.yaml`, or `n-005.md`. The other four gaps
(BCR page unread, SOSC numbering from memory, prior-art scoping carried outside the
claim, the Kingbird thirteen-vs-four tension) are all present in `evidence.yaml`’s
`limitations` / `novelty_basis.gaps`. This is an unevenness in how thoroughly the six
gaps are echoed at the registry layer versus the round-record layer it cites, not a
dropped fact (both gaps are reachable via the cited artifact and both are graded
non-blocking by the review) and not an overclaim.

## 4. T-012’s relationship to T-014

`T-012`’s `next_rung` field (the field that previously advertised the open
curve-selection action) now reads:

> Local rigidity is discharged, not open: X-007’s curve-selection argument was written
> out in full as X-012, checked against a complete exact accounting of the 400 local
> inequalities, independently reviewed by BC-153 and registered as T-014, which is where
> the n = 5 frontier property now rests.
> What remains here is V5 by a proof-assistant port.

The open action ("local rigidity needed the curve-selection argument written out") is
gone; T-012 now points forward to T-014 by name and correctly narrows its own remaining
`next_rung` to a proof-assistant port, which is a different, smaller action than the one
it used to advertise.
`n-005.md`’s `rigidity.scope` also names T-012’s role precisely ("T-012’s first-order
cone … and its non-negative self-stress transfer to that chart … The declared replay
decides the cone and the self-stress, which is the part T-012 owns"). No leftover “open”
language for the discharged action was found in `T-012`, `results.yaml`, `RESULTS.md`,
or `SYNOPSIS.md`.

## 5. The six recorded gaps — traced from review to registry

| # | Review’s gap (§5) | Where it lands in the registered record |
| --- | --- | --- |
| 1 | BCR Prop. 8.1.13 unread in print | `evidence.yaml` limitations: “the printed BCR page remains unread here; see proof.assumptions for the two independent derivations …” — present, non-blocking framing preserved |
| 2 | SOSC numbering from memory (non-acceptance route only) | `evidence.yaml` limitations: “The second-order-sufficiency theorem numbering in X-012 section 8.3 is from memory and is on the non-acceptance route only.” — present verbatim in substance |
| 3 | Prior-art scoping unverified, carried outside the claim | `evidence.yaml` `novelty_basis.gaps`: “The prior-art scoping beyond the three sources above comes from BC-152’s coordinator survey, is unverified against the primary texts, and is carried outside the claim.” — present; also X-012 §7.4/§8.5 carries it outside the claim, confirmed by direct read |
| 4 | Instrument binds the restricted second jet only | Present in `exp-058` (cited artifact); **not echoed** in `evidence.yaml`/`n-005.md` — see Finding 2 |
| 5 | Instrument’s audit samples the neighbourhood interior only | Present in `exp-058` (cited artifact); **not echoed** in `evidence.yaml`/`n-005.md` — see Finding 2 |
| 6 | Kingbird thirteen-vs-four list tension | `evidence.yaml` `novelty_basis.gaps`: “The Kingbird thirteen-versus-four rigid-list tension (X-012 section 7.3) is real and unresolved; it is not load-bearing here because n = 5 is on both lists.” — present, and X-012 §7.3 itself independently confirms the archived page has exactly four `[Rigid.]` annotations at n <= 100 (verified by direct read of `packing/resources/web/kingbird-squares-in-squares.md` reference), consistent with the review |

All six gaps are traceable to the registered record (none silently dropped); four are
carried at the frontier-register layer itself, two only at the cited round-record layer
(Finding 2).

## Additional context found, not a T-014 finding

A prior review, **BC-158**
(`docs/project/reviews/review-2026-09-03-bc158-h060-record-factual-review.md`, also
mapped `lifecycle: retained`), found and ranked four material overstatements in the
*round records* (`exp-058`, `X-012`, `SYNOPSIS.md`, `ledger.md`) as they stood at
08:10–08:35Z on 2026-09-03: a false “the instrument does not exist” claim, a stale “two
independent secondary sources … and they agree” after one was withdrawn, a false
“byte-identical” installation claim, and an over-restored “equivalently Milnor 1968
Lemma 3.1” attribution.
Checked against current HEAD: all four are corrected.
X-012’s own preface documents a “Correction pass, 2026-09-03” that names and fixes
exactly these four items, and grep across the current repository finds none of the
flagged phrases still attached to H-060/T-014 content (the `SYNOPSIS.md`
“byte-identical” and “does not exist” hits under scan are unrelated sentences about
other results).
BC-153’s review (dated later, reading from 08:46Z) reflects the corrected
state throughout — e.g. it already describes the Milnor citation as “X-012 withdrew it”
rather than repeating it.
This is not a T-014 registration finding since BC-158 predates and is independent of the
registration being audited, but it is relevant provenance: the record T-014 rests on had
already been factually corrected before BC-153 reviewed it and before registration.

## Ranked findings (by potential to mislead a reader about what was proved)

1. **Finding 2** (six-gaps completeness) — low.
   Both facts are true, non-blocking per the review, and reachable via a cited artifact;
   only their placement is uneven.
2. **Finding 1** (`SYNOPSIS.md` V3/C3 vs V3/C5) — low, and in the safe direction
   (understates rather than overclaims); an easy one-line fix once flagged.

No finding rises to drift or overclaim against the review’s authorised scope.
Nothing implies an isolation radius, side-free rigidity, global uniqueness,
other-optimum rigidity, unstated Connelly–Whiteley applicability, or method novelty
anywhere in the registered record.

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
