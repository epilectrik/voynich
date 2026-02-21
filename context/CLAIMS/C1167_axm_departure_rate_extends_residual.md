# C1167: AXM Departure Rate at Exit Extends Residual

**Tier:** 2
**Scope:** B, folio, AXM residual, exit
**Phase:** EXIT_DIVERGENCE_SYMMETRY (Phase 416)
**Depends on:** C1035, C1158, C1163, C1165, C1166

## Statement

AXM departure rate at exit (fraction of exit-zone transitions with SOURCE in AXM leaving to non-AXM states) carries independent signal beyond the entry bundle (C1035 baseline + entry_div + AXM_return). Adding AXM departure rate: dR²=0.035, F=11.80, p=0.0012, LOO improves from 0.696 to 0.745. This is the strongest single exit feature; raw jsd_exit adds nothing (dR²≈0, C1166) but the directional routing metric succeeds. Closer routing features collectively explain R²=0.338 of exit divergence variance, with AXM departure rate as the dominant component (rho=0.509 with exit div).

## Evidence

| Metric | Value |
|--------|-------|
| Entry bundle R² (LOO) | 0.814 (0.696) |
| + jsd_exit: dR² | 0.000 (F=0.002, p=0.963) |
| + AXM departure: dR² | 0.035 (F=11.80, p=0.0012) |
| + AXM departure: LOO | 0.745 (+0.049) |
| + all exit features: dR² | 0.042 (F=4.71, p=0.006) |
| + all exit features: LOO | 0.712 |
| AXM departure mean (std) | 0.410 (0.177) |
| AXM departure vs exit div rho | 0.509 (p<0.0001) |
| AXM departure vs AXM self rho | -0.687 (p<0.0001) |
| Closer features R² on exit div | 0.338 |
| Best exit feature | axm_departure |

## Interpretation

Exit-specific information is captured NOT by aggregate divergence (JSD) but by directional routing: how strongly programs depart AXM state at line endings. High AXM departure = program leaves operational mode at exit = more complex closure behavior. This complements C1163 (AXM return rate at entry) — entry measures how quickly programs enter AXM, exit measures how readily they leave it. The two are mechanistically independent channels.

## Provenance

- Phase 416 Tests 2+4: CLOSER_ROUTING_PROFILE + EXIT_INCREMENTAL_SIGNAL
- Script: `phases/EXIT_DIVERGENCE_SYMMETRY/scripts/exit_divergence_symmetry.py`
- Results: `phases/EXIT_DIVERGENCE_SYMMETRY/results/exit_divergence_symmetry.json` → test2_closer_routing_profile, test4_exit_incremental_signal
