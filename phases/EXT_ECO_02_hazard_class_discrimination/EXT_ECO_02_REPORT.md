# Phase EXT-ECO-02: Hazard Class Discrimination

**Status:** COMPLETE
**Date:** 2026-01-05
**Tier:** 3 (External Alignment Only)

---

## Purpose

Stress test the hybrid hazard model: Do CONTAINMENT_TIMING and ENERGY_OVERSHOOT
hazards show different structural signatures than batch-focused hazards?

**Classification:**
- **Batch-Focused:** PHASE_ORDERING, COMPOSITION_JUMP, RATE_MISMATCH (12/17 = 71%)
- **Apparatus-Focused:** CONTAINMENT_TIMING, ENERGY_OVERSHOOT (5/17 = 29%)

---

## Test Results

### Test 1: Severity Distribution

| Metric | Value |
|--------|-------|
| batch_mean_severity | 0.733 |
| apparatus_mean_severity | 0.8 |
| difference | 0.067 |
| effect_size | 0.707 |

**Prediction:** Apparatus hazards should have HIGHER severity (more urgent)
**Observed:** Apparatus HIGHER
**Supports Hybrid:** YES

---

### Test 2: LINK Proximity

| Metric | Value |
|--------|-------|
| batch_mean_link_nearby | 1.229 |
| apparatus_mean_link_nearby | 0.0 |
| difference | 1.229 |

**Prediction:** Apparatus hazards should have LOWER LINK nearby (faster response needed)
**Observed:** Batch higher LINK
**Supports Hybrid:** YES

---

### Test 3: Rapid Intervention Patterns

| Metric | Value |
|--------|-------|
| batch_mean_run_length | 0 |
| apparatus_mean_run_length | 0 |
| batch_short_run_rate | 0 |
| apparatus_short_run_rate | 0 |

**Prediction:** Apparatus hazards should have SHORTER action runs (urgent intervention)
**Observed:** Batch shorter or equal
**Supports Hybrid:** NO

---

### Test 4: Token Frequency

| Metric | Value |
|--------|-------|
| batch_total_occurrences | 13845 |
| apparatus_total_occurrences | 6110 |
| batch_per_hazard_token | 865.3 |
| apparatus_per_hazard_token | 678.9 |

**Prediction:** Apparatus hazard tokens should be RARER (emergency states)
**Observed:** Apparatus RARER
**Supports Hybrid:** YES

---

### Test 5: Kernel Distance

| Metric | Value |
|--------|-------|
| batch_mean_kernel_distance | 1.0 |
| apparatus_mean_kernel_distance | 1.0 |
| difference | 0.0 |

**Prediction:** Apparatus hazard tokens should be CLOSER to kernel (control-critical)
**Observed:** Batch closer or equal
**Supports Hybrid:** NO

---

## Summary

| Metric | Value |
|--------|-------|
| Tests supporting hybrid | 3/5 |
| Support rate | 0.6 |
| **Verdict** | **HYBRID_SUPPORTED** |
| **Confidence** | **MODERATE** |

---

## Interpretation

The hybrid hazard model is **SUPPORTED**. CONTAINMENT_TIMING and ENERGY_OVERSHOOT
hazards show structurally distinct signatures from batch-focused hazards.

**Refined Hazard Interpretation:**

| Hazard Type | Classes | % | Primary Mode |
|-------------|---------|---|--------------|
| Batch-Focused | PHASE_ORDERING, COMPOSITION_JUMP, RATE_MISMATCH | 71% | Opportunity-loss (batch ruination) |
| Apparatus-Focused | CONTAINMENT_TIMING, ENERGY_OVERSHOOT | 29% | Equipment protection |

This tightens the interpretation by accounting for:
- The 3020 rapid intervention runs (apparatus protection responses)
- The Test F ambiguity in EXT-ECO-01 (physical-instability got STRONG there)
- Real workshop concerns (both product AND equipment matter)

---

## Interpretive Boundary

This analysis evaluates structural signatures only. It does NOT:
- Identify specific apparatus or equipment
- Prove any historical claim
- Modify the frozen grammar model

---

*EXT-ECO-02 COMPLETE.*
