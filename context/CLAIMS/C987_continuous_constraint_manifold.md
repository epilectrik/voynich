# C987: Discrimination Manifold Is Continuous (Not Block-Structured)

**Tier:** 2 | **Scope:** A | **Phase:** DISCRIMINATION_SPACE_DERIVATION

## Statement

After removing the hub eigenmode (λ₁), the residual ~99D discrimination space forms a continuous curved manifold, not discrete blocks. Best clustering is k=5 with silhouette 0.245 (MIXED_BANDS), where 865/972 MIDDLEs fall in a single cluster. Silhouette turns negative at k≥12. Gap statistic is -0.014 (no evidence for discrete clusters above noise). The manifold has fuzzy density bands but no clean categorical partitions.

## Evidence

### Clustering Analysis (T11)

| k | Silhouette | Largest Cluster | Structure |
|---|-----------|----------------|-----------|
| 5 | 0.245 | 865/972 (89%) | One mass + 4 outlier groups |
| 8 | 0.059 | 578/972 | Fragmenting |
| 10 | 0.079 | 721/972 | Re-consolidating |
| 12 | -0.018 | 484/972 | Negative = forced |
| 15 | -0.040 | 296/972 | Degrading |
| 20 | -0.042 | 407/972 | No structure |
| 30 | 0.009 | 431/972 | Noise |

### Manifold Diagnostics (T11)

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Best k | 5 | Minimal structure, not rich taxonomy |
| Best silhouette | 0.245 | MIXED_BANDS (∈ [0.15, 0.30]) |
| Gap statistic | -0.014 | No evidence for discrete clusters |
| NN distance CV | 0.983 | High variability = density gradients |
| Connector residual ratio | 2.47 | Universal MIDDLEs EXPAND (not collapse) |

### Key Finding: Expert's Fork Resolved

The T9 clustering ceiling (0.49) raised a question: is compatibility imposed by correlated blocks or a smooth manifold? T11 resolves this:

- **NOT blocks**: Silhouette never exceeds 0.245, gap statistic negative
- **Continuous manifold**: One massive cluster at every k, with outlier groups peeling off
- **Density gradients**: NN distance CV=0.983 indicates smooth density variation, not sharp boundaries
- Universal MIDDLEs (connectors) expand in residual space (ratio 2.47), occupying MORE of the manifold — they are differentiated, not generic

### Interpretation

1. Compatibility constraints form a **continuous geometry**, not a set of discrete types
2. The high transitivity (C983, 0.873) arises from smooth manifold curvature, not block membership
3. PREFIX blocks (C985, 3.92× enrichment) are soft density variations on a continuous surface
4. This rules out "N types of MIDDLE" models — the constraint space is inherently high-dimensional and smooth

## Provenance

- T11 (hub-residual structure analysis)
- Resolves C984 (independent features insufficient → because manifold is continuous, not factorial)
- Consistent with C982 (~101 dimensions needed to describe a continuous manifold)
- Extends C983 (transitivity from manifold curvature, not block co-membership)
