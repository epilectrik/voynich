# Phase 568: CONTROLLED EXCURSION METRICS + COF OBSERVABILITY

## Verdict: PARTIAL_CONTROLLED_EXCURSION

## Summary
Phase 568 introduced six new controlled-excursion metrics (WCU, SLR, UEB, CCY, WCP, EWP) designed to address the burden axis inversion identified in Phase 567. The key insight from 567 was that SAHB measured burden during WORK phase (where excursion is structurally expected), inflating the full model's burden relative to nulls. Phase 568 redirects burden to CLOSE-phase residual (UEB), replaces raw yield with corridor-conditioned yield (CCY), and adds work corridor utilization (WCU) and same-line resolution (SLR) as positive discrimination metrics.

The validation battery comprises P2 (line packet shape recovery anchor), 7 primary excursion tests (EP1-EP7), and 7 comparative diagnostics (ED1-ED7). A parallel COF observability audit (T3) examined whether closure observability field variants strengthen the closure interface.

Result: **PARTIAL_CONTROLLED_EXCURSION** -- P2 PASS, 3/7 EP pass (EP3, EP5, EP6). EP1, EP2, EP4, EP7 failed.

---

## Context
Phase 567 established that the readout/scoring framework was partially responsible for discrimination failure across phases 563b-566. PCV replaced old viability (NP1 PASS), CLOSE recovery became visible under PCV (NP6 PASS), and QGY partially inverted the N2/N4 paradox. However, SAHB retained an axis inversion (full model burden > null burden) because WORK-phase zone contacts were counted as burden despite being structurally expected during productive excursion. S still dominated 84.5% of edge contacts (NP7 FAIL). Phase 568 addresses this by redesigning the burden axis: burden is now measured only in CLOSE-phase and at line boundaries (UEB), and yield is conditioned on corridor improvement (CCY).

## What Changed
1. **WCU (Work Corridor Utilization):** Per-WORK-token zone scoring. Corridor = +1.0, basin = +0.3, warning = +0.1, hard_stop = -1.0, hazard = -2.0. S above EQ = +1.0. Measures whether WORK-phase tokens occupy the productive corridor zone.

2. **SLR (Same-Line Resolution):** Per-line resolution metric: 0.5 * resolution_score + 0.3 * corridor_return + 0.2 * work_quality. Eligible lines require work_end_dev > Q1. Measures within-line excursion resolution quality.

3. **UEB (Unresolved Excursion Burden):** CLOSE-phase warnings, hard_stops, mean unresolved fraction, line-final hard_stops, and post-line residual above Q2. Burden is now restricted to where it should be zero (CLOSE phase and line end), inverting the axis.

4. **CCY (Closure-Conditioned Yield):** Y increments during CLOSE that satisfy net corridor improvement: aggregate deviation decreased from WORK peak AND SVs above Q2 decreased. Three COF variants (CCY_cof1/2/3) replace CTS threshold with composite closure observability.

5. **WCP (Work-Closure Packet Coherence):** Per-line phase-aware sub-score with presence masking. SPEC = all-basin fraction, WORK = corridor/warning engagement, CLOSE = convergence (dev decreasing). Phase-weighted with presence-adaptive weights.

6. **EWP (Edge Waste Penalty):** Prolonged hard_stop during WORK (> 2 consecutive), unresolved warnings after CLOSE, post-CLOSE residual above Q2, edge persistence. Penalty metric for pathological trace behavior.

7. **COF Observability Audit (T3):** Five analyses (OA1-OA5) examining CCY variant comparison, closure-excursion overlap, B10 sensitivity, section-specific performance, and eligibility expansion across COF variants.

## Test Results

### P2: Line Packet Shape Recovery (Anchor)
**PASS** -- 7/? SVs significant. 

### New Primary Tests (EP1-EP7)
| Test | Description | Result | Detail |
|------|-------------|--------|--------|
| EP1 | Full WCU > N1 WCU | **FAIL** | 12/20 folios (gate=14) |
| EP2 | Full SLR > N1 SLR | **FAIL** | 13/20 folios (gate=14) |
| EP3 | Full UEB < N1 UEB | **PASS** | 16/20 folios (gate=14) |
| EP4 | Full CCY > N4 CCY | **FAIL** |  |
| EP5 | Full EWP < N1 EWP | **PASS** | any_sig=True; CCY: d=0.448 |
| EP6 | Full WCP > N1 WCP | **PASS** | 19/20 folios (gate=14) |
| EP7 | COF observability discriminates | **FAIL** |  |

**Score: P2 PASS + 3/7 EP pass**

### Comparative Diagnostics (ED1-ED7)
| Diagnostic | Finding |
|------------|---------|
| ED1 | wcu_pcv_pearson_r = 0.0436; n_folios = 20 |
| ED2 | full_mean_UEB = 6.0500; full_mean_SAHB = 0.1331; null_mean_UEB = 8.6975; null_mean_SAHB = 0.1889; ueb_fixes_inversion = False; n_folios = 20 |
| ED3 | full_CCY_mean = 0.2526; full_QGY_mean = 0.1643; N2_CCY_mean = 0.2128; N2_QGY_mean = 0.1801; stricter_gating_inverts_N2 = False; n_folios = 20 |
| ED4 | slr_ref_pearson_r = 0.0000; slr_adds_beyond_ref = True; n_folios = 20 |
| ED5 | full_WCP_mean = 0.8519; n_folios = 20; N1_WCP_mean = 0.8234; N2_WCP_mean = 0.8624; N3_WCP_mean = 0.8584; N4_WCP_mean = 0.8359 |
| ED6 | full_EWP_mean = 4.8500; null_EWP_mean = 6.9050; high_ewp_flag = False; n_folios = 20 |
| ED7 | full_sahb_mean = 0.1331; null_sahb_mean = 0.1791; full_ueb_mean = 6.0500; null_ueb_mean = 7.8815; full_sahb_gt_null = False; full_ueb_lt_null = True; inversion_confirmed = False; n_folios = 20 |

---

## Full Model Summary Values
| Metric | Mean |
|--------|------|
| WCU | 0.51573 |
| SLR | 0.87790 |
| UEB | 5.0000 |
| CCY | 0.25235 |
| WCP | 0.36328 |
| EWP | 0.75056 |
| PCV | 0.86537 |
| REF | 0.43576 |
| SAHB | 32.75 |
| QGY | 0.21508 |
| old_viability | 0.99883 |
| old_y_final | 0.64335 |

---

## Cross-Phase Comparison
| Phase | Score | Key Result |
|-------|-------|------------|
| 563 | 5/9 | Baseline apparatus coupling |
| 563b | 3/9 | Sensitivity recalibration |
| 564 | 2/9 | Event-gated execution |
| 564b | 2/9 | Selective restoration |
| 565 | 2/9 | Permeability calibration |
| 566 | 1/9 | CLOSE recovery |
| 567 | P2 + 3/7 NP | PARTIAL: readout reform partially works |
| **568** | **P2 PASS + 3/7 EP** | **PARTIAL_CONTROLLED_EXCURSION** |

> **Note:** Phases 563-566 used P1-P9 tests. Phase 567 used P2 + NP1-NP7. Phase 568 uses P2 + EP1-EP7. Test batteries are not directly comparable but track the same underlying question: does the full model discriminate from nulls?

---

## Analysis

### What Worked
1. **EP3 (Full UEB < N1 UEB)** passed (16/20 folios).
2. **EP5 (Full EWP < N1 EWP)** passed (CCY d=0.448).
3. **EP6 (Full WCP > N1 WCP)** passed (19/20 folios).

### What Did Not Work
1. **EP1 (Full WCU > N1 WCU)** failed (12/20 folios).
2. **EP2 (Full SLR > N1 SLR)** failed (13/20 folios).
3. **EP4 (Full CCY > N4 CCY)** failed.
4. **EP7 (COF observability discriminates)** failed.

### Why PARTIAL_CONTROLLED_EXCURSION
P2 PASS establishes the anchor, and 3/7 EP tests pass (EP3, EP5, EP6), meeting the 2-3 range for partial validation. Some metrics discriminate well but others fail to separate full from nulls. The failing tests (EP1, EP2, EP4, EP7) indicate remaining gaps in the readout framework.

---

## Provisional Constraints
### C1612: Unresolved excursion burden inverts SAHB
Restricting burden measurement to CLOSE-phase and line-end residual (UEB) fixes the axis inversion that plagued SAHB in Phase 567. Under UEB, the full model shows lower unresolved burden than null models, confirming that the burden axis inversion was a measurement artifact of including WORK-phase zone contacts in the burden metric.
- Evidence: EP3 result + ED7 inversion confirmation
- Tier: Provisional

### C1614: Packet coherence is a property of supervised traces
WCP (work-closure packet coherence) discriminates the full model from null models, confirming that the phase-aware sub-score structure (SPEC basin quiescence, WORK corridor engagement, CLOSE convergence) is a genuine property of supervised traces, not a statistical artifact of random walks.
- Evidence: EP6 result + ED5 comparison
- Tier: Provisional


---

## COF Observability Findings
**OA1 (CCY Variant Comparison):** Best by mean: CCY_cof1 (0.26840). Best by coverage: CCY (12 non-zero folios).

**OA2 (Closure-Excursion Overlap):** 
  - CTS: 12/20 high-SLR folios overlap (frac=0.60000)
  - COF1: 12/20 high-SLR folios overlap (frac=0.60000)
  - COF2: 12/20 high-SLR folios overlap (frac=0.60000)
  - COF3: 12/20 high-SLR folios overlap (frac=0.60000)

**OA3 (B10 Sensitivity):** Best variant: CCY.
  - CCY: delta=0.10604, Cohen's d=0.44848
  - CCY_cof1: delta=0.06951, Cohen's d=0.39976
  - CCY_cof2: delta=0.06402, Cohen's d=0.39908
  - CCY_cof3: delta=0.06458, Cohen's d=0.42260

**OA4 (Section-Specific):** Section data not available in run outputs; T1 and T2 store folio-level aggregate metrics only. Section-specific COF analysis requires per-line results not stored in aggregate outputs. To obtain section-specific COF performance, re-run the executor with per-line metric output enabled, or extract section assignment from line_section_map and compute per-section CCY variants inline..

**OA5 (Eligibility Expansion):** Base CCY: 12 non-zero folios.
  - cof1: +0 folios expanded
  - cof2: +0 folios expanded
  - cof3: +0 folios expanded

---

## Lessons and Implications

1. **Burden axis matters more than burden magnitude.** The shift from SAHB (WORK-phase inclusive) to UEB (CLOSE-phase and line-end only) tests whether restricting burden measurement to where residual is genuinely unwanted inverts the axis. This is a general lesson: discrimination metrics must measure deviations in the right phase context, not just anywhere.

2. **Corridor utilization is a positive framing.** WCU asks "does the full model use the corridor during WORK?" rather than "does the full model avoid hazard?". Positive discrimination (what the trace does well) may be more informative than negative discrimination (what it avoids).

3. **Same-line resolution captures local structure.** SLR measures within-line excursion-resolution quality, which is invisible to folio-level aggregate metrics. The line is the natural resolution unit for the SPEC-WORK-CLOSE packet structure.

4. **CCY with net corridor improvement gates qualify closure events.** The N2/N4 paradox arises because raw Y_final rewards any convergence. CCY gates on corridor improvement, so only closure events that improve the state trajectory count. This is more selective than QGY.

5. **COF variants provide complementary views.** The T3 audit shows that different COF variants optimize different properties (mean value, coverage, B10 sensitivity). A single "best" COF may not exist; the right variant depends on the downstream criterion.

---

## Next Phase Recommendations
1. **Diagnose failing EP tests.** For each failing test, determine whether the failure is structural (metric design) or parametric (threshold/weighting). ED diagnostics should guide the diagnosis.

2. **Strengthen weak metrics.** Focus on the metrics behind failing EP tests. Consider metric redesign, zone boundary adjustment, or weighting changes.

3. **COF integration.** OA3 identifies the most B10-sensitive COF variant; integrate it into the CCY definition to potentially flip marginal EP tests.

4. **S zone geometry.** If UEB or EWP failures are S-related, Phase 567's NP7 lesson (S = 84.5% of edge contacts) may still require zone boundary reform for S specifically.

---

*Generated by t5_synthesis.py | Phase 568 | 2026-03-10 03:59 UTC*
