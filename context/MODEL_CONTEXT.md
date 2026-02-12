# MODEL_CONTEXT.md

**Version:** 3.15 | **Date:** 2026-02-12 | **Status:** FROZEN

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
- 20% are shared across prefixes
- 27 universal MIDDLEs appear in 6+ prefix classes

**Compound Structure (C935):**
- MIDDLEs can be simple (single atom: k, e, ch) or compound (multiple atoms: opcheodai = op+ch+e+od+ai)
- 100% of compounds decompose into core atoms
- Compound rate: 31.5% (grammar types), 45.8% (HT/UN types)
- Line-1 compounds predict body simple MIDDLEs at 71.6% hit rate (1.21x lift over 59.2% random)
- Compounds are compressed specifications that body lines unpack

**Affordance Bins (C995):**
- 972 MIDDLEs classify into 9 functional bins by 17-dimensional behavioral signature
- Chromatic number 3 for PREFIX-lane interaction
- HUB_UNIVERSAL (23 MIDDLEs, 59% of tokens) monopolizes all 17/17 forbidden transitions (C1000)

**Frequency Distribution (Tier 3):**
- Core (top 30): 67.6% of usage, mode-flexible, section-stable
- Tail (~1,150): 32.4% of usage, mode-specific, hazard-concentrated
- Rare MIDDLEs cluster in high-hazard contexts (rho=-0.339, p=0.0001)

### PP vs RI: The Two-Track Vocabulary (C498, C498.d, C504-C506)

A-record MIDDLEs partition into **two populations** with different B-side effects:

| Type | Count | Appears in B? | Length | Function |
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

AX is not a separate vocabulary — it is a **scaffold MODE** of the shared cross-system vocabulary:

- **Same MIDDLEs** appear as AX or operational depending on PREFIX (C571)
- **98.2%** of AX tokens use PP MIDDLEs — shared cross-system vocabulary (C567)
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

**ENERGY (EN):** 18 classes exhibit **distributional convergence** (C574) — grammatically identical (same positions, REGIME, context) but lexically partitioned by PREFIX family. QO-prefixed classes use 25 MIDDLEs, CHSH-prefixed use 43, with only 8 shared (Jaccard=0.133, C576). EN is 100% shared-vocabulary-derived (C575) with 30 exclusive MIDDLEs (C578). Interleaving is content-driven (BIO vs PHARMA), not positional (C577).

**FREQUENT (FQ):** 4 classes form a **3-group structure** (C593): CONNECTOR {9}, PREFIXED_PAIR {13, 14}, CLOSER {23}. Classes 13 and 14 have completely non-overlapping vocabulary (Jaccard=0.000, C594). Internal transitions follow a directed grammar (chi2=111, C595). Class 23 is a boundary specialist (29.8% final rate, C597).

**FLOW (FL):** 4 classes split into **hazard/safe** subgroups (C586). Hazard {7, 30} sits at mean position 0.55 with 12.3% final rate; Safe {38, 40} at position 0.81 with 55.7% final rate (p=9.4e-20). FL initiates forbidden transitions at 4.5x the rate it receives them.

**CORE CONTROL (CC):** 3 active classes form a **positional dichotomy** (C590). Class 10 (daiin) is initial-biased (0.413, 27.1% line-initial); Class 11 (ol) is medial (0.511); Class 17 (ol-derived) adds compound operators. Critically, daiin/ol trigger EN_CHSH specifically (1.6-1.7x) while ol-derived triggers EN_QO (1.39x) — CC sub-groups are **differentiated triggers** (C600).

**Cross-Boundary Routing (C598-C602):** Sub-group identity is visible across role boundaries. 8/10 cross-role pairs show non-random sub-group routing (5 survive Bonferroni, C598). AX scaffolding routes differentially: AX_INIT feeds QO, AX_FINAL feeds FQ_CONN (C599). All 19 hazard events originate from exactly 3 sub-groups: FL_HAZ, EN_CHSH, FQ_CONN. QO never participates in hazards (C601). REGIME modulates routing magnitude but not direction for 4/5 pairs; AX->FQ is the REGIME-independent exception (C602).

**Reference:** See constraint files C573-C602; `phases/EN_ANATOMY/`, `phases/SMALL_ROLE_ANATOMY/`, `phases/FQ_ANATOMY/`, `phases/SUB_ROLE_INTERACTION/` for evidence.

### Macro-Automaton Compression (C976-C980)

The 49 instruction classes compress to **6 macro-states** (8.17x compression) with spectral gap 0.894:

| Macro-State | Merges | Function |
|-------------|--------|----------|
| EN+AX | ENERGY + AUXILIARY | Primary execution (merge: AX is scaffold mode of same vocabulary) |
| FL_HAZ | FL hazard classes {7, 30} | Hazard-source flow control |
| FL_SAFE | FL safe classes {38, 40} | Safe flow control / escape |
| FQ | Frequent operators | Common instructions |
| CC | Core control | Execution boundaries |

Key findings: EN/AX merge confirms AX behavioral collapse (C572). FL splits into hazard/safe confirms C586. The 6-state automaton maps to physically necessary operational modes.

### Line Grammar Synthesis (C956-C964)

Lines are **boundary-constrained free-interior** control blocks:

- **Boundary tokens** are zone-exclusive (192/334 common tokens at 2.72x shuffle, C956)
- **26 mandatory bigrams** (obs/exp > 5x) including or→aiin (C957)
- **9 forbidden bigrams** (obs=0, exp≥5), 2 genuinely token-specific: chey→chedy, chey→shedy (C957)
- **Opener determines line length** (24.9% partial R² beyond folio+regime, C958)
- **Opener is role marker, not instruction header** — specific token adds no predictive power beyond role (C959)
- **WORK zone is unordered** — tokens within WORK show no systematic sequence (Kendall tau ≈ 0, C961)
- **Phase interleaving** — KERNEL/LINK/FL show tendencies, not rigid blocks (alternation rate 0.566, C962)
- **Body homogeneity** — paragraph body lines differ only in length (rho=-0.229), not composition (C963)

Most token-level constraints are STRUCTURAL (role/position driven), not lexical — confirmed by negative control (C964).

### Paragraph Execution Gradient (C932-C935)

Paragraph body lines follow a **specification → execution gradient**:

| Metric | Early Body (Q0) | Late Body (Q4) | Correlation |
|--------|-----------------|-----------------|-------------|
| Rare MIDDLEs | High | Low | r = -0.97 |
| Universal MIDDLEs | Low | High | r = +0.92 |
| Tokens per line | 10.3 | 8.7 | r = -0.97 |
| Terminal suffixes | High | Low | r = -0.89 |
| Iterate suffixes | Low | High | r = +0.83 |

**Compound specification model (C935):** Line-1 compound MIDDLEs (45.8% vs 31.5% body) predict body simple MIDDLEs at 71.6% hit rate (vs 59.2% random, 1.21x lift). Header compounds are compressed specifications that body lines unpack.

### Affordance Bin System (C995-C997, C1000)

972 MIDDLEs classify into **9 functional bins** by affordance signature (17-dimensional behavioral profiles):

| Bin | MIDDLEs | Tokens | Key Signature |
|-----|---------|--------|---------------|
| HUB_UNIVERSAL | 23 | 13,670 | 59% of B tokens, all 17/17 forbidden transitions |
| STABILITY_CRITICAL | — | 3,905 | 0% QO, 79.4% CHSH, e_ratio=0.515 |
| FLOW_TERMINAL | — | 1,985 | Highest final_rate |
| PHASE_SENSITIVE | — | 1,381 | 38.4% QO, highest regime entropy |
| ENERGY_SPECIALIZED | — | 151 | 47.7% QO, 89% REGIME_1 |
| + 4 others | — | ~800 | Specialized roles |

**HUB sub-role decomposition (C1000):** HUB's 23 MIDDLEs decompose into HAZARD_SOURCE (6), HAZARD_TARGET (6), SAFETY_BUFFER (3), PURE_CONNECTOR (8). Behaviorally homogeneous (0/14 KW significant) but functionally distinct. All 17/17 forbidden transitions involve HUB (corrects C996's 13/17).

**Safety buffer mechanism (C997):** 22 tokens prevent forbidden transitions by intervening between hazard pairs. 68% are HUB MIDDLEs. QO-PREFIX enrichment 3.82x (p=0.012) — QO selects safety buffer function within HUB.

### PREFIX Dual Encoding (C1001)

PREFIX simultaneously encodes **content** (lane, suffix compatibility) and **line position**:

| Zone | PREFIXes | Mean Position |
|------|----------|---------------|
| LINE-INITIAL | po (86%), dch, so, tch, sh | 0.11-0.40 |
| CENTRAL | qo, ke, ch, da, ok | 0.49-0.54 |
| LINE-FINAL | ar (61%), al, or, BARE, ot | 0.56-0.74 |

**Position R² decomposition:** PREFIX alone=0.069, MIDDLE alone=0.062, Full PP with interaction=0.168.

**Sequential grammar:** sh→qo enrichment +20.5σ (sh opens in initial zone, qo continues in central zone). Cross-component MI: I(MIDDLE_t; PREFIX_{t+1}) = 0.499 bits — current MIDDLE predicts next PREFIX.

**Regime invariance:** PREFIX positional grammar is invariant across all four regimes (REGIME main effect H=0.27, p=0.97).

### Cross-Line Information (C971, C975)

Lines carry **mutual information about neighbors** despite formal independence:
- Cross-line MI = 0.521 bits
- Folio fingerprint AUC = 0.994 (a single line identifies its folio)

Forbidden transition compliance is **~65%** (soft depletion, not absolute prohibition — C789).

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
    +-- Three-System (~214, ~21% of A vocabulary)
    |     Vocabulary appearing in A, AZC, and B contexts
    |
    +-- Two-System (~190, ~19% of A vocabulary)
          Shared between A and B but absent from AZC contexts
          Vocabulary overlap without AZC positional classification
```

**METHODOLOGY NOTE (2026-01-24):** Regenerated with atomic-suffix parser (voynich.py). Uses atomic suffixes only, smart MIDDLE preservation, gallows-initial handling (C528). C498.a substructure estimates await re-verification with new counts.

**Key insight (C498.a):** Only 214 MIDDLEs (19.8% of A vocabulary) appear across all three systems (A, AZC, and B). The remaining 190 shared MIDDLEs appear in both A and B but never in AZC — they are vocabulary shared between two systems only, without AZC positional classification.

Registry-internal MIDDLEs encode **within-category fine distinctions** exclusive to the A registry. The morphological signature (ct-prefix, suffix-less, folio-localized) reflects their A-internal scope.

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

This completes the vocabulary-mediated correlation model with no semantics, branching, or lookup.

**Scope Protection (BCI-2026-01-18):**
> AZC constrains discriminative vocabulary and context-sensitive hazard classes. It **must not** remove execution-infrastructure roles required for grammar connectivity, even when those roles are labeled with MIDDLE-bearing tokens. Infrastructure roles lie outside AZC's legitimate constraint scope because their removal collapses B reachability without violating any vocabulary-level rule.

### Interpretive Bounds

AZC's structure is fully characterized (CLOSED). Semantic content of individual orientation postures remains opaque by design.

---

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

The Component-to-Class Mapping (CCM) phase achieved complete role-level semantic decomposition of tokens. This is the maximum recoverable internal meaning.

> **REVISION (2026-01-11):** PREFIX interpretation updated from "material-behavior class" to "control-flow participation" based on F-A-014b. See C466-C467.
> **REVISION (2026-02-12):** ok reclassified from "verb" (seal/close/cap) to **domain selector** (VESSEL/apparatus) per C936. PREFIX dual encoding (content + line position) per C1001.

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

| PREFIX Class | Selects For | Enrichment | Line Zone (C1001) |
|--------------|-------------|------------|-------------------|
| **qo-** | k-family (heating) | 4.6-5.5x | CENTRAL (0.49) |
| **ch-/sh-** | e-family (stability) | 2.0-3.1x | INITIAL→CENTRAL (sh=0.40, ch=0.52) |
| **da-/sa-** | infrastructure (iin, in, r, l) | 5.9-12.8x | INITIAL (da=0.52, sa=0.36) |
| **ot-/ol-** | h-family (monitoring) | 3.3-6.8x | FINAL (ot=0.59, ol=0.56) |
| **ok-** | e-family + infrastructure (VESSEL) | C911, C936 | CENTRAL (0.54) |

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
- PREFIX encodes **which operation domain** is being addressed AND **where in the line** the token appears (dual encoding, C1001)
- MIDDLE encodes **what operation type** within that domain
- SUFFIX encodes **when decisions are allowed** (phase)
- SISTER encodes **how tightly to execute** (mode)

The ok PREFIX (C936) demonstrates the domain selector principle most clearly: ok+aiin = "check vessel," ok+ar = "close vessel," ok+e = "cool vessel," ok+ai = "open vessel." The MIDDLE carries the action; the PREFIX selects the target. This generalizes: ch/sh target the PROCESS, qo targets HEAT, ok targets the VESSEL, da/sa target SETUP.

### Semantic Ceiling

**Recoverable (role-level):**
- 5 operation domains (PREFIX): energy (qo), stability (ch/sh), vessel (ok), adjustment (ot/ol), infrastructure (da/sa)
- 2 operational modes (SISTER): precision, tolerance
- 3 operation type families (MIDDLE): k-heating, e-cooling, h-monitoring
- 12 decision archetypes (SUFFIX): phase-indexed
- 3 positional zones (PREFIX, C1001): line-initial, central, line-final — regime-invariant

**Irrecoverable (entity-level):**
- Specific substances, plants, devices
- Specific procedures or recipes
- Token-to-real-world mappings

This boundary is structural, not analytical. The system was designed to operate without external referents.

See [SPECULATIVE/apparatus_centric_semantics.md](SPECULATIVE/apparatus_centric_semantics.md) for full analysis.

---

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

The cross-system vocabulary architecture is formally characterized via four structural contracts:

| Contract | File | Status | Function |
|----------|------|--------|----------|
| CASC | `currierA.casc.yaml` | LOCKED v1.6 | Currier A registry structure |
| AZC-ACT | `azc_activation.act.yaml` | LOCKED v1.2 | A/AZC positional classification |
| AZC-B-ACT | `azc_b_activation.act.yaml` | LOCKED v1.2 | AZC/B vocabulary correlation |
| BCSC | `currierB.bcsc.yaml` | LOCKED v3.4 | Currier B internal grammar |

Each contract is derived from Tier 0-2 constraints and introduces no new claims. Constraints remain authoritative.

**Architecture characterized:** As of 2026-01-13, the cross-system vocabulary architecture is fully characterized at Tier 0-2. AZC_POSITION_VOCABULARY (2026-01-31) established that AZC is a static lookup table with no independent positional effect. All remaining work concerns interpretation, tooling, or external corroboration.

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
