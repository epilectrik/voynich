# Phase: PUFF_COMPLEXITY_CORRELATION

**Status:** COMPLETED
**Date:** 2026-01-15
**Output:** `results/puff_regime_complexity.json`

## Summary

Tests the hypothesis that Puff material chapters are ordered by B grammar complexity. Specifically: Material N requires the cumulative capability achieved by folio N (not folio N specifically).

## Tests Performed

1. Puff Position -> REGIME Correlation
2. Puff Category -> REGIME Distribution
3. Dangerous Flag -> REGIME Association
4. Cumulative Capability Threshold
5. CEI -> Puff Complexity Correlation
6. Negative Control (shuffle test)

## Scripts

- `puff_regime_complexity_test.py` - Main correlation test

## Dependencies

- `results/puff_83_chapters.json` - Puff chapter data
- `results/proposed_folio_order.txt` - Folio ordering with REGIME

## Constraints Affected

- Supports Tier 4 interpretation of B folio ordering
- Referenced in `context/SPECULATIVE/INTERPRETATION_SUMMARY.md`
