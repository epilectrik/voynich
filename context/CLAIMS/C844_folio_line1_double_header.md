# C844: Folio Line 1 Double-Header Effect

**Tier:** 2
**Scope:** B
**Phase:** B_PARAGRAPH_STRUCTURE

## Constraint

B folio line 1's elevated HT rate (50.2% per C747) results from the overlap of folio-level header and first paragraph header functions. Folio line 1 is a double-header.

## Evidence

From paragraph_analysis.json:

| Position | First Token HT% | Paragraph Line 1 HT% |
|----------|-----------------|----------------------|
| Folio line 1 | 79.0% | 44.9% (overlaps with folio header) |
| Mid-folio paragraph start | 73.8% | 43.6% |

**Component analysis:**
- C747 folio line 1: 50.2% HT
- C840 paragraph line 1: 44.9% HT
- C840 paragraph body: 29.1% HT

The extra ~5pp in folio line 1 (50.2% vs 44.9%) represents the folio-level identification component that only appears once per folio.

## Structural Interpretation

```
FOLIO LINE 1 = FOLIO HEADER + PARAGRAPH 1 HEADER
  ↓
Combined HT rate: 50.2%

PARAGRAPH 2+ LINE 1 = PARAGRAPH HEADER ONLY
  ↓
Single-function HT rate: 43.6%
```

## Why This Matters

C747 documented the phenomenon; C844 explains the mechanism:
1. Every paragraph has a header zone (C840)
2. Folios have an additional identification layer
3. Folio line 1 combines both, producing the highest HT density

## Provenance

- Script: `phases/B_PARAGRAPH_STRUCTURE/investigate_paragraphs_v2.py`
- Data: `phases/B_PARAGRAPH_STRUCTURE/results/paragraph_analysis.json`
- Depends: C747 (folio line 1 HT), C840 (paragraph structure)

## Status

CONFIRMED - Mechanistic explanation for C747.
