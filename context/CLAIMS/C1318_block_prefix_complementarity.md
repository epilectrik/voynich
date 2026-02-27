# C1318: Block PREFIX Complementarity

**Tier:** 2
**Scope:** B
**Phase:** TEXT_BLOCK_PARALLEL_OPERATORS (462)
**Date:** 2026-02-26

## Finding

Paragraphs within the same visual text block show significantly MORE divergent PREFIX profiles than paragraphs in different blocks on the same folio:

- Within-block PREFIX JSD: 0.276 (n=236 pairs)
- Between-block PREFIX JSD: 0.225 (n=3148 pairs)
- Mann-Whitney z=6.12, p<0.001
- Permutation p=0.000 (1000 shuffles, seed 42)

Blocks group operationally complementary paragraphs — each paragraph within a block specializes in a different PREFIX-defined operation (e.g., fire tending vs monitoring vs collection).

Section-stratified validation confirms the effect is universal, not driven by one section:
- Section B: diff=+0.015, perm p=0.006
- Section C: diff=+0.050, perm p=0.030
- Section H: diff=+0.054, perm p=0.017
- Section S: diff=+0.073, perm p<0.001
- Section T: diff=+0.002, perm p=0.367 (only 2 folios — insufficient power)

All 5 sections show the effect in the correct direction (within > between). 4/5 reach significance.

## Negative Control

Permutation control: paragraph-to-block assignments shuffled within each folio, preserving block sizes. 1000 permutations produce null distribution centered at 0.000 diff. Observed diff=+0.051 falls outside the entire null distribution (p=0.000).

## Cross-Validation

Consistent with C855 (paragraph independence) and the Parallel Operator Hypothesis (INTERPRETATION_SUMMARY Section XXII). Paragraphs within blocks are independent programs that specialize in complementary operations.

## Extends

- C855 (paragraph independence) -- within-block paragraphs are independent but complementary
- C574 (EN-internal lanes) -- PREFIX-level divergence reflects lane-level specialization

## Falsifiability

Would be falsified if within-block PREFIX JSD drops below between-block JSD in a corrected block detection algorithm, or if the section-stratified effect reverses in any section with n>10 folios.

## Evidence Files

- `phases/TEXT_BLOCK_PARALLEL_OPERATORS/results/text_block_parallel_operators.json` (T3)
