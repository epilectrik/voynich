# Grammar System Constraints (C085-C114, C126-C144)

**Scope:** Kernel structure, hazard topology, executability
**Status:** CLOSED

---

## Kernel Structure (C085-C108)

### C085 - 10 Single-Character Primitives
**Tier:** 2 | **Status:** CLOSED
Primitives: s, e, t, d, l, o, h, c, k, r
**Source:** Phase 15

### C089 - Core Within Core
**Tier:** 2 | **Status:** CLOSED
Three kernel operators: k, h, e form the irreducible control core.
**Source:** Phase 15

### C090 - Cycle Topology
**Tier:** 2 | **Status:** CLOSED
500+ 4-cycles, 56 3-cycles in grammar graph. Note: Phase CYCLE found NO distinct semantics (100% token overlap).
**Source:** Phase 15, CYCLE

### C103 - k = ENERGY_MODULATOR
**Tier:** 2 | **Status:** CLOSED
Kernel 'k' controls energy input to system.
**Source:** Phase 17

### C104 - h = PHASE_MANAGER
**Tier:** 2 | **Status:** CLOSED
Kernel 'h' manages phase transitions and material state.
**Source:** Phase 17

### C105 - e = STABILITY_ANCHOR
**Tier:** 2 | **Status:** CLOSED
Kernel 'e' anchors system to stable state. 54.7% of recovery paths pass through 'e'.
**Source:** Phase 17

### C107 - Kernel Boundary-Adjacent
**Tier:** 2 | **Status:** CLOSED
All kernel nodes are BOUNDARY_ADJACENT to forbidden transitions. Kernel controls hazard proximity.
**Source:** Phase 17

---

## Hazard Topology (C109-C114)

### C109 - 5 Failure Classes
→ See [C109_hazard_classes.md](C109_hazard_classes.md)

### C110 - PHASE_ORDERING Dominant
**Tier:** 2 | **Status:** CLOSED
PHASE_ORDERING is 7/17 = 41% of forbidden transitions. Primary failure mode.
**Source:** Phase 18

### C111 - 65% Asymmetric
**Tier:** 2 | **Status:** CLOSED
65% of forbidden transitions are asymmetric (A→B forbidden, B→A allowed). SEL-D revision from prior "100% bidirectional" claim.
**Source:** Phase 18, SEL-D

### C112 - 59% Distant from Kernel
**Tier:** 2 | **Status:** CLOSED
59% of forbidden transitions occur distant from kernel operators. SEL-D revision from prior "KERNEL_ADJACENT clustering" claim.
**Source:** Phase 18, SEL-D

---

## Family Structure (C126-C144)

### C126 - 0 Cross-Family Contradictions
**Tier:** 2 | **Status:** CLOSED
Zero grammatical contradictions across 8 recipe families.
**Source:** Phase FSS

### C129 - Family Differences = Coverage Artifacts
**Tier:** 2 | **Status:** CLOSED
Apparent family differences explained by coverage variation, not distinct grammars.
**Source:** Phase FSS

### C141 - Cross-Family Transplant = Zero Degradation
**Tier:** 2 | **Status:** CLOSED
Transplanting text between families causes zero grammar degradation.
**Source:** Phase FSS

### C144 - Families Are Emergent
**Tier:** 2 | **Status:** CLOSED
Recipe families are emergent regularities, not designed categories.
**Source:** Phase FSS

---

## Illustration Independence (C137-C140)

### C137 - Swap Invariance Confirmed
**Tier:** 2 | **Status:** CLOSED
Swapping illustrations between folios has no effect on grammar. p=1.0
**Source:** Phase ILL

### C138 - Illustrations Don't Constrain Execution
**Tier:** 2 | **Status:** CLOSED
Text grammar is independent of illustration content.
**Source:** Phase ILL

### C139 - Grammar Recovered from Text-Only
**Tier:** 2 | **Status:** CLOSED
Full grammar structure recoverable without any illustration data.
**Source:** Phase ILL

### C140 - Illustrations Are Epiphenomenal
**Tier:** 2 | **Status:** CLOSED
Illustrations are decorative, not instructional. Do not affect execution.
**Source:** Phase ILL

---

## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
