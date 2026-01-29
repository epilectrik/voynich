# LANE_CHANGE_HOLD_ANALYSIS

**Status:** COMPLETE | **Date:** 2026-01-26

## Objective

Two-part research phase testing the functional architecture of QO and CHSH execution lanes:

1. **PP Discrimination Test** -- Which Currier A PP MIDDLEs predict QO vs CHSH lane preference?
2. **Change/Hold Validation** -- Test the control-theoretic interpretation that CHSH = state-changing intervention, QO = state-preserving/stabilizing intervention.

## Key Findings

### PP Lane Discrimination (Script 1)

**Verdict: DISCRETE_SIGNATURE** -- 20/99 PP MIDDLEs significantly predict lane preference (FDR < 0.05, z = 24.26).

- QO-enriched MIDDLEs: k/t-based, ENERGY_OPERATOR role (11/15), AZC-Mediated (12/15)
- CHSH-enriched MIDDLEs: o-based, AUXILIARY role (3/5)
- 17/20 EN-associated (partially tautological); 3 non-EN novel discriminators
- No obligatory lane-exclusive slots; signal is probabilistic

### Change/Hold Validation (Script 2)

**Verdict: MODERATE (3/5)** under original framing. **5/5 consistent** under reversed interpretation.

| Test | Prediction | Result | Note |
|------|-----------|--------|------|
| Kernel co-occurrence | QO -> more e, CHSH -> more k/h | **REJECTED** | QO has 70.7% k, CHSH has 68.7% e (reversed) |
| Transition stability | QO more stable | **CONFIRMED** | p = 0.0006, r = -0.039 |
| Recovery routing | QO dominates post-hazard | **REJECTED** | CHSH = 75.2% post-hazard (reversed) |
| Hazard proximity | CHSH closer | **CONFIRMED** | p = 0.002, r = 0.072 |
| Hysteresis oscillation | Alternation > chance | **CONFIRMED** | 0.563 vs 0.494, p < 0.0001 |

### Critical Reinterpretation

The "Change/Hold" label (QO = hold, CHSH = change) is **FALSIFIED** in its literal form. The data supports a reversed mapping:

- **QO = Controlled Energy Addition** -- QO carries k (ENERGY_MODULATOR) at 70.7%, has zero hazard participation (C601), operates in stable contexts
- **CHSH = Stabilization/Correction** -- CHSH carries e (STABILITY_ANCHOR) at 68.7%, dominates post-hazard recovery (75.2%), operates in variable contexts

This resolves all five findings and is consistent with all Tier 0-2 constraints. F-B-002 ("QO = safe energy pathway") is **validated** as controlled energy application, not energy absence.

### Hysteresis Pattern

Lane alternation is elevated (0.563 vs 0.494 null), with short runs (median 1.0 for both lanes). Section variation: BIO = 0.606 (highest oscillation), HERBAL_B = 0.427 (lowest). This is consistent with bang-bang temperature control in a system without reliable thermometry.

## Constraints Produced

| # | Name | Tier |
|---|------|------|
| C643 | Lane Hysteresis Oscillation | 2 |
| C644 | QO Transition Stability | 2 |
| C645 | CHSH Post-Hazard Dominance | 2 |
| C646 | PP-Lane MIDDLE Discrimination | 2 |
| C647 | Morphological Lane Signature | 2 |

## Fits Produced

| ID | Name | Tier | Result |
|----|------|------|--------|
| F-B-004 | Lane Hysteresis Control Model | F2 | SUCCESS |
| F-B-005 | PP-Lane MIDDLE Discrimination | F2 | SUCCESS |
| F-B-006 | Energy/Stabilization Lane Assignment | F3 | PARTIAL |

F-B-002 annotated (not revised): "safe energy" = controlled energy addition confirmed.

## Expert-Advisor Assessment

- No Tier 0-2 conflicts
- Hysteresis and morphological lane signature are robust Tier 2
- "Change/Hold" label falsified (Tier 1); reversed "Energy/Stabilization" is Tier 3
- C574 (QO/CHSH grammatically identical) refined: successor distributions identical, but stability asymmetry exists
- C522 (construction-execution independence) is critical: MIDDLE content reflects vocabulary heritage, not runtime behavior

## Scripts

| Script | Purpose | Results |
|--------|---------|---------|
| `scripts/lane_pp_discrimination.py` | PP MIDDLE lane prediction | `results/lane_pp_discrimination.json` |
| `scripts/change_hold_validation.py` | Change/Hold 5-prediction test | `results/change_hold_validation.json` |

## Data Dependencies

- middle_classes_v2_backup.json (A_INTERNAL_STRATIFICATION)
- pp_classification.json (PP_CLASSIFICATION)
- pp_role_foundation.json (A_TO_B_ROLE_PROJECTION)
- population_profiles.json (A_TO_B_ROLE_PROJECTION)
- en_census.json (EN_ANATOMY)
- class_token_map.json (CLASS_COSURVIVAL_TEST)
