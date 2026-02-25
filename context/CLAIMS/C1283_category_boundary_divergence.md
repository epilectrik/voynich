# C1283: Category Differentiates Line Entry vs Exit Zones

**Tier:** 2
**Scope:** B
**Phase:** CATEGORY_B_EXECUTION (Phase 454)
**Date:** 2026-02-24

## Statement

Line entry zones (positions 1-2) and exit zones (last 2 positions) have distinct category profiles. Entry vs exit: chi2=183.6, V=0.141, p<0.001. Entry is THERMAL-enriched (24.4% vs 17.1%) and STAGING-enriched (15.7% vs 13.3%). Exit is TRANSITION-enriched (20.2% vs 13.9%) and FLOW-enriched (21.3% vs 17.2%). Three-way (entry/exit/interior): chi2=334.2, V=0.086, p<0.001. 4,612 entry tokens, 4,612 exit tokens, 13,469 interior.

## Architecture

- **Lines begin with thermal specification, end with transitions.** Entry zones carry the category-variable THERMAL content (escape-capable vocabulary per C1277). Exit zones converge on TRANSITION/FLOW (the operational baseline).
- **Connects to boundary divergence architecture.** C1157-C1168 established dual boundary divergence (entry drives 3.5x more variance than exit). C1283 shows the category mechanism: entry carries THERMAL/STAGING specification, exit carries TRANSITION/FLOW convergence.
- **THERMAL gradient within lines.** THERMAL drops from 24.4% at entry to 17.1% at exit, with interior at 25.5%. Exit zones shed thermal vocabulary, consistent with THERMAL providing escape-capable specification at line start that resolves by line end.

## Key Findings

| Category | Entry | Exit | Interior |
|----------|-------|------|----------|
| THERMAL | 0.244 | 0.171 | 0.255 |
| STAGING | 0.157 | 0.133 | 0.118 |
| OPERATION | 0.159 | 0.128 | 0.155 |
| TRANSITION | 0.139 | 0.202 | 0.134 |
| FLOW | 0.172 | 0.213 | 0.197 |
| CONTAINMENT | 0.033 | 0.055 | 0.050 |

| Metric | Value |
|--------|-------|
| Entry vs Exit chi2 | 183.6 |
| Entry vs Exit V | 0.141 |
| 3-way chi2 | 334.2 |
| 3-way V | 0.086 |

## Provenance

- Extends C1157-C1168 (boundary divergence architecture) with category mechanism
- Connects C1277 (THERMAL escape mediation) to positional structure
- Complements C1279 (mode-category differentiation) at within-line level
