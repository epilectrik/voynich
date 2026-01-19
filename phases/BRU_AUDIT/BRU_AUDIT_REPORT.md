# BRU-AUDIT: Brunschwig Backprop Data Hygiene Audit

**Phase:** BRU-AUDIT
**Date:** 2026-01-16
**Status:** COMPLETE
**Verdict:** PARTIAL VALIDATION - Structure preserved, magnitudes weakened

---

## Executive Summary

This phase audited the Brunschwig backward propagation work for H-only transcriber compliance. We found:

1. **9 scripts lacked H-only filtering** (creating ~3.2x token inflation)
2. **All scripts have been fixed**
3. **Core findings SURVIVE but are WEAKER** with clean data:
   - Product-exclusive MIDDLEs: 78.2% -> 71.8% (survived)
   - Profile differences: 0.105 -> 0.064 (below threshold)
   - MIDDLE hierarchy: PRESERVED (ratio shifts but structure intact)
   - Blind predictions: 8/8 -> 6/8 (still valid, less precise)

**Conclusion:** The Brunschwig backprop framework is structurally valid but the product type discrimination was overstated. Findings should be used with revised values.

---

## Scripts Fixed

### BRUNSCHWIG_TEMPLATE_FIT (4 scripts)

| Script | Status |
|--------|--------|
| `exclusive_middle_backprop.py` | FIXED (foundational) |
| `product_a_correlation.py` | FIXED |
| `a_record_product_profiles.py` | FIXED |
| `precision_prefix_analysis.py` | FIXED |

### BRUNSCHWIG_BACKPROP_VALIDATION (5 scripts)

| Script | Status |
|--------|--------|
| `recipe_to_register_test.py` | FIXED |
| `cross_type_middle_analysis.py` | FIXED |
| `middle_property_analysis.py` | FIXED |
| `cluster_property_correlation.py` | FIXED |
| `stability_perturbation_test.py` | FIXED |

### Already Compliant (2 scripts)

| Script | Status |
|--------|--------|
| `azc_projection_invariance.py` | Already had H-only filter |
| `azc_zone_bias_test.py` | Already had H-only filter |

---

## Test Results

### Test 1: Product-Exclusive MIDDLEs

**Question:** Does the 78.2% product-exclusive finding hold?

| Metric | OLD (inflated) | NEW (H-only) | Change |
|--------|----------------|--------------|--------|
| Total MIDDLEs | 3,357 | 2,240 | -33.3% |
| PRECISION exclusive | 513 | 368 | -28.3% |
| WATER_GENTLE exclusive | 519 | 368 | -29.1% |
| OIL_RESIN exclusive | 466 | 383 | -17.8% |
| WATER_STANDARD exclusive | 1,859 | 1,121 | -39.7% |
| **% Exclusive** | **78.2%** | **71.8%** | **-6.4pp** |

**Verdict:** SURVIVED - Structure exists but counts lower

---

### Test 2: Product Type Profile Discrimination

**Question:** Do product types show distinct A signatures?

| Metric | OLD | NEW | Threshold | Verdict |
|--------|-----|-----|-----------|---------|
| Mean profile diff | 0.105 | 0.064 | 0.10 | FAILED |

**Verdict:** WEAKENED - Profiles now below discriminability threshold

The original claim "A records show PRODUCT-SPECIFIC profiles" is no longer supported at the 0.10 threshold. Product types exist but are less separable.

---

### Test 3: MIDDLE Hierarchy (F-BRU-005)

**Question:** Does the Universal/Cross-cutting/Type-specific split hold?

| Layer | OLD | NEW | Change | Status |
|-------|-----|-----|--------|--------|
| Universal (4 types) | 3.5% (106) | 6.1% (129) | +2.6pp | PRESERVED |
| Cross-cutting (2-3 types) | 15.7% (480) | 18.5% (392) | +2.8pp | PRESERVED |
| Type-specific (1 type) | 80.8% (2,474) | 75.4% (1,597) | -5.4pp | PRESERVED |

**Verdict:** VALIDATED - Hierarchical structure fully preserved

The three-layer MIDDLE hierarchy remains intact with clean data. F-BRU-005 is confirmed.

---

### Test 4: Blind Predictions (F-BRU-001)

**Question:** Do the 8/8 blind predictions still hold?

| Recipe | OLD | NEW | Status |
|--------|-----|-----|--------|
| Lavender Water (WATER_GENTLE) | 3/3 | 1/3 | WEAKENED |
| Sage Water (WATER_STANDARD) | 2/2 | 2/2 | PRESERVED |
| Juniper Oil (OIL_RESIN) | 3/3 | 3/3 | PRESERVED |
| **Total** | **8/8** | **6/8** | **PARTIAL** |

**Verdict:** PARTIAL VALIDATION - Above 6/8 threshold, directions correct, magnitudes off

Calibration needed for precise predictions but framework remains valid.

---

## Fit Status Updates

| Fit | Original Status | Updated Status | Notes |
|-----|-----------------|----------------|-------|
| F-BRU-001 | SUCCESS (8/8) | PARTIAL (6/8) | Calibration needed |
| F-BRU-003 | NEGATIVE | UNCHANGED | Synthetic data, no transcript |
| F-BRU-004 | SUCCESS | NEEDS RE-TEST | Stability under clean data |
| F-BRU-005 | SUCCESS | CONFIRMED | Hierarchy preserved |

---

---

## Track 4: PCC Integration Tests

### Test 4.1: Product Type x Closure Pattern

**Question:** Do product types show different closure morphology?

| Product | y-closure | m-closure | other |
|---------|-----------|-----------|-------|
| WATER_GENTLE | **54.5%** | 36.4% | 0.0% |
| PRECISION | **46.2%** | 3.8% | 42.3% |
| WATER_STANDARD | 33.3% | 10.4% | 22.9% |
| OIL_RESIN | **24.0%** | 12.0% | 32.0% |

**Chi-square:** p = 0.0226 → **SIGNIFICANT**

**Finding:** Product types have different closure patterns:
- WATER_GENTLE and PRECISION show high y-closure (54.5%, 46.2%)
- OIL_RESIN shows low y-closure (24.0%)
- Difference of +22% between PRECISION and OIL_RESIN

**Interpretation:** Products requiring precise monitoring (gentle waters, precision distillates) may use more y-closure markers.

---

### Test 4.2: Product Type x Breadth

**Question:** Do product types align with hub-dominant vs tail-dominant?

| Product | Hub Ratio | Tail Ratio |
|---------|-----------|------------|
| OIL_RESIN | 76.5% | 7.9% |
| PRECISION | 73.2% | 9.7% |
| WATER_GENTLE | 71.6% | 9.0% |
| WATER_STANDARD | 71.3% | 11.1% |

**ANOVA:** p = 0.5458 → **NOT SIGNIFICANT**

**Finding:** All product types are hub-dominant (~71-77%). No significant difference in tail ratios.

---

### Test 4.3: Product Type x Cluster Membership

**Question:** Do product types cluster spatially?

- Found 3 clusters (Jaccard >= 0.10)
- Homogeneous: 1/3 (33.3%)
- Expected under random: 30.8%

**Binomial test:** p = 0.6685 → **NOT SIGNIFICANT**

**Finding:** Clusters are not product-homogeneous. Product types interleave spatially.

---

### Track 4 Summary

| Test | Result | p-value | Finding |
|------|--------|---------|---------|
| Closure Pattern | **SIGNIFICANT** | 0.0226 | Product types differ in y-closure |
| Breadth | NOT SIGNIFICANT | 0.5458 | All types hub-dominant |
| Cluster Membership | NOT SIGNIFICANT | 0.6685 | Types interleave spatially |

**Verdict:** WEAK correlation (1/3 significant)

**New Fit Candidate:** F-BRU-006 (Product Type x Closure Pattern) - products requiring monitoring show higher y-closure rates.

---

## Key Implications

### What Changes

1. **Product type discrimination is weaker** - 0.064 < 0.10 threshold
2. **Blind prediction precision decreased** - 6/8 not 8/8
3. **Absolute MIDDLE counts decreased** - ~33% drop

### What Remains Valid

1. **Product types still exist** - 71.8% exclusive MIDDLEs
2. **MIDDLE hierarchy preserved** - Three-layer structure intact
3. **Backward propagation framework** - Still structurally valid
4. **Directional predictions** - Still work, less precise

### Recommended Actions

1. **Update F-BRU-001** to PARTIAL status in fits_brunschwig.md
2. **Revise product type claims** to use 0.064 difference not 0.105
3. **Use 71.8% not 78.2%** for product-exclusive MIDDLE percentage
4. **Note calibration needed** for any predictive use of product profiles

---

## Comparison Metrics (Full)

See `comparison_metrics.json` for complete old vs new comparison data.

---

## Files Modified

| File | Change |
|------|--------|
| `phases/BRUNSCHWIG_TEMPLATE_FIT/exclusive_middle_backprop.py` | Added H-only filter |
| `phases/BRUNSCHWIG_TEMPLATE_FIT/product_a_correlation.py` | Added H-only filter |
| `phases/BRUNSCHWIG_TEMPLATE_FIT/a_record_product_profiles.py` | Added H-only filter |
| `phases/BRUNSCHWIG_TEMPLATE_FIT/precision_prefix_analysis.py` | Added H-only filter |
| `phases/BRUNSCHWIG_BACKPROP_VALIDATION/recipe_to_register_test.py` | Added H-only filter |
| `phases/BRUNSCHWIG_BACKPROP_VALIDATION/cross_type_middle_analysis.py` | Added H-only filter |
| `phases/BRUNSCHWIG_BACKPROP_VALIDATION/middle_property_analysis.py` | Added H-only filter |
| `phases/BRUNSCHWIG_BACKPROP_VALIDATION/cluster_property_correlation.py` | Added H-only filter |
| `phases/BRUNSCHWIG_BACKPROP_VALIDATION/stability_perturbation_test.py` | Added H-only filter |
| `results/exclusive_middle_backprop.json` | Regenerated with H-only |
| `results/cross_type_middle_analysis.json` | Regenerated with H-only |
| `results/blind_prediction_results.json` | Regenerated with H-only |

---

## Conclusion

The Brunschwig backward propagation work **survives data hygiene audit** with the following caveats:

1. **Product type discrimination is weaker** than originally claimed
2. **Precise predictive use** requires recalibration
3. **Structural findings** (hierarchy, exclusivity patterns) are preserved
4. **Framework validity** confirmed but claims should use revised values

**Verdict: PARTIAL VALIDATION**

The core insight - that product types exist and show structural signatures in Currier A - remains valid. The overstated magnitude claims have been corrected.

---

*BRU-AUDIT complete. 2026-01-16*
