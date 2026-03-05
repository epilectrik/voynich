# C1433: PREFIX-AXM mediation chain is complete at paragraph level

**Tier:** 2
**Scope:** B, paragraph, AXM, PREFIX, mediation, C1405, C1411, C1418, C1422
**Phase:** 520 (PARAGRAPH_AXM_RESIDUAL)
**Date:** 2026-03-05

## Claim

The PREFIX->AXM pathway (C1405) is the ONLY load-bearing predictor at paragraph level. The mediation chain is complete: PREFIX selects MIDDLE HEAD atoms (C1411), MIDDLE determines suffix mode (C1422), PREFIX determines articulators (C1418). All downstream features are fully mediated. No interaction, compound, or structural feature carries independent signal. The instruction construction grammar (C1411-C1415) generates paragraph-level dynamics through a single bottleneck: PREFIX composition. The 4.2% genuine design freedom (C1432) represents irreducible per-program variation that no token-level feature can predict.

## Evidence

### Mediation chain validated
1. PREFIX -> MIDDLE HEAD: V=0.414 (C1411). HEAD atoms alone explain 26.0% of AXM (CV R2) but add -0.5% beyond PREFIX. Fully mediated.
2. PREFIX -> ARTICULATOR: PREFIX-locked (C1418). Articulators add -0.2% beyond PREFIX. Fully mediated.
3. MIDDLE -> suffix mode: NMI=0.173 (C1422). Suffix features add -0.3% beyond PREFIX. Doubly mediated (PREFIX->MIDDLE->suffix).
4. HEAD atom correlations with AXM (k: +0.491, a: -0.553) survive individually but vanish when PREFIX is controlled. The chain k-initial -> Mode A -> THERMAL -> AXM dwell (C1384) is REAL but operates THROUGH PREFIX.

### No independent signal from any non-PREFIX source
- Full model (41 features) degrades relative to PREFIX-only: CV delta = -0.004, LOO delta = -0.011
- 0/7 non-PREFIX groups improve prediction in add-one analysis (excluding marginal MIDDLE_PROPS at +0.013 which vanishes in full model)
- PREFIX-MIDDLE interaction terms produce massive overfitting (60 terms: delta = -0.155)
- Even 3 key interaction terms add nothing (delta = -0.006)

### Residual is unstructured
- Normally distributed (Shapiro-Wilk p=0.152)
- No section, REGIME, position, or folio pattern survives
- 85.5% of residual is measurement noise (C1432)

## Interpretation

The instruction grammar has a single dynamical control point at paragraph level. PREFIX composition -- specifically the relative fractions of qo, chsh, bare, ok, ot, da, pch, tch, lch, and ol -- determines what macro-state dynamics a paragraph will exhibit. This is not a partial mediation or a dominant effect with secondary contributors. It is the SOLE pathway. The remaining 4.2% genuine design freedom cannot be captured by any morphological, structural, or compositional feature of the tokens.

## Method

- 283 paragraphs, 41 features, 10-fold CV Ridge regression
- Systematic add-one and drop-one analysis across 8 feature groups
- Interaction term testing (60 full + 3 key terms)
- Noise floor estimation via binomial sampling variance

## Provenance

- Script: `phases/PARAGRAPH_AXM_RESIDUAL/scripts/paragraph_axm_residual.py`
- Results: `phases/PARAGRAPH_AXM_RESIDUAL/results/paragraph_axm_residual.json`

## Dependencies

- C1405 (PREFIX alone R2=0.736)
- C1411 (PREFIX->MIDDLE HEAD selectivity V=0.414)
- C1418 (PREFIX->ARTICULATOR)
- C1422 (MIDDLE->suffix mode NMI=0.173)
- C1384 (k-initial predicts AXM dwell)
- C1432 (residual is 85% noise)
- C1169 (AXM residual closed at folio level)
