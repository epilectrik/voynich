# C1276: AZC Sections Converge on A Pharma Atom Profile

**Tier:** 2
**Scope:** AZC, A
**Phase:** AZC_CATEGORY_SCATTERSHOT (Phase 453)
**Date:** 2026-02-24

## Statement

All AZC sections (A, C, Z) show strongest atom-profile correspondence with Currier A's Pharma (P) section. AZC-A to A-P: r=0.920, JSD=0.009. AZC-C to A-P: r=0.916, JSD=0.011. AZC-Z to A-P: r=0.928, JSD=0.010. No diverse mapping exists -- all AZC sections converge on the same A-section atom signature rather than each matching a different A section. AZC internal JSD between sections (mean 0.013) is smaller than most cross-system JSD values.

## Architecture

- **AZC draws from a Pharma-like atom pool.** Regardless of AZC section (A, C, or Zodiac), the character-level composition matches A's Pharma section most closely. This is consistent with C1271 (zone atom uniformity) -- AZC is atom-homogeneous internally.
- **No section-to-section correspondence.** Unlike a mapping where AZC-Z matches A-H and AZC-C matches A-T, all converge on P. This means AZC section labels do not reflect A section origin at the atom level.
- **Pharma affinity.** A's Pharma section is STABILITY/STRUCTURAL-enriched (C1266). AZC's convergence on this profile suggests AZC vocabulary draws disproportionately from the stability/structural atom pool, consistent with its classification/lookup function.

## Key Findings

| AZC Section | Closest A Section | r | JSD |
|-------------|-------------------|---|-----|
| A | P (Pharma) | 0.920 | 0.009 |
| C | P (Pharma) | 0.916 | 0.011 |
| Z | P (Pharma) | 0.928 | 0.010 |
| H (small, n=82) | P (Pharma) | 0.657 | 0.031 |

| Metric | Value |
|--------|-------|
| AZC internal mean JSD | 0.013 |
| Diverse mapping | No |

## Provenance

- Extends C1266 (A section atom differentiation) into AZC cross-comparison
- Complements C1271 (AZC zone atom uniformity) -- AZC is atom-uniform internally
- Tests C946 (MIDDLE-level section uniformity) at cross-system atom resolution
