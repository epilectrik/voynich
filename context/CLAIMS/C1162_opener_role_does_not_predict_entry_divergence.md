# C1162: Opener Role Does Not Predict Entry Divergence

**Tier:** 2
**Scope:** B, line, opener, entry divergence
**Phase:** ENTRY_RESET_MECHANISM (Phase 415)
**Depends on:** C1158, C959, C556

## Statement

The per-folio distribution of opener roles (5 roles: AUXILIARY 37.8%, ENERGY 38.2%, FLOW 5.4%, FREQUENT 11.5%, CORE_CONTROL 7.1%) explains only 12.8% of entry divergence variance (R²=0.128). No individual role fraction correlates with entry divergence at |rho|≥0.30 (best: ENERGY rho=-0.195, p=0.061). Opener role entropy is uncorrelated with entry divergence (rho=-0.116, p=0.101). The entry reset mechanism is not driven by what operational role opens the line.

## Evidence

| Role | Mean Fraction | rho vs Entry Div | p |
|------|--------------|-------------------|---|
| AUXILIARY | 0.378 | 0.075 | 0.092 |
| ENERGY_OPERATOR | 0.382 | -0.195 | 0.061 |
| FLOW_OPERATOR | 0.054 | -0.131 | 0.097 |
| FREQUENT_OPERATOR | 0.115 | -0.013 | 0.021 |
| CORE_CONTROL | 0.071 | 0.131 | 0.098 |

**Role entropy vs entry divergence:** rho=-0.116, p=0.101 (no relationship)

**OLS R²:** 0.128 (n=65 folios)

## Structural Implication

C959 established that the opener is a role marker, not an instruction header — token substitution within a role is free. C1162 extends this: not only is the specific token interchangeable, but the role itself is interchangeable with respect to entry dynamics. The entry reset mechanism operates below role-level identity. Two folios with identical opener role distributions can have very different entry divergence, because what matters is not what role opens the line but how the opener routes the system (C1163).
