# C1121: Folio-Level Domain Determination

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** LIFECYCLE_DOMAIN_TEST (Phase 400)
**Extends:** C860 (section paragraph organization), C1087 (Bio-REGIME_1 divergence)
**Relates to:** C855 (role cohesion), C1029 (section-parameterized grammar), C1116 (Bio/Stars character)

---

## Statement

Paragraph domain character (Bio vs Stars) is determined at folio level, not paragraph level. ICC(1) = 0.393, ANOVA F(45,95) = 2.98. Within REGIME_1, section predicts paragraph Bio-score (Bio=0.131 vs Stars=-0.027, diff=0.158), consistent with C1087 Bio-REGIME_1 divergence. Within-paragraph domain stability confirmed (mean |delta| = 0.110, permutation p=0.19). Domain variation is a folio/section property that paragraphs inherit, not a within-paragraph progression.

---

## Evidence

### ICC Analysis

| Metric | Value |
|--------|-------|
| ICC(1) | 0.393 |
| ANOVA F(45,95) | 2.98 |
| Folios with 2+ paragraphs | 46 |
| Total paragraphs | 141 |

ICC=0.393 means folio membership explains ~39% of paragraph-level domain variance. This is substantial — comparable to C855's role cohesion (0.831 within folios).

### REGIME_1 Section Parameterization

| Section | N paragraphs | Mean Bio-score |
|---------|-------------|----------------|
| Bio (B) | 67 | +0.131 |
| Stars (S) | 29 | -0.027 |
| Herbal (H) | 3 | +0.109 |

Bio-Stars difference = 0.158 within REGIME_1, confirming section parameterization (C1087).

### Within-Paragraph Stability

First-half vs second-half Bio-fraction: real |delta|=0.110, permutation mean=0.104, p=0.19. No evidence of domain shift within paragraphs — domain character is stable throughout.

### Interpretation

Paragraphs inherit their domain character from their folio context, which is determined by section membership and REGIME assignment. This is consistent with the parallel programs model (C855): each paragraph is an independent mini-program that operates within its folio's parametric regime, not a lifecycle stage in a multi-domain progression.

---

## Provenance

- Phase: 400 (LIFECYCLE_DOMAIN_TEST)
- Script: `phases/LIFECYCLE_DOMAIN_TEST/scripts/lifecycle_domain_test.py`
- Results: `phases/LIFECYCLE_DOMAIN_TEST/results/lifecycle_domain_results.json`
- Related: C860, C855, C1029, C1087, C1116, C1120
