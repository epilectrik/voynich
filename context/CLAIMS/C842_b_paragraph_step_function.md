# C842: B Paragraph HT Step Function

**Tier:** 2
**Scope:** B
**Phase:** B_PARAGRAPH_STRUCTURE

## Constraint

Within B paragraphs, HT fraction drops sharply from line 1 (45.2%) to line 2 (26.5%) and remains flat thereafter. The header zone is exactly one line, not a gradient.

## Evidence

From paragraph_analysis.json (196 paragraphs with 5+ lines):

| Line Position | HT% |
|---------------|-----|
| 1 | 45.2% |
| 2 | 26.5% |
| 3 | 26.2% |
| 4 | 27.1% |
| 5+ | 25.6% |

**Step magnitude:** -18.7pp from position 1 to position 2
**Body variance:** Positions 2-5+ range only 25.6-27.1% (1.5pp spread)

## Parallel to C748

This mirrors the folio-level step function (C748):
- Folio line 1: 50.2% HT
- Folio lines 2+: ~30% HT

Both folio and paragraph levels show the same one-line header pattern.

## Interpretation

The header zone is structurally constrained to exactly one line. This is not gradual context decay but a discrete boundary:
- **Line 1:** Identification/setup (HT vocabulary)
- **Lines 2+:** Execution (operational grammar)

The sharp boundary suggests functional separation, not just statistical tendency.

## Provenance

- Script: `phases/B_PARAGRAPH_STRUCTURE/investigate_paragraphs_v2.py`
- Data: `phases/B_PARAGRAPH_STRUCTURE/results/paragraph_analysis.json`
- Depends: C748 (folio-level step function)

## Status

CONFIRMED - Step pattern unambiguous in data.
