# Phase 564: Event-Gated Apparatus Dynamics

**Phase:** 564 (VIRTUAL_APPARATUS_EVENT_DYNAMICS)
**Date:** 2026-03-09
**Verdict:** EVENT_GATING_FAILED (2/9 tests pass)
**New constraints:** None (negative result)

## Summary

Phase 564 replaced Phase 563's first-order drift plant with an event-gated apparatus featuring five architectural enhancements:

1. **Nonlinear restoring force** -- cubic stiffening (d_nonlinear=1.0-1.5) creating progressive resistance that increases with deviation from equilibrium
2. **Phase-specific update laws** -- different state update rules for SPEC, WORK, and CLOSE line phases, with phase-dependent multipliers
3. **Threshold-triggered terms** -- additional restoring contributions activated when state variables exceed deviation thresholds
4. **Dual-channel routing** -- separate routing pathways for containment (m, h) and transition (r, y) channels
5. **Headless configuration modes** -- three config modes (H0_LOW_INFRA, H1_MEDIUM_INFRA, H2_HIGH_INFRA) assigned by folio headless rate

The goal was to produce bounded work-close-recovery oscillation cycles that the Phase 563 monotonic-drift plant could not generate.

**Result: EVENT_GATING_FAILED.** The plant's nonlinear restoring force is so effective that NOTHING -- full model, baselines, or nulls -- ever violates a hazard boundary. Universal viability=1.0 collapses all viability-based discrimination tests. The phase scored 2/9, down from 5/9 in Phase 563 and 3/9 in Phase 563b.

## Results

| Test | 563 | 563b | 564 | Key Finding |
|------|-----|------|-----|-------------|
| P1 | PASS | FAIL | **FAIL** | full=B2=N1=1.0 (all viabilities identical) |
| P2 | PASS | PASS | **PASS** | 7/7 SVs significant (strongest result across all phases) |
| P3 | FAIL | FAIL | **FAIL** | mean cycles=2.8, bounded_frac=0.126, only A3 folios oscillate (5/20) |
| P4 | FAIL | FAIL(2/4) | **FAIL(1/4)** | Only m->C correct (p~0, delta=+0.063). r->X, y->T, h->TR all fail |
| P5 | FAIL | FAIL | **FAIL** | P5a: 5/20 C_better, 3/20 S_better; P5b: C p=0.083, S p=0.139 |
| P6 | PASS | PASS | **FAIL** | full=B3 identical (CTS has no effect when plant is over-stiffened) |
| P7 | PASS | FAIL | **FAIL** | 0/4 null types destroyed (all viab=1.0, std=0) |
| P8 | PASS | PASS | **PASS** | 20/20 preferred best (trivially true on Y_final discrimination) |
| P9 | SEC | SEC | **SEC** | 2/7 SVs significant (S, Y) |

### Composite Metrics

| Metric | 563 | 563b | 564 |
|--------|-----|------|-----|
| Mean viability | 0.9616 | 0.9635 | 1.0 |
| Mean Y_final | 0.878 | 0.848 | 0.7366 |
| Total hazard events | 34 | 255 | 0 |
| Folios with perfect viability | 4/7 | 12/20 | 20/20 |

### Diagnostics

| Diagnostic | Finding |
|------------|---------|
| D1 (threshold terms) | 0/20 viab better, 0/20 hazard better. B7 (minus thresholds) produces identical outcomes to full model. |
| D2 (phase laws) | 0/20 viab better, 0/20 hazard better. B8 (fixed WORK law) produces identical outcomes. Mean viab delta = 0.0. |

## Analysis

### Root cause: Nonlinear restoring force + threshold terms dominate

The cubic restoring force (d_nonlinear=1.0-1.5) creates progressive stiffening that, combined with the original Phase 563 linear decay parameters, absorbs all supervisory signal variation before it can reach hazard boundaries. At deviation 0.2, the cubic term adds approximately 40% to the linear restoring force. At deviation 0.3, the cubic term matches the linear term. The result: state variables stay locked in a narrow band around equilibrium regardless of input.

### V7 self-test passed because synthetic inputs are much stronger than real supervisory signals

The self-test V7 used large dV values (0.08-0.15) that could push past the stiffening threshold. Real supervisory contributions are typically 0.01-0.05, which the combined linear + cubic restoring force absorbs completely. This reveals a calibration gap: the self-test verifies the plant CAN oscillate, but not that real-world supervisory traces are strong enough to MAKE it oscillate.

### Profile-dependent oscillation confirms the mechanism

A3 (DISTILL_COLLECT, highest sensitivity) produces bounded excursions in S-section folios (5-13 cycles in f104r, f105r, f111r, f34r, f86v6). A1 (BATH_REFLUX, lowest sensitivity) produces 0 cycles across all folios. A2 (SEALED_RECIRCULATION) produces 0-3 cycles. This gradient confirms the problem is insufficient effective signal strength relative to the restoring force, not absence of oscillation capability in the architecture.

### P6 regression (was PASS in 563 and 563b)

CTS closure previously modulated hazard exposure by separating containment from general process dynamics. With universal viability=1.0, CTS has no differentiating effect. The full model and B3 (no CTS) produce identical mean C states to 5 decimal places for 18/20 folios. Only f116r and f86v6 show any separation (at the 5th decimal place). The CTS mechanism exists and operates correctly, but its effects are invisible when no state variable ever approaches a hazard boundary.

### P4 regression (was 2/4 in 563b, now 1/4)

The stiff plant absorbs routing buffer effects. Only m->C survives because it is the strongest routing signal in the system (delta=+0.063, p~0). The containment channel (C sensitivity is highest in A2 profiles) produces sufficient dV to overcome the restoring force at the margin. The other three routes -- h->TR (delta=-0.001, p=0.51), r->X (delta=-0.001, p=0.28), y->T (delta=-0.008, p=0.75) -- are undetectable. In 563b, h->TR passed (delta=+0.003, p=0.007); the additional cubic stiffening in 564 pushed this below detection.

### P7 catastrophic failure (0/4 vs 2/4 in 563b)

All four null types (N1 token shuffle, N2 domain preserve, N3 line shuffle, N4 within-line shuffle) achieve viability=1.0 with standard deviation=0 across all 20 folios and all 50 permutations. The plant cannot distinguish structured from random input. The restoring force dominates regardless of token sequence, making the plant a universal absorber that converts any input stream into the same near-equilibrium trajectory.

### P8 passes trivially

With all viabilities at 1.0 and all hazard counts at 0, the only remaining discriminator is Y_final. Because A3 profiles have the highest Y sensitivity, they consistently produce the highest Y_final values. P8 passes 20/20 but this is a degenerate success: profile superiority on Y_final alone, with no viability or hazard differentiation.

## Lessons Learned

1. **Over-stabilization is as fatal as under-stabilization.** Phase 563 had too little decay, leading to hazard violations. Phase 564 has too much restoring force -- universal viability=1.0 kills all discrimination. The parametric sweet spot requires viability significantly above chance but below 1.0 for the full model, with baselines and nulls producing lower viability.

2. **Self-test V7 is a necessary but not sufficient gate.** Synthetic inputs (dV=0.08-0.15) produce oscillation; real supervisory traces (dV~0.01-0.05) do not. Future self-tests should calibrate dV magnitudes against actual supervisory signal distributions. A self-test that uses the observed dV range would have caught this before running the full validation battery.

3. **A3 profile CAN oscillate (5/20 folios meet P3 criterion).** The architecture is not wrong -- the parametric regime is. Linear decay needs reduction (not increase) when cubic stiffening is added. The 5 folios that oscillate (f104r: 13 cycles, f111r: 9 cycles, f116r: 8 cycles, f108v: 6 cycles, f105r: 5 cycles) demonstrate that the event-gating mechanism works when the effective signal-to-restoring-force ratio is high enough.

4. **P2 packet shape (7/7 significant) is the most robust coupling signal across all three phases (563, 563b, 564).** It survived over-stabilization, under-stabilization, and parametric recalibration. Line-level SPEC/WORK/CLOSE differentiation in plant state is the primary grammar-to-apparatus coupling channel and appears to be architecture-independent.

5. **m->C routing remains the strongest and most robust routing signal.** It passed in 563b (delta=+0.065, p~0) and 564 (delta=+0.063, p~0) despite the over-stiffened plant. This confirms m (MIDDLE) has a genuine, large effect on the C (containment) state variable that persists across parametric regimes.

6. **The additive architecture (linear + cubic + threshold + phase multiplier) layers too many restoring mechanisms.** Each individually reasonable; combined they create an impenetrable equilibrium basin. D1 shows B7 (minus thresholds) has identical outcomes to the full model. D2 shows B8 (fixed WORK law) has identical outcomes. These diagnostics confirm that the cubic restoring force alone dominates all dynamics, making threshold terms and phase-specific laws invisible.

## Implications for Next Phase

1. **Reduce linear decay by 50-70% when cubic stiffening is active.** The cubic term should REPLACE linear restoring force near hazard boundaries, not ADD to it. Consider a crossover formulation: `rf = d_linear * dev * (1 - cubic_dominance_factor * dev^2) + d_nonlinear * dev^3`, so that the linear contribution decreases as the cubic contribution increases.

2. **Calibrate against actual dV distribution.** Measure the 90th percentile dV magnitude from real supervisory signals. The restoring force at deviation 0.15 should be approximately 50% of the mean dV, not 200%. This ensures the plant is stiff enough to prevent runaway but permeable enough to register supervisory input.

3. **Threshold terms may be unnecessary.** D1 shows B7 (minus thresholds) has identical outcomes to the full model. If the cubic restoring force already prevents hazard violations, threshold terms add complexity without value. Remove them until the base dynamics produce non-trivial viability variation.

4. **Phase-specific laws showed no effect (D2).** B8 (fixed WORK law) produced identical outcomes. This may improve once overall stiffness is reduced -- the phase multipliers need room to operate. Defer phase-specific law evaluation until the base plant produces hazard events.

5. **Profile sensitivity scaling needs recalibration.** A1 should produce detectable excursions, not zero cycles. The base signal strength at the lowest sensitivity level needs to exceed the equilibrium restoring force. This may require either reducing restoring force parameters or increasing the base contribution magnitudes.

6. **Consider asymmetric restoring force.** The current architecture applies equal restoring force in both directions. A hazard-aware design could use strong restoring force only near boundaries (deviation > 0.3) and weak restoring force near equilibrium (deviation < 0.15), creating a basin that is soft in the middle and hard at the edges.

## Scripts

| Script | Purpose | Output |
|--------|---------|--------|
| t1_event_gated_apparatus.py | Build event-gated apparatus with nonlinear restoring force, phase laws, thresholds | t1_event_gated_apparatus.json |
| t2_event_gated_executor.py | Run 20 folios x 3 profiles + config ablations (90 runs total) | t2_event_gated_runs.json |
| t3_null_and_ablation_executor.py | 8 baselines + 4 nulls x 50 perms per folio (4,160 runs) | t3_null_ablation_runs.json |
| t4_behavior_validation.py | 9-test validation battery + 2 diagnostics (D1, D2) | t4_behavior_validation.json |
| t5_synthesis.py | Aggregate results, cross-phase comparison, verdict | t5_synthesis.json |

## Constraints

No new constraints created (EVENT_GATING_FAILED verdict). Phase 563 constraints C1581-C1587 remain valid for the original 563 configuration. This phase is a documented negative result that establishes the failure mode of over-stabilization through additive restoring mechanisms.
