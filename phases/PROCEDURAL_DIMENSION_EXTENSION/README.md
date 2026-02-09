# PROCEDURAL_DIMENSION_EXTENSION Phase

**Date:** 2026-02-05
**Status:** IN PROGRESS
**Tier:** 2-3 (Structural / Semantic Interpretation)
**Prerequisites:** BRUNSCHWIG_CLOSED_LOOP_DIMENSIONS, F-BRU-011/012/013 (Three-Tier Structure)

---

## Objective

Extend the BRUNSCHWIG_CLOSED_LOOP_DIMENSIONS PCA analysis to include **procedural/temporal features** based on the three-tier MIDDLE structure (preparation → thermodynamic → extended).

**Core question:** Does the three-tier procedural structure add independent dimensionality beyond the 5 aggregate dimensions already identified?

---

## Background

### BRUNSCHWIG_CLOSED_LOOP_DIMENSIONS (5 Dimensions)

The original PCA used aggregate features:
- ENERGY_RATE, FREQUENT_RATE, FLOW_RATE, CORE_RATE, LINK_RATE
- kernel_k, kernel_h, kernel_e
- FQ_rate, post_FQ_h

**Result:** 5 dimensions for 80% variance, exceeding Brunschwig's ~3 dimensions.

### Three-Tier MIDDLE Structure (F-BRU-011/012/013)

| Tier | MIDDLEs | Position | Brunschwig Phase |
|------|---------|----------|------------------|
| **Preparation** | te, pch, lch, tch, ksh | 0.31-0.41 | GATHER, CHOP, STRIP, POUND |
| **Thermodynamic** | k, t, e | 0.40-0.44 | Heat, timing, equilibration |
| **Extended** | ke, kch | 0.47-0.49 | Sustained/precision operations |

### Positional Constraints

| Constraint | Pattern |
|------------|---------|
| C556 | Line-level: INITIAL → MEDIAL → FINAL |
| C813 | Phase: LINK → KERNEL → FL |
| C863 | Paragraph: EARLY qo- → LATE ch/sh- |
| C873 | Kernel: e → h → k |

### Gap

The original PCA captured **what** operations occur (rates) but not **when** they occur (positional structure). The three-tier model adds temporal/procedural sequencing that may be orthogonal to aggregate rates.

---

## New Features

### Tier Density Features

| Feature | Definition | Expected Variance Contribution |
|---------|------------|-------------------------------|
| `prep_density` | (te + pch + lch + tch + ksh tokens) / total | Procedural complexity |
| `thermo_density` | (base k + t + e tokens) / total | Core operation intensity |
| `extended_density` | (ke + kch tokens) / total | Sustained/precision processing |
| `prep_thermo_ratio` | prep_density / thermo_density | Preparation vs execution balance |
| `ke_kch_ratio` | ke / (ke + kch) | Sustained vs precision mode |

### Positional Features

| Feature | Definition | Expected Variance Contribution |
|---------|------------|-------------------------------|
| `prep_mean_position` | Mean line position of prep MIDDLEs | When preparation occurs |
| `thermo_mean_position` | Mean line position of thermo MIDDLEs | When core ops occur |
| `extended_mean_position` | Mean line position of extended MIDDLEs | When extended ops occur |
| `tier_spread` | extended_position - prep_position | Procedural phase separation |
| `kernel_order_compliance` | % of lines following e→h→k order | Safety interlock adherence |

### Diversity Features

| Feature | Definition | Expected Variance Contribution |
|---------|------------|-------------------------------|
| `prep_diversity` | # unique prep MIDDLEs used / 5 | Preparation operation variety |
| `qo_chsh_early_ratio` | qo / (qo + chsh) in early lines | Energy input vs stabilization |

---

## Test Design

### Test 1: Feature Extraction

**Method:**
1. For each B folio, compute all new features
2. Validate feature distributions (outliers, missing values)
3. Compute correlation matrix with original features

**Output:** `procedural_features.json`

---

### Test 2: Extended PCA

**Method:**
1. Combine original 10 features + new 12 features = 22 features
2. Standardize all features
3. Run PCA
4. Compare variance explained: original 5D vs extended

**Expected outcomes:**
- If procedural features add independent variance: 6-8 dimensions for 80%
- If redundant with existing: Still 5 dimensions

**Output:** `extended_pca.json`

---

### Test 3: Procedural-Only PCA

**Method:**
1. Run PCA on only the 12 new procedural features
2. Determine intrinsic dimensionality
3. Test correlation with original 5 principal components

**Expected outcomes:**
- If orthogonal: Low correlation with original PCs
- If captured by existing: High correlation (r > 0.5) with original PCs

**Output:** `procedural_pca.json`

---

### Test 4: Tier Position Gradient Validation

**Method:**
1. Compute mean position per tier across all folios
2. Test if PREP < THERMO < EXTENDED ordering holds
3. Compute effect size and variance

**Expected:** Significant ordering (p < 0.001), consistent with F-BRU-011.

**Output:** `tier_position_gradient.json`

---

### Test 5: REGIME Stratification

**Method:**
1. Compute procedural features per REGIME
2. Test if REGIMEs differ on procedural dimensions
3. Compare to aggregate dimension differences

**Expected:**
- REGIME_4 (precision): Higher kch, lower ke
- REGIME_2 (gentle): Higher ke, balanced prep
- REGIME_3 (intense): Higher prep diversity

**Output:** `regime_procedural_profiles.json`

---

### Test 6: Integrated Dimensionality

**Method:**
1. Run factor analysis on combined feature set
2. Identify independent factors
3. Map factors to interpretable dimensions
4. Compare to Brunschwig procedural phases

**Output:** `integrated_dimensions.json`

---

## Success Criteria

| Level | Criteria |
|-------|----------|
| **STRONG** | 2+ new independent dimensions; procedural features orthogonal to existing |
| **MODERATE** | 1 new dimension; partial independence |
| **WEAK** | No new dimensions; procedural features redundant with existing |

**Statistical thresholds:**
- New dimension: eigenvalue > 1.0, variance contribution > 5%
- Independence: correlation with existing PCs < 0.3
- Tier ordering: Kruskal-Wallis p < 0.001

---

## Relationship to Prior Work

| Prior Work | This Phase Extends |
|------------|-------------------|
| BRUNSCHWIG_CLOSED_LOOP_DIMENSIONS | Adds procedural/positional features to PCA |
| F-BRU-011 (Three-Tier) | Tests whether tiers are independent dimensions |
| F-BRU-012 (Prep Mapping) | Uses prep MIDDLEs as features |
| F-BRU-013 (ke vs kch) | Uses extended MIDDLE differentiation |
| C556 (ENERGY medial) | Validates positional structure |
| C863 (qo early, chsh late) | Tests paragraph-level temporal structure |

---

## Data Dependencies

| Source | Use |
|--------|-----|
| BRUNSCHWIG_CLOSED_LOOP_DIMENSIONS/results/*.json | Original PCA features |
| scripts/voynich.py | Morphology extraction |
| results/regime_folio_mapping.json | REGIME assignments |

---

## Scripts

| Script | Test | Output |
|--------|------|--------|
| 01_procedural_features.py | Test 1 | procedural_features.json |
| 02_extended_pca.py | Test 2 | extended_pca.json |
| 03_procedural_pca.py | Test 3 | procedural_pca.json |
| 04_tier_position_gradient.py | Test 4 | tier_position_gradient.json |
| 05_regime_procedural_profiles.py | Test 5 | regime_procedural_profiles.json |
| 06_integrated_dimensions.py | Test 6 | integrated_dimensions.json |
| 07_integrated_verdict.py | Synthesis | procedural_dimension_verdict.json |

---

## Expected Outcomes

### If STRONG (most likely based on prior findings):

The three-tier structure adds 1-2 independent dimensions capturing:
1. **Procedural Balance** - prep vs thermo vs extended ratio
2. **Temporal Spread** - how separated the phases are within folios

This would extend the parameter space from 5D to 6-7D, strengthening the case that Voynich encodes more procedural complexity than Brunschwig's linear recipe model.

### If WEAK:

Procedural features are already captured by aggregate rates (e.g., prep_density correlates with ENERGY_RATE). This would suggest the three-tier structure is a consequence of rate patterns, not an independent encoding.

---

## Constraint Implications

Depending on results:

| Finding | Potential Constraint |
|---------|---------------------|
| Procedural dimension independent | **C9XX:** Procedural tier features add independent dimensionality beyond aggregate rates |
| Tier ordering significant | **C9XX:** PREP < THERMO < EXTENDED positional ordering (validates F-BRU-011 as Tier 2) |
| REGIME-procedural correlation | **C9XX:** REGIME predicts procedural profile (prep/thermo/extended balance) |

---

*Phase drafted: 2026-02-05*
