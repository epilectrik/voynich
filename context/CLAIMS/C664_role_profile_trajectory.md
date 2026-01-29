# C664: Role Profile Trajectory

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

## Finding

Within-folio role composition is **predominantly stationary** with one significant exception: AUXILIARY scaffold fraction increases from early to late lines (rho=+0.082, p=5.6e-05, KW H=18.0, p=4.5e-04). No other role shows a significant monotonic trajectory across the corpus.

EN shows marginal decline (rho=-0.027, p=0.178, KW p=0.062) that becomes regime-dependent: REGIME_1 shows -0.052 EN slope, REGIME_3 shows +0.067 EN slope. Regime predicts EN and FL trajectory shapes (KW on slopes: EN p=0.038, FL p=0.006), but CC, FQ, and AX trajectories are regime-independent.

## Evidence

### Corpus-Wide Role Trajectories (2420 lines, 82 folios)

| Role | Q1 | Q2 | Q3 | Q4 | rho | p | KW p | Verdict |
|------|-----|-----|-----|-----|------|---|------|---------|
| CC | 0.0424 | 0.0464 | 0.0449 | 0.0457 | +0.002 | 0.93 | 0.71 | FLAT |
| EN | 0.3188 | 0.3269 | 0.3157 | 0.2973 | -0.027 | 0.18 | 0.062 | MARGINAL decline |
| FL | 0.0418 | 0.0425 | 0.0438 | 0.0471 | +0.030 | 0.14 | 0.81 | FLAT |
| FQ | 0.1258 | 0.1146 | 0.1076 | 0.1367 | +0.020 | 0.33 | 6.7e-04 | NON-MONOTONIC |
| **AX** | **0.1536** | **0.1552** | **0.1709** | **0.1806** | **+0.082** | **5.6e-05** | **4.5e-04** | **INCREASING** |

### Regime-Dependent EN Trajectory

| Regime | EN Q1 | EN Q4 | Slope |
|--------|-------|-------|-------|
| REGIME_1 | 0.4062 | 0.3541 | -0.052 |
| REGIME_2 | 0.2736 | 0.2471 | -0.027 |
| REGIME_3 | 0.2370 | 0.3037 | +0.067 |
| REGIME_4 | 0.2829 | 0.2772 | -0.006 |

KW on EN slopes across regimes: H=8.41, p=0.038.

### Folio Trajectory Clustering

Best k=2, silhouette=0.451 (79 folios with >=8 lines):
- Cluster 1: 2 outlier folios (both REGIME_1) with extreme slopes
- Cluster 2: 77 folios with mild EN decline (-0.023), mild AX increase (+0.032)

## Interpretation

Programs are quasi-stationary in role composition. The one consistent signal is AX scaffold build-up toward program end (Q1=15.4%, Q4=18.1%). This is consistent with convergence-phase behavior: late control blocks require more contextual scaffolding as the program approaches its terminal state. EN's marginal decline mirrors this — energy operations yield to scaffolding.

The regime-dependent EN trajectory suggests that different program types manage energy differently across their execution: high-energy programs (REGIME_1) deplete energy late, while REGIME_3 programs intensify energy late. But the effect is small and not corpus-wide.

## Cross-References

- C556: ENERGY medial within lines — C664 shows EN is also approximately medial across folios
- C557: daiin line-opener — CC is flat across folio position (not front-loaded at meso level)
- C458: Design freedom — EN trajectory varies by regime (consistent with recovery freedom)
- C563: AX positional sub-structure — AX_FINAL increases late within lines; C664 shows AX increases late within folios too

## Provenance

B_FOLIO_TEMPORAL_PROFILE, Script 1 (folio_temporal_metrics.py), Test 1
