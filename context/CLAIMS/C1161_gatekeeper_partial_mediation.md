# C1161: Gatekeeper Classes Partially Mediate Boundary Divergence

**Tier:** 2
**Scope:** B, line, gatekeeper, AXM residual
**Phase:** BOUNDARY_DIVERGENCE_DECOMPOSITION (Phase 414)
**Depends on:** C1007, C1157, C1158

## Statement

Excluding gatekeeper class transitions ({15, 20, 21, 22, 25}) from boundary divergence computation reduces the AXM residual effect by 30.5% (dR² drops from 0.0845 to 0.0587, F=8.21, p=0.006). The effect survives gatekeeper removal: gatekeeper-free boundary divergence still correlates with AXM self-transition (rho=-0.673, p<0.0001) and adds significant explanatory power (LOO 0.386→0.435). Gatekeeper density itself is nearly uncorrelated with boundary divergence (rho=0.016) and does not correlate with AXM (rho=0.051, p=0.073). Controlling for gatekeeper density barely changes the BD-AXM relationship (partial rho=-0.745).

## Evidence

| Model | dR² | F | p | LOO R² |
|-------|-----|---|---|--------|
| Original BD (n=70) | 0.085 | 14.15 | 0.0004 | 0.512 |
| GK-free BD (n=66) | 0.059 | 8.21 | 0.006 | 0.435 |
| **Drop** | **30.5%** | | | |

**Gatekeeper density:** Mean 2.4% of tokens (5.2% of AXM tokens). Effectively uncorrelated with BD (rho=0.016).

**n=66 after exclusion:** 4 folios lost (dropped below MIN_ZONE_TRANS=10 threshold in at least one zone after gatekeeper removal).

## Structural Implication

The gatekeeper mechanism (C1007) contributes ~30% of boundary divergence's predictive power. The remaining ~70% comes from non-gatekeeper transition routing — the way ordinary AXM, AXm, FQ, CC, and FL classes change their routing patterns at line boundaries. This is consistent with C1158's finding that entry (not exit) dominates: gatekeepers are exit-enriched (C1007), so their removal preferentially weakens exit divergence while leaving the dominant entry component intact. Boundary divergence captures a broader positional routing phenomenon that partially overlaps with but is not reducible to the gatekeeper mechanism.
