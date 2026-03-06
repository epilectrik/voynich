# C1464: k-IMMUNE THERMAL_WORK Onset Concentration

**Tier:** 2
**Scope:** B, MIDDLE, atom, k-HEAD, IMMUNE, line, position, zone, THERMAL_WORK, C103, C1446, C1428, C1463
**Phase:** 528 (LINE_ZONE_FRAME_HAZARD)
**Date:** 2026-03-05

## Claim

k-HEAD (IMMUNE) tokens peak sharply at Q1 (1.311x enrichment), the entrance to the THERMAL_WORK zone, and are depleted at both SPECIFICATION (Q0: 0.826x) and CLOSURE (Q4: 0.786x). 63.1% of all k-HEAD tokens fall within Q1-Q3, a 1.165x enrichment over the work zone baseline. Mean position: IMMUNE 0.484 vs non-IMMUNE 0.503. The Q1 peak (not Q2 or Q3) indicates k-HEAD is concentrated at the ONSET of thermal work, consistent with C103 (k = ENERGY_MODULATOR) and C1238 (kernel initiation order: e first, then k).

## Evidence

### k-HEAD Quintile Distribution

| Quintile | k-HEAD N | Enrichment |
|----------|----------|------------|
| Q0 | 557 | 0.826x |
| **Q1** | **737** | **1.311x** |
| Q2 | 618 | 1.113x |
| Q3 | 601 | 1.069x |
| Q4 | 587 | 0.786x |

### Zone Concentration

| Zone | k-HEAD % | Enrichment |
|------|----------|------------|
| SPECIFICATION (Q0) | 18.0% | 0.826x |
| THERMAL_WORK (Q1-Q3) | 63.1% | 1.165x |
| CLOSURE (Q4) | 18.9% | 0.786x |

### Positional Summary

| Metric | Value |
|--------|-------|
| Total k-HEAD tokens | 3,100 (13.4% of corpus) |
| Mean position (IMMUNE) | 0.484 |
| Mean position (non-IMMUNE) | 0.503 |
| Peak quintile | Q1 (1.311x) |
| Work zone enrichment | 1.165x |

## Interpretation

k-HEAD is the energy input operator (C103: ENERGY_MODULATOR). Its concentration at Q1 -- the start of the thermal work zone, not the middle or end -- means energy is applied at the beginning of the work phase. This is physically natural: in distillation, you fire the heat source first, then monitor and adjust. The Q1 peak also follows the e-first pattern from C1238: cooling/stability operations (e-HEAD, ZERO frames) deploy at Q0 (SPECIFICATION), then energy input (k-HEAD) enters at Q1 to begin the thermal processing cycle. The CLOSURE depletion (0.786x) confirms that by the time the line reaches closure, energy input has ended and the system is transitioning to state-change operations.

## Falsification Criteria

1. If k-HEAD Q1 enrichment drops below 1.15x
2. If k-HEAD shows flat distribution across quintiles (no peak)
3. If k-HEAD work zone enrichment drops below 1.05x

## Method

- 3,100 k-HEAD tokens identified from 23,090 Currier B corpus
- Fractional line position computed per token
- Quintile assignment: Q0=[0,0.2), Q1=[0.2,0.4), etc.
- Enrichment = observed fraction / expected fraction per quintile
- Zone grouping: SPECIFICATION=Q0, THERMAL_WORK=Q1-Q3, CLOSURE=Q4

**Script:** `phases/LINE_ZONE_FRAME_HAZARD/scripts/line_zone_frame_hazard.py`
**Results:** `phases/LINE_ZONE_FRAME_HAZARD/results/line_zone_frame_hazard.json`

## Dependencies

- C103 (k = ENERGY_MODULATOR)
- C1238 (kernel initiation order: e before k)
- C1428 (THERMAL peak-then-decline positional gradient)
- C1446 (k-HEAD complete hazard immunity)
- C1463 (zone-hazard routing at line level)
