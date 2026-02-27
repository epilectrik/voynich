# C1324: Block-Final Termination Absence

**Tier:** 2
**Scope:** B
**Phase:** BLOCK_EXECUTION_CYCLE (464)
**Date:** 2026-02-26

## Finding

Block-final paragraphs show NO additional termination signatures beyond normal paragraph endings. Block boundaries are gallows-level structural markers, not vocabulary-level content markers.

**-am termination (B1):**
- Block-final -am rate: 4/109 = 3.7%
- Block-internal -am rate: 19/188 = 10.1%
- Enrichment: 0.36x (DEPLETED, not enriched)
- Fisher exact p=0.990 (not significant in enrichment direction)

**Suffix mode (B2):**
- Block-final Mode B rate: 58.9%
- Block-internal Mode B rate: 58.9%
- Chi-sq=0.00, p=0.959 (identical)

**Category profile (B3):**
- 0/8 categories show significant difference between block-final and block-internal paragraph tails
- Closest: OPERATION p=0.094 (not significant)

The block-final -am depletion (0.36x) suggests -am termination is a WITHIN-block handoff signal, not a block-boundary marker. Paragraphs ending mid-block may use -am to signal completion before the next operation starts, while block-final paragraphs transition structurally via gallows reset (C1323).

## Negative Control

C1237 establishes -am at 5.19x enrichment at paragraph-final positions generally. The block-final depletion (0.36x) is measured against this already-elevated paragraph-final baseline, showing that block position does not add additional -am signal.

## Extends

- C1237 (paragraph-final -am enrichment) — block position does not add to paragraph-level -am signal
- C845 (gallows structural marker) — block boundaries are gallows-level, consistent with C845
- C1323 (gallows restart) — gallows provide the block boundary signal, not vocabulary

## Falsifiability

Would be falsified if block-final -am rate exceeds block-internal by >1.5x with Fisher p<0.01, or if any category shows significant block-final enrichment (p<0.001) in >=2 sections.

## Evidence Files

- `phases/BLOCK_EXECUTION_CYCLE/results/block_execution_cycle.json` (B1, B2, B3)
