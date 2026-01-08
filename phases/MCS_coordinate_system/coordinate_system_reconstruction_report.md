# Phase MCS: Manuscript Coordinate System Reconstruction

**Status:** COMPLETE
**Date:** 2026-01-04
**Prerequisite:** Phase UTC (Uncategorized Token Characterization)

---

## Executive Summary

Two of five hypotheses were supported. Uncategorized tokens form a **SECTION-LEVEL COORDINATE SYSTEM**, not a line-level or quire-level one.

### Critical Finding

**80.7% of uncategorized token types appear in only ONE section.**

This is the dominant structural signal. Combined with the Phase UTC finding (9.1% vocabulary overlap across manuscript), this confirms uncategorized tokens are **section-specific organizational markers**.

---

## Hypothesis Results

| Hypothesis | Test | Verdict | Key Finding |
|------------|------|---------|-------------|
| MCS-1: Line Number | Chi-square vs uniform | **FALSIFIED** | 0% showed line-position affinity |
| MCS-2: Quire Boundary | Boundary enrichment | **FALSIFIED** | Only 1.07x enrichment (threshold 1.3x) |
| MCS-3: Section Header | Section-exclusive count | **SUPPORTED** | **80.7% section-exclusive** |
| MCS-4: Prefix/Suffix | Distribution comparison | **SUPPORTED** | p < 0.001 (highly significant) |
| MCS-5: Line-Initial | Vocabulary concentration | **FALSIFIED** | 1,220 types for 50% (too diffuse) |

---

## Detailed Results

### MCS-1: Line Number Encoding (FALSIFIED)

**Question:** Do uncategorized tokens encode line positions?

**Result:**
- Tested: 155 tokens (freq >= 10)
- Significant line-position affinity: **0 tokens (0%)**
- Threshold for support: >10%

**Conclusion:** No uncategorized token type shows systematic preference for specific line numbers. This is not a line-numbering system.

---

### MCS-2: Quire Boundary Markers (FALSIFIED)

**Question:** Do uncategorized tokens cluster at quire boundaries?

**Result:**
- Boundary folios: 43.1% uncategorized
- Interior folios: 40.3% uncategorized
- Enrichment: **1.07x** (threshold 1.3x)
- Chi-square p = 1.45e-05 (significant but effect size too small)

**Conclusion:** While statistically significant, the enrichment is too small to constitute a boundary-marking system. Quire transitions are not marked by distinct vocabulary.

---

### MCS-3: Section Header Tokens (SUPPORTED)

**Question:** Are uncategorized tokens section-specific markers?

**Result:**
- Total uncategorized types: 11,649
- Section-exclusive: **9,402 (80.7%)**
- Section-dominant (>50%): 640 (5.5%)

**Section Breakdown:**
| Section | Exclusive Tokens |
|---------|-----------------|
| H | 2,896 |
| S | 2,331 |
| B | 1,153 |
| P | 830 |
| C | 738 |
| Z | 586 |
| A | 454 |
| T | 414 |

**Conclusion:** **This is the dominant signal.** Over 80% of uncategorized token types appear exclusively within a single section. Each section has its own private vocabulary of organizational markers.

---

### MCS-4: Prefix/Suffix Correlation (SUPPORTED)

**Question:** Do uncategorized tokens use different prefix/suffix patterns?

**Result:**
- Prefix distribution difference: **p = 0.00** (highly significant)
- Suffix distribution difference: **p = 0.00** (highly significant)

**Key Pattern Shifts:**

| Prefix | Categorized | Uncategorized | Shift |
|--------|-------------|---------------|-------|
| qo | 18.3% | 13.3% | -5% |
| da | 9.5% | 4.3% | -5% |
| yk | 1.5% | 3.3% | +1.8% |

| Suffix | Categorized | Uncategorized | Shift |
|--------|-------------|---------------|-------|
| aiin | 12.8% | 8.5% | -4% |
| edy | 10.6% | 4.3% | -6% |
| dy | 6.9% | 10.8% | +4% |
| hy | 5.6% | 8.1% | +2.5% |

**Conclusion:** Uncategorized tokens occupy a **different morphological region** of the prefix/suffix coordinate space. They avoid the high-frequency operational prefixes (qo, da) and suffixes (aiin, edy) while favoring others (yk, dy, hy).

---

### MCS-5: Line-Initial Vocabulary (FALSIFIED)

**Question:** Is line-initial enrichment driven by concentrated vocabulary?

**Result:**
- Line-initial types: 3,352
- Types needed for 50% of occurrences: **1,220**
- Line-initial-specific (>70%): 43 tokens
- Jaccard similarity (LI vs non-LI): 0.087

**Conclusion:** The line-initial enrichment (2.16x from Phase UTC) is NOT driven by a small concentrated vocabulary. 1,220 types are needed for 50% coverage - far above the 100 threshold. The 43 line-initial-specific tokens are a minor subpopulation, not the explanation.

---

## Synthesis

### What the Coordinate System IS

1. **SECTION-BOUND** (primary dimension)
   - 80.7% of uncategorized types are section-exclusive
   - Each of the 8 sections has distinct organizational vocabulary
   - Section H has the most (2,896), Section T the least (414)

2. **MORPHOLOGICALLY DISTINCT** (secondary dimension)
   - Uses different prefix/suffix patterns than operational grammar
   - Avoids high-frequency operational morphemes
   - Clusters in different regions of prefix/suffix space

### What the Coordinate System IS NOT

1. **NOT line-level** - No line number encoding detected
2. **NOT quire-level** - Boundary enrichment negligible (1.07x)
3. **NOT concentrated** - Vocabulary too diffuse for simple markers

---

## Structural Model

```
MANUSCRIPT ARCHITECTURE (Two-Track)
====================================

TRACK 1: OPERATIONAL GRAMMAR (frozen)
  - 479 categorized tokens
  - 49 instruction classes
  - Hazard topology
  - Kernel control structure
  - OPERATES apparatus

TRACK 2: SECTION COORDINATE SYSTEM (this finding)
  - ~11,649 uncategorized types
  - 80.7% section-exclusive
  - Morphologically distinct
  - LOCATES operator in manuscript

RELATIONSHIP:
  - Tracks are INDEPENDENT
  - Section markers never at forbidden seams
  - Section markers avoid hazard-involved tokens
  - Each section has private organizational vocabulary
```

---

## Interpretive Constraints (Updated)

### LOCKED (from Phase UTC + MCS)

1. Uncategorized tokens encode **WHERE** in the manuscript, not **WHAT** to do
2. The coordinate system operates at **SECTION** level, not line or quire
3. Each section has **private vocabulary** (80.7% exclusive)
4. Uncategorized tokens use **different morphological patterns**
5. They are **NOT** line numbers, page markers, or quire indicators

### DO NOT

- Assign operational semantics to uncategorized tokens
- Merge section vocabularies into single grammar
- Treat section-exclusive tokens as missing operational vocabulary
- Expect cross-section vocabulary consistency

---

## Implications for VEE App

The tooltip system should:
1. Display section affiliation for uncategorized tokens
2. NOT display operational characteristics (they have none)
3. Indicate "Section-specific organizational marker" rather than "Unknown"
4. Consider visual distinction between Track 1 (operational) and Track 2 (navigational)

---

## Next Phase Recommendations

### Immediate (High Confidence)

1. **Characterize section vocabularies** - What morphological patterns dominate each section?
2. **Test illustration correlation** - Do section-specific tokens cluster near diagrams?
3. **Map Track 2 visually** - Color-code section markers in VEE app

### Speculative (Lower Confidence)

4. **Test for sub-section structure** - Are there coordinate levels finer than section?
5. **Cross-reference with codicology** - Do section boundaries align with physical gatherings?

---

## Files Generated

- `manuscript_coordinate_analysis.py` - Analysis script
- `phases/MCS_coordinate_system/coordinate_system_reconstruction_report.md` - This report

---

*Phase MCS complete. Two-track architecture confirmed at section level.*
