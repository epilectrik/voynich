# Phase 579: FORGIVING POLE RESIDUAL AUDIT

## Status: COMPLETE

## Aim

Determine whether the 8 stubborn A2 forgiving folios (f39v, f40r, f50v, f55v, f85r2, f86v5, f86v6, f95r2) are a **structural endpoint** (inherent apparatus property) or a **parameter underfit** (fixable by F-axis retuning).

## Motivation

Phase 576 found the dominant intervention (regime admission gating, A2 delta=+0.0635, null wins 7->2). Phases 577-578 proved that refining the closure classifier cannot improve on Phase 576. The same 8 A2 forgiving folios remain forgiving across ALL gate configurations. The expert's verdict: "the remaining forgivingness is a folio-level apparatus property, not a local event-labeling error."

## Constraints

| ID | Subject | Verdict | Runtime |
|----|---------|---------|---------|
| C1663 | Pole coherence | GRADIENT_TAIL | T1 |
| C1664 | Channel concentration | CHANNEL_CONCENTRATED | T2 |
| C1665 | Opportunity confound | OPPORTUNITY_NEUTRAL | T3 |
| C1666 | Structural endpoint (DECISIVE) | MIXED_BOUNDARY_STRATUM | T4 |

## Scripts

| Script | Purpose | Runtime |
|--------|---------|---------|
| t0_pole_census.py | Data assembly + statistical characterization | 0.1s |
| t1_coherence_profiling.py | Coherence analysis + distance geometry | 0.01s |
| t2_channel_decomposition.py | R1-R5 sub-ablation for the 8 | 6.0s |
| t3_opportunity_geometry.py | Event count, CTS, strong-close opportunity | 0.02s |
| t4_constrained_retuning.py | F1xF2 grid sweep + conditional 3rd-axis | 115s |
| t5_synthesis.py | Constraints + REPORT_579.md | 0.01s |

## Key Dependencies

- Phase 572 (PRODUCTIVE_DISRUPTION_EXPANSION): M1/M4f runs, F1-F5 setup
- Phase 573 (A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES): 5-channel ablation, gap analysis
- Phase 574 (COUNTERFEIT_CLOSURE_THRESHOLD_RECOVERY_GATE_MAP): Per-event features, R1-R5 sub-ablation, landscape
- Phase 576 (CLOSURE_REGIME_ADMISSION_GATE): Gated DYE under AMB_PESSIMISTIC
