# C1380: Apparatus Profile Partially Explains AXM Residual

**Tier:** 2
**Scope:** B
**Phase:** PARALLEL_MONITORING_TRACKS (Phase 494)
**Date:** 2026-03-02

## Statement

Apparatus profile similarity predicts AXM self-transition residual similarity (Mantel r=0.224, p=0.002, 5K permutations). Folios with the same dominant apparatus type cluster in residual space (eta²=0.083, p=0.034). The signal is also present without section residualization (raw Mantel r=0.243, p=0.0002). Apparatus parameterization accounts for ~8% of what C1169 classified as irreducible design freedom. The remaining ~92% is still genuinely free.

## Hypothesis Tested

The ~27% irreducible AXM residual (C1169) was declared "genuine design freedom" after a 5-test exhaustive battery found zero signal from 23 candidate predictors. But that battery tested univariate regression and random forest on individual variables — not pairwise similarity. If the residual reflects input parameterization (apparatus configuration fed into the program), folios with similar apparatus profiles should have similar residuals even though no single apparatus variable predicts residual magnitude.

## Evidence

### T3: Mantel Test (apparatus distance ~ residual distance) — PASS
- Mantel r = 0.224, p = 0.0016 (5,000 permutations)
- Null mean = -0.001, null std = 0.064
- 82 folios, 3,321 pairwise distances
- Apparatus distance: Euclidean over 5 profile scores (DISTILLATION, SEALED_VESSEL, SUSTAINED_HEAT, PRECISION, DIRECT_FIRE)
- Residual: section-mean-adjusted category self-transition rate

### T4: Within vs Between Apparatus Group — PASS
- Dominant groups: DISTILLATION (39), SEALED_VESSEL (19), PRECISION (14), SUSTAINED_HEAT (9), DIRECT_FIRE (1)
- Total residual variance: 0.001847
- Within-group variance: 0.001694
- Eta-squared: 0.083, permutation p = 0.034

### Per-group residual means
| Group | Mean Residual | Std | n | Interpretation |
|-------|--------------|-----|---|----------------|
| SEALED_VESSEL | +0.022 | 0.058 | 19 | More self-repetitive (waiting/checking) |
| PRECISION | +0.012 | 0.041 | 14 | Moderately repetitive |
| DISTILLATION | -0.011 | 0.029 | 39 | More varied sequences |
| SUSTAINED_HEAT | -0.018 | 0.031 | 9 | Most varied (active cycling) |

### T5: Raw Mantel (no section residualization) — PASS
- Mantel r = 0.243, p = 0.0002
- Confirms signal is not an artifact of section adjustment

## Why C1169 Missed This

C1169's 5-test battery was thorough but tested a different question: "does any single variable predict residual magnitude?" (univariate scan + random forest). The answer was correctly no. This test asks: "do folios with similar apparatus configurations have similar residuals?" — a pairwise similarity question that regression cannot detect when the effect is multivariate (the 5-dimensional profile matters, not any single marker).

## Interpretation

Part of what appears to be free authorial variation is actually determined by the apparatus specification. Sealed-vessel operations produce more self-repetitive programs (more same-category transitions) because the operator repeatedly checks the same thing while waiting. Active distillation produces more varied sequences because the operator cycles through different actions. The program dynamics partially reflect what the apparatus demands, not just what the author chose.

This is consistent with the "input parameterization" model: the manuscript's programs are generated from specifications that include apparatus type, and the apparatus type influences the resulting transition dynamics.

## Qualifies

- C1169 (AXM residual closed, genuine design freedom) — qualified: ~8% of residual is apparatus-parameterized, ~92% remains free
- C1035 (AXM residual irreducible) — qualified: irreducible to univariate predictors, but pairwise apparatus similarity has signal
- C1248 (apparatus marker co-occurrence) — extended: apparatus profiles predict not just vocabulary but dynamics
- C1249 (section apparatus diversity) — converges: Section H's apparatus diversity explains its higher residual variance (noted in C1169 Test 4)

## Method

- 82 Currier B folios, 23,096 tokens
- Category self-transition rate per folio (8 operational categories, C1250)
- Residuals from section-mean baseline
- Apparatus profiles: 5 dimensions from C1248 marker MIDDLEs (per-folio token fraction)
- Mantel test: Pearson correlation between pairwise distance matrices, 5,000 permutations
- Eta-squared: within vs between dominant apparatus group, 5,000 permutations

## Provenance

- Script: `phases/PARALLEL_MONITORING_TRACKS/scripts/design_freedom_apparatus_test.py`
- Results: `phases/PARALLEL_MONITORING_TRACKS/results/design_freedom_apparatus_test.json`
- Depends: C1035, C1169, C1247, C1248, C1249, C1250

## Status

CONFIRMED — Apparatus profile predicts residual similarity (Mantel r=0.224, p=0.002). C1169's "genuine design freedom" is ~92% correct; ~8% is apparatus parameterization.
