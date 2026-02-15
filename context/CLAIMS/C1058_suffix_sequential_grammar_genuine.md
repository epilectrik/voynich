# C1058: Suffix Sequential Grammar Is Genuine

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** MORPHOLOGICAL_DEEP_STRUCTURE (Phase 379)
**Extends:** C1002 (suffix sequential grammar V=0.063)
**Relates to:** C1004 (zero cross-token prediction), C957 (mandatory bigrams), C1029 (section-parameterized grammar), C611 (PREFIX-based role assignment)

---

## Statement

The suffix bigram signal (C1002: V=0.063) is **genuine suffix-to-suffix grammar**, not an artifact of role sequences or token repetition. A 3-stage decomposition removes only 6.2% of the signal:

| Stage | V | Reduction |
|-------|---|-----------|
| Raw | 0.0662 | — |
| Role-conditioned | 0.0635 | -4.1% |
| No token repeats | 0.0644 | -2.7% |
| Combined (residual) | **0.0621** | -6.2% |

Top residual suffix pairs (after both corrections):

| Pair | Observed | Expected | z |
|------|----------|----------|---|
| dy→dy | 104 | 41.3 | +9.76 |
| edy→edy | 297 | 175.9 | +9.13 |
| ain→hy | 69 | 28.8 | +7.48 |
| s→s | 19 | 5.5 | +5.74 |
| edy→NONE | 707 | 852.3 | -4.98 |

18 suffix pairs with |z| > 3.0 in the combined residual. Signal is dominated by self-repetition (dy→dy, edy→edy, s→s) and cross-suffix transitions (ain→hy, dy→ar).

Section sub-analysis (no-repeat raw V):

| Section | V | n |
|---------|---|---|
| S | 0.079 | 9508 |
| B | 0.086 | 6002 |
| H | 0.092 | 3033 |
| C | 0.129 | 1345 |
| T | 0.195 | 590 |

Signal is **section-universal** (present in all 5 sections) but **section-modulated** (stronger in smaller sections T, C).

---

## Interpretation

C1002 found suffix bigram grammar (V=0.063) but could not determine whether this was genuine suffix structure or confounded by role sequences (e.g., EN→EN inherently produces edy→edy). This decomposition proves the signal is genuine: role conditioning removes only 4.1%, token repetition removes only 2.7%, and the combined residual (V=0.062) remains highly significant.

The top drivers (dy→dy, edy→edy, ain→hy) include both within-suffix repetition and cross-suffix transitions. The ain→hy pair is particularly informative: -ain and -hy are different suffixes on different tokens, confirming the signal is not merely self-repetition.

The negative residuals (edy→NONE at z=-4.98) show that suffixed tokens are **depleted** before bare tokens — a token with -edy suffix is followed by a bare MIDDLE less often than expected. This complements C1004's finding of zero cross-token information: the sequential grammar operates at the suffix level, not the full-token level.

---

## Method

- 20,676 suffix bigrams from Currier B consecutive token pairs within lines
- Stage 1: Assign roles via 49-class taxonomy (classified) or PREFIX-dominant role (UN, per C611). Compute expected suffix bigrams conditioned on role-pair frequencies. Compute residual V.
- Stage 2: Remove 198 exact token-repeat pairs (1.0% of total). Recompute V.
- Stage 3: Apply both corrections. Compute residual V.
- Section sub-analysis: Repeat Stage 2 per section.
- Residual pairs: Standardized residuals (observed - expected) / sqrt(expected) for the combined-corrected table.

**Script:** `phases/MORPHOLOGICAL_DEEP_STRUCTURE/scripts/morphological_deep_structure.py`
**Results:** `phases/MORPHOLOGICAL_DEEP_STRUCTURE/results/t1_suffix_signal_decomposition.json`
