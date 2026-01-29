# B_PARAGRAPH_STRUCTURE: Findings

**Phase Status:** COMPLETE
**Date:** 2026-01-29

## Summary

Currier B paragraphs function as **mini-programs** within folios, exhibiting the same header-body structure documented at the folio level (C747, C748). Each paragraph has a single-line header zone with elevated HT (unclassified token) density, followed by a body zone dominated by operational 49-class grammar.

## Key Findings

### 1. Paragraph Statistics

| Metric | Value |
|--------|-------|
| Total B paragraphs | 585 |
| B folios | 82 |
| Mean paragraphs/folio | 7.1 |
| Mean lines/paragraph | 4.4 |
| Max paragraphs (f66r) | 37 |

### 2. HT Enrichment at Paragraph Boundaries

**All paragraphs (n=478 with 2+ lines):**
- Paragraph line 1: 44.9% HT
- Paragraph body: 29.1% HT
- Delta: **+15.8pp**
- Wilcoxon z = 13.63, p < 10^-20
- Cohen's d = 0.72

**Mid-folio paragraphs only (n=391):**
- Paragraph line 1: 43.6% HT
- Paragraph body: 29.4% HT
- Delta: **+14.2pp**

**Comparison to folio-level (C747):**
- Folio line 1: 50.2% HT
- Folio body: 29.8% HT
- Delta: +20.3pp

The paragraph-level effect is slightly weaker than folio line 1 (which may combine folio header + paragraph header functions) but remains highly significant.

### 3. Step Function Pattern

HT fraction by paragraph line position (196 paragraphs with 5+ lines):

| Position | HT% |
|----------|-----|
| 1 | 45.2% |
| 2 | 26.5% |
| 3 | 26.2% |
| 4 | 27.1% |
| 5+ | 25.6% |

**Interpretation:** The drop from position 1 to position 2 is sharp and complete (18.7pp). Positions 2+ are flat. This mirrors C748 (folio-level step function).

### 4. Paragraph Initiation Patterns

**First character of paragraph-initial tokens:**
- Gallows (p/t/k/f): **71.5%**
- `p`: 43.6%, `t`: 19.3%, `o`: 12.0%, `k`: 5.5%, `f`: 3.1%

**Top prefixes:**
- `pch`: 16.9%
- `po`: 16.6%
- (none): 12.1%
- `sh`: 11.6%
- `tch`: 6.5%

**HT rate by prefix:**
- `sh`: 94.1% HT
- `po`: 85.6% HT
- `ol`: 85.7% HT
- `pch`: 78.8% HT
- `tch`: 65.8% HT
- `qo`: 35.7% HT (mostly operational)

**Key observation:** pch- and po- combined account for 33.5% of paragraph initiators and are predominantly HT tokens. They function as **paragraph markers** rather than operational instructions.

### 5. Folio Line 1 vs Mid-Folio Paragraphs

| Start Position | Count | First Token HT% |
|----------------|-------|-----------------|
| Folio line 1 | 100 | 79.0% |
| Elsewhere | 485 | 73.8% |

The patterns are consistent regardless of where in the folio the paragraph starts.

## Structural Interpretation

B folios contain approximately 7 **mini-programs** (paragraphs) each. Each mini-program has:

1. **Header zone** (line 1): 45% HT vocabulary, including:
   - Paragraph identification markers (pch-, po-, sh- initial HT tokens)
   - Potentially folio-specific or context-setting vocabulary

2. **Body zone** (lines 2+): 26-29% HT, dominated by:
   - 49-class operational grammar
   - Control loop instructions (k/h/e operators)
   - Hazard navigation sequences

Folio line 1 is a special case where the **folio header** and **first paragraph header** overlap, producing the elevated 50.2% HT rate documented in C747.

## Relation to Existing Constraints

- **C747 (Line-1 HT Enrichment):** Paragraph structure partially explains this. Folio line 1 = folio header + paragraph 1 header.
- **C748 (Line-1 Step Function):** Confirmed at paragraph level. HT is header-only.
- **C233 (LINE_ATOMIC):** Paragraphs reinforce that lines are control blocks; paragraphs bundle related control blocks.
- **C166 (HT identification):** Paragraph initiators are predominantly HT vocabulary.

## Constraints Produced

| # | Name | Finding |
|---|------|---------|
| C840 | B Paragraph Mini-Program Structure | Line 1: 44.9% HT vs body 29.1%, +15.8pp, p<10^-20 |
| C841 | B Paragraph Gallows-Initial Markers | 71.5% p/t/k/f initial, matching A paragraph structure |
| C842 | B Paragraph HT Step Function | Pos 1=45.2%, pos 2=26.5%, body flat; -18.7pp drop |
| C843 | B Paragraph Prefix Markers | pch- + po- = 33.5% of initiators, 78-86% HT |
| C844 | Folio Line 1 Double-Header | 50.2% HT = folio header + paragraph 1 header overlap |
| C845 | B Paragraph Self-Containment | No inter-paragraph linking; 7.1% both-position rate (vs A's 0.6%); no ct-ho signature |

## Source Files

- `phases/B_PARAGRAPH_STRUCTURE/investigate_paragraphs.py`
- `phases/B_PARAGRAPH_STRUCTURE/investigate_paragraphs_v2.py`
- `phases/B_PARAGRAPH_STRUCTURE/scripts/b_ht_linker_test.py`
- `phases/B_PARAGRAPH_STRUCTURE/scripts/b_ht_linker_deep.py`
- `phases/B_PARAGRAPH_STRUCTURE/results/paragraph_analysis.json`
- `phases/B_PARAGRAPH_STRUCTURE/results/b_ht_linker_test.json`
