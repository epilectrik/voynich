# C543: Role Positional Grammar

**Tier:** 2 | **Status:** CLOSED | **Scope:** POSITIONAL_GRAMMAR

---

## Statement

> Instruction class roles exhibit systematic line-position preferences: FLOW_OPERATOR is final-biased (mean 0.68), CORE_CONTROL is initial-biased (mean 0.45).

---

## Role Position Profiles

| Role | Mean Position | Tendency | Interpretation |
|------|---------------|----------|----------------|
| CORE_CONTROL | 0.45 | Initial-biased | Intervention triggers early |
| ENERGY_OPERATOR | 0.48 | Neutral | Distributed throughout |
| AUXILIARY | 0.53 | Neutral (high variance) | Context-dependent |
| FREQUENT_OPERATOR | 0.57 | Slightly final | Output marking late |
| FLOW_OPERATOR | **0.68** | **Final-biased** | Redirection at boundaries |

---

## Extreme Specialists

**LINE-INITIAL specialists:**
| Class | Role | Initial Rate | Tokens |
|-------|------|--------------|--------|
| 4 | AUXILIARY | 42.8% | ykeody, lkchedy |
| 26 | AUXILIARY | 40.9% | ykeedy, opchey |
| 10 | CORE_CONTROL | 35.1% | daiin |

**LINE-FINAL specialists:**
| Class | Role | Final Rate | Tokens |
|-------|------|------------|--------|
| 40 | FLOW_OPERATOR | **69.0%** | daly, aly, ary |
| 22 | AUXILIARY | 62.2% | ly, ry |
| 38 | FLOW_OPERATOR | 58.0% | aral, aldy |

---

## Evidence

**Test:** `phases/INSTRUCTION_CLASS_CHARACTERIZATION/scripts/class_position_analysis.py`

- Analyzed 2,409 lines with 2+ classified tokens
- Calculated relative position (0=initial, 1=final) for each class occurrence
- Role averages computed across all member classes

---

## Interpretation

FLOW_OPERATOR's final bias (0.68) reflects its function as execution terminator/redirector at control block boundaries. This extends prefix/suffix positional grammar (C371, C375) to the role level.

Class 40 (daly/aly) as strongest final specialist (69%) confirms its role as line-boundary flow operator.

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C371 | Extended - role-level positional patterns |
| C375 | Extended - role-level positional patterns |
| C357 | Consistent - line regularity |
| C358 | Extended - boundary token characterization |

---

## Provenance

- **Phase:** INSTRUCTION_CLASS_CHARACTERIZATION
- **Date:** 2026-01-25
- **Script:** class_position_analysis.py

---

## Navigation

<- [C542_gateway_terminal_asymmetry.md](C542_gateway_terminal_asymmetry.md) | [C544_energy_interleaving.md](C544_energy_interleaving.md) ->
