# C1326: Cross-Block Category Continuity

**Tier:** 2
**Scope:** B
**Phase:** BLOCK_EXECUTION_CYCLE (464)
**Date:** 2026-02-26

## Finding

Adjacent blocks are MORE categorically similar to each other than paragraphs within the same block. Cross-block category JSD is significantly LOWER than within-block cross-paragraph JSD.

- Cross-block category JSD: 0.071 (n=403 transitions)
- Within-block cross-paragraph JSD: 0.136 (n=192 pairs)
- Mann-Whitney z=-8.98, p<0.001
- Permutation p=1.000 (observed in wrong direction for discontinuity hypothesis)

This is the inverse of what a "discontinuity at boundaries" hypothesis predicts. Block boundaries do NOT introduce categorical breaks — instead, the high within-block diversity (C1320) makes within-block paragraph pairs MORE different than cross-block paragraph pairs.

## Interpretation

Adjacent blocks draw from the same folio REGIME (C1325), so their aggregate category profiles are similar. But within a block, paragraphs DIVERSIFY maximally (C1320, C1318). The result: crossing a block boundary is categorically smooth, while crossing a paragraph boundary within a block is categorically jarring.

This rules out a "block = categorically distinct stage" model. Blocks are not operationally different from each other — they are operationally diverse WITHIN themselves.

## Extends

- C1320 (block internal diversity) — cross-block continuity is the complement of within-block diversity
- C1325 (folio REGIME homogeneity) — adjacent blocks share REGIME, explaining their category similarity
- C1318 (PREFIX complementarity) — operational diversity is within-block, not between-block

## Falsifiability

Would be falsified if cross-block category JSD significantly exceeds within-block (MW p<0.01), showing block boundaries as categorical discontinuities.

## Evidence Files

- `phases/BLOCK_EXECUTION_CYCLE/results/block_execution_cycle.json` (A4)
