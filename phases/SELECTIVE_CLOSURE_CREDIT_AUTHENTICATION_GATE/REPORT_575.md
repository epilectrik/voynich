# Phase 575: SELECTIVE CLOSURE CREDIT + AUTHENTICATION GATE

## Summary

Authentication gate internalizing Phase 574's counterfeit-closure threshold as an online apparatus parameter. Four constraints (C1647-C1650) produced.

**Best gate configuration:** CONSERVATIVE
**SSI (Surgical Selectivity Index):** 0.0000

## Constraint Verdicts

| ID | Verdict | Pass? |
|------|---------|-------|
| C1647 (ACS Configuration) | CONFIGURATION_ACS_VALIDATED | YES |
| C1648 (Two-Layer Gate) | TWO_LAYER_GATE_SYNERGISTIC | YES |
| C1649 (Event-Band Stratification) | STRATIFIED_SELECTIVITY_REJECTED | PARTIAL/NO |
| C1650 (Landscape Shift) | LANDSCAPE_POLE_AGGRAVATED | PARTIAL/NO |

## T0: ACS Assembly

- Events: 463
- Signature table coverage: 86.6%
- CTS-ACS Spearman rho: 0.8045
- ACS discrimination gap: 0.2704 (vs CTS: 0.1012)
- Empirical A2 thresholds: CONSERVATIVE=0.35656, MODERATE=0.32422, AGGRESSIVE=0.38524

## T1: Authenticated Apparatus

- Identity check (threshold=0): PASS
- Zero-auth check (threshold=999): FAIL
- Both-layers synergy: FAIL

## T2: Gated Simulation

- Configurations tested: 5
- Total runs: 2280
- Elapsed: 54.74s

### Profile Summary (best config: CONSERVATIVE)

- **A1_BATH_REFLUX**: delta_adv=-0.0016, CCS1_red=-11.6%, improved/degraded=6/10
- **A2_SEALED_RECIRCULATION**: delta_adv=-0.0057, CCS1_red=-1.6%, improved/degraded=8/9
- **A3_DISTILL_COLLECT**: delta_adv=-0.0038, CCS1_red=-4.5%, improved/degraded=13/20

## T3: Surgical Selectivity

- Best config SSI: 0.0000
- FI reduction: 0.000000
- Strong-band loss: 0.005717
- Layer 1 delta: 0.003021
- Layer 2 incremental: 0.000538
- Combined delta: 0.003560
- Synergy: True

### Confusion Matrix (MODERATE)

- TP (counterfeitable correctly starved): 0
- TN (resistant correctly spared): 5
- FP (resistant incorrectly starved): 0
- FN (counterfeitable incorrectly spared): 5

## T4: Landscape Remapping

- A2 FORGIVING: 8 -> 8 (0.0% reduction)
- Total FORGIVING: 9 -> 10
- New A1/A3 FORGIVING: 1

### Transition Matrix

| From \ To | STABLE_AMPLIFIER | THRESHOLD_DEPENDENT | FORGIVING_RECIRCULATOR |
|-----------|------------------|--------------------|-----------------------|
| STABLE_AMPLIFIER | 10 | 9 | 0 |
| THRESHOLD_DEPENDENT | 1 | 46 | 1 |
| FORGIVING_RECIRCULATOR | 0 | 0 | 9 |

## Tier 3 Interpretation

> Tier 3 interpretation NOT frozen. Non-validated constraints: C1649=STRATIFIED_SELECTIVITY_REJECTED, C1650=LANDSCAPE_POLE_AGGRAVATED. The authentication gate shows mixed effectiveness. Further iteration may be needed.

*Generated: 2026-03-11T02:57:27.430147+00:00*
