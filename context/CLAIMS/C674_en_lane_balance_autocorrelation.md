# C674: EN Lane Balance Autocorrelation

**Status:** VALIDATED | **Tier:** 0 | **Phase:** B_LINE_SEQUENTIAL_STRUCTURE | **Scope:** B

## Finding

QO fraction (EN lane balance) shows significant raw lag-1 autocorrelation (rho=0.167, p<1e-6) that persists after position control (partial rho=0.162, p<1e-6). However, permutation test within folios returns p=1.0 — the autocorrelation is **entirely folio-driven**, not sequentially propagated.

## Method

For lines with >=3 EN tokens: compute QO fraction = QO/(QO+CHSH). Lag-1 autocorrelation for strictly consecutive lines. Partial correlation: residualize both QO_N and QO_N+1 against norm_pos_N+1. Permutation: shuffle QO fractions within folio 1000 times, recompute lag-1 rho.

## Key Numbers

| Metric | Value |
|--------|-------|
| Eligible lines (>=3 EN) | 1,331 |
| Consecutive pairs | 870 |
| Raw lag-1 rho | 0.167 (p=7.6e-7) |
| Partial lag-1 rho (position-controlled) | 0.162 (p=1.5e-6) |
| Lag-2 rho | 0.222 (p=2.4e-10) |
| Lag-3 rho | 0.212 (p=3.8e-9) |
| Permutation mean rho | 0.143 |
| Permutation p (two-sided) | 1.000 |

## Interpretation

The autocorrelation structure reveals **folio-level lane configuration**, not line-to-line state memory. Key evidence:

1. Lag-2 (0.222) and lag-3 (0.212) are STRONGER than lag-1 (0.167). Sequential coupling would show decay; folio-level clustering shows flat or increasing correlations at longer lags.
2. Permutation within folios produces equivalent correlations (0.143 vs 0.167, p=1.0). The signal is fully explained by lines sharing the same folio's lane balance configuration.

Each folio has a characteristic QO fraction (determined by REGIME and folio-specific conditions). Lines sample from this folio-level parameter, not from the previous line's value. This extends C608 (no lane coherence, p=0.963) from binary classification to continuous autocorrelation.

## Provenance

- Script: `phases/B_LINE_SEQUENTIAL_STRUCTURE/scripts/line_sequential_coupling.py` (Test 5)
- Extends: C608 (no lane coherence), C668 (QO fraction declines late within folios)
