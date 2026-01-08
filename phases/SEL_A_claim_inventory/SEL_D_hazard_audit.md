# SEL-D: Hazard Topology Necessity Audit

**Phase:** SEL-D (Self-Evaluation - Hazard Audit)
**Date:** 2026-01-05
**Authority Scope:** OPS ONLY
**Status:** DESTRUCTIVE AUDIT (no repairs)

---

## SECTION A — HAZARD INVENTORY

### Canonical Source: Phase 18A (17 transitions)

| ID | Source | Target | Fwd | Rev | Unique | Hazard Class |
|----|--------|--------|-----|-----|--------|--------------|
| 1 | shey | aiin | 0 | 10 | REDUNDANT | PHASE_ORDERING |
| 2 | shey | al | 0 | 6 | UNIQUE | PHASE_ORDERING |
| 3 | shey | c | 0 | 0 | UNIQUE | PHASE_ORDERING |
| 4 | chol | r | 0 | 2 | UNIQUE | PHASE_ORDERING |
| 5 | chedy | ee | 0 | 0 | UNIQUE | PHASE_ORDERING |
| 6 | dy | aiin | 0 | 8 | REDUNDANT | COMPOSITION_JUMP |
| 7 | dy | chey | 0 | 3 | UNIQUE | COMPOSITION_JUMP |
| 8 | l | chol | 0 | 1 | UNIQUE | PHASE_ORDERING |
| 9 | or | dal | 0 | 16 | UNIQUE | COMPOSITION_JUMP |
| 10 | chey | chedy | 0 | 5 | UNIQUE | PHASE_ORDERING |
| 11 | chey | shedy | 0 | 14 | UNIQUE | RATE_MISMATCH |
| 12 | ar | dal | 0 | 7 | UNIQUE | COMPOSITION_JUMP |
| 13 | c | ee | 0 | 0 | UNIQUE | CONTAINMENT_TIMING |
| 14 | he | t | 0 | 0 | UNIQUE | CONTAINMENT_TIMING |
| 15 | he | or | 0 | 0 | UNIQUE | CONTAINMENT_TIMING |
| 16 | shedy | aiin | 0 | 12 | REDUNDANT | ENERGY_OVERSHOOT |
| 17 | shedy | o | 0 | 0 | UNIQUE | CONTAINMENT_TIMING |

**Summary:**
- **Unique transitions:** 14/17
- **Potentially redundant:** 3/17 (all target `aiin`)
- **Corpus-blocking:** 11/17 (reverse > 0)
- **Theoretical only:** 6/17 (reverse = 0)

### CRITICAL FINDING: Implementation Discrepancy

**The `hazards.py` file implements a DIFFERENT list than Phase 18A canonical.**

| In Phase 18A only (7) | In hazards.py only (7) |
|----------------------|------------------------|
| ar → dal | ar → chol **(VIOLATED: 2)** |
| c → ee | qo → shey |
| chey → shedy | qo → shy **(VIOLATED: 1)** |
| he → or | ok → shol |
| he → t | ol → shor |
| shedy → aiin | dar → qokaiin **(VIOLATED: 4)** |
| shedy → o | qokaiin → qokedy **(VIOLATED: 3)** |

**Impact:** 4 transitions in hazards.py are violated in the actual corpus. This is a **data integrity failure**.

---

## SECTION B — CLASS TEST RESULTS

### Class Sizes

| Class | Members | Tokens | Status |
|-------|---------|--------|--------|
| PHASE_ORDERING | 7 | 10 | STRUCTURALLY FORCED |
| COMPOSITION_JUMP | 4 | 6 | STRUCTURALLY FORCED |
| CONTAINMENT_TIMING | 4 | 7 | ANALYST-GROUPED |
| RATE_MISMATCH | 1 | 2 | MERGEABLE |
| ENERGY_OVERSHOOT | 1 | 2 | MERGEABLE |

### Token Overlap (Jaccard)

| Pair | Jaccard | Shared |
|------|---------|--------|
| PHASE_ORDERING × COMPOSITION_JUMP | 0.143 | 2 |
| PHASE_ORDERING × CONTAINMENT_TIMING | 0.133 | 2 |
| RATE_MISMATCH × ENERGY_OVERSHOOT | **0.333** | 1 |

### Class Minimality Assessment

| Class | Minimal | Mergeable With |
|-------|---------|----------------|
| PHASE_ORDERING | YES | — |
| COMPOSITION_JUMP | YES | — |
| CONTAINMENT_TIMING | PARTIAL | Could absorb single-member classes |
| RATE_MISMATCH | **NO** | ENERGY_OVERSHOOT |
| ENERGY_OVERSHOOT | **NO** | RATE_MISMATCH |

**Verdict:** OVER_PARTITIONED

- Two single-member classes (RATE_MISMATCH, ENERGY_OVERSHOOT) are unjustified
- Could be merged into MISCELLANEOUS or absorbed into adjacent classes
- Class count could be reduced from 5 to 3-4 without structural loss

---

## SECTION C — BIDIRECTIONALITY FINDINGS

### Summary Table

| Pattern | Count | % |
|---------|-------|---|
| REVERSE_ALLOWED (asymmetric) | 11 | 65% |
| BOTH_ABSENT (symmetric) | 6 | 35% |

### Asymmetric Transitions (Reverse Exists)

| Transition | Reverse Count |
|------------|---------------|
| shey → aiin | 10 |
| shey → al | 6 |
| chol → r | 2 |
| dy → aiin | 8 |
| dy → chey | 3 |
| l → chol | 1 |
| or → dal | 16 |
| chey → chedy | 5 |
| chey → shedy | 14 |
| ar → dal | 7 |
| shedy → aiin | 12 |

**Critical Finding:**
- **OPS claims:** "100% bidirectional (mutual exclusions)"
- **Actual:** 65% (11/17) show asymmetric corpus evidence
- The corpus shows B→A exists while A→B is blocked
- These are **CAUSAL_HAZARDS**, not mutual exclusions

**Verdict:** OPS bidirectionality claim is **PARTIALLY FALSIFIED**

---

## SECTION D — KERNEL DEPENDENCE ANALYSIS

### Kernel Involvement

| Involvement | Count | % |
|-------------|-------|---|
| DIRECT (involves k/h/e) | 0 | 0% |
| ADJACENT (corpus-neighbor to k/h/e) | 7 | 41% |
| DISTANT (no kernel connection) | 10 | 59% |

### Transitions Distant from Kernel

1. chedy → ee
2. dy → aiin
3. dy → chey
4. or → dal
5. chey → chedy
6. chey → shedy
7. ar → dal
8. he → t
9. he → or
10. shedy → aiin

**Critical Finding:**
- **OPS claims:** "KERNEL_ADJACENT clustering"
- **Actual:** 59% (10/17) are distant from kernel
- No forbidden transition directly involves kernel nodes (k, h, e)
- Kernel adjacency is NOT structurally forced

**Verdict:** OPS kernel-adjacency claim is **FALSIFIED**

---

## SECTION E — COUNTERFACTUAL OUTCOMES

### Class-by-Class Removal Effects

| Class | Members | Corpus Impact | Effect of Removal |
|-------|---------|---------------|-------------------|
| PHASE_ORDERING | 7 | 24 | **BREAKS** corpus blocking |
| COMPOSITION_JUMP | 4 | 34 | **BREAKS** corpus blocking |
| CONTAINMENT_TIMING | 4 | 0 | No effect (theoretical only) |
| RATE_MISMATCH | 1 | 14 | **BREAKS** corpus blocking |
| ENERGY_OVERSHOOT | 1 | 12 | **BREAKS** corpus blocking |

### Removal Summary

| Outcome | Classes |
|---------|---------|
| Corpus-necessary (removal breaks blocking) | PHASE_ORDERING, COMPOSITION_JUMP, RATE_MISMATCH, ENERGY_OVERSHOOT |
| Theoretical-only (removal has no corpus effect) | **CONTAINMENT_TIMING** |

**Critical Finding:**
- CONTAINMENT_TIMING has **0 corpus impact**
- All 4 members (c→ee, he→t, he→or, shedy→o) have reverse=0
- This class is entirely theoretical with no observable corpus constraint
- Removal would NOT change any execution detection or convergence behavior

---

## SECTION F — SEL-D VERDICT

### Test Summary

| Test | Result | OPS Claim Status |
|------|--------|------------------|
| T1 - Principality | 14/17 unique, 3 redundant | **WEAKENED** |
| T2 - Class Minimality | 2 single-member classes | **OVER_PARTITIONED** |
| T3 - Bidirectionality | 11/17 asymmetric | **PARTIALLY FALSIFIED** |
| T4 - Kernel Adjacency | 10/17 distant | **FALSIFIED** |
| T5 - Counterfactual | 1 theoretical-only class | **WEAKENED** |

### Hazard Topology Status

| Claim | Prior Tier | New Status |
|-------|------------|------------|
| "17 forbidden transitions" | Tier 0 | **STABLE** (count confirmed) |
| "5 failure classes" | Tier 0 | **WEAKEN to Tier 2** (reducible to 3-4) |
| "100% bidirectional" | Tier 0 | **FALSIFIED** (65% asymmetric) |
| "KERNEL_ADJACENT clustering" | Tier 0 | **FALSIFIED** (59% distant) |
| "All hazards are active constraints" | Tier 0 | **WEAKEN** (1 class theoretical-only) |

### Structural Changes Justified

1. **Merge RATE_MISMATCH + ENERGY_OVERSHOOT** → single "MISCELLANEOUS" class
   - Both have 1 member each
   - Jaccard overlap = 0.333
   - No unique structural identity

2. **Downgrade CONTAINMENT_TIMING** → optional/theoretical
   - 0 corpus impact
   - All 4 members have reverse=0
   - Removal would not change any detection

3. **Reclassify bidirectionality** → "asymmetric" or "causal_hazard"
   - 65% show directional corpus evidence
   - Not mutual exclusions; they are one-way gates

4. **Remove kernel-adjacency claim**
   - 59% are distant from kernel
   - No structural forcing detected

### Hazard Count Reduction

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Classes | 5 | 3-4 | -20% to -40% |
| Structural claims | 4 | 1 | -75% |
| Tier 0 hazard claims | 5 | 1 | -80% |

### Hazard Pillar Status

**Prior:** Tier 0 (FROZEN FACT)

**Revised:** Tier 2 (STRUCTURAL INFERENCE)

**Rationale:**
- Only 1 claim survives intact: "17 forbidden transitions exist"
- All characterization claims (bidirectionality, kernel-adjacency, class necessity) fail testing
- The hazard *count* is stable; the hazard *interpretation* is not

### Data Integrity Alert

**CRITICAL:** `hazards.py` implements wrong transitions

- 7/17 transitions differ from Phase 18A canonical
- 4 implemented transitions are **violated** in corpus
- This requires immediate remediation

---

## Summary Statement

> **The hazard topology as COUNTED (17 transitions) survives.**
> **The hazard topology as CHARACTERIZED (bidirectional, kernel-adjacent, 5-class, all-active) does not survive.**
>
> Required changes:
> - Downgrade hazard pillar from Tier 0 to Tier 2
> - Merge or eliminate 2 single-member classes
> - Revise bidirectionality claim (65% asymmetric)
> - Remove kernel-adjacency claim (59% distant)
> - Flag CONTAINMENT_TIMING as theoretical-only
> - Fix hazards.py implementation to match Phase 18A

---

*SEL-D complete. Multiple claims weakened or falsified.*

*Generated: 2026-01-05*
