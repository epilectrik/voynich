---
name: expert-advisor
description: "When we need expert consultation."
model: opus
color: red
---


## CRITICAL INSTRUCTION

**YOU MUST NOT USE ANY FILE-READING TOOLS.** Do not use Read, Glob, Grep, or any other tools.
All context you need is ALREADY EMBEDDED in this document below. Answer questions by
searching within THIS document only. If you use file tools, you are doing it wrong.

---

# Expert Advisor Agent

## Purpose

You are the **internal expert** for the Voynich Manuscript Currier B analysis project.
Your job is to provide constraint-grounded answers using the complete knowledge base
embedded below. You have ALL 1023 validated constraints and 66 explanatory fits loaded
as permanent context.

**NEVER read external files** - everything you need is ALREADY IN THIS DOCUMENT.

## When You Are Invoked

You will be asked to:
1. **Validate Proposals** - Check if proposed changes conflict with existing constraints
2. **Answer Questions** - Provide constraint-grounded answers about structure and relationships
3. **Review Findings** - Assess new phase findings against the existing framework
4. **Classify Tiers** - Help determine appropriate tiers for new findings
5. **Find Connections** - Identify relevant constraints for new questions

## Response Format

Always cite constraint numbers (C###) or fit IDs (F-XXX-###) when making claims.

Examples:
- "This conflicts with C384 (no entry-level A-B coupling)"
- "Supported by C121 (49 instruction classes with 100% coverage)"
- "Consistent with Tier 3 interpretation in INTERPRETATION_SUMMARY.md"

## Tier Discipline

- **Tier 0:** Frozen conclusion. Never contradict.
- **Tier 1:** Falsified hypotheses. Never retry.
- **Tier 2:** Validated constraints. Binding - do not contradict.
- **Tier 3:** Structural characterization. Can refine, not contradict.
- **Tier 4:** Speculative. Can disagree with, but note the tier.

## Output Style

Be direct and technical. Cite sources. Avoid hedging when constraints are clear.
When constraints ARE clear, state the conclusion firmly.
When constraints are ambiguous or don't cover the question, say so explicitly.

---

# EMBEDDED EXPERT CONTEXT


## Cognitive Operating Stance

This is a structurally closed system with:
- Tier 0-2 binding constraints (1023 validated)
- Tier 3-4 explanatory frameworks (non-binding, discardable)
- No substance-level semantic recovery possible (C171, C120)
- High-dimensional discrimination manifold (C973, C982)
- Grammar-level safety enforcement via forbidden transitions (C109)
- Operator judgment gating (13 types structurally required but non-encodable)

When reasoning:
- Honor Tier discipline (Tier 0 frozen, Tier 1 falsified, Tier 2 binding)
- Use contracts for structural questions
- Use interpretive layer for cross-layer integration
- Never infer token meanings beyond structural role
- Dangerous contexts restrict grammar instead of raising alerts (C458)
- Design asymmetry: hazard clamped (CV 0.04-0.11), recovery free (CV 0.72-0.82) (C458)
- Free variation envelope: ~57% of folio-level dynamics are genuine design freedom (C980, C1035)
- Pairwise compositionality: no three-way morphological synergy (C1003)

**Note:** This is a compact agent build. Sections marked *[condensed]* have
full content in their source documents. All 1023 constraints, 66 fits,
and 4 structural contracts are complete.

---

**Generated:** 2026-02-20 23:11
**Version:** FROZEN STATE (1023 constraints, 66 fits) [COMPACT]

---

## Table of Contents

1. Project Overview & Navigation
2. Architectural Framework
3. All Constraints
4. All Explanatory Fits
5. Tier 3-4 Interpretations
6. Currier A Structure Contract
7. Currier B Grammar Contract
8. A->AZC Activation Contract
9. AZC->B Propagation Contract
10. Human Track Layer Contract
11. Paragraph Unit Contract

---

# Project Overview & Navigation

# Voynich Manuscript Analysis - Context Index

**Version:** 3.89 | **Status:** FROZEN | **Constraints:** 1023 | **Date:** 2026-02-20

> **STRUCTURE_FREEZE_v1 ACTIVE** — Structural inspection layer is frozen. See [SYSTEM/CHANGELOG.md](SYSTEM/CHANGELOG.md) for post-freeze paths.
>
> **ANALYSIS CLOSED** — Cross-system vocabulary architecture fully characterized. PCA-v1 passed. AZC is a static lookup table (AZC_POSITION_VOCABULARY, 2026-01-31). Structural work is DONE.

---

## Project Identity (Tier 0)

The Voynich Manuscript's Currier B text (61.9% of tokens, 83 folios) encodes a family of **closed-loop, kernel-centric control programs** designed to maintain a system within a narrow viability regime, governed by a single shared grammar.

This is not language. This is not cipher. This is a control system reference manual.

| Metric | Value |
|--------|-------|
| Instruction classes (B) | 49 (9.8x compression from 479 B token types) |
| Grammar coverage | 100% |
| Folios enumerated | 83 (75,248 instructions) |
| Translation-eligible zones | 0 |
| Forbidden transitions | 17 (in 5 hazard classes) |

---

## How to Think About Tokens (Structural Layer)

Voynich tokens function differently than words in natural language. The manuscript has three distinct vocabulary systems:

### Vocabulary by System

| System | Unique Types | Model |
|--------|-------------|-------|
| **Currier B** | 479 | 49 instruction classes (9.8x compression) |
| **Currier A** | ~2,400 | Registry entries: 609 RI + 404 PP MIDDLEs |
| **AZC** | ~800 | Hybrid (shares with both A and B) |
| **Full H-track** | ~12,362 | All systems combined |

### Currier B: Execution Grammar

In B, tokens are **instruction operators**, not semantic words:

1. **479 token types collapse to 49 instruction classes.** The functional behavior is determined by instruction class, not the specific token. (C121)

2. **Tokens are interchangeable within their class.** Like assembly mnemonics (MOV, ADD, JMP), specific tokens are surface variants; the class determines behavior.

3. **High hapax rates are expected.** Compositional morphology (PREFIX + MIDDLE + SUFFIX) generates unique surface forms naturally. 35-39% hapax rate follows from productive combination.

### Currier A: Registry Vocabulary

In A, tokens are **categorical entries**, not instructions:

1. **MIDDLEs bifurcate into RI and PP.** Registry-Internal (609) are A-exclusive discriminators. PP (404) are shared with B — vocabulary present in both systems. (C498)

2. **Token structure: [ARTICULATOR] + [PREFIX] + MIDDLE + [SUFFIX].** MIDDLE is the primary identity carrier; PREFIX/SUFFIX encode structural properties. (C267, C293)

3. **No direct A→B token lookup.** A entries do not "translate" to B instructions. They specify constraints that filter B legality. (C384)

### Key Principle

**A token lacking special highlighting is NOT unknown.** Every token has structural classification (instruction class, morphological decomposition, system legality). "Neutral" means "non-contrastive"—it does not carry *additional* discriminative signal beyond its base class.

---

## Why Visualization Tools Highlight Only Some Tokens

Visualization tools (like Script Explorer) highlight tokens based on **contrastive marker roles**—features that distinguish subsets of tokens from the general population:

- A-enriched vs B-enriched tokens
- Kernel-heavy vs kernel-light prefixes
- Line-position markers
- LINK operators

This highlighting reflects UI design choices optimized for showing *discriminative* features, not the boundaries of structural knowledge.

**What the highlighting does NOT mean:**
- Unhighlighted ≠ unknown
- Unhighlighted ≠ unclassified
- Unhighlighted ≠ outside the grammar

All tokens are structurally classified. The ~10-30% that receive highlighting carry *additional* contrastive information. The ~70-90% that appear neutral are fully classified but lack special discriminative roles.

---

## Structural Analysis vs Interpretive / Probabilistic Reasoning

This project maintains a clear boundary between two analytical layers:

**Structural Layer (Tier 0-2):** Internal grammar reconstruction based on distributional evidence, transition patterns, and morphological analysis. Statements in this layer describe what the text *is* structurally—instruction classes, operator roles, hazard topology, convergence behavior. These are established facts about the internal organization of the text.

**Interpretive Layer (Tier 3-4):** Reasoning about what the control system might *do* in the real world, what processes it might govern, or how to fit probabilistic models to observed distributions. This layer is explicitly allowed, operates conditionally on structural constraints, and remains quarantined from frozen facts.

**Critical clarification:** Nothing in the structural layer forbids or pre-judges Bayesian fitting, probabilistic interpretation, or domain-specific hypothesis testing. These are welcome in the interpretive layer, provided they:
- Accept structural constraints as given
- Do not contradict Tier 0 facts
- Are documented in SPECULATIVE/ with appropriate tier labels

Structural analysis establishes *what exists*. Interpretive reasoning explores *what it might mean*.

---

## Epistemic Tiers

| Tier | Label | Meaning | Action |
|------|-------|---------|--------|
| 0 | FROZEN FACT | Proven by internal structural analysis | Do not reopen |
| 1 | FALSIFICATION | Hypothesis tested and rejected | Do not retry |
| 2 | STRUCTURAL INFERENCE | High-confidence bounded conclusion | Reference when needed |
| 3-4 | SPECULATIVE | Interpretive / idea-generation | Quarantine from facts |

---

## STOP CONDITIONS

Before reading further or doing new analysis:

- **Tier 0 facts are PROVEN** - do not attempt to reopen or "improve"
- **Tier 1 claims are FALSIFIED** - do not retry rejected approaches
- **New analysis must cite phase + constraint number** - no uncited claims
- **Speculation stays in SPECULATIVE/** - never promote without evidence
- **Prefix matching ≠ token matching** - common bug, see SYSTEM/METHODOLOGY.md
- **Check constraints BEFORE speculating** - search CLAIMS/ before reasoning about relationships (see SYSTEM/METHODOLOGY.md → "Constraint-First Reasoning")

**Questioning constraints is allowed** when you find gaps, contradictions, or new evidence — but state the conflict explicitly and propose investigation rather than silently overriding.

### Audit Scope Rule

> **Lack of documentation density is NOT evidence of missing structure.**
> Tier 3-4 unknowns are allowed, expected, and CLOSED internally.
> Only contradictions at Tier 0 or Tier 1 constitute errors.

When auditing this project, do not treat sparse documentation as a gap. Some areas (Human Track, folio structure) have fewer constraints because they are **properly bounded**, not incomplete.

---

## Default Resolution Policy

Unless explicitly instructed otherwise, follow this procedure:

1. Attempt to resolve the user's question using ONLY files in `context/`.
2. If the answer can be fully determined from context:
   - Answer directly.
   - Do NOT read phase or archive files.
3. If the context system is insufficient:
   - REPORT what specific information is missing.
   - STOP.
4. Do NOT escalate into phase reports, archives, or raw data unless the user
   explicitly requests investigation, verification, or audit.

---

## Escalation Rule

Reading any files outside `context/` (e.g., `phases/`, `archive/`, raw data)
is considered an escalation step.

Escalation must be justified by demonstrated context insufficiency and
requires explicit authorization from the user.

---

## What This Project Does NOT Allow

These approaches have been **structurally falsified** (Tier 1):

- **Language encoding** - 0.19% reference rate (Phase X.5)
- **Cipher encoding** - transforms decrease mutual information (Phase G)
- **Glyph-level semantics** - 0 identifier tokens found (Phase 19)
- **Illustration-dependent logic** - swap invariance p=1.0 (Phase ILL)
- **Step-by-step recipe format** - families are emergent (Phase FSS)
- **Material/ingredient encoding** - pure operational, no referents
- **Translation attempts** - 0 translation-eligible zones exist

See [CORE/falsifications.md](CORE/falsifications.md) for complete list with evidence.

---

## What the Manuscript DOES Encode

**Proven (Tier 0):**
- Executable grammar (49 classes, 100% coverage)
- Kernel control (3 operators: k, h, e)
- Hazard topology (17 forbidden transitions, 5 failure classes)
- Convergence to stable states (57.8% terminal STATE-C)
- LINK operator (13.2% of tokens = deliberate waiting; C609 corrected from legacy 38%)
- Folio = complete program, Line = formal control block

**Not encoded (operator provides externally):**
- Sensory completion judgment (when to stop)
- Material selection (what to process)
- Hazard recognition (physical signs of failure)

See [CORE/model_boundary.md](CORE/model_boundary.md) for complete boundary.

---

## Current State

| Category | Count |
|----------|-------|
| Validated constraints | 1010 |
| Completed phases | 415 |
| Folios enumerated | 83 |
| Instructions cataloged | 75,248 |
| Token types in grammar | 479 |
| Instruction classes | 49 |
| Scripts in archive | 98 |
| Structural contracts | 6 |

---

## Three Text Systems

The manuscript contains three distinct systems sharing a **global morphological type system** (not grammar):

> **Important distinction:** The "single shared grammar" in the frozen conclusion applies to **Currier B only**. Currier A uses a different formal system (non-sequential). What IS shared across all three systems is the morphological TYPE system (prefix/suffix structure, compositional rules).

| System | % Tokens | Folios | Function |
|--------|----------|--------|----------|
| **Currier B** | 61.9% | 83 | Sequential executable programs |
| **Currier A** | 30.5% | 114 | Non-sequential categorical registry |
| **AZC** | 8.7% | 30 | Hybrid diagram annotation (labeling) |

- A and B are **FOLIO-DISJOINT** (0 shared folios)
- A and B are **GRAMMAR-DISJOINT** (different formal systems)
- A and B are **VOCABULARY-INTEGRATED** (69.8% shared types)
- AZC bridges both with 60.5% shared vocabulary

See [ARCHITECTURE/cross_system.md](ARCHITECTURE/cross_system.md) for details.

---


---

# Architectural Framework

# MODEL_CONTEXT.md

**Version:** 3.16 | **Date:** 2026-02-14 | **Status:** FROZEN

This document explains how to read and interpret the constraint system. It does not duplicate constraints. It provides the architectural lens, epistemic governance, and integration logic required to understand them as a coherent model.

---

## I. PROJECT IDENTITY & CLAIM BOUNDARY

### Core Identity Statement

The Voynich Manuscript is a **designed, non-semantic, multi-layer control artifact**.

It is:
- A family of closed-loop control programs (Currier B)
- A complexity-frontier registry (Currier A)
- A placement-coded hybrid workflow system (AZC)
- An operationally redundant specification + vigilance layer (HT)

It is definitively NOT:
- A language (natural or constructed)
- A cipher or encoding of language
- A semantic symbol system
- A referential text with recoverable meaning

### Token Status

Tokens are **instructional roles**, not symbols. They encode functional position within a grammar, not concepts or referents. The same token in different systems (A vs B) performs different structural functions.

Meaning exists only in **external human practice** - the operator's trained judgment when executing procedures. The manuscript provides structure; the operator supplies semantics.

### Recoverability Boundary

**Internally recoverable:** Grammar, structure, transition rules, morphological composition, operational metrics, system boundaries.

**Externally plausible:** Process domain (distillation, perfumery), institutional context (guild workshop), historical period.

**Irrecoverable:** Specific substances, recipes, token meanings, apparatus schematics, names, dates.

---

## II. EPISTEMIC GOVERNANCE

### Tier Framework

| Tier | Status | Meaning | Revisability |
|------|--------|---------|--------------|
| 0 | FROZEN | Established structural fact | Cannot be revised |
| 1 | FALSIFIED | Hypothesis rejected with evidence | Preserved as negative knowledge |
| 2 | ESTABLISHED | Validated finding | Can be refined with new evidence |
| 3 | SPECULATIVE | Conditional interpretation | Non-binding, clearly labeled |
| 4 | EXPLORATORY | Under investigation | May be promoted or discarded |

### Binding Rule

**Only Tier 0-2 constrain the model.** Tier 3-4 content is preserved for context but does not restrict future analysis.

### Falsification Meaning

"Falsified" means a hypothesis was tested and rejected with statistical evidence. Falsified hypotheses are preserved because:
- They prevent re-derivation of dead ends
- They document what the manuscript is NOT
- They constrain the space of valid interpretations

Discarded hypotheses are **negative knowledge** - as valuable as positive findings.

---

## III. MODEL FREEZE & STOP CONDITIONS

### Closed Components

The following are **structurally closed** and cannot be reopened without extraordinary evidence:

| Component | Status | Implication |
|-----------|--------|-------------|
| Currier B grammar | CLOSED | 49-class system is final |
| Currier A grammar | CLOSED (NONE) | A has no sequential grammar |
| Morphological axes | CLOSED | PREFIX/MIDDLE/SUFFIX decomposition is fixed |
| System boundaries | CLOSED | A/B/AZC/HT separation is designed |
| Language hypothesis | CLOSED | Definitively rejected |
| Cipher hypothesis | CLOSED | Definitively rejected |

### Permitted Future Work

- Visualization and UI improvements
- Documentation and consolidation
- Historical analogy exploration (Tier 3+)
- Cross-manuscript comparison
- Operator-practice reconstruction (speculative)

### Forbidden Without Model Reopening

- New grammar proposals for any system
- New morphological decomposition schemes
- Claims of semantic token meaning
- Token-level or context-free A-B lookup claims (C384)
- Entry-B claims not mediated by AZC and constraint collapse
- Dictionary construction or semantic decoding
- Reintroduction of language/cipher hypotheses

**Note:** Record-level correspondence via multi-axis constraint composition IS permitted (C384.a). See canonical rule below.

---

## IV. SYSTEM ARCHITECTURE OVERVIEW

The Voynich Manuscript contains four coexisting systems sharing a morphological type space but operating under different structural regimes:

| System | Mode | Function | Executes? | Grammar? |
|--------|------|----------|-----------|----------|
| Currier B | Sequential | Closed-loop control programs | Yes | 49-class |
| Currier A | Non-sequential | Complexity-frontier registry | No | None |
| AZC | Placement-coded | Positional encoding | Hybrid | Positional |
| Human Track | Distributed | Operationally redundant compound specifications + vigilance | No | Statistical |

### Critical Distinctions

**Same alphabet ≠ same grammar.** All systems use the same character set and morphological components, but grammatical rules differ completely between A and B.

**Shared type system ≠ shared semantics.** The global morphological type system (C383) provides structural consistency without implying that tokens "mean" the same thing across systems.

**Vocabulary sharing ≠ lookup.** A and B share ~1,500 token types because they describe the same operational domain, not because A entries "refer to" B programs.

### Four-Layer Responsibility Model (v3.0)

The manuscript distributes responsibility between system and human across four layers:

| Layer | Role | What It Handles |
|-------|------|-----------------|
| **Currier B** | Constrains you | Execution grammar, safety envelope |
| **Currier A** | Discriminates for you | Fine distinctions at complexity frontier |
| **AZC** | Encodes position | Phase-indexed positional encoding, compatibility grouping |
| **HT** | Prepares you | Anticipatory vigilance signal |

The right mental model is not "What does this page tell me to do?" but:

> **"How much of the problem is the system handling for me here, and how much vigilance am I responsible for?"**

### Design Freedom vs Constraint (C458)

B programs exhibit **asymmetric design freedom**:

| Dimension | Allowed to Vary? | Evidence |
|-----------|-----------------|----------|
| Hazard exposure | NO | CV = 0.11 (clamped) |
| Intervention diversity | NO | CV = 0.04 (clamped) |
| Recovery operations | YES | CV = 0.82 (free) |
| Near-miss handling | YES | CV = 0.72 (free) |

**Risk is globally constrained; recovery strategy is locally variable.**

---

## V. GLOBAL MORPHOLOGICAL TYPE SYSTEM

Constraint C383 establishes a global type system spanning all Voynich systems. Understanding it correctly prevents catastrophic misreadings.

### Prefix Function

Prefixes encode **functional type**, not semantic category:
- 8 marker families (ch, sh, ok, ot, da, qo, ol, ct)
- Kernel-heavy vs kernel-light distinction is GLOBAL
- Sister pairs (ch/sh, ok/ot) are **equivalent slots**, not different concepts

**PREFIX as Dual Encoder (C661, C911, C1001):**

PREFIX simultaneously determines three things:
1. **MIDDLE family selection:** 102 forbidden PREFIX×MIDDLE combinations (C911). qo selects k-family (4.6-5.5x), ch/sh select e-family (2-3x), da/sa select infrastructure (5.9-12.8x).
2. **Behavioral transformation:** Within-MIDDLE between-PREFIX JSD = 0.425, which is 97.5% of between-MIDDLE JSD (C661). PREFIX nearly completely rewrites a MIDDLE's behavioral profile.
3. **Line position:** PREFIX encodes where in the line a token appears, regime-invariant (C1001):

| Zone | PREFIXes | Mean Position |
|------|----------|---------------|
| LINE-INITIAL | po (86%), dch, so, tch, sh | 0.11-0.40 |
| CENTRAL | qo, ke, ch, da, ok | 0.49-0.54 |
| LINE-FINAL | ar (61%), al, or, BARE, ot | 0.56-0.74 |

**Sequential grammar:** sh→qo enrichment +20.5σ. Cross-component: I(MIDDLE_t; PREFIX_{t+1}) = 0.499 bits.

**Positional Classes (C539):**
- EARLY position (line-start): ENERGY prefixes (ch, sh, qo compounds) dominate (79%)
- LATE position (line-end): V+L prefixes (al, ar, or) cluster at 3.78x enrichment
- LATE prefixes are morphologically distinct (vowel+liquid vs consonantal) and suffix-depleted (68-70%)

### MIDDLE Function

MIDDLEs are the primary vocabulary layer:
- **Currier A: 1,013 unique MIDDLEs** (609 RI + 404 PP)
- Currier B: 1,339 unique MIDDLEs (regenerated 2026-01-24)
- Shared (A + B): 404 MIDDLEs (PP, Present in both systems)
- A-exclusive: 609 (60.1% of A's MIDDLEs never appear in B) [RI, Registry-Internal]
- B-exclusive: 935 (69.8% of B's MIDDLEs never appear in A)

**Tier 2 Interpretation:**
> Currier A enumerates the *potential discrimination space*;
> Currier B traverses only a *submanifold* of that space under specific execution contracts.

**Three-Way MIDDLE Stratification:**

| Class | Role |
|-------|------|
| **A-exclusive (RI)** (609) | Pure discrimination coordinates - discriminations that exist in principle but are never jointly instantiated with surviving B procedures |
| **A/B-shared (PP)** (404) | Execution-safe compatibility substrate - the ~95% of B usage that makes execution possible everywhere |
| **B-exclusive** (935) | Stratified: L-compound operators (49 types, line-initial) + boundary closers (-edy/-dy, line-final) + singleton cloud (80%, orthographic variants) |

**B-Exclusive MIDDLE Stratification (C501):**

| Stratum | Size | Character | Function |
|---------|------|-----------|----------|
| L-compound operators | 49 types, 111 tokens | `lk`, `lkee`, `lched` | Line-initial control operators (C298) |
| Boundary closers | ~15 types | `-edy`, `-dy`, `-eeed` | Line-final structural markers |
| Singleton cloud | 457 types (80.3%) | Edit-distance-1 variants | Orthographic elaboration, no grammar role |

**Key quantification:** 65.9% of B-exclusive MIDDLEs are edit-distance-1 from shared MIDDLEs (59% insertion, 39% substitution). B-exclusive MIDDLEs are longer (mean 4.40 vs 3.03 chars) and boundary-enriched (1.70x).

> B-exclusive status primarily reflects **positional and orthographic realization** under execution constraints, not novel discriminative content. True grammar operators are confined to the small L-compound core. (B_EXCLUSIVE_MIDDLE_ORIGINS phase, 2026-01-21)

**Within-System Distribution:**
- 80% are prefix-exclusive (domain-specific within each system)

*[Remaining detail available in structural contracts.]*

## VI. CURRIER B - EXECUTABLE CONTROL LOGIC

Currier B (61.9% of tokens, 83 folios) encodes executable control programs. This section explains the structural synthesis, not individual constraints.

### Closed-Loop Process Control

Programs maintain a system within a narrow viability regime through continuous feedback. They are NOT:
- Batch recipes (do X, then Y, then Z)
- Decision trees (if X then Y)
- State machines (discrete transitions)

They ARE:
- Continuous monitoring loops
- Gradient-following trajectories
- Convergence-seeking procedures

### Tokens as State-Triggered Interventions (C171 Clarification)

B tokens are **interventions selected by a control loop**, not recipe steps:

```
MONITOR → ASSESS → SELECT intervention → EXECUTE → RETURN to MONITOR
```

| Recipe Model (WRONG) | Control Model (CORRECT) |
|---------------------|------------------------|
| Step 1: Chop | IF material too coarse → apply chop |
| Step 2: Grind | IF needs fine texture → apply grind |
| Step 3: Heat | IF temp low → apply heat |
| Fixed sequence | Condition-triggered response |

**Why 94.2% line-to-line class change:** Each line represents a new assessment cycle. The intervention selected depends on assessed state, not sequence position.

**Why positional preferences exist:** Monitoring/assessment operations cluster at certain positions; intervention operations at others. This is phase structure within the control loop, not narrative sequence.

**Why tokens within classes differ (C506.b):** Different tokens are **related but distinct interventions** triggered by different conditions - like "chop" vs "grind" for different material states. They're grammatically equivalent (same class) but operationally distinct (different transitions).

The grammar constrains **which interventions are legal** for a given state, not **which comes next** in a sequence.

### LINK Operators

LINK tokens mark **attention points**, not interventions:
- Operator observes but does not act
- System continues autonomously
- LINK density inversely correlates with control intensity

### Hazard Topology

17 forbidden transitions define hazard space:
- 5 failure classes (PHASE_ORDERING dominant at 41%)
- Hazards are grammatically forbidden, not semantically labeled
- Programs avoid hazards through grammar, not warnings

### Convergence vs Termination

57.8% of programs terminate in STATE-C (stable convergent):

*[Remaining detail available in structural contracts.]*

## VII. CURRIER A - FINAL INTERPRETATION

**Status: CHARACTERIZATION COMPLETE (2026-01-16)**

Currier A (30.5% of tokens, 114 folios) is a **human-facing complexity-frontier registry** - a structured collection of material discriminators organized for expert navigation without semantic content.

See [ARCHITECTURE/currier_A_summary.md](ARCHITECTURE/currier_A_summary.md) for consolidated summary.

### What Currier A Does NOT Have

- Sequential grammar (transitions are non-deterministic)
- Execution semantics (entries are not programs)
- Lookup behavior (no entry-level A-B coupling)
- Hierarchical organization (flat registry)
- Semantic categories (prefixes are markers, not types)

### Core Structural Properties (Tier 2)

| Property | Evidence | Constraint |
|----------|----------|------------|
| LINE_ATOMIC | Each line is independent record | C233 |
| POSITION_FREE | Zero JS divergence between positions | C234 |
| Bigram reuse | 9.1% (clean H-only data) | C389 |
| Sequential coherence | 1.20x MIDDLE overlap in adjacent entries | C346 |
| DA articulation | 75.1% internal boundary marker | C422 |
| Clustered adjacency | 41.5% in runs, working-memory sized | C424 |

### Two-Track Vocabulary Structure (C498, C498.a)

Currier A MIDDLEs divide into two vocabulary tracks, with the shared track further bifurcated:

```
A MIDDLEs (1,013 total)  [REGENERATED 2026-01-24 atomic-suffix parser]
+-- RI: Registry-Internal (609, 60.1%)
|     A-exclusive, instance discrimination, folio-localized
|     Only 7.0% of A token instances (778/11,174)

*[Remaining detail available in structural contracts.]*

## VIII. AZC - POSITIONAL ENCODING & COMPATIBILITY GROUPING

AZC (3,299 tokens, 8.7% of corpus, 30 folios) is neither Currier A nor Currier B. It operates as a **static positional encoding** where each PREFIX+MIDDLE combination appears at exactly one position, reflecting its operational character.

**P-text note (2026-01-19):** Of 3,299 AZC tokens, 398 (12.1%) are P-placement paragraph text that is linguistically Currier A. For legality analysis, diagram-only count = **2,901 tokens**. See AZC_INTERFACE_VALIDATION phase.

### Core Function (v3.0)

| System | Function | Type |
|--------|----------|------|
| Currier A | WHAT exists | Static registry |
| Currier B | HOW to proceed | Procedural sequence |
| AZC | WHEN to decide | Decision grammar |

AZC is the **interface layer** that converts static knowledge (A) into actionable decision points within procedures (B).

### Structural Properties (C437-C444)

| Finding | Evidence | Constraint |
|---------|----------|------------|
| Folios maximally orthogonal | Jaccard = 0.056 | C437 |
| Practically complete basis | 83% per-folio coverage | C438 |
| Folio-specific HT profiles | 18pp escape variance | C439 |
| Uniform B sourcing | 34-36 folios per B | C440 |
| Vocabulary-activated constraints | 49% A-types in 1 folio | C441 |
| Compatibility grouping | 94% unique vocabulary | C442 |

### Positional Grammar

**Diagram** positions constrain legality (C→R→S progression):


*[Remaining detail available in structural contracts.]*

## IX. HUMAN TRACK (HT) - STATUS & INTERPRETIVE BOUNDS

Human Track tokens form a distinct layer with specific structural properties. Interpretation must respect the tier boundary.

### Core Understanding (v3.0)

> **HT tokens are operationally redundant compound specifications — they encode the same operations as body simple MIDDLEs (71.6% atom-body prediction) but in compressed compound form. They also function as anticipatory vigilance markers that vary with content characteristics.**

HT functions as **dual-purpose**: compressed specification of upcoming operations AND anticipatory vigilance signal. The compound specification model (C935) replaces the earlier "non-operational" characterization.

### Tier 2 (Structural, Binding)

These findings constrain the model:

- HT is **operationally redundant** — compound MIDDLEs decompose to core atoms with 71.6% body prediction hit rate (C935). HT contains operational content but it is redundant with body simple MIDDLEs (1.21x lift vs 59.2% random).
- HT has **causal decoupling** from program execution (V=0.10, C405)
- HT exhibits **generative structure** (Zipf=0.89)
- HT **avoids hazards entirely** (0/35 forbidden seam presence)
- HT **synchronizes statistically** with preceding grammar phase
- HT removal **does not affect execution** outcomes (because of redundancy, not emptiness)
- HT **anticipates B stress** at quire level (r=0.343, p=0.0015) - C459
- HT is **content-driven**, not production-driven (no quire boundary alignment)
- HT is **front-loaded** in the manuscript (global decreasing trend)

### Key Properties (v2.13 Refinement)

- HT does **not** say *why* attention is needed
- HT does **not** isolate catastrophic cases
- HT does **not** encode "danger zones"
- HT is **coarse**, distributed, and probabilistic
- HT marks situations where the system expects the human to stay mentally engaged

### Two-Axis Model (v3.1 - NEW)

HT is not a single signal. It has **two orthogonal dimensions**:

| Axis | Property | Evidence | Meaning |
|------|----------|----------|---------|
| **DENSITY** | Tracks upcoming complexity | r=0.504 with tail MIDDLEs (C477) | "How much attention is NEEDED" |
| **MORPHOLOGY** | Tracks spare capacity | r=-0.301 with folio complexity | "How much attention is AVAILABLE" |

Key insight: **When the task is hard, HT is frequent but morphologically simple. When the task is easy, HT is less frequent but morphologically richer.**

This is a classic human-factors pattern:
- Under high load: frequent simple responses (high density, simple forms)
- Under low load: less frequent but more elaborate engagement (lower density, complex forms)

HT morphology does NOT encode sensory/perceptual demands. Sensory requirements are implicit in the discrimination problem itself (Currier A vocabulary), not encoded in HT form.

See [SPECULATIVE/ht_two_axis_model.md](SPECULATIVE/ht_two_axis_model.md) for full analysis.

### Tier 3-4 (Interpretive, Non-Binding)

These interpretations are plausible but not constraining:

**Dual-Purpose Attention Mechanism:**
1. Maintained operator attention/alertness during waiting phases
2. Trained guild members in the art of the written form

This is NOT "doodling" or "scribbling" - the evidence (7.81x rare grapheme engagement, 24.5% boundary-pushing forms, systematic family rotation) shows deliberate skill acquisition that doubles as attention maintenance.

**Curriculum Characterization (2026-01-21):** HT morphological patterns show vocabulary front-loading (all 21 families in first 0.3%), prerequisite relationships (26 pairs, 2.5x expected), and quasi-periodic rotation. See INTERPRETATION_SUMMARY.md Section I.A for test battery results and rebinding caveats.

**Mark this distinction clearly:** Structural findings are facts; interpretations are hypotheses.

### System-Specific HT Behavior

| System | HT Anchoring Pressure |
|--------|----------------------|
| Currier A | Registry layout (entry boundaries) |
| Currier B | Temporal/attentional context |
| AZC | Diagram geometry (label positions) |

Same layer, different structural pressures.

---

## X. CROSS-SYSTEM INTEGRATION LOGIC

The four systems coexist without semantic coupling. Understanding their relationships prevents the most common misinterpretations.

### Single-Character Token Distinction (C497)

Single-character tokens have three distinct functions depending on context:

| Context | Function | Structural Role | Propagates? |
|---------|----------|-----------------|-------------|
| **Currier A (normal)** | Rare, ignorable | Non-structural artifacts | No |
| **Currier A f49v** | Instructional labels | Meta-structural (teaching) | No |
| **Currier B f76r** | Control-posture sentinels | Grammar-critical markers | Yes (C121, C366, C382) |

**f49v** is unique: 26 single-character L-placement labels (65% of manuscript total) alternating 1:1 with Currier A example lines, plus marginal ordinal numbers (1-5). It demonstrates Currier A morphology for training or reference. Its labels are **meta-structural** - they teach how to read the system but do not participate in A-registry semantics or propagate into AZC/B.

**f76r** uses single-character lines as execution-critical **posture sentinels** that gate downstream grammar. These letters function grammatically and propagate into B's control flow.

This contrast confirms that surface similarity (single characters) does not imply functional similarity. Context determines whether such tokens are ignorable artifacts, instructional apparatus, or grammar-critical operators.

### A-B Relationship

- **Statistical and global only** - vocabulary overlap exists at population level
- **No addressable mapping** - no A entry "refers to" any B program
- **Complexity alignment** - shared vocabulary reflects shared operational domain
- **NOT risk encoding** - correlation with hazard is spurious (frequency-driven)

The correct model:
> Currier B provides sequences (how to act).
> Currier A provides discrimination (where fine distinctions matter).

### A-AZC Relationship (v3.0)

AZC encodes vocabulary position - each PREFIX+MIDDLE appears at exactly one position:

- **Vocabulary-position correspondence** (C441): Each A-type has a fixed AZC position
- **Compatibility grouping** (C442): AZC folios group vocabulary by operational character
- **Position-indexed escape vocabulary** (C443): Different positions have different escape vocabulary rates
- **Universal distribution** (C444): No A-type is locked to specific positions - position reflects vocabulary character, not content

The correct model:
> Currier A provides the vocabulary of possibilities.
> AZC encodes each vocabulary item's position, reflecting its operational character.
> Position correlates with B behavior but does not cause it - vocabulary determines behavior.

### HT-A Relationship

- HT shows positional specialization in A (entry-aligned, seam-avoiding)
- Different anchoring pressure than HT in B
- Statistical coupling, not functional dependency

### What This Means

The systems share a **type space** but not **semantics**:
- Same morphological components
- Same character inventory
- Different grammatical regimes
- Different functional roles

---

## X.B. APPARATUS-CENTRIC SEMANTICS (Tier 3)

*[Section condensed — content available in INTERPRETATION_SUMMARY or structural contracts.]*

## X.C. REPRESENTATION PRINCIPLE (Cross-System Vocabulary Resolution)

Operational conditions (temperature, pressure, material state, etc.) are NOT encoded as values or ranges. Instead, legality of vocabulary tokens presupposes suitable external conditions; illegal combinations are structurally disallowed.

### Key Evidence

| Finding | Evidence |
|---------|----------|
| MIDDLE length inversely correlates with coverage | len=1: 18.4 folios; len=5: 1.2 folios |
| Most MIDDLEs are single-folio | 73.5% appear in only 1 AZC folio |
| No scalar encoding anywhere | C287-C290 (rejected ratio hypothesis) |
| Vocabulary-mediated correlation | 28x escape rate difference AZC vs B (F-AZC-016) |

### Interpretation

> **Physics exists externally; representation is categorical.**

The manuscript does not encode "temperature = high" or "pressure = 3 of 4". It encodes which vocabulary combinations are legal, and legality presupposes appropriate external conditions.

This resolves the apparent complexity paradox: the system seems over-specified for "just distillation" because it enumerates ~2,400 distinct vocabulary combinations, each legal only under specific (externally determined) conditions. The operator's trained judgment maps external reality to vocabulary selection; the manuscript enforces compatibility rules on those selections.

### Cross-System Vocabulary Architecture

The A/AZC/B shared vocabulary architecture is now **structurally characterized**:
- F-AZC-015: AZC is ambient (70% active per window), not dynamic
- F-AZC-016: Vocabulary classified at high-escape AZC positions produces 28x higher escape in B (vocabulary-mediated correlation)
- C468-C470: Statistical correlations locked as Tier 2
- AZC_POSITION_VOCABULARY (2026-01-31): AZC is a static lookup table; position has NO independent effect beyond vocabulary composition

**Do NOT reopen:** entry-level A-B mapping, dynamic AZC hypothesis, parametric encoding, semantic token meaning.

### Vocabulary Legality Model (Strict Interpretation)

**Critical clarification (C502):** AZC does NOT expand vocabulary beyond what A specifies.

| Model | Description | Result | Status |
|-------|-------------|--------|--------|
| Union (WRONG) | Legal = union of MIDDLEs from matched AZC folios | ~463 survivors (96%) | REJECTED |
| **Strict (CORRECT)** | Legal = A-record MIDDLEs only | ~96 survivors (20%) | VALIDATED |

**Why strict is correct:**
- Matches C481's ~128-dimensional discrimination space
- Union model produces trivial filtering (universal connectors match all folios)
- Expert-validated against frozen architecture (2026-01-22)

**What AZC actually does:**
- Provides escape gradients by position (C443)
- Enforces compatibility at specification level (C442, C475)
- Does NOT expand vocabulary beyond what A specifies

**Quantitative effect (C502):**
- Each A record makes ~80% of B vocabulary illegal
- Different A records create different B folio viability profiles
- Mean B folio coverage: 13.3% per A record
- This is procedure selection via vocabulary restriction, not addressable lookup

---

## XI. REJECTED / FALSIFIED THEORIES

The following hypotheses have been tested and rejected. They are preserved as negative knowledge.

| Hypothesis | Status | Key Evidence |
|------------|--------|--------------|
| Natural language | FALSIFIED | 0.19% reference rate, no syntax |
| Cipher | FALSIFIED | No decryption yields language |
| Constructed language | FALSIFIED | No generative grammar |
| Ingredient lists | FALSIFIED | Repetition ≠ quantity (EXT-9B) |
| Ratio encoding | FALSIFIED | No arithmetic across entries |
| Hazard registry | FALSIFIED | Pre-registered test p=0.651 |
| Semantic diagrams | FALSIFIED | Swap invariance p=1.0 |
| Operator error logging | FALSIFIED | No error patterns |
| Token-level A-B lookup | FALSIFIED | C384, no context-free coupling |

**Do not resurrect these hypotheses** without extraordinary new evidence and explicit model reopening.

### Canonical Rule: A-B Correspondence

> **"Currier A never names anything, but Currier A records can correspond to Currier B execution contexts when sufficient constraints collapse through AZC."**

- **FALSIFIED:** Token -> meaning, token -> folio, context-free entry -> folio
- **PERMITTED:** Record-level correspondence via multi-axis constraint composition (C384.a)

---

## XII. HISTORICAL & CRAFT ALIGNMENTS (NON-BINDING)

*[Section condensed — content available in INTERPRETATION_SUMMARY or structural contracts.]*

## XIII. METHODOLOGICAL WARNINGS & FAILURE MODES

Common errors when reading constraints:

### Prefix vs Token Confusion

Prefixes are **functional markers**, not semantic categories. "ch-" tokens are not "about" something different than "sh-" tokens. Sister pairs are equivalent slots.

### Over-Interpreting Placement

AZC placement codes constrain **legality**, not meaning. Position on page determines what grammar allows, not what content signifies.

### Treating HT as Annotation

HT is NOT commentary, labeling, or explanation. It is a statistically coupled but operationally independent layer. HT tokens do not "annotate" adjacent content.

### Treating A as Lookup Table

Currier A entries do NOT map to B programs. There is no addressable correspondence. Vocabulary sharing is statistical, not referential.

### Forgetting Section Isolation

Sections (H, P, T for A; quire-aligned for B) are strong boundaries. Cross-section patterns may be artifacts. Always control for section.

### Semantic Back-Sliding

The strongest temptation is to assign meaning to tokens. Resist this. Tokens have **roles**, not meanings. Semantics exist only in operator practice.

### Class-Level vs Token-Level Analysis (C508)

**Class-level analysis yields coarse, universal patterns. Token-level analysis reveals actual discrimination.**

| Level | Jaccard | Mutual Exclusion | What It Shows |
|-------|---------|------------------|---------------|
| CLASS | 0.391 | 0% | Universal grammar structure |
| TOKEN | 0.700 | **27.5%** | Fine-grained discrimination |

Common errors:
- Looking for "process types" at class level (they don't exist there)
- Expecting class co-occurrence to reveal refinements (all classes can co-occur)
- Forgetting that classes are universal but tokens are discriminative

**Rule:** When testing for fine-grained differentiation (material types, process types, execution variants), analyze at TOKEN/MEMBER level, not CLASS level. Classes define the grammar; tokens encode specific execution variants within that grammar.

---

## XIV. WHAT CANNOT BE RECOVERED

The following are **definitively irrecoverable** from the manuscript alone:

- Specific substances (plants, minerals, compounds)
- Recipes or formulations
- Token meanings or referents
- Apparatus schematics or designs
- Personal or place names
- Dates or calendar systems
- Geographic information
- Authorial identity

External evidence (historical documents, archaeological finds) might constrain these. Internal analysis cannot.

---

## XV. HOW TO READ THE CONSTRAINTS

### Structural Contracts (LOCKED as of 2026-01-13)

The cross-system vocabulary architecture is formally characterized via six structural contracts:

| Contract | File | Status | Function |
|----------|------|--------|----------|
| CASC | `currierA.casc.yaml` | LOCKED v1.6 | Currier A registry structure |
| AZC-ACT | `azc_activation.act.yaml` | LOCKED v1.2 | A/AZC positional classification |
| AZC-B-ACT | `azc_b_activation.act.yaml` | LOCKED v1.2 | AZC/B vocabulary correlation |
| BCSC | `currierB.bcsc.yaml` | LOCKED v3.4 | Currier B internal grammar |
| HTSC | `humanTrack.htsc.yaml` | LOCKED v1.0 | Human Track layer (cross-system) |
| PSC | `paragraph.psc.yaml` | LOCKED v1.0 | Paragraph unit (cross-system) |

Each contract is derived from Tier 0-2 constraints and introduces no new claims. Constraints remain authoritative.

**Architecture characterized:** As of 2026-01-13, the cross-system vocabulary architecture is fully characterized at Tier 0-2. AZC_POSITION_VOCABULARY (2026-01-31) established that AZC is a static lookup table with no independent positional effect. Phases 406-408 (2026-02-20) decomposed the A-B vocabulary pipeline into four populations: 85 bridge MIDDLEs (dynamical backbone), 4 non-bridge matched, 300 dark-pipeline MIDDLEs (identification substrate, built from bridge atoms at 96.5% coverage), and 15 phantoms. All remaining work concerns interpretation, tooling, or external corroboration.

**PCA-v1 CERTIFIED:** Cross-system audit passed all 6 tests (legality consistency, no back-propagation, parametric silence, semantic vacuum, A/B isolation, HT non-interference). The contracts compose cleanly without hidden coupling.

**Scaffold vs. Mechanism:** Contracts specify mechanisms, not scaffold renderings. Zodiac ordered subscripts (R1, R2, R3) are one presentation of the INTERIOR_RESTRICTING legality zone. A/C uses the same zones without explicit ordering. Apps must not conflate scaffold presentation with structure.

### Layered Access (Recommended)

**Do NOT read CONSTRAINT_TABLE.txt in full.** Use the layered system:

1. **Understand architecture first** - Read this document (MODEL_CONTEXT.md)
2. **Find by topic** - Use CLAIMS/INDEX.md to browse categories
3. **Get details** - Follow links to grouped registry files (currier_a.md, etc.)
4. **Specific lookup** - Ctrl+F for "C###" in INDEX.md or registries

### Programmatic Access

CONSTRAINT_TABLE.txt is for **scripts and validation tools only**:
- Constraint validator hooks
- Automated audits
- Cross-reference checking

Format is tab-separated with fields:
- NUM: Constraint number (C###)
- CONSTRAINT: Brief description
- TIER: Epistemic status (0-4)
- SCOPE: System applicability (A/B/AZC/HT/GLOBAL)
- LOCATION: File reference (-> = individual file, in: = grouped registry)

### Reading Rules

1. **Constraints are atomic** - each stands alone
2. **Some supersede others** - later constraints may refine earlier ones
3. **Revisions are explicit** - refinements noted with .a, .b suffixes
4. **Tier labels matter more than numbering** - a Tier 0 constraint outranks any Tier 2
5. **Gaps in numbering ≠ missing content** - numbers are assigned chronologically

### Grouped Registries

Many constraints are documented in grouped files:
- tier0_core.md - Frozen Tier 0 facts
- grammar_system.md - B grammar structure
- currier_a.md - A registry properties
- morphology.md - Compositional system
- operations.md - OPS doctrine
- human_track.md - HT layer
- azc_system.md - AZC hybrid system

---

## XVI. CHANGE-SAFETY STATEMENT

> **The constraints file encodes what is known.**
> **This document encodes how to understand it.**
> **Neither replaces the other.**

Together, these two files provide complete model reconstruction capability. All other documentation is convenience, not necessity.

### Document Relationship

| File | Contains | Purpose |
|------|----------|---------|
| CONSTRAINT_TABLE.txt | Atomic findings | What is true |
| MODEL_CONTEXT.md | Architectural integration | How to read it |

### Restart Guarantee

With these two files alone, a future analyst can:
- Reconstruct the complete architecture
- Understand all epistemic tiers
- Know what is closed vs open
- Know what is structural vs speculative
- Avoid resurrecting falsified ideas

Nothing else is logically required.

---

## Navigation

-> [CONSTRAINT_TABLE.txt](CONSTRAINT_TABLE.txt) | ^ [CLAUDE_INDEX.md](CLAUDE_INDEX.md)


---

# All Constraints

CONSTRAINT_REFERENCE v2.6 | 1023 constraints | 2026-02-20
TIER: 0=frozen 1=falsified 2=established 3=speculative 4=exploratory
SCOPE: A=CurrierA B=CurrierB AZC=diagrams HT=HumanTrack GLOBAL=cross-system
LOCATION: ->=individual_file in:=grouped_registry
NUM	CONSTRAINT
C001	A | **INVALIDATED** - depend on C250 |
C074	Dominant convergence to stable states (57.8% STATE-C terminal)
C079	Only STATE-C essential
C084	System targets MONOSTATE (42.2% end in transitional)
C085	10 single-character primitives (s,e,t,d,l,o,h,c,k,r)
C089	Core within core: k, h, e
C090	500+ 4-cycles, 56 3-cycles (topological)
C103	k = ENERGY_MODULATOR
C104	h = PHASE_MANAGER
C105	e = STABILITY_ANCHOR (54.7% recovery paths)
C107	All kernel nodes BOUNDARY_ADJACENT to forbidden
C109	5 failure classes (PHASE_ORDERING dominant 41%)
C110	PHASE_ORDERING 7/17 = 41%
C111	65% asymmetric
C112	59% distant from kernel
C115	0 non-executable tokens
C119	0 translation-eligible zones
C120	PURE_OPERATIONAL verdict
C121	49 instruction equivalence classes (9.8x compression)
C124	100% grammar coverage
C126	0 contradictions across 8 families
C129	Family differences = coverage artifacts
C130	DSL hypothesis rejected (0.19% reference rate)
C131	Role consistency LOW (23.8%)
C132	Language encoding CLOSED
C137	Swap invariance confirmed
C138	Illustrations do not constrain execution
C139	Grammar recovered from text-only
C140	Illustrations are epiphenomenal
C141	Cross-family transplant = ZERO degradation
C144	Families are emergent regularities
C153	Prefix/suffix axes partially independent (MI=0.075)
C154	Extreme local continuity (d=17.5)
C155	Piecewise-sequential geometry
C156	Detected sections match codicology (4.3x quire alignment)
C157	Circulatory reflux uniquely compatible (100%)
C158	Extended runs necessary (12.6% envelope gap)
C159	Section boundaries organizational (F-ratio 0.37)
C160	Variants are discrete alternatives (43%)
C161	Folio Ordering = Risk Gradient
C162	Aggressive programs buffered (88% vs 49% null)
C163	7 domains ruled incompatible
C164	86.7% Perfumery-Aligned Plants
C165	No Program-Morphology Correlation
C166	Uncategorized: zero forbidden seam presence (0/35)
C167	Uncategorized: 80.7% section-exclusive
C168	Uncategorized: single unified layer
C169	Uncategorized: hazard avoidance 4.84 vs 2.5
C170	Uncategorized: morphologically distinct
C171	Only continuous closed-loop process control survives
C172	SUPERSEDED
C173	Linguistic hypothesis EXHAUSTED
C174	Intra-role outcome divergence (CF-1=0.62, CF-2=0.34)
C175	3 process classes survive (reflux, extraction, conditioning)
C176	5 product families survive
C177	Both extraction/conditioning survive; extraction favored
C178	83 folios yield 33 operational metrics
C179	4 stable regimes (K-Means k=4, Silhouette=0.23)
C180	All 6 aggressive folios in REGIME_3
C181	3/4 regimes Pareto-efficient; REGIME_3 dominated
C182	Restart-capable = higher stability
C183	No regime dominates all axes
C184	9 pressure-induced transitions; 3 prohibited
C185	REGIME_3 = Transient Throughput
C186	No pressure-free cycles
C187	CEI manifold formalized
C188	CEI bands: R2 < R1 < R4 < R3
C189	CEI bidirectional; down-CEI easier (1.44x)
C190	LINK-CEI r=-0.7057
C191	CEI Smoothing
C192	Restart at Low-CEI
C193	Navigation WORSE than random (d=-7.33)
C194	PARTIAL codex organization (2/5)
C195	Human-track compensation NOT detected
C196	100% match EXPERT_REFERENCE archetype
C197	Designed for experts, not novices
C198	OPS CLOSED
C199	Both mineral AND botanical survive
C200	6 Product Survivors
C201	Guild-Restricted Ecosystem
C202	Goldsmith/Assayer Workshops Survive
C203	Voynich structurally exceptional
C204	OPS-R RESOLVED by SEL-F (definitional ambiguity, not formal contradiction)
C205	Residue 82% section-exclusive
C206	Sections not compressible to regimes
C207	0/18 micro-cipher tests passed
C208	Residue compatible with non-encoding dynamics
C209	Attentional pacing wins (6/8)
C210	External alignments robust to HT removal
C211	Seasonal ordering underpowered
C212	93% plants peak May-August
C213	Opportunity-loss model supported (64.7% premature hazards)
C214	EXT-4 duration criterion INVALIDATED
C215	BOTANICAL_FAVORED (8/8 tests, ratio 2.37)
C216	Hybrid hazard model (71% batch, 29% apparatus)
C217	0 true HT near hazards
C221	Deliberate skill practice (4/5) - NOT random mark-making
C222	No intentional layout function
C223	Procedural fluency MIXED
C224	A coverage = 13.6% (threshold 70%)
C225	A Transition Validity = 2.1%
C226	A Has 5 Forbidden Violations
C227	A LINK Density = 3.0%
C228	A Density = 0.35x B
C229	A = DISJOINT
C230	A Silhouette = 0.049
C231	A is REGULAR but NOT GRAMMATICAL
C232	A Section-Conditioned but Class-Uniform
C233	A = LINE_ATOMIC
C234	A = POSITION_FREE
C235	8+ mutually exclusive markers
C236	A = FLAT
C237	A = DATABASE_LIKE
C238	Global Schema, Local Instantiation
C239	A/B separation = DESIGNED (0.0% cross)
C240	A = NON_SEQUENTIAL_CATEGORICAL_REGISTRY
C241	daiin A-enriched (1.62x), ol B-enriched (0.24x)
C242	daiin neighborhood flip (content in A, grammar in B)
C243	daiin-ol adjacent: 16 in B, 10 in A
C244	Infrastructure reuse without semantic transfer
C245	MINIMAL vocabulary: exactly 2 tokens (daiin, ol)
C246	4 mandatory criteria for structural primitives
C247	SP-01 (daiin): affects 30.2% A, 16.5% B
C248	SP-02 (ol): affects 7.4% A, 17.7% B
C249	Scan COMPLETE: 11 candidates tested
C250	~~64.1% show repeating blocks~~
C251	Repetition is Intra-Record Only
C252	Repetition Bounded 2-6x
C253	All Blocks Unique
C254	Multiplicity does NOT interact with B; isolated from operational grammar
C255	Blocks 100% Section-Exclusive
C256	Markers at block END 60.3% (vs 44% start); marker is trailing tag (CAS-DEEP)
C257	72.6% of tokens MARKER-EXCLUSIVE; markers define distinct vocabulary domains (CAS-DEEP)
C258	3x Dominance Reflects Human Counting
C259	INVERSE COMPLEXITY: higher repetitions have MORE diverse blocks (CAS-DEEP)
C260	Section vocabulary overlap 9.7%; sections are isolated domains (CAS-DEEP)
C261	Token Order Non-Random
C262	Low Mutation Across Repetitions
C263	Section-specific ceilings: H max=5x, P max=5x, T max=6x (CAS-DEEP-V)
C264	Inverse-complexity is BETWEEN-MARKER effect (Simpson's paradox); within-marker rho<0 for all 8 markers (CAS-DEEP-V)
C265	1,123 unique marker tokens across 8 classes; 85 core tokens (freq>=10); `daiin` dominates DA (51.7%), `ol` dominates OL (32.3%) (CAS-CAT)
C266	Block vs Non-Block Entry Types
C267	Tokens are COMPOSITIONAL (PREFIX+MIDDLE+SUFFIX)
C267.a	**MIDDLE Sub-Component Structure** (218 sub-components reconstruct 97.8% of MIDDLEs; morphology extends to sub-MIDDLE level)
C268	897 observed combinations
C269	7 Universal Suffixes
C270	Some middles are PREFIX-EXCLUSIVE (CT:-h-, DA:-i-, QO:-kch-); internal structure within classifier families (CAS-MORPH)
C271	Compositional structure explains low TTR and bigram reuse
C272	A and B on COMPLETELY DIFFERENT folios
C273	Section specialization NON-UNIFORM: CT is 85.9% Section H vs OK/OL at 53-55%; at least one prefix is specialized to one product line (EXT-8)
C274	Co-occurrence UNIFORM: no prefix pair shows strong association (>1.5x) or avoidance (<0.5x) in compounds; prefixes can combine freely (EXT-8)
C275	Suffix-prefix interaction SIGNIFICANT: different prefixes have different suffix preferences; EXCLUDES prefixes being processing states (EXT-8)
C276	MIDDLE is PREFIX-BOUND
C277	SUFFIX is UNIVERSAL
C278	Three-axis HIERARCHY (PREFIX→MIDDLE→SUFFIX)
C279	STRONG cross-axis dependencies: all three pairwise interactions p < 10⁻³⁰⁰; axes are HIERARCHICALLY RELATED, not independent dimensions (EXT-8)
C280	Section P ANOMALY: suffix -eol is 59.7% Section P (only axis value favoring P); suggests P involves specific output form (EXT-8)
C281	Components SHARED across A and B
C282	Component ENRICHMENT: CT is A-enriched (0.14x), OL/QO are B-enriched (5x/4x); -dy suffix 27x B-enriched, -or 0.45x A-enriched; usage patterns differ dramatically (EXT-8)
C283	Suffixes show CONTEXT PREFERENCE: -or (0.67x), -chy (0.61x), -chor (0.18x) A-enriched; -edy (191x!), -dy (4.6x), -ar (3.2x) B-enriched; -ol, -aiin BALANCED (EXT-9)
C284	CT in B is CONCENTRATED in specific folios (48 folios); when CT appears in B it uses B-suffixes (-edy, -dy); registry materials take operational form in procedures (EXT-9)
C285	161 BALANCED tokens (0.5x-2x ratio) serve as shared vocabulary; DA-family dominates; cross-reference points between A and B (EXT-9)
C286	Modal preference is PREFIX x SUFFIX dependent; CT consistently A-enriched across suffixes, OL consistently B-enriched; not simple suffix-determines-context (EXT-9)
C287	Repetition does NOT encode abstract quantity, proportion, or scale; remains LITERAL ENUMERATION without arithmetic semantics (EXT-9B RETRACTION)
C288	3x dominance (55%) reflects human counting bias and registry ergonomics, NOT proportional tiers; no cross-entry comparison mechanism exists (EXT-9B RETRACTION)
C289	Folio-level uniformity reflects ENUMERATION DEPTH PREFERENCE (scribal convention, category density), NOT batch scale; no reference frame for ratios (EXT-9B RETRACTION)
C290	Same composition with different counts confirms count is INSTANCE MULTIPLICITY, not magnitude; "3x here" is not comparable to "3x there" due to section isolation (EXT-9B RETRACTION)
C291	~20% have optional ARTICULATOR forms
C292	Articulators = ZERO unique identity distinctions
C293	Component essentiality hierarchy: MIDDLE (402 distinctions) > SUFFIX (13) > ARTICULATOR (0); PREFIX provides foundation (1387 base); MIDDLE is primary discriminator (CAS-POST)
C294	Articulator density INVERSELY correlates with prefix count (15% at 0-1 prefix to 4% at 6 prefixes); articulators COMPENSATE for low complexity (CAS-POST)
C295	Sections exhibit DISTINCT configurations: H=dense mixed (87% mixed, 8.2% art), P=balanced (48% exclusive, 5.1% art), T=uniform sparse (81% uniform, 2.57x mean rep) (CAS-POST)
C296	CH appears in nearly all common prefix pairs (CH+DA, CH+QO, CH+SH); functions as UNIVERSAL MIXING ANCHOR (CAS-POST)
C297	-eol is ONLY suffix concentrated in section P (55.9% vs 41.3% H); all other suffixes favor H; P has distinct suffix profile (CAS-POST)
C298	L-compound middle patterns (lch-, lk-, lsh-) function as B-specific grammatical operators; 30-135x more common in B, largely absent from A; grammar-level specialization not covered by shared component inventory (B-MORPH)
C299	Section H vocabulary dominates B procedures (76/83 = 91.6%); Section P rare (7/83 = 8.4%); Section T absent (0/83 = 0%); chi² = 127.54, p < 0.0001; A sections have NON-UNIFORM mapping to B procedure applicability (CAS-XREF)
C300	3,299 tokens (8.7%) unclassified by Currier
C301	AZC is HYBRID (B=69.7%, A=65.4%)
C302	Distinct Line Structure
C303	Elevated LINK Density
C304	27.4% Unique Vocabulary
C305	LABELING Signature
C306	Placement-coding axis established
C307	Placement × Morphology Dependency
C308	Ordered Subscripts
C309	Grammar-Like Placement Transitions
C310	Placement Constrains Repetition
C311	Positional Grammar
C312	Section × Placement Strong
C313	Position constrains LEGALITY not PREDICTION
C314	Global Illegality + Local Exceptions
C315	Placement-Locked Operators
C316	Phase-Locked Binding
C317	Hybrid architecture (topological + positional)
C318	Folio-Specific Profiles
C319	Zodiac Template Reuse
C320	S2 < S1 Ordering
C321	Zodiac Vocabulary Isolated
C322	SEASON-GATED WORKFLOW interpretation
C323	57.8% STATE-C terminal
C324	Section-Dependent Terminals
C325	Completion Gradient
C326	A-reference sharing within clusters: 1.31x enrichment; material conditioning is real but SOFT and OVERLAPPING (silhouette=0.018); NOT a clean taxonomy (SEL-F, Tier 2)
C327	Cluster 3 (f75-f84) is locally anomalous: only contiguous cluster, 70% STATE-C, highest A-ref coherence (0.294); LOCAL observation, not organizational law (SEL-F, Tier 2)
C328	10% corruption = 3.3% entropy increase
C329	Top 10 token removal = 0.8% entropy change
C330	Leave-one-folio-out = max 0.25% change
C331	49-class minimality WEAKENED but confirmed
C332	Kernel Bigram Ordering
C333	Kernel Trigram Dominance
C334	LINK Section Conditioning
C335	69.8% Vocabulary Integration
C336	Hybrid A-Access Pattern
C337	Mixed-Marker Dominance
C338	Marker Independence
C339	E-Class Dominance
C340	LINK-Escalation Complementarity
C341	HT-Program Stratification
C342	HT-LINK Decoupling
C343	A-AZC persistence independence: A-vocabulary tokens appear in 2.2x more AZC placements than AZC-only tokens (p < 0.0001); high-multiplicity A-tokens have 43% broader coverage (p = 0.001); A-registry assets persist independently of AZC legality windows; supports managed stewardship model (AAZ, Tier 2)
C344	HT-A Inverse Coupling
C345	A folios lack thematic coherence
C346	A exhibits SEQUENTIAL COHERENCE
C347	Disjoint Prefix Vocabulary
C348	Phase Synchrony
C349	Extended Cluster Prefixes
C350	HT+B Hybrids Explained
C351	Final Classification
C352	TRUE ORPHAN Residue
C353	State Continuity Better Than Random
C354	HT Orientation Intact
C355	75.9% Known Prefixes at Folio Start
C356	Section Symmetry Preserved
C357	Lines 3.3x more regular than random
C358	Specific boundary tokens identified
C359	LINK Suppressed at Boundaries
C360	Grammar is LINE-INVARIANT
C361	Adjacent B folios share 1.30x more vocabulary
C362	Regime Vocabulary Fingerprints
C363	Vocabulary Independent of Profiles
C364	Hub-Peripheral Structure
C365	~~LINK tokens are SPATIALLY UNIFORM~~ **REFUTED by C805**
C366	LINK marks GRAMMAR STATE TRANSITIONS **REVISED by C804**
C367	Sections are QUIRE-ALIGNED (4.3x)
C368	Regime Clustering in Quires
C369	Quire Vocabulary Continuity
C370	Quire Boundaries = Discontinuities
C371	Prefixes have POSITIONAL GRAMMAR
C372	Kernel dichotomy (100% vs <5%)
C373	LINK affinity patterns
C374	Section Preferences
C375	Suffixes have POSITIONAL GRAMMAR
C376	Suffix Kernel Dichotomy
C377	KERNEL-LIGHT Suffixes LINK-Attracted
C378	Prefix-Suffix Constrained
C379	Vocabulary Varies by Context
C380	Function is INVARIANT
C381	Instruction Concentration
C382	MORPHOLOGY ENCODES CONTROL PHASE
C383	GLOBAL MORPHOLOGICAL TYPE SYSTEM
C384	NO TOKEN-LEVEL OR CONTEXT-FREE A-B LOOKUP
C384.a	CONDITIONAL RECORD-LEVEL CORRESPONDENCE PERMITTED
C385	STRUCTURAL GRADIENT in Currier A
C386	Transition Suppression
C387	QO as Phase-Transition Hub
C388	Self-Transition Enrichment
C389	BIGRAM-DOMINANT local determinism (H=0.41 bits)
C390	No Recurring N-Grams
C391	CONDITIONAL ENTROPY SYMMETRY (H(X|past)=H(X|future); constraint symmetry, not transition symmetry - see C886)
C392	ROLE-LEVEL CAPACITY (97.2% observed)
C393	FLAT TOPOLOGY (diameter=1)
C394	INTENSITY-ROLE DIFFERENTIATION
C395	DUAL CONTROL STRATEGY
C396	AUXILIARY Invariance
C397	qo-prefix = escape route (25-47%)
C398	Post-Source Role Distribution (REVISED)
C399	Safe Precedence Pattern
C400	BOUNDARY HAZARD DEPLETION (5-7x)
C401	Self-Transition Dominance
C402	HIGH_IMPACT Clustering
C403	5 PROGRAM ARCHETYPES (continuum)
C404	HT TERMINAL INDEPENDENCE
C405	HT CAUSAL DECOUPLING (V=0.10)
C406	HT GENERATIVE STRUCTURE (Zipf=0.89)
C407	DA = INFRASTRUCTURE
C408	ch-sh/ok-ot form EQUIVALENCE CLASSES
C409	Sister pairs MUTUALLY EXCLUSIVE but substitutable
C410	Sister choice is SECTION-CONDITIONED
C411	Grammar DELIBERATELY OVER-SPECIFIED (~40% reducible)
C412	ch-preference anticorrelated with qo-escape density
C413	HT prefix phase-class predicted by preceding grammar (V=0.319)
C414	HT STRONG GRAMMAR ASSOCIATION
C415	HT NON-PREDICTIVITY (MAE worsens)
C416	HT DIRECTIONAL ASYMMETRY (V=0.324 vs 0.202)
C417	HT MODULAR ADDITIVE
C418	HT POSITIONAL WITHOUT INFORMATIVENESS
C419	HT POSITIONAL SPECIALIZATION IN A (entry-aligned)
C420	Folio-initial position permits otherwise illegal C+vowel variants (ko-, po-, to-)
C421	Section-boundary adjacency suppression (2.42x)
C422	DA as internal articulation punctuation (75% separation)
C423	PREFIX-BOUND VOCABULARY DOMAINS (80% exclusive MIDDLEs)
C424	Adjacency coherence is clustered, not uniform
C430	**AZC Bifurcation: two folio families**
C431	**Zodiac Family Coherence (refines C319)**
C432	**Ordered Subscript Exclusivity**
C433	**Zodiac Block Grammar (98%+ self-transition)**
C434	**R-Series Strict Forward Ordering**
C435	**S/R Positional Division (boundary/interior)**
C436	**Dual Rigidity: uniform vs varied scaffolds**
C437	AZC Folios Maximally Orthogonal
C438	AZC Practically Complete Basis
C439	Folio-Specific HT Profiles
C440	Uniform B-to-AZC Sourcing
C441	Vocabulary-Activated Constraints
C442	AZC Compatibility Grouping
C443	Positional Escape Gradient
C444	A-Type Position Distribution
C450	HT Quire Clustering
C451	HT System Stratification (A > AZC > B density)
C452	HT Unified Prefix Vocabulary
C453	HT Adjacency Clustering (1.69x enrichment, stronger than C424)
C454	**AZC-B Adjacency Coupling FALSIFIED**
C455	**AZC Simple Cycle Topology FALSIFIED** (cycle_rank=5, CV=0.817)
C456	**AZC Interleaved Spiral Topology** (R-S-R-S alternation)
C457	**HT Boundary Preference in Zodiac AZC** (S=39.7% > R=29.5%, V=0.105)
C458	**Execution Design Clamp vs Recovery Freedom** (CV 0.04-0.11 vs 0.72-0.82)
C459	**HT Anticipatory Compensation**
C460	AZC Entry Orientation Effect
C461	HT density correlates with MIDDLE rarity
C462	Universal MIDDLEs are mode-balanced
C466	PREFIX Encodes Control-Flow Participation
C467	qo-Prefix is Kernel-Adjacent
C468	AZC Legality Inheritance
C469	Categorical Resolution Principle
C470	MIDDLE Restriction Inheritance
C471	PREFIX Encodes AZC Family Affinity
C472	MIDDLE Is Primary Carrier of AZC Folio Specificity
C473	Currier A Entry Defines a Constraint Bundle
C475	MIDDLE ATOMIC INCOMPATIBILITY
C476	COVERAGE OPTIMALITY
C477	**HT Tail Correlation**
C478	TEMPORAL COVERAGE SCHEDULING
C479	**Survivor-Set Discrimination Scaling**
C480	Constrained Execution Variability
C481	**Survivor-Set Uniqueness** (0 collisions in 1575 lines)
C482	**Compound Input Specification**
C483	**Ordinal Repetition Invariance** (magnitude has no downstream effect)
C484	**A Channel Bifurcation**
C485	**Grammar Minimality** (e-operator and h->k suppression are load-bearing)
C486	Bidirectional Constraint Coherence (B behavior constrains A zone inference)
C487	A-Registry Memory Optimization (z=-97 vs random, 0th percentile)
C488	HT Predicts Strategy Viability
C489	HT Zone Diversity Correlation
C490	**Categorical Strategy Exclusion** (20.5% of programs forbid AGGRESSIVE, not gradient but prohibition)
C491	Judgment-Critical Program Axis (OPPORTUNISTIC orthogonal to caution/aggression)
C492	**PREFIX Phase-Exclusive Legality** (ct PREFIX is 0% C/S-zones, 26% P-zone, invariant)
C493	**Brunschwig Grammar Embedding** (balneum marie procedure fits with 0 forbidden violations)
C494	**REGIME_4 Precision Axis** (encodes precision-constrained execution, not intensity)
C495	**SUFFIX–REGIME Compatibility Breadth** (-r universal, -ar/-or restricted; V=0.159)
C496	**Nymph-Adjacent S-Position Prefix Bias (o-prefix 75%)**
C497	**f49v Instructional Apparatus Folio** (26 L-labels alternating 1:1 with example lines, demonstrates morphology limits)
C498	**Registry-Internal Vocabulary Track** (61.8% A-exclusive MIDDLEs: ct-prefix 5.1×, suffix-less 3×, folio-localized; don't propagate to B)
C498.a	**A∩B Shared Vocabulary Bifurcation** (154 AZC-Mediated + 114 B-Native Overlap; pipeline scope narrowed)
C498.b	**RI Singleton Population** (~977 singletons, mean 4.82 chars; functional interpretation WEAKENED - see C498.d)
C498.c	**RI Repeater Population** (~313 repeaters, mean 3.61 chars; functional interpretation WEAKENED - see C498.d)
C498.d	**RI Length-Frequency Correlation**
C499	Bounded Material-Class Recoverability (128 MIDDLEs with P(material_class) vectors; conditional on Brunschwig)
C500	Suffix Posture Temporal Pattern (CLOSURE front-loaded 77% Q1, NAKED late 38% Q4, ratio 5.69×)
C501	**B-Exclusive MIDDLE Stratification** (569 B-exclusive types: L-compounds 49, boundary closers, 80% singletons; elaboration not novelty)
C502	**A-Record Viability Filtering** (Strict interpretation: ~96/480 B tokens legal per A; 13.3% mean B folio coverage; 80% filtered)
C502.a	**Full Morphological Filtering Cascade** (PREFIX+MIDDLE+SUFFIX: 38 tokens legal (0.8%); MIDDLE 5.3%, +PREFIX 64% reduction, +SUFFIX 50% reduction, combined 85% beyond MIDDLE)
C503	**Class-Level Filtering** (MIDDLE-only: 1,203 unique patterns, 6 always-survive classes, 32.3 mean; infrastructure classes vulnerable)
C503.a	**Class Survival Under Full Morphology** (PREFIX+MIDDLE+SUFFIX: 6.8 mean classes (10.8%); 83.7% reduction from MIDDLE-only; ~7 classes = actual instruction budget)
C503.b	**No Universal Classes Under Full Morphology** (C121's 49 classes: 0 universal; Class 9 highest at 56.1%; C503's "6 unfilterable" = 10-56% coverage; MIDDLE-only claim doesn't hold under full filtering)
C503.c	**Kernel Character Coverage**
C504	**MIDDLE Function Bifurcation**
C505	**PP Profile Differentiation by Material Class** ('te' 16.1×, 'ho' 8.6×, 'ke' 5.1× in animal records; A-registry organization only)
C506	**PP Composition Non-Propagation**
C506.a	**Intra-Class Token Configuration**
C506.b	**Intra-Class Behavioral Heterogeneity**
C507	**PP-HT Partial Responsibility Substitution**
C508	**Token-Level Discrimination Primacy**
C508.a	**Class-Level Discrimination Under Full Morphology**
C509	**PP/RI Dimensional Separability** (72 PP sets shared by records with different RI; 229 records (14.5%) share PP; 26 pure-RI, 399 pure-PP; dimensions orthogonal)
C509.a	**RI Morphological Divergence** (RI: 58.5% PREFIX, 3.96-char MIDDLE; PP: 85.4% PREFIX, 1.46-char MIDDLE; RI is MIDDLE-centric, PP is template-balanced)
C509.b	**PREFIX-Class Determinism** (Class P_xxx requires A-PREFIX 'xxx' with 100% necessity; sufficiency 72-100%; 27% mutual exclusion = PREFIX sparsity)
C509.c	**No Universal Instruction Set** (0 classes in ALL records; BARE highest at 96.8%; 50 records lack BARE-compatible MIDDLEs; ~7 classes = ~2.5 PREFIXes + BARE + SUFFIXes)
C509.d	**Independent Morphological Filtering** (PREFIX/MIDDLE/SUFFIX filter independently; 27% class ME = morphological sparsity not class interaction; SUFFIX classes 100% PREFIX-free)
C510	**Positional Sub-Component Grammar**
C511	**Derivational Productivity** (Repeater MIDDLEs seed singletons at 12.67x above chance; 89.8% exceed baseline)
C512	**PP/RI Stylistic Bifurcation**
C512.a	**Positional Asymmetry** (END-class 71.4% PP; START-class 16.1% PP; pattern: RI-START + PP-FREE + PP-END)
C513	**Short Singleton Sampling Variance**
C514	**RI Compositional Bifurcation** (17.4% locally-derived, 82.6% globally-composed; Section P highest local rate 26.1%)
C515	**RI Compositional Mode Correlates with Length**
C515.a	**Compositional Embedding Mechanism** (local derivation is additive - embedding local PP context requires more sub-components)
C516	**RI Multi-Atom Observation** (99.6% multi-atom but trivially expected from lengths; intersection formula PROVISIONAL)
C517	**Superstring Compression (GLOBAL)** (65-77% overlap, 2.2-2.7x compression; hinge letters are 7/8 kernel primitives; global substrate)
C518	**Compatibility Enrichment (GLOBAL)** (5-7x enrichment across all systems; extends C383 global type system)
C519	**Global Compatibility Architecture** (compression + enrichment = embedded compatibility relationships spanning A/B/AZC)
C520	**System-Specific Exploitation Gradient** (RI 6.8x > AZC 7.2x > PP 5.5x > B 5.3x; discrimination intensity varies)
C521	**Kernel Primitive Directional Asymmetry** (one-way valve: e→h=0.00, h→k=0.22, e→k=0.27 suppressed; h→e=7.00x, k→e=4.32x elevated; stabilization is absorbing)
C522	**Construction-Execution Layer Independence**
C523	**Pharma Label Vocabulary Bifurcation**
C524	**Jar Label Morphological Compression** (7.1 vs 6.0 char mean; 5-8 PP atoms per MIDDLE; superstring packing)
C525	**Label Morphological Stratification** (o-prefix 50% vs 20% text; qo-prefix ~0% vs 14%; 61% label-only vocabulary; within-group MIDDLE sharing)
C526	**RI Lexical Layer Hypothesis** (609 unique RI as referential lexicon; 87% localized to 1-2 folios; PREFIX/SUFFIX global grammar vs RI extensions as substance anchors)
C527	**Suffix-Material Class Correlation**
C528	**RI PREFIX Lexical Bifurcation** (334 PREFIX-REQUIRED, 321 PREFIX-FORBIDDEN, 12 optional; 98.2% disjoint; PREFIX attachment lexically determined; section-independent; refines C509.a aggregate rate)
C529	**Gallows Positional Asymmetry**
C530	**Gallows Folio Specialization** (k-default 54%, t-specialized folios cluster; p/f never folio-dominant; 2-5x same-gallows co-occurrence RI↔PP in records)
C531	**Folio Unique Vocabulary Prevalence** (98.8% of B folios have ≥1 unique MIDDLE; only f95r1 lacks unique vocabulary; mean 10.5 unique MIDDLEs per folio)
C532	**Unique MIDDLE B-Exclusivity** (88% of unique B MIDDLEs are B-exclusive, not in A; 12% are PP; unique vocabulary is primarily B-internal grammar, not AZC-modulated)
C533	**Unique MIDDLE Grammatical Slot Consistency** (75% of unique MIDDLE tokens share PREFIX/SUFFIX patterns with classified tokens; adjacent folios' unique MIDDLEs fill similar slots 1.30x vs non-adjacent)
C534	Section-Specific Prefixless MIDDLE Profiles
C535	**B Folio Vocabulary Minimality**
C536	**Material-Class REGIME Invariance**
C537	**Token-Level Material Differentiation**
C538	PP Material-Class Distribution (ANIMAL 15.6%, HERB 28.0%, MIXED 16.6%, NEUTRAL 39.9%; classification conditional on Brunschwig suffix alignment)
C539	**LATE Prefix Morphological Class** (al/ar/or: V+L pattern, 3.78x line-final enrichment, 68-70% suffix-depleted, short MIDDLE preference)
C540	**Kernel Primitives Are Bound Morphemes** (k, e, h never standalone; 0 occurrences each; intervention modifiers only)
C541	**Hazard Class Enumeration** (only 6/49 classes participate in 17 forbidden transitions; 43 classes have 0% hazard involvement)
C542	**Gateway/Terminal Hazard Class Asymmetry** (Class 30 = pure gateway, Class 31 = pure terminal; 100% asymmetry)
C543	**Role Positional Grammar** (FLOW final-biased 0.68, CORE initial-biased 0.45; Class 40 = 69% line-final)
C544	**ENERGY_OPERATOR Interleaving** (qo/ch-sh families alternate with 2.5x enrichment; Class 33 self-repeat 14.6%)
C545	**REGIME Instruction Class Profiles** (REGIME_3 = 1.83x CORE_CONTROL; REGIME_1 = 52% qo-family; each REGIME has signature classes)
C546	**Class 40 Safe Flow Operator** (daly/aly/ary: 4.22 avg distance from hazards, 0% hazard rate, 69% line-final; safe flow alternative)
C547	qo-Chain REGIME_1 Enrichment (1.53x enrichment, 51.4% of chains in REGIME_1; depleted in REGIME_2/3; thermal processing context)
C548	**Manuscript-Level Gateway/Terminal Envelope**
C549	**qo/ch-sh Interleaving Significance**
C550	**Role Transition Grammar** (roles self-chain: FREQ 2.38x, FLOW 2.11x, ENERGY 1.35x; FLOW-FREQ bidirectional affinity 1.54-1.73x; ENERGY avoids other roles 0.71-0.80x; phrasal role structure)
C551	**Grammar Universality and REGIME Specialization** (67% classes universal; CC most universal 0.836; ENERGY REGIME_1 enriched 1.26-1.48x; FLOW REGIME_1 depleted 0.40-0.63x; thermal/flow anticorrelation)
C552	**Section-Specific Role Profiles**
C553	**BIO-REGIME Energy Independence**
C554	**Hazard Class Clustering**
C555	**PHARMA Thermal Operator Substitution** (Class 33 0.20x depleted, Class 34 1.90x enriched in PHARMA; ~10x divergence; section-specific not REGIME-driven; ENERGY operators not interchangeable)
C556	**ENERGY Medial Concentration**
C557	**daiin Line-Initial ENERGY Trigger** (27.7% line-initial rate, 2.2x CC average; 47.1% ENERGY followers; Class 10 singleton; RECIPE 36.3% initial; unique control signal)
C558	**Singleton Class Structure** (only 3 singletons: Class 10/11/12; 2/3 CC classes are singletons; daiin initial-biased 27.7%, ol final-biased 9.5%; complementary control primitives)
C560	**Class 17 ol-Derived Control Operators** (9 tokens all PREFIX:ol + ENERGY-morph; BIO 1.72x enriched; PHARMA 0 occurrences; REGIME_3 1.90x; non-singleton CC is ol-derived)
C561	**Class 9 or->aiin Directional Bigram** (87.5% of chains are or->aiin; zero aiin->aiin; directional grammatical unit; HERBAL 21.7% chain rate; refines C559 "self-chaining")
C562	**FLOW Role Structure** (19 tokens, 4.7% corpus; final-biased 17.5%; Class 40 59.7% final, ary 100% final; PHARMA 1.38x enriched, BIO 0.83x; ENERGY inverse pattern)
C563	**AX Internal Positional Stratification**
C564	**AX Morphological-Positional Correspondence** (AX_INIT: 17.5% articulator; AX_MED: ok/ot 88.8%; AX_FINAL: prefix-light 60.9%, zero articulators; prefix family predicts position)
C565	**AX Execution Scaffold Function** (AX mirrors named role positions; 0% hazard; 1.09x self-chaining; AX_FINAL enriched R1 39.4% BIO 40.9%; structural frame not functional operations)
C566	**UN Token Resolution** (7042 UN = 30.5% of B; 74.1% hapax, 74.8% single-folio; morphologically normal; cosurvival threshold artifact; NOT a separate role)
C567	**AX-Operational MIDDLE Sharing**
C568	**AX Pipeline Ubiquity** (97.2% of A records carry AX vocabulary; 0 zero-AX B contexts; classes 21,22 always survive; AX_FINAL 100%, all subgroups 95.6%)
C569	**AX Proportional Scaling** (AX fraction 0.454 vs expected 0.455; R²=0.83; NOT pure byproduct; AX_INIT over-represented slope 0.130 vs 0.102; AX_FINAL under-represented)
C570	**AX PREFIX Derivability** (89.6% binary accuracy; PREFIX is role selector; 22 AX-exclusive prefixes; F1=0.904; same MIDDLE becomes AX or operational via PREFIX)
C571	**AX Functional Identity Resolution** (AX = PREFIX-determined default mode of pipeline vocabulary; same MIDDLEs serve as scaffold or operations; PREFIX selects role, MIDDLE carries material)
C572	**AX Class Behavioral Collapse**
C573	**EN Definitive Count: 18 Classes** (ICC-based: {8, 31-37, 39, 41-49}; resolves BCSC=11 undercount; 7211 tokens = 31.2% of B; Core 6 = 79.5%, Minor 12 = 20.5%)
C574	**EN Distributional Convergence** (k=2 silhouette 0.180; QO/CHSH identical positions, REGIME, context (JS=0.0024); but MIDDLE Jaccard=0.133, trigger chi2=134; grammatically equivalent, lexically partitioned; C276/C423 within single role)
C575	**EN is 100% Pipeline-Derived** (64 unique MIDDLEs, all PP; 0 RI, 0 B-exclusive; even purer than AX's 98.2% PP; vocabulary entirely inherited from Currier A)
C576	**EN MIDDLE Vocabulary Bifurcation by Prefix**
C577	**EN Interleaving is Content-Driven**
C578	**EN Has 30 Exclusive MIDDLEs** (46.9% of EN vocabulary; not shared with AX, CC, FL, or FQ; dedicated content subvocabulary within pipeline)
C579	**CHSH-First Ordering Bias**
C580	**EN Trigger Profile Differentiation**
C581	**CC Definitive Census** (CC={10,11,12,17}; 1023 tokens, 4.4% of B; Classes 10,11 active, 12 ghost (zero tokens per C540), 17 ol-derived per C560)
C582	**FL Definitive Census** (FL={7,30,38,40}; 1078 tokens, 4.7% of B; 4 classes confirmed vs BCSC=2; hazard pair {7,30} + safe pair {38,40})
C583	**FQ Definitive Census** (FQ={9,13,14,23}; 2890 tokens, 12.5% of B; supersedes C559's {9,20,21,23}; Classes 20,21 are AX per C563)
C584	**Near-Universal Pipeline Purity** (CC/EN/FL/FQ all 100% PP; AX 98.2% per C567; pipeline vocabulary dominates all roles; operational roles pure, scaffold near-pure)
C585	**Cross-Role MIDDLE Sharing**
C586	**FL Hazard-Safe Split**
C587	**FQ Internal Differentiation**
C588	**Suffix Role Selectivity**
C589	**Small Role Genuine Structure**
C590	**CC Positional Dichotomy**
C591	**Five-Role Complete Taxonomy**
C592	**C559 Membership Correction** (C559 used {9,20,21,23} for FQ; correct is {9,13,14,23}; C559 SUPERSEDED; downstream C550/C551/C552/C556 flagged for re-verification with corrected membership)
C593	**FQ 3-Group Structure** ({9} connector, {13,14} prefixed-pair, {23} closer; k=3 silhouette 0.68; PC1=position 64.2%, PC2=morphology 28.2%; BARE=HAZARDOUS, PREFIXED=SAFE perfect overlap)
C594	**FQ 13-14 Complete Vocabulary Bifurcation**
C595	**FQ Internal Transition Grammar**
C596	**FQ-FL Position-Driven Symbiosis**
C597	**FQ Class 23 Boundary Dominance** (29.8% final rate, 39% of FQ finals despite 12.5% token share; 12.2% initial; mean run length 1.19, 84% singletons; boundary specialist)
C598	**Cross-Boundary Sub-Group Structure** (8/10 pairs significant; FQ_CONN->EN_CHSH 1.41x, FQ_CONN->EN_QO 0.16x; sub-group routing visible across role boundaries)
C599	**AX Scaffolding Routing**
C600	**CC Trigger Sub-Group Selectivity**
C601	**Hazard Sub-Group Concentration** (19 events from 3 source sub-groups: FL_HAZ/EN_CHSH/FQ_CONN; EN_CHSH absorbs 58%; QO never participates)
C602	**REGIME-Conditioned Sub-Role Grammar** (4/5 pairs REGIME-dependent; AX->FQ REGIME-independent; core routing invariant, magnitudes shift by REGIME)
C603	**CC Folio-Level Subfamily Prediction**
C604	**C412 REGIME Decomposition**
C605	**Two-Lane Folio-Level Validation**
C606	**CC->EN Line-Level Routing**
C607	**Line-Level Escape Prediction**
C608	**No Lane Coherence / Local Routing**
C609	**LINK Density Reconciliation** (true density 13.2%=3,047/23,096; legacy 6.6% and 38% not reproducible; LINK cuts all 5 ICC roles: AX 26.2%, EN 19.0%, CC 13.8%; 'ol' in MIDDLE 41.2%, PREFIX 28.7%)
C610	**UN Morphological Profile** (7,042 tokens=30.5% B; 2x suffix rate 77.3% vs 38.7%; 5.3x articulator rate; 79.4% PP MIDDLEs, 0% RI; 90.7% novel MIDDLEs contain PP atoms; complexity is mechanism of non-classification)
C611	**UN Role Prediction** (PREFIX assigns 99.2%; consensus 99.9%; EN 37.1%, AX 34.6%, FQ 22.4%, FL 5.9%, CC 0.0%; CC fully resolved; UN is morphological tail of EN/AX/FQ)
C612	**UN Population Structure**
C613	**AX-UN Boundary**
C614	**AX MIDDLE-Level Routing**
C615	**AX-UN Functional Integration** (2,246 AX-predicted UN route identically all subgroups p>0.1; 89.3% classified AX MIDDLEs shared; 312 truly novel MIDDLEs; combined AX = 6,098 = 26.4% of B)
C616	**AX Section/REGIME Conditioning**
C617	**AX-LINK Subgroup Asymmetry**
C618	**Unique MIDDLE Identity** (858 unique MIDDLEs are 100% UN, 99.7% hapax, MIDDLE length 4.55 vs 2.12 shared, 83.1% suffix rate, 88% B-exclusive, 95.7% contain PP atoms; morphological extreme tail of B)
C619	**Unique MIDDLE Behavioral Equivalence**
C620	**Folio Vocabulary Network**
C621	**Vocabulary Removal Impact** (removing 868 unique MIDDLE tokens: 96.2% survival, mean role shift 2.80 pp, max 7.04 pp, 1/82 folios lose ICC role; UN -2.71 pp; vocabulary minimality is type diversity, not functional necessity)
C622	**Hazard Exposure Anatomy** (43 safe classes: 23 role-excluded (20 AX + 3 CC) + 20 sub-group-excluded (16 EN + 2 FL + 2 FQ); 0 incidental; safe classes route to hazard at 24.6%; FL_SAFE line-final mean=0.811 vs hazard FL 0.546 p<0.001)
C623	**Hazard Token Morphological Profile**
C624	**Hazard Boundary Architecture**
C625	**Hazard Circuit Token Mapping**
C626	**Lane-Hazard MIDDLE Discrimination**
C627	**Forbidden Pair Selectivity** (no frequency bias rank 0.562; 0/17 reciprocal-forbidden; circuit topology explains 9/12=75%; FQ_CLOSER boundary tokens account for 3 unexplained; directional token-specific lookup table)
C628	**FQ_CLOSER Positional Segregation Test**
C629	**FQ_CLOSER Source Token Discrimination** (dy c9 restart rate 0% vs s 48.6%; forbidden sources lower hazard rate 28.2% vs 35.5%; higher EN_CHSH rate 13.1% vs 8.6%; JSD 0.219; class 23 contains restart specialists and general distributors)
C630	**FQ_CLOSER Boundary Mechanism** (25% gap resolved: dy→aiin positional, l→chol frequency artifact P(0)=0.85, dy→chey likely genuine E=1.32; s→aiin 20x over-represented dominates restart loop; class 23 not unified mechanism)
C631	**Intra-Class Clustering Census** (effective vocabulary 56 from 49 classes + 7 k=2 splits; 86% uniform; mean JSD 0.639 continuous not clustered; silhouette <0.25 in 34/36 classes; 480 types compress 8.6x)
C632	**Morphological Subtype Prediction**
C633	**Effective Vocabulary Census**
C634	**Recovery Pathway Profiling**
C635	**Escape Strategy Decomposition**
C636	**Recovery-Regime Interaction**
C637	**B MIDDLE Sister Preference**
C638	**Quire Sister Consistency**=0.362 FAIR; but CONFOUNDED with section Cramer's V=0.875; within section H quire NS p=0.665; section KW eta_sq=0.321 3.6x stronger than REGIME eta_sq=0.088)
C639	**Sister Pair Variance Decomposition** (47.1% explained adj_R2=32.3%; 52.9% UNEXPLAINED free choice; shared variance 36.4% dominates; unique: quire 3.8%, lane balance 2.7%, MIDDLE 2.6%, REGIME 1.2%, section 0.4%; clean residuals no autocorrelation)
C640	**PP Role Projection Architecture**
C641	**PP Population Execution Profiles**
C642	**A Record Role & Material Architecture**
C643	**Lane Hysteresis Oscillation**
C644	**QO Transition Stability**
C645	**CHSH Post-Hazard Dominance**
C646	**PP-Lane MIDDLE Discrimination**
C647	**Morphological Lane Signature**
C648	**LINK-Lane Independence**
C649	**EN-Exclusive MIDDLE Deterministic Lane Partition** (22/30 exclusive MIDDLEs 100% lane-specific FDR<0.05; 13 QO-only k/t/p-initial 9 CHSH-only e/o-initial; absolute not probabilistic)
C650	**Section-Driven EN Oscillation Rate**
C651	**Fast Uniform Post-Hazard QO Recovery**
C652	**PP Lane Character Asymmetry**
C653	**AZC Lane Filtering Bias**
C654	**Non-EN PP Lane Independence**
C655	**PP Lane Balance Redundancy**
C656	**PP Co-Occurrence Continuity**
C657	**PP Behavioral Profile Continuity** (93 eligible PP; best sil=0.237 degenerate k=2: 2 vs 91; mean JSD=0.537; lane character ARI=0.010; no discrete behavioral clusters)
C658	**PP Material Gradient** (36.2% entropy reduction as gradient not partition; NMI(pool,material)=0.129; chi2 p=0.002 V=0.392; pool 18 54% MIXED; all cross-axis NMI<0.15)
C659	**PP Axis Independence**
C660	**PREFIX x MIDDLE Selectivity Spectrum**
C661	**PREFIX x MIDDLE Behavioral Interaction** (within-MIDDLE between-PREFIX JSD=0.425 vs between-MIDDLE JSD=0.436; effect ratio=0.975 computed / 0.792 vs C657; PREFIX transforms behavior; ckh JSD=0.710 max)
C662	**PREFIX Role Reclassification** (mean 75% class reduction median 82%; EN PREFIX->EN class 94.1%; AX PREFIX->AX/FQ 70.8%; 50.4% of pairs reduce to <20% of MIDDLE's classes)
C663	**Effective PREFIX x MIDDLE Inventory** (1190 observed, 501 effective pairs, 1.24x expansion; best sil=0.350 k=2 vs C657 0.237; k=3 degenerate; binary EN/non-EN split)
C664	**Role Profile Trajectory**
C665	**LINK Density Trajectory**
C666	**Kernel Contact Trajectory**
C667	**Escape/Hazard Density Trajectory**
C668	**Lane Balance Trajectory**
C669	**Hazard Proximity Trajectory**
C670	**Adjacent-Line Vocabulary Coupling**
C671	**MIDDLE Novelty Shape** (front-loaded; 87.3% FL 0% BL; first-half frac=0.685 vs perm=0.653; vocabulary introduced early, reused late)
C672	**Cross-Line Boundary Grammar**
C673	**CC Trigger Sequential Independence**
C674	**EN Lane Balance Autocorrelation**
C675	**MIDDLE Vocabulary Trajectory** (minimal drift; JSD Q1-Q4=0.081 ratio=1.078; 4/135 MIDDLEs positionally biased after Bonferroni; token identity position-invariant)
C676	**Morphological Parameterization Trajectory**
C677	**Line Complexity Trajectory**
C678	**Line Profile Classification** (continuous; best KMeans sil=0.100 no discrete types; PC1=morphological complexity 12.1%; PC2=monitoring intensity 9.3%; 10 PCs for 68.3%)
C679	**Line Type Sequencing**
C680	**Positional Feature Prediction** (11/27 features position-correlated; 9/27 add beyond REGIME; line_length dR2=0.040 strongest; 16/27 position-independent)
C681	**Sequential Coupling Verdict** (24/27 features lag-1 sig; SEQUENTIALLY_COUPLED but folio-mediated not sequential; top: line_length dR2=0.098 EN dR2=0.091 LINK dR2=0.063; lines = contextually-coupled independently-assessed)
C682	**Survivor Distribution Profile**
C683	**Role Composition Under Filtering**
C684	**Hazard Pruning Under Filtering** (83.9% full elimination of all 17 forbidden transitions; mean 0.21 active; max 5; filtering = natural hazard suppression)
C685	**LINK and Kernel Survival Rates** (97.4% kernel union access h=95.5% k=81.0% e=60.7%; 36.5% lose all LINK tokens; monitoring capacity fragile)
C686	**Role Vulnerability Gradient** (FL most fragile 2.3% at 0-2 PP; FQ most resilient 13.5%; vulnerability ordering FL>EN>AX>CC>FQ; all roles >0% in all PP bins)
C687	**Composition-Filtering Interaction**
C688	**REGIME Filtering Robustness** (REGIME_2 most robust 0.222; REGIME_3 least 0.167; REGIMEs 1/2/4 clustered ~0.21; filtering severity A-record-driven not REGIME-driven)
C689	**Survivor Set Uniqueness**
C690	**Line-Level Legality Distribution**
C691	**Program Coherence Under Filtering** (0-20% operational completeness; work group survives best up to 87%; close group is bottleneck; max gap = entire folio for most records)
C692	**Filtering Failure Mode Distribution** (94.7% MIDDLE miss, 3.6% PREFIX, 1.7% SUFFIX; consistent across all roles 91-97% MIDDLE; MIDDLE = gatekeeper)
C693	**Usability Gradient** (266x dynamic range; best=0.107 Max-classes; 78% pairings unusable >50% empty; single A record does NOT produce usable B program)
C694	**RI Placement Non-Random**
C696	**RI Line-Final Preference**
C698	**Bundle-C424 Size Match** (INFORMATIONAL; bundles and C424 adjacency clusters are distinct constructs; KS p < 0.001)
C700	**Bundle PP Exceeds Random**
C702	**Boundary Vocabulary Discontinuity**
C704	**Folio PP Pool Size** (mean 35.3 MIDDLEs per folio, 7.0x record-level; range 20-88; folio = complete PP specification)
C706	**B Line Viability Under Folio Filtering** (13.7% empty lines vs 78% record-level; 76.3% pairings have <=20% empty)
C708	**Inter-Folio PP Discrimination**
C709	**Section Invariance** (all sections H/P/T 100% viable; P=0.182, T=0.293 higher than H=0.085; no dead zones)
C710	**RI-PP Positional Complementarity** (d=0.12, RI slightly later in lines; effect too small for structural complementarity)
C712	**RI Singleton-Repeater Behavioral Equivalence**
C714	**Line-Final RI Morphological Profile** (143 unique types in 156 final positions; no morphological difference from non-final RI)
C716	**Cross-Folio RI Reuse Independence**
C717	**PP Homogeneity Across Line Types** (PP-pure and RI-bearing lines draw from same PP pool; RI-exclusive PP is sampling artifact, null=9.4 vs obs=8.9, 106% explained; PP-pure alone recovers 90.1% of B class survival)
C719	**RI-PP Functional Independence** (0/6 binding tests pass; shared RI does not predict PP similarity J=0.074 vs 0.065, PP consistency ratio 1.05, adjacent PP ratio 0.99; RI and PP are orthogonal discrimination axes)
C721	**RI Section Sharing Trivial** (76.6% within-section vs 71.5% expected from section sizes; enrichment 1.07x trivially explained by 95/114 folios being Herbal)
C722	**Within-Line Accessibility Arch**
C723	**Role Accessibility Hierarchy**
C724	**Within-Class Suffix Accessibility Gradient**
C725	**Across-Line Accessibility Gradient**
C726	**Role-Position Accessibility Interaction** (aggregate arch decomposes into role-specific trajectories; CC/AX increase toward final, EN/FQ decrease; non-unanimous but morphologically explained by C590/C564 composition effects)
C727	**B Vocabulary Autonomy Rate** (69.3% of B token types have low-or-zero accessibility from A; 34.4% completely B-exclusive; 0% universally legal; B's structural scaffold is autonomously determined)
C728	**PP Co-occurrence Incompatibility Compliance**
C729	**C475 Record-Level Scope** (MIDDLE incompatibility operates perfectly at A record level; 0 violations across 19,576 pair occurrences; 15,518 within-folio avoidance pairs never appear on same line; extends C475 from AZC to A)
C730	**PP PREFIX-MIDDLE Within-Line Coupling**
C731	**PP Adjacent Line Continuity**
C732	**PP Within-Line Selection Uniformity**
C733	**PP Token Variant Line Structure**
C734	**A-B Coverage Architecture** (per-A-folio C502.a coverage of B folios: mean 26.1%, range 2.6-79.3%; A folio identity explains 72.0% of variance, B folio 18.1%; routing architecture, not flat)
C735	**Pool Size Coverage Dominance**
C736	**B Vocabulary Accessibility Partition** (0 B tokens universally legal; 34.4% never legal under any A folio; median accessibility 3 A folios; tripartite: B-exclusive 34.4%, narrow-access 33.9%, broad-access 31.7%)
C737	**A-Folio Cluster Structure**
C738	**Union Coverage Ceiling** (all 114 A folios combined reach ~83-89% B folio coverage, never 95%; 34.4% of B vocabulary permanently B-exclusive; represents B's autonomous grammar)
C739	**Best-Match Specificity**
C740	**HT/UN Population Identity** (HT = UN: 4,421 types, 7,042 occ, zero delta; both defined by exclusion from 479-type grammar)
C741	**HT C475 Minimal Graph Participation** (4.6% of HT MIDDLE types in C475 graph, but 38.5% of occurrences; 95.4% too rare to test)
C742	**HT C475 Line-Level Compliance** (0.69% violation rate vs 0.63% classified baseline; z=+1.74 marginal; compliance by structural sparsity)
C743	**HT Lane Segregation**
C744	**HT Lane Indifference** (same-lane rate 37.7% = expected 37.9%, lift=0.994x; z=-1.66 ns; HT is lane-neutral in placement)
C745	**HT Coverage Metric Sensitivity**
C746	**HT Folio Compensatory Distribution**
C747	**Line-1 HT Enrichment**
C748	**Line-1 Step Function** (pos 1=50.2%, pos 2=31.7%, pos 3-10=27-33%; enrichment confined to single opening line)
C749	**First-Line HT Morphological Distinction**
C750	**Opening-Only HT Asymmetry**
C751	**Coverage Pool-Size Confound**
C752	**No Section-to-Section Routing**
C753	**No Content-Specific A-B Routing** (partial r=-0.038 after size control; no granularity achieves discrimination; reframe as constraint propagation)
C754	**Role-Aware Infrastructure Filtering**
C755	**A Folio Coverage Homogeneity** (real A folios at 0th percentile for discrimination vs random; deliberate coverage optimization)
C756	**Coverage Optimization Confirmed** (11x higher pairwise similarity than random; first 10 folios cover 60% PP; hub MIDDLEs 100% PP)
C757	**AZC Zero Kernel/Link** (0 KERNEL, 0 LINK; ~50% OPERATIONAL, ~50% UN; AZC is outside execution layer)
C758	**P-Text Currier A Identity** (PREFIX cosine 0.97 to A, 0.74 to diagram; 19.5% MIDDLE overlap with same-folio diagram)
C759	**AZC Position-Vocabulary Correlation**
C760	**AZC Folio Vocabulary Specialization** (70% MIDDLEs exclusive to 1 folio; 13 universal MIDDLEs; no family pattern)
C761	**AZC Family B-Coverage Redundancy**
C762	**Cross-System Single-Char Primitive Overlap** (f49v/f76r/f57v share 4 chars d,k,o,r - all C085 primitives; spans PREFIX/MIDDLE/SUFFIX positions)
C763	**f57v R2 Single-Char Ring Anomaly** (100% single chars, 0% morphology; ~27-char repeating pattern with p/f variation; m,n unique terminators; diagram-integrated unlike margin labels)
C764	**f57v R2 Coordinate System** (UNIQUE to f57v across 13 Zodiac folios; p/f at 27-pos apart mark ring halves; R1-R2 1:1 token correspondence; 'x' coord-only char never in R1)
C765	**AZC Kernel Access Bottleneck** (AZC-mediated: 31.3% escape, 51.3% kernel; B-native: 21.5% escape, 77.8% kernel; AZC constrains B by limiting kernel access, not escape directly)
C766	**UN = Derived Identification Vocabulary** (UN 81.1% compound vs classified 35.2%; +45.9pp; 1,251 UN-only MIDDLEs at 84.3% compound; 0 classified-only MIDDLEs)
C767	**Class Compound Bimodality** (21 base-only classes at 0-5% compound, 3 compound-heavy classes at 85%+; grammar has two functional vocabularies)
C768	**Role-Compound Correlation** (FL=0% compound, FQ=46.7%; 46.7pp spread; FL uses 0 kernel chars k/h/e; role determines vocabulary type)
C769	**Compound Context Prediction**
C770	**FL Kernel Exclusion** (FL uses 0 kernel chars k/h/e; only role with complete kernel exclusion; 17 MIDDLEs, 1,078 tokens)
C771	**FL Character Restriction** (FL uses exactly 9 chars: a,d,i,l,m,n,o,r,y; excludes c,e,h,k,s,t; mean MIDDLE length 1.58)
C772	**FL Primitive Substrate** (FL provides substrate layer; other roles add kernel k/h/e then helpers c/s/t; EN 60.7% kernel-containing highest)
C773	**FL Hazard-Safe Position Split** (Hazard FL 88.7% at mean pos 0.546 medial; Safe FL 11.3% at mean pos 0.811 line-final; 0.265 position gap)
C774	**FL Outside Forbidden Topology** (FL classes not in any of 17 forbidden pairs; FL operates below hazard layer)
C775	**Hazard FL Escape Driver** (Hazard FL 7/30 drive 98% of FL->FQ; safe FL 38/40 drive 2%; FL->FQ rate 22.5%)
C776	**Post-FL Kernel Enrichment** (59.4% of post-FL tokens have kernel chars k/h/e; confirms FL -> kernel-modulated flow pattern)
C777	**FL State Index** (FL MIDDLEs index material state; 'i'-forms at start (0.30), 'y'-forms at end (0.94); position range 0.64; 77% state change rate)
C778	**EN Kernel Profile** (EN 91.9% kernel; dominant h+e (35.8%); h=59.4%, e=58.3%, k=38.6%; phase/stability operator not energy)
C779	**EN-FL State Coupling** (EN 'h' rate drops 95%->77% as FL advances early->late; early states need phase management, late states stable)
C780	**Role Kernel Taxonomy**
C781	**FQ Phase Bypass** (FQ has exactly 0% 'h'; escape routes bypass phase management using k+e only)
C782	**CC Kernel Paradox** (Classes 10,11=0% kernel, class 17=88%; CC bifurcates into hazard sources vs hazard buffers)
C783	**Forbidden Pair Asymmetry** (All 17 forbidden pairs are asymmetric/directional; 0 symmetric; hazard is directed graph)
C784	**FL/AX Hazard Immunity** (FL and AX never appear in any forbidden pair; exempt from hazard topology)
C785	**FQ Medial Targeting** (FQ->FL routes to MEDIAL at 77.2%; escape re-injects at mid-process, not start/end)
C786	**FL Forward Bias** (FL state transitions: 27% forward, 68% same, 5% backward; 5:1 forward:backward ratio)
C787	**FL State Reset Prohibition** (LATE->EARLY transition = 0 occurrences; full state reset is forbidden)
C788	**CC Singleton Identity** (Class 10=daiin, Class 11=ol, Class 12=k(absent), Class 17=9 ol- tokens; CC classes are specific tokens not broad categories)
C789	**Forbidden Pair Permeability** (34% of CC->FQ transitions violate forbidden pairs; forbidden = disfavored, not prohibited)
C790	**CC Positional Gradient**
C791	**CC-EN Dominant Flow** (CC->EN at 33% vs CC->FQ at 12%; CC primarily routes to kernel ops, not escape)
C792	**B-Exclusive = HT Identity** (100% of B-exclusive vocabulary is HT/UN; 0 classified tokens are B-exclusive; all 88 classified MIDDLEs are in PP; C736's "autonomous grammar" is HT layer, not classified)
C793	**Residual Specificity = Vocabulary Coincidence** (the 24 residual-best A folios are those with best sample of common PP MIDDLEs; f42r dominates via 8 near-universal MIDDLEs; no content routing)
C794	**Line-1 Composite Header Structure** (68.3% PP for A-context declaration, 31.7% B-exclusive for folio ID; PP predicts A at 15.8x random; B-exclusive 94.1% folio-unique)
C795	**Line-1 A-Context Prediction** (PP line-1 HT predicts best-match A folio: 13.9% correct vs 0.88% random baseline, lift=15.8x)
C796	**HT-Escape Correlation**
C797	**AZC-HT Inverse Relationship**
C798	**HT Dual Control Architecture** (AZC and FL are orthogonal predictors of HT; effects additive; quadrant range 25%-37% HT)
C799	**Line-1 AZC Independence** (Line-1 PP fraction and A-context prediction accuracy do NOT vary by AZC tertile; header is fixed structure)
C800	**Body HT Escape Driver**
C801	**Body HT Primitive Vocabulary**
C802	**Body HT LINK Proximity**
C803	**Body HT Boundary Enrichment** (HT rate: first=45.8%, last=42.9%, middle=25.7%; marks control block boundaries)
C804	**LINK Transition Grammar Revision**
C805	**LINK Positional Bias (C365 Refutation)** (Mean pos 0.476 vs 0.504; first=17.2%, last=15.3%, middle=12.4%; shares HT boundary pattern)
C806	**LINK-HT Positive Association**
C807	**LINK-FL Inverse Relationship**
C808	**LINK 'ol' is PP MIDDLE** ('ol' appears 759x as MIDDLE, in A vocabulary; LINK PP rate 92.4%)
C809	**LINK-Kernel Separation**
C810	**LINK-FL Non-Adjacency** (Direct LINK->FL rare: 0.70x expected; confirms complementary phases)
C811	**FL Chaining** (FL->FL enriched 2.11x; extended escape sequences; FL->KERNEL neutral 0.86x)
C812	**HT Novel MIDDLE Combinations** (11.19% novel pairs; NOT C475 violation; HT in distinct combinatorial space)
C813	**Canonical Phase Ordering** (LINK 0.476 -> KERNEL 0.482 -> FL 0.576; monitoring early, escape late)
C814	**Kernel-Escape Inverse**
C815	**Phase Position Significance**
C816	**CC Positional Ordering** (daiin 0.413 -> LINK 0.476 -> KERNEL -> ol 0.511 -> FL 0.576; daiin initiates loop)
C817	**CC Lane Routing** (C600 confirmed: daiin->CHSH 90.8%, ol_derived->QO 57.4%; rapid decay by +2)
C818	**CC Kernel Bridge** (Class 17 = CC-KERNEL interface; 88% kernel chars; resolves C782 paradox)
C819	**CC Boundary Asymmetry** (daiin initial 27.1%; ol/ol_derived medial 85%; unlike LINK 1.23x)
C820	**CC Hazard Immunity** (0/700 forbidden; EN absorbs 99.8% hazard; CC is safe control layer)
C821	**Line Syntax REGIME Invariance** (All 5 roles invariant; eta^2=0.13%; confirms C124 universality)
C822	**CC Position REGIME Invariance**
C823	**Bigram REGIME Partial Variation**
C824	**A-Record Filtering Mechanism** (81.3% filtering confirms C502; aggregation helps usability)
C825	**Continuous Not Discrete Routing** (silhouette=0.124; no discrete clusters; 97.6% unique profiles)
C826	**Token Filtering Model Validation**
C827	**Paragraph Operational Unit** (gallows-initial paragraphs: 31.8% survival, 2.8x better than lines)
C828	**PP Repetition Exclusivity**
C829	**daiin Repetition Dominance** (22% of all repeats; CC trigger may encode control-loop cycle count)
C830	**Repetition Position Bias** (late-biased 0.675; FINAL 12x higher than INITIAL; parameters follow identity)
C831	**RI Three-Tier Population Structure** (singletons 95.3%, position-locked ~4%, linkers 0.6%)
C832	**Initial/Final RI Vocabulary Separation**
C833	**RI First-Line Concentration** (1.85x in paragraph first line; 1.03x at folio level - no structure)
C834	**Paragraph Granularity Validation** (RI structure visible ONLY at paragraph level; validates record size)
C835	**RI Linker Mechanism** (4 tokens, 12 links, 12 folios; 66.7% forward flow; f93v=5 inputs collector)
C838	**qo-Linker Exception** (qokoiiin doesn't follow ct-ho; may be different linkage mechanism)
C839	**RI Input-Output Morphological Asymmetry** (12+ INPUT markers vs 5 OUTPUT markers; -ry strongest OUTPUT)
C840	**B Paragraph Mini-Program Structure**
C841	**B Paragraph Gallows-Initial Markers**
C842	**B Paragraph HT Step Function** (pos 1=45.2%, pos 2=26.5%, pos 3-5+=26-27%; -18.7pp drop at line 2; body flat)
C843	**B Paragraph Prefix Markers** (pch- 16.9% + po- 16.6% = 33.5% of initiators; 78-86% HT; paragraph identification vocabulary)
C844	**Folio Line 1 Double-Header** (50.2% HT = folio header + paragraph 1 header overlap; mid-folio paragraphs 43.6% HT)
C845	**B Paragraph Self-Containment** (no inter-paragraph linking; 7.1% both-position rate vs A's 0.6%; no ct-ho signature; symmetric topology)
C846	**A-B Paragraph Pool Relationship**
C847	**A Paragraph Size Distribution**
C848	**A Paragraph RI Position Variance**
C849	**A Paragraph Section Profile**
C850	**A Paragraph Cluster Taxonomy** (5 clusters: short-RI 34%, long-linker 8%, standard 58%; silhouette=0.337)
C851	**B Paragraph HT Variance Validation** (delta +0.134; 76.8% positive; line 1 = 46.5% HT; validates C840)
C852	**B Paragraph Section-Role Interaction**
C853	**B Paragraph Cluster Taxonomy** (5 clusters: single-line 9%, long-EN 10%, standard 81%; silhouette=0.237)
C854	**A-B Paragraph Structural Parallel**
C855	Folio role template (role cohesion 0.831)
C856	Vocabulary distribution (Gini 0.279, distributed)
C857	First paragraph ordinariness (predicts 11.8%)
C858	Paragraph count reflects complexity (rho 0.836)
C859	Vocabulary convergence (14%→39% overlap)
C860	Section paragraph organization (HERBAL 2.2 vs RECIPE 10.2)
C861	LINK/hazard paragraph neutrality (CV < 0.21)
C862	Role template verdict: hybrid model
C863	Paragraph-ordinal EN subfamily gradient (qo-early, ch-late)
C864	Gallows paragraph marker (81.5% gallows-initial)
C865	Gallows folio position (k/f front-biased, p/t distributed)
C866	Gallows morphological patterns (k uses e, f often bare)
C867	P-T transition dynamics (p stable 54%, t returns to p 50%)
C868	Gallows-QO/CHSH independence (0.3% variance explained)
C869	Gallows functional model (f/k openers, p/t modes)
C870	Line-1 HT folio specificity (86% singletons, 1229 Line-1-only)
C871	HT role cooccurrence pattern (enriched FL, depleted CC/FQ)
C872	HT discrimination vocabulary interpretation
C873	Kernel positional ordering: e (0.404) < h (0.410) < k (0.443)
C874	CC token functions: daiin=init (0.370), ol=continue (0.461)
C875	Escape trigger grammar: 80.4% from hazard FL stages
C876	LINK checkpoint function (position 0.405, routes to EN)
C877	Role transition grammar: EN->EN 38.5%, CC->EN 37.7%, FQ->EN 29.5%
C878	Section program variation: BIO high EN, HERBAL_B high FL/FQ
C879	Process domain: batch processing, 59.2% forward bias
C880	Integrated control model: batch processing with escape handling
C881	A Record Paragraph Structure (paragraphs not lines; RI in first line 3.84x baseline)
C882	PRECISION Kernel Signature (ESCAPE+AUX shows k+e 3x baseline, suppressed h)
C883	Handling-Type Distribution Alignment (66% CAREFUL matches 60% Brunschwig degree-2)
C884	PRECISION-Animal Correspondence (6 paragraphs pass kernel validation as animal candidates)
C885	A-B Vocabulary Correspondence (A folios provide 81% coverage for B paragraphs; single A paragraphs insufficient at 58%)
C886	Transition Probability Directionality (P(A→B) uncorrelated with P(B→A), r=-0.055; symmetric constraints but directional execution)
C887	WITHOUT-RI Backward Reference (1.23x backward/forward asymmetry; highest overlap 0.228 when following WITH-RI)
C888	Section-Specific WITHOUT-RI Function (H: ct 3.87x cross-ref; P: qo/ok/ol safety protocols)
C889	ct-ho Reserved PP Vocabulary (MIDDLEs h/hy/ho 98-100% ct-prefixed; extends C837 to PP level)
C890	Recovery Rate-Pathway Independence (FQ rate and post-FQ kernel vary independently; extends C458)
C891	ENERGY-FREQUENT Inverse Correlation
C892	Post-FQ h-Dominance (h 24-36% post-FQ vs e 3-8%; recovery enters via phase-check)
C893	Paragraph Kernel Signature Predicts Operation Type
C894	REGIME_4 Recovery Specialization Concentration
C895	Kernel-Recovery Correlation Asymmetry (k-FQ: r=+0.27; h-FQ: r=-0.29; e-FQ: n.s.; phase monitoring substitutes for recovery)
C896	Process Mode Discrimination via Kernel Profile (HIGH_K_LOW_H=2.5x FQ; discriminates distillation from boiling/decoction)
C897	Prefixed FL MIDDLEs as Line-Final State Markers (tokens contain FL TERMINAL MIDDLEs am/y/dy/ly per C777; 72.7% line-final; operation→state mapping extends FL state index)
C898	A PP Internal Structure
C899	A-B Within-Line Positional Correspondence
C900	**AZC P-Text Annotation Pages** (f65v/f66v are 100% P-text, linguistically A (0.941 cosine), flanking f66r zodiac; 60%+ vocabulary overlap confirms annotation role)
C901	**Extended e Stability Gradient** (e→ee→eee→eeee forms stability depth continuum; quadruple-e in 11 folios concentrated late Currier A; odeeeey = maximum observed)
C902	**Late Currier A Register** (f100-f102 show distinct characteristics: p/f-domain concentration, extended vowels, short lines, MONSTERS; suggests appendix/addendum content)
C903	**Prefix Rarity Gradient** (Common ch/sh/qo vs rare ct vs very-rare qk (9 folios) vs extremely-rare qy (3 folios); rarity correlates with specialization)
C904	**-ry Suffix S-Zone Enrichment (3.18x; cross-validates C839 OUTPUT marker)**
C905	**FL_TERMINAL Early-Line Concentration**
C906	**Vowel Primitive Suffix Saturation** (Vowel MIDDLEs a/e/o + END-class suffix = closed compound that suppresses further suffixation; e→98.3% suffix, edy→0.4% suffix; explains 38% of unmapped tokens)
C907	**-hy Consonant Cluster Infrastructure** (Tokens with -hy suffix form formulaic class: ch/sh prefix + consonant cluster MIDDLE + hy; 910 tokens (3.9%); connector hypothesis FALSIFIED - 0.99x boundary enrichment)
C908	**MIDDLE-Kernel Correlation** (55% of MIDDLEs significantly correlate with kernel profile; k-MIDDLEs→HIGH_K, e-MIDDLEs→HIGH_E, ch/sh→HIGH_H)
C909	**Section-Specific MIDDLE Vocabularies** (96% of MIDDLEs section-specific; B=k-energy, H=k+h mixed, S=e-stability, T=h-monitoring, C=infrastructure)
C910	**REGIME-MIDDLE Clustering** (67% REGIME-specific; REGIME_4 precision shows extreme enrichment: m=7.24x, ek=3.79x, y=2.57x)
C911	**PREFIX-MIDDLE Compatibility Constraints** (PREFIX selects MIDDLE family; qo→k-family 4.6x, da→infra 12.8x, ch/sh→e-family 2-3x; 102 forbidden combinations)
C912	**Precision Vocabulary - dam Token** (m MIDDLE 7.24x in REGIME_4; appears as `dam` 55% of cases; da- anchor prefix + no suffix; precision anchoring marker)
C913	**RI Derivational Morphology** (90.9% of RI MIDDLEs contain PP as substring; extensions 71.6% single-char; 53% suffix, 47% prefix; position preferences: 'd' 89% suffix, 'h' 79% prefix, 'q' 100% prefix)
C914	**RI Label Enrichment** (RI 3.7x enriched in labels (27.3%) vs text (7.4%); labels identify specific illustrated items requiring instance-specific vocabulary from PP+extension system)
C915	**Section P Pure-RI Entries** (83% of pure-RI first-line paragraphs in Section P; 23/24 single-line; mean para 7.7; da/ot/sa prefixes NOT ct-; distinct from linker system)
C916	**RI Instance Identification System** (RI functions as instance identification via PP+extension derivation; PP=category, RI=specific instance; explains A as index bridging B procedures to specific applications; labels 3.7x RI-enriched for illustration identification)
C917	**Extension-Prefix Operational Alignment**
C918	**Currier A as Operational Configuration Layer** (A provides context-specific material variants via RI=PP+extension; extensions encode operational context: h=monitoring, k=energy, t=terminal, d=transition; A parameterizes B's generic procedures)
C919	**d-Extension Suffix Exclusion** (d-extension categorically excludes -y suffix family: 0% rate vs 46-83% for all other extensions; takes -iin/-al instead; indicates END-class grammatical behavior)
C920	**f57v R2 Extension Vocabulary Overlap** (92% of R2 chars are extension characters; only 'x' non-extension per C764; 'h' categorically absent)
C921	**f57v R2 Twelve-Character Period** (exact 12-char period with 4 cycles + 2-char terminal; 10/12 positions invariant; only positions 7-8 variable: k/m and f/p)
C922	**Single-Character AZC Ring h-Exclusion**
C923	**Label Extension Bifurcation (r/h Axis)**
C924	**HT-RI Shared Derivational Morphology** (HT MIDDLEs 97.9% contain PP; 15/16 extension chars overlap with RI; same derivational system, different PREFIX layer; HT_PREFIX + [PP+ext] vs A/B_PREFIX + [PP+ext])
C925	**B Vocabulary Morphological Partition** (B-exclusive 66% has kernel density ~1.0; RI bases 20% have density 0.76; A's RI derivation draws selectively from lower-density subset; morphological not semantic partition per C522)
C926	**HT-RI Line-Level Anti-Correlation**
C927	**HT Elevation in Label Contexts**
C928	**Jar Label AX_FINAL Concentration**
C929	**ch/sh Sensory Modality Discrimination** (ch=active test pos 0.515, sh=passive monitor pos 0.396, delta +0.120; ch+checkpoint suffix 1.87x; sh followed by heat 18.3% vs ch 10.6%; ch followed by input 1.98x, iterate 2.01x; maps to Brunschwig continuous monitoring vs discrete sampling)
C930	**lk Section-S Concentration and Fire-Method Specificity**
C931	**Prefix Positional Phase Mapping** (pch 15.9x, tch 18.4x line-initial; ol 0.33x, lch 0.32x, ot 0.29x line-final; pch 25.5x par-initial; qo/ch 0.03-0.13x par-initial; temporal ordering PREP->PRE-TREAT->SEAL->EXECUTE->POST->STORE matches Brunschwig 7-phase workflow)
C932	**Body Vocabulary Gradient** (RARE r=-0.97 early-to-late; UNIVERSAL r=+0.92; tokens/line 10.3->8.7 r=-0.97; terminal suffix r=-0.89; bare suffix r=+0.90; extends C842 flat-body finding to show vocabulary rarity gradient within body)
C933	**Prep Verb Early Concentration** (te avg=0.394 Q0:Q4=2.7x; pch avg=0.429 Q0:Q4=2.8x; tch avg=0.424 Q0:Q4=1.9x; lch avg=0.445 Q0:Q4=1.3x; all four Brunschwig prep verbs front-load in paragraph body)
C934	**Parallel Startup Pattern** (heat first 65%, prep first 27%, same line 8%; first heat avg pos=0.079, first prep avg pos=0.212; BOTH lines Q0=9.9% Q4=3.4% r=-0.94; consistent with "light coals first, prep materials while stabilizing")
C935	**Compound Specification Dual Purpose** (line-1 compound atoms predict body simple MIDDLEs: 71.6% hit vs 59.2% random, 1.21x lift; HT compound rate 45.8% vs grammar 31.5%; 100% decomposable to core atoms; REVISES C404 "non-operational" to "operationally redundant"; weakens Tier 3 attention/practice interpretation)
C937	**Rare MIDDLE Zone-Exclusivity**
C938	**Section-Specific Tail Vocabulary**
C939	**Zone-Exclusive MIDDLEs Are Compositional Variants**
C940	**FL State Marking via Rare MIDDLEs FALSIFIED**
C941	**Section Is the Primary Vocabulary Organizer**
C942	**Context-Dependent MIDDLE Successor Profiles** (45.8% significant by section after Bonferroni; section KL 2.0x > position KL; 100% MIDDLEs have section KL > position KL)
C943	**Whole-Token Variant Coordination Carries Section Signal**
C944	**Paragraph Kernel Sequence Stereotypy**
C945	**No Folio-Persistent Rare MIDDLEs as Material Markers FALSIFIED** (0 rare MIDDLEs at >80% persistence; 81.8% confined to single paragraph; mean edit distance 1.33)
C946	**A Folios Show No Material-Domain Routing FALSIFIED** (cosine similarity 0.997; ARI=-0.007; RI extension V=0.071; A is generic pool)
C947	**No Specification Vocabulary Gradient FALSIFIED**
C948	**Gloss Gap Paragraph-Start Enrichment** (4.03x at par_start; section H gap rate 8.6% vs B 2.4%; 16 distinct gaps all hapax)
C949	**FL Non-Executive Verdict** (6-test battery; variant NMI 97.1th pctile but fails 99.9th threshold; FL is deliberately low-impact ordered annotation layer, non-executive)
C950	**FL Two-Dimensional Structure**
C951	**FL-LINK Spatial Independence**
C952	**FL Stage-Suffix Global Independence**
C953	**ch-FL Precision Annotation Submode**
C954	**Section T FL Enrichment**
C955	**FL Killed Hypotheses Registry** (12 hypotheses falsified: active control, loops, routing, batch processing, cross-line state, testing criteria, assessment output)
C956	**Positional Token Exclusivity** (192/334 tokens zone-exclusive, 2.72x shuffle; 50% survive suffix-stripping; effect is STRUCTURAL per negative control)
C957	**Token-Level Bigram Constraints** (26 mandatory, 9 forbidden; 2 genuinely token-specific: chey->chedy, chey->shedy both ENERGY; effect is STRUCTURAL)
C958	**Opener Class Determines Line Length** (24.9% partial R^2 beyond folio+regime; folio+opener_token = 93.7% R^2; strongest token-level finding)
C959	**Opener Is Role Marker, Not Instruction Header** (role accuracy 29.2% = 1.46x chance; token JSD not significant; free substitution within role)
C960	**Boundary Vocabulary Is Open** (Gini 0.47 < 0.60; 663 tokens for 80% coverage; no closed boundary set)
C961	**WORK Zone Is Unordered** (EN tau ~ 0, AX tau ~ 0; no systematic within-zone sequence; interior operations are parallel)
C962	**Phase Interleaving Pattern**
C963	**Paragraph Body Homogeneity**
C964	**Boundary-Constrained Free-Interior Grammar** (SYNTHESIS: grammar strength 0.500; boundaries constrained by role, interior free; system is role-complete)
C965	**Body Kernel Composition Shift** (h-kernel fraction rises +0.10, e-kernel drops -0.086 through body; survives length control; composition shift not diversity collapse)
C966	**EN Lane Oscillation First-Order Sufficiency** (markov_haz BIC=9166.3, 12 params; composite deviation 0.975 on 8 valid metrics; 2nd-order correction worsens fidelity; no hidden accumulator, no cross-line memory)
C967	**Hazard Gate Duration Exactly One Token**
C968	**Folio Drift Emergent Not Intrinsic**
C969	**2nd-Order Alternation Bias Non-Load-Bearing** (CMI=0.012 bits; post-SWITCH epsilon=+0.062, post-STAY delta=-0.067; statistically significant but correction worsens composite deviation 1.427->1.495; asymmetric between lanes; soft stabilization bias)
C970	**CC-Hazard Gate Priority**
C971	**Transition Asymmetry Structurally Rare**
C972	**Cross-Line Independence Stronger Than Random Markov**
C973	**Compositional Sparsity Exceeds Low-Dimensional Models**
C974	**Suffix-Role Binding Structural Not Random**
C975	**Fingerprint Joint Uniqueness UNCOMMON**
C976	**Transition Topology Compresses to 6 States** (49 classes → 6 states, 8.2x compression; preserves role integrity + depletion asymmetry; holdout-invariant 100/100 trials, ARI=0.939; generative fidelity 4/5 metrics)
C977	**EN/AX Transitionally Indistinguishable at Topology Level** (38 EN/AX classes merge freely; split into S3-minor 6 classes and S4-major 32 classes by depletion constraint; AXm→AXM flow 24.4x stronger than reverse)
C978	**Hub-and-Spoke Topology with Sub-2-Token Mixing** (S4/AXM universal attractor >56% from all states; spectral gap 0.894; mixing time 1.1 tokens; hazard/safe asymmetry 6.5x from operational mass)
C979	**REGIME Modulates Transition Weights Not Topology**
C980	**Free Variation Envelope: 48 Eigenvalues, 6 Necessary States** (effective rank 48 at >0.01 threshold; constraint compression to 6 states; gap = parametric control space; S4 has 81 MIDDLEs, Gini=0.545, within-state JSD=0.365)
C981	**MIDDLE Discrimination Space Is a Structural Fingerprint** (972 MIDDLEs; 4/5 metrics anomalous under Configuration Model z=+17 to +137; CV < 0.055 at 20% removal; λ₁ degrades linearly; FINGERPRINT_CONFIRMED)
C982	**Discrimination Space Dimensionality ~101**
C983	**Compatibility Is Strongly Transitive** (clustering 0.873 vs CM 0.253, z=+136.9; single most anomalous property; implies AND-style constraint intersection in structured feature space)
C984	**Independent Binary Features Insufficient** (AND-model matches density/λ₁/eigencount/rank but clustering ceiling 0.49 vs target 0.87 at all K∈[20,200]; features must be correlated/hierarchical/block-structured)
C985	**Character-Level Features Insufficient for Discrimination**
C986	**Hub Eigenmode Is Frequency Gradient** (λ₁=82.0, 4.3× next eigenvalue; hub-frequency Spearman ρ=-0.792, p≈0; hub loading monotonic with frequency band; hub axis = coverage axis C476/C755)
C987	**Discrimination Manifold Is Continuous** (residual space: best k=5, silhouette 0.245 MIXED_BANDS, 865/972 in one cluster; gap statistic -0.014; negative silhouette at k≥12; continuous curved manifold, not blocks)
C988	**AZC Folio Cohesion Is Hub-Driven** (full embedding: 27/27 coherent z=+13.26; residual: 0/27 coherent z=-2.68; folios sample frequency-coherent slices with diverse residual positions; zone C→R→S traces hub gradient)
C989	**B Execution Inhabits A's Discrimination Geometry** (80.2% token-weighted A-compatible at 37× enrichment; residual cosine: compat +0.076, incompat -0.051; violations concentrate in rare MIDDLEs; section S isolated; geometric realization of C468)
C990	**B Operates at Elevated Constraint Tension**
C991	**Radial Depth Dominates Line-Level Energy**
C992	**e-Kernel Is the Compatibility Kernel**
C993	**REGIME_4 Uniquely Converges in Energy**
C994	**B-Exclusive MIDDLEs Are Geometrically Subordinate**
C995	**Affordance Bin Behavioral Coherence**
C996	**Forbidden Topology at HUB-STABILITY Interface** (13/17 forbidden transitions involve HUB_UNIVERSAL; 5/17 involve STABILITY_CRITICAL; no other bin participates; 8/17 are HUB→HUB self-transitions; hazard zone = compatibility carrier meets stability commitment)
C997	**Sparse Safety Buffer Architecture** (22/18085 interior tokens are safety-necessary; 0.12% buffer rate; 68% in HUB_UNIVERSAL; dominant pair chey→chedy buffered 9x; safety mechanism is QO lane-crossing in CHSH sequences; removing Bin 8 or Bin 0 induces forbidden pairs; grammar = sparse-critical-buffer regime)
C998	**Analog Physics Does Not Force Voynich Grammar Topology** (minimal reflux simulation median 3/10 targets; null models score equally; spectral gap 1% hit rate, forbidden pairs 4%, post-overshoot cooling 2%; continuous thermal dynamics cannot produce 6-state hub-spoke topology; grammar requires discrete encoding layer beyond analog physics)
C999	**Categorical Discretization Does Not Bridge Voynich Topology Gap** (5 physical strategies + 1 random null across 100 parameterizations; best physical 3/9 metrics toward Voynich = random 3/9; zero forbidden transitions from any strategy; hub mass degrades under all strategies; spectral gap is discretization artifact; Voynich discreteness is engineered abstraction, not categorization artifact)
C1000	**HUB_UNIVERSAL Decomposes Into Functional Sub-Roles** (23 HUB MIDDLEs → 4 sub-roles: HAZARD_SOURCE(6), HAZARD_TARGET(6), SAFETY_BUFFER(3), PURE_CONNECTOR(8); behaviorally homogeneous but functionally distinct; 17/17 forbidden transitions involve HUB; PREFIX lane chi²=12957 V=0.689; safety buffers 3.8x qo-enriched; regime clustering sil=0.398 at k=4; corrects C996 from 13/17 to 17/17)
C1001	**PREFIX Dual Encoding — Content and Positional Grammar** (PREFIX encodes both content (lane, class, suffix) and line position; PREFIX R²=0.069 ≈ MIDDLE R²=0.062 for position; 20/32 PREFIXes non-uniform positional profiles; po=86% initial, ar=61% final; PREFIX positional grammar regime-invariant for 7/7 major PREFIXes; sh→qo enrichment +20.5σ reveals line sequencing; I(MIDDLE_t; PREFIX_{t+1})=0.499 bits cross-component dependency)
C1002	**SUFFIX Positional and Sequential Grammar** (8/22 suffixes non-uniform positional profiles vs PREFIX 20/32; R² suffix=0.027 vs PREFIX=0.069; extreme specialists am 88% line-final, om 88% final; SUFFIX sequential grammar chi²=2896 V=0.063 comparable to PREFIX V=0.060; edy→edy +14.3σ self-repetition dominance; I(SUFFIX; PREFIX_{t+1} \| MIDDLE) = -0.074 bits — zero cross-token signal; C932 category paragraph gradients do NOT decompose to individual suffixes)
C1003	**TOKEN is Pairwise Composite — No Three-Way Synergy**
C1004	**49-Class Sufficiency Confirmed — No Hidden Suffix State** (Token-level Markov 38% worse than 49-class; only 1/17 classes shows suffix-differentiated transitions (JSD); H reduction from suffix conditioning = 0.259 bits (5.6%) — present but modest; no fourth architectural layer; 49-class grammar is the correct resolution for transition dynamics)
C1005	**Bubble-Point Oscillation Falsified — Duty-Cycle Pattern**
C1006	**Macro-State Dwell Non-Geometricity is Topology Artifact**
C1007	**AXM Exit-Boundary Gatekeeper Subset**
C1008	**AXM Directional Gating Mechanism**
C1009	**AXM Exit Hazard-Target Compositional Curvature**
C1010	**6-State Macro-Automaton is Minimal Invariant-Preserving Partition**
C1011	**Discrimination Manifold and Macro-Automaton are Geometrically Independent** (only 85/972 MIDDLEs (8.7%) bridge A manifold → B grammar; macro-state silhouette = -0.126 z=-0.96 p=0.843 — no geometric footprint; forbidden transitions not at geometric boundaries ratio=0.991 p=1.0; HUB MIDDLEs peripheral not central norm 2.31 vs 0.76 p≈0; HUB sub-roles not geometrically distinct p=0.577; 3/6 pre-registered predictions passed; manifold = A-level compatibility, automaton = B-level transition topology — complementary not redundant)
C1012	**PREFIX is Macro-State Selector via Positive Channeling, Not Negative Prohibition**
C1013	A->B Vocabulary Bridge is a Topological Generality Filter
C1014	Discrimination Manifold Encodes Viability Structure via Bridge Backbone
C1015	**PREFIX-Conditioned Macro-State Mutability with FL-Specific Routing Asymmetry**
C1016	**Folio-Level Macro-Automaton Decomposition with Dynamical Archetypes**
C1017	**Macro-State Dynamics Decompose into PREFIX Routing, Hazard Density, and Bridge Geometry**
C1018	**Archetype Geometric Anatomy — Slope Anomalies, Bridge PC1 Decomposition, and HUB Sub-Role Differentiation**
C1019	**Morphological Tensor Decomposition — Transition Tensor Has Rank-8 Pairwise Structure Orthogonal to 6-State Macro-Automaton** (rank 8 at 97.0% variance; CP ≥ Tucker confirming C1003; class factors ARI=0.053 vs C1010 — macro-automaton NOT a tensor projection; ΔR²=0.465 dynamical prediction 4x C1017; SUFFIX 2 SVD dims confirming C1004; HUB vs STABILITY cosine=0.574)
C1020	**Tensor Archetype Geometry — Tensor Factors Encode Dynamics Through Graded Curvature, Not Macro-State Clustering**
C1021	**CP Factor Characterization — Tensor Factors Are Frequency-Dominated, Rank Is Continuous, Tensor-Automaton Orthogonality Is Complete**
C1022	**Paragraph Macro-Dynamics — 6-State Automaton Does Not Differentiate Paragraph Structure**
C1023	**Structural Necessity Ablation — PREFIX Routing Is Sole Load-Bearing Macro Component** (PREFIX→state content routing: 78-81% of non-random structure destroyed by shuffle+reassignment; FL merge: -0.34% spectral gap; gatekeeper JSD=0.0014, z=-0.70 vs null; within-state routing: 0% structure loss; REGIME pooling: 1.1% gap difference; hierarchy: PREFIX routing >> FL ≈ gatekeepers ≈ REGIME; 3/6 pre-registered predictions correct on verdict, overall hierarchy confirmed)
C1024	**Structural Directionality — MIDDLE Carries Execution Asymmetry, PREFIX Is Symmetric Router** (MIDDLE asymmetry 0.070 bits, PREFIX 0.018 bits, ratio 0.25x; FL role highest per-class JSD 0.311; class-level bigram JSD=0.089 confirming C886; null control retains 64% of JSD from sparsity; resolves C391/C886 tension: PREFIX symmetric routing + MIDDLE directional execution = symmetric constraints with directional probabilities; 1/5 predictions correct)
C1025	**Generative Sufficiency — Class Markov + Forbidden Suppression Is Sufficient at M2 (80%)** (M0 i.i.d. passes 11/15=73% revealing most tests are marginal; M2 49-class Markov + forbidden suppression = sufficiency frontier at 12/15=80%; M4 compositional generation WORST at 9.4/15=63% from 4.2% hallucination rate; macro-automaton M3 ties M2, adds nothing; B4/C2 universally failed = test specification issues; 2/5 predictions correct)
C1026	**Grammar Component Necessity — Class Ordering and Forbidden Avoidance Are Load-Bearing; Token Identity Is Partial**
C1027	**Hazard Violation Archaeology — Forbidden Pair Violations Are Spatially Uniform but Structurally Conditioned**
C1028	**Vocabulary Curation Rule — Pairwise Co-occurrence Is Necessary and Dominant** (productive product space 48,640; 419 existing = 0.9% occupancy; pairwise co-occurrence gate: 100% recall, 58.4% precision; depth-3 tree 99.4% CV using only pm_cooc + ms_cooc; no three-way compilation rule detectable; 718 pairwise-compatible → 419 exist; consistent with C1003 no three-way synergy)
C1029	**Section-Parameterized Grammar Weights**
C1030	**M2 Gap Decomposition — B4 Misspecified, Two Independent Mechanisms** (B4 trivially passes: M2 self-rates identical to real; corrected 13/15=86.7%; B5 asymmetry 3.85x overestimate needs PREFIX routing C1024; C2 CC 100% suffix-free needs role morphology; independent: C2 constant across sections, B5 varies)
C1031	**FL Cross-Line Independence**
C1032	**B5 Asymmetry Mechanism — Forbidden Suppression + PREFIX Routing** (M2 B5=0.178 vs real 0.090; 16/17 forbidden pairs one-directional; alpha=0.15 blending fixes B5=0.111 but regresses B1 spectral gap 0.894->0.770 and B3 5 violations; C1024 PREFIX fraction 20.5% consistent with 15% blending; M2 stays 13/15=86.7%; true fix needs PREFIX-factored generation)
C1033	**C2 Test Misspecification — CC Definition Mismatch** (test uses CC={10,11,12,17} but C588 used {10,11,12}; class 17 has 59% suffixed; real C2=0.834 fails 99% threshold; M2=0.824 matches real; corrected 14/15=93.3%; C590 class 17 suffix=NONE wrong; only B5 remains)
C1034	**Symmetric Forbidden Suppression Fixes B5** (M5-SF: bidirectional forbidden, B5=0.132 80% pass, B1=0.873 100% pass, B3=0; M2.5 blending fails under C1025 mapping; PREFIX-factored distributionally equivalent to M2; projected 15/15=100% with B4+C2 corrections)
C1035	**AXM Residual Irreducible** (0/7 PASS; all 6 predictors dR2 < 0.013; RF CV R2 = -0.149; LOO gap 0.132; residual = free design space per C458/C980)
C1036	**AXM Exit Pathway Allocation Frequency-Neutral**
C1037	**AXM Class Composition Redundant**
C1038	**AXM Run Entropy Convergence + Micro-Sequential Stratum Empty** (0/6 PASS after size control; entropy slope=-0.248 bits/pos; JSD/CMI size-confounded; four-phase elimination complete; residual = design freedom)
C1039	**A Paragraph Cluster Selectivity**
C1040	**A Folio-Level Paragraph Compatibility Coherence** (within-folio 0.880 vs between-folio 0.811, p~0; survives section matching 0.810, p~0)
C1041	**A Paragraph Complementary Diversification** (cross-line compatibility 0.700 vs null 0.707, z=-3.567; paragraphs diversify, not select for compatibility; extends C476 coverage optimality)
C1042	**Section-Conditional Positional Exclusivity Reduction** (C956 zone-exclusive tokens retain only 30-55% exclusivity within sections; global exclusivity partially a section composition effect; qualifies C956)
C1043	**Role Self-Loop Section Dependence**
C1044	**Section-Dependent Phase Interleaving Rate**
C1045	**Section-Dependent Boundary Role Composition**
C1046	**Mandatory Bigram Section Modulation** (5/10 mandatory bigrams show section-dependent rates at Bonferroni alpha=0.005; extends C957 and C1029 to bigram level)
C1047	**Section-Dynamics Interaction Absent** (0/3 interaction terms significant; section modulates dynamics additively only; per-section LOO 0.037 vs global 0.412; strengthens C1035)
C1048	**BIO Section Dynamical Coherence** (BIO LOO R²=0.754 vs HERBAL -0.242 and RECIPE -0.319; C1017 predictors explain 75% of BIO AXM variance; design freedom concentrated in non-BIO sections)
C1049	**Shared Vocabulary Section-Universal Substrate**
C1050	**PP Composition Section-Differential Coverage**
C1051	**Section-Conditioned Class Convergence Asymmetry**
C1052	**B Paragraph Cluster Selectivity**
C1053	**Compound Atom C475 Mediation**
C1054	**Affordance Bin Gradient Invariance** (HUB fraction ~64% at every quintile; 0/9 bins show gradient dependence; bin scaffold is static across spec→exec gradient; 73 paragraphs)
C1055	**M2 Near-Section-Decomposable** (per-section M2: BIO 78%, STARS_RECIPE 79%, HERBAL 70%; pooling advantage only +0.5 tests; topology preserved, distributional tests degrade cross-section)
C1056	**MIDPROCESS Structural Absence / OJLM-1 Boundary** (0/245 v3 recipes have MIDPROCESS actions; 0/509 master materials have process monitoring; MIDPROCESS is tacit operator knowledge; Path C mechanically passable but circular; Voynich M2 residual parallels 2/3 dynamic/pairwise)
C1057	**Lane-Sister Orthogonal Axes**
C1058	**Suffix Sequential Grammar Genuine**
C1059	**Suffix-Role PREFIX Independent** (V_raw=0.2869, V_conditioned=0.3750, mediation=-30.7%; per-PREFIX V: ol=0.663, ok=0.655, da=0.611, ot=0.532, BARE=0.436, ch=0.129, sh=0.120; 16054 classified tokens)
C1060	**Atom Position Grammar**
C1061	**Atom Co-occurrence Structure**
C1062	**Compound Depth-Folio Specificity**
C1063	**PREFIX-SUFFIX Compatibility** (chi²=8703.4, V=0.138; 17 forbidden pairs vs C911's 102; 16/17 novel, 1 role-explained; 50 enriched, 57 depleted; LATE prediction failed; ch/sh 0 forbidden; 30 PREFIXes x 21 SUFFIXes)
C1064	**PREFIX-SUFFIX Joint Role Encoding** (joint 88.5% vs PREFIX 82.6% vs SUFFIX 45.9%; +5.9pp gain; QO-family within-PREFIX V=0.615, sister V=0.124; three-layer encoding: PREFIX + suffix + joint; 16054 classified tokens)
C1065	**Atom Bigram Ordering Grammar**
C1066	**Construction-Execution Independence Confirmed**
C1067	**Terminal Character Positional Bias**
C1068	**Cross-Layer Partial Coupling**
C1069	**Weak Residual Community Structure** (3 communities after hub removal + frequency regression; Q_residual=0.125, Q_random=0.042, signal=0.082; weak but above-random; one community concentrates kernel-classified MIDDLEs)
C1070	**Atom Ordering Grammar Independent of Kernel Directional Bias** (only 2/21 cross-class pairs; both mismatch C521; compound construction grammar has own rules not reducible to kernel physics)
C1071	**Forbidden Transitions Operate Above Component-Level Rules** (only 4/17 C109 transitions blocked by C475/C911/C1063; 0 by C911 or C1063; 13/13 residual are C475-COMPATIBLE; confirms C627 token-specific directional mechanism)
C1072	**Terminal Character Predicts Within-Group Compatibility**
C1073	**Terminal-Role Association Is Frequency-Mediated**
C1074	**Terminal-State Association Is Frequency-Mediated**
C1075	**Compatibility Asymmetry Is Frequency-Dominated** (freq_sum +1.654 std coef dominates; INITIAL_match +0.089 below 0.10 threshold; INITIAL_x_FINAL +0.016 NS confirms C1003; shared_hinge +0.096; 271K pairs after singleton exclusion)
C1076	**Terminal Character Predicts Affordance Bin Beyond Frequency**
C1077	**Terminal Compatibility Groups Form Genuine Cliques**
C1078	**HT Hazard Avoidance Is Vocabulary-Level**
C1079	**Line-1 Exclusivity Is Folio-Specificity Tautology** (line-1 100% vs body 78.3% exclusive, p~0; singleton control: both 100%; C870 folio-specificity fully explains difference)
C1080	**Tail Pressure Predicts HT Compound Rate**
C1081	**LINK Adjacency Does Not Modulate HT Prefix Phase**
C1082	**HT Oscillation Is Section-Driven** (raw ACF significant at lags 1,2,4,6,20; section-residualized: only lag 7 survives; no lag 8-12 signal; resolves open question)
C1083	**HT Density Is Paragraph-Ordinal Neutral**
C1084	**Section-Specific AXM Attractor Ordering** > S(0.687) > C(0.635) > H(0.587); decomposes C1017 baseline; survives REGIME control)
C1085	**Bio Section Kernel-Balance Distinctiveness**
C1086	**Bio Section Apparatus-Hazard Depletion**
C1087	**Bio-REGIME_1 Multidimensional Divergence**
C1099	**Bridge Density Section Gradient**
C1102	**Bridge Density REGIME Dependence**
C1103	**REGIME-Bridge Density Is Section Confound**
C1104	**Bridge Density Enables Dynamical Freedom**
C1105	**Bridge Geometry-Density Collinearity** (r=-0.805; delta-R²=0.007 NS beyond C1017; BIO LOO exception +0.071; same structural property, different measures)
C1106	**Stars e-Stability Kernel Enrichment**
C1107	**Stars LINK Monitoring Concentration**
C1108	**Stars Vocabulary Clamping Falsified** (S7-S10: 0 PASS, 3 FAIL; no consistent intra-REGIME clamping, no e-mediation, no bridge mediation, vocabulary LESS homogeneous across REGIMEs; Stars Paradox remains open)
C1111	**Stars Paradox is REGIME Composition Artifact**
C1112	**P-Text Bridge Enrichment** (45.5% bridge MIDDLEs, 55/121 unique, 100th percentile of A bootstrap; exceeds Rosettes 21.5% by 2.1x; evidence independent of Rosettes transcript)
C1116	**Within-REGIME Section Parameterization**
C1117	**LTR Reading Direction Confirmed**
C1118	**Bidirectional Forbidden Co-occurrence Dominance** (75.2% of MIDDLE-level forbidden pairs 1244/1655 are bidirectional adjacency prohibitions; 24.8% direction-specific; explains C1034 symmetric forbidden model improvement; broader MIDDLE co-occurrence landscape is predominantly symmetric while 17 class-level transitions C783 are directional)
C1119	**MIDDLE Forward Bias as Reading Direction Evidence**
C1120	**Lifecycle Domain Progression Falsified**
C1121	**Folio-Level Domain Determination** (paragraph domain character Bio/Stars determined at folio level ICC=0.393, F(45,95)=2.98; within REGIME_1 section predicts Bio-score Bio=0.131 vs Stars=-0.027 diff=0.158; within-paragraph domain stable perm p=0.19; consistent with C1087 Bio divergence)
C1124	**Rosettes Bridge Enrichment (Revalidated)** (3.05x enrichment: 21.5% bridge MIDDLEs vs 7.0% B baseline; universal across entity types — ring 4.56x, inner_label 4.74x, outer_label 5.17x, spiral 3.55x, clock 7.11x; no type below 25%)
C1125	**Rosettes Universal Section T Correlation**
C1126	**Rosettes Metalayer Status (Revalidated)** (confirmed metalayer: AZC-like entity types, 3.05x bridge enrichment, universal Section T indexing, 2.2x MIDDLE compatibility; verdict ROSETTES_CONFIRMED_METALAYER)
C1127	**Rosettes AZC-Like Grammar Profile** (grammar coverage 42.0%, kernel density 29-41%, LINK density <2.1% except ring 4.2%; morphological cosine 0.49-0.82 with AZC vs 0.25-0.67 with B; PP ~50%, RI ~2%; consistently AZC-like not hybrid)
C1128	**Rosettes Generic (Not Specific) Indexing**
C1129	**P-Text/Rosettes Unified Indexing (Revalidated)**
C1130	**Ring Text Forbidden Compliance Without Transition Grammar** (0 forbidden violations in 277 MIDDLE bigrams; bigram entropy 7.92 bits vs B ~0.41; 252/277 unique bigrams; respects C783 hard constraints but has random transition structure; supersedes C1114/C1115)
C1131	**Ring Text Register Classification — BRIDGE_VOCABULARY_INDEX** (52.4% map to B grammar using 33/49 classes; AUXILIARY 42.7%, ENERGY 11.3%; bridge enrichment 32.1% > non-ring 25.5% > B p95 11.0%; 100% of classified MIDDLEs are bridge; no positional structure; structured class distribution JS=0.291 from uniform)
C1132	**Ring Text Dual Population Structure** (classified: 150 tokens, 4.0 chars, 27.3% kernel, 22.6% compound, 100% bridge; unclassified: 136 tokens, 6.4 chars, 47.8% kernel, 49.5% compound, 22.1% bridge — two interleaved functional vocabularies)
C1133	**Rosettes Targeting Decomposition**
C1134	**Section Specificity Is Frequency-Modulated** (PP drives 74% of section divergence through token frequency variation; B-exclusive JS=0.847 but only 5.8% of tokens; resolves C1049/C909 paradox)
C1135	**Unmatched PP Dark Pipeline** (300/315 unmatched PP MIDDLEs present in B at low frequency: mean 5.7 tokens vs 224.8 matched; section-concentrated Herf=0.716; 66.7% compound; large HT/UN substrate)
C1136	**A->B Flow: Uniform Pool, Concentration-Structured** (A-H/A-P cosine=0.9997; 12 A folios cover 100% classified grammar; f58v alone=60.7%; max A->B coverage ceiling 30.4%)
C1137	**Dark Pipeline = 100% HT/UN Substrate** (1,696 tokens from 300 MIDDLEs: 0.0% grammar-classified, 100.0% HT/UN; all 300 MIDDLEs pure-HT; mean 5.7 tokens/MIDDLE; positionally and sectionally indistinguishable from general HT)
C1138	**Dark Pipeline Has Distinct Construction Grammar** (grammar-standard/extended PREFIX ratio 3.39 vs general HT 1.81; suffix rate 89.9% vs HT 77.3%; articulator rate 2.5% vs HT 10.1%; same MIDDLEs but different morphological wrapping than general HT)
C1139	**Dark Pipeline and Bridge Backbone Completely Disjoint** (0/300 dark-pipeline MIDDLEs overlap with 85 bridge MIDDLEs; separate A->B channels: bridges carry dynamical structure, dark pipeline carries identification vocabulary)
C1140	**PP Pipeline Is a Complete Four-Way Partition** (85 bridge + 4 non-bridge matched + 300 dark pipeline + 15 phantom = 404; exhaustive and mutually exclusive; non-bridge matched are c/ch/cho/otc, AUXILIARY-dominant edge cases; phantoms all ch/sh-prefixed with 0 A tokens)
C1141	**Dark Pipeline Compounds Built from Bridge Atoms** (86% of atom types are bridge MIDDLEs, 91.6% of occurrences; 96.5% of compounds contain >= 1 bridge atom; 50 unique atoms: 43 BRIDGE, 6 DARK_PIPELINE, 1 OTHER; mean 1.44 atoms/compound)
C1142	**Dark Pipeline Uses Modified Construction Grammar**
C1143	**Dark-Exclusive and Shared Atoms Have Equivalent Section Profiles** and less spread (11.4 vs 22.1 folios) but same section Herfindahl)
C1144	**Dark Pipeline Ordering Divergence Is Genuine Grammar Modification**
C1145	**Dark-Exclusive and Shared Atoms Occupy Equivalent Positional Slots**
C1146	**Dark Pipeline Token Density Anti-Correlates with Bridge Tokens** (r=-0.865 overall; within-section r=-0.82 to -0.88 in all 4 sections; section R²=0.193; 80.7% of variance within-section; complementary distribution)
C1147	**Dark Pipeline Tokens Are Interior-Enriched Within Lines**
C1148	**Dark Pipeline Frequency Profiles Are Hyper-Modulated Across Sections** (mean JS=0.483, 3.9x C1134 baseline of 0.124; dark pipeline is primary vehicle for section-level vocabulary modulation)
C1149	**Vocabulary Balance Is Orthogonal to Dynamical Archetypes**
C1150	**Dark-Dominant Folios Shift Kernel Profile Within Section**
C1151	**Balance Distribution Is Section-Structured**
C1152	**Section-M2 Captures Vocabulary Composition but Not Sequential Dynamics** (class dist ratio 1.48x near-captured; AXM spread 1.76x uncaptured; kernel profile 1.79x uncaptured; 87% folios improved by section-conditioning; vocabulary is section-determined, dynamics are program-specific)
C1153	**Generative Design Freedom Is ~40%** (32.4% class-dist + 43.2% AXM + 44.0% kernel uncaptured; aggregate 39.9%; AXM consistent with C1035's 57%; lower than C1016's 66.3% because class distribution IS section-captured)
C1154	**k-Kernel and e-Kernel Variance Are Universally Program-Specific** (k ratio 1.82-2.32x, e ratio 1.76-2.21x across all sections; h-kernel section-determined in BIO/HERBAL/COSMO (0.74-1.29x) but program-specific in STARS_RECIPE (2.18x))
C1155	**Paragraph Kernel Dynamics Do Not Mediate the AXM Residual** (kernel heterogeneity dR²=0.0012, trajectory slope variance dR²=0.0014, type entropy dR²=0.0002; all with negative LOO; within-section rho all <0.16; C1035 residual confirmed closed at paragraph level)
C1156	**Line Position Structures Class Transitions**
C1157	**Boundary Divergence Mediates the AXM Residual**
C1158	**Entry Divergence Dominates Boundary Divergence Effect** (entry dR²=0.098 vs exit dR²=0.028, 3.5×; entry is the "reset to base" intensity; contradicts gatekeeper hypothesis)
C1159	**Boundary Divergence Is a Routing Shift, Not AXM Persistence Decay** (AXM→AXM only 3.2% of total delta; dominant: AXm→AXM +0.124, FQ→AXM +0.103 at entry; CC→AXM -0.296 at exit; inter-state routing, not self-transition)
C1160	**Boundary Divergence Is Section-Confounded but Carries Independent Signal**
C1161	**Gatekeeper Classes Partially Mediate Boundary Divergence**
C1162	**Opener Role Does Not Predict Entry Divergence** (R²=0.128; no role |rho|≥0.30; role entropy uncorrelated; entry mechanism operates below role-level identity)
C1163	**AXM Return Rate Dominates Entry Mechanism**
C1164	**Opener Routing Partially Mediates Entry Divergence**
C1165	**AXM Return Rate Extends Residual Beyond Entry Divergence**
C1166	**Exit Divergence Redundant After Entry Control**
C1167	**AXM Departure Rate at Exit Extends Residual**
C1168	**Dual Boundary Architecture** (entry+exit independent channels; dual R²=0.852 LOO=0.732; exit dR²=0.039 LOO+0.036; all 3 sections benefit; irreducible ~57%→~27%)
C1169	**AXM Residual Closed — ~27% Is Genuine Design Freedom**
C1170	**LINK Vocabulary Stratified by Role**
C1171	**LINK Behavior Is Role-Dominant**
C1172	**BIO LINK Excess Is SPAN-Targeted**
C1173	**LINK Boundary Enrichment Is Passive**
C1174	**LINK Is Morphological Artifact** (synthesis: STRATIFIED + ROLE_DOMINANT + PASSIVE → `ol` is morphological component not functional layer; revises C366/C609 interpretation)
C1175	**Dark Compound Pair Space C475-Gated**
C1176	**Section Hyper-Modulation Atom-Selection-Dominated** (multiplicative model R²=0.781 pseudo-R²=0.677; atoms carry section signal, compounds inherit)
C1177	**Dark Ordering Consistent with C1065** (4/4 match 0 mismatch; revises C1142 50% from low-count noise; same grammar, sparse coverage)
C1178	**Phantom MIDDLEs Morphologically Isolated** (0/15 valid-unfilled; 11 partial 4 invalid; ch/sh-initial MIDDLE is dead naming pattern)

---

# All Explanatory Fits

# FIT_TABLE.txt - Programmatic Fit Index
# WARNING: No entry in this file constrains the model.
# Generated: 2026-02-20
# Total: 66 fits
# Format: ID	FIT	TIER	SCOPE	RESULT	SUPPORTS	FILE

ID	FIT	TIER	SCOPE	RESULT	SUPPORTS	FILE
F-A-001	Compositional Token Generator	F2	A	PARTIAL	C267-C282	in: fits_currier_a
F-A-002	Sister-Pair Classifier	F1	A	NULL	C407-C410	in: fits_currier_a
F-A-003	Repetition Distribution	F1	A	INVALIDATED	(none - artifact)	in: fits_currier_a
F-A-004	Entry Clustering HMM	F2	A	SUCCESS	C424	in: fits_currier_a
F-A-005	Scarcity-Weighted Registry Effort	F1	A	NULL	C293	in: fits_currier_a
F-A-007	Forbidden-Zone Attraction	F1	A	NULL	C281	in: fits_currier_a
F-A-008	Repetition as Relational Stabilizer	F1	A	INVALIDATED	(none - artifact)	in: fits_currier_a
F-A-009	Comparability Window	F2	A	SUCCESS	C424	in: fits_currier_a
F-B-001	LINK Operator as Sustained Monitoring Interval	F2	B	SUCCESS	C366, C609, C190	in: fits_currier_b
F-B-002	QO Lane as Safe Energy Pathway	F3	B	SUCCESS	C601, C574, C600	in: fits_currier_b
F-B-003	Pre-Operational Configuration via A→AZC→B Pipeline	F2	B	SUCCESS	C473, C506, C468	in: fits_currier_b
F-B-004	Lane Hysteresis Control Model	F2	B	SUCCESS	C643, C549, C577, C608	in: fits_currier_b
F-B-005	PP-Lane MIDDLE Discrimination	F2	B	SUCCESS	C646, C576, C642	in: fits_currier_b
F-B-006	Energy/Stabilization Lane Assignment	F3	B	PARTIAL	C647, C645, C601, C521	in: fits_currier_b
F-AZC-001	Placement Prediction Model	F4	AZC	NEGATIVE	C466-C467	in: fits_azc
F-AZC-002	Zodiac Positional Grammar	F2	AZC	SUCCESS	C467	in: fits_azc
F-AZC-005	A/C Positional Grammar Test (DECISIVE)	F2	AZC	SUCCESS	C430-C436, C467	in: fits_azc
F-AZC-003	Family Membership Classifier	F4	AZC	PARTIAL	C466	in: fits_azc
F-AZC-004	Option-Space Compression	F2	AZC	SUCCESS	C463-C465	in: fits_azc
F-AZC-006	Boundary Airlock Profile	F4	AZC	INCONCLUSIVE	(pending data)	in: fits_azc
F-AZC-007	Position-Conditioned Escape Suppression	F2	AZC	SUCCESS	C463-C465	in: fits_azc
F-AZC-008	Boundary Asymmetry (Semantic Hypothesis Test)	F3	AZC	PARTIAL	(exploratory)	in: fits_azc
F-AZC-009	Local vs Global Reference Partition (FINAL SEMANTIC TEST)	F4	AZC	DISCARDED	(none - frame rejected)	in: fits_azc
F-AZC-010	Cross-System Alignment by Family (CALENDRIC STRESS TEST)	F4	AZC	FALSIFIED	(strengthens null hypothesis)	in: fits_azc
F-AZC-011	Folio Threading Analysis	F2	AZC	SUCCESS	C318, C321, C430, C436	in: fits_azc
F-AZC-012	Orientation Basis Coverage	F2	AZC	SUCCESS	C301, C318, C326, C343	in: fits_azc
F-AZC-013	Orientation Posture Differentiation	F2	AZC	SUCCESS	C436, C457, C458, C460	in: fits_azc
F-AZC-015	Windowed AZC Activation Trace	F2	AZC	SUCCESS	C440, C441-C444	in: fits_azc
F-AZC-016	AZC->B Constraint Fit Validation	F2	AZC	SUCCESS	C468, C469, C470	in: fits_azc
F-AZC-017	Zodiac Internal Stratification Test (NEGATIVE)	F4	AZC	FALSIFIED	C431, C436	in: fits_azc
F-AZC-018	A/C Internal Stratification Test (NEGATIVE)	F4	AZC	FALSIFIED	C430, C436	in: fits_azc
F-AZC-019	A/C Incompatibility Density Test (POSITIVE)	F2	AZC	SUCCESS	C430, C475	in: fits_azc
F-ECR-001	Material-Class Identification	F3	GLOBAL	SUCCESS	C109-C114, C232	in: fits_global
F-ECR-002	Apparatus-Role Identification	F3	GLOBAL	SUCCESS	C085-C108, C171, C216	in: fits_global
F-ECR-003	Decision-State Semantics	F3	GLOBAL	SUCCESS	C384, C404-C405, C459-C460	in: fits_global
F-BRU-001	Brunschwig Product Type Prediction (Blind)	F2	A	SUCCESS	C475, C476	in: fits_brunschwig
F-BRU-002	Degree-REGIME Boundary Asymmetry	F3	B	SUCCESS	C179-C185, C458	in: fits_brunschwig
F-BRU-003	Property-Based Generator Rejection	F2	A	NEGATIVE	C475, C476	in: fits_brunschwig
F-BRU-004	A-Register Cluster Stability	F2	A	SUCCESS	C481	in: fits_brunschwig
F-BRU-005	MIDDLE Hierarchical Structure	F2	A	SUCCESS	C383, C475	in: fits_brunschwig
F-BRU-006	Closure × Product Affordance Correlation	F3	A	SUCCESS	C233, C422 (closure/DA structure)	in: fits_brunschwig
F-BRU-007	SLI-Constraint Substitution Model	F2	B	SUCCESS	C458, C477	in: fits_brunschwig
F-BRU-008	Zone Affinity Differentiation	F2	B	SUCCESS	C443 (Positional Escape Gradient)	in: fits_brunschwig
F-BRU-009	Zone-Modality Addressing (Two-Stage Model)	F3	B	CONFIRMED	C477 (HT), C443 (Escape Gradient), C458 (Execution Design Clamp)	in: fits_brunschwig
F-BRU-010	Folio Position Procedural Phase Mapping	F3	B	PARTIAL	C676 (Morphological Parameterization Trajectory), C668 (Lane Balance Trajectory)	in: fits_brunschwig
F-BRU-011	Three-Tier MIDDLE Operational Structure	F2	B	CONFIRMED	C423 (MIDDLE Census), F-BRU-005 (MIDDLE Hierarchy)	in: fits_brunschwig
F-BRU-012	Preparation MIDDLE Operation Mapping	F3	B	SUPPORTED	F-BRU-011 (Three-Tier Structure)	in: fits_brunschwig
F-BRU-013	Extended Operation MIDDLE Differentiation (ke vs kch)	F3	B	SUPPORTED	F-BRU-011 (Three-Tier Structure), F-BRU-012 (Preparation Mapping)	in: fits_brunschwig
F-BRU-014	Vowel Primitive Suffix Saturation	F2	GLOBAL	CONFIRMED	C906 (Vowel Primitive Suffix Saturation), C267 (Compositional Morphology), C510-C513 (Sub-Component Grammar)	in: fits_brunschwig
F-BRU-015	Procedural Dimension Independence	F2	B	CONFIRMED	F-BRU-011 (Three-Tier Structure), BRUNSCHWIG_CLOSED_LOOP_DIMENSIONS	in: fits_brunschwig
F-BRU-016	REGIME Procedural Differentiation	F2	B	CONFIRMED	C494 (REGIME_4 Precision Axis), F-BRU-015 (Procedural Independence)	in: fits_brunschwig
F-BRU-017	REGIME_4 Sustained Equilibration Mechanism	F3	B	SUPPORTED	C494 (REGIME_4 Precision Axis), F-BRU-013 (ke vs kch)	in: fits_brunschwig
F-BRU-018	Root Illustration Processing Correlation (Tier 4 External Anchor)	F4	A	CONFIRMED	C883 (Handling Distribution Alignment), F-BRU-012 (Preparation Mapping)	in: fits_brunschwig
F-BRU-019	Delicate Plant Material as Unmarked Default	F3	A	SUPPORTED	F-BRU-018 (Root Illustration Correlation), C884 (Animal Correspondence)	in: fits_brunschwig
F-BRU-020	Output Category Vocabulary Signatures	F4	B	CONFIRMED	F-BRU-017 (REGIME_4 Sustained Equilibration), C494 (REGIME_4 Precision Axis)	in: fits_brunschwig
F-BRU-021	Controlled Variable Identification (Temperature / Thermal State)	F3	B	SUCCESS	C976 (6-State Topology), C978 (Hub-and-Spoke), C979 (REGIME Modulates Weights), C980 (Free Variation Envelope)	in: fits_brunschwig
F-BRU-022	Recipe Triangulation via PP-REGIME Pathway (NEGATIVE)	F3	B	NEGATIVE	C882 (PRECISION Kernel), C883 (Handling Distribution), C502 (PP Filtering), C753 (Near-Zero Routing)	in: fits_brunschwig
F-BRU-023	Forbidden Transition Thermodynamics (TOKEN-LEVEL COHERENCE)	F4	B	THERMODYNAMIC_COHERENCE	C109 (Hazard Classes), C783 (Directional Asymmetry), C997 (Safety Buffers)	in: fits_brunschwig
F-BRU-024	PP MIDDLE Extension Validation (NEGATIVE)	F4	B	EXTENSION_UNSUPPORTED	C498 (RI/PP Bifurcation), C267 (Compositional Morphology), C995-C1000 (Affordance Bins)	in: fits_brunschwig
F-BRU-025	Gloss Structural Validation (Adversarial + Distributional)	F4	B	GLOSS_NOT_CONSTRAINED	(negative — forbidden transitions too few for category-level adversarial test; distributional context weakly aligns)	in: fits_brunschwig
F-BRU-026	Gloss Adversarial Validation (PREFIX-Domain + Mantel)	F4	B	DOMAIN_VALIDATED_MANTEL_CIRCULAR	C911 (PREFIX-MIDDLE Selectivity), C601 (QO Hazard Exclusion), C997 (Safety Buffers), C995 (Affordance Bins)	in: fits_brunschwig
F-BRU-027	Variance Architecture Alignment (Process-Constrained / Output-Free)	F3	B	VARIANCE_ARCHITECTURE_ALIGNED	C458 (design asymmetry: hazard clamped, recovery free), C980 (66.3% free variation envelope)	in: fits_brunschwig
F-BRU-028	Output Parameter REGIME Gradient Mapping (GRADIENT INVERTED)	F3	B	GRADIENT_INVERTED	C458 (design asymmetry), C980 (free variation envelope), C1035 (irreducible residual), C494 (REGIME_4 precision axis)	in: fits_brunschwig
F-BRU-029	Semantic Boundary Probe (Three-Path)	F4	B	PARTIAL_EXTENSION	C997 (safety buffer architecture), F-BRU-023 (thermodynamic coherence), C494 (REGIME_4 precision axis)	in: fits_brunschwig
F-BRU-030	MIDPROCESS Absence Characterization	F3	B	MIDPROCESS_STRUCTURALLY_ABSENT	C1056 (MIDPROCESS structural absence), F-BRU-029 (Path C closure)	in: fits_brunschwig
F-RUP-001	Galenic Framework Directional Enhancement	F4	B	DIRECTIONAL_COHERENCE	C109 (Hazard Classes), C121 (49 Instruction Classes), C475 (MIDDLE Incompatibility), C494 (REGIME_4 Precision Axis), C458 (Design Asymmetry), C911 (PREFIX-MIDDLE Compatibility), C995 (Affordance Bins), C997 (Safety Buffers), C1053 (Compound Atom C475 Mediation)	in: fits_rupescissa

---

# Tier 3-4 Interpretations

# Speculative Interpretation Summary

**Status:** SPECULATIVE | **Tier:** 3-4 | **Version:** 4.70

---


## Purpose

This document consolidates all Tier 3-4 interpretations into a single reference. It is designed for external AI context loading.

**Critical:** Everything in this document is NON-BINDING speculation. It is consistent with the structural evidence but NOT proven by it. Treat as discardable if contradicted by new evidence.

---


## Frozen Conclusion (Tier 0 - Context Only)

> The Voynich Manuscript's Currier B text encodes a family of closed-loop, kernel-centric control programs designed to maintain a system within a narrow viability regime, governed by a single shared grammar.

This structural finding is FROZEN. The interpretations below attempt to explain what this structure might have been FOR.

---


## Universal Boundaries

All interpretations in this document respect these constraints. Individual sections may add section-specific caveats but these five apply universally:

1. **Semantic ceiling** (C171, C120): No token-level meaning or translation is recoverable from internal analysis alone.
2. **No entry-level A-B coupling** (C384): No mapping from individual A entries to individual B tokens exists.
3. **No substance identification**: Specific plants, materials, or substances cannot be identified from the text.
4. **No Brunschwig equivalence**: Voynich is not a cipher for Brunschwig; no folio-to-passage mapping exists.
5. **Tier discipline**: All interpretations are Tier 3-4 speculation, consistent with but not proven by structural evidence.

---


## Epistemological Frame: Structure-Fitting, Not Translation





---


## 0. APPARATUS-CENTRIC SEMANTICS (CCM Phase)
### Tier 3: Core Finding

> **The manuscript encodes the operational worldview of a controlled apparatus, not the descriptive worldview of a human observer.**

All recoverable semantics are those available to the apparatus and its control logic: states, transitions, risks, recoveries. All referential meaning (materials, plants, devices) is supplied externally by trained human operators.

### Token Decomposition (Complete)

Every Currier A/B token decomposes into four functional components:

```
TOKEN = PREFIX   → operation domain selector (selects allowed MIDDLE family)
      + SISTER   → operational mode (how carefully)
      + MIDDLE   → operation type (heating/cooling/monitoring)
      + SUFFIX   → context-dependent marker (system role + material class)
```

| Component | Encodes | Classes | Evidence |
|-----------|---------|---------|----------|
| **PREFIX** | Operation domain | 4 classes selecting MIDDLE families | C911: 102 forbidden combinations |
| **SISTER** | Operational mode | 2 modes (precision/tolerance) | C412 anticorrelation |

| PREFIX Class | Selects For | Enrichment | Forbidden From |
|--------------|-------------|------------|----------------|
| **qo-** | k-family (k, ke, t, kch) | 4.6-5.5x | e-family, infrastructure |
| **ch-/sh-** | e-family (edy, ey, eey) | 2.0-3.1x | k-family, infrastructure |


**SUFFIX Two-Axis Model (revised 2026-01-24):**

| Axis | Scope | Finding | Tier |
|------|-------|---------|------|
| System role | A vs B enrichment | -edy 49x B, -ol 0.35x A-enriched | 2 (C283) |
| Material class | Within A: animal vs herb | Animal: 78% -ey/-ol; Herb: 41% -y/-dy | 3 (C527) |

| Class | Prefixes | Domain Target | Selects MIDDLE Family | Brunschwig Parallel |
|-------|----------|---------------|----------------------|---------------------|
| **Energy** | qo | Heat source | k-family only | Heating, distillation |
| **Process Testing** | ch, sh | The process | e-family only | Finger test, drip watching |




| Family | MIDDLEs | Kernel Profile | Section Concentration | Function |
|--------|---------|---------------|----------------------|----------|
| **k-family** | k, ke, ck, ek, eck, kch, lk | HIGH_K (1.3-1.6x) | B (bathing) 1.5-2x | Heating, energy input |
| **e-family** | e, ed, eed, eo, eeo, eod, eey | HIGH_E (1.2-1.6x) | S (recipes) 1.3-1.7x | Cooling, stabilization |
**Evidence strength:**
- 55% of MIDDLEs significantly correlate with kernel profile (C908)
- 96% of MIDDLEs are section-specific (C909)
- 67% of MIDDLEs are REGIME-specific (C910)

| Section | Content | MIDDLE Profile | Brunschwig Interpretation |
|---------|---------|---------------|---------------------------|
| **B** (Bathing) | Human figures in tubs | k-enriched 1.5-2x | Balneum marie (water bath heating) |
| **H** (Herbal) | Plant illustrations | Mixed k+h | Extraction (heat + phase monitoring) |


| Property | Value |
|----------|-------|
| Form | `dam` = da (anchor) + m + ø (no suffix) |
| Frequency | 55% of all m-MIDDLE tokens |


| Level | Unit | Constraint Type | Freedom |
|-------|------|-----------------|---------|
| **Paragraph** | Multi-token sequence | Co-occurrence | Nearly free (585 positive pairs, 1 negative) |
| **Token** | PREFIX + MIDDLE | Morphological selection | Tight (102 forbidden combinations) |

| Sister | Mode | Escape Density | Meaning |
|--------|------|----------------|---------|
| **ch** (vs sh) | Precision | 7.1% | Tight tolerances, fewer recovery options |
| **sh** (vs ch) | Tolerance | 24.7% | Loose tolerances, more escape routes |


| Prefix | Position | Suffix-Less | Interpretation |
|--------|----------|-------------|----------------|
| al | 0.692 | 43.9% | Output marker |
| ar | 0.744 | 68.4% | Terminal form |
**Structural evidence (C539, Tier 2):**

**Interpretive hypothesis (Tier 3):**




| Pattern | Count | Interpretation |
|---------|-------|----------------|
| lch = l + ch | 74 | Modified ch operation |
| lk = l + k | 58 | Modified k operation |

**Provenance contrast with LATE:**



| Folio Type | Example | L-compound | LATE | ENERGY |
|------------|---------|------------|------|--------|
| Control-intensive | f83v | 4.94% | 0.00% | High |
| Output-intensive | f40r | 0.00% | 6.19% | Lower |
**REGIME correlation:**




| REGIME | L-compound | Kernel | LATE | Profile |
|--------|------------|--------|------|---------|
| REGIME_1 | 2.35% | 16.8% | 1.37% | Control-infrastructure-heavy |
| REGIME_2 | 0.32% | 10.2% | 3.14% | Output-intensive |
**Section B Concentration (70% REGIME_1):**
| Section | REGIME_1 | REGIME_2 | REGIME_4 | Interpretation |
|---------|----------|----------|----------|----------------|
| B (balneological) | 70% | 5% | 10% | Control-heavy |
| H (herbal) | 13% | 31% | 44% | Output-distributed |

**Enriched MIDDLEs in REGIME_1:**

**Fire-degree distributes by Section, not REGIME:**
| Section | High-Fire | Low-Fire | Ratio |
|---------|-----------|----------|-------|
| H | 3.9% | 17.8% | 0.22 (lowest) |
| B | 7.5% | 19.4% | 0.39 |

| Tier | MIDDLEs | Usage | Properties |
|------|---------|-------|------------|
| **Core** (top 30) | 30 | 67.6% | Mode-flexible, section-stable, cross-class |
| **Tail** | 1,154 | 32.4% | Mode-specific, hazard-concentrated, class-exclusive |

**Recoverable internally (role-level):**

**Irrecoverable internally (entity-level):**


**Semantic Ceiling Gradient (C499, v4.31):**

| Level | Recoverability | Method |
|-------|----------------|--------|
| Entity identity (lavender) | IRRECOVERABLE | - |
| Material CLASS priors | **PARTIALLY RECOVERABLE** | Bayesian inference via procedural context |
**Conditional recovery (IF Brunschwig applies):**



---


## 0.A. CURRIER A COGNITIVE INTERFACE (PCC Phase)
### Tier 3: Core Finding

> **Currier A is designed for expert navigation without meaning - a human-facing complexity-frontier registry with cognitive affordances optimized for working memory.**

This extends the Complexity-Frontier Registry model with empirical characterization of how humans would interact with the system.


| Property | Finding |
|----------|---------|
| Function | Return vocabulary to neutral, maximally compatible state |
| -y ending | 36.5% at final position |


| Metric | Value |
|--------|-------|
| Within-cluster coherence | 2.14x vs cross-cluster |
| Median cluster size | 2 |


| Property | Clustered | Singleton |
|----------|-----------|-----------|
| Hub overlap | 0.850 | 0.731 |
| Incompatibility density | 0.979 | 0.986 |


| Factor | Effect on Breadth | p-value |
|--------|-------------------|---------|
| Hub-dominant | Broader | - |
| Tail-dominant | Narrower | <0.0001 |



### What This Does NOT Claim

Universal Boundaries apply. Additionally:
- ❌ Closure markers are adaptive signals
- ❌ Working-memory structure implies temporal ordering

### Cross-References

| Constraint | Finding |
|------------|---------|
| C233 | LINE_ATOMIC (base for closure model) |
| C346 | Sequential coherence 1.20x |
| C424 | Clustered adjacency |
| C422 | DA articulation |


---


## 0.A.1. RI INSTANCE IDENTIFICATION SYSTEM (RI_EXTENSION_MAPPING Phase)
### Tier 2/3: Core Finding

> **RI vocabulary functions as an instance identification system built via derivational morphology from PP vocabulary. PP encodes general categories shared with B execution; RI extends PP with single-character markers to identify specific instances. This explains A's purpose as an index bridging general procedures (B) to specific applications (labels, illustrated items).**

This resolves the fundamental question: "Why does Currier A exist if Currier B is self-sufficient for execution?"

| Level | Vocabulary | Function | Example |
|-------|-----------|----------|---------|
| **B (Execution)** | PP only | General operations | "Process 'od' at temperature 'kch'" |
| **A (Registry)** | PP + RI | Specific instances | "Entry for 'odo': follow procedure X" |

     |

**Structural evidence:**
- 90.9% of RI MIDDLEs contain PP as substring (C913)


| PP MIDDLE | Direct Uses | As RI Base | Interpretation |
|-----------|-------------|------------|----------------|
| 'od' | 191 | 23 | Category AND instances |
| 'eo' | 211 | 14 | Category AND instances |


       |
       |

| Question | Answer |
|----------|--------|
| Why does A exist if B is self-sufficient? | A indexes specific applications of general B procedures |
| Why are labels RI-enriched? | Labels point to specific illustrated items |
### What This Does NOT Claim

Universal Boundaries apply. Additionally:
- X RI encodes semantic content beyond instance differentiation

### Cross-References

| Constraint | Finding |
|------------|---------|
| C240 | A = Registry - now explains the indexing mechanism |
| C913 | RI Derivational Morphology |
| C914 | RI Label Enrichment (3.7x) |
| C915 | Section P Pure-RI Entries |
| C916 | RI Instance Identification System (synthesis) |


---


## 0.A.2. LABEL-TO-B PIPELINE (LABEL_INVESTIGATION Phase)
### Tier 2/3: Core Finding

> **Labels connect to B through shared PP vocabulary, with jar labels specifically concentrating in AX_FINAL (material-carrying) positions at 2.1x baseline rate. This validates the three-level model: Labels identify materials that B procedures operate ON.**

     |
     |
     |

| Label Type | B Connection | AX_FINAL Rate | Function |
|------------|--------------|---------------|----------|
| **Jar** | PP bases in B | **35.1%** (2.1x) | Container/configuration identifier |
| **Content** | PP bases in B | 19.1% (1.14x) | Material identifier (root, leaf) |

| Finding | Significance |
|---------|--------------|
| **C571 confirmed** | PREFIX selects role, MIDDLE carries material identity |
| **Labels are functional** | They point to materials that B operates on |
     |
     |


### What This Does NOT Claim

Universal Boundaries apply. Additionally:
- X Specific jar-to-procedure mappings are recoverable
- X Content labels have the same AX_FINAL concentration (they don't)

### Cross-References

| Constraint | Finding |
|------------|---------|
| C565 | AX_FINAL positional semantics |
| C570 | AX PREFIX derivability |
| C571 | PREFIX selects role, MIDDLE carries material |
| C523 | Pharma jar label vocabulary bifurcation |
| C914 | RI label enrichment (3.7x) |
| C928 | Jar label AX_FINAL concentration (2.1x) |


---


## 0.B. PP FUNCTIONAL ROLE CLOSURE (PP_B_EXECUTION_TEST Phase)
### Tier 2: Core Finding

> **PP (Pipeline-Participating) MIDDLEs have a two-level effect: COUNT determines class survival breadth, COMPOSITION determines intra-class token configuration.**

This resolves both the C505 paradox (material-class PP differentiation with null class-level effects) and the "480 token paradox" (why maintain 480 tokens if 49 classes suffice).

| Level | What PP Determines | Evidence |
|-------|-------------------|----------|
| **Class** | Which instruction types survive | COUNT matters (r=0.715), COMPOSITION doesn't (cosine=0.995) |
| **Token** | Which variants within classes are available | COMPOSITION matters (Jaccard=0.953 when same classes) |
**Variable taxonomy:**
| Variable Type | System | What It Does | Evidence |
|---------------|--------|--------------|----------|
| **Routing** | AZC | Position-indexed legality | C443, C468 |
| **Differentiation** | RI | Identity exclusion (95.7% incompatibility) | C475, C481 |

| Test | Result | Interpretation |
|------|--------|----------------|
| PP count vs B class survival | r=0.715, p<10^-247 | COUNT determines class breadth |
| PP composition vs B class mix | Cosine=0.995 | COMPOSITION irrelevant at class level |
| PP Count | Mean B Classes | n |
|----------|----------------|---|
| 0-2 | 19.0 | 171 |
| 3-5 | 30.9 | 805 |





| Dimension | Same-MIDDLE | Different-MIDDLE | p-value |
|-----------|-------------|------------------|---------|
| Position | Similar | Similar | 0.11 (NS) |
| Transitions | Similar | **Different** | <0.0001 |

**The "Chop vs Grind" Pattern:**


**Implication for PP composition:**



> PP profiles shape which token variants are available within surviving classes.




- PP composition → class survival: **FALSIFIED** (C506)
- PP composition → token configuration: **CONFIRMED** (C506.a)
- PP composition → behavioral variation: **CONFIRMED** (C506.b)


| Metric | Value | Interpretation |
|--------|-------|----------------|
| Spearman rho | **-0.294** | Moderate negative |
| p-value | **0.0015** | Highly significant |
**Two-axis HT model:**


- HT tracking PP content (composition doesn't matter per C506)



### Cross-References

| Constraint | Role |
|------------|------|
| C504 | PP count correlation (r=0.772) |
| C505 | A-side profile differences |
| C506 | Non-propagation to B |
| C507 | PP-HT partial substitution |
| C171 | Semantic ceiling protection |
| C469 | Categorical resolution |


---


## 0.C. THREE-LAYER CONSTRAINT ARCHITECTURE (MIDDLE_SUBCOMPONENT_GRAMMAR Phase)
### Tier 2-3: Architectural Discovery

> **The manuscript's symbol system operates through three independent constraint layers sharing a single substrate - construction, compatibility, and execution - which together achieve complex morphology, extreme vocabulary sparsity, AND execution safety simultaneously.**

- C085: 10 kernel primitives (s, e, t, d, l, o, h, c, k, r)
- C109: 17 forbidden transitions between token classes
- C475: 95.7% of MIDDLE pairs are incompatible
- C517: Superstring compression with hinge letters




| Metric | Value |
|--------|-------|
| Pearson correlation | r = -0.21 |
| p-value | 0.07 (not significant) |

         |
         |     - Directional asymmetry within tokens
         |     - One-way valve: e→h blocked (0.00), h→e favored (7.00x)
         |     - Result: Legal token forms
         |
         |     - MIDDLE atomic incompatibility
         |     - 95.7% of pairs forbidden
         |     - Result: Legal co-occurrence
         |

**Independence enables modularity:**

**Shared substrate enables compactness:**




**Directional Asymmetry (C521):**
| Transition | Ratio | Interpretation |
|------------|-------|----------------|
| e→h | 0.00 | STABILITY → PHASE: completely blocked |
| h→e | 7.00x | PHASE → STABILITY: highly favored |




- 85.4% contain multiple PP atoms (C516)


### Cross-References

| Constraint | Role |
|------------|------|
| C085 | 10 kernel primitives (shared substrate) |
| C109 | Execution hazards (execution layer) |
| C475 | MIDDLE incompatibility (compatibility layer) |
| C517 | Superstring compression (hinge letters) |
| C521 | Directional asymmetry (construction layer) |
| C522 | Layer independence (falsified isomorphism) |


---


## 0.D. RI LEXICAL LAYER HYPOTHESIS (RI_STRUCTURE_ANALYSIS Phase)
### Tier 3: Grammar vs Lexicon Distinction

> **RI extensions within MIDDLEs may function as a LEXICAL layer that anchors abstract grammar to specific external substances, while PREFIX/SUFFIX/PP remain purely functional markers operating as GRAMMAR.**

This extends C526 with a detailed characterization of the two-layer model.




| Layer | Components | Function | Semantic Status |
|-------|------------|----------|-----------------|
| **Grammar** | PREFIX, SUFFIX, PP atoms | Control-flow, procedural | No content (C120 applies) |
| **Lexicon** | RI extensions | Referential anchoring | Points to substances (THAT, not WHAT) |


**RI Localization Pattern:**
| Category | Percent | Avg Folios | Interpretation |
|----------|---------|------------|----------------|
| Strictly local (1 folio) | 87.3% | 1.0 | Specific material identifiers |
| Local (1-2 folios) | ~90% | 1.28 avg | Material identifiers |

**PREFIX/SUFFIX Versatility:**
| Affix | Different MIDDLEs | Role |
|-------|-------------------|------|
| ch | 57 | Global grammatical marker |
| sh | 29 | Global grammatical marker |

**Variation Pattern:**


**Interpretation:**


| Population | Count | % of RI |
|------------|-------|---------|
| PREFIX-REQUIRED | 334 | 50.1% |
| PREFIX-FORBIDDEN | 321 | 48.1% |



|     Examples: acp, afd, aiikh, akod, alda
|



| What | Status |
|------|--------|
| Grammar (PREFIX, SUFFIX, PP) | No semantic content - abstract functional positions |
| Lexicon (RI extensions) | REFERENTIAL content - points to substances |

**For the apparatus model:**

**For interpretation:**

**For the expert-oriented design:**

### What This Does NOT Claim

Universal Boundaries apply. Additionally:
- ❌ RI extensions are linguistic labels (the distinction is functional, not semantic)

**The distinction is functional, not semantic:** RI extensions POINT TO substances the way dictionary entries point to concepts - without encoding WHICH concepts.

### Cross-References

| Constraint | Role |
|------------|------|
| C120 | PURE_OPERATIONAL (applies to grammar, refined for lexicon) |
| C498 | RI vocabulary track (83% localized) |
| C475 | MIDDLE incompatibility (compatibility layer) |
| C509 | PP/RI dimensional separability |
| C517 | Superstring compression |
| C526 | RI Lexical Layer Hypothesis |



| Gallows | PP baseline | Observed in same record | Enrichment |
|---------|-------------|-------------------------|------------|
| k | 23.5% | 54.8% | 2.3x |
| t | 15.8% | 33.1% | 2.1x |
**Interpretation:**



**What this supports:**

**What this does NOT claim:**


**Topology is CONVERGENT (many-to-one):**


**Two Alternative Interpretations (cannot distinguish structurally):**
| Model | Logic | Meaning | Physical Analog |
|-------|-------|---------|-----------------|
| **AND (aggregation)** | Intersection | f93v requires ALL 5 conditions satisfied | Compound needing 5 ingredients |
| **OR (alternatives)** | Union | f93v accepts ANY of the 5 as valid input | 5 equivalent suppliers for same ingredient |
**Why the ambiguity matters:**

**Network Properties (Tier 2):**



**New Evidence Favoring OR (2026-01-30):**








---


## 0.E. B FOLIO AS CONDITIONAL PROCEDURE (CLASS_COMPATIBILITY_ANALYSIS Phase)
### Tier 3: Core Finding

> **Each B folio is a distinct procedure defined by unique vocabulary. Folio selection is external (human choice based on desired outcome). AZC modulates which core operations are available, creating conditional execution paths through the selected procedure.**

This upgrades "specific folio = specific recipe" from **NOT CLAIMED** (previous X.10 disclaimer) to **TIER 3 SUPPORTED**.

| Finding | Value | Constraint |
|---------|-------|------------|
| Folios with unique MIDDLE | **98.8%** (81/82) | C531 |
| Unique MIDDLEs that are B-exclusive | **88%** | C532 |

| Layer | Source | AZC Role | Function |
|-------|--------|----------|----------|
| **Core vocabulary** | Shared (41 MIDDLEs) | **Filtered** - determines what's legal | Control flow (~79% of tokens) |
| **Unique vocabulary** | B-exclusive (88%) | **Not filtered** - always available | Procedure identity (~21% of tokens) |










| Property | Evidence | Interpretation |
|----------|----------|----------------|
| Unique vocabulary | 98.8% have unique MIDDLEs | Each procedure has specific details |
| Same grammar | All use 49 classes (C121) | Shared control structure |


| Brunschwig | Voynich | Mapping |
|------------|---------|---------|
| Fire degree (1-4) | REGIME (1-4) | Completeness requirements |
| Recipe within degree | B folio within REGIME | Specific procedure |


### What This Does NOT Claim

Universal Boundaries apply. Additionally:
- ❌ Folio selection is encoded in the text (it's external/human)
- ❌ AZC "chooses" which folio runs

### What This DOES Claim (Tier 3)

- ✓ Each B folio is a distinct procedure (unique vocabulary defines it)
- ✓ Folio identity is independent of AZC (88% B-exclusive)
- ✓ AZC modulates execution paths, not procedure selection
- ✓ The manuscript is a conditional procedure library, not a sequential program
- ✓ Human operator selects folio based on external context





### Cross-References

| Constraint | Role |
|------------|------|
| C531 | Folio unique vocabulary prevalence |
| C532 | Unique MIDDLE B-exclusivity |
| C533 | Grammatical slot consistency |
| C534 | Section-specific profiles (partial) |
| C502 | A-record viability filtering |
| C470 | MIDDLE restriction inheritance |
| C121 | 49-class grammar universality |


---


## 0.E.1. GENERATIVE SUFFICIENCY AND DESIGN FREEDOM (Saturation Frontier)

### Tier 2: Core Finding

> **A minimal generative model (49-class Markov chain + symmetric forbidden suppression) reproduces 87% of measurable structure across 15 statistical tests, achieving 100% pass rate after three test corrections. The remaining ~57% of folio-level dynamical variance is genuine program-specific free variation that cannot be predicted from any aggregate structural property.**

### Generative Sufficiency (C1025, C1030, C1033, C1034)

The M2 model: sample instruction class from first-order transition probabilities, suppress forbidden transitions bidirectionally.

| Test Category | Tests | Pass Rate | Notes |
|---------------|-------|-----------|-------|
| Class distribution | 4 | 4/4 | Frequency, entropy, hapax |
| Transition structure | 4 | 4/4 | Spectral gap, forbidden compliance |
| Morphological | 4 | 4/4 | PREFIX, SUFFIX rates |
| Macro-state | 3 | 3/3 | After B4+C2+B5 corrections |
| **Total** | **15** | **15/15** | **100%** |

Three test corrections:
- **B4** (C1030): Test was misspecified for non-stationary data
- **C2** (C1033): Wrong CC class definition; class 17 has 59% suffixed tokens
- **B5** (C1034): Required symmetric (bidirectional) forbidden suppression, not asymmetric

PREFIX-factored generation (sampling PREFIX first, then class conditioned on PREFIX) is distributionally equivalent to M2 (C1034). PREFIX routing operates through selective inclusion (C1012), not through the generative process.

### Macro-Dynamics Variance Decomposition (C1017, C1035)

Folio-level AXM self-transition rate (how strongly each program orbits its dominant operational mode) decomposes as:

| Source | Variance | Cumulative |
|--------|----------|------------|
| REGIME + section | 42.0% | 42.0% |
| PREFIX entropy | 5.1% | 47.1% |
| Hazard density | 6.1% | 53.2% |
| Bridge geometry PC1 | 6.3% | 59.5% |
| **Residual (irreducible)** | **~57%** | **LOO-corrected** |

The C1017 model is moderately overfit (LOO CV R-squared = 0.433 vs training 0.564). The true explained fraction is ~43%.

Six additional folio-level predictors tested (paragraph count, HT density, gatekeeper fraction, QO fraction, vocabulary size, line count) all produce zero incremental variance beyond the baseline (C1035). Random forest finds no non-linear signal.

### Design Freedom Interpretation (C458, C980)

The ~57% residual is the **grammar's free design space**:
- Hazard exposure is clamped (CV = 0.04-0.11) — globally constrained
- Recovery strategy is locally free (CV = 0.72-0.82) — per-folio variation
- Each program is independently parameterized within its archetype
- The parameterization is not predictable from any aggregate structural property

This is consistent with C980's 66.3% free variation envelope. The manuscript provides the grammar, the forbidden constraints, and the macro-state topology. Within those constraints, each folio's author chose a specific operational style — and those choices are the irreducible residual.


---


## 0.F. LINE-LEVEL EXECUTION SYNTAX (CLASS_SEMANTIC_VALIDATION Phase)
### Tier 2-3: Execution Cycle Discovery

> **Each line follows a positional template: SETUP (initial) → THERMAL WORK (medial) → CHECKPOINT/CLOSURE (final). The 5 role categories (CC, EN, FL, FQ, AX) have distinct positional preferences, transition grammars, and REGIME/section profiles that collectively define line-level execution syntax.**

This fills a critical gap: we previously knew the VOCABULARY of operations (what roles exist) but not the SYNTAX (how they flow within a line).






### Key Structural Findings (C547-C562)

**Positional Grammar (C556):**

| Role | Initial Enrichment | Final Enrichment | Position |
|------|-------------------|------------------|----------|
| UNCLASSIFIED | 1.55x | 1.42x | Initial-biased |
| AUXILIARY | 0.97x | 0.79x | Initial-biased |
| ENERGY | **0.45x** | **0.50x** | **Medial-concentrated** |
| CORE_CONTROL | 1.16x | 0.83x | Initial-biased |
| FREQUENT | 0.70x | **1.67x** | **Final-biased** |
| FLOW | 0.73x | **1.65x** | **Final-biased** |

**Transition Grammar (C550):**

| Pattern | Finding |
|---------|---------|
| Self-chaining hierarchy | FREQUENT 2.38x > FLOW 2.11x > ENERGY 1.35x |
| FLOW-FREQUENT affinity | Bidirectional 1.54-1.73x |
| ENERGY transition asymmetry | Avoids FL (0.75x), FQ (0.71x), UN (0.80x) |

ENERGY operators preferentially chain with themselves (transition preference asymmetry), forming functionally coherent thermal sequences that avoid mixing with non-thermal roles.

**ENERGY/FLOW Anticorrelation (C551, C562):**

| Dimension | ENERGY | FLOW |
|-----------|--------|------|
| Position | Medial (0.45x initial) | Final (17.5%) |
| REGIME_1 | **Enriched** (1.26-1.48x) | **Depleted** (0.40-0.63x) |
| BIO section | **Enriched** (1.72x) | **Depleted** (0.83x) |
| PHARMA section | Class 33 depleted (0.20x) | **Enriched** (1.38x) |
| EN/FL ratio | REGIME_1: **7.57** | REGIME_2: **3.71** |

**CORE_CONTROL Hierarchy (C557, C558, C560):**


**or→aiin Directional Bigram (C561):**
| Expected (random) | Observed |
|-------------------|----------|
| aiin→aiin: 31% | **0%** |
| or→aiin: 22% | **87.5%** |

**FLOW Final Hierarchy (C562):**
| Class | Final% | Function |
|-------|--------|----------|
| 40 (ary, dary, aly) | 59.7% | Strong closers |
| 38 (aral, aram) | 52.0% | Strong closers |

**Section Profiles (C552, C553, C555):**
| Section | Signature | Profile |
|---------|-----------|---------|
| BIO | +CC +EN (45.2% ENERGY) | Thermal-intensive processing |
| HERBAL_B | +FQ -EN (1.62x FREQUENT) | Repetitive non-thermal cycles |

### Tier 3-4: Distillation Cycle Interpretation

The line-level execution syntax maps directly to a distillation control cycle:

| Line Phase | Structural Evidence | Distillation Interpretation |
|------------|--------------------|-----------------------------|
| **SETUP** (initial) | daiin 27.7% initial, 47.1% ENERGY followers (C557) | "Begin heating sequence" - operator initiates fire |
| **WORK** (medial) | ENERGY chains, qo↔ch-sh interleaving at 56.3% (C549, C550) | Sustained thermal processing: heat (ch-sh) → vent/monitor (qo) → heat again |
| **CHECK** (medial-final) | or→aiin bigram, 87.5% directional (C561) | Sensory checkpoint - "taste and scent" verification |
| **CLOSE** (final) | FLOW hierarchy, ary 100% final (C562) | Completion: provisional (ar) to absolute (ary) |

**REGIME as operational mode:**

| REGIME | EN/FL Ratio | Interpretation |
|--------|-------------|----------------|
| REGIME_1 | 7.57 | Active heating mode (Brunschwig first degree) |
| REGIME_2 | 3.71 | Cooling/collection mode (second degree) |
| REGIME_3 | 5.04 | Intervention mode (third degree) |
| REGIME_4 | 4.76 | Precision mode (controlled execution) |

**Section as procedural type:**

| Section | Thermal Intensity | Distillation Parallel |
|---------|-------------------|-----------------------|
| BIO (45% ENERGY) | Maximum | Hot bath distillation (balneum mariae) |
| HERBAL (FREQUENT-enriched) | Low | Maceration/infusion (cold processing) |
| PHARMA (FLOW-dominated) | Moderate | Controlled condensation/collection |

**Brunschwig's fire-degree cycle now maps to line structure:**
| Brunschwig Phase | Voynich Line Position | Key Marker |
|------------------|-----------------------|------------|
| "First degree - initiate heat" | Initial zone | daiin (trigger) |
| "Second/third degree - work" | Medial zone | ENERGY chains, qo↔ch-sh |


| Before CLASS_SEMANTIC_VALIDATION | After |
|----------------------------------|-------|
| Knew token decomposition (PREFIX+MIDDLE+SUFFIX) | Now know how tokens FLOW within lines |
| Knew roles existed (CC, EN, FL, FQ, AX) | Now know roles have positional grammar |
### What This Does NOT Claim

Universal Boundaries apply. Additionally:
- That or→aiin literally means "sensory test"
- That daiin literally means "begin heating"

The interpretation is STRUCTURAL, not semantic: line-level syntax exhibits a cycle structure consistent with thermal processing.

### Cross-References

| Constraint | Role |
|------------|------|
| C547 | qo-chain REGIME_1 enrichment |
| C548 | Manuscript-level gateway/terminal envelope |
| C549 | qo/ch-sh interleaving significance |
| C550 | Role transition grammar (ENERGY asymmetry) |
| C551 | Grammar universality, REGIME specialization |
| C552 | Section-specific role profiles |
| C553 | BIO-REGIME independence |
| C554 | Hazard class clustering |
| C555 | PHARMA thermal operator substitution |
| C556 | ENERGY medial concentration |
| C557 | daiin line-initial ENERGY trigger |
| C558 | Singleton class structure |
| C559 | FREQUENT role structure **(SUPERSEDED by C583, C587 — used wrong FQ membership)** |
| C560 | Class 17 ol-derived operators |
| C561 | or→aiin directional bigram |
| C562 | FLOW role structure |


---


## 0.G. THE SCAFFOLD AND THE SHADOW (AX_FUNCTIONAL_ANATOMY Phase)
### Tier 3-4: What the Other 28% Was Doing All Along

For months, one-fifth of the instruction classes sat in a bucket labeled AUXILIARY — 480 tokens, 20 classes, 28.4% of everything Currier B ever wrote — and nobody could say what they *did*. They weren't ENERGY. They weren't FLOW. They weren't CONTROL or FREQUENT. They were just... there. Structurally present, positionally real (C563-C566 proved they had INIT/MED/FINAL sub-positions with p=3.6e-47), but functionally invisible. The grammar had a heartbeat and a skeleton and a nervous system, and then this enormous quiet mass of tissue that nobody could name.

It turns out we were looking at the problem backwards.

We kept asking: *What does AUXILIARY do that the other roles don't?* The answer is nothing. AX doesn't do anything the other roles don't do. It uses the same vocabulary, drawn from the same pipeline, carrying the same material identity. The difference isn't in the vocabulary. The difference is in the *prefix*.




























| Constraint | Finding | Key Number |
|------------|---------|------------|
| C567 | AX MIDDLEs overlap with operational roles | 72% shared, Jaccard=0.400 |
| C568 | AX vocabulary present in nearly all pipeline contexts | 97.2% A-records, 0 zero-AX B-contexts |
---


## 0.H. ENERGY ANATOMY (EN_ANATOMY Phase)

### Tier 2: EN Internal Architecture

> **EN comprises 18 instruction classes (not 11 as BCSC stated), accounting for 7,211 tokens (31.2% of B). Internally, EN classes show DISTRIBUTIONAL_CONVERGENCE — grammatically equivalent but lexically partitioned by PREFIX family. EN is 100% pipeline-derived and has 30 exclusive MIDDLEs.**

This resolves the EN undercount (BCSC v1.2 listed 11 classes) and completes the EN role characterization.

### The 18-Class Census (C573)

ICC-based definitive count: {8, 31-37, 39, 41-49}. Core 6 classes provide 79.5% of EN tokens; Minor 12 provide 20.5%. The discrepancy with BCSC's 11-class count arose because the original grammar analysis used a coarser clustering.

### Distributional Convergence (C574)

The 18 EN classes do NOT form distinct behavioral clusters. Best clustering: k=2, silhouette=0.180. QO-prefixed and CHSH-prefixed classes have identical positions, REGIME profiles, and context distributions (JS divergence = 0.0024). But their MIDDLE vocabularies are nearly disjoint: QO uses 25 MIDDLEs, CHSH uses 43, only 8 shared (Jaccard=0.133, C576).

**Verdict:** EN is grammatically equivalent but lexically partitioned. PREFIX selects which material subvocabulary to use, not what grammatical function to perform. The QO/CHSH split (C276, C423) operates within a single role, not between roles.

### Pipeline Purity (C575)

All 64 unique EN MIDDLEs are PP (pipeline-participating). Zero RI, zero B-exclusive. EN is the purest role — even purer than AX (98.2% PP). The entire EN vocabulary traces back to Currier A.

### Content-Driven Interleaving (C577)

QO and CHSH occupy the same positions (p=0.104, not significantly different). Alternation is driven by material-type selection (BIO 58.5%, PHARMA 27.5%), not positional preferences.

### Exclusive Vocabulary (C578)

EN has 30 exclusive MIDDLEs — 46.9% of its vocabulary is not shared with AX, CC, FL, or FQ. This is a dedicated content subvocabulary within the pipeline.

### Trigger Profile Differentiation (C580)

CHSH is triggered by AX (32.5%) and CC (11%). QO is triggered by EN-self (53.5%) and boundary contexts (68.8%). Chi2=134, p<0.001. The two PREFIX families enter EN through different grammatical pathways.

### Evidence Summary (C573-C580)

| Constraint | Finding | Key Number |
|------------|---------|------------|
| C573 | EN definitive count | 18 classes (not 11) |
| C574 | Distributional convergence | silhouette=0.180, JS=0.0024 |
| C575 | 100% pipeline-derived | 64 MIDDLEs, all PP |
| C576 | MIDDLE vocabulary bifurcation | QO 25, CHSH 43, 8 shared |
| C577 | Interleaving is content-driven | Position p=0.104 (NS) |
| C578 | 30 exclusive MIDDLEs | 46.9% of EN vocabulary |
| C579 | CHSH-first ordering bias | 53.9%, p=0.010 |
| C580 | Trigger profile differentiation | chi2=134, p<0.001 |


---


## 0.I. SMALL ROLE ANATOMY AND FIVE-ROLE SYNTHESIS (SMALL_ROLE_ANATOMY Phase)
### Tier 2: Complete Role Taxonomy

> **The 49 Currier B instruction classes partition into 5 roles — CC (3-4 classes), EN (18), FL (4), FQ (4), AX (19-20) — with complete coverage. All roles are 100% PP (AX 98.2%). Small roles (CC, FL, FQ) show GENUINE internal structure; large roles (EN, AX) are COLLAPSED or CONVERGENT. Suffix usage is strongly role-stratified (chi2=5063.2). FL is hazard-source-biased; EN is hazard-target.**

This phase completes the five-role taxonomy by characterizing the three small operational roles (CC, FL, FQ), resolving census discrepancies, introducing the suffix dimension, and producing a unified cross-role comparison.

### Census Resolution (C581-C583)

Three long-standing discrepancies resolved:

| Role | Resolved Classes | Tokens | % of B | Note |
|------|-----------------|--------|--------|------|
| CC | {10, 11, 12, 17} | ~1,023 | 4.4% | Class 12 ghost (0 tokens, C540); Class 17 per C560 |
| FL | {7, 30, 38, 40} | 1,078 | 4.7% | BCSC undercounted at 2; ICC gives 4 |
| FQ | {9, 13, 14, 23} | 2,890 | 12.5% | C559 used wrong set {9,20,21,23} — SUPERSEDED |

**Resolved (2026-01-26):** Class 14 = FQ per ICC phase20a + behavioral evidence (suffix rate 0.0 vs AX_MED 0.56–1.0; token count 707 vs AX_MED 38–212; JS divergence 0.0018 with FQ Class 13). Class 17 = CC per C560. AX corrected from 20 to 19 classes. C563 updated.


| Role | Classes | KW Significant | Verdict |
|------|---------|---------------|---------|
| CC | 2 active | 75% | GENUINE_STRUCTURE |
| FL | 4 | 100% | GENUINE_STRUCTURE |



| Stratum | Role | Suffix Types | Bare Rate |
|---------|------|-------------|-----------|
| SUFFIX_RICH | EN | 17 | 39.0% |
| SUFFIX_MODERATE | AX | 19 | 62.3% |



| Subgroup | Classes | Mean Position | Final Rate | Hazard Role |
|----------|---------|--------------|------------|-------------|
| Hazard | {7, 30} | 0.55 | 12.3% | Source (4.5x initiation bias) |
| Safe | {38, 40} | 0.81 | 55.7% | Non-hazardous |


| Class | Tokens | Character | Distinctive Feature |
|-------|--------|-----------|-------------------|
| 9 | 630 | aiin/o/or | Medial self-chaining, prefix-free |
| 13 | 1,191 | ok/ot+suffix | Largest FQ class, 16% suffixed |



| Property | CC | EN | FL | FQ | AX |
|----------|-----|-----|-----|-----|-----|
| Classes | 3-4 | 18 | 4 | 4 | 19-20 |
| Tokens | 735-1023 | 7,211 | 1,078 | 2,890 | 4,559 |

| Layer | Role | Function | Distillation Parallel |
|-------|------|----------|----------------------|
| Frame | AX | Positional template | Apparatus arrangement |
| Signal | CC | Control primitives | Operator hand signals |


| Constraint | Finding | Key Number |
|------------|---------|------------|
| C581 | CC definitive census | {10,11,12,17} — Class 17 confirmed CC per C560 |
| C582 | FL definitive census | {7,30,38,40}, 4 classes (was 2) |
---


## 0.J. FQ INTERNAL ARCHITECTURE (FQ_ANATOMY Phase)

### Tier 2: FQ 3-Group Structure

> **FQ's 4 classes form 3 functional groups: CONNECTOR {9}, PREFIXED_PAIR {13, 14}, CLOSER {23}. Classes 13 and 14 have completely non-overlapping MIDDLE vocabularies (Jaccard=0.000). Internal transitions follow a directed grammar (chi2=111, p<0.0001). Class 23 is a boundary specialist with 29.8% final rate. FQ-FL symbiosis is position-driven, not hazard-mediated.**

This phase deepens the FQ characterization from SMALL_ROLE_ANATOMY (C587) by examining internal vocabulary, transitions, and upstream context.

### 3-Group Structure (C593)

Silhouette analysis yields 3 groups (silhouette=0.68):
- **CONNECTOR** {9}: or/aiin bigram, medial self-chaining, prefix-free. Functions as the operational connector between EN blocks.
- **PREFIXED_PAIR** {13, 14}: ok/ot-prefixed classes, the bulk of FQ (1,898 tokens). Share PREFIX family but differ completely in MIDDLE vocabulary.
- **CLOSER** {23}: morphologically minimal (d/l/r/s/y), final-biased. Terminates sequences.

### Complete 13-14 Vocabulary Bifurcation (C594)

Classes 13 and 14 share zero MIDDLEs (Jaccard=0.000). This is sharper than EN's QO/CHSH split (Jaccard=0.133). Class 13 has 18.2% suffix rate; Class 14 has 0%. Despite sharing the ok/ot PREFIX family, they access completely different content vocabularies — the most extreme vocabulary segregation in the corpus.

### Internal Transition Grammar (C595)

FQ internal transitions are non-random (chi2=111, p<0.0001):
- 23->9 enriched 2.85x (closer feeds connector)
- 9->13 vs 9->14 ratio is 4.6:1 (connector preferentially feeds Class 13)
- 13->23 enriched (Class 13 feeds closer to terminate)

### FQ-FL Symbiosis (C596)

FQ and FL co-occur in positionally structured patterns, but hazard alignment is non-significant (p=0.33). The symbiosis is position-driven — both roles concentrate at line boundaries — not hazard-mediated. FQ does not preferentially pair with hazardous FL classes.

### Class 23 Boundary Dominance (C597)

Class 23 has the highest final rate of any FQ class (29.8%) and accounts for 39% of all FQ line-final tokens despite being only 12.5% of FQ by count. Mean run length 1.19 — almost always appears as a singleton. It functions as a dedicated boundary marker.

### Tier 3 Interpretation

FQ implements **iteration control** within the line grammar:
- CONNECTOR (Class 9) chains operational blocks — the "and then" between EN sequences
- PREFIXED_PAIR (13, 14) provides parameterized repetition with two completely different content vocabularies (possibly different iteration modes or targets)
- CLOSER (23) terminates sequences — the "stop" signal

The 13-14 complete bifurcation suggests two distinct iteration pathways sharing a common structural frame (ok/ot PREFIX) but accessing different material specifications.

### Evidence Summary (C593-C597)

| Constraint | Finding | Key Number |
|------------|---------|------------|
| C593 | FQ 3-group structure | silhouette=0.68 |
| C594 | Complete 13-14 vocabulary bifurcation | Jaccard=0.000 |
| C595 | Internal transition grammar | chi2=111, p<0.0001 |
| C596 | FQ-FL position-driven symbiosis | hazard p=0.33 (NS) |
| C597 | Class 23 boundary dominance | 29.8% final, 39% of FQ finals |


---


## 0.K. SUB-ROLE INTERACTION GRAMMAR (SUB_ROLE_INTERACTION Phase)

### Tier 2: Cross-Boundary Sub-Group Routing

> **Internal sub-groups of each role interact non-randomly across role boundaries. 8/10 cross-role pairs show significant sub-group routing (5 survive Bonferroni). CC sub-groups are differentiated triggers: daiin/ol activate EN_CHSH while ol-derived activates EN_QO. All 19 hazard events originate from exactly 3 sub-groups (FL_HAZ, EN_CHSH, FQ_CONN). REGIME modulates routing magnitude but not direction.**

This phase connects the role-level transition grammar (C550) with the internal anatomy of each role, testing whether sub-group identity is visible across role boundaries.

### Cross-Boundary Structure (C598)

13 sub-groups across 5 roles (EN: QO/CHSH/MINOR; FQ: CONN/PAIR/CLOSER; FL: HAZ/SAFE; AX: INIT/MED/FINAL; CC: DAIIN/OL/OL_D) produce 10 testable cross-role pairs. 8/10 are significant raw, 5/10 survive Bonferroni. Strongest: CC->EN (chi2=104, p=2.5e-20), FQ->EN (chi2=35, p=3.5e-8).

### CC Trigger Selectivity (C600)

The sharpest finding. CC sub-groups are **differentiated triggers** (chi2=129.2, p=9.6e-21):
- **daiin** (Class 10) and **ol** (Class 11): trigger EN_CHSH at 1.60-1.74x, suppress EN_QO to 0.18x
- **ol-derived** (Class 17): triggers EN_QO at 1.39x, suppresses EN_CHSH to 0.77x

This refines C557 ("daiin opens lines") to "daiin specifically opens the CHSH pathway." The QO pathway has a completely different upstream activator.

### AX Scaffolding Routing (C599)

AX sub-positions route differently to operational sub-groups (chi2=48.3, p=3.9e-4):
- AX_INIT feeds QO at 1.32x
- AX_FINAL avoids QO (0.59x) and feeds FQ_CONN (1.31x)
- AX is not a uniform frame — it is a directional routing mechanism

### Hazard Sub-Group Concentration (C601)

All 19 corpus hazard events originate from exactly 3 source sub-groups: FL_HAZ (47%), EN_CHSH (26%), FQ_CONN (26%). EN_CHSH absorbs 58% of hazard targets. EN_QO never participates — zero as source, zero as target. This confirms the QO/CHSH bifurcation is functional, not just lexical.

### REGIME-Conditioned Routing (C602)

4/5 tested cross-role pairs are REGIME-dependent (homogeneity p<0.05). The exception is AX->FQ which is REGIME-independent (p=0.86), consistent with AX being structural scaffolding rather than content-sensitive. REGIME modulates magnitude but never flips direction — FQ_CONN always feeds CHSH in every REGIME.

### Tier 3 Interpretation: Two Parallel Processing Lanes

The sub-role interaction data reveals **two parallel processing pathways**:

```
CC_DAIIN/OL  --triggers-->  EN_CHSH  --feeds-->  FQ_CONN
                                                    |
                                             (hazard loop)
                                                    |
CC_OL_D      --triggers-->  EN_QO    --feeds-->  FQ_PAIR
                                                 (safe)
```

- **CHSH lane:** Triggered by daiin/ol, carries hazardous operations, uses connector routing
- **QO lane:** Triggered by ol-derived compounds, carries safe operations, uses prefixed pair routing
- **AX scaffolding:** Routes differentially — INIT feeds QO, FINAL feeds CONN

In the apparatus-centric model: daiin opens a hazardous processing sequence (high-temperature distillation, reactive materials), while ol-derived compounds open a safe processing sequence (routine operations, stable materials). The two lanes share grammar but access different vocabularies and carry different risk profiles.

### Evidence Summary (C598-C602)

| Constraint | Finding | Key Number |
|------------|---------|------------|
| C598 | Cross-boundary sub-group structure | 8/10 significant, 5/10 Bonferroni |
| C599 | AX scaffolding routing | chi2=48.3, p=3.9e-4 |
| C600 | CC trigger sub-group selectivity | chi2=129.2, p=9.6e-21 |
| C601 | Hazard sub-group concentration | 3 sources, QO never participates |
| C602 | REGIME-conditioned sub-role grammar | 4/5 REGIME-dependent, AX->FQ exception |


---


## 0.L. LANE CONTROL ARCHITECTURE (LANE_CHANGE_HOLD_ANALYSIS Phase)
### Tier 3: Core Finding

> **The two EN execution lanes (QO/CHSH) encode complementary control functions — energy application and stabilization — that alternate with inertia-driven dynamics within a phase-gated legality framework. Thresholds are categorical (legality transitions), not numeric (accumulation values).**


| Lane | PREFIX | MIDDLE Character | Kernel Content | Hazard Role | Post-Hazard |
|------|--------|-----------------|----------------|-------------|-------------|
| **QO** | qo- | k-rich (70.7%) | ENERGY_MODULATOR | Zero participation (C601) | 24.8% (depleted) |
| **CHSH** | ch-/sh- | e-rich (68.7%) | STABILITY_ANCHOR | All 19 forbidden transitions | 75.2% (dominant) |





**Switching dynamics are inertia-driven, not threshold-driven:**
| Run Length N | QO P(switch) | CHSH P(switch) |
|-------------|-------------|---------------|
| 1 | 0.500 | 0.482 |
| 2 | 0.438 | 0.417 |



| Threshold | Mechanism | Evidence |
|-----------|-----------|----------|
| **Lower bound** | Aggression categorically forbidden in 20.5% of folios | C490: zero AGGRESSIVE compatibility, not low probability |
| **Upper bound** | Stabilization is absorbing (e->h = 0.00) | C521: kernel one-way valve; once stable, can't destabilize |



### Constraints Produced

| # | Name | Tier |
|---|------|------|
| C643 | Lane Hysteresis Oscillation | 2 |
| C644 | QO Transition Stability | 2 |
| C645 | CHSH Post-Hazard Dominance | 2 |
| C646 | PP-Lane MIDDLE Discrimination | 2 |
| C647 | Morphological Lane Signature | 2 |

### Fits Produced

| ID | Name | Tier | Result |
|----|------|------|--------|
| F-B-004 | Lane Hysteresis Control Model | F2 | SUCCESS |
| F-B-005 | PP-Lane MIDDLE Discrimination | F2 | SUCCESS |
| F-B-006 | Energy/Stabilization Lane Assignment | F3 | PARTIAL |



























**Independence findings:**
- **No vocabulary coupling** (C670): adjacent lines share no more MIDDLEs than random (Jaccard obs=0.140, 0/79 folios significant)
- **No CC trigger memory** (C673): CC type re-selected independently each line (permutation p=1.0)
- **No lane balance memory** (C674): QO fraction autocorrelation is entirely folio-driven (raw lag-1 rho=0.167 but permutation p=1.0; lag-2/3 stronger than lag-1, confirming folio clustering not sequential propagation)
**Structural findings:**
- **Vocabulary is front-loaded** (C671): 87.3% of folios introduce >60% of unique MIDDLEs in first half of lines
- **Line boundaries are grammar-transparent** (C672): boundary entropy 7.4% lower than within-line (H_boundary=4.28 vs H_within=4.63)
- **MIDDLE identity is position-stable** (C675): JSD Q1-Q4=0.081, only 4/135 MIDDLEs positionally biased
- **Morphological mode evolves** (C676): PREFIX chi2 p=3.7e-9, suffix chi2 p=1.7e-7; qo PREFIX declines late, bare suffix increases
- **Lines simplify late** (C677): unique tokens rho=-0.196 (p<1e-21), but TTR flat at 0.962 — concision, not repetition
- **No discrete line types** (C678): best KMeans silhouette=0.100, continuous variation across 27 features
- **Weak adjacent coupling** (C679): consecutive lines +3.1% more similar than random (p<0.001), but mild


---


## 0.M. B PARAGRAPH AND FOLIO STRUCTURE (Annotation-Derived)
### Tier 3: Core Finding

> **B folios are sequential procedures where paragraphs represent named operations executed in order. Early paragraphs concentrate identification vocabulary (HT), middle paragraphs concentrate processing (QO/CHSH), and late paragraphs show terminal vocabulary signature (AX clustering + TERMINAL FL). Lines with HT at both boundaries mark explicit state transitions.**

This interpretation derives from detailed line-by-line annotation of 10 Currier B folios (f41v, f43r, f43v, f46r, f46v, f103r, f103v, f104r, f104v, f105r) totaling ~350 lines with token-level role classification.


| Position | HT Density | Dominant Roles | FL Profile | Line Length |
|----------|------------|----------------|------------|-------------|
| **Early** (L2-L10) | HIGH (4 HT in L10) | INFRA LINE-INITIAL, QO/CHSH processing | ar (INITIAL) | Normal (10-12) |
| **Middle** (L11-L25) | VARIABLE (0-4 per line) | Heavy QO LANE, DOUBLED patterns | Mixed | Some SHORT (4-6) |




| Folio | Line | Pattern | Example |
|-------|------|---------|---------|
| f105r | L29 | HT CONSECUTIVE at both ends | oleedar...cheolkary |
| f105r | L18 | HT bracketing | dsechey...aiiral |






| Observation | Brunschwig Parallel |
|-------------|---------------------|
| Paragraphs as named operations | Brunschwig organizes by operation (maceration, distillation, rectification) |
| Early = identification heavy | Recipe headers identify materials/process |

| FL Stage | Tokens | Mean Position | Interpretation |
|----------|--------|---------------|----------------|
| INITIAL | ar, r | 0.30-0.51 | Early material state |
| LATE | al, l, ol | 0.61 | Intermediate state |


| Pattern | Frequency | Note |
|---------|-----------|------|
| HT LINE-INITIAL | Common | Identification at block entry |
| HT LINE-FINAL | Common | State marking at block exit |
### What This Does NOT Claim

Universal Boundaries apply. Additionally:
- ❌ Paragraph boundaries are syntactically marked (they're visual)
- ❌ All folios have identical paragraph structure
- ❌ The progression is strictly monotonic

### What This DOES Claim (Tier 3)

- ✓ B folios have internal sequential structure (not random token distribution)
- ✓ Vocabulary distribution correlates with folio position
- ✓ Terminal paragraphs have distinctive signature (AX + TERMINAL FL + SHORT)
- ✓ HT bracket patterns mark state transitions
- ✓ This structure is consistent with sequential procedural documentation


| Structural Finding | Control-Loop Interpretation |
|-------------------|----------------------------|
| Line = SETUP→WORK→CHECK→CLOSE | Line = one control cycle |
| Paragraph = operation | Paragraph = series of related control cycles |

---


## I. Human Track (HT) Interpretation
### Tier 2: Core Finding (v2.13)

> **HT is a scalar signal of required human vigilance that varies with content characteristics, not with codicology, singular hazards, or execution failure modes.**

HT functions as **anticipatory vigilance** - preparing the human operator for upcoming demands rather than reacting to past events (C459).



### Tier 3: Dual-Purpose Attention Mechanism

HT may serve **two complementary functions**:

1. **Anticipatory vigilance** during high-demand phases
2. **Guild training** in the art of the written form

This is NOT "doodling" or "scribbling" - the evidence shows deliberate skill acquisition.

| Evidence | Finding | Implication |
|----------|---------|-------------|
| Rare grapheme engagement | 7.81x over-representation | Practicing difficult forms |
| Run structure | CV=0.35 (fixed-block range) | Deliberate practice blocks |
| System | Anchoring Pressure | Pattern |
|--------|-------------------|---------|
| Currier A | Registry layout | Entry-boundary aligned |
| Currier B | Temporal/attentional context | Waiting-profile correlated |

---


## I.A. HT Morphological Curriculum (Tier 3 Characterization)

> HT morphological choices follow a curriculum structure: systematic introduction of grapheme families, spaced repetition of difficult forms, and complexity progression within practice blocks.
| Test | Verdict | Key Finding |
|------|---------|-------------|
| 1. Introduction Sequencing | **STRONG PASS** | All 21 families in first 0.3% (KS=0.857) |
| 2. Spaced Repetition | UNDERPOWERED | Insufficient rare-but-repeated tokens |



> HT morphological patterns exhibit vocabulary front-loading (all families established in first 0.3%), significant prerequisite relationships (26 pairs vs 10.5 expected), and quasi-periodic family rotation. This is consistent with a "vocabulary-first" curriculum structure distinct from gradual introduction.


---


## I.B. Four-Layer Responsibility Model (v2.13)
### Tier 2: Structural Finding

The manuscript distributes responsibility between system and human across four layers:

| Layer | Role | What It Handles |
|-------|------|-----------------|
| **Currier B** | Constrains you | Execution grammar, safety envelope |
| **Currier A** | Discriminates for you | Fine distinctions at complexity frontier |
| **AZC** | Encodes position | Phase-indexed positional encoding, compatibility grouping |
| **HT** | Prepares you | Anticipatory vigilance signal |


| Dimension | Allowed to Vary? | Evidence |
|-----------|-----------------|----------|
| Hazard exposure | NO | CV = 0.11 (clamped) |
| Intervention diversity | NO | CV = 0.04 (clamped) |
### Tier 3: Interpretive Framing

The right mental model is not "What does this page tell me to do?" but:

> **"How much of the problem is the system handling for me here, and how much vigilance am I responsible for?"**

This suggests the manuscript is a **manual of responsibility allocation** rather than a manual of actions. The grammar guarantees safety by construction; the system guarantees risk will not exceed bounds; HT signals when human attention is required.

---


## I.C. AZC as Decision-Point Grammar (C437-C444)
### Tier 2: Structural Findings

AZC serves as a **positional encoding system** where each PREFIX+MIDDLE has exactly one fixed position:

| Finding | Evidence | Constraint |
|---------|----------|------------|
| Folios maximally orthogonal | Jaccard = 0.056 | C437 |
| Practically complete basis | 83% per-folio coverage | C438 |
| Folio-specific HT profiles | 18pp escape variance | C439 |
| Uniform B sourcing | 34-36 folios per B | C440 |
| Vocabulary-activated constraints | 49% A-types in 1 folio | C441 |
| Compatibility grouping | 94% unique vocabulary | C442 |

### Tier 3: Operational Interpretation

**Core insight:** AZC encodes vocabulary position; each PREFIX+MIDDLE has one fixed position reflecting its operational character.

| System | Function | Type |
|--------|----------|------|
| Currier A | WHAT exists | Static registry |
| Currier B | HOW to respond | State-triggered interventions |
| AZC | WHEN to decide | Decision grammar |

**Note (C171 clarification, v4.37):** "HOW to respond" means state-triggered interventions, NOT sequential steps. B tokens are control actions selected based on assessed system state, following a MONITOR→ASSESS→SELECT→EXECUTE→RETURN cycle. See MODEL_CONTEXT.md Section VI.


| Diagram Position | Workflow Phase | Escape Rate | Meaning |
|------------------|----------------|-------------|---------|
| C | Core/Interior | ~1.4% | Moderate flexibility |
| R1→R2→R3 | Progression | 2.0%→1.2%→0% | Options narrowing, committing |



**Precise Definition (C442 refined):**
> Two AZC folio vocabularies are compatible iff there exists at least one Currier A entry whose vocabulary bridges both.
**Empirical Test (2026-01-12):**
| Metric | Value |
|--------|-------|
| Total folio pairs | 435 |
| Bridged pairs | 390 (89.7%) |
**Family-Level Coherence:**
| Family Type | % Unbridged | Interpretation |
|-------------|-------------|----------------|
| Within-Zodiac | **0.0%** | Interchangeable discrimination contexts |
| Within-A/C | **14.7%** | True fine-grained alternatives |
**Key Corollaries:**
- Folios are NOT execution-exclusive (C440 still holds)

**f116v Structural Isolation:**




| Family | Scaffold | HT Oscillation | Interpretation |
|--------|----------|----------------|----------------|
| Zodiac (15 folios) | Uniform (same 12x) | 0.060 (low) | Coarse discrimination, sustained flow |
| A/C (21 folios) | Varied (unique each) | 0.110 (high) | Fine discrimination, punctuated checkpoints |
**Final Interpretation (Tier 3 - VALIDATED):**
> Zodiac and A/C AZC families correspond to regimes of perceptual discrimination complexity rather than operational difficulty. Zodiac contexts permit coarse categorization and sustained attentional flow, while A/C contexts require finer categorical distinctions, producing punctuated attentional checkpoints reflected in higher HT oscillation. Execution grammar absorbs this difference, resulting in no detectable change in behavioral brittleness or CEI.
**Empirically Tested (2026-01-11):**
| Test | Result |
|------|--------|
| MIDDLE Discrimination Gradient | WEAK SUPPORT (5/15 prefixes) |
| Residual Brittleness | FAILED (effect is PREFIX, not regime) |
**The Coherent Explanatory Axis:**
| Layer | Zodiac | A/C |
|-------|--------|-----|
| Currier A | Coarse categories | Fine distinctions |
| AZC | Uniform scaffolds | Varied scaffolds |
> **Where discrimination is fine, attention becomes punctuated; where discrimination is coarse, attention can flow.**
**Falsified Variants:**




| Cluster | Family Bias | Sample Tokens | Shared Folios |
|---------|-------------|---------------|---------------|
| 66 | 85.7% Zodiac | ytaly, opaiin, alar | f72v1, f73v |
| 61 | 69.7% A/C | okeod, ykey, ykeeody | f69v, f73v |


**Contrast with regime-committed prefixes:**


> **AZC is a decision-point grammar that transforms static material references into phase-gated choice nodes, enforces compatibility between materials and operations, and encodes when intervention is legal versus when outcomes must be accepted.**
---


## I.D. MIDDLE Atomic Incompatibility Layer (C475)
### Tier 2: Core Finding

> **MIDDLE-level compatibility is extremely sparse (4.3% legal), forming a hard incompatibility lattice. This is the atomic discrimination layer—everything above it (A entries, AZC folios, families, HT) is an aggregation of this graph.**

| Metric | Value |
|--------|-------|
| Total MIDDLEs | 1,187 |
| Total possible pairs | 703,891 |


**3. PREFIX = soft prior, MIDDLE = hard constraint**


> The space is globally navigable, but only by changing discrimination regime step-by-step.
| Prior Finding | Resolution |
|---------------|------------|
| C293 (MIDDLE is primary discriminator) | **Quantified**: 95.7% exclusion rate |
| C423 (PREFIX-bound vocabulary) | PREFIX is first partition, MIDDLE is sharper second |
### Tier 3: Interpretive Implications

**Why This Matters:**

This explains several long-standing puzzles at once:
- Why AZC folios had to be so numerous (enumerating compatibility classes)
- Why Currier A appears both flat AND highly constrained
- Why HT tracks discrimination pressure rather than execution danger
- Why vocabulary sharing ≠ combinability

**What Kind of System This Is:**

> A globally navigable but locally forbidden discrimination space — the strongest internal explanation yet of why the Voynich Manuscript looks the way it does without invoking semantics.

**Bayesian Modeling Progress:**

1. ~~**Latent Discrimination Axes**~~ — **DONE: K=128 for 97% AUC** (see I.E below)
2. ~~**Probabilistic A Bundle Generator**~~ — **DONE: 9/14 metrics FAIL** (see I.F below)
3. ~~**Coverage Optimality**~~ — **DONE: 100% coverage, 22.3% hub savings** (see I.G below)
4. ~~**HT Variance Decomposition**~~ — **DONE: R²=0.28, TAIL PRESSURE dominant** (see I.H below)
5. ~~**Temporal Coverage Trajectories**~~ — **DONE: STRONG SCHEDULING with pedagogical pacing** (see I.I below)



| K | Cross-Validation AUC |
|---|----------------------|
| 2 | 0.869 |
| 4 | 0.870 |
**Key Findings:**

**Interpretation (Tier 3):**

> **The MIDDLE vocabulary is not a categorization system with a few dimensions. It is a rich feature space where each variant has a unique 128-dimensional fingerprint.**
**What This Means for Generative Modeling:**

**Hub Confirmation:**
| MIDDLE | Degree |
|--------|--------|
| 'a' | 2047 |
| 'o' | 1870 |




**Generator Configuration:**

**Diagnostic Results:**
| Metric | Real | Synthetic | Verdict |
|--------|------|-----------|---------|
| lines_zero_mixing | 61.5% | 2.7% | **FAIL** |
| pure_block_frac | 46.9% | 2.7% | **FAIL** |
**Residual Interpretation (New Structure):**

**Interpretation (Tier 3):**
> **Incompatibility + priors are NECESSARY but NOT SUFFICIENT.** The generator reveals at least four additional structural principles: PREFIX coherence, tail forcing, repetition structure, and hub rationing.



**The Test:**
| Model | Coverage | Hub Usage | Verdict |
|-------|----------|-----------|---------|
| **Real A** | **100%** | **31.6%** | **OPTIMAL + HUB RATIONING** |
| Greedy | 100% | 53.9% | Optimal but hub-heavy |
**Key Insight:**

> **Currier A achieves greedy-optimal coverage while deliberately avoiding over-reliance on universal connectors.**
**Interpretation (Tier 2 - now CONFIRMED):**

| Residual | Purpose |
|----------|---------|
| PREFIX coherence | Reduce cognitive load |
| Tail forcing | Ensure rare variant coverage |
**The Conceptual Pivot:**
> **Currier A is not meant to be *generated*. It is meant to be *maintained*.**




**Regression Results:**
| Predictor | r | p-value | Importance |
|-----------|---|---------|------------|
| **tail_pressure** | **0.504** | **0.0045*** | **68.2%** |
| novelty | 0.153 | 0.42 | 6.3% |
**Interpretation (Tier 2 - CONFIRMED):**
> **HT density correlates with tail pressure - the fraction of rare MIDDLEs in A entries.**


| MIDDLE Type | Cognitive Load | HT Response |
|-------------|---------------|-------------|
| Hubs ('a','o','e') | LOW | Lower HT |
| Common MIDDLEs | LOW | Lower HT |





| Model | Prediction | Evidence | Verdict |
|-------|------------|----------|---------|
| Static-Optimal | Order doesn't matter | 0 signals | REJECTED |
| Weak Temporal | Soft pedagogy | 0 signals | REJECTED |
**The Four Signals (5/5 Support Strong Scheduling):**




**Interpretation (Tier 2 - CONFIRMED):**
> **PEDAGOGICAL_PACING: Currier A introduces vocabulary early, reinforces throughout, and cycles between prefix domains.**

| Phase | Novelty | Tail Pressure | Interpretation |
|-------|---------|---------------|----------------|
| 1 (Early) | HIGH (21.2%) | HIGH (7.9%) | Vocabulary establishment + initial difficulty |
| 2 (Middle) | LOW (9.4%) | LOW (4.2%) | Reinforcement + relief |
**Reconciliation with Prior Findings:**
| Constraint | What it Shows |
|------------|---------------|
| C476 | WHAT Currier A optimizes (coverage with hub rationing) |
| **C478** | **HOW it achieves that (temporal scheduling)** |




**Test Results (12/12 passed):**
| Category | Tests | Result |
|----------|-------|--------|
| Behavior-Structural (BS-*) | 5 | 5/5 PASS |
| Process-Sequence (PS-*) | 4 | 4/4 PASS |
**Key Findings:**





**Behavior Mappings (NO NOUNS):**
| Element | Grammar Role | Process Behavior |
|---------|-------------|------------------|
| k | ENERGY_MODULATOR | Energy ingress control |
| h | PHASE_MANAGER | Phase boundary handling |



**Verdict (Tier 3 - SUPPORTED):**
> The grammar structure is isomorphic to reflux-distillation behavior. This does not prove the domain but establishes maximal structural alignment within epistemological constraints.




**The Unexpected Finding:**

| Metric | Expected | Observed |
|--------|----------|----------|
| LATE in high-complexity folios | HIGH | **LOW** (0.180) |
| LATE in low-complexity folios | LOW | **HIGH** (0.281) |

**The Two-Axis Model (Tier 2 - CONFIRMED):**

| Axis | Property | Evidence | Meaning |
|------|----------|----------|---------|
| **DENSITY** | Tracks upcoming complexity | r=0.504 with tail MIDDLEs (C477) | "How much attention is NEEDED" |
| **MORPHOLOGY** | Tracks spare capacity | r=-0.301 with folio complexity | "How much attention is AVAILABLE" |
**Why This Makes Sense:**
> **When the task is hard, HT is frequent but morphologically simple.**
> **When the task is easy, HT is less frequent but morphologically richer.**

**Constraint Alignment:**
| Constraint | How This Fits |
|------------|---------------|
| **C344** - HT-A Inverse Coupling | Direct instantiation: high A-complexity suppresses complex HT forms |
| **C417** - HT Modular Additive | HT is composite: density = vigilance, form = engagement |
**What HT Does NOT Encode:**

**Final Integrated Statement:**
> HT has two orthogonal properties:
>
> 1. **HT density tracks upcoming discrimination complexity** (tail MIDDLE pressure, AZC commitment).
>
> 2. **HT morphological complexity tracks operator spare cognitive capacity**, increasing during low-load phases and decreasing during high-load phases.
>
> HT does not encode what sensory modalities are needed. Sensory demands are implicit in the discrimination problem itself.




**Test Results:**
| Metric | Value |
|--------|-------|
| AZC tokens analyzed | 8,257 |
| Qualified MIDDLEs | 175 (≥5 occurrences) |
**The Four Clusters:**
| Cluster | n | Dominant Zone | Profile | Interpretation |
|---------|---|---------------|---------|----------------|
| S-cluster | 47 | S (59%) | Boundary-heavy | Commitment-safe discriminators |
| P-cluster | 29 | P (75%) | Permissive | Intervention-requiring discriminators |
**Interpretation (Tier 3):**
> **Currier A's discriminators are not only incompatible with each other - they are tuned to different *degrees of intervention affordance*, which the AZC legality field later enforces.**

**What This Does NOT Show:**

**Cross-References (Tier 2):**
| Constraint | Relationship |
|------------|--------------|
| C293 | MIDDLE is primary discriminator |
| C313 | Position constrains legality, not content |
**Why This Is Tier 3 (Not Tier 2):**





**Test Results:**

| Zone | Predicted Class | Actual Dominant | Match |
|------|-----------------|-----------------|-------|
| P (high intervention) | M-A | M-A | YES |
| S (boundary-surviving) | M-D | M-A | NO |
| Metric | Value |
|--------|-------|
| Hypothesis matches | 1/4 |
| P-value (permutation) | 0.852 |

**Interpretation (Tier 3):**
> **The Voynich system tracks what a thing is (PREFIX) and how cautiously it must be handled (MIDDLE zone survival) as independent dimensions. This design choice explains both the richness of the registry and the irrecoverability of specific substances.**

| Dimension | Encoded By | Question Answered |
|-----------|------------|-------------------|
| Material type | PREFIX | "What category of stuff is this?" |
| Handling requirement | MIDDLE zone | "How much intervention latitude?" |

**Why This Matters for Solvent/Material Decoding:**

> Solvent identity sits at the **intersection** of material type and handling sensitivity - and that intersection is never encoded. The operator supplies it from practice.
**What This Does NOT Show:**

**Cross-References:**
| Finding | Phase | Relationship |
|---------|-------|--------------|
| MIDDLE zone survival | MIDDLE_ZONE_SURVIVAL | Source of zone clusters |
| Material behavior classes | PROCESS_ISOMORPHISM | Source of M-A...M-D |


**Test Results Summary:**
| Test | Question | Verdict | Key Finding |
|------|----------|---------|-------------|
| 2A | Shared temporal trajectories? | BORDERLINE | 14/15 folios share PEAK_MID (p=0.062) |
| 1A | B behavior constrains A zones? | **STRONG** | High-escape -> +10.4% P-zone (p<0.0001) |
**New Structural Confirmations (Tier 3):**





**Nine-Layer Model:**
| Layer | Role | Mechanism |
|-------|------|-----------|
| Currier B | Execution safety | Frozen Tier 0 |
| - | - | **e-operator load-bearing** |
**B->A Inversion Axis:**

| Direction | What Flows | Evidence |
|-----------|-----------|----------|
| A->B | Discrimination vocabulary, zone legality | C437-C444 |
| **B->A** | **Escape profile constrains zone preference** | **Test 1A** |

**Operator Strategy Taxonomy:**
| Archetype | n | Viable Strategies |
|-----------|---|-------------------|
| AGGRESSIVE_INTERVENTION | 6 | AGGRESSIVE, OPPORTUNISTIC |
| ENERGY_INTENSIVE | 10 | AGGRESSIVE, OPPORTUNISTIC |

---


## I.O. Physical World Reverse Engineering Phases
### Overview

Six investigation phases tested the physical grounding of the control architecture:

| Phase | Question | Result |
|-------|----------|--------|
| **PWRE-1** | What plant class is admissible? | Circulatory thermal (12 exclusions) |
| **FM-PHY-1** | Is hazard distribution natural? | YES - diagnostic for reflux |
| **SSD-PHY-1a** | Is dimensionality physics-forced? | YES - D ≥ 50 required |
| **OJLM-1** | What must operators supply? | 13 judgment types |
| **APP-1** | Which apparatus exhibits this behavioral profile? | Pelican (4/4 axes match) |
| **MAT-PHY-1** | Does A's topology match botanical chemistry? | YES (5/5 tests pass) |



| Evidence Type | Result |
|---------------|--------|
| Historical sources (Brunschwig) | **SYSTEMATIC_MATCH** (4/6 axes, see brunschwig_comparison.md) |
| Modern engineering taxonomy | STRONG_MATCH (exact 5-class mapping) |
**Key Finding:**



| Objective | Result |
|-----------|--------|
| Dimensional lower-bound | D ≥ 50 proven |
| Topology classification | DISCRIMINATION SPACE (not taxonomy) |
**Key Findings:**

**One-Sentence Synthesis:**
> **MIDDLE tokens are indivisible discriminators whose only "content" is their position in a very large, physics-forced compatibility space; the number of distinctions exists because the real process demands them, not because the author chose them.**


| Category | Count | Types |
|----------|-------|-------|
| Watch Closely | 6 | Temperature, Phase Transition, Quality/Purity, Timing, Material State, Stability |
| Forbidden Intervention | 3 | Equilibrium Establishment, Phase Transition, Purification Cycle |
**Key Findings:**

**Design Principle:**
> The controller's omissions are not gaps - they are deliberate acknowledgment that some knowledge cannot be encoded. This is design integrity, not incompleteness.


| Axis | Test | Result |
|------|------|--------|
| 1. Responsibility Split | Do manuals assume same responsibilities? | DISTINCTIVE_MATCH |
| 2. Failure Fears | Do operators fear same things? | STRONG_MATCH (41/24/24/6/6) |
**Key Finding:**
- Fourth degree fire prohibition matches C490 EXACTLY: "It would coerce the thing, which the art of true distillation rejects, because nature too rejects, forbids, and repels all coercion."

**What Excluded:**



| Test | Question | Result |
|------|----------|--------|
| A. Incompatibility Density | ~95% under co-processing? | **95-97%** (vs 95.7% in A) |
| B. Infrastructure Elements | 3-7 bridges? | **5-7** (solvents, fixatives) |
**Key Findings:**

**What This Establishes:**

| Phase | Established |
|-------|-------------|
| PWRE-1 | What KIND of plant is admissible |
| FM-PHY-1 | That hazard logic is DIAGNOSTIC |
> **The Voynich Manuscript controls a circulatory thermal plant whose hazard profile matches distillation physics, whose discrimination space is forced by the physical state-space, whose operation REQUIRES human judgment for 13 structurally distinct types of non-codifiable knowledge, whose behavioral profile is isomorphic to the historical pelican apparatus, and whose registry topology matches the constraints that real botanical chemistry imposes.**

---


## II. Process Domain Interpretation

### Tier 3: Apparatus Identification

**Best match:** Circulatory reflux systems (pelican alembic or similar)

| Metric | Value |
|--------|-------|
| Structural compatibility | 100% (CLASS_D) |
| Next best alternative | 20% |
| Historical representative | Pelican alembic (late 15th c.) |
| Structural homology | 8/8 dimensions |

### Surviving Process Classes

1. **Circulatory Reflux Distillation** - 100% compatible
2. **Volatile Aromatic Extraction** - compatible
3. **Circulatory Thermal Conditioning** - compatible

Common signature: **CLOSED-LOOP CIRCULATORY THERMAL PROCESS CONTROL**

### Line-Level Execution Cycle

Lines follow SETUP→WORK→CHECK→CLOSE thermal processing cycle. See Section 0.F for full details (C547-C562).

### Historical Pattern Alignment

| Voynich Feature | Historical Match | Strength |
|-----------------|------------------|----------|
| 49 instruction classes | Brunschwig's 4 degrees of fire | STRONG |
| 17 forbidden transitions | "Fourth degree coerces - reject it" | STRONG |
| 8 recipe families | Antidotaria procedures | STRONG |
| 0 material encoding | Apparatus manuals omit feedstock | STRONG |
| Expert knowledge assumed | Guild training model | STRONG |
| Kernel control points | Process control theory | STRONG |
| Local continuity | Codex organization | STRONG |
| Line-level SETUP→WORK→CHECK→CLOSE | Fire-degree cycle | STRONG |
| ENERGY medial concentration | "Work phase" in process middle | STRONG |
| or→aiin checkpoint | Sensory verification points | STRONG |

10/15 patterns show STRONG alignment.

---


## III. Material Domain Interpretation

### Tier 3: Botanical-Aromatic Favored

**Verdict:** BOTANICAL over alchemical-mineral (8/8 tests, ratio 2.37)

### Abstract Material Classes

| Class | Properties | Medieval Examples | Grammar Fit |
|-------|------------|-------------------|-------------|
| CLASS_A | Porous, swelling | Dried leaves, flowers, roots | COMPATIBLE |
| CLASS_B | Dense, hydrophobic | Resins, seeds, citrus peel | COMPATIBLE |
| CLASS_C | Phase-unstable | Fresh plant, fats, emulsions | **INCOMPATIBLE** |
| CLASS_D | Stable, rapid diffusion | Alcohol/water, clear extracts | COMPATIBLE |
| CLASS_E | Homogeneous fluid | Distilled water, pure alcohol | COMPATIBLE |

CLASS_C shows 19.8% failure rate - grammar designed to AVOID phase transitions.

### Product Space

Plausible product families:
1. **Aromatic Waters** (90.5% convergence - primary)
2. Essential Oils
3. Resin Extracts
4. Digested Preparations
5. Stabilized Compounds

Multi-product workshop likely. Programs represent **substrate x intensity combinations**, not 83 distinct products.

### Plant Illustration Alignment

| Metric | Value |
|--------|-------|
| Perfumery-aligned plants | 86.7% (p<0.001) |
| Root emphasis | 73% |
| Program-morphology correlation | NONE |

---


## IV. Craft Interpretation

### Tier 3: Perfumery as Interpretive Lens

5/5 tests PLAUSIBLE:

| Test | Verdict |
|------|---------|
| Token clusters align with smell-change windows? | PLAUSIBLE |
| Tokens encode warning memories? | CRAFT-PLAUSIBLE |
| Tokens support resumption after breaks? | STRONGLY PLAUSIBLE |
| Same roles, different vocabulary across sections? | CRAFT NAMING |
| Absences match perfumery tacit knowledge? | EXACTLY ALIGNED |

### What the Author Feared (via failure analysis)

| Fear | Percentage |
|------|------------|
| Phase disorder (material in wrong state) | 41% |
| Contamination (impure fractions) | 24% |
| Apparatus failure (overflow, pressure) | 24% |
| Flow chaos (rate imbalance) | 6% |
| Thermal damage (scorching) | 6% |

> "The book encodes my fears, so that you do not have to learn them through loss."

---


## V. Institutional Context

### Tier 3: Guild Workshop Setting

**Surviving candidates:**
- Goldsmith/assayer workshops
- Central Europe 1400-1550
- Northern Italy 1400-1470

### Scale Indicators

| Metric | Value | Implication |
|--------|-------|-------------|
| Currier A entries | ~1,800 | Larger than typical recipe books (300-400) |
| Program count | 83 | Major institutional operation |
| Historical parallels | Santa Maria Novella, Venetian muschieri guild | Court-sponsored production |

### Characteristics

- Expert-oriented (no novice accommodation)
- Guild-restricted (assumes trained operators)
- Court-sponsored (scale suggests patronage)

### Proprietary Pharmaceutical Manufacturing (Tier 4, Phase 385-386)

**Hypothesis:** The manuscript is a proprietary manufacturing manual for a guild apothecary operation — the medieval equivalent of a pharmaceutical company's trade-secret process documentation. The script's unbreakability is not incidental; it protects the competitive advantage.

**Historical fit (1404-1438 radiocarbon window):**

The Voynich was written during the peak era of guild pharmaceutical secrecy:
- **1351:** Rupescissa's *De consideratione quintae essentiae* establishes theoretical framework for medicinal distillation (quinta essentia = repeatedly distilled alcohol as universal medicine)
- **1353:** Paris Guild of Spice Merchants-Apothecaries receives royal statutes regulating practice
- **1400-1500:** Apothecary guilds across Europe guard distillation techniques as trade secrets. Proprietary recipes circulate only through master-apprentice chains. Coded language and Latin names used to keep formulations confidential.
- **1424:** Bruges spice dealer/apothecary sells distilling glasses to John of Bavaria — distillation equipment is commodity trade goods
- **1500:** Brunschwig publishes *Liber de arte distillandi*, the first printed distillation manual, breaking guild secrecy

**The economic logic:** Plant properties and common remedies were widely known, even by laypeople. The competitive advantage was in the *manufacturing process* — how to distill, extract, compound, and formulate products of consistently superior quality. The control grammar (49 classes, 17 forbidden transitions, 6 macro states) represents an extraordinary engineering investment that is only justified if protecting high-value proprietary processes.

**Structural evidence from Phases 385-386:**

| Section | Profile | Possible Role |
|---------|---------|---------------|
| Bio | k-enriched, 100% REGIME_1, LINK-depleted, QO-dominant | Sustained gentle heating (balneum mariae distillation) |
| Stars | e-dominant, mixed REGIMEs, highest LINK density | Product collection/quality control |
| Herbal | All 4 REGIMEs, FQ-heavy, operationally diverse | Material preparation/compounding |
| Cosmo | h-enriched, zero REGIME_1, monitoring-intensive | Observation-heavy process (quality verification or treatment) |
| Recipe | Precision REGIMEs, balanced triggers | Complex reference procedures |

Phase 386 found that 4/6 dimensional differences between sections are explained by REGIME composition alone. Only h% (monitoring intensity) and LINK density (checkpoint frequency) show independent section effects beyond REGIME. This means sections encode different *REGIME mixtures* (different techniques), with modest independent effects on monitoring and checkpointing strategy.

**What this resolves:**
- Why an unbreakable script (trade secrets worth protecting)
- Why C138 holds — illustrations show raw materials (commodity knowledge), text encodes process (proprietary knowledge)
- Why the grammar is domain-general — one control system handles many products
- Why such engineering effort — 949 constraints worth of structure is justified for a pharmaceutical empire's operating manual
- Why Brunschwig aligns — he published (in 1500) what practitioners like the Voynich author had been keeping secret for decades

**What this does NOT claim:**
- Specific products or materials (C171 semantic ceiling)
- Identity of the guild or workshop
- That sections map 1:1 to craft domains (Phase 386: most variation is REGIME-mediated)
- That the "treatment" interpretation for Cosmo is confirmed (N=5, simpler alternatives exist)

**Falsification:** If the manuscript's dating were revised outside the 1350-1500 pharmaceutical secrecy window, or if the structural architecture proved incompatible with process control (already falsified by 383 phases of evidence), the interpretation would fail.

---


## VI. HT Speculative Vocabulary

| Label | Structural Function | Speculative Meaning |
|-------|---------------------|---------------------|
| ESTABLISHING | Section entry anchor | System warming, circulation starting |
| RUNNING | Wait phase marker | Steady reflux, all normal |
| HOLDING | Persistence marker | Maintain current state |
| APPROACHING | Constraint rise | Watch closely, risk increasing |
| RELAXING | Constraint fall | Critical passed, ease vigilance |
| EXHAUSTING | Section exit anchor | Run winding down |

---


## VII. Program Characteristics

### Forgiveness Gradient

Programs vary along a **forgiving <-> brittle** axis:

| Quartile | Hazard Density | Escape Density | Safe Run Length |
|----------|----------------|----------------|-----------------|
| Q1 (Brittle) | 11.1% | 7.5% | 27.6 |
| Q4 (Forgiving) | 7.8% | 23.8% | 45.0 |

- Most brittle: f33v, f48v, f39v
- Most forgiving: f77r, f82r, f83v

Interpretation: Different "slack" for operator error. May serve competency grading.

---


## VIII. Limits of Interpretation

### What Cannot Be Recovered Internally

Even with complete structural understanding:

| Category | Examples |
|----------|----------|
| Materials | Specific substances, plants, minerals |
| Products | Specific outputs, recipes, formulations |
| Language | Natural language equivalents for tokens |
| Identity | Author, institution, school |
| History | Precise dating, geographic origin |
| Physical | Apparatus construction, illustration meanings |

### Discardability

All interpretations in this document are DISCARDABLE:
- If structural evidence contradicts, discard interpretation
- Apparatus identification is discardable
- Material alignment is discardable
- Craft domain is discardable

Only Tier 0-2 structural findings are binding.

---


## IX. Open Questions

### Fully Answered

| Question | Status | Finding |
|----------|--------|---------|
| Why are some programs forgiving and others brittle? | PARTIALLY ANSWERED | Recovery varies freely (CV=0.82), hazard is clamped (CV=0.11) - C458 |
| What does HT signal? | ANSWERED | Anticipatory vigilance, content-driven - C459 |
| What role does AZC play in the manuscript? | **FULLY ANSWERED** | Positional encoding, compatibility grouping, position reflects vocabulary character - C437-C444 |
| Why are there so many AZC folios? | **FULLY ANSWERED** | Enumerates all compatibility classes; each folio = distinct legal combination space - C437, C442 |
| How does AZC relate to A and B? | **FULLY ANSWERED** | AZC encodes vocabulary position; each PREFIX+MIDDLE has one fixed position reflecting operational character - F-AZC-011/012/013 |
| How do roles flow within a line? | **FULLY ANSWERED** | SETUP→WORK→CHECK→CLOSE positional template (p=3e-89) - C547-C562 |
| What is the relationship between ENERGY and FLOW? | **FULLY ANSWERED** | Anticorrelated by REGIME and section; heating vs cooling modes - C551, C562 |
| What does daiin do? | **FULLY ANSWERED** | Line-initial ENERGY trigger (27.7% initial, 47.1% EN followers) - C557 |
| What is Class 9 "self-chaining"? | **FULLY ANSWERED** | Directional or→aiin bigram (87.5%), zero aiin→aiin - C561 |

### Still Open (structural)

- What determines sister pair choice beyond section?
- What morphology-level choices affect HT density?
- Why do HT hotspots cluster in tails rather than forming modes?

### Requires External Evidence (historical)

- Who created this manuscript?
- What institution supported it?
- Why was this level of documentation created?

### May Never Be Answerable (interpretive)

- What specific products were made?
- What specific apparatus was used?
- What language(s) did the operators speak?

---


## X. External Alignment: Puff-Voynich-Brunschwig (2026-01-14)
### Core Finding: SHARED CURRICULUM TRAJECTORY (v4.22 - UPGRADED)

> **The Voynich Manuscript and Brunschwig's distillation treatise instantiate the same procedural classification of thermal-circulatory operations.**
>
> **Brunschwig externalizes explanation and ethics for novices; Voynich internalizes safety and recovery for experts.**
>
> **The alignment is regime-level and architectural, not textual or semantic.**
>
> **Puff and Brunschwig preserve the original pedagogical progression of the Voynich Currier B corpus, which has been disrupted by early misbinding.**

### The Three-Text Relationship

| Text | Date | Function | Perspective |
|------|------|----------|-------------|
| **Puff von Schrick** | ~1455 | Enumerates materials | NOUN catalog |
| **Voynich Currier B** | 1404-1438 | Enforces safe execution | VERB programs |
| **Brunschwig** | 1500 | Explains method | Pedagogical |

> **Puff, Voynich, and Brunschwig are three orthogonal projections of a single late-medieval distillation curriculum.**

### Evidence Strength Summary

| Test Suite | Score | Status |
|------------|-------|--------|
| Puff-Voynich Mastery Horizon | 83:83 isomorphism | **PASS** |
| Equivalence Class Collapse | REGIME_2: 11->3, REGIME_3: 16->7 | **PASS** |
| Regime-Degree Discrimination | 5/6 tests | **STRONG** |
| Suppression Alignment | 5/5 tests | **PASS** |
| Recovery Corridor | 4/4 tests | **PASS** |
| Clamping Magnitude (C458) | 5/5 tests | **PASS** |
| **Total** | **19/20** | **FULL PROCEDURAL ALIGNMENT** |


## Navigation

## XI. Rosettes Foldout (STATUS: REVALIDATED — Phase 402)

### Tier 2: Structural Findings

**Metalayer confirmed (C1126):** The Rosettes foldout is an organizational metalayer sitting above the standard A/B/AZC systems and cross-referencing the body text. This is the core finding — it is not a standard B program page, not a standard AZC positional page, but a meta-structural index.

**AZC-like grammar (C1127):** All entity types (ring text, labels, paths, spiral, clock) show consistent AZC-type morphology: grammar coverage ~42% (B: ~100%, AZC: ~50%), kernel density 29-41%, PP ~50%/RI ~2%. Not a hybrid — the old hybrid classification (C1088) was a data artifact.

**Bridge enrichment (C1124):** 3.05x enrichment over B corpus (21.5% vs 7.0%). Universal across all sub-region types — ring 4.56x, labels 4.74-5.17x, clock 7.11x. The foldout preferentially samples cross-system vocabulary.

**Section T indexing — QUALIFIED (C1125, C1133):** All 9 rosettes correlate most strongly with Section T at the section level, but this is a vocabulary-size artifact (C1133). Section T has only 1 non-Rosettes folio (f66r, 112 MIDDLEs); per-folio, f66r ranks #11/76. Top 10 overlapping folios are 9 Section S + 1 Section H. Bridge density anticorrelates with overlap (rho = -0.60). The foldout indexes diverse, vocabulary-rich folios, not Section T specifically.

**Generic indexing (C1128):** All rosettes point to approximately the same B folios (mean inter-rosette Jaccard of top-5 sets = 0.322; f40v in top-5 for 8/9 rosettes). The foldout is a shared vocabulary hub, not a specific lookup table.

**Ring text forbidden compliance (C1130):** Ring text has 0/277 forbidden transition violations but transition entropy 7.92 bits (vs B's ~0.41). Respects hard constraints, ignores soft ones.

**Ring text register classification (C1131):** Ring text is a BRIDGE_VOCABULARY_INDEX — a distinct register that samples B-grammar bridge vocabulary under hard constraints. 52.4% of tokens map to B grammar, AUXILIARY role dominates (42.7%), 100% of classified MIDDLEs are bridge. Structured class distribution, not random enumeration.

**Ring text dual population (C1132):** Ring text interleaves two populations: (1) B-grammar bridge tokens (short, simple, 100% bridge) that serve as index entries, and (2) unclassified identification tokens (long, complex, mostly non-bridge) that label foldout-specific concepts.

### Tier 3: Spatial Structure (Inconclusive)

Path tokens do not bridge endpoint rosette vocabularies, and vocabulary similarity does not decay with spatial distance. These tests were underpowered — most individual entities have <10 tokens, limiting statistical sensitivity for spatial patterns.


---


## XII. Cross-System Vocabulary Flow (Phase 406)

### Tier 2: Structural Findings

**Section specificity is frequency-modulated (C1134):** The same shared/PP MIDDLEs appear in all B sections (type-universal) but at section-specific token frequencies. PP vocabulary drives 74% of between-section JS divergence (JS_PP=0.124 vs JS_ALL=0.167). B-exclusive vocabulary is maximally section-specific per-type (JS=0.847) but carries only 5.8% of tokens, making it token-negligible for section discrimination. The paradox resolves: vocabulary is type-universal but frequency-specific.

**Unmatched PP dark pipeline (C1135):** Of 404 PP MIDDLEs, only 89 match B grammar classes. The other 315 are overwhelmingly present in B (95.2%, 300/315) but at dramatically lower frequency (mean 5.7 tokens vs 224.8 for matched; mean 4.6 folios vs 39.0). They are section-concentrated (Herf 0.716), mostly compound (66.7%), and constitute the HT/UN derivational substrate — the morphological bridge between A's registry and B's unclassified layer.

**A->B flow is uniform and concentrated (C1136):** A-Herbal and A-Pharmaceutical produce indistinguishable B coverage profiles (cosine 0.9997). The pipeline is section-blind — all A sections cover B-Herbal best and B-Stars worst, with identical relative profiles. Pipeline grammar is highly concentrated: 12 A folios cover 100% of B's 89 classified MIDDLEs, with f58v (Section T, text-only) alone covering 60.7%. The full B inventory ceiling is 30.4% from all 114 A folios — 70% of B vocabulary is completely B-internal.


---


## XIII. Dark Pipeline Functional Test (Phase 407)

### Tier 2: Structural Findings

**100% HT/UN substrate (C1137):** All 1,696 B tokens built from dark-pipeline MIDDLEs are HT/UN classified. Zero are grammar-classified. This is not a tendency but a complete partition: matched PP MIDDLEs (89) produce 80.2% grammar-classified tokens, while dark-pipeline MIDDLEs (300) produce exclusively identification vocabulary. The mean 5.7 tokens per dark-pipeline MIDDLE (vs 224.8 for matched) validates C1135's frequency characterization.

**Distinct construction grammar (C1138):** Dark-pipeline tokens use a morphological recipe distinct from both general HT and grammar tokens. Grammar-standard/extended PREFIX ratio is 3.39 (vs general HT 1.81, 87% higher) — dark tokens strongly prefer grammar-standard prefixes (ch, sh, qo, etc.) over extended/HT-specific ones. Suffix rate is 89.9% (vs HT 77.3%, grammar 38.7%). Articulator rate is 2.5% (vs HT 10.1%). The pattern is: simpler at the front (fewer articulators, more grammar-standard prefixes), more elaborated at the back (higher suffix rate). This constitutes a third morphological register within B's token inventory.

**Bridge-disjoint (C1139):** The 300 dark-pipeline MIDDLEs and 85 bridge MIDDLEs (C1013) have zero overlap. The A-B vocabulary pipeline has three cleanly separated channels: (1) bridge MIDDLEs carrying dynamical/behavioral information, (2) ~4 non-bridge matched PPs, and (3) dark-pipeline MIDDLEs carrying identification/specification information. Neither population borrows from the other.



---


## XIV. PP Pipeline Atom Decomposition (Phase 408)

### Tier 2: Structural Findings

**PP pipeline complete partition (C1140):** The 404 PP MIDDLEs partition into exactly four mutually exclusive populations: 85 bridge, 4 non-bridge matched (c, ch, cho, otc -- AUXILIARY-dominant edge cases), 300 dark pipeline, and 15 B-absent phantoms (all ch/sh-prefixed with zero A tokens). The partition is exhaustive and all six pairwise intersections are empty.

**Dark pipeline compounds built from bridge atoms (C1141):** Despite zero MIDDLE-level overlap (C1139), 96.5% of dark-pipeline compounds contain at least one bridge atom as a building block. Of 50 unique atoms found in the 200 compound dark-pipeline MIDDLEs, 43 (86%) are bridge MIDDLEs. Bridge atoms account for 91.6% of all atom occurrences. The construction hierarchy is: bridge atoms (short, universal) -> compositional assembly (1-3 atoms per compound) -> dark-pipeline compounds (section-concentrated) -> HT/UN identification tokens.

**Modified construction grammar (C1142):** Dark-pipeline compounds follow a variant dialect of B's general atom ordering grammar (C1065). Agreement on asymmetric pair direction is 50% (7/14 matches), but gateway/terminal atom positioning is preserved (gateway mean position 0.083, terminal 0.352). The dark pipeline uses a larger atom vocabulary (50 vs 27 for grammar compounds), with 25 dark-exclusive atoms extending the construction alphabet. Section concentration (C1135 Herfindahl 0.716) is NOT atom-driven (permutation p = 0.303) -- the same atoms appear across sections, with specificity arising from combination rather than selection.




### Tier 4: Operational-Profile Nomenclature

The dark pipeline may be a **naming system that defines things by their processing behavior**. Bridge atoms encode operational primitives (heat, cool, monitor, stabilize); the 49-class grammar uses these to specify what to DO. The dark pipeline recombines the same atoms into compound labels that specify what you are WORKING WITH. The names are not arbitrary -- they are compressed operational profiles. A dark-pipeline compound built from [cooling-atom + monitoring-atom] does not mean "lavender" or "rosemary"; it means "the material you cool while monitoring."

This would explain the full structural signature:
- **Built from bridge atoms (96.5%):** Things are named using operational vocabulary because the names ARE operational descriptions.
- **Never grammar-classified (100% HT/UN):** Names do not execute. They sit alongside the grammar as labels.
- **Section-concentrated but not atom-driven (Herf 0.716, perm p=0.303):** Every section uses the same operational primitives; different sections combine them differently because different material classes have different processing profiles.
- **Low frequency (5.7 tokens/MIDDLE):** Each specific material or preparation appears rarely across the manuscript.
- **Modified ordering grammar (50% C1065 agreement):** Atoms are sequenced differently when naming something than when specifying operations on it -- perhaps the dominant processing property leads.
- **Grammar-standard prefixes (C1138, GS/EXT ratio 3.39):** Even identification tokens need a domain selector. Materials are identified within operational contexts.
- **Phantoms (15 B-absent):** Morphologically valid name-slots that no actual material instantiates. The system can generate more names than it needs.

The analogy is chemical nomenclature: methyl-ethyl-ketone names a substance by concatenating its structural components. A distiller trained in this system would not read a substance name in natural language -- they would read a compound MIDDLE and recognize the material by its operational profile. The semantic ceiling (C171) holds: we cannot recover WHICH material a compound names, but we can see that the naming system is built from the same atoms that drive the operational grammar.








---

# Currier A Structure Contract

```yaml

meta:
  name: "Currier A Structural Contract"
  acronym: "CASC"
  version: "2.0"
  date: "2026-02-14"
  status: "ACTIVE"
  derived_from: "Tier-2 constraints only"
  governance: |
    CASC is NOT authoritative. Constraints are authoritative.
    CASC is a convenience layer for tooling and AI comprehension.
    Do not edit CASC without updating source constraints first.

scope:
  system: "Currier A"
  coverage_under_b_grammar: "13.6%"  # C224
  folio_count: 114  # C272
  physical_separation: "complete (0 folios shared with B)"  # C272
  sections: ["H", "P", "T"]  # C232, C260
  token_density: "0.35x B density"  # C228

guarantees:
  - id: "LINE_ATOMIC"
    statement: "Each line is an independent unit"
    provenance: "C233"

  - id: "POSITION_FREE"
    statement: "No positional grammar within lines"
    provenance: "C234"

  - id: "NON_SEQUENTIAL"
    statement: "No generative grammar exists"
    provenance: "C225, C230, C231, C240"

  - id: "FLAT_REGISTRY"
    statement: "Not hierarchical"
    provenance: "C236"

record_types:
  control_operator:
    token_count: 1
    frequency: "0.6% (10 instances)"
    vocabulary: "90% disjoint from registry entries"
    missing_prefixes: ["ch-", "qo-"]
    overrepresented_prefixes: ["yd-", "so-", "ke-", "sa-"]
    azc_participation: false
    ht_involvement: false
    positional_bias:
      boundary_enriched: true
      p_value: 0.0099
      folio_start_rate: "30%"
      folio_end_rate: "30%"
    function: "Operate on registry organization, not content"
    provenance: "C484"

  registry_entry:
    token_count: "2+"
    minimum_size: 2
    frequency: "99.4%"
    azc_participation: true
    batch_processing: true
    function: "Define fine distinctions at complexity frontier"
    provenance: "C482, C484"

morphology:
  decomposition: "PREFIX + SISTER? + MIDDLE + SUFFIX + ARTICULATOR?"
  combination_count: 897  # C268
  provenance: "C267, C278"

  prefix:
    families: ["ch", "sh", "ok", "ot", "da", "qo", "ol", "ct"]
    count: 8
    function: "Control-flow participation / functional type marker"
    mutual_exclusion: true
    semantic_meaning: false  # Markers, not categories
    provenance: "C235, C466-C467"

  sister:
    pairs:
      - ["ch", "sh"]
      - ["ok", "ot"]
    function: "Operational mode (precision vs tolerance)"
    equivalent_slots: true
    anticorrelation: "rho=-0.326"
    provenance: "C408, C412"

  middle:
    count: 1184
    prefix_exclusive_rate: "80% (947 MIDDLEs)"
    shared_rate: "20% (237 MIDDLEs)"
    universal_count: 27  # Appear in 6+ prefixes
    top_30_coverage: "67.6% of usage"
    function: "Variant discriminator / compatibility carrier"
    essentiality: "Primary discriminator (402 unique distinctions)"
    entropy: "6.70 bits (65.6% of maximum)"
    incompatibility_rate: "95.7% of pairs are illegal"  # C475
    two_track_structure:
      # REGENERATED 2026-01-24: Atomic-suffix parser (voynich.py)
      shared_with_b:
        count: 404
        substructure:  # C498.a - RE-VERIFIED 2026-01-24
          azc_mediated:
            count: 214
            percent: "19.8% of A vocabulary"
            role: "Vocabulary appearing in A, AZC, and B contexts (three-system vocabulary)"
            breakdown:
              universal: 28   # 10+ AZC folios, avg 54.8 B spread
              moderate: 69    # 3-9 AZC folios, avg 15.4 B spread
              restricted: 117 # 1-2 AZC folios, avg 6.3 B spread
          b_native_overlap:
            count: 198
            percent: "18.4% of A vocabulary"
            role: "Vocabulary shared between A and B but absent from AZC contexts"
            characteristics: "Zero AZC presence, avg 3.5 B folios"
        functional_partition:  # C1140 — orthogonal to C498.a's AZC-presence partition
          description: |
            The 404 PP MIDDLEs also partition by B grammar role into four mutually
            exclusive, collectively exhaustive populations. This grammar-role partition
            (C1140) is orthogonal to C498.a's AZC-presence partition (214 AZC-mediated
            + 198 B-native). Both classify the same 404 PP MIDDLEs by different criteria.
          bridge: { count: 85, function: "Cross-system dynamical backbone (C1013)" }
          non_bridge_matched: { count: 4, function: "Edge-case grammar participants (c, ch, cho, otc)" }
          dark_pipeline: { count: 300, function: "HT/UN identification substrate (C1137)" }
          phantom: { count: 15, function: "A-present, B-absent artifacts (all ch-/sh- prefixed, 0 A tokens)" }
          total: 404
          provenance: "C1140"
        provenance: "C498.a, C1140"
      registry_internal:
        count: 609
        characteristics: "ct-prefix enriched, suffix-less, folio-localized"
        role: "Stay in A registry, encode within-category fine distinctions"

        # Population structure (C498.b, C498.c, C498.d)
        population_structure:
          length_frequency_correlation:  # C498.d
            correlation: "rho = -0.367, p < 10^-42"
            short_2_chars: { singleton_rate: "48%", mean_freq: 3.45 }
            short_3_chars: { singleton_rate: "55%", mean_freq: 2.72 }
            mid_4_chars: { singleton_rate: "73%", mean_freq: 1.84 }
            mid_5_chars: { singleton_rate: "82%", mean_freq: 1.35 }
            long_6_chars: { singleton_rate: "96%", mean_freq: 1.04 }
            long_8plus: { singleton_rate: "100%", mean_freq: 1.00 }
          singleton_repeater_independence: "chi2 p=0.165 (not significant) - co-occurrence is near-random"
          provenance: "C498.b, C498.c, C498.d"

        # PREFIX lexical bifurcation (C528)
        prefix_bifurcation:  # C528
          prefix_required: { count: 334, percent: "50.1%" }
          prefix_forbidden: { count: 321, percent: "48.1%" }
          prefix_optional: { count: 12, percent: "1.8%" }
          disjoint_rate: "98.2%"
          section_independence: true  # Same ~50/50 split holds within each section
          provenance: "C528"

        # Orthogonal feature structure (C513-NOTE-B)
        orthogonal_features:  # C513-NOTE-B
          axes:
            DOMAIN: { rate: "54.9%", feature: "Gallows presence (k/t/p/f)" }
            POSITION: { rate: "40.7%", feature: "Line-initial or line-final" }
            SCOPE: { rate: "57.5%/42.5%", feature: "Record-anchored vs independent" }
            EMPHASIS: { rate: "2.7%", feature: "Articulator present (71.5% at boundaries)" }
            PREFIX: { rate: "50.1%/48.1%", feature: "Required vs forbidden (C528)" }
          independence_evidence:
            articulator_x_gallows: { expected: 11.5, observed: 10, ratio: "0.87x" }
            gallows_x_record_scope: { expected: 181.7, observed: 166, ratio: "0.91x" }
            articulator_x_record_scope: { expected: 8.9, observed: 9, ratio: "1.01x" }
          provenance: "C513-NOTE-B"

        # RI functional population structure (C831-C839)
        ri_functional_structure:

          three_tier_population:  # C831
            singletons: { rate: "95.3%", count: 674, behavior: "Appear exactly once corpus-wide" }
            position_locked: { rate: "~4%", count: 29, behavior: "Repeat but stay within INITIAL/MIDDLE/FINAL" }
            linkers: { rate: "0.6%", count: 4, behavior: "Appear as FINAL then INITIAL (cross-paragraph bridge)" }
            provenance: "C831"

          positional_separation:  # C832
            initial_only_count: 10
            final_only_count: 15
            middle_only_count: 8
            overlap_rate: "0% between INITIAL-only and FINAL-only"
            provenance: "C832"

          line1_concentration:  # C833
            ri_line1_rate: "3.84x baseline"
            provenance: "C833"

          linker_mechanism:  # C835-C838
            linkers: ["cthody", "ctho", "ctheody", "qokoiiin"]
            link_count: 12
            direction_bias: "66.7% forward"
            mean_distance: "+6.6 folios"
            topology: "Convergent (many-to-one)"
            hub_structure:
              f93v: "5 incoming links (major collector)"
              f32r: "4 incoming links"
            ct_prefix_signature: "3/4 linkers have ct- prefix"  # C836
            qo_exception: "qokoiiin is only non-ct linker"  # C838
            provenance: "C835, C836, C837, C838"

          input_output_asymmetry:  # C839
            input_markers: 12
            output_markers: 5
            asymmetry_ratio: "2.4x"
            strongest_input: ["ko- (9x)", "to- (inf)", "-r (7x)", "-ey (4.5x)"]
            strongest_output: ["-ry (0.20x = 5x OUTPUT bias)"]
            provenance: "C839"

          provenance: "C831, C832, C833, C835, C836, C837, C838, C839"

      provenance: "C498, C498.a, C498.b, C498.c, C498.d, C513-NOTE-B, C528, C831-C839"
      revision_date: "2026-01-29"

    # Gallows patterns (C529-C530)
    gallows:

      positional_asymmetry:  # C529
        pp_gallows_initial: "30.4%"
        ri_gallows_initial: "20.1%"
        pp_gallows_medial: "39.3%"
        ri_gallows_medial: "57.8%"
        statistical_significance: "chi2=7.69, p<0.01"
        bench_gallows_ri_enriched:
          cph: "81% RI"
          ckh: "65% RI"
          cth: "59% RI"
        discrimination_heuristic: "len>=4 AND not gallows-initial -> 76.6% RI accuracy"
        provenance: "C529"

      folio_specialization:  # C530
        global_distribution:
          k: "53.7%"
          t: "30.4%"
          p: "11.4%"
          f: "4.5%"
        k_dominant_folios: "78/109 (72%)"
        t_specialized_folios: ["f4r (69%)", "f10r (74%)", "f29v (71%)"]
        p_f_never_dominant: true
        ri_pp_coherence: "62.2% same dominant (vs 54% expected)"
        provenance: "C530"

    # Sub-component grammar (C510-C513)
    sub_component_grammar:
      sub_component_count: 218  # C267.a
      reconstruction_coverage: "97.8%"

      positional_classes:  # C510
        START_class: 62
        END_class: 14
        MIDDLE_class: 1
        FREE_class: 110
        constrained_rate: "41.2%"
        free_rate: "58.8%"
        statistical_significance: "z=34.16, p<0.0001"
        provenance: "C510"

      derivational_productivity:  # C511
        seeding_ratio: "12.67x above chance"
        relationships_above_chance: "89.8%"
        explains: "C498.d length-frequency correlation"
        provenance: "C511"

      pp_substrate:  # C512
        pp_as_subcomponents: "72.2%"
        ri_containing_pp: "99.1%"
        section_invariance_ratio: "8.3x (PP vs RI)"
        pp_in_all_sections: "60.7%"
        ri_in_all_sections: "2.6%"
        provenance: "C512"

      positional_asymmetry:  # C512.a
        END_class_pp_rate: "71.4%"
        START_class_pp_rate: "16.1%"
        FREE_class_pp_rate: "40.9%"
        pp_free_rate: "69.2%"
        architecture: "RI-START + PP-FREE + PP-END"
        pp_terminators: ["ch", "d", "e", "g", "h", "k", "s", "t"]
        provenance: "C512.a"

      short_singleton_variance:  # C513
        character_inventory_jaccard: "1.00"
        provenance: "C513"

      provenance: "C267.a, C510, C511, C512, C512.a, C513"

    provenance: "C293, C423, C475, C498, C510-C513"

  suffix:
    count: 25
    universal_rate: "22/25 appear in 6+ prefix classes"
    function: "Decision archetype (phase-indexed)"
    regime_association:
      enriched_universal: ["-r"]
      enriched_restricted: ["-ar", "-or"]
      effect_size: "Cramér's V = 0.159"
      provenance: "C495"
    provenance: "C269, C277, C495"

  articulator:
    frequency: "~20% of tokens"
    forms: ["yk-", "yt-", "kch-"]
    discriminative: false
    unique_distinctions: 0  # C292 ablation test
    function: "Expressive refinement only"
    section_concentrated: true
    provenance: "C291, C292"

line_structure:
  atomicity:
    statement: "Each line is independent unit"
    median_tokens: 3
    mutual_information_across_lines: 0
    provenance: "C233"

  minimum_size:
    control_operators: 1
    registry_entries: 2
    provenance: "C484"

  batch_semantics:
    enabled: true
    b_invariance: "B structure invariant to A line length"
    test_result: "p=1.0 (all A categories map to same B folios)"
    provenance: "C482"

  repetition:
    status: "INVALIDATED (2026-01-15)"
    provenance: "C250 INVALIDATED"

  da_articulation:
    function: "Internal sub-record boundary punctuation"
    separation_rate: "75.1% between different prefix runs"
    section_gradient:
      H: "76.9%"
      P: "71.7%"
      T: "65.0%"
    semantic_content: false  # Punctuation, not classifier
    provenance: "C422"

paragraph_structure:
  # For comprehensive paragraph-as-unit model, see PSC (paragraph.psc.yaml)
  # PSC owns: definition (C827), independence model, A-B correspondence, stability
  # CASC retains: A-specific profiling below (size, RI variance, section profile, combinatorics)

  operational_unit:  # C827
    statement: "Paragraphs are the operational aggregation level (not lines, not folios)"
    provenance: "C827"

  paragraph_granularity:  # C834
    validated: true
    line_aggregation_insufficient: "Too narrow for operational coverage"
    folio_aggregation_excessive: "Obscures meaningful variation"
    provenance: "C834"

  a_paragraph_properties:
    size_distribution:  # C847
      mean_lines: 4.8
      by_position:
        first: { lines: 5.35, tokens: 39.0 }
        middle: { lines: 2.75, tokens: 18.7 }
        last: { lines: 5.36, tokens: 36.2 }
        only: { lines: 11.79, tokens: 73.4 }
      provenance: "C847"

    ri_position_variance:  # C848
      pattern: "RI concentrated in specific paragraph positions"
      line1_concentration: "3.84x baseline (header zone)"
      provenance: "C848"

    section_profile:  # C849
      H_section: "Standard paragraph structure"
      P_section: "Variant paragraph structure"
      T_section: "Different organizational pattern"
      provenance: "C849"

    cluster_taxonomy:  # C850
      cluster_count: 5
      silhouette: 0.337
      types: ["short", "standard", "long", "only", "metadata"]
      provenance: "C850"

    # Paragraph combinatorial grammar (C1039-C1041)
    combinatorial_grammar:

      cluster_selectivity:  # C1039
        statement: "Paragraphs draw from fewer C475 compatibility clusters than random"
        observed_entropy: 1.502
        null_entropy: 1.780
        z_score: -2.830
        p_value: 0.002
        interpretation: "Paragraphs specialize within the compatibility graph"
        provenance: "C1039"

      folio_compatibility_coherence:  # C1040
        statement: "Within-folio paragraph pairs have higher MIDDLE compatibility than between-folio"
        within_folio_median: 0.880
        between_folio_median: 0.811
        section_matched_median: 0.810
        effect_survives_section_matching: true
        interpretation: "Folio is a designed unit of compatibility, not just a container"
        provenance: "C1040"

      complementary_diversification:  # C1041
        statement: "Paragraphs have LOWER cross-line compatibility than random (diversify, not cluster)"
        observed_density: 0.6996
        null_density: 0.7071
        z_score: -3.567
        direction: "NEGATIVE (diversification)"
        interpretation: "Paragraphs maximize coverage by grouping complementary entries"
        extends: "C476 coverage optimality"
        provenance: "C1041"

      ordering_not_compositional: true  # H4 FAIL (p=0.223)
      linkers_not_compositional: true  # H7 FAIL (p=0.151)
      provenance: "C1039, C1040, C1041"

  ab_relationship:  # C846
    model: "Pool-based, not address-based"
    statement: "A paragraphs and B programs overlap in vocabulary (pool-based, not address-based)"
    best_match_lift: "2.49x raw, 1.20x pool-size-controlled"
    hub_concentration: "Top 10 A paragraphs capture 85.9% of best matches"
    pool_size_correlation: "Spearman rho = 0.694"
    provenance: "C846"

  structural_parallel:  # C854
    a_b_comparison:
      a_mean_lines: 4.8
      b_mean_lines: 4.37
      statistical_significance: "Mann-Whitney p=0.067 (not significant)"
      effect_size: "Cohen's d = 0.110 (negligible)"
    header_enrichment:
      a_ri_line1: "3.84x"
      b_ht_line1: "46.5%"
      b_ht_body: "23.7%"
    clustering:
      a_clusters: 5
      b_clusters: 5
      a_silhouette: 0.337
      b_silhouette: 0.237
    provenance: "C854"

  provenance: "C827, C834, C846, C847, C848, C849, C850, C854"

participation:
  azc:
    registry_entries:
      participates: true
      shared_vocabulary: true
      vocabulary_overlap: true
    control_operators:
      participates: false
      azc_tokens_in_folios: 0
    provenance: "C441-C442, C484"

  ht:
    registry_entries:
      triggers_ht: "possible"
      correlation: "statistical, not functional"
    control_operators:
      triggers_ht: false
      single_char_rate_nearby: "3.2%"
    provenance: "C484"

  b_relationship:
    token_level_coupling: false  # C384 - no context-free token->folio lookup
    record_level_correspondence: "conditional"  # C384.a - via multi-axis constraint composition
    vocabulary_sharing: "statistical (shared domain)"
    mapping_type: "not addressable via single tokens"
    conditional_correspondence_permitted:
      - "multi-axis constraint composition"
      - "AZC legality routing"
      - "survivor-set collapse (C481)"
      - "bridge MIDDLE topological selection (C1013)"
      - "geometric viability alignment via bridge backbone (C1014)"
      - "bridge conduit mediation — bridge MIDDLEs carry 3.8x more archetype-predictive information than non-bridges in B folio dynamical behavior (C1016)"
      - "dark pipeline identification channel — 300 PP MIDDLEs produce exclusively HT/UN tokens in B, built from bridge atoms (C1137, C1141)"
      - "multi-dimensional PP convergence at RECORD level"
    section_distribution:
      H_in_B: "91.6% (76/83 folios)"
      P_in_B: "8.4% (7/83 folios)"
      T_in_B: "0% (0/83 folios)"

    # Full morphological filtering cascade (C502.a)
    filtering_cascade:
      middle_only: { legal: "257 tokens (5.3%)", filtered: "94.7%" }
      middle_plus_prefix: { legal: "92 tokens (1.9%)", additional_reduction: "64%" }
      middle_plus_suffix: { legal: "130 tokens (2.7%)", additional_reduction: "50%" }
      full_morphology: { legal: "38 tokens (0.8%)", additional_reduction: "85% beyond MIDDLE" }
      provenance: "C502.a"

    # A-record filtering validation (C824-C826)
    filtering_validation:

      mechanism_confirmation:  # C824
        mean_filtering_rate: "81.3%"
        pp_count_correlation: "rho=+0.734 (more PP = more survival)"
        aggregation_effect:
          line_level: "11.2% survival"
          paragraph_level: "31.8% survival"
          folio_level: "50.0% survival"
        routing_lift: "82.9% of A-records have >2x routing lift"
        provenance: "C824"

      routing_topology:  # C825
        model: "Continuous, not discrete"
        viability_distribution: "Continuous gradient, not categorical bins"
        provenance: "C825"

      model_reconciliation:  # C826
        correct_model: "Token filtering (C502)"
        rejected_model: "Subset viability"
        provenance: "C826"

      provenance: "C824, C825, C826"

      viability_landscape:  # C1013, C1014
        bridge_mechanism:
          bridge_count: 85  # out of 972 MIDDLEs
          selection_principle: "Topological generality (frequency AUC=0.978)"
          hub_universal_coverage: "100% (23/23)"
          dark_pipeline_disjoint: "0 shared MIDDLEs between bridge (85) and dark pipeline (300) at MIDDLE level (C1139)"
          atom_substrate_role: "Bridge atoms are building blocks for dark-pipeline compounds (86% of atom types, 96.5% compound coverage) — MIDDLE-level disjointness coexists with atom-level derivation (C1141)"
          provenance: "C1013, C1139, C1141"
        geometric_alignment:
          manifold_viability_r: 0.914  # Mantel p=0.001
          hub_removed_stronger: true  # ratio=1.031
          size_independent: true  # retention=100.1%
          class_propagation_r: 0.622
          bridge_signal_share: "91% (r=0.905 vs non-bridge r=0.194)"
          provenance: "C1014"
        bridge_density_dynamics:
          mean_folio_bridge_density: 0.727  # 72.7% of manifold MIDDLEs per folio are bridges
          bridge_archetype_ari: 0.141  # bridge-only manifold features predict B dynamical archetypes
          nonbridge_archetype_ari: 0.037  # non-bridge features carry essentially no archetype information
          bridge_advantage: "3.8x"  # bridge/non-bridge ARI ratio
          bridge_density_vs_axm_self: { rho: -0.308, p: 0.009 }  # more bridges = weaker attractor = more dynamical options
          interpretation: "Bridge backbone is the geometry→dynamics conduit — the A-derived vocabulary that directly shapes B's macro-state behavior at folio level"
          b_internal_degeneracy: "At the B corpus level, all 85 unique MIDDLEs are bridges (100% coverage; C1020). Bridge density 0.727 is the per-folio A-manifold metric. The bridge concept distinguishes A→B crossover vocabulary, not a B-internal partition."
          provenance: "C1016, C1018, C1020"

        dark_pipeline:  # A-side properties of the identification channel
          population: 300  # PP MIDDLEs that bypass B grammar
          compound_rate: "66.7%"
          section_concentration: "Herf 0.716 (strongly section-specific)"
          a_to_b_flow:
            uniformity: "cosine 0.9997 (A folio distribution ≈ B grammar distribution)"
            concentration: "12 A folios cover 100% of B classified grammar; f58v alone at 60.7%"
          bridge_disjoint: "0 shared MIDDLEs with bridge set (C1139)"
          atom_substrate: "Built from bridge atoms (86% of atom types, C1141)"
          bridge_anticorrelation: "Folio-level dark-pipeline and bridge token rates anti-correlate (r=-0.865, within-section r=-0.82 to -0.88); complementary distribution across the A->B pipeline (C1146)"
          note: "B-side behavioral characterization (C1134 frequency modulation, C1137 HT substrate, C1138 distinct grammar, C1147 interior enrichment, C1148 hyper-modulation) lives in BCSC"
          provenance: "C1135, C1136, C1139, C1140, C1141, C1146"

    provenance: "C299, C384, C384.a, C502.a, C824, C825, C826, C1013, C1014, C1016, C1135, C1136, C1139, C1140, C1141, C1146"

positional:
  within_line:
    grammar: "position-free"
    folio_initial_exception:
      failure_rate_pos1: "75%"
      failure_rate_pos2_3: "31%"
      suffix_compatibility: "100% with standard forms"
      p_value: "<0.0001"
      provenance: "C420"

  within_folio:
    adjacency_coherence:
      rate: "1.31x vocabulary sharing"
      driver: "Clustered minority, not uniform"
    clustering:
      clustered_rate: "31%"
      singleton_rate: "69%"
      mean_cluster_size: 3
      cluster_range: [2, 20]
      autocorrelation: 0.80
      vocabulary_divergence: "68% between clustered and singletons"
    provenance: "C346, C424"

  section_boundaries:
    suppression: "2.42x lower overlap at boundaries"
    cross_section_overlap: "9.7% Jaccard"
    hard_discontinuity: true
    provenance: "C260, C421"

  control_operator_boundary_bias:
    boundary_proximity_p: 0.0099
    mean_normalized_distance: 0.138
    random_baseline: 0.259
    folio_start_rate: "30%"
    folio_end_rate: "30%"
    prefix_regime_shift: "All 4 testable cases show >3% shift"
    provenance: "C484"


disallowed:
  - interpretation: "A tokens map to B folios (context-free)"
    reason: "No token-level or context-free lookup exists"
    status: "FALSIFIED"

  - interpretation: "Repetition encodes quantity or ratio"
    reason: "Magnitude has no downstream effect"
    status: "FALSIFIED"

  - interpretation: "A has sequential grammar"
    reason: "Transition validity is 2.1%"
    status: "FALSIFIED"

  - interpretation: "Prefixes are semantic categories"
    reason: "They are functional markers"
    status: "FALSIFIED"

  - interpretation: "A is lookup table for B"
    reason: "No addressable mapping mechanism"
    status: "FALSIFIED"

  - interpretation: "A encodes danger or hazard"
    reason: "Correlation is entirely frequency-driven"
    status: "FALSIFIED"

  - interpretation: "Control operators are headers or section markers"
    reason: "No semantic category evidence"
    status: "UNSUBSTANTIATED"

  - interpretation: "A is generative or producible"
    reason: "A is maintained, not produced"
    status: "FALSIFIED"



```

---

# Currier B Grammar Contract

```yaml

meta:
  name: "Currier B Structural Contract"
  acronym: "BCSC"
  version: "3.11"
  date: "2026-02-13"
  status: "ACTIVE"
  layer_type: "grammar contract"
  derived_from: "Tier 0-2 constraints (structural); Tier 3 operational layer clearly marked"
  governance: |
    BCSC is NOT authoritative. Constraints are authoritative.
    BCSC describes the internal grammar of Currier B.
    Do not edit without updating source constraints first.
    Sections marked [TIER 3] contain behaviorally-derived interpretations
    that are conditional on external alignment (Brunschwig). These are
    included for operational grounding but do not carry Tier 0-2 authority.

scope:
  system: "Currier B"
  coverage: "61.9% of tokens, 83 folios"
  function: "What a valid Currier B program is, internally"
  a_agnostic: true  # Does not reference Currier A
  azc_agnostic: true  # Does not reference AZC mechanics
  semantic_status:
    structural_correlations: true  # MIDDLEs have measurable behavioral profiles (Tier 2)
    behavioral_glosses: "Tier 3 (conditional on Brunschwig alignment)"
    referential_content: false  # No substance/material identification from tokens (C120, C171)
    token_translation: false  # No natural-language translation recoverable (C120)

# Explicit ownership declaration
ownership:
  bcsc_describes:
    - grammar_structure
    - kernel_roles
    - hazard_topology
    - convergence_behavior
    - program_structure
    - recovery_architecture
    - vocabulary_architecture
    - execution_syntax
    - morphological_architecture  # Added v3.0: TOKEN decomposition, PREFIX/MIDDLE/SUFFIX roles
    - paragraph_execution_model  # Added v3.0: spec→exec gradient, startup patterns
    - operational_layer  # Added v3.0: Tier 3 behavioral glosses for context grounding
  bcsc_does_not_describe:
    - currier_a_entries
    - azc_mechanics
    - process_domain_identity  # Revised v3.0: "what substance" is irrecoverable, but "what kind of operation" has Tier 3 glosses

guarantees:
  - id: "GRAMMAR_UNIVERSAL"
    statement: "49-class grammar applies to all 83 folios without exception"
    provenance: "C121, C124"

  - id: "FORTY_NINE_CLASS_OPTIMALITY"
    statement: "49-class is the optimal resolution for transition dynamics; token-level Markov is 38% worse due to sparsity; suffix conditioning reduces next-class entropy by only 5.6% (0.259 bits), not justifying state-space doubling"
    provenance: "C1004"

  - id: "TOTAL_COVERAGE"
    statement: "Every Currier B token parses; zero non-executable"
    provenance: "C115, C124"

  - id: "CONVERGENT_ARCHITECTURE"
    statement: "Grammar targets single stable state (STATE-C)"
    provenance: "C074, C079, C084"

  - id: "HAZARD_TOPOLOGY_FIXED"
    statement: "17 forbidden transitions in 5 classes are DISFAVORED (~65% compliance, not absolute)"
    provenance: "C109, C789"

  - id: "KERNEL_CENTRALITY"
    statement: "k, h, e form irreducible morphological core governing within-token construction"
    provenance: "C089, C521, C522"

  - id: "LINE_FORMALITY"
    statement: "Lines are formal control blocks, not scribal wrapping"
    provenance: "C357-C360"

  - id: "LINK_PHASE_MARKER"
    statement: "LINK marks boundary between monitoring and intervention"
    provenance: "C366"

  - id: "DESIGN_ASYMMETRY"
    statement: "Hazard exposure clamped; recovery architecture free"
    provenance: "C458"

  - id: "CONDITIONAL_ENTROPY_SYMMETRIC"
    statement: "Grammar constraints are bidirectional (H(X|past)=H(X|future)), but execution is directional (transition probabilities uncorrelated). Resolution: PREFIX is the symmetric router (MI asymmetry 0.018 bits), MIDDLE is the directional executor (MI asymmetry 0.070 bits, 4x PREFIX). FL tokens show highest role-specific directionality (JSD 0.311)."
    provenance: "C391, C886, C1024"

  - id: "CLOSED_LOOP_ONLY"
    statement: "Execution is closed-loop control, not batch, decision tree, or state machine"
    provenance: "C171"

  - id: "MACRO_AUTOMATON_COMPRESSION"
    statement: "49 instruction classes compress to 6 macro-states (8.17x) with spectral gap 0.896; EN/AX merge, FL splits HAZ/SAFE; non-geometric dwell is aggregation artifact; partition is MINIMAL (no coarser grouping preserves invariants); geometrically independent of discrimination manifold at both corpus and folio level (ARI=0.163, with bridge backbone mediating weak geometry→dynamics coupling); dynamically characterized (full transition matrix, stationary distribution matches empirical within 1.2%); macro-automaton is a LOSSY PROJECTION of the 49-class chain — adds zero generative power (M3 ties M2; C1025); paragraph-level structure operates below its resolution floor (C1022)"
    provenance: "C976, C977, C978, C1006, C1010, C1011, C1015, C1016, C1022, C1025"

  - id: "GENERATIVE_SUFFICIENCY_AND_NECESSITY"
    statement: "The 49-class first-order Markov transition matrix + 17 forbidden MIDDLE pair suppression is both SUFFICIENT (reproduces 80% of measurable structure; M2 frontier, C1025) and NECESSARY (class shuffle within macro-states breaks 5/10 topology-sensitive metrics, spectral gap z=8.85; forbidden injection breaks 4/10; C1026). The 6-state macro-automaton adds zero generative power (M3 ties M2). Compositional generation (PREFIX×MIDDLE×SUFFIX product) OVER-generates (4.2% hallucination; real vocabulary is a curated subset). Token identity within class is PARTIAL — MIDDLE-level forbidden constraints leak through class boundaries (z=3.51)."
    provenance: "C1025, C1026"

  - id: "MACRO_STATE_DYNAMICS"
    statement: "6-state macro-automaton has full 6×6 transition matrix: AXM is a massive attractor (self=0.697, gravitational pull=0.642), FL_SAFE is a fleeting terminal (self=0.023, return time=117.7 steps, NOT absorbing), CC is a pure initiator (self=0.041); system is ergodic (spectral gap=0.896, mixing time=1.1 steps, stationary matches empirical within 1.2%). Folio-level decomposition reveals 6 dynamical archetypes (silhouette=0.185) that are orthogonal to the 4 REGIMEs (ARI=0.065); REGIME+section explain only 33.7% of transition variance, with 66.3% program-specific. Folio-level AXM self-transition decomposes as: REGIME+section (42.0%) + PREFIX entropy (5.1%) + hazard density (6.1%) + bridge geometry (6.3%) + non-linear residual (40.1%)"
    provenance: "C1015, C1016, C1017"

  - id: "FL_ROUTING_ASYMMETRY"
    statement: "FL_HAZ/FL_SAFE split is morphologically routed by PREFIX: da is the unique bi-directional FL router (5 HAZ, 5 SAFE, Fisher OR=126.67, p≈0); ar is a pure FL_SAFE selector (5/5=100%, binomial p≈0 vs 2.5% base rate); no other PREFIX has ≥2 tokens in each FL state"
    provenance: "C1015, C586"

  - id: "PREFIX_MDL_OPTIMALITY"
    statement: "PREFIX is the MDL-optimal single morphological component for macro-state routing at corpus scale (N=16,054): rank 1/4, 33.9% compression vs baseline; BIC penalty accounts for model complexity"
    provenance: "C1015"

  - id: "BRIDGE_CONDUIT_MECHANISM"
    statement: "Bridge MIDDLE backbone (85 MIDDLEs spanning A→B) mediates geometry→dynamics coupling at folio level: bridge-only manifold features predict dynamical archetypes with ARI=0.141 vs non-bridge ARI=0.037 (3.8x); non-bridge MIDDLEs carry essentially zero archetype-predictive information. All 85 unique B corpus MIDDLEs are bridges (100% degeneracy; C1020) — bridge/non-bridge distinguishes A→B crossover vocabulary, not a B-internal partition. The bridge effect is geometric, not densimetric. Bridge centroid PC1 in the 100D discrimination manifold adds ΔR²=0.063 (F=9.58, p=0.003) beyond all morphological features (PREFIX, hazard density), confirming that bridge geometry is a load-bearing dynamics predictor. PC1 is partially redundant with hub frequency gradient (rho=0.568; C1018), but the non-redundant component still significantly differentiates archetypes (F=3.56, p=0.006); PC1 represents a HUB_UNIVERSAL↔STABILITY_CRITICAL gradient"
    provenance: "C1016, C1017, C1018, C1020, C1013, C1014"

  - id: "FOLIO_DYNAMICAL_ARCHETYPES"
    statement: "72 folios with sufficient transitions (N≥50) cluster into 6 dynamical archetypes organized along an AXM attractor strength axis: 'strong attractor' (AXM self=0.82, n=10) to 'active interchange' (AXM self=0.47, n=7). Archetypes are nearly orthogonal to REGIMEs (ARI=0.065) and weakly aligned with sections (ARI=0.185). Forgiveness = AXM attractor strength (rho=0.678, 6 Bonferroni-significant features). Archetype-specific dynamics show suggestive non-linearity: PREFIX slope is positive in archetype 5 (β=+0.024, but n=7, bootstrap CI spans zero — not established; C1018) and hazard slope is positive in archetype 6 (β=+0.009, permutation p=0.014 but bootstrap CI spans zero — directionally supported, not robust; C1018); mean within-archetype R²=0.230 vs global R²=0.534. Archetypes are discriminated by 8 features across 5 families; strongest: k_frac (F=15.81), SAFETY_BUFFER fraction (F=11.37), HAZARD_TARGET fraction (F=5.73). Archetype 6's hazard tolerance is explained by 1.7x SAFETY_BUFFER enrichment (p=0.003; C1018)"
    provenance: "C1016, C1017, C1018"

  - id: "AFFORDANCE_BIN_SYSTEM"
    statement: "972 MIDDLEs classify into 9 functional bins by affordance signature; chromatic number 3 for PREFIX-lane interaction; HUB_UNIVERSAL (23 MIDDLEs) monopolizes all 17/17 forbidden transitions"
    provenance: "C995, C996, C997, C1000"

  - id: "PREFIX_DUAL_ENCODING"
    statement: "PREFIX simultaneously encodes content (lane, suffix compatibility) and line position; positional grammar is regime-invariant (p=0.97)"
    provenance: "C1001"

  - id: "FOLIO_VOCABULARY_UNIQUENESS"
    statement: "98.8% of folios contribute unique vocabulary appearing in no other folio"
    provenance: "C531, C532"

  - id: "FOLIO_COUNT_STRUCTURAL"
    statement: "83 folios determined by vocabulary coverage, not arbitrary"
    provenance: "C535"

  - id: "CLASS_MEMBER_DIFFERENTIATION"
    statement: "Grammar universal at class level; differentiation occurs at token level within classes"
    provenance: "C506.b, C537"

  - id: "EXECUTION_SYNTAX"
    statement: "Lines follow a positional role grammar: SETUP→WORK→CHECK→CLOSE"
    provenance: "C556"

  - id: "AX_BEHAVIORAL_COLLAPSE"
    statement: "19 AX classes collapse to ≤2 effective behavioral groups; position is the only differentiator"
    provenance: "C572"

  - id: "AX_VOCABULARY_SCAFFOLD"
    statement: "AX is the scaffold layer of the shared cross-system vocabulary: 98.2% PP MIDDLEs, PREFIX-determined role"
    provenance: "C567, C568, C571"

  - id: "MORPHOLOGICAL_COMPOSITIONALITY"
    statement: "Every token decomposes into [ARTICULATOR] + PREFIX + MIDDLE + [SUFFIX] with predictable combination rules"
    provenance: "C267, C382, C383"

  - id: "PAIRWISE_COMPOSITIONALITY"
    statement: "TOKEN information is fully captured by pairwise component interactions (PREFIX x MIDDLE, PREFIX x SUFFIX, MIDDLE x SUFFIX); no three-way synergy exists (Co-I < 0.02 bits on all 4 targets; R-squared increment = 0)"
    provenance: "C1003"

  - id: "PREFIX_MIDDLE_SELECTIVITY"
    statement: "PREFIX selects MIDDLE family (102 forbidden combinations) and transforms MIDDLE behavior (within-MIDDLE between-PREFIX JSD = 97.5% of between-MIDDLE JSD); PREFIX channels macro-state selection (76.7% binary FL entropy reduction via positive inclusion; 41.0% entropy reduction across full 6-state partition); 40.2% of MIDDLEs span multiple macro states depending on PREFIX. Within-MIDDLE routing is genuine (78.7% entropy reduction, z=65.59, p≈0), 80.1% non-positional (survives position-preserving shuffling, z=41.78), and REGIME-invariant (range 0.785–0.832, ratio=1.06 across all 4 REGIMEs)"
    provenance: "C911, C661, C1012, C1015, C1017"

  - id: "PARAGRAPH_EXECUTION_GRADIENT"
    statement: "Paragraph body lines follow a specification→execution gradient: early lines have rare/unique vocabulary (specification), late lines have universal vocabulary (generic execution loop)"
    provenance: "C932, C933, C934"

  - id: "HT_OPERATIONAL_REDUNDANCY"
    statement: "HT/compound tokens contain operational content that is redundant with body simple MIDDLEs (71.6% atom hit rate vs 59.2% random). Removal doesn't change outcomes because of redundancy, not emptiness."
    provenance: "C404, C935"

invariants:
  grammar_universality:
    statement: "Same 49 classes apply to every folio"
    provenance: "C124"

  convergence_dominance:
    statement: "Majority of programs terminate in STATE-C"
    provenance: "C074, C084, C323"

  hazard_asymmetry:
    statement: "Most forbidden transitions are directional"
    provenance: "C111"

  line_invariance:
    statement: "Grammar violations do not cross line boundaries"
    provenance: "C360"

  constraint_symmetry:
    statement: "Grammar constraints are bidirectional; execution is directional. PREFIX routes symmetrically; MIDDLE executes directionally (4x asymmetry ratio). FL tokens are most directionally asymmetric role."
    provenance: "C391, C886, C1024"

  kernel_boundary_adjacency:
    statement: "Classes containing kernel characters tend to be hazard-involved"
    provenance: "C107, C522"

  class_member_differentiation:
    statement: "Grammar is universal at class level, differentiation at token level"
    provenance: "C506.b, C537"

  folio_vocabulary_minimality:
    statement: "81/82 folios required for complete vocabulary coverage"
    provenance: "C535"

  execution_syntax:
    statement: "Lines follow SETUP→WORK→CHECK→CLOSE positional grammar"
    provenance: "C556, C562"

  energy_flow_anticorrelation:
    statement: "ENERGY and FLOW roles are anticorrelated across sections"
    provenance: "C551"

  ax_behavioral_collapse:
    statement: "19 AX classes do not form distinct behavioral groups"
    provenance: "C572"

  regime_syntax_invariance:
    statement: "Line syntax is INVARIANT across all four REGIMEs"
    provenance: "C821"

  regime_cc_position_invariance:
    statement: "CC token positions are INVARIANT across REGIMEs"
    provenance: "C822"

  regime_bigram_partial_variation:
    statement: "Bigram transition patterns show PARTIAL REGIME variation"
    provenance: "C823"

  morphological_compositionality:
    statement: "TOKEN = [ARTICULATOR] + PREFIX + MIDDLE + [SUFFIX] is universal"
    provenance: "C267, C382"

  prefix_middle_selectivity:
    statement: "PREFIX constrains which MIDDLE families are allowed (102 forbidden pairs)"
    provenance: "C911"

  prefix_positional_grammar:
    statement: "PREFIX encodes line position independently of regime"
    provenance: "C1001"

  pairwise_interaction_sufficiency:
    statement: "Pairwise morphological component interactions capture all exploitable TOKEN structure; no three-way synergy"
    provenance: "C1003"

  prefix_routing_regime_invariance:
    statement: "PREFIX macro-state routing magnitude is invariant across REGIMEs (range 0.785–0.832, ratio=1.06); REGIME modulates transition matrix weights (C979) but NOT the PREFIX routing mechanism itself"
    provenance: "C1017"

  dwell_shape_regime_invariance:
    statement: "Weibull dwell shape (k=1.55) is invariant across REGIMEs; REGIME modulates scale only"
    provenance: "C1006"

  generative_specification_bracketed:
    statement: "The grammar's minimal executable specification is bracketed: 49-class Markov + 17 forbidden pairs is both sufficient (C1025) and necessary (C1026); everything else (macro-automaton, PREFIX routing, tensor curvature, archetype dynamics) is secondary structure"
    provenance: "C1025, C1026"

grammar:

  classification:
    token_types: 479
    instruction_classes: 49
    compression_ratio: "9.8x"
    coverage: "100%"
    exceptions: 0
    optimality: "49-class is optimal: token-level (479 states) overfits by 38%; suffix-augmented (98 states) gains only 5.6%; 6-state macro underfits but useful as coarse view (perplexity 2.75 vs 28.76 vs 39.73)"
    provenance: "C121, C124, C1004"

  primitives:
    count: 10
    characters: ["s", "e", "t", "d", "l", "o", "h", "c", "k", "r"]
    provenance: "C085"

  properties:
    universal: true
    compositional: true
    over_specified: true
    reducible_classes: "~40% (deliberate)"
    provenance: "C121, C411"

morphology:
  # Added v3.0: The structural decomposition of tokens is proven (Tier 2).
  # This section describes HOW tokens are built, not what they mean.

  token_structure:
    formula: "[ARTICULATOR] + PREFIX + MIDDLE + [SUFFIX]"
    provenance: "C267, C382, C383"
    components:
      ARTICULATOR:
        required: false
        count: "~9 forms"
        function: "Optional refinement layer"
        example: "y- in ychody"
        provenance: "C267"
      PREFIX:
        required: true  # Most tokens have a prefix; unprefixed tokens exist but are a specific category
        common_prefixes: ["qo", "ch", "sh", "da", "sa", "ok", "ot", "ol", "lk", "lch", "te", "pch", "tch"]
        function: "Determines operational channel and MIDDLE family selection"
        selectivity: "102 forbidden PREFIX×MIDDLE combinations"
        behavioral_transformation: "Within-MIDDLE between-PREFIX JSD = 97.5% of between-MIDDLE JSD"
        macro_state_routing: "78.7% within-MIDDLE entropy reduction (genuine, not C662 tautology); 80.1% non-positional; REGIME-invariant (ratio=1.06)"
        provenance: "C267, C911, C661, C662, C1017"
      MIDDLE:
        required: true  # Core semantic carrier
        core_count: 75  # Core MIDDLEs appearing across many folios
        total_unique: 1339
        function: "Primary operational vocabulary — determines WHAT happens"
        compound_structure: |
          MIDDLEs can be simple (single atom: k, e, ch, edy) or compound
          (multiple atoms: opcheodai = op+ch+e+od+ai). 100% of compounds
          decompose into core atoms. Compound rate: 31.5% (grammar types),
          45.8% (HT/UN types). Dark-pipeline compounds are built from
          bridge atoms (86% of atom types, 91.6% of occurrences, 96.5%
          compound coverage) using a modified construction grammar (50%
          agreement with C1065 atom ordering, gateway/terminal positioning
          preserved). C935, C1141, C1142.
        provenance: "C267, C506.b, C935, C1141, C1142"
      SUFFIX:
        required: false
        unique_count: 35
        function: "Flow control — determines WHAT HAPPENS NEXT after the operation"
        sequential_state: "SUFFIX is a within-token modifier and positional/sequential grammar participant, but NOT a sequential state carrier. Only 1/17 testable classes shows suffix-differentiated transition distributions after Bonferroni correction (C1004)."
        suffix_strata: |
          EN: 17 types, 39% bare (suffix-rich, most flow options)
          AX: 19 types, 62% bare (moderate)
          FL: 2 types, 94% bare (suffix-depleted)
          FQ: 1 type, 93% bare (suffix-depleted)
          CC: 0 types, 100% bare (suffix-free)
        provenance: "C267, C382, C588, C1004"

  prefix_channel_architecture:
    # Tier 2 structural fact: PREFIX selects MIDDLE family and transforms behavior
    # The "channel" label is descriptive shorthand, not a semantic claim
    statement: "Each PREFIX class selects for specific MIDDLE families, creating operational channels"
    channels:
      qo:
        selects: "k-family (k, ke, t, kch)"
        enrichment: "4.6-5.5x"
        forbidden: "e-family, infrastructure MIDDLEs"
        token_count: 4069
      ch_sh:
        selects: "e-family (edy, ey, eey)"
        enrichment: "2.0-3.1x"
        forbidden: "k-family, infrastructure MIDDLEs"
        token_count: "ch=3492, sh=2329"
      da_sa:
        selects: "infrastructure (iin, in, r, l)"
        enrichment: "5.9-12.8x"
        forbidden: "k-family, e-family"
        token_count: "da=1083, sa=579"
        fl_routing: "da is the UNIQUE bi-directional FL router — routes both FL_HAZ and FL_SAFE (Fisher OR=126.67, p≈0); da+{r,l,in,ir,m}→FL_HAZ; da+{ly,ry,iir,n}→FL_SAFE"
        fl_provenance: "C1015"
      ot_ol:
        selects: "h-family (ch, sh)"
        enrichment: "3.3-6.8x"
        forbidden: "k-family"
      ok:
        selects: "e-family + infrastructure (e, aiin, ar)"
        enrichment: "2.6-3.3x"
        forbidden: "k-family"
        domain_selector: "VESSEL/APPARATUS — MIDDLE provides action on vessel (C936 revised)"
        positional_behavior: "Late in line (mean 0.538 vs 0.484 non-ok)"
        sister_pair: "ot (C408) — ok=proactive vessel management, ot=corrective adjustment"
        note: "ok is NOT a verb. Same-MIDDLE pairing with other prefixes (378 pairs) confirms PREFIX selects target domain, MIDDLE provides action. Semantic label 'VESSEL' is Tier 3."
      ar:
        selects: "FL_SAFE MIDDLEs exclusively"
        purity: "5/5 = 100% FL_SAFE (binomial p≈0 vs 2.5% base rate)"
        positional_behavior: "Late in line (LINE_FINAL zone, 61% Q5)"
        note: "ar as PREFIX is a pure FL_SAFE selector — the only PREFIX with 100% purity for a non-AXM state (n≥3). Distinct from ar as MIDDLE (MEDIAL state index)."
        provenance: "C1015"
    provenance: "C911, C661, C662, C936, C1015"

  prefix_positional_zones:
    # Tier 2 structural fact: PREFIX encodes line position (dual encoding with content)
    statement: "PREFIXes occupy distinct line zones, regime-invariant"
    zones:
      LINE_INITIAL:
        prefixes: ["po", "dch", "so", "to", "tch", "pch", "sa", "lsh", "sh"]
        mean_position_range: "0.11-0.40"
        extreme: "po 86% Q1 (4.30x concentration)"
      CENTRAL:
        prefixes: ["qo", "ke", "ta", "ch", "da", "lk", "ok"]
        mean_position_range: "0.49-0.54"
      LINE_FINAL:
        prefixes: ["BARE", "ot", "ol", "ka", "ko", "or", "al", "ar"]
        mean_position_range: "0.56-0.74"
        extreme: "ar 61% Q5 (3.05x concentration)"
    variance_decomposition:
      prefix_alone_r2: 0.069
      middle_alone_r2: 0.062
      additive_r2: 0.118
      full_pp_with_interaction_r2: 0.168
    provenance: "C1001"

  prefix_sequential_grammar:
    statement: "PREFIX transitions are structured with forbidden and enriched sequences"
    key_enrichments:
      - pair: "sh→qo"
        sigma: "+20.5"
        interpretation: "sh opens (initial zone), qo continues (central zone)"
      - pair: "BARE→qo"
        sigma: "-14.4"
        interpretation: "Strong avoidance"
    cross_component_mi: "I(MIDDLE_t; PREFIX_{t+1}) = 0.499 bits"
    prefix_sequential_mi: "0.124 bits (10.4% of MIDDLE's 1.195 bits)"
    provenance: "C1001"

  morphological_phase_encoding:
    statement: "Morphological composition (PREFIX + SUFFIX) encodes control phase"
    phases:
      MONITORING:
        prefix: "da-"
        suffixes: ["-in", "-l", "-r"]
        link_proximity: "Adjacent"
        kernel_contact: "<5%"
      INTERVENTION:
        prefix: "ch-/sh-"
        suffixes: ["-edy", "-ey"]
        link_proximity: "Distant"
        kernel_contact: "100%"
    line_template: "ENTRY → MONITORING → LINK → INTERVENTION → EXIT"
    provenance: "C382"

  fl_state_index:
    statement: "FL MIDDLEs function as state indices marking progression through a process within each line"
    scope: "LINE-LEVEL (not paragraph-level)"
    gradient:
      - stage: "INITIAL"
        middles: ["ii", "i"]
        mean_position: "0.30-0.35"
      - stage: "EARLY"
        middles: ["in"]
        mean_position: "0.42"
      - stage: "MEDIAL"
        middles: ["r", "ar"]
        mean_position: "0.51-0.55"
      - stage: "LATE"
        middles: ["al", "l", "ol"]
        mean_position: "0.61-0.64"
      - stage: "FINAL"
        middles: ["o", "ly", "am"]
        mean_position: "0.75-0.80"
      - stage: "TERMINAL"
        middles: ["m", "dy", "ry", "y"]
        mean_position: "0.86-0.94"
    prefixed_fl_terminals:
      statement: "Prefixed FL MIDDLEs (dam, oly, daly, etc.) inherit state-indexing function"
      line_final_rate: "72.7%"
      operation_state_mapping: "Different ENERGY operations produce different FL terminal states"
      provenance: "C897"
    macro_state_routing:
      statement: "FL_HAZ vs FL_SAFE macro-state membership is determined by PREFIX, not MIDDLE alone"
      mechanism: "da routes both FL_HAZ and FL_SAFE; ar routes exclusively FL_SAFE; 40.2% of MIDDLEs span multiple macro states depending on PREFIX context. Within-MIDDLE routing is genuine (78.7% entropy reduction, z=65.59), 80.1% non-positional, and REGIME-invariant (ratio=1.06)"
      provenance: "C1015, C1017"
    character_encoding:
      early: "'i' character marks initial state"
      late: "Consonants (r, l, n, m) mark intermediate states"
      terminal: "'y' character marks terminal state"
    provenance: "C777, C897, C1015"


role_taxonomy:

  roles:
    CORE_CONTROL:
      function: "Execution boundaries"
      classes: "{10, 11, 12, 17}"
      token_share: "4.4% of B (~1023 tokens)"
      provenance: "C121, C557, C558, C560, C581, C788-C791"

    ENERGY_OPERATOR:
      function: "Energy modulation"
      class_count: 18
      classes: "{8, 31-37, 39, 41-49}"
      token_share: "31.2% of B (7211 tokens)"
      provenance: "C121, C573"

    AUXILIARY:
      function: "PREFIX-switched scaffold layer of shared cross-system vocabulary"
      class_count: 19
      classes: "{1, 2, 3, 4, 5, 6, 15, 16, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29}"
      token_share: "16.6% of B (~3852 tokens)"
      provenance: "C121, C563-C572, C583"

    FREQUENT_OPERATOR:
      function: "Common instructions"
      class_count: 4
      classes: "{9, 13, 14, 23}"
      token_share: "12.5% of B (2890 tokens)"
      provenance: "C121, C583, C587, C593-C597"

    HIGH_IMPACT:
      function: "Major interventions"
      class_count: 3
      status: "LEGACY — classes absorbed into ENERGY_OPERATOR per C573"
      provenance: "C121"

    FLOW_OPERATOR:
      function: "Flow control - primitive substrate layer"
      abbreviation: "FO"  # Use "FO" to distinguish from FL (MIDDLE taxonomy)
      class_count: 4
      classes: "{7, 30, 38, 40}"
      token_share: "4.7% of B (1078 tokens)"
      provenance: "C121, C562, C582, C770-C777"

    LINK:
      function: "Monitoring/observation phase marker"
      provenance: "C366"

  functional_classification:
    roles_mapped:
      CC: "Core Control (execution boundaries, 4 classes, 4.4% of B)"
      EN: "Energy Operators (energy modulation, 18 classes, 31.2% of B)"
      FL: "Flow Operators (flow control, 4 classes, 4.7% of B)"
      FQ: "Frequent Operators (common instructions, 4 classes, 12.5% of B)"
      AX: "Auxiliary (scaffold, 19 classes, 16.6% of B)"
    provenance: "C547-C550, C573, C581-C583, C591"
    internal_structure:
      CC: "GENUINE_STRUCTURE (2 active + 1 ghost, 75% KW significant)"
      EN: "DISTRIBUTIONAL_CONVERGENCE (C574: grammatically equivalent, lexically partitioned)"
      FL: "GENUINE_STRUCTURE (hazard/safe split, 100% KW significant)"
      FQ: "GENUINE_STRUCTURE (3-group: CONNECTOR/PREFIXED_PAIR/CLOSER, C593; 13-14 Jaccard=0.000, C594; internal transitions chi2=111, C595)"
      AX: "COLLAPSED (positional gradient only, C572)"
    vocabulary_purity:
      # C584: Near-universal shared-vocabulary purity
      CC: "100% PP"
      EN: "100% PP (C575)"
      FL: "100% PP"
      FQ: "100% PP"
      AX: "98.2% PP (C567)"
    suffix_strata:
      # C588: Suffix role selectivity (chi2=5063.2)
      SUFFIX_RICH: "EN (17 types, 39% bare)"
      SUFFIX_MODERATE: "AX (19 types, 62% bare)"
      SUFFIX_DEPLETED: "FL (2 types, 94% bare), FQ (1 type, 93% bare)"
      SUFFIX_FREE: "CC (0 types, 100% bare)"
    hazard_direction:
      # C586: Roles have distinct hazard directionality
      FL: "SOURCE-biased (initiates 4.5x more than receives)"
      EN: "TARGET-biased (absorbs 11/19 corpus forbidden transitions)"
      FQ: "MIXED (both source and target)"
      CC: "NON-PARTICIPANT (0% hazard exposure)"
      AX: "NON-PARTICIPANT (0% hazard exposure)"

  gallows_dynamics:
    paragraph_marker:
      statement: "Gallows-initial tokens mark paragraph boundaries"
      initial_rate: "8.6% paragraph-initial vs 2.7% body"
      enrichment: "3.2x"
      provenance: "C864"
    folio_position:
      statement: "Gallows distribution varies by folio position"
      early_folio_rate: "higher"
      late_folio_rate: "lower"
      provenance: "C865"
    morphological_patterns:
      statement: "Gallows have distinct morphological contexts"
      t_context: "most common, broadest distribution"
      k_context: "kernel operator, restricted"
      p_context: "paragraph marker, positional"
      f_context: "rare, specialized"
      provenance: "C866"
    p_t_transition:
      statement: "P->T transitions follow paragraph dynamics"
      provenance: "C867"
    qo_chsh_independence:
      statement: "Gallows use is INDEPENDENT of QO/CHSH lane"
      provenance: "C868"
    functional_model:
      statement: "Gallows function as paragraph/section delimiters"
      provenance: "C869"
    provenance: "C863-C869"

kernel:
  scope: "CONSTRUCTION level - how tokens are built, not how they execute"

  operators:
    k:
      role: "ENERGY_MODULATOR"
      function: "Morphological contribution to energy-related tokens"
      position_in_token: "Early (mean 0.356)"
      provenance: "C103"

    h:
      role: "PHASE_MANAGER"
      function: "Morphological contribution to phase-related tokens"
      position_in_token: "Middle (mean 0.402)"
      provenance: "C104"

    e:
      role: "STABILITY_ANCHOR"
      function: "Morphological contribution to stability-related tokens"
      position_in_token: "Late (mean 0.565)"
      recovery_path_rate: "54.7%"
      provenance: "C105"

  construction_grammar:
    k_to_e: "4.02x (elevated)"
    h_to_e: "6.09x (elevated)"
    e_to_h: "0.004x (blocked)"
    h_to_k: "0.24x (suppressed)"
    provenance: "C521, KERNEL_STATE_SEMANTICS T9"

  properties:
    irreducible: true
    morphological_core: true
    h_to_k_suppressed: true  # Within-token only
    e_trigram_dominance: "97.2%"
    provenance: "C089, C332, C333, C521"

  relationships:
    e_class_dominance:
      provenance: "C339"

    kernel_bigram_ordering:
      provenance: "C332"

hazards:

  forbidden_transitions:
    count: 17
    compliance_rate: "~65%"  # C789: 34% violation rate - disfavored, not prohibited
    provenance: "C109, C789"

  failure_classes:
    thermodynamic_grounding: |
      All 5 failure classes validated as physically coherent distillation failure modes:
      15/15 glossed forbidden transitions map to recognizable failures;
      8/8 asymmetric pairs have coherent physical explanations (reverse = safe).
      Provenance: F-BRU-023 (THERMODYNAMIC_COHERENCE, Phase 334)

    PHASE_ORDERING:
      count: 7
      percentage: "41%"
      provenance: "C110"

    COMPOSITION_JUMP:
      count: 4
      percentage: "24%"
      provenance: "C109"

    CONTAINMENT_TIMING:
      count: 4
      percentage: "24%"
      provenance: "C109"

    RATE_MISMATCH:
      count: 1
      percentage: "6%"
      provenance: "C109"

    ENERGY_OVERSHOOT:
      count: 1
      percentage: "6%"
      provenance: "C109"

  properties:
    asymmetric_rate: "65%"
    distant_from_kernel_rate: "59%"
    suppressed_additional: 8
    provenance: "C111, C112, C386"

program_structure:

  folio:
    function: "Complete, self-contained program with unique vocabulary"
    count: 83
    macro_chaining: false
    unique_vocabulary_rate: "98.8%"  # 81/82 folios have unique MIDDLEs
    mean_unique_middles: 10.5
    count_structural: true  # 81/82 needed for coverage, not arbitrary
    redundancy_ratio: "1.01x"
    provenance: "C178, C531, C535"

  line:
    function: "Boundary-constrained control block with free interior and FL state tracking"
    regularity: "3.3x more regular than random"
    architecture: "BOUNDARY_CONSTRAINED_FREE_INTERIOR"  # C964
    boundary_markers:
      initial: ["daiin", "saiin", "sain"]
      final: ["am", "oly", "dy"]
      vocabulary_openness: "Boundary vocabulary is OPEN — 663 tokens cover 80% of openers; Gini 0.47 (C960)"
    link_suppressed_at_boundary: true
    grammar_line_invariant: true
    opener_properties:
      role_marker: "Opener is a ROLE marker, not an instruction header — specific token adds no predictive power beyond role (C959)"
      length_determination: "Opener class determines line length — 24.9% partial R-squared beyond folio+regime; folio+opener_token = 93.7% (C958)"
    token_level_constraints:
      positional_exclusivity: "192/334 common tokens are zone-exclusive (2.72x shuffle); STRUCTURAL per negative control (C956)"
      mandatory_bigrams: "26 mandatory token bigrams (obs/exp > 5x); includes or->aiin (C561) + 25 new (C957)"
      forbidden_bigrams: "9 forbidden token bigrams (obs=0, exp>=5); 2 genuinely token-specific: chey->chedy, chey->shedy (C957)"
      structural_origin: "Most token-level effects are STRUCTURAL (role/position driven), not lexical — confirmed by negative control (C956, C964)"
    fl_state_tracking:
      statement: "FL MIDDLEs track state progression WITHIN each line (C777)"
      scope: "LINE-LEVEL"
      range: "0.64 (64% of line span)"
      pattern: "[i/ii] → [r/ar] → [al/l/ol] → [o/ly/am] → [y/ry/dy]"
      prefixed_fl_line_final: "72.7% (C897)"
      provenance: "C777, C897"
    cross_line_information:
      statement: "Lines carry mutual information about neighbors despite formal independence"
      cross_line_mi: "0.521 bits"
      folio_fingerprint_auc: "0.994 (single line identifies folio)"
      provenance: "C971, C975"

    execution_syntax:
      positions:
        - position: "SETUP"
          location: "line-initial"
          dominant_roles: ["AX_INIT", "CC"]
          function: "Initialize scaffold and control state"
        - position: "WORK"
          location: "early-medial"
          dominant_roles: ["EN", "FQ"]
          function: "Primary operational activity"
          internal_ordering: "UNORDERED — tokens within WORK zone show no systematic sequence (Kendall tau ~ 0, p ~ 0.5); operations are a concurrent SET, not a sequence (C961)"
        - position: "CHECK"
          location: "mid-line"
          dominant_roles: ["EN", "AX_MED"]
          function: "Verification / adjustment"
        - position: "CLOSE"
          location: "line-final"
          dominant_roles: ["FL", "AX_FINAL", "CC"]
          function: "Flow resolution and boundary"
      triggers:
        daiin_trigger: "daiin marks WORK→CHECK transition (C557)"
        or_aiin_bigram: "or→aiin is strongest role-transition bigram (C561)"
      role_concentration:
        ENERGY: "medial (peaks at positions 3-6)"
        FLOW: "final (hierarchy FL > CC at line end, C562)"
        AX: "distributed across INIT/MED/FINAL sub-positions"
      phase_interleaving:
        statement: "KERNEL/LINK/FL phases show weak clustering but NOT sequential blocking (C962)"
        alternation_rate: "0.566 (shuffle 0.596, p<0.001)"
        sequential_compliance: "32.7% (shuffle 21.7%)"
        pair_ordering:
          LINK_to_KERNEL: "0.517 (neutral)"
          KERNEL_to_FL: "0.623 (moderately ordered)"
          LINK_to_FL: "0.659 (moderately ordered)"
        interpretation: "Phases are positional tendencies, not rigid blocks — consistent with C815 (eta-squared=0.015)"
      provenance: "C556, C557, C561, C562, C956-C964"
    provenance: "C357, C358, C359, C360, C556, C557, C561, C562, C777, C897"

  paragraph:
    # For comprehensive paragraph-as-unit model, see PSC (paragraph.psc.yaml)
    # PSC owns: definition, independence model, folio organization, A-B correspondence, stability
    # BCSC retains: B-specific execution patterns below (HT enrichment, spec->exec gradient, gallows dynamics)
    function: "Self-contained mini-program with header/specification/execution architecture"
    mean_per_folio: 7.1
    mean_lines_per_paragraph: 4.4

    header_body_structure:
      line1_compound_rate: "45.8%"
      body_compound_rate: "31.5%"
      line1_ht_rate: "44.9%"  # Legacy metric — HT = compound operational specifications (C935)
      body_ht_rate: "29.1%"
      delta: "+15.8pp"
      significance: "Wilcoxon z=13.63, p<10^-20, Cohen's d=0.721"
      compound_atom_prediction:
        statement: "Line-1 compound atoms predict body simple MIDDLEs at 71.6% hit rate (vs 59.2% random)"
        lift: "1.21x"
        interpretation: "Header compounds are compressed specifications that body lines unpack"
      provenance: "C840, C935"

    body_homogeneity:
      statement: "Body lines are compositionally homogeneous — only length progression (rho=-0.23), no role-composition change after length control (C963)"
      length_progression: "rho = -0.229, p = 0.001"
      composition_after_control: "EN/FL/CC fractions collapse to rho ~ 0 after controlling for line length"
      interpretation: "Paragraphs shrink toward their ends but each body line is a structurally equivalent control block"
      provenance: "C963, C677"

    execution_gradient:
      statement: "Body lines follow a specification->execution gradient"
      spec_exec_vocabulary:
        rare_middle_trend: "r=-0.97 (Q0→Q4)"
        universal_middle_trend: "r=+0.92 (Q0→Q4)"
        tokens_per_line: "10.3→8.7 (r=-0.97)"
        terminal_suffix_trend: "r=-0.89 (declining — parameter setting is early)"
        bare_suffix_trend: "r=+0.90 (increasing — continuation is late)"
        iterate_suffix_trend: "r=+0.83 (increasing — looping is late)"
        provenance: "C932"
      prep_verb_concentration:
        statement: "Prep verbs (pch, lch, tch, te) concentrate 2-3x in Q0 vs Q4"
        te_ratio: "2.7x (Q0/Q4)"
        pch_ratio: "2.8x"
        tch_ratio: "1.9x"
        lch_ratio: "1.3x"
        all_avg_position: "<0.45 (early half)"
        provenance: "C933"
      parallel_startup:
        statement: "Heat operations appear before prep operations in 65% of paragraphs"
        first_heat_position: 0.079
        first_prep_position: 0.212
        heat_first_rate: "65%"
        heat_prep_cooccurrence_trend: "r=-0.94 (Q0→Q4)"
        provenance: "C934"

    paragraph_zones:
      # Descriptive model of paragraph architecture
      statement: "Each paragraph has three functional zones"
      zones:
        - zone: "HEADER"
          lines: "Line 1"
          content: "Compound MIDDLEs (specification + identification)"
          unique_to_folio: "85.9% of line-1 HT tokens are folio-singletons"
          provenance: "C840, C870, C935"
        - zone: "SPECIFICATION"
          lines: "Early body (Q0-Q1)"
          content: "Rare/unique vocabulary, prep operations, parameter setting"
          provenance: "C932, C933"
        - zone: "EXECUTION"
          lines: "Late body (Q3-Q4)"
          content: "Universal vocabulary, iterate suffixes, generic control loop"
          provenance: "C932, C934"

    gallows_initial:
      paragraph_initial_rate: "8.6% vs 2.7% body"
      ratio: "3.2x enrichment"
      provenance: "C841, C864"
    ht_step_function:
      pattern: "Step function, not gradual decline"
      provenance: "C842"
    prefix_markers:
      provenance: "C843"
    self_containment:
      provenance: "C845"
    provenance: "C840-C845, C932-C935"

  folio_paragraph_architecture:
    # Paragraph-as-unit properties (C855-C862) are now owned by PSC (paragraph.psc.yaml)
    # BCSC retains this section for B-context reference; PSC is authoritative
    role_template:
      statement: "Paragraphs are NOT variations on a folio template"
      verdict: "PARALLEL_PROGRAMS model (independent mini-programs)"
      provenance: "C855, C862"
    vocabulary_distribution:
      statement: "Folio unique vocabulary is DISTRIBUTED across paragraphs, not concentrated"
      par1_share: "~15%"
      distribution: "Roughly uniform across ordinals"
      provenance: "C856"
    first_paragraph_ordinariness:
      statement: "Paragraph 1 is NOT structurally special"
      ht_rate_par1: "comparable to later paragraphs"
      unique_vocab_rate: "not elevated"
      provenance: "C857"
    paragraph_count_complexity:
      statement: "Paragraph count is weak proxy for folio complexity"
      correlation_with_unique_middles: "rho=0.42"
      provenance: "C858"
    vocabulary_convergence:
      statement: "Later paragraphs show WEAK vocabulary convergence"
      provenance: "C859"
    section_organization:
      statement: "Different sections show different paragraph patterns"
      bio_profile: "larger paragraphs (46 tok/par)"
      pharma_profile: "smaller paragraphs (13 tok/par)"
      provenance: "C860"
    link_hazard_neutrality:
      statement: "LINK and hazard density are NEUTRAL across paragraph ordinals"
      provenance: "C861"
    provenance: "C855-C862"

convergence:

  target:
    state: "STATE-C"
    type: "MONOSTATE"
    provenance: "C079, C084"

  terminal_distribution:
    state_c: "57.8%"
    transitional: "38.6%"
    initial_reset: "3.6%"
    provenance: "C323"

  gradient:
    direction: "STATE-C increases with position"
    provenance: "C325"

link_operator:

  function: "Morphological artifact — `ol` substring recruited differently by each role, not a unified functional layer"
  provenance: "C1174 (revises C366)"

  definition:
    marker: "'ol' substring in token"
    density: "13.2% of B tokens (3,047 tokens)"
    provenance: "C609"

  properties:
    # C365 REFUTED by C805: LINK shows boundary enrichment like HT
    spatially_uniform: false  # CORRECTED v1.7
    boundary_enriched: true
    first_token_rate: "17.2%"
    middle_token_rate: "12.4%"
    last_token_rate: "15.3%"
    mean_position: 0.476  # Earlier than baseline 0.504
    provenance: "C805 (refutes C365)"

  grammar_transitions:
    predecessor_bias: "NOT SIGNIFICANT (p=0.41)"
    successor_bias: "WEAK (p<0.001, enrichments ~1.1x)"
    provenance: "C804 (revises C366)"

  fl_relationship:
    # LINK and FL are inversely related (C807, C810)
    inverse: true
    distance: "LINK farther from FL (3.91 vs 3.38, p<0.0001)"
    correlation: "rho=-0.222 (negative)"
    direct_transitions: "0.70x expected (depleted)"
    provenance: "C807, C810"

  kernel_relationship:
    # LINK separated from kernel (C809)
    separated: true
    kernel_depletion: "k=0.86x, h=0.93x, e=0.82x"
    distance: "1.31 vs 0.41 (farther from kernel)"
    provenance: "C809"

  ht_overlap:
    # LINK-HT positive association (C806)
    odds_ratio: 1.50
    link_are_ht: "38.3%"
    ht_are_link: "16.6%"
    provenance: "C806"

  morphology:
    # 'ol' is a legitimate PP MIDDLE (C808)
    ol_is_pp: true
    ol_in_a_vocab: true
    link_pp_rate: "92.4%"
    provenance: "C808"

  complementarity:
    with_escalation: true
    provenance: "C340"

  functional_architecture:
    # Phase 418: LINK_FUNCTIONAL_ARCHITECTURE (C1170-C1174)
    overall_verdict: "LINK_MORPHOLOGICAL_ARTIFACT"
    vocabulary_stratification:
      cramers_v: 0.404
      cc_types: 1  # standalone `ol` only
      ax_prefix_fraction: "59.4%"
      un_types: 735
      hapax_fraction: "69.0%"
      provenance: "C1170"
    cross_role_behavior:
      consistent_roles: "0/4"
      link_jsd: 0.0138
      nonlink_jsd: 0.0128
      verdict: "ROLE_DOMINANT"
      provenance: "C1171"
    bio_excess:
      bio_density: "20.2%"
      en_span_enrichment: "4.65×"
      ax_span_enrichment: "2.15×"
      middle_depleted: true
      verdict: "BIO_TARGETED_ENRICHMENT"
      provenance: "C1172"
    boundary_behavior:
      entry_rate: "17.2%"
      interior_rate: "12.4%"
      exit_rate: "15.3%"
      entry_divergence_rho: -0.059
      exit_divergence_rho: -0.151
      dynamics_boundary_enrichment: "1.09×"
      verdict: "BOUNDARY_ENRICHED_PASSIVE"
      provenance: "C1173"
    interpretation: |
      The `ol` substring is a morphological component, not a functional marker.
      CC uses `ol` as standalone operator (continue instruction).
      AX uses `ol` as prefix (modifying auxiliary morphology).
      EN uses `ol` within/across MIDDLE boundaries.
      BIO excess is SPAN-targeted (morphological complexity, not functional LINK deployment).
      Boundary enrichment reflects positional preferences of ol-containing roles, not LINK-specific function.
    provenance: "C1174"

recovery:

  post_hazard_handling:
    primary_lane: "CHSH"  # e-rich (68.7%), 75.2% post-hazard
    secondary_lane: "QO"  # k-rich (70.7%), depleted near hazards (0.55x)
    provenance: "C601, C643, C645"

  lane_transition_pattern:
    # What C397/C398 actually measured (corrected interpretation)
    observation: "After CHSH hazard-source tokens, QO follows 25-47%"
    provenance: "C397 (REVISED), C398 (REVISED), C643"

  stability_anchor:
    operator: "e"
    function: "Anchors system to stable state"
    provenance: "C105"

  safe_precedence:
    provenance: "C399"

safety_buffer_architecture:

  statement: "22 safety buffer tokens prevent forbidden transitions by intervening between hazard pairs"
  physical_coherence: "22/22 buffers validated as physically coherent interventions (lane switches, work insertions); buffer REGIME distribution non-uniform: REGIME_1 enriched 1.86x (chi²=11.79, p=0.008)"
  physical_coherence_provenance: "F-BRU-023"
  buffer_rate: "0.12% of interior tokens"
  bin_distribution:
    HUB_UNIVERSAL: "68% (15/22)"
    STABILITY_CRITICAL: "18% (4/22)"
    FLOW_TERMINAL: "9% (2/22)"
  prefix_mechanism:
    qo_enrichment: "3.82x (46.7% vs 18.6% baseline, Fisher p=0.012)"
    interpretation: "QO-PREFIX selects safety buffer function within HUB"
  top_prevented_pairs:
    - pair: "chey → chedy"
      count: 9
    - pair: "chey → shedy"
      count: 5
  hub_sub_roles:
    HAZARD_SOURCE: ["ar", "dy", "ey", "l", "ol", "or"]
    HAZARD_TARGET: ["aiin", "al", "ee", "o", "r", "t"]
    SAFETY_BUFFER: ["eol", "k", "od"]
    PURE_CONNECTOR: ["d", "e", "eey", "ek", "eo", "iin", "s", "y"]
  behavioral_homogeneity: "0/14 KW dimensions significant — functional diversity beneath behavioral uniformity"
  exit_boundary_connection: "HAZARD_TARGET MIDDLEs accumulate at AXM exit boundaries (C1009) — linking safety/hazard vocabulary to gatekeeper mechanism"
  archetype_differentiation: "SAFETY_BUFFER enrichment differentiates archetypes: archetype 6 has 1.7x more SAFETY_BUFFER MIDDLEs than archetype 5 (0.124 vs 0.072, p=0.003), explaining archetype 6's anomalous hazard tolerance (C1018)"
  provenance: "C997, C1000, C1009, C1018, F-BRU-023"

axm_internal_architecture:

  dwell_dynamics:
    statement: "Non-geometric AXM dwell is a phase-type aggregation artifact, not temporal memory"
    mechanism: "32 AXM classes almost never repeat (mean run 1.054 at 49-class); long 6-state runs are diverse class sequences"
    null_model: "First-order Markov null reproduces empirical dwell (KS D=0.020, p=0.074)"
    weibull_shape: "k=1.55 globally; REGIME-invariant (range 0.096)"
    regime_modulation: "REGIME modulates dwell SCALE (lambda: 2.3-3.1) but NOT shape — consistent with C979. At folio level, REGIME explains only 14.9% of transition variance (eta²); section explains 24.3%; combined 33.7%. Archetype structure (6 clusters) is orthogonal to REGIME (ARI=0.065) — consistent with C1016. PREFIX routing mechanism itself is REGIME-invariant (ratio=1.06; C1017)"
    non_geometricity_gradient: "Correlates with class compression: AXM (32 classes) > FQ (4 classes) > FL_HAZ (2 classes, geometric)"
    provenance: "C1006"

  gatekeeper_mechanism:
    statement: "Five AUXILIARY classes {15, 20, 21, 22, 25} form exit-boundary specialists enriched 2-10x at AXM run exits"
    enrichment:
      class_22: "9.58x"
      class_21: "4.25x"
      class_15: "3.08x"
      class_20: "2.68x"
      class_25: "2.30x"
    properties:
      directional: "Exit-enriched, NOT entry-enriched (chi2=152.60, p<0.0001)"
      genuine: "Survives mid-line positional control (chi2=58.42, p=0.002)"
      low_entropy: "4.123 vs 4.555 bits (p=0.016) — constrained exit points"
      destination_agnostic: "No target-state routing specificity (p=0.286)"
      structural_role: "Gatekeepers MARK exit boundaries but do NOT CHANNEL exit destinations (JSD=0.0014, below null mean 0.0024; C1023). They are exit markers, not exit directors."
      peripheral: "Low betweenness centrality (p=0.514) — endpoints, not bridges"
      single_token: "No multi-step exit motif (pre-GK p=0.940, exit entropy matches baseline)"
      regime_contextual: "Specific gatekeeper class identity shifts across REGIMEs (mean cross-rho=-0.245) but mechanism is universal"
    provenance: "C1007, C1008, C1023"

  exit_curvature:
    statement: "HAZARD_TARGET MIDDLE density increases from ~10% at t-3 to ~16% at exit token (rho=-0.055, p=0.0001)"
    mechanism: "Compositional (which sub-role appears), NOT spectral-geometric (radial depth p=0.098)"
    subrole_enrichment: "Exit boundaries enriched in HAZARD_TARGET (22.7% vs 17.5%, chi2=13.89, p=0.003)"
    gatekeeper_spike: "GK fraction rises from ~2% at t-3 to 8.7% at t-0 — single-token switching"
    regime_invariance: "Curvature slope does NOT vary with REGIME intensity (p=0.200)"
    provenance: "C1009"

  interchange_state:
    statement: "FQ is the principal interchange state for AXM"
    exit_skyline: "AXM exits to FQ 57.1%, FL_HAZ 17.1%, CC 13.8%, AXm 9.4%, FL_SAFE 2.5%"
    entry_skyline: "AXM enters from FQ 55.1%, FL_HAZ 16.7%, CC 16.4%, AXm 10.6%, FL_SAFE 1.2%"
    provenance: "C1007"

macro_state_transition_matrix:

  statement: "Full 6×6 transition probability matrix computed from 13,645 consecutive token-pair transitions across all B lines (16,054 mapped tokens)"
  state_order: ["AXM", "AXm", "FL_HAZ", "FQ", "CC", "FL_SAFE"]

  # Row = FROM state, Column = TO state
  transition_probabilities:
    AXM:     { AXM: 0.697, AXm: 0.029, FL_HAZ: 0.052, FQ: 0.173, CC: 0.042, FL_SAFE: 0.008 }
    AXm:     { AXM: 0.682, AXm: 0.025, FL_HAZ: 0.062, FQ: 0.189, CC: 0.032, FL_SAFE: 0.010 }
    FL_HAZ:  { AXM: 0.565, AXm: 0.026, FL_HAZ: 0.106, FQ: 0.239, CC: 0.049, FL_SAFE: 0.016 }
    FQ:      { AXM: 0.591, AXm: 0.033, FL_HAZ: 0.073, FQ: 0.250, CC: 0.043, FL_SAFE: 0.009 }
    CC:      { AXM: 0.672, AXm: 0.033, FL_HAZ: 0.070, FQ: 0.176, CC: 0.041, FL_SAFE: 0.008 }
    FL_SAFE: { AXM: 0.698, AXm: 0.023, FL_HAZ: 0.070, FQ: 0.093, CC: 0.093, FL_SAFE: 0.023 }

  stationary_distribution:
    AXM: 0.667
    AXm: 0.029
    FL_HAZ: 0.060
    FQ: 0.192
    CC: 0.043
    FL_SAFE: 0.008
    max_deviation_from_empirical: "1.2%"

  expected_return_times:
    AXM: "1.5 steps (ever-present)"
    FQ: "5.2 steps (frequent excursion)"
    FL_HAZ: "16.5 steps (infrequent)"
    CC: "23.5 steps (rare)"
    AXm: "34.1 steps (rare variant)"
    FL_SAFE: "117.7 steps (extremely rare fleeting terminal)"

  dynamical_properties:
    axm_attractor: "Self-transition 0.697; gravitational pull from all non-AXM states = 0.642"
    fl_safe_fleeting: "Self-transition 0.023; NOT absorbing; immediate return to AXM (0.698)"
    cc_initiator: "Self-transition 0.041; exits to AXM 0.672 — pure start-then-leave"
    fl_haz_persistent: "Moderate self-transition 0.106; elevated FQ exit 0.239"
    ergodic: "Spectral gap = 0.896; mixing time = 1.1 steps"

  provenance: "C1015"

three_compression_architecture:

  statement: "Three orthogonal compressions of B grammar — tensor (variance), macro-automaton (topology), archetypes (dynamics) — are irreducibly independent"

  tensor_characterization:
    structure: "Morphological transition tensor T[PREFIX, MIDDLE_BIN, SUFFIX_GROUP, CLASS] has rank-8 pairwise-sufficient structure (97.0% variance, CP ≥ Tucker -21%)"
    automaton_orthogonality: "Tensor class factors do NOT recover 6-state partition (ARI=0.053); macro-automaton is an interpretive abstraction imposed by coarse-graining, not a natural tensor factorization"
    frequency_dominance: "Tensor's strongest AXM predictor (Factor 2, rho=-0.750) is a class-level frequency gradient (C986, rho=0.854 with class frequency), not structural gating (gatekeeper cosine=0.059)"
    rank_continuity: "Rank is continuous — CV cosine saturates at rank 4 (0.713); rank 6-12 within 0.006 of each other; no structural knee at rank 8"
    constraint_irreducibility: "Constraint filtering (35 forbidden/depleted pairs) cannot reconcile tensor and automaton — constrained ARI=0.007, WORSE than unconstrained 0.050 (permutation z=-0.22)"
    hub_simplicity: "HUB MIDDLEs carry simpler transition structure (effective rank 3 vs 8, PREFIX-diverse); consistent with universal connector role (C1000)"
    pairwise_confirmation: "Tucker decomposition at matched parameters performs 21% worse — no irreducible multi-axis interactions; confirms C1003 at tensor level"
    suffix_degeneracy: "SUFFIX is near-degenerate (2 SVD dims for 90% variance); confirms C1004"

  compression_summary:
    tensor: "Continuous variance landscape (rank 8, graded frequency structure)"
    automaton: "Discrete topological constraint skeleton (6 states, transition rules)"
    archetypes: "Categorical folio dynamical personalities (6 types, non-linear profiles)"
    independence: "ARI=0.053 (tensor vs automaton); silhouette=-0.040 (tensor vs archetypes); ARI=0.065 (archetypes vs REGIMEs)"

  bridge_dual_role: |
    Bridge MIDDLEs serve dual function: grammar backbone (all 85 classified
    MIDDLEs are bridges, C1020) AND morphological substrate for dark-pipeline
    compounds (86% of atom types are bridges, C1141). MIDDLE-level disjointness
    between bridge and dark pipeline (C1139) coexists with atom-level derivation
    (C1141) — dark-pipeline compounds are built FROM bridge atoms but share no
    complete MIDDLEs with bridges.

  provenance: "C1019, C1020, C1021, C1003, C1004, C1010, C1013, C1139, C1141"

design_freedom:

  clamped:
    - dimension: "hazard_exposure"
      freedom: "NO"
    - dimension: "intervention_diversity"
      freedom: "NO"

  free:
    - dimension: "recovery_operations"
      freedom: "YES"
    - dimension: "near_miss_handling"
      freedom: "YES"

  principle: "Risk is globally constrained; recovery strategy is locally variable"
  mechanism: "Recovery variation is mediated by AXM attractor strength — forgiving programs have higher AXM self-transition (rho=0.651), less FQ interchange; brittle programs have weaker attractors. C458's aggregate clamping (hazard CV=0.04-0.11) is the result of stable recovery channels (AXM self≈0.66, CV=0.174), not individual hazard transition stability (hazard CV=1.814). AXM basin depth decomposes into: REGIME+section (42.0%) + PREFIX entropy (5.1%) + hazard density (6.1%) + bridge geometry (6.3%) + non-linear archetype residual (40.1%). Archetype-specific slopes differ suggestively (sign changes observed but not statistically robust at current sample sizes; C1018), consistent with non-linear program-specific tuning"
  provenance: "C458, C1016, C1017, C1018"

control_loop:

  three_zones:
    kernel:
      function: "Active processing (k, h, e operators)"
      mean_position: 0.482
      density: "~69% of tokens contain kernel characters"
    link:
      function: "Monitoring/waiting phases ('ol' marker)"
      mean_position: 0.476
      density: "13.2% of tokens"
    fl:
      function: "State indexing and escape/recovery operations"
      mean_position: 0.576
      density: "4.7% of tokens"

  canonical_ordering:
    sequence: "daiin -> LINK -> KERNEL -> ol -> FL"
    positions: "0.413 -> 0.476 -> 0.482 -> 0.511 -> 0.576"
    significance: "daiin vs LINK p<0.001, KERNEL vs FL p<0.0001"
    provenance: "C813, C816"
    cc_integration:
      daiin_position: 0.413  # Earliest - initiates control loop
      ol_position: 0.511  # Medial - bridges to FL
      ol_derived_position: 0.515  # Medial - kernel interface

  phase_flexibility:
    # Phases have significant but weak positional preferences
    anova_f: 70.28
    anova_p: "<10^-73"
    eta_squared: 0.015  # Only 1.5% variance explained
    provenance: "C815"

  phase_relationships:
    link_fl:
      relationship: "Inverse/complementary (not adjacent)"
      direct_transitions: "0.70x expected"
      provenance: "C807, C810"
    fl_chaining:
      enrichment: "2.11x"
      loop_closure: "FL->KERNEL neutral (0.86x)"
      provenance: "C811"

  folio_predictors:
    # What predicts escape (FL) rate at folio level
    strongest: "KERNEL (rho=-0.528, p<0.0001)"
    provenance: "C814"

section_profiles:

  anticorrelation:
    statement: "ENERGY and FLOW roles are anticorrelated across sections"
    correlation: "r = -0.89"
    provenance: "C551"

  profiles:
    section_b:
      signature: "Highest ENERGY concentration"
      provenance: "C552"
    section_h:
      signature: "Highest FLOW concentration, lowest ENERGY"
      provenance: "C553"
    section_c:
      signature: "Balanced ENERGY/FLOW, highest AX density"
      provenance: "C554"
    section_s:
      signature: "Distinctive FQ elevation"
      provenance: "C555"

  section_differentiation_mechanism:
    statement: "74% of section JS divergence is explained by PP frequency modulation"
    mechanism: "Sections use the SAME PP vocabulary at DIFFERENT frequencies — frequency modulation of shared vocabulary, not vocabulary switching"
    js_explained: "74%"
    resolves: "C1049/C909 paradox (vocabulary is type-universal but frequency-specific)"
    provenance: "C1134"

vocabulary_architecture:

  class_level:
    coverage: "100%"
    folio_invariant: true
    provenance: "C121, C124"

  member_level:
    behavioral_heterogeneity: true  # Different MIDDLEs -> different transitions
    js_divergence: "73% of MIDDLE pairs have JS > 0.4"
    provenance: "C506.b"

  folio_uniqueness:
    unique_folio_rate: "98.8%"  # 81/82 folios
    mean_unique_per_folio: 10.5
    total_unique_middles: 858
    unique_share_of_total: "64%"
    only_non_unique_folio: "f95r1"
    dynamical_uniqueness: "66.3% of folio-level transition variance is program-specific (REGIME+section explain only 33.7%); vocabulary uniqueness parallels dynamical uniqueness"
    provenance: "C531, C1016"

  folio_exclusivity:
    b_exclusive_rate: "88%"  # Not in A
    pp_rate: "12%"  # A-derived
    azc_modulates: "shared PP vocabulary only, not folio identity"
    provenance: "C532"

  pp_pipeline_partition:
    statement: "404 PP MIDDLEs partition into four mutually exclusive, collectively exhaustive populations"
    bridge: 85       # Cross-system dynamical backbone (C1013)
    non_bridge_matched: 4  # Edge-case grammar participants (c, ch, cho, otc)
    dark_pipeline: 300     # HT/UN identification substrate (C1137)
    phantom: 15            # A-present, B-absent artifacts (all ch-/sh- prefixed)
    total: 404
    bridge_dark_disjointness: "0 shared MIDDLEs between bridge (85) and dark pipeline (300) — C1139"
    bridge_dark_anticorrelation:
      statement: "Dark-pipeline and bridge token rates are strongly anti-correlated at the folio level"
      overall_r: -0.865
      within_section_r: "-0.82 to -0.88 (all 4 testable sections)"
      section_r2: 0.193  # Section identity explains only 19.3% of dark density variance
      implication: "Complementary distribution: folios invest more in grammar execution (bridge) OR identification (dark pipeline), not both equally"
      provenance: "C1146"
    folio_balance_characterization:
      classification: "BRIDGE_DOMINANT (21) / BALANCED (41) / DARK_DOMINANT (20) by dark/bridge ratio quartiles"
      section_structured: "chi-sq=29.95, p<0.0001 — BIO=bridge-dom, PHARMA=dark-dom, RECIPE_B=balanced, HERBAL_B=mixed"
      dynamics_orthogonal: "ARI=-0.002 vs archetypes, rho=0.001 vs AXM — vocabulary balance is independent of control-plane dynamics"
      kernel_coupling: "Dark-dominant folios shift kernel profile: k_frac 0.314→0.226, h_frac 0.100→0.135; survives within RECIPE_B (p=0.002)"
      c1035_residual: "Balance does NOT explain the 57% irreducible AXM residual"
      provenance: "C1149, C1150, C1151"
    vocabulary_dynamics_layer_separation:
      statement: "Section-conditioned M2 captures vocabulary composition but not sequential dynamics or kernel engagement"
      class_dist_ratio: 1.48  # real/synth inter-folio JSD — near-captured
      axm_spread_ratio: 1.76  # real/synth AXM SD — uncaptured
      kernel_profile_ratio: 1.79  # real/synth k/h/e SD — uncaptured
      folio_fidelity: "87% of folios improved by section-conditioning (71/82)"
      layer_1: "Vocabulary composition — section-determined"
      layer_2: "Sequential dynamics + kernel engagement — program-specific"
      provenance: "C1152"
    generative_design_freedom:
      aggregate: 0.399  # fraction of folio variation not section-captured
      class_dist_uncaptured: 0.324
      axm_uncaptured: 0.432
      kernel_uncaptured: 0.440
      c1035_consistent: true  # AXM 43.2% vs C1035 57%
      c1016_note: "Lower than C1016 66.3% because class distribution IS section-captured (different metric layer)"
      provenance: "C1153"
    kernel_execution_universality:
      k_ratio_range: "1.82-2.32x across all sections (always program-specific)"
      e_ratio_range: "1.76-2.21x across all sections (tracks k-kernel)"
      h_ratio_captured: "BIO 1.29x, HERBAL 1.04x, COSMO 0.74x (section-determined)"
      h_ratio_uncaptured: "STARS_RECIPE 2.18x (program-specific)"
      implication: "Execution kernel (k/e) is always program-level; monitoring kernel (h) is domain-dependent"
      provenance: "C1154"
    paragraph_kernel_dynamics_residual_closure:
      statement: "Within-folio paragraph kernel diversity does not mediate the C1035 AXM residual"
      best_delta_r2: 0.0014  # trajectory slope variance — effectively zero
      loo_contributions: "all negative (overfitting)"
      within_section: "all |rho| < 0.16"
      implication: "C1035 residual confirmed closed at paragraph level; design freedom is genuinely program-specific"
      provenance: "C1155"
    line_position_transition_dynamics:
      statement: "49-class transition matrix differs strongly by line position zone"
      zone_jsd_range: "0.217-0.333 (all p<0.001 vs 1000 permutations)"
      axm_self_gradient: "0.730 (entry) → 0.704 (interior) → 0.633 (exit)"
      spectral_gap_range: "0.883-0.939"
      section_dependent: true  # KW p<0.0001
      generative_impact: "none — M2p 0/3 metrics improved"
      provenance: "C1156"
    boundary_divergence_residual:
      statement: "Per-folio boundary divergence mediates C1035 AXM residual — first successful predictor"
      delta_r2: 0.0845  # F=14.15, p=0.0004
      loo_improvement: "0.433 → 0.512"
      spearman_vs_axm: -0.732  # p<0.0001
      note: "Descriptive not generative — position conditioning does not improve M2"
      c1035_status: "partially reopened — ~49% irreducible remains"
      provenance: "C1157"
    entry_dominance:
      statement: "Entry zone drives 3.5x more AXM residual variance than exit zone"
      entry_delta_r2: 0.098  # F=16.63, p=0.0001
      exit_delta_r2: 0.028  # F=4.51, p=0.038
      entry_spearman: -0.692  # p<0.0001
      exit_spearman: -0.472  # p<0.0001
      note: "Contradicts gatekeeper exit hypothesis — predictive signal comes from line beginnings, not endings"
      provenance: "C1158"
    routing_shift:
      statement: "Boundary divergence is driven by inter-state routing changes, not AXM self-transition decay"
      axm_self_fraction: "3.2% of total transition delta"
      top_entry_shifts: "AXm→AXM (+0.124), FQ→AXM (+0.103)"
      top_exit_shifts: "CC→AXM (-0.296), FL_HAZ→AXM (-0.129)"
      implication: "Line is a reset→explore→handoff arc at routing level"
      provenance: "C1159"
    section_confound_independence:
      statement: "Section explains 70.2% of BD variance, but BD carries independent signal"
      section_r2_on_bd: 0.702
      partial_rho_bd_axm_given_section: -0.459  # p=0.0001
      bd_increment_over_section: 0.135  # F=17.28, p=0.0001
      loo_section_only: 0.259
      loo_section_plus_bd: 0.330
      provenance: "C1160"
    gatekeeper_partial_mediation:
      statement: "Gatekeeper classes explain ~30% of BD signal; 70% comes from non-gatekeeper routing"
      original_delta_r2: 0.085
      gk_free_delta_r2: 0.059  # 30.5% drop
      gk_density_vs_bd: "rho=0.016 (uncorrelated)"
      gk_free_bd_vs_axm: "rho=-0.673 (p<0.0001)"
      provenance: "C1161"
    opener_role_neutrality:
      statement: "Opener role distribution does not predict entry divergence"
      r2_roles_on_entry_div: 0.128
      best_role_rho: -0.195  # ENERGY, p=0.061
      role_entropy_rho: -0.116  # p=0.101
      note: "Entry mechanism operates below role-level identity; consistent with C959"
      provenance: "C1162"
    axm_return_rate_dominance:
      statement: "AXM return rate at entry is the dominant entry mechanism"
      rho_vs_axm_self: 0.841  # p<0.0001 — near-perfect
      rho_vs_entry_div: -0.510  # p<0.0001
      r2_on_entry_div: 0.318
      mean_return_rate: 0.707
      note: "Per-line opening routing pattern IS the folio's dynamical identity"
      provenance: "C1163"
    opener_routing_mediation:
      statement: "Opener routing partially mediates entry divergence (40% shrinkage)"
      coefficient_shrinkage: 0.406
      partial_rho_entry_div_surviving: -0.293  # p=0.013
      opener_features_dr2: 0.159  # F=13.01, p<0.000002
      entry_div_dr2: 0.068
      combined_r2: 0.815
      combined_loo: 0.669
      provenance: "C1164"
    axm_return_rate_residual_extension:
      statement: "AXM return rate extends AXM residual beyond entry divergence"
      incremental_dr2: 0.111  # F=30.95, p<0.000001
      loo_improvement: "0.543 → 0.696"
      total_bundle_dr2: 0.180  # entry_div + AXM_return vs C1035
      c1035_status: "substantially reopened — irreducible reduced ~57% → ~32%"
      provenance: "C1165"
    exit_divergence_redundancy:
      statement: "Exit JSD redundant after entry bundle control (partial rho=-0.097)"
      bivariate_rho_exit_axm: -0.710  # strong alone
      partial_rho_after_entry_bundle: -0.097  # p=0.101 — non-significant
      entry_exit_collinearity: 0.697  # rho(jsd_entry, jsd_exit)
      note: "Aggregate divergence metric collinear; directional routing metrics carry independent signal"
      provenance: "C1166"
    axm_departure_rate_extension:
      statement: "AXM departure rate at exit extends residual beyond entry bundle"
      incremental_dr2: 0.035  # F=11.80, p=0.0012
      loo_improvement: "0.696 → 0.745"
      closer_routing_r2: 0.338
      axm_departure_rho_exit_div: 0.509  # p<0.0001
      axm_departure_rho_axm_self: -0.687  # p<0.0001
      best_exit_feature: "axm_departure"
      note: "Exit signal is directional routing (AXM→non-AXM at exit), not aggregate divergence"
      provenance: "C1167"
    dual_boundary_architecture:
      statement: "Entry + exit = independent predictive channels for AXM self-transition"
      dual_model_r2: 0.852
      dual_model_loo: 0.732
      exit_increment_dr2: 0.039
      exit_increment_loo_gain: 0.036
      per_section_exit_dr2: {B: 0.189, H: 0.107, S: 0.100}
      sections_benefiting: 3  # out of 3 testable
      partial_rho_entry_exit: 0.259  # p=0.025 — correlated but not redundant
      c1035_trajectory: "~57% → ~49% → ~32% → ~27% irreducible"
      provenance: "C1168"
    residual_freedom_closure:
      statement: "AXM residual CLOSED at ~27% — genuine per-program design freedom"
      exhaustive_battery: "5 tests, 23 candidate predictors"
      univariate_holm_sig: 0  # out of 23
      rf_cv_r2: -0.141  # permutation p=0.375
      spatial_lag1_ac: 0.102  # permutation p=0.378
      regime_kw_p: 0.998  # perfect homogeneity
      c458_asymmetry: "SYMMETRIC — freedom not preferentially in recovery space"
      c1035_final_trajectory: "~57% → ~49% → ~32% → ~27% CLOSED"
      interpretation: "73% structurally determined (dual boundary model), 27% genuine per-program design freedom"
      provenance: "C1169"
    dark_pipeline_profile:
      compound_rate: "66.7%"
      section_concentration: "Herf 0.716 (strongly section-specific)"
      ht_substrate: "100% HT/UN tokens, 0% grammar tokens (C1137)"
    a_to_b_flow:
      uniformity: "cosine 0.9997 (A folio distribution ≈ B grammar distribution)"
      concentration: "12 A folios cover 100% of B classified grammar; f58v alone at 60.7%"
    provenance: "C1135, C1136, C1139, C1140"

  grammatical_consistency:
    slot_match_rate: "75%"
    adjacent_folio_class_ratio: "1.30x"  # vs non-adjacent
    provenance: "C533"

  minimality:
    min_folios_for_coverage: 81
    actual_folios: 82
    redundancy_ratio: "1.01x"
    max_pairwise_jaccard: "<50%"  # Zero pairs exceed
    provenance: "C535"

  differentiation_principle: |
    Grammar is universal at CLASS level (same 49 classes everywhere).
    Differentiation occurs at TOKEN level within classes.
    Section differentiation occurs at FREQUENCY level within shared
    vocabulary — same PP types, different usage rates (C1134, 74% of
    section JS divergence). This enables material-appropriate execution
    via variant selection and frequency modulation, not via different
    procedures. (C506.b, C537, C1134)

ht_un_integration:

  population_identity:
    statement: "HT = UN (identical by definition)"
    ht_types: 4421
    ht_occurrences: 7042
    hapax_rate: "74.1%"
    provenance: "C740"

  c475_compliance:
    statement: "HT tokens obey C475 MIDDLE incompatibility when co-occurring with classified tokens"
    violation_rate: "0.44%"
    provenance: "C742"

  novel_combinations:
    statement: "HT uses MIDDLE combinations that never occur in classified adjacencies"
    novel_pair_rate: "11.19%"  # Pairs where both MIDDLEs in classified but pair not seen
    ht_exclusive_middles: "90.7%"  # MIDDLEs that appear only in HT
    classified_overlap: "14.4%"  # HT-HT pairs also seen in classified
    provenance: "C812"

  lane_architecture:
    statement: "HT tokens are lane-segregated (CHSH-dominant) but lane-indifferent in transitions"
    chsh_fraction: "dominant"
    lane_transitions: "indifferent (no lane-tracking)"
    provenance: "C743, C744"

  line1_enrichment:
    statement: "Line-1 has 50.2% HT vs 29.8% on lines 2+ (Tier 0 frozen fact)"
    delta: "+20.3 percentage points"
    tier: 0
    provenance: "C747"

  line1_composite_header:
    statement: "Line-1 HT is a two-part composite header"
    structure:
      pp_component:
        share: "68.3%"
        function: "A-context declaration"
        prediction_accuracy: "13.9% vs 0.88% baseline"
      b_exclusive_component:
        share: "31.7%"
        function: "Folio identification"
        folio_unique_rate: "94.1%"
    independence: "PP fraction does NOT correlate with body PP size (rho=0.002)"
    provenance: "C794, C795"

  folio_distribution:
    statement: "HT density varies by folio in compensatory pattern"
    provenance: "C746"

  operational_redundancy:
    # REVISED v3.0: Was "non_operational" — revised per C935
    statement: |
      HT tokens are OPERATIONALLY REDUNDANT, not non-operational.
      They contain operational content (compound MIDDLEs decompose to core atoms)
      but this content is redundant with body simple MIDDLEs (71.6% hit rate
      vs 59.2% random, 1.21x lift). Removing HT doesn't change outcomes
      because the body already encodes the same operations in simple form.
    statistical_evidence_unchanged:
      terminal_independence: "p=0.92 (C404)"
      causal_decoupling: "V=0.10 (C405)"
    revision_note: |
      C404 evidence is UNCHANGED. What changed is the EXPLANATION:
      Old: "HT has no operational content" → New: "HT has redundant operational content"
      The compound specification model (C935) is a simpler explanation than
      attention pacing (C209) or calligraphy practice, both of which are WEAKENED.
    compound_specification:
      ht_compound_rate: "45.8% (vs 31.5% grammar)"
      avg_middle_length: "2.64 (vs 2.04 grammar)"
      decomposition_rate: "100% of compounds decompose to core atoms"
      body_prediction_hit_rate: "71.6%"
      random_baseline: "59.2%"
      lift: "1.21x"
    provenance: "C404, C405, C935"

  line1_ht_folio_specificity:
    statement: "Line-1 HT tokens are highly folio-specific"
    folio_singleton_rate: "85.9%"  # appear in only ONE folio
    folio_unique_and_line1_only: "1,229 tokens (67%)"
    provenance: "C870"

  ht_role_cooccurrence:
    statement: "HT tokens show systematic role cooccurrence patterns"
    chsh_bias: "HT preferentially co-occurs with CHSH lane"
    provenance: "C871"

  ht_discrimination_vocabulary:
    statement: "HT tokens form a discrimination vocabulary for folio/procedure identification"
    function: "Identify WHICH procedure AND specify WHAT operations (dual purpose, C935)"
    semantic_ceiling_compliant: true
    vocabulary_size: "4,421 types"
    line1_concentration: "50.2% of Line-1 are HT"
    provenance: "C872, C935"

  dark_pipeline_integration:
    statement: "300 dark-pipeline PP MIDDLEs produce exclusively HT/UN tokens in B"
    ht_tokens: 1696
    grammar_tokens: 0
    ht_substrate_rate: "100%"
    construction_grammar:
      statement: "Dark-pipeline HT tokens use a distinct construction grammar from grammar-classified HT"
      gs_ext_middle_length: 3.39   # Grammar/Section tokens
      ht_middle_length: 1.81       # HT tokens
      prefix_rate_gs_ext: "83.9%"
      prefix_rate_ht: "58.1%"
      provenance: "C1138"
    atom_substrate:
      statement: "Dark-pipeline compounds are built from bridge atoms"
      bridge_atom_types: "86% (43/50 unique atoms)"
      bridge_atom_occurrences: "91.6%"
      compound_coverage: "96.5% (193/200 compounds contain ≥1 bridge atom)"
      construction_hierarchy: "bridge atoms → compositional assembly (1-3 atoms) → dark-pipeline compounds → HT/UN identification tokens"
      provenance: "C1141"
    modified_ordering:
      statement: "Dark pipeline follows SAME ordering grammar as C1065 (revised from 'modified')"
      c1065_agreement: "100% (4/4 testable asymmetric pairs at strict threshold; C1142's 50% was low-count noise)"
      dark_asymmetric_pairs: 4  # ek->ke, ke->eo, eo->ot, ok->ke (all match C1065)
      internal_consistency: "100% transitive (0 violations)"
      dark_exclusive_atoms: 25  # Atoms not in grammar compounds
      atom_equivalence: "Dark-exclusive and shared atoms have equivalent section profiles (MW p=0.107, C1143) and equivalent positional slots (chi-sq p=0.421, C1145)"
      provenance: "C1177 (revises C1142, C1144)"
    line_position:
      statement: "Dark-pipeline tokens preferentially occupy line-interior positions"
      dark_middle_rate: "73.2%"
      general_ht_middle_rate: "67.7%"
      grammar_middle_rate: "83.5%"
      chi_sq_dark_vs_ht: "23.2 (p < 0.0001)"
      implication: "Interior-enriched relative to HT but less interior than grammar; identification vocabulary fills line interior"
      provenance: "C1147"
    hyper_modulation:
      statement: "Dark-pipeline MIDDLEs are 3.9x more section-differentiated than PP baseline"
      dark_mean_js: 0.483
      pp_baseline_js: 0.124
      ratio: "3.9x"
      mechanism: "ATOM_SELECTION_DOMINATED — multiplicative atom model R²=0.781 (C1176)"
      implication: "Atoms carry section signal; compounds inherit multiplicatively. No combination-emergent section effects."
      provenance: "C1148, C1176"
    combinatorics:
      # Phase 419: DARK_PIPELINE_COMBINATORICS (C1175-C1178)
      pair_space_occupancy: "7.9% (71/903 possible atom pairs)"
      c475_gate: "100% recall, 13.4% precision — necessary but loose"
      curation_parallel: "Parallels C1028 (0.9% PREFIX×MIDDLE×SUFFIX occupancy)"
      phantom_middles: "15 B-absent ch/sh-initial MIDDLEs — morphologically isolated, dead naming pattern (C1178)"
      provenance: "C1175, C1176, C1177, C1178"
    provenance: "C1137, C1138, C1141, C1142, C1143, C1144, C1145, C1146, C1147, C1148, C1175, C1176, C1177, C1178"

robustness:

  noise_robustness:
    provenance: "C328"

  ablation_robustness:
    provenance: "C329"

  cross_validation:
    provenance: "C330"

  minimality:
    provenance: "C331"

# OPERATIONAL LAYER [TIER 3]
#
# This section contains behaviorally-derived operational glosses
# and interpretations. These are CONDITIONAL on Brunschwig alignment
# and do NOT carry Tier 0-2 structural authority. They are included
# because operational grounding is essential for reading programs
# and the structural layer alone does not provide it.
#
# Structural basis: C506.b (behavioral heterogeneity), C908-C910
# (MIDDLE-kernel-REGIME correlations), C911 (PREFIX-MIDDLE selectivity).
# These are Tier 2. The GLOSSES derived from them are Tier 3.
operational_layer:
  tier: 3
  status: "WORKING — glosses derived from behavioral correlations + Brunschwig alignment"
  caveat: |
    Everything in this section is conditional on the Brunschwig structural
    alignment (fits F-BRU-001 through F-BRU-016). If that alignment is
    invalidated, glosses must be re-derived from internal correlations only.

  middle_glosses:
    description: |
      75 core MIDDLEs have behavioral glosses derived from kernel profile
      correlations (which kernel characters they co-occur with), REGIME
      distribution (which folios they concentrate in), section distribution,
      and Brunschwig operation alignment. Full dictionary: data/middle_dictionary.json
    coverage: "75/75 core MIDDLEs glossed (100%)"
    dictionary_structure: "mid_dict['middles'][MIDDLE_NAME]['gloss']"
    top_middles_by_frequency:
      k: {gloss: "heat", freq: 2081, kernel: "K"}
      edy: {gloss: "batch", freq: 1763}
      e: {gloss: "cool", freq: 845, kernel: "E"}
      aiin: {gloss: "check", freq: 831}
      ey: {gloss: "set", freq: 769}
      ol: {gloss: "continue", freq: 759}
      ar: {gloss: "close", freq: 670}
      eey: {gloss: "deep cool", freq: 615, kernel: "E"}
      dy: {gloss: "close", freq: 594}
      t: {gloss: "transfer", freq: 574}
      ke: {gloss: "sustained heat", freq: 421, kernel: "K"}
      ch: {gloss: "check", freq: 351}
      d: {gloss: "checkpoint", freq: 312}
      h: {gloss: "monitor", freq: 48, kernel: "H"}
    provenance: "MIDDLE_SEMANTIC_MAPPING phase, data/middle_dictionary.json v2.0"

  suffix_flow_control:
    description: |
      Suffixes encode flow control: what happens AFTER the operation completes.
      The same characters used as MIDDLEs appear in suffix position with
      control-flow semantics. 35 unique suffixes, covering 50.5% of B tokens.
    top_suffixes:
      edy: {gloss: "batch", freq: 2147, pct: "9.3%"}
      dy: {gloss: "close", freq: 1081, pct: "4.7%"}
      aiin: {gloss: "check", freq: 952, pct: "4.1%"}
      hy: {gloss: "hazard flag", freq: 910, pct: "3.9%"}
      ar: {gloss: "close", freq: 834, pct: "3.6%"}
      ain: {gloss: "intake", freq: 742, pct: "3.2%"}
      y: {gloss: "end", freq: 678, pct: "2.9%"}
      al: {gloss: "collect", freq: 661, pct: "2.9%"}
      eey: {gloss: "deep cool", freq: 622, pct: "2.7%"}
      ey: {gloss: "set", freq: 618, pct: "2.7%"}
      s: {gloss: "break", freq: 429, pct: "1.9%"}
      or: {gloss: "portion", freq: 418, pct: "1.8%"}
    provenance: "C382, C588, MIDDLE_SEMANTIC_MAPPING"

  token_reading_pattern:
    description: |
      A token reads as: PREFIX:MIDDLE.SUFFIX
      = "on [channel], do [operation], then [flow control]"
    examples:
      - token: "qokedy"
        parse: "qo:k.edy"
        reading: "on energy channel: heat, then batch"
      - token: "chedy"
        parse: "ch:e.dy"
        reading: "on stability channel: cool, then close"
      - token: "sheckhy"
        parse: "sh:eck.hy"
        reading: "on verify channel: hard precision, hazard flag"
      - token: "daiin"
        parse: "da:iin"
        reading: "infrastructure: iterate (control loop marker)"
      - token: "okeey"
        parse: "ok:eey"
        reading: "VESSEL: deep cool (C936 — ok selects vessel, eey = deep cool action)"
      - token: "okaiin"
        parse: "ok:aiin"
        reading: "VESSEL: check (C936 — ok selects vessel, aiin = check action)"
      - token: "okam"
        parse: "ok:am"
        reading: "VESSEL: seal permanently (C936 — ok selects vessel, am = finalize)"

  program_reading:
    description: |
      A B paragraph reads as a mini-program:
      Line 1 (HEADER):  Compound specification + folio identification
      Lines 2-N/3 (SPEC): Prep operations, parameter setting, unique vocabulary
      Lines N/3-2N/3 (BODY): Mixed heat/cool/check cycles
      Lines 2N/3-N (LOOP): Generic control loop, universal vocabulary, iterate suffixes
    line_reading: |
      Each line reads left-to-right with FL state tracking:
        da:FL:EARLY  sh:batch  qo:heat.deep_cool  ch:precision.close  ol:FL:END
        [init state]  [verify:  [energy: heat,     [stability: precision, [continue:
                       batch]    then deep cool]     then close]           end state]

negative_guarantees:
  - guarantee: "No Currier A references"
    reason: "BCSC is A-agnostic"

  - guarantee: "No AZC references"
    reason: "BCSC is AZC-agnostic"

  - guarantee: "No Human Track as separate non-operational layer"
    reason: "HT is operationally redundant (C935), not a separate layer; compound specification model replaces attention/practice interpretations"

  - guarantee: "No referential token meanings (substance identification, material names)"
    reason: "Semantic ceiling (C120, C171): no natural-language translation or material identification recoverable from internal analysis. Behavioral glosses (Tier 3) describe operational PROFILES, not referential MEANINGS."

  - guarantee: "No family structure"
    reason: "Families are emergent, not grammar partitions (C126, C144)"

disallowed:
  - interpretation: "B grammar varies by Currier A source"
    reason: "Grammar is universal (C124)"
    provenance: "C124"

  - interpretation: "B grammar varies by AZC context"
    reason: "Grammar unchanged by legality (AZC-B-ACT)"
    provenance: "C121, C124"

  - interpretation: "Families are different grammars"
    reason: "Cross-family transplant = zero degradation"
    provenance: "C141"

  - interpretation: "Grammar encodes semantic content"
    reason: "PURE_OPERATIONAL verdict"
    provenance: "C120"

  - interpretation: "Grammar is directional (narrative)"
    reason: "Time-reversal symmetric"
    provenance: "C391"

  - interpretation: "Grammar is a decision tree or state machine"
    reason: "Closed-loop control only"
    provenance: "C171"

  - interpretation: "AX classes represent distinct behavioral modes"
    reason: "Classes collapse to ≤2 effective groups; position is sole differentiator"
    provenance: "C572"

  - interpretation: "C559 FQ membership {9,20,21,23} is correct"
    reason: "Classes 20,21 are AX per C563; correct FQ is {9,13,14,23} per ICC"
    provenance: "C583, C592"

  - interpretation: "HT tokens are non-operational (contain no operational content)"
    reason: "C935 shows HT compounds decompose to core atoms with 71.6% body prediction. They are operationally REDUNDANT, not empty."
    provenance: "C935, C404 (revised)"

  - interpretation: "PREFIX is a passive label with no behavioral effect"
    reason: "PREFIX transforms MIDDLE behavior (JSD=0.425, 97.5% of between-MIDDLE divergence)"
    provenance: "C661, C911"

  - interpretation: "ok encodes a verb (seal/lock/close/cover) with MIDDLE as modifier"
    reason: "ok is a domain selector (VESSEL), not a verb. MIDDLE provides the action. Verb-based glosses produce word salad at line level. 15 hypotheses tested; only domain-selector produces coherent procedures. 378 same-MIDDLE pairs confirm PREFIX differentiates target domain."
    provenance: "C936 (revised)"

  - interpretation: "FL_SAFE is an absorbing or long-duration collection state"
    reason: "FL_SAFE has self-transition of only 0.023, exits to AXM at 0.698, and has expected return time of 117.7 steps — a rare fleeting terminal excursion, not an absorbing state"
    provenance: "C1015"


```

---

# A->AZC Activation Contract

```yaml

meta:
  name: "AZC Positional Classification Contract"
  acronym: "AZC-ACT"
  version: "1.2"
  date: "2026-02-06"
  status: "ACTIVE"
  layer_type: "mapping contract"
  derived_from: "Tier-2 constraints only"
  audit_note: "v1.2: Pipeline framing removed per AZC_POSITION_VOCABULARY (2026-01-31) finding that AZC is static lookup table with no independent positional effect."
  governance: |
    AZC-ACT is NOT authoritative. Constraints are authoritative.
    AZC-ACT describes HOW vocabulary is positionally classified in AZC.
    Do not edit without updating source constraints first.

scope:
  function: "How vocabulary shared between A and AZC is positionally classified"
  direction: "A -> AZC (one-way transformation, not reverse)"
  vocabulary_authority: false  # AZC does not "own" vocabulary
  generativity: false  # No derivation rules
  b_semantics: false  # Execution is downstream, not here

# Explicit ownership declaration (prevents misreading)
ownership:
  azc_owns:
    - nothing
  azc_encodes:
    - positional_classification
    - vocabulary_grouping
    - compatibility_signature

guarantees:
  - id: "VOCABULARY_ACTIVATED"
    statement: "AZC constraint activation is vocabulary-driven"
    provenance: "C441"

  - id: "COMPATIBILITY_GROUPING"
    statement: "AZC folios group vocabulary by compatibility signature"
    provenance: "C442"

  - id: "LEGALITY_CORRELATION"
    statement: "AZC positional vocabulary profiles correlate reliably with B behavior (28x escape rate difference)"
    provenance: "C468"

  - id: "NO_CONTENT_MUTATION"
    statement: "AZC does not mutate A entry contents"
    provenance: "C444"

  - id: "FAMILY_AGNOSTIC_MECHANISM"
    statement: "AZC legality mechanism is family-agnostic"
    provenance: "C430-C436, C441-C443"

invariants:
  monotonicity:
    statement: "Survivor options never increase from earlier to later positions"
    provenance: "C443, C444"

  position_independence:
    statement: "The SAME A-type can appear in any position; position determines legality, not content"
    provenance: "C444"

  vocabulary_mediation:
    statement: "All A->B relationships are vocabulary-mediated, not addressable"
    provenance: "C384, C441"

  scaffold_independence:
    statement: "Legality zones are independent of scaffold presentation"
    provenance: "C430-C436"

inputs:
  accepted:
    type: "registry_entry"
    from_casc: "record_types.registry_entry"
    minimum_tokens: 2
    provenance: "C482, C484"

  excluded:
    type: "control_operator"
    reason: "Control operators are meta-structural, not registry content"
    provenance: "C484"


positional_zones:
  provenance: "C306, C313"

  zones:
    C:
      function: "Interior placement, rotation-tolerant"
      escape_permission: "moderate"
      provenance: "C306, C317"


    R_series:
      members: ["R1", "R2", "R3"]
      ordering: "strictly forward (R1->R2->R3 only)"
      backward_transitions: "FORBIDDEN"
      skip_transitions: "FORBIDDEN"
      function: "Ordered interior stages, progressive escape restriction"
      escape_gradient: "decreasing (high to zero)"
      restricted_to_ordered_subscript_family: true
      observed_in: "Zodiac family (C432)"
      provenance: "C432, C434, C443"

    S_series:
      members: ["S0", "S1", "S2"]
      function: "Boundary markers, no intervention permitted"
      escape_permission: "zero"
      ordering: "S2 appears earlier than S1"
      restricted_to_ordered_subscript_family: true
      observed_in: "Zodiac family (C432)"
      provenance: "C320, C432, C435, C443"

  zone_semantics: |
    Diagram positions only: C, R-series, S-series.
    Interior diagram positions (R-series, C) have moderate escape permission.
    Boundary diagram positions (S-series) forbid intervention.
    P (Paragraph) is NOT a diagram position - it is Currier A text on AZC folios.


transformations:

  compatibility_grouping:
    observation: "Specialized vocabulary appears at distinct positions; combinations that don't occur reflect fixed positional encoding"
    provenance: "C442, C475"

  escape_permission_changes:
    effect: "Same A-type has different intervention permission by position"
    provenance: "C443, C444"

  categorical_resolution:
    effect: "Operational conditions represented categorically"
    provenance: "C469"

  vocabulary_legality:
    expansion: false  # AZC does NOT expand vocabulary beyond A specification
    observation: "Only tokens with matching PREFIX, MIDDLE, and SUFFIX appear in B execution"
    morphological_correspondence:  # C502.a - full morphological correspondence
      middle_only:
        legal_tokens: "257 (5.3%)"
        excluded: "94.7%"
      middle_plus_prefix:
        legal_tokens: "92 (1.9%)"
        additional_reduction: "64%"
      middle_plus_suffix:
        legal_tokens: "130 (2.7%)"
        additional_reduction: "50%"
      full_morphology:
        legal_tokens: "38 (0.8%)"
        additional_reduction: "85% beyond MIDDLE"
    legacy_claim: "Original ~80%/~96 of 480 was MIDDLE-only against token types"
    provenance: "C481, C502, C502.a"

  content_invariants:
    - "No movement of tokens"
    - "No selection"
    - "No branching"
    - "No instruction creation"
    - "No mutation of entry contents"

persistence:
  a_survivor_independence:
    statement: "A-vocabulary tokens persist independently of AZC legality windows"
    provenance: "C343"

  vanishing_semantics:
    statement: "Position exclusivity, not active filtering"
    provenance: "C444"

  restriction_inheritance:
    statement: "MIDDLE restrictions transfer to B"
    provenance: "C470"

morphological_binding:

  prefix_affinity:
    provenance: "C471"

  middle_specificity:
    provenance: "C472"

  constraint_bundle:
    statement: "Each A entry functions as a constraint bundle"
    effect: "Determines which AZC legality envelopes apply"
    provenance: "C473"

negative_guarantees:
  - guarantee: "No token movement"
    reason: "AZC encodes position, does not route"

  - guarantee: "No selection"
    reason: "AZC records vocabulary position; it does not select or route vocabulary"

  - guarantee: "No branching"
    reason: "No conditional paths in AZC structure"

  - guarantee: "No instruction creation"
    reason: "AZC encodes position, B executes"

  - guarantee: "No semantic content"
    reason: "Positions are legality regimes, not meanings"

  - guarantee: "No dynamic AZC decision-making"
    reason: "F-AZC-015 closed this (Case B confirmed)"


disallowed:
  - interpretation: "AZC owns vocabulary"
    reason: "Vocabulary is A-derived, AZC constrains positions"
    provenance: "C441, CASC"

  - interpretation: "AZC selects procedures"
    reason: "AZC defines legality, B executes, operator selects"
    provenance: "C473"

  - interpretation: "Position encodes meaning"
    reason: "Position encodes legality constraints, not semantics"
    provenance: "C313"

  - interpretation: "AZC is addressable lookup from A entries to B programs"
    reason: "No entry-level A-B coupling exists (C384); AZC classifies vocabulary, not entries"
    provenance: "C384, C441"

  - interpretation: "AZC decides dynamically"
    reason: "Ambient legality field, not decision engine"
    provenance: "F-AZC-015"

  - interpretation: "AZC expands vocabulary beyond A specification"
    reason: "AZC restricts, does not expand. Only A-record MIDDLEs are legal for B execution."
    provenance: "C481, C502"


```

---

# AZC->B Propagation Contract

```yaml

meta:
  name: "AZC-B Vocabulary Correlation Contract"
  acronym: "AZC-B-ACT"
  version: "1.2"
  date: "2026-02-06"
  status: "ACTIVE"
  layer_type: "correlation contract"
  derived_from: "Tier-2 constraints only"
  audit_note: "v1.2: Pipeline framing removed per AZC_POSITION_VOCABULARY (2026-01-31) finding that AZC is static lookup table with no independent positional effect."
  governance: |
    AZC-B-ACT is NOT authoritative. Constraints are authoritative.
    AZC-B-ACT describes HOW vocabulary classified in AZC co-varies with B behavior.
    Do not edit without updating source constraints first.

scope:
  function: "How AZC legality states constrain Currier B execution"
  direction: "AZC -> B (vocabulary-mediated correlation, not reverse)"
  b_grammar_authority: false  # Does not modify B grammar
  a_visibility: false  # B does not see A entries
  azc_visibility: false  # B does not see AZC internal structure

# Explicit ownership declaration (prevents misreading)
ownership:
  azc_b_act_owns:
    - nothing
  azc_b_act_describes:
    - legality_correlation
    - intervention_permission_envelope
    - vocabulary_restriction_inheritance

# What B receives (effects, not signals)
b_reception:
  receives:
    - description: "Grammar paths silently constrained by legality"
    - description: "Intervention permission envelope"
    - description: "Vocabulary restriction inheritance"
  does_not_receive:
    - "Currier A entry identity"
    - "AZC internal structure"
    - "Why tokens are legal/illegal"
    - "Compatibility graph mechanics"
    - "Positional semantics (C, P, R, S zones)"

guarantees:
  - id: "LEGALITY_CORRELATION"
    statement: "Vocabulary classified at high-escape AZC positions produces high escape rates in B (28x difference); both determined by vocabulary properties"
    provenance: "C468"

  - id: "RESTRICTION_PRESERVATION"
    statement: "MIDDLE restrictions transfer intact to B"
    provenance: "C470"

  - id: "GRAMMAR_INDEPENDENCE"
    statement: "B grammar is unchanged by AZC legality"
    provenance: "C121, C124"

  - id: "BLIND_EXECUTION"
    statement: "B executes without knowledge of upstream mechanics"
    provenance: "C384, C468"

  - id: "CATEGORICAL_RESOLUTION"
    statement: "Resolution via vocabulary availability, not parameters"
    provenance: "C469"

invariants:
  vocabulary_mediated_correlation:
    statement: "AZC positional classification and B intervention dynamics co-vary via shared vocabulary properties"
    provenance: "C468"

  restriction_correlation:
    statement: "Vocabulary restrictions correlate across AZC and B contexts"
    provenance: "C470"

  grammar_stability:
    statement: "B grammar rules apply universally regardless of AZC source"
    provenance: "C124"

  non_parametric:
    statement: "No numeric values are encoded; all distinctions are categorical"
    provenance: "C469"

  no_token_transmission:
    statement: "No tokens are transmitted from Currier A to Currier B"
    provenance: "C384, C281, C285, C343"

inputs:
  from_azc:
    type: "legality_effect"
    components:
      - escape_permission: "Position-indexed intervention permission envelope"
      - folio_restriction: "MIDDLE-level compatibility constraints"
    provenance: "C443, C468, C470"

  not_exported:
    - "AZC position labels (C, P, R, S)"
    - "Folio identity"
    - "Family membership (Zodiac vs A/C)"
    - "Compatibility graph structure"
    - "Escape rate thresholds or numeric values"

correlation:

  escape_permission_transfer:
    direction: "Higher AZC escape permission yields higher B escape incidence"
    categorical: true
    parametric: false
    provenance: "C468"

  vocabulary_restriction_transfer:
    direction: "Restricted MIDDLEs remain restricted in B"
    categorical: true
    parametric: false
    provenance: "C470"

  categorical_resolution:
    effect: "Fine distinctions encoded in which tokens are legal"
    frequency_dimension: "Section differentiation also manifests as frequency variation of shared PP vocabulary (74% of section JS divergence from PP frequency modulation, C1134)"
    provenance: "C469, C1134"

  vanishing_semantics:
    statement: "Illegality manifests as absence, not marking"
    provenance: "C444, C468"

  vocabulary_scope:
    statement: "B vocabulary is restricted to A-record MIDDLEs only"
    expansion: false  # AZC does NOT expand vocabulary beyond A specification
    filtering_magnitude: "~80% of B vocabulary filtered per A context"
    effect: "Different A records make different B folios viable"
    dual_channel: |
      A-derived MIDDLEs feed B through two distinct channels:
      - Grammar channel: 89 PP MIDDLEs (85 bridge + 4 non-bridge matched) enter
        B's 49-class grammar as classified vocabulary
      - Identification channel: 300 dark-pipeline PP MIDDLEs produce exclusively
        HT/UN tokens (1,696 tokens, 0 grammar tokens), built from bridge atoms
      Per C1140 four-way partition: 85 bridge + 4 matched + 300 dark pipeline + 15 phantom = 404 PP total.
      Channels are anti-correlated at folio level (r=-0.865, C1146): folios
      invest more in grammar execution OR identification, not both equally.
    identification_channel_modulation: "Dark-pipeline MIDDLEs are 3.9x more section-differentiated than PP baseline (JS=0.483 vs 0.124); primary vehicle for section-level vocabulary modulation (C1148)"
    provenance: "C481, C502, C1137, C1140, C1146, C1148"

b_reception_architecture:

  escape_routes:
    primary: "qo-prefix tokens"
    role_stratification:
      primary: "ENERGY_OPERATOR"
      secondary: "CORE_CONTROL"
    provenance: "C397, C398"

  stability_anchor:
    provenance: "C105"

  design_constraints:
    hazard_exposure: "CLAMPED"
    intervention_operations: "FREE"
    principle: "Constrain dangerous interactions; let intervention vary"
    provenance: "C458"

b_isolation:

  blocked:
    - item: "A entry identity"
      reason: "C384 - no entry-level coupling"
    - item: "AZC position structure"
      reason: "B receives effects, not positions"
    - item: "AZC folio semantics"
      reason: "Folio identity does not transfer"
    - item: "Compatibility graph"
      reason: "B sees legal/illegal as absence/presence, not why"
    - item: "MIDDLE incompatibility details"
      reason: "Filtering happens upstream"
    - item: "Numeric thresholds or ratios"
      reason: "C469 - categorical resolution only"

negative_guarantees:
  - guarantee: "No A entry visibility in B"
    reason: "C384 - vocabulary-mediated only"

  - guarantee: "No AZC structure visibility in B"
    reason: "B observes effects (vocabulary availability), not AZC structure"

  - guarantee: "No B grammar modification by AZC"
    reason: "C121, C124 - grammar is universal"

  - guarantee: "No reverse inference from B to AZC"
    reason: "Correlation is vocabulary-mediated, not reverse-inferrable"

  - guarantee: "No parametric encoding"
    reason: "C469 - categorical resolution only"

  - guarantee: "No numeric values transmitted"
    reason: "All distinctions are categorical"

disallowed:
  - interpretation: "B sees A entries"
    reason: "Vocabulary-mediated only (C384)"
    provenance: "C384"

  - interpretation: "B can infer AZC position"
    reason: "B sees vocabulary availability, not positional structure"
    provenance: "C468"

  - interpretation: "AZC modifies B grammar"
    reason: "Grammar is universal and unchanged"
    provenance: "C121, C124"

  - interpretation: "Recovery budget is a quantitative resource"
    reason: "Categorical permission only, no parametric values"
    provenance: "C469"

  - interpretation: "Legality is a state variable in B"
    reason: "Ambient constraint (absence/presence), not signal"
    provenance: "C468, C469"

  - interpretation: "Numeric thresholds are contractual"
    reason: "Thresholds are empirical observations, not rules"
    provenance: "C469"

  - interpretation: "AZC expands B vocabulary beyond A specification"
    reason: "AZC restricts, does not expand. Only A-record MIDDLEs are legal for B."
    provenance: "C481, C502"


```

---

# Human Track Layer Contract

```yaml

meta:
  name: "Human Track Structural Contract"
  acronym: "HTSC"
  version: "1.1"
  date: "2026-02-15"
  status: "ACTIVE"
  layer_type: "cross-system layer contract"
  derived_from: "Tier 0-2 constraints (structural); Tier 3 two-axis model clearly marked"
  governance: |
    HTSC is NOT authoritative. Constraints are authoritative.
    HTSC describes the HT layer from HT's own perspective, across all systems.
    Do not edit without updating source constraints first.
    Sections marked [TIER 3] contain interpretive models that are
    plausible but do not carry Tier 0-2 authority.

scope:
  system: "Manuscript-wide (A, B, AZC)"
  coverage:
    b_types: 4421
    b_occurrences: 7042
    b_fraction: "30.5%"
    azc_tokens: "~3,299"
    a_present: true
  function: "What HT is, how it manifests across systems, what it cannot do"
  b_grammar_independent: true  # HT is defined by EXCLUSION from 479-type B grammar
  operationally_redundant: true  # C935 revision: not empty, but redundant
  owns_nothing: true  # HT does not own any structural object

# Explicit ownership declaration
ownership:
  htsc_describes:
    - population_definition
    - cross_system_manifestation
    - morphological_architecture
    - positional_properties
    - threading_architecture
    - interaction_architecture
    - operational_status
    - line1_header_structure
    - paragraph_header_structure
  htsc_does_not_describe:
    - b_grammar: "-> BCSC"
    - a_registry: "-> CASC"
    - azc_classification: "-> AZC-ACT"
    - interpretation_beyond_tier2: "-> SPECULATIVE/"
  ownership_boundaries: |
    BCSC ht_un_integration remains in BCSC as B-perspective summary.
    For comprehensive HT properties, see HTSC.
    Line-1/paragraph header: HTSC owns HT rates and morphology;
    BCSC owns program-structural implications.
    C935: Referenced by HTSC as evidence, not owned. Primary home is BCSC.
    AZC HT constraints (C439, C457): Referenced, not owned. Primary home is AZC-ACT.
    Each constraint in provenance is tagged OWNED or REFERENCED.

guarantees:

  - id: "POPULATION_IDENTITY"
    statement: "HT = UN (identical by definition); 4,421 types, 7,042 occurrences in B (30.5%)"
    provenance: "C740"

  - id: "UNIFIED_VOCABULARY"
    statement: "Same HT prefix inventory across A, B, and AZC systems (Jaccard >= 0.947)"
    provenance: "C452"

  - id: "SINGLE_LAYER"
    statement: "HT forms one coherent layer, not multiple overlapping systems"
    provenance: "C168"

  - id: "OPERATIONAL_REDUNDANCY"
    statement: |
      HT tokens are OPERATIONALLY REDUNDANT, not non-operational.
      They contain operational content (compound MIDDLEs decompose to core atoms)
      but this content is redundant with body simple MIDDLEs (71.6% hit rate
      vs 59.2% random, 1.21x lift). Removing HT doesn't change outcomes
      because the body already encodes the same operations in simple form.
    revision_note: |
      C404 evidence is UNCHANGED. What changed is the EXPLANATION:
      Old: "HT has no operational content" -> New: "HT has redundant operational content"
      The compound specification model (C935) is a simpler explanation than
      attention pacing (C209) or calligraphy practice, both of which are WEAKENED.
    provenance: "C404, C405, C935"

  - id: "CAUSAL_DECOUPLING"
    statement: "HT presence does not alter subsequent grammar probabilities (V=0.10, negligible)"
    provenance: "C405"

  - id: "NON_PREDICTIVE"
    statement: "HT does not improve prediction of subsequent content; MAE worsens by 0.003-0.005"
    provenance: "C415"

  - id: "DIRECTIONAL_DOWNSTREAM"
    statement: "Coupling is unidirectional: System->HT (V=0.324), HT->System (V=0.202), ratio 1.6x"
    provenance: "C416"

  - id: "HAZARD_AVOIDANCE"
    statement: |
      0/35 HT tokens at forbidden transition seams; average distance 4.84 (vs 2.5 expected).
      Mechanism: vocabulary-level exclusion (C1078). Only 5/7042 HT tokens participate in
      forbidden vocabulary at all. Avoidance is lexical, not positional — HT words simply
      do not appear in C109 forbidden pairs. Boundary position does not modulate distance.
    provenance: "C166, C169, C1078"

  - id: "LINE1_ENRICHMENT"
    tier: 0
    statement: "Line-1 has 50.2% HT vs 29.8% on lines 2+ (+20.3 pp)"
    provenance: "C747"

  - id: "LINE1_STEP_FUNCTION"
    tier: 0
    statement: "Enrichment is confined to position 1 only: pos1=50.2%, pos2=31.7%, pos3+=27-33%"
    provenance: "C748"

  - id: "OPENING_ONLY"
    tier: 0
    statement: "No closing enrichment: last line 30.8% = interior 29.8%"
    provenance: "C750"

  - id: "LINE1_COMPOSITE_HEADER"
    statement: |
      Line-1 HT is a two-part composite header:
      - PP component (68.3%): A-context declaration, 13.9% prediction accuracy vs 0.88% baseline (15.8x lift)
      - B-exclusive component (31.7%): Folio identification, 94.1% folio-unique
      PP fraction does NOT correlate with body PP size (rho=0.002).
    provenance: "C794, C795, C799"

  - id: "COMPOSITIONAL_GENERATIVITY"
    statement: "HT follows Zipf distribution (exponent 0.892, R-sq=0.92) with 67.5% hapax rate"
    provenance: "C406"

  - id: "COMPOUND_SPECIFICATION"
    statement: |
      100% of HT compound MIDDLEs decompose to core atoms.
      Compound atoms predict body MIDDLEs at 71.6% hit rate (1.21x lift vs 59.2% random).
      HT compound rate: 45.8% (vs 31.5% grammar).
      Mean HT MIDDLE length: 2.64 (vs 2.04 grammar).
      Dark-pipeline HT compounds are built from bridge atoms (86% of atom types,
      96.5% compound coverage). The bridge backbone is both the dynamical backbone
      of B's grammar AND the morphological substrate of identification vocabulary.
    provenance: "C935, C1137, C1141"

  - id: "QUIRE_ORGANIZED"
    statement: "HT shows codicological clustering at the quire level"
    provenance: "C450"

  - id: "ANTICIPATORY_COMPENSATION"
    statement: "HT anticipates B stress at quire level (r=0.343, p=0.0015)"
    provenance: "C459"

  - id: "TAIL_CORRELATION"
    statement: "HT density tracks MIDDLE rarity (r=0.504, p=0.0045); tail_pressure explains 68% of R-sq=0.279"
    provenance: "C477, C461"

invariants:

  - id: "SYSTEM_STRATIFICATION"
    statement: "HT density (prefix-based, C451 methodology): A (0.170) > AZC (0.162) > B (0.149)"
    note: |
      C451 used 19-family prefix detection (pre-C740). Under full C740 UN definition,
      ordering becomes AZC > A > B because AZC labels are heavily HT.
      The prefix-based ordering is stable and reproduced exactly by HTSC verification.
    provenance: "C451"

  - id: "SECTION_EXCLUSIVITY"
    statement: "80.7% of HT types appear in only one section"
    provenance: "C167"

  - id: "PREFIX_DISJOINTNESS"
    statement: "Zero overlap between HT prefixes (yk-, op-, yt-, sa-, etc.) and A/B prefixes (ch-, qo-, sh-, etc.)"
    provenance: "C347"

  - id: "MORPHOLOGICAL_MODULARITY"
    statement: "HT_PREFIX + MIDDLE + SUFFIX; components are independent and additive (no synergy, p=1.0)"
    provenance: "C417"

  - id: "ADJACENCY_CLUSTERING"
    statement: "1.69x enrichment of HT tokens in adjacent positions"
    provenance: "C453"

  - id: "LANE_SEGREGATION_INDIFFERENCE"
    statement: |
      HT is lane-SEGREGATED (composition: chi2=278.71, p=4e-60; OTHER +9.5pp, QO -7.7pp)
      but lane-INDIFFERENT in transitions (same-lane rate 37.7% = expected 37.9%, lift=0.994x)
    provenance: "C743, C744"

  - id: "C475_COMPLIANCE"
    statement: "HT obeys MIDDLE incompatibility when adjacent to classified tokens (violation rate 0.69%)"
    provenance: "C742"

  - id: "FOLIO_COMPENSATORY"
    statement: "HT density anti-correlated with folio grammar coverage (r=-0.376)"
    provenance: "C746"

  - id: "BODY_BOUNDARY_ENRICHMENT"
    statement: "HT enriched at control block boundaries: first position=45.8%, last=42.9%, middle=25.7%"
    provenance: "C803"

  - id: "LINK_POSITIVE_ASSOCIATION"
    statement: "HT shows positive LINK association: OR=1.50 (p<0.001), 38.3% of LINK tokens are HT"
    provenance: "C806"

cross_system_manifestation:

  currier_a:
    anchoring: "Registry entry boundaries"
    density: 0.170
    positional_bias: "2.61x line-initial enrichment (p < 10^-126); 0 at category transition seams"
    category_correlation: "V=0.130 (weak, non-predictive)"
    ht_a_inverse: "rho=-0.367 — high-HT programs use less registry vocabulary (C344)"
    pp_ht_substitution: "rho=-0.294 — PP and HT partially substitute in responsibility budget (C507)"
    ri_ht_derivation: "97.9% HT MIDDLEs contain PP atoms (C924)"
    ri_ht_anti_correlation: "RI 0.48x in lines with HT (chi2=105.83) (C926)"
    label_elevation: "45.0% in labels vs 18.6% in paragraphs (2.42x enrichment) (C927)"
    morphology_a: "-or/-ol simplex forms favored (C419)"
    provenance: "C344, C419, C507, C924, C926, C927"

  currier_b:
    anchoring: "Temporal/attentional context"
    density: 0.149
    program_stratification: "EXTREME 15.9% > HIGH 10.4% > MODERATE 8.5% > LOW 5.7% (C341)"
    link_decoupling: "rho=0.010 (C342), but OR=1.50 positive association (C806)"
    link_proximity: "Body HT 2.53 vs 3.08 distance to LINK (C802)"
    escape_correlation: "rho=0.377, body-driven not line-1-driven (C796, C800)"
    azc_inverse: "rho=-0.352 (C797)"
    dual_control: "AZC(-) and FL(+) are orthogonal predictors (C798)"
    phase_synchrony: "EARLY (op-, pc-, do-), LATE (ta-); V=0.136 (p<0.0001) (C348)"
    grammar_trigger: "Preceding ch- -> 1.94x LATE enrichment (C413)"
    novel_combinations: "11.19% novel MIDDLE pairs; 90.7% HT-exclusive MIDDLEs (C812)"
    strategy_prediction: "r=+0.46 CAUTIOUS, r=-0.48 OPPORTUNISTIC (C488)"
    morphology_b: "-edy complex forms favored (C347, C348)"
    dark_pipeline_substrate: "300 dark-pipeline PP MIDDLEs produce exclusively HT/UN tokens (1,696 tokens, 0 grammar) — identification vocabulary channel distinct from grammar channel (C1137, C1138)"
    dark_pipeline_line_position: "Dark-pipeline HT tokens are interior-enriched (73.2% MIDDLE vs general HT 67.7%, chi-sq p<0.0001) — fills line interior rather than anchoring boundaries (C1147)"
    dark_pipeline_modulation: "Dark-pipeline MIDDLEs are 3.9x more section-differentiated than PP baseline (JS=0.483 vs 0.124); primary vehicle for section-level HT vocabulary modulation (C1148)"
    dark_bridge_tradeoff: "Dark-pipeline and bridge token rates anti-correlate (r=-0.865, within-section r=-0.82 to -0.88); folios allocate between identification and grammar channels (C1146)"
    provenance: "C341, C342, C348, C413, C488, C796, C797, C798, C800, C802, C806, C812, C1137, C1138, C1146, C1147, C1148"

  azc:
    anchoring: "Diagram geometry"
    density: 0.162
    boundary_preference: "S=39.7% > R=29.5% (C457)"
    entry_orientation: "Elevated before AZC, reduced after (C460)"
    anticipatory_compensation: "Quire r=0.343 (C459)"
    label_driven: "L-placement HT: 88.8% initial, 95% final; short lines drive both-boundary enrichment"
    provenance: "C457, C459, C460"

line1_header:

  enrichment: "50.2% vs 29.8% (Tier 0, C747)"
  step_function: "pos1=50.2%, pos2=31.7%, pos3+=27-33% (Tier 0, C748)"
  opening_only: "Last line 30.8% = interior 29.8% (Tier 0, C750)"

  composite_header:
    pp_component:
      share: "68.3%"
      function: "A-context declaration"
      prediction_accuracy: "13.9% vs 0.88% baseline (15.8x lift)"
    b_exclusive_component:
      share: "31.7%"
      function: "Folio identification"
      folio_unique_rate: "94.1%"
    independence: "PP fraction does NOT correlate with body PP size (rho=0.002)"
    provenance: "C794, C795, C799"

  morphological_distinction: "95.9% unique types; pch prefix 7.0% vs 1.9% in body (C749)"
  folio_specificity: "85.9% folio-singletons; 1,229 folio-unique AND line1-only tokens (67%) (C870)"
  double_header: "Folio line 1 = 50.2% HT (folio + paragraph header overlap) (C844)"
  provenance: "C747, C748, C749, C750, C794, C795, C799, C844, C870"

paragraph_header:

  header_enrichment: "44.9% HT vs 29.1% body (C840)"
  step_function: "pos1=45.2%, pos2=26.5%, pos3+=26-27% (C842)"
  prefix_markers: "pch- 16.9% + po- 16.6% = 33.5% of paragraph initiators (C843)"

  body_ht:
    vocabulary: "80.1% PP morphology (C085 primitives) (C801)"
    boundary_enrichment: "first=45.8%, last=42.9%, middle=25.7% (C803)"
    link_proximity: "2.53 vs 3.08 distance to LINK (C802)"
    jaccard_with_line1: "0.122 (very low overlap — different HT populations) (C801)"

  provenance: "C801, C802, C803, C840, C842, C843, C851"

morphology:

  decomposition: "HT_PREFIX + MIDDLE + SUFFIX"
  decomposition_rate: "71.3% (C347)"
  prefix_families: "yk-, op-, yt-, sa-, pc-, po-, pch-, do-, ta-"
  prefix_disjointness: "Zero overlap with A/B prefixes (ch-, qo-, sh-, etc.) (C347)"
  modularity: "Independent additive (no interaction, synergy p=1.0, interaction model 3.9% worse) (C417)"
  positional_signal: "CORE carries signal (d=69.6% line-initial, am=52.8% line-final) (C418)"

  compound_rate:
    ht: "45.8%"
    grammar: "31.5%"
  mean_middle_length:
    ht: "2.64"
    grammar: "2.04"
  decomposition_to_atoms: "100% of compounds decompose to core atoms (C935)"
  derived_vocabulary: "81.1% compound, 64.5% folio-unique (C766)"

  dark_pipeline_morphology:
    statement: "Dark-pipeline HT tokens use distinct construction from grammar-classified HT"
    gs_ext_middle_length: 3.39   # Grammar/Section tokens
    ht_middle_length: 1.81       # HT tokens
    prefix_rate_gs_ext: "83.9%"
    prefix_rate_ht: "58.1%"
    provenance: "C1138"
  atom_substrate:
    statement: "Dark-pipeline compounds are built from bridge atoms (86% of atom types, 91.6% of occurrences, 96.5% compound coverage)"
    bridge_atom_types: "43/50 (86%)"
    construction_hierarchy: "bridge atoms → compositional assembly (1-3 atoms) → dark-pipeline compounds → HT/UN identification tokens"
    provenance: "C1141"
  construction_grammar:
    statement: "Dark pipeline follows modified version of B's atom ordering grammar"
    c1065_agreement: "50% (7 matches, 7 mismatches of 14 testable pairs)"
    gateway_terminal_preserved: true
    dark_exclusive_atoms: 25
    provenance: "C1142"

  provenance: "C347, C417, C418, C766, C935, C1138, C1141, C1142"

operational_status:

  tier0_facts:
    terminal_independence: "p=0.92 (C404)"
    causal_decoupling: "V=0.10 (C405)"
    non_predictive: "MAE worsens by 0.003-0.005 (C415)"

  revision_c935:
    old: "HT has no operational content (non-operational)"
    new: "HT has redundant operational content (operationally redundant)"
    evidence: "Compound atoms predict body MIDDLEs at 71.6% hit (1.21x lift vs 59.2% random)"
    implication: "Removing HT doesn't change outcomes due to REDUNDANCY, not emptiness"
    weakens:
      - "C209 (attention pacing) — not falsified, just simpler explanation available"
      - "C221 (calligraphy practice) — not falsified, just simpler explanation available"

  construction_channel:
    statement: "Dark-pipeline PP MIDDLEs are the mechanistic source of HT identification vocabulary"
    pathway: "300 dark-pipeline MIDDLEs (C1137) → built from bridge atoms (C1141) → produce 1,696 HT/UN tokens, 0 grammar tokens"
    provenance: "C1137, C1141"

  b_exclusive_identity: "100% of B-exclusive vocabulary is HT (C792)"
  b_exclusive_count: "3,694 types (C792)"

  provenance: "C404, C405, C415, C792, C935, C1137, C1141"

# [TIER 3] Two-Axis Model
two_axis_model:
  tier: 3
  status: "WORKING — plausible but not promotable without external evidence"

  density_axis:
    description: "Tracks upcoming discrimination complexity"
    evidence: "r=0.504 with tail MIDDLEs (C477)"
    driver: "tail_pressure explains 68% of R-sq=0.279 (C461)"

  morphology_axis:
    description: "Tracks spare cognitive capacity"
    evidence: "r=-0.301 with folio complexity"
    pattern: "Hard task -> frequent but simple HT; easy task -> rare but complex HT"
    caveat: |
      C1080 REJECTS the compound rate prediction of this axis.
      Tail pressure POSITIVELY correlates with HT compound rate (rho=0.367, p=0.0007).
      High-tail folios have MORE compound HT, not less. The specification model (C935)
      wins: compound rate tracks specification density, not cognitive simplicity.
      The morphology axis may still apply to other complexity measures but NOT compound rate.

  strategy_connection: "r=+0.46 CAUTIOUS, r=-0.48 OPPORTUNISTIC (C488)"

  provenance: "C461, C477, C488, C489, C1080"

disallowed_interpretations:

  - claim: "HT tokens are non-operational (contain no content)"
    refutation: "C935 shows HT contains redundant operational content (compound atoms)"

  - claim: "HT annotates or labels adjacent content"
    refutation: "C415 (MAE worsens with HT conditioning), C416 (directional asymmetry)"

  - claim: "HT is scribal error or random mark-making"
    refutation: "C221 (deliberate practice structure), C406 (Zipf distribution, R-sq=0.92)"

  - claim: "HT encodes a separate message"
    refutation: "C415 (non-predictive), C418 (positional specialization without informativeness)"

  - claim: "HT is separate from grammar"
    refutation: "C414 (chi2=934, p<10^-145 grammar association)"

  - claim: "HT marks specific hazard zones"
    refutation: "C166 (0/35 at forbidden seams), C217 (0 true HT near hazards)"

  - claim: "HT is production-driven / codicologically organized"
    refutation: "C459 (content-driven anticipatory compensation, not quire-boundary aligned)"

  - claim: "HT has different vocabulary across systems"
    refutation: "C452 (Jaccard >= 0.947 unified prefix vocabulary across A/B/AZC)"

  - claim: "HT tokens are unknown / unclassified"
    refutation: "C611 (99.2% role prediction by PREFIX), C740 (HT = UN population, structurally classified)"

# Summary statement
summary: |
  HT is a structured, modular, operationally redundant compound specification
  layer that serves dual purpose: encoding operations (same atoms as body) and
  identifying programs (rare combinations). It exhibits system-conditioned
  positional alignment without predictive or causal influence on system behavior.

  In Currier A: aligned with registry layout (entry boundaries)
  In Currier B: aligned with temporal/attentional context (execution phase)
  In AZC: aligned with diagram geometry (label positions)

  Same layer, different anchoring pressures.

```

---

# Paragraph Unit Contract

```yaml

meta:
  name: "Paragraph Structural Contract"
  acronym: "PSC"
  version: "1.1"
  date: "2026-02-15"
  status: "ACTIVE"
  layer_type: "cross-system structural unit contract"
  derived_from: "Tier 0-2 constraints (structural)"
  governance: |
    PSC is NOT authoritative. Constraints are authoritative.
    PSC describes the paragraph as a structural primitive from the
    paragraph's own perspective, across Currier A and Currier B.
    Do not edit without updating source constraints first.

scope:
  systems: "Currier A and Currier B"
  excluded: "AZC (uses rings/stars/circles, not paragraphs)"
  definition: "Gallows-delimited text block within a folio"
  b_paragraphs: 585
  a_paragraphs: 342
  b_mean_per_folio: 7.1
  b_mean_lines: 4.4
  a_mean_lines: 4.8

# Explicit ownership declaration
ownership:
  psc_describes:
    - paragraph_definition     # operational unit, granularity validation
    - header_body_architecture # universal header-body pattern
    - independence_model       # parallel programs, self-containment
    - folio_paragraph_organization  # distribution, ordinariness, convergence
    - section_parameterization # section-dependent paragraph counts/roles
    - stability_properties     # neutrality, homogeneity, macro-dynamics
    - combinatorial_properties # cluster selectivity, gradient invariance
    - a_b_correspondence       # pool relationship, structural parallel
    - cross_system_manifestation  # A vs B paragraph properties
  psc_does_not_describe:
    - b_execution_gradient: "-> BCSC (spec->exec vocabulary C932-C934, prep verb concentration)"
    - b_ht_paragraph_structure: "-> BCSC (HT enrichment C840-C844, step function, prefix markers)"
    - a_internal_profiling: "-> CASC (size distribution C847, RI variance C848, section profile C849)"
    - a_combinatorial_grammar: "-> CASC (C1039-C1041 cluster selectivity, diversification)"
    - gallows_dynamics_detail: "-> BCSC (P-T transition C867, EN subfamily gradient C863)"
    - kernel_operation_mapping: "-> BCSC (kernel signature prediction C893, stereotypy C944)"
  ownership_boundaries: |
    PSC owns paragraph-as-unit properties (identity, organization, stability).
    BCSC retains B-grammar-expressed-at-paragraph-scale (execution gradient, HT patterns).
    CASC retains A-specific paragraph profiling (size, RI, cluster taxonomy).
    Ownership principle: if understanding a constraint requires knowing instruction
    classes, kernel operators, or roles -> stays in BCSC/CASC.
    If it describes a property of paragraphs independent of grammar -> PSC owns it.
    Each constraint in provenance is tagged OWNED or REFERENCED.

guarantees:

  - id: "OPERATIONAL_UNIT"
    statement: |
      Paragraphs are the operational aggregation level (not lines, not folios).
      Single line: 11.2% token survival. Paragraph: 31.8% survival (2.8x vs line).
      Full A-folio: 50.0% survival. RI structure visible ONLY at paragraph level.
    provenance: "C827, C834"

  - id: "GALLOWS_DELIMITED"
    statement: |
      Gallows-initial tokens mark paragraph boundaries at 81.5%.
      Distribution: p=55.3%, t=28.7%, k=11.9%, f=4.0%.
      Paragraph-initial rate: 8.6% vs 2.7% body (3.2x enrichment).
    provenance: "C864, C841"

  - id: "HEADER_BODY"
    statement: |
      Universal header-body architecture across both systems.
      Currier A: RI concentration 3.84x in paragraph first line (C848).
      Currier B: HT enrichment +15.8pp (44.9% line 1 vs 29.1% body, d=0.721) (C840).
      Both systems show step function: sharp drop at line 2, flat body thereafter.
    provenance: "C840, C848, C854"

  - id: "COMPOUND_SPECIFICATION"
    statement: |
      Headers contain compressed specifications that body lines unpack.
      Line-1 compound atoms predict body simple MIDDLEs at 71.6% hit rate
      (vs 59.2% random, 1.21x lift). HT compound rate: 45.8% vs grammar 31.5%.
      A shows parallel pattern: RI concentrated 3.84x in first line.
    provenance: "C935, C848"

  - id: "PARALLEL_PROGRAMS"
    statement: |
      Paragraphs within a folio are independent mini-programs, not sequential steps.
      Role similarity (normalized): 0.831 cohesion.
      Prefix overlap: 0.300. Vocabulary Jaccard: 0.061.
      Verdict: PARALLEL_PROGRAMS model (independent mini-programs).
    provenance: "C855, C862"

  - id: "SELF_CONTAINMENT"
    statement: |
      No inter-paragraph linking. B both-position tokens: 7.1% (187 types:
      24 convergent, 39 divergent, 124 symmetric). A RI both-position: 0.6%.
      Paragraphs are self-contained operational units.
    provenance: "C845"

  - id: "VOCABULARY_DISTRIBUTION"
    statement: |
      Folio unique vocabulary is DISTRIBUTED across paragraphs, not concentrated.
      Gini coefficient: 0.279. Paragraph 1 unique vocab share: 27.4% mean, 21.2% median.
      Distribution is roughly uniform across ordinals.
    provenance: "C856"

  - id: "FIRST_ORDINARINESS"
    statement: |
      First paragraph is NOT structurally special.
      Vocabulary predictivity: 11.8%. HT rate Par 1: 34.6% vs Later: 36.8% (0.94x).
      No elevated unique vocabulary rate. Not a template or summary.
    provenance: "C857"

  - id: "BODY_HOMOGENEITY"
    statement: |
      Body lines are compositionally homogeneous after controlling for line length.
      EN fraction rho: -0.023 (p=0.350). FL fraction rho: -0.050 (p=0.068).
      CC fraction rho: -0.049 (p=0.076). All collapse to ~0 after length control.
      Only length progression (rho=-0.229, p=0.001) is systematic.
    provenance: "C963"

  - id: "POOL_RELATIONSHIP"
    statement: |
      A-B vocabulary relationship is pool-based, not address-based.
      Spearman rho: 0.694 (p < 0.001). Raw lift: 2.49x, pool-size-controlled: 1.20x.
      Top 10 A paragraphs capture 85.9% of best matches. No 1:1 A->B pairing.
    provenance: "C846"

  - id: "STRUCTURAL_PARALLEL"
    statement: |
      A and B show matching paragraph architecture.
      A mean lines: 4.8. B mean lines: 4.37 (Mann-Whitney p=0.067, d=0.110).
      Both exhibit 5-cluster taxonomy (A silhouette=0.337, B silhouette=0.237).
      Both show header-body enrichment in first line.
    provenance: "C854, C850, C853"

  - id: "SECTION_PARAMETERIZED"
    statement: |
      Section modulates paragraph count, size, and role composition.
      HERBAL: 2.2 pars/folio, 49.8 tok/par.
      BIO: 7.5 pars/folio, 46.0 tok/par.
      RECIPE: 10.2 pars/folio, 38.3 tok/par.
      PHARMA: 14.0 pars/folio, 12.6 tok/par.
      Section effects are ADDITIVE only (C1047: no section-dynamics interaction).
    provenance: "C860, C852"

  - id: "LINK_HAZARD_HT_NEUTRAL"
    statement: |
      LINK, hazard density, and HT density are all NEUTRAL across paragraph ordinals.
      LINK rate CV: 0.16. Hazard rate CV: 0.21.
      LINK body allocation: 79.4%. Hazard body allocation: 80.9%.
      HT ordinal correlation: rho=0.018, p=0.69. First vs last: MW p=0.086 NS (C1083).
    provenance: "C861, C1083"

  - id: "MACRO_DYNAMICS_NEUTRAL"
    statement: |
      6-state automaton does NOT differentiate paragraph position.
      Header AXM: 0.705, body AXM: 0.677 (delta +0.028, p=0.007).
      Effect is tiny and driven by gallows tokens (87.7% AXM).
      Macro-dynamics operate at folio/section scale, not paragraph scale.
    provenance: "C1022"

  - id: "CLUSTER_SELECTIVE"
    statement: |
      Paragraphs draw from fewer C475 compatibility clusters than random.
      Currier A: entropy 1.502 vs null 1.780 (z=-2.830, p=0.002) (C1039).
      Currier B: entropy 1.512 vs null 1.824 (z=-2.614, p=0.007) (C1052).
      Paragraphs specialize within the compatibility graph in both systems.
    provenance: "C1039, C1052"

invariants:

  - id: "SIZE_SIMILARITY"
    statement: "A=4.8 vs B=4.4 lines per paragraph (Mann-Whitney p=0.067, d=0.110)"
    provenance: "C854"

  - id: "COUNT_SECTION_DEPENDENT"
    statement: "HERBAL 2.2, BIO 7.5, RECIPE 10.2, PHARMA 14.0 paragraphs per folio"
    provenance: "C860"

  - id: "VOCABULARY_CONVERGENCE_WEAK"
    statement: "Later paragraphs weakly converge: cumulative overlap rises from 14% (par 2) to 39% (par 8). Vocabulary similarity by pair distance: FLAT (0.055->0.045)"
    provenance: "C859"

  - id: "HAZARD_NO_PARAGRAPH_CLUSTERING"
    statement: "No paragraph-level hazard concentration (folio p=0.688, paragraph p=0.320)"
    provenance: "C1027"

  - id: "GRADIENT_INVARIANCE"
    statement: "Affordance bin composition static across quintiles: HUB Q0=64.9%, Q1=61.6%, Q2=67.4%, Q3=62.8%, Q4=64.9% (rho=-0.10, p=0.873)"
    provenance: "C1054"

  - id: "VOCABULARY_CORRESPONDENCE"
    statement: "A folios provide 81.2% MIDDLE coverage for B paragraphs (lift 1.71x). Single A paragraph covers 58.3%; aggregating 3+ reaches 80%"
    provenance: "C885"

  - id: "PARAGRAPH_COUNT_COMPLEXITY"
    statement: "Paragraph count is weak proxy for complexity: rho=0.836 with vocabulary size, 0.802 with total tokens, 0.826 with role diversity"
    provenance: "C858"

  - id: "GALLOWS_BOUNDARY_ENRICHMENT"
    statement: "3.2x gallows enrichment at paragraph boundaries: 8.6% paragraph-initial vs 2.7% body"
    provenance: "C841, C864"

  - id: "CLUSTER_COUNT_CONVERGENCE"
    statement: "Both A and B exhibit 5-cluster paragraph taxonomy (A silhouette=0.337, B silhouette=0.237)"
    provenance: "C850, C853"

  - id: "BODY_LENGTH_SHRINKAGE"
    statement: "Lines shrink toward paragraph end: rho=-0.229, p=0.001 — sole systematic body progression"
    provenance: "C963"

cross_system_manifestation:

  currier_a:
    function: "Material specification pool"
    paragraph_count: 342
    mean_lines: 4.8
    header_enrichment: "RI 3.84x in first line (C848)"
    size_distribution:
      by_position: "first=5.35, middle=2.75, last=5.36, only=11.79 lines"
      provenance: "C847 (CASC)"
    section_profile:
      statement: "P: 17.2% RI, 67.5% PP vs H: 8.4% RI, 42% PP (p=0.0006)"
      provenance: "C849 (CASC)"
    cluster_taxonomy:
      clusters: 5
      silhouette: 0.337
      types: "short-RI (34%), long-linker (8%), standard (58%)"
      provenance: "C850 (CASC)"
    combinatorial_grammar:
      cluster_selectivity: "Entropy 1.502 vs null 1.780 (z=-2.830, p=0.002) (C1039, CASC)"
      folio_compatibility: "Within-folio 0.880 vs between-folio 0.811 (C1040, CASC)"
      diversification: "Cross-line compatibility LOWER than random (z=-3.567) — complementary, not redundant (C1041, CASC)"
    special_types:
      pure_ri: "83% of pure-RI first-line paragraphs in section P (C915, CASC)"
      animal_candidates: "6 paragraphs pass kernel validation (C884, CASC, Tier 3)"
    provenance: "C847-C850, C881, C884, C915, C1039-C1041 (all CASC-owned)"

  currier_b:
    function: "Self-contained execution program"
    paragraph_count: 585
    mean_per_folio: 7.1
    mean_lines: 4.4
    header_enrichment: "HT +15.8pp (44.9% vs 29.1%, d=0.721) (C840, BCSC)"
    ht_step_function: "Pos 1=45.2%, pos 2=26.5%, pos 3+=26-27% (C842, BCSC)"
    ht_prefix_markers: "pch- 16.9% + po- 16.6% = 33.5% of initiators (C843, BCSC)"
    gallows_initial: "71.5% p/t/k/f initial (C841, BCSC)"
    execution_gradient:
      statement: "Spec->exec vocabulary gradient (BCSC-owned)"
      rare_middle_trend: "r=-0.97 (Q0->Q4)"
      universal_middle_trend: "r=+0.92 (Q0->Q4)"
      provenance: "C932 (BCSC)"
    prep_verb_concentration: "te 2.7x, pch 2.8x enrichment in Q0 vs Q4 (C933, BCSC)"
    kernel_signature:
      statement: "HIGH_K=2x FQ (p<0.0001); HIGH_H EN (p=0.036)"
      provenance: "C893 (BCSC)"
    section_role_interaction:
      statement: "RECIPE 44.5% EN; PHARMA 43.2% FQ (Kruskal-Wallis p<0.0001)"
      provenance: "C852 (BCSC)"
    cluster_taxonomy:
      clusters: 5
      silhouette: 0.237
      types: "single-line (9%), long-EN (10%), standard (81%)"
      provenance: "C853 (BCSC)"
    novel_combinations: "B paragraphs show 11.19% novel MIDDLE pairs (C812, BCSC)"
    cluster_selectivity: "Entropy 1.512 vs null 1.824 (z=-2.614, p=0.007) (C1052)"
    gradient_invariance: "Affordance bin composition static across quintiles (C1054)"
    provenance: "C840-C844, C851-C853, C863-C869, C893, C932-C935, C944, C1052, C1054"

a_b_correspondence:

  pool_model:
    statement: |
      A paragraphs and B paragraphs share vocabulary via pool overlap,
      not direct 1:1 address mapping. 39 A paragraphs serve 568 B paragraphs.
    best_match_coverage: "66.2%"
    random_baseline: "26.6%"
    raw_lift: "2.49x"
    controlled_lift: "1.20x"
    pool_size_correlation: "rho=0.694"
    hub_concentration: "Top 10 A paragraphs capture 85.9% of best matches"
    provenance: "C846"

  vocabulary_correspondence:
    statement: "A folios provide 81.2% MIDDLE coverage for B paragraphs"
    a_folio_coverage: "81.2% (lift 1.71x)"
    a_paragraph_coverage: "58.3% (lift 2.04x, paragraphs with >= 10 PP tokens)"
    aggregation_curve: "2 A paragraphs=76.5%, 3=80.4%, 5=84.7%"
    provenance: "C885"

  structural_parallel:
    size: "A=4.8 vs B=4.4 lines (p=0.067, d=0.110, not significant)"
    clustering: "Both k=5 (A sil=0.337, B sil=0.237)"
    header_body: "Both show first-line enrichment (A: RI 3.84x, B: HT +15.8pp)"
    provenance: "C854"

folio_paragraph_organization:

  role_template:
    statement: "Paragraphs are NOT variations on a folio template"
    role_similarity: 0.831
    prefix_overlap: 0.300
    vocabulary_jaccard: 0.061
    ht_overlap: 0.024
    verdict: "PARALLEL_PROGRAMS"
    provenance: "C855, C862"

  vocabulary_distribution:
    statement: "Folio unique vocabulary is DISTRIBUTED, not concentrated"
    gini: 0.279
    par1_share_mean: "27.4%"
    par1_share_median: "21.2%"
    provenance: "C856"

  first_paragraph:
    statement: "Paragraph 1 is NOT structurally special"
    vocabulary_predictivity: "11.8%"
    ht_ratio: "0.94x (34.6% vs 36.8%)"
    provenance: "C857"

  paragraph_count:
    statement: "Paragraph count correlates with folio complexity but is weak proxy"
    rho_vocabulary: 0.836
    rho_tokens: 0.802
    rho_roles: 0.826
    provenance: "C858"

  vocabulary_convergence:
    statement: "Later paragraphs show WEAK vocabulary convergence"
    cumulative_overlap: "par2=14.2%, par4=25.4%, par8=38.6%"
    similarity_by_distance: "FLAT (0.055->0.045)"
    role_distance_by_distance: "INCREASING (0.259->0.329)"
    provenance: "C859"

  section_organization:
    herbal: {pars_per_folio: 2.2, tokens_per_par: 49.8, cohesion: 0.070}
    bio: {pars_per_folio: 7.5, tokens_per_par: 46.0, cohesion: 0.071}
    recipe: {pars_per_folio: 10.2, tokens_per_par: 38.3, cohesion: 0.053}
    pharma: {pars_per_folio: 14.0, tokens_per_par: 12.6, cohesion: 0.056}
    provenance: "C860"

  link_hazard_neutrality:
    link_cv: 0.16
    hazard_cv: 0.21
    link_body_allocation: "79.4%"
    hazard_body_allocation: "80.9%"
    provenance: "C861"

stability_properties:

  body_homogeneity:
    statement: "Body lines compositionally homogeneous after length control"
    length_rho: -0.229
    length_p: 0.001
    en_rho: -0.023
    fl_rho: -0.050
    cc_rho: -0.049
    interpretation: "Paragraphs shrink toward end but each body line is structurally equivalent"
    provenance: "C963"

  macro_dynamics_neutral:
    statement: "6-state automaton does NOT differentiate paragraph position"
    header_axm: 0.705
    body_axm: 0.677
    delta: "+0.028"
    chi2: 16.04
    p: 0.007
    interpretation: "Tiny effect driven by gallows tokens (87.7% AXM); dynamics operate at folio/section scale"
    provenance: "C1022"

  hazard_no_paragraph_clustering:
    statement: "Hazard violations do not cluster by paragraph"
    folio_p: 0.688
    paragraph_p: 0.320
    violation_rate: "26.5% (717/2707 transitions)"
    provenance: "C1027"

  gradient_invariance:
    statement: "Affordance bin composition static across paragraph quintiles"
    hub_q0: 0.649
    hub_q1: 0.616
    hub_q2: 0.674
    hub_q3: 0.628
    hub_q4: 0.649
    spearman_rho: -0.10
    p: 0.873
    interpretation: "HUB vocabulary provides static scaffold; gradient is surface, not deep structure"
    provenance: "C1054"

disallowed_interpretations:

  - id: "NOT_SEQUENTIAL_STEPS"
    claim: "Paragraphs are sequential steps in a single process"
    refutation: "C855, C862: Role similarity 0.831 but vocabulary Jaccard 0.061; PARALLEL_PROGRAMS verdict"

  - id: "NOT_ORDINAL_EXECUTION"
    claim: "Paragraph ordinal position encodes execution order"
    refutation: "C855, C862: Independent mini-programs; ordinal 3 does not execute 'after' ordinal 2. C863 shows statistical gradient by ordinal but this is distributional, not ordering."

  - id: "NOT_FIRST_TEMPLATE"
    claim: "First paragraph is template or summary for the folio"
    refutation: "C857: Vocabulary predictivity only 11.8%; HT rate 0.94x (not elevated)"

  - id: "NOT_ROLE_DIFFERENTIATED_BODY"
    claim: "Body lines have different structural roles (e.g., setup vs execution)"
    refutation: "C963: EN/FL/CC fractions collapse to rho~0 after length control; only length shrinks"

  - id: "NOT_ONE_TO_ONE_MAPPING"
    claim: "A paragraphs map 1:1 to B paragraphs"
    refutation: "C846: Pool-based with rho=0.694; 39 A paragraphs serve 568 B; lift drops from 2.49x to 1.20x after pool-size control"

  - id: "NOT_RECIPES"
    claim: "Paragraphs encode individual recipes or formulations"
    refutation: "C120 (PURE_OPERATIONAL), C846 (pool-based), C171 (closed-loop control, not batch recipes)"

  - id: "NOT_LENGTH_COMPLEXITY"
    claim: "Paragraph length determines operational complexity"
    refutation: "C858: rho=0.42 only (weak proxy); complexity is multi-dimensional"

  - id: "NOT_POSITIONAL_GRAMMAR"
    claim: "Paragraph position within folio affects grammar"
    refutation: "C861: LINK CV=0.16, hazard CV=0.21 — both neutral across ordinals"

  - id: "NOT_HAZARD_CLUSTERS"
    claim: "Paragraphs cluster hazard violations"
    refutation: "C1027: paragraph clustering p=0.320; folio p=0.688; no spatial concentration"

# Summary statement
summary: |
  A paragraph is a gallows-delimited, self-contained operational unit that
  constitutes the primary aggregation level for both Currier A and Currier B.

  In Currier A: paragraphs are material specification pools — groups of
  complementary entries that diversify within selected compatibility clusters.
  In Currier B: paragraphs are independent mini-programs with header-body
  architecture, specification-to-execution vocabulary gradients, and
  kernel-predicted operation types.

  Both systems show matching 5-cluster taxonomy, header-body enrichment,
  and pool-based vocabulary correspondence. Paragraphs operate independently
  within folios (PARALLEL_PROGRAMS model). Grammar, hazard density, and
  macro-dynamics are all paragraph-position-neutral.

```

---
