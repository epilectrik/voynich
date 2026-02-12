# C969: 2nd-Order Alternation Bias Detected But Non-Load-Bearing

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> A weak alternation-accelerating 2nd-order Markov effect exists in EN lane sequences (CMI=0.012 bits, above 0.01 threshold). After a SWITCH, P(switch again) increases by epsilon=+0.062. After a STAY, P(switch) decreases by delta=-0.067. This is statistically significant (3/4 conditioning states p<0.05, trigrams p<0.0001) but NOT generatively necessary: adding a 2-parameter correction worsens composite deviation from 1.427 to 1.495 due to asymmetric lane effects. The effect is a soft stabilization bias emergent from first-order inertia + hazard gating, not a structural state machine.

---

## Evidence

**Test:** `phases/LANE_OSCILLATION_CONTROL_LAW/scripts/t8_higher_order_test.py` and `t9_alternation_corrected_simulation.py`

### 2nd-Order Transitions (T8)

| Context | P(switch) | 1st-order baseline | Delta | Chi2 p |
|---------|-----------|-------------------|-------|--------|
| QO->CHSH (QC) | 62.7% switch back | 56.3% | +6.4% | 0.006 |
| CHSH->QO (CQ) | 64.7% switch back | 58.8% | +5.9% | 0.011 |
| QO->QO (QQ) | 53.8% switch | 58.8% | -5.0% | 0.071 (NS) |
| CHSH->CHSH (CC) | 48.0% switch | 56.3% | -8.3% | 0.001 |

### Conditional Mutual Information

CMI = 0.012 bits (threshold: 0.01). Lane at t-2 provides 0.012 bits about lane at t given lane at t-1.

### Run-Length Departure

Both QO and CHSH run lengths depart from geometric (chi2 p < 1e-8). Excess short runs (k=1) relative to first-order prediction.

### Hazard Functions

Approximately flat (CV < 0.12 for reliable data points). The non-geometric distribution is due to elevated baseline hazard rate, not shape variation.

### Generative Correction Test (T9)

| Model | Composite Dev | Within CI | Verdict |
|-------|---------------|-----------|---------|
| markov_haz (T7) | 1.427 | 6/9 | PARTIAL |
| markov_haz + alt_corr (T9) | 1.495 | 6/9 | NO_IMPROVEMENT |

The correction fixes QO run mean (2.02->1.29 SD) but breaks CHSH run mean (1.06->2.03 SD). The asymmetric effect (delta_QQ=-0.050 vs delta_CC=-0.083) prevents a symmetric correction from working.

---

## Interpretation

The 2nd-order alternation bias creates a faint "balance-restoring correction force": switches beget switches, stays beget stays. This produces slightly shorter runs than pure first-order Markov predicts. But the effect is so small (0.012 bits) and so asymmetric between lanes that it cannot be usefully parameterized. It is emergent from the interaction of first-order inertia with hazard gating — a consequence of the system's architecture, not an additional control layer. This is consistent with C643 (hysteresis oscillation), C814 (kernel-escape inverse), and C891 (ENERGY-FREQUENT inverse).

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C966 | Context: 2nd-order effect is non-load-bearing within first-order model |
| C643 | Related: hysteresis oscillation has micro-rhythm not captured by first-order |
| C814 | Related: kernel-escape inverse creates alternation pressure |
| C608 | Preserved: no lane coherence at line level |
| C670-C673 | Preserved: per-line independence maintained |

---

## Provenance

- **Phase:** LANE_OSCILLATION_CONTROL_LAW
- **Date:** 2026-02-10
- **Scripts:** t8_higher_order_test.py, t9_alternation_corrected_simulation.py
- **Results:** `phases/LANE_OSCILLATION_CONTROL_LAW/results/t8_higher_order.json`, `t9_alternation_corrected.json`

---

## Navigation

<- [C968_folio_drift_emergent.md](C968_folio_drift_emergent.md) | [INDEX.md](INDEX.md) ->
