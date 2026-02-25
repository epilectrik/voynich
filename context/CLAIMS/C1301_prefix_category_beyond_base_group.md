# C1301: PREFIX Category Information Beyond Base Group

**Tier:** 2
**Scope:** B
**Phase:** PREFIX_CATEGORY_ANATOMY (458)
**Date:** 2026-02-24

## Finding

PREFIX identity carries genuine category information beyond what base-group membership explains. Conditional mutual information I(CATEGORY; PREFIX | BASE) = 0.058 bits (2.1% of total category entropy H = 2.742 bits). Fisher-combined within-base p ~ 0.

## Tautology Decomposition

| Level | V | MI (bits) | MI % |
|-------|---|-----------|------|
| BASE x CATEGORY | 0.258 | 0.333 | 12.2% |
| PREFIX x CATEGORY | 0.311 | 0.391 | 14.3% |
| PREFIX beyond BASE | -- | 0.058 | 2.1% |

## Within-Base Differentiation

| Base | PREFIXes | N | Within-base V | p |
|------|----------|---|---------------|---|
| t-base | ct, ot | 1,508 | 0.891 | ~10^-254 |
| o-base | do, ko, po, qo, so, to | 4,683 | 0.217 | ~10^-209 |
| l-base | al, ol | 1,048 | 0.140 | 0.005 |
| e-base | ke, te | 548 | 0.161 | 0.047 |
| k-base | lk, ok, yk | 2,228 | 0.103 | 1.8e-5 |
| a-base | da, ka, sa, ta | 1,887 | 0.098 | 7.6e-5 |
| h-base | ch, dch, fch, kch, lch, lsh, pch, rch, sh, tch | 6,968 | 0.081 | ~10^-35 |
| r-base | ar, or | 309 | 0.152 | 0.416 (NS) |

## Key Result: t-base

The t-base pair (ct vs ot) has V = 0.891, the highest within-base divergence. ct is 90% MONITORING while ot is 27.9% FLOW. This is not a base-group artifact: the same base (t) hosts two PREFIXes with nearly opposite category profiles. ct belongs to a different operational channel than ot.

## Interpretation

Base group explains most (12.2%) of the PREFIX-category association, but 2.1% is PREFIX-specific. This is small but highly significant (p ~ 0) and concentrated in specific pairs (t-base, o-base). The system is not tautological: knowing the exact PREFIX gives genuine categorical information that knowing only the base group does not.

## Method

- H(CATEGORY) = 2.742 bits, H(CATEGORY|BASE) = 2.409 bits, H(CATEGORY|PREFIX) = 2.351 bits
- Conditional MI = H(CATEGORY|BASE) - H(CATEGORY|PREFIX) = 0.058 bits
- Within-base chi-squared for each base group with 2+ PREFIXes, Fisher-combined
- N = 23,086 tokens across 32 qualifying PREFIXes in 9 base groups

## Extends

- C1219 (base determines MIDDLE content, within-base cosine 0.950) -- categories add finer resolution
- C1278 (category adds 18.6% beyond PREFIX for class) -- reciprocal: PREFIX adds category info beyond base

## Falsifiability

Would be falsified if within-base tests all had p > 0.05 (pure base-group artifact) or if CMI < 0.01 bits.

## Evidence

- `phases/PREFIX_CATEGORY_ANATOMY/results/prefix_category_anatomy.json` (T6_tautology_decomposition)
