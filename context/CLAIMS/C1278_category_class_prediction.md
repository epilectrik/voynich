# C1278: Category Predicts Instruction Class Beyond PREFIX

**Tier:** 2
**Scope:** B
**Phase:** CATEGORY_B_EXECUTION (Phase 454)
**Date:** 2026-02-24

## Statement

Operational category reduces instruction class entropy by 1.207 bits (24.7% of H(CLASS)=4.878 bits). Critically, category adds 0.906 bits (18.6%) BEYOND what PREFIX alone provides. PREFIX explains 53.1%, category explains 24.7%, together 71.7%. The two axes are complementary: PREFIX determines lane, category determines operational role within lane. Permutation test: p=0.001, d=1051.1 (16,054 classified tokens).

## Architecture

- **Category is not a PREFIX proxy.** If categories just recapitulated PREFIX information, the conditional information gain would be zero. 18.6% additional entropy reduction proves categories capture independent instruction class structure.
- **PREFIX is still dominant.** PREFIX explains 53.1% of class entropy (C662: PREFIX reduces class membership by 75%). Category is secondary but substantial.
- **Complementary axes.** PREFIX determines the processing lane (qo, ch, sh, other). Category determines the operational role within that lane (THERMAL, TRANSITION, FLOW, etc.). Together they explain 71.7% of instruction class assignment.

## Key Findings

| Metric | Bits | % of H(CLASS) |
|--------|------|---------------|
| H(CLASS) | 4.878 | 100% |
| H(CLASS\|CATEGORY) | 3.671 | - |
| H(CLASS\|PREFIX) | 2.289 | - |
| H(CLASS\|CAT,PFX) | 1.383 | - |
| IG(CATEGORY) | 1.207 | 24.7% |
| IG(PREFIX) | 2.589 | 53.1% |
| IG(CAT+PFX) | 3.496 | 71.7% |
| IG(CAT beyond PFX) | 0.906 | 18.6% |

## Provenance

- Extends C121 (49 instruction classes) with category predictor
- Extends C662 (PREFIX reduces class membership 75%) with complementary axis
- Extends C1059 (suffix-role PREFIX-independent) with category dimension
