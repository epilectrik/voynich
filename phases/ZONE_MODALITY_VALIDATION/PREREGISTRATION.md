# Pre-Registration: Zone-Modality Validation

**Date:** 2026-01-19
**Phase:** ZONE_MODALITY_VALIDATION
**Status:** LOCKED (do not modify after analysis begins)

---

## 1. Hypotheses

### H1: P-Zone → SIGHT (Confirmation)
The intervention-permitting P-zone should correlate with SIGHT (visual monitoring) because visual cues may trigger operator action.

**Prior evidence:** t=9.00, p<0.0001, n=20

### H2: R-Zone → SOUND (Confirmation)
The progressive-restriction R-zone should correlate with SOUND (auditory monitoring) because continuous signals are tracked over time.

**Prior evidence:** t=3.97, p<0.001, n=70

### H3: S-Zone → TOUCH (Test with Enhanced Data)
The locked S-zone should correlate with TOUCH (tactile monitoring) because boundary conditions involve physical state confirmation.

**Prior evidence:** n=5, not significant
**Prediction:** With enhanced extraction (n≥15), effect should reach significance.

### H4: C-Zone → PREPARATION VERBS (Novel Hypothesis)
The setup/flexible C-zone should correlate with preparation verb density, NOT with active sensory modalities (SIGHT, SOUND).

**Prior evidence:** None (untested)
**Prediction:** C-zone shows significant positive correlation with preparation_density (r>0.2, p<0.05) and NO significant correlation with SIGHT or SOUND affinity.

---

## 2. Falsification Criteria

### Strong Falsification (Kill Hypothesis)

| Criterion | Implication |
|-----------|-------------|
| SMELL associates with P-zone (r>0.2, p<0.05) | Contradicts preparation/commitment model |
| SOUND associates with S-zone (r>0.2, p<0.05) | Contradicts progressive-restriction model |
| P-SIGHT or R-SOUND correlation flips sign | Prior findings spurious |

### Weak Falsification (Weaken Hypothesis)

| Criterion | Implication |
|-----------|-------------|
| C-zone shows no significant correlation with any property | C-zone may be purely structural |
| TOUCH remains p>0.1 at n≥15 | S-zone hypothesis fails |
| All effect sizes d<0.3 | Associations too weak to be meaningful |

---

## 3. Statistical Thresholds

| Test | Threshold | Justification |
|------|-----------|---------------|
| Significance (α) | 0.05 | Standard |
| Effect size (Cohen's d) | ≥0.3 | Small-to-medium effect |
| Permutation p-value | <0.01 | Robust confirmation |
| Bonferroni-corrected α | 0.0125 | 4 zones tested |

---

## 4. Sample Size Requirements

| Modality | Current n | Required n | Action |
|----------|-----------|------------|--------|
| SOUND | 70 | 15 | ✓ Adequate |
| SIGHT | 20 | 15 | ✓ Adequate |
| TOUCH | 5 | 15 | Enhanced extraction needed |
| SMELL | 1 | 15 | Enhanced extraction needed |
| TASTE | 2 | 15 | Likely underpowered |

---

## 5. Analysis Plan

### Step 1: Enhanced Sensory Extraction
Add keywords: verdampf, verflüchtig, qualm, wallend, erkalt, verfärbung, etc.
Target: SMELL ≥8, TOUCH ≥20 at step level

### Step 2: Zone Affinity Computation
Use existing reverse_activation results for C/P/R/S affinity per recipe.

### Step 3: Modality-Zone Correlation
For each modality with n≥15:
1. Group recipes by dominant modality
2. Compare zone affinity profiles to baseline (NONE modality)
3. Compute t-statistic and p-value
4. Compute Cohen's d effect size
5. Run 1000-iteration permutation test

### Step 4: Multiple Comparison Correction
Apply Bonferroni correction: α_corrected = 0.05/4 = 0.0125

### Step 5: C-Zone Structural Test
1. Extract preparation verbs: take, put, place, fill, gather, measure, etc.
2. Compute preparation_density = prep_verbs / total_steps
3. Correlate with C-affinity
4. Verify C-zone does NOT correlate with SIGHT or SOUND

### Step 6: Regression Controls
Run logistic regression: zone_affinity ~ modality + complexity + product_type + REGIME

---

## 6. Predictions (Locked)

| Zone | Predicted Modality | Effect Direction | Minimum d |
|------|-------------------|------------------|-----------|
| C | PREPARATION (structural) | Positive | 0.3 |
| P | SIGHT | Positive | 0.5 (existing) |
| R | SOUND | Positive | 0.4 (existing) |
| S | TOUCH | Positive | 0.3 |

### Negative Predictions (Should NOT Occur)
- C-zone correlates with SIGHT (r>0.2)
- C-zone correlates with SOUND (r>0.2)
- SMELL correlates with P-zone (r>0.2)
- SOUND correlates with S-zone (r>0.2)

---

## 7. Outcome Classification

### Strong Success
- All 4 zones have significant associations (sensory or structural)
- At least 3 zones show d≥0.3
- No strong falsification criteria triggered
- Permutation p<0.01 for confirmed associations

### Moderate Success
- Enhanced extraction reaches n≥15 for TOUCH
- P/R associations remain significant with corrections
- C-zone shows structural pattern (preparation verbs)

### Failure
- Enhanced extraction insufficient
- Strong falsification criteria triggered
- Effect sizes all d<0.3

---

## 8. Tier Decision Rule

**Remain Tier 3 if:**
- Any zone lacks n≥15 samples
- Any falsification criterion triggered
- Permutation p>0.001 for main effects

**Upgrade to Tier 2 candidate if:**
- All 4 zones tested with n≥15
- Falsification tests passed
- Permutation p<0.001
- Effect replicates in second historical source (future work)

---

*This document is LOCKED. Do not modify after analysis begins.*
