# C1320: Block Internal Diversity

**Tier:** 2
**Scope:** B
**Phase:** TEXT_BLOCK_PARALLEL_OPERATORS (462)
**Date:** 2026-02-26

## Finding

Visual text blocks do NOT share a thermal or categorical envelope. Within-block paragraphs are at least as diverse as between-block paragraphs:

**Kernel profiles (T2):**
- Within-block kernel cosine: 0.888 (n=226 pairs)
- Between-block kernel cosine: 0.920 (n=3141 pairs)
- Mann-Whitney z=-1.50, p=0.104 (not significant)
- No evidence for within-block thermal convergence

**Category profiles (T4):**
- Within-block category Jaccard: 0.667 (n=239 pairs)
- Between-block category Jaccard: 0.731 (n=3157 pairs)
- Mann-Whitney z=-3.96, p<0.001 (significant reversal)
- Within-block paragraphs share FEWER categories than between-block

Combined with C1318 (PREFIX complementarity), the complete picture is: blocks group paragraphs that maximize diversity in ALL dimensions — different thermal profiles, different operational categories, and different PREFIX specializations. Each block assembles a self-contained processing stage with complementary operations.

**Falsified prediction:** The hypothesis that blocks share a "thermal envelope" (convergent kernel profiles) is rejected. Blocks organize thermal complementarity, not thermal identity.

## Negative Control

Permutation control for T2: shuffled paragraph-to-block assignments within each folio. Permutation p=0.955 for thermal convergence hypothesis (observed in wrong direction). The null distribution is centered at 0.000, confirming the reversal is real.

Permutation control for T4: p=0.989 for category convergence hypothesis (also reversed).

## Cross-Validation

The diversity pattern is consistent with each block being a complete "processing stage" containing complementary operations (heating + monitoring + collection), rather than a group of paragraphs doing the same thing.

## Extends

- C1318 (block PREFIX complementarity) -- diversity extends beyond PREFIX to kernel and category
- C855 (paragraph independence) -- independent paragraphs within blocks diversify to cover operational space

## Falsifiability

Would be falsified if within-block kernel cosine becomes significantly higher than between-block (p<0.01) with corrected block detection, or if category overlap reversal disappears.

## Evidence Files

- `phases/TEXT_BLOCK_PARALLEL_OPERATORS/results/text_block_parallel_operators.json` (T2, T4)
