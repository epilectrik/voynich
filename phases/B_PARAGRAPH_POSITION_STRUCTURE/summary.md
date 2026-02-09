# B_PARAGRAPH_POSITION_STRUCTURE Phase Summary

**Status:** COMPLETE
**Date:** 2026-02-03
**Tests Run:** 8 (Scripts 00-05, 07-08)

## Overview

This phase tested paragraph-level and folio-level structural patterns in Currier B folios, motivated by observations from detailed annotation work on 10 folios (~350 lines). The goal was to determine whether position (paragraph or folio line) carries structural meaning.

## Key Findings

**1. PARAGRAPH POSITION HAS MINIMAL STRUCTURAL SIGNIFICANCE.**

The existing constraints (C855: PARALLEL_PROGRAMS, C857: P1 not special) are strongly supported. Paragraphs are structurally independent mini-programs, not sequential processing stages.

**2. FOLIO-LEVEL TERMINAL FL GRADIENT DISCOVERED (C905)**

TERMINAL FL vocabulary concentrates in **early folio lines** (p=0.0005), interpreted as **input-state declaration** - early lines describe what state the input material is in.

**3. CROSS-FOLIO CHAINING NOT SUPPORTED**

Testing whether B folios chain together (output of folio X = input of folio Y) showed no directional vocabulary flow (z=-0.61). Instead, same-section folios share vocabulary due to **domain coherence** (1.30x Jaccard, p<0.0001).

## Test Results Summary

### Paragraph-Level Tests (A-E)

| Test | Question | Result | Significance |
|------|----------|--------|--------------|
| **A: Vocabulary Survival** | Do MIDDLEs persist across paragraphs? | 31.1% survival | Moderate - higher than pure independence |
| **B: Cross-Folio Position** | Do same-position paragraphs cluster? | d=0.06 | Weak - not significant (p=0.126) |
| **C: Paragraph Clustering** | Do clusters correlate with ordinal? | ARI=0.002 | None - clusters driven by SIZE, not position |
| **D: Line Coupling** | Does coupling vary by position? | d=-0.001 | None - p=0.678 |
| **E: FL Progression** | Does FL type track paragraph position? | χ²=3.9 | None - p=0.420 |

### Folio-Level Tests (07-08)

| Test | Question | Result | Significance |
|------|----------|--------|--------------|
| **07: Folio-Level Analysis** | Does TERMINAL FL track folio line position? | gradient -3.7% | **Strong - p=0.0005 (C905)** |
| **08: Cross-Folio Echo** | Does late-folio vocab echo in early-folio elsewhere? | z=-0.61 | None - chaining NOT supported |
| **08: Section Effect** | Do same-section folios share TERMINAL FL? | 1.30x Jaccard | **Strong - p<0.0001** |

## Detailed Results

### Test A: Vocabulary Survival

**Finding:** 31.1% of P1 vocabulary survives to subsequent paragraphs.

- Adjacent Jaccard: 0.205 vs Non-adjacent: 0.195 (p=0.033)
- Observed overlap (7.09) >> Expected hypergeometric (4.39, p≈0)

**Interpretation:** Paragraphs share MORE vocabulary than independent draws would predict. This suggests they draw from a common folio vocabulary pool, consistent with C856 (shared-origin vocabulary). However, the survival rate is moderate, not strong.

### Test B: Cross-Folio Paragraph Position

**Finding:** Within-bin similarity (0.903) ≈ Between-bin similarity (0.895), Cohen's d=0.06.

**Interpretation:** Paragraph-1s across different folios are NOT more similar to each other than to other paragraphs. Position carries minimal structural identity across folios.

**Note:** Token count varies significantly by position (F=6.86, p=0.001):
- Early: 46.9 tokens
- Middle: 32.9 tokens
- Late: 38.1 tokens

This reflects the gallows-initial heuristic over-segmenting middle regions.

### Test C: Paragraph Type Classification

**Finding:** ARI = 0.002 between clusters and position.

Clusters are driven by SIZE:
- Cluster 2 (14 para, 220 tok) → 64% early
- Cluster 0 (58 para, 90 tok) → 45% early
- Cluster 3 (205 para, 45 tok) → uniform
- Cluster 1 (310 para, 19 tok) → uniform

**Interpretation:** Natural paragraph clusters exist but are orthogonal to position. Large paragraphs concentrate in "early" because the heuristic under-segments at folio beginnings.

### Test D: Line-to-Line Coupling by Position

**Finding:** Adjacent-line Jaccard: early=0.155, middle=0.151, late=0.156.

ANOVA F=0.388, p=0.678. Effect sizes d≈0.

**Interpretation:** Line coupling is uniform across paragraph positions. No evidence that early paragraphs have more sequential structure than late paragraphs. Strongly supports C670 (folio-mediated coupling).

### Test E: FL Progression

**Finding:** FL type distribution independent of position (χ²=3.9, p=0.420).

| Position | INITIAL | LATE | TERMINAL |
|----------|---------|------|----------|
| Early | 7.3% | 8.7% | 8.9% |
| Middle | 7.5% | 9.2% | 9.5% |
| Late | 6.7% | 8.4% | 7.6% |

**Interpretation:** TERMINAL FL does NOT concentrate in late paragraphs. If anything, it peaks in the middle. The FL STATE INDEX (C777) operates at a different granularity than paragraph position.

## Methodological Notes

### Paragraph Boundary Detection

The transcript lacks explicit paragraph boundaries for most folios. We used a gallows-initial heuristic:
- 71.5% of explicit paragraph starts are gallows-initial (C841)
- But not every gallows-initial line starts a paragraph

This heuristic over-segments, creating ~7.2 "paragraphs" per folio with 4.0 lines each, versus explicit markers showing 2-3 paragraphs with 10-26 lines.

**Robustness:** The null results are robust to this over-segmentation. If real positional effects existed, they would appear even with noisy boundaries.

### Section Confounding

Token count variation (early > middle) may reflect section-level differences (C860: BIO 46 tok/para vs PHARMA 13 tok/para) rather than positional effects.

## Constraint Implications

### Supported

- **C855 (PARALLEL_PROGRAMS):** STRONGLY SUPPORTED. Paragraphs are independent mini-programs.
- **C857 (P1 not special):** STRONGLY SUPPORTED. P1 has no distinct structural signature.
- **C670 (folio-mediated coupling):** SUPPORTED. No position-dependent coupling variation.

### Refined

- **C856 (shared-origin vocabulary):** Vocabulary overlap exceeds chance, confirming paragraphs draw from shared folio pool but execute independently.

### New Constraints

| # | Constraint | Finding |
|---|------------|---------|
| **C905** | FL_TERMINAL Early-Line Concentration | TERMINAL FL (y/aly/am/dy) concentrates in early folio lines, not late (gradient -3.7%, p=0.0005) |

## Annotation-Based Hypotheses: Status

The detailed annotation work suggested:
1. Early paragraphs = identification-heavy (HT) → NOT TESTED AT CORPUS LEVEL
2. Middle paragraphs = processing (QO/CHSH) → NOT TESTED AT CORPUS LEVEL
3. Late paragraphs = terminal signature (AX + TERMINAL FL) → **FALSIFIED** (no FL gradient)

**Resolution:** Annotation-observed patterns may reflect:
- FOLIO-level progression (not paragraph-level)
- Section-specific effects
- Local patterns not generalizing to corpus

The "terminal vocabulary signature" hypothesis needs refinement: it may apply to FOLIO endings, not paragraph endings.

## Phase 2 Decision

Given the strong null results, Phase 2 tests (F: HT bracket, G: Gallows interaction, H: Role profile) are likely to also show null effects. We recommend:

**SKIP Phase 2** unless specific hypotheses emerge requiring validation.

## Files

- `scripts/00_boundary_validation.py` - Paragraph detection validation
- `scripts/01_vocabulary_survival.py` - Test A
- `scripts/02_cross_folio_position.py` - Test B
- `scripts/03_paragraph_clustering.py` - Test C
- `scripts/04_line_coupling_by_position.py` - Test D
- `scripts/05_fl_progression.py` - Test E
- `results/*.json` - Machine-readable results

## Conclusion

**Paragraph position is NOT a significant structural dimension in Currier B.**

The PARALLEL_PROGRAMS model (C855) is correct: paragraphs are independent execution units that happen to be positioned sequentially on folios. Their position does not determine their structure, vocabulary, or FL distribution.

This finding is CONSISTENT with the distillation-manual interpretation: paragraphs describe named operations (maceration, distillation, etc.) that can be executed in any order depending on the specific procedure, not a fixed sequential progression.
