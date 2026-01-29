# C668: Lane Balance Trajectory

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

## Finding

QO fraction among EN tokens **declines from early to late lines** within folios (rho=-0.058, p=0.006, KW H=9.52, p=0.023). Programs shift from 46.3% QO in Q1 to 41.3% QO in Q4 — a 5.0 percentage-point CHSH-ward drift.

This trajectory is regime-dependent: REGIME_1/2/3 all show QO decline (strongest in REGIME_2: -9.9pp), while REGIME_4 is flat or slightly QO-increasing (+1.4pp).

## Evidence

### Corpus-Wide Lane Trajectory (2244 lines with QO+CHSH EN tokens)

| Quartile | QO Fraction |
|----------|------------|
| Q1 | 0.4633 |
| Q2 | 0.4125 |
| Q3 | 0.4350 |
| Q4 | 0.4129 |

Spearman rho = -0.058, p = 0.006. KW H = 9.52, p = 0.023.

### Regime Stratification

| Regime | N lines | QO Q1 | QO Q4 | Slope |
|--------|---------|-------|-------|-------|
| REGIME_1 | 799 | 0.499 | 0.422 | **-0.077** |
| REGIME_2 | 566 | 0.423 | 0.324 | **-0.099** |
| REGIME_3 | 171 | 0.436 | 0.388 | -0.048 |
| REGIME_4 | 708 | 0.463 | 0.478 | +0.014 |

REGIME_2 shows the strongest CHSH-ward drift: from 42.3% QO early to 32.4% QO late.

## Interpretation

Programs shift from energy-emphasis (QO-heavier) early to stabilization-emphasis (CHSH-heavier) late. This is the strongest meso-temporal signal in the dynamics tests.

The QO lane carries ENERGY_MODULATOR (k) affinity (C647: 70.7% k in QO MIDDLEs). The CHSH lane carries STABILITY_ANCHOR (e) affinity (68.7% e). The late CHSH gain means programs transition from energy application toward stabilization as they progress — consistent with convergence behavior.

REGIME_4 is the exception: its lane balance is stable throughout. REGIME_4 is the precision-constrained regime (C494), which may maintain tighter lane discipline. REGIME_2 (steady-state vigilance) shows the largest drift, suggesting its programs most aggressively transition from energy to stabilization.

## Cross-References

- C643: Lane hysteresis oscillation (alternation rate 0.563) — the oscillation continues throughout, but its baseline shifts CHSH-ward
- C645: CHSH post-hazard dominance (75.2%) — post-hazard CHSH dominance is constant across quartiles (C667)
- C647: Morphological lane signature (QO=k, CHSH=e) — the QO decline means k-affinity tokens decline late
- C494: REGIME_4 precision axis — REGIME_4 uniquely maintains lane balance, consistent with precision constraint

## Provenance

B_FOLIO_TEMPORAL_PROFILE, Script 2 (folio_temporal_dynamics.py), Test 5
