# C1163: AXM Return Rate Dominates Entry Mechanism

**Tier:** 2
**Scope:** B, line, opener, routing, AXM
**Phase:** ENTRY_RESET_MECHANISM (Phase 415)
**Depends on:** C1158, C1159, C976

## Statement

The per-folio AXM return rate at entry — the fraction of entry transitions (position 0→1) with target in AXM macro-state — correlates with AXM self-transition at rho=0.841 (p<0.0001) and with entry divergence at rho=-0.510 (p<0.0001). It explains 31.8% of entry divergence variance (R²=0.318, 19% increment over role model). The entry mechanism is fundamentally about how strongly the opener routes the system back to operational mode, not about what role or PREFIX the opener carries. AXM return rate mean=0.707, std=0.134 across 65 folios.

## Evidence

| Metric | Value |
|--------|-------|
| AXM return rate vs AXM self-transition | rho=0.841, p<0.0001 |
| AXM return rate vs entry divergence | rho=-0.510, p<0.0001 |
| R² (entry_div ~ routing features) | 0.318 |
| R² increment over role model | 0.190 |
| Routing concentration vs entry div | rho=-0.510, p<0.0001 |

**Global entry routing deltas (vs interior):**

| Transition | Delta |
|-----------|-------|
| AXm→AXM | +0.124 |
| FQ→AXM | +0.103 |
| FL_SAFE→CC | -0.115 |
| AXm→FQ | -0.092 |
| FL_SAFE→FL_HAZ | +0.090 |

## Structural Implication

C1159 showed boundary divergence is a routing shift, not AXM persistence decay. C1163 identifies the specific routing dimension: the fraction of entry transitions that route back to AXM. Folios with high AXM return (>0.80) have minimal setup at line openings — the opener immediately returns the system to operational mode. Folios with low AXM return (<0.55) route openers to control, frequency, or hazard states — each step requires substantial setup before work resumes. The rho=0.841 with AXM self-transition means this per-line opening routing pattern is nearly the same information as the folio's overall dynamical character.
