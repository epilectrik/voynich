# CURRIER_A_STRUCTURE_V2 - Findings

## Overall Verdict: MODERATE

**Gaps addressed: 3/5**

---

## Test Results Summary

### Test 1: Position vs Cluster Type ✓ HIGHLY SIGNIFICANT

**Finding:** Paragraph ordinal position within folio DOES predict cluster type.

| Position | Strongest Association | Ratio |
|----------|----------------------|-------|
| ONLY | LINKER_RICH | 2.67x enriched |
| MIDDLE | SHORT_RI_HEAVY | 1.90x enriched |
| LAST | MIDDLE_RI_ONLY | 1.99x enriched |
| ONLY | SHORT_RI_HEAVY | 0.00x depleted |
| ONLY | NO_RI | 0.23x depleted |

**Chi-squared: 102.22 (p < 0.01)**

**Interpretation:** Folios have structural organization - single-paragraph folios tend to have linkers, middle paragraphs tend to be short with high RI density, and last paragraphs tend to have RI only in middle lines.

### Test 2: PP Composition ✓ TWO OPENING TYPES

**Finding:** First lines WITH initial RI have different PP profiles than lines WITHOUT.

- Lines WITH RI: 215
- Lines WITHOUT RI: 127
- **Jaccard similarity: 0.164** (very low overlap)

**Distinctive PREFIX patterns:**
- `ke`, `te`: 3.5-4.8x enriched in WITH-RI lines
- `al`, `ar`, `de`, `lch`, `lk`: Nearly exclusive to WITH-RI lines
- `ct`, `dch`, `tch`, `po`: Depleted in WITH-RI lines

**Interpretation:** There are TWO distinct types of paragraph openings with different vocabularies.

### Test 3: RI Morphology ✗ UNIFORM FUNCTION

**Finding:** RI tokens have SAME morphology regardless of position.

- Initial vs Middle similarity: 0.951
- Initial vs Final similarity: 0.895
- Middle vs Final similarity: 0.962
- **Average similarity: 0.936**

**Position-specific PREFIX patterns (minor):**
- `ot`, `ko`, `sa`, `so`, `to`: INITIAL-preferred
- `ol`: MIDDLE-preferred
- `ar`, `ka`, `tch`, `yk`: FINAL-preferred

**Interpretation:** RI function is uniform. Position-specific patterns exist but don't suggest different functions.

### Test 4: Linker Targets ✓ STRUCTURALLY DISTINCT

**Finding:** Target folios (f93v, f32r) have distinct PREFIX profiles.

- Found 101 linker RI tokens (ct-prefix)
- Target folios have LOWER ch prefix (0.56x)
- Target folios ENRICHED for: dch (3.7x), fch (7.7x), sch (5.6x), te (3.6x)
- Target folios DEPLETED for many prefixes (al, ar, da, de, kch, ke, etc.)

**Interpretation:** Linker target folios ARE structurally distinct from non-targets.

### Test 5: Sequential Coherence ✗ MEASUREMENT ARTIFACTS

**Finding:** Cluster types have SIMILAR coherence patterns.

| Cluster Type | PREFIX Cont | Middle Rep | Cond Entropy | Unique Ratio | N |
|--------------|-------------|------------|--------------|--------------|---|
| LINKER_RICH | 0.171 | 0.144 | 0.223 | 0.900 | 87 |
| MIDDLE_RI_ONLY | 0.212 | 0.161 | 0.216 | 0.895 | 58 |
| NO_RI | 0.181 | 0.199 | 0.153 | 0.925 | 45 |
| SHORT_RI_HEAVY | 0.148 | 0.234 | 0.081 | 0.959 | 56 |
| STANDARD | 0.199 | 0.155 | 0.190 | 0.907 | 82 |

- PREFIX continuity range: 0.064
- Conditional entropy range: 0.142

**Interpretation:** The 5 cluster types do NOT have functionally different coherence patterns. They may be measurement artifacts rather than reflecting distinct record types.

---

## Gaps Addressed

| Gap | Status | Finding |
|-----|--------|---------|
| No initial RI (53%) | ✓ ADDRESSED | Two distinct opening types |
| Paragraph size variance | ✓ ADDRESSED | Position predicts structure |
| Middle-line RI | ✗ NOT ADDRESSED | RI function is uniform |
| 5 cluster types | ✗ NOT ADDRESSED | Similar coherence = artifacts |
| Linker sparsity | ✓ ADDRESSED | Targets structurally distinct |

---

## Potential New Constraints

### C887: Paragraph Position Predicts Cluster Type
**Tier:** 2
**Scope:** A

Paragraph ordinal position within a Currier A folio predicts cluster type membership (chi2=102.22, p<0.01). Single-paragraph folios (ONLY) are 2.67x enriched for LINKER_RICH clusters and 0.00x depleted for SHORT_RI_HEAVY. Middle paragraphs are 1.90x enriched for SHORT_RI_HEAVY. Last paragraphs are 1.99x enriched for MIDDLE_RI_ONLY.

**Source:** CURRIER_A_STRUCTURE_V2

### C888: Two Paragraph Opening Types
**Tier:** 2
**Scope:** A

First lines with initial RI have distinct PP vocabulary from first lines without RI (Jaccard=0.164). Lines with RI are enriched for ke (3.5x), te (4.8x), and nearly exclusive prefixes (al, ar, de, lch, lk). Lines without RI are enriched for ct, dch, tch, po. This indicates two functionally distinct paragraph opening patterns.

**Source:** CURRIER_A_STRUCTURE_V2

---

## Remaining Questions

1. **What determines middle-line RI placement?** RI morphology is uniform regardless of position, so position doesn't encode function. What does?

2. **Are the 5 cluster types real or artifacts?** Sequential coherence is similar across types. The clusters may reflect measurement thresholds rather than functional categories.

3. **What connects position to cluster membership?** Why are single-paragraph folios dominated by linkers? Why do last paragraphs have middle-only RI?

---

## Files Generated

| File | Description |
|------|-------------|
| results/position_cluster_analysis.json | Test 1 full results |
| results/pp_composition_analysis.json | Test 2 full results |
| results/ri_morphology_analysis.json | Test 3 full results |
| results/linker_target_analysis.json | Test 4 full results |
| results/sequential_coherence_analysis.json | Test 5 full results |
| results/synthesis.json | Combined synthesis |
