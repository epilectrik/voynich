# C1569: Section-Level Within-Domain Parameterization

**Tier:** 2
**Scope:** B, MIDDLE, atom, HEAD, domain, compositional, section, parameterization, folio, within-section, C1475, C1556, C1563, C1567, C1568
**Phase:** WITHIN_DOMAIN_COMPOSITIONAL_CONTROL (Phase 560)
**Date:** 2026-03-08

## Claim

Folio specificity extends into within-domain parameterization at section level. Manuscript sections (Herbal, Bio, Stars, Cosmo, Pharma, Text) have systematically different within-domain control dial settings. However, within-section folio-to-folio resolution is not established — folios within the same section are indistinguishable by their within-domain profiles.

This means:
1. Section identity is a real signal in within-domain tuning (D1: 76.8%, D2: 15/32 features significant)
2. Folio specificity within sections lives primarily in domain mix (HEAD proportions), not within-domain parameterization (D3: 0/3 sections show within-section differentiation, D4: ARI = -0.024)
3. Paragraph-level differentiation is suggestive but borderline (D6a: 28.8% of folios, threshold 30%; D6b: 8 folios show gradient alignment)

## Evidence

### Section discrimination (D1)

| Metric | Value |
|---|---|
| Within-domain feature section accuracy | 76.8% |
| Null accuracy (domain-shuffled) | 52.7% +/- 4.9% |
| Separation | 4.9 sigma |

### Feature variance (D2)

15 of 32 within-domain features show significant section-level variance (ANOVA F > 3.2).

### Within-section resolution (D3)

| Section | Folios | Real dist | Null dist | Result |
|---|---|---|---|---|
| Stars | 23 | 7.856 | 7.912 +/- 0.017 | NOT DISTINGUISHABLE |
| Herbal | 32 | 7.352 | 7.400 +/- 0.019 | NOT DISTINGUISHABLE |
| Bio | 20 | 7.919 | 7.905 +/- 0.019 | NOT DISTINGUISHABLE |

Within each section, the pairwise distance between folio feature vectors is NOT larger than expected from shuffling within-domain tokens across folios (preserving domain counts). Folios within sections share the same within-domain profile.

### Clustering (D4)

Adjusted Rand Index = -0.024 (threshold > 0.10). Single-linkage clustering of 82 folio vectors does not recover section structure.

### Paragraph differentiation (D6)

- D6a: 17/59 (28.8%) qualifying folios show significant paragraph-level domain profile differentiation at p < 0.05. Below 30% threshold but borderline.
- D6b: 8 folios show strong Spearman correlation (|rho| > 0.7) between paragraph rank and C1398 gradient axes.

## Interpretation

The within-domain control system has a two-level architecture:
1. **Section level:** Shared within-domain parameterization across all folios in a section. Stars folios, for example, all use similar ARRANGEMENT terminal allocation and FLOW modifier rates.
2. **Folio level:** Individual folios differ from each other primarily through domain MIX (HEAD proportions), not through within-domain tuning.

This is consistent with the manuscript's organizational logic: sections correspond to different operational contexts (different plant types, different procedures, different celestial configurations), and each context has a characteristic within-domain profile. Individual folios within a section specify different PROGRAMS (different domain mixes) but execute each domain in the same section-characteristic way.

The borderline paragraph differentiation (D6a) suggests there may be a third level — paragraph-as-subroutine with different within-domain emphasis — but this is not yet confirmed at the 30% threshold.

## Falsification Criteria

1. If a richer feature set (more than 32 features) reveals within-section folio resolution that D3 missed
2. If section labels are not the right grouping variable (e.g., if bifolio pairs or quire boundaries produce sharper within-domain clusters)
3. If paragraph-level analysis with more sensitive methods crosses the 30% threshold

## Source

`phases/WITHIN_DOMAIN_COMPOSITIONAL_CONTROL/results/t3_cross_folio_discriminability.json`
