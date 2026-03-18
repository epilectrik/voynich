# Phase 599: Pre-Registered Predictions
# APPARATUS_BUNDLE_ALIGNMENT
# Date: 2026-03-17
# Hash this file BEFORE loading any Voynich apparatus profile data

## Method-Bundle Classes

| Bundle Class | Methods | Physical Character |
|---|---|---|
| GENTLE_SUSTAINED | balneum_mariae, horse_dung, sun | Gentle ambient/water-bath heat, long duration, passive |
| OPEN_CYCLE_ELEVATED | open_fire, ashes, gentle_fire | Direct or semi-direct heat, active tending, volatile drive-off |
| SEALED_RECIRCULATION | circulation | Sealed vessel, recirculating condensate, precise temperature |
| PRECISION_CONTROLLED | sand_bath | Even controlled heat through intermediary medium |

## Admissible Bridge Family

### Certain Profile Mappings (always included)
- GENTLE_SUSTAINED -> SUSTAINED_HEAT
- OPEN_CYCLE_ELEVATED -> DIRECT_FIRE
- SEALED_RECIRCULATION -> SEALED_VESSEL
- PRECISION_CONTROLLED -> PRECISION

### Admissible Alternate Mappings (included or excluded per variant)
- GENTLE_SUSTAINED alternate: SEALED_VESSEL (balneum uses sealed bath)
- OPEN_CYCLE_ELEVATED alternate: DISTILLATION (base operation for all fire methods)
- SEALED_RECIRCULATION alternate: PRECISION (circulation requires control)
- PRECISION_CONTROLLED alternate: SUSTAINED_HEAT (sand provides even sustained heat)

Note: OPEN_CYCLE_ELEVATED alternate maps to DISTILLATION which is removed in secondary profile analysis. When this alternate is included, its weight redistributes to remaining secondary profiles proportionally.

### Excluded Mappings (never included)
- GENTLE_SUSTAINED excludes DIRECT_FIRE
- OPEN_CYCLE_ELEVATED excludes SEALED_VESSEL
- SEALED_RECIRCULATION excludes DIRECT_FIRE
- PRECISION_CONTROLLED excludes DIRECT_FIRE

### Weight Family
- Primary (certain) weight: {0.55, 0.60, 0.65, 0.70, 0.75, 0.80}
- Secondary (alternate) weight: 1 - primary
- Sole-profile bundles (no alternate included): weight = 1.0
- 3 bundles have on/off alternates = 2^3 = 8 configurations (PRECISION_CONTROLLED always has alternate because it only has 14 recipes — too few for sole-profile to be stable)

Actually: PRECISION_CONTROLLED's alternate is optional too.
- 4 bundles have on/off alternates = 2^4 = 16 configurations
- But OPEN_CYCLE_ELEVATED's alternate maps to DISTILLATION (removed in secondary space), so it only matters for raw-profile analysis, not secondary. Include it anyway for completeness.
- Total: 6 weight levels x 16 alternate configurations = 96 bridge variants
- For tractability, use: 6 weight levels x 8 alternate configs (3 meaningful bundles: GS, SR, PC) = 48 variants

Correction: Only 3 alternates matter in secondary space (GS, SR, PC). OC's alternate is DISTILLATION which is removed. So 2^3 = 8 configs x 6 weights = 48 variants.

### Final Bridge Variant Count: 48

## Cell-to-Prototype Mapping

Based on frozen constraints (not fire-degree equivalence):

| Cell | Prototype | Justification |
|------|-----------|---------------|
| S:R1 | GENTLE_SUSTAINED | R1 = continuous sustained operation (C494, C1248: 97% DISTILLATION-dominant with highest SUSTAINED_HEAT among non-mixed REGIMEs) |
| S:R3 | OPEN_CYCLE_ELEVATED | R3 = batch/open-cycle (C1247: aii 41x enriched, open-cycle batch with unsealing) |
| H:R2 | SEALED_RECIRCULATION | R2 = 60% SEALED_VESSEL dominant corpus-wide (C1248) |
| H:R4 | PRECISION_CONTROLLED | R4 = precision axis (C494: REGIME_4 precision axis) |
| H:R3 | OPEN_CYCLE_ELEVATED | Same as S:R3, open-cycle batch |

## P1: Geometry Concordance Predictions

The predicted inter-cell distance matrix in 4D secondary space should correlate with the observed inter-cell distance matrix (Mantel test, Spearman).

Specific structural predictions:
- S:R1 and H:R2 should be CLOSE (both emphasize sustained/sealed secondary profiles)
- S:R3 and H:R3 should be CLOSE (both OPEN_CYCLE_ELEVATED)
- H:R4 should be DISTANT from S:R1 (precision vs sustained — strongest anti-correlation per C1248 DISTILLATION-PRECISION rho=-0.666)
- S:R3 and H:R4 should be MODERATELY distant (different apparatus types, both elevated)

## P2: Dominant Secondary Profile Predictions

| Cell | Predicted Dominant | Admissible Alternative |
|------|-------------------|----------------------|
| S:R1 | SUSTAINED_HEAT | SEALED_VESSEL (if GS alternate active) |
| S:R3 | DIRECT_FIRE | SUSTAINED_HEAT |
| H:R2 | SEALED_VESSEL | PRECISION (if SR alternate active) |
| H:R4 | PRECISION | SUSTAINED_HEAT (if PC alternate active) |
| H:R3 | DIRECT_FIRE | SUSTAINED_HEAT |

Margin rule: if observed top minus second < 0.02, cell is AMBIGUOUS.
Top-2 overlap: predicted top-2 should overlap with observed top-2.

## P3: Stars R1 vs R3 Direction Predictions

Pre-registered directions (sign of R1 mean minus R3 mean):

| Axis | Predicted Sign | Rationale |
|------|---------------|-----------|
| SEALED_VESSEL | R1 > R3 (+) | balneum = sealed water bath; R3 = open-cycle (unsealing) |
| SUSTAINED_HEAT | R1 > R3 (+) | horse_dung/sun/balneum = gentle sustained; R3 = elevated batch |
| DIRECT_FIRE | R1 < R3 (-) | open_fire/ashes cluster with elevated methods |
| PRECISION | EXPLORATORY | R3 is batch not precision; R4 is precision per C494 |

3 pre-registered axes. PRECISION reported but not scored.

## P4: Open-Cycle Signature Predictions

Open-cycle recipes (distill_references >= 2, n~207) vs single-pass (distill_references <= 1, n~224):

Predicted direction of (open-cycle minus single-pass) profile:
- SEALED_VESSEL: LOWER (open-cycle unseals; single-pass can stay sealed)
- DIRECT_FIRE: HIGHER (re-driving requires renewed heat application)
- SUSTAINED_HEAT: LOWER (repeated distillation is active, not sustained)
- PRECISION: NEUTRAL or HIGHER (repeated steps may require more precise control)

This direction vector should have POSITIVE cosine similarity with the observed (R3 minus R1) secondary profile direction, because R3 is the open-cycle REGIME (C1247).

## Thresholds

| Test | Metric | PASS Threshold |
|------|--------|----------------|
| P1 | Median Mantel r across bridge family | > 0.30, median p < 0.05, ≥75% variants positive |
| P2 | Top-1 match fraction (non-ambiguous) | ≥ 3 of non-ambiguous match, permutation p < 0.05 |
| P3 | Direction concordance (3 axes) | 3/3 concordant, permutation p < 0.05 |
| P4 | Cosine similarity (open-cycle direction vs R3-R1 direction) | > 0, permutation p < 0.05 |
