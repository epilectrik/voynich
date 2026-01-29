# C672: Cross-Line Boundary Grammar

**Status:** VALIDATED | **Tier:** 0 | **Phase:** B_LINE_SEQUENTIAL_STRUCTURE | **Scope:** B

## Finding

Cross-line boundary transitions (last class of line N -> first class of line N+1) are **slightly more constrained** than within-line bigrams. H(next|prev) at boundaries = 4.284 bits vs within-line = 4.628 bits (ratio = 0.926). However, the boundary transition matrix is NOT significantly non-independent (chi2=2267.89, dof=2209, p=0.187).

## Method

Collect all boundary pairs (last token class of line N, first token class of line N+1) for adjacent lines within folios. Build transition matrix. Compute conditional entropy H(next_class | prev_class) for boundary vs within-line contexts. Chi-square independence test on boundary matrix.

## Key Numbers

| Metric | Value |
|--------|-------|
| Boundary pairs | 2,304 |
| Within-line pairs | 13,457 |
| H(next\|prev) boundary | 4.284 bits |
| H(next\|prev) within-line | 4.628 bits |
| H unconditional | 5.028 bits |
| Boundary/within ratio | 0.926 |
| Chi-square | 2267.89, dof=2209, p=0.187 |

## Boundary Role Transitions

| From \ To | CC | EN | FL | FQ | AX |
|-----------|----|----|----|----|-----|
| CC | 9.7% | 36.8% | 4.2% | 14.6% | 34.7% |
| EN | 8.5% | 43.6% | 5.7% | 11.6% | 30.6% |
| FL | 7.4% | 38.8% | 5.4% | 9.3% | 39.1% |
| FQ | 10.0% | 32.0% | 7.8% | 13.5% | 36.6% |
| AX | 8.6% | 37.5% | 6.2% | 11.1% | 36.6% |

## Interpretation

Line boundaries are not informationally special — they carry similar but slightly less uncertainty than within-line transitions. The 7.4% entropy reduction at boundaries is consistent with C389's bigram determinism operating across line boundaries, not just within them. Lines are grammatically contiguous: the grammar treats line breaks as transparent, not as reset points.

This is consistent with C357 (0 cross-line grammar violations) — now quantified as entropy reduction rather than binary violation count.

## Provenance

- Script: `phases/B_LINE_SEQUENTIAL_STRUCTURE/scripts/line_sequential_coupling.py` (Test 3)
- Extends: C389 (H=0.41 bits within-line bigram determinism), C357 (lines as formal control blocks)
