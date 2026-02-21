# C1187: Sister-Pair Mechanism Is a Boundary Control Knob (Synthesis)

**Tier:** 2
**Scope:** B, sister pairs, program design
**Phase:** SISTER_PAIR_MECHANISM (Phase 420)
**Depends on:** C1179, C1180, C1181, C1182, C1183, C1184, C1185, C1186

## Statement

The 52.9% unexplained variance in sister-pair choice (C639) is NOT genuine free variation. It is a BOUNDARY_CONTROL_KNOB: sister preference modulates entry boundary dynamics (C1186: partial rho=0.312), is positionally mediated (C1180: +12.8% variance), dynamically consequential (C1181: AXM rho=-0.250, hazard rho=+0.255), and structured even within identical morphological slots (C1179: 14/174 Bonferroni-significant). The mechanism operates at moderate folio-level consistency (C1182: ICC=0.317) and is independent of vocabulary pipeline architecture (C1183). ch/sh and ok/ot are largely independent axes (C1184). Successor routing effects are MIDDLE-dependent, not universal (C1185), preserving C121's 49-class grammar.

## 8-Test Battery Summary

| Test | Verdict | Key Finding |
|------|---------|-------------|
| SP-0 Slot equivalence | STRUCTURED_IN_SLOT | 14/174 slots significant (p<0.0001) |
| SP-1 Positional mediation | POSITIONAL_MEDIATION | +12.8% R2, LOO confirmed |
| SP-2 Dynamical consequence | DYNAMICALLY_CONSEQUENTIAL | AXM -0.250, hazard +0.255 |
| SP-3 Concentration | MODERATE_CONSISTENCY | ICC=0.317 |
| SP-4 Bridge/dark coupling | BRIDGE_WEAK | Independent of pipeline (partial <0.16) |
| SP-5 ok/ot parallel | WEAK_COUPLING | Independent axes (partial=0.204) |
| SP-6 Successor routing | MIDDLE_DEPENDENT | 5/102 strata, global p=0.034 |
| SP-7 Boundary divergence | BOUNDARY_COUPLED | Entry JSD rho=0.312 (p=0.004) |

## Integrated Model

Sister choice (ch vs sh) is a within-class control parameter (C506.b, C1026) that:
1. **Positions differently in lines**: ch later (0.487), sh earlier (0.395)
2. **Modulates hazard exposure**: ch-heavy = higher hazard, lower AXM stability
3. **Modulates entry diversity**: ch-heavy = more divergent line openings
4. **Operates at program + paragraph level**: 32% folio-determined, 68% locally modulated
5. **Is independent of**: vocabulary pipeline (C1183), the other sister pair ok/ot (C1184)
6. **Does NOT reopen C121**: successor effects are MIDDLE-specific, not universal

This reduces C639's unexplained variance from 52.9% to approximately 40% (position alone absorbs ~13%), with the remaining fraction partially structured by dynamics and boundary effects.

## Provenance

- Phase 420: SISTER_PAIR_MECHANISM (8-test battery)
- Script: `phases/SISTER_PAIR_MECHANISM/scripts/sister_pair_mechanism.py`
- Results: `phases/SISTER_PAIR_MECHANISM/results/sister_pair_mechanism.json` -> synthesis
