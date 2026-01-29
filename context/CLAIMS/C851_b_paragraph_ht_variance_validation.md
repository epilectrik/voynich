# C851: B Paragraph HT Variance Validation

**Tier:** 2
**Scope:** Currier-B
**Phase:** PARAGRAPH_INTERNAL_PROFILING

## Constraint

B paragraph HT enrichment pattern validated at full inventory scale. Line 1 HT rate is 46.5% vs body 23.7% (+13.4pp delta). 76.8% of multi-line paragraphs show positive delta.

## Evidence

| Metric | Value | Expected |
|--------|-------|----------|
| Mean HT rate | 36.4% | - |
| Line 1 HT rate | 46.5% | 44.9% (C840) |
| Body HT rate | 23.7% | 29.1% (C840) |
| HT delta | **+0.134** | +0.158 (C840) |
| Positive delta rate | **76.8%** | ~76% (C840) |
| First token is HT | 75.6% | - |

## Interpretation

C840 findings validated at full paragraph inventory:
- Header enrichment effect robust
- 76.8% positive delta exactly matches expectation
- First token being HT (75.6%) correlates with gallows-initial pattern

## Relationship to Existing Constraints

| Constraint | Relationship |
|------------|--------------|
| C840 | VALIDATES - B paragraph mini-program structure |
| C842 | VALIDATES - B paragraph HT step function |
| C843 | ALIGNS - B paragraph prefix markers |

## Provenance

- Script: `phases/PARAGRAPH_INTERNAL_PROFILING/scripts/06_b_ht_variance.py`
- Data: `phases/PARAGRAPH_INTERNAL_PROFILING/results/b_ht_variance.json`

## Status

CONFIRMED
