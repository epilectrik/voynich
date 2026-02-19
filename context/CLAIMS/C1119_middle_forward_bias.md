# C1119: MIDDLE Forward Bias as Reading Direction Evidence

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** READING_DIRECTION_TEST (Phase 399)
**Extends:** C1024 (structural directionality), C886 (transition directionality)
**Relates to:** C391 (symmetric conditional entropy), C1001 (PREFIX dual encoding)

---

## Statement

MIDDLE-level mutual information is forward-biased under LTR reading: MI(MIDDLE_t; class_{t+1}) = 0.312 bits vs MI(MIDDLE_t; class_{t-1}) = 0.242 bits (asymmetry +0.070 bits, z=17.0 vs within-line positional shuffle null). PREFIX shows weak backward bias (-0.018 bits, z=-4.4), consistent with positional autocorrelation. SUFFIX shows weak forward bias (+0.018 bits, z=5.5). Confirms C1024 class-level finding at raw MIDDLE resolution; provides direct structural evidence for left-to-right reading direction.

---

## Evidence

### MI Decomposition by Component

| Component | MI_forward | MI_backward | Asymmetry | z-score | Genuine % |
|-----------|-----------|-------------|-----------|---------|-----------|
| PREFIX | 0.153 | 0.171 | -0.018 | -4.4 | 98% |
| **MIDDLE** | **0.312** | **0.242** | **+0.070** | **+17.0** | **100%** |
| SUFFIX | 0.103 | 0.085 | +0.018 | +5.5 | 100% |

### Null Control

100 within-line token shuffles. Real MIDDLE asymmetry is 17 standard deviations above the null mean (-0.0002). The genuine sequential component accounts for 100% of the observed asymmetry.

### Physical Interpretation

MIDDLE at position t predicts the class at physical-right position (t+1) better than at physical-left position (t-1) by 0.070 bits. Information flows left-to-right at the MIDDLE level. This is the primary structural carrier of reading direction — MIDDLE is the directional executor (C1024), and its directional bias aligns with LTR reading.

PREFIX weak backward bias (-0.018) reflects positional autocorrelation: PREFIXes are spatially clustered (C1001 zones), so a PREFIX predicts its physical-left neighbor slightly better due to zone membership persistence.

### Comparison with C1024

C1024 measured MI asymmetry using instruction class (49-class) bigrams. This measurement uses raw MIDDLE bigrams. The numerical agreement (both +0.070 bits) suggests the asymmetry is a property of the MIDDLE identity itself, not an artifact of class compression.

---

## Provenance

- Phase: 399 (READING_DIRECTION_TEST)
- Script: `phases/READING_DIRECTION_TEST/scripts/reading_direction_test.py` (T2)
- Results: `phases/READING_DIRECTION_TEST/results/reading_direction_results.json`
- Related: C1024, C886, C391, C1001
