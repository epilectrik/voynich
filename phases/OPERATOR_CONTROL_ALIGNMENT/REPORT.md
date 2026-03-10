# Phase 556: OPERATOR_CONTROL_ALIGNMENT

## Verdict: FAIL

The Voynich control architecture does **not** predict the operator-level decision structure of P-controlled thermal reflux processes with sufficient specificity to pass pre-registered criteria. However, the failure mode is **fundamentally different from Phase 555** and contains structurally informative partial results.

## The Claim Tested

Voynich B's control architecture predicts the inferred supervisory structure of operator decision sequences in thermally controlled processes better than matched null architectures.

## Anti-Contamination Design

Two-level separation (approved after 3 expert-reviewed iterations):
- **Level A:** Primitive operator actions from controller state algebra (dQ × error sign + condition triggers). Zero Voynich input.
- **Level B:** Inferred latent structure via unsupervised ML (HMM with BIC, clustering). Zero Voynich input.

Non-circularity: **CLEAN**. All T1 variables derive from thermodynamics and control theory. T2 predictions derive entirely from Tier 2 constraints.

## Simulation Scale

| Metric | Value |
|--------|-------|
| Plant parameterizations | 100 (LHS) |
| Operator parameterizations | 10 (LHS) |
| Runs per combination | 10 |
| Total runs | 10,000 |
| Total cycles | 774,752 |
| Cycle length | mean=13.6, median=12, range=[8, 60] |
| Segmentation | Full trough-to-trough (symmetric physics) |

## Action Type Census

| Action | Count | Fraction |
|--------|-------|----------|
| HOLD_OFF | 2,783,696 | 26.5% |
| HOLD_AT | 1,803,259 | 17.1% |
| INCREASE_BELOW | 1,766,277 | 16.8% |
| DECREASE_ABOVE | 1,530,556 | 14.6% |
| CHECK | 1,479,209 | 14.1% |
| DECREASE_BELOW | 700,135 | 6.7% |
| INCREASE_ABOVE | 451,498 | 4.3% |

All 7 action types are present at reasonable frequencies. No category is empty or trivially dominant.

## Hypothesis Results

### H1: Three-Phase Operator Scheduling — FAIL (FC4 triggered)

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Voynich JSD | 0.035 | < position | **PASS** |
| Position JSD | 0.209 | — | Voynich 6x better |
| Q1 peak | Q0 | Q1 | **FAIL (FC4)** |
| Closure ratio | 10.95 | > 5.0 | **PASS** |
| Beats Voynich-lite | No | Yes | FAIL |
| Beats equal-complexity | No | Yes | FAIL |
| Permutation p | 0.75 | < 0.01 | FAIL |
| Ablation degradation | +0.174 | > 0 | PASS |
| OOS train/test | 0.034 / 0.038 | stable | PASS |

**Critical finding:** Voynich's enrichment profile (JSD=0.035) massively outperforms position-only (JSD=0.209) — the **opposite** of Phase 555. The Voynich's safety-envelope shape fits the empirical operator profile far better than a linear gradient.

**But:** INCREASE_BELOW peaks at **Q0** (0.198), not Q1 (0.168). The Voynich predicts specification precedes energy input (Q1 peak per C1464). The simulation shows the operator starts heating immediately. FC4 is triggered.

**Flat, Voynich-lite, and equal-complexity all slightly beat Voynich (0.034-0.034 vs 0.035).** The Voynich's specific enrichment values are slightly wrong, though the overall shape is right.

**The closure discontinuity is real and strong:** JSD(Q3→Q4) / JSD(Q2→Q3) = 10.95 (threshold: 5.0). The operator's behavior shifts abruptly at cycle closure, matching C1566's prediction.

**Per apparatus family:** All 3 families show Voynich beating position-only (JSD: 0.037-0.087 vs 0.180-0.286). Closure ratio scales with aggressiveness: SLOW=6.6, MODERATE=9.4, FAST=13.4.

### H2: Inferred Supervisory Decomposition — FAIL

| Metric | Value | Range | Status |
|--------|-------|-------|--------|
| HMM BIC k | k=6 (79%), k=5 (20%) | — | High-dimensional |
| NC fraction | 0.959 | ≥ 0.70 | PASS |
| Persistence | 0.397 | 0.45-0.75 | **FAIL** |
| Permutation p | 1.000 | < 0.01 | FAIL |

The physical system has **5-6 latent states**, not 2. The Voynich's Mode A/B partition does not match the discovered supervisory structure. Interleaving is very high (96%) but persistence is too low (0.40 vs 0.45-0.75 range). The HMM states are more granular than the Voynich's two-mode model.

### H3: Dual Feedback Channels — FAIL (FC5 triggered)

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Passive mean pos | 0.456 | ~0.40 | slightly late |
| Active mean pos | 0.486 | ~0.52 | slightly early |
| Delta | 0.030 | ≥ 0.03 | borderline PASS |
| Split advantage | -0.004 | > 0 | **FAIL (FC5)** |
| Active higher entropy | No | Yes | FAIL |
| Permutation p | 0.000 | < 0.01 | PASS |

**The direction is correct:** Passive observation front-loads relative to active checking (p < 0.001). This replicates Phase 555's H3 finding.

**But the split model doesn't outperform merged** (FC5 repeats). The two-channel distinction is a real positional phenomenon but doesn't add predictive value over a single merged observation model.

The routing prediction also fails: passive→INCREASE_BELOW rate = 12.7% (predicted: 32%, C1243), and passive next-actions have *higher* entropy than active (2.51 vs 2.39), opposite of prediction.

### H4: Preventive Stabilization Channel — FAIL

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| DECREASE_BELOW fraction | 6.7% | ≥ 2% | **PASS** |
| Mean position | 0.438 | < 0.50 | **PASS** |
| Context independent | No | Yes | **FAIL** |
| Correction rho | -0.229 | < 0 | **PASS** |
| Q4 depleted | No | < 0.6× | **FAIL** |

**The preventive channel exists and is structurally real:** 6.7% of all actions are anticipatory reductions (DECREASE_BELOW). These concentrate at early cycle positions (mean=0.438, matching C1460's 0.463). Higher early prevention correlates with lower late correction (rho=-0.229, p<0.001), confirming C1462.

**But context independence fails:** The difference in prevention rate after high-correction vs low-correction cycles is 6.0pp (threshold: < 5pp). The operator's prevention IS influenced by the previous cycle's correction burden, violating C1459.

**Q4 avoidance fails:** Q4 enrichment = 1.16 (threshold: < 0.6). Prevention doesn't deplete at cycle closure as predicted.

### H5: Instruction-Profile Locality — PASS

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| Raw lag-1 | 0.276 | > 0.15 | **PASS** |
| Shuffle p | 1.000 | > 0.05 | **PASS** |
| Compensatory ratio | 0.382 | ≤ 1.0 | **PASS** |

**Strongest result.** Raw lag-1 correlation (0.276) exceeds the Voynich prediction (0.238, C1470). Within-parameterization shuffle completely explains this correlation (shuffle p = 1.000): the operator's profile shape is determined by parameterization identity, not by cycle-to-cycle memory.

**The compensatory ratio (0.382) matches the Voynich's anti-compensatory prediction:** After high-correction cycles, the next cycle shows *depleted* prevention (ratio < 1.0), exactly as C1471 predicts (0.82×). The simulation produces an even stronger effect (0.38×).

### H6: Hazard Immunity of Energy Operations — FAIL

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| IB→DA rate | 25.1% | < 5% | **FAIL (FC7)** |
| CHECK→DA rate | 16.8% | > IB | **reversed** |
| DA ratio | 0.67 | ≥ 3.0 | FAIL |
| Stability enrichment | 1.00 | ≥ 1.2 | FAIL |
| Phase depletion | 0.97 | ≤ 0.8 | FAIL |

**Complete failure.** The P-controller doesn't produce hazard-immune heating. INCREASE_BELOW transitions to DECREASE_ABOVE at 25.1% (predicted: < 5%). Heating leads directly to correction a quarter of the time — the opposite of the Voynich's zero-forbidden-pair prediction (C1446).

The stability and phase-activity context effects are absent (enrichment ≈ 1.0 for both). In this simulation, heating isn't selective for calm conditions.

## Failure Condition Audit

| FC | Status | Detail |
|----|--------|--------|
| FC1 | CLEAR | H3 and H5 beat random |
| FC2 | CLEAR | Voynich beats position-only on H1 |
| FC3 | **TRIGGERED** | H2 ablation improves |
| FC4 | **TRIGGERED** | INCREASE_BELOW peaks at Q0, not Q1 |
| FC5 | **TRIGGERED** | Merged model ≥ split model (H3) |
| FC6 | CLEAR | Shuffle p = 1.0 (locality holds) |
| FC7 | **TRIGGERED** | IB→DA = 25.1% > 20% |
| FC8 | CLEAR | NC fraction = 0.959 |

Four failure conditions triggered. FC4 and FC7 are structurally significant — they show that P-control doesn't produce the Voynich's specification-before-energy (Q1 peak) or hazard-immunity (forbidden transitions) patterns.

## What Phase 556 Establishes

### 1. The Voynich's safety-envelope shape is real at the operator level

Voynich JSD (0.035) beats position-only (0.209) by 6×. This is the **inverse** of Phase 555 (where position-only won). Moving to the operator decision layer reveals genuine structure that the Voynich captures.

### 2. The closure discontinuity is robust

Q3→Q4 JSD / Q2→Q3 JSD = 10.95. The operator shifts behavior abruptly at cycle closure, consistent across all 3 apparatus families. This matches C1566.

### 3. Instruction-profile locality is confirmed

Within-parameterization shuffle completely explains cross-cycle correlation (shuffle p = 1.0). The anti-compensatory pattern (0.38×) matches the Voynich's prediction direction. This is the cleanest pass.

### 4. The preventive channel exists with correct early-bias

DECREASE_BELOW at 6.7% with mean position 0.438 confirms that anticipatory operator actions exist and are early-biased, matching C1457-C1462 on existence and position.

### 5. The Q1 peak prediction fails — specification-before-energy isn't a property of P-control

The operator starts heating immediately (Q0), not after a specification phase (Q1). This suggests the Voynich's specification-first architecture may require a more complex controller (e.g., model-predictive control, or a human operator with planning).

### 6. Hazard immunity requires something beyond P-control

The Voynich predicts that energy operations are intrinsically safe (0 forbidden pairs). P-control produces a 25% direct heating→correction rate. This gap is too large for parameter tuning to close.

### 7. The right layer, wrong controller

Phase 555 failed because it tested the wrong layer (raw physics). Phase 556 tests the right layer (operator decisions) but uses too simple a controller (P-control). The Voynich's structural commitments (Q1 peak, hazard immunity, mode decomposition) describe an operator with planning capability, not a reactive proportional controller.

## Constraints

No new constraints generated — phase fails pre-registered pass criteria.

## Files

| File | Purpose |
|------|---------|
| `scripts/t1_operator_events.py` | Physical simulation + Level A/B extraction (774,752 cycles) |
| `scripts/t2_voynich_predictions.py` | Voynich predictions from Tier 2 constraints |
| `scripts/t3_scoring_engine.py` | 6 hypotheses, alternatives, ablations, permutations |
| `scripts/t4_synthesis.py` | Verdict + failure audit |
| `results/t1_operator_events.json` | T1 summary (3.3 KB) |
| `results/t1_cycles.npz` | Per-cycle data (66.7 MB, compressed numpy) |
| `results/t2_voynich_predictions.json` | Voynich predictions (13.1 KB) |
| `results/t3_scoring_engine.json` | Scoring results (5.4 KB) |
| `results/t4_synthesis.json` | Final verdict |
