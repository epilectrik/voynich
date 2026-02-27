# C1319: Block-Initial Paragraph Enrichment

**Tier:** 2
**Scope:** B
**Phase:** TEXT_BLOCK_PARALLEL_OPERATORS (462)
**Date:** 2026-02-26

## Finding

Block-initial paragraphs (first paragraph in each visual text block) are significantly enriched for HT tokens and MARKING category compared to block-internal paragraphs:

- HT density: initial=7.32% vs internal=4.85% (Mann-Whitney z=7.07, p<0.001)
- MARKING rate: initial=9.42% vs internal=7.00% (Mann-Whitney z=4.81, p<0.001)

Sample: 484 block-initial paragraphs, 190 block-internal paragraphs.

This parallels the line-1 enrichment pattern (C842/C747) at a higher organizational level: just as line-1 tokens serve as headers for lines, block-initial paragraphs serve as headers for blocks.

## Negative Control

The HT and MARKING enrichment is specific to block-initial position, not a general folio-position effect. Internal paragraphs (non-first within block) show lower rates regardless of their position within the folio.

## Cross-Validation

Consistent with:
- C842 (line-1 HT enrichment) -- same pattern at line level
- C747 (paragraph header zone) -- same pattern at paragraph level
- C1317 (block census) -- blocks have structural internal organization

## Extends

- C842 (line-1 HT enrichment) -- block-level analogue of line-level enrichment
- C747 (paragraph zones: HEADER/BODY/TAIL) -- block-level header pattern

## Falsifiability

Would be falsified if block-initial vs block-internal HT density difference reverses or becomes non-significant (p>0.01) with corrected block boundaries, or if the effect disappears when controlling for paragraph size.

## Evidence Files

- `phases/TEXT_BLOCK_PARALLEL_OPERATORS/results/text_block_parallel_operators.json` (T6)
