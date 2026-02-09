# RI-AZC Linking Investigation

**Status:** COMPLETE - NEGATIVE RESULT
**Date:** 2026-02-02
**Verdict:** Vocabulary clustering hypothesis NOT SUPPORTED; confirms C835 navigational interpretation

---

## Summary

This investigation tested whether RI tokens appearing in AZC diagram positions serve as "see also" pointers to semantically related Currier A content. The hypothesis was falsified through controlled testing.

**Key conclusion:** RI tokens can appear in AZC diagram positions (architecturally permitted), but they do NOT create vocabulary clustering beyond baseline frequency/section effects. This confirms that the C835 linker mechanism is navigational/structural, not semantic.

---

## Initial Observations

### RI Tokens in AZC Diagram Positions

| Metric | Value |
|--------|-------|
| Total RI tokens in AZC | 60 |
| In P-text positions | 8 (13.3%) |
| In diagram positions (C/R/S/etc) | 52 (86.7%) |

**cthody** (documented A linker per C835) appears at:
- f68v1 **C** (center position)
- f69r **R** (ring position)

### RI Vocabulary Coverage

- 33/592 RI MIDDLEs (5.6%) appear in AZC diagrams
- This is a selective subset, not random vocabulary overlap

### Initial Signal

A lines sharing AZC-referenced RI MIDDLEs showed **1.92x vocabulary overlap** vs random baseline. This appeared to support the "see also" hypothesis.

---

## Control Tests

### 1. Frequency Control: CONFOUND DETECTED

The 10 testable MIDDLEs (those appearing in 2+ A lines) are extremely frequency-biased:

| Metric | Testable MIDDLEs | Expected (random) |
|--------|------------------|-------------------|
| Mean rank | 37.5 | 296.5 |
| Ratio | **0.13** | 1.0 |

**All 10 testable MIDDLEs are in the TOP 13% by frequency.**

- 'ho' (cthody) is rank #1 with freq=42 (vs mean of 1.3)
- The "testable" criterion selected for high-frequency types
- High-frequency MIDDLEs naturally co-occur more, creating artificial overlap

### 2. Section Control: EFFECT COLLAPSES

When pairs are separated by within-section vs cross-section:

| Pair Type | AZC-linked | Random | Ratio |
|-----------|------------|--------|-------|
| Within-section | 0.077 | 0.079 | **0.98x** |
| Cross-section | 0.070 | 0.072 | **0.97x** |

**The 1.92x effect completely disappears.** Both categories are slightly below baseline.

### 3. Directionality Test: INSUFFICIENT DATA

- Only 2 documented linkers appear in AZC diagrams (both cthody)
- Only 3 ct-prefix RI tokens total in AZC diagrams
- Cannot determine position-directionality correlation

**Folio flow observation:** cthody's A appearances span folios both before (8) and after (5) the AZC range (f57-f73), consistent with AZC functioning as a bidirectional hub.

---

## Conclusions

### 1. Vocabulary Clustering Hypothesis: FALSIFIED

The original 1.92x overlap was an artifact of:
1. **Frequency bias** - testable MIDDLEs are in top 13% by frequency
2. **Section composition** - effect disappears when within/cross-section pairs are separated

### 2. What Remains Valid

- RI tokens CAN appear in AZC diagram positions (architecturally permitted per C301)
- cthody specifically appears at C and R positions
- 5.6% of RI vocabulary is selectively present in AZC diagrams

### 3. Interpretation

Per expert consultation, this negative result **strengthens** existing understanding:

- C835 already documents that linkers connect "complements not similars"
- The linker function is **navigational cross-reference** ("see also folio X")
- NOT semantic similarity clustering

The appearance of cthody in AZC diagram positions is consistent with its documented linker function - marking where cross-reference relationships apply within the diagram context.

---

## Recommendations

### No New Constraint Warranted

The observations are covered by existing architecture:
- C301 (AZC Hybrid): AZC shares vocabulary with both A and B
- C835 (RI Linker Mechanism): Documents linker function as navigational

### Path Closed

**Do NOT retry** vocabulary-based semantic interpretations for RI-AZC relationship. The hypothesis has been properly tested and falsified.

### Documentation Value

This negative result is valuable because it:
1. Closes a plausible but incorrect interpretation
2. Confirms C835's navigational (not semantic) interpretation
3. Demonstrates proper methodological controls (frequency, section)

---

## Test Scripts

Located in scratchpad (session-specific):
- `verify_ri_positions.py` - P-text vs diagram position separation
- `ri_azc_see_also.py` - Vocabulary overlap test
- `ri_frequency_control.py` - Frequency confound analysis
- `ri_section_control.py` - Section confound analysis
- `ri_azc_directionality.py` - Position-directionality test

---

## Expert Consultations

Three expert consultations were conducted:

1. **Initial finding review** - Raised P-text contamination concern (addressed by position verification)
2. **Vocabulary overlap review** - Identified frequency and section as potential confounds
3. **Final review** - Confirmed negative result, recommended documentation as phase summary

---

## Quantitative Summary

| Test | Result | Interpretation |
|------|--------|----------------|
| RI in diagram positions | 86.7% | Not P-text contamination |
| Initial vocabulary overlap | 1.92x | Appeared significant |
| Frequency control | Testable MIDDLEs in top 13% | Confound detected |
| Section control (within) | 0.98x baseline | Effect collapses |
| Section control (cross) | 0.97x baseline | Effect collapses |
| Directionality | n=3 | Insufficient data |

**Final verdict:** Vocabulary clustering hypothesis NOT SUPPORTED. RI-AZC relationship is navigational/structural per C835, not semantic indexing.
