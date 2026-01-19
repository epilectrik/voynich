# Voynich Expert Context

**Generated:** 2026-01-18 11:12
**Version:** FROZEN STATE (356 constraints, 35 fits)

This document combines all expert reference materials for the Voynich Manuscript
Currier B analysis project. It provides complete context for validating claims,
reviewing proposals, and answering architectural questions.

## How to Use This Document

1. **For constraint validation:** Search for "C###" to find specific constraints
2. **For fit references:** Search for "F-XXX-###" patterns
3. **For architectural questions:** See "Architectural Framework" section
4. **For speculative interpretations:** See "Tier 3-4 Interpretations" section

---

## Table of Contents

1. Project Overview & Navigation
2. Architectural Framework
3. All 356 Constraints
4. All 35 Explanatory Fits
5. Tier 3-4 Interpretations
6. Currier A Structure Contract
7. Currier B Grammar Contract
8. A->AZC Activation Contract
9. AZC->B Propagation Contract

---

# Project Overview & Navigation

**Source:** `context/CLAUDE_INDEX.md`

# Voynich Manuscript Analysis - Context Index

**Version:** 2.55 | **Status:** FROZEN | **Constraints:** 356 | **Date:** 2026-01-17

> **STRUCTURE_FREEZE_v1 ACTIVE** — Structural inspection layer is frozen. See [SYSTEM/CHANGELOG.md](SYSTEM/CHANGELOG.md) for post-freeze paths.
>
> **PIPELINE CLOSED** — A→AZC→B control architecture fully reconstructed and certified. PCA-v1 passed. Structural work is DONE.

---

## Project Identity (Tier 0)

The Voynich Manuscript's Currier B text (61.9% of tokens, 83 folios) encodes a family of **closed-loop, kernel-centric control programs** designed to maintain a system within a narrow viability regime, governed by a single shared grammar.

This is not language. This is not cipher. This is a control system reference manual.

| Metric | Value |
|--------|-------|
| Instruction classes | 49 (9.8x compression from 479 token types) |
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

Within the internal structural analysis, Voynich tokens function differently than words in natural language. Understanding this prevents a common misinterpretation.

**Key principles:**

1. **Tokens are surface realizations, not functional operators.** At the level of grammar reconstruction, the functional behavior of a token is determined by its *instruction class*, not by the token itself. The 479 distinct token types collapse to 49 instruction classes (9.8x compression).

2. **Most tokens are interchangeable within their class.** Just as assembly language mnemonics (MOV, ADD, JMP) map to opcodes, Voynich tokens map to instruction classes. The specific token is often a surface variant; the class determines behavior.

3. **High hapax rates are expected, not anomalous.** Compositional morphology (PREFIX + MIDDLE + SUFFIX) generates unique surface forms naturally. A 35-39% hapax rate follows directly from productive combination, not from vocabulary size or "unknown" content.

4. **A token lacking special highlighting is NOT unknown.** Every token has a structural classification (instruction class, morphological decomposition, system legality). "Neutral" means "non-contrastive"—the token does not carry *additional* discriminative signal beyond its base class. It does not mean the token is unanalyzed.

**Analogy:** Consider a programming language where `foo`, `bar`, and `qux` are all valid variable names. They are structurally equivalent (all identifiers), interchangeable in most contexts, and individually unremarkable. Their *function* is determined by their syntactic role, not their spelling. Voynich tokens work similarly at the structural level.

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
- LINK operator (38% of text = deliberate waiting)
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
| Validated constraints | 356 |
| Completed phases | 138 |
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

*Context System v2.49 | Project v1.8 FROZEN STATE | PIPELINE CLOSED | PCA-v1 CERTIFIED | 2026-01-16*


---

# Architectural Framework

**Source:** `context/MODEL_CONTEXT.md`

# MODEL_CONTEXT.md

**Version:** 3.6 | **Date:** 2026-01-18 | **Status:** FROZEN

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
- Entry-level A-B correspondence claims
- Reintroduction of language/cipher hypotheses

---

## IV. SYSTEM ARCHITECTURE OVERVIEW

The Voynich Manuscript contains four coexisting systems sharing a morphological type space but operating under different structural regimes:

| System | Mode | Function | Executes? | Grammar? |
|--------|------|----------|-----------|----------|
| Currier B | Sequential | Closed-loop control programs | Yes | 49-class |
| Currier A | Non-sequential | Complexity-frontier registry | No | None |
| AZC | Placement-coded | Context-gated workflow | Hybrid | Positional |
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
| **AZC** | Gates you | Phase-indexed decision legality, compatibility filtering |
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

### MIDDLE Function

MIDDLEs are the primary vocabulary layer:
- **1,186 distinct MIDDLEs globally** (A ∪ B union)
- Currier A: 617 unique MIDDLEs
- Currier B: 837 unique MIDDLEs
- Shared (A ∩ B): 268 MIDDLEs (Jaccard = 0.226)
- A-exclusive: 349 (56.6% of A's MIDDLEs never appear in B)
- B-exclusive: 569 (68.0% of B's MIDDLEs never appear in A)

**Tier 2 Interpretation:**
> Currier A enumerates the *potential discrimination space*;
> Currier B traverses only a *submanifold* of that space under specific execution contracts.

**Three-Way MIDDLE Stratification:**

| Class | Role |
|-------|------|
| **A-exclusive** (349) | Pure discrimination coordinates - discriminations that exist in principle but are never jointly instantiated with surviving B procedures |
| **A/B-shared** (268) | Execution-safe compatibility substrate - the ~95% of B usage that makes execution possible everywhere |
| **B-exclusive** (569) | Boundary-condition discriminators - stabilize line transitions, encode edge-case variation; NOT grammar operators |
| **L-compounds** (subset) | True grammar operators (C298) - rare, B-specific, NOT representative of B-exclusive class |

> B-exclusive MIDDLEs predominantly function as boundary-condition discriminators and orthographic variants, not as execution grammar operators. (B-EXCL-ROLE phase, 2026-01-16)

**Within-System Distribution:**
- 80% are prefix-exclusive (domain-specific within each system)
- 20% are shared across prefixes
- 27 universal MIDDLEs appear in 6+ prefix classes

**Frequency Distribution (Tier 3):**
- Core (top 30): 67.6% of usage, mode-flexible, section-stable
- Tail (~1,150): 32.4% of usage, mode-specific, hazard-concentrated
- Rare MIDDLEs cluster in high-hazard contexts (rho=-0.339, p=0.0001)

### SUFFIX Function

Suffixes encode universal form markers:
- 22/25 significant suffixes appear across 6+ prefix classes
- Suffix selection is compositionally conditioned
- Suffixes do not carry semantic content

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

### Execution Infrastructure Roles (Characterized, Non-Primitive)

**Status:** Tier 3 structural characterization. Derivable from Tier 2 constraints (C124, C485, C411). Not a new mechanism.

Some Currier B instruction roles are **execution-critical infrastructure**: they are required for nearly all executable programs to exist but are not grammar primitives or hazard anchors.

**Position in Architecture:**
- Below kernel primitives (k, h, e)
- Above decomposable instruction classes
- Outside AZC vocabulary gating scope

**Key Properties (BCI Characterization, 2026-01-18):**

| Property | Evidence |
|----------|----------|
| Near-universal B coverage | 96-100% of B folios require these roles |
| Kernel-mediating | 70.6% cluster within 0-2 tokens of k/h/e operators |
| Partial REGIME sensitivity | One role fully invariant; others show 6-14% spread |
| Zone-sensitive | All thin sharply in S-zone (43% → 19% legal) |
| Redundant | Threshold behavior at 50% availability; mutual substitutability |

**What These Roles Are NOT:**
- Kernel primitives (not atomic, not forbidden-transition adjacent)
- Semantic carriers (no material, procedure, or substance encoding)
- Neutral vocabulary (they actively mediate control flow)

**Interpretive Bound:**
> These roles implement structural mediation between control primitives and contextual grammar. They do not encode semantics, materials, or procedures.

**Reference:** See [TIER3/b_execution_infrastructure_characterization.md](TIER3/b_execution_infrastructure_characterization.md) for full BCI test results.

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

## VIII. AZC - DECISION-POINT GRAMMAR & COMPATIBILITY FILTER

AZC (3,299 tokens, 8.7% of corpus, 30 folios) is neither Currier A nor Currier B. It operates as a **decision-point grammar** that converts static A-registry entries into phase-gated choice nodes.

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
| Compatibility filter | 94% unique vocabulary | C442 |

### Positional Grammar

Position on the page constrains legality (C→P→R→S progression):

| Position | Workflow Phase | Escape Rate | Meaning |
|----------|----------------|-------------|---------|
| C | Setup/Loading | 1.4% | Entry constrained, errors fixable |
| P | Active work | 11.6% | Recovery permitted, intervention legal |
| R1→R2→R3 | Progression | 2.0%→1.2%→0% | Options narrowing, committing |
| S | Collection/Exit | 0-3.8% | Locked, must accept outcome |

### Compatibility Filter Mechanism

AZC folios function as **compatibility filters**:
- Specialized A-types appear in only 1-3 folios
- Using vocabulary from one folio excludes vocabulary from others
- Incompatible A-registry entries CANNOT be combined
- The grammar blocks dangerous combinations at specification level

**Why AZC is large:** It enumerates all compatibility classes. Each folio = a different set of legal combinations.

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

### A-B Relationship

- **Statistical and global only** - vocabulary overlap exists at population level
- **No addressable mapping** - no A entry "refers to" any B program
- **Complexity alignment** - shared vocabulary reflects shared operational domain
- **NOT risk encoding** - correlation with hazard is spurious (frequency-driven)

The correct model:
> Currier B provides sequences (how to act).
> Currier A provides discrimination (where fine distinctions matter).

### A-AZC Relationship (v3.0)

AZC converts static A-registry entries into **phase-gated decision points**:

- **Vocabulary-activated constraints** (C441): Using an A-type activates its associated AZC constraint profile
- **Compatibility filtering** (C442): AZC folios block incompatible A-type combinations
- **Position-indexed escape** (C443): Same A-type has different intervention legality depending on AZC position
- **Universal distribution** (C444): No A-type is locked to specific positions - position determines legality, not content

The correct model:
> Currier A provides the vocabulary of possibilities.
> AZC converts each possibility into a phase-gated decision with location-dependent legality.
> No explicit selection - constraints activate ambientally based on vocabulary used.

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
TOKEN = PREFIX   → control-flow participation (how token engages control)
      + SISTER   → operational mode (precision/tolerance)
      + MIDDLE   → variant discriminator (compatibility carrier)
      + SUFFIX   → decision archetype (phase-indexed)
```

### Component Mappings (Tier 3)

| Component | Encodes | Evidence |
|-----------|---------|----------|
| **PREFIX** | Control-flow participation (intervention/core/anchor) | C466-C467, F-A-014b |
| **SISTER** | Operational mode | C412 anticorrelation (rho=-0.326) |
| **MIDDLE** | Compatibility carrier | C441-C442, 80% prefix-exclusive |
| **SUFFIX** | Phase-indexed decision archetype | F-AZC-014 (74% P-position for -ain) |

### The Unifying Perspective

> The manuscript encodes the operational worldview of a controlled apparatus, not the descriptive worldview of a human observer.

From the apparatus's perspective:
- PREFIX encodes **how tokens participate in control** at complexity peaks
- MIDDLE encodes **what must not be confused** (compatibility)
- SUFFIX encodes **when decisions are allowed** (phase)
- SISTER encodes **how tightly to execute** (mode)

### Semantic Ceiling

**Recoverable (role-level):**
- 3 control-flow roles (PREFIX): intervention, core, anchor
- 2 operational modes (SISTER): precision, tolerance
- ~1,000 variant discriminators (MIDDLE): compatibility carriers
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
| Entry-level A-B correspondence | FALSIFIED | C384, no coupling |

**Do not resurrect these hypotheses** without extraordinary new evidence and explicit model reopening.

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
| BCSC | `currierB.bcsc.yaml` | LOCKED v1.0 | Currier B internal grammar |

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

# All 356 Constraints

**Source:** `context/CONSTRAINT_TABLE.txt`

CONSTRAINT_REFERENCE v2.6 | 356 constraints | 2026-01-17
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
C130	DSL hypothesis rejected (0.19% reference rate)	1	B	in: falsified
C131	Role consistency LOW (23.8%)	2	B	in: grammar_system
C132	Language encoding CLOSED	1	B	in: falsified
C137	Swap invariance confirmed (p=1.0)	1	B	in: falsified
C138	Illustrations do not constrain execution	1	B	in: falsified
C139	Grammar recovered from text-only	2	B	in: grammar_system
C140	Illustrations are epiphenomenal	1	B	in: falsified
C141	Cross-family transplant = ZERO degradation	2	B	in: grammar_system
C144	Families are emergent regularities	2	B	in: grammar_system
C153	Prefix/suffix axes partially independent (MI=0.075)	2	B	in: organization
C154	Extreme local continuity (d=17.5)	2	B	in: organization
C155	Piecewise-sequential geometry (PC1 rho=-0.624)	2	B	in: organization
C156	Detected sections match codicology (4.3x quire alignment)	2	B	in: organization
C157	Circulatory reflux uniquely compatible (100%)	3	B	in: speculative
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
C199	Both mineral AND botanical survive	3	B	in: speculative
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
C215	BOTANICAL_FAVORED (8/8 tests, ratio 2.37)	3	B	in: speculative
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
C384	NO ENTRY-LEVEL A-B COUPLING	2	A↔B	-> C384_no_entry_coupling.md
C385	STRUCTURAL GRADIENT in Currier A	2	A	in: currier_a
C386	Transition Suppression	2	GLOBAL	in: morphology
C387	QO as Phase-Transition Hub	2	GLOBAL	in: morphology
C388	Self-Transition Enrichment	2	GLOBAL	in: morphology
C389	BIGRAM-DOMINANT local determinism (H=0.41 bits)	2	GLOBAL	in: grammar_system
C390	No Recurring N-Grams	2	GLOBAL	in: morphology
C391	TIME-REVERSAL SYMMETRY	2	GLOBAL	in: grammar_system
C392	ROLE-LEVEL CAPACITY (97.2% observed)	2	GLOBAL	in: grammar_system
C393	FLAT TOPOLOGY (diameter=1)	2	GLOBAL	in: grammar_system
C394	INTENSITY-ROLE DIFFERENTIATION	2	GLOBAL	in: operations
C395	DUAL CONTROL STRATEGY	2	GLOBAL	in: operations
C396	AUXILIARY Invariance	2	GLOBAL	in: morphology
C397	qo-prefix = escape route (25-47%)	2	GLOBAL	in: grammar_system
C398	Escape Role Stratification	2	GLOBAL	in: morphology
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
C442	AZC Compatibility Filter	2	AZC	in: azc_system
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

---

# All 35 Explanatory Fits

**Source:** `context/MODEL_FITS/FIT_TABLE.txt`

# FIT_TABLE.txt - Programmatic Fit Index
# WARNING: No entry in this file constrains the model.
# Generated: 2026-01-17
# Total: 35 fits
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
F-BRU-001	Brunschwig Product Type Prediction (Blind)	F3	A	PARTIAL	C475, C476	in: fits_brunschwig
F-BRU-002	Degree-REGIME Boundary Asymmetry	F3	B	SUCCESS	C179-C185, C458	in: fits_brunschwig
F-BRU-003	Property-Based Generator Rejection	F2	A	NEGATIVE	C475, C476	in: fits_brunschwig
F-BRU-004	A-Register Cluster Stability	F2	A	SUCCESS	C481	in: fits_brunschwig
F-BRU-005	MIDDLE Hierarchical Structure	F2	A	SUCCESS	C383, C475	in: fits_brunschwig
F-BRU-006	Closure × Product Affordance Correlation	F3	A	SUCCESS	C233, C422 (closure/DA structure)	in: fits_brunschwig

---

# Tier 3-4 Interpretations

**Source:** `context/SPECULATIVE/INTERPRETATION_SUMMARY.md`

# Speculative Interpretation Summary

**Status:** SPECULATIVE | **Tier:** 3-4 | **Version:** 4.27

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
TOKEN = PREFIX   → material-behavior class (what kind of thing)
      + SISTER   → operational mode (how carefully)
      + MIDDLE   → variant discriminator (which specific variant)
      + SUFFIX   → decision archetype (what decision is needed)
```

### Component-to-Class Mapping

| Component | Encodes | Classes | Evidence |
|-----------|---------|---------|----------|
| **PREFIX** | Material-behavior | 4 classes (M-A/B/C/D) | Grammar roles, enrichment |
| **SISTER** | Operational mode | 2 modes (precision/tolerance) | C412 anticorrelation |
| **MIDDLE** | Variant identity | ~1,184 discriminators | 80% prefix-exclusive |
| **SUFFIX** | Decision archetype | 12 archetypes (D1-D12) | A/B enrichment patterns |

### Material-Behavior Classes

| Class | Phase | Composition | Prefixes | Example Role |
|-------|-------|-------------|----------|--------------|
| **M-A** | Mobile | Distinct | ch, sh, qo | Energy operations |
| **M-B** | Mobile | Homogeneous | ok, ot | Routine operations |
| **M-C** | Stable | Distinct | ct | Registry reference |
| **M-D** | Stable | Homogeneous | ol, da | Structural anchor |

### Operational Modes (Sister Pairs)

| Sister | Mode | Escape Density | Meaning |
|--------|------|----------------|---------|
| **ch** (vs sh) | Precision | 7.1% | Tight tolerances, fewer recovery options |
| **sh** (vs ch) | Tolerance | 24.7% | Loose tolerances, more escape routes |

Statistical validation: rho = -0.326, p = 0.002 (C412)

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

## I.B. Four-Layer Responsibility Model (v2.13)

### Tier 2: Structural Finding

The manuscript distributes responsibility between system and human across four layers:

| Layer | Role | What It Handles |
|-------|------|-----------------|
| **Currier B** | Constrains you | Execution grammar, safety envelope |
| **Currier A** | Discriminates for you | Fine distinctions at complexity frontier |
| **AZC** | Gates you | Phase-indexed decision legality, compatibility filtering |
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

AZC serves as a **decision-point grammar** that transforms static A-registry entries into phase-gated choice nodes:

| Finding | Evidence | Constraint |
|---------|----------|------------|
| Folios maximally orthogonal | Jaccard = 0.056 | C437 |
| Practically complete basis | 83% per-folio coverage | C438 |
| Folio-specific HT profiles | 18pp escape variance | C439 |
| Uniform B sourcing | 34-36 folios per B | C440 |
| Vocabulary-activated constraints | 49% A-types in 1 folio | C441 |
| Compatibility filter | 94% unique vocabulary | C442 |

### Tier 3: Operational Interpretation

**Core insight:** AZC converts static Currier A entries into phase-gated decision points.

| System | Function | Type |
|--------|----------|------|
| Currier A | WHAT exists | Static registry |
| Currier B | HOW to proceed | Procedural sequence |
| AZC | WHEN to decide | Decision grammar |

### Phase-to-Workflow Mapping

AZC positional grammar maps to operational workflow:

| Position | Workflow Phase | Escape Rate | Meaning |
|----------|----------------|-------------|---------|
| C | Setup/Loading | 1.4% | Entry constrained, errors fixable |
| P | Active work | 11.6% | Recovery permitted, intervention legal |
| R1→R2→R3 | Progression | 2.0%→1.2%→0% | Options narrowing, committing |
| S | Collection/Exit | 0-3.8% | Locked, must accept outcome |

In reflux distillation: early phases are reversible, late phases are committed. AZC encodes this grammatically.

### Compatibility Filter Mechanism (v4.5 - REFINED)

AZC compatibility operates at the **Currier A constraint-bundle level**, not at execution level.

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
- **Position (C→P→R→S)** → determines phase-specific rules

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

7/12 patterns show STRONG alignment.

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

### Fully Answered (v4.0)

| Question | Status | Finding |
|----------|--------|---------|
| Why are some programs forgiving and others brittle? | PARTIALLY ANSWERED | Recovery varies freely (CV=0.82), hazard is clamped (CV=0.11) - C458 |
| What does HT signal? | ANSWERED | Anticipatory vigilance, content-driven - C459 |
| What role does AZC play in the manuscript? | **FULLY ANSWERED** | Decision-point grammar, compatibility filter, phase-indexed escape gating - C437-C444 |
| Why are there so many AZC folios? | **FULLY ANSWERED** | Enumerates all compatibility classes; each folio = distinct legal combination space - C437, C442 |
| How does AZC relate to A and B? | **FULLY ANSWERED** | AZC converts static A entries into phase-gated decision points within B procedures - F-AZC-011/012/013 |

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
- Specific folio = specific recipe
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
  version: "1.0"
  date: "2026-01-13"
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
    provenance: "C293, C423, C475"

  suffix:
    count: 25
    universal_rate: "22/25 appear in 6+ prefix classes"
    function: "Decision archetype (phase-indexed)"
    provenance: "C269, C277"

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
    entry_level_coupling: false
    vocabulary_sharing: "statistical (shared domain)"
    mapping_type: "not addressable"
    section_distribution:
      H_in_B: "91.6% (76/83 folios)"
      P_in_B: "8.4% (7/83 folios)"
      T_in_B: "0% (0/83 folios)"
    provenance: "C299, C384"

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
  - interpretation: "A entries map to B programs"
    reason: "No entry-level coupling exists"
    evidence: "C384 - no addressable correspondence"
    status: "FALSIFIED"

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

  participation:
    - "C299"  # Section distribution in B
    - "C384"  # No A-B coupling
    - "C441"  # AZC vocabulary-activated
    - "C442"  # AZC compatibility filter
    - "C484"  # Control operator exclusion

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
# Version: 1.0
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
  version: "1.0"
  date: "2026-01-13"
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
    statement: "17 forbidden transitions in 5 classes are absolute"
    provenance: "C109"

  - id: "KERNEL_CENTRALITY"
    statement: "k, h, e form irreducible control core, boundary-adjacent to hazards"
    provenance: "C089, C107"

  - id: "LINE_FORMALITY"
    statement: "Lines are formal control blocks, not scribal wrapping"
    provenance: "C357-C360"

  - id: "LINK_PHASE_MARKER"
    statement: "LINK marks boundary between monitoring and intervention"
    provenance: "C366"

  - id: "DESIGN_ASYMMETRY"
    statement: "Hazard exposure clamped; recovery architecture free"
    provenance: "C458"

  - id: "TIME_REVERSAL_SYMMETRIC"
    statement: "Grammar is invariant under time reversal"
    provenance: "C391"

  - id: "CLOSED_LOOP_ONLY"
    statement: "Execution is closed-loop control, not batch, decision tree, or state machine"
    provenance: "C171"

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

  time_reversal:
    statement: "Grammar is symmetric under time reversal"
    description: "No privileged directionality at grammar level"
    provenance: "C391"

  kernel_boundary_adjacency:
    statement: "All kernel nodes are boundary-adjacent to forbidden transitions"
    description: "Kernel controls hazard proximity"
    provenance: "C107"

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
      provenance: "C121"

    ENERGY_OPERATOR:
      function: "Energy modulation"
      class_count: 11
      provenance: "C121"

    AUXILIARY:
      function: "Support operations"
      class_count: 8
      provenance: "C121"
      # BCI refinement (2026-01-18): AUXILIARY roles are execution-critical
      # infrastructure that mediate kernel access. They are redundant internally
      # (collapsible per C411) but must never be pruned by AZC vocabulary filtering.
      # See C396.a and TIER3/b_execution_infrastructure_characterization.md

    FREQUENT_OPERATOR:
      function: "Common instructions"
      class_count: 4
      provenance: "C121"

    HIGH_IMPACT:
      function: "Major interventions"
      class_count: 3
      provenance: "C121"

    FLOW_OPERATOR:
      function: "Flow control"
      class_count: 2
      provenance: "C121"

    LINK:
      function: "Monitoring/observation phase marker"
      provenance: "C366"

  note: |
    Role classes are abstract grammar categories.
    Morphological realization (PREFIX/MIDDLE/SUFFIX composition)
    is NOT part of BCSC. See global morphology contracts.

# ============================================================
# KERNEL STRUCTURE
# ============================================================
kernel:
  description: "Three operators form the irreducible control core"

  operators:
    k:
      role: "ENERGY_MODULATOR"
      function: "Adjusts energy input"
      provenance: "C103"

    h:
      role: "PHASE_MANAGER"
      function: "Manages phase transitions"
      provenance: "C104"

    e:
      role: "STABILITY_ANCHOR"
      function: "Maintains stable state"
      recovery_path_rate: "54.7%"
      provenance: "C105"

  properties:
    irreducible: true
    boundary_adjacent: true
    h_to_k_suppressed: true
    e_trigram_dominance: "97.2%"
    provenance: "C089, C107, C332, C333"

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
  description: "17 forbidden transitions in 5 failure classes"

  forbidden_transitions:
    count: 17
    provenance: "C109"

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
    function: "Complete, self-contained program"
    count: 83
    macro_chaining: false
    provenance: "C178"

  line:
    function: "Formal control block"
    regularity: "3.3x more regular than random"
    boundary_markers:
      initial: ["daiin", "saiin", "sain"]
      final: ["am", "oly", "dy"]
    link_suppressed_at_boundary: true
    grammar_line_invariant: true
    provenance: "C357, C358, C359, C360"

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

  properties:
    spatially_uniform: true
    position_marking: false
    provenance: "C365"

  grammar_transitions:
    preceded_by: ["AUXILIARY", "FLOW_OPERATOR"]
    followed_by: ["HIGH_IMPACT", "ENERGY_OPERATOR"]
    provenance: "C366"

  complementarity:
    with_escalation: true
    description: "LINK suppressed near escalation"
    provenance: "C340"

# ============================================================
# RECOVERY ARCHITECTURE
# ============================================================
recovery:
  description: "How programs recover from near-hazard states"

  escape_routes:
    primary_role: "ENERGY_OPERATOR"
    secondary_role: "CORE_CONTROL"
    provenance: "C397, C398"

  stability_anchor:
    operator: "e"
    function: "Anchors system to stable state"
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

  - guarantee: "No Human Track references"
    reason: "HT is separate layer"

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
    - "C365"   # LINK spatially uniform
    - "C366"   # LINK marks grammar state transitions

  convergence:
    - "C323"   # Terminal distribution
    - "C324"   # Section-dependent terminals
    - "C325"   # Completion gradient

  recovery:
    - "C397"   # qo-prefix escape route
    - "C398"   # Escape role stratification
    - "C399"   # Safe precedence pattern

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
  version: "1.0"
  date: "2026-01-13"
  status: "LOCKED"
  layer_type: "mapping contract"
  derived_from: "Tier-2 constraints only"
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
  azc_controls:
    - legality
    - compatibility
    - intervention_permission
  note: "AZC gates, it does not define content or workflow"

guarantees:
  - id: "VOCABULARY_ACTIVATED"
    statement: "AZC constraint activation is vocabulary-driven"
    provenance: "C441"

  - id: "COMPATIBILITY_FILTER"
    statement: "AZC folios function as compatibility filters"
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

    P:
      function: "Interior placement, intervention-permitting"
      escape_permission: "high"
      high_escape_subclass:
        id: "P2"
        description: "Empirical subclass with elevated escape rate"
        note: "Not a distinct symbolic position; an observed subpopulation"
        provenance: "C443"
      provenance: "C306, C443"

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
    Interior positions (P, R-series, C) permit intervention.
    Boundary positions (S-series) forbid intervention.
    Position determines legality, not prediction.

# ============================================================
# TRANSFORMATIONS
# ============================================================
# What happens when an A entry is placed in an AZC position

transformations:
  description: "Constraints applied to A entries under position"

  compatibility_filtering:
    mechanism: "MIDDLE atomic incompatibility"
    effect: "Specialized vocabulary from one folio cannot combine with another"
    provenance: "C442, C475"

  escape_permission_changes:
    mechanism: "Phase-indexed gradient"
    effect: "Same A-type has different intervention permission by position"
    provenance: "C443, C444"

  categorical_resolution:
    mechanism: "Token legality, not parametric encoding"
    effect: "Operational conditions represented categorically"
    provenance: "C469"

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
    statement: "Vanishing = illegality, not execution"
    description: "If an A entry is not permitted in a position, it simply doesn't appear"
    mechanism: "AZC is ambient legality field, not selective filter"
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
    reason: "AZC gates, does not route"

  - guarantee: "No selection"
    reason: "AZC defines legality, operator selects vocabulary"

  - guarantee: "No branching"
    reason: "No conditional paths in AZC structure"

  - guarantee: "No instruction creation"
    reason: "AZC constrains, B executes"

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
    P: "11.0% (shared)"
    note: "Frequencies are dataset-dependent"

  interior_rates:
    C: "77.6%"
    P: "75.8%"
    R_series: "89-95%"
    S_series: "95%+ at line edges"

  escape_rates:
    P_typical: "11.6%"
    P_high_subclass: "24.7%"
    R1: "2.0%"
    R2: "1.2%"
    R3: "0%"
    S_series: "0%"
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
    - "C441"  # Vocabulary-activated constraints
    - "C442"  # Compatibility filter

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
  version: "1.0"
  date: "2026-01-13"
  status: "LOCKED"
  layer_type: "propagation contract"
  derived_from: "Tier-2 constraints only"
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
