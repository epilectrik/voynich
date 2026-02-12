# C986: Hub Eigenmode Is Frequency Gradient

**Tier:** 2 | **Scope:** A | **Phase:** DISCRIMINATION_SPACE_DERIVATION

## Statement

The dominant eigenmode (λ₁=82.0) of the 972×972 MIDDLE compatibility matrix encodes MIDDLE frequency, not structural differentiation. Hub loading correlates with MIDDLE frequency at Spearman ρ = -0.792 (p ≈ 0). Mean hub loading increases monotonically with frequency band: rare (1-2 lines) -0.010, uncommon (3-10) -0.029, common (11-50) -0.060, universal (51+) -0.125. The hub eigenvalue is 4.3× the next eigenvalue (19.2), confirming a single dominant frequency axis.

## Evidence

### Hub-Frequency Correlation (T11)

| Metric | Value |
|--------|-------|
| Hub eigenvalue λ₁ | 82.0 |
| Next eigenvalue λ₂ | 19.2 |
| Hub dominance ratio | 4.28× |
| Hub-frequency Spearman ρ | -0.792 |
| Hub-frequency p-value | 6.1 × 10⁻²¹⁰ |
| Residual norm-frequency ρ | 0.727 |

### Hub Loading by Frequency Band (T11)

| Band | Count | Mean Hub Loading | Mean Residual Norm |
|------|-------|------------------|--------------------|
| Rare (1-2 lines) | 748 | -0.010 | 0.613 |
| Uncommon (3-10) | 131 | -0.029 | 1.071 |
| Common (11-50) | 59 | -0.060 | 1.623 |
| Universal (51+) | 34 | -0.125 | 2.227 |

### Interpretation

1. λ₁ encodes **how many contexts a MIDDLE appears in** (coverage/centrality), not which contexts
2. Removing λ₁ strips the frequency gradient and reveals the residual constraint geometry (C987)
3. Residual norm also scales with frequency (ρ=0.727) — frequent MIDDLEs are more differentiated in constraint space
4. Consistent with C476 (coverage optimization) and C755 (hub rationing) — the hub axis IS the coverage axis

## Provenance

- T11 (hub-residual structure analysis)
- Extends C981 (fingerprint architecture: hub + structured + fine-grained)
- Explains C983 (transitive clustering driven in part by hub alignment)
- Related: C476 (coverage optimization), C755 (hub rationing)
