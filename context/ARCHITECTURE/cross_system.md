# Cross-System Architecture

**Status:** CLOSED | **Tier:** 2 | **Scope:** All three text systems

---

## The Three Systems

The Voynich Manuscript contains three distinct text systems:

| System | % Tokens | Folios | Function |
|--------|----------|--------|----------|
| **Currier B** | 61.9% | 83 | Sequential executable programs |
| **Currier A** | 30.5% | 114 | Non-sequential categorical registry |
| **AZC** | 8.7% | 30 | Static positional vocabulary classification |

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

### Vocabulary Overlap Pattern (C336)

B and A vocabulary overlap shows both sequential and semantic correlation:
- **Sequential correlation**: Adjacent B folios share more A-vocabulary (0.548 vs 0.404)
- **Semantic correlation**: Similar B programs share more A-vocabulary (0.427 vs 0.256)

The functional mechanism producing these correlations is not established at Tier 2.

---

## AZC Vocabulary Classification

AZC classifies vocabulary from the shared type system by positional properties:

| Connection | Value |
|------------|-------|
| A vocabulary coverage | 65.4% |
| B vocabulary coverage | 69.7% |
| Shared vocabulary (A∩B) | 60.5% |
| Unique vocabulary | 25.4% |

AZC vocabulary is primarily from the shared A/B vocabulary pool, with additional diagram-specific terms.

---

## Analogy

| System | Analogy | Function |
|--------|---------|----------|
| Currier A | Discrimination index | Fine distinctions within shared vocabulary |
| Currier B | Execution grammar | Sequential programs using shared vocabulary |
| AZC | Positional classification | Vocabulary organized by operational character |

Same vocabulary, different formal systems.

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

## Type Coherence vs Semantic Reference

Currier A and Currier B share a global morphological type system (C383). This produces structural coherence between registry entries and execution grammar without implying semantic reference or entry-level correspondence.

**The systems feel aligned because they use the same types - not because they reference each other.**

This distinction resolves a common confusion: observing that A's material/variant encoding aligns with B's hazard topology does not indicate semantic coupling. It indicates that both systems instantiate the same type system - one as registry, one as executable grammar. The alignment is structural, not referential.

### Construction-Time vs Runtime (Tier 3)

The vocabulary overlap is clearly deliberate but no runtime coupling mechanism exists (A_PURPOSE_INVESTIGATION, 2026-02-04: 6 hypotheses tested, all failed). The most parsimonious explanation is a **construction-time relationship**: A served as the reference vocabulary when B programs were authored. AZC classified that vocabulary by operational character. Once written, B programs are fixed and self-contained — no active compilation from A data occurs during execution. A may also have served as a lookup reference for operators encountering unfamiliar tokens.

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
| 336 | Vocabulary overlap (sequential + semantic correlation) |
| 383 | GLOBAL TYPE SYSTEM across A/B/AZC |
| 384 | NO entry-level coupling |

---

## Navigation

← [currier_AZC.md](currier_AZC.md) | [human_track.md](human_track.md) →
