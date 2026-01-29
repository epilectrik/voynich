# C858: Paragraph Count Complexity Proxy

**Status:** Validated
**Tier:** 2
**Phase:** FOLIO_PARAGRAPH_ARCHITECTURE
**Scope:** B

## Statement

Paragraph count **reflects folio complexity**. Strong correlations: vocabulary size (rho=0.836), total tokens (rho=0.802), role diversity (rho=0.826).

## Evidence

```
Spearman correlations:
  Par count vs vocabulary size: rho = 0.836
  Par count vs total tokens:    rho = 0.802
  Par count vs role diversity:  rho = 0.826

All exceed 0.8 threshold for strong correlation.
```

## Section Variation

```
Section F-ratio: 10.85 (p < 0.001)

Mean pars/folio by section:
  HERBAL_B:  2.2
  BIO:       7.5
  RECIPE_B: 10.2
  PHARMA:   14.0
```

## Interpretation

More paragraphs = more complex program. Sections differ in complexity requirements: HERBAL_B uses few comprehensive paragraphs, RECIPE_B/PHARMA use many specialized ones.

## Related

- C552 (section role profiles)
- C860 (section organization)
