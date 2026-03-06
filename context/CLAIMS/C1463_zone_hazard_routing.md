# C1463: Zone-Hazard Routing at Line Level

**Tier:** 2
**Scope:** B, line, position, zone, hazard, frame, routing, C1425, C1426, C1427, C1428, C1448
**Phase:** 528 (LINE_ZONE_FRAME_HAZARD)
**Date:** 2026-03-05

## Claim

The three-zone line model (SPECIFICATION/THERMAL_WORK/CLOSURE) and frame hazard classification (HIGH/LOW/ZERO/IMMUNE) are NOT independent -- they interact with a structured routing pattern. ZERO-hazard frames (e->y, e->l, i->n) are enriched 1.236x at SPECIFICATION (Q0), IMMUNE frames (k-HEAD) are enriched 1.165x at THERMAL_WORK (Q1-Q3), and HIGH-hazard frames are enriched 1.134x at CLOSURE (Q4). Chi-squared=336.3, dof=6, p=1.38e-69, Cramer's V=0.085. All pairwise zone comparisons significant (V=0.082-0.135). The line creates a monotonic hazard gradient: safe operations open, energy operations work, hazardous operations close.

## Evidence

### Zone x Hazard Class Enrichment Table

| Zone | N | HIGH | LOW | ZERO | IMMUNE |
|------|---|------|-----|------|--------|
| SPECIFICATION (Q0) | 5,022 | 0.836x | 1.021x | **1.236x** | 0.826x |
| THERMAL_WORK (Q1-Q3) | 12,507 | 1.006x | 0.940x | 1.019x | **1.165x** |
| CLOSURE (Q4) | 5,561 | **1.134x** | 1.116x | 0.743x | 0.786x |

### Pairwise Zone Comparisons

| Comparison | chi2 | p | V |
|-----------|------|---|---|
| SPECIFICATION vs CLOSURE | 192.4 | 1.86e-41 | 0.135 |
| THERMAL_WORK vs CLOSURE | 201.1 | 2.40e-43 | 0.106 |
| SPECIFICATION vs THERMAL_WORK | 117.0 | 3.40e-25 | 0.082 |

### Mean Fractional Position by Hazard Class

| Class | Mean | N |
|-------|------|---|
| HIGH | 0.536 | 4,782 |
| LOW | 0.513 | 10,552 |
| IMMUNE | 0.484 | 3,100 |
| ZERO | 0.444 | 4,656 |

Kruskal-Wallis: H=225.0, p=1.71e-48, eta2=0.010.

### e->y CLOSURE depletion

The primary safe pathway e->y (3,475 tokens) is specifically depleted at CLOSURE: Q4 enrichment = 0.762x. e->y concentrates at Q0-Q1 (1.09x-1.13x). This extends C1459 (context-independent deployment) with spatial specificity: e->y is deployed everywhere EXCEPT where hazard concentrates.

## Interpretation

Lines are not just operationally zoned (C1425-C1430) -- they are HAZARD-zoned. The SPECIFICATION opener deploys categorically safe vocabulary. The THERMAL_WORK phase deploys energy operations that are immune to hazard by construction (k-HEAD). The CLOSURE phase is where hazardous a/d-HEAD operations concentrate. This creates a built-in safety gradient: by the time the operator reaches hazardous operations, the line has already established its context with safe vocabulary. The grammar puts danger last, when the operational context is fully specified.

## Falsification Criteria

1. If ZERO enrichment at SPECIFICATION drops below 1.1x
2. If HIGH enrichment at CLOSURE drops below 1.05x
3. If IMMUNE enrichment at THERMAL_WORK drops below 1.05x
4. If pairwise zone V drops below 0.05 for any pair

## Method

- 23,090 Currier B tokens (H-track, labels/uncertain excluded)
- Frame hazard class from decoder_maps.json (HIGH: 7 frames, ZERO: 3 frames, IMMUNE: k-HEAD, LOW: default)
- Fractional line position -> quintile -> zone mapping
- Chi-squared contingency tests with Cramer's V
- Mann-Whitney U for continuous position comparison

**Script:** `phases/LINE_ZONE_FRAME_HAZARD/scripts/line_zone_frame_hazard.py`
**Results:** `phases/LINE_ZONE_FRAME_HAZARD/results/line_zone_frame_hazard.json`

## Dependencies

- C1425-C1430 (three-zone line model: SPECIFICATION/THERMAL_WORK/CLOSURE)
- C1448 (HEAD x TERM frame hazard map)
- C1446 (k-HEAD complete hazard immunity)
- C1459 (e->y context-independent deployment -- extended with spatial specificity)
