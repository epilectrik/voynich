# SEL-B: Internal Consistency & Tension Audit

**Phase:** SEL-B (Self-Evaluation - Consistency Audit)
**Date:** 2026-01-05
**Prerequisite:** SEL-A complete
**Status:** DESTRUCTIVE AUDIT (no repairs)

---

## SECTION A — CLAIM SET UNDER TEST

### Tier 0 Claims (from CLAUDE.md Model Boundary)

| ID | Statement | Tier | Tension Zones |
|----|-----------|------|---------------|
| T0-01 | "49 instruction classes, 100% coverage" | 0 | TZ-4 |
| T0-02 | "3 fixed operators (k, h, e) with mandatory waypoint (STATE-C)" | 0 | TZ-2, TZ-4 |
| T0-03 | "17 forbidden transitions in 5 failure classes" | 0 | TZ-4 |
| T0-04 | "100% execution convergence to STATE-C" | 0 | TZ-2 |
| T0-05 | "System is fundamentally MONOSTATE" | 0 | TZ-2 |
| T0-06 | "LINK Operator = Deliberate non-intervention" | 0 | TZ-5 |
| T0-07 | "Each folio is a complete, self-contained execution unit" | 0 | TZ-3 |
| T0-08 | "KERNEL_ADJACENT clustering" of hazards | 0 | TZ-4 |

### Tier 2 Claims (from OPS/OPS-R, post SEL-A)

| ID | Statement | Tier | Tension Zones |
|----|-----------|------|---------------|
| OPS1-01 | 83 folios yield 33 operational metrics | 2 | TZ-3 |
| OPSR-01 | Surface grammar compresses to 2-cycle latent oscillation | 2 | TZ-1, TZ-2 |
| OPSR-02 | Compression ratio = 24.5:1 | 2 | TZ-1 |
| OPSR-03 | Loops occur in state space not token space | 2 | TZ-1 |
| OPSR-04 | LINK = class of constraint-preserving trajectories | 2→3 | TZ-5 |
| OPSR-05 | Forward-progressing composition implements cyclic control | 2→3 | TZ-1 |
| OPS5-05 | LINK-CEI correlation = -0.7057 | 2 | TZ-5 |

---

## SECTION B — FORMAL DEFINITIONS IN USE

### TZ-1: Surface Irreversibility vs Latent Recurrence

**Definition of "surface irreversibility" (OPS-R line 141):**
> "Token space | Forward-progressing, non-repetitive | 75,248 unique positions"

**Definition of "latent recurrence" (OPS-R line 142):**
> "State space | Cyclic, recurrent | 2-cycle universal"

**Definition of "reconciliation" (OPS-R line 145):**
> "irreversibility at token level coexists with recurrence at state level"

**Flagged issues:**
- "Token space" and "state space" are not formally defined
- "State" is used without operational definition
- "Cyclic" at state level is asserted, not demonstrated
- The mapping from tokens to states is described as "many-to-one" but the mapping function is not specified

---

### TZ-2: MONOSTATE (STATE-C) vs 2-State Oscillation

**Definition of MONOSTATE (CLAUDE.md line 1331):**
> "System is fundamentally MONOSTATE"

**Definition of STATE-C (CLAUDE.md line 98):**
> "3 fixed operators (k, h, e) with mandatory waypoint (STATE-C)"

**Definition of 2-cycle (OPS-R line 31):**
> "Dominant 2-cycle at execution level (universal across all 83 folios)"

**Definition of compression (OPS-R lines 61-62):**
> "49 surface classes → 2 latent oscillation states → 1 terminal attractor"
> "Effective compression: **49:2:1**"

**Flagged issues:**
- "MONOSTATE" (single state) and "2-cycle oscillation" (two states) are terminologically contradictory
- OPS-R uses "2 latent oscillation states" but CLAUDE.md uses "MONOSTATE"
- STATE-C is described as both "terminal attractor" and "mandatory waypoint"
- "Oscillation" implies alternation between states; "convergence to STATE-C" implies collapse to one state
- No explicit definition of what constitutes a "state" vs a "waypoint"

---

### TZ-3: One Folio = One Executable Program

**Definition (CLAUDE.md line 102):**
> "**Folio = Atomic Program** | Each folio is a complete, self-contained execution unit | Phase 22: 83 folios enumerated, 75,248 instructions"

**Supporting claim (OPS-1):**
> "All 83 folios present | PASS"
> "No collapsed folios | PASS"

**Flagged issues:**
- "Atomic" is not defined (indivisible? minimal? isolated?)
- "Self-contained" is not defined (no external dependencies? no cross-references?)
- No definition of what would constitute a "partial" or "composite" program
- No explicit statement of what observations would violate this claim
- The claim conflates physical unit (folio) with logical unit (program)

---

### TZ-4: Kernel Primacy & Hazard Locality

**Definition of kernel (CLAUDE.md line 1343):**
> "Core within core: k, h, e (centrality 4847, 2968, 2181)"

**Definition of kernel adjacency (CLAUDE.md line 1348):**
> "All kernel nodes BOUNDARY_ADJACENT to forbidden transitions"

**Definition of hazard clustering (CLAUDE.md line 1357):**
> "KERNEL_ADJACENT clustering"

**Flagged issues:**
- "KERNEL_ADJACENT" appears to be both a finding (hazards cluster near kernel) and a definition (what makes something kernel-related)
- Centrality is a graph metric; "kernel" is a functional label; these are not the same
- "Boundary-adjacent" is spatial metaphor applied to graph structure
- No definition of what would constitute non-kernel-adjacent hazard distribution

---

### TZ-5: LINK as Control Action vs Non-Intervention Descriptor

**Definition 1 (CLAUDE.md line 101):**
> "**LINK Operator** | Deliberate non-intervention (distinct from other operators)"

**Definition 2 (OPS-R line 67):**
> "LINK is a **class of constraint-preserving trajectories**, not a single constant operator"

**Definition 3 (OPS-R line 161):**
> "LINK represents 'deliberate waiting' regardless of surface realization"

**Definition 4 (OPS-R lines 162-164):**
> "The class is defined by:
> 1. Non-intervention (no state change)
> 2. Hazard preservation (no forbidden transition approach)
> 3. CEI dampening (reduces engagement intensity)"

**Flagged issues:**
- LINK is called an "operator" (action) and "non-intervention" (absence of action) simultaneously
- "Class of trajectories" (set of paths) vs "operator" (single function) is terminological shift
- "Deliberate waiting" assigns intentionality; "constraint-preserving trajectories" is structural
- "No state change" contradicts participation in "2-cycle oscillation"
- If LINK causes "no state change," how does it participate in cycles?

---

## SECTION C — CONSISTENCY TEST RESULTS

### TZ-1 — Surface Irreversibility vs Latent Recurrence

**Verdict:** ⚠️ Consistent only under loose / narrative interpretation

**Minimal reason:**
- "Token space" and "state space" are not formally defined
- The mapping function from tokens to states is not specified
- "Irreversibility" and "recurrence" are asserted at different levels without formal layer separation
- The claim that both properties are "forced by the same data" is not demonstrated; they are derived from different analyses

---

### TZ-2 — MONOSTATE (STATE-C) vs 2-State Oscillation

**Verdict:** ❌ Internally inconsistent

**Minimal reason:**
- "MONOSTATE" = single state system (from CLAUDE.md Constraint 84)
- "2-cycle oscillation" = alternation between two states (from OPS-R)
- These are logically contradictory unless "state" means different things
- No explicit disambiguation is provided
- The compression "49:2:1" implies three distinct levels (49 classes, 2 oscillation states, 1 attractor), but MONOSTATE implies only one

---

### TZ-3 — One Folio = One Executable Program

**Verdict:** ⚠️ Consistent only under loose / narrative interpretation

**Minimal reason:**
- "Atomic" and "self-contained" are not formally defined
- No negative criterion (what would falsify this claim) is specified
- The claim is consistent with the data but not forced by it
- Alternative interpretations (folios as chapters, fragments, or variants) are not formally excluded

---

### TZ-4 — Kernel Primacy & Hazard Locality

**Verdict:** ⚠️ Consistent only under loose / narrative interpretation

**Minimal reason:**
- "KERNEL_ADJACENT" is used as both observation and category, risking circularity
- Centrality and kernel identity are conflated
- The claim that hazards cluster near kernel nodes could be an artifact of how "kernel" is defined
- No null hypothesis or alternative distribution is specified for comparison

---

### TZ-5 — LINK as Control Action vs Non-Intervention Descriptor

**Verdict:** ❌ Internally inconsistent

**Minimal reason:**
- LINK is defined as "non-intervention (no state change)" (OPS-R line 162)
- LINK participates in "2-cycle oscillation" which requires state transitions
- If LINK causes no state change, it cannot participate in oscillation
- If LINK does participate in oscillation, it causes state change and is not "non-intervention"
- The term shifts between "operator," "class of trajectories," and "waiting" without formal reconciliation

---

## SECTION D — UNRESOLVED TENSIONS

### D.1 MONOSTATE vs 2-Cycle (TZ-2)

| Issue | Type |
|-------|------|
| "MONOSTATE" (1 state) vs "2-cycle oscillation" (2 states) | **Contradiction** |
| No formal definition of "state" | Ambiguity |
| STATE-C as "attractor" vs STATE-C as "waypoint" | Equivocation |

---

### D.2 LINK as Non-Intervention in Cyclic System (TZ-5)

| Issue | Type |
|-------|------|
| "No state change" vs participation in oscillation | **Contradiction** |
| "Operator" vs "class of trajectories" | Equivocation |
| "Deliberate waiting" (intentional) vs "constraint-preserving" (structural) | Dual use |

---

### D.3 Undefined Layer Separation (TZ-1)

| Issue | Type |
|-------|------|
| "Token space" not formally defined | Ambiguity |
| "State space" not formally defined | Ambiguity |
| Mapping function not specified | Incompleteness |

---

### D.4 Circular Kernel Definition (TZ-4)

| Issue | Type |
|-------|------|
| "KERNEL_ADJACENT" used as finding and category | Potential circularity |
| Centrality ≠ functional primacy | Conflation |

---

### D.5 Folio = Program Assumption (TZ-3)

| Issue | Type |
|-------|------|
| "Atomic" undefined | Ambiguity |
| "Self-contained" undefined | Ambiguity |
| No falsification criterion | Incompleteness |

---

## SECTION E — DEPENDENCY IMPACT ANALYSIS

### E.1 MONOSTATE vs 2-Cycle Contradiction

**Dependent claims:**
- T0-04: 100% execution convergence to STATE-C
- T0-05: System is fundamentally MONOSTATE
- OPSR-01: Surface grammar compresses to 2-cycle latent oscillation
- OPSR-02: Compression ratio = 24.5:1

**Impact classification:** **PILLAR-LEVEL**
- If "MONOSTATE" and "2-cycle" cannot be reconciled, either OPS-R or the frozen model requires revision
- The compression ratio 49:2:1 depends on both claims being true simultaneously

---

### E.2 LINK Non-Intervention vs Oscillation Participation

**Dependent claims:**
- T0-06: LINK Operator = Deliberate non-intervention
- OPSR-04: LINK = class of constraint-preserving trajectories
- OPS5-05: LINK-CEI correlation = -0.7057
- OPS7-02: Waiting is the default (OPS-7 doctrine)

**Impact classification:** **PILLAR-LEVEL**
- LINK is central to OPS-5 (CEI), OPS-6 (navigation), OPS-7 (doctrine)
- If LINK's definition is internally inconsistent, these depend on an unstable construct

---

### E.3 Undefined Layer Separation

**Dependent claims:**
- OPSR-01: Surface grammar compresses to 2-cycle latent oscillation
- OPSR-03: Loops occur in state space not token space
- OPSR-05: Forward-progressing composition implements cyclic control

**Impact classification:** **LOCAL**
- Affects OPS-R reconciliation specifically
- Does not directly threaten Tier 0 claims if layers are defined formally

---

### E.4 Circular Kernel Definition

**Dependent claims:**
- T0-02: 3 fixed operators (k, h, e) with mandatory waypoint
- T0-08: KERNEL_ADJACENT clustering of hazards

**Impact classification:** **LOCAL**
- If kernel identity is circular, the hazard clustering claim is tautological
- Does not threaten other pillars if kernel is redefined operationally

---

### E.5 Folio = Program Assumption

**Dependent claims:**
- T0-07: Each folio is a complete, self-contained execution unit
- OPS1-01: 83 folios yield 33 operational metrics

**Impact classification:** **LOCAL**
- All OPS metrics are per-folio; assumption is load-bearing for OPS-1
- Does not threaten grammar or hazard claims if folios are redefined

---

## SECTION F — SEL-B VERDICT (NON-NARRATIVE)

### Pillar Status

| Pillar | Status |
|--------|--------|
| Grammar (49 classes, 100% coverage) | STABLE |
| Hazard topology (17 transitions, 5 classes) | STABLE (but TZ-4 circularity concern) |
| Convergence (MONOSTATE / STATE-C) | **DESTABILIZED** by TZ-2 contradiction |
| LINK operator | **DESTABILIZED** by TZ-5 contradiction |
| Folio = Program | Underdetermined (TZ-3) |

### Tier 0 Threat Assessment

| Claim | Threatened? | Reason |
|-------|-------------|--------|
| T0-01 (49 classes) | No | — |
| T0-02 (k, h, e kernel) | No | — |
| T0-03 (17 forbidden) | No | — |
| T0-04 (100% convergence) | **YES** | Contradicts 2-cycle oscillation unless "state" is disambiguated |
| T0-05 (MONOSTATE) | **YES** | Contradicts 2-cycle oscillation |
| T0-06 (LINK = non-intervention) | **YES** | Contradicts oscillation participation |
| T0-07 (folio = program) | Underdetermined | Definition incomplete |
| T0-08 (KERNEL_ADJACENT) | Underdetermined | Potential circularity |

### Issue Classification

| Issue | Type |
|-------|------|
| MONOSTATE vs 2-cycle | **Formal contradiction** |
| LINK non-intervention vs oscillation | **Formal contradiction** |
| Layer separation (token/state) | **Linguistic ambiguity** |
| Kernel definition | **Potential circularity** |
| Folio = program | **Definitional incompleteness** |

### Continuation Recommendation

| Phase | Proceed? | Condition |
|-------|----------|-----------|
| SEL-C (Scope Audit) | YES | TZ-2 and TZ-5 must be flagged as unresolved |
| SEL-D (External Comparison) | YES | With caution; internal model unstable |
| SEL-E (Final Assessment) | YES | After SEL-C |

---

## Summary

**Two formal contradictions identified:**
1. MONOSTATE (1 state) vs 2-cycle oscillation (2 states)
2. LINK as non-intervention vs LINK participation in oscillation

**Three ambiguities identified:**
1. "Token space" and "state space" undefined
2. "Kernel" definition potentially circular
3. "Folio = atomic program" not formally specified

**Pillar impact:**
- Convergence pillar: DESTABILIZED
- LINK pillar: DESTABILIZED
- Grammar and hazard pillars: STABLE

**Tier 0 claims T0-04, T0-05, T0-06 are internally threatened.**

---

*SEL-B complete. No repairs proposed. Contradictions exposed.*

*Generated: 2026-01-05*
