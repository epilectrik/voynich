# Voynich Manuscript Analysis - Context Index

**Version:** 7.36 | **Status:** characterization ACTIVE | **Constraints:** 1,897 live in the generated table (T0 2, T1 38, T2 1,687, T3 166, T4 4) | **Phases:** 772 | **Date:** 2026-09-30

*(Header previously read "Version 6.03 | FROZEN | 1907 constraints | 2026-03-29" — historical.)*

> **STATUS (2026-09-27):** Structure mapped; referents unrecovered; Tier 0's semantic character under adversarial test. The earlier "ANALYSIS CLOSED / Structural work is DONE" banner is WITHDRAWN: 34 of the 43 most-cited constraints were never re-audited under a modern null, several atom-level constraints are EVA-orthography artifacts, and no meaningful-cipher generator has been tested. Forward plan: [SYSTEM/STRATEGIC_REVIEW_2026-09-27.md](SYSTEM/STRATEGIC_REVIEW_2026-09-27.md). PCA-v1 certified internal contract consistency only. *(Update 2026-09-28: Tier 0 restated to its measured core (v7.24); the kernel claim C089 superseded by C2082 (PHASE_763, v7.25).)*

---

> **Project-state overview:** the current one-page status is [SYSTEM/STATUS_BRIEF.md](SYSTEM/STATUS_BRIEF.md) (v7.25). [PROJECT_SYNTHESIS.md](PROJECT_SYNTHESIS.md) is the historical synthesis of 2026-05-18 (v6.71, through PHASE_701); it predates the September 2026 review, and its sections resting on withdrawn constructs are bannered in place. This index was last fully rewritten on 2026-03-29 and has been aligned with the registry on 2026-09-28; where any passage below conflicts with STATUS_BRIEF or `CONSTRAINT_TABLE.txt`, those win.

---

## Project Identity (Tier 0)

**Tier 0 (restated 2026-09-28):** Currier B is written in a single, compact token grammar: 49 classes covering 69.5% of its tokens, organised by line with positional zones and word-boundary glyph coupling, and applied in folio units that share the grammar while carrying their own vocabulary. This structure is not reproduced by copy-and-modify generation or by the Naibbe cipher as published.

**Current status in one page:** [SYSTEM/STATUS_BRIEF.md](SYSTEM/STATUS_BRIEF.md) — read this before any other document; documents written before the September 2026 review may present withdrawn claims as structure.

**Working interpretation (Tier 3):** the grammar is read as procedural notation (a family of programs for a process); no current measurement distinguishes this from other constrained notations. The former reading ("closed-loop, kernel-centric control programs") lost its supports on re-check — kernel C089 superseded by C2082; closed-loop legs withdrawn (C171, Tier 3); see [CORE/frozen_conclusion.md](CORE/frozen_conclusion.md).

Not natural language written one token per word (C132, C2015, C2022); the cipher classes tested so far are excluded — token≈word codes, atom-level polyalphabetic ciphers, three published decipherments (C1976, C2017), Timm & Schinner copy-and-modify (C2077), and the Naibbe verbose homophonic cipher as published (PHASE_757, C2080). Plain syllable writing (one spelling per syllable) is excluded on unit inventory (C2085); syllables written with spelling variation, word-level codebooks, modified verbose ciphers and the Rugg grille remain untested (STATUS_BRIEF §4). The older Tier-3 phrase "a control-system reference manual" rests on the withdrawn control legs (C171, C120 demoted to Tier 3).

| Metric | Value |
|--------|-------|
| Instruction classes (B) | 49 (9.8x compression from 479 B token types; C121) |
| Grammar coverage | 100% of the grammar's own 480 types = 69.5% of B tokens (C124, C566; HT/UN defined by exclusion) |
| Folios enumerated | 83 (23,243 H-track Currier B tokens; the older "75,248 instructions" figure is a legacy count that appears to be pre-H-filter — see DATA/TRANSCRIPT_ARCHITECTURE.md) |
| Translation-eligible zones | 0 (C119, now Tier 2 negative knowledge) |
| Forbidden transitions | none beyond known effects: token-level zeros reduce under a joint null (C2081, supersedes C957); class-level "17 in 5 classes" demoted (C783, C2060) |
| Operational categories | 8, keyword-imposed rather than discovered (C2069) |
| Macro-automaton states | 6 (8.17x class compression; C976, C1010). AXM self=0.697 is a mass-dominant state, not an attractor: the self-rate is composition (C978 scope-corrected) and there is no sequential convergence to AXM (C1402) |
| Generative sufficiency | 87% of measurable structure (M2 frontier; C1025/C1030/C1033/C1034). The "forbidden suppression" component is an idealization test (C2063); the prohibition layer it suppresses is withdrawn (C2081) |

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

Voynich tokens function differently than words in natural language. The manuscript has four distinct layers:

### Vocabulary by System

| System | Unique Types | Model |
|--------|-------------|-------|
| **Currier B** | 479 | 49 instruction classes (9.8x compression) |
| **Currier A** | ~2,400 | Registry entries: 609 RI + 404 PP MIDDLEs |
| **AZC** | ~800 | Static positional lookup table (shares with both A and B) |
| **HT** | ~1,200 | Compound specifications (morphological subset of B; C935) |
| **Full H-track** | ~12,362 | All systems combined |

### Currier B: Execution Grammar

In B, tokens behave as members of grammar classes, not as semantic words. ("Instruction", "operator" and "execution" below are the Tier-3 working vocabulary; the measured fact is the class grammar, C121.)

1. **479 token types collapse to 49 instruction classes.** The distributional behavior is determined by class, not the specific token. (C121)

2. **Token morphology: [ARTICULATOR] + [PREFIX] + MIDDLE + [SUFFIX].** PREFIX carries line position via a base-modifier positional grammar (C1218-C1219); readings of PREFIX as "operational channel" (C929), MIDDLE as "core action" and SUFFIX as "role marker" are interpretive glosses (operational referents are not recovered; C171, demoted to Tier 3).

3. **8 operational categories** (THERMAL, CONTAINMENT, FLOW, MONITORING, OPERATION, STAGING, MARKING, TRANSITION) — the taxonomy is keyword-imposed, not discovered (C2069); C1250 is kept at Tier 2 for its atom-independent signal only. "Categories predict escape dynamics" (C1274) is demoted to Tier 3 (circular). Category sequence structure: C1286.

4. **6-state macro-automaton** compresses 49 classes (C976, C1010). AXM is the mass-dominant state (self=0.697 is composition, C978 scope note); there is no sequential convergence to it (C1402, C1403). 6 folio archetypes (C1025); REGIME is a soft gradient, not 4 crisp classes (C1712, C2070). [v7.26 status: C1025 demoted to Tier 3 (reduced by C2063)]

5. **Paragraph body cycling:** Two universal suffix modes alternate within paragraphs — Mode A (specification/energy) and Mode B (continuation/equilibration). Cross-mode coupling is positional and paragraph-scoped, not sequential (C1229-C1231, C1308-C1312).

### Currier A: Registry Vocabulary

In A, tokens are **categorical entries**, not instructions:

1. **MIDDLEs bifurcate into RI and PP.** Registry-Internal (609) are A-exclusive discriminators. PP (404) are shared with B — vocabulary present in both systems. (C498)

2. **Token structure: [ARTICULATOR] + [PREFIX] + MIDDLE + [SUFFIX].** MIDDLE is the primary identity carrier; PREFIX/SUFFIX encode structural properties. (C267, C293)

3. **No direct A→B token lookup.** A entries do not "translate" to B instructions. They specify constraints that filter B legality. (C384)

### Key Principle

**A token lacking special highlighting is NOT unknown.** Every token has structural classification (instruction class, morphological decomposition, system legality). [Correction per C124 as corrected and C566: in Currier B, the HT/UN tokens (30.5% of B) lie outside the 49-class grammar and are classified by exclusion, not by instruction class.] "Neutral" means "non-contrastive"—it does not carry *additional* discriminative signal beyond its base class.

---

## Why Visualization Tools Highlight Only Some Tokens

Visualization tools (like Script Explorer) highlight tokens based on **contrastive marker roles**—features that distinguish subsets of tokens from the general population:

- A-enriched vs B-enriched tokens
- Kernel-heavy vs kernel-light prefixes [the "kernel" label is historical: C089 superseded by C2082 — k/h/e are not a core operator set]
- Line-position markers
- LINK operators [C609/C1174: LINK is 13.2% of B and a morphological artifact of "ol"; the monitoring reading is withdrawn]

This highlighting reflects UI design choices optimized for showing *discriminative* features, not the boundaries of structural knowledge.

**What the highlighting does NOT mean:**
- Unhighlighted ≠ unknown
- Unhighlighted ≠ unclassified
- Unhighlighted ≠ outside the grammar

All tokens are structurally classified. The ~10-30% that receive highlighting carry *additional* contrastive information. The ~70-90% that appear neutral are fully classified but lack special discriminative roles.

---

## Structural Analysis vs Interpretive / Probabilistic Reasoning

This project maintains a clear boundary between two analytical layers:

**Structural Layer (Tier 0-2):** Internal grammar reconstruction based on distributional evidence, transition patterns, and morphological analysis. Statements in this layer describe what the text *is* structurally—the 49 classes, line organisation (zones, regularity, boundary glyph coupling), folio units, word-ending routing (C2082). These are the established measurements about the internal organization of the text. (Operator roles, hazard topology and convergence behavior were once listed here; they are withdrawn or demoted — see [SYSTEM/STATUS_BRIEF.md](SYSTEM/STATUS_BRIEF.md) §3.)

**Interpretive Layer (Tier 3-4):** Reasoning about what the notation might *describe* in the real world (including the control-program reading), what processes it might govern, or how to fit probabilistic models to observed distributions. This layer is explicitly allowed, operates conditionally on structural constraints, and remains quarantined from frozen facts.

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

- **Tier 0 facts are PROVEN** - do not attempt to reopen or "improve" (note: the Tier-0 statement was itself restated to its measured core on 2026-09-28 after re-check, with human sign-off; several former Tier-0 rows are now Tier 2/3 or superseded — check `CONSTRAINT_TABLE.txt`, not this page's older lists)
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
| **Know what currently stands / what is withdrawn** | [SYSTEM/STATUS_BRIEF.md](SYSTEM/STATUS_BRIEF.md) — read first |
| **Check a constraint's live status and tier** | `CONSTRAINT_TABLE.txt` (generated; absent = dead, Tier 3 = demoted) |
| **Find a primary/secondary source text** | [SOURCES.md](SOURCES.md) — what's under `sources/` |
| **Load transcript data** | [DATA/TRANSCRIPT_ARCHITECTURE.md](DATA/TRANSCRIPT_ARCHITECTURE.md) |
| **Token annotation data** | [DATA/TRANSCRIPT_ARCHITECTURE.md](DATA/TRANSCRIPT_ARCHITECTURE.md) → Annotation Data Files |
| **Rosettes foldout data** | [DATA/ROSETTES_DATA_ARCHITECTURE.md](DATA/ROSETTES_DATA_ARCHITECTURE.md) |
| **AZC notation (placement codes, ring order, IVTFF mapping)** | [DATA/AZC_NOTATION_PROVENANCE.md](DATA/AZC_NOTATION_PROVENANCE.md) — read before any AZC `placement`-driven analysis |
| Understand the core finding | [CORE/frozen_conclusion.md](CORE/frozen_conclusion.md) |
| Know what's been ruled out | [CORE/falsifications.md](CORE/falsifications.md) |
| **Validate A structure (API)** | [STRUCTURAL_CONTRACTS/currierA.casc.yaml](STRUCTURAL_CONTRACTS/currierA.casc.yaml) |
| **Validate B grammar (API)** | [STRUCTURAL_CONTRACTS/currierB.bcsc.yaml](STRUCTURAL_CONTRACTS/currierB.bcsc.yaml) — its kernel, hazard-topology, LINK, convergence and recovery sections predate the September 2026 review; check STATUS_BRIEF §3 before relying on them |
| **Understand A→AZC transform** | [STRUCTURAL_CONTRACTS/azc_activation.act.yaml](STRUCTURAL_CONTRACTS/azc_activation.act.yaml) |
| **Understand AZC→B propagation** | [STRUCTURAL_CONTRACTS/azc_b_activation.act.yaml](STRUCTURAL_CONTRACTS/azc_b_activation.act.yaml) |
| **Validate HT properties (API)** | [STRUCTURAL_CONTRACTS/humanTrack.htsc.yaml](STRUCTURAL_CONTRACTS/humanTrack.htsc.yaml) |
| **Validate paragraph structure (API)** | [STRUCTURAL_CONTRACTS/paragraph.psc.yaml](STRUCTURAL_CONTRACTS/paragraph.psc.yaml) |
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
| Check quantitative metrics | [METRICS/](METRICS/) (grammar, coverage, LINK; `hazard_metrics.md` is historical — the hazard layer is withdrawn, C2081) |
| **Glossing rules and vocabulary** | [GLOSSING.md](GLOSSING.md) (read before ANY gloss work) |
| **Atom decomposition for glossing** | [GLOSSING.md](GLOSSING.md) → Atom-Level Decomposition (`morph.atomize()`) |
| **Per-folio findings** | [FOLIOS/INDEX.md](FOLIOS/INDEX.md) — individual folio analysis notes |
| See speculative interpretations | [SPECULATIVE/](SPECULATIVE/) (apparatus-centric semantics, CCM, ECR) |
| **Currier A interface postures** | [SPECULATIVE/tier3_interface_postures.md](SPECULATIVE/tier3_interface_postures.md) |
| Understand apparatus-centric view | [SPECULATIVE/apparatus_centric_semantics.md](SPECULATIVE/apparatus_centric_semantics.md) |
| Trace constraint to source phase | [MAPS/claim_to_phase.md](MAPS/claim_to_phase.md) (provenance only, early numbers; not status) |
| Work with explanatory fits | [MODEL_FITS/INDEX.md](MODEL_FITS/INDEX.md) |
| Understand fit methodology | [SYSTEM/FIT_METHODOLOGY.md](SYSTEM/FIT_METHODOLOGY.md) |

---

## What This Project Does NOT Allow

These approaches have been tested and rejected (tiers vary — check each number in `CONSTRAINT_TABLE.txt`; the current scoped list of excluded rivals is [SYSTEM/STATUS_BRIEF.md](SYSTEM/STATUS_BRIEF.md) §4):

- **Language encoding** - natural language written one token per word is excluded (C132, C2015, C2022). The older "0.19% reference rate" figure (C130, Phase X.5) is tainted and not relied on.
- **Cipher encoding** - only the classes actually tested are excluded: token≈word codes, atom-level polyalphabetic ciphers, three published decipherments (C1976, C2017), Timm & Schinner (C2077), the Naibbe cipher as published (C2080). The older blanket line "transforms decrease mutual information (Phase G)" is scoped: plain syllable writing is excluded on unit inventory (C2085); syllables written with spelling variation, word-level codebooks, modified verbose ciphers and the Rugg grille are untested.
- **Glyph-level semantics** - 0 identifier tokens found (Phase 19)
- **Illustration-dependent logic** - swap invariance p=1.0 (Phase ILL)
- **Step-by-step recipe format** - families are emergent (Phase FSS)
- **Material/ingredient encoding** - listed here on the PURE_OPERATIONAL verdict (C120), now demoted to Tier 3; what stands is only that no referents have been recovered (C171, also Tier 3). Not a current falsification.
- **Translation attempts** - 0 translation-eligible zones exist (C119, Tier 2 negative knowledge)

See [CORE/falsifications.md](CORE/falsifications.md) for complete list with evidence.

---

## What the Manuscript DOES Encode (measured structure)

**Tier 0 (restated 2026-09-28, measured core):**
- A 49-class token grammar covering 100% of its own 480-type vocabulary = 69.5% of Currier B tokens; HT/UN defined by exclusion (C121, C124 as corrected, C566)
- Line organisation: positional zones (C956), line regularity (C357), word-boundary glyph coupling (C1212, C1563)
- Folio units that share the grammar and carry their own vocabulary (C531); no duplicate lines or paragraphs (C1790)
- Not reproduced by copy-and-modify generation (C2077) or by the Naibbe cipher as published (C2080)

**Formerly listed here as Tier 0 — withdrawn or demoted (v7.24/7.25; STATUS_BRIEF §3):**
- "Executable grammar, 100% coverage" — coverage is of the grammar's own vocabulary only (C124 as corrected); "executable" is interpretive (C115 demoted to Tier 3)
- "Kernel control (3 operators: k, h, e)" — C089 superseded by C2082: at glyph level k shows nothing beyond its controls, and the e/bench signal is word-ending routing; C085, C103–C105 Tier 3
- "Hazard topology (17 forbidden transitions, 5 failure classes)" — class level demoted (C783), 5-class taxonomy imposed (C2060), token-level zeros reduce to composition, zones and boundary coupling (C2081; C957 superseded)
- "Convergence to stable states (57.8% terminal STATE-C)" — kept only as an occupancy measurement (C074, Tier 2); no sequential convergence (C1401–C1403); C079, C084 demoted to Tier 3
- LINK population — 13.2% of tokens, a morphological artifact of "ol" (C609, C1174), not a monitoring operator
- "Folio = complete program, Line = formal control block" — the measured parts are the folio units and line organisation above; "program" / "control block" is the Tier-3 working reading

**Established (Tier 2):**
- Word-ending routing: a token's two-glyph ending predicts the next token's class beyond boundary coupling (C2082)
- 6-state macro-automaton (C976, C1010); AXM is mass-dominant, not an attractor — no sequential convergence to it (C978 scope note, C1402)
- 8 operational categories spanning all 4 systems (C1250) — taxonomy keyword-imposed (C2069); only the atom-independent signal is kept
- PREFIX base-modifier positional grammar (C929, C1218-C1219)
- Sister pairs achieve category divergence through vocabulary selection (C1303-C1307)
- Paragraph body: suffix mode cycling within execution gradient envelope (C1229-C1232)
- Cross-mode parallel tracks: positional alignment, B→A thermal feedback, no sequential coupling (C1308-C1312)
- 5 apparatus profiles from marker MIDDLEs (C1247-C1249) — "REGIME encodes apparatus type" is interpretive; REGIME is a soft gradient, and REGIME effects need a within-section re-test (C1712, C2070)
- Generative sufficiency: 49-class Markov + forbidden suppression reproduces 87% of structure (C1025/C1030) — the forbidden-suppression test is an idealization test (C2063) and the prohibition layer is withdrawn (C2081)

**Not encoded (operator provides externally)** — this boundary list presupposes the Tier-3 control reading:
- Sensory completion judgment (when to stop)
- Material selection (what to process)
- Hazard recognition (physical signs of failure) [the in-text hazard layer is withdrawn, C2081]

See [CORE/model_boundary.md](CORE/model_boundary.md) for complete boundary.

---

## Current State

| Category | Count |
|----------|-------|
| Live constraints (generated table, v7.36) | 1,897 (T0 2, T1 38, T2 1,687, T3 166, T4 4) |
| Completed phases | 763 |
| Folios enumerated | 83 |
| Currier B tokens (H-track) | 23,243 (the legacy "75,248 instructions cataloged" appears to be a pre-H-filter count) |
| Token types in grammar | 479 (the corrected C124 row counts 480) |
| Instruction classes | 49 |
| Scripts in archive | 98 |
| Structural contracts | 6 |

---

## Four-Layer Architecture

The manuscript comprises four structurally distinct systems sharing a **global morphological type system** (not grammar):

> **Important distinction:** The "single shared grammar" in the frozen conclusion applies to **Currier B only**. Currier A uses a different formal system (non-sequential). What IS shared across all systems is the morphological TYPE system (prefix/suffix structure, compositional rules).

| Layer | System | Tokens (H-track) | Function (Tier-3 working reading) |
|-------|--------|--------|----------|
| **Execution** | Currier B | 23,243 (61.2%) | Controls what you do over time |
| **Distinction** | Currier A | 11,415 (30.1%) | Catalogs where distinctions matter |
| **Context** | AZC | 3,299 (8.7%) | Static positional lookup table classifying vocabulary |
| **Orientation** | HT | 7,042* | Compound specifications redundant with body lines; keeps operator oriented |

(Percentages recomputed on the canonical H-track total of 37,957; the earlier 61.9% / 30.5% did not match these counts.)

*HT tokens are a morphological subset of Currier B — already counted in B total. They use the same morphology but do not participate in the 49-class grammar. (C935)

- A and B are **FOLIO-DISJOINT** (0 shared folios)
- A and B are **GRAMMAR-DISJOINT** (different formal systems)
- A and B are **VOCABULARY-INTEGRATED** (69.8% shared types)
- AZC bridges both with 60.5% shared vocabulary
- 8 operational categories are the first organizing principle spanning all 4 systems (C1250) [scoped: the taxonomy is keyword-imposed, C2069]

See [ARCHITECTURE/cross_system.md](ARCHITECTURE/cross_system.md) for details.

---

## File Registry

- **Constraints (by topic):** [CLAIMS/INDEX.md](CLAIMS/INDEX.md) - Browse by category, follow links to details
- **Architectural guide:** [MODEL_CONTEXT.md](MODEL_CONTEXT.md) - How to interpret the constraint system
- **Structural contracts:** [STRUCTURAL_CONTRACTS/](STRUCTURAL_CONTRACTS/) - Derived API specifications (CASC, AZC-ACT, AZC-B-ACT, BCSC, HTSC, PSC)
- **Per-folio findings:** [FOLIOS/INDEX.md](FOLIOS/INDEX.md) - Individual folio analysis notes (crib decodes, structural properties)
- **Glossing system:** [GLOSSING.md](GLOSSING.md) - Atom glosses, PREFIX/SUFFIX semantics, expert validation workflow
- **Dark pipeline dictionary:** [DARK_PIPELINE_DICTIONARY.md](DARK_PIPELINE_DICTIONARY.md) - Candidate material identifications from cross-folio dark MIDDLE analysis (Tier 4 exploratory)
- **Catalan vocabulary mapping:** [CATALAN_VOCABULARY.md](CATALAN_VOCABULARY.md) - Old Catalan → Latin → Voynich verb/term mapping from Buosi-Moncunill thesis. ABC cipher key. Drip-counting system. Partial coverage (Practica Ch1-12, Mercuriorum Ch1-14); full SISMEL edition on order
- **Pending tests:** [PENDING_TESTS.md](PENDING_TESTS.md) - Informal findings and exploratory results awaiting formal testing (promote to phase when data available, delete when resolved)
- **Phases:** [MAPS/phase_index.md](MAPS/phase_index.md) - Phase index (early phases only; current phases are under `phases/` and in the changelog)
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
- **Fit registry:** [MODEL_FITS/INDEX.md](MODEL_FITS/INDEX.md) (75 fits in the generated `FIT_TABLE.txt`)
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

*Context System v4.63 footer (historical, 2026-02-25; the "FROZEN STATE / ANALYSIS CLOSED" status is withdrawn — see the STATUS banner at the top) | PCA-v1 certified internal contract consistency only*
