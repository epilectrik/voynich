# C546: Class 40 Safe Flow Operator

**Tier:** 2 | **Status:** CLOSED | **Scope:** HAZARD_TOPOLOGY

---

## Statement

> Class 40 (daly/aly/ary) is maximally distant from hazards (avg 4.22) despite being FLOW_OPERATOR, serving as a "safe flow" alternative to hazardous Classes 7 and 30.

---

## Distance from Hazards

| Class | Role | Avg Distance | Hazard Rate |
|-------|------|--------------|-------------|
| 7 | FLOW | 0.00 | 1.02% |
| 30 | FLOW | 2.03 | 1.57% |
| 38 | FLOW | - | 0% |
| **40** | **FLOW** | **4.22** | **0%** |

Class 40 has:
- Highest average distance from hazard tokens (4.22)
- Zero direct hazard participation
- Zero hazard exposure in corpus

---

## Positional Pattern

Class 40 is also the strongest LINE-FINAL specialist:

| Property | Value |
|----------|-------|
| Mean position | 0.85 |
| Final rate | 69.0% |
| Initial rate | 1.4% |

This suggests Class 40 operates at safe line-boundary positions, providing flow redirection without hazard risk.

---

## FLOW_OPERATOR Split

The FLOW_OPERATOR role contains both hazardous and safe classes:

| Class | Tokens | Hazard Status | Function |
|-------|--------|---------------|----------|
| 7 | ar, al | HAZARDOUS | Basic flow (hazard-adjacent) |
| 30 | dar, dal | HAZARDOUS | Gateway into hazards |
| 38 | aral, aldy | Safe | Compound flow |
| 40 | daly, aly | **SAFE** | Safe line-final flow |

---

## Interpretation

Class 40 provides a grammatical mechanism for safe flow redirection. When hazard-free line termination is needed, Class 40 tokens (daly, aly, ary) are used instead of hazardous alternatives (ar, dar).

This is consistent with:
- C400 (Boundary Hazard Depletion 5-7x)
- C399 (Safe Precedence Pattern)
- Designed safety architecture

---

## Evidence

**Test:** `phases/INSTRUCTION_CLASS_CHARACTERIZATION/scripts/class_hazard_proximity.py`

- Measured average distance to nearest hazard token for each class
- Class 40 has highest average distance (4.22) among all FLOW classes
- Zero hazard exposure despite high corpus frequency (72 tokens)

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C400 | Extended - class-level safe boundary operator |
| C399 | Consistent - safe precedence pattern |
| C541 | Related - Class 40 not in hazard enumeration |
| C543 | Related - Class 40 is line-final specialist |

---

## Provenance

- **Phase:** INSTRUCTION_CLASS_CHARACTERIZATION
- **Date:** 2026-01-25
- **Script:** class_hazard_proximity.py

---

## Navigation

<- [C545_regime_class_profiles.md](C545_regime_class_profiles.md) | [INDEX.md](INDEX.md) ->
