# Phase: MULTI_LINE_RECORDS

**Status:** COMPLETED (CLOSED)
**Date:** 2026-01-15
**Outcome:** Multi-line record hypothesis FALSIFIED; Single-line records CONFIRMED

## Summary

Tests whether structural tokens truly restrict AZC folios or whether apparent restrictions were artifacts of incomplete data. Using all 30 ZACHS folios confirms:

1. Structural tokens ARE genuinely restrictive (not artifact)
2. Single-line records ARE the correct segmentation (robust)
3. Adding C/H/S sections makes NO difference (invariant)

## Scripts

- `compatibility_boundary_test.py` - Tests compatibility boundaries
- `full_azc_landscape_test.py` - Full AZC landscape analysis

## Output

- `results/full_azc_landscape.json`

## Detailed Report

See [AZC_CLOSURE_REPORT.md](AZC_CLOSURE_REPORT.md) for full analysis and findings.

## Constraints Affected

- Confirms C427 (single-line A records)
- Supports CASC segmentation rules
