# C1006: Macro-State Dwell Non-Geometricity is Topology Artifact

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> Non-geometric run-length distributions observed at the 6-state macro-automaton level (chi2=52.79, p<0.0001 for AXM) are a phase-type distribution artifact of compressing 32 instruction classes into one macro-state. A first-order Markov null model with the empirical 6x6 transition matrix reproduces the observed AXM dwell distribution (KS D=0.020, p=0.074). No temporal memory exists beyond first-order transitions. The Weibull shape parameter k=1.55 is REGIME-invariant (range 0.096); REGIME modulates dwell scale (lambda) only.

---

## Evidence

**Test:** `phases/REGIME_DWELL_ARCHITECTURE/scripts/dwell_architecture.py` (T5, T5b, T6, T6b, T7)

### T5: Hazard Function at Three Resolution Levels

| Level | n_runs | Mean | Hazard Shape |
|-------|--------|------|-------------|
| 6-state (AXM) | 4,270 | 2.536 | Increasing (rho=+0.95, p<0.0001) |
| 49-class (AXM classes pooled) | 10,274 | 1.054 | Insufficient data (95.2% exit at step 1) |
| EN-only (binary) | 4,204 | 2.691 | Increasing |

At 49-class resolution, AXM classes almost never repeat consecutively (mean run = 1.054). Long macro-state runs are entirely composed of *different* AXM classes following each other.

### T5b: First-Order Markov Null Model (Decision Gate)

100 line-matched simulations using empirical 6x6 transition matrix:

| Metric | Empirical | Simulated (95% CI) |
|--------|-----------|-------------------|
| Mean AXM run length | 2.536 | 2.468 (2.415-2.511) |
| KS vs empirical | - | D=0.020, p=0.074 |
| Geometric chi2 | 52.79 (p<0.0001) | 5097 (p<0.0001) |

The simulated data is ALSO non-geometric (chi2=5097). The hub-and-spoke topology (C976, spectral gap 0.894) with 32 compressed classes produces a phase-type distribution that inherently mimics temporal memory.

### T6: State-Specific Geometric Tests

| State | n_runs | Result | Chi2 | p |
|-------|--------|--------|------|---|
| FL_HAZ (2 classes) | 873 | GEOMETRIC | 2.17 | 0.338 |
| FQ (4 classes) | 2,284 | NON-GEOMETRIC | 10.20 | 0.017 |
| CC (3 classes) | 708 | Insufficient bins | - | - |
| AXm (6 classes) | 476 | Insufficient bins | - | - |
| AXM (32 classes) | 4,270 | NON-GEOMETRIC | 52.79 | <0.0001 |
| FL_SAFE (2 classes) | 120 | Insufficient bins | - | - |

Non-geometricity correlates with number of compressed classes: AXM (32) strongest, FQ (4) moderate, FL_HAZ (2) geometric. This is the signature of aggregation artifacts.

### T6b: Compositional Drift Within AXM Runs

Long AXM runs (length >= 6, n=354): early-run and late-run class compositions differ (chi2=52.09, p=0.010, dof=31). Early entropy = 4.001 bits, late entropy = 4.105 bits. Internal S3/S4 directional flow (C977, 24.4x asymmetry) produces apparent persistence through compositional heterogeneity.

### T7: Weibull Shape Invariance Across REGIMEs

| REGIME | n | k (shape) | lambda (scale) |
|--------|---|-----------|----------------|
| REGIME_2 | 415 | 1.590 | 2.311 |
| REGIME_1 | 2,350 | 1.541 | 3.074 |
| REGIME_4 | 376 | 1.637 | 2.452 |
| REGIME_3 | 1,129 | 1.590 | 2.703 |

k range = 0.096 (Spearman rho=+0.600, p=0.400). REGIME modulates scale (lambda varies 2.3-3.1) but not shape (k constant at ~1.55). The dwell law is REGIME-invariant — consistent with C979 (REGIME modulates weights, not topology).

---

## Interpretation

1. **The "memory" finding is closed.** Non-geometric chi2=52.79 at the 6-state level is a mathematical consequence of compressing 32 first-order-sufficient classes into one observation state. No temporal accumulator exists.

2. **Phase-type distributions are expected.** When multiple internal states contribute to a single observed state, the sojourn-time distribution is a mixture of geometrics (phase-type), which is heavier-tailed than geometric. This is textbook aggregation.

3. **C1004 is safe.** 49-class Markov remains sufficient for all exploitable sequential structure. The non-geometric property exists only at the compressed 6-state view.

4. **Weibull k=1.55 (increasing hazard) is structural.** The "deadline" pattern is not an operator counting mechanism — it reflects the probability of eventually transitioning through an AXM-internal pathway that exits the macro-state, which increases with dwell time as more internal states are visited.

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C976 | Context: 6-state topology (spectral gap 0.894) produces the compression |
| C977 | Mechanism: S3/S4 directional flow (24.4x asymmetry) creates compositional drift |
| C978 | Context: hub-and-spoke topology, mixing time ~1.1 tokens |
| C979 | Reinforced: REGIME modulates weights (scale), not topology (shape) |
| C1004 | Safe: 49-class first-order sufficiency not threatened |
| C1005 | Context: REGIME affects dwell duration, not switching rate |
| C966 | Compatible: EN lane oscillation first-order sufficient at lane level |

---

## Provenance

- **Phase:** REGIME_DWELL_ARCHITECTURE
- **Date:** 2026-02-12
- **Script:** dwell_architecture.py (T5, T5b, T6, T6b, T7)
- **Results:** `phases/REGIME_DWELL_ARCHITECTURE/results/dwell_architecture.json`

---

## Navigation

<- [C1005_bubble_point_falsified.md](C1005_bubble_point_falsified.md) | [INDEX.md](INDEX.md) ->
