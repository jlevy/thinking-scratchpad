# BC-152 instrument-readiness review — H-060 half-angle chart (independent)

## Provenance and installation

This document is the review deliverable of BC-152’s registered readiness checkpoint for
the n = 5 rigidity instrument, written on 2026-09-03 in the agenda-016 ten-hour run.
Its author wrote only to `scratchpad/bc152-review/` -- a container-local directory
outside the repository, which does not survive the session -- and modified no repository
file.
It is installed here so that the evidence the records cite outlives that directory.

The source was `468` lines with SHA-256
`b0d9ad71612201186e7bb6765d45b34753f8f344cbc118cd308a3bce955ec43e`, and that hash names
the scratchpad source rather than this file.
The installation added this preface and the closing guidelines footer, and reformatted
the body to house Markdown conventions; it altered no classification, verdict, finding,
number, citation, recommendation or claim boundary, and none may be altered here.
References of the form `scratchpad/...` in the body below are the reviewer’s own record
of what was read and where it was written at review time, and are left as written.

* * *

- Reviewer: independent Max reviewer for the 220–245 readiness checkpoint of BC-152,
  agenda-016. Authored none of the code, tests, receipt, exp-058 or X-012.
- Reviewed at: 2026-09-03, 07:37Z–07:55Z. No command was run inside the 08:58Z–09:58Z
  quiet lease.
- Write scope honoured: nothing under `/home/user/squares` was modified; nothing was
  committed. All reviewer artifacts are under this directory.

## Classification: BOUNDED-CAVEAT

> **Superseded.** Re-review of `609e7392` (BOUNDED-CAVEAT: one provenance defect) and
> the final review of the observed-commit pin, corrected constant and provenance fix
> (**PASS**, source digest `9382bae1…6357`) are appended at the end of this document.

Every mathematical and computational claim of the instrument reproduces exactly and
independently. No discrepancy, no reproduction failure, nothing invalid.
The caveat is bounded and precisely stated in §7: two of the eight registered negative
controls (`changed_feature`, `invented_contact`) are structurally incapable of failing
and never touch the binding’s refusal path, so the receipt’s “all eight controls reject”
overstates the evidence for the one refusal the instrument exists to make.
The refusal itself is real — I exercised it (§7) — but it is exercised only in this
reviewer’s scratchpad, not in the instrument’s control suite or its tests.
Under the author’s own stated standard ("a certificate that cannot fail is not
evidence") and the block’s, that obligation is met nominally, not substantively, so this
is not an exact PASS and does not by itself authorize flipping `instrument_ready`.
Converting to PASS needs the ~30-line change in §9 and a re-recorded digest; it does not
need the mathematics re-reviewed.

## 1. What was reviewed, pinned

The files under review changed on disk *during* the review: the author committed
`2f112f4c` ("research: Register the H-060 chart and proof as exp-058 and X-012") at
07:40:30Z, with a formatter pass over the package at 07:39:33Z that landed while my
first `-O` replay was running.
I therefore pinned the review to HEAD `2f112f4c` and redid every replay against it.
Hashes are in `reviewed-file-hashes.txt`; they equal `git show HEAD:` for every file.
The packet must pin the instrument at `2f112f4c` (or later, re-reviewed); “frozen” was
not true while under review.

Semantic content of the format commit: the assert count in the package went from five to
four because two adjacent asserts in `controls.py` were merged into one; no refusal was
removed. The receipt prose still says “the five asserts” (§8, cosmetic).

## 2. Replay from a clean root, both interpreters (item 1)

```
cd packing && export PYTHONPATH=$PWD
./.venv/bin/python3    build_receipt.py bc152-review/replay2/normal
./.venv/bin/python3 -O build_receipt.py bc152-review/replay2/optimized
```

- Digest, both interpreters, both replays (pre- and post-`2f112f4c`):
  `1ab2708623cf4dd077a0f125ba81cf3777088ea8e4d750a56d1dc3f55f807978` — equals the
  author’s claim.
- `cmp` normal vs optimized: identical (JSON and Markdown).
- `cmp` reviewer replay vs author’s retained files: identical
  (`instrument-certificate.json` sha256 `fd221f8c…a032`, `instrument-receipt.md`
  `6324384c…443b`).
- Package hashes were verified unchanged across the replay run.
- `pytest -q tests/test_n5_local_rigidity.py tests/test_n5_rigidity.py`: 41 passed (33
  s), normal interpreter.
  I did not run `pytest -O` and agree with the author that it is not interpreter
  evidence (pytest disables assertion rewriting under `-O`, so test asserts become
  no-ops). The byte comparison above is the evidence and it shows what it claims.

## 3. Exactness of the certified path (item 2)

`grep` over `local_rigidity/*.py` for
`float|decimal|numpy|scipy|math\.|linprog|approx| root_approx`: hits only in docstrings
and the receipt’s own prose.
Imports on the path: `dataclasses`, `typing`, `collections.abc`, `itertools`,
`fractions.Fraction` (exact, receipt printing only), `hashlib`, `json`, `copy`,
`sqpack.field`. The field’s decision procedures (`is_zero` on rational coefficients;
`sign` by rational interval bisection of the isolating interval) are exact; its
`decimal`, `root_approx`, `__float__` exist but are never called by the package.
`load_t012_system` imports only exact functions of the devtool
(`active_contacts, constraint_rows, load_pose, rationalize, row_scales, second_order_terms, unconstrained, variable_names`),
none of which touches `linprog`.

Asserts: four remain (`system.py:533,545,546`, `controls.py:110`). Each guards an
`Optional` attribute that the constructor path already set (noncontact ⇒
`witness_branch`; touching ⇒ `active_branch`, `active_constraint`). Under `-O` a
violated guard would raise `AttributeError` instead of `AssertionError`; no branch
produces a different value.
Confirmed empirically by byte-identical `-O` output.

## 4. The counts, recomputed independently (item 3)

`independent_enumeration.py` shares nothing with the instrument: its own `Q(√2)` on
`Fraction` pairs with an exact sign rule, its own transcription of the pose from
`cases/gobel5/packing.py`, its own SAT margins, rows and jets.
Only at the end does it import the instrument and compare key by key.
Output in `independent_enumeration.out`.

| quantity | reviewer | author | agrees |
| --- | --- | --- | --- |
| wall-corner inequalities | 80 (16 active / 64 inactive / 0 violated) | same | yes |
| minimum inactive wall margin | `1 − √2/4` | same | yes |
| pairs | 10 (4 touching / 6 noncontact / 0 overlap) | same | yes |
| SAT branches / support features | 80 / 320 | same | yes |
| each touching pair | exactly 1 zero branch, 1 zero corner, 7 refuted branches | same | yes |
| noncontact witness margins | `√2/2` on all six | (receipt) | yes |
| `U` | 100 positive + 28 negative = 128 strict | same | yes |
| least-negative competing witness | `−√2/4` | same | yes |
| active system | 20 = 16 walls + `pair/4/3/0/2, 4/0/1/3, 4/2/2/1, 4/1/3/0` | same | yes |
| 400 base margins vs instrument, key by key | 0 mismatches | — | yes |
| 28 negative witnesses, key and value | equal | — | yes |

A missing constraint was the danger; the reviewer’s enumeration is from the pose’s
combinatorics (4 walls × 4 corners × 5 squares; per pair, both hosts × 4 edges × 4
corners) and matches the instrument’s on every key.
The instrument’s own cardinality guard (`expected_cardinality` recomputed from the pose)
is the right shape and is exercised by control C3.

Geometric preconditions the instrument does **not** machine-check but which the SAT
encoding needs: counter-clockwise corner order (so `(dy, −dx)` is outward), right
angles, and centroid-to-edge distance exactly `1/2` (the “1/2” constant is an inradius,
and the unit-normal certificate proves only unit edge length).
I verified all three hold for all five squares.
Undisclosed; true; see §8.

## 5. The `q` factor (item 4)

Reviewer’s own algebra, per pair contact (host square 4, corner `p` of the moving
square, `s = p − c_4`, `n` the host edge’s outward normal):

- `n_⊥ · s = 0` exactly at all four contacts (foot of the perpendicular), so the
  first-order rotation term vanishes; column `w4` is zero in all 20 rows and is the only
  such column.
- Along a true rotation at rate `ω = 1`: `g(δ) = n(δ)·s − 1/2`, `n'' = −n`, so
  `q_geo = −n·s = −1/2`. Matches T-012’s `second_order_terms` exactly.
- Along the chart ray `u4 = t`: the cleared polynomial is
  `G(t) = (n·s)(1 − t²) + 2t (n × s) − (1 + t²)/2 = −t²` exactly (coefficients
  `0, 0, −1` for all four rows).
  Hence `G''(e_u4) = −2` and `G''(e_u4/2) = −1/2`.
- Chain rule: `δ = 2 atan u` has `δ'(0) = 2`, `δ''(0) = 0`, so
  `d²g/du² = 4 g_δδ + 0 = −2`. The chart unit `e_u4` **is** `ω = 2`, and `q` is
  quadratic in the direction: `q(2ω) = 4 q(ω)`. The instrument’s `−2` at `e_u4` and
  `−1/2` at `e_u4/2`, X-012’s `q_chart = 4 q_geo`, `w·q_geo = −√2/2`, `w·q_chart = −2√2`
  are one fact in two normalizations.
  I replayed the self-stress (`1/2` on the six named rows) on my own rows:
  `w·A_rat = 0`, `w·q_geo = −√2/2`, `w·q_chart = −2√2`; ratio exactly 4.
- The binding’s convention, stated precisely: `σ_j · grad G_j = A_j^rat · S` with
  `S = diag(1,1,2)` per square and `σ_j ∈ {1, √2}` the T-012 rationalizing scalar,
  equivalently `grad G_j = A_j^raw · S`; and
  `σ_j · G_j''(e_u4/2) = σ_j · q_j^raw(e_w4)`. Since `w·A^rat = 0` gives the chart
  self-stress `w' = wσ ≥ 0` with `w'·G'' = w·q^scaled < 0`, the sign of the obstruction
  is invariant under any positive rescaling of the direction.
  A factor-of-four error could not flip it; and it would not be silently absorbed
  either: `bind` refuses T-012 data with `q × 4` and with `q / 4` (`refusal_paths.out`).

Not a discrepancy. One wording caveat, §8 item 7: the receipt binds the *restricted*
second jet along the free direction, which is all the registered order-`2m` argument
consumes; it does not verify the full Hessian transform `Jᵀ H J` that X-012 Prop.
6 also mentions. The receipt should say “restricted second jet along `e_u4`”.

## 6. The degeneracy the author found (item 6)

Verified on reviewer rows: exactly 4 of the 12 sibling substitutions have the same
gradient as the contact they replace — `pair/4/3/0/0` for `4/3/0/2`, `4/0/1/1` for
`4/0/1/3`, `4/2/2/3` for `4/2/2/1`, `4/1/3/2` for `4/1/3/0` — in each case the corner
diagonally opposite the contact corner, whose offset difference `(±1, ±1)` is parallel
to the host normal `(±1, ±1)/√2`, so both rotation columns agree; each such sibling has
base margin exactly `√2`. Consequence for the proof’s claim boundary: the active support
feature of each touching pair is identified by its exact zero margin and by nothing
else; a first-order or gradient-based identification is ambiguous at this pose and must
not be used. This must survive into the packet.
`bind` refuses even the degenerate swap, by key agreement
(`missing_from_chart = ('pair/4/3/0/0',)`, `missing_from_t012 = ('pair/4/3/0/2',)`, 19
rows bound, `holds = False`).

## 7. The controls, and the caveat

Genuine perturbation controls (each could fail if the instrument were wrong): C3
`omitted_constraint` (prunes a branch, cardinality guard raises), C5 `side_release`
(exhibits exact feasible neighbours at side + 1/1000 and none at the fixed side), C6
`wrong_chart` (three impostors refused by the chart’s own identities), C7
`certificate_drift` (digest moves), C8 `exp034_angle_and_slide` (feasibility predicate
finds exp-034’s real family at side `1 + 5√2/4` — a positive control — and none of it at
Goebel’s side; sides differ by `3√2/4 − 1 > 0`). C2 `zero_margin` is a thin but real
unit test of `holds_at_base` strictness.

Tautological (cannot fail once `build_system` has succeeded, and do not call `bind`):

- C1 `changed_feature`:
  `rejected = all(margin_is_nonzero and active_key_agreement_breaks)`. The siblings’
  nonzero margins are guaranteed by the classification that already ran (`_pair_report`
  raises `DisjunctiveTouchError` on a second zero corner), and `claimed != t012_keys` is
  true whenever `substitute != contact`. Its only non-trivial output is the
  informational `gradient_indistinguishable = 4`.
- C4 `invented_contact`: `invented = inactive_walls[0]`, whose margin is positive by the
  property’s definition; `claimed != t012_keys` is true whenever the added key is not
  already active.

The binding’s refusal — the certificate this instrument exists to produce — has no
negative coverage in the author’s suite or tests.
I exercised it (`refusal_paths.py`, output `refusal_paths.out`): `bind` returns
`holds = False` for a swapped contact key (even the gradient-degenerate one), an
appended contact, a sign-flipped `q`, a wrong row scale, and `q` scaled by 4 or 1/4. So
the instrument refuses; the suite does not show it.

## 8. Gaps

Author-disclosed, checked accurate:

1. `isolation_decided = False` unconditionally — confirmed in `Determination`; the
   receipt, exp-058 (`decision: unresolved`, `instrument_ready` false) and the H-060
   file (`instrument_ready: false`) all agree; no target determination ran.
2. Four cited mathematical inputs (SAT, `2 atan` topology, convex-hull containment,
   polynomial continuity) — accurately listed; each is used exactly as stated and the
   reduction “on `U`, feasible ⇔ the 20 active inequalities” is sound given them (both
   directions checked by me: seven refuted branches collapse the disjunction; the active
   branch’s three slack siblings keep it a single inequality).
3. Probe (180 points) and reduction audit (244 points) are corroboration only —
   accurately labelled.
   Weaker than it reads: all 244 audit points lie inside `U`, so the audit never samples
   `U`’s boundary or its complement.
4. Single-support-feature touches only; edge-flush and corner-on-corner refused by
   `DisjunctiveTouchError` — confirmed, and the edge-flush test exists.

Undisclosed, found by this review:

5. **C1 and C4 are tautological** (§7). Material for readiness; bounded fix (§9).
6. Unchecked geometric preconditions (CCW order, right angles, inradius 1/2) behind the
   SAT constant and the outward-normal convention — verified true by me; should be
   machine-checked or declared alongside the four cited inputs.
7. The second-jet binding is the restricted jet along `e_u4`, not the full Hessian
   transform; sufficient for the registered argument, but the receipt’s “second jets”
   should say so.
8. Receipt prose “the five asserts” is stale; four exist after `2f112f4c`.
9. The instrument is a new package (`sqpack.local_rigidity`) binding to
   `devtools.assess_n5_rigidity`, not an extension of it as the hypothesis’s instrument
   text says. Structural, not substantive; the binding-to-the-devtool is the right design
   and the packet should say the instrument text was realised this way.
10. `instrument_ready` does not gate on `count_disagreements` (computed only in
    `build_receipt.py`); a receipt disagreeing with the agenda would still print
    `instrument_ready: True`. Defensible under “computed, never adopted”, but the packet
    should state that the agenda comparison is informational.
11. The instrument was edited and committed while under review (§1). Pin `2f112f4c`.

Nothing found that makes an infeasible direction look feasible, that weakens the frozen
criterion, or that changes any exact quantity.

## 9. What converts this to PASS

1. Replace C1 and C4 with controls that perturb T-012’s contact list and call `bind`:
   rename one contact key onto its gradient-degenerate sibling (require `holds = False`,
   `missing_from_chart`/`missing_from_t012` non-empty), and append one inactive wall key
   (require `holds = False`). `refusal_paths.py` is a template.
   Keep the degeneracy finding as a recorded finding, not as the control’s rejection
   mechanism.
2. Add the same two cases to `tests/test_n5_local_rigidity.py`.
3. Fix “five asserts” → “four”; say “restricted second jet along `e_u4`”; either
   machine-check CCW/right-angle/inradius or add them to `DECLARED_MATHEMATICAL_INPUTS`.
4. Re-run `build_receipt.py` under both interpreters and re-record the digest (it will
   change, because control findings are in the payload).
   Re-pin the commit.

No re-review of the chart identities, counts, margins, binding or `q` is needed; this
document is the independent verification of those and it stands for the pinned code.

## 10. Novelty basis (S3 as scoped): accepted, with two qualifications

Checked by me:

- Kingbird’s rigid page (fetched 07:51Z): the definition is verbatim as X-012 quotes it
  ("cannot be continuously transformed into any other valid packing without changing the
  size of its enclosing square"); `n = 5` is listed as rigid; no method, argument or
  proof appears. The definition coincides with H-060’s fixed-side notion.
- Goebel 1979: no PDF text tool is installed here; a stdlib decompression of the PDF’s
  30 content streams yields ~29k characters of text operands with zero occurrences of
  “rigid” or “uniqu”. Partial corroboration of X-012’s “0 hits over 21 pages” (my
  extraction is crude and I could not confirm it reached the square-packing section);
  X-012’s full text-layer extraction is the primary evidence and I did not reproduce it.
- Friedman DS7 not annotating `n = 5`: taken from `frontier/evidence.yaml`
  (`E-n005-second-order-rigidity.novelty_basis`), not re-verified.

Qualifications:

1. The clause “not covered by any stated rigidity theorem for polygon contacts” ([CW96]
   Theorem 4.3.1 shape match, the disk-jamming sign requirement, Donev et al.
   2007\) is, by X-012’s own §7.1 and §8.3, the coordinator’s survey finding, unverified
   against the primary texts by the lane — and not by me.
   It is not needed for S3 ("first exact proof of a property Kingbird asserts without
   proof; closing principle and Connelly–Whiteley proof shape excluded from the claim")
   and should be carried as an unverified survey assertion, not as part of the claim.
2. Novelty is registered by BC-153 only after the target evaluation passes; at this
   checkpoint the acceptance is provisional on the target, and on X-012’s
   curve-selection citation obligation (BCR Prop.
   8.1.13 / Milnor Lemma 3.1, still secondary quotations).

With those, I accept S3 as scoped: the statement is Kingbird’s, the proof would be the
first exact one, and no method novelty is claimed.

## 11. Reviewer artifacts

- `reviewed-file-hashes.txt` — sha256 of every reviewed file at `2f112f4c`.
- `replay/`, `replay2/` — clean-root replays (pre- and post-commit), normal and `-O`.
- `independent_enumeration.py`, `.out` — the reviewer’s recomputation (§4–6).
- `refusal_paths.py`, `.out` — the binding’s refusal exercised (§7).
- `gobel-1979.txt` was not produced (no text tool); see §10.

* * *

# Re-review of the C1/C4 repair (commit `609e7392`), 08:08Z–08:14Z

Narrow scope as directed: the mathematics was not re-derived.
Package hashes at `609e7392` are in `rereview-file-hashes.txt` and were verified
unchanged across the replay.

## Classification: BOUNDED-CAVEAT (instrument passes every item; one provenance defect in the packet)

Every item the coordinator listed passes.
The single remaining defect is not in the instrument but in the packet’s provenance: the
digested payload carries `"pinned_commit": "2f112f4c…"` and the receipt says “this
packet is pinned to commit `2f112f4c`”, yet the code at `2f112f4c` cannot produce this
payload — its `receipt.py` has no `pose_shape` field, and its `assess()` does not accept
`expected_counts`, so the current build script raises `TypeError` there.
The commit whose package produced the reproduced digest is `609e7392` (HEAD). A future
replayer following the packet’s own pin would get CANNOT-REPRODUCE. Closure is
mechanical and needs no repository change: set `PINNED_COMMIT` to
`609e739243827f537025ad800d8eb9eab3ce1c8c` in the scratchpad `build_receipt.py`,
regenerate under both interpreters, and confirm the new certificate differs from the
current one *only* in `pinned_commit` (the digest will move).
On that byte-level confirmation this re-review’s verdict is PASS; nothing else needs my
eyes again.

## 1. C1 and C4 now bite — verified by removal (`guard_is_load_bearing.py`, `.out`)

| configuration | C1 rejected | C4 rejected |
| --- | --- | --- |
| guard and `bind` intact | True | True |
| `require_active_margins_zero` replaced by a no-op | **False** | **False** |
| `bind` replaced by an always-holding certificate | **False** | **False** |
| both removed | False | False |

Both refusal paths are load-bearing for both controls; neither control can reject
without the instrument refusing.
C1’s predicate requires `key_swapped_guard_refused`, `key_swapped_binding_refused` and
`forgery_guard_refused` for all 12 substitutions (`forgery_binding_refused` is recorded,
not required — correct, since the gradient alone misses four).
C4 requires the guard, `not certificate.holds`, and the invented key in
`missing_from_t012`; the mutated active set has 21 members.

## 2. The guard is on the real path, and recomputation is what sees the forgery

- Replacing `instrument.require_active_margins_zero` with a raiser makes `assess()`
  raise: the guard runs on the assessment path, immediately after `build_system`, not
  only in the controls.
- Key-preserving forgery `pair/4/3/0/2 ← pair/4/3/0/0`: cached margin `0`; recomputed
  value `poly[0,1] = √2`; guard refuses.
  Invented `wall/0/0/right`: enters the active set (size 21) on its cached `0`;
  recomputed `2 + √2/2`; guard refuses.
  A cache read would pass both; the re-evaluation is the detection.
- `assess(..., expected_counts={"active_total": 19})` → `instrument_ready = False`,
  refusal “declared counts disagree with the pose on ['active_total']”. The count gate
  is real and on the path.

## 3. The claimed finding — true, with one qualification that belongs in the claim boundary

Independently, from my own rows (`degeneracy_order.py`, `.out`): the gradient
distinguishes 8 of 12 sibling substitutions; the second-order term along the flex
distinguishes 12 of 12. So the support-feature degeneracy is first-order only —
confirmed. But the second jet is doing less *independent* work than “catches all 12”
suggests: along a pure host rotation the term is
`q_host(j′) = −n·s′ = −(margin(j′) + 1/2)` exactly, i.e. an affine function of the
sibling’s own base margin (chart form `G″(e_u4/2) = −(m + 1)/2`). It separates support
features precisely when their margins do, and would not separate two siblings of equal
margin. The claim boundary should say: first-order rows do not identify the support
feature; the second-order term along the flex does at this pose only because it is the
base margin in disguise; identification rests on the exact recomputed margin, which is
the guard. The receipt’s own wording — “the recomputed base margin is what decides” — is
the right one.

## 4. The four undisclosed gaps — closed, spot-checked

- Pose preconditions: `pose_shape_certificate` — shoelace `+2`, unit edges, right
  angles, inradius `1/2` — 65 checks (5 + 20 + 20 + 20), all hold, wired into
  `require_valid` (a CW pose now refuses before any margin is read).
- Audit widened to 304 points, 252 inside `U`, 52 outside and skipped (denominators 1
  and 2 added). Significant, as the coordinator says: the inside-`U` filter had never
  excluded a point before and so had never run; it now demonstrably does.
  The new `sample_is_not_adversarial` caveat is accurate.
- Readiness refuses on a count disagreement (§2 above).
- Devtool deviation recorded in the receipt’s claim boundary with its layering reason.
- Also: the receipt now says “four asserts”; the restricted-jet scope is stated.

## 5. Replay — reproduced exactly

Clean root `replay3/`, author’s current build script, normal and `-O`: digest
`ba99ccccd7303f260f48c62a10fb9b6dc43ca3e8ff804646ef5de89a48967971`; certificate sha256
`69256c99…193`, receipt `81a5d5c0…4c9`; byte-identical between interpreters and against
the author’s retained files; 45 tests pass (37.6 s).

## Notes outside the classification

- The repair commit’s message says “record two defects”, but the two entries it adds
  (`D-422`, `D-423`) concern other lanes’ work; the tautological-controls finding has no
  `defects.yaml` entry as of `609e7392`. A documentation-pass item, not an instrument
  one.
- The working tree carries an unrelated uncommitted modification
  (`tests/test_campaign_runner_trust_boundary.py`); the package itself is clean at HEAD.
- Timing: all commands completed by 08:14Z, before the 08:58Z lease.

* * *

# Final review — pin mechanism, corrected constant, provenance fix (08:31Z–08:36Z)

Scope as directed: the observed-commit pin mechanism, the corrected second-jet constant,
and the provenance fix.
Nothing mathematical was re-derived.
Package hashes at HEAD `fe8bccde` are in `final-file-hashes.txt`; the package is
identical to what the author ran at `d45a3269` (all eight recorded file hashes match the
working tree).

## Classification: PASS

## 1. The pin mechanism — replayed one commit later, and the separation held exactly

I replayed from a clean root (`replay4/`) at HEAD `fe8bccde`, one commit past the
author’s observed `d45a3269`, with the package untouched in between.
Normal and `-O` byte-identical.
Against the author’s final certificate the leaf-diff shows **exactly one differing
leaf**, `/claim_boundary/provenance/pinned_commit` (`d45a3269` → `fe8bccde`), and the
receipts differ in exactly the three lines that print the commit or the payload digest.
Source digest identical on both sides, `tree_matches_pinned_commit: True`,
`paths_differing: []`. That is the author’s separation demonstrated on a real unrelated
commit rather than argued: the record moved, the instrument did not.

`source_digest` reproduced independently from the recipe (rolling SHA-256 over
`path + sha256hex`, the eight package files repo-relative in sorted order, then the
driver as `build_receipt.py`): `9382bae1…6357`, equal to the author’s. The packet’s
`source/` carries the nine files with matching hashes, so the packet replays even
without a commit. The receipt’s “checking it out and rerunning the driver is a complete
replay” sentence is in the `else` branch of `tree_matches` (the other branch tells the
replayer to find a containing commit and re-pin), so it cannot be printed falsely.

**Judgment on the separation:** sound as a two-signal design, with one scope caveat on
the wording. `source_digest` covers the package and the driver but not the three inputs
the instrument reads — `sqpack/field.py`, `cases/gobel5/packing.py`,
`devtools/assess_n5_rigidity.py`. A change to any of those changes what the instrument
computes (and would move the payload digest through the margins and rows) while leaving
`source_digest` unchanged; so “compare `source_digest` to decide whether the instrument
differs” is exact for the package’s own code, not for its inputs.
Replayability is not affected — when `tree_matches` is true the observed commit fixes
those three — but the sentence should either say “the package’s code” or the three paths
should join the hashed set.
Recommendation, not a condition.
Minor: the provenance `note` says the commit is “recorded only when the working tree
agrees”; the code records it always and flags disagreement separately, which is the
better behaviour — the note should say that.

## 2. The corrected constant — confirmed; the author is right about the chart polynomial

On all 16 support features of the four contact branches, using the instrument’s cleared
polynomials (`constant_check.out`): `G″(e_u4) = −2(m + 1)` exactly, equivalently
`G″(e_u4/2) = −(m + 1)/2`. The author’s derivation is correct: `G = D_h D_k g`,
`D″(0) = 2`, `g′(0) = 0` along the host rotation, so
`G″ = 2m + 4·g_δδ = 2m − 4(m + ½) = −2(m + 1)`.

My `q_host(j′) = −(m + ½)` is the second derivative of the *geometric* gap `g` at
`ω = 1` and was labelled as such; it is not the chart’s jet.
The two differ by exactly `D″(0)·g(0) = 2m`, zero on active rows, which is why the
binding (active rows only) was never touched.
My addendum also gave the chart form `G″(e_u4/2) = −(m + 1)/2`, which equals the
author’s `−2(m + 1)/4`; so the derivations are consistent, and the constant to carry in
the record is the receipt’s, because it is the object the binding compares.
The structural conclusion stands unchanged: the restricted second jet along the flex is
an exact affine function of the support feature’s own base margin, separates support
features precisely when their margins do, and is not an independent identifier.
The receipt records `second_jet_is_an_independent_identifier: false` and the affine law
holds on all 12 substitutions; a dedicated test pins it; 46 tests pass.

## 3. The provenance fix — spot-checked

The provenance block resolves real paths: the eight package files repo-relative, the
driver by bare name matching the packet’s `source/build_receipt.py` (hash `d82964cb…`).
`paths_differing` is computed from `git diff --name-only HEAD -- <package>` and
`git ls-files --others --exclude-standard -- <package>`, which emit bare paths and
cannot lose a character; the working tree’s unrelated uncommitted `defects.md` /
`packing/defects.yaml` correctly do not appear because they are outside the package.

## 4. What changed since the re-reviewed revision (leaf-diff `ba99cccc` → final)

Five changed leaves (C1’s `detail` and `finding` wording; C7’s three derived drift
digests), the new provenance block, and the affine-law fields.
No margin, count, certificate, binding row, or control verdict moved.
The narrow scope is confirmed by the diff itself.

## Record

Replay at `fe8bccde`: payload digest `eccf0e1e…e93f` (author’s at `d45a3269`:
`743fd18a…cc67`); source digest `9382bae1…6357` on both; certificate/receipt
byte-identical across interpreters; 46 tests pass.
All commands completed by 08:36Z, before the 08:58Z lease.
Artifacts: `replay4/`, `final_checks.py/.out`, `constant_check.out`,
`final-file-hashes.txt`.

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
