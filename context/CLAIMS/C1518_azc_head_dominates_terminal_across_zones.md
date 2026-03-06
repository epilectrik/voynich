# C1518: AZC HEAD Differentiation Dominates TERMINAL Across Zones

**Tier:** 2
**Scope:** AZC, zone, atom, HEAD, TERMINAL, JSD, dominance, slot
**Phase:** AZC_ZONE_ATOMIZATION (Phase 541)

## Claim

AZC zones differentiate primarily through HEAD domain selection, not TERMINAL closure. Mean pairwise HEAD JSD between major zones (R/C/S/P) is 0.0254, while mean TERMINAL JSD is 0.0049 -- HEAD is 5.2x more discriminating. The most divergent zone pair (S-P) has HEAD JSD=0.0586 but TERMINAL JSD=0.0081 (7.2x ratio). TERMINAL profiles are remarkably uniform across zones: bare ~50%, y ~14%, l ~13%, r ~10%, n ~5%, h ~4%, m ~2%. This means zones specify WHAT DOMAIN their vocabulary occupies (through HEAD) while sharing HOW instructions close (through TERMINAL). Parallels C1501 at zone level: bridge MIDDLEs have constrained terminal ecology, and AZC zones inherit this terminal stability.

## Evidence

- Pairwise HEAD JSD vs TERMINAL JSD:
  - R-C: HEAD=0.0091, TERM=0.0029 (3.1x)
  - R-S: HEAD=0.0296, TERM=0.0033 (9.0x)
  - R-P: HEAD=0.0180, TERM=0.0082 (2.2x)
  - C-S: HEAD=0.0163, TERM=0.0014 (11.6x)
  - C-P: HEAD=0.0209, TERM=0.0054 (3.9x)
  - S-P: HEAD=0.0586, TERM=0.0081 (7.2x)
- Mean HEAD JSD: 0.0254, Mean TERMINAL JSD: 0.0049, ratio 5.2x
- TERMINAL profile remarkably stable: bare 48-52%, y 12-22%, l 12-14%, r 7-10%, n 4-6%, h 2-6%, m 1-4%
- TERMINAL tier proportions also stable: LOCKED 10-13%, CHANNELED 31-36%, DIFFUSE 4-6%, bare 48-52%

## Relationship to Prior Constraints

- **Extends C1516**: HEAD differentiation is the primary zone-discrimination mechanism
- **Parallels C1501**: Bridge terminal tier outlier (most constrained terminal ecology) -- AZC zones inherit terminal stability from the bridge backbone
- **Connects C1487**: Three-tier terminal taxonomy (LOCKED/CHANNELED/DIFFUSE) shows the same proportions across all AZC zones
- **Contrasts C1507**: In bridge MIDDLEs, HEAD redistributes across A/B (JSD=0.077) while TERMINAL stays stable (JSD=0.014); AZC zones show the same pattern (HEAD varies, TERMINAL stable)
- **Extends C1499**: Shared substrate is zone-independent at TERMINAL level

## Source

`phases/AZC_ZONE_ATOMIZATION/results/azc_zone_atomization.json` (T3, T8)
