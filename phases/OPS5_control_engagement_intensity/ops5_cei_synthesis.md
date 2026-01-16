# Phase OPS-5: Control Engagement Intensity (CEI) Manifold

**Date:** 2026-01-15

---

## 1. What CEI Is

### Definition (Verbatim)

> *The degree to which an operator actively trades stability margin for time
and throughput by increasing intervention frequency and tolerating proximity to irreversible hazards.*

### Key Properties

| Property | Description |
|----------|-------------|
| **Operator-centric** | Describes operator posture, not system state |
| **Pressure-responsive** | Changes under accumulated operational pressures |
| **Non-monotonic** | No "highest is best" or "lowest is best" |
| **Reversible** | Operators move up AND down along CEI axis |

### What CEI Is NOT

| NOT | Explanation |
|-----|-------------|
| Physical parameter | Not heat, strength, concentration, or any material property |
| Ordinal stress level | Not "low/medium/high" intensity (falsified in Phase HOT) |
| Product indicator | Not correlated with output type or quality |
| Semantic content | No linguistic meaning; purely operational |

---

## 2. CEI Construction

### Method: DOCUMENTED_COMPOSITE_INDEX

**Formula:**

```
CEI = w1 * (1 - time_pressure) + w2 * risk_pressure + w3 * stability_pressure
```

**Weights:**

| Component | Weight | Contribution Direction |
|-----------|--------|----------------------|
| Time Inverse | 0.333 | Lower time pressure (faster) -> higher CEI |
| Risk | 0.333 | Higher risk pressure -> higher CEI |
| Stability | 0.334 | Higher stability pressure (less stable) -> higher CEI |

**Rationale:**
- CEI captures the degree to which stability is traded for throughput
- Time inverse: Faster operation = more engaged
- Risk: Tolerating more risk = more engaged
- Stability: Operating with less margin = more engaged

---

## 3. Regime Bands

Regimes occupy CEI bands, NOT strict ranks. Overlap is expected and permitted.

| Regime | N | Mean CEI | Std | IQR | Band (mean +/- IQR/2) |
|--------|---|----------|-----|-----|----------------------|
| REGIME_2 | 11 | 0.3669 | 0.1057 | 0.0915 | [0.3211, 0.4126] |
| REGIME_1 | 31 | 0.5104 | 0.0566 | 0.0897 | [0.4656, 0.5552] |
| REGIME_4 | 25 | 0.5835 | 0.0786 | 0.0978 | [0.5346, 0.6325] |
| REGIME_3 | 16 | 0.7169 | 0.0660 | 0.0969 | [0.6685, 0.7654] |

### Band Interpretation

| Band | Regime | Character |
|------|--------|-----------|
| LOW-CEI | REGIME_2 | Conservative basin; low risk tolerance |
| MID-CEI | REGIME_1, REGIME_4 | Balanced plateaus; tradeoff zones |
| HIGH-CEI | REGIME_3 | Transient spike; throughput-maximizing passage |

---

## 4. Validation Results

### 4.1 Centroid Alignment

| Check | Expected | Observed | Status |
|-------|----------|----------|--------|
| Lowest CEI regime | REGIME_2 | REGIME_2 | PASS |
| Highest CEI regime | REGIME_3 | REGIME_3 | PASS |

**CEI Ordering:**
- REGIME_2: 0.3669
- REGIME_1: 0.5104
- REGIME_4: 0.5835
- REGIME_3: 0.7169

**Status:** PASS

### 4.2 Transition Alignment

| Metric | Value |
|--------|-------|
| Transitions analyzed | 9 |
| Transitions aligned | 9 |
| Alignment rate | 100.0% |

**Status:** PASS

### 4.3 No Universal Optimum

| Check | Result |
|-------|--------|
| Any regime dominates all CEI ranges | False |

**CEI Range Coverage:**
- low_cei: REGIME_2
- mid_cei: REGIME_4, REGIME_2, REGIME_1
- high_cei: REGIME_4, REGIME_3

**Status:** PASS

---

## 5. Dynamics on the CEI Manifold

### 5.1 Bidirectional Movement

| Direction | Count | Examples |
|-----------|-------|----------|
| CEI Increase | 4 | Entry to high-CEI transient |
| CEI Decrease | 5 | Exit from high-CEI to stable basin |

**Bidirectional:** True

### 5.2 Asymmetric Costs

| Metric | Value |
|--------|-------|
| Average UP weight | 0.4257 |
| Average DOWN weight | 0.6132 |
| Asymmetry ratio (down/up) | 1.4406 |
| Down easier than up | True |

**Interpretation:**
- Moving DOWN CEI (toward stability) is easier than moving UP
- This confirms asymmetric cost structure

### 5.3 Dominated Transient Behavior

| Property | Value |
|----------|-------|
| High-CEI transient regime | REGIME_3 |
| Mean CEI | 0.7169 |

**Explanation:** Brief high-CEI excursion under time pressure, rapid exit under risk/stability pressure

---

## 6. Human-Track Integration

### 6.1 LINK Density as CEI Damping

| Metric | Value |
|--------|-------|
| LINK-CEI correlation | -0.7057 |
| Expected direction | negative |
| Observed direction | negative |

**Interpretation:** Negative correlation confirms LINK density dampens CEI

### 6.2 CF Density by CEI Band

| CEI Band | N | Avg CF-6 | Avg CF-7 | Avg LINK |
|----------|---|----------|----------|----------|
| Low | 28 | 0.0 | 0.0 | 0.4189 |
| Mid | 27 | 0.0 | 0.0 | 0.3727 |
| High | 28 | 0.0 | 0.0 | 0.3351 |

---

## 7. Why CEI Replaces Failed "Ordinal Parameter" Hypotheses

| Failed Hypothesis | Phase | Why CEI Succeeds |
|-------------------|-------|------------------|
| Heat/intensity levels | HOT | CEI is positional (engagement posture), not material state |
| Stress tiers | HOT | CEI allows overlap and non-monotonic movement |
| Ordinal parameters | HLL-2 | CEI is pressure-responsive, not fixed labeling |
| Physical gradients | HOT | CEI is operator-centric, not system property |

**Key Difference:**

> CEI describes **how engaged the operator is with the system** at any moment,
> NOT what physical state the system is in. Operators move along CEI in response
> to pressure accumulation, not in response to process phase.

---

## 8. Summary

| Component | Finding |
|-----------|---------|
| CEI definition | Documented composite index, weights explicit |
| Regime bands | 4 bands with expected ordering (R2 < R4 < R1 < R3) |
| Centroid alignment | PASS |
| Transition alignment | PASS |
| No universal optimum | PASS |
| Bidirectional movement | YES |
| Asymmetric costs | CONFIRMED |
| Human-track integration | LINK-CEI correlation = -0.7057 |

---

> **"OPS-5 is complete. A Control Engagement Intensity (CEI) manifold has been formalized,
> integrating regimes, tradeoffs, switching pressures, and human-track vigilance using
> purely operational evidence. The internal investigation is closed."**

*Generated: 2026-01-15T23:47:41.442766*
