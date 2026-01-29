# C752: No Section-to-Section Routing

**Status:** VALIDATED | **Tier:** 2 | **Phase:** A_B_FOLIO_SPECIFICITY | **Scope:** A<>B

## Finding

A folio section identity does NOT predict which B folio section it best serves. After removing pool-size confound (C751), residual best-match assignment shows 27/82 (33%) same-section matches — statistically indistinguishable from the null expectation of 26.7.

### Permutation Test (10,000 iterations)

| Metric | Value |
|--------|-------|
| Observed same-section | 27 |
| Null mean | 26.7 |
| Null std | 3.43 |
| z-score | 0.08 |
| p-value | 0.573 |
| Verdict | NO_ROUTING |

The 33% rate reflects base-rate composition: 83% of A folios are Herbal, 39% of B folios are Herbal, so most random assignments will pair Herbal-to-Herbal.

### Section Residual Matrix

After pool-size regression, section-level residual means:

|  | B-B | B-C | B-H | B-S | B-T |
|--|-----|-----|-----|-----|-----|
| A-H | -1.2% | +2.0% | +2.5% | -4.2% | -1.0% |
| A-P | +4.7% | +3.3% | +5.3% | +0.3% | +1.1% |
| A-T | -5.6% | -5.3% | -2.3% | -10.5% | -10.4% |

A-H folios have a real +2.49% residual preference for B-H folios (t=24.65, p=3.3e-129 cell-level comparison). But this small effect (+2.49pp) is insufficient to override the 24 distinct A folio assignments — only a fraction of B-H folios actually get a Herbal A folio as their residual best-match.

### Interpretation

Section labels (H, P, T, B, C, S) do not function as routing addresses. The content specificity detected in C737 (6 clusters) and the residual differentiation in C751 (24 A folios) arise from MIDDLE composition differences, not section membership. Two Herbal A folios with the same pool size can serve completely different B folios depending on which MIDDLEs they contain.

## Implication

A-B routing is vocabulary-driven, not section-driven. This is consistent with C441 (ambient activation) and C384 (no direct A-B lookup). The manuscript's sections describe physical organization (illustration type, layout), not functional routing domains.

## Provenance

- Script: `phases/A_B_FOLIO_SPECIFICITY/scripts/section_coverage.py` (T9)
- Depends: C734, C735, C737, C739, C751
