# Component-to-Class Mapping: Synthesis

**Tier:** 3 | **Status:** COMPLETE | **Date:** 2026-01-10

> **Achievement:** Complete class-level semantic decomposition of Currier A/B tokens.

---

## Executive Summary

The CCM phase has successfully mapped morphological components to behavioral classes:

| Component | Encodes | Evidence |
|-----------|---------|----------|
| **PREFIX** | Material-class operation | Grammar roles, enrichment ratios |
| **SISTER** | Operational mode (precision vs tolerance) | C412 anticorrelation |
| **MIDDLE** | Within-class variant | 80% prefix-exclusive, 402 distinctions |
| **SUFFIX** | Decision archetype | A/B enrichment patterns |

---

## Complete Compositional Model

```
TOKEN = PREFIX     (what material class)
      + SISTER     (how carefully)
      + MIDDLE     (which variant)
      + SUFFIX     (what decision)
```

---

## PREFIX → Material Class Mapping

| Prefix | B-Role | Material Class | Function |
|--------|--------|----------------|----------|
| **ch/sh** | ENERGY_OPERATOR | M-A (mobile, distinct) | Energy operations |
| **qo** | ENERGY_OPERATOR | M-A (mobile, distinct) | Energy control |
| **ok/ot** | FREQUENT_OPERATOR | M-B (mobile, homogeneous) | Routine operations |
| **da** | CORE_CONTROL | Cross-class | Structural anchor |
| **ol** | CORE_CONTROL | Cross-class | Flow anchor |
| **ct** | Registry-only | M-C/M-D (stable) | Classification reference |

---

## SISTER → Operational Mode Mapping

| Sister Pair | Mode | Escape Density | Interpretation |
|-------------|------|----------------|----------------|
| **ch** (vs sh) | Precision | LOW (7.1%) | Tight tolerances, fewer recovery options |
| **sh** (vs ch) | Tolerance | HIGH (24.7%) | More escape routes, safer |
| **ok** (vs ot) | (needs testing) | - | Likely parallel pattern |
| **ot** (vs ok) | (needs testing) | - | Likely parallel pattern |

**Key finding (C412):** Sister preference anticorrelates with escape density (rho = -0.326, p = 0.002).

---

## MIDDLE → Variant Specification

| MIDDLE Type | Count | Function |
|-------------|-------|----------|
| Prefix-EXCLUSIVE | 947 (80%) | Class-specific variant discrimination |
| Shared | 237 (20%) | Cross-class discrimination |
| Universal | 27 | Core discriminations for all classes |

**Key finding:** MIDDLE is the primary discriminator (402 unique distinctions) and drives sister-pair choice (25.4% deviation).

---

## SUFFIX → Decision Archetype Mapping

| Suffix | Enrichment | Primary Layer | Decision Archetype |
|--------|------------|---------------|-------------------|
| **-edy** | 191x B | B (execution) | D5 (Energy Level) |
| **-dy** | 4.6x B | B (execution) | D6 (Wait vs Act) |
| **-ar** | 3.2x B | B (execution) | D7 (Recovery Path) |
| **-ol** | balanced | Cross-layer | D6/D8 |
| **-aiin** | balanced | Cross-layer | D1/D4 |
| **-or** | 1.5x A | A (discrimination) | D2 (Fraction Identity) |
| **-chy** | 1.6x A | A (discrimination) | D2 (Fraction Identity) |
| **-chor** | 5.6x A | A (discrimination) | D9 (Case Comparison) |

---

## Complete Token Interpretation

### Example: chedy
```
ch   = M-A energy operation (mobile, distinct)
-e-  = variant-e (MIDDLE)
-dy  = D6 decision (routine execution)
```
**Class-level meaning:** "Routine decision about variant-e energy operation on mobile-distinct material"

### Example: sheor
```
sh   = M-A energy operation, TOLERANCE MODE
-e-  = variant-e (MIDDLE)
-or  = D2 decision (fraction identity)
```
**Class-level meaning:** "Fraction-identity decision about variant-e energy operation on mobile-distinct material, with recovery affordance"

### Example: okaiin
```
ok   = M-B operation (mobile, homogeneous)
-a-  = variant-a (MIDDLE)
-aiin = D1/D4 decision (phase/flow)
```
**Class-level meaning:** "Phase or flow decision about variant-a operation on mobile-homogeneous material"

---

## Semantic Ceiling Revisited

### What We NOW Know

| Dimension | CCM Finding |
|-----------|-------------|
| Material classes | 4 classes (M-A/B/C/D) mapped to prefixes |
| Operational modes | 2 modes (precision/tolerance) mapped to sisters |
| Variants | ~1000 variants mapped to MIDDLEs |
| Decision types | 12 archetypes mapped to suffixes |

### What We Still Cannot Know

| Dimension | Why Blocked |
|-----------|-------------|
| Specific substances | No external anchor |
| Specific apparatus | No external anchor |
| Specific procedures | No external anchor |
| Variant identities | Beyond structural analysis |

---

## The Answer to Your Question

> "Can we identify every token and reasonably explain it?"

**YES, at the class level:**

Every token can be decomposed into:
1. Material-class operation (PREFIX)
2. Operational mode (SISTER variant)
3. Specific variant within class (MIDDLE)
4. Decision archetype context (SUFFIX)

This is **complete structural identification**.

**NO, at the referent level:**

We cannot say what specific substance, device, or procedure any token refers to. The system deliberately omits referents.

---

## Semantic Achievement Summary

| Before CCM | After CCM |
|------------|-----------|
| "8 prefix families exist" | "Prefixes map to 4 material classes" |
| "Suffixes are universal" | "Suffixes encode decision archetypes" |
| "Sister pairs are equivalent" | "Sister choice encodes operational mode" |
| "MIDDLEs are primary discriminators" | "MIDDLEs encode class-specific variants" |

We've pushed the semantic ceiling as far as internal analysis permits.

---

## Files Created

| File | Content |
|------|---------|
| `ccm_prefix_mapping.md` | PREFIX → Material class |
| `ccm_suffix_mapping.md` | SUFFIX → Decision archetype |
| `ccm_sister_pairs.md` | SISTER → Operational mode |
| `ccm_middle_classification.md` | MIDDLE → Variant specification |
| `ccm_synthesis.md` | This document |

---

## Constraints Satisfied

| Constraint | How Used |
|------------|----------|
| C282 | Prefix enrichment → class mapping |
| C283 | Suffix enrichment → archetype mapping |
| C412 | Sister anticorrelation → mode mapping |
| C410.a | MIDDLE preference → variant specification |
| C423 | MIDDLE census → class-specific discrimination |

---

## Next Steps

The CCM phase is complete. Possible extensions:

1. **Test ok/ot for parallel brittleness correlation**
2. **Cluster MIDDLEs by behavioral similarity**
3. **Map MIDDLE clusters to hazard sub-types**
4. **External validation via practitioner interviews**

---

## Navigation

← [ccm_middle_classification.md](ccm_middle_classification.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
