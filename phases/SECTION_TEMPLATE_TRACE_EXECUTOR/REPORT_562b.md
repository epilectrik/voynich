# Phase 562b: Closure + Paragraph Cloud Mini-Audit

**Phase:** 562b
**Date:** 2026-03-09
**Verdict:** IMPROVED (CTS closure), DEGRADED (paragraph hazard blend)
**New constraints:** C1579-C1580

## Summary

Phase 562b tested two targeted improvements to the trace executor validated in Phase 562:

**Problem A (Closure):** The 5-class closure encoding was 87% dominated by WORK_SEMI, making the closure axis non-discriminative. T3 computes closure_armed, close_opacity_bias, m_close_bias, but T4 ignored them all (e4_closure = e2_closure).

**Problem B (Paragraph Cloud):** C1576 established that paragraph kNN doesn't improve per-token domain LL. The hypothesis was that paragraph cloud could instead modulate line-level hazard envelope expectations.

## Results

### CTS Closure (IMPROVED)

Replacing categorical 5-class closure with continuous CTS scored via Gaussian LL:
- E3 closure (0.226) > E2 closure (0.187): **+0.039** — paragraph-level closure modulation now works
- CTS correlates strongly with q4_opaque_rate (r=0.81)
- q3→q4 discontinuity captured (p=1.19e-29)
- V1 FAIL: SPEC median CTS > CLOSE > WORK (CTS doesn't recapitulate packet_phase)
- V2 FAIL: CTS is section-driven, not folio-individuated (consistent with C1570)

### Paragraph Hazard Blend (DEGRADED)

Blending paragraph envelope distribution (0.3) with folio envelope at E3:
- E3 hazard (-1.097) < E2 hazard (-1.092): **-0.005** — blend hurts
- Within-paragraph envelope std (0.563) >> between-paragraph (0.090)
- Paragraphs are NOT envelope-consistent

### Composite

| Level | Original | Revised | Delta |
|-------|----------|---------|-------|
| E1 | -3.364 | -3.023 | +0.340 |
| E2 | -3.293 | -2.937 | +0.355 |
| E3 | -3.293 | -2.920 | +0.373 |
| E4 | -3.283 | -2.911 | +0.373 |

Note: composite delta is primarily a scale change (Gaussian LL vs categorical log-prob on closure axis), not a discrimination improvement. The meaningful finding is E3 ≠ E2 (+0.017), driven by CTS paragraph modulation overwhelming hazard degradation.

Monotonicity E4 >= E3 >= E2 > E1: **HOLDS**

## Implications for Phase 563

1. **CTS closure should replace categorical closure** in the trace executor going forward
2. **Paragraph cloud should NOT be used as online hazard controller** — confirmed as offline trace-distribution validator only
3. **The hazard-slope term (q0q4_hazard_slope_pos)** contributes nothing (p90=0 in all sections) — can be dropped in future CTS iterations
4. **E4 line-phase delta for closure** is slightly counterproductive (-0.005) — consider disabling for closure while keeping for hazard

## Scripts

| Script | Purpose | Output |
|--------|---------|--------|
| t7_closure_cts_redesign.py | Compute CTS from T3 packet_state | t7_closure_cts.json |
| t8_revised_trace_executor.py | Re-run executor with CTS + hazard blend | t8_revised_traces.json |
| t9_revised_validation.py | Validate vs T4/T5 baseline | t9_revised_validation.json |
