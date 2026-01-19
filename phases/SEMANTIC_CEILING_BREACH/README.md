# SEMANTIC_CEILING_BREACH Phase

**Status:** IN PROGRESS
**Date:** 2026-01-19

---

## Pre-Registration (Locked Before Analysis)

This document was created BEFORE running any prediction tests. The hypotheses and thresholds below are fixed.

---

## Primary Hypothesis

**H1: Zone affinity profiles discriminate sensory modality classes**

Given only a recipe's zone_affinity vector (C/P/R/S proportions), we can predict whether the recipe is SOUND-dominant or non-SOUND with accuracy significantly above baseline.

---

## Pre-Registered Predictions

### P1: Binary Classification (SOUND vs non-SOUND)

- **Baseline**: 79.1% (majority class = SOUND, n=87/110)
- **Success threshold**: >85% accuracy with balanced F1 >0.7
- **Permutation significance**: p<0.01 (1000 shuffles)

### P2: 4-Class Classification

- **Baseline**: 25% (random chance)
- **Success threshold**: >40% accuracy (p<0.05)
- **Classes**: SOUND (n=87), TASTE (n=13), SIGHT (n=7), TOUCH (n=3)

### P3: MIDDLE Cluster-Modality Correlation

- **Threshold**: Correlation coefficient >0.3 between zone cluster assignment and modality distribution
- **Clusters**: 3 existing clusters from middle_zone_survival.json

### P4: REGIME Independence

- **If REGIME alone explains zone variance (R-squared >0.7)**: Semantic ceiling is at REGIME level
- **If residual variance is semantically patterned (R-squared <0.3)**: Zone carries independent information

---

## Falsification Criteria

### Strong Falsification (KILLS hypothesis)

1. Binary accuracy <79.1% (worse than majority baseline)
2. 4-class accuracy <25% (worse than random)
3. Zone-modality correlation r <0.1

### Weak Falsification (WEAKENS hypothesis)

1. Binary accuracy 79-85% (not significantly better than baseline)
2. Permutation p-value >0.05
3. REGIME alone explains >90% of zone variance

---

## Success Criteria

### Tier 2 Upgrade (ALL required)

1. Binary accuracy >85% with permutation p<0.01
2. OR 4-class accuracy >50% with p<0.001
3. Cross-validation stability: std <10% across folds
4. No C384 violations detected

### Tier 3 Confirmation

- Accuracy 80-85%, borderline significant
- Clear trend supporting two-stage model
- Consistent with existing constraints

---

## Constraints Respected

| Constraint | How Respected |
|------------|---------------|
| **C384** | All tests at vocabulary/aggregate level, no entry-level mapping |
| **C469** | Categorical zone assignment maintained |
| **C468** | Legality inheritance respected |

---

## Data Sources

| File | Contents | Locked |
|------|----------|--------|
| `results/brunschwig_reverse_activation.json` | Zone affinity per recipe | YES |
| `results/enhanced_sensory_extraction.json` | Modality labels | YES |
| `results/middle_zone_survival.json` | MIDDLE clustering | YES |

---

## Scripts

| Script | Purpose |
|--------|---------|
| `scb_01_modality_prediction_test.py` | PRIMARY: Zone -> Modality classifier |
| `scb_02_middle_zone_clustering.py` | SECONDARY: MIDDLE cluster correlation |
| `scb_03_regime_zone_regression.py` | CONTROL: REGIME independence test |
| `scb_04_folio_behavioral_profiles.py` | EXTENSION: B folio fingerprints |
| `scb_05_synthesis.py` | Generate final report |

---

*Pre-registration locked: 2026-01-19*
*Expert-advisor consultation completed*
