# Grammar System Constraints (C085-C114, C126-C144)

**Scope:** Kernel structure, hazard topology, executability
**Status:** CLOSED

---

## Kernel Structure (C085-C108)

### C085 - 10 Single-Character Primitives
**Tier:** 2 | **Status:** CLOSED
Primitives: s, e, t, d, l, o, h, c, k, r
**Source:** Phase 15

**Compression Reality Note (2026-01-23):** These primitives also serve as compression hinges in superstring morphology (C517). Test 15-16 confirmed they are REAL OPERATORS with distinct functional roles, not compression artifacts. Evidence: directional asymmetry (e→h=0.00, h→e=7.00x) cannot arise from compression mechanics.

### C089 - Core Within Core
**Tier:** 2 | **Status:** CLOSED
Three kernel operators: k, h, e form the irreducible control core.
**Source:** Phase 15

**Compression Reality Note (2026-01-23):** Core primitives k, h, e exhibit one-way valve topology (C521). This directional asymmetry confirms functional operator status independent of their role as compression hinges.

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
**Tier:** 2 | **Status:** CLOSED | **Scope:** B
All kernel nodes are BOUNDARY_ADJACENT to forbidden transitions. Classes containing kernel characters tend to be hazard-involved.
**Source:** Phase 17

**Scope Clarification (KERNEL_STATE_SEMANTICS, 2026-01):**
This relationship is CORRELATIONAL, not causal. Classes with high k/h/e content are often in hazard-involved categories, but k/h/e character content does NOT determine forbidden transition participation. Evidence from T10:
- Class 10 (daiin): 0% k, 0% h, 0% e - yet participates in forbidden transitions
- Class 31 (chey): 0% k, 100% h, 65% e - yet also participates in forbidden transitions
- Both k-free and k-containing classes serve as forbidden transition sources

The forbidden transitions operate at CLASS level (which token types follow which), not CHARACTER level (which k/h/e characters are present). See C522 for layer independence.

### C521 - Kernel Primitive Directional Asymmetry
**Tier:** 2 | **Status:** CLOSED | **Scope:** B
**Source:** MIDDLE_SUBCOMPONENT_GRAMMAR (2026-01-23)

Kernel primitives (k, h, e) exhibit one-way valve topology at the character level.

**Note:** This constraint documents character-level (within-token) asymmetry only. See C522 for independence from class-level (between-token) execution constraints. These are distinct constraint regimes sharing a symbol substrate.

**SUPPRESSED transitions:**
| Transition | Ratio | Interpretation |
|------------|-------|----------------|
| e→h | 0.00 | STABILITY → PHASE: completely blocked |
| h→k | 0.22 | PHASE → ENERGY: strongly suppressed |
| e→k | 0.27 | STABILITY → ENERGY: strongly suppressed |

**ELEVATED transitions:**
| Transition | Ratio | Interpretation |
|------------|-------|----------------|
| h→e | 7.00x | PHASE → STABILITY: highly favored |
| k→e | 4.32x | ENERGY → STABILITY: favored |
| k→h | 1.10x | ENERGY → PHASE: neutral |

**Topology:**
```
     k (ENERGY_MODULATOR)
      ↓ (4.32x)
     e (STABILITY_ANCHOR) ←── h (PHASE_MANAGER)
                              (7.00x)
   [NO RETURN - blocked at 0.00-0.27]
```

**Interpretation:** Once execution reaches STABILITY_ANCHOR (e), return to ENERGY_MODULATOR (k) or PHASE_MANAGER (h) is blocked. Stabilization is an absorbing boundary at the primitive level.

**Supports:** C105 (e dominates recovery because it's absorbing), C332 (h→k suppression confirmed), C111 (65% asymmetry)

**Significance:** This directional asymmetry confirms kernel primitives are functional operators, not compression artifacts (addresses C517-C520 concern). Compression mechanics cannot create one-way valve topology.

### C522 - Construction-Execution Layer Independence
**Tier:** 2 | **Status:** CLOSED | **Scope:** B
**Source:** MIDDLE_SUBCOMPONENT_GRAMMAR (2026-01-23)

Character-level constraints (within-token composition) and class-level constraints (between-token transitions) are statistically independent.

**Evidence (Test 17):**
| Metric | Value |
|--------|-------|
| Pearson correlation | r = -0.21 |
| p-value | 0.07 (not significant) |
| Spearman rho | -0.15 |
| Category match rate | 28.4% (near random) |

**Key finding:** Pairs suppressed in construction are NOT suppressed in execution:
- Construction-suppressed pairs: only 2.9% also suppressed in execution
- Construction-elevated pairs: 0% also elevated in execution

**Architectural Implication:**

Three independent constraint layers share the same symbol substrate:

```
SYMBOL SUBSTRATE (10 primitives: s,e,t,d,l,o,h,c,k,r)
         |
         ├── CONSTRUCTION LAYER (C521)
         |     - Directional asymmetry within tokens
         |     - Result: Legal token forms
         |
         ├── COMPATIBILITY LAYER (C475)
         |     - MIDDLE atomic incompatibility
         |     - Result: Legal co-occurrence
         |
         └── EXECUTION LAYER (C109)
               - 17 forbidden transitions between classes
               - Result: Legal program paths
```

**Interpretation:** Kernel primitives exhibit real constraints at EACH level, but these are distinct constraint regimes, not propagation of a single constraint. The same `h` character participates in construction constraints, compatibility constraints, AND execution constraints - but these are three separate systems.

**Significance:** This independence explains how the manuscript achieves complex morphology, extreme vocabulary sparsity, AND execution safety simultaneously - these are independent constraint systems, not one system doing all three jobs.

**Additional Evidence (KERNEL_STATE_SEMANTICS, 2026-01):**

KERNEL_STATE_SEMANTICS phase tests T1-T10 provided strong confirmation:

| Test | Finding | Implication |
|------|---------|-------------|
| T1-T6 | Between-token k/h/e transitions are UNIFORM (O/E 0.87-1.21) | No execution-level k/h/e flow |
| T7 | Class-level transitions show STRONG structure (O/E 0.20-7.31) | Grammar is at class level |
| T9 | Within-token k/h/e transitions confirm C521 (5/5 claims) | Construction layer real |
| T10 | k/h/e content does NOT predict forbidden transition participation | Layers independent |

Key T10 findings:
- Class 10 (daiin): 0% k, 0% h, 0% e - participates in forbidden transitions
- Class 31 (chey): 0% k, 100% h, 65% e - participates in forbidden transitions
- Both k-free and k-containing classes can be forbidden sources
- Forbidden status is determined by CLASS identity, not k/h/e content

**Cross-references:** C521 (construction asymmetry), C475 (compatibility), C109 (execution hazards), C085 (shared primitives), C107 (boundary adjacency - correlational only)

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
