# C1575: Hierarchical trace executor produces weakly monotonic improvement across 4 layers

**Tier:** 2
**Phase:** 562 (SECTION_TEMPLATE_TRACE_EXECUTOR)
**Scope:** B, structural, hierarchy, trace, executor, section, folio, paragraph, line, token, monotonic, C1572, C1573, C1574

## Claim

Section-template trace executor with 4-layer hierarchy produces weakly monotonic improvement in multi-axis token execution prediction (domain + hazard + routing + closure + headless): E4 >= E3 >= E2 > E1. Composite LL improvement: 2.39% from section-only (E1) to full hierarchical context (E4). E4 > E1 in all 5 sections. Wilcoxon E4 vs E1: z=-27.85, p=9.5e-171.

## Evidence

- Mean composite LL: E1=-3.3635, E2=-3.2928, E3=-3.2928, E4=-3.2832
- E2 accounts for ~87% of total improvement (section -> folio budget is primary)
- E3 = E2 for per-token LL (paragraph cloud does not improve token-level prediction)
- E4 improves over E2 via line-phase domain adjustment and hazard envelope
- Per-axis improvement (E4 vs E1): domain +0.046, hazard +0.020, routing +0.027, closure +0.008, headless +0.053
- All 3 ablations significant: phase adjustment (p=3.7e-58), routing mask (p=2.8e-3), hazard envelope (p~0)

## Provenance

- T4: `phases/SECTION_TEMPLATE_TRACE_EXECUTOR/scripts/t4_token_trace_executor.py`
- T5: `phases/SECTION_TEMPLATE_TRACE_EXECUTOR/scripts/t5_trace_validation.py`
- Builds on: C1572 (4-layer hierarchy), C1573 (paragraph cloud recovery), C1574 (headless folio-specific)
