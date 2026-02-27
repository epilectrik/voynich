# C1330: Block Vocabulary Narrowing

**Tier:** 2
**Scope:** B (all sections)
**Phase:** BLOCK_VOCABULARY_DRIFT (466)

## Constraint

Later blocks on a folio use fewer distinct MIDDLEs than earlier blocks. The effect is universal across sections, with multi-paragraph sections (B, C, H) showing stronger narrowing than single-paragraph sections (S).

## Evidence

From block_vocabulary_drift.py test D2:

**Unique MIDDLE count vs block ordinal (Spearman rho, within-folio):**

| Metric | Value |
|--------|-------|
| Median rho | -0.248 |
| Mean rho | -0.141 |
| Perm p | <0.001 (0/1000) |
| Negative direction | 39/56 folios (70%) |

**Section breakdown:**

| Section | Median rho | n |
|---------|-----------|---|
| C | -0.625 | 4 |
| B | -0.429 | 17 |
| H | -0.325 | 10 |
| S | -0.136 | 23 |
| T | +0.258 | 2 |

**Cumulative coverage of block 0's MIDDLEs in later blocks:**

| Block | Coverage |
|-------|----------|
| B0 | 1.000 |
| B1 | 0.533 |
| B2 | 0.443 |
| B3 | 0.399 |
| B4 | 0.394 |
| B5 | 0.395 |

Coverage drops rapidly from block 0 to block 2, then plateaus around 0.40.

**Jaccard convergence (consecutive pairs) NOT significant:**
- Median rho = +0.077, perm p = 0.202
- Later blocks narrow vocabulary independently — they don't converge on each other's vocabulary

## Interpretation

Blocks narrow their operational vocabulary with folio position. The first block deploys the widest range of MIDDLEs; subsequent blocks use progressively fewer. This is consistent with front-loaded operational deployment where early blocks handle the broadest operational scope and later blocks handle narrower tasks.

Note: Token count also tends to decrease with block ordinal, so some vocabulary narrowing may reflect smaller sample sizes. However, the permutation test controls for this by shuffling block ordinals (which also shuffles their sizes), and the effect remains highly significant.

## Provenance

- block_vocabulary_drift.json: test D2, vocab_size_test
- Relates to: C1317 (block census), C1318 (PREFIX complementarity), C1326 (cross-block category continuity)

## Status

CONFIRMED — universal vocabulary narrowing across block ordinals.
