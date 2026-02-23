# C1224: Voynich Axis Distribution Transforms Plant Distillation Profiles

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** PLANT_DISTILLATION_PROFILE_MATCHING (Phase 436)
**Extends:** C1207 (atom correlation clusters), C1222/C1223 (modern distillation dimensional match)
**Related:** C120 (PURE_OPERATIONAL), C179 (4 stable regimes), C855/C862 (paragraphs as programs)

---

## Statement

Voynich paragraph operational profiles (479 paragraphs x 7 atom axes) have the same PCA dimensionality as plant distillation profiles (35 plants x 7 axes) -- both require 4 PCs for 80% variance (entropy: 2.451 vs 2.369 bits). However, the axis proportions are dramatically different: the Voynich inflates ITERATION 7.0x (25.1% vs 3.6%) and CLOSURE 1.3x (18.0% vs 14.3%) while deflating FREE 6.3x (3.0% vs 18.9%) and MONITORING 2.3x (7.9% vs 18.1%). PC alignment between the two spaces is not significant (p=0.30). The Voynich does not encode plant distillation profiles directly -- it encodes the *control program structure* for distillation, transforming process requirements into loop/termination grammar.

**Unit correction:** Analysis uses paragraphs as the comparison unit (C855, C862: paragraphs are independent mini-programs). The ITERATION inflation is stable across units (25.1% paragraph vs 25.2% folio), confirming it is a real transformation property, not an aggregation artifact.

### Axis Distribution Comparison

| Axis | Plants | Paragraphs | Ratio | Interpretation |
|------|--------|------------|-------|----------------|
| ITERATION | 3.6% | **25.1%** | **7.0x** | Loop/cycle counting infrastructure |
| CLOSURE | 14.3% | **18.0%** | 1.3x | Termination conditions |
| STABILITY | 15.8% | 19.9% | 1.3x | ~balanced |
| ENERGY | 18.0% | 14.9% | 0.8x | ~balanced |
| STRUCTURAL | 11.2% | 11.2% | 1.0x | Exact match |
| MONITORING | 18.1% | **7.9%** | **0.4x** | Observation compressed |
| FREE | 18.9% | **3.0%** | **0.2x** | Timing flexibility eliminated |

### PCA Dimensionality

| Metric | Plants | Paragraphs | Folios (comparison) |
|--------|--------|------------|---------------------|
| n_for_80% | 4 | 4 | 4 |
| Entropy (bits) | 2.369 | 2.451 | 2.314 |
| PC alignment p-value | -- | 0.30 (NS) | 0.48 (NS) |

### Category x Regime Association

80% of paragraphs map nearest to FLOWER category, 14% to ROOT, 6% to WOOD. REGIME_1 (ENERGY-heavy) captures 82% (54/66) of ROOT-matching paragraphs. ROOT matches concentrate in Section B (BIO), FLOWER in Sections S (STAR) and H (HERBAL).

| Regime | FLOWER | ROOT | WOOD |
|--------|--------|------|------|
| REGIME_1 | 129 | 54 | 24 |
| REGIME_2 | 32 | 0 | 0 |
| REGIME_3 | 184 | 7 | 5 |
| REGIME_4 | 39 | 5 | 0 |

Category adds 13.9% of remaining variance beyond section (partial R^2 = 0.139, up from 8.1% at folio level). Section alone explains R^2 = 0.129 at paragraph level (vs 0.265 at folio level), confirming paragraphs have more within-section variance than folios.

---

## Interpretation

The Voynich system transforms plant distillation requirements through a control-program encoding that:

1. **Massively inflates ITERATION** -- The {a,i,n,r} atoms (25.1%) encode the cycling, counting, and loop structure needed to control distillation. Real distillation has few cycles (most plants are single-pass) but a control program must specify WHEN to cycle, HOW MANY times, and WHAT terminates the loop. This is stable at both paragraph and folio level, confirming it is intrinsic to the grammar.

2. **Massively deflates FREE** -- Timing flexibility (3.0%) is nearly eliminated. A control program specifies rigid sequences, not "whenever convenient." This is consistent with C120 (PURE_OPERATIONAL): tokens are state-triggered interventions, not flexible guidelines.

3. **Deflates MONITORING** -- Observation (7.9%) is compressed because monitoring is implicit in the control loop. You don't need to SAY "watch the temperature" when the program structure already specifies the monitoring interval and response conditions.

4. **Preserves ENERGY, STABILITY, STRUCTURAL** -- The physical parameters of distillation (heat, cooling, apparatus) map through approximately unchanged, because these ARE the control variables. STRUCTURAL is an exact match (11.2% in both).

This explains why C1222/C1223 showed dimensional MATCH (both 5 PCs) while direct profile matching fails: the Voynich operates in a *transformed* version of the distillation parameter space optimized for control-program representation.

---

## Method

- 35 aromatic plants scored on 7 axes (0-5 scale) from modern distillation literature
- 479 valid Currier B paragraphs (>=15 mapped atoms) profiled by atom axis proportions (C1207 mapping)
- Paragraphs segmented using par_initial token attribute (C855: paragraphs are programs)
- PCA comparison: T1 (plant PCA), T2 (paragraph PCA), T3 (PC alignment with 1000-iteration permutation null)
- Distance matching: T4 (nearest plant vs nearest category), T5 (section confound control)
- Folio-level comparison retained for artifact check (ITERATION stable across units)

**Script:** `phases/PLANT_DISTILLATION_PROFILE_MATCHING/scripts/plant_profile_matching.py`
**Data:** `phases/PLANT_DISTILLATION_PROFILE_MATCHING/data/plant_profiles.json`
**Results:** `phases/PLANT_DISTILLATION_PROFILE_MATCHING/results/plant_matching_results.json`
