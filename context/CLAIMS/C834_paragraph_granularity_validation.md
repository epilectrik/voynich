# C834: Paragraph Granularity Validation

**Tier:** 2
**Scope:** A
**Phase:** A_RECORD_B_ROUTING_TOPOLOGY

## Constraint

The INITIAL vs FINAL RI distinction and first-line RI concentration are visible ONLY at paragraph level, validating the paragraph (gallows-initial chunk) as the correct operational record size.

## Evidence

From t15_granularity_validation.py:

```
INITIAL vs FINAL RI SEPARATION:
Granularity   Init Types   Final Types    Overlap    Jaccard
------------ ------------ ------------ ---------- ----------
LINE                   76          110         29      0.185
PARAGRAPH             155          218          9      0.025
FOLIO                 195          220          4      0.010

RI FIRST-UNIT CONCENTRATION:
PARAGRAPH (first line vs others): 1.85x  <- SHOWS STRUCTURE
FOLIO (first para vs others):     1.03x  <- NO STRUCTURE
```

Key observations:

1. **Jaccard decreases with aggregation** - Line (0.185) > Paragraph (0.025) > Folio (0.010)
   - At paragraph level, INITIAL and FINAL RI are already nearly disjoint
   - Further aggregation to folio doesn't improve separation much

2. **First-unit concentration is paragraph-specific**
   - 1.85x at paragraph level (first LINE vs others)
   - 1.03x at folio level (first PARAGRAPH vs others)
   - Pattern exists within paragraphs, not within folios

## Interpretation

The paragraph is the "Goldilocks" unit:

- **Line level**: Too small - INITIAL/FINAL distinction blurred (Jaccard 0.185)
- **Paragraph level**: Just right - Clear structure visible
- **Folio level**: Too large - Structure washes out, no internal differentiation

This confirms that the gallows-initial paragraph is the operational record size where A-record structural patterns manifest.

## Provenance

- t15_granularity_validation.json: line_jaccard=0.185, para_jaccard=0.025, folio_jaccard=0.010
- Related: C827 (paragraph operational unit), C833 (first-line concentration)

## Status

CONFIRMED - Paragraph is validated as correct record granularity through multi-level analysis.
