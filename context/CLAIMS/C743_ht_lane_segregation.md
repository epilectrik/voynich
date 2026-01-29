# C743: HT Lane Segregation

**Tier:** 2
**Phase:** HT_RECONCILIATION
**Test:** T4
**Scope:** B

## Statement

HT tokens have a radically different PREFIX lane distribution from classified tokens (chi2=278.71, p=4.02e-60). HT is over-represented in the OTHER lane (+9.5pp) and under-represented in the QO lane (-7.7pp). CHSH and NONE proportions are comparable.

## Evidence

| Lane | HT (n=7,042) | Classified (n=16,054) | Delta |
|------|--------------|----------------------|-------|
| QO | 12.3% | 20.0% | -7.7pp |
| CHSH | 24.4% | 25.6% | -1.2pp |
| OTHER | 47.1% | 37.5% | +9.5pp |
| NONE | 16.3% | 16.9% | -0.6pp |

Chi-squared: 278.71, p = 4.02e-60, dof = 3.

### Top HT Prefixes

| Prefix | HT | Classified | HT-enriched? |
|--------|-----|-----------|---------------|
| ch | 982 | 2,510 | No |
| qo | 863 | 3,206 | Under-represented |
| sh | 734 | 1,595 | No |
| ol | 400 | 475 | Slightly enriched |
| pch | 155 | 90 | Enriched |
| al | 150 | 23 | Highly enriched |
| po | 114 | 22 | Highly enriched |
| so | 100 | 89 | Enriched |

## Interpretation

HT tokens skew toward non-standard prefixes (al, po, pch, so) that are rare in the classified grammar. The QO deficit means HT under-participates in the primary lane. This is consistent with HT being the morphological diversity tail — tokens that use uncommon prefix-MIDDLE combinations not represented in the 49-class system.

## Provenance

- Phase: HT_RECONCILIATION/results/ht_lane_participation.json
- Script: ht_lane_participation.py
- Related: C643-C654 (lane architecture), C341-C348 (HT stratification)
