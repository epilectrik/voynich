# Global Fit Registry

> **No entry in this file constrains the model.**

**Version:** 2.1 | **Last Updated:** 2026-01-11 | **Fit Count:** 3

---

## Entity-Class Reconstruction (ECR) Fits

### F-ECR-001 - Material-Class Identification

**Tier:** F3 | **Result:** SUCCESS | **Supports:** C109-C114, C232

#### Question
Can behavioral material classes be inferred from frozen constraints without naming specific substances?

#### Method
Constraint-driven inference using hazard topology (C109-C114), registry patterns (F-A-007, F-A-009), and section conditioning (C232).

Evidence sources:
- Hazard topology: PHASE_ORDERING (41%) + COMPOSITION_JUMP (24%) = 65% of hazards
- Registry structure: 8 prefix families with 2 equivalence pairs (ch/sh, ok/ot)
- Universality bands: Exclusive 3%, Shared 48%, Universal 45%

Success criteria:
- Minimal class count satisfies all constraints
- Classes are behavioral, not identity-based
- Cross-validation against registry patterns

#### Result Details
- Minimum class count: 4 (2x2 structure from phase mobility × composition distinctness)
- M-A (mobile, distinct): 65% hazard exposure, Universal/Shared registry
- M-B (mobile, homogeneous): Moderate hazard, Shared registry
- M-C (stable, distinct): Moderate hazard, Shared/Exclusive registry
- M-D (stable, homogeneous): Low hazard, Universal registry (baseline)
- Stress tests passed: B-1 (mobility discrete), B-3 (M-B ≠ M-D), B-4 (cannot collapse to 3)
- Partial resistance: B-2 (composition could subdivide at A-layer)

#### Interpretation
The 2x2 material class structure is the minimum dimensionality that satisfies all frozen constraints. Phase mobility and composition distinctness are the primary behavioral axes. The grammar treats these as discrete categories (not continuous gradients). Classes explain why A vocabulary shows universal preference—stable baseline classes (M-D) are safe across all contexts.

#### Limitations
Does NOT establish:
- What specific substances the classes contain
- How to identify class membership from tokens
- Whether all 4 combinatorial classes are populated
- Token-to-material mappings of any kind

See [ecr_stress_tests.md](ecr_stress_tests.md) for detailed stress test results.

---

### F-ECR-002 - Apparatus-Role Identification

**Tier:** F3 | **Result:** SUCCESS | **Supports:** C085-C108, C171, C216

#### Question
Can functional apparatus roles be inferred from kernel structure and operational constraints without naming specific devices?

#### Method
Role inference using:
- Kernel operators: k (ENERGY_MODULATOR), h (PHASE_MANAGER), e (STABILITY_ANCHOR)
- Circulatory requirement (C171): Closed-loop process control
- Hybrid hazard model (C216): 71% batch-focused, 29% apparatus-focused
- Regime structure (C179-C185): 4 operating regimes

Success criteria:
- Roles are functional positions, not device names
- Roles explain kernel operator behavior
- Roles consistent with hazard topology

#### Result Details
- Required roles (structurally mandated):
  - Energy Source Role (k-controlled): Controls energy input
  - Phase Container Role (h-controlled): Manages phase transitions
  - Circulation Path Role (C171): Material cycles through apparatus
  - Stability Anchor Role (e-controlled): 54.7% of recovery paths
- Implied roles (hazard-consistent):
  - Separator Role: PHASE_ORDERING hazard (41%)
  - Collector Role: COMPOSITION_JUMP hazard (24%)
  - Containment Role: CONTAINMENT_TIMING hazard (24%)
- Role-to-regime mapping verified across all 4 regimes
- Apparatus hazards (29%) require immediate response (zero LINK nearby)

#### Interpretation
4-7 apparatus functional roles are derivable from frozen constraints. The system assumes apparatus exists but does NOT encode its configuration—operator is expected to know physical setup (OPS-7: EXPERT_REFERENCE archetype). Apparatus hazards require faster response than batch hazards. The 29% apparatus-focused hazard rate explains why some transitions have no waiting option.

#### Limitations
Does NOT establish:
- What specific devices fill each role
- Physical construction or materials
- Spatial arrangement of apparatus
- Whether distinct devices map to each role (vs. co-located roles)

---

### F-ECR-003 - Decision-State Semantics

**Tier:** F3 | **Result:** SUCCESS | **Supports:** C384, C404-C405, C459-C460

#### Question
Can decision archetypes be identified that explain why each system layer (A/B/AZC/HT) exists?

#### Method
Map entity classes + grammar + hazards → decision archetypes.

Sources:
- 5 hazard classes (C109) → D1-D5 archetypes
- OPS doctrine → D6-D8 archetypes
- Kernel operators → D7 refinement
- Layer structure (C384, C404-405, C459-460) → D9-D11 archetypes
- Regime structure (C179) → D12 archetype

Success criteria:
- Each layer handles specific archetype classes
- Layers exist because other layers cannot handle their archetypes
- Decision types identifiable without decision content

#### Result Details
12 decision archetypes identified:
- D1 (Phase Position): PHASE_ORDERING, B-layer
- D2 (Fraction Identity): COMPOSITION_JUMP, B+A layers
- D3 (Containment Status): CONTAINMENT_TIMING, B-layer
- D4 (Flow Balance): RATE_MISMATCH, B-layer
- D5 (Energy Level): ENERGY_OVERSHOOT, B-layer
- D6 (Wait vs Act): LINK (38%), B-layer
- D7 (Recovery Path): e-operator, B-layer
- D8 (Restart Viability): C182, B-layer
- D9 (Case Comparison): A registry, A-layer
- D10 (Attention Focus): HT (C459), HT-layer
- D11 (Context Orientation): AZC (C460), AZC-layer
- D12 (Regime Recognition): C179, B-layer

Layer-to-archetype mapping:
- B handles execution: D1, D3, D4, D5, D6, D7, D8, D12
- A handles discrimination: D2, D9
- HT handles attention: D10
- AZC handles orientation: D11

#### Interpretation
Each layer exists because other layers cannot handle its decisions:
- B cannot discriminate cases → A exists (C384: no entry-level coupling)
- B cannot encode attention demand → HT exists (C404-405: non-operational)
- B cannot mark context shifts → AZC exists (C460: orientation markers)

This is the "semantic ceiling"—we can identify decision TYPES without knowing decision CONTENT. The four-layer structure is not arbitrary; it reflects what each encoding layer can and cannot express.

#### Limitations
Does NOT establish:
- What specific decisions the operator makes
- Content of any decision
- Procedural instructions or recipes
- Whether all 12 archetypes are equally important

---

## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
