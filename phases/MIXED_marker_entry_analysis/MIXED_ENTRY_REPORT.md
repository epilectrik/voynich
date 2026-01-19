# Direction E: Mixed-Marker Entry Analysis

**Phase:** MIXED
**Date:** 2026-01-07
**Status:** CLOSED
**Updated:** 2026-01-16 (H-only transcriber filter verified)

---

## Scope Constraints (Pre-Committed)

This analysis was BOUNDED to:
- 5 specific tests (E-1 through E-5)
- Hard stop on: no pattern beyond random, only section-dependent
- Max 2 Tier 2 constraints
- No semantic interpretation

---

## Executive Summary

| Test | Finding | Verdict |
|------|---------|---------|
| **E-1: Marker count** | Mean 3.36 markers per mixed entry | 2-4 markers typical |
| **E-2: Co-occurrence** | All pairs ratio 0.9-1.0 | INDEPENDENT mixing |
| **E-3: Section** | H=90.1%, P=94.1%, T=96.2% mixed | SECTION-DEPENDENT (weak) |
| **E-4: Structure** | Mixed: longer, more B-vocab, earlier | STRUCTURAL DIFFERENCE |
| **E-5: Dominance** | Mean 0.48 dominance | BALANCED (not dominated) |

**Overall:** Mixed-marker lines are the DOMINANT mode (89.2%). Exclusive lines (8.7%) are shorter, have less B-vocabulary, and appear later in folios. Marker mixing is approximately INDEPENDENT (no preferred pairs). Direction E is now CLOSED.

---

## Key Finding: Mixed is the NORM

| Entry Type | Count | % |
|------------|-------|---|
| Mixed (2+ markers) | 1,410 | 89.2% |
| Exclusive (1 marker) | 137 | 8.7% |
| No markers | 33 | 2.1% |

**Critical insight:** The CAS-SCAN finding of "64.1% block entries" referred to REPETITION patterns, not marker composition. At the LINE level, 89.2% of A lines contain multiple marker classes.

**Note (2026-01-16):** The "64.1% block entries" finding (C250) was later INVALIDATED - it was a transcriber artifact caused by loading all transcribers instead of H (primary) only. With H-only data, block repetition is 0%.

---

## E-1: Marker Count Distribution

**Question:** How many markers per mixed entry?

| Marker Count | Entries | % |
|--------------|---------|---|
| 2 markers | 384 | 27.2% |
| 3 markers | 447 | 31.7% |
| 4 markers | 350 | 24.8% |
| 5 markers | 167 | 11.8% |
| 6 markers | 45 | 3.2% |
| 7 markers | 15 | 1.1% |
| 8 markers | 2 | 0.1% |

Statistics: Mean = 3.36, Std = 1.17, Max = 8

**Interpretation:** Most mixed lines have 2-4 markers (83.7%). Lines with 5+ markers are uncommon (16.3%). This suggests typical A lines reference 3-4 different marker families.

---

## E-2: Marker Co-occurrence Patterns

**Question:** Which markers appear together in mixed entries?

### Marker Frequency
| Marker | In Mixed Lines | % |
|--------|----------------|---|
| CH | 1,053 | 74.7% |
| DA | 764 | 54.2% |
| QO | 725 | 51.4% |
| SH | 698 | 49.5% |
| OK | 442 | 31.3% |
| OT | 413 | 29.3% |
| CT | 390 | 27.7% |
| OL | 250 | 17.7% |

### Co-occurrence Enrichment
| Pair | Observed | Expected | Ratio |
|------|----------|----------|-------|
| CH+DA | 548 | 570.6 | 0.96 |
| CH+QO | 504 | 541.4 | 0.93 |
| CH+SH | 496 | 521.3 | 0.95 |
| DA+QO | 403 | 392.8 | 1.03 |
| DA+SH | 361 | 378.2 | 0.95 |
| QO+SH | 342 | 358.9 | 0.95 |

All pairs: 0.9-1.0 ratio (NORMAL)

**Enriched pairs: 0**
**Avoided pairs: 0**

**Interpretation:** Marker mixing is approximately INDEPENDENT. No marker pair shows significant enrichment (>1.5x) or avoidance (<0.5x). Markers combine freely without preferred or forbidden combinations.

---

## E-3: Section Distribution

**Question:** Do mixed entries cluster in certain sections?

| Section | Exclusive | Mixed | Mixed Rate |
|---------|-----------|-------|------------|
| H | 119 | 1,087 | 90.1% |
| P | 14 | 222 | 94.1% |
| T | 4 | 101 | 96.2% |

Chi-square: p = 0.025

**Interpretation:** Mixing rate is weakly SECTION-DEPENDENT. Section T has highest mixing (96.2%), Section H lowest (90.1%). But all sections have >90% mixed lines - mixing is universal, section just modulates degree.

---

## E-4: Structural Differences

**Question:** Do mixed entries differ structurally from exclusive entries?

### Length

| Type | Mean Tokens | Std |
|------|-------------|-----|
| Exclusive | 14.5 | 8.4 |
| Mixed | 24.8 | 11.2 |

Mann-Whitney: p < 0.000001

**RESULT: Mixed entries are 71% LONGER**

### Position in Folio

| Type | Mean Line | Median |
|------|-----------|--------|
| Exclusive | 10.5 | 10.0 |
| Mixed | 8.2 | 7.0 |

Mann-Whitney: p < 0.000001

**RESULT: Exclusive entries appear LATER in folios**

### B-Vocabulary Overlap

| Type | Mean B-Overlap |
|------|----------------|
| Exclusive | 65.6% |
| Mixed | 76.1% |

Mann-Whitney: p < 0.000004

**RESULT: Mixed entries have MORE B-vocabulary**

### Interpretation

Exclusive lines are structurally distinct:
- **Shorter** (14.5 vs 24.8 tokens)
- **Later in folio** (mean line 10.5 vs 8.2)
- **Less B-vocabulary** (65.6% vs 76.1%)

This suggests exclusive lines are:
1. SPECIALIZED entries (single-marker focus)
2. ADDENDA or supplements (later position)
3. LESS procedurally relevant (lower B-overlap)

---

## E-5: Marker Dominance

**Question:** In mixed entries, is one marker dominant or balanced?

| Dominance Range | Entries | % |
|-----------------|---------|---|
| 0-50% | 694 | 49.2% |
| 50-67% | 593 | 42.1% |
| 67-80% | 77 | 5.5% |
| 80-90% | 41 | 2.9% |
| 90-100% | 5 | 0.4% |

Mean dominance: 0.48

**VERDICT: BALANCED.** In most mixed lines (91.3%), no single marker exceeds 67% of marked tokens. Marker distribution is genuinely mixed, not "one dominant + minor others."

---

## What These Tests Prove

### Mixed is the NORM

1. **89.2% of A lines are mixed** (2+ markers)
2. **Typical count is 2-4 markers** (83.7%)
3. **Mixing is universal across sections** (90-96%)

**Conclusion:** Currier A lines routinely combine multiple marker families. Single-marker lines are exceptions, not the standard.

### Markers Mix INDEPENDENTLY

1. **All pair ratios 0.9-1.0** (no enrichment/avoidance)
2. **No forbidden combinations** detected
3. **CH dominates** (74.7%) but doesn't exclude others

**Conclusion:** The 8 marker classes can combine freely. No grammatical constraints on which markers appear together.

### Exclusive Lines are SPECIALIZED

1. **Shorter** (14.5 vs 24.8 tokens)
2. **Later in folio** (mean line 10.5 vs 8.2)
3. **Less B-vocabulary** (65.6% vs 76.1%)

**Conclusion:** Exclusive lines likely serve a different function - specialized entries, addenda, or low-procedure-relevance annotations.

---

## Constraints to Add

### Constraint 337 (Tier 2)
**Mixed-marker dominance:** 89.2% of A lines contain 2+ marker classes; exclusive lines (8.7%) are shorter (14.5 vs 24.8 tokens), appear later in folios (10.5 vs 8.2), and have less B-vocabulary (65.6% vs 76.1%); mixing is the NORM, exclusivity is SPECIALIZED.

### Constraint 338 (Tier 2)
**Marker co-occurrence independence:** All marker pair ratios 0.9-1.0 (observed/expected); no enriched (>1.5x) or avoided (<0.5x) pairs; markers mix FREELY without grammatical constraints.

---

## Hard Stop Evaluation

| Condition | Status |
|-----------|--------|
| No pattern beyond random? | NO (structural differences detected) |
| Only section-dependent? | NO (E-4 findings are structural, not section) |
| Max 2 constraints? | YES (2 Tier 2) |

**STOP CONDITION 3 APPLIES:** 2 Tier 2 constraints found. Direction E is CLOSED.

---

## Clarification: CAS-SCAN vs E-Analysis

| Analysis | Unit | Finding |
|----------|------|---------|
| ~~CAS-SCAN~~ | ~~Blocks (repetition patterns)~~ | ~~64.1% block entries~~ **INVALIDATED** |
| E-Analysis | Lines (marker composition) | 89.2% mixed lines |

**Note (2026-01-16):** The CAS-SCAN "64.1% block entries" finding (C250) was INVALIDATED. It was a transcriber artifact - with H-only data, block repetition is 0%.

The E-Analysis finding (89.2% mixed lines) remains valid as it measures marker diversity, not repetition.

---

## Direction E: CLOSED

All five tests complete. Mixed-marker investigation is now FINISHED.

**Outcome:** 2 Tier 2 constraints added. Mixed-marker lines are the norm (89.2%), markers mix independently, exclusive lines are specialized.

No further mixed-marker investigation is warranted.

---

## Files

| File | Purpose |
|------|---------|
| `mixed_entry_tests.py` | Test implementation |
| `mixed_entry_results.json` | Raw results |
| `MIXED_ENTRY_REPORT.md` | This document |

---

*Direction E: CLOSED*
*Generated: 2026-01-07*
