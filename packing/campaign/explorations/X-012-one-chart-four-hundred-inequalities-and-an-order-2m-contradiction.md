---
title: X-012 — one chart, four hundred inequalities, and an order-2m contradiction
softschema:
  contract: packing.squares:Exploration/v1
  schema: ../schemas/exploration.schema.yaml
  envelope: exploration
  status: enforced
exploration:
  id: X-012
  title: One chart, four hundred inequalities, and an order-2m contradiction
  date: '2026-09-03'
  author: Claude (agent), in the BC-152 n = 5 proof lane of agenda-016, bead think-760r
  campaign: packing.squares
  brief: >-
    BC-152 asked whether Goebel's exact n = 5 optimum is locally rigid at fixed side under
    H-060's preregistered neighbourhood, curve-selection and coefficient criterion. This is
    that lane's frozen mathematics: an intrinsic half-angle chart, injective on all of
    R^15, whose cleared denominators are 1 + t_i^2 >= 1 and whose second-jet transfer is
    J = diag(1, 1, 2) per square with no second-order angle correction; a complete
    accounting of all 400 elementary polynomial inequalities that define a valid packing at
    the exact side, which confirms the agenda's 16/64 wall and 4/6 pair counts with no
    discrepancy and pins the local feasible set to exactly the twenty active rows on a
    neighbourhood defined by 128 strict sign conditions; T-012's cone and self-stress
    transferred to the chart, with all 28 Farkas certificates replaying and
    w . q_chart = -2 sqrt 2 < 0; and an induction on the Taylor coefficients of a putative
    analytic feasible arc that reaches a contradiction at order 2m. A second, corroborating
    proof by the classical second-order sufficiency principle is recorded and explicitly
    labelled non-acceptance; its multiplier scaling is not cosmetic, since at mu = 1 the
    inequality holds in the chart normalization and fails in the (c, theta) one.

    This report on its own did not resolve H-060; BC-153's independent review did, on
    2026-09-03, and exp-058 carries that determination. The acceptance route is the
    registered curve-selection and coefficient argument, and the two obligations this
    report left open are now closed or judged non-blocking: the W7 executable instrument
    with its receipt and eight rejecting controls, built by a separate lane after this
    packet was frozen, passed its independent readiness review, so instrument_ready is
    true; and primary-text confirmation of the curve-selection statement, which a separate
    verification lane answered YES on the mathematics, the statement being attested
    verbatim by one of BCR's own authors, still without reaching the printed BCR page --
    the BC-153 reviewer judged that non-blocking after deriving the same statement from
    primary-text Basu-Pollack-Roy plus the one-variable Puiseux fact. The
    admissible novelty claim is S3, not S4. The closing principle is classical and the
    curve-selection proof shape matches Connelly-Whiteley 1996 Theorem 4.3.1; neither is
    claimed as new. Control C8 confirms exp-034's family is not a refutation: it sits at
    container side 1 + 5 sqrt 2 / 4, exactly 3 sqrt 2 / 4 - 1 above Goebel's side, so the
    two feasible sets are disjoint. Reviewed and passed; the frontier and result-register
    changes that followed are T-014 and the n = 5 rigidity property, and they were made by
    BC-153, not by this report.
  sources:
  - packing/campaign/hypotheses/H-060-n5-local-rigidity.md
  - packing/campaign/explorations/X-007-the-n5-optimum-flexes-once-and-that-once-is-shut.md
  - packing/campaign/agendas/agenda-016-results-first-continuation-rigidity-and-remediation.md
  - packing/campaign/series/series-000-smoke-and-calibration/results/bc-049-n5-rigidity-certificates.json
  - packing/campaign/series/series-000-smoke-and-calibration/results/exp-058-h-060-n5-chart-and-proof.json
  - packing/cases/gobel5/packing.py
  - packing/devtools/assess_n5_rigidity.py
  - packing/resources/papers/gobel-1979-geometrical-packing-and-covering-problems.pdf
  proposes: []
---
# X-012 — One Chart, Four Hundred Inequalities, and an Order-`2m` Contradiction

**Date:** 2026-09-03

**Status:** Reviewed and passed.
The frozen `BC-152` proof packet, installed unchanged in substance.
`H-060` is **confirmed** and `instrument_ready` is **true**: `BC-153`’s independent
review returned PASS on 2026-09-03, and the frontier property and the `T-014` register
entry that followed were made there, not by this report.

**Owns:** The mathematics of `BC-152` phase 0–105 at `n = 5`. It owns no code: the `W7`
executable instrument, its receipt and the eight rejecting controls of §6 belong to a
separate lane. That lane built them after this packet was frozen, at `6580a9fd`, as the
package `src/sqpack/local_rigidity/`; their readiness review returned BOUNDED-CAVEAT
twice and then **PASS**, which is what moved `instrument_ready` to true (§8.4).

## Provenance and installation

This report is the frozen `BC-152` proof packet, whose own header block read:

- **Lane:** BC-152 (agenda-016), n = 5, phase 0–105 (mathematics, not code).
- **Hypothesis:** [H-060](../hypotheses/H-060-n5-local-rigidity.md), Goebel’s exact n =
  5 optimum is locally rigid at fixed side.
- **Inputs held fixed:** T-012 (certificate record
  [`bc-049-n5-rigidity-certificates.json`](../series/series-000-smoke-and-calibration/results/bc-049-n5-rigidity-certificates.json)),
  [X-007](X-007-the-n5-optimum-flexes-once-and-that-once-is-shut.md),
  [`cases/gobel5/packing.py`](../../cases/gobel5/packing.py),
  [`devtools/assess_n5_rigidity.py`](../../devtools/assess_n5_rigidity.py).
- **Date:** 2026-09-03.
- **Write scope:** the packet lane wrote only to its own scratchpad directory.
  No repository file was modified by it.

The packet is `925` lines with SHA-256
`28343b743e689fc99968d589a542d9022d061de8ec3ae5100bf4ef4930e40b6b`, and that hash names
the frozen source rather than this file: the body from the rule below reproduces the
packet’s content, reformatted to house Markdown conventions.
What this installation added is the frontmatter, this preface, the artifact table
immediately below, and the closing guidelines footer; no mathematical statement, number,
count, citation or claim boundary was altered by the installation, and none may be
altered here — the packet is frozen, and the hash above is what a reviewer checks
against.

**Provenance pass, 2026-09-03.** One later pass has touched the body, and it is named
here so that a reviewer diffing against the frozen source knows what to expect.
The packet’s open obligation `O2` — primary-text confirmation of the curve-selection
statement — was worked by a separate verification lane, which returned **YES**: the
statement as used follows from the theorem cited, and §4 is sound as written.
Its recommendations were provenance and completeness only.
Applying them rewrote the citation apparatus of §4.1 (including one citation withdrawn),
de-flagged the Milnor statement of §4.1 from “from memory”, added two items to that
route’s reduction, added the nonconstancy clause and the hypothesis inventory to §4.2,
and updated §8.3, the closing obligation note, the replay-artifact note above and this
record’s brief. No statement, number, count, margin, inequality, proof step or claim
boundary changed; at that pass `H-060` was still unresolved and `instrument_ready` still
false, and the printed BCR page is still unread today.

**Correction pass, 2026-09-03.** A second later pass, following an independent factual
review of the round records against the artifacts they rest on, corrected four
overstatements in this document: the “do not exist yet” description of the instrument
above and in §8.4, which was false when written; the “equivalently Milnor 1968 Lemma
3.1” clause in the closing obligation, which restores exactly the over-attribution §4.1
withdraws a citation for; the survey clause “not covered by any stated rigidity theorem
for polygon contacts”, which is demoted out of the novelty claim in §7.4 and §8.5; and
§7.3’s list of thirteen rigid `n`, which is now recorded as in tension with the archived
page. No statement, number, count, margin, inequality or proof step changed, and every
correction makes this record weaker.

**Status pass, 2026-09-03.** A third later pass, after `BC-153`’s independent review
returned **PASS**, corrected the six places where this document still said `H-060` was
unresolved and `instrument_ready` false: the brief, the status line, the *Owns*
paragraph, the provenance-pass note above, §8.4, and the closing obligation.
Each now says what is true after the review, and §8.4 and the closing obligation also
record the readiness `PASS` and what `BC-153` did with the unread `BCR` page.
No statement, number, count, margin, inequality, proof step or claim boundary changed
here either. One thing the review asked for is deliberately *not* done: §1.3 (i)'s
one-line argument that a nonconstant continuous path leaves the singleton is terse — a
path can be constant on an initial segment, so it wants a sentence taking the supremum
of that interval — and adding it would put a new proof step into a frozen packet.
It is recorded as a gap in `exp-058`’s amendment instead, where the review’s other six
gaps are, and the conclusion it supports is unaffected.

The packet’s replay scripts are **not** installed as repository code.
Nothing under `campaign/` is code — the campaign tree holds records — and the executable
form of this mathematics was built after this packet was frozen, as
`src/sqpack/local_rigidity/`, which binds to
[`devtools/assess_n5_rigidity.py`](../../devtools/assess_n5_rigidity.py) rather than
extending it as `W7`’s text asks.
Promoting seven scratchpad scripts to tooling would cross that boundary and leave a
measurement in one-off code.
Their verbatim source, sizes and SHA-256 digests are retained instead as the round’s raw
run data, in
[`exp-058-h-060-n5-chart-and-proof.json`](../series/series-000-smoke-and-calibration/results/exp-058-h-060-n5-chart-and-proof.json),
which is also where the round record
[`exp-058`](../series/series-000-smoke-and-calibration/experiments/exp-058-h-060-n5-chart-and-proof.md)
points.

## Replay artifacts

All seven scripts are read-only against the repository and were all re-run on 2026-09-03
under `packing/.venv/bin/python3` = Python 3.14.7, sympy 1.14.0. Their retained source
and digests are in the results record named above.

| File | What it replays |
| --- | --- |
| `verify_chart.py` | pose = `cases.gobel5` corner-for-corner; 80 wall and 320 pair elementary margins; the 20 chart polynomials and their 2-jets; `A_chart = A_geo J`, `H_chart = J^T H_geo J`, `q_chart = 4 q_geo`; the 28 Farkas certificates and the self-stress of T-012 replayed on the chart rows; the flex line restricted gap `= -t4^2` |
| `print_polys.py` | prints the 20 cleared polynomials, gradient rows and `q` (table in §2.5) |
| `margins.py` | the multiset of the 64 inactive wall margins (table in §3.3) |
| `midpoint_check.py` | each active pair corner has along-edge parameter exactly `1/2` (no D-390 endpoint incidence) |
| `control_exp034.py` | pre-run of the exp-034 negative control through the T-012 machinery (§6) |
| `c8_side_check.py` | exact proof that the exp-034 family is at side `1 + 5√2/4 ≠ 2 + √2/2`, infeasible at Goebel’s side, and at positive distance from `P^0` (§6, C8 note) |
| `sosc_check.py` | the numbers of §5.7: `w · q_geo = -√2/2`, `w · q_chart = -2√2`, the `mu = 1` signs in both normalizations, the threshold `mu > 2/(-w · q)` |

The packet also drew on text extractions of `gobel-1979`, the Whiteley handbook chapter,
`arXiv:2301.00128` and `arXiv:2504.03348` for §4 and §7. Those are literature, not
first-party artifacts; retaining them is a `packing/resources/` decision outside this
round’s write scope, and §7.3’s recommendation to archive the Kingbird page stands
unactioned for the same reason.
`arXiv:2301.00128` is no longer relied on for §4; §4.1 records the withdrawal and why.

`verify_chart.py` ends with `ALL CHECKS PASSED`; every number quoted below is taken from
its output or from the repository’s own certificate record.

* * *

## 0. What this document claims, in one paragraph

Let `s = 2 + sqrt(2)/2`. Section 2 gives an explicit half-angle chart `Phi : R^15 -> C`
onto an open subset of the labeled configuration space `C = (R^2 x S^1)^5`, injective on
all of `R^15`, whose cleared denominators are `1 + t_i^2 >= 1` everywhere.
Section 3 accounts for all 400 elementary polynomial inequalities that define “valid
packing at side `s`” (80 wall–corner, 320 pair) and proves, from exact base margins and
continuity only, that on an explicitly defined open neighbourhood `N` of the pose the
feasible set is exactly `{ g_1 >= 0, ..., g_20 >= 0 }` for the twenty active
contact-normal polynomials.
Section 4 states the Nash curve selection lemma and verifies its hypotheses for
`F \ {0}`. Section 5 proves, by an induction on the Taylor coefficients of a putative
nonconstant analytic feasible arc through order `2m`, that no such arc exists, using
only T-012’s first-order cone and second-order self-stress transferred to the chart by
the transform `J = diag(1,1,2)^{(+)5}` and the positive row scaling
`S = diag(1 on wall rows, sqrt 2 on pair rows)`. Together: **the pose is an isolated
point of the fixed-side feasible set**, i.e. H-060’s target property.
Section 5.7 records, at the coordinator’s direction, an independent corroborating second
proof by classical second-order sufficiency; it is not the acceptance route, which is
the registered curve-selection-and-coefficient argument alone.
Section 8 states exactly what is proved, what is cited, what is claimed as new (bound to
the coordinator’s novelty scoping), and what remains open; the single largest remaining
obligation is named there.

* * *

## 1. Setting

### 1.1 The pose, exactly

Field `Q(sqrt 2)`, `r := sqrt 2`, side `s = 2 + r/2` (`2 s^2 - 8 s + 7 = 0`). Square `i`
has centre `c_i`, angle `theta_i`, and corners `p_{i,k} = c_i + R(theta_i) rho_k`,
`k = 0..3`, with body offsets

```
rho_0 = (-1/2, -1/2)   rho_1 = (1/2, -1/2)   rho_2 = (1/2, 1/2)   rho_3 = (-1/2, 1/2)
```

(counter-clockwise; this is the corner order of `cases/gobel5/packing.py`, checked
corner-for-corner by `verify_chart.py`). Edge `e` runs from corner `e` to corner `e+1`;
its outward unit normal is `n_{i,e} = R(theta_i) nu_e` with

```
nu_0 = (0, -1)   nu_1 = (1, 0)   nu_2 = (0, 1)   nu_3 = (-1, 0).
```

| square | centre `c_i^0` | `theta_i^0` |
| --- | --- | --- |
| 0 | `(1/2, 1/2)` | 0 |
| 1 | `(s - 1/2, 1/2)` | 0 |
| 2 | `(1/2, s - 1/2)` | 0 |
| 3 | `(s - 1/2, s - 1/2)` | 0 |
| 4 | `(s/2, s/2) = (1 + r/4, 1 + r/4)` | `pi/4` |

Square 4’s corners are `(s/2 +- r/2, s/2)` and `(s/2, s/2 +- r/2)`; its extreme
coordinate `s/2 + r/2 = 1 + 3r/4 ~ 2.06 < s`, so it touches no wall (margin
`1 - r/4 ~ 0.646`, §3.3).

### 1.2 Valid packing, feasible set

A configuration `P = (c_i, theta_i)_{i<5}` is a **valid packing at side `s`** when every
closed square `Q_i(P) = c_i + R(theta_i)[-1/2, 1/2]^2` lies in the closed container
`[0, s]^2` and the interiors of `Q_i, Q_j` are disjoint for `i != j`. This is the
definition in `sqpack/verify.py` ("every square lies inside the container and every pair
of squares has disjoint interiors") and in Martin 2000 (archive), and it allows
touching.

`Feas(s) subset C = (R^2 x S^1)^5` is the set of valid packings at side `s`. The
configuration space is *labeled*: squares and their corners carry indices, and `theta_i`
is an angle, not an angle mod `pi/2`.

### 1.3 Local rigidity at fixed side

**Definition.** `P^0` is *locally rigid at fixed side `s`* when `P^0` is an isolated
point of `Feas(s)`: there is an open `W ∋ P^0` in `C` with `Feas(s) ∩ W = {P^0}`.

Equivalent formulations that the proof also delivers: (i) there is no nonconstant
continuous path `[0,1] -> Feas(s)` starting at `P^0`; (ii) there is no sequence of
feasible configurations `P^(k) != P^0` with `P^(k) -> P^0`. (i) follows from isolation
because a nonconstant continuous path leaves every neighbourhood’s singleton; (ii) is
the definition restated.
H-060’s rejection clause ("a verified nonconstant feasible arc through the pose or an
exact sequence of distinct feasible poses converging to it") is exactly the negation of
(i)/(ii).

**Remark (unlabeled squares, Kingbird’s notion).** Kingbird defines: “A packing is rigid
when it cannot be continuously transformed into any other valid packing without changing
the size of its enclosing square” (retrieved 2026-09-03, §7.3). That is a statement
about squares as *sets*. The map `(c, theta) -> c + R(theta)[-1/2,1/2]^2` from
`R^2 x S^1` to placed squares is a 4-fold covering (fibre `theta + k pi/2`), so a
continuous path of placed squares lifts uniquely to a continuous path in `(c, theta)`
from any lift of its start.
Hence isolation of the labeled pose implies Kingbird’s fixed-side rigidity of the
unlabeled packing. Relabelings and container symmetries give *other* labeled poses at
positive distance (e.g. `theta_4 + pi/2` is at chart distance `t_4 = 1`), which
isolation does not see and does not need to.

* * *

## 2. (a) The intrinsic half-angle chart

### 2.1 Definition

Chart coordinates `z = (dx_i, dy_i, t_i)_{i<5} in R^15`, ordered as T-012’s
`(vx_i, vy_i, w_i)`. Define

```
Phi(z) = ( c_i^0 + (dx_i, dy_i),  theta_i^0 + 2 arctan t_i )_{i<5}.
```

Then `cos(2 arctan t) = (1 - t^2)/(1 + t^2)`, `sin(2 arctan t) = 2t/(1 + t^2)`, so

```
R(theta_i) = R(theta_i^0) M(t_i) / (1 + t_i^2),     M(t) = [[1 - t^2, -2t], [2t, 1 - t^2]],
p_{i,k}(z) = c_i^0 + (dx_i, dy_i) + R(theta_i^0) M(t_i) rho_k / (1 + t_i^2),
n_{h,e}(z) = R(theta_h^0) M(t_h) nu_e / (1 + t_h^2).
```

Every corner and normal is a rational function of `z` with denominator a product of
factors `1 + t_i^2`, and numerator a polynomial with coefficients in `Q(sqrt 2)`.

### 2.2 Lemma 1 (injectivity, on all of `R^15`)

`Phi` is a homeomorphism of `R^15` onto the open set
`U = { P in C : theta_i in (theta_i^0 - pi, theta_i^0 + pi) for all i }`, and
`Phi(0) = P^0`.

*Proof.* The translation part is the identity.
`t -> theta^0 + 2 arctan t` is a real-analytic bijection
`R -> (theta^0 - pi, theta^0 + pi)` (derivative `2/(1+t^2) > 0`), with analytic inverse
`theta -> tan((theta - theta^0)/2)`. Products of homeomorphisms are homeomorphisms.
`U` is open in `C` because it is a product of open arcs of `S^1` and copies of `R^2`. □

So the “neighbourhood on which the chart is injective” is the whole of `R^15`; nothing
smaller is needed, and `U` is an open neighbourhood of `P^0` in `C`.

### 2.3 Lemma 2 (denominators)

For every `i`, `D_i(z) := 1 + t_i^2 >= 1 > 0` on all of `R^15`, and `D_i(0) = 1`,
`grad D_i(0) = 0`. The same holds for every product of the `D_i`.

*Proof.* `t_i^2 >= 0`; `d/dt (1 + t^2) = 2t` vanishes at `0`; a product of functions
with value 1 and zero gradient at 0 has value 1 and zero gradient at 0. □

Consequently, for any geometric margin `G` that is a rational function with denominator
`D`, the **cleared polynomial** `G~ := D · G` has the same sign as `G` at every point of
`R^15`. All sign conditions below are therefore stated on cleared polynomials without
loss.

### 2.4 Lemma 3 (2-jet transfer to T-012’s coordinates)

Let `G(c, theta)` be real-analytic near `P^0`, with `G(P^0) = 0`, and let `D` be a
product of factors `1 + t_i^2`. Put `G~(z) := D(z) · G(Phi(z))` and
`J := diag(1, 1, 2)^{(+)5}` (the 15 x 15 diagonal matrix with `2` in the `t_i` slots).
Then

```
grad G~(0) = J^T grad G(P^0),        Hess G~(0) = J^T Hess G(P^0) J,
```

where `grad G`, `Hess G` are taken in the coordinates `(c_i, theta_i)` that T-012’s
`constraint_rows` and `second_order_terms` differentiate.

*Proof.* `2 arctan t = 2t - (2/3) t^3 + O(t^5)`, so `Phi(z) = P^0 + J z + O(|z|^3)`: the
second derivative of `Phi` at 0 vanishes.
Hence `G ∘ Phi` has 2-jet `grad G(P^0)^T (J z) + (1/2) (J z)^T Hess G(P^0) (J z)` at 0.
Multiplying by `D` with `D(0) = 1`, `grad D(0) = 0`, `G(Phi(0)) = 0`:
`grad(D · G∘Phi)(0) = D(0) grad(G∘Phi)(0) + (G∘Phi)(0) grad D(0) = grad(G∘Phi)(0)`, and
`Hess(D · G∘Phi)(0) = D(0) Hess(G∘Phi)(0) + grad D(0) grad(G∘Phi)(0)^T + grad(G∘Phi)(0) grad D(0)^T + (G∘Phi)(0) Hess D(0) = Hess(G∘Phi)(0)`.
□

**Consequences used later** (all replayed exactly in `verify_chart.py`):

- `A_chart = A_geo J`, where `A_geo` is T-012’s 20 x 15 matrix `constraint_rows`. Since
  `J` is diagonal positive, `{ x : A_chart x >= 0 } = J^{-1} { u : A_geo u >= 0 }`; the
  cone is a line in one system iff in the other, and `A_geo e_{w4} = 0` iff
  `A_chart e_{t4} = 0`.
- `q_chart_j := e_{t4}^T Hess g~_j(0) e_{t4} = 4 · (e_{w4}^T Hess G_j e_{w4}) = 4 q_geo_j`.
  T-012 reports `q_geo = -1/2` on the four pair rows and `0` on the sixteen wall rows;
  so `q_chart = -2` and `0`. (Directly: each pair polynomial restricted to the line
  `z = t_4 e_{t4}` is exactly `-t_4^2`.)
- Positive row scalings: T-012 verifies its certificates against `A~ = S A_geo` with
  `S = diag(1 on wall rows, sqrt 2 on pair rows)`. In the chart,
  `S A_chart = S A_geo J`. If `w >= 0` and `w^T S A_geo = 0` then `w^T (S A_chart) = 0`;
  if `w^T S A_geo = e_k^T` then `w^T (S A_chart) = J_kk e_k^T`, a positive multiple of
  `e_k^T`. Sign information is preserved by every one of these positive diagonal
  factors.

### 2.5 The twenty cleared polynomials

Row order is that of the retained record (`contacts.detail`). Wall rows are
`D_i · (margin)`; pair rows are `D_i D_4 · ((p_{i,k} - c_4) · n_{4,e} - 1/2)`. From
`print_polys.py`:

| j | contact | cleared polynomial `g~_j` | `grad g~_j(0)` (nonzero entries) | `q_chart_j` |
| --- | --- | --- | --- | --- |
| 0 | sq0 c0 left | `dx0 (1+t0^2) + t0^2 + t0` | `dx0: 1, t0: 1` | 0 |
| 1 | sq0 c0 bottom | `dy0 (1+t0^2) + t0^2 - t0` | `dy0: 1, t0: -1` | 0 |
| 2 | sq0 c1 bottom | `dy0 (1+t0^2) + t0^2 + t0` | `dy0: 1, t0: 1` | 0 |
| 3 | sq0 c2 on sq4 e3 | (pair, see below) | `dx0: -r/2, dy0: -r/2, dx4: r/2, dy4: r/2` | `-2` |
| 4 | sq0 c3 left | `dx0 (1+t0^2) + t0^2 - t0` | `dx0: 1, t0: -1` | 0 |
| 5 | sq1 c0 bottom | `dy1 (1+t1^2) + t1^2 - t1` | `dy1: 1, t1: -1` | 0 |
| 6 | sq1 c1 bottom | `dy1 (1+t1^2) + t1^2 + t1` | `dy1: 1, t1: 1` | 0 |
| 7 | sq1 c1 right | `-dx1 (1+t1^2) + t1^2 - t1` | `dx1: -1, t1: -1` | 0 |
| 8 | sq1 c2 right | `-dx1 (1+t1^2) + t1^2 + t1` | `dx1: -1, t1: 1` | 0 |
| 9 | sq1 c3 on sq4 e0 | (pair) | `dx1: r/2, dy1: -r/2, dx4: -r/2, dy4: r/2` | `-2` |
| 10 | sq2 c0 left | `dx2 (1+t2^2) + t2^2 + t2` | `dx2: 1, t2: 1` | 0 |
| 11 | sq2 c1 on sq4 e2 | (pair) | `dx2: -r/2, dy2: r/2, dx4: r/2, dy4: -r/2` | `-2` |
| 12 | sq2 c2 top | `-dy2 (1+t2^2) + t2^2 - t2` | `dy2: -1, t2: -1` | 0 |
| 13 | sq2 c3 left | `dx2 (1+t2^2) + t2^2 - t2` | `dx2: 1, t2: -1` | 0 |
| 14 | sq2 c3 top | `-dy2 (1+t2^2) + t2^2 + t2` | `dy2: -1, t2: 1` | 0 |
| 15 | sq3 c0 on sq4 e1 | (pair) | `dx3: r/2, dy3: r/2, dx4: -r/2, dy4: -r/2` | `-2` |
| 16 | sq3 c1 right | `-dx3 (1+t3^2) + t3^2 - t3` | `dx3: -1, t3: -1` | 0 |
| 17 | sq3 c2 right | `-dx3 (1+t3^2) + t3^2 + t3` | `dx3: -1, t3: 1` | 0 |
| 18 | sq3 c2 top | `-dy3 (1+t3^2) + t3^2 - t3` | `dy3: -1, t3: -1` | 0 |
| 19 | sq3 c3 top | `-dy3 (1+t3^2) + t3^2 + t3` | `dy3: -1, t3: 1` | 0 |

The pair polynomial for row 3 (the others are its images under the container’s
symmetries) is

```
g~_3 = (r/2) [ (dx0 - dx4)(t0^2 t4^2 + 2 t0^2 t4 - t0^2 + t4^2 + 2 t4 - 1)
             + (dy0 - dy4)(t0^2 t4^2 - 2 t0^2 t4 - t0^2 + t4^2 - 2 t4 - 1) ]
       + t0^2 (r - (r+1) t4^2) - 2 r t0 t4 - t4^2 .
```

(The printed form in `print_polys.py` output is the expanded equivalent.)
Two features matter: the coordinate `t4` is absent from every gradient row, and each
pair row carries `-t4^2` as its only pure-`t4` term.
The cross term `-2 r t0 t4` never enters the argument: §5 only ever evaluates the
Hessian on multiples of `e_{t4}`.

* * *

## 3. (b) The complete constraint accounting

### 3.1 Lemma 4 (separating axes for two closed squares)

Let `Q_i, Q_j` be closed unit squares with centres `c_i, c_j` and outward edge normals
`n_{i,e}, n_{j,e}` (`e = 0..3`). Then `int Q_i ∩ int Q_j = ∅` if and only if

```
OR over (owner, e) in {i, j} x {0,1,2,3}:   AND over k in {0,1,2,3}:
        (p_{other,k} - c_owner) · n_{owner,e} - 1/2  >= 0,
```

where `other` is the square that is not `owner`.

*Proof.* Put `K = Q_i - Q_j` (Minkowski difference), a convex polygon.
For convex sets with nonempty interior `int(A + B) = int A + int B` (`int A + int B` is
open and lies in `A + B`; conversely `A ⊂ Cl(int A)` gives `A + B ⊂ Cl(int A + int B)`,
and the interior of the closure of an open convex set is that set), so
`int Q_i ∩ int Q_j != ∅` iff `0 in int K`. Thus interiors are disjoint iff `0` lies on
the boundary of `K` or outside it, iff some edge of `K` has `0` on its closed outer
side, i.e. `h_K(a) <= 0` for that edge’s outward normal `a`, where
`h_K(a) = max_{Q_i} a·x + max_{Q_j} (-a)·x` is the support function of `K`. Edges of a
Minkowski sum of polygons are translates of edges of the summands, so `a` is an outward
normal of `Q_i` or of `-Q_j`; since a square’s outward normals form the set
`{+-n, +-n^perp}`, `a` is an outward edge normal of `Q_i` or of `Q_j`. If `a = n_{i,e}`:
`max_{Q_i} a·x = c_i·a + 1/2` and `max_{Q_j} (-a)·x = -min_k p_{j,k}·a`, so the
condition reads `min_k (p_{j,k} - c_i)·n_{i,e} >= 1/2`, the `(owner, e) = (i, e)`
branch. If `a = n_{j,e}`: the condition reads `max_k p_{i,k}·a <= c_j·a - 1/2`, i.e.
`min_k (p_{i,k} - c_j)·(-a) >= 1/2` with `-a = n_{j,e+2}`, the `(j, e+2)` branch.
Conversely each branch exhibits a separating line.
□

In agenda vocabulary: 4 **axes** per pair (`n_{i,0}`, `n_{i,1}`, `n_{j,0}`, `n_{j,1}` up
to sign), 2 **orientations** per axis (edges `e` and `e+2` of the owner), giving the 8
`(owner, e)` branches, and 4 **support-feature branches** per `(owner, e)` (which corner
of the other square is the support point), giving 32 elementary functions per pair.

### 3.2 The full system

- **Wall–corner:** for each of the 20 corners and each of the 4 walls, one polynomial
  (`p_x`, `p_y`, `s - p_x`, `s - p_y`, cleared by `D_i`): **80** functions, all required
  `>= 0` (convexity of `[0, s]^2` makes corner containment equivalent to square
  containment).
- **Pairs:** `C(5,2) = 10` pairs x 32 elementary polynomials (cleared by
  `D_owner D_other`): **320** functions, combined per pair as `OR_8 AND_4`.

`Feas(s) ∩ U` corresponds under `Phi` to

```
F := { z in R^15 : all 80 wall polynomials >= 0  and, for each pair, OR_8 AND_4 (...) >= 0 }.
```

`F` is a Boolean combination of 400 polynomial inequalities, hence **semialgebraic** (no
Tarski–Seidenberg needed), and `0 in F`.

### 3.3 Exact values at the pose (base margins)

All values are in `Q(sqrt 2)` and were computed by an implementation (`verify_chart.py`,
sympy) independent of `sqpack.field`; the classification is by exact sign.

**Wall–corner (80).** Exactly 16 vanish — the 16 wall rows of the retained record, four
per corner square (two corners on each of its two walls; the container-corner corner
counts twice). The other 64 are strictly positive with multiset

| margin | count | where |
| --- | --- | --- |
| `1` | 16 | corner squares: the corner at coordinate 1 against the wall at 0 (`1 - 0`) |
| `1 + r/2` | 16 | corner squares: the corner at coordinate 1 against the wall at `s` (`s - 1`) |
| `2 + r/2` | 16 | corner squares: the corner at coordinate 0 against the wall at `s` (`s - 0`) |
| `1 + r/4` | 8 | square 4, its four axis-extreme corners against the two side walls each |
| `1 - r/4` | 4 | square 4, each corner against its nearest wall |
| `1 + 3r/4` | 4 | square 4, each corner against its farthest wall |

Minimum inactive wall margin: `1 - r/4 ~ 0.6464`. Counts: **16 active + 64 inactive =
80**, agreeing with the agenda.

**Touching pairs (4):** `(0,4)`, `(1,4)`, `(2,4)`, `(3,4)`. For each, exactly one of the
8 branches is satisfied, it has exactly one zero corner, and each of the other 7
branches has a corner with strictly negative margin:

| pair | separating branch | active corner | other 3 corner margins | witnesses of the 7 violated branches: `(owner,e) -> most negative corner margin` |
| --- | --- | --- | --- | --- |
| (0,4) | owner 4, e3 | sq0 c2 | `r, r/2, r/2` | `(0,0): -1-3r/4; (0,1): -r/4; (0,2): -r/4; (0,3): -1-3r/4; (4,0): -1/2-r/2; (4,1): -1-r; (4,2): -1/2-r/2` |
| (1,4) | owner 4, e0 | sq1 c3 | `r/2, r, r/2` | `(1,0): -1-3r/4; (1,1): -1-3r/4; (1,2): -r/4; (1,3): -r/4; (4,1): -1/2-r/2; (4,2): -1-r; (4,3): -1/2-r/2` |
| (2,4) | owner 4, e2 | sq2 c1 | `r/2, r/2, r` | `(2,0): -r/4; (2,1): -r/4; (2,2): -1-3r/4; (2,3): -1-3r/4; (4,0): -1-r; (4,1): -1/2-r/2; (4,3): -1/2-r/2` |
| (3,4) | owner 4, e1 | sq3 c0 | `r/2, r, r/2` | `(3,0): -r/4; (3,1): -1-3r/4; (3,2): -1-3r/4; (3,3): -r/4; (4,0): -1/2-r/2; (4,2): -1/2-r/2; (4,3): -1-r` |

Least negative witness: `-r/4 ~ -0.3536`. Least positive non-active corner margin in a
separating branch: `r/2 ~ 0.7071`. The active corner sits at the **midpoint** of the
host edge: its along-edge parameter `((p - a) · (b - a)) / |b - a|^2` is exactly `1/2`
for all four contacts (`midpoint_check.py`), so no D-390 endpoint incidence occurs; and
since exactly one branch is satisfied per pair there is no D-391 disjunction.
Both facts are now *computed*, not argued.

**Non-touching pairs (6):** each has a branch with all four corners strictly positive:

| pair | witness branch | four corner margins |
| --- | --- | --- |
| (0,1) | owner 0, e1 | `r/2, 1+r/2, 1+r/2, r/2` |
| (0,2) | owner 0, e2 | `r/2, r/2, 1+r/2, 1+r/2` |
| (0,3) | owner 0, e1 | `r/2, 1+r/2, 1+r/2, r/2` |
| (1,2) | owner 1, e2 | `r/2, r/2, 1+r/2, 1+r/2` |
| (1,3) | owner 1, e2 | `r/2, r/2, 1+r/2, 1+r/2` |
| (2,3) | owner 2, e1 | `r/2, 1+r/2, 1+r/2, r/2` |

Counts: **4 touching + 6 non-touching = 10**, agreeing with the agenda.
Every one of the 400 elementary functions has been evaluated; the agenda’s counts
(16/64, 4/6) are confirmed, and no discrepancy was found.

### 3.4 Proposition 5 (the local system is exactly the twenty active inequalities)

Let `g~_1, ..., g~_20` be the cleared active polynomials of §2.5. Define the open set

```
N := { z in R^15 :  f(z) > 0 for each of the 64 inactive wall polynomials f;
                    f(z) > 0 for each of the 24 corner polynomials of the 6 non-touching witness branches;
                    f(z) > 0 for each of the 12 non-active corner polynomials of the 4 separating branches;
                    f(z) < 0 for each of the 28 witness corner polynomials of the violated branches }.
```

Then `0 in N`, `N` is open, and

```
(i)   F ∩ N  subset  { z in N : g~_j(z) >= 0, j = 1..20 },
(ii)  F ∩ N  =       { z in N : g~_j(z) >= 0, j = 1..20 }.
```

*Proof.* `N` is a finite intersection of preimages of open half-lines under continuous
(polynomial) functions, hence open; it contains `0` by §3.3 (every listed sign is strict
at the pose). (i): let `z in F ∩ N` and take a touching pair `(c, 4)` with separating
branch `b_c` and active corner `k_c`. Since `z in F`, some branch of `(c,4)` is
satisfied at `z`; since `z in N`, each of the other 7 branches has a strictly negative
corner at `z`, so the satisfied branch is `b_c`; in particular its corner `k_c`
inequality — which is `g~_j >= 0` for the corresponding pair row `j` — holds.
The 16 active wall rows are among the 80 wall inequalities that `z in F` satisfies.
(ii): conversely let `z in N` satisfy the 20 inequalities.
The 64 inactive wall inequalities hold strictly on `N`; for a non-touching pair the
witness branch holds strictly on `N`; for a touching pair the three non-active corners
of `b_c` hold strictly on `N` and the active one holds by hypothesis, so `b_c` is
satisfied and the pair’s `OR` is true.
Hence `z in F`. □

Two remarks that a reviewer should hold onto:

- **Only (i) is used by the isolation proof** (§5.5), and (i) uses only the 28 strictly
  negative witnesses. The 100 strictly positive margins are needed for (ii), i.e. for the
  statement that the local feasible set is *exactly* the twenty-row system, which is
  what H-060’s criterion asks the instrument to certify and what a future REJECT route
  (an arc satisfying the twenty inequalities) would rely on.
- **No numerical radius is claimed or needed.** `N` is exactly specified as a set.
  A radius could be certified later by bounding each polynomial’s Lipschitz constant on
  a box and comparing with the base margins tabulated above; that is an optional
  strengthening, outside the claim.

* * *

## 4. (c) Curve selection

### 4.1 The theorem

**Nash curve selection lemma** (Bochnak–Coste–Roy, *Real Algebraic Geometry*, Ergeb.
Math. Grenzgeb. (3) 36, Springer 1998, Proposition 8.1.13). *Let `A ⊂ R^n` be
semialgebraic and `x ∈ Cl(A)`. Then there is a Nash arc `gamma : (-1, 1) -> R^n`
(real-analytic and semialgebraic) with `gamma(0) = x` and `gamma((0, 1)) ⊂ A`.*

Provenance, stated honestly: the printed text of BCR was **not** available in this
environment, and it was not reached by the verification lane that later worked this
obligation either — Springer Link redirects to an identity provider, the De Gruyter
digitisation answers `405`, this project’s Google Books quota is `0`, and neither BCR
nor Milnor is on archive.org or HathiTrust in readable form.
Nothing below is the printed page of Proposition 8.1.13 and none of it is offered as a
substitute for one. What it does establish is that the statement used here is attested
verbatim by one of BCR’s own authors, and that its hypothesis class is attested by four
verbatim applications of the proposition in the literature — all four by Fernando and
coauthors, which is one author group and not four independent ones.

- **The printed table of contents of BCR itself** (Deutsche Nationalbibliothek scan,
  `d-nb.info/953926273/04`), verbatim: “8. Nash Functions 161”, “8.1 Germs of Nash
  Functions and Algebraic Power Series 161”, “8.2 Local Properties of Nash Functions
  167”, and separately “2.5 Closed and Bounded Semi-algebraic Sets.
  Curve-selection Lemma 35”. This is front matter of the book, and it places Proposition
  8.1.13 in §8.1, pp. 161–166 — germs of Nash functions and algebraic power series, which
  is the machinery a *Nash* curve selection lemma is proved with.
  It also shows that the book carries a second, continuous curve-selection lemma at
  §2.5, which is not the one cited here.
- **M. Coste, *Real Algebraic Sets***, lecture notes from the RAAG winter school at
  Aussois, document dated 23 March 2005, Theorem 1.15 (Analytic curve selection),
  verbatim: “For A and x as in theorem 1.14, there exists a Nash curve γ : (−1, 1) → R^n
  such that γ(0) = x and γ((0, 1)) ⊂ A.” Coste is the “C” of Bochnak–Coste–Roy, so this
  is the cited statement in an author’s own words, and it is the statement used here;
  his Theorem 1.14 is the continuous version, in the `x ∈ clos(S)`, `x ∉ S` form.
  Two caveats, stated because they are why this is still not primary text: the notes are
  self-described as “still in a provisional form”, and Theorem 1.15 is introduced with
  “We explain the reason for this fact, without giving a complete proof”.
- J. F. Fernando, *On a Nash curve selection lemma through finitely many points*,
  arXiv:2504.03348 (2025), proof of Lemma 3.1, verbatim: “there exists by
  [BCR, Prop.8.1.13] a Nash arc η := (η_1, ..., η_n) : [−1,1] → R^n such that η(0) = p
  and η((0,1]) ⊂ Int(S)” and “After shrinking the domain of η, we may assume that each
  η_i ∈ R[[t]]_alg is an algebraic analytic series.”
  Bibliography entry: “[BCR] J. Bochnak, M. Coste, M.-F. Roy: Real algebraic geometry.
  Ergeb. Math. 36, Springer-Verlag, Berlin (1998).” (`arxiv-2504.03348.txt`, lines 850,
  875–877, 3121.)
- **Two further verbatim uses of the same proposition**, carrying the same bibliography
  entry: Fernando & Ueno, arXiv:1212.1811, “there exists by the Nash curve selection
  lemma [BCR, 8.1.13] a Nash path γ : (−1,1) → RP^m such that γ((0,1)) ⊂ S_1 and γ(0) =
  p”; and Fernando, arXiv:1503.05706, “By the Nash curve selection lemma
  [BCR, Prop.8.1.13] there exists a Nash arc γ : (−1,1) → M × S^{k−1} such that γ(0) =
  (a,b) and γ((0,1)) ⊂ Γ_ε”.
- **A. Carbone & J. F. Fernando, arXiv:2601.13164**, which applies the proposition to a
  *difference*: “By the Nash curve selection lemma [BCR, Prop.8.1.13] there exist Nash
  arcs γ_1 : [−1,0] → (R_1\R_2) ∪ {p} and γ_2 : [0,1] → (R_2\Y_1) ∪ {p} such that γ_i(0)
  = p, γ_1([−1,0)) ⊂ R_1 and γ_2((0,1]) ⊂ R_2\Y_1.” `R_2 \ Y_1` is a semialgebraic set
  minus an algebraic one — neither closed, nor open, nor basic — so this use is direct
  evidence that Proposition 8.1.13 carries no unstated closedness, boundedness,
  openness, basic-ness or dimension hypothesis.
  §4.2 does not lean on that, since the set here satisfies all of those conditions
  anyway.

One author group leaves the *numbering* worth an independent check, and it has one:
Coste, Ruiz and Shiota, *Nash triviality in families of Nash mappings* (Annales de
l’Institut Fourier), state “PROPOSITION 1.1 ([BCR], 8.10.3)”, which matches “8.10
Families of Nash Functions 202” in the printed table of contents above.
BCR’s chapter 8 is numbered the way these citations assume.

**One citation withdrawn.** The packet also quoted Nguyen Hong Duc, *Curve selection
lemma in arc spaces*, arXiv:2301.00128 (2022), §1, which states the
arbitrary-semialgebraic Nash version and attributes it to Milnor.
The statement it gives is right and agrees with the one above; the attribution is not,
because Milnor’s own hypotheses are narrower — see the alternative route below.
Keeping it would have made this document repeat an over-attribution, so it is withdrawn:
the general statement is cited to BCR, and Milnor is cited only together with the
reduction that puts the set into his class.

**What the sources agree on, and what is not used.** Semialgebraic `A`, `x` in its
closure, a Nash — that is, real-analytic *and* semialgebraic — arc, one branch inside
`A`. Nash is strictly stronger than anything consumed below: `sin` and `exp` are
analytic and not Nash, and Corollary 4.3 and §5 use only real-analyticity.
That much is load-bearing rather than decorative, because analyticity is what supplies a
least `m` with `a_m != 0`: a merely `C^∞` arc could be flat at `0`, and a merely
continuous semialgebraic one would carry a Puiseux expansion in fractional powers and
need a reparametrisation `s = u^N` before the induction of §5 could start.
The domain (`(-1,1)`, `[-1,1]` or `[0, ε)`) is immaterial here: only a convergent power
series at `0` and the inclusion of `(0, ε)` are used.

**Alternative route** (for a reviewer who prefers the older statement).
Milnor, *Singular Points of Complex Hypersurfaces*, Ann.
of Math.
Studies 61, Princeton 1968, §3 “The curve selection lemma”, Lemma 3.1. No longer
quoted from memory: the statement below matches, hypothesis for hypothesis, the
restatement in A. Derdzinski and Ś. R. Gal, *Indefinite Einstein metrics on simple Lie
groups*, arXiv:1209.6084, §4 (“Milnor’s curve-selection lemma”), Theorem 4.1, which
attributes it to “Milnor [14, p. 25]” — p. 25 being the opening page of Milnor’s §3.
Milnor’s own printed page was not reached.
*If `V ⊂ R^m` is a real algebraic set and `U = {g_1 > 0, ..., g_l > 0}` with `g_i`
polynomials, and `U ∩ V` contains points arbitrarily close to the origin, then there is
a real-analytic curve `p : [0, ε) -> R^m` with `p(0) = 0` and `p(t) ∈ U ∩ V` for
`t > 0`.*

The narrowness of that class is confirmed rather than suspected, and it is why the
reduction below is required rather than decorative.
Derdzinski–Gal define, verbatim: “By a *semi-algebraic set* in `S` one means the
intersection of an algebraic set with `⋂_{j=1}^{k} f_j^{−1}((0, ∞))`, where `k ≥ 1` and
`f_1, ..., f_k` are polynomial functions `S → R`” — finitely many **strict**
inequalities. `F \ {0}` is outside that class on two counts before its per-pair
disjunctions are even considered: its inequalities are non-strict, and it has a point
removed.

To apply it, write `F \ {0}` as a finite union of sets of the form
`{ f = 0 for f in Z } ∩ { f > 0 for f in P } ∩ { |z|^2 > 0 }`, obtained by choosing one
branch per pair (`8^10` choices) and, for each of the resulting closed basic sets,
splitting each `f >= 0` into `f = 0` or `f > 0`; `0` is in the closure of a finite union
iff it is in the closure of one member; apply the lemma to that member.
The finiteness is all that matters.
This route needs no Nash-function theory.

Two things the reduction owes, stated because their omission is the kind that survives
review. **Localisation must stay inside the class.** Corollary 4.3 applies the lemma to
`F \ {0}` and only then localises, by continuity, to `N`; a reviewer who prefers to
localise first, applying the lemma to `(F ∩ N) \ {0}`, needs the restriction to `N` to
be a strict polynomial inequality itself, and it is — `N` is defined in §3.4 by 128
strict sign conditions, the 28 conditions `f < 0` being `-f > 0`, so intersecting with
`N` keeps every member of the union in Milnor’s class and keeps the set semialgebraic
for the BCR route. Nothing is lost either way, because isolation is local.
**The finite-union step is in print.** Derdzinski–Gal’s displayed remark (4.1) —
“whenever `Z ⊂ S` and `L ⊂ S` are algebraic, one easily sees that `Z \ L` is a finite
union of semi-algebraic sets in `S`” — is precisely this move, made in a peer-reviewed
paper immediately before they invoke Milnor’s lemma.

### 4.2 Hypotheses, verified for this chart

- `A := F \ {0}` is semialgebraic: `F` is (§3.2), and `{0} = { |z|^2 = 0 }` is;
  differences of semialgebraic sets are semialgebraic.
- `0 ∈ Cl(A)` **if and only if** `P^0` is not isolated in `Feas(s)`: `Phi` is a
  homeomorphism onto the open set `U ∋ P^0` (Lemma 1), so `Feas(s) ∩ U` corresponds to
  `F`, and a point is nonisolated in a set iff it lies in the closure of the set minus
  the point.

Those two bullets are the whole hypothesis of Proposition 8.1.13.

**Applying the lemma to `F \ {0}` rather than to `F` is load-bearing, not tidiness.**
The theorem is stated with `x ∈ Cl(A)`, which permits `x ∈ A`; and when `x ∈ A` the
*constant* arc `gamma ≡ x` already satisfies `gamma(0) = x` and `gamma((0,1)) ⊂ A`, so a
lemma entitled to return it says nothing about isolation and leaves the coefficient
induction of §5 with no `a_m != 0` to run on.
Removing the point is exactly what excludes that: with `0 ∉ A`, every arc satisfying
`gamma((0,1)) ⊂ A` has `gamma(s) != 0` for `s ∈ (0,1)`, which is where Corollary 4.3
gets its nonconstancy.
Any rephrasing that applies the lemma to `F` itself breaks the argument silently.
A reviewer who prefers the guard inside the theorem can cite Coste’s Theorem 1.14/1.15,
stated for `x ∈ clos(A)`, `x ∉ A`.

**Every hypothesis a weaker version of the lemma could impose is also satisfied**, so
the argument does not depend on which formulation a reviewer reaches for:

- **Closed, and locally closed basic.** All 400 conditions of §3.2 are non-strict, and
  finite unions and intersections of closed sets are closed, so `F` is closed; the
  twenty-row system `G := { g~_1 >= 0, ..., g~_20 >= 0 }` is a **closed basic**
  semialgebraic set (inequalities only, no equalities), and Proposition 5(ii) says
  `F ∩ N = G ∩ N`. Hence `F \ {0} = F ∩ (R^15 \ {0})` is closed intersected with open:
  **locally closed**.
- **`0 ∉ A`, and `0 ∈ Cl(A)` is exactly “not isolated”.** The first holds by
  construction, the second is the second bullet above.
- **Bounded, if a reviewer insists on it.** No cited statement asks for it: “Closed and
  Bounded Semi-algebraic Sets” is the *title* of BCR §2.5, not a hypothesis, and Coste’s
  proof of Theorem 1.14 opens by *reducing* to the bounded case (“Replacing `S` with its
  intersection with a ball with center `x` and radius 1, we can assume `S` bounded”). It
  is free here in any case: intersecting `A` with the open unit ball `{ 1 - |z|^2 > 0 }`
  about the pose — Coste’s own reduction — is one more strict polynomial inequality,
  which preserves semialgebraicity, local closedness and membership in Milnor’s class,
  leaves `0 ∈ Cl(A)` undisturbed because closure membership is local, and costs nothing
  because isolation is local.
  It is not done above only because nothing above needs it.

**Corollary 4.3.** If `P^0` is not isolated in `Feas(s)`, there is a real-analytic
`gamma : (-1,1) -> R^15` with `gamma(0) = 0`, `gamma((0,1)) ⊂ F \ {0}`; writing its
convergent Taylor series at 0 as `gamma(s) = sum_{k>=1} a_k s^k` (`a_k ∈ R^15`, radius
`rho > 0`), not all `a_k` vanish (else `gamma ≡ 0` near 0, contradicting `gamma(s) != 0`
for `s ∈ (0,1)`). Let `m >= 1` be least with `a_m != 0`. By continuity there is
`ε ∈ (0, min(rho, 1))` with `gamma((0, ε)) ⊂ N`, hence by Proposition 5(i)

```
g~_j(gamma(s)) >= 0     for all j = 1..20 and all s ∈ (0, ε).                    (4.1)
```

* * *

## 5. (d) The coefficient argument

### 5.1 Proposition 6 (T-012, transferred to the chart)

Let `A := A_chart` (20 x 15, the gradient rows of §2.5), `S` the positive diagonal
scaling (`sqrt 2` on rows 3, 9, 11, 15; `1` elsewhere), `q := q_chart ∈ R^20` (`-2` on
rows 3, 9, 11, 15; `0` elsewhere).
Then:

1. **Cone.** `C := { x ∈ R^15 : A x >= 0 } = R e_{t4}`, and `A e_{t4} = 0`.
2. **Self-stress.** There is `w ∈ R^20`, `w >= 0`, with `w^T A = 0` and `w · q < 0`.

*Proof.* (1) `A e_{t4} = 0` because `t4` appears in no gradient row (§2.5). For each of
the 14 coordinates `k != t4`, T-012’s record carries weights `w^{k,+}, w^{k,-} >= 0`
with `(w^{k,+-})^T S A_geo = +- e_k^T`; by §2.4, `(w^{k,+-})^T (S A) = +- J_kk e_k^T`.
If `A x >= 0` then `S A x >= 0`, so `+- J_kk x_k = (w^{k,+-})^T S A x >= 0`, i.e.
`x_k = 0`. Hence `C ⊂ R e_{t4}`, and `R e_{t4} ⊂ C` by `A e_{t4} = 0`. (2) T-012’s
self-stress `w~ = 1/2` on the six rows `{5, 8, 9, 10, 11, 12}` satisfies
`w~^T S A_geo = 0`, hence `w~^T S A = 0`; put `w := S w~`, i.e. weights
`1/2, 1/2, r/2, 1/2, r/2, 1/2` on those rows.
Then `w >= 0`, `w^T A = w~^T S A = 0`, and `w · q = (r/2)(-2) + (r/2)(-2) = -2r < 0`.
All of this was replayed exactly (`verify_chart.py`: the 28 certificates and the
self-stress against `S A_chart`; `w · q~ = -2 sqrt 2`). By hand, for the reader:
`(1/2)(dy1 - t1) + (1/2)(-dx1 + t1) + (1/2)(dx1 - dy1 - dx4 + dy4) + (1/2)(dx2 + t2) + (1/2)(-dx2 + dy2 + dx4 - dy4) + (1/2)(-dy2 - t2) = 0`.
□

### 5.2 Lemma 7 (sign of the leading coefficient)

Let `f(s) = sum_{k >= K} f_k s^k` converge on `(-rho, rho)` and satisfy `f(s) >= 0` for
`s ∈ (0, ε)`. Then `f_K >= 0`.

*Proof.* If `f_K < 0`, then `f(s) = s^K (f_K + O(s))` is negative for small `s > 0`. □

### 5.3 Lemma 8 (coefficient extraction)

Let `g` be a polynomial on `R^15` with `g(0) = 0`, gradient `a` and Hessian `H` at 0,
and let `gamma(s) = sum_{k >= m} a_k s^k` with `a_m != 0`. Then `g(gamma(s))` is a
convergent power series whose coefficient of `s^k` is

```
[s^k] g(gamma(s)) = a · a_k                                  for m <= k < 2m,
[s^{2m}] g(gamma(s)) = a · a_{2m} + (1/2) a_m^T H a_m .
```

*Proof.* Write `g(z) = a·z + (1/2) z^T H z + (terms of degree >= 3)`. A monomial of
degree `d` in `z` contributes to orders `>= d·m` in `s`. The linear part contributes
`a · a_k` at each order `k`. The quadratic part contributes
`(1/2) sum_{k+l = order, k,l >= m} a_k^T H a_l`, which is empty below order `2m` and
equals `(1/2) a_m^T H a_m` at order `2m` (the only solution of `k + l = 2m`, `k, l >= m`
is `k = l = m`). Cubic and higher parts start at order `3m > 2m`. □

### 5.4 Theorem 9 (no nonconstant analytic feasible arc)

There is no real-analytic `gamma : (-rho, rho) -> R^15`, `gamma(0) = 0`, `gamma` not
identically zero near 0, satisfying (4.1) on some `(0, ε)`.

*Proof.* Suppose there is one; let `m >= 1` be least with `a_m != 0`, and write `a_j`
for row `j` of `A`. We prove by induction on `k`, `m <= k <= 2m - 1`:

> **(I_k)** `a_k ∈ C`, hence (Proposition 6.1) `a_k = lambda_k e_{t4}` and `A a_k = 0`.

*Base `k = m`.* By Lemma 8, for each `j`,
`g~_j(gamma(s)) = (a_j · a_m) s^m + O(s^{m+1})` (all lower coefficients vanish because
`g~_j(0) = 0` and `a_k = 0` for `k < m`). By (4.1) and Lemma 7, `a_j · a_m >= 0` for
every `j`, i.e. `A a_m >= 0`, i.e. `a_m ∈ C`. So `a_m = lambda e_{t4}` with
`lambda := lambda_m != 0`, and `A a_m = 0`.

*Step `m < k <= 2m - 1`.* Assume `(I_{k'})` for `m <= k' < k`. Then for each `j` the
coefficients of `s^{k'}`, `k' < k`, in `g~_j(gamma(s))` are `a_j · a_{k'} = 0` (Lemma 8
and `A a_{k'} = 0`), so `g~_j(gamma(s)) = (a_j · a_k) s^k + O(s^{k+1})`, and Lemma 7
with (4.1) gives `A a_k >= 0`, i.e. `(I_k)`.

*Order `2m`.* By `(I_{k})` for all `m <= k < 2m`, every coefficient of `g~_j(gamma(s))`
of order `< 2m` vanishes, and by Lemma 8 the order-`2m` coefficient is
`a_j · a_{2m} + (1/2) a_m^T H_j a_m = a_j · a_{2m} + (lambda^2 / 2) q_j`, since
`a_m = lambda e_{t4}` and `e_{t4}^T H_j e_{t4} = q_j`. Lemma 7 with (4.1) gives, for
every `j`,

```
a_j · a_{2m} + (lambda^2 / 2) q_j >= 0,      i.e.      A a_{2m} >= -(lambda^2 / 2) q .
```

Apply the self-stress `w` of Proposition 6.2 (`w >= 0`, `w^T A = 0`, `w · q < 0`):

```
0 = w^T A a_{2m} >= -(lambda^2 / 2) (w · q) > 0 ,
```

using `w >= 0` to preserve the inequality, `lambda != 0`, and `w · q = -2 sqrt 2 < 0`.
Contradiction. □

### 5.5 Theorem 10 (fixed-side local rigidity of Goebel’s pose)

`P^0` is an isolated point of `Feas(s)`, `s = 2 + sqrt(2)/2`. Consequently there is no
nonconstant continuous path in `Feas(s)` starting at `P^0`, no sequence of distinct
feasible configurations converging to `P^0`, and (by the lifting remark of §1.3) the
unlabeled packing is rigid in Kingbird’s sense at fixed side.

*Proof.* If `P^0` were not isolated, Corollary 4.3 would supply an analytic `gamma` with
`gamma(0) = 0`, nonconstant near 0, satisfying (4.1); Theorem 9 forbids it.
The consequences are §1.3. □

### 5.6 Remarks on the proof

- **`m = 1` is T-012.** Then `2m = 2` and the induction has no intermediate steps; the
  order-2 inequality is exactly X-007’s `A y >= -q` with `y = 2 a_2` (up to the chart’s
  factor, since `gamma''(0) = 2 a_2`).
- **Why no reparametrization is needed, and why X-007’s “wrong version” fails.** The
  induction works on the arc’s own coefficients; substituting `sigma = s^m` would
  destroy analyticity at 0 for `m >= 2`. The argument never differentiates `gamma` more
  than the power series allows.
- **Where the geometry enters.** Exactly twice: `C ⊂ ker A` (the flex line is in the
  kernel, so lower-order coefficients vanish *exactly* rather than merely being
  nonnegative — this is what lets the induction proceed to order `2m` with nothing
  accumulating), and `q < 0` on rows that a nonnegative self-stress combines to zero.
  The cross terms `t_i t_4` of the pair polynomials are invisible because the Hessian is
  only ever evaluated on `e_{t4}`.
- **Fixed side is load-bearing.** With `s` a 16th variable the cone opens and
  `A y >= -q` becomes feasible (X-007’s measurement); nothing here survives.
  This is control C5.
- **Nothing is claimed about a numerical isolation radius**, about other optimal `n = 5`
  packings, about global uniqueness, or about the container growing.

### 5.7 Second, corroborating proof: classical second-order sufficiency (not the acceptance route)

**Status.** Recorded at the coordinator’s direction (Decision 2) as an independent
second route to Theorem 10 with weaker hypotheses.
It is **not** the acceptance route: H-060’s registered `direction` names the intrinsic
chart, the derivative binding and the curve-selection-and-coefficient argument, and
acceptance runs through §§2–5.5 only.
Nothing in this subsection discharges or softens any obligation of the primary route
(§8).

**Theorem 11.** Let `g_1, ..., g_20` be `C^2` on a neighbourhood of `0` in `R^15` with
`g_j(0) = 0`, gradients `a_j` (the rows of `A`) and Hessians `H_j` at `0`. Assume

- (i) `{ d : A d >= 0 } = R e` for a unit vector `e` with `A e = 0`;
- (ii) there is `w ∈ R^20`, `w >= 0`, with `w^T A = 0` and `w · q < 0`, where
  `q_j := e^T H_j e`.

Then `0` is an isolated point of `G := { z : g_j(z) >= 0, j = 1..20 }`.

*Proof (normalized sequence).* Suppose `z_k ∈ G \ {0}` with `z_k -> 0`. Put
`rho_k := |z_k| -> 0` and `d_k := z_k / rho_k`; pass to a subsequence with `d_k -> d`,
`|d| = 1`. By Taylor’s theorem with Peano remainder (`C^2` suffices),
`g_j(z_k) = rho_k a_j · d_k + (1/2) rho_k^2 d_k^T H_j d_k + o(rho_k^2)`. *First order:*
divide `g_j(z_k) >= 0` by `rho_k` and let `k -> ∞`: `a_j · d >= 0` for every `j`, so
`d ∈ R e` by (i), i.e. `d = +-e`. *Second order:* since `w >= 0`,
`sum_j w_j g_j(z_k) >= 0`; since `w^T A = 0` the first-order terms cancel exactly,
leaving `(1/2) rho_k^2 d_k^T H_w d_k + o(rho_k^2) >= 0` with `H_w := sum_j w_j H_j`.
Divide by `rho_k^2` and let `k -> ∞`: `d^T H_w d >= 0`. But
`d^T H_w d = e^T H_w e = sum_j w_j q_j = w · q < 0` by (ii).
Contradiction. □

**Hypotheses reduced to this system.** (a) The `g_j` are the twenty cleared polynomials
of §2.5, hence `C^∞`. (b) Proposition 5(i) gives `F ∩ N ⊂ G`, so isolation of `0` in `G`
implies isolation in `F`, and through Lemma 1 isolation of `P^0` in `Feas(s)`; this is
the same local reduction (the 28 strictly negative witnesses of §3.3) that the primary
route uses, and it is the only geometric input shared by the two routes.
(c) Hypothesis (i) is Proposition 6.1 with `e = e_{t4}`. (d) Hypothesis (ii) is
Proposition 6.2, with `w · q = -2 sqrt 2`. The route uses no semialgebraicity, no
property of the chart beyond its being a `C^2` local coordinate system, no curve
selection and no Puiseux induction; it works verbatim in the raw `(c, theta)`
coordinates with T-012’s `A_geo`, `q_geo` and the unscaled weights `S w~` (there
`w · q_geo = -sqrt(2)/2`).

**Relation to the classical SOSC.** Theorem 11 is the second-order sufficient optimality
condition (McCormick 1967, *SIAM J. Appl.
Math.* 15; Fiacco–McCormick 1968, *Nonlinear Programming*; Nocedal–Wright, *Numerical
Optimization*, 2nd ed.
2006, Theorem 12.6 — citations from memory, numbering to be checked) applied to
`min f(z) = -|z|^2` subject to `g_j(z) >= 0` at `x* = 0`: a strict local minimizer of
`-|z|^2` over `G` is exactly an isolated point of `G`. KKT holds at `0` with multiplier
`lambda = mu w` for any `mu > 0` (`grad f(0) = 0` and `w^T A = 0`); the critical cone
`C(x*, lambda)` is contained in `{ d : A d >= 0 } = R e`; and
`d^T Hess_zz L(x*, lambda) d = -2|d|^2 - mu d^T H_w d = |d|^2 (-2 - mu w · q)`, which is
positive for all `d ∈ C \ {0}` as soon as `mu > 2 / (-w · q)`. The multiplier scaling is
not cosmetic: with `mu = 1` the inequality reads `-2 + 2 sqrt 2 > 0` in the chart
normalization but `-2 + sqrt(2)/2 < 0` in the `(c, theta)` normalization
(`q_geo = -1/2`, `w · q_geo = -sqrt(2)/2`); the freedom to scale a self-stress is what
makes the objective’s Hessian irrelevant.
The normalized-sequence proof above is this theorem’s standard proof, specialized, and
is included so that the packet does not depend on the numbering.

**What this does and does not add.** It corroborates Theorem 10 from strictly weaker
hypotheses (`C^2` rather than semialgebraic; no curve selection), so an error in §4
would not by itself break isolation.
It does not change the acceptance criterion, does not close or soften the primary
route’s open obligation, and claims no novelty: the closing principle is classical (§8).

* * *

## 6. (e) Negative and positive controls (to be run in the instrument phase)

The instrument (W7 extension of `devtools.assess_n5_rigidity`) will (1) declare the
chart and check `J`, the denominators and their 1-jets; (2) recompute the 400 base
margins in `Q(sqrt 2)` and classify by exact sign, refusing on any unexpected sign; (3)
compute gradient and Hessian rows of the cleared polynomials and bind them to `A_geo J`,
`4 q_geo`; (4) replay T-012’s certificates on `S A_chart`; (5) emit a neighbourhood
receipt. A control “rejects” when the instrument refuses to emit a passing receipt.

| id | control | mutation | check that must refuse | expected refusal |
| --- | --- | --- | --- | --- |
| C1 | changed feature | replace “sq0 c2 on sq4 e3” by “sq0 c1 on sq4 e3” in the declared active list | step 2: declared active row must vanish; true zero must be declared | declared row has value `r/2 != 0`; the actual zero (c2) is undeclared |
| C2 | zero margin | (a) receipt mutation: one strict margin overwritten by `0`; (b) declare row 3 inactive | step 2: strict-sign check | (a) sign 0 fails `> 0`; (b) an inactive-classified function vanishes |
| C3 | omitted constraint | drop “sq1 c0 on the bottom wall” (row 5, carried by the self-stress) from the declared list; variant: drop it from the certificate step only | step 2 (undeclared zero) / step 4 (`w^T A != 0`) | refuse; and the self-stress no longer verifies |
| C4 | invented contact | add “sq4 c1 on the right wall” (margin `1 - r/4 > 0`) as active; variant: a D-390-style endpoint incidence injected as a pair row | step 2 | declared row nonzero; the endpoint incidence fails the separating test |
| C5 | side release | add `s` as a 16th coordinate (`ds`) to every wall row and the chart | steps 3–4: cone certificates | the 14 certificates no longer pin (X-007: the cone opens to 16 dimensions and `A y >= -q` becomes feasible); no receipt |
| C6 | wrong chart | (a) declare `J = I` with the half-angle polynomials; (b) declare `theta = theta^0 + t` but keep the cleared polynomials; (c) declare a denominator `1 - t^2` | step 1/3: `A_chart = A_geo J` binding; denominator positivity | (a),(b) the `t_i` columns differ by the factor 2; (c) `1 - t^2` has a zero |
| C7 | certificate drift | perturb one self-stress weight by `1/1000`; flip the sign of one Farkas weight; set `q_3 = +2` | step 4 | `w^T A != 0`; negative weight; `w · q >= 0` |
| C8 | exp-034 family (true negative) | run the instrument on the exp-033/034 pose at side `1 + 5r/4`, square 0 at `u = delta/2 = 3r/4 - 1`, `t = 0` (and `t = 1/200`) | steps 3–4 | the cone is not a line; certificates for `vx0, vy0, w0` (at least) do not exist; no receipt. Exp-034’s exact two-parameter family is a **verified nonconstant feasible arc** through that pose, so a “locally rigid” receipt there would be a false positive |

Pre-run evidence for C8 (`control_exp034.py`, read-only, T-012 machinery): at
`(u, t) = (delta/2, 0)` the pose is valid with 15 active contacts and no disjunctive
pair; the slide `+-(dx0, dy0) = +-(1,1)` and the rotation `+-w0` all lie in the
first-order cone; `w0` appears in no row; only `vx2, vy2, w2, vx3, vy3` are pinned.
At the endpoint `u = 0` the slide is one-sided and rotation is refused at first order
(rate `-1/2`), which is consistent with exp-034’s boundary `u >= e(t)`. So C8’s expected
outcome is fixed: refusal by an open cone, never a receipt.

**C8 does not touch H-060’s target, and is not a rejection witness.** The exp-034 family
lives at side `S = 1 + 5√2/4 ≈ 2.7678`, not at Goebel’s `s = 2 + √2/2 ≈ 2.7071`
(`S − s = 3√2/4 − 1 ≈ 0.0607 > 0` exactly), with squares 3 and 4 diagonal rather than
square 4 alone, and its square 1 centred at `(1/2 + 5√2/4, 1/2)` versus Goebel’s
`(3/2 + √2/2, 1/2)`. `c8_side_check.py` (exact, `sqpack.verify`) shows every point of
the family at `u ∈ {0, δ/2, δ}` is valid at side `S` and **invalid at side `s`**: square
1’s right edge sits at `x = S`, overshooting Goebel’s wall by exactly `3√2/4 − 1`. So
the family is a subset of `Feas(S)`, disjoint from `Feas(s)`, and at positive distance
from `P^0`; it is consistent with Theorem 10 because the two statements concern
different sets. C8 is a specificity control: a pose where a nonconstant feasible arc is
known to exist (at its own fixed side) at which the instrument must refuse a
local-rigidity receipt.

All controls are to be run under normal and optimized Python per the agenda; none was
run here except the C8 pre-run above.

* * *

## 7. (f) Novelty gaps named by H-060

### 7.1 Structural rigidity (Connelly, Whiteley) — partly closed, remainder stated

What the corpus lacked (evidence.yaml, `E-n005-second-order-rigidity.gaps`): any of the
structural-rigidity literature.
Retrieved here (text extracted, `whiteley-chapter.txt`): W. Whiteley, “Rigidity and
scene analysis”, *Handbook of Discrete and Computational Geometry*, 2nd ed., CRC 2004,
Chapter 60 (pp. 1327–1354). Verbatim:

- “Rigid tensegrity framework `G±(p)`: For every analytic path `p(t)` in `R^{vd}`,
  `0 ≤ t < 1`, if `p(0) = p` and `G(p)` dominates `G(p(t))` for all `t`, then `p` is
  congruent to `p(t)` for all `t`.” (p. 1342) — rigidity is *defined* through analytic
  paths, which is legitimate precisely because of curve selection.
- “(If this first derivative is trivial, then the earliest nontrivial derivative is a
  first-order motion.)” (p. 1341, bar frameworks) — the base case of §5.4 in the
  equality setting.
- “THEOREM 60.1.39 Rigidity Stress Test.
  A tensegrity framework `G±(p)` is rigid if, for each nontrivial first-order motion
  `p'` of `G±(p)`, there is a proper self-stress `ω_{p'}` making
  `∑ ω_{p'}_{ij} (p'_i − p'_j)·(p'_i − p'_j) > 0`”, drawn from [CW96] = R. Connelly, W.
  Whiteley, *Second-order rigidity and prestress stability for tensegrity frameworks*,
  SIAM J. Discrete Math.
  9 (1996) 453–492.

Relation to H-060: Theorem 60.1.39 has the same *shape* as §5 — one self-stress per
first-order flex, pairing negatively with the flex’s second-order term — but its
hypotheses are squared-distance constraints between points; ours are corner-on-line and
corner-on-wall inequalities in `(c, theta)`. The theorem is therefore **not invoked**;
§5 proves the transplant directly from the chart polynomials, Farkas and curve selection
(exactly what X-007 and H-060 demanded).
The primary [CW96] text (Cornell PDF) is a scanned image and could not be text-extracted
here; the 1980 Connelly paper (Adv.
Math. 37) was not retrieved.
**Governing finding (coordinator’s independent prior-art survey; not verified by this
lane against the primary texts):** the Puiseux/curve-selection proof shape of §5 matches
[CW96] Theorem 4.3.1 and is **not new**; the closing inference itself (first-order cone
plus a self-stress with `w · q < 0` implies isolation) is the classical second-order
sufficient optimality condition (§5.7) and is **not new**. No stated theorem in that
literature applies to this system: [CW96]'s members are point-pair distance constraints;
the disk-jamming second-order results require a non-negative quadratic term, which is
exactly false here (`q_geo_j = -1/2` on every pair row); and Donev et al.
2007 explicitly defer particles with sharp corners and flat edges.
What §5 supplies is the adaptation to corner-on-line and corner-on-wall inequalities,
proved directly.

### 7.2 Goebel 1979 — closed

`gobel-1979-geometrical-packing-and-covering-problems.pdf` (archive) has a text layer;
extracted here (`gobel-1979.txt`, 21 pages).
§1 “Packing a square with unit squares”: “The exact value of `z*(n)` is known only for
`n = 2, 3, 5` and the squares of integers”; Proposition 1: `S(2 + ½√2 − ε)` cannot be
packed with 5 unit squares, proved by four unavoidable points at distance `1 − ε/3` from
the sides. The words “rigid” and “unique” do not occur anywhere in the paper (0 hits
each). **Goebel proves the side and makes no rigidity or uniqueness claim**; H-060’s
result does not contradict or duplicate anything in the source.

### 7.3 Kingbird — definition closed, methodology open

`https://kingbird.myphotos.cc/packing/squares_in_squares__rigid.html`, retrieved
2026-09-03 (not archived under `packing/resources/`; recommend archiving).
Verbatim: “A packing is rigid when it cannot be continuously transformed into any other
valid packing without changing the size of its enclosing square.”
It lists as rigid `n = 5, 11, 18, 28, 40, 52, 149, 296, 493, 740, 1037, 1384, 1781`,
defines “semi-rigid” by example (`n = 28`: a carousel-like sliding group), and **states
no method** of determination.
**This list is uncorroborated and in tension with the archived page**, which is stated
rather than resolved here: the rigid page is not under `packing/resources/`, and the
archived main page
([`kingbird-squares-in-squares.md`](../../resources/web/kingbird-squares-in-squares.md))
carries exactly four “Rigid.”
annotations at `n <= 100` — `n = 5, 11, 28, 40`, lines 44, 80, 163, 224 — which is what
the coordinator’s prior-art survey reports, and which agrees with that page’s schema
comment “all but four packings at n <= 100”. The thirteen-entry list adds `n = 18` and
`n = 52` below 100. The two are reconcilable if rigid-but-inoptimal entries are simply
not annotated on the main list, which the rigid page’s own preamble allows (“in cases
where they are inoptimal, they are shown alongside the best known”), but no reader can
check that from anything in this repository until the rigid page is archived.
Only the `n = 5` entry is used below, and it is corroborated on the archived page.
So the catalogue’s “Rigid.”
for `n = 5` is an assertion under a definition that coincides with H-060’s fixed-side
notion (§1.3), without argument.
H-060 supplies the proof; it does not supply a *new* claim.

### 7.4 Novelty statement (bound to the coordinator’s scoping)

- **Goebel 1979:** proved only the bound; “rigid” and “unique” occur zero times.
  CLOSED-NOVEL with respect to the source.
- **Friedman DS7:** does not annotate `n = 5` for rigidity (evidence.yaml).
- **Kingbird:** asserts exactly this property for `n = 5` ("cannot be continuously
  transformed into any other valid packing without changing the size of its enclosing
  square") with no method or argument anywhere on the site.
  The **statement** is not novel; a **proof** is.
- **Structural rigidity:** the closing principle is classical (SOSC) and is not claimed
  as new; the Puiseux/curve-selection proof shape matches [CW96] Theorem 4.3.1 and is
  not presented as new.
  The coordinator’s survey reports that no theorem stated in the structural-rigidity or
  jamming literature covers polygon contact systems (§7.1); that is an unverified survey
  assertion, carried outside the claim below rather than inside it.

**Admissible claim:** the first exact proof that Goebel’s `n = 5` optimum is locally
rigid at fixed side — a property asserted without proof by Kingbird and not stated by
Goebel or Friedman. **Novelty score S3, not S4.** Carried *outside* the claim: the
survey’s finding that no theorem stated in the structural-rigidity or jamming literature
covers polygon contact systems.
It is unverified against the primary texts by any lane, and it is narrower than “no
stated rigidity theorem covers this” — the same survey records that the classical
second-order sufficiency theorems have no failing hypothesis once the system is reduced
to the local twenty inequalities.
Nothing in the method (chart, SAT accounting, coefficient induction, SOSC) is claimed as
new.

* * *

## 8. Claim boundary

### 8.1 The acceptance route is the registered one, and only it

H-060’s registered `direction` accepts only if “a checked intrinsic semialgebraic chart
accounts for the entire local feasible set, its polynomial derivatives bind exactly to
the first- and second-order certificates, and a reviewed curve-selection and coefficient
argument excludes every nonconstant feasible arc”.
That route is §§2–5.5. The second proof of §5.7 is corroboration with weaker hypotheses;
it is not a substitute, does not amend the criterion, and does not discharge any
obligation listed below.

### 8.2 Proved in this document

Paper proofs, with every exact quantity replayed by an independent sympy implementation
(`verify_chart.py`, `midpoint_check.py`, `c8_side_check.py`):

- Lemmas 1–3: the half-angle chart is a homeomorphism of `R^15` onto an open
  neighbourhood of the pose; denominators `1 + t_i^2 >= 1` on all of `R^15`; the cleared
  polynomials’ 2-jets are `J^T grad G`, `J^T Hess G J` with `J = diag(1,1,2)^{(+)5}`.
- Lemma 4: SAT characterization of disjoint interiors for two closed squares (8 branches
  x 4 corners).
- §3.3: all 400 elementary margins at the pose, exact; counts 16/64 and 4/6 confirmed;
  no D-390 incidence, no D-391 disjunction, computed.
- Proposition 5: the local feasible set is exactly the 20 active inequalities on the
  explicitly defined open set `N`; direction (i) uses only the 28 negative witnesses.
- Proposition 6: T-012’s cone and self-stress transfer to the chart under `J` and `S`;
  all 28 Farkas certificates and the self-stress replay exactly on `S A_chart`;
  `w · q_chart = -2 sqrt 2`.
- Lemmas 7–8, Theorem 9: the order-`2m` coefficient induction, with every sign explicit.
- Theorem 10: isolation, given Corollary 4.3 (primary route).
- Theorem 11: isolation by the normalized-sequence (SOSC) argument from `C^2` gaps,
  Proposition 5(i) and Proposition 6 alone (second, corroborating route).
- exp-034’s family is at side `1 + 5 sqrt(2)/4`, infeasible at Goebel’s side, disjoint
  from `Feas(s)`, and at positive distance from `P^0`; it is not a rejection witness.

### 8.3 Cited, not verified against a primary text

- The Nash curve selection lemma, BCR Prop.
  8.1.13. The printed page was not reached, here or by the verification lane that later
  worked this obligation; what stands behind it is the book’s own table of contents, the
  statement in the words of Coste — an author of BCR — and four verbatim uses of
  `[BCR, Prop. 8.1.13]` in the literature, one of them on a *difference* of
  semialgebraic sets (§4.1). Alternative: Milnor 1968 Lemma 3.1 with the finite-union
  reduction of §4.1, no longer quoted from memory but corroborated word for word against
  Derdzinski–Gal §4, which cites Milnor p. 25; Milnor’s printed page was not reached
  either. Its hypotheses are verified for `F \ {0}` in §4.2.
- The SOSC numbering (Nocedal–Wright Theorem 12.6; McCormick 1967; Fiacco–McCormick
  1968). The packet does not depend on it: Theorem 11 is proved in full.
- The prior-art scoping of §7.1 (the [CW96] Theorem 4.3.1 shape match, the disk-jamming
  sign requirement, Donev et al.
  2007\) is the coordinator’s survey finding, adopted as governing; this lane did not
  read those primary texts.

### 8.4 Verified only outside the repository instrument

The 400 margins, the 2-jet binding and the certificate replay were computed by
scratchpad sympy scripts, not by the repository instrument.
The W7 instrument, its receipt, and the eight controls of §6 are not written by this
lane. A separate lane wrote them after this packet was frozen, at `6580a9fd`, as
`src/sqpack/local_rigidity/` — a new package binding to `devtools.assess_n5_rigidity`
rather than an extension of it, which is a deviation from `W7`’s registered text.
It self-reports ready with `isolation_decided` false.
Its independent readiness review returned **BOUNDED-CAVEAT** at `2f112f4c` (payload
digest `1ab27086…`), because two of the eight controls could not fail; after the repair
at `609e7392` (digest `ba99cccc…`) the re-review verified the repair by removal and
returned BOUNDED-CAVEAT again, a pass conditional on one unclosed provenance item; and
on the third round it returned **PASS**, at payload digest `743fd18a…` over source
digest `9382bae1…`, with the leaf diff against the author’s certificate showing exactly
one differing leaf. That is what moved `H-060` to `instrument_ready: true`. `H-060` was
still **unresolved** at the end of this phase, which is what the agenda required of it;
what resolved it was `BC-153`’s independent review of this document together with that
instrument, recorded in `exp-058`.

### 8.5 What is claimed as new, and what is not (governing novelty scoping)

- **Claimed:** the first exact proof that Goebel’s `n = 5` optimum is locally rigid at
  fixed side — a property asserted without proof by Kingbird and not stated by Goebel or
  Friedman. Novelty score **S3, not S4**.
- **Carried outside the claim, unverified:** the coordinator’s survey finding that no
  theorem stated in the structural-rigidity or jamming literature covers polygon contact
  systems. No lane checked it against the primary texts, and it is narrower than “no
  stated rigidity theorem covers this”: the same survey records that the classical
  second-order sufficiency theorems have no failing hypothesis once the system is
  reduced.
- **Not claimed as new:** the statement itself (Kingbird asserts it); the closing
  principle (classical second-order sufficiency, McCormick 1967 / Fiacco–McCormick
  1968); the Puiseux/curve-selection proof shape (it matches [CW96] Theorem 4.3.1); the
  half-angle rationalization; the separating-axis accounting; Farkas certification.
- **Why no stated theorem covers it:** [CW96] is for point-pair distance members; the
  disk-jamming second-order results need a non-negative quadratic term, and here
  `q_geo_j = -1/2` on every pair row; Donev et al.
  2007 explicitly defer particles with sharp corners and flat edges.

### 8.6 Not established, and not claimed

A numerical isolation radius; rigidity when the side is free (false, X-007); global
uniqueness of the `n = 5` optimum; rigidity of any other `n = 5` optimal family
(exp-034’s sheet at a larger side is a different object); applicability of the
Connelly–Whiteley theorem as stated; any novelty beyond §8.5.

### 8.7 Rejection routes that remain open in principle

Only a verified nonconstant feasible arc through `P^0` in `Feas(s)` or an exact sequence
of distinct feasible poses in `Feas(s)` converging to `P^0`. A lone feasible point at
positive distance would only refute a proposed neighbourhood, and `N` here is defined by
sign persistence rather than by a radius, so no such point is even a candidate
refutation of §3.4. Feasible families at other container sides (exp-034) are not
candidates at all.

### The single largest remaining proof obligation

**The curve-selection citation, on the acceptance route.** Every other step of the
primary route is either proved above or exactly replayed.
The one step this lane could not check against a primary source is the statement of BCR
Proposition 8.1.13 — or Milnor 1968 Lemma 3.1 *with the finite-union reduction of §4.1*,
which is a different route and not an equivalent statement, since Milnor’s
“semi-algebraic” means a real algebraic set intersected with finitely many **strict**
polynomial inequalities: that for an arbitrary semialgebraic `A ⊂ R^n` (not assumed
open, closed, or of any dimension) and `x ∈ Cl(A)`, there exists a *real-analytic* arc
`gamma` with `gamma(0) = x` and `gamma((0, ε)) ⊂ A`. The BC-153 reviewer should confirm
this against the printed text; the second proof of §5.7 does not remove this obligation,
because acceptance is preregistered on the curve-selection route.
If the primary statement is as quoted, the registered proof is complete and H-060’s
mathematical criterion is met; what then stands between “unresolved” and “accepted” is
engineering (the instrument, its receipt, and the eight rejecting controls), not
mathematics.

**Where that obligation stands after the verification pass (2026-09-03).** A separate
lane worked it and returned **YES**: the statement as used follows from the theorem
cited, §4 is sound as written, and no mathematical defect was found.
Its evidence is folded into §4.1 and §4.2 above, and so is its limit — the printed page
of BCR Proposition 8.1.13 was not reached, so the strongest thing on record is the
statement in the words of one of BCR’s three authors, four verbatim uses of the
proposition by one author group, and the Milnor route corroborated word for word against
a peer-reviewed restatement that cites Milnor’s page.
A reviewer who requires the printed page still has that to do.

**Where it stands after `BC-153` (2026-09-03).** The independent review returned
**PASS** and judged this obligation non-blocking without closing it: the printed page is
still unread, and in its place the reviewer derived the same statement first-hand from
primary-text Basu–Pollack–Roy Theorem 3.22 plus the one-variable Puiseux fact, through
the `t = u^p` change of variable Coste states in his own notes, with the Milnor route
and the finite-union reduction of §4.1 as a third derivation.
The engineering half is closed as well: the instrument’s readiness review passed and the
`BC-153` reviewer replayed the instrument itself from clean roots.
So `H-060` is **confirmed** and the property is registered as `T-014`; the unread page
remains a named, non-blocking citation-provenance gap and nothing in this document’s
mathematics changed with it.

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
