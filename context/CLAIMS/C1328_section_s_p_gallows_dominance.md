# C1328: Section S p-Gallows Dominance

**Tier:** 2
**Scope:** B, section-S
**Phase:** SECTION_S_BLOCK_ARCHITECTURE (465)
**Date:** 2026-02-26

## Finding

Section S has its own gallows transition structure, distinct from the k/f/p→t pattern (C1321) observed in multi-paragraph blocks. p-gallows dominates and self-continues.

**Section S gallows distribution (286 blocks):**
- p: 59.8%, t: 25.5%, k: 8.4%, f: 6.3%

**Section S transition matrix (chi-sq=61.58, df=9, p<0.001):**
- p→p: 69% (strong self-continuation)
- t→p: 53% (t transitions back to p)
- k→p: 43%, k→t: 35%
- f→p: 41%, f→f: 41%

**Comparison with non-S (chi-sq=108.79):**
- Non-S shows k/f/p→t flow with t→t at 47% (C1321)
- S shows p→p flow with p self-continuing at 69%
- Gallows TYPE distribution is similar between S and non-S (chi-sq=3.13, p=0.341)

**Key difference:** In non-S multi-paragraph blocks, the gallows cycle is k/f/p (initiation) → t (continuation). In S single-paragraph blocks, p IS the dominant mode throughout. The initiation→continuation distinction collapses when blocks have only one paragraph — everything is "continuation."

## Interpretation

Section S blocks are overwhelmingly in p-mode ("running"). There is no initiation→continuation transition because each block is already a single running paragraph. The p→p self-continuation reflects that consecutive monitoring checkpoints are all mid-process observations, not initiations of new cycles.

## Extends

- C1321 (gallows within-block ordering) — S represents a different deployment of the same gallows system
- C1323 (cross-block gallows restart) — restart pattern does not apply in S where blocks are single-paragraph

## Evidence Files

- `phases/SECTION_S_BLOCK_ARCHITECTURE/results/section_s_block_architecture.json` (S3)
