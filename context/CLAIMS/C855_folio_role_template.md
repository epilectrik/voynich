# C855: Folio Role Template

**Status:** Validated
**Tier:** 2
**Phase:** FOLIO_PARAGRAPH_ARCHITECTURE
**Scope:** B

## Statement

Paragraphs on the same folio share a consistent **role profile** (EN/FL/FQ/CC proportions) but NOT a shared vocabulary. Role similarity (0.831 normalized) far exceeds vocabulary Jaccard (0.061).

## Evidence

```
Cohesion scores (normalized 0-1):
  Role similarity:  0.831
  Prefix overlap:   0.300
  Vocabulary:       0.061
  HT overlap:       0.024

Ranking: Role > Prefix > Vocabulary > HT
```

## Interpretation

The folio defines **proportions** of instruction classes, not specific instructions. Each paragraph independently selects tokens that satisfy these proportions. This is constraint satisfaction, not instruction copying.

## Mechanism

Folio = role profile template → paragraphs sample from vocabulary to match profile

## Related

- C552 (section role profiles)
- C862 (template verdict)
- C857 (Par 1 ordinariness)
