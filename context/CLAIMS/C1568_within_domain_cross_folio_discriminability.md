# C1568: Within-Domain Cross-Folio Discriminability

**Tier:** 2
**Scope:** B, MIDDLE, atom, HEAD, domain, compositional, cross-folio, discriminability, section, classification, random-forest, C1475, C1556, C1563
**Phase:** WITHIN_DOMAIN_COMPOSITIONAL_CONTROL (Phase 560)
**Date:** 2026-03-08

## Claim

Cross-folio within-domain profiles add discriminative power beyond HEAD distribution alone. Two independent methods confirm the gain:

- **Nearest-neighbor:** +6.1 percentage points (HEAD-only 73.2%, full 79.3%)
- **Random forest:** +8.8 percentage points (HEAD-only 79.2%, full 87.9%)

Both exceed the 5pp threshold. The additional information comes from within-domain parameterization (terminal allocation, modifier rates, routing preferences), not just domain proportions.

Top discriminative within-domain features (RF importance):
1. o_l_frac (0.105) — ARRANGEMENT terminal allocation
2. xd_headless_frac (0.091) — headless fraction of total
3. t_flow_purity (0.060) — FLOW category purity
4. e_ey_frac (0.048) — STABILITY e->y density
5. t_mod_rate (0.048) — FLOW modifier rate
6. adj_r_to_a_rate (0.042) — r->a routing rate
7. adj_y_to_k_rate (0.039) — y->k routing rate

## Evidence

### D5a: Leave-one-out nearest-neighbor

82 qualifying folios (>= 20 tokens), 6-feature HEAD-only baseline vs 38-feature full model (HEAD + 32 within-domain features), z-scored, NaN-aware.

| Model | Accuracy |
|---|---|
| HEAD-only (6 features) | 73.2% |
| Full (38 features) | 79.3% |
| **Gain** | **+6.1pp** |

### D5b: Random forest 5-fold CV

100 trees, max_depth=5, same feature sets.

| Model | Accuracy |
|---|---|
| HEAD-only | 79.2% |
| Full | 87.9% |
| **Gain** | **+8.8pp** |

### Null model comparison (D1)

Within-domain permutation null (200 seeds, shuffling tokens across folios within each domain while preserving per-folio domain counts):

| Metric | Real | Null |
|---|---|---|
| Section classification accuracy | 76.8% | 52.7% +/- 4.9% |

Real accuracy is 4.9 sigma above null mean, confirming within-domain features carry genuine folio/section-specific information.

### Feature variance (D2)

15 of 32 within-domain features show significant section-level variance (F > 3.2, one-way ANOVA).

## Interpretation

Within-domain features — how each domain's control dials are tuned — carry information beyond what HEAD proportions alone reveal. This means sections (Herbal, Bio, Stars, etc.) differ not just in HOW MUCH of each domain they use, but in HOW they use each domain. For example, Stars folios may have different ARRANGEMENT terminal allocation (o_l_frac) or STABILITY e->y density than Bio folios, even after accounting for their different HEAD distributions.

This validates the architectural premise: HEAD selects domain, subordinate features are real control dials that carry programmatic meaning, and that meaning varies systematically across the manuscript.

## Falsification Criteria

1. If the D5 gain disappears under leave-section-out cross-validation (i.e., when predicting sections never seen in training)
2. If the gain is entirely driven by domain proportion features (hl_frac, a_frac) rather than true within-domain features
3. If a different token decomposition (e.g., different HEAD/TERM boundary rules) produces no D5 gain

## Source

`phases/WITHIN_DOMAIN_COMPOSITIONAL_CONTROL/results/t3_cross_folio_discriminability.json`
