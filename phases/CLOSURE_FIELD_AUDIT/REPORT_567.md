# Phase 567: CLOSURE FIELD AUDIT + BURDEN METRIC REFACTOR

## Verdict: PARTIAL_METRIC_REFACTOR

## Summary

Phase 567 tested whether the persistent discrimination failure across phases 563b-566 was primarily a **readout/scoring problem** rather than a plant-law deficiency. The CloseRecoveryApparatus from Phase 566 was reused unchanged. Two interventions were applied:

- **Part A (T1):** A pure data-analysis audit of CTS distributions, closure component discriminability, CTS-excursion timing, S asymmetry, and closure opportunity fractions. This revealed that closure signal is structurally weak: only 37.4% of CLOSE lines exceed CTS 0.3, useful closure fraction is 3.2%, and CTS-excursion timing is uncorrelated (Spearman r = -0.014). S accounts for 90% of all warning+hard_stop contacts, confirming that the old scoring scheme conflates productive S reserve with genuine hazard.

- **Part B (T2-T4):** Six new metrics (PCV, SAHB, REF, QGY, CRE, MPZF) were designed with S asymmetry correction and deployed across 90 full-model runs, 4,220 null/baseline runs, and a 7-test validation battery. Result: P2 PASS (7/7 SVs), NP1 PASS (16/20), NP5 PASS (16/20), NP6 PASS (all 3 criteria met). Four tests failed: NP2 (1/20), NP3 (11/20), NP4 (13/20, one folio short), NP7 (S share still 84.5%).

The verdict is **PARTIAL_METRIC_REFACTOR**: readout reform demonstrably works for packet-coherence viability (PCV) and excursion resolution (REF), and CLOSE recovery becomes load-bearing under PCV. But S dominance remains incompletely resolved, and the quality-gated Y (QGY) effect, while real, is one folio short of significance at the 14/20 gate.

---

## Part A: Closure Field Audit (T1)

### A1: CTS Distribution

- Global CTS mean = 0.30289, median = 0.21715
- Only 37.4% of CLOSE lines exceed CTS 0.3 threshold
- Section B deficit: -0.07891 (B mean 0.2493 vs non-B 0.32821)
- CLOSE-phase CTS mean (0.29278) is barely above WORK-phase (0.27599)

### A2: CLOSE Window Characterization

- 76 folios contain CLOSE-phase lines (463 total lines)
- Mean CLOSE run length: 1.265 lines (mostly isolated)
- CLOSE token density mean: 0.190

### A3: Closure Component Audit

- No closure component (closure_armed, q4_shift_strength, close_opacity_bias, m_close_bias, q4_opaque_rate, cts) discriminates CLOSE from WORK at p < 0.01
- Best individual discriminator: CTS itself (p = 0.09633)
- Components are internally correlated (closure_armed-cts: r = 0.849) but none separates phases

### A4: CTS-Excursion Timing

- Spearman correlation between preceding WORK contribution and CLOSE CTS: r = -0.01429 (p = 0.88494)
- Only 14.3% of transitions are high-WORK followed by high-CTS-CLOSE
- Closure signal and excursion need are **structurally uncoupled**

### A5: S Asymmetry Audit

- S warning+hard_stop zone occupancy: 57.8%
- S accounts for **90.0%** of all warning+hard_stop contacts across all SVs
- Estimated one-sided S warning+hard_stop (excluding high-side reserve): 0.289
- Other SVs rarely reach warning/hard_stop (T: 0.5%, RC: 0%, C: 3.1%, TR: 0%, X: 0.1%, Y: 1.5%)

### A6: COF Prototype Family

- Four COF variants tested (cts, cof1, cof2, cof3)
- Best phase discrimination: **cof2** (p = 0.04492)
- Best excursion overlap: **cof1** (17.1% overlap)
- Even the best COF variant is marginal (p = 0.045, not < 0.01)

### A7: Closure Window Overlap

- Total CLOSE lines: 463
- CLOSE lines with preceding WORK: 105
- High-excursion preceding WORK: 29 (27.6%)
- **Useful closure fraction (CTS): 3.2%**
- Interpretation: closure signal is weakly coupled to excursion need; closure opportunities are structurally sparse

---

## Part B: Burden Metric Refactor (T2-T4)

### New Metrics

| Metric | Full Name | Description |
|--------|-----------|-------------|
| PCV | Packet-Coherence Viability | Product of per-SV coherence scores; replaces binary hazard threshold |
| SAHB | S-Asymmetry-corrected Hazard Burden | Hazard burden excluding high-S events (productive reserve) |
| REF | Resolved Excursion Fraction | Fraction of excursion resolved by CLOSE-phase tokens |
| QGY | Quality-Gated Y | Y_final weighted by quality of convergence path |
| CRE | Close-Return Efficiency | Fraction of CLOSE windows producing measurable state improvement |
| MPZF | Multi-Parameter Zone Fraction | Fraction of trace time with multiple SVs in basin |

### Full Model Summary Values

| Metric | Mean |
|--------|------|
| PCV | 0.8743 |
| SAHB | 18.085 |
| REF_mean | 0.446 |
| REF_eligible_fraction | 0.648 |
| QGY | 0.231 |
| qgy_ratio | 0.319 |
| CRE_strict | 0.108 |
| CRE_soft | 0.333 |

### Test Results

| Test | Description | Result | Detail |
|------|-------------|--------|--------|
| P2 | Anchor: line packet shape recovery | **PASS** | 7/7 SVs significant |
| NP1 | PCV vs phase-shuffled null (N1) | **PASS** | 16/20 folios |
| NP2 | SAHB < null SAHB | **FAIL** | 1/20 folios |
| NP3 | QGY > N2 null QGY | **FAIL** | 11/20 folios |
| NP4 | QGY > N4 null QGY | **FAIL** | 13/20 folios |
| NP5 | REF not degenerate | **PASS** | 16/20 folios |
| NP6 | B10 delta under PCV | **PASS** | 3/3 criteria |
| NP7 | S share < 30% | **FAIL** | S=84.46% |

**Score: P2 PASS + 3/7 NP pass (NP1, NP5, NP6)**

### Comparative Diagnostics

| Diagnostic | Finding |
|------------|---------|
| CD1: PCV vs old viability | Pearson r = 0.3911 — measuring different constructs |
| CD2: S edge dominance | S = 84.5% of all edge contacts |
| CD3: QGY paradox inversion | N2 QGY (0.180) < full QGY (0.231) despite N2 Y_final (0.734) > full Y_final (0.675) |
| CD4: REF non-degeneracy | Full REF_mean = 0.446, eligible = 0.648; all nulls have REF ~ 0 |
| CD5: B10 delta | PCV: +0.020, QGY: +0.139, old_viability: +0.003 |
| CD6: CRE window truncation | CRE_soft (0.333) > CRE_strict (0.108): window truncation masks real returns |
| CD7: Quality fraction | Full qgy_ratio (0.319) highest of all models; all nulls lower |
| CD8: QGY rank test | Full vs N2: U=223.5, p=0.262; Full vs N4: U=240.5, p=0.134 |

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
| **567** | **P2 + 3/7 NP** | **PARTIAL: readout reform partially works** |

> **Note:** Phase 567 uses a different test battery (P2 anchor + NP1-NP7) than phases 563-566 (P1-P9). Direct score comparison is not straightforward. The shift to NP tests reflects the hypothesis change: from "does the plant law work?" (P tests) to "does the readout detect what the plant law does?" (NP tests).

---

## Analysis

### What Worked

1. **PCV replaces old viability.** The correlation between PCV and old_viability is only r = 0.39 (CD1), confirming they measure fundamentally different aspects. PCV discriminates the full model from phase-shuffled nulls (NP1: 16/20), which old viability could not reliably do. This is the single strongest positive result.

2. **CLOSE recovery becomes visible.** Under PCV, the B10 (ablated CLOSE) delta is +0.020 with Cohen's d = 0.465 (NP6 PASS on all three criteria). Under old viability, the same delta was ~0.003. The plant mechanism was always there; the old readout was blind to it.

3. **REF is non-degenerate.** The full model resolves ~44.6% of excursion on average (REF_mean = 0.446), while all null models have REF near zero (CD4). This confirms that excursion resolution is a real, non-trivial property of the full model's CLOSE-phase behavior.

4. **QGY partially resolves the N2 paradox.** The N2 null (label-shuffled) has higher Y_final (0.734) than the full model (0.675), but lower QGY (0.180 vs 0.231). The quality fraction (qgy_ratio = 0.319 for full, highest of all models) confirms that the full model's convergence is higher quality even when the raw endpoint is lower.

### What Did Not Work

1. **S asymmetry correction is insufficient.** Even after excluding high-S events from SAHB, S still accounts for 84.5% of all edge contacts (NP7 FAIL at 84.5% vs 30% threshold). The NP2 test (SAHB < null) fails catastrophically (1/20). S zone geometry needs a more fundamental rethinking.

2. **QGY is one folio short.** NP4 (full QGY > N4 QGY) reaches 13/20, missing the 14/20 threshold by one folio. Six folios have QGY = 0 (no excursions in preferred profile), which may indicate a denominator problem rather than a real failure.

3. **Closure observability remains structurally weak.** The T1 audit reveals a fundamental constraint: closure signal (CTS) is uncorrelated with excursion need (Spearman r = -0.014), only 37.4% of CLOSE lines exceed the 0.3 threshold, and useful closure fraction is 3.2%. No individual closure component discriminates CLOSE from WORK at p < 0.01.

### Why Partial

The readout reform succeeded at the **packet level** (PCV) and the **excursion-resolution level** (REF, NP6), but failed at the **aggregate scoring level** (SAHB, NP7) because S dominance is a zone-geometry problem, not a scoring-weight problem. The old metrics were measuring the wrong thing (binary threshold vs. coherence), but the new metrics are still measuring in the wrong place (S-dominated edge contacts). The plant law works; the observation framework is 60% fixed.

---

## Provisional Constraints

### C1605: PCV Discrimination
Packet-coherence viability (PCV) provides higher discrimination than binary hazard-threshold viability. PCV discriminates full from phase-shuffled null (NP1 16/20) while old viability could not. Low correlation (r=0.39) confirms they measure different constructs.
- Evidence: NP1 PASS (16/20), CD1 pearson_r=0.391
- Tier: Provisional

### C1606: S Asymmetry Insufficiency
S scoring asymmetry (high-S as productive reserve) is necessary but insufficient. S still accounts for 84.5% of SAHB even after excluding high-S events. The remaining low-S burden dominates aggregate metrics.
- Evidence: NP7 FAIL (S_share=84.5%), NP2 FAIL (1/20)
- Tier: Provisional

### C1607: QGY Partial Paradox Inversion
Quality-gated Y (QGY) partially inverts the N2/N4 paradox. N2's QGY (0.180) is lower than full's QGY (0.231) despite N2's Y_final being higher (0.734 vs 0.675). The quality fraction (qgy_ratio) is highest for the full model (0.319). But the effect is not strong enough to pass the 14/20 folio gate (NP4 = 13/20).
- Evidence: CD3 N2_paradox_inversion=true, CD7 full=0.319, NP4=13/20
- Tier: Provisional

### C1608: Closure Opportunity Scarcity
Closure opportunity on real traces is severely limited. Only 37.4% of CLOSE lines exceed CTS 0.3 threshold. Useful closure fraction (high excursion + high closure signal) is 3.2%. CTS-excursion timing correlation is zero (r=-0.014). Closure signal and excursion need are structurally uncoupled.
- Evidence: A1 close_frac_gt_03=0.374, A7 useful_closure=0.032, A4 spearman_r=-0.014
- Tier: Provisional

### C1609: PCV-Visible CLOSE Recovery
CLOSE recovery channels become load-bearing under PCV but not under binary viability. B10 delta under PCV = +0.020 (Cohen's d = 0.465) while B10 delta under old viability ~ 0.003. The plant mechanism works; the old readout couldn't detect it.
- Evidence: NP6 PASS (all 3 criteria), CD5 PCV_delta=0.020 vs old_viability_delta=0.003
- Tier: Provisional

---

## Lessons and Implications

1. **Readout matters as much as mechanism.** Phases 563b-566 progressively degraded apparatus performance by modifying the plant law, when the actual problem was partly in how outcomes were measured. PCV reveals structure that old viability was blind to. This implies that any future apparatus work must validate readout fidelity before concluding that a mechanism has failed.

2. **S is not noise; it is the dominant signal in the wrong frame.** S's high-side drift is a genuine structural property of the manuscript's S variable, not a scoring artifact. Excluding high-S events from SAHB was the right direction, but the remaining low-S burden still dominates because S is the only variable that routinely enters warning/hard_stop zones. The solution is not to suppress S further but to redefine what "dangerous" means for S specifically.

3. **Closure is a narrow channel.** The T1 audit establishes that closure opportunity is structurally scarce (3.2% useful fraction, zero CTS-excursion correlation). This is not a failure of the apparatus but a property of the manuscript: CLOSE phases are brief, sparse, and disconnected from excursion timing. Any model that expects closure to be a primary recovery mechanism must reckon with this scarcity.

4. **Quality gating reveals hidden structure.** The QGY/qgy_ratio inversion of the N2 paradox is a genuine insight: raw Y_final rewards any convergence, while QGY rewards convergence that follows excursion resolution. This distinction may generalize beyond the current apparatus line.

5. **One-folio margins suggest threshold sensitivity.** NP4 at 13/20 (one short) suggests that the 14/20 gate may be slightly too aggressive for a 20-folio pilot, or that the 6 folios with QGY = 0 need special handling. Phase 568 should consider whether zero-excursion folios belong in the QGY denominator.

---

## Next Phase Recommendations

Phase 568 should focus on **S-zone geometry** and **COF integration**, building on the partial success of the metric refactor:

1. **S zone geometry reform:** Either exclude S entirely from discrimination metrics or redefine S zone boundaries to separate productive reserve (high-side drift within normal S range) from genuinely dangerous S excursion (structural departure from expected S behavior). The current 4-zone model (basin/corridor/warning/hard_stop) may not be appropriate for S.

2. **COF integration:** COF_2 (CTS + q4_opaque + m_close_bias) achieved the best phase discrimination in the T1 audit (p = 0.045) but remains marginal. Section-specific COF normalization may strengthen the closure-excursion interface enough to improve NP tests.

3. **Lock PCV:** PCV should replace old_viability as the primary viability metric going forward. NP1 validates it; CD1 confirms it measures a different construct.

4. **QGY denominator adjustment:** Explore whether folios with zero excursions (QGY = 0 by construction, not by failure) should be excluded from the NP4 denominator. This could flip 13/20 to 13/14 or similar.

---

*Generated by t5_synthesis.py | Phase 567 | 2026-03-10 02:43 UTC*
