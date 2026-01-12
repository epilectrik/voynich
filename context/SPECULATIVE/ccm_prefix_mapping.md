# Component-to-Class Mapping: Prefix Analysis (CCM-1)

**Tier:** 3 | **Status:** IN PROGRESS | **Date:** 2026-01-10

> **Goal:** Map the 8 Currier A prefix families to material classes (M-A/B/C/D) using B-context behavior.

---

## Data Sources

| Source | What It Provides |
|--------|------------------|
| C282 | Prefix enrichment ratios (A vs B) |
| canonical_grammar.json | Token → grammar role mapping |
| hazard_metrics | Escape route patterns |
| C298 | L-compound middles as B-specific operators |
| C299 | Section H dominates B (91.6%) |

---

## Step 1: Prefix → Grammar Role

From canonical_grammar.json (20 terminal tokens):

| Prefix | Tokens Found | Dominant Role |
|--------|--------------|---------------|
| **ch-** | chey, cheey, chedy, cheky, checkhy, chol | ENERGY_OPERATOR (5), FLOW_OPERATOR (1) |
| **qo-** | qokaiin, qokal | ENERGY_OPERATOR (2) |
| **ok-** | okaiin, okal | FREQUENT_OPERATOR (2) |
| **da-** | daiin, dar | CORE_CONTROL (1), AUXILIARY (1) |
| **ol** | ol | CORE_CONTROL (1) |
| **ot-** | otain | AUXILIARY (1) |
| **sh-** | (none in terminals) | Inferred: Sister to ch- |
| **ct-** | (none in terminals) | Inferred: Registry-specialized |

**Key finding:** ch- and qo- dominate ENERGY_OPERATOR role. ok- is FREQUENT_OPERATOR. da-/ol is CORE_CONTROL.

---

## Step 2: Prefix Enrichment Patterns

From C282:

| Prefix | B-Enrichment | Interpretation |
|--------|--------------|----------------|
| **ct** | 0.14x (= 7x A-enriched) | Registry-specialized, rare in B |
| **ol** | 5x B-enriched | Operationally critical |
| **qo** | 4x B-enriched | Operationally active |
| **da** | ~1x (balanced) | Structural articulation |
| **ch/sh** | ~1x (balanced) | Cross-system utility |
| **ok/ot** | ~1x (balanced) | Cross-system utility |

**Pattern:** High B-enrichment = operational role. High A-enrichment = registry/classification role.

---

## Step 3: Hazard Context Behavior

From hazard_metrics:

| Metric | Value | Implication |
|--------|-------|-------------|
| qo-prefix escape rate | 25-47% | qo- tokens help escape hazards |
| ENERGY_OPERATOR as escape | 40-67% | ch-, qo- are recovery mechanisms |
| CORE_CONTROL as escape | 22-32% | da-/ol stabilize after hazards |

**Pattern:** ENERGY-family prefixes (ch-, qo-) dominate hazard recovery.

---

## Step 4: Cross-Reference with ECR Material Classes

Recall from ECR-1:

| Class | Phase | Composition | Hazard Exposure | Primary Hazards |
|-------|-------|-------------|-----------------|-----------------|
| M-A | Mobile | Distinct | HIGH (65%) | PHASE_ORDERING, COMPOSITION_JUMP |
| M-B | Mobile | Homogeneous | MODERATE | PHASE_ORDERING |
| M-C | Stable | Distinct | MODERATE | COMPOSITION_JUMP |
| M-D | Stable | Homogeneous | LOW | Baseline |

---

## CCM-1 Synthesis: Prefix → Material Class Mapping

### Proposed Mapping

| Prefix | B-Role | Hazard Behavior | Material Class | Confidence |
|--------|--------|-----------------|----------------|------------|
| **ch-** | ENERGY_OPERATOR | Escape (40-67%) | **Operates ON M-A** | HIGH |
| **sh-** | (Sister to ch-) | Section-conditioned | **Operates ON M-A** (variant) | MEDIUM |
| **qo-** | ENERGY_OPERATOR | Escape (25-47%) | **Operates ON M-A** | HIGH |
| **ok-** | FREQUENT_OPERATOR | Active operations | **M-B associated** | MEDIUM |
| **ot-** | AUXILIARY | Support role | **M-B associated** (variant) | LOW |
| **da-** | CORE_CONTROL | Structural | **Cross-class anchor** | HIGH |
| **ol** | CORE_CONTROL | Stabilization | **Cross-class anchor** | HIGH |
| **ct-** | Registry-specialized | 0% of B terminals | **M-C/M-D reference** | HIGH |

### Interpretation

**Energy prefixes (ch-, qo-):** Do not ENCODE M-A materials — they encode OPERATIONS on M-A materials. They are the energy-control vocabulary for handling mobile, distinct substances where phase ordering and composition hazards dominate.

**Frequent prefixes (ok-):** Encode operations on M-B materials (mobile but homogeneous). Simpler hazard profile, hence "frequent" operations.

**Control prefixes (da-, ol):** Cross-class structural anchors. They articulate records (A) and control execution flow (B) regardless of material class.

**Registry-only prefix (ct-):** Encodes M-C/M-D materials (stable). These rarely appear in B because stable materials don't require active operational control — they're referenced in the registry for discrimination but not manipulated in real-time.

---

## Critical Distinction

**Prefixes do NOT encode material identity.**

They encode **operational mode relative to material behavior class:**

| Prefix Type | Encodes |
|-------------|---------|
| ch-, qo- | Energy operations (for mobile-distinct materials) |
| ok-, ot- | Frequent operations (for mobile-homogeneous) |
| da-, ol | Control structure (class-independent) |
| ct- | Registry reference (for stable materials) |

This is consistent with the semantic ceiling: we know **what kind of operations** each prefix family supports, but not **which specific substances** they operate on.

---

## Constraints Satisfied

| Constraint | How Satisfied |
|------------|---------------|
| C282 | Enrichment patterns explain operational vs registry roles |
| C397-398 | qo-/ch- escape behavior maps to energy-control function |
| C299 | Section H dominance (91.6% in B) aligns with ch-/qo- as operational |
| C298 | L-compound middles (lch-, lk-) are B-specific → prefix + middle = operational mode |

---

## Remaining Uncertainty

| Question | Status |
|----------|--------|
| Exact ok-/ot- material class association | LOW confidence |
| Whether sh- is strictly M-A or section-variant | Needs testing |
| Whether ct- maps to M-C, M-D, or both | Needs testing |

---

## Next Steps

- CCM-2: Test suffix → decision archetype mapping
- CCM-3: Test sister-pair choice predictors (ch vs sh, ok vs ot)
- CCM-4: Classify MIDDLEs by prefix class

---

## Navigation

← [ecr_synthesis.md](ecr_synthesis.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
