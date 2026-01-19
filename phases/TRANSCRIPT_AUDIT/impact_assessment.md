# TRANSCRIPT-ARCHITECTURE-AUDIT: Impact Assessment

**Date:** 2026-01-16

---

## Summary

The audit discovered that prior analyses may have included non-text tokens (LABEL, RING, CIRCLE, STAR, OTHER) mixed with TEXT tokens. This document assesses the impact.

---

## Contamination Levels

| Language | Total H-only | TEXT | LABEL | % Labels |
|----------|--------------|------|-------|----------|
| Currier A | 11,415 | 11,081 | 183 | **1.6%** |
| Currier B | 23,243 | 21,649 | 99 | **0.4%** |

---

## Affected Analyses

### 1. MIDDLE-AB Overlap Analysis

**File:** `phases/MIDDLE_AB/middle_ab_overlap.py`

**Status:** Potentially affected

**Details:**
- Filters: `transcriber == 'H'` and `language == 'A'/'B'` only
- Does NOT filter by placement
- 183 A labels and 99 B labels were included

**Impact:** LOW
- Label tokens are 1.6% of A, 0.4% of B
- Labels have ~38% vocabulary overlap with text
- MIDDLE extraction would fail on most labels (they don't follow PREFIX+MIDDLE+SUFFIX structure)
- The core finding (84%+ of A MIDDLEs appear in B) is unlikely to change

### 2. Single-Token Record Analysis (23 records)

**Status:** DIRECTLY AFFECTED

**Details:**
- Found 23 "single-token" Currier A records
- 16/23 were later identified as pharmaceutical labels (placement=L*)
- Only 7 are actual single-token TEXT records

**Impact:** HIGH (for that specific analysis)
- The "single-token record" phenomenon is mostly labels, not text
- Original conclusion needs revision

### 3. Vocabulary Counts

**Status:** Potentially affected

**Details:**
- A vocabulary: 3,270 TEXT types + 161 LABEL types = ~3,370 combined
- Label-only types: 100 unique (not in text)

**Impact:** LOW
- 100 label-only types represent ~3% of apparent A vocabulary
- Core vocabulary statistics remain valid

---

## Recommended Actions

### Immediate (required)
1. Revise single-token record conclusion: 16/23 are labels, only 7 are text
2. Document that labels have their own vocabulary (~38% overlap with text)

### Deferred (optional)
3. Re-run MIDDLE-AB with placement filter to confirm findings
4. Audit vocabulary studies for label contamination

---

## Conclusion

**Overall impact: MINIMAL**

The primary contamination (1.6% A labels) is unlikely to have affected core findings about Currier A/B structure. The main casualty is the single-token record analysis, which was based on only 23 records.

For future analyses, filter by `placement.startswith('P')` when TEXT analysis is intended.
