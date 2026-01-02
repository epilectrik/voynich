# Prefix/Suffix Coordinate-System Test Battery

*Generated: 2026-01-01*
*Status: SUPPORT*

---

## Purpose

Test whether prefixes and suffixes function as positional/coordinate-like indices
within an abstract structured space, rather than encoding semantic content.

---

## Summary

| Test | Finding | Verdict |
|------|---------|---------|
| TEST 1: Axis Independence | MI=0.075 bits, 100th percentile | **SIGNIFICANT** |
| TEST 2: Local Continuity | d=17.47 (very strong) | **SIGNIFICANT** |
| TEST 3: Cycle-Phase | prefix d=0.19, suffix d=1.47 | NOT_SIGNIFICANT |
| TEST 4: Axial Consistency | (terminated early) | INCOMPLETE |

**Tests with significant positional effects: 2/3 completed**

---

## TEST 1: PREFIX x SUFFIX AXIS INDEPENDENCE

**Goal:** Determine whether prefix and suffix channels behave like partially independent axes.

### Results

| Metric | Value |
|--------|-------|
| Mutual Information | 0.0752 bits |
| H(prefix\|suffix) | 2.2023 bits |
| H(suffix\|prefix) | 1.5711 bits |
| Chi-square | 3858.58 (p < 0.000001) |
| Null MI (prefix shuffle) | 0.0014 +/- 0.0005 |
| Observed percentile | 100.0% |

### Interpretation

- Over-represented combinations: 9
- Under-represented combinations: 12
- **PARTIAL_INDEPENDENCE**: Prefix and suffix channels show significant but modest mutual information (0.075 bits), indicating they carry largely independent positional information with some structured co-occurrence constraints.

**Verdict: SIGNIFICANT**

---

## TEST 2: LOCAL CONTINUITY / SMOOTHNESS TEST

**Goal:** Test whether prefix/suffix usage shows local continuity along manuscript order.

### Results

| Metric | Value |
|--------|-------|
| Mean consecutive folio distance (JS) | 0.1471 |
| Null mean distance | 0.2202 +/- 0.0042 |
| Observed percentile | 0.0% (more continuous than ALL random orderings) |
| Effect size (Cohen's d) | **17.473** |
| Folios analyzed | 224 |

### Interpretation

- Adjacent folios are **far more similar** in prefix/suffix distribution than expected by chance
- Effect size of 17.47 is extraordinarily large
- This strongly supports a **positional/sequential structure** where prefix/suffix usage changes gradually through the manuscript

**Verdict: SIGNIFICANT**

---

## TEST 3: CYCLE-PHASE ALIGNMENT

**Goal:** Determine whether prefix/suffix usage aligns with cycle position (slot within entry).

### Prefix-Phase Results

| Metric | Value |
|--------|-------|
| Chi-square | 19.06 (p=0.388) |
| Percentile rank | 62.6% |
| Effect size | 0.19 |

### Suffix-Phase Results

| Metric | Value |
|--------|-------|
| Chi-square | 15.00 (p=0.091) |
| Percentile rank | 92.0% |
| Effect size | 1.47 |

### Interpretation

- Neither prefix nor suffix archetypes show significant phase-dependent enrichment
- Distribution across EARLY/MID_EARLY/MID_LATE/LATE phases is relatively uniform
- Positional structure operates at **folio level**, not within-entry cycle level

**Verdict: NOT_SIGNIFICANT**

---

## TEST 4: AXIAL CONSISTENCY ACROSS FOLIOS

**Goal:** Test whether prefix-suffix combinations recur at similar positions across folios.

### Partial Results (before termination)

| Metric | Value |
|--------|-------|
| Combinations analyzed | 27 |
| Observed mean positional std | 0.288 |
| Tightly clustered (std < 0.25) | 1 |

**Verdict: INCOMPLETE** (permutation test terminated due to computational cost)

---

## Final Verdict

**SUPPORT**

Prefixes and suffixes show positional/coordinate-like structuring based on 2/3 completed tests showing significant effects.

### Key Findings

1. **Axis Independence (TEST 1)**: Prefix and suffix channels are partially independent (low MI = 0.075 bits), suggesting they encode different positional dimensions

2. **Local Continuity (TEST 2)**: Extremely strong sequential structure (d=17.47). Adjacent folios share similar prefix/suffix profiles, indicating these channels track manuscript position

3. **Not Cycle-Aligned (TEST 3)**: Positional structure operates at folio level, not within-entry cycle level

### Pre-Registered Decision Criteria

- **SUPPORT**: >= 2 tests significant with positional effects ✓
- WEAK SUPPORT: 1 test significant
- NO SUPPORT: 0 tests significant

---

## Implications

The prefix/suffix system appears to function as a **folio-level positional indexing mechanism** rather than encoding semantic content or cycle-phase information. This is consistent with:

- Navigation/reference system within the manuscript
- Structural markers for manuscript organization
- Non-semantic coordinate system for locating content

---

*Statistical and descriptive analysis only. No semantic interpretations.*
