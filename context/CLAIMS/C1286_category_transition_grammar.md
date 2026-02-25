# C1286: Category Transition Grammar is Structured

**Tier:** 2
**Scope:** B
**Phase:** CATEGORY_MECHANISM_DECOMPOSITION (Phase 455)
**Date:** 2026-02-24

## Statement

The 8x8 category-to-category transition matrix departs massively from independence. Chi2=526.1, V=0.060, p=3.75e-81. Self-transitions enriched: MARKING (+10.4 residual), THERMAL (+6.0), FLOW (+4.6). Key asymmetries: FLOW->TRANSITION enriched (+6.7), OPERATION->THERMAL enriched (+6.5), THERMAL->TRANSITION depleted (-3.4), FLOW->THERMAL depleted (-7.3). N=20,656 categorized bigrams.

## Architecture

- **Categories organize sequential flow.** Operations persist within their theme (self-transition enrichment) and follow preferred pathways between themes. This extends C877 (role transition grammar) to the category level.
- **Operational sequencing.** FLOW->TRANSITION (+6.7): flow/transfer operations lead to closing/finalizing. OPERATION->THERMAL (+6.5): work leads to heating. THERMAL->TRANSITION (-3.4): heating does not lead directly to closing. Matches process control logic.
- **FLOW->THERMAL depleted (-7.3).** Strongest depletion. Flow/transfer operations do not directly feed into heating. Consistent with phase separation in process control.
- **Asymmetric pathways.** FLOW->TRANSITION (779) vs TRANSITION->FLOW (525): flow leads to closing more than closing leads to flow. Directional process structure.

## Key Transitions

| Pathway | Residual | Interpretation |
|---------|----------|----------------|
| MARKING -> MARKING | +10.4 | Strongest self-loop |
| FLOW -> TRANSITION | +6.7 | Transfer -> close |
| OPERATION -> THERMAL | +6.5 | Work -> heat |
| THERMAL -> THERMAL | +6.0 | Sustained heating |
| FLOW -> FLOW | +4.6 | Sustained transfer |
| FLOW -> THERMAL | -7.3 | No direct flow -> heat |
| OPERATION -> TRANSITION | -4.7 | No direct work -> close |
| THERMAL -> MARKING | -4.5 | No direct heat -> mark |

## Provenance

- Extends C877 (role transition grammar EN->EN 38.5%) to category level
- Extends C1278 (category adds 18.6% class entropy beyond PREFIX) with sequential structure
- Connects C1277 (THERMAL escape) and C1285 (TRANSITION anti-escape) via transition pathways
