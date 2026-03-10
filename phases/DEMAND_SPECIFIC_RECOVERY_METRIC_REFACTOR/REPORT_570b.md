# Phase 570b: DEMAND-SPECIFIC RECOVERY METRIC REFACTOR

## Verdict: PARTIAL_DEMAND_METRIC

## Summary

Phase 570b tested whether demand-specific recovery metrics (TRA, nTRA, DRS, SCP, YGA, DBP) can separate the full model (M1) from demand-matched nulls (M4f) at closure events. These metrics were designed to address the ERM axis inversion identified in Phases 569 and 570a, where undirected ERM rewards nulls for regression-to-mean recovery at shuffled positions.

Results show partial success. BP3 passes (4/4): the Y-gain advantage (YGA) is consistently positive across all four pilot folios, including all three demand-strong folios. The Y-gain channel captures a real signal: real closure tokens produce smaller dV magnitudes (less system disruption), yielding higher clean_close_mult and thus more Y accumulation per step. BP4 passes: anchors survive. However, BP1 (nTRA) and BP2 (DRS) fail, revealing that the recovery *amount* and *direction* are dominated by the restoring force regardless of token identity. The verdict is PARTIAL_DEMAND_METRIC.

## Context

Phase 570a (FOLIO_SPECIFIC_APPARATUS_PILOT) validated folio-specific parameterization (F1-F5) but could not pass the null-separation gate (AP2: 2/4) due to the ERM axis inversion. The expert diagnosis identified that ERM rewards *any* post-close residual reduction, giving shuffled nulls a structural advantage from regression-to-mean effects.

Phase 570b addresses this by replacing ERM with a family of demand-specific metrics that measure recovery quality from different angles:

- **TRA/nTRA**: Total Recovery Advantage -- raw and normalized recovery amount at demanded events
- **DRS**: Demand-Response Specificity -- whether recovery direction aligns with demand direction
- **SCP**: State Convergence Profile -- whether demanded events end in better attractor basins
- **YGA**: Y-Gain Advantage -- whether real tokens accumulate more Y than nulls at demanded events
- **DBP**: Differential B10 Potency -- whether B10 channel is differentially more effective for directed recovery

## What Changed

### New Metric Family

| Metric | Measures | Formula |
|--------|----------|---------|
| TRA | Absolute recovery amount | mean(recovery_M1) - mean(recovery_M4f) |
| nTRA | Normalized recovery (fraction of demand recovered) | mean(nrec_M1) - mean(nrec_M4f) |
| DRS | Recovery direction alignment with demand | combined(mag+rank) DRS_M1 - DRS_M4f |
| SCP | End-state zone quality | fraction in BASIN (M1) - fraction in BASIN (M4f) |
| YGA | Y accumulation per demanded event | mean(ygain_M1) - mean(ygain_M4f) |
| DBP | Differential B10 channel potency | (M1-M2b) - (M0-M2a) at same demand mask |

## Test Results

### BP1: nTRA > 0 at >= 3/4 folios

| Folio | nTRA | Result |
|-------|------|--------|
| f108v | -0.108564 | FAIL |
| f86v6 | -0.015111 | FAIL |
| f111r | -0.020929 | FAIL |
| f84r | -0.085627 | FAIL |

BP1 result: 0/4 -> **FAIL**

### BP2: DRS Advantage > 0 (CENTRAL)

| Folio | DRS_adv | mag_adv | rank_adv | Result |
|-------|---------|---------|----------|--------|
| f108v | -0.1224 | -0.1079 | -0.1443 | FAIL |
| f86v6 | -0.0769 | +0.0184 | -0.2197 | FAIL |
| f111r | -0.0510 | -0.0288 | -0.0843 | FAIL |
| f84r | +0.0857 | +0.1339 | +0.0133 | PASS |

BP2 result: 1/4 -> **FAIL**

### BP3: YGA > 0 at >= 3/4 folios (supporting)

| Folio | YGA | M1 y-gain | M4f y-gain | Demand-Strong | Result |
|-------|-----|-----------|------------|---------------|--------|
| f108v | +0.076075 | 0.092806 | 0.016732 | YES | PASS |
| f86v6 | +0.037408 | 0.091342 | 0.053934 | YES | PASS |
| f111r | +0.055826 | 0.090208 | 0.034383 | YES | PASS |
| f84r | +0.074989 | 0.071950 | -0.003040 | no | PASS |

BP3 result: 4/4 -> **PASS** (demand-strong: 3/3)

### BP4: Anchor Stability

**P2: PASS** (by reference to Phase 569)

**UEB** (M1 <= M0):

| Folio | M0 UEB | M1 UEB | Delta | Result |
|-------|--------|--------|-------|--------|
| f108v | 7.5 | 6.0 | -1.5 | PASS |
| f86v6 | 23.5 | 28.5 | +5.0 | FAIL |
| f111r | 7.5 | 7.5 | +0.0 | PASS |
| f84r | 0.0 | 0.0 | +0.0 | PASS |

UEB sub-test: 3/4 -> PASS

**WCP** (M1 >= M0):

| Folio | M0 WCP | M1 WCP | Delta | Result |
|-------|--------|--------|-------|--------|
| f108v | 0.791812 | 0.785245 | -0.006567 | FAIL |
| f86v6 | 0.858899 | 0.857267 | -0.001632 | FAIL |
| f111r | 0.825646 | 0.823677 | -0.001969 | FAIL |
| f84r | 0.906563 | 0.898368 | -0.008195 | FAIL |

WCP sub-test: 0/4 -> FAIL

BP4 overall: P2=PASS, secondary fails=1 (<= 1 allowed) -> **PASS**

## Diagnostics Summary

### BD1: Full Metric Table

| Folio | Sel | N | TRA | nTRA | DRS_adv | SCP_delta | YGA | DBP | Strong |
|-------|-----|---|-----|------|---------|-----------|-----|-----|--------|
| f108v | work_preceded | 7 | -0.011512 | -0.108564 | -0.122429 | +0.000000 | +0.076075 | -0.003545 | YES |
| f86v6 | work_preceded | 7 | -0.002981 | -0.015111 | -0.076856 | -0.023810 | +0.037408 | -0.001268 | YES |
| f111r | work_preceded | 3 | +0.002535 | -0.020929 | -0.051000 | +0.000000 | +0.055826 | -0.001315 | YES |
| f84r | E_any | 11 | -0.011081 | -0.085627 | +0.085699 | -0.015152 | +0.074989 | +0.000999 | no |

### BD2: Per-SV Recovery Profiles

**f108v** (n_M1=7):

| SV | M1 demand | M1 recovery | M4f demand | M4f recovery | Delta recovery |
|----|-----------|-------------|------------|--------------|----------------|
| T | 0.1322 | +0.1214 | 0.1344 | +0.1285 | -0.0071 |
| RC | 0.0435 | +0.0300 | 0.0428 | +0.0319 | -0.0020 |
| S | 0.2636 | +0.0608 | 0.2493 | +0.0972 | -0.0364 |
| C | 0.0646 | +0.0548 | 0.0670 | +0.0604 | -0.0056 |
| TR | 0.0409 | +0.0268 | 0.0565 | +0.0385 | -0.0117 |
| X | 0.0855 | +0.0514 | 0.0849 | +0.0576 | -0.0062 |

**f86v6** (n_M1=7):

| SV | M1 demand | M1 recovery | M4f demand | M4f recovery | Delta recovery |
|----|-----------|-------------|------------|--------------|----------------|
| T | 0.1063 | +0.0938 | 0.0914 | +0.0809 | +0.0129 |
| RC | 0.0316 | +0.0178 | 0.0238 | +0.0026 | +0.0152 |
| S | 0.1878 | +0.0577 | 0.1970 | +0.0487 | +0.0089 |
| C | 0.2685 | +0.2100 | 0.2909 | +0.2823 | -0.0723 |
| TR | 0.0199 | +0.0110 | 0.0174 | -0.0010 | +0.0120 |
| X | 0.0806 | +0.0736 | 0.0909 | +0.0682 | +0.0054 |

**f111r** (n_M1=3):

| SV | M1 demand | M1 recovery | M4f demand | M4f recovery | Delta recovery |
|----|-----------|-------------|------------|--------------|----------------|
| T | 0.0849 | +0.0747 | 0.1157 | +0.1114 | -0.0367 |
| RC | 0.0189 | +0.0097 | 0.0335 | +0.0254 | -0.0157 |
| S | 0.2371 | +0.0364 | 0.2488 | +0.0755 | -0.0391 |
| C | 0.1171 | +0.0940 | 0.0555 | +0.0509 | +0.0431 |
| TR | 0.0298 | +0.0249 | 0.0368 | +0.0301 | -0.0052 |
| X | 0.0962 | +0.0770 | 0.0266 | +0.0081 | +0.0689 |

**f84r** (n_M1=11):

| SV | M1 demand | M1 recovery | M4f demand | M4f recovery | Delta recovery |
|----|-----------|-------------|------------|--------------|----------------|
| T | 0.0106 | +0.0047 | 0.0264 | +0.0233 | -0.0186 |
| RC | 0.0274 | +0.0135 | 0.0307 | +0.0167 | -0.0032 |
| S | 0.2537 | +0.0287 | 0.2585 | +0.0260 | +0.0027 |
| C | 0.0328 | +0.0027 | 0.0547 | +0.0495 | -0.0468 |
| TR | 0.0175 | +0.0090 | 0.0130 | +0.0047 | +0.0043 |
| X | 0.0073 | -0.0001 | 0.0072 | +0.0047 | -0.0048 |

### BD3: Event-Type Stratification

**f108v:**

| Event Type | M1 count | M1 recovery | M1 y-gain | M4f count | TRA adv | YGA adv |
|------------|----------|-------------|-----------|-----------|---------|---------|
| E_any | 7 | +0.0575 | 0.0928 | 84 | -0.0112 | +0.0761 |
| E_armed | 2 | +0.0636 | 0.1289 | 0 | N/A | N/A |
| E_compound | 2 | +0.0636 | 0.1289 | 0 | N/A | N/A |
| E_cts50 | 1 | +0.0480 | 0.0886 | 0 | N/A | N/A |
| E_opaque | 3 | +0.0706 | 0.0968 | 0 | N/A | N/A |
| E_opaque_decisive | 2 | +0.0636 | 0.1289 | 0 | N/A | N/A |

**f86v6:**

| Event Type | M1 count | M1 recovery | M1 y-gain | M4f count | TRA adv | YGA adv |
|------------|----------|-------------|-----------|-----------|---------|---------|
| E_any | 7 | +0.0773 | 0.0913 | 71 | -0.0032 | +0.0374 |
| E_compound | 2 | +0.0753 | 0.1508 | 0 | N/A | N/A |
| E_cts50 | 1 | +0.0474 | 0.1344 | 0 | N/A | N/A |
| E_mcb | 2 | +0.0753 | 0.1508 | 0 | N/A | N/A |
| E_opaque | 2 | +0.0753 | 0.1508 | 0 | N/A | N/A |
| E_opaque_decisive | 2 | +0.0753 | 0.1508 | 0 | N/A | N/A |

**f111r:**

| Event Type | M1 count | M1 recovery | M1 y-gain | M4f count | TRA adv | YGA adv |
|------------|----------|-------------|-----------|-----------|---------|---------|
| E_any | 3 | +0.0528 | 0.0902 | 65 | +0.0093 | +0.0567 |
| E_armed | 1 | +0.0507 | 0.1151 | 0 | N/A | N/A |
| E_compound | 1 | +0.0507 | 0.1151 | 0 | N/A | N/A |
| E_cts50 | 1 | +0.0507 | 0.1151 | 0 | N/A | N/A |
| E_opaque | 1 | +0.0507 | 0.1151 | 0 | N/A | N/A |
| E_opaque_decisive | 1 | +0.0507 | 0.1151 | 0 | N/A | N/A |

**f84r:**

| Event Type | M1 count | M1 recovery | M1 y-gain | M4f count | TRA adv | YGA adv |
|------------|----------|-------------|-----------|-----------|---------|---------|
| E_any | 11 | +0.0097 | 0.0719 | 199 | -0.0110 | +0.0750 |
| E_armed | 2 | +0.0019 | 0.0690 | 0 | N/A | N/A |
| E_compound | 2 | +0.0019 | 0.0690 | 0 | N/A | N/A |
| E_cts50 | 2 | +0.0019 | 0.0690 | 0 | N/A | N/A |
| E_opaque | 2 | +0.0019 | 0.0690 | 0 | N/A | N/A |
| E_opaque_decisive | 2 | +0.0019 | 0.0690 | 0 | N/A | N/A |

### BD4: Differential Demand Slope (CRITICAL)

| Folio | N | M1 r(demand,rec) | M1 r(demand,yg) | M4f r(demand,rec) | M4f r(demand,yg) | M1 steeper rec | M1 steeper yg |
|-------|---|------------------|-----------------|-------------------|-----------------|----------------|---------------|
| f108v | 7 | +0.9781 | -0.2050 | +0.9395 | -0.5816 | True | True |
| f86v6 | 7 | +0.8985 | +0.1117 | +0.9243 | +0.4859 | False | False |
| f111r | 3 | +0.8688 | -0.9368 | +0.9112 | +0.2911 | False | False |
| f84r | 11 | +0.8217 | +0.2958 | +0.9643 | +0.3402 | False | False |

### BD5: Old Metrics Continuity

| Folio | M1 dem. ERM | M1 E_any ERM | M4f E_any ERM | AP2 delta |
|-------|-------------|--------------|---------------|-----------|
| f108v | 0.350597 | 0.226878 | 0.330388 | +0.020209 |
| f86v6 | 0.546943 | 0.443482 | 0.434564 | +0.112379 |
| f111r | 0.353302 | 0.229484 | 0.331260 | +0.022042 |
| f84r | 0.397466 | 0.131164 | 0.199290 | +0.198176 |

These match the 570a values, confirming old-metric continuity.

### BD6: Per-Event State Trajectories

**f108v f108v|16** (ERM=0.2329, dv_mag=0.9884, y_gain=0.1071):

| SV | pre | end | demand | residual | recovery |
|----|-----|-----|--------|----------|----------|
| T | 0.5665 | 0.5023 | 0.0665 | 0.0023 | +0.0642 |
| RC | 0.5170 | 0.5107 | 0.0170 | 0.0107 | +0.0063 |
| S | 0.7739 | 0.7526 | 0.2739 | 0.2526 | +0.0213 |
| C | 0.5499 | 0.5007 | 0.0499 | 0.0007 | +0.0492 |
| TR | 0.5098 | 0.5188 | 0.0098 | 0.0188 | -0.0090 |
| X | 0.5353 | 0.4653 | 0.0353 | 0.0347 | +0.0006 |
| Y | 0.7147 | 0.8218 | -- | -- | -- |

**f108v f108v|22** (ERM=0.3961, dv_mag=0.7766, y_gain=0.1651):

| SV | pre | end | demand | residual | recovery |
|----|-----|-----|--------|----------|----------|
| T | 0.4324 | 0.5045 | 0.0676 | 0.0045 | +0.0631 |
| RC | 0.5323 | 0.5056 | 0.0323 | 0.0056 | +0.0267 |
| S | 0.7691 | 0.6636 | 0.2691 | 0.1636 | +0.1056 |
| C | 0.5020 | 0.5302 | 0.0020 | 0.0302 | -0.0282 |
| TR | 0.5767 | 0.5209 | 0.0767 | 0.0209 | +0.0558 |
| X | 0.4102 | 0.4787 | 0.0898 | 0.0213 | +0.0685 |
| Y | 0.6572 | 0.8223 | -- | -- | -- |

**f86v6 f86v6|6** (ERM=0.5756, dv_mag=0.7972, y_gain=0.0760):

| SV | pre | end | demand | residual | recovery |
|----|-----|-----|--------|----------|----------|
| T | 0.6283 | 0.5197 | 0.1283 | 0.0197 | +0.1086 |
| RC | 0.5123 | 0.5145 | 0.0123 | 0.0145 | -0.0022 |
| S | 0.7464 | 0.6565 | 0.2464 | 0.1565 | +0.0899 |
| C | 0.7931 | 0.5355 | 0.2931 | 0.0355 | +0.2576 |
| TR | 0.4894 | 0.5010 | 0.0106 | 0.0010 | +0.0095 |
| X | 0.5646 | 0.5118 | 0.0646 | 0.0118 | +0.0528 |
| Y | 0.5652 | 0.6411 | -- | -- | -- |

**f86v6 f86v6|13** (ERM=0.4825, dv_mag=0.6891, y_gain=0.0701):

| SV | pre | end | demand | residual | recovery |
|----|-----|-----|--------|----------|----------|
| T | 0.6668 | 0.5055 | 0.1668 | 0.0055 | +0.1613 |
| RC | 0.5339 | 0.5005 | 0.0339 | 0.0005 | +0.0334 |
| S | 0.6930 | 0.6703 | 0.1930 | 0.1703 | +0.0227 |
| C | 0.7516 | 0.6091 | 0.2516 | 0.1091 | +0.1424 |
| TR | 0.4909 | 0.4867 | 0.0091 | 0.0133 | -0.0042 |
| X | 0.6503 | 0.4967 | 0.1503 | 0.0033 | +0.1470 |
| Y | 0.6332 | 0.7034 | -- | -- | -- |

**f111r f111r|5** (ERM=0.2961, dv_mag=0.5587, y_gain=0.1151):

| SV | pre | end | demand | residual | recovery |
|----|-----|-----|--------|----------|----------|
| T | 0.5833 | 0.5018 | 0.0833 | 0.0018 | +0.0815 |
| RC | 0.5251 | 0.5076 | 0.0251 | 0.0076 | +0.0175 |
| S | 0.7270 | 0.7086 | 0.2270 | 0.2086 | +0.0184 |
| C | 0.5647 | 0.5382 | 0.0647 | 0.0382 | +0.0265 |
| TR | 0.5116 | 0.4980 | 0.0116 | 0.0020 | +0.0096 |
| X | 0.6546 | 0.4959 | 0.1546 | 0.0041 | +0.1505 |
| Y | 0.6292 | 0.7444 | -- | -- | -- |

**f111r f111r|22** (ERM=0.3145, dv_mag=0.8842, y_gain=0.0876):

| SV | pre | end | demand | residual | recovery |
|----|-----|-----|--------|----------|----------|
| T | 0.5782 | 0.5227 | 0.0782 | 0.0227 | +0.0556 |
| RC | 0.5262 | 0.5087 | 0.0262 | 0.0087 | +0.0175 |
| S | 0.7728 | 0.6924 | 0.2728 | 0.1924 | +0.0803 |
| C | 0.5832 | 0.5294 | 0.0832 | 0.0294 | +0.0537 |
| TR | 0.5231 | 0.5051 | 0.0231 | 0.0051 | +0.0180 |
| X | 0.5940 | 0.4639 | 0.0940 | 0.0361 | +0.0579 |
| Y | 0.7517 | 0.8393 | -- | -- | -- |

**f84r f84r|2** (ERM=-0.0759, dv_mag=1.1611, y_gain=0.1315):

| SV | pre | end | demand | residual | recovery |
|----|-----|-----|--------|----------|----------|
| T | 0.4950 | 0.5000 | 0.0050 | 0.0000 | +0.0050 |
| RC | 0.5068 | 0.4933 | 0.0068 | 0.0067 | +0.0001 |
| S | 0.7583 | 0.7533 | 0.2583 | 0.2533 | +0.0051 |
| C | 0.5154 | 0.5466 | 0.0154 | 0.0466 | -0.0312 |
| TR | 0.5098 | 0.4957 | 0.0098 | 0.0043 | +0.0055 |
| X | 0.4966 | 0.4949 | 0.0034 | 0.0051 | -0.0017 |
| Y | 0.5118 | 0.6433 | -- | -- | -- |

**f84r f84r|12** (ERM=0.3975, dv_mag=0.9572, y_gain=0.0869):

| SV | pre | end | demand | residual | recovery |
|----|-----|-----|--------|----------|----------|
| T | 0.5226 | 0.5129 | 0.0226 | 0.0129 | +0.0097 |
| RC | 0.5514 | 0.5228 | 0.0514 | 0.0228 | +0.0286 |
| S | 0.8128 | 0.7491 | 0.3128 | 0.2491 | +0.0636 |
| C | 0.6033 | 0.5087 | 0.1033 | 0.0087 | +0.0946 |
| TR | 0.5265 | 0.5086 | 0.0265 | 0.0086 | +0.0179 |
| X | 0.5191 | 0.4936 | 0.0191 | 0.0064 | +0.0127 |
| Y | 0.6001 | 0.6870 | -- | -- | -- |

### BD7: DBP Decomposition

| Folio | DBP | M0 rec | M1 rec | M2a rec | M2b rec | M0 B10 | M1 B10 | Mask |
|-------|-----|--------|--------|---------|---------|--------|--------|------|
| f108v | -0.003545 | 0.057711 | 0.057513 | 0.033916 | 0.037263 | 0.023795 | 0.020250 | 7 |
| f86v6 | -0.001268 | 0.076411 | 0.077301 | 0.027977 | 0.030136 | 0.048433 | 0.047166 | 7 |
| f111r | -0.001315 | 0.053707 | 0.052778 | 0.029284 | 0.029669 | 0.024424 | 0.023109 | 3 |
| f84r | +0.000999 | 0.010703 | 0.009746 | 0.002602 | 0.000647 | 0.008101 | 0.009100 | 11 |

## Analysis

### What Worked

1. **YGA is the only consistently discriminating metric** (4/4, effect sizes +0.037 to +0.076). This works because Y accumulates via `clean_close_mult = 1.0 / (1.0 + 10.0 * dv_magnitude)` -- real closure tokens have smaller dV (less system disruption), yielding higher clean_close_mult and thus more Y per step. Nulls (random tokens at CLOSE positions) produce larger dV, less Y.

2. **The Y-gain channel captures an intensity signal, not a directional one.** Token identity affects dV magnitude (disruption per step), which flows through clean_close_mult to Y accumulation. The apparatus grammar alignment manifests as smoother execution (lower dV), not as different recovery direction. This is why YGA succeeds where DRS fails.

3. **BP4 anchors survive.** P2 is unaffected (independent of demand metrics). UEB improves or holds for 3/4 folios. WCP drops for all 4, but effects are small (< 0.01), consistent with F1 attractor force compression.

### What Did Not Work

1. **TRA/nTRA fail** (0/4). Both M1 and M4f show comparable absolute recovery amounts -- the restoring force pulls states toward equilibrium regardless of token identity. What differs is the *quality* of the path (dV magnitude), not the *total distance* recovered.

2. **DRS fails** (1/4, and the one pass is the demand-weak folio f84r). The recovery *direction* (which SVs recover most) is dominated by the restoring force's proportional response to demand, not by token identity. Both M1 and M4f achieve similarly directional recovery.

3. **SCP fails** (0/4 with positive delta). Nearly all events end in BASIN (zone 4) regardless of model -- the restoring force is strong enough to pull most SVs back to near-equilibrium by line end.

4. **DBP is near zero** (-0.004 to +0.001). The B10 effect (close recovery channels) operates comparably on both M0 and M1 -- folio-specific tuning does not make B10 differentially more effective for directed recovery vs undirected.

## Why PARTIAL_DEMAND_METRIC

BP3 passes unanimously (4/4 including 3/3 demand-strong), establishing that the Y-gain channel is a genuine discriminator between real and null closure tokens. However, the central test BP2 (DRS advantage) fails, and BP1 (nTRA) also fails. The demand-specific metric family partially succeeds: one of six metrics discriminates, and it does so through an unexpected channel (execution smoothness -> Y accumulation) rather than through the hypothesized recovery-direction mechanism.

The partial success is meaningful because it identifies *where* token identity matters: not in how much or which direction the system recovers (both dominated by restoring force), but in how smoothly the recovery proceeds (dV magnitude per step). This is an intensity signal embedded in the Y-accumulation pathway.

## Provisional Constraints

- **C1632** (Tier 2, BP3): Real closure tokens produce greater Y accumulation at demanded events than state-matched nulls (YGA > 0, 4/4 folios including 3/3 demand-strong).

C1630 (nTRA positive): NOT ISSUED -- BP1 fails (0/4)
C1631 (DRS advantage): NOT ISSUED -- BP2 fails (1/4)

## Lessons and Implications

1. **The restoring force dominates recovery amount and direction.** TRA, nTRA, DRS, and SCP all fail because the proportional restoring force produces similar recovery trajectories regardless of token identity. The system is designed to recover -- the question is not *whether* it recovers but *how smoothly*.

2. **Token identity manifests as execution smoothness.** Real closure tokens produce lower dV magnitudes than null tokens at the same positions. This does not change the recovery endpoint (restoring force ensures convergence) but changes the path quality. The clean_close_mult mechanism translates this smoothness into differential Y accumulation.

3. **The ERM axis inversion is a symptom of the wrong measurement axis.** ERM, TRA, DRS, and SCP all measure *recovery outcome* (endpoint state). The discriminating signal is in *recovery process* (path smoothness). Future metrics should focus on process-level signals: dV distributions, step-by-step coherence, or accumulation-pathway differentials.

4. **Y-gain is a viable discriminator but is a supporting metric.** YGA effect sizes (+0.037 to +0.076) are modest but consistent. As a single-channel signal, it may not be sufficient for full model validation. Combining Y-gain with dV-distribution metrics could produce a stronger composite.

5. **Demand-strong folios behave consistently.** The three demand-strong folios (f108v, f86v6, f111r) all show the same pattern: negative TRA/nTRA/DRS, near-zero SCP/DBP, positive YGA. f84r (demand-weak, E_any fallback) is anomalous on DRS (positive) but conforms on other metrics. The demand-strong selection criterion is validated.

## Next Phase Recommendations

1. **Explore dV-distribution metrics.** Since token identity manifests as execution smoothness (lower dV), a metric comparing dV distributions at demanded events between M1 and M4f could be the primary discriminator. Options include: mean dV magnitude ratio, KS statistic on dV distributions, or per-step dV quantile comparisons.

2. **Composite YGA + dV metric.** Combine the Y-gain advantage (which captures smoothness through clean_close_mult) with direct dV magnitude comparison into a single composite score. This attacks the signal from two angles: accumulation pathway (YGA) and raw process quality (dV).

3. **Retain folio-specific parameterization.** F1-F5 from Phase 570a should carry forward -- they produce genuine improvements in demanded-event ERM even though the current metric framework cannot validate them against nulls.

4. **Consider expanding pilot.** If a dV-based metric succeeds on the 4-folio pilot, test on all 20 candidate folios to assess generalization.

## Cross-Phase Comparison

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
| **570b** | **BP1:0/4, BP2:1/4, BP3:4/4** | **PARTIAL_DEMAND_METRIC** |

---

*Generated by t5_validation_synthesis.py | Phase 570b | 2026-03-10T19:08:58.036664+00:00*