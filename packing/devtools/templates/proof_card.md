# Proof Card: s(11) ≥ {{L_FRAC}}

**Eleven unit squares, free to rotate, do not fit in a square of side {{L_DEC}}.** Write
`s(n)` for the side of the smallest square holding `n` unit squares with pairwise
disjoint interiors; then `s(11) ≥ {{L_FRAC}} = {{L_DEC}}`.

## The Argument

The certificate is {{N_ATOMS}} nonnegative weighted points in the container
`[0, {{L_FRAC}}]²`, invariant under its eight symmetries and carrying total weight
`{{TOTAL_FRAC}} = {{TOTAL_DEC}}`, which is below 11. It fixes a shrunken side
`B = {{B_FRAC}}` and a net of {{N_DIRECTIONS}} directions, at half-angle tangents
`t_k = ({{LIMIT_FRAC}})·k/{{N_DIRECTIONS_MAX}}` for `k = 0..{{N_DIRECTIONS_MAX}}`; the
net reaches π/4 and its largest half-gap tangent is `D = {{D_FRAC}}`, so
`B(1 + D) = {{CONTAINMENT_FRAC}} ≈ {{CONTAINMENT_APPROX}} < 1` and every unit square, at
any angle, contains a closed `B`-square at one of the net angles — angles past π/4 fold
back onto the net by the symmetry the atoms carry.
Every closed `B`-square at a net angle that lies inside the container covers weight at
least `{{LEAST_FRAC}} = {{LEAST_DEC}}`, checked exactly over all {{CELLS}} event cells
its centre can reach, at all {{N_DIRECTIONS}} directions.
Eleven unit squares with disjoint interiors would therefore contain eleven pairwise
disjoint such `B`-squares, carrying at least 11 between them.
The atoms carry `{{TOTAL_DEC}}`, so no such packing exists, and `s(11) ≥ {{L_FRAC}}`.

## The Card

```text
s(11) >= {{L_FRAC}} = {{L_DEC}}   eleven unit squares do not fit in a square of side {{L_DEC}}

  atoms          {{N_ATOMS}} nonnegative weighted points in [0, {{L_FRAC}}]^2, D4-invariant
  total weight   {{TOTAL_FRAC}} = {{TOTAL_DEC}}   (< 11: Condition 2)
  container side L = {{L_FRAC}} = {{L_DEC}}
  shrink         B = {{B_FRAC}} = {{B_DEC}}
  net            {{N_DIRECTIONS}} directions, half-angle tangents t_k = ({{LIMIT_FRAC}}) k / {{N_DIRECTIONS_MAX}},
                 k = 0..{{N_DIRECTIONS_MAX}}; reaches pi/4, as t_K^2 + 2 t_K - 1 = {{ARC_SLACK_FRAC}}
                 >= 0 (Condition 3)
  half-gap       D = {{D_FRAC}} ~ {{D_APPROX}}, the largest of the net
  containment    B(1 + D) = {{CONTAINMENT_FRAC}} ~ {{CONTAINMENT_APPROX}} < 1
                 (Condition 4: a unit square at ANY angle holds a B-square at a net
                 angle; Condition 1, the D4 symmetry, folds angles past pi/4 back)
  least cover    {{LEAST_FRAC}} = {{LEAST_DEC}} >= 1, the least weight any B-square at a net
                 angle inside the container covers, over {{CELLS}} reachable event
                 cells at {{N_DIRECTIONS}} directions -- exact, not sampled (Condition 5)

  so             11 disjoint unit squares would hold 11 disjoint B-squares of weight
                 >= 1 each, i.e. weight >= 11, and the atoms carry only {{TOTAL_DEC}}.

  bytes          {{CERT_PATH}}
                 sha256 {{DIGEST_PREFIX}}...  (`sha256sum {{CERT_NAME}}` for all 64)
  check          python3 minimal_verify.py {{CERT_NAME}}   ->  VERIFIED, ~1 min
                 any CPython 3.12+, standard library only, nothing else installed
```

The bytes on `main`: [{{CERT_NAME}}]({{CERT_URL}}).

## Verify It in One Command

```bash
cd packing/cases/n11_fractional_certificate
python3 minimal_verify.py {{CERT_NAME}}
```

It prints the SHA-256 it checked, one `PASS` line per condition with the numbers it
decided on, and `VERIFIED s(11) >= {{L_FRAC}}`; the exit status is 0 only after that
line. Any other outcome prints `REFUSED` with its reason and exits 1. Measured
2026-09-05, single-threaded with an empty environment: 47.5 s under CPython 3.14 on one
four-core machine, and 67.0 s under CPython 3.14.7 and 64.8 s under CPython 3.12.3 on a
slower one, where the file’s previous bytes took 66.7 s.
[`minimal_verify.py`](minimal_verify.py) imports nothing from this repository and holds
the only copy of the digest; `sha256sum {{CERT_NAME}}` is the other way to get it.

## What This Establishes, and What It Does Not

- **It proves the bound from those bytes.** The theorem is stated and proved in
  [`certificate.py`](../../src/sqpack/fractional/certificate.py) and, with the verifier
  and the certificate embedded, in [`{{CLAIM_NAME}}`]({{CLAIM_NAME}}); the verifier
  decides its five conditions on this file, in exact rational arithmetic, with no
  tolerance and no sampled angle anywhere.
- **The record, not this card, carries the result’s standing.**
  [`results.yaml`](../../frontier/results.yaml) holds `T-018` at confirmation rung
  `{{CONFIRMATION}}` on the scale [`epistemics.md`](../../../epistemics.md) defines,
  with [the review it rests on]({{REVIEW_ARTIFACT}}) mapped beside it, and its novelty
  as `{{NOVELTY}}`, a statement about what a search of the literature found, not a claim
  of priority.
- **It says nothing about an upper bound.** The case stays open: eleven unit squares do
  pack into some larger square, and nothing here bears on how much larger.
- **What a reader is still trusting**: that the theorem is right, that this verifier
  implements it, and that CPython’s integers and `fractions` are.
  Reading `minimal_verify.py` against the theorem is the check that closes the first
  two; [`thirdparty/README.md`](thirdparty/README.md) writes the theorem out with its
  proof for the rung below.

<!-- This document follows common-doc-guidelines.md.
See github.com/jlevy/practical-prose and review guidelines before editing.
-->
