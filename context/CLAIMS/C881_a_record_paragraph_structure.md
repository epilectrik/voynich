# C881 - A Record Paragraph Structure

**Tier:** 2 | **Scope:** A | **Phase:** MATERIAL_MAPPING_V2, CURRIER_A_STRUCTURE_V2

## Statement

Currier A records are paragraphs (gallows-initial text blocks), not individual lines. Paragraphs divide into two opening types based on first-line RI presence:

> **Scope Clarification (2026-01-30):** Paragraph is the A-internal record unit (describing
> material identification and process structure). For A-B vocabulary correspondence, C885
> establishes A FOLIO (114 units, 81% coverage) as the operational unit, not individual
> paragraphs (342 units, 58% coverage).

| Type | Count | % | First Line Content |
|------|-------|---|-------------------|
| WITH-RI | 215 | 62.9% | RI + PP tokens (material identification) |
| WITHOUT-RI | 127 | 37.1% | Pure PP (92.7% have no RI) |

## Structure

**WITH-RI paragraphs (standard record):**

| Position | Function | Token Class | Rate |
|----------|----------|-------------|------|
| First line | Material identifier | Initial RI | 3.84x baseline |
| Middle lines | Processing instructions | PP tokens | Standard |
| Last line | Output specification | Final RI | Variable |

**WITHOUT-RI paragraphs (process annotation):**

| Position | Function | Token Class |
|----------|----------|-------------|
| First line | Process instructions | Pure PP (92.7%) |
| All lines | Process instructions | PP-dominated, low RI |

## Two Opening Types

RI vocabulary comparison between types:
- Jaccard similarity: **0.028** (almost completely distinct)
- Linker density in WITHOUT-RI: **1.35x** higher
- LINK prefixes (ol/or) in WITHOUT-RI: **2.7x** enriched
- WITHOUT-RI enriched in LAST folio position: **1.62x**

WITHOUT-RI paragraphs show backward reference to preceding paragraphs:
- Backward/forward asymmetry: 1.23x
- Highest overlap when following WITH-RI: Jaccard 0.228
- See C882 for details

## Evidence

1. **C827:** "Paragraphs are the operational aggregation level (not lines, not folios)"
2. **C833:** "RI line-1 rate: 3.84x baseline" - RI concentrates in paragraph first lines
3. **C834:** "RI structure visible ONLY at paragraph level; validates record size"
4. **CURRIER_A_STRUCTURE_V2:** 24 tests characterizing paragraph structure

## Invalidation of Line-Level Approach

Previous analysis treating lines as records was methodologically flawed:
- eoschso (claimed as "chicken") appears at position 41/70 in paragraph A_268
- This is in middle lines, NOT the first line
- Therefore eoschso is NOT initial RI and cannot be a material identifier

## Metrics

| Metric | Value |
|--------|-------|
| Total A paragraphs | 342 |
| WITH-RI paragraphs | 215 (62.9%) |
| WITHOUT-RI paragraphs | 127 (37.1%) |
| WITHOUT-RI pure PP first line | 92.7% |

## Interpretation (Tier 3)

The two types may serve different functions:
- WITH-RI: Material-focused records (identify material, then process)
- WITHOUT-RI: Process-focused annotations (process only, implicit material reference via backward reference)

## Provenance

- `phases/MATERIAL_MAPPING_V2/scripts/09_pp_triangulation_v3.py`
- `phases/CURRIER_A_STRUCTURE_V2/results/consolidated_summary.json`
- `phases/CURRIER_A_STRUCTURE_V2/results/first_line_composition.json`
- Builds on: C827, C833, C834
- Extended by: C882, C883, C884
