# C864: Gallows Paragraph Marker

**Status:** Validated
**Tier:** 2
**Phase:** FOLIO_PARAGRAPH_ARCHITECTURE
**Scope:** B

## Statement

81.5% of B paragraphs begin with a gallows-initial token. Distribution: p (55%), t (29%), k (12%), f (4%). Gallows tokens at paragraph start function as procedure-type markers.

## Evidence

```
Total paragraphs with first token: 585
Gallows-initial: 477 (81.5%)

Distribution:
  p: 264 (55.3%)
  t: 137 (28.7%)
  k:  57 (11.9%)
  f:  19 (4.0%)
```

## Morphological Structure

Gallows-initial tokens follow: GALLOWS_PREFIX + MIDDLE + SUFFIX

Where GALLOWS_PREFIX is a special PREFIX class (p+ch, p+o, t+sh, k+e, etc.) not fully captured in the standard 8-family PREFIX system.

Note: k-initial tokens are compound (keedy, kaiin) not standalone k, consistent with C540.

## Provenance

- Script: `10_gallows_initial_probe.py`
- Data: `gallows_initial_probe.json`

## Related

- C841 (B paragraph gallows-initial pattern)
- C540 (kernel primitives are bound morphemes)
- C267 (token morphological structure)
