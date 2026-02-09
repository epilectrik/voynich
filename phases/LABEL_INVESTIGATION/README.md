# LABEL_INVESTIGATION Phase

**Phase ID:** LABEL_INVESTIGATION
**Status:** COMPLETE
**Started:** 2026-02-05
**Completed:** 2026-02-05

---

## Purpose

Validate and extend findings about label extension patterns (C923) and investigate HT behavior in label contexts.

---

## Key Findings

### 1. Extension Bifurcation (Test 1)

**C923 Partial Validation** - The pattern is more specific than originally claimed:

| Extension | Label % | Text % | Enrichment | p-value |
|-----------|---------|--------|------------|---------|
| **r** | 17.2% | 3.6% | **4.9x** | <0.0001 |
| **h** | 0.0% | 10.4% | **0.0x** | 0.0002 |
| **a** | 13.8% | 6.1% | 2.3x | 0.0121 |
| o | 14.9% | 17.6% | 0.9x | 0.66 |
| d | 9.2% | 9.5% | 1.0x | 1.0 |

**Strong findings:**
- **r-extension**: 4.9x enriched in labels (p<0.0001) - STRONG
- **h-extension**: Categorically absent from labels (p=0.0002) - STRONG
- **a-extension**: 2.3x enriched (p=0.012) - MODERATE

**Not confirmed:**
- o, d, and k do not clearly differentiate labels from text
- t marginal (0.2x but p=0.12)

**Statistical summary:**
- Chi-square: 11.62, p=0.00065
- Cramér's V: 0.136 (small effect)
- Sample: 87 label extensions, 1013 text extensions

### 2. HT Elevated in Labels (Test 2)

**UNEXPECTED FINDING** - HT is *enriched* in labels, not suppressed:

| Region | HT Density |
|--------|------------|
| Labels | 45.0% |
| Paragraphs | 18.6% |
| **Ratio** | **2.42x enriched** |

- Chi-square: 107.33, p<0.0001
- **INCONSISTENT with C926 prediction**

C926 predicts HT suppressed in RI-rich contexts (0.48x). Labels are RI-rich (C914: 3.7x). But HT is 2.42x *elevated* in labels.

**Interpretation:** Labels use HT-derived vocabulary to identify illustrated items. The "spare capacity" model (HT in idle periods) may not apply to annotation contexts.

### 3. Cross-Folio Consistency (Test 3)

| Pattern | Consistency |
|---------|-------------|
| h-absence (0%) | **11/11 folios (100%)** |
| r-enrichment (>10%) | 7/11 folios (64%) |

**h-absence is universal** - Not a single h-extension appears in any label across all 11 folios. This is the most robust finding.

---

## Constraint Updates

### C923 Revision Recommended

Original claim: "Extensions bifurcate into identification (r,a,o,k) vs operational (h,d,t)"

Revised claim: **"r and h extensions mark the label/text boundary"**
- r-extension: 4.9x enriched in labels
- h-extension: Categorically absent from labels (100% consistency)
- a-extension: Moderately enriched (2.3x)
- o, d, k, t: Do not clearly bifurcate

**Tier:** Can be promoted to Tier 2 for r/h bifurcation specifically.

### New Finding: HT Elevated in Labels (C927)

HT tokens are 2.42x enriched in label regions vs paragraph text (chi2=107.33, p<0.0001). This is INCONSISTENT with C926's prediction of HT suppression in RI-rich contexts.

**Interpretation:** Labels use HT-derived vocabulary for identification, not as "spare capacity" practice. The HT-RI anti-correlation (C926) does not extend to label contexts.

---

## Files

| File | Description |
|------|-------------|
| `scripts/t1_extension_validation.py` | Full sample extension test |
| `scripts/t2_label_ht_patterns.py` | HT-label interaction test |
| `scripts/t3_crossfolio_consistency.py` | Cross-folio robustness |
| `results/extension_validation.json` | Test 1 results |
| `results/label_ht_patterns.json` | Test 2 results |
| `results/crossfolio_consistency.json` | Test 3 results |

---

## Verdict

**MIXED** - Core extension patterns confirmed with refinement:

1. **r/h bifurcation CONFIRMED** (Tier 2 worthy)
   - r: 4.9x enriched in labels
   - h: 0% in labels (100% consistent across folios)

2. **Broader ID/OP grouping NOT CONFIRMED**
   - o, d do not differentiate
   - Original C923 groupings too broad

3. **HT-label interaction UNEXPECTED**
   - HT elevated in labels (2.42x)
   - C926 does not extend to label contexts
   - Labels may represent different cognitive task

---

## Implications

1. **Labels identify via r-extension**: The r-extension marks instance identification vocabulary used in labels.

2. **h-extension is operational-only**: h never appears in labels, confirming its role in procedural/monitoring contexts.

3. **HT in labels needs reframing**: Labels aren't "spare capacity" - they're a distinct annotation layer that uses HT-style vocabulary for identification purposes.

4. **C926 has a scope limit**: The HT-RI anti-correlation applies to lines within text, not to the label/text distinction.

---

## Extended Investigation: Label-to-B Pipeline

### Test 4: Label PP Base Connection to B

**97.9% of labels connect to B vocabulary through PP bases.**

| Classification | Count | Description |
|----------------|-------|-------------|
| PP labels | 135 | MIDDLE appears directly in B |
| RI labels | 53 | MIDDLE derived from PP via extension |
| No match | 4 | Label-only vocabulary |

### Test 5: B Role Distribution (C928)

**Jar labels show significant AX_FINAL concentration:**

| Metric | Jar PP Bases | B Baseline | Significance |
|--------|--------------|------------|--------------|
| AX_FINAL rate | 35.1% | 16.7% | **2.1x enriched** |
| Chi-square | 30.15 | - | p = 4.0e-08 |

Overall label AX enrichment is marginal (1.03x), but **jar-specific AX_FINAL** is highly significant.

**Interpretation:** Jar labels identify materials that B deploys at maximum scaffold depth (AX_FINAL = boundary/completion position). This validates C571: PREFIX selects role, MIDDLE carries material.

### New Constraint: C928

**Jar Label AX_FINAL Concentration** - Jar PP bases appear in B at 2.1x AX_FINAL enrichment. Tier 2 (chi2=30.15, p=4e-08).

---

## Final Files

| File | Description |
|------|-------------|
| `scripts/label_to_b_pipeline.py` | Trace label->PP->B connections |
| `scripts/label_b_role_analysis.py` | Role distribution analysis |
| `scripts/label_b_role_stats.py` | Statistical validation |
| `results/label_b_pipeline.json` | Pipeline connections |
| `results/label_b_role_analysis.json` | Role analysis |
| `results/label_b_role_stats.json` | Statistical results |

---

## Summary: The Complete Label Architecture

```
ILLUSTRATION
     |
     v
LABEL (RI/HT vocabulary)
  - r-extension: identification (4.9x)
  - h-extension: absent (operational only)
  - HT elevated (2.42x) for identification
     |
     v
PP BASE (shared with B)
  - 97.9% of labels connect to B
     |
     v
B PROCEDURE
  - Jar PP bases -> AX_FINAL (2.1x) = material specification
  - Content PP bases -> moderate AX enrichment
```

Labels are functional reference markers connecting illustrations to B procedures through shared vocabulary, with jar labels specifically identifying materials at the maximum scaffold depth where "what to process" is specified.
