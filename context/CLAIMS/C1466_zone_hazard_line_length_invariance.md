# C1466: Zone-Hazard Pattern Line-Length Invariance

**Tier:** 2
**Scope:** B, line, position, zone, hazard, frame, length, invariance, universality, C1425, C1463
**Phase:** 528 (LINE_ZONE_FRAME_HAZARD)
**Date:** 2026-03-05

## Claim

The zone x hazard routing pattern (C1463) is INVARIANT across line lengths. Short lines (<=7 tokens, N=2,751), medium lines (8-11, N=14,017), and long lines (>=12, N=6,322) all show the same enrichment structure: HIGH at CLOSURE, ZERO at SPECIFICATION, IMMUNE at THERMAL_WORK. Cramer's V ranges from 0.081 (long) to 0.091 (short) with no systematic trend. The hazard gradient is a universal property of line grammar, not an artifact of line length.

## Evidence

### Zone x Hazard V by Line Length

| Length | N | V | p |
|--------|---|---|---|
| Short (<=7) | 2,751 | 0.091 | 3.11e-08 |
| Medium (8-11) | 14,017 | 0.089 | 9.52e-45 |
| Long (>=12) | 6,322 | 0.081 | 5.96e-16 |

### Enrichment Pattern Consistency

| Zone | Feature | Short | Medium | Long |
|------|---------|-------|--------|------|
| SPEC | ZERO enrich | 1.243x | 1.262x | 1.178x |
| SPEC | HIGH deplete | 0.708x | 0.842x | 0.857x |
| WORK | IMMUNE enrich | 1.182x | 1.160x | 1.158x |
| CLOSURE | HIGH enrich | 1.160x | 1.141x | 1.112x |
| CLOSURE | ZERO deplete | 0.873x | 0.725x | 0.701x |

### Minor Length Interaction at CLOSURE

| Metric | Short | Long | Delta |
|--------|-------|------|-------|
| HIGH rate at CLOSURE | 22.7% | 26.7% | +4.0pp |
| Chi-squared (short vs long closure) | 22.8 | -- | -- |
| p-value | 4.35e-05 | -- | -- |
| V | 0.100 | -- | -- |

Longer lines accumulate slightly more hazard at closure (+4.0pp), but this is a small quantitative modulation on top of a structurally invariant pattern.

## Interpretation

The zone-hazard routing is built into line grammar at a level that does not depend on how many tokens a line contains. Whether a line has 5 tokens or 15, the same proportional allocation of safe/hazardous/immune operations to specification/work/closure zones is maintained. This universality extends C1425 (line length unimodal) and C1363 (gradient steepness universal) to the frame hazard level. The minor length interaction at closure (+4pp) suggests longer lines have slightly more room for hazardous closure operations, but the grammar's fundamental safety architecture -- safe first, hazardous last -- is invariant.

## Falsification Criteria

1. If V for any length group drops below 0.05 (pattern disappears)
2. If the enrichment direction reverses for any length group (e.g., HIGH at SPECIFICATION instead of CLOSURE)
3. If V varies by more than 2x across length groups (e.g., V=0.15 vs 0.04)

## Method

- 23,090 Currier B tokens partitioned by line length: short (<=7), medium (8-11), long (>=12)
- Zone x hazard contingency table computed independently for each length group
- Cramer's V computed for each table
- Closure hazard rate compared between short and long via chi-squared

**Script:** `phases/LINE_ZONE_FRAME_HAZARD/scripts/line_zone_frame_hazard.py`
**Results:** `phases/LINE_ZONE_FRAME_HAZARD/results/line_zone_frame_hazard.json`

## Dependencies

- C1425 (line length unimodal distribution)
- C1363 (gradient steepness universal)
- C1463 (zone-hazard routing at line level)
