# C992: e-Kernel Is the Compatibility Kernel

**Tier:** 2 | **Scope:** A↔B | **Phase:** CONSTRAINT_ENERGY_FUNCTIONAL

## Statement

Among the three core kernel operators (k, h, e), the e-kernel dominates compatibility energy: E vs e-fraction ρ = +0.309 (p = 2×10⁻⁵⁴), compared to k ρ = +0.103 and h ρ = +0.054. Lines with high e-fraction average E = +0.0005 (near compatible); lines with low e-fraction average E = -0.018 (tense). The e-kernel's compatibility dominance is consistent with its role as stability anchor (C105: 54.7% of recovery paths pass through e).

## Evidence

### Kernel-Energy Correlations (T5)

| Kernel | ρ(fraction, E) | p-value | Interpretation |
|--------|----------------|---------|----------------|
| e | +0.309 | 2×10⁻⁵⁴ | Strong — compatibility driver |
| k | +0.103 | 4×10⁻⁷ | Moderate |
| h | +0.054 | 0.008 | Weak |

### e-Fraction Bins (T5)

| Bin | n | Mean E |
|-----|---|--------|
| Low e | 616 | -0.018 |
| Med-low e | 597 | -0.014 |
| Med-high e | 750 | -0.010 |
| High e | 449 | +0.001 |

Monotonic increase from low-e (tense) to high-e (compatible).

### First-Line vs Body (T5)

| Property | First Lines | Body Lines |
|----------|-------------|------------|
| h_frac | 0.153 | 0.069 |
| e_frac | 0.338 | 0.362 |
| compound_frac | 0.188 | 0.102 |
| E | -0.003 | -0.011 |

First lines (HT specification) have 2.2× more h-kernel and 1.8× more compounds but only slightly less e — their higher compatibility comes primarily from compound MIDDLEs, not kernel composition.

### Interpretation

1. e is the **compatibility kernel** — it stabilizes lines toward the compatible end of the energy spectrum
2. This geometrically explains C105 (e = stability anchor): e-rich MIDDLEs occupy shallow, compatible regions of the manifold
3. h is the weakest kernel predictor despite being the "phase manager" (C104) — h operates near the tension boundary
4. k sits between h and e, consistent with its "energy modulator" role (C103) — modulating between compatible and tense regions
5. The kernel hierarchy in compatibility (e > k > h) mirrors the kernel hierarchy in recovery (C105: e dominates recovery paths)

## Provenance

- T5 (kernel composition)
- Confirms C105 (e = stability anchor) geometrically
- Consistent with C521 (directional asymmetry: e→h suppressed, h→e elevated — stability is absorbing)
- Extends C965 (kernel composition shift) — the h/e shift through body lines is a shift along the energy gradient
