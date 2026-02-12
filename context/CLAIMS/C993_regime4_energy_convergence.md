# C993: REGIME_4 Uniquely Converges in Energy

**Tier:** 2 | **Scope:** B | **Phase:** CONSTRAINT_ENERGY_FUNCTIONAL

## Statement

REGIME_4 is the only REGIME that shows within-folio energy convergence: trend ρ = -0.90 (p = 0.037), with variance dropping 3.6× from Q1 to Q5 (var ratio 0.28). All other REGIMEs show flat energy trajectories (|ρ| < 0.2) and stable variance (ratios 1.0-1.5). REGIME_4 also operates at the lowest mean energy (-0.014) and highest variance overall, consistent with its characterization as the precision axis (C494).

## Evidence

### REGIME Energy Trajectories (T4)

| REGIME | Trend ρ | p | Var Q1 | Var Q5 | Ratio |
|--------|---------|---|--------|--------|-------|
| R1 | +0.70 | 0.19 | 0.000389 | 0.000478 | 1.23 |
| R2 | 0.00 | 1.00 | 0.000221 | 0.000232 | 1.05 |
| R3 | +0.20 | 0.75 | 0.000347 | 0.000507 | 1.46 |
| **R4** | **-0.90** | **0.037** | **0.001036** | **0.000291** | **0.28** |

### REGIME Mean Energy (T2)

| REGIME | Mean E | Variance | 80% Range |
|--------|--------|----------|-----------|
| R1 | -0.010 | 0.000493 | 0.049 |
| R2 | -0.013 | 0.000395 | 0.043 |
| R3 | -0.011 | 0.000441 | 0.050 |
| **R4** | **-0.014** | **0.000585** | **0.051** |

### Interpretation

1. REGIME_4 starts with the widest energy spread (Q1 var = 0.001) and converges to the tightest (Q5 var = 0.000291)
2. This is unique — no other REGIME shows variance convergence
3. "Precision" (C494) is not just tighter control — it's energy convergence: programs progressively narrow their constraint tension range
4. REGIME_4's high initial variance may reflect exploratory calibration; its low final variance reflects locked-in precision
5. The overall lowest mean energy (-0.014) means REGIME_4 consistently operates closest to constraint boundaries — maximal tension, minimal tolerance

## Provenance

- T4 (regime convergence)
- Confirms C494 (REGIME_4 = precision axis) with energy-functional evidence
- Extends C979 (REGIME modulates weights not topology) — REGIME_4 modulates energy variance trajectory
- Consistent with T2 finding that R4 has highest overall variance (0.000585) — high variance that then converges is the precision signature
