# Voynich Manuscript Analysis - Context Index

**Version:** 3.77 | **Status:** FROZEN | **Constraints:** 892 | **Date:** 2026-02-14

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
| **Glossing rules and vocabulary** | [GLOSSING.md](GLOSSING.md) (read before ANY gloss work) |
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
| Validated constraints | 892 |
| Completed phases | 350 |
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

*Context System v3.77 | Project v3.77 FROZEN STATE | ANALYSIS CLOSED | PCA-v1 CERTIFIED | 2026-02-14*
