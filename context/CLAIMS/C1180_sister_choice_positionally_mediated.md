# C1180: Sister Choice Is Positionally Mediated (+12.8% Variance)

**Tier:** 2
**Scope:** B, sister pairs, positional structure
**Phase:** SISTER_PAIR_MECHANISM (Phase 420)
**Depends on:** C639, C929

## Statement

Within-line position mediates sister-pair choice, absorbing 12.8% additional variance beyond section alone (delta-R2=0.128, LOO-confirmed delta=0.097). ch-prefixed tokens occupy later line positions (mean 0.487) vs sh-prefixed tokens earlier (mean 0.395), gap=0.092. This extends C929's observation (ch=active test at 0.515, sh=passive monitor at 0.396) from a behavioral characterization to a quantitative variance predictor. Position variables (position gap, opener ch fraction, early/late bin asymmetry) together reduce C639's unexplained mass from 52.9% to approximately 40%.

## Evidence

| Metric | Value |
|--------|-------|
| Folios tested | 82 |
| Global ch mean position | 0.487 |
| Global sh mean position | 0.395 |
| Position gap | 0.092 |
| Section-only R2 | 0.355 (LOO: 0.290) |
| Section+position R2 | 0.483 (LOO: 0.387) |
| Delta-R2 | 0.128 |
| Delta-LOO | 0.097 |

## Interpretation

Position is a substantial mediator of sister choice. Folios where ch is concentrated later in lines (and sh earlier) have systematically different ch_preference ratios. This is consistent with C929's interpretation that ch=active testing (later, after observation) and sh=passive monitoring (earlier, during process). The LOO-confirmed improvement rules out overfitting — position carries genuine predictive power for sister preference.

## Provenance

- Phase 420 Test 1: POSITIONAL_MEDIATION
- Script: `phases/SISTER_PAIR_MECHANISM/scripts/sister_pair_mechanism.py`
- Results: `phases/SISTER_PAIR_MECHANISM/results/sister_pair_mechanism.json` -> test1_positional_mediation
