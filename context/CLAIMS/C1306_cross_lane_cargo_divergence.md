# C1306: Cross-Lane Cargo Divergence -- ch and sh Route Different Categories to QO Lane

**Tier:** 2
**Scope:** B
**Phase:** SISTER_CATEGORY_MECHANISM (459)
**Date:** 2026-02-24

## Finding

When ch and sh tokens transition to QO-lane tokens (the next token has a QO PREFIX), the QO-lane token's category profile differs significantly (V=0.122, chi2=33.29, p=2.34e-5). ch routes more STAGING cargo (20.6% vs 12.9%), sh routes more THERMAL cargo (53.6% vs 45.0%).

## Method

- QO PREFIXes defined as: qo, ok, ot, ko, to, po, so, do
- For each ch/sh token at position i, check if token at position i+1 has a QO PREFIX
- Build 2 x 8 contingency table of the NEXT token's category (ch-to-QO vs sh-to-QO)
- N = 2,220 transitions (1,119 ch->QO, 1,101 sh->QO)

## QO Cargo Profiles

| Category | ch->QO cargo | sh->QO cargo | Ratio |
|----------|-------------|-------------|-------|
| THERMAL | 45.0% | 53.6% | 0.84x |
| STAGING | 20.6% | 12.9% | 1.59x |
| FLOW | 18.3% | 16.8% | 1.09x |
| MARKING | 9.5% | 10.4% | 0.91x |
| OPERATION | 2.4% | 1.8% | 1.33x |
| CONTAINMENT | 2.0% | 2.3% | 0.87x |
| TRANSITION | 1.9% | 1.3% | 1.48x |
| MONITORING | 0.4% | 0.9% | 0.49x |

## Self-Category at Transition

The ch/sh token's OWN category also differs at transition points (V=0.115, p=1.37e-4). ch tokens that precede QO-lane tokens are more MARKING-heavy (40.4% vs 38.4%) and CONTAINMENT-heavy (9.2% vs 6.7%). sh tokens at transition are more THERMAL (38.1% vs 29.9%).

## Interpretation

Sister pairs do not just select different vocabulary for themselves -- they influence what the NEXT token carries. ch routes more STAGING/preparation cargo into the QO lane, while sh routes more THERMAL/parameter cargo. This extends the sister pair mechanism beyond self-category into inter-token category routing: the sister pair identity shapes the categorical composition of the downstream execution channel.

## Extends

- C1303 (ch/sh position-independent category) -- extends to cross-token effects
- C1299 (ch/sh B category divergence) -- cargo routing is a downstream consequence
- C932-era (QO-lane transitions) -- categorical dimension of lane transitions

## Falsifiability

Would be falsified if ch->QO and sh->QO cargo profiles were statistically identical (p > 0.05, V < 0.03).

## Evidence

- `phases/SISTER_CATEGORY_MECHANISM/results/sister_category_mechanism.json` (T4_cross_lane_cargo)
