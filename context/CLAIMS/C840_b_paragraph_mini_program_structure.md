# C840: B Paragraph Mini-Program Structure

**Tier:** 2
**Scope:** B
**Phase:** B_PARAGRAPH_STRUCTURE

## Constraint

Currier B paragraphs function as mini-programs within folios, exhibiting header-body structure with line 1 showing +15.8pp HT enrichment over body lines. The effect is independent of folio position.

## Evidence

From paragraph_analysis.json:

**All paragraphs (n=478 with 2+ lines):**

| Zone | HT% |
|------|-----|
| Paragraph line 1 | 44.9% |
| Paragraph body (lines 2+) | 29.1% |
| **Delta** | **+15.8pp** |

**Statistical significance:**
- Wilcoxon z = 13.63, p < 10^-20
- Cohen's d = 0.721
- Direction: 363 positive / 10 zero / 105 negative (76% show enrichment)

**Mid-folio paragraphs only (n=391):**
- Line 1: 43.6% HT
- Body: 29.4% HT
- Delta: +14.2pp

The effect persists even for paragraphs NOT starting at folio line 1.

## Structural Hierarchy

```
B FOLIO (program)
├── Paragraph 1 (mini-program)
│   ├── Line 1: HEADER (45% HT - identification markers)
│   └── Lines 2+: BODY (29% HT - operational grammar)
├── Paragraph 2 (mini-program)
│   ├── Line 1: HEADER
│   └── Lines 2+: BODY
...
```

Mean 7.1 paragraphs per folio, mean 4.4 lines per paragraph.

## Interpretation

Each B paragraph is a self-contained mini-program with:
1. **Header zone** (line 1): Identification/context-setting vocabulary (HT-dominated)
2. **Body zone** (lines 2+): Operational 49-class grammar

This parallels A paragraph structure (RI header + PP body) and suggests paragraph-level correspondence between systems.

## Provenance

- Script: `phases/B_PARAGRAPH_STRUCTURE/investigate_paragraphs_v2.py`
- Data: `phases/B_PARAGRAPH_STRUCTURE/results/paragraph_analysis.json`
- Depends: C747 (folio line 1 HT), C166 (HT identification), C404 (HT non-operational)

## Status

CONFIRMED - Statistical significance overwhelming (p < 10^-20).
