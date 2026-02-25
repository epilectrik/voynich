# C1303: ch/sh Category Divergence Is Position-Independent

**Tier:** 2
**Scope:** B
**Phase:** SISTER_CATEGORY_MECHANISM (459)
**Date:** 2026-02-24

## Finding

ch/sh category divergence (C1299, V=0.099) survives position control with 98.3% V retention. The divergence is CATEGORY_GENUINE, not a positional artifact.

## Method

- Tokens split into three position zones: EARLY (<0.333), MID (0.333-0.667), LATE (>0.667), normalized by line length
- Short lines (<=3 tokens) assigned to MID zone
- Within-zone 2 x 8 contingency tables (ch vs sh x 8 categories) computed per zone
- Fisher-combined across zones: chi2 = 27.50, dof = 6, p = 1.17e-4
- V retention = mean(within-zone V) / raw V = 0.0977 / 0.0994 = 98.3%

## Zone Detail

| Zone | N_ch | N_sh | V | p |
|------|------|------|---|---|
| EARLY | 1,030 | 1,060 | 0.094 | 0.011 |
| MID | 1,330 | 785 | 0.097 | 0.005 |
| LATE | 1,132 | 484 | 0.102 | 0.018 |

## Interpretation

C929 established that ch appears later in lines and sh earlier. The V retention of 98.3% means that removing position's effect leaves nearly all of the category divergence intact. ch and sh select different operational categories regardless of where they sit in the line. The positional axis (WHEN to act, C929) and the categorical axis (WHAT to act on) are independent dimensions.

## Extends

- C1299 (ch/sh B category divergence V=0.121) -- position control confirms genuineness
- C929 (ch later, sh earlier) -- positional axis is orthogonal to category axis

## Falsifiability

Would be falsified if V retention < 50% (position explains most of the category divergence).

## Evidence

- `phases/SISTER_CATEGORY_MECHANISM/results/sister_category_mechanism.json` (T2_position_controlled_ch_sh)
