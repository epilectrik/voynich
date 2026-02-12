# C982: Discrimination Space Dimensionality ~101

**Tier:** 2 | **Scope:** A | **Phase:** DISCRIMINATION_SPACE_DERIVATION

## Statement

The MIDDLE discrimination space has an effective dimensionality of approximately 101, estimated as the median across 7 independent methods. The space is STRUCTURED_HIGH_DIMENSIONAL — too complex for low-dimensional latent models but far below the full 972-node space.

## Evidence

### Convergence of 7 Independent Methods (T2, T3, T4, T5)

| Method | Estimate | Source |
|--------|----------|--------|
| CV-AUC plateau | K ≈ 256 | T2 link prediction |
| CV-AUC elbow | K ≈ 96 | T2 diminishing returns |
| NMF elbow | K ≈ 128 | T2 reconstruction |
| Marchenko-Pastur | 28 above noise | T1 random matrix theory |
| Factored estimate | ~86 | T3 structural decomposition |
| Morphological PCA k_95 | 101 | T4 character features |
| Spectral prediction AUC | 0.934 at K=256 | T2 (best achievable) |

### Median Estimate: 101

- Sorted estimates: [28, 86, 96, **101**, 128, 256, 256]
- Median = 101
- Range: 28 (noise-floor count) to 256 (CV-AUC asymptote)

### Classification: STRUCTURED_HIGH_DIMENSIONAL

- NOT low-dimensional: 3-5D latent models totally fail (C973)
- NOT full-rank: 101 << 972 (10.4% of theoretical maximum)
- Structured: slow eigenvalue decay, 28 modes above noise, clear convergence

## Relationship to Three-Layer Architecture (C976)

| Layer | Dimensionality | This phase |
|-------|---------------|------------|
| Control topology | 6 states | C976 |
| Grammar | 49 classes | C976 |
| Token-level parameterization | ~101 | **This constraint** |

The ~101 dimensions quantify the "token-level parameterization" layer identified in C976. The 49 instruction classes are dressed in ~101 dimensions of free variation, of which ~28 are structurally prominent (above noise floor).

## Provenance

- T2 (dimensionality convergence), T3 (structural decomposition), T4 (morphological derivation), T5 (synthesis)
- Refines C976's "token-level parameterization" with a concrete dimensionality estimate
- Supersedes SSD_PHY_1a (D≥50 lower bound) with tighter estimate
