# Phase 665: III.19 ↔ f75r Quantitative Subrecipe-Paragraph Alignment

**Phase:** 665
**Status:** COMPLETE — VERDICT INCONCLUSIVE leaning FALSIFIED
**Started:** 2026-04-26
**Pre-reg commit:** 70ca0eb
**Motivation:** H1 from expert packet consultation (both experts ranked #1)

## Result

| Test | Value |
|---|---|
| Primary Spearman ρ | +0.3264 (below DIRECTIONAL 0.4 threshold) |
| Permutation p | 0.1988 |
| Pearson r (sanity) | +0.8276 (tail-dominated) |
| LOO: drop P9/III.19.8 | ρ collapses to +0.04 |

**Effect entirely carried by one pair (P9, 120T ↔ III.19.8, 2265 chars).** Without that pair, no quantitative alignment at all.

### Secondary verb-category densities (Bonferroni α=0.0125)

| Category | Spearman ρ | p | Status |
|---|---:|---:|---|
| DISTILLATION (qok vs Catalan dist) | -0.50 | 0.92 | REVERSED |
| MATERIAL_TAKE (pen/pol/pch vs Pren) | +0.44 | 0.13 | close to DIRECTIONAL |
| MATERIAL_PLACE (dar/dal vs met) | -0.11 | 0.61 | NULL |
| OBSERVATION (aiin/ain vs guarda) | -0.44 | 0.89 | REVERSED |

0/4 reach strict significance. 2/4 actually REVERSED.

## Methodological note

The transcript's `par_initial` markers segment f75r into only 3 paragraphs (235, 57, 120 tokens), inconsistent with the documented 9-paragraph structure (46, 9, 58, 39, 52, 31, 11, 46, 120) used in C1959 and the f75r decode. Phase 665 used line-range segmentation per the locked pre-reg (matches the documented decode). This methodology issue affects Phase 663 retrospectively — Phase 663's "12 CONFIRMED paragraphs" used par_initial-based segmentation, which gave only 3 paragraphs from f75r, not 9.

## What this confirms

1. **C1959's rank-correlation finding (paragraphs in approximately right order, mean ρ=+0.81 across 5-7 confirmed matches) does NOT extend to magnitude.** Paragraph sizes do not track subrecipe sizes at quantitative correlation strength on III.19/f75r.

2. **The 1:1 ordinal mapping may be wrong.** Multiple paragraphs likely map to subsets of subrecipes (or vice versa). The strict P_i ↔ III.19.{i-1} mapping fails.

3. **VMS atom proxies for verb categories are weak/REVERSED.** qok-density doesn't track DISTILLATION-verb count; aiin doesn't track OBSERVATION-verb count. Consistent with Phase 661's finding that DISTILLATION-verb-category doesn't carve VMS signatures cleanly.

## What this does NOT change

- C1959 stands at rank-correlation level (was tested at rank level; this phase tests at magnitude level — distinct claim)
- C1969, C1970 unaffected
- f75r ↔ III.19 match unchanged (still CONFIRMED via 5-6 independent levels)
- The matched-pair table is unchanged

## What this teaches

The expert convergence on H1 didn't survive contact with data. That's exactly what pre-registration is for — it caught a plausible-looking but non-holding pattern. Both experts independently identified the same hypothesis as highest-priority; the hypothesis wasn't wrong because they were wrong, it was wrong because the underlying structure isn't what they predicted from the existing constraint summary.

The methodologically-honest next step would test whether paragraph-to-subrecipe is a many-to-many mapping (multiple paragraphs aggregate to one subrecipe, or one paragraph spans multiple subrecipes) rather than 1:1.

## Untested next moves (NOT committed)

- **Cumulative-position alignment:** instead of pair-wise correlation, test whether cumulative paragraph position fraction (0% to 100%) tracks cumulative subrecipe position fraction. Less restrictive than 1:1 ordinal mapping.
- **Many-to-many DTW alignment:** Dynamic Time Warping between paragraph sequence and subrecipe sequence. Tests structural alignment without locking exact pairings.
- **Paragraph-sub-paragraph re-segmentation:** if III.19's 9 subrecipes don't 1:1 with f75r's 9 paragraphs, what segmentation DOES align? Reverse-engineer from longest-pair-anchor.

These are notes, not commitments.

## No constraint registered

Per pre-reg: SUPPORTED requires ρ ≥ 0.6 AND ≥ 2/4 secondary at strict α; neither holds. Verdict INCONCLUSIVE-leaning-FALSIFIED. No tier change to C1959 (which remains valid at its tested resolution).
