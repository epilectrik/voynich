# C1157: Boundary Divergence Mediates the AXM Residual

**Tier:** 2
**Scope:** B, line, AXM residual
**Phase:** LINE_TRANSITION_DYNAMICS (Phase 413)
**Depends on:** C1035, C1155, C1156

## Statement

Per-folio boundary divergence — how much a folio's entry/exit transition profiles differ from its interior — is the first predictor to explain incremental variance in the C1035 AXM residual. Adding boundary divergence to the C1035 baseline (R²=0.569, LOO=0.433, n=70) yields dR²=0.0845, F=14.15, p=0.0004, with LOO R² improving from 0.433 to 0.512. This is genuine out-of-sample improvement, not overfitting. Boundary divergence anticorrelates with AXM self-transition (Spearman rho=-0.732, p<0.0001): folios with stronger boundary structure have less self-reinforcing dynamics.

## Evidence

| Model | R² | LOO R² | n |
|-------|-----|--------|---|
| C1035 baseline | 0.569 | 0.433 | 70 |
| + boundary divergence | 0.654 | 0.512 | 70 |
| **Increment** | **+0.085** | **+0.079** | |

**F-test:** F=14.15, p=0.0004 (well beyond 0.03/0.05 thresholds)

**Boundary divergence:** Mean=0.350, SD=0.175. Computed as JSD(entry_6state, interior_6state) + JSD(exit_6state, interior_6state) per folio. Minimum 10 transitions per zone per folio required (70/72 folios qualify).

**Cross-validation with C1017 residual:** Spearman rho=-0.264, p=0.019 (significant against the post-baseline residual itself).

## Structural Implication

The C1035 residual is no longer fully closed. Boundary divergence captures a structural dimension — how strongly a procedure differentiates its entry/exit phases from its operational interior — that was invisible to all previous folio-level predictors (paragraph count, HT density, gatekeeper fraction, QO lane balance, vocabulary residual, line count, kernel heterogeneity, trajectory diversity, type entropy). This is a LINE-LEVEL property that only manifests when transition dynamics are computed separately by position zone.

**Important caveat:** Position conditioning does NOT improve the M2 generative model (T3: 0/3 metrics improved). The position structure is real and predictive of folio-level dynamics, but the aggregate M2 transition matrix already absorbs it for generation purposes. This means boundary divergence is a descriptive structural feature, not a missing generative mechanism.

**C1035 status:** Partially reopened. The 57% irreducible residual is now ~49% after boundary divergence (LOO: 0.512 explained). The remaining ~49% may still be genuine design freedom, but the closure is no longer absolute.
