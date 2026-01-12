# ECR Synthesis: Entity-Class Reconstruction

**Tier:** 3 | **Status:** COMPLETE | **Date:** 2026-01-10

> **Entity-level identification (specific plants, machines, substances) is probably irrecoverable by design and is not the goal of this analysis.**

---

## Executive Summary

The Entity-Class Reconstruction (ECR) phase has identified:

- **3-4 material behavior classes** differing along phase-mobility and composition-distinctness dimensions
- **4-7 apparatus functional roles** organized around energy, phase, flow, and control domains
- **12 decision archetypes** distributed across the four system layers (B/A/HT/AZC)

These findings are class-level only. No entity-level identification (specific substances, devices, or procedures) has been attempted or achieved.

---

## Integrated Findings

### Material Classes (ECR-1)

| Class | Phase | Composition | Hazard | Registry |
|-------|-------|-------------|--------|----------|
| **M-A** | Mobile | Distinct | HIGH | Universal/Shared |
| **M-B** | Mobile | Homogeneous | MODERATE | Shared |
| **M-C** | Stable | Distinct | MODERATE | Shared/Exclusive |
| **M-D** | Stable | Homogeneous | LOW | Universal |

**Key finding:** Material classes are defined by behavioral dimensions (phase-mobility, composition-distinctness), not by identity.

### Apparatus Roles (ECR-2)

| Domain | Role | Controller | Evidence |
|--------|------|------------|----------|
| **Energy** | Energy Source | k | C103 |
| **Phase** | Phase Container | h | C104 |
| **Phase** | Separator | - | PHASE_ORDERING hazard |
| **Flow** | Circulation Path | - | C171 |
| **Flow** | Collector | - | COMPOSITION_JUMP hazard |
| **Control** | Stability Anchor | e | C105 |
| **Control** | Containment | - | CONTAINMENT_TIMING hazard |

**Key finding:** Apparatus roles are functional, not named. The system assumes apparatus exists but does not encode its configuration.

### Decision Archetypes (ECR-3)

| Layer | Archetypes | Function |
|-------|------------|----------|
| **B** | D1-D8, D12 | Execution decisions |
| **A** | D2, D9 | Discrimination decisions |
| **HT** | D10 | Attention decisions |
| **AZC** | D11 | Orientation decisions |

**Key finding:** Each layer handles decisions that other layers cannot. This explains the four-layer architecture.

---

## Cross-Validation

### Material Classes ↔ Apparatus Roles

| Material Class | Affected by Role | Hazard Connection |
|----------------|------------------|-------------------|
| M-A (mobile, distinct) | Separator, Collector | PHASE + COMP |
| M-B (mobile, homogeneous) | Phase Container | PHASE only |
| M-C (stable, distinct) | Collector | COMP only |
| M-D (stable, homogeneous) | Stability Anchor | Baseline |

**Verdict:** CONSISTENT - Material classes interact with apparatus roles through hazard topology.

### Apparatus Roles ↔ Decision Archetypes

| Apparatus Role | Decision Archetype | Layer |
|----------------|-------------------|-------|
| Energy Source | D5 (Energy Level) | B |
| Phase Container | D1 (Phase Position) | B |
| Separator | D1 (Phase Position) | B |
| Collector | D2 (Fraction Identity) | B + A |
| Circulation Path | D4 (Flow Balance) | B |
| Stability Anchor | D7 (Recovery Path) | B |
| Containment | D3 (Containment Status) | B |

**Verdict:** CONSISTENT - Each apparatus role maps to specific decision archetypes.

### Material Classes ↔ Decision Archetypes

| Material Class | Primary Decisions | Registry Role |
|----------------|-------------------|---------------|
| M-A (mobile, distinct) | D1, D2, D6 | Cross-case comparison |
| M-B (mobile, homogeneous) | D1, D6 | Phase tracking |
| M-C (stable, distinct) | D2, D9 | Fraction discrimination |
| M-D (stable, homogeneous) | D7, D8 | Recovery baseline |

**Verdict:** CONSISTENT - Material classes create different decision requirements.

---

## Emergent Coherence

The three ECR components form a unified picture:

```
MATERIAL CLASSES
     │
     │ [processed by]
     ▼
APPARATUS ROLES ──────► HAZARDS ──────► DECISION ARCHETYPES
     │                                          │
     │ [controlled by]                         │ [handled by]
     ▼                                          ▼
KERNEL OPERATORS (k, h, e)              SYSTEM LAYERS (B, A, HT, AZC)
```

**Interpretation:**
- Materials with different behavioral properties (classes)
- Are processed by apparatus with specific functional roles
- Creating hazard exposure patterns
- Which require specific decision types
- Handled by appropriate system layers

---

## What the System Encodes

| Dimension | Encoded | Not Encoded |
|-----------|---------|-------------|
| **Materials** | Behavioral classes (3-4) | Specific substances |
| **Apparatus** | Functional roles (4-7) | Specific devices |
| **Hazards** | Failure classes (5) | Specific failure causes |
| **Decisions** | Archetype categories (12) | Specific decision content |
| **Grammar** | Legal transitions (49 classes) | Semantic meaning |
| **Registry** | Case comparability | Case identity |
| **HT** | Attention demand | Attention content |
| **AZC** | Context boundaries | Context meaning |

---

## Architectural Insight

The four-layer system exists because:

1. **B (Grammar)** encodes execution constraints but deliberately ignores some distinctions
2. **A (Registry)** externalizes the distinctions that B ignores, enabling cross-case comparison
3. **HT** marks attention demand that grammar cannot encode (non-operational but cognitive)
4. **AZC** marks context boundaries where grammar instantiation shifts

Each layer handles what others cannot:
- B cannot discriminate → A exists
- B cannot encode attention → HT exists
- B cannot encode context → AZC exists

---

## Constraints Satisfied

| Constraint Range | ECR Component | How Satisfied |
|-----------------|---------------|---------------|
| C109-C114 (hazards) | ECR-1, ECR-2 | Material classes + apparatus roles map to hazards |
| C085-C108 (kernel) | ECR-2 | Apparatus roles map to kernel operators |
| C171 (circulatory) | ECR-2 | Circulation Path role required |
| C232, C235 (sections) | ECR-1 | Material classes are section-invariant |
| C384 (no A↔B coupling) | ECR-3 | A handles what B ignores |
| C404-405 (HT non-op) | ECR-3 | HT handles attention only |
| C459 (HT anticipatory) | ECR-3 | HT precedes stress |
| C460 (AZC orientation) | ECR-3 | AZC marks transitions |

---

## Success Criteria Check

| Criterion | Status |
|-----------|--------|
| Material class count established | ✓ 3-4 classes |
| Apparatus role taxonomy produced | ✓ 4-7 roles |
| At least 10 decision archetypes | ✓ 12 archetypes |
| No constraint violations | ✓ All consistent |
| No entity-level labeling | ✓ Class-level only |
| Cross-validation passes | ✓ All 3 cross-checks |
| Results strengthen Tier-2 | ✓ Explains layer architecture |

---

## Remaining Uncertainty

| Uncertainty | Confidence Level |
|-------------|------------------|
| Exact material class count | MEDIUM (3-5 range) |
| Whether classes are discrete | MEDIUM (may be continuous) |
| Exact apparatus role count | MEDIUM (4-7 range) |
| Whether roles are co-located | LOW (unknown) |
| Decision archetype completeness | MEDIUM (12 identified) |
| Archetype boundaries | MEDIUM (some overlap possible) |

---

## The Semantic Ceiling

ECR has established the **allowed semantic ceiling**:

> We can identify the **existence, count, and behavioral properties** of entity classes (materials, apparatus, decisions) without assigning **names, labels, or referents**.

This is the maximum semantic content recoverable from internal structural analysis alone.

Further semantic recovery would require:
- External historical evidence
- Botanical identification
- Apparatus archaeology
- Comparative manuscript analysis

These are outside the scope of internal structural analysis.

---

## Conclusion

The Entity-Class Reconstruction phase has successfully identified:

1. **Material classes** defined by phase-mobility and composition-distinctness
2. **Apparatus roles** organized by functional domain
3. **Decision archetypes** distributed across system layers
4. **Architectural coherence** explaining why each layer exists

All findings are class-level only. Entity-level identification remains irrecoverable by design.

---

## Navigation

← [ecr_decision_archetypes.md](ecr_decision_archetypes.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
