# Brunschwig Backpropagation Fits

**Phase:** BRUNSCHWIG_BACKPROP_VALIDATION
**Date:** 2026-01-15
**Status:** COMPLETE

---

## Purpose

These fits demonstrate the explanatory power of the frozen constraint system by showing that:
1. Historical distillation procedures align with inferred product types
2. Alternative interpretations (property-based) fail to reproduce observed structure
3. The geometric/manifold interpretation is stable under perturbation

**WARNING:** These are FITs, not constraints. They show *what happens to be true* given this manuscript and this external corpus. They do not define architectural necessity.

---

## F-BRU-001: Brunschwig Product Type Prediction (Blind)

**Tier:** F3 (External Alignment)
**Scope:** A
**Result:** SUCCESS
**Supports:** C475, C476

### Method
Pre-registered predictions for 3 Brunschwig recipes, locked before execution:
- Lavender water (1st degree) → WATER_GENTLE
- Sage water (2nd degree) → WATER_STANDARD
- Juniper oil (3rd degree) → OIL_RESIN

### Finding
8/8 signature predictions correct. Product type correctly predicts PREFIX profile without circularity.

### Status
✔ Real, strong, falsifiable
✖ Depends on one external corpus (Brunschwig)
✖ Not architecturally necessary

---

## F-BRU-002: Degree-REGIME Boundary Asymmetry

**Tier:** F3 (Structural Characterization)
**Scope:** B
**Result:** SUCCESS
**Supports:** C179-C185, C458

### Method
Tested whether Brunschwig degree profiles can fit REGIME constraints:
- Can Degree 1 violate R3? → YES (insufficient e_ops)
- Can Degree 4 fit R2? → NO (k exceeds max)
- Can Degree 3 fit R4? → NO (HIGH_IMPACT forbidden)

### Finding
All 3 questions CONFIRMED. Violations are asymmetric (not nested structure).

### Status
✔ Real, boundary-defining
⚠ Borderline constraint-eligible
✖ Empirically described, not architecturally forced

**Correct handling:** Refinement note attached to REGIME block, not new constraint.

---

## F-BRU-003: Property-Based Generator Rejection

**Tier:** F2 (Negative Knowledge)
**Scope:** A
**Result:** NEGATIVE
**Supports:** C475, C476

### Method
Synthetic property-based registry with:
- 8 "properties"
- Smooth overlap
- Zipf-like frequencies

Tested against same metrics as Voynich.

### Finding
Property model FAILS to reproduce Voynich structure:

| Metric | Voynich | Property Model |
|--------|---------|----------------|
| Uniqueness | 72.7% | 41.5% |
| Hub/Tail ratio | 0.006 | 0.091 |
| Clusters | 33 | 56 |

### Status
✔ Real, methodologically strong
✔ Permanently kills property/low-rank interpretations
✖ Negative knowledge, not positive constraint

**Correct handling:** Document as generator rejection, link to C475/C476 as evidentiary support. Do NOT mint new constraint.

---

## F-BRU-004: A-Register Cluster Stability

**Tier:** F2 (Robustness Characterization)
**Scope:** A
**Result:** SUCCESS
**Supports:** C481

### Method
Perturbation tests on WATER_GENTLE clusters:
- Tail removal (10-20%)
- Hub downweight (30-50%)
- Random removal (10-20%)

### Finding
Clusters robust to artifact-indicating perturbations:
- Tail removal: 100% survival
- Hub downweight: 100% survival
- Random removal: Degrades (expected - vocabulary-dependent)

### Status
✔ Real, good defensive test
✖ Characterization, not necessity
✖ Clusters could exist or not without breaking architecture

**Correct handling:** Registry geometry stability fit, useful for robustness arguments.

---

## F-BRU-005: MIDDLE Hierarchical Structure

**Tier:** F2 (Characterization)
**Scope:** A
**Result:** SUCCESS
**Supports:** C383, C475

### Method
Cross-type MIDDLE analysis measuring sharing patterns.

### Finding
Hierarchical vocabulary structure confirmed:

| Layer | Count | % | Meaning |
|-------|-------|---|---------|
| Universal | 106 | 3.5% | Connective infrastructure |
| Cross-cutting | 480 | 15.7% | Shared constraint dimensions |
| Type-specific | 2,474 | 80.8% | Local coordinates |

### Status
✔ Real, quantifies existing implications
✖ Already implicit in C383, C475, C476
✖ Adds clarity, not new rule

**Correct handling:** Fold into C383/C475 documentation, not separate constraint.

---

## Governance Note

None of these fits justify new Tier 0-2 constraints. This is the **best possible outcome**: the frozen architecture predicted these results without requiring changes.

> The model is saturated, not brittle.

---

## Files

All test scripts in: `phases/BRUNSCHWIG_BACKPROP_VALIDATION/`

| Script | Fit |
|--------|-----|
| `blind_prediction_test.py` | F-BRU-001 |
| `degree_regime_violations.py` | F-BRU-002 |
| `synthetic_property_control.py` | F-BRU-003 |
| `stability_perturbation_test.py` | F-BRU-004 |
| `cross_type_middle_analysis.py` | F-BRU-005 |
