# Phase 576: CLOSURE REGIME ADMISSION GATE

**Status:** COMPLETE
**Phase:** 576
**Constraints:** C1651-C1654
**Depends on:** Phase 572 (apparatus), Phase 574 (signatures), Phase 575 (failed scalar gate)

## Purpose

Gate closure regime admission (R1-R5) based on packet legitimacy, not just downstream Y-credit. Phase 575 proved that gating Layer 3 (Y-credit) after closure is already admitted is insufficient. Phase 576 gates Layer 2 (whether `_apply_close_recovery` fires at all).

## Architecture

- **Two-stage gate:** admit_mult (regime admission) + credit_mult (yield credit)
- **6-class tiered classifier:** AUTH_RESISTANT, AUTH_COUNTERFEITABLE, AUTH_THRESHOLD, AUTH_PROTECTIVE, AUTH_PRONE, AUTH_AMBIGUOUS
- **Burden conditioning:** no real containment burden → no closure regime admission
- **5 configs:** REGIME_GATED, REGIME_LENIENT, REGIME_STRICT, REGIME_AMB_PESSIMISTIC, CREDIT_ONLY (control)
- **Best config:** REGIME_AMB_PESSIMISTIC (SSI=63.5, A2 delta_adv=+0.0635)
- **Architecture robust:** 4/4 regime configs beat CREDIT_ONLY

## Scripts

| Script | Purpose | Runtime |
|--------|---------|---------|
| `t0_corpus_classification.py` | Tiered classification + burden calibration | ~1s |
| `t1_closure_admission_apparatus.py` | ClosureAdmissionApparatus + verification | <1s |
| `t2_admission_simulation.py` | Full simulation (5 configs × 76 folios × 6 runs) | ~55s |
| `t3_gate_anatomy.py` | Signature battery + config robustness | <1s |
| `t4_landscape_remap.py` | Post-gate landscape | <1s |
| `t5_synthesis.py` | Integration + C1651-C1654 | <1s |

## Constraints

| ID | Subject | Verdict |
|----|---------|---------|
| C1651 | Tiered Classification | CLASSIFICATION_PARTIAL |
| C1652 | Regime Admission Selectivity (decisive) | ADMISSION_SELECTIVE |
| C1653 | Event-Band Discrimination | DISCRIMINATION_PARTIAL |
| C1654 | Landscape + CCS1 | LANDSCAPE_STABLE |
