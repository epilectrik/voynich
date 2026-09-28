# Cross-System Architecture

**Status:** CLOSED | **Tier:** 2 | **Scope:** All three text systems

> **Status note (v7.25, 2026-09-28).** Written before the September 2026 review; `SYSTEM/STATUS_BRIEF.md` and the
> generated `CONSTRAINT_TABLE.txt` win on conflict. "Executable programs" / "execution" for Currier B is the Tier-3
> working interpretation; the Tier-0 claim is the measured grammar (STATUS_BRIEF §1). References below to the kernel,
> LINK monitoring and hazard topology are annotated as withdrawn (STATUS_BRIEF §3).

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

### Folio Disjunction (Tier 2 — C272 and C239 are Tier 2 in the registry)

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
| Grammar coverage | 13.6% (49-class grammar fails) | 100% of its own vocabulary = 69.5% of B tokens (C124 as corrected) |

*[The forbidden-transition row is historical: the hazard/forbidden-transition layer is withdrawn — zero bigrams reduce to composition, zones and boundary coupling (C2081; C783 demoted).]*

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

The same morphological type system spans all three systems (C383): [v7.26 status: C383 demoted to Tier 3 (kernel contact is a spelling identity; monitoring reading withdrawn)]

### Type Dichotomy

| Type | Prefixes | Kernel Contact | LINK Affinity |
|------|----------|----------------|---------------|
| INTERVENTION | ch, sh, ok | 100% | Avoiding |
| MONITORING | da, sa | <5% | Attracted |

*[Status: C383 remains Tier 2 as registered. The INTERVENTION/MONITORING labels rest on withdrawn readings — LINK as monitoring (C609, C1174: LINK is a morphological artifact of "ol") and the k/h/e kernel (C089 superseded by C2082). "Kernel contact" counts EVA letters, and h is half the bench glyph (C1440). Treat the labels as historical.]*

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
| LINK affinity patterns | da/al attracted, qo/ok avoiding (LINK = tokens containing "ol", a morphological artifact, C1174) |

### What is NOT Shared

| Not Shared | Evidence |
|------------|----------|
| Entry-level coupling | J=0.998 across all B folios (no targeting) |
| Folio-level cross-reference | 0 shared folios |
| Sequential grammar | A has none |
| Forbidden transitions | Different violations (historical — the forbidden-transition layer is withdrawn, C2081) |

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

Currier A and Currier B share a global morphological type system (C383 [demoted to Tier 3, v7.26]). This produces structural coherence between registry entries and execution grammar without implying semantic reference or entry-level correspondence. [v7.26 status: C383 demoted to Tier 3 (kernel contact is a spelling identity; monitoring reading withdrawn)]

**The systems feel aligned because they use the same types - not because they reference each other.**

This distinction resolves a common confusion: observing that A's material/variant encoding aligns with B's hazard topology does not indicate semantic coupling [the hazard topology itself is now withdrawn — STATUS_BRIEF §3; C2081]. It indicates that both systems instantiate the same type system - one as registry, one as executable grammar. The alignment is structural, not referential.

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
