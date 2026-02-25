# C1302: BARE Distinctive Category Profile

**Tier:** 2
**Scope:** B
**Phase:** PREFIX_CATEGORY_ANATOMY (458)
**Date:** 2026-02-24

## Finding

BARE tokens (no PREFIX) have a distinctive 8-category operational profile that diverges strongly from prefixed tokens (chi2 = 1,368, dof = 7, p ~ 10^-291, Cramer's V = 0.243).

## Profile Comparison

| Category | BARE | Prefixed | BARE Enrichment |
|----------|------|----------|-----------------|
| FLOW | 29.4% | 17.5% | 1.68x |
| STAGING | 20.7% | 11.3% | 1.83x |
| TRANSITION | 19.3% | 14.0% | 1.37x |
| MARKING | 10.5% | 7.2% | 1.46x |
| OPERATION | 11.1% | 15.9% | 0.69x |
| THERMAL | 4.1% | 27.5% | 0.15x |
| CONTAINMENT | 3.7% | 5.0% | 0.75x |
| MONITORING | 1.3% | 1.7% | 0.79x |

## Key Pattern

BARE is **THERMAL-depleted** (4.1% vs 27.5%, 6.7x depletion) and **FLOW/STAGING-enriched** (29.4%/20.7%). This is the inverse of qo (C1300), which is THERMAL-enriched and FLOW-secondary. BARE bypasses the base-MIDDLE-category chain entirely, serving as a natural circularity control: the absence of a PREFIX shifts category distribution toward non-thermal operations.

## Interpretation

BARE tokens operate primarily in FLOW (routing/transfer) and STAGING (preparation/setup) modes. They are nearly excluded from THERMAL operations. This is consistent with BARE tokens being infrastructure/routing tokens that do not carry thermal parameters. The PREFIX slot appears to be the primary mechanism for injecting thermal content into B grammar.

## Method

- N = 23,086 total (BARE = 3,854; prefixed = 19,232)
- 2 x 8 contingency table, chi-squared test
- Bonferroni p < 0.00625 threshold

## Extends

- C1297 (PREFIX-category structured association) -- BARE as category anchor point
- C1300 (qo near-pure THERMAL) -- BARE is anti-qo (THERMAL-depleted vs THERMAL-enriched)

## Falsifiability

Would be falsified if BARE's THERMAL depletion were driven by BARE tokens clustering in non-thermal sections.

## Evidence

- `phases/PREFIX_CATEGORY_ANATOMY/results/prefix_category_anatomy.json` (T7_bare_profile)
