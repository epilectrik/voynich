# Phase: TTDT_terminal_differentiation

**Status:** COMPLETED
**Date:** 2026-01-16
**Output:** `results/ttdt_results.json`, `results/ttdt_results_v2.json`, `results/within_folio_diversity.json`, `results/middle_universality.json`

## Summary

Terminal Trajectory Differentiation Test (TTDT) - tests whether Currier B folios define distinct terminal execution profiles that cannot be reduced to REGIME, hazard level, or AZC legality alone.

## Expert Predictions

- ~83 stable clusters -> B folios ARE outcome-typed, 83 is structurally forced
- ~4 clusters -> B only encodes REGIME, hypothesis falsified
- ~10-20 clusters -> Outcome types exist but not 1:1 with folios
- No stable clustering -> 83 remains unexplained

## Method

1. Define terminal profile vector using B-internal metrics
2. Regress out REGIME to get residuals
3. Cluster the residual terminal profiles
4. Evaluate cluster count vs 83

## Scripts

- `ttdt_test.py` - Version 1 of TTDT
- `ttdt_test_v2.py` - Version 2 with refined metrics
- `within_folio_diversity.py` - Within-folio diversity analysis
- `middle_universality_test.py` - MIDDLE universality testing

## Constraints Affected

- Tests whether 83 B folios represent distinct execution endpoints
- Related to REGIME stratification (C394-C396)
- Related to outcome typing interpretation (Tier 4)
