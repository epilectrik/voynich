# C542: Gateway/Terminal Hazard Class Asymmetry

**Tier:** 2 | **Status:** CLOSED | **Scope:** HAZARD_TOPOLOGY

---

## Statement

> Hazard-involved classes show gateway/terminal asymmetry: Class 30 (dar/dal) exclusively precedes hazards (gateway), while Class 31 (chey/shey) exclusively follows hazards (terminal).

---

## Gateway/Terminal Distribution

| Class | Role | Gateway | Terminal | Balance | Pattern |
|-------|------|---------|----------|---------|---------|
| 30 | FLOW | 7 | 0 | +1.00 | **Pure gateway** |
| 8 | ENERGY | 5 | 3 | +0.25 | Gateway-biased |
| 31 | ENERGY | 0 | 8 | -1.00 | **Pure terminal** |

---

## Interpretation

- **Class 30 (dar/dal)** = Entry point into hazard zones
- **Class 31 (chey/shey)** = Exit/recovery from hazards

This creates a grammatically-marked hazard envelope:
```
[normal operation] -> dar/dal -> [HAZARD ZONE] -> chey/shey -> [recovery]
```

The 100% asymmetry of Classes 30 and 31 suggests these are structural markers for hazard entry and exit, not incidental participants.

---

## Evidence

**Test:** `phases/INSTRUCTION_CLASS_CHARACTERIZATION/scripts/class_hazard_proximity.py`

- Analyzed forbidden transition bigrams in corpus
- Tracked which class precedes vs follows each hazard token pair
- Class 30: 7 gateway occurrences, 0 terminal
- Class 31: 0 gateway occurrences, 8 terminal

---

## Scope Clarification

**This constraint applies only to hazard-adjacent contexts** (the 15 occurrences where Class 30/31 tokens appear immediately before/after forbidden transition pairs).

When Class 30 and Class 31 co-occur in the same line WITHOUT a hazard between them, the ordering is NOT constrained by this finding. General co-occurrence shows only 40.4% gateway→terminal order (CLASS_SEMANTIC_VALIDATION phase), which is consistent with C542 since those cases lack the hazard-adjacency context.

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C111 | Extended - class-level manifestation of 65% asymmetry |
| C399 | Consistent - safe precedence pattern |
| C541 | Related - enumeration of hazard classes |

---

## Provenance

- **Phase:** INSTRUCTION_CLASS_CHARACTERIZATION
- **Date:** 2026-01-25
- **Script:** class_hazard_proximity.py

---

## Navigation

<- [C541_hazard_class_enumeration.md](C541_hazard_class_enumeration.md) | [C543_role_positional_grammar.md](C543_role_positional_grammar.md) ->
