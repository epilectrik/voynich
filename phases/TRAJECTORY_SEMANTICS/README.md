# TRAJECTORY_SEMANTICS Phase

**Status:** PRE-REGISTERED
**Date:** 2026-01-19
**Purpose:** Test trajectory semantics beyond the token semantic ceiling

---

## Motivation

The SEMANTIC_CEILING_BREACH phase confirmed that **token semantics** are irrecoverable by design. However, the expert-advisor identified unexplored territory in **trajectory semantics** - characterizing how constraint pressure evolves through procedural sequences.

Three pressure vectors were identified:

1. **Vector C (Gradient Steepness):** Zone transition dynamics - not WHERE but HOW FAST
2. **Vector A (Interface Theory):** Operator judgment availability by zone
3. **Vector B (Multi-Modality):** Modality mixtures and transitions (optional)

---

## Pre-Registered Hypotheses

### Vector C: Gradient Steepness

**H-C1:** Transition velocity (steps per zone change) differs significantly by REGIME.
- Prediction: PRECISION has sharpest transitions; GENTLE has smoothest

**H-C2:** Commitment sharpness (R→S transition steepness) correlates with REGIME_4 membership.
- Prediction: r > 0.3

**H-C3:** Setup duration (steps before R-zone) differs by REGIME.
- Prediction: GENTLE > others (t-test significant)

**H-C4:** Gradient steepness correlates with HT density.
- Prediction: Steeper gradients → higher HT (r > 0.25)

### Vector A: Interface Theory

**H-A1:** Judgment availability matrix shows >70% non-uniform distribution.
- At least 9/13 judgments have non-uniform zone distribution

**H-A2:** At least 3 judgments show significant zone restriction.
- χ² p < 0.01 for each

**H-A3:** HT density correlates with judgment count per zone.
- Higher judgment load → higher HT (r > 0.3)

### Vector B: Multi-Modality (Optional)

**H-B1:** Recipes with multiple modalities have higher zone entropy.
- More modalities → more spread across zones

**H-B2:** S-zone approach correlates with modality narrowing.
- Fewer active modalities as S-zone is reached

---

## Success Criteria

### Tier 2 Upgrade (ALL required)

- H-C1, H-C2, H-C3, H-C4: 3/4 confirmed at p < 0.01
- H-A1: >70% non-uniformity confirmed
- H-A2: ≥3 judgments with significant restriction

### Tier 3 Enrichment

- Vector C: 2/4 predictions confirmed at p < 0.05
- Vector A: Partial non-uniformity with interpretable pattern

### FALSIFIED

- Vector C: No REGIME differentiation (all p > 0.10)
- Vector A: Uniform judgment distribution across zones

---

## Constraint Compliance

| Constraint | How Respected |
|------------|---------------|
| **C384** | Labels trajectories and phases, not tokens |
| **C434** | Uses R-series ordering as foundation |
| **C443** | Extends escape gradients with temporal dimension |
| **C469** | Judgment availability is categorical |

---

## Data Sources

| File | Purpose |
|------|---------|
| `data/brunschwig_materials_master.json` | Step-by-step instruction sequences |
| `results/brunschwig_reverse_activation.json` | Zone affinity profiles |
| `results/enhanced_sensory_extraction.json` | Modality labels |
| `results/unified_folio_profiles.json` | HT density by folio |

---

## Scripts

| Script | Vector | Purpose |
|--------|--------|---------|
| `ts_01_gradient_steepness.py` | C | Transition dynamics metrics |
| `ts_02_judgment_zone_matrix.py` | A | Judgment availability matrix |
| `ts_03_multimodality.py` | B | Modality mixture analysis (optional) |
| `ts_04_synthesis.py` | All | Aggregate results and tier assessment |

---

*Pre-registration locked: 2026-01-19*
*No changes to hypotheses after first test execution*
