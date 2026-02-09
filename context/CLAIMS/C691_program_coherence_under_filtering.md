# C691: Program Coherence Under Filtering

**Status:** VALIDATED | **Tier:** 2 | **Phase:** A_RECORD_B_FILTERING | **Scope:** A-B

## Finding

Filtered B programs are **operationally incoherent** for typical A records. Operational completeness (line has setup + work + close roles) ranges from 0% (most pairings) to 20% (Max-classes, most permissive). Maximum consecutive empty/thin line gaps reach the entire folio length for restrictive records. Only the least restrictive A records (~14 PP MIDDLEs, 38 classes) produce marginally coherent programs.

## Operational Completeness Definition

A line is "operationally complete" if it retains at least one token from:
- **Setup group**: CC or AX
- **Work group**: EN or FQ
- **Close group**: FL or CC

## Key Numbers

| Record Profile | Complete Lines | Setup Coverage | Work Coverage | Max Gap |
|---------------|---------------|---------------|--------------|---------|
| Max-classes | 12-20% | 24-45% | 55-87% | 5-13 |
| High-PP | 0-11% | 13-25% | 38-52% | 13-23 |
| Low-PP | 0-5% | 6-15% | 7-25% | 16-54 |
| Median-PP | 0% | 0% | 0-24% | 16-45 |
| Min-classes | 0% | 0% | 0-6% | 16-54 |
| PURE_RI | 0% | 0-2% | 0% | 16-54 |

## Interpretation

The work group (EN/FQ) survives best — up to 87% coverage for the most permissive record. The close group (FL/CC) is the bottleneck: FL's high depletion (C683: 60.9%) and CC's moderate depletion (44.6%) starve the close function. A filtered B folio is not a reduced-but-functional program; it is a **vocabulary projection** showing which instructions the A record permits. Full operational coherence requires aggregating multiple A records.

> **Aggregation Note (2026-01-30):** This analysis demonstrates why line-level filtering is
> insufficient for operational coherence. C885 establishes that A FOLIO (114 units, 81% PP
> coverage) is the operational unit for A-B vocabulary correspondence.

## Provenance

- Script: `phases/A_RECORD_B_FILTERING/scripts/instance_trace_analysis.py` (Test 10)
- Extends: C690 (legality map), C683 (role composition)
