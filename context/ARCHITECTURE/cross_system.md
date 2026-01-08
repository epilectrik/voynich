# Cross-System Architecture

**Status:** CLOSED | **Tier:** 2 | **Scope:** All three text systems

---

## The Three Systems

The Voynich Manuscript contains three distinct text systems:

| System | % Tokens | Folios | Function |
|--------|----------|--------|----------|
| **Currier B** | 61.9% | 83 | Sequential executable programs |
| **Currier A** | 30.5% | 114 | Non-sequential categorical registry |
| **AZC** | 7.7% | 30 | Hybrid diagram annotation |

---

## Relationships

### Folio Disjunction (Tier 0)

A and B are **completely folio-disjoint**:

| Fact | Value | Constraint |
|------|-------|------------|
| Shared folios | 0 | C272 |
| A folios | 114 | |
| B folios | 83 | |
| Cross-transitions | 25/112,733 (0.0%) | C239 |

This is **designed separation**, not gradual drift. The manuscript was organized to keep A and B physically apart.

### Grammar Disjunction (Tier 2)

A and B have **completely different formal systems**:

| Aspect | Currier A | Currier B |
|--------|-----------|-----------|
| Sequential grammar | NO | YES (49 classes) |
| Line structure | Atomic (3 tokens median) | Blocked (31 tokens median) |
| Position dependence | NONE (JS=0) | HIGH (positional grammar) |
| Forbidden transitions | 5 violations | 0 violations |
| Grammar coverage | 13.6% (49-class grammar fails) | 100% |

### Vocabulary Integration (Tier 2)

Despite grammar disjunction, A and B **share vocabulary**:

| Metric | Value | Constraint |
|--------|-------|------------|
| B tokens appearing in A vocabulary | 69.8% | C335 |
| Shared token types | 1,532 | |
| All B folios access same A pool | J=0.998 | C384 |

This is **global type system sharing**, not entry-level cross-reference.

---

## Global Type System (Tier 2)

The same morphological type system spans all three systems (C383):

### Type Dichotomy

| Type | Prefixes | Kernel Contact | LINK Affinity |
|------|----------|----------------|---------------|
| INTERVENTION | ch, sh, ok | 100% | Avoiding |
| MONITORING | da, sa | <5% | Attracted |

This dichotomy holds **identically** in:
- Currier B (sequential programs)
- Currier A (non-sequential registry)
- AZC (hybrid annotation)

### Implications

- **Same alphabet, different grammar**: A and B use same tokens differently
- **Type = function, not meaning**: Morphological type encodes operational role
- **No semantic transfer**: Vocabulary sharing doesn't imply meaning sharing

---

## A↔B Integration Pattern (Tier 2)

### What IS Shared

| Shared Element | Evidence |
|----------------|----------|
| Token vocabulary | 69.8% overlap |
| Morphological components | Same prefixes, suffixes, middles |
| Type dichotomy | ch/sh/ok vs da/sa in both |
| LINK affinity patterns | da/al attracted, qo/ok avoiding |

### What is NOT Shared

| Not Shared | Evidence |
|------------|----------|
| Entry-level coupling | J=0.998 across all B folios (no targeting) |
| Folio-level cross-reference | 0 shared folios |
| Sequential grammar | A has none |
| Forbidden transitions | Different violations |

### Hybrid Access Pattern (C336)

B programs access A vocabulary through **both**:
- **Sequential reading**: Adjacent B folios share more A-vocab (0.548 vs 0.404)
- **Semantic lookup**: Similar B programs share more A-vocab (0.427 vs 0.256)

Operators use **both** sequential reading and semantic lookup.

---

## AZC Bridge Role

AZC mediates between A and B:

| Connection | Value |
|------------|-------|
| A vocabulary coverage | 65.4% |
| B vocabulary coverage | 69.7% |
| Shared vocabulary (A∩B) | 60.5% |
| Unique vocabulary | 25.4% |

AZC draws primarily from the **shared core** while adding diagram-specific terms.

---

## Analogy

| System | Analogy | Function |
|--------|---------|----------|
| Currier A | Parts catalog | Index of available components |
| Currier B | Assembly instructions | How to use components |
| AZC | Diagram labels | Position markers on illustrations |

Same part types, different formal systems.

---

## No Entry-Level Coupling (Tier 2)

Despite vocabulary sharing, there is **no entry-level cross-reference** (C384):

| Finding | Evidence |
|---------|----------|
| All B folios use identical A pool | J=0.998 |
| 215 one-to-one tokens scatter | 207 unique pairings (no repeated) |
| Rare tokens are globally rare | Not relationally rare |

**A does NOT function as lookup catalog for B programs.** Coupling occurs only at the global type-system level.

---

## Section Mapping (Tier 2)

A sections map non-uniformly to B procedures (C299):

| A Section | % of B folios using | Interpretation |
|-----------|---------------------|----------------|
| H | 91.6% (76/83) | Broadly applicable |
| P | 8.4% (7/83) | Specialized use |
| T | 0% (0/83) | Not used in procedures |

H-section vocabulary dominates B procedures.

---

## Key Constraints

| # | Constraint |
|---|------------|
| 272 | A and B are folio-disjoint (0 shared) |
| 335 | 69.8% vocabulary integration |
| 336 | Hybrid access (sequential + semantic) |
| 383 | GLOBAL TYPE SYSTEM across A/B/AZC |
| 384 | NO entry-level coupling |

---

## Navigation

← [currier_AZC.md](currier_AZC.md) | [human_track.md](human_track.md) →
