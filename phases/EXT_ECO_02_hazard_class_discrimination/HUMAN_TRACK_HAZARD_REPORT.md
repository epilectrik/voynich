# Human-Track Behavior Near Hazard Classes

**Date:** 2026-01-05
**Extension of:** EXT-ECO-02

---

## Purpose

Test whether human-track (residue) tokens behave differently near
batch-focused vs apparatus-focused hazards.

**Hypothesis:** Apparatus hazards have no LINK (no waiting) → no time for attentional pacing marks.

---

## Test Results

### Test 1: Human-Track Density Near Hazards

| Metric | Value |
|--------|-------|
| batch_mean_ht_nearby | 0.004 |
| apparatus_mean_ht_nearby | 0.001 |
| difference | 0.002 |
| effect_size | 0.021 |

**Prediction:** Batch hazards should have HIGHER human-track density (time to write)
**Observed:** Batch HIGHER
**Supports Hypothesis:** YES

---

### Test 2: Human-Track Complexity Near Hazards

| Metric | Value |
|--------|-------|
| batch_mean_length | 0.889 |
| apparatus_mean_length | 3.0 |
| batch_ht_tokens | 54 |
| apparatus_ht_tokens | 6 |

**Prediction:** Batch hazards should have MORE COMPLEX human-track (time for elaborate marks)
**Observed:** No difference or apparatus more complex
**Supports Hypothesis:** NO

---

### Test 3: Human-Track Presence Rate

| Metric | Value |
|--------|-------|
| batch_presence_rate | 0.001 |
| apparatus_presence_rate | 0.001 |
| batch_with_ht / total | 16 / 13845 |
| apparatus_with_ht / total | 6 / 4138 |

**Prediction:** Batch hazards should have HIGHER presence rate (some HT nearby)
**Observed:** No difference or apparatus higher
**Supports Hypothesis:** NO

---

### Test 4: Immediate Adjacency

| Metric | Value |
|--------|-------|
| batch_adjacency_rate | 0.001 |
| apparatus_adjacency_rate | 0.0 |
| difference | 0.0 |

**Prediction:** Batch hazards should have HIGHER immediate HT adjacency
**Observed:** Batch HIGHER
**Supports Hypothesis:** YES

---

## Summary

| Metric | Value |
|--------|-------|
| Tests supporting hypothesis | 2/4 |
| **Verdict** | **PARTIAL_SUPPORT** |
| **Confidence** | **LOW** |

---

## Interpretation

The hypothesis is **PARTIALLY SUPPORTED**. Some difference exists between hazard types,
but the effect is not strong enough to confidently conclude that apparatus hazards drive suppression.

---

*Analysis complete.*
