# Phase 576: CLOSURE REGIME ADMISSION GATE

## Summary

Closure regime admission gate that gates Layer 2 (whether `_apply_close_recovery` fires at all) based on packet legitimacy class, CTS band, and containment burden. Phase 575 proved that gating Layer 3 (Y-credit) after closure is already admitted is insufficient. Phase 576 gates Layer 2 (closure regime admission R1-R5). Four constraints (C1651-C1654) produced.

**Best gate configuration:** REGIME_AMB_PESSIMISTIC
**SSI (Surgical Selectivity Index):** 63.5040
**Architecture robust:** ARCHITECTURE_ROBUST

## Constraint Verdicts

| ID | Subject | Verdict | Pass? |
|------|---------|---------|-------|
| C1651 | Tiered Classification | CLASSIFICATION_PARTIAL | PARTIAL/NO |
| C1652 | Regime Admission Selectivity | ADMISSION_SELECTIVE | YES |
| C1653 | Event-Band Discrimination | DISCRIMINATION_PARTIAL | PARTIAL/NO |
| C1654 | Landscape + CCS1 | LANDSCAPE_STABLE | PARTIAL/NO |

## T0: Tiered Classification + Burden Calibration

- Lines classified: 2323
- Classes populated: 6/6
- AUTH_AMBIGUOUS: 5.4%
- M1 event agreement: 76.0%
- Burden threshold: 0.05

### Class Distribution

| Class | Lines | % |
|-------|-------|---|
| AUTH_RESISTANT | 1409 | 60.6% |
| AUTH_COUNTERFEITABLE | 476 | 20.5% |
| AUTH_THRESHOLD | 140 | 6.0% |
| AUTH_PROTECTIVE | 128 | 5.5% |
| AUTH_PRONE | 44 | 1.9% |
| AUTH_AMBIGUOUS | 126 | 5.4% |

## T1: ClosureAdmissionApparatus Verification

- Identity check: PASS
- Full rejection check: PASS
- Credit-only control: PASS
- Regime admission: PASS
- Admit vs credit: PASS
- Burden conditioning: PASS

## T2: Full Simulation

- Configurations: 5
- Total runs: 2280
- Elapsed: 54.28s

### Profile Summary (best config: REGIME_AMB_PESSIMISTIC)

- **A1_BATH_REFLUX**: delta_adv=-0.0010, CCS1_red=3.8%, improved/degraded=0/0
- **A2_SEALED_RECIRCULATION**: delta_adv=0.0635, CCS1_red=66.2%, improved/degraded=0/0
- **A3_DISTILL_COLLECT**: delta_adv=0.0073, CCS1_red=30.9%, improved/degraded=0/0

## T3: Gate Anatomy + Config Robustness

- Best config SSI: 63.5040

### SSI per Config

| Config | SSI |
|--------|-----|
| REGIME_GATED | 52.5554 |
| REGIME_LENIENT | 53.4030 |
| REGIME_STRICT | 64.4694 |
| REGIME_AMB_PESSIMISTIC | 63.5040 |
| CREDIT_ONLY | 53.0292 |

### Confusion Matrix (REGIME_AMB_PESSIMISTIC)

- TP (CF correctly suppressed): 4/5
- TN (RESISTANT correctly preserved): 4/4
- FP (RESISTANT incorrectly harmed): 0
- FN (CF incorrectly spared): 1

### Config Robustness

- SSI > 1.0: 4/4 regime configs
- TN >= 4/5: 4/4 regime configs
- Beat CREDIT_ONLY: 4/4 regime configs
- All regime beat CREDIT_ONLY: True
- Architecture robust: True
- Assessment: **ARCHITECTURE_ROBUST**

### AMB_PESSIMISTIC Comparison

- AMB_PESSIMISTIC SSI: 63.5040
- REGIME_GATED SSI: 52.5554
- Pessimistic better: True
- Interpretation: Base AUTH_AMBIGUOUS too generous

## T4: Landscape Remapping

- A2 FORGIVING: 8 -> 8 (0.0% reduction)
- New A1/A3 FORGIVING: 0
- CCS1 reduction: 66.2%

### Transition Matrix

| From \ To | STABLE_AMPLIFIER | THRESHOLD_DEPENDENT | FORGIVING_RECIRCULATOR |
|-----------|------------------|--------------------|-----------------------|
| STABLE_AMPLIFIER | 9 | 10 | 0 |
| THRESHOLD_DEPENDENT | 3 | 45 | 0 |
| FORGIVING_RECIRCULATOR | 0 | 0 | 9 |

## Tier 3 Interpretation

> Tier 3 interpretation NOT frozen. Non-validated constraints: C1651=CLASSIFICATION_PARTIAL, C1653=DISCRIMINATION_PARTIAL, C1654=LANDSCAPE_STABLE. The closure regime admission gate shows partial effectiveness. Architecture assessment: ARCHITECTURE_ROBUST. The regime admission concept may be sound but tuning or architecture changes needed.

*Generated: 2026-03-11T04:28:38.938456+00:00*
