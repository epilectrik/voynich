# Phase 579: FORGIVING POLE RESIDUAL AUDIT - Report

## Executive Summary

Phase 579 audits the 8 stubborn A2 forgiving folios that survive all
closure-gating improvements from Phases 574-578. Four diagnostic tracks
determine whether these represent a structural endpoint or parameter underfit.

### Verdicts

| Constraint | Track | Verdict |
|------------|-------|---------|
| C1663 | Coherence | **GRADIENT_TAIL** |
| C1664 | Channel | **CHANNEL_CONCENTRATED** |
| C1665 | Opportunity | **OPPORTUNITY_NEUTRAL** |
| C1666 | Endpoint (DECISIVE) | **MIXED_BOUNDARY_STRATUM** |

## Track A: Coherence Profiling (C1663)

LOO nearest-centroid accuracy: 33.3%
Significant F-axes: 0/5
Significant ablation channels: 2/5
Within-forgiving cosine similarity: 0.9186
Between-group similarity: 0.8909
Lobe tightness: TIGHT

The 8 form a tight lobe in feature space but are not separable from passing
A2 folios. This is consistent with C1641 (A2 weakly structured, continuous
variation). The forgiving folios are the tail of a gradient, not a distinct
subfamily.

## Track B: Channel Decomposition (C1664)

Post-gate dominant channel counts: {'NO_R1': 6, 'NO_R4': 2}
Concentrated (>60% share): 8/8

Per-folio dominant channels:

  f39v: NO_R1 -> NO_R1 (share=1.15)
  f40r: NO_R1 -> NO_R1 (share=1.22)
  f50v: NO_R1 -> NO_R1 (share=1.10)
  f55v: NO_R1 -> NO_R1 (share=1.13)
  f85r2: NO_R1 -> NO_R1 (share=1.37)
  f86v5: NO_R4 -> NO_R4 (share=1.24)
  f86v6: NO_R4 -> NO_R4 (share=1.09)
  f95r2: NO_R1 -> NO_R1 (share=1.12)

R1 (per-SV CLOSE drawdown) dominates 6/8 folios. R4 (quality-conditioned
Y accumulation) dominates the remaining 2 (f86v5, f86v6). The gating from
Phase 576 did not change the dominant conversion mechanism for any folio.

## Track C: Opportunity Geometry (C1665)

Event count R-sq on CCS1: 0.0001
CTS: forgiving=0.200 vs passing=0.350

Key morphological contrasts (forgiving vs passing):
  Mean CTS: 0.200 vs 0.350
  WEAK grammar band: 24 vs 16
  E_armed: ? vs ?

Event count has no explanatory power (R-sq ~ 0). The forgiving folios
have structurally weaker closure events (lower CTS, fewer strong signals,
less e-head support). These are intrinsic folio properties, not sampling
artifacts.

## Track D: Constrained Retuning (C1666)

Grid: F1 x F2 in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6]
Total simulation runs: 7488

### T4a: F1 x F2 Sweep

| Folio | Orig F1 | Orig F2 | Best F1 | Best F2 | Best Adv | Disp | Pass | Class |
|-------|---------|---------|---------|---------|----------|------|------|-------|
| f39v | 0.83 | 0.90 | 1.60 | 0.50 | -0.0265 | 0.868 | N | STRUCTURAL_ENDPOINT |
| f40r | 0.70 | 0.77 | 1.60 | 0.50 | +0.0035 | 0.939 | Y | STRUCTURAL_ENDPOINT |
| f50v | 0.97 | 1.12 | 1.60 | 0.50 | +0.0332 | 0.881 | Y | STRUCTURAL_ENDPOINT |
| f55v | 0.70 | 1.23 | 1.60 | 0.50 | -0.0727 | 1.157 | N | STRUCTURAL_ENDPOINT |
| f85r2 | 0.77 | 1.05 | 1.60 | 0.50 | +0.0734 | 0.999 | Y | STRUCTURAL_ENDPOINT |
| f86v5 | 0.93 | 1.04 | 1.60 | 0.50 | -0.0425 | 0.865 | N | STRUCTURAL_ENDPOINT |
| f86v6 | 1.06 | 1.02 | 1.60 | 0.50 | +0.0226 | 0.753 | Y | STRUCTURAL_ENDPOINT |
| f95r2 | 0.95 | 0.78 | 1.60 | 0.50 | -0.1014 | 0.705 | N | STRUCTURAL_ENDPOINT |

### T4b: 3rd-Axis Extension

  f39v: F3=1.30 adv=-0.0263 ext_disp=0.969 -> FAIL [STRUCTURAL_ENDPOINT]
  f40r: F3=1.60 adv=+0.0041 ext_disp=1.169 -> PASS [PARAMETER_ACHIEVABLE]
  f50v: F3=1.60 adv=+0.0337 ext_disp=1.102 -> PASS [PARAMETER_ACHIEVABLE]
  f55v: F3=1.60 adv=-0.0718 ext_disp=1.426 -> FAIL [STRUCTURAL_ENDPOINT]
  f85r2: F3=0.50 adv=+0.0738 ext_disp=1.041 -> PASS [PARAMETER_ACHIEVABLE]
  f86v5: F5=1.60 adv=-0.0212 ext_disp=1.230 -> FAIL [STRUCTURAL_ENDPOINT]
  f86v6: F5=1.60 adv=+0.0376 ext_disp=1.133 -> PASS [PARAMETER_ACHIEVABLE]
  f95r2: F3=1.60 adv=-0.1011 ext_disp=0.875 -> FAIL [STRUCTURAL_ENDPOINT]

### Final Classification

  f39v: **STRUCTURAL_ENDPOINT**
  f40r: **PARAMETER_ACHIEVABLE**
  f50v: **PARAMETER_ACHIEVABLE**
  f55v: **STRUCTURAL_ENDPOINT**
  f85r2: **PARAMETER_ACHIEVABLE**
  f86v5: **STRUCTURAL_ENDPOINT**
  f86v6: **PARAMETER_ACHIEVABLE**
  f95r2: **STRUCTURAL_ENDPOINT**

Counts: {'STRUCTURAL_ENDPOINT': 4, 'PARAMETER_ACHIEVABLE': 4}
**C1666 verdict: MIXED_BOUNDARY_STRATUM**

## Per-Folio Cards

### f39v

- Section: H, Profile: A2_SEALED_RECIRCULATION
- F-params: F1=0.8291, F2=0.8993, F3=0.8706, F4=0.6226, F5=1.0065
- CCS1: 0.16876282179733043, DYE advantage: -0.06962221017759507, Gap: 0.0696
- Close events: 2
- Dominant channel: NO_R1 (share=1.1505)
- T4a: best (1.6, 0.5), adv=-0.026467, disp=0.8682, passing=0.0
- T4b: F3=1.3, passes=False, ext_disp=0.9686
- **Final: STRUCTURAL_ENDPOINT**

### f40r

- Section: H, Profile: A2_SEALED_RECIRCULATION
- F-params: F1=0.7, F2=0.7669, F3=0.9025, F4=0.5334, F5=1.4
- CCS1: 0.14759810736304863, DYE advantage: -0.021996118994484837, Gap: 0.022
- Close events: 1
- Dominant channel: NO_R1 (share=1.2248)
- T4a: best (1.6, 0.5), adv=0.003522, disp=0.9387, passing=0.0139
- T4b: F3=1.6, passes=True, ext_disp=1.1695
- **Final: PARAMETER_ACHIEVABLE**

### f50v

- Section: H, Profile: A2_SEALED_RECIRCULATION
- F-params: F1=0.9706, F2=1.1166, F3=0.9382, F4=0.6881, F5=1.3384
- CCS1: 0.18238834324160585, DYE advantage: -0.036598254910793354, Gap: 0.0366
- Close events: 1
- Dominant channel: NO_R1 (share=1.0987)
- T4a: best (1.6, 0.5), adv=0.033158, disp=0.8811, passing=0.4375
- T4b: F3=1.6, passes=True, ext_disp=1.102
- **Final: PARAMETER_ACHIEVABLE**

### f55v

- Section: H, Profile: A2_SEALED_RECIRCULATION
- F-params: F1=0.7, F2=1.2276, F3=0.7671, F4=0.369, F5=0.9742
- CCS1: 0.20044103792479176, DYE advantage: -0.11561087501640871, Gap: 0.1156
- Close events: 2
- Dominant channel: NO_R1 (share=1.1301)
- T4a: best (1.6, 0.5), adv=-0.07265, disp=1.1573, passing=0.0
- T4b: F3=1.6, passes=False, ext_disp=1.4259
- **Final: STRUCTURAL_ENDPOINT**

### f85r2

- Section: C, Profile: A2_SEALED_RECIRCULATION
- F-params: F1=0.7663, F2=1.0501, F3=0.7935, F4=0.3497, F5=0.7513
- CCS1: 0.1538088345346945, DYE advantage: -0.008648340226419665, Gap: 0.0086
- Close events: 3
- Dominant channel: NO_R1 (share=1.37)
- T4a: best (1.6, 0.5), adv=0.073353, disp=0.9988, passing=0.9583
- T4b: F3=0.5, passes=True, ext_disp=1.0411
- **Final: PARAMETER_ACHIEVABLE**

### f86v5

- Section: C, Profile: A2_SEALED_RECIRCULATION
- F-params: F1=0.926, F2=1.0427, F3=0.8382, F4=0.3951, F5=0.7252
- CCS1: 0.2739347637029585, DYE advantage: -0.147126454274279, Gap: 0.1471
- Close events: 9
- Dominant channel: NO_R4 (share=1.2358)
- T4a: best (1.6, 0.5), adv=-0.042462, disp=0.8653, passing=0.0
- T4b: F5=1.6, passes=False, ext_disp=1.2305
- **Final: STRUCTURAL_ENDPOINT**

### f86v6

- Section: C, Profile: A2_SEALED_RECIRCULATION
- F-params: F1=1.0579, F2=1.0224, F3=1.1487, F4=0.5065, F5=0.7531
- CCS1: 0.12041399089641588, DYE advantage: 0.00033192276457666425, Gap: 0
- Close events: 11
- Dominant channel: NO_R4 (share=1.0922)
- T4a: best (1.6, 0.5), adv=0.022627, disp=0.7528, passing=0.2778
- T4b: F5=1.6, passes=True, ext_disp=1.1331
- **Final: PARAMETER_ACHIEVABLE**

### f95r2

- Section: H, Profile: A2_SEALED_RECIRCULATION
- F-params: F1=0.9535, F2=0.7822, F3=1.0818, F4=0.8228, F5=1.1307
- CCS1: 0.29822522921834466, DYE advantage: -0.18094041793894786, Gap: 0.1809
- Close events: 1
- Dominant channel: NO_R1 (share=1.1238)
- T4a: best (1.6, 0.5), adv=-0.101444, disp=0.7054, passing=0.0
- T4b: F3=1.6, passes=False, ext_disp=0.8753
- **Final: STRUCTURAL_ENDPOINT**

## Implications

The 8 stubborn folios show MIXED_BOUNDARY_STRATUM: some are genuine
structural endpoints while others are parameter underfits. This is
consistent with C1641 (A2 continuous variation, many boundary folios).
The forgiving/passing boundary is a gradient, not a clean partition.
