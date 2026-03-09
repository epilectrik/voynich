# C1579: CTS continuous closure encoding improves over categorical closure

**Tier:** 2
**Phase:** 562b (SECTION_TEMPLATE_TRACE_EXECUTOR closure+paragraph mini-audit)
**Scope:** B, closure, CTS, line, paragraph, Gaussian, encoding, C1434, C1440, C1566

## Claim

Replacing the categorical 5-class closure encoding (87% WORK_SEMI dominated) with a continuous Closure Transition Score (CTS) per line activates paragraph-level closure modulation that was previously impossible. E3 closure LL (paragraph LOO) exceeds E2 closure LL (folio): +0.039 improvement. CTS strongly correlates with q4_opaque_rate (r=0.81, p~0) and captures q3→q4 discontinuity (Mann-Whitney p=1.19e-29).

CTS is a 5-term weighted composite of T3 packet_state descriptors:
- 0.22 * closure_armed + 0.22 * norm(close_opacity_bias) + 0.28 * norm(m_close_bias) + 0.18 * norm(q4_shift_strength) + 0.10 * norm(q0q4_hazard_slope_pos)

Scored via Gaussian log-likelihood rather than categorical log-probability. All tokens on the same line share the same closure LL. The 5th term (q0q4_hazard_slope_pos) contributes nothing (p90=0 in all sections).

V1 (CTS vs packet_phase monotonicity) FAILS: SPEC median CTS (0.238) > CLOSE (0.203) > WORK (0.187). CTS captures closure properties that do not recapitulate packet_phase classification. V2 (folio-within-section CTS variance) FAILS: z=0.29 — CTS is section-driven, consistent with C1570.

## Evidence

- E2 closure: 0.187, E3 closure: 0.226 (+0.039)
- E4 closure: 0.221 (line-phase delta slightly counterproductive: -0.005 from E3)
- B5a: CTS vs q4_opaque_rate r=0.809, p~0
- B5b: CTS vs m_close_bias r=0.395, p=4.83e-87
- B5d: High-shift CTS=0.340 vs Low-shift CTS=0.268, Mann-Whitney p=1.19e-29
- V3 PASS: CTS range [0, 0.9], std=0.209

## Provenance

- T7: `phases/SECTION_TEMPLATE_TRACE_EXECUTOR/scripts/t7_closure_cts_redesign.py`
- T8: `phases/SECTION_TEMPLATE_TRACE_EXECUTOR/scripts/t8_revised_trace_executor.py`
- T9: `phases/SECTION_TEMPLATE_TRACE_EXECUTOR/scripts/t9_revised_validation.py`
- Builds on: C1434-C1439 (m-terminal closure valve), C1440-C1445 (terminal opacity), C1566 (Q3→Q4 discontinuity)
