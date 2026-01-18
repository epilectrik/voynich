# Phase: SURVIVOR_SET_COUNT

**Status:** COMPLETED
**Date:** 2026-01-16
**Output:** `results/survivor_set_count.json`

## Summary

Tests how many distinct survivor-sets Currier A produces when quotiented by AZC compatibility. This tests whether |A/AZC| approximates 83.

## Hypothesis

Expert claim: "~80ish distinct survivor-set bundles once phase legality and hub rationing are enforced"

## Method

1. Extract all A lines with their MIDDLE sets
2. For each A line, identify which AZC folios it's compatible with (via shared MIDDLEs)
3. Group A lines by their AZC compatibility profile
4. Count the resulting equivalence classes

## Scripts

- `survivor_set_count.py` - Main survivor-set counting logic

## Constraints Affected

- Tests A-AZC-B coupling claims
- Related to C427 (single-line A records)
- Related to AZC compatibility filtering
