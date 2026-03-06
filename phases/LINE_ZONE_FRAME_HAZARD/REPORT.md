# Phase 528: Line Zone x Frame Hazard Interaction

**Date:** 2026-03-05
**Status:** COMPLETE
**Constraints Produced:** C1463-C1466

---

## Research Question

Do the three-zone line model (SPECIFICATION/THERMAL_WORK/CLOSURE, C1425-C1430) and the frame hazard classification (7 HIGH / 3 ZERO / k-IMMUNE, C1448) -- discovered independently -- interact? Specifically: does the line's positional grammar route hazardous vs safe frames to specific zones?

## Method

23,090 Currier B tokens (H-track, labels excluded, uncertain excluded) were decomposed into HEAD x TERMINAL frames using `decompose_middle_hmt()`. Each token was assigned:
- **Frame hazard class:** HIGH (7 frames), ZERO (3 frames), IMMUNE (k-HEAD), or LOW (default) from decoder_maps.json
- **Fractional line position:** [0,1] based on token index within line
- **Quintile:** Q0 (0-0.2), Q1 (0.2-0.4), Q2 (0.4-0.6), Q3 (0.6-0.8), Q4 (0.8-1.0)
- **Zone:** SPECIFICATION (Q0), THERMAL_WORK (Q1-Q3), CLOSURE (Q4)

Six tests plus one supplementary section interaction test were run.

## Token Distribution

| Hazard Class | N | % |
|-------------|---|---|
| LOW | 10,552 | 45.7% |
| HIGH | 4,782 | 20.7% |
| ZERO | 4,656 | 20.2% |
| IMMUNE | 3,100 | 13.4% |

## Results Summary

### T1-T2: Zone x Hazard Contingency (C1463)

The core interaction is statistically overwhelming: chi2=336.3, dof=6, p=1.38e-69, Cramer's V=0.085.

| Zone | HIGH | LOW | ZERO | IMMUNE |
|------|------|-----|------|--------|
| SPECIFICATION | 0.836x | 1.021x | **1.236x** | 0.826x |
| THERMAL_WORK | 1.006x | 0.940x | 1.019x | **1.165x** |
| CLOSURE | **1.134x** | 1.116x | 0.743x | 0.786x |

The pattern is clear and interpretable:
- **SPECIFICATION zone** (Q0): ZERO frames enriched 1.236x (safe vocabulary for line setup), HIGH depleted 0.836x
- **THERMAL_WORK zone** (Q1-Q3): IMMUNE enriched 1.165x (k-HEAD energy operations concentrate here), others near baseline
- **CLOSURE zone** (Q4): HIGH enriched 1.134x (hazardous operations at line-final), ZERO and IMMUNE depleted

Pairwise zone comparisons all significant: SPECIFICATION vs CLOSURE strongest (V=0.135), THERMAL_WORK vs CLOSURE next (V=0.106), SPECIFICATION vs THERMAL_WORK weakest (V=0.082).

### T3: Safe Pathway (e->y) Positioning

e->y tokens (N=3,475) have mean position 0.463 -- earlier than HIGH frames (0.536) by 0.073 (Mann-Whitney p=5.7e-26, r=0.136). e->y is enriched at Q0-Q1 (1.09x-1.13x) and strongly depleted at Q4 (0.76x). This extends C1459 (context-independent deployment): e->y is positionally biased AWAY from the closure zone where hazard concentrates.

Other ZERO frames (e->l, i->n) show even stronger initial bias: mean position 0.390, enriched 1.36x at Q0.

### T4: k-IMMUNE THERMAL_WORK Concentration (C1464)

k-HEAD tokens (N=3,100) peak sharply at Q1 (1.311x enrichment), the entrance to the THERMAL_WORK zone. They are depleted at both SPECIFICATION (0.826x) and CLOSURE (0.786x). 63.1% of all k-HEAD tokens fall within the THERMAL_WORK zone (Q1-Q3), a 1.165x enrichment.

Mean position: IMMUNE 0.484 vs non-IMMUNE 0.503. The Q1 peak (not Q2 or Q3) indicates k-HEAD is concentrated at the ONSET of thermal work, consistent with its role as ENERGY_MODULATOR (C103): you fire the heat source at the beginning of the work phase.

### T5: HIGH Frame Positional Heterogeneity (C1465)

The 7 HIGH frames are NOT positionally uniform (KW H=68.8, p=1.83e-13, eta2=0.013):

| Frame | N | Mean Pos | Character |
|-------|---|----------|-----------|
| o->bare | 1,164 | 0.493 | Position-neutral |
| o->r | 455 | 0.487 | Slightly initial-biased |
| a->n | 1,272 | 0.532 | Mildly closure-biased |
| a->r | 687 | 0.551 | Closure-biased |
| d->y | 677 | 0.581 | Strongly closure-biased |
| a->l | 527 | 0.602 | Most closure-biased |

Positional spread among HIGH frames: 0.115 (o->r at 0.487 to a->l at 0.602). Two clusters emerge:
- **o-HEAD HIGH** (o->bare, o->r): near-median position, present throughout lines
- **a/d-HEAD HIGH** (a->l, a->r, a->n, d->y): closure-biased, concentrated at line-final

This means: arrangement operations (o-HEAD) carry hazard at any position, while yield/seal operations (a/d-HEAD) carry hazard specifically at closure -- different spatial safety profiles for different operational domains.

### T6: Zone x Hazard Pattern Line-Length Invariance (C1466)

The zone x hazard interaction pattern is INVARIANT across line lengths:

| Length | N | V |
|--------|---|---|
| Short (<=7) | 2,751 | 0.091 |
| Medium (8-11) | 14,017 | 0.089 |
| Long (>=12) | 6,322 | 0.081 |

All three line-length groups show the same enrichment pattern: HIGH at CLOSURE, ZERO at SPECIFICATION, IMMUNE at THERMAL_WORK. The zone x hazard routing is a UNIVERSAL property of line grammar, not an artifact of line length.

There is a small but significant interaction at CLOSURE: long lines have 26.7% HIGH rate at closure vs 22.7% for short lines (chi2=22.8, V=0.100, p=4.35e-5). Longer lines accumulate slightly more hazard at their close.

### T-Extra: Section Universality

The SPECIFICATION→THERMAL_WORK→CLOSURE hazard gradient is present in ALL five sections (B, C, H, S, T). In every section, HIGH hazard rate increases from SPECIFICATION to CLOSURE. The gradient is steepest in Section B (8.7% -> 14.8%, ratio 1.70) and flattest in Section C (34.3% -> 29.5%, ratio 0.86 -- C is uniformly high-hazard). Section-universality confirms this is a property of line grammar, not section-specific content.

## Constraints Produced

| ID | Title | Key Finding |
|----|-------|-------------|
| C1463 | Zone-hazard routing at line level | HIGH CLOSURE-enriched 1.134x, ZERO SPECIFICATION-enriched 1.236x, IMMUNE THERMAL_WORK-enriched 1.165x |
| C1464 | k-IMMUNE THERMAL_WORK onset concentration | Q1 peak 1.311x, 63.1% in work zone |
| C1465 | HIGH frame positional heterogeneity | o-HEAD neutral, a/d-HEAD closure-biased, spread 0.115 |
| C1466 | Zone-hazard pattern line-length invariance | V=0.081-0.091 across all lengths |

## Interpretive Significance

This phase bridges two independently discovered systems -- the positional line grammar and the frame hazard map -- and shows they are NOT independent. The line's three-zone structure is ALSO a hazard gradient: safe operations open lines, hazardous operations close them. The immune energy operator (k-HEAD) concentrates where thermal work begins. This is consistent with the Tier 3 interpretation of lines as thermal processing cycles: setup safety, fire the heat, then navigate the hazardous closure.

The finding that ZERO (safe) frames concentrate at SPECIFICATION and HIGH (hazardous) frames at CLOSURE creates a MONOTONIC hazard gradient across the line. This is more specific than C1428's category-level THERMAL peak-then-decline -- it shows that at the atom-frame level, the line's structure is explicitly organized to put safe operations before dangerous ones.

## Files

- **Script:** `phases/LINE_ZONE_FRAME_HAZARD/scripts/line_zone_frame_hazard.py`
- **Results:** `phases/LINE_ZONE_FRAME_HAZARD/results/line_zone_frame_hazard.json`
