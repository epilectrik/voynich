# EXT-8: Full Compositional Morphology Analysis

**Phase ID:** EXT-8
**Tier:** 2 (STRUCTURAL INFERENCE)
**Status:** COMPLETE
**Date:** 2026-01-06

---

## Executive Summary

> **The three-axis compositional structure (PREFIX × MIDDLE × SUFFIX) exhibits a highly specific pattern: PREFIX-bound MIDDLE modifiers, UNIVERSAL SUFFIX forms, and STRONG cross-axis dependencies. This pattern is the structural signature of a MATERIAL CLASSIFICATION SYSTEM — incompatible with linguistic encoding, quality grading, or geographic cataloging.**

---

## Part 1: Independent Axis Analysis

### PREFIX (8 values)

| Prefix | Section H | Section P | Section T | Total |
|--------|-----------|-----------|-----------|-------|
| CT     | 85.9%     | 8.6%      | 5.5%      | 1,492 |
| CH     | 75.5%     | 19.5%     | 5.0%      | 7,181 |
| SH     | 74.7%     | 16.6%     | 8.8%      | 3,303 |
| OT     | 72.8%     | 19.5%     | 7.7%      | 1,640 |
| DA     | 71.8%     | 21.8%     | 6.4%      | 3,619 |
| QO     | 69.2%     | 25.1%     | 5.7%      | 3,449 |
| OK     | 55.5%     | 35.4%     | 9.1%      | 1,905 |
| OL     | 52.9%     | 38.7%     | 8.4%      | 853   |

**Specialization variance:** 102.6 (SPECIALIZED)
**Range:** 53% - 86%

### MIDDLE (1,155 unique values)

| Middle | Section H | Section P | Section T | Total | Notes |
|--------|-----------|-----------|-----------|-------|-------|
| -iin   | 77.7%     | 19.1%     | 3.2%      | 1,778 | DA exclusive |
| -k     | 53.5%     | 39.6%     | 6.9%      | 1,015 | QO dominant |
| -o     | 83.9%     | 10.7%     | 5.5%      | 935   | Universal |
| -h     | 82.6%     | 12.7%     | 4.7%      | 740   | **CT exclusive** |
| -t     | 87.8%     | 10.2%     | 2.0%      | 597   | QO dominant |
| -e     | 60.0%     | 29.9%     | 10.2%     | 472   | Universal |

**Specialization variance:** 131.3 (SPECIALIZED)
**Range:** 51% - 89%

### SUFFIX (27 unique values)

| Suffix | Section H | Section P | Section T | Total |
|--------|-----------|-----------|-----------|-------|
| -ol    | 78.1%     | 17.4%     | 4.6%      | 2,345 |
| -y     | 75.9%     | 15.0%     | 9.1%      | 1,617 |
| -or    | 83.4%     | 12.9%     | 3.7%      | 1,493 |
| -ey    | 63.0%     | 28.5%     | 8.4%      | 1,220 |
| -hy    | 82.0%     | 13.5%     | 4.5%      | 1,021 |
| -chy   | 93.8%     | 3.9%      | 2.3%      | 870   |
| -eol   | 36.6%     | **59.7%** | 3.7%      | 694   | **Section P dominant** |

**Specialization variance:** 160.5 (SPECIALIZED)
**Note:** One suffix (-eol) is Section P dominant — the only axis value favoring P.

---

## Part 2: Pairwise Interactions

### PREFIX × MIDDLE

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Chi-square | 25,303.36 | |
| p-value | **< 10⁻³⁰⁰** | Effectively zero |
| Cramer's V | **0.674** | **STRONG** |

**Critical finding:** MIDDLE is **STRONGLY PREFIX-BOUND**

| Category | Count | Examples |
|----------|-------|----------|
| **EXCLUSIVE middles** (1 prefix only) | 28 | -h (CT), -in (DA), -m (DA), -ir (DA), -kcho (QO) |
| **UNIVERSAL middles** (6+ prefixes) | 10 | -o, -e, -ch, -ol, -s, -ain |
| **SHARED middles** (2-5 prefixes) | 100 | |

**Interpretation:** Different PREFIX families have different available MIDDLE modifiers. This is inconsistent with MIDDLE being a universal property (like quality grade) and consistent with MIDDLE being a TYPE-SPECIFIC refinement (like botanical variety within a plant family).

### PREFIX × SUFFIX

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Chi-square | 2,955.39 | |
| p-value | **< 10⁻³⁰⁰** | Effectively zero |
| Cramer's V | **0.183** | **MODERATE** |

**Critical finding:** SUFFIX is **LARGELY UNIVERSAL**

| Category | Count |
|----------|-------|
| **UNIVERSAL suffixes** (6+ prefixes) | 22 |
| **PARTIAL suffixes** (<6 prefixes) | 3 |

**Prefix-specific suffix preferences:**

| Prefix | Most Over-represented Suffix | Ratio |
|--------|------------------------------|-------|
| CT     | -hy                          | **4.56x** |
| DA     | -y                           | 2.69x |
| QO     | -chy                         | 2.43x |
| OT     | -al                          | 2.28x |
| OK     | -al                          | 2.15x |
| OL     | -aiin                        | 1.93x |
| CH     | -or                          | 1.33x |
| SH     | -ey                          | 1.30x |

**Interpretation:** While suffixes are available to all prefixes, different prefixes PREFER different suffixes. This is consistent with different material types having different typical output forms.

### MIDDLE × SUFFIX

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Chi-square | 3,915.46 | |
| p-value | **< 10⁻³⁰⁰** | Effectively zero |
| Cramer's V | **0.402** | **STRONG** |

**Interpretation:** MIDDLE and SUFFIX are not independent. Certain modifiers prefer certain output forms.

---

## Part 3: Three-Way Patterns

| Metric | Value |
|--------|-------|
| Unique PREFIX × MIDDLE × SUFFIX combinations | **1,329** |
| Unique PREFIX × MIDDLE combinations | 739 |
| Unique PREFIX × SUFFIX combinations | 172 |
| Unique MIDDLE × SUFFIX combinations | 1,004 |

### Top 10 Full Combinations

| PREFIX | MIDDLE | SUFFIX | Count | % of tokens |
|--------|--------|--------|-------|-------------|
| CT     | -h     | -ol    | 188   | 1.9% |
| QO     | -t     | -chy   | 179   | 1.8% |
| CT     | -h     | -or    | 148   | 1.5% |
| QO     | -k     | -chy   | 139   | 1.4% |
| QO     | -k     | -ol    | 137   | 1.4% |
| CT     | -h     | -ey    | 127   | 1.3% |
| QO     | -k     | -eey   | 115   | 1.2% |
| QO     | -k     | -eol   | 97    | 1.0% |
| CH     | -o     | -ky    | 90    | 0.9% |
| CH     | -o     | -ty    | 81    | 0.8% |

**Concentration:**
- Top 10 combinations: 17.2% of tokens
- Top 50 combinations: 39.4% of tokens
- Remaining 1,279 combinations: 60.6% of tokens

**Interpretation:** The system is MODERATELY concentrated — a core vocabulary with a long tail of variants. This is consistent with a workshop register where some materials are common and many are rare.

---

## Part 4: Taxonomy Model

### Axis Roles (Structurally Derived)

| Axis | Count | Section Variance | Binding | Structural Role |
|------|-------|------------------|---------|-----------------|
| PREFIX | 8 | 102.6 | — | **PRIMARY CLASSIFIER** |
| MIDDLE | 1,155 | 131.3 | **PREFIX-BOUND** (28 exclusive) | **TYPE-SPECIFIC MODIFIER** |
| SUFFIX | 27 | 160.5 | **UNIVERSAL** (22 of 25 significant) | **UNIVERSAL OUTPUT FORM** |

### The Structural Signature

```
IDENTIFIER = PREFIX + [MIDDLE] + SUFFIX

Where:
  - PREFIX defines the FAMILY (8 options)
  - MIDDLE refines within family (some family-specific, some universal)
  - SUFFIX defines OUTPUT FORM (universal across all families)
```

This pattern has a **specific real-world signature**:

**COMPATIBLE taxonomy types:**

| Type | PREFIX = | MIDDLE = | SUFFIX = |
|------|----------|----------|----------|
| **Botanical Register** | Plant family | Variety/preparation | Product form |
| **Aromatic Inventory** | Material source | Quality/origin | Output form |
| **Pharmacognosy Codex** | Therapeutic class | Specific material | Dosage form |

**INCOMPATIBLE taxonomy types:**

| Type | Why Excluded |
|------|--------------|
| Quality grading system | MIDDLE would be universal, not prefix-bound |
| Geographic catalog | SUFFIX would be exclusive, not universal |
| Processing state system | PREFIX would be universal, not section-specialized |
| Linguistic encoding | No compositional semantics would show this pattern |
| Simple enumeration | No structure at all |

---

## New Constraints

### Constraint 276: MIDDLE is PREFIX-BOUND
28 MIDDLE values are EXCLUSIVE to single prefixes (Cramer's V = 0.674, p ≈ 0). MIDDLE is not a universal modifier but a TYPE-SPECIFIC refinement.

### Constraint 277: SUFFIX is UNIVERSAL
22 of 25 significant SUFFIX values appear in 6+ PREFIX classes. SUFFIX represents a UNIVERSAL OUTPUT FORM applicable to all material types.

### Constraint 278: Three-Axis Hierarchy
The compositional structure follows: PREFIX (family) → MIDDLE (type-specific refinement) → SUFFIX (universal form). This is the signature of a MATERIAL CLASSIFICATION SYSTEM.

### Constraint 279: Strong Cross-Axis Dependencies
All three pairwise interactions are statistically significant (p < 10⁻³⁰⁰). The axes are NOT independent dimensions but HIERARCHICALLY RELATED.

### Constraint 280: Section P Anomaly
Suffix -eol is 59.7% Section P (the only axis value favoring P). This suggests Section P involves a specific OUTPUT FORM not common elsewhere.

### Constraint 281: Components SHARED
All 8 prefixes and all 27 suffixes appear in BOTH Currier A and B. Only 9 middles are A-exclusive (mostly CT-family patterns like -ho, -hod, -hom). The systems share the SAME ALPHABET but use DIFFERENT GRAMMAR.

### Constraint 282: Component ENRICHMENT
Usage patterns differ dramatically between A and B:
- CT is A-enriched (0.14x ratio — 7x more frequent in A)
- OL/QO are B-enriched (5x/4x ratios)
- -dy suffix is 27x B-enriched
- -or suffix is A-enriched (0.45x ratio)

---

## Part 5: Component Exclusivity

### Token-Level Overlap
| Metric | Value |
|--------|-------|
| Marker tokens in A | 2,425 types |
| Shared with B | 819 types (33.8%) |

### PREFIX Distribution

| Prefix | In A | In B | Ratio | Status |
|--------|------|------|-------|--------|
| CT | 1,492 | 214 | 0.14x | **A-ENRICHED** |
| DA | 3,619 | 3,583 | 0.99x | BALANCED |
| CH | 7,181 | 10,784 | 1.50x | SHARED |
| SH | 3,303 | 6,805 | 2.06x | B-ENRICHED |
| OK | 1,905 | 4,807 | 2.52x | B-ENRICHED |
| OT | 1,640 | 4,565 | 2.78x | B-ENRICHED |
| QO | 3,449 | 13,483 | 3.91x | **B-ENRICHED** |
| OL | 853 | 4,279 | 5.02x | **B-ENRICHED** |

### A-Exclusive Middles (freq >= 10)
Only 9 middles are exclusive to A, almost all CT-family:
- `-ho` (66x), `-hod` (33x), `-hom` (29x), `-hol` (16x), `-hor` (12x)

### Interpretation

**SHARED INFRASTRUCTURE**: The compositional components are the same "alphabet" used throughout the manuscript, but with different "grammars":
- In A: compositional codes for identification
- In B: sequential tokens within operational grammar

This strongly supports the **co-design hypothesis** — A and B are complementary systems using shared notation.

---

## Verdict

**MATERIAL_CLASSIFICATION_SIGNATURE**

The three-axis compositional structure exhibits the precise pattern expected of a **workshop material register**:

1. **8 material families** (PREFIX) with different section affinities
2. **Type-specific varieties** (MIDDLE) bound to families + some universal modifiers
3. **Universal output forms** (SUFFIX) applicable to all materials

This is **structurally incompatible** with:
- Linguistic encoding
- Quality grading
- Geographic cataloging
- Abstract enumeration

And **structurally compatible** with:
- Botanical material register
- Aromatic inventory
- Pharmacognosy codex

---

## Files Generated

- `ext8_prefix_taxonomy_tests.py` — Initial prefix tests
- `ext8_full_morphology_analysis.py` — Complete three-axis analysis
- `ext8_results.json` — Initial results
- `ext8_full_results.json` — Complete results
- `EXT8_REPORT.md` — This report

---

## Phase Tag

```
Phase: EXT-8
Tier: 2 (STRUCTURAL INFERENCE)
Subject: Full Compositional Morphology Analysis
Type: Taxonomy compatibility testing
Status: COMPLETE
Verdict: MATERIAL_CLASSIFICATION_SIGNATURE
  - 8 material families (PREFIX)
  - Type-bound modifiers (MIDDLE)
  - Universal output forms (SUFFIX)
  - SHARED INFRASTRUCTURE with B (same alphabet, different grammar)
Constraints: 273-282
```
