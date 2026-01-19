# Direction F: Cycle Semantics Analysis

**Phase:** CYCLE
**Date:** 2026-01-07
**Status:** CLOSED (Hard Stop Triggered)
**Updated:** 2026-01-16 (H-only transcriber filter verified)

---

## Scope Constraints (Pre-Committed)

This analysis was BOUNDED to:
- 3 specific tests (F-1 through F-3)
- Focus on core vocabulary (top 200 tokens)
- Hard stop on: populations identical, no kernel distinction
- Max 2 Tier 2 constraints

---

## Executive Summary

| Test | Finding | Verdict |
|------|---------|---------|
| **F-1: Cycle topology** | 100% token overlap | IDENTICAL POPULATIONS |
| **F-2: Kernel relationship** | Same composition (30.5% e, 69.5% none) | NO DISTINCTION |
| **F-3: Folio distribution** | r=1.000 correlation | PERFECTLY CORRELATED |

**Overall:** 3-cycles and 4-cycles involve the SAME tokens with the SAME kernel composition. No semantic distinction exists. Direction F is CLOSED via hard stop.

---

## Key Finding: No Semantic Distinction

The core vocabulary (top 200 tokens) forms a densely connected graph where:

- **ALL 200 tokens** participate in both 3-cycles and 4-cycles
- **Overlap is 100%** - no token-level distinction
- **Kernel composition identical** (30.5% 'e'-class in both)
- **Folio density perfectly correlated** (r=1.000)

**Conclusion:** The "500+ 4-cycles, 56 3-cycles" documented in Constraint 90 are emergent properties of dense connectivity, NOT meaningful structural categories.

---

## F-1: Cycle Topology

**Question:** What tokens form 3-cycles vs 4-cycles?

### Results

| Metric | 3-cycles | 4-cycles |
|--------|----------|----------|
| Unique cycles | 33,791 | 1,018,127 |
| Tokens involved | 200 | 200 |
| Overlap with other type | 200 (100%) | 200 (100%) |

**Interpretation:** The core vocabulary is so densely interconnected that EVERY token participates in BOTH cycle types. There is no token-level discrimination between 3-cycle and 4-cycle membership.

---

## F-2: Kernel Relationship

**Question:** Do 3-cycles and 4-cycles have different kernel composition?

### Results

| Type | k | h | e | None |
|------|---|---|---|------|
| 3-cycles | 0.0% | 0.0% | 30.5% | 69.5% |
| 4-cycles | 0.0% | 0.0% | 30.5% | 69.5% |
| Core vocab | 0.0% | 0.0% | 30.5% | 69.5% |

**Interpretation:** Kernel composition is IDENTICAL across 3-cycles, 4-cycles, and the baseline vocabulary. Cycle membership does not correlate with kernel class.

Note: The absence of 'k' and 'h' in the top 200 is due to their rarity in the corpus (0.2% and 0.1% respectively).

---

## F-3: Folio Distribution

**Question:** Does cycle density vary by folio?

### Results

| Metric | 3-cycle | 4-cycle |
|--------|---------|---------|
| Mean density | 36.4% | 36.4% |
| Std | 8.0% | 8.0% |
| Min | 16.8% | 16.8% |
| Max | 59.8% | 59.8% |

**Spearman correlation:** r = 1.000, p < 0.000001

**Interpretation:** 3-cycle and 4-cycle densities are PERFECTLY CORRELATED across folios. Wherever 3-cycle tokens appear, 4-cycle tokens appear in exactly the same proportion.

---

## Why This Matters

### Original Understanding (Constraint 90)
> "500+ 4-cycles, 56 3-cycles"

This was interpreted as two DISTINCT structural phenomena possibly encoding different control strategies.

### Revised Understanding (Direction F)

The 3-cycle/4-cycle distinction is **NOT MEANINGFUL**:

1. **Same tokens** participate in both cycle types (100% overlap)
2. **Same kernel composition** in both (30.5% 'e')
3. **Same folio distribution** (r=1.000)

The different COUNTS (56 vs 500+) simply reflect that longer paths are combinatorially more numerous in a dense graph, not that they encode different information.

---

## Hard Stop Triggered

| Condition | Status |
|-----------|--------|
| Populations identical? | YES (100% overlap) |
| No kernel distinction? | YES (same composition) |

**STOP CONDITION APPLIES:** Cycle populations identical with no kernel distinction. Direction F is CLOSED.

**No new constraints warranted.**

---

## Constraint 90 Revision

The original constraint stated cycle counts as if they were structurally significant. Direction F shows they are NOT semantically distinct.

**Suggested revision to Constraint 90:**
> "500+ 4-cycles, 56 3-cycles exist in the transition graph; Direction F showed these are NOT distinct phenomena - all core vocabulary participates in both cycle types with identical kernel composition."

---

## Direction F: CLOSED

All three tests complete. Cycle semantics investigation is now FINISHED.

**Outcome:** Hard stop triggered. 3-cycles and 4-cycles are not semantically distinct. 0 new constraints.

No further cycle investigation is warranted.

---

## Files

| File | Purpose |
|------|---------|
| `cycle_semantics_tests_v2.py` | Test implementation |
| `cycle_semantics_results.json` | Raw results |
| `CYCLE_SEMANTICS_REPORT.md` | This document |

---

*Direction F: CLOSED (Hard Stop)*
*Generated: 2026-01-07*
