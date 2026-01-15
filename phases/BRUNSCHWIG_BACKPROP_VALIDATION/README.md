# BRUNSCHWIG_BACKPROP_VALIDATION Phase

**Date:** 2026-01-15 | **Status:** COMPLETE

---

## Purpose

Strengthen the bidirectional constraint story with **predictive tests** that stay within Tier 0-2 boundaries, avoiding semantic drift.

---

## Key Outcome: EXPLANATORY SATURATION

The frozen architecture **predicted** these results without requiring changes. This is the best possible outcome:

> **The model is saturated, not brittle.**

No new constraints were added. All results slot as **FITS** (demonstrations of explanatory power), not architectural necessities.

---

## Test Results Summary

### Core Tests (Predictive)

| # | Test | Result | Key Finding |
|---|------|--------|-------------|
| 1 | Forward Blind Prediction | **SUCCESS** | 8/8 predictions correct |
| 2 | Degree-REGIME Violation Matrix | SUCCESS | All 3 questions CONFIRMED |
| 3 | Section Distribution by REGIME | SUCCESS | χ²=60951, p≈0 significant |
| 4 | Multi-Recipe Compliance | SUCCESS | 3/3 recipes comply with C332 |

### Tier A Defensive Tests

| # | Test | Result | Key Finding |
|---|------|--------|-------------|
| A-1 | Stability Under Perturbation | SUCCESS | Robust to tail/hub perturbation |
| A-2 | AZC Projection Invariance | CONFIRMED | r=0.036, axes orthogonal |
| A-3 | Synthetic Property Control | **NEGATIVE** | Property model cannot reproduce structure |

---

## Fits Added (NOT Constraints)

These results are tracked in `context/MODEL_FITS/fits_brunschwig.md`:

| ID | Fit | Tier | Status |
|----|-----|------|--------|
| F-BRU-001 | Brunschwig Product Type Prediction (Blind) | F3 | SUCCESS |
| F-BRU-002 | Degree-REGIME Boundary Asymmetry | F3 | SUCCESS |
| F-BRU-003 | Property-Based Generator Rejection | F2 | NEGATIVE |
| F-BRU-004 | A-Register Cluster Stability | F2 | SUCCESS |
| F-BRU-005 | MIDDLE Hierarchical Structure | F2 | SUCCESS |

### Why Fits, Not Constraints

Per expert governance:

- **Constraints** = things that *must* be true for the system to exist
- **Fits** = things that *happen to be true* given this manuscript and world
- These tests answer: "Does the model explain reality?" not "What must the model contain?"

The frozen constraint table (353 entries) remains **unchanged**.

---

## Key Interpretive Result

**The definitive interpretation (now well-defended):**

> Currier A registers enumerate stable regions of a high-dimensional incompatibility manifold that arise when materials, handling constraints, process phase, and recoverability jointly constrain what must not be confused.

This is NOT:
- Individual materials
- Species names
- Scalar properties
- Broad material classes

This IS:
- Configurational regions in constraint space
- Defined by what must be distinguished
- Hierarchical vocabulary structure

---

## Negative Knowledge (F-BRU-003)

The synthetic property control **permanently kills** an entire class of interpretations:

| Metric | Voynich | Property Model |
|--------|---------|----------------|
| Uniqueness | **72.7%** | 41.5% |
| Hub/Tail ratio | 0.006 | 0.091 |
| Clusters | 33 | 56 |

MIDDLEs do NOT encode:
- Aromatic vs medicinal properties
- Material class membership
- Any smooth property partition

---

## Semantic Risk Guardrails

**DO:**
- Test constraints and boundaries
- Use structural predictions
- Log what violations occur
- Describe geometric patterns, not semantic meanings

**DO NOT:**
- Assign semantic meaning to prefixes
- Label individual folios by product
- Assert procedural sequence order
- Read property semantics into clusters

---

## Files

| Script | Purpose | Fit |
|--------|---------|-----|
| `blind_prediction_test.py` | Test 1 - Forward prediction | F-BRU-001 |
| `degree_regime_violations.py` | Test 2 - Violation matrix | F-BRU-002 |
| `azc_zone_bias_test.py` | Test 3 - Section distribution | (supporting) |
| `multi_recipe_compliance.py` | Test 4 - Additional recipes | (supporting) |
| `stability_perturbation_test.py` | A-1 Robustness | F-BRU-004 |
| `azc_projection_invariance.py` | A-2 Orthogonality | (supporting) |
| `synthetic_property_control.py` | A-3 Negative control | F-BRU-003 |
| `cross_type_middle_analysis.py` | Hierarchy analysis | F-BRU-005 |

---

## Verdict

**Phase complete. Model unchanged. Explanatory power confirmed.**

The structure explains itself more strongly than any semantic hypothesis could. The remaining work is:
- Documentation ✓
- Clarification ✓
- Defensive testing ✓
- Visualization (future)
- Narrative discipline (ongoing)

---

*Phase completed 2026-01-15*
