# Currier A Compositional Morphology

**Phase:** CAS-MORPH
**Tier:** 2 (STRUCTURAL INFERENCE)
**Date:** 2026-01-06

---

## Executive Summary

> **Currier A marker tokens are compositional, not atomic. They decompose into multiple orthogonal sub-components reused across tokens, enabling a large identity space from a small formal codebook.**

This is a structural finding about HOW the registry is generated, NOT about what it represents.

---

## The Compositional Structure

### Observed Decomposition

```
marker_token = PREFIX + [MIDDLE] + SUFFIX
```

| Component | Unique Values | Universality |
|-----------|---------------|--------------|
| PREFIX | 8 | All tokens have exactly one |
| MIDDLE | 396 total, 42 common | 56.1% of tokens have one |
| SUFFIX | 807 total, 7 universal | Most tokens have one |

### Axis Characteristics (Non-Semantic)

| Axis | Structural Role | Evidence |
|------|-----------------|----------|
| **PREFIX** | Primary classifier family (top-level partition) | 8 mutually exclusive classes |
| **MIDDLE** | Modifier subcode (secondary refinement) | Some universal, some prefix-exclusive |
| **SUFFIX** | Terminal variant code (final differentiation) | 7 suffixes appear across 6+ prefixes |

**IMPORTANT:** These are formal roles, NOT semantic meanings. "Primary classifier" does not imply "material type" or any other real-world referent.

---

## Key Metrics

| Metric | Value |
|--------|-------|
| Observed PREFIX × SUFFIX combinations | ~56 (8 × 7 universal) |
| Observed PREFIX × MIDDLE × SUFFIX combinations | **897** |
| Tokens with middle component | 56.1% |
| Universal suffixes (6+ prefixes) | 7 |
| Universal middles (6+ prefixes) | 3 |
| Common middles (3-5 prefixes) | 39 |
| Prefix-exclusive middles | Multiple per prefix |

---

## Universal Suffixes

These 7 suffixes appear across 6 or more prefix classes:

| Suffix | Occurrences | Prefix Coverage |
|--------|-------------|-----------------|
| -ol | 343 | 6 prefixes |
| -or | 204 | 7 prefixes |
| -y | 189 | 7 prefixes |
| -aiin | 113 | 6 prefixes |
| -ar | 44 | 6 prefixes |
| -chy | 42 | 7 prefixes |
| -eeol | 14 | 6 prefixes |

---

## Prefix-Exclusive Middles

Some modifiers are bound to specific classifier families:

| Prefix | Exclusive Middle | Occurrences |
|--------|------------------|-------------|
| CT | -h- | 174 |
| DA | -i- | 98 |
| QO | -kch- | 19 |

This suggests internal structure within classifier families, NOT semantic content.

---

## What This Discovery Shows

### ✅ Structurally Proven (Tier 2)

1. **The registry scales combinatorially** — 897 distinct identities from a small codebook
2. **The system supports many distinctions** — Far more than 8 simple categories
3. **Distinctions are bounded** — Not open-ended; finite formal space
4. **Components show strict reuse** — Same suffixes across prefixes
5. **The system is learnable** — Small codebook, compositional rules

### ❌ NOT Proven (Must Remain External)

- What the prefixes "mean"
- What the middles "mean"
- What the suffixes "mean"
- What real-world domain this classifies
- What materials, products, or specimens are involved

---

## Relationship to Prior Findings

This discovery **strengthens** earlier results:

| Prior Finding | How Strengthened |
|---------------|------------------|
| Low TTR (0.137) | Explained by component reuse |
| 70.7% bigram reuse | Components combine predictably |
| Database-like structure | Compositional key generation |
| No semantics recoverable | Meanings are external to code |
| Infrastructure reuse (daiin, ol) | Part of compositional system |

---

## What This Discovery Does NOT Do

| Claim | Status |
|-------|--------|
| "We found 897 materials" | ❌ FALSE |
| "Prefixes encode material types" | ❌ NOT LICENSED |
| "Suffixes encode forms or states" | ❌ NOT LICENSED |
| "This proves perfumery" | ❌ NOT LICENSED |
| "This is an inventory" | ❌ NOT LICENSED |

The correct statement:

> **We found how one builds 897 unambiguous identities without names.**

---

## Formal Characterization

> **Currier A is a compositional, non-semantic classification registry built from a small number of orthogonal code components, allowing hundreds of fine-grained distinctions while remaining formally stable, enumerable, and isolated from execution.**

---

## Compatibility with Prior Interpretations

The compositional structure is **compatible with** (but does not identify):

- Botanical/aromatic material catalogs
- Specimen classification systems
- Assay preparation registers
- Pharmacognosy inventories
- Metallurgical material tracking
- Archival specimen systems
- Any domain requiring many distinctions without semantic drift

Perfumery/botanical interpretation remains **Tier 3** (plausible, not identified).

---

## New Constraints

| # | Constraint |
|---|------------|
| 267 | Currier A marker tokens are COMPOSITIONAL: decompose into PREFIX + [MIDDLE] + SUFFIX with orthogonal reuse (CAS-MORPH) |
| 268 | 897 observed PREFIX × MIDDLE × SUFFIX combinations; identity space scales combinatorially from small codebook (CAS-MORPH) |
| 269 | 7 UNIVERSAL suffixes appear across 6+ prefixes; 3 UNIVERSAL middles appear across 6+ prefixes (CAS-MORPH) |
| 270 | Some middles are PREFIX-EXCLUSIVE (CT:-h-, DA:-i-, QO:-kch-); internal structure within classifier families (CAS-MORPH) |
| 271 | Compositional structure explains low TTR (0.137) and high bigram reuse (70.7%); components combine predictably (CAS-MORPH) |

---

## Files Generated

- `cas_suffix_analysis.py` — Suffix extraction and analysis
- `cas_morphology_deep.py` — Three-axis decomposition
- `CAS_COMPOSITIONAL_MORPHOLOGY.md` — This report

---

## Phase Tag

```
Phase: CAS-MORPH
Tier: 2 (STRUCTURAL INFERENCE)
Subject: Compositional Morphology of Currier A Marker Tokens
Type: Morphological decomposition analysis
Status: COMPLETE
Verdict: COMPOSITIONAL_IDENTITY_SPACE (897 combinations from small codebook)
```
