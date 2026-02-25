# C1300: qo Near-Pure THERMAL Channel

**Tier:** 2
**Scope:** B
**Phase:** PREFIX_CATEGORY_ANATOMY (458)
**Date:** 2026-02-24

## Finding

PREFIX qo is 59.0% THERMAL (2.50x corpus baseline of 23.6%), ranking #1 among all 32 qualifying PREFIXes. Binomial test p ~ 0. The next-most THERMAL PREFIX is ol at 42.2%. qo is the only PREFIX where a single category exceeds 50%.

## qo Full Profile

| Category | Rate | vs Baseline |
|----------|------|-------------|
| THERMAL | 59.0% | 2.50x |
| FLOW | 20.1% | 1.15x |
| MARKING | 7.3% | 0.93x |
| STAGING | 6.7% | 0.56x |
| OPERATION | 3.2% | 0.20x |
| CONTAINMENT | 1.5% | 0.30x |
| TRANSITION | 1.5% | 0.11x |
| MONITORING | 0.8% | 0.49x |

## Interpretation

qo functions as a near-pure THERMAL channel with a secondary FLOW component (20.1%). OPERATION (3.2%) and TRANSITION (1.5%) are strongly suppressed. This confirms and sharpens C1277 (44.1% qo-THERMAL at 4-group resolution): individual PREFIX resolution shows even stronger concentration at 8-category resolution.

The qo-THERMAL dominance means approximately 3 in 5 qo-prefixed tokens perform thermal operations (heating/cooling/thermal state management). Combined with qo's alternation behavior (C1277), this establishes qo as the primary thermal injection channel in B text.

## Method

- N = 4,069 qo-prefixed tokens
- Binomial test: qo THERMAL rate (59.0%) vs corpus THERMAL rate (23.6%)
- Ranked among all 32 PREFIXes with N >= 30

## Extends

- C1277 (THERMAL escape is qo-mediated, 44.1%) -- sharpened to 59.0% at 8-category resolution
- C1297 (PREFIX-category structured association) -- qo is the purest categorical channel among common PREFIXes

## Falsifiability

Would be falsified if qo's THERMAL concentration were driven by a single MIDDLE (e.g., if removing one MIDDLE dropped rate below 40%).

## Evidence

- `phases/PREFIX_CATEGORY_ANATOMY/results/prefix_category_anatomy.json` (T4_qo_purity)
