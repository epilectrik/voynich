# AZC Interface Validation Report

**Date:** 2026-01-19
**Phase:** AZC_INTERFACE_VALIDATION
**Status:** COMPLETE

---

## Executive Summary

This validation phase tested whether AZC visual heterogeneity (scatter diagrams, rings, nymph pages) represents **interface variation** or **mechanism variation**.

**Conclusion:** AZC visual variation is primarily **interface-level** - the same legality basis is rendered through multiple visual idioms. The core A→AZC→B architecture remains intact.

---

## Test Results

### TEST 0: Transcript Hygiene Check (PRE-REQUISITE)

| Metric | Result |
|--------|--------|
| AZC folios | 29 |
| AZC tokens | 3,299 (exact match) |
| P-text tokens | 398 (12.1%) |
| P-text cosine to A | 0.988 |

**Status:** PASS - Data quality confirmed

---

### TEST 1: P-Text Reclassification (CRITICAL)

**Question:** Does P-text (paragraph text above diagrams) behave as Currier A or as AZC?

| Metric | P-text to A | P-text to AZC | Winner |
|--------|------------|---------------|--------|
| PREFIX cosine | 0.946 | 0.777 | **A-like** |
| Exclusive vocab | 57 types | 10 types | **A-like** (5.7x) |
| Jaccard | 0.050 | 0.078 | AZC-like |
| MIDDLE cosine | 0.839 | 0.924 | AZC-like |

**Classification:** A-ON-AZC-FOLIO

**Action:** Reclassify P-text as Currier A; update C300/C301 counts

**Implication:** The 398 P-text tokens are linguistically Currier A material that happens to appear on AZC folios. They should be excluded from AZC legality calculations.

---

### TEST 2: Diagram-Type Stratification (HIGH)

**Question:** Do different diagram types (scatter, ring, segmented, nymph) differ functionally?

| Diagram Type | Folios | Tokens | Uniformity to Pooled |
|--------------|--------|--------|---------------------|
| STANDARD_RING | 12 | 1,109 | 0.9670 (UNIFORM) |
| SCATTER | 2 | 81 | 0.8795 (MARGINAL) |
| SEGMENTED | 3 | 381 | 0.9179 (UNIFORM) |
| NYMPH | 12 | 1,330 | 0.9710 (UNIFORM) |

**Verdict:** UNIFORM

**Interpretation:** Visual diagram variation is INTERFACE only - same functional signature across all types.

**Constraint confirmed:** C137 (illustration independence) - visual layout does not encode linguistic content.

---

### TEST 3: Center Token Audit (HIGH)

**Question:** Do center tokens participate in legality or function as labels/anchors?

| Criterion | Value | Label-like? |
|-----------|-------|-------------|
| Single-char tokens | 3.2% | No (threshold: >5%) |
| PREFIX sim to ring | 0.9395 | No (threshold: <0.85) |
| Vocab overlap | 30.0% | No (threshold: <30%) |

**Classification:** LEGALITY-PARTICIPATING

**Interpretation:** Center tokens behave like normal ring text, not labels. They should be included in standard legality calculations.

**Note:** This contradicts the prior that center tokens are "labels or anchors." The tokens present in the transcript are linguistically standard; the issue is that many center tokens are MISSING from the transcript.

---

### TEST 4: Nymph-Interrupted vs Continuous Rings (MEDIUM)

**Question:** Does nymph visual interruption (S placement) have functional consequences?

| Comparison | PREFIX Cosine |
|------------|---------------|
| S-interrupted vs Nymph R-continuous | 0.8421 |
| S-interrupted vs Non-nymph continuous | 0.7382 |
| Nymph R-cont vs Non-nymph cont | 0.8529 |

**Verdict:** FUNCTIONAL

**Interpretation:** S-interrupted rings show a distinct PREFIX profile (o-heavy: ok 25%, ot 25%, o 25%). This suggests positional encoding near nymph illustrations.

**Constraint status:** NEW CONSTRAINT NEEDED - nymph-adjacent positions may encode distinct lexical selection.

---

## Consolidated Findings

### Architecture Status

| Component | Status |
|-----------|--------|
| A→AZC→B pipeline | **INTACT** |
| AZC as decision-point grammar | **INTACT** |
| Position constrains legality | **INTACT** |
| REGIME reconstruction | **INTACT** |
| Grammar invariance (C121, C124) | **INTACT** |

### Constraint Updates Needed

| Constraint | Update |
|------------|--------|
| C300, C301 | Subtract 398 P-text tokens from AZC counts |
| NEW | Nymph-adjacent S-positions show o-prefix enrichment |

### Classification Decisions

| Element | Classification |
|---------|---------------|
| P-text | Reclassify as Currier A (not AZC) |
| Diagram types | Interface variation (not mechanism) |
| Center tokens | Legality-participating (not labels) |
| Nymph interruption | Functional (PREFIX-distinct) |

---

## Implications for Prior Work

1. **C481 (survivor-set uniqueness):** Re-validate after P-text exclusion
2. **F-AZC-016 (escape suppression):** Re-validate after P-text exclusion
3. **C437-C444 (AZC compatibility):** Core mechanics CONFIRMED
4. **C430 (Zodiac bifurcation):** CONFIRMED - diagram type doesn't affect

---

## Files Generated

| File | Purpose |
|------|---------|
| `test0_transcript_hygiene.py` | Data quality check |
| `test1_ptext_reclassification.py` | P-text analysis |
| `test2_diagram_stratification.py` | Diagram type comparison |
| `test3_center_token_audit.py` | Center token analysis |
| `test4_nymph_interruption.py` | Nymph interruption test |
| `results/test1_ptext_reclassification.json` | TEST 1 raw results |
| `results/test2_diagram_stratification.json` | TEST 2 raw results |
| `results/test3_center_token_audit.json` | TEST 3 raw results |
| `results/test4_nymph_interruption.json` | TEST 4 raw results |

---

## Conclusion

The AZC_INTERFACE_VALIDATION phase confirms:

> **Visual heterogeneity in AZC folios is an interface-level phenomenon.**
> The underlying legality grammar is consistent across diagram types.

The one exception is nymph-interrupted rings (S placement), which show a distinct PREFIX profile that may encode proximity to nymph illustrations.

**Next steps:**
1. Update AZC token counts (exclude P-text)
2. Propose new constraint for S-position PREFIX enrichment
3. Re-run survivor-set and escape-suppression validation with corrected data
