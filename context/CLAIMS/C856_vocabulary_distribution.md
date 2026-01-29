# C856: Folio Vocabulary Distribution

**Status:** Validated
**Tier:** 2
**Phase:** FOLIO_PARAGRAPH_ARCHITECTURE
**Scope:** B

## Statement

Folio-unique vocabulary is **distributed** across paragraphs (Gini coefficient 0.279), not concentrated. Paragraph 1 contains only **27.4%** of folio-unique vocabulary.

## Evidence

```
Par 1 unique vocab share: 27.4% mean, 21.2% median
Gini coefficient: 0.279 (0 = equal, 1 = concentrated)

Cumulative by ordinal:
  Par 1: 27.4%
  Par 2: 50.2%
  Par 3: ~50%
  ...
  Par 8: 67.3%
```

## Interpretation

No single paragraph dominates folio identity. Folio-unique vocabulary emerges from the union of independently-selected paragraph vocabularies, not from a template paragraph.

## Verdict

DISTRIBUTED model confirmed. Gini < 0.3 indicates spread, not concentration.

## Related

- C531 (folio unique vocabulary)
- C855 (role template)
- C857 (Par 1 ordinariness)
