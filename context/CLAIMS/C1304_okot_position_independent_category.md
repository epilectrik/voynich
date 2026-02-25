# C1304: ok/ot Category Divergence Is Position-Independent

**Tier:** 2
**Scope:** B
**Phase:** SISTER_CATEGORY_MECHANISM (459)
**Date:** 2026-02-24

## Finding

ok/ot category divergence (C1298, V=0.114) survives position control with 124.1% V retention. The divergence is CATEGORY_GENUINE -- position was actually masking the true divergence.

## Method

- Tokens split into three position zones: EARLY (<0.333), MID (0.333-0.667), LATE (>0.667), normalized by line length
- Within-zone 2 x 8 contingency tables (ok vs ot x 8 categories) computed per zone
- Fisher-combined across zones: chi2 = 29.63, dof = 6, p = 4.62e-5
- V retention = mean(within-zone V) / raw V = 0.1415 / 0.1140 = 124.1%

## Zone Detail

| Zone | N_ok | N_ot | V | p |
|------|------|------|---|---|
| EARLY | 390 | 302 | 0.207 | 1.1e-4 |
| MID | 578 | 526 | 0.125 | 0.016 |
| LATE | 508 | 620 | 0.093 | 0.204 |

## Key Pattern

V retention >100% means position was a confounder suppressing divergence. When ok and ot tokens in the same position zone are compared, they diverge MORE than the raw comparison suggests. The strongest divergence is in EARLY positions (V=0.207), where ok is STAGING-enriched (33.6% vs 20.2%) and ot is MARKING-enriched (23.2% vs 13.3%).

## Interpretation

ok and ot encode different operational emphases that are independent of line position. ok selects THERMAL/STAGING vocabulary (set parameters), ot selects MARKING/OPERATION vocabulary (transfer/routing). The base atom (k=heat vs t=transfer) drives category selection, not positional placement.

## Extends

- C1298 (ok/ot category divergence V=0.105) -- position control reveals suppressed divergence
- C1184 (ok/ot independent axes, opposite positional polarity) -- positional polarity was hiding category signal

## Falsifiability

Would be falsified if V retention < 50% (position explains most of the category divergence).

## Evidence

- `phases/SISTER_CATEGORY_MECHANISM/results/sister_category_mechanism.json` (T5_position_controlled_ok_ot)
