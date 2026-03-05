# C1398: Paragraph Operational Gradient

**Tier:** 2 (ESTABLISHED)
**Scope:** B, paragraph, clustering, section, REGIME
**Phase:** PARAGRAPH_PROGRAM_TYPING (Phase 510)
**Extends:** C862 (parallel programs verdict), C1288 (within-folio category coherence), C1378 (paragraph material differentiation NULL)
**Relates to:** C855 (folio role template), C1295 (termination memoryless), C1296 (tail type divergence), C1380 (apparatus parameterization)

---

## Statement

Paragraphs form a **continuous operational variation space**, not discrete program types. Clustering (k-means, k=2-8, 23 features) yields a best silhouette of 0.113 (k=4), well below the 0.25 threshold for meaningful discrete structure. However, the continuum is **structured**: 4 interpretable gradient zones emerge with strong section correspondence (V=0.408) and REGIME correspondence (V=0.371). Half of all folios (50%) contain paragraphs from multiple zones, confirming that folios combine different operational emphases as subroutines within a single program.

### Gradient Zones (k=4, n=264 paragraphs with 3+ body lines)

| Zone | n | Signature | Section Bias | REGIME Bias |
|------|---|-----------|-------------|-------------|
| 0: THERMAL-QO | 87 | THERMAL +0.69z, qo_frac +0.80z, k-kernel +0.68z | BIO (55/87) | REGIME_1 (80/87) |
| 1: CONTAINMENT-Sealing | 68 | dy_frac +1.23z, headless_d +1.01z, CONTAINMENT +0.90z | HERBAL (29/68) | Mixed |
| 2: OPERATION-Iteration | 75 | OPERATION +0.88z, bare_frac +0.83z, headless_i +0.65z | STARS_RECIPE (54/75) | REGIME_3 (34/75) |
| 3: MONITORING-Phase | 34 | h_kernel +1.72z, MONITORING +1.61z, mean_middle_len +1.11z | STARS_RECIPE (24/34) | REGIME_3 (23/34) |

---

## Key Findings

### T1: Clustering — CONTINUOUS (silhouette 0.113)

All silhouette scores below 0.25 for k=2 through k=8. Best at k=4 (0.113). No elbow in inertia curve. Paragraphs do not form discrete types — they vary continuously along multiple operational dimensions.

### T2: Zone Interpretation — DIFFERENTIATED

Each zone has distinct enriched and depleted features:
- Zone 0 enriched: qo_frac (+0.80z), THERMAL (+0.69z), k_kernel (+0.68z), e_kernel (+0.52z). Depleted: STAGING (-0.79z), bare_frac (-0.68z)
- Zone 1 enriched: dy_frac (+1.23z), headless_d (+1.01z), CONTAINMENT (+0.90z), headless_frac (+0.76z). Depleted: THERMAL (-0.78z), e_kernel (-0.59z)
- Zone 2 enriched: OPERATION (+0.88z), bare_frac (+0.83z), STAGING (+0.67z), headless_i (+0.65z). Depleted: CONTAINMENT (-0.82z), k_kernel (-0.60z)
- Zone 3 enriched: h_kernel (+1.72z), MONITORING (+1.61z), mean_middle_len (+1.11z), mode_a_frac (+0.89z). Depleted: FLOW (-0.54z)

### T3: Section Correspondence — STRONG (V=0.408)

Chi2=131.9, p=2.6e-22, dof=12. BIO strongly sorts to Zone 0 (55/81). HERBAL sorts to Zone 1 (29/44). STARS_RECIPE distributes across Zones 2 and 3 (78/119). COSMO spreads across non-thermal zones.

### T4: REGIME Correspondence — STRONG (V=0.371)

Chi2=108.8, p=2.5e-19. REGIME_1 dominates Zone 0 (80/139). REGIME_3 dominates Zones 2-3 (57/80). REGIME_2 concentrates in Zone 1 (16/25). REGIME_4 distributes weakly.

### T5: Folio Composition — MULTI-TYPE (50%)

40/80 folios contain paragraphs from a single zone. 26 folios span 2 zones. 14 folios span 3 zones. Mean 1.68 clusters per folio. Folios are programs that combine multiple operational emphases.

### T6: Feature Importance — dy_frac TOP

Top discriminating features (ANOVA F-ratio): dy_frac (0.532), h_kernel (0.442), MONITORING (0.428), CONTAINMENT (0.420), headless_d_frac (0.357), mean_middle_len (0.355), bare_frac (0.355), STAGING (0.354).

The dy token (C1397: d-initial headless = CONTAINMENT sealing) is the single most discriminating feature.

### T7: Stability — MODERATE (ARI=0.765)

100 bootstrap runs: mean ARI=0.765, std=0.179. The zones are real tendencies with fuzzy boundaries, consistent with the continuous nature of the space.

### T8: Length Differentiation — SIGNIFICANT

ANOVA F=8.40, p=2.4e-5, eta2=0.088. Zone 0 longest (mean 7.0 lines), Zone 3 shortest (mean 3.9 lines). Thermal-QO paragraphs are extended programs; monitoring paragraphs are compact checks.

---

## Connection to C1378 (Paragraph Material Differentiation NULL)

Phase 492 (C1378) tested whether paragraphs encode different materials on a shared apparatus. Result: NULL — dark-pipeline MIDDLEs are near-identical across paragraphs within a folio (Jaccard 0.972). Paragraphs do NOT differentiate by material.

Phase 510 shows they differentiate by **operational emphasis** instead. Combined:
- **Same material** (C1378: dark-pipeline vocabulary identical within folio)
- **Same role proportions** (C855/C862: role template shared)
- **Different operational emphases** (C1398: thermal vs containment vs iteration vs monitoring)

Paragraphs are subroutines that each handle a different aspect of the same job, not different jobs on the same equipment. A folio-program breaks into paragraphs that specialize in different operational concerns while processing the same material with the same equipment.

---

## Falsification Criteria

1. If section control eliminates zone discrimination (V drops below 0.15), zones are section artifacts
2. If REGIME control eliminates zone discrimination, zones are REGIME artifacts
3. If silhouette exceeds 0.30 with more data or better features, the continuous verdict is wrong

---

## Method

- 264 paragraphs with 3+ body lines from 80 Currier B folios (H-track, labels excluded)
- 23 features: 8 category fractions, headless fraction + 3 sub-fractions (d/i/c), mode_a fraction, prep_prefix fraction, 3 kernel fractions (k/e/h), body line count, mean MIDDLE length, qo/chsh/bare/dy fractions
- StandardScaler normalization
- K-means clustering k=2-8 with silhouette evaluation
- Chi-squared + Cramer's V for section and REGIME correspondence
- ANOVA for length differentiation
- 100 bootstrap resamples for stability (ARI)
- Random seed 42

**Script:** `phases/PARAGRAPH_PROGRAM_TYPING/scripts/paragraph_program_typing.py`
**Results:** `phases/PARAGRAPH_PROGRAM_TYPING/results/paragraph_program_typing.json`
