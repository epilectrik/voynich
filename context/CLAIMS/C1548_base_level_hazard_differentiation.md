# C1548: PREFIX Base-Level Hazard Differentiation (chi2=2038.0, V=0.133)

**Tier:** 2
**Scope:** B, PREFIX, base, hazard, source, enrichment, e-base, a-base, k-base, h-base, o-base, C1536, C1475, C1546
**Phase:** HAZARD_PREFIX_INTEGRATION (Phase 546)
**Date:** 2026-03-06

## Claim

PREFIX bases show significant hazard source rate differentiation (chi-squared=2038.0, V=0.133). e-base is most hazard-enriched at 3.37x (22.4% source rate), a-base at 2.00x (13.3%), while k-base is most depleted at 0.30x (2.02%) and t-base at 0.36x (2.39%). The hazard gradient tracks the HEAD domain structure (C1475, C1536) because each base selects a different HEAD distribution, and HEAD presence categorically blocks hazard sourcing (C1546). However, the base effect operates THROUGH headless tokens — within headless tokens of each base, hazard rates still differ, indicating base carries independent hazard routing beyond HEAD selection alone.

## Evidence

### Base hazard source profiles (B corpus, Phase 546)

| Base | Total tokens | Source tokens | Source rate | Enrichment vs mean |
|---|---|---|---|---|
| e-base | 598 | 134 | 22.40% | 3.365x |
| a-base | 2,220 | 296 | 13.33% | 1.999x |
| BARE | 3,363 | 276 | 8.21% | 1.233x |
| o-base | 5,207 | 416 | 7.99% | 1.200x |
| l-base | 1,031 | 78 | 7.57% | 1.136x |
| r-base | 154 | 8 | 5.19% | 0.780x |
| h-base | 4,826 | 229 | 4.75% | 0.713x |
| t-base | 419 | 10 | 2.39% | 0.359x |
| k-base | 4,952 | 100 | 2.02% | 0.304x |

Chi-squared = 2038.0, Cramer's V = 0.133, p < 0.0001.

### Headless mediation

Within each base, headed tokens universally have 0% source rate (C1546). The base-level rates above are driven entirely by the headless fraction within each base:
- e-base: 22.4% headless source rate (but only 598 total tokens — small base)
- k-base: headless tokens have 2.02% source rate (k-base is 62.6% k-HEAD = low headless proportion)
- a-base: headless tokens have 13.3% source rate (a-base is 8.5% a-HEAD = high headless proportion)

The base effect is partly mediated by HEAD selection (bases with more headed tokens have lower aggregate hazard) and partly independent (headless hazard rates differ across bases).

## Interpretation

PREFIX base creates a hazard gradient by two mechanisms: (1) INDIRECT — bases selecting more HEAD atoms produce lower aggregate hazard because HEAD is categorically immune; (2) DIRECT — even among headless tokens, different bases route to different MIDDLE vocabularies with different hazard profiles. e-base PREFIXes feed into e-initial headless MIDDLEs that include hazard sources like 'he'. k-base PREFIXes channel through k-HEAD immunity at 62.6% and route remaining headless tokens to low-hazard configurations. This connects C1536 (base-to-HEAD selection) with the hazard topology.

## Falsification Criteria

1. If base-level hazard differentiation disappears after controlling for HEAD proportion
2. If chi-squared drops below significance after section/REGIME stratification
3. If headless hazard rates are uniform across bases (currently they differ from 2% to 22%)

## Source

`phases/HAZARD_PREFIX_INTEGRATION/results/hazard_prefix_integration.json`
