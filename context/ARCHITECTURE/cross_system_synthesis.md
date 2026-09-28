# Cross-System Synthesis: A/B/AZC Structural Architecture

**Date:** 2026-01-09
**Status:** COMPLETE
**Tier:** 2

> **Status note (v7.25, 2026-09-28).** Written before the September 2026 review; `SYSTEM/STATUS_BRIEF.md` and the
> generated `CONSTRAINT_TABLE.txt` win on conflict. Kernel contact, LINK affinity, convergence to STATE-C and
> "phase-encoded" position rest on constructs now withdrawn (STATUS_BRIEF §3) and are annotated where they occur.

---

## Executive Summary

Analysis of Currier A record structure (DA articulation, block repetition, positional tendencies) revealed insights about cross-system architecture. The key finding: **the type system is UNIFIED but structural realization is SYSTEM-SPECIFIC**.

---

## What Transfers Across Systems

### Global Type System (C383) [v7.26 status: C383 demoted to Tier 3 (kernel contact is a spelling identity; monitoring reading withdrawn)]

The PREFIX/MIDDLE/SUFFIX morphology and type dichotomy work **identically** in A, B, and AZC:

| Type Class | Definition | A | B | AZC |
|------------|------------|---|---|-----|
| INTERVENTION | ch, sh, ok | 100% kernel contact | 100% kernel contact | 100% kernel contact |
| MONITORING | da, sa | <5% kernel contact | <5% kernel contact | <5% kernel contact |
| Morphology | Prefix+Middle+Suffix | Yes | Yes | Yes |

*[C383 remains Tier 2 as registered. "Kernel contact" counts EVA letters k/h/e (kernel reading superseded, C089 → C2082; h is half the bench glyph, C1440), and the INTERVENTION/MONITORING labels rest on the withdrawn LINK-monitoring reading (C609, C1174). Treat the labels as historical.]*

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
| Repetition | Compositional (897 combos) | Convergence (57.8% STATE-C) | Placement-constrained |
| Position | FREE (except initial) | DEPENDENT (phase-encoded) | CODED (99 forbidden pairs) |
| Grammar | None (silhouette=0.049) | 49-class sequential | Hybrid |

*[Status notes: B "convergence" is withdrawn — C074 is kept as occupancy only (57.8% of folios end in their dominant macro-state; no sequential convergence, C1401–C1403). B position dependence is measured as positional zones (C956) and boundary glyph coupling (C1212, C1563); "phase-encoded" is the C382 reading, whose labels rest on withdrawn constructs. The AZC "99 forbidden pairs" (C309, Tier 2) are placement-code transitions — the same kind of measurement as C433/C434, which were retracted in PHASE_742 as transcription-serialization artifacts; C309 has not been re-audited.]*

### Closure Mechanisms

Both A and B have closure strategies, but they differ:

| System | Mechanism | Evidence |
|--------|-----------|----------|
| Currier A | **Compositional closure** | 897 PREFIX+MIDDLE+SUFFIX combinations (C267) |
| Currier B | **Execution closure** | 57.8% folios terminate in STATE-C |

These are **functionally equivalent** at the conceptual level (both represent "completion") but structurally distinct.

*[Historical: "execution closure" rests on convergence to STATE-C, which is withdrawn; C074 is occupancy only (C1401–C1403). See STATUS_BRIEF §3.]*

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

B expresses positional preferences through **morphological phase encoding** (C382; Tier 2, labels rest on withdrawn kernel/LINK readings):
- KERNEL-HEAVY prefixes (ch, sh, ok): 100% kernel contact, LINK-avoiding
- KERNEL-LIGHT prefixes (da, sa): <5% kernel contact, LINK-attracted

**Same signal, different expression:** Both A and B show prefix-position associations, but A uses block structure while B uses kernel topology.

*[Status: the kernel/LINK readings above are withdrawn (C089 superseded by C2082; C609, C1174). B's measured position structure is positional zones (C956), boundary glyph coupling (C1212, C1563) and word-ending routing (C2082).]*

---

## Three-System Model

```
           CURRIER A                CURRIER B                    AZC
           ─────────                ─────────                    ───
           Registry                 Programs                     Diagrams

Structure: Entry → DA → Entry      Line → Line → Line          Placement → Placement
           [blocks repeat]          [converges to STATE-C]*      [spatially coded]

Position:  FREE (block-relative)   DEPENDENT (phase-encoded)   CODED (placement-locked)

Grammar:   None                     49-class sequential          Hybrid (99 forbidden pairs)

DA Role:   Entry/segment boundary   Line boundary               Central diagram position

Type:      UNIFIED (C383)          UNIFIED (C383)              UNIFIED (C383) [v7.26 status: C383 demoted to Tier 3 (kernel contact is a spelling identity; monitoring reading withdrawn)]
```

\* Withdrawn: convergence to STATE-C (C074 occupancy only; C1401–C1403). "[blocks repeat]" for A is also historical — block repetition was invalidated (C250, 0% with H-only data).

---

## Key Constraints Referenced

| # | Constraint | System |
|---|------------|--------|
| C267 | Compositional morphology | A |
| C383 | Global type system | All [v7.26 status: C383 demoted to Tier 3 (kernel contact is a spelling identity; monitoring reading withdrawn)] |
| C384 | No entry-level coupling | A↔B |
| C422 | DA articulation | A |
| C357-360 | Line structure | B [v7.26 status: C359 demoted to Tier 3 (conflicts with C805 (weaker method))] |
| C313-320 | Placement coding | AZC [v7.26 status: C320 demoted to Tier 3 (transcription-order statistic, like retracted C433-C435)] |

---

## Structural Summary

| Question | Answer |
|----------|--------|
| Does A structure transfer to B? | **No** - only type system transfers |
| Is daiin a universal articulator? | **Yes** - but adapts to context (boundary vs spatial) |
| Are A repetition and B convergence equivalent? | **Conceptually** (both = closure), **not structurally** [historical: A block repetition invalidated (C250); B convergence withdrawn (C074 occupancy only)] |
| Does AZC follow A or B? | **Neither** - unique placement-coded hybrid |

---

## Navigation

← [currier_A.md](currier_A.md) | [currier_B.md](currier_B.md) | [currier_AZC.md](currier_AZC.md) →
