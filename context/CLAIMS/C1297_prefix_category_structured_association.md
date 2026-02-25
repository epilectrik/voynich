# C1297: PREFIX-Category Structured Association

**Tier:** 2
**Scope:** B
**Phase:** PREFIX_CATEGORY_ANATOMY (458)
**Date:** 2026-02-24

## Finding

Individual PREFIXes predict 8-category operational labels with structured selectivity. The 32 x 8 contingency table (PREFIXes with N >= 30) yields chi2 = 15,598 (dof = 217, p ~ 0), Cramer's V = 0.311. This is not a monolithic effect: different PREFIXes concentrate on different categories.

## Key Category Profiles (dominant category, purity)

| PREFIX | N | Dominant | Purity | Secondary |
|--------|---|----------|--------|-----------|
| qo | 4069 | THERMAL | 59.0% | FLOW 20.1% |
| ct | 60 | MONITORING | 90.0% | -- |
| da | 1083 | STAGING | 56.3% | FLOW 22.2% |
| sa | 329 | STAGING | 52.3% | FLOW 22.2% |
| do | 126 | STAGING | 57.1% | FLOW 23.0% |
| ta | 237 | STAGING | 46.0% | FLOW 31.7% |
| ka | 238 | STAGING | 42.9% | FLOW 26.5% |
| ol | 875 | THERMAL | 42.2% | TRANSITION 17.9% |
| ok | 1476 | FLOW | 27.6% | TRANSITION 26.5% |
| ot | 1448 | FLOW | 27.9% | TRANSITION 25.2% |
| ch | 3492 | OPERATION | 25.9% | THERMAL 20.9% |
| sh | 2329 | OPERATION | 30.8% | THERMAL 24.0% |
| lch | 315 | OPERATION | 40.0% | TRANSITION 20.6% |
| te | 289 | CONTAINMENT | 26.3% | TRANSITION 23.5% |
| BARE | 3854 | FLOW | 29.4% | STAGING 20.7% |

## Structural Patterns

1. **a-base PREFIXes** (da, ka, sa, ta) uniformly select STAGING (43-56%)
2. **o-base PREFIXes** split: qo = THERMAL (59%), others = STAGING/FLOW
3. **h-base PREFIXes** (ch, sh, lch, etc.) select OPERATION (26-40%)
4. **k-base PREFIXes** (ok, lk, yk) select THERMAL/FLOW/TRANSITION mix
5. **BARE** tokens are FLOW-enriched (29.4%) and THERMAL-depleted (4.1%)

## Method

- H-track Currier B tokens, no labels, no asterisks, category-assigned only (N = 23,086)
- Category assignment via auto_assign_category() (atom plurality vote from middle_dictionary.json glosses)
- PREFIXes with N >= 30 qualify (32 of 36)
- Chi-squared test on 32 x 8 contingency table

## Extends

- C1278 (category adds 18.6% beyond PREFIX for class prediction) -- now resolved to individual PREFIX level
- C911 (PREFIX-MIDDLE selectivity) -- category provides higher-level grouping of MIDDLE selectivity
- C1219 (base determines MIDDLE content) -- categories capture base-group effects at coarser grain

## Falsifiability

Would be falsified if PREFIX-category association were driven entirely by sample size (V < 0.10) or by a single dominant PREFIX.

## Evidence

- `phases/PREFIX_CATEGORY_ANATOMY/results/prefix_category_anatomy.json` (T1_full_contingency)
