# Phase 587: BSIDE_OPERATIONAL_SIGNATURES

**Status:** COMPLETE
**Date:** 2026-03-14
**Version:** 5.60
**Constraints:** C1702-C1705

## Purpose

Phases 585-586 showed the discrimination manifold is mostly a frequency artifact (73%) and no deployment layer closes the remaining gap. This phase changes approach: instead of looking at A's internal structure, look at what A does to B. Each A record's C502.a three-axis morphological filter reduces B's 4,889 tokens to ~38 survivors (0.8%). The survivor set IS the record's operational meaning — which B program the material permits. If A classifies by operational parametrics, this should be visible in B-side operational signatures.

## Scripts

| Script | Runtime | Purpose |
|--------|---------|---------|
| `scripts/bside_operational_signatures.py` | ~760s | 5 tests (T0-T4): noise floor, folio coherence, section prediction, RI extension predictions, C475-pair divergence |

## Results

### B-Side Signature Vector (16 dimensions)

Per record's survivor set: 8 category fractions (THERMAL, FLOW, CONTAINMENT, STAGING, OPERATION, TRANSITION, MARKING, MONITORING), 6 HEAD fractions (k, t, a, e, o, headless), k-initial fraction, hazard exposure count.

### Test Results

| Test | Metric | Value | Threshold | Pass? |
|------|--------|-------|-----------|-------|
| T0: Noise Floor | Mean cosine sim | 0.902 | --- | baseline |
| T1: Folio Coherence | z-score | 15.15 | --- | significant |
| T1: Folio Coherence | Within/between ratio | 1.086 | --- | weak |
| T1: Section ANOVA | Significant features | 11/16 | --- | most vary |
| T2: Section Prediction (record) | LOO-CV accuracy | 34.8% (1.74x) | 2.0x | NO |
| T2: Section Prediction (folio) | LOO-CV accuracy | 43.9% (2.19x) | 2.0x | YES |
| T3: RI Extension | Predictions passed | 1/5 | 4/5 | NO |
| T4: C475 Divergence | Cohen's d | 0.816 | significant | YES |
| T4: C475 Divergence | p-value | 3.8e-289 | <0.05 | YES |

### Key Findings

1. **Noise floor is very high (0.902 cosine similarity).** Random draws of 36 B tokens from a 4,889-token universe already look very similar in 16-dim signature space. This makes detecting genuine structure harder — real signatures must overcome this high baseline.

2. **Folio coherence exists but is weak (ratio 1.086).** Records within the same folio have B-side signatures only 8.6% more similar than between-folio pairs. This is statistically significant (z=15.15) but practically small. Most signature variation is between records, not between folios.

3. **Section prediction works at folio level (2.19x) but not record level (1.74x).** Pooling across records within a folio averages out noise and reveals weak section-level structure. Top discriminating features: HEAD_headless (0.109), HEAD_o (0.103), STAGING (0.096), HEAD_e (0.093), FLOW (0.084).

4. **RI extension predictions mostly fail (1/5).** Only e-extension → HEAD_e enrichment passes Bonferroni (d=0.479, p=0.003). k-extension → HEAD_k has correct direction with medium effect (d=0.515) but fails Bonferroni (p=0.060). Other predictions (h→MONITORING, d→TRANSITION, t→FLOW) show negligible effects.

5. **C475-pair divergence is the star finding (d=0.816).** C475-incompatible record pairs (sharing no compatible MIDDLEs) produce significantly more divergent B-side operational signatures than compatible pairs (mean cosine distance 0.618 vs 0.450). This is a large effect. The discrimination manifold's geometry maps to B-side operational divergence — records that are C475-incompatible specify genuinely different B programs.

6. **The structure is pair-level, not categorical.** C475 compatibility geometry has strong B-side operational meaning, but this doesn't organize into clean macroscopic categories (sections, RI extension groups). The discrimination manifold encodes operational specificity at the MIDDLE-pair level, not at the category level.

## Constraint Verdicts

| C# | Verdict | Description |
|----|---------|-------------|
| C1702 | FOLIO_BSIDE_COHERENCE_WEAK | Within-folio B-side similarity z=15.15 (significant) but ratio=1.086 (8.6% above between-folio); PP Jaccard within=0.110 vs between=0.085; 11/16 features significant in section ANOVA |
| C1703 | SECTION_PREDICTION_PARTIAL | Folio-level LOO-CV 43.9% (2.19x chance, passes); record-level 34.8% (1.74x, fails); section signal exists but is noisy at record level |
| C1704 | EXTENSION_PREDICTIONS_FAIL | 1/5 RI extension directional predictions pass Bonferroni; only e→HEAD_e confirmed (d=0.479, p=0.003); k→HEAD_k correct direction but p=0.060 |
| C1705 | C475_OPERATIONAL_DIVERGENCE_CONFIRMED | C475-incompatible pairs diverge more in B-side space (d=0.816, p=3.8e-289); discrimination manifold geometry maps to B-side operational meaning at pair level |

## Verdict

**C475_DIVERGENCE_CONFIRMED / SECTION_STRUCTURE_PARTIAL.** The discrimination manifold has real functional meaning: records that are C475-incompatible (share no compatible MIDDLEs) produce significantly different B-side operational signatures (d=0.816). However, this pair-level operational divergence does not organize into clean macroscopic categories — section prediction works only at folio level (2.19x), and RI extension predictions fail.

The manifold encodes which B programs each A record permits, but this encoding is specific to individual MIDDLE compatibility relationships, not to categorical groupings. A's organizational logic propagates through C502.a filtering to B-side operational space, but at the resolution of individual record pairs, not sections or extension types.
