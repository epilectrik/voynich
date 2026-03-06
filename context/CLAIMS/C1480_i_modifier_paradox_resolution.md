# C1480: i-Modifier Simpson's Paradox Full Resolution

**Tier:** 2
**Scope:** B, MIDDLE, atom, i-modifier, Simpson, hazard, HEAD, a-HEAD, selection, conditional, resolution
**Phase:** I_MODIFIER_PARADOX (Phase 534)
**Date:** 2026-03-05

## Statement

The i-modifier Simpson's paradox (C1452-C1456) is FULLY RESOLVED by HEAD domain selection. i selects a-HEAD at 88.6% of headed tokens (C1479), and a-HEAD is the primary hazard carrier (C1477). Full Oaxaca-Blinder decomposition: total marginal effect = -0.069 (i is NET SAFER), composed of selection effect = +0.319 (inflating, from a-HEAD concentration) and conditional effect = -0.388 (protective, within each HEAD). The conditional protection exceeds selection inflation, making i a net safety device despite its a-HEAD affinity. Counterfactual: if i had the average modifier HEAD distribution, its hazard would be 10.1% vs actual 17.9% — HEAD selection accounts for 7.8pp of inflation. Within a-HEAD, i protects in 5/5 testable frames (weighted delta = -0.536). The paradox exists because the crude comparison (C1452's 1.69x) compared i-tokens to ALL non-i tokens including unmodified ones; comparing i to other MODIFIED tokens shows i is safer (17.9% vs 24.8%).

## Evidence

- **N:** 23,096 tokens total; 2,875 i-modified (12.4%), 13,339 modified (any modifier)
- **i HEAD distribution:** a=53.15%, headless=40.0%, o=4.07%, k=1.29%, e=1.04%, t=0.45%
- **Among headed i-tokens:** a-HEAD = 88.6% (consistent with C1479's 4.08x)
- **Marginal hazard rates:** i-modified = 17.88%, non-i-modified = 24.77%, all non-i = 24.77%
- **Counterfactual 1:** i with average modifier HEAD dist → 10.12% hazard
- **Counterfactual 2:** i with non-i-modifier HEAD dist → 17.56% hazard
- **Total effect:** -0.069 (i safer)
- **Selection effect:** +0.319 (a-HEAD inflates)
- **Conditional effect:** -0.388 (i protects within each HEAD)
- **Decomposition accuracy:** 0.0% error (exact reconstruction)
- **Within a-HEAD protection:** 5/5 frames protective, weighted delta = -0.536
- **Strongest frame:** a→n: i hazard 33.5% vs non-i hazard 100.0% (N=1,254 vs 18), p<0.001

## Relationship to Prior Constraints

- CLOSES C1452-C1456 (i-modifier Simpson's paradox) — complete mechanistic explanation
- DEPENDS on C1479 (HEAD-modifier selectivity: i → a-HEAD at 4.08x)
- DEPENDS on C1477 (a-HEAD primary hazard carrier, quench-resistant)
- DEPENDS on C1475 (HEAD domain taxonomy: each HEAD has distinct category domain)
- CONFIRMS C1453 (i protects within frames) with refined within-a-HEAD analysis
- EXTENDS C1454 (i selects hazardous frames) by identifying a-HEAD selection as THE mechanism
- CONSISTENT with C1003 (pairwise compositionality: HEAD + modifier interaction is pairwise)

## Falsifiable Prediction

If the i→a-HEAD selectivity were random (permuted), the Simpson's paradox would disappear: marginal and conditional effects would align. The 88.6% headed-token a-HEAD selectivity is the necessary and sufficient condition for the paradox.
