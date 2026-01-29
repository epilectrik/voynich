# AZC_REASSESSMENT Phase

## Objective

Determine whether A-B "routing" represents functional structure or statistical artifact, and if functional, at what granularity.

## Background

Investigation of A-B folio-level routing revealed troubling findings:
- Only 2-4 A folios serve all 82 B folios (degenerate assignment)
- Pool size dominates coverage (r=0.88)
- Only ~20% actual token overlap between best-match pairs
- No section-to-section routing (permutation p=0.57)

This phase tests whether the AZC routing model describes functional content-specific routing or merely shared vocabulary with size effects.

## Tests

| Test | Question | Falsification Threshold |
|------|----------|-------------------------|
| T1 | Does content predict B match after size control? | partial r > 0.15 |
| T2 | Do rare MIDDLEs show higher A-B specificity? | rho < -0.3 |
| T3 | Does material class align with B section? | Cramer's V > 0.2 |
| T4 | Is A-B exclusion asymmetric by role? | McNemar p < 0.01 |
| T5 | At what granularity is routing non-degenerate? | disc > 1.5, unique > 30 |
| T6 | Is observed matching distinguishable from random? | Real > 95th percentile |
| T7 | Is A folio homogeneity deliberate coverage optimization? | Overlap > 95th percentile |

## Results Summary

| Test | Result | Verdict |
|------|--------|---------|
| T1 | partial r = -0.038 | NO_SIGNAL |
| T2 | rho = +0.69 | COMMON_MORE_SPREAD |
| T3 | Cramer's V = 0.12 | WEAK_ALIGNMENT |
| T4 | McNemar p < 0.0001 | ASYMMETRIC_EXCLUSION |
| T5 | max disc = 1.12 | NO_GRANULARITY |
| T6 | real at 0th percentile | REAL_BELOW_SYNTHETIC |
| T7 | 11x higher overlap, z=1144 | COVERAGE_OPTIMIZED |

## Key Findings

1. **No content routing** (T1, T5): A content doesn't predict B folio match
2. **Shared vocabulary pattern** (T2): Common MIDDLEs spread to both A and B
3. **Role-aware filtering** (T4): Kernel tokens survive; auxiliary filtered
4. **A folios are deliberately homogeneous** (T6, T7): 11x more similar than random
5. **Coverage optimization** (T7): First 10 folios cover 60% of PP vocabulary

## Revised Model

A→AZC→B is **constraint propagation**, not **content routing**:
- A provides vocabulary coverage (homogeneous by design)
- AZC provides constraint gradients (position-indexed escape)
- B executes within constrained vocabulary (role-aware infrastructure preservation)

## Interpretation Guide

**If most tests show null results:**
- Routing model should be downgraded from "structural mechanism" to "statistical correlation from shared vocabulary"
- Reframe: "vocabulary FILTERING, not content ROUTING"

**If tests show positive results:**
- Routing model is supported at the identified granularity
- Document which granularity produces non-degenerate routing

## Scripts

- `t1_size_controlled_specificity.py` - Partial correlation controlling for pool size
- `t2_rare_vocabulary_fidelity.py` - Frequency stratification analysis
- `t3_material_class_alignment.py` - Section-vocabulary alignment
- `t4_exclusion_asymmetry.py` - Role-specific exclusion patterns
- `t5_operating_unit_discovery.py` - Granularity sweep (line to folio)
- `t6_null_model_comparison.py` - Real vs synthetic A folio discrimination

## Dependencies

- `scripts/voynich.py` (Transcript, Morphology)
- `phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json` (for T4)

## Provenance

Phase designed based on expert-advisor consultation regarding whether the AZC routing model is well-founded or potentially over-interpreted.
