# MODEL_CONTEXT.md

**Version:** 3.4 | **Date:** 2026-01-16 | **Status:** FROZEN

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
