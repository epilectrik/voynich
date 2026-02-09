# A_B_CORRESPONDENCE_SYSTEMATIC Findings

**Date:** 2026-01-29
**Status:** COMPLETE
**Verdict:** MEANINGFUL CORRESPONDENCE AT AGGREGATED LEVEL

---

## Executive Summary

**THE DEFINITIVE ANSWER:**

| A Unit | B Unit | Best-Match Coverage | Random | Lift |
|--------|--------|---------------------|--------|------|
| Paragraph | Paragraph (>=10 PP) | 58.3% | 28.5% | **2.04x** |
| Paragraph | Folio | 36.9% | 20.1% | 1.83x |
| Folio | Folio | 59.8% | 37.5% | 1.60x |
| **Folio** | **Paragraph** | **81.2%** | 47.4% | 1.71x |

**Key Finding:** An A folio provides 81% vocabulary coverage for a B paragraph. This is sufficient for B program usability.

**Multiple A paragraphs:**
- 2 A paragraphs → 76.5% coverage
- 3 A paragraphs → 80.4% coverage
- 5 A paragraphs → 84.7% coverage

---

## The Answer

**Does an A record constrain/relate to a B program?**

**YES, but at the right level of aggregation:**

1. **A paragraph → B paragraph: 58%** (insufficient alone)
2. **A folio → B paragraph: 81%** (sufficient)
3. **2-3 A paragraphs → B paragraph: 76-80%** (sufficient)

**The relationship is real** (2.04x lift over random), but operates at folio or multi-paragraph level, not single paragraph.

---

## What Works vs What Doesn't

### Works (Real Signal)

| Approach | Result | Meaning |
|----------|--------|---------|
| A folio → B paragraph | 81.2% coverage, 1.71x lift | A folios provide B vocabulary |
| A para → B para (best-match) | 58.3%, 2.04x lift | Structure exists at para level |
| Multi-para aggregation | 80%+ with 3 paragraphs | Aggregation works |

### Doesn't Work (Artifacts or Null)

| Approach | Result | Meaning |
|----------|--------|---------|
| Lane balance matching | 0.99x lift | Artifact of best-match algorithm |
| Kernel matching | 1.17x lift | Marginal, not useful |
| Hazard exposure | 99.7% match | Too universal to discriminate |

---

## The Model

```
A FOLIO (multiple paragraphs)
├── Paragraph 1: ~20 PP MIDDLEs
├── Paragraph 2: ~20 PP MIDDLEs
├── ...
└── Combined: 60-100 PP MIDDLEs
         │
         ▼
    81% coverage of B paragraph vocabulary
         │
         ▼
B PARAGRAPH (mini-program)
├── 15-30 PP MIDDLEs
└── Executes with available vocabulary
```

**Interpretation:**
- A folios are "material contexts" that define available vocabulary
- B paragraphs are "mini-programs" that execute with that vocabulary
- The operator selects an A context (folio) appropriate for their material
- B programs execute using the vocabulary available in that context

---

## Implications

1. **A and B are related** - 2x lift over random is meaningful
2. **Aggregation is required** - Single A paragraph insufficient (~58%)
3. **A folio is natural unit** - 81% coverage matches B paragraph needs
4. **No 1:1 mapping** - Multiple A contexts can work with same B program
5. **Operator judgment needed** - System doesn't auto-select; operator chooses

---

## Proposed Constraint

**C885: A-B Vocabulary Correspondence (Tier 2)**

> A folios provide 81.2% vocabulary coverage for B paragraphs (1.71x vs random). Single A paragraphs provide 58.3% (2.04x vs random). Aggregating 2-3 A paragraphs achieves 76-80% coverage. The relationship is meaningful but requires folio-level or multi-paragraph aggregation; single A paragraphs are insufficient for B program execution.

**Evidence:** Definitive test across 306 A paragraphs, 114 A folios, 481 large B paragraphs, 82 B folios.

---

## Files Generated

- `results/definitive_test.json` - Core A-B coverage results
- `results/unit_para_para_large.json` - Paragraph matching
- `results/lane_balance.json` - Lane matching (null result)
- `results/kernel_accessibility.json` - Kernel matching (weak)
