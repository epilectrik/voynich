# C1186: Sister Preference Is Coupled to Entry Boundary Divergence

**Tier:** 2
**Scope:** B, sister pairs, boundary dynamics
**Phase:** SISTER_PAIR_MECHANISM (Phase 420)
**Depends on:** C639, C1158, C1162

## Statement

ch-heavy folios have more divergent entry dynamics: partial Spearman rho=0.312 (p=0.004) between ch_preference and entry JSD (controlling for section). Opener ch fraction correlates strongly with folio ch_preference (partial rho=0.455). AXM return rate at entry shows no significant coupling (partial rho=0.106, p=0.343). The boundary coupling is specifically through entry DIVERGENCE, not entry AXM composition.

## Evidence

| Metric | Partial rho | p-value |
|--------|------------|---------|
| Entry JSD (entry vs interior) | +0.312 | 0.004 |
| AXM return rate at entry | +0.106 | 0.343 |
| Opener ch fraction | +0.455 | <0.001 |

n=82 folios, all controlling for section.

## Interpretation

ch-heavy programs have more heterogeneous line-opening sequences (higher entry JSD). This connects sister choice to boundary mechanisms (C1157-C1168): programs that use more active testing (ch) also have more diverse entry dynamics, suggesting that active-test style programs require more varied initialization sequences. The strong opener-ch correlation (rho=0.455) confirms that sister preference is especially concentrated at line boundaries, where it modulates the diversity of entry routing patterns.

## Provenance

- Phase 420 Test 7: BOUNDARY_DIVERGENCE
- Script: `phases/SISTER_PAIR_MECHANISM/scripts/sister_pair_mechanism.py`
- Results: `phases/SISTER_PAIR_MECHANISM/results/sister_pair_mechanism.json` -> test7_boundary_divergence
