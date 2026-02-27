# C1329: Section S Block Categorical Diversity

**Tier:** 2
**Scope:** B, section-S
**Phase:** SECTION_S_BLOCK_ARCHITECTURE (465)
**Date:** 2026-02-26

## Finding

Section S blocks within a folio are MORE categorically diverse than blocks in other sections, not less. This reverses the "parallel stations" prediction and shows S blocks specialize in different operational domains.

**Within-folio between-block category JSD:**
- Section S: 0.069 (n=1741 pairs)
- Non-S: 0.052 (n=357 pairs)
- MW z=7.20, p<0.001

**Per-section breakdown:**
- C: 0.025 (most homogeneous)
- B: 0.044
- H: 0.068
- S: 0.069
- T: 0.077 (most diverse)

**Within-folio kernel distance (REGIME):**
- S: 0.060 (NOT the most homogeneous)
- B: 0.033, C: 0.025 (more homogeneous)
- S significantly LESS homogeneous than B (z=6.54), C (z=2.98), T (z=2.68)

## Interpretation

Section S blocks are not all running the same protocol. Each block on a folio has a different operational focus (high category JSD), and even the kernel balance varies between blocks (high kernel distance). Combined with C1327 (ordinal progression), the picture is: S blocks progress through a sequence of operationally distinct monitoring checkpoints.

Despite the blocks being vocabulary-independent (S1: Jaccard 0.327 < non-S 0.438, p<0.001), they are categorically diverse. They use different words AND do different jobs. This is the extreme version of C1320 (blocks maximize internal diversity) — in S, each single-paragraph block IS a different job.

## Extends

- C1320 (block internal diversity) — S takes within-block diversity to the block-to-block level
- C1111 (Stars REGIME composition R1+R3) — REGIME diversity manifests at block level

## Falsifies

- Parallel stations prediction: if all blocks ran the same monitoring protocol, within-folio JSD should be LOW. It is HIGH.

## Evidence Files

- `phases/SECTION_S_BLOCK_ARCHITECTURE/results/section_s_block_architecture.json` (S4, S5)
