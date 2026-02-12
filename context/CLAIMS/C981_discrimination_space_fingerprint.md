# C981: MIDDLE Discrimination Space Is a Structural Fingerprint

**Tier:** 2 | **Scope:** A | **Phase:** DISCRIMINATION_SPACE_DERIVATION

## Statement

The MIDDLE compatibility graph (972 MIDDLEs from Currier A line co-occurrence, C475 basis) has a spectral profile that is anomalous under degree-preserving randomization (4/5 metrics anomalous, z-scores +17 to +137) AND stable under bootstrap subsampling (CV < 0.055 at 20% removal). This is a genuine structural fingerprint of the underlying constraint system, not an artifact of sparse graph statistics or sampling noise.

## Evidence

### Matrix Characterization (T1)
- 972 MIDDLEs, 10,241 compatible pairs out of 471,906 (2.17% density, 97.8% incompatible)
- Leading eigenvalue λ₁ = 82.0 (ratio 4.3× over λ₂)
- Effective rank 344, decay profile SLOW_DECAY
- Only 1 eigenvalue exceeds Marchenko-Pastur 99th percentile; 28 exceed random 2nd + 2σ

### Null Ensemble Rarity (T6)
- 100 Configuration Model trials (degree-preserving): 4/5 metrics anomalous
  - λ₁: z = +79.6 (real 82.0 vs CM 15.5±0.84)
  - n_eig > 12: z = +17.5 (real 18 vs CM 1.6±0.94)
  - Effective rank: z = +15.9 (real 27.7 vs CM 11.9±1.00)
  - Clustering: z = +136.9 (real 0.873 vs CM 0.253±0.005)
  - Spectral gap: NOT anomalous (z = +1.3) — hub structure is degree-driven
- 100 Erdős-Rényi trials: 5/5 metrics anomalous

### Bootstrap Stability (T7)
- 50 trials at 10%, 20%, 30% MIDDLE removal
- Max CV at 20% removal: 0.0546 (all core metrics < 0.10)
- λ₁ degrades perfectly linearly: ratio 0.90 at 10%, 0.80 at 20%, 0.71 at 30%
- Verdict: STABLE — structure is intrinsic, not dependent on specific MIDDLEs

## Integrated Verdict

**FINGERPRINT_CONFIRMED:** The spectral profile is anomalous under degree-preserving randomization AND stable under subsampling. The compatibility structure encodes genuine constraint information that cannot be explained by degree heterogeneity alone.

## Provenance

- T1 (definitive matrix), T6 (null ensemble), T7 (bootstrap stability), T8 (synthesis)
- Builds on C475 (1,187 MIDDLEs, 95.7% incompatible)
- Supersedes LATENT_AXES phase (early probe, AZC-only, no convergence found)
