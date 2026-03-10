# Phase 566: Close-Driven Recovery and Signal Inversion

**Phase:** 566 (VIRTUAL_APPARATUS_CLOSE_RECOVERY)
**Date:** 2026-03-09
**Verdict:** CLOSE_RECOVERY_FAILED (1/9 tests pass)
**New constraints:** None (negative result)
**Diagnostic status:** D1 OK (ratio=6.05), D2 OK (corridor=16.2%), D3 below threshold (B9 delta=0.041, need 0.05), D4 OK (ratio=1.321), D5 FAIL (CLOSE recovery too weak), D6 diagnostic (N2/N4 > full), D7 PASS (latency=2.34)

## Summary

Phase 566 added CLOSE recovery channels to the graduated-edge apparatus from Phase 565: per-SV CLOSE recovery gains (K_CLOSE), CTS-weighted discharge (K_CTS_CLOSE=6.0), profile-specific CLOSE multipliers, relief scaling, and R4/R5 cross-coupling. A preflight ladder tested three parameter packs (566-Low, 566-Mid, 566-High); the 566-Mid pack was selected because all synthetic self-tests (V10-V12) passed.

**Result: CLOSE_RECOVERY_FAILED.** The recovery mechanism works in synthetic preflights but fails on real folios. V10 passes (aligned recovery > 0, disrupted = 0). V11 passes (CTS-weighted recovery is 25% stronger than non-CTS). V12 passes (aligned traces achieve lower hazard burden than random). But on real folios: B10 (no CLOSE recovery) has a viability delta of only -0.00018 vs the full model -- removing CLOSE recovery makes virtually no difference. N2 (contribution-shuffled) and N4 (random-walk) nulls beat the full model on composite score (0.920 and 0.920 vs 0.891). P8 regressed from PASS to FAIL (15/20, threshold 16). The score drops from 2/9 to 1/9.

The synthetic-to-real gap is the defining finding of Phase 566: CTS-weighted CLOSE recovery functions correctly in controlled conditions but real folio CTS values are too low and sparse for the channels to produce meaningful discrimination.

## Results

| Test | 563 | 563b | 564 | 564b | 565 | **566** |
|------|-----|------|-----|------|-----|---------|
| P1 | PASS | FAIL | FAIL | FAIL | FAIL | **FAIL** |
| P2 | PASS | PASS | PASS | PASS | PASS | **PASS** |
| P3 | FAIL | FAIL | FAIL | FAIL | FAIL | **FAIL** |
| P4 | FAIL | FAIL | FAIL | FAIL | FAIL | **FAIL** |
| P5 | FAIL | FAIL | FAIL | FAIL | FAIL | **FAIL** |
| P6 | PASS | PASS | FAIL | FAIL | FAIL | **FAIL** |
| P7 | PASS | FAIL | FAIL | FAIL | FAIL | **FAIL** |
| P8 | PASS | PASS | PASS | PASS | PASS | **FAIL** |
| P9 | SEC | SEC | SEC | SEC | SEC | **SEC** |

**Score: 1/9 pass** (P2 only). Regression from 565's 2/9 (lost P8).

**Cross-phase trajectory:** 5/9 -> 3/9 -> 2/9 -> 2/9 -> 2/9 -> **1/9**

### Key Findings per Test

| Test | Result | Key Metric |
|------|--------|------------|
| P1 | FAIL | full_gt_N1=4/20 (need 14); mean_viab=0.996562, folios_lt_1=5/20 (need >=8) |
| P2 | **PASS** | 7/7 SVs significant; strongest H=3683.5 (Y); 6th consecutive pass |
| P3 | FAIL | mean_cycles=1.50, bounded_frac=0.142, n_meeting_both=2/20 |
| P4 | FAIL | P4a: 0/4 correct; P4b: viab_delta=-0.00066 |
| P5 | FAIL | P5a: C_differs=8/20, S_differs=10/20; P5b: C: H=1.6789,p=0.432; S: H=3.7767,p=0.151 |
| P6 | FAIL | viab_better=0/20, C_sep_positive=1/20 |
| P7 | FAIL | 0/4 null types destroyed; N1 delta=-0.002476, N2 delta=-0.002447 |
| P8 | **FAIL** | preferred_best=15/20 (threshold 16); regressed from PASS in 565 |
| P9 | SEC | 2/7 SVs significant |

### Composite Metrics

| Metric | 563 | 563b | 564 | 564b | 565 | **566** |
|--------|-----|------|-----|------|-----|---------|
| Mean viability | 0.9616 | 0.9635 | 1.0 | 0.99985 | 0.9967 | **0.9993** |
| Mean Y_final | 0.878 | 0.848 | 0.7366 | 0.5686 | 0.6281 | **0.6399** |
| Total hazard events | 34 | 255 | 0 | 1 | 17 | **3** |
| Perfect viability | 4/7 | 12/20 | 20/20 | 19/20 | 14/20 | **17/20** |
| Corridor occupancy | -- | -- | -- | 18.7% | 19.0% | **16.2%** |
| Signal/restoring ratio | -- | -- | -- | 6.05 | 6.05 | **6.05** |
| B9 mean viab delta | -- | -- | -- | +0.125 | +0.122 | **+0.041** |

Note: 563 used 7 pilot folios; all others use 20 pilot folios.

### Diagnostics

| Diagnostic | Status | Value | Finding |
|------------|--------|-------|---------|
| D1 (corridor signal ratio) | OK | 6.05 | Signal dominates restoring in corridor. Range: 0.93 to 15.78. |
| D2 (corridor occupancy) | OK | 16.2% | S dominates (40.3% corridor, 34.6% warning, 21.2% hard_stop). |
| D3 (B9 uniform restoring) | BELOW | +0.041 | Below 0.05 threshold (was +0.122 in 565). Zone architecture weakening. |
| D4 (edge contact audit) | OK | 1.321 | cond2 now passes (was FAIL in 565). Full model has more edge contact than nulls. |
| D5 (CLOSE recovery asymmetry) | **FAIL** | work=+0.0027, close=-0.0006 | CLOSE recovery ~4.3x weaker than WORK push. |
| D6 (composite scoring) | DIAG | full=0.891 | N2=0.920 and N4=0.920 beat full model. |
| D7 (corridor return latency) | OK | 2.34 tokens | CLOSE channels produce rapid corridor returns. |

### Null Model Comparison (T3)

| Model | Mean Viability | Mean Y_final | Composite |
|-------|---------------|--------------|-----------|
| Reference (full) | 0.9993 | 0.640 | 0.891 |
| B1 (uniform sens) | 1.0000 | 0.640 | -- |
| B2 (zero input) | 1.0000 | 0.500 | 0.850 |
| B3 (shuffled phase) | 0.9993 | -- | 0.886 |
| B9 (uniform restoring) | -- | -- | 0.856 |
| B10 (no CLOSE recovery) | -- | -- | 0.886 |
| N1 (phase-shuffled) | -- | -- | 0.889 |
| N2 (contrib-shuffled) | -- | -- | 0.920 |
| N3 (cross-folio) | -- | -- | 0.883 |
| N4 (random walk) | -- | -- | 0.920 |

## Analysis

### Why CLOSE recovery failed to discriminate on real folios

The CLOSE recovery mechanism has three channels: (R1) per-SV CLOSE recovery with K_CLOSE gains, (R2) CTS-weighted discharge scaling contributions by CTS value, and (R3) profile-specific CLOSE multipliers. All three work correctly in synthetic preflights:

- **V10 passes:** Aligned trace recovers (0.119), disrupted trace does not (0.0).
- **V11 passes:** CTS-weighted recovery is 25% stronger (ratio=1.251), Y gain with CTS is 0.101 vs 0.0 without.
- **V12 passes:** Aligned traces achieve lower hazard burden (561 vs 617), higher Y (0.911 vs 0.910), higher composite (0.796 vs 0.715).

But on real folios, the channels barely fire. B10 (no CLOSE recovery) has a viability delta of -0.00018 vs the full model. The CLOSE recovery channels exist but produce negligible effect. The gap between synthetic and real:

1. **Synthetic preflights use controlled CTS values** where CTS is artificially injected at known positions. Real folios have CTS values derived from token morphology, which may be too low, too sparse, or too uniform.
2. **Synthetic preflights use a single idealized trace** running multiple SPEC->WORK->CLOSE cycles. Real folios have complex token sequences where CLOSE phases may be short, infrequent, or poorly aligned with edge approach.
3. **Recovery magnitude scales with P90_dV** (~0.006-0.057 depending on SV). Even with K_CLOSE gains of 0.05-0.50, the actual per-token recovery is a fraction of a single supervisory contribution. It takes many CLOSE tokens to produce measurable recovery, and real folios may not have enough consecutive CLOSE tokens.

### The N2/N4 paradox: contribution-shuffled and random-walk nulls beat the full model

This is the deepest paradox in the apparatus line. N2 (contribution-shuffled) and N4 (random-walk) nulls produce higher composite scores (0.920 and 0.920) than the full model (0.891). Both produce higher Y_final too.

The implication: the full model's supervisory routing (phase-differentiated contributions, packet-aligned signals) CONSTRAINS Y accumulation rather than enabling it. When contributions are shuffled randomly (N2) or replaced with random walks (N4), Y grows more freely because the routing constraints that attenuate signal during SPEC and modulate it during CLOSE are removed.

This suggests a fundamental tension in the apparatus design: the phase structure that enables discrimination (SPEC->WORK->CLOSE) simultaneously limits the Y pathway. The viability-discrimination axis and the Y-accumulation axis are in conflict.

### D5 asymmetry: CLOSE recovery is real but too weak

D5 confirms that CLOSE phases DO produce negative mean dV (pulling state back toward equilibrium) while WORK phases produce positive mean dV (pushing state away). This asymmetry is real and in the correct direction. But the magnitudes are severely imbalanced:

- WORK grand mean: +0.0027 (pushing out)
- CLOSE grand mean: -0.0006 (pulling back)
- Ratio: CLOSE is ~4.3x weaker than WORK

For CLOSE recovery to create discrimination, it would need to be strong enough that a properly aligned trace (with CTS-weighted discharge during CLOSE) recovers from WORK excursions before reaching hazard, while a misaligned trace does not. At current magnitudes, neither the full model nor nulls recover meaningfully during CLOSE.

### S instability dominates edge contact statistics

S spends 55.8% of time in warning+hard_stop zones (warning=34.6%, hard_stop=21.2%), with only 3.9% in basin. This means S is essentially always in danger zones, contributing the majority of warning/hard_stop contacts. This masks the discrimination signal from other SVs, which do have meaningful variation between full and null models but are swamped by S's constant danger-zone residence.

gamma_basin_S = 0.025 may be too low for S's dynamics, or the S zone boundaries (Q2_S=0.24, Q3_S=0.29) may be too tight.

### B10 delta is only -0.00018: CLOSE recovery barely matters

The B10 ablation (remove CLOSE recovery) produces a viability delta of -0.00018 compared to the full model. This is three orders of magnitude smaller than the B9 delta (0.041). Removing CLOSE recovery entirely makes virtually no difference to viability outcomes. The CLOSE recovery channels added in Phase 566 are not load-bearing on real folios.

This confirms the synthetic-to-real gap: the channels work when CTS is artificially injected but do not fire meaningfully on real data.

## What 566 Proved

1. **P2 packet-shape coupling survives six consecutive phases.** 7/7 SVs significant with the strongest H=3683.5 (Y). This is now the most robustly confirmed property in the apparatus line: SPEC, WORK, and CLOSE phases produce genuinely different state-variable dynamics regardless of parametric regime or architectural variant.

2. **CTS-weighted recovery works mechanistically (V11 passes).** Recovery ratio=1.251 (25% stronger with CTS). Residual with CTS=0.013 vs without=0.056. The mechanism is sound; the inputs are too weak on real data.

3. **Safety inversion is achievable under synthetic conditions (V12a passes).** Aligned traces achieve lower hazard burden (561 vs 617 for random), confirming that in principle, structured input CAN produce LESS hazard than random input. The discrimination axis CAN be inverted -- but only with sufficiently strong CTS values.

4. **B9 remains the strongest ablation signal (delta=0.041).** Although below the 0.05 threshold for the first time, B9 (uniform restoring) still produces the largest viability difference. Zone architecture remains the primary load-bearing element, even as its discriminative power weakens under the CLOSE recovery regime.

5. **D4 edge contact discrimination improved.** Full/null ratio=1.321 (was 1.064 in 565). cond2_not_indiscriminate now passes, meaning the full model contacts edges at a measurably higher rate than nulls. This is a structural improvement, even though it does not translate to viability discrimination.

6. **D7 corridor return latency is short.** Mean latency=2.34 tokens, meaning the CLOSE recovery channels DO produce rapid state recovery when they fire. The mechanism is fast but fires too rarely.

## Lessons Learned

1. **Recovery magnitudes commensurate with P90 dV are still insufficient** for real folio discrimination. Even with K_CLOSE gains up to 0.50, K_CTS_CLOSE=6.0, and profile-specific multipliers, the per-token recovery is a fraction of a single supervisory contribution. Real folio CTS values are too low/sparse for CTS-weighted channels to fire strongly.

2. **Real folio CTS values need empirical characterization.** The assumption that CTS values from token morphology would provide sufficient discharge weighting has not been validated against actual CTS distributions. If most tokens have CTS near zero, the CTS-weighted channel is effectively disabled.

3. **The viability scoring function may need fundamental revision.** Zone-occupancy-based viability scoring (fraction of time NOT in hazard) produces insufficient dynamic range. When viability is 0.997-1.0 for all models including nulls, there is no room for discrimination. A hazard-burden-based score (cumulative hazard exposure, weighted by depth and duration) might provide more dynamic range.

4. **The contribution-shuffled null paradox (N2/N4 > full on Y and composite) suggests the full model's supervisory routing CONSTRAINS Y accumulation** rather than enabling it. Phase-differentiated contribution scaling attenuates signal during SPEC and modulates it during CLOSE, limiting Y growth. This is a fundamental design tension that may require decoupling the Y pathway from viability dynamics.

5. **S instability needs attention.** S spends 55.8% in danger zones, dominating edge contact statistics. gamma_basin_S may need to be increased, or S zone boundaries may need to be widened, or S may need to be excluded from certain viability calculations.

6. **P8 regression from PASS (17/20 in 565) to FAIL (15/20)** shows that the CLOSE recovery channels perturbed profile dynamics. The recovery channels preferentially benefit certain profiles (A3_DISTILL_COLLECT, which has K_RELIEF_CLOSE=6.0 vs A1's 3.6), shifting the competitive landscape.

## Implications for Next Phase

1. **The viability metric itself may be the bottleneck**, not the plant architecture. Zone-occupancy scoring produces insufficient dynamic range. Consider:
   - Hazard-burden scoring: integrate (depth * duration) in hazard zones
   - Cumulative exceedance scoring: penalize proportionally to how far state exceeds zone boundaries
   - Asymmetric scoring: weight warning and hard_stop contacts differently

2. **Real CTS values need empirical characterization.** Before designing another CLOSE recovery variant, measure the actual distribution of CTS values across real folios. If CTS is uniformly low, the CTS-weighted channel will never fire meaningfully regardless of gain settings.

3. **The S instability needs attention.** S's constant residence in danger zones masks discrimination signal from other SVs. Options:
   - Increase gamma_basin_S to strengthen S restoring
   - Widen S zone boundaries (raise Q2_S, Q3_S, HAZARD_DEV_S)
   - Exclude S from viability scoring if it is constitutively unstable

4. **The N2/N4 paradox (supervisory routing constrains Y) may require architectural revision.** If the phase structure simultaneously enables discrimination and limits Y accumulation, the two objectives may need to be decoupled. Possible approaches:
   - Allow Y to accumulate independently of phase structure
   - Use a separate Y pathway that is not attenuated during SPEC
   - Redefine what "success" means: perhaps Y should not be maximized but rather maintained in a target range

5. **Cross-phase score trajectory: 5/9 -> 3/9 -> 2/9 -> 2/9 -> 2/9 -> 1/9.** The score has reached its lowest point. Six phases of incremental parametric refinement have not recovered the discrimination that 563 achieved on 7 pilot folios. The apparatus line has likely exhausted incremental improvements. The next step requires either a fundamentally different viability scoring function, a different viability/Y coupling, or a reconsideration of what the apparatus is trying to discriminate.

## Scripts

| Script | Purpose | Output |
|--------|---------|--------|
| t1_close_recovery_apparatus.py | Build CLOSE recovery apparatus with V10-V12 preflights | t1_close_recovery_apparatus.json |
| t2_close_recovery_executor.py | Run 20 folios x 3 profiles x 3 configs + ablations (90 runs) | t2_close_recovery_runs.json |
| t3_null_and_ablation_executor.py | 10 baselines + 4 nulls x 50 perms per folio + B9/B10 (4,220 runs) | t3_null_ablation_runs.json |
| t4_behavior_validation.py | 9-test validation battery + 7 diagnostics (D1-D7) | t4_behavior_validation.json |
| t5_synthesis.py | Aggregate results, cross-phase comparison, verdict, report | t5_synthesis.json, REPORT_566.md |

## Constraints

No new constraints created (CLOSE_RECOVERY_FAILED verdict). This phase proves CTS-weighted CLOSE recovery works mechanistically (V10-V12 pass in synthetic preflights) but real supervisory signals are too weak for the recovery channels to create meaningful discrimination. B10 delta=-0.00018 confirms CLOSE recovery is not load-bearing on real folios.

Phase 563 constraints C1581-C1587 remain valid for the original 563 configuration. The progressive negative results from 564 through 566 collectively establish:
- Zone geometry is correct (B9 ablation confirms across three regimes, albeit weakening)
- Corridor dynamics are correct (D1/D2 stable across three regimes)
- Edge permeability is achievable (565/566 vs 564b)
- CLOSE recovery is mechanistically sound (V10-V12 pass)
- The remaining bottleneck is either the viability scoring function, real CTS value distributions, or a fundamental tension between supervisory routing and Y accumulation
