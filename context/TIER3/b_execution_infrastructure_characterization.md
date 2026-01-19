# B Execution Infrastructure Characterization (BCI)

**Tier:** 3 (Structural Characterization)
**Status:** CHARACTERIZED
**Date:** 2026-01-18
**Phase:** BCI (B-Class Infrastructure Characterization)

---

## Summary Statement

Currier B contains execution-infrastructure roles that are not primitives but are structurally required for almost all programs. They mediate kernel control, show limited context sensitivity, and lie outside AZC's scope of constraint. This layer is characterized but not promoted to a new constraint.

---

## Discovery Context

During development of the constraint flow visualizer, we observed that AZC-activating bundles were blocking ALL B programs. Investigation revealed:

1. Certain instruction classes (AUXILIARY role) were being pruned by AZC vocabulary filtering
2. These classes are required in 80-81/82 B folios (96-99% coverage)
3. Their removal collapses B reachability entirely
4. They are NOT kernel primitives (not atomic, not boundary-adjacent to forbidden transitions)

This prompted the BCI characterization phase to understand their structural role.

---

## What Is Established (Tier 2-3)

### Hard Facts (Directly Supported by Tests)

1. **There exists a subset of Currier B instruction classes required for almost all executable programs**
   - Evidence: 96-99% B folio coverage (Phase 4)
   - Evidence: Removal collapses reachability (Phase 1)
   - Evidence: Grammar itself remains viable (Phase 3)

2. **These classes are not kernel primitives**
   - Not atomic operators
   - Not forbidden-transition adjacent
   - Not hazard-defining
   - Composed of MIDDLE-labeled roles

3. **They are not neutral carriers**
   - 70.6% cluster within 0-2 tokens of kernel operators (k/h/e)
   - They mediate execution, not just exist

4. **They are partially sensitive to REGIME and AZC zone**
   - One class fully invariant across REGIMEs
   - Others show REGIME_4 (precision) sensitivity
   - All thin sharply in S-zone (late commitment)

5. **They exhibit redundancy and threshold behavior**
   - Reachability recovers at ≥50% immunity
   - Redundancy between primary infrastructure classes is structural

---

## BCI Test Results

### Test 1: REGIME Invariance

**Question:** Do infrastructure classes appear equally across REGIME_1-4?

| Class | REGIME_1 | REGIME_2 | REGIME_3 | REGIME_4 | Spread | Verdict |
|-------|----------|----------|----------|----------|--------|---------|
| 36 | 100% | 90% | 100% | 92% | 10% | SENSITIVE |
| 42 | 90% | 90% | 88% | 76% | 14% | SENSITIVE |
| 44 | 100% | 100% | 94% | 96% | 6% | SENSITIVE |
| 46 | 100% | 100% | 100% | 96% | 4% | **INVARIANT** |

**Finding:** Only class 46 is truly REGIME-invariant (spread < 5%). Class 42 shows highest sensitivity, dropping to 76% in REGIME_4 (precision/brittle folios).

---

### Test 2: Kernel Interaction Profile

**Question:** Do infrastructure classes cluster temporally around kernel operators (k, h, e)?

| Class | Occurrences | Mean Distance | Near (0-2) | Verdict |
|-------|-------------|---------------|------------|---------|
| 36 | 1,827 | **0.89** tokens | **89.2%** | TIGHT CLUSTERING |
| 44 | 886 | 3.33 tokens | 57.8% | MODERATE CLUSTERING |
| 46 | 1,068 | 3.47 tokens | 57.2% | MODERATE CLUSTERING |
| 42 | 314 | 4.57 tokens | 44.3% | WEAK CLUSTERING |

**Overall:** 70.6% of infrastructure class occurrences appear within 2 tokens of a kernel operator.

**Finding:** Infrastructure classes are MEDIATORS, not neutral carriers. They cluster near kernel operations, suggesting active participation in control flow.

---

### Test 3: Connectivity vs Modulation

**Question:** Do infrastructure classes enable paths (binary) or modulate path density?

**Result:** UNINFORMATIVE
- Folios WITH infrastructure: 82/82 (100%)
- Folios WITHOUT infrastructure: 0

**Finding:** Infrastructure is UNIVERSAL - present in all B folios. This itself confirms their role as execution prerequisites, but prevents comparative density analysis.

---

### Test 4: AZC Zone Sensitivity

**Question:** Are infrastructure classes equally present across C/P/R/S zones?

| Zone | MIDDLEs Legal | Rate |
|------|---------------|------|
| C | 7/16 | 43.8% |
| P | 7/16 | 43.8% |
| R | 7/16 | 43.8% |
| S | 3/16 | **18.8%** |

**Spread (C - S):** 25%

**Finding:** FOLLOWS ESCAPE GRADIENT. Infrastructure MIDDLEs thin sharply in S-zone (late commitment), matching the general escape gradient documented in C443. Infrastructure is zone-sensitive, not zone-invariant.

---

### Test 5: Removal Gradient (Perturbation Sensitivity)

**Question:** Does partial infrastructure removal have linear or nonlinear effects?

| Immunity Level | Avg Reachable B Folios | Deviation from Linear |
|----------------|------------------------|----------------------|
| 0% | 9.2 | baseline |
| 25% | 13.4 | -26% |
| 50% | **44.9** | **+66%** |
| 75% | 44.9 | +25% |
| 100% | 44.9 | baseline |

**Finding:** NONLINEAR (THRESHOLD at 50%). Reachability does not degrade linearly. Once 50% infrastructure immunity is achieved, full reachability is restored. This indicates redundancy between primary infrastructure classes - they can substitute for each other.

---

## Structural Characterization Summary

| Property | Class 46 | Class 44 | Class 36 | Class 42 |
|----------|----------|----------|----------|----------|
| B Coverage | 99% | 98% | 96% | 85% |
| REGIME Invariant | **YES** | borderline | no | no |
| Kernel Proximity | moderate | moderate | **tight** | weak |
| Delta When Immune | +80 | +157 | +3 | +67 |
| Infrastructure Tier | PRIMARY | PRIMARY | SECONDARY | SECONDARY |

**Hierarchy:**
1. **Class 46** = True infrastructure (regime-invariant, kernel-mediating)
2. **Class 44** = Near-infrastructure (slight regime sensitivity, highest reachability impact)
3. **Class 36** = Tight kernel-coupling (89% within 2 tokens) but regime-variable
4. **Class 42** = Weakest candidate (drops 14% in brittle regimes, weakest kernel coupling)

---

## What This Does NOT Claim

- **No specific class identification in documentation** - We describe role behavior, not catalog membership
- **No semantic interpretation** - These are structural roles, not meaning-carriers
- **No Tier 2 constraint** - Behavior is derivable from existing constraints
- **No grammar primitive status** - These are execution infrastructure, not atomic operators

---

## Relationship to Existing Constraints

This characterization is **derivable from**:
- **C124** - B grammar 49-class structure
- **C485** - Hazard topology (17 forbidden transitions)
- **C411** - Kernel operator roles (k, h, e)
- **C458** - Design freedom asymmetry (hazard clamped, recovery free)

No new constraint is required. This is structural characterization within existing framework.

---

## Implementation Guidance

### For Tooling

When implementing AZC→B reachability:
- Do NOT prune instruction classes with >90% B folio coverage
- Treat high-coverage AUXILIARY classes as infrastructure
- Infrastructure removal should trigger warning, not silent failure

### For Analysis

When analyzing B program structure:
- Infrastructure classes are execution prerequisites, not content carriers
- Their presence is necessary but not informative about program semantics
- Their absence indicates structural invalidity, not variant program type

---

## Data Files

| Test | Output File |
|------|-------------|
| REGIME Invariance | `results/bci_regime_invariance.json` |
| Kernel Interaction | `results/bci_kernel_interaction.json` |
| Connectivity Modulation | `results/bci_connectivity_modulation.json` |
| Zone Sensitivity | `results/bci_zone_sensitivity.json` |
| Removal Gradient | `results/bci_removal_gradient.json` |

**Scripts:** `apps/constraint_flow_visualizer/scripts/bci_*.py`

---

## Navigation

<- [../MODEL_CONTEXT.md](../MODEL_CONTEXT.md) Section VI | ^ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
