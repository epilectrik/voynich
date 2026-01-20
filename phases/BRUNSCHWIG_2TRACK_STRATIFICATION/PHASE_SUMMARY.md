# BRUNSCHWIG_2TRACK_STRATIFICATION Phase Summary

**Date:** 2026-01-20
**Status:** COMPLETE

---

## Question

Does the 2-track vocabulary classification (C498) affect F-BRU-005's finding that 75.4% of MIDDLEs are type-specific?

**Hypothesis:** Registry-internal MIDDLEs (56.6%, folio-localized at avg 1.34 folios) might show artificially high type-specificity because they appear in fewer folios and thus naturally span fewer product types.

---

## Results

### Type-Coverage Distribution by Track

| Track | Type-Specific | 2-Type | 3-Type | Universal | n |
|-------|--------------|--------|--------|-----------|---|
| **Registry-internal** | **62.5%** | 17.2% | 3.9% | 16.4% | 128 |
| **Pipeline-participating** | **46.1%** | 16.4% | 14.8% | 22.7% | 128 |

### Statistical Test

- **Chi-square:** 12.64, df=3, **p < 0.01**
- **Cramer's V:** 0.222 (small-medium effect)
- **Result:** SIGNIFICANT - Track and type-coverage are NOT independent

### Key Difference

- Registry-internal: **62.5%** type-specific
- Pipeline-participating: **46.1%** type-specific
- Difference: **+16.4 percentage points**

---

## Interpretation

**CONFIRMED:** The original F-BRU-005 finding (75.4% type-specific) is confounded by the 2-track structure.

1. **Registry-internal MIDDLEs show artificially high type-specificity** because:
   - They are folio-localized (avg 1.34 folios per C498)
   - Fewer folios = fewer opportunities to appear in multiple product types
   - High type-specificity is a byproduct of folio-localization, not functional design

2. **Pipeline-participating MIDDLEs show 46.1% type-specificity**:
   - These are the MIDDLEs that actually flow through A→AZC→B
   - Product-type encoding in operational vocabulary is weaker than aggregate suggests
   - Still substantial but not the dominant pattern

3. **The hierarchical structure remains valid**:
   - Both tracks show universal, cross-cutting, and type-specific layers
   - The *proportions* differ between tracks
   - Type-specific layer is dominated by registry-internal vocabulary

---

## Documentation Updates

| File | Change |
|------|--------|
| `context/MODEL_FITS/fits_brunschwig.md` | Added 2-track stratification section to F-BRU-005 |

---

## Provenance

- **Input:** C498 (Two-Track Vocabulary Structure), F-BRU-005 (MIDDLE Hierarchical Structure)
- **Method:** Cross-tabulation of MIDDLE type-coverage by 2-track classification
- **Script:** `scripts/stratified_product_analysis.py`
- **Results:** `results/stratified_product_analysis.json`

---

## Conclusion

The 2-track classification (C498) has a significant effect on F-BRU-005's type-specificity finding. The aggregate 75.4% rate is confounded by registry-internal vocabulary's folio-localization. The operational vocabulary (pipeline-participating) shows a lower but still substantial 46.1% type-specificity rate.

This REFINES but does not FALSIFY F-BRU-005:
- The hierarchical structure is preserved
- Product-type encoding exists in both tracks
- The *magnitude* differs, favoring registry-internal vocabulary

**Implication:** Registry-internal vocabulary may encode within-category fine distinctions (sub-variety markers) that are naturally type-specific, while pipeline-participating vocabulary encodes broader operational categories that cross product types more freely.

---

## Angle D: Registry-Internal as Reference Entries

### Hypothesis

If registry-internal vocabulary encodes "fine distinctions below execution threshold" (C498), then product types with more reference-only Brunschwig materials (listed but no procedure) should correlate with higher registry-internal vocabulary density.

### Brunschwig Reference Ratios

| Product Type | Processed | Reference | Reference Ratio |
|--------------|-----------|-----------|-----------------|
| OIL_RESIN | 7 | 28 | **80.0%** |
| WATER_GENTLE | 14 | 34 | **70.8%** |
| WATER_STANDARD | 169 | 248 | 59.5% |
| PRECISION | 7 | 2 | 22.2% |

### Folio-Level Test (n=110)

| Group | Product Types | n Folios | Mean Reg-Int Ratio |
|-------|---------------|----------|-------------------|
| HIGH-REFERENCE | OIL_RESIN, WATER_GENTLE | 36 | **35.6%** |
| LOW-REFERENCE | WATER_STANDARD, PRECISION | 74 | **30.3%** |

**Mann-Whitney U:** z = -2.602, **p = 0.01**, effect size r = 0.248

### Result

**SUPPORTED:** Folios in product types with more reference-only Brunschwig materials have significantly higher registry-internal vocabulary density.

### Interpretation

This validates C498's interpretation: registry-internal vocabulary encodes "fine distinctions below execution granularity threshold" - paralleling Brunschwig's reference materials (information recorded but not executed).

The correlation suggests a functional parallel:
- **Brunschwig reference materials**: Listed for completeness but no procedure documented
- **Voynich registry-internal vocabulary**: Recorded for completeness but doesn't participate in A→AZC→B execution

---

## Scripts

| Script | Purpose |
|--------|---------|
| `stratified_product_analysis.py` | Type-coverage stratification by 2-track |
| `reference_material_correlation.py` | Product-type level correlation (n=4, underpowered) |
| `reference_material_folio_level.py` | Folio-level Mann-Whitney test (n=110, significant) |

---

## Expert Validation

**Internal expert-advisor:** Validated consistency with C476, C478, C475, C171/C384, C498. No Tier 0-2 violations. Governance assessment correct.

**External expert assessment:**
- F-BRU-005 is REFINED, not falsified
- Test 2 provides "the strongest form of external validation without violating the semantic ceiling"
- C498 externally corroborated by orthogonal historical signal
- Model-strengthening refinement, not scope creep

**Locked-in summary sentence:**

> Separating Currier A into pipeline-participating and registry-internal vocabulary reveals that much of the apparent product-type specificity arises from coverage-driven folio localization; genuine operational alignment exists only in the pipeline vocabulary and is necessarily weaker, overlapping, and regime-mediated—exactly as required by an expert-only, non-semantic control system.

---

## Status

**COMPLETE** - Phase moved to consolidation/documentation mode.

Brunschwig is now **fully bounded**:
- He corroborates structure
- He does not decode tokens
- He validates architecture, not content
