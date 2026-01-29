# C666: Kernel Contact Trajectory

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

## Finding

Kernel operator rates (k, h, e) are **stationary within folios**. No kernel type shows significant monotonic evolution from early to late lines. The k/e ratio (energy vs stability balance) is also flat.

The e kernel (STABILITY_ANCHOR) dominates at ~29% regardless of position. The k kernel (ENERGY_MODULATOR) is rare (~0.2%) and h (PHASE_MANAGER) is rarer (~0.08%), both flat.

## Evidence

### Corpus-Wide Kernel Trajectories (2420 lines)

| Kernel | Q1 | Q2 | Q3 | Q4 | rho | p | KW p | Verdict |
|--------|-----|-----|-----|-----|------|---|------|---------|
| k | 0.0024 | 0.0005 | 0.0021 | 0.0019 | -0.023 | 0.26 | 0.047 | NON-MONOTONIC |
| h | 0.0008 | 0.0007 | 0.0007 | 0.0008 | -0.014 | 0.48 | 0.98 | FLAT |
| e | 0.3002 | 0.2884 | 0.3033 | 0.2842 | -0.022 | 0.28 | 0.20 | FLAT |

### k/e Ratio Trajectory

| Q1 | Q2 | Q3 | Q4 | rho | p |
|-----|-----|-----|-----|------|---|
| 0.059 | 0.057 | 0.051 | 0.069 | -0.023 | 0.29 |

## Interpretation

The kernel control layer operates at constant intensity throughout programs. There is no "energy ramp-up" (early k) or "stabilization convergence" (late e) pattern at the meso-temporal level.

This is consistent with the stationary control loop model: every line maintains the same relationship to the kernel operators. The program does not progress through kernel-defined phases; it maintains a constant kernel contact regime throughout.

Note: k and h are extremely rare in the token population. The ~29% e rate reflects the dominance of e-ending tokens (ey, eey, edy) in the B vocabulary, not just kernel-operator-specific tokens. The kernel detection heuristic captures morphological signatures of kernel affinity, not pure kernel operations.

## Cross-References

- C074: 57.8% terminal STATE-C — convergence to e-anchored state, but rate is constant throughout program
- C105: e anchors stability (54.7% recovery path rate) — e's constancy means stability anchoring is uniform
- C458: Kernel contact ratio CV=0.112 (clamped between folios) — C666 shows it's also clamped within folios

## Provenance

B_FOLIO_TEMPORAL_PROFILE, Script 1 (folio_temporal_metrics.py), Test 3
