# C1369 — Accent Spatial Structure

**Tier:** 2
**Scope:** B, folio, accent, spatial, section, archetype
**Phase:** 482 (ACCENT_SPATIAL_STRUCTURE)
**Depends on:** C1368, C1367, C1366, C1120, C638, C361

## Constraint

The folio_position signal in C1368's PC2 model is a **section confound** (partial R² = 0.010 < 0.02 after section control). However, **within-section local coherence exists**: adjacent folios within Bio (p=0.039) and Stars (p=0.024) have more similar accent vectors than non-adjacent folios in the same section. This local coherence does not rise to statistical significance in lag autocorrelation (0/9 significant) and does not create a manuscript-level gradient. Section boundaries show only moderate accent discontinuity (ratio 1.18). Archetypes 1 and 2 are spatially clustered (p=0.005, p=0.026), consistent with section concentration.

## Gate Test (T1): Position Beyond Section

| PC | R²(section) | R²(section+position) | Partial R² | F | p |
|----|-------------|----------------------|-----------|---|---|
| PC1 | 0.456 | 0.457 | **0.001** | 0.07 | 0.791 |
| PC2 | 0.067 | 0.077 | **0.010** | 0.72 | 0.398 |
| PC3 | 0.457 | 0.461 | **0.004** | 0.44 | 0.510 |

**Gate decision: SECTION_CONFOUND.** Position adds negligible explanatory power beyond section for all PCs. The folio_position variable in C1368's PC2 stepwise model was capturing section membership (sections are contiguous in the manuscript).

**C1368 amendment:** The PC2 model's folio_position term should be understood as section-mediated, not as evidence of manuscript-order structure. The THERMAL term remains valid (it was selected first by AIC and is section-independent).

## T2: Within-Section Adjacent Similarity

| Section | n | Observed Mean Dist | Null Mean Dist | p |
|---------|---|-------------------|----------------|---|
| B (Bio) | 20 | 3.277 | 3.976 | **0.039** |
| H (Herbal) | 22 | 1.954 | 2.126 | 0.155 |
| S (Stars) | 23 | 3.192 | 3.712 | **0.024** |

**Adjacent Bio and Stars folios are more accent-similar than random within-section pairs.** This is genuine local coherence — not a section artifact because the test is entirely within-section. Adjacent Herbal folios do NOT show this effect.

**Interpretation:** Bio and Stars programs that are physically adjacent in the manuscript tend to have similar operational accents. This is consistent with C361's 1.30x vocabulary adjacency enrichment and extends it to the M2.1 generative residual. The effect size is modest: observed distances are ~82-86% of null distances.

## T3: Quire Clustering (Herbal)

Insufficient quire data for within-Herbal comparison (quire assignments missing or all in same quire).

## T4: Lag Autocorrelation

| Section | PC1 lag-1 | PC2 lag-1 | PC3 lag-1 |
|---------|-----------|-----------|-----------|
| B | r=0.323, p=0.177 | r=0.053, p=0.828 | r=0.072, p=0.770 |
| H | r=-0.100, p=0.667 | r=0.335, p=0.138 | r=0.152, p=0.510 |
| S | r=0.196, p=0.382 | r=0.340, p=0.122 | r=0.127, p=0.573 |

**0/9 significant at p<0.05.** PC2 shows suggestive lag-1 autocorrelation in Herbal (r=0.335) and Stars (r=0.340) but neither reaches significance. Consistent with T2's local coherence being weak but present.

## T5: Section-Boundary Discontinuity

- Within-section adjacent pairs: n=64, mean distance=2.755
- Boundary pairs: n=7, mean distance=3.241
- **Ratio: 1.18** (moderate discontinuity)

Section boundaries are NOT dramatically different from within-section transitions. The accent varies relatively smoothly across the manuscript; section structure is additive (C1047) rather than creating sharp discontinuities.

## T6: Archetype Spatial Clustering

| Archetype | n | Observed Mean Position Distance | Null Mean | p |
|-----------|---|-------------------------------|-----------|---|
| 1 | 10 | 14.0 | 24.3 | **0.005** |
| 2 | 13 | 17.8 | 24.4 | **0.026** |
| 3 | 7 | 26.9 | 24.6 | 0.676 |
| 4 | 5 | 23.6 | 24.1 | 0.479 |
| 5 | 7 | 25.8 | 24.6 | 0.566 |
| 6 | 30 | 25.8 | 24.3 | 0.829 |

Archetypes 1 and 2 are spatially clustered. This is expected: Archetype 1 = BIO (C1367), and Bio folios are contiguous. Archetype 2 is similarly section-concentrated. Archetypes 3-6 are NOT spatially clustered — they are distributed throughout the manuscript.

## Synthesis

The accent has **weak but genuine local coherence** (adjacent folios within Bio and Stars share operational accent) but **no manuscript-level gradient** (position adds nothing beyond section). The spatial structure is:

1. **Section-driven at the macro level** — section membership explains 46% of PC1 and PC3, 7% of PC2
2. **Locally coherent within Bio and Stars** — adjacent folios are ~15-18% more accent-similar than random same-section pairs
3. **Not gradient-structured** — no monotonic manuscript-order trend in any PC
4. **Archetype-clustered for types 1-2** — but this reflects section concentration, not independent spatial organization

This rules out the C1368 folio_position signal as genuine manuscript-order structure and constrains the accent's spatial character to local (within-section adjacency) rather than global (manuscript-wide gradient).

## Provenance

Script: `phases/ACCENT_SPATIAL_STRUCTURE/scripts/accent_spatial_structure.py`
Results: `phases/ACCENT_SPATIAL_STRUCTURE/results/accent_spatial_structure.json`
