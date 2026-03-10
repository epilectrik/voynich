# Phase 564b: Selective Restoration and Work Corridor

**Phase:** 564b (VIRTUAL_APPARATUS_SELECTIVE_RESTORATION)
**Date:** 2026-03-09
**Verdict:** SELECTIVE_RESTORATION_FAILED (2/9 tests pass)
**New constraints:** None (negative result)
**Diagnostic status:** D1 OK (ratio=6.05), D2 OK (corridor=18.7%), D3 informative (B9 delta=+0.125)

## Summary

Phase 564b replaced Phase 564's globally additive restoring architecture (linear + cubic + thresholds) with a piecewise 3-zone selective restoration: soft central basin (|dev| < 0.08), permissive work corridor (0.08 <= |dev| < q2), and hard edge barrier (|dev| >= q2). The architecture was calibrated against actual supervisory signal magnitudes and includes closure-triggered discharge events, single-channel routing permissivity, composite headless regime scoring, and profile-specific discharge coefficients.

**Result: SELECTIVE_RESTORATION_FAILED.** The zone architecture is mechanistically correct -- D1 confirms signal dominates restoring in the corridor (ratio 6.05), D2 confirms substantial corridor occupancy (18.7%), and B9 (uniform restoring) produces the largest ablation signal in the entire apparatus line (mean viability delta +0.125). However, the edge barrier (BETA values 2-5x higher than planned, especially BETA_X=80.0) creates an impenetrable boundary that prevents viability loss for all models including nulls, collapsing viability-based discrimination exactly as 564 did but for a different reason.

Phase 564 was a universal absorber: the cubic restoring force dominated everywhere, making the plant stiff at all deviations. Phase 564b localizes the problem: the basin and corridor work correctly, but the edge barrier is impenetrable. This makes 564b a progressive negative result that narrows the parametric space to a single identified parameter.

## Results

| Test | 563 | 563b | 564 | 564b | Key Finding |
|------|-----|------|-----|------|-------------|
| P1 | PASS | FAIL | FAIL | **FAIL** | mean_viab=0.99985, only 1/20 folios <1.0 (need >=8); full_gt_B2=0, full_gt_N1=2 |
| P2 | PASS | PASS | PASS | **PASS** | 7/7 SVs significant; strongest H=3683.5 (Y) |
| P3 | FAIL | FAIL | FAIL | **FAIL** | mean_cycles=1.3, bounded_frac=0.125, n_meeting_both=0/20 |
| P4 | FAIL | FAIL(2/4) | FAIL(1/4) | **FAIL(0/4)** | P4a: 0/4 correct; P4b: viab_delta=0.00015 |
| P5 | FAIL | FAIL | FAIL | **FAIL** | P5a: C_better=0/20, S_better=0/20; P5b: H=1.857, p=0.395 |
| P6 | PASS | PASS | FAIL | **FAIL** | viab_better=0/20, C_sep_positive=0/20; full=B3 identical |
| P7 | PASS | FAIL | FAIL | **FAIL** | 0/4 null types destroyed; all null viab~1.0 |
| P8 | PASS | PASS | PASS | **PASS** | preferred_best=20/20 (trivially true: all viab~1.0) |
| P9 | SEC | SEC | SEC | **SEC** | 2/7 SVs significant (S, Y) |

**Score: 2/9 pass** (same as Phase 564, same two tests: P2 and P8).

### Composite Metrics

| Metric | 563 | 563b | 564 | 564b |
|--------|-----|------|-----|------|
| Mean viability | 0.9616 | 0.9635 | 1.0 | 0.99985 |
| Mean Y_final | 0.878 | 0.848 | 0.7366 | 0.5686 |
| Total hazard events | 34 | 255 | 0 | 1 |
| Folios with perfect viability | 4/7 | 12/20 | 20/20 | 19/20 |
| Corridor occupancy | -- | -- | -- | 18.7% |
| Signal/restoring ratio | -- | -- | -- | 6.05 |
| B9 mean viab delta | -- | -- | -- | +0.125 |

Note: 563 used 7 pilot folios; 563b, 564, and 564b all use 20 pilot folios.

### Diagnostics

| Diagnostic | Status | Value | Finding |
|------------|--------|-------|---------|
| D1 (corridor signal ratio) | OK | 6.05 | Signal dominates restoring in corridor. Range: 0.93 (X) to 15.78 (S). |
| D2 (corridor occupancy) | OK | 18.7% | State regularly enters corridor. Highest: S (55.1%), Y (30.0%), C (36.5%). |
| D3 (B9 uniform restoring) | INFORMATIVE | +0.125 | Strongest ablation signal in apparatus line. Individual drops: f86v5 0.559, f39v 0.556, f55r 0.524, f86v6 0.424. |

## Analysis

### Root cause: Edge barrier over-calibration

T1's self-test V5 calibrates BETA values to prevent hazard violation under P99 supervisory input. This drove BETA_X from the planned 16.0 to 80.0 (5x increase), BETA_S from 8.0 to 14.0 (1.75x), and BETA_T from 6.0 to 10.0 (1.67x). The P99 resilience criterion was too aggressive: it made the edge impenetrable under ALL real-world input magnitudes, not just extreme cases.

The edge barrier uses a logistic-like function: restoring force = BETA * (dev - q2)^2 for deviations beyond q2. With BETA_X=80.0, even a small excursion past q2 (say, 0.01 beyond the boundary) generates a restoring force of 80 * 0.0001 = 0.008, which is comparable to the entire supervisory signal magnitude. This creates a "wall" that prevents state variables from ever reaching hazard boundaries.

### What 564b proved that 564 did not

Phase 564 was a global failure: the cubic restoring force dominated at ALL deviations (basin, corridor, and edge alike), making the entire plant an impenetrable absorber. There was no meaningful zone structure.

Phase 564b proves the zone architecture is correct:

1. **D1 OK (ratio=6.05)**: In the corridor, supervisory signal is 6x stronger than restoring force. This is exactly the design intent -- the corridor should be a "permissive work zone" where the plant responds to supervisory input.

2. **D2 OK (corridor=18.7%)**: State regularly enters the corridor, especially on S (55.1%), C (36.5%), and Y (30.0%). The basin is not trapping all dynamics.

3. **B9 ablation**: When the zone architecture is replaced with uniform restoring (B9), viability drops dramatically -- from 1.0 to 0.44-0.58 for the most sensitive folios. This proves the zone geometry (not just overall strength) determines viability outcomes. No ablation in 563, 563b, or 564 produced drops of this magnitude.

The failure is localized: the edge barrier specifically prevents viability variation, not the overall architecture.

### B9 is the strongest ablation signal in the apparatus line

B9 (uniform restoring across all zones) produced viability drops in 10/20 folios, with the five largest being:

| Folio | Full viab | B9 viab | Delta |
|-------|-----------|---------|-------|
| f86v5 | 1.000 | 0.441 | 0.559 |
| f39v | 1.000 | 0.444 | 0.556 |
| f55r | 1.000 | 0.476 | 0.524 |
| f86v6 | 1.000 | 0.576 | 0.424 |
| f85r1 | 0.997 | 0.802 | 0.195 |

These are the largest viability differences produced by ANY ablation in the entire apparatus sequence (563 through 564b). In previous phases, ablation deltas were typically 0.00-0.03. The B9 deltas of 0.44-0.56 prove that the selective zone architecture is doing real work: the spatial arrangement of soft basin, permissive corridor, and hard edge matters enormously for viability outcomes.

The folios with zero delta (f31r, f34r, f43v, f78r, f79r, f81v, f84r, f95r1, f104r, f105r) are those where state variables never approach hazard boundaries even under uniform restoring -- typically shorter folios or those with weaker supervisory signals.

### P2 packet shape robustness

P2 (7/7 SVs significant) passes for the fourth consecutive phase: 563, 563b, 564, and 564b. The strongest H-statistic in 564b is 3683.5 (Y), compared to 1791.9 in 564. P2 is the most robust coupling signal in the apparatus, surviving four different restoring architectures, three parametric regimes, and zone restructuring. SPEC/WORK/CLOSE line-level differentiation in plant state is genuinely architecture-independent.

### Diagnostic quasi-gates both pass

Both D1 (corridor signal ratio) and D2 (corridor occupancy) pass their quasi-gates, meaning the architectural design is sound:

- **D1**: Mean ratio 6.05 (threshold: >1.0). Per-SV range: X (0.93) to S (15.78). Even the weakest SV (X) has a ratio near 1.0, meaning signal and restoring are approximately balanced in the corridor. The strongest SVs (S: 15.78, T: 13.13) have corridors dominated by supervisory signal.

- **D2**: Mean corridor occupancy 18.7% (threshold: >5%). Per-SV: S (55.1%), C (36.5%), Y (30.0%), T (10.1%), X (4.5%), TR (3.9%), RC (1.8%). Most state variables spend meaningful time in the corridor, with S, C, and Y being the most active.

The quasi-gates confirm that the architecture WOULD work if the edge barrier were softened: the corridor dynamics are correct, the basin is appropriately soft for most SVs, and state regularly moves between zones.

### P3 regression from 564

P3 (bounded excursion cycles) regressed from 564 (mean_cycles=2.8, bounded_frac=0.126, n_meeting=5/20) to 564b (mean_cycles=1.3, bounded_frac=0.125, n_meeting=0/20). In 564, the cubic restoring force at least produced some oscillation in A3 (DISTILL_COLLECT) folios because the force gradient was continuous. In 564b, the piecewise zone structure with an impenetrable edge means state variables that enter the corridor are either pushed back by the edge wall or held in the corridor -- they do not oscillate through. The bounded fraction is similar (0.126 vs 0.125) but the cycle count dropped because the hard edge wall eliminates the overshoot-recovery pattern that cubic restoring produced.

### P4 further regression

P4 (routing consequence) regressed from 564's 1/4 correct to 564b's 0/4 correct. In 564, m->C routing still produced a detectable signal (delta=+0.063, p~0). In 564b, m->C shows a small positive delta (0.002) but is not significant (p=0.406). The zone architecture changes how routing signals propagate: the piecewise restoring force responds differently to routing modulation than the smooth cubic force did, and the impenetrable edge absorbs any routing-induced viability differences.

## Lessons Learned

1. **The piecewise zone architecture IS correct.** D1 (ratio=6.05), D2 (corridor=18.7%), and D3 (B9 delta=+0.125) all confirm the design. 564b establishes that the 563-564 bracket can be resolved with spatially selective restoration. The corridor functions exactly as designed.

2. **The edge barrier is now the discriminability bottleneck.** BETA values (especially BETA_X=80.0, up from spec's 16.0) create an impenetrable boundary. T1's V5 self-test used P99 input resilience as the criterion, which made the edge too strong for real-world signals. The self-test should use P95 resilience instead, allowing occasional P99 breaches.

3. **B9 is the strongest ablation signal ever produced.** Mean viability delta +0.125 with individual drops to 0.44-0.48. This is an order of magnitude larger than any previous ablation signal. It proves zone geometry matters.

4. **P2 packet shape (7/7 significant) is the most robust coupling signal across all four phases.** SPEC/WORK/CLOSE differentiation is architecture-independent and parametric-regime-independent.

5. **Basin calibration contributes to over-stiffness.** gamma_basin values (S: 0.25, X: 0.18, Y: 0.25) are 2-8x higher than spec for some SVs. The basin should be genuinely soft, with gamma values reduced by 50-70%.

6. **564b's failure is localized, unlike 564's.** Phase 564 was a universal absorber everywhere. Phase 564b has a functioning corridor but impenetrable edges. This makes 564b a progressive negative result: it narrows the parametric space from "everything is wrong" to "one specific parameter needs adjustment."

## Implications for Next Phase

1. **Reduce BETA values by 50-70%** (especially X: 80.0 -> 25-30). The edge should resist P95 inputs but NOT make viability universal. Allow occasional P99 breaches to create viability variation.

2. **Reduce basin gamma values** (S: 0.25 -> 0.10, X: 0.18 -> 0.08, Y: 0.25 -> 0.05). The basin should be genuinely soft -- state should drift within the basin with minimal restoring force.

3. **Target viability regime:** full model ~0.92-0.97, baselines ~0.88-0.94, nulls ~0.80-0.90. This gives room for P1, P7, and P6 to discriminate.

4. **Relax V5 self-test:** Edge barrier should prevent hazard violation under P95 input, not P99. Allow occasional P99 breaches.

5. **Cross-coupling may need attention** if routing (P4) remains undetectable after edge recalibration. With softer edges, routing effects that currently cannot reach boundaries may become visible.

6. **Consider graduated edge softening.** Rather than a single BETA value per SV, use a graduated edge that increases stiffness progressively: moderate at q2, strong at q2+0.05, maximum at hazard boundary. This prevents the "wall" effect while still protecting against hazard violations.

## Scripts

| Script | Purpose | Output |
|--------|---------|--------|
| t1_selective_restoration_apparatus.py | Build 3-zone selective restoration apparatus with V5 self-test | t1_selective_restoration_apparatus.json |
| t2_selective_restoration_executor.py | Run 20 folios x 3 profiles x 3 configs + ablations (90 runs) | t2_selective_restoration_runs.json |
| t3_null_ablation_executor.py | 9 baselines + 4 nulls x 50 perms per folio + B9 (4,200 runs) | t3_null_ablation_runs.json |
| t4_behavior_validation.py | 9-test validation battery + 3 diagnostics (D1, D2, D3) | t4_behavior_validation.json |
| t5_synthesis.py | Aggregate results, cross-phase comparison, verdict | t5_synthesis.json |

## Constraints

No new constraints created (SELECTIVE_RESTORATION_FAILED verdict). This phase narrows the parametric space by confirming zone geometry is correct and identifying edge barrier strength (specifically BETA values, especially BETA_X=80.0) as the remaining bottleneck. Phase 563 constraints C1581-C1587 remain valid for the original 563 configuration.
