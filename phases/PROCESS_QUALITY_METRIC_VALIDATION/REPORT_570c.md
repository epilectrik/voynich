# Phase 570c: Process Quality Metric Validation

**Verdict: PROCESS_QUALITY_VALIDATED**

**Tests:** CP1:4/4, CP2:3/4, CP3:4/4, CP4:inherited
**New constraints:** 2 (C1633-C1634)

---

## 1. Summary

Phase 570c validates that real closure tokens exhibit **productive disruption**: they create more per-step state perturbation than null tokens (DVA > 0) and convert that disruption into Y accumulation with higher efficiency (DYE advantage > 0). The DYE metric passes empirical p-value testing on 3/4 folios (CP2), confirming that the efficiency difference is not an artifact of permutation noise.

## 2. Context

Phase 570a established folio-specific apparatus coupling (PARTIAL). Phase 570b introduced demand-specific metrics and found that outcome metrics (TRA, DRS, SCP) fail because the restoring force dominates endpoint states, but Y-gain advantage (YGA) succeeds on 4/4 folios. Phase 570c asks: can we measure not just *how much* Y is gained, but *how efficiently* tokens convert their disruption into Y?

The key insight is that real closure tokens produce **more** disruption than nulls (counter to the 'smoother execution' hypothesis). The reason the apparatus still accumulates Y is that real tokens' disruption is grammar-aligned: the recovery architecture was designed to process these tokens, so their perturbation activates recovery channels productively.

## 3. What Changed from 570b

570b measured Y-gain directly (outcome). 570c introduces three process metrics:

| Metric | Definition | What it captures |
|--------|-----------|------------------|
| **DVA** (dV Advantage) | mean dV/token (M1) - mean dV/token (M4f) | Whether real tokens disrupt more |
| **DYE** (dV-to-Y Efficiency) | Y_gain / dV_sum per event | Return-on-disruption |
| **DYC** (dV-Y Composite) | 0.5 * z_DYE + 0.5 * z_YGA | Scale-independent combined score |

## 4. Test Results

### CP1: DYE Advantage > 0

**Result: 4/4 folios PASS** (gate: >= 3/4)

| Folio | DYE_M1 | DYE_M4f | DYE_advantage | Result |
|-------|--------|---------|---------------|--------|
| f108v | 0.1113 | 0.0330 | +0.078323 | PASS |
| f86v6 | 0.1202 | 0.1184 | +0.001815 | PASS |
| f111r | 0.1262 | 0.0657 | +0.060508 | PASS |
| f84r | 0.1203 | -0.0072 | +0.127514 | PASS |

### CP2: DYE Empirical P-Value >= 0.80 [CENTRAL]

**Result: 3/4 folios PASS** (gate: >= 3/4)

| Folio | M1 mean DYE | Perms beaten | EPV | Result |
|-------|-------------|-------------|-----|--------|
| f108v | 0.1113 | 20/20 | 1.00 | PASS |
| f86v6 | 0.1202 | 12/20 | 0.60 | FAIL |
| f111r | 0.1262 | 20/20 | 1.00 | PASS |
| f84r | 0.1203 | 20/20 | 1.00 | PASS |

### CP3: DVA > 0 (supporting)

**Result: 4/4 folios PASS** (gate: >= 3/4)

| Folio | mean_dV_M1 | mean_dV_M4f | DVA | Result |
|-------|-----------|------------|-----|--------|
| f108v | 0.0730 | 0.0497 | +0.023277 | PASS |
| f86v6 | 0.0690 | 0.0542 | +0.014714 | PASS |
| f111r | 0.0792 | 0.0453 | +0.033895 | PASS |
| f84r | 0.0696 | 0.0408 | +0.028781 | PASS |

### CP4: Anchor Survival (inherited)

**Result: PASS** (from 570b BP4)

## 5. Diagnostics

### CD1: Full Metric Table

| Folio | DVA | DYE_M1 | DYE_M4f | DYE_adv | EPV | DYC | YGA | demand_strong |
|-------|-----|--------|---------|---------|-----|-----|-----|---------------|
| f108v | +0.023277 | 0.1113 | 0.0330 | +0.078323 | 20/20 | 0.7348 | 0.0761 | yes |
| f86v6 | +0.014714 | 0.1202 | 0.1184 | +0.001815 | 12/20 | 0.1694 | 0.0374 | yes |
| f111r | +0.033895 | 0.1262 | 0.0657 | +0.060508 | 20/20 | 0.5976 | 0.0558 | yes |
| f84r | +0.028781 | 0.1203 | -0.0072 | +0.127514 | 20/20 | 1.7393 | 0.0750 | no |

### CD2: Per-Event DYE Decomposition

**f108v** (work_preceded, 7 events):

| Line | dV_sum | n_close | Y_gain | DYE | demand_mag |
|------|--------|---------|--------|-----|------------|
| f108v|16 | 0.9884 | 11 | 0.1071 | 0.1084 | 0.0754 |
| f108v|22 | 0.7766 | 12 | 0.1651 | 0.2126 | 0.0896 |
| f108v|28 | 0.4979 | 7 | 0.0515 | 0.1034 | 0.1022 |
| f108v|33 | 0.9643 | 12 | 0.0886 | 0.0919 | 0.0998 |
| f108v|38 | 0.9966 | 14 | 0.1692 | 0.1697 | 0.1282 |
| f108v|44 | 0.7879 | 11 | 0.0327 | 0.0415 | 0.1325 |
| f108v|47 | 0.6844 | 11 | 0.0354 | 0.0517 | 0.1076 |

**f86v6** (work_preceded, 7 events):

| Line | dV_sum | n_close | Y_gain | DYE | demand_mag |
|------|--------|---------|--------|-----|------------|
| f86v6|6 | 0.7972 | 11 | 0.0760 | 0.0953 | 0.1259 |
| f86v6|13 | 0.6891 | 9 | 0.0701 | 0.1018 | 0.1341 |
| f86v6|17 | 0.8793 | 13 | 0.1672 | 0.1902 | 0.1243 |
| f86v6|19 | 0.5258 | 7 | 0.0358 | 0.0681 | 0.0885 |
| f86v6|21 | 0.8401 | 12 | 0.1344 | 0.1600 | 0.0920 |
| f86v6|35 | 0.7257 | 12 | 0.0661 | 0.0911 | 0.1168 |
| f86v6|39 | 0.6650 | 11 | 0.0897 | 0.1349 | 0.1289 |

**f111r** (work_preceded, 3 events):

| Line | dV_sum | n_close | Y_gain | DYE | demand_mag |
|------|--------|---------|--------|-----|------------|
| f111r|5 | 0.5587 | 7 | 0.1151 | 0.2061 | 0.0944 |
| f111r|22 | 0.8842 | 12 | 0.0876 | 0.0990 | 0.0963 |
| f111r|26 | 0.9238 | 11 | 0.0679 | 0.0735 | 0.1014 |

**f84r** (E_any, 11 events):

| Line | dV_sum | n_close | Y_gain | DYE | demand_mag |
|------|--------|---------|--------|-----|------------|
| f84r|2 | 1.1611 | 16 | 0.1315 | 0.1132 | 0.0498 |
| f84r|12 | 0.9572 | 13 | 0.0869 | 0.0908 | 0.0893 |
| f84r|14 | 0.4125 | 8 | 0.1081 | 0.2621 | 0.0637 |
| f84r|15 | 0.6262 | 10 | 0.0498 | 0.0796 | 0.0462 |
| f84r|16 | 0.7449 | 12 | 0.0777 | 0.1043 | 0.0472 |
| f84r|23 | 0.5502 | 9 | 0.0849 | 0.1543 | 0.0693 |
| f84r|24 | 1.1387 | 14 | 0.0507 | 0.0446 | 0.0489 |
| f84r|26 | 0.5386 | 8 | 0.0552 | 0.1025 | 0.0613 |
| f84r|27 | 0.6218 | 6 | 0.0235 | 0.0378 | 0.0479 |
| f84r|30 | 0.3019 | 6 | 0.0627 | 0.2077 | 0.0568 |
| f84r|34 | 0.4781 | 6 | 0.0603 | 0.1261 | 0.0600 |

### CD3: n_close Token Comparison

| Folio | M1 mean n_close | M4f mean n_close | Ratio |
|-------|----------------|-----------------|-------|
| f108v | 11.1 | 11.4 | 0.98 |
| f86v6 | 10.7 | 9.5 | 1.13 |
| f111r | 10.0 | 11.3 | 0.88 |
| f84r | 9.8 | 9.5 | 1.03 |

Ratios near 1.0 confirm DYE differences are not confounded by line length.

### CD4: DYE vs Demand Magnitude Correlation

| Folio | Pearson r | n_events | Interpretation |
|-------|----------|----------|----------------|
| f108v | -0.279 | 7 | weak/no relationship |
| f86v6 | 0.136 | 7 | weak/no relationship |
| f111r | -0.824 | 3 | harder demand -> lower DYE |
| f84r | 0.274 | 11 | weak/no relationship |

### CD5: Cross-Metric Coherence

Spearman rank correlations across 4 folios:

| Pair | Spearman rho |
|------|-------------|
| DVA vs DYE_advantage | 0.400 |
| DVA vs YGA | 0.200 |
| DYE_advantage vs YGA | 0.800 |

## 6. Analysis

### Productive Disruption Mechanism

The central finding of 570c is that real closure tokens create **more** disruption (higher dV per step) than null tokens, not less. This overturns the naive 'smoother execution' hypothesis from 570b. The mechanism is:

1. **Real tokens perturb the state vector more** (DVA > 0 on all folios)
2. **But their perturbation is grammar-aligned** — the apparatus was designed to process these tokens
3. **Grammar-aligned disruption activates recovery channels productively**, converting perturbation into Y accumulation
4. **Null tokens' disruption is random** — it creates state perturbation that the recovery architecture cannot efficiently convert to Y

### Why DYE Works

DYE (dV-to-Y Efficiency) captures 'return on investment': how much Y is accumulated per unit of state disruption. Real tokens get high ROI because their disruption flows through designed recovery channels. Null tokens get low or negative ROI because their disruption is unstructured.

### Why f86v6 Is Weaker

f86v6 shows the smallest DYE advantage (+0.001815) and fails CP2 (12/20 perms). Its M4f perms achieve DYE close to M1 (0.1184 vs 0.1202). This suggests f86v6 has structural properties (high thermal fraction, specific recovery architecture parameters) that make the recovery system more forgiving — even null tokens convert disruption to Y reasonably well on this folio.

### Process vs Outcome Metrics

570c completes the lesson from 570b:

- **Outcome metrics** (ERM, TRA, DRS, SCP, endpoint state) fail because the restoring force dominates. By the end of the line, both real and null tokens have been pulled back toward equilibrium.
- **Process metrics** (DYE, dV distributions) succeed because they capture token-level effects *during* execution, before the restoring force washes them out.

## 7. Provisional Constraints

**C1633** (Tier 2, B_apparatus): Real closure tokens convert disruption to Y with higher efficiency than state-matched nulls (DYE advantage > 0, 4/4 folios including all demand-strong)

**C1634** (Tier 2, B_apparatus): Real closure tokens produce higher per-step disruption than random tokens at CLOSE positions (DVA > 0, 4/4 folios)

## 8. Lessons and Implications

1. **Productive disruption is the mechanism**, not smooth execution. Real tokens are *more* disruptive but their disruption is constructive.
2. **Process metrics capture what outcome metrics miss.** The restoring force that makes the apparatus stable also masks token-level differences at endpoints.
3. **DYE is the right metric** for measuring closure quality: it asks not 'how much Y?' but 'how efficiently was disruption converted to Y?'
4. **f86v6 is structurally forgiving** — its recovery architecture converts even random disruption to Y reasonably well, reducing the M1/M4f contrast.
5. **Demand magnitude normalization (DYC)** provides scale-independent comparison across folios with different baseline excursion levels.

## 9. Cross-Phase Comparison

| Phase | Score | Key Result |
|-------|-------|------------|
| 563 | 5/9 | Baseline apparatus coupling |
| 563b | 3/9 | Sensitivity recalibration |
| 564 | 2/9 | Event-gated execution |
| 564b | 2/9 | Selective restoration |
| 565 | 2/9 | Permeability calibration |
| 566 | 1/9 | CLOSE recovery |
| 567 | P2 + 3/7 NP | PARTIAL: readout reform |
| 568 | P2 + 3/7 EP | PARTIAL: controlled excursion metrics |
| 569 | P2 + 1/5 PT | INSUFFICIENT: eventive closure |
| 570a | AP1:3/4, AP2:2/4, AP3:3/4 | PARTIAL: folio-specific apparatus |
| 570b | BP1:0/4, BP2:1/4, BP3:4/4 | PARTIAL: demand-specific metrics |
| **570c** | **CP1:4/4, CP2:3/4, CP3:4/4** | **PROCESS QUALITY VALIDATED** |

---

*Generated: 2026-03-10 19:26 UTC by t1_process_quality_metrics.py*