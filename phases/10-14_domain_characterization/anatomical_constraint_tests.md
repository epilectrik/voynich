# Anatomical Constraint Tests

*Generated: 2026-01-01*
*Updated: 2026-01-01 (v2 with visual data)*
*Status: WEAK SUPPORT - Structural signal exists, material-selection interpretation unproven*

---

## Test Overview

This document reports the results of 5 pre-registered tests for the hypothesis:

> **H:** Prefix and/or suffix morphology encodes a small, reusable set of plant-part usage constraints, invisible to execution logic.

---

## Summary Table

| Test | Name | Verdict | Notes |
|------|------|---------|-------|
| TEST 1 | Prefix/Suffix Archetype Discovery | **PASS** | 5 stable archetypes (silhouette 0.463) |
| TEST 2 | Family-Invariance Check | **FAIL** | 40% recurrence (threshold 50%) |
| TEST 3 | Plant Feature Absence Test | **PASS** | Root prominence significant (p=0.0002, survives Bonferroni) |
| TEST 4 | Era-Compatibility Filter | **PASS** | 5 archetypes, no anachronistic patterns |
| TEST 5 | Adversarial Null Tests | **PASS** | 3/3 nulls survived (including visual) |

**Final Outcome:** 4 PASS, 1 FAIL

---

## TEST 1: Prefix/Suffix Archetype Discovery

**Goal:** Determine if prefix/suffix morphology collapses into a small number of reusable archetypes.

**Result:** PASS

**Findings:**
- 5 stable archetypes discovered (k=5 optimal by silhouette)
- Silhouette score: 0.463 (well above 0.2 threshold)
- Archetypes are distinguishable by hub association, slot position, and entry-initial rate
- Count is within era-appropriate range (4-7)

**Interpretation:** Prefix morphology exhibits non-random clustering structure. This is a necessary (but not sufficient) condition for material-selection encoding.

---

## TEST 2: Family-Invariance Check

**Goal:** Verify that prefix archetypes recur across multiple recipe families and do NOT define families.

**Result:** FAIL

**Findings:**
- Archetype recurrence across families: 40% (below 50% threshold)
- Only archetypes 0 and 2 appear in all 8 families
- Archetypes 1, 3, 4 do NOT appear in any family-assigned folios
- Archetype variance across families: 0.0002 (very low - independence confirmed)

**Interpretation:** While archetypes show low family-dependence (variance 0.0002), they fail the recurrence test. Only 2/5 archetypes are reusable across families. This suggests archetypes may be section-specific rather than universally reusable.

**Why this matters:** If prefixes encode plant-part constraints, they should appear across all recipe families (since any recipe could use any plant part). The failure suggests either:
1. Archetypes are NOT material-selection markers
2. Certain archetypes are restricted to specific manuscript sections (not available in the 83 B-text folios tested)

---

## TEST 3: Plant Feature Absence Test (CRITICAL)

**Goal:** Test whether prefix archetypes AVOID folios whose plant illustrations lack specific anatomical features.

**Result:** PASS

**Visual Data Used:** `blinded_visual_coding.json` (30 folios with complete visual annotation)

**Visual Features Tested:**
- Root prominence (HIGH/MEDIUM vs LOW)
- Flower presence (present vs absent)
- Root type (BULBOUS vs BRANCHING)

### TEST 3A: Archetype x Root Prominence

| Group | Archetype 0 | Archetype 2 | Total Tokens |
|-------|-------------|-------------|--------------|
| HIGH/MEDIUM root | 834 (95.5%) | 39 (4.5%) | 873 |
| LOW root | 187 (88.6%) | 24 (11.4%) | 211 |

**Chi-square:** X2=13.57, p=0.0002 **SIGNIFICANT**

**Key finding:** Archetype 2 (entry-initial position markers) is 2.5x more common in LOW root prominence folios (11.4%) than HIGH root folios (4.5%).

### TEST 3B: Archetype x Flower Presence

| Group | Archetype 0 | Archetype 2 | Total Tokens |
|-------|-------------|-------------|--------------|
| With flowers | 965 (94.4%) | 57 (5.6%) | 1,022 |
| Without flowers | 99 (93.4%) | 7 (6.6%) | 106 |

**Chi-square:** X2=0.05, p=0.8303 (not significant)

### TEST 3C: Archetype x Root Type

| Group | Archetype 0 | Archetype 2 | Total Tokens |
|-------|-------------|-------------|--------------|
| BULBOUS root | 137 (94.5%) | 8 (5.5%) | 145 |
| BRANCHING root | 732 (94.6%) | 42 (5.4%) | 774 |

**Chi-square:** X2=0.00, p=1.0000 (not significant)

### Bonferroni Correction

- Corrected alpha: 0.0167 (0.05/3)
- Root prominence: p=0.0002 < 0.0167 **SURVIVES CORRECTION**
- Significant associations after correction: 1/3

### Adversarial Null (Visual Shuffle)

- Shuffled visual features across 1000 permutations
- Real p-value percentile: 0.2%
- **Signal SURVIVES null** (real is better than 95% of shuffled)

**Interpretation:** A significant association exists between prefix archetype and root prominence in plant illustrations. The direction (more position markers when roots are less prominent) suggests prefixes may encode structural/organizational information that correlates with visual complexity, rather than direct plant-part selection.

---

## TEST 4: Era-Compatibility Filter

**Goal:** Test whether discovered constraints align with 15th-century plant anatomy concepts.

**Result:** PASS

**Findings:**
- Archetype count (5) is within medieval range (4-7 major plant-part categories)
- No anachronistic patterns detected (no modern botanical concepts required)
- Archetype features (hub association, slot position) could correspond to:
  - Material type (which hub category)
  - Processing stage (which slot in recipe)
  - Recipe section (entry-initial vs internal)

**Medieval anatomy categories considered:**
1. Radix (roots, rhizomes, bulbs)
2. Herba/Herba tota (aerial parts)
3. Folium (leaves)
4. Flos (flowers)
5. Fructus/Semen (fruits, seeds)
6. Cortex/Lignum (bark, wood)
7. Succus/Gummi/Resina (saps, gums, resins)

5 archetypes could plausibly map to a subset of these categories, though we cannot prove this.

---

## TEST 5: Adversarial Null Tests

**Goal:** Verify that discovered patterns collapse under randomization.

**Result:** PASS (3/3 nulls survived)

### Null 1: Shuffled Prefix-Archetype Assignments
- Real archetype variance: 0.0053
- Null mean variance: 0.0009 (±0.0006)
- Z-score: 7.07
- Percentile: 100%
- **Result:** PASS - Real archetypes have significantly higher internal coherence than random assignments

### Null 2: Shuffled Visual Features (v2)
- Real p-value: 0.0002
- Null median p-value: 0.4839
- Real p-value percentile: 0.2%
- **Result:** PASS - Visual association survives permutation testing

### Null 3: Synthetic Random Prefix System
- Real best silhouette: 0.463
- Synthetic best silhouette: 0.265
- **Result:** PASS - Real prefixes cluster much better than random synthetic prefixes

---

## Why Prior Correlation Tests Failed

The current analysis helps explain why earlier visual-text correlation tests (Phase D, Phase E) failed to find significant patterns:

1. **Missing layer identification:** Prior tests assumed direct token-to-visual correlation. This test proposes prefix/suffix as a separate annotation layer.

2. **Weak proxy problem:** Without actual visual annotations, any test using section codes as proxy will have low power.

3. **Structural vs semantic:** The archetypes are structurally real (TEST 1, 5 passed) but may encode grammatical function (position, hub association) rather than material selection.

4. **Family restriction:** Archetypes 1, 3, 4 are absent from B-text family-assigned folios, suggesting they may be A-text (definitional) specific.

---

## Final Verdict

**HYPOTHESIS STATUS: WEAK SUPPORT**

The hypothesis that prefix/suffix morphology encodes plant-part usage constraints receives limited support from the data.

**Evidence FOR:**
- 5 stable, era-appropriate archetypes exist (TEST 1 PASS)
- Significant association with root prominence in illustrations (TEST 3 PASS)
- Association survives Bonferroni correction and permutation testing (TEST 5 PASS)
- No anachronistic patterns detected (TEST 4 PASS)

**Evidence AGAINST:**
- Only 2/5 archetypes recur across families (TEST 2 FAIL)
- Only 1/3 visual features show association (root prominence only)
- Direction of effect is inverse (more markers when roots less prominent)

**Critical nuance:**

The significant association is with **root prominence** specifically, not with root presence/absence or other anatomical features. The direction suggests:

> Prefixes may encode **structural/organizational complexity** rather than direct plant-part selection.

When illustrations have less prominent root features, entries use more position-marking prefixes. This is consistent with:
1. Organizational compensation (more textual structure when visual is simpler)
2. Genre correlation (simpler plants may have different procedural requirements)
3. Manuscript section effects (folios with simpler illustrations may be from different production phases)

**DOES NOT PROVE:** That prefixes directly encode "which plant part to use"
**DOES PROVE:** Statistical relationship exists between prefix morphology and illustration features

---

## Remaining Questions

1. **Expand visual coverage:** Only 30 folios have visual annotation; 53 folios remain uncoded
2. **Test direction hypothesis:** Does textual complexity compensate for visual simplicity?
3. **Currier A analysis:** Extend analysis to A-text (definitional) folios where archetypes 1, 3, 4 may appear
4. **Leaf/stem features:** Additional visual coding could test other anatomical correlations

---

## Conclusion

> The prefix archetype structure shows a **real, non-random association** with plant illustration features. However, the pattern is better explained as **organizational correlation** rather than direct material-selection encoding.
>
> The material-selection hypothesis receives **WEAK SUPPORT** - there is a signal, but the interpretation remains ambiguous.

---

*This document reports the primary constraint tests. See era_compatibility_assessment.md for detailed era-appropriateness analysis.*
*Updated with visual data from blinded_visual_coding.json (30 folios)*
