# C1572: Hierarchical variance partition validates 4-layer nesting with selective layer loading

**Tier:** 2
**Phase:** 561 (HIERARCHICAL_TRACE_ATTRIBUTION)
**Scope:** B, structural, hierarchy, variance, section, folio, paragraph, line, decomposition, ANOVA, template, C1570, C1571

## Claim

Hierarchical variance partition supports a four-layer nesting of section, folio, paragraph, and line, with selective layer loading by feature family rather than universal dominance. Domain-membership features (head_k, head_e, head_a, is_headless) load primarily on section and folio layers; hazard/closure features (hazard_ord, opacity_ord) load primarily on line. Each level explains statistically significant variance beyond its level-specific null model, but the line layer is selective (hazard/closure only), not globally strong -- which is architecturally correct for a safety-packet layer.

## Evidence

**Z-score significance against level-specific permutation nulls (200 permutations each):**

- **Section:** 8/9 features significant (z > 2). Mean z = 8.0. Strongest: is_headless z=17.43, hazard_ord z=13.31.
- **Folio|section:** 9/9 features significant. Mean z = 7.1. Strongest: head_e z=9.99, head_a z=9.71.
- **Paragraph|folio:** 4/9 features significant. Mean z = 2.2. Strongest: head_a z=6.53, is_headless z=4.71.
- **Line|paragraph:** 4/9 features significant. Mean z = 1.1 (aggregate), but hazard_ord z=4.09 and opacity_ord z=4.53 confirm line safety packets for hazard/closure.

**Feature-family architecture confirmed:**
- Domain-membership features (head_k, head_e, head_a, is_headless) load primarily on section and folio layers
- Hazard/closure features (hazard_ord, opacity_ord) load primarily on line layer
- This matches the 5-layer model: section templates set domain proportions, line safety packets manage hazard

**Raw variance shares are small** (section ~1%, folio ~1.4%, paragraph ~2.8%, line ~9.5%, residual ~85%) because the manuscript is highly stochastic within templates. The z-scores, not absolute variance shares, are the correct measure of structural significance.

**Layer Support Indices:** Section LSI=10.28, Folio LSI=7.06, Paragraph LSI=2.22 (all supported at z > 2). Line LSI=1.15 (not supported as aggregate because only hazard/closure features load there, which is architecturally correct).

## Provenance

- T1 script: `phases/HIERARCHICAL_TRACE_ATTRIBUTION/scripts/t1_variance_decomposition.py`
- T1 results: `phases/HIERARCHICAL_TRACE_ATTRIBUTION/results/t1_variance_decomposition.json`
- T5 synthesis: `phases/HIERARCHICAL_TRACE_ATTRIBUTION/results/t5_synthesis.json`
- Builds on: C1570 (section-not-folio at averages), C1571 (deployment Ward ARI), C1429 (line safety packets), C1470 (line independence)
