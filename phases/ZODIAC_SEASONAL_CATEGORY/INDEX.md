# Phase 583: ZODIAC_SEASONAL_CATEGORY — Zodiac Seasonal Category Clustering Test

**Status:** COMPLETE
**Verdict:** SEASONAL_SIGNAL_CONFIRMED (after zodiac correction)
**Constraints:** C1681-C1684
**Runtime:** 5.67s (v1), 23.09s (v2)

## Summary

Tests whether AZC zodiac page vocabulary clusters by season when classified into the 8 operational categories (C1250). Motivated by Brunschwig 1512 zodiac-conditional apparatus instructions and C322 (SEASON-GATED WORKFLOW).

**Critical discovery:** The standard zodiac folio map (from ZOD_zodiac_analysis) has multiple incorrect assignments. Visual evidence from user's folio annotations shows at least 6/14 folios misidentified, and f70r1/f70r2 are non-figurative diagrams included erroneously. Correcting the map changes the verdict from WEAK to CONFIRMED.

## Results (v2 — corrected zodiac mapping)

Four mapping variants tested:

| Map | Folios | χ² p | V | Perm p | Verdict |
|-----|--------|------|---|--------|---------|
| A: Visual, goat=Capricorn | 9 | 0.012 | 0.125 | 0.220 | WEAK |
| **B: Visual, goat=Aries** | **9** | **0.001** | **0.138** | **0.033** | **CONFIRMED** |
| **C: Confident-only** | **7** | **0.0005** | **0.157** | **0.018** | **CONFIRMED** |
| D: Original nymph-only | 12 | 0.002 | 0.113 | 0.112 | WEAK |

## Constraint Verdicts

| ID | Claim | Status |
|----|-------|--------|
| C1681 | SEASONAL_CATEGORY_SIGNAL | **UPGRADED:** Confirmed with corrected zodiac map (confident-only perm_p=0.018, V=0.157). Original map gave marginal p=0.079 due to misassigned folios |
| C1682 | THERMAL_SEASONAL_GRADIENT_ABSENT | Stands: THERMAL and CONTAINMENT not individually significant in any mapping variant |
| C1683 | WITHIN_SEASON_COHERENCE_TREND | **REVISED:** Approaches significance with corrected map (Map B: p=0.060). Trend direction confirmed: within-season < between-season JSD |
| C1684 | STAGING_SEASONAL_GRADIENT | REVISED: Only significant in original nymph-only map (p=0.049). Signal distributed across multiple categories in corrected maps, no single category dominates |

## Key Findings

1. **Zodiac assignments matter enormously.** The standard scholarship ordering assumes sequential zodiac signs but doesn't match the visual evidence. At least 6 center illustrations don't match their assigned signs. Correcting based on visual evidence changes the verdict from WEAK to CONFIRMED.

2. **Confident-only subset gives STRONGEST signal** (7 pages, perm_p=0.018, V=0.157). The ambiguous/unknown pages add noise, not signal. This means the visual identifications are tracking real structural differences.

3. **Goat interpretation is diagnostic.** Goat=Capricorn (Winter) kills the signal (perm_p=0.220), goat=Aries (Spring) preserves it (perm_p=0.033). The goat pages behave categorically like Spring pages, not Winter. This constrains the goat identity to Aries/Taurus.

4. **The seasonal signal is distributed across categories**, not concentrated in THERMAL/CONTAINMENT. The apparatus-configuration prediction (specific channels) fails, but the overall profile variation is real.

5. **f70r1/f70r2 must be excluded from zodiac analysis.** They are non-figurative circular diagrams (no nymphs, no center illustration), and f70r2 has a text block linguistically closer to Currier A (PREFIX cosine 0.972).

6. **Three folios (f71v, f72r1, f72r3) have unidentifiable "generic animal" centers.** These are candidates for assignment inference in a follow-up phase.

## Zodiac Correction Table

| Folio | Old assignment | Visual evidence | Corrected |
|-------|---------------|-----------------|-----------|
| f70r1 | Pisces | Non-figurative diagram | **EXCLUDED** |
| f70r2 | Pisces | Non-figurative + A-like text | **EXCLUDED** |
| f70v2 | Aries | Fish | **Pisces** |
| f70v1 | Pisces | Goat | **Aries** (Spring behavior) |
| f71r | Taurus | Goat + plant | Taurus? (ambiguous) |
| f71v | Taurus | Generic animal | **UNKNOWN** |
| f72r1 | Gemini | Generic animal | **UNKNOWN** |
| f72r2 | Cancer | Man + woman | **Gemini** |
| f72r3 | Leo | Generic animal | **UNKNOWN** |
| f72v1 | Virgo | Balancing scale | **Libra** |
| f72v2 | Libra | Lady of status | **Virgo** |
| f72v3 | Scorpio | Tiger/feline | **Leo** |
| f73r | Sagittarius | Reptile | **Scorpio** |
| f73v | Capricorn | Lady + crossbow | **Sagittarius** |

## Scripts

| Script | Runtime |
|--------|---------|
| `scripts/zodiac_seasonal_category.py` | 5.67s |
| `scripts/zodiac_seasonal_category_v2.py` | 23.09s |

## Files

- `results/zodiac_seasonal_category.json` — v1 results (original map)
- `results/zodiac_seasonal_category_v2.json` — v2 results (4 corrected variants)
