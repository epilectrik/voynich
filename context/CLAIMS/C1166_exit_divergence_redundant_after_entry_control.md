# C1166: Exit Divergence Redundant After Entry Control

**Tier:** 2
**Scope:** B, line, boundary, exit
**Phase:** EXIT_DIVERGENCE_SYMMETRY (Phase 416)
**Depends on:** C1035, C1157, C1158, C1163, C1165

## Statement

Per-folio exit divergence (JSD of exit-zone transition matrix vs interior) loses all predictive signal for AXM self-transition rate after controlling for the entry bundle (entry divergence + AXM return rate). Bivariate rho(jsd_exit, AXM) = -0.710 is strong, but partial rho controlling for entry bundle = -0.097 (p=0.101). Exit JSD and entry JSD are highly collinear (rho=0.697). The aggregate exit divergence metric captures the same routing information already explained by entry divergence.

## Evidence

| Metric | Value |
|--------|-------|
| n_folios | 65 |
| jsd_exit mean (std) | 0.168 (0.091) |
| jsd_entry mean (std) | 0.164 (0.087) |
| Bivariate rho(entry, exit) | 0.697 (p<0.0001) |
| Bivariate rho(exit, AXM) | -0.710 (p<0.0001) |
| Bivariate rho(entry, AXM) | -0.676 (p<0.0001) |
| Partial rho(exit, AXM \| entry) | -0.194 (p=0.062) |
| Partial rho(exit, AXM \| entry bundle) | -0.097 (p=0.101) |
| Verdict | EXIT_REDUNDANT |

## Interpretation

Entry and exit divergence measure structurally similar phenomena — both capture how strongly boundary transitions deviate from interior routing. Because entry divergence enters the model first (C1158: entry dominates 3.5×), exit JSD adds nothing new. This does NOT mean exit is uninformative — it means the JSD metric is collinear. Exit-specific mechanisms (AXM departure rate, closer routing) carry independent signal through different metrics (see C1167).

## Provenance

- Phase 416 Test 1: EXIT_DIVERGENCE_BASELINE
- Script: `phases/EXIT_DIVERGENCE_SYMMETRY/scripts/exit_divergence_symmetry.py`
- Results: `phases/EXIT_DIVERGENCE_SYMMETRY/results/exit_divergence_symmetry.json` → test1_exit_divergence_baseline
