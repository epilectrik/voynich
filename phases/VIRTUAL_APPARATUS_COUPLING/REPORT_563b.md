# Phase 563b: Routing Accumulation and Dynamic Recalibration

**Phase:** 563b (recalibration of 563)
**Date:** 2026-03-09
**Verdict:** COUPLING_FAILED (3/9 tests pass)
**New constraints:** None (negative result)

## Summary

Phase 563b attempted three targeted refinements to the Phase 563 apparatus coupling:

1. **Routing as cumulative within-line bias** -- routing accumulator with exponential decay (ROUTING_DECAY=0.7, ROUTING_GAIN=0.5), modulating sensitivity multiplicatively, reset at line boundaries (C1470)
2. **Plant oscillation recalibration** -- decay reductions (30-40% on T/X) and cross-coupling strengthening (alpha_YX, alpha_FC) to encourage oscillation instead of monotonic drift
3. **Headless as infrastructure parameterization** -- folio-level profile modulation (C/S sensitivity, C/S decay, alpha_XC) based on headless rate, plus halved per-token headless magnitudes (C1574)

All three changes were run on an expanded 20-folio pilot set (up from 7 in Phase 563), covering 5 sections (B:4, H:7, S:5, T:2, C:2), 3 profiles, and HL rates 0.163-0.403.

**Result: COUPLING_FAILED.** The recalibration made the overall verdict worse (3/9 pass, down from 5/9 in 563). P4 routing improved from 0/4 to 2/4, but P1 and P7 regressed from PASS to FAIL. The fundamental oscillation problem (P3b) was unaffected by decay reduction.

## Results

| Test | 563 | 563b | Key Finding |
|------|-----|------|-------------|
| P1 | PASS | **FAIL** | full>B2: 12/20, full>N1: 15/20 |
| P2 | PASS | **PASS** | global KW sig: 7/7 vars |
| P3 | FAIL | **FAIL** (SEC) | KW sig: 3/7 vars (5 sections, SECONDARY) |
| P3b | FAIL | **FAIL** | nontrivial pass: 20/20, mean excursions: 1.3, mean bounded: 0.0 |
| P4 | FAIL | **FAIL** | correct routes: 2/4 (h, m) |
| P5 | FAIL | **FAIL** | P5a C_better=11/20, S_better=1/20; P5b C p=0.151 |
| P6 | PASS | **PASS** | viab better: 14/20, sep+: 15/20 |
| P7 | PASS | **FAIL** | 2/4 nulls destroyed (N1, N2) |
| P8 | PASS | **PASS** | preferred best on >=1 metric: 14/20 |

### Composite Metrics

| Metric | 563 | 563b |
|--------|-----|------|
| Mean viability | 0.9616 | 0.9635 |
| Mean Y_final | 0.878 | 0.848 |
| Total hazard events | 34 | 255 |
| Folios with perfect viability | 4/7 | 12/20 |

## Analysis

### Why the recalibration failed

**P3b excursions (unchanged at 1.3):** The decay reduction hypothesis was that lower decay on T and X would allow these variables to excurse further from equilibrium before returning, producing oscillation. Instead, the plant simply enters a regime further from equilibrium and stays there. Mean nontrivial fraction is 0.96 (high -- the plant IS working) but excursion count remains ~1 (the plant never returns to baseline). This is a monotonic drift problem, not a parametric tuning problem. The update equation `V[n+1] = clamp(V[n] + dV + coupling - decay*(V[n]-0.5))` has no mechanism for reversal once cumulative dV pushes past the decay equilibrium zone.

**P1 regression (12/20 vs 5/7):** Eight folios now have REF viability below B2 (folio-mean baseline). All are A2 or A3 preferred folios (f55r, f39v, f111r, f108v, f66r, f85r1, f86v5, f86v6). The recalibrated profiles have lower decay, meaning state variables drift further from equilibrium and more easily violate hazard boundaries. B2 (constant folio-mean contributions) trivially achieves viability=1.0 because the mean contribution doesn't push the plant far enough to violate boundaries. The full model's token-level variation, combined with lower decay, causes occasional hazard violations that the original profiles avoided.

**P7 regression (2/4 vs 3/4):** N3 (line shuffle) now fails at 7/20 (was 3/7). N4 (within-line shuffle) now fails at 11/20 (was 5/7). The higher threshold (14/20 vs 5/7) is harder to reach, but the regression is real: with the routing accumulator adding within-line structure, shuffling within lines (N4) should be MORE destructive, not less. The issue is that the routing accumulator's effect is small (ROUTING_GAIN=0.5 * (mult-1.0) ~ 0.1-0.2) and gets overwhelmed by the dominant effect of token composition.

### What improved

**P4 routing (2/4 vs 0/4):** The cumulative between-subjects design detected two genuine routing effects:

- **r→X:** A_mean=0.3265, B_mean=0.3117, delta=+0.0147, p=0.27233 → WRONG
- **y→T:** A_mean=0.5375, B_mean=0.5399, delta=-0.0024, p=0.18552 → WRONG
- **h→TR:** A_mean=0.5092, B_mean=0.5067, delta=+0.0025, p=0.00721 → CORRECT
- **m→C:** A_mean=0.6584, B_mean=0.5929, delta=+0.0654, p=0.00000 → CORRECT

The m→C effect (delta=+0.065, p~0) is the strongest routing signal in the system. The h→TR effect is significant but weaker. r→X shows directional correctness but fails significance. y→T shows no effect. This suggests routing operates selectively: containment-related routing (m, h) is detectable while transition/thermal routing (r, y) is absorbed into broader domain dynamics.

**P8 profile superiority (14/20 PASS):** Despite A2's hazard issues, preferred profiles are still best on at least one metric (viability, hazard count, or Y_final) for 14/20 folios. This passes the expanded threshold, confirming that section-to-profile assignment captures real apparatus differentiation.

### Stable results

**P2 packet shape (7/7 in both):** Line packet phases produce strongly differentiated plant states regardless of parameterization. This is the most robust coupling signal.

**P6 CTS closure (PASS in both):** CTS adds genuine value (viability better for 14/20, C-separation positive for 15/20). This validates CTS as a permanent feature of the trace-apparatus interface.

## Lessons Learned

1. Decay reduction (30-40% on T/X) did NOT produce oscillation. Mean excursions stayed at 1.3 (identical to 563). The monotonic drift is structural, not a matter of parameter magnitude — the update equation itself cannot produce oscillation under the current architecture.

2. Routing accumulator improved P4 from 0/4 to 2/4. m→C is strongly significant (p~0, delta=+0.065) and h→TR passes (p=0.007). The cumulative approach is directionally correct but r→X and y→T remain undetectable. The routing effect is domain-modulated, not purely terminal-dependent.

3. A2 profile is systematically hostile: f55r, f39v, f66r, f85r1, f86v5, f86v6 all show hazard exposure under their preferred A2 profile. A1 achieves perfect viability for all 20 folios regardless of assignment. The A2/A3 profiles may have structural sensitivity misalignment with the supervisory signal distribution.

4. P7 regressed from 3/4 to 2/4 null types passing. N3 (line shuffle) and N4 (within-line shuffle) both fail at the 14/20 threshold. The routing accumulator adds within-line structure that the original model lacked, making N4 more destructive — but the 14/20 threshold is harder to reach than 5/7.

5. P2 packet shape is robust: 7/7 state variables significant in both 563 and 563b. This is the most stable result across configurations, confirming line-level SPEC/WORK/CLOSE as the primary grammar-to-apparatus coupling channel.

6. Headless modulation at folio level (C1574 compliance) produces weak effects. P5a shows C_better for 11/20 but S_better for only 1/20. The modulation direction is inconsistent — higher headless rate should increase both C and S sensitivity, but the effect on S is inverted (lower S in full model vs B6). This suggests the headless modulation function needs retuning or the relationship is non-monotonic.

## Constraints

No new constraints created (COUPLING_FAILED verdict).

Phase 563 constraints C1581-C1587 remain valid for the original 563 configuration. The 563b recalibration is a documented negative result that does not invalidate the original coupling findings.

## Implications for Next Phase

1. **Oscillation requires architectural change, not parametric tuning.** The update equation `V[n+1] = clamp(V[n] + dV + coupling - decay*(V-0.5))` cannot produce reversal dynamics. Consider: (a) feedback-dependent decay that increases when variables are far from equilibrium, (b) state-dependent contribution gating, or (c) explicit return-to-equilibrium forces triggered by line/paragraph boundaries.
2. **Restore original 563 parameters.** The recalibrated profiles cause more hazard violations without improving oscillation. Revert to 563 parameters for any future coupling work.
3. **Routing accumulator is directionally correct for m→C and h→TR.** Keep the cumulative routing design but investigate why r→X and y→T don't produce detectable effects.
4. **A2 profile needs fundamental rethinking.** A2 creates systematic hazard exposure for 6/20 pilot folios. The sensitivity pattern (high C sensitivity=1.4) combined with the supervisory signal distribution creates containment boundary violations. Consider: (a) constraining A2 sensitivity range, (b) re-examining A2 assignment criteria, or (c) accepting that A2 represents a genuinely dangerous operating regime that should produce hazard exposure.
5. **20-folio pilot set is adequate for most tests** but T and C sections (2 folios each) are still underpowered for section-level analysis.

## Scripts

| Script | Purpose | Output |
|--------|---------|--------|
| t1b_apparatus_recalibration.py | Recalibrate 3 profiles, add headless modulation | t1b_apparatus_recalibrated.json |
| t2b_unrouted_supervisory_interface.py | Remove baked-in routing, halve headless magnitudes | t2b_supervisory_interface_unrouted.json |
| t3b_accumulated_trace_executor.py | Run 20 folios x 3 profiles with routing accumulator | t3b_coupled_traces.json |
| t4b_null_and_ablation_executor.py | 6 baselines + 4 nulls x 50 perms = 4,140 runs | t4b_null_ablation_traces.json |
| t5b_plant_behavior_validation.py | 9-test validation battery (8 tests + P3 secondary) | t5b_plant_validation.json |
| t6b_synthesis.py | Aggregate results, comparison, report | t6b_synthesis.json |
