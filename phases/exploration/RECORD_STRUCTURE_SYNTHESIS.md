# Currier A Record Structure Analysis - Synthesis

**Date:** 2026-01-09
**Status:** COMPLETE
**Constraint outcome:** C250.a refinement only (see expert review below)

---

## Executive Summary

Now that DA articulation is established (C422), we analyzed record-level structure in Currier A for the first time with proper block boundaries. This analysis reveals that Currier A entries follow predictable structural templates with block-level repetition.

---

## Key Findings

### Finding 1: Block Count Distribution

| Block Count | Entries | % | Cumulative |
|-------------|---------|---|------------|
| 1 (no internal DA) | 1,049 | 57.1% | 57.1% |
| 2 | 74 | 4.0% | 61.1% |
| 3 | 206 | 11.2% | 72.3% |
| 4 | 220 | 12.0% | 84.3% |
| 5+ | 289 | 15.7% | 100% |

**Interpretation:** ~57% of entries are simple (single block), ~43% have internal DA segmentation.

### Finding 2: Block Size Asymmetry

| Block Position | Mean Size (tokens) | Median |
|----------------|-------------------|--------|
| First | 11.5 | 7.0 |
| Second | 5.6 | 5.0 |
| Third | 5.2 | 5.0 |
| Fourth+ | 3.8 | 3.0 |

**Pattern:** FRONT-HEAVY structure. First block carries primary content, subsequent blocks are smaller.

63.5% of multi-block entries show skewed (unbalanced) block sizes.

### Finding 3: Positional Prefix Preferences (NEW)

| Prefix | First Block % | Last Block % | Delta |
|--------|---------------|--------------|-------|
| qo | 18.4% | 15.1% | -3.3% |
| sh | 16.5% | 12.9% | -3.6% |
| ct | 2.5% | 7.8% | +5.2% |
| ch | 45.7% | 45.8% | 0.0% |

**Statistical validation:** chi2=24.5, p<0.001, V=0.136

**Pattern:**
- qo, sh prefer FIRST block position
- ct prefers LAST block position
- ch is neutral

### Finding 4: Block-Level Repetition (CONFIRMS Hypothesis)

| Metric | Value |
|--------|-------|
| Multi-block entries with J >= 0.5 similarity | 91.5% |
| Exact block repetition | 58.7% |
| Mean block similarity | 0.815 |
| Median block similarity | 0.875 |

**Pattern:** Non-adjacent blocks are MORE similar (0.836) than adjacent (0.775).

This suggests interleaved repetition: A-DA-A-DA-B-DA-B

**Critical refinement:** Repetition operates at BLOCK level, not token/entry level. The `[BLOCK] × N` pattern from C250 is now confirmed to use DA-segmented blocks.

### Finding 5: Record Templates

| Template | % of Entries |
|----------|-------------|
| SINGLE/POLY (single block, 3+ prefixes) | 38.0% |
| MULTI/VARIABLE/POLY | 13.5% |
| SINGLE/DUAL_PF (single block, 2 prefixes) | 10.1% |
| SINGLE/MONO (single block, 1 prefix) | 9.0% |
| MULTI/BALANCED/POLY | 6.7% |
| *Top 5 coverage* | **77.3%** |

**Interpretation:** 3-5 dominant templates, long tail of variations. Consistent with human-usable registry design.

---

## Section Differences

| Section | Single-Block % | Mean Blocks | Complexity |
|---------|---------------|-------------|------------|
| H (Herbal) | 54.1% | 2.8 | Highest |
| P (Pharma) | 66.5% | 2.0 | Lowest |
| T (Text) | 52.6% | 2.4 | Medium |

Section P has simplest records. Section H has most complex multi-block entries.

---

## Expert Review Outcome

**Key principle:** A constraint must describe something that MUST be true, not something that OFTEN happens.

### ACCEPTED: C250.a - Block-Aligned Repetition (Refinement)

Refines C250. The `[BLOCK] × N` structure operates on DA-segmented units:
- 58.7% exact block repetition within entries
- 91.5% high similarity (J >= 0.5)
- Blocks repeat non-adjacently, suggesting enumeration of similar items

This adds *precision* to existing CAS-MULT constraints without introducing new behavior.

### REJECTED: Positional Prefix Preferences

NOT a constraint because:
- No illegality (prefixes allowed everywhere)
- No mutual exclusion
- Effect size modest (V=0.136)
- Explained by existing prefix roles (C407-C410)

**Status:** Kept as descriptive finding only.

### REJECTED: Record Structure Templates

NOT a constraint because:
- Templates are *emergent regularities*, not rules
- Same reasoning that excluded program archetypes, regime clusters
- No prohibition, no necessity

**Status:** Kept as descriptive finding only.

---

## Files Created

| File | Purpose |
|------|---------|
| `record_structure_analysis.py` | Main analysis script |
| `block_position_prefix_test.py` | Statistical validation |
| `repetition_block_alignment.py` | Block repetition test |

---

## Integration with Existing Constraints

| Constraint | Status |
|------------|--------|
| C250 (64.1% repetition) | REFINED by C250.a |
| C262 (7.7% variation) | CONFIRMED - block similarity explains this |
| C422 (DA articulation) | LEVERAGED - blocks now defined |
| C410 (section conditioning) | CONFIRMED - section affects complexity |

---

## Conclusion

Currier A record structure is now characterized at descriptive level:

1. **Entry = 1-N blocks separated by DA** (structural)
2. **Blocks are FRONT-HEAVY (first block largest)** (tendency)
3. **Blocks REPEAT within entries (58.7% exact)** (refined C250)
4. **Prefix families show positional tendencies** (preference, not rule)
5. **3-5 stable templates cover 77% of entries** (emergent pattern)

These findings describe **USE of structure**, not design limits.

Only C250.a (block-aligned repetition) rises to refinement level.
Other findings remain valuable descriptive documentation.
