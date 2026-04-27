# Phase 667: Retraction Retests

**Phase:** 667
**Status:** COMPLETE
**Started:** 2026-04-27
**Motivation:** Audit of Phases 643-666 found 6 constraints with serious methodological issues. This phase retested 4 quick-fixable ones. 2 remain deferred for methodology redesign.

## Results

| C# | Original Claim | Issue Found | Retest Result | Action |
|---|---|---|---|---|
| **C1964** | 85% within-line interleaving | Baseline artifact (all-token rate is 91%) | REVERSED: transitions at 85.3% vs prefixed baseline 85.6%, z=-0.96 NS | **PERMANENTLY RETRACTED** |
| **C1966** | HT rate vs compound diversity rho=+0.602 | Type-token confound (count vs types: rho=+0.960) | Partial rho=+0.189, p=0.045 after controlling for HT count | **RE-REGISTERED** with corrected metrics |
| **C1967** | e_depth gradient qo>ch>sh, no statistical test | No test; compositional confound | Non-prefix gradient: 0.471>0.446>0.357, p=0.024 | **RE-REGISTERED** with stats + control |
| **C1970** | ke/ek ratio: d=+1.04, p=0.0023 | Inconsistent metric (ratio vs count) | ke/(ke+ek) proportion: d=+0.256, p=0.24 | **PERMANENTLY RETRACTED** (metric artifact) |

## Deferred (require methodology redesign)

| C# | Original Phase | Issue | Status |
|---|---|---|---|
| **C1959** | 643 | Monotone-by-construction circularity in phase assignment | RETRACTED, awaiting independent phase-assignment methodology |
| **C1960** | 647 | Failed own pre-reg criteria (1/5 vs required 3/5); paragraph-size confound | RETRACTED, awaiting size-controlled redesign |

## Net constraint impact

- v6.36: 1970 constraints
- v6.37: 1966 constraints (-4 permanent retractions, 2 re-registered with corrections)

## Methodology lessons

1. **Always compute a null baseline** before claiming a rate is "high" or "dominant." 85% means nothing without knowing what random gives you.
2. **Type-token confounds are real.** When X predicts count-of-Y and also predicts total-Y, partial correlation is mandatory.
3. **Statistical tests are not optional.** Point estimates without significance tests are not registrable claims.
4. **Metric units must be consistent.** A metric that is a ratio sometimes and a raw count other times produces artificial outliers.
5. **Pre-registration criteria are binding.** If the result doesn't meet the locked bar, the test failed. Register the failure, not the result.
