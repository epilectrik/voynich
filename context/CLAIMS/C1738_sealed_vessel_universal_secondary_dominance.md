# C1738: SEALED_VESSEL Universal Secondary Dominance

**Tier:** 2
**Phase:** APPARATUS_BUNDLE_ALIGNMENT (Phase 599)
**Scope:** B, apparatus, secondary profiles, SEALED_VESSEL

## Finding

Across the five viable section×REGIME cells, SEALED_VESSEL was the dominant observed secondary axis in every cell:

| Cell | SEALED_VESSEL | SUSTAINED_HEAT | PRECISION | DIRECT_FIRE |
|------|--------------|----------------|-----------|-------------|
| S:R1 | **0.609** | 0.285 | 0.045 | 0.061 |
| S:R3 | **0.516** | 0.344 | 0.103 | 0.038 |
| H:R2 | **0.488** | 0.277 | 0.171 | 0.064 |
| H:R4 | **0.374** | 0.353 | 0.236 | 0.037 |
| H:R3 | **0.328** | 0.314 | 0.264 | 0.094 |

This compressed the dominant-axis contrast expected under the tested historical bridge (Phase 599) and reduced the discriminability of apparatus-shape predictions at the cell-mean level.

## What This Shows and Does Not Show

**Shows:** SEALED_VESSEL vocabulary (ok, aii, ee, eey, eeol) is the largest secondary vocabulary component across all tested section×REGIME cells. A bridge that predicts different dominant secondary profiles for different cells will not find support at the cell-mean level.

**Does NOT show:** That the secondary profile space fails to differentiate by apparatus identity. Internal apparatus structure is validated by C1248, C1380, C1625-C1629, C1640, C1668, and C1722. Cells may differ meaningfully in relative proportions, geometry within the simplex, distributional shape, or covariance structure while sharing SEALED_VESSEL as top-1. A system can be globally sealed-biased and still meaningfully differentiate apparatus styles — sealedness may be a common background operating condition (containment/waiting is universal in distillation), not evidence that apparatus identity is absent.

## Significance

The SEALED_VESSEL markers may represent general-purpose containment/waiting operations rather than apparatus-specific sealed-vessel indicators. Their universality is consistent with a containment-response architecture where most control programs require waiting, monitoring, and containment regardless of the specific apparatus being controlled.

This constrains interpretations of C1248 apparatus profile labels: "SEALED_VESSEL" as a historical-apparatus label may be misleading for the secondary vocabulary's function, but the profile system itself (internal vocabulary differentiation, folio-specific response surfaces, manifold structure) remains valid.

## Key Metrics

- SEALED_VESSEL secondary fraction: 0.328–0.609 across all 5 viable cells
- Margin to second-place profile: 0.013–0.324
- 4/5 cells have margin > 0.02 (non-ambiguous dominance)

## Provenance

- Source: `phases/APPARATUS_BUNDLE_ALIGNMENT/results/bundle_alignment_results.json`
- Depends on: C1248 (apparatus profile definitions), C1249 (section-conditioned diversity)
