# C739: Best-Match Specificity

**Status:** VALIDATED | **Tier:** 2 | **Phase:** A_B_FOLIO_SPECIFICITY | **Scope:** A<>B

## Finding

Every B folio has a strongly preferred A folio. The best-matching A folio provides coverage at least 1.5x the mean, and the best-match z-scores average 3.77 standard deviations above the mean.

### Best-Match Statistics (B folio -> best A folio)

| Metric | Value |
|--------|-------|
| Mean best-match lift | 2.431x |
| Max best-match lift | 3.027x |
| Mean best-match z-score | 3.772 |
| Max best-match z-score | 4.369 |
| B folios with lift > 1.2x | 82/82 (100%) |
| B folios with lift > 1.5x | 82/82 (100%) |

### Reverse: A folio -> best B folio

| Metric | Value |
|--------|-------|
| Mean best-B lift | 1.653x |
| Max best-B lift | 2.200x |

The asymmetry (B->A lift 2.43x vs A->B lift 1.65x) reflects the structural difference: B folios have specific vocabulary needs that are better served by some A folios than others, while A folios are less discriminating about which B folio they serve.

## Implication

The routing is directional. B folios are the "consumers" with specific vocabulary requirements; A folios are the "providers" with varying scope. Every B program has a natural A folio partner that makes roughly 2.4x more vocabulary available than a random A folio would. This is consistent with a reference architecture where B programs consult domain-specific A folios for operational vocabulary.

The reverse asymmetry (A folios less specific about B folios) means A folios define broad domain scopes, while B programs have specific domain needs. Many A folios can partially serve a given B program, but only specific A folios serve it well.

## Provenance

- Script: `phases/A_B_FOLIO_SPECIFICITY/scripts/ab_specificity.py` (T5)
- Depends: C734 (coverage architecture), C735 (pool size dominance)
