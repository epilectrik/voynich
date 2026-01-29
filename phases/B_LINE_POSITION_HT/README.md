# Phase: B_LINE_POSITION_HT

## Purpose

Test whether opening lines of Currier B folios have elevated HT (unclassified token) density compared to working lines, and characterize the effect.

## Background

Manual inspection of B folios revealed that opening lines appeared visually distinct — loaded with unclassified vocabulary that disappeared by line 3-4. No existing constraint (out of 562) addressed within-folio line-position HT density. Expert advisor validated this as a genuinely novel observation.

## Tests

| Test | Question | Verdict |
|------|----------|---------|
| T1 | Line-1 vs Lines-2+ HT density | **ENRICHED** (50.2% vs 29.8%, +20.3pp, d=0.99, p<10^-6) |
| T2 | Positional gradient shape | **GRADIENT** (step function: pos 1 elevated, pos 2-10 flat) |
| T3 | First-line HT morphology distinct? | **DISTINCT** (95.9% unique types, pch prefix 7.0% vs 1.9%, chi2=496) |
| T4 | Section breakdown | H=+27.1pp***, B=+19.1pp***, S=+14.7pp*** |
| T5 | Permutation test (10,000x) | **SIGNIFICANT** (z=11.07, p=0.0000) |
| T6 | Last-line enrichment | **LAST_NORMAL** (30.8% vs 29.8%, p=0.497) |

## Key Findings

### 1. Opening lines are HT-enriched (C747)

Line 1 of B folios averages 50.2% HT tokens vs 29.8% for all subsequent lines. 69 of 82 folios show positive enrichment. Cohen's d = 0.99 (large effect). Permutation test: z = 11.07, p = 0.0000 across 10,000 shuffles.

### 2. Sharp step function, not gradient (C748)

The enrichment is confined to exactly one line. Position 1 = 50.2%, position 2 = 31.7% (already at baseline), positions 3-10 = 27-33% (flat). The "header" zone is precisely one line.

### 3. First-line HT is morphologically distinct (C749)

First-line HT tokens show:
- 95.9% type uniqueness (vs 62.8% working-line HT)
- Elevated `pch` prefix: 7.0% vs 1.9% (3.7x)
- Reduced `qo` prefix: 9.4% vs 12.4%
- Higher articulator rate: 13.0% vs 9.9%
- PREFIX distribution: chi2 = 496.37, p < 10^-6

These are not the same HT tokens in a different position — they are a morphologically distinct sub-population.

### 4. Opening-only, no closing (C750)

Last lines have 30.8% HT, indistinguishable from interior (29.8%, p = 0.497). Programs begin with an identification header but end without HT-based closure.

### 5. Effect spans all sections

The effect is universal across manuscript sections, though magnitude varies:
- Herbal (H): +27.1pp (strongest)
- Stars/Recipe (S): +14.7pp
- Bio (B): +19.1pp
- Cosmological (C) and Text (T): positive but too few folios for significance

## Constraints Established

| # | Name | Tier |
|---|------|------|
| C747 | Line-1 HT Enrichment | 0 |
| C748 | Line-1 Step Function | 0 |
| C749 | First-Line HT Morphological Distinction | 2 |
| C750 | Opening-Only HT Asymmetry | 0 |

## Structural Implications

B folio-programs have a one-line non-operational header. This header:
- Uses vocabulary outside the 49-class grammar (HT tokens)
- Draws from nearly unique morphological forms (95.9% hapax)
- Is morphologically distinct from working-line HT (different prefix profile)
- Appears at the opening only — no closing counterpart

This connects to the program architecture: each folio is a complete program (C124), and the opening line identifies or contextualizes the program before the operational control sequence begins.

## Files

- `scripts/ht_line_position.py` — All tests
- `results/ht_line_position.json` — Full results with per-folio detail
