# C1323: Cross-Block Gallows Restart

**Tier:** 2
**Scope:** B
**Phase:** BLOCK_EXECUTION_CYCLE (464)
**Date:** 2026-02-26

## Finding

The gallows k/f/p→t cycle (C1321) restarts at block boundaries. Block-final paragraphs are t-enriched (39.8%) while block-initial paragraphs are k/f/p-enriched (72.3% vs 60.2% at block-final).

**Contingency table (gallows x position):**
- FINAL: f=4.6%, k=7.1%, p=48.5%, t=39.8% (n=392)
- INITIAL: f=5.0%, k=6.0%, p=61.2%, t=27.7% (n=397)
- Chi-sq=14.82, df=3, p=0.002

The execution cycle initiation (k/f/p) → continuation (t) restarts at each block boundary: the final paragraph in a block is more likely to be t-initial (continuation), and the first paragraph of the next block is more likely to be k/f/p-initial (initiation).

403 cross-block transitions tested across 82 B folios.

## Interpretation

Each block runs a complete gallows cycle: paragraphs progress from initiation phase (k/f/p) to continuation phase (t), then the next block resets to initiation. This establishes blocks as gallos-delimited execution stages, not just visual groupings.

However, block boundaries carry NO vocabulary-level termination signatures (C1324) — the restart is a structural marker (gallows reset) not a content marker (-am, suffix mode, category shift).

## Extends

- C1321 (gallows within-block ordering) — extends from within-block to cross-block: the cycle actively restarts
- C864 (gallows as paragraph marker) — gallows mark both paragraph AND block structure
- C1317 (block census) — blocks have gallows-level execution structure

## Falsifiability

Would be falsified if block-initial paragraphs show t-enrichment equal to or greater than block-final, or if chi-squared p>0.05 with corrected block detection.

## Evidence Files

- `phases/BLOCK_EXECUTION_CYCLE/results/block_execution_cycle.json` (A1)
