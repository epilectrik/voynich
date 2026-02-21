# C1165: AXM Return Rate Extends AXM Residual Beyond Entry Divergence

**Tier:** 2
**Scope:** B, folio, AXM residual, opener routing
**Phase:** ENTRY_RESET_MECHANISM (Phase 415)
**Depends on:** C1035, C1157, C1158, C1163

## Statement

Per-folio AXM return rate at entry adds dR²=0.111 beyond the entry model (C1035 baseline + entry divergence), F=30.95, p<0.000001, LOO improves 0.543→0.696. The total explained variance of the entry_div + AXM_return bundle is dR²=0.180 beyond C1035 baseline (R²=0.634→0.814, LOO=0.511→0.676). AXM return rate is the single most powerful individual predictor of AXM self-transition discovered in this project (rho=0.841). C1035 residual status: substantially reopened — LOO rises from the original 0.433 (C1035) to 0.676, reducing irreducible variance from ~57% to ~32%.

## Evidence

| Model | R² | LOO |
|-------|-----|-----|
| C1035 baseline | 0.634 | 0.511 |
| + entry_div | 0.703 | 0.543 |
| + entry_div + AXM_return | 0.814 | 0.696 |

**AXM return rate incremental (on entry model):**
- dR²=0.111, F=30.95, p<0.000001
- LOO change: +0.153 (0.543→0.696)

**Total bundle vs C1035:**
- dR²=0.180 (0.634→0.814)
- LOO change: +0.165 (0.511→0.676)

**C1035 status:** LOO improved from 0.433 (original C1035, n=72) to 0.676 (n=65). Irreducible residual reduced from ~57% to ~32%.

**Note:** n=65 vs n=70 (Phase 414) due to MIN_OPENERS=10 filter. Routing_concentration produces identical results (dR²=0.111) as AXM_return_rate because both derive from the same 6-state entry target distribution.

## Structural Implication

The C1035 residual — previously characterized as irreducible program-specific variance — is now substantially explained by a two-predictor bundle: entry divergence (how different are line openings from the interior?) plus AXM return rate (how strongly do openers route back to operational mode?). These capture complementary aspects of the same phenomenon: the per-line "setup cost" of each procedural step. Together they reduce the irreducible fraction from ~57% to ~32%, demonstrating that most of the folio-level dynamical variation is driven by measurable line-opening routing behavior.
