# C1224: Voynich Axis Distribution Transforms Plant Distillation Profiles

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** PLANT_DISTILLATION_PROFILE_MATCHING (Phase 436)
**Extends:** C1207 (atom correlation clusters), C1222/C1223 (modern distillation dimensional match)
**Related:** C120 (PURE_OPERATIONAL), C179 (4 stable regimes)

---

## Statement

Voynich folio operational profiles (82 folios × 7 atom axes) have the same PCA dimensionality as plant distillation profiles (35 plants × 7 axes) — both require 4 PCs for 80% variance with near-identical entropy (2.314 vs 2.369 bits). However, the axis proportions are dramatically different: the Voynich inflates ITERATION 7.0× (25.2% vs 3.6%) and CLOSURE 1.4× (20.0% vs 14.3%) while deflating FREE 6.5× (2.9% vs 18.9%) and MONITORING 2.3× (7.8% vs 18.1%). PC alignment between the two spaces is not significant (p=0.48). The Voynich does not encode plant distillation profiles directly — it encodes the *control program structure* for distillation, transforming process requirements into loop/termination grammar.

### Axis Distribution Comparison

| Axis | Plants | Folios | Ratio | Interpretation |
|------|--------|--------|-------|----------------|
| ITERATION | 3.6% | **25.2%** | **7.0×** | Loop/cycle counting infrastructure |
| CLOSURE | 14.3% | **20.0%** | 1.4× | Termination conditions |
| STABILITY | 15.8% | 18.7% | 1.2× | ~balanced |
| ENERGY | 18.0% | 15.0% | 0.8× | ~balanced |
| STRUCTURAL | 11.2% | 10.4% | 0.9× | ~balanced |
| MONITORING | 18.1% | **7.8%** | **0.43×** | Observation compressed |
| FREE | 18.9% | **2.9%** | **0.15×** | Timing flexibility eliminated |

### PCA Dimensionality

| Metric | Plants | Folios |
|--------|--------|--------|
| n_for_80% | 4 | 4 |
| Entropy (bits) | 2.369 | 2.314 |
| PC alignment p-value | — | 0.48 (NS) |

### Category × Regime Association

82% of folios map nearest to FLOWER category, 17% to ROOT. REGIME_1 (ENERGY-heavy) captures 13/14 ROOT-matching folios. ROOT matches concentrate in Section B (BIO), FLOWER in Sections H (HERBAL) and S (STAR).

| Regime | FLOWER | ROOT | WOOD |
|--------|--------|------|------|
| REGIME_1 | 18 | 13 | 1 |
| REGIME_2 | 15 | 0 | 0 |
| REGIME_3 | 20 | 0 | 0 |
| REGIME_4 | 14 | 1 | 0 |

Category adds 8.1% of variance beyond section (partial R² = 0.081).

---

## Interpretation

The Voynich system transforms plant distillation requirements through a control-program encoding that:

1. **Massively inflates ITERATION** — The {a,i,n,r} atoms (25.2%) encode the cycling, counting, and loop structure needed to control distillation. Real distillation has few cycles (most plants are single-pass) but a control program must specify WHEN to cycle, HOW MANY times, and WHAT terminates the loop.

2. **Massively deflates FREE** — Timing flexibility (2.9%) is nearly eliminated. A control program specifies rigid sequences, not "whenever convenient." This is consistent with C120 (PURE_OPERATIONAL): tokens are state-triggered interventions, not flexible guidelines.

3. **Deflates MONITORING** — Observation (7.8%) is compressed because monitoring is implicit in the control loop. You don't need to SAY "watch the temperature" when the program structure already specifies the monitoring interval and response conditions.

4. **Preserves ENERGY, STABILITY, STRUCTURAL** — The physical parameters of distillation (heat, cooling, apparatus) map through approximately unchanged, because these ARE the control variables.

This explains why C1222/C1223 showed dimensional MATCH (both 5 PCs) while direct profile matching fails: the Voynich operates in a *transformed* version of the distillation parameter space optimized for control-program representation.

---

## Method

- 35 aromatic plants scored on 7 axes (0-5 scale) from modern distillation literature
- 82 Currier B folios profiled by atom axis proportions (C1207 mapping)
- PCA comparison: T1 (plant PCA), T2 (folio PCA), T3 (PC alignment with 1000-iteration permutation null)
- Distance matching: T4 (nearest plant vs nearest category), T5 (section confound control)

**Script:** `phases/PLANT_DISTILLATION_PROFILE_MATCHING/scripts/plant_profile_matching.py`
**Data:** `phases/PLANT_DISTILLATION_PROFILE_MATCHING/data/plant_profiles.json`
**Results:** `phases/PLANT_DISTILLATION_PROFILE_MATCHING/results/plant_matching_results.json`
