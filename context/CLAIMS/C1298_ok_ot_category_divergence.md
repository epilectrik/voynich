# C1298: ok-ot Category Divergence

**Tier:** 2
**Scope:** B
**Phase:** PREFIX_CATEGORY_ANATOMY (458)
**Date:** 2026-02-24

## Finding

Sister PREFIXes ok and ot (C408) diverge in 8-category operational profiles despite sharing FLOW as dominant category. Chi2 = 32.0 (dof = 7, p = 4.0e-5), Cramer's V = 0.105, JSD = 0.008.

## Category Enrichment

| Category | ok | ot | ok/ot Ratio |
|----------|----|----|-------------|
| THERMAL | 24.7% | 20.2% | 1.22 |
| MONITORING | 1.2% | 0.5% | 2.52 |
| MARKING | 3.1% | 2.1% | 1.42 |
| FLOW | 27.6% | 27.9% | 0.99 |
| TRANSITION | 26.5% | 25.2% | 1.05 |
| OPERATION | 12.5% | 17.3% | 0.72 |
| STAGING | 2.8% | 4.3% | 0.65 |
| CONTAINMENT | 1.7% | 2.4% | 0.70 |

## Interpretation

ok is THERMAL-enriched (24.7% vs 20.2%) and MONITORING-enriched (2.52x). ot is OPERATION-enriched (17.3% vs 12.5%) and STAGING-enriched (4.3% vs 2.8%). Despite overlapping on FLOW and TRANSITION, the sister pair selects different operational emphasis: ok skews toward monitoring/measurement, ot toward execution/staging.

ok belongs to k-base (C1219), ot belongs to t-base. The divergence is partially explained by base-group differences (T6 within-base analysis), but the magnitude (V = 0.105) confirms functional differentiation beyond mere labeling convention.

## Method

- N = 2,924 tokens (ok = 1,476; ot = 1,448)
- 2 x 8 contingency table, chi-squared test
- Bonferroni p < 0.00625 threshold

## Extends

- C408 (sister pairs: ok/ot share selectivity patterns) -- now shown to diverge at category grain
- C1184 (independent axes: ok/ot have opposite positional polarity) -- category divergence adds functional dimension
- C911 (ok selects e-family + infrastructure; ot selects h-family) -- categories organize the MIDDLE selectivity

## Falsifiability

Would be falsified if ok-ot divergence vanished after controlling for section (Herbal-B vs Pharma).

## Evidence

- `phases/PREFIX_CATEGORY_ANATOMY/results/prefix_category_anatomy.json` (T2_ok_ot_divergence)
