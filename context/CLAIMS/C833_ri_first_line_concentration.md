# C833: RI First-Line Concentration

**Tier:** 2
**Scope:** A
**Phase:** A_RECORD_B_ROUTING_TOPOLOGY

## Constraint

RI tokens concentrate 1.85x in the first line of paragraphs compared to subsequent lines. This pattern exists at paragraph level but NOT at folio level (1.03x ratio for first paragraph vs others).

> **Refinement (2026-02-01):** Systematic annotation of 114 Currier A folios reveals RI tokens appear outside L1 in **57 folios (50%)**. This establishes that L1 concentration is a **preference, not a requirement**. RI has "header affinity" but can appear anywhere. Non-L1 RI tokens should be flagged during annotation (C833 FLAG) but are structurally valid.

> **Scope Clarification (2026-01-30):** This constraint correctly identifies paragraph as the
> A-internal record unit where RI structure manifests. For A-B vocabulary correspondence,
> C885 establishes that folio is the operational unit (81% coverage vs paragraph's 58%).

## Evidence

From t15_granularity_validation.py:

```
RI FIRST-UNIT CONCENTRATION:
Level                    First Sub-unit   Other           Ratio
--------------------     --------------- --------------- ----------
PARAGRAPH (lines)              13.0%           6.4%       1.85x
FOLIO (paragraphs)             10.0%           9.7%       1.03x
```

From t13_ri_position.py:

```
RI density:
  First line: 259 RI / 2597 tokens = 10.0%
  Other lines: 267 RI / 4569 tokens = 5.8%
  Ratio: 1.71x
```

## Interpretation

The paragraph (gallows-initial chunk) is the correct operational unit for A records because:

1. RI shows internal structure at paragraph level (1.85x first-line concentration)
2. RI shows NO structure at folio level (1.03x ratio)
3. The first line contains both INITIAL and FINAL RI - it's a "header" that brackets the record's scope

This validates the gallows-initial paragraph as the operational record size.

## Provenance

- t15_granularity_validation.json: para_first_line_ratio=1.85, folio_first_para_ratio=1.03
- t13_ri_position.json: ri_rate_first_line, ri_rate_other_lines
- Related: C827 (paragraph operational unit), C834 (granularity validation)

## Status

CONFIRMED - First-line concentration is structural feature of paragraphs.
