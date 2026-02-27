# C1317: Visual Text Block Census

**Tier:** 2
**Scope:** B
**Phase:** TEXT_BLOCK_PARALLEL_OPERATORS (462)
**Date:** 2026-02-26

## Finding

91.5% of Currier B folios (75/82) contain 2+ visual text blocks, detected by par_initial counter resets in the transcript. Total: 485 blocks across 82 folios.

Block count varies dramatically by section (Kruskal-Wallis H=56.8, p<0.001):
- Section S (recipe/stars): 12.43 blocks/folio (range 6-18), 1.17 paras/block
- Section T (textual): 8.0 blocks/folio (range 6-10), 1.81 paras/block
- Section B (bio/bathing): 4.55 blocks/folio (range 2-8), 1.59 paras/block
- Section C (cosmological): 4.0 blocks/folio (range 2-6), 1.70 paras/block
- Section H (herbal): 2.25 blocks/folio (range 1-4), 1.86 paras/block

Block token size also section-specific (KW H=123.5, p<0.001): Section B blocks average 104.1 tokens, Section H 51.2, Section S 49.0.

## Negative Control

Section H shows lowest multi-block rate (78.1%) and fewest blocks/folio (2.25), consistent with herbal folios having simpler page layouts. The census correctly captures this section-specific variation.

## Cross-Validation

Block detection aligns with the par_initial counter reset mechanism in the Takahashi transcript. The counter runs sequentially within each visual text clump and resets at visual boundaries. Census results match independent spot-checks (e.g., f75r: 3 blocks confirmed visually).

## Extends

- C855 (paragraph independence) -- blocks are a higher-level organizational unit containing independent paragraphs
- C747/C963 (paragraph zones) -- block-level structure parallels paragraph-level zones

## Falsifiability

Would be falsified if par_initial resets are shown to be transcription artifacts rather than layout-based, or if multi-block rate drops below 80% with a corrected detection algorithm.

## Evidence Files

- `phases/TEXT_BLOCK_PARALLEL_OPERATORS/results/text_block_parallel_operators.json` (T1, T7)
