# C1038: AXM Runs Converge — Within-Run Entropy Decreases Monotonically, Micro-Sequential Dynamics Do Not Decompose the Residual

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** AXM_RUN_MICROSEQUENCE (Phase 360)
**Extends:** C1035 (57% residual irreducible), C1036 (exit pathways frequency-neutral), C1037 (class composition redundant)
**Strengthens:** C458 (design freedom confirmed), C980 (free variation envelope confirmed), C978 (mixing time), C1007 (gatekeeper enrichment), C1024 (MIDDLE asymmetry validated)
**Relates to:** C1006 (AXM dwell dynamics), C969 (CMI), C1010 (6-state partition), C1016 (folio archetypes)

---

## Statement

Conditional transition entropy within AXM macro-state runs decreases monotonically from H=3.84 bits (position 1) to H=2.52 bits (position 6), with slope=-0.248 bits/position and accelerating curvature=-0.036. As runs extend, class repertoire narrows — consistent with gatekeeper exit boundary enrichment (C1007) and hub-and-spoke mixing (C978). This convergence rate is uniform across folios (not archetype-differentiated, ANOVA p=0.117) and does NOT predict C1017's AXM self-transition residual (incremental LOO R² = -0.096). Entropy convergence is a grammar-level invariant, not a program-specific parameter.

Three micro-sequential measures were tested for residual prediction: entropy gradient, per-folio MIDDLE asymmetry (JSD), and per-folio conditional mutual information (CMI). After sample-size control, all three collapse to noise. JSD and CMI are heavily confounded with transition count (JSD vs log(N): rho=-0.675; CMI vs log(N): rho=+0.499), and log(N) itself correlates with the residual (rho=+0.394). After residualizing against sample size: JSD-residual rho drops from -0.295 to -0.149 (p=0.279); CMI-residual rho drops from +0.237 to +0.082 (p=0.552). No micro-sequential feature survives size control.

This completes a four-phase elimination of C1035's 57% irreducible AXM self-transition residual. The residual is the design freedom space predicted by C458 (recovery freedom CV=0.72-0.82) and C980 (66.3% free variation envelope).

---

## Evidence

### S1: AXM Run Statistics

| Metric | Value |
|--------|-------|
| Folios passing threshold | 55 (of 72 with C1035 data) |
| Total AXM runs (length >= 2) | 2,383 |
| Total within-run bigrams | 6,054 |
| Mean run length | 3.54 tokens |
| Median run length | 3.0 |
| Max run length | 13 |
| Q75 run length | 4 |

Threshold: >= 30 within-run bigrams per folio. 17 folios excluded (predominantly low AXM self-transition folios). C1017 baseline on 55 folios: train R²=0.575, LOO R²=0.307.

### S2: Entropy Convergence (Primary Finding)

| Position | H (bits) | N transitions |
|----------|----------|---------------|
| 1 | 3.8445 | 2,383 |
| 2 | 3.6553 | 1,503 |
| 3 | 3.5024 | 960 |
| 4 | 3.2824 | 584 |
| 5 | 3.0427 | 341 |
| 6 | 2.5191 | 155 |

Corpus slope: -0.248 bits/position. Curvature: -0.036 (accelerating convergence).

Per-folio: slope mean=-0.268, std=0.141. Valid positions per folio: mean=4.5.

ANOVA by archetype: F=1.946, p=0.117, eta²=0.135 — convergence rate does NOT differ by archetype.

### S3: Per-Folio MIDDLE Asymmetry (JSD)

Corpus weighted JSD = 0.0657 bits (validates C1024's 0.070 bits within-AXM-run scope). Per-folio JSD heavily inflated by sparsity: mean=0.449 (only 7.1 classes computed per folio at MIN_CLASS_COUNT=5).

Raw: JSD mean vs residual rho=-0.295, p=0.029. Incremental LOO R²=+0.037.

### S4: Per-Folio CMI

Per-folio CMI: mean=1.696 bits, std=0.300. Permutation test (200 runs, pool all runs across folios, reassign to pseudo-folios): p=0.455. CMI variance does NOT exceed random partitioning.

Raw: CMI vs residual rho=+0.237, p=0.081. Incremental LOO R²=+0.164.

### S10: Sample-Size Control (DECISIVE)

| Confound test | rho | p |
|---------------|-----|---|
| CMI vs log(N_transitions) | +0.499 | 0.0001 |
| JSD mean vs log(N_transitions) | -0.675 | <0.000001 |
| log(N_transitions) vs residual | +0.394 | 0.003 |

After residualizing against sample size:

| Feature | Raw rho / p | Residualized rho / p | Raw incr LOO | Resid incr LOO |
|---------|-------------|---------------------|--------------|----------------|
| JSD mean | -0.295 / 0.029 | -0.149 / 0.279 | +0.037 | -0.042 |
| CMI | +0.237 / 0.081 | +0.082 / 0.552 | +0.164 | +0.009 |

Both signals collapse completely after removing the sample-size confound. The raw correlations were artifacts of: (a) finite-sample estimator bias in JSD and CMI, (b) correlation between sample size and the target variable.

Without CMI (entropy + JSD only): incremental LOO R² = -0.052. The micro-sequential stratum adds nothing.

---

## Interpretation

### 1. Entropy convergence is a grammar-level invariant

The monotonic entropy decrease within AXM runs reflects the grammar's structure: early transitions explore the full 32-class AXM space, but as runs extend, the system narrows to a smaller class vocabulary — predominantly gatekeeper and high-frequency kernel classes. This is consistent with:
- C978 (mixing time 1.1 tokens): fast mixing means broad initial exploration
- C1007 (gatekeeper enrichment 2-10x at exits): extended runs converge toward exit-boundary classes
- C1006 (Weibull dwell shape k=1.55): increasing exit hazard with run length implies fewer "escape-free" class options at depth

The convergence rate is NOT program-specific (ANOVA p=0.117). Every program converges the same way because the grammar's transition structure is shared.

### 2. Micro-sequential dynamics are not a separate stratum

All three measures (entropy gradient, JSD, CMI) either reflect grammar-level properties (entropy convergence) or are sample-size artifacts (JSD, CMI). The micro-sequential stratum is empty — it contains no information about program-specific design that isn't already captured by composition and transition rates.

### 3. The four-phase elimination is complete

| Phase | Stratum tested | Result |
|-------|---------------|--------|
| 357 (C1035) | Aggregate folio statistics | 0/7 pass, all dR² < 0.013 |
| 358 (C1036) | AXM boundary transitions | Frequency-proportional CV |
| 359 (C1037) | Within-AXM class composition | Redundant (+0.005 LOO incr) |
| 360 (C1038) | Micro-sequential dynamics | Size artifacts, entropy convergence is grammar-level |

The 57% residual is confirmed irreducible. It matches C458's prediction (recovery freedom) and C980's prediction (66.3% free variation envelope). The residual IS the design freedom space — each program is independently parameterized within the grammar's constraints.

---

## Pre-registered prediction outcomes

| # | Prediction | Result | Pass |
|---|-----------|--------|------|
| P1 | Entropy gradient predicts residual (LOO incr R² > 0.02) | incr = -0.096 | FAIL |
| P2 | JSD features predict residual (LOO incr R² > 0.02) | incr = +0.037 (raw), -0.042 (size-controlled) | FAIL* |
| P3 | Per-folio CMI variance exceeds permutation null (p < 0.01) | p = 0.455 | FAIL |
| P4 | Combined features predict residual (LOO incr R² > 0.02) | incr = +0.153 (raw), driven by CMI artifact | FAIL* |
| P5 | Curvature differs by archetype (ANOVA p < 0.01) | p = 0.186 | FAIL |
| P6 | JSD CV > composition CV | 0.283 < 1.048 | FAIL |

*P2 and P4 passed the raw threshold but failed after sample-size control (S10). Adjusted verdict: 0/6 pass.

Global decision rule: all three residual-prediction measures < 0.01 after size control → MICROSEQUENCE_STRATUM_EMPTY.

---

## Method

- 55 B folios with >= 30 within-AXM-run class bigrams (C1010 6-state partition)
- AXM run extraction: maximal consecutive AXM-state class sequences within lines (runs of length >= 2)
- Entropy gradient: pool all transitions at each position depth across runs per folio, compute H(class_t | class_{t-1}), fit linear slope. Cap at position 6.
- MIDDLE asymmetry: per-folio 32x32 forward/reverse class transition matrices from within-run bigrams, per-class JSD (forward vs reverse), extract mean/variance/skewness
- CMI: per-folio I(class_t ; class_{t-2} | class_{t-1}) from within-run trigrams
- CMI permutation null: pool all runs, randomly reassign to pseudo-folios (200 permutations), compute CMI variance
- Sample-size control: regress JSD/CMI against log(N_transitions), use residualized values for prediction
- Miller-Madow bias correction for CMI (diagnostic, confirms artifact)
- OLS + LOO CV for residual prediction, incremental R² over C1017 baseline

**Script:** `phases/AXM_RUN_MICROSEQUENCE/scripts/axm_run_microsequence.py`
**Results:** `phases/AXM_RUN_MICROSEQUENCE/results/axm_run_microsequence.json`

---

## Verdict

**MICROSEQUENCE_STRATUM_EMPTY**: Micro-sequential dynamics within AXM runs do not decompose C1035's 57% irreducible residual. The one genuine finding — monotonic entropy convergence (3.84 → 2.52 bits, slope -0.248) — is a grammar-level invariant shared by all programs, not a program-specific parameter. Apparent JSD and CMI signals collapse after sample-size control (JSD rho: -0.295 → -0.149; CMI rho: +0.237 → +0.082). This completes a four-phase elimination (C1035/C1036/C1037/C1038) confirming the residual as genuine design freedom, consistent with C458 (recovery freedom) and C980 (66.3% free variation envelope).
