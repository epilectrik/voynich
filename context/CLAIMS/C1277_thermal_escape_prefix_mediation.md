# C1277: THERMAL Escape is PREFIX-Mediated

**Tier:** 2
**Scope:** B, A->B
**Phase:** CATEGORY_B_EXECUTION (Phase 454)
**Date:** 2026-02-24

## Statement

The THERMAL category→escape correlation (C1274, rho=+0.780) is fully mediated by qo-PREFIX routing. THERMAL MIDDLEs are 44.1% qo-prefixed (vs 9.5% baseline, 4.6x enrichment). After controlling for qo-PREFIX composition at folio level, the partial correlation collapses to rho=-0.081 (p=0.468). The causal chain is: THERMAL MIDDLEs -> qo-PREFIX selection -> zero-hazard QO lane (C601) -> escape.

## Architecture

- **Solves the escape mechanism.** C468 established 28x escape rate difference. C1274 identified THERMAL category as predictor. C1277 completes the chain: the mechanism is PREFIX routing, not an independent category effect.
- **44.1% vs 1.7%.** THERMAL MIDDLEs are 44.1% qo-prefixed. TRANSITION MIDDLEs are 1.7%. This 26x routing difference fully explains the category-escape correlation.
- **QO lane is hazard-free.** C601 established that EN_QO never participates in hazard sub-groups. THERMAL vocabulary is routed into this safe lane via qo-PREFIX, producing escape permission.
- **Category x PREFIX chi2=5845.3, V=0.291.** Category strongly predicts PREFIX selection across all 8 categories and 4 PREFIX groups (qo, ch, sh, other).

## Key Findings

| Metric | Value |
|--------|-------|
| THERMAL qo-rate | 44.1% |
| Other qo-rate | 9.5% |
| Category x PREFIX chi2 | 5845.3 |
| Cramer's V | 0.291 |
| Raw THERMAL-escape rho | +0.758 |
| Partial (controlling qo) | -0.081 (p=0.468) |
| Mediation collapsed | Yes |

## Provenance

- Decomposes C1274 (THERMAL predicts escape, rho=+0.780) into PREFIX-mediated mechanism
- Extends C397 (qo-prefix = escape route) with upstream category predictor
- Extends C911 (qo selects k-family) with category-level interpretation
- Connects C601 (EN_QO zero hazard) to category routing
