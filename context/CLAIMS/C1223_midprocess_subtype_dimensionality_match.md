# C1223: MIDPROCESS Sub-Type Split Matches Voynich Dimensionality

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** MODERN_DISTILLATION_DIMENSIONAL_COMPARISON (Phase 435)
**Extends:** C1222 (modern distillation closer to Voynich), C1056 (MIDPROCESS structural absence)
**Relates to:** F-BRU-031 (modern dimensional comparison), C1207 (seven operational axes)

---

## Statement

Splitting MIDPROCESS into 5 Voynich-aligned sub-types (MONITORING, ENERGY, STABILITY, CLOSURE, STRUCTURAL) increases modern distillation from 4 PCs to 5 PCs for 80% variance, exactly matching Voynich. The remaining dimensional gap between 7-phase modern distillation (4 PCs) and Voynich (5 PCs) is fully explained by material-specific process control parameterization within MIDPROCESS.

### Dimensional Progression

| Metric | Brunschwig | Modern (7-phase) | Modern (11-feature) | Voynich |
|--------|-----------|-----------------|-------------------|---------|
| Features | 7 | 7 | 11 | 10 |
| Active dimensions | 5 | 7 | 11 | 10 |
| n_for_80% | 3 | 4 | **5** | **5** |
| n_for_90% | 4 | 5 | 7 | 6 |
| Entropy (bits) | 1.908 | 2.334 | 2.921 | 2.660 |

### MIDPROCESS Sub-Type Mapping to Voynich Axes

| Sub-Type | Actions | Mean | Voynich Axis |
|----------|---------|------|-------------|
| MID_MONITORING | MONITOR_TEMP, MONITOR_VISUAL, MONITOR_RATE, DETECT_CHANNELING | 11.0% | MONITORING {c,h} |
| MID_ENERGY | ADJUST_HEAT | 6.7% | ENERGY {k,l} |
| MID_STABILITY | COOL_CONDENSER, REPLENISH_WATER | 4.8% | STABILITY {e} |
| MID_CLOSURE | DETECT_ENDPOINT, COLLECT_FRACTION, COHOBATE | 9.8% | CLOSURE {d,y} |
| MID_STRUCTURAL | AGITATE, MANAGE_PRESSURE, SEAL_JOINTS | 2.1% | STRUCTURAL {o,p} |

### PC Structure (11-feature model)

- PC1 (24.4%): STORAGE vs PREPARATION+POSTPROCESS — procedure length/complexity
- PC2 (19.6%): MID_MONITORING+MID_STRUCTURAL vs MID_ENERGY+MID_STABILITY — **monitoring vs regulation trade-off within MIDPROCESS**
- PC3 (16.9%): MID_STABILITY vs MID_ENERGY+DISTILLATION — thermal management mode
- PC4 (11.9%): MID_CLOSURE vs COLLECTION+PREPARATION — endpoint complexity
- PC5 (8.7%): PRETREATMENT+MID_STRUCTURAL — material conditioning

### Entropy Overshoot

The 11-feature model slightly overshoots Voynich entropy (2.921 vs 2.660), consistent with:
1. 11 features vs Voynich's 10 (one extra degree of freedom)
2. Sparse sub-types (MID_STRUCTURAL = 2.1%) adding noise variance
3. The Voynich's axes being better integrated than crude action-level coding

---

## Interpretation

The full dimensional story is now:

1. **Brunschwig (3 PCs):** Recipe specification — what materials, what preparation, what distillation mode. MIDPROCESS entirely absent (tacit knowledge).
2. **Modern 7-phase (4 PCs):** Adds process control as a single lumped dimension (MIDPROCESS = 34.5% of actions). The 4th PC is "whether you monitor."
3. **Modern 11-feature (5 PCs):** Differentiates types of process control — monitoring vs energy regulation vs stability management vs endpoint detection. The 5th PC is "how you parameterize monitoring for this specific material."
4. **Voynich (5 PCs):** Matches the 11-feature model. Its 7 operational axes (ENERGY, STABILITY, MONITORING, ITERATION, CLOSURE, STRUCTURAL, FREE) directly encode the same sub-type differentiation within process control.

The Voynich is not a recipe book (Brunschwig), not a general SOP (7-phase modern), but a parameterized process control manual where each folio specifies the full control parameter set for a specific material.

---

## Method

- Same 20 modern procedures as C1222
- Split 13 MIDPROCESS action types into 5 Voynich-aligned sub-types
- Expanded feature matrix: 20 procedures × 11 features (6 non-MIDPROCESS + 5 sub-types)
- StandardScaler → PCA, compared against 7-phase PCA and Voynich reference

**Script:** `phases/MODERN_DISTILLATION_DIMENSIONAL_COMPARISON/scripts/midprocess_subtype_test.py`
**Results:** `phases/MODERN_DISTILLATION_DIMENSIONAL_COMPARISON/results/midprocess_subtype_test.json`
