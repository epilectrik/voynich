# MIDDLE A-B Overlap Analysis

**Phase:** MIDDLE-AB
**Date:** 2026-01-16
**Status:** COMPLETE

---

## Executive Summary

> **56.6% of Currier A MIDDLEs are A-exclusive** (never appear in B). This supports a "material catalog" model where A catalogues entities that B doesn't directly reference, rather than a pure "shared operational vocabulary" model.

---

## Background

The context system had conflicting MIDDLE counts:

| Source | Claimed Count | What It Actually Is |
|--------|---------------|---------------------|
| C423, MODEL_CONTEXT | 1,184 | **Union of A ∪ B MIDDLEs** (confirmed) |
| EXT9_REPORT | 725 | Unknown origin - likely parsing error |
| This analysis | 617 (A), 837 (B) | Distinct counts per system |

---

## Results

### Token Parsing

| System | Tokens | Parsed | Rate |
|--------|--------|--------|------|
| Currier A | 11,346 | 9,140 | 80.6% |
| Currier B | 23,195 | 19,439 | 83.8% |

### MIDDLE Inventory

| Metric | Count |
|--------|-------|
| A unique MIDDLEs | 617 |
| B unique MIDDLEs | 837 |
| **Shared (A ∩ B)** | **268** |
| **A-only (A - B)** | **349** |
| B-only (B - A) | 569 |
| Total union | 1,186 |

### Overlap Percentages

| Metric | Value |
|--------|-------|
| A MIDDLEs that are A-exclusive | **56.6%** |
| A MIDDLEs that appear in B | 43.4% |
| B MIDDLEs that are B-exclusive | 68.0% |
| B MIDDLEs that appear in A | 32.0% |
| Jaccard similarity | 0.226 |

### Frequency Analysis

| Metric | A | B |
|--------|---|---|
| Hapax (freq=1) | 397 (64.3%) | 528 (63.1%) |
| Core (freq≥10) | 56 | 83 |

---

## Key Examples

### A-Only MIDDLEs (never in B)

| MIDDLE | Count | Notes |
|--------|-------|-------|
| ho | 43 | Most common A-exclusive |
| heo | 10 | |
| hod | 10 | |
| okeo | 6 | |
| tod | 6 | |

These may represent:
- Material/entity identifiers catalogued but not operationally processed
- Registry-specific discriminators
- Specialized classification vocabulary

### B-Only MIDDLEs (never in A)

| MIDDLE | Count | Notes |
|--------|-------|-------|
| lk | 30 | L-compound (C298: B-specific) |
| ked | 26 | |
| ched | 17 | |
| ted | 16 | |
| lkee | 15 | L-compound |

These include L-compounds (lk-, lkee) which C298 already identified as B-specific grammatical operators.

### Most Common Shared MIDDLEs

| MIDDLE | Total Count | Notes |
|--------|-------------|-------|
| _EMPTY_ | 14,614 | PREFIX+SUFFIX only, no MIDDLE |
| e | 2,465 | |
| k | 1,140 | |
| o | 865 | |
| ee | 707 | |

The most shared MIDDLEs are simple, short forms - likely infrastructure/connective vocabulary.

---

## Interpretation

### The 1,184 Mystery: SOLVED

The oft-cited "1,184 MIDDLEs" is the **union** of A and B vocabularies, not just A's count:

- A contributes 617 unique MIDDLEs
- B contributes 837 unique MIDDLEs
- Together they form 1,186 (≈1,184) distinct MIDDLEs

### The 725 Mystery: UNRESOLVED

EXT9_REPORT claimed "~725 Middles (8 A-exclusive)". This doesn't match:
- A has 617 unique MIDDLEs, not 725
- A has 349 A-exclusive MIDDLEs, not 8-9

The EXT9 figure likely used different parsing rules or was an error.

### Model Implications

**Finding:** 56.6% of A MIDDLEs never appear in B.

This is **inconsistent** with a pure "operational vocabulary" model where A and B share a common MIDDLE language. Instead, it suggests:

1. **A catalogues entities B doesn't reference** - Over half of A's discriminators are irrelevant to B programs

2. **B has its own vocabulary** - 68% of B MIDDLEs are B-exclusive, including specialized L-compound operators

3. **Limited shared core** - Only 268 MIDDLEs bridge both systems (22.6% Jaccard)

### What This Means for Currier A

A's ~617 MIDDLEs fall into two populations:

| Population | Size | Function |
|------------|------|----------|
| **A-exclusive** | 349 (56.6%) | Catalog-only discriminators - material/entity identifiers that B never operates on |
| **Shared** | 268 (43.4%) | Cross-system vocabulary - operational config that B uses |

This supports viewing A as a **registry that extends beyond B's operational needs** - cataloguing more than B processes.

---

## Constraint Implications

### C423 Needs Clarification

Current: "1,184 distinct MIDDLEs"

Should be: "1,186 distinct MIDDLEs across A and B combined (617 in A, 837 in B, 268 shared)"

### EXT9_REPORT Needs Correction

The "~725 Middles (8 A-exclusive)" claim is incorrect and should be updated with these findings.

### Potential New Constraint

> **C4XX:** Currier A and B share only 268 MIDDLEs (22.6% Jaccard); 56.6% of A MIDDLEs are A-exclusive; A catalogues entities beyond B's operational scope.

---

## Files

| File | Purpose |
|------|---------|
| `phases/MIDDLE_AB/middle_ab_overlap.py` | Analysis script |
| `results/middle_ab_overlap.json` | Full results |
| `phases/MIDDLE_AB/MIDDLE_AB_REPORT.md` | This report |

---

*Analysis complete 2026-01-16.*
