# C1578: E4 improvement sources are line-phase domain adjustment and hazard envelope

**Tier:** 2
**Phase:** 562 (SECTION_TEMPLATE_TRACE_EXECUTOR)
**Scope:** B, line, phase, domain, hazard, envelope, routing, closure, ablation

## Claim

E4 trace improvement over E2 comes from two specific sources: (1) dampened line-phase domain adjustment (domain axis +0.008 vs E2, ablation p=3.7e-58) and (2) hazard envelope adjustment (hazard axis +0.004 vs E2, ablation p~0). Routing and headless axes remain at folio level (no line-level improvement). Closure phase gating is counterproductive (WORK_SEMI at 87% dominance makes any redistribution harmful to LL) and was disabled.

This identifies the line safety packet's mechanistic contribution to the trace: line position modulates domain expectations (via SPEC/WORK/CLOSE phase), and line-level hazard characterization (SAFE_OPEN/THERMAL_INTERIOR/DANGEROUS_CLOSE) refines hazard posture prediction. The packet does NOT modulate routing, closure, or headless at the line level — these are folio-parameterized.

## Evidence

- E4 vs E2: domain -1.5663 vs -1.5739 (+0.008), hazard -1.0878 vs -1.0917 (+0.004)
- E5 ablation (minus phase adj): p=3.7e-58
- E6 ablation (minus routing mask): p=2.8e-3
- E7 ablation (minus hazard envelope): p~0
- Closure mask disabled: softened masks at any intensity degrade closure axis LL

## Provenance

- T4, T5: `phases/SECTION_TEMPLATE_TRACE_EXECUTOR/scripts/`
- Builds on: C1572 (line layer selective for hazard/closure features)
