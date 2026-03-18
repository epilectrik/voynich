# C1738: SEALED_VESSEL Universal Secondary Dominance

**Tier:** 2
**Phase:** APPARATUS_BUNDLE_ALIGNMENT (Phase 599)
**Scope:** B, apparatus, secondary profiles, SEALED_VESSEL

## Finding

SEALED_VESSEL is the dominant secondary apparatus profile in ALL viable section×REGIME cells:

| Cell | SEALED_VESSEL | SUSTAINED_HEAT | PRECISION | DIRECT_FIRE |
|------|--------------|----------------|-----------|-------------|
| S:R1 | **0.609** | 0.285 | 0.045 | 0.061 |
| S:R3 | **0.516** | 0.344 | 0.103 | 0.038 |
| H:R2 | **0.488** | 0.277 | 0.171 | 0.064 |
| H:R4 | **0.374** | 0.353 | 0.236 | 0.037 |
| H:R3 | **0.328** | 0.314 | 0.264 | 0.094 |

The secondary profile space does not differentiate cells by apparatus identity — SEALED_VESSEL vocabulary (ok, aii, ee, eey, eeol) is the universal secondary mode after DISTILLATION is removed.

## Significance

The SEALED_VESSEL markers (ok=seal, aii=unseal, ee=extended cooling, eey=overnight cooling, eeol=overnight standing) may represent **general-purpose containment/waiting operations** rather than specific apparatus types. Their universality across all REGIMEs and sections suggests they encode a grammatical function (waiting, containment, monitoring cycles) that is required by all control programs, not just those involving sealed vessels.

This constrains interpretation of the apparatus profile system (C1248): the 5 profiles are real vocabulary clusters, but "SEALED_VESSEL" as a historical-apparatus label may be misleading. The vocabulary may be better understood as "containment/patience operations" that are structurally universal.

## Key Metrics

- SEALED_VESSEL secondary fraction: 0.328–0.609 across all 5 viable cells
- Margin to second-place profile: 0.013–0.324
- 4/5 cells have margin > 0.02 (non-ambiguous dominance)

## Provenance

- Source: `phases/APPARATUS_BUNDLE_ALIGNMENT/results/bundle_alignment_results.json`
- Depends on: C1248 (apparatus profile definitions), C1249 (section-conditioned diversity)
