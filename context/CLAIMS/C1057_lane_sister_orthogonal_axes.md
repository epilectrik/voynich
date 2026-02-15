# C1057: Lane-Sister Orthogonal Axes

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** RUPESCISSA_REVERSE_TEST (Phase 376)
**Extends:** C574 (EN distributional convergence), C412 (sister-QO anticorrelation)
**Relates to:** C639 (sister pair variance decomposition), C604 (C412 REGIME mediation), C605 (lane activation)

---

## Statement

Lane balance (QO/CHSH proportion) and sister preference (ch/sh choice) are **independent folio-level decisions**: partial correlation r=-0.064 after controlling for QO density. The raw correlation (rho=0.210, p=0.058) vanishes entirely when the shared QO component is partialed out.

| Measure | Value | n |
|---------|-------|---|
| Raw rho (lane vs ch_pref) | 0.210 | 82 folios |
| Raw p | 0.058 | |
| Partial r (controlling QO density) | **-0.064** | 82 folios |
| PCA significant PCs (Kaiser) | **2** | 3 variables |
| ok/ot vs lane (rho) | 0.143 (p=0.200) | NS, not independent |
| ok/ot vs ch_pref (rho) | 0.200 (p=0.072) | NS, not independent |

Two orthogonal control dimensions confirmed:
1. **WHICH EN subfamily** to deploy (QO k-energy vs CHSH e-stability)
2. **WHICH sister variant** within CHSH (ch active testing vs sh passive monitoring)

ok/ot preference is NOT a third independent axis.

---

## Interpretation

C412 documented an anticorrelation (rho=-0.326) between ch-preference and qo-density, and C604 showed 27.6% was REGIME-mediated. This constraint goes further: once QO density is controlled, lane balance and sister preference are completely decoupled (r=-0.064, effectively zero).

This means each folio (program) makes two independent decisions about its operational profile: (1) what balance of energy-application vs stability-maintenance operations (lane), and (2) what balance of active-testing vs passive-monitoring within the stability lane (sister). These are orthogonal design axes, not a single continuum.

The absence of a third axis (ok/ot) is also informative: ok and ot do not form an independent oppositional pair like QO/CHSH or ch/sh. Their distribution is driven by the same factors that drive lane balance.

---

## Method

- 82 B folios with >= 30 prefixed tokens
- Per-folio: qo_proportion, lane_balance (CHSH/(QO+CHSH)), ch_preference (ch/(ch+sh)), ok_preference (ok/(ok+ot))
- Partial correlation: residual method (rank-transform, regress out QO density, correlate residuals)
- PCA on 3 independent measures (lane_balance, ch_preference, ok_preference; qo_density excluded due to near-algebraic redundancy with lane_balance, rho=-0.862)
- Kaiser criterion for significant PCs (eigenvalue > 1.0)

**Script:** `phases/RUPESCISSA_REVERSE_TEST/scripts/rupescissa_reverse_test.py`
**Results:** `phases/RUPESCISSA_REVERSE_TEST/results/test3_oppositional_pairing.json`
