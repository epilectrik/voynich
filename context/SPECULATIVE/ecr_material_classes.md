# ECR-1: Material-Class Identification

**Tier:** 3 | **Status:** ACTIVE | **Date:** 2026-01-10

> **Entity-level identification (specific plants, machines, substances) is probably irrecoverable by design and is not the goal of this analysis.**

---

## Objective

Infer the minimal set of **material behavior classes** required to satisfy all frozen constraints, WITHOUT assigning names, labels, or referents.

---

## Evidence Summary

### From Hazard Topology (C109-C114)

| Hazard Class | % | Material Class Implication |
|--------------|---|---------------------------|
| PHASE_ORDERING | 41% | Phase-mobile materials exist |
| COMPOSITION_JUMP | 24% | Composition-distinct materials exist |
| CONTAINMENT_TIMING | 24% | Pressure-sensitive materials exist |
| RATE_MISMATCH | 6% | Flow-sensitive materials exist |
| ENERGY_OVERSHOOT | 6% | Thermal-sensitive materials exist |

**Primary axes:** Phase mobility + Composition distinctness = 65% of hazards

### From Registry Patterns (F-A-007, F-A-009)

| Pattern | Finding | Implication |
|---------|---------|-------------|
| Universal vocab preference | 48% universal vs 8% random | Cross-domain classes dominate |
| Universality bands | Exclusive 3%, Shared 48%, Universal 45% | 3-band classification visible |
| Spatial clustering | Similar bands cluster (p < 0.001) | Comparable classes grouped |

### From Registry Structure (C235, C408)

| Structure | Finding | Implication |
|-----------|---------|-------------|
| 8 prefix families | ch/sh, ok/ot are equivalence pairs | 2 effective classification dimensions |
| Section conditioning | Same structure, different vocabulary | Classes are context-invariant |
| Sister pairs | Mutually exclusive alternatives | Binary choice within dimension |

---

## Inferred Class Count

### Minimum: 3 classes

Based on hazard topology alone:
1. Phase-mobile class (PHASE_ORDERING target)
2. Composition-distinct class (COMPOSITION_JUMP target)
3. Baseline class (neither primary hazard)

### Maximum: 4-6 classes

Based on registry structure:
- 2 dimensions × 2 values = 4 combinatorial classes
- Section conditioning may add contextual variants

### Best Estimate: 4 classes (±1)

The 2-dimensional classification structure (ch/sh × ok/ot) suggests 4 fundamental categories.

---

## Behavioral Profiles

| Class | Phase Behavior | Composition | Hazard Exposure | Registry Pattern |
|-------|---------------|-------------|-----------------|------------------|
| **M-A** | Mobile | Distinct | HIGH (65%) | Universal/Shared |
| **M-B** | Mobile | Homogeneous | MODERATE | Shared |
| **M-C** | Stable | Distinct | MODERATE | Shared/Exclusive |
| **M-D** | Stable | Homogeneous | LOW | Universal |

### Key Behavioral Dimensions

1. **Phase Mobility**
   - Can the material change phase/location under control conditions?
   - Distinguishes materials subject to PHASE_ORDERING hazard

2. **Composition Distinctness**
   - Can the material be fractionated or contaminate other materials?
   - Distinguishes materials subject to COMPOSITION_JUMP hazard

---

## Class-Grammar Relationships

### Grammar-Privileged Classes

- Universal vocabulary entries (45%) describe materials **safe across all contexts**
- Likely the stable, baseline classes (M-D type)
- Grammar does not need to track these carefully

### Grammar-Avoided Classes

- Exclusive vocabulary entries (3%) describe materials **requiring domain-specific handling**
- Likely the most hazard-sensitive classes (M-A type)
- Grammar must track these precisely

### Section Conditioning (C232)

- Same classes appear in different sections
- Section affects vocabulary, NOT class structure
- Material classes are **process-invariant** but **context-instantiated**

---

## Cross-Validation

| Test | Result | Verdict |
|------|--------|---------|
| Regime structure (4 regimes) | Could map to 4 classes OR be orthogonal | CONSISTENT |
| F-A-009 clustering | Similar universality entries cluster | SUPPORTS |
| Prefix pair structure | 2 pairs suggest 2×2 = 4 classes | SUPPORTS |
| Hazard proportion | 65% = phase + composition | SUPPORTS |

---

## Findings

### Established (High Confidence)

1. **At least 3-4 material behavior classes exist**
2. **Classes differ along two primary dimensions:**
   - Phase mobility (mobile vs. stable)
   - Composition behavior (distinct vs. homogeneous)
3. **PHASE_ORDERING (41%) indicates phase-mobile materials are primary concern**
4. **Registry uses 2 classification dimensions** (consistent with 4-class model)
5. **Cross-domain vocabulary preference** indicates comparable profiles across contexts
6. **Section conditioning** affects vocabulary, not class structure

### Uncertain (Lower Confidence)

- Exact class count (3-5 range)
- Whether classes are discrete or continuous
- Precise mapping of prefix pairs to behavioral dimensions
- Whether all 4 combinatorial classes are populated

---

## Constraints Satisfied

| Constraint | How Satisfied |
|------------|---------------|
| C109 (5 hazard classes) | Material classes map to hazard exposure |
| C232 (section-conditioned) | Classes instantiated differently per section |
| C235 (8 markers) | 2 equivalence pairs = 2 dimensions |
| F-A-007 (universal preference) | Cross-domain classes dominate |
| F-A-009 (clustering) | Similar classes grouped spatially |

---

## What This Does NOT Establish

- What specific substances the classes contain
- What the materials are called
- How to identify class membership from tokens
- Token-to-material mappings of any kind

---

## Navigation

← [README.md](README.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
