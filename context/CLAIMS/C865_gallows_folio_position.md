# C865: Gallows Folio Position Distribution

**Status:** Validated
**Tier:** 2
**Phase:** FOLIO_PARAGRAPH_ARCHITECTURE
**Scope:** B

## Statement

Gallows types have distinct positional distributions within folios. k and f are front-biased (openers), while p and t are distributed throughout (continuers).

## Evidence

```
Gallows  Mean Pos  Front(<0.3)  Back(>0.7)
p          0.52        30%         36%
t          0.49        32%         31%
k          0.35        52%         24%
f          0.30        56%          6%
```

k and f appear predominantly in the first third of folios.
p and t are evenly distributed across folio positions.

## Folio Profiles

```
p-mono:     30 folios (p throughout)
p-dominant: 23 folios
t-dominant:  8 folios
k-dominant:  6 folios
mixed:       6 folios
```

Most folios are p-dominated. k and f rarely dominate entire folios.

## Interpretation

| Gallows | Position Role |
|---------|---------------|
| f | Folio opener (position 0.30) |
| k | Early-phase marker (position 0.35) |
| p | Throughout (continuation) |
| t | Throughout (continuation) |

## Provenance

- Script: `13_gallows_meaning_probe.py`
- Data: `gallows_initial_probe.json`

## Related

- C864 (gallows paragraph marker)
- C671 (MIDDLE novelty front-loaded)
