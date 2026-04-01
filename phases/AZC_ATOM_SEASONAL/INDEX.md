# AZC_ATOM_SEASONAL — Exploratory

**Status:** EXPLORATORY (not formalized)
**Date:** 2026-03-31

## Purpose
Atom-level analysis of zodiac folios to test whether seasonal differentiation appears in MOD/TERM atom distributions.

## Key Finding
- **i/d MOD swap** (chi2=39.3, p=0.0006): Summer/Winter zodiac folios are i-dominant (`aiin` family), Spring/Autumn are d-dominant (`-ody` family). Two structurally distinct token populations with different HEAD, MOD, and TERM profiles.
- HEAD atoms also differ (p=0.005): Autumn has elevated e-HEAD (43.5%).
- TERM atoms NOT significant (p=0.104).
- e_depth gradient: Autumn highest (0.813), Winter lowest (0.515).
- f57v R2 variant mapping to folio clusters: **negative result** (p=0.34).

## Constraint Registered
- C1908: Zodiac folio i/d MOD swap (pending registration)

## Scripts
| Script | Purpose |
|--------|---------|
| s1_zodiac_atom_profiles.py | Per-folio and per-season atom profiles, chi-squared tests |
| s2_id_swap_analysis.py | Token-level i/d analysis, HEAD+i/d compounds, word families |
| s3_r2_variant_mapping.py | Test R2 parameterized variants → folio cluster mapping (negative) |

## Results
All in `results/` — JSON outputs from each script.
