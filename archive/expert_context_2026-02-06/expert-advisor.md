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
embedded below. You have ALL 783 validated constraints and 55 explanatory fits loaded
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

**Generated:** 2026-02-05 13:55
**Version:** FROZEN STATE (783 constraints, 55 fits)

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

---

# Project Overview & Navigation

**Source:** `context/CLAUDE_INDEX.md`

# Voynich Manuscript Analysis - Context Index

**Version:** 3.12 | **Status:** FROZEN | **Constraints:** 794 | **Date:** 2026-02-05

> **STRUCTURE_FREEZE_v1 ACTIVE** — Structural inspection layer is frozen. See [SYSTEM/CHANGELOG.md](SYSTEM/CHANGELOG.md) for post-freeze paths.
>
> **PIPELINE CLOSED** — A→AZC→B control architecture fully reconstructed and certified. PCA-v1 passed. Structural work is DONE.

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

## DATA LOADING WARNING

> **CRITICAL: When writing scripts that load the transcript, ALWAYS filter to the H transcriber track.**
>
> The transcript contains 18 parallel transcriber readings. Using all transcribers causes **~3.2x token inflation** and creates **false patterns** from transcriber interleaving.
>
> **Required reading before writing ANY data-loading code:** [DATA/TRANSCRIPT_ARCHITECTURE.md](DATA/TRANSCRIPT_ARCHITECTURE.md)

```python
# MANDATORY pattern for loading data
df = df[df['transcriber'] == 'H']  # PRIMARY track only
```

| Metric | All Transcribers | H Only (CORRECT) |
|--------|------------------|------------------|
| Total tokens | 122,235 | 37,957 |
| Currier A | 37,214 | 11,415 |
| Currier B | 75,620 | 23,243 |
| AZC (NA) | 9,401 | 3,299 |

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

1. **MIDDLEs bifurcate into RI and PP.** Registry-Internal (609) are A-exclusive discriminators. Pipeline-Participating (404) are shared with B. (C498)

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

## Navigation

| I need to... | Read this file |
|--------------|----------------|
| **Load transcript data** | [DATA/TRANSCRIPT_ARCHITECTURE.md](DATA/TRANSCRIPT_ARCHITECTURE.md) |
| **Token annotation data** | [DATA/TRANSCRIPT_ARCHITECTURE.md](DATA/TRANSCRIPT_ARCHITECTURE.md) → Annotation Data Files |
| Understand the core finding | [CORE/frozen_conclusion.md](CORE/frozen_conclusion.md) |
| Know what's been ruled out | [CORE/falsifications.md](CORE/falsifications.md) |
| **Validate A structure (API)** | [STRUCTURAL_CONTRACTS/currierA.casc.yaml](STRUCTURAL_CONTRACTS/currierA.casc.yaml) |
| **Validate B grammar (API)** | [STRUCTURAL_CONTRACTS/currierB.bcsc.yaml](STRUCTURAL_CONTRACTS/currierB.bcsc.yaml) |
| **Understand A→AZC transform** | [STRUCTURAL_CONTRACTS/azc_activation.act.yaml](STRUCTURAL_CONTRACTS/azc_activation.act.yaml) |
| **Understand AZC→B propagation** | [STRUCTURAL_CONTRACTS/azc_b_activation.act.yaml](STRUCTURAL_CONTRACTS/azc_b_activation.act.yaml) |
| Work with Currier B grammar | [ARCHITECTURE/currier_B.md](ARCHITECTURE/currier_B.md) |
| Work with Currier A registry | [ARCHITECTURE/currier_A.md](ARCHITECTURE/currier_A.md) |
| Currier A characterization (detailed) | [ARCHITECTURE/currier_A_summary.md](ARCHITECTURE/currier_A_summary.md) |
| Work with AZC hybrid text | [ARCHITECTURE/currier_AZC.md](ARCHITECTURE/currier_AZC.md) |
| Understand the Human Track layer | [CLAIMS/HT_HIERARCHY.md](CLAIMS/HT_HIERARCHY.md) (canonical) |
| Look up a specific constraint | [CLAIMS/INDEX.md](CLAIMS/INDEX.md) → find by number, then follow to registry |
| Understand the constraint system | [MODEL_CONTEXT.md](MODEL_CONTEXT.md) → architectural guide (read BEFORE constraints) |
| Write new analysis safely | [SYSTEM/METHODOLOGY.md](SYSTEM/METHODOLOGY.md) |
| Understand tier definitions | [SYSTEM/TIERS.md](SYSTEM/TIERS.md) |
| Understand semantic boundaries | [SYSTEM/SEMANTIC_MANIFESTO.md](SYSTEM/SEMANTIC_MANIFESTO.md) |
| Design external validation | [SYSTEM/EXTERNAL_CORROBORATION.md](SYSTEM/EXTERNAL_CORROBORATION.md) |
| Check quantitative metrics | [METRICS/](METRICS/) (grammar, hazard, coverage) |
| See speculative interpretations | [SPECULATIVE/](SPECULATIVE/) (apparatus-centric semantics, CCM, ECR) |
| **Currier A interface postures** | [SPECULATIVE/tier3_interface_postures.md](SPECULATIVE/tier3_interface_postures.md) |
| Understand apparatus-centric view | [SPECULATIVE/apparatus_centric_semantics.md](SPECULATIVE/apparatus_centric_semantics.md) |
| Trace constraint to source phase | [MAPS/claim_to_phase.md](MAPS/claim_to_phase.md) |
| Work with explanatory fits | [MODEL_FITS/INDEX.md](MODEL_FITS/INDEX.md) |
| Understand fit methodology | [SYSTEM/FIT_METHODOLOGY.md](SYSTEM/FIT_METHODOLOGY.md) |

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
| Validated constraints | 794 |
| Completed phases | 274 |
| Folios enumerated | 83 |
| Instructions cataloged | 75,248 |
| Token types in grammar | 479 |
| Instruction classes | 49 |
| Scripts in archive | 98 |
| Structural contracts | 4 (LOCKED) |

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

## File Registry

- **Constraints (by topic):** [CLAIMS/INDEX.md](CLAIMS/INDEX.md) - Browse by category, follow links to details
- **Architectural guide:** [MODEL_CONTEXT.md](MODEL_CONTEXT.md) - How to interpret the constraint system
- **Structural contracts:** [STRUCTURAL_CONTRACTS/](STRUCTURAL_CONTRACTS/) - Derived API specifications (CASC, AZC-ACT, AZC-B-ACT, BCSC)
- **Phases:** [MAPS/phase_index.md](MAPS/phase_index.md) - 118 phases with status
- **Methodology:** [SYSTEM/METHODOLOGY.md](SYSTEM/METHODOLOGY.md) - Warnings and patterns
- **Changelog:** [SYSTEM/CHANGELOG.md](SYSTEM/CHANGELOG.md) - Context system updates

### Programmatic Resources

These files are for scripts and validation tools, NOT for reading in full:

- **CONSTRAINT_TABLE.txt** - TSV format for programmatic constraint lookup/validation
- **generate_constraint_table.py** - Regenerates table from registry files
- **MODEL_FITS/FIT_TABLE.txt** - TSV format for programmatic fit lookup

### Model Fits (Separate from Constraints)

Fits are explanatory models that account for observed patterns. They do NOT constrain the model.

- **Fits explain. Constraints bind.** See [SYSTEM/FIT_METHODOLOGY.md](SYSTEM/FIT_METHODOLOGY.md)
- **Fit registry:** [MODEL_FITS/INDEX.md](MODEL_FITS/INDEX.md) (31 fits logged)
- **Cross-reference:** [MAPS/fit_to_constraint.md](MAPS/fit_to_constraint.md)
- **Epistemic layers:** [SYSTEM/epistemic_layers.md](SYSTEM/epistemic_layers.md) - Constraint vs Fit vs Speculation legend

### Projection Specs (UI Display Rules)

Projection specs govern how external alignments are displayed in tooling without acting like structure.

- **Directory:** [PROJECTIONS/](PROJECTIONS/) - Non-binding, UI-only display rules
- **Brunschwig lens:** [PROJECTIONS/brunschwig_lens.md](PROJECTIONS/brunschwig_lens.md) - Product type alignment display
- **Principle:** "Shows where external practice fits; never claims manuscript encodes that practice"

---

## Automation

This project includes skills and hooks for automated research workflows:

| Tool | Purpose | Location |
|------|---------|----------|
| **phase-analysis** skill | Analyze phase results, validate constraints | `.claude/skills/phase-analysis/` |
| **constraint-lookup** skill | Find and cite constraints | `.claude/skills/constraint-lookup/` |
| **Constraint validator** | Warn on invalid C### references | `archive/scripts/validate_constraint_reference.py` |
| **Metrics extractor** | Quick phase metric extraction | `archive/scripts/extract_phase_metrics.py` |

**Workflows are documented in:** [SYSTEM/METHODOLOGY.md](SYSTEM/METHODOLOGY.md) → "Research Workflow (Automated)"

---

## Context System

This directory uses **progressive disclosure**. Do not read all files.

1. Start here (CLAUDE_INDEX.md)
2. Follow links as needed
3. Stop when you have enough context
4. Use skills for repetitive research tasks

See [README.md](README.md) and [SYSTEM/HOW_TO_READ.md](SYSTEM/HOW_TO_READ.md) for navigation.

---

*Context System v3.07 | Project v1.8 FROZEN STATE | PIPELINE CLOSED | PCA-v1 CERTIFIED | 2026-01-27*


---

# Architectural Framework

**Source:** `context/MODEL_CONTEXT.md`

# MODEL_CONTEXT.md

**Version:** 3.14 | **Date:** 2026-02-04 | **Status:** FROZEN

This document explains how to read and interpret the constraint system. It does not duplicate constraints. It provides the architectural lens, epistemic governance, and integration logic required to understand them as a coherent model.

---

## I. PROJECT IDENTITY & CLAIM BOUNDARY

### Core Identity Statement

The Voynich Manuscript is a **designed, non-semantic, multi-layer control artifact**.

It is:
- A family of closed-loop control programs (Currier B)
- A complexity-frontier registry (Currier A)
- A placement-coded hybrid workflow system (AZC)
- A human-pacing layer (HT)

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
| Human Track | Distributed | Non-operational human pacing | No | Statistical |

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

**Positional Classes (C539):**
- EARLY position (line-start): ENERGY prefixes (ch, sh, qo compounds) dominate (79%)
- LATE position (line-end): V+L prefixes (al, ar, or) cluster at 3.78x enrichment
- LATE prefixes are morphologically distinct (vowel+liquid vs consonantal) and suffix-depleted (68-70%)

### MIDDLE Function

MIDDLEs are the primary vocabulary layer:
- **Currier A: 1,013 unique MIDDLEs** (609 RI + 404 PP)
- Currier B: 1,339 unique MIDDLEs (regenerated 2026-01-24)
- Shared (A + B): 404 MIDDLEs (PP, Pipeline-Participating)
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
- 20% are shared across prefixes
- 27 universal MIDDLEs appear in 6+ prefix classes

**Frequency Distribution (Tier 3):**
- Core (top 30): 67.6% of usage, mode-flexible, section-stable
- Tail (~1,150): 32.4% of usage, mode-specific, hazard-concentrated
- Rare MIDDLEs cluster in high-hazard contexts (rho=-0.339, p=0.0001)

### PP vs RI: The Two-Track Vocabulary (C498, C498.d, C504-C506)

A-record MIDDLEs partition into **two populations** with different B-side effects:

| Type | Count | Propagates to B? | Length | Function |
|------|-------|------------------|--------|----------|
| **PP** | ~90 | **Yes** | 1-2 chars | Compatibility carriers |
| **RI** | ~1,290 | **No** | 2-6 chars | A-internal discrimination |

**RI as Complexity Gradient (C498.d):**

RI singleton/repeater status is **primarily a combinatorial effect**, not a functional bifurcation:

```
RI MIDDLEs (~1,290 types)
│
└── Single population with LENGTH/COMPLEXITY GRADIENT:

    Short (2-3 chars) ←────────────────→ Long (5+ chars)
         │                                    │
     More repeats                        More unique
      (48-55%)                           (82-100%)
         │                                    │
     Combinatorially                    Combinatorially
       limited                             diverse
```

**Evidence (C498.d):**
- Spearman correlation: rho = -0.367, p < 10⁻⁴²
- Singleton rate by length: 2-char=48%, 4-char=73%, 6-char=96%, 8+=100%
- Mean length singletons: 4.82 chars; repeaters: 3.61 chars

**MIDDLE Sub-Component Structure (C267.a):**

MIDDLEs are compositional - **218 sub-components** reconstruct 97.8% of all MIDDLEs:

```
TOKEN = PREFIX + MIDDLE + SUFFIX
                   ↓
              MIDDLE = SUB1 + SUB2 + [SUB3...]
```

This explains why longer MIDDLEs are more likely unique: more sub-components → more combinations.

**Previous interpretations WEAKENED:**
- "RI-D as section markers" → Tier 3 (provisional)
- "RI-B as scaffolding" → Tier 3 (provisional)
- The structural observations remain Tier 2; functional interpretations demoted

**'fachys' clarification:** 'fachys' (the famous first word) appears exactly once and is folio-first. However, this pattern represents only 4.2% of RI singletons (41 tokens). The remaining 95.8% appear mid-record.

**Two-level PP effect (C506, C506.a):**

| Level | What PP Determines | Evidence |
|-------|-------------------|----------|
| **Class** | Which instruction types survive | COUNT matters (r=0.715), COMPOSITION doesn't (cosine=0.995) |
| **Token** | Which variants within classes are available | COMPOSITION matters (Jaccard=0.953 when same classes) |

PP is a **capacity variable** at class level, but a **configuration variable** at token level:
- PP COUNT strongly predicts B class survival (r=0.715, p<10^-247)
- PP COMPOSITION does not affect which classes survive (cosine=0.995)
- PP COMPOSITION does affect which tokens within surviving classes are available (~5% variation)

**Intra-class behavioral heterogeneity (C506.b):**

Tokens within the same class but with different MIDDLEs are **positionally compatible but behaviorally distinct**:

| Dimension | Same-MIDDLE | Different-MIDDLE | p-value |
|-----------|-------------|------------------|---------|
| Position | Similar | Similar | 0.11 (NS) |
| Transitions | Similar | **Different** | <0.0001 |

73% of MIDDLE pairs within classes have transition JS divergence > 0.4. This is the "chop vs grind" pattern: both can appear in the same grammatical slot, but they lead to different subsequent operations.

**Variable taxonomy:**

| Variable | System | What It Does |
|----------|--------|--------------|
| **Routing** | AZC | Position-indexed legality |
| **Differentiation** | RI | Identity exclusion |
| **Capacity** | PP | Class survival breadth (count) |
| **Configuration** | PP | Intra-class token selection (composition) |

**Key insight:** Classes define **grammatical equivalence** (what can substitute), not **semantic equivalence** (what does the same thing). The 49 classes provide the operational grammar. The ~480 tokens provide behaviorally distinct variants within that grammar. PP COUNT determines class breadth. PP COMPOSITION determines which behavioral variants are available.

This resolves the "480 token paradox": why maintain 480 tokens if 49 classes suffice? Answer: material-specific behavioral parameterization. Animal materials don't need different *classes* than plant materials — they need different *execution flows* within the same class structure.

### MIDDLE Compositional Grammar (C510-C513)

MIDDLEs have internal compositional structure with systematic construction rules:

**Generative Architecture:**
```
[RI elaboration] + [PP flexible core] + [PP terminator]
   START-class        FREE-class          END-class
   (16.1% PP)         (40.9% PP)          (71.4% PP)
```

**Key Properties:**

| Property | Value | Constraint |
|----------|-------|------------|
| Positional constraint rate | 41.2% | C510 |
| Positional FREE rate | 58.8% | C510 |
| Derivational seeding ratio | 12.67x | C511 |
| RI containing PP atoms | 99.1% | C512 |
| PP section-invariance ratio | 8.3x | C512 |

**PP as Generative Substrate (C512):**
- PP MIDDLEs are 8.3x more section-invariant than RI MIDDLEs (Jaccard 0.729 vs 0.088)
- 60.7% of PP atoms appear in ALL three sections (H/P/T) vs 2.6% of RI MIDDLEs
- RI MIDDLEs are compositional elaborations of PP stock, not independently constructed

**Positional Asymmetry (C512.a):**
- END-class dominated by PP atoms (71.4%): `ch`, `d`, `e`, `g`, `h`, `k`, `s`, `t`
- START-class dominated by RI elaborations (only 16.1% PP)
- PP atoms are more positionally FREE (69.2%) than average (58.8%)

**Interpretation:**
The grammar is permissive but structured. PP atoms are the universal morphological substrate — the "Lego bricks" that appear across all sections. RI elaborations provide section-specific discriminative extensions, predominantly at the start of MIDDLEs. PP terminators close forms.

**This explains:**
- C498.d (length predicts uniqueness): Short forms seed long forms derivationally
- C475 (95.7% incompatibility): Positional grammar restricts legal combinations
- C506.b (intra-class heterogeneity): PP composition determines behavioral variants
- C502 (~80% filtering): Extracts PP primitives from RI elaborations

**Short Singleton Variance (C513):** Singleton status at ≤3 characters is sampling variance (Jaccard = 1.00 with repeaters), not a functional distinction.

### SUFFIX Function

Suffixes encode universal form markers:
- 22/25 significant suffixes appear across 6+ prefix classes
- Suffix selection is compositionally conditioned
- Suffixes do not carry semantic content

**REGIME Compatibility (C495):** SUFFIX is associated with execution-context breadth:
- `-r` suffix enriched in universal REGIME compatibility (11.5% vs 4.2%)
- `-ar`, `-or` suffixes enriched in single-REGIME restriction
- PREFIX shows no REGIME association
- This is associative, not causal - SUFFIX correlates with breadth, doesn't encode it

### Infrastructure Tokens

DA-family tokens are **infrastructural**:
- Same role in A, B, and AZC
- Mark internal articulation boundaries
- Do not encode category identity
- Function as punctuation, not classification

---

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
- Convergence is structural (grammar reaches absorbing state)
- Termination is physical (operator ends session)
- These are independent

### Time-Reversal Symmetry

Grammar is symmetric under time reversal (C391):
- No privileged direction
- Consistent with continuous process (not narrative)
- Supports circulatory/reflux interpretation

### Operator Role

The manuscript provides **structure**; the operator supplies **meaning**:
- Programs assume expert judgment
- No explanations, only instructions
- Designed for practitioners, not novices

**Constraint Substitution (F-BRU-007):** When operations are dangerous (high sensory load), grammar restricts options - reducing the need for active vigilance. When operations are forgiving, grammar permits many options - requiring more discrimination and higher HT density. HT functions as residual vigilance after grammar has constrained the decision space.

### 5-Role Functional System (ICC-Validated, C547-C550)

**Status:** Tier 2 validated. ICC (Intra-Class Correlation) analysis independently confirmed role boundaries, converging on the same taxonomy as the original grammar analysis.

Currier B's 49 classes organize into 5 functional roles:

| Role | Function | Classes | Key Property |
|------|----------|---------|--------------|
| **CC** | Core Control | 4 classes (4.4% of B) | Execution boundaries, line-initial/final |
| **EN** | Energy | 18 classes (31.2% of B) | Medial line concentration (positions 3-6) |
| **FL** | Flow | 4 classes (4.7% of B) | Line-final hierarchy (FL > CC at end) |
| **FQ** | Frequent | 4 classes (12.5% of B) | Common instructions, section S elevation |
| **AX** | Auxiliary | 19 classes (16.6% of B) | PREFIX-switched scaffold layer |

### Line Execution Syntax (C556-C562)

Lines are formal control blocks with **internal positional grammar**:

```
SETUP → WORK → CHECK → CLOSE
```

- ENERGY roles concentrate medially; FLOW roles concentrate at line-final
- `daiin` marks the WORK→CHECK transition (C557)
- `or→aiin` is the strongest role-transition bigram (C561)
- ENERGY and FLOW are anticorrelated across sections (r = -0.89, C551)

**Section Profiles (C552-C555):**

| Section | Signature |
|---------|-----------|
| B | Highest ENERGY concentration |
| H | Highest FLOW, lowest ENERGY |
| C | Balanced ENERGY/FLOW, highest AX density |
| S | Distinctive FQ elevation |

Same grammar everywhere (C124); profiles reflect different operational emphases, not different grammars.

### AUXILIARY Architecture (C563-C572)

AX is not a separate vocabulary — it is a **scaffold MODE** of the shared pipeline vocabulary:

- **Same MIDDLEs** appear as AX or operational depending on PREFIX (C571)
- **98.2%** of AX tokens use PP MIDDLEs — shared pipeline vocabulary (C567)
- AX tokens stratify into 3 positional sub-types: **INIT / MED / FINAL** (C563)
- 19 classes collapse to **≤2 effective behavioral groups** (C572)
- Position is the sole differentiator; transitions uniform, context classifier below random baseline

**What AX Is NOT:**
- Not a separate vocabulary (same MIDDLEs as operational roles)
- Not 19 meaningfully distinct modes (behavioral collapse)
- Not semantic carriers (no material, procedure, or substance encoding)

**Interpretive Bound:**
> These roles implement structural mediation between control primitives and contextual grammar. They do not encode semantics, materials, or procedures.

**Reference:** See BCSC v1.3 for full structural contract; `phases/CLASS_SEMANTIC_VALIDATION/`, `phases/AUXILIARY_STRATIFICATION/`, `phases/AX_FUNCTIONAL_ANATOMY/`, `phases/AX_CLASS_BEHAVIOR/` for evidence.

### Role Internal Anatomy (C573-C602)

**Status:** Tier 2 validated. Five anatomy phases completed 2026-01-26 (EN_ANATOMY, SMALL_ROLE_ANATOMY, FQ_ANATOMY, AX_REVERIFICATION, SUB_ROLE_INTERACTION).

Each role's internal class structure has been characterized. Key findings:

**ENERGY (EN):** 18 classes exhibit **distributional convergence** (C574) — grammatically identical (same positions, REGIME, context) but lexically partitioned by PREFIX family. QO-prefixed classes use 25 MIDDLEs, CHSH-prefixed use 43, with only 8 shared (Jaccard=0.133, C576). EN is 100% pipeline-derived (C575) with 30 exclusive MIDDLEs (C578). Interleaving is content-driven (BIO vs PHARMA), not positional (C577).

**FREQUENT (FQ):** 4 classes form a **3-group structure** (C593): CONNECTOR {9}, PREFIXED_PAIR {13, 14}, CLOSER {23}. Classes 13 and 14 have completely non-overlapping vocabulary (Jaccard=0.000, C594). Internal transitions follow a directed grammar (chi2=111, C595). Class 23 is a boundary specialist (29.8% final rate, C597).

**FLOW (FL):** 4 classes split into **hazard/safe** subgroups (C586). Hazard {7, 30} sits at mean position 0.55 with 12.3% final rate; Safe {38, 40} at position 0.81 with 55.7% final rate (p=9.4e-20). FL initiates forbidden transitions at 4.5x the rate it receives them.

**CORE CONTROL (CC):** 3 active classes form a **positional dichotomy** (C590). Class 10 (daiin) is initial-biased (0.413, 27.1% line-initial); Class 11 (ol) is medial (0.511); Class 17 (ol-derived) adds compound operators. Critically, daiin/ol trigger EN_CHSH specifically (1.6-1.7x) while ol-derived triggers EN_QO (1.39x) — CC sub-groups are **differentiated triggers** (C600).

**Cross-Boundary Routing (C598-C602):** Sub-group identity is visible across role boundaries. 8/10 cross-role pairs show non-random sub-group routing (5 survive Bonferroni, C598). AX scaffolding routes differentially: AX_INIT feeds QO, AX_FINAL feeds FQ_CONN (C599). All 19 hazard events originate from exactly 3 sub-groups: FL_HAZ, EN_CHSH, FQ_CONN. QO never participates in hazards (C601). REGIME modulates routing magnitude but not direction for 4/5 pairs; AX->FQ is the REGIME-independent exception (C602).

**Reference:** See constraint files C573-C602; `phases/EN_ANATOMY/`, `phases/SMALL_ROLE_ANATOMY/`, `phases/FQ_ANATOMY/`, `phases/SUB_ROLE_INTERACTION/` for evidence.

---

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
|
+-- Shared with B (404, 39.9%)
    +-- AZC-Mediated (~214, ~21% of A vocabulary)
    |     A->AZC->B constraint propagation
    |
    +-- B-Native Overlap (~190, ~19% of A vocabulary)
          Zero AZC presence, B-dominant frequency
          Execution-layer vocabulary with incidental A appearance
```

**METHODOLOGY NOTE (2026-01-24):** Regenerated with atomic-suffix parser (voynich.py). Uses atomic suffixes only, smart MIDDLE preservation, gallows-initial handling (C528). C498.a substructure estimates await re-verification with new counts.

**Key insight (C498.a):** Only 214 MIDDLEs (19.8% of A vocabulary) genuinely participate in the A->AZC->B pipeline. The 198 B-Native Overlap MIDDLEs appear in both A and B but never in AZC - they are B operational vocabulary with incidental A presence, not pipeline participants.

Registry-internal MIDDLEs encode **within-category fine distinctions** for A-registry navigation that don't propagate to B execution. The morphological signature (ct-prefix, suffix-less, folio-localized) reflects their A-internal scope.

**Note:** 8.9% of A-exclusive MIDDLEs also appear in AZC - this is interface noise from systems sharing the same alphabet, not a distinct vocabulary stratum. Verification testing rejected the "AZC-terminal bifurcation" hypothesis.

### Human-Factors Model (Tier 3)

Currier A is designed for **expert navigation without meaning**:

| Feature | Function |
|---------|----------|
| Closure markers | Visual record bracketing (-y, -n, -m at final position) |
| Working-memory clusters | Attention stabilization (median 2, max 7) |
| Singleton isolation | Deliberate separation points |
| DA articulation | Within-record segmentation |

### A-AZC Interface (Tier 3)

Entry vocabulary composition predicts AZC activation breadth:

| Factor | Effect on Breadth |
|--------|-------------------|
| Hub-dominant | Broader compatibility |
| Tail-dominant | Narrower compatibility |
| Universal vs Tail asymmetry | 0.58 vs 0.31 breadth |

### Special Folio: f49v Instructional Apparatus (C497)

Folio f49v is structurally distinct - it demonstrates Currier A morphology rather than serving as registry content. It contains 26 single-character labels alternating with example lines and marginal ordinal numbers (1-5). This is the only folio where the manuscript "teaches how to read itself." See C497 for details.

### Why Failure-Memory Was Rejected

Initial A-B hazard correlation (rho=0.228, p=0.038) was tested:
- Permutation control: p=0.111 (FAILED)
- Frequency-matched control: p=0.056 (FAILED)
- Pre-registered low-frequency MIDDLE test: p=0.651 (FAIL)

**Conclusion:** Apparent correlation was entirely driven by token frequency. High-frequency tokens appear in complex structures in both systems. When frequency is controlled, no residual signal exists.

**Currier A is complexity-aligned, not risk-encoding.**

### Multiplicity Encoding

**INVALIDATED (2026-01-15):** The "64.1% block repetition" finding (C250) was an artifact of loading all transcribers instead of H (primary) only. With H-only data: **0% block repetition**. The apparent repetition was caused by interleaved transcriber readings.

---

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

| Diagram Position | Workflow Phase | Escape Rate | Meaning |
|------------------|----------------|-------------|---------|
| C | Core/Interior | ~1.4% | Moderate flexibility |
| R1→R2→R3 | Progression | 2.0%→1.2%→0% | Options narrowing, committing |
| S | Boundary/Exit | 0% | Locked, must accept outcome |

*Note: P (Paragraph) is NOT a diagram position - it is Currier A text appearing on AZC folios.*

### Compatibility Grouping Mechanism

AZC folios group vocabulary by **compatibility signature**:
- Specialized A-types appear in only 1-3 folios
- Each PREFIX+MIDDLE appears at exactly one position
- Combinations that don't occur together reflect fixed positional encoding
- AZC does not actively block - it records which combinations exist

**Why AZC is large:** It encodes many distinct position classes. Each folio = a different set of vocabulary grouped by operational character.

### Ambient Constraint Activation

AZC is not selected explicitly. Constraints activate automatically based on vocabulary used:
- **Core vocabulary** (20+ folios) → broadly legal, averaged constraints
- **Specialized vocabulary** (1-3 folios) → activates specific constraint profile
- B procedures touch ALL 34-36 AZC folios because they span the full vocabulary

### Two Families

| Family | Folios | Mean Escape | Context |
|--------|--------|-------------|---------|
| Zodiac | 26 | 2.4% | Routine, predictable, low intervention |
| Non-Zodiac | 10 | 7.6% | Variable, demanding, more intervention |

The distinction encodes **context risk profiles**, not different domains.

### Reachability Suppression Mechanism (v2.56)

AZC constrains B grammar through a **two-tier constraint system**:

**Tier 1 - Universal (Always Active):**
- 49 instruction classes, 17 forbidden transitions
- 9 hazard-involved classes
- Base grammar graph 99.1% connected

**Tier 2 - AZC-Conditioned (Context-Dependent):**
- 77% of MIDDLEs appear in only 1 AZC folio
- Restricted MIDDLEs become unavailable under certain legality fields
- 6 of 9 hazard classes have reduced effective membership

**Hazard Class Taxonomy:**

| Type | Classes | Representatives | AZC Effect |
|------|---------|-----------------|------------|
| **Atomic** | 7, 9, 23 | ar, aiin, dy | Universal enforcement - NOT affected by AZC |
| **Decomposable** | 8, 11, 30, 31, 33, 41 | chedy, ol, dar, chey, qokeey, qo | Context-tunable via MIDDLE availability |

**Mechanism:** AZC does not modify B's grammar; it shortens the reachable language by restricting vocabulary availability. When AZC provides a legality field, decomposable hazard classes lose membership because their MIDDLEs become unavailable. Atomic hazard classes remain fully active regardless of AZC context.

This completes the A→AZC→B control-theoretic explanation with no semantics, branching, or lookup.

**Scope Protection (BCI-2026-01-18):**
> AZC constrains discriminative vocabulary and context-sensitive hazard classes. It **must not** remove execution-infrastructure roles required for grammar connectivity, even when those roles are labeled with MIDDLE-bearing tokens. Infrastructure roles lie outside AZC's legitimate constraint scope because their removal collapses B reachability without violating any vocabulary-level rule.

### Interpretive Bounds

AZC's structure is fully characterized (CLOSED). Semantic content of individual orientation postures remains opaque by design.

---

## IX. HUMAN TRACK (HT) - STATUS & INTERPRETIVE BOUNDS

Human Track tokens form a distinct layer with specific structural properties. Interpretation must respect the tier boundary.

### Core Understanding (v2.13)

> **HT is a scalar signal of required human vigilance that varies with content characteristics, not with codicology, singular hazards, or execution failure modes.**

HT functions as **anticipatory vigilance** - it prepares the human operator for upcoming demands rather than reacting to past events.

### Tier 2 (Structural, Binding)

These findings constrain the model:

- HT is **non-operational** (terminal independence p=0.92)
- HT has **causal decoupling** from program execution (V=0.10)
- HT exhibits **generative structure** (Zipf=0.89)
- HT **avoids hazards entirely** (0/35 forbidden seam presence)
- HT **synchronizes statistically** with preceding grammar phase
- HT removal **does not affect execution** outcomes
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

The Component-to-Class Mapping (CCM) phase achieved complete role-level semantic decomposition of tokens. This is the maximum recoverable internal meaning.

> **REVISION (2026-01-11):** PREFIX interpretation updated from "material-behavior class" to "control-flow participation" based on F-A-014b. See C466-C467.

### Token Decomposition

Every token decomposes as:

```
TOKEN = PREFIX   → operation domain selector (which MIDDLE family is legal)
      + SISTER   → operational mode (precision/tolerance)
      + MIDDLE   → operation type (heating/cooling/monitoring)
      + SUFFIX   → decision archetype (phase-indexed)
```

### Component Mappings (Tier 2-3)

| Component | Encodes | Evidence |
|-----------|---------|----------|
| **PREFIX** | Operation domain selector | C911: 102 forbidden PREFIX+MIDDLE combinations |
| **SISTER** | Operational mode | C412 anticorrelation (rho=-0.326) |
| **MIDDLE** | Operation type (3 families) | C908-C910: kernel/section/REGIME correlation |
| **SUFFIX** | Phase-indexed decision archetype | F-AZC-014 (74% P-position for -ain) |

### PREFIX-MIDDLE Selection (C911 - Tier 2)

PREFIX and MIDDLE are NOT independent. Each PREFIX class selects which MIDDLE family is grammatically legal:

| PREFIX Class | Selects For | Enrichment |
|--------------|-------------|------------|
| **qo-** | k-family (heating) | 4.6-5.5x |
| **ch-/sh-** | e-family (stability) | 2.0-3.1x |
| **da-/sa-** | infrastructure (iin, in, r, l) | 5.9-12.8x |
| **ot-/ol-** | h-family (monitoring) | 3.3-6.8x |

### MIDDLE Semantic Families (C908-C910 - Tier 2)

MIDDLEs encode operation types, not just variant identity:

| Family | MIDDLEs | Function | Section Concentration |
|--------|---------|----------|----------------------|
| **k-family** | k, ke, ck, ek, kch | Heating/energy | B (bathing/balneum) |
| **e-family** | e, ed, eed, eo, eey | Cooling/stability | S (recipes) |
| **h-family** | ch, sh, pch, d | Phase monitoring | T (text/instructions) |

### The Unifying Perspective

> The manuscript encodes the operational worldview of a controlled apparatus, not the descriptive worldview of a human observer.

From the apparatus's perspective:
- PREFIX encodes **which operation domain** is being addressed
- MIDDLE encodes **what operation type** within that domain
- SUFFIX encodes **when decisions are allowed** (phase)
- SISTER encodes **how tightly to execute** (mode)

### Semantic Ceiling

**Recoverable (role-level):**
- 4 operation domains (PREFIX): energy, stability, monitoring, infrastructure
- 2 operational modes (SISTER): precision, tolerance
- 3 operation type families (MIDDLE): k-heating, e-cooling, h-monitoring
- 12 decision archetypes (SUFFIX): phase-indexed

**Irrecoverable (entity-level):**
- Specific substances, plants, devices
- Specific procedures or recipes
- Token-to-real-world mappings

This boundary is structural, not analytical. The system was designed to operate without external referents.

See [SPECULATIVE/apparatus_centric_semantics.md](SPECULATIVE/apparatus_centric_semantics.md) for full analysis.

---

## X.C. REPRESENTATION PRINCIPLE (Pipeline Resolution)

Operational conditions (temperature, pressure, material state, etc.) are NOT encoded as values or ranges. Instead, legality of vocabulary tokens presupposes suitable external conditions; illegal combinations are structurally disallowed.

### Key Evidence

| Finding | Evidence |
|---------|----------|
| MIDDLE length inversely correlates with coverage | len=1: 18.4 folios; len=5: 1.2 folios |
| Most MIDDLEs are single-folio | 73.5% appear in only 1 AZC folio |
| No scalar encoding anywhere | C287-C290 (rejected ratio hypothesis) |
| Constraint transfer is causal | 28x escape rate difference AZC->B (F-AZC-016) |

### Interpretation

> **Physics exists externally; representation is categorical.**

The manuscript does not encode "temperature = high" or "pressure = 3 of 4". It encodes which vocabulary combinations are legal, and legality presupposes appropriate external conditions.

This resolves the apparent complexity paradox: the system seems over-specified for "just distillation" because it enumerates ~2,400 distinct vocabulary combinations, each legal only under specific (externally determined) conditions. The operator's trained judgment maps external reality to vocabulary selection; the manuscript enforces compatibility rules on those selections.

### Pipeline Closure

The A -> AZC -> B control pipeline is now **structurally and behaviorally validated**:
- F-AZC-015: AZC is ambient (70% active per window), not dynamic
- F-AZC-016: Constraint profiles transfer causally (28x escape difference)
- C468-C470: Structural facts locked as Tier 2

**Do NOT reopen:** entry-level A-B mapping, dynamic AZC hypothesis, parametric encoding, semantic token meaning.

### Pipeline Legality Model (Strict Interpretation)

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

The following interpretations are **plausible but do not constrain the model**:

### Process Domain

- **Reflux distillation** (circulatory alembic) - uniquely compatible with grammar (100%)
- **Perfumery/botanical extraction** - favored by 8/8 diagnostic tests
- **Hybrid hazard model** - 71% batch, 29% apparatus failure modes

### Institutional Context

- **Guild workshop** - expert-oriented, no novice accommodation
- **Master-practitioner reference** - assumes trained judgment
- **Working manual** - not teaching text

### Historical Plausibility

- Medieval/early modern craft practice
- European workshop tradition
- Pre-modern process control

**These do not constrain the model.** They provide interpretive context only.

### XII.A. Physical World Reverse Engineering (Tier 3)

Six investigation phases tested the physical grounding of the control architecture:

| Phase | Question | Result |
|-------|----------|--------|
| **PWRE-1** | What plant class is admissible? | Circulatory thermal (12 exclusions) |
| **FM-PHY-1** | Is hazard distribution natural? | YES - diagnostic for reflux |
| **SSD-PHY-1a** | Is dimensionality physics-forced? | YES - D ≥ 50 required |
| **OJLM-1** | What must operators supply? | 13 judgment types |
| **APP-1** | Which apparatus exhibits this behavioral profile? | Pelican (4/4 axes match) |
| **MAT-PHY-1** | Does A's topology match botanical chemistry? | YES (5/5 tests pass) |

**Key Findings:**

1. **Hazard distribution is DIAGNOSTIC** — The 41/24/24/6/6 profile matches circulatory reflux distillation and *excludes* batch distillation and chemical synthesis.

2. **Dimensionality is physics-forced** — The ~128-dimensional MIDDLE space is not a notation choice. Low-dimensional spaces (≤20 axes) mathematically cannot satisfy the observed sparsity, clustering, and navigability constraints.

3. **13 judgment types deliberately omitted** — The controller acknowledges its limits by NOT encoding what cannot be written: sensory calibration, equipment feel, timing intuition, trouble recognition, and 9 others.

4. **Pelican behavioral isomorphism** — The circulatory reflux apparatus (pelican) is the only surveyed apparatus class exhibiting the same responsibility split, failure fears, judgment requirements, and state complexity across all 4 axes.

5. **Material topology match** — Currier A's incompatibility structure (~95%, 5-7 hubs, clustering, hub rationing, Zipf frequency) matches what real pre-instrumental botanical chemistry forces on any registry tracking distinct materials.

**Combined Arc:**
> The Voynich Manuscript controls a circulatory thermal plant whose hazard profile matches distillation physics, whose discrimination space is forced by the physical state-space, whose operation REQUIRES human judgment for 13 structurally distinct types of non-codifiable knowledge, whose behavioral profile is isomorphic to the historical pelican apparatus, and whose registry topology matches the constraints that real botanical chemistry imposes.

**Files:** `phases/FM_PHY_1_failure_mode_alignment/`, `phases/SSD_PHY_1a/`, `phases/OJLM_1_operator_judgment/`, `phases/APP_1_apparatus_validation/`, `phases/MAT_PHY_1_material_topology/`

See [SPECULATIVE/INTERPRETATION_SUMMARY.md](SPECULATIVE/INTERPRETATION_SUMMARY.md) Section I.O for full details.

---

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

The A→AZC→B control architecture is formally closed via four structural contracts:

| Contract | File | Status | Function |
|----------|------|--------|----------|
| CASC | `currierA.casc.yaml` | LOCKED v1.0 | Currier A registry structure |
| AZC-ACT | `azc_activation.act.yaml` | LOCKED v1.0 | A→AZC transformation |
| AZC-B-ACT | `azc_b_activation.act.yaml` | LOCKED v1.0 | AZC→B propagation |
| BCSC | `currierB.bcsc.yaml` | LOCKED v1.2 | Currier B internal grammar |

Each contract is derived from Tier 0-2 constraints and introduces no new claims. Constraints remain authoritative.

**Pipeline completion:** As of 2026-01-13, the A→AZC→B control architecture is fully reconstructed at Tier 0-2. All remaining work concerns interpretation, tooling, or external corroboration.

**PCA-v1 CERTIFIED:** Pipeline Closure Audit passed all 6 tests (legality consistency, no back-propagation, parametric silence, semantic vacuum, A/B isolation, HT non-interference). The contracts compose cleanly without hidden coupling.

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

**Source:** `context/CONSTRAINT_TABLE.txt`

CONSTRAINT_REFERENCE v2.6 | 794 constraints | 2026-02-05
TIER: 0=frozen 1=falsified 2=established 3=speculative 4=exploratory
SCOPE: A=CurrierA B=CurrierB AZC=diagrams HT=HumanTrack GLOBAL=cross-system
LOCATION: ->=individual_file in:=grouped_registry

NUM	CONSTRAINT	TIER	SCOPE	LOCATION
C001	A | **INVALIDATED** - depend on C250 |	266	~~Block vs non-block entry types~~	1
C074	Dominant convergence to stable states (57.8% STATE-C terminal)	0	B	-> C074_dominant_convergence.md
C079	Only STATE-C essential	0	B	in: tier0_core
C084	System targets MONOSTATE (42.2% end in transitional)	0	B	in: tier0_core
C085	10 single-character primitives (s,e,t,d,l,o,h,c,k,r)	0	B	in: tier0_core
C089	Core within core: k, h, e	0	B	in: tier0_core
C090	500+ 4-cycles, 56 3-cycles (topological)	2	B	in: grammar_system
C103	k = ENERGY_MODULATOR	2	B	in: grammar_system
C104	h = PHASE_MANAGER	2	B	in: grammar_system
C105	e = STABILITY_ANCHOR (54.7% recovery paths)	2	B	in: grammar_system
C107	All kernel nodes BOUNDARY_ADJACENT to forbidden	2	B	in: grammar_system
C109	5 failure classes (PHASE_ORDERING dominant 41%)	2	B	-> C109_hazard_classes.md
C110	PHASE_ORDERING 7/17 = 41%	2	B	in: grammar_system
C111	65% asymmetric	2	B	in: grammar_system
C112	59% distant from kernel	2	B	in: grammar_system
C115	0 non-executable tokens	0	B	in: tier0_core
C119	0 translation-eligible zones	0	B	in: tier0_core
C120	PURE_OPERATIONAL verdict	0	B	in: tier0_core
C121	49 instruction equivalence classes (9.8x compression)	0	B	-> C121_49_instruction_classes.md
C124	100% grammar coverage	0	B	-> C124_grammar_coverage.md
C126	0 contradictions across 8 families	2	B	in: grammar_system
C129	Family differences = coverage artifacts	2	B	in: grammar_system
C130	DSL hypothesis rejected (0.19% reference rate)	1	B	-> CORE/falsifications
C131	Role consistency LOW (23.8%)	2	B	in: grammar_system
C132	Language encoding CLOSED	1	B	-> CORE/falsifications
C137	Swap invariance confirmed (p=1.0)	1	B	-> CORE/falsifications
C138	Illustrations do not constrain execution	1	B	-> CORE/falsifications
C139	Grammar recovered from text-only	2	B	in: grammar_system
C140	Illustrations are epiphenomenal	1	B	-> CORE/falsifications
C141	Cross-family transplant = ZERO degradation	2	B	in: grammar_system
C144	Families are emergent regularities	2	B	in: grammar_system
C153	Prefix/suffix axes partially independent (MI=0.075)	2	B	in: organization
C154	Extreme local continuity (d=17.5)	2	B	in: organization
C155	Piecewise-sequential geometry (PC1 rho=-0.624)	2	B	in: organization
C156	Detected sections match codicology (4.3x quire alignment)	2	B	in: organization
C157	Circulatory reflux uniquely compatible (100%)	3	B	-> SPECULATIVE/
C158	Extended runs necessary (12.6% envelope gap)	2	B	in: organization
C159	Section boundaries organizational (F-ratio 0.37)	2	B	in: organization
C160	Variants are discrete alternatives (43%)	2	B	in: organization
C161	Folio Ordering = Risk Gradient	2	B	in: organization
C162	Aggressive programs buffered (88% vs 49% null)	2	B	in: organization
C163	7 domains ruled incompatible	2	B	in: organization
C164	86.7% Perfumery-Aligned Plants	2	B	in: organization
C165	No Program-Morphology Correlation	2	B	in: organization
C166	Uncategorized: zero forbidden seam presence (0/35)	2	HT	in: human_track
C167	Uncategorized: 80.7% section-exclusive	2	HT	in: human_track
C168	Uncategorized: single unified layer	2	HT	in: human_track
C169	Uncategorized: hazard avoidance 4.84 vs 2.5	2	HT	in: human_track
C170	Uncategorized: morphologically distinct (p<0.001)	2	HT	in: human_track
C171	Only continuous closed-loop process control survives	2	B	-> C171_closed_loop_only.md
C172	SUPERSEDED	2	HT	in: human_track
C173	Linguistic hypothesis EXHAUSTED	2	B	in: organization
C174	Intra-role outcome divergence (CF-1=0.62, CF-2=0.34)	2	B	in: organization
C175	3 process classes survive (reflux, extraction, conditioning)	2	B	in: organization
C176	5 product families survive	2	B	in: organization
C177	Both extraction/conditioning survive; extraction favored	2	B	in: organization
C178	83 folios yield 33 operational metrics	2	B	in: operations
C179	4 stable regimes (K-Means k=4, Silhouette=0.23)	2	B	in: operations
C180	All 6 aggressive folios in REGIME_3	2	B	in: operations
C181	3/4 regimes Pareto-efficient; REGIME_3 dominated	2	B	in: operations
C182	Restart-capable = higher stability	2	B	in: operations
C183	No regime dominates all axes	2	B	in: operations
C184	9 pressure-induced transitions; 3 prohibited	2	B	in: operations
C185	REGIME_3 = Transient Throughput	2	B	in: operations
C186	No pressure-free cycles	2	B	in: operations
C187	CEI manifold formalized	2	B	in: operations
C188	CEI bands: R2 < R1 < R4 < R3	2	B	in: operations
C189	CEI bidirectional; down-CEI easier (1.44x)	2	B	in: operations
C190	LINK-CEI r=-0.7057	2	B	in: operations
C191	CEI Smoothing	2	B	in: operations
C192	Restart at Low-CEI	2	B	in: operations
C193	Navigation WORSE than random (d=-7.33)	2	B	in: operations
C194	PARTIAL codex organization (2/5)	2	B	in: operations
C195	Human-track compensation NOT detected	2	B	in: operations
C196	100% match EXPERT_REFERENCE archetype	2	B	in: operations
C197	Designed for experts, not novices	2	B	in: operations
C198	OPS CLOSED	2	B	in: operations
C199	Both mineral AND botanical survive	3	B	in: operations
C200	6 Product Survivors	2	B	in: operations
C201	Guild-Restricted Ecosystem	2	B	in: operations
C202	Goldsmith/Assayer Workshops Survive	2	B	in: operations
C203	Voynich structurally exceptional	2	B	in: operations
C204	OPS-R RESOLVED by SEL-F (definitional ambiguity, not formal contradiction)	2	B	in: operations
C205	Residue 82% section-exclusive	2	B	in: operations
C206	Sections not compressible to regimes	2	B	in: operations
C207	0/18 micro-cipher tests passed	2	B	in: operations
C208	Residue compatible with non-encoding dynamics	2	B	in: operations
C209	Attentional pacing wins (6/8)	2	HT	in: human_track
C210	External alignments robust to HT removal	2	B	in: operations
C211	Seasonal ordering underpowered	2	B	in: operations
C212	93% plants peak May-August	2	B	in: operations
C213	Opportunity-loss model supported (64.7% premature hazards)	2	B	in: operations
C214	EXT-4 duration criterion INVALIDATED	2	B	in: operations
C215	BOTANICAL_FAVORED (8/8 tests, ratio 2.37)	3	B	in: operations
C216	Hybrid hazard model (71% batch, 29% apparatus)	2	B	in: operations
C217	0 true HT near hazards	2	HT	in: human_track
C221	Deliberate skill practice (4/5) - NOT random mark-making	2	HT	in: operations
C222	No intentional layout function	2	B	in: operations
C223	Procedural fluency MIXED	2	B	in: operations
C224	A coverage = 13.6% (threshold 70%)	2	A	in: currier_a
C225	A Transition Validity = 2.1%	2	A	in: currier_a
C226	A Has 5 Forbidden Violations	2	A	in: currier_a
C227	A LINK Density = 3.0%	2	A	in: currier_a
C228	A Density = 0.35x B	2	A	in: currier_a
C229	A = DISJOINT	2	A	-> C229_currier_a_disjoint.md
C230	A Silhouette = 0.049	2	A	in: currier_a
C231	A is REGULAR but NOT GRAMMATICAL	2	A	in: currier_a
C232	A Section-Conditioned but Class-Uniform	2	A	in: currier_a
C233	A = LINE_ATOMIC	2	A	in: currier_a
C234	A = POSITION_FREE	2	A	in: currier_a
C235	8+ mutually exclusive markers	2	A	in: currier_a
C236	A = FLAT	2	A	in: currier_a
C237	A = DATABASE_LIKE	2	A	in: currier_a
C238	Global Schema, Local Instantiation	2	A	in: currier_a
C239	A/B separation = DESIGNED (0.0% cross)	2	A↔B	in: currier_a
C240	A = NON_SEQUENTIAL_CATEGORICAL_REGISTRY	2	A	-> C240_currier_a_registry.md
C241	daiin A-enriched (1.62x), ol B-enriched (0.24x)	2	A	in: currier_a
C242	daiin neighborhood flip (content in A, grammar in B)	2	A	in: currier_a
C243	daiin-ol adjacent: 16 in B, 10 in A	2	A	in: currier_a
C244	Infrastructure reuse without semantic transfer	2	A	in: currier_a
C245	MINIMAL vocabulary: exactly 2 tokens (daiin, ol)	2	A	in: currier_a
C246	4 mandatory criteria for structural primitives	2	A	in: currier_a
C247	SP-01 (daiin): affects 30.2% A, 16.5% B	2	A	in: currier_a
C248	SP-02 (ol): affects 7.4% A, 17.7% B	2	A	in: currier_a
C249	Scan COMPLETE: 11 candidates tested	2	A	in: currier_a
C250	~~64.1% show repeating blocks~~	1	A	**INVALIDATED** - transcriber artifact
C251	Repetition is Intra-Record Only	2	A	in: currier_a
C252	Repetition Bounded 2-6x	2	A	in: currier_a
C253	All Blocks Unique	2	A	in: currier_a
C254	Multiplicity does NOT interact with B; isolated from operational grammar	2	A	in: currier_a
C255	Blocks 100% Section-Exclusive	2	A	in: currier_a
C256	Markers at block END 60.3% (vs 44% start); marker is trailing tag (CAS-DEEP)	2	A	in: currier_a
C257	72.6% of tokens MARKER-EXCLUSIVE; markers define distinct vocabulary domains (CAS-DEEP)	2	A	in: currier_a
C258	3x Dominance Reflects Human Counting	2	A	in: currier_a
C259	INVERSE COMPLEXITY: higher repetitions have MORE diverse blocks (rho=0.248) (CAS-DEEP)	2	A	in: currier_a
C260	Section vocabulary overlap 9.7% (Jaccard); sections are isolated domains (CAS-DEEP)	2	A	in: currier_a
C261	Token Order Non-Random	2	A	in: currier_a
C262	Low Mutation Across Repetitions	2	A	in: currier_a
C263	Section-specific ceilings: H max=5x, P max=5x, T max=6x (CAS-DEEP-V)	2	A	in: currier_a
C264	Inverse-complexity is BETWEEN-MARKER effect (Simpson's paradox); within-marker rho<0 for all 8 markers (CAS-DEEP-V)	2	A	in: currier_a
C265	1,123 unique marker tokens across 8 classes; 85 core tokens (freq>=10); `daiin` dominates DA (51.7%), `ol` dominates OL (32.3%) (CAS-CAT)	2	A	in: currier_a
C266	Block vs Non-Block Entry Types	2	A	in: currier_a
C267	Tokens are COMPOSITIONAL (PREFIX+MIDDLE+SUFFIX)	2	A→B	-> C267_compositional_morphology.md
C267.a	**MIDDLE Sub-Component Structure** (218 sub-components reconstruct 97.8% of MIDDLEs; morphology extends to sub-MIDDLE level)	2	GLOBAL	in: currier_a
C268	897 observed combinations	2	A→B	in: morphology
C269	7 Universal Suffixes	2	A	in: currier_a
C270	Some middles are PREFIX-EXCLUSIVE (CT:-h-, DA:-i-, QO:-kch-); internal structure within classifier families (CAS-MORPH)	2	A	in: currier_a
C271	Compositional structure explains low TTR and bigram reuse	2	A	in: currier_a
C272	A and B on COMPLETELY DIFFERENT folios	2	A↔B	in: morphology
C273	Section specialization NON-UNIFORM: CT is 85.9% Section H vs OK/OL at 53-55%; at least one prefix is specialized to one product line (EXT-8)	2	A	in: currier_a
C274	Co-occurrence UNIFORM: no prefix pair shows strong association (>1.5x) or avoidance (<0.5x) in compounds; prefixes can combine freely (EXT-8)	2	A	in: currier_a
C275	Suffix-prefix interaction SIGNIFICANT (Chi2 p=2.69e-05): different prefixes have different suffix preferences; EXCLUDES prefixes being processing states (EXT-8)	2	A	in: currier_a
C276	MIDDLE is PREFIX-BOUND	2	A	in: currier_a
C277	SUFFIX is UNIVERSAL	2	A	in: currier_a
C278	Three-axis HIERARCHY (PREFIX→MIDDLE→SUFFIX)	2	A→B	in: morphology
C279	STRONG cross-axis dependencies: all three pairwise interactions p < 10⁻³⁰⁰; axes are HIERARCHICALLY RELATED, not independent dimensions (EXT-8)	2	A	in: currier_a
C280	Section P ANOMALY: suffix -eol is 59.7% Section P (only axis value favoring P); suggests P involves specific output form (EXT-8)	2	A	in: currier_a
C281	Components SHARED across A and B	2	A↔B	in: morphology
C282	Component ENRICHMENT: CT is A-enriched (0.14x), OL/QO are B-enriched (5x/4x); -dy suffix 27x B-enriched, -or 0.45x A-enriched; usage patterns differ dramatically (EXT-8)	2	A	in: currier_a
C283	Suffixes show CONTEXT PREFERENCE: -or (0.67x), -chy (0.61x), -chor (0.18x) A-enriched; -edy (191x!), -dy (4.6x), -ar (3.2x) B-enriched; -ol, -aiin BALANCED (EXT-9)	2	A	in: currier_a
C284	CT in B is CONCENTRATED in specific folios (48 folios); when CT appears in B it uses B-suffixes (-edy, -dy); registry materials take operational form in procedures (EXT-9)	2	A	in: currier_a
C285	161 BALANCED tokens (0.5x-2x ratio) serve as shared vocabulary; DA-family dominates; cross-reference points between A and B (EXT-9)	2	A	in: currier_a
C286	Modal preference is PREFIX x SUFFIX dependent; CT consistently A-enriched across suffixes, OL consistently B-enriched; not simple suffix-determines-context (EXT-9)	2	A	in: currier_a
C287	Repetition does NOT encode abstract quantity, proportion, or scale; remains LITERAL ENUMERATION without arithmetic semantics (EXT-9B RETRACTION)	2	A	in: currier_a
C288	3x dominance (55%) reflects human counting bias and registry ergonomics, NOT proportional tiers; no cross-entry comparison mechanism exists (EXT-9B RETRACTION)	2	A	in: currier_a
C289	Folio-level uniformity reflects ENUMERATION DEPTH PREFERENCE (scribal convention, category density), NOT batch scale; no reference frame for ratios (EXT-9B RETRACTION)	2	A	in: currier_a
C290	Same composition with different counts confirms count is INSTANCE MULTIPLICITY, not magnitude; "3x here" is not comparable to "3x there" due to section isolation (EXT-9B RETRACTION)	2	A	in: currier_a
C291	~20% have optional ARTICULATOR forms	2	A	in: morphology
C292	Articulators = ZERO unique identity distinctions	2	A	in: morphology
C293	Component essentiality hierarchy: MIDDLE (402 distinctions) > SUFFIX (13) > ARTICULATOR (0); PREFIX provides foundation (1387 base); MIDDLE is primary discriminator (CAS-POST)	2	A	in: currier_a
C294	Articulator density INVERSELY correlates with prefix count (15% at 0-1 prefix to 4% at 6 prefixes); articulators COMPENSATE for low complexity (CAS-POST)	2	A	in: currier_a
C295	Sections exhibit DISTINCT configurations: H=dense mixed (87% mixed, 8.2% art), P=balanced (48% exclusive, 5.1% art), T=uniform sparse (81% uniform, 2.57x mean rep) (CAS-POST)	2	A	in: currier_a
C296	CH appears in nearly all common prefix pairs (CH+DA, CH+QO, CH+SH); functions as UNIVERSAL MIXING ANCHOR (CAS-POST)	2	A	in: currier_a
C297	-eol is ONLY suffix concentrated in section P (55.9% vs 41.3% H); all other suffixes favor H; P has distinct suffix profile (CAS-POST)	2	A	in: currier_a
C298	L-compound middle patterns (lch-, lk-, lsh-) function as B-specific grammatical operators; 30-135x more common in B, largely absent from A; grammar-level specialization not covered by shared component inventory (B-MORPH)	2	A	in: currier_a
C299	Section H vocabulary dominates B procedures (76/83 = 91.6%); Section P rare (7/83 = 8.4%); Section T absent (0/83 = 0%); chi² = 127.54, p < 0.0001; A sections have NON-UNIFORM mapping to B procedure applicability (CAS-XREF)	2	A	in: currier_a
C300	3,299 tokens (8.7%) unclassified by Currier	2	AZC	in: azc_system
C301	AZC is HYBRID (B=69.7%, A=65.4%)	2	AZC	-> C301_azc_hybrid.md
C302	Distinct Line Structure	2	AZC	in: azc_system
C303	Elevated LINK Density	2	AZC	in: azc_system
C304	27.4% Unique Vocabulary	2	AZC	in: azc_system
C305	LABELING Signature	2	AZC	in: azc_system
C306	Placement-coding axis established	2	AZC	in: azc_system
C307	Placement × Morphology Dependency	2	AZC	in: azc_system
C308	Ordered Subscripts	2	AZC	in: azc_system
C309	Grammar-Like Placement Transitions	2	AZC	in: azc_system
C310	Placement Constrains Repetition	2	AZC	in: azc_system
C311	Positional Grammar	2	AZC	in: azc_system
C312	Section × Placement Strong	2	AZC	in: azc_system
C313	Position constrains LEGALITY not PREDICTION	2	AZC	in: azc_system
C314	Global Illegality + Local Exceptions	2	AZC	in: azc_system
C315	Placement-Locked Operators	2	AZC	in: azc_system
C316	Phase-Locked Binding	2	AZC	in: azc_system
C317	Hybrid architecture (topological + positional)	2	AZC	in: azc_system
C318	Folio-Specific Profiles	2	AZC	in: azc_system
C319	Zodiac Template Reuse	2	AZC	in: azc_system
C320	S2 < S1 Ordering	2	AZC	in: azc_system
C321	Zodiac Vocabulary Isolated	2	AZC	in: azc_system
C322	SEASON-GATED WORKFLOW interpretation	2	AZC	in: azc_system
C323	57.8% STATE-C terminal	2	B	in: grammar_system
C324	Section-Dependent Terminals	2	B	in: organization
C325	Completion Gradient	2	B	in: organization
C326	A-reference sharing within clusters: 1.31x enrichment (p<0.000001); material conditioning is real but SOFT and OVERLAPPING (silhouette=0.018); NOT a clean taxonomy (SEL-F, Tier 2)	2	AZC	in: azc_system
C327	Cluster 3 (f75-f84) is locally anomalous: only contiguous cluster, 70% STATE-C, highest A-ref coherence (0.294); LOCAL observation, not organizational law (SEL-F, Tier 2)	2	AZC	in: azc_system
C328	10% corruption = 3.3% entropy increase	2	B	in: grammar_system
C329	Top 10 token removal = 0.8% entropy change	2	B	in: grammar_system
C330	Leave-one-folio-out = max 0.25% change	2	B	in: grammar_system
C331	49-class minimality WEAKENED but confirmed	2	B	in: grammar_system
C332	Kernel Bigram Ordering	2	B	in: organization
C333	Kernel Trigram Dominance	2	B	in: organization
C334	LINK Section Conditioning	2	B	in: organization
C335	69.8% Vocabulary Integration	2	B	in: organization
C336	Hybrid A-Access Pattern	2	B	in: organization
C337	Mixed-Marker Dominance	2	B	in: organization
C338	Marker Independence	2	B	in: organization
C339	E-Class Dominance	2	B	in: organization
C340	LINK-Escalation Complementarity	2	B	in: organization
C341	HT-Program Stratification	2	HT	in: human_track
C342	HT-LINK Decoupling	2	HT	in: human_track
C343	A-AZC persistence independence: A-vocabulary tokens appear in 2.2x more AZC placements than AZC-only tokens (p < 0.0001); high-multiplicity A-tokens have 43% broader coverage (p = 0.001); A-registry assets persist independently of AZC legality windows; supports managed stewardship model (AAZ, Tier 2)	2	B	in: organization
C344	HT-A Inverse Coupling	2	HT	in: human_track
C345	A folios lack thematic coherence	2	A	in: currier_a
C346	A exhibits SEQUENTIAL COHERENCE	2	A	in: currier_a
C347	Disjoint Prefix Vocabulary	2	HT	in: human_track
C348	Phase Synchrony	2	HT	in: human_track
C349	Extended Cluster Prefixes	2	GLOBAL	in: morphology
C350	HT+B Hybrids Explained	2	GLOBAL	in: morphology
C351	Final Classification	2	GLOBAL	in: morphology
C352	TRUE ORPHAN Residue	2	GLOBAL	in: morphology
C353	State Continuity Better Than Random	2	B	in: organization
C354	HT Orientation Intact	2	B	in: organization
C355	75.9% Known Prefixes at Folio Start	2	B	in: organization
C356	Section Symmetry Preserved	2	B	in: organization
C357	Lines 3.3x more regular than random	2	B	-> C357_lines_chunked.md
C358	Specific boundary tokens identified	2	B	in: organization
C359	LINK Suppressed at Boundaries	2	B	in: organization
C360	Grammar is LINE-INVARIANT	2	B	in: grammar_system
C361	Adjacent B folios share 1.30x more vocabulary	2	GLOBAL	in: organization
C362	Regime Vocabulary Fingerprints	2	GLOBAL	in: morphology
C363	Vocabulary Independent of Profiles	2	GLOBAL	in: morphology
C364	Hub-Peripheral Structure	2	GLOBAL	in: morphology
C365	LINK tokens are SPATIALLY UNIFORM within folios and lines: no positional clustering (p=0.005), run lengths match random (z=0.14), line-position uniform (p=0.80); LINK has no positional marking function (LDF, Tier 2)	2	GLOBAL	in: morphology
C366	LINK marks GRAMMAR STATE TRANSITIONS: preceded by AUXILIARY (1.50x), FLOW_OPERATOR (1.30x); followed by HIGH_IMPACT (2.70x), ENERGY_OPERATOR (1.15x); p<10^-18; LINK is boundary between monitoring and intervention phases (LDF, Tier 2)	2	GLOBAL	in: morphology
C367	Sections are QUIRE-ALIGNED (4.3x)	2	B	in: organization
C368	Regime Clustering in Quires	2	B	in: organization
C369	Quire Vocabulary Continuity	2	B	in: organization
C370	Quire Boundaries = Discontinuities	2	B	in: organization
C371	Prefixes have POSITIONAL GRAMMAR	2	GLOBAL	in: morphology
C372	Kernel dichotomy (100% vs <5%)	2	GLOBAL	in: morphology
C373	LINK affinity patterns	2	GLOBAL	in: morphology
C374	Section Preferences	2	GLOBAL	in: morphology
C375	Suffixes have POSITIONAL GRAMMAR	2	GLOBAL	in: morphology
C376	Suffix Kernel Dichotomy	2	GLOBAL	in: morphology
C377	KERNEL-LIGHT Suffixes LINK-Attracted	2	GLOBAL	in: morphology
C378	Prefix-Suffix Constrained	2	GLOBAL	in: morphology
C379	Vocabulary Varies by Context	2	GLOBAL	in: morphology
C380	Function is INVARIANT	2	GLOBAL	in: morphology
C381	Instruction Concentration	2	GLOBAL	in: morphology
C382	MORPHOLOGY ENCODES CONTROL PHASE	2	GLOBAL	-> C382_morphology_control_phase.md
C383	GLOBAL MORPHOLOGICAL TYPE SYSTEM	2	GLOBAL	-> C383_global_type_system.md
C384	NO TOKEN-LEVEL OR CONTEXT-FREE A-B LOOKUP	2	A↔B	-> C384_no_entry_coupling.md
C384.a	CONDITIONAL RECORD-LEVEL CORRESPONDENCE PERMITTED	2	A↔B	-> C384a_conditional_correspondence.md
C385	STRUCTURAL GRADIENT in Currier A	2	A	in: currier_a
C386	Transition Suppression	2	GLOBAL	in: morphology
C387	QO as Phase-Transition Hub	2	GLOBAL	in: morphology
C388	Self-Transition Enrichment	2	GLOBAL	in: morphology
C389	BIGRAM-DOMINANT local determinism (H=0.41 bits)	2	GLOBAL	in: grammar_system
C390	No Recurring N-Grams	2	GLOBAL	in: morphology
C391	CONDITIONAL ENTROPY SYMMETRY (H(X|past)=H(X|future); constraint symmetry, not transition symmetry - see C886)	2	GLOBAL	in: grammar_system
C392	ROLE-LEVEL CAPACITY (97.2% observed)	2	GLOBAL	in: grammar_system
C393	FLAT TOPOLOGY (diameter=1)	2	GLOBAL	in: grammar_system
C394	INTENSITY-ROLE DIFFERENTIATION	2	GLOBAL	in: operations
C395	DUAL CONTROL STRATEGY	2	GLOBAL	in: operations
C396	AUXILIARY Invariance	2	GLOBAL	in: morphology
C397	qo-prefix = escape route (25-47%)	2	GLOBAL	in: grammar_system
C398	Post-Source Role Distribution (REVISED)	2	GLOBAL	in: morphology
C399	Safe Precedence Pattern	2	GLOBAL	in: morphology
C400	BOUNDARY HAZARD DEPLETION (5-7x)	2	GLOBAL	in: grammar_system
C401	Self-Transition Dominance	2	GLOBAL	in: morphology
C402	HIGH_IMPACT Clustering	2	GLOBAL	in: morphology
C403	5 PROGRAM ARCHETYPES (continuum)	2	B	in: operations
C404	HT TERMINAL INDEPENDENCE (p=0.92)	2	HT	-> C404_ht_non_operational.md
C405	HT CAUSAL DECOUPLING (V=0.10)	2	HT	in: human_track
C406	HT GENERATIVE STRUCTURE (Zipf=0.89)	2	HT	in: human_track
C407	DA = INFRASTRUCTURE	2	GLOBAL	in: morphology
C408	ch-sh/ok-ot form EQUIVALENCE CLASSES	2	GLOBAL	-> C408_sister_pairs.md
C409	Sister pairs MUTUALLY EXCLUSIVE but substitutable	2	GLOBAL	in: morphology
C410	Sister choice is SECTION-CONDITIONED	2	GLOBAL	in: morphology
C411	Grammar DELIBERATELY OVER-SPECIFIED (~40% reducible)	2	GLOBAL	-> C411_over_specification.md
C412	ch-preference anticorrelated with qo-escape density (rho=-0.33)	2	GLOBAL	-> C412_sister_escape_anticorrelation.md
C413	HT prefix phase-class predicted by preceding grammar (V=0.319)	2	HT	-> C413_ht_grammar_trigger.md
C414	HT STRONG GRAMMAR ASSOCIATION (chi2=934)	2	HT	in: human_track
C415	HT NON-PREDICTIVITY (MAE worsens)	1	HT	in: human_track
C416	HT DIRECTIONAL ASYMMETRY (V=0.324 vs 0.202)	2	HT	in: human_track
C417	HT MODULAR ADDITIVE (no synergy, p=1.0)	2	HT	in: human_track
C418	HT POSITIONAL WITHOUT INFORMATIVENESS	2	HT	in: human_track
C419	HT POSITIONAL SPECIALIZATION IN A (entry-aligned)	2	A+HT	in: human_track
C420	Folio-initial position permits otherwise illegal C+vowel variants (ko-, po-, to-)	2	A	-> C420_folio_initial_exception.md
C421	Section-boundary adjacency suppression (2.42x)	2	A	in: currier_a
C422	DA as internal articulation punctuation (75% separation)	2	A	in: currier_a
C423	PREFIX-BOUND VOCABULARY DOMAINS (80% exclusive MIDDLEs)	2	A	in: currier_a
C424	Adjacency coherence is clustered, not uniform (~3-entry runs, autocorr r=0.80)	2	A	-> C424_clustered_adjacency.md
C430	**AZC Bifurcation: two folio families**	2	AZC	in: azc_system
C431	**Zodiac Family Coherence (refines C319)**	2	AZC	in: azc_system
C432	**Ordered Subscript Exclusivity**	2	AZC	in: azc_system
C433	**Zodiac Block Grammar (98%+ self-transition)**	2	AZC	in: azc_system
C434	**R-Series Strict Forward Ordering**	2	AZC	in: azc_system
C435	**S/R Positional Division (boundary/interior)**	2	AZC	in: azc_system
C436	**Dual Rigidity: uniform vs varied scaffolds**	2	AZC	in: azc_system
C437	AZC Folios Maximally Orthogonal	2	AZC	in: azc_system
C438	AZC Practically Complete Basis	2	AZC	in: azc_system
C439	Folio-Specific HT Profiles	2	AZC	in: azc_system
C440	Uniform B-to-AZC Sourcing	2	AZC	in: azc_system
C441	Vocabulary-Activated Constraints	2	AZC	in: azc_system
C442	AZC Compatibility Grouping	2	AZC	in: azc_system
C443	Positional Escape Gradient	2	AZC	in: azc_system
C444	A-Type Position Distribution	2	AZC	in: azc_system
C450	HT Quire Clustering (H=47.20, p<0.0001, eta-sq=0.150)	2	HT/GLOBAL	-> C450_ht_quire_clustering.md
C451	HT System Stratification (A > AZC > B density)	2	HT/GLOBAL	-> C451_ht_system_stratification.md
C452	HT Unified Prefix Vocabulary (Jaccard >= 0.947)	2	HT/GLOBAL	-> C452_ht_unified_vocabulary.md
C453	HT Adjacency Clustering (1.69x enrichment, stronger than C424)	2	HT/GLOBAL	-> C453_ht_adjacency_clustering.md
C454	**AZC-B Adjacency Coupling FALSIFIED** (no p<0.01 at any window)	1	AZC/B	-> C454_azc_b_adjacency_falsified.md
C455	**AZC Simple Cycle Topology FALSIFIED** (cycle_rank=5, CV=0.817)	1	AZC	-> C455_azc_simple_cycle_falsified.md
C456	**AZC Interleaved Spiral Topology** (R-S-R-S alternation)	2	AZC	-> C456_azc_interleaved_spiral.md
C457	**HT Boundary Preference in Zodiac AZC** (S=39.7% > R=29.5%, V=0.105)	2	HT/AZC	-> C457_ht_boundary_preference.md
C458	**Execution Design Clamp vs Recovery Freedom** (CV 0.04-0.11 vs 0.72-0.82)	2	B	-> C458_execution_design_clamp.md
C459	**HT Anticipatory Compensation** (quire r=0.343, p=0.0015, HT precedes stress)	2	HT/B	-> C459_ht_anticipatory_compensation.md
C460	AZC Entry Orientation Effect (step-change p<0.002, decay R^2>0.86)	2	HT/AZC	-> C460_azc_entry_orientation.md
C461	HT density correlates with MIDDLE rarity (Tail 1.58x, chi2=180.56)	3	A→B	-> C461_ht_middle_rarity.md
C462	Universal MIDDLEs are mode-balanced (51% vs 87% precision, chi2=471.55)	3	A→B	-> C462_universal_mode_balance.md
C466	PREFIX Encodes Control-Flow Participation	2	GLOBAL	in: morphology
C467	qo-Prefix is Kernel-Adjacent	2	GLOBAL	in: morphology
C468	AZC Legality Inheritance	2	AZC	in: azc_system
C469	Categorical Resolution Principle	2	AZC	in: azc_system
C470	MIDDLE Restriction Inheritance	2	AZC	in: azc_system
C471	PREFIX Encodes AZC Family Affinity	2	AZC	in: azc_system
C472	MIDDLE Is Primary Carrier of AZC Folio Specificity	2	AZC	in: azc_system
C473	Currier A Entry Defines a Constraint Bundle	2	AZC	in: azc_system
C475	MIDDLE ATOMIC INCOMPATIBILITY	2	A	in: currier_a
C476	COVERAGE OPTIMALITY	2	A	in: currier_a
C477	**HT Tail Correlation** (r=0.504, p=0.0045, R²=0.28)	2	HT/A	-> C477_ht_tail_correlation.md
C478	TEMPORAL COVERAGE SCHEDULING	2	A	in: currier_a
C479	**Survivor-Set Discrimination Scaling** (partial rho=0.395, p<10^-29)	2	A+AZC+HT	-> C479_survivor_discrimination_scaling.md
C480	Constrained Execution Variability (rho=0.306, p=0.078, PROVISIONAL)	3	A→B	-> C480_constrained_variability.md
C481	**Survivor-Set Uniqueness** (0 collisions in 1575 lines)	2	A+AZC	-> C481_survivor_set_uniqueness.md
C482	**Compound Input Specification** (B invariant to A line length, p=1.0)	2	A→B	-> C482_compound_input_specification.md
C483	**Ordinal Repetition Invariance** (magnitude has no downstream effect)	2	A	-> C483_ordinal_repetition_invariance.md
C484	**A Channel Bifurcation** (registry entries + control operators, p<0.01)	2	A	-> C484_a_channel_bifurcation.md
C485	**Grammar Minimality** (e-operator and h->k suppression are load-bearing)	2	B	-> C485_grammar_minimality.md
C486	Bidirectional Constraint Coherence (B behavior constrains A zone inference)	3	CROSS_SYSTEM	-> C486_bidirectional_constraints.md
C487	A-Registry Memory Optimization (z=-97 vs random, 0th percentile)	3	A	-> C487_memory_optimization.md
C488	HT Predicts Strategy Viability (r=0.46 CAUTIOUS, r=-0.48 OPPORTUNISTIC)	3	HT	-> C488_ht_strategy_prediction.md
C489	HT Zone Diversity Correlation (r=0.24, p=0.0006)	3	HT	-> C489_ht_zone_diversity.md
C490	**Categorical Strategy Exclusion** (20.5% of programs forbid AGGRESSIVE, not gradient but prohibition)	2	B	-> C490_categorical_strategy_exclusion.md
C491	Judgment-Critical Program Axis (OPPORTUNISTIC orthogonal to caution/aggression)	3	B	in: SPECULATIVE
C492	**PREFIX Phase-Exclusive Legality** (ct PREFIX is 0% C/S-zones, 26% P-zone, invariant)	2	A→AZC	-> C492_prefix_phase_exclusion.md
C493	**Brunschwig Grammar Embedding** (balneum marie procedure fits with 0 forbidden violations)	2	B	-> C493_brunschwig_grammar_embedding.md
C494	**REGIME_4 Precision Axis** (encodes precision-constrained execution, not intensity)	2	B	-> C494_regime4_precision_axis.md
C495	**SUFFIX–REGIME Compatibility Breadth** (-r universal, -ar/-or restricted; V=0.159)	2	A→B	in: morphology
C496	**Nymph-Adjacent S-Position Prefix Bias (o-prefix 75%)**	2	AZC	in: azc_system
C497	**f49v Instructional Apparatus Folio** (26 L-labels alternating 1:1 with example lines, demonstrates morphology limits)	2	A	in: currier_a
C498	**Registry-Internal Vocabulary Track** (61.8% A-exclusive MIDDLEs: ct-prefix 5.1×, suffix-less 3×, folio-localized; don't propagate to B)	2	A	in: currier_a
C498.a	**A∩B Shared Vocabulary Bifurcation** (154 AZC-Mediated + 114 B-Native Overlap; pipeline scope narrowed)	2	A	in: currier_a
C498.b	**RI Singleton Population** (~977 singletons, mean 4.82 chars; functional interpretation WEAKENED - see C498.d)	2	A	in: currier_a
C498.c	**RI Repeater Population** (~313 repeaters, mean 3.61 chars; functional interpretation WEAKENED - see C498.d)	2	A	in: currier_a
C498.d	**RI Length-Frequency Correlation** (rho=-0.367, p<10⁻⁴²; singleton rate: 2-char=48%, 6-char=96%; complexity gradient, not functional bifurcation)	2	A	in: currier_a
C499	Bounded Material-Class Recoverability (128 MIDDLEs with P(material_class) vectors; conditional on Brunschwig)	3	A	in: currier_a
C500	Suffix Posture Temporal Pattern (CLOSURE front-loaded 77% Q1, NAKED late 38% Q4, ratio 5.69×)	3	A	in: currier_a
C501	**B-Exclusive MIDDLE Stratification** (569 B-exclusive types: L-compounds 49, boundary closers, 80% singletons; elaboration not novelty)	2	A	in: currier_a
C502	**A-Record Viability Filtering** (Strict interpretation: ~96/480 B tokens legal per A; 13.3% mean B folio coverage; 80% filtered)	2	A+B	in: currier_a
C502.a	**Full Morphological Filtering Cascade** (PREFIX+MIDDLE+SUFFIX: 38 tokens legal (0.8%); MIDDLE 5.3%, +PREFIX 64% reduction, +SUFFIX 50% reduction, combined 85% beyond MIDDLE)	2	A+B	in: currier_a
C503	**Class-Level Filtering** (MIDDLE-only: 1,203 unique patterns, 6 always-survive classes, 32.3 mean; infrastructure classes vulnerable)	2	A+B	in: currier_a
C503.a	**Class Survival Under Full Morphology** (PREFIX+MIDDLE+SUFFIX: 6.8 mean classes (10.8%); 83.7% reduction from MIDDLE-only; ~7 classes = actual instruction budget)	2	A+B	in: currier_a
C503.b	**No Universal Classes Under Full Morphology** (C121's 49 classes: 0 universal; Class 9 highest at 56.1%; C503's "6 unfilterable" = 10-56% coverage; MIDDLE-only claim doesn't hold under full filtering)	2	A+B	in: currier_a
C503.c	**Kernel Character Coverage** (k/h/e are chars within tokens, not standalone; h=95.6%, k=81.1%, e=60.8%; union=97.6%; only 2.4% lack kernel access; kernel nearly universal)	2	A+B	in: currier_a
C504	**MIDDLE Function Bifurcation** (PP 86 types r=0.772 with survival; RI 1,293 types r=-0.046; 75% records have both)	2	A+B	in: currier_a
C505	**PP Profile Differentiation by Material Class** ('te' 16.1×, 'ho' 8.6×, 'ke' 5.1× in animal records; A-registry organization only)	2	A	in: currier_a
C506	**PP Composition Non-Propagation** (PP count r=0.715; composition cosine=0.995 with baseline; capacity not routing)	2	A+B	in: currier_a
C506.a	**Intra-Class Token Configuration** (Same classes, different PP: Jaccard=0.953; ~5% token variation; classes=types, tokens=parameterizations)	2	A+B	in: currier_a
C506.b	**Intra-Class Behavioral Heterogeneity** (Different-MIDDLE tokens: same position p=0.11, different transitions p<0.0001; 73% MIDDLE pairs have JS>0.4)	2	B	in: currier_a
C507	**PP-HT Partial Responsibility Substitution** (rho=-0.294, p=0.0015; PP 0-3 = 18.8% HT vs PP 6+ = 12.6% HT; HT TTR r=+0.40)	2	A+HT	in: currier_a, human_track
C508	**Token-Level Discrimination Primacy** (MIDDLE-only: Class Jaccard=0.391, Token Jaccard=0.700; 27.5% within-class mutual exclusion; fine discrimination at member level, not class level)	2	A→B	in: currier_a
C508.a	**Class-Level Discrimination Under Full Morphology** (REVISION: Full morph Class Jaccard=0.755, Token=0.961; 27% class mutual exclusion; "WHICH" now matters, not just "HOW MANY")	2	A→B	in: currier_a
C509	**PP/RI Dimensional Separability** (72 PP sets shared by records with different RI; 229 records (14.5%) share PP; 26 pure-RI, 399 pure-PP; dimensions orthogonal)	2	A	in: currier_a
C509.a	**RI Morphological Divergence** (RI: 58.5% PREFIX, 3.96-char MIDDLE; PP: 85.4% PREFIX, 1.46-char MIDDLE; RI is MIDDLE-centric, PP is template-balanced)	2	A	in: currier_a
C509.b	**PREFIX-Class Determinism** (Class P_xxx requires A-PREFIX 'xxx' with 100% necessity; sufficiency 72-100%; 27% mutual exclusion = PREFIX sparsity)	2	A→B	in: currier_a
C509.c	**No Universal Instruction Set** (0 classes in ALL records; BARE highest at 96.8%; 50 records lack BARE-compatible MIDDLEs; ~7 classes = ~2.5 PREFIXes + BARE + SUFFIXes)	2	A→B	in: currier_a
C509.d	**Independent Morphological Filtering** (PREFIX/MIDDLE/SUFFIX filter independently; 27% class ME = morphological sparsity not class interaction; SUFFIX classes 100% PREFIX-free)	2	A→B	in: currier_a
C510	**Positional Sub-Component Grammar** (41.2% constrained: 62 START, 14 END, 110 FREE; z=34.16, p<0.0001; grammar is permissive)	2	A	in: currier_a
C511	**Derivational Productivity** (Repeater MIDDLEs seed singletons at 12.67x above chance; 89.8% exceed baseline)	2	A	in: currier_a
C512	**PP/RI Stylistic Bifurcation** (100% containment but z=1.11 vs null - NOT significant; 8.3x section-invariance; composition PROVISIONAL)	2	GLOBAL	in: currier_a
C512.a	**Positional Asymmetry** (END-class 71.4% PP; START-class 16.1% PP; pattern: RI-START + PP-FREE + PP-END)	2	A	in: currier_a
C513	**Short Singleton Sampling Variance** (Jaccard=1.00 vs repeaters; singleton status at ≤3 chars is sampling, not function)	2	A	in: currier_a
C514	**RI Compositional Bifurcation** (17.4% locally-derived, 82.6% globally-composed; Section P highest local rate 26.1%)	2	A	in: currier_a
C515	**RI Compositional Mode Correlates with Length** (short RI = atomic/global; long RI = compound/local; rho=0.192, p<0.0001)	2	A	in: currier_a
C515.a	**Compositional Embedding Mechanism** (local derivation is additive - embedding local PP context requires more sub-components)	2	A	in: currier_a
C516	**RI Multi-Atom Observation** (99.6% multi-atom but trivially expected from lengths; intersection formula PROVISIONAL)	2	A	in: currier_a
C517	**Superstring Compression (GLOBAL)** (65-77% overlap, 2.2-2.7x compression; hinge letters are 7/8 kernel primitives; global substrate)	3	GLOBAL	in: currier_a
C518	**Compatibility Enrichment (GLOBAL)** (5-7x enrichment across all systems; extends C383 global type system)	3	GLOBAL	in: currier_a
C519	**Global Compatibility Architecture** (compression + enrichment = embedded compatibility relationships spanning A/B/AZC)	3	GLOBAL	in: currier_a
C520	**System-Specific Exploitation Gradient** (RI 6.8x > AZC 7.2x > PP 5.5x > B 5.3x; discrimination intensity varies)	3	GLOBAL	in: currier_a
C521	**Kernel Primitive Directional Asymmetry** (one-way valve: e→h=0.00, h→k=0.22, e→k=0.27 suppressed; h→e=7.00x, k→e=4.32x elevated; stabilization is absorbing)	2	B	in: grammar_system
C522	**Construction-Execution Layer Independence** (r=-0.21, p=0.07; character and class constraints are independent regimes sharing symbol substrate)	2	B	in: grammar_system
C523	**Pharma Label Vocabulary Bifurcation** (jar labels Jaccard=0.000 with content; content 58.3% PP vs 33.5% baseline)	2	A	in: currier_a
C524	**Jar Label Morphological Compression** (7.1 vs 6.0 char mean; 5-8 PP atoms per MIDDLE; superstring packing)	2	A	in: currier_a
C525	**Label Morphological Stratification** (o-prefix 50% vs 20% text; qo-prefix ~0% vs 14%; 61% label-only vocabulary; within-group MIDDLE sharing)	3	A	in: currier_a
C526	**RI Lexical Layer Hypothesis** (609 unique RI as referential lexicon; 87% localized to 1-2 folios; PREFIX/SUFFIX global grammar vs RI extensions as substance anchors)	3	A	in: currier_a
C527	**Suffix-Material Class Correlation** (Animal PP: 0% -y/-dy, 78% -ey/-ol; Herb PP: 41% -y/-dy, 27% -ey/-ol; chi2=178, p<10^-40; fire-degree interpretation conditional on Brunschwig)	3	A	in: currier_a
C528	**RI PREFIX Lexical Bifurcation** (334 PREFIX-REQUIRED, 321 PREFIX-FORBIDDEN, 12 optional; 98.2% disjoint; PREFIX attachment lexically determined; section-independent; refines C509.a aggregate rate)	2	A	in: currier_a
C529	**Gallows Positional Asymmetry** (PP gallows-initial 30% vs RI 20%; RI gallows-medial 58% vs PP 39%; chi2=7.69 p<0.01; bench gallows cph 81% RI; parallel bifurcation to C528)	2	A	in: currier_a
C530	**Gallows Folio Specialization** (k-default 54%, t-specialized folios cluster; p/f never folio-dominant; 2-5x same-gallows co-occurrence RI↔PP in records)	2	A	in: currier_a
C531	**Folio Unique Vocabulary Prevalence** (98.8% of B folios have ≥1 unique MIDDLE; only f95r1 lacks unique vocabulary; mean 10.5 unique MIDDLEs per folio)	2	A	in: currier_a
C532	**Unique MIDDLE B-Exclusivity** (88% of unique B MIDDLEs are B-exclusive, not in A; 12% are PP; unique vocabulary is primarily B-internal grammar, not AZC-modulated)	2	A	in: currier_a
C533	**Unique MIDDLE Grammatical Slot Consistency** (75% of unique MIDDLE tokens share PREFIX/SUFFIX patterns with classified tokens; adjacent folios' unique MIDDLEs fill similar slots 1.30x vs non-adjacent)	2	A	in: currier_a
C534	Section-Specific Prefixless MIDDLE Profiles (prefixless unique MIDDLEs show section-specific distribution p=0.023; effect vanishes for prefixed tokens where PREFIX-section associations explain pattern; partial signal only)	3	A	in: currier_a
C535	**B Folio Vocabulary Minimality** (81/82 folios needed for complete MIDDLE coverage; redundancy ratio 1.01x; zero folio pairs exceed 50% Jaccard; each folio contributes mean 10.5 unique MIDDLEs)	2	A	in: currier_a
C536	**Material-Class REGIME Invariance** (Both animal AND herb material classes route to REGIME_4: animal 2.03x p=0.024, herb 2.09x p=0.011; REGIME encodes precision requirement, not material identity)	2	A->B	in: currier_a
C537	**Token-Level Material Differentiation** (Despite identical REGIME routing, 62% of token variants differ: overall Jaccard=0.382, per-class mean=0.371; confirms C506.b behavioral heterogeneity)	2	A->B	in: currier_a
C538	PP Material-Class Distribution (ANIMAL 15.6%, HERB 28.0%, MIXED 16.6%, NEUTRAL 39.9%; classification conditional on Brunschwig suffix alignment)	3	A	in: currier_a
C539	**LATE Prefix Morphological Class** (al/ar/or: V+L pattern, 3.78x line-final enrichment, 68-70% suffix-depleted, short MIDDLE preference)	2	B	-> C539_late_prefix_class.md
C540	**Kernel Primitives Are Bound Morphemes** (k, e, h never standalone; 0 occurrences each; intervention modifiers only)	2	MORPHOLOGY	-> C540_kernel_bound_morpheme.md
C541	**Hazard Class Enumeration** (only 6/49 classes participate in 17 forbidden transitions; 43 classes have 0% hazard involvement)	2	HAZARD_TOPOLOGY	-> C541_hazard_class_enumeration.md
C542	**Gateway/Terminal Hazard Class Asymmetry** (Class 30 = pure gateway, Class 31 = pure terminal; 100% asymmetry)	2	HAZARD_TOPOLOGY	-> C542_gateway_terminal_asymmetry.md
C543	**Role Positional Grammar** (FLOW final-biased 0.68, CORE initial-biased 0.45; Class 40 = 69% line-final)	2	POSITIONAL_GRAMMAR	-> C543_role_positional_grammar.md
C544	**ENERGY_OPERATOR Interleaving** (qo/ch-sh families alternate with 2.5x enrichment; Class 33 self-repeat 14.6%)	2	CO-OCCURRENCE	-> C544_energy_interleaving.md
C545	**REGIME Instruction Class Profiles** (REGIME_3 = 1.83x CORE_CONTROL; REGIME_1 = 52% qo-family; each REGIME has signature classes)	2	REGIME_INTERPRETATION	-> C545_regime_class_profiles.md
C546	**Class 40 Safe Flow Operator** (daly/aly/ary: 4.22 avg distance from hazards, 0% hazard rate, 69% line-final; safe flow alternative)	2	HAZARD_TOPOLOGY	-> C546_class40_safe_flow.md
C547	qo-Chain REGIME_1 Enrichment (1.53x enrichment, 51.4% of chains in REGIME_1; depleted in REGIME_2/3; thermal processing context)	3	B	-> C547_qo_chain_regime_enrichment.md
C548	**Manuscript-Level Gateway/Terminal Envelope** (90.2% folios have both; rho=0.499 count correlation; gateways front-loaded rho=-0.368; arc from entry to exit)	2	B	-> C548_manuscript_level_envelope.md
C549	**qo/ch-sh Interleaving Significance** (56.3% vs 50.6% expected; z=10.27, p<0.001; grammatical preference for alternation; REGIME_3 highest 59.0%)	2	B	-> C549_interleaving_significance.md
C550	**Role Transition Grammar** (roles self-chain: FREQ 2.38x, FLOW 2.11x, ENERGY 1.35x; FLOW-FREQ bidirectional affinity 1.54-1.73x; ENERGY avoids other roles 0.71-0.80x; phrasal role structure)	2	B	-> C550_role_transition_grammar.md
C551	**Grammar Universality and REGIME Specialization** (67% classes universal; CC most universal 0.836; ENERGY REGIME_1 enriched 1.26-1.48x; FLOW REGIME_1 depleted 0.40-0.63x; thermal/flow anticorrelation)	2	B	-> C551_grammar_universality.md
C552	**Section-Specific Role Profiles** (Chi2=565.8, p<0.001; BIO +CC +EN thermal-intensive; HERBAL_B +FQ -EN repetitive; PHARMA +FL flow-dominated; RECIPE_B -CC autonomous; sections encode procedural types)	2	B	-> C552_section_role_profiles.md
C553	**BIO-REGIME Energy Independence** (BIO 70% REGIME_1; effects additive: baseline 27.5%, +6.5pp REGIME, +9.8pp section; both significant p<0.001; BIO+R1 reaches 48.9% ENERGY through independent combination)	2	B	-> C553_bio_regime_independence.md
C554	**Hazard Class Clustering** (dispersion index 1.29, p<0.001; 93% lines have hazard classes, mean 3.1/line; gateway-terminal 1.06x confirms C548; hazard management is zone-concentrated not point-distributed)	2	B	-> C554_hazard_clustering.md
C555	**PHARMA Thermal Operator Substitution** (Class 33 0.20x depleted, Class 34 1.90x enriched in PHARMA; ~10x divergence; section-specific not REGIME-driven; ENERGY operators not interchangeable)	2	B	-> C555_pharma_thermal_substitution.md
C556	**ENERGY Medial Concentration** (ENERGY 0.45x initial, 0.50x final - medial-concentrated; FLOW/FREQ 1.65x final; UNCLASS 1.55x initial; lines have positional template; p=3e-89)	2	B	-> C556_energy_medial_concentration.md
C557	**daiin Line-Initial ENERGY Trigger** (27.7% line-initial rate, 2.2x CC average; 47.1% ENERGY followers; Class 10 singleton; RECIPE 36.3% initial; unique control signal)	2	B	-> C557_daiin_line_opener.md
C558	**Singleton Class Structure** (only 3 singletons: Class 10/11/12; 2/3 CC classes are singletons; daiin initial-biased 27.7%, ol final-biased 9.5%; complementary control primitives)	2	B	-> C558_singleton_class_structure.md
C560	**Class 17 ol-Derived Control Operators** (9 tokens all PREFIX:ol + ENERGY-morph; BIO 1.72x enriched; PHARMA 0 occurrences; REGIME_3 1.90x; non-singleton CC is ol-derived)	2	B	-> C560_class17_ol_derivation.md
C561	**Class 9 or->aiin Directional Bigram** (87.5% of chains are or->aiin; zero aiin->aiin; directional grammatical unit; HERBAL 21.7% chain rate; refines C559 "self-chaining")	2	B	-> C561_class9_or_aiin_bigram.md
C562	**FLOW Role Structure** (19 tokens, 4.7% corpus; final-biased 17.5%; Class 40 59.7% final, ary 100% final; PHARMA 1.38x enriched, BIO 0.83x; ENERGY inverse pattern)	2	B	-> C562_flow_role_structure.md
C563	**AX Internal Positional Stratification** (20 AX classes split into INIT/5, MED/9, FINAL/6; H=213.9 p=3.6e-47; 71.8% INIT-before-FINAL; Cohen's d=0.69; positional gradient not clusters)	2	B	-> C563_ax_positional_stratification.md
C564	**AX Morphological-Positional Correspondence** (AX_INIT: 17.5% articulator; AX_MED: ok/ot 88.8%; AX_FINAL: prefix-light 60.9%, zero articulators; prefix family predicts position)	2	B	-> C564_ax_morphological_positional_correspondence.md
C565	**AX Execution Scaffold Function** (AX mirrors named role positions; 0% hazard; 1.09x self-chaining; AX_FINAL enriched R1 39.4% BIO 40.9%; structural frame not functional operations)	2	B	-> C565_ax_scaffold_function.md
C566	**UN Token Resolution** (7042 UN = 30.5% of B; 74.1% hapax, 74.8% single-folio; morphologically normal; cosurvival threshold artifact; NOT a separate role)	2	B	-> C566_un_token_resolution.md
C567	**AX-Operational MIDDLE Sharing** (57 AX MIDDLEs; 98.2% PP; 72% shared with operational roles; AX-EN Jaccard=0.400; 16 AX-exclusive; 78% PREFIX+ARTICULATOR differentiated)	2	B	-> C567_ax_operational_middle_sharing.md
C568	**AX Pipeline Ubiquity** (97.2% of A records carry AX vocabulary; 0 zero-AX B contexts; classes 21,22 always survive; AX_FINAL 100%, all subgroups 95.6%)	2	B	-> C568_ax_pipeline_ubiquity.md
C569	**AX Proportional Scaling** (AX fraction 0.454 vs expected 0.455; R²=0.83; NOT pure byproduct; AX_INIT over-represented slope 0.130 vs 0.102; AX_FINAL under-represented)	2	B	-> C569_ax_proportional_scaling.md
C570	**AX PREFIX Derivability** (89.6% binary accuracy; PREFIX is role selector; 22 AX-exclusive prefixes; F1=0.904; same MIDDLE becomes AX or operational via PREFIX)	2	B	-> C570_ax_prefix_derivability.md
C571	**AX Functional Identity Resolution** (AX = PREFIX-determined default mode of pipeline vocabulary; same MIDDLEs serve as scaffold or operations; PREFIX selects role, MIDDLE carries material)	2	B	-> C571_ax_functional_identity.md
C572	**AX Class Behavioral Collapse**	2	B	AX_CLASS_BEHAVIOR
C573	**EN Definitive Count: 18 Classes** (ICC-based: {8, 31-37, 39, 41-49}; resolves BCSC=11 undercount; 7211 tokens = 31.2% of B; Core 6 = 79.5%, Minor 12 = 20.5%)	2	B	-> C573_en_definitive_count.md
C574	**EN Distributional Convergence** (k=2 silhouette 0.180; QO/CHSH identical positions, REGIME, context (JS=0.0024); but MIDDLE Jaccard=0.133, trigger chi2=134; grammatically equivalent, lexically partitioned; C276/C423 within single role)	2	B	-> C574_en_behavioral_collapse.md
C575	**EN is 100% Pipeline-Derived** (64 unique MIDDLEs, all PP; 0 RI, 0 B-exclusive; even purer than AX's 98.2% PP; vocabulary entirely inherited from Currier A)	2	B	-> C575_en_pipeline_derived.md
C576	**EN MIDDLE Vocabulary Bifurcation by Prefix** (QO uses 25 MIDDLEs, CHSH uses 43; only 8 shared, Jaccard=0.133; PREFIX selects MIDDLE subvocabulary, not grammatical function)	2	B	-> C576_en_middle_bifurcation.md
C577	**EN Interleaving is Content-Driven** (QO/CHSH same positions p=0.104; BIO 58.5%, PHARMA 27.5%; alternation is material-type selection, not positional)	2	B	-> C577_en_interleaving_content_driven.md
C578	**EN Has 30 Exclusive MIDDLEs** (46.9% of EN vocabulary; not shared with AX, CC, FL, or FQ; dedicated content subvocabulary within pipeline)	2	B	-> C578_en_exclusive_middles.md
C579	**CHSH-First Ordering Bias** (53.9% CHSH-first in mixed lines; p=0.010, n=1130; modest but significant asymmetry)	2	B	-> C579_chsh_first_ordering.md
C580	**EN Trigger Profile Differentiation** (CHSH triggered by AX 32.5%, CC 11%; QO triggered by EN-self 53.5%, boundary 68.8%; chi2=134, p<0.001)	2	B	-> C580_en_trigger_profiles.md
C581	**CC Definitive Census** (CC={10,11,12,17}; 1023 tokens, 4.4% of B; Classes 10,11 active, 12 ghost (zero tokens per C540), 17 ol-derived per C560)	2	B	-> C581_cc_definitive_census.md
C582	**FL Definitive Census** (FL={7,30,38,40}; 1078 tokens, 4.7% of B; 4 classes confirmed vs BCSC=2; hazard pair {7,30} + safe pair {38,40})	2	B	-> C582_fl_definitive_census.md
C583	**FQ Definitive Census** (FQ={9,13,14,23}; 2890 tokens, 12.5% of B; supersedes C559's {9,20,21,23}; Classes 20,21 are AX per C563)	2	B	-> C583_fq_definitive_census.md
C584	**Near-Universal Pipeline Purity** (CC/EN/FL/FQ all 100% PP; AX 98.2% per C567; pipeline vocabulary dominates all roles; operational roles pure, scaffold near-pure)	2	B	-> C584_near_universal_pipeline_purity.md
C585	**Cross-Role MIDDLE Sharing** (EN-AX Jaccard=0.400; EN 30 exclusive MIDDLEs; CC/FL/FQ 0-5 exclusive; small roles share heavily with EN/AX; vocabulary partition follows role hierarchy)	2	B	-> C585_cross_role_middle_sharing.md
C586	**FL Hazard-Safe Split** (hazard {7,30} vs safe {38,40}; position p=9.4e-20; final rate p=7.3e-33; FL source-biased 4.5x; Class 30 gateway, Class 40 maximally hazard-distant)	2	B	-> C586_fl_hazard_safe_split.md
C587	**FQ Internal Differentiation** (4-way genuine structure, 100% KW significance; Class 9 medial self-chaining; 13/14 ok/ot-prefixed large medial; 23 minimal final-biased)	2	B	-> C587_fq_internal_differentiation.md
C588	**Suffix Role Selectivity** (chi2=5063.2, p<0.001; EN 17 suffix types 61% suffixed; CC 100% suffix-free; FL/FQ ~93% suffix-free; AX intermediate 38%; three-tier suffix structure)	2	B	-> C588_suffix_role_selectivity.md
C589	**Small Role Genuine Structure** (CC, FL, FQ all GENUINE_STRUCTURE; CC 75%, FL 100%, FQ 100% KW features significant; contrasts AX COLLAPSED and EN CONVERGENCE)	2	B	-> C589_small_role_genuine_structure.md
C590	**CC Positional Dichotomy** (Class 10 daiin initial-biased mean=0.41; Class 11 ol medial-biased mean=0.51; p=2.8e-5; complementary control primitives)	2	B	-> C590_cc_positional_dichotomy.md
C591	**Five-Role Complete Taxonomy** (49 classes → 5 roles: EN=18, AX=19, FQ=4, CC=4, FL=4; complete partition; each role has distinct suffix, position, hazard, section, REGIME profile)	2	B	-> C591_five_role_complete_taxonomy.md
C592	**C559 Membership Correction** (C559 used {9,20,21,23} for FQ; correct is {9,13,14,23}; C559 SUPERSEDED; downstream C550/C551/C552/C556 flagged for re-verification with corrected membership)	2	B	-> C592_c559_membership_correction.md
C593	**FQ 3-Group Structure** ({9} connector, {13,14} prefixed-pair, {23} closer; k=3 silhouette 0.68; PC1=position 64.2%, PC2=morphology 28.2%; BARE=HAZARDOUS, PREFIXED=SAFE perfect overlap)	2	B	-> C593_fq_3group_structure.md
C594	**FQ 13-14 Complete Vocabulary Bifurcation** (Jaccard=0.000, zero shared MIDDLEs; 13: {aiin,ain,e,edy,eey,eol} 18.2% suffixed; 14: {al,am,ar,ey,ol,or,y} 0% suffixed; sharper than EN C576)	2	B	-> C594_fq_13_14_vocabulary_bifurcation.md
C595	**FQ Internal Transition Grammar** (chi2=111 p<0.0001; 23→9 enriched 2.85x; 9→13 ratio 4.6:1; all self-chain; 2×2 BARE/PREFIXED chi2=69.7; sequential structure not random mixing)	2	B	-> C595_fq_internal_transition_grammar.md
C596	**FQ-FL Position-Driven Symbiosis** (chi2=20.5 p=0.015; hazard alignment p=0.33 NS; FL7→FQ9 medial, FL30→FQ13/14 final; symbiosis is positional not hazard-mediated)	2	B	-> C596_fq_fl_position_driven_symbiosis.md
C597	**FQ Class 23 Boundary Dominance** (29.8% final rate, 39% of FQ finals despite 12.5% token share; 12.2% initial; mean run length 1.19, 84% singletons; boundary specialist)	2	B	-> C597_fq_class23_boundary_dominance.md
C598	**Cross-Boundary Sub-Group Structure** (8/10 pairs significant; FQ_CONN->EN_CHSH 1.41x, FQ_CONN->EN_QO 0.16x; sub-group routing visible across role boundaries)	2	B	-> C598_cross_boundary_subgroup_structure.md
C599	**AX Scaffolding Routing** (chi2=48.3 p=3.9e-4; AX_FINAL avoids EN_QO 0.59x, feeds FQ_CONN 1.31x; AX is routing mechanism not neutral frame)	2	B	-> C599_ax_scaffolding_routing.md
C600	**CC Trigger Sub-Group Selectivity** (chi2=129.2 p=9.6e-21; daiin/ol trigger EN_CHSH 1.60-1.74x, avoid EN_QO 0.18x; ol-derived reverses: EN_QO 1.39x)	2	B	-> C600_cc_trigger_subgroup_selectivity.md
C601	**Hazard Sub-Group Concentration** (19 events from 3 source sub-groups: FL_HAZ/EN_CHSH/FQ_CONN; EN_CHSH absorbs 58%; QO never participates)	2	B	-> C601_hazard_subgroup_concentration.md
C602	**REGIME-Conditioned Sub-Role Grammar** (4/5 pairs REGIME-dependent; AX->FQ REGIME-independent; core routing invariant, magnitudes shift by REGIME)	2	B	-> C602_regime_conditioned_subrole_grammar.md
C603	**CC Folio-Level Subfamily Prediction** (CC_OL_D fraction->QO proportion rho=0.355 p=0.001; CC_DAIIN fraction->CHSH proportion rho=0.345 p=0.002; CC composition strongest predictor of EN subfamily balance)	2	B	-> C603_cc_folio_level_subfamily_prediction.md
C604	**C412 REGIME Decomposition** (C412 rho=-0.304 partially REGIME-mediated, 27.6% reduction; vanishes within REGIME_1 rho=-0.075 and REGIME_2 rho=-0.051; EN subfamily 8.2% and CC composition 11.7% do not mediate)	2	B	-> C604_c412_regime_decomposition.md
C605	**Two-Lane Folio-Level Validation** (lane balance predicts escape_density rho=-0.506 vs ch_preference rho=-0.301; adds independent info partial rho=-0.452 p<0.0001; two-lane model validated at folio level)	2	B	-> C605_two_lane_folio_validation.md
C606	**CC->EN Line-Level Routing** (chi2=40.28 p<10^-6 V=0.246; CC_OL_D->QO 1.67x enrichment; same-lane pairs 1.81-1.83 tokens apart vs cross-lane 2.48-2.78; token-level routing confirmed)	2	B	-> C606_cc_en_line_level_routing.md
C607	**Line-Level Escape Prediction** (EN_CHSH->escape rho=-0.707 n=2240 p<10^-6, 2.3x stronger than folio C412 rho=-0.304; lane balance->escape rho=-0.363 n=409; escape is line-level phenomenon)	2	B	-> C607_line_level_escape_prediction.md
C608	**No Lane Coherence / Local Routing** (coherence p=0.963, lines do not specialize; directionality diff=-0.008 CI[-0.151,0.141]; two-lane model is local token routing, not line-level identity)	2	B	-> C608_no_lane_coherence.md
C609	**LINK Density Reconciliation** (true density 13.2%=3,047/23,096; legacy 6.6% and 38% not reproducible; LINK cuts all 5 ICC roles: AX 26.2%, EN 19.0%, CC 13.8%; 'ol' in MIDDLE 41.2%, PREFIX 28.7%)	2	B	-> C609_link_density_reconciliation.md
C610	**UN Morphological Profile** (7,042 tokens=30.5% B; 2x suffix rate 77.3% vs 38.7%; 5.3x articulator rate; 79.4% PP MIDDLEs, 0% RI; 90.7% novel MIDDLEs contain PP atoms; complexity is mechanism of non-classification)	2	B	-> C610_un_morphological_profile.md
C611	**UN Role Prediction** (PREFIX assigns 99.2%; consensus 99.9%; EN 37.1%, AX 34.6%, FQ 22.4%, FL 5.9%, CC 0.0%; CC fully resolved; UN is morphological tail of EN/AX/FQ)	2	B	-> C611_un_role_prediction.md
C612	**UN Population Structure** (bifurcates k=2 silhouette=0.263; Cluster 0 high-suffix EN/AX, Cluster 1 lower-suffix FQ/AX; hapax longer 6.65 vs 5.84 p<0.0001; UN~TTR rho=+0.631***, UN~LINK rho=-0.524***; REGIME ns)	2	B	-> C612_un_population_structure.md
C613	**AX-UN Boundary** (2,150 AX-predicted UN tokens; similar positions p=0.084; similar transition contexts; boundary continuous not categorical; if absorbed AX grows 17.9%->27.2% of B)	2	B	-> C613_ax_un_boundary.md
C614	**AX MIDDLE-Level Routing** (MIDDLE predicts successor role: INIT V=0.167 p<0.001, MED V=0.147 p<0.001, FINAL n.s.; no priming; AX~EN diversity rho=+0.796***; Class 22 = extreme FINAL 62.2% line-final)	2	B	-> C614_ax_middle_level_routing.md
C615	**AX-UN Functional Integration** (2,246 AX-predicted UN route identically all subgroups p>0.1; 89.3% classified AX MIDDLEs shared; 312 truly novel MIDDLEs; combined AX = 6,098 = 26.4% of B)	2	B	-> C615_ax_un_functional_integration.md
C616	**AX Section/REGIME Conditioning** (section: transitions V=0.081, MIDDLE V=0.227; REGIME: transitions V=0.082, AX->EN varies 24.5-39.1% p=0.0006; AX->FQ REGIME-dependent p=0.003 refining C602)	2	B	-> C616_ax_context_conditioning.md
C617	**AX-LINK Subgroup Asymmetry** (AX_FINAL 35.3% LINK, AX_INIT 19.4%, AX_MED 3.3%; LINK concentrates at AX boundaries; line co-occurrence chi2=16.21 p<0.001; no folio-level correlation p=0.198)	2	B	-> C617_ax_link_subgroup_asymmetry.md
C618	**Unique MIDDLE Identity** (858 unique MIDDLEs are 100% UN, 99.7% hapax, MIDDLE length 4.55 vs 2.12 shared, 83.1% suffix rate, 88% B-exclusive, 95.7% contain PP atoms; morphological extreme tail of B)	2	B	-> C618_unique_middle_identity.md
C619	**Unique MIDDLE Behavioral Equivalence** (unique vs shared UN transitions: successor V=0.070, predecessor V=0.051; UN-neighbor rate 54.6% vs 47.5%; unique density = UN proportion rho=+0.740***; H1 lexical tail CONFIRMED, H2/H3 REJECTED)	2	B	-> C619_unique_middle_behavioral_equivalence.md
C620	**Folio Vocabulary Network** (k=2 silhouette=0.055, ARI_section=0.497, ARI_REGIME=0.022; section-controlled adjacency 1.057x vs raw 1.179x; section H vs rest; no manuscript gradient in unique density p=0.676)	2	B	-> C620_folio_vocabulary_network.md
C621	**Vocabulary Removal Impact** (removing 868 unique MIDDLE tokens: 96.2% survival, mean role shift 2.80 pp, max 7.04 pp, 1/82 folios lose ICC role; UN -2.71 pp; vocabulary minimality is type diversity, not functional necessity)	2	B	-> C621_vocabulary_removal_impact.md
C622	**Hazard Exposure Anatomy** (43 safe classes: 23 role-excluded (20 AX + 3 CC) + 20 sub-group-excluded (16 EN + 2 FL + 2 FQ); 0 incidental; safe classes route to hazard at 24.6%; FL_SAFE line-final mean=0.811 vs hazard FL 0.546 p<0.001)	2	B	-> C622_hazard_exposure_anatomy.md
C623	**Hazard Token Morphological Profile** (18 forbidden tokens: 0% suffix, 0% articulator, 33% prefix; best discriminant 68.8% on n=32 baseline 56.2%; hazard participation is lexically specific, not morphologically predictable)	2	B	-> C623_hazard_token_morphological_profile.md
C624	**Hazard Boundary Architecture** (17 forbidden pairs: 0 occurrences confirmed; 114 near-misses; FL/CC buffer enrichment 1.55x/1.50x; AX under-represented 0.84x; selectivity 6.4% of observed pairs; regime does not predict hazard density p=0.26)	2	B	-> C624_hazard_boundary_architecture.md
C625	**Hazard Circuit Token Mapping** (6/12 classifiable forbidden pairs are reverse-circuit flows; circuit topology explains 75% of classifiable pairs; 4 unclassified tokens trivial; Fisher p=0.193 odds ratio 2.44)	2	B	-> C625_hazard_circuit_token_mapping.md
C626	**Lane-Hazard MIDDLE Discrimination** (NULL: two-lane architecture does NOT predict hazard; forbidden MIDDLEs in neither lane 4/5; CC trigger p=0.866; QO contexts have 55% more hazard bigrams than CHSH)	2	B	-> C626_lane_hazard_middle_discrimination.md
C627	**Forbidden Pair Selectivity** (no frequency bias rank 0.562; 0/17 reciprocal-forbidden; circuit topology explains 9/12=75%; FQ_CLOSER boundary tokens account for 3 unexplained; directional token-specific lookup table)	2	B	-> C627_forbidden_pair_selectivity.md
C628	**FQ_CLOSER Positional Segregation Test** (dy→aiin positionally separated via 35.8% final bias p<0.000001; dy→chey genuine prohibition 1 adj to class but 0 to token; l→chol genuine prohibition 4 adj to class but 0 to token; boundary gap not discriminative)	2	B	-> C628_fq_closer_positional_segregation.md
C629	**FQ_CLOSER Source Token Discrimination** (dy c9 restart rate 0% vs s 48.6%; forbidden sources lower hazard rate 28.2% vs 35.5%; higher EN_CHSH rate 13.1% vs 8.6%; JSD 0.219; class 23 contains restart specialists and general distributors)	2	B	-> C629_fq_closer_source_discrimination.md
C630	**FQ_CLOSER Boundary Mechanism** (25% gap resolved: dy→aiin positional, l→chol frequency artifact P(0)=0.85, dy→chey likely genuine E=1.32; s→aiin 20x over-represented dominates restart loop; class 23 not unified mechanism)	2	B	-> C630_fq_closer_boundary_mechanism.md
C631	**Intra-Class Clustering Census** (effective vocabulary 56 from 49 classes + 7 k=2 splits; 86% uniform; mean JSD 0.639 continuous not clustered; silhouette <0.25 in 34/36 classes; 480 types compress 8.6x)	2	B	-> C631_intra_class_clustering_census.md
C632	**Morphological Subtype Prediction** (MIDDLE predicts clusters in 6/7 classes ARI=1.0; no significance at n=2-5; class 30 FL_HAZ morphologically opaque; PREFIX/ARTICULATOR zero power; MIDDLE-centric identity validated)	2	B	-> C632_morphological_subtype_prediction.md
C633	**Effective Vocabulary Census** (56 effective sub-types; FLOW_OPERATOR most diverse mean k=1.50; hazard 50% heterogeneous vs non-hazard 9% Fisher p=0.031; size inversely predicts k rho=-0.321 p=0.025; JSD continuous not discrete)	2	B	-> C633_effective_vocabulary_census.md
C634	**Recovery Pathway Profiling** (0/13 KW tests significant; kernel absorption exit rate ~98-100% all REGIMEs; recovery path mean 3.76-4.78; post-kernel EN-dominated ~49-75%; recovery pathways NOT regime-stratified)	2	B	-> C634_recovery_pathway_profiling.md
C635	**Escape Strategy Decomposition** (0/9 per-folio KW significant; aggregate chi2 first-EN p=0.0003 but folio-level NS; JSD between REGIME fingerprints 0.031-0.082; escape strategies NOT regime-stratified)	2	B	-> C635_escape_strategy_decomposition.md
C636	**Recovery-Regime Interaction** (10/12 features FREE; 2/12 SUPPRESSOR: e_rate partial_p=0.0005 eta_sq=0.188, h_rate partial_p<0.0001 eta_sq=0.293; class composition masks kernel routing; recovery UNCONDITIONALLY FREE with latent e/h suppressor)	2	B	-> C636_recovery_regime_interaction.md
C637	**B MIDDLE Sister Preference** (77 MIDDLEs, 22.9% of ch_preference variance from MIDDLE composition rho=0.479 p=0.000005; B less differentiated than A 0.140 vs 0.254; A-B cross-system rho=0.440 p=0.003; ok/ot near 50/50 less differentiated)	2	B	-> C637_b_middle_sister_preference.md
C638	**Quire Sister Consistency** (quire KW H=32.002 p=0.0001 eta_sq=0.329; ICC(1,1)=0.362 FAIR; but CONFOUNDED with section Cramer's V=0.875; within section H quire NS p=0.665; section KW eta_sq=0.321 3.6x stronger than REGIME eta_sq=0.088)	2	B	-> C638_quire_sister_consistency.md
C639	**Sister Pair Variance Decomposition** (47.1% explained adj_R2=32.3%; 52.9% UNEXPLAINED free choice; shared variance 36.4% dominates; unique: quire 3.8%, lane balance 2.7%, MIDDLE 2.6%, REGIME 1.2%, section 0.4%; clean residuals no autocorrelation)	2	B	-> C639_sister_pair_variance_decomposition.md
C640	**PP Role Projection Architecture** (89/404 PP match B classes 22%; B has only 90 MIDDLEs from 480 types; B-Native 100% EN-dominant 8/8; AZC-Med AX 53.1% EN 40.7%; PP role dist differs from B shares chi2=42.37 p<0.0001; AX over-represented CC/FQ absent; frequency confound severe p<0.0001)	2	CROSS_SYSTEM	-> C640_pp_role_projection_architecture.md
C641	**PP Population Execution Profiles** (AZC-Med/B-Native differ: AX p=0.006, EN p=0.001; REGIME_2 p=0.0004, REGIME_3 p<0.0001; suffix diversity p<0.0001 frequency-confounded rho=0.795; EN subfamily partially independent of PREFIX rho=0.510; QO records smaller 5.5 vs 7.4, ANIMAL-enriched p=0.003)	2	CROSS_SYSTEM	-> C641_pp_population_execution_profiles.md
C642	**A Record Role & Material Architecture** (lattice 8.0% density 92% incompatibility; pair-level role heterogeneity at chance p=0.55; record-level role coverage below expected 1.91 vs 2.13 p=0.022; material consistency BELOW chance 0.6% vs 4.1% p=0.0006 active mixing; material-role NS V=0.122)	2	CROSS_SYSTEM	-> C642_a_record_role_material_architecture.md
C643	**Lane Hysteresis Oscillation** (EN alternation 0.563 vs null 0.494 p<0.0001; run lengths QO=1.46 CHSH=1.61 median 1.0; QO exits faster 60.0% vs CHSH 53.3%; section variation BIO=0.606 HERBAL_B=0.427; extends C549 within-line)	2	B	-> C643_lane_hysteresis_oscillation.md
C644	**QO Transition Stability** (QO mean stability=0.318 CHSH=0.278 p=0.0006 r=-0.039; entropy QO=4.08 CHSH=4.51; small effect; QO in more predictable contexts)	2	B	-> C644_qo_transition_stability.md
C645	**CHSH Post-Hazard Dominance** (post-hazard EN: CHSH=75.2% QO=24.8%; QO enrichment 0.55x depleted; CHSH closer to hazard mean=3.81 vs 3.82 p=0.002 r=0.072; extends C601 continuous gradient)	2	B	-> C645_chsh_post_hazard_dominance.md
C646	**PP-Lane MIDDLE Discrimination** (20/99 PP MIDDLEs predict lane FDR<0.05 z=24.26; 15 QO 5 CHSH; QO=k/t ENERGY_OPERATOR 11/15; CHSH=o AUXILIARY 3/5; 17/20 EN-mediated caveat; 3 non-EN novel; no obligatory slots)	2	A/B	-> C646_pp_lane_middle_discrimination.md
C647	**Morphological Lane Signature** (QO k=70.7% CHSH e=68.7% V=0.654 p<0.0001; CC proximity shows no discrimination p=0.879; signature is MIDDLE-internal not positional; lanes built from different kernel-character vocabularies)	2	B	-> C647_morphological_lane_signature.md
C648	**LINK-Lane Independence** (QO 15.4% vs CHSH 14.7% LINK chi2=0.44 p=0.506 V=0.0095; excluding AX_FINAL 11.0% vs 11.1%; monitoring operates above lane identity)	2	B	-> C648_link_lane_independence.md
C649	**EN-Exclusive MIDDLE Deterministic Lane Partition** (22/30 exclusive MIDDLEs 100% lane-specific FDR<0.05; 13 QO-only k/t/p-initial 9 CHSH-only e/o-initial; absolute not probabilistic)	2	B	-> C649_exclusive_middle_lane_partition.md
C650	**Section-Driven EN Oscillation Rate** (section partial eta2=0.174 p=0.024 controlling REGIME; REGIME eta2=0.158 p=0.069 NS controlling section; BIO=0.593 HERBAL=0.457; material type drives oscillation)	2	B	-> C650_section_driven_oscillation.md
C651	**Fast Uniform Post-Hazard QO Recovery** (CHSH 75.2% first-EN post-hazard replicates C645; mean 0.77 CHSH before QO median=1.0; 45.1% immediate; no section/REGIME/class variation; unconditionally stable)	2	B	-> C651_fast_post_hazard_recovery.md
C652	**PP Lane Character Asymmetry** (25.5% QO-predicting at type level p<3e-14; 31.3% token level; 3:1 CHSH bias in PP vocabulary; material class NS chi2=2.4 p=0.49)	2	GLOBAL	-> C652_pp_lane_character_asymmetry.md
C653	**AZC Lane Filtering Bias** (AZC-Med 19.7% QO vs B-Native 33.7% QO; OR=0.48 p=0.023; token-level OR=0.47 p<1e-17; pipeline suppresses QO vocabulary)	2	GLOBAL	-> C653_azc_lane_filtering_bias.md
C654	**Non-EN PP Lane Independence** (partial r=0.028 p=0.80 controlling section+REGIME; tautological sensitivity r=0.645; lane is EN-internal not vocabulary-landscape; grammar compensates 2.2x)	2	B	-> C654_non_en_pp_lane_independence.md
C655	**PP Lane Balance Redundancy** (incr R2=0.0005 F=0.058 p=0.81; AZC-Med incr=0.000 B-Native incr=0.004 both NS; A-record vs B-folio KS D=0.554 p<1e-10 divergent; section+REGIME fully account)	2	B	-> C655_pp_lane_balance_redundancy.md
C656	**PP Co-Occurrence Continuity** (max silhouette 0.016 across k=2..20; 76% zero-Jaccard; single connected component; within-Herbal sil=0.020; no discrete PP pools by co-occurrence)	2	A	-> C656_pp_cooccurrence_continuity.md
C657	**PP Behavioral Profile Continuity** (93 eligible PP; best sil=0.237 degenerate k=2: 2 vs 91; mean JSD=0.537; lane character ARI=0.010; no discrete behavioral clusters)	2	B	-> C657_pp_behavioral_profile_continuity.md
C658	**PP Material Gradient** (36.2% entropy reduction as gradient not partition; NMI(pool,material)=0.129; chi2 p=0.002 V=0.392; pool 18 54% MIXED; all cross-axis NMI<0.15)	2	A	-> C658_pp_material_gradient.md
C659	**PP Axis Independence** (co-occurrence vs behavior ARI=0.052; NMI material=0.129 pathway=0.032 lane=0.062 section=0.087; role eta2 mean=0.146; axes mutually independent; PP is high-dimensional continuous space)	2	A/B	-> C659_pp_axis_independence.md
C660	**PREFIX x MIDDLE Selectivity Spectrum** (128 testable: 3.9% locked, 27.3% dominant, 22.7% bimodal, 46.1% promiscuous; QO 100% qo-locked; chi2=50.65 V=0.445; B wider than A Jaccard=0.484)	2	B	-> C660_prefix_middle_selectivity_spectrum.md
C661	**PREFIX x MIDDLE Behavioral Interaction** (within-MIDDLE between-PREFIX JSD=0.425 vs between-MIDDLE JSD=0.436; effect ratio=0.975 computed / 0.792 vs C657; PREFIX transforms behavior; ckh JSD=0.710 max)	2	B	-> C661_prefix_middle_behavioral_interaction.md
C662	**PREFIX Role Reclassification** (mean 75% class reduction median 82%; EN PREFIX->EN class 94.1%; AX PREFIX->AX/FQ 70.8%; 50.4% of pairs reduce to <20% of MIDDLE's classes)	2	B	-> C662_prefix_role_reclassification.md
C663	**Effective PREFIX x MIDDLE Inventory** (1190 observed, 501 effective pairs, 1.24x expansion; best sil=0.350 k=2 vs C657 0.237; k=3 degenerate; binary EN/non-EN split)	2	B	-> C663_effective_prefix_middle_inventory.md
C664	**Role Profile Trajectory** (AX increases late rho=+0.082 p<0.001 Q1=15.4% Q4=18.1%; EN marginal decline; CC/FL/FQ flat; EN slope regime-dependent KW p=0.038; folio trajectory clustering k=2 sil=0.451 two outliers)	2	B	-> C664_role_profile_trajectory.md
C665	**LINK Density Trajectory** (stationary within folios rho=+0.020 p=0.333 KW p=0.559; extends C365 line-level uniformity to meso-temporal; REGIME_3 steepest +0.051 but NS)	2	B	-> C665_link_density_trajectory.md
C666	**Kernel Contact Trajectory** (k/h/e all stationary within folios; e dominates ~29% flat; k rare ~0.2% flat; k/e ratio flat rho=-0.023 p=0.29; extends C458 between-folio clamping to within-folio)	2	B	-> C666_kernel_contact_trajectory.md
C667	**Escape/Hazard Density Trajectory** (hazard density flat rho=+0.009 p=0.650; 0 forbidden events in corpus; escape density flat; Q4 escape efficiency drops 0.579 vs 0.636; REGIME_2/3 late hazard increase)	2	B	-> C667_escape_hazard_trajectory.md
C668	**Lane Balance Trajectory** (QO fraction declines rho=-0.058 p=0.006 Q1=46.3% Q4=41.3%; REGIME_2 strongest -9.9pp; REGIME_4 flat +1.4pp; CHSH-ward drift = energy-to-stabilization shift)	2	B	-> C668_lane_balance_trajectory.md
C669	**Hazard Proximity Trajectory** (mean distance-to-hazard tightens rho=-0.104 p<0.001 Q1=2.75 Q4=2.45; QO tightens rho=-0.082 p=0.003 CHSH static; REGIME_2 strongest -0.602; REGIME_4 flat -0.051)	2	B	-> C669_hazard_proximity_trajectory.md
C670	**Adjacent-Line Vocabulary Coupling** (no coupling; Jaccard obs=0.140 perm=0.126 diff=+0.014; 0/79 folios sig; MIDDLEs selected independently per line)	0	B	-> C670_adjacent_line_vocabulary_coupling.md
C671	**MIDDLE Novelty Shape** (front-loaded; 87.3% FL 0% BL; first-half frac=0.685 vs perm=0.653; vocabulary introduced early, reused late)	0	B	-> C671_middle_novelty_shape.md
C672	**Cross-Line Boundary Grammar** (grammar-transparent; H_boundary=4.284 H_within=4.628 ratio=0.926; chi2 p=0.187 not sig non-independent; 7.4% entropy reduction at boundaries)	0	B	-> C672_cross_line_boundary_grammar.md
C673	**CC Trigger Sequential Independence** (no memory; self-transition 0.390 vs perm 0.395 p=1.0; CC trigger re-selected each line independently)	0	B	-> C673_cc_trigger_sequential_independence.md
C674	**EN Lane Balance Autocorrelation** (folio-driven; raw lag-1 rho=0.167 p<1e-6 but perm p=1.0; lag-2/3 stronger than lag-1; autocorrelation entirely explained by folio identity)	0	B	-> C674_en_lane_balance_autocorrelation.md
C675	**MIDDLE Vocabulary Trajectory** (minimal drift; JSD Q1-Q4=0.081 ratio=1.078; 4/135 MIDDLEs positionally biased after Bonferroni; token identity position-invariant)	0	B	-> C675_middle_vocabulary_trajectory.md
C676	**Morphological Parameterization Trajectory** (PREFIX chi2 p=3.7e-9 suffix p=1.7e-7; qo PREFIX rho=-0.085 bare suffix rho=+0.095; morphological simplification late)	0	B	-> C676_morphological_parameterization_trajectory.md
C677	**Line Complexity Trajectory** (unique tokens rho=-0.196 p<1e-21; unique MIDDLEs rho=-0.174; mean token len rho=-0.093; TTR flat 0.962; lines shorten late, equally diverse per token)	0	B	-> C677_line_complexity_trajectory.md
C678	**Line Profile Classification** (continuous; best KMeans sil=0.100 no discrete types; PC1=morphological complexity 12.1%; PC2=monitoring intensity 9.3%; 10 PCs for 68.3%)	0	B	-> C678_line_profile_classification.md
C679	**Line Type Sequencing** (weak coupling; adjacent cosine sim=0.675 vs random=0.641 diff=+0.031 p<0.001; 3.1% similarity elevation for consecutive lines)	0	B	-> C679_line_type_sequencing.md
C680	**Positional Feature Prediction** (11/27 features position-correlated; 9/27 add beyond REGIME; line_length dR2=0.040 strongest; 16/27 position-independent)	0	B	-> C680_positional_feature_prediction.md
C681	**Sequential Coupling Verdict** (24/27 features lag-1 sig; SEQUENTIALLY_COUPLED but folio-mediated not sequential; top: line_length dR2=0.098 EN dR2=0.091 LINK dR2=0.063; lines = contextually-coupled independently-assessed)	0	B	-> C681_sequential_coupling_verdict.md
C682	**Survivor Distribution Profile** (mean 11.08/49 classes survive per A record; median=10 std=5.79; 1.2% zero-class; token survival mean=38.5/4889; right-skewed distribution)	2	A-B	-> C682_survivor_distribution_profile.md
C683	**Role Composition Under Filtering** (FL most depleted 60.9%; CC 44.6%; FQ most resilient 12.5%; role entropy mean=1.611/2.322; asymmetric depletion hierarchy)	2	A-B	-> C683_role_composition_under_filtering.md
C684	**Hazard Pruning Under Filtering** (83.9% full elimination of all 17 forbidden transitions; mean 0.21 active; max 5; filtering = natural hazard suppression)	2	A-B	-> C684_hazard_pruning_under_filtering.md
C685	**LINK and Kernel Survival Rates** (97.4% kernel union access h=95.5% k=81.0% e=60.7%; 36.5% lose all LINK tokens; monitoring capacity fragile)	2	A-B	-> C685_link_kernel_survival_rates.md
C686	**Role Vulnerability Gradient** (FL most fragile 2.3% at 0-2 PP; FQ most resilient 13.5%; vulnerability ordering FL>EN>AX>CC>FQ; all roles >0% in all PP bins)	2	A-B	-> C686_role_vulnerability_gradient.md
C687	**Composition-Filtering Interaction** (PURE_RI mean=0.44 classes near-zero; MIXED=PURE_PP p=0.997; only 9 PURE_RI records; composition binary divide PP vs RI)	2	A-B	-> C687_composition_filtering_interaction.md
C688	**REGIME Filtering Robustness** (REGIME_2 most robust 0.222; REGIME_3 least 0.167; REGIMEs 1/2/4 clustered ~0.21; filtering severity A-record-driven not REGIME-driven)	2	A-B	-> C688_regime_filtering_robustness.md
C689	**Survivor Set Uniqueness** (1525/1562 unique class sets = 97.6%; Jaccard mean=0.199; each A record = near-unique filter fingerprint)	2	A-B	-> C689_survivor_set_uniqueness.md
C690	**Line-Level Legality Distribution** (25/32 pairings >50% empty lines; median record makes 74-100% empty; no positional effect rho=0.005 p=0.87; max-classes = 7-27% empty)	2	A-B	-> C690_line_level_legality_distribution.md
C691	**Program Coherence Under Filtering** (0-20% operational completeness; work group survives best up to 87%; close group is bottleneck; max gap = entire folio for most records)	2	A-B	-> C691_program_coherence_under_filtering.md
C692	**Filtering Failure Mode Distribution** (94.7% MIDDLE miss, 3.6% PREFIX, 1.7% SUFFIX; consistent across all roles 91-97% MIDDLE; MIDDLE = gatekeeper)	2	A-B	-> C692_filtering_failure_mode_distribution.md
C693	**Usability Gradient** (266x dynamic range; best=0.107 Max-classes; 78% pairings unusable >50% empty; single A record does NOT produce usable B program)	2	A-B	-> C693_usability_gradient.md
C694	**RI Placement Non-Random** (Fisher combined KS p ~ 10^-306; inter-RI gaps deviate from geometric; Wald-Wolfowitz runs test p=0.78 ns)	2	A	|
C696	**RI Line-Final Preference** (1.48x enrichment, p=1.26e-07; threshold artifact from strict RI definition vs C498's 1.76x)	2	A	|
C698	**Bundle-C424 Size Match** (INFORMATIONAL; bundles and C424 adjacency clusters are distinct constructs; KS p < 0.001)	2	A	|
C700	**Bundle PP Exceeds Random** (MARGINAL; 1.02x effect, Fisher p < 10^-157 but median per-bundle p=0.512)	2	A	|
C702	**Boundary Vocabulary Discontinuity** (FALSIFIED; interior/boundary ratio 1.06x, p=0.207; no vocabulary cliff at RI boundaries)	1	A	|
C704	**Folio PP Pool Size** (mean 35.3 MIDDLEs per folio, 7.0x record-level; range 20-88; folio = complete PP specification)	2	A	|
C706	**B Line Viability Under Folio Filtering** (13.7% empty lines vs 78% record-level; 76.3% pairings have <=20% empty)	2	A-B	|
C708	**Inter-Folio PP Discrimination** (PP Jaccard=0.274 discriminative; CLASS Jaccard=0.830 convergent; funnel topology)	2	A-B	-> C708_inter_folio_pp_discrimination.md
C709	**Section Invariance** (all sections H/P/T 100% viable; P=0.182, T=0.293 higher than H=0.085; no dead zones)	2	A-B	
C710	**RI-PP Positional Complementarity** (d=0.12, RI slightly later in lines; effect too small for structural complementarity)	2	A	|
C712	**RI Singleton-Repeater Behavioral Equivalence** (KS p=0.16; singletons and repeaters show same positional/final-rate behavior)	2	A	|
C714	**Line-Final RI Morphological Profile** (143 unique types in 156 final positions; no morphological difference from non-final RI)	2	A	|
C716	**Cross-Folio RI Reuse Independence** (75 RI on 2+ folios; PP Jaccard ratio 1.045; reuse independent of PP context)	2	A	
C717	**PP Homogeneity Across Line Types** (PP-pure and RI-bearing lines draw from same PP pool; RI-exclusive PP is sampling artifact, null=9.4 vs obs=8.9, 106% explained; PP-pure alone recovers 90.1% of B class survival)	2	A	|
C719	**RI-PP Functional Independence** (0/6 binding tests pass; shared RI does not predict PP similarity J=0.074 vs 0.065, PP consistency ratio 1.05, adjacent PP ratio 0.99; RI and PP are orthogonal discrimination axes)	2	A	|
C721	**RI Section Sharing Trivial** (76.6% within-section vs 71.5% expected from section sizes; enrichment 1.07x trivially explained by 95/114 folios being Herbal)	2	A	
C722	**Within-Line Accessibility Arch** (B token accessibility follows nonlinear arch by within-line position; initial 0.279, medial 0.306, final 0.282; KW H=74.4, p=2.67e-15; mirrors C556 SETUP-WORK-CLOSE via morphological composition)	2	A-B	-> C722_within_line_accessibility_arch.md
C723	**Role Accessibility Hierarchy** (FQ 0.582 > EN 0.382 > AX 0.321 > CC 0.261 > FL 0.085; KW p=2.4e-10; FL and CC are near-exclusively B-internal grammar infrastructure)	2	A-B	-> C723_role_accessibility_hierarchy.md
C724	**Within-Class Suffix Accessibility Gradient** (up to 19x accessibility variation within same class from SUFFIX alone; Class 33: qokaiin=0.675 vs qokeedy=0.035; confirms C502.a three-axis filtering at individual token resolution)	2	A-B	-> C724_within_class_suffix_accessibility.md
C725	**Across-Line Accessibility Gradient** (later B folio lines have higher accessibility; rho=0.124, p=8.6e-10; 56/82 folios positive; first-third 0.276, last-third 0.306; consistent with C325 completion gradient)	2	B	-> C725_across_line_accessibility_gradient.md
C726	**Role-Position Accessibility Interaction** (aggregate arch decomposes into role-specific trajectories; CC/AX increase toward final, EN/FQ decrease; non-unanimous but morphologically explained by C590/C564 composition effects)	2	A-B	-> C726_role_position_accessibility_interaction.md
C727	**B Vocabulary Autonomy Rate** (69.3% of B token types have low-or-zero accessibility from A; 34.4% completely B-exclusive; 0% universally legal; B's structural scaffold is autonomously determined)	2	A-B	-> C727_b_vocabulary_autonomy_rate.md
C728	**PP Co-occurrence Incompatibility Compliance** (PP MIDDLE co-occurrence is non-random: 5,460 vs 5,669 null unique pairs, p<0.001; fully explained by MIDDLE incompatibility C475; 0 avoidance violations; legal-pair variance below null; lines are compatibility-valid subsets)	2	A	-> C728_pp_cooccurrence_incompatibility_compliance.md
C729	**C475 Record-Level Scope** (MIDDLE incompatibility operates perfectly at A record level; 0 violations across 19,576 pair occurrences; 15,518 within-folio avoidance pairs never appear on same line; extends C475 from AZC to A)	2	A	-> C729_c475_record_level_scope.md
C730	**PP PREFIX-MIDDLE Within-Line Coupling** (cross-token PREFIX-MIDDLE MI 0.133 vs null 0.121, p<0.001; MI ratio 2.79x between-line; may be mediated by C475 incompatibility)	2	A	-> C730_pp_prefix_middle_line_coupling.md
C731	**PP Adjacent Line Continuity** (adjacent lines share more PP MIDDLEs; Jaccard 0.102 vs 0.092 non-adjacent, ratio 1.10x, p=0.001; soft local sequential continuity)	2	A	-> C731_pp_adjacent_line_continuity.md
C732	**PP Within-Line Selection Uniformity** (no SUFFIX coherence 1.02x, no diversity anomaly effect=0.13, no folio position trajectory p=0.633; PP selection is uniform beyond incompatibility across SUFFIX/diversity/position dimensions)	2	A	-> C732_pp_within_line_selection_uniformity.md
C733	**PP Token Variant Line Structure** (whole-token co-occurrence is non-random beyond MIDDLE assignment; variant shuffle p<0.001 for both unique pairs and variance; ~38% of word-level structure from PREFIX+SUFFIX coordination; reverses MIDDLE-level uniformity finding)	2	A	-> C733_pp_token_variant_line_structure.md
C734	**A-B Coverage Architecture** (per-A-folio C502.a coverage of B folios: mean 26.1%, range 2.6-79.3%; A folio identity explains 72.0% of variance, B folio 18.1%; routing architecture, not flat)	2	A<>B	-> C734_ab_coverage_architecture.md
C735	**Pool Size Coverage Dominance** (A folio PP pool size predicts B coverage: Spearman rho=0.85, p=5e-33; pool range 20-88 MIDDLEs; relationship primarily quantitative)	2	A<>B	-> C735_pool_size_coverage_dominance.md
C736	**B Vocabulary Accessibility Partition** (0 B tokens universally legal; 34.4% never legal under any A folio; median accessibility 3 A folios; tripartite: B-exclusive 34.4%, narrow-access 33.9%, broad-access 31.7%)	2	A<>B	-> C736_b_vocabulary_accessibility_partition.md
C737	**A-Folio Cluster Structure** (A folios cluster into ~6 groups by B-coverage profile; mean pairwise correlation 0.648; specificity ratio 1.544x null; dominant standard cluster n=62 plus 5 specialized groups)	2	A<>B	-> C737_a_folio_cluster_structure.md
C738	**Union Coverage Ceiling** (all 114 A folios combined reach ~83-89% B folio coverage, never 95%; 34.4% of B vocabulary permanently B-exclusive; represents B's autonomous grammar)	2	A<>B	-> C738_union_coverage_ceiling.md
C739	**Best-Match Specificity** (every B folio has a strongly preferred A folio: all 82 show lift >1.5x, mean 2.43x, mean z=3.77; routing is directional: B folios are consumers, A folios are providers)	2	A<>B	-> C739_best_match_specificity.md
C740	**HT/UN Population Identity** (HT = UN: 4,421 types, 7,042 occ, zero delta; both defined by exclusion from 479-type grammar)	2	B/HT	-> C740_ht_un_population_identity.md
C741	**HT C475 Minimal Graph Participation** (4.6% of HT MIDDLE types in C475 graph, but 38.5% of occurrences; 95.4% too rare to test)	2	B/HT	-> C741_ht_c475_minimal_participation.md
C742	**HT C475 Line-Level Compliance** (0.69% violation rate vs 0.63% classified baseline; z=+1.74 marginal; compliance by structural sparsity)	2	B/HT	-> C742_ht_c475_compliance.md
C743	**HT Lane Segregation** (chi2=278.71, p=4e-60; OTHER +9.5pp, QO -7.7pp; HT skews toward non-standard prefixes)	2	B/HT	-> C743_ht_lane_segregation.md
C744	**HT Lane Indifference** (same-lane rate 37.7% = expected 37.9%, lift=0.994x; z=-1.66 ns; HT is lane-neutral in placement)	2	B/HT	-> C744_ht_lane_indifference.md
C745	**HT Coverage Metric Sensitivity** (coverage 31%->43% on HT removal; routing preserved r=0.85; metric artifact, not operational)	2	A<>B/HT	-> C745_ht_coverage_metric_sensitivity.md
C746	**HT Folio Compensatory Distribution** (density 15.5-47.2%, chi2=429.72; anti-correlated with coverage r=-0.376, p=0.0005)	2	B/HT	-> C746_ht_folio_compensatory_distribution.md
C747	**Line-1 HT Enrichment** (50.2% HT vs 29.8% rest, +20.3pp, d=0.99, p<10^-6; 69/82 folios positive; permutation z=11.07)	0	B/HT	-> C747_line1_ht_enrichment.md
C748	**Line-1 Step Function** (pos 1=50.2%, pos 2=31.7%, pos 3-10=27-33%; enrichment confined to single opening line)	0	B/HT	-> C748_line1_step_function.md
C749	**First-Line HT Morphological Distinction** (95.9% unique types vs 62.8% working; pch prefix 7.0% vs 1.9%; articulator 13.0% vs 9.9%; chi2=496.37)	2	B/HT	-> C749_line1_ht_morphological_distinction.md
C750	**Opening-Only HT Asymmetry** (last line 30.8% HT = interior 29.8%, p=0.50; no closing HT enrichment)	0	B/HT	-> C750_opening_only_asymmetry.md
C751	**Coverage Pool-Size Confound** (raw best-match degenerate: 2 A folios serve all 82 B; coverage~pool r=0.883; folio length->pool r=0.584; residual reveals 24 distinct A folios with content specificity)	2	A<>B	-> C751_coverage_pool_size_confound.md
C752	**No Section-to-Section Routing** (permutation test: 27/82 same-section = null 26.7, z=0.08, p=0.57; section labels are physical organization, not routing addresses; routing is vocabulary-driven)	2	A<>B	-> C752_no_section_routing.md
C753	**No Content-Specific A-B Routing** (partial r=-0.038 after size control; no granularity achieves discrimination; reframe as constraint propagation)	2	A<>B	-> C753_no_content_routing.md
C754	**Role-Aware Infrastructure Filtering** (CORE_CONTROL 95%+ survival regardless of pool size; AUXILIARY 20% under small pools; McNemar p<0.0001)	2	A<>B	-> C754_role_aware_filtering.md
C755	**A Folio Coverage Homogeneity** (real A folios at 0th percentile for discrimination vs random; deliberate coverage optimization)	2	A	-> C755_a_folio_coverage_homogeneity.md
C756	**Coverage Optimization Confirmed** (11x higher pairwise similarity than random; first 10 folios cover 60% PP; hub MIDDLEs 100% PP)	2	A	-> C756_coverage_optimization_confirmed.md
C757	**AZC Zero Kernel/Link** (0 KERNEL, 0 LINK; ~50% OPERATIONAL, ~50% UN; AZC is outside execution layer)	2	AZC	-> C757_azc_zero_kernel.md
C758	**P-Text Currier A Identity** (PREFIX cosine 0.97 to A, 0.74 to diagram; 19.5% MIDDLE overlap with same-folio diagram)	2	AZC	-> C758_ptext_currier_a_identity.md
C759	**AZC Position-Vocabulary Correlation** (position affects PREFIX: chi2=112.6, p<0.001, V=0.21; S=56% ok+ot, C=28% ch)	2	AZC	-> C759_azc_position_vocabulary.md
C760	**AZC Folio Vocabulary Specialization** (70% MIDDLEs exclusive to 1 folio; 13 universal MIDDLEs; no family pattern)	2	AZC	-> C760_azc_folio_vocabulary_specialization.md
C761	**AZC Family B-Coverage Redundancy** (Zodiac-A/C correlation r=0.90; 81/82 B folios balanced; both families contribute ~5-6 exclusive MIDDLEs per B)	2	AZC	-> C761_azc_family_b_redundancy.md
C762	**Cross-System Single-Char Primitive Overlap** (f49v/f76r/f57v share 4 chars d,k,o,r - all C085 primitives; spans PREFIX/MIDDLE/SUFFIX positions)	2	GLOBAL	-> C762_cross_system_single_char_primitives.md
C763	**f57v R2 Single-Char Ring Anomaly** (100% single chars, 0% morphology; ~27-char repeating pattern with p/f variation; m,n unique terminators; diagram-integrated unlike margin labels)	2	AZC	-> C763_f57v_r2_single_char_ring.md
C764	**f57v R2 Coordinate System** (UNIQUE to f57v across 13 Zodiac folios; p/f at 27-pos apart mark ring halves; R1-R2 1:1 token correspondence; 'x' coord-only char never in R1)	2	AZC	-> C764_f57v_coordinate_system.md
C765	**AZC Kernel Access Bottleneck** (AZC-mediated: 31.3% escape, 51.3% kernel; B-native: 21.5% escape, 77.8% kernel; AZC constrains B by limiting kernel access, not escape directly)	2	GLOBAL	-> C765_azc_kernel_access_bottleneck.md
C766	**UN = Derived Identification Vocabulary** (UN 81.1% compound vs classified 35.2%; +45.9pp; 1,251 UN-only MIDDLEs at 84.3% compound; 0 classified-only MIDDLEs)	2	B	-> C766_un_derived_vocabulary.md
C767	**Class Compound Bimodality** (21 base-only classes at 0-5% compound, 3 compound-heavy classes at 85%+; grammar has two functional vocabularies)	2	B	-> C767_class_compound_bimodality.md
C768	**Role-Compound Correlation** (FL=0% compound, FQ=46.7%; 46.7pp spread; FL uses 0 kernel chars k/h/e; role determines vocabulary type)	2	B	-> C768_role_compound_correlation.md
C769	**Compound Context Prediction** (Line-1 +5pp more compound; folio-unique correlation r=0.553; class range 0%-100%; compound structure is informative)	2	B	-> C769_compound_context_prediction.md
C770	**FL Kernel Exclusion** (FL uses 0 kernel chars k/h/e; only role with complete kernel exclusion; 17 MIDDLEs, 1,078 tokens)	2	B	-> C770_fl_kernel_exclusion.md
C771	**FL Character Restriction** (FL uses exactly 9 chars: a,d,i,l,m,n,o,r,y; excludes c,e,h,k,s,t; mean MIDDLE length 1.58)	2	B	-> C771_fl_character_restriction.md
C772	**FL Primitive Substrate** (FL provides substrate layer; other roles add kernel k/h/e then helpers c/s/t; EN 60.7% kernel-containing highest)	2	B	-> C772_fl_primitive_substrate.md
C773	**FL Hazard-Safe Position Split** (Hazard FL 88.7% at mean pos 0.546 medial; Safe FL 11.3% at mean pos 0.811 line-final; 0.265 position gap)	2	B	-> C773_fl_hazard_position_split.md
C774	**FL Outside Forbidden Topology** (FL classes not in any of 17 forbidden pairs; FL operates below hazard layer)	2	B	-> C774_fl_outside_forbidden_topology.md
C775	**Hazard FL Escape Driver** (Hazard FL 7/30 drive 98% of FL->FQ; safe FL 38/40 drive 2%; FL->FQ rate 22.5%)	2	B	-> C775_hazard_fl_escape_driver.md
C776	**Post-FL Kernel Enrichment** (59.4% of post-FL tokens have kernel chars k/h/e; confirms FL -> kernel-modulated flow pattern)	2	B	-> C776_post_fl_kernel_enrichment.md
C777	**FL State Index** (FL MIDDLEs index material state; 'i'-forms at start (0.30), 'y'-forms at end (0.94); position range 0.64; 77% state change rate)	2	B	-> C777_fl_state_index.md
C778	**EN Kernel Profile** (EN 91.9% kernel; dominant h+e (35.8%); h=59.4%, e=58.3%, k=38.6%; phase/stability operator not energy)	2	B	-> C778_en_kernel_profile.md
C779	**EN-FL State Coupling** (EN 'h' rate drops 95%->77% as FL advances early->late; early states need phase management, late states stable)	2	B	-> C779_en_fl_state_coupling.md
C780	**Role Kernel Taxonomy** (FL=0%, EN=92% h+e, FQ=46% k+e 0%h, CC=25%, AX=57%; roles partition kernel responsibilities)	2	B	-> C780_role_kernel_taxonomy.md
C781	**FQ Phase Bypass** (FQ has exactly 0% 'h'; escape routes bypass phase management using k+e only)	2	B	-> C781_fq_phase_bypass.md
C782	**CC Kernel Paradox** (Classes 10,11=0% kernel, class 17=88%; CC bifurcates into hazard sources vs hazard buffers)	2	B	-> C782_cc_kernel_paradox.md
C783	**Forbidden Pair Asymmetry** (All 17 forbidden pairs are asymmetric/directional; 0 symmetric; hazard is directed graph)	2	B	-> C783_forbidden_pair_asymmetry.md
C784	**FL/AX Hazard Immunity** (FL and AX never appear in any forbidden pair; exempt from hazard topology)	2	B	-> C784_fl_ax_hazard_immunity.md
C785	**FQ Medial Targeting** (FQ->FL routes to MEDIAL at 77.2%; escape re-injects at mid-process, not start/end)	2	B	-> C785_fq_medial_targeting.md
C786	**FL Forward Bias** (FL state transitions: 27% forward, 68% same, 5% backward; 5:1 forward:backward ratio)	2	B	-> C786_fl_forward_bias.md
C787	**FL State Reset Prohibition** (LATE->EARLY transition = 0 occurrences; full state reset is forbidden)	2	B	-> C787_fl_state_reset_prohibition.md
C788	**CC Singleton Identity** (Class 10=daiin, Class 11=ol, Class 12=k(absent), Class 17=9 ol- tokens; CC classes are specific tokens not broad categories)	2	B	-> C788_cc_singleton_identity.md
C789	**Forbidden Pair Permeability** (34% of CC->FQ transitions violate forbidden pairs; forbidden = disfavored, not prohibited)	2	B	-> C789_forbidden_pair_permeability.md
C790	**CC Positional Gradient** (Group A mean 0.469, Group B mean 0.515, p=0.045; sources earlier, targets later)	2	B	-> C790_cc_positional_gradient.md
C791	**CC-EN Dominant Flow** (CC->EN at 33% vs CC->FQ at 12%; CC primarily routes to kernel ops, not escape)	2	B	-> C791_cc_en_dominant_flow.md
C792	**B-Exclusive = HT Identity** (100% of B-exclusive vocabulary is HT/UN; 0 classified tokens are B-exclusive; all 88 classified MIDDLEs are in PP; C736's "autonomous grammar" is HT layer, not classified)	2	A<>B/HT	-> C792_b_exclusive_ht_identity.md
C793	**Residual Specificity = Vocabulary Coincidence** (the 24 residual-best A folios are those with best sample of common PP MIDDLEs; f42r dominates via 8 near-universal MIDDLEs; no content routing)	2	A<>B	-> C793_residual_specificity_is_vocabulary_coincidence.md
C794	**Line-1 Composite Header Structure** (68.3% PP for A-context declaration, 31.7% B-exclusive for folio ID; PP predicts A at 15.8x random; B-exclusive 94.1% folio-unique)	2	B/A<>B	-> C794_line1_composite_header.md
C795	**Line-1 A-Context Prediction** (PP line-1 HT predicts best-match A folio: 13.9% correct vs 0.88% random baseline, lift=15.8x)	2	A<>B	-> C795_line1_a_context_prediction.md
C796	**HT-Escape Correlation** (HT% correlates with FL%: rho=0.377, p=0.0005; high escape -> more HT; independent of AZC)	2	B/HT	-> C796_ht_escape_correlation.md
C797	**AZC-HT Inverse Relationship** (AZC% anti-correlates with HT%: rho=-0.352, p=0.0012; high AZC -> less HT; confounded by vocab size)	2	A<>B/HT	-> C797_azc_ht_inverse.md
C798	**HT Dual Control Architecture** (AZC and FL are orthogonal predictors of HT; effects additive; quadrant range 25%-37% HT)	2	GLOBAL/HT	-> C798_ht_dual_control.md
C799	**Line-1 AZC Independence** (Line-1 PP fraction and A-context prediction accuracy do NOT vary by AZC tertile; header is fixed structure)	2	B/HT	-> C799_line1_azc_independence.md
C800	**Body HT Escape Driver** (Body HT drives escape correlation: rho=0.367, p=0.0007; line-1 HT is independent: rho=0.107, p=0.35)	2	B/HT	-> C800_body_ht_escape_driver.md
C801	**Body HT Primitive Vocabulary** (80.1% PP, top MIDDLEs are C085 primitives e/ed/d/l/k/o; Jaccard overlap with line-1 = 0.122)	2	B/HT	-> C801_body_ht_primitive_vocabulary.md
C802	**Body HT LINK Proximity** (HT clusters near LINK: 2.53 vs 3.08 distance, p<0.0001; NOT near FL: 4.04 vs 3.82, p=0.056 NS)	2	B/HT	-> C802_body_ht_link_proximity.md
C803	**Body HT Boundary Enrichment** (HT rate: first=45.8%, last=42.9%, middle=25.7%; marks control block boundaries)	2	B/HT	-> C803_body_ht_boundary_enrichment.md
C804	**LINK Transition Grammar Revision** (C366 predecessor claims not confirmed; successor enrichment weak; chi2=5.1 pred NS, chi2=48.2 succ p<0.001)	2	B	-> C804_link_transition_grammar_revision.md
C805	**LINK Positional Bias (C365 Refutation)** (Mean pos 0.476 vs 0.504; first=17.2%, last=15.3%, middle=12.4%; shares HT boundary pattern)	2	B	-> C805_link_positional_bias.md
C806	**LINK-HT Positive Association** (OR=1.50, p<0.001; 38.3% of LINK are HT; HT contains 'ol' at 16.6% vs 11.7%)	2	B/HT	-> C806_link_ht_overlap.md
C807	**LINK-FL Inverse Relationship** (LINK farther from FL: 3.91 vs 3.38, p<0.0001; rho=-0.222; depleted around FL 0.67x/0.87x)	2	B	-> C807_link_fl_inverse.md
C808	**LINK 'ol' is PP MIDDLE** ('ol' appears 759x as MIDDLE, in A vocabulary; LINK PP rate 92.4%)	2	B	-> C808_link_ol_pp_middle.md
C809	**LINK-Kernel Separation** (LINK depleted of k/h/e: 0.82-0.93x; distance 1.31 vs 0.41, p<0.0001)	2	B	-> C809_link_kernel_separation.md
C810	**LINK-FL Non-Adjacency** (Direct LINK->FL rare: 0.70x expected; confirms complementary phases)	2	B	-> C810_link_fl_non_adjacency.md
C811	**FL Chaining** (FL->FL enriched 2.11x; extended escape sequences; FL->KERNEL neutral 0.86x)	2	B	-> C811_fl_chaining.md
C812	**HT Novel MIDDLE Combinations** (11.19% novel pairs; NOT C475 violation; HT in distinct combinatorial space)	2	B/HT	-> C812_ht_c475_violation.md
C813	**Canonical Phase Ordering** (LINK 0.476 -> KERNEL 0.482 -> FL 0.576; monitoring early, escape late)	2	B	-> C813_canonical_phase_ordering.md
C814	**Kernel-Escape Inverse** (KERNEL vs FL rho=-0.528; high kernel = low escape; strongest predictor)	2	B	-> C814_kernel_escape_inverse.md
C815	**Phase Position Significance** (F=70.28, p<10^-73 but eta^2=0.015; phases flexible, not rigid)	2	B	-> C815_phase_position_significance.md
C816	**CC Positional Ordering** (daiin 0.413 -> LINK 0.476 -> KERNEL -> ol 0.511 -> FL 0.576; daiin initiates loop)	2	B	-> C816_cc_positional_ordering.md
C817	**CC Lane Routing** (C600 confirmed: daiin->CHSH 90.8%, ol_derived->QO 57.4%; rapid decay by +2)	2	B	-> C817_cc_lane_routing.md
C818	**CC Kernel Bridge** (Class 17 = CC-KERNEL interface; 88% kernel chars; resolves C782 paradox)	2	B	-> C818_cc_kernel_bridge.md
C819	**CC Boundary Asymmetry** (daiin initial 27.1%; ol/ol_derived medial 85%; unlike LINK 1.23x)	2	B	-> C819_cc_boundary_asymmetry.md
C820	**CC Hazard Immunity** (0/700 forbidden; EN absorbs 99.8% hazard; CC is safe control layer)	2	B	-> C820_cc_hazard_immunity.md
C821	**Line Syntax REGIME Invariance** (All 5 roles invariant; eta^2=0.13%; confirms C124 universality)	2	B	-> C821_line_syntax_regime_invariance.md
C822	**CC Position REGIME Invariance** (REGIME affects CC frequency not placement; daiin initial-bias p=0.65)	2	B	-> C822_cc_position_regime_invariance.md
C823	**Bigram REGIME Partial Variation** (or->aiin varies 6x; daiin->CHSH invariant p=0.63)	2	B	-> C823_bigram_regime_partial_variation.md
C824	**A-Record Filtering Mechanism** (81.3% filtering confirms C502; aggregation helps usability)	2	A/B	-> C824_a_record_filtering_mechanism.md
C825	**Continuous Not Discrete Routing** (silhouette=0.124; no discrete clusters; 97.6% unique profiles)	2	A/B	-> C825_continuous_not_discrete_routing.md
C826	**Token Filtering Model Validation** (C502 CORRECT: more PP = more survival rho=+0.734; aggregation 4.45x)	2	A/B	-> C826_token_filtering_model_validation.md
C827	**Paragraph Operational Unit** (gallows-initial paragraphs: 31.8% survival, 2.8x better than lines)	2	A/B	-> C827_paragraph_operational_unit.md
C828	**PP Repetition Exclusivity** (100% PP, 0% RI within-line repeats; p=2.64e-07; confirms C498 bifurcation)	2	A	-> C828_pp_repetition_exclusivity.md
C829	**daiin Repetition Dominance** (22% of all repeats; CC trigger may encode control-loop cycle count)	2	A	-> C829_daiin_repetition_dominance.md
C830	**Repetition Position Bias** (late-biased 0.675; FINAL 12x higher than INITIAL; parameters follow identity)	2	A	-> C830_repetition_position_bias.md
C831	**RI Three-Tier Population Structure** (singletons 95.3%, position-locked ~4%, linkers 0.6%)	2	A	-> C831_ri_three_tier_structure.md
C832	**Initial/Final RI Vocabulary Separation** (Jaccard=0.010; only 4 words overlap; different PREFIX profiles)	2	A	-> C832_initial_final_ri_separation.md
C833	**RI First-Line Concentration** (1.85x in paragraph first line; 1.03x at folio level - no structure)	2	A	-> C833_ri_first_line_concentration.md
C834	**Paragraph Granularity Validation** (RI structure visible ONLY at paragraph level; validates record size)	2	A	-> C834_paragraph_granularity_validation.md
C835	**RI Linker Mechanism** (4 tokens, 12 links, 12 folios; 66.7% forward flow; f93v=5 inputs collector)	2	A	-> C835_ri_linker_mechanism.md
C838	**qo-Linker Exception** (qokoiiin doesn't follow ct-ho; may be different linkage mechanism)	2	A	-> C838_qo_linker_exception.md
C839	**RI Input-Output Morphological Asymmetry** (12+ INPUT markers vs 5 OUTPUT markers; -ry strongest OUTPUT)	2	A	-> C839_input_output_morphological_asymmetry.md
C840	**B Paragraph Mini-Program Structure** (line 1: 44.9% HT vs body 29.1%, +15.8pp, d=0.72, p<10^-20; 76% of paragraphs show enrichment)	2	B	-> C840_b_paragraph_mini_program_structure.md
C841	**B Paragraph Gallows-Initial Markers** (71.5% p/t/k/f initial; p=43.6%, t=19.3%, k=5.5%, f=3.1%; matches A paragraph structure)	2	B	-> C841_b_paragraph_gallows_initial.md
C842	**B Paragraph HT Step Function** (pos 1=45.2%, pos 2=26.5%, pos 3-5+=26-27%; -18.7pp drop at line 2; body flat)	2	B	-> C842_b_paragraph_step_function.md
C843	**B Paragraph Prefix Markers** (pch- 16.9% + po- 16.6% = 33.5% of initiators; 78-86% HT; paragraph identification vocabulary)	2	B	-> C843_b_paragraph_prefix_markers.md
C844	**Folio Line 1 Double-Header** (50.2% HT = folio header + paragraph 1 header overlap; mid-folio paragraphs 43.6% HT)	2	B	-> C844_folio_line1_double_header.md
C845	**B Paragraph Self-Containment** (no inter-paragraph linking; 7.1% both-position rate vs A's 0.6%; no ct-ho signature; symmetric topology)	2	B	-> C845_b_paragraph_self_containment.md
C846	**A-B Paragraph Pool Relationship** (no specific A→B pairing; 39 A paragraphs serve 568 B; pool-size rho=0.694; raw lift 2.49x → 1.20x controlled; relationship is pool-based not address-based)	2	A<>B	-> C846_ab_paragraph_pool_relationship.md
C847	**A Paragraph Size Distribution** (mean 4.8 lines; "only" position = 11.79 lines; Cohen's d = 0.110 vs B)	2	A	-> C847_a_paragraph_size_distribution.md
C848	**A Paragraph RI Position Variance** (middle 14.3% RI vs first 9.3%; Kruskal-Wallis p=0.001; RI line-1 concentration 3.84x)	2	A	-> C848_a_paragraph_ri_position_variance.md
C849	**A Paragraph Section Profile** (P section: 17.2% RI, 67.5% PP vs H: 8.4% RI, 42% PP; p=0.0006)	2	A	-> C849_a_paragraph_section_profile.md
C850	**A Paragraph Cluster Taxonomy** (5 clusters: short-RI 34%, long-linker 8%, standard 58%; silhouette=0.337)	2	A	-> C850_a_paragraph_cluster_taxonomy.md
C851	**B Paragraph HT Variance Validation** (delta +0.134; 76.8% positive; line 1 = 46.5% HT; validates C840)	2	B	-> C851_b_paragraph_ht_variance_validation.md
C852	**B Paragraph Section-Role Interaction** (RECIPE 44.5% EN; PHARMA 43.2% FQ; Kruskal-Wallis p<0.0001)	2	B	-> C852_b_paragraph_section_role_interaction.md
C853	**B Paragraph Cluster Taxonomy** (5 clusters: single-line 9%, long-EN 10%, standard 81%; silhouette=0.237)	2	B	-> C853_b_paragraph_cluster_taxonomy.md
C854	**A-B Paragraph Structural Parallel** (both header-body; line counts indistinguishable p=0.067; both k=5 clusters)	2	A<>B	-> C854_ab_paragraph_structural_parallel.md
C855	Folio role template (role cohesion 0.831)	2	B	-> C855_folio_role_template.md
C856	Vocabulary distribution (Gini 0.279, distributed)	2	B	-> C856_vocabulary_distribution.md
C857	First paragraph ordinariness (predicts 11.8%)	2	B	-> C857_first_paragraph_ordinariness.md
C858	Paragraph count reflects complexity (rho 0.836)	2	B	-> C858_paragraph_count_complexity.md
C859	Vocabulary convergence (14%→39% overlap)	2	B	-> C859_vocabulary_convergence.md
C860	Section paragraph organization (HERBAL 2.2 vs RECIPE 10.2)	2	B	-> C860_section_paragraph_organization.md
C861	LINK/hazard paragraph neutrality (CV < 0.21)	2	B	-> C861_link_hazard_paragraph_neutrality.md
C862	Role template verdict: hybrid model	2	B	-> C862_role_template_verdict.md
C863	Paragraph-ordinal EN subfamily gradient (qo-early, ch-late)	3	B	-> C863_paragraph_ordinal_en_gradient.md
C864	Gallows paragraph marker (81.5% gallows-initial)	2	B	-> C864_gallows_paragraph_marker.md
C865	Gallows folio position (k/f front-biased, p/t distributed)	2	B	-> C865_gallows_folio_position.md
C866	Gallows morphological patterns (k uses e, f often bare)	2	B	-> C866_gallows_morphological_patterns.md
C867	P-T transition dynamics (p stable 54%, t returns to p 50%)	2	B	-> C867_p_t_transition_dynamics.md
C868	Gallows-QO/CHSH independence (0.3% variance explained)	2	B	-> C868_gallows_qochsh_independence.md
C869	Gallows functional model (f/k openers, p/t modes)	3	B	-> C869_gallows_functional_model.md
C870	Line-1 HT folio specificity (86% singletons, 1229 Line-1-only)	2	HT	-> C870_line1_ht_folio_specificity.md
C871	HT role cooccurrence pattern (enriched FL, depleted CC/FQ)	2	HT	-> C871_ht_role_cooccurrence_pattern.md
C872	HT discrimination vocabulary interpretation	3	HT	-> C872_ht_discrimination_vocabulary.md
C873	Kernel positional ordering: e (0.404) < h (0.410) < k (0.443)	3	B	-> C873_kernel_positional_ordering.md
C874	CC token functions: daiin=init (0.370), ol=continue (0.461)	3	B	-> C874_cc_token_functions.md
C875	Escape trigger grammar: 80.4% from hazard FL stages	3	B	-> C875_escape_trigger_grammar.md
C876	LINK checkpoint function (position 0.405, routes to EN)	3	B	-> C876_link_checkpoint_function.md
C877	Role transition grammar: EN->EN 38.5%, CC->EN 37.7%, FQ->EN 29.5%	2	B	-> C877_role_transition_grammar.md
C878	Section program variation: BIO high EN, HERBAL_B high FL/FQ	2	B	-> C878_section_program_variation.md
C879	Process domain: batch processing, 59.2% forward bias	3	B	-> C879_process_domain_verdict.md
C880	Integrated control model: batch processing with escape handling	3	B	-> C880_integrated_control_model.md
C881	A Record Paragraph Structure (paragraphs not lines; RI in first line 3.84x baseline)	2	A	-> C881_a_record_paragraph_structure.md
C882	PRECISION Kernel Signature (ESCAPE+AUX shows k+e 3x baseline, suppressed h)	2	A	-> C882_precision_kernel_signature.md
C883	Handling-Type Distribution Alignment (66% CAREFUL matches 60% Brunschwig degree-2)	3	A	-> C883_handling_distribution_alignment.md
C884	PRECISION-Animal Correspondence (6 paragraphs pass kernel validation as animal candidates)	3	A	-> C884_precision_animal_correspondence.md
C885	A-B Vocabulary Correspondence (A folios provide 81% coverage for B paragraphs; single A paragraphs insufficient at 58%)	2	A-B	-> C885_ab_vocabulary_correspondence.md
C886	Transition Probability Directionality (P(A→B) uncorrelated with P(B→A), r=-0.055; symmetric constraints but directional execution)	2	B	-> C886_transition_directionality.md
C887	WITHOUT-RI Backward Reference (1.23x backward/forward asymmetry; highest overlap 0.228 when following WITH-RI)	2	A	-> C887_without_ri_backward_reference.md
C888	Section-Specific WITHOUT-RI Function (H: ct 3.87x cross-ref; P: qo/ok/ol safety protocols)	2	A	-> C888_section_specific_without_ri.md
C889	ct-ho Reserved PP Vocabulary (MIDDLEs h/hy/ho 98-100% ct-prefixed; extends C837 to PP level)	2	A	-> C889_ct_ho_reserved_vocabulary.md
C890	Recovery Rate-Pathway Independence (FQ rate and post-FQ kernel vary independently; extends C458)	2	B	-> C890_recovery_rate_pathway_independence.md
C891	ENERGY-FREQUENT Inverse Correlation (rho=-0.80; high energy = low escape operators)	2	B	-> C891_energy_frequent_inverse.md
C892	Post-FQ h-Dominance (h 24-36% post-FQ vs e 3-8%; recovery enters via phase-check)	2	B	-> C892_post_fq_h_dominance.md
C893	Paragraph Kernel Signature Predicts Operation Type (HIGH_K=2x FQ p<0.0001; HIGH_H=elevated EN p=0.036; maps to Brunschwig operation categories)	2	B	-> C893_paragraph_kernel_operation_mapping.md
C894	REGIME_4 Recovery Specialization Concentration (33% recovery-specialized folios in REGIME_4 vs 0-3% other REGIMEs; chi-sq=28.41 p=0.0001; validates C494 precision interpretation at paragraph level)	2	B	-> C894_regime4_recovery_concentration.md
C895	Kernel-Recovery Correlation Asymmetry (k-FQ: r=+0.27; h-FQ: r=-0.29; e-FQ: n.s.; phase monitoring substitutes for recovery)	2	B	-> C895_kernel_recovery_correlation.md
C896	Process Mode Discrimination via Kernel Profile (HIGH_K_LOW_H=2.5x FQ; discriminates distillation from boiling/decoction)	3	B	-> C896_process_mode_discrimination.md
C897	Prefixed FL MIDDLEs as Line-Final State Markers (tokens contain FL TERMINAL MIDDLEs am/y/dy/ly per C777; 72.7% line-final; operation→state mapping extends FL state index)	2	B	-> C897_apparatus_output_markers.md
C898	A PP Internal Structure (positional preferences p<0.0001; hub network CV=1.69; refines C234 aggregate position-freedom)	2	A	-> C898_a_pp_internal_structure.md
C899	A-B Within-Line Positional Correspondence (shared MIDDLEs have consistent within-line positions across systems r=0.654 p<0.0001; corpus-level grammar property, not folio-level mapping)	2	A↔B	-> C899_ab_positional_correspondence.md
C900	**AZC P-Text Annotation Pages** (f65v/f66v are 100% P-text, linguistically A (0.941 cosine), flanking f66r zodiac; 60%+ vocabulary overlap confirms annotation role)	2	AZC	-> C900_azc_ptext_annotation_pages.md
C901	**Extended e Stability Gradient** (e→ee→eee→eeee forms stability depth continuum; quadruple-e in 11 folios concentrated late Currier A; odeeeey = maximum observed)	2	A	-> C901_extended_e_stability_gradient.md
C902	**Late Currier A Register** (f100-f102 show distinct characteristics: p/f-domain concentration, extended vowels, short lines, MONSTERS; suggests appendix/addendum content)	2	A	-> C902_late_currier_a_register.md
C903	**Prefix Rarity Gradient** (Common ch/sh/qo vs rare ct vs very-rare qk (9 folios) vs extremely-rare qy (3 folios); rarity correlates with specialization)	2	A	-> C903_prefix_rarity_gradient.md
C904	**-ry Suffix S-Zone Enrichment (3.18x; cross-validates C839 OUTPUT marker)**	2	AZC	-> C904_ry_szone_enrichment.md
C905	**FL_TERMINAL Early-Line Concentration** (TERMINAL FL = input-state declaration, not completion marking; early>late gradient -3.7%, p=0.0005; same-section vocabulary sharing 1.30x, p<0.0001; cross-folio chaining NOT supported)	2	B	-> C905_fl_terminal_early_concentration.md
C906	**Vowel Primitive Suffix Saturation** (Vowel MIDDLEs a/e/o + END-class suffix = closed compound that suppresses further suffixation; e→98.3% suffix, edy→0.4% suffix; explains 38% of unmapped tokens)	2	GLOBAL	-> C906_vowel_primitive_suffix_saturation.md
C907	**-hy Consonant Cluster Infrastructure** (Tokens with -hy suffix form formulaic class: ch/sh prefix + consonant cluster MIDDLE + hy; 910 tokens (3.9%); connector hypothesis FALSIFIED - 0.99x boundary enrichment)	4	B	-> C907_hy_consonant_cluster_infrastructure.md
C908	**MIDDLE-Kernel Correlation** (55% of MIDDLEs significantly correlate with kernel profile; k-MIDDLEs→HIGH_K, e-MIDDLEs→HIGH_E, ch/sh→HIGH_H)	2	B	-> C908_middle_kernel_correlation.md
C909	**Section-Specific MIDDLE Vocabularies** (96% of MIDDLEs section-specific; B=k-energy, H=k+h mixed, S=e-stability, T=h-monitoring, C=infrastructure)	2	B	-> C909_section_middle_vocabulary.md
C910	**REGIME-MIDDLE Clustering** (67% REGIME-specific; REGIME_4 precision shows extreme enrichment: m=7.24x, ek=3.79x, y=2.57x)	2	B	-> C910_regime_middle_clustering.md
C911	**PREFIX-MIDDLE Compatibility Constraints** (PREFIX selects MIDDLE family; qo→k-family 4.6x, da→infra 12.8x, ch/sh→e-family 2-3x; 102 forbidden combinations)	2	B	-> C911_prefix_middle_compatibility.md
C912	**Precision Vocabulary - dam Token** (m MIDDLE 7.24x in REGIME_4; appears as `dam` 55% of cases; da- anchor prefix + no suffix; precision anchoring marker)	2	B	-> C912_precision_vocabulary_dam.md
C913	**RI Derivational Morphology** (90.9% of RI MIDDLEs contain PP as substring; extensions 71.6% single-char; 53% suffix, 47% prefix; position preferences: 'd' 89% suffix, 'h' 79% prefix, 'q' 100% prefix)	2	A	-> C913_ri_derivational_morphology.md
C914	**RI Label Enrichment** (RI 3.7x enriched in labels (27.3%) vs text (7.4%); labels identify specific illustrated items requiring instance-specific vocabulary from PP+extension system)	2	A	-> C914_ri_label_enrichment.md
C915	**Section P Pure-RI Entries** (83% of pure-RI first-line paragraphs in Section P; 23/24 single-line; mean para 7.7; da/ot/sa prefixes NOT ct-; distinct from linker system)	2	A	-> C915_section_p_pure_ri_entries.md
C916	**RI Instance Identification System** (RI functions as instance identification via PP+extension derivation; PP=category, RI=specific instance; explains A as index bridging B procedures to specific applications; labels 3.7x RI-enriched for illustration identification)	2	A	-> C916_ri_instance_identification_system.md
C917	**Extension-Prefix Operational Alignment** (h-extension→ct prefix 82% vs 0% for others; chi-square=404.9, p=4.70e-90; mirrors B's ct+h linker signature 75%; k/t→qo 30-46%; secondary: o→ct 5.1x, l→da 3.1x, s→sh 3.1x)	2	A↔B	-> C917_extension_prefix_alignment.md
C918	**Currier A as Operational Configuration Layer** (A provides context-specific material variants via RI=PP+extension; extensions encode operational context: h=monitoring, k=energy, t=terminal, d=transition; A parameterizes B's generic procedures)	2	A↔B	-> C918_currier_a_operational_configuration.md
C919	**d-Extension Suffix Exclusion** (d-extension categorically excludes -y suffix family: 0% rate vs 46-83% for all other extensions; takes -iin/-al instead; indicates END-class grammatical behavior)	2	A	-> C919_d_extension_suffix_exclusion.md
C920	**f57v R2 Extension Vocabulary Overlap** (92% of R2 chars are extension characters; only 'x' non-extension per C764; 'h' categorically absent)	2	AZC	-> C920_f57v_r2_extension_vocabulary.md
C921	**f57v R2 Twelve-Character Period** (exact 12-char period with 4 cycles + 2-char terminal; 10/12 positions invariant; only positions 7-8 variable: k/m and f/p)	2	AZC	-> C921_f57v_r2_twelve_char_period.md
C922	**Single-Character AZC Ring h-Exclusion** (single-char rings 1.9% h vs multi-char 7.4%; Fisher p=0.023; systematic under-representation of monitoring context in reference content)	2	AZC	-> C922_single_char_ring_h_exclusion.md
C923	**Label Extension Bifurcation (r/h Axis)** (r-extension 4.9x enriched in labels p<0.0001; h-extension 0% in labels across 11 folios p=0.0002; broader ID/OP groupings NOT confirmed - only r/h strongly differentiate; n=87 labels)	2	A	-> C923_label_extension_bifurcation.md
C924	**HT-RI Shared Derivational Morphology** (HT MIDDLEs 97.9% contain PP; 15/16 extension chars overlap with RI; same derivational system, different PREFIX layer; HT_PREFIX + [PP+ext] vs A/B_PREFIX + [PP+ext])	2	GLOBAL	-> C924_ht_ri_shared_derivation.md
C925	**B Vocabulary Morphological Partition** (B-exclusive 66% has kernel density ~1.0; RI bases 20% have density 0.76; A's RI derivation draws selectively from lower-density subset; morphological not semantic partition per C522)	2	B, A↔B	-> C925_b_vocabulary_morphological_partition.md
C926	**HT-RI Line-Level Anti-Correlation** (RI 0.48x in lines with HT; chi2=105.83 p<0.0001; same derivational system but partition space; HT tracks complexity, RI encodes instances; complementary not coordinated)	2	A	-> C926_ht_ri_anti_correlation.md
C927	**HT Elevation in Label Contexts** (HT 45.0% in labels vs 18.6% in paragraphs; 2.42x enrichment chi2=107.33 p<0.0001; INCONSISTENT with C926 prediction; labels use HT vocabulary for identification, not spare capacity)	2	A, HT	-> C927_ht_label_elevation.md
C928	**Jar Label AX_FINAL Concentration** (jar PP bases 35.1% AX_FINAL vs 16.7% baseline; 2.1x enrichment chi2=30.15 p=4e-08; jar labels identify materials B deploys at boundary/completion positions; content labels show only 1.14x AX enrichment)	2	A, B, Labels	-> C928_jar_label_ax_final_concentration.md

---

# All Explanatory Fits

**Source:** `context/MODEL_FITS/FIT_TABLE.txt`

# FIT_TABLE.txt - Programmatic Fit Index
# WARNING: No entry in this file constrains the model.
# Generated: 2026-02-05
# Total: 55 fits
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

---

# Tier 3-4 Interpretations

**Source:** `context/SPECULATIVE/INTERPRETATION_SUMMARY.md`

# Speculative Interpretation Summary

**Status:** SPECULATIVE | **Tier:** 3-4 | **Version:** 4.63

---

## Purpose

This document consolidates all Tier 3-4 interpretations into a single reference. It is designed for external AI context loading.

**Critical:** Everything in this document is NON-BINDING speculation. It is consistent with the structural evidence but NOT proven by it. Treat as discardable if contradicted by new evidence.

---

## Frozen Conclusion (Tier 0 - Context Only)

> The Voynich Manuscript's Currier B text encodes a family of closed-loop, kernel-centric control programs designed to maintain a system within a narrow viability regime, governed by a single shared grammar.

This structural finding is FROZEN. The interpretations below attempt to explain what this structure might have been FOR.

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

### Component-to-Class Mapping

| Component | Encodes | Classes | Evidence |
|-----------|---------|---------|----------|
| **PREFIX** | Operation domain | 4 classes selecting MIDDLE families | C911: 102 forbidden combinations |
| **SISTER** | Operational mode | 2 modes (precision/tolerance) | C412 anticorrelation |
| **MIDDLE** | Operation type | 3 families (k-energy, e-stability, h-monitoring) | C908-C910: kernel/section/REGIME correlation |
| **SUFFIX** | Two-axis marker | A/B system role + material class | C283, C495, C527 |

### PREFIX-MIDDLE Selection (C911 - Tier 2)

PREFIX and MIDDLE are **not independent**. Each PREFIX selects which MIDDLE family is grammatically legal:

| PREFIX Class | Selects For | Enrichment | Forbidden From |
|--------------|-------------|------------|----------------|
| **qo-** | k-family (k, ke, t, kch) | 4.6-5.5x | e-family, infrastructure |
| **ch-/sh-** | e-family (edy, ey, eey) | 2.0-3.1x | k-family, infrastructure |
| **da-/sa-** | infrastructure (iin, in, r, l) | 5.9-12.8x | All operational MIDDLEs |
| **ot-/ol-** | h-family (ch, sh) | 3.3-6.8x | k-family |
| **ok-** | e-family + infra | 2.6-3.3x | k-family |

**102 forbidden combinations** where expected ≥5 but observed = 0 (e.g., qo+ey, da+edy, ok+k).

This is **grammatical agreement**, not free combination. PREFIX determines the operation domain; MIDDLE specifies within that domain.

**SUFFIX Two-Axis Model (revised 2026-01-24):**

Suffix operates on two orthogonal dimensions:

| Axis | Scope | Finding | Tier |
|------|-------|---------|------|
| System role | A vs B enrichment | -edy 49x B, -ol 0.35x A-enriched | 2 (C283) |
| Material class | Within A: animal vs herb | Animal: 78% -ey/-ol; Herb: 41% -y/-dy | 3 (C527) |

The earlier "decision archetype (D1-D12)" mapping in ccm_suffix_mapping.md is **provisional and incomplete**. The fire-degree interpretation (C527) is conditional on Brunschwig alignment.

### Material-Behavior Classes (Revised with C911)

| Class | Prefixes | Selects MIDDLE Family | Brunschwig Parallel |
|-------|----------|----------------------|---------------------|
| **Energy** | qo | k-family only | Heating, distillation |
| **Stability** | ch, sh | e-family only | Cooling, settling |
| **Monitoring** | ot, ol, ok | h-family, e-family | Phase checking, output |
| **Infrastructure** | da, sa | iin/in/r/l only | Anchors, connectors |

The earlier M-A/B/C/D classification is superseded by this operation-domain model. PREFIX class determines which operations (MIDDLEs) are grammatically permitted.

### MIDDLE Semantic Families (C908-C910 - Tier 2)

MIDDLEs encode **operation types**, not just variant identity. Three functional families emerge from kernel correlation, section distribution, and REGIME clustering:

| Family | MIDDLEs | Kernel Profile | Section Concentration | Function |
|--------|---------|---------------|----------------------|----------|
| **k-family** | k, ke, ck, ek, eck, kch, lk | HIGH_K (1.3-1.6x) | B (bathing) 1.5-2x | Heating, energy input |
| **e-family** | e, ed, eed, eo, eeo, eod, eey | HIGH_E (1.2-1.6x) | S (recipes) 1.3-1.7x | Cooling, stabilization |
| **h-family** | ch, sh, pch, opch, d | HIGH_H (1.2-1.6x) | T (text) 1.7-4x | Phase monitoring |

**Evidence strength:**
- 55% of MIDDLEs significantly correlate with kernel profile (C908)
- 96% of MIDDLEs are section-specific (C909)
- 67% of MIDDLEs are REGIME-specific (C910)

### Section-MIDDLE Alignment (C909 - Tier 2)

Manuscript sections use systematically different MIDDLE vocabularies, validating content interpretation:

| Section | Content | MIDDLE Profile | Brunschwig Interpretation |
|---------|---------|---------------|---------------------------|
| **B** (Bathing) | Human figures in tubs | k-enriched 1.5-2x | Balneum marie (water bath heating) |
| **H** (Herbal) | Plant illustrations | Mixed k+h | Extraction (heat + phase monitoring) |
| **S** (Recipes) | Recipe-like text | e-enriched 1.3-1.7x | Final products, stabilization |
| **T** (Text) | Text-only pages | h-enriched 1.7-4x | Instructions, procedures |
| **C** (Cosmological) | Diagrams | Infrastructure | Relational, connectors |

The "bathing figures" are not people bathing - they are **vessels in water baths** (balneum marie), the gentlest distillation method. The k-MIDDLE enrichment confirms heating operations.

### Precision Vocabulary (C912 - Tier 2)

The `m` MIDDLE (7.24x enriched in REGIME_4 precision folios) appears almost exclusively as the token `dam`:

| Property | Value |
|----------|-------|
| Form | `dam` = da (anchor) + m + ø (no suffix) |
| Frequency | 55% of all m-MIDDLE tokens |
| Section | Herbal 41% (precision extraction) |
| Function | Precision anchoring / verification marker |

This is a **specific lexical item**, not a productive pattern. It marks precision verification steps in quality-critical procedures.

### Two-Level Grammar Constraint (C908-C911)

Grammar operates at two levels with different constraint profiles:

| Level | Unit | Constraint Type | Freedom |
|-------|------|-----------------|---------|
| **Paragraph** | Multi-token sequence | Co-occurrence | Nearly free (585 positive pairs, 1 negative) |
| **Token** | PREFIX + MIDDLE | Morphological selection | Tight (102 forbidden combinations) |

**Interpretation:** A paragraph is a **recipe** containing multiple operation types. Individual tokens are **single operations** constrained to compatible PREFIX+MIDDLE combinations. You can have heating AND cooling in the same paragraph (different tokens), but a single qo- token cannot encode a cooling operation.

### Operational Modes (Sister Pairs)

| Sister | Mode | Escape Density | Meaning |
|--------|------|----------------|---------|
| **ch** (vs sh) | Precision | 7.1% | Tight tolerances, fewer recovery options |
| **sh** (vs ch) | Tolerance | 24.7% | Loose tolerances, more escape routes |

Statistical validation: rho = -0.326, p = 0.002 (C412)

### LATE Prefixes as Output/Completion Phase (Tier 3)

The V+L prefixes (al, ar, or) may function as output/completion markers within line-level control loops:

| Prefix | Position | Suffix-Less | Interpretation |
|--------|----------|-------------|----------------|
| al | 0.692 | 43.9% | Output marker |
| ar | 0.744 | 68.4% | Terminal form |
| or | 0.664 | 70.5% | Terminal form |

**Structural evidence (C539, Tier 2):**
- 3.78x enrichment at absolute line end
- V+L morphology distinct from consonantal ENERGY prefixes
- Short MIDDLE preference (om, am, y enriched)
- When not line-final, followed by ENERGY prefixes (cycle reset)

**Interpretive hypothesis (Tier 3):**
- EARLY position (ENERGY prefixes) = Initialize energy state
- MIDDLE position (mixed roles) = Monitor and intervene
- LATE position (V+L prefixes) = Record output / mark completion

This interpretation is consistent with closed-loop control semantics where each line represents a control cycle: setup → work → output. The V+L morphology may be phonologically motivated (easier articulation at phrase boundaries).

**Contrast with ol:** Despite sharing V+L morphology, ol sits at MIDDLE position (0.560) and has only 27.8% suffix-less rate (below baseline). ol is CORE_CONTROL, not LATE class. V+L pattern is necessary but not sufficient.

### L-compound as Modified Energy Operators (Tier 3)

L-compound operators (lch, lk, lsh) are structurally `l` + energy operator root (C298.a):

| Pattern | Count | Interpretation |
|---------|-------|----------------|
| lch = l + ch | 74 | Modified ch operation |
| lk = l + k | 58 | Modified k operation |
| lsh = l + sh | 24 | Modified sh operation |

**Positional shift:** The `l` modifier moves energy operations earlier in line (lch 0.344 vs ch 0.483). This may represent "pre-positioned" or "setup" energy operations before the main working phase.

**Provenance contrast with LATE:**
- L-compound: Fully B-internal (97% exclusive tokens, 86% exclusive MIDDLEs)
- LATE: B-prefix on PP vocabulary (85% exclusive tokens, 76% PP MIDDLEs)

L-compound is B's own infrastructure; LATE marks pipeline content at boundaries.

### Folio Program Type Differentiation (Tier 3)

L-compound rate and LATE rate show negative correlation (r = -0.305) at folio level:

| Folio Type | Example | L-compound | LATE | ENERGY |
|------------|---------|------------|------|--------|
| Control-intensive | f83v | 4.94% | 0.00% | High |
| Output-intensive | f40r | 0.00% | 6.19% | Lower |

**REGIME correlation:**
- REGIME_1/3: Higher L-compound (1.2-1.6%), higher ENERGY (48-50%), lower LATE
- REGIME_2/4: Lower L-compound (0.7-1.0%), lower ENERGY (35-38%), higher LATE

This suggests folios differ not just in content but in **control architecture**: some programs emphasize active control (L-compound heavy), others emphasize output recording (LATE heavy).

**Note:** Symmetric bracketing hypothesis (L-compound + LATE as line brackets) was tested and **falsified** - co-occurrence ratio 0.95x (independent), bracket order only 67.4%.

### Grammar Infrastructure Allocation by Section (Tier 3)

REGIME classifications reflect **grammar infrastructure allocation**, orthogonal to C494's execution precision axis:

| REGIME | L-compound | Kernel | LATE | Profile |
|--------|------------|--------|------|---------|
| REGIME_1 | 2.35% | 16.8% | 1.37% | Control-infrastructure-heavy |
| REGIME_2 | 0.32% | 10.2% | 3.14% | Output-intensive |
| REGIME_4 | 0.87% | 14.0% | 1.98% | Balanced |

**Section B Concentration (70% REGIME_1):**

| Section | REGIME_1 | REGIME_2 | REGIME_4 | Interpretation |
|---------|----------|----------|----------|----------------|
| B (balneological) | 70% | 5% | 10% | Control-heavy |
| H (herbal) | 13% | 31% | 44% | Output-distributed |
| S (stellar) | 17% | 35% | 43% | Output-distributed |

Section B (traditionally "bathing figures") concentrates in REGIME_1, suggesting these folios document procedures requiring:
- Heavy control infrastructure (L-compound, kernel)
- Active intervention (16.8% kernel contact per line)
- Modified energy operations (L-compounds enriched 2.6-7.5x)

**Enriched MIDDLEs in REGIME_1:**
- lsh: 7.51x, lch: 4.38x, lk: 2.61x (L-compound family)
- ect: 4.66x, ct: 2.31x (control operators)

**Fire-degree distributes by Section, not REGIME:**

| Section | High-Fire | Low-Fire | Ratio |
|---------|-----------|----------|-------|
| H | 3.9% | 17.8% | 0.22 (lowest) |
| B | 7.5% | 19.4% | 0.39 |
| S | 7.1% | 15.2% | 0.47 |
| C | 6.1% | 12.9% | 0.48 (highest) |

**Orthogonality with C494:** This classification (grammar composition) is independent of C494's precision axis (execution requirements). A folio can be both high-precision (C494 REGIME_4) AND control-infrastructure-heavy (this analysis REGIME_1).

**Source:** REGIME_SEMANTIC_INTERPRETATION phase (2026-01-25)

### MIDDLE Frequency Structure

| Tier | MIDDLEs | Usage | Properties |
|------|---------|-------|------------|
| **Core** (top 30) | 30 | 67.6% | Mode-flexible, section-stable, cross-class |
| **Tail** | 1,154 | 32.4% | Mode-specific, hazard-concentrated, class-exclusive |

Key findings:
- Rare MIDDLEs cluster in high-hazard contexts (rho=-0.339, p=0.0001)
- Core MIDDLEs are 15x more rank-stable across sections
- Distribution is Zipf-like (s=1.26) with cutoff — bounded expert vocabulary

### Semantic Ceiling

**Recoverable internally (role-level):**
- What material-behavior class is involved
- What operational mode applies
- Which variant within the class
- What decision archetype is needed

**Irrecoverable internally (entity-level):**
- Specific substances, plants, or minerals
- Specific apparatus or devices
- Specific procedures or recipes
- What any token "means" in natural language

This is the terminal internal semantic layer. The boundary is by design.

**Semantic Ceiling Gradient (C499, v4.31):**

The ceiling has layers - not all irrecoverable information is equally irrecoverable:

| Level | Recoverability | Method |
|-------|----------------|--------|
| Entity identity (lavender) | IRRECOVERABLE | - |
| Material CLASS priors | **PARTIALLY RECOVERABLE** | Bayesian inference via procedural context |
| Procedural context | RECOVERABLE | Folio classification, product type |

**Conditional recovery (IF Brunschwig applies):**
- 128 registry-internal MIDDLEs with full P(material_class) vectors
- 27 tokens with P(animal) = 1.00 (PRECISION-exclusive)
- Mean entropy: 1.08 bits (86% match null baseline)

The distinction is epistemological, not ontological: the system MAY encode specific materials, we just can't recover WHICH.

### Why This Matters

The apparatus-centric perspective explains:
- Why vocabulary is universal across sections (comparability over specificity)
- Why no quantities appear (apparatus tracks state, not magnitude)
- Why illustrations look botanical but grammar does not (images are human context; text is control logic)
- Why ~1,184 MIDDLEs exist (expert recognition vocabulary, not linguistic labels)

---

## 0.A. CURRIER A COGNITIVE INTERFACE (PCC Phase) - NEW in v4.24

### Tier 3: Core Finding

> **Currier A is designed for expert navigation without meaning - a human-facing complexity-frontier registry with cognitive affordances optimized for working memory.**

This extends the Complexity-Frontier Registry model with empirical characterization of how humans would interact with the system.

### Closure State Architecture

Boundary tokens are **closure states**, not delimiters:

| Property | Finding |
|----------|---------|
| Function | Return vocabulary to neutral, maximally compatible state |
| -y ending | 36.5% at final position |
| -n ending | 15.2% at final position |
| -m ending | 12.2% at final position |
| Uniformity | NOT adjusted to entry complexity (no complexity correlation) |

Closure markers signal that an entry has emitted all discriminating vocabulary, enabling cognitive bracketing without punctuation.

### Working-Memory Chunks

Adjacent entries form **working-memory-sized clusters**:

| Metric | Value |
|--------|-------|
| Within-cluster coherence | 2.14x vs cross-cluster |
| Median cluster size | 2 |
| Max cluster size | 7 (working memory limit) |
| Cohen's d | 1.44 (large effect) |

Clusters are INVARIANT under folio reordering - this is local structure, not global organization.

### Singleton Isolation

Entries not in clusters (singletons) show distinct properties:

| Property | Clustered | Singleton |
|----------|-----------|-----------|
| Hub overlap | 0.850 | 0.731 |
| Incompatibility density | 0.979 | 0.986 |

Singletons are **deliberate isolation points**, not noise - entries with unique discrimination profiles that cannot cluster.

### A-AZC Breadth Interface

Entry vocabulary composition predicts downstream AZC compatibility:

| Factor | Effect on Breadth | p-value |
|--------|-------------------|---------|
| Hub-dominant | Broader | - |
| Tail-dominant | Narrower | <0.0001 |
| Closure present | Slightly broader | 0.003 |
| Non-prefix opener | Narrower | <0.0001 |

**Strong asymmetry:** Universal-dominant entries have 0.58 breadth; Tail-dominant entries have 0.31 breadth.

### The Navigation Model (Tier 3)

An expert using Currier A would:
1. Recognize entry boundaries via closure morphology
2. Process clusters as working-memory chunks
3. Use adjacency similarity for local orientation
4. Treat singletons as special/isolated items
5. Navigate via marker class organization

This is interface characterization, not semantic mapping. The system supports expert navigation without encoding meaning.

### What This Does NOT Claim

- ❌ Entries have semantic content
- ❌ Closure markers are adaptive signals
- ❌ Working-memory structure implies temporal ordering
- ❌ A-AZC breadth enables material identification

### Cross-References

| Constraint | Finding |
|------------|---------|
| C233 | LINE_ATOMIC (base for closure model) |
| C346 | Sequential coherence 1.20x |
| C424 | Clustered adjacency |
| C422 | DA articulation |

**Source:** phases/POST_CLOSURE_CHARACTERIZATION/PCC_SUMMARY_REPORT.md

---

## 0.A.1. RI INSTANCE IDENTIFICATION SYSTEM (RI_EXTENSION_MAPPING Phase) - NEW in v4.60

### Tier 2/3: Core Finding

> **RI vocabulary functions as an instance identification system built via derivational morphology from PP vocabulary. PP encodes general categories shared with B execution; RI extends PP with single-character markers to identify specific instances. This explains A's purpose as an index bridging general procedures (B) to specific applications (labels, illustrated items).**

This resolves the fundamental question: "Why does Currier A exist if Currier B is self-sufficient for execution?"

### The Three-Level Model

| Level | Vocabulary | Function | Example |
|-------|-----------|----------|---------|
| **B (Execution)** | PP only | General operations | "Process 'od' at temperature 'kch'" |
| **A (Registry)** | PP + RI | Specific instances | "Entry for 'odo': follow procedure X" |
| **Labels** | RI-enriched (3.7x) | Illustration pointers | "This drawing = 'odo'" |

### The Derivational System

RI is built from PP through single-character extensions:

```
PP MIDDLE 'od' (category: herb/material class)
     |
     +-- 'odo' (instance 1) - used in label
     +-- 'oda' (instance 2) - used in text
     +-- 'odd' (instance 3) - used in text
```

**Structural evidence:**
- 90.9% of RI MIDDLEs contain PP as substring (C913)
- 71.6% of extensions are single characters
- Position preferences exist: 'd' is 89% suffix, 'h' is 79% prefix

### Dual-Use Pattern

225 PP MIDDLEs appear both directly AND as RI bases, demonstrating the category/instance distinction:

| PP MIDDLE | Direct Uses | As RI Base | Interpretation |
|-----------|-------------|------------|----------------|
| 'od' | 191 | 23 | Category AND instances |
| 'eo' | 211 | 14 | Category AND instances |
| 'ol' | 790 | 4 | Mostly category |

### Why Labels Are RI-Enriched (3.7x)

Labels point to **specific illustrated items**, not general categories:
- Text: 7.4% RI (discusses general procedures)
- Labels: 27.3% RI (points to THIS plant, not plants in general)

The derivational system provides the instance-specificity labels require.

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
  - RI-enriched for instance-specificity
```

### What This Resolves

| Question | Answer |
|----------|--------|
| Why does A exist if B is self-sufficient? | A indexes specific applications of general B procedures |
| Why are labels RI-enriched? | Labels point to specific illustrated items |
| What is RI vocabulary? | Instance identifiers derived from PP categories |
| How do A and B relate? | Same conceptual vocabulary, different granularity |

### What This Does NOT Claim

- X Specific substance identification is possible
- X Extension characters have recoverable meanings
- X Labels are translatable
- X RI encodes semantic content beyond instance differentiation

### Cross-References

| Constraint | Finding |
|------------|---------|
| C240 | A = Registry - now explains the indexing mechanism |
| C913 | RI Derivational Morphology |
| C914 | RI Label Enrichment (3.7x) |
| C915 | Section P Pure-RI Entries |
| C916 | RI Instance Identification System (synthesis) |

**Source:** phases/RI_EXTENSION_MAPPING/README.md

---

## 0.A.2. LABEL-TO-B PIPELINE (LABEL_INVESTIGATION Phase) - NEW in v4.62

### Tier 2/3: Core Finding

> **Labels connect to B through shared PP vocabulary, with jar labels specifically concentrating in AX_FINAL (material-carrying) positions at 2.1x baseline rate. This validates the three-level model: Labels identify materials that B procedures operate ON.**

### The Complete Pipeline

```
ILLUSTRATION
     |
     v
LABEL (uses RI/PP vocabulary)
  - Jar labels: container identifiers (35.1% AX_FINAL in B)
  - Content labels: material identifiers (roots, leaves)
     |
     v
PP BASE (shared with B)
  - 97.9% of labels connect to B vocabulary
  - 104 unique PP bases from 192 labels
     |
     v
B PROCEDURE (deploys PP in roles)
  - AX_FINAL: maximum scaffold depth (material specification)
  - EN: operational positions
```

### Jar vs Content Distinction

| Label Type | B Connection | AX_FINAL Rate | Function |
|------------|--------------|---------------|----------|
| **Jar** | PP bases in B | **35.1%** (2.1x) | Container/configuration identifier |
| **Content** | PP bases in B | 19.1% (1.14x) | Material identifier (root, leaf) |
| B Baseline | - | 16.7% | Reference |

Jar labels are statistically significant (chi2=30.15, p=4e-08); content labels show moderate enrichment.

### What This Validates

| Finding | Significance |
|---------|--------------|
| **C571 confirmed** | PREFIX selects role, MIDDLE carries material identity |
| **Labels are functional** | They point to materials that B operates on |
| **AX_FINAL = material slot** | Per C565, maximum scaffold depth = where materials are specified |
| **Cross-system coherence** | A (labels) -> B (procedures) uses shared vocabulary in predictable positions |

### The Jar-to-AX_FINAL Interpretation

```
JAR LABEL "okaradag" (f99r)
     |
     v
PP BASE "ara" (extracted MIDDLE)
     |
     v
B TOKEN "ot-ara-y" appearing in AX_FINAL position
     = "the thing being processed"
```

Jar labels identify materials at **maximum scaffold depth** - the boundary/completion position where material identity is specified without operational modification. This is where you'd expect "what to process" to appear.

### What This Does NOT Claim

- X Specific jar-to-procedure mappings are recoverable
- X Label translations are possible
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

**Source:** phases/LABEL_INVESTIGATION/README.md

---

## 0.B. PP FUNCTIONAL ROLE CLOSURE (PP_B_EXECUTION_TEST Phase) - NEW in v4.33

### Tier 2: Core Finding

> **PP (Pipeline-Participating) MIDDLEs have a two-level effect: COUNT determines class survival breadth, COMPOSITION determines intra-class token configuration.**

This resolves both the C505 paradox (material-class PP differentiation with null class-level effects) and the "480 token paradox" (why maintain 480 tokens if 49 classes suffice).

### The Two-Level PP Effect (C506, C506.a)

| Level | What PP Determines | Evidence |
|-------|-------------------|----------|
| **Class** | Which instruction types survive | COUNT matters (r=0.715), COMPOSITION doesn't (cosine=0.995) |
| **Token** | Which variants within classes are available | COMPOSITION matters (Jaccard=0.953 when same classes) |

**Variable taxonomy:**

| Variable Type | System | What It Does | Evidence |
|---------------|--------|--------------|----------|
| **Routing** | AZC | Position-indexed legality | C443, C468 |
| **Differentiation** | RI | Identity exclusion (95.7% incompatibility) | C475, C481 |
| **Capacity** | PP | Class survival breadth (count) | C504, C506 |
| **Configuration** | PP | Intra-class token selection (composition) | C506.a |

**Key insight:** Classes are instruction types; tokens are parameterized variants.

### Evidence Summary

| Test | Result | Interpretation |
|------|--------|----------------|
| PP count vs B class survival | r=0.715, p<10^-247 | COUNT determines class breadth |
| PP composition vs B class mix | Cosine=0.995 | COMPOSITION irrelevant at class level |
| PP composition vs token availability | Jaccard=0.953 | COMPOSITION matters at token level (~5% variation) |
| Per-class survival | 0/49 significant | No individual class differs |

### PP Count Gradient (Class Level)

| PP Count | Mean B Classes | n |
|----------|----------------|---|
| 0-2 | 19.0 | 171 |
| 3-5 | 30.9 | 805 |
| 6-8 | 37.2 | 525 |
| 9-11 | 41.4 | 64 |
| 12-15 | 43.9 | 13 |

### Resolution of the 480 Token Paradox

Why maintain 480 distinct tokens across 49 classes?

Answer: **Intra-class behavioral parameterization.**

- The 49 classes provide the operational grammar (what instructions exist)
- The ~480 tokens provide behaviorally distinct variants (how each instruction executes)
- PP COUNT determines class survival breadth (how many instruction types)
- PP COMPOSITION determines intra-class configuration (which behavioral variants)

Animal materials don't need different *classes* than plant materials — they need different *execution flows* within the same class structure. C505's PP profile differences shape which behavioral variants are available, not which classes survive.

### Intra-Class Behavioral Heterogeneity (C506.b, v4.36)

Tokens within the same class but with different MIDDLEs are **positionally compatible but behaviorally distinct**:

| Dimension | Same-MIDDLE | Different-MIDDLE | p-value |
|-----------|-------------|------------------|---------|
| Position | Similar | Similar | 0.11 (NS) |
| Transitions | Similar | **Different** | <0.0001 |

73% of MIDDLE pairs within classes have transition JS divergence > 0.4.

**The "Chop vs Grind" Pattern:**

Like "chop" and "grind" in a recipe:
- Both appear in the same grammatical slot (positionally compatible)
- But they lead to different subsequent operations (behaviorally distinct)

Classes define **grammatical equivalence** (what can substitute syntactically), not **semantic equivalence** (what does the same thing operationally).

**Implication for PP composition:**

```
PP composition → MIDDLE selection → transition pattern variation
                                  → execution flow differences
                                  (within fixed class structure)
```

The ~5% token variation (C506.a) is **behaviorally meaningful**, not noise.

### What C505 Actually Means (Revised)

C505's material-class PP profile differences are **configuration markers**:

> PP profiles shape which token variants are available within surviving classes.

PP profile variation allows:
- Material-specific parameterization within shared class framework
- Same operational grammar, different execution variants
- Structural adaptation without semantic encoding

### Why Class-Level Null Effects Are Correct

The class-level null results (C506) protect the semantic ceiling (C171, C469):

- If PP composition caused different *classes* to survive → PP would encode material-specific instruction sets
- Material-specific instruction sets → violates PURE_OPERATIONAL constraint
- Therefore: class-level null effects are architecturally necessary

But token-level variation (C506.a, C506.b) is permitted:
- Same classes, different behavioral variants
- Structural adaptation without changing the instruction vocabulary
- This is parameterization, not semantic encoding

### What This Closes

- PP composition → class survival: **FALSIFIED** (C506)
- PP composition → token configuration: **CONFIRMED** (C506.a)
- PP composition → behavioral variation: **CONFIRMED** (C506.b)
- PP functional characterization: **COMPLETE** (two-level model)

### PP-HT Responsibility Substitution (C507, v4.34)

**Resolved:** PP capacity is weakly but significantly inversely correlated with HT density.

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Spearman rho | **-0.294** | Moderate negative |
| p-value | **0.0015** | Highly significant |
| PP 0-3 HT density | 18.83% | High HT when low PP |
| PP 6+ HT density | 12.62% | Low HT when high PP |
| PP vs HT TTR | **+0.40** | More varied HT with more PP |

**Two-axis HT model:**
1. **HT density axis** — how much HT appears (negatively correlated with PP)
2. **HT diversity axis** — how varied HT is when it appears (positively correlated with PP)

**Interpretation:** PP and HT partially substitute in a "responsibility budget." More grammatical freedom (PP capacity) correlates with less human vigilance (HT density) but more varied vigilance (HT TTR).

This is NOT:
- Complete substitution (r = -0.29, not -0.8)
- HT tracking PP content (composition doesn't matter per C506)
- Causal relationship (correlation only)

### What Remains Open

The next frontier is **PP × HT × AZC three-way interaction**:
- Does AZC position modulate the PP-HT trade-off?
- Does PP count increase operator error tolerance?
- Regime-specific HT compensation patterns

This shifts from "what PP is" to "what the artifact does to the human."

### Cross-References

| Constraint | Role |
|------------|------|
| C504 | PP count correlation (r=0.772) |
| C505 | A-side profile differences |
| C506 | Non-propagation to B |
| C507 | PP-HT partial substitution |
| C171 | Semantic ceiling protection |
| C469 | Categorical resolution |

**Source:** PP_B_EXECUTION_TEST (2026-01-23), PP_HT_INTERACTION_TEST (2026-01-23)

---

## 0.C. THREE-LAYER CONSTRAINT ARCHITECTURE (MIDDLE_SUBCOMPONENT_GRAMMAR Phase) - NEW in v4.38

### Tier 2-3: Architectural Discovery

> **The manuscript's symbol system operates through three independent constraint layers sharing a single substrate - construction, compatibility, and execution - which together achieve complex morphology, extreme vocabulary sparsity, AND execution safety simultaneously.**

### The Problem This Solves

Prior analysis identified multiple constraint regimes:
- C085: 10 kernel primitives (s, e, t, d, l, o, h, c, k, r)
- C109: 17 forbidden transitions between token classes
- C475: 95.7% of MIDDLE pairs are incompatible
- C517: Superstring compression with hinge letters

The question: Are these the same constraint seen at different scales, or independent systems?

### Key Evidence (Test 17)

**Hypothesis tested:** Construction constraints (within-token) are isomorphic to execution constraints (between-token).

**Result:** FALSIFIED

| Metric | Value |
|--------|-------|
| Pearson correlation | r = -0.21 |
| p-value | 0.07 (not significant) |
| Category match rate | 28.4% (near random) |

Construction-suppressed pairs: only 2.9% also suppressed in execution.
Construction-elevated pairs: 0% also elevated in execution.

### Three-Layer Architecture

```
SYMBOL SUBSTRATE (10 primitives: s,e,t,d,l,o,h,c,k,r)
         |
         ├── CONSTRUCTION LAYER (C521)
         |     - Directional asymmetry within tokens
         |     - One-way valve: e→h blocked (0.00), h→e favored (7.00x)
         |     - Result: Legal token forms
         |
         ├── COMPATIBILITY LAYER (C475)
         |     - MIDDLE atomic incompatibility
         |     - 95.7% of pairs forbidden
         |     - Result: Legal co-occurrence
         |
         └── EXECUTION LAYER (C109)
               - 17 forbidden transitions between classes
               - Phase-ordering dominant (41%)
               - Result: Legal program paths
```

### Why This Matters

**Independence enables modularity:**
- Construction constraints can evolve without breaking execution
- Compatibility constraints can be tuned without rebuilding morphology
- Execution hazards can be managed without token redesign

**Shared substrate enables compactness:**
- Same 10 characters do triple duty
- No separate "syntax layer" needed
- Information density maximized

**Real-world analogy:** Consider a programming language where:
- Character encoding rules govern what strings are valid identifiers
- Type system rules govern what combinations are semantically valid
- Control flow rules govern what execution orders are safe

These are independent - changing identifier rules doesn't change type checking.

### Kernel Primitive Reality

Test 15-16 confirmed kernel primitives (k, h, e) are **real operators**, not compression artifacts:

**Directional Asymmetry (C521):**
| Transition | Ratio | Interpretation |
|------------|-------|----------------|
| e→h | 0.00 | STABILITY → PHASE: completely blocked |
| h→e | 7.00x | PHASE → STABILITY: highly favored |
| k→e | 4.32x | ENERGY → STABILITY: favored |

This one-way valve topology **cannot arise from compression mechanics**. Compression would create symmetric patterns (hinges work both directions). The asymmetry proves functional operator status.

### Interpretive Implication (Tier 3)

The three-layer architecture suggests the manuscript was designed for:

1. **Expressive power:** Complex token morphology (construction layer)
2. **Safety:** Incompatibility prevents dangerous combinations (compatibility layer)
3. **Control:** Execution constraints maintain system stability (execution layer)

These goals are achieved **independently**, allowing each to be optimized without trade-offs.

### RI as Operational Signature (Tier 3)

RI MIDDLEs encode **compatibility intersections** at the construction layer:
- 85.4% contain multiple PP atoms (C516)
- Each atom is a compatibility dimension
- RI = PP₁ ∩ PP₂ ∩ PP₃ ∩ ... ∩ modifier

This explains why RI is:
- Unique to A (compatibility specification is A-side)
- Highly specific (multi-atom = narrow intersection)
- Length-correlated with uniqueness (more atoms = more specific)

### Cross-References

| Constraint | Role |
|------------|------|
| C085 | 10 kernel primitives (shared substrate) |
| C109 | Execution hazards (execution layer) |
| C475 | MIDDLE incompatibility (compatibility layer) |
| C517 | Superstring compression (hinge letters) |
| C521 | Directional asymmetry (construction layer) |
| C522 | Layer independence (falsified isomorphism) |

**Source:** MIDDLE_SUBCOMPONENT_GRAMMAR (2026-01-23)

---

## 0.D. RI LEXICAL LAYER HYPOTHESIS (RI_STRUCTURE_ANALYSIS Phase) - NEW in v4.39

### Tier 3: Grammar vs Lexicon Distinction

> **RI extensions within MIDDLEs may function as a LEXICAL layer that anchors abstract grammar to specific external substances, while PREFIX/SUFFIX/PP remain purely functional markers operating as GRAMMAR.**

This extends C526 with a detailed characterization of the two-layer model.

### The Problem This Addresses

C120 (PURE_OPERATIONAL) establishes that Voynich tokens have no semantic content. But RI MIDDLEs exhibit vocabulary-like behavior:
- 609 unique identifiers (regenerated 2026-01-24 with atomic-suffix parser)
- Localized to specific folios (87% on only 1 folio)
- Non-compositional (don't decompose systematically)
- Appear with varying PREFIX/SUFFIX combinations

This creates tension: How can 609 arbitrary localized identifiers have "no semantic content"?

### Resolution: Grammar vs Lexicon

The resolution distinguishes two functional layers:

| Layer | Components | Function | Semantic Status |
|-------|------------|----------|-----------------|
| **Grammar** | PREFIX, SUFFIX, PP atoms | Control-flow, procedural | No content (C120 applies) |
| **Lexicon** | RI extensions | Referential anchoring | Points to substances (THAT, not WHAT) |

**Grammar** is combinatorial and global:
- ch prefix used with 57 different MIDDLEs
- dy suffix used with 40 different MIDDLEs
- PP atoms appear across all systems (A, B, AZC)

**Lexicon** is arbitrary and localized:
- RI extensions don't decompose systematically
- 83% appear on only 1-2 folios
- Extensions function as dictionary entries, not grammatical positions

### Evidence Summary

**RI Localization Pattern:**

| Category | Percent | Avg Folios | Interpretation |
|----------|---------|------------|----------------|
| Strictly local (1 folio) | 87.3% | 1.0 | Specific material identifiers |
| Local (1-2 folios) | ~90% | 1.28 avg | Material identifiers |
| Distributed (10+ folios) | <1% | varies | Compatibility bridges |

**NOTE (2026-01-24):** Regenerated with atomic-suffix parser. With 609 RI MIDDLEs: 87% appear on only 1 folio, avg ~1.3 folios.

**PREFIX/SUFFIX Versatility:**

| Affix | Different MIDDLEs | Role |
|-------|-------------------|------|
| ch | 57 | Global grammatical marker |
| sh | 29 | Global grammatical marker |
| qo | 27 | Global grammatical marker |
| dy | 40 | Global grammatical marker |
| y | 34 | Global grammatical marker |

Same affixes combine with many different RI extensions - the grammar layer is independent of the lexical layer.

**Variation Pattern:**
- 95% of localized RI appear with multiple PREFIX/SUFFIX combinations
- Same RI MIDDLE, different grammatical context
- Example: `cheom`, `sheom`, `okeom`, `cheomam` all share MIDDLE `eom`

### The Two-Layer Model

```
Word Structure:
  TOKEN = PREFIX + MIDDLE + SUFFIX
          ↓        ↓        ↓
          Grammar  MIDDLE   Grammar
                   ↓
           PP_atom + Extension
           ↓         ↓
           Grammar   Lexicon
```

**Interpretation:**
- PP atoms encode **procedural compatibility** (what can be done)
- RI extensions encode **referential identity** (to what)
- PREFIX/SUFFIX encode **grammatical context** (in what form)

### RI PREFIX Bifurcation (C528) - NEW in v4.40

RI MIDDLEs split into two nearly-disjoint populations based on PREFIX behavior:

| Population | Count | % of RI |
|------------|-------|---------|
| PREFIX-REQUIRED | 334 | 50.1% |
| PREFIX-FORBIDDEN | 321 | 48.1% |
| PREFIX-OPTIONAL | 12 | 1.8% |

**Key finding:** Only 1.8% of RI MIDDLEs appear both ways. The rest are locked into one pattern.

**Section independence:** Both populations show identical distributions across H and P sections (~54% PREFIX rate in each). The split is substance-inherent, not section-driven.

**Implication for two-layer model:** PREFIX is grammatical globally, but its attachment to specific RI MIDDLEs is **lexically encoded**. Each substance identifier inherently requires or forbids PREFIX marking:

```
RI Vocabulary (609 MIDDLEs)  [regenerated 2026-01-24]
+-- PREFIX-REQUIRED (~50%): Always appear with PREFIX
|     Examples: acp, afd, aiikh, akod, alda
|
+-- PREFIX-FORBIDDEN (~50%): Never appear with PREFIX
      Examples: aiee, aiid, cckh, cfaras, cfhod
```

This creates two parallel substance vocabularies on each folio, both following the same localization pattern (87-90% on exactly 1 folio).

### Semantic Ceiling Refinement

This refines C120 (PURE_OPERATIONAL):

| What | Status |
|------|--------|
| Grammar (PREFIX, SUFFIX, PP) | No semantic content - abstract functional positions |
| Lexicon (RI extensions) | REFERENTIAL content - points to substances |
| Entity identity | IRRECOVERABLE - we know THAT 609 things are distinguished, not WHAT |

The system can **reference** specific substances without **encoding** which substances they are. The manuscript is operational AND referential - these are not contradictory.

### Why This Matters

**For the apparatus model:**
- Grammar tells the operator WHAT TO DO
- Lexicon tells the operator TO WHAT
- Both are necessary for functional completeness

**For interpretation:**
- ~609 substances/categories are distinguished in Currier A
- Cannot identify which (semantic ceiling)
- But we know they exist as distinct referents

**For the expert-oriented design:**
- Expert knows WHAT each RI extension refers to
- Grammar provides procedural context
- System assumes external knowledge of referents

### What This Does NOT Claim

- ❌ RI extensions encode specific plants (we can't know which)
- ❌ The lexical layer enables translation
- ❌ Meaning can be recovered from the text
- ❌ RI extensions are linguistic labels

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

**Source:** RI_STRUCTURE_ANALYSIS (2026-01-24)

### Gallows Domain Coherence (Tier 3)

**Finding (C530):** When RI contains gallows letter X, PP in the same record is 2-5x more likely to also contain X:

| Gallows | PP baseline | Observed in same record | Enrichment |
|---------|-------------|-------------------------|------------|
| k | 23.5% | 54.8% | 2.3x |
| t | 15.8% | 33.1% | 2.1x |
| p | 8.7% | 42.9% | 4.9x |
| f | 5.0% | 17.9% | 3.6x |

**Interpretation:**

This supports the RI lexical layer hypothesis: RI MIDDLEs reference specific materials that cluster by some property. Records and folios appear to organize around gallows "domains":

- **k-domain:** Default/unmarked (78/109 folios are k-dominant)
- **t-domain:** Alternative category (cluster of t-specialized folios)
- **p/f-domains:** Rare specialized markers (never folio-dominant)

This is NOT compositional derivation (the PP-as-atoms theory was statistically insignificant per C512 retest). Rather, it suggests **thematic coherence** - records dealing with the same category of material tend to use vocabulary (both RI and PP) from the same gallows domain.

**What this supports:**
- RI references external substances organized by some categorical property
- That property correlates with gallows letter usage
- The expert user would recognize these domain clusters

**What this does NOT claim:**
- ❌ Gallows letters encode specific meanings (we can't know what k vs t signifies)
- ❌ Domain clustering enables translation or identification

**Source:** GALLOWS_MIDDLE_ANALYSIS (2026-01-24)

### RI Linker Mechanism: Convergent Inter-Record References (Tier 3) - NEW in v4.54

**Finding (C835):** 0.6% of RI tokens (4 out of 707 types) function as "linkers" - they appear as FINAL in one paragraph and INITIAL in another, creating directed links between records.

**Topology is CONVERGENT (many-to-one):**

```
cthody:  5 folios (FINAL) ───→ 1 folio (INITIAL): f93v
ctho:    4 folios (FINAL) ───→ 1 folio (INITIAL): f32r
```

Each linker appears as INITIAL in exactly ONE folio but as FINAL in MULTIPLE folios. This creates collector hubs (f93v receives 5 inputs).

**Two Alternative Interpretations (cannot distinguish structurally):**

| Model | Logic | Meaning | Physical Analog |
|-------|-------|---------|-----------------|
| **AND (aggregation)** | Intersection | f93v requires ALL 5 conditions satisfied | Compound needing 5 ingredients |
| **OR (alternatives)** | Union | f93v accepts ANY of the 5 as valid input | 5 equivalent suppliers for same ingredient |

**Why the ambiguity matters:**

The same structural pattern supports both interpretations. An encoding where the logical operator (AND vs OR) is context-dependent would be:
- **Compact** - same notation serves multiple purposes
- **Expert-dependent** - practitioners know which applies
- **Opaque to outsiders** - hard to decode without domain knowledge

**Network Properties (Tier 2):**
- 12 directed links connecting 12 folios
- 66.7% forward flow (earlier folio → later folio)
- 75% ct-prefix in linkers (morphological marker)
- 95.3% of RI are singletons (linkers are rare)

**Interpretation:** Collector records (f93v, f32r) may document:
- **AND:** Compound materials/procedures requiring multiple source satisfactions
- **OR:** Procedures accepting alternative equivalent inputs

The sparse linking (0.6%) suggests most records are self-contained. Only rare "hub" entries aggregate or accept alternatives from multiple sources.

**New Evidence Favoring OR (2026-01-30):**

From linker_destination_characterization.py and linker_destination_followup.py:

1. **Hub destinations are structurally typical** - f93v and f32r show no outlier properties (all z-scores < |1|). They don't look like "aggregation points" that would combine inputs.

2. **Linkers don't consistently appear as INITIAL in destinations:**
   - cthody: INITIAL (pos 1) in f93v ✓
   - ctho: MIDDLE (pos 13) in f32r ✗
   - ctheody, qokoiiin: NOT FOUND in their destinations

   This suggests linkers function as cross-references ("see also folio X") rather than procedural inputs.

3. **High source vocabulary similarity (Jaccard 0.50-0.77):**
   - If AND (aggregation): sources should have DIFFERENT content (distinct ingredients)
   - If OR (alternatives): sources should have SIMILAR content (interchangeable)

   Observed Jaccard similarity is high, supporting the OR interpretation. Sources share substantial vocabulary beyond the linker token.

4. **Section concentration:** 96% (all destinations + 8/9 sources) are in section H. This suggests domain-specific cross-referencing within herbal content.

**Interpretation refined:** Linkers likely function as **cross-references** marking alternative entries or variations, not as procedural input aggregation points. The ct-ho morphology may mark "see also" rather than "requires".

**Source:** A_RECORD_B_ROUTING_TOPOLOGY (2026-01-28), LINKER_DESTINATION_CHARACTERIZATION (2026-01-30)

---

## 0.E. B FOLIO AS CONDITIONAL PROCEDURE (CLASS_COMPATIBILITY_ANALYSIS Phase) - NEW in v4.41

### Tier 3: Core Finding

> **Each B folio is a distinct procedure defined by unique vocabulary. Folio selection is external (human choice based on desired outcome). AZC modulates which core operations are available, creating conditional execution paths through the selected procedure.**

This upgrades "specific folio = specific recipe" from **NOT CLAIMED** (previous X.10 disclaimer) to **TIER 3 SUPPORTED**.

### Evidence Summary (C531-C534)

| Finding | Value | Constraint |
|---------|-------|------------|
| Folios with unique MIDDLE | **98.8%** (81/82) | C531 |
| Unique MIDDLEs that are B-exclusive | **88%** | C532 |
| Adjacent folio grammatical slot overlap | **1.30x** vs non-adjacent | C533 |
| Mean unique MIDDLEs per folio | 10.5 | C531 |
| Only folio without unique vocabulary | f95r1 | C531 |

### The Two-Vocabulary Model

Each B folio contains two vocabulary layers:

| Layer | Source | AZC Role | Function |
|-------|--------|----------|----------|
| **Core vocabulary** | Shared (41 MIDDLEs) | **Filtered** - determines what's legal | Control flow (~79% of tokens) |
| **Unique vocabulary** | B-exclusive (88%) | **Not filtered** - always available | Procedure identity (~21% of tokens) |

**Key insight:** AZC doesn't determine WHICH folio runs. AZC determines which OPERATIONS are available within any folio.

### The Conditional Execution Model

The same B folio can produce different execution paths depending on the A record:

```
B Folio F (fixed procedure):
├── Unique vocabulary: Always available (procedure identity)
│   └── 10-15 MIDDLEs specific to this folio
│
└── Core vocabulary: Conditionally available
    ├── A record X active → core ops {a, b, c} legal
    │   └── Execution path: unique + {a, b, c}
    │
    └── A record Y active → core ops {a, d, e} legal
        └── Execution path: unique + {a, d, e}
```

This is **constraint satisfaction**, not **program selection**:
- The manuscript provides 83 procedures (B folios)
- AZC provides runtime constraints (which core ops are legal)
- Actual execution = intersection of procedure content and AZC legality

### The Operational Workflow

```
1. MATERIAL IDENTIFICATION
   Human has substance → finds matching A record
   A record's PP vocabulary encodes compatibility profile

2. COMPATIBILITY CHECK
   A record position activates AZC constraints
   ~80% of B core vocabulary filtered (C502)

3. PROCEDURE SELECTION
   Human chooses B folio based on desired outcome
   Each folio is a complete procedure with unique specifics

4. CONDITIONAL EXECUTION
   Procedure runs with:
   - Unique vocabulary (always available) = procedure identity
   - Legal core vocabulary (AZC-filtered) = available operations

5. MONITORING
   Human Track annotations record observations
   Higher HT with rare materials (C461)
```

### Why 83 Folios With Unique Vocabulary?

Each folio is a **specific recipe**, not a generic template:

| Property | Evidence | Interpretation |
|----------|----------|----------------|
| Unique vocabulary | 98.8% have unique MIDDLEs | Each procedure has specific details |
| Same grammar | All use 49 classes (C121) | Shared control structure |
| Adjacent similarity | 1.30x slot overlap | Related procedures (variations) |
| Section clustering | Partial (C534) | Domain organization |

The ~10.5 unique MIDDLEs per folio encode:
- Specific equipment/apparatus references
- Specific timing/temperature markers
- Specific outcome indicators
- What makes THIS procedure distinct from others

### Integration with Brunschwig Model

This strengthens the Brunschwig alignment:

| Brunschwig | Voynich | Mapping |
|------------|---------|---------|
| Fire degree (1-4) | REGIME (1-4) | Completeness requirements |
| Recipe within degree | B folio within REGIME | Specific procedure |
| Recipe-specific steps | Unique vocabulary | Procedure identity |
| Shared techniques | Core vocabulary | Control operations |

The pathway becomes concrete:

```
Brunschwig recipe
    → Product type
    → REGIME (completeness tier)
    → B folio (specific procedure)
    → Execution with A-record constraints
```

### What This Does NOT Claim

- ❌ Folio selection is encoded in the text (it's external/human)
- ❌ Unique vocabulary has recoverable meaning (semantic ceiling applies)
- ❌ Each folio maps to exactly one Brunschwig recipe
- ❌ AZC "chooses" which folio runs

### What This DOES Claim (Tier 3)

- ✓ Each B folio is a distinct procedure (unique vocabulary defines it)
- ✓ Folio identity is independent of AZC (88% B-exclusive)
- ✓ AZC modulates execution paths, not procedure selection
- ✓ The manuscript is a conditional procedure library, not a sequential program
- ✓ Human operator selects folio based on external context

### Architectural Implication

The Voynich B section is a **reference library** of 83 conditional procedures:

```
┌─────────────────────────────────────────────────────────┐
│                   B PROCEDURE LIBRARY                    │
│                      (83 folios)                         │
├─────────────────────────────────────────────────────────┤
│  Each folio:                                             │
│  ├── IDENTITY: Unique vocabulary (always available)     │
│  ├── GRAMMAR: 49 instruction classes (shared)           │
│  └── CONSTRAINTS: Core vocab filtered by AZC            │
├─────────────────────────────────────────────────────────┤
│  Human selects folio based on:                          │
│  ├── Domain (herbal, pharma, astro sections)            │
│  ├── Desired outcome (product type)                     │
│  └── Material compatibility (A record determines)        │
└─────────────────────────────────────────────────────────┘
```

This is why:
- Illustrations exist (visual indexing for folio selection)
- Sections exist (domain organization for navigation)
- Labels exist (identification markers)
- Each folio has unique vocabulary (procedure specificity)

The text encodes procedures and constraints. The decision of WHEN to use them is external.

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

**Source:** CLASS_COMPATIBILITY_ANALYSIS (2026-01-25)

---

## 0.F. LINE-LEVEL EXECUTION SYNTAX (CLASS_SEMANTIC_VALIDATION Phase) - NEW in v4.43

### Tier 2-3: Execution Cycle Discovery

> **Each line follows a positional template: SETUP (initial) → THERMAL WORK (medial) → CHECKPOINT/CLOSURE (final). The 5 role categories (CC, EN, FL, FQ, AX) have distinct positional preferences, transition grammars, and REGIME/section profiles that collectively define line-level execution syntax.**

This fills a critical gap: we previously knew the VOCABULARY of operations (what roles exist) but not the SYNTAX (how they flow within a line).

### The Line as Control Cycle

The 49 instruction classes participate in 5 validated roles with distinct positional preferences (C556, Chi2 p=3e-89):

```
LINE STRUCTURE:

INITIAL zone              MEDIAL zone              FINAL zone
[0.0 -------- 0.3]        [0.3 -------- 0.7]       [0.7 -------- 1.0]

  daiin (CC trigger)         ENERGY chains            FLOW (ar, al, ary)
  AUXILIARY setup            qo ↔ ch-sh interleave    FREQUENT (or→aiin)
  UNCLASSIFIED (1.55x)      ENERGY (avoids edges)     FL/FQ (~1.65x)

        CC/AX                  ENERGY 0.45x              FL/FQ
      (openers)              (medial-concentrated)       (closers)
```

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

### Role-Specific Structure

**CORE_CONTROL Hierarchy (C557, C558, C560):**

```
CORE_CONTROL
├── Singletons (atomic)
│   ├── daiin (Class 10): 27.7% line-initial, 47.1% ENERGY followers
│   ├── ol (Class 11): 9.5% line-final, closure signal
│   └── k (Class 12): 0 occurrences in Currier B (bound morpheme)
└── Derived (compound)
    └── Class 17 (ol+X): 9 tokens, ALL PREFIX=ol
        BIO enriched 1.72x, PHARMA 0 occurrences
```

**daiin** functions as an ENERGY trigger - "begin thermal sequence." **ol** functions as closure - "processing complete." Class 17 represents elaborated control operators derived from the atomic ol.

**or→aiin Directional Bigram (C561):**

| Expected (random) | Observed |
|-------------------|----------|
| aiin→aiin: 31% | **0%** |
| or→aiin: 22% | **87.5%** |

Zero aiin→aiin sequences exist (structural constraint, not statistical tendency). The or→aiin bigram functions as a grammatical unit: or initiates (85%), aiin terminates (90%). This is a checkpoint marker, not token repetition.

**FLOW Final Hierarchy (C562):**

| Class | Final% | Function |
|-------|--------|----------|
| 40 (ary, dary, aly) | 59.7% | Strong closers |
| 38 (aral, aram) | 52.0% | Strong closers |
| 30 (dar, dal, dam) | 14.8% | Neutral/provisional |
| 7 (al, ar) | 9.9% | Soft closers |

**ary is 100% line-final** - a pure termination signal. The hierarchy represents degrees of closure from provisional (ar) to absolute (ary).

**Section Profiles (C552, C553, C555):**

| Section | Signature | Profile |
|---------|-----------|---------|
| BIO | +CC +EN (45.2% ENERGY) | Thermal-intensive processing |
| HERBAL_B | +FQ -EN (1.62x FREQUENT) | Repetitive non-thermal cycles |
| PHARMA | +FL, Class 34 replaces 33 | Flow-dominated, controlled collection |
| RECIPE_B | -CC | Reduced control overhead |

BIO-REGIME effects are independent and additive (C553): baseline 27.5% ENERGY, +6.5pp from REGIME_1, +9.8pp from BIO section. BIO + REGIME_1 = 48.9% ENERGY (highest in manuscript).

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

### Integration with Brunschwig

**Brunschwig's fire-degree cycle now maps to line structure:**

| Brunschwig Phase | Voynich Line Position | Key Marker |
|------------------|-----------------------|------------|
| "First degree - initiate heat" | Initial zone | daiin (trigger) |
| "Second/third degree - work" | Medial zone | ENERGY chains, qo↔ch-sh |
| "Finger test / scent test" | Medial-final boundary | or→aiin (checkpoint) |
| "Overnight cooling" | Final zone | FLOW hierarchy (ar < ary) |

Brunschwig writes: *"Rose and lavender waters are discarded when their taste and scent have diminished."* The or→aiin bigram may mark exactly this moment - where sensory judgment determines whether the batch passes.

Brunschwig writes: *"must be left to stand overnight to cool."* The FLOW final hierarchy encodes degrees of this commitment - from provisional cooling (ar) to irreversible batch completion (ary).

### The Gap This Fills

| Before CLASS_SEMANTIC_VALIDATION | After |
|----------------------------------|-------|
| Knew token decomposition (PREFIX+MIDDLE+SUFFIX) | Now know how tokens FLOW within lines |
| Knew roles existed (CC, EN, FL, FQ, AX) | Now know roles have positional grammar |
| Knew REGIME controlled intensity | Now know REGIME controls ENERGY/FLOW ratio |
| Knew sections had different profiles | Now know profiles map to procedural types |
| Knew lines were control blocks | Now know control blocks have SETUP→WORK→CHECK→CLOSE structure |

### What This Does NOT Claim

- That specific Brunschwig passages map to specific tokens
- That or→aiin literally means "sensory test"
- That daiin literally means "begin heating"
- That any token has recoverable referential meaning

The interpretation is STRUCTURAL, not semantic: line-level syntax exhibits a cycle structure consistent with thermal processing, but the semantic ceiling (C171) still applies.

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

**Source:** CLASS_SEMANTIC_VALIDATION (2026-01-25)

---

## 0.G. THE SCAFFOLD AND THE SHADOW (AX_FUNCTIONAL_ANATOMY Phase) - NEW in v4.44

### Tier 3-4: What the Other 28% Was Doing All Along

For months, one-fifth of the instruction classes sat in a bucket labeled AUXILIARY — 480 tokens, 20 classes, 28.4% of everything Currier B ever wrote — and nobody could say what they *did*. They weren't ENERGY. They weren't FLOW. They weren't CONTROL or FREQUENT. They were just... there. Structurally present, positionally real (C563-C566 proved they had INIT/MED/FINAL sub-positions with p=3.6e-47), but functionally invisible. The grammar had a heartbeat and a skeleton and a nervous system, and then this enormous quiet mass of tissue that nobody could name.

It turns out we were looking at the problem backwards.

We kept asking: *What does AUXILIARY do that the other roles don't?* The answer is nothing. AX doesn't do anything the other roles don't do. It uses the same vocabulary, drawn from the same pipeline, carrying the same material identity. The difference isn't in the vocabulary. The difference is in the *prefix*.

### One Vocabulary, Two Postures

Take a MIDDLE — any MIDDLE, say `edy`. The pipeline delivers it from Currier A through AZC into B. Now watch what happens:

Attach the prefix `ch` and you get `chedy` — an ENERGY operator. The distiller picks up the material and puts it to work. Heat applied, vapor rising, the cucurbit is active.

Attach the prefix `ok` and you get `okedy` — an AUXILIARY scaffold token. The distiller *stages* the material. It's on the bench, accounted for, positioned for use. But the fire isn't lit yet.

Strip the prefix entirely and you get bare `edy` — an AX_FINAL frame-closer. The material is declared ready. The workspace around this step is complete.

Now add an articulator: `ychedy`, `dchedy`, `lchedy` — AX_INIT frame-openers. The distiller announces: *this workspace is now open for processing this material*. The `ch` prefix is still there — it still names the operational mode — but the articulator (`y`, `d`, `l`) shifts it from present tense to future tense. Not "processing now" but "preparing to process."

Same MIDDLE. Same material. Four different deployment modes, selected entirely by what prefix wraps around it (C571). A classifier using nothing but prefix achieves 89.6% accuracy at telling AX from non-AX (C570). The remaining 10.4% are exactly the ambiguous cases — the articulated ch/sh forms where the system deliberately blurs the line between announcing work and doing it.

This is the resolution: **PREFIX is the role selector. MIDDLE is the material carrier. AX is not a different vocabulary — it is the same vocabulary in scaffold mode** (C571).

### The Numbers Behind the Story

The overlap is not subtle. Of 57 unique MIDDLEs that appear in AX tokens, 41 — seventy-two percent — are shared with operational ENERGY tokens (C567). The Jaccard similarity between AX and EN vocabulary is 0.400, which is enormous for two categories that were supposed to be doing different things. And 98.2% of AX MIDDLEs come through the PP pipeline from Currier A. This is not independent material. This is the same material the pipeline sends everywhere else.

How much of Currier A feeds into AX? Nearly all of it. 97.2% of A records carry at least one MIDDLE that ends up in an AX class (C568). The average record contributes 3.7 AX-relevant MIDDLEs. The top contributors are the universal single-character forms — `o` appears in 60% of records, `i` in 39%, `e` in 34% — the same hub MIDDLEs that anchor the entire discrimination space. Only 44 records (2.8%) have zero AX vocabulary, and every one of them is tiny, with four or fewer total MIDDLEs. They're not AX-excluded; they're just small.

On the B side, the guarantee is absolute: zero contexts have zero AX classes. Classes 21 and 22 survive in every single pipeline configuration. You cannot construct a legal B line without scaffolding. The frame is architecturally mandatory (C568).

### Proportional but Not Random

Here is where it gets interesting. The fraction of surviving classes that are AX is 0.4540. The expected fraction under uniform distribution is 0.4545. The deviation is -0.0005 — less than a tenth of a percent. AX doesn't grow or shrink relative to operational roles. It scales in perfect proportion to pipeline throughput (C569).

But the linear model only achieves R²=0.83, not 0.99. The *volume* is proportional; the *composition* has structure of its own. AX_INIT is systematically over-represented (regression slope 0.130 vs expected 0.102) while AX_FINAL is under-represented (0.093 vs 0.122). The manuscript opens frames more eagerly than it closes them. Workspaces are declared with enthusiasm and wrapped up with restraint — which, if you've ever watched someone set up a distillation bench versus clean one up, sounds about right.

### The Shadow on the Scaffold

So what *is* AUXILIARY?

It is the shadow cast by operational vocabulary onto the structural frame of each line. The same light source — MIDDLEs from the pipeline — hits two surfaces. When it hits an operational prefix (ch, sh, qo), you get active processing: ENERGY work, thermal sequences, the grammar's engine running. When it hits a scaffold prefix (ok, ot, bare, articulated), you get staging: workspace management, frame boundaries, material accounting.

The shadow is real. It has shape — INIT/MED/FINAL positional structure with p=3.6e-47 (C563). It has guaranteed presence — classes 21 and 22 always survive (C568). It has independent composition — the subgroup slopes differ from expectation (C569). But it is defined by what casts it. Remove the operational vocabulary and the shadow vanishes. The scaffold has no vocabulary of its own — or rather, it has 16 exclusive MIDDLEs (28.1%), just enough to prove it isn't *entirely* derivative, but not enough to stand alone.

This means the line-level execution cycle from Section 0.F is richer than we thought. Each line doesn't just run SETUP→WORK→CHECK→CLOSE. Each line *brackets* its work in a structural frame made from the same material it processes:

```
 AX_INIT                    ENERGY work               AX_FINAL
 "Opening workspace:        "Processing lavender:      "Workspace closed:
  lavender staged"           heat, vent, monitor"       lavender complete"
  (ychedy)                   (chedy, shedy)             (dy)
       └──── same MIDDLE ──────── same MIDDLE ──────────┘
              different PREFIX      different PREFIX
```

The manuscript records not just what was done to the lavender, but the opening and closing of the workspace *around* the lavender. Every step is framed. Every frame is built from the step's own material. This is why AX is 28.4% of the text — it takes real structural work to bracket every operation with its own scaffold, and that scaffold is proportional to the operations it frames.

### What This Means for the Workshop

Picture Brunschwig's distillery. The master has a bench, a furnace, a cucurbit, an alembic, collection vessels. Before each operation, he stages: lays out the rose petals, checks the alembic's seal, positions the receiver. This staging uses the same materials that will be processed — you can't stage lavender without handling lavender — but the *posture* is different. Staging is inventory. Processing is chemistry. Same hands, same materials, different intent.

The manuscript, it appears, records both. Not just "heat the lavender" (ENERGY) and "collect the distillate" (FLOW) and "check the scent" (FREQUENT) and "begin the sequence" (CONTROL) — but also "workspace open for lavender" (AX_INIT), "lavender staged" (AX_MED), "lavender workspace closed" (AX_FINAL). The staging protocol. The part of the procedure that a modern recipe would leave implicit but that a 15th-century reference manual for trained operators — a manual designed to be *safe* — would make explicit.

This is consistent with a system that takes safety seriously enough to encode it structurally. The scaffold is guaranteed (C568). The frame always opens (AX_INIT present 95.9% of the time). The frame always closes (AX_FINAL present 100%). You cannot skip the staging protocol. The grammar won't let you.

If the manuscript is a manual for operating dangerous thermal-chemical equipment — and the structural evidence increasingly says it is — then the 28% we couldn't explain wasn't wasted space. It was the safety margin. The part of every procedure that says: *before you light the fire, confirm your workspace is ready. After the fire goes out, confirm your workspace is clear.*

Every good workshop has this discipline. The Voynich manuscript, it seems, wrote it down.

### Twenty Classes, One Shadow (C572)

One question remained after the anatomy was clear: if AX has 19 instruction classes, do those 19 classes correspond to 19 different *kinds* of scaffolding? Nineteen distinct staging protocols? Nineteen ways to open a workspace?

No. We tested every dimension we could think of — transition structure, positional profiles, neighborhood context — and the answer was emphatic. Only 3 of 19 classes showed any structured transitions. A classifier trained on context signatures scored 6.8% accuracy, *below* the 10.3% random baseline. The best clustering algorithm could manage was k=2 with silhouette 0.18 — worse than the prior attempt that already found weak signal. The sole outlier was Class 22, AX_FINAL's workhorse, which distinguished itself not by what it *did* but by where it *sat*.

The 19 classes are not 19 kinds of scaffold. They are one shadow, cast from 19 slightly different angles. Position is the only thing that separates them. The AX vocabulary is positionally structured (INIT/MED/FINAL is real, p=3.6e-47) but behaviorally uniform. Every scaffold token does the same thing: frame the workspace. The grammar gives you 19 classes because the morphological system — 22 AX-exclusive prefixes crossed with articulators — generates 19 distinct surface forms. But the behavioral space those forms occupy is a single cloud, not 19 clusters.

This is the final simplification. Currier B's 49 instruction classes decompose into 30 behaviorally meaningful roles (the operational classes) plus 19 positional variants of a single scaffold function. The grammar is simpler than it looks. The complexity is in the operations. The scaffold is just... scaffolding.

### Evidence Summary (C567-C572)

| Constraint | Finding | Key Number |
|------------|---------|------------|
| C567 | AX MIDDLEs overlap with operational roles | 72% shared, Jaccard=0.400 |
| C568 | AX vocabulary present in nearly all pipeline contexts | 97.2% A-records, 0 zero-AX B-contexts |
| C569 | AX volume scales proportionally, composition is independent | Fraction 0.454, R²=0.83 |
| C570 | PREFIX alone predicts AX membership | 89.6% accuracy, 22 AX-exclusive prefixes |
| C571 | AX = PREFIX-determined scaffold mode of pipeline vocabulary | PREFIX is role selector, MIDDLE is material |
| C572 | 19 AX classes collapse to ≤2 effective behavioral groups | silhouette=0.18, context below baseline |

**Source:** AX_FUNCTIONAL_ANATOMY (2026-01-25), AUXILIARY_STRATIFICATION (2026-01-25), AX_CLASS_BEHAVIOR (2026-01-25)

---

## 0.H. ENERGY ANATOMY (EN_ANATOMY Phase) - NEW in v4.45

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

**Source:** EN_ANATOMY (2026-01-26)

---

## 0.I. SMALL ROLE ANATOMY AND FIVE-ROLE SYNTHESIS (SMALL_ROLE_ANATOMY Phase) - NEW in v4.45

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

### The Structure Inversion (C589)

The most counterintuitive finding: small roles are more internally structured than large roles.

| Role | Classes | KW Significant | Verdict |
|------|---------|---------------|---------|
| CC | 2 active | 75% | GENUINE_STRUCTURE |
| FL | 4 | 100% | GENUINE_STRUCTURE |
| FQ | 4 | 100% | GENUINE_STRUCTURE |
| EN | 18 | — | DISTRIBUTIONAL_CONVERGENCE (C574) |
| AX | 19 | — | COLLAPSED (C572) |

Small roles have few classes but each class does something distinct. Large roles have many classes doing roughly the same thing. Control signals are differentiated; content carriers are interchangeable.

**Tier 3 interpretation:** This maps to how procedural knowledge is organized. You need a few specialized control tools (begin, transition, iterate, close) but many interchangeable content instances (different materials through the same operations). The system differentiates its control signals and mass-produces its content carriers.

### Suffix Role Selectivity (C588)

First cross-role suffix analysis. Chi-square = 5063.2, dof=80, p < 1e-300.

| Stratum | Role | Suffix Types | Bare Rate |
|---------|------|-------------|-----------|
| SUFFIX_RICH | EN | 17 | 39.0% |
| SUFFIX_MODERATE | AX | 19 | 62.3% |
| SUFFIX_DEPLETED | FL, FQ | 1-2 | 93-94% |
| SUFFIX_FREE | CC | 0 | 100.0% |

EN and AX share suffix vocabulary (Jaccard = 0.800). CC/FL/FQ are suffix-isolated.

**Tier 3 interpretation:** Suffixes encode material variants on content tokens. EN is suffix-rich because it specifies *which variant* of an operation to perform — different materials need different treatment. CC/FL/FQ are suffix-free because control signals are material-independent. "Begin" is "begin" regardless of what you're distilling.

### FL Hazard-Safe Split (C586)

FL divides into two genuine subgroups:

| Subgroup | Classes | Mean Position | Final Rate | Hazard Role |
|----------|---------|--------------|------------|-------------|
| Hazard | {7, 30} | 0.55 | 12.3% | Source (4.5x initiation bias) |
| Safe | {38, 40} | 0.81 | 55.7% | Non-hazardous |

Mann-Whitney: position p=9.4e-20, final rate p=7.3e-33. FL initiates forbidden transitions far more than it receives them. EN is the mirror: mostly a target.

**Tier 3 interpretation:** In distillation, the danger comes from flow decisions — opening a valve at the wrong time, transitioning between phases incorrectly. The material itself (EN) doesn't create hazards; it suffers the consequences. FL → EN hazard directionality is exactly what you'd see in a system where flow control errors damage the batch.

### FQ Four-Way Differentiation (C587)

| Class | Tokens | Character | Distinctive Feature |
|-------|--------|-----------|-------------------|
| 9 | 630 | aiin/o/or | Medial self-chaining, prefix-free |
| 13 | 1,191 | ok/ot+suffix | Largest FQ class, 16% suffixed |
| 14 | 707 | ok/ot+bare | Distinct from 13 (p=1.6e-10) |
| 23 | 362 | d/l/r/s/y | Final-biased, morphologically minimal |

Classes 13 and 14 share the ok/ot PREFIX family but differ in suffix behavior. This mirrors C570's PREFIX-as-role-selector principle operating *within* a single role.

### CC Positional Dichotomy (C590)

Class 10 (daiin): initial-biased (0.413), 27.1% line-initial. Class 11 (ol): medial (0.511), 5.0% initial. Mann-Whitney p=2.8e-5. CC is operationally a two-token toggle with complementary control primitives. Class 12 (k) is ghost. If Class 17 is included (C560), it adds ol-derived compound control operators.

### C559 Correction (C592)

C559 (FREQUENT Role Structure) used incorrect membership {9, 20, 21, 23}. Classes 20 and 21 are AX (C563). Correct FQ is {9, 13, 14, 23} per ICC. C559 is SUPERSEDED by C583 and C587. Downstream constraints C550, C551, C552, C556 flagged for re-verification with corrected membership.

### Five-Role Summary Table (C591)

| Property | CC | EN | FL | FQ | AX |
|----------|-----|-----|-----|-----|-----|
| Classes | 3-4 | 18 | 4 | 4 | 19-20 |
| Tokens | 735-1023 | 7,211 | 1,078 | 2,890 | 4,559 |
| % of B | 3-4% | 31.2% | 4.7% | 12.5% | 19.7% |
| PP% | 100% | 100% | 100% | 100% | 98.2% |
| Suffix types | 0 | 17 | 2 | 1 | 19 |
| Bare rate | 100% | 39% | 94% | 93% | 62% |
| Hazard role | None | Target | Source | Mixed | None |
| Structure | GENUINE | CONVERGENCE | GENUINE | GENUINE | COLLAPSED |

### Integration with Distillation Interpretation

The five-role taxonomy maps to a layered execution model:

| Layer | Role | Function | Distillation Parallel |
|-------|------|----------|----------------------|
| Frame | AX | Positional template | Apparatus arrangement |
| Signal | CC | Control primitives | Operator hand signals |
| Content | EN | Material operations (suffix-modified) | Substance processing |
| Flow | FL | State transitions (hazard-aware) | Valve/gate operations |
| Iteration | FQ | Repetition and closure | Cycle count, batch completion |

A line reads as: AX frame → CC signal → EN content + FL transitions + FQ iteration → FQ/FL close.

The suffix boundary confirms the apparatus-centric model: content tokens (EN) carry material-specific parameterization via suffixes; control tokens (CC/FL/FQ) are universal and bare. The system encodes *what material* through suffixes on EN, but *how to process* through suffix-free control signals.

### Evidence Summary (C581-C592)

| Constraint | Finding | Key Number |
|------------|---------|------------|
| C581 | CC definitive census | {10,11,12,17} — Class 17 confirmed CC per C560 |
| C582 | FL definitive census | {7,30,38,40}, 4 classes (was 2) |
| C583 | FQ definitive census | {9,13,14,23}, 2890 tokens (supersedes C559) |
| C584 | Near-universal pipeline purity | CC/EN/FL/FQ 100% PP; AX 98.2% |
| C585 | Cross-role MIDDLE sharing | EN-AX Jaccard=0.402; CC isolated |
| C586 | FL hazard-safe split | p=9.4e-20; FL source-biased 4.5x |
| C587 | FQ internal differentiation | 4-way genuine, 100% KW significant |
| C588 | Suffix role selectivity | chi2=5063.2; three suffix strata |
| C589 | Small role genuine structure | CC/FL/FQ all GENUINE vs large roles |
| C590 | CC positional dichotomy | daiin initial vs ol medial, p=2.8e-5 |
| C591 | Five-role complete taxonomy | 49 classes → 5 roles, complete partition |
| C592 | C559 membership correction | C559 SUPERSEDED; downstream flags |

**Source:** SMALL_ROLE_ANATOMY (2026-01-26)

---

## 0.J. FQ INTERNAL ARCHITECTURE (FQ_ANATOMY Phase) - NEW in v4.47

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

**Source:** FQ_ANATOMY (2026-01-26)

---

## 0.K. SUB-ROLE INTERACTION GRAMMAR (SUB_ROLE_INTERACTION Phase) - NEW in v4.47

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

**Source:** SUB_ROLE_INTERACTION (2026-01-26)

---

## 0.L. LANE CONTROL ARCHITECTURE (LANE_CHANGE_HOLD_ANALYSIS Phase) - NEW in v4.49

### Tier 3: Core Finding

> **The two EN execution lanes (QO/CHSH) encode complementary control functions — energy application and stabilization — that alternate with inertia-driven dynamics within a phase-gated legality framework. Thresholds are categorical (legality transitions), not numeric (accumulation values).**

### Two-Lane Functional Assignment

EN tokens carry one of two PREFIX subfamilies (C570-571) drawing from non-overlapping MIDDLE vocabularies (C576, Jaccard = 0.133):

| Lane | PREFIX | MIDDLE Character | Kernel Content | Hazard Role | Post-Hazard |
|------|--------|-----------------|----------------|-------------|-------------|
| **QO** | qo- | k-rich (70.7%) | ENERGY_MODULATOR | Zero participation (C601) | 24.8% (depleted) |
| **CHSH** | ch-/sh- | e-rich (68.7%) | STABILITY_ANCHOR | All 19 forbidden transitions | 75.2% (dominant) |

**Morphological lane signature** (C647): Cramer's V = 0.654, p < 0.0001. The lanes are built from different kernel-character vocabularies.

**Interpretation:** QO = controlled energy addition (non-hazardous). CHSH = stabilization/correction (hazard recovery). "Safe energy pathway" (F-B-002) means energy application that stays within bounds, not absence of energy.

### Change/Hold Label: FALSIFIED

The original interpretation (CHSH = state-changing, QO = state-preserving) was tested with 5 predictions. Two critical reversals falsified it:
- QO tokens contain k (energy), not e (stability) — opposite of prediction
- CHSH dominates post-hazard recovery (75.2%), not QO — opposite of prediction

The reversed mapping (QO = energy, CHSH = stabilization) resolves all 5 predictions. F-B-006 documents this.

### Oscillation Architecture

**Hysteresis oscillation confirmed** (C643): alternation rate = 0.563 vs null = 0.494 (p < 0.0001, z > 10). Short runs (median = 1.0). Section-dependent: BIO = 0.606, HERBAL_B = 0.427.

**Switching dynamics are inertia-driven, not threshold-driven:**

| Run Length N | QO P(switch) | CHSH P(switch) |
|-------------|-------------|---------------|
| 1 | 0.500 | 0.482 |
| 2 | 0.438 | 0.417 |
| 3 | 0.416 | 0.324 |
| 4 | 0.111 | 0.180 |
| 5 | 0.308 | 0.111 |

Hazard function is **DECREASING** (Spearman rho = -0.90 QO, -1.00 CHSH). Once in a lane, the system tends to stay. No numeric accumulation toward a switching threshold.

CC tokens between EN pairs **suppress** switching (42.6% switch rate with CC vs 57.1% without, p = 0.0002). Gap content explains only 1.25% of switching variance (pseudo-R2). Switching is not externally triggered — it emerges from the grammar's alternation preference at N=1.

### Categorical Legality Thresholds (Phase-Gated)

While token-level switching is memoryless-with-inertia, the system encodes **macro-level categorical thresholds** as legality transitions:

| Threshold | Mechanism | Evidence |
|-----------|-----------|----------|
| **Lower bound** | Aggression categorically forbidden in 20.5% of folios | C490: zero AGGRESSIVE compatibility, not low probability |
| **Upper bound** | Stabilization is absorbing (e->h = 0.00) | C521: kernel one-way valve; once stable, can't destabilize |
| **Observation band** | LINK enforces monitoring posture (r = -0.7057 with CEI) | C366, C190: non-operational boundary operator |
| **Intervention clamp** | Hazard exposure CV = 0.04-0.11 (tightly constrained) | C458: risky dimensions locked, recovery free |

**Key distinction:** Thresholds are not "push until temperature X." They are "at this phase, intervention Y is structurally impossible." Legality transitions, not parametric bounds (C469, C287-290).

### PP-Lane Discrimination (Cross-System)

20/99 PP MIDDLEs predict lane preference (FDR < 0.05, z = 24.26). QO-enriched MIDDLEs are k/t-based ENERGY_OPERATORs (11/15). CHSH-enriched are o-based AUXILIARY (3/5). Signal is primarily EN-mediated (17/20); 3 non-EN novel discriminators. No obligatory slots.

**Interpretation:** Pre-operational material vocabulary (A) carries kernel-character signatures that align with downstream execution lanes (B). The A->AZC->B pipeline transmits lane-relevant information.

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

### Functional Profiling (v4.50, LANE_FUNCTIONAL_PROFILING)

**LINK-lane independence (C648):** LINK monitoring operates above lane identity -- both lanes receive equal observation. This is consistent with LINK as a phase-marking function (C366) rather than a lane-specific intervention. If LINK encodes observation posture, the operator observes regardless of which energy mode is active.

**Deterministic MIDDLE partition (C649):** The 22 testable EN-exclusive MIDDLEs are 100% lane-specific (k/t/p-initial = QO only; e/o-initial = CHSH only). This means the token construction layer (C522) hard-codes lane assignment through morphological composition -- the initial character of a MIDDLE determines its lane. Sensory implication: if k presupposes thermal affordance and e presupposes multi-modal affordance, the exclusive vocabulary is partitioned by perceptual domain at the morphological level.

**Section-driven oscillation (C650):** BIO oscillates fastest (0.593), HERBAL slowest (0.457). This is section-driven, not REGIME-driven. Sensory interpretation: BIO content (volatile materials, rapid phase changes) requires faster sensory mode-switching; herbal processing allows sustained attention in one mode.

**Fast recovery (C651):** Post-hazard QO return in 0-1 CHSH tokens, unconditionally. If CHSH = stabilization posture and QO = energy application, the system's recovery time is a single stabilization check before returning to active energy management. This is consistent with a brief perceptual confirmation ("is it settled?") before resuming thermal work.

**HT is not elevated at lane switches** (no constraint; methodological artifact). The inertia pattern (decreasing hazard function from Script 3) is grammatical momentum, not perceptual cost. HT density is also lane-balance-independent after controlling confounds.

### Open Questions

1. Does the inertia pattern (decreasing hazard function) have a physical correlate? Thermal momentum (vessel retains heat) would produce exactly this signature.
2. Can the phase-gated legality transitions (C490, C521, C458) be mapped to specific Brunschwig procedural stages?
3. Do the 3 non-EN discriminators (g, kcho, ko) reveal a PP-level material distinction that the EN system doesn't capture?
4. Does the deterministic MIDDLE partition (C649) extend to non-exclusive MIDDLEs? The 34 shared MIDDLEs may show softer probabilistic enrichment.
5. Is the section-driven oscillation (C650) related to material volatility, or does it reflect structural properties of the text (line length, token density)?

**Source:** LANE_CHANGE_HOLD_ANALYSIS (2026-01-26), LANE_FUNCTIONAL_PROFILING (2026-01-27)

### PP Pipeline Lane Architecture (v4.51, PP_LANE_PIPELINE)

**PP vocabulary is lane-structured but non-functional (C652, C653):** The 404 PP MIDDLEs carry a 3:1 CHSH bias by initial character (25.5% QO, 74.5% CHSH). AZC filtering amplifies this to 5:1 in the pipeline pathway (19.7% QO, OR=0.48). If PP vocabulary defined the "rules" of the hysteresis control loop, this asymmetry should manifest as CHSH-dominated B programs. It doesn't.

**Grammar compensates for vocabulary bias (C654):** B programs show ~40.7% QO in EN lane balance -- 2.2x more than the vocabulary landscape predicts (18.7%). Non-EN PP composition does not predict EN lane balance (partial r=0.028, p=0.80). The grammar-level PREFIX->MIDDLE binding overrides vocabulary-level character distribution. Sensory implication: the operator's energy/stabilization balance is set by the grammar (instruction selection), not by the vocabulary available to the grammar. The control loop doesn't read its parameters from the A-side vocabulary shelf -- it generates them internally at execution time.

**PP does not define control loop rules (C655):** PP character composition adds zero incremental prediction beyond section and REGIME (incr R2=0.0005, p=0.81). Neither AZC-Med nor B-Native PP adds anything. The Tier 3 hypothesis that "PP is meant to define the rules in our hysteresis system" is **falsified at the lane-balance level**. PP constrains vocabulary availability (Tier 2, C502), but this constraint does not propagate to lane selection.

**Revised interpretation:** The pipeline is a vocabulary supply chain, not a rule-setting mechanism. A records define what PP MIDDLEs are available. AZC filtering refines availability. But once vocabulary reaches B, the grammar selects freely from what's available, applying its own PREFIX->MIDDLE binding to determine lane. The pipeline shapes the *palette*; the grammar paints the *picture*.

**Source:** PP_LANE_PIPELINE (2026-01-27)

### PP Pool Classification (v4.52, PP_POOL_CLASSIFICATION)

**PP MIDDLEs form a continuous parameter space, not discrete functional pools (C656, C657).** Hierarchical clustering on A-record co-occurrence (Jaccard similarity) produces maximum silhouette of 0.016 across k=2..20 (threshold: 0.25). B-side behavioral profiles are also continuous (best sil=0.237, degenerate k=2 split). The two axes are independent (ARI=0.052).

**Material class creates a gradient, not a partition (C658).** Forced co-occurrence clusters reduce material entropy by 36.2% (1.88 to 1.20 bits), but NMI=0.13. ANIMAL-enriched and HERB-enriched PP partially segregate, but 56% of PP are MIXED or NEUTRAL, occupying the gradient's middle.

**All PP axes are mutually independent (C659).** No axis pair exceeds NMI=0.15. Co-occurrence tells you nothing about behavior. Material class tells you nothing about pathway. PP is a high-dimensional continuous space where each MIDDLE occupies a unique position defined by weak, independent gradients.

**Revised Tier 4 interpretation:** The "toolbox" metaphor for PP is partially correct -- different A records have different PP compositions biased by material class -- but the toolboxes are not discrete types. They shade into each other. There are no "ANIMAL toolboxes" vs "HERB toolboxes." Instead, each A record draws from a continuous PP landscape where the draw is weakly biased by material. The 404 PP MIDDLEs are best understood as a continuous parametric vocabulary where each MIDDLE encodes a specific operational technique, and the techniques vary along multiple independent axes (material affinity, execution role, pipeline pathway) without forming coherent groupings.

**Source:** PP_POOL_CLASSIFICATION (2026-01-27)

### PREFIX x MIDDLE Selectivity (v4.53, PREFIX_MIDDLE_SELECTIVITY)

**PREFIX is a behavioral transformer, not a modifier (C661).** Changing the PREFIX on the same MIDDLE produces behavioral divergence (JSD=0.425) nearly as large as changing the MIDDLE entirely (JSD=0.436). Effect ratio = 0.975. The same PP MIDDLE deployed with different PREFIXes produces completely different successor class profiles.

**PREFIX massively narrows class membership (C662).** Mean 75% reduction (median 82%). EN PREFIXes (ch/sh/qo) channel MIDDLEs into EN classes at 94.1%. The combination (PREFIX, MIDDLE) -- not MIDDLE alone -- determines instruction class membership.

**Most PP MIDDLEs are PREFIX-promiscuous (C660).** Only 3.9% of testable MIDDLEs are locked to a single PREFIX. 46.1% are promiscuous (no dominant PREFIX). Exception: QO-predicting MIDDLEs (k/t/p-initial) are 100% qo-PREFIX locked. B uses more PREFIX combinations than A records show.

**PREFIX x MIDDLE pairs cluster better than MIDDLEs alone (C663).** Best silhouette = 0.350 at k=2 (vs C657's 0.237). The binary split likely reflects the EN/non-EN role dichotomy. Beyond this split, variation remains continuous.

**Revised Tier 4 interpretation:** The PP continuity puzzle (C656-C659) is resolved. MIDDLEs don't form discrete pools because their functional identity is determined by the PREFIX+MIDDLE combination. MIDDLE encodes the material/technique identity (continuous). PREFIX determines what role that technique plays (discrete: EN, AX, FQ, INFRA). The same technique can serve completely different roles depending on PREFIX. The 404 PP MIDDLEs are a continuous landscape of techniques; PREFIX provides the discrete operational grammar that deploys them.

**Source:** PREFIX_MIDDLE_SELECTIVITY (2026-01-27)

### Within-Folio Temporal Profile (v4.54, B_FOLIO_TEMPORAL_PROFILE)

**Programs are quasi-stationary at the meso-temporal level (C664-C669).** Within-folio evolution (line 1 to line N) was measured across 9 dimensions: 5 role fractions, LINK density, 3 kernel rates, hazard density, escape density, lane balance, and hazard proximity. Six of nine metrics are flat. Three show significant but mild positional evolution:

1. **AX scaffold increases late** (C664: rho=+0.082, p<0.001, Q1=15.4% -> Q4=18.1%) -- convergence-phase scaffolding
2. **QO lane fraction declines late** (C668: rho=-0.058, p=0.006, Q1=46.3% -> Q4=41.3%) -- energy-to-stabilization shift
3. **Hazard proximity tightens late** (C669: rho=-0.104, p<0.001, Q1=2.75 -> Q4=2.45 tokens) -- narrowing risk envelope

**Interpretation:** The controller maintains constant hazard exposure (C667), monitoring intensity (C665), and kernel contact (C666) throughout program execution. The mild late-program signals are consistent with convergence behavior: the control loop narrows its operating range as it approaches terminal state, accumulating scaffolding and shifting from energy-emphasis to stabilization-emphasis. This is thermostat steady-state approach, not phased execution.

**REGIME_4 is uniquely flat** across all dimensions (lane balance +1.4pp, hazard proximity slope -0.051), consistent with its precision-constrained identity (C494). **REGIME_2 shows the strongest temporal evolution** (lane balance -9.9pp, proximity slope -0.602), consistent with its aggressive energy-to-stabilization transition.

**Zero forbidden transition events** across the entire H-track B corpus. The 17 token-level forbidden pairs (C109) never occur literally. Hazard topology operates at the class level, not the specific token-pair level.

**This phase closes the meso-temporal gap.** Combined with within-line structure (C556-C562) and between-folio structure (C325, C458, C548), temporal behavior is now characterized at all three scales. The dominant finding: stationarity, with mild convergence drift.

**Source:** B_FOLIO_TEMPORAL_PROFILE (2026-01-27)

### Line-to-Line Sequential Structure (v4.55, B_LINE_SEQUENTIAL_STRUCTURE)

**Lines are contextually-coupled, individually-independent assessments (C670-C681).** This phase measured what changes from line to line at the token level, answering whether lines are sequentially coupled or independent draws from a stationary distribution.

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

**The critical test (C681):** 24/27 features show significant lag-1 prediction beyond position — verdict SEQUENTIALLY_COUPLED. But reconciliation with C670/C673/C674 reveals this coupling is **folio-mediated** (shared operating context), not line-to-line state transfer. The "memory" is the folio's configuration, not information passed between lines.

**Tier 4 synthesis:** Each folio configures a parameter context (REGIME + folio-specific conditions). Each line independently assesses the system within that context. Early lines use broad vocabulary and complex morphology; late lines are shorter, simpler, more bare-suffix. The controller converges toward a minimal-parameter operating mode across the folio, but each individual assessment is stateless — informed by folio context, not by what the previous line found.

**Source:** B_LINE_SEQUENTIAL_STRUCTURE (2026-01-27)

---

## 0.M. B PARAGRAPH AND FOLIO STRUCTURE (Annotation-Derived) - NEW in v4.56

### Tier 3: Core Finding

> **B folios are sequential procedures where paragraphs represent named operations executed in order. Early paragraphs concentrate identification vocabulary (HT), middle paragraphs concentrate processing (QO/CHSH), and late paragraphs show terminal vocabulary signature (AX clustering + TERMINAL FL). Lines with HT at both boundaries mark explicit state transitions.**

This interpretation derives from detailed line-by-line annotation of 10 Currier B folios (f41v, f43r, f43v, f46r, f46v, f103r, f103v, f104r, f104v, f105r) totaling ~350 lines with token-level role classification.

### Evidence: Paragraph-Position Vocabulary Distribution

Direct inspection of f105r (36 lines) revealed distinct vocabulary by folio position:

| Position | HT Density | Dominant Roles | FL Profile | Line Length |
|----------|------------|----------------|------------|-------------|
| **Early** (L2-L10) | HIGH (4 HT in L10) | INFRA LINE-INITIAL, QO/CHSH processing | ar (INITIAL) | Normal (10-12) |
| **Middle** (L11-L25) | VARIABLE (0-4 per line) | Heavy QO LANE, DOUBLED patterns | Mixed | Some SHORT (4-6) |
| **Late** (L26-L36) | DECLINING (mostly 0-1) | AX clustering, FL concentration | aly, am (TERMINAL) | SHORT (4-7) |

### The Terminal Vocabulary Signature

Late folio lines show a distinctive structural pattern:

1. **AX clustering** - L35 of f105r had 5 ot- tokens (otedaiin, otar, oteodar, otam, otaiin)
2. **TERMINAL FL** - Final lines end with -aly (otaly in L36) and -am closures
3. **Compressed length** - L36 had only 4 tokens vs normal 10-12
4. **HT depletion** - Identification work complete; late lines have 0-1 HT

**Interpretation:** Terminal paragraphs are "winding down" operations - auxiliary-heavy, completion-marked, stabilization-focused. The vocabulary shift from active processing (QO/CHSH/EN) to auxiliary completion (AX + TERMINAL FL) marks the transition from transformation to stabilization.

### State Transition Marking (Bracket Patterns)

Lines with HT at BOTH LINE-INITIAL and LINE-FINAL positions appeared multiple times:

| Folio | Line | Pattern | Example |
|-------|------|---------|---------|
| f105r | L29 | HT CONSECUTIVE at both ends | oleedar...cheolkary |
| f105r | L18 | HT bracketing | dsechey...aiiral |

**Interpretation:** If HT tokens identify materials/states, then:
- LINE-INITIAL HT = "starting with material/state X"
- LINE-FINAL HT = "ending with material/state Y"

The line documents a state transition: X → Y. This is explicit transformation tracking within the procedural record.

### Paragraph = Named Operation Model

Building on section 0.E (B Folio as Conditional Procedure), the internal structure is:

```
FOLIO = Complete procedure (e.g., "distill rose water")
│
├── PARAGRAPH 1 = Named operation (e.g., "maceration")
│     ├── Line 1: HEADER (high HT - identifies operation)
│     ├── Line 2-N: Control blocks (SETUP→WORK→CHECK→CLOSE)
│     └── State transitions marked by HT brackets
│
├── PARAGRAPH 2 = Named operation (e.g., "first distillation")
│     └── ... control blocks
│
└── PARAGRAPH N = Terminal operation (e.g., "stabilization")
      └── AX + TERMINAL FL signature, SHORT lines
```

**Sequential, not parallel:** The progression from identification-heavy (early) to completion-focused (late) indicates sequential execution of operations, not parallel processes.

### Strengthening the Brunschwig Alignment

The annotation findings strengthen the distillation manual interpretation:

| Observation | Brunschwig Parallel |
|-------------|---------------------|
| Paragraphs as named operations | Brunschwig organizes by operation (maceration, distillation, rectification) |
| Early = identification heavy | Recipe headers identify materials/process |
| Middle = processing heavy | Active transformation steps |
| Late = terminal vocabulary | "Until done" completion markers |
| State transition brackets | Brunschwig tracks material state changes |
| AX clustering at end | Final stabilization/storage operations |

### The FL STATE INDEX as Material Progression

The FL token distribution supports material-state tracking:

| FL Stage | Tokens | Mean Position | Interpretation |
|----------|--------|---------------|----------------|
| INITIAL | ar, r | 0.30-0.51 | Early material state |
| LATE | al, l, ol | 0.61 | Intermediate state |
| TERMINAL | aly, am, y | 0.78-0.94 | Final state |

**Hypothesis:** FL tokens encode material progression stages within the folio. Early paragraphs use INITIAL FL; late paragraphs use TERMINAL FL. This is consistent with a transformation procedure tracking material state through sequential operations.

### Quantitative Patterns from Annotation

From 10 annotated folios:

| Pattern | Frequency | Note |
|---------|-----------|------|
| HT LINE-INITIAL | Common | Identification at block entry |
| HT LINE-FINAL | Common | State marking at block exit |
| HT CONSECUTIVE | Occasional | Clusters of identification |
| HT Bracket (both ends) | Rare but systematic | Explicit state transition |
| EXCEPTIONAL lines (3+ HT) | ~15-30% per folio | Identification-critical blocks |
| SHORT lines (4-7 tokens) | Concentrated late | Terminal compression |
| AX clustering | Concentrated late | Completion operations |

### What This Does NOT Claim

- ❌ Paragraph boundaries are syntactically marked (they're visual)
- ❌ We can recover operation names (semantic ceiling applies)
- ❌ All folios have identical paragraph structure
- ❌ The progression is strictly monotonic

### What This DOES Claim (Tier 3)

- ✓ B folios have internal sequential structure (not random token distribution)
- ✓ Vocabulary distribution correlates with folio position
- ✓ Terminal paragraphs have distinctive signature (AX + TERMINAL FL + SHORT)
- ✓ HT bracket patterns mark state transitions
- ✓ This structure is consistent with sequential procedural documentation

### Integration with Control-Loop Model

The findings are robustly consistent with the control-loop interpretation:

| Structural Finding | Control-Loop Interpretation |
|-------------------|----------------------------|
| Line = SETUP→WORK→CHECK→CLOSE | Line = one control cycle |
| Paragraph = operation | Paragraph = series of related control cycles |
| Folio = procedure | Folio = complete control program |
| HT = identification | HT = state/material identification |
| FL progression | Material state tracking through transformation |
| Terminal signature | Stabilization and completion operations |

The annotation work didn't just confirm patterns exist - it showed how they compose into a coherent procedural document. The pieces fit together as a working whole.

**Source:** Manual annotation of f41v, f43r, f43v, f46r, f46v, f103r, f103v, f104r, f104v, f105r (2026-02-03)

---

## I. Human Track (HT) Interpretation

### Tier 2: Core Finding (v2.13)

> **HT is a scalar signal of required human vigilance that varies with content characteristics, not with codicology, singular hazards, or execution failure modes.**

HT functions as **anticipatory vigilance** - preparing the human operator for upcoming demands rather than reacting to past events (C459).

### What HT Is (Structural, Confirmed)

- HT **anticipates B stress** at quire level (r=0.343, p=0.0015)
- HT is **content-driven**, not production-driven (no quire boundary alignment)
- HT is **front-loaded** in the manuscript (decreasing trend)
- HT is **coarse**, distributed, and probabilistic

### What HT Is NOT

- HT does **not** say *why* attention is needed
- HT does **not** isolate catastrophic cases
- HT does **not** encode "danger zones"
- HT does **not** react to error or failure

### Tier 3: Dual-Purpose Attention Mechanism

HT may serve **two complementary functions**:

1. **Anticipatory vigilance** during high-demand phases
2. **Guild training** in the art of the written form

This is NOT "doodling" or "scribbling" - the evidence shows deliberate skill acquisition.

### Supporting Evidence (Tier 2 facts)

| Evidence | Finding | Implication |
|----------|---------|-------------|
| Rare grapheme engagement | 7.81x over-representation | Practicing difficult forms |
| Run structure | CV=0.35 (fixed-block range) | Deliberate practice blocks |
| Boundary-pushing forms | 24.5% | Exploring morphological limits |
| Family rotation | Change rate 0.71 | Systematic curriculum |
| Hazard avoidance | 0/35 at forbidden seams | Stop writing when attention demanded |
| Phase synchronization | V=0.136 | Writing tracks procedural phase |
| Anticipatory correlation | r=0.236 (HT before B) | HT precedes stress, not follows |

### System-Specific Anchoring

| System | Anchoring Pressure | Pattern |
|--------|-------------------|---------|
| Currier A | Registry layout | Entry-boundary aligned |
| Currier B | Temporal/attentional context | Waiting-profile correlated |
| AZC | Diagram geometry | Label-position synchronized |

### Historical Parallel

Medieval apprentice work-study combination. Productive use of operational waiting periods for skill development. Silent activity appropriate for apparatus monitoring.

---

## I.A. HT Morphological Curriculum (Tier 3 Characterization)

**Phase:** HT_MORPHOLOGICAL_CURRICULUM (2026-01-21)

### Hypothesis Tested

> HT morphological choices follow a curriculum structure: systematic introduction of grapheme families, spaced repetition of difficult forms, and complexity progression within practice blocks.

### Test Battery Results

| Test | Verdict | Key Finding |
|------|---------|-------------|
| 1. Introduction Sequencing | **STRONG PASS** | All 21 families in first 0.3% (KS=0.857) |
| 2. Spaced Repetition | UNDERPOWERED | Insufficient rare-but-repeated tokens |
| 3. Block Complexity | FAIL | No within-block gradient (33/33/33 split) |
| 4. Family Rotation | **WEAK PASS** | Quasi-periodic ACF peaks at 6,9,12,14,17 |
| 5. Difficulty Gradient | **PROVISIONAL** | Inverted-U pattern (H=89.04) - *rebinding confound* |
| 6. Prerequisite Structure | **WEAK PASS** | 26 pairs (2.5x expected by chance) |

### Confirmed Curriculum Properties

1. **Vocabulary Front-Loading:** All 21 HT families established in first 0.3% of manuscript (not gradual introduction)
2. **Prerequisite Relationships:** Complex families (esp. `yp`) consistently precede simpler consolidation forms
3. **Quasi-Periodic Rotation:** Families cycle with regular periodicity

### Provisional Finding (Rebinding Caveat)

The inverted-U difficulty pattern (middle zone easier than early/late) is statistically significant but **cannot be distinguished from rebinding artifact** without additional controls. The manuscript was rebound by someone who couldn't read it (C156, C367-C370). What we observe as "middle" may be a mixture of originally non-adjacent folios.

**Required follow-up:** Quire-level analysis to test whether pattern holds within preserved local ordering.

### Characterization (Not Constraint)

> HT morphological patterns exhibit vocabulary front-loading (all families established in first 0.3%), significant prerequisite relationships (26 pairs vs 10.5 expected), and quasi-periodic family rotation. This is consistent with a "vocabulary-first" curriculum structure distinct from gradual introduction.

**Tier 3** because: Test 3 failed, Test 5 is confounded by rebinding, pattern is distributional regularity not architectural necessity.

### Integration with C221

This refines the existing "Deliberate Skill Practice" interpretation (C221) with specific curriculum mechanics: front-loading vocabulary establishment, prerequisite ordering, and periodic rotation.

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

### Design Freedom vs Constraint (C458)

B programs exhibit **asymmetric design freedom**:

| Dimension | Allowed to Vary? | Evidence |
|-----------|-----------------|----------|
| Hazard exposure | NO | CV = 0.11 (clamped) |
| Intervention diversity | NO | CV = 0.04 (clamped) |
| Recovery operations | YES | CV = 0.82 (free) |
| Near-miss handling | YES | CV = 0.72 (free) |

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

### Phase-to-Workflow Mapping

AZC **diagram** positional grammar maps to operational workflow:

| Diagram Position | Workflow Phase | Escape Rate | Meaning |
|------------------|----------------|-------------|---------|
| C | Core/Interior | ~1.4% | Moderate flexibility |
| R1→R2→R3 | Progression | 2.0%→1.2%→0% | Options narrowing, committing |
| S | Boundary/Exit | 0% | Locked, must accept outcome |

*Note: P (Paragraph) is NOT a diagram position - it is Currier A text appearing on AZC folios.*

In reflux distillation: early phases are reversible, late phases are committed. AZC encodes this grammatically.

### Compatibility Grouping Mechanism (v4.5 - REFINED)

AZC compatibility reflects vocabulary co-occurrence at the **Currier A positional encoding level**, not active filtering.

**Precise Definition (C442 refined):**
> Two AZC folio vocabularies are compatible iff there exists at least one Currier A entry whose vocabulary bridges both.

**Empirical Test (2026-01-12):**

| Metric | Value |
|--------|-------|
| Total folio pairs | 435 |
| Bridged pairs | 390 (89.7%) |
| **Unbridged pairs** | **45 (10.3%)** |
| Graph connectivity | FULLY_CONNECTED |

**Family-Level Coherence:**

| Family Type | % Unbridged | Interpretation |
|-------------|-------------|----------------|
| Within-Zodiac | **0.0%** | Interchangeable discrimination contexts |
| Within-A/C | **14.7%** | True fine-grained alternatives |
| Cross-family | **11.3%** | Partial overlap |

**Key Corollaries:**
- Folios are NOT execution-exclusive (C440 still holds)
- Folios are NOT globally incompatible
- Incompatibility exists only at **specification time**
- Disallowed combinations leave no trace—they simply never occur

**f116v Structural Isolation:**
f116v shares NO bridging tokens with most other folios—it defines a discrimination profile that cannot be jointly specified with most other constraint bundles.

**Why AZC is large:** It enumerates all compatibility classes. Each folio = a different set of legal A-bundle combinations.

### Ambient Constraint Activation

AZC is not selected explicitly. Constraints activate automatically:
- **Core vocabulary** (20+ folios) → broadly legal
- **Specialized vocabulary** (1-3 folios) → activates specific profile
- **Diagram position (C→R→S)** → determines phase-specific rules

The vocabulary you use determines which constraints apply.

### Zodiac vs A/C as Perceptual Discrimination Regimes (v4.3 - VALIDATED)

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
| Universal MIDDLE Control | **PASSED** (58.7% vs 64.8%) |
| Family Escape Transfer | PARTIAL (r=0.265) |
| **HT Oscillation Density** | **PASSED** (A/C 80% higher) |

**The Coherent Explanatory Axis:**

| Layer | Zodiac | A/C |
|-------|--------|-----|
| Currier A | Coarse categories | Fine distinctions |
| AZC | Uniform scaffolds | Varied scaffolds |
| HT | Sustained flow | Punctuated checkpoints |
| Currier B | Same difficulty | Same difficulty |
| CEI | Same effort | Same effort |

> **Where discrimination is fine, attention becomes punctuated; where discrimination is coarse, attention can flow.**

**Falsified Variants:**
- Calendar/seasonal encoding ❌
- Parallel batch management ❌ (HT reversed)
- Regime-dependent execution difficulty ❌
- Family affects CEI or recovery ❌

See [efficiency_regimes.md](efficiency_regimes.md) for full test results.

### PREFIX Sub-Families via AZC Clustering (v4.4)

AZC folio co-occurrence can reveal sub-families within PREFIX classes that morphology alone doesn't show.

**Key Finding:** The y- PREFIX exhibits a **FAMILY_SPLIT**:

| Cluster | Family Bias | Sample Tokens | Shared Folios |
|---------|-------------|---------------|---------------|
| 66 | 85.7% Zodiac | ytaly, opaiin, alar | f72v1, f73v |
| 61 | 69.7% A/C | okeod, ykey, ykeeody | f69v, f73v |

**Interpretation:** y- does not behave like a single material class. It spans both discrimination regimes, suggesting:

1. **y- encodes something orthogonal to the Zodiac/A-C axis**
2. **y- may be a modifier or state marker** rather than a material class
3. **Regime-independent function** - applies in both coarse and fine discrimination contexts

**Contrast with regime-committed prefixes:**
- qo- (71.9% A/C) → tied to fine discrimination
- or- (58.3% Zodiac) → tied to coarse discrimination
- y- (split) → **regime-independent**

This strengthens the interpretation that PREFIX encodes more than material class - some prefixes encode functional roles that apply across discrimination regimes.

### Summary

> **AZC is a decision-point grammar that transforms static material references into phase-gated choice nodes, enforces compatibility between materials and operations, and encodes when intervention is legal versus when outcomes must be accepted.**

---

## I.D. MIDDLE Atomic Incompatibility Layer (C475) - NEW in v4.6

### Tier 2: Core Finding

> **MIDDLE-level compatibility is extremely sparse (4.3% legal), forming a hard incompatibility lattice. This is the atomic discrimination layer—everything above it (A entries, AZC folios, families, HT) is an aggregation of this graph.**

### Evidence (middle_incompatibility.py, 2026-01-12)

| Metric | Value |
|--------|-------|
| Total MIDDLEs | 1,187 |
| Total possible pairs | 703,891 |
| **Legal pairs** | **30,394 (4.3%)** |
| **Illegal pairs** | **673,342 (95.7%)** |
| Connected components | 30 |
| Largest component | 1,141 (96% of vocabulary) |
| Isolated MIDDLEs | 20 |
| Robustness (2-line check) | 97.3% overlap |

### Key Structural Objects

**1. Universal Connector MIDDLEs** ('a', 'o', 'e', 'ee', 'eo')
- Compatibility basis elements
- Bridge otherwise incompatible regimes
- "Legal transition anchors"
- Dominate strongest bridges (71, 50, 49 co-occurrences)

**2. Isolated MIDDLEs** (20 total)
- Hard decision points
- "If you specify this, you cannot specify anything else"
- Pure regime commitment
- Likely tail MIDDLEs, highly prefix-exclusive

**3. PREFIX = soft prior, MIDDLE = hard constraint**
- Within-PREFIX legal: 17.39%
- Cross-PREFIX legal: 5.44%
- Ratio: 3.2x (PREFIX increases odds, MIDDLE applies near-binary exclusions)

### Graph Structure

The incompatibility graph has:
- **30 connected components** (discrimination regimes)
- **One giant component** (1,141 MIDDLEs, 96%)
- Giant component ≠ free mixing — most pairs within it are still forbidden
- **Navigation requires changing regime step-by-step**

> The space is globally navigable, but only by changing discrimination regime step-by-step.

### Reconciliation with Prior Structure

| Prior Finding | Resolution |
|---------------|------------|
| C293 (MIDDLE is primary discriminator) | **Quantified**: 95.7% exclusion rate |
| C423 (PREFIX-bound vocabulary) | PREFIX is first partition, MIDDLE is sharper second |
| Why so many AZC folios? (C437-C442) | AZC = projections of sparse graph onto positional scaffolds |
| HT anticipatory function (C459, C461) | HT ≈ local incompatibility density (now testable) |
| f116v folio isolation | **Explained by data sparsity** (2 words), not MIDDLE incompatibility |

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

### I.E. Latent Discrimination Dimensionality (v4.7) - NEW

**Question:** How many latent "axes of distinction" are needed to explain the MIDDLE incompatibility graph?

**Answer:** ~128 dimensions for 97% AUC. The discrimination space is HIGH-DIMENSIONAL.

| K | Cross-Validation AUC |
|---|----------------------|
| 2 | 0.869 |
| 4 | 0.870 |
| 8 | 0.869 |
| 16 | 0.886 |
| 32 | 0.900 |
| 64 | 0.923 |
| 128 | **0.972** |

**Key Findings:**

1. **Not low-rank** — The expert hypothesis of "2-4 binary switches" is rejected
2. **Axes don't align with PREFIX** — Max separation 0.011 (very weak)
3. **Axes don't align with characters** — Max correlation 0.138 (weak)
4. **Axes don't align with length** — Max correlation 0.160 (weak)

**Interpretation (Tier 3):**

The 128 latent axes represent:
- NOT simple features (prefix, characters, length)
- Emergent compatibility structure learned from co-occurrence
- Each MIDDLE carries ~128 bits of discriminatory information

> **The MIDDLE vocabulary is not a categorization system with a few dimensions. It is a rich feature space where each variant has a unique 128-dimensional fingerprint.**

**What This Means for Generative Modeling:**

Any generator that reproduces Currier A must implicitly encode these ~128 dimensions. This rules out:
- Simple rule-based generators
- Low-parameter Markov models
- "Random but constrained" generation

**Hub Confirmation:**

The top-5 MIDDLEs by degree (weighted co-occurrence) match prior finding:
| MIDDLE | Degree |
|--------|--------|
| 'a' | 2047 |
| 'o' | 1870 |
| 'e' | 1800 |
| 'ee' | 1625 |
| 'eo' | 1579 |

These universal connectors remain valid; they simply have high compatibility across all 128 dimensions.

### I.F. Bundle Generator Diagnostic (v4.8) - NEW

**Question:** Can a generator constrained only by MIDDLE incompatibility + line length + PREFIX priors reproduce Currier A entries?

**Answer:** NO. 9/14 diagnostic metrics fail. Residuals reveal additional structure.

**Generator Configuration:**
- Included: MIDDLE incompatibility, line length, PREFIX priors
- Excluded: marker exclusivity, section conditioning, AZC info, adjacency coherence

**Diagnostic Results:**

| Metric | Real | Synthetic | Verdict |
|--------|------|-----------|---------|
| lines_zero_mixing | 61.5% | 2.7% | **FAIL** |
| pure_block_frac | 46.9% | 2.7% | **FAIL** |
| universal_middle_frac | 31.6% | 56.7% | **FAIL** |
| unique_middles | 1187 | 330 | **FAIL** |
| lines_with_repetition | 96.4% | 63.9% | **FAIL** |
| prefixes_per_line | 1.78 | 4.64 | **FAIL** |
| line_length (mean/median) | 19.2/8.0 | 20.0/8.0 | OK |

**Residual Interpretation (New Structure):**

1. **PREFIX COHERENCE** — Lines prefer single PREFIX family (not just compatibility)
2. **TAIL FORCING** — Real A systematically uses rare MIDDLEs
3. **REPETITION IS STRUCTURAL** — 96.4% of lines have repetition (deliberate)
4. **HUB RATIONING** — Universal MIDDLEs used sparingly (31.6% vs 56.7%)

**Interpretation (Tier 3):**

> **Incompatibility + priors are NECESSARY but NOT SUFFICIENT.** The generator reveals at least four additional structural principles: PREFIX coherence, tail forcing, repetition structure, and hub rationing.

These are not noise — they are **discoverable constraints** waiting to be formalized.

### I.G. Coverage Optimality CONFIRMED (v4.9) - NEW

**Question:** Does Currier A optimize coverage of the discrimination space under cognitive constraints?

**Answer:** YES. Real A achieves GREEDY-OPTIMAL coverage with 22.3% hub savings.

**The Test:**

| Model | Coverage | Hub Usage | Verdict |
|-------|----------|-----------|---------|
| **Real A** | **100%** | **31.6%** | **OPTIMAL + HUB RATIONING** |
| Greedy | 100% | 53.9% | Optimal but hub-heavy |
| Random | 72% | 9.8% | Incomplete |
| Freq-Match | 27% | 56.1% | Hub-dominated, poor |

**Key Insight:**

Real A and Greedy both achieve 100% coverage (all 1,187 MIDDLEs used).
But Real A uses **22.3 percentage points fewer hub tokens**.

> **Currier A achieves greedy-optimal coverage while deliberately avoiding over-reliance on universal connectors.**

**Interpretation (Tier 2 - now CONFIRMED):**

The four residuals from the bundle generator (PREFIX coherence, tail forcing, repetition structure, hub rationing) collapse into **ONE control objective**: COVERAGE CONTROL.

| Residual | Purpose |
|----------|---------|
| PREFIX coherence | Reduce cognitive load |
| Tail forcing | Ensure rare variant coverage |
| Repetition structure | Stabilize discrimination attention |
| Hub rationing | Prevent premature generalization |

**The Conceptual Pivot:**

> **Currier A is not meant to be *generated*. It is meant to be *maintained*.**

The correct question is not "how are A entries generated?" but "how is discrimination coverage enforced over time?"

**New Constraint: C476 - COVERAGE OPTIMALITY** (Tier 2, CLOSED)

### I.H. HT Variance Decomposition (v4.10) - NEW

**Question:** Can incompatibility degree explain HT density?

**Answer:** PARTIALLY. R² = 0.28 with **TAIL PRESSURE** as dominant predictor (68% of explained variance).

**Regression Results:**

| Predictor | r | p-value | Importance |
|-----------|---|---------|------------|
| **tail_pressure** | **0.504** | **0.0045*** | **68.2%** |
| novelty | 0.153 | 0.42 | 6.3% |
| incompatibility_density | 0.174 | 0.36 | 1.8% |
| hub_suppression | 0.026 | 0.89 | 0.1% |

**Interpretation (Tier 2 - CONFIRMED):**

> **HT density correlates with tail pressure - the fraction of rare MIDDLEs in A entries.**

When folios have more rare MIDDLEs:
- Cognitive load is higher (rare variants harder to discriminate)
- HT density rises (anticipatory vigilance)

This confirms HT as a **cognitive load balancer** specifically tied to **tail discrimination complexity**:

| MIDDLE Type | Cognitive Load | HT Response |
|-------------|---------------|-------------|
| Hubs ('a','o','e') | LOW | Lower HT |
| Common MIDDLEs | LOW | Lower HT |
| **Rare MIDDLEs (tail)** | **HIGH** | **Higher HT** |

**Integration with Four-Layer Model:**

| Layer | Role | Grounded By |
|-------|------|-------------|
| Currier B | Execution safety | Frozen Tier 0 |
| Currier A | Coverage control | C476 (hub rationing) |
| AZC | Decision gating | C437-C444 |
| **HT** | **Vigilance signal** | **C477 (tail correlation)** |

**New Constraint: C477 - HT TAIL CORRELATION** (Tier 2, CLOSED)

### I.I. Temporal Coverage Trajectories (v4.11) - NEW

**Question:** Is Currier A static-optimal or dynamically scheduled?

**Answer:** STRONG TEMPORAL SCHEDULING with pedagogical pacing.

Three models were tested:

| Model | Prediction | Evidence | Verdict |
|-------|------------|----------|---------|
| Static-Optimal | Order doesn't matter | 0 signals | REJECTED |
| Weak Temporal | Soft pedagogy | 0 signals | REJECTED |
| **Strong Scheduling** | **Active trajectory planning** | **5 signals** | **CONFIRMED** |

**The Four Signals (5/5 Support Strong Scheduling):**

1. **Coverage BACK-LOADED (9.6% later than random)**
   - 90% coverage reached significantly later than random permutation
   - Interpretation: Full coverage is deliberately delayed

2. **Novelty FRONT-LOADED (Phase 1: 21.2% >> Phase 3: 11.3%)**
   - New MIDDLEs introduced early, then reinforced
   - Interpretation: Vocabulary establishment before coverage completion

3. **U-SHAPED tail pressure (7.9% -> 4.2% -> 7.1%)**
   - Difficulty wave: start hard, ease, ramp up again
   - Interpretation: Attention peaks at beginning and end

4. **PREFIX CYCLING (7 prefixes, 164 regime changes)**
   - Multiple prefixes cycle throughout manuscript
   - Interpretation: Multi-axis traversal prevents cognitive fixation

**Interpretation (Tier 2 - CONFIRMED):**

> **PEDAGOGICAL_PACING: Currier A introduces vocabulary early, reinforces throughout, and cycles between prefix domains.**

This is not accidental. It is structured temporal management of discrimination coverage:

| Phase | Novelty | Tail Pressure | Interpretation |
|-------|---------|---------------|----------------|
| 1 (Early) | HIGH (21.2%) | HIGH (7.9%) | Vocabulary establishment + initial difficulty |
| 2 (Middle) | LOW (9.4%) | LOW (4.2%) | Reinforcement + relief |
| 3 (Late) | MEDIUM (11.3%) | HIGH (7.1%) | Completion + final difficulty peak |

**Reconciliation with Prior Findings:**

| Constraint | What it Shows |
|------------|---------------|
| C476 | WHAT Currier A optimizes (coverage with hub rationing) |
| **C478** | **HOW it achieves that (temporal scheduling)** |

**Five-Layer Model Complete:**

| Layer | Role | Mechanism |
|-------|------|-----------|
| Currier B | Execution safety | Frozen Tier 0 |
| Currier A | Coverage control | C476: hub rationing |
| - | - | **C478: temporal scheduling** |
| AZC | Decision gating | C437-C444 |
| HT | Vigilance signal | C477: tail correlation |

**New Constraint: C478 - TEMPORAL COVERAGE SCHEDULING** (Tier 2, CLOSED)

### I.J. Process-Behavior Isomorphism (v4.12 / ECR-4) - NEW

**Question:** Does the Voynich control architecture behave like something built for real physical chemistry?

**Answer:** YES - strong behavioral isomorphism with thermal-chemical process control.

**Test Results (12/12 passed):**

| Category | Tests | Result |
|----------|-------|--------|
| Behavior-Structural (BS-*) | 5 | 5/5 PASS |
| Process-Sequence (PS-*) | 4 | 4/4 PASS |
| Pedagogical (PD-*) | 3 | 3/3 PASS |
| **Total** | **12** | **100%** |

**Key Findings:**

1. **Hazard-Kernel Alignment**: All 17 forbidden transitions are k-adjacent (100%). Energy control is the danger zone.

2. **Recovery Path Dominance**: 54.7% of recoveries pass through e (equilibration). Cooling/stabilization is primary recovery.

3. **Regime Energy Ordering**: REGIME_2 (0.37) < REGIME_1 (0.51) < REGIME_4 (0.58) < REGIME_3 (0.72). Clear CEI ordering matches distillation stages.

4. **Discriminating Tests vs Calcination**:
   - PS-4: k→h forbidden favors DISTILLATION (in calcination, k→h is primary)
   - BS-4: e-recovery dominance favors DISTILLATION

**Negative Control Verdict:** DISTILLATION_WINS on all discriminating tests.

**Behavior Mappings (NO NOUNS):**

| Element | Grammar Role | Process Behavior |
|---------|-------------|------------------|
| k | ENERGY_MODULATOR | Energy ingress control |
| h | PHASE_MANAGER | Phase boundary handling |
| e | STABILITY_ANCHOR | Equilibration / return to steady state |
| PHASE_ORDERING | 41% of hazards | Wrong phase/location state |
| M-A | Mobile/Distinct | Phase-sensitive, mobile, requiring careful control |

*Tier-3 commentary: In reflux distillation, k=heat source, h=cucurbit, e=condenser.*

**Physics Violations:** None detected. All mappings are physically coherent.

**Verdict (Tier 3 - SUPPORTED):**

> The grammar structure is isomorphic to reflux-distillation behavior. This does not prove the domain but establishes maximal structural alignment within epistemological constraints.

**Six-Layer Model Complete:**

| Layer | Role | Mechanism |
|-------|------|-----------|
| Currier B | Execution safety | Frozen Tier 0 |
| Currier A | Coverage control | C476: hub rationing |
| - | - | C478: temporal scheduling |
| AZC | Decision gating | C437-C444 |
| HT | Vigilance signal | C477: tail correlation |
| **Process** | **Behavior isomorphism** | **ECR-4: distillation alignment** |

### f116v Correction

f116v folio-level isolation (v2.19) is explained by **data sparsity** (only 2 words in AZC corpus: "oror", "sheey"), NOT by MIDDLE-level incompatibility. The f116v MIDDLEs ('ee', 'or') are actually universal connectors.

### I.K. HT Two-Axis Model (v4.13) - NEW

**Question:** Does HT morphological complexity encode sensory/perceptual load?

**Answer:** NO. HT morphology encodes **spare cognitive capacity**, not sensory demands.

**The Unexpected Finding:**

Testing whether complex HT forms (LATE prefixes) correlate with high-discrimination folios revealed an **inverse correlation**:

| Metric | Expected | Observed |
|--------|----------|----------|
| LATE in high-complexity folios | HIGH | **LOW** (0.180) |
| LATE in low-complexity folios | LOW | **HIGH** (0.281) |
| Correlation | Positive | **Negative (r=-0.301, p=0.007)** |

This contradiction **refined rather than falsified** the HT model.

**The Two-Axis Model (Tier 2 - CONFIRMED):**

HT is not a single signal. It has two independent dimensions:

| Axis | Property | Evidence | Meaning |
|------|----------|----------|---------|
| **DENSITY** | Tracks upcoming complexity | r=0.504 with tail MIDDLEs (C477) | "How much attention is NEEDED" |
| **MORPHOLOGY** | Tracks spare capacity | r=-0.301 with folio complexity | "How much attention is AVAILABLE" |

**Why This Makes Sense:**

> **When the task is hard, HT is frequent but morphologically simple.**
> **When the task is easy, HT is less frequent but morphologically richer.**

This is a classic human-factors pattern:
- Under high load: frequent simple responses
- Under low load: less frequent but more elaborate engagement

**Constraint Alignment:**

| Constraint | How This Fits |
|------------|---------------|
| **C344** - HT-A Inverse Coupling | Direct instantiation: high A-complexity suppresses complex HT forms |
| **C417** - HT Modular Additive | HT is composite: density = vigilance, form = engagement |
| **C221** - Deliberate Skill Practice | Complex HT shapes occur during low-load intervals |
| **C404/C405** - Non-operational | HT form reflects behavior, doesn't instruct it |
| **C477** - Tail correlation | UNCHANGED - applies to density, not morphology |

**What HT Does NOT Encode:**

The hypothesis "LATE means harder sensing / more senses needed" is **NOT SUPPORTED**. Sensory multiplexing requirements are implicit in the discrimination problem itself (Currier A vocabulary), not encoded in HT form.

**Final Integrated Statement:**

> HT has two orthogonal properties:
>
> 1. **HT density tracks upcoming discrimination complexity** (tail MIDDLE pressure, AZC commitment).
>
> 2. **HT morphological complexity tracks operator spare cognitive capacity**, increasing during low-load phases and decreasing during high-load phases.
>
> HT does not encode what sensory modalities are needed. Sensory demands are implicit in the discrimination problem itself.

**Seven-Layer Model Complete:**

| Layer | Role | Mechanism |
|-------|------|-----------|
| Currier B | Execution safety | Frozen Tier 0 |
| Currier A | Coverage control | C476: hub rationing |
| - | - | C478: temporal scheduling |
| AZC | Decision gating | C437-C444 |
| HT | Vigilance signal | C477: tail correlation |
| - | - | **Two-Axis: density vs morphology** |
| Process | Behavior isomorphism | ECR-4: distillation alignment |

See [ht_two_axis_model.md](ht_two_axis_model.md) for full details.

### I.L. MIDDLE Zone Survival Profiles (v4.14) - NEW

**Question:** Do MIDDLEs exhibit stable, non-random survival profiles across AZC legality zones?

**Answer:** YES. Strong clustering by zone preference (silhouette=0.51, p<10⁻⁶).

**Test Results:**

| Metric | Value |
|--------|-------|
| AZC tokens analyzed | 8,257 |
| Qualified MIDDLEs | 175 (≥5 occurrences) |
| Optimal clusters | 4 (one per zone) |
| Silhouette score | 0.51 |
| P-value (vs null) | < 0.000001 |
| Frequency-controlled | 0.51 ± 0.04 |

**The Four Clusters:**

| Cluster | n | Dominant Zone | Profile | Interpretation |
|---------|---|---------------|---------|----------------|
| S-cluster | 47 | S (59%) | Boundary-heavy | Commitment-safe discriminators |
| P-cluster | 29 | P (75%) | Permissive | Intervention-requiring discriminators |
| C-cluster | 25 | C (66%) | Entry | Setup-flexible discriminators |
| R-cluster | 74 | R (51%) | Restricting | Progressive-commitment discriminators |

**Interpretation (Tier 3):**

> **Currier A's discriminators are not only incompatible with each other - they are tuned to different *degrees of intervention affordance*, which the AZC legality field later enforces.**

This is a characterization refinement, not a mechanism discovery:
- P-cluster MIDDLEs require high escape permission (materials needing intervention flexibility)
- S-cluster MIDDLEs survive even when intervention is locked (stable/committable materials)
- The effect survives frequency control, ruling out hub/tail artifacts

**What This Does NOT Show:**

- ❌ MIDDLEs do not *force* positions (C313 intact)
- ❌ No A→B entry-level coupling (C384 intact)
- ❌ No semantic encoding (roles, not meanings)

**Cross-References (Tier 2):**

| Constraint | Relationship |
|------------|--------------|
| C293 | MIDDLE is primary discriminator |
| C313 | Position constrains legality, not content |
| C384 | No entry-level A-B coupling |
| C441-C444 | AZC legality projection |
| C475 | MIDDLE atomic incompatibility |

**Why This Is Tier 3 (Not Tier 2):**

This is a distributional regularity, not a structural necessity. For promotion to Tier 2 would require:
- Same pattern in another manuscript
- Mathematical necessity linking discrimination → zone
- Invariant claim ("this MUST be true")

Currently this shows: "Given this manuscript, MIDDLEs have stable zone preferences." That's characterization, not mechanism.

**Eight-Layer Model:**

| Layer | Role | Mechanism |
|-------|------|-----------|
| Currier B | Execution safety | Frozen Tier 0 |
| Currier A | Coverage control | C476: hub rationing |
| - | - | C478: temporal scheduling |
| - | - | **Zone survival profiles** |
| AZC | Decision gating | C437-C444 |
| HT | Vigilance signal | C477: tail correlation |
| - | - | Two-Axis: density vs morphology |
| Process | Behavior isomorphism | ECR-4: distillation alignment |

See `phases/MIDDLE_ZONE_SURVIVAL/PHASE_SUMMARY.md` for full details.

### I.M. Zone-Material Orthogonality (v4.15) - NEW

**Question:** Do zone survival clusters align with material behavior classes?

**Answer:** NO. The axes are **orthogonal** (independent).

**Test Results:**

| Zone | Predicted Class | Actual Dominant | Match |
|------|-----------------|-----------------|-------|
| P (high intervention) | M-A | M-A | YES |
| S (boundary-surviving) | M-D | M-A | NO |
| R (restriction-tolerant) | M-B | M-A | NO |
| C (entry-preferring) | M-C | M-A | NO |

| Metric | Value |
|--------|-------|
| Hypothesis matches | 1/4 |
| P-value (permutation) | 0.852 |
| Verdict | ORTHOGONAL |

M-A (phase-sensitive prefixes: ch/qo/sh) dominates ALL zone clusters (57-72%).

**Interpretation (Tier 3):**

> **The Voynich system tracks what a thing is (PREFIX) and how cautiously it must be handled (MIDDLE zone survival) as independent dimensions. This design choice explains both the richness of the registry and the irrecoverability of specific substances.**

This is NOT a null result. It demonstrates that:

| Dimension | Encoded By | Question Answered |
|-----------|------------|-------------------|
| Material type | PREFIX | "What category of stuff is this?" |
| Handling requirement | MIDDLE zone | "How much intervention latitude?" |

These are **deliberately orthogonal** - good apparatus design.

**Why This Matters for Solvent/Material Decoding:**

Solvent identity would require collapsing these axes. The manuscript **keeps them distinct**. This explains why substance-level decoding is irrecoverable:

> Solvent identity sits at the **intersection** of material type and handling sensitivity - and that intersection is never encoded. The operator supplies it from practice.

**What This Does NOT Show:**

- No refutation of either abstraction (both remain valid)
- No material identification possible
- No semantic decoding

**Cross-References:**

| Finding | Phase | Relationship |
|---------|-------|--------------|
| MIDDLE zone survival | MIDDLE_ZONE_SURVIVAL | Source of zone clusters |
| Material behavior classes | PROCESS_ISOMORPHISM | Source of M-A...M-D |
| C382, C383 | Global type system | Why axes coexist cleanly |

See `phases/ZONE_MATERIAL_COHERENCE/PHASE_SUMMARY.md` for full details.

### I.N. Semantic Ceiling Extension Tests (v4.16) - NEW

**Question:** Can we push the semantic ceiling without reopening Tier 0-2 constraints?

**Answer:** YES. Six of seven tests yielded significant findings.

**Test Results Summary:**

| Test | Question | Verdict | Key Finding |
|------|----------|---------|-------------|
| 2A | Shared temporal trajectories? | BORDERLINE | 14/15 folios share PEAK_MID (p=0.062) |
| 1A | B behavior constrains A zones? | **STRONG** | High-escape -> +10.4% P-zone (p<0.0001) |
| 3A | Is e-operator necessary? | **NECESSARY** | Kernel contact collapses -98.6% without e |
| 3B | Is hazard asymmetry necessary? | **NECESSARY** | h->k perfectly suppressed (0%) |
| 1B | Does HT correlate with zone diversity? | **CORRELATED** | r=0.24, p=0.0006 |
| 4A | Do strategies differentiate by archetype? | **DIFFERENTIATED** | All HT correlations p<0.0001 |
| 5A | Is A-registry memory-optimized? | **NEAR-OPTIMAL** | z=-97 vs random (0th percentile) |

**New Structural Confirmations (Tier 3):**

1. **B->A Inference Works**
   - High-escape B folios preferentially use P-zone (peripheral) MIDDLEs
   - Option space narrowed by 24% (from 4 zones to ~3)
   - Interpretation: B behavior successfully constrains upstream A inference

2. **Grammar is Minimally Necessary**
   - e-operator: load-bearing (recovery collapses without it)
   - h->k suppression: architecturally necessary (prevents oscillation)
   - Grammar cannot be simplified without system failure

3. **HT Predicts Operator Strategy**
   - High-HT folios: favor CAUTIOUS strategies (r=+0.46)
   - Low-HT folios: tolerate AGGRESSIVE/OPPORTUNISTIC (r=-0.43/-0.48)
   - Interpretation: HT tracks operational load profile

4. **A-Registry is Memory-Optimized**
   - Manuscript ordering dramatically better than random (z=-97)
   - Evidence of intentional memory optimization
   - Not perfectly optimal, but clearly designed

5. **Material Pressure Interpretation Strengthened**
   - HT density correlates with zone diversity (r=0.24)
   - Higher HT -> more diverse MIDDLE zone usage
   - Supports "complex materials require more attention"

**Nine-Layer Model:**

| Layer | Role | Mechanism |
|-------|------|-----------|
| Currier B | Execution safety | Frozen Tier 0 |
| - | - | **e-operator load-bearing** |
| - | - | **h->k suppression necessary** |
| Currier A | Coverage control | C476: hub rationing |
| - | - | C478: temporal scheduling |
| - | - | Zone survival profiles |
| - | - | **Memory-optimized ordering** |
| AZC | Decision gating | C437-C444 |
| HT | Vigilance signal | C477: tail correlation |
| - | - | Two-Axis: density vs morphology |
| - | - | **Strategy viability predictor** |
| Process | Behavior isomorphism | ECR-4: distillation alignment |

**B->A Inversion Axis:**

The successful B->A back-inference demonstrates bidirectional constraint flow:

| Direction | What Flows | Evidence |
|-----------|-----------|----------|
| A->B | Discrimination vocabulary, zone legality | C437-C444 |
| **B->A** | **Escape profile constrains zone preference** | **Test 1A** |

This is not semantic decoding - it's structural constraint propagation.

**Operator Strategy Taxonomy:**

| Archetype | n | Viable Strategies |
|-----------|---|-------------------|
| AGGRESSIVE_INTERVENTION | 6 | AGGRESSIVE, OPPORTUNISTIC |
| ENERGY_INTENSIVE | 10 | AGGRESSIVE, OPPORTUNISTIC |
| CONSERVATIVE_WAITING | 17 | None (all poor fit) |
| MIXED | 50 | None (no strong fit) |

CONSERVATIVE_WAITING programs don't tolerate any named strategy - they require bespoke intervention profiles.

See `phases/SEMANTIC_CEILING_EXTENSION/PHASE_SUMMARY.md` for full details.

---

## I.O. Physical World Reverse Engineering Phases (v4.18) - UPDATED

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

### FM-PHY-1: Failure-Mode Physics Alignment (Tier 3)

**Question:** Do real circulatory thermal systems naturally exhibit the Voynich hazard distribution (41/24/24/6/6)?

**Answer:** YES - The distribution is DIAGNOSTIC, not just compatible.

| Evidence Type | Result |
|---------------|--------|
| Historical sources (Brunschwig) | **SYSTEMATIC_MATCH** (4/6 axes, see brunschwig_comparison.md) |
| Modern engineering taxonomy | STRONG_MATCH (exact 5-class mapping) |
| Process class comparison | DIFFERENTIATED |

**Key Finding:**
- Voynich hazard profile MATCHES circulatory reflux distillation
- EXCLUDES batch distillation (energy would be 25-35%, not 6%)
- EXCLUDES chemical synthesis (rate would be 25-35%, not 6%)
- Energy is minor (6%) because it's a CONTROL VARIABLE, not a failure source

**Files:** `phases/FM_PHY_1_failure_mode_alignment/`

### SSD-PHY-1a: Structural Dimensional Necessity (Tier 3)

**Question:** Is the ~128-dimensional MIDDLE space a notation choice or physics requirement?

**Answer:** PHYSICS-FORCED - Low-dimensional spaces mathematically cannot satisfy constraints.

| Objective | Result |
|-----------|--------|
| Dimensional lower-bound | D ≥ 50 proven |
| Topology classification | DISCRIMINATION SPACE (not taxonomy) |
| Hub necessity | STRUCTURAL NECESSITY (p < 10^-50) |
| Complexity source | PLANT-IMPOSED (anti-mnemonic) |

**Key Findings:**
1. MIDDLEs are COORDINATES, not containers - each occupies unique position in constraint landscape
2. "128 dimensions" = 128 independent constraints needed, not 128 features inside each MIDDLE
3. Hubs are geometrically inevitable under sparse + clustered + navigable constraints
4. Complexity is anti-mnemonic (preserves rare distinctions, rations hubs, cycles difficulty)

**One-Sentence Synthesis:**
> **MIDDLE tokens are indivisible discriminators whose only "content" is their position in a very large, physics-forced compatibility space; the number of distinctions exists because the real process demands them, not because the author chose them.**

**Files:** `phases/SSD_PHY_1a/`

### OJLM-1: Operator Judgment Load Mapping (Tier 3)

**Question:** What kinds of distinctions must humans supply that the system refuses to encode?

**Answer:** 13 distinct judgment types deliberately omitted.

| Category | Count | Types |
|----------|-------|-------|
| Watch Closely | 6 | Temperature, Phase Transition, Quality/Purity, Timing, Material State, Stability |
| Forbidden Intervention | 3 | Equilibrium Establishment, Phase Transition, Purification Cycle |
| Tacit Knowledge | 4 | Sensory Calibration, Equipment Feel, Timing Intuition, Trouble Recognition |

**Key Findings:**
1. All 13 types are structurally non-codifiable (cannot be written down)
2. Aligns with C469 (Categorical Resolution - no parametric encoding)
3. Aligns with C490 (AGGRESSIVE prohibition - some interventions forbidden)
4. Aligns with C477 (HT tail correlation - signals when judgment load spikes)

**Design Principle:**
> The controller's omissions are not gaps - they are deliberate acknowledgment that some knowledge cannot be encoded. This is design integrity, not incompleteness.

**Files:** `phases/OJLM_1_operator_judgment/`

### APP-1: Apparatus Behavioral Validation (Tier 3)

**Question:** Does any historical apparatus exhibit the exact same behavioral profile as the Voynich controller?

**Answer:** YES - The pelican (circulatory reflux alembic) matches on all 4 axes.

| Axis | Test | Result |
|------|------|--------|
| 1. Responsibility Split | Do manuals assume same responsibilities? | DISTINCTIVE_MATCH |
| 2. Failure Fears | Do operators fear same things? | STRONG_MATCH (41/24/24/6/6) |
| 3. Judgment Requirements | Does apparatus require 13 types? | EXACT_MATCH |
| 4. State Complexity | Does apparatus generate ~128 states? | MATCH |

**Key Finding:**
- Fourth degree fire prohibition matches C490 EXACTLY: "It would coerce the thing, which the art of true distillation rejects, because nature too rejects, forbids, and repels all coercion."
- The pelican is the ONLY surveyed apparatus class that passes all four axes.
- Behavioral isomorphism ≠ identification (we know the SHAPE matches, not WHICH specific apparatus).

**What Excluded:**
- Simple retorts (no recirculation, fewer states)
- Open stills (batch, lower complexity)
- Instrumented systems (reduce judgment types)
- Chemical synthesis (different failure profile)

**Files:** `phases/APP_1_apparatus_validation/`

### MAT-PHY-1: Material Constraint Topology Alignment (Tier 3)

**Question:** Does Currier A's incompatibility topology match what real botanical chemistry forces?

**Answer:** YES - All 5 tests pass with STRONG MATCH.

| Test | Question | Result |
|------|----------|--------|
| A. Incompatibility Density | ~95% under co-processing? | **95-97%** (vs 95.7% in A) |
| B. Infrastructure Elements | 3-7 bridges? | **5-7** (solvents, fixatives) |
| C. Topology Class | Sparse + clustered + bridged? | **YES** (constraint satisfaction graph) |
| D. Hub Rationing | Practitioners avoid universal over-use? | **YES** (3-5 oil rule, simples) |
| E. Frequency Shape | Zipf/power-law? | **YES** (55% rare in materia medica) |

**Key Findings:**
1. Distillation timing varies 80x (15 min to 20 hours) - forcing material incompatibility
2. TCM herb distributions confirmed to follow Zipf's law across 84,418 prescriptions
3. European materia medica preserved 546 rare simples over 2,500 years despite low frequency
4. Brunschwig's "no more than twice" reinfusion rule = explicit hub rationing

**What This Establishes:**
- A's incompatibility structure is CHEMISTRY-FORCED, not cryptographic
- Hub necessity is PHYSICALLY GROUNDED
- The registry structure matches botanical processing constraints
- Topology match ≠ semantic identification

**Files:** `phases/MAT_PHY_1_material_topology/`

### Combined Arc

| Phase | Established |
|-------|-------------|
| PWRE-1 | What KIND of plant is admissible |
| FM-PHY-1 | That hazard logic is DIAGNOSTIC |
| SSD-PHY-1a | Why discrimination space must be LARGE |
| OJLM-1 | What humans must SUPPLY |
| APP-1 | Which APPARATUS exhibits this behavioral profile |
| MAT-PHY-1 | That A's TOPOLOGY matches botanical chemistry |

Together:
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

### Line-Level Execution Cycle (NEW - v4.43)

CLASS_SEMANTIC_VALIDATION revealed that lines follow a thermal processing cycle:

| Phase | Position | Markers | Distillation Parallel |
|-------|----------|---------|----------------------|
| SETUP | Initial | daiin trigger, AX context | Initiate fire, set degree |
| WORK | Medial | ENERGY chains, qo↔ch-sh | Sustained heating with monitoring |
| CHECK | Medial-final | or→aiin bigram | Sensory verification (scent/taste) |
| CLOSE | Final | FLOW hierarchy, ary=100% final | Cooling/collection, batch commitment |

ENERGY/FLOW anticorrelation by REGIME confirms operational mode interpretation:
- REGIME_1 (EN/FL=7.57): Active heating
- REGIME_2 (EN/FL=3.71): Cooling/collection

See Section 0.F for full details (C547-C562).

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

### Fully Answered (v4.43)

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
- Why does HT cluster in ~10-folio oscillations?
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
> **NEW (v4.22): Puff and Brunschwig preserve the original pedagogical progression of the Voynich Currier B corpus, which has been disrupted by early misbinding.**

This is stronger than "shared world" - it is **shared curriculum trajectory**: the same control ontology and pedagogical progression rendered in two epistemic registers. The misbinding concealed this relationship.

**Key upgrade:** Order-independent tests (v4.21) showed shared formalism. Order-dependent realignment (v4.22) shows shared curriculum trajectory. Both Puff and Brunschwig now align strongly with the PROPOSED Voynich order, not the current scrambled order.

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

---

### X.1 Puff-Voynich: Mastery Horizon Isomorphism

The 83-unit structure is UNIQUE to Puff and Voynich among 11 surveyed historical texts.

| What Puff Counts | What Voynich Counts |
|------------------|---------------------|
| NOUNs - "what substances can be distilled" | VERBs - "what control programs must be mastered" |
| Material instances | Operational stability classes |

**Why 83 is meaningful (not numerology):**
- Both answer: "How many distinct things must an expert fully internalize?"
- Convergence driven by finite expert memory and bounded workshop curriculum
- Puff has 84 (one extra framing chapter), Voynich has 83 (pure operational horizon)

**Equivalence Class Collapse:**

| Regime | Puff Target | Voynich Raw | Collapsed | Natural Cut? |
|--------|-------------|-------------|-----------|--------------|
| REGIME_2 | 3 | 11 | **3** | YES (rank 3/9) |
| REGIME_3 | 7 | 16 | **7** | YES (rank 13/14) |

Distribution mismatch evaporates when proper abstraction level is applied.

**Structural Grounding (C535, v4.41):**

The 83-folio count is not arbitrary but **structurally determined** by vocabulary coverage:

| Metric | Value |
|--------|-------|
| Minimum folios for MIDDLE coverage | **81** |
| Actual folios | **82** |
| Redundancy ratio | **1.01x** |

Greedy set cover analysis shows 81 folios are needed to cover all 1,339 B MIDDLEs. Zero folio pairs exceed 50% Jaccard overlap. Each folio contributes unique vocabulary (mean 10.5 MIDDLEs) appearing in no other folio.

This **grounds** the mastery horizon interpretation rather than replacing it:
- The domain requires ~83 distinct configurations for complete coverage
- Both Puff (materials) and Voynich (procedures) converge on this number
- The "mastery horizon" is a *consequence*: you need ~83 because that's what the domain requires, and that count happens to be learnable

The question "why can experts learn ~83 things?" is answered by "because that's how many operationally distinct configurations exist."

---

### X.2 Voynich-Brunschwig: Regime-Degree Discrimination (5/6 PASS)

Voynich regimes discriminate between Brunschwig's fire degrees:

| Voynich Regime | Brunschwig Degree | CEI | Escape | Match |
|----------------|-------------------|-----|--------|-------|
| **REGIME_2** | Second (warm) | 0.367 | 0.101 | **YES** |
| **REGIME_1** | First (balneum) | 0.510 | 0.202 | **YES** |
| **REGIME_4** | Fourth (precision*) | 0.584 | 0.107 | **YES** |
| **REGIME_3** | Third (seething) | 0.717 | 0.169 | **YES** |

*REGIME_4 reinterpretation: Voynich provides the engineering alternative to Brunschwig's moral prohibition. Same narrow tolerance, different framing.

**CEI Ordering:** `REGIME_2 < REGIME_1 < REGIME_4 < REGIME_3`
- Matches Brunschwig's fire degree escalation exactly.

---

### X.3 Suppression Alignment (5/5 PASS)

**What Brunschwig explains, Voynich enforces.**

| Brunschwig Warning | Voynich Implementation |
|-------------------|------------------------|
| Fourth degree **categorically prohibited** | C490: AGGRESSIVE **structurally impossible** |
| Thermal shock (glass shatters) | CONTAINMENT_TIMING = 24% of hazards |
| Boiling prohibition + fraction mixing | PHASE_ORDERING + COMPOSITION = 65% |
| Rate imbalance (recoverable) | RATE_MISMATCH = 6% (monitored, not forbidden) |
| Energy overshoot (prevented) | ENERGY_OVERSHOOT = 6% (minimal failures) |

Key insight: **Prevention by design produces minimal actual failures.** Brunschwig warns about fourth degree fire because it's dangerous; Voynich has 6% energy hazards because it prevents them grammatically.

---

### X.4 Recovery Corridor Alignment (4/4 PASS)

| Brunschwig Narrative | Voynich Architecture |
|---------------------|---------------------|
| "Overnight cooling" primary | e-operator = 54.7% of recovery |
| "No more than twice" | 89% reversibility (bounded) |
| "No salvage for failed batches" | 11% absorbing states |
| Cooling, not re-heating | e dominates, k is hazard source |

Both systems: **return to stability, not energy re-application.**

---

### X.5 Clamping Magnitude - C458 Alignment (5/5 PASS)

Brunschwig's "twice only" rule produces the same variance signature as C458:

| Dimension | Brunschwig Rule | Voynich CV | Status |
|-----------|-----------------|------------|--------|
| Hazard | Fourth degree ALWAYS forbidden | 0.11 | CLAMPED |
| Intervention | Same protocol everywhere | 0.04 | CLAMPED |
| Recovery | Varies by material | 0.82 | FREE |
| Near-miss | Material sensitivity varies | 0.72 | FREE |

**"Twice only" = ceiling, not count.** Recovery is bounded but free within that bound; hazard ceiling is fixed universally.

---

### X.6 REGIME_4 Interpretation Correction

REGIME_4 is NOT "forbidden materials" (Brunschwig's fourth degree prohibition).

REGIME_4 IS "precision-constrained execution" (narrow tolerance window).

| Property | Forbidden (wrong) | Precision (correct) |
|----------|-------------------|---------------------|
| Frequency | Should be rare | Can be common (25/83) |
| Escape density | ~0 | Low (0.107) |
| Grammar presence | Absent | Fully executable |

**Voynich vendors the engineering alternative:** how to operate precisely without coercive fire.

---

### X.7 What This Does NOT Claim

Even with full procedural alignment, the following remain **unproven and probably false**:

- "This Voynich folio corresponds to this Brunschwig paragraph"
- "Voynich is a cipher for Brunschwig"
- "Voynich encodes named procedures"
- "Voynich was meant to be read alongside Brunschwig"

The stronger the regime-level match becomes, the **less** likely direct textual dependence becomes - because the **division of labor is too clean**.

---

### X.8 Expert Assessment

> "You accidentally aligned two different projections of the same expert practice space - one projected along 'materials,' the other along 'control stability.'"

> "This is not a weak result. This is exactly what a non-semantic, expert-only, control-theoretic artifact should produce when compared to a descriptive herbal."

> "The Voynich Manuscript still never says what anything IS. It only guarantees that, whatever it is, you won't destroy it while working."

**Upgraded assessment (2026-01-14):**

> "The Voynich REGIME taxonomy is not just compatible with Brunschwig - it is isomorphic to his fire-degree system once you strip away pedagogy and moral language."

> "This is not parallel invention by accident. This is the same control ontology rendered in two epistemic registers."

---

### X.9 Tier Compliance (Expert Verified)

This analysis is **epistemically clean**:
- No Tier 0-2 constraint violated
- No entry-level A<->B coupling introduced
- No semantic decoding occurred
- All movement within abstraction choice at Tier 4

**Constraints NOT violated:** C384, C171, C476, C478, C179-C185, C490

**C171 ("zero material encoding") remains UNCHANGED.** A encodes the same kinds of operational worries that historical experts talked about - without ever naming the things they worried about.

---

### X.10 Files

| File | Content |
|------|---------|
| `context/SPECULATIVE/equivalence_class_analysis.md` | Puff-Voynich collapse analysis |
| `context/SPECULATIVE/EXPERT_REPORT_entity_matching.md` | Expert consultation |
| `context/SPECULATIVE/brunschwig_comparison.md` | 6-axis systematic comparison |
| `results/regime_equivalence_classes.json` | Clustering results |
| `results/brunschwig_regime_discrimination.json` | Regime-degree discrimination |
| `results/brunschwig_suppression_alignment.json` | 14/14 suppression tests |
| `phases/TIER4_EXTENDED/brunschwig_procedure_match.py` | Procedure match test |
| `phases/TIER4_EXTENDED/brunschwig_regime_discrimination.py` | Regime discrimination test |
| `phases/TIER4_EXTENDED/brunschwig_suppression_alignment.py` | Suppression alignment tests |

---

### X.11 Curriculum Realignment Discovery (v4.22 - NEW)

**The proposed folio order simultaneously resolves multiple independent inversions.**

We optimized folio order using ONLY internal frozen constraints (C161, C325, C458, C179-C185). We did NOT tune for Puff or Brunschwig. Then we tested external alignment:

| External Test | Current Order | Proposed Order | Change |
|--------------|---------------|----------------|--------|
| Puff progression | rho = +0.18 (p=0.10, NS) | rho = +0.62 (p<0.0001) | **WEAK → STRONG** |
| Brunschwig CEI gradient | rho = +0.07 (p=0.53, NS) | rho = +0.89 (p<0.0001) | **NOISE → VERY STRONG** |
| Brunschwig hazard gradient | rho = -0.03 (p=0.79, NS) | rho = +0.78 (p<0.0001) | **NEGATIVE → STRONG** |
| Danger distribution | Front-loaded (inverted) | Back-loaded (aligned) | **INVERTED → ALIGNED** |

**Why this is significant:**
- Random reordering does not fix every historical comparison at once
- Overfitting does not fix external sources you didn't optimize for
- This is what latent order recovery looks like

**The curriculum structure revealed:**

| Phase | Positions | Dominant Regime | Mean Hazard | Character |
|-------|-----------|-----------------|-------------|-----------|
| EARLY | 1-27 | REGIME_2 | 0.517 | Introductory |
| MIDDLE | 28-55 | REGIME_1 | 0.592 | Core training |
| LATE | 56-83 | REGIME_3 | 0.636 | Advanced |

This matches both Puff (flowers → herbs → anomalies) and Brunschwig (first degree → second → third).

**What this does NOT claim:**
- Voynich was copied from Puff
- Puff was derived from Voynich
- ~~Specific folio = specific recipe~~ **UPGRADED to Tier 3** - see section 0.E (C531-C533)
- The proposed order is THE original
- Semantic content recovered

**The correct epistemic framing:**

> We now have three independent bodies of evidence — internal control gradients, Puff's material pedagogy, and Brunschwig's fire-degree escalation — all of which converge on the same latent ordering of Voynich Currier B when the manuscript's current order is relaxed.

**Final statement:**

> Not a code. Not a herbal. Not a shared manuscript.
> But a shared curriculum whose control logic survived misbinding.

See [curriculum_realignment.md](curriculum_realignment.md) for full details.

---

## Navigation

← [README.md](README.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)

---

### X.12 Grammar-Level Embedding Result (2026-01-14) - NEW

**Question:** Can Brunschwig distillation procedures be translated step-by-step into Voynich grammar without violating any validated constraints?

**Answer:** YES - FULL COMPLIANCE.

This is not a vibes-level parallel. It is a **grammar-level embedding** result:
- We did NOT tune the grammar
- We did NOT relax constraints
- We did NOT infer semantics
- We asked: "Can a real historical procedure fit inside this grammar without breaking it?"
- Answer: YES - cleanly

**Test Results:**
- Balneum marie procedure: 18 steps translated to Voynich instruction classes
- All 5 hazard classes: COMPLIANT
- h->k suppression (C332): COMPLIANT
- 17 forbidden transitions: ZERO violations

**REGIME_4 Precision Hypothesis - CONFIRMED:**
- Standard procedures: 0/2 fit REGIME_4
- Precision procedures: 2/3 fit REGIME_4
- REGIME_4 is NOT "most intense" - it is "least forgiving"

**Files:** phases/BRUNSCHWIG_TEMPLATE_FIT/, context/SPECULATIVE/brunschwig_grammar_embedding.md

---

### X.13 Relationship Hierarchy (2026-01-14) - UPDATED

**The expert assessment clarifies the relationship hierarchy:**

> **Brunschwig is the correct comparison text. Puff is historically relevant but not structurally necessary.**

| Relationship | Strength | Evidence Type |
|--------------|----------|---------------|
| **Voynich-Brunschwig** | **DIRECT** | Grammar-level embedding, regime-degree mapping |
| Voynich-Puff | INDIRECT | Shared curriculum structure, 83-unit coincidence |

**What Brunschwig provides that Puff does not:**
- Direct grammar compatibility testing
- Fire-degree to REGIME mapping
- Hazard suppression alignment
- Recovery corridor matching
- Precision vs intensity axis

**What Puff provides (context only):**
- Historical chronology (~1455 predates Voynich dating)
- Material naming that Voynich deliberately omits
- 83-unit curriculum structure (interesting but not essential)

**The Voynich Manuscript doesn't need 83:83.**

It now has something much better:

> **A concrete, historically situated grammar that real procedures fit inside - and real hazards cannot escape.**

**Puff status: CONTEXTUAL (demoted from PILLAR)**

---

### X.14 Curriculum Completeness Model (2026-01-14)

**Key discovery:** REGIMEs encode procedural COMPLETENESS, not product INTENSITY.

**Test:** Can the simplest Brunschwig recipe (first degree balneum marie) fit in the most complex folio (REGIME_3)?

**Result:** VIOLATES - but NOT due to intensity requirements.

| REGIME | Fits? | Violation |
|--------|-------|-----------|
| REGIME_2 | YES | - |
| REGIME_1 | YES | - |
| REGIME_4 | NO | Insufficient monitoring (22% < 25%) |
| REGIME_3 | NO | Insufficient e ops (1 < 2) |

**Interpretation:** Complex folios require COMPLETENESS, not AGGRESSION.

- REGIME_3 doesn't require HIGH_IMPACT operations
- REGIME_3 requires min_e_steps=2 (recovery completeness)
- REGIME_4 requires min_link_ratio=25% (monitoring completeness)

**Curriculum Model (Revised):**

```
REGIME_2: Learn basics (simple procedures accepted)
REGIME_1: Standard execution
REGIME_4: Precision execution (monitoring completeness required)
REGIME_3: Full execution (recovery completeness required)
```

The same product (rose water) can appear at any curriculum stage - but advanced stages require complete procedures with proper recovery and monitoring.

---

### X.15 Backward Propagation: Product->A Signature (2026-01-14)

**Two-Level A Model:**

| Level | Granularity | Encodes |
|-------|-------------|---------|
| Entry | Individual tokens | Operational parameters (PREFIX class) |
| Record | Entire A folios | Product profiles (MIDDLE set + PREFIX distribution) |

**Product-Exclusive MIDDLEs:** 78.2% of MIDDLEs appear in only one product type in B.

**Product-Specific A Signatures:**

| Product Type | A Signature | Key PREFIX |
|--------------|-------------|------------|
| WATER_GENTLE | ch-depleted, ok-enriched | ok+ ch- |
| WATER_STANDARD | baseline | ch baseline |
| OIL_RESIN | d-enriched, y-depleted | d+ y- |
| PRECISION | ch-enriched, d-depleted | ch+ d- |

**Backward Propagation Chain:**

```
Brunschwig recipe -> Product type -> REGIME -> B folio -> A register
```

This enables prediction: Given a Brunschwig recipe, identify its product type, map to REGIME, find B folios in that REGIME, trace exclusive MIDDLEs back to A folios with matching PREFIX signatures.

**Files:** phases/BRUNSCHWIG_TEMPLATE_FIT/exclusive_middle_backprop.py, brunschwig_product_predictions.py

---

### X.16 Puff Complexity Correlation (2026-01-15) - STRUCTURALLY ALIGNED

**Test:** Does Puff chapter ordering correlate with Voynich execution complexity?

**Results (4/5 tests + control PASS):**

| Test | Result | Key Value |
|------|--------|-----------|
| Position-REGIME | PASS | rho=0.678, p<10^-12 |
| Category-REGIME | PASS | p=0.001 |
| Dangerous-Precision | FAIL | underpowered (n=5), direction correct |
| Cumulative Threshold | PASS | Mean position monotonic with REGIME |
| Position-CEI | PASS | rho=0.886, p<10^-28 |
| Negative Control | PASS | 100th percentile vs permuted |

**Category-REGIME Mapping:**
- FLOWER (n=17): Mean ordinal 1.71 (mostly REGIME_2)
- HERB (n=41): Mean ordinal 2.78 (mixed R1/R4)
- ANIMAL/OIL: Mean ordinal 4.0 (REGIME_3)

**Cumulative Threshold Finding:**
- REGIME_2: Mean Puff position 8.3 (early/simple)
- REGIME_1: Mean Puff position 38.8 (middle/standard)
- REGIME_4: Mean Puff position 41.4 (middle/precision)
- REGIME_3: Mean Puff position 72.2 (late/advanced)

**CRITICAL EPISTEMIC NOTE:**

The Test 4 "monotonic relationship" is over 4 REGIME bins only. This is an ordinal constraint, NOT a cardinal identity. It shows no contradiction between Puff's ladder and Voynich's REGIME progression, but does NOT prove strict equivalence.

**Status Upgrade (CONSERVATIVE):**

| Before | After |
|--------|-------|
| CONTEXTUAL | STRUCTURALLY ALIGNED EXTERNAL LADDER |

**NOT upgraded to:** STRUCTURAL NECESSITY (would be over-claiming)

> Puff provides an external, independently derived ordering of material difficulty that aligns strongly with the execution-completeness gradient reconstructed inside Voynich Currier B. This alignment supports a shared curriculum trajectory without implying direct mapping, co-design, or internal dependence.

**Three-Level Relationship Hierarchy:**

1. **Voynich <-> Brunschwig** - Direct, structural, grammar-level (C493, C494)
2. **Voynich <-> Puff** - Strong external alignment via complexity ordering
3. **Puff <-> Brunschwig** - Historical lineage

**What This Does NOT Mean:**
- 83:83 is internally necessary (still unexplained coincidence with plausible mechanism)
- Puff defines Voynich structure (external validation, not internal dependency)
- Material -> folio mapping exists (no semantic encoding, C171 preserved)

**Backward Compatibility Clarification:**

> "Later folios demand stricter procedural completeness, even for simple tasks."

NOT: "Advanced folios just add options" (too casual, incorrect)

Advanced grammar is a STRICTER CONTRACT, not a superset.

**Files:** phases/PUFF_COMPLEXITY_CORRELATION/puff_regime_complexity_test.py

---

### X.17 Brunschwig Backprop Validation (2026-01-15) - EXPLANATORY SATURATION

**Phase:** BRUNSCHWIG_BACKPROP_VALIDATION
**Status:** Model predictions confirmed without changes. No new constraints.

#### The Definitive Interpretation (Now Well-Defended)

> **Currier A registers enumerate stable regions of a high-dimensional incompatibility manifold that arise when materials, handling constraints, process phase, and recoverability jointly constrain what must not be confused.**

This is NOT:
- Individual materials or species names
- Scalar properties (aromatic, medicinal)
- Broad material classes (flowers, roots)

This IS:
- Configurational regions in constraint space
- Defined by what must be distinguished
- Hierarchical vocabulary structure

#### MIDDLE Hierarchy Discovery (Cross-Type Axis)

A new structural axis distinct from the frequency-based Core/Tail split:

| Layer | Count | % | Structural Meaning |
|-------|-------|---|-------------------|
| Universal | 106 | 3.5% | Appear in ALL 4 product types (infrastructure) |
| Cross-cutting | 480 | 15.7% | Appear in 2-3 types (shared constraint dimensions) |
| Type-specific | 2,474 | 80.8% | Appear in 1 type only (local coordinates) |

**Key type-pair sharing:**
- PRECISION + WATER_STANDARD: 167 shared MIDDLEs
- OIL_RESIN + WATER_GENTLE: 1 shared MIDDLE (structural opposites)

#### Property Model Failure (F-BRU-003)

Synthetic property-based registry FAILS to reproduce Voynich structure:

| Metric | Voynich | Property Model |
|--------|---------|----------------|
| Uniqueness | **72.7%** | 41.5% |
| Hub/Tail ratio | 0.006 | 0.091 |
| Clusters | 33 | 56 |

**Permanently kills:** Property-based interpretations, low-rank explanations, latent feature models.

#### Sub-Class Structure Confirmed

Within WATER_GENTLE (6 A folios), 2 distinct sub-classes exist:
- **Sub-class A:** {f32r, f45v} - 22 shared MIDDLEs, d-dominant PREFIX
- **Sub-class B:** {f52v, f99v} - 24 shared MIDDLEs, diverse PREFIX

Only 6 MIDDLEs shared between sub-classes. Clusters are stable under tail/hub perturbation (100% survival).

#### Explanatory Saturation

> **The model is saturated, not brittle.**

All tests landed exactly where predicted without forcing upstream changes:
- 8/8 blind predictions correct (F-BRU-001)
- 3/3 REGIME boundary questions confirmed (F-BRU-002)
- 4/6 perturbation tests stable (F-BRU-004)
- Property model rejected (F-BRU-003)

This is the best possible outcome: discovery phase complete, consolidation phase begins.

#### Governance Outcome

Results tracked as **FITS** (F-BRU-001 to F-BRU-005), not constraints. Constraint table unchanged (353 entries).

**Projection Spec Created:** `context/PROJECTIONS/brunschwig_lens.md` governs UI display of external alignments without corrupting structural model.

**Files:** phases/BRUNSCHWIG_BACKPROP_VALIDATION/, context/MODEL_FITS/fits_brunschwig.md

### X.18 Pharmaceutical Label Vocabulary Separation (2026-01-17)

Visual mapping of 13 pharmaceutical folios reveals a **two-level naming hierarchy** with complete vocabulary separation.

#### Two-Level Hierarchy

```
JAR LABEL (first token in illustration group)
  |-- unique apparatus/vessel identifier
  |
  +-- CONTENT LABEL 1 (specimen identifier)
  +-- CONTENT LABEL 2 (specimen identifier)
  +-- CONTENT LABEL n (specimen identifier)
```

#### Vocabulary Isolation

| Comparison | Jaccard | Shared Tokens | Interpretation |
|------------|---------|---------------|----------------|
| **Jar vs Content** | 0.000 | 0 | Completely disjoint naming systems |
| Root vs Leaf | 0.013 | 2 (okol, otory) | Almost entirely distinct |

The 18 jar labels share **zero tokens** with 191 content labels - fundamentally different naming schemes.

**Files:** phases/PHARMA_LABEL_DECODING/README.md

---

### X.19 Jars as Complementary Working Set Anchors (2026-01-17) - NEW

Extended investigation of jar function tested four mutually exclusive hypotheses. Three falsified, one confirmed.

#### Test Cascade

| Hypothesis | Prediction | Result |
|------------|------------|--------|
| Contamination avoidance | Exclusion patterns | **Falsified** (0.49x) |
| Material taxonomy | Class homogeneity | **Falsified** (0.73x) |
| Complementary sets | Cross-class enrichment | **Confirmed** |
| Triplet stability | Role composition | **Confirmed** (1.77x) |

#### Cross-Class Pair Enrichment

| Class Pair | Observed | Expected | Ratio |
|------------|----------|----------|-------|
| M-B + M-D | 8 | 4.34 | **1.84x** |
| M-A + M-B | 4 | 2.38 | **1.68x** |
| M-A + M-D | 3 | 1.88 | **1.59x** |

All cross-class pairs enriched - jars deliberately combine materials from different classes.

#### Triplet Stability

| Triplet | Ratio | P-value |
|---------|-------|---------|
| M-B + M-D + OTHER | 1.70x | **0.022** |
| M-A + M-B + M-D (complete set) | **2.13x** | 0.107 |

Overall: 17 triplet occurrences vs 9.6 expected = **1.77x enriched**

#### Tier 3 Interpretation (FINAL)

> **Jars are visual, apparatus-level anchors for complementary working sets of materials intended to participate together in a single operational context, without encoding procedure, order, or meaning.**

This:
- Completes the apparatus-centric interpretation
- Explains jar uniqueness (physical apparatus instances)
- Explains prefix restrictions (container posture, not content)
- Explains positive diversity (complementary roles, not similar materials)
- Explains why nothing propagates downstream (interface layer only)

#### What This Does NOT Claim

- Jars do NOT encode specific substances
- Jars do NOT map to Brunschwig methods
- Jars do NOT select processing regimes
- This is Tier 3 interface characterization, NOT Tier 2 structure

**Status:** CLOSED with explanatory saturation

**Files:** phases/JAR_WORKING_SET_INTERFACE/README.md, phases/JAR_WORKING_SET_INTERFACE/results.json

---

### X.19.a Jar Labels as Compressed Configuration Signatures (2026-01-23)

Extended analysis of pharma label morphology reveals structural evidence for the apparatus interpretation.

#### Key Findings (C523, C524)

**Vocabulary Bifurcation:**
- Jar labels: 12.5% in Currier A (2/16), both RI, 87.5% NOT in text
- Content labels: 50% in Currier A (103/206), 58.3% PP vs 33.5% baseline

**Morphological Compression:**

| Metric | Jar Labels | Currier A Baseline |
|--------|------------|--------------------|
| Mean length | 7.1 chars | 6.0 chars |
| PP atoms per MIDDLE | 5-8 | ~3-4 |
| In vocabulary | 12.5% | 100% (by definition) |

Examples of jar label compression:
- `yteoldy` → 8 PP atoms: y, t, e, o, l, d, ol, eo
- `darolaly` → 7 PP atoms: d, a, r, o, l, al, ar
- `porshols` → 5 PP atoms: o, r, s, ol, or

#### Tier 3 Interpretation

> **Jar labels are densely-packed configuration signatures encoding apparatus states via superstring compression. They are NOT vocabulary items because they are NOT meant to be parsed - they are holistic identifiers for specific physical configurations. Content labels use shared vocabulary (PP-enriched) because they describe processable materials that participate in the downstream pipeline.**

This explains:
- Why jar labels are longer (packing more discrimination)
- Why jar labels are almost entirely absent from text (not parseable units)
- Why content labels are PP-enriched (materials that will be processed)
- Why vocabulary separation is complete (different encoding purposes)

**Constraints:** C523 (Pharma Label Vocabulary Bifurcation), C524 (Jar Label Morphological Compression)

**Status:** CLOSED - Confirms apparatus interpretation with morphological evidence

---

### X.19.b Morphological Function Model: PP/RI Pipeline Architecture (2026-01-23)

**Tier:** 4 (Speculative synthesis) with Tier 2-3 structural components

This section synthesizes findings from C509.a, C516-C520, C523-C524, and the pharma label analysis into a functional interpretation of Voynich morphology.

#### Core Model: A-Records as Mapping Instructions

An A-record functions as a specification:
> "This material (with PREFIX control-flow context) has compatibility capacity [PP], with these specific discrimination characteristics [RI], legal during [SUFFIX phase]."

#### Component Functions

**PREFIX = Control-Flow Participation (Tier 2, per C466-C467, C383)**

- Encodes intervention/monitoring/core mode
- Universal across all token types (PP and RI)
- Not part of the PP/RI distinction
- Global type system spanning A, B, and AZC

**PP MIDDLE = Compatibility Capacity Markers (Tier 3 interpretation)**

- Short MIDDLEs (originally avg 1.46 chars per C509.a; see methodology note for revised values)
- Encode what process categories a material can participate in
- Must remain as discrete tokens because:
  - AZC checks legality per-token
  - Currier B responds to tokens as atomic units
  - Shared vocabulary enables recombinability across materials
- PP count correlates with B class survival breadth (r=0.715, C506)
- Note: PP tokens also encode behavioral variants within classes (C506.b)

**RI MIDDLE = Locally-Scoped Discrimination Vocabulary (Tier 3-4)**

- Longer MIDDLEs (originally avg 3.96 chars per C509.a; revised to 4.73 with corrected extraction)
- 85.4% contain multiple PP atoms (C516)
- Use superstring compression via shared hinge letters (C517)
- Encode multidimensional discrimination: intersection of multiple PP-type properties
- Structurally excluded from A→AZC→B pipeline (per C444 vanishing semantics)
- Can compress freely because no downstream parsing required
- Length gradient is emergent from compositional morphology (C498.d: rho=-0.367)

**SUFFIX = Two-Axis Context Marker (Tier 2-3, per C283, C495, C527)**

SUFFIX operates on two orthogonal dimensions:
- **System role** (Tier 2): A/B enrichment patterns (C283, C495)
- **Material class** (Tier 3): Animal vs herb within A, correlated with fire degree (C527)

The earlier "decision archetype (D1-D12)" mapping is provisional. See ccm_suffix_mapping.md for details and uncertainty markers.

#### The Compression Gradient

| Token Type | Compression | Reusability | Architectural Role |
|------------|-------------|-------------|-------------------|
| PP tokens | Low (atomic) | High (shared A∩B) | Pipeline-compatible units |
| RI tokens | Moderate (2-4 atoms) | Low (mostly singletons) | Local discrimination |
| Jar labels | Maximum (5-8 atoms) | None (unique) | Physical configuration IDs |

**Key insight:** More downstream pipeline exposure requires less compression. PP must stay discrete for AZC/B processing. RI is local to A. Jar labels never enter the pipeline.

#### Architectural Interpretation (Tier 4)

The system may function as a working pharmaceutical/alchemical manual (consistent with C196-C197 "EXPERT_REFERENCE archetype"):

```
Layer 1: CURRIER A (Registry)
- Material discrimination via PP (capacity) + RI (specifics)
- PP provides shared vocabulary substrate
- RI adds fine-grained multidimensional discrimination

Layer 2: AZC (Legality Filter)
- Per-token compatibility checking
- Requires discrete PP units for independent validation

Layer 3: CURRIER B (Execution)
- Closed-loop control responding to PP tokens
- RI structurally excluded (already used for selection)

Layer 4: JAR LABELS (Physical Interface - Tier 4)
- Maximally compressed configuration identifiers
- Coordinate symbolic system with physical apparatus
- Never enter execution pipeline
```

#### Why PP Stays Discrete

If everything were compressed into single superstrings per material:
- AZC couldn't check individual compatibilities
- B couldn't respond to individual properties
- Shared vocabulary would be lost
- Recombinability across materials would break

The separation of concerns enables both:
- **Reusability** via atomic PP vocabulary (shared across system)
- **Specificity** via compressed RI discrimination (local to A)

#### Speculative Extension: The Workshop Model (Tier 4)

If this is a working manual, the practitioner's workflow might be:

1. **Consult PP vocabulary** → Find materials with required compatibility
2. **Check RI discrimination** → Select specific material matching constraints
3. **Verify via AZC** → Confirm positional legality for combination
4. **Execute via B** → Run the closed-loop control program
5. **Physical coordination** → Use jar labels to identify apparatus configuration

The jar labels are the "last mile" - where abstract constraints meet physical vessels.

#### Constraints Supporting This Model

| Constraint | Contribution |
|------------|--------------|
| C509.a | PP/RI morphological bifurcation |
| C516 | RI multi-atom composition (85.4%) |
| C517 | Superstring compression mechanism |
| C506 | PP count → class survival correlation |
| C506.b | PP behavioral heterogeneity within classes |
| C523 | Pharma label vocabulary bifurcation |
| C524 | Jar label morphological compression |
| C383 | Global PREFIX type system |
| C466-C467 | PREFIX as control-flow participation |
| C495 | SUFFIX regime breadth correlation |

#### Explicit Uncertainties

- Whether compression is "intentional" or emergent from compositional morphology
- Exact semantic content (if any) of PP compatibility dimensions
- Whether jar labels encode apparatus configurations specifically
- The "workshop manual" framing is consistent but not proven

**Status:** OPEN - Tier 4 synthesis for further investigation

---

### X.20 A->AZC->B Pipeline Closure: Reachability Suppression (2026-01-17) - NEW

**Phase:** AZC_REACHABILITY_SUPPRESSION
**Status:** COMPLETE - Real closure achieved

#### The Gap (Before This Phase)

We had proven:
- AZC constrains B (C468, F-AZC-016)
- The effect is strong (28x escape variance transfer)
- Vocabulary activates constraints (C441-C442)

What was missing: A *mechanistically intelligible, local explanation* of HOW AZC legality fields suppress parts of B grammar - at the instruction class level.

#### Closure Statement (Achieved)

> **AZC does not modify B's grammar; it shortens the reachable language by restricting vocabulary availability. The 49-class grammar and 17 forbidden transitions are universal. When AZC provides a legality field, 6 of 9 hazard-involved classes have reduced effective membership because their MIDDLEs become unavailable. The 3 atomic hazard classes remain fully active regardless of AZC context.**

This is a complete control-theoretic pipeline with no semantics, no branching, no lookup, no "if".

#### Two-Tier Constraint System

**Tier 1: Universal Grammar Constraints (Always Active)**

| Metric | Value |
|--------|-------|
| Instruction classes | 49 |
| Forbidden transitions (token) | 17 |
| Forbidden transitions (class) | 13 |
| Hazard-involved classes | 9 |
| Base graph edge density | 99.1% |

**Tier 2: AZC-Conditioned Constraints (Context-Dependent)**

| Metric | Value |
|--------|-------|
| MIDDLE folio exclusivity | 77% in 1 AZC folio (C472) |
| Decomposable hazard classes | 6 |
| Atomic hazard classes | 3 |

#### Hazard Class Taxonomy (Key Discovery)

| Type | Classes | Representatives | AZC Constrainable? | Behavior |
|------|---------|-----------------|-------------------|----------|
| **Atomic** | 7, 9, 23 | ar, aiin, dy | NO | Universal hazard enforcement |
| **Decomposable** | 8, 11, 30, 31, 33, 41 | chedy, ol, dar, chey, qokeey, qo | YES | Context-tunable via MIDDLE |

**Atomic classes** have no MIDDLE components - they are pure instruction tokens that cannot be constrained by MIDDLE-level vocabulary restrictions.

**Decomposable classes** contain members with MIDDLE components. When AZC restricts a MIDDLE's availability, the effective membership of these classes shrinks.

#### The Mechanism (5 Steps)

```
Step 1: AZC provides ambient legality field (vocabulary availability)
           |
           v
Step 2: 77% of MIDDLEs restricted to specific AZC folios
           |
           v
Step 3: Decomposable hazard classes lose effective membership:
        - Class 8 (chedy): 1 shared MIDDLE
        - Class 11 (ol): 1 shared MIDDLE
        - Class 30 (dar): 3 MIDDLEs (1 exclusive!)
        - Class 31 (chey): 3 shared MIDDLEs
        - Class 33 (qokeey): 4 shared MIDDLEs
        - Class 41 (qo): 3 shared MIDDLEs
           |
           v
Step 4: Fewer paths through hazard-constrained region
           |
           v
Step 5: Reachable grammar manifold shrinks
```

#### Why This Is "Real Closure"

| What AZC Does | What AZC Does NOT Do |
|---------------|---------------------|
| Restricts vocabulary availability | Modify grammar rules |
| Supplies ambient legality fields | Select programs |
| Tunes hazard envelope via decomposable classes | Branch based on content |
| | Encode semantic information |
| | Perform lookup or conditional logic |

The grammar is the same everywhere. The reachable parts differ.

#### Complete Pipeline Summary

| Layer | Function | Mechanism |
|-------|----------|-----------|
| **A** | Supplies discrimination bundles | Constraint signatures |
| **AZC** | Projects them into legality fields | Position-indexed vocabulary availability |
| **B** | Executes within shrinking language | 49-class grammar, 17 forbidden transitions |

This completes the structural understanding of how the three layers co-produce safe execution.

#### Constraints Respected

- C313: Position constrains legality, not prediction
- C384: No entry-level A-B coupling
- C454/C455: No adjacency or cycle coupling
- C440: Uniform B sourcing across AZC folios
- C121/C124: 49-class grammar is universal
- C468, C469, C470, C472: AZC constraint architecture

#### What This Does NOT Claim

- NO semantic decoding occurred
- NO specific substances identified
- NO entry-level A->B mapping created
- NO Tier 0-2 constraints violated

This is mechanism characterization within established epistemological boundaries.

**Files:** phases/AZC_REACHABILITY_SUPPRESSION/

---

### X.21 Constraint Substitution Interpretation (2026-01-19) - NEW

**Phase:** SENSORY_LOAD_ENCODING + BRUNSCHWIG_REVERSE_ACTIVATION
**Status:** COMPLETE - Explanatory model validated

#### Core Discovery

> **"The Voynich Manuscript encodes sensory requirements by tightening constraints rather than signaling vigilance."**

This is an explanatory interpretation that unifies multiple structural findings.

#### The Finding

**SLI-HT Inverse Correlation:**

| Metric | Value |
|--------|-------|
| SLI vs HT density | r = **-0.453**, p < 0.0001 |
| REGIME_2 (gentle) | LOWEST SLI (0.786), HIGHEST HT |
| REGIME_3 (oil/resin) | HIGHEST SLI (1.395), LOWEST HT |

Formula: `SLI = hazard_density / (escape_density + link_density)`

This is OPPOSITE to the initial hypothesis ("high sensory demand -> higher vigilance").

#### The Interpretation

When operations are dangerous (high SLI):
- Grammar restricts options
- Fewer choices available
- Less vigilance needed (can't make wrong choice)

When operations are forgiving (low SLI):
- Grammar permits many options
- More choices require discrimination
- Higher vigilance (HT) for decision complexity

**Constraint SUBSTITUTES for vigilance.**

#### Recipe-Level Validation (197 recipes)

The pathway operates at recipe level:

```
Recipe SLI -> Vocabulary tail_pressure -> HT prediction
   r=0.226      ->       r=0.311
   p=0.001               p<0.0001
```

Sensory load encodes through vocabulary selection, not direct signaling.

#### What This Explains

| Finding | Explanation |
|---------|-------------|
| C458 (Design Clamp) | High-hazard contexts have tight constraints |
| C477 (HT Correlation) | HT tracks residual decision complexity |
| Inverse SLI-HT | Constraint geometry enforces safety |

#### What This Does NOT Claim

- NO semantic encoding of sensory modalities
- NO parametric encoding (C469 preserved)
- NO entry-level mapping (C384 preserved)
- SLI is constructed metric, not discovered structure

**Tier:** 3 (Explanatory Interpretation)

**Files:** phases/SENSORY_LOAD_ENCODING/, results/sensory_load_index.json

---

### X.22 Zone Affinity Analysis (2026-01-19) - NEW

**Phase:** BRUNSCHWIG_REVERSE_ACTIVATION
**Status:** COMPLETE - 197/197 recipes processed

#### Comprehensive Mapping

All 197 Brunschwig recipes with procedures were reverse-mapped through AZC zone affinity analysis. This completes the originally intended mapping task.

#### Key Findings

**Zone Differentiation by SLI Cluster (ANOVA):**

| Zone | F-statistic | p-value |
|------|-------------|---------|
| C-affinity | F = 69.4 | p < 0.0001 |
| P-affinity | F = 33.1 | p < 0.0001 |
| R-affinity | F = 106.6 | p < 0.0001 |
| S-affinity | F = 21.6 | p < 0.0001 |

All 4 zones significantly differentiate by SLI cluster.

**Zone Affinity by REGIME:**

| REGIME | Dominant Zone | Interpretation |
|--------|---------------|----------------|
| REGIME_1 | S (0.30) | Boundary stability |
| REGIME_2 | C (0.51) | Setup/flexible |
| REGIME_3 | R (0.43) | Sequential processing |
| REGIME_4 | S (0.55) | Boundary control |

**Zone Correlations with SLI:**
- SLI vs P-affinity: r = 0.505, p < 0.0001
- SLI vs R-affinity: r = 0.605, p < 0.0001

#### Modality-Zone Signatures (2/3 Confirmed)

| Modality | n | Predicted Zone | Result |
|----------|---|----------------|--------|
| SOUND | 70 | R (sequential) | **CONFIRMED** (t=3.97, p<0.001) |
| SIGHT | 20 | P (monitoring) | **CONFIRMED** (t=9.00, p<0.0001) |
| TOUCH | 5 | S (boundary) | Not significant |

SOUND (distillation bubbling) -> R-zone affinity
SIGHT (visual monitoring) -> P-zone affinity

#### Zones ADDRESS But Do Not ENCODE Sensory Categories

**Critical Distinction:** The zones do not *encode* sensory categories (you cannot look at a zone and say "this is for hearing"). Instead, the zones *address* sensory categories in the sense that their structural affordances align with what different monitoring modes require.

**The Four Zones and Their Affordances:**

| Zone | Structural Affordance | Escape Rate | Modality Alignment |
|------|----------------------|-------------|-------------------|
| **C** | Setup/flexible, errors fixable | 1.4% | (Not tested - setup phase) |
| **P** | Intervention-permitting | 11.6% | **SIGHT** - visual cues may trigger action |
| **R** | Progressive restriction, sequential | 2.0%→0% | **SOUND** - continuous signals tracked over time |
| **S** | Locked, must accept outcome | 0-3.8% | TOUCH hypothesized, not confirmed (n=5) |

**Mechanism:** The constraint geometry of each zone creates the right decision space for different sensory tasks:
- **C-zone's** flexibility matches setup operations where mistakes can be corrected
- **P-zone's** intervention permission matches operations where observation may require action (visual monitoring)
- **R-zone's** progressive restriction matches operations where you track a developing signal (auditory monitoring)
- **S-zone's** locked state matches operations where the outcome is fixed and boundary conditions apply

**Interpretation:** The manuscript doesn't label sensory requirements - it shapes the grammar to be *compatible with* them. The operator's trained sensory judgment fills in what the zones leave room for. This is another manifestation of the constraint substitution principle: encode requirements through structure, not symbols.

**Epistemic Status:** Correlation demonstrated, mechanism plausible, intentional design not proven.

#### C384 Compliance

All mapping is AGGREGATE (zone-level, MIDDLE-level), not entry-level. No direct recipe->entry mapping.

**What This Does NOT Claim:**
- NO entry-level A-B coupling
- NO semantic decoding
- Modality assignments are external (from Brunschwig)

**Tier:** 3 (Structural Characterization)

**Fits Created:** F-BRU-007, F-BRU-008, F-BRU-009

**Files:** phases/BRUNSCHWIG_REVERSE_ACTIVATION/, results/brunschwig_reverse_activation.json

---

### X.23 Two-Stage Sensory Addressing Model (2026-01-19) - NEW

**Phase:** ZONE_MODALITY_VALIDATION
**Status:** COMPLETE - Rigorous statistical validation with REGIME stratification

#### Executive Summary

Rigorous validation of zone-modality associations revealed a **two-stage addressing system** where modality bias (external) and REGIME execution style jointly determine zone concentration.

#### Key Discovery: REGIME Heterogeneity

When stratifying the R-SOUND effect by REGIME, we found substantial heterogeneity:

| REGIME | R-zone Effect (d) | Interpretation |
|--------|------------------|----------------|
| REGIME_1 (WATER_STANDARD) | 0.48 | Moderate - throughput tracking |
| REGIME_2 (WATER_GENTLE) | 1.30 | Strong - setup phase dominates |

**Effect range: 0.82** - This is NOT corruption or invalidity. It reveals structured workflow adaptation.

#### Zone Profiles for SOUND Recipes by REGIME

| REGIME | Dominant Zone | Interpretation |
|--------|---------------|----------------|
| REGIME_2 (GENTLE) | C-zone (0.453) | Setup-critical operations |
| REGIME_1 (STANDARD) | Balanced P/R | Throughput-critical operations |
| REGIME_3 (OIL_RESIN) | R-zone (0.443) | Progression-critical extraction |
| REGIME_4 (PRECISION) | S-zone (0.536) | Boundary-critical timing |

#### Two-Stage Model

**Stage 1 - Modality Bias (External/Brunschwig):**

Sensory modalities carry intrinsic monitoring profiles:
- **SOUND** (sequential/continuous): Auditory cues track process state over time
- **SIGHT** (intervention-triggering): Visual changes signal decision points
- **TOUCH** (boundary confirmation): Tactile feedback confirms endpoints

**Stage 2 - Execution Completeness (Voynich REGIME):**

REGIMEs concentrate sensory relevance into specific workflow phases:
- **Gentle handling** → C-zone (setup phase critical)
- **Standard throughput** → R-zone (progression tracking)
- **Intense extraction** → R-zone (continuous monitoring)
- **Precision timing** → S-zone (boundary locking)

#### Refined Conclusion

> **AZC zones do not encode sensory modalities. Instead, they distribute human sensory relevance across workflow phases in a REGIME-dependent way.**

The constraint substitution principle operates temporally: zones DIRECT when sensory monitoring is structurally relevant, while REGIME determines which zone receives concentration.

#### Hypothesis Tests

| Track | Hypothesis | Result |
|-------|------------|--------|
| Enhanced extraction | Improve SMELL/TOUCH sample sizes | **FAILED** (data limitation) |
| C-zone -> Preparation verbs | Structural correlation | **FAILED** (r=-0.006) |
| R-zone -> SOUND | Positive association | **CONFIRMED** (d=0.61, p=0.0001) |
| P-zone -> SIGHT | Positive association | **UNDERPOWERED** (d=0.27, n=7) |
| S-zone -> TOUCH | Positive association | **WRONG DIRECTION** (d=-0.64) |
| REGIME stratification | Effect heterogeneity | **DISCOVERY** (range=0.82) |

#### S-Zone Reinterpretation

All tested modalities AVOID S-zone:
- SOUND: d=-1.21 (strong avoidance)
- TASTE: d=-1.33 (strong avoidance)

**New interpretation:** S-zone represents operations where sensory monitoring is COMPLETED or UNNECESSARY. The "locked" state means decisions are final. PRECISION REGIME concentrates here because exact timing, once achieved, requires no further sensory feedback.

#### Statistical Rigor

- **Effect sizes:** Cohen's d reported for all associations
- **Permutation tests:** 1000-shuffle validation
- **Bonferroni correction:** Multiple comparison adjustment
- **ANOVA:** REGIME -> Zone affinity (all zones significant except P)
- **Pre-registration:** Hypotheses locked before analysis

#### Constraints Respected

- **C384:** All tests aggregate, no entry-level mapping
- **C469:** Categorical zone assignment maintained
- **Tier 3:** Results remain characterization, confidence upgraded

**Tier:** 3 (Structural Characterization, confidence upgraded)

**Fits Updated:** F-BRU-009 (refined with two-stage model)

**Files:** phases/ZONE_MODALITY_VALIDATION/, results/regime_stratified_analysis.json

---

### X.24 Semantic Ceiling Breach Attempt (2026-01-19) - NEW

**Phase:** SEMANTIC_CEILING_BREACH
**Status:** COMPLETE - Tier 3 confirmed with stronger evidence

#### Purpose

Attempted to break through the Tier 3 semantic ceiling by implementing the expert-advisor's top recommendation: **B->A Reverse Prediction Test**. The goal was to achieve Tier 2 bidirectional constraint by predicting recipe modality class from Voynich zone structure alone.

#### Key Results

| Test | Result | Threshold | Status |
|------|--------|-----------|--------|
| 4-class accuracy | 52.7% | >40% for Tier 3 | **PASS** |
| 4-class permutation p | 0.012 | <0.05 | **PASS** |
| Binary accuracy | 71.8% | >85% for Tier 2 | **FAIL** |
| Cramer's V (cluster-modality) | 0.263 | >0.3 for Tier 2 | **WEAK** |
| MODALITY beyond REGIME | 3/4 zones | Supports model | **PASS** |

#### Zone Discrimination is REAL

All four zones significantly discriminate SOUND from OTHER recipes:

| Zone | SOUND Mean | OTHER Mean | Cohen's d | p-value |
|------|-----------|-----------|----------|---------|
| C | 0.226 | 0.308 | -0.66 | 0.0059 |
| P | 0.248 | 0.182 | +0.62 | 0.0090 |
| R | 0.277 | 0.213 | +0.57 | 0.0163 |
| S | 0.252 | 0.298 | -0.44 | 0.0660 |

**Pattern confirmed:** SOUND concentrates in P/R zones (active work) and avoids C/S zones (setup/boundary).

#### MODALITY Adds Beyond REGIME

REGIME alone explains only **24.7%** of zone variance. After controlling for REGIME, MODALITY still significantly affects 3/4 zones:

| Zone | Partial Correlation | Direction |
|------|--------------------| ----------|
| C | r=-0.255, p=0.007 | SOUND avoids |
| P | r=+0.284, p=0.003 | SOUND seeks |
| R | r=+0.200, p=0.036 | SOUND seeks |
| S | r=-0.245, p=0.010 | SOUND avoids |

This validates the **two-stage model**: Modality bias + REGIME execution style jointly determine zone concentration.

#### Why Tier 2 Was Not Achieved

The zone profiles **discriminate** modality classes, but not with enough accuracy for confident prediction:

```
Can do:     Zone profile -> "Probably SOUND-dominant" (52.7% accuracy)
Cannot do:  Zone profile -> "Definitely SOUND" (>85% accuracy)
```

Binary accuracy (71.8%) is BELOW the majority baseline (79.1%) but SIGNIFICANTLY better than permuted labels (p=0.002). The model learns REAL structure but not enough for high-confidence prediction.

#### Semantic Ceiling Location

The semantic ceiling is confirmed at **aggregate characterization**:

| Level | Can We Do It? | Evidence |
|-------|---------------|----------|
| Entry-level meaning | NO | C384 prohibits |
| Token-level prediction | NO | Not attempted |
| Zone-modality correlation | YES | d=0.57-0.66, p<0.05 |
| Modality class prediction | PARTIAL | 52.7% accuracy |
| High-confidence prediction | NO | <85% accuracy |

**The ceiling is real but discrimination exists.** Zone profiles carry semantic information about modality domains, but the signal-to-noise ratio is insufficient for Tier 2 predictive power.

#### Implications for Future Work

1. **More labeled data needed**: SIGHT (n=7), TOUCH (n=3) are severely underpowered
2. **Process verb extraction**: Parsing Brunschwig raw text could add discriminating features
3. **Multi-modal recipes**: Testing interference patterns could reveal additional structure
4. **Alternative historical sources**: Cross-validation with Libavius or Della Porta

#### Constraints Respected

- **C384:** All tests at vocabulary/aggregate level, no entry-level mapping
- **C469:** Categorical zone assignment maintained
- **C468:** Legality inheritance respected

**Tier:** 3 (Structural Characterization, confirmed with stronger evidence)

**Files:** phases/SEMANTIC_CEILING_BREACH/, results/scb_modality_prediction.json, results/scb_synthesis.json

---

### X.25 Trajectory Semantics: Judgment-Gating System (2026-01-19) - NEW

**Phase:** TRAJECTORY_SEMANTICS
**Status:** COMPLETE - Semantic boundary resolution achieved

#### Purpose

Applied three pressure vectors beyond the token semantic ceiling to explore "trajectory semantics" - characterizing HOW constraint pressure evolves, rather than WHAT tokens mean.

#### Test Results

| Vector | Hypotheses | Passed | Verdict |
|--------|------------|--------|---------|
| C (Gradient Steepness) | 4 | 0/4 | INCONCLUSIVE |
| A (Interface Theory) | 3 | 2/3 | TIER_3_ENRICHMENT |
| Final (Judgment Trajectories) | N/A | N/A | DECISIVE |

**Vector C failed:** Instruction sequences are too coarse (2-5 steps) to detect transition dynamics. This is a **diagnostic negative** - if transition dynamics matter, they are handled internally by apparatus + operator, not by text.

**Vector A succeeded:** The 13 judgment types show **84.6% non-uniform distribution** across zones, with **11/13 judgments** showing significant zone restriction (p<0.01).

#### The Decisive Finding: Judgment-Zone Availability Matrix

| Zone | Required | Permitted | Impossible | Freedom |
|------|----------|-----------|------------|---------|
| **C** | 1 | 9 | 3 | **77%** |
| **P** | 9 | 1 | 3 | **77%** |
| **R** | 6 | 7 | 0 | **100%** |
| **S** | 5 | 0 | 8 | **38%** |

**Key findings:**
- **P-zone REQUIRES 9/13 judgments** - observation phase demands active cognitive engagement
- **S-zone makes 8/13 judgments IMPOSSIBLE** - outcome is locked, human intervention forbidden
- **R-zone permits ALL 13 judgments** - active phase where all cognition is possible but narrowing
- **Freedom collapses 77% → 38%** from C-zone to S-zone

#### Agency Withdrawal Curve

The manuscript progressively removes human judgment freedoms phase by phase:

```
C-zone: 77% freedom (setup - flexible)
    ↓
P-zone: 77% freedom (but 9 judgments REQUIRED - observation load)
    ↓
R-zone: 100% freedom (all possible, but narrowing toward commitment)
    ↓
S-zone: 38% freedom (8/13 judgments IMPOSSIBLE - locked)
```

This is not a failure mode. This is **designed under-determinacy** - the system deliberately restricts cognitive options at exactly the phases where unrestricted judgment would be dangerous.

#### The Reframe

> **"The Voynich Manuscript is a machine for removing human freedom at exactly the moments where freedom would be dangerous."**

This reframes the entire manuscript as:

> **A machine-readable declaration of which human cognitive faculties are admissible at each phase of a dangerous process.**

#### What Was Discovered

- **NOT:** What tokens mean
- **NOT:** How fast processes change
- **YES:** Which human judgments are IMPOSSIBLE vs UNAVOIDABLE in each zone

This is **meta-semantics of control and responsibility** - the artifact tells you when judgment is no longer yours.

#### Semantic Boundary Resolution

The semantic ceiling was NOT breached by naming things. It was breached by discovering that:

1. Meaning does not live in tokens
2. Meaning lives in the **withdrawal of agency**
3. The artifact specifies **when judgment becomes impossible**

This is not a failure to "go further." This IS going further - into procedural semantics that no token-level decoding could ever reveal.

#### Constraints Respected

- **C384:** Labels trajectories and phases, not tokens
- **C434:** Uses R-series ordering as foundation
- **C443:** Extends escape gradients with temporal dimension
- **C469:** Judgment availability is categorical

**Tier:** 3 (Structural Characterization with semantic boundary resolution)

**Files:** phases/TRAJECTORY_SEMANTICS/, results/ts_judgment_trajectories.json, results/ts_synthesis.json

---

### X.26 AZC Trajectory Shape: Scaffold Fingerprint Discovery (2026-01-19) - NEW

**Phase:** AZC_TRAJECTORY_SHAPE
**Status:** COMPLETE - Critical corrective insight achieved

#### Purpose

Test whether Zodiac and A/C families have different judgment withdrawal trajectories, combining:
- **Vector 1 (External Expert):** Trajectory shape - "wide-then-collapse" vs "narrow-then-spike"
- **Vector 2 (Expert-Advisor):** Apparatus mapping - pelican alembic structural correspondence

#### The Critical Reframe

> **"AZC trajectory shape is a fingerprint of control scaffold architecture, not a simulation of apparatus dynamics."**

This phase rescues trajectory analysis from a wrong question (apparatus physics) and repositions it as structural characterization. The key insight:

> **Escape permission encodes decision affordance, not physical reversibility.**

#### Test Results (3/9 hypotheses passed)

| Hypothesis | Result | Key Finding |
|------------|--------|-------------|
| H2: Monotonicity | **PASS** | Zodiac rho=-0.755 (steady decline), A/C rho=-0.247 (oscillatory) |
| H6: R-series restriction | **PASS** | Perfect vocabulary narrowing: R1(316)->R2(217)->R3(128) unique MIDDLEs |
| H7: S->B-terminal flow | **PASS** | S-zone vocabulary 3.5x enriched in B-terminal (OR=3.51, p<0.0001) |
| H8: Pelican reversibility | **FAIL** | Zone escape does NOT correlate with operational reversibility |

**Failed hypotheses:** H1 (entropy slope), H3 (terminal compression), H4 (peak count), H5 (elimination order), H9 (escape variance) - entropy-based and apparatus-based metrics do not differentiate families.

#### Key Discoveries

**1. Monotonicity = Scaffold Type Signature (H2)**

This aligns with C436 (Dual Rigidity):

| Family | Scaffold Type | Trajectory Shape | Cognitive Effect |
|--------|---------------|------------------|------------------|
| **Zodiac** | Uniform scaffold | Smooth monotonic tightening | Sustained flow cognition |
| **A/C** | Varied scaffold | Punctuated tightening | Checkpoint cognition |

> **Uniform constraints produce smooth trajectories; varied constraints produce punctuated trajectories.**

This explains HT oscillation differences, why entropy metrics failed, and why "spikiness" predictions inverted.

**2. R-Series + S->B-Terminal Form Causal Chain (H6 + H7)**

These findings connect into a mechanistic pipeline:

1. **R-series positional grammar** (C434) -> progressively restricts legal MIDDLE vocabulary
2. **S-zone survival** -> selectively feeds into **B terminal states**

This closes the architectural loop: **AZC legality -> vocabulary survival -> executable program completion**

**3. Pelican Reversibility Model Falsified (H8)**

The apparatus-phase alignment hypothesis failed (rho=-0.20) because:
- AZC does NOT mirror physical reversibility
- AZC encodes **when human intervention must be permitted**
- Interior diagram positions (C, R-early) have higher escape than boundary positions (S)

*Note: P (Paragraph) is Currier A text on AZC folios, not a diagram position.*

> **Physics enforces order; AZC enforces responsibility allocation. These are orthogonal.**

#### New Tier 3 Characterization

> **AZC families differ not in what judgments are removed, but in how smoothly those removals are imposed over execution - a property determined by scaffold uniformity versus variability.**

#### Integration with Global Model

| Layer | Function | This Phase Clarifies |
|-------|----------|---------------------|
| Currier A | Enumerates discrimination space | UNCHANGED |
| **AZC** | Gates when judgments are legal | **NOW adds: pacing style determined by scaffold type** |
| HT | Tracks cognitive load & capacity | Explains oscillation patterns |
| Currier B | Executes safely | UNCHANGED |

This phase does NOT add a new layer - it clarifies an attribute of an existing one.

#### The Corrective Pivot

Earlier phases implicitly blurred:
- Apparatus behavior (physics)
- Control scaffold behavior (how legality is imposed)

This phase disentangles them cleanly:

> **Templates don't select senses - they shape cognitive pacing. Sensory strategies emerge downstream.**

#### Constraints Respected

- **C384:** Aggregate distributions only, no token-to-referent mapping
- **C430:** Explicit Zodiac/A/C family separation
- **C434:** Uses R-series forward ordering
- **C436:** Scaffold uniformity difference confirmed

**Tier:** 3 (Structural Characterization - scaffold->trajectory signature)

**Files:** phases/AZC_TRAJECTORY_SHAPE/, results/ats_*.json

---

### X.27 Brunschwig-Voynich Relationship Bounded: Explanation-Enforcement Complementarity FALSIFIED (2026-01-19) - NEW

**Phase:** BC_EXPLANATION_ENFORCEMENT
**Status:** COMPLETE - Clean falsification achieved

#### Purpose

Test the "one remaining legitimate reverse-Brunschwig test" (external expert): Does Brunschwig's pedagogical verbosity inversely correlate with AZC scaffold constraint rigidity?

> **Core question:** Where Voynich enforces more, does Brunschwig explain less?

#### Test Results (0/4 hypotheses passed = FALSIFIED)

| Hypothesis | Prediction | Result | Status |
|------------|------------|--------|--------|
| H1: Freedom correlation | Inverse density-freedom correlation | rho=+0.09 (opposite direction) | **FAIL** |
| H2: Scaffold rigidity | UNIFORM < VARIED density | d=-0.37 (correct direction, p=0.11) | **FAIL** |
| H3: Interaction | Freedom x Pacing interaction > main | dR2=0.00 (no effect) | **FAIL** |
| H4: Complementarity ratio | Stable ratio across regimes | CV increased 9.6% | **FAIL** |

#### What Was Falsified

The stronger hypothesis:

> **"Brunschwig's pedagogical verbosity systematically complements Voynich's enforcement rigidity at the recipe/regime level."**

This hypothesis is now **dead permanently**.

#### What Survives Intact

The falsification does NOT touch:

- Zone-modality discrimination (F-BRU-009, two-stage model) - INTACT
- Zones structure judgment admissibility, not sensory labels - INTACT
- AZC trajectory shape = scaffold fingerprint, not apparatus dynamics - INTACT
- Scaffold uniformity vs variability determines cognitive pacing - INTACT

#### The Corrected Relationship

| Aspect | Brunschwig | Voynich |
|--------|------------|---------|
| Primary function | Explains **WHAT** | Enforces **WHEN** |
| Audience | Learners / practitioners | Experts only |
| Content | Materials, heat, moral warnings | Legality, transitions, recoverability |
| Silence | On enforcement | On explanation |
| Alignment level | Curriculum trajectory | Curriculum trajectory |
| **NOT aligned** | Interface timing | Interface timing |

#### Why This Strengthens the Model

If the test had succeeded, we'd be forced into:
- Implicit co-design claims
- Hidden synchrony assumptions
- An explanation-enforcement dual-manual model

The falsification produces something cleaner:

> **Voynich stands alone as an enforcement artifact.**

Voynich and Brunschwig converge on:
- The same process domain
- The same hazard ontology
- The same curriculum ordering
- The same notion of completeness vs intensity

...but **only at the level of control worldview**, not at the level of interface behavior.

#### Final Synthesis (Corrected)

> **AZC zones and scaffold families address sensory strategies indirectly by structuring judgment admissibility and cognitive pacing, not by encoding modalities. Brunschwig and Voynich align at the level of procedural ontology and curriculum trajectory, but they do not coordinate explanation and enforcement at the level of individual recipes or phases.**

This formulation:
- Respects every Tier 0-2 constraint
- Incorporates the falsification
- Preserves the genuine AZC/sensory insight
- Closes the Brunschwig line of inquiry cleanly

#### New Constraints

**C-BOUND-01:** Voynich is not part of a fine-grained pedagogical feedback loop with Brunschwig.
**C-BOUND-02:** The Voynich-Brunschwig relationship is maximally abstract: convergent at ontology level, independent at interface level.

**Tier:** FALSIFIED (0/4) - Clean negative result, bounds relationship appropriately

**Files:** phases/BC_EXPLANATION_ENFORCEMENT/, results/bc_*.json

---

### X.28 Recipe Triangulation Methodology: Multi-Dimensional PP Convergence (2026-01-21) - NEW

**Phase:** ANIMAL_PRECISION_CORRELATION

#### The Problem

Previous attempts at reverse-Brunschwig mapping failed because:
1. Single PP tokens don't discriminate (90%+ folio overlap between recipes)
2. REGIME alone provides weak selection (only 11.9% exclusive vocabulary)
3. Working at folio level loses record-level signal

#### The Solution

Multi-dimensional PP convergence at RECORD level, combined with PREFIX profile matching.

#### The Pipeline

```
Brunschwig Recipe Dimensions
       ↓
B Folio Constraints (REGIME + PREFIX profile)
       ↓
Multi-dimensional Conjunction → Candidate B Folios
       ↓
PP Vocabulary Extraction
       ↓
A RECORD Convergence (3+ PP tokens)
       ↓
RI Token Extraction
       ↓
PREFIX Profile Matching → Instruction Sequence
       ↓
Material Identification
```

#### Key Mappings

| Recipe Dimension | B Constraint | Implementation |
|------------------|--------------|----------------|
| fire_degree = N | REGIME_N | `regime_folio_mapping.json` |
| e_ESCAPE in sequence | High qo ratio | `qo_ratio >= avg` |
| AUX in sequence | High ok/ot ratio | `aux_ratio >= avg` |
| FLOW in sequence | High da ratio | `da_ratio >= avg` |

#### Worked Example: Chicken (ennen)

**Input:**
- fire_degree: 4 → REGIME_4
- instruction_sequence: [e_ESCAPE, AUX, UNKNOWN, e_ESCAPE]
- Unique pattern: ESCAPE bookends + AUX (no FLOW)

**4D Conjunction:**
- REGIME_4 + high qo + high aux + low da → 1 folio (f95v1)
- Relaxed to 5 chicken-like folios

**A Record Convergence:**
- 110 records converge to 3+ chicken folios at 2+ PP each
- 4 records contain known animal RI tokens

**PREFIX Profile Matching:**
| RI Token | Has ESCAPE PP? | Has AUX PP? | Chicken Match? |
|----------|----------------|-------------|----------------|
| teold | YES (t=88% qo) | NO | Partial |
| chald | YES (fch=74% qo) | NO | Partial |
| **eoschso** | YES (ke,keo) | **YES (ch=48%)** | **FULL** |
| eyd | weak | weak | No |

**Result:** Only **eoschso** has BOTH escape AND aux PP, matching chicken's unique [e_ESCAPE, AUX, UNKNOWN, e_ESCAPE] pattern.

**Conclusion:** eoschso = ennen (chicken) [Tier 3 hypothesis]

#### Critical Constraints

**DO:**
- Use multi-dimensional conjunction for B folio selection
- Require 3+ PP convergence at RECORD level (not folio)
- Match PREFIX profiles to instruction patterns
- Compare against Brunschwig sequences for identification

**DO NOT:**
- Use single PP tokens for discrimination
- Work at folio level (90%+ overlap)
- Skip PREFIX profile matching
- Assume REGIME alone discriminates

#### Constraint Implications

Refines C384 (no entry-level A-B coupling):
> "Single PP tokens do not establish entry-level coupling, but multi-dimensional PP convergence combined with PREFIX profile matching can identify specific A records."

#### Status

- **Validated:** Animal material class (chicken identification)
- **Pending:** Plant materials (rose water), other animal refinement
- **Tier:** 3 (requires Brunschwig alignment for interpretation)

**Files:**
- Methodology: `context/SPECULATIVE/recipe_triangulation_methodology.md`
- Results: `phases/ANIMAL_PRECISION_CORRELATION/results/`
- Scripts: `phases/ANIMAL_PRECISION_CORRELATION/scripts/`

---

### X.29 Material-Class REGIME Invariance: Precision as Universal Requirement (2026-01-25) - REVISED

**REVISED FINDING:** Both animal AND herb material classes route preferentially to REGIME_4 (precision control). Material differentiation occurs at **token variant level**, not REGIME level.

#### Key Discovery

| Material Class | REGIME_4 Enrichment | p-value |
|----------------|---------------------|---------|
| Animal | **2.03x** | 0.024 |
| Herb | **2.09x** | 0.011 |

Both material classes prefer REGIME_4 at nearly identical enrichment (~2x). This contradicts the initial hypothesis that different materials would route to different REGIMEs.

#### Hypothesis Evolution

| Version | Prediction | Result |
|---------|------------|--------|
| **Original** | Animal -> REGIME_1/2 | WRONG |
| **Intermediate** | Animal -> REGIME_4 | INCOMPLETE |
| **Final** | Both Animal AND Herb -> REGIME_4 | CONFIRMED |

#### Where Differentiation Actually Occurs

| Level | Differentiation? | Evidence |
|-------|-----------------|----------|
| REGIME | **NO** | Both ~2x REGIME_4 enriched |
| Folio | **NO** | r=0.845 correlation |
| Token Variants | **YES** | Jaccard=0.38 (62% different) |

#### Statistical Evidence

**REGIME distribution:**
- Animal: 13/21 high-reception folios in REGIME_4 (62%)
- Herb: 14/22 high-reception folios in REGIME_4 (64%)
- Baseline: 25/82 folios in REGIME_4 (30.5%)

**Token-level differentiation:**
- Overall Jaccard: 0.382
- Per-class mean Jaccard: 0.371
- Most differentiated: ke (0.037), fch (0.111), ol (0.169)

#### Interpretation

**REGIME_4 encodes execution precision requirements, not material identity.** Different materials can share execution requirements while differing in behavioral parameterization.

The manuscript achieves material-appropriate execution NOT by routing to different procedures, but by **selecting different token variants within a shared grammatical framework**:

```
Material -> REGIME: Same (both -> precision)
Material -> Token: Different (62% non-overlap)
```

This confirms C506.b: tokens within same class are positionally compatible but behaviorally distinct. The 480-token vocabulary parameterizes a 49-class grammar, not replaces it.

#### PP Classification (Tier 3)

| Class | Count | % | Top Markers |
|-------|-------|---|-------------|
| ANIMAL | 63 | 15.6% | pch, opch, ch, h |
| HERB | 113 | 28.0% | keo, eok, ko, to |
| MIXED | 67 | 16.6% | - |
| NEUTRAL | 161 | 39.9% | - |

RI projection: 95.9% of RI contain classifiable PP atoms, enabling material-class inference through composition.

#### Relationship to X.6

This finding STRONGLY REINFORCES X.6 (REGIME_4 Interpretation Correction):

> "REGIME_4 is NOT 'forbidden materials' - it IS 'precision-constrained execution'"

Now demonstrated across BOTH material classes: REGIME_4 is universal precision infrastructure, not material-specific processing.

#### Tier Compliance

- **C536 (Tier 2):** Material-class REGIME invariance (structural fact)
- **C537 (Tier 2):** Token-level differentiation (structural fact)
- **C538 (Tier 3):** PP material-class distribution (conditional on Brunschwig)
- **This section (Tier 4):** Interpretation as execution parameterization

**Files:**
- Phase: `phases/MATERIAL_REGIME_MAPPING/`
- PP Classification: `phases/PP_CLASSIFICATION/`
- Results: `phases/*/results/`

---

### X.30 Three-Tier MIDDLE Structure and AZC Bridge Tokens (2026-02-04) - NEW

**Phase:** REVERSE_BRUNSCHWIG_V2
**Status:** COMPLETE - Structural pattern with speculative interpretation

#### Core Discovery

The MIDDLE layer in Currier B exhibits a three-tier structure based on folio position and AZC presence:

| Tier | MIDDLEs | Mean Position | AZC Presence | Origin |
|------|---------|---------------|--------------|--------|
| **EARLY** | ksh, lch, tch, pch, te | 0.31-0.41 | **6 tokens** | B-specific |
| **MID** | k, t, e | 0.42-0.46 | **151 tokens** | Pipeline (A→AZC→B) |
| **LATE** | ke, kch | 0.47-0.59 | **4 tokens** | B-specific |

#### The AZC Discriminator

AZC presence/absence distinguishes vocabulary origin:

| Tier | % of AZC tier tokens | Interpretation |
|------|---------------------|----------------|
| MID | **93.8%** | Core operations flow through A→AZC→B pipeline |
| EARLY+LATE | **6.2%** | B-specific vocabulary, not AZC-mediated |

**The rule:** If a MIDDLE appears significantly in AZC → it's MID tier (pipeline vocabulary). If absent from AZC → it's EARLY or LATE tier (B-internal vocabulary).

#### The 10 EARLY/LATE Tokens in AZC: Bridge Vocabulary

Of ~900 EARLY/LATE tokens in B, only 10 appear in AZC. These split into two groups:

**AZC-Only (3 tokens) - Pure Labels:**

| Token | PREFIX | MIDDLE | In B? |
|-------|--------|--------|-------|
| orkeeey | or | ke | NO |
| shkeal | sh | ke | NO |
| ypolcheey | po | lch | NO |

- Non-qo prefixes (or-, sh-, po-)
- Appear only in Zodiac diagram positions
- Function as positional labels, not executable operations

**Bridge Tokens (7 tokens) - Cross to B:**

| Token | PREFIX | MIDDLE | B Count | B Position |
|-------|--------|--------|---------|------------|
| qoteedy | **qo** | te | 73 | 0.43 (early) |
| qokchdy | **qo** | kch | 54 | 0.45 (early) |
| qopchey | **qo** | pch | 7 | - |
| dalchdy | da | lch | 3 | - |
| qoteor | **qo** | te | 3 | - |
| dolchedy | do | lch | 2 | - |

- **96.5% qo-prefixed** (vs 79.3% for other EARLY/LATE in B)
- Appear **earlier** in B folios than other EARLY/LATE tokens (0.432 vs 0.479)
- Dominated by two tokens: `qoteedy` (73) and `qokchdy` (54) = 89% of B occurrences

#### The qo- PREFIX Discriminator

The qo- prefix determines whether an EARLY/LATE token can cross from AZC to B:

| Pattern | AZC Role | B Role |
|---------|----------|--------|
| qo- + EARLY/LATE MIDDLE | Bridge marker | Executable operation |
| non-qo + EARLY/LATE MIDDLE | Position label | Absent or rare |

**Example:** The MIDDLE `ke` appears in both groups:
- `qokeedy` → 306 occurrences in B (executable)
- `orkeeey` → 0 occurrences in B (AZC label only)

Same MIDDLE, different PREFIX → different pipeline behavior.

#### Speculative Interpretation: Sparse Indexing System

The Zodiac diagrams function as **configuration templates** where:

1. **Most vocabulary is simple labels** (y, o, r, l, ar, dy) - positional markers
2. **MID tier tokens (k, t, e)** mark core operational states
3. **Specific qo-EARLY/LATE tokens** mark phase boundaries:
   - `qoteedy` (qo-te-edy) → preparation phase entry point
   - `qokchdy` (qo-kch-dy) → extended operation marker

**The Zodiac doesn't encode full procedural vocabulary.** It encodes **which procedural template/phase structure to activate**. B then generates appropriate EARLY/LATE vocabulary based on that configuration.

```
ZODIAC CONFIGURATION SPACE
    │
    ├─ Simple labels (y, o, r, l)     → Position markers only
    ├─ MID tier (k, t, e)             → Core operational states
    ├─ qoteedy                         → "Start preparation phase"
    └─ qokchdy                         → "Include extended operations"
    │
    ▼
B EXECUTION
    │
    ├─ EARLY tier (B-generated)       → Full preparation vocabulary
    ├─ MID tier (from pipeline)       → Core operations
    └─ LATE tier (B-generated)        → Extended operations
```

#### Alignment with Brunschwig Model

This maps to Brunschwig's procedural structure:

| Brunschwig Phase | Voynich Tier | AZC Role |
|------------------|--------------|----------|
| Preparation (14 ops) | EARLY | Sparse markers (qoteedy) |
| Distillation (27 ops) | MID | Full vocabulary (k, t, e) |
| Extended treatment | LATE | Sparse markers (qokchdy) |

The Zodiac encodes **which phases are active**, not the full procedural detail. B supplies the detail.

#### Structural Evidence

| Finding | Evidence | Tier |
|---------|----------|------|
| Three-tier positional structure | ANOVA p=0.013, Cohen's d=-0.875 | 2 |
| MID tier AZC dominance | 93.8% of AZC tier tokens | 2 |
| qo- prefix bridge pattern | 96.5% vs 79.3% | 2 |
| Bridge tokens earlier in B | 0.432 vs 0.479 mean position | 2 |
| Sparse indexing interpretation | - | 4 (this section) |

#### What This Does NOT Claim

- ❌ Specific semantic content of phase markers
- ❌ Direct material→token mapping
- ❌ Complete understanding of Zodiac function
- ✓ Structural pattern of vocabulary flow through pipeline
- ✓ PREFIX as execution-eligibility marker
- ✓ Zodiac as sparse index, not full procedure encoding

#### Tier Compliance

- **F-BRU-011 (Tier 2):** Three-tier MIDDLE operational structure
- **Structural patterns (Tier 2):** AZC presence, qo- discrimination, positional differences
- **This interpretation (Tier 4):** Sparse indexing model for AZC→B phase activation

**Files:**
- Phase: `phases/REVERSE_BRUNSCHWIG_V2/`
- Analysis scripts: `phases/REVERSE_BRUNSCHWIG_V2/scripts/`
- Results: `phases/REVERSE_BRUNSCHWIG_V2/results/`

### X.31 Preparation Operation Mapping and Modification System (2026-02-04) - NEW

**Phase:** REVERSE_BRUNSCHWIG_V2
**Status:** SUPPORTED - Statistical correlation with speculative interpretation
**Fit:** F-BRU-012

#### Core Discovery

The 5 preparation-tier MIDDLEs correlate with Brunschwig preparation operations at statistically significant levels, with PREFIX and SUFFIX encoding operational modifications.

#### Operation Mapping (Spearman rho = 1.000, p < 0.001)

| Brunschwig Operation | MIDDLE | Evidence | Confidence |
|---------------------|--------|----------|------------|
| **GATHER** (selection) | te | Earliest position (0.410), most uniform morphology (87% -edy) | MEDIUM-HIGH |
| **CHOP** (mechanical) | pch | HERBAL_B concentrated (36.5%), herb material class | MEDIUM |
| **STRIP** (separation) | lch | BIO concentrated (37.5%), extreme PREFIX diversity (12 types) | MEDIUM |
| **POUND** (intensive) | tch | OTHER concentrated (37.4%), pharma/intensive context | LOW-MEDIUM |
| **Rare ops** (BREAK, WASH) | ksh | Lowest frequency (7.9%), specialized contexts | LOW |

#### PREFIX Modification: Handling Mode

| PREFIX | Rate | Position | Meaning | Pattern |
|--------|------|----------|---------|---------|
| qo- | 77.9% | 0.429 | Standard operation | All MIDDLEs |
| ol- | 5.1% | 0.378 | Output/terminal form | All MIDDLEs |
| so- | 4.5% | 0.478 | Tolerance mode | **Only lch** |
| po- | 3.6% | 0.415 | Specialized/restricted | **Only lch** |
| da- | 2.1% | 0.367 | Anchoring reference | **Only lch** |

**Key finding:** `lch` (STRIP) has 12 different prefixes vs 2-5 for others. This matches Brunschwig's STRIP operation which applies to diverse materials (leaves, bark, feathers, stomach linings) requiring different handling modes.

#### SUFFIX Modification: Operation Intensity

| SUFFIX | Rate | Meaning | Brunschwig Parallel |
|--------|------|---------|---------------------|
| -edy | 56.2% | Complete/thorough | "chopped fine", "pounded well" |
| -dy | 16.6% | Basic operation | Standard processing |
| -ey | 14.8% | Selective/delicate | "lightly", careful handling |

**Section correlation (statistical):**
- BIO (delicate materials): 68.8% -edy (thorough processing)
- HERBAL_B (herbs): 55.2% -edy, 22.9% -dy (more variation)
- OTHER (intensive): 42.1% -edy, 20.6% -ey (selective in harsh context)

#### Full Token Interpretation

| Token | Count | Interpretation |
|-------|-------|----------------|
| qoteedy | 73 | Standard GATHER, complete |
| qopchedy | 32 | Standard CHOP, complete |
| qopchdy | 15 | Standard CHOP, basic |
| solchedy | 8 | Tolerant STRIP, complete (delicate materials) |
| dalchedy | 7 | Anchored STRIP, complete (registry reference) |
| qotchedy | 24 | Standard POUND, complete |
| qotchdy | 23 | Standard POUND, basic |

#### Brunschwig Modifier System Parallel

| Brunschwig | Voynich | Evidence |
|------------|---------|----------|
| Intensity ("fine" vs "coarse") | SUFFIX (-edy/-dy/-ey) | Section correlation (p<0.01) |
| Material type (delicate vs tough) | PREFIX (qo-/so-/da-) | lch diversity pattern |
| Downstream fire degree | Section distribution | Material-section alignment |

#### What This Does NOT Claim

- The specific operation names are hypothetical (MIDDLE "correlates with" not "encodes")
- This respects the semantic ceiling (C171, C120) - no direct material→token mapping
- Token interpretations are illustrative, not proven

#### Tier Compliance

- **Statistical patterns (Tier 2):** Frequency correlation, section distributions, PREFIX diversity
- **F-BRU-012 (Tier F3):** Operation mapping with section-material correspondence
- **Token interpretations (Tier 4):** Specific semantic assignments

#### Naming Note

Uses "preparation-tier MIDDLEs" rather than "EARLY tier" to avoid collision with C539's EARLY/LATE PREFIX terminology.

### X.32 Extended Operation Differentiation: ke vs kch (2026-02-04) - NEW

**Phase:** REVERSE_BRUNSCHWIG_V2
**Status:** SUPPORTED - Statistical differentiation with speculative interpretation
**Fit:** F-BRU-013

#### Core Discovery

The two extended-tier MIDDLEs (ke, kch) encode different operational modes that map to Brunschwig's fire degree monitoring protocols.

#### Section Specialization (Key Discriminator)

| MIDDLE | BIO+HERBAL_B | OTHER | Processing Mode |
|--------|--------------|-------|-----------------|
| **ke** | **85.3%** | 14.7% | Gentle/sustained |
| **kch** | 45.3% | **54.7%** | Intensive/precision |

#### Suffix Pattern Differentiation

| MIDDLE | -edy | -dy | -ey | Pattern |
|--------|------|-----|-----|---------|
| **ke** | 85.3% | 0% | 0% | Uniform (complete operation) |
| **kch** | 32.4% | 41.2% | 19.6% | Mixed (context-dependent) |

ke maintains uniform -edy regardless of section; kch adapts its suffix to context.

#### Morphological Interpretation

| MIDDLE | Components | Interpretation |
|--------|------------|----------------|
| **ke** | k + e | Heat + equilibration (sustained cycles) |
| **kch** | k + ch | Heat + precision (C412: ch = precision mode) |

#### Brunschwig Mapping

| Fire Degree | Monitoring Mode | MIDDLE | Evidence |
|-------------|-----------------|--------|----------|
| Degree 1-2 (gentle) | Sustained heat cycles | **ke** | BIO/HERBAL_B concentration |
| Degree 3 (critical) | "Finger test" precision | **kch** | OTHER concentration, tch co-occurrence |

#### Co-occurrence Pattern

kch is enriched 17x with `tch` (POUND equivalent), confirming that intensive operations require precision heat control.

#### Complete Three-Tier Model

| Tier | MIDDLEs | Function | Brunschwig Phase |
|------|---------|----------|------------------|
| **Preparation** | te, pch, lch, tch, ksh | Material preparation | GATHER, CHOP, STRIP, POUND |
| **Core** | k, t, e | Base thermodynamic | Heat, timing, equilibrate |
| **Extended** | ke, kch | Modified operations | Sustained (ke) or precision (kch) |

#### Tier Compliance

- **Section specialization (Tier 2):** Statistical measurement
- **Suffix differentiation (Tier 2):** Statistical measurement
- **F-BRU-013 (Tier F3):** Brunschwig monitoring parallel
- **Morphological interpretation (Tier 4):** k+e, k+ch decomposition

---

### X.33 Procedural Dimension Independence (2026-02-05) - NEW

**Phase:** REVERSE_BRUNSCHWIG_V3
**Status:** CONFIRMED - Statistical validation with Tier 2 findings
**Fits:** F-BRU-015, F-BRU-016

#### Core Discovery

Procedural tier features add 2-3 independent dimensions beyond aggregate rate features in PCA.

#### Dimensional Increase

| Metric | Original | Combined |
|--------|----------|----------|
| Dims for 80% variance | **5** | **8** |
| Independent procedural PCs | - | **2** (|r| < 0.3) |

#### Independence Test

| Procedural PC | Max |r| with Original PCs | Status |
|---------------|----------------------------|--------|
| Proc PC1 | 0.28 | INDEPENDENT |
| Proc PC2 | 0.24 | INDEPENDENT |

#### REGIME Differentiation

6/12 procedural features show significant REGIME differences (Kruskal-Wallis p < 0.05):
- prep_density: eta-squared = 0.18 (LARGE)
- thermo_density: eta-squared = 0.16 (LARGE)
- extended_density: eta-squared = 0.15 (LARGE)

#### REGIME_4 Clarification (F-BRU-017)

REGIME_4 shows HIGHER ke_kch ratio (more ke/sustained), clarifying "precision" in C494:
- Precision = tight tolerance, not intensity
- Achieved via sustained equilibration cycles (ke = k + e)
- NOT via burst precision (kch = k + ch)

#### Interpretation

The three-tier procedural structure captures variance orthogonal to aggregate rates:
- WHAT operations occur (rates) is partially independent from WHEN they occur (positions)
- REGIMEs encode different procedural BALANCES, not just operation intensities

---

### X.34 Root Illustration Processing Correlation: Tier 4 External Anchor (2026-02-05) - NEW

**Phase:** REVERSE_BRUNSCHWIG_V3
**Status:** CONFIRMED - Statistical significance with external semantic grounding
**Fit:** F-BRU-018

#### Core Discovery

B folios using vocabulary from root-illustrated A folios show elevated root-processing operations (tch=POUND, pch=CHOP), providing external semantic anchoring.

#### Statistical Evidence

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Pearson r | **0.366** | Moderate correlation |
| p-value | **0.0007** | Highly significant |
| Spearman rho | **0.315** | Robust to outliers |
| Direction | CORRECT | Root overlap -> higher root ops |

#### External Anchor Logic

```
Brunschwig (External): "POUND/CHOP roots" (dense materials need mechanical breakdown)
          |
          v
Voynich illustrations: 73% emphasize root systems (PIAA phase classification)
          |
          v
A folios with root illustrations -> PP bases (vocabulary extraction)
          |
          v
B folios using root-sourced PP -> elevated tch (POUND) + pch (CHOP)
```

This is NOT circular reasoning - it connects:
- Visual features (illustration root emphasis)
- Brunschwig domain knowledge (root processing methods)
- Voynich text patterns (prep MIDDLE distribution)

#### Methodological Compliance (C384)

The analysis operates at **folio aggregate level**:
- C384 prohibits token-level A-B lookup
- C384.a permits "record-level correspondence via multi-axis constraint composition"
- PP-base overlap is aggregate vocabulary matching, not token mapping

#### Effect Size Benchmark

The r=0.37 correlation is comparable to validated Tier 3 findings:
- C477 (HT-tail correlation): r=0.504
- C459 (HT anticipatory): r=0.343
- C412 (sister-escape anticorrelation): rho=-0.326

#### What This Does Claim (Tier 4)

- Illustrations DO encode material category information (even if epiphenomenal to execution)
- The A->B vocabulary pipeline preserves material-category signals
- Brunschwig material-operation mappings have predictive power for Voynich patterns

#### What This Does NOT Claim

- NO specific plants identified
- NO token-level material encoding
- NO violation of semantic ceiling for individual tokens
- This is aggregate statistical correspondence, not decipherment

#### Tier Compliance

- **Statistical correlation (Tier 2):** Measured effect (r=0.37, p<0.001)
- **F-BRU-018 (Tier 4):** External semantic anchoring via Brunschwig + illustrations

**Files:** phases/REVERSE_BRUNSCHWIG_V3/, phases/PROCEDURAL_DIMENSION_EXTENSION/

---

### X.35 Material Category Hierarchy: Marked vs Unmarked (2026-02-05) - NEW

**Phase:** REVERSE_BRUNSCHWIG_V3
**Status:** SUPPORTED - Explains asymmetric pathway evidence
**Fit:** F-BRU-019

#### Core Discovery

The Voynich system marks **deviations from default processing**, not the default itself. Delicate plant materials (leaves, flowers, petals) are the unmarked default.

#### Three-Pathway Summary

| Material Category | A Signal | B Signal | Status |
|-------------------|----------|----------|--------|
| **Roots/Dense** | Illustration (root emphasis) | tch+pch elevated (r=0.37) | **CONFIRMED** |
| **Animals** | Suffix -ey/-ol | REGIME_4, k+e >> h | **CONFIRMED** |
| **Delicate plants** | Suffix -y/-dy | No distinctive signature | **UNMARKED DEFAULT** |

#### Why Delicate Plants Have No Marker

Herb-suffix pathway test showed:
- Modest correlation with gentle density (r=0.24, p=0.028)
- BUT no REGIME-specific routing (KW p=0.80)
- Both herb AND animal overlap correlate similarly with B metrics

**Interpretation:** Gentle processing is the baseline assumption. Only deviations require marking:
- "POUND this" (roots)
- "Precision timing" (animals)
- [nothing] = proceed with gentle processing (flowers/leaves)

#### Brunschwig Parallel

Brunschwig's manual follows the same pattern:
- Most recipes are for aromatic flowers/leaves (unmarked default)
- Special instructions only for dense materials and animals

#### Category Consolidation

From this point forward:
- **Delicate plant material** = leaves, flowers, petals, soft herbs (single category)
- **Dense plant material** = roots, bark, seeds (requires marking)
- **Animal material** = fats, organs, kermes (requires precision marking)

#### Tier Compliance

- Statistical tests: Tier 2 (null finding is still a finding)
- Theoretical coherence: Tier 3 (Brunschwig alignment)
- Material category consolidation: Tier 4 (interpretive)


---

# Currier A Structure Contract

**Source:** `context/STRUCTURAL_CONTRACTS/currierA.casc.yaml`

```yaml
# ============================================================
# CASC: Currier A Structural Contract
# Version: 1.0
# ============================================================
#
# This is a DERIVED, READ-ONLY specification.
# It introduces NO NEW CLAIMS.
# Constraints remain authoritative.
# Do not edit without constraint update.
#
# Purpose: Shallow interface to Currier A structure for
# AI reasoning, validation, synthesis, and tooling.
#
# ============================================================

meta:
  name: "Currier A Structural Contract"
  acronym: "CASC"
  version: "1.5"
  date: "2026-01-31"
  status: "LOCKED"
  derived_from: "Tier-2 constraints only"
  governance: |
    CASC is NOT authoritative. Constraints are authoritative.
    CASC is a convenience layer for tooling and AI comprehension.
    Do not edit CASC without updating source constraints first.

# ============================================================
# SCOPE & GUARANTEES
# ============================================================
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
    evidence: "Median 3 tokens/line, MI=0 across lines"
    provenance: "C233"

  - id: "POSITION_FREE"
    statement: "No positional grammar within lines"
    evidence: "Zero JS divergence between positions"
    provenance: "C234"

  - id: "NON_SEQUENTIAL"
    statement: "No generative grammar exists"
    evidence: "2.1% transition validity, silhouette=0.049"
    provenance: "C225, C230, C231, C240"

  - id: "FLAT_REGISTRY"
    statement: "Not hierarchical"
    evidence: "Zero vocabulary overlap between markers"
    provenance: "C236"

# ============================================================
# RECORD TYPES (C484 bifurcation)
# ============================================================
record_types:
  control_operator:
    description: "Meta-structural markers for registry scope/mode"
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
    description: "Compound constraint bundles specifying discriminations"
    token_count: "2+"
    minimum_size: 2
    frequency: "99.4%"
    azc_participation: true
    batch_processing: true
    function: "Define fine distinctions at complexity frontier"
    provenance: "C482, C484"

# ============================================================
# MORPHOLOGY (compositional structure)
# ============================================================
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
      description: "MIDDLEs divide into shared-with-B (39.9%) and registry-internal (60.1%)"
      shared_with_b:
        count: 404
        substructure:  # C498.a - RE-VERIFIED 2026-01-24
          azc_mediated:
            count: 214
            percent: "19.8% of A vocabulary"
            role: "True pipeline participation: A->AZC->B constraint propagation"
            breakdown:
              universal: 28   # 10+ AZC folios, avg 54.8 B spread
              moderate: 69    # 3-9 AZC folios, avg 15.4 B spread
              restricted: 117 # 1-2 AZC folios, avg 6.3 B spread
          b_native_overlap:
            count: 198
            percent: "18.4% of A vocabulary"
            role: "B operational vocabulary with incidental A presence"
            characteristics: "Zero AZC presence, avg 3.5 B folios"
            note: "NOT pipeline-participating despite A&B membership"
        provenance: "C498.a"
      registry_internal:
        count: 609
        characteristics: "ct-prefix enriched, suffix-less, folio-localized"
        role: "Stay in A registry, encode within-category fine distinctions"
        interpretation: "Below granularity threshold for execution"

        # Population structure (C498.b, C498.c, C498.d)
        population_structure:
          description: "Single population with length-dependent uniqueness gradient"
          length_frequency_correlation:  # C498.d
            correlation: "rho = -0.367, p < 10^-42"
            short_2_chars: { singleton_rate: "48%", mean_freq: 3.45 }
            short_3_chars: { singleton_rate: "55%", mean_freq: 2.72 }
            mid_4_chars: { singleton_rate: "73%", mean_freq: 1.84 }
            mid_5_chars: { singleton_rate: "82%", mean_freq: 1.35 }
            long_6_chars: { singleton_rate: "96%", mean_freq: 1.04 }
            long_8plus: { singleton_rate: "100%", mean_freq: 1.00 }
          interpretation: "Combinatorial effect from sub-component morphology - short MIDDLEs have fewer combinations"
          singleton_repeater_independence: "chi2 p=0.165 (not significant) - co-occurrence is near-random"
          provenance: "C498.b, C498.c, C498.d"

        # PREFIX lexical bifurcation (C528)
        prefix_bifurcation:  # C528
          description: "RI MIDDLEs split into two nearly-disjoint PREFIX populations"
          prefix_required: { count: 334, percent: "50.1%" }
          prefix_forbidden: { count: 321, percent: "48.1%" }
          prefix_optional: { count: 12, percent: "1.8%" }
          disjoint_rate: "98.2%"
          section_independence: true  # Same ~50/50 split holds within each section
          interpretation: "PREFIX attachment is lexically determined per-entry, not grammatically optional"
          provenance: "C528"

        # Orthogonal feature structure (C513-NOTE-B)
        orthogonal_features:  # C513-NOTE-B
          description: "RI tokens encode 5 independent features that combine freely"
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
          interpretation: "RI = feature bundle, not categorical type. Apparent subtypes are projections onto single dimensions."
          provenance: "C513-NOTE-B"

        # RI functional population structure (C831-C839)
        ri_functional_structure:
          description: "RI MIDDLEs partition into three functional tiers with distinct behaviors"

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
            interpretation: "Positional assignment is lexical, not contextual"
            provenance: "C832"

          line1_concentration:  # C833
            ri_line1_rate: "3.84x baseline"
            interpretation: "Line 1 serves as paragraph header zone"
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
            interpretation: "Many inputs → fewer outputs (convergent processing)"
            provenance: "C839"

          provenance: "C831, C832, C833, C835, C836, C837, C838, C839"

      provenance: "C498, C498.a, C498.b, C498.c, C498.d, C513-NOTE-B, C528, C831-C839"
      revision_date: "2026-01-29"

    # Gallows patterns (C529-C530)
    gallows:
      description: "Gallows letters (p,t,k,f) show positional and distributional asymmetry"

      positional_asymmetry:  # C529
        pp_gallows_initial: "30.4%"
        ri_gallows_initial: "20.1%"
        pp_gallows_medial: "39.3%"
        ri_gallows_medial: "57.8%"
        statistical_significance: "chi2=7.69, p<0.01"
        interpretation: "PP gallows are atomic (initial); RI gallows are embedded (medial)"
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
        interpretation: "k=default domain, t=alternative domain, p/f=specialized markers"
        provenance: "C530"

    # Sub-component grammar (C510-C513)
    sub_component_grammar:
      description: "MIDDLEs exhibit internal compositional structure with systematic construction rules"
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
        interpretation: "Permissive grammar - constraints exist but majority of components are positionally free"
        provenance: "C510"

      derivational_productivity:  # C511
        seeding_ratio: "12.67x above chance"
        relationships_above_chance: "89.8%"
        mechanism: "Short frequent forms extended into longer unique forms"
        explains: "C498.d length-frequency correlation"
        provenance: "C511"

      pp_substrate:  # C512
        pp_as_subcomponents: "72.2%"
        ri_containing_pp: "99.1%"
        section_invariance_ratio: "8.3x (PP vs RI)"
        pp_in_all_sections: "60.7%"
        ri_in_all_sections: "2.6%"
        interpretation: "PP is universal substrate; RI is section-specific elaboration"
        provenance: "C512"

      positional_asymmetry:  # C512.a
        END_class_pp_rate: "71.4%"
        START_class_pp_rate: "16.1%"
        FREE_class_pp_rate: "40.9%"
        pp_free_rate: "69.2%"
        architecture: "RI-START + PP-FREE + PP-END"
        pp_terminators: ["ch", "d", "e", "g", "h", "k", "s", "t"]
        interpretation: "RI elaborates at start, PP terminates at end"
        provenance: "C512.a"

      short_singleton_variance:  # C513
        character_inventory_jaccard: "1.00"
        interpretation: "Singleton status at ≤3 chars is sampling variance, not functional distinction"
        provenance: "C513"

      provenance: "C267.a, C510, C511, C512, C512.a, C513"

    provenance: "C293, C423, C475, C498, C510-C513"

  suffix:
    count: 25
    universal_rate: "22/25 appear in 6+ prefix classes"
    function: "Decision archetype (phase-indexed)"
    regime_association:
      description: "SUFFIX associated with downstream REGIME compatibility breadth"
      enriched_universal: ["-r"]
      enriched_restricted: ["-ar", "-or"]
      effect_size: "Cramér's V = 0.159"
      note: "Associative, not causal"
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

# ============================================================
# LINE STRUCTURE
# ============================================================
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
    description: "Multiple items co-processed as compound input"
    b_invariance: "B structure invariant to A line length"
    test_result: "p=1.0 (all A categories map to same B folios)"
    provenance: "C482"

  repetition:
    status: "INVALIDATED (2026-01-15)"
    note: |
      Block repetition patterns (C250-C262) were discovered to be transcriber artifacts.
      When filtered to PRIMARY transcriber (H) only, block repetition rate is 0%.
      The apparent patterns were caused by interleaved readings from multiple transcribers.
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

# ============================================================
# PARAGRAPH STRUCTURE (C827, C834, C846-C850, C854)
# ============================================================
paragraph_structure:
  description: "Paragraphs serve as operational aggregation units with systematic organization"

  operational_unit:  # C827
    statement: "Paragraphs are the operational aggregation level (not lines, not folios)"
    evidence: "Token survival rates increase with aggregation: line 11.2% -> paragraph 31.8% -> folio 50.0%"
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
      interpretation: "'Only' paragraphs are complete programs; 'middle' paragraphs are compact metadata"
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

  ab_relationship:  # C846
    model: "Pool-based, not address-based"
    statement: "A paragraphs provide vocabulary pools; B draws without specific pairing"
    best_match_lift: "2.49x raw, 1.20x pool-size-controlled"
    hub_concentration: "Top 10 A paragraphs capture 85.9% of best matches"
    pool_size_correlation: "Spearman rho = 0.694"
    interpretation: "Selection artifact from large PP pools, not specific correspondence"
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
    interpretation: "Shared design principle: header zone (RI/HT) + body zone (PP/classified)"
    provenance: "C854"

  provenance: "C827, C834, C846, C847, C848, C849, C850, C854"

# ============================================================
# PARTICIPATION RULES
# ============================================================
participation:
  azc:
    registry_entries:
      participates: true
      pipeline: "A -> AZC -> B"
      compatibility_filtering: true
    control_operators:
      participates: false
      evidence: "0/10 in AZC folios"
      azc_tokens_in_folios: 0
    provenance: "C441-C442, C484"

  ht:
    registry_entries:
      triggers_ht: "possible"
      correlation: "statistical, not functional"
    control_operators:
      triggers_ht: false
      single_char_rate_nearby: "3.2%"
      evidence: "7/10 show 0% single-char nearby"
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
      - "multi-dimensional PP convergence at RECORD level"
    section_distribution:
      H_in_B: "91.6% (76/83 folios)"
      P_in_B: "8.4% (7/83 folios)"
      T_in_B: "0% (0/83 folios)"

    # Full morphological filtering cascade (C502.a)
    filtering_cascade:
      description: "A record morphology constrains B vocabulary through three cascading filters"
      middle_only: { legal: "257 tokens (5.3%)", filtered: "94.7%" }
      middle_plus_prefix: { legal: "92 tokens (1.9%)", additional_reduction: "64%" }
      middle_plus_suffix: { legal: "130 tokens (2.7%)", additional_reduction: "50%" }
      full_morphology: { legal: "38 tokens (0.8%)", additional_reduction: "85% beyond MIDDLE" }
      mechanism: "B token legal iff MIDDLE in A-record AND PREFIX in A-record AND SUFFIX in A-record"
      provenance: "C502.a"

    # A-record filtering validation (C824-C826)
    filtering_validation:
      description: "Comprehensive validation of A->B filtering mechanism"

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
        evidence: "No natural clustering in folio viability"
        provenance: "C825"

      model_reconciliation:  # C826
        correct_model: "Token filtering (C502)"
        rejected_model: "Subset viability"
        interpretation: "B tokens legal when MIDDLE in A's PP set; more PP = more tokens survive"
        provenance: "C826"

      provenance: "C824, C825, C826"

    provenance: "C299, C384, C384.a, C502.a, C824, C825, C826"

# ============================================================
# POSITIONAL PROPERTIES
# ============================================================
positional:
  within_line:
    grammar: "position-free"
    folio_initial_exception:
      description: "C+vowel prefixes (ko-, po-, to-) permitted at position 1 only"
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

# ============================================================
# DISALLOWED INTERPRETATIONS
# ============================================================
# These interpretations have been tested and rejected.
# Do not resurrect without extraordinary new evidence.

disallowed:
  - interpretation: "A tokens map to B folios (context-free)"
    reason: "No token-level or context-free lookup exists"
    evidence: "C384 - no single-token correspondence"
    status: "FALSIFIED"
    note: "Record-level correspondence via constraint collapse IS permitted (C384.a)"

  - interpretation: "Repetition encodes quantity or ratio"
    reason: "Magnitude has no downstream effect"
    evidence: "C483, C287-C290 - ordinal emphasis only"
    status: "FALSIFIED"

  - interpretation: "A has sequential grammar"
    reason: "Transition validity is 2.1%"
    evidence: "C225, C231 - regular but not grammatical"
    status: "FALSIFIED"

  - interpretation: "Prefixes are semantic categories"
    reason: "They are functional markers"
    evidence: "C235 - mutual exclusion without semantic content"
    status: "FALSIFIED"

  - interpretation: "A is lookup table for B"
    reason: "No addressable mapping mechanism"
    evidence: "Vocabulary sharing is statistical, not referential"
    status: "FALSIFIED"

  - interpretation: "A encodes danger or hazard"
    reason: "Correlation is entirely frequency-driven"
    evidence: "Pre-registered test p=0.651; permutation p=0.111"
    status: "FALSIFIED"

  - interpretation: "Control operators are headers or section markers"
    reason: "No semantic category evidence"
    evidence: "C484 - meta-structural function only"
    status: "UNSUBSTANTIATED"

  - interpretation: "A is generative or producible"
    reason: "A is maintained, not produced"
    evidence: "C476 - coverage-optimal with hub rationing"
    status: "FALSIFIED"

# ============================================================
# PROVENANCE MAP
# ============================================================
# Maps CASC sections to authoritative constraint IDs

provenance:
  scope:
    - "C224"  # Coverage 13.6%
    - "C228"  # Density 0.35x
    - "C232"  # Section-conditioned
    - "C272"  # Physical separation

  guarantees:
    - "C225"  # Transition validity
    - "C230"  # Silhouette
    - "C231"  # Regular not grammatical
    - "C233"  # Line atomic
    - "C234"  # Position free
    - "C236"  # Flat
    - "C240"  # Non-sequential registry

  record_types:
    - "C482"  # Batch semantics
    - "C484"  # Channel bifurcation

  morphology:
    - "C235"  # 8 markers
    - "C267"  # Compositional
    - "C268"  # 897 combinations
    - "C269"  # 7 universal suffixes
    - "C277"  # Suffix universal
    - "C278"  # Three-axis hierarchy
    - "C291"  # Articulators
    - "C292"  # Articulator non-discriminative
    - "C293"  # Component essentiality
    - "C408"  # Sister pairs
    - "C412"  # Sister anticorrelation
    - "C423"  # Vocabulary domains
    - "C466"  # PREFIX function
    - "C467"  # PREFIX function
    - "C475"  # MIDDLE incompatibility
    - "C495"  # SUFFIX-REGIME association
    - "C498"  # Registry-internal vocabulary track
    - "C498.b"  # RI singletons
    - "C498.c"  # RI repeaters
    - "C498.d"  # RI length-frequency correlation
    - "C513-NOTE-B"  # RI orthogonal feature structure
    - "C528"  # RI PREFIX lexical bifurcation
    - "C831"  # RI three-tier population structure
    - "C832"  # INITIAL/FINAL positional separation
    - "C833"  # RI line-1 concentration
    - "C835"  # RI linker mechanism
    - "C836"  # ct-prefix linker signature
    - "C837"  # ct-ho linker signature
    - "C838"  # qo linker exception
    - "C839"  # Input-output morphological asymmetry
    - "C887"  # WITHOUT-RI backward reference (1.23x asymmetry)
    - "C888"  # Section-specific WITHOUT-RI function
    - "C889"  # ct-ho reserved PP vocabulary
    - "C898"  # A PP internal structure (positional preferences)

  line_structure:
    - "C250"  # INVALIDATED (was 64.1% repetition - transcriber artifact)
    - "C251"  # Intra-record only
    - "C252"  # Bounded 2-6x
    - "C253"  # Blocks unique
    - "C255"  # Section exclusive
    - "C422"  # DA articulation
    - "C482"  # Batch semantics
    - "C483"  # Ordinal repetition
    - "C484"  # Minimum sizes

  paragraph_structure:
    - "C827"  # Paragraph operational unit
    - "C834"  # Paragraph granularity validation
    - "C846"  # A-B paragraph pool relationship
    - "C847"  # A paragraph size distribution
    - "C848"  # A paragraph RI position variance
    - "C849"  # A paragraph section profile
    - "C850"  # A paragraph cluster taxonomy
    - "C854"  # A-B paragraph structural parallel
    - "C881"  # A record paragraph structure (RI first-line 3.84x)
    - "C882"  # PRECISION kernel signature
    - "C883"  # Handling-type distribution alignment
    - "C884"  # PRECISION-animal correspondence

  participation:
    - "C299"  # Section distribution in B
    - "C384"  # No A-B coupling
    - "C441"  # AZC vocabulary-activated
    - "C442"  # AZC compatibility grouping
    - "C484"  # Control operator exclusion
    - "C502.a"  # Full morphological filtering cascade
    - "C824"  # A-record filtering mechanism validated
    - "C825"  # Continuous routing topology
    - "C826"  # Token filtering model reconciliation
    - "C885"  # A-B vocabulary correspondence (81% coverage)
    - "C899"  # A-B within-line positional correspondence

  positional:
    - "C260"  # Section isolation
    - "C346"  # Adjacency coherence
    - "C420"  # Folio-initial exception
    - "C421"  # Boundary suppression
    - "C424"  # Clustered adjacency
    - "C484"  # Control operator bias

  disallowed:
    - "C225"  # No grammar
    - "C231"  # Not grammatical
    - "C235"  # Markers not categories
    - "C287"  # No ratio encoding
    - "C288"  # No ratio encoding
    - "C289"  # No ratio encoding
    - "C290"  # No ratio encoding
    - "C384"  # No A-B coupling
    - "C476"  # Maintained not produced
    - "C483"  # Ordinal only
    - "C484"  # No header interpretation

# ============================================================
# END OF CASC
# ============================================================

```

---

# Currier B Grammar Contract

**Source:** `context/STRUCTURAL_CONTRACTS/currierB.bcsc.yaml`

```yaml
# ============================================================
# BCSC: Currier B Structural Contract
# Version: 2.0
# ============================================================
#
# This is a DERIVED, READ-ONLY specification.
# It introduces NO NEW CLAIMS.
# Constraints remain authoritative.
# Do not edit without constraint update.
#
# Purpose: Pure internal grammar contract describing what a
# valid Currier B program is, without referencing A or AZC.
#
# This is NOT a workflow description, simulation spec, or
# semantic interpretation. It is abstract control grammar.
#
# ============================================================

meta:
  name: "Currier B Structural Contract"
  acronym: "BCSC"
  version: "2.1"
  date: "2026-01-31"
  status: "LOCKED"
  layer_type: "grammar contract"
  derived_from: "Tier 0-2 constraints only"
  governance: |
    BCSC is NOT authoritative. Constraints are authoritative.
    BCSC describes the internal grammar of Currier B.
    Do not edit without updating source constraints first.

# ============================================================
# SCOPE & GUARANTEES
# ============================================================
scope:
  system: "Currier B"
  coverage: "61.9% of tokens, 83 folios"
  function: "What a valid Currier B program is, internally"
  a_agnostic: true  # Does not reference Currier A
  azc_agnostic: true  # Does not reference AZC mechanics
  non_semantic: true  # No process domain interpretation

# Explicit ownership declaration
ownership:
  bcsc_describes:
    - grammar_structure
    - kernel_roles
    - hazard_topology
    - convergence_behavior
    - program_structure
    - recovery_architecture
    - vocabulary_architecture  # Added v1.1: folio uniqueness, class-member differentiation
    - execution_syntax  # Added v1.2: line-level role positioning, section profiles, AX architecture
  bcsc_does_not_describe:
    - currier_a_entries
    - azc_mechanics
    - human_track_layer
    - process_domain
    - token_meanings
  note: "Pure grammar contract, not workflow or simulation"

guarantees:
  - id: "GRAMMAR_UNIVERSAL"
    statement: "49-class grammar applies to all 83 folios without exception"
    provenance: "C121, C124"

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
    note: "Kernel characters operate at CONSTRUCTION level (C521), not execution level. Forbidden transitions operate at CLASS level (C109). These layers are independent (C522)."
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
    statement: "Grammar constraints are bidirectional (H(X|past)=H(X|future)), but execution is directional (transition probabilities uncorrelated)"
    provenance: "C391, C886"

  - id: "CLOSED_LOOP_ONLY"
    statement: "Execution is closed-loop control, not batch, decision tree, or state machine"
    provenance: "C171"

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
    statement: "20 AX classes collapse to ≤2 effective behavioral groups; position is the only differentiator"
    provenance: "C572"

  - id: "AX_PIPELINE_SCAFFOLD"
    statement: "AX is the scaffold layer of the shared pipeline: 98.2% PP MIDDLEs, PREFIX-determined role"
    provenance: "C567, C568, C571"

# ============================================================
# INVARIANTS
# ============================================================
invariants:
  grammar_universality:
    statement: "Same 49 classes apply to every folio"
    description: "Grammar is universal across all 83 folios"
    provenance: "C124"

  convergence_dominance:
    statement: "Majority of programs terminate in STATE-C"
    description: "Grammar architecture targets single stable state"
    provenance: "C074, C084, C323"

  hazard_asymmetry:
    statement: "Most forbidden transitions are directional"
    description: "65% of forbidden transitions are one-way"
    provenance: "C111"

  line_invariance:
    statement: "Grammar violations do not cross line boundaries"
    description: "0 forbidden transitions span line breaks"
    provenance: "C360"

  constraint_symmetry:
    statement: "Grammar constraints are bidirectional; execution is directional"
    description: "Conditional entropy symmetric (H(X|past)=H(X|future)), but transition probabilities uncorrelated (r=-0.055). Constraints work both ways; actual usage is directional."
    provenance: "C391, C886"

  kernel_boundary_adjacency:
    statement: "Classes containing kernel characters tend to be hazard-involved"
    description: "Correlational, not causal: classes with high k/h/e content are often in hazard-involved categories, but k/h/e content does not DETERMINE forbidden transition participation. Forbidden transitions operate at CLASS level, not character level."
    note: "KERNEL_STATE_SEMANTICS phase (T10) confirmed: Class 10 (daiin) has 0% k/h/e yet participates in forbidden transitions; Class 31 (chey) has 100% h yet also participates. The mechanism is class-based sequencing, not character-based."
    provenance: "C107, C522"

  class_member_differentiation:
    statement: "Grammar is universal at class level, differentiation at token level"
    description: "Same 49 classes everywhere, but different tokens within class enable different behavioral flows"
    provenance: "C506.b, C537"

  folio_vocabulary_minimality:
    statement: "81/82 folios required for complete vocabulary coverage"
    description: "Folio count is structurally determined; redundancy ratio 1.01x"
    provenance: "C535"

  execution_syntax:
    statement: "Lines follow SETUP→WORK→CHECK→CLOSE positional grammar"
    description: "5 functional roles (CC, EN, FL, FQ, AX) occupy preferred line positions; ENERGY concentrates medially, FLOW concentrates finally"
    provenance: "C556, C562"

  energy_flow_anticorrelation:
    statement: "ENERGY and FLOW roles are anticorrelated across sections"
    description: "High-ENERGY sections are low-FLOW and vice versa; r = -0.89"
    provenance: "C551"

  ax_behavioral_collapse:
    statement: "19 AX classes do not form distinct behavioral groups"
    description: "Transitions uniform (0/19 structured), context below random baseline (9.8% vs 11.1%), best clustering k=2 silhouette=0.43"
    provenance: "C572"

  regime_syntax_invariance:
    statement: "Line syntax is INVARIANT across all four REGIMEs"
    description: "All 5 roles show p>0.4 for REGIME effect; REGIME explains 0.13% of position variance (11x less than phase). REGIME determines WHAT to do, not WHERE in line."
    provenance: "C821"

  regime_cc_position_invariance:
    statement: "CC token positions are INVARIANT across REGIMEs"
    description: "daiin and ol positions show no significant REGIME variation; control loop structure is universal"
    provenance: "C822"

  regime_bigram_partial_variation:
    statement: "Bigram transition patterns show PARTIAL REGIME variation"
    description: "23.3% of top bigrams show REGIME effects; 76.7% are universal. REGIME tunes execution details, not syntax structure."
    provenance: "C823"

# ============================================================
# GRAMMAR STRUCTURE
# ============================================================
grammar:
  description: "49 instruction equivalence classes with 100% coverage"

  classification:
    token_types: 479
    instruction_classes: 49
    compression_ratio: "9.8x"
    coverage: "100%"
    exceptions: 0
    provenance: "C121, C124"

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

# ============================================================
# ROLE TAXONOMY (Morphology at Role Level Only)
# ============================================================
# NOTE: These are ABSTRACT role classes, not morphological composition.
# Specific prefixes, character sequences, and compositional rules
# are NOT part of BCSC.

role_taxonomy:
  description: "Abstract role classes used by grammar (not morphological realization)"

  roles:
    CORE_CONTROL:
      function: "Execution boundaries"
      classes: "{10, 11, 12, 17}"
      token_share: "4.4% of B (~1023 tokens)"
      provenance: "C121, C557, C558, C560, C581, C788-C791"
      # SINGLETON IDENTITY (C788):
      #   CC "classes" are NOT broad categories — they are SPECIFIC TOKENS:
      #   Class 10 = "daiin" only (1 type, 314 tokens)
      #   Class 11 = "ol" only (1 type, 421 tokens)
      #   Class 12 = "k" only (1 type, 0 tokens — ghost class, never appears in B)
      #   Class 17 = 9 "ol-" prefixed tokens (olkeedy, olkeey, etc., 288 tokens)
      #   This reframes CC from "control role" to "specific control tokens."
      # INTERNAL STRUCTURE (C590):
      #   GENUINE_STRUCTURE — Class 10 (daiin) initial-biased (mean 0.413),
      #   Class 11 (ol) medial (mean 0.511), p=2.8e-5.
      #   Class 12 (k) is ghost — zero corpus tokens (C540).
      #   Class 17 assigned to CC per C560 (ol-derived compound control).
      # TRANSITION ROUTING (C791):
      #   CC->EN dominant: 78.3% of CC successors are EN (kernel operations).
      #   CC->FQ: only 19.1%. CC primarily routes to energy modulation.
      # SUFFIX-FREE (C588):
      #   0 suffix types, 100% bare. Most constrained suffix profile.
      # PIPELINE PURITY (C584):
      #   100% PP — all 3 MIDDLEs (iin, k, ol) are pipeline-participating.
      # CONTROL LOOP INTEGRATION (C816-C820):
      #   CC INITIATES the control loop:
      #   - daiin (0.413) -> LINK (0.476) -> KERNEL (0.477) -> ol (0.511) -> FL (0.576)
      #   - daiin is earliest control token, significantly earlier than LINK (p<0.001)
      #   Lane routing (C817): daiin->CHSH 90.8%, ol_derived->QO 57.4%, rapid decay by +2
      #   Kernel bridge (C818): Class 17 is CC-KERNEL interface (88% kernel chars)
      #   Boundary asymmetry (C819): daiin initial 27.1%, ol/ol_derived medial 85%
      #   HAZARD IMMUNITY (C820): CC has ZERO forbidden transitions (0/700)
      #     EN absorbs 99.8% of all hazard; CC is the SAFE control layer

    ENERGY_OPERATOR:
      function: "Energy modulation"
      class_count: 18
      classes: "{8, 31-37, 39, 41-49}"
      token_share: "31.2% of B (7211 tokens)"
      provenance: "C121, C573"
      # INTERNAL STRUCTURE (C574):
      #   18 classes show DISTRIBUTIONAL_CONVERGENCE — grammatically
      #   equivalent (same positions, same REGIME, same context) but
      #   lexically partitioned (QO uses 25 MIDDLEs, CHSH uses 43,
      #   only 8 shared; Jaccard=0.133). PREFIX selects material
      #   subvocabulary, not grammatical function (C576, C577).
      # SUFFIX-RICH (C588):
      #   17 suffix types, only 39% bare. Suffixes encode material
      #   variants — EN and AX share suffix vocabulary (Jaccard=0.800).
      # PIPELINE PURITY (C575):
      #   100% PP — all 64 unique MIDDLEs are pipeline-participating.
      # HAZARD ROLE (C586):
      #   EN is hazard-TARGET — absorbs 11 of 19 corpus forbidden transitions.
      #   Opposite of FL which is hazard-source.

    AUXILIARY:
      function: "PREFIX-switched scaffold layer of shared pipeline vocabulary"
      class_count: 19
      classes: "{1, 2, 3, 4, 5, 6, 15, 16, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29}"
      token_share: "16.6% of B (~3852 tokens)"
      provenance: "C121, C563-C572, C583"
      # ARCHITECTURE:
      #   AX tokens use the SAME MIDDLEs as operational roles (98.2% PP, C567).
      #   PREFIX determines whether a MIDDLE acts as AX or operational (C571).
      #   AX is not a separate vocabulary—it is a scaffold MODE of the pipeline.
      #
      # POSITIONAL SUB-STRUCTURE (C563, corrected 2026-01-26):
      #   AX_INIT  (classes 4, 5, 6, 24, 26): line-initial scaffold
      #   AX_MED   (classes 1, 2, 3, 16, 18, 27, 28, 29): medial scaffold
      #   AX_FINAL (classes 15, 19, 20, 21, 22, 25): line-final scaffold
      #   Note: Class 14 removed from AX_MED — confirmed FQ per ICC + behavioral
      #   evidence (suffix rate 0.0, token count 707). See C583.
      #   Class 17 removed per C560 — confirmed CC (ol-derived control). See C581.
      #
      # BEHAVIORAL COLLAPSE (C572):
      #   19 classes do NOT form distinct behavioral groups.
      #   Transitions: uniform (only 3/19 structured). Context: below random baseline.
      #   Best clustering: k=2, silhouette=0.18. Position is the only differentiator.
      #   Effective behavioral groups: ≤2 (not 19).
      #
      # SUFFIX-MODERATE (C588):
      #   19 suffix types, 62% bare. Shares suffix vocabulary with EN (Jaccard=0.800).
      #
      # CO-OCCURRENCE:
      #   97.4% of class pairs co-occur; no pair mutually exclusive.
      #   At Jaccard 0.7, all 19 cluster together (functional coherence).
      #   Survival stratification (28%-100%) reflects MIDDLE availability, not importance.

    FREQUENT_OPERATOR:
      function: "Common instructions"
      class_count: 4
      classes: "{9, 13, 14, 23}"
      token_share: "12.5% of B (2890 tokens)"
      provenance: "C121, C583, C587, C593-C597"
      # INTERNAL STRUCTURE (C587, C593):
      #   4-way GENUINE_STRUCTURE — 100% Kruskal-Wallis significance.
      #   3-group organizing principle (k=3 silhouette 0.68):
      #     CONNECTOR {9}: bare, medial, or→aiin bigram (C561), hazardous
      #     PREFIXED_PAIR {13, 14}: ok/ot-prefixed, medial-to-final, non-hazardous
      #     CLOSER {23}: bare, final-biased, hazardous, boundary specialist
      #   Morphology × hazard: BARE={9,23}=HAZARDOUS, PREFIXED={13,14}=SAFE (perfect overlap)
      # VOCABULARY BIFURCATION (C594):
      #   Classes 13/14 share ZERO MIDDLEs (Jaccard=0.000). Complete lexical partition.
      #   13: {aiin,ain,e,edy,eey,eol} 18.2% suffixed. 14: {al,am,ar,ey,ol,or,y} 0% suffixed.
      #   Sharper than EN's QO/CHSH bifurcation (Jaccard=0.133, C576).
      # INTERNAL TRANSITIONS (C595):
      #   chi2=111, p<0.0001 (470 pairs). Sequential structure, not random.
      #   23→9 enriched 2.85x (closer→connector restart loop).
      #   9→13 directional 4.6:1 (connector→workhorse feed-forward).
      #   All classes self-chain (1.27-1.60x).
      # FQ-FL SYMBIOSIS (C596):
      #   Position-driven, NOT hazard-mediated (hazard p=0.33).
      #   FL7→FQ9 (medial-medial), FL30→FQ13/14 (final-medial).
      # BOUNDARY BEHAVIOR (C597):
      #   Class 23: 29.8% final rate, 39% of FQ finals. Boundary specialist.
      #   Mean run length 1.19 — FQ is 84% singletons.
      # SUFFIX-DEPLETED (C588):
      #   1 suffix type (edy, on Class 13 only), 93.4% bare.
      # PIPELINE PURITY (C584):
      #   100% PP — all unique MIDDLEs are pipeline-participating.
      # NOTE: C559 used wrong membership {9,20,21,23} — SUPERSEDED by C583.
      #   Classes 20,21 are AX_FINAL per C563. Class 14 is FQ per ICC,
      #   confirmed by behavioral evidence (suffix rate 0.0, 707 tokens).
      # RE-VERIFICATION (C550/C551/C552/C556):
      #   C550: MAGNITUDES_SHIFTED — FQ self 2.38x→1.44x, FL→FQ 1.73x→1.34x (directions preserved)
      #   C551: UNCHANGED — mean evenness 0.911→0.916
      #   C552: MAGNITUDES_SHIFTED — FQ baseline 5.6%→12.5%, PHARMA 1.31x→0.79x
      #   C556: DIRECTION_SHIFTED — FQ final 1.67x→0.92x (no longer final-biased)

    HIGH_IMPACT:
      function: "Major interventions"
      class_count: 3
      status: "LEGACY — classes absorbed into ENERGY_OPERATOR per C573"
      provenance: "C121"
      # RETAINED for backward compatibility with C366, C394, C402 which
      # reference HIGH_IMPACT by name. The 3 HIGH_IMPACT classes are now
      # part of EN's 18-class taxonomy. Role label no longer in active use.

    FLOW_OPERATOR:
      function: "Flow control - primitive substrate layer"
      abbreviation: "FO"  # Use "FO" to distinguish from FL (MIDDLE taxonomy)
      class_count: 4
      classes: "{7, 30, 38, 40}"
      token_share: "4.7% of B (1078 tokens)"
      provenance: "C121, C562, C582, C770-C777"
      # DISAMBIGUATION NOTE:
      #   "FO" (FLOW_OPERATOR) = this 49-class behavioral role (4.7% of tokens)
      #   "FL" = MIDDLE-based material state taxonomy (C777, ~25% of tokens)
      #   FO tokens contain FL MIDDLEs, but FL MIDDLEs appear across all roles.
      #   See: TERMINOLOGY/fl_disambiguation.md
      # PRIMITIVE ARCHITECTURE (C770-C772):
      #   FL is the PRIMITIVE SUBSTRATE for the entire grammar.
      #   Character set: ONLY {a, d, i, l, m, n, o, r, y} — 9 chars total.
      #   Kernel chars (k, h, e): ZERO. FL operates below kernel layer.
      #   Helper chars (c, s, t): ZERO. Complete exclusion.
      #   Compound rate: 0%. FL MIDDLEs cannot be decomposed further.
      #   Other roles are built by ADDING kernel/helper chars to FL-like bases.
      #   EN is most kernel-enriched (60.7% kernel-containing MIDDLEs).
      # INTERNAL STRUCTURE (C586):
      #   GENUINE_STRUCTURE with hazard/safe split:
      #   Hazard pair {7, 30}: medial position (mean 0.55), 12.3% final.
      #     Class 30 (dar/dal) is gateway — precedes hazard events (C542).
      #   Safe pair {38, 40}: final position (mean 0.81), 55.7% final.
      #     Class 40 is maximally hazard-distant (C546).
      #   Mann-Whitney position p=9.4e-20, final rate p=7.3e-33.
      # HAZARD ROLE (C586, C773-C775):
      #   FL is hazard-SOURCE — initiates 4.5x more than receives.
      #   Opposite of EN which is hazard-target.
      #   FL has 83.3% forward-facing hazard exposure (C786).
      #   No FL->FL transitions exist (state reset prohibited, C787).
      # SUFFIX-DEPLETED (C588):
      #   2 suffix types (r, dy), 93.8% bare.
      # PIPELINE PURITY (C584):
      #   100% PP — all 17 unique MIDDLEs are pipeline-participating.

    LINK:
      function: "Monitoring/observation phase marker"
      provenance: "C366"

  functional_classification:
    description: "ICC-based 5-role functional system (C591: complete taxonomy)"
    roles_mapped:
      CC: "Core Control (execution boundaries, 4 classes, 4.4% of B)"
      EN: "Energy Operators (energy modulation, 18 classes, 31.2% of B)"
      FL: "Flow Operators (flow control, 4 classes, 4.7% of B)"
      FQ: "Frequent Operators (common instructions, 4 classes, 12.5% of B)"
      AX: "Auxiliary (scaffold, 19 classes, 16.6% of B)"
    provenance: "C547-C550, C573, C581-C583, C591"
    note: |
      ICC classification independently converged on the same role boundaries
      as the original grammar analysis. This validates the role taxonomy
      as structural rather than artifact of classification method.

      Class 14/17 resolved: Class 14 = FQ per ICC + behavioral evidence
      (C583); Class 17 = CC per C560. AX = 19 classes (corrected from 20).
    internal_structure:
      # C589: Structure inversion — small roles are more internally
      # differentiated than large roles.
      CC: "GENUINE_STRUCTURE (2 active + 1 ghost, 75% KW significant)"
      EN: "DISTRIBUTIONAL_CONVERGENCE (C574: grammatically equivalent, lexically partitioned)"
      FL: "GENUINE_STRUCTURE (hazard/safe split, 100% KW significant)"
      FQ: "GENUINE_STRUCTURE (3-group: CONNECTOR/PREFIXED_PAIR/CLOSER, C593; 13-14 Jaccard=0.000, C594; internal transitions chi2=111, C595)"
      AX: "COLLAPSED (positional gradient only, C572)"
    pipeline_purity:
      # C584: Near-universal pipeline purity
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

  note: |
    Role classes are abstract grammar categories.
    Morphological realization (PREFIX/MIDDLE/SUFFIX composition)
    is NOT part of BCSC. See global morphology contracts.

  gallows_dynamics:
    description: "Gallows characters (t, k, p, f) as paragraph-level markers"
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
      mechanism: "P initiates, T continues"
      provenance: "C867"
    qo_chsh_independence:
      statement: "Gallows use is INDEPENDENT of QO/CHSH lane"
      interpretation: "Gallows mark structure, not material class"
      provenance: "C868"
    functional_model:
      statement: "Gallows function as paragraph/section delimiters"
      interpretation: "Not semantic content, but structural scaffolding"
      provenance: "C869"
    provenance: "C863-C869"

# ============================================================
# KERNEL STRUCTURE
# ============================================================
# SCOPE NOTE (KERNEL_STATE_SEMANTICS phase, 2026-01):
# k, h, e operate at CONSTRUCTION level (within-token morphology).
# Within-token transitions show strong asymmetry: k->e (4.0x), h->e (6.1x),
# e->h blocked (0.004x). This is a TOKEN-BUILDING grammar (C521).
# Between-token transitions at k/h/e level are UNIFORM (all O/E 0.87-1.21).
# Forbidden transitions operate at CLASS level, not k/h/e level (C109).
# The operator roles below describe MORPHOLOGICAL CONTRIBUTION to tokens,
# not execution-level state control.
# ============================================================
kernel:
  description: "Three morphological operators governing within-token construction"
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
    description: "Within-token character ordering follows k -> h -> e (C521)"
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
      description: "e-class tokens dominate corpus"
      provenance: "C339"

    kernel_bigram_ordering:
      description: "h->k suppressed (0 observed); k->k, h->h enriched"
      provenance: "C332"

# ============================================================
# HAZARD TOPOLOGY
# ============================================================
hazards:
  description: "17 disfavored transitions in 5 failure classes (~65% compliance)"

  forbidden_transitions:
    count: 17
    compliance_rate: "~65%"  # C789: 34% violation rate - disfavored, not prohibited
    interpretation: "Statistical bias creating 'cost', not absolute barrier"
    provenance: "C109, C789"

  failure_classes:
    PHASE_ORDERING:
      count: 7
      percentage: "41%"
      description: "Material in wrong phase location"
      provenance: "C110"

    COMPOSITION_JUMP:
      count: 4
      percentage: "24%"
      description: "Impure fractions passing"
      provenance: "C109"

    CONTAINMENT_TIMING:
      count: 4
      percentage: "24%"
      description: "Overflow/pressure events"
      provenance: "C109"

    RATE_MISMATCH:
      count: 1
      percentage: "6%"
      description: "Flow imbalance"
      provenance: "C109"

    ENERGY_OVERSHOOT:
      count: 1
      percentage: "6%"
      description: "Thermal damage"
      provenance: "C109"

  properties:
    asymmetric_rate: "65%"
    distant_from_kernel_rate: "59%"
    suppressed_additional: 8
    provenance: "C111, C112, C386"

# ============================================================
# PROGRAM STRUCTURE
# ============================================================
program_structure:
  description: "Folio = program, Line = control block"

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
    function: "Formal control block with internal positional grammar"
    regularity: "3.3x more regular than random"
    boundary_markers:
      initial: ["daiin", "saiin", "sain"]
      final: ["am", "oly", "dy"]
    link_suppressed_at_boundary: true
    grammar_line_invariant: true
    execution_syntax:
      description: "Lines follow a 5-position functional role grammar"
      positions:
        - position: "SETUP"
          location: "line-initial"
          dominant_roles: ["AX_INIT", "CC"]
          function: "Initialize scaffold and control state"
        - position: "WORK"
          location: "early-medial"
          dominant_roles: ["EN", "FQ"]
          function: "Primary operational activity"
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
      provenance: "C556, C557, C561, C562"
    provenance: "C357, C358, C359, C360, C556, C557, C561, C562"

  paragraph:
    function: "Mini-program unit within folio with header-body structure"
    mean_per_folio: 7.1
    mean_lines_per_paragraph: 4.4
    header_body_structure:
      description: "Paragraph line 1 is HEADER (identification), lines 2+ are BODY (operational)"
      line1_ht_rate: "44.9%"
      body_ht_rate: "29.1%"
      delta: "+15.8pp"
      significance: "Wilcoxon z=13.63, p<10^-20, Cohen's d=0.721"
      provenance: "C840"
    gallows_initial:
      description: "Gallows-initial tokens (t,k,p,f) mark paragraph boundaries"
      paragraph_initial_rate: "8.6% vs 2.7% body"
      ratio: "3.2x enrichment"
      provenance: "C841, C864"
    ht_step_function:
      description: "HT drops from 44.9% (line 1) to 29.1% (lines 2+), then stable"
      pattern: "Step function, not gradual decline"
      provenance: "C842"
    prefix_markers:
      description: "Specific prefixes (ct, ok, qo) mark paragraph header vs body"
      provenance: "C843"
    self_containment:
      description: "Paragraphs are self-contained; no cross-paragraph transitions required"
      provenance: "C845"
    provenance: "C840-C845"

  folio_paragraph_architecture:
    description: "How paragraphs organize within folios"
    role_template:
      statement: "Paragraphs are NOT variations on a folio template"
      evidence: "Each paragraph introduces 63-85% new vocabulary; template model correlation only 0.23"
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
      interpretation: "Paragraphs are largely independent but share folio-level vocabulary pool"
      provenance: "C859"
    section_organization:
      statement: "Different sections show different paragraph patterns"
      bio_profile: "larger paragraphs (46 tok/par)"
      pharma_profile: "smaller paragraphs (13 tok/par)"
      provenance: "C860"
    link_hazard_neutrality:
      statement: "LINK and hazard density are NEUTRAL across paragraph ordinals"
      interpretation: "No paragraph position specializes in monitoring or hazard navigation"
      provenance: "C861"
    provenance: "C855-C862"

# ============================================================
# CONVERGENCE BEHAVIOR
# ============================================================
convergence:
  description: "Programs converge toward stable states"

  target:
    state: "STATE-C"
    type: "MONOSTATE"
    description: "Single stable state is the grammar target"
    provenance: "C079, C084"

  terminal_distribution:
    state_c: "57.8%"
    transitional: "38.6%"
    initial_reset: "3.6%"
    provenance: "C323"

  gradient:
    direction: "STATE-C increases with position"
    description: "Later folios show higher completion rates"
    provenance: "C325"

# ============================================================
# LINK OPERATOR
# ============================================================
link_operator:
  description: "Marks boundary between monitoring and intervention"

  function: "Deliberate waiting/monitoring phases"
  provenance: "C366"

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
    # C366 quantitative claims NOT REPRODUCIBLE with current taxonomy (C804)
    # Qualitative "monitoring/intervention boundary" supported
    predecessor_bias: "NOT SIGNIFICANT (p=0.41)"
    successor_bias: "WEAK (p<0.001, enrichments ~1.1x)"
    note: "Original 1.5x/1.3x/2.7x claims not reproducible"
    provenance: "C804 (revises C366)"

  fl_relationship:
    # LINK and FL are inversely related (C807, C810)
    inverse: true
    distance: "LINK farther from FL (3.91 vs 3.38, p<0.0001)"
    correlation: "rho=-0.222 (negative)"
    direct_transitions: "0.70x expected (depleted)"
    interpretation: "Complementary phases, not adjacent"
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
    mechanism: "Vocabulary composition (HT contains 'ol' more often)"
    provenance: "C806"

  morphology:
    # 'ol' is a legitimate PP MIDDLE (C808)
    ol_is_pp: true
    ol_in_a_vocab: true
    link_pp_rate: "92.4%"
    provenance: "C808"

  complementarity:
    with_escalation: true
    description: "LINK suppressed near escalation"
    provenance: "C340"

# ============================================================
# RECOVERY ARCHITECTURE
# ============================================================
recovery:
  description: "How programs recover from near-hazard states"

  # REVISED 2026-01-31: Original "escape_routes" interpretation was incorrect.
  # C397/C398 measured lane transitions after hazard sources, not escape.
  # Actual hazard recovery is CHSH-dominant (C645: 75.2% post-hazard).
  post_hazard_handling:
    primary_lane: "CHSH"  # e-rich (68.7%), 75.2% post-hazard
    secondary_lane: "QO"  # k-rich (70.7%), depleted near hazards (0.55x)
    mechanism: "CHSH handles hazard-adjacent contexts; QO operates hazard-distant"
    provenance: "C601, C643, C645"

  lane_transition_pattern:
    # What C397/C398 actually measured (corrected interpretation)
    observation: "After CHSH hazard-source tokens, QO follows 25-47%"
    interpretation: "Normal CHSH->QO lane alternation, not escape mechanism"
    provenance: "C397 (REVISED), C398 (REVISED), C643"

  stability_anchor:
    operator: "e"
    function: "Anchors system to stable state"
    note: "CHSH MIDDLEs are 68.7% e-content, explaining CHSH recovery dominance"
    provenance: "C105"

  safe_precedence:
    description: "Safe operations precede hazardous ones"
    provenance: "C399"

# ============================================================
# DESIGN FREEDOM
# ============================================================
design_freedom:
  description: "Asymmetric design freedom across dimensions"

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
  provenance: "C458"

# ============================================================
# CONTROL LOOP SYNTHESIS
# ============================================================
# Added v1.7: CONTROL_LOOP_SYNTHESIS phase findings (C810-C815)
control_loop:
  description: "Integration of KERNEL, LINK, FL into unified control model"

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
      function: "Escape/recovery operations"
      mean_position: 0.576
      density: "4.7% of tokens"

  canonical_ordering:
    sequence: "daiin -> LINK -> KERNEL -> ol -> FL"
    positions: "0.413 -> 0.476 -> 0.482 -> 0.511 -> 0.576"
    interpretation: "CC initiates, monitoring early, processing throughout, CC bridges to escape"
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
    interpretation: "Phases are temporally flexible, not rigidly positional"
    provenance: "C815"

  phase_relationships:
    link_fl:
      relationship: "Inverse/complementary (not adjacent)"
      direct_transitions: "0.70x expected"
      provenance: "C807, C810"
    fl_chaining:
      enrichment: "2.11x"
      interpretation: "Escape is multi-step, not single-token"
      loop_closure: "FL->KERNEL neutral (0.86x)"
      provenance: "C811"

  folio_predictors:
    # What predicts escape (FL) rate at folio level
    strongest: "KERNEL (rho=-0.528, p<0.0001)"
    interpretation: "High kernel density = stable program, low escape"
    provenance: "C814"

# ============================================================
# SECTION PROFILES
# ============================================================
# Added v1.2: CLASS_SEMANTIC_VALIDATION phase findings
section_profiles:
  description: "Section-specific behavioral signatures within B"

  anticorrelation:
    statement: "ENERGY and FLOW roles are anticorrelated across sections"
    correlation: "r = -0.89"
    interpretation: "Sections specialize in energy-intensive vs flow-intensive programs"
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

  note: |
    Section profiles describe observational signatures, not
    different grammars. The same 49-class grammar applies to
    all sections (C124). Profiles reflect different operational
    emphases within a single grammar.

# ============================================================
# VOCABULARY ARCHITECTURE
# ============================================================
# Added 2026-01-25: CLASS_COMPATIBILITY_ANALYSIS phase findings
vocabulary_architecture:
  description: "Grammar-vocabulary relationship structure"

  class_level:
    description: "49-class grammar applies universally to all folios"
    coverage: "100%"
    folio_invariant: true
    provenance: "C121, C124"

  member_level:
    description: "Token variants within classes are NOT interchangeable"
    behavioral_heterogeneity: true  # Different MIDDLEs -> different transitions
    js_divergence: "73% of MIDDLE pairs have JS > 0.4"
    provenance: "C506.b"

  folio_uniqueness:
    description: "Each folio contributes unique vocabulary"
    unique_folio_rate: "98.8%"  # 81/82 folios
    mean_unique_per_folio: 10.5
    total_unique_middles: 858
    unique_share_of_total: "64%"
    only_non_unique_folio: "f95r1"
    provenance: "C531"

  folio_exclusivity:
    description: "Unique vocabulary is primarily B-internal"
    b_exclusive_rate: "88%"  # Not in A
    pp_rate: "12%"  # A-derived
    azc_modulates: "shared PP vocabulary only, not folio identity"
    provenance: "C532"

  grammatical_consistency:
    description: "Unique MIDDLEs fill same grammatical slots"
    slot_match_rate: "75%"
    adjacent_folio_class_ratio: "1.30x"  # vs non-adjacent
    interpretation: "Different words, same roles"
    provenance: "C533"

  minimality:
    description: "Folio count is structurally determined by vocabulary"
    min_folios_for_coverage: 81
    actual_folios: 82
    redundancy_ratio: "1.01x"
    max_pairwise_jaccard: "<50%"  # Zero pairs exceed
    provenance: "C535"

  differentiation_principle: |
    Grammar is universal at CLASS level (same 49 classes everywhere).
    Differentiation occurs at TOKEN level within classes.
    This enables material-appropriate execution via variant selection,
    not via different procedures. (C506.b, C537)

# ============================================================
# HT/UN STRUCTURAL INTEGRATION
# ============================================================
# Note: HT (Human Track) = UN (Unclassified) are identical populations (C740).
# While HT is OUTSIDE the 49-class grammar, it has structural properties
# that interface with the grammar. BCSC documents these interface properties.
ht_un_integration:
  description: "HT/UN tokens (4,421 types, 7,042 occurrences) are outside 49-class grammar but structurally integrated"

  population_identity:
    statement: "HT = UN (identical by definition)"
    ht_types: 4421
    ht_occurrences: 7042
    hapax_rate: "74.1%"
    provenance: "C740"

  c475_compliance:
    statement: "HT tokens obey C475 MIDDLE incompatibility when co-occurring with classified tokens"
    violation_rate: "0.44%"
    interpretation: "HT is structurally constrained by the same forbidden pair rules"
    provenance: "C742"

  novel_combinations:
    statement: "HT uses MIDDLE combinations that never occur in classified adjacencies"
    novel_pair_rate: "11.19%"  # Pairs where both MIDDLEs in classified but pair not seen
    ht_exclusive_middles: "90.7%"  # MIDDLEs that appear only in HT
    classified_overlap: "14.4%"  # HT-HT pairs also seen in classified
    interpretation: |
      HT operates in a distinct combinatorial space. It doesn't violate C475
      forbidden pair rules (0.44%), but it combines MIDDLEs differently than
      classified tokens. This supports HT as a structurally separate layer
      that shares morphological building blocks but uses them independently.
    provenance: "C812"

  lane_architecture:
    statement: "HT tokens are lane-segregated (CHSH-dominant) but lane-indifferent in transitions"
    chsh_fraction: "dominant"
    lane_transitions: "indifferent (no lane-tracking)"
    provenance: "C743, C744"

  line1_enrichment:
    statement: "Line-1 has 50.2% HT vs 29.8% on lines 2+ (Tier 0 frozen fact)"
    delta: "+20.3 percentage points"
    interpretation: "Opening lines use non-operational vocabulary before executable sequence"
    tier: 0
    provenance: "C747"

  line1_composite_header:
    statement: "Line-1 HT is a two-part composite header"
    structure:
      pp_component:
        share: "68.3%"
        function: "A-context declaration"
        mechanism: "PP MIDDLEs predict best-match A folio at 15.8x random"
        prediction_accuracy: "13.9% vs 0.88% baseline"
      b_exclusive_component:
        share: "31.7%"
        function: "Folio identification"
        folio_unique_rate: "94.1%"
    independence: "PP fraction does NOT correlate with body PP size (rho=0.002)"
    interpretation: |
      Line-1 is metadata, not operational content.
      PP portion declares: "This program operates under A-folio X's constraints"
      B-exclusive portion declares: "This is program Y"
      The operational sequence begins on line 2.
    provenance: "C794, C795"

  folio_distribution:
    statement: "HT density varies by folio in compensatory pattern"
    interpretation: "Folios with lower classified coverage have higher HT density"
    provenance: "C746"

  non_operational:
    statement: "HT tokens do not participate in grammar operations (C404-C405 protected)"
    note: "Structural integration does not imply operational participation"
    provenance: "C404, C405"

  line1_ht_folio_specificity:
    statement: "Line-1 HT tokens are highly folio-specific"
    folio_singleton_rate: "85.9%"  # appear in only ONE folio
    folio_unique_and_line1_only: "1,229 tokens (67%)"
    interpretation: "Line-1 HT = folio identification vocabulary"
    provenance: "C870"

  ht_role_cooccurrence:
    statement: "HT tokens show systematic role cooccurrence patterns"
    chsh_bias: "HT preferentially co-occurs with CHSH lane"
    interpretation: "HT identification is lane-aware"
    provenance: "C871"

  ht_discrimination_vocabulary:
    statement: "HT tokens form a discrimination vocabulary for folio/procedure identification"
    function: "Identify WHICH procedure, not WHAT material"
    semantic_ceiling_compliant: true
    vocabulary_size: "4,421 types"
    line1_concentration: "50.2% of Line-1 are HT"
    interpretation: |
      HT is the identification layer that complements the operational grammar (PP).
      Grammar (PP) encodes HOW to execute; HT encodes WHICH procedure is active.
      This division is by design - maintains semantic ceiling (C120).
    provenance: "C872"

# ============================================================
# ROBUSTNESS
# ============================================================
robustness:
  description: "Grammar is robust to noise, ablation, and cross-validation"

  noise_robustness:
    description: "10% corruption = 3.3% entropy increase"
    provenance: "C328"

  ablation_robustness:
    description: "Top 10 tokens removed = 0.8% entropy change"
    provenance: "C329"

  cross_validation:
    description: "Leave-one-folio-out = max 0.25% entropy change"
    provenance: "C330"

  minimality:
    description: "49-class functional classification confirmed"
    provenance: "C331"

# ============================================================
# NEGATIVE GUARANTEES
# ============================================================
negative_guarantees:
  - guarantee: "No Currier A references"
    reason: "BCSC is A-agnostic"

  - guarantee: "No AZC references"
    reason: "BCSC is AZC-agnostic"

  - guarantee: "No Human Track internal structure"
    reason: "HT is separate layer; however HT/UN obeys C475 and lane architecture (C740-C750)"

  - guarantee: "No process domain semantics"
    reason: "Tier 3 speculative layer"

  - guarantee: "No token meanings"
    reason: "Irrecoverable by design"

  - guarantee: "No family structure"
    reason: "Families are emergent, not grammar partitions (C126, C144)"

  - guarantee: "No morphological composition rules"
    reason: "BCSC uses role classes only; composition belongs elsewhere"

# ============================================================
# EXPLICITLY DEFERRED
# ============================================================
deferred:
  - topic: "Currier A structure"
    reason: "Belongs to CASC"

  - topic: "AZC positional zones"
    reason: "Belongs to AZC-ACT"

  - topic: "AZC -> B propagation"
    reason: "Belongs to AZC-B-ACT"

  - topic: "Human Track layer"
    reason: "Separate contract if needed"

  - topic: "Process domain interpretation"
    reason: "Tier 3 speculative layer"

  - topic: "Token meanings"
    reason: "Irrecoverable by design"

  - topic: "Historical context"
    reason: "Non-binding interpretive layer"

  - topic: "Family structure"
    reason: "Emergent organization, not grammar (C126, C144)"

  - topic: "Morphological composition"
    reason: "Global morphology contracts handle this"

# ============================================================
# DISALLOWED INTERPRETATIONS
# ============================================================
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

# ============================================================
# NON-NORMATIVE ANNOTATIONS
# ============================================================
annotations:
  note: "Empirical observations, NOT structural guarantees"
  status: "NON-NORMATIVE"

  coverage_statistics:
    token_coverage: "61.9%"
    folio_count: 83
    token_types: 479
    instruction_classes: 49
    compression_ratio: "9.8x"
    provenance: "C121"

  kernel_statistics:
    e_class_corpus_share: "36%"
    e_recovery_path_rate: "54.7%"
    e_trigram_rate: "97.2%"
    provenance: "C105, C333, C339"

  hazard_statistics:
    forbidden_count: 17
    asymmetric_rate: "65%"
    distant_from_kernel: "59%"
    phase_ordering_dominant: "41%"
    provenance: "C109, C110, C111, C112"

  convergence_statistics:
    state_c_terminal: "57.8%"
    transitional_terminal: "38.6%"
    completion_gradient_rho: "+0.24"
    provenance: "C323, C325"

  link_statistics:
    density: "38%"
    section_b: "19.6%"
    section_h: "9.1%"
    section_c: "10.1%"
    provenance: "C334"

  design_statistics:
    hazard_cv: "0.04-0.11"
    recovery_cv: "0.72-0.82"
    provenance: "C458"

  robustness_statistics:
    noise_entropy_increase: "3.3%"
    ablation_entropy_change: "0.8%"
    cross_validation_max_change: "0.25%"
    provenance: "C328, C329, C330"

  execution_syntax_statistics:
    icc_role_count: 5
    line_positions: 4  # SETUP, WORK, CHECK, CLOSE
    energy_flow_correlation: "-0.89"
    daiin_trigger_frequency: "highest initial bigram"
    provenance: "C547, C551, C556, C557"

  role_anatomy_statistics:
    en_classes: 18
    en_tokens: 7211
    en_suffix_types: 17
    en_internal_verdict: "DISTRIBUTIONAL_CONVERGENCE"
    fl_classes: 4
    fl_tokens: 1078
    fl_suffix_types: 2
    fl_hazard_source_bias: "4.5x"
    fl_internal_verdict: "GENUINE_STRUCTURE"
    fq_classes: 4
    fq_tokens: 2890
    fq_suffix_types: 1
    fq_internal_verdict: "GENUINE_STRUCTURE"
    fq_3group_silhouette: 0.68
    fq_13_14_jaccard: 0.000
    fq_transition_chi2: 111.0
    fq_mean_run_length: 1.19
    fq_class23_final_rate: "29.8%"
    cc_classes: 4  # {10, 11, 12, 17} per C560, C581
    cc_tokens: 1023
    cc_suffix_types: 0
    cc_internal_verdict: "GENUINE_STRUCTURE"
    suffix_selectivity_chi2: 5063.2
    pipeline_purity: "CC/EN/FL/FQ 100% PP; AX 98.2%"
    provenance: "C573-C597"

  folio_level_composition:
    cc_subfamily_prediction_rho: "0.345-0.355"  # CC_DAIIN->CHSH and CC_OL_D->QO
    c412_regime_mediation: "27.6%"  # C412 partially REGIME artifact
    two_lane_escape_rho: "-0.506"  # Lane balance -> escape density
    two_lane_vs_ch_preference: "68% stronger"  # |0.506| vs |0.301|
    lane_balance_independent: true  # Partial rho=-0.452 after controlling ch_pref
    provenance: "C603, C604, C605"

  ax_architecture_statistics:
    ax_classes: 19
    ax_token_share: "16.6%"  # corrected: Class 14 removed (FQ), Class 17 removed (CC)
    ax_pp_middle_rate: "98.2%"
    ax_positional_subtypes: 3  # INIT, MED, FINAL
    ax_effective_groups: "≤2"
    ax_best_silhouette: "0.18"
    ax_context_classifier_accuracy: "6.8%"  # below 10.3% baseline
    provenance: "C563, C567, C568, C572"

# ============================================================
# PROVENANCE MAP
# ============================================================
provenance:
  tier_0_frozen:
    - "C074"   # Dominant Convergence
    - "C079"   # Only STATE-C Essential
    - "C084"   # System Targets MONOSTATE
    - "C109"   # 5 Hazard Failure Classes
    - "C115"   # 0 Non-Executable Tokens
    - "C121"   # 49 Instruction Classes
    - "C124"   # 100% Grammar Coverage
    - "C171"   # Closed-Loop Control Only

  kernel:
    - "C085"   # 10 primitives
    - "C089"   # Core within core
    - "C103"   # k = ENERGY_MODULATOR
    - "C104"   # h = PHASE_MANAGER
    - "C105"   # e = STABILITY_ANCHOR
    - "C107"   # Kernel BOUNDARY_ADJACENT

  hazard:
    - "C110"   # PHASE_ORDERING dominant
    - "C111"   # 65% asymmetric
    - "C112"   # 59% distant from kernel
    - "C386"   # Additional suppressed transitions

  program_line:
    - "C357"   # Lines deliberately chunked
    - "C358"   # Boundary tokens
    - "C359"   # LINK suppressed at boundaries
    - "C360"   # Grammar LINE-INVARIANT

  link:
    - "C334"   # LINK section conditioning
    - "C339"   # E-class dominance
    - "C340"   # LINK-escalation complementarity
    - "C365"   # LINK spatially uniform - REFUTED by C805 (boundary enrichment)
    - "C366"   # LINK marks grammar state transitions - REVISED by C804 (quantitative claims not reproducible)

  convergence:
    - "C323"   # Terminal distribution
    - "C324"   # Section-dependent terminals
    - "C325"   # Completion gradient

  recovery:
    - "C397"   # qo-prefix post-source frequency (REVISED: lane transition, not escape)
    - "C398"   # Post-source role distribution (REVISED: baseline after CHSH)
    - "C399"   # Safe precedence pattern
    - "C601"   # QO zero hazard participation
    - "C643"   # QO-CHSH rapid alternation
    - "C645"   # CHSH 75.2% post-hazard dominance

  design:
    - "C458"   # Execution design clamp

  robustness:
    - "C328"   # Noise robustness
    - "C329"   # Ablation robustness
    - "C330"   # Cross-validation stable
    - "C331"   # 49-class minimality

  symmetry:
    - "C391"   # Time-reversal symmetry

  family_exclusion:
    - "C126"   # 0 cross-family contradictions
    - "C141"   # Cross-family transplant = zero degradation
    - "C144"   # Families are emergent

  vocabulary_architecture:
    - "C506.b" # Intra-class behavioral heterogeneity
    - "C531"   # Folio unique vocabulary prevalence
    - "C532"   # Unique MIDDLE B-exclusivity
    - "C533"   # Unique MIDDLE grammatical slot consistency
    - "C535"   # B folio vocabulary minimality
    - "C537"   # Token-level material differentiation

  execution_syntax:
    - "C547"   # ICC-based role validation
    - "C548"   # EN role pattern
    - "C549"   # FL role pattern
    - "C550"   # FQ role pattern
    - "C551"   # ENERGY/FLOW anticorrelation
    - "C552"   # Section B profile
    - "C553"   # Section H profile
    - "C554"   # Section C profile
    - "C555"   # Section S profile
    - "C556"   # 5-position line syntax
    - "C557"   # daiin trigger
    - "C561"   # or→aiin bigram
    - "C562"   # FLOW final hierarchy

  ax_architecture:
    - "C563"   # AX positional sub-structure
    - "C564"   # AX_INIT characterization
    - "C565"   # AX_MED characterization
    - "C566"   # AX_FINAL characterization
    - "C567"   # AX MIDDLE sharing (98.2% PP)
    - "C568"   # AX pipeline ubiquity
    - "C569"   # AX PREFIX exclusivity
    - "C570"   # AX articulator stratification
    - "C571"   # PREFIX as role selector
    - "C572"   # AX class behavioral collapse

  en_anatomy:
    - "C573"   # EN definitive count (18 classes)
    - "C574"   # EN distributional convergence
    - "C575"   # EN 100% pipeline-derived
    - "C576"   # EN MIDDLE vocabulary bifurcation
    - "C577"   # EN interleaving content-driven
    - "C578"   # EN exclusive MIDDLEs (30)
    - "C579"   # CHSH-first ordering bias
    - "C580"   # EN trigger profile differentiation

  small_role_anatomy:
    - "C581"   # CC definitive census
    - "C582"   # FL definitive census
    - "C583"   # FQ definitive census
    - "C584"   # Near-universal pipeline purity
    - "C585"   # Cross-role MIDDLE sharing
    - "C586"   # FL hazard-safe split
    - "C587"   # FQ internal differentiation
    - "C588"   # Suffix role selectivity
    - "C589"   # Small role genuine structure
    - "C590"   # CC positional dichotomy
    - "C591"   # Five-role complete taxonomy
    - "C592"   # C559 membership correction

  fq_anatomy:
    - "C593"   # FQ 3-group structure (CONNECTOR/PREFIXED_PAIR/CLOSER)
    - "C594"   # FQ 13-14 complete vocabulary bifurcation (Jaccard=0.000)
    - "C595"   # FQ internal transition grammar (chi2=111)
    - "C596"   # FQ-FL position-driven symbiosis (hazard p=0.33 NS)
    - "C597"   # FQ Class 23 boundary dominance (29.8% final)

  sub_role_interaction:
    - "C598"   # Cross-boundary sub-group structure (8/10 significant)
    - "C599"   # AX scaffolding routing (AX_FINAL->FQ_CONN)
    - "C600"   # CC trigger selectivity (daiin->CHSH, ol-derived->QO)
    - "C601"   # Hazard sub-group concentration (FL_HAZ/EN_CHSH/FQ_CONN)
    - "C602"   # REGIME-conditioned sub-role grammar (4/5 REGIME-dependent)

  sister_pair_decomposition:
    - "C603"   # CC folio-level subfamily prediction (OL_D->QO rho=0.355, DAIIN->CHSH rho=0.345)
    - "C604"   # C412 REGIME decomposition (27.6% mediation; vanishes within REGIME_1/2)
    - "C605"   # Two-lane folio-level validation (lane balance rho=-0.506, independent of ch_preference)

  ht_un_reconciliation:
    - "C740"   # HT/UN population identity (identical by definition)
    - "C741"   # HT C475 minimal participation
    - "C742"   # HT C475 compliance (0.44% violation)
    - "C743"   # HT lane segregation (CHSH-dominant)
    - "C744"   # HT lane indifference (no lane-tracking)
    - "C745"   # HT coverage metric sensitivity
    - "C746"   # HT folio compensatory distribution
    - "C747"   # Line-1 HT enrichment (50.2% vs 29.8%, Tier 0)
    - "C748"   # Line-1 step function
    - "C749"   # Line-1 HT morphological distinction
    - "C750"   # Opening-only asymmetry
    - "C794"   # Line-1 composite header structure (68.3% PP + 31.7% B-exclusive)
    - "C795"   # Line-1 A-context prediction (15.8x random)
    - "C812"   # HT novel MIDDLE combinations (11.19% novel pairs, distinct combinatorial space)

  fl_primitive_architecture:
    - "C770"   # FL kernel exclusion (0 kernel chars)
    - "C771"   # FL character restriction (only a,d,i,l,m,n,o,r,y)
    - "C772"   # FL primitive substrate (base layer for all roles)
    - "C773"   # FL hazard position split
    - "C774"   # FL outside forbidden topology
    - "C775"   # Hazard FL escape driver
    - "C776"   # Post-FL kernel enrichment
    - "C777"   # FL state index

  control_topology:
    - "C782"   # CC kernel paradox (highest contact, lowest compound)
    - "C783"   # Forbidden pair asymmetry (direction matters)
    - "C784"   # FL/AX hazard immunity (0% exposure)
    - "C785"   # FQ medial targeting
    - "C786"   # FL forward bias (83.3% forward-facing)
    - "C787"   # FL state reset prohibition (no FL->FL)

  cc_mechanics:
    - "C788"   # CC singleton identity (daiin, ol, k are specific tokens)
    - "C789"   # Forbidden pair permeability (34% violation - disfavored not prohibited)
    - "C790"   # CC positional gradient
    - "C791"   # CC-EN dominant flow (78.3% CC->EN)

  link_operator_architecture:
    - "C804"   # LINK transition grammar revision (C366 quantitative claims not reproducible)
    - "C805"   # LINK boundary enrichment (refutes C365 spatially uniform)
    - "C806"   # LINK-HT overlap (OR=1.50)
    - "C807"   # LINK-FL inverse relationship (distance 3.91 vs 3.38)
    - "C808"   # 'ol' is PP MIDDLE (92.4% LINK tokens are PP)
    - "C809"   # LINK-kernel separation (farther from kernel chars)

  control_loop_synthesis:
    - "C810"   # LINK-FL non-adjacency (0.70x direct transitions)
    - "C811"   # FL chaining (2.11x enrichment, multi-step escape)
    - "C812"   # HT novel MIDDLE combinations (11.19% novel pairs)
    - "C813"   # Canonical phase ordering (LINK->KERNEL->FL)
    - "C814"   # Kernel-escape inverse (rho=-0.528)
    - "C815"   # Phase position significance (1.5% variance, flexible timing)

  cc_control_loop_integration:
    - "C816"   # CC positional ordering (daiin->LINK->KERNEL->ol->FL)
    - "C817"   # CC lane routing confirmed (daiin->CHSH 90.8%, rapid decay)
    - "C818"   # CC kernel bridge (Class 17 = CC-KERNEL interface, 88% kernel)
    - "C819"   # CC boundary asymmetry (daiin initial, ol/ol_derived medial)
    - "C820"   # CC hazard immunity (0/700 forbidden, EN absorbs 99.8%)

  regime_line_syntax_interaction:
    - "C821"   # Line syntax REGIME invariance (all roles p>0.4, 0.13% variance)
    - "C822"   # CC position REGIME invariance (daiin/ol universal)
    - "C823"   # Bigram REGIME partial variation (23.3% show effects, 76.7% universal)

  b_paragraph_structure:
    - "C840"   # B paragraph mini-program structure (header 44.9% HT, body 29.1%)
    - "C841"   # B paragraph gallows-initial markers (3.2x enrichment)
    - "C842"   # B paragraph HT step function (line 1 vs body)
    - "C843"   # B paragraph prefix identification markers
    - "C844"   # Folio line 1 double-header effect
    - "C845"   # B paragraph self-containment

  folio_paragraph_architecture:
    - "C855"   # Folio role template (parallel programs, not template)
    - "C856"   # Folio vocabulary distribution (distributed, not concentrated)
    - "C857"   # First paragraph ordinariness (not special)
    - "C858"   # Paragraph count complexity proxy (rho=0.42)
    - "C859"   # Paragraph vocabulary convergence (weak)
    - "C860"   # Section paragraph organization (BIO large, PHARMA small)
    - "C861"   # LINK/hazard paragraph neutrality
    - "C862"   # Role template verdict (PARALLEL_PROGRAMS)

  gallows_paragraph_dynamics:
    - "C863"   # Paragraph-ordinal EN subfamily gradient
    - "C864"   # Gallows paragraph marker (8.6% initial vs 2.7% body)
    - "C865"   # Gallows folio position distribution
    - "C866"   # Gallows morphological patterns
    - "C867"   # P-T transition dynamics
    - "C868"   # Gallows-QO/CHSH independence
    - "C869"   # Gallows functional model

  ht_discrimination_vocabulary:
    - "C870"   # Line-1 HT folio specificity (85.9% singleton)
    - "C871"   # HT role cooccurrence pattern (CHSH bias)
    - "C872"   # HT discrimination vocabulary interpretation

  control_flow_semantics:
    - "C873"   # Kernel positional ordering (e < h < k)
    - "C874"   # CC token functions (daiin=init, ol=continue)
    - "C875"   # Escape trigger grammar (80.4% from hazard FL stages)
    - "C876"   # LINK checkpoint function
    - "C877"   # Role transition grammar (EN->EN 38.5%, CC->EN 37.7%)
    - "C878"   # Section program variation
    - "C879"   # Process domain verdict (batch processing)
    - "C880"   # Integrated control model

  closed_loop_orthogonality:
    - "C886"   # Transition probability directionality (symmetric constraints, directional execution)
    - "C890"   # Recovery rate-pathway independence
    - "C891"   # ENERGY-FREQUENT inverse correlation
    - "C892"   # Post-FQ h-dominance (recovery via phase-check)
    - "C893"   # Paragraph kernel signature predicts operation type
    - "C894"   # REGIME_4 recovery concentration
    - "C895"   # Kernel-recovery correlation asymmetry
    - "C896"   # Process mode discrimination via kernel profile

  apparatus_markers:
    - "C897"   # Prefixed FL MIDDLEs as line-final state markers

# ============================================================
# END OF BCSC
# ============================================================

```

---

# A->AZC Activation Contract

**Source:** `context/STRUCTURAL_CONTRACTS/azc_activation.act.yaml`

```yaml
# ============================================================
# AZC-ACT: AZC Activation Contract
# Version: 1.0
# ============================================================
#
# This is a DERIVED, READ-ONLY specification.
# It introduces NO NEW CLAIMS.
# Constraints remain authoritative.
# Do not edit without constraint update.
#
# Purpose: Thin, directional layer specifying how AZC transforms
# Currier A entries under positional legality.
#
# This is NOT a standalone AZC schema. It is an A-facing
# interface contract describing the A->AZC boundary only.
#
# ============================================================

meta:
  name: "AZC Activation Contract"
  acronym: "AZC-ACT"
  version: "1.1"
  date: "2026-01-29"
  status: "LOCKED"
  layer_type: "mapping contract"
  derived_from: "Tier-2 constraints only"
  audit_note: "Reviewed against constraints through C872. No changes needed - new constraints are internal A/B structure, not pipeline boundaries."
  governance: |
    AZC-ACT is NOT authoritative. Constraints are authoritative.
    AZC-ACT describes HOW A entries activate AZC constraints.
    Do not edit without updating source constraints first.

# ============================================================
# SCOPE & GUARANTEES
# ============================================================
scope:
  function: "How AZC constrains Currier A entries under positional legality"
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
  note: "AZC indexes vocabulary by position, it does not affect content or execution"

guarantees:
  - id: "VOCABULARY_ACTIVATED"
    statement: "AZC constraint activation is vocabulary-driven"
    provenance: "C441"

  - id: "COMPATIBILITY_GROUPING"
    statement: "AZC folios group vocabulary by compatibility signature"
    provenance: "C442"

  - id: "LEGALITY_INHERITANCE"
    statement: "AZC constraint profiles propagate causally into B"
    provenance: "C468"

  - id: "NO_CONTENT_MUTATION"
    statement: "AZC does not mutate A entry contents"
    provenance: "C444"

  - id: "FAMILY_AGNOSTIC_MECHANISM"
    statement: "AZC legality mechanism is family-agnostic"
    mechanism: "Zodiac and A/C instantiate the same legality zones; ordered subscripts (R1-R3, S0-S2) are one scaffold rendering, not the schema"
    note: "Apps must treat positions as abstract legality classes, not family-specific symbolic states"
    provenance: "C430-C436, C441-C443"

# ============================================================
# INVARIANTS (structural guarantees for tooling/testing)
# ============================================================
invariants:
  monotonicity:
    statement: "Survivor options never increase from earlier to later positions"
    description: "Escape permission decreases monotonically through R-series"
    provenance: "C443, C444"

  position_independence:
    statement: "The SAME A-type can appear in any position; position determines legality, not content"
    provenance: "C444"

  vocabulary_mediation:
    statement: "All A->B relationships are vocabulary-mediated, not addressable"
    provenance: "C384, C441"

  scaffold_independence:
    statement: "Legality zones are independent of scaffold presentation"
    description: "Zodiac ordered subscripts and A/C unordered positions map to the same abstract zones (C, P, R, S)"
    provenance: "C430-C436"

# ============================================================
# INPUTS (what enters AZC)
# ============================================================
inputs:
  accepted:
    type: "registry_entry"
    from_casc: "record_types.registry_entry"
    minimum_tokens: 2
    description: "Compound constraint bundles from Currier A"
    provenance: "C482, C484"

  excluded:
    type: "control_operator"
    reason: "Control operators are meta-structural, not registry content"
    provenance: "C484"

# ============================================================
# POSITIONAL ZONES
# ============================================================
# These are LEGALITY zones, not pipeline stages.
# Position determines what constraints apply, not execution order.

positional_zones:
  description: "Finite placement classes with distinct legality semantics"
  provenance: "C306, C313"

  zones:
    C:
      function: "Interior placement, rotation-tolerant"
      escape_permission: "moderate"
      provenance: "C306, C317"

    # NOTE: P (Paragraph) is NOT a diagram position. It is paragraph text that
    # appears on AZC folios but is physically separate from circular diagrams.
    # See azc_transcript_encoding.md for physical meanings.
    # P escape statistics (11.6%, P2=24.7%) characterize Currier A material
    # on AZC folios, not diagram text. Diagram positions are C, R-series, S-series only.

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

# ============================================================
# TRANSFORMATIONS
# ============================================================
# What happens when an A entry is placed in an AZC position

transformations:
  description: "Constraints applied to A entries under position"

  compatibility_grouping:
    mechanism: "MIDDLE positional exclusivity"
    observation: "Specialized vocabulary appears at distinct positions; combinations that don't occur reflect fixed positional encoding"
    provenance: "C442, C475"

  escape_permission_changes:
    mechanism: "Phase-indexed gradient"
    effect: "Same A-type has different intervention permission by position"
    provenance: "C443, C444"

  categorical_resolution:
    mechanism: "Token legality, not parametric encoding"
    effect: "Operational conditions represented categorically"
    provenance: "C469"

  vocabulary_legality:
    mechanism: "A-record morphology corresponds to B vocabulary availability"
    expansion: false  # AZC does NOT expand vocabulary beyond A specification
    observation: "Only tokens with matching PREFIX, MIDDLE, and SUFFIX appear in B execution"
    morphological_correspondence:  # C502.a - full morphological correspondence
      middle_only:
        legal_tokens: "257 (5.3%)"
        excluded: "94.7%"
        note: "MIDDLE is primary discriminator (C472)"
      middle_plus_prefix:
        legal_tokens: "92 (1.9%)"
        additional_reduction: "64%"
        note: "PREFIX adds AZC family affinity (C471)"
      middle_plus_suffix:
        legal_tokens: "130 (2.7%)"
        additional_reduction: "50%"
        note: "SUFFIX adds regime breadth (C495)"
      full_morphology:
        legal_tokens: "38 (0.8%)"
        additional_reduction: "85% beyond MIDDLE"
        note: "All three axes compose independently"
    legacy_claim: "Original ~80%/~96 of 480 was MIDDLE-only against token types"
    note: "AZC provides compatibility grouping and positional encoding, not vocabulary expansion"
    provenance: "C481, C502, C502.a"

  content_invariants:
    - "No movement of tokens"
    - "No selection"
    - "No branching"
    - "No instruction creation"
    - "No mutation of entry contents"

# ============================================================
# PERSISTENCE RULES
# ============================================================
persistence:
  a_survivor_independence:
    statement: "A-vocabulary tokens persist independently of AZC legality windows"
    provenance: "C343"

  vanishing_semantics:
    statement: "Position exclusivity, not active filtering"
    description: "Each PREFIX+MIDDLE appears at exactly one position; absence elsewhere reflects fixed encoding"
    mechanism: "AZC is static positional encoding, not selective filter"
    provenance: "C444"

  restriction_inheritance:
    statement: "MIDDLE restrictions transfer to B"
    provenance: "C470"

# ============================================================
# MORPHOLOGICAL BINDING
# ============================================================
morphological_binding:
  description: "How A entry morphology maps to AZC constraints"

  prefix_affinity:
    mechanism: "PREFIX encodes AZC family affinity"
    note: "Affinity shapes likely postures, not exclusive mapping"
    provenance: "C471"

  middle_specificity:
    mechanism: "MIDDLE is primary carrier of folio specificity"
    provenance: "C472"

  constraint_bundle:
    statement: "Each A entry functions as a constraint bundle"
    mechanism: "PREFIX + MIDDLE + SUFFIX specifies compatibility signature"
    effect: "Determines which AZC legality envelopes apply"
    provenance: "C473"

# ============================================================
# NEGATIVE GUARANTEES
# ============================================================
negative_guarantees:
  - guarantee: "No token movement"
    reason: "AZC encodes position, does not route"

  - guarantee: "No selection"
    reason: "AZC records vocabulary position, operator selects vocabulary"

  - guarantee: "No branching"
    reason: "No conditional paths in AZC structure"

  - guarantee: "No instruction creation"
    reason: "AZC encodes position, B executes"

  - guarantee: "No semantic content"
    reason: "Positions are legality regimes, not meanings"

  - guarantee: "No dynamic AZC decision-making"
    reason: "F-AZC-015 closed this (Case B confirmed)"

# ============================================================
# EXPLICITLY DEFERRED
# ============================================================
# These belong to full AZC CASC, NOT to this activation contract

deferred:
  - topic: "Zodiac vs A/C family internal scaffolds"
    reason: "Family-level structure, not A-entry transformation"

  - topic: "Ordered subscript internal semantics (R1-R3, S1-S2)"
    reason: "Zodiac internal organization, not A-entry effects"

  - topic: "Spiral topology"
    reason: "Diagram geometry, outside positional legality"

  - topic: "Diagram physical layout"
    reason: "Geometric structure, not constraint mechanics"

  - topic: "Orientation postures"
    reason: "Physical interpretation, not structural contract"

  - topic: "HT positional asymmetries"
    reason: "HT layer belongs to separate contract (HT-ACT)"

# ============================================================
# DISALLOWED INTERPRETATIONS
# ============================================================
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

  - interpretation: "AZC is lookup table for A entries"
    reason: "Vocabulary-activated constraints, not addressable mapping"
    provenance: "C441"

  - interpretation: "AZC decides dynamically"
    reason: "Ambient legality field, not decision engine"
    provenance: "F-AZC-015"

  - interpretation: "AZC expands vocabulary beyond A specification"
    reason: "AZC restricts, does not expand. Only A-record MIDDLEs are legal for B execution."
    provenance: "C481, C502"

# ============================================================
# NON-NORMATIVE ANNOTATIONS
# ============================================================
# Empirical observations for reference. These are NOT contractual
# guarantees and may vary with filtering or dataset changes.

annotations:
  note: "These are empirical observations, NOT structural guarantees"
  status: "NON-NORMATIVE"

  zone_frequencies:
    C: "17.1% (A/C family dominant)"
    note: "Frequencies are dataset-dependent; P is paragraph text, not diagram"

  interior_rates:
    C: "77.6%"
    R_series: "89-95%"
    S_series: "95%+ at line edges"
    # P is paragraph text, not diagram - excluded from interior analysis

  escape_rates:
    # Diagram positions only (C, R, S):
    C: "~1.4%"
    R1: "2.0%"
    R2: "1.2%"
    R3: "0%"
    S_series: "0%"
    # P is paragraph text (not diagram): P=11.6%, P2=24.7% - characterizes Currier A material
    provenance: "C443"

  compatibility_statistics:
    illegal_pair_rate: "95.7%"
    legal_pair_rate: "4.3%"
    illegal_pairs_count: 673342
    legal_pairs_count: 30394
    provenance: "C475"

  morphological_affinity:
    ac_enriched_prefixes: ["qo- (91%)", "ol- (81%)"]
    zodiac_enriched_prefixes: ["ot- (54%)"]
    broadly_distributed: ["ch-", "sh-", "ok-"]
    provenance: "C471"

  middle_exclusivity:
    exclusive_rate: "77%"
    exclusive_entropy: "median = 0.0"
    shared_coverage: "18.7% vs 3.3%"
    folio_exclusive_rate: "73.5%"
    provenance: "C472, C469"

  persistence_statistics:
    a_vocab_placement_ratio: "2.2x more than AZC-only"
    high_multiplicity_coverage: "43% broader"
    restriction_inheritance_ratio: "12.7x difference preserved"
    provenance: "C343, C470"

# ============================================================
# PROVENANCE MAP
# ============================================================
provenance:
  vocabulary_activation:
    - "C441"  # Vocabulary-activated positional encoding
    - "C442"  # Compatibility grouping

  positional_legality:
    - "C306"  # Placement-coding axis
    - "C313"  # Position constrains LEGALITY not PREDICTION
    - "C443"  # Positional escape gradient
    - "C444"  # A-type position distribution

  pipeline_causality:
    - "C468"  # Legality inheritance
    - "C469"  # Categorical resolution principle
    - "C470"  # MIDDLE restriction inheritance

  morphological_binding:
    - "C471"  # PREFIX encodes AZC family affinity
    - "C472"  # MIDDLE is primary carrier of folio specificity
    - "C473"  # A entry defines constraint bundle

  middle_incompatibility:
    - "C475"  # MIDDLE atomic incompatibility

  persistence:
    - "C343"  # A-AZC persistence independence

  ordered_subscript_family:
    - "C432"  # Ordered subscript exclusivity
    - "C434"  # R-series strict forward ordering
    - "C435"  # S/R positional division

  invariants:
    - "C384"  # No entry-level A-B coupling
    - "C443"  # Monotonicity source
    - "C444"  # Position independence

# ============================================================
# END OF AZC-ACT
# ============================================================

```

---

# AZC->B Propagation Contract

**Source:** `context/STRUCTURAL_CONTRACTS/azc_b_activation.act.yaml`

```yaml
# ============================================================
# AZC-B-ACT: AZC-B Activation Contract
# Version: 1.0
# ============================================================
#
# This is a DERIVED, READ-ONLY specification.
# It introduces NO NEW CLAIMS.
# Constraints remain authoritative.
# Do not edit without constraint update.
#
# Purpose: Thin, directional layer specifying how AZC legality
# states propagate into Currier B execution without altering
# B grammar.
#
# This is NOT a Currier B structural contract. It is an
# AZC-output-facing interface contract describing the
# AZC->B boundary only.
#
# ============================================================

meta:
  name: "AZC-B Activation Contract"
  acronym: "AZC-B-ACT"
  version: "1.1"
  date: "2026-01-29"
  status: "LOCKED"
  layer_type: "propagation contract"
  derived_from: "Tier-2 constraints only"
  audit_note: "Reviewed against constraints through C872. No changes needed - new constraints are internal A/B structure, not pipeline boundaries."
  governance: |
    AZC-B-ACT is NOT authoritative. Constraints are authoritative.
    AZC-B-ACT describes HOW AZC legality states propagate into B.
    Do not edit without updating source constraints first.

# ============================================================
# SCOPE & GUARANTEES
# ============================================================
scope:
  function: "How AZC legality states constrain Currier B execution"
  direction: "AZC -> B (one-way propagation, not reverse)"
  b_grammar_authority: false  # Does not modify B grammar
  a_visibility: false  # B does not see A entries
  azc_visibility: false  # B does not see AZC internal structure

# Explicit ownership declaration (prevents misreading)
ownership:
  azc_b_act_owns:
    - nothing
  azc_b_act_describes:
    - legality_propagation
    - intervention_permission_envelope
    - vocabulary_restriction_inheritance
  note: "Propagation contract, not grammar definition"

# What B receives (effects, not signals)
b_reception:
  receives:
    - description: "Grammar paths silently constrained by legality"
      mechanism: "Illegal tokens/transitions are absent, not marked"
      note: "Legality is ambient constraint, not state variable"
    - description: "Intervention permission envelope"
      mechanism: "Categorical permission, not quantitative resource"
    - description: "Vocabulary restriction inheritance"
      mechanism: "MIDDLE restrictions transfer intact"
  does_not_receive:
    - "Currier A entry identity"
    - "AZC internal structure"
    - "Why tokens are legal/illegal"
    - "Compatibility graph mechanics"
    - "Positional semantics (C, P, R, S zones)"
  note: "B executes blindly against the legality field"

guarantees:
  - id: "LEGALITY_INHERITANCE"
    statement: "AZC escape/constraint profiles propagate causally into B"
    mechanism: "High-escape AZC contexts yield higher B escape incidence"
    provenance: "C468"

  - id: "RESTRICTION_PRESERVATION"
    statement: "MIDDLE restrictions transfer intact to B"
    mechanism: "AZC-restricted vocabulary remains restricted in B"
    provenance: "C470"

  - id: "GRAMMAR_INDEPENDENCE"
    statement: "B grammar is unchanged by AZC legality"
    mechanism: "All 49 classes, all transitions, all hazards apply regardless"
    provenance: "C121, C124"

  - id: "BLIND_EXECUTION"
    statement: "B executes without knowledge of upstream mechanics"
    mechanism: "Vocabulary -> legality -> B; no reverse inference"
    provenance: "C384, C468"

  - id: "CATEGORICAL_RESOLUTION"
    statement: "Resolution via vocabulary availability, not parameters"
    mechanism: "Fine distinctions encoded in which tokens are legal"
    provenance: "C469"

# ============================================================
# INVARIANTS (structural guarantees for tooling/testing)
# ============================================================
invariants:
  causal_transfer:
    statement: "AZC legality causally determines B intervention dynamics"
    description: "High-escape AZC contexts produce elevated B escape rates"
    provenance: "C468"

  restriction_inheritance:
    statement: "Vocabulary restrictions survive pipeline transfer"
    description: "MIDDLE-level folio restrictions propagate into B"
    provenance: "C470"

  grammar_stability:
    statement: "B grammar rules apply universally regardless of AZC source"
    description: "100% coverage, 0 folio exceptions"
    provenance: "C124"

  non_parametric:
    statement: "No numeric values are transmitted through the pipeline"
    description: "All distinctions are categorical (present/absent)"
    provenance: "C469"

  no_token_transmission:
    statement: "No tokens are transmitted from Currier A to Currier B"
    description: "Constraint inheritance modifies which token types are present for B execution; no token identity crosses system boundaries"
    note: "A and B instantiate the same global type space under different structural roles; shared tokens ≠ shared reference"
    provenance: "C384, C281, C285, C343"

# ============================================================
# INPUTS (what AZC exports)
# ============================================================
inputs:
  from_azc:
    type: "legality_effect"
    components:
      - escape_permission: "Position-indexed intervention permission envelope"
      - folio_restriction: "MIDDLE-level compatibility constraints"
    note: "Effects, not signals; ambient constraints, not state variables"
    provenance: "C443, C468, C470"

  not_exported:
    - "AZC position labels (C, P, R, S)"
    - "Folio identity"
    - "Family membership (Zodiac vs A/C)"
    - "Compatibility graph structure"
    - "Escape rate thresholds or numeric values"
    note: "B receives effects, not structure"

# ============================================================
# PROPAGATION MECHANICS
# ============================================================
propagation:
  description: "How AZC legality transforms into B constraints"

  escape_permission_transfer:
    mechanism: "AZC escape permission envelope -> B intervention availability"
    direction: "Higher AZC escape permission yields higher B escape incidence"
    categorical: true
    parametric: false
    provenance: "C468"

  vocabulary_restriction_transfer:
    mechanism: "AZC MIDDLE restrictions -> B folio spread constraints"
    direction: "Restricted MIDDLEs remain restricted in B"
    categorical: true
    parametric: false
    provenance: "C470"

  categorical_resolution:
    mechanism: "Resolution via vocabulary availability, not parameters"
    effect: "Fine distinctions encoded in which tokens are legal"
    note: "No numeric values cross the boundary"
    provenance: "C469"

  vanishing_semantics:
    statement: "Illegality manifests as absence, not marking"
    description: "Illegal tokens/transitions simply do not appear in B"
    mechanism: "Grammar paths are silently constrained"
    provenance: "C444, C468"

  vocabulary_scope:
    statement: "B vocabulary is restricted to A-record MIDDLEs only"
    mechanism: "Tokens with MIDDLEs not in the A record are illegal (vanish)"
    expansion: false  # AZC does NOT expand vocabulary beyond A specification
    filtering_magnitude: "~80% of B vocabulary filtered per A context"
    effect: "Different A records make different B folios viable"
    note: "Viability is emergent from vocabulary restriction, not intentional selection"
    provenance: "C481, C502"

# ============================================================
# B RECEPTION ARCHITECTURE (what receives AZC output)
# ============================================================
b_reception_architecture:
  description: "How B uses the propagated legality constraints"
  note: "Documents affected B aspects, not B internal structure"

  escape_routes:
    primary: "qo-prefix tokens"
    role_stratification:
      primary: "ENERGY_OPERATOR"
      secondary: "CORE_CONTROL"
    provenance: "C397, C398"

  stability_anchor:
    mechanism: "e-class tokens anchor to stable state"
    provenance: "C105"

  design_constraints:
    hazard_exposure: "CLAMPED"
    intervention_operations: "FREE"
    principle: "Constrain dangerous interactions; let intervention vary"
    provenance: "C458"

# ============================================================
# WHAT B DOES NOT RECEIVE
# ============================================================
b_isolation:
  description: "What is explicitly NOT propagated to B"

  blocked:
    - item: "A entry identity"
      reason: "C384 - no entry-level coupling"
    - item: "AZC position structure"
      reason: "B receives effects, not positions"
    - item: "AZC folio semantics"
      reason: "Folio identity does not propagate"
    - item: "Compatibility graph"
      reason: "B sees legal/illegal as absence/presence, not why"
    - item: "MIDDLE incompatibility details"
      reason: "Filtering happens upstream"
    - item: "Numeric thresholds or ratios"
      reason: "C469 - categorical resolution only"

  note: |
    B grammar is SELF-CONTAINED.
    AZC provides only: which tokens are legal (by absence/presence).
    B applies its own 49-class grammar regardless.

# ============================================================
# NEGATIVE GUARANTEES
# ============================================================
negative_guarantees:
  - guarantee: "No A entry visibility in B"
    reason: "C384 - vocabulary-mediated only"

  - guarantee: "No AZC structure visibility in B"
    reason: "Propagation is effects-only"

  - guarantee: "No B grammar modification by AZC"
    reason: "C121, C124 - grammar is universal"

  - guarantee: "No reverse inference from B to AZC"
    reason: "Pipeline is unidirectional"

  - guarantee: "No parametric encoding"
    reason: "C469 - categorical resolution only"

  - guarantee: "No numeric values transmitted"
    reason: "All distinctions are categorical"

# ============================================================
# EXPLICITLY DEFERRED
# ============================================================
deferred:
  - topic: "B internal grammar structure"
    reason: "Belongs to BCSC, not this activation contract"

  - topic: "49-class taxonomy details"
    reason: "B internal structure"

  - topic: "Hazard topology details"
    reason: "B internal structure"

  - topic: "LINK operator semantics"
    reason: "B internal structure"

  - topic: "Folio program taxonomy"
    reason: "B internal structure"

  - topic: "STATE-C / STATE-X semantics"
    reason: "B internal structure"

  - topic: "Procedure identity"
    reason: "B internal structure / Tier-3"

  - topic: "Process domain interpretation"
    reason: "Tier-3 speculative layer"

# ============================================================
# DISALLOWED INTERPRETATIONS
# ============================================================
disallowed:
  - interpretation: "B sees A entries"
    reason: "Vocabulary-mediated only (C384)"
    provenance: "C384"

  - interpretation: "B can infer AZC position"
    reason: "Effects propagate, not structure"
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

# ============================================================
# NON-NORMATIVE ANNOTATIONS
# ============================================================
# Empirical observations for reference. These are NOT contractual
# guarantees and may vary with filtering or dataset changes.

annotations:
  note: "These are empirical observations, NOT structural guarantees"
  status: "NON-NORMATIVE"

  escape_statistics:
    high_context_b_escape: "28.6%"
    low_context_b_escape: "1.0%"
    ratio: "28x"
    azc_threshold_used: ">=5% vs <5%"
    note: "Thresholds are observational, not definitional"
    provenance: "C468"

  restriction_statistics:
    restricted_middle_spread: "4.0 folios mean"
    universal_middle_spread: "50.6 folios mean"
    ratio: "12.7x"
    note: "Spread difference preserved through pipeline"
    provenance: "C470"

  recovery_statistics:
    qo_escape_rate: "25-47%"
    e_recovery_path_rate: "54.7%"
    energy_operator_escape: "40-67%"
    core_control_escape: "22-32%"
    provenance: "C397, C398, C105"

  design_clamp_statistics:
    hazard_cv: "0.04-0.11"
    recovery_cv: "0.72-0.82"
    provenance: "C458"

# ============================================================
# PROVENANCE MAP
# ============================================================
provenance:
  pipeline_causality:
    - "C468"  # Legality inheritance
    - "C469"  # Categorical resolution
    - "C470"  # MIDDLE restriction inheritance

  b_reception:
    - "C105"  # e = STABILITY_ANCHOR
    - "C397"  # qo-prefix escape route
    - "C398"  # Escape role stratification
    - "C399"  # Safe precedence pattern
    - "C458"  # Execution design clamp

  boundary_preservation:
    - "C384"  # No entry-level A-B coupling
    - "C121"  # 49 instruction classes
    - "C124"  # 100% grammar coverage

  vanishing_semantics:
    - "C444"  # Position independence (vanishing = illegality)

  invariants:
    - "C443"  # Escape gradient source
    - "C468"  # Causal transfer
    - "C470"  # Restriction preservation
    - "C469"  # Non-parametric

# ============================================================
# END OF AZC-B-ACT
# ============================================================

```

---
