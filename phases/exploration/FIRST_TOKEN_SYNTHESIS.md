# First-Token Positional Exception: Research Synthesis

**Phase:** Exploration
**Date:** 2026-01-09
**Status:** COMPLETE - Constraint C420 created

---

## Executive Summary

**Finding:** First-token position in Currier A folios permits otherwise illegal but morphologically compatible prefix variants (C+vowel forms: ko-, po-, to-) that do not occur elsewhere in the registry.

**Evidence strength:** VERY STRONG (Fisher exact p < 0.0001)

**Constraint created:** C420 (Folio-Initial Positional Exception)

**Framing:** This is a **positional tolerance** at codicological boundaries, NOT a semantic system, header register, or categorical marker.

---

## Research Questions & Answers

### Q1: Do ko- tokens pattern like ok- tokens morphologically?

**Answer: YES (Morphological Compatibility Confirmed)**

| Metric | Value | Threshold |
|--------|-------|-----------|
| Suffix Jaccard | 0.214 | > 0.20 |
| Direct token equivalents | 50% | - |
| Suffix compatibility | 100% | - |

100% of ko- suffixes are valid ok- suffixes. This rules out gibberish and damage.

### Q2: Do "inverted prefix" patterns correlate with folio organization?

**Answer: PARTIAL**

| Test | p-value | Decision |
|------|---------|----------|
| Quire x pass/fail | 0.86 | NOT SIGNIFICANT |
| Recto vs Verso | 0.02 | SIGNIFICANT |

The pattern is quire-independent but shows verso preference (67% vs 29%).

### Q3: Is first-token position structurally exceptional?

**Answer: YES**

| Position | Fail Rate | C+vowel |
|----------|-----------|---------|
| 1 | 75% | 47.9% |
| 2 | 31% | 0.0% |
| 3 | 29% | 0.0% |

Position 1 is structurally distinct. Positions 2-3 show different failure types (HT, damage).

---

## Falsified Hypotheses

| Hypothesis | Status | Evidence |
|------------|--------|----------|
| Random noise | REJECTED | p < 0.0001 |
| Section-conditioned | REJECTED | Quire chi2 p = 0.86 |
| Damage artifacts | REJECTED | Morphological compatibility |
| Sequential enumeration | REJECTED | No ordering, 97.9% unique |
| Chapter markers/headers | NOT SUPPORTED | No semantic evidence |
| Functional labeling | NOT SUPPORTED | No predictive content |

---

## Correct Interpretation

**What this IS:**
- Positional tolerance at physical (codicological) boundaries
- Position-restricted morphological variants
- Consistent with medieval registry boundary conditions

**What this is NOT:**
- A new register or subsystem
- Chapter markers or headers
- Functional labeling or titles
- Enumeration or numbering
- Semantic categories

---

## Constraint Impact

| Constraint | Status |
|------------|--------|
| C240 (8 Marker Families) | **UNCHANGED** |
| C234 (POSITION_FREE) | **UNCHANGED** (applies to entries, not boundaries) |
| C267 (Compositional Morphology) | **CONSISTENT** |
| **C420** (NEW) | Folio-Initial Positional Exception |

---

## Key Statistics

| Metric | Value |
|--------|-------|
| Folios analyzed | 48 |
| Position-1 failure rate | 75% |
| C+vowel in position 1 | 47.9% |
| C+vowel in positions 2-3 | 0.0% |
| Token uniqueness | 97.9% (47/48) |
| Only repeated token | pchor (19r, 21r) |
| ko- suffix compatibility with ok- | 100% |

---

## Files Generated

| File | Purpose |
|------|---------|
| `first_token_analysis.py` | Data collection |
| `first_token_data.json` | Raw data |
| `first_token_morphology.py` | Morphological tests |
| `first_token_morphology_results.json` | Phase 2 results |
| `first_token_position.py` | Position analysis |
| `first_token_position_results.json` | Phase 3 results |
| `check_*.py` | Supporting analyses |
| `test_*.py` | Statistical tests |

---

## Archived to Constraint System

**C420** created at: `context/CLAIMS/C420_folio_initial_exception.md`

---

## References

- C234: currier_a.md (POSITION_FREE)
- C240: C240_currier_a_registry.md (8 Marker Families)
- C267: morphology.md (Compositional Morphology)
