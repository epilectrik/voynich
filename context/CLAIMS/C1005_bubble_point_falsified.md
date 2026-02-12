# C1005: Bubble-Point Oscillation Falsified (Duty-Cycle Pattern)

**Tier:** 4 | **Status:** CLOSED | **Scope:** B

---

## Statement

> Bubble-point oscillation (faster lane switching at higher REGIME intensity) is falsified. The opposite holds: hotter REGIMEs have longer run lengths in both lanes and lower alternation rates (rho=-0.44, p<0.0001). However, this effect is primarily section-driven (T7: rho=0.011, p=0.924 after section control). A modest REGIME-independent signal survives only in the double partial controlling section + QO fraction (rho=0.278, p=0.016). Lane oscillation pace is set by section context, not REGIME intensity.

---

## Evidence

**Test:** `phases/BUBBLE_POINT_OSCILLATION_TEST/scripts/bubble_point_test.py` (7-test battery)

### Hypothesis

If REGIME intensity corresponds to fire degree (F-BRU-021, SIG-07), and lane oscillation is driven by bubble-point transitions, then hotter REGIMEs should show shorter QO run lengths (faster cycling through bubble point).

### REGIME Intensity Ordering (CEI, from process_isomorphism.md)

| REGIME | CEI | Interpretation |
|--------|-----|----------------|
| REGIME_2 | 0.367 | Quiescent / low-energy |
| REGIME_1 | 0.510 | Standard operation |
| REGIME_4 | 0.584 | Active engagement |
| REGIME_3 | 0.717 | Peak throughput |

### T1: QO Run Length by REGIME (Primary)

| REGIME | n | Mean | Median | Std |
|--------|---|------|--------|-----|
| REGIME_2 | 15 | 1.226 | 1.200 | 0.195 |
| REGIME_1 | 32 | 1.434 | 1.423 | 0.143 |
| REGIME_4 | 15 | 1.366 | 1.400 | 0.282 |
| REGIME_3 | 20 | 1.411 | 1.470 | 0.251 |

Spearman: rho=+0.201, p=0.069 (marginal, WRONG direction). KW: H=8.69, p=0.034.

### T2: CHSH Run Length by REGIME

| REGIME | n | Mean | Median |
|--------|---|------|--------|
| REGIME_2 | 15 | 1.698 | 1.649 |
| REGIME_1 | 32 | 1.580 | 1.551 |
| REGIME_4 | 15 | 2.190 | 2.308 |
| REGIME_3 | 20 | 1.891 | 1.842 |

Spearman: rho=+0.370, p=0.0006. REGIME_4 anomalously long CHSH runs (precision regime = extended stabilization monitoring).

### T3: Alternation Rate by REGIME

| REGIME | n | Mean |
|--------|---|------|
| REGIME_2 | 15 | 0.526 |
| REGIME_1 | 32 | 0.562 |
| REGIME_4 | 15 | 0.375 |
| REGIME_3 | 20 | 0.468 |

Spearman: rho=-0.441, p<0.0001. Prediction was positive (faster cycling). Observed: **slower cycling at higher intensity**.

### T5: Partial Correlation (QO Run ~ REGIME | QO Fraction)

Partial Spearman: rho=+0.457, p<0.0001. Effect strengthens after QO fraction control. REGIME-independent.

### T7: Partial Correlation (QO Run ~ REGIME | Section)

| Control | Partial rho | p |
|---------|------------|---|
| Section only | +0.011 | 0.924 |
| Section + QO fraction | +0.278 | 0.016 |

**Section absorbs the REGIME effect almost entirely.** The T5 finding (rho=+0.457) was section-confounded. A modest residual (rho=0.278) survives only in the double partial.

### T6: Section-Stratified (No Within-Section Signal)

- BIO: all REGIME_1 (untestable)
- HERBAL: rho=-0.095, p=0.605
- STARS: rho=+0.105, p=0.632

---

## Interpretation

1. **Bubble-point oscillation is falsified.** Hotter REGIMEs do not produce faster lane switching. The opposite trend exists but is section-driven.

2. **Section is the primary pace-setter.** BIO (alternation ~60%) oscillates fastest; HERBAL (~43%) slowest. This confirms C650 (section-specific oscillation rates).

3. **Duty-cycle model replaces bubble-point.** The operator-controlled duty cycle (how long to sustain each mode before switching) varies by operational context (section), not by thermal intensity (REGIME). This is consistent with the Voynich system encoding operator actions, not physical dynamics.

4. **REGIME_4 CHSH anomaly.** REGIME_4 has uniquely long CHSH runs (2.19 vs 1.58-1.89 elsewhere), consistent with C494 (precision axis) and F-BRU-017 (sustained equilibration). Precision operations require extended stabilization monitoring.

5. **Distillation narrative unaffected.** This eliminates one candidate switching mechanism (physics-driven bubble-point) and supports operator-driven duty cycles, which better matches Brunschwig's procedural structure (sustained attention at high fire degrees).

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C966 | Context: first-order Markov sufficient (no hidden accumulator) |
| C643 | Context: baseline oscillation parameters |
| C650 | Confirmed: section-specific alternation rates are the primary signal |
| C494 | Supported: REGIME_4 precision axis manifests as extended CHSH monitoring |
| F-BRU-017 | Supported: REGIME_4 sustained equilibration = long stabilization runs |
| F-BRU-021 | Context: temperature is controlled variable (95.8% fit) |
| C647 | Context: QO=k-rich (energy), CHSH=e-rich (stability) vocabulary |

---

## Provenance

- **Phase:** BUBBLE_POINT_OSCILLATION_TEST
- **Date:** 2026-02-12
- **Script:** bubble_point_test.py (T1-T7)
- **Results:** `phases/BUBBLE_POINT_OSCILLATION_TEST/results/bubble_point_results.json`

---

## Navigation

<- [C1004_49class_sufficiency_confirmed.md](C1004_49class_sufficiency_confirmed.md) | [INDEX.md](INDEX.md) ->
