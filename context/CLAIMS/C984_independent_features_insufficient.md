# C984: Independent Binary Features Cannot Reproduce Compatibility Structure

**Tier:** 2 | **Scope:** A | **Phase:** DISCRIMINATION_SPACE_DERIVATION

## Statement

An AND-style model with K independent binary features per MIDDLE (compatible if shared features ≥ threshold) can match the graph's density (2.2%), leading eigenvalue (~82), eigenvalue count (18 above 12), and effective rank (~28) — but fails categorically on clustering. The best achievable clustering is 0.49 (at K=200), versus the real 0.87, a 44% shortfall at all K values tested. The constraint features governing MIDDLE compatibility must be correlated, hierarchical, or block-structured — not independent.

## Evidence

### AND-Model Sweep (T9, 8 K values, 10 seeds each)

| K | p | T | Density | Clustering | λ₁ | n_eig>12 | Eff. rank |
|---|---|---|---------|------------|-----|----------|-----------|
| **Target** | — | — | **0.022** | **0.873** | **82.0** | **18** | **27.7** |
| 40 | 0.45 | 14 | 0.022 | 0.437 | 81.4 | 20 | 28.7 |
| 60 | 0.55 | 26 | 0.022 | 0.444 | 87.8 | 19 | 27.9 |
| 150 | 0.57 | 61 | 0.020 | 0.434 | 81.6 | 17 | 27.9 |
| 200 | 0.77 | 133 | 0.022 | 0.488 | 99.9 | 7 | 24.3 |

### Key Observations

1. **Density is trivially matchable** — many (K, p, T) combinations give 2.2%
2. **Spectral profile is matchable** — K=40 and K=150 reproduce λ₁, eigenvalue count, and effective rank within error bars
3. **Clustering is the insurmountable gap** — best 0.49 vs target 0.87, regardless of K
4. Clustering is approximately constant (0.30-0.49) across K=[20,200] — the independent feature model has a structural ceiling

### Architectural Implication

Independent features produce clustering ~0.44 because feature overlap between (A,B) and (B,C) doesn't strongly predict overlap between (A,C) when features are uncorrelated. Achieving clustering 0.87 requires that features come in correlated bundles: if you have feature X, you're likely to also have features Y and Z. This implies:

- **Hierarchical feature structure** (features organized in groups/levels)
- **Block-structured compatibility** (compatibility determined by membership in overlapping communities)
- **Correlated feature assignments** (features are not drawn independently)

The discrimination space has internal structure beyond independent binary axes.

## Provenance

- T9 (independent feature model), building on T6 (null ensemble) and T1 (matrix characterization)
- Falsifies the simplest generative model for the compatibility structure
- Consistent with C983 (transitive compatibility) — transitivity requires correlated features
