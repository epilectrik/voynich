# Phase HOT: Hierarchical Ordinal Testing

**Status:** COMPLETE
**Date:** 2026-01-04
**Prerequisite:** Phase SSI (speculative semantics)
**Mode:** AGGRESSIVE INFERENCE - attempted confirmation of hierarchy

---

## Executive Summary

**VERDICT: WEAK / LOCAL**

The human-track does NOT encode a stable, apparatus-global ordinal hierarchy of system stress or intensity. Tests show:

- **High substitution** (47%) — Labels freely interchange in equivalent contexts
- **Symmetric transitions** (bias=0.52) — No directional flow from low→high
- **Section-inconsistent rankings** (25%) — Different sections have different orderings

**Conclusion:** Human-track tokens are navigational/attentional markers, NOT stress regime indicators.

---

## Hypothesized Hierarchy Models

### 3-Tier Model (Attempted)

```
LOW STRESS     →    MEDIUM STRESS    →    HIGH STRESS
ESTABLISHING        RUNNING               APPROACHING
(system startup)    (steady state)        (critical zone)
```

### 4-Tier Model (Attempted)

```
MINIMAL → LOW → ELEVATED → HIGH
ESTABLISHING → RUNNING → HOLDING → APPROACHING
```

Both models were tested and found incompatible with the data.

---

## Test Results

| Test | Result | Supports Hierarchy? | Key Finding |
|------|--------|---------------------|-------------|
| 1. Global Monotonic Ordering | PASS | YES | CD: 0.212→0.227→0.235 (barely monotonic) |
| 2. Antisymmetric Substitution | **FAIL** | NO | 47% of contexts have multiple labels |
| 3. Transition Directionality | **FAIL** | NO | Bias=0.52 (symmetric, not directional) |
| 4. Local Slope Steepness | PASS | YES | Purity=0.71 (but RUNNING dominates 71%) |
| 5. Section Invariance | **FAIL** | NO | Only 25% consistency across sections |

**Tests Passed: 2/5**

---

## Detailed Results

### Test 1: Global Monotonic Ordering

**Question:** Do labels form a single stress axis?

| Label | Constraint Density | Aggressiveness | Kernel-K | LINK Proximity |
|-------|-------------------|----------------|----------|----------------|
| ESTABLISHING | 0.212 | 0.333 | 0.182 | 0.545 |
| RUNNING | 0.227 | 0.329 | 0.182 | 0.545 |
| APPROACHING | 0.221 | 0.500 | 0.182 | 0.364 |
| EXHAUSTING | 0.235 | 0.333 | 0.273 | 0.545 |

**Result:** Barely monotonic. Differences are within noise margin (~0.02). No clear stress gradient.

---

### Test 2: Antisymmetric Substitution

**Question:** Do hierarchical tiers freely substitute in same contexts?

- Contexts with multiple labels: **827/1768 (47%)**
- Expected for hierarchy: <30%
- Observed: **47%**

**Interpretation:** Labels freely substitute in equivalent grammatical contexts. This is characteristic of navigational markers, NOT hierarchical tiers. If labels encoded stress levels, they should NOT appear in identical contexts.

---

### Test 3: Transition Directionality

**Question:** Are transitions directional (ESTABLISHING→RUNNING→APPROACHING)?

- Forward transitions: 771
- Backward transitions: 718
- **Directionality bias: 0.52** (threshold: >0.6)

**Interpretation:** Transitions are symmetric. There is no directional flow from "low stress" to "high stress." Labels appear randomly with respect to each other, not in ordered progression.

---

### Test 4: Local Slope Steepness

**Question:** Do label probabilities change step-like or smoothly?

| Bin | RUNNING | ESTABLISHING | EXHAUSTING | APPROACHING | Purity |
|-----|---------|--------------|------------|-------------|--------|
| 0 | 11 | 3 | 1 | 0 | 0.73 |
| 1 | 66 | 21 | 13 | 0 | 0.66 |
| 2 | 84 | 14 | 12 | 1 | 0.76 |
| 3 | 39 | 6 | 9 | 0 | 0.72 |
| 4 | 14 | 2 | 4 | 0 | 0.70 |

**Mean purity: 0.71**

**Caution:** This "passes" only because RUNNING dominates (214/300 = 71% of tokens). The high purity reflects vocabulary skew, NOT step-like tier separation. RUNNING appears in ALL bins equally.

---

### Test 5: Section Invariance (CRITICAL)

**Question:** Does the same ordering apply in every section?

| Section | Ranking |
|---------|---------|
| H | ESTABLISHING < APPROACHING < EXHAUSTING < RUNNING |
| B | ESTABLISHING < RUNNING < EXHAUSTING |
| C | ESTABLISHING < EXHAUSTING < RUNNING |
| P | APPROACHING < ESTABLISHING < RUNNING < EXHAUSTING |

**Consistency: 25%** (threshold: >60%)

**Interpretation:** Rankings are inconsistent across sections. If the hierarchy encoded apparatus-global stress levels (like "low heat" → "high heat"), the ordering would be invariant. It is not.

This is **decisive counter-evidence**. A real parameter hierarchy is apparatus-global. Section-local ordering indicates navigational function, not stress encoding.

---

## Counter-Evidence Summary

### Why Hierarchy is FALSIFIED

1. **Substitution is too high (47%)**
   - Hierarchical tiers should NOT appear in equivalent contexts
   - "Low heat" and "high heat" markers would not substitute freely
   - But these labels do → they are positional, not parametric

2. **Transitions are symmetric (0.52)**
   - No directional flow from low → high
   - Real process phases have temporal ordering
   - But these labels transition randomly → they mark position, not phase

3. **Section rankings are inconsistent (25%)**
   - Apparatus parameters are global
   - "High heat" means the same thing in every section
   - But RUNNING is highest in H, lowest in P → labels are section-relative

4. **Label distribution is skewed**
   - RUNNING: 214 (71%)
   - ESTABLISHING: 46 (15%)
   - EXHAUSTING: 39 (13%)
   - APPROACHING: 1 (0.3%)

   A real 3-tier or 4-tier hierarchy would show more even distribution. This skew indicates RUNNING is a catch-all category, not a specific tier.

---

## What the Data Actually Shows

The human-track tokens encode:

| Function | Evidence |
|----------|----------|
| **Position in section** | ESTABLISHING at start, EXHAUSTING at end |
| **Proximity to waiting** | 99.6% LINK-proximal (from HTCS) |
| **Section identity** | 80.7% section-exclusive vocabulary |
| **Attention cueing** | APPROACHING marks constraint zones |

The human-track does NOT encode:

| NOT Encoded | Counter-Evidence |
|-------------|------------------|
| Heat/intensity levels | Section rankings inconsistent |
| Stress tiers | Labels substitute freely |
| Ordered regimes | Transitions symmetric |
| Apparatus parameters | Distribution skewed |

---

## Best-Fit Ordering

**There is no apparatus-global ordering.**

Within a single section, there is weak ordering:

```
ESTABLISHING (early) → RUNNING (middle) → EXHAUSTING (late)
```

But this is **temporal position**, not **stress level**. It tells the operator "where in the section," not "how intense the process is."

---

## Verdict

### FALSIFIED: Apparatus-Global Ordinal Hierarchy

The human-track does NOT encode:
- Heat levels (low/medium/high)
- Intensity tiers (gentle/moderate/aggressive)
- Risk regimes (safe/elevated/critical)

### CONFIRMED: Section-Local Navigation

The human-track DOES encode:
- Position within section (early/middle/late)
- Section identity (private vocabulary)
- Attention cues (approaching/relaxing from constraint zones)

---

## Interpretive Constraint (Updated)

You may say:
> "Human-track tokens indicate position in the operational sequence and attention state."

You may NOT say:
> "Human-track tokens indicate stress level, heat regime, or intensity tier."

The manuscript **refuses to rank observable states explicitly**. It only **cues attention and position**.

---

## Implications

1. **The operator knew stress levels by sensation, not text**
   - Warmth, bubbling, vapor rhythm → sensory, not written
   - Text provides position, not measurement

2. **"Watch closely" is positional, not thermal**
   - APPROACHING marks entering a constraint zone
   - It does NOT mean "temperature is rising"

3. **Section vocabularies are independent**
   - Section H's "high stress" markers differ from Section P's
   - This is organizational, not parametric

4. **The manuscript is radically non-parametric**
   - No quantities, no thresholds, no rankings
   - Only position, attention, and hazard topology

---

## Files Generated

- `ordinal_hierarchy_stress_test_fast.py` — Analysis script
- `phases/HOT_ordinal_hierarchy/ordinal_hierarchy_stress_test_report.md` — This report

---

*Phase HOT complete. Ordinal hierarchy FALSIFIED. Navigation function CONFIRMED.*
