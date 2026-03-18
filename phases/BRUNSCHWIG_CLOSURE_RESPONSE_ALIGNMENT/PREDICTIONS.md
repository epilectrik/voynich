# Phase 600: BRUNSCHWIG_CLOSURE_RESPONSE_ALIGNMENT — Pre-Registration

**Date:** 2026-03-17
**Status:** LOCKED — hash this file before loading any Voynich response data

## Historical Predictor Axes

### H1: CONTAINMENT_BURDEN (per 100 words + boosts)

**Strict lexicon:** `sealed`, `luted`, `lutum`, `luto sapientiae`, `hermetically`, `stopped and sealed`, `pelican`, `circulatorium`

**Broad lexicon:** `seal`, `lut`, `stopp`, `wax`, `clay`, `dough`, `paste`, `hermet`, `close well`, `close tight`, `cork`, `let it stand`, `let it rest`, `let it sit`, `leave it`, `putref`, `digest`, `infuse`

**Boosts:** vessel pelican/circulatorium +2, method circulation/horse_dung +1

### H2: OPEN_INTERVENTION (per 100 words + boosts)

**Strict lexicon:** `pour off`, `pour out`, `pour back`, `pour into`, `transfer`, `remove the`, `take off the`, `open the`, `opened the`

**Broad lexicon:** `stir`, `stirred`, `stirring`, `add more`, `replenish`, `shake`, `check`, `turn`, `look at`, `observe` + all strict terms

**Boosts:** method open_fire/ashes +1

### H3: RECYCLE_COMPLEXITY

**Formula:** max(distill_references, named_distillations * 2) from recipe JSON

### Method-Class Assignment

Same as Phase 599:
- GENTLE_SUSTAINED: balneum_mariae, horse_dung, sun
- OPEN_CYCLE_ELEVATED: open_fire, ashes, gentle_fire
- SEALED_RECIRCULATION: circulation
- PRECISION_CONTROLLED: sand_bath
- Assignment rule: dominant method; multi-class → rarest method

## Cell-to-Method-Class Mapping (Frozen)

| Cell | Method-Class | Provenance |
|------|-------------|------------|
| S:R1 | GENTLE_SUSTAINED | C494 (R1 = continuous sustained) |
| S:R3 | OPEN_CYCLE_ELEVATED | C1247 (aii 41x enriched in R3) |
| H:R2 | SEALED_RECIRCULATION | C1248 (60% SEALED_VESSEL dominant) |
| H:R4 | PRECISION_CONTROLLED | C494 (R4 = precision axis) |
| H:R3 | OPEN_CYCLE_ELEVATED | Same as S:R3 |

## Voynich Response Vector (7D)

[mean_CTS, strong_close_fraction, DYE_advantage, mean_dv_magnitude, mean_ACS, ey_rate, ii_rate]

## Test Predictions

### P1: Mantel Geometry Concordance
- Predicted 3D (H1_strict, H2_strict, H3) distance matrix vs observed 7D response distance matrix
- Threshold: r > 0.30 AND p < 0.05

### P2: Stars R1 vs R3 Directional (4 axes)
1. ey_rate: R1 > R3
2. ii_rate: R1 < R3
3. DYE_advantage: R1 > R3
4. strong_close_fraction: R1 > R3
- Threshold: >=3/4 concordant AND combined p < 0.05

### P3: Rank Concordance (3 pairs)
1. CONTAINMENT_RANK concordant with ey_rate rank (tau > 0)
2. INTERVENTION_RANK concordant with ii_rate rank (inverted; tau > 0)
3. CONTAINMENT_RANK concordant with mean_CTS rank (tau > 0)
- Threshold: >=2/3 concordant AND >=1 tau p < 0.10

### P4: Herbal R2 vs R4 Directional (3 axes)
1. ey_rate: H:R2 > H:R4
2. ii_rate: H:R2 < H:R4
3. DYE_advantage: H:R2 > H:R4
- Threshold: >=2/3 concordant AND >=1 p < 0.10

## Decision Logic

4/4=CLOSURE_RESPONSE_ALIGNED, 3/4=CLOSURE_RESPONSE_PARTIAL, 2/4=WEAK_CLOSURE_SIGNAL, <=1/4=CLOSURE_RESPONSE_NOT_CONFIRMED

## Annotation Quality Gates

- H1 strict-broad Spearman > 0.5 (else ANNOTATION_UNSTABLE)
- H2 strict-broad Spearman > 0.5 (else ANNOTATION_UNSTABLE)
