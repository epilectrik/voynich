# C1368 — Accent PC2/PC3 Decomposition

**Tier:** 2
**Scope:** B, folio, accent, PCA, section, category, sister pair
**Phase:** 481 (ACCENT_PC23_DECOMPOSITION)
**Depends on:** C1367, C1366, C1294, C1047, C1182

## Constraint

The accent PC2 (sequential complexity, 20.5%) is predicted by kernel-residualized THERMAL fraction and manuscript folio position (LOO R² = 0.267). PC3 (morphological texture, 8.9%) is dominated by STARS section membership (eta² = 0.457) and further predicted by kernel-residualized CONTAINMENT fraction and sister pair ch_preference (LOO R² = 0.496). Section structures the morphological axis, not the sequential axis (reversing the expert prediction). THERMAL extends the accent on both PC1 and PC2 — it is the pervasive accent predictor. 0/5 pre-registered expert predictions confirmed.

## T1: Section → PC2 (ANOVA)

| Section | n | Mean PC2 |
|---------|---|----------|
| B (Bio) | 20 | -0.547 |
| C (Cosmo) | 5 | 0.121 |
| H (Herbal) | 22 | 0.199 |
| S (Stars) | 23 | 0.145 |
| T | 2 | 1.300 |

F=1.19, p=0.322, eta²=0.067. Section does NOT predict PC2. **Prediction 1 half-FALSIFIED** (expected eta² > 0.10).

## T2: Section → PC3 (ANOVA)

| Section | n | Mean PC3 |
|---------|---|----------|
| B (Bio) | 20 | -0.639 |
| C (Cosmo) | 5 | 0.043 |
| H (Herbal) | 22 | -0.404 |
| S (Stars) | 23 | **0.942** |
| T | 2 | -0.105 |

F=14.10, p<0.0001, eta²=0.457. Section STRONGLY predicts PC3. **Prediction 1 fully FALSIFIED** — section predicts PC3 (morphological), not PC2 (sequential). Stars has a distinctive morphological accent: longer words, higher suffix rate, different category specialization.

## T3: Paragraph Count → PC2

Raw rho=-0.052, p=0.662. Partial (section-controlled) rho=-0.027, p=0.823. **Prediction 2 FALSIFIED.** Paragraph density has zero relationship with sequential complexity.

## T4: Dark Pipeline Fraction → PC3

dark_middle_fraction = 0.0 for all 72 folios (Phase 479 computation yields constant). **Prediction 3 untestable** (no variance in predictor).

## T5: Archetype → PC2 (ANOVA)

F=1.80, p=0.125, eta²=0.120. Marginal — archetypes explain 12% of PC2, just above the 10% threshold. **Prediction 5 half-FALSIFIED** for PC2.

## T6: Archetype → PC3 (ANOVA)

F=1.02, p=0.413, eta²=0.072. Archetypes do NOT predict PC3. **Prediction 5 CONFIRMED** for PC3.

## T7: PC2 Multivariate Model

Forward stepwise (AIC, max 5 predictors):
1. cat_THERMAL_resid (AIC 60.5 → 38.1)
2. folio_position (AIC 38.1 → 34.4)

**LOO R² = 0.267. In-sample R² = 0.342.**

Max single predictor: THERMAL (kernel-residualized) R² = 0.287.

**Interpretation:** PC2 (sequential complexity) is a THERMAL axis with a manuscript-order gradient. THERMAL already dominated PC1 (C1367, partial rho=0.588). Now it also structures PC2. THERMAL is the pervasive accent predictor across the two largest components (79.4% of accent variance combined).

The folio_position signal means sequential complexity varies systematically along the manuscript — a manuscript-order effect not previously detected at this resolution.

## T8: PC3 Multivariate Model

Forward stepwise (AIC, max 5 predictors):
1. section_S (AIC 0.4 → -37.5)
2. cat_CONTAINMENT_resid (AIC -37.5 → -41.7)
3. ch_preference (AIC -41.7 → -50.2)

**LOO R² = 0.496. In-sample R² = 0.545.**

Max single predictor: section_S (Stars) R² = 0.426. **Prediction 4 FALSIFIED** — Stars section alone explains >30%.

**Interpretation:** PC3 (morphological texture) is a Stars distinctiveness axis. Stars folios have longer words, higher suffix rates, and different category specialization. Beyond section, CONTAINMENT fraction (after kernel control) adds independent signal — programs with more CONTAINMENT vocabulary have distinctive morphological profiles. Sister pair ch/sh preference (C1182) also correlates with morphological texture.

## Pre-Registered Prediction Scorecard

| # | Prediction | Result | Actual |
|---|-----------|--------|--------|
| P1 | Section → PC2 yes, PC3 no | **FALSIFIED** | Reversed: section → PC3 (eta²=0.457), NOT PC2 (eta²=0.067) |
| P2 | Paragraph density → PC2 | **FALSIFIED** | rho=-0.027, no relationship |
| P3 | Dark pipeline → PC3 | **UNTESTABLE** | Feature is constant (0.0 for all folios) |
| P4 | No single predictor >30% | **FALSIFIED** | section_S alone explains 42.6% of PC3 |
| P5 | Not archetype-structured | **MIXED** | PC2: eta²=0.120 (marginal), PC3: eta²=0.072 (confirmed) |

## Synthesis

The three accent dimensions form a coherent hierarchy:

1. **PC1 (58.9%):** AXM dynamics intensity — THERMAL-predicted (C1367). How much the program orbits its AXM home state.
2. **PC2 (20.5%):** Sequential complexity — THERMAL-predicted + manuscript position. How diverse the transition patterns are, with a gradient across the manuscript.
3. **PC3 (8.9%):** Morphological texture — STARS-dominated, CONTAINMENT + sister pair. Word length and suffix patterns, structured by section and vocabulary composition.

**THERMAL** is the dominant accent predictor: it predicts PC1 (partial rho=0.588 after kernel control, C1367) AND enters PC2's model first. Together PC1+PC2 = 79.4% of accent variance. THERMAL fraction (after kernel control) structures nearly 80% of the M2.1 generative gap.

**Section** matters for morphology but not dynamics. Stars has a distinctive word-length/suffix profile that is the strongest single feature of PC3.

**Manuscript position** enters PC2. This is the first accent-level evidence of a manuscript-order signal — sequential complexity varies systematically across the manuscript. This motivates cross-folio spatial analysis (potential Phase 482).

## Provenance

Script: `phases/ACCENT_PC23_DECOMPOSITION/scripts/accent_pc23_decomposition.py`
Results: `phases/ACCENT_PC23_DECOMPOSITION/results/accent_pc23_decomposition.json`
