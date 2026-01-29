# C735: Pool Size Coverage Dominance

**Status:** VALIDATED | **Tier:** 2 | **Phase:** A_B_FOLIO_SPECIFICITY | **Scope:** A<>B

## Finding

A folio PP pool size is the primary predictor of B vocabulary coverage. Larger PP pools produce proportionally more legal B tokens.

### Correlation

| Metric | Value |
|--------|-------|
| Pool size vs mean B coverage (Spearman) | rho = 0.8504, p = 5.16e-33 |
| Pool size vs mean B coverage (Pearson) | r = 0.8875, p = 1.71e-39 |
| Pool size vs coverage variance (Spearman) | rho = 0.3654, p = 6.41e-05 |

### Pool Size Range

| Metric | Value |
|--------|-------|
| Median PP MIDDLE pool | 34 |
| Mean | 35.3 |
| Min | 20 |
| Max | 88 |
| Total unique PP MIDDLEs | 389 |

The relationship is nearly linear: each additional MIDDLE in the A folio's PP pool opens roughly the same marginal amount of B vocabulary. The rho=0.85 means pool size alone explains ~72% of the variance in mean coverage (matching the ANOVA result in C734).

## Implication

The A-B routing architecture is primarily quantitative, not qualitative. An A folio's "reach" into B vocabulary is mostly determined by how many MIDDLEs it catalogs, not which specific ones. However, the remaining ~15% unexplained variance (and the 1.544x specificity ratio from C734) indicates that WHICH MIDDLEs matter too — the relationship is not purely a size effect.

## Provenance

- Script: `phases/A_B_FOLIO_SPECIFICITY/scripts/ab_specificity.py` (T8)
- Depends: C703 (folio-level PP pooling)
- Extends: C734 (explains the dominant variance component)
