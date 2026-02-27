# C1372: Thermodynamic Arc Validation

**Tier:** 2 (ESTABLISHED — falsification result)
**Scope:** B
**Phase:** 485 (THERMODYNAMIC_ARC_VALIDATION)
**Depends on:** C1371, C1361, C1047, C1001, C1012, C1305, C1250

## Statement

A first-principles thermodynamic ordering model (STAGING < MARKING < CONTAINMENT < THERMAL < MONITORING < OPERATION < FLOW < TRANSITION) derived from distillation process logic **fails to predict** the observed 8-category quintile profiles (C1371). 0/7 formal tests pass. 6/7 directional predictions confirmed, but these are partially circular with C1371 findings. The thermodynamic model is 2.8x worse than a uniform null at predicting gradient shapes. **After controlling for PREFIX positional grammar (C1001), the category gradient signal collapses** — the "thermal arc" may be substantially a downstream consequence of PREFIX positional specialization rather than independent thermodynamic ordering.

## Key Findings

### Formal Test Results (0/7 pass)

| Test | Metric | Result | Threshold | Verdict |
|------|--------|--------|-----------|---------|
| T1 Rank correlation | rho=0.286, p=0.493 | Below threshold | rho≥0.60, p<0.05 | FAIL |
| T2 Shape classification | 2/8 correct | Below threshold | ≥5/8 | FAIL |
| T3 Superiority over null | MSE ratio=2.81 | Worse than null | ratio<0.80 | FAIL |
| T4 Cross-section stability | min rho=0.071 | Below threshold | min rho≥0.40 | FAIL |
| T5 OPERATION lag | lag=0.082, folio p=0.605 | Not significant | p<0.05, lag≥0.5 | FAIL |
| T6 MONITORING flat | CV=0.133, rank=5/8 | Not in bottom 3 | CV<0.15 AND rank≤3 | FAIL |
| T7 Pairwise ordering | 18/28 (64%) | Below threshold | ≥20/28 (71%) | FAIL |

### Directional Predictions (6/7 confirmed)

| # | Prediction | Result | Note |
|---|-----------|--------|------|
| P1 | THERMAL peaks Q1/Q2 | CONFIRMED (Q2) | Known from C1371 |
| P2 | FLOW monotonic rise (rho≥0.8) | CONFIRMED (rho=0.900) | Known from C1371 |
| P3 | STAGING front-loaded | CONFIRMED (ratio=1.155) | Novel |
| P4 | TRANSITION peaks Q5 | CONFIRMED | Known from C1371 |
| P5 | MONITORING flat (CV<0.15) | CONFIRMED (CV=0.133) | Novel |
| P6 | CONTAINMENT early | **FALSIFIED** (latest COM=2.235) | Novel; reframes containment |
| P7 | OPERATION after THERMAL | CONFIRMED (COM 1.955 vs 1.873) | Novel but lag tiny |

### PREFIX Confound Control (COLLAPSES)

After controlling for PREFIX positional grammar (C1001: R²=0.069):
- Residualized rank correlation: rho=0.333, p=0.420 (NOT significant)
- Residualized shape classification: 1/8 correct
- Verdict: **COLLAPSES** — category quintile gradients are substantially mediated by PREFIX positional grammar

### Critical Observations

1. **Predicted ordering is wrong.** Empirical: THERMAL(1.87) < OPERATION(1.96) < STAGING(1.96) < MARKING(2.07) < MONITORING(2.09) < FLOW(2.20) < TRANSITION(2.21) < CONTAINMENT(2.24). Predicted: STAGING(1) < MARKING(2) < CONTAINMENT(3). THERMAL appears earliest, not STAGING.

2. **CONTAINMENT is LATE, not early.** The "seal vessel before heating" prediction is wrong. Containment has the highest COM (latest). This is consistent with "collecting the distillate" rather than "sealing the vessel" — but it contradicts the thermodynamic ordering model.

3. **Most shapes are FLAT or U-SHAPED.** Only FLOW (RISING) and CONTAINMENT (PEAKED) match predictions. THERMAL is PEAKED (not DECLINING), STAGING is U-SHAPED (not DECLINING), OPERATION is FLAT (not RISING), TRANSITION is U-SHAPED (not RISING).

4. **PREFIX explains the gradient.** Line-initial PREFIXes (po, dch, so) select THERMAL-heavy MIDDLEs; line-final PREFIXes (ar, al, or, BARE) select FLOW-heavy MIDDLEs. The category gradient may be entirely a PREFIX artifact flowing through MIDDLE selection (C1012) and category determination (C1305).

## Interpretation

The "thermal arc" (C1371) is a real structural fact — category frequencies genuinely shift by line position. However, this shift is NOT well-predicted by a first-principles thermodynamic ordering model. The gradient is likely mediated by PREFIX positional grammar rather than reflecting independent process-ordering constraints.

This constrains Tier 3 interpretation: the distillation narrative must accommodate the fact that:
- THERMAL is already earliest (not preceded by setup/staging)
- CONTAINMENT is latest (collection, not preparation)
- The ordering is substantially explained by PREFIX mechanics

## Verdict

**WEAK: 0/7 tests pass, 0/7 strong, 6/7 predictions confirmed (PREFIX-confounded)**

## Evidence

- Script: `phases/THERMODYNAMIC_ARC_VALIDATION/scripts/thermodynamic_arc_validation.py`
- Results: `phases/THERMODYNAMIC_ARC_VALIDATION/results/thermodynamic_arc_validation.json`
- 22,753 tokens, 2,413 lines, 82 folios
- 10,000 permutations for T1

## Falsification Conditions

This constraint would be revised if:
1. A different thermodynamic ordering model (not the one tested here) achieves rho≥0.60
2. A MIDDLE-level analysis (bypassing PREFIX) reveals independent category-position correlation
3. The category classification system (C1250) is revised, changing positional profiles
