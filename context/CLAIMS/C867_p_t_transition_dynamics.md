# C867: P-T Transition Dynamics

**Status:** Validated
**Tier:** 2
**Phase:** FOLIO_PARAGRAPH_ARCHITECTURE
**Scope:** B

## Statement

p and t have distinct transition dynamics. p is self-continuing (54% p->p), while t is transitional and returns to p (50% t->p). This establishes p as the stable mode and t as a perturbation.

## Evidence

### Transition Matrix

```
From p:
  p -> p: 120 (54%)
  p -> t:  44 (20%)
  p -> k:  15 (7%)
  p -> f:   3 (1%)
  p -> end: 42 (19%)

From t:
  t -> p:  49 (50%)
  t -> t:  30 (31%)
  t -> k:   2 (2%)
  t -> f:   3 (3%)
  t -> end: 14 (14%)
```

### Self-Transition Rates

```
p -> p: 62.6% (including all contexts)
t -> t: 36.7%
k -> k: 18.4%
f -> f: 33.3%
```

p has the highest self-transition rate.

### Key Differences

| Metric | p | t |
|--------|---|---|
| Self-continuation | 54% | 31% |
| Returns to other | 20% -> t | 50% -> p |
| Vocabulary | 3,200 words | 1,678 words |
| Mean size | 49 tokens | 43 tokens |

## Interpretation

- **p = Primary mode**: Self-continuing, large vocabulary, stable
- **t = Transitional mode**: Returns to p, restricted vocabulary, temporary

t paragraphs function as excursions that return to the main p-mode processing.

## Provenance

- Script: `15_p_vs_t_comparison.py`
- Data: `gallows_initial_probe.json`

## Related

- C864 (gallows paragraph marker)
- C865 (gallows folio position)
