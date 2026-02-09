# ECR-3: Decision-State Semantics

**Tier:** 3 | **Status:** ACTIVE | **Date:** 2026-01-10

> **Entity-level identification (specific plants, machines, substances) is probably irrecoverable by design and is not the goal of this analysis.**

---

## Objective

Map **entity classes + grammar + hazards** → **decision archetypes**, and explain why each system layer (A/B/AZC/HT) exists.

---

## Decision Archetype Framework

A decision archetype is a **situation type** where the operator must make a judgment call. The system encodes these situations without specifying what the operator should do.

---

## Hazard-Derived Decision Archetypes

### From 5 Failure Classes (C109)

| Failure Class | % | Decision Archetype |
|---------------|---|-------------------|
| PHASE_ORDERING | 41% | "Is material in correct phase/location?" |
| COMPOSITION_JUMP | 24% | "Is this the right fraction to collect?" |
| CONTAINMENT_TIMING | 24% | "Is pressure/overflow imminent?" |
| RATE_MISMATCH | 6% | "Is flow balance maintained?" |
| ENERGY_OVERSHOOT | 6% | "Is energy input appropriate?" |

### From OPS Doctrine

| Principle | Decision Archetype |
|-----------|-------------------|
| Waiting is default (38%) | "Should I intervene or wait?" |
| Escalation irreversible | "Can I afford this escalation?" |
| Restart requires low-CEI | "Can I restart from here?" |
| Throughput transient | "Can I sustain this intensity?" |

### From Kernel Structure

| Operator | Decision Archetype |
|----------|-------------------|
| k (ENERGY_MODULATOR) | "Should I adjust energy?" |
| h (PHASE_MANAGER) | "Should I trigger phase change?" |
| e (STABILITY_ANCHOR) | "Should I move toward stability?" |

---

## Complete Decision Archetype Catalog

| # | Archetype | Hazard/Source | Layer | Description |
|---|-----------|---------------|-------|-------------|
| **D1** | Phase Position | PHASE_ORDERING | B | "Is material where it should be in phase space?" |
| **D2** | Fraction Identity | COMPOSITION_JUMP | B + A | "Is this the fraction I think it is?" |
| **D3** | Containment Status | CONTAINMENT_TIMING | B | "Is containment secure?" |
| **D4** | Flow Balance | RATE_MISMATCH | B | "Are inputs and outputs balanced?" |
| **D5** | Energy Level | ENERGY_OVERSHOOT | B | "Is energy appropriate?" |
| **D6** | Wait vs Act | LINK (38%) | B | "Should I intervene or wait?" |
| **D7** | Recovery Path | e-operator | B | "How do I return to stability?" |
| **D8** | Restart Viability | C182 | B | "Can I restart from this state?" |
| **D9** | Case Comparison | A registry | A | "Is this case like that previous case?" |
| **D10** | Attention Focus | HT (C459) | HT | "Where should I be vigilant?" |
| **D11** | Context Orientation | AZC (C460) | AZC | "Where am I in the process?" |
| **D12** | Regime Recognition | C179 | B | "What operating regime am I in?" |

---

## Layer-to-Archetype Mapping

### Currier B (Grammar): Execution Decisions

**Archetypes handled:** D1, D3, D4, D5, D6, D7, D8, D12

**Function:** Encodes what transitions are legal, what states are stable, what hazards must be avoided.

**Why B exists:**
- To constrain execution to safe paths
- To maintain system within viability envelope
- To enable recovery from off-nominal states

### Currier A (Registry): Discrimination Decisions

**Archetypes handled:** D2, D9

**Function:** Enables comparison between cases that grammar treats identically.

**Why A exists:**
- Grammar intentionally collapses some distinctions (C384: no entry-level coupling)
- Some distinctions are decision-relevant but not grammar-relevant
- Operator needs to know "is this case like that case" for expert judgment
- Registry externalizes what grammar cannot track

**Key insight:** A exists precisely BECAUSE B deliberately ignores certain distinctions.

### Human Track (HT): Attention Decisions

**Archetype handled:** D10

**Function:** Marks where human vigilance is elevated.

**Why HT exists:**
- Some situations require extra attention (C459: anticipatory compensation)
- Grammar cannot encode "pay more attention here"
- HT precedes stress (anticipatory, not reactive)
- Operator needs preparation for high-demand sections

**Key insight:** HT is non-operational (C404-405) but cognitively functional.

### AZC (Hybrid): Orientation Decisions

**Archetype handled:** D11

**Function:** Marks section transitions and cognitive boundaries.

**Why AZC exists:**
- Different sections instantiate same grammar differently (C232)
- Operator needs to know which context applies
- AZC positioned at natural HT transition zones (C460)
- Orientation, not control

---

## Why Each Layer Cannot Handle Other Layers' Archetypes

| Layer | Cannot Handle | Reason |
|-------|---------------|--------|
| **B** | D9 (comparison) | Grammar collapses distinctions intentionally |
| **B** | D10 (attention) | Grammar is execution logic, not cognitive load |
| **B** | D11 (orientation) | Grammar is context-free within execution |
| **A** | D1-D8 (execution) | Registry is lookup, not control flow |
| **A** | D10 (attention) | Registry is static, not attention-modulated |
| **HT** | D1-D9 (any operational) | HT is non-operational (C404-405) |
| **AZC** | D1-D9 (any operational) | AZC constrains legality, not behavior (C313) |

---

## Decision Situations by Hazard Severity

### HIGH HAZARD (Immediate Decision Required)

| Archetype | Hazard | LINK Nearby | Constraint |
|-----------|--------|-------------|------------|
| D5 (Energy Level) | ENERGY_OVERSHOOT | ZERO | Apparatus-focused |
| D3 (Containment) | CONTAINMENT_TIMING | ZERO | Apparatus-focused |

These require immediate response (no waiting allowed).

### MODERATE HAZARD (Decision Can Wait)

| Archetype | Hazard | LINK Nearby | Constraint |
|-----------|--------|-------------|------------|
| D1 (Phase Position) | PHASE_ORDERING | Yes | Batch-focused |
| D2 (Fraction Identity) | COMPOSITION_JUMP | Yes | Batch-focused |

These allow monitoring before decision.

### LOW HAZARD (Standard Operation)

| Archetype | Context | LINK | Constraint |
|-----------|---------|------|------------|
| D6 (Wait vs Act) | Normal operation | 38% | Default mode |
| D12 (Regime Recognition) | State awareness | - | Regime transitions |

---

## The Semantic Ceiling

### What Each Layer Encodes

| Layer | Encodes | Does NOT Encode |
|-------|---------|-----------------|
| B | What transitions are legal | What to do next |
| A | What cases are comparable | What cases mean |
| HT | Where attention is needed | What to attend to |
| AZC | Where context shifts | What context means |

### Why Grammar Cannot Protect Everything

From the layer analysis:

> "The grammar handles execution decisions (D1-D8). But the grammar deliberately ignores some distinctions (creating D9: comparison decisions). And the grammar cannot encode cognitive load (creating D10: attention decisions) or contextual boundaries (creating D11: orientation decisions)."

This is the **allowed semantic ceiling** - we can identify decision TYPES without knowing decision CONTENT.

---

## Findings

### Established (High Confidence)

1. **12 decision archetypes identified** from hazard topology and layer structure
2. **Each layer handles specific archetype classes:**
   - B: Execution (D1-D8, D12)
   - A: Discrimination (D2, D9)
   - HT: Attention (D10)
   - AZC: Orientation (D11)

3. **Currier A exists because B deliberately collapses distinctions**
   - Grammar cannot track everything
   - Some distinctions are decision-relevant
   - Registry externalizes what grammar ignores

4. **HT exists because grammar cannot encode attention demand**
   - Some situations require vigilance
   - HT anticipates stress (C459)
   - Non-operational but cognitively functional

5. **AZC exists because sections differ in instantiation**
   - Same grammar, different context
   - Orientation markers at cognitive boundaries
   - Positioned at natural HT transition zones (C460)

### Uncertain (Lower Confidence)

- Exact boundaries between some archetypes
- Whether all 12 archetypes are equally important
- Whether additional archetypes exist

---

## Constraints Satisfied

| Constraint | How Satisfied |
|------------|---------------|
| C109 (5 hazard classes) | Mapped to decision archetypes D1-D5 |
| C384 (no A↔B coupling) | A handles what B ignores |
| C404-405 (HT non-operational) | HT handles attention, not execution |
| C459 (HT anticipatory) | HT precedes stress |
| C460 (AZC orientation) | AZC marks transitions |

---

## What This Does NOT Establish

- What specific decisions the operator makes
- Content of any decision
- Procedural instructions
- Recipe or operational details

---

## Navigation

← [ecr_apparatus_roles.md](ecr_apparatus_roles.md) | → [ecr_synthesis.md](ecr_synthesis.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
