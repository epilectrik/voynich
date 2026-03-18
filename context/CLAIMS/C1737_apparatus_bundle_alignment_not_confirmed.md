# C1737: Apparatus Bundle Alignment Not Confirmed

**Tier:** 2
**Phase:** APPARATUS_BUNDLE_ALIGNMENT (Phase 599)
**Scope:** B, apparatus, Brunschwig, REGIME, secondary profiles

## Finding

No support was found for the tested family of Brunschwig-derived secondary-profile bridges. The Brunschwig 1512 method-bundle taxonomy (balneum_mariae, circulation, open_fire, sand_bath) does not recover Voynich secondary apparatus profile shape under 48 pre-registered bridge variants. All 4 primary tests fail:

1. **Mantel geometry**: median r=-0.279, p=0.794, 0/48 bridge variants significant (predicted inter-cell distances anti-correlated with observed)
2. **Dominant match**: median 0.25 match fraction — all cells show SEALED_VESSEL as dominant, but bridge predicted different dominants per cell
3. **Stars R1-R3 direction**: 1/3 concordant (p=0.913) — SUSTAINED_HEAT and DIRECT_FIRE flip vs prediction
4. **Open-cycle signature**: cosine=-0.606 (p=0.806) — multi-distillation recipes predict the opposite direction from R3

The negative is robustly consistent across all 48 bridge variants (0% significant, 88% negative Mantel r).

## Method

Pre-registered predictions with SHA-256 hash (`5dded97c...`). 48 bridge variants across admissible weight family [0.55-0.80] and alternate profile mappings. 5 viable section×REGIME cells (H:R2=13, H:R3=5, H:R4=12, S:R1=10, S:R3=12). Secondary profiles = DISTILLATION removed, 4 remaining axes re-normalized.

## Significance

With the current bridge design, support remains strongest for thermal-intensity / safety-modulation alignment (C1735/C1736). This phase did not recover an additional apparatus-shape alignment from Brunschwig method bundles to Voynich secondary apparatus profiles.

The DISTILLATION diagnostic is clean (S1: p=0.624), confirming this is a genuine secondary-space failure, not a thermal intensity confound.

This result should be interpreted as failure of the tested bridge family, not as disconfirmation of Voynich apparatus structure itself, which remains internally validated by C1248, C1380, C1625-C1629, C1640, C1668, and C1722.

## Caveats

- **P4 design concern**: `distill_references >= 2` may not correspond to open-cycle/unseal intervention (C1247). Multi-distillation recipes concentrate balneum_mariae and horse_dung (gentle sustained methods), not reopening operations. This weakens P4 specifically.
- **Bridge family breadth**: 48 variants share the same 4 prototype families, same cell-mean geometry, same exclusion of distributional signatures. Robustness is across weight/alternate parameters of one bridge framework, not across fundamentally different alignment approaches.
- **Voynich apparatus space may be a containment/closure/response manifold** rather than a direct historical method inventory, which would explain why thermal intensity alignment succeeds (C1735/C1736) while method-bundle alignment fails.

## Key Metrics

- Mantel r: -0.279 (median across 48 variants)
- Dominant match: 0.25 (1/4 non-ambiguous)
- Stars direction: 1/3 concordant
- Open-cycle cosine: -0.606
- Bridge variants yielding positive Mantel: 12%

## Provenance

- Source: `phases/APPARATUS_BUNDLE_ALIGNMENT/results/bundle_alignment_results.json`
- Pre-registration: `phases/APPARATUS_BUNDLE_ALIGNMENT/PREDICTIONS.md`
- Depends on: C1248 (apparatus profiles), C1247 (aii R3 specificity), C494 (R4 precision axis), C1735 (thermal intensity alignment), C1736 (thermal-safety paragraph gradient)
