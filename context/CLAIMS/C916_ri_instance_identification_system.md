# C916: RI Instance Identification System

**Tier:** 2 (Structural evidence) / 3 (Interpretive implications)
**Scope:** A
**Status:** REFINED (see C917-C918)
**Phase:** RI_EXTENSION_MAPPING

---

> **Note:** This constraint's "index bridging" interpretation has been REFINED by C917-C918. The structural findings (RI=PP+extension, 90.9% containment, label enrichment) remain valid. However, C917-C918 discovered that extensions encode **operational context** (h=monitoring/linker, k=energy, t=terminal), not arbitrary instance identifiers. A is better described as an **operational configuration layer** that specifies material variants for specific operational contexts, not a simple index.

---

## Statement

RI (Registry-Internal) vocabulary functions as an **instance identification system** built via derivational morphology from PP (Procedural Payload) vocabulary. PP encodes general categories shared with B execution; RI extends PP with single-character markers to identify specific instances. This explains A's purpose as an index that bridges general procedures (B) to specific applications (labels, illustrated items).

---

## The Three-Level Model

| Level | Vocabulary | Function | Example |
|-------|-----------|----------|---------|
| **B (Execution)** | PP only | General operations | "Process 'od' at temperature 'kch'" |
| **A (Registry)** | PP + RI | Specific instances | "Entry for 'odo': follow procedure X" |
| **Labels** | RI-enriched (3.7x) | Illustration pointers | "This drawing = 'odo'" |

---

## Evidence

### Structural Evidence (Tier 2)

| Metric | Value | Source |
|--------|-------|--------|
| RI containment in PP | 90.9% | C913 |
| Single-char extensions | 71.6% | C913 |
| Label RI enrichment | 3.7x (27.3% vs 7.4%) | C914 |
| Dual-use PP roots | 225 | RI_EXTENSION_MAPPING |
| PP in both A and B | 408 MIDDLEs | RI_EXTENSION_MAPPING |

### Dual-Use Pattern

225 PP MIDDLEs appear both:
1. **Directly** in A text (general category reference)
2. **As RI bases** via extension (specific instance reference)

Top examples:
- 'od': 191 direct uses, 23 as RI base
- 'eo': 211 direct uses, 14 as RI base
- 'ol': 790 direct uses, 4 as RI base

This demonstrates the **category vs. instance** distinction at the vocabulary level.

---

## Functional Model

```
PP MIDDLE 'od' (category: herb/material class)
     |
     +-- 'odo' (instance 1) - used in f1r label
     +-- 'oda' (instance 2) - used in f3v text
     +-- 'odd' (instance 3) - used in f8r text
```

### The A-B Relationship

```
Currier B = PROCEDURE LIBRARY
  - General instructions for operations
  - Uses PP vocabulary (categories only)
  - "How to process herbs" (general)
       |
       v
Currier A = REGISTRY/INDEX
  - Specific instances of procedures
  - Uses PP + RI vocabulary
  - "Entry for THIS herb: follow procedure X"
       |
       v
Labels = POINTERS
  - Link illustrations to registry entries
  - RI-enriched (3.7x) for instance-specificity
  - "This illustration is the 'odo' referenced in entries"
```

---

## Interpretive Implications (Tier 3)

1. **A exists because B is general**: B provides procedures; A indexes specific applications
2. **Labels need RI**: Pointing to "this specific plant" requires instance markers
3. **RI is productive**: The derivational system can create new instance IDs as needed
4. **A bridges general and specific**: Same conceptual vocabulary at different granularity levels

---

## What This Resolves

| Question | Answer |
|----------|--------|
| Why does A exist if B is self-sufficient? | A indexes specific applications of general B procedures |
| Why are labels RI-enriched? | Labels point to specific illustrated items |
| What is RI vocabulary? | Instance identifiers derived from PP categories |
| How do A and B relate? | Same conceptual vocabulary, different granularity |

---

## Related Constraints

| Constraint | Relationship |
|------------|--------------|
| C240 | A = Registry - this explains the indexing mechanism |
| C913 | RI Derivational Morphology - the structural basis |
| C914 | RI Label Enrichment - why labels need RI |
| C915 | Section P Pure-RI Entries - specialized reference entries |
| C498 | RI definition - now explained functionally |
| C526 | RI lexical layer - instance anchoring explained |

---

## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
