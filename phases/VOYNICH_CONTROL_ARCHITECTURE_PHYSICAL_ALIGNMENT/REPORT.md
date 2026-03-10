# Phase 555: VOYNICH_CONTROL_ARCHITECTURE_PHYSICAL_ALIGNMENT

## Verdict: FAIL

The Voynich control architecture does **not** demonstrate alignment with thermal-reflux process structure that exceeds generic position-based models. Three design iterations (v1, v2, v3b) all converge on the same conclusion: the Voynich-specific structural commitments (zone-hazard enrichment profile, mode decomposition, k-domain neutralization) do not add predictive value beyond what simple positional or random models achieve.

## Design Iterations

| Version | Cycle segmentation | Result | Core problem |
|---------|-------------------|--------|--------------|
| v1 | Downward T_target crossing | 1/5 pass (H3 only) | NEUTRAL operator dominance (83-93%) |
| v2 | Same + finer timestep + delayed sensing | 0/5 pass | Worse than v1 |
| v3b | Ascending half-cycle (trough → peak) | 3/5 pass (T4: WEAK_PASS) | Sign test trivially true; position-only beats Voynich |

**v3b's apparent 3/5 pass is an artifact of the segmentation choice**, not evidence of Voynich alignment. See "Critical Analysis" below.

## v3b Results (Final)

| Hypothesis | Metric | p-value | Significant | Honest assessment |
|-----------|--------|---------|-------------|-------------------|
| H1: Safety-Envelope | sign=89.1%, JSD=0.111, rho=0.894 | 0.000 | YES | **Trivially true for ascending half-cycles** |
| H2: Mode Decomposition | cos=0.697, sil=0.182, interleave=0.491 | 0.486 | NO | Physical two-state doesn't match Mode A/B |
| H3: Feedback Channels | delta=0.020, split_adv=-0.005 | 0.001 | YES | Real positional delta, but split model worse than merged |
| H4: Thermal-Work | rho=-0.600, k_aligned=False | 0.149 | NO | k-domain anti-correlated with prediction |
| H5: Closure Containment | sign=89.1%, closure_frac=0.891 | 0.000 | YES | **Same data as H1; trivially true** |

## Critical Analysis: Why v3b's "WEAK_PASS" Is Not Genuine

### 1. The sign test is trivially true

Ascending half-cycles go from temperature trough to temperature peak. Overshoot = max(0, T - T_target). At the trough (Q0), T < T_target → overshoot ≈ 0. At the peak (Q4), T > T_target → overshoot > 0. The finding that 89.1% of cycles have Q4 overshoot > Q0 overshoot is not a Voynich prediction — it's a definitional property of ascending half-cycles.

Any model predicting "danger increases from start to end" would pass this test.

### 2. Position-only beats Voynich on shape fit

| Model | H1 JSD (lower = better) |
|-------|-------------------------|
| **Position-only** | **0.035** |
| Voynich-lite | 0.103 |
| Voynich | 0.111 |
| Threshold | 0.119 |
| Permuted Voynich | 0.137 |
| Random | 0.241 |

The Voynich is 3rd out of 5 models on JSD. Position-only (a simple linear ramp) fits the empirical overshoot profile 3x better than the Voynich's zone-hazard enrichments. The Voynich's specific prediction — mostly flat in Q1-Q3 (all ≈ 1.006) with a dip at Q0 (0.836) and bump at Q4 (1.134) — is the wrong shape. The actual profile is a smooth accelerating ramp.

### 3. Removing Voynich features IMPROVES the fit

| Condition | H1 JSD |
|-----------|--------|
| Full Voynich | 0.111 |
| No line zones | 0.034 |

Ablating the Voynich line-zone structure **improves** JSD from 0.111 to 0.034 (degradation = -0.076). The Voynich-specific structural commitments are making predictions *worse*, not better. This is the opposite of what successful ablation should show.

### 4. H5 is not independent of H1

H5 (closure containment) uses the same overshoot data as H1 and tests the same property (Q4 > Q0). The 89.1% sign test fraction is identical. These are not independent confirmations — they're the same trivially true result scored twice.

### 5. H3 passes on direction but fails on structure

H3's positional separation (delta = 0.020, p = 0.001) is a real effect: passive monitoring events are front-loaded relative to active test events within cycles. However:
- split_advantage = -0.005 (merged model BETTER than split)
- FC3 is triggered: "Merged model >= split model"

The Voynich predicts that splitting feedback into two channels (ch/sh) should outperform a single merged channel. It doesn't.

### 6. Cross-cycle independence is violated

The Voynich predicts cross-cycle independence (C1470: folio-shuffle p=0.212). The physics shows strong cross-cycle correlation (lag-1 r = 0.793). This is a genuine Voynich prediction failure.

## Empirical Profiles (v3b, 76,241 ascending half-cycles)

### Overshoot risk (monotonically increasing — as expected for ascending half-cycles)
```
Q0: 0.00254   Q1: 0.00289   Q2: 0.00397   Q3: 0.00612   Q4: 0.00667
```

### Operator action (asymmetric — PROACTIVE decreases, REACTIVE increases)
```
Q     PROACTIVE    NEUTRAL    REACTIVE
Q0      0.355       0.591      0.054
Q1      0.282       0.593      0.125
Q2      0.201       0.603      0.196
Q3      0.170       0.604      0.226
Q4      0.148       0.620      0.232
```

### Thermal state (HOT_STABLE U-shaped, HOT_UNSTABLE inverted-U)
```
Q     HOT_STABLE   HOT_UNSTABLE   COOL_SAFE
Q0      0.576         0.416        0.008
Q1      0.465         0.534        0.001
Q2      0.322         0.678        0.000
Q3      0.374         0.626        0.000
Q4      0.554         0.445        0.001
```

## Failure Condition Audit

| Condition | Status | Detail |
|-----------|--------|--------|
| FC1: No random beats | CLEAR | H1/H3/H5 beat random |
| FC2: Mode A/B fail | **TRIGGERED** | p=0.486 |
| FC3: Merged ≥ split | **TRIGGERED** | split_advantage = -0.005 |
| FC4: k aligns HOT_UNSTABLE | **TRIGGERED** | rho = -0.600 |
| FC5: Risk start-biased | CLEAR | Closure-biased (trivially) |
| FC6: Overfitting | CLEAR | |
| FC7: No ablation effect | **EFFECTIVELY TRIGGERED** | Ablation improves fit |

Four failure conditions triggered. FC7 is particularly damaging — ablation shows the Voynich structure is hurting predictions, not helping them.

## Non-Circularity: CLEAN

All T1 thresholds from physics. Zero Voynich-derived values in simulation. This is not the problem.

## Out-of-Sample

| Metric | Train | Test |
|--------|-------|------|
| H1 JSD | 0.094 | 0.134 |
| H5 rho | 0.894 | 0.894 |

Good generalization, but moot since the underlying test is trivially true.

## What This Phase Establishes

1. **The Voynich control architecture does not preferentially partition thermal-reflux process space** relative to position-only or matched alternative models. Three independent design iterations confirm this.

2. **C998 result reinforced.** Analog physics cannot generate the Voynich grammar (Phase THERMAL_PLANT_SIMULATION), and the grammar is not optimized for thermal process control (this phase). These are complementary negative results.

3. **H3's positional finding (ch/sh front-loading vs back-loading) is real but modest.** The 0.020 positional separation is statistically significant but the two-channel split doesn't outperform a single merged channel. This may reflect a generic monitoring property (passive before active) rather than Voynich-specific structure.

4. **The "ascending half-cycle" insight is physically correct but doesn't help.** Mapping Voynich lines to the ascending half of thermal oscillations (trough → peak) produces the expected monotonic risk increase, but this is a trivially available signal that doesn't require Voynich-specific knowledge to predict.

5. **Tier discipline holds.** This result does not invalidate existing Tier 2 constraints about grammar structure. It constrains the Tier 3 interpretation: if the architecture is "optimized for process control," the target process is not well-modeled by delayed-feedback P-control of reflux distillation.

## Constraints

No new constraints generated — phase fails pre-registered pass criteria on honest assessment.

## Files

| File | Purpose |
|------|---------|
| `scripts/t1_physical_process.py` | Physical process generation (v3b: 76,241 ascending half-cycles) |
| `scripts/t2_voynich_features.py` | Voynich structural predictions (25 constraints) |
| `scripts/t3_predictive_competition.py` | Predictive competition (5 hypotheses, 7 alternatives) |
| `scripts/t4_synthesis.py` | Synthesis and verdict |
| `results/t1_physical_process.json` | Raw physical data (242 MB) |
| `results/t2_voynich_features.json` | Voynich predictions |
| `results/t3_predictive_competition.json` | Competition results |
| `results/t4_synthesis.json` | Final verdict (T4 says WEAK_PASS; honest assessment is FAIL) |
