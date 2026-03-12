# Phase 583: ZODIAC_SEASONAL_CATEGORY — Zodiac Seasonal Category Clustering Test

**Status:** COMPLETE
**Verdict:** SEASONAL_SIGNAL_WEAK
**Constraints:** C1681-C1684
**Runtime:** 5.67s

## Summary

Tests whether AZC zodiac page vocabulary clusters by season when classified into the 8 operational categories (C1250). Motivated by Brunschwig 1512 zodiac-conditional apparatus instructions and C322 (SEASON-GATED WORKFLOW). The apparatus-configuration hypothesis predicted THERMAL and CONTAINMENT categories should show seasonal variation.

## Results

| Test | Statistic | p-value | Verdict |
|------|-----------|---------|---------|
| Chi-squared (4×8) | χ²=51.84, V=0.108 | p=0.0002 | SIGNIFICANT |
| Permutation (10K) | 785/10000 ≥ obs | p=0.079 | NOT CONFIRMED |
| THERMAL gradient | H=4.55 | p=0.208 | not significant |
| CONTAINMENT gradient | H=0.48 | p=0.924 | not significant |
| STAGING gradient | H=9.31 | p=0.026 | SIGNIFICANT |
| Seasonal JSD gradient | U=4.0 | p=0.600 | NO gradient |
| Within/between coherence | U=629 | p=0.115 | NOT coherent |

## Constraint Verdicts

| ID | Claim | Status |
|----|-------|--------|
| C1681 | SEASONAL_CATEGORY_SIGNAL_WEAK | Token-level χ² significant (p=0.0002, V=0.108) but permutation marginal (p=0.079) |
| C1682 | THERMAL_SEASONAL_GRADIENT_ABSENT | THERMAL (p=0.208) and CONTAINMENT (p=0.924) not seasonal |
| C1683 | WITHIN_SEASON_COHERENCE_ABSENT | Within-season JSD (0.024) < between (0.029) but not significant (p=0.115) |
| C1684 | STAGING_SEASONAL_GRADIENT | Only category with significant seasonal variation: Spring 16.9% → Winter 8.2% (p=0.026) |

## Key Findings

1. **Token-level category variation EXISTS across zodiac pages** (χ²=51.84, p=0.0002) but does not survive folio-level permutation testing (p=0.079). The signal is real but weak — it's folio-specific variation, not cleanly seasonal clustering.

2. **The apparatus-configuration prediction FAILS.** THERMAL and CONTAINMENT categories — the ones most directly tied to heat regime and seal quality — show no significant seasonal variation. The hypothesis that zodiac pages encode seasonal apparatus legality via these channels is not supported.

3. **STAGING is the only significant category** (p=0.026): declines monotonically from Spring (16.9%) to Winter (8.2%). TRANSITION shows an inverse pattern (Spring 22.1% → Winter 32.2%) but doesn't reach significance (p=0.18).

4. **No gradient structure**: adjacent seasons aren't more similar than distant ones, ruling out smooth seasonal transitions in category composition.

5. **C322 stands but mechanism unclear.** The season-gated workflow constraint is still valid (from vocabulary overlap analysis), but category-level evidence for apparatus-configuration seasonal gating is absent. Whatever drives seasonal vocabulary variation, it's not operating through the THERMAL/CONTAINMENT channels.

## Scripts

| Script | Runtime |
|--------|---------|
| `scripts/zodiac_seasonal_category.py` | 5.67s |

## Files

- `results/zodiac_seasonal_category.json` — Full statistical output
