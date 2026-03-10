# Phase 565: Permeability Calibration

**Phase:** 565 (VIRTUAL_APPARATUS_PERMEABILITY_CALIBRATION)
**Date:** 2026-03-09
**Verdict:** PERMEABILITY_FAILED (2/9 tests pass)
**New constraints:** None (negative result)
**Diagnostic status:** D1 OK (ratio=6.05), D2 OK (corridor=19.0%), D3 OK (B9 delta=+0.122), D4 FAILED (full/null ratio=1.064)

## Summary

Phase 565 softened the edge barrier from Phase 564b's impenetrable wall into a graduated two-stage edge (warning band + hard-stop band) with BETA1_X=8.0/BETA2_X=24.0 (down from 564b's BETA_X=80.0), reduced basin gamma values by 50-94%, and recalibrated V5 from P99 to P95 resilience. The architecture is otherwise identical to 564b: same 20 pilot folios, same 3 profiles, same Q1/Q2 zone boundaries, same corridor multipliers, same cross-coupling, same discharge events.

**Result: PERMEABILITY_FAILED.** The edge IS now permeable -- 17 hazard events (vs 1 in 564b, 0 in 564) -- but the discrimination axis is inverted. B2 (zero contributions) achieves viability=1.0 for ALL folios, while the full model produces hazard events in 6/20 folios. The supervisory signal CAUSES hazard rather than preventing it. Mean viability 0.9967 exceeds the P1b ceiling of 0.995. Only 6/20 folios have viability < 1.0 (threshold: 8). Null viabilities are HIGHER than reference for many folios because shuffling disrupts constructive alignment, producing fewer hazard events. D4 confirms edge contact is indiscriminate between full model and nulls (ratio=1.064).

The score remains 2/9 (P2, P8) -- same as Phases 564 and 564b -- but the nature of failure has fundamentally changed. Phase 564 was a universal absorber. Phase 564b localized the problem to an impenetrable edge. Phase 565 proves the edge is permeable but reveals that the entire discrimination mechanism is oriented backward: structured input is penalized, not rewarded.

## Results

| Test | 563 | 563b | 564 | 564b | **565** | Key Finding |
|------|-----|------|-----|------|---------|-------------|
| P1 | PASS | FAIL | FAIL | FAIL | **FAIL** | mean_viab=0.9967, folios_lt_1=6/20 (need>=8); full_gt_B2=0, full_gt_N1=3; B2 paradox |
| P2 | PASS | PASS | PASS | PASS | **PASS** | 7/7 SVs significant; strongest H=3683.5 (Y); 5th consecutive pass |
| P3 | FAIL | FAIL | FAIL | FAIL | **FAIL** | mean_cycles=1.25, bounded_frac=0.125, n_meeting_both=0/20 |
| P4 | FAIL | FAIL(2/4) | FAIL(1/4) | FAIL(0/4) | **FAIL(0/4)** | P4a: 0/4 correct; P4b: viab_delta=0.00152 |
| P5 | FAIL | FAIL | FAIL | FAIL | **FAIL** | P5a: C_differs=9/10, S_differs=10/10; P5b: C p=0.897, S p=0.337 |
| P6 | PASS | PASS | FAIL | FAIL | **FAIL** | viab_better=0/20, C_sep_positive=0/20; full=B3 identical |
| P7 | PASS | FAIL | FAIL | FAIL | **FAIL** | 0/4 null types destroyed; N1 mean_delta=-0.002 (nulls SAFER than full) |
| P8 | PASS | PASS | PASS | PASS | **PASS** | preferred_best=17/20 (threshold 16) |
| P9 | SEC | SEC | SEC | SEC | **SEC** | 2/7 SVs significant (S, Y) |

**Score: 2/9 pass** (same as Phases 564 and 564b, same two tests: P2 and P8).

### Composite Metrics

| Metric | 563 | 563b | 564 | 564b | **565** |
|--------|-----|------|-----|------|---------|
| Mean viability | 0.9616 | 0.9635 | 1.0 | 0.99985 | **0.9967** |
| Mean Y_final | 0.878 | 0.848 | 0.7366 | 0.5686 | **0.6281** |
| Total hazard events | 34 | 255 | 0 | 1 | **17** |
| Folios with perfect viability | 4/7 | 12/20 | 20/20 | 19/20 | **14/20** |
| Corridor occupancy | -- | -- | -- | 18.7% | **19.0%** |
| Signal/restoring ratio | -- | -- | -- | 6.05 | **6.05** |
| B9 mean viab delta | -- | -- | -- | +0.125 | **+0.122** |

Note: 563 used 7 pilot folios; 563b, 564, 564b, and 565 all use 20 pilot folios.

### Diagnostics

| Diagnostic | Status | Value | Finding |
|------------|--------|-------|---------|
| D1 (corridor signal ratio) | OK | 6.05 | Signal dominates restoring in corridor. Range: 0.93 (X) to 15.78 (S). Identical to 564b. |
| D2 (corridor occupancy) | OK | 19.0% | State regularly enters corridor. S (38.8%), Y (47.6%), C (39.7%) most active. |
| D3 (B9 uniform restoring) | OK | +0.122 | Zone architecture confirmed load-bearing. Largest: f86v5 0.559, f39v 0.556, f55r 0.500. |
| D4 (edge contact audit) | **FAILED** | 1.064 | Edge contact is indiscriminate. Full model: 242.1/folio, nulls: 227.5/folio. Ratio 1.064. |

## Analysis

### What 565 proved

The edge IS now permeable. 17 hazard events occurred across 6 folios (vs 1 in 564b, 0 in 564). The graduated two-stage edge (warning + hard-stop) with reduced BETA values (X: 8.0/24.0, down from 80.0) allows state variables to reach and breach hazard boundaries. Zone architecture metrics are essentially identical to 564b (D1: 6.05 vs 6.05; D2: 19.0% vs 18.7%; B9 delta: +0.122 vs +0.125), confirming that the selective restoration geometry is load-bearing and stable across two parametric regimes.

### Why P1 still fails

Mean viability 0.9967 is above the P1b ceiling of 0.995. Only 6/20 folios have viability < 1.0 (threshold: 8). The 6 folios that breach hazard are:

| Folio | Viability | Profile | B2 Viability | N1 Viability |
|-------|-----------|---------|--------------|--------------|
| f55r | 0.97581 | A2_SEALED_RECIRCULATION | 1.000 | 0.990 |
| f86v6 | 0.98539 | A2_SEALED_RECIRCULATION | 1.000 | 0.994 |
| f40v | 0.99057 | A2_SEALED_RECIRCULATION | 1.000 | 0.999 |
| f66r | 0.99088 | A2_SEALED_RECIRCULATION | 1.000 | 1.000 |
| f85r1 | 0.99099 | A2_SEALED_RECIRCULATION | 1.000 | 0.992 |
| f108v | 0.99825 | A3_DISTILL_COLLECT | 1.000 | 1.000 |

Five of six are A2_SEALED_RECIRCULATION profile. A1 and A3 folios never breach hazard. This reveals a profile-specific vulnerability: A2's containment sensitivity drives C and X state variables into edge zones, but only for certain folios with high supervisory signal variance.

### The B2 paradox

B2 (zero contributions) achieves viability=1.0 for ALL 20 folios. The supervisory signal CAUSES hazard events rather than preventing them. This means the plant currently penalizes strong signals rather than rewarding aligned ones. The model with no input is the safest.

This is the fundamental structural problem revealed by 565. In all previous phases, B2's perfect viability was masked by the edge barrier also giving the full model perfect viability. Now that the edge is permeable, the inversion becomes visible: the full model is LESS viable than the zero-input baseline.

The implication is severe. For the apparatus to discriminate, structured (packet-aligned) input must produce LOWER hazard exposure than unstructured or absent input. Currently the opposite is true. The discharge events during CLOSE (CTS discharge, containment resolution, thermal recovery) are too weak to produce measurable recovery from WORK excursions. Without effective CLOSE recovery, every WORK excursion is additive -- it pushes the state further from equilibrium without recovery -- and enough accumulated excursion eventually hits a hazard boundary. More signal means more excursion means more hazard.

### Why P7 fails

Null viabilities are actually HIGHER than reference for many folios. N1 (token shuffle) has mean_delta=-0.002, meaning nulls are on average 0.2% MORE viable than the full model. The mechanism: shuffling disrupts constructive alignment between supervisory contributions within a line, producing weaker effective signals. Weaker signals mean smaller state excursions, which means fewer hazard events, which means higher viability.

This is the direct consequence of the B2 paradox. If absence of signal produces perfect viability, then weakening signal (via shuffling) produces near-perfect viability. The discrimination axis that P7 requires (full > null) is inverted: null > full because weaker signal = less hazard.

Per-null breakdown:
- N1 (token shuffle): mean_delta=-0.002, p=0.951 -- nulls slightly safer
- N2 (domain preserve): mean_delta=-0.001, p=0.903 -- nulls slightly safer
- N3 (line shuffle): mean_delta=+0.001, p=0.213 -- nearly equal
- N4 (within-line shuffle): mean_delta=+0.000, p=0.207 -- nearly equal

N3 and N4 (which preserve more within-line structure) show the full model slightly outperforming nulls, but the effect is tiny and non-significant.

### D4 failure: edge contact is indiscriminate

Edge contact IS happening (D4 cond1 passes), but it is indiscriminate between the full model and nulls (D4 cond2 fails). Full model: 242.1 edge contacts per folio. Null grand mean: 227.5 per folio. Ratio: 1.064.

The full model actually has SLIGHTLY MORE edge contacts than nulls, consistent with the B2 paradox: stronger structured signal produces more excursion and more edge approach. The graduated edge is being reached, but packet alignment does not determine who reaches it.

### The fundamental calibration challenge

The apparatus line has now explored four parametric regimes:

1. **563** (too loose): viab=0.96, 34 hazard events, 5/9 pass -- discrimination worked but viability was too low
2. **564** (impenetrable everywhere): viab=1.0, 0 hazard events, 2/9 pass -- cubic restoring was universal absorber
3. **564b** (impenetrable edge): viab=1.0, 1 hazard event, 2/9 pass -- zone geometry correct but edge too strong
4. **565** (permeable but inverted): viab=0.997, 17 hazard events, 2/9 pass -- edge softened but discrimination axis wrong

The trajectory reveals a deeper structural problem: the plant's response to supervisory input is monotonically excitatory. Input drives state away from equilibrium. More input means more excursion. The restoring force (basin/corridor/edge geometry) provides the only means of pulling state back. But the restoring force is spatially uniform -- it applies equally to all models.

What is missing is a mechanism where packet-aligned input produces BOUNDED excursions that AVOID hazard through coordinated CLOSE recovery, while misaligned input produces UNBOUNDED excursions that breach hazard. Currently the CLOSE recovery mechanism (discharge events, thermal recovery) is too weak to differentiate. Discharge magnitudes (e.g., thermal recovery: count=1, total_magnitude=6e-05 in a sample run) are negligible compared to supervisory signal magnitudes (dV~0.01-0.08).

For the discrimination to work, the discharge events during CLOSE need to be strong enough that a properly aligned trace (SPEC->WORK->CLOSE) recovers from WORK excursions before hitting hazard, while a misaligned trace (WORK during CLOSE, or no CLOSE phase) does not recover. This means discharge rates need to increase by 1-2 orders of magnitude, or the relationship between packet phase and edge approach needs to fundamentally change.

### P3 stagnation

P3 (bounded excursion cycles) remains flat: mean_cycles=1.25, bounded_frac=0.125, n_meeting_both=0/20. This is nearly identical to 564b (1.3, 0.125, 0/20). The edge softening did not improve cycling behavior. Profile stratification:

- A1 (BATH_REFLUX): 0/6 meet P3, mean_cycles=1.0, bounded_frac=0.0
- A2 (SEALED_RECIRCULATION): 0/7 meet P3, mean_cycles=1.29, bounded_frac=0.143
- A3 (DISTILL_COLLECT): 0/7 meet P3, mean_cycles=1.43, bounded_frac=0.214

A3 shows the most oscillation, consistent with its higher sensitivity, but no folio meets both criteria (>=3 cycles AND >=50% bounded). The bounded excursion cycle pattern requires effective CLOSE recovery to pull state back from corridor/edge, creating oscillation. Without strong discharge events, state drifts monotonically.

### P5 partial improvement

P5 shows a marginal structural improvement: P5a now passes (9/10 C_differs, 10/10 S_differs) where it had 0/20 in 564b. The softer basin allows headless configuration to modulate mean state position. However, P5b still fails: the Kruskal-Wallis H-statistics are non-significant for both C (p=0.897) and S (p=0.337). Directional differences exist (H0_C < H2_C for 9/10 folios) but the between-config variance is too small relative to between-folio variance to reach significance.

### P8 is now non-trivial

P8 passes at 17/20 (threshold 16), down from 20/20 in 564b. This is no longer a trivially degenerate pass -- with viability variation, profile superiority is now tested on a combination of viability, Y_final, and bounded cycles. Three folios (f31r, f40v, f55r) fail P8 because the preferred profile (A1 for f31r, A2 for f40v/f55r) is not the best on all three metrics simultaneously.

## Lessons Learned

1. **The graduated edge IS now permeable.** 17 hazard events (vs 1 in 564b, 0 in 564). BETA1_X=8.0/BETA2_X=24.0 (down from BETA_X=80.0) allows state variables to breach hazard boundaries. The primary objective of 565 -- making the edge permeable -- succeeded.

2. **B9 ablation delta remains strong at +0.122** (vs +0.125 in 564b). Zone architecture is confirmed across two parametric regimes. The selective restoration geometry is load-bearing regardless of edge stiffness.

3. **P2 packet shape (7/7 significant) passes for the fifth consecutive phase** (563, 563b, 564, 564b, 565). This is the most robust coupling signal in the entire apparatus line, surviving five different parametric regimes. SPEC/WORK/CLOSE differentiation is genuinely architecture-independent.

4. **The B2 paradox is the key discovery of 565.** The supervisory signal CAUSES hazard events rather than preventing them. B2 (zero contributions) achieves viability=1.0 for ALL folios while the full model has viability < 1.0 for 6/20 folios. The discrimination axis is inverted.

5. **Null discrimination fails because weaker signal = fewer hazard events.** Shuffled nulls produce weaker effective signals, which means smaller excursions, which means fewer hazard events. The inverse of what P7 requires.

6. **D4 confirms edge contact is indiscriminate** (ratio=1.064). Packet alignment does not determine who reaches the edge. The graduated edge is being reached by all models at similar rates.

7. **The CLOSE recovery mechanism is the bottleneck.** Discharge events (CTS discharge, containment resolution, thermal recovery) are too weak to produce measurable recovery from WORK excursions. Without effective CLOSE recovery, every WORK excursion accumulates, and more signal means more accumulated excursion means more hazard.

8. **Profile-specific vulnerability: A2_SEALED_RECIRCULATION accounts for 5/6 folios with viab<1.0.** A1 and A3 folios never breach hazard. A2's containment sensitivity (low C decay) drives C and X into edge zones for high-variance folios.

## Implications for Next Phase

1. **Strengthen CLOSE recovery mechanism by 1-2 orders of magnitude.** Discharge events during CLOSE must produce measurable state recovery (dV~0.01-0.03, not 6e-05). A properly aligned trace (SPEC->WORK->CLOSE) should recover from WORK excursions before hitting hazard. A misaligned trace should not recover.

2. **Invert the discrimination axis.** The plant must reward packet alignment. A well-aligned trace should produce BOUNDED excursions (WORK pushes out, CLOSE pulls back) that stay below hazard. A misaligned trace should produce UNBOUNDED excursions (WORK pushes out, CLOSE fails to recover, state breaches hazard).

3. **Consider phase-asymmetric edge stiffness.** During CLOSE, increase effective restoring force (helping recovery). During WORK, decrease it (allowing exploration). This creates an asymmetry where CLOSE phases pull state back from edges while WORK phases allow approach.

4. **Do NOT change zone boundaries or D1/D2 corridor dynamics.** The basin/corridor/edge geometry is confirmed correct across two parametric regimes. The problem is exclusively in how CLOSE recovery interacts with edge approach.

5. **Cross-phase score trajectory: 5/9 -> 3/9 -> 2/9 -> 2/9 -> 2/9.** The score has plateaued at 2/9 but the nature of failure has changed from "everything wrong" (564) to "edge impenetrable" (564b) to "edge permeable but discrimination inverted" (565). Each phase narrows the parametric space.

## Scripts

| Script | Purpose | Output |
|--------|---------|--------|
| t1_permeability_apparatus.py | Build graduated edge apparatus with V5 P95 calibration, V9 preflight | t1_permeability_apparatus.json |
| t2_permeability_executor.py | Run 20 folios x 3 profiles x 3 configs + ablations (90 runs) | t2_permeability_runs.json |
| t3_null_and_ablation_executor.py | 9 baselines + 4 nulls x 50 perms per folio + B9 (4,200 runs) | t3_null_ablation_runs.json |
| t4_behavior_validation.py | 9-test validation battery + 4 diagnostics (D1, D2, D3, D4) | t4_behavior_validation.json |
| t5_synthesis.py | Aggregate results, cross-phase comparison, verdict | t5_synthesis.json |

## Constraints

No new constraints created (PERMEABILITY_FAILED verdict). This phase proves the edge IS now permeable (17 hazard events) but reveals that the discrimination axis is inverted: structured supervisory input produces MORE hazard than absent or random input. The CLOSE recovery mechanism needs strengthening by 1-2 orders of magnitude to invert this relationship.

Phase 563 constraints C1581-C1587 remain valid for the original 563 configuration. The progressive negative results from 564, 564b, and 565 collectively establish that:
- Zone geometry is correct (B9 ablation confirms across two regimes)
- Corridor dynamics are correct (D1/D2 stable across two regimes)
- Edge permeability is achievable (565 vs 564b)
- The remaining bottleneck is CLOSE recovery strength relative to WORK excursion magnitude
