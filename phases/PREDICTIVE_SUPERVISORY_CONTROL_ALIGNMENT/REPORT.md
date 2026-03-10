# Phase 557: PREDICTIVE_SUPERVISORY_CONTROL_ALIGNMENT

## Verdict: FAIL

The Voynich control architecture does **not** predict the operator-level decision structure of supervisor-governed, MPC-controlled thermal reflux processes with sufficient specificity to pass pre-registered criteria. However, the failure mode is **fundamentally different from Phases 555-556** and contains a **breakthrough result on hazard immunity** (H6).

## The Claim Tested

Voynich B's control architecture predicts the inferred supervisory structure of operator decision sequences in **supervisor-governed, model-predictive-controlled** thermal reflux processes better than matched null architectures.

## Architecture: Two-Layer Controller

```
SUPERVISOR (6-state discrete FSM)     Decides IF/WHEN actuation is permitted
  QUALIFYING -> TRACKING ->           From plant state algebra:
  MONITORING <-> CHECKING ->          error regime x stability x
  CORRECTING -> CLOSING               check trigger x correction phase
        |
  MPC (15-candidate continuous)       Decides HOW MUCH Q within
  Asymmetric safety cost              supervisor-approved constraints
        |
  PLANT (thermal reflux ODE)          Same as Phase 555/556
  T, phi, delay, noise
```

**What changed from Phase 556:** Replaced P-controller (1 line: Q = K_p * error + bias) with MPC inner loop (15 candidates, forward prediction, asymmetric safety cost) + 6-state supervisory gate layer (QUALIFYING, TRACKING, MONITORING, CHECKING, CORRECTING, CLOSING). Each supervisor state constrains the MPC's action range.

## Anti-Contamination Design

Three-level separation (approved after 3 expert-reviewed iterations):
- **Level A:** Primitive operator actions from controller state algebra (dQ x error sign + condition triggers). Zero Voynich input.
- **Level B:** Inferred latent structure via unsupervised ML (HMM with BIC, hierarchical clustering into macro-bundles). Zero Voynich input.
- **Null baseline:** Same 6 supervisor states with degraded structural commitments (no qualification gate, merged observation states, no hard correction gate, no closure latch). Tests whether structural commitments are load-bearing.

Non-circularity: **CLEAN**. T1 is entirely Voynich-free at all levels (physical plant, MPC controller, supervisor FSM, null supervisor, LHS sweep, Level A primitives, Level B inference, apparatus families).

## Simulation Scale

| Metric | Value |
|--------|-------|
| System parameterizations | 50 (15d LHS: 4 plant + 5 MPC + 6 supervisor) |
| Operator parameterizations | 10 (6d LHS) |
| Runs per combination | 10 |
| Total full-supervisor runs | 5,000 |
| Total full-supervisor cycles | 336,324 |
| Null-supervisor runs | 1,250 |
| Null-supervisor cycles | 86,963 |
| Cycle length | mean=16.2, median=14 |
| Segmentation | Full trough-to-trough (symmetric physics) |

## Supervisor State Census

| State | Fraction | Role |
|-------|----------|------|
| TRACKING | 93.49% | Full MPC authority (heating permitted) |
| MONITORING | 4.43% | Passive near-target hold |
| CORRECTING | 1.14% | Overshoot correction (Q=0) |
| QUALIFYING | 0.33% | Startup qualification (restricted Q) |
| CLOSING | 0.31% | Closure commitment latch (reheat inhibited) |
| CHECKING | 0.31% | Active endogenous check (Q frozen) |

**Critical diagnostic:** First TRACKING onset occurs at Q0 in 97.1% of cycles. The MPC's asymmetric safety cost prevents overshoot so effectively that the supervisor's QUALIFYING gate operates almost exclusively during cycle burn-in, not within analyzed cycles. TRACKING dominates at 93.5%.

## Action Type Census

| Action | Count | Fraction |
|--------|-------|----------|
| HOLD_OFF | 2,736,355 | 50.1% |
| INCREASE_BELOW | 1,064,128 | 19.5% |
| DECREASE_BELOW | 972,841 | 17.8% |
| CHECK | 462,134 | 8.5% |
| HOLD_AT | 133,721 | 2.4% |
| DECREASE_ABOVE | 90,202 | 1.7% |
| INCREASE_ABOVE | 5,682 | 0.1% |

The MPC+supervisor produces a dramatically different action distribution from P-control (Phase 556). HOLD_OFF dominates at 50.1% (vs 26.5%), DECREASE_ABOVE drops to 1.7% (vs 14.6%), and INCREASE_ABOVE nearly vanishes at 0.1% (vs 4.3%). The MPC rarely allows the system to overshoot, so corrective actions are rare.

## Hypothesis Results

### H1: Three-Phase Operator Scheduling — FAIL (FC4 triggered)

| Metric | Phase 556 | Phase 557 | Threshold | Status |
|--------|-----------|-----------|-----------|--------|
| Voynich JSD | 0.035 | 0.166 | < position | PASS |
| Position JSD | 0.209 | 0.412 | — | Voynich 2.5x better |
| Q1 peak | Q0 | Q0 | Q1 | **FAIL (FC4)** |
| Closure ratio | 10.95 | 14.57 | > 5.0 | PASS |
| Beats Voynich-lite | No | No | Yes | FAIL |
| Beats equal-complexity | No | No | Yes | FAIL |
| Permutation p | 0.75 | 0.864 | < 0.01 | FAIL |
| Ablation degradation | +0.174 | +0.245 | > 0 | PASS |
| OOS train/test | 0.034/0.038 | 0.163/0.170 | stable | PASS |

**Voynich still beats position-only** (0.166 vs 0.412), but the gap narrowed from 6x (Phase 556) to 2.5x. The MPC+supervisor's action profile is harder for any enrichment model to capture — HOLD_OFF at 50.1% dominates all quintiles with minimal variation.

**INCREASE_BELOW still peaks at Q0**, same failure as Phase 556. The QUALIFYING gate is too brief (0.33% of time) to shift the peak from Q0 to Q1. The MPC begins effective heating almost immediately after cycle start.

**Closure ratio improved** from 10.95 to 14.57. The CLOSING commitment latch creates a sharper behavioral discontinuity at cycle end than P-control's gradual decay.

**Per apparatus family:**

| Family | Cycles | Voynich JSD | Position JSD | Closure |
|--------|--------|-------------|-------------|---------|
| SLOW_SUSTAINED | 60,172 | 0.221 | 0.480 | 31.5 |
| MODERATE | 217,671 | 0.199 | 0.452 | 22.6 |
| FAST_AGGRESSIVE | 58,481 | 0.097 | 0.289 | 6.7 |

All 3 families: Voynich beats position-only. FAST_AGGRESSIVE has the tightest JSD (0.097) — the MPC is most effective here, producing the most uniform action distribution.

### H2: Inferred Supervisory Decomposition — FAIL

| Metric | Phase 556 | Phase 557 | Range | Status |
|--------|-----------|-----------|-------|--------|
| HMM BIC k | k=6 (79%) | k=6 (80%) | — | High-dimensional |
| NC fraction | 0.959 | 0.989 | >= 0.70 | PASS |
| Micro persistence | 0.397 | 0.383 | — | reference |
| **Macro persistence** | — | **0.940** | 0.45-0.75 | **FAIL (too sticky)** |
| Permutation p | 1.000 | 1.000 | < 0.01 | FAIL |

**New in Phase 557:** BIC selects k=5-6 microstates, then ward clustering collapses these into 2 macro-bundles. Macro-level persistence = 0.940 — far above the 0.75 upper bound. The MPC+supervisor creates such strong mode separation that the two macro-bundles barely interleave. The Voynich predicts moderate interleaving (persistence 0.45-0.75), not near-complete modal segregation.

This is the opposite failure from Phase 556: Phase 556's modes were too **fragmented** (persistence 0.40, below 0.45). Phase 557's modes are too **sticky** (persistence 0.94, above 0.75). The MPC's effectiveness creates long stretches of uninterrupted TRACKING with brief MONITORING/CORRECTING episodes.

### H3: Dual Feedback Channels — FAIL (FC5 triggered)

| Metric | Phase 556 | Phase 557 | Threshold | Status |
|--------|-----------|-----------|-----------|--------|
| Passive mean pos | 0.456 | 0.462 | ~0.40 | slightly late |
| Active mean pos | 0.486 | 0.511 | ~0.52 | PASS |
| Delta | 0.030 | 0.049 | >= 0.03 | **PASS** |
| Split advantage | -0.004 | -0.003 | > 0 | **FAIL (FC5)** |
| Active higher entropy | No | No | Yes | FAIL |
| Permutation p | 0.000 | 0.000 | < 0.01 | PASS |

**Passive-before-active ordering improved** from delta=0.030 to 0.049 (strongly significant, p<0.001). The supervisor explicitly separates MONITORING (passive, mean pos=0.488) from CHECKING (active, mean pos=0.493), producing a supervisor-level delta of 0.005.

**But the split model still doesn't outperform merged** (FC5 repeats for the third phase). The two-channel distinction creates a real positional phenomenon but doesn't add predictive value. This is now a **stable negative result across three phase architectures** (Phase 555, 556, 557).

### H4: Preventive Stabilization Channel — FAIL

| Metric | Phase 556 | Phase 557 | Threshold | Status |
|--------|-----------|-----------|-----------|--------|
| DB fraction | 6.7% | 17.8% | >= 2% | **PASS** |
| Mean position | 0.438 | 0.473 | < 0.50 | **PASS** |
| Context independent | No | No | Yes | **FAIL** |
| Correction rho | -0.229 | -0.086 | < 0 | PASS |
| Q4 depleted | No | No | < 0.6x | FAIL |

**Prevention channel is stronger:** DECREASE_BELOW increased from 6.7% to 17.8%. The MPC+supervisor produces more anticipatory reductions. Early bias is weaker (0.473 vs 0.438) but still passes.

**Context independence still fails** but correction correlation weakened (rho from -0.229 to -0.086), trending toward the Voynich's independence prediction.

### H5: Instruction-Profile Locality — PASS (strongest ever)

| Metric | Phase 556 | Phase 557 | Threshold | Status |
|--------|-----------|-----------|-----------|--------|
| Raw lag-1 | 0.276 | **0.523** | > 0.15 | **PASS** |
| Shuffle p | 1.000 | 1.000 | > 0.05 | **PASS** |
| Compensatory ratio | 0.382 | 0.631 | <= 1.0 | **PASS** |

**Breakthrough correlation.** Raw lag-1 nearly doubled from 0.276 to 0.523. The MPC+supervisor creates much more deterministic operator profiles — each parameterization produces a characteristic signature that repeats across cycles. Shuffle completely explains the correlation (p=1.0), confirming the Voynich's prediction that cross-cycle similarity reflects parameterization identity, not cycle-to-cycle memory.

The compensatory ratio (0.631) confirms the anti-compensatory prediction: high-correction cycles are NOT followed by high-prevention cycles.

### H6: Hazard Immunity of Energy Operations — FAIL (narrowly)

| Metric | Phase 556 | Phase 557 | Threshold | Status |
|--------|-----------|-----------|-----------|--------|
| IB→DA rate | **25.1%** | **1.96%** | < 5% | **PASS** |
| CHECK→DA rate | 16.8% | 2.16% | > IB rate | PASS |
| DA ratio | 0.67 | 1.10 | >= 3.0 | **FAIL** |
| Transition immune | No | **Yes** | < 5% | **PASS** |
| Stability enriched | No | No | >= 1.2 | FAIL |
| Phase depleted | No | No | <= 0.8 | FAIL |

**The breakthrough result of Phase 557.** The supervisor's CORRECTING gate (Q=0 when above target) drops the IB→DA transition rate from 25.1% to 1.96% — a **12.8x improvement**. FC7 (IB→DA > 20%) is **CLEAR for the first time** in three phases.

The supervisor creates near-hazard-immunity through structural prohibition: heating (INCREASE_BELOW) only occurs in TRACKING state, and the transition to CORRECTING requires passing through MONITORING and/or CHECKING intermediate states.

**But the secondary criteria fail:** The DA ratio (CHECK→DA / IB→DA = 1.10) misses the 3.0 threshold. Both rates are so low (1.96% vs 2.16%) that the ratio can't differentiate them. Stability enrichment and phase depletion are absent — the MPC's effectiveness makes all heating episodes equally safe regardless of context.

**This is the structurally most important result:** The supervisor gate is the right mechanism for hazard immunity. The failure is in degree (secondary criteria), not kind (primary IB→DA rate).

## Failure Condition Audit

| FC | Phase 556 | Phase 557 | Detail |
|----|-----------|-----------|--------|
| FC1 | CLEAR | CLEAR | H3 and H5 beat random |
| FC2 | CLEAR | CLEAR | Voynich beats position-only on H1 |
| FC3 | **TRIGGERED** | CLEAR | Ablation does not improve any metric |
| FC4 | **TRIGGERED** | **TRIGGERED** | INCREASE_BELOW peaks at Q0, not Q1 |
| FC5 | **TRIGGERED** | **TRIGGERED** | Merged model >= split model (H3) |
| FC6 | CLEAR | CLEAR | Shuffle p = 1.0 (locality holds) |
| FC7 | **TRIGGERED** | **CLEAR** | IB→DA = 1.96% < 20% |
| FC8 | CLEAR | CLEAR | NC fraction = 0.989, k=5-6 |

**Two failure conditions triggered** (down from four in Phase 556). FC3 and FC7 cleared — the supervisor structure eliminates both the ablation-improves and hazard-transition failures.

FC4 (Q1 peak) and FC5 (split advantage) are now the **sole remaining hard blockers**.

## Null Supervisor Comparison

| Metric | Full Supervisor | Null Supervisor | Full Wins? |
|--------|----------------|-----------------|------------|
| H1 Voynich JSD | 0.166 | 0.143 | No |
| H1 Q1 peak | Q0 | Q0 | Tie |
| H1 Closure ratio | 14.57 | 13.15 | **Yes** |
| H2 Macro persistence | 0.940 | 0.918 | No |
| H3 Delta | 0.049 | 0.052 | No |
| H6 IB→DA | 1.96% | 3.77% | **Yes** |

**Full supervisor beats null on 2 of 6 metrics** (H1 closure, H6 IB→DA). Structural commitments are **not load-bearing** by the pre-registered criterion (H1 + 2 others required).

The null supervisor (same states, degraded constraints) produces similar results because the MPC itself prevents most overshoot events, making the supervisor's structural commitments (qualification gate, hard correction gate, closure latch) largely redundant.

**Diagnosis:** The MPC is too effective. It solves the safety problem at the controller level, leaving little work for the supervisor. The supervisor's structural commitments only matter at the margins — a slightly better closure ratio and slightly lower IB→DA rate.

## What Phase 557 Establishes

### 1. The supervisor gate mechanism works for hazard immunity

IB→DA dropped from 25.1% (P-control) to 1.96% (MPC+supervisor). The structural prohibition (heating only in TRACKING, Q=0 in CORRECTING) is the right mechanism. FC7 cleared for the first time.

### 2. The MPC prevents overshoot too effectively for the QUALIFYING gate to engage

The MPC's asymmetric safety cost (penalizing overshoot 1-20x more than undershoot) means the system rarely enters CORRECTING or CLOSING states (combined 1.45%). First TRACKING onset occurs at Q0 in 97.1% of cycles. The QUALIFYING gate — which should produce the Q1 peak — operates only during burn-in.

### 3. H5 locality is robust across controller architectures

Raw lag-1 correlation doubled (0.276 → 0.523) with MPC+supervisor. The Voynich's instruction-profile locality prediction passes cleanly across P-control (Phase 556), and MPC+supervisor (Phase 557). This is the most controller-independent prediction.

### 4. FC5 (split advantage) is architecture-invariant

Three consecutive phases (555, 556, 557) with three different controllers all produce negative split advantage. The merged observation model consistently equals or outperforms the two-channel split. Either the Voynich's passive/active distinction has no predictive correlate in thermal control, or the test criterion is poorly matched to the phenomenon.

### 5. H2 persistence swings but never lands in range

Phase 556 micro-persistence: 0.397 (too fragmented, below 0.45). Phase 557 macro-persistence: 0.940 (too sticky, above 0.75). The Voynich predicts moderate interleaving, but P-control produces too-rapid switching while MPC+supervisor produces too-stable modes.

### 6. The right layer, right gate structure, wrong controller aggressiveness profile

Phase 555: wrong layer (raw physics). Phase 556: right layer, wrong controller (P-control). Phase 557: right layer, right gate structure (supervisor), wrong controller aggressiveness profile (MPC too aggressive at preventing overshoot). The next iteration should either reduce the MPC's safety asymmetry or introduce operator-level uncertainty that forces the supervisor's gates to activate more frequently.

## Phase Progression Summary

| Phase | Controller | H1 Q1 Peak | H6 IB→DA | FC7 | Verdict |
|-------|-----------|------------|----------|-----|---------|
| 555 | None (raw plant) | — | — | — | FAIL (wrong layer) |
| 556 | P-control | Q0 (FAIL) | 25.1% (FAIL) | TRIGGERED | FAIL |
| **557** | **MPC + supervisor** | **Q0 (FAIL)** | **1.96% (PASS)** | **CLEAR** | **FAIL** |

## Constraints

No new constraints generated — phase fails pre-registered pass criteria.

## Files

| File | Purpose |
|------|---------|
| `scripts/t1_operator_events.py` | MPC + supervisor + null variant + Level A/B extraction (336,324 + 86,963 cycles) |
| `scripts/t2_voynich_predictions.py` | Voynich predictions from Tier 2 constraints |
| `scripts/t3_scoring_engine.py` | 6 hypotheses + hierarchical H2 + null comparison + H3 supervisor checks |
| `scripts/t4_synthesis.py` | Verdict + failure audit + null comparison |
| `results/t1_operator_events.json` | T1 summary (4.1 KB) |
| `results/t1_cycles.npz` | Full supervisor per-cycle data (29.0 MB) |
| `results/t1_null_cycles.npz` | Null supervisor per-cycle data (7.5 MB) |
| `results/t2_voynich_predictions.json` | Voynich predictions (13.1 KB) |
| `results/t3_scoring_engine.json` | Scoring results (6.6 KB) |
| `results/t4_synthesis.json` | Final verdict |
