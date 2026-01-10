# Cross-System Synthesis: A/B/AZC Structural Architecture

**Date:** 2026-01-09
**Status:** COMPLETE
**Tier:** 2

---

## Executive Summary

Analysis of Currier A record structure (DA articulation, block repetition, positional tendencies) revealed insights about cross-system architecture. The key finding: **the type system is UNIFIED but structural realization is SYSTEM-SPECIFIC**.

---

## What Transfers Across Systems

### Global Type System (C383)

The PREFIX/MIDDLE/SUFFIX morphology and type dichotomy work **identically** in A, B, and AZC:

| Type Class | Definition | A | B | AZC |
|------------|------------|---|---|-----|
| INTERVENTION | ch, sh, ok | 100% kernel contact | 100% kernel contact | 100% kernel contact |
| MONITORING | da, sa | <5% kernel contact | <5% kernel contact | <5% kernel contact |
| Morphology | Prefix+Middle+Suffix | Yes | Yes | Yes |

**This is the ONLY structural element that transfers perfectly across all three systems.**

### Vocabulary Integration (C384)

- All B folios access identical A vocabulary pool (J=0.998)
- 69.8% of B tokens appear in A vocabulary (C335)
- This is GLOBAL type-system sharing, not entry-level lookup
- A is NOT a catalog for B; they share a training corpus

---

## What Does NOT Transfer

### Structural Mechanisms

| Dimension | Currier A | Currier B | AZC |
|-----------|-----------|-----------|-----|
| Segmentation | DA internal punctuation | Line boundaries | Placement codes |
| Line length | 3 tokens (atomic) | 31 tokens (blocks) | 8 tokens (labels) |
| Repetition | 64.1% block-level | Convergence (57.8% STATE-C) | Placement-constrained |
| Position | FREE (except initial) | DEPENDENT (phase-encoded) | CODED (99 forbidden pairs) |
| Grammar | None (silhouette=0.049) | 49-class sequential | Hybrid |

### Closure Mechanisms

Both A and B have closure strategies, but they differ:

| System | Mechanism | Evidence |
|--------|-----------|----------|
| Currier A | **Enumeration closure** | 64.1% entries repeat blocks (C250) |
| Currier B | **Execution closure** | 57.8% folios terminate in STATE-C |

These are **functionally equivalent** at the conceptual level (both represent "completion") but structurally distinct.

---

## daiin Cross-System Analysis (NEW)

### Hypothesis

daiin (and DA family) serves as a **universal articulator** that adapts its structural role by system context.

### Findings

#### Position Distribution (Line-Level)

| System | DA Rate | Initial Enrichment | Internal Enrichment | Final Enrichment |
|--------|---------|-------------------|---------------------|------------------|
| A | 9.72% | 0.64x | 0.90x | **1.72x** |
| B | 4.74% | **1.63x** | 0.82x | **1.60x** |
| AZC | 6.32% | 0.64x | 1.01x | 0.96x |

**Patterns:**
- **Currier A:** DA enriched at FINAL positions (1.72x) - marks segment boundaries
- **Currier B:** DA enriched at INITIAL (1.63x) and FINAL (1.60x) - marks line boundaries
- **AZC:** DA shows NO positional enrichment (~1.0x) - neutral at line level

#### AZC Placement Correlation

| Placement | DA Rate | Enrichment | Interpretation |
|-----------|---------|------------|----------------|
| B (central) | 27.27% | **4.32x** | DA marks central diagram position |
| R (radial) | 12.60% | **1.99x** | DA marks radial positions |
| O | 11.33% | **1.79x** | DA marks "other" positions |
| S1, S2 | 1-3% | 0.07-0.46x | DA AVOIDS edge positions |

**Key finding:** In AZC, DA is **PLACEMENT-coded**, not **POSITION-coded**.

#### Form Distribution

| Form | Currier A | Currier B | AZC |
|------|-----------|-----------|-----|
| daiin* | **49.3%** | 32.4% | 19.9% |
| dar* | 11.9% | 23.2% | 23.6% |
| dal* | 11.8% | 22.0% | **28.3%** |
| da*other | 11.6% | 10.0% | 20.5% |

- A is **daiin-dominant** (49.3%)
- B is more diverse (daiin shares space with dar, dal)
- AZC is **most diverse**, daiin is minority (19.9%)

### Conclusion: Refined Universal Articulator

DA adapts its structural role by system context:

| System | DA Role | Mechanism |
|--------|---------|-----------|
| Currier A | **Entry articulator** | Marks segment boundaries (final-enriched) |
| Currier B | **Line articulator** | Marks line boundaries (initial/final-enriched) |
| AZC | **Diagram articulator** | Marks central positions (placement-coded) |

> **daiin is a universal articulator that expresses structure differently in each text mode: sequential boundaries in A/B, spatial positions in AZC.**

---

## Positional Tendencies

### Currier A (Block-Level)

From second-wave record geometry analysis:

| Prefix | INITIAL | INTERNAL | FINAL | Pattern |
|--------|---------|----------|-------|---------|
| qo | **+2.5%** | baseline | - | Enriched at block start |
| ch | **-6.5%** | baseline | - | Depleted at block start |
| sh | - | baseline | **-3.2%** | Depleted at block end |
| ct | - | - | **+1.0%** | Enriched at block end |

These are **tendencies** (2-7% effect), not rules. All prefixes appear at all positions.

### Currier B (Phase-Encoded)

B expresses positional preferences through **morphological phase encoding** (C382):
- KERNEL-HEAVY prefixes (ch, sh, ok): 100% kernel contact, LINK-avoiding
- KERNEL-LIGHT prefixes (da, sa): <5% kernel contact, LINK-attracted

**Same signal, different expression:** Both A and B show prefix-position associations, but A uses block structure while B uses kernel topology.

---

## Three-System Model

```
           CURRIER A                CURRIER B                    AZC
           ─────────                ─────────                    ───
           Registry                 Programs                     Diagrams

Structure: Entry → DA → Entry      Line → Line → Line          Placement → Placement
           [blocks repeat]          [converges to STATE-C]       [spatially coded]

Position:  FREE (block-relative)   DEPENDENT (phase-encoded)   CODED (placement-locked)

Grammar:   None                     49-class sequential          Hybrid (99 forbidden pairs)

DA Role:   Entry/segment boundary   Line boundary               Central diagram position

Type:      UNIFIED (C383)          UNIFIED (C383)              UNIFIED (C383)
```

---

## Key Constraints Referenced

| # | Constraint | System |
|---|------------|--------|
| C250 | 64.1% block repetition | A |
| C250.a | Block-aligned repetition | A |
| C383 | Global type system | All |
| C384 | No entry-level coupling | A↔B |
| C422 | DA articulation | A |
| C357-360 | Line structure | B |
| C313-320 | Placement coding | AZC |

---

## Structural Summary

| Question | Answer |
|----------|--------|
| Does A structure transfer to B? | **No** - only type system transfers |
| Is daiin a universal articulator? | **Yes** - but adapts to context (boundary vs spatial) |
| Are A repetition and B convergence equivalent? | **Conceptually** (both = closure), **not structurally** |
| Does AZC follow A or B? | **Neither** - unique placement-coded hybrid |

---

## Navigation

← [currier_A.md](currier_A.md) | [currier_B.md](currier_B.md) | [currier_AZC.md](currier_AZC.md) →
