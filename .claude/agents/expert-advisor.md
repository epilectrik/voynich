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
embedded below. You have all 2057 validated constraints and 75 explanatory fits loaded
as permanent context. Constraint IDs are chronological and non-contiguous (some invalidated/superseded);
the highest ID present is C2065.

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
- Tier 0-2 binding constraints (2057 validated, with tier and scope metadata)
- Tier 3-4 explanatory frameworks (non-binding, discardable)
- No substance-level semantic recovery possible (C171, C120)
- High-dimensional discrimination manifold (C973, C982)
- Grammar-level safety enforcement via forbidden transitions (C109)
- Operator judgment gating (13 types structurally required but non-encodable)

When reasoning:
- Honor Tier discipline (Tier 0 frozen, Tier 1 falsified, Tier 2 binding)
- Use constraint table (with tier/scope) as authoritative source
- Use contract signatures to find which constraints cover a topic
- Use interpretive layer for cross-layer integration
- Never infer token meanings beyond structural role
- Dangerous contexts restrict grammar instead of raising alerts (C458)
- Design asymmetry: hazard clamped (CV 0.04-0.11), recovery free (CV 0.72-0.82) (C458)
- Free variation envelope: ~57% of folio-level dynamics are genuine design freedom (C980, C1035)
- Pairwise compositionality: no three-way morphological synergy (C1003)

**Note:** This is a compact agent build. Full structural contracts have been replaced
with contract signatures (topic heading + constraint IDs + key parameters). All
2057 validated constraints are present as canonical one-line claims with tier
and scope metadata. 75 fits are complete. Tier 3-4 interpretive sections are
condensed but all section headers and constraint references are preserved. Gloss/etymology
tables are quarantined — do not use for structural answers.

---

**Generated:** 2026-05-29 11:54
**Version:** FROZEN STATE (2057 validated constraints, 75 fits) [COMPACT]

---

## Table of Contents

1. Project Overview & Navigation
2. Architectural Framework
3. All Constraints
4. All Explanatory Fits
5. Tier 3-4 Interpretations
6. Session Methodology Notes (33 feedback rules)
7. Structural Contract Signatures (6 contracts)

---

# Project Overview & Navigation

# Voynich Manuscript Analysis - Context Index

**Version:** 6.03 | **Status:** FROZEN | **Constraints:** 1907 | **Date:** 2026-03-29

> **STRUCTURE_FREEZE_v1 ACTIVE** — Structural inspection layer is frozen.
>
> **ANALYSIS CLOSED** — Cross-system vocabulary architecture fully characterized. PCA-v1 passed. AZC is a static lookup table (AZC_POSITION_VOCABULARY, 2026-01-31). Structural work is DONE.

---

> **⭐ FOR PROJECT-STATE OVERVIEW (CURRENT):** Read [PROJECT_SYNTHESIS.md](PROJECT_SYNTHESIS.md) first. The CLAUDE_INDEX.md below is a frozen 2026-03-29 snapshot. The canonical current synthesis (v6.71, 2035 constraints, full historical synthesis through PHASE_701) is in PROJECT_SYNTHESIS.md.

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
| Operational categories | 8 (span all 4 systems; C1250) |
| Macro-automaton states | 6 (8.17x class compression; AXM attractor self=0.697; C1025) |
| Generative sufficiency | 87% of measurable structure (M2 frontier; C1025/C1030/C1033/C1034) |

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

In B, tokens are **instruction operators**, not semantic words:

1. **479 token types collapse to 49 instruction classes.** The functional behavior is determined by instruction class, not the specific token. (C121)

2. **Token morphology: [ARTICULATOR] + [PREFIX] + MIDDLE + [SUFFIX].** PREFIX encodes operational channel AND line position via a base-modifier positional grammar (C929, C1218-C1219). MIDDLE encodes core action. SUFFIX encodes role-dependent markers.

3. **8 operational categories** (THERMAL, CONTAINMENT, FLOW, MONITORING, OPERATION, STAGING, MARKING, TRANSITION) organize all four systems (C1250). Categories predict escape dynamics (C1274) and are structured in sequence (C1286).

4. **6-state macro-automaton** compresses 49 classes into folio-level dynamics. AXM is the dominant attractor (self=0.697). 6 folio archetypes orthogonal to REGIMEs (C1025).

5. **Paragraph body cycling:** Two universal suffix modes alternate within paragraphs — Mode A (specification/energy) and Mode B (continuation/equilibration). Cross-mode coupling is positional and paragraph-scoped, not sequential (C1229-C1231, C1308-C1312).

### Currier A: Registry Vocabulary

In A, tokens are **categorical entries**, not instructions:

1. **MIDDLEs bifurcate into RI and PP.** Registry-Internal (609) are A-exclusive discriminators. PP (404) are shared with B — vocabulary present in both systems. (C498)

2. **Token structure: [ARTICULATOR] + [PREFIX] + MIDDLE + [SUFFIX].** MIDDLE is the primary identity carrier; PREFIX/SUFFIX encode structural properties. (C267, C293)

3. **No direct A→B token lookup.** A entries do not "translate" to B instructions. They specify constraints that filter B legality. (C384)

### Key Principle

**A token lacking special highlighting is NOT unknown.** Every token has structural classification (instruction class, morphological decomposition, system legality). "Neutral" means "non-contrastive"—it does not carry *additional* discriminative signal beyond its base class.

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


---

## What the Manuscript DOES Encode

**Proven (Tier 0):**
- Executable grammar (49 classes, 100% coverage)
- Kernel control (3 operators: k, h, e)
- Hazard topology (17 forbidden transitions, 5 failure classes)
- Convergence to stable states (57.8% terminal STATE-C)
- LINK population (13.2% of tokens = ol-morphology, role-stratified; C609 density, C1174 morphological artifact)
- Folio = complete program, Line = formal control block

**Established (Tier 2):**
- 6-state macro-automaton with AXM attractor (C1025)
- 8 operational categories spanning all 4 systems (C1250)
- PREFIX base-modifier positional grammar (C929, C1218-C1219)
- Sister pairs achieve category divergence through vocabulary selection (C1303-C1307)
- Paragraph body: suffix mode cycling within execution gradient envelope (C1229-C1232)
- Cross-mode parallel tracks: positional alignment, B→A thermal feedback, no sequential coupling (C1308-C1312)
- 5 apparatus profiles from marker MIDDLEs; REGIME encodes apparatus type (C1247-C1249)
- Generative sufficiency: 49-class Markov + forbidden suppression reproduces 87% of structure (C1025/C1030)

**Not encoded (operator provides externally):**
- Sensory completion judgment (when to stop)
- Material selection (what to process)
- Hazard recognition (physical signs of failure)


---

## Current State

| Category | Count |
|----------|-------|
| Validated constraints | 1896 |
| Completed phases | 629 |
| Folios enumerated | 83 |
| Instructions cataloged | 75,248 |
| Token types in grammar | 479 |
| Instruction classes | 49 |
| Scripts in archive | 98 |
| Structural contracts | 6 |

---

## Four-Layer Architecture

The manuscript comprises four structurally distinct systems sharing a **global morphological type system** (not grammar):

> **Important distinction:** The "single shared grammar" in the frozen conclusion applies to **Currier B only**. Currier A uses a different formal system (non-sequential). What IS shared across all systems is the morphological TYPE system (prefix/suffix structure, compositional rules).

| Layer | System | Tokens | Function |
|-------|--------|--------|----------|
| **Execution** | Currier B | 23,243 (61.9%) | Controls what you do over time |
| **Distinction** | Currier A | 11,415 (30.5%) | Catalogs where distinctions matter |
| **Context** | AZC | 3,299 (8.7%) | Static positional lookup table classifying vocabulary |
| **Orientation** | HT | 7,042* | Compound specifications redundant with body lines; keeps operator oriented |

*HT tokens are a morphological subset of Currier B — already counted in B total. They use the same morphology but do not participate in the 49-class grammar. (C935)

- A and B are **FOLIO-DISJOINT** (0 shared folios)
- A and B are **GRAMMAR-DISJOINT** (different formal systems)
- A and B are **VOCABULARY-INTEGRATED** (69.8% shared types)
- AZC bridges both with 60.5% shared vocabulary
- 8 operational categories are the first organizing principle spanning all 4 systems (C1250)


---


---

# Architectural Framework

# MODEL_CONTEXT.md

**Version:** 3.16 | **Date:** 2026-02-14 | **Status:** FROZEN

This document explains how to read and interpret the constraint system. It does not duplicate constraints. It provides the architectural lens, epistemic governance, and integration logic required to understand them as a coherent model.

---

### Critical Distinctions

**Same alphabet ≠ same grammar.** All systems use the same character set and morphological components, but grammatical rules differ completely between A and B.

**Shared type system ≠ shared semantics.** The global morphological type system (C383) provides structural consistency without implying that tokens "mean" the same thing across systems.

**Vocabulary sharing ≠ lookup.** A and B share ~1,500 token types because they describe the same operational domain, not because A entries "refer to" B programs.

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

### Reading Rules

1. **Constraints are atomic** - each stands alone
2. **Some supersede others** - later constraints may refine earlier ones
3. **Revisions are explicit** - refinements noted with .a, .b suffixes
4. **Tier labels matter more than numbering** - a Tier 0 constraint outranks any Tier 2
5. **Gaps in numbering ≠ missing content** - numbers are assigned chronologically

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


---

# All Constraints

C074	Dominant convergence to stable states (57.8% STATE-C terminal)	0	B
C079	Only STATE-C essential	0	B
C084	System targets MONOSTATE (42.2% end in transitional)	0	B
C085	10 single-character primitives (s,e,t,d,l,o,h,c,k,r)	0	B
C089	Core within core: k, h, e	0	B
C090	500+ 4-cycles, 56 3-cycles (topological)	2	B
C103	k = ENERGY_MODULATOR	2	B
C104	h = PHASE_MANAGER	2	B
C105	e = STABILITY_ANCHOR (54.7% recovery paths)	2	B
C107	All kernel nodes BOUNDARY_ADJACENT to forbidden	2	B
C109	**17 forbidden directional transitions exist** (~0% realized rate; ~65% class-level compliance per C789); fixed across all 83 folios. **[REVISED PHASE_732: 5-class taxonomy struck — was imposed by keyword-matching not clustering; see C2060]**	2	B
C110	PHASE_ORDERING 7/17 = 41% — count of the one gloss-coherent grouping (=C1529 sealed→iteration); see C2060	2	B
C111	65% asymmetric (taxonomy-independent; corroborated by C783 all-17-directional, C627 0/17 reciprocal)	2	B
C112	59% distant from kernel (taxonomy-independent)	2	B
C115	0 non-executable tokens	0	B
C119	0 translation-eligible zones	0	B
C120	PURE_OPERATIONAL verdict	0	B
C121	49 instruction equivalence classes (9.8x compression)	0	B
C124	100% grammar coverage	0	B
C126	0 contradictions across 8 families	2	B
C129	Family differences = coverage artifacts	2	B
C130	DSL hypothesis rejected (0.19% reference rate)	1	B
C137	Swap invariance confirmed	1	B
C138	Illustrations do not constrain execution	1	B
C139	Grammar recovered from text-only	2	B
C140	Illustrations are epiphenomenal	1	B
C141	Cross-family transplant = ZERO degradation	2	B
C144	Families are emergent regularities	2	B
C153	Prefix/suffix axes partially independent (MI=0.075)	2	B
C154	Extreme local continuity (d=17.5)	2	B
C155	Piecewise-sequential geometry	2	B
C156	Detected sections match codicology (4.3x quire alignment)	2	B
C157	Circulatory reflux uniquely compatible (100%)	3	B
C158	Extended runs necessary (12.6% envelope gap)	2	B
C159	Section boundaries organizational (F-ratio 0.37)	2	B
C160	Variants are discrete alternatives (43%)	2	B
C161	Folio Ordering = Risk Gradient	2	B
C162	Aggressive programs buffered (88% vs 49% null)	2	B
C163	7 domains ruled incompatible	2	B
C164	86.7% Perfumery-Aligned Plants	2	B
C165	No Program-Morphology Correlation	2	B
C166	Uncategorized: zero forbidden seam presence (0/35)	2	HT
C167	Uncategorized: 80.7% section-exclusive	2	HT
C168	Uncategorized: single unified layer	2	HT
C169	Uncategorized: hazard avoidance 4.84 vs 2.5	2	HT
C170	Uncategorized: morphologically distinct	2	HT
C171	Only continuous closed-loop process control survives	2	B
C172	SUPERSEDED	2	HT
C173	Linguistic hypothesis EXHAUSTED	2	B
C174	Intra-role outcome divergence (CF-1=0.62, CF-2=0.34)	2	B
C175	3 process classes survive (reflux, extraction, conditioning)	2	B
C176	5 product families survive	2	B
C177	Both extraction/conditioning survive; extraction favored	2	B
C178	83 folios yield 33 operational metrics	2	B
C179	4 stable regimes (K-Means k=4, Silhouette=0.23)	2	B
C180	All 6 aggressive folios in REGIME_3	2	B
C181	3/4 regimes Pareto-efficient; REGIME_3 dominated	2	B
C182	Restart-capable = higher stability	2	B
C183	No regime dominates all axes	2	B
C184	9 pressure-induced transitions; 3 prohibited	2	B
C185	REGIME_3 = Transient Throughput	2	B
C186	No pressure-free cycles	2	B
C187	CEI manifold formalized	2	B
C188	CEI bands: R2 < R1 < R4 < R3	2	B
C189	CEI bidirectional; down-CEI easier (1.44x)	2	B
C190	LINK-CEI r=-0.7057	2	B
C191	CEI Smoothing	2	B
C192	Restart at Low-CEI	2	B
C193	Navigation WORSE than random (d=-7.33)	2	B
C194	PARTIAL codex organization (2/5)	2	B
C195	Human-track compensation NOT detected	2	B
C196	100% match EXPERT_REFERENCE archetype	2	B
C197	Designed for experts, not novices	2	B
C198	OPS CLOSED	2	B
C199	Both mineral AND botanical survive	3	B
C200	6 Product Survivors	2	B
C201	Guild-Restricted Ecosystem	2	B
C202	Goldsmith/Assayer Workshops Survive	2	B
C203	Voynich structurally exceptional	2	B
C204	OPS-R RESOLVED by SEL-F (definitional ambiguity, not formal contradiction)	2	B
C205	Residue 82% section-exclusive	2	B
C206	Sections not compressible to regimes	2	B
C207	0/18 micro-cipher tests passed	2	B
C208	Residue compatible with non-encoding dynamics	2	B
C209	Attentional pacing wins (6/8)	2	HT
C210	External alignments robust to HT removal	2	B
C211	Seasonal ordering underpowered	2	B
C212	93% plants peak May-August	2	B
C213	Opportunity-loss model supported (64.7% premature hazards)	2	B
C214	EXT-4 duration criterion INVALIDATED	2	B
C215	BOTANICAL_FAVORED (8/8 tests, ratio 2.37)	3	B
C216	Hybrid Hazard Model	2	B
C217	0 true HT near hazards	2	HT
C221	Deliberate skill practice (4/5) - NOT random mark-making	2	HT
C222	No intentional layout function	2	B
C223	Procedural fluency MIXED	2	B
C224	A coverage = 13.6% (threshold 70%)	2	A
C225	A Transition Validity = 2.1%	2	A
C226	A Has 5 Forbidden Violations	2	A
C227	A LINK Density = 3.0%	2	A
C228	A Density = 0.35x B	2	A
C229	A = DISJOINT	2	A
C230	A Silhouette = 0.049	2	A
C231	A is REGULAR but NOT GRAMMATICAL	2	A
C232	A Section-Conditioned but Class-Uniform	2	A
C233	A = LINE_ATOMIC	2	A
C234	A = POSITION_FREE	2	A
C235	8+ mutually exclusive markers	2	A
C236	A = FLAT	2	A
C237	A = DATABASE_LIKE	2	A
C238	Global Schema, Local Instantiation	2	A
C239	A/B separation = DESIGNED (0.0% cross)	2	A↔B
C240	A = NON_SEQUENTIAL_CATEGORICAL_REGISTRY	2	A
C241	daiin A-enriched (1.62x), ol B-enriched (0.24x)	2	A
C242	daiin neighborhood flip (content in A, grammar in B)	2	A
C243	daiin-ol adjacent: 16 in B, 10 in A	2	A
C244	Infrastructure reuse without semantic transfer	2	A
C245	MINIMAL vocabulary: exactly 2 tokens (daiin, ol)	2	A
C246	4 mandatory criteria for structural primitives	2	A
C247	SP-01 (daiin): affects 30.2% A, 16.5% B	2	A
C248	SP-02 (ol): affects 7.4% A, 17.7% B	2	A
C249	Scan COMPLETE: 11 candidates tested	2	A
C250	~~64.1% show repeating blocks~~	1	A
C251	Repetition is Intra-Record Only	2	A
C252	Repetition Bounded 2-6x	2	A
C253	All Blocks Unique	2	A
C254	Multiplicity does NOT interact with B; isolated from operational grammar	2	A
C255	Blocks 100% Section-Exclusive	2	A
C256	Markers at block END 60.3% (vs 44% start); marker is trailing tag (CAS-DEEP)	2	A
C257	72.6% of tokens MARKER-EXCLUSIVE; markers define distinct vocabulary domains (CAS-DEEP)	2	A
C258	3x Dominance Reflects Human Counting	2	A
C259	INVERSE COMPLEXITY: higher repetitions have MORE diverse blocks (CAS-DEEP)	2	A
C260	Section vocabulary overlap 9.7%; sections are isolated domains (CAS-DEEP)	2	A
C261	Token Order Non-Random	2	A
C262	Low Mutation Across Repetitions	2	A
C263	Section-specific ceilings: H max=5x, P max=5x, T max=6x (CAS-DEEP-V)	2	A
C264	Inverse-complexity is BETWEEN-MARKER effect (Simpson's paradox); within-marker rho<0 for all 8 markers (CAS-DEEP-V)	2	A
C265	1,123 unique marker tokens across 8 classes; 85 core tokens (freq>=10); `daiin` dominates DA (51.7%), `ol` dominates OL (32.3%) (CAS-CAT)	2	A
C266	Block vs Non-Block Entry Types	2	A
C267	Tokens are COMPOSITIONAL (PREFIX+MIDDLE+SUFFIX)	2	A→B
C267.a	**MIDDLE Sub-Component Structure** (218 sub-components reconstruct 97.8% of MIDDLEs; morphology extends to sub-MIDDLE level)	2	GLOBAL
C268	897 observed combinations	2	A→B
C269	7 Universal Suffixes	2	A
C270	Some middles are PREFIX-EXCLUSIVE (CT:-h-, DA:-i-, QO:-kch-); internal structure within classifier families (CAS-MORPH)	2	A
C271	Compositional structure explains low TTR and bigram reuse	2	A
C272	A and B on COMPLETELY DIFFERENT folios	2	A↔B
C273	Section specialization NON-UNIFORM: CT is 85.9% Section H vs OK/OL at 53-55%; at least one prefix is specialized to one product line (EXT-8)	2	A
C274	Co-occurrence UNIFORM: no prefix pair shows strong association (>1.5x) or avoidance (<0.5x) in compounds; prefixes can combine freely (EXT-8)	2	A
C275	Suffix-prefix interaction SIGNIFICANT: different prefixes have different suffix preferences; EXCLUDES prefixes being processing states (EXT-8)	2	A
C276	MIDDLE is PREFIX-BOUND	2	A
C277	SUFFIX is UNIVERSAL	2	A
C278	Three-axis HIERARCHY (PREFIX→MIDDLE→SUFFIX)	2	A→B
C279	STRONG cross-axis dependencies: all three pairwise interactions p < 10⁻³⁰⁰; axes are HIERARCHICALLY RELATED, not independent dimensions (EXT-8)	2	A
C280	Section P ANOMALY: suffix -eol is 59.7% Section P (only axis value favoring P); suggests P involves specific output form (EXT-8)	2	A
C281	Components SHARED across A and B	2	A↔B
C282	Component ENRICHMENT: CT is A-enriched (0.14x), OL/QO are B-enriched (5x/4x); -dy suffix 27x B-enriched, -or 0.45x A-enriched; usage patterns differ dramatically (EXT-8)	2	A
C283	Suffixes show CONTEXT PREFERENCE: -or (0.67x), -chy (0.61x), -chor (0.18x) A-enriched; -edy (191x!), -dy (4.6x), -ar (3.2x) B-enriched; -ol, -aiin BALANCED (EXT-9)	2	A
C284	CT in B is CONCENTRATED in specific folios (48 folios); when CT appears in B it uses B-suffixes (-edy, -dy); registry materials take operational form in procedures (EXT-9)	2	A
C285	161 BALANCED tokens (0.5x-2x ratio) serve as shared vocabulary; DA-family dominates; cross-reference points between A and B (EXT-9)	2	A
C286	Modal preference is PREFIX x SUFFIX dependent; CT consistently A-enriched across suffixes, OL consistently B-enriched; not simple suffix-determines-context (EXT-9)	2	A
C287	Repetition does NOT encode abstract quantity, proportion, or scale; remains LITERAL ENUMERATION without arithmetic semantics (EXT-9B RETRACTION)	2	A
C288	3x dominance (55%) reflects human counting bias and registry ergonomics, NOT proportional tiers; no cross-entry comparison mechanism exists (EXT-9B RETRACTION)	2	A
C289	Folio-level uniformity reflects ENUMERATION DEPTH PREFERENCE (scribal convention, category density), NOT batch scale; no reference frame for ratios (EXT-9B RETRACTION)	2	A
C290	Same composition with different counts confirms count is INSTANCE MULTIPLICITY, not magnitude; "3x here" is not comparable to "3x there" due to section isolation (EXT-9B RETRACTION)	2	A
C291	~20% have optional ARTICULATOR forms	2	A
C292	Articulators = ZERO unique identity distinctions	2	A
C293	Component essentiality hierarchy: MIDDLE (402 distinctions) > SUFFIX (13) > ARTICULATOR (0); PREFIX provides foundation (1387 base); MIDDLE is primary discriminator (CAS-POST)	2	A
C294	Articulator density INVERSELY correlates with prefix count (15% at 0-1 prefix to 4% at 6 prefixes); articulators COMPENSATE for low complexity (CAS-POST)	2	A
C295	Sections exhibit DISTINCT configurations: H=dense mixed (87% mixed, 8.2% art), P=balanced (48% exclusive, 5.1% art), T=uniform sparse (81% uniform, 2.57x mean rep) (CAS-POST)	2	A
C296	CH appears in nearly all common prefix pairs (CH+DA, CH+QO, CH+SH); functions as UNIVERSAL MIXING ANCHOR (CAS-POST)	2	A
C297	-eol is ONLY suffix concentrated in section P (55.9% vs 41.3% H); all other suffixes favor H; P has distinct suffix profile (CAS-POST)	2	A
C298	L-compound middle patterns (lch-, lk-, lsh-) function as B-specific grammatical operators; 30-135x more common in B, largely absent from A; grammar-level specialization not covered by shared component inventory (B-MORPH)	2	A
C299	Section H vocabulary dominates B procedures (76/83 = 91.6%); Section P rare (7/83 = 8.4%); Section T absent (0/83 = 0%); chi² = 127.54, p < 0.0001; A sections have NON-UNIFORM mapping to B procedure applicability (CAS-XREF)	2	A
C300	3,299 tokens (8.7%) unclassified by Currier	2	AZC
C301	AZC is HYBRID (B=69.7%, A=65.4%)	2	AZC
C302	Distinct Line Structure	2	AZC
C303	Elevated LINK Density	2	AZC
C304	27.4% Unique Vocabulary	2	AZC
C305	LABELING Signature	2	AZC
C306	Placement-coding axis established	2	AZC
C307	Placement × Morphology Dependency	2	AZC
C308	Ordered Subscripts	2	AZC
C309	Grammar-Like Placement Transitions	2	AZC
C310	Placement Constrains Repetition	2	AZC
C311	Positional Grammar	2	AZC
C312	Section × Placement Strong	2	AZC
C313	Position constrains LEGALITY not PREDICTION	2	AZC
C314	Global Illegality + Local Exceptions	2	AZC
C315	Placement-Locked Operators	2	AZC
C316	Phase-Locked Binding	2	AZC
C317	Hybrid architecture (topological + positional)	2	AZC
C318	Folio-Specific Profiles	2	AZC
C319	Zodiac Template Reuse	2	AZC
C320	S2 < S1 Ordering	2	AZC
C321	Zodiac Vocabulary Isolated	2	AZC
C322	SEASON-GATED WORKFLOW interpretation	2	AZC
C323	57.8% STATE-C terminal	2	B
C324	Section-Dependent Terminals	2	B
C325	Completion Gradient	2	B
C326	A-reference sharing within clusters: 1.31x enrichment; material conditioning is real but SOFT and OVERLAPPING (silhouette=0.018); NOT a clean taxonomy (SEL-F, Tier 2)	2	AZC
C327	Cluster 3 (f75-f84) is locally anomalous: only contiguous cluster, 70% STATE-C, highest A-ref coherence (0.294); LOCAL observation, not organizational law (SEL-F, Tier 2)	2	AZC
C328	10% corruption = 3.3% entropy increase	2	B
C329	Top 10 token removal = 0.8% entropy change	2	B
C330	Leave-one-folio-out = max 0.25% change	2	B
C331	49-class minimality WEAKENED but confirmed	2	B
C332	Kernel Bigram Ordering	2	B
C333	Kernel Trigram Dominance	2	B
C334	LINK Section Conditioning	2	B
C335	69.8% Vocabulary Integration	2	B
C336	Hybrid A-Access Pattern	2	B
C337	Mixed-Marker Dominance	2	B
C338	Marker Independence	2	B
C339	E-Class Dominance	2	B
C340	LINK-Escalation Complementarity	2	B
C341	HT-Program Stratification	2	HT
C342	HT-LINK Decoupling	2	HT
C343	A-AZC persistence independence: A-vocabulary tokens appear in 2.2x more AZC placements than AZC-only tokens (p < 0.0001); high-multiplicity A-tokens have 43% broader coverage (p = 0.001); A-registry assets persist independently of AZC legality windows; supports managed stewardship model (AAZ, Tier 2)	2	B
C344	HT-A Inverse Coupling	2	HT
C345	A folios lack thematic coherence	2	A
C346	A exhibits SEQUENTIAL COHERENCE	2	A
C347	Disjoint Prefix Vocabulary	2	HT
C348	Phase Synchrony	2	HT
C349	Extended Cluster Prefixes	2	GLOBAL
C350	HT+B Hybrids Explained	2	GLOBAL
C351	Final Classification	2	GLOBAL
C352	TRUE ORPHAN Residue	2	GLOBAL
C353	State Continuity Better Than Random	2	B
C354	HT Orientation Intact	2	B
C355	75.9% Known Prefixes at Folio Start	2	B
C356	Section Symmetry Preserved	2	B
C357	Lines 3.3x more regular than random	2	B
C358	Specific boundary tokens identified	2	B
C359	LINK Suppressed at Boundaries	2	B
C360	Grammar is LINE-INVARIANT	2	B
C361	Adjacent B folios share 1.30x more vocabulary	2	GLOBAL
C362	Regime Vocabulary Fingerprints	2	GLOBAL
C363	Vocabulary Independent of Profiles	2	GLOBAL
C364	Hub-Peripheral Structure	2	GLOBAL
C365	~~LINK tokens are SPATIALLY UNIFORM~~ **REFUTED by C805**	2	GLOBAL
C366	LINK marks GRAMMAR STATE TRANSITIONS **REVISED by C804**	2	GLOBAL
C367	Sections are QUIRE-ALIGNED (4.3x)	2	B
C368	Regime Clustering in Quires	2	B
C369	Quire Vocabulary Continuity	2	B
C370	Quire Boundaries = Discontinuities	2	B
C371	Prefixes have POSITIONAL GRAMMAR	2	GLOBAL
C372	Kernel dichotomy (100% vs <5%)	2	GLOBAL
C373	LINK affinity patterns	2	GLOBAL
C374	Section Preferences	2	GLOBAL
C375	Suffixes have POSITIONAL GRAMMAR	2	GLOBAL
C376	Suffix Kernel Dichotomy	2	GLOBAL
C377	KERNEL-LIGHT Suffixes LINK-Attracted	2	GLOBAL
C378	Prefix-Suffix Constrained	2	GLOBAL
C379	Vocabulary Varies by Context	2	GLOBAL
C380	Function is INVARIANT	2	GLOBAL
C381	Instruction Concentration	2	GLOBAL
C382	MORPHOLOGY ENCODES CONTROL PHASE	2	GLOBAL
C383	GLOBAL MORPHOLOGICAL TYPE SYSTEM	2	GLOBAL
C384	NO TOKEN-LEVEL OR CONTEXT-FREE A-B LOOKUP	2	A↔B
C384.a	CONDITIONAL RECORD-LEVEL CORRESPONDENCE PERMITTED	2	A↔B
C385	STRUCTURAL GRADIENT in Currier A	2	A
C386	Transition Suppression	2	GLOBAL
C387	QO as Phase-Transition Hub	2	GLOBAL
C388	Self-Transition Enrichment	2	GLOBAL
C389	BIGRAM-DOMINANT local determinism (H=0.41 bits)	2	GLOBAL
C390	No Recurring N-Grams	2	GLOBAL
C391	CONDITIONAL ENTROPY SYMMETRY (H(X|past)=H(X|future); constraint symmetry, not transition symmetry - see C886)	2	GLOBAL
C392	ROLE-LEVEL CAPACITY (97.2% observed)	2	GLOBAL
C393	FLAT TOPOLOGY (diameter=1)	2	GLOBAL
C394	INTENSITY-ROLE DIFFERENTIATION	2	GLOBAL
C395	DUAL CONTROL STRATEGY	2	GLOBAL
C396	AUXILIARY Invariance	2	GLOBAL
C397	qo-prefix = escape route (25-47%)	2	GLOBAL
C398	Post-Source Role Distribution (REVISED)	2	GLOBAL
C399	Safe Precedence Pattern	2	GLOBAL
C400	BOUNDARY HAZARD DEPLETION (5-7x)	2	GLOBAL
C401	Self-Transition Dominance	2	GLOBAL
C402	HIGH_IMPACT Clustering	2	GLOBAL
C403	5 PROGRAM ARCHETYPES (continuum)	2	B
C404	HT TERMINAL INDEPENDENCE	2	HT
C405	HT CAUSAL DECOUPLING (V=0.10)	2	HT
C406	HT GENERATIVE STRUCTURE (Zipf=0.89)	2	HT
C407	DA = INFRASTRUCTURE	2	GLOBAL
C408	ch-sh/ok-ot form EQUIVALENCE CLASSES	2	GLOBAL
C409	Sister pairs MUTUALLY EXCLUSIVE but substitutable	2	GLOBAL
C410	Sister choice is SECTION-CONDITIONED	2	GLOBAL
C411	Grammar DELIBERATELY OVER-SPECIFIED (~40% reducible)	2	GLOBAL
C412	ch-preference anticorrelated with qo-escape density	2	GLOBAL
C413	HT prefix phase-class predicted by preceding grammar (V=0.319)	2	HT
C414	HT STRONG GRAMMAR ASSOCIATION	2	HT
C415	HT NON-PREDICTIVITY (MAE worsens)	1	HT
C416	HT DIRECTIONAL ASYMMETRY (V=0.324 vs 0.202)	2	HT
C417	HT MODULAR ADDITIVE	2	HT
C418	HT POSITIONAL WITHOUT INFORMATIVENESS	2	HT
C419	HT POSITIONAL SPECIALIZATION IN A (entry-aligned)	2	A+HT
C420	Folio-initial position permits otherwise illegal C+vowel variants (ko-, po-, to-)	2	A
C421	Section-boundary adjacency suppression (2.42x)	2	A
C422	DA as internal articulation punctuation (75% separation)	2	A
C423	PREFIX-BOUND VOCABULARY DOMAINS (80% exclusive MIDDLEs)	2	A
C424	Adjacency coherence is clustered, not uniform	2	A
C430	**AZC Bifurcation: two folio families**	2	AZC
C431	**Zodiac Family Coherence (refines C319)**	2	AZC
C432	**Ordered Subscript Exclusivity**	2	AZC
C433	**Zodiac Block Grammar (98%+ self-transition)**	2	AZC
C434	**R-Series Strict Forward Ordering**	2	AZC
C435	**S/R Positional Division (boundary/interior)**	2	AZC
C436	**Dual Rigidity: uniform vs varied scaffolds**	2	AZC
C437	AZC Folios Maximally Orthogonal	2	AZC
C438	AZC Practically Complete Basis	2	AZC
C439	Folio-Specific HT Profiles	2	AZC
C440	Uniform B-to-AZC Sourcing	2	AZC
C441	Vocabulary-Activated Constraints	2	AZC
C442	AZC Compatibility Grouping	2	AZC
C443	Positional Escape Gradient	2	AZC
C444	A-Type Position Distribution	2	AZC
C450	HT Quire Clustering	2	HT/GLOBAL
C451	HT System Stratification (A > AZC > B density)	2	HT/GLOBAL
C452	HT Unified Prefix Vocabulary	2	HT/GLOBAL
C453	HT Adjacency Clustering (1.69x enrichment, stronger than C424)	2	HT/GLOBAL
C454	**AZC-B Adjacency Coupling FALSIFIED**	1	AZC/B
C455	**AZC Simple Cycle Topology FALSIFIED** (cycle_rank=5, CV=0.817)	1	AZC
C456	**AZC Interleaved Spiral Topology** (R-S-R-S alternation)	2	AZC
C457	**HT Boundary Preference in Zodiac AZC** (S=39.7% > R=29.5%, V=0.105)	2	HT/AZC
C458	**Execution Design Clamp vs Recovery Freedom** (CV 0.04-0.11 vs 0.72-0.82)	2	B
C459	**HT Anticipatory Compensation**	2	HT/B
C460	AZC Entry Orientation Effect	2	HT/AZC
C461	HT density correlates with MIDDLE rarity	3	A→B
C462	Universal MIDDLEs are mode-balanced	3	A→B
C466	PREFIX Encodes Control-Flow Participation	2	GLOBAL
C467	qo-Prefix is Kernel-Adjacent	2	GLOBAL
C468	AZC Legality Inheritance	2	AZC
C469	Categorical Resolution Principle	2	AZC
C470	MIDDLE Restriction Inheritance	2	AZC
C471	PREFIX Encodes AZC Family Affinity	2	AZC
C472	MIDDLE Is Primary Carrier of AZC Folio Specificity	2	AZC
C473	Currier A Entry Defines a Constraint Bundle	2	AZC
C475	MIDDLE ATOMIC INCOMPATIBILITY [DEMOTED Tier 2 → Tier 3, REFRAMED 2026-05-19]	2	A
C477	**HT Tail Correlation**	2	HT/A
C478	TEMPORAL COVERAGE SCHEDULING [REFRAMED 2026-05-19]	2	A
C479	**Survivor-Set Discrimination Scaling**	2	A+AZC+HT
C480	Constrained Execution Variability	3	A→B
C482	**Compound Input Specification**	2	A→B
C483	**Ordinal Repetition Invariance** (magnitude has no downstream effect)	2	A
C484	**A Channel Bifurcation**	2	A
C485	**Grammar Minimality** (e-operator and h->k suppression are load-bearing)	2	B
C486	Bidirectional Constraint Coherence (B behavior constrains A zone inference)	3	CROSS_SYSTEM
C487	A-Registry Memory Optimization (z=-97 vs random, 0th percentile)	3	A
C488	HT Predicts Strategy Viability	3	HT
C489	HT Zone Diversity Correlation	3	HT
C490	**Categorical Strategy Exclusion** (20.5% of programs forbid AGGRESSIVE, not gradient but prohibition)	2	B
C491	Judgment-Critical Program Axis (OPPORTUNISTIC orthogonal to caution/aggression)	3	B
C492	**PREFIX Phase-Exclusive Legality** (ct PREFIX is 0% C/S-zones, 26% P-zone, invariant)	2	A→AZC
C493	**Brunschwig Grammar Embedding** (balneum marie procedure fits with 0 forbidden violations)	2	B
C494	**REGIME_4 Precision Axis** (encodes precision-constrained execution, not intensity)	2	B
C495	**SUFFIX–REGIME Compatibility Breadth** (-r universal, -ar/-or restricted; V=0.159)	2	A→B
C496	**Nymph-Adjacent S-Position Prefix Bias (o-prefix 75%)**	2	AZC
C497	**f49v Instructional Apparatus Folio** (26 L-labels alternating 1:1 with example lines, demonstrates morphology limits)	2	A
C498	**Registry-Internal Vocabulary Track** (61.8% A-exclusive MIDDLEs: ct-prefix 5.1×, suffix-less 3×, folio-localized; don't propagate to B)	2	A
C498.a	**A∩B Shared Vocabulary Bifurcation** (154 AZC-Mediated + 114 B-Native Overlap; pipeline scope narrowed)	2	A
C498.b	**RI Singleton Population** (~977 singletons, mean 4.82 chars; functional interpretation WEAKENED - see C498.d)	2	A
C498.c	**RI Repeater Population** (~313 repeaters, mean 3.61 chars; functional interpretation WEAKENED - see C498.d)	2	A
C498.d	**RI Length-Frequency Correlation**	2	A
C499	Bounded Material-Class Recoverability (128 MIDDLEs with P(material_class) vectors; conditional on Brunschwig)	3	A
C500	Suffix Posture Temporal Pattern (CLOSURE front-loaded 77% Q1, NAKED late 38% Q4, ratio 5.69×)	3	A
C501	**B-Exclusive MIDDLE Stratification** (569 B-exclusive types: L-compounds 49, boundary closers, 80% singletons; elaboration not novelty)	2	A
C502	**A-Record Viability Filtering** (Strict interpretation: ~96/480 B tokens legal per A; 13.3% mean B folio coverage; 80% filtered)	2	A+B
C502.a	**Full Morphological Filtering Cascade** (PREFIX+MIDDLE+SUFFIX: 38 tokens legal (0.8%); MIDDLE 5.3%, +PREFIX 64% reduction, +SUFFIX 50% reduction, combined 85% beyond MIDDLE)	2	A+B
C503	**Class-Level Filtering** (MIDDLE-only: 1,203 unique patterns, 6 always-survive classes, 32.3 mean; infrastructure classes vulnerable)	2	A+B
C503.a	**Class Survival Under Full Morphology** (PREFIX+MIDDLE+SUFFIX: 6.8 mean classes (10.8%); 83.7% reduction from MIDDLE-only; ~7 classes = actual instruction budget)	2	A+B
C503.b	**No Universal Classes Under Full Morphology** (C121's 49 classes: 0 universal; Class 9 highest at 56.1%; C503's "6 unfilterable" = 10-56% coverage; MIDDLE-only claim doesn't hold under full filtering)	2	A+B
C503.c	**Kernel Character Coverage**	2	A+B
C504	**MIDDLE Function Bifurcation**	2	A+B
C505	**PP Profile Differentiation by Material Class** ('te' 16.1×, 'ho' 8.6×, 'ke' 5.1× in animal records; A-registry organization only)	2	A
C506	**PP Composition Non-Propagation**	2	A+B
C506.a	**Intra-Class Token Configuration**	2	A+B
C506.b	**Intra-Class Behavioral Heterogeneity**	2	B
C507	**PP-HT Partial Responsibility Substitution**	2	A+HT
C508	**Token-Level Discrimination Primacy**	2	A→B
C508.a	**Class-Level Discrimination Under Full Morphology**	2	A→B
C509	**PP/RI Dimensional Separability** (72 PP sets shared by records with different RI; 229 records (14.5%) share PP; 26 pure-RI, 399 pure-PP; dimensions orthogonal)	2	A
C509.a	**RI Morphological Divergence** (RI: 58.5% PREFIX, 3.96-char MIDDLE; PP: 85.4% PREFIX, 1.46-char MIDDLE; RI is MIDDLE-centric, PP is template-balanced)	2	A
C509.b	**PREFIX-Class Determinism** (Class P_xxx requires A-PREFIX 'xxx' with 100% necessity; sufficiency 72-100%; 27% mutual exclusion = PREFIX sparsity)	2	A→B
C509.c	**No Universal Instruction Set** (0 classes in ALL records; BARE highest at 96.8%; 50 records lack BARE-compatible MIDDLEs; ~7 classes = ~2.5 PREFIXes + BARE + SUFFIXes)	2	A→B
C509.d	**Independent Morphological Filtering** (PREFIX/MIDDLE/SUFFIX filter independently; 27% class ME = morphological sparsity not class interaction; SUFFIX classes 100% PREFIX-free)	2	A→B
C510	**Positional Sub-Component Grammar**	2	A
C511	**Derivational Productivity** (Repeater MIDDLEs seed singletons at 12.67x above chance; 89.8% exceed baseline)	2	A
C512	**PP/RI Stylistic Bifurcation**	2	GLOBAL
C512.a	**Positional Asymmetry** (END-class 71.4% PP; START-class 16.1% PP; pattern: RI-START + PP-FREE + PP-END)	2	A
C513	**Short Singleton Sampling Variance**	2	A
C514	**RI Compositional Bifurcation** (17.4% locally-derived, 82.6% globally-composed; Section P highest local rate 26.1%)	2	A
C515	**RI Compositional Mode Correlates with Length**	2	A
C515.a	**Compositional Embedding Mechanism** (local derivation is additive - embedding local PP context requires more sub-components)	2	A
C516	**RI Multi-Atom Observation** (99.6% multi-atom but trivially expected from lengths; intersection formula PROVISIONAL)	2	A
C517	**Superstring Compression (GLOBAL)** (65-77% overlap, 2.2-2.7x compression; hinge letters are 7/8 kernel primitives; global substrate)	3	GLOBAL
C518	**Compatibility Enrichment (GLOBAL)** (5-7x enrichment across all systems; extends C383 global type system)	3	GLOBAL
C519	**Global Compatibility Architecture** (compression + enrichment = embedded compatibility relationships spanning A/B/AZC)	3	GLOBAL
C520	**System-Specific Exploitation Gradient** (RI 6.8x > AZC 7.2x > PP 5.5x > B 5.3x; discrimination intensity varies)	3	GLOBAL
C521	**Kernel Primitive Directional Asymmetry** (one-way valve: e→h=0.00, h→k=0.22, e→k=0.27 suppressed; h→e=7.00x, k→e=4.32x elevated; stabilization is absorbing)	2	B
C522	**Construction-Execution Layer Independence**	2	B
C523	**Pharma Label Vocabulary Bifurcation**	2	A
C524	**Jar Label Morphological Compression** (7.1 vs 6.0 char mean; 5-8 PP atoms per MIDDLE; superstring packing)	2	A
C525	**Label Morphological Stratification** (o-prefix 50% vs 20% text; qo-prefix ~0% vs 14%; 61% label-only vocabulary; within-group MIDDLE sharing)	3	A
C526	**RI Lexical Layer Hypothesis** (609 unique RI as referential lexicon; 87% localized to 1-2 folios; PREFIX/SUFFIX global grammar vs RI extensions as substance anchors)	3	A
C527	**Suffix-Material Class Correlation**	3	A
C528	**RI PREFIX Lexical Bifurcation** (334 PREFIX-REQUIRED, 321 PREFIX-FORBIDDEN, 12 optional; 98.2% disjoint; PREFIX attachment lexically determined; section-independent; refines C509.a aggregate rate)	2	A
C529	**Gallows Positional Asymmetry**	2	A
C530	**Gallows Folio Specialization** (k-default 54%, t-specialized folios cluster; p/f never folio-dominant; 2-5x same-gallows co-occurrence RI↔PP in records)	2	A
C531	**Folio Unique Vocabulary Prevalence** (98.8% of B folios have ≥1 unique MIDDLE; only f95r1 lacks unique vocabulary; mean 10.5 unique MIDDLEs per folio)	2	A
C532	**Unique MIDDLE B-Exclusivity** (88% of unique B MIDDLEs are B-exclusive, not in A; 12% are PP; unique vocabulary is primarily B-internal grammar, not AZC-modulated)	2	A
C533	**Unique MIDDLE Grammatical Slot Consistency** (75% of unique MIDDLE tokens share PREFIX/SUFFIX patterns with classified tokens; adjacent folios' unique MIDDLEs fill similar slots 1.30x vs non-adjacent)	2	A
C534	Section-Specific Prefixless MIDDLE Profiles	3	A
C535	**B Folio Vocabulary Minimality**	2	A
C536	**Material-Class REGIME Invariance**	2	A->B
C537	**Token-Level Material Differentiation**	2	A->B
C538	PP Material-Class Distribution (ANIMAL 15.6%, HERB 28.0%, MIXED 16.6%, NEUTRAL 39.9%; classification conditional on Brunschwig suffix alignment)	3	A
C539	**LATE Prefix Morphological Class** (al/ar/or: V+L pattern, 3.78x line-final enrichment, 68-70% suffix-depleted, short MIDDLE preference)	2	B
C540	**Kernel Primitives Are Bound Morphemes** (k, e, h never standalone; 0 occurrences each; intervention modifiers only)	2	MORPHOLOGY
C541	**Hazard Class Enumeration** (only 6/49 classes participate in 17 forbidden transitions; 43 classes have 0% hazard involvement)	2	HAZARD_TOPOLOGY
C542	**Gateway/Terminal Hazard Class Asymmetry** (Class 30 = pure gateway, Class 31 = pure terminal; 100% asymmetry)	2	HAZARD_TOPOLOGY
C543	**Role Positional Grammar** (FLOW final-biased 0.68, CORE initial-biased 0.45; Class 40 = 69% line-final)	2	POSITIONAL_GRAMMAR
C544	**ENERGY_OPERATOR Interleaving** (qo/ch-sh families alternate with 2.5x enrichment; Class 33 self-repeat 14.6%)	2	CO-OCCURRENCE
C545	**REGIME Instruction Class Profiles** (REGIME_3 = 1.83x CORE_CONTROL; REGIME_1 = 52% qo-family; each REGIME has signature classes)	2	REGIME_INTERPRETATION
C546	**Class 40 Safe Flow Operator** (daly/aly/ary: 4.22 avg distance from hazards, 0% hazard rate, 69% line-final; safe flow alternative)	2	HAZARD_TOPOLOGY
C547	qo-Chain REGIME_1 Enrichment (1.53x enrichment, 51.4% of chains in REGIME_1; depleted in REGIME_2/3; thermal processing context)	3	B
C548	**Manuscript-Level Gateway/Terminal Envelope**	2	B
C549	**qo/ch-sh Interleaving Significance**	2	B
C550	**Role Transition Grammar** (roles self-chain: FREQ 2.38x, FLOW 2.11x, ENERGY 1.35x; FLOW-FREQ bidirectional affinity 1.54-1.73x; ENERGY avoids other roles 0.71-0.80x; phrasal role structure)	2	B
C551	**Grammar Universality and REGIME Specialization** (67% classes universal; CC most universal 0.836; ENERGY REGIME_1 enriched 1.26-1.48x; FLOW REGIME_1 depleted 0.40-0.63x; thermal/flow anticorrelation)	2	B
C552	**Section-Specific Role Profiles**	2	B
C553	**BIO-REGIME Energy Independence**	2	B
C554	**Hazard Class Clustering**	2	B
C555	**PHARMA Thermal Operator Substitution** (Class 33 0.20x depleted, Class 34 1.90x enriched in PHARMA; ~10x divergence; section-specific not REGIME-driven; ENERGY operators not interchangeable)	2	B
C556	**ENERGY Medial Concentration**	2	B
C558	**Singleton Class Structure** (only 3 singletons: Class 10/11/12; 2/3 CC classes are singletons; ~~daiin initial-biased 27.7%, ol final-biased 9.5%~~; complementary control primitives). **[PHASE_735: positional sub-claims DEMOTED Tier 3 — daiin-initial fails 5-gram null under Bonferroni, ol-final was already at-shuffle. Singleton class-structure claim (Class 10/11/12) untested by 5-gram null (wrong instrument), STANDS Tier 2.]**	2	B
C560	**Class 17 ol-Derived Control Operators** (9 tokens all PREFIX:ol + ENERGY-morph; BIO 1.72x enriched; PHARMA 0 occurrences; REGIME_3 1.90x; non-singleton CC is ol-derived)	2	B
C562	**FLOW Role Structure** (19 tokens, 4.7% corpus; final-biased 17.5%; Class 40 59.7% final, ary 100% final; PHARMA 1.38x enriched, BIO 0.83x; ENERGY inverse pattern)	2	B
C563	**AX Internal Positional Stratification**	2	B
C564	**AX Morphological-Positional Correspondence** (AX_INIT: 17.5% articulator; AX_MED: ok/ot 88.8%; AX_FINAL: prefix-light 60.9%, zero articulators; prefix family predicts position)	2	B
C565	**AX Execution Scaffold Function** (AX mirrors named role positions; 0% hazard; 1.09x self-chaining; AX_FINAL enriched R1 39.4% BIO 40.9%; structural frame not functional operations)	2	B
C566	**UN Token Resolution** (7042 UN = 30.5% of B; 74.1% hapax, 74.8% single-folio; morphologically normal; cosurvival threshold artifact; NOT a separate role)	2	B
C567	**AX-Operational MIDDLE Sharing**	2	B
C568	**AX Pipeline Ubiquity** (97.2% of A records carry AX vocabulary; 0 zero-AX B contexts; classes 21,22 always survive; AX_FINAL 100%, all subgroups 95.6%)	2	B
C569	**AX Proportional Scaling** (AX fraction 0.454 vs expected 0.455; R²=0.83; NOT pure byproduct; AX_INIT over-represented slope 0.130 vs 0.102; AX_FINAL under-represented)	2	B
C570	**AX PREFIX Derivability** (89.6% binary accuracy; PREFIX is role selector; 22 AX-exclusive prefixes; F1=0.904; same MIDDLE becomes AX or operational via PREFIX)	2	B
C571	**AX Functional Identity Resolution** (AX = PREFIX-determined default mode of pipeline vocabulary; same MIDDLEs serve as scaffold or operations; PREFIX selects role, MIDDLE carries material)	2	B
C572	**AX Class Behavioral Collapse**	2	B
C573	**EN Definitive Count: 18 Classes** (ICC-based: {8, 31-37, 39, 41-49}; resolves BCSC=11 undercount; 7211 tokens = 31.2% of B; Core 6 = 79.5%, Minor 12 = 20.5%)	2	B
C574	**EN Distributional Convergence** (k=2 silhouette 0.180; QO/CHSH identical positions, REGIME, context (JS=0.0024); but MIDDLE Jaccard=0.133, trigger chi2=134; grammatically equivalent, lexically partitioned; C276/C423 within single role)	2	B
C575	**EN is 100% Pipeline-Derived** (64 unique MIDDLEs, all PP; 0 RI, 0 B-exclusive; even purer than AX's 98.2% PP; vocabulary entirely inherited from Currier A)	2	B
C576	**EN MIDDLE Vocabulary Bifurcation by Prefix**	2	B
C577	**EN Interleaving is Content-Driven**	2	B
C578	**EN Has 30 Exclusive MIDDLEs** (46.9% of EN vocabulary; not shared with AX, CC, FL, or FQ; dedicated content subvocabulary within pipeline)	2	B
C579	**CHSH-First Ordering Bias**	2	B
C580	**EN Trigger Profile Differentiation**	2	B
C581	**CC Definitive Census** (CC={10,11,12,17}; 1023 tokens, 4.4% of B; Classes 10,11 active, 12 ghost (zero tokens per C540), 17 ol-derived per C560)	2	B
C582	**FL Definitive Census** (FL={7,30,38,40}; 1078 tokens, 4.7% of B; 4 classes confirmed vs BCSC=2; hazard pair {7,30} + safe pair {38,40})	2	B
C583	**FQ Definitive Census** (FQ={9,13,14,23}; 2890 tokens, 12.5% of B; supersedes C559's {9,20,21,23}; Classes 20,21 are AX per C563)	2	B
C584	**Near-Universal Pipeline Purity** (CC/EN/FL/FQ all 100% PP; AX 98.2% per C567; pipeline vocabulary dominates all roles; operational roles pure, scaffold near-pure)	2	B
C585	**Cross-Role MIDDLE Sharing**	2	B
C586	**FL Hazard-Safe Split**	2	B
C587	**FQ Internal Differentiation**	2	B
C588	**Suffix Role Selectivity**	2	B
C589	**Small Role Genuine Structure**	2	B
C590	**CC Positional Dichotomy**	2	B
C591	**Five-Role Complete Taxonomy**	2	B
C592	**C559 Membership Correction** (C559 used {9,20,21,23} for FQ; correct is {9,13,14,23}; C559 SUPERSEDED; downstream C550/C551/C552/C556 flagged for re-verification with corrected membership)	2	B
C593	**FQ 3-Group Structure** ({9} connector, {13,14} prefixed-pair, {23} closer; k=3 silhouette 0.68; PC1=position 64.2%, PC2=morphology 28.2%; BARE=HAZARDOUS, PREFIXED=SAFE perfect overlap)	2	B
C594	**FQ 13-14 Complete Vocabulary Bifurcation**	2	B
C595	**FQ Internal Transition Grammar**	2	B
C596	**FQ-FL Position-Driven Symbiosis**	2	B
C597	**FQ Class 23 Boundary Dominance** (29.8% final rate, 39% of FQ finals despite 12.5% token share; 12.2% initial; mean run length 1.19, 84% singletons; boundary specialist)	2	B
C598	**Cross-Boundary Sub-Group Structure** (8/10 pairs significant; FQ_CONN->EN_CHSH 1.41x, FQ_CONN->EN_QO 0.16x; sub-group routing visible across role boundaries)	2	B
C599	**AX Scaffolding Routing**	2	B
C601	**Hazard Sub-Group Concentration** (19 events from 3 source sub-groups: FL_HAZ/EN_CHSH/FQ_CONN; EN_CHSH absorbs 58%; QO never participates)	2	B
C602	**REGIME-Conditioned Sub-Role Grammar** (4/5 pairs REGIME-dependent; AX->FQ REGIME-independent; core routing invariant, magnitudes shift by REGIME)	2	B
C603	**CC Folio-Level Subfamily Prediction**	2	B
C604	**C412 REGIME Decomposition**	2	B
C605	**Two-Lane Folio-Level Validation**	2	B
C606	**CC->EN Line-Level Routing**	2	B
C607	**Line-Level Escape Prediction**	2	B
C608	**No Lane Coherence / Local Routing**	2	B
C609	**LINK Density Reconciliation** (true density 13.2%=3,047/23,096; legacy 6.6% and 38% not reproducible; LINK cuts all 5 ICC roles: AX 26.2%, EN 19.0%, CC 13.8%; 'ol' in MIDDLE 41.2%, PREFIX 28.7%)	2	B
C610	**UN Morphological Profile** (7,042 tokens=30.5% B; 2x suffix rate 77.3% vs 38.7%; 5.3x articulator rate; 79.4% PP MIDDLEs, 0% RI; 90.7% novel MIDDLEs contain PP atoms; complexity is mechanism of non-classification)	2	B
C611	**UN Role Prediction** (PREFIX assigns 99.2%; consensus 99.9%; EN 37.1%, AX 34.6%, FQ 22.4%, FL 5.9%, CC 0.0%; CC fully resolved; UN is morphological tail of EN/AX/FQ)	2	B
C612	**UN Population Structure**	2	B
C613	**AX-UN Boundary**	2	B
C614	**AX MIDDLE-Level Routing**	2	B
C615	**AX-UN Functional Integration** (2,246 AX-predicted UN route identically all subgroups p>0.1; 89.3% classified AX MIDDLEs shared; 312 truly novel MIDDLEs; combined AX = 6,098 = 26.4% of B)	2	B
C616	**AX Section/REGIME Conditioning**	2	B
C617	**AX-LINK Subgroup Asymmetry**	2	B
C618	**Unique MIDDLE Identity** (858 unique MIDDLEs are 100% UN, 99.7% hapax, MIDDLE length 4.55 vs 2.12 shared, 83.1% suffix rate, 88% B-exclusive, 95.7% contain PP atoms; morphological extreme tail of B)	2	B
C619	**Unique MIDDLE Behavioral Equivalence**	2	B
C620	**Folio Vocabulary Network**	2	B
C621	**Vocabulary Removal Impact** (removing 868 unique MIDDLE tokens: 96.2% survival, mean role shift 2.80 pp, max 7.04 pp, 1/82 folios lose ICC role; UN -2.71 pp; vocabulary minimality is type diversity, not functional necessity)	2	B
C622	**Hazard Exposure Anatomy** (43 safe classes: 23 role-excluded (20 AX + 3 CC) + 20 sub-group-excluded (16 EN + 2 FL + 2 FQ); 0 incidental; safe classes route to hazard at 24.6%; FL_SAFE line-final mean=0.811 vs hazard FL 0.546 p<0.001)	2	B
C623	**Hazard Token Morphological Profile**	2	B
C624	**Hazard Boundary Architecture**	2	B
C625	**Hazard Circuit Token Mapping**	2	B
C626	**Lane-Hazard MIDDLE Discrimination**	2	B
C627	**Forbidden Pair Selectivity** (no frequency bias rank 0.562; 0/17 reciprocal-forbidden; circuit topology explains 9/12=75%; FQ_CLOSER boundary tokens account for 3 unexplained; directional token-specific lookup table)	2	B
C628	**FQ_CLOSER Positional Segregation Test**	2	B
C629	**FQ_CLOSER Source Token Discrimination** (dy c9 restart rate 0% vs s 48.6%; forbidden sources lower hazard rate 28.2% vs 35.5%; higher EN_CHSH rate 13.1% vs 8.6%; JSD 0.219; class 23 contains restart specialists and general distributors)	2	B
C630	**FQ_CLOSER Boundary Mechanism** (25% gap resolved: dy→aiin positional, l→chol frequency artifact P(0)=0.85, dy→chey likely genuine E=1.32; s→aiin 20x over-represented dominates restart loop; class 23 not unified mechanism)	2	B
C631	**Intra-Class Clustering Census** (effective vocabulary 56 from 49 classes + 7 k=2 splits; 86% uniform; mean JSD 0.639 continuous not clustered; silhouette <0.25 in 34/36 classes; 480 types compress 8.6x)	2	B
C632	**Morphological Subtype Prediction**	2	B
C633	**Effective Vocabulary Census**	2	B
C634	**Recovery Pathway Profiling**	2	B
C635	**Escape Strategy Decomposition**	2	B
C636	**Recovery-Regime Interaction**	2	B
C637	**B MIDDLE Sister Preference**	2	B
C638	**Quire Sister Consistency**=0.362 FAIR; but CONFOUNDED with section Cramer's V=0.875; within section H quire NS p=0.665; section KW eta_sq=0.321 3.6x stronger than REGIME eta_sq=0.088)	2	B
C639	**Sister Pair Variance Decomposition** (47.1% explained adj_R2=32.3%; 52.9% UNEXPLAINED free choice; shared variance 36.4% dominates; unique: quire 3.8%, lane balance 2.7%, MIDDLE 2.6%, REGIME 1.2%, section 0.4%; clean residuals no autocorrelation)	2	B
C640	**PP Role Projection Architecture**	2	CROSS_SYSTEM
C641	**PP Population Execution Profiles**	2	CROSS_SYSTEM
C642	**A Record Role & Material Architecture**	2	CROSS_SYSTEM
C643	**Lane Hysteresis Oscillation**	2	B
C644	**QO Transition Stability**	2	B
C645	**CHSH Post-Hazard Dominance**	2	B
C646	**PP-Lane MIDDLE Discrimination**	2	A/B
C647	**Morphological Lane Signature**	2	B
C648	**LINK-Lane Independence**	2	B
C649	**EN-Exclusive MIDDLE Deterministic Lane Partition** (22/30 exclusive MIDDLEs 100% lane-specific FDR<0.05; 13 QO-only k/t/p-initial 9 CHSH-only e/o-initial; absolute not probabilistic)	2	B
C650	**Section-Driven EN Oscillation Rate**	2	B
C651	**Fast Uniform Post-Hazard QO Recovery**	2	B
C652	**PP Lane Character Asymmetry**	2	GLOBAL
C653	**AZC Lane Filtering Bias**	2	GLOBAL
C654	**Non-EN PP Lane Independence**	2	B
C655	**PP Lane Balance Redundancy**	2	B
C656	**PP Co-Occurrence Continuity**	2	A
C657	**PP Behavioral Profile Continuity** (93 eligible PP; best sil=0.237 degenerate k=2: 2 vs 91; mean JSD=0.537; lane character ARI=0.010; no discrete behavioral clusters)	2	B
C658	**PP Material Gradient** (36.2% entropy reduction as gradient not partition; NMI(pool,material)=0.129; chi2 p=0.002 V=0.392; pool 18 54% MIXED; all cross-axis NMI<0.15)	2	A
C659	**PP Axis Independence**	2	A/B
C660	**PREFIX x MIDDLE Selectivity Spectrum**	2	B
C661	**PREFIX x MIDDLE Behavioral Interaction** (within-MIDDLE between-PREFIX JSD=0.425 vs between-MIDDLE JSD=0.436; effect ratio=0.975 computed / 0.792 vs C657; PREFIX transforms behavior; ckh JSD=0.710 max)	2	B
C662	**PREFIX Role Reclassification** (mean 75% class reduction median 82%; EN PREFIX->EN class 94.1%; AX PREFIX->AX/FQ 70.8%; 50.4% of pairs reduce to <20% of MIDDLE's classes)	2	B
C663	**Effective PREFIX x MIDDLE Inventory** (1190 observed, 501 effective pairs, 1.24x expansion; best sil=0.350 k=2 vs C657 0.237; k=3 degenerate; binary EN/non-EN split)	2	B
C664	**Role Profile Trajectory**	2	B
C665	**LINK Density Trajectory**	2	B
C666	**Kernel Contact Trajectory**	2	B
C667	**Escape/Hazard Density Trajectory**	2	B
C668	**Lane Balance Trajectory**	2	B
C669	**Hazard Proximity Trajectory**	2	B
C670	**Adjacent-Line Vocabulary Coupling**	0	B
C671	**MIDDLE Novelty Shape** (front-loaded; 87.3% FL 0% BL; first-half frac=0.685 vs perm=0.653; vocabulary introduced early, reused late)	0	B
C672	**Cross-Line Boundary Grammar**	0	B
C673	**CC Trigger Sequential Independence**	0	B
C674	**EN Lane Balance Autocorrelation**	0	B
C675	**MIDDLE Vocabulary Trajectory** (minimal drift; JSD Q1-Q4=0.081 ratio=1.078; 4/135 MIDDLEs positionally biased after Bonferroni; token identity position-invariant)	0	B
C676	**Morphological Parameterization Trajectory**	0	B
C677	**Line Complexity Trajectory**	0	B
C678	**Line Profile Classification** (continuous; best KMeans sil=0.100 no discrete types; PC1=morphological complexity 12.1%; PC2=monitoring intensity 9.3%; 10 PCs for 68.3%)	0	B
C679	**Line Type Sequencing**	0	B
C680	**Positional Feature Prediction** (11/27 features position-correlated; 9/27 add beyond REGIME; line_length dR2=0.040 strongest; 16/27 position-independent)	0	B
C681	**Sequential Coupling Verdict** (24/27 features lag-1 sig; SEQUENTIALLY_COUPLED but folio-mediated not sequential; top: line_length dR2=0.098 EN dR2=0.091 LINK dR2=0.063; lines = contextually-coupled independently-assessed)	0	B
C682	**Survivor Distribution Profile**	2	A-B
C683	**Role Composition Under Filtering**	2	A-B
C684	**Hazard Pruning Under Filtering** (83.9% full elimination of all 17 forbidden transitions; mean 0.21 active; max 5; filtering = natural hazard suppression)	2	A-B
C685	**LINK and Kernel Survival Rates** (97.4% kernel union access h=95.5% k=81.0% e=60.7%; 36.5% lose all LINK tokens; monitoring capacity fragile)	2	A-B
C686	**Role Vulnerability Gradient** (FL most fragile 2.3% at 0-2 PP; FQ most resilient 13.5%; vulnerability ordering FL>EN>AX>CC>FQ; all roles >0% in all PP bins)	2	A-B
C687	**Composition-Filtering Interaction**	2	A-B
C688	**REGIME Filtering Robustness** (REGIME_2 most robust 0.222; REGIME_3 least 0.167; REGIMEs 1/2/4 clustered ~0.21; filtering severity A-record-driven not REGIME-driven)	2	A-B
C689	**Survivor Set Uniqueness**	2	A-B
C690	**Line-Level Legality Distribution**	2	A-B
C691	**Program Coherence Under Filtering** (0-20% operational completeness; work group survives best up to 87%; close group is bottleneck; max gap = entire folio for most records)	2	A-B
C692	**Filtering Failure Mode Distribution** (94.7% MIDDLE miss, 3.6% PREFIX, 1.7% SUFFIX; consistent across all roles 91-97% MIDDLE; MIDDLE = gatekeeper)	2	A-B
C693	**Usability Gradient** (266x dynamic range; best=0.107 Max-classes; 78% pairings unusable >50% empty; single A record does NOT produce usable B program)	2	A-B
C694	**RI Placement Non-Random**	2	A
C696	**RI Line-Final Preference**	2	A
C698	**Bundle-C424 Size Match** (INFORMATIONAL; bundles and C424 adjacency clusters are distinct constructs; KS p < 0.001)	2	A
C700	**Bundle PP Exceeds Random**	2	A
C702	**Boundary Vocabulary Discontinuity**	1	A
C704	**Folio PP Pool Size** (mean 35.3 MIDDLEs per folio, 7.0x record-level; range 20-88; folio = complete PP specification)	2	A
C706	**B Line Viability Under Folio Filtering** (13.7% empty lines vs 78% record-level; 76.3% pairings have <=20% empty)	2	A-B
C708	**Inter-Folio PP Discrimination**	2	A-B
C709	**Section Invariance** (all sections H/P/T 100% viable; P=0.182, T=0.293 higher than H=0.085; no dead zones)	2	A-B
C710	**RI-PP Positional Complementarity** (d=0.12, RI slightly later in lines; effect too small for structural complementarity)	2	A
C712	**RI Singleton-Repeater Behavioral Equivalence**	2	A
C714	**Line-Final RI Morphological Profile** (143 unique types in 156 final positions; no morphological difference from non-final RI)	2	A
C716	**Cross-Folio RI Reuse Independence**	2	A
C717	**PP Homogeneity Across Line Types** (PP-pure and RI-bearing lines draw from same PP pool; RI-exclusive PP is sampling artifact, null=9.4 vs obs=8.9, 106% explained; PP-pure alone recovers 90.1% of B class survival)	2	A
C719	**RI-PP Functional Independence** (0/6 binding tests pass; shared RI does not predict PP similarity J=0.074 vs 0.065, PP consistency ratio 1.05, adjacent PP ratio 0.99; RI and PP are orthogonal discrimination axes)	2	A
C721	**RI Section Sharing Trivial** (76.6% within-section vs 71.5% expected from section sizes; enrichment 1.07x trivially explained by 95/114 folios being Herbal)	2	A
C722	**Within-Line Accessibility Arch**	2	A-B
C723	**Role Accessibility Hierarchy**	2	A-B
C724	**Within-Class Suffix Accessibility Gradient**	2	A-B
C725	**Across-Line Accessibility Gradient**	2	B
C726	**Role-Position Accessibility Interaction** (aggregate arch decomposes into role-specific trajectories; CC/AX increase toward final, EN/FQ decrease; non-unanimous but morphologically explained by C590/C564 composition effects)	2	A-B
C727	**B Vocabulary Autonomy Rate** (69.3% of B token types have low-or-zero accessibility from A; 34.4% completely B-exclusive; 0% universally legal; B's structural scaffold is autonomously determined)	2	A-B
C728	**PP Co-occurrence Incompatibility Compliance**	2	A
C729	**C475 Record-Level Scope** (MIDDLE incompatibility operates perfectly at A record level; 0 violations across 19,576 pair occurrences; 15,518 within-folio avoidance pairs never appear on same line; extends C475 from AZC to A)	2	A
C730	**PP PREFIX-MIDDLE Within-Line Coupling**	2	A
C731	**PP Adjacent Line Continuity**	2	A
C732	**PP Within-Line Selection Uniformity**	2	A
C733	**PP Token Variant Line Structure**	2	A
C734	**A-B Coverage Architecture** (per-A-folio C502.a coverage of B folios: mean 26.1%, range 2.6-79.3%; A folio identity explains 72.0% of variance, B folio 18.1%; routing architecture, not flat)	2	A<>B
C735	**Pool Size Coverage Dominance**	2	A<>B
C736	**B Vocabulary Accessibility Partition** (0 B tokens universally legal; 34.4% never legal under any A folio; median accessibility 3 A folios; tripartite: B-exclusive 34.4%, narrow-access 33.9%, broad-access 31.7%)	2	A<>B
C737	**A-Folio Cluster Structure**	2	A<>B
C738	**Union Coverage Ceiling** (all 114 A folios combined reach ~83-89% B folio coverage, never 95%; 34.4% of B vocabulary permanently B-exclusive; represents B's autonomous grammar)	2	A<>B
C739	**Best-Match Specificity**	2	A<>B
C740	**HT/UN Population Identity** (HT = UN: 4,421 types, 7,042 occ, zero delta; both defined by exclusion from 479-type grammar)	2	B/HT
C741	**HT C475 Minimal Graph Participation** (4.6% of HT MIDDLE types in C475 graph, but 38.5% of occurrences; 95.4% too rare to test)	2	B/HT
C742	**HT C475 Line-Level Compliance** (0.69% violation rate vs 0.63% classified baseline; z=+1.74 marginal; compliance by structural sparsity)	2	B/HT
C743	**HT Lane Segregation**	2	B/HT
C744	**HT Lane Indifference** (same-lane rate 37.7% = expected 37.9%, lift=0.994x; z=-1.66 ns; HT is lane-neutral in placement)	2	B/HT
C745	**HT Coverage Metric Sensitivity**	2	A<>B/HT
C746	**HT Folio Compensatory Distribution**	2	B/HT
C747	**Line-1 HT Enrichment**	0	B/HT
C748	**Line-1 Step Function** (pos 1=50.2%, pos 2=31.7%, pos 3-10=27-33%; enrichment confined to single opening line)	0	B/HT
C749	**First-Line HT Morphological Distinction**	2	B/HT
C750	**Opening-Only HT Asymmetry**	0	B/HT
C751	**Coverage Pool-Size Confound**	2	A<>B
C752	**No Section-to-Section Routing**	2	A<>B
C753	**No Content-Specific A-B Routing** (partial r=-0.038 after size control; no granularity achieves discrimination; reframe as constraint propagation)	2	A<>B
C754	**Role-Aware Infrastructure Filtering**	2	A<>B
C755	**[DEMOTED Tier 2→3 2026-05-19]** Originally "A Folio Coverage Homogeneity" Tier 2. Measurement survives (real A folios at 0th percentile vs synthetic for discrimination, mean 1.064 vs 1.281). Interpretation as "deliberate coverage optimization" demoted because inherits from retracted C476. Same "real worse than random reframed as deliberate" pattern that broke C476. Batch-sweep `phases/BATCH_SWEEP_2026_01_12/`.	3	A
C756	**[DEMOTED Tier 2→3 2026-05-19]** Originally "Coverage Optimization Confirmed" Tier 2. 11× pairwise similarity likely has broken-baseline issue (random PP vocab doesn't represent meaningful alternative). Hub-MIDDLE structural observation (25 MIDDLEs in >50% folios, 100% PP) survives as descriptive. "Coverage optimization confirmed" headline inherits from retracted C476. Batch-sweep `phases/BATCH_SWEEP_2026_01_12/`.	3	A
C757	**AZC Zero Kernel/Link** (0 KERNEL, 0 LINK; ~50% OPERATIONAL, ~50% UN; AZC is outside execution layer)	2	AZC
C758	**P-Text Currier A Identity** (PREFIX cosine 0.97 to A, 0.74 to diagram; 19.5% MIDDLE overlap with same-folio diagram)	2	AZC
C759	**AZC Position-Vocabulary Correlation**	2	AZC
C760	**AZC Folio Vocabulary Specialization** (70% MIDDLEs exclusive to 1 folio; 13 universal MIDDLEs; no family pattern)	2	AZC
C761	**AZC Family B-Coverage Redundancy**	2	AZC
C762	**Cross-System Single-Char Primitive Overlap** (f49v/f76r/f57v share 4 chars d,k,o,r - all C085 primitives; spans PREFIX/MIDDLE/SUFFIX positions)	2	GLOBAL
C763	**f57v R2 Single-Char Ring Anomaly** (100% single chars, 0% morphology; ~27-char repeating pattern with p/f variation; m,n unique terminators; diagram-integrated unlike margin labels)	2	AZC
C764	**f57v R2 Coordinate System** (UNIQUE to f57v across 13 Zodiac folios; p/f at 27-pos apart mark ring halves; R1-R2 1:1 token correspondence; 'x' coord-only char never in R1)	2	AZC
C765	**AZC Kernel Access Bottleneck** (AZC-mediated: 31.3% escape, 51.3% kernel; B-native: 21.5% escape, 77.8% kernel; AZC constrains B by limiting kernel access, not escape directly)	2	GLOBAL
C766	**UN = Derived Identification Vocabulary** (UN 81.1% compound vs classified 35.2%; +45.9pp; 1,251 UN-only MIDDLEs at 84.3% compound; 0 classified-only MIDDLEs)	2	B
C767	**Class Compound Bimodality** (21 base-only classes at 0-5% compound, 3 compound-heavy classes at 85%+; grammar has two functional vocabularies)	2	B
C768	**Role-Compound Correlation** (FL=0% compound, FQ=46.7%; 46.7pp spread; FL uses 0 kernel chars k/h/e; role determines vocabulary type)	2	B
C769	**Compound Context Prediction**	2	B
C770	**FL Kernel Exclusion** (FL uses 0 kernel chars k/h/e; only role with complete kernel exclusion; 17 MIDDLEs, 1,078 tokens)	2	B
C771	**FL Character Restriction** (FL uses exactly 9 chars: a,d,i,l,m,n,o,r,y; excludes c,e,h,k,s,t; mean MIDDLE length 1.58)	2	B
C772	**FL Primitive Substrate** (FL provides substrate layer; other roles add kernel k/h/e then helpers c/s/t; EN 60.7% kernel-containing highest)	2	B
C773	**FL Hazard-Safe Position Split** (Hazard FL 88.7% at mean pos 0.546 medial; Safe FL 11.3% at mean pos 0.811 line-final; 0.265 position gap)	2	B
C774	**FL Outside Forbidden Topology** (FL classes not in any of 17 forbidden pairs; FL operates below hazard layer)	2	B
C775	**Hazard FL Escape Driver** (Hazard FL 7/30 drive 98% of FL->FQ; safe FL 38/40 drive 2%; FL->FQ rate 22.5%)	2	B
C776	**Post-FL Kernel Enrichment** (59.4% of post-FL tokens have kernel chars k/h/e; confirms FL -> kernel-modulated flow pattern)	2	B
C777	**FL State Index** (FL MIDDLEs index material state; 'i'-forms at start (0.30), 'y'-forms at end (0.94); position range 0.64; 77% state change rate)	2	B
C778	**EN Kernel Profile** (EN 91.9% kernel; dominant h+e (35.8%); h=59.4%, e=58.3%, k=38.6%; phase/stability operator not energy)	2	B
C779	**EN-FL State Coupling** (EN 'h' rate drops 95%->77% as FL advances early->late; early states need phase management, late states stable)	2	B
C780	**Role Kernel Taxonomy**	2	B
C781	**FQ Phase Bypass** (FQ has exactly 0% 'h'; escape routes bypass phase management using k+e only)	2	B
C782	**CC Kernel Paradox** (Classes 10,11=0% kernel, class 17=88%; CC bifurcates into hazard sources vs hazard buffers)	2	B
C783	**Forbidden Pair Asymmetry** (All 17 forbidden pairs are asymmetric/directional; 0 symmetric; hazard is directed graph)	2	B
C784	**FL/AX Hazard Immunity** (FL and AX never appear in any forbidden pair; exempt from hazard topology)	2	B
C785	**FQ Medial Targeting** (FQ->FL routes to MEDIAL at 77.2%; escape re-injects at mid-process, not start/end)	2	B
C786	**FL Forward Bias** (FL state transitions: 27% forward, 68% same, 5% backward; 5:1 forward:backward ratio)	2	B
C787	**FL State Reset Prohibition** (LATE->EARLY transition = 0 occurrences; full state reset is forbidden)	2	B
C788	**CC Singleton Identity** (Class 10=daiin, Class 11=ol, Class 12=k(absent), Class 17=9 ol- tokens; CC classes are specific tokens not broad categories)	2	B
C789	**Forbidden Pair Permeability** (34% of CC->FQ transitions violate forbidden pairs; forbidden = disfavored, not prohibited)	2	B
C790	**CC Positional Gradient**	2	B
C791	**CC-EN Dominant Flow** (CC->EN at 33% vs CC->FQ at 12%; CC primarily routes to kernel ops, not escape)	2	B
C792	**B-Exclusive = HT Identity** (100% of B-exclusive vocabulary is HT/UN; 0 classified tokens are B-exclusive; all 88 classified MIDDLEs are in PP; C736's "autonomous grammar" is HT layer, not classified)	2	A<>B/HT
C793	**Residual Specificity = Vocabulary Coincidence** (the 24 residual-best A folios are those with best sample of common PP MIDDLEs; f42r dominates via 8 near-universal MIDDLEs; no content routing)	2	A<>B
C794	**Line-1 Composite Header Structure** (68.3% PP for A-context declaration, 31.7% B-exclusive for folio ID; PP predicts A at 15.8x random; B-exclusive 94.1% folio-unique)	2	B/A<>B
C795	**Line-1 A-Context Prediction** (PP line-1 HT predicts best-match A folio: 13.9% correct vs 0.88% random baseline, lift=15.8x)	2	A<>B
C796	**HT-Escape Correlation**	2	B/HT
C797	**AZC-HT Inverse Relationship**	2	A<>B/HT
C798	**HT Dual Control Architecture** (AZC and FL are orthogonal predictors of HT; effects additive; quadrant range 25%-37% HT)	2	GLOBAL/HT
C799	**Line-1 AZC Independence** (Line-1 PP fraction and A-context prediction accuracy do NOT vary by AZC tertile; header is fixed structure)	2	B/HT
C800	**Body HT Escape Driver**	2	B/HT
C801	**Body HT Primitive Vocabulary**	2	B/HT
C802	**Body HT LINK Proximity**	2	B/HT
C803	**Body HT Boundary Enrichment** (HT rate: first=45.8%, last=42.9%, middle=25.7%; marks control block boundaries)	2	B/HT
C804	**LINK Transition Grammar Revision**	2	B
C805	**LINK Positional Bias (C365 Refutation)** (Mean pos 0.476 vs 0.504; first=17.2%, last=15.3%, middle=12.4%; shares HT boundary pattern)	2	B
C806	**LINK-HT Positive Association**	2	B/HT
C807	**LINK-FL Inverse Relationship**	2	B
C808	**LINK 'ol' is PP MIDDLE** ('ol' appears 759x as MIDDLE, in A vocabulary; LINK PP rate 92.4%)	2	B
C809	**LINK-Kernel Separation**	2	B
C810	**LINK-FL Non-Adjacency** (Direct LINK->FL rare: 0.70x expected; confirms complementary phases)	2	B
C811	**FL Chaining** (FL->FL enriched 2.11x; extended escape sequences; FL->KERNEL neutral 0.86x)	2	B
C812	**HT Novel MIDDLE Combinations** (11.19% novel pairs; NOT C475 violation; HT in distinct combinatorial space)	2	B/HT
C813	**Canonical Phase Ordering** (LINK 0.476 -> KERNEL 0.482 -> FL 0.576; monitoring early, escape late)	2	B
C814	**Kernel-Escape Inverse**	2	B
C815	**Phase Position Significance**	2	B
C818	**CC Kernel Bridge** (Class 17 = CC-KERNEL interface; 88% kernel chars; resolves C782 paradox) **[PHASE_735: composition claim, not sequential — correctly excluded from 5-gram audit; UNTOUCHED Tier 2]**	2	B
C820	**CC Hazard Immunity** (0/700 forbidden; EN absorbs 99.8% hazard; CC is safe control layer)	2	B
C821	**Line Syntax REGIME Invariance** (All 5 roles invariant; eta^2=0.13%; confirms C124 universality)	2	B
C822	**CC Position REGIME Invariance**	2	B
C823	**Bigram REGIME Partial Variation**	2	B
C824	**A-Record Filtering Mechanism** (81.3% filtering confirms C502; aggregation helps usability)	2	A/B
C825	**Continuous Not Discrete Routing** (silhouette=0.124; no discrete clusters; 97.6% unique profiles)	2	A/B
C826	**Token Filtering Model Validation**	2	A/B
C827	**Paragraph Operational Unit** (gallows-initial paragraphs: 31.8% survival, 2.8x better than lines)	2	A/B
C828	**PP Repetition Exclusivity**	2	A
C829	**daiin Repetition Dominance** (22% of all repeats; CC trigger may encode control-loop cycle count)	2	A
C830	**Repetition Position Bias** (late-biased 0.675; FINAL 12x higher than INITIAL; parameters follow identity)	2	A
C831	**RI Three-Tier Population Structure** (singletons 95.3%, position-locked ~4%, linkers 0.6%)	2	A
C832	**Initial/Final RI Vocabulary Separation**	2	A
C833	**RI First-Line Concentration** (1.85x in paragraph first line; 1.03x at folio level - no structure)	2	A
C834	**Paragraph Granularity Validation** (RI structure visible ONLY at paragraph level; validates record size)	2	A
C835	**RI Linker Mechanism** (4 tokens, 12 links, 12 folios; 66.7% forward flow; f93v=5 inputs collector)	2	A
C838	**qo-Linker Exception** (qokoiiin doesn't follow ct-ho; may be different linkage mechanism)	2	A
C839	**RI Input-Output Morphological Asymmetry** (12+ INPUT markers vs 5 OUTPUT markers; -ry strongest OUTPUT)	2	A
C840	**B Paragraph Mini-Program Structure**	2	B
C841	**B Paragraph Gallows-Initial Markers**	2	B
C842	**B Paragraph HT Step Function** (pos 1=45.2%, pos 2=26.5%, pos 3-5+=26-27%; -18.7pp drop at line 2; body flat)	2	B
C843	**B Paragraph Prefix Markers** (pch- 16.9% + po- 16.6% = 33.5% of initiators; 78-86% HT; paragraph identification vocabulary)	2	B
C844	**Folio Line 1 Double-Header** (50.2% HT = folio header + paragraph 1 header overlap; mid-folio paragraphs 43.6% HT)	2	B
C845	**B Paragraph Self-Containment** (no inter-paragraph linking; 7.1% both-position rate vs A's 0.6%; no ct-ho signature; symmetric topology)	2	B
C846	**A-B Paragraph Pool Relationship**	2	A<>B
C847	**A Paragraph Size Distribution**	2	A
C848	**A Paragraph RI Position Variance**	2	A
C849	**A Paragraph Section Profile**	2	A
C850	**A Paragraph Cluster Taxonomy** (5 clusters: short-RI 34%, long-linker 8%, standard 58%; silhouette=0.337)	2	A
C851	**B Paragraph HT Variance Validation** (delta +0.134; 76.8% positive; line 1 = 46.5% HT; validates C840)	2	B
C852	**B Paragraph Section-Role Interaction**	2	B
C853	**B Paragraph Cluster Taxonomy** (5 clusters: single-line 9%, long-EN 10%, standard 81%; silhouette=0.237)	2	B
C854	**A-B Paragraph Structural Parallel**	2	A<>B
C855	Folio role template (role cohesion 0.831)	2	B
C856	Vocabulary distribution (Gini 0.279, distributed)	2	B
C857	First paragraph ordinariness (predicts 11.8%)	2	B
C858	Paragraph count reflects complexity (rho 0.836)	2	B
C859	Vocabulary convergence (14%→39% overlap)	2	B
C860	Section paragraph organization (HERBAL 2.2 vs RECIPE 10.2)	2	B
C861	LINK/hazard paragraph neutrality (CV < 0.21)	2	B
C862	Role template verdict: hybrid model	2	B
C863	Paragraph-ordinal EN subfamily gradient (qo-early, ch-late)	3	B
C864	Gallows paragraph marker (81.5% gallows-initial)	2	B
C865	Gallows folio position (k/f front-biased, p/t distributed)	2	B
C866	Gallows morphological patterns (k uses e, f often bare)	2	B
C867	P-T transition dynamics (p stable 54%, t returns to p 50%)	2	B
C868	Gallows-QO/CHSH independence (0.3% variance explained)	2	B
C869	Gallows functional model (f/k openers, p/t modes)	3	B
C870	Line-1 HT folio specificity (86% singletons, 1229 Line-1-only)	2	HT
C871	HT role cooccurrence pattern (enriched FL, depleted CC/FQ)	2	HT
C872	HT discrimination vocabulary interpretation	3	HT
C873	Kernel positional ordering: e (0.404) < h (0.410) < k (0.443)	3	B
C874	CC token functions: daiin=init (0.370), ol=continue (0.461)	3	B
C875	Escape trigger grammar: 80.4% from hazard FL stages	3	B
C876	LINK checkpoint function (position 0.405, routes to EN)	3	B
C877	Role transition grammar: EN->EN 38.5%, CC->EN 37.7%, FQ->EN 29.5%	2	B
C878	Section program variation: BIO high EN, HERBAL_B high FL/FQ	2	B
C879	Process domain: batch processing, 59.2% forward bias	3	B
C880	Integrated control model: batch processing with escape handling	3	B
C881	A Record Paragraph Structure (paragraphs not lines; RI in first line 3.84x baseline)	2	A
C882	PRECISION Kernel Signature (ESCAPE+AUX shows k+e 3x baseline, suppressed h)	2	A
C883	Handling-Type Distribution Alignment (66% CAREFUL matches 60% Brunschwig degree-2)	3	A
C884	PRECISION-Animal Correspondence (6 paragraphs pass kernel validation as animal candidates)	3	A
C885	A-B Vocabulary Correspondence (A folios provide 81% coverage for B paragraphs; single A paragraphs insufficient at 58%)	2	A-B
C886	Transition Probability Directionality (P(A→B) uncorrelated with P(B→A), r=-0.055; symmetric constraints but directional execution)	2	B
C887	WITHOUT-RI Backward Reference (1.23x backward/forward asymmetry; highest overlap 0.228 when following WITH-RI)	2	A
C888	Section-Specific WITHOUT-RI Function (H: ct 3.87x cross-ref; P: qo/ok/ol safety protocols)	2	A
C889	ct-ho Reserved PP Vocabulary (MIDDLEs h/hy/ho 98-100% ct-prefixed; extends C837 to PP level)	2	A
C890	Recovery Rate-Pathway Independence (FQ rate and post-FQ kernel vary independently; extends C458)	2	B
C891	ENERGY-FREQUENT Inverse Correlation	2	B
C892	Post-FQ h-Dominance (h 24-36% post-FQ vs e 3-8%; recovery enters via phase-check)	2	B
C893	Paragraph Kernel Signature Predicts Operation Type	2	B
C894	REGIME_4 Recovery Specialization Concentration	2	B
C895	Kernel-Recovery Correlation Asymmetry (k-FQ: r=+0.27; h-FQ: r=-0.29; e-FQ: n.s.; phase monitoring substitutes for recovery)	2	B
C896	Process Mode Discrimination via Kernel Profile (HIGH_K_LOW_H=2.5x FQ; discriminates distillation from boiling/decoction)	3	B
C897	Prefixed FL MIDDLEs as Line-Final State Markers (tokens contain FL TERMINAL MIDDLEs am/y/dy/ly per C777; 72.7% line-final; operation→state mapping extends FL state index)	2	B
C898	A PP Internal Structure	2	A
C899	A-B Within-Line Positional Correspondence	2	A↔B
C900	**AZC P-Text Annotation Pages** (f65v/f66v are 100% P-text, linguistically A (0.941 cosine), flanking f66r zodiac; 60%+ vocabulary overlap confirms annotation role)	2	AZC
C901	**Extended e Stability Gradient** (e→ee→eee→eeee forms stability depth continuum; quadruple-e in 11 folios concentrated late Currier A; odeeeey = maximum observed)	2	A
C902	**Late Currier A Register** (f100-f102 show distinct characteristics: p/f-domain concentration, extended vowels, short lines, MONSTERS; suggests appendix/addendum content)	2	A
C903	**Prefix Rarity Gradient** (Common ch/sh/qo vs rare ct vs very-rare qk (9 folios) vs extremely-rare qy (3 folios); rarity correlates with specialization)	2	A
C904	**-ry Suffix S-Zone Enrichment (3.18x; cross-validates C839 OUTPUT marker)**	2	AZC
C905	**FL_TERMINAL Early-Line Concentration**	2	B
C906	**Vowel Primitive Suffix Saturation** (Vowel MIDDLEs a/e/o + END-class suffix = closed compound that suppresses further suffixation; e→98.3% suffix, edy→0.4% suffix; explains 38% of unmapped tokens)	2	GLOBAL
C907	**-hy Consonant Cluster Infrastructure** (Tokens with -hy suffix form formulaic class: ch/sh prefix + consonant cluster MIDDLE + hy; 910 tokens (3.9%); connector hypothesis FALSIFIED - 0.99x boundary enrichment)	4	B
C908	**MIDDLE-Kernel Correlation** (55% of MIDDLEs significantly correlate with kernel profile; k-MIDDLEs→HIGH_K, e-MIDDLEs→HIGH_E, ch/sh→HIGH_H)	2	B
C909	**Section-Specific MIDDLE Vocabularies** (96% of MIDDLEs section-specific; B=k-energy, H=k+h mixed, S=e-stability, T=h-monitoring, C=infrastructure)	2	B
C910	**REGIME-MIDDLE Clustering** (67% REGIME-specific; REGIME_4 precision shows extreme enrichment: m=7.24x, ek=3.79x, y=2.57x)	2	B
C911	**PREFIX-MIDDLE Compatibility Constraints** (PREFIX selects MIDDLE family; qo→k-family 4.6x, da→infra 12.8x, ch/sh→e-family 2-3x; 102 forbidden combinations)	2	B
C912	**Precision Vocabulary - dam Token** (m MIDDLE 7.24x in REGIME_4; appears as `dam` 55% of cases; da- anchor prefix + no suffix; precision anchoring marker)	2	B
C913	**RI Derivational Morphology** (90.9% of RI MIDDLEs contain PP as substring; extensions 71.6% single-char; 53% suffix, 47% prefix; position preferences: 'd' 89% suffix, 'h' 79% prefix, 'q' 100% prefix)	2	A
C914	**RI Label Enrichment** (RI 3.7x enriched in labels (27.3%) vs text (7.4%); labels identify specific illustrated items requiring instance-specific vocabulary from PP+extension system)	2	A
C915	**Section P Pure-RI Entries** (83% of pure-RI first-line paragraphs in Section P; 23/24 single-line; mean para 7.7; da/ot/sa prefixes NOT ct-; distinct from linker system)	2	A
C916	**RI Instance Identification System** (RI functions as instance identification via PP+extension derivation; PP=category, RI=specific instance; explains A as index bridging B procedures to specific applications; labels 3.7x RI-enriched for illustration identification)	2	A
C917	**Extension-Prefix Operational Alignment**	2	A↔B
C918	**Currier A as Operational Configuration Layer** (A provides context-specific material variants via RI=PP+extension; extensions encode operational context: h=monitoring, k=energy, t=terminal, d=transition; A parameterizes B's generic procedures)	2	A↔B
C919	**d-Extension Suffix Exclusion** (d-extension categorically excludes -y suffix family: 0% rate vs 46-83% for all other extensions; takes -iin/-al instead; indicates END-class grammatical behavior)	2	A
C920	**f57v R2 Extension Vocabulary Overlap** (92% of R2 chars are extension characters; only 'x' non-extension per C764; 'h' categorically absent)	2	AZC
C921	**f57v R2 Twelve-Character Period** (exact 12-char period with 4 cycles + 2-char terminal; 10/12 positions invariant; only positions 7-8 variable: k/m and f/p)	2	AZC
C922	**Single-Character AZC Ring h-Exclusion**	2	AZC
C923	**Label Extension Bifurcation (r/h Axis)**	2	A
C924	**HT-RI Shared Derivational Morphology** (HT MIDDLEs 97.9% contain PP; 15/16 extension chars overlap with RI; same derivational system, different PREFIX layer; HT_PREFIX + [PP+ext] vs A/B_PREFIX + [PP+ext])	2	GLOBAL
C925	**B Vocabulary Morphological Partition** (B-exclusive 66% has kernel density ~1.0; RI bases 20% have density 0.76; A's RI derivation draws selectively from lower-density subset; morphological not semantic partition per C522)	2	B, A↔B
C926	**HT-RI Line-Level Anti-Correlation**	2	A
C927	**HT Elevation in Label Contexts**	2	A, HT
C928	**Jar Label AX_FINAL Concentration**	2	A, B, Labels
C929	**ch/sh Sensory Modality Discrimination** (ch=active test pos 0.515, sh=passive monitor pos 0.396, delta +0.120; ch+checkpoint suffix 1.87x; sh followed by heat 18.3% vs ch 10.6%; ch followed by input 1.98x, iterate 2.01x; maps to Brunschwig continuous monitoring vs discrete sampling)	2	B
C930	**lk Section-S Concentration and Fire-Method Specificity**	2	B
C931	**Prefix Positional Phase Mapping** (pch 15.9x, tch 18.4x line-initial; ol 0.33x, lch 0.32x, ot 0.29x line-final; pch 25.5x par-initial; qo/ch 0.03-0.13x par-initial; temporal ordering PREP->PRE-TREAT->SEAL->EXECUTE->POST->STORE matches Brunschwig 7-phase workflow)	2	B
C932	**Body Vocabulary Gradient** (RARE r=-0.97 early-to-late; UNIVERSAL r=+0.92; tokens/line 10.3->8.7 r=-0.97; terminal suffix r=-0.89; bare suffix r=+0.90; extends C842 flat-body finding to show vocabulary rarity gradient within body)	2	B
C933	**Prep Verb Early Concentration** (te avg=0.394 Q0:Q4=2.7x; pch avg=0.429 Q0:Q4=2.8x; tch avg=0.424 Q0:Q4=1.9x; lch avg=0.445 Q0:Q4=1.3x; all four Brunschwig prep verbs front-load in paragraph body)	2	B
C934	**Parallel Startup Pattern** (heat first 65%, prep first 27%, same line 8%; first heat avg pos=0.079, first prep avg pos=0.212; BOTH lines Q0=9.9% Q4=3.4% r=-0.94; consistent with "light coals first, prep materials while stabilizing")	2	B
C935	**Compound Specification Dual Purpose** (line-1 compound atoms predict body simple MIDDLEs: 71.6% hit vs 59.2% random, 1.21x lift; HT compound rate 45.8% vs grammar 31.5%; 100% decomposable to core atoms; REVISES C404 "non-operational" to "operationally redundant"; weakens Tier 3 attention/practice interpretation)	2	B
C937	**Rare MIDDLE Zone-Exclusivity**	2	B
C938	**Section-Specific Tail Vocabulary**	2	B
C939	**Zone-Exclusive MIDDLEs Are Compositional Variants**	2	B
C940	**FL State Marking via Rare MIDDLEs FALSIFIED**	1	B
C941	**Section Is the Primary Vocabulary Organizer**	2	B
C942	**Context-Dependent MIDDLE Successor Profiles** (45.8% significant by section after Bonferroni; section KL 2.0x > position KL; 100% MIDDLEs have section KL > position KL)	2	B
C943	**Whole-Token Variant Coordination Carries Section Signal**	2	B
C944	**Paragraph Kernel Sequence Stereotypy**	2	B
C945	**No Folio-Persistent Rare MIDDLEs as Material Markers FALSIFIED** (0 rare MIDDLEs at >80% persistence; 81.8% confined to single paragraph; mean edit distance 1.33)	1	B
C946	**A Folios Show No Material-Domain Routing FALSIFIED** (cosine similarity 0.997; ARI=-0.007; RI extension V=0.071; A is generic pool)	1	A
C947	**No Specification Vocabulary Gradient FALSIFIED**	1	B
C948	**Gloss Gap Paragraph-Start Enrichment** (4.03x at par_start; section H gap rate 8.6% vs B 2.4%; 16 distinct gaps all hapax)	2	B
C949	**FL Non-Executive Verdict** (6-test battery; variant NMI 97.1th pctile but fails 99.9th threshold; FL is deliberately low-impact ordered annotation layer, non-executive)	2	B
C950	**FL Two-Dimensional Structure**	2	B
C951	**FL-LINK Spatial Independence**	2	B
C952	**FL Stage-Suffix Global Independence**	2	B
C953	**ch-FL Precision Annotation Submode**	2	B
C954	**Section T FL Enrichment**	2	B
C955	**FL Killed Hypotheses Registry** (12 hypotheses falsified: active control, loops, routing, batch processing, cross-line state, testing criteria, assessment output)	1	B
C956	**Positional Token Exclusivity** (192/334 tokens zone-exclusive, 2.72x shuffle; 50% survive suffix-stripping; effect is STRUCTURAL per negative control)	2	B
C957	**Token-Level Bigram Constraints** (26 mandatory, 9 forbidden; 2 genuinely token-specific: chey->chedy, chey->shedy both ENERGY; effect is STRUCTURAL)	2	B
C958	**Opener Class Determines Line Length** (24.9% partial R^2 beyond folio+regime; folio+opener_token = 93.7% R^2; strongest token-level finding)	2	B
C959	**Opener Is Role Marker, Not Instruction Header** (role accuracy 29.2% = 1.46x chance; token JSD not significant; free substitution within role)	2	B
C960	**Boundary Vocabulary Is Open** (Gini 0.47 < 0.60; 663 tokens for 80% coverage; no closed boundary set)	2	B
C961	**WORK Zone Is Unordered** (EN tau ~ 0, AX tau ~ 0; no systematic within-zone sequence; interior operations are parallel)	2	B
C962	**Phase Interleaving Pattern**	2	B
C963	**Paragraph Body Homogeneity**	2	B
C964	**Boundary-Constrained Free-Interior Grammar** (SYNTHESIS: grammar strength 0.500; boundaries constrained by role, interior free; system is role-complete)	2	B
C965	**Body Kernel Composition Shift** (h-kernel fraction rises +0.10, e-kernel drops -0.086 through body; survives length control; composition shift not diversity collapse)	2	B
C966	**EN Lane Oscillation First-Order Sufficiency** (markov_haz BIC=9166.3, 12 params; composite deviation 0.975 on 8 valid metrics; 2nd-order correction worsens fidelity; no hidden accumulator, no cross-line memory)	2	B
C967	**Hazard Gate Duration Exactly One Token**	2	B
C968	**Folio Drift Emergent Not Intrinsic**	2	B
C969	**2nd-Order Alternation Bias Non-Load-Bearing** (CMI=0.012 bits; post-SWITCH epsilon=+0.062, post-STAY delta=-0.067; statistically significant but correction worsens composite deviation 1.427->1.495; asymmetric between lanes; soft stabilization bias)	2	B
C970	**CC-Hazard Gate Priority**	2	B
C971	**Transition Asymmetry Structurally Rare**	2	B
C972	**Cross-Line Independence Stronger Than Random Markov**	2	B
C973	**Compositional Sparsity Exceeds Low-Dimensional Models**	2	B
C974	**Suffix-Role Binding Structural Not Random**	2	B
C975	**Fingerprint Joint Uniqueness UNCOMMON**	2	B
C976	**Transition Topology Compresses to 6 States** (49 classes → 6 states, 8.2x compression; preserves role integrity + depletion asymmetry; holdout-invariant 100/100 trials, ARI=0.939; generative fidelity 4/5 metrics)	2	B
C977	**EN/AX Transitionally Indistinguishable at Topology Level** (38 EN/AX classes merge freely; split into S3-minor 6 classes and S4-major 32 classes by depletion constraint; AXm→AXM flow 24.4x stronger than reverse)	2	B
C978	**Hub-and-Spoke Topology with Sub-2-Token Mixing** (S4/AXM universal attractor >56% from all states; spectral gap 0.894; mixing time 1.1 tokens; hazard/safe asymmetry 6.5x from operational mass) **[PHASE_736 scope-correction: the AXM self-transition RATE (0.698) is composition/mass-artifact — a 68%-mass block self-transitions ~68% by construction; "attractor cohesion / designed dwell" interpretation corrected to "mass-dominant macro-state." Spectral-gap MEASUREMENT stands. The above-Markov slow mode (C2061 λ2) is DISTRIBUTED, not in the self-loop — see C2065. Corroborates C1403. NOT a demotion.]**	2	B
C979	**REGIME Modulates Transition Weights Not Topology**	2	B
C980	**Free Variation Envelope: 48 Eigenvalues, 6 Necessary States** (effective rank 48 at >0.01 threshold; constraint compression to 6 states; gap = parametric control space; S4 has 81 MIDDLEs, Gini=0.545, within-state JSD=0.365)	2	B
C981	**MIDDLE Discrimination Space Is a Structural Fingerprint** (972 MIDDLEs; 4/5 metrics anomalous under Configuration Model z=+17 to +137; CV < 0.055 at 20% removal; λ₁ degrades linearly; FINGERPRINT_CONFIRMED)	2	A
C982	**Discrimination Space Dimensionality ~101**	2	A
C983	**Compatibility Is Strongly Transitive** (clustering 0.873 vs CM 0.253, z=+136.9; single most anomalous property; implies AND-style constraint intersection in structured feature space)	2	A
C984	**Independent Binary Features Insufficient** (AND-model matches density/λ₁/eigencount/rank but clustering ceiling 0.49 vs target 0.87 at all K∈[20,200]; features must be correlated/hierarchical/block-structured)	2	A
C985	**Character-Level Features Insufficient for Discrimination**	2	A
C986	**Hub Eigenmode Is Frequency Gradient** (λ₁=82.0, 4.3× next eigenvalue; hub-frequency Spearman ρ=-0.792, p≈0; hub loading monotonic with frequency band; hub axis = coverage axis C476/C755)	2	A
C987	**Discrimination Manifold Is Continuous** (residual space: best k=5, silhouette 0.245 MIXED_BANDS, 865/972 in one cluster; gap statistic -0.014; negative silhouette at k≥12; continuous curved manifold, not blocks)	2	A
C988	**AZC Folio Cohesion Is Hub-Driven** (full embedding: 27/27 coherent z=+13.26; residual: 0/27 coherent z=-2.68; folios sample frequency-coherent slices with diverse residual positions; zone C→R→S traces hub gradient)	2	AZC
C989	**B Execution Inhabits A's Discrimination Geometry** (80.2% token-weighted A-compatible at 37× enrichment; residual cosine: compat +0.076, incompat -0.051; violations concentrate in rare MIDDLEs; section S isolated; geometric realization of C468)	2	A↔B
C990	**B Operates at Elevated Constraint Tension**	2	A↔B
C991	**Radial Depth Dominates Line-Level Energy**	2	A↔B
C992	**e-Kernel Is the Compatibility Kernel**	2	A↔B
C993	**REGIME_4 Uniquely Converges in Energy**	2	B
C994	**B-Exclusive MIDDLEs Are Geometrically Subordinate**	2	A↔B
C995	**Affordance Bin Behavioral Coherence**	2	B
C996	**Forbidden Topology at HUB-STABILITY Interface** (13/17 forbidden transitions involve HUB_UNIVERSAL; 5/17 involve STABILITY_CRITICAL; no other bin participates; 8/17 are HUB→HUB self-transitions; hazard zone = compatibility carrier meets stability commitment)	2	B
C997	**Sparse Safety Buffer Architecture** (22/18085 interior tokens are safety-necessary; 0.12% buffer rate; 68% in HUB_UNIVERSAL; dominant pair chey→chedy buffered 9x; safety mechanism is QO lane-crossing in CHSH sequences; removing Bin 8 or Bin 0 induces forbidden pairs; grammar = sparse-critical-buffer regime)	2	B
C998	**Analog Physics Does Not Force Voynich Grammar Topology** (minimal reflux simulation median 3/10 targets; null models score equally; spectral gap 1% hit rate, forbidden pairs 4%, post-overshoot cooling 2%; continuous thermal dynamics cannot produce 6-state hub-spoke topology; grammar requires discrete encoding layer beyond analog physics)	2	B
C999	**Categorical Discretization Does Not Bridge Voynich Topology Gap** (5 physical strategies + 1 random null across 100 parameterizations; best physical 3/9 metrics toward Voynich = random 3/9; zero forbidden transitions from any strategy; hub mass degrades under all strategies; spectral gap is discretization artifact; Voynich discreteness is engineered abstraction, not categorization artifact)	2	B
C1000	**HUB_UNIVERSAL Decomposes Into Functional Sub-Roles** (23 HUB MIDDLEs → 4 sub-roles: HAZARD_SOURCE(6), HAZARD_TARGET(6), SAFETY_BUFFER(3), PURE_CONNECTOR(8); behaviorally homogeneous but functionally distinct; 17/17 forbidden transitions involve HUB; PREFIX lane chi²=12957 V=0.689; safety buffers 3.8x qo-enriched; regime clustering sil=0.398 at k=4; corrects C996 from 13/17 to 17/17)	2	B
C1001	**PREFIX Dual Encoding — Content and Positional Grammar** (PREFIX encodes both content (lane, class, suffix) and line position; PREFIX R²=0.069 ≈ MIDDLE R²=0.062 for position; 20/32 PREFIXes non-uniform positional profiles; po=86% initial, ar=61% final; PREFIX positional grammar regime-invariant for 7/7 major PREFIXes; sh→qo enrichment +20.5σ reveals line sequencing; I(MIDDLE_t; PREFIX_{t+1})=0.499 bits cross-component dependency)	2	B
C1002	**SUFFIX Positional and Sequential Grammar** (8/22 suffixes non-uniform positional profiles vs PREFIX 20/32; R² suffix=0.027 vs PREFIX=0.069; extreme specialists am 88% line-final, om 88% final; SUFFIX sequential grammar chi²=2896 V=0.063 comparable to PREFIX V=0.060; edy→edy +14.3σ self-repetition dominance; I(SUFFIX; PREFIX_{t+1} \| MIDDLE) = -0.074 bits — zero cross-token signal; C932 category paragraph gradients do NOT decompose to individual suffixes)	2	B
C1003	**TOKEN is Pairwise Composite — No Three-Way Synergy**	2	B
C1004	**49-Class Sufficiency Confirmed — No Hidden Suffix State** (Token-level Markov 38% worse than 49-class; only 1/17 classes shows suffix-differentiated transitions (JSD); H reduction from suffix conditioning = 0.259 bits (5.6%) — present but modest; no fourth architectural layer; 49-class grammar is the correct resolution for transition dynamics)	2	B
C1005	**Bubble-Point Oscillation Falsified — Duty-Cycle Pattern**	4	B
C1006	**Macro-State Dwell Non-Geometricity is Topology Artifact**	2	B
C1007	**AXM Exit-Boundary Gatekeeper Subset**	2	B
C1008	**AXM Directional Gating Mechanism**	2	B
C1009	**AXM Exit Hazard-Target Compositional Curvature**	2	B
C1010	**6-State Macro-Automaton is Minimal Invariant-Preserving Partition**	2	B
C1011	**Discrimination Manifold and Macro-Automaton are Geometrically Independent** (only 85/972 MIDDLEs (8.7%) bridge A manifold → B grammar; macro-state silhouette = -0.126 z=-0.96 p=0.843 — no geometric footprint; forbidden transitions not at geometric boundaries ratio=0.991 p=1.0; HUB MIDDLEs peripheral not central norm 2.31 vs 0.76 p≈0; HUB sub-roles not geometrically distinct p=0.577; 3/6 pre-registered predictions passed; manifold = A-level compatibility, automaton = B-level transition topology — complementary not redundant)	2	A→B
C1012	**PREFIX is Macro-State Selector via Positive Channeling, Not Negative Prohibition**	2	B
C1013	A->B Vocabulary Bridge is a Topological Generality Filter	2	A->B
C1014	Discrimination Manifold Encodes Viability Structure via Bridge Backbone	2	A->B
C1015	**PREFIX-Conditioned Macro-State Mutability with FL-Specific Routing Asymmetry**	2	B
C1016	**Folio-Level Macro-Automaton Decomposition with Dynamical Archetypes**	2	B
C1017	**Macro-State Dynamics Decompose into PREFIX Routing, Hazard Density, and Bridge Geometry**	2	B
C1018	**Archetype Geometric Anatomy — Slope Anomalies, Bridge PC1 Decomposition, and HUB Sub-Role Differentiation**	2	B
C1019	**Morphological Tensor Decomposition — Transition Tensor Has Rank-8 Pairwise Structure Orthogonal to 6-State Macro-Automaton** (rank 8 at 97.0% variance; CP ≥ Tucker confirming C1003; class factors ARI=0.053 vs C1010 — macro-automaton NOT a tensor projection; ΔR²=0.465 dynamical prediction 4x C1017; SUFFIX 2 SVD dims confirming C1004; HUB vs STABILITY cosine=0.574)	2	B
C1020	**Tensor Archetype Geometry — Tensor Factors Encode Dynamics Through Graded Curvature, Not Macro-State Clustering**	2	B
C1021	**CP Factor Characterization — Tensor Factors Are Frequency-Dominated, Rank Is Continuous, Tensor-Automaton Orthogonality Is Complete**	2	B
C1022	**Paragraph Macro-Dynamics — 6-State Automaton Does Not Differentiate Paragraph Structure**	2	B
C1023	**Structural Necessity Ablation — PREFIX Routing Is Sole Load-Bearing Macro Component** (PREFIX→state content routing: 78-81% of non-random structure destroyed by shuffle+reassignment; FL merge: -0.34% spectral gap; gatekeeper JSD=0.0014, z=-0.70 vs null; within-state routing: 0% structure loss; REGIME pooling: 1.1% gap difference; hierarchy: PREFIX routing >> FL ≈ gatekeepers ≈ REGIME; 3/6 pre-registered predictions correct on verdict, overall hierarchy confirmed)	2	B
C1024	**Structural Directionality — MIDDLE Carries Execution Asymmetry, PREFIX Is Symmetric Router** (MIDDLE asymmetry 0.070 bits, PREFIX 0.018 bits, ratio 0.25x; FL role highest per-class JSD 0.311; class-level bigram JSD=0.089 confirming C886; null control retains 64% of JSD from sparsity; resolves C391/C886 tension: PREFIX symmetric routing + MIDDLE directional execution = symmetric constraints with directional probabilities; 1/5 predictions correct)	2	B
C1025	**Generative Sufficiency — Class Markov + Forbidden Suppression Is Sufficient at M2 (80%)** (M0 i.i.d. passes 11/15=73% revealing most tests are marginal; M2 49-class Markov + forbidden suppression = sufficiency frontier at 12/15=80%; M4 compositional generation WORST at 9.4/15=63% from 4.2% hallucination rate; macro-automaton M3 ties M2, adds nothing; B4/C2 universally failed = test specification issues; 2/5 predictions correct)	2	B
C1026	**Grammar Component Necessity — Class Ordering and Forbidden Avoidance Are Load-Bearing; Token Identity Is Partial**	2	B
C1027	**Hazard Violation Archaeology — Forbidden Pair Violations Are Spatially Uniform but Structurally Conditioned**	2	B
C1028	**Vocabulary Curation Rule — Pairwise Co-occurrence Is Necessary and Dominant** (productive product space 48,640; 419 existing = 0.9% occupancy; pairwise co-occurrence gate: 100% recall, 58.4% precision; depth-3 tree 99.4% CV using only pm_cooc + ms_cooc; no three-way compilation rule detectable; 718 pairwise-compatible → 419 exist; consistent with C1003 no three-way synergy)	2	B
C1029	**Section-Parameterized Grammar Weights**	2	B
C1030	**M2 Gap Decomposition — B4 Misspecified, Two Independent Mechanisms** (B4 trivially passes: M2 self-rates identical to real; corrected 13/15=86.7%; B5 asymmetry 3.85x overestimate needs PREFIX routing C1024; C2 CC 100% suffix-free needs role morphology; independent: C2 constant across sections, B5 varies)	2	B
C1031	**FL Cross-Line Independence**	2	B
C1032	**B5 Asymmetry Mechanism — Forbidden Suppression + PREFIX Routing** (M2 B5=0.178 vs real 0.090; 16/17 forbidden pairs one-directional; alpha=0.15 blending fixes B5=0.111 but regresses B1 spectral gap 0.894->0.770 and B3 5 violations; C1024 PREFIX fraction 20.5% consistent with 15% blending; M2 stays 13/15=86.7%; true fix needs PREFIX-factored generation)	2	B
C1033	**C2 Test Misspecification — CC Definition Mismatch** (test uses CC={10,11,12,17} but C588 used {10,11,12}; class 17 has 59% suffixed; real C2=0.834 fails 99% threshold; M2=0.824 matches real; corrected 14/15=93.3%; C590 class 17 suffix=NONE wrong; only B5 remains)	2	B
C1034	**Symmetric Forbidden Suppression Fixes B5** (M5-SF: bidirectional forbidden, B5=0.132 80% pass, B1=0.873 100% pass, B3=0; M2.5 blending fails under C1025 mapping; PREFIX-factored distributionally equivalent to M2; projected 15/15=100% with B4+C2 corrections)	2	B
C1035	**AXM Residual Irreducible** (0/7 PASS; all 6 predictors dR2 < 0.013; RF CV R2 = -0.149; LOO gap 0.132; residual = free design space per C458/C980)	2	B
C1036	**AXM Exit Pathway Allocation Frequency-Neutral**	2	B
C1037	**AXM Class Composition Redundant**	2	B
C1038	**AXM Run Entropy Convergence + Micro-Sequential Stratum Empty** (0/6 PASS after size control; entropy slope=-0.248 bits/pos; JSD/CMI size-confounded; four-phase elimination complete; residual = design freedom)	2	B
C1039	**A Paragraph Cluster Selectivity**	2	A
C1040	**A Folio-Level Paragraph Compatibility Coherence** (within-folio 0.880 vs between-folio 0.811, p~0; survives section matching 0.810, p~0)	2	A
C1041	**A Paragraph Complementary Diversification** (cross-line compatibility 0.700 vs null 0.707, z=-3.567; paragraphs diversify, not select for compatibility; extends C476 coverage optimality)	2	A
C1042	**Section-Conditional Positional Exclusivity Reduction** (C956 zone-exclusive tokens retain only 30-55% exclusivity within sections; global exclusivity partially a section composition effect; qualifies C956)	2	B
C1043	**Role Self-Loop Section Dependence**	2	B
C1044	**Section-Dependent Phase Interleaving Rate**	2	B
C1045	**Section-Dependent Boundary Role Composition**	2	B
C1046	**Mandatory Bigram Section Modulation** (5/10 mandatory bigrams show section-dependent rates at Bonferroni alpha=0.005; extends C957 and C1029 to bigram level)	2	B
C1047	**Section-Dynamics Interaction Absent** (0/3 interaction terms significant; section modulates dynamics additively only; per-section LOO 0.037 vs global 0.412; strengthens C1035)	2	B
C1048	**BIO Section Dynamical Coherence** (BIO LOO R²=0.754 vs HERBAL -0.242 and RECIPE -0.319; C1017 predictors explain 75% of BIO AXM variance; design freedom concentrated in non-BIO sections)	2	B
C1049	**Shared Vocabulary Section-Universal Substrate**	2	A<>B
C1050	**PP Composition Section-Differential Coverage**	2	A<>B
C1051	**Section-Conditioned Class Convergence Asymmetry**	2	A<>B
C1052	**B Paragraph Cluster Selectivity**	2	B
C1053	**Compound Atom C475 Mediation**	2	B
C1054	**Affordance Bin Gradient Invariance** (HUB fraction ~64% at every quintile; 0/9 bins show gradient dependence; bin scaffold is static across spec→exec gradient; 73 paragraphs)	2	B
C1055	**M2 Near-Section-Decomposable** (per-section M2: BIO 78%, STARS_RECIPE 79%, HERBAL 70%; pooling advantage only +0.5 tests; topology preserved, distributional tests degrade cross-section)	2	B
C1056	**MIDPROCESS Structural Absence / OJLM-1 Boundary** (0/245 v3 recipes have MIDPROCESS actions; 0/509 master materials have process monitoring; MIDPROCESS is tacit operator knowledge; Path C mechanically passable but circular; Voynich M2 residual parallels 2/3 dynamic/pairwise)	2	B
C1057	**Lane-Sister Orthogonal Axes**	2	B
C1058	**Suffix Sequential Grammar Genuine**	2	B
C1059	**Suffix-Role PREFIX Independent** (V_raw=0.2869, V_conditioned=0.3750, mediation=-30.7%; per-PREFIX V: ol=0.663, ok=0.655, da=0.611, ot=0.532, BARE=0.436, ch=0.129, sh=0.120; 16054 classified tokens)	2	B
C1060	**Atom Position Grammar**	2	B
C1061	**Atom Co-occurrence Structure**	2	B
C1062	**Compound Depth-Folio Specificity**	2	B
C1063	**PREFIX-SUFFIX Compatibility** (chi²=8703.4, V=0.138; 17 forbidden pairs vs C911's 102; 16/17 novel, 1 role-explained; 50 enriched, 57 depleted; LATE prediction failed; ch/sh 0 forbidden; 30 PREFIXes x 21 SUFFIXes)	2	B
C1064	**PREFIX-SUFFIX Joint Role Encoding** (joint 88.5% vs PREFIX 82.6% vs SUFFIX 45.9%; +5.9pp gain; QO-family within-PREFIX V=0.615, sister V=0.124; three-layer encoding: PREFIX + suffix + joint; 16054 classified tokens)	2	B
C1065	**Atom Bigram Ordering Grammar**	2	B
C1066	**Construction-Execution Independence Confirmed**	2	B
C1067	**Terminal Character Positional Bias**	2	B
C1068	**[DEMOTED Tier 2→3 2026-05-19]** Originally "Cross-Layer Partial Coupling" (Tier 2). **Audit:** C475_degree × C911_restriction NMI=0.185 is marginal under proper null — chi² p=3.4e-292 used independence null which assumes independent marginals, but both factors correlate with token frequency. Marginal-preserving permutation null gives **p=0.13** (not significant at 0.05). C475-wholesale-graph concern from C475 demotion was AUDIT_PENDING; spot-check cleared it (methodology uses per-MIDDLE attested-degree, not sparsity-driven edges). Companion C1063-layer independence findings preserved within demotion narrative — these survive at proper null and are clean independence statements but kept within C1068 rather than split. Methodology memory: feedback_chi2_vs_permutation_null_mismatch.md.	3	B
C1069	**Weak Residual Community Structure** (3 communities after hub removal + frequency regression; Q_residual=0.125, Q_random=0.042, signal=0.082; weak but above-random; one community concentrates kernel-classified MIDDLEs)	2	B
C1070	**Atom Ordering Grammar Independent of Kernel Directional Bias** (only 2/21 cross-class pairs; both mismatch C521; compound construction grammar has own rules not reducible to kernel physics)	2	B
C1071	**Forbidden Transitions Operate Above Component-Level Rules** (only 4/17 C109 transitions blocked by C475/C911/C1063; 0 by C911 or C1063; 13/13 residual are C475-COMPATIBLE; confirms C627 token-specific directional mechanism)	2	B
C1072	**Terminal Character Predicts Within-Group Compatibility**	2	B
C1073	**Terminal-Role Association Is Frequency-Mediated**	2	B
C1074	**Terminal-State Association Is Frequency-Mediated**	2	B
C1075	**Compatibility Asymmetry Is Frequency-Dominated** (freq_sum +1.654 std coef dominates; INITIAL_match +0.089 below 0.10 threshold; INITIAL_x_FINAL +0.016 NS confirms C1003; shared_hinge +0.096; 271K pairs after singleton exclusion)	2	B
C1076	**Terminal Character Predicts Affordance Bin Beyond Frequency**	2	B
C1077	**Terminal Compatibility Groups Form Genuine Cliques**	2	B
C1078	**HT Hazard Avoidance Is Vocabulary-Level**	2	B
C1079	**Line-1 Exclusivity Is Folio-Specificity Tautology** (line-1 100% vs body 78.3% exclusive, p~0; singleton control: both 100%; C870 folio-specificity fully explains difference)	2	B
C1080	**Tail Pressure Predicts HT Compound Rate**	2	B
C1081	**LINK Adjacency Does Not Modulate HT Prefix Phase**	2	B
C1082	**HT Oscillation Is Section-Driven** (raw ACF significant at lags 1,2,4,6,20; section-residualized: only lag 7 survives; no lag 8-12 signal; resolves open question)	2	B
C1083	**HT Density Is Paragraph-Ordinal Neutral**	2	B
C1084	**Section-Specific AXM Attractor Ordering** > S(0.687) > C(0.635) > H(0.587); decomposes C1017 baseline; survives REGIME control)	2	B
C1085	**Bio Section Kernel-Balance Distinctiveness**	2	B
C1086	**Bio Section Apparatus-Hazard Depletion**	2	B
C1087	**Bio-REGIME_1 Multidimensional Divergence**	2	B
C1099	**Bridge Density Section Gradient**	2	GLOBAL
C1102	**Bridge Density REGIME Dependence**	2	GLOBAL
C1103	**REGIME-Bridge Density Is Section Confound**	2	GLOBAL
C1104	**Bridge Density Enables Dynamical Freedom**	2	B
C1105	**Bridge Geometry-Density Collinearity** (r=-0.805; delta-R²=0.007 NS beyond C1017; BIO LOO exception +0.071; same structural property, different measures)	2	B
C1106	**Stars e-Stability Kernel Enrichment**	2	B
C1107	**Stars LINK Monitoring Concentration**	2	B
C1108	**Stars Vocabulary Clamping Falsified** (S7-S10: 0 PASS, 3 FAIL; no consistent intra-REGIME clamping, no e-mediation, no bridge mediation, vocabulary LESS homogeneous across REGIMEs; Stars Paradox remains open)	2	B
C1111	**Stars Paradox is REGIME Composition Artifact**	2	B
C1112	**P-Text Bridge Enrichment** (45.5% bridge MIDDLEs, 55/121 unique, 100th percentile of A bootstrap; exceeds Rosettes 21.5% by 2.1x; evidence independent of Rosettes transcript)	2	A/AZC
C1116	**Within-REGIME Section Parameterization**	2	B
C1117	**LTR Reading Direction Confirmed**	2	B
C1118	**Bidirectional Forbidden Co-occurrence Dominance** (75.2% of MIDDLE-level forbidden pairs 1244/1655 are bidirectional adjacency prohibitions; 24.8% direction-specific; explains C1034 symmetric forbidden model improvement; broader MIDDLE co-occurrence landscape is predominantly symmetric while 17 class-level transitions C783 are directional)	2	B
C1119	**MIDDLE Forward Bias as Reading Direction Evidence**	2	B
C1120	**Lifecycle Domain Progression Falsified**	2	B
C1121	**Folio-Level Domain Determination** (paragraph domain character Bio/Stars determined at folio level ICC=0.393, F(45,95)=2.98; within REGIME_1 section predicts Bio-score Bio=0.131 vs Stars=-0.027 diff=0.158; within-paragraph domain stable perm p=0.19; consistent with C1087 Bio divergence)	2	B
C1124	**Rosettes Bridge Enrichment (Revalidated)** (3.05x enrichment: 21.5% bridge MIDDLEs vs 7.0% B baseline; universal across entity types — ring 4.56x, inner_label 4.74x, outer_label 5.17x, spiral 3.55x, clock 7.11x; no type below 25%)	2	Rosettes
C1125	**Rosettes Universal Section T Correlation**	2	Rosettes
C1126	**Rosettes Metalayer Status (Revalidated)** (confirmed metalayer: AZC-like entity types, 3.05x bridge enrichment, universal Section T indexing, 2.2x MIDDLE compatibility; verdict ROSETTES_CONFIRMED_METALAYER)	2	Rosettes
C1127	**Rosettes AZC-Like Grammar Profile** (grammar coverage 42.0%, kernel density 29-41%, LINK density <2.1% except ring 4.2%; morphological cosine 0.49-0.82 with AZC vs 0.25-0.67 with B; PP ~50%, RI ~2%; consistently AZC-like not hybrid)	2	Rosettes
C1128	**Rosettes Generic (Not Specific) Indexing**	2	Rosettes
C1129	**P-Text/Rosettes Unified Indexing (Revalidated)**	2	GLOBAL
C1130	**Ring Text Forbidden Compliance Without Transition Grammar** (0 forbidden violations in 277 MIDDLE bigrams; bigram entropy 7.92 bits vs B ~0.41; 252/277 unique bigrams; respects C783 hard constraints but has random transition structure; supersedes C1114/C1115)	2	Rosettes
C1131	**Ring Text Register Classification — BRIDGE_VOCABULARY_INDEX** (52.4% map to B grammar using 33/49 classes; AUXILIARY 42.7%, ENERGY 11.3%; bridge enrichment 32.1% > non-ring 25.5% > B p95 11.0%; 100% of classified MIDDLEs are bridge; no positional structure; structured class distribution JS=0.291 from uniform)	2	Rosettes
C1132	**Ring Text Dual Population Structure** (classified: 150 tokens, 4.0 chars, 27.3% kernel, 22.6% compound, 100% bridge; unclassified: 136 tokens, 6.4 chars, 47.8% kernel, 49.5% compound, 22.1% bridge — two interleaved functional vocabularies)	2	Rosettes
C1133	**Rosettes Targeting Decomposition**	2	Rosettes
C1134	**Section Specificity Is Frequency-Modulated** (PP drives 74% of section divergence through token frequency variation; B-exclusive JS=0.847 but only 5.8% of tokens; resolves C1049/C909 paradox)	2	B, A->B
C1135	**Unmatched PP Dark Pipeline** (300/315 unmatched PP MIDDLEs present in B at low frequency: mean 5.7 tokens vs 224.8 matched; section-concentrated Herf=0.716; 66.7% compound; large HT/UN substrate)	2	A->B
C1136	**A->B Flow: Uniform Pool, Concentration-Structured** (A-H/A-P cosine=0.9997; 12 A folios cover 100% classified grammar; f58v alone=60.7%; max A->B coverage ceiling 30.4%)	2	A->B
C1137	**Dark Pipeline = 100% HT/UN Substrate** (1,696 tokens from 300 MIDDLEs: 0.0% grammar-classified, 100.0% HT/UN; all 300 MIDDLEs pure-HT; mean 5.7 tokens/MIDDLE; positionally and sectionally indistinguishable from general HT)	2	B, A->B
C1138	**Dark Pipeline Has Distinct Construction Grammar** (grammar-standard/extended PREFIX ratio 3.39 vs general HT 1.81; suffix rate 89.9% vs HT 77.3%; articulator rate 2.5% vs HT 10.1%; same MIDDLEs but different morphological wrapping than general HT)	2	B morphology
C1139	**Dark Pipeline and Bridge Backbone Completely Disjoint** (0/300 dark-pipeline MIDDLEs overlap with 85 bridge MIDDLEs; separate A->B channels: bridges carry dynamical structure, dark pipeline carries identification vocabulary)	2	A->B
C1140	**PP Pipeline Is a Complete Four-Way Partition** (85 bridge + 4 non-bridge matched + 300 dark pipeline + 15 phantom = 404; exhaustive and mutually exclusive; non-bridge matched are c/ch/cho/otc, AUXILIARY-dominant edge cases; phantoms all ch/sh-prefixed with 0 A tokens)	2	A->B
C1141	**Dark Pipeline Compounds Built from Bridge Atoms** (86% of atom types are bridge MIDDLEs, 91.6% of occurrences; 96.5% of compounds contain >= 1 bridge atom; 50 unique atoms: 43 BRIDGE, 6 DARK_PIPELINE, 1 OTHER; mean 1.44 atoms/compound)	2	B morphology
C1142	**Dark Pipeline Uses Modified Construction Grammar**	2	B morphology
C1143	**Dark-Exclusive and Shared Atoms Have Equivalent Section Profiles** and less spread (11.4 vs 22.1 folios) but same section Herfindahl)	2	B morphology
C1144	**Dark Pipeline Ordering Divergence Is Genuine Grammar Modification**	2	B morphology
C1145	**Dark-Exclusive and Shared Atoms Occupy Equivalent Positional Slots**	2	B morphology
C1146	**Dark Pipeline Token Density Anti-Correlates with Bridge Tokens** (r=-0.865 overall; within-section r=-0.82 to -0.88 in all 4 sections; section R²=0.193; 80.7% of variance within-section; complementary distribution)	2	B, A->B
C1147	**Dark Pipeline Tokens Are Interior-Enriched Within Lines**	2	B, line structure
C1148	**Dark Pipeline Frequency Profiles Are Hyper-Modulated Across Sections** (mean JS=0.483, 3.9x C1134 baseline of 0.124; dark pipeline is primary vehicle for section-level vocabulary modulation)	2	B, section differentiation
C1149	**Vocabulary Balance Is Orthogonal to Dynamical Archetypes**	2	B, cross-system, dynamics
C1150	**Dark-Dominant Folios Shift Kernel Profile Within Section**	2	B, kernel, section
C1151	**Balance Distribution Is Section-Structured**	2	B, section differentiation
C1152	**Section-M2 Captures Vocabulary Composition but Not Sequential Dynamics** (class dist ratio 1.48x near-captured; AXM spread 1.76x uncaptured; kernel profile 1.79x uncaptured; 87% folios improved by section-conditioning; vocabulary is section-determined, dynamics are program-specific)	2	B, section, generative
C1153	**Generative Design Freedom Is ~40%** (32.4% class-dist + 43.2% AXM + 44.0% kernel uncaptured; aggregate 39.9%; AXM consistent with C1035's 57%; lower than C1016's 66.3% because class distribution IS section-captured)	2	B, generative, dynamics
C1154	**k-Kernel and e-Kernel Variance Are Universally Program-Specific** (k ratio 1.82-2.32x, e ratio 1.76-2.21x across all sections; h-kernel section-determined in BIO/HERBAL/COSMO (0.74-1.29x) but program-specific in STARS_RECIPE (2.18x))	2	B, kernel, section
C1155	**Paragraph Kernel Dynamics Do Not Mediate the AXM Residual** (kernel heterogeneity dR²=0.0012, trajectory slope variance dR²=0.0014, type entropy dR²=0.0002; all with negative LOO; within-section rho all <0.16; C1035 residual confirmed closed at paragraph level)	2	B, paragraph, kernel, AXM
C1156	**Line Position Structures Class Transitions**	2	B, line, transitions
C1157	**Boundary Divergence Mediates the AXM Residual**	2	B, line, AXM residual
C1158	**Entry Divergence Dominates Boundary Divergence Effect** (entry dR²=0.098 vs exit dR²=0.028, 3.5×; entry is the "reset to base" intensity; contradicts gatekeeper hypothesis)	2	B, line, AXM
C1159	**Boundary Divergence Is a Routing Shift, Not AXM Persistence Decay** (AXM→AXM only 3.2% of total delta; dominant: AXm→AXM +0.124, FQ→AXM +0.103 at entry; CC→AXM -0.296 at exit; inter-state routing, not self-transition)	2	B, line, transitions
C1160	**Boundary Divergence Is Section-Confounded but Carries Independent Signal**	2	B, line, section
C1161	**Gatekeeper Classes Partially Mediate Boundary Divergence**	2	B, line, gatekeeper
C1162	**Opener Role Does Not Predict Entry Divergence** (R²=0.128; no role |rho|≥0.30; role entropy uncorrelated; entry mechanism operates below role-level identity)	2	B, line, opener
C1163	**AXM Return Rate Dominates Entry Mechanism**	2	B, line, opener, routing
C1164	**Opener Routing Partially Mediates Entry Divergence**	2	B, line, opener, AXM
C1165	**AXM Return Rate Extends Residual Beyond Entry Divergence**	2	B, folio, AXM residual
C1166	**Exit Divergence Redundant After Entry Control**	2	B, line, boundary, exit
C1167	**AXM Departure Rate at Exit Extends Residual**	2	B, folio, AXM residual, exit
C1168	**Dual Boundary Architecture** (entry+exit independent channels; dual R²=0.852 LOO=0.732; exit dR²=0.039 LOO+0.036; all 3 sections benefit; irreducible ~57%→~27%)	2	B, folio, AXM residual, boundary
C1169	**AXM Residual Closed — ~27% Is Genuine Design Freedom**	2	B, folio, AXM residual, closure
C1170	**LINK Vocabulary Stratified by Role**	2	B, LINK, vocabulary, role
C1171	**LINK Behavior Is Role-Dominant**	2	B, LINK, cross-role, position
C1172	**BIO LINK Excess Is SPAN-Targeted**	2	B, BIO, LINK, section
C1173	**LINK Boundary Enrichment Is Passive**	2	B, LINK, boundary, dynamics
C1174	**LINK Is Morphological Artifact** (synthesis: STRATIFIED + ROLE_DOMINANT + PASSIVE → `ol` is morphological component not functional layer; revises C366/C609 interpretation)	2	B, LINK, synthesis
C1175	**Dark Compound Pair Space C475-Gated**	2	B, dark pipeline, combinatorics
C1176	**Section Hyper-Modulation Atom-Selection-Dominated** (multiplicative model R²=0.781 pseudo-R²=0.677; atoms carry section signal, compounds inherit)	2	B, dark pipeline, section, atoms
C1177	**Dark Ordering Consistent with C1065** (4/4 match 0 mismatch; revises C1142 50% from low-count noise; same grammar, sparse coverage)	2	B, dark pipeline, ordering grammar
C1178	**Phantom MIDDLEs Morphologically Isolated** (0/15 valid-unfilled; 11 partial 4 invalid; ch/sh-initial MIDDLE is dead naming pattern)	2	B, dark pipeline, phantoms
C1179	**Sister Choice Structured in Slot**	2	B, sister pairs, within-class
C1180	**Sister Choice Positionally Mediated**	2	B, sister pairs, position
C1181	**Sister Choice Dynamically Consequential**	2	B, sister pairs, dynamics
C1182	**Sister Concentration Moderate Consistency** (ICC=0.317; 32% folio-determined, 68% paragraph-variable; unimodal)	2	B, sister pairs, program structure
C1183	**Sister Bridge/Dark Independent** (all partial rho <0.16 after section control; vocabulary pipeline orthogonal)	2	B, sister pairs, vocabulary
C1184	**ch/sh and ok/ot Independent Axes**	2	B, sister pairs, within-class
C1185	**Sister Successor Routing MIDDLE-Dependent**	2	B, sister pairs, transitions
C1186	**Sister Boundary Coupled**	2	B, sister pairs, boundary
C1187	**Sister Mechanism: BOUNDARY_CONTROL_KNOB** (synthesis: structured, positional, dynamical, boundary-coupled; reduces C639 unexplained from 52.9% to ~40%)	2	B, sister pairs, synthesis
C1188	**Sister Entry Divergence Absent**	2	B, sister pairs, boundary architecture
C1189	**Sister Is Proxy Not Lever** (C1186 correlation mediated by C1163-C1165 opener-routing features; boundary architecture structurally complete; C1169 residual confirmed irreducible by sister)	2	B, sister pairs, boundary architecture, synthesis
C1190	**MIDDLE Behavioral Atomicity**	2	B, morphology, atomic composition
C1191	**Position-Dependent Behavioral Composition**	2	B, morphology, positional composition
C1192	**SUFFIX Additive Composition**	2	B, SUFFIX, composition
C1193	**PREFIX Compositional Duality** (PREFIX compounds split into compositional class (ke/te/ka/po/pch, predictable from atom profiles) and emergent class (ch/sh/da/ot/ok/ol, opaque); maps to EXTENDED/CORE prefix classification; discrete role clustering k=2: {a,d,o,q} vs {c,e,f,h,k,l,p,r,s,t,y})	2	B, PREFIX, composition
C1194	**Position-Specific Pair Discrimination** (near-identical atom pairs separate under position-specific profiles: k-t 0.993->0.568, d-o 0.945->0.296, p-t 0.935->0.467, l-r 0.919->0.806; global identity was masking PREFIX distinctions; no true atom redundancy)	2	B, atoms, discrimination
C1195	**Atom Gloss Confidence Tiers** (18 atoms in 4 tiers: 8 LOCKED (k,e,h,y,i,n,a,m), 6 SOLID (d,t,l,o,c,p), 5 PLAUSIBLE (f,s,g,x,r), 0 WEAK; validated against 91 glossed compounds; upgraded by Phases 496-500)	2	B, atoms, glossing
C1196	**Autogloss Composition Coverage** (1144/1273 compound MIDDLEs auto-glossed from atom decomposition; confidence: 72 LOCKED, 86 SOLID, 289 PLAUSIBLE, 768 WEAK; 58 incomplete (q); 67.1% WEAK driven by 3 generic atoms o/l/r)	2	B, compounds, glossing
C1197	**Atom Extensibility Partition** (only e and i repeat consecutively at structural levels (1555/1554 tokens); 18 other atoms are binary (present once or absent); extends C901 from A to B; 129 ratio families exist)	2	B, atoms, extensibility
C1198	**MIDDLE Order Irrelevance**	2	B, composition, order
C1199	**Extension Distributional Gradient**	2	B, extension, distribution
C1200	**Order Encodes Procedural State**	2	B, order, state
C1201	**PREFIX-Mediated Energy State Routing**	2	B, prefix, energy, routing
C1202	**H-Kernel MIDDLE No Transition Mediation**	2	B, h-kernel, negative
C1203	**ch/sh MIDDLE Atom-Level Differentiation** (ch-prefix MIDDLEs have higher k-atom fraction (7.1% vs 5.9%) and prefer e-free MIDDLEs: dy 3.1x, k 3.1x, d 2.8x ch-biased; sh-prefix MIDDLEs are more e-enriched (35.1% vs 30.2%); both share core vocabulary but frequency distributions diverge along k/e axis)	2	B, prefix, atoms, ch, sh
C1204	**i-Extension Inverted Gradient** (i-gradient inverted vs e: ii 53.7% > single-i 45.9%, unlike e where single-e 81.1% dominates; driven by aIn family where ii-form is 2x more common; HERBAL highest ii+ rate 67.6%, BIO lowest 46.7%)	2	B, i-atom, extension
C1205	**i-Atom Orthogonal to k/e Energy System** (i operates on independent axis: no carryover z=-6.14 (anti-clusters), disjoint atom space chi2=2272, folio r(i,k)=-0.437 r(i,e)=-0.412, program-specific within/between=1.83, partial carryover interruption; all signals survive daiin removal)	2	B, i-atom, orthogonality, k/e
C1206	**Paragraph Kernel Gradient** (h declines r=-0.920 through folio line quintiles while k rises r=+0.727 and e rises r=+0.881; early lines monitoring-heavy, later lines operation-heavy; extends C965 kernel composition shift)	2	B, paragraph, gradient, kernel
C1207	**Atom Correlation Clusters** (~20 atoms organize into 5-6 correlated clusters at folio level; {a,i,n,r} iteration axis r=+0.81-0.83, {c,h} monitoring r=+0.75, {k,l} energy r=+0.54, {d,y} closure r=+0.48, {o,p} structural r=+0.41; 64/153 pairs FDR-significant; all survive daiin removal)	2	B, atoms, dimensionality, clusters
C1208	**Atom Carryover Classification** (18 atoms classify into 3 carryover classes: POSITIVE state persistence {a,c,h,k,m,p,r,s,t} z=+2.5 to +9.6; NEGATIVE anti-clustering {e,i,n,y} z=-4.3 to -6.1; NEUTRAL {d,f,l,o,q}; e anti-clusters despite C1200 directional carryover; all survive daiin removal)	2	B, atoms, carryover, classification
C1209	**MIDDLE Positional Grammar** (atoms occupy ordered slots within MIDDLEs: INITIAL {a,q,e,o} 86-57% initial; MEDIAL {c,i,p,d,f,s}; TERMINAL {n,y,m,r,h,l} 71-99% terminal; FREE {k,t} no preference; n 99.4% terminal, a 86.3% initial; all 18 atoms FDR-significant; k/t position-freedom consistent with kernel operator role)	2	B, atoms, position, grammar
C1210	**MIDDLE Slot Syntax**	2	B, atoms, syntax, slots
C1211	**Sub-MIDDLE Pairwise Sufficiency** (INITIAL+MEDIAL+TERMINAL show REDUNDANCY not synergy: synergy=-0.827 bits; extends C1003 to sub-MIDDLE level; INITIAL explains 35.9% of TERMINAL entropy, MEDIAL 49.1%, both together 57.5%; pairwise interactions sufficient at both morphological levels)	2	B, atoms, synergy, pairwise
C1212	**Cross-Token Sequential Chaining** (TERMINAL(N)->INITIAL(N+1) is the strongest genuine sequential signal z=20.3; full 3x3 slot matrix shows MEDIAL->MEDIAL has highest raw MI=0.092 but lowest z=3.4 -- 80% co-occurrence not sequence; cross-token signal 6% of within-MIDDLE MI; enriched: h->p 2.61x, r->a 1.99x; depleted: r->t 0.25x; cross-line NOT weaker MI ratio=1.262; within-lane stratification confirms not purely PREFIX confound)	2	B, atoms, chaining, sequential
C1213	**Axis-Switching Dominance** (programs switch C1207 axes between tokens 84.8% of the time; same-axis continuation 15.2% vs expected 13.2%, enrichment only 1.15x; ITERATION->ITERATION highest same-axis at 33.2%; STABILITY dominant target from all axes; programs interleave across operational channels)	2	B, atoms, axes, switching, programs
C1214	**Line Compositional Homogeneity** (lines mildly more homogeneous than within-folio shuffled: z=-7.0, 3.8% entropy reduction; all slots equal INITIAL z=-8.1, MEDIAL z=-7.0, TERMINAL z=-8.2; PC1 36.2% CLOSURE vs ITERATION; section explains only 12.6% of PC1; no position gradient; explains C1212 MEDIAL co-occurrence as whole-token tuning; survives daiin exclusion z=-6.78)	2	B, lines, homogeneity, composition
C1215	**Compound MIDDLE Slot Compliance** (compound MIDDLEs obey C1210 forbidden combinations: a->y 1/1422, e->n 1/3972, k->n 0/475; compound slot syntax weaker V=0.329 vs atomic V=0.416 reflecting greater INITIAL->TERMINAL diversity; forbidden rules are scale-invariant)	2	B, compounds, slots, compliance
C1216	**Compound Junction Grammar**	2	B, compounds, junctions, grammar, routing
C1217	**Lane vs Non-Lane Atom Content Separation**	2	B, lanes, atoms, PREFIX, energy, iteration
C1218	**PREFIX Internal Positional Grammar** (PREFIX characters have strong positional preferences: dedicated modifiers q,d,f,p,y,s at POS-0, dedicated bases h,e at POS-1+, dual-role o,k,l,t,c,a,r; forms base-modifier grammar parallel to MIDDLE INITIAL/TERMINAL syntax; reinterprets C1193 low additivity as role-switching not non-compositionality)	2	B, PREFIX, atoms, grammar, positional
C1219	**Base Character Determines MIDDLE Content** (final character of PREFIX predicts MIDDLE atom profile: within-base cosine 0.950 vs between-base 0.515, ratio 1.84; a-base=80% ITERATION, o-base=42% ENERGY, h-base=32% STABILITY+31% CLOSURE, e-base=53% CLOSURE; base defines operational domain, modifier selects variant)	2	B, PREFIX, atoms, base, MIDDLE
C1220	**PREFIX Modifier Consistency Varies by Character** (cross-base modifier consistency ranges from high o=0.836, l=0.794, a=0.756 to low d=0.345, s=0.368, c=0.380; compositionality is partial and modifier-specific; consistent modifiers are genuine compositional elements, base-dependent modifiers function more as allomorphs)	2	B, PREFIX, atoms, modifier, compositionality
C1221	**Prep PREFIX Similarity is Base-Driven**	2	B, PREFIX, prep, Brunschwig, base
C1222	**Modern Distillation Dimensionality Closer to Voynich** (modern distillation 4 PCs for 80% vs Brunschwig 3, Voynich 5; entropy 2.334 bits 2.3× closer to Voynich; MIDPROCESS 34.5% of modern actions forming PC2 at 20.2% variance vs Brunschwig 0%; 7 active dimensions vs 5; process control vs recipe specification)	2	B, Brunschwig, modern, PCA, MIDPROCESS, dimensional
C1223	**MIDPROCESS Sub-Type Split Matches Voynich Dimensionality** (splitting MIDPROCESS into 5 Voynich-aligned sub-types MONITORING/ENERGY/STABILITY/CLOSURE/STRUCTURAL increases modern distillation from 4 to 5 PCs for 80%, exactly matching Voynich; entropy 2.921 bits; 11 active dimensions vs Voynich 10; remaining gap from C1222 fully explained by material-specific process control parameterization)	2	B, modern, PCA, MIDPROCESS, dimensional, axes
C1224	**Axis Distribution Transformation**	2	B, plants, PCA, axes, transformation, control program, paragraphs
C1225	**E-depth Suffix Parametricity**	2	B, ke-family, e-depth, suffix, parametric, MIDDLE
C1226	**ke/ek Ratio Process-Context Conditioning**	2	B, ke-family, ek, REGIME, section, process-sensitivity, MIDDLE
C1227	**FL Cross-Line Reset Clustering**	2	B, FL, paragraph, cross-line, reset, cycling
C1228	**PREFIX Channel Switching Within Paragraphs** (73.2% of paragraphs have interior body line pairs with PREFIX JSD matching or exceeding header-body opening JSD; interior JSD mean 0.470 vs opening 0.504; operational mode routinely resets mid-paragraph; section-consistent 69.6-93.3%; combined with smooth kernel gradient 2.4% breakpoints indicates cycling not apparatus switching)	2	B, PREFIX, paragraph, channel, switching, cycling
C1229	**Alternating Suffix Modes Within Paragraphs**	2	B, suffix, paragraph, clustering, alternating, gradient
C1230	**Suffix Mode MIDDLE Differentiation**	2	B, MIDDLE, PREFIX, suffix-mode, cycling, energy, extraction
C1231	**Universal Suffix Mode Centroids**	2	B, suffix-mode, universal, paragraph, clustering
C1232	**Paragraph Tail Product Signatures**	2	B, paragraph, tail, product, clustering, section
C1233	**Cross-Line Independence** (cross-line FL regression, mode alternation, and channel switching are near-random entropy 97.8%, mutual info <1%; each line independently composed)	2	B, cross-line, independence, entropy
C1234	**Iteration Two-Track System** (iin at line-initial 29.6% for cycle setup, aiin at penultimate 1.35x for bounded loop control; ii=formal bounded 92.6% n, i=open 52.9% n)	2	B, iteration, iin, aiin, loop, line-initial
C1235	**Line-Final Routing Architecture** (line-final = routing not processing; m 29.77x enriched, k/e depleted 0.52-0.63x; 34.9% batch-close / 14.6% loop-check / 50.5% neutral)	2	B, line-final, routing, m, batch-close
C1236	**Suffix Scope Markers** (terminal suffixes -edy Mode A specification 2.5-3.0x; checkpoint suffixes -aiin mode-independent; Mode A=36.1% terminal, Mode B=62.0% bare)	2	B, suffix, scope, terminal, checkpoint, mode
C1237	**Paragraph Termination by -am** (-am 5.19x at paragraph-final; terminal suffixes are batch-close not termination; last lines shorter 7.3 vs 10.0, cooling-enriched; steady-state until -am)	2	B, paragraph, termination, -am, cooling
C1238	**Kernel Initiation Order** (first-occurrence ordering e->k->h cool->process->monitor; e before k 64.6%, h before k only 28.3%; refines C873 mean-position ordering)	2	B, kernel, initiation, ordering, e, k, h
C1239	**Paragraph Body Length Parameterization**	2	B, paragraph, length, section, REGIME, memoryless
C1240	**Paragraph-Final -am Trigger Context**	2	B, paragraph, termination, -am, trigger, cooling, shutdown
C1241	**Header-Body Length Independence** (header complexity does not predict body length r=-0.039 tokens, -0.072 unique MIDDLEs; length externally determined; short and long paragraphs structurally identical)	2	B, paragraph, header, body, length, independence
C1242	**Cross-Lane Content Prediction**	2	B, cross-lane, MI, prediction, kernel, routing, line-scoped
C1243	**sh/ch Cross-Lane Routing Split** (sh→QO(k) 32.0% vs ch→QO(k) 24.0% 1.34x; sh entropy 4.763 ch entropy 5.068; sh=monitor-pivot formulaic ch=checkpoint-gate varied; extends C929 with routing evidence)	2	B, sh, ch, routing, pivot, gate, C929-extension
C1244	**aiin-ain Sequential Wind-Down** (aiin before ain 64.9% on co-occurring lines 98/151; adjacent aiin→ain 19 vs ain→aiin 11; loop-back 15.5% 2.05x baseline; 84.5% advance to different MIDDLE; sustained cycling to final pass)	2	B, suffix, aiin, ain, wind-down, iteration, ordering
C1245	**Cross-Lane Selectivity Gradient**	2	B, cross-lane, selectivity, entropy, e-depth, pairing
C1246	**Mode-Differentiated Cross-Lane Pairing**	2	B, cross-lane, mode, pairing, specification, execution
C1247	**aii REGIME_3 Specificity** (aii "unseal" is 41x enriched in R3 vs R1; 14/20 R3 folios contain aii vs 1/32 R1; line context shows close→unseal→open transition; R3 = open-cycle batch apparatus)	2	B, REGIME, aii, apparatus, batch
C1248	**Apparatus-Marker Co-occurrence Architecture**	2	B, apparatus, co-occurrence, REGIME, profile
C1249	**Section-Conditioned Apparatus Diversity** (Herbal is most apparatus-diverse section; R2-SEALED 100% Herbal; R4-SEALED/SUSTAINED 100% Herbal; Section B overwhelmingly distillation 0.293 vs H 0.134; weakest signatures all Herbal)	2	B, section, apparatus, diversity, Herbal
C1250	**Gloss Category Structural Coherence**	2	B, gloss, category, validation, corpus-scale
C1251	**Atom Gloss Compositional Validation**	2	B, atom, gloss, composition, C1191, positional-grammar
C1252	**Folio Operational Specialization**	2	B, folio, paragraph, specialization, gloss, JSD
C1253	**Paragraph-Level Apparatus Correlation**	2	B, paragraph, apparatus, THERMAL, correlation
C1254	**Dark Pipeline Category Generalization**	2	B, dark-pipeline, gloss, generalization, HT, atom, coverage
C1255	**Category-Section Universal Vocabulary**	2	B, section, category, vocabulary, frequency, universal, dark-pipeline
C1256	**Opener Mode Selection**	2	B, opener, suffix-mode, paragraph-type, mode-selection
C1257	**Consecutive Paragraph Vocabulary Coupling**	2	B, paragraph, vocabulary, sequential, self-containment
C1258	**Parallel Mode Tracks**	2	B, suffix-mode, parallel-tracks, counterpoint, line-structure, vocabulary, kernel, FL
C1259	**Gradient Decomposition by Suffix Mode**	2	B, gradient, suffix-mode, decomposition, mode-proportion, artifact, genuine
C1260	**Mode B Thermal State Tracking**	2	B, mode-b, thermal, state-tracking, energy-balance, propagation, FL, steady-state
C1261	**A Record Category Coherence**	2	A, category, record, coherence, entropy
C1262	**RI Extension Character Category Coupling**	2	A, RI, extension, category, coupling, C913
C1263	**A Paragraph Category Specialization**	2	A, paragraph, category, specialization, entropy
C1264	**Bridge vs Dark Pipeline Category Divergence**	2	A->B, bridge, dark-pipeline, category, divergence
C1265	**A Record Atom-Profile Coherence Independent of Category**	2	A, atom, coherence, AXIS, independent, record
C1266	**A Section Atom-Level Differentiation** (5/7 AXIS clusters differentiate H/P/T sections at Bonferroni; STABILITY H=30.2 FREE H=20.9 ENERGY H=20.2 MONITORING H=16.7 CLOSURE H=12.9; H CLOSURE/MONITORING-heavy P STABILITY/ENERGY-heavy T ITERATION/ENERGY-heavy; breaks C946 cosine-0.997 barrier at atom resolution)	2	A, section, atom, differentiation, AXIS, C946
C1267	**Mode A/B Distinction is B-Execution Only**	2	A, B, mode, null, orthogonality
C1268	**PREFIX Track and Category Track Orthogonal**	2	A, prefix, category, orthogonal, ch, sh, null
C1269	**AZC Zone Category Specialization**	2	AZC, zone, category, specialization, C313
C1270	**AZC Family Category Divergence**	2	AZC, family, category, zodiac, divergence
C1271	**AZC Zone Atom-Level Uniformity**	2	AZC, zone, atom, uniformity, null, AXIS
C1272	**AZC Mediates Bridge-Dark Category Sorting**	2	AZC, A->B, bridge, dark-pipeline, sorting, zone
C1273	**AZC-Exclusive Vocabulary is MARKING/THERMAL Enriched** (356 UNK MIDDLEs assigned by atom vote; MARKING 27.2% THERMAL 27.0% TRANSITION 6.5%; divergent from bridge V=0.382 dark V=0.210 PP V=0.192; AZC has categorically specialized private vocabulary)	2	AZC, exclusive, vocabulary, MARKING, THERMAL
C1274	**AZC Category Composition Predicts B Escape Rate**	2	AZC, A->B, category, escape, THERMAL, TRANSITION, qo-prefix
C1275	**No Within-Zone Spatial Category Coherence**	2	AZC, spatial, coherence, null, entropy
C1276	**AZC Sections Converge on A Pharma Atom Profile**	2	AZC, A, section, atom, Pharma, convergence
C1277	**THERMAL Escape is PREFIX-Mediated**	2	B, A->B, THERMAL, escape, PREFIX, qo, mediation
C1278	**Category Predicts Instruction Class Beyond PREFIX**	2	B, category, instruction-class, entropy, PREFIX
C1279	**Mode A/B Lines Differ by Category**	2	B, mode, category, THERMAL, TRANSITION
C1280	**Hazard Concentrates in FLOW/CONTAINMENT**	2	B, hazard, FLOW, CONTAINMENT, THERMAL, category
C1281	**TRANSITION Anti-Escape is PREFIX-Independent**	2	B, TRANSITION, escape, PREFIX-independent, anti-escape
C1282	**Category Predicts B Section Membership**	2	B, section, category, differentiation
C1283	**Category Differentiates Entry vs Exit Zones**	2	B, boundary, entry, exit, THERMAL, TRANSITION
C1284	**Kernel-Category Calibration** (CALIBRATION not discovery; THERMAL-k +0.646 THERMAL-e +0.668 TRANSITION-k -0.606 MONITORING-h +0.378; 9/24 sig; expected by C1250 construction; confirms consistency)	2	B, kernel, calibration, category, circularity
C1285	**TRANSITION Anti-Escape via Role Redirection**	2	B, TRANSITION, anti-escape, role-redirection, AUX, FQ
C1286	**Category Transition Grammar is Structured**	2	B, category, transition-matrix, sequential, grammar
C1287	**Paragraph Headers are MARKING-Enriched**	2	B, paragraph, header, MARKING, STAGING, specification
C1288	**Within-Folio Paragraphs Share Category Profiles**	2	B, paragraph, folio, coherence, category, JSD
C1289	**Category Predicts AXM Self-Transition Rate**	2	B, AXM, category, THERMAL, TRANSITION, dwell, macro-state
C1290	**Paragraph Category Predicts Mode**	2	B, paragraph, mode, category, THERMAL, TRANSITION
C1291	**Category-REGIME Association is Kernel-Mediated**	2	B, category, REGIME, kernel, circularity, mediation
C1292	**Section-Independent Category-REGIME Association**	2	B, category, REGIME, section, stratified
C1293	**Categories Discriminate Beyond Role Profiles**	2	B, category, role, REGIME, resolution, discrimination
C1294	**Category Fractions Do Not Extend C1169 AXM Model**	2	B, AXM, category, C1169, residual, validation, negative
C1295	**Paragraph Termination is Memoryless**	2	B, paragraph, termination, memoryless, thermal, negative
C1296	**Tail Type Category Divergence**	2	B, paragraph, termination, tail, category, divergence
C1297	**PREFIX-Category Structured Association**	2	B, PREFIX, category, contingency
C1298	**ok-ot Category Divergence**	2	B, PREFIX, sister pair, ok, ot, category, divergence
C1299	**ch-sh B-Specific Category Divergence**	2	B, PREFIX, sister pair, ch, sh, category, divergence, system-dependent
C1300	**qo Near-Pure THERMAL Channel**	2	B, PREFIX, qo, THERMAL, channel, purity
C1301	**PREFIX Category Information Beyond Base Group** (conditional MI I(CAT;PREFIX|BASE)=0.058 bits 2.1% of H(CAT)=2.742; Fisher-combined within-base p~0; t-base V=0.891 ct vs ot; o-base V=0.217 qo-driven; PREFIX is not tautological with base group; N=23,086 across 9 base groups)	2	B, PREFIX, base group, tautology, information theory, conditional MI
C1302	**BARE Distinctive Category Profile**	2	B, PREFIX, BARE, category, THERMAL depletion, FLOW
C1303	**ch/sh Category Divergence Is Position-Independent**	2	B, PREFIX, sister pair, ch, sh, category, position
C1304	**ok/ot Category Divergence Is Position-Independent**	2	B, PREFIX, sister pair, ok, ot, category, position
C1305	**MIDDLE Determines Category**	2	B, PREFIX, MIDDLE, sister pair, category, mechanism
C1306	**Cross-Lane Cargo Divergence**	2	B, PREFIX, sister pair, ch, sh, QO lane, cross-lane, category
C1307	**No Sister x Category x Position Interaction**	2	B, PREFIX, sister pair, position, category, interaction
C1308	**Within-Paragraph Category Coherence**	2	B, paragraph, mode, category, coherence
C1309	**Mode Category Specialization**	2	B, mode, category, specialization, THERMAL, TRANSITION
C1310	**Positional Category Alignment**	2	B, mode, position, category, alignment, parallel tracks
C1311	**B-to-A Thermal Feedback Signal**	2	B, mode, thermal, feedback, cross-mode, MARKING
C1312	**No Cross-Line Sequential Category Coupling**	2	B, mode, cross-line, sequential, independence, forbidden
C1313	**Two-Channel Thermal Atom Separation**	2	B, PREFIX, thermal, atom, qo, ok, separation
C1314	**Overshoot-Correct Bigram Enrichment**	2	B, PREFIX, thermal, sequencing, bigram, cycling
C1315	**REGIME B Token Profile Discrimination**	2	B, REGIME, discrimination, category, atom, A-control
C1316	**O-PREFIX Categorical Distinction**	2	B, PREFIX, o-prefix, ok, ot, ol, or, category, sequential
C1317	**Visual Text Block Census**	2	B, block, census, section, layout
C1318	**Block PREFIX Complementarity**	2	B, block, PREFIX, complementarity, divergence, parallel
C1319	**Block-Initial Paragraph Enrichment**	2	B, block, HT, MARKING, enrichment, header
C1320	**Block Internal Diversity**	2	B, block, kernel, category, diversity, falsified
C1321	**Gallows Within-Block Ordering**	2	B, gallows, block, ordering, transition, t-late
C1322	**Gallows-Category Independence**	2	B, gallows, category, independence, kernel, falsified
C1323	**Cross-Block Gallows Restart**	2	B, gallows, block, restart, cross-block
C1324	**Block-Final Termination Absence** (block-final -am DEPLETED 0.36x; suffix mode identical 58.9%=58.9%; 0/8 category shifts; boundaries are gallows-level not vocabulary-level)	2	B, block, termination, -am, suffix-mode, falsified
C1325	**Folio REGIME Homogeneity**	2	B, block, folio, REGIME, kernel, homogeneity
C1326	**Cross-Block Category Continuity**	2	B, block, category, continuity, cross-block, diversity
C1327	**Section S Ordinal Progression**	2	B, section-S, ordinal, category, progression, falsified
C1328	**Section S p-Gallows Dominance**	2	B, section-S, gallows, p-dominance, transition
C1329	**Section S Block Diversity**	2	B, section-S, block, diversity, category, REGIME, falsified
C1330	**Block Vocabulary Narrowing**	2	B, block, vocabulary, MIDDLE, ordinal, narrowing
C1331	**Iterative Refinement Falsified**	1	B, block, refinement, falsified, kernel, suffix-mode, FL
C1332	**Block-0 Marking Enrichment**	2	B, block, MARKING, MONITORING, category, vocabulary, block-0
C1333	**Kernel Most Stable Dimension**	2	B, block, kernel, stability, REGIME, dimension
C1334	**A Paragraph Dominance Structure**	2	A, paragraph, category, dominance, STAGING, section
C1335	**A Paragraph Category Taxonomy**	2	A, paragraph, category, taxonomy, type
C1336	**MARKING Paragraph-Initial Concentration**	2	A, paragraph, MARKING, positional, cross-system
C1337	**A Folio Paragraph Category Independence**	2	A, paragraph, folio, category, independence, NON_SEQUENTIAL
C1338	**MIDDLE Suffix Selectivity** (I(MIDDLE; suffix_cat) = 0.697 bits, 11.57x more than I(line_mode; suffix_cat) = 0.060; 60% of frequent MIDDLEs suffix-locked at >80%; 37.1% bare-locked, 22.9% terminal-locked; suffix is a MIDDLE property not a line property)	2	B, suffix, mode, MIDDLE, identity, mutual-information
C1339	**MIDDLE Mode Flexibility** (only 7.7% of frequent MIDDLEs mode-locked >80%; 34.6% flexible 40-60%; MIDDLEs freely appear in both modes; THERMAL MIDDLEs lean Mode B 0.406 despite THERMAL enrichment in Mode A — suffix behavior not token selection)	2	B, suffix, mode, MIDDLE, flexibility, category
C1340	**Suffix Stability Across Modes**	2	B, suffix, mode, stability, context
C1341	**Suffix Mode Is Emergent Property** (token-identity-predicted mode matches actual 80.0% accuracy; baseline 59.7% lift 1.34x; Mode A recall 89.4%; mode emerges from token composition ~80%, contextual modulation ~20%; resolves C1256 opener mechanism and C1259 flat mode proportion)	2	B, suffix, mode, emergent, generative, identity
C1342	**PREFIX Modulates Suffix Choice**	2	B, PREFIX, suffix, modulation, context
C1343	**Category Environment Suffix Effect**	2	B, category, environment, suffix, THERMAL
C1344	**Position Suffix Modulation**	2	B, position, suffix, modulation
C1345	**Opener Mode Weak Propagation**	2	B, opener, mode, paragraph, propagation
C1346	**Contextual Modulation Decomposition** (20% contextual residual decomposes: PREFIX 0.097 bits 50% → environment 0.057 bits 29% → position 0.024 bits 12% → opener 0.016 bits 8%; factors largely non-redundant MI 0.003-0.006 bits between pairs; modulation is probabilistic not deterministic)	2	B, context, decomposition, PREFIX, suffix, mode
C1347	**B Reshapes Bridge Category Usage**	2	cross-system, bridge, category, reshaping, THERMAL
C1348	**A Sections Differentiate at Category Level**	2	cross-system, section, category, differentiation
C1349	**Dark Pipeline Preserves Category Structure**	2	cross-system, dark, category, preservation, independence
C1350	**Dark MIDDLEs Atomistically Distributed**	2	B, dark, co-occurrence, adjacency, atomistic
C1351	**Dark Successor Entropy Is Narrow**	2	B, dark, entropy, successor, grammar, context
C1352	**Dark Folio Span Frequency-Matched** (78.3% of reliable dark MIDDLEs span folios within ±2σ of frequency-controlled null; 21.7% concentrated 0% dispersed; no bimodal staples-vs-specialists split; unimodal median 8 folios mean 10.8; span is consequence of abundance not role)	2	B, dark, span, frequency, distribution
C1353	**Dark Weak Positional Bias**	2	B, dark, position, ordering, weak
C1354	**Dark Grammar Influence Is Local Not Contextual**	2	B, dark, grammar, local, falsification
C1355	**Dark Entropy Difference Partially Frequency-Mediated**	2	B, dark, entropy, frequency, artifact
C1356	**Dark MIDDLE Identity Beyond PREFIX**	2	B, dark, PREFIX, MIDDLE, information
C1357	**Dark Proximity Weakly Boosts Terminal Suffix**	2	B, dark, suffix, terminal, proximity
C1358	**Class Positional Specialization**	2	B, line, position, 49-class
C1359	**Transition Gradient Resolution**	2	B, line, transition, gradient, position
C1360	**Forbidden Transition Violations Dispersed and Rare** (11 violations in 20,676 transitions 0.053% rate; KS=0.232 p>=0.05 vs uniform; 10/11 are dy→aiin; hazard avoidance uniform across line positions; forbidden pairs nearly absolute at MIDDLE level)	2	B, line, forbidden, position
C1361	**No Positional Motifs** (1/1556 class bigrams significant after Bonferroni; class-class transitions not locked to positions; grammar same everywhere; positional gradient arises from shifting class FREQUENCIES not position-specific rules; confirms C964 free interior at 49-class)	2	B, line, bigrams, position, motifs
C1362	**Position-Conditioned Generative Improvement** (M2p quintile-conditioned wins 5/5 metrics vs stationary M2; class KL 2.4x better, transition JSD 1.7x, positional entropy 1.6x, AXM self 1.8x, specialist accuracy 2.5x; position is M2's primary blind spot; grammar unchanged but class frequencies shift across line)	2	B, line, generative, M2p, position
C1363	**Gradient Steepness Universal**	2	B, line, folio, gradient
C1364	**Position-Conditioned Generation M2.1** (quintile-conditioned 49-class Markov + symmetric forbidden passes 16/18 generative metrics; gains P1 P2 P3 with zero regressions vs M2-SF 13/18; P1 class KL 2.2x better P2 trans JSD 2.0x P3 specialist 2.4x; remaining failures B4 C2 are morphological not sequential; M2.1 is new generative frontier at 88.9%)	2	B, generative, position, M2.1
C1365	**Corrected Evaluation Full Pass** (M2.1 passes 21/21 after correcting B4 test spec C1030 and C2 test spec C1033; adds C2a macro-CC C2b role-CC X1 PREFIX symmetry X2 MIDDLE asymmetry; PREFIX factoring proven unnecessary C1034; 49-class grammar generatively closed; remaining variance is stochastic not structural)	2	B, generative, evaluation, M2.1
C1366	**M2.1 Generative Gap Characterization** (Per-folio accent concentrates in class distribution and sequential dynamics, not positional structure or vocabulary composition; 11/31 features show systematic gaps mean\|z\|>1.5; BIO most anomalous section, Archetype 1 highest anomaly; C458 asymmetry not confirmed at generative resolution; 76.5% feature-folio pairs within \|z\|<2)	2	B, folio, M2.1, design freedom, accent
C1367	**Folio Accent Vector Analysis**	2	B, folio, accent, PCA, category, archetype
C1368	**Accent PC2/PC3 Decomposition** (PC2 sequential complexity predicted by THERMAL + folio position LOO R²=0.267; PC3 morphological texture dominated by STARS section eta²=0.457 + CONTAINMENT + sister pair LOO R²=0.496; 0/5 expert predictions confirmed; THERMAL extends accent across PC1+PC2 = 79.4% of variance)	2	B, folio, accent, PCA, section, category, sister pair
C1369	**Accent Spatial Structure**	2	B, folio, accent, spatial, section, archetype
C1370	**Category Pipeline Trace A→AZC→B**	2	A, AZC, B, cross-system, category, bridge, dark pipeline
C1371	**Position-Conditioned Category Grammar**	2	B, line, category, positional, transition
C1372	**Thermodynamic Arc Validation**	2	B, line, category, positional, interpretation, PREFIX
C1373	**PREFIX Category-Position Decomposition**	2	B, PREFIX, line, category, positional, sister pair
C1374	**Within-PREFIX MIDDLE Positional Selection**	2	B, PREFIX, MIDDLE, line, positional, category, sister pair
C1375	**Hebrew Cipher Cross-Validation** (Gatta Hebrew cipher decode INCREASES entropy +0.218 bits DECREASES MI -0.755 bits opposite of decipherment; 0/8 categories show Hebrew coherence ratio=0.991; 1/35 PREFIXes match Hebrew morpheme; T2 class clustering z=-15.5 is morphological confound; 3/7 control program 1/7 cipher 3/7 ambiguous = STRONG FALSIFICATION at grammar layer)	2	B, cross-validation, external, cipher, Hebrew, information theory
C1376	**Character-Level RTL Signal Is Grammar-Internal**	2	B, directionality, character-level, slot syntax, external, grammar
C1377	**Puff-Voynich Structural Revisit (NULL)**	2	B, Puff, material type, category, apparatus, NULL, ceiling
C1378	**Paragraph-Level Material Differentiation (NULL)**	2	B, paragraph, material, dark-pipeline, MIDDLE, NULL, header, ceiling
C1379	**Two-Level Parallel Composition with Priority Ordering**	2	B, MIDDLE, composition, macro-atom, parallel, priority, channel, suffix-mode, C1190, C1210, C1229
C1380	**Apparatus Profile Partially Explains AXM Residual**	2	B, AXM, residual, apparatus, design-freedom, Mantel, C1169, C1248
C1381	**o-Initial MIDDLE Enrichment in AZC**	2	CROSS, AZC, MIDDLE, atom, o-initial, apparatus, C496, C1269, C1273, C1274
C1382	**k/a Atom-Initial Suffix Mode Polarization**	2	B, MIDDLE, atom, suffix-mode, k-initial, a-initial, C1229, C1309, C908, C1381
C1383	**n-Terminal MIDDLE Boundary Avoidance**	2	B, MIDDLE, atom, n-terminal, boundary, position, mode, C1208, C1209, C1210, C1382
C1384	**k-Initial MIDDLE Fraction Predicts AXM Self-Transition**	2	B, MIDDLE, atom, k-initial, AXM, dwell, folio, C1382, C1289, C1309, C1208
C1385	**l-Terminal State/Condition Marker**	2	B, MIDDLE, atom, l-terminal, state, gloss, C1195, C1207, C1209, C1250, C1386
C1386	**ACTOR/RESPONDER Terminal-Atom Timing Split**	2	B, MIDDLE, atom, timing, macro-state, transition, C1200, C1209, C1208, C976
C1387	**r-Terminal Hazard-Response Partitioning**	2	B, MIDDLE, atom, r-terminal, FL_HAZ, macro-state, hazard, respond, C1195, C1207, C1208, C1386, C976
C1388	**o-Atom Arrangement Domain Marker** #1 kernel interleaver (52.1%); C874 convergence — ol=LINK from structural analysis independently confirmed by o(arrange)+l(state) = 100% STAGING 7.68x; 100% compound determinism ol=STAGING ok=CONTAINMENT or=FLOW ot=MONITORING; temporal ordering falsified (48.6% chance) — domain marker not sequential verb; 23-test battery 8/23 confirmed; upgrades o from WEAK to SOLID; German: ordnen)	2	B, MIDDLE, atom, o-initial, o-terminal, arrange, ordnen, STAGING, OPERATION, anti-AXM, interleaving, domain-marker, C874, C1195, C1207, C1381, C1384, C1386, C1190, C1305
C1389	c-atom main-loop modifier profile	2	B
C1390	p-atom marking pause profile	2	B
C1391	s-atom staging sequence profile	2	B
C1392	f-atom marking flag profile	2	B
C1393	compound MIDDLE composition grammar	2	B, grammar, composition
C1394	instruction encoding architecture	2	GLOBAL, grammar, composition
C1395	cross-system instruction encoding	2	GLOBAL, grammar, composition
C1396	prep PREFIX structural differentiation	2	B, PREFIX, prep, position, REGIME, suffix, atom
C1397	headless compound functional grammar	2	B, MIDDLE, headless, grammar, composition
C1398	paragraph operational gradient	2	B, paragraph, clustering, section, REGIME
C1399	paragraph ordering null	2	B, paragraph, ordering, folio, sequence
C1400	paragraph state-independent ordering	2	B, paragraph, ordering, thermal, state
C1401	C325 completion gradient is section confound	2	B, convergence, section, position
C1402	no sequential convergence to AXM at any scale	2	B, convergence, paragraph, line, AXM
C1403	MONOSTATE is thematic dominance not sequential convergence	2	B, convergence, MONOSTATE, AXM, reframe
C1404	Section structural differentiation is REGIME-dominated	2	B, section, REGIME, macro-state, kernel, hazard, morphology
C1405	Paragraph AXM driven by PREFIX not section	2	B, paragraph, AXM, PREFIX, variance decomposition
C1406	Section is REGIME composition at paragraph level	2	B, section, REGIME, paragraph, PREFIX
C1407	PREFIX-AXM relationship universal across sections	2	B, PREFIX, AXM, section, universality
C1408	suffix has HEAD→TERM compositional structure	2	B, suffix, atom, compositional, structure
C1409	suffix atoms diverge from MIDDLE-terminal atoms	2	B, suffix, atom, MIDDLE, cross-position, divergence
C1410	suffix modes are atom-level category partitions	2	B, suffix, atom, mode, paragraph, cycling
C1411	PREFIX->MIDDLE selectivity hierarchy with sister pair atom identity	2	B, PREFIX, MIDDLE, atom, sister pair, selectivity
C1412	MIDDLE dominates suffix determination via terminal atom	2	B, MIDDLE, suffix, atom, selectivity, terminal
C1413	PREFIX-SUFFIX coupling is MIDDLE-mediated	2	B, PREFIX, MIDDLE, suffix, independence, mediation
C1414	Cross-slot atom co-occurrence exclusion rules	2	B, MIDDLE, suffix, atom, co-occurrence, exclusion
C1415	83 forbidden PREFIX x MIDDLE HEAD combinations at atom level	2	B, PREFIX, MIDDLE, atom, forbidden, combinations
C1416	ARTICULATOR rate and inventory	2	B
C1417	ARTICULATOR line-initial concentration	2	B, line, position
C1418	ARTICULATOR PREFIX-locked with BARE/qo exclusion	2	B, PREFIX, ARTICULATOR
C1419	ARTICULATOR e-HEAD selectivity and k-HEAD exclusion	2	B, MIDDLE, ARTICULATOR, atom
C1420	ARTICULATOR suffix suppression	2	B, SUFFIX, ARTICULATOR
C1421	ARTICULATOR category full MIDDLE mediation	2	B, ARTICULATOR, category
C1422	suffix mode is MIDDLE-determined without sequential dependency	2	B, suffix, mode, MIDDLE, sequential, token-level
C1423	line-level mode persistence with weak inertia	2	B, suffix, mode, line, sequential, persistence
C1424	mode switching is TERMINAL-independent at line level	2	B, suffix, mode, line, TERMINAL, independence
C1425	line length unimodal distribution	2	B, line, length, distribution
C1426	line-initial specification profile	2	B, line, position, initial, specification
C1427	line-final transition profile	2	B, line, position, final, transition, closure
C1428	THERMAL-peak-then-decline positional gradient	2	B, line, position, gradient, category, THERMAL
C1429	cross-line category independence	2	B, line, independence, category, cross-line
C1430	information U-shape at line boundaries	2	B, line, information, position, boundary
C1431	non-PREFIX features add zero predictive power for paragraph AXM	2	B, paragraph, AXM, MIDDLE, suffix, articulator, line, design-freedom
C1432	paragraph AXM residual is 85% measurement noise	2	B, paragraph, AXM, noise, design-freedom, C1169, C1405
C1433	PREFIX-AXM mediation chain is complete at paragraph level	2	B, paragraph, AXM, PREFIX, mediation, C1405, C1411, C1418, C1422
C1434	m-terminal low-diversity closure specialization	2	B, MIDDLE, atom, m-terminal, closure, diversity
C1435	m-terminal body-line exclusivity	2	B, MIDDLE, atom, m-terminal, line, paragraph, body, header, position
C1436	m-terminal near-pure TRANSITION category	2	B, MIDDLE, atom, m-terminal, category, TRANSITION
C1437	m-terminal complete hazard exclusion	2	B, MIDDLE, atom, m-terminal, hazard, FLOW, CONTAINMENT
C1438	m-terminal categorical suffix suppression	2	B, MIDDLE, atom, m-terminal, suffix, suppression
C1439	m-terminal MIDDLE and -am suffix are orthogonal systems	2	B, MIDDLE, atom, m-terminal, suffix, -am, paragraph, line, closure
C1440	three-tier terminal opacity gradient	2	B, MIDDLE, atom, terminal, suffix, gradient, opacity
C1441	active terminal-suffix exclusion grammar rule	2	B, MIDDLE, atom, terminal, suffix, exclusion, grammar, rule
C1442	TERMINAL-suffix category information complementarity	2	B, MIDDLE, atom, terminal, suffix, information, complementarity, mutual-information, category
C1443	17 forbidden TERMINAL x suffix-head pairs	2	B, MIDDLE, atom, terminal, suffix, forbidden, co-occurrence, exclusion
C1444	self-atom cross-layer repulsion	2	B, MIDDLE, atom, terminal, suffix, self-repulsion, cross-layer
C1445	m-terminal and suffix anticorrelation at paragraph level	2	B, MIDDLE, atom, m-terminal, suffix, paragraph, anticorrelation, section
C1446	k-HEAD complete hazard immunity	2	B, MIDDLE, atom, k-initial, hazard, HEAD, immunity
C1447	terminal atom hazard partition	2	B, MIDDLE, atom, terminal, hazard, partition, FLOW
C1448	HEAD x TERM frame hazard map with k-neutralization	2	B, MIDDLE, atom, HEAD, TERM, frame, hazard, k-neutralization
C1449	PREFIX channel hazard with sister parity	2	B, PREFIX, hazard, sister pair, ch, sh, ok, ot, channel
C1450	opacity tier hazard gradient	2	B, MIDDLE, atom, terminal, hazard, opacity, gradient, suffix
C1451	Mode B exclusive forbidden violation concentration	2	B, suffix, mode, hazard, forbidden, violation, Mode-B
C1452	Non-monotonic i-extension hazard gradient	2	B, MIDDLE, atom, i-modifier, extension, hazard, non-monotonic
C1453	i-modifier frame selection, not inherent hazard	2	B, MIDDLE, atom, i-modifier, hazard, frame-selection
C1454	i-modifier anti-thermal category profile	2	B, MIDDLE, atom, i-modifier, category, anti-thermal
C1455	Quenching modifier partial i-override	2	B, MIDDLE, atom, i-modifier, quenching, co-occurrence
C1456	i-modifier suffix depletion	2	B, MIDDLE, atom, i-modifier, suffix, mode, n-terminal
C1457	e→y narrow vocabulary dominance	2	B, MIDDLE, atom, e-HEAD, y-terminal, vocabulary, dominance
C1458	e→y categorical safety with OPERATION enrichment	2	B, MIDDLE, atom, e-HEAD, y-terminal, hazard, safety, category, OPERATION
C1459	e→y context-independent deployment (not recovery-specific)	2	B, MIDDLE, atom, e-HEAD, y-terminal, context, recovery, ambient
C1460	e→y early-line concentration with final avoidance	2	B, MIDDLE, atom, e-HEAD, y-terminal, position, line, paragraph
C1461	e→y CHSH-channel with sh enrichment and qo/BARE exclusion	2	B, PREFIX, MIDDLE, atom, e-HEAD, y-terminal, channel, sh, qo
C1462	e→y rate predicts folio forgiveness via AXM attractor	2	B, MIDDLE, atom, e-HEAD, y-terminal, AXM, forgiveness, folio, hazard
C1463	Zone-hazard routing at line level	2	B, line, position, zone, hazard, frame, routing
C1464	k-IMMUNE THERMAL_WORK onset concentration	2	B, MIDDLE, atom, k-HEAD, IMMUNE, line, position, zone
C1465	HIGH frame positional heterogeneity	2	B, MIDDLE, atom, HEAD, TERM, frame, hazard, position, heterogeneity
C1466	Zone-hazard pattern line-length invariance	2	B, line, position, zone, hazard, frame, length, invariance
C1467	Paragraph zone x hazard interaction (non-fractal)	2	B, paragraph, zone, hazard, frame, routing
C1468	Header infrastructure-first composition	2	B, paragraph, header, hazard, LOW, ZERO, composition
C1469	Line hazard gradient paragraph-independent	2	B, line, paragraph, zone, hazard, independence, nested
C1470	Cross-line hazard correlation is folio-mediated	2	B, line, hazard, cross-line, folio, independence
C1471	No compensatory safe opening after hazardous closure	2	B, line, hazard, cross-line, e->y, recovery, compensatory
C1472	Modifier co-occurrence avoidance dominates ordering	2	B, grammar, composition
C1473	Modifier avoidance is frame incompatibility	2	B, MIDDLE, atom, modifier, co-occurrence, avoidance, frame, HEAD, TERMINAL
C1474	s-modifier universal connector	2	B, MIDDLE, atom, modifier, s, co-occurrence, universality
C1475	HEAD atom domain taxonomy	2	B, MIDDLE, atom, HEAD, category, domain, taxonomy
C1476	k-HEAD immunity is intrinsic not compositional	2	B, MIDDLE, atom, HEAD, k, hazard, immunity, intrinsic, modifier
C1477	a-HEAD is the primary hazard carrier	2	B, MIDDLE, atom, HEAD, a, hazard, forbidden, modifier, quench-resistant
C1478	k/t terminal mirror with category opposition	2	B, MIDDLE, atom, HEAD, k, t, terminal, category, mirror, PREFIX
C1479	HEAD-modifier selectivity partition	2	B, MIDDLE, atom, HEAD, modifier, selectivity, partition, co-occurrence
C1480	i-modifier Simpson's paradox full resolution	2	B, MIDDLE, atom, i-modifier, Simpson, hazard, HEAD, selection, resolution
C1481	i-modifier terminal transformation within a-HEAD	2	B, MIDDLE, atom, i-modifier, a-HEAD, terminal, transformation, TRANSITION
C1482	Double-ii safety via TRANSITION-locked n-terminal	2	B, MIDDLE, atom, i-modifier, double-ii, safety, n-terminal, TRANSITION, gradient
C1483	TERMINAL category specificity gradient	2	B, MIDDLE, atom, terminal, category, specificity, gradient, V=0.463
C1484	TERMINAL modifier exclusivity partition	2	B, MIDDLE, atom, terminal, modifier, exclusivity, partition, C1472, C1479
C1485	TERMINAL HEAD affinity partition	2	B, MIDDLE, atom, terminal, HEAD, affinity, partition, frame
C1486	m-terminal line-final closure confirmation	2	B, MIDDLE, atom, terminal, m, line-final, closure, C1434
C1487	Six-terminal functional taxonomy	2	B, MIDDLE, atom, terminal, taxonomy, LOCKED, CHANNELED, DIFFUSE, opacity, orthogonal
C1488	Headless compound population structure	2	B, MIDDLE, headless, population, census, compound
C1489	Headless pseudo-HEAD category differentiation	2	B, MIDDLE, headless, atom, category, pseudo-HEAD, domain
C1490	Headless terminal profile shift	2	B, MIDDLE, headless, atom, terminal, profile, enrichment, hazard
C1491	Headless da-PREFIX near-exclusivity	2	B, MIDDLE, headless, PREFIX, da, selectivity, sa, ta
C1492	Headless suffix bifurcation	2	B, MIDDLE, headless, suffix, bifurcation, binary, parametric
C1493	Headless internal structure with displaced HEAD	2	B, MIDDLE, headless, internal, structure, displaced, HEAD
C1494	Displaced HEAD k/t enrichment with inverted frequency	2	B, MIDDLE, headless, displaced, HEAD, k, t, e, frequency, inversion
C1495	HEAD-set atoms do not function as domain selectors when displaced	2	B, MIDDLE, headless, displaced, HEAD, category, pseudo-HEAD, domain, prediction
C1496	c-modifier primary displacement context	2	B, MIDDLE, headless, displaced, HEAD, c-modifier, k, t, ck, ct, context
C1497	Displaced HEAD extreme suffix rate	2	B, MIDDLE, headless, displaced, HEAD, suffix, rate, morphology
C1498	n/y-terminal categorical displacement exclusion	2	B, MIDDLE, headless, displaced, HEAD, terminal, n, y, bare, exclusion, gate
C1499	Atom ontology manuscript-wide shared substrate	2	GLOBAL, MIDDLE, atom, substrate, cross-system, Jaccard
C1500	Bridge-dark HEAD domain differentiation	2	B, A->B, MIDDLE, atom, bridge, dark, HEAD, differentiation
C1501	Bridge terminal tier outlier	2	B, A->B, MIDDLE, atom, bridge, terminal, tier, outlier
C1502	AZC o-HEAD domain enrichment (2.70x)	2	AZC, MIDDLE, atom, o-HEAD, enrichment, arrangement
C1503	Bridge atom redistribution across A/B	2	GLOBAL, A->B, MIDDLE, atom, bridge, redistribution, suffix, PREFIX
C1504	Modifier grammar universality across channels	2	GLOBAL, MIDDLE, atom, modifier, universality, cross-system
C1505	Dark pipeline MARKING-dominant category profile	2	B, A->B, MIDDLE, atom, dark, pipeline, category, MARKING, bridge, balanced
C1506	Bridge terminal atom stability across A and B	2	GLOBAL, A->B, MIDDLE, atom, bridge, terminal, stability, cross-system
C1507	Bridge HEAD redistribution A vs B	2	GLOBAL, A->B, MIDDLE, atom, bridge, HEAD, redistribution, arrangement, execution
C1508	Bridge category redistribution A vs B	2	GLOBAL, A->B, MIDDLE, atom, bridge, category, redistribution, THERMAL, STAGING
C1509	Three-tier atom behavioral stability across A and B	2	GLOBAL, A->B, MIDDLE, atom, behavioral, stability, correlation, cross-system
C1510	Suffix parallel HEAD+TERM decomposition	2	B, suffix, atom, decomposition, HEAD, TERM, parallel
C1511	Suffix excludes ACTION HEAD and EXECUTIVE MOD atoms	2	B, suffix, atom, missing, HEAD, MOD, exclusion
C1512	MIDDLE terminal dominates suffix content (V=0.513)	2	B, MIDDLE, suffix, atom, terminal, gating, content
C1513	Suffix atoms universally divergent from MIDDLE atoms	2	B, suffix, MIDDLE, atom, behavioral, divergence, JSD
C1514	Cross-system suffix atom identity (A=B=13, JSD=0.050)	2	GLOBAL, suffix, atom, cross-system, identity
C1515	Suffix mode category anatomy with positional asymmetry	2	B, suffix, mode, category, positional, THERMAL, FLOW
C1516	AZC HEAD domain differentiation across zones	2	AZC, zone, HEAD, atom, differentiation, V=0.115, C1271-refinement, C1394
C1517	o-HEAD enrichment is zone-graded not uniform	2	AZC, zone, o-HEAD, graded, arrangement, C1502, C1381, C1388
C1518	HEAD differentiation dominates TERMINAL across zones	2	AZC, zone, HEAD, TERMINAL, JSD, domain-selection, C1487, C1501
C1519	Zodiac HEAD uniformity vs A/C internal diversity	2	AZC, family, zodiac, AC, HEAD, diversity, C436, C1270
C1520	R-series no HEAD gradient	2	AZC, R-series, HEAD, gradient, null, R4-anomalous, C434
C1521	AZC zone pipeline composition varies	2	AZC, zone, pipeline, bridge, dark, exclusive, o-HEAD, C1139, C1272, C1500, C1505
C1522	AZC zones partition B-proximate vs A-proximate by HEAD JSD	2	AZC, zone, HEAD, JSD, B, A, proximity, partition, C301, C1507, C1517
C1523	Currier A headless rate 1.43x higher than B/AZC	2	GLOBAL, cross-system, headless, A, B, AZC, HEAD, rate, enrichment, C1488, C1507, C1519
C1524	da/sa/ta PREFIX exclusivity universal across systems	2	GLOBAL, cross-system, headless, PREFIX, da, sa, ta, exclusivity, universal, C1491, C1394
C1525	Headless suffix depletion universal across systems	2	GLOBAL, cross-system, headless, suffix, rate, depletion, universal, C1440, C1490, C1492
C1526	Headless category profile universal across systems	2	GLOBAL, cross-system, headless, category, THERMAL, STAGING, MARKING, universal, C1488, C1489, C1505
C1527	Headless functional core shared: 69 types cover 88-89%	2	GLOBAL, cross-system, headless, MIDDLE, overlap, shared, functional-core, type-exclusive, C1499, C1488
C1528	Hazard classes map to near-orthogonal atom HEAD territories	2	B, MIDDLE, atom, HEAD, TERM, hazard, failure-class, territory, orthogonal, C109, C1446, C1447, C1448, C1475
C1529	PHASE_ORDERING is headless y-terminal to a-HEAD transition failure	2	B, MIDDLE, atom, HEAD, TERM, hazard, PHASE_ORDERING, headless, y-terminal, a-HEAD, violation, C109, C1397, C1446, C1477, C1528
C1530	CONTAINMENT_TIMING is l/r-terminal SEMI_TRANSPARENT class with 100% avoidance	2	B, MIDDLE, atom, TERM, hazard, CONTAINMENT_TIMING, l-terminal, r-terminal, SEMI_TRANSPARENT, avoidance, C109, C1440, C1447, C1487
C1531	Forbidden MIDDLEs include 5 phantom types absent from corpus	2	B, MIDDLE, hazard, forbidden, phantom, construction, grammar, C109, C1178, C1394, C1528, C1529
C1532	Hazard classes partition by line position (setup-early to closure-late)	2	B, MIDDLE, hazard, failure-class, line, position, zone, gradient, C109, C1463, C1464, C1465, C1528
C1533	PHASE_ORDERING is CHSH-channel specific (28.4% CHSH, 7/11 violations)	2	B, MIDDLE, atom, PREFIX, hazard, PHASE_ORDERING, CHSH, channel, violation, C109, C929, C1449, C1451, C1529
C1534	PREFIX uses 15 characters in three-tier positional classification identical across all systems	2	GLOBAL, PREFIX, atom, positional, inventory, three-tier, MODIFIER, BASE, DUAL, C1218, C1499
C1535	i-atom categorically excluded from PREFIX — iteration absent from channel selection	2	GLOBAL, PREFIX, MIDDLE, atom, i-atom, exclusion, iteration, C1197, C1204, C1394, C1499, C1511
C1536	Base-to-HEAD selection V=0.478 — each base selects a distinct operational domain	2	GLOBAL, PREFIX, atom, base, HEAD, domain, V=0.478, C1218, C1219, C1475, C1507
C1537	a-base is the universal headless gateway (94-96% headless regardless of modifier)	2	GLOBAL, PREFIX, atom, base, a-base, headless, gateway, modifier-independent, C1488, C1491, C1524, C1536
C1538	q-modifier uniquely activates THERMAL channel on o-base (64% k-HEAD vs 5-19% other modifiers)	2	B, PREFIX, atom, modifier, q, o-base, THERMAL, k-HEAD, compositional, qo, C1300, C1313, C1536, C1537
C1539	Sister pairs decompose into SAME_BASE (ch/sh, da/sa) and SAME_MOD (ok/ot) structural types	2	GLOBAL, PREFIX, atom, sister-pair, ch, sh, ok, ot, da, sa, SAME_BASE, SAME_MOD, C408, C1478, C1534, C1536
C1540	p/f/c behavioral non-divergence vs stable MODs	2	GLOBAL, atom, cross-system, instability, JSD, behavioral, C1509, C1499
C1541	Suffix exclusion defines instruction-only atom tier	2	GLOBAL, atom, suffix, exclusion, instruction, tier, C1509, C1511, C1540
C1542	c-atom slot-switching between PREFIX and MIDDLE	2	B, MIDDLE, PREFIX, atom, c, slot-switching, HEAD, headless, e-HEAD, C1389, C1496, C1542
C1543	p/f are o-HEAD arrangement-affiliated atoms	2	B, MIDDLE, atom, p, f, o-HEAD, arrangement, headless, C1388, C1502, C1543
C1544	Unstable atoms increase Mode A suffix rate A->B	2	B, MIDDLE, atom, suffix, mode, UNSTABLE, Mode A, THERMAL, specification, C1509, C1515, C1229
C1545	f-atom anomalous B-exclusive vocabulary affinity	2	B, MIDDLE, atom, f, bridge, dark-pipeline, B-exclusive, vocabulary, rarity, C1139, C1499
C1546	Universal HEAD atom hazard source immunity	2	B, MIDDLE, atom, HEAD, hazard, immunity, universal, source, C1446, C1475, C1476, C1528
C1547	TERMINAL atom determines hazard class type (stronger than HEAD)	2	B, MIDDLE, atom, terminal, hazard, class, PHASE_ORDERING, CONTAINMENT_TIMING, y, l, C1447, C1483, C1487, C1528
C1548	PREFIX base-level hazard differentiation	2	B, PREFIX, base, hazard, source, enrichment, C1536, C1475, C1546
C1549	q-modifier hazard protection on o-base (~7x vs other modifiers)	2	B, PREFIX, modifier, q, o-base, hazard, protection, qo, C1538, C1546, C1548, C1452
C1550	Sister pair hazard source asymmetry	2	B, PREFIX, sister pair, hazard, asymmetry, ch, sh, ok, ot, da, sa, C1449, C1539, C1187
C1551	PHASE_ORDERING exclusively headless y-terminal dy; CONTAINMENT_TIMING exclusively l-terminal	2	B, MIDDLE, hazard, PHASE_ORDERING, CONTAINMENT_TIMING, headless, y-terminal, l-terminal, dy, l, C1529, C1530, C1547
C1552	5/9 hazard source MIDDLEs are phantom types absent from corpus	2	B, MIDDLE, hazard, phantom, forbidden, corpus, chey, shey, chedy, shedy, chol, C1531, C1178
C1553	ch/sh-initial compound MIDDLE categorical absence	2	B, MIDDLE, atom, ch, sh, compound, positional-partition, PREFIX, C1178, C1394, C1534, C1552
C1554	Phantom MIDDLEs are atom-legal but construction-dead (defense-in-depth)	2	B, MIDDLE, phantom, atom, slot, construction, defense-in-depth, hazard, C1552, C1553, C1178, C1209, C1546
C1555	c-initial compound second-atom selectivity (c+h adjacency absent)	2	B, MIDDLE, atom, c-initial, h-atom, second-atom, selectivity, C1389, C1553, C1472
C1556	o-HEAD terminal-to-category deterministic mapping	2	B, MIDDLE, atom, HEAD, o-HEAD, terminal, category, deterministic, STAGING, FLOW, OPERATION, C1388, C1475, C1483, C1485, C1487
C1557	o-HEAD y-terminal near-complete depletion (0.007x)	2	B, MIDDLE, atom, HEAD, o-HEAD, y-terminal, depletion, safety, PHASE_ORDERING, hazard, C1388, C1475, C1546, C1551
C1558	o-HEAD p/f executive modifier enrichment with i/d depletion	2	B, MIDDLE, atom, HEAD, o-HEAD, modifier, p, f, i, d, enrichment, depletion, arrangement, C1388, C1475, C1479, C1543
C1559	o-HEAD cross-system gradient A(28.5%)>AZC(22.4%)>B(11.8%) with AZC S/R=1.66x	2	CROSS, A, B, AZC, MIDDLE, atom, HEAD, o-HEAD, cross-system, gradient, AZC-zone, boundary, C1381, C1388, C1502, C1507, C1517, C1522
C1560	o-HEAD inner atom composition divergent (y 0.023x, l 2.74x, p 4.67x)	2	B, MIDDLE, atom, HEAD, o-HEAD, inner-atom, composition, divergent, y-depletion, l-enrichment, p-enrichment, CHANNELED, terminal, C1388, C1475, C1484, C1487, C1556
C1561	o-HEAD empirical hazard immunity (0% source AND 0% target)	2	B, MIDDLE, atom, HEAD, o-HEAD, hazard, immunity, source, target, double-protection, C1388, C1446, C1546, C1551, C1557
C1562	HEAD self-transition rate hierarchy	2	B, MIDDLE, atom, HEAD, self-transition, sequential, hierarchy, persistence, switching, C1212, C1384, C1475, C1478, C1521
C1563	Terminal-to-next-HEAD cross-token routing grammar	2	B, MIDDLE, atom, terminal, HEAD, routing, cross-token, sequential, instruction-phrases, C1212, C1440, C1475, C1483, C1484, C1487
C1564	Suffix carries zero forward information to next HEAD	2	B, suffix, HEAD, cross-token, information, null, compositionality, C1003, C1510, C1412, C1422
C1565	Paragraph header modifier divergence exceeds HEAD divergence 10x	2	B, paragraph, header, atom, modifier, HEAD, divergence, specification, executive, C1287, C1396, C1468, C1479, C1543
C1566	Line position Q3-Q4 step discontinuity	2	B, line, position, gradient, quintile, closure, step, discontinuity, specification, work-zone, C1425, C1426, C1427, C1428, C1429, C1430, C1434, C1463
C1567	Within-domain structural spine validation	2	B, MIDDLE, atom, HEAD, domain, compositional, validation, structural, T2A, C1475, C1476, C1477, C1478, C1482, C1556, C1557, C1561, C1563, C1566
C1568	Within-domain cross-folio discriminability	2	B, MIDDLE, atom, HEAD, domain, compositional, cross-folio, discriminability, section, classification, random-forest, C1475, C1556, C1563
C1569	Section-level within-domain parameterization	2	B, MIDDLE, atom, HEAD, domain, compositional, section, parameterization, folio, within-section, C1475, C1556, C1563, C1567, C1568
C1570	Deployment features are section-level not folio-level discriminators	2	B, MIDDLE, atom, HEAD, domain, compositional, deployment, zone, routing, closure, headless, paragraph, section, folio, within-section, discrimination, C1463, C1464, C1466, C1486, C1563, C1567, C1568, C1569
C1571	Deployment Ward clustering highest section ARI	2	B, MIDDLE, atom, HEAD, domain, compositional, deployment, clustering, Ward, ARI, section, C1567, C1568, C1569, C1570
C1572	Hierarchical variance partition validates 4-layer nesting with selective layer loading	2	B, structural, hierarchy, variance, section, folio, paragraph, line, decomposition, ANOVA, template, C1570, C1571
C1573	Paragraph emphasis distributions recover within-section folio specificity that averaging destroyed	2	B, paragraph, distribution, folio, within-section, specificity, emphasis, EMD, C1398, C1570, domain, section
C1574	Headless ecology is folio-specific not paragraph-specific	2	B, headless, ecology, folio, paragraph, section, hierarchy, C1398
C1575	Hierarchical trace executor produces weakly monotonic improvement across 4 layers	2	B, structural, hierarchy, trace, executor, section, folio, paragraph, line, token, monotonic, C1572, C1573, C1574
C1576	Paragraph cloud operates at aggregate geometric level not per-token level	2	B, paragraph, cloud, folio, recovery, distributional, geometry, C1573
C1577	Four permutation null models confirm non-trivial hierarchical structure	2	B, null, permutation, hierarchy, token, domain, terminal, routing, C1563
C1578	E4 improvement sources are line-phase domain adjustment and hazard envelope	2	B, line, phase, domain, hazard, envelope, routing, closure, ablation
C1579	CTS continuous closure encoding improves over categorical closure	2	B, closure, CTS, line, paragraph, Gaussian, encoding, C1434, C1440, C1566
C1580	Paragraph domain composition does NOT predict line hazard envelope	2	B, paragraph, hazard, envelope, cloud, blend, negative
C1581	Full hierarchical supervisory trace coupled to virtual apparatus yields structured plant behavior beyond section-only, budget-only, and null controls	2	B, virtual apparatus, hierarchy, trace, coupling, C1575, C1577, C1569
C1582	Line packet state produces statistically significant plant state differentiation across all 7 state variables	2	B, virtual apparatus, line, packet, state, C1425, C1426, C1427, C1428, C1578
C1583	Terminal routing grammar does NOT produce observable punctual plant deflections at token level (negative result)	2	B, virtual apparatus, routing, terminal, negative, C1563, C1564, C1470
C1584	Headless folio regime effect on plant containment is directionally correct but statistically underpowered	3	B, virtual apparatus, headless, containment, underpowered, C1488, C1574, C1523
C1585	CTS continuous closure contributes genuine value to coupled plant behavior	2	B, virtual apparatus, CTS, closure, line, paragraph, C1579, C1434, C1440, C1566
C1586	N3 line-shuffle null is non-destructive: line ordering carries less coupled-plant information than token composition	2	B, virtual apparatus, null, line-shuffle, ordering, C1399, C1400, C1470, C1577
C1587	A2_SEALED_RECIRCULATION underperforms A1_BATH_REFLUX for Herbal folios	3	B, virtual apparatus, profile, Herbal, assignment, C1248, C1249, C1380
C1605	PCV discrimination exceeds binary viability	2	B, virtual apparatus, PCV, viability, discrimination, C1581
C1606	S asymmetry insufficiency in burden metric	2	B, virtual apparatus, S, asymmetry, burden, SAHB
C1607	QGY partial paradox inversion	2	B, virtual apparatus, QGY, yield, quality, paradox, inversion
C1608	Closure opportunity scarcity	2	B, virtual apparatus, closure, CTS, opportunity, scarcity, C1566, C1579
C1609	PCV-visible CLOSE recovery	2	B, virtual apparatus, PCV, CLOSE, recovery, B10, C1585
C1612	Unresolved excursion burden inverts SAHB	2	B, virtual apparatus, UEB, burden, SAHB, inversion, C1606
C1614	Packet coherence discriminates supervised traces	2	B, virtual apparatus, WCP, coherence, discrimination, C1582, C1605
C1625	Folio-specific apparatus parameterization improves demanded-event ERM	2	B, virtual apparatus, folio-specific, F1-F5, demanded, ERM, C1569, C1574, C1380
C1627	B10 sensitivity increases under folio-specific config	2	B, virtual apparatus, folio-specific, B10, sensitivity, CLOSE, recovery, C1609, C1612
C1628	Existing anchors survive folio-specific parameterization	2	B, virtual apparatus, folio-specific, anchor, P2, UEB, WCP, stability, C1605
C1629	Folio-specific parameters align with structural proxies	2	B, virtual apparatus, folio-specific, F1-F5, structural, proxy, monotone, interpretability, C1380, C1574, C1569
C1632	Real closure tokens produce greater Y accumulation at demanded events than state-matched nulls	2	B, virtual apparatus, folio-specific, YGA, Y-gain, demanded, closure, M1, M4f, C1625, C1629
C1633	Real closure tokens convert disruption to Y with higher efficiency than state-matched nulls	2	B, virtual apparatus, folio-specific, DYE, efficiency, disruption, Y-gain, productive, closure, M1, M4f, C1632
C1634	Real closure tokens produce higher per-step disruption than random tokens at CLOSE positions	2	B, virtual apparatus, folio-specific, DVA, disruption, dV, CLOSE, productive, M1, M4f, C1633
C1635	Productive disruption efficiency (DYE advantage > 0) generalizes beyond hand-selected pilot folios to the broader 18-folio pilot set spanning 5 sections and 3 apparatus profiles	2	B, virtual apparatus, folio-specific, DYE, DVA, generalization, productive disruption, 18-folio, sections, profiles, C1633, C1634
C1636	Productive disruption efficiency is a broad apparatus property of Currier B: real closure tokens produce greater per-step disruption than demand-matched nulls and convert it into Y more efficiently across the full 76-folio eligible set, with strongest validation in demand-strong folios and systematic attenuation concentrated in the A2/section C stratum	2	B, virtual apparatus, folio-specific, DYE, DVA, expansion, productive disruption, 76-folio, sections, profiles, A2 forgivingness, C1633, C1634, C1635
C1637	WCP (whole-closure-packet coherence) is demoted from apparatus success criterion to legacy continuity diagnostic; endpoint packet coherence does not discriminate grammar advantage at scale (38% pass at Tier A) because the restoring force that makes the apparatus stable masks token-level differences at endpoints	2	B, virtual apparatus, WCP, demotion, legacy, endpoint, restoring force, C1614, C1636
C1638	The primary apparatus-side success family is DYE (dV-to-Y efficiency), DVA (dV advantage), and YGA (Y-gain advantage) — process-quality metrics that measure execution dynamics during closure, not endpoint state	2	B, virtual apparatus, DYE, DVA, YGA, success family, process quality, productive disruption, C1632, C1633, C1634, C1636, C1637
C1639	A2_SEALED_RECIRCULATION excess forgivingness mechanism identified: CLOSE recovery channels (R1-R5) account for 159.5% of A2's excess CCS1. Removing close recovery drops A2 null DYE from 0.114 to near zero. Within-A2, CCS1 correlates rho=0.963 with close recovery ablation effect. The mechanism is single-channel dominant, not distributed	2	B, virtual apparatus, A2, mechanism, CCS, close recovery, R1-R5, ablation, forgivingness, C1636
C1640	Currier B apparatus family partition: response-only clustering finds real but sub-threshold structure. Two-cluster split isolates 12 forgiving folios (9 A2 + 3 A3) from 64 productive folios. Response-surface clustering recovers profiles better at k=3 (ARI=0.348) but with low silhouette (0.126). Families are gradient-like, not crisp	2	B, virtual apparatus, clustering, family partition, Ward, silhouette, ARI, C1636, C1639
C1641	Within-A2 structure is weakly structured: section does not explain CCS1 variance (F-ratio=0.055), but 44% of A2 folios are boundary cases (4 A2→A1, 4 A2→A3). T\|A2 anomalously good (EPV=0.90). Only 6/18 A2 folios pass EPV≥0.80. Core A2 mean CCS1=0.180, boundary-to-A1 mean=0.013	2	B, virtual apparatus, A2, internal structure, conformity, boundary, C1636, C1639
C1642	A2 grammar-strength forgivingness is strength-dependent: only STRONG-grammar A2 events beat the null, while WEAK events lose to the null. Grammar strength modulates whether real closure outcompetes A2's generous close-recovery physics. This rules out uniform recirculation and confirms strength-gated conversion	2	B, virtual apparatus, A2, grammar, forgivingness, CCS, strength-dependent, C1636, C1639
C1643	A2 recovery gate sub-channel decomposition: RECOVERY_GATE_R1_C_DOMINANT. Both R1_C (117.3%) and R4_C (118.8%) containment pathways dominate the close recovery effect. Sub-channels are strongly non-additive (interaction fraction=-1.059), confirming R1-C feeds R4-C in a coupled containment-to-yield loop	2	B, virtual apparatus, A2, recovery gate, sub-channel, R1, R4, containment, C1639
C1644	Counterfeit closure threshold: THRESHOLD_A2_SHIFTED_GRADUAL. A2 requires CTS=0.18 for positive magnitude advantage vs CTS=0.04 for A1 (+0.138 shift). Transition is gradual (width=0.327 CTS). A2 needs minimum 1 strong grammar signal; A1/A3 need 0. A2 counterfeit susceptibility 64% at CTS<0.2, 0% above CTS=0.6	2	B, virtual apparatus, threshold, closure, CTS, counterfeiting, C1639, C1642
C1645	Closure packet morphology selectivity: MORPHOLOGY_SELECTIVE_COUNTERFEITING. 5 packet signatures resistant (armed+headless+high_cts types), 5 A2-counterfeitable (low-signal types). Top A2 protective features: headless_involved (+0.126), high_cts (+0.107), armed (+0.092). Counterfeiting is selective, not universal	2	B, virtual apparatus, morphology, closure packet, counterfeiting, C1639, C1644
C1646	Apparatus response landscape: LANDSCAPE_THREE_POLE. 25% STABLE_AMPLIFIER (12 A3 + 6 A1 + 1 A2), 63% THRESHOLD_DEPENDENT (24 A3 + 15 A1 + 9 A2), 12% FORGIVING_RECIRCULATOR (8 A2 + 1 A3). Classification partially cross-cuts profile (cross-cut=0.25). NOTE: classes are descriptive convenience overlays, not ontological species	2	B, virtual apparatus, landscape, folio classification, continuous, C1639, C1640
C1647	ACS configuration: CONFIGURATION_ACS_VALIDATED. Signature offset table covers 86.6% of events, CTS-ACS Spearman rho=0.8045 (correlated but non-redundant), RESISTANT mean ACS=0.6311 vs COUNTERFEITABLE=0.2241, ACS discrimination gap (0.2704) > CTS gap (0.1012). Empirical thresholds differ between profiles (A1=0.116, A2=0.324, A3=0.154)	2	B, apparatus, ACS, configuration, morphology, C1645
C1648	Two-layer gate: TWO_LAYER_GATE_SYNERGISTIC. Layer 1 (Y-credit gating) delta=0.003021, Layer 2 (cleanliness gain modulation) incremental=0.000538, combined=0.003560. Both layers contribute with synergy. A2 CCS1 reduction=1.6%. Non-A2 degradation within tolerance (A1=1.4%, A3=3.4%)	2	B, apparatus, gate, two_layer, Y_credit, cleanliness, C1643
C1649	Event-band stratification: STRATIFIED_SELECTIVITY_REJECTED. SSI=0.0 across all 5 gate configurations. No false intelligence reduction achieved. Gate is too permissive: counterfeitable signature auth_mult ranges 0.83-1.00 (all >0.5, none correctly starved). CTS weight (alpha=0.60) in ACS formula dominates, drowning out morphological configuration signal	2	B, apparatus, stratification, event_band, SSI, NEGATIVE, C1645, C1647
C1650	Landscape shift: LANDSCAPE_POLE_AGGRAVATED. A2 FORGIVING unchanged (8→8). Total FORGIVING increased by 1 (9→10, one new A1/A3 folio). Gate produces uniform advantage reduction, not surgical selectivity. Descriptive landscape classification is too sensitive to small advantage changes in borderline folios	2	B, apparatus, landscape, pole_reduction, NEGATIVE, C1646, C1647
C1651	Tiered classification: CLASSIFICATION_PARTIAL. 6-class tiered classifier (AUTH_RESISTANT through AUTH_AMBIGUOUS) covers 2323 lines, all 6 classes populated, AUTH_AMBIGUOUS only 5.4%. M1 signature agreement 76% (below 90% target) due to armed/unarmed proxy differences vs Phase 574. Class-level agreement higher	2	B, apparatus, classification, tiered_classifier, closure
C1652	Regime admission selectivity: ADMISSION_SELECTIVE. Best config REGIME_AMB_PESSIMISTIC SSI=63.5. REGIME_GATED A2 delta_adv=0.0605 > CREDIT_ONLY=0.0561, proving regime admission (gating R1-R5) outperforms credit-only (gating Y). Architecture robust: 4/4 regime configs beat credit-only control. Decisive test: gating Layer 2 (closure regime admission) works where Layer 3 (Y-credit, Phase 575) failed	2	B, apparatus, regime_admission, gate, SSI, decisive, POSITIVE, C1649, C1643
C1653	Event-band discrimination: DISCRIMINATION_PARTIAL. TP=4/5 CF signatures suppressed, TN=4/4 RESISTANT preserved, FP=0. Strong-band DYE preserved 58.7% (target 90%). Weak CF null suppression 71.4%. Gate correctly discriminates CF from RESISTANT at signature level but reduces strong-band DYE because some STRONG events land on non-RESISTANT lines (AUTH_PROTECTIVE, AUTH_THRESHOLD)	2	B, apparatus, discrimination, event_band, confusion_matrix, C1645
C1654	Landscape + CCS1: LANDSCAPE_STABLE. A2 FORGIVING pole unchanged (8→8) despite 66.2% CCS1 reduction. No new A1/A3 FORGIVING. DYE improvement does not translate to classification shifts. A2 null wins reduced 7→2. Landscape classification may be too insensitive to capture the gate's discriminative improvement	2	B, apparatus, landscape, CCS1, pole_reduction, C1646
C1655	Authenticity strength coverage: COVERAGE_PARTIAL. 2323 lines receive strength bands, all 3 bands populated (STRONG=460, MED=1729, WEAK=134). 4 structural zeros documented (AUTH_THRESHOLD+WEAK/MED, AUTH_PROTECTIVE+WEAK, AUTH_PRONE+WEAK). Surrogate agreement with Phase 574 event bands only 21.6%. Signal alignment changes: 1782 lines changed opaque, 572 changed armed	2	B, apparatus, strength, coverage, closure
C1656	Strong-band rescue: RESCUE_REJECTED. Best config=NO_STRENGTH (=P576 AMB_PESSIMISTIC). Strong preserved=69.1% (<80% target). Weak guardrail=SAFE (null wins not increased). A2 delta=0.0635 (matches P576). STRENGTH_RESCUE achieves 76.8% strong but A2 delta drops to 0.0475. The strength dimension does not improve performance	2	B, apparatus, rescue, strength, decisive, NEGATIVE, C1653, C1652
C1657	Configuration robustness: SPECIFIC. 0/3 strength configs beat NO_STRENGTH. 3/3 beat CREDIT_ONLY_4D. Architecture not robust for the strength dimension — result is config-specific (only NO_STRENGTH works). Per-config SSI: NO_STRENGTH=86.5, RESCUE=92.4, CAUTIOUS=77.8, AMB_ONLY=86.8, CREDIT_ONLY_4D=93.5	2	B, apparatus, robustness, configuration, closure
C1658	Landscape migration: MIGRATION_ABSENT. A2 FORGIVING pole unchanged (8→8). 0 migrating folios. No new A1/A3 FORGIVING. Pole reduction 0.0%. No regression. Landscape identical to Phase 576	2	B, apparatus, landscape, migration, closure
C1659	Event-local feature coverage: COVERAGE_VALIDATED. 463 events classified into 4 tiers (AUTHENTIC_RESOLVER=128, PARTIAL_RESOLVER=174, NONRESOLVING_COUNTERFEIT=161, INERT_PSEUDO=0). 2323 total lines. burden_frac_resolved range [-3.46, 1.00]. Y_gain NOT used in classification (outcome leakage avoidance)	2	B, apparatus, event_local, coverage, closure
C1660	Event legitimacy gating: EVENT_GATING_REJECTED. Best config=LINE_CLASS_CONTROL (Phase 576 AMB_PESSIMISTIC). EVENT_CLASS_FULL A2 delta=-0.0185 (vs LCC +0.0635). All event configs produce negative A2 delta. Null wins: ECF 7→8 vs LCC 7→2. Event-class gating strictly worse than morphological gating	2	B, apparatus, event_gating, decisive, NEGATIVE, C1652, C1656
C1661	Burden resolution discriminator: DISCRIMINATOR_WEAK. AUTHENTIC mean DYE_adv=0.119 > COUNTERFEIT=0.098 (direction OK). Cohen's d=0.267 (<0.3 threshold). COUNTERFEIT has 90.1% positive DYE rate — burden non-resolution does NOT mean lack of M1 advantage. Resolution coherence: AUTH 68.8% vs CF 7.5% (stark but doesn't predict DYE)	2	B, apparatus, burden_resolution, discriminator, closure
C1662	Landscape migration: MIGRATION_ABSENT. A2 FORGIVING pole unchanged (8→8). 0 migrating folios. No regression. Landscape identical to Phase 576/577	2	B, apparatus, landscape, migration, closure
C1663	Pole coherence: GRADIENT_TAIL. LOO nearest-centroid accuracy=33.3% (INSEPARABLE). 0/5 significant F-axes, 2/5 significant ablation channels. Within-forgiving cosine similarity=0.919, between-group=0.891. Lobe tightness=TIGHT. The 8 are the tail of A2's continuous gradient, not a distinct subfamily	2	B, apparatus, A2_forgiving, coherence, closure
C1664	Channel concentration: CHANNEL_CONCENTRATED. 8/8 folios have >60% share in single recovery channel. NO_R1 dominates 6/8 (f39v,f40r,f50v,f55v,f85r2,f95r2). NO_R4 dominates 2/8 (f86v5,f86v6). Pre-gate and post-gate dominant channels identical -- regime admission gating did not alter residual conversion mechanism	2	B, apparatus, A2_forgiving, channel, sub_ablation, closure
C1665	Opportunity confound: OPPORTUNITY_NEUTRAL. Event count R-sq=0.0001 on CCS1 (no explanatory power). Forgiving CTS=0.200 vs passing=0.350. Grammar bands: forgiving 80% WEAK vs passing 48.5%. E_armed: 6.7% vs 39.4%. Weaker closure events are intrinsic folio properties, not sampling artifacts	2	B, apparatus, A2_forgiving, opportunity, confound, closure
C1666	Structural endpoint: MIXED_BOUNDARY_STRATUM. F1xF2 grid (144pts/folio) + conditional 3rd-axis (F3/F5). 4 STRUCTURAL_ENDPOINT (f39v,f55v,f86v5,f95r2): no passing config. 4 PARAMETER_ACHIEVABLE (f40r,f50v,f85r2,f86v6): pass with displacement>=0.5. 0 PARAMETER_UNDERFIT. All best points at grid extreme (F1=1.6,F2=0.5). 7488 total runs	2	B, apparatus, A2_forgiving, endpoint, DECISIVE, retuning, closure
C1667	Response-surface manifold dimensionality: MANIFOLD_DIFFUSE. Space A (11 apparatus features) has effective rank 5.88 and requires 5 PCs for 80% variance. Not compressible to a low-dimensional summary	2	B_APPARATUS
C1668	Family geometry in manifold: FAMILY_GRADIENT. LOO accuracy 0.78, silhouette 0.13. Families distinguishable but extensively overlapping. A2 most elongated (ratio 1.36). A3 bridges A1-A2 (54% equidistant)	2	B_APPARATUS
C1669	Landscape alignment: LANDSCAPE_ALIGNED. SA/TD/FR classes show 2 significant KW PCs in Space A with between/within ratio 1.07. Three-pole structure reproduced in apparatus space	2	B_APPARATUS
C1670	Accent is manifold position: ACCENT_IS_MANIFOLD_POSITION. Canonical r1=0.871, max incremental R²=0.268. Folio accent is substantially captured by apparatus manifold position. Within-A2 R²=0.946	2	B_APPARATUS, ACCENT
C1671	Atom positional gradient structure: GRADIENT_HETEROGENEOUS. HEAD and TERMINAL atoms gradient heterogeneously across quintiles — some atoms are sharply position-bound, others nearly flat. e/headless most position-sensitive, o nearly position-neutral	2	B, line, atom, position, gradient, HEAD, TERMINAL
C1672	Q3->Q4 atom decomposition: CLOSURE_DISTRIBUTED. Closure step is TERMINAL-concentrated (m-terminal alone = 77% of TERM JSD) but HEAD-distributed (e-collapse + headless/a-surge). Closure and specification are mechanistically distinct (TERM cosine=0.08)	2	B, line, atom, position, closure, Q3Q4, JSD, m-terminal
C1673	Hazard x atom x position: HAZARD_POSITION_COUPLED. Safety architecture operates through specific atom-position couplings, not aggregate rates. 16 zone-specific pairs at >1.5x enrichment. Work-zone safety is k-LED (k WORK=63.2% vs t 61.2% vs e 56.1%)	2	B, line, atom, position, hazard, zone, safety, k-HEAD
C1674	Section-conditioned atom gradients: SECTION_MODULATES_GRADIENT. Sections preserve the three-zone scaffold but modulate atom deployment amplitudes. C section HEAD corr=0.76 (below 0.80). Q3Q4 JSD ratio across sections=2.2x	2	B, line, atom, position, section, gradient, modulation
C1675	Component atlas coverage: ATLAS_COMPLETE. 21 total atlas components: 5 knob axes, 11 packet types, 5 metrics. Full coverage of manifold-to-hardware bridge	3	B_APPARATUS, bridge, atlas
C1676	Instruction translation coverage: TRANSLATION_COMPLETE. All 6 macro-states, 3 line zones, 4 REGIMEs mapped as heuristics. 13 non-encodable judgment types identified. Explicitly secondary to manifold-to-knob mapping	3	B_APPARATUS, bridge, heuristic
C1677	Safety protocol derivability: SAFETY_DERIVABLE. All 5 hazard classes mapped to physical failure modes with prevention protocols. 3 safety levels translated from structural mechanisms. Operator judgment boundaries defined	3	B_APPARATUS, bridge, safety, hazard
C1678	Validation experiment feasibility: EXPERIMENTS_FEASIBLE. 7/7 experiments have available materials, defined measurements, and clear pass/fail criteria. 61 total minimum runs. 5 hardware nulls used	3	B_APPARATUS, bridge, validation, experiment
C1679	Metric bridge adequacy: METRIC_BRIDGE_COMPLETE. All 5 virtual process metrics (DVA, YGA, DYE, CTS, forgivingness) have operational physical definitions with specified sensors and formulas	3	B_APPARATUS, bridge, metrics, DYE, DVA, YGA, CTS
C1680	Manifold knob identifiability: KNOB_MAPPING_IDENTIFIABLE. All 5 F-axes (F1-F5) mapped to physical control surface candidates with directional predictions. PC1 led by abl_CLOSE_RECOVERY, PC5 led by F2	3	B_APPARATUS, bridge, manifold, knob
C1681	Zodiac category seasonal signal: SEASONAL_SIGNAL_CONFIRMED (after zodiac correction). Standard scholarship zodiac map has ≥6 misassigned folios + 2 non-zodiac pages included. Corrected confident-only map (7 folios): chi2=48.73, V=0.157, perm_p=0.018. Visual-Aries map (9 folios): V=0.138, perm_p=0.033. Signal is real but was masked by incorrect assignments	2	AZC, zodiac, category, season
C1682	Thermal seasonal gradient absent: THERMAL_GRADIENT_ABSENT. THERMAL and CONTAINMENT categories not individually significant in any mapping variant. Seasonal signal is distributed across categories, not concentrated in apparatus-specific channels	2	AZC, zodiac, category, THERMAL, CONTAINMENT, season, negative
C1683	Within-season coherence trend: COHERENCE_TREND. Approaches significance with corrected map. Consistent direction: within-season JSD < between-season JSD in all mapping variants	2	AZC, zodiac, category, coherence, season
C1684	Goat-folio seasonal identity: GOAT_PAGES_SPRING. Goat pages (f70v1, f71r) behave like Spring pages not Winter. Goat=Capricorn (Winter) kills seasonal signal, goat=Aries (Spring) preserves it. Diagnostic constraint on zodiac assignment	2	AZC, zodiac, category, season, goat, identity
C1685	Full zodiac map NOT INFERRED: ZODIAC_MAP_NOT_INFERRED. Brute-force enumeration of all 12 valid sign assignments for 5 unknown nymph folios. Best assignment (f72r3=Cancer, f71v/f72r1=Winter, goats=Spring) gives V=0.113, perm_p=0.112. Full 12-folio seasonal signal too dilute for inference	2	AZC, zodiac, category, season, negative
C1686	Within-season assignment degeneracy: WITHIN_SEASON_DEGENERATE. Swapping signs within the same season (Aries↔Taurus, Capricorn↔Aquarius) produces identical chi2/V. The 12 nominal assignments collapse to 3 distinct seasonal groupings. A season-level test structurally cannot resolve within-season ordering	2	AZC, zodiac, category, season, degeneracy
C1687	Unknown folios degrade seasonal signal: UNKNOWNS_DEGRADE_SIGNAL. Best 12-folio V=0.113 < confident-only V=0.157 (C1681). Adding 5 unknown folios weakens the signal at every possible assignment. Unknown folios have ambiguous category profiles that don't fit seasonal patterns	2	AZC, zodiac, category, season, noise
C1688	f72r3 seasonal assignment resolved: F72R3_SEASONAL_ASSIGNMENT. f72r3=Cancer (Summer) in all top-4 assignments (V=0.113). f72r3=Winter drops to V=0.092-0.098. f72r3 has most tokens (163) among unknowns. f71v and f72r1 both Winter in all top assignments	2	AZC, zodiac, category, season, f72r3
C1689	Atom compatibility partially predictable: ATOM_COMPATIBILITY_PARTIAL. Logistic regression on atom-level features predicts pairwise compatibility with AUC=0.7452. But density-matched application to real MIDDLEs yields edge Jaccard overlap of only 6.4%. Statistical predictive power exists but near-zero overlap with actual deployment edges	2	A, atom, compatibility, logistic, deployment
C1690	Atom composition breaks independent feature ceiling: COMPOSITION_BREAKS_CEILING. Empirical atom-compositional generator (HEAD+MOD+TERM with real C1475-C1487 parameters) achieves clustering 0.599±0.008, breaking C984's independent feature ceiling of 0.49. Atom composition contributes structure beyond independent features but falls far short of real 0.873	2	A, atom, composition, discrimination, generator
C1691	Slot architecture sufficient for compositional clustering: SLOT_ARCHITECTURE_SUFFICIENT. Structured-Random model (uniform HEAD weights, uniform modifier selection, no avoidance/gating) achieves clustering 0.501 = 83.6% of Empirical 0.599. The three-slot HEAD+MOD+TERM architecture, not specific parameter values, drives compositional clustering	2	A, atom, architecture, slot, composition
C1692	Cross-slot dependencies neutral for clustering: CROSS_SLOT_DEPENDENCIES_NEUTRAL. Param-Independent model (real marginal frequencies, no cross-slot avoidance/selectivity/gating) achieves clustering 0.623 >= Empirical 0.599. Avoidance rules (C1472), selectivity profiles (C1479), terminal gating (C1484) do not increase clustering. These constraints serve other purposes (diversity maintenance, degeneracy prevention)	2	A, atom, dependency, avoidance, clustering, neutral
C1693	Naive property model confirmed dead on clean baseline: NAIVE_PROPERTY_CONFIRMED_DEAD. F-BRU-003-style naive generator (8 random property bins, featureless MIDDLEs) produces clustering 0.021±0.001 on H-filtered clean baseline. Qualitative result of F-BRU-003 confirmed	2	A, property, generator, naive, negative
C1694	No dominant compositional layer: NO_DOMINANT_COMPOSITIONAL_LAYER. Ablation on Empirical model (removing one architectural layer at a time) shows all variants within 0.56-0.62 clustering range. No single layer (modifier avoidance, HEAD-modifier selectivity, terminal gating, slot syntax, HEAD structure) dominates. Compositional clustering is distributed across the architecture	2	A, atom, ablation, architecture, distributed
C1695	Deployment not compositional: DEPLOYMENT_NOT_COMPOSITIONAL. Logistic compatibility model applied to real 972 MIDDLEs at density-matched threshold: predicted clustering 0.412, edge Jaccard 0.064. The model predicts ~10,500 edges but only 1,250 overlap with the real 10,241. Atom features do not determine which MIDDLEs co-occur on lines. Discrimination manifold clustering (0.873) arises from deployment grammar (B execution), not morphological composition	2	A, A↔B, atom, deployment, grammar, discrimination, manifold
C1696	Frequency baseline high: FREQUENCY_BASELINE_HIGH. Global frequency sampling (D0) produces co-occurrence graph with clustering 0.639±0.014, explaining 73% of the manifold's 0.873 clustering. The CM null baseline (0.250) measures random edge rewiring, not co-occurrence generation. Most of the manifold's "anomalous" clustering is a natural property of frequency-weighted co-occurrence through shared lines, not a special structural feature	2	A, discrimination, manifold, frequency, baseline, co-occurrence
C1697	Section effect negligible: SECTION_EFFECT_NEGLIGIBLE. Section-conditioned frequency (D1) adds only +0.004 clustering over global frequency (D0). Currier A is predominantly Herbal; section partitioning has near-zero effect on the manifold	2	A, discrimination, manifold, section, negligible
C1698	Folio pool moderate: FOLIO_POOL_MODERATE. Folio pool restriction with uniform sampling (D2) adds +0.032 clustering but inflates density to 0.0335 (real: 0.0217). Pool restriction creates vocabulary cliques but is not the dominant manifold mechanism. Frequency weighting (D3) corrects density but reduces clustering by -0.022 while improving Jaccard by +0.045	2	A, discrimination, manifold, folio, pool, vocabulary
C1699	Frequency corrects not adds: FREQUENCY_CORRECTS_NOT_ADDS. Per-folio frequency weighting (D3) corrects density inflation from uniform sampling but does not add clustering. D3-D2 = -0.022 clustering, +0.045 Jaccard. Best model by edge overlap	2	A, discrimination, manifold, folio, frequency, density
C1700	PREFIX selectivity hurts: PREFIX_SELECTIVITY_HURTS. Adding PREFIX->HEAD compatibility filtering (D4) REDUCES both clustering (-0.106) and Jaccard (-0.049) versus D3. PREFIX constraints remove correct co-occurrence edges faster than incorrect ones. 35.2% of PREFIX*HEAD pairs forbidden in A, but filtering by these constraints is misaligned with actual line-level co-occurrence patterns	2	A, discrimination, manifold, PREFIX, HEAD, selectivity, negative
C1701	Manifold residual is content: MANIFOLD_RESIDUAL_CONTENT. Best deployment model (D3) reproduces only 28.5% of real edges. Final model (D4) achieves clustering 0.546, Jaccard 0.236. The 0.234 clustering gap (0.873-0.639) between real and frequency baseline is not explained by section conditioning, folio pool restriction, frequency weighting, or PREFIX selectivity. Residual reflects line-level content specificity — which specific MIDDLEs each folio assigns to each line	2	A, discrimination, manifold, content, residual, deployment
C1702	Folio B-side coherence weak: FOLIO_BSIDE_COHERENCE_WEAK. Within-folio B-side signature similarity is statistically significant but practically weak: within/between ratio=1.086 (only 8.6% more similar). PP Jaccard within=0.110 vs between=0.085. 11/16 signature features show significant section-level ANOVA	2	A, A↔B, folio, B-side, signature, coherence, weak
C1703	Section prediction partial: SECTION_PREDICTION_PARTIAL. Folio-level LOO-CV accuracy 43.9% (2.19x chance, passes 2x threshold). Record-level 34.8% (1.74x, fails). Top features: HEAD_headless (0.109), HEAD_o (0.103), STAGING (0.096), HEAD_e (0.093). Section signal exists in B-side signatures but is noisy at individual record level	2	A, A↔B, section, prediction, B-side, RF, LOO-CV
C1704	RI extension directional predictions fail: EXTENSION_PREDICTIONS_FAIL. 1/5 RI extension directional predictions pass Bonferroni. Only e-extension → HEAD_e enrichment confirmed. k→HEAD_k correct direction with medium effect (d=0.515) but p=0.060. h→MONITORING (d=0.023), d→TRANSITION (d=0.127), t→FLOW (d=0.184) all non-significant. RI extensions do not reliably predict B-side operational enrichment	2	A, A↔B, RI, extension, B-side, directional, negative
C1705	C475 operational divergence confirmed: C475_OPERATIONAL_DIVERGENCE_CONFIRMED. C475-incompatible record pairs (sharing no compatible MIDDLEs) produce significantly more divergent B-side signatures than compatible pairs. The discrimination manifold's compatibility geometry maps to B-side operational meaning — records with non-overlapping PP MIDDLE sets specify genuinely different B programs. Structure is pair-level, not categorical	2	A, A↔B, C475, discrimination, manifold, B-side, divergence, operational
C1706	PP content predicts B-side similarity: PP_CONTENT_PREDICTS_BSIDE. Partial Spearman rho=0.502 (controlling pool size, hub fraction, section) between folio PP Jaccard and B-side cosine similarity. Overturns C753's class-level null (r=-0.038). PP MIDDLE content genuinely predicts B-side operational similarity at token level. Signal is HIGHER after controlling for confounds, meaning size/hub confounds suppress, not inflate. Within-section rho=0.467, between-section rho=0.476	2	A, A↔B, PP, folio, B-side, content, correlation
C1707	Restricted PP MIDDLEs carry discriminative power: RESTRICTED_PP_DISCRIMINATIVE. PP MIDDLEs appearing on ≤2 A folios produce between-folio B-side distances of 0.520 vs 0.005 for multi-folio PPs (≥10 folios). Cohen's d=3.667, p=7.3e-58. Partly mechanical: hub MIDDLEs produce near-identical signatures everywhere. Restricted PPs are rare (mean 2.3 per folio). N_restricted vs folio distinctiveness correlation weak	2	A, A↔B, PP, folio, restricted, discriminative
C1708	Folio category diversity matches coverage-optimized null: FOLIO_CATEGORY_NOT_SPECIALIZED. Category entropy z=0.116 vs coverage-matched null (hub-weighted random draws). 73/114 folios have |z|<1. Real entropy 2.830 ≈ null 2.816. Folios span all 8 operational categories equally, indistinguishable from coverage-optimized random draws. Recipe specialization prediction fails	2	A, folio, category, entropy, specialization, coverage, negative
C1709	PP MIDDLE distance predicts B-side manifold position: PP_MANIFOLD_CORRELATION. Mantel test on 114 A folio pairs: PP Jaccard distance vs coverage-weighted B-side manifold centroid distance yields r=0.4226. Partial Mantel controlling pool size + section: r=0.4062. Bridge-dominant pipeline: bridge PP r=0.4278 > full > dark PP r=0.2047. Bridge MIDDLEs (77% of PP pool) carry the dominant signal	2	A→B, PP, manifold, bridge, dark-pipeline, Mantel
C1710	PP composition predicts three B-side manifold axes: PP_AXIS_PREDICTION. 3/10 axes significant after Bonferroni: F4_raw rho=-0.340 (headless infrastructure), SUSTAINED_HEAT rho=-0.227, DIRECT_FIRE rho=-0.224. 7/10 axes non-significant. Bridge and dark each independently predict 3/10 axes. Prediction is partial not comprehensive	2	A→B, PP, manifold, prediction, axis
C1711	PP-manifold correlation is section-independent: PP_MANIFOLD_SECTION_INDEPENDENT. Within-section Spearman rho=0.381. Between-section rho=0.390 (5176 pairs). Per-axis partial correlations change max 0.019 after section control. Signal is intrinsic to PP content, not section composition	2	A→B, PP, manifold, section, independence
C1712	REGIME partition is gradient-like, not discrete: REGIME_GRADIENT. All 3 methods (K-Means, Ward, GMM) select k=2 by silhouette on 22 features (12 PCs), but k=2 is NOT significant vs permutation null (sil=0.2175 < null p95=0.2343). The k=2 split is Bio vs non-Bio section membership. At k=4, genuine above-null structure exists (KM sil=0.2142 > null p95=0.1671, excess=0.047). C179's count of 4 retained as strongest non-trivial partition, but these are soft modes on a gradient, not crisp clusters	2	B, REGIME, clustering, gradient, C179
C1713	REGIME has within-section functional substructure: REGIME_WITHIN_SECTION. Within Herbal alone (32 folios), k=2 clustering yields sil=0.1676 but HEAD self-transition rate differs dramatically across subgroups. Section-residualized clustering on all 82 folios yields sil=0.1768 at k=2. REGIME is not purely a section alias — within-section operational variation exists and is functionally meaningful	2	B, REGIME, section, Herbal, functional
C1714	REGIME assignment bootstrap stability 0.76-0.80: REGIME_STABILITY. Bootstrap stability (200 resamples) yields ARI=0.80±0.15 at k=2 and ARI=0.76±0.14 at k=4. Both partitions moderately stable. The 4-REGIME partition is less stable than the binary section split but not drastically so	2	B, REGIME, stability, bootstrap
C1715	PC1 is PREFIX/kernel axis (32% variance): PC1_PREFIX_KERNEL. PCA on 22 folio features yields 12 PCs at 95% variance. PC1 (32%) loads on qo_frac (+0.326), headless_frac (-0.306), k_frac (+0.304). PC2 (17%) loads on suffix_rate (+0.348), mean_middle_length (+0.346), e_frac (+0.325). First two PCs capture 49% of variance and correspond to known structural axes	2	B, PCA, PREFIX, kernel, folio
C1716	Category trajectory flat at 8-category resolution: CATEGORY_TRAJECTORY_FLAT. Body lines within paragraphs show no systematic category trajectory after length control. 0/8 categories significant at Bonferroni alpha=0.00625, both pooled and within-section. Largest partial rho: -0.042. No serial dependence: lag-1 autocorrelation on category PC1 = -0.13. All 8 categories collapse under kernel control (T6). Extends C963 from role-fraction level to 8-category (C1250) resolution	2	B, paragraph, body, category, trajectory, position, C963, C1250, C965
C1717	Within-paragraph category diversity exceeds between-paragraph: WITHIN_PARA_JSD_HIGHER. Within-paragraph body-line JSD on 8-category vector (0.209) exceeds between-paragraph-same-folio JSD (0.188), ratio=1.11. Cross-folio JSD=0.241. Paragraph identity does NOT constrain body-line category composition beyond the folio template. Folio shuffle null JSD=0.212; within-paragraph below null in 0/100 permutations. Extends C963 and C1288	2	B, paragraph, body, JSD, category, folio, C963, C1288
C1718	Residual is weakly HEAD-structured, hub-suppressed: HEAD_STRUCTURED_HUB_SUPPRESSED. The PP manifold's 0.234 residual gap (C1701) has genuine HEAD-domain assortativity. Hub removal (top 5% by degree) increases HEAD from 0.032 to 0.051, reveals frame at 0.033, flips category from -0.030 to +0.032. Low-frequency MIDDLEs show HEAD assortativity of 0.163. Domain structure is concentrated in the frequency tail and masked by cross-domain hub bridging	2	A, manifold, HEAD, assortativity, hub, C1701, C475
C1719	Non-pipeline edges dominate the manifold residual: NON_PIPELINE_RESIDUAL. Of 6,074 residual edges (real minus D3 majority), non-pipeline edges carry 57.8%. D3 explains 86.4% of bridge-bridge co-occurrence (2095 to 284 residual) but only 1.1% of dark-dark (359 to 355) and 0.4% of non-pipeline-non-pipeline (243 to 242). Bridge triangles dominate the manifold's clique structure (28,969 of 29,153 homogeneous triangles). The frequency/folio model captures hub-mediated co-occurrence but fails for the long tail of domain-specific MIDDLEs	2	A, manifold, bridge, dark, pipeline, residual, C1701, C1139, C1140
C1720	Low-frequency MIDDLEs show strongest compositional homophily: LOW_FREQ_HOMOPHILY. In residual edges, Q1 (lowest frequency quartile) has 56.9% same-terminal, 32.6% same-HEAD, 24.6% same-category. Q4 (highest frequency) has 25.3% same-terminal, 29.4% same-HEAD, 4.2% same-category. Low-frequency MIDDLEs co-occur preferentially with morphologically similar neighbors. High-frequency MIDDLEs connect promiscuously across domains, suppressing full-graph assortativity despite genuine tail structure	2	A, manifold, frequency, homophily, terminal, HEAD, category
C1721	Terminal routing is section-parameterized, not folio-specific: ROUTING_SECTION_ONLY. Per-folio TERM→HEAD transition matrices (61 B folios, ≥100 transitions, 42-cell MIDDLE-atom vectors) do NOT discriminate folios within sections. ICC=0.0015 (≈0), token-shuffle null not exceeded. Within-section distance variance indistinguishable from noise in all 4 sections. Section structure real. C1570 criterion #1 NOT met. Strong length confound	2	B, routing, TERM, HEAD, section, folio, C1563, C1570
C1722	Section-level routing correlates with apparatus manifold: ROUTING_APPARATUS_LINKED. TERM→HEAD routing distance (JSD) correlates with apparatus manifold distance across 57 B folios: Mantel r=0.279. Survives section control: partial Mantel r=0.212. Routing PC1 aligns with accent PC1 (dynamics intensity): rho=0.603 (q<1e-5). Routing PC3 aligns with accent PC3: rho=0.586. 4/24 routing-accent correlations FDR-significant	2	B, routing, apparatus, manifold, accent, Mantel, C1670, C1367
C1723	Routing space is high-dimensional and bare-terminal dominated: ROUTING_HIGH_DIM. TERM→HEAD routing space has effective rank 11 (11 PCs for 90% variance), nearly double apparatus manifold effective rank (5.88). PC1 (26.3%) loads on bare→e (+0.55) and bare→k (+0.33); PC2 (21.5%) loads on y→headless (+0.62). Bare-terminal MIDDLEs contribute most cross-folio variance (0.0061 vs 0.0029 for y). m-terminal has near-zero variance (2.5e-5)	2	B, routing, PCA, TERM, bare, dimensionality, C1563
C1724	Routing grammar is position-invariant (MARGINAL_PRODUCT). TERM×HEAD×Quintile three-way interaction not significant. Routing varies by line position (Q4 JSD vs global=0.0209, 14x Q2's 0.0012) but entirely explained by independent positional marginals P(TERM|Q) × P(HEAD|Q). Global routing grammar (C1563) applies uniformly across all line positions. Specification→work→closure arc (C1425-C1430) produced by compositional change, not position-dependent routing rules. Universal across all 4 sections and all line-length strata	2	B, routing, position, quintile, TERM, HEAD, line, C1563, C1425, C1721
C1725	Closure zone has strongest routing discrimination (mild synergy). Position-conditional MI decomposition: interaction MI=-0.0044 bits (-7.9% of total 0.0552 bits), SYNERGY. Within each quintile, TERM→HEAD associations slightly stronger than aggregate. Q4 (closure) has highest per-quintile MI (0.0714 bits) vs Q1 (0.0496 bits). Reflects sharp compositional focus of closure: fewer active TERM/HEAD types allow grammar to discriminate more sharply among reduced options. Synergy is small (7.9%) — grammar fundamentally position-invariant (C1724)	2	B, routing, MI, synergy, closure, position, C1724, C1566
C1726	Per-rule activation profiles are compositionally driven. Individual routing rules show significant positional trends despite overall three-way interaction being non-significant: l→e declines Q0→Q4, m→o rises Q0→Q4, n→k declines Q0→Q4. Strongest per-quintile enrichment: r→a at Q4 (3.87x vs 2.23x global). Trends explained by compositional change: more r-terminal and a-HEAD at Q4 → r→a rises. No globally depleted rule becomes enriched at any quintile (T6: no position-specific exceptions). Grammar applies uniformly; profiles are readout of positional composition	2	B, routing, activation, rules, position, composition, C1563, C1724, C1671
C1727	Line ordering carries non-trivial sequential information. Within-paragraph body-line ordering is significantly smoother than shuffled. Only 8.5% individually significant — weak per-paragraph, strong aggregate. Universal across all 4 sections (B: z=-3.70, C: z=-3.00, ?: z=-2.92, H: z=-1.75) and all paragraph-length strata. Revises strong form of C670/C1233/C1429: compositional channels are independent, but structural channels (length, boundary position) carry ordering information	2	B, line, ordering, paragraph, sequential, C670, C1233, C1429
C1728	Sequential information is NOT primarily Mode A/B persistence. Full mode residualization barely changes signal: T3 z=-5.864 vs T2 z=-6.048, effect -0.648 vs -0.668. Mode accounts for ~3% of total sequential structure. Dominant channel is line length (lag-1 MI=0.178 bits, 9.3% of H(length), p<0.001), 4x stronger than suffix mode. HEAD and TERM show no significant lag-1 MI. Compositional channels carry no sequential signal; ordering information lives in structural channels	2	B, line, ordering, mode, length, MI, C1423, C1429
C1729	Paragraph boundary lines carry distinctive content (BOUNDARY_ENRICHED). First body lines (Q0) and last body lines (Q4) deviate significantly from paragraph mean: Q0 obs_norm=0.548, Q4 obs_norm=0.946. Interior positions indistinct. Last body line has strongest positional signature. Paragraph-level macro-arc from specification to closure across lines. Primary driver of sequential smoothness in C1727	2	B, paragraph, boundary, position, arc, C1425, C1430, C1727
C1730	ii-deployment follows a REGIME refinement-intensity gradient. Double-ii/single-i ratio varies significantly across REGIMEs: REGIME_4 (precision-constrained, 0.635) > REGIME_2 (output-intensive, 0.631) > REGIME_3 (transient-throughput, 0.575) > REGIME_1 (thermal-control-intensive, 0.468). No paragraph-level i-distribution signal. Context hazard test confirms ii appears in high-hazard contexts. Safety-routing mechanism (C1480-C1482) explains HOW; REGIME gradient characterizes WHERE	2	B, i-extension, REGIME, hazard, safety, C1480, C1399, C1204
C1731	Currier A has higher double-ii concentration than B. A ii-ratio=0.730 vs B ii-ratio=0.540. Within B: HERBAL highest (0.676), section B lowest (0.467), replicating C1204. A>B pattern consistent with A as specification registry (C240) recording process requirements. Does not discriminate safety-routing from redistillation interpretations — both predict A>B	2	A, B, cross-system, i-extension, C240, C1204
C1732	Folio-level safety substitution: ii and e-to-y are safety substitutes operating in complementary HEAD domains. Folios deploying high e-to-y (e-HEAD domain, C1457) deploy low ii (a-HEAD domain, C1480) and vice versa. Anti-correlation kills redistillation co-deployment prediction. Section+REGIME controlled partial rho=+0.264 — weak positive after controls does not reach significance threshold (p>0.01). FL state elevation on ii-lines entirely explained by a-HEAD embedding. Mode A residual dead null. Redistillation purpose hypothesis falsified	2	B, MIDDLE, atom, safety, substitution, folio, ii, e-to-y, C1457, C1480
C1733	Two-strategy safety architecture with forgiveness asymmetry. e-to-y pathway (preventive, e-HEAD domain) positively predicts folio forgiveness. ii pathway (transformative, a-HEAD domain) anti-predicts forgiveness. Preventive safety (avoiding hazardous territory) produces forgiving programs; transformative safety (operating within hazardous territory with categorical protections, C1482) produces less forgiving programs	2	B, MIDDLE, atom, ii, e-to-y, forgiveness, safety, folio, AXM, C1462, C1482
C1735	1512 thermal intensity alignment: held-out 1512 Brunschwig gentle/elevated fire degree distinction predicts e-to-y safe pathway rate between R1 and R3+R4 within Stars section. Instruction class entropy correlates with ke-depth after size control. Alignment is thermal intensity, NOT apparatus identity. Fire degrees do not predict REGIME distribution (P1 FAIL), k/(k+ke) within sections, r-to-a routing, or apparatus profile scores within sections (598d FAIL)	2	B, Brunschwig, REGIME, safety, e-to-y, ke-depth, C1457, C1225
C1736	Within-folio THERMAL-safety paragraph gradient: paragraphs with higher THERMAL category fraction show higher e-to-y rate and deeper ke engagement within individual folios. No systematic ordinal gradient. Section confound impossible at paragraph level. Strongest single result from Phase 598	2	B, paragraph, THERMAL, safety, e-to-y, ke-depth, C1399, C1400, C1250
C1737	Apparatus bundle alignment not confirmed for the tested Brunschwig→secondary-profile bridge family. 0/4 tests pass: Mantel geometry anti-correlated, dominant match 0.25 (all cells SEALED_VESSEL dominated), Stars R1-R3 direction 1/3 concordant, open-cycle cosine=-0.606. Robustly negative across 48 bridge variants (0% significant). DISTILLATION diagnostic clean. Result is failure of the tested bridge family, not disconfirmation of Voynich apparatus structure itself (which remains validated by C1248, C1380, C1625-C1629, C1640, C1668, C1722). P4 design concern: distill_references>=2 may not correspond to open-cycle/unseal intervention (C1247)	2	B, apparatus, Brunschwig, REGIME, secondary profiles, C1248, C1735, C1736
C1738	SEALED_VESSEL universal secondary dominance at cell-mean level: all 5 viable section×REGIME cells show SEALED_VESSEL as dominant secondary profile (range 0.328-0.609). S:R1=0.609, S:R3=0.516, H:R2=0.488, H:R4=0.374, H:R3=0.328. 4/5 non-ambiguous (margin>0.02). Compressed expected dominant-axis contrast under the tested historical bridge. Cells may still differ meaningfully in relative proportions, geometry, and distributional shape while sharing SEALED_VESSEL top-1. SV vocabulary may encode general containment/waiting operations rather than apparatus-specific sealed-vessel indicators	2	B, apparatus, SEALED_VESSEL, secondary profiles, C1248, C1249
C1739	Closure-response alignment not confirmed: historical closure-burden features (3 axes: containment density, intervention density, recycle complexity) from 431 Brunschwig 1512 recipes do not predict Voynich 7D closure-response phenotype across section×REGIME cells. 0/4 tests: Mantel r=-0.385, Stars 3/4 concordant but combined p=0.319, rank 0/3, Herbal 0/3. Annotation stable. Failure is structural: bridge assumes monotone containment→preventive safety mapping, but Voynich closure manifold is profile- and threshold-dependent (C1639-C1648, C1732-C1733). H:R2 reversal (lowest ey, highest ii) consistent with authenticity-sensitive containment loading onto transformative safety. Individual safety axes within Stars significant (see C1740)	2	B, Stars, apparatus, Brunschwig, REGIME, closure, safety, C1735, C1737, C1639, C1642
C1740	Stars safety substitution within-section concordance: within Stars, safety substitution aligns with Brunschwig operational framework at individual axis level. ey_rate R1=0.1823 > R3=0.1039. ii_rate R1=0.0605 < R3=0.0918. DYE_advantage REVERSED (R1<R3). Combined 4-axis p=0.319 (fails due to DYE reversal). First direct confirmation that safety substitution model (C1732/C1733) aligns with Brunschwig framework within-section	2	B, Stars, safety, e-to-y, ii, REGIME, Brunschwig, C1732, C1733, C1735
C1741	A2 profile categorical safety-style shift: A2 is a compound apparatus regime (high null close recovery C1639, higher authenticity threshold C1644, morphology-selective counterfeiting C1645, weak events lose to null C1642) that categorically shifts safety toward transformative intervention (ii) over preventive stabilization (e→y). Section-controlled OLS: A2 dummy coeff=-0.124, t=-5.31, p=1.2×10⁻⁶, R²=0.579. A2 mean safety_balance=-0.022 vs non-A2=0.096. Continuous forgivingness moderation fails. Stars anchor replicates: R1=0.122 > R3=0.012, p=0.002. A2 is a profile regime, not a one-dimensional forgivingness coordinate	2	B, apparatus, safety, A2, profile, REGIME, Herbal, Stars, Brunschwig, C1739, C1740, C1639, C1732, C1733
C1742	Closure authenticity modulates safety strategy: per-folio strong_close_fraction positively predicts safety_balance (ey_rate - ii_rate) after section control. Folios with more authentic closures sustain preventive safety; weak/counterfeitable closures shift toward transformative rescue. Section-controlled partial Spearman rho=0.304, p=0.008. Raw rho=0.010, p=0.932 — effect only emerges within sections. DYE orthogonal to safety: Stars rho=-0.282, p=0.204; all folios rho=0.045, p=0.702. Two independent safety modulators identified: (1) apparatus profile A2 vs A3 (discrete, C1741) and (2) closure authenticity (continuous, within-section)	2	B, closure, safety, authenticity, strong_close_fraction, C1642, C1732, C1733, C1741
C1743	Removing A2 restores Herbal thermal-intensity ordering: within Herbal A3 folios (excluding A2), R4>R3 on safety_balance. Phase 600 Herbal reversal (C1739) was specifically A2 contamination, not general Herbal behavior. Does NOT establish general law "higher REGIME = more preventive safety" (C1730 shows non-monotone global pattern; C494 identifies R4 as precision axis). Result is specific to A3 Herbal context	2	B, Herbal, A2, A3, REGIME, safety, surgery, C1741, C1739, C494, C1730
C1744	Monitor->action chain outcome distribution matches Voynich kernel directionality: pseudo-Lull E8 judgment cue consequences show stabilization-dominant asymmetry (stabilization ratio 2.39, abort fraction 1.0%), paralleling Voynich kernel k->e 4.02x, h->e 6.09x (observation -> stabilize dominant) and e->h blockage 0.004x (escalation suppressed). Brunschwig generates no monitoring passages (C1056: 0/245 recipes, 0/509 materials), so this prediction is uniquely pseudo-Lull.	2	B, kernel, monitoring, pseudo-Lull, C1056, BCSC
C1745	Recovery doctrine aligns with safety-style split: both pseudo-Lull and Voynich show preventive-dominant safety architecture. PL recovery/irrecoverable ratio=6.24 (156/25). Voynich ey/ii ratio=1.92 (mean ey_rate 0.138, mean ii_rate 0.072). Both ratios > 1.0 and same direction: preventive/forgiving pathway dominates transformative. Maps PL E6 two-strategy correction to Voynich C1732-C1733 two-strategy safety (e->y preventive vs ii transformative).	2	B, safety, recovery, pseudo-Lull, C1732, C1733
C1746	Thresholded termination gap: pseudo-Lull threshold/count ratio 13.9:1 (139 threshold-based, 10 count-based) vs Brunschwig 1.42:1 (252 threshold, 178 count), a 9.8x gap. Quality-dependent stopping (not fixed step counts) differentiates the midprocess control layer from recipe-level specification. Compatible with C1403 MONOSTATE (AXM > 50% all sections) and C1642-C1648 closure authenticity (grammar advantage only for STRONG closures).	2	B, termination, pseudo-Lull, Brunschwig, C1403, C1642, C1648
C1747	Recovery asymmetry replication: pseudo-Lull shows convergent recovery (5 failure modes, 2 correction strategies, ratio 2.5), matching Voynich C458 clamped-hazard/free-recovery asymmetry (hazard CV=0.115, recovery CV=0.824). Both systems constrain dangerous interactions tightly while allowing recovery operations to vary freely. Per-part correction density CV=0.31 further parallels recovery freedom.	2	B, recovery, hazard, pseudo-Lull, C458
C1748	Register architecture partially confirmed: pseudo-Lull operational parts (Practica, Mercuriorum, Furnis) share >= 64% of operation families with pairwise JSD 0.19-0.26, matching C1134 same-inventory-different-weighting pattern. FAILS when including Theorica (88% theoretical, overlap 36-50%). Voynich has no purely theoretical section, so the analogy is incomplete. Mean pairwise JSD=0.27 vs Voynich C1134 inter-section JS=0.124.	2	B, register, sections, pseudo-Lull, C1134, C1499
C1749	Procedure-family prototype assignment does not project onto Voynich folio structure: z-scored cosine bridge maps pseudo-Lull families (distillation, fixation, sublimation, dissolution) onto known REGIME/section manifold, not family-specific residual structure. N1 fails (theoretical not worst-fitting: distillation worst in Approach A, dissolution worst in Approach B). N2 fails (real directional score 0.056, permutation 95th=0.223, 43.5% of random permutations exceed real). Assignments capture REGIME gradients (distillation→R1/Bio, sublimation→R3/Herbal, dissolution→mixed high-R) not PL family identity. Categorical partition not recoverable despite shared operational axes. Extends C1377 (Puff material types also fail to differentiate V profiles)	2	B, pseudo-Lull, families, REGIME, assignment, C1377, C1712, C1744
C1750	Pseudo-Lull sublimation vs distillation monitoring contrast replicates in Voynich with perfect rank separation: sublimation-assigned folios h_ratio=0.235 vs distillation-assigned h_ratio=0.113, Mann-Whitney U=638, p=6.9e-10, rank_biserial=-1.0. Strengthens C1744 at family resolution — PL's monitoring-intensive family corresponds to a real Voynich axis contrast. Within-A3 thermal specificity also confirmed. Axis-level alignment genuine even though categorical assignment fails	2	B, pseudo-Lull, monitoring, h_ratio, k_ratio, sublimation, distillation, C1744, C1735
C1751	Pseudo-Lull fixation is not a valid A2/recirculation proxy under folio-mean feature mapping: only 6/82 folios assigned to fixation, 5/6 in Bio, 0/6 in A2, safety direction inverted. High-termination/high-chain PL fixation prototype selects Bio/REGIME_1/A1 folios (strong preventive safety) not predicted A2/Herbal (transformative safety). Pre-registered limitation acknowledged fixation as recirculation proxy; result confirms proxy inadequacy. The PL dimensions that most discriminate families (termination_rate, chain_rate) have no folio-level V analog	2	B, pseudo-Lull, fixation, A2, recirculation, safety, proxy, C1741, C1471
C1752	Thermal axis alignment confirmed: h_ratio_resid (residualized on section + k_ratio) negatively correlates with thermo_ke and thermal paragraph fraction. Pseudo-Lull distillation is heat-dominant (heat_rate 13.33 vs sublimation 11.37); V folios with higher monitoring residual have lower thermal burden. Survives N1 permutation (frac_exceeding=0.002), N2 random axis (0/4 pass), N3 wrong-direction (p>0.99), within-Herbal replication, and section+REGIME control. First clean historical family contrast recovered inside Voynich	2	B, pseudo-Lull, thermal, monitoring, h_ratio, distillation, sublimation, C1750, C1735, C1744
C1753	Termination/iteration family contrasts directionally correct but sub-threshold after residualization: P1 terminal_rate rho=+0.158, P2 iteration_rate rho=+0.169. PL sublimation has 2.5x termination and 2.4x chain_rate vs distillation. Both predictions in correct direction but fail p<0.05. Raw h_ratio recovers P1 — section confound partially mediates. V closure and chaining may be too line-local (C1471) for folio-level family contrast recovery	2	B, pseudo-Lull, termination, iteration, monitoring, C1471, C1746, C1398
C1754	Family contrast is distillation-vs-rest, not sublimation-specific: N4 dissolution contrast shows P3/P4 thermal predictions match dissolution (dissolution heat_rate 7.09 < distillation 13.33, same direction as sublimation 11.37). Both sublimation and dissolution are "less thermal than distillation." P1/P2 directions diverge (dissolution termination 2.59 < distillation 4.87, opposite to sublimation 12.20 > distillation). Recovered signal is a distillation-centered thermal family vs monitoring-rich non-distillation basin, not unique sublimation identification	2	B, pseudo-Lull, dissolution, distillation, sublimation, thermal, families, C1750, C1752
C1755	Paragraph distributional shape tracks monitoring axis: shape_margin (EMD_to_distillation - EMD_to_basin) vs h_resid Spearman rho=+0.525, surviving cross-folio permutation (N1 frac=0.000) and within-Stars replication. Extends C1573 (distributional shape carries folio-specific information) to PL-derived zone profiles. Secondary S2 and S3 confirm paragraph-zone distributions carry monitoring-axis information within and across sections	2	B, pseudo-Lull, paragraph, distributional, shape, monitoring, C1573, C1752, C1398
C1756	Current 4D PL zone profiles lack specificity for paragraph shape: N2 random Dirichlet profiles achieve comparable shape margins (frac_exceeding=0.062), N3 theoretical_neg profile predicts h_resid comparably. The 4D paragraph-zone representation cannot distinguish PL family profiles from generic asymmetric shapes or from PL theoretical chapters (which share operational vocabulary per C1748). Rejects this profile-construction method, not the broader PL midprocess alignment (C1744-C1748). Profile construction needs finer-grained typed features (monitoring subtypes, correction classes, action outcomes) for specificity	2	B, pseudo-Lull, paragraph, profile, specificity, N2, N3, C1748, C1749, C1754
C1757	Within-Stars paragraph shape discrimination confirmed: shape_margin vs h_resid within Stars Spearman rho=+0.739. Paragraph distributional shape carries folio-specific information beyond section membership, consistent with C1573 within-section recovery. Stars remains the cleanest historical calibration surface (C1735, C1740, C1750, now C1757)	2	B, Stars, paragraph, distributional, within-section, C1573, C1735, C1740, C1750
C1758	Threshold-authenticity subset is internally coherent in PL but its co-variate structure does NOT transfer to V Stars. P1 strong_close_fraction↔checkpoint_rate rho=-0.278 (directional contradiction — negative, not positive). P2 h_ratio↔checkpoint_rate rho=+0.249 p=0.126 (not significant). Novel feature mappings (termination→strong_close_fraction, judgment→checkpoint_rate) rejected	2	B, pseudo-Lull, Stars, threshold, closure, checkpoint, C1742, C1647, C1752
C1759	Heat-monitoring anchor marginal within Stars: A1 thermo_ke↔h_ratio rho=-0.340 p=0.056. C1752 confirmed at broader scope but insufficient power within Stars alone. Directionally correct — a power limitation, not a directional failure. Bounds where within-section co-variate transfer can be tested	2	B, Stars, thermal, monitoring, C1752, C1755
C1760	PL threshold-authenticity procedures are iterative: term↔chain rho=+0.324 p=0.051 within S_T relaxed. Chapters with high termination also have high chaining, contradicting the assumption that threshold procedures avoid iteration. Validates expert's correction (C1579, C1642-C1648). S_T strict (3-condition) yielded only n=6 chapters (below n>=12 minimum)	2	pseudo-Lull, threshold, iteration, C1579, C1642, C1648
C1761	Folio-level zone co-occurrence shows universal depletion: all 6 zone-type pairs depleted (O/E 0.378-0.789), 4/6 significant under section-stratified null (Bonferroni alpha=0.0083). THERMAL-MONITORING most depleted, extending C1399 transition-level avoidance to repertoire level. MONITORING-Phase is the most exclusionary zone. No zone pair shows enrichment. Folios actively restrict their paragraph zone repertoire beyond section ecology	2	B, paragraph, repertoire, co-occurrence, C1398, C1399, C1573
C1762	Repertoire typology: 13 of 15 possible binary zone signatures observed. Entropy 3.303 bits (84.5% max), below section-stratified null. 50% of folios mono-type. CONTAINMENT-Sealing dominates overall mono-type (22/40) due to Herbal single-paragraph folios; among genuine 2+-paragraph mono-types, THERMAL-QO leads (8/17). Stars has highest repertoire diversity (entropy=2.94), Herbal lowest (1.73). Mono-type folios have lower thermo_ke and higher CEI than multi-type	2	B, paragraph, repertoire, typology, mono-type, C1398, C1569, C1573
C1763	Repertoire type independently predicts h_ratio: nested model comparison shows 31.9% additional variance explained by repertoire type beyond PREFIX fractions + section + paragraph_count. Only feature (of 5 tested) surviving full controls. 4/5 other features (thermo_ke, strong_close_fraction, cei_total, link_density) fully absorbed by PREFIX + section, confirming PREFIX confound (C1405-C1431). Monitoring-execution balance is not fully determined by token-level PREFIX composition	2	B, paragraph, repertoire, h_ratio, monitoring, PREFIX, C1405, C1431, C1574
C1764	MP_present is best simple repertoire predictor of h_ratio: among 4 simple properties tested against Baseline A (PREFIX+section+parcount), MP_present (binary: folio has MONITORING-Phase paragraph) adds dR^2=0.083. TQ_MP_exclusion marginal. Breadth properties null. Full repertoire type (M5, 8 dummies) adds 0.241 dR^2 total but requires 7 extra parameters over M1. MP_present is the most parsimonious simple mechanism for the C1763 finding	2	B, paragraph, repertoire, h_ratio, monitoring, MP, C1761, C1763
C1765	Continuous paragraph means dominate discrete zone labels for h_ratio prediction: 3 continuous paragraph-level means (THERMAL_score, MONITORING_score, h_kernel_frac) explain 53.6% additional h_ratio variance beyond PREFIX+section+parcount, vs 24.1% for discrete zone labels (8 dummies). LOO: continuous R^2_cv=0.679 vs discrete R^2_cv=0.111. Tier 2+3 distributional features add only 2.2% in-sample and hurt OOS. The C1763 "repertoire predicts h_ratio" effect is a continuous gradient — discrete categorization (C1398) is a crude proxy that loses information	2	B, paragraph, repertoire, h_ratio, continuous, discrete, C1763, C1398
C1766	Stars-specific repertoire-h_ratio effect via MP_present: within Stars, MP_present explains 27.6% additional h_ratio variance — only section with significant single-predictor repertoire effect. Biologicals marginal. Herbal marginal via breadth not presence. Consistent with C1154: h is section-determined except in Stars where monitoring balance varies by program	2	B, Stars, paragraph, repertoire, h_ratio, monitoring, MP, C1154, C1764
C1767	Kernel ecology fully absorbs repertoire effects on h_ratio: adding k_ratio and e_ratio to Baseline A yields R^2=0.969. Against this Baseline B, MP_present adds dR^2=0.0003 and full repertoire type adds dR^2=0.0022 (both null). Algebraically expected (h_ratio=h/(k+h+e)). PREFIX fractions are poor proxies for kernel ecology — continuous paragraph means (C1765) capture what PREFIX cannot. Repertoire does not carry independent architectural information about h_ratio beyond kernel composition	2	B, paragraph, repertoire, h_ratio, kernel, PREFIX, C1763, C1765
C1768	Blind token-level monitoring prediction succeeds in Stars: expert-advisor reading raw f104r token data (atom glosses, morphology, categories) without aggregate statistics correctly predicted HIGH-MONITORING. Actual h_resid=+0.069 (rank 21/23 in Stars, strongly h-enriched). Evidence: h-kernel in compounds across all paragraphs, e-dominance over k, MONITORING-category tokens on 6-8 lines, triple/quadruple kernel tokens. Validates token-level predictive power of C1195 atom glosses, C1250 categories, C1393 positional decomposition	2	B_Stars, monitoring, h_ratio, blind_test, C1154, C1195, C1250, C1393, C1755
C1769	Stars monitoring axis encodes operational philosophy: extreme-pair comparison (f108v h_resid=-0.101 vs f107v h_resid=+0.075, both R1) reveals 5-dimensional divergence — paragraph architecture (9 large vs 20 small), kernel balance (e-dominant vs balanced), monitoring mode (passive vs active checkpoints), h morphological position (medial vs TERMINAL), sister pair selection (balanced ch/sh vs ch-dominant). Low-h = confidence programs ("trust the process"), high-h = vigilance programs ("watch constantly"). Not a parametric dial but a complete operational strategy difference	2	B_Stars, monitoring, h_ratio, paragraph, kernel, morphology, C1154, C1755, C1740
C1770	Bridge rate invariant to monitoring level within Stars: bridge rate 88.1% for f108v (lowest h_resid) and 88.6% for f107v (highest h_resid). Monitoring axis operates through token deployment (composition, sequencing, positional emphasis) not vocabulary sourcing. All Stars folios draw from the same lexicon but deploy it under different operational strategies	2	B_Stars, monitoring, h_ratio, bridge, vocabulary
C1771	h morphological position tracks monitoring philosophy: in high-monitoring Stars folios (f107v, f104r), h-kernel appears in TERMINAL compound position (architecturally significant endpoint per C1393/C1394). In lowest-monitoring folio (f108v), h is buried medially in compounds (structurally passive). Monitoring character (not just amount) varies with h_resid. When h is TERMINAL, instruction "ends with" monitoring; when h is medial, monitoring is incidental to other operations	2	B_Stars, monitoring, h_ratio, morphology, TERMINAL, C1393, C1394
C1772	Gallows-body composition association: gallows type predicts paragraph body composition at multiple resolutions with effect strength increasing at higher structure levels. Atom V=0.039, bigram V=0.065, MIDDLE V=0.087. Escalation confirms compositional not just individual-atom gallows influence on body content	2	B_paragraph, gallows, composition, C866
C1773	p-gallows direct body continuity: p-gallows paragraphs show robust p-atom enrichment in body tokens (excluding header): O/E=1.417, p=0.0001. Survives section stratification (Bio 2.058x, Herbal 1.666x, Stars 1.283x, T 5.812x). p is the only gallows type with significant self-atom enrichment	2	B_paragraph, p-gallows, self-enrichment
C1774	k-gallows complementary e-bias: k-gallows paragraphs enrich e-atoms not k-atoms. Complementary rather than self-identity continuity. Consistent with C866 (k uses e-POST 29.8%) and C521 (e=cooling)	2	B_paragraph, k-gallows, e-atom, C866, C521
C1775	Gallows ambient-context deployment: gallows selection correlates with ambient thermal/monitoring context but not event triggers. Deployment is context-conditioned not event-dispatched	2	B_paragraph, deployment, context, thermal, monitoring
C1776	Gallows-archetype non-reducibility: aggregate gallows-archetype association is section-mediated. Within-section: Stars p=0.227, Bio p=0.683, Cosmo p=0.959. Gallows and archetypes are distinct structural layers	2	B_paragraph, gallows, archetype, section
C1777	Gallows atom-substrate asymmetry: body inheritance from shared atom substrate is partial and asymmetric. Direct in p, complementary in k, null in t and f. Four gallows types have qualitatively different body ecology relationships	2	B_paragraph, gallows, atom_substrate, asymmetry
C1778	Gallows variance absorption: gallows type does not contribute unique variance to paragraph body atom ecology after sequential control for section, folio, block position, paragraph archetype, and ambient context. Forward SS: gallows\|context=6.72% of total but permutation null (200 shuffles within section) gives mean=7.16%, z=-0.61, p_perm=0.73. Mediation delta R²=0.006. Within-archetype effects (3/4 significant under simple thermal control) are absorbed by full hierarchy. Gallows function as explicit paragraph-header labels of deployment context, not independent body-ecology channels	2	B_paragraph, gallows, disentanglement, variance
C1779	Gallows header-body signal attenuation: gallows-body atom association attenuates across paragraph zones. Z1 (gallows token) V=0.238, Z2 (first-line residual) V=0.059 (confounded with C1426/C1729 first-line effects), Z3 (body lines 2+) V=0.046. Attenuation ratio Z3/Z1=0.191. All zones p<10⁻⁶. ~81% of compositional effect confined to header zone. Body signal is residual echo of header declaration	2	B_paragraph, gallows, header, body, attenuation
C1780	Gallows irreducible four-type architecture: opener/mode split (k/f vs p/t) captures genuine positional axis but only 35.5% of body-ecology variance (R²=0.00292 of 0.00823). Within-family contrasts carry 64.5%: k vs f V=0.102, p vs t V=0.041. System requires all 4 types	2	B_paragraph, gallows, architecture, opener_mode
C1781	Gallows section-conditional posture: p-gallows body O/E vectors vary across sections in direction not just amplitude. Section-to-global cosines: Bio=0.455, Cosmo=0.809, Herbal=0.817, Stars=0.746. Cross-section cosines as low as 0.233 (Bio-Herbal). Bootstrap 90% CIs all have lower bounds below 0.30. Section alters direction of gallows-body relationship in atom space	2	B_paragraph, gallows, section, stability, posture
C1782	First-body-line length declines across paragraph ordinals: first body line of later paragraphs within a folio is genuinely shorter. Header line length does NOT decline. Mean body line length also declines. NOT C963 leaking upward -- genuine cross-paragraph specification compression. Consistent across sections: Stars -0.150, Bio -0.232, Herbal -0.267	2	B, paragraph, line, length, ordinal, sequential
C1783	Paragraph structural ordering real via line length gradient: paragraph order within folios carries non-trivial structural information. 76.1% of folios individually show negative line-length gradient. First-body-line shuffle also passes. Refines C1399 which tested compositional ordering -- structural ordering is a distinct channel. TTR flat, n_lines flat: abbreviation not simplification	2	B, paragraph, ordering, line, length, shuffle, C1399
C1784	Gallows transition matrix non-random with type-specific sequential signatures: transitions highly non-random. k never self-follows (0%), positioned early as one-shot intervention. t self-clusters (46.9%) as independent blocks. p self-chains (56.2%) as sequential backbone. k/f are openers (mean pos ~0.33), p/t are body types (mean pos ~0.52), aligning with C1780 opener/mode axis	2	B, paragraph, gallows, transition, sequential, C1780
C1785	No thermal state carryover after folio residualization: raw thermal correlations across paragraph boundaries are positive (p-chain thermal r=+0.285, e_frac r=+0.485) but collapse after folio-mean removal. All-chain residualized thermal r=-0.093. Residualized correlations null or negative (anti-correlation). Each paragraph completes its thermal cycle independently. Extends C1399/C1400 to thermal state	2	B, paragraph, thermal, carryover, independence, C1399, C1400
C1786	Header atom echo into body: atom-level not token-level. Atoms o, d, k enriched in body when present in boundary token MIDDLE (gallows-controlled). C670 whole-token null preserved at atom resolution	2	B, paragraph, header, body, atom, echo, C670, C1772
C1787	Header internal positional structure: pos2 body-prediction r=0.238 (t=5.35) declining monotonically to pos7 r=0.089 (t=2.12). Position-2 dominated by sh-prefix (22.2%), qo-prefix (15.5%). Header is not flat -- early positions carry strongest specification signal	2	B, paragraph, header, position, decay, gradient, specification
C1788	Header specification register: p-atom 7.8x enriched, f-atom 7.7x, h-atom 1.9x, c-atom 1.5x vs body; e-atom 0.75x and k-atom 0.72x depleted. Header atoms are executive/modifier-class (C1541 instruction tier), not thermal-work atoms. Fixed width ~10 tokens	2	B, paragraph, header, specification, atom, enrichment, C1541, C1287
C1789	86.0% of boundary token types exclusive to boundaries; body has 49.5% gallows-containing tokens but completely different vocabulary. Header non-BT tokens: 54.2% types exclusive. Header and body draw from overlapping atom pool but non-overlapping token inventory	2	B, paragraph, header, body, vocabulary, exclusivity, boundary
C1790	Zero duplicate lines (0/2420), zero duplicate paragraphs (0/591), zero near-duplicates. Only 10 trigrams in 3+ folios, zero 4-grams in 3+ folios. Each paragraph is a unique specification, not a template instantiation	2	B, paragraph, uniqueness, duplicate, specification, C531
C1791	Header atom echo universal across sections and independent of boundary token. Incremental prediction beyond gallows+section+folio small but significant. Gallows atom is PRIMARY specification; remaining header tokens provide modest refinement	2	B, paragraph, header, body, section, universal, gallows, residual, C1772, C1777
C1792	Header transition grammar beyond gallows: (gallows, header_cluster) state pairs follow non-random sequential transitions. Header clusters independent of gallows (ARI=0.006). The specification register has sequential structure beyond gallows type alone	2	B, paragraph, header, transition, grammar, sequential, gallows, C1784
C1793	Consecutive paragraph header independence: header divergence does NOT predict body divergence. Paragraphs relate through state sequences not similarity chains. Sequential grammar (C1792) is about transitions between DIFFERENT states, not continuation of similar ones	2	B, paragraph, header, body, consecutive, independence, C1792
C1794	Specification divergence not convergence: later paragraphs within folios slightly DIVERGE in header specification. Refutes convergence prediction. Each paragraph maintains distinct specification throughout folio. Later paragraphs do not converge toward a common target	2	B, paragraph, header, specification, divergence, ordinal, C1782
C1795	Header atoms predict body operational domain: header atom fractions predict body category fractions beyond gallows+section controls. Turns C1786 statistical atom echo into functional claim: header specifies which operational domain (category mix) the body emphasizes. Control R2=0.107, full R2=0.170	2	B, paragraph, header, body, domain, prediction, atom, C1786
C1796	Paragraph shape predicts apparatus manifold: 22-dim paragraph shape vector (gallows fracs, header atoms, zone fracs, n_paras, mode_a_frac) predicts folio apparatus manifold position. First evidence that paragraph-level composition encodes folio-level operational identity. Closes paragraph→folio compositional gap	2	B, paragraph, folio, manifold, composition, Mantel, apparatus, C1709, C1722
C1797	Paragraph shape → manifold broadly distributed across sections: per-section Mantel r: Herbal=0.350, Stars=0.257, Bio=0.119. Herbal strongest, Stars significant, Bio underpowered. Effect not driven by single section. Reduced shape (10-dim, no atoms) r=0.201 — atom features add ~0.11 Mantel r	2	B, paragraph, folio, manifold, section, Herbal, Stars, Bio, C1796
C1798	Paragraph shape → manifold multi-axis: 15/110 feature-PC pairs significant after FDR correction. Dominant: zone_0×PC1 rho=-0.643, hdr_d×PC4 rho=-0.475, zone_1×PC4 rho=-0.435. Full shape outperforms C1722 routing distance and approaches C1709 PP distance. Paragraph composition is a competitive apparatus manifold predictor	2	B, paragraph, folio, manifold, axis, feature, PC, benchmark, C1722, C1709, C1796
C1799	Vocabulary completely absorbed by PREFIX composition: B-folio MIDDLE Jaccard distance→manifold collapses from r=0.257 to r=-0.028 after controlling for PREFIX JSD. Controlling for PREFIX+shape yields r=-0.041. Vocabulary carries zero independent information about apparatus manifold position; it is entirely a downstream readout of PREFIX composition	2	B, vocabulary, PREFIX, manifold, mediation, Mantel, C1709, C1801
C1800	Paragraph shape carries independent deployment signal: 22-dim shape vector→manifold partial r=0.163 after controlling for both PREFIX composition and vocabulary. Half the raw signal (0.317→0.163) survives. Deployment architecture (HOW MIDDLEs are arranged into paragraphs) encodes apparatus identity independently of vocabulary composition	2	B, paragraph, shape, deployment, manifold, PREFIX, independent, C1796, C1799
C1801	PREFIX composition is strongest single apparatus manifold predictor: PREFIX JSD→manifold Mantel r=0.476, partial\|section r=0.437. Stronger than vocabulary, shape, or combined. PREFIX composition determines both which MIDDLEs appear (C1799) and contributes to apparatus position independently of deployment	2	B, PREFIX, manifold, Mantel, prediction, C1405, C1709, C1796
C1802	Combined vocab+shape improvement real but modest: alpha=0.5 combination yields r=0.358 vs max individual r=0.317, improvement +0.040. Below pre-registered +0.05 complementary threshold. T4-null permutation test confirms improvement is real (frac=0.002, <5%). Best exploratory alpha=0.4 yields r=0.361. Channels add modestly but do not reach full complementarity	2	B, vocabulary, shape, combined, manifold, alpha, complementary, threshold
C1803	Asymmetric partial Mantels: shape\|vocab partial r=0.263 vs vocab\|shape partial r=0.182. Both significant before PREFIX control. After PREFIX control, shape survives but vocab collapses (r=-0.041). The apparent bidirectional complementarity is illusory — only shape carries genuinely independent apparatus information	2	B, vocabulary, shape, partial, Mantel, asymmetry, PREFIX, C1799, C1800
C1804	Within-Herbal deployment dominance: among 27 Herbal folios, shape\|PREFIX partial r=0.337, vocab\|PREFIX partial r=0.098. Shape dominates within-section; vocabulary is marginal. Raw within-Herbal: shape r=0.347, vocab r=0.146 (ns). Deployment signal operates within-section, not as section proxy	2	B, Herbal, shape, vocabulary, PREFIX, within-section, C1797, C1800
C1805	Section retention strong across all channels: vocab\|section retains 79.4% of raw r, shape\|section retains 90.4%, combined\|section retains 87.2%. No channel is primarily a section proxy. Shape is least section-dependent. Bridge-only vocab ≈ dark-only vocab in B-space, inverting the A-side pattern (C1709) due to dark pipeline section hyper-modulation (C1148)	2	B, section, retention, partial, Mantel, bridge, dark, C1148, C1709
C1806	Stars within-section h_ratio REGIME gradient: R3 h_ratio exceeds R1 with perfect separation (U=0, all 12 R3 values > all 10 R1 values). R3 mean=0.219, R1 mean=0.101. Extends C1750 (sublimation > distillation monitoring) to REGIME level. Pre-registered in OPPOSITE direction (R1>R3) due to C1750 misreading; corrected direction confirmed post-hoc. Consistent with C1735 (elevated fire = more thermal demand) and C1752 (monitoring-thermal anti-correlation). Requires replication as pre-registered prediction	2	B, Stars, REGIME, h_ratio, monitoring, C1735, C1750, C1752, post-hoc
C1807	Brunschwig elevated-fire recipes have higher monitoring keyword density than gentle-fire: conditional density 0.00298 vs 0.00184, raw density 0.00444 vs 0.00328. Both measures agree. Complex procedures require more checkpoint instructions. Corrects assumption that gentle = more monitoring-intensive. Brunschwig-internal empirical fact independent of Voynich data	2	Brunschwig, monitoring, fire_degree, recipe_structure
C1808	Section significantly affects 13/14 PREFIX fractions (mean eta2=0.21) but explains only LOO R2=0.14 of PREFIX variance. REGIME adds near-zero within sections (Herbal 1/14 sig, Stars 3/14 sig). Section effect is real but modest; REGIME contributes almost nothing to PREFIX beyond section	2	B, section, PREFIX, REGIME, KW, eta-squared, C1405, C1406
C1809	Hierarchical variance decomposition of PREFIX composition: section+REGIME+kernel+headless LOO R2=0.11 (excluding definitional BARE-headless overlap; 0.18 including BARE). qo most section-determined (LOO R2=0.58); or/tch/ar unpredictable (LOO R2<0). ~89% of PREFIX composition unexplained by structural variables	2	B, PREFIX, variance, section, REGIME, kernel, LOO, C1169, C1715
C1810	PREFIX composition retains 81.4% of apparatus manifold correlation after controlling for section+REGIME+kernel+headless. Kernel+headless control alone retains 94.5%. PREFIX carries independent manifold information not mediated by section, REGIME, or kernel ecology	2	B, PREFIX, manifold, apparatus, independence, Mantel, C1801, C1715
C1811	Within-folio paragraph PREFIX composition ICC=0.185 (81.5% of variance within-folio). Within-folio JSD (0.328) exceeds between-folio JSD (0.240) by 1.37x. PREFIX composition is paragraph-level, not folio-level. sh most folio-consistent (ICC=0.382); or/pch/ar near-zero (ICC<0.05)	2	B, PREFIX, paragraph, folio, ICC, design_freedom, C1182, C1399, C1573
C1812	PREFIX composition is an independent paragraph-level design parameter, not downstream of section, REGIME, or kernel ecology. Section explains ~14%, REGIME near-zero within sections, kernel retention 94.5%. Folio identity = statistical ensemble of paragraph-level PREFIX choices. REGIME is emergent from PREFIX composition, not a cause of it. Closes architectural question of how folio identity arises	2	B, PREFIX, design_freedom, paragraph, manifold, synthesis, C1405, C1569, C1573, C1801
C1813	Rosettes atom inventory shared with B: character-level Jaccard=0.950, 0 novel atoms, 0 suffix exclusion violations ({k,t,p,f,c} absent from suffixes). Slot compliance 31.3% raw but misleading — 47.3% of violations are compound MIDDLEs with internal HEAD/TERM atoms, 21.4% HEAD-HEAD bare pairs. Universal atom substrate (C1499) confirmed for rosettes. Modifier JSD=0.054 (marginal, near 0.05 threshold)	2	Rosettes, atoms, substrate, Jaccard, C1499, C1511
C1814	Rosettes o-HEAD arrangement enrichment 3.30x vs B (37.1% vs 11.2%) — highest of any system. Cross-system gradient: Rosettes(37.1%) > A(28.5%) > AZC(22.4%) > B(11.2%). HEAD profile closest to AZC (JSD=0.024 vs JSD=0.096 to B). Headless rate 22.3% (below AZC-adjacent 25-35% range due to o-HEAD crowding). Extends C1559 o-HEAD gradient and C1502 AZC enrichment to rosettes endpoint	2	Rosettes, HEAD, o-atom, arrangement, gradient, C1388, C1502, C1559
C1815	Bridge backbone in rosettes deploys with A-side HEAD distribution: JSD ros-A=0.050 < ros-B=0.090. Terminal stability preserved across systems (max JSD=0.046). 38/85 bridge types present, 286 bridge tokens. Extends C1507 (bridge HEAD redistribution) — rosettes are the A-adjacent endpoint of bridge deployment	2	Rosettes, bridge, HEAD, A-side, terminal, C1506, C1507
C1816	C1132 dual population (classified/unclassified) converges at atom level: HEAD profile JSD=0.021 between populations. Both are o-HEAD dominant. Classified e/k/t HEAD share=26.9% (not 55% as predicted). Unclassified headless=26.4%. Compound bridge atom rate 100% (67/67). The dual population is vocabulary-level (MIDDLE length, compound rate, bridge rate) not domain-level. All rosettes content serves arrangement function regardless of vocabulary stratum	2	Rosettes, dual_population, HEAD, convergence, C1132
C1817	Rosettes entity operational uniformity at 8-category level: mean pairwise category JSD=0.074 across 9 rosettes, below bootstrap 95th percentile threshold 0.106 (1000 permutation resamples). All entities share common operational profile. Extends C1128 (generic indexing) from vocabulary to operational level	2	Rosettes, category, uniformity, bootstrap, C1128, C1250
C1818	Rosettes spatial non-coherence at category level: adjacent-pair mean JSD=0.080, non-adjacent=0.073, delta=0.007 < 0.02 threshold. Entity operational character is NOT organized by physical proximity. Octagonal adjacency graph from PATH entities. Extends C1128 generic indexing to category-level spatial test	2	Rosettes, spatial, adjacency, category, C1128
C1819	HEAD-category dissociation in rosettes: HEAD closest to AZC (JSD=0.026), category closest to B (JSD=0.037). Mechanism: all tokens drive HEAD toward AZC o-enriched profile; classified-only tokens (bridge-dominated) drive category toward B execution profile. Expert consensus: compilation interface between declarative (AZC-like) and executable (B-like) manuscript layers	2	Rosettes, HEAD, category, dissociation, AZC, B, compilation, C1127, C1502, C1506
C1820	Per-entity dual population category divergence: within-entity classified/unclassified category JSD ranges 0.116 (NE) to 0.646 (SW), mean=0.267. C1132 dual population manifests strongly at category level with large entity-specific variation. SW extreme (classified=OPERATION, unclassified=MARKING). CENTER minimal (0.124) = integration hub	2	Rosettes, dual_population, category, C1132, entity_variation
C1821	EAST rosette e-HEAD anomaly: only entity with e-HEAD > o-HEAD (31% vs 25%), highest kernel density (32.3%), OPERATION 44.4% among classified. ok-prefix dominance (10/32 tokens). Most execution-like rosette entity, displaced from AZC-like metalayer profile toward B execution character	2	Rosettes, EAST, e-HEAD, execution, anomaly, C1475
C1822	CENTER rosette integration hub: lowest dual-population JSD (0.124), highest headless rate (32.8%), most balanced HEAD distribution, largest token count (67). Both vocabulary layers encode same operational context. Spatial analog of AXM universal attractor (C978)	2	Rosettes, CENTER, integration, headless, convergence, C978, C1132
C1823	CLOCK entity zero-energy monitoring: k-kernel=0%, FLOW=50%, zero energy modulation. Indexes pure monitoring/flow operations without thermal input. Unique among all Rosettes entities. 6 tokens (low power)	3	Rosettes, CLOCK, kernel, monitoring, flow
C1824	Rosettes visual-grammar independence at entity level: composite alignment score 0.156 vs permutation null mean 0.338, p=0.888 (10,000 shuffles). Visual imagery does NOT predict grammar profiles. C138 illustration epiphenomenality holds at the metalayer entity level. Three pre-registered hypotheses (liquid->e-HEAD, plan_view->o-HEAD, complexity->compound) all fail or show negligible effect. H1 reversed (liquid entities have LOWER e-HEAD). Framed as C138 exception test with contaminated descriptions — null confirmed despite favorable bias	2	Rosettes, visual, grammar, correlation, C138, C140, independence
C1825	Rosettes visual complexity co-varies with grammar diversity: rho(feature_count, mean_pairwise_JSD)=0.533. Entities with more complex visual descriptions are more grammatically distinctive. Does NOT mean visual content predicts grammar content — both may reflect functional prominence. C1817 uniformity (mean_JSD=0.074) holds at aggregate, but diversity gradient exists	2	Rosettes, visual, complexity, diversity, grammar, C1817
C1826	Rosettes spatial non-prediction replicated at category level (Phase 621): mean adjacent JSD=0.080, non-adjacent=0.073, delta=0.007. Independent replication of C1818 within Phase 621's correlation framework	2	Rosettes, spatial, adjacency, replication, C1818
C1827	Compound-context category alignment persists through progressive confound removal: N0 (global) 4.94σ -> N1 (within-folio) 3.85σ -> N2 (folio+position) 4.14σ -> N3 (folio+PREFIX) 3.29σ, all p<0.001, 67% of global effect retained after tightest control. Cross-line diagnostic ratio 0.991 confirms folio-mediated, not line-specific	2	B, compounds, categories, confound removal, C1214, C1176
C1828	Compound atom composition constrained below folio base rate: synthetic random-folio-pool draws score 0.387 vs real compounds 0.348, difference -10.25σ. Morphological rules (C1060 atom position grammar, C1215 slot compliance) reduce generic context alignment. Compounds are category-specific, not category-generic	2	B, compounds, morphology, synthetic control, C1060, C1215, C935
C1829	Compound information content verdict COMPOUND_RESIDUAL_SIGNAL: within-folio signal exists (P2/P3 PASS at 3.85σ/3.29σ) but compounds not optimized for context matching (C0 FAIL at -10.25σ). Residual reflects line-level homogeneity (C1214) through shared atom substrate, not specification encoding. Extends C935 "operationally redundant"	2	B, compounds, specification, verdict, C935, C1214
C1830	Sequential channel census: only 2/18 channels show significant lag-1 MI between consecutive body lines. Length MI=0.359 bits and PREFIX JSD MI=0.047 bits. All 16 other channels null at Bonferroni alpha=0.00278. Extends C1728 from 3 to 18 channels	2	B, sequential, MI, line_ordering, C1727, C1728
C1831	Ablation non-additivity: length accounts for only 26% of smoothness ablation signal, not predicted >60%. Sum of single-channel ablation deltas=0.281 relative to baseline=0.186. Channels share redundant information through structural coupling, not independent streams	2	B, sequential, ablation, C1727, C1728
C1832	Transfer entropy backward-dominant: TE(future→past) > TE(past→future) for both significant channels. Length asymmetry=-0.868, PREFIX JSD asymmetry=-0.922. Line features contain more information about preceding than following lines. Inconsistent with simple sequential generation	2	B, sequential, transfer_entropy, directionality
C1833	Safety alternation null: no ey/ii cross-MI between consecutive lines. Preventive and transformative safety atoms show no line-level alternation pattern. Extends C1732 to sequential context	2	B, safety, ey, ii, sequential, C1732
C1834	Within-paragraph sequential exclusivity: body-body MI >> cross-paragraph MI for all channels (length BB=0.359, CP=0.000; total BB=0.690, CP=0.087). Paragraph boundaries are complete sequential resets at full feature resolution. Extends C1785 from thermal carryover to all 18 channels	2	B, sequential, paragraph_boundary, C1785, C1793
C1835	CTS-conditioned routing null: no CTS tercile shows significant TERM→HEAD MI. Terminal-to-HEAD routing is strictly token-local. C1563 (token-level routing real) and C1728 (line-level null) operate at genuinely orthogonal scales	2	B, CTS, routing, terminal, HEAD, C1563, C1728
C1836	Partial complexity gradient: 3/9 features show genuine body-position gradients surviving length control. Modifier entropy decreases, atom diversity increases, distinct frames increase. Conditional entropy rate killed by length control. Strongest in sections B and H	2	B, complexity, gradient, paragraph, body_position, C1206, C1782
C1837	Anti-parallel boundary divergence: first-line and last-line divergence vectors from interior have cosine=-0.989. Last-line enriched in length, PREFIX JSD, and category entropy. First-line shows no significant enrichment at Bonferroni alpha. Boundaries are distinctive in OPPOSITE directions. Extends C1729 to channel-resolved decomposition	2	B, boundary, paragraph, first_line, last_line, C1729
C1838	Grammar temperature section-stratified: T_composite mean=1.926 (range 1.479-2.439). Section B=2.063, H=1.806, S=1.972. Raw quire correlation rho=0.352 disappears after section residualization. Grammar compliance is section-determined, not quire-ordered. NOT pre-crystallized (section variance significant)	2	B, grammar_temperature, section, compliance, C1360, C1440
C1839	Consecutive folio coherence without global ordering: Mantel test significant but PCA PC1 vs quire null. Section-residualized maturity vectors show local coherence within quires but no global compositional gradient. Consistent with C1399/C1400 independence at global scale, new finding of local coherence	2	B, folio, quire, coherence, Mantel, PCA, C1399, C1400
C1840	B paragraph arc signatures form a CONTINUOUS_MANIFOLD: section-residualized silhouette peaks at 0.075 (k=2), far below 0.15 threshold. No discrete template types exist in the 27-dim arc feature space (9 features x 3 boundary-aware bins). 75 eligible paragraphs (>=6 body lines) from 528 total (85.8% exclusion). Falsifies the hypothesis that paragraphs collapse into a small template library	2	B, paragraph, clustering, arc_templates
C1841	Bin permutation IMPROVES clustering (null/real silhouette ratio=3.49): the universal OPEN->INTERIOR->CLOSE gradient spreads paragraphs across feature space rather than concentrating them into types. Pool shuffle (N1, ratio=1.79) and within-folio shuffle (N4, ratio=1.77) also inverted. The positional arc is a shared grammar property, not a paragraph differentiator	2	B, paragraph, positional, null_model, C1836, C1729
C1842	OPEN and CLOSE bins show positive cosine similarity (0.967) across 9 compositional features (log_ke, h_rate, headless, mode_a, opacity, cat_entropy, line_length, m_term, dark_frac). Unlike C1837's anti-parallel finding (cosine=-0.989) at atom enrichment level, compositional features yield similar boundary profiles. Anti-parallel structure operates below arc feature grain	2	B, paragraph, boundary, C1837
C1843	REGIME does not mediate paragraph arc shape: REGIME-template ARI=0.004, Cramer's V=0.065. Despite REGIME driving PREFIX (C1404, R2=0.736), this does not produce arc template types. REGIME parameterization affects token-level composition but not paragraph-level trajectory shape	2	B, paragraph, REGIME, C1404, C1405
C1844	Arc templates orthogonal to C853 static taxonomy: ARI(arc_clusters, C853_k5)=0.035. Dynamic positional arc features provide no clustering value beyond C853's static features (line count, HT delta, EN rate). Paragraph variation is continuous on both static and dynamic axes	2	B, paragraph, clustering, C853
C1845	Section weakly affects raw arc clustering: Cramer's V=0.154 for Pass A (raw, non-residualized). Unlike most structural features where section is the dominant axis, arc shape is minimally section-determined. Consistent with the universal grammar arc being shared across sections	2	B, paragraph, section, C1838
C1846	Within Herbal, paragraph arc clustering is unstable: bootstrap ARI=0.40 (below 0.50 stability threshold). Even the largest section produces no robust within-section template structure. Per-section template diversity entropy=0.984	2	B, H-section, paragraph, bootstrap
C1847	Header features do not predict arc template above chance: LOO accuracy=0.56 vs chance=0.50. Gallows type alone (0.63) outperforms full header features. Templates lack specification-level reality, confirming arc shape is not header-determined. Template ordering within folios is null, consistent with C1399	2	B, paragraph, header, gallows, C1399, C1795
C1848	Short paragraphs (0-4 body lines, 85.8% of B) NOT truncated beginnings of long paragraphs: position-matched subsample null fails at pooled level (4/11 features pass KS p>0.05, need 8+). Both position-matched and random subsamples fail similarly — pooled distinctness is driven by section composition mismatch, not positional truncation	2	B, paragraph, stratum, subsample, C1206
C1849	Section dominates stratum variance: section x stratum V=0.468. After section residualization, 8/11 paragraph features become stratum-invariant (SHORT vs LONG). Within Recipe: 10/11 invariant. Golden folio (48 folios with both strata from same section): 7/11 invariant. Most apparent stratum effects are section selection artifacts	2	B, paragraph, section, stratum, C860, C1404
C1850	Three features show genuine stratum effects after section control: cat_entropy, tokens_per_line, m_terminal_rate. All length-mechanical, not operational mode differences	2	B, paragraph, stratum, features, length_residual
C1851	Zone classification (C1398) stratum-independent: V=0.098 across MINIMAL/SHORT/LONG. MINIMAL paragraphs span all operational zones uniformly (OPERATION 56%, THERMAL_QO 29%, CONTAINMENT 13%, MONITORING 2%). Within Recipe: V=0.101, p=0.447. Short paragraphs are compressed general-purpose units, not zone-specialized	2	B, paragraph, zones, stratum, C1398
C1852	HEADER_ONLY paragraphs overwhelmingly non-gallows-initial: 87.8% (79/90) have no gallows-initial token. Opener fraction (k+f) = 4.4% (lowest of all strata vs LONG 8.9%). k-fraction enriched in header atoms, o-fraction depleted. Reverses C1780/C1784 prediction — HEADER_ONLY are NOT executive gallows declarations	2	B, paragraph, header_only, gallows, C1780, C1784
C1853	HEADER_ONLY do not create paragraph dependencies after section control: post-HO paragraphs differ in 8/11 features pooled (section confound) but 0/11 within Recipe (2 post-HO paragraphs). Punctuation function borderline: zone change rate 64.7% vs baseline 47.7%, permutation p=0.06 (not significant). Consistent with C845 self-containment	2	B, paragraph, header_only, independence, C845, C1399
C1854	No anti-parallel arc in category-level feature space: first/last body line cosine=+0.999 at all strata (MINIMAL 0.9992, SHORT 0.9992, LONG 0.9993). C1837's anti-parallel finding (cosine=-0.989) operates at atom enrichment grain not captured by 12 category-level features. Caveat: features not z-scored, tokens_per_line (d>2.0 first vs last) dominates cosine	2	B, paragraph, arc, boundary, C1837, C1842
C1855	Kernel h-rate declining gradient (C1206) not detected at paragraph body-position level in any stratum. SHORT: rho=-0.078, p=0.086. LONG: rho=-0.035, p=0.278. MINIMAL: rho=-0.041, p=0.539. C1206 gradient may operate at finer position resolution, within specific sections, or at sub-paragraph scale not captured by between-body-line analysis	2	B, paragraph, kernel, gradient, C1206
C1856	Header-body feature coupling increases monotonically with paragraph length: MINIMAL mean|rho|=0.070, SHORT 0.078, LONG 0.098. Longer paragraphs allow more header→body prediction. Consistent with C1795 (dR2=+0.063). Coupling does NOT increase with shortness — short paragraphs are more header-independent	2	B, paragraph, header, coupling, C1795
C1857	HIGH-count folios (9+ paragraphs) show stronger sequential organization: steeper first-line length gradient, more structured gallows transitions, MORE paragraph diversity (mean within-folio JSD=0.146 vs LOW 0.119). HIGH-count folios are internally heterogeneous recipe collections with strong ordering	2	B, folio, paragraph, organization, gradient
C1858	Section-specific truncation: within Recipe, MINIMAL paragraphs pass position-matched subsample null (8/11 features, n_real=163, n_synth=44). Recipe MINIMAL specifically resembles truncated beginnings of Recipe LONG. B-section (9/11, n_real=5) and H-section (9/11, n_real=12) show same pattern. Pooled failure (C1848) is driven by cross-section composition mismatch	2	B, paragraph, section, Recipe, truncation, C1848
C1859	PP Jaccard clustering exceeds permutation null (sil=0.057 vs null p95=0.014, k=2) but is section-dominated (V=0.628). Cluster 1=23P/14H (Pharma-heavy), Cluster 2=74H/3P (Herbal-dominant). Within-H clustering marginal (sil=0.039). PP composition clusters primarily reflect the H/P section boundary	2	A, A↔B, clustering, section, C1706, C1709
C1860	A→B bridge signal is FEATURE-CHANNELED not holistic: overall Mantel r=0.043 but 18/840 per-feature Spearman pairs significant at Bonferroni p<0.005. HEAD identity is the primary channel. The bridge carries specific feature channels, not diffuse context-to-consequence alignment	2	A↔B, bridge, mantel, feature_channels, C1706, C1709
C1861	Bridge MIDDLE HEAD redistribution strongly non-random. Dominant pathway: A-o→B-k accounts for 38/84 bridge MIDDLEs (45%). Self-transition rate=45.2%. A-side HEAD predicts B-side HEAD assignment with high fidelity per channel	2	A↔B, bridge, HEAD, redistribution, C1507
C1862	Bridge MIDDLEs form 6 sharp functional groups by B-consequence (sil=0.751, best ever for internal bridge structure). Groups are HEAD-homogeneous: G1=o-HEAD(14), G2=e-HEAD(16), G3=t-HEAD(6), G4=k-HEAD(9), G5=headless/a(33), G6=a/headless(6). HEAD is the primary differentiator of bridge MIDDLE B-side function	2	A↔B, B, bridge, clustering, functional_groups, C1264, C1500
C1863	Restricted-PP density (fraction of PP MIDDLEs appearing on ≤2 folios) differs by PP cluster. Cluster 1 (P-heavy) has 2× density (0.053 vs 0.026). Pharma-section folios carry more folio-specific PP vocabulary, consistent with C1707 restricted-PP discrimination	2	A, PP, restricted, cluster, section, C1707
C1864	PREFIX ol_or is 3.4× enriched in Cluster 1 vs Cluster 2. PREFIX da enriched in Cluster 2. PREFIX qo marginally different. PREFIX composition differentiates PP clusters beyond section assignment, consistent with C1801 (PREFIX as strongest manifold predictor)	2	A, PREFIX, cluster, C1801
C1865	Folio-level A→B correlations are emergent properties of aggregation. Individual MIDDLE-level Mantel r=0.043 (n.s.). The 10-SD folio-level signal arises from summing many weak per-MIDDLE channels, not from holistic MIDDLE-level alignment	2	A↔B, bridge, aggregation, C1706, C1709
C1866	RI Jaccard is higher within PP-cluster than between but below the 1.2 threshold. Weak evidence that operational similarity tracks identification similarity. Statistically significant but practically small	2	A, RI, PP, cluster, identification
C1867	A→B bridge carries signal through 4 independent HEAD channels with channel-specific preservation: head_e rho=0.675, head_o rho=0.617, head_k rho=0.449, head_a rho=0.456. Cross-HEAD prediction is near-zero. The bridge operates as parallel HEAD-typed pipelines, not a unified transformation	2	A↔B, bridge, HEAD, channels, C1507
C1868	B-side functional groups show HEAD→category specialization: G1(o-HEAD)=OPERATION/MARKING/FLOW, G2(e-HEAD)=THERMAL/OPERATION/TRANSITION, G3(t-HEAD)=FLOW, G4(k-HEAD)=THERMAL/STAGING. HEAD identity constrains operational category assignment in B, extending C1507 redistribution to category-level consequences	2	B, bridge, HEAD, category, functional_groups, C1507
C1869	5 pilot folio decode cards (f58v, f8r, f58r, f101v2, f101r1) show complete A→bridge→B chains. Cross-folio PP Jaccard distance does NOT predict B-side operational cosine distance or manifold distance. Confirms MIDDLE-level signal is not holistic at pilot scale	2	A↔B, bridge, decode_cards, pilot, C1706
C1870	BRIDGE_FEATURE_COHERENT_NOT_HOLISTIC verdict: A→B bridge carries operationally meaningful signal through HEAD-typed feature channels (P5/P6/P7 pass strongly) but holistic context→consequence prediction fails. PP clustering section-dominated (V=0.628). Bridge is parallel HEAD-typed pipes, not a single translation layer. 6 PASS, 3 FAIL, 1 INCONCLUSIVE	2	A↔B, bridge, verdict
C1871	All 4 HEAD-channel features (k, h, e, t) discriminate REGIMEs at Bonferroni significance, survives within-Herbal replication. k: H=44.7, h: H=43.8, e: H=31.7, t: H=46.8. HEAD-channel organization is strongly REGIME-structured	2	B, REGIME, HEAD, within-Herbal
C1872	k_ratio INVERSELY correlated with REGIME ordinal/fire degree, within-Herbal confirmed (H=39.8). k-HEAD tokens index thermal management/regulation intensity, not thermal energy delivery. R2 (fire degree 1, gentlest) has highest k_ratio (0.418), R4 (fire degree 4, strongest) has lowest (0.221)	2	B, k-channel, REGIME, thermal
C1873	e-channel (e_ratio) differentiates Stars R1 vs R3, replicating C1735 at HEAD-channel resolution. PL correction_rate shows directional alignment	2	B, e-channel, Stars, C1735
C1874	PL within-distillation chapter distance does NOT correspond to V within-R1 folio HEAD-channel distance. PL Theorica null r=-0.176, shuffled null r=0.003. Within-family structure mapping fails completely	2	A↔B, cross-family, PL, distillation
C1875	PL Theorica chapters show zero correlation with V HEAD-channel profiles. Negative control confirmed: non-operational PL text has no V HEAD-channel signature	2	cross-family, PL, negative-control
C1876	PL chapter length does NOT predict V HEAD-channel features. Null control confirmed: chapter length artifact excluded	2	cross-family, PL, null-control
C1877	Cross-channel leakage via 4-REGIME mediation measured at 0.513 mean |off-diagonal rho|, but n=4 makes this measurement unreliable. Channel independence NOT assessable at this resolution. Requires within-REGIME variance analysis for proper test	2	B, channels, REGIME
C1878	Brunschwig fire degree ordering weakly consistent with V k_ratio REGIME ordering. Directional agreement present but far below significance — power insufficient for 3-point calibration	3	cross-family, Brunschwig, k-channel
C1879	LOO REGIME prediction from PL features: mean MAE=0.11, worst R4 MAE=0.19. PL family features are poor predictors of individual REGIME HEAD-channel profiles. R4 (precision axis, C494) is least predictable	2	cross-family, PL, REGIME
C1880	PL-to-V calibration operates at domain level (distillation-vs-rest per C1754), not at per-channel level. HEAD-channel structure is V-internal organization, not externally calibratable by PL features alone. PL subtype features at chapter resolution do not map to V folio-level HEAD-channel variation	2	A↔B, cross-family, PL, HEAD
C1881	CHANNEL_DISCRIMINATIVE_NOT_STRUCTURALLY_CALIBRATED verdict: HEAD channels discriminate REGIMEs strongly (V-internal), e-channel has external Stars calibration, but PL feature structure does not map to V HEAD-channel structure. 4 PASS / 3 FAIL	2	A↔B, B, phase-verdict
C1882	8D residual matching of distillation chapters to R1 folios (TRAINING SET, features tuned on this task): 9/16 confident matches (ratio>1.15), mean ratio 1.284, 11 unique NN targets out of 32 folios. Validation via C1885 cross-family and C1887 permutation	2	A↔B, cross-family, PL, REGIME, matching
C1883	CV stability: 11/16 distillation chapters have >40% consensus folio assignment across 500 feature-subset trials (sampling 60-80% of 8 dimensions per trial). Matching is robust to feature perturbation	2	A↔B, cross-family, PL, stability
C1884	Three highest-confidence recipe-folio assignments from content interpretation: Ch19 (aqua vitae composite, 9x distillation) -> f75r, Ch18 (element separation, graduated heating) -> f76r, Ch12 (mercury sublimation, color monitoring) -> f113v. Content alignment is interpretive, not structural	4	A↔B, cross-family, PL, content
C1885	Cross-family replication with frozen 8D features (no re-tuning): sublimation->R3 4/7 confident (57%), dissolution->R1 5/15 confident, fixation->R3 3/10 confident. Features generalize beyond training family. Sublimation strongest, consistent with C1750/C1752 distillation-sublimation contrast	2	A↔B, cross-family, PL, REGIME, replication
C1886	Wrong-regime negative control: distillation->R4 collapses to 1/16 confident, mean ratio 0.863 (below 1.0 = worse than random). Distillation->R3 degrades to 4/16, ratio 1.017. Feature set is regime-discriminating, not noise-accepting	2	A↔B, cross-family, PL, REGIME, negative-control
C1887	Within-family permutation test: real optimized assignment beats 1000 random chapter-to-folio shuffles. Mean ratio 1.284 vs null 0.572, confident 9 vs null 0.32. Random-draw specificity: only 1/100 random 16-chapter draws reach 9 confident. Both chapter identity and assignment specificity confirmed	2	A↔B, cross-family, PL, REGIME, permutation
C1888	8D vs 4D feature comparison: adding 4 discovered dimensions (consistency_frac, suffix_transparency, header_enrichment, thermo_ke) to 4 known channel mappings raises confident from 4 to 9, mean ratio from 1.123 to 1.284. Only 4/15 assignments agree between 4D and 8D. TRAINING-SET result; cross-family validation is C1885	2	A↔B, cross-family, PL, features
C1889	f75r is the only Currier B folio (of 82) with a 4+ consecutive identical token run (qokedy x4, line 13). Only 7 folios have runs of 3+; 75/82 have max run ≤2. Pure corpus fact independent of matching features	2	B, token, repetition, corpus
C1890	ot-PREFIX fraction significantly higher on R3 folios (mean 0.306) than R1 folios (mean 0.196). Mann-Whitney U=171, p=0.005. Confirms C1478 prediction (k/t terminal mirrors): k-HEAD-dominant regime (R1) shows qo-PREFIX dominance, t-HEAD-involved regime (R3) shows ot-PREFIX elevation	2	B, PREFIX, REGIME, C1478, C1300
C1891	f76r P1 has the strongest monotonic monitoring gradient in Currier B. Not part of 8D matching features (which use folio-level HEAD ratios, not within-paragraph positional gradients). Small comparison set	2	B, PREFIX, monitoring, gradient
C1892	f76r P1 monitoring gradient loads more on ch (rho_ch=0.341) than sh (rho_sh=0.221). Consistent with Ch18's active testing procedure (C929: ch=active test). Difference not formally tested for significance at this sample size	2	B, PREFIX, monitoring, C929
C1893	f75r and f76r show PREFIX balance shift within same section/REGIME/quire: f75r qo-enriched (26.2% vs f76r 19.1%), f76r ch-enriched (17.0% vs f75r 10.2%). Both folios in section B, REGIME_1, quire M — section effects controlled. Consistent with C929/C1313 k/e channel architecture. 8D matching features use HEAD ratios not PREFIX fractions (not circular)	2	B, PREFIX, k-channel, e-channel, C929, C1313
C1894	f75r has the only consecutive double-dar sequences in Currier B (lines 35, 36). 188 total dar tokens across 65 folios, but consecutive doubles unique to f75r	2	B, token, repetition, corpus
C1895	Blind prediction test: formalized predictions (tertile thresholds) scored against all 82 B folios. Null rate 42.3%, matched rate 61.3%, lift 1.45x. Ch24->f84v significant. Ch9->f83r and Ch16->f108r suggestive. Ch27->f77v and Ch18t->f81v worse than random (p>0.84). Aggregate lift is modest; individual chapter results vary widely	3	B, matching, PL, methodology
C1896	C1884 upgraded from Tier 4 to Tier 3 for Ch19->f75r and Ch18->f76r based on structural convergence (C1891-C1894 + C1889). Supporting evidence has caveats: C1891 small n, C1892 untested difference. Ch12->f113v remains Tier 4	3	B, matching, PL, content, upgrade
C1897	Suffix -edy suppresses e-depth in compound MIDDLEs: parses kee+dy as ke+edy, hiding gentle-heat (e-depth=2) signatures. Morphology.atomize() bypasses MIDDLE/SUFFIX boundary, reading post-prefix chars as flat HEAD+MOD*+TERM atom sequence (C1394). 100% coverage on 23,096 B tokens	2	B, GLOBAL, morphology, parser, C1225, C1394
C1898	HT articulators exhibit two-group positional split (refines C1417): OPENER (p,t,f,d) 66.7% line-initial, EMBEDDED (l,r) 4.3% line-initial. Chi-squared=171.4. 92% folio consistency (23/25). y-articulator splits by prefix: sh/ch-prefixed 77-87% initial, te/ta-prefixed 15-24%	2	HT, B, articulator, position, C1417
C1899	f75r atom decode confirms Ch19 alignment with corrected e-depth (extends C1896): 8/8 structural predictions confirmed, e-depth trajectory in P9 shows kee/ke gentle/steady alternation, L41 100% gentle heat preceding material addition and quality check	3	B, f75r, PL, Ch19, C1896, C1225
C1900	Fermentation structural fingerprint falsified: criteria (sh>20%, ch<10%, qo<15%, e>25%, k<15%) match 1/555 paragraphs. Text encodes operational behavior shifts, not process labels. Confirms C171	1	B, paragraph, fermentation, C171
C1901	Dark MIDDLEs select into PREFIX channels in B, diverging from host folio baselines (cosine 0.53-0.59). Categorical exclusions persist cross-folio: eet 0% qo across 16 folios, ksh 0% sh/ch across 18. Per-MIDDLE channel selection, extends C1138	2	B, dark pipeline, PREFIX, C1138, C1356
C1902	Dark MIDDLEs are PREFIX-affiliated in A registry (V=0.449). Same domain locking as B-side (C1901). Extends C1138 cross-system	2	A, dark pipeline, PREFIX, C1138
C1903	78% of dark MIDDLEs (234/300) spawn RI instance derivatives in A, at 0.83x bridge rate. Dark pipeline is major RI derivational substrate. Three-level chain: bridge atoms -> dark compounds -> RI instances. Extends C913	2	A, dark pipeline, RI, C913, C1141
C1904	Dark and bridge MIDDLEs positionally identical in A lines (cosine 0.977). A does not distinguish pipeline membership at line level. Consistent with C234	2	A, dark pipeline, bridge, position, C234
C1905	Dark MIDDLEs LESS PREFIX-concentrated than bridge at matched frequency. Dark spreads across more channels — identification vocabulary in multiple operational contexts vs channel-specific bridge operations	2	B, dark pipeline, bridge, PREFIX
C1906	Dark atom compositions match section grammar HEAD profiles: r=0.378 (C) to 0.924 (B). Section hyper-modulation (C1148) operates through atom-level selection matching operational character. Extends C1148	2	B, GLOBAL, dark pipeline, section, C1148
C1907	Dark PREFIX domain locking is HEAD-stratified: k-initial channels 65-100% to qo (thermal), e-initial shows moderate spread (mean cos 0.629), headless routes through specification PREFIXes. HEAD determines channeling behavior	2	B, dark pipeline, HEAD, PREFIX, C1475
C1908	Zodiac folio i/d MOD atom swap: MOD distribution differs significantly across seasonal folio groups. i-tokens (`aiin` family: a-HEAD, ii-MOD, n-TERM) enriched in Summer/Winter; d-tokens (`-ody` family: e/o-HEAD, od-MOD, y-TERM) enriched in Spring/Autumn. Two structurally distinct, nearly mutually exclusive token populations (3-7% co-occurrence). HEAD also significant; TERM not. e_depth gradient: Autumn 0.813 > Winter 0.515	2	AZC, zodiac, MOD, atom, seasonal, C321, C1519, C1681, C1394
C1909	aiin absolute line-initial exclusion: 0/469 across A, B, and AZC. bare aiin NEVER appears at line position 1. daiin line-initial enrichment is B-specific and absent in A (11.3%, ns). The exclusion is construction-layer; the enrichment is execution-layer	2	GLOBAL, aiin, position, C557, C1234
C1910	ii-extension n-terminal lock is cross-system: A=93.7%, B=94.7%, AZC=83.3%. Chi-squared A vs B p=0.197 (fail to reject). Safety mechanism morphologically encoded at construction layer — does not require B execution grammar. Non-aiin ii-tokens have 0% n-terminal, confirming clean binary split	2	GLOBAL, safety, ii, terminal, C1482, C1484
C1911	ii-token HEAD anatomy diverges across systems: a-HEAD rate A=19.2%, B=35.9%, AZC=36.0%. A's ii-tokens are 57% headless. A-specific null hypothesis (ii HEAD = non-ii HEAD) rejected at p=1.3e-143. Safety encoding is morphological (construction-layer) but HEAD selection is execution-layer	2	A, B, AZC, safety, ii, HEAD, C1480, C1507
C1912	ii/ee complementary domain split confirmed cross-system: a-HEAD tokens preferentially use ii (not ee), e-HEAD tokens preferentially use ee (not ii), in all three systems. Two-strategy safety architecture (C1732-C1733) is construction-layer	2	GLOBAL, safety, ii, ee, HEAD, C1732, C1733
C1913	C1908 seasonal i/d swap driven specifically by aiin-family: Summer+Winter aiin rate 0.120 vs Spring+Autumn 0.072. ody-family shows exact inverse. 65-74% of all seasonal i-tokens are aiin-family. Decomposes C1908 to token-family level	2	AZC, zodiac, aiin, seasonal, C1908
C1914	daiin rate anti-correlates with folio thermal complexity: folio-level rho=-0.324, p=0.0004. Herbal line-level rho=-0.089, p=0.0018. daiin is infrastructure accompanying simpler (lower e_depth) content. Cluster 3 (Stripped-down Herbal, e_depth 0.133) has highest daiin rate	2	A, aiin, daiin, thermal, e_depth
C1915	AZC daiin-aiin co-occurrence attraction: OR=5.04, Fisher p=0.003. In AZC only, daiin and aiin co-occur on same line 3.3x more than expected. A and B show independence (OR~1.0, ns). AZC uses both tokens in complementary diagram-entry roles	2	AZC, aiin, daiin, co-occurrence
C1916	aiin-family internal composition is section-conditioned: headed/headless ratio differs by section in A and B. Herbal/Pharma A-side majority headless (daiin-driven); Text A-side majority headed. B Cosmo/Stars headed-dominant; Bio most headless	2	GLOBAL, aiin, section, HEAD, C1507
C1917	67% genuine atom freedom: within-section atom variance is 2.5x larger than C1169's 27% AXM residual. AXM captures <2% of atom variance (mean R²=0.083). Atoms measure compositional dimensions almost entirely orthogonal to AXM's dynamical property. Verdict: ATOMS_ORTHOGONAL_TO_AXM	2	B, design freedom, atom, C1169
C1918	Atom-level effective dimensionality: 11 PCs at 80% variance, 18 at 95% (from 30 section-residualized features). PC1 (23.8%) = yield vs cooling emphasis (head_a vs e_depth/head_e). Dimensionality ratio 0.60 matches C1715's 0.55, confirming atom features don't dramatically compress	2	B, design freedom, PCA, C1715
C1919	4 pure FREEDOM atom features (section eta² < 0.10, REGIME-orthogonal within Herbal): mod_c (adjust, eta²=0.015), term_h (transparent, eta²=0.068), mod_d (mark, eta²=0.079), mod_s (sequence, eta²=0.033). Freedom concentrates in C1207's monitoring cluster ({c,h})	2	B, design freedom, MOD, TERM, C1207, C1154
C1920	REGIME is atom-decomposable but narrow: RF LOO-CV accuracy 85.4% (chance 25%). Top 2 features (head_k importance=0.245, pfx_qo=0.103) capture most REGIME signal. Within-Herbal: only head_k (eta²=0.887) and pfx_qo (eta²=0.640) are REGIME-constrained; all other features eta² < 0.15	2	B, REGIME, atom, HEAD, PREFIX
C1921	Freedom channels consistent across sections: Bio-Herbal, Bio-Stars, Herbal-Stars feature rankings correlate. The same atom dimensions differentiate folios regardless of section. Not an artifact of any single section	2	B, design freedom, section, cross-section
C1922	PREFIX and MOD layers drive folio differentiation: ~60% of pairwise JSD between folios comes from PREFIX (~30-34%) and MOD (~26-30%) distributions. HEAD and TERM contribute less. Within-section, these layers carry the operational tuning that makes each program unique	2	B, design freedom, PREFIX, MOD, JSD
C1923	Atom features predict operational profiles strongly: head_e↔e_ratio rho=+0.816, term_n↔checkpoint_rate rho=+0.809, e_depth↔e_ratio rho=+0.749. Atom-level composition directly maps to known operational metrics	2	B, atom, operational, e_ratio, checkpoint
C1924	Freedom concentrates in monitoring/closure atom clusters: of C1207's 5 clusters, {c,h} monitoring contains 2 of 4 FREEDOM features, {d,y} closure contains 1. Energy ({k,l}) and iteration ({a,i,n,r}) clusters have zero FREEDOM features — they are section/REGIME-constrained	2	B, design freedom, C1207, monitoring, closure
C1925	dar encodes new material introduction: dar present on all 4 folios matched to recipes introducing new/distinct materials (f75r=10, f84r=13, f76r=7, f82r=1), absent on all 2 folios matched to cohobation/separation-only recipes (f112r=0, f108r=0). 6/6 partition. dal is the passive counterpart (output/transfer). f75r double-dar maps to Ch19's two-ingredient addition (honey+wax)	2	B, cross-folio, PL, dar, dal, C1894
C1926	chekar (ch+ek+ar) appears in post-thermal vessel-monitoring context across 7/83 B folios: on chekar lines qo depleted 0.48x, ok enriched 1.60x, daiin enriched 3.7x, okal enriched 3.8x. 3/3 confirmed balneum folios have chekar. 4 predicted folios (f33r, f34r, f94r, f95r1) show chekar in balneum-compatible local context but NOT balneum-dominated folio profiles (Section H folios with balneum as one step). f76r absence = correct negative (silver-plate test, not balneum)	2	B, cross-folio, chekar, ek-MIDDLE, C929
C1927	f75-f84 maps to Liber Mercuriorum at section level: 8/11 folios match Mercuriorum chapters (3 confirmed, 3 supported, 2 not confident), 3 match Practica (base preparations). Folio-chapter ordering does NOT follow book order (r=-0.179) — manuscript may follow procedural/product-chain order	2	B, section, PL, Mercuriorum, C1882
C1928	Mercuriorum Ch18-Ch29 encodes parallel mineral + animal production chains: mineral chain (Ch15-19, mercury→gold→quintessence) produces active medicine; animal chain (Ch20-25, systematic capon disassembly into 5 waters) produces carrier vehicles; both converge at Ch26 (humoral medical administration). f75r quintessence is explicit input to f84r gold tincture (Ch14 requires "vegetable G" = quintessence)	3	B, PL, Mercuriorum, product chain, C1882, C1927
C1929	f82r exhibits recipe-predicted sealing micro-paragraph: P3 (5 tokens, L18) at material→maceration boundary contains 2x okain (vessel-intake). Ch22 says "close the cucurbit with glass cover and wax." Supporting: dar=1 (single new material=lunaria), P4 has 12 consecutive qo lines (3-day sustained heat), gentle=22.9%, sh=11.3% elevated. Match NOT confident by 8D criteria (ratio=0.791, CV=48.2%) but atom-level evidence exceeds several confident matches	2	B, f82r, PL, Ch22, C1882, C1925
C1930	Mercuriorum splits across two manuscript sections: Ch1-28 → Section B (f75-f84, 14 folios, preparation), Ch40+ → Section S (f103-f116, 6 folios, transmutation/multiplication). Split is functional. Folio-chapter ordering does not follow book order within either section	2	B, S, PL, Mercuriorum, C1927
C1931	B-grammar recipe content in Section T ring format: f66r (language=B, 349 tokens, 0 A/AZC) matches Ch24 Practica fixation with da=10.0% (rank 5/82), 82% dry heat, 62 folio-unique words. Ring physical format, B operational grammar. Contrasts C1127 (rosettes = AZC-like)	2	B, T, f66r, ring, C1127
C1932	Full-spectrum scan: Theorica (96 ch) and Furnis (30 ch) produce zero atom-validated matches. "Confident" theoretical matches collapse onto universal attractor folios (f84v=24ch, f34v=17ch) or are metaphorical keyword false positives. Manuscript encodes procedural Practica + Mercuriorum content only	2	B, PL, Theorica, Furnis, C171
C1933	Expanded matching beyond distillation family generalizes: mean distance +7% (2.358 vs 2.214). 8+ new atom-validated matches including f79r←Ch12M (d=1.02, 3 dar at 3 predicted positions, P7 color endpoint). 8D features capture cross-family operational similarity	2	B, PL, matching, C1882
C1934	d=do/execute replaces d=mark: 7-axis battery scores 12/14 (margin 4). Matches OPERATION category shift (+55.6%), 2.11x B-enriched, non-tautological with y=end. Compounds improve: ed=cool+do=discharge, od=arrange+do=collect, dy=do+end=done. o/c/p/s confirmed at current glosses	2	B, atom, d, C1195, C1394
C1935	Reverse-blind matching produces predictive folio identifications: recipe-derived predictions scan 49 unmatched folios. f103v/Ch27P scored 10/11 in scan, confirmed 6/7 at atom level. First predictive (not confirmatory) recipe-folio match	2	B, PL, matching, C1882
C1936	Recto/verso pairs encode sequential operations on same leaf: f66r/v (fixation→inceration), f103r/v (multiplication→imbibition), f108r/v (separation→dissolution). Procedural sequence preserved across page turn	2	B, manuscript organization, C1927
C1937	Multi-chapter folios combine related short procedures: f80r = Ch21-25M (5 chapters). Ch10P+Ch11P within f108v. Organizing unit is operational scope not chapter count. Explains Phase 628 paragraph-count null result	2	B, manuscript organization, C1927
C1938	Blind atom reading correctly predicts recipe type: f115r (fully blind) predicted fixation from atoms, confirmed by Ch28P. Score 6/8. f112v partial blind 7/8. Prediction accuracy tracks recipe detail level	2	B, atom, blind test, C1394, C1897
C1939	**DEMOTED 2026-05-15 — Tier 4 (was Tier 3): material-identifier claim does not survive strict audit.** Original claim: fch (flag.adjust.watch) encodes mercury/mercury-water, ∞ enrichment on 6/6 mercury-recipe folios, 19/82 corpus. Audit (Phase 684 retest, 2026-05-15) with three strictness levels: at MIDDLE=='fch' exact (6 tokens corpus-wide) enrichment 4.70× p=0.016 — marginal but underpowered. At MIDDLE starts-with 'fch' (broader, 27 tokens / 23 folios) enrichment drops to 1.65× p=0.094 — FAILS. At MIDDLE contains 'fch' (44 folios) enrichment is DEPLETED at 0.57× p=0.77. The "∞ enrichment on 6/6" framing was a sparse-data artifact (zero non-target tokens at strict def). At broader definitions, fch-token concentration tracks botanical-section distribution (f46r 25.5/1k, f41v 29.9/1k) not mercury-recipe distribution. Material-identifier interpretation NOT supported beyond strictness-1 with N=6.	4	B, A, dark pipeline, fch, DEMOTED, AUDIT_FAIL, C1901
C1940	cs (adjust.sequence) concentrates on f84 leaf (gold-recipe matched, Ch.14P/Ch.15P): 17.5× original enrichment, 9/82 corpus. **Audit 2026-05-15 (Phase 684 retest):** at MIDDLE starts-with 'cs' (21 tokens / 16 folios) f84r+f84v rate 8.90/1k vs non-gold baseline 0.68/1k = **13.15× enrichment, within-section shuffle null p=0.004**. Held-out test on f81v (Ch.18M potable gold per C1958, NOT in original derivation): cs-rate 3.91/1k = **5.77× baseline** (passes 3× threshold) but **less than half** training rate (8.90/1k) with only N=1 cs-initial token. **Refined interpretation:** cs-token concentration on f84 leaf is structurally validated (Tier 3); the broader "cs encodes gold" lexicon-gloss is partially supported — held-out attenuation consistent with cs encoding a specific gold-handling operation present on f84 but absent in potable-gold maceration, OR with f84 concentration being structural rather than material-specific.	3	B, dark pipeline, cs, AUDIT_REFINED, C1901, C1958
C1941	**RETRACTED 2026-05-15 — three functional classes do not survive distribution testing.** Original claim: dark pipeline MIDDLEs divide into three functional classes: equipment (lch, lk, eed — 10+ folios), process (cth, eke, ksh — 3-9 folios), material (fch, cs, eckh — enriched on specific recipe types). Audit (Phase 684 retest, 2026-05-15): all 7 named MIDDLEs FAIL their predicted predicate enrichment. Equipment-class lch=1.18-1.24× / lk=0.62-0.95× / eed=0.98× — no enrichment over baseline. Process-class cth=0.71× / eke=0.71-0.82× / ksh=0.85-0.93× — depleted or null. Material-class eckh=0.27-1.08× — no enrichment on either mercury or gold predicates. Only cs survives audit (separate C1940 verdict). Operational-story-first taxonomy: 2 STRONG / 2 MODERATE dimensions from original analysis may have been post-hoc clustering on token-frequency × folio-breadth rather than functional separation. Cross-references `feedback_operational_story_first_trap.md` — same trap pattern as C1993, triple-i, hh, k-e-depth thermal regimes. The frequency stratification observation (10+ folios vs 3-9 vs ≤2) survives as descriptive fact, but the functional-class interpretation does not.	1	B, dark pipeline, RETRACTED, AUDIT_FAIL, post-hoc-classification, C1901, C1906
C1942	f58r/f58v (Section T, Currier A) are master catalog folios: contain A-system records for 6/9 tested dark pipeline identifiers (fch, lch, lk, cth, eet, tsh). No other A folio shows this catalog concentration	3	A, T, dark pipeline, C1499, C1903
C1943	Ch40M (silver transmutation) matches f106v: 8D distance 0.933 (confident, ratio 1.164). 449 tokens, 20 Latin verbs. fch×2 bracket main operations. e_depth clusters match two bath phases. Token/verb ratio 22.5	3	B, S, PL, Ch40M, f106v, fch
C1944	Ch47M (coded elemental separation) matches f113r: 8D distance 1.245 (ratio 1.992, highest confidence). 518 tokens, 23 verbs. fch×4 tracking 4 element extractions. cs at L43 endpoint matches gold projection discussion. Heavy lk (furnace)	3	B, S, PL, Ch47M, f113r, fch, cs
C1945	Ch50M (error correction) matches f111r: 8D weak (3.755) but atom-level diagnostic. 614 tokens. Near-zero dar (2+2 on 614 tokens, lowest for size). Inverted e_depth (depth1>depth0, unique in corpus). P2=359 tokens (58%). 5×eed (cooling after overheating). 8D fails on structurally atypical recipes	3	B, S, PL, Ch50M, f111r, fch, eed, cth
C1946	Higher Mercuriorum chapters (Ch36-Ch52) contain 6+ procedural chapters previously classified as "theoretical." Latin verb counting reveals Ch40M (~20 verbs), Ch42M (~18), Ch43M (~10), Ch47M (~23), Ch48M (~20), Ch50M (~20), Ch51M (~20), Ch52M (~42). Matching extends from 42 to 45 chapters (3 confirmed + 1 tentative)	2	B, PL, Mercuriorum, C1882, C1932
C1947	Ch15P (alternative gold dissolution) matches f84v: cs×2 at L7,L9 (gold introduced early), dar=4 exactly matching 4 material introductions (vegetable G, rectified water, gold, lunaria juice), dal=1 matching vigorous *proijce* operations, lch×3 matching double alembic. Recto/verso of f84r (Ch14P gold dissolution, C1936). Fourth confirmed recto/verso pair	3	B, PL, Ch15P, f84v, cs, C1936
C1948	Ch25P (fixation of air) matches f115v: dar=0, dal=0 (zero material addition — fixation cycles existing material). eed×7 (extended cooling, one per sublimation cycle). lk=31 prefix (graduated fire over 3 days). lch×4 (sublimatory apparatus). cth (fixation monitoring). Recto/verso of f115r (Ch21P+28P red sulfur). Fifth confirmed recto/verso pair	3	S, PL, Ch25P, f115v, eed, C1936
C1949	A-system RI-embedded dark breadth distinguishes catalog from specification folios. f58r breadth=11/16, herbal mean=1.1. Section T embed 2.7x Section H. Raw dark density negligible (coverage optimization suppresses PP-level signal per C755)	2	A, dark pipeline, RI, C1903, C1942, C755
C1950	**DEPENDS ON RETRACTED C1941; AUDIT NEEDED.** Original claim: herbal A folio dark tokens are PROCESS-class (cth, ro, eke), not material or equipment class per C1941 taxonomy. C1941 retracted 2026-05-15 after all 7 named MIDDLEs failed enrichment audit — the three-class differentiation does not survive distribution testing. The structural observation that 5 outlier A herbal folios have elevated cth/ro/eke density may survive as descriptive fact, but the functional-class interpretation is gone. Re-audit needed before treating as Tier 2.	2	A, H, dark pipeline, DEPENDS_RETRACTED, C1941
C1951	**DEPENDS ON DEMOTED C1939 + REFINED C1940.** Original claim: dark pipeline serves as text-based channel substitute for illustrations: plant illustrations carry material identity visually; dark MIDDLEs (fch, cs) carry material identity textually where illustrations cannot depict the material. 2026-05-15 audit: C1939 demoted to Tier 4; C1940 refined (cs concentration on f84 leaf validated structurally, broader gold-encoding interpretation partially supported with held-out attenuation). The "text-as-channel-substitute" interpretation rests on fch+cs jointly carrying material identity — fch component now weakened.	3	A, B, dark pipeline, illustration, DEPENDS_REFINED, C1939, C1940, C1942
C1952	Ch48M (ferment preparation) matches f113v: UPGRADED from tentative. ro (fermentation marker) at L10. fch at L33 (67%) matches mercury at step 11/14. ot=70 dominant (4 powder types). dar=2, daiin=4 (reiteration/multiplication). e_depth=4 tokens (rare, extreme refinement). Token/verb ratio 24.0	3	S, PL, Ch48M, f113v, fch, ro
C1953	Ch23P (sulfur multiplication testing) matches f114r: eed×8 (cooling per test cycle, highest of all candidates), daiin=11 (iterative testing, highest), zero material markers (testing existing stone), 12 paragraphs for ~12 steps, e_depth=4 (rare extreme refinement), cth (state-transition monitoring). Recto of f114v/Ch31P	3	S, PL, Ch23P, f114r, eed, C1936
C1954	Ch31P (medicine multiplication in quantity) matches f114v: dar=2, daiin=6 (iterative projections), cth×3 (congelation monitoring), eed×3. Recto/verso of f114r/Ch23P (testing→production). Sixth confirmed recto/verso pair. Non-procedural promotional content (~50% of Latin chapter) not encoded	3	S, PL, Ch31P, f114v, cth, C1936
C1955	Ch17M (first mercury purification water) matches f106r (TENTATIVE): ro×2 matching fermentation step, lch (cucurbit+alembic), eed×2, ir (iteration). Recto/verso of f106v/Ch40M (preparation→application). Token/verb ratio low (16.8)	3	S, PL, Ch17M, f106r, ro, C1936
C1956	10-dimension permutation test: 0/10,000 shuffles beat real 41-assignment set across all dimensions. ~5-6 effectively independent dimensions. Strongest: eed→cooling, Merc-prep→Section-B, Higher-Merc→Section-S, ro→fermentation. Post-hoc dimension selection acknowledged. Extends C1887 from 16 to 41 assignments across families	2	B, PL, matching, permutation, C1887, C1936, C1939
C1957	Suffix boundary revision: blocked e-initial and h-initial suffixes from extract() parser. e=cool is a MOD atom encoding e_depth (C1225); h=watch is a MIDDLE terminal (C1487). Both steal operational atoms from MIDDLE when parsed as suffix-initial. Fix: e_depth match MIDDLE-vs-atoms rises from 16.7% to 98.6%; max folio distortion drops from 14pp to 0.000. Suffix set reduced to d/a/i/o-initial + single TERM atoms. Zero empty-MIDDLE regression	2	B, morphology, SUFFIX, atom, C1225, C1487, C1511
C1958	ot PREFIX = transfer rate / drip rate monitoring (upgraded from "operational verification"). ok/ot ratio correlates with recipe emphasis: f83r (Ch9P drip-counting recipe) has lowest ok/ot=0.38; f81v (Ch18M potable gold/maceration) has highest ok/ot=5.50. On f83r L22, ot×3 clusters exactly where Catalan text specifies drop counting at 6/10/15/20. Three ot MIDDLEs encode check(otchedy), iterate(otaiin), done(otedy) — control actions around drip monitoring, not numerical values. Control loop: sh→qo→ok→ot→sh = watch→heat→vessel temp→drip rate→watch	2	B, PREFIX, ot, ok, C929, C1313, C1316
C1959	Paragraph layout-order on confirmed-match folios corresponds to recipe-phase order in matched chapter. Mean Spearman rho=+0.812 across 5 matches; f84r p=0.0005, f86v3 p=0.025; effect size 3.2x random-phase noise floor (0.245). Compatible with C1399/C1400 state-coupling-independence at corpus-aggregate scope; falsifies the strong-form interpretive reading "paragraphs are genuinely parallel subroutines, not sequential steps" when applied to individual matched folios. Resolves three-claim distinction: (1) state-coupling absent, (2) operational interchangeability untested, (3) semantic layout-ordering empirically supported on matches. C1399/C1400 phrasings revised to scope-restrict to corpus-aggregate measurements. **Updated 2026-04-25 (Phase 644):** evidence base extended to 7 confirmed matches with f108v + f79v added; aggregate mean rho +0.848, 4/7 at strict significance.	3	B, paragraph, ordering, recipe-correspondence, C1399, C1400, C845, C1287, C858, C1888
C1960	Per-paragraph heat metrics derived from atom decomposition correlate with predicted recipe fire-degree on heat-phase-distinct matched folios. Best metric qokeedy_frac: mean rho=+0.710 across 5 phase-distinct folios (f84r, f82r, f78r, f86v3, f77r), 5/5 positive direction. Heat-uniform control (f75r, f108v, f79v): mean rho=+0.066. Difference +0.643. Effect is SCOPE-RESTRICTED — encoding holds where recipes have distinct heat-phase changes; absent where recipes are heat-uniform throughout. Second syntactic rule complementing C1959.	3	B, paragraph, heat-mode, recipe-correspondence, layout, scope-restricted, C1959, C1225, C1226, C1957
C1961	Fire-side / vessel-side paragraph-level PREFIX partition. Fire-side {qo, ch, sh} anti-correlates with vessel-side {ok, ot, ol, or}: mean cross-block r=−0.232, within-block r=+0.080. Folio-level differential +0.295. **Paragraph-level differential +0.131** — survives at PREFIX-load-bearing scale per C1811-C1812. Survives 3/4 sections and 3/4 regimes. REGIME_2 (iteration-dominated, low-link) fails directionally — documented scope exception, possibly LINK-as-separator mechanism (Tier 3 candidate). The bridge: qo↔ol = +0.29 (heat application correlates with vessel-state change). Compatible with token-scope C1217/C1242/C1306 lane architecture at orthogonal scale.	2	B, PREFIX, paragraph, partition, fire-vessel, architecture, C1811, C1812, C1217, C1242, C1306
C1962	4-axis o-prefix runtime channel taxonomy. ol = vessel-content state monitoring (which vessel holds what, batch identity, vessel role). ot = material transfer / addition / iteration cycles (broadens C1958 drip-rate). ok = thermal regime / fire-degree state on contents. or = outcome / completion state (per C539 LATE class; weakest gloss, no matched recipes). All four positionally uniform within paragraphs (early/base 0.75–1.13×). Within-sample top-1 fit 16/16 (100%) on matched recipes; top-2 strict 7/16 (43.8% vs 17% random). Refines C1388 (ol gloss sharpened, preserving C1174 deflation) and C1958 (ot generalized; drip-rate is f83r-specific manifestation). Out-of-sample validation pending.	3	B, PREFIX, o-prefix, taxonomy, channels, recipe-correspondence, C1388, C1958, C1316, C539
C1963	qo as paragraph operational opener. When qo and any o-prefix appear in same paragraph, qo precedes the o-prefix in 77.9% of cases on average. qo→ok 72.9%, qo→ot 73.6%, qo→ol 80.5%, qo→or 84.7%. Sister pairs ok↔ot, ol↔ot symmetric ~50/50 (confirms C1304). ch/sh asymmetric: sh→ch 61.2% (passive monitor before active test, refines C929). qo precedes da in 80% (heat-setup before material-introduction). Mechanism: grammatical precedence of operational opener per C1300/C1316/C1394, NOT pair-specific. Thermal-mass alternative tested (T5/T6/T7), directional but not significant; not registered.	2	B, PREFIX, paragraph, ordering, qo, generic-precedence, C1300, C1316, C1394, C929, C1304
C1964	o-Prefix within-line interleaving dominance. The 4-axis o-prefix architecture (C1962) is token-scoped at prefix level, NOT line-scoped. Mean prefix run length 1.27, median 1, 80.8% singletons, max 10. 85.3% of prefix transitions occur within-line, not at line breaks. Falsifies "channels persist within lines" intuition. Block-level (fire/vessel) coherence: mean run 2.39, max 50, 50.3% singletons, 11.7% reach length 5. Paragraph-level: 46% >70% block-pure (independent confirmation of C1961), 13% >85%, 1% 100% block-pure. Tokens are atomic instruction primitives (per C1394) interleaving rapidly; paragraphs are block-specialized units (per C1961). Line is not an architectural unit for this dimension.	2	B, PREFIX, line, paragraph, persistence, interleaving, run-length, C1962, C1228, C1722, C1394, C1961
C1965	f75r cycle-counting + per-cycle annotation idiom. The recipe's two-phase reflux specification (×4 then ×9 vegades, III.19) is encoded as line-localized closed-cycle clusters. Closed cycles = tokens matching qok+...+dy (qok prefix + -dy closure suffix; transitional sub-states like qokey are excluded). ×4 phase: 4 closed cycles on L13 single line (4-qokedy identical run, corpus rarity ~7). ×9 phase: 10 closed cycles in L36-L38 3-line window (1 initial + 9 redistillations) — **CORPUS-SINGULAR** (only such window in all of Currier B). Cycles 4-5 (qokchdy, qokechdy) carry ch MOD atoms at the recipe's phase boundary, marking active-test cycles per C929 generalized to per-cycle annotation. Idiom does NOT generalize to small-count recipes (f82v ×4: corpus rarity 30+; f112r ×3: no clean window match) — small counts are structurally indistinguishable from corpus noise at line-window resolution. Refinement of C1394: MOD-atom class includes both continuous-extensible (e for thermal degree per F-B-007/C1735) and discrete-event (ch for tests per C929) subtypes; should not be conflated.	3	B, f75r, qok-cycles, recipe-correspondence, atom-annotation, C929, C1394, C1735, C1300, C1958, C1316
C1966	HT density per Currier B folio correlates with distinct compound MIDDLE count after controlling for type-token confound. Original bivariate rho=+0.602 was ~70% inflated by type-token coupling. Partial Spearman controlling for total HT token count: rho=+0.189, p=0.045. Signal survives but is weak. HT rate tracks compound diversity independently of total HT token sampling, but the effect is small. Attention-scaffolding hypothesis remains REJECTED (sh_rate opposite direction). Original C1966 (v6.36) did not control for the species-area relationship between token count and type count. Phase 667 retest adds partial correlation.	2	B, HT, compound, specification, per-folio, density, C935, C740, HTSC
C1967	e_depth paragraph-channel gradient survives compositional control. Among block-pure Currier B paragraphs, mean e_depth on NON-PREFIX tokens (removing qo/ch/sh/ok/ot/ol/or tokens to eliminate compositional confound) orders monotonically: qo-dominant = 0.471 > ch-dominant = 0.446 > sh-dominant = 0.357. Gradient (qo-sh) = +0.114, permutation p=0.024. Monotonicity p=0.20 (gradient significant, strict monotonic ordering marginal). All-token gradient also confirmed: qo 0.670 > ch 0.609 > sh 0.536, p=0.005. Original C1967 (v6.36) lacked statistical test and did not control for compositional confound (qo tokens inherently carry higher e_depth). Phase 667 retest adds both. Cross-validates F-B-007 at paragraph aggregation.	2	B, paragraph, e_depth, channel-class, thermal-intensity, F-B-007, C1300, C929, C1961, C1225
C1968	ch-class paragraph-header compound-specification concentration. Block-pure Currier B paragraphs with ch-dominant channel show shared-token-controlled HT-rate gap of +0.066. Other channel classes (qo, sh) do NOT show genuine concentration after token-pool control: qo collapses; sh actually reverses (-0.041). Refines C929 (ch=active test) with operational claim: active-testing operations require explicit compound-specification at the paragraph header before test execution in the body. Pairs with C1967 supplement (sh-class largest e_depth body-concentration) to establish channel-class-distinctive header-body specialization. The architecture is NOT universal "headers=spec, bodies=execution" — it's channel-class-specific with each class concentrating different content (ch: compound-spec at header; sh: thermal-commitment at body; qo: consistent throughout). Token-pool control addresses C1789 86% header-vocabulary-exclusivity caveat.	2	B, paragraph, header-body, ch, compound-specification, channel-class, C929, C935, C966, C1789, C1967
C1969	Window-density specificity test confirms the Phase 636 f75r ×9 anchor under a third independent methodology after Phase 657 (prefix-class contiguous, NULL) and Phase 658 (lexeme contiguous, INCONCLUSIVE). ≥9 qok-class tokens within any 2-consecutive-line window appears on 3/82 = 3.7% of Currier B folios (f75r L37-L38, f86v3 L1-L2, f108r L48-L49). Of those three high-density folios, only f75r matches a Catalan chapter (III.19.0) carrying explicit `×9 vegades`. Matched-pair specificity test: 4/4 anchors land on matched folios, p=0.0208 under 10,000-permutation null with within-recipe pairing preserved. Corpus ceiling at 9 (no folio reaches ≥10). f86v3 (matched II.10.0 conjunction of liquefactions) and f108r (matched III.16.0 ferment multiplication) both reach the threshold without numerical `vegades` in their Catalan, separating density-as-cycle-count (falsified) from density-as-procedure-type-signature (consistent with).	2	B, cross-folio, qok, window-density, recipe-correspondence, x9-anchor, C1925, C1928, C1959, C1965
C1970	Token-internal ke pattern density tracks dampened/indirect thermal regime on CONFIRMED-tier matched folios. The 3 CONFIRMED matches (f75r/III.19 aqua vitae `en bany`, f76r/II.18 element separation in controlled bath, f84r/II.14 gold dissolution `met al bany`) show paragraph-level ke/ek mean = 9.74 vs supported-tier mean = 5.03, Cohen's d=+1.04, p=0.0023. Corpus-wide sanity check: CONFIRMED 9.74 vs corpus baseline 4.68, d=+0.97, p=0.0057. Leave-one-folio-out safeguard: all three LOO splits maintain d≥0.8 (min d=+0.92). `ke` decomposes as k(HEAD heat)+e(MOD intensity-dampener) per C1394/C1225 atom system, so high ke density indicates dampened/indirect thermal regime. Refines C1226 (ke/ek = process-context conditioning) with external Catalan recipe-content alignment. Phrasing scoped to "indirect/dampened thermal regime" not "balneum specifically" — 3-folio sample cannot distinguish balneum from cognate gentle-heat operations. Tier 3 due to interpretive routing through Catalan content; statistical evidence Tier 2 caliber. HARKing-borderline (motivated by Phase 663 sensitivity check) disclosed and bounded by T2 corpus-wide control + LOO safeguard per expert consensus.	3	B, paragraph, ke/ek, balneum-mariae, indirect-heat, recipe-correspondence, match-tier, C1225, C1226, C1735, C1872, C1899
C1971	Cold read coherence: 15/15 matched folios produce coherent or plausible paragraph-level readings against Pseudo-Lull Testamentum recipes (12 coherent, 3 plausible, 0 incoherent). All 3 CONFIRMED-tier matches coherent; all 4 strong-supported coherent; 5/8 supported coherent, 3 plausible (specification/philosophical chapters). Atom glosses (C1394/C1195) produce control-grammar readings that align with recipe operations without post-hoc adjustment.	2	B, recipe-correspondence, cold-read, paragraph, atom
C1972	e-depth quantitative thermal encoding across 15 matched folios. e-depth tracks physical chemistry thermal requirements at paragraph resolution. Range 0.09 (final coagulation fire, f107r P18) to 1.50 (cold collection, f79r P9 / f107r P7). Balneum mariae paragraphs cluster 0.55-0.67; distillation/condensation 0.92-1.20; strongest fire 0.09-0.34. Cross-validates C1967 non-prefix gradient against external recipe content.	2	B, atom, e-depth, thermal, recipe-correspondence, C1967, C1735, C1225
C1973	Observation MIDDLE density tracks recipe monitoring requirement across 15 matched folios. ckh/cth/ecth/ckhh/cthh density correlates with recipe type: fusibility test (f116r ~23) and calcination (f80r 23) produce dense observation; patience/coagulation (f82r 3, f107r 2) produce near-zero. Active intervention paragraphs carry observation MIDDLEs; autonomous processing paragraphs lose them (fade-out confirmed on f79r, f103r, f82r, f76v, f80r). ecth (cooled-transfer-watch) concentrates on calcination/transfer recipes (f80r: 11 tokens).	2	B, MIDDLE, observation, recipe-correspondence, paragraph, C929
C1974	Paragraph count tracks recipe step complexity across 15 matched folios. Range 2 (two-phase potable gold, f81v) to 18 (highly iterative coagulation, f107r). Simple single-operation recipes → 2-4 paragraphs; multi-step distillation/sublimation → 8-12; highly iterative → 14-18. Extends C1399/C1400 paragraph model.	2	B, paragraph, recipe-correspondence, C1399, C1400
C1975	dar distribution tracks recipe material-addition pattern across 15 matched folios. Five patterns: front-loaded (preparation then processing, f103r 81% in P1-P5), back-loaded (material renewal during reiteration, f75r P9 46%), zero-after-midpoint (cohobation recycling, f112r P6-P14 zero dar), extreme-density (specification/dissolution, f77v P2 17.2%, f81v P1 16.5%), uniform-low (existing material, f107r 2.0%).	2	B, PREFIX, dar, recipe-correspondence, paragraph
C1976	Polyalphabetic cipher hypothesis REJECTED. Soft atoms (d,o,c,p,s,f,r) tested for meaning shift across prefix classes via bigram cosine similarity. Core atoms stable: d=0.994, o=0.924, r=0.939. Lower c=0.640, p=0.660, f=0.609 explained by positional artifact (PSEUDO_HEAD under ch vs MOD under qo), not semantic shift. One cipher system; atoms have stable meaning across all prefix channels.	1	B, atom, cipher, falsification, C1394
C1977	Recto/verso thermal pairing: same-leaf folios have correlated e-depth	2	n=35 pairs, mean diff=0.124 vs 0.213 random
C1979	PREFIX-conditional terminal-atom positional gradient (da family). Same-prefix tokens sort to systematically different line positions by terminal atom: -ir/-iin/-in early, -l late, -m strict line-final. Within-line and folio-level permutation tests both p<0.01 for 5 of 6 tokens. Length and dam-adjacency confounds excluded. Cross-references C1486 (universal -m line-final).	2	B, PREFIX, terminal, atom, da, position, gradient, C1486, C1394, C1925
C1980	dar bimodal line-position distribution (observation). Despite mean=0.507, dar distribution is bimodal — concentrating at line edges (deciles 13.3,6.4,11.7,8.0,6.9,8.5,8.0,11.7,12.2,13.3), avoiding middle. Bimodality coefficient 0.581 (threshold 0.555). Mechanism (clause-edge marker, mixed populations, deployment artifact) not adjudicated.	3	B, PREFIX, dar, distribution, bimodal, observation, C1925, C1979
C1981	Clause-structure hypothesis for dar bimodality REJECTED. Pre-registered test: J1 length-conditional peak tracking shows peaks are position-absolute (decile 0 + line-end), NOT scaling with line length to mark interior boundaries. J2 conditional MI(dar_pos; nearest_headless_offset \| length_bin) = 0.0000 bits, p=1.0000. dar bimodality = line-edge concentration only, not interior clause-boundary marking. C1980 observation stable but mechanism falsified.	1	B, dar, bimodality, falsification, clause-structure, C1980, C964
C1982	a-HEAD r-TERM tokens share bimodal line-position class profile. 4 of 5 a-HEAD r-TERM tokens with n>=30 are bimodal (BC > 0.555): ar (BC=0.600), dar (BC=0.581), otar (BC=0.576), air (BC=0.638). One outlier: okar (BC=0.490). dar bimodality (C1980) is not dar-specific — generalizes to a-HEAD r-TERM frame class. Mechanism unknown (clause structure rejected per C1981).	3	B, atom, frame, a-HEAD, r-TERM, bimodality, observation, C1980, C1394
C1983	sh-prefix and ch-prefix differ in within-line position on fixed e->y frame (Currier B body-only, articulators excluded). sh-e->y start-loaded; ch-e->y flat. Within-line permutation diff=-0.088, p=0.0000. Survives paragraph-line>=3, section stratification (sh start-loaded in H, B, S; ch flat in all 3), articulator exclusion (C1417), LATE-class exclusion (C539). PREFIX carries positional info beyond frame composition, articulator, LATE-class, and line-zone effects (C1426). Direct extension of C1001 (PREFIX dual encoding).	2	B, PREFIX, position, sh, ch, e->y, frame, C1001, C929, C1426, C1457, C1808, C1417, C539
C1984	Folio-level PREFIX-content alignment fails. Across 11 Phase-668-validated Voynich-Pseudo-Lull folio-recipe pairs, PREFIX rates (qo, ch, sh, ok, ot, ol, lk, lch) tested against keyword-density categories (heat, monitor, transfer, iter, vessel, complete) show no surviving correlations after multiple-comparison correction. 2/48 cells passed uncorrected p<0.05 — within chance frequency (~2.4 expected). PREFIX gloss system survives at category level (intra-folio operational classification per C1300, C929, C1962) but fails at folio-density-prediction level (cross-folio rate vs recipe content density).	3	B, PREFIX, recipe-correspondence, alignment, scale, NULL, C1300, C929, C1962, C1971, C1983
C1985	Phase 642 26-folio pharmaceutical cluster maps to Herbal section (19/26 H, 4 C, 2 S, 1 T) with zero overlap with Phase 668 matched-alchemical folios (7 B + 4 S, no H). Naïve cluster-vs-matched comparison shows multiple |d|>2.0 effects on e-channel suppression and morphological palette (HEAD-e d=-2.68, TERM-r d=+2.59, e-depth=0 d=+2.75, qo d=-2.06, kernel-e d=-2.46) but these recapitulate known section-mediated effects (C939, C1404, C1893, C1808) and cannot be distinguished from them given zero matched folios in Herbal section. Limits cluster-property claims pending matched-H folios or within-folio tests.	3	B, cluster, herbal, section, scope-limit, confound, NULL, C939, C1404, C1893, C1808, Phase642
C1986	Manuscript-wide procedural arc via internal e-depth gradient REJECTED. Pre-registered Phase 675 test failed at baseline (|mean_rho|=0.367 < 0.4 threshold). Section-conditional pattern (Herbal -0.48, Cluster -0.29) collapsed under paragraph-1 ablation (Herbal: -0.48 → -0.10; Cluster: -0.29 → -0.04). C1287 (paragraph-header MARKING-enrichment) explains the apparent gradient as paragraph-1 specification-vocabulary artifact. Only Biological-section weak gradient survives — no manuscript-wide procedural-arc signature. C1399 (paragraph independence) survives this test.	1	B, paragraph, layout, e-depth, gradient, falsification, NULL, C1287, C1399, C939, C1985
C1987	Cross-cipher token operational profiles equivalent under section-matched comparison. For 30 frequent tokens (n>=5) appearing in both Part-II-matched and Part-III B-section-matched folios, per-token operational profiles (position, e-depth, terminal/head rates) are statistically equivalent. Mean profile distance Part II vs Part III B-sec = 0.086, smaller than within-Part III random-split null (0.139). REGIME-mismatched control (Part II vs Part III S-sec) = 0.124, slightly higher, consistent with REGIME secondary factor. Foundation of matching catalog (C1971) survives controlled test for first time. Scope: n=2 Part-II folios; cannot generalize to all cipher systems.	3	B, cipher, token, invariance, foundation, recipe-correspondence, C171, C1394, C1976, C1971
C1988	f103r encodes rare-cardinality cluster matching source iteration count. f103r matched to III.16 (ferment multiplication "all four or eight chambers"). Pre-registered N=8 from source. Observed exactly 8 qok-class tokens (qokeedy x3, qokeey x3, qokeodair, qokshy) at L36-L37, in rare 15% folio-relative baseline band. Position aligns with recipe's late chamber-multiplication passage. Joint with f75r ×9 template (C1965): 2/2 rare-N predictions hit exactly, joint chance p=0.006. Adds one novel anchor to C1965/C1969 evidence base. Limitations: single novel case (f75r is template); f82r ×9 miss explainable but post-hoc; N=3 cases corpus-trivial (83% baseline) and uninformative; qualitative cluster-reading inadmissible for tier promotion.	3	B, cardinality, iteration, recipe-correspondence, qok-class, f103r, C1965, C1969, C1925, C1971
C1989	Rosette path/node structural differentiation. Within the f85-86 rosettes foldout (data/rosettes_annotated.json), path tokens between rosettes differ structurally from rosette node tokens. Paths show 9.4x enrichment in da-prefix (16% vs 1.7%) and 4.3x depletion in ok-prefix (4% vs 17.1%). Survives same-folio baseline control (f85+f86 body has 6% da-prefix, intermediate). Recipe-class operational map interpretation FALSIFIED by whitelist-sensitivity test (45/100 random non-matched 11-folio pools reproduce same spatial coherence). Path/node distinction is intentional structural property, not arithmetic artifact. Mechanism not adjudicated; consistent with workshop-apparatus-diagram interpretation.	3	Rosettes, foldout, path-node, da-prefix, ok-prefix, structural, C1124, C1126, C1128
C1990	Recipes-as-transitions in rosette graph REJECTED. Pre-registered Phase 682 test of "recipes are single state transitions in the rosette graph (recipe-as-edge)" with 11 matched-recipe folios. Test 1 (start_node != end_node, >=10/11): FAIL (3/9 testable). Test 2 (path-aligned, >=8/11): FAIL. Test 3 (coherent walk): trivial pass (8/9 starts collapse to EAST). Recipes are NOT single edges in operations graph; they share common preparation/apparatus signature. The "rosettes-as-PFD with recipes-as-paths" interpretation falsified at structural level.	1	B, Rosettes, recipe-correspondence, falsification, NULL, C1124, C1128, C1989
C1991	C1970 underlying balneum text-signature claim NOT supported with corrected methodology. Pre-registered Phase 683 retest of C1970's underlying claim ("CONFIRMED-tier matched folios have elevated indirect/dampened-thermal signature") with corrected metric ke/(ke+ek) proportion and expanded sample. Failed all 4 pre-registered criteria: d=+0.207 (req >=0.35), p=0.257 (req <0.05), LOO min d=+0.163 (req >=0.20), perm p=0.0547 (req <0.05). C1970 retraction final; underlying balneum text-signature claim is not statistically distinguishable from chance even with corrected methodology. Workshop-diagram interpretation cannot lean on body-text balneum signature as anchor.	1	B, paragraph, ke, balneum, falsification, NULL, C1970-retracted, C1972, C1225
C1992	f66r is a structural singleton in Currier B for line-initial token brevity. 30 of 34 lines (88.2%) start with a 1-2 character token, vs corpus null max distribution mean=22.1%. Next-highest folio is f43v at 18.8%, a 69-percentage-point gap. Corpus-rare standalone characters cluster as f66r line-starts (f: 4/4 corpus instances, x: 3/3, t: 2/3, d: 4/6). Pure structural fact about line-first-token brevity distribution; no interpretation of WHY f66r has this property is registered. Cross-references C156 (quire alignment), C260 (section isolation), C763-C764 (f57v R2 single-char ring as comparable structural singleton).	2	B, f66r, short-start, structural-singleton, line-first-token, null-distribution, C156, C260, C763, C764
C1993	**RETRACTED 2026-05-15 — atom-gloss header-content correspondence FALSIFIED.** Original claim: f66r M-column atoms systematically classify L-label operational role via header→content prefix correspondence (d→da 5.4x, t→ot 3.7x; cross-folio specificity 1/46). Discriminating test 2026-05-15 (Phase 684 follow-up): M-marker dominance test on the 4 cross-referenced L-labels (rary, qor, raiin, qokal) — f66r-assigned M-marker should be top-1 dominant atom class in the label's neighborhood across matched recipes. Result: 0/4 top-1 matches; 1/4 top-3 (qokal sh ranks 3rd behind o, ch). For rary [M=y], qor [M=s], raiin [M=d], the f66r M-marker is not even in top-3. Strict Phase-684 pre-reg also failed (2/4 with sh-inverted at 0.6x). Combined with frequency-matched null on 11/15 singleton split AND L1-L15 vs L16-L32 R-body zone test, the unified glossary frame collapses. The cross-folio specificity (1/46) that justified Tier 3 is reinterpreted as a multiple-comparison artifact: f66r is structurally unique on many axes (per C1992), so uniquely passing any pattern test is unsurprising.	1	B, f66r, RETRACTED, FALSIFIED, atom-gloss, character-key, C1992
C1994	Currier B Section S folios exhibit lag-1 autocorrelation of e-depth on within-paragraph cross-token-type adjacent pairs at mean z=+1.51 vs marginal-preserving null. Section B folios show mean z=-0.36 with 0/19 folios at z>2. S vs B permutation p=0.0001 (10000 perms, n_perm=500 per folio for null). Effect WIDENS when restricted to REGIME_1. Survives Mode-B-line-fraction residualization. Five top folios from exploration (f112v=+4.98, f108r=+3.91, f111r=+4.05, f55v=+3.34, f95r2=+2.76) survive killer-test controls. Pure structural fact about token-token e-depth coupling distribution; interpretation registered separately as C1995.	2	B, section, S-section, e-depth, autocorrelation, thermal-coupling, killer-test, C1404-controlled, C1260-controlled, C1789-controlled, C1308-controlled, C1106-controlled, C1206, C1455
C1995	Section S exhibits operational-compactness (dense morphological near-relative runs); Section B exhibits operational-alternation (cross-PREFIX e-depth anti-correlation). Three-tier autocorrelation decomposition of C1994 controlling for stem-locality (Tier A=near-relatives Levenshtein<=1 OR same MIDDLE; Tier B=same-PREFIX different-MIDDLE; Tier C=cross-PREFIX): Tier A both sections strong (S=+5.43, B=+4.53 — morphological clustering universal, not S-specific). Tier C cross-PREFIX S=-0.01 (null), B=-1.47. Original C1994 aggregate difference (S>+1.51, B<-0.36) decomposes into: (a) S has more near-relative pairs in proportion (3.0% vs 2.0%), (b) B's cross-PREFIX pairs alternate between high-e and low-e operations. Continuous-state thermal tracking interpretation REJECTED — Tier C collapses in S. Replaces previous architectural-granularity reading with structural decomposition: S is index/list-format dense (consistent with pharmacy-index or short-recipe-list); B is operationally varied with thermal cycling between PREFIX classes (consistent with multi-step alchemical procedures alternating thermal regimes). Tier 4 synthesis: SPECULATIVE/section_thermal_architectures.md (revised).	3	B, section, operational-compactness, near-relative, cross-PREFIX, anti-correlation, observation, C1789, C1206, C1404, C1994, three-tier-decomposition
C1996	Token-transition order constraints exceed unigram-frequency expectations on full H-track corpus. μ_actual = 22380 vs mean(μ_shuffle) = 24162 over 1000 frequency-preserving shuffles, gap = -1782, z = -38.3. Replicates Earnhart 2026 (their gap = -1831 on 37,967-token extraction; ours = -1782 on 37,429-token filtered). Convergent measurement of same constraint phenomenon captured at class level by C389 (low bigram conditional entropy H=0.41 bits) and C1025 (49-class Markov + symmetric forbidden suppression). Compatible with C109, C361, C1808. External replication.	2	GLOBAL, transition-graph, circuit-rank, order-constraint, replication, Earnhart-2026, C389, C1025, C109
C1997	Per-folio token-transition order constraint is widespread but heterogeneous. 115 folios with n>=100 tokens, mean z_μ = -1.266 (one-sample t = -8.66, df = 114, one-sided p << 1e-13), 76% folios negative, 29% below -2, 0/115 above +2. Length-confound: regression z_μ ~ log(n_tokens) gives slope = -1.14; effect partly size-amplified but genuine even at small sizes. Cross-section heterogeneity per C1999 dominates within sections. Order constraint is not corpus-aggregate artifact.	2	GLOBAL, per-folio, transition-graph, z-score, order-constraint, length-confound-controlled, C1999
C1998	INFRA-RI H_succ comparison in Currier B is confounded by frequency-induced ceiling on RI; pre-registered direction not testable under naive comparison. Naive comparison (NOT FREQUENCY-MATCHED): E[H_succ\|INFRA] = 2.89 bits, E[H_succ\|RI] = 2.29 bits, gap +0.60 bits in opposite direction from pre-reg. **Construct-validity issue:** H_succ is mechanically bounded by log2(k) where k = observed successor count. RI tokens in Currier B are predominantly rare, capping their H_succ regardless of any structural property. INFRA tokens are by definition frequent. The pre-reg's directional prediction (INFRA<RI as formulaic-glue mechanism) presumed frequency was matched; it wasn't. The +0.60 bit gap is the construct-validity confound, not a structural finding about INFRA vs RI semantic role. Pre-registered formulaic-glue mechanism is **NOT TESTED** by this measurement. Forecloses retest under same methodology; a frequency-matched comparison would be a different test. **Revised 2026-05-07** (post Phase 689 measurement-vs-mechanism hygiene pass) to reflect construct-validity issue. Original framing as "directional negative on INFRA vs RI" was inaccurate — the test was confounded from the start.	2	B, construct-validity, frequency-confound, transition-graph, H_succ, INFRA, RI, NOT_TESTED, C498, C831, hygiene-revised
C1999	Section-level transition-graph order-constraint magnitude varies systematically. Per-folio z_μ differs across 7 sections: Kruskal-Wallis H = 27.7, df = 6, p = 0.0001. Section ordering: S (-2.04) > C (-1.96) > B (-1.95) > Z (-1.20) > T (-1.12) > P (-0.93) > A (-0.74) > H (-0.30). Pre-registered post-hoc B vs H: MWU two-sided p = 0.0003, mean B (-1.95) < mean H (-0.30). By Currier language: AZC (-1.59) > B (-1.40) > A (-0.82). z_μ controls for vocabulary size via folio-specific shuffles. REGIME-mediation caveat (C1404): S-section dominated by REGIME_3/REGIME_4; section effect could be partly REGIME-composition. Length-confound caveat (C1997): partly mediated by section-typical folio length. A weakest consistent with C233 (LINE_ATOMIC), C234 (POSITION_FREE). AZC strongest consistent with C302, C311, C313 (positional grammar). Descriptive measurement; functional interpretation reserved.	2	GLOBAL, section, transition-graph, z-mu, ordering, KW-test, C1404-flagged, C233, C234, C302, C311, C313
C2000	daiin state-flush hypothesis REJECTED; no positive characterization of daiin's MI regime established. Pre-registered prediction (MI(prev; next \| T=daiin) below population median AND below significance threshold z<+1.0): T1 FAILS (daiin z=+0.76 at 67th percentile of 72 eligible tokens, ABOVE median z=-0.11). T2 PASSES (daiin z<+1.0, MI not significantly above shuffle null). T3 PARTIAL (dar z=+0.91 above median, saiin z=-0.41 below — no class-level pattern). T4 PASSES (qokedy z=+2.51, shedy z=+2.07 confirm methodology detects context propagation). **The state-flush hypothesis is rejected as a directional prediction**; daiin is statistically indistinguishable from population median (\|z-median\|<2). **No positive characterization is established by this test** — daiin is neither a low-MI state-flush operator nor a high-MI context-propagating operator at the resolution measured. T3 PARTIAL means class-level test (C2001) NOT registered per pre-reg. Auxiliary observation (NOT registered): in the broader population, MI z appears to correlate with token complexity (long compound tokens qotar +3.95, chol +3.17, qokedy +2.51 are top; short stems qokal -1.31, shey -1.24, al -0.95 are bottom) — observation only, not a tested hypothesis. **Revised 2026-05-07** (Phase 689 hygiene pass): original framing "daiin is moderate-context-propagation" converted a non-rejection into a positive characterization; revised text retains only the directional rejection and the population-median indistinguishability.	2	B, falsification, NULL, daiin, state-flush, mutual-information, MI, no-positive-characterization, C557, C998, C1998, hygiene-revised
C2001	qokedy cross-tier MI persistence — qokedy MI is non-collapsing under qo-family removal. Pre-registered Phase 688 hypothesis (MI(prev; next \| T=qokedy) restricted to (prev, next) pairs where neither is qo-prefix has z > +1.0): T1 PASSES at z_cross = +2.49. Cross-tier z is HIGHER than qo-cluster and boundary. **Morphological-clustering hypothesis (that qokedy's elevated MI is driven by qo-family token co-occurrence) is REJECTED** — cross-tier MI does not collapse. Mechanism for the residual cross-tier MI elevation (operational, recipe-structural, REGIME-conditioning per C979, section-conditioning per C1029, category-routing per C1286, or other) is not isolated by this test and is reserved as Tier 3 interpretation (see C2003). Auxiliary T4 observation (NOT registered): Phase 687 overall z-ranking does NOT predict cross-tier persistence — qotar (Phase 687 rank 1, z=+3.95) collapses cross-tier (z=-0.20); chcthy (rank 3, z=+2.77) has highest cross-tier z (+3.78); chol collapses cross-tier (z=-0.23). The "morphological clusterer" framing of qotar/chol was further refuted by Phase 689 (C2002) at same-stem density level. Cross-tier MI z is a measurement, not a mechanism (see feedback_measurement_vs_mechanism.md). **Revised 2026-05-07** (Phase 689 hygiene pass): original "operational embedding CONFIRMED" framing smuggled mechanism interpretation; revised text retains only the measurement (cross-tier MI persistence) and the directly-tested rejection of the morphological-clustering alternative.	2	B, qokedy, mutual-information, cross-tier-persistence, morphological-clustering-rejected, three-tier-decomposition, C1300, C1394, C1965, C1988, C1995, C1971, PT-013, C2003, hygiene-revised
C2002	qotar cross-tier MI collapse mechanism — three pre-registered candidates FALSIFIED. T1 (same-stem density >30% per C1995 Section S compactness): observed 1.7% (2/121 adjacent positions). T2 (folio Gini >0.70): observed 0.684 (just below threshold). T3: observed χ²=5.39, p=0.25, ratio=1.15. None of the three mechanisms predicted by C1995/C1404 explain qotar's clustering. Surprising counter-finding (T4 partial): qokedy (operational embedder per C2001) has 9.2× higher same-stem density (15.7%) than qotar (1.7%) — opposite of Phase 688's framing. The cross-tier z=−0.20 measurement (Phase 688) is preserved; the "morphological clustering" mechanism inference is refuted at same-stem level. Auxiliary structural observation (NOT registered, no mechanism test performed): per C1195 atom gloss tiers and C1487 terminal taxonomy, qotar's atom composition (qo + t-HEAD-transfer + a-MOD-yield + r-TERM-respond per C1394) is consistent with junction/marker function — borrowed framing from existing atom-level constraints, not a new mechanism claim. qotar's neighbors are dominated by o-prefix family (otal, okar, okedy, otedy) but not same-stem.	2	B, qotar, NULL, falsification, mechanism, same-stem-density, folio-Gini, section-concentration, C1995, C1404, C1962, C2001
C2003	qokedy operational-embedding candidate (Tier 3 interpretation of C2001 measurement). The cross-tier MI persistence in C2001 (z=+2.49) is consistent with qokedy carrying recipe-structural information that survives qo-family ablation. The morphological-clustering alternative was directly tested and rejected (C2001). The remaining mechanism candidates include: (a) operational/recipe-structural embedding (predecessor predicts successor through qokedy via recipe sequence), (b) REGIME-conditioning per C979, (c) section-conditioning per C1029, (d) category-routing per C1286, (e) other multi-causal joint structure. Direct test of the recipe-structural embedding hypothesis would require alignment of qokedy positions with matched-recipe phase ordinals (per C1971/C1965/C1988 framework), which has not been performed. Consistent with PT-013 (qokedy="maintain fire level"), C1300 (qo=100% k-HEAD thermal channel), C1394 (HEAD+MOD*+TERM atom model). The operational-embedding interpretation is a directional hypothesis for future phases; not promoted to Tier 2 without source-aligned or atom-functional confirmation.	3	B, qokedy, operational-embedding-candidate, interpretation, recipe-structural, C2001, C979, C1029, C1286, C1971, C1965, C1988
C2004	AZC annotation-transcript audit summary. Of 26 user-annotated AZC folios audited against H-track transcript (sample: 13 annotation files in data/folio_annotations/azc/), 20 (77%) show non-zero discrepancy on at least one of three measures (total token count, center-token count, ring-layer count). 17/26 (65%) show non-zero total-token discrepancy. 9/26 (35%) show center-token discrepancy. 1/26 shows ring-layer count discrepancy. Methodology: H-track only, uncertain tokens excluded, center-token detection via placement codes C/C1/C2/W/I/B. AZC transcript encoding has documented gaps relative to user visual inspection at scale.	2	AZC, audit, transcript-encoding, annotation-diff, measurement, gaps, C302, C311, C313
C2005	Nymph-page center-token systematic gap in H-track transcript. Of 26 audited AZC folios, 9 show user-observed center tokens that H-track transcript does not encode under center placement codes (C/C1/C2/W/I/B). ALL 9 discrepancies are in user > transcript direction. 8 of 9 are on nymph-page folios (f70v-f73r). Hypergeometric p ≈ 0.0023 for nymph-concentration vs random base rate (12/26 nymph-type folios). Binomial p ≈ 0.0039 for same-sign direction vs random. Both patterns statistically real. Specific candidate transcript-error folios: f70v2 (user=2 vs transcript=1), f70v1, f71r, f71v, f72r1, f72r2 (man+woman center), f72r3 (largest), f72v1 (balancing scale), f73r (reptile). Mechanism reserved at Tier 2: gap could reflect (a) transcriber methodological choice on nymph pages, (b) genuine missing transcription, (c) center text encoded under non-center placement codes (R3 inner ring or S0 top), or (d) user mis-counting figure elements. Direct verification requires high-resolution scan inspection or independent OCR.	2	AZC, nymph-page, center-token, transcript-gap, systematic, candidate-errors, audit, C302, C311, C313, OCR-target
C2006	**LM-corroborated MIDDLE compositionality.** Char-level LM trained from scratch on H-track corpus independently recovers MIDDLE-class compositionality at distributional level. Same-MIDDLE token pairs cluster tighter than same-PREFIX-different-MIDDLE pairs. Sister-pair tokens (ch↔sh, qok↔qot) exhibit near-mirror geometry. Atom-class HEAD vs TERM linear probe on character embeddings achieves 100% LOO accuracy with +36pp lift over random init. Convergent triple evidence corroborates compositional claims. Char-level LM does not test compositional mechanism, only that compositionality leaves distributional traces.	2	LM, char-level, BERT, MIDDLE, compositionality, sister-pair, atom-class, P1, P2, P9_binary, C1190, C1191, C267, C383, C1003
C2007	**LM recovers A/B system distinction.** Linear probe on char-LM token embeddings distinguishes Currier A from Currier B at 92% held-out accuracy, while A and B centroid cosine similarity is 0.92 (highly non-orthogonal). System distinction is real and recoverable from distributional structure alone, AND simultaneously A and B share substantial geometric overlap. Confirms C239 (folio-disjoint partition) and C281 (component sharing) and C335 (69.8% vocabulary integration) as a JOINT statistical fact: A and B are designed to be separable via methodology yet integrated via shared components.	2	LM, A_B_distinction, linear_probe, centroid_cosine, P4, C239, C281, C335
C2008	**LM-corroborated frequency-structure geometric independence.** Char-LM token embeddings exhibit |Pearson r| = 0.024 between token frequency rank and embedding centrality (mean Euclidean distance from corpus centroid). Frequency hubs are NOT structural hubs. Independent external corroboration of C1011 (manifold-automaton geometric independence) and C986 (hub eigenmode aligned to frequency gradient, separable from automaton state). Two independent methodologies (A-side eigendecomposition and char-LM embeddings) converge on the same independence conclusion.	2	LM, frequency_structure_independence, geometric, P6, C1011, C986, C1696, C1067
C2009	**Same-MIDDLE A-context vs B-context embedding divergence beyond substrate identity.** A-only and B-only char-LMs trained separately on Currier A (1255 lines) and Currier B (2006 lines) exhibit asymmetric cross-system behavior. (i) Cross-section perplexity asymmetric: B-LM is 2.8x more native-fit on B test lines than A-LM is on A test lines (B logprob advantage +0.347 vs A advantage +0.124). (ii) Procrustes alignment of 369 shared MIDDLEs (freq>=3 each section) yields residual ratio 0.30 (real/shuffle-null), substantial but imperfect alignment. (iii) B-LM penalizes forbidden-pair substitutions 30% more strongly than A-LM (-0.040 vs -0.031 mean delta). After optimal alignment, B-context embeddings retain ~30% residual structure not present in A-context. EXTENDS C522 (construction-execution layer independence) to MIDDLE-level contextual divergence. NOT a falsification of C1499/C1509 (atom-substrate identity holds; this finding is at the contextual-usage level, distinct from atom inventory).	2	LM, A_B_split, Procrustes, contextual_divergence, asymmetric_perplexity, C522, C239, C281, C384, P8
C2010	**Stratified-by-length LM surprise correlates with 18-transcriber disagreement.** Per-token pseudo-likelihood from char-LM, ranked within each character-length bucket separately. Top 1% within each length has overlap with positions where 3+ of 18 transcribers disagree with H-track at aggregate enrichment 3.40x baseline (eligible 4.8% disagree rate). Length-stratified version doubles signal-to-noise vs unstratified (1.55x). Within-length sweet spot is 4-8 chars (3.4-6.2x enrichment per length). Baseline H-track-vs-other-transcribers same-position disagreement rate is 4.8% in length buckets >=100. External validation of LM-uncertainty as an anomaly-detection signal cross-referenced against transcriber-consensus ground truth (Phase 690 audit context).	2	LM, anomaly_detection, transcriber_disagreement, length_stratified, C209, F-A-001
C2011	**LM independently flags f66r as outlier-rich.** Folio-mean LM surprise z-score for f66r = +1.61, rank 12 of 224 H-track folios. Single-folio replication via independent methodology of C1992 (f66r line-initial brevity) — confirms the structural anomaly. **Note (2026-05-15):** Original framing referenced C1993 (character-key interpretation), now retracted. LM evidence corroborates C1992 structural anomaly only, NOT the glossary interpretation.	3	LM, f66r, structural_anomaly, single_folio_replication, C1992
C2012	**Token-level forbidden-pair penalty in char-LM, asymmetric across A/B.** Token-level substitution test: replacing legal continuation token with forbidden bigram target produces a 25x stronger log-prob penalty than substituting a legal target. External token-level corroboration of C109 (17 forbidden transitions zero-occurrence) and C997 (sparse safety-buffer architecture). B-LM penalizes forbidden pairs 30% more strongly than A-LM (-0.040 vs -0.031), aligning with C521 (kernel directional asymmetry) and C1034 (token-level asymmetric forbidden suppression). PAIRED WITH METHODOLOGY NOTE: original char-level synthetic test in P7 failed because char-level model evaluates char sequences without MIDDLE-class abstraction; token-level substitution test recovers the constraint correctly.	2	LM, forbidden_pair, token_level, P7_redo, C109, C997, C521, C1034, methodology_correction
C2013	**Length-8 H-track tokens with high LM surprise are candidate transcript-error pool.** Of length-8 tokens, top 1% by LM pseudo-likelihood surprise have 41.2% transcriber-disagreement rate (>=3 of 18 transcribers disagree with H-track) versus 6.6% length-8 baseline. Enrichment 6.21x. Strongest length-bucket enrichment in stratified anomaly analysis (vs 2.3x at length-3, 4.7x at length-5, 4.1x at length-7). Concrete candidate transcript-error pool produced for follow-up; intersection with Phase 690's nymph-page center-token audit pending direct verification.	2	LM, length_stratified, anomaly, transcript_error_candidates, length_8, C209, C2010, F-A-001
C2014	**Multi-folio scaffolding-page corroboration via LM-derived folio-mean surprise.** Three folios independently flagged as anomaly-rich at z>=1.0 versus 224-folio H-track baseline: f57v (z=+7.26, RANK 1), f66r (z=+1.61, rank 12), f49v (z=+1.41, rank 13). f57v is the most distinctive folio in the entire H-track corpus. f57v hosts the AZC R2 single-char ring (C763, C764) and now-confirmed at whole-folio level the distinctiveness extends beyond the ring itself. f49v hosts L-label/example-token alternation per C497. Negative control: rosettes foldout (f86v3-v6) NOT flagged (z range -0.55 to +0.52, ranks 50-165) — confirming rosettes are operational diagrams, not instructional scaffolding (C1126, C1130). Three-of-four-testable structural-scaffolding-candidates corroboration via independent methodology.	2	LM, folio_mean_surprise, scaffolding_folios, f57v, f66r, f49v, rosettes, C763, C764, C1130, C1992, C497
C2015	**Voynich character entropy is markedly lower than matched-size natural language.** Three matched-corpus char-LMs (Voynich H-track, Latin SISMEL, English Brunschwig translation; ~4435 lines and ~38K tokens each) yield bits-per-character measurements: Voynich 0.893, Latin 1.704, English 1.403. Compression ratio (BPC / log2(vocab)): Voynich 0.207, Latin 0.362, English 0.299. Voynich is approximately 2x more compressible at the character level than matched natural language corpora. Char-level statistics of Voynich are consistent with a constructed slot-grammar notation where char-level structure IS the morphological structure (no hidden phonological layer being compressed away), in contrast to natural-language phoneme distributions where information is distributed across positions and resists char-level compression. Strengthens C171 (semantic ceiling: high compressibility consistent with operational/notational rather than linguistic content) and C1499 (universal atom substrate: compressibility consequence of constrained slot grammar).	2	LM, three_corpus, compression, BPC, char_entropy, vocab_normalized, C171, C1499, C130, C132, C1976
C2016	**Voynich position-conditional entropy U-shape externally distinct from natural language.** Char-LM per-position bits-per-char binned into 10 quantiles within line content reveals U-shape signature in Voynich (bits at edges minus bits in middle = +0.281), absent in natural language. Latin shows +0.091 (weak), English shows -0.066 (no U-shape; entropy rises monotonically from start to end as expected for natural-language sentence structure). External cross-language corroboration of C1430 (line position-conditional structure: SPEC-WORK-CLOSE architecture). Voynich line architecture is language-distinctive — NL sentences have monotonic entropy, Voynich lines have boundary-loaded specification/closure structure. Consistent with line-as-instruction-block / parameterized control-block readings.	2	LM, three_corpus, position_conditional, U_shape, C1430, line_architecture, C1729, C1837, C1842
C2017	**Industrial cipher-hypothesis falsification framework: three published-style hypotheses fail empirical plausibility test.** Built tester applying candidate Voynich -> target-language token mapping, scoring decoded text under matched-corpus target-language char-LM (English/Latin/Voynich). Tested 3 hypothesis families: Bax 2014 (10-token specific identifications), Cheshire 2019 (proto-Romance char-phonetic mapping), Currier-like consonant cipher. All three decode to 4.04-4.16x worse than real-English baseline (5.4-5.5 bits/char vs 1.33 baseline) — only marginally better than random word-substitution (6.51x; 8.4 bits/char). Framework validated by positive control (identity passthrough scores 0.99x under Voynich LM, confirming framework works) and negative control (random substitution distinguishable as gibberish). Framework operationalizes plausibility threshold: real cipher decoding should score within 1.5x of target-language baseline. None of three hypotheses meet this threshold. Empirical falsification, not theoretical objection.	2	LM, cipher_falsification, Bax_2014, Cheshire_2019, Currier, hypothesis_testing, three_corpus, C171, C1976
C2018	**Voynich n-gram bpc plateaus at n=3.** Char-level n-gram models trained on H-track corpus train split, evaluated on test split (autoregressive likelihood, Laplace smoothing): n=2 yields 2.21 bpc, n=3 yields 1.95 bpc (best), n=4 yields 1.97, n=5 yields 2.08, n=7 yields 2.62 (overfit). Optimal n=3 with diminishing returns past lag-3 and active degradation past lag-5. Empirically extends C1025 (49-class Markov + forbidden-pair generative sufficiency) from class-level generative tests to character-level compression measurement. Voynich's character-level correlation length is ~3 characters — local statistics capture the common-case structure. Methodology caveat: comparison to transformer pseudo-likelihood (2.79 bpc) is methodologically asymmetric, but n-gram saturation pattern is independent of the comparison and confirms structure depth.	2	LM, n_gram, compression, Voynich_correlation_length, C1025, C1727, C1728
C2019	**Markov-based generation reproduces Voynich distribution center but not tail.** Generated 200 synthetic Voynich lines via scheduled-token sampling. Mixed with 200 real H-track test lines. Both scored under same Voynich char-LM. Real lines: mean 0.906 bpc (std 0.426, max 3.10). Synthetic: mean 0.453 bpc (std 0.206, max 1.40). Mann-Whitney p<0.001 (distinguishable). Best single-feature classifier accuracy 82.5%. Synthetic scores 50% LOWER than real — generation reproduces statistical center but not rare-content tail (high-bpc events, anomalous tokens, single-instance lines). The ~50% real-vs-synthetic gap is concentrated in tail diversity. Extends C1153 (~40% generative design freedom) from class-distribution to character-tail layer, AND complements C2018: Voynich has shallow center + diverse tail. Tail diversity is where structurally-distinctive content concentrates (cf. C2014 scaffolding folios, C2013 length-stratified anomalies).	2	LM, generation, Turing_test, tail_diversity, C1153, C2014, C2013, C2018
C2020	**f67v2 is a caption-inventory reference page (fourth structurally-distinct scaffolding type).** Pre-registered hypothesis (per crazy-expert prediction) tested with 5 predictions on f67v2 (rank 2 of 224 by LM surprise, z=+4.12): (P-67-1) token length skewed short (4.90 vs corpus 5.06): PASS. (P-67-2) low PREFIX rate (56.7% vs corpus 82.4%): PASS. (P-67-3) ≥80% rare types (key prediction): 100% of f67v2's 57 unique tokens occur ≤2 times: PASS. (P-67-4) token count consistent with ~12 surrounding diagram elements (57 unique tokens): PASS. (P-67-5) not periodic (0.037 vs f57v's 0.87): PASS. 5/5 confirmed. Placement code distribution shows 36/60 = 60% C (Center) tokens consistent with per-element labels for a central rosette diagram. f67v2 represents a fourth structurally-distinct reference type alongside f57v (tabular C921), f66r (structural singleton C1992; glossary interpretation retracted 2026-05-15), f49v (apparatus C497). All four scaffolding types share ZERO common structural pattern but all serve reference/metadata function — heterogeneous reference apparatus consistent with single-author multi-content-type workshop manual.	2	LM, scaffolding, caption_inventory, f67v2, single_author_evidence, C497, C921, C1992
C2021	**Voynich-to-gloss translator: C1394 atom cipher is learnable from data with 92.6% held-out accuracy + 75% novel-token generalization.** Trained small autoregressive transformer (4 layer, 128 dim, ~700K params) on 8021 unique H-track tokens paired with their Morphology.atomize() output (per C1394 HEAD+MOD*+TERM structure with semantic tags: heat, cool, do, end, yield, respond, state, arrange, bind, iterate, watch, etc.). Format: input chars + SEP + autoregressive gloss generation. Held-out val set sequence-level exact-match: 92.6% (743/802). On 8 made-up Voynichese-shaped tokens never seen during training: 6/8 correct (failures are high-e-depth counting errors with 4+ consecutive e's). Model has learned the atomization RULE not just memorized corpus mapping. Operationalizes C1394 atom cipher as queryable artifact. Foundation for line-level glossing, recipe-alignment, and structural-decoding follow-up work. Methodology contribution: structural decoding rules are recoverable from data via small supervised models.	2	LM, glosser, atom_cipher, C1394, translator, sequence_to_sequence, learnable_structure
C2022	**Voynich has substantial learnable structure that contradicts natural-language priors.** Three independent pretrained-model probes confirm Voynich is structurally rich AND structurally distinct from natural language. (1) TinyLlama-1.1B base perplexity on H-track: 1388 (10.44 bpt) — useless. (2) After 3 epochs fine-tuning on H-track train split: 24.2 perplexity (4.60 bpt) on held-out test. **57x improvement, 56% bits-per-token drop**, exceeds pre-registered >=50% threshold. Comparable to pretrained TinyLlama's perplexity on Python code (22.4). (3) ByT5-small (char-level, no BPE) distinguishes real from token-shuffled Voynich at 67% classifier accuracy, confirming character-level structure. **Critically, real Voynich has HIGHER ByT5 perplexity (6.96 bpc) than shuffled Voynich (6.65 bpc): the structural arrangement actively contradicts NL char-level priors.** Combined evidence supports C171 (PURE_OPERATIONAL non-linguistic) + C2015 (char-level compression contrast) + C2018 (Markov plateau) jointly: Voynich is a rich constructed notation whose statistical structure is alien to natural language.	2	LM, pretrained_probe, fine_tune, ByT5, TinyLlama, C171, C2015, C2018
C2023	**[CLASS-LAYER SCALAR-MI HALF DEMOTED Tier 2→3, PHASE_733 — see C2061/C2062]** **MIDDLE-Layer Sequential Null vs Class-Layer Sequential Structure in Currier B.** Within-line shuffle null on Currier B yields opposite verdicts at two abstraction layers. At the MIDDLE-string layer: real I(middle; prev_middle) = 1.546 bits vs null 1.553 ± 0.017, z = −0.39 (at-null). At the 49-class layer: real I(class; prev_class) = 0.264 vs null 0.215 ± 0.013, **z = +3.91 (significantly above SHUFFLE null)**. **PHASE_733 5-gram null UPDATE:** the class-layer *scalar first-order MI* is 5-gram-REPRODUCIBLE — it is above composition but NOT above local character statistics. This SCALAR claim demotes to Tier 3 (joins C1727/C645 as a shuffle-survivor failing the sharper null). HOWEVER the macro-state *eigenstructure* (λ2) SURVIVES (C2061): the "genuinely sequential" claim holds at the eigenstructure level, not the scalar-MI level. Same data, two layers, two results — and within the class layer, two metrics (scalar-MI fails, eigenstructure survives). The C976/C1010 macro-state automaton at the 49-class projection carries above-Markov eigenstructure (C2061); the MIDDLE-token layer below it is co-occurrence-only. C109/C997 forbidden pairs are bag-of-line co-occurrence prohibitions: directional analysis of all 17 pairs yields 0 real adjacent occurrences in BOTH directions, 16/17 with zero same-line co-occurrence (per C1552 phantom pattern), 1/17 (`he`→`t`) with both directions symmetrically suppressed against fwd_null=0.53 / bwd_null=0.63. The "forbidden transitions" terminology applies at the 49-class projection (per C783 directional); at the MIDDLE layer, the constraint is co-occurrence-forbidden (per C1118 75.2% bidirectional). Operationalizes via shuffle-null methodology the layer distinction already implicit in C1118 / C1212 / C1024 / C1034 / C886.	2	shuffle_null, MIDDLE_layer, class_layer, two_layer, co_occurrence_vs_transition, C109, C627, C783, C886, C391, C976, C996, C1010, C1011, C1019, C1024, C1025, C1031, C1032, C1034, C1071, C1118, C1212, C1552
C2024	**Bio Section Carries Marginal Residual MIDDLE-Layer Sequential Structure in Currier B; Other Sections at-or-below Null.** Per-section within-line shuffle null on Currier B yields heterogeneous signatures. Section B (Bio, f74-f84 region): z = +1.49 (real I=1.137, null=1.104, excess +0.034). Section H (Herbal_B): z = −2.70. Section S (Stars/Recipe_B): z = −1.33. Section C (Cosmological foldouts, B-language text): z = −1.17. Section T (Top/intro B-tokens): z = −0.91. **Bio is the only B-section with positive residual sequential excess at the MIDDLE layer.** The whole-of-B at-null result (C2023, z = −0.39) is an average of Bio's marginal positive signal and four near-null-or-negative sections. Confirms C1048's prediction that BIO carries the strongest residual sequential structure in B. Section-level heterogeneity in residual sequential signal is consistent with C1047 (section-dynamics interaction absent at macro level but present at residual level) and C1055 (M2 near-section-decomposable).	2	shuffle_null, section_stratified, Bio_residual, B_section, MIDDLE_layer, C1047, C1048, C1055, C1085, C1086, C1116, C1404, C2023
C2025	**Currier A Class-Layer Shuffle Null at-null Confirms C225 via Independent Methodology.** Class-layer within-line shuffle null on Currier A yields real I(class; prev_class) = 0.707 bits vs null 0.698 ± 0.023, z = +0.37 (at-null). Confirms C225's "A Transition Validity = 2.1%" claim via independent shuffle-null methodology — A has minimal class-Markov transition structure. C346's reported "sequential coherence" (1.20x) therefore lives at a different organizational level than class-Markov adjacency: it must be record-level / positional / compositional (C233 LINE_ATOMIC, C240 NON_SEQUENTIAL_CATEGORICAL_REGISTRY, C422 DA articulation, C475/C729 PP co-occurrence compliance, C964 boundary-constrained free-interior). Combined with A's MIDDLE-layer shuffle-null excess of z = −5.09 (the most strongly negative across subsets — entirely sparsity-driven exclusion of unrealizable pairs), A is bag-of-line at both class and MIDDLE layers despite C346's within-record coherence. Methodological strengthening of C225: shuffle-null is a stricter test than the 2.1% validity threshold count.	2	shuffle_null, Currier_A, class_layer, sequential_coherence_locus, C225_corroboration, C225, C230, C231, C233, C240, C346, C422, C475, C729, C964
C2026	**Antidotarium Nicolai 8D Matcher Baseline — Section S Source-Matching Not Closed by Acquisition.** Featurized 124 named Antidotarium recipes using Latin keyword patterns (ignis/calefac/bulli for k; videre/color/consistency for h; donec/dum/sufficit for t; addatur/agitando for e) substituting for English in the Brunschwig compound-matcher featurizer; ran through TUNED_DIMS residual matcher. Result: no Antidotarium recipe matches any Section S folio under d=1.0 (min Section S distance = 1.375 on f106v↔YEra; min anywhere = 1.058). Top-1 attractor degenerates to f34v (Section H, REGIME_3, 115 tokens) for 82 of 124 recipes (66%). **Same f34v collapse observed for two control corpora**: Codicillus (19 PL-companion alchemy segments, in-domain): 11/19 default to f34v, no ratios > 1.30; Brunschwig 1512 (20 validated compound recipes, in-domain): 12/20 default to f34v, no ratios > 1.30. f34v universal attractor consistent with C1366 (top-5 least-anomalous folio = f34v 0.71 / f106r 0.67 / f106v 0.65 / f31r 0.62 / f66v 0.62) — a geometric centrality property of the V-side feature space, not a corpus signal. **Top-1 ratio-confidence mode of the 8D matcher is therefore not a validated evaluation method**; validated C1971 matches (e.g., C1943 f106v↔Ch40M d=0.933, C1990 f75r↔Ch.28) use hypothesis-driven distance gating instead. Antidotarium Nicolai itself is over-curated 12th-c. Salernitan teaching canon; practitioner-use sources (Mesue's Grabadin, Antidotarium Magnum) remain candidate Section S source classes per `project_section_s_source_genre_gap.md`. Acquisition closes the corpus-availability gap for Nicolai specifically but does not close the Section S source-matching gap.	2	matcher_baseline, Section_S_source_gap, top1_degeneracy, geometric_centrality, C1366, C1971, C1943, C1955, C1990, C1995, Antidotarium_Nicolai, project_section_s_source_genre_gap
C2027	**[RETRACTED 2026-05-16 to Tier 1]** Originally claimed: heat-cycle MIDDLE-class adjacency chains UNIQUE to PL-matched Section S folios, corroborating iteration-encoding mechanism. Pre-registered discriminating control on 2026-05-16 (family-stratified shuffle null + cross-group comparison) falsified three of the four pillars: (a) **"Matched-S unique" is FALSE** — both matched-S (+0.034) and unmatched-S (+0.044) Section S folios show heat-cycle adjacency excess at comparable strength across length filters; the original "unmatched folios LACK this signature" claim was a paragraph-level-mean confound with token density. (b) **"Iteration-encoding mechanism" is PARTIALLY FALSE** — iteration markers (aii/daiin family) show near-zero adjacency excess (+0.001 corpus level, 0 adjacent pairs across 4 daiin-heavy folios). The chain signal lives in heat-cycle MIDDLE classes specifically AND in closure-class (late_term) markers, NOT in the canonical iteration-marker family. (c) **The +0.0037 baseline excess decomposes** into heat_cycle (+0.026 family-stratified) + late_term (+0.038 family-stratified) — late_term contribution was missed in original framing. Surviving fact (registered as C2028): Section S vs Section B heat-cycle adjacency divergence is real and Section-level. Surviving fact (registered as C2030): late_term Voynich-wide adjacency is real. Surviving fact (registered as C2029): iteration markers don't chain at adjacency (measurement only). Methodology lesson: framework-as-null discriminating-test discipline caught the overclaim within 24 hours of registration. C2027 is preserved as Tier 1 retraction with full narrative for traceability of the audit precedent.	1	RETRACTED, FALSIFIED, iteration_encoding_mismatched, framework_as_null_caught, audit_2026_05_16, C2028, C2029, C2030
C2028	**Section S vs Section B Heat-Cycle MIDDLE-Class Adjacency Divergence.** Length-controlled within-paragraph shuffle null on MIDDLE-class first-3-chars lag-1 adjacency, stratified by class family. Heat-cycle MIDDLE classes (kee/ee — the qokee* family) cluster adjacently in Section S folios but not Section B. Section S matched (+0.034 at length 20-100, +0.037 all paragraphs ≥10, +0.060 at length 50-150). Section S unmatched (+0.044, +0.044, +0.093). **Section B near-zero across all length filters: +0.003 to +0.006.** The pattern is Section-level structural distinction, NOT matched-folio-level — both matched and unmatched Section S folios show the signature at comparable or higher strength. Survives stricter within-line shuffle null (+0.026 within-line excess vs +0.034 within-paragraph excess at matched-S, length 20-100; delta only +0.008 indicates clustering is genuine token-sequence adjacency not line-boundary positional). Concrete examples: f112v P4 `qokeedy → qokeeey → qokeeody` triple-run; f111r P5 six-token kee/ee chain `qockhey, qokeey, keeor, okeey, lkeedy, lkeey`; f108r P2 identical-token pair `qokeey → qokeey`. Cross-references heat-cycle iteration encoding documented at atom level (C1394 e MOD = thermal microstate) and anchor level (C1969 qok-window-density ×9 anchor on f75r). Refines C2027's matched-folio framing to the correct Section-level scope.	2	heat_cycle, MIDDLE_class_adjacency, Section_S_signature, Section_B_negative, structural_divergence, within_line_null, C1394, C1969, C1971
C2029	**Iteration Markers (aii / daiin Family) Do NOT Chain at Adjacency.** Across 4 daiin-heavy matched-S folios tested (f114r×11, f112v×6, f106v×3, f103r insufficient), zero pairs of daiin tokens occur in adjacent positions. Corpus-level aii MIDDLE-class adjacency excess: +0.001 (essentially zero) under within-paragraph shuffle null. Distributional measurement-only — no mechanism inference claimed for what daiin DOES do positionally. Resolves a measurement-vs-mechanism asymmetry in the prior literature: C1953 documents daiin×N count-clustering at folio/paragraph level (e.g., f114r daiin×11, f114r is C1953's canonical case), but count-clustering and adjacency-clustering are independent measurements; count-presence does not entail token-sequence chaining. Daiin distribution within paragraphs is non-uniform across all 3 folios with sufficient data (max-deviation-from-uniform >0.20), but the LOCATION of clustering varies by folio (f114r late-biased 0.455, f112v mid-range 0.333, f106v early-biased 0.000). Single-folio late-position bias on f114r does not generalize per pre-registered multi-folio replication test (1/3 folios pass late-bias criterion). C2029 registers only the chaining-null measurement; the f114r-specific phase-boundary observation is logged in memory at Tier 4 pending more data.	2	iteration_markers, daiin_no_chain, aii_class_null, measurement_only, no_mechanism, distinction_from_count_clustering, C1953, C2000, C2001, C2002
C2030	**Voynich-Wide Late-Term MIDDLE-Class Adjacency Clustering Within-Line.** LATE-class MIDDLE families (ar, ary, aly, al — the closure/output-terminal markers per C539/C562) chain adjacently at +0.036 within-line excess in matched-S folios (within-line null isolates positional artifact from genuine adjacency). Voynich-wide pattern across all tested groups: matched-S +0.038, unmatched-S +0.017, Section B +0.041 (at length-filtered comparison). Survives stricter within-line shuffle null (preserves line membership and position): late_term within-line excess +0.0365 vs within-paragraph excess +0.0391, delta only +0.0026. Clustering is genuine token-sequence adjacency within lines, not purely line-boundary positional artifact. **Scope clarification:** the within-line shuffle controls for within-line position randomization but does not control for cross-line adjacency at line boundaries (last token of line N to first token of line N+1 remain canonically paired). The +0.036 within-line excess therefore reflects within-line adjacency clustering specifically. Cross-references C1235 (line-final routing) and C539 (LATE prefix class line-final concentration) as related but distinct phenomena — those describe line-final concentration; C2030 describes within-line adjacency clustering of closure-class MIDDLEs. Predicts (NOT tested): closure protocols may have internal bigram grammar (e.g., directional `or → al` vs `al → or` asymmetries, forbidden LATE-LATE pairs parallel to C109's class-level forbidden transitions).	2	late_term, closure_protocol, MIDDLE_class_adjacency, within_line_null, Voynich_wide, C1235, C539, C562
C2031	**Section B vs matched-S Operational e-Depth Sequential Asymmetry.** Per-paragraph e-depth (number of consecutive `e` MOD atoms in MIDDLE per C1394, the registered thermal microstate control parameter per C1225) lag-N autocorrelation analysis, length-controlled (20-200 word paragraphs), with within-folio shuffle null per `feedback_within_folio_shuffle_null_first.md`. Two complementary measurements form one structural divergence: **(a) Section B operational tokens show period-2 e-depth modulation** (lag-1 excess = −0.026 in operational-only subset, stronger than mixed-token −0.016; lag-2 = +0.011 positive jump, lag-3 = +0.000 back to null; lag2/lag1 ratio = −0.66, textbook period-2 sign-reversal pattern). **(b) matched-S operational tokens show NULL sequential e-depth structure** (lag-1 excess = −0.002, indistinguishable from null; lag-2 = −0.003, lag-3 = +0.006). Within-folio shuffle null: matched-S all-tokens lag-1 +0.022→+0.033 (sustained or stronger), Section B all-tokens lag-1 −0.016→−0.011 (oscillation preserved); signal is line-level structure, not folio-composition shadow. AX/operational decomposition: matched-S all-tokens sustain (+0.023) is driven by SCAFFOLD tokens (+0.019), not operational tokens (NULL); Section B operational tokens carry the period-2 signature (−0.026 stronger than mixed −0.016). **Scaffold-token e-depth clustering at +0.016-0.019 is Voynich-wide background** (same in both groups; non-discriminating; likely connected to C539/C1235/C2030 line-final routing phenomena, NOT registered as separate finding here). Subsumes C2027's narrow-heat-cycle surface measurement (lag-2/lag-1 ratio 8.28 in Section B vs 0.36 in matched-S) — that pattern is the surface manifestation of underlying e-depth control parameter divergence at the operational-token level. **Pre-registered binary criteria locked before running:** SUSTAINED-DEPTH (SS1 lag1>+0.010, SS2 lag2>0 AND lag2/lag1<1.0, SS3 lag3>0 AND lag3<=lag2) — matched-S 3/3 PASS in all-tokens but FAIL in operational-only (operational FLAT, not sustained). OSCILLATING-DEPTH (OD1 lag1<+0.005, OD2 lag2>+0.005, OD3 lag2/lag1>1.2 or lag2>+0.010 if lag1≈0) — Section B 3/3 PASS in all-tokens AND in operational-only (oscillation strengthens under operational restriction). The asymmetric outcome (Section B operational has structure; matched-S operational has none) cannot be produced by framework vocabulary echo, which would predict uniform behavior. Measurement-only Tier 2 registration; operational interpretation candidate ("trajectory-encoded vs instruction-encoded") deferred to SPECULATIVE/encoding_modes.md at Tier 3. **2026-05-16 update:** Codicillus cross-validation FAILED for the trajectory-encoded-alchemy cross-language framing (see C2032); structural divergence is Voynich-internal, mechanism unidentified; SPECULATIVE/encoding_modes.md marked half-falsified accordingly.	2	e_depth, sequential_structure, operational_vs_scaffold_decomposition, within_folio_shuffle_null, period_2_oscillation, sustained_depth, Section_B, matched_S, asymmetry, mechanism_measurement, C1394, C1225, C1197, C1995, C2027_retracted_predecessor, C2028, C2030
C2032	**Voynich Sequential Stem-Class Structure is Absent from Natural-Language Latin Reference Corpora (Engineered Substrate Triad, Third Axis).** Cross-language test of the C2031 sequential e-depth asymmetry. Per-paragraph stem-class lag-N autocorrelation (Latin stem-class = first 3 chars after case-ending stripping; methodology consistent with prior cross-corpus tests) applied at length-matched 20-50 word paragraphs to Codicillus Latin and Mesue Liber Primus Latin. Pre-registered binary criteria for the encoding-modes Tier 3 interpretation: Codicillus should show period-2 sign-reversal matching Voynich Section B's lag2/lag1 = −0.66; Mesue should show monotonic decay matching matched-S's +0.66. **Result: NEITHER Latin corpus shows the predicted pattern.** Codicillus alchemy Latin: lag-1 = −0.006, lag-2 = −0.000, lag-3 = +0.005, lag2/lag1 = +0.05 (near-zero, natural-language baseline). Mesue pharmacy Latin: lag-1 = −0.002, lag-2 = +0.000, lag-3 = +0.001, lag2/lag1 = −0.17 (near-zero). Voynich reference values: Section B −0.66, matched-S +0.66 — order-of-magnitude separation from Latin baselines with NO overlap. **Cross-language structural corroboration FAILS for the trajectory-encoded-alchemy interpretation;** what survives is the demonstration that the Voynich-internal section-divergent sequential e-depth structure (C2031) is ABSENT from genre-matched natural-language Latin reference corpora. The asymmetric pattern is Voynich-specific structural engineering, not a generic alchemy/pharmacy linguistic property. Forms the **third axis of the engineered substrate triad** alongside C2015 (Voynich ~2× more compressible than NL at char level) and C2022 (anti-NL char distribution + Markov plateau at higher-order). Three orthogonal measurement axes — information density (C2015), surface statistics (C2022), sequential grammar (C2032) — independently establish that Voynich is structurally distinct from genre-matched natural-language baseline at multiple decomposition levels. SPECULATIVE synthesis: see `context/SPECULATIVE/engineered_substrate_triad.md`. Methodology vindicates `feedback_mechanism_cycle_procedural_ceiling.md` (2026-05-16): the encoding-modes interpretation was a Tier 3 candidate that survived all Voynich-internal discriminating controls but failed external grounding — exactly the trap pattern the ceiling memory note predicts at this project stage.	2	engineered_substrate, Voynich_vs_NL, sequential_grammar, cross_language_test, encoding_modes_falsification, structural_distinctness, C2015, C2022, C2031, Codicillus, Mesue_Liber_Primus, SPECULATIVE_engineered_substrate_triad
C2033	**Voynich Currier B V/C-Partition Projection Flexibility — Uniquely Tunable vs Natural-Language Latin Baselines.** Voynich Currier B's character-shape V/C-partition optimization (hill-climbing search across 2^20 vowel/consonant partitions to minimize Jensen-Shannon divergence between Voynich CV-pattern distribution and target NL CV-pattern distribution, target=Italian Dante Inferno, 20K-token cap, 15-30 random restarts) produces hill-climb improvement of **+0.286 bits** from EVA-vowel baseline (JS=0.544 → optimal JS=0.257) to bootstrap-stable optimal partition {a, g, h, n, o, r, y} (5/5 identical resamples, JS spread 0.0027). **This improvement is 2.4× the maximum NL Latin improvement** observed across 8 natural-language Latin corpora (Codicillus +0.001, Mesue +0.026, PL Testamentum +0.001, Brunschwig +0.120, SISMEL +0.006, Caesar +0.009, Piccolomini +0.009, Ebendorfer +0.000; max = Brunschwig +0.120; mean = +0.020). Most NL Latin corpora improve essentially zero (≤0.01) — their known vowels {a,e,i,o,u,y} are already near-optimal for projection to Italian, leaving no headroom for hill-climbing. Voynich's EVA partition is far from optimal (baseline 0.544 vs operational Latin 0.235-0.460), giving substantial headroom that hill-climbing exploits. **Substrate finding is FLEXIBILITY, not CLOSENESS:** Voynich's final optimal JS (0.257) is NOT uniquely low — SISMEL Testamentum Latin baseline (0.229) and Codicillus baseline (0.270) match or beat Voynich's hill-climbed optimum. Multiple discriminating tests confirm the partition is positional-grammatical (mean max-position-bucket 84% across 7 chars, within-token character scrambling destroys recovery 0/5 trials, within-folio shuffle null destroys recovery 0/3 trials), NOT identity-phonological (NL-vowel partition gives JS=0.735, much worse than core's 0.250; NL-operational sanity null shows NL Latin corpora recover NL-vowel-like sets at 66% mean overlap vs Voynich's 43%), and combinatorial-not-frequency (top-7-by-frequency overlaps only 4/7 with core). Atom-system correspondence is PARTIAL: 5/7 partition chars map to slot-grammar atoms (h↔C1487 TRANSPARENT terminal, n↔C1209 terminal, y↔end-marker, a↔HEAD slot, o↔C1502 HEAD arrangement); 9 other positionally-locked Voynich chars (e, i, q, m, k, t, d, f, s) are excluded by the optimization (Control 3 atom-role uniqueness check FAILED in narrow framing — partition is a SUBSET of slot-grammar atoms, target-language-fitted). **Explicit confound disclaimers:** (a) Voynich's smaller character inventory (20 vs Latin's 22-26) may give optimizer mechanical headroom — uncontrolled; (b) Voynich's higher baseline JS gives larger improvement room mechanically — normalized improvement (improvement/baseline) gives Voynich 52.5% vs Brunschwig 26%, still 2× max NL but less dramatic than absolute; (c) N=1 in engineered-grammar column — "engineered grammars are tunable" class claim requires synthetic-corpus or cross-script transfer test (queued PHASE_698). Currier A optimal partition {a, g, h, k, l, n, r, t, y} shares 6/7 chars with Currier B's core (substrate-deep shared partition per C1499 with dialect-specific differences). Pre-registered criteria summary: 8 of 10 binary criteria PASS; 2 caught morning's overclaims (atom-role uniqueness narrowed "rediscovers slot grammar" framing; NL→NL ceiling narrowed "uniquely close to Italian" framing). Three operational overclaim retractions documented in PHASE_697 audit trail. Independently motivated: Layfield & Davis (2026 DHQ) LSA-based methodology adapted with project's H-track + P-placement filtering. **Methodology lesson:** the discipline that killed the closeness framing today is the same discipline that makes the flexibility framing trustworthy — register the measurement, not the operational interpretation. See `feedback_calibrate_thresholds_against_controls.md`.	2	engineered_substrate, Voynich_vs_NL, projection_flexibility, V_C_partition, hill_climb, Layfield_Davis_replication, methodology_bridge, NL_distinct_measurement, audit_trail, three_narrowings, C2015, C2022, C2032, C1394, C1209, C1487, C1499, C1502, C864, project_section_s_source_genre_gap
C2034	**Catalan Cardinality Baseline — III.19.0 ×4+×9 Conjunction Is Unique in SISMEL.** Systematic regex sweep across 189 SISMEL sub-recipes for Catalan cardinality phrases (quatre/iv/iiii × vegades; nou/ix × vegades; tres/iii × vegades; etc.). Only 2 of 189 contain ANY cardinality phrase in Catalan: III.12.0 (×3 only) and III.19.0 (×4 AND ×9). III.19.0 is the ONLY Catalan sub-recipe with both ×4 and ×9 jointly (1/189 = 0.5% corpus rate). Combined with C1889 (f75r is the corpus-singular Currier B folio with 4-identical-token run, 1/82), the joint conjunction probability under independent random pairing is approximately 1/16,500. Bounds look-elsewhere effect at Catalan corpus level to essentially zero. Reinforces C1889/C1965/C1969/C1971 by confirming the f75r↔III.19 cardinality match is not retrievable from any other Catalan sub-recipe in the corpus. (Latin baseline is higher due to ordinal "quart[oa]" / "tertia" forms appearing in many contexts; the Catalan baseline is the cleaner discriminator because Catalan cardinality phrases use specific "X vegades" construction.)	2	cardinality, baseline_rate, SISMEL_Catalan, look_elsewhere, joint_singular, C1889, C1965, C1969, C1971, C1989, project_chapter_numbering_remap
C2035	**Mantel Null on Folio-Aggregate Token Similarity vs Latin Chapter Content Similarity.** Across 14 catalogued folios in C1971 (excluding f76r diagram folio), pairwise Voynich token-set Jaccard distance is uncorrelated with pairwise matched-Latin-chapter content-word Jaccard distance. Pearson correlation between distance matrices computed across 6 variants. Range: ρ = −0.21 to +0.12. Most-favorable variant (Part III only, MIDDLE-level, overlap coefficient): ρ = +0.12, z = +1.09, two-tailed p = 0.27, one-tailed positive p = 0.14. Permutation null with 5000 shuffles. **Operational-class signature matching (C1971) does NOT propagate to folio-aggregate lexical overlap.** Bounds the interpretation of C1971: the 8D matcher's operational-class identification is real but does not entail token-level content correspondence between folios and their matched Latin chapters. C2034's specific structural conjunctions (×4 + ×9 anchors) remain discriminating; what fails is the diffuse lexical-overlap signal that would be expected under a textual-cipher reading. Combined with C2034 + sharpened C1971, gives a complete characterization: cold-read matching is structural/operational at the discriminating-feature level, not lexical at the token-aggregate level.	2	bounding_constraint, Mantel_null, folio_aggregate, lexical_overlap, C1971_scope, operational_not_lexical, C1366, C1888, C1971, near_miss_separation_complement
C2036	**Closed-Lexicon NL Hypothesis FALSIFIED — MIDDLE Inventory Size Refutes Chinese-Character-Style Lexicon.** Crazy-expert speculative hypothesis (PHASE_698): MIDDLEs might be arbitrary lexical units of a restricted technical lexicon (~80-150 morphemes, Chinese-character-style closed inventory) rather than compositional operational primitives. Test: compute MIDDLE distribution statistics on Currier B vs natural-language Catalan morpheme statistics matched in token count. Result: Voynich Currier B MIDDLE inventory = 1,302 unique types in 21,610 tokens — **10× larger than the 80-150 hypothesized closed-lexicon range.** Distribution is more concentrated than NL (top-10 token share 49.1% vs Catalan subsampled 25.3%) and Zipf slope is steeper (−1.51 vs Catalan −0.91). TTR 0.060 (vs Catalan 0.203 at matched n). MIDDLE distribution looks operational with productive tail, not closed lexical inventory. Hapax rate (63.0%) does match NL-Catalan (64.2%), indicating productive-tail behavior similar to natural language's long tail of rare words — but this is consistent with multiple interpretations (open-class operational specifications, productive morphology, or genuinely lexical-content tail) and does NOT salvage the closed-lexicon framing. Parallels C1976 (polyalphabetic cipher rejected), C1376 (Currier B not NL), C130 (DSL rejected). Follow-on phase queued: discriminating test between operational-productive-tail vs lexical-content-tail via per-folio hapax concentration index (crazy-expert proposal; C914's 3.7× label enrichment as precedent).	1	NL_falsification, closed_lexicon, MIDDLE_inventory, Chinese_character_hypothesis, distribution_statistics, productive_tail, C130, C1376, C1976, C2015, C2022
C2037	**AZC-Diagram-Token Placement Contamination Correction.** Pre-registered H3 test (hapax > n_2_3 paired sign test on top-decile folios) verdict depends on placement filter choice. P-only filter gives 6/8 FAIL. P+L (paragraph + label tokens) gives identical 6/8 FAIL — labels alone do NOT explain placement sensitivity. All-placement filter (P + L + R + S + C + X + Y + N + T) gives 7/8 PASS. The verdict flip is driven specifically by AZC diagram tokens (R rings, S stars, C circles, etc.), NOT by labels. Diagnostic: hapax cohort grows from 820 (P-only) to 866 (all-placement), and the added 46 hapaxes are MIDDLEs that appear exactly once on a diagram position (and nowhere else in B paragraphs/labels). These AZC diagram singletons have categorically different distributional properties per AZC architecture (C300-series), and concentrate on diagram-heavy folios which artificially inflates per-folio enrichment ratios there. For MIDDLE inventory or per-folio frequency analyses on paragraph-text content, the defensible standard placement filter is P+L (equivalent to P-only for this purpose); all-placement contaminates with AZC diagram tokens. PHASE_699 v2 H3 PASS verdict (7/8) is AZC-token-contamination artifact, not a real paragraph-text signal.	2	methodology, placement_filter, AZC_contamination, MIDDLE_inventory, hapax_cohort_definition, C300, C1135, AZC_distinct
C2038	**Low-Frequency Hapax-Band Corpus Census.** Distributional measurement: Currier B has 866 corpus-wide hapax MIDDLEs (all-placement filter, H-track non-uncertain). The C1135-catalogued unmatched-PP MIDDLE set ("dark pipeline," 300 MIDDLEs, mean 5.7 tokens, section-concentrated Herf=0.716) has a heavily-skewed frequency distribution: median frequency=3, 60% of catalogued MIDDLEs at n≤3, 28% at n=1 (hapax frequency band). 70 corpus-wide hapax MIDDLEs (sample of 866) overlap with C1135's catalog under exact MIDDLE-string match. 96% (67/70) of these overlap MIDDLEs occur on P-placement (paragraph text); 0/70 occur on R (ring) placement; <5% on C (circle), X, or T placements. **Distributional census only.** The 70-MIDDLE overlap is consistent with C1135's own frequency profile (the catalog already documents a long low-frequency tail extending to hapax band) and does NOT constitute independent association evidence beyond what C1135's frequency profile implies. The within-folio shuffle null on the rate-correlation form of this measurement (see C2039) demonstrates that the per-folio relationship is composition shadow, not hapax-specific.	2	distributional_census, hapax_corpus_wide, low_freq_band, MIDDLE_inventory, no_association_claim, C1135, C1137, C1140
C2039	**Hapax×Dark Rate vs Hapax Enrichment Correlation Is Composition Shadow.** Per-folio analysis: hapax×dark-pipeline rate (count of hapax-MIDDLE occurrences on folio normalized by folio token count, restricted to MIDDLEs in C1135 catalog) vs per-folio hapax enrichment (folio hapax token rate / corpus hapax token rate) gives raw Pearson r=0.557, TTR-controlled partial r=0.395. Within-folio shuffle null (200 permutations preserving per-folio token counts and global MIDDLE frequency distribution): observed partial r vs null mean 0.286 (SD 0.119) gives **z=0.91, p=0.18**. The signal does NOT survive within-folio shuffle null. Folio-composition shadow, NOT hapax-specific association beyond TTR + composition. Notable secondary: raw r=0.56 gives z=2.30 (nominally significant), but TTR control absorbs half the signal and within-folio shuffle absorbs the rest (z_raw=2.30 → z_partial_TTR=NA → z_partial_TTR_plus_within_folio_null=0.91). **Third documented within-folio-null falsification in +0.4-aggregate-rho pattern**, following k-e-depth thermal regimes and triple-i ↔ iter-terminal (both 2026-05-11). Reinforces `feedback_within_folio_shuffle_null_first.md`: aggregate rho in +0.15 to +0.65 range with no within-folio null is the documented composition-shadow signature; PHASE_699 confirms this for the third time. Specific lexical-content-tail interpretations (PHASE_698 crazy-expert proposal of hapaxes as material/parameter identifiers) are NOT supported by per-folio rate analysis at corpus scale.	2	within_folio_shuffle_null, composition_shadow, lexical_content_tail_falsification, third_documented_case, methodology_validation, C2038, C1135, feedback_within_folio_shuffle_null_first
C2040	**Six Medieval Periodic-Notation Alternative Classes EXCLUDED via Peak-Specificity Test.** External adversarial corpus test. Synthetic corpora generated for canonical medieval periodicities: Weekly (P=7), Zodiac (P=12), Indiction (P=15), Computus Metonic (P=19), Solar dominical (P=28), Lunaria (P=30). Each shows peak-specificity ≈ +1.0 at its target lag by construction. Peak-specificity metric: agreement_rate(P) − mean(agreement_rate at lags P±1..±4). Discriminates SHARP cyclic peak (synthetic) from UNIFORM topical elevation (NL Mesue ≈ 0 across all periods). Voynich Section B and matched-S tested on each period: peak-specificity ranges from -0.18% to +0.36% of synthetic baselines across all 6 classes, statistically indistinguishable from NL Mesue. **All 6 classes EXCLUDED** (Voynich peak-specificity < 10% of synthetic threshold). Multiple-comparisons: 0/6 false positives observed. **Scope limit:** peak-specificity metric appropriate for periods ≥ 7 where ±4 neighborhood window doesn't catch period multiples; period-2 case has secondary-peak-in-neighborhood artifact (Voynich Section B period-2 specificity reads 0.86% of synthetic due to lag-4 secondary peak inclusion). Voynich's known period-2 grammar remains confirmed via C2032's lag-ratio methodology, NOT via peak-specificity. Combined with mensural falsification (C2032 cross-language test, 2026-05-16), brings cumulative alternative-class falsification series to 7 medieval periodic notational systems excluded. **Bounded scope:** measurement-level claim about these 6 specific periodicity classes; does NOT claim "Voynich isn't notation" or "Voynich is unique" — see methodology lesson below.	2	external_adversarial, alternative_class_exclusion, peak_specificity, multi_class_sweep, computus_falsified, mensural_followup, C2031, C2032, feedback_calibrate_thresholds_against_controls, feedback_peak_specificity_for_periods_geq_7
C2041	**LATE-Class Closure Protocol Directional Asymmetry (`ar → al`).** Within-line LATE-LATE bigrams in Currier B P-placement extracted via Morphology.extract MIDDLE field equal to one of {ar, ary, aly, al, dar, dal, dary, daly, or, ory, oly, ol} (closure/output-terminal MIDDLE inventory per C539/C562). 320 LATE-LATE bigrams across 17 unique types observed in 2,299 within-line sequences. Of 6 unordered pairs meeting N≥5 floor for FDR testing, ONE pair passes pre-registered combined criterion (Benjamini-Hochberg FDR p_BH < 0.05 AND |asymmetry| ≥ 0.30): **`ar → al` = 39 occurrences vs `al → ar` = 14 occurrences.** Three near-miss pairs show consistent +0.23 asymmetry toward `ol` as later position (ar→ol 27/17, al→ol 16/10, or→ol 16/10) but do not survive FDR at current N. Forbidden-bigram complementary test was INCONCLUSIVE (data sparseness: 320 bigrams across 144 possible 12×12 types yields mean expected per type ≈2, below pre-registered ≥5 floor; zero bigrams qualified for the test; not a negative result). Pre-registered combined criteria assign Tier 3 when exactly one of two tests passes. **Refines C2030 by adding directional sub-structure to within-line LATE adjacency clustering.** Operationally suggests closure protocols have ordered structure (`ar` precedes `al` ~2.8× more often than reverse) — interpretation candidate "ar = primary closure, al = final closure" deferred to SPECULATIVE pending external grounding. Methodology note: within-line shuffle null implicitly tests against positional artifacts (under shuffle, A→B and B→A directions are exchangeable); the +0.47 asymmetry is genuine directional bias, not positional-distribution artifact. **PHASE_705 refinement (2026-05-19):** Terminal-atom generalization test examined whether ar→al is one instance of a broader r-terminal → l-terminal class-level grammar. Aggregate r-class (ar/dar/or) → l-class (al/dal/ol) = 94 vs 51 PASSES pre-registered Test A. However, per-pair direction test failed strict 6/9 criterion (5/9 r→l, 0/9 l→r, 4 empty pairs all involving rare dar/dal). Expert consultation concluded the aggregate inherits C2041 signal: removing the ar→al pair from aggregate yields r→l=55 vs l→r=37, asymmetry +0.196, p≈0.06 (NOT significant) — the "generalization" is largely C2041 re-measured, not independent. **Load-bearing diagnostic: or→al at +0.05 is near-symmetric.** If r→l were class-grammar, or→al should also be asymmetric. It is not. The pattern is therefore (a) ar-lexeme-specific (ar prefers preceding al and ol) + (b) ol-as-late-destination tendency (both ar→ol and or→ol show +0.23 asymmetry). C2041 sharpened: not "LATE-class directional grammar" but "ar-lexeme directional preference + ol-as-late-destination." y-class members (ary/aly/dary/daly/ory/oly) of the original C2030 LATE inventory do NOT exist at MIDDLE-extraction level (parsed as MIDDLE=ar/ol/etc + SUFFIX=y); only 1 y-class MIDDLE token in entire Currier B P-placement — closure claims involving -y terminals require suffix-level not MIDDLE-level measurement. PHASE_705 closed INDEX-only (no C2042 registered) per crazy-expert methodological argument that aggregate inherits ~37% of signal from ar→al pair already in C2041.	3	late_term, closure_protocol, directional_asymmetry, MIDDLE_class_bigrams, within_line_null, FDR_corrected, refinement_of_C2030, lexeme_specific_not_class_grammar, ol_as_late_destination, C2030, C539, C562, C886, C109
C2042	**Voynich Atom-Layer Vocabulary Categorical-Homogeneity.** Project's existing 18-atom inventory (C1195 ATOM_GLOSSES, current as of 2026-05-20) classified by gloss semantic category: OPERATION (action-role) vs ENTITY (thing/value) vs PROPERTY (quality/state) vs FUNCTION (grammatical glue) vs AMBIGUOUS_OP_* (operation-or-entity/property dual-glossable). Result: 13/18 atoms unambiguously OPERATION-role; 5/18 ambiguous (m=final OP/PROP; l=state OP/ENT; f=flag OP/ENT; s=sequence OP/ENT; x=diagram OP/ENT); 0/18 unambiguously ENTITY-pure, PROPERTY-pure, or FUNCTION-pure. **H_OPERATION = 72% strict (op-pure only) to 100% inclusive (treating ambiguous atoms as project uses them operationally).** Comparison corpora at multiple granularities: (a) Latin Codicillus top-50 word-forms cleaned of OCR fragments = 12% OPERATION, 54% ENTITY-dominant; (b) Latin productive morpheme inventory (~46 derivational + inflectional suffixes from Allen/Gildersleeve grammar reference) = 15% OPERATION, 43% FUNCTION-dominant; (c) Mensural duration classes (8 items from MEI corpus) = 0% OPERATION, 100% ENTITY (floor control — establishes that "small inventory + categorical homogeneity" alone is not informative; dominant category matters); (d) Forth CORE wordset (57 items) = 100% OPERATION; (e) x86 base instructions (56 items) = 100% OPERATION (Forth/x86 are designed-monocategorical positive controls — they verify the methodology recognizes operational-DSL inventories but are non-load-bearing for the Voynich claim). **Load-bearing contrast:** Voynich atom-layer has 0/18 non-operational atoms vs Latin morpheme inventory's ~85% non-operational morphemes (FUNCTION 20, ENTITY 11, PROPERTY 8 of 46) — zero-count asymmetry at any reasonable sampling. The categorical signature distinguishes Voynich's atom-layer from NL morpheme inventories (heterogeneous-categorical) and from non-operational symbolic systems (mensural). **Scope caveats:** (1) Result reported as 72-100% band, not 100% — the inclusive coding upper bound depends on gloss judgment for 5 ambiguous atoms; if a stricter audit demoted ambiguous atoms to ENTITY, strict H_OPERATION would stand at 72% (still 4-6× higher than Latin baselines). (2) Category assignments are hermeneutic (glossing judgment), placing this measurement at Tier 3 not Tier 2. (3) Signature distinguishes "operational" from "non-operational" categorically; does NOT specifically prove "procedural DSL" — could equally fit operational specification language or taxonomic classification system. (4) Forth/x86 positive controls are tautological by design (programming-language opcode sets are constructed monocategorical); load-bearing comparison is Voynich-vs-Latin and Voynich-vs-mensural. (5) Mechanism interpretation ("Voynich IS a programming language") remains Tier 4 SPECULATIVE — promotion requires external grounding (per `feedback_mechanism_cycle_procedural_ceiling.md`). (6) Framework-as-null discipline applied: result fits Tier 0 closed-loop-control framing cleanly which is yellow flag per `feedback_framework_as_null.md`, but specific zero-counts (0 entity-pure, 0 function-pure, 0 property-pure) are sharp enough to be discriminating measurement rather than framework-echo. (7) Atom glosses used to compute H_OP were assigned via project's 7-axis battery framework — Voynich-side category assignment carries some framework baggage; mensural and Latin baselines are externally grounded. **Refines/extends C1195 (atom gloss inventory), C1003 (pairwise compositionality), C1190/C1191 (MIDDLE atomicity), C1394 (HEAD+MOD*+TERM template). Does NOT conflict with C171 (semantic ceiling) because claim is about ROLE-category not lexical-meaning content.**	3	atom_layer, categorical_homogeneity, operational_role, gloss_classification, comparison_to_NL_morphemes, mensural_floor_control, programming_language_analog, tier3_glossing_hermeneutic, expert_scrutiny_applied, C1195, C1003, C1190, C1191, C1394, C171
C2043	**Atom-Level Slot Features Carry Forward-Predictive Information Beyond 49-Class Label (Sub-Class Refinement).** PHASE_711 main test. 10,111 within-line adjacent (current, next) token pairs in Currier B P-placement where both tokens have C121 49-class labels. 5-fold folio-out CV with three model architectures, all multinomial LogReg with L2 regularization (apples-to-apples calibrated comparison): (a) Markov reference (class-only empirical transitions, α=0.1 Laplace) CE=4.8785 bits / Acc@1=13.67%; (b) LogReg class-only baseline CE=4.7597 / Acc@1=13.76% / Acc@3=30.5%; (c) **LogReg slot model (class + 6 slot features: prefix_cat, e_depth ∈{0,1,2,3+}, head_atom, term_atom, has_suffix, suffix_first) CE=4.6903 / Acc@1=16.12% / Acc@3=33.6%**; (d) Shuffle control (same LogReg architecture, slot features randomly permuted across training tokens) CE=4.8377 / Acc@1=13.17% / Acc@3=29.5%. **Slot model improves over class-only baseline by +0.0693 bits CE / +2.36pp Acc@1 / +3.1pp Acc@3, replicating 5/5 folds with consistent direction.** Slot model beats shuffle control by +0.1473 bits CE / +2.95pp Acc@1 — rules out overfitting/random-feature inflation. Pre-registered thresholds (locked before test): CE improvement ≥0.05 bits PASS, real gain over shuffle ≥0.04 bits PASS, accuracy improvement ≥2pp PASS. All three axes triggered PARAMETER-SLOT INFORMATIVE verdict. **Scope:** measurement of forward-predictive value of slot features beyond class label; effect size modest (1.5% of total CE) but consistent and survives shuffle control by 2× margin. **Initial methodology note:** first run used HistGradientBoosting which gave PATHOLOGICAL verdict due to GBM probability miscalibration (CE=5.81 worse than Markov 4.88 despite slot beating shuffle on accuracy +6.4pp); re-run with calibrated LogReg gave clean apples-to-apples verdict. Per `feedback_calibrate_thresholds_against_controls.md`: methodology choice can flip primary metric without changing underlying signal; calibrated baseline comparison was the load-bearing fix. **Refines C1025** (M2 generative sufficiency 87%) by showing slot features provide additional forward-predictive value — but does NOT beat M2 (M2 is generative, this is predictive accuracy). **No conflict with C1004** (no fourth architectural layer beyond C121) — slot features provide within-C121 sub-class refinement, not a new architectural layer. **Mechanism interpretation registered separately as C2044 (rejected parametric reading).**	2	parameter_slot_decoding, sub_class_refinement, forward_prediction, CE_improvement, shuffle_control, 5_fold_folio_CV, calibrated_LogReg, C121, C1025, C1004, methodology_calibration_lesson
C2044	**Parametric-Semantics Interpretation of Slot Features REJECTED by Pre-Registered Diagnostics.** PHASE_711 follow-up. Crazy-expert pre-registered TWO discriminating tests in PHASE_710 follow-up speculation to distinguish "atoms function as opcodes + operands with parametric semantics" from "atoms function as sub-class labels refining C121 partition." Both tests REJECT parametric reading. **Test 1 — Within-class retention:** For each of top-10 most-frequent current-classes, held class fixed and tested if slot features add WITHIN-class forward-predictive value via 5-fold folio-CV. Crazy-expert thresholds: >50% retention of full-slot gain → parametric survives; <20% → sub-class refinement wins. Result: **7/10 classes show full-slot model PERFORMS WORSE than marginal baseline within fixed class** (slot features actively hurt within-class prediction — class 13 -0.009, class 8 -0.277, class 31 -0.395, class 32 -0.297, class 29 -0.084, class 14 -0.470, class 9 -0.463); only class 33 had positive full-slot gain (+0.034) but e-depth alone beat full-slot there. **Slot features have no within-class predictive value; PHASE_711 main test's 0.07 bits gain comes entirely from BETWEEN-class differentiation** (slot features help identify class membership at finer granularity than C121, not parameterize next-instruction within class). **Test 2 — Feature importance ordering:** Crazy-expert prediction if parametric: HEAD atom dominates >> e_depth >> TERM atom >> suffix_first (HEAD selects operator domain per C1475's 5-way HEAD partition); HEAD vs prefix_category ratio >2× signals parametric. Observed per-dim L1 coefficient norms from full slot LogReg: TERM atom 17.62, suffix_first 15.28, prefix_cat 12.81, HEAD atom 12.33, e_depth 11.15. **HEAD is 4th of 5; HEAD/prefix_cat ratio = 0.96 (essentially equal, NOT >2× toward parametric). TERM and suffix dominate — exactly the CLOSURE features that define class membership per C1487 (terminal opacity three-tier taxonomy) and C1510 (suffix as parallel compositional domain).** Both pre-registered discriminators converge on sub-class refinement, away from parametric. **Crazy-expert accepted rejection in registration consultation:** "Both pre-registered diagnostics fired against me ... feature ranking with TERM > suffix_first > prefix_cat ≈ HEAD is the death blow for parametric: if HEAD were the opcode and other slots were operands, HEAD should dominate. It doesn't ... I lose." **Implication:** crazy-expert's PHASE_710 maximum-claim ("Voynich is microcode-like with parametric instructions") retracts one rung. Atoms have differentiated categorical signatures (DSL-like SHAPE per C2042) but do NOT parametrically modulate next-instruction selection (NOT DSL-like SEMANTICS). The shape-without-semantics framing is the new ceiling. **Mechanism inference "atoms function as opcodes with operand parameters" returns to Tier 4 SPECULATIVE.** Weakest survivable form (per crazy-expert): localized parametric semantics in specific frames (e→y per C1457, o-HEAD compositional determinism per C1556) — but these are already covered by existing constraints, not substrate-level claim. **C2042 atom-layer categorical signature unaffected** — that's about gloss categorization (operational role), independent of forward-predictive mechanism. **Tier 0 (closed-loop control programs) unaffected** — substrate framing survives, only specific mechanism inference falls. **Framework-as-null discipline validated:** crazy-expert's own pre-registered tests rejected crazy-expert's hypothesis. Per `feedback_expert_predictions_are_pre_registrations.md` and `feedback_framework_as_null.md`, this is the methodology working as designed. **Scope caveats:** (1) within-class test had small N per class with several degenerate "retention undefined" outcomes; "rejected by pre-registered diagnostics" not "FALSIFIED Tier 1" — save Tier 1 falsification for unambiguous well-powered discriminators (per expert-advisor scrutiny). (2) Feature importance interpretation depends on L2 regularization choice; ranking stable across reasonable C-values but exact magnitudes vary. (3) Sub-class refinement vs new architectural layer distinction: this is refinement WITHIN C121 partition, NOT a fourth architectural layer (no conflict with C1004).	2	mechanism_rejection, parametric_semantics, sub_class_refinement_wins, pre_registered_discriminators, framework_as_null_validation, methodology_discipline_working, C2042, C2043, C1004, C1003, C1024, C1487, C1510, C1475, C631, C506.b, feedback_expert_predictions_are_pre_registrations, feedback_framework_as_null
C2045	**C645 Sharpening: Substrate-Level Single-Step Post-Hazard Cooling Bigram (Class-Agnostic, No Continuation).** PHASE_714 5-axis refinement of C645. (a) **Multi-lag trajectory test:** post-hazard CHSH rate is 0.752 at lag +1, drops to 0.522 at lag +2 (within null distribution), 0.560 at lag +3, 0.521 at lag +4. Per-lag null distribution (1000 trials of random non-hazard tokens of matched count): ONLY lag +1 passes null p99=0.653; lag +2/+3/+4 are within random distribution. **Single-step decay; no sustained multi-step intervention.** (b) **Hazard-class specificity test:** hazard class 30 post-CHSH rate 76.6% vs class 7 rate 73.4%; spread 0.032 below 0.05 threshold; NOT class-specific. (c) **Triplet pattern test (hazard → CHSH → ?):** after hazard followed by CHSH, next EN is 50% CHSH / 50% QO — no continuation protocol; asymmetry -0.084 vs hazard→QO-then comparison. NO multi-step protocol. (d) **Folio-level consistency test:** 94.9% of 59 folios with ≥3 post-hazard EN events show CHSH > baseline rate 0.447; mean across-folio CHSH 0.775. (e) **Within-folio shuffle null (1000 perms, expert-advisor required before registration):** observed global rate 0.752 vs null p99 0.625, p_emp=0.0000; observed folio-fraction-above-baseline 94.9% vs null p99 84.8%, p_emp=0.0000; observed mean-across-folio rate 0.775 vs null p99 0.645, p_emp=0.0000. All three measures pass within-folio shuffle null at p<0.001 — effect is NOT composition shadow, substrate-level claim is valid per `feedback_within_folio_shuffle_null_first.md`. **Synthesis:** C645's post-hazard cooling-bias is real, substrate-level, single-step instruction-grammar bigram rule. The multi-step thermal-kinetic-architecture reading is NOT supported by refinement. Mechanism interpretation (thermal damage-control vs generic perturbation-recovery vs syntactic-only) is underdetermined within internal procedure per `feedback_mechanism_cycle_procedural_ceiling.md` — remains Tier 4 SPECULATIVE. **Refines C645's scope** (lag-1 specifically, not multi-step). **Does NOT conflict with C645** — directional fact stands; this constraint narrows interpretive extension. **References:** C645 (anchor), C109 (hazard topology, 5 hazard classes), C1487 (terminal opacity defining recovery direction), C521 (cohesion directionality).	2	post_hazard_recovery, single_step_bigram, substrate_level, folio_shuffle_null_pass, multi_lag_trajectory, class_agnostic, no_continuation, sharpening_of_C645, expert_consultation_split_registration, C645, C109, C1487, C521, feedback_within_folio_shuffle_null_first, feedback_post_hoc_claim_substitution
C2046	**No Pre-Hazard QO/Heating Buildup (Hazards Not Precipitated by Heating Excursion).** PHASE_714 Refinement 4 result: clean negative measurement falsifying "hazards are precipitated by cumulative heating" interpretation. For each hazard token in Currier B, measure QO/CHSH distribution at lag -1, -2, -3 EN-positions BEFORE the hazard. Thermal-overshoot prediction: elevated QO (heating buildup) at lag -1 to -2 before hazard. **Observed:** QO rate at lag -1 = 42.3%, lag -2 = 41.2%, lag -3 = 43.0%. All BELOW baseline QO rate 44.7% — by -0.024, -0.035, -0.017 respectively. There is NO heating buildup before hazards; if anything, CHSH (cooling) is mildly elevated in pre-hazard contexts. **Crazy-expert interpretation (Tier 4 SPECULATIVE only):** hazards occur during sustained CHSH-dominant contexts ("stabilization failure" rather than "thermal overshoot"). System is already in CHSH/cooling mode when hazard event triggers; the failure is INSIDE the absorbing well (e-stabilizer capacity), not from heating excursion. **Implications for thermal interpretation:** falsifies the specific "hazards arise from accumulated heating" reading. The hazard event class per C109 (5 hazard categories) includes ENERGY_OVERSHOOT (1 of 5), but the observable token-grammar signature is not consistent with energy-overshoot dominance. Hazards are more compatible with composition/timing/phase events than thermal overshoot. **References:** C645 (post-hazard recovery direction), C109 (hazard taxonomy 5 classes), C2045 (PHASE_714 companion sharpening), C105 (stability anchor — possible mechanism for "stabilization failure" reading), C521 (one-way absorption directionality), F-B-008/F-B-009 (two-channel thermal, overshoot-correct cycling — both flagged for review per crazy-expert; the multi-step overshoot-cycling mechanism is not supported by R4 negative). **Scope caveats:** (1) Negative measurement only — does NOT prove thermal interpretation is wrong, only that the specific "heating buildup → overshoot → cooling recovery" mechanism inference is not supported. (2) The 5 hazard classes per C109 are NOT individually mapped to physical hazard categories at the token level; PHASE_714 cannot test which hazard category dominates. (3) Pre-hazard window may not capture all relevant context if hazards are non-locally triggered. (4) "No QO buildup" does not exclude other excitation modes (other heating signatures not measured here).	2	pre_hazard_signature, negative_measurement, no_QO_buildup, falsifies_thermal_overshoot_mechanism, stabilization_failure_candidate_tier4, multi_step_thermal_protocol_falsified, C645, C2045, C109, C105, C521, F-B-008, F-B-009
C2047	**Substrate Has Heterogeneous Directional Depth (5-Anchor Cross-Refinement).** PHASE_715 applied PHASE_714 methodology (multi-lag trajectory, folio consistency, within-folio shuffle null, per-lag null distribution) to 5 directional anchors. **Results:** A0 hazard→CHSH: lag+1 obs 0.221 vs null p99 0.219 (marginal pass), lag+2 obs 0.152 fails null — SINGLE-STEP. A1a h-TERM→MIDDLE[0]=p: lag+1 obs 0.022 vs null p99 0.015, lag+2 obs 0.018 PASSES null p99 0.015 — MULTI-STEP (note: low absolute magnitudes, A1a borderline-stable, A1b is primary evidence). A1b r-TERM→MIDDLE[0]=a: lag+1 obs 0.320 vs null p99 0.145, lag+2 obs 0.187 PASSES null p99 0.164, lag+3 obs 0.181 barely passes 0.176 — MULTI-STEP. A2 qo-k→ok-e: lag+1 obs 0.042 vs null p99 0.037 (marginal), lag+2 fails — SINGLE-STEP. A3 ar→al: lag+1 obs 0.069 vs null p99 0.041, lag+2 fails — SINGLE-STEP. **All 5 anchors pass within-folio shuffle null at p<0.001 at lag+1; effects are substrate-level not folio-composition.** **Cross-anchor verdict:** 3 single-step + 2 multi-step = HETEROGENEOUS DEPTH. Substrate is NOT uniformly bigram-rule. **C2045's scope narrowed:** its "substrate-level single-step" framing applied only to hazard recovery anchor; cross-anchor refinement shows different operational domains have different depths. **Methodology fix:** A1a originally tested `head_atom == 'p'` predicate but 'p' is MOD atom not HEAD atom (HEAD = 'aeokt'), so target was always False. Corrected to `MIDDLE[0] == 'p'` first-character predicate regardless of role classification. After fix, A1a multi-step finding independently confirms A1b. **Scope caveats:** (1) A1a borderline-stable; A1b is primary evidence for multi-step pattern. Recommend A1a re-run with 5000-iter shuffle for robustness if leaning hard on this result. (2) No NL Latin floor check run on heterogeneous-depth claim — expert-advisor flagged this as optional but high-value strengthening. (3) Mechanism interpretation ("two-tier grammar architecture") stays Tier 3-4 per `feedback_mechanism_cycle_procedural_ceiling.md`. (4) The 5 anchors are not exhaustive; other directional patterns may show different depths not tested here. **References:** C2045 (scope-narrowing relationship), C645, C1212, C1314, C2041, C1019 (tensor rank-8 pairwise structure as already-present framework support), C1379 (two-level parallel composition).	2	cross_anchor_refinement, heterogeneous_depth, multi_step_substrate, single_step_substrate, within_folio_shuffle_null_pass, methodology_fix_documented, C2045_scope_narrowed, C645, C1212, C1314, C2041, C1019, C1379, feedback_mechanism_cycle_procedural_ceiling
C2048	**C1212-Type Cross-Token TERM→MIDDLE[0] Chaining Shows Multi-Step Substrate Dependency.** PHASE_715 A1a + A1b results. C1212's z=20.3 cross-token sequential signal (TERMINAL→INITIAL chaining) was previously characterized at bigram-level. PHASE_715 extends: the dependency is MULTI-STEP, not just adjacent-token. **Two independent predicates:** (a) **r-TERM → MIDDLE[0]=a**: baseline 0.133, lag+1 0.320 (2.41× baseline), lag+2 0.187 (1.41× baseline, passes null p99 0.164), lag+3 0.181 (1.36× baseline, barely passes null p99 0.176), lag+4 0.184 (close to baseline). Within-folio shuffle null: observed 0.320 vs null p99 0.175, p_empirical=0.000. (b) **h-TERM → MIDDLE[0]=p**: baseline 0.009, lag+1 0.022 (2.45× baseline), lag+2 0.018 (2.00× baseline, passes null p99 0.015), lag+3 0.018 (2.00×, marginal). Within-folio shuffle null: observed 0.022 vs null p99 0.015, p_emp=0.000. **A1a magnitude caveat:** absolute rates are small (0.022 lag+1) and null p99 (0.015) is close — borderline-stability concern. A1b is the cleaner separation; A1a provides independent confirmation of the multi-step pattern but absolute effect size is in noise-floor territory. **Layer distinction:** C2048 operates at atom-character composition layer (C1394 HEAD+MOD*+TERM atom positions), INDEPENDENT of C109's class-layer forbidden transitions (49 instruction class taxonomy). The multi-step chaining is at the atom level within MIDDLE positions, not at the class-level transitions. **Predicate semantics:** target predicate is `MIDDLE[0] == X` (first character of MIDDLE field after PREFIX stripped, regardless of whether X is HEAD atom 'aeokt', MOD atom 'pficds', or TERM atom — operates purely on first-character match). This is structurally cleaner than role-classification predicate; documented for audit clarity. **Refines C1212:** the strongest sequential signal in project has multi-step depth extending 2-3 positions beyond immediate adjacency, not just bigram-level. Mechanism interpretation ("compositional carry-over," "instruction-packet 2-3-gram") remains Tier 3 framing. **Scope caveats:** (1) Tested two TERM→MIDDLE[0] predicate pairs; other TERM-atom or MIDDLE[0]-atom combinations not yet characterized. (2) Multi-step magnitude attenuates with lag — describe as "lag+2 dependency with attenuation" not "persistent plateau through lag+3." (3) A1a borderline; A1b primary. (4) Mensural floor not applicable — TERM/MIDDLE compositional grammar (per C1394) is Voynich-specific structure with no clean cross-corpus analog. **References:** C1212, C1394 (HEAD+MOD*+TERM atom-position grammar), C2047 (companion cross-anchor result), C109 (layer-distinct: class-level forbidden transitions, NOT what C2048 measures), C1019 (tensor rank-8 pairwise structure), C1727 (line-ordering smoothness — possible mechanism candidate per crazy-expert PHASE_716 proposal).	2	C1212_refinement, cross_token_chaining, multi_step_dependency, atom_character_layer, MIDDLE_first_position, A1b_primary_A1a_replication, layer_distinct_from_C109, predicate_semantics_documented, mensural_skip_justified, C1212, C1394, C109, C1019, C1727
C2049	**C1212 Cross-Line Chaining is NOT the Mechanism for C1727 Line-Ordering Smoothness.** PHASE_716 main test. Crazy-expert hypothesis from PHASE_715 follow-up: multi-step C1212 chaining (TERM→MIDDLE[0] extending lag+2/+3 per C2048) propagates across line boundaries and produces line-ordering smoothness. Pre-registered discriminating test: if C1212 cross-line chaining IS the mechanism, excluding first 3 tokens of each line should COLLAPSE smoothness toward z=0 (≥80% magnitude collapse). **Result: OPPOSITE direction.** Excluding first 3 tokens INTENSIFIES smoothness +21.2% (z=-3.79→-4.59); excluding last 3 tokens also intensifies +8.6%; excluding both intensifies +23.7%. The line-boundary tokens (first 3, last 3) add NOISE to line-level smoothness signal rather than contributing to it. Cross-line C1212 multi-step propagation FALSIFIED as mechanism. Implication: C1212/C2048 multi-step chaining is **line-INTERNAL**, not line-spanning. Lines are hard structural envelopes (consistent with C1429 cross-line independence MI=0.032 bits, C1470 cross-line hazard folio-mediated only, C964 boundary-constrained free-interior). **Crazy-expert accepted falsification in registration consultation:** "This isn't ambiguous — it's not 'weak signal,' it's anti-signal. Symmetric intensification kills the directional version too." Methodology validates per `feedback_expert_predictions_are_pre_registrations.md`: expert directional predictions ARE pre-registered tests. **Scope caveats:** (1) Reproduction discrepancy (folio-segmented z=-3.81 vs original C1727 z=-6.05 paragraph-segmented). Direction and pre-registered discriminator result hold despite magnitude attenuation. (2) Methodology error caught (paragraph-mean residualization mathematically invalid — constant shift identity; documented for audit clarity).	2	mechanism_falsification, C1212_NOT_mechanism, line_spanning_chaining_rejected, pre_registered_discriminator, boundary_tokens_add_noise, line_internal_not_line_spanning, C1212, C2048, C1727, C1429, C1470, C964, feedback_expert_predictions_are_pre_registrations
C2050	**Mode A/B Coherence is NOT the Mechanism for C1727 Line-Ordering Smoothness.** PHASE_716 mode-aware extension. User-suggested hypothesis: paragraphs are mode-coherent per C1423 mode persistence (2.89% CMI), so lines within paragraph tend to share mode, producing aggregate smoothness via mode-coherence. Three tests: (a) **Within-mode vs cross-mode pair distances:** A-A mean d²=11.27 (median 1.57), B-B mean=17.27 (median 4.29), A-B mean=10.69 (median 5.15), B-A mean=11.76 (median 5.18). Within-mode mean d²=14.07 vs cross-mode mean d²=11.23. **Ratio cross/within = 0.80** — cross-mode pairs are SMALLER than within-mode, OPPOSITE the mode-coherence prediction. (b) **Mode-residualization effect:** 0% (mathematically expected — constant shift identity; not informative). (c) **Mode-transition rate:** 40.4% of consecutive line pairs cross modes — paragraphs are NOT strongly mode-locked (transition rate would be ~5-10% if strongly coherent). **Mode coherence FALSIFIED as mechanism.** Mode is downstream of HEAD/TERM per C1341 (80% mode predicted by composition alone) — mode doesn't carry independent sequential structure. C2051 below shows the actual smoothness signal lives in HEAD+TERM JOINT coherence, not mode. **Scope caveats:** (1) Test (b) was mathematically invalid (constant per-paragraph shift); documented. The verdict is driven by tests (a) and (c). (2) Mode partition uses C1410 atom partition (Mode A = {d,e,ee,h,y}, Mode B = {a,i,ii,l,m,n,o,r,s}).	2	mode_NOT_mechanism, C1410_partition_test, cross_mode_pairs_NOT_larger_than_within_mode, mode_transition_rate_40pct, mode_is_downstream_of_HEAD_TERM, falsifies_user_proposed_hypothesis, C1410, C1423, C1341, C1727, C2049
C2051	**HEAD+TERM JOINT Coherence is the Localizable Signal for Line-Ordering Smoothness (Folio-Segmented).** PHASE_716 comprehensive search + expert-advisor blocking control validation. Of 12 schemes tested (ablations + subsets + residualizations), the smoothness signal is concentrated in HEAD+TERM JOINT features (13-dim subset: z=-7.76, baseline=-3.81). Individual HEAD-only (6 dims: z=-6.13) and TERM-only (7 dims: z=-6.31) are weaker than joint. Mode and length features DILUTE the signal at the aggregate level (no_mode z=-3.69, no_length z=-4.75 — removing length INTENSIFIES signal). **Critical artifact control (expert-advisor required):** Run shuffle null on 50 random feature subsets matched to each dimensionality. Random 13-feature subsets: mean z=-3.88, std 0.29; HEAD+TERM **rank 2% (more negative than 98%)** — REAL specific signal. Random 6-feature subsets: mean z=-4.55, std 1.17; HEAD-only rank 14% — MARGINAL above random. Random 7-feature subsets: mean z=-4.46, std 1.23; TERM-only rank 18% — MARGINAL. **Verdict:** the JOINT HEAD+TERM coherence is specific and survives dimensionality artifact control; the individual HEAD-only or TERM-only signals are only marginally above what random feature subsets produce. **Mechanism:** the signal is within-paragraph sequential variation in HEAD+TERM distributions jointly. Lines have correlated HEAD AND TERM profiles that vary gradually across paragraph beyond what within-paragraph shuffle predicts. **Mechanism interpretation remains Tier 3-4 SPECULATIVE** per `feedback_mechanism_cycle_procedural_ceiling.md`: possible readings include recipe progression, topic shift, narrative structure, but none distinguishable from internal data alone. **Scope caveats:** (1) Folio-as-paragraph segmentation: my z=-3.81 vs original C1727 z=-6.05. Direction consistent; magnitude attenuated. (2) HEAD+TERM joint signal is specific; individual HEAD-only and TERM-only signals are only marginally above dimensionality-matched random subsets. (3) Mechanism interpretation requires external grounding for promotion past Tier 3. (4) Baseline z stable across 3 seeds × 3000 shuffles (mean -3.811, std 0.052) — measurement is robust. **References:** C1727 (line-ordering smoothness anchor — this constraint narrows its mechanism), C2049+C2050 (companion falsifications), C1379 (two-level parallel composition framework support), C1003 (pairwise compositionality at token level), C1394 (HEAD+MOD*+TERM atom-position grammar).	2	mechanism_narrowing, HEAD_TERM_joint_coherence, dimensionality_artifact_control, baseline_robustness_passes, mode_and_length_dilute, scope_folio_segmented, mechanism_interpretation_tier_3, C1727, C2049, C2050, C1379, C1003, C1394, feedback_mechanism_cycle_procedural_ceiling
C2052	**8D Matcher Theophilus Negative Control FAILS: Matcher is Generic, Not Alchemy-Specific.** Pre-registered negative-control test (locked 2026-05-14 per `sources/theophilus/README.md`) executed for first time 2026-05-20 via existing script `_theophilus_negative_control.py`. Theophilus De Diversis Artibus (~1120 CE, metalwork/glass/pigments — NOT alchemy) tested. **Pre-registered failure criteria observed:** (C1) ≤2/30 confident matches — observed 4/30 (13.3%) AMBIGUOUS; (C2) mean ratio ≤1.10 — observed 0.878 PASS; (C3) permutation p ≥0.10 — observed **0.0000 FAIL**; (C4) Section B concentration <40% — observed **53.3% FAIL**. Script's overall verdict: "FAIL — matcher is generic; demote C1882-C1956 to structural-similarity." 30 Theophilus chapters → 32 REGIME_1 folios, mean distance 2.72, mean ratio 0.878. 16/30 Theophilus matches land on Voynich folios that are also on the original Pseudo-Lull match list (f84r, f77v, f75r, f76v, f76r, f81v, f75v, f77r, f81r, f80v, f83r, f82r, f78r). **Same folios attract both Codicillus AND Theophilus chapters at similar rates.** Permutation test: real mean ratio 0.878 vs random 0.612, p=0.0000 — Theophilus matches significantly above random in STRUCTURAL not OPERATIONAL way. **Pre-registered consequence (per README):** "demote C1882-C1956 from 'operational correspondence' to 'structural attraction to medieval procedural text generally.'" **Expert convergence:** (a) Accept falsification; methodology clean. (b) Do NOT blanket-demote 75 constraints; per-constraint triage required. (c) Triage criterion: content claims (specific PL chapter→folio correspondence, "Ch19=aqua vitae", Mercuriorum book mapping) → DEMOTE to Tier 3; structural claims (8D distance, alignment topology, feature-space geometry) → SURVIVE at Tier 2. (d) **Tier 0 unaffected** — "closed-loop control programs" framing is genre-structural; Theophilus is also closed-loop craft control. (e) C2032 substrate quintet, C2042 atom-monocategorical signature unaffected. (f) **Critical scope clarification:** what fails is the 8D MATCHER's domain-discriminative power. This does NOT refute the distillation/thermal interpretation broadly, which rests on multiple INDEPENDENT lines of evidence: **PWRE-1 structural narrowing** (specifically EXCLUDES Theophilus-type irreversible-transformation metalwork from controller's compatible physics class, leaving circulatory thermal conditioning / volatile extraction / circulatory reflux as candidates); **PHYS kernel dynamics** (k/h excitation → e stability, rapid recovery); **C1314 qo-k/ok-e thermal cycling** within-line bigram pattern; **C2042 atom-monocategorical operational signature**; **C645+C2045 hazard-recovery directional pattern**; **substrate quintet** non-NL discriminators. PWRE+matcher together imply the matcher's text features aren't physics-sensitive — they cluster by surface text properties regardless of underlying physical compatibility. The matcher's genericity REVEALS this measurement limitation; it does NOT refute the independent physics narrowing. **Pattern confirmation (8D-matcher-specific):** four failed mechanism interpretations this session (PHASE_711 parametric, PHASE_716 line-spanning + mode coherence, PHASE_718 matcher domain-specificity) + cumulative audit failures establish the "interpretation-overreach death zone" pattern as predictable for internal-only domain claims. Mechanism interpretations at "encodes X domain" level reliably die under discriminating tests; structural measurements survive. C171's semantic ceiling re-confirmed at the matcher level. **What this changes:** C1971 + C1882-C1956's 8D-matcher-based content-correspondence claims (e.g., "Voynich folio X has alchemical content matching Pseudo-Lull chapter Y") refined from "matcher demonstrates alchemy-specific correspondence" to "matcher demonstrates medieval-craft-procedural structural alignment; specific alchemical content interpretation requires non-matcher evidence." **What this does NOT change:** Tier 0; C2032 substrate quintet; C2042 atom-monocategorical signature; structural-measurement-level constraints in C1882-C1956; the 8D distance values themselves; **the distillation/thermal-circulatory interpretation broadly** (which rests on PWRE structural narrowing + PHYS dynamics + C1314 cycling + C2042 + substrate quintet, none touched by this test). **Action plan:** per-constraint audit of C1971 + C1882-C1956 family queued as future phase (PHASE_719 candidate). Each constraint gets explicit reasoning for SURVIVE vs DEMOTE per triage criterion. NOT blanket-batch update per `feedback_post_hoc_claim_substitution.md`. Expert estimate: ~15-25 of ~75 constraints actually need demotion; most are structural measurements that survive.	2	negative_control_FAIL, matcher_generic, matcher_domain_specificity_falsified, structural_attraction_survives, distillation_interpretation_broadly_NOT_refuted, PWRE_independent_evidence_survives, pre_registered_test, per_constraint_audit_queued, C1971_family_scope_refinement_matcher_only, Tier_0_unaffected, C2042_unaffected, C2032_unaffected, C1314_unaffected, PHYS_kernel_dynamics_unaffected, C645_C2045_unaffected, semantic_ceiling_reconfirmed_at_matcher_level, C1971, C1882-C1956, C171, C2032, C2042
C2053	**C2032 NL Latin Baseline Range Expanded From N=2 to N=4 — Voynich-vs-NL Discrimination Preserved But Narrower.** PHASE_720 v2 calibrated (15-80 length filter, matches canonical C2032 methodology per `phases/RECIPE_FOLIO_CORRESPONDENCE/scripts/_c2031_codicillus_cross_validation.py`). Calibration verification: Codicillus reproduces r21=-0.229 (canonical -0.22 within rounding). New corpora tested: **Rupescissa** (distillation/quintessence Latin, ~1351, 279 paragraphs / 11293 words) r21=+0.226 — monotonic same-sign decay, opposite of Codicillus despite same domain class; **Theophilus body** (metalwork/glass/pigments, ~1120, 144 paragraphs / 6364 words) r21=+0.495 — most positive of any tested Latin, monotonic. Combined with existing references (Codicillus -0.229, Mesue -0.17 per documented C2031 cross-validation), **NL Latin r21 spans -0.23 to +0.50 across four corpora**, substantially wider than C2032's original N=2 baseline range of -0.17 to -0.22 (Codicillus + Mesue only, both compact-formulaic-recipe Latin). **Voynich Section B at r21=-0.66 remains strongest period-2** across all tested corpora. **Discrimination magnitude affected:** the "engineered-substrate-vs-NL" gap per C2032 narrows from ~3× to nearest NL (Codicillus -0.229) to ~1.4× when broader Latin range is considered (closest NL still Codicillus at -0.229; Voynich -0.66 is 2.88× more negative). Direction (Voynich more period-2 than any tested NL) preserved. **Scope refinement to C2032:** the "NL Latin range -0.17 to -0.22" characterization in C2032's claim text was a generalization from N=2 compact-recipe Latin corpora. Broader Latin (theoretical/discursive like Rupescissa, descriptive like Theophilus) extends the range substantially. C2032's core finding (Voynich at -0.66 is non-NL) stands; the NL baseline characterization needs footnoting. **Why measurement-only registration:** expert-advisor noted that the four-data-point pattern (Codicillus + Voynich period-2 vs Rupescissa + Theophilus monotonic) admits a register-vs-domain interpretation (compact-formulaic-recipe register vs discursive register), but this is post-hoc N=4 framework-fit per `feedback_framework_as_null.md`. Registering the interpretation risks the trap pattern documented across mensural quartet (2026-05-16) and PHASE_711/716/718 mechanism falsifications this session. Register the measurement; defer interpretation to Tier 3 SPECULATIVE / future intra-corpus stratification test. **Methodology note:** PHASE_720 v1's calibration gap (r21=-0.007 vs canonical -0.22 at 20-50 filter) traced to length-filter parameter mismatch — canonical baseline uses 15-80, not 20-50. Documented in PHASE_721 investigation. **Refines C2032** — does not retract, does not falsify; refines the NL baseline characterization with expanded data. **Does not affect:** Tier 0, C2042 atom-monocategorical signature, PWRE-1 structural narrowing, PHYS kernel dynamics, C1314 thermal cycling, C645+C2045 hazard recovery — these are independent of the C2032 stem-class measurement. **Queued follow-up (not run):** intra-corpus stratification of Rupescissa to test whether recipe-dense segments show period-2 while theory-dense segments show monotonic — would discriminate register-tracking from other explanations of the cross-corpus pattern. **References:** C2032 (this constraint scope-refines its NL baseline characterization), C2031 cross-validation (canonical methodology source), Codicillus + Mesue + Rupescissa + Theophilus corpora, feedback_calibrate_thresholds_against_controls.md, feedback_framework_as_null.md.	2	C2032_scope_refinement, NL_baseline_expanded_from_N2_to_N4, calibrated_methodology, Codicillus_reproduces_canonical_minus_0_22, Rupescissa_opposite_sign_from_Codicillus, Theophilus_most_positive, Voynich_remains_strongest_period_2, register_vs_domain_interpretation_deferred_per_framework_as_null, measurement_only_no_interpretation, C2032, C2031, feedback_calibrate_thresholds_against_controls, feedback_framework_as_null
C2054	**Physics-Architectural Matcher Achieves Three-Class Discrimination Within Medieval Procedural Latin (Latin-Side Instrument Calibration).** PHASE_723 Phase 1-3. Hand-tuned distillation-vs-metalwork feature set designed from physics-architecture (apparatus markers like alembic/cucurbita/distillatorium vs incus/malleus/tenax; phase-transition operations like distill/sublim/condens/evapor vs fund/conflat/cud/trah; reversibility markers like revert/restaur/iter/circul vs solid-state markers durus/indurat/rigid; ambiguous terms like fornax/crucibulum/ignis/aqua/aurum EXCLUDED to prevent masking). Distillation_score and metalwork_score computed per paragraph (15-80 word filter); discrimination_score = distillation_score - metalwork_score. **Phase 1-2 (4/5 pre-registered criteria PASS):** Codicillus discrimination_score = +0.0152 (predicted positive, PASS); Theophilus body discrimination_score = -0.0052 (predicted negative, PASS); Codicillus-Theophilus gap = 0.0204 > 0.010 threshold PASS; Mann-Whitney p = 0.00000 (Codicillus vs Theophilus) PASS; Rupescissa = +0.0005 (predicted positive, FAILED — actually neutral). **Phase 3 (3/3 pre-registered criteria PASS):** full Pseudo-Lull Testamentum (~336 paragraphs, 13655 words via paragraph filter) discrimination_score = +0.0077 (positive distillation class) PASS; within 0.0075 of Codicillus subset (close to baseline) PASS; separates from Theophilus at Mann-Whitney p < 10⁻⁵ PASS. **Three-class discrimination structure emerged from data:** (1) operational distillation positive (Codicillus +0.0152, full Testamentum +0.0077; 11-14 distillation hits per 1000 words); (2) theoretical-alchemy/pharmacy neutral (Rupescissa +0.0005, Mesue -0.0004; ~1-2 marker hits per 1000 words); (3) metalwork negative (Theophilus -0.0052; 4.7 metalwork hits, 0.79 distillation hits per 1000 words). **Rupescissa's neutral result is interpretive refinement, not failure:** Rupescissa is theoretical-quintessence text (philosophical discussion ABOUT quintessence) vs Codicillus is operational-distillation manual (procedural recipes). The matcher discriminates OPERATIONAL distillation specifically, not distillation-as-content-domain. **Qualitative validation:** top operational-distillation paragraphs from full Testamentum are explicit distillation operations ("distilla aquam per alembicum in digestione", "claude cucurbitam cum suo coopertorio", "sublimationem mercurii"); bottom paragraphs are alchemical-stone-making with metalwork-style transformations ("balandina componitur ex argento viuo ferri", "calcedoneus componitur ex aqua terrea ferri ad indurandum"). **Important scope:** this is LATIN-SIDE instrument calibration ONLY. Demonstrates that physics-architecturally designed features can discriminate Latin texts cleanly where text-feature-density features (8D matcher per PHASE_718) cannot. **Does NOT yet say anything about Voynich.** Phase 4 Voynich-side mapping was proposed using C1314/C645+C2045/C2042 as analog features, BUT both experts independently identified this as framework-as-null trap (those constraints were DERIVED FROM Voynich substrate observations; using them as positive features for "Voynich is distillation" would be tautological per `feedback_framework_as_null.md`). Phase 4 blocked pending decoupled feature design (Voynich-side features defined a priori from external Latin features, NOT from existing Voynich constraints). **Important caveats:** (a) Codicillus complete_latin.txt appears to contain some English commentary mixed with Latin (qualitative check showed English paragraph at top score); prefix-stem matching catches both Latin and English distillation/metalwork keywords. Discrimination still works on Theophilus side; signal magnitude may be inflated by English. Documented but not invalidating. (b) The 13655-word Testamentum count is after 15-80 paragraph filter; full corpus is ~104k words (lots of content outside paragraph length filter). (c) Marker lists are hand-curated; may be incomplete or biased toward Codicillus-style vocabulary. (d) Phase 1-3 result is a LATIN-SIDE measurement; Voynich classification is NOT yet established. **What this changes:** demonstrates physics-architectural feature design CAN discriminate Latin domains where text-feature-density cannot. Refines PHASE_718's finding from "8D matcher is generic" to "8D matcher's specific text-feature-density approach is generic; physics-architectural feature design can discriminate at the same Latin-corpus level." Does NOT yet refute or confirm distillation interpretation of Voynich. **What this does NOT change:** Tier 0, C2032, C2042, PWRE-1 narrowing, PHYS dynamics, C1314, C645+C2045, C2052, C2053 — none touched by this Latin-side calibration. **References:** PHASE_718 / C2052 (matcher genericity problem this addresses); C2053 (calibrated NL baseline expansion); `feedback_framework_as_null.md` (Phase 4 block reasoning); `feedback_specific_vs_tautological_predictions.md` (verdict-discipline for any future Phase 4); `feedback_text_statistical_methods_generic_at_domain_level.md` (cumulative methodology lesson refined by this finding — physics-architectural features DO discriminate; text-feature-density doesn't).	2	physics_architectural_feature_design, three_class_discrimination_within_latin, operational_distillation_vs_theoretical_vs_metalwork, latin_side_instrument_calibration_only, Voynich_classification_NOT_established, Phase_4_blocked_on_framework_as_null, refines_PHASE_718_finding, hand_tuned_features_designed_from_physics, apparatus_phase_transition_reversibility_markers, ambiguous_terms_excluded, Rupescissa_neutral_interpretive_refinement, English_contamination_caveat, Codicillus, Pseudo_Lull_Testamentum, Theophilus, Mesue, Rupescissa
C2055	**Voynich Currier B is character-Markov at 5-gram order.** A character n-gram trained on Currier B reproduces every surface statistic measured today within sampling noise: TTR 0.231 vs real 0.212; hapax-types 64.5% vs 67.2%; hapax-tokens 14.9% vs 14.2%; Zipf slope -0.913 vs -0.930; top-100 coverage 42.6% vs 47.5%; cell-fill at 4-7 char range 70.4% vs 71.0%; distinct 2-char starts 141 vs 148. The 3-gram trained on same data **beats** the 4.8M-parameter transformer LM on bpc (1.95 vs 2.79, ratio 0.70) — character-level structure beyond trigram **degrades** prediction. Order ≥ 5 is the saturation point. **Consequences:** (a) the historical "Voynichese is too statistically weird to be language" framing inverts to "Voynichese is too statistically regular to be language" — it lacks the long-range structure NL requires. (b) Surface-statistics arguments for "designed slot grammar" are now floor-level: Markov chain noise reproduces all of them. (c) Combined with C2032 (lag2/lag1 = -0.66 cross-NL discriminator surviving Markov null at synthetic +0.22), C2015 (compression), C2022 (anti-NL char distribution), this is the **fourth axis of the engineered-substrate stack** — Voynich is locally-Markov-regular in a way no NL is. (d) Establishes 5-gram null as a methodological discipline for the project going forward. **Does NOT falsify:** NL-character-level falsification is strengthened. Architectural-tier claims that survived this null (C2032, correction-lane family C2056, atom monocategorical C2042) are sharpened by being above-Markov. **References:** C2015, C2022, C2032 (engineered-substrate companion axes); PHASE_691 markov_showdown.py (forgotten earlier result); new methodology memory `feedback_5gram_markov_null_for_surface_patterns.md`.	2	character_markov_5gram_match, surface_statistics_floor_level, transformer_loses_to_trigram, engineered_substrate_fourth_axis, NL_falsification_strengthened, methodological_discipline_for_future_constraints
C2056	**Post-Heat Polymorphic Correction-Lane Family (Architectural Unit Subsuming C1314).** After qo-k (heat addition) tokens, the immediately-following token shows above-Markov enrichment across multiple specific lanes — not a single bigram preference. Five lanes tested with 5-gram null trained on Currier B; all 5 show 17-30 percentage points of residual signal beyond local-character-statistics floor: (a) qo-k → ok (broad vessel correction): real +35.1% above shuffle null, synthetic +5.5%, **residual +29.6 pp**; (b) qo-k → ot (transfer): real +23.4%, synth -4.4%, **residual +27.8 pp**; (c) qo-k → ch (active monitor): real +36.3%, synth +12.2%, **residual +24.1 pp**; (d) qo-k → ok-e (cool-stabilize, narrow C1314): real +41.3%, synth +18.1%, **residual +23.3 pp**; (e) qo-k → sh (passive monitor): real +4.7%, synth -12.3%, **residual +17.0 pp**. Broader qo → ch (any qo prefix) gives **residual +25.0 pp**. Negative control qo → sh (broad) gives +8.2 pp (weakest signal in family). **Interpretive shift:** C1314 narrow form (qo-k → ok-e specifically, registered Tier 2 2026-02-25) measured one branch of a much wider polymorphic correction pattern. The architectural unit is not the individual bigram but the **correction window** following thermal initiation: real text routes through any of {ok, ot, ch, sh, ok-e} with consistent above-Markov probability while a character 5-gram routes uniformly. Maps directly to thermal-process control: heat → {vessel adjust, transfer, active test, passive watch, cool stabilize}. **Supersedes C1314 (narrow form) and references C1313, C645, C2045, C929** as predecessor measurements within the same architectural unit. The narrow constraints are preserved as historical scope; C2056 is the consolidated architectural-level claim. **Crucial distinction from C1727 and C645+C2045 demotion (this same phase):** the 17-30 pp residuals here represent genuine above-Markov structure; C1727 (line-ordering smoothness residual ~0) and C645+C2045 (post-hazard CHSH residual +2.3 pp) are Markov-reproducible. The correction-lane family is what real structural signal looks like vs surface-statistic floor. **Falsifiability:** would be falsified if any of the 5 lanes drops to <5 pp residual under improved-methodology re-test; or if the family-level enrichment is reproduced by a properly-calibrated 5-gram trained on a non-Voynich procedural corpus. **References:** C1314 (predecessor; narrow form), C1313 (two-channel atom separation), C929 (ch=active, sh=passive monitoring), C645+C2045 (now demoted; hazard recovery), C2055 (5-gram methodology).	2	correction_lane_family, post_heat_polymorphic_response, supersedes_C1314_narrow_form, five_lanes_17_to_30_pp_residual, architectural_unit_not_individual_bigram, thermal_control_loop_signature, survives_5gram_null, distinguishes_from_C1727_C645_demotion, B, B_grammar, thermal_control
C2057	**Currier A RI linker topology is structural-only — no atom-level semantic content.** Extending C835 (4 linkers / 12 edges with non-random topology vs degree-preserving null), an atom-specificity battery on the linker MIDDLEs returns 0/5 PASS: linker-bearing tokens do not concentrate any specific atom signature relative to controls. Linker topology H1+H5 PASS (non-random connection pattern survives); linker content H2/H3/H4 all FAIL. Linkers mark structural connections without carrying semantic content. Consistent with C171 (semantic ceiling) and C233 (LINE_ATOMIC) — content-empty linkers don't violate non-sequentiality. **References:** C835 (predecessor), C171, C233.	2	linker_topology_real, linker_content_empty, A_RI, atom_specificity_zero_of_five, refines_C835
C2058	**Currier A o-HEAD ("arrange") rate does NOT track plant-illustration morphological complexity.** Pre-registered, locked before running: if o-HEAD vocabulary encodes botanical spatial structure, herbal folios with more-complex plant illustrations should have higher o-HEAD rate. N=29 Currier A herbal folios with PIAA blind "Key Features" morphological scoring. Raw Spearman ρ(complexity, o-rate) = +0.031, p=0.87. Token-count confound: ρ(tokens, o-rate)=+0.41, p=0.027. **Partial correlation controlling for token count: ρ=-0.057, p=0.77.** Falsifies "o-HEAD arrangement vocabulary describes plant visual structure" via this specific proxy. **Scope of falsification:** spatial-complexity-via-morphological-tag-count proxy. Does NOT falsify botanical-category-coded, use-coded, or any non-spatial interpretation. Extends manuscript-wide pattern (C138/C140) — Voynich text does not describe its illustrations; the arrangement vocabulary is operational, not depictive. **References:** C138, C140, C1388, C1502, C1559.	2	falsification, A_o_HEAD_not_botanical_proxy, scope_limited_to_spatial_complexity, partial_correlation_controlled, extends_C138_C140
C2059	**Currier A Section P recovers a thermal HEAD-domain profile (B-like) inside A.** Section-stratified HEAD distribution across Currier A: Section H (herbal) o=26.2%, e=10.9%, k=4.6%, a=5.8% — arrangement-dominant; Section P (pharma) o=21.1%, **e=28.0%**, k=8.1%, a=6.4% — thermal-recovery (e-dominant, like Currier B's 40.4% e-HEAD); Section T (text) o=20.6%, e=13.4%, k=8.8%, a=21.7% — yield+arrange co-dominant. The Section P thermal-recovery is not articulated by C1266 (which used atom-cluster framing); this finding sharpens C1266 at HEAD-domain resolution. **Interpretive scope:** structural measurement only. Operational reading ("P is A's pharma-execution sub-context") is framework-echo-suspect and held to Tier 4 SPECULATIVE pending independent discriminating evidence. **References:** C1266 (predecessor), C1559 (cross-system HEAD gradient), C1502 (AZC arrangement domain).	3	section_HEAD_domain_split_within_A, section_P_thermal_recovery, refines_C1266_at_HEAD_resolution, operational_interpretation_held_to_Tier_4
C2060	**The C109 5-class hazard taxonomy was imposed by keyword-matching, not discovered by clustering.** Source `phase18_failure_typology.py` hardcodes 5 distillation-failure-mode classes + keyword lists (lines 61-87); the 17 forbidden transitions are sorted by substring keyword match (lines 392-411). No clustering produced 5 — the only clustering in the phase 15-20 chain produced 1 cluster (phase15a internal_clusters=1); phase 16 had a different 12-mode scheme. C109's stated evidence "Cluster analysis reveals 5 natural groupings" is FALSE about its method. Empirical clustering of the 17 transitions by atom territory (src/tgt HEAD+TERM): silhouette-optimal k=8 (0.479); k=3 (0.400) ≥ k=5 (0.372) — **5 is not data-preferred**; natural-vs-imposed ARI=0.42 (weak match). Only **PHASE_ORDERING is a tight gloss-coherent cluster** (=C1529 sealed/y-terminal → iteration/a-HEAD); CONTAINMENT_TIMING barely cohesive (0.218 vs random 0.224); RATE_MISMATCH + ENERGY_OVERSHOOT are singletons. **Gloss-coherence check:** ENERGY_OVERSHOOT ("scorching/heat") is CONTRADICTED — its sole member `he→t` contains no k-HEAD heat atom (`he`=watch.cool per C1394; consistent with C1448 k-HEAD hazard immunity); RATE_MISMATCH ("flow") and COMPOSITION_JUMP ("purification") have no supporting atoms; PHASE_ORDERING supports only a generic sequencing reading, not "vapor lock." The real atom-territory structure is independently and more rigorously held by C1528-C1533. **Caveat:** imposed-partition cohesion z=−4.10 vs 2000 random partitions is near-circular (keyword lists encode atom-family intuitions) and is NOT evidence for the 5-class count. **Disposition:** C109 revised to existence-only; 5-class taxonomy → Tier 3-4 interpretive labeling; ENERGY_OVERSHOOT/RATE_MISMATCH labels not gloss-supported; C216 demoted (71/29 split over imposed partition). Tier 0 untouched (frozen conclusion never depended on the taxonomy).	2	imposed_taxonomy, false_method_claim, hazard_classes, k5_not_data_preferred, PHASE_ORDERING_only_real_cluster, ENERGY_OVERSHOOT_gloss_contradicted, atom_structure_held_by_C1528, provenance_audit, PHASE_732
C2061	**Macro-state eigenstructure of the Currier B class-transition operator survives the 5-gram null (vindicates C976-C978).** The second eigenvalue λ2 of the raw 49×49 class transition matrix (the clean measure of macro-state slow-mixing structure; bypasses the C976 merge's hardcoded role/depletion constraints) is genuinely above-Markov: real λ2=0.2063, 5-gram-synth λ2=0.1194±0.017 sitting at the within-line-shuffle floor 0.1176±0.009 (5-gram only 2% of the way from floor to real). Per-synth-own-shuffle symmetry control: real λ2 excess +0.0873 vs 5-gram synth excess +0.0517±0.014, **z=+2.51, p=0.000** — real significantly exceeds synth under the SAME metric where scalar-MI was reproduced. The 5-gram reproduces ~60% of the λ2 excess (partly morphology-derivable) but the remaining ~40% is above-Markov. The macro-automaton (C976-C978/C1010) faced the sharpest null it has ever been tested against and passed at the eigenstructure level. **SCOPE: validates above-Markov macro-structure in the raw 49-class transition operator — NOT a re-derivation of C978's 6-state 0.894 spectral gap (a different operator on the merged 6×6 matrix, not re-measured here).** Partition-ARI through the C976 merge was confounded (role/depletion constraints force ARI 0.67-0.80 even for structureless nulls: random 0.669, shuffle 0.804, real 0.937, 5-gram 0.762) and is uninformative; λ2 of the raw matrix is the uncontaminated metric. **References:** C976, C977, C978, C1010, C2023, C2055, C2056, C549, C562.	2	macro_eigenstructure_survives_5gram, lambda2_above_markov, vindicates_C976_C978, scoped_to_raw49_operator_not_C978_gap, partition_ARI_confounded_by_merge_constraints, per_synth_own_shuffle_symmetry, B
C2062	**Three-axis decomposition of Currier B class-sequential structure.** The class-layer sequential signal splits into three components with distinct 5-gram-null verdicts: (a) **local control bigrams** (specific token transitions, e.g. qo→ch/sh) — REAL above-Markov; (b) **macro-state eigenstructure** (λ2 of the 49-class operator) — REAL above-Markov; (c) **aggregate scalar first-order class-MI** (C2023) — the floor-dominated MIDDLE layer, morphology-reproducible. The genuine above-Markov grammar lives in the local bigrams and the macro-eigenstructure; the aggregate scalar one-step MI is reproducible from local character statistics because it is dominated by the high-mass local bigrams and conflates them with the morphology-derivable bulk. This explains why a character 5-gram (which reproduces all surface statistics, C2055) reproduces the scalar class-MI but not the macro-eigenstructure: scalar MI is a high-mass-dominated lumped functional, λ2 is a global community-structure functional. **References:** C2023 (demoted middle layer), C2061 (eigenstructure), C549/C562 (local bigrams), C2055 (5-gram surface reproduction), C2056.	2	three_axis_decomposition, local_bigrams_real, macro_eigenstructure_real, scalar_MI_morphology_shadow, scalar_vs_eigenstructure_distinction, B
C2063	**C1025 battery's B3 forbidden-suppression test is an idealization-conformance test, not a fidelity test.** B3 scores `forbidden violations == 0`. The REAL Currier B corpus has 13 forbidden violations (the ~0.7% leakage; C1360 ~0.05% realized rate, C789 permeability). M2 produces 0 by hard bidirectional suppression → passes B3. A character-5-gram produces 12.8 ≈ real's 13 → fails B3. **So M2 passes B3 by being LESS faithful to the real corpus than the 5-gram is** — B3 rewards over-idealization. This is the 4th C1025-battery test-spec correction (cf. C1030/C1033/C1034), of INVERSE polarity: those were too strict on the model, B3 is too lenient on the over-idealized model. Consequence for C1025: M2's advertised +0.1-test edge over M1 was concentrated in B3 (idealization) and B5 (which M2 actually fails); **M1 (pure 49-class Markov, no forbidden suppression) is the corpus-fidelity frontier**, and the macro-automaton topology lives in the class-Markov matrix itself — forbidden suppression is a thin idealizing overlay (consistent with C622 0.12% buffer rate, C997 sparse-critical-buffer, C1023 PREFIX-routing sole load-bearing macro component), not load-bearing for the topology. Consistent with C2060 (forbidden pairs real-but-Markov-reproducible-as-rare-events). **References:** C1025, C1030, C1033, C1034, C1360, C789, C2060, C622, C997, C1023.	2	B3_idealization_not_fidelity, M2_over_suppresses, 5gram_more_faithful_than_M2, M1_is_corpus_fidelity_frontier, forbidden_thin_overlay, fourth_C1025_battery_test_spec_correction_inverse_polarity, B
C2064	**daiin→ch/sh-prefix bigram is above the 5-gram floor — measurement-only, mechanism ambiguous.** Under per-synth-own-shuffle 5-gram null, the unconditional daiin→(ch/sh-prefix) transition tendency has real excess +0.2272 vs synth +0.1297. This is a genuine above-Markov bigram, grouped with C549 and the C2056 correction-lane family. **TWO load-bearing caveats keep it measurement-only:** (1) DENOMINATOR — this is the UNCONDITIONAL prefix-transition rate (47.9%), NOT C817's lane-conditional 90.8% (of next-tokens in QO∪CHSH, share that is CHSH); the lane-conditional magnitude is UNTESTED. (2) MECHANISM AMBIGUOUS — daiin→CHSH survives but the parallel ol→CHSH demotes despite similar real rates; this daiin-survives/ol-demotes asymmetry is exactly what a token-length/char-signature artifact predicts (daiin is a long fixed token the 5-gram routes past poorly, like qo; ol is short and char-reproducible). So the survival may be "char-5-gram cannot route past long tokens," NOT "CC lane-routing is designed structure." **Does NOT validate C600/C817's routing-mechanism claim** (both demoted). Discriminating test (pre-registered, future work): test ≥2 SHORT char-reproducible CHSH-source tokens — if they survive, general lane-attraction is real; if not, char-signature artifact. Extends C2062 (local control bigrams real, positional gradients floor). **References:** C549, C2056, C2062, C600, C817, C816.	2	daiin_chsh_bigram_above_5gram, measurement_only, mechanism_ambiguous_tokenlength_vs_routing, unconditional_not_lane_conditional, does_not_validate_C600_C817, discriminating_test_short_source_future, extends_C2062, B
C2065	**The Currier B macro-eigenstructure slow mode (C2061's above-Markov λ2) is DISTRIBUTED across the class space, NOT localized in the AXM attractor self-loop.** Submatrix-λ2 localization: full-49 λ2=0.236, AXM-block-only 0.222, non-AXM lanes 0.205 — comparable across attractor and lanes, not attractor-concentrated. 2nd-eigenvector loading (falsification test): AXM-block loading 0.642 ≈ class-fraction 0.65 (proportional, not concentrated); participation ratio 28.8/49; top-5 share 0.299; top loaders mix AXM (22,21,2,8,41) and lane (7,23,9) classes — spread, not block-boundary-aligned. The "distributed" claim SURVIVED its falsification (a concentrated within-AXM gradient would have collapsed it and predicted high spectral ARI). **Mechanistically grounds C1010's non-spectral 6-state partition (spectral-clustering ARI=0.059):** the role/depletion-defined partition cannot be spectrally recovered because the above-Markov slow mode genuinely does not align with the blocks. Companion to the PHASE_736 non-finding that the AXM self-transition RATE is composition (the C2062 scalar-vs-eigenstructure split, recurring at the block level). **References:** C2061 (above-Markov λ2, localized here), C1010 (non-spectral partition, grounded), C1019 (tensor-orthogonality), C978 (scope-corrected), C2062 (scalar-vs-eigenstructure), C976.	2	macro_slow_mode_distributed, not_in_attractor_self_loop, participation_ratio_28.8, loading_class_proportional, not_block_aligned, grounds_C1010_nonspectral_partition, falsification_survived, B

---

# All Explanatory Fits

# FIT_TABLE.txt - Programmatic Fit Index
# WARNING: No entry in this file constrains the model.
# Generated: 2026-05-28
# Total: 75 fits
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
F-B-001	LINK Operator as Sustained Monitoring Interval	F2	B	SUPERSEDED	C366, C609, C190 | **Superseded by:** C1174	in: fits_currier_b
F-B-002	QO Lane as Safe Energy Pathway	F3	B	SUCCESS	C601, C574, C600	in: fits_currier_b
F-B-003	Pre-Operational Configuration via A→AZC→B Pipeline	F2	B	SUCCESS	C473, C506, C468	in: fits_currier_b
F-B-004	Lane Hysteresis Control Model	F2	B	SUCCESS	C643, C549, C577, C608	in: fits_currier_b
F-B-005	PP-Lane MIDDLE Discrimination	F2	B	SUCCESS	C646, C576, C642	in: fits_currier_b
F-B-006	Energy/Stabilization Lane Assignment	F3	B	PARTIAL	C647, C645, C601, C521	in: fits_currier_b
F-B-007	Extensible Atom Scaling: Intensity and Duration Dimensions	F3	B	CONSISTENT	C1197, C1204, C1205, C1242, C1244	in: fits_currier_b
F-B-008	Two-Channel Thermal Architecture	F3	B	SUCCESS	C647, C601, C1207	in: fits_currier_b
F-B-009	Overshoot-Correct Cycling	F3	B	SUCCESS	C643, C647	in: fits_currier_b
F-B-010	REGIME Token Profile Discrimination	F3	B	SUCCESS	C643, REGIME system	in: fits_currier_b
F-B-012	E-Compound Cooling Taxonomy	F4	B	SUCCESS	C1197, REGIME system	in: fits_currier_b
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
F-BRU-031	Modern Distillation Dimensional Comparison	F3	B	MODERN_CLOSER_TO_VOYNICH	F-BRU-030 (MIDPROCESS absence characterization), C1056 (MIDPROCESS structural absence)	in: fits_brunschwig
F-BRU-032	KE-Family Parametric Differentiation	F2	B	PARAMETRIC_DIFFERENTIATION	C1225 (E-depth Suffix Parametricity), C1226 (ke/ek Ratio Process Conditioning)	in: fits_brunschwig
F-BRU-033	Iterative Extraction Cycling Within Paragraphs	F3	B	ITERATIVE_CYCLING_SUPPORTED	C1227 (FL cross-line reset clustering), C1228 (PREFIX channel switching), C1229 (alternating suffix modes)	in: fits_brunschwig
F-BRU-034	Extraction Cycling Mode Differentiation	F3	B	CYCLING_MODES_FUNCTIONALLY_GROUNDED	C1230 (Mode MIDDLE differentiation), C1231 (Universal suffix modes), C1232 (Tail product signatures)	in: fits_brunschwig
F-RUP-001	Galenic Framework Directional Enhancement	F4	B	DIRECTIONAL_COHERENCE	C109 (Hazard Classes), C121 (49 Instruction Classes), C475 (MIDDLE Incompatibility), C494 (REGIME_4 Precision Axis), C458 (Design Asymmetry), C911 (PREFIX-MIDDLE Compatibility), C995 (Affordance Bins), C997 (Safety Buffers), C1053 (Compound Atom C475 Mediation)	in: fits_rupescissa

---

# Tier 3-4 Interpretations

# Speculative Interpretation Summary

**Status:** SPECULATIVE | **Tier:** 3-4 | **Version:** 4.73

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


## Architectural Layering: Finite-Grammar vs. Special-Case Notation

- Token morphology (HEAD+MOD*+TERM atom architecture, C1394)
- Forbidden transitions (5 hazard classes, C789)
- Block-level paragraph specialization (C1961)
- Within-line interleaving (C1964)


- Cycle-counting idiom on f75r (C1965) — used for operationally-non-derivable iteration counts; does not generalize because most recipes don't need it



**What this means for interpretation:**



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




| Suffix | Kernel | Gloss | Tokens | Compositional Reading |
|--------|--------|-------|--------|-----------------------|
| `-y`   | null   | "end" | 458 | bare close |
| `-ey`  | E      | "set" | 769 | e-kernel stabilizing close |









> **TIER 4 QUARANTINE:** The following etymology/gloss candidates are speculative external-language mappings. Do NOT use these for structural answers. Use only when the user explicitly asks about etymology or external-language alignment. Structural role is determined by grammar position (C121), not word meaning (C171, C120).

| Kernel | Function | Abbreviation | Meaning | Confidence |
|--------|----------|-------------|---------|------------|
| **K** | ENERGY_DRIVER | **K**ochen (Ger.) | to boil/cook | Strong |
| **E** | STABILITY_ANCHOR | **E**rkalten (Ger.) | to cool down | Strong |



> **TIER 4 QUARANTINE:** The following etymology/gloss candidates are speculative external-language mappings. Do NOT use these for structural answers. Use only when the user explicitly asks about etymology or external-language alignment. Structural role is determined by grammar position (C121), not word meaning (C171, C120).

| Element | Position | Abbreviation | Meaning | Confidence |
|---------|----------|-------------|---------|------------|
| **qo** | PREFIX (energy channel) | **Co**quo (Lat.) | I boil/cook | Strong |
| **op** | PREFIX | **Op**erare (Lat.) | to operate/work | Moderate |



> **TIER 4 QUARANTINE:** The following etymology/gloss candidates are speculative external-language mappings. Do NOT use these for structural answers. Use only when the user explicitly asks about etymology or external-language alignment. Structural role is determined by grammar position (C121), not word meaning (C171, C120).

| Consonant | Our Gloss | German Candidate | Meaning | Confidence |
|-----------|-----------|-----------------|---------|------------|
| **d** | "seal" (END-class, C919) | **D**ichten | to seal/make tight | Moderate |
| **t** | "transfer" | **T**reiben | to drive; also *abtreiben* = to drive off volatiles | Moderate |


| Element | Position | Candidate | Meaning | Confidence |
|---------|----------|-----------|---------|------------|
| **l** | SUFFIX/MIDDLE | **L**etzt (last) or **L**assen (to let) | last; to allow/release | Weak |
| **p** | SUFFIX | **P**ause | pause/rest | Weak |








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


## 0.C.1. MIDDLE ATOM BEHAVIORAL COMPOSITION (COMPOUND_DECOMPOSITION + CROSSWORD_GLOSS_VALIDATION Phases)
### Tier 2: Statistical Foundation (C1190, C1191)

> **Single-character MIDDLEs are genuine behavioral atoms. Compound MIDDLEs inherit behavioral profiles by additive composition of their component atoms. Permutation test: r=0.754, z=3.32, p<0.001, 0/1000 permutations beating real assignment.**

> **Additive composition is MIDDLE-specific (C1190 scope correction, Phase 422). PREFIX compounds show emergent behavior — atoms c, h, s, p acquire specialized profiles in PREFIX position that exceed simple addition (C1191). SUFFIX position imposes a systematic behavioral shift on all atoms (pairwise shift correlation r=0.892). Atoms maintain consistent IDENTITY across positions (15/18 CONSISTENT) but follow position-specific COMPOSITIONAL RULES (C1191).**

This finding provides behavioral validation of Section 0.C's three-layer architecture. The construction layer isn't just string manipulation — the atoms being constructed with carry genuine functional signatures that compose additively in MIDDLE position, while PREFIX and SUFFIX positions apply distinct compositional rules.

| Variant | Real r | Perm r | Z | p |
|---------|--------|--------|---|---|
| All features (incl kernel) | 0.711 | 0.478 | 5.04 | <0.001 |
| **No kernel (circularity-free)** | **0.754** | **0.605** | **3.32** | **<0.001** |

### Tier 3: Compositional Gloss Families

The following atom composition patterns are consistent across all compound appearances. Glosses derived from independent behavioral analysis (MIDDLE_SEMANTIC_MAPPING phase), NOT from decomposition.

**The y-terminal family (6/6 compounds fit):**

y = "end" (458 tokens standalone). Every -y compound is a type of ending:

| Compound | Decomposition | Gloss | Fit |
|----------|--------------|-------|-----|
| ey | cool + end | "set" (cooling done) | Strong |
| dy | mark + end | "seal" | Strong |
| hy | watch + end | "confirm" | Strong |
| ly | late + end | "end" | Strong |
| ry | mid + end | "finish" | Strong |
| eey | cool + cool + end | "deep" | Strong |

**The i+n intake/iterate family (6/6 compounds fit):**

If i = "cycle/iterate" and n = "bind/connect":

| Compound | Decomposition | Gloss | Fit |
|----------|--------------|-------|-----|
| ii | cycle + cycle | "repeat" | Strong |
| in | cycle + bind | "link" | Strong |
| iin | cycle + cycle + bind | "iterate" | Strong |
| ain | into + cycle + bind | "intake" | Strong |
| aiin | into + cycle + cycle + bind | "settle" | Strong |
| oiin | vessel + cycle + cycle + bind | "loop" | Strong |

**Order-sensitive kernel compounds (Tier 2 atoms only):**

| Compound | Decomposition | Gloss | Note |
|----------|--------------|-------|------|
| ke | heat + cool | "steady" | Heat-first: balanced by cooling |
| ek | cool + heat | "exact" | Cool-first: precise temperature |
| ee | cool + cool | "long" | Extended cooling |
| kee | heat + cool + cool | "deep" | Deep processing |
| eek | cool + cool + heat | "lock" | Locked/fixed state |

Same letters in different orders produce different but related glosses. Order sensitivity is structurally grounded in C521 (kernel directional asymmetry) and C1065 (atom bigram ordering grammar).

### Tier 4: The "o = vessel" Hypothesis

Current dictionary gloss "near" fails across 21 compound appearances. The hypothesis o = "vessel" (German *Ofen* = furnace) improves most fits:

| Compound | Decomposition | Gloss | Fit |
|----------|--------------|-------|-----|
| ok | vessel + heat | "seal" (seal before heating) | Strong |
| ot | vessel + transfer | "route" (through vessel) | Strong |
| ol | vessel + late | "continue" (let proceed) | Moderate |
| eo | cool + vessel | "open" (open cooled vessel) | Strong |
| opch | vessel + pause + adjust + watch | "operate" | Moderate |
| oiin | vessel + cycle + cycle + bind | "loop" | Strong |

The ok/ot sister pair (C408) decomposes as: ok = proactive vessel+heat management, ot = corrective vessel+transfer adjustment — matching the structural analysis exactly.

### Tier 4: Confidence Gradient Methodology

C1190 licenses using compound decomposition as a **gloss correction tool** with confidence grading:

- **High confidence:** Compounds whose atoms have Tier 2 behavioral profiles AND whose predicted profile closely matches observed (ke, ek, ee, hy, dy, ey)
- **Medium confidence:** Compounds with moderate-confidence atoms and reasonable fit (al, ar, ol, or)
- **Low confidence:** Compounds with weak atoms or poor prediction residuals

This methodology respects the semantic ceiling (C171, C120) — glosses describe operational function, not material identification.

### Cross-References

| Constraint | Role |
|------------|------|
| C1190 | MIDDLE behavioral atomicity (additive composition, MIDDLE-specific) |
| C1191 | Position-dependent composition (PREFIX emergent, SUFFIX systematic shift) |
| C267.a | 218 sub-components reconstruct 97.8% (structural basis) |
| C1003 | Pairwise compositionality at TOKEN level |
| C1065 | Atom bigram ordering grammar |
| C521 | Kernel directional asymmetry (order sensitivity) |
| C1070 | Ordering grammar independent of kernel physics |
| C929 | ch/sh sensory modality (explains PREFIX compound emergence) |
| C906 | Vowel primitive suffix saturation |


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

### Evidence (middle_incompatibility.py, 2026-01-12)


### Key Structural Objects



**3. PREFIX = soft prior, MIDDLE = hard constraint**

### Graph Structure


> The space is globally navigable, but only by changing discrimination regime step-by-step.

### Reconciliation with Prior Structure


### Tier 3: Interpretive Implications

**Why This Matters:**


**What Kind of System This Is:**

> A globally navigable but locally forbidden discrimination space — the strongest internal explanation yet of why the Voynich Manuscript looks the way it does without invoking semantics.

**Bayesian Modeling Progress:**


### I.E. Latent Discrimination Dimensionality




**Key Findings:**


**Interpretation (Tier 3):**


> **The MIDDLE vocabulary is not a categorization system with a few dimensions. It is a rich feature space where each variant has a unique 128-dimensional fingerprint.**

**What This Means for Generative Modeling:**


**Hub Confirmation:**



### I.F. Bundle Generator Diagnostic



**Generator Configuration:**

**Diagnostic Results:**


**Residual Interpretation (New Structure):**


**Interpretation (Tier 3):**

> **Incompatibility + priors are NECESSARY but NOT SUFFICIENT.** The generator reveals at least four additional structural principles: PREFIX coherence, tail forcing, repetition structure, and hub rationing.


### I.G. Coverage Optimality CONFIRMED



**The Test:**


**Key Insight:**


> **Currier A achieves greedy-optimal coverage while deliberately avoiding over-reliance on universal connectors.**

**Interpretation (Tier 2 - now CONFIRMED):**



**The Conceptual Pivot:**

> **Currier A is not meant to be *generated*. It is meant to be *maintained*.**



### I.H. HT Variance Decomposition



**Regression Results:**


**Interpretation (Tier 2 - CONFIRMED):**

> **HT density correlates with tail pressure - the fraction of rare MIDDLEs in A entries.**






### I.I. Temporal Coverage Trajectories





**The Four Signals (5/5 Support Strong Scheduling):**





**Interpretation (Tier 2 - CONFIRMED):**

> **PEDAGOGICAL_PACING: Currier A introduces vocabulary early, reinforces throughout, and cycles between prefix domains.**



**Reconciliation with Prior Findings:**




### I.J. Process-Behavior Isomorphism (v4.12 / ECR-4)



**Test Results (12/12 passed):**


**Key Findings:**






**Behavior Mappings (NO NOUNS):**





**Verdict (Tier 3 - SUPPORTED):**

> The grammar structure is isomorphic to reflux-distillation behavior. This does not prove the domain but establishes maximal structural alignment within epistemological constraints.


### f116v Correction


### I.K. HT Two-Axis Model



**The Unexpected Finding:**




**The Two-Axis Model (Tier 2 - CONFIRMED):**



**Why This Makes Sense:**

> **When the task is hard, HT is frequent but morphologically simple.**
> **When the task is easy, HT is less frequent but morphologically richer.**


**Constraint Alignment:**


**What HT Does NOT Encode:**


**Final Integrated Statement:**

> HT has two orthogonal properties:
>
> 1. **HT density tracks upcoming discrimination complexity** (tail MIDDLE pressure, AZC commitment).
>
> 2. **HT morphological complexity tracks operator spare cognitive capacity**, increasing during low-load phases and decreasing during high-load phases.
>
> HT does not encode what sensory modalities are needed. Sensory demands are implicit in the discrimination problem itself.


### I.L. MIDDLE Zone Survival Profiles



**Test Results:**


**The Four Clusters:**


**Interpretation (Tier 3):**

> **Currier A's discriminators are not only incompatible with each other - they are tuned to different *degrees of intervention affordance*, which the AZC legality field later enforces.**


**What This Does NOT Show:**


**Cross-References (Tier 2):**


**Why This Is Tier 3 (Not Tier 2):**




### I.M. Zone-Material Orthogonality



**Test Results:**





**Interpretation (Tier 3):**

> **The Voynich system tracks what a thing is (PREFIX) and how cautiously it must be handled (MIDDLE zone survival) as independent dimensions. This design choice explains both the richness of the registry and the irrecoverability of specific substances.**




**Why This Matters for Solvent/Material Decoding:**


> Solvent identity sits at the **intersection** of material type and handling sensitivity - and that intersection is never encoded. The operator supplies it from practice.

**What This Does NOT Show:**


**Cross-References:**


### I.N. Semantic Ceiling Extension Tests



**Test Results Summary:**


**New Structural Confirmations (Tier 3):**






**Nine-Layer Model:**


**B->A Inversion Axis:**




**Operator Strategy Taxonomy:**





## I.O. Physical World Reverse Engineering Phases
### Overview



### FM-PHY-1: Failure-Mode Physics Alignment (Tier 3)




**Key Finding:**

### SSD-PHY-1a: Structural Dimensional Necessity (Tier 3)




**Key Findings:**

**One-Sentence Synthesis:**
> **MIDDLE tokens are indivisible discriminators whose only "content" is their position in a very large, physics-forced compatibility space; the number of distinctions exists because the real process demands them, not because the author chose them.**

### OJLM-1: Operator Judgment Load Mapping (Tier 3)




**Key Findings:**

**Design Principle:**
> The controller's omissions are not gaps - they are deliberate acknowledgment that some knowledge cannot be encoded. This is design integrity, not incompleteness.

### APP-1: Apparatus Behavioral Validation (Tier 3)




**Key Finding:**
- Fourth degree fire prohibition matches C490 EXACTLY: "It would coerce the thing, which the art of true distillation rejects, because nature too rejects, forbids, and repels all coercion."

**What Excluded:**

### MAT-PHY-1: Material Constraint Topology Alignment (Tier 3)




**Key Findings:**

**What This Establishes:**

### Combined Arc


> **The Voynich Manuscript controls a circulatory thermal plant whose hazard profile matches distillation physics, whose discrimination space is forced by the physical state-space, whose operation REQUIRES human judgment for 13 structurally distinct types of non-codifiable knowledge, whose behavioral profile is isomorphic to the historical pelican apparatus, and whose registry topology matches the constraints that real botanical chemistry imposes.**



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

Phase 386 found that 4/6 dimensional differences between sections are explained by REGIME composition alone. Only h% and ol-density show independent section effects beyond REGIME. This means sections encode different *REGIME mixtures* (different techniques), with modest independent effects on h-kernel allocation and ol-morphology density. (Note: C1174 revises the prior "monitoring/checkpointing" interpretation of these effects.)

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









### Tier 3: Spatial Structure (Inconclusive)


### Interpretation (Tier 3-4)




## XII. Cross-System Vocabulary Flow (Phase 406)

### Tier 2: Structural Findings




### Interpretation (Tier 3-4)




## XIII. Dark Pipeline Functional Test (Phase 407)

### Tier 2: Structural Findings




### Interpretation (Tier 3-4)





## XIV. PP Pipeline Atom Decomposition (Phase 408)

### Tier 2: Structural Findings




### Interpretation (Tier 3-4)




### Tier 4: Operational-Profile Nomenclature


- **Modified ordering grammar (50% C1065 agreement):** Atoms are sequenced differently when naming something than when specifying operations on it -- perhaps the dominant processing property leads.
- **Grammar-standard prefixes (C1138, GS/EXT ratio 3.39):** Even identification tokens need a domain selector. Materials are identified within operational contexts.


### Phase 409 Extension: Dual-Channel Budget and Section-Specific Catalogs








## XV. Cross-Lane Content Prediction and Heat-Measure Cycle (Phase 443)

### Core Finding


### The Heat-Measure Cycle




### sh Monitor-Pivot vs ch Checkpoint-Gate (C1243)




### aiin→ain Wind-Down Pattern (C1244)




### Two Independent Scaling Axes (F-B-007)




### Cycle Is Strictly Line-Scoped


### Cross-Lane Pairing Decomposition (C1245, C1246)




### Apparatus Vocabulary Classification (C1247-C1249)


**Key structural findings:**










## XVI. 8-Category Operational System (Phases 452-456)

### Core Finding


### The 8 Categories


### Cross-System Organization (Phases 452-453)




### B Execution Grammar (Phase 454)


**Escape architecture solved:**
- THERMAL escape is fully PREFIX-mediated (C1277): THERMAL MIDDLEs are 44.1% qo-prefixed (vs 9.5% baseline). Partial correlation collapses to rho=-0.081 after controlling for qo. Chain: THERMAL MIDDLE -> qo-PREFIX selection -> zero-hazard QO lane (C601) -> escape.
- TRANSITION anti-escape is PREFIX-independent (C1281): partial=-0.586 survives ch/sh control. Mechanism initially unknown.




### Category Mechanism Decomposition (Phase 455)








**Paragraph architecture (C1287-C1290):**

- **Headers are MARKING-enriched (C1287):** Paragraph headers (first token) are 2.44x enriched for MARKING and 1.45x for STAGING, while THERMAL is suppressed (0.46x). This contrasts with line entries, which are THERMAL-enriched (C1283). Three-level specification hierarchy: paragraph header = marking/staging specification -> line entry = thermal specification -> line body = flow/transition execution.

- **Within-folio paragraph coherence (C1288):** Paragraphs within the same folio are more category-similar than cross-folio paragraphs (within JSD=0.109 vs null=0.122, z=-4.92). The folio (= program) imposes a category theme on all its paragraphs. Paragraph independence (C891-C893) is structural (grammar, kernel access) but not thematic (category composition).

- **Category predicts AXM dwell (C1289):** THERMAL fraction predicts high AXM self-transition (rho=+0.520), TRANSITION fraction predicts low AXM self-transition (rho=-0.519). Both survive Bonferroni. AXM is the dominant macro-state where 33/49 classes reside. THERMAL vocabulary keeps the system in its main operational loop; TRANSITION vocabulary moves it through state changes. This partially resolves the C1169 27% AXM residual variance.

- **Paragraph mode = category emphasis (C1290):** Mode A paragraphs are THERMAL-enriched (28.8% vs 21.0%), Mode B are TRANSITION-enriched (16.7% vs 11.5%). Chi2=300.4, V=0.114. Confirms C1279 at paragraph granularity.

### Relationship to Galenic Framework



### Interpretation (Tier 3)







### REGIME-Category Relationship (Phase 456)


**Key findings:**
- Categories survive section control but not kernel residualization -- kernel atoms are the primary pathway (C1291-C1292)
- Categories add genuine resolution beyond role profiles (Fisher p=7.5e-8) -- not a relabeling of existing class/role structure (C1293)
- **Categories do NOT extend C1169 AXM model** (C1294) -- the raw correlations (C1289, rho=+/-0.52) are fully absorbed by existing predictors. The 27% AXM residual is validated as irreducible design freedom.




## XVII. Paragraph Termination Mechanism (Phase 457)

### Core Finding


### What Was Tested and Failed


### Interpretation (Tier 3)






## XVIII. PREFIX Category Anatomy (Phase 458)

### Core Finding


### Channel Architecture




### Sister Pair Divergence in B



### BARE as Anti-Thermal Anchor


### Interpretation (Tier 3)






## XIX. Sister Category Mechanism (Phase 459)

### Core Finding


### Position Independence



### Mechanism: Vocabulary Selection



### Cross-Lane Category Routing


### Two-Atom PREFIX Instructions (Tier 3)




### Additivity



## XX. Cross-Mode Category Coupling (Phase 460)

### Core Finding


### Paragraph Category Coherence


### Mode Specialization


### Positional Synchronization


### B-to-A Thermal Feedback


### No Sequential Coupling


### BA Handoff Pattern


### Cross-Mode Sheet Music Principle (Tier 3 Synthesis)



## XXI. Distillation Terminology Mapping (Phase 461)



| PREFIX | k-fraction | e-fraction | Role |
|--------|-----------|-----------|------|
| qo | **0.510** | 0.102 | Heat source (k-dominant) |
| ok | 0.001 | **0.282** | Vessel temperature (e-dominant) |








| Property | ok (coarse) | ot (fine) |
|----------|------------|----------|
| THERMAL | 24.7% | 20.2% |
| OPERATION | 12.5% | 17.3% |





| PREFIX | Domain | Physical Referent | Evidence |
|--------|--------|-------------------|----------|
| qo | Heat source | Fire/furnace management | C1313, C1314 |
| ok | Vessel temperature | Thermal verification (coarse) | C1313, C1316 |
| REGIME | Proposed Method | Characteristic | Evidence |
|--------|----------------|----------------|----------|
| REGIME_1 | Balneum marie (water bath) | Gentle, e-rich, more sealing, highest alternation rate | T4, T5, T6, T10 |
| REGIME_2 | Sustained operation | High iteration, overnight cooling | T4, T10 |
| Test | Topic | Result | p-value |
|------|-------|--------|---------|
| T1 | Two-channel thermal model | PASS | 0.0 |
| T2 | Overshoot-correct cycling | PASS | 0.0 |


## XXII. Parallel Operator Hypothesis (Session Analysis, 2026-02-25)

**1. Shared vs Divergent MIDDLE Category Profiles (chi-squared = 2604, p < 0.001, 73 folios, 2721 paragraph pairs)**

| Category | Shared | Divergent | Ratio | Interpretation |
|----------|--------|-----------|-------|----------------|
| THERMAL | 23.7% | 18.5% | 1.28x | Shared: batch identity |
| TRANSITION | 18.8% | 13.3% | 1.41x | Shared: state changes |


**2. No Ordinal Complexity Gradient (74 folios with 3+ paragraphs)**

**3. "Master" Paragraph is Not a Combiner (59 folios with 4+ paragraphs)**

**4. Paragraph Count Distribution**


- Each operator has their own instructions (self-contained paragraphs, C845)



- C1121 (domain irrecoverability) still applies — we cannot identify what product was being made


## XXIII. Block Architecture: Gallows-Delimited Processing Stages (Phases 462-465)



| Section | Blocks/folio | Paras/block | Tokens/block |
|---------|-------------|-------------|--------------|
| B | 3.1 | 3.16 | 190 |
| H | 5.3 | 2.24 | 186 |















| Level | Unit | Sets | Inherits | Internal Structure |
|-------|------|------|----------|-------------------|
| **Folio** | Program | REGIME (thermal mode) | — | Blocks inherit REGIME |
| **Block** | Processing stage | Operational emphasis (PREFIX) | REGIME from folio | Paragraphs diversify within |




- The "no shutdown signal" finding (C1324) could mean blocks truly lack termination, or that the termination signal uses a channel we haven't tested (e.g., visual markers, spacing).

---


## XXIV. Block Vocabulary Drift and Multiplexing (Phases 466-467)



| Test | Metric | Result | Verdict |
|------|--------|--------|---------|
| Kernel drift (k→e) | Spearman rho | +0.026, p=0.600 | **FAIL** |
| Vocabulary narrowing | Spearman rho | **-0.248, p<0.001** | **PASS** |








---


## XXV. A Paragraph Category Architecture (Phase 468)



| Type | Count | % | Section bias |
|------|-------|---|-------------|
| STAGING | 105 | 43.6% | H-dominant (88/105) |
| FLOW | 48 | 19.9% | T-dominant (7/48) |





| System | Location | MARKING Signal |
|--------|----------|---------------|
| **Currier A** | Paragraph beginnings (C1336) | Position 0.429, 2.07x first-token |
| **Currier B** | Paragraph headers (C1287) | Header enrichment |







- The C171 semantic ceiling means we cannot confirm that "STAGING-dominant" paragraphs actually describe procedural sequences — the category labels are structural metaphors, not translations

---


## XXVI. Suffix Mode as Emergent Property (Phase 469)






| Band | Count | % |
|------|-------|---|
| Bare-locked (>80% bare) | 26 | 37.1% |
| Terminal-locked (>80% terminal) | 16 | 22.9% |









- **C1259**: Mode proportion is flat across body position (rho=-0.027) — because the vocabulary pool doesn't change position
- **C1233**: Mode alternation has near-random entropy (97.8%) — because mode is a consequence of vocabulary sampling, not a deterministic sequence
- **C1267**: Mode distinction doesn't organize A records — because mode is a B-execution phenomenon that emerges from how B tokens are suffixed, not from which MIDDLEs are selected

- The suffix sets and centroids (C1231) are defined from the corpus itself, so the "mode" construct is inherently circular at some level — mode is defined by suffixes, and we're testing what determines suffixes

---


## XXVII. Historical Genre Placement (Phase 552)
### Core Finding

> **The VMS does not belong to any existing medieval technical document genre. It occupies a unique position in document-design space at the intersection of non-linguistic notation, operational specificity, and formal grammar -- properties that no surveyed genre shares simultaneously.**


| Rank | Genre | Score | Key Matches | Key Gaps |
|------|-------|-------|-------------|----------|
| 1 | Laboratory notebooks | 2.5/7 | Expert audience, apparatus-specific | Natural language, single register, no safety architecture |
| 2 | Tally/accounting systems | 2.0/7 | Non-linguistic, externalized reference | Quantity-only, one-dimensional |


> **OPERATIONAL CONTROL CODEX:** A purpose-built, non-linguistic operational notation system encoding parameterized control programs for a specific apparatus class, designed for expert practitioners, with structural safety enforcement and multi-register architecture.

### Cross-References

| Topic | Evidence |
|-------|----------|
| Language/cipher falsification | C130, C132, C207 |
| Four-register architecture | C1499 |
| Instruction grammar | C121, C124 |
| Safety architecture | C109, C783, C997 |
| Brunschwig alignment | F-BRU-001 through F-BRU-034 |
| Expert audience | C197 |
| Paragraph non-sequentiality | C1399, C1400 |
| Full genre analysis | `phases/HISTORICAL_GENRE_PLACEMENT/GENRE_ANALYSIS.md` |


## XXVIII. Recipe-to-Folio Correspondence (Phase 628)
### Core Finding

Individual pseudo-Lull (PL) alchemical chapters can be matched to individual Voynich Currier B folios using 8-dimensional residual feature profiles, and this matching generalizes across unseen family-regime pairings. The within-family permutation test passes decisively (p < 0.001), confirming chapter-level specificity beyond regime-level gradient.


| PL Feature | V Feature | Sign | Channel |
|-----------|-----------|------|---------|
| heat_rate | k_ratio | -1 | Known (C1871) |
| monitoring_rate | h_ratio | +1 | Known (C1872) |
**Ch19 -> f75r: Aqua Vitae Composite (repeated distillation)**

**Ch18 -> f76r: Element Separation (graduated distillation)**

**Ch12 -> f113v: Mercury Sublimation (dissolve/distill/return cycle)**


| Family → REGIME | Confident | CV Consensus | Mean Ratio |
|----------------|-----------|-------------|------------|
| Distillation → R1 (training) | 9/16 | 11/16 | 1.284 |
| Sublimation → R3 | 4/7 | 4/7 | 1.174 |


### Tier Assessment

**Tier 3** — The matching is statistically validated (permutation p < 0.001) and replicates across unseen family-regime pairings. Independent structural evidence (PREFIX inversion, token repetition uniqueness) converges with feature-based matching. However, individual chapter-folio assignments remain speculative (the matching algorithm finds best fits, not proven correspondences).

### What This Does NOT Claim

1. No individual recipe translation is recoverable from matching alone
2. The token repetition count does not "mean" the number nine — it indicates unusually high iteration
3. Feature correspondences are statistical associations, not semantic mappings
4. The 8D feature set was tuned on distillation->R1; generalization is encouraging but not proof of universality

### Cross-References

| Topic | Evidence |
|-------|----------|
| Channel discriminative mapping | C1871-C1874 (Phase 627) |
| Permutation significance | C1888 (Phase 628) |
| PREFIX inversion | C1478, C1891 (Phase 628) |
| Token repetition uniqueness | C1890 (Phase 628) |
| e-depth parametricity | C1225, C1394 |
| Section-level paragraph count | C1090, C1091, C1893 |
| Literal enumeration | C287 |
| Full analysis | `phases/RECIPE_FOLIO_CORRESPONDENCE/` |


---

# Session Methodology Notes

These are project-level methodology rules accumulated across sessions. They document trap patterns we have already caught, controls that are load-bearing, and discipline rules that govern how new findings should be validated. **Apply these as priors when assessing new proposals.**


## feedback-5gram-markov-null-for-surface-patterns

*"5-gram null is the appropriate floor for sequence/positional claims; within-folio shuffle catches composition shadow but not local-character-statistic shadow. Run 5-gram null FIRST for any \"X follows Y\" or smoothness claim."*

# 5-gram Markov null is the appropriate first null for sequence/positional claims

## Rule

For any constraint of the form "X follows Y at rate above baseline" or "adjacent units are smoother than shuffled" or "transition pattern is enriched," **the first null run must be a character 5-gram trained on the corpus, NOT within-folio shuffle**. Within-folio shuffle is still the right null for co-occurrence / density claims (does X appear with Y more than chance within the same folio?) but it tests a different question than what most positional/sequential constraints actually claim.

## Why: 5-gram and within-folio shuffle answer different questions

- **Within-folio shuffle null** tests: "Are the labels randomly placed in their positions given folio composition?" Preserves marginal counts; breaks ordering. Catches the trap "this folio happens to have many CHSH tokens and many hazard tokens, so they co-occur by composition."

- **5-gram Markov null** tests: "Is the joint pattern reproducible from local character statistics?" Generates new text from `P(char | previous 4 chars)`. Catches the trap "the end-of-X character sequences naturally transition to start-of-Y character sequences in this corpus's character co-occurrence."

A pattern can pass within-folio shuffle at p<0.001 and still fail 5-gram null with residual ~0. Both demoted constraints in PHASE_729 (C1727 line-ordering smoothness, C645+C2045 post-hazard CHSH recovery) fit this profile: they showed strong above-shuffle effects, but those effects emerge naturally from local character statistics and don't require any intentional structural rule.

## How to apply

For any new constraint claiming positional/sequential/transitional structure:

1. **Train a character n-gram (order 5 default) on the corpus**, optionally with target-folio held out.
2. **Generate synthetic text** with matched line/folio structure.
3. **Apply the same measurement** to synthetic.
4. **Report residual** = (real effect) − (synthetic effect).
5. **Threshold for "survives Markov null":** residual >10 pp for percentage-based effects, or z-difference >2 for z-based effects. Residuals <5 pp are in noise floor.

Within-folio shuffle remains valid as a *second* null for composition shadow — but it does not certify a pattern as "above Markov." The two are complementary, not substitutable.

## Why this matters now

PHASE_729 demonstrated the issue empirically. C1727 (line-ordering smoothness, z=-6.05) and C645+C2045 (post-hazard CHSH 75.2% vs 55.3% baseline) had both passed within-folio shuffle null at p<0.001 and were treated as load-bearing architectural evidence. The 5-gram null gave:

- C1727: real z=-3.83 vs synthetic z=-3.71 (residual ~0, Markov-trivial)
- C645+C2045: real +19.6 pp vs synthetic +17.3 pp (residual +2.3 pp, Markov-trivial)

Both demoted. Meanwhile constraints that *do* survive 5-gram null (C2032 lag2/lag1, the C2056 correction-lane family with 17-30 pp residuals, f77r and f39r reverse-blind matches) are reinforced precisely because they survive the sharper null.

## Diagnostic shortcut for re-auditing legacy constraints

Crazy-expert's suspect-zone heuristic (from PHASE_729 expert consultation):

- Constraint cites positional/sequential pattern with bigram-level or unigram-level baseline
- Effect size in 1.5-3× range (Markov-trivial patterns produce moderate but consistent effects)
- Validated with shuffle null only, no Markov control
- Date of validation pre-PHASE_700 (before methodology lessons)

Constraints matching all four criteria are high-suspicion. Estimated ~120 in the C600-C800 range. Expected 40-60% demotion rate under 5-gram null.

## Refinement (PHASE_731 batch 1, 2026-05-28): bimodal expert prior on high-percentage claims

PHASE_731 batch 1 produced a clean expert prediction miss on C562 (ary 100% line-final). Both experts (especially crazy-expert) predicted DEMOTE on "100% won't reproduce on re-measurement." The 100% DID reproduce (16/16 ary tokens line-final in Currier B), and the 5-gram synth produced only 11.86% — SURVIVES STRONG at z=10.25, residual +88pp. The miss revealed a needed refinement to the expert prior:

**Distinguish two sub-types of high-percentage claims:**

- **Frequency claims** (>95% but <100%, e.g., "97% line-final," "98% of class X"): typically drift slightly under re-measurement (counting denominator shifts) AND are often Markov-reproducible at modest residual. **HIGH audit suspicion** — these match the C600-C800 suspect-zone heuristic above.

- **Categorical exclusions** (exactly 100% or 0% with structural rationale, e.g., LATE-class membership predicting categorical line-final lock): typically robust under re-measurement (the structural rationale enforces the exact value) AND often survive 5-gram null at large residuals because character-Markov can't reproduce 100% positional locks or 0% exact prohibitions backed by morphological class structure. **LOWER audit suspicion** when the structural backing is present.

The C562 case fits the C539 LATE-class membership pattern — ary's grammar requires line-terminal position. The 5-gram learned ary tends to appear line-final but didn't enforce 100%. The categorical structure is real and above-Markov.

**Decision rule for batch 2+:** when a candidate constraint cites a 100% or 0% rate, ask whether there's a structural rationale (terminal class, role-class binding, atom-grammar constraint, codified hazard topology). If yes → likely-survivor family, lower suspicion. If no (just a count that happens to be 100%) → still suspect, audit as before.

**Likely-survivor categorical-exclusion family:** C539 (LATE-class), C1486 (m-terminal line-final), C1487 (six-terminal taxonomy), C109 (17 forbidden transitions — but split needed: some Markov-trivial, some genuinely above-Markov per crazy-expert), k-HEAD 0% hazard claims (C1446, C1476), e→y zero hazard (C1457-C1462).

**Likely-demoter positional-gradient family** (validated by PHASE_731 batch 1): C600-C700 ordinal/sequential claims, "X enriched at position Y" without categorical structure, paragraph-position HT claims (C842, C843, C870), CC positional ordering cascade from C816 (C817, C818, C874, C600, C558, C819).

## Related memories

- [[feedback-within-folio-shuffle-null-first]] — load-bearing for composition-shadow questions
- [[feedback-made-up-threshold-audit]] — failure-mode taxonomy now spans 8 patterns; pattern 8 added per PHASE_729
- [[feedback-mechanism-cycle-procedural-ceiling]] — mechanism interpretation retraction discipline applies when 5-gram demotes structural finding

---

## feedback-aggregate-minus-original-independence-test

*"When testing whether a registered specific finding generalizes to a class-level pattern, the aggregate must show independent significance after removing the original signal. If aggregate-minus-original doesn't clear significance, the \"generalization\" is consistency-checking not new evidence (PHASE_705, 2026-05-19)"*

When a registered specific finding (single-pair, single-folio, single-token-class) is followed by a generalization test (aggregate across multiple instances of a putative class), the load-bearing analysis is **aggregate minus original**.

**Why:** PHASE_705 tested whether C2041's ar→al directional asymmetry generalizes to r-terminal → l-terminal class grammar. Aggregate Test A passed cleanly: r-class→l-class = 94 vs l-class→r-class = 51, asymmetry +0.297, p_BH=0.0018, N=145. Looked like a clean Tier 2 generalization.

Crazy-expert caught the methodological issue: of the 5 observable cross-class pairs contributing to the aggregate, two (ar→al and al→ar) ARE C2041's data. Removing the ar→al pair from the aggregate:
- r-class → l-class without ar→al: 94 − 39 = 55
- l-class → r-class without al→ar: 51 − 14 = 37
- Aggregate-minus-original asymmetry: +0.196
- Binomial p ≈ 0.06 — **NOT significant**

The "generalization" was inheriting ~37% of its signal from the already-registered pair. Aggregate independence test failed.

Confirming diagnostic: or→al at +0.05 (N=21) is near-symmetric. If r→l were truly a class-level grammar, all observable r-class × l-class pairs should show asymmetry. or→al doesn't. The actual pattern is (a) ar-lexeme-specific + (b) ol-as-late-destination, not class-grammar.

**How to apply:**
- When aggregating across instances of a putative class to test generalization of a registered pair-level finding, the load-bearing analysis is: does the aggregate remain significant after removing the original pair?
- Specifically: compute (aggregate - original) statistics. If significance is lost, the aggregate is not independent evidence — it's consistency-checking with overlapping data.
- Decision rule: if aggregate-minus-original doesn't independently clear the same significance threshold (p < 0.05 corrected, effect size above floor), DO NOT register a new aggregate-level constraint. Instead, sharpen the original constraint's description or refine its scope.
- Also check the "uniformity diagnostic": if the class-grammar reading were correct, all observable pairs should show the asymmetry. A single observable pair contradicting the direction at near-zero asymmetry (like or→al here at +0.05) is the load-bearing falsifier of class-grammar interpretation.

**Combines with:** [[feedback-framework-as-null]] (treat framework-fit as prior toward null at mature stage), [[feedback-n-matching-for-within-scribe-comparisons]] (control for overlapping/imbalanced evidence), [[feedback-operational-story-first-trap]] (resist promoting consistency-checks to generalizations).

Related: PHASE_705 INDEX-only documentation; C2041 sharpened with refinement footnote.

---

## Atom decomposition reads as word salad in cold reads

*Token-level atom glosses (heat.cool.mark.end) are not compelling to outsiders — cold reads should lean on structural patterns (counting anchors, e-depth arcs, dar distribution) not atom-by-atom decomposition*

Atom-by-atom token decomposition in cold reads produces word salad like "add material, iterate bind" that is unconvincing to outsiders and academics. "Iterate what? Bind what?" — the atoms are structural labels, not readable language.

**Why:** Tokens take on operational identity in practice beyond their atom composition. C1193 (core prefixes as frozen functional units), C171 (semantic ceiling), MODEL_CONTEXT.md ("tokens have roles, not meanings — semantics exist only in operator practice"). Token meanings are listed as IRRECOVERABLE. The atom glosses (C1195, Tier 3-4) describe positional role in the grammar, not what the operator was doing.

**How to apply:** In cold reads and external-facing documents, lead with the quantitative structural evidence that doesn't require believing the gloss system: counting anchors (corpus-singular token runs), e-depth thermal arcs, dar distribution patterns, observation MIDDLE distribution, paragraph structure. Use atom glosses only as supporting context with heavy caveats, not as the primary argument. When glossing tokens for a reader, use whole-token operational descriptions ("one complete heat cycle", "material addition") rather than atom chains ("heat.cool.do.end", "into.iterate.bind").

---

## bootstrap-ratio-at-noise-floor

*r21 = lag2/lag1 ratio explodes into apparent large signatures when lag1 is at noise floor. Random subsets at N=70 can produce Voynich-magnitude r21 by chance. The metric needs lag1 magnitude well above noise floor (|lag1| > ~0.005) to be interpretable.*

**7th distinct failure pattern** in the project's failure-mode taxonomy, documented from PHASE_722 (2026-05-20).

PHASE_722 ran Rupescissa intra-corpus register stratification (recipe-dense vs theory-dense quartiles, N=69 and 72 respectively). Pre-registered criteria nominally PASSED (recipe-dense r21=-1.44, theory-dense r21=+0.46, register_diff > 1.5× control_diff). But controls revealed the result was bootstrap-ratio noise amplification:

- Recipe-dense lag1 = -0.00162 (6× smaller than Codicillus canonical -0.01013)
- r21 = -1.44 is the ratio of two noise-floor values (lag2=+0.00233 / lag1=-0.00162)
- Random quartile split control (seed 0) produced r21=-0.658 in a RANDOM subset — Voynich's exact magnitude — purely by chance

**The diagnostic pattern:** when lag1 is at noise floor (|lag1| < ~0.005), the r21 ratio amplifies tiny numerator variations into apparent large signatures. Both directions (-1.44 and +0.66) are reachable via random selection at this N.

**Why pre-reg criteria failed to catch it:** the binary thresholds (register_diff > 1.5× control_diff) were calibrated against expected effect sizes, not against the noise floor of the metric itself. The random_quartile control produced max diff=1.034, the register difference was 1.897. Nominal pass. But seed 0's bottom-quartile r21=-0.658 is the load-bearing signal: noise can produce Voynich-magnitude r21 in random subsets at N=70.

**Comparison to canonical magnitudes:**
- Codicillus canonical lag1 = -0.01013, r21 = -0.229 (stable, well above noise floor)
- Voynich Section B canonical lag1 ≈ -0.03 to -0.04, r21 = -0.66 (well above noise floor)
- Recipe-dense Rupescissa lag1 = -0.00162 (noise floor)

The r21 metric requires lag1 magnitude **at least 5-10× above noise floor** for stable interpretation. At lag1 ≈ -0.002, r21 is meaningless as a signal-vs-noise indicator.

**How to apply:**

When evaluating any r21 (or similar bootstrap-ratio) result:
1. Check lag1 (denominator) magnitude. If |lag1| < 0.005, r21 is in noise-amplified regime and the result is unreliable regardless of how strong it looks.
2. Always run random-subset control at the same N and same metric. If random subsets produce comparable magnitudes (e.g., random subset r21 ≈ target effect), the metric has no discriminating power at this N.
3. Pre-registered binary thresholds that don't account for the noise floor of the metric itself can produce nominal passes that fail proper scrutiny. The threshold should be calibrated against the random-subset distribution at the target N, not against theoretical expectations.

**Resolution paths (per expert convergence):**

When a metric hits this failure mode:
- **(a)** Aggregate larger corpora to escape the noise floor (need ≥150 paragraphs per stratum for stable r21)
- **(b)** Abandon the ratio metric; use the numerator (lag2) or denominator (lag1) directly, OR use peak-specificity methodology per `feedback_peak_specificity_for_periods_geq_7.md`
- **(c)** External grounding (the r21 method is exhausted at this N for this corpus)

**Generalizes:** this is a specific instance of `feedback_n_matching_for_within_scribe_comparisons.md` (bootstrap-ratio fragility when denominators are small) extended to noise-floor regime specifically.

**Cumulative pattern recognition:** PHASE_722 is the 6th interpretive finding in a single session (2026-05-20) that passed nominal pre-reg but failed proper scrutiny. Per crazy-expert: "the framework now has enough operational vocabulary that ANY new stratification can be told as a clean operational story with surface-passing statistics." When in the operational-specificity death zone, NEW failure patterns emerge as the cycle saturates. This memory documents one such pattern; expect more as the cycle continues until methodology pivots or external grounding is achieved.

---

## feedback-broken-baseline-audit

*"When a constraint claims \"X optimized vs Y-alternative,\" audit Y's implementation. If Y is an algorithm artifact (alphabetical fallback, sampling-with-replacement on Zipfian, etc.) rather than a meaningful representative of the alternative hypothesis, the comparison is broken — independent of how clean the numbers look. C476 audit established (2026-05-19)"*

The C131/C475/C1068 audit patterns address invented thresholds, wrong denominators, and wrong-null-tests respectively. C476's pattern is distinct: **the null/baseline implementation doesn't represent the alternative hypothesis the constraint claims to refute**.

The constraint construct may be sound (compare real corpus to baseline-strategy). The numerical machinery may be sound (proper sampling, correct statistics). But the BASELINE itself is contaminated by implementation choices that have nothing to do with the hypothesis being tested.

**The C476 case study (2026-05-19 audit):**
- C476 claimed: "Currier A achieves greedy-optimal coverage while using 22.3% FEWER hub tokens than greedy would require" (Tier 2). Interpreted as "deliberate hub rationing."
- Real A: 100% coverage, 31.6% hub usage
- Greedy baseline: 100% coverage, 53.9% hub usage
- Headline: 22.3pp "hub savings"

Audit found the greedy algorithm picks new MIDDLEs first (gain=1) but **once all MIDDLEs are seen, every candidate has gain=0**. The algorithm then picks the FIRST candidate from a sorted list — which means alphabetical fallback. Hub MIDDLEs ('a', 'o', 'e', 'ee', 'eo' per C475) happen to be alphabetically early, so greedy spams hubs after coverage is achieved.

The "22.3pp hub savings" was measuring `sort(alphabetically_early_strings)` not `coverage_optimization_strategy_vs_rationing`. The comparison was algorithm-implementation-artifact, not hypothesis-testing.

**Diagnostic test for this failure pattern:**
1. Identify constraints framed as "X is optimized/conserved/managed vs [BASELINE] alternative"
2. Find the BASELINE algorithm's source code
3. Ask: does this algorithm have **tie-breaking, fallback, or default behavior** that gets invoked frequently in practice?
4. If yes, ask: does that behavior have anything to do with the alternative hypothesis?
5. Specific red flags:
   - Alphabetical or numerical sort as tie-breaker (fires whenever multiple candidates score equal)
   - Sampling with replacement (over-samples high-frequency items)
   - Greedy-then-fallback (the fallback dominates once the greedy goal is met)
   - Random.choice from a sorted/non-shuffled list (favors early items)

If the baseline's measured behavior is dominated by such artifacts, the comparison is broken regardless of how clean the numbers look.

**How to apply:**
- When proposing new "X vs Y-baseline" constraints: explicitly test the baseline's behavior under degenerate cases (all-equal scores, post-saturation, etc.). If the baseline's behavior in those cases is non-representative, the comparison won't generalize
- When auditing existing constraints citing "optimized vs greedy/uniform/freq-matched baselines": read the baseline algorithm before trusting the comparison
- The surviving substantive measurement may be **directionally opposite** to the original framing (as with C476: claim was "rationing," reality is "enrichment"). In that case retraction is cleaner than demotion — demotion under wrong-direction framing misleads future readers

**Demote vs retract decision rule:**
- If broken baseline + surviving measurement supports the claim's direction → demote with reframe
- If broken baseline + surviving measurement contradicts the claim's direction → retract (don't demote)
- C476 fell into the second category (3.2× hub ENRICHMENT vs uniform contradicts "hub rationing")

**Related methodology memories:**
- [[feedback-made-up-threshold-audit]] (C131 — invented threshold, three-axis failure)
- [[feedback-denominator-choice-sparse-cooccurrence]] (C475 — wrong denominator in sparse co-occurrence)
- [[feedback-chi2-vs-permutation-null-mismatch]] (C1068 — wrong-null-test in frequency-correlated data)
- [[feedback-calibrate-thresholds-against-controls]] (PHASE_697 — calibrate against in-distribution controls before locking)

**Failure-mode taxonomy (4 patterns now established):**
1. **C131 pattern:** invented threshold + non-reproducing value + null at observed → RETRACT
2. **C475 pattern:** wrong denominator (N_possible vs N_attested) on sparse data → DEMOTE if strong-form survives in adjacent constraint
3. **C1068 pattern:** chi² against wrong null when factors share frequency marginals → DEMOTE with marginal-perm-null note
4. **C476 pattern:** broken baseline that doesn't represent the alternative hypothesis being claimed → RETRACT if surviving measurement is wrong-direction, DEMOTE if right-direction-but-weaker

Each is a distinct audit-shape worth its own diagnostic. The taxonomy is high-EV for mechanizing audit-sweep work.

**Broader audit policy implication:**
2026-01-12 probe family (MIDDLE_INCOMPATIBILITY, COVERAGE_OPTIMALITY, TEMPORAL_TRAJECTORIES) is producing 2/2 audit-hit rate (C475 demoted, C476 retracted). Elevated prior for related constraints in same batch — targeted audit-sweep of C478, C481, C755, C756 indicated. Crazy-expert estimated 30-40% retraction/demotion rate in this batch based on 2/2 prior.

**Audit-sweep tool refinement candidate:**
The audit-sweep regex patterns don't currently catch broken-baseline issues — they're invisible in constraint description text (the baseline name appears, but its implementation details don't). Detection requires reading the source code of the baseline algorithm. Manual audit will remain essential for this pattern.

---

## Pre-registered numerical thresholds require empirical calibration against in-distribution controls (2026-05-17)

*When a metric is new (no prior project benchmarks), the threshold for "significant" or "pass" must be calibrated against control distributions (other corpora, scrambled data, null shuffles) BEFORE locking binary pre-registration criteria. Pre-locking thresholds based on intuition produces either false-pass (threshold too lenient) or false-fail (threshold too strict for the metric's actual variance). PHASE_697 demonstrated this: pre-bookkeeping cross-NL ceiling threshold was set at ≤0.10 for "Reading B opens" based on theoretical priors, but actual cross-NL ceiling (Latin→Italian) turned out to be 0.319 — making the original criterion uninformative. When the threshold falls inside the calibration range, the test is uninformative; don't flip verdicts on a falsified threshold; register the calibration failure and re-design the test.*

## The rule

When pre-registering binary criteria for a novel metric, calibrate the threshold against in-distribution controls BEFORE locking the binary criteria. Don't pick thresholds from theoretical intuition — pick them from observed control distributions.

## How it failed in PHASE_697

The V/C-partition cross-NL ceiling test was pre-registered with thresholds based on theoretical priors:
- **"Reading B opens"** if cross-NL ceiling JS ≤ 0.10
- **"Reading B fails (overfitting confirmed)"** if cross-NL ceiling JS ≥ 0.20

Both thresholds turned out wrong. Actual cross-NL ceiling values:
- Cicero → Caesar (same-language sanity): JS = 0.110 (not ≤0.05 as another threshold predicted)
- Cicero → Dante Inferno (Latin → Italian): JS = 0.319 with NO hill-climb improvement
- Italian → German: JS = 0.330 under optimal V/C

The "Reading B opens" threshold (≤0.10) was unrealistic — no cross-NL pair achieves that. The "overfitting confirmed" threshold (≥0.20) is satisfied by ALL cross-NL pairs trivially. The metric's actual noise floor was higher than either threshold accounted for.

## What this caused

Initial verdict per pre-registration said "FAIL Reading B (overfitting confirmed)" because Voynich's 0.256 was above the 0.20 threshold. But the real comparison was Voynich's 0.256 vs ACTUAL cross-NL ceiling of 0.319 — Voynich is BELOW the real ceiling. The pre-registered verdict reversed the substantive conclusion.

This was caught only because the test was re-run with proper baselines and the threshold was reconsidered. Without that re-examination, the morning's work could have been falsely shut down by an uncalibrated pre-registration.

## How to apply

**Procedure for novel-metric pre-registration:**

1. **Before locking thresholds**, run the metric on at least 2-3 control distributions:
   - Same-class baseline (e.g., within-language pairs for cross-language metrics)
   - Different-class baseline (e.g., cross-language pairs)
   - Random/shuffled baseline (e.g., scrambled corpus)
2. **Document observed control values** with explicit ranges
3. **Set thresholds AT calibrated boundaries**, not at theoretical priors:
   - "PASS" threshold = best observed control value + margin
   - "FAIL" threshold = worst observed control value − margin
4. **Lock thresholds, then run main test.** Verdict is now informative.

**When mid-test you find a threshold was wrong:**

1. Acknowledge calibration failure transparently
2. Do NOT flip the verdict based on the falsified threshold
3. Register the calibration failure as a methodological note
4. Re-design the test with calibrated thresholds
5. Re-run if substantively necessary

## Why this matters at this project stage

PHASE_697 was a substrate-level finding registered after three narrowings of operational interpretations. The discipline that caught the operational overclaims (cardinality, slot-grammar, Italian-ear) is the same discipline that should catch threshold-calibration errors. The framework-as-null memory note warns against operational interpretations fitting the project's framework too cleanly; this companion note warns against numerical thresholds fitting theoretical priors too cleanly.

The metric's behavior is empirical. Treat the threshold as empirical too.

## Connection to other methodology notes

- `feedback_framework_as_null.md` — operational-interpretation overclaim catching (semantic)
- `feedback_calibrate_thresholds_against_controls.md` (this note) — numerical-threshold overclaim catching (quantitative)
- `feedback_within_folio_shuffle_null_first.md` — load-bearing first control for paragraph-level metrics
- `feedback_three_mechanism_demotion_trifecta_2026_05_16.md` — operational interpretations die at any specificity
- `feedback_mechanism_cycle_procedural_ceiling.md` — internal mechanism cycle has procedural ceiling

Together these establish the substrate-vs-mechanism distinction and the controls each requires.

## See also

- `phases/PHASE_697_VC_PARTITION_DISCOVERY/INDEX.md` — the audit trail of three threshold-related narrowings
- C2033 — the surviving narrow Tier 2 measurement after the threshold recalibration
- `phases/PHASE_697_VC_PARTITION_DISCOVERY/results/vc_ceiling_and_bootstrap.json` — the moment the pre-registered threshold was discovered wrong

---

## feedback-chained-controls-scalar-vs-eigenstructure

*"Three load-bearing nuances from PHASE_733 — (1) per-synth-own-shuffle baseline is mandatory (raw real-vs-synth conflates composition-fidelity with structure), (2) metrics through constraint-laden algorithms are confounded (floor-control or bypass), (3) scalar aggregate MI ≠ eigenstructure — a 5-gram can reproduce one and not the other."*

# Chained controls + scalar-vs-eigenstructure (PHASE_733)

PHASE_733 tested C2023 (class-layer sequential structure, grounds the macro-automaton) against the 5-gram null for the first time. A chain of controls — each catching the previous one's confound — flipped the verdict twice before converging. Three reusable lessons.

## Lesson 1: per-synth-own-shuffle (own-baseline) is mandatory for cross-corpus structured-metric comparison

The naive test compared real raw MI (0.264) to 5-gram-synth raw MI (0.221), got z=+3.83, "survives." FALSE POSITIVE. The synth has lower class diversity → lower raw MI AND lower own-shuffle floor. Comparing raw values measured composition-fidelity, not the structure under test.

**Fix:** compute each corpus's metric as an EXCESS over its OWN shuffle null (real_excess = real − real_shuffle; synth_excess = synth − synth_OWN_shuffle), then compare excesses. This cancels the MI-estimator bias and the composition-fidelity gap. Under the correct metric: real excess +0.0485 vs synth +0.0421, p=0.21 → C2023 actually FAILS (5-gram-reproducible).

Generalizes `feedback_within_folio_shuffle_null_first.md`: whenever comparing a structured metric (MI, λ2, autocorrelation, …) across corpora with different composition, each corpus must be referenced to its OWN null, never to a shared/real null. Raw cross-corpus comparison is a composition-fidelity artifact generator.

## Lesson 2: metrics computed THROUGH a constraint-laden algorithm are confounded

To test whether the 5-gram reproduces the C976 6-state macro-automaton TOPOLOGY, I ran C976's constraint-preserving merge on synth corpora and computed partition-ARI vs canonical. 5-gram gave ARI 0.762, all 6 states — looked like reproduction. CONFOUND: the merge has hardcoded role-integrity + 18 depleted-pair constraints that FORCE a 6-state partition. Floor control: within-line shuffle through the merge → 0.804; UNIFORM-RANDOM matrix → 0.669; real → 0.937. Even structureless noise scores 0.67-0.80 because the constraints dominate.

**Fix:** floor-control any algorithm-mediated metric with shuffle AND random fed through the SAME pipeline. Better: prefer a metric that bypasses the constraint-laden algorithm entirely. Here, λ2 of the RAW 49×49 transition matrix (no merge) is the clean macro-structure measure.

## Lesson 3: scalar aggregate ≠ eigenstructure — test the right functional

C2023's scalar I(class;prev) was 5-gram-reproducible (p=0.21) BUT the macro-state eigenstructure λ2 was NOT (real 0.206 vs 5-gram 0.119 ≈ shuffle floor 0.118; per-synth excess p=0.000). Both true, fully coherent:
- **Scalar MI** = high-mass-dominated lumped functional of the bigram joint. Dominated by frequent LOCAL control bigrams (qo→ch/sh, which survived 5-gram null in PHASE_731). A 5-gram reproduces those → reproduces scalar MI.
- **λ2** = global community/slow-mixing structure (which classes form metastable macro-states). A relational pattern across many cells, not in any local n-gram window. The 5-gram has no mechanism to reproduce it.

A model can match the high-mass joint distribution (→ matched scalar MI) while flattening the slow-mixing block structure (→ collapsed λ2). λ2 is the more sensitive, more discriminating measure of genuine macro-organization. **For macro-state / automaton / "does it have global structure" claims, test the eigenstructure (λ2) directly — do not rely on scalar MI, which is floor-dominated.**

## The synthesis this produced

Three-axis decomposition (registered C2062): class-sequential structure = (a) local control bigrams [real, above-Markov], (b) macro-state eigenstructure [real, above-Markov], (c) aggregate scalar first-order class-MI [morphology-reproducible middle layer]. The genuine grammar lives in (a) and (b); the scalar aggregate that C2023 measured is the weak floor-dominated layer.

## Outcome

C2023 scalar-MI half demoted Tier 2→3 (joins C1727/C645 as shuffle-survivor failing 5-gram). C976-C978 macro-automaton VINDICATED at the eigenstructure level (C2061) — passed the sharpest null it has ever faced. Cascade stopped at C2023; Tier 0 and the 49-class partition untouched. The discipline (chained controls + expert adjudication) prevented BOTH a false-positive registration (naive "survive") AND a false cascade (steamrolling C2023's failure into a macro-automaton demotion).

## PHASE_736 extension: self-transition/dwell scalar is a mass artifact; eigenstructure may be DISTRIBUTED

The scalar-vs-eigenstructure split recurred at the macro-state-block level (PHASE_736, the AXM attractor). Two reusable lessons:

1. **A macro-state's self-transition / dwell RATE is a mass artifact — never infer "designed cohesion" from it.** AXM (68% of token mass) has 0.698 self-transition. Under per-synth-own-shuffle 5-gram null: real excess over composition +0.0104, synth +0.0121, z=−0.39, p=0.655 — fully Markov-reproducible. A block holding fraction f of the mass self-transitions at ~f by construction; a character model reproduces it because it knows the mass. This is a NON-FINDING, not a demotion (it was never above-Markov). Diagnostic: before claiming an attractor/dwell is "designed," check whether self-rate ≈ mass-fraction — if so, it's composition.

2. **The above-Markov eigenstructure (λ2) may be DISTRIBUTED, not localized in the high-mass block.** Test where the slow mode lives: (a) submatrix-λ2 (real-data, no null) — compare block-only vs rest; (b) 2nd-eigenvector LOADING falsification — if loading concentrates on a few classes within one block, the mode is localized (and would predict high spectral clustering ARI); if it's class-proportional and spread across blocks, it's distributed. PHASE_736: AXM-block λ2 0.222 ≈ lanes 0.205; loading 0.642 ≈ class-fraction 0.65, participation ratio 28.8/49, top loaders mixed AXM+lane → distributed. This mechanistically explained C1010's non-spectral partition (ARI=0.059): the role/depletion partition can't be spectrally recovered because the slow mode doesn't align with the blocks. Registered C2065.

The eigenvector-loading test is the cheap falsification for any "distributed vs localized eigenstructure" claim — it can collapse the claim (concentrated gradient) and survived here.

## Related memories

- [[feedback_within_folio_shuffle_null_first]] — own-baseline generalization
- [[feedback_5gram_markov_null_for_surface_patterns]] — the 5-gram null discipline; C2023 is the cleanest application
- [[feedback_expert_audit_prevented_post_hoc_registration]] — expert-mandated controls catch false positives
- [[feedback_made_up_threshold_audit]] — don't compare a raw number to an arbitrary absolute threshold (the topology script's 0.70 cut was exactly this trap)

---

## feedback-chi2-vs-permutation-null-mismatch

*"Chi² test against independence null assumes independent marginals; when factors correlate with token frequency, chi² gives astronomically significant p-values while marginal-preserving permutation null gives correct (often marginal) p-values. C1068 audit established (2026-05-19) — perm_p=0.13 with chi² p=3.4e-292"*

When testing cross-layer or cross-factor coupling/dependency, **chi² against the independence null is misleading if both factors correlate with token frequency**. Both factors will inherit the token-frequency distribution as a shared marginal, and chi² will reject independence trivially — even when the underlying coupling is absent or fully explained by frequency mediation.

The methodologically appropriate test is the **marginal-preserving permutation null**: shuffle one factor's assignments across categories while preserving its marginal frequency distribution, then re-compute the coupling statistic (NMI, Cramér's V, or similar). The empirical p-value from this permutation null is the correct significance test.

**The C1068 case study (2026-05-19 audit):**
- C1068 claimed "Cross-Layer Partial Coupling" between C475_degree (MIDDLE attested-compatibility-degree) and C911_restriction (PREFIX×MIDDLE forbidden pairs)
- Test statistics: chi² = 1367.0, p = 3.4 × 10⁻²⁹² (astronomically significant)
- NMI = 0.185 (moderate)
- Marginal-preserving permutation null mean NMI = 0.070
- **Permutation null p = 0.13** (not significant at α=0.05)

The chi² p-value of 3.4e-292 is rejecting the WRONG null. Both C475_degree and C911_restriction correlate with token frequency: common MIDDLEs have higher compatibility-degree AND appear in more testing pools for PREFIX restrictions. The chi² test sees a structured contingency table and rejects independence, but doesn't account for the shared frequency dependency.

The 1000-permutation null (shuffling C911 restriction values across MIDDLEs while preserving their marginal distribution) gives the correct comparison: null mean NMI = 0.070, observed NMI = 0.185, **but the observation is reached or exceeded in 13% of permutations**. That's not significant exclusion.

The original constraint text was self-aware ("partially frequency-mediated, perm_null_p=0.13") but the Tier 2 status was too generous given the proper null.

**Diagnostic test for this failure pattern:**
1. Identify constraints that cite chi² p-values for coupling/dependency claims
2. Check whether both factors plausibly correlate with token frequency (or any shared marginal)
3. Look for whether a marginal-preserving permutation null is cited
4. If permutation null absent or perm_p > 0.05, the constraint is audit-eligible
5. Pattern: pre-PHASE_700 constraints in cross-layer / co-occurrence / coupling space are highest-suspicion

**How to apply:**
- When proposing new cross-layer coupling constraints: always run marginal-preserving permutation null, don't rely on chi² alone
- When auditing existing constraints: chi² p << 1e-10 with NMI ~0.1-0.2 is the warning signature — check if perm_p is reported and whether it crosses 0.05
- Cleanly-framed alternative: report effect size (NMI / Cramér's V) and perm_p separately. Don't let chi² p-value carry interpretive weight
- For tier classification: if perm_p > 0.05, claim is at best Tier 3 (suggestive measurement, no significance under proper null)

**Related methodology memories:**
- [[feedback-within-folio-shuffle-null-first]] (within-folio shuffle null discipline; sister test for adjacency claims — same family of "preserve marginal, shuffle assignment" nulls)
- [[feedback-made-up-threshold-audit]] (C131 audit — three-axis early-investigation diagnostic)
- [[feedback-denominator-choice-sparse-cooccurrence]] (C475 audit — N_possible vs N_attested denominator)
- [[feedback-aggregate-minus-original-independence-test]] (PHASE_705 — analogous for class-generalization claims)
- [[feedback-framework-as-null]] (mature-stage prior toward null)

**Broader audit policy implication:**
Per crazy-expert estimate, ~8-20 constraints in the C660-C1100 range share this signature (chi² p-value load-bearing while perm_p marginal). Add to the C475 audit-sweep target list. Grep heuristic: constraints with `chi²` or `chi2` in metrics, NMI/Cramér's V claims, registered pre-PHASE_700. Spot-check 5-10; if hit rate >40%, do the full sweep.

**Failure-mode taxonomy now spans three distinct patterns** (three audits this session, three different patterns):
1. C131 — invented threshold + non-reproducing value + null at observed (retract)
2. C475 — wrong framing/denominator + sparsity-driven headline (demote, strong-form survives in adjacent constraint)
3. C1068 — chi² p-value load-bearing while perm_p marginal (demote, methodology was sound, just wrong null reported as load-bearing)

Each is a distinct audit-shape worth its own diagnostic.

---

## feedback-denominator-choice-sparse-cooccurrence

*"In sparse co-occurrence graphs, denominator choice (N_possible vs N_attested) changes claims by orders of magnitude. \"X% of pairs are forbidden\" on sparse data is dominantly sparsity-driven unless max-expected-count among \"forbidden\" pairs exceeds ~5. C475 audit established (2026-05-19)"*

When a constraint reports "X% of pairs/triples/combinations are forbidden/illegal/incompatible," the denominator choice is the load-bearing methodological decision. Two denominators produce orders-of-magnitude different headlines on the same data:

**N_possible denominator:** count of all combinatorially-possible pairs in vocabulary V (= V × (V-1) / 2 for unordered pairs). This is what C475 used.

**N_attested denominator:** count of pairs that were actually observed at least once. This is what C729 used (and got 0/19,576 violations).

On sparse graphs, these denominators differ by factors of 10-50×. The N_possible framing artificially inflates "forbidden" counts because most unobserved pairs have null expectations below 1 at corpus size — they're not forbidden, they just haven't been seen yet.

**The C475 case study (2026-05-19 audit):**
- C475 reported: "95.7% of MIDDLE pairs are statistically illegal" (Tier 2)
- Methodology: pair "illegal" if observed=0 AND expected>0.5 under frequency-matched null
- Audit re-run: 309,740 illegal pairs (85.0% — minor discrepancy from 95.7%)
- **Max expected count among ANY of 309,740 "illegal" pairs: 2.51**
- Mean expected: 0.90, median 1.00, 99th percentile 1.08
- Pairs illegal at meaningful threshold (exp ≥ 5): **0**
- Under Poisson, observed=0 given expected=2.5 happens 8.2% of the time by chance

The "95.7%" was sparsity, not prohibition. C729's strong-form using attested denominator survived intact.

**Diagnostic test for this failure pattern:**
1. Identify the denominator the constraint cites ("X of N pairs/triples/combinations")
2. Ask: is N the count of POSSIBLE or ATTESTED?
3. If POSSIBLE and corpus is sparse: compute distribution of expected counts among the "forbidden" subset
4. If max expected count < 5 (or 99th percentile < 5), the claim is sparsity-dominated
5. Reframe to use attested denominator OR demote to descriptive statistic

**How to apply:**
- When auditing graph/co-occurrence-pattern constraints from sparse corpora (Voynich AZC, HT subsets, rare-MIDDLE strata): always check the denominator
- When proposing a new constraint: if the claim is "X% of possible pairs are forbidden," compute max expected count BEFORE registering. If below 5, use attested denominator instead
- Cleanly-framed alternative: "X violations across N attested pair occurrences" (C729-style). This is the methodologically defensible form
- Trap signature: the all-possible-pairs framing makes claims look stronger than they are — be skeptical of "95%+" exclusion rates on sparse data
- Frequency-matched null DOES NOT solve this — the null itself produces near-zero expectations for most pairs at sparse corpus size, so observed=0 vs null=0.5 isn't meaningful exclusion

**Related methodology memories:**
- [[feedback-made-up-threshold-audit]] (C131 audit — invented threshold + non-reproducing value + null at observed)
- [[feedback-within-folio-shuffle-null-first]] (within-folio shuffle null discipline; sister test for adjacency claims)
- [[feedback-aggregate-minus-original-independence-test]] (PHASE_705; analogous for class-generalization claims)
- [[feedback-framework-as-null]] (mature-stage prior toward null)

**Broader audit policy implication:**
Constraints from the 2026-01-08 through 2026-01-15 work burst (the AZC-graph + cross-system-compatibility development period) likely contain other instances of this denominator pattern. High-suspicion targets per crazy-expert: C153, C268, C476, C481, C517, C518, C982, C983, C996. Audit signature: any constraint citing a percentage of "possible" or "potential" pairs/triples on sparse data.

Expected outcome of audit-sweep: 5-15% retraction rate (per C131 + C475 precedent), 15-25% demotion rate (where strong-form survives in adjacent constraint like C729).

This is a generalizable methodological pattern, not a one-off finding.

---

## feedback-expert-audit-prevented-post-hoc-registration

*PHASE_730 within-A action-form — expert pre-registration audit caught six design flaws before running a post-hoc o-selectivity test that would have framework-echo-registered; B-side mirror + terminal-atom-matched null then independently killed the mechanism story*

PHASE_730 (2026-05-28) produced the cleanest demonstration so far of the expert-audit-before-running discipline working as designed. Worth preserving as a procedural reference.

**Sequence:**

1. Within-A action-form test (load-bearing on Finding 1 per crazy-expert's earlier recommendation): H1 PASS at 38.9% (A grammatically CAN host dy — falsifies architectural-tautology framing of original 95% state-form claim). H2 FAIL at p=0.51 (positional deployment not the axis). Pre-registered verdict AMBIGUOUS.

2. Post-hoc inspection of per-MIDDLE data revealed an apparent o-content split. User and I generated clean operational gloss: "A=setup, B=execute via arrangement-selective dy-completion."

3. **Critical step: requested expert audit on proposed pre-registered confirmation test BEFORE running it.** Expert-advisor and crazy-expert independently flagged six convergent design flaws:
   - Post-hoc fig leaf (yesterday's threshold filtered population; today's threshold partitions same population; partition chosen after seeing answer)
   - Cherry-picked descriptive split (kal, kche, ksh, lch, lsh violated "permissive=o-only" at descriptive level — I'd missed these)
   - Frequency confound + structural-domain confound (frequency-matched permutation null catches only count problem)
   - B-side mirror missing (load-bearing — if B also o-preferring, asymmetry framing dies)
   - HEAD vs ANY predicate ambiguity (predicate-fits-observation problem)
   - C1557 cross-check unaddressed (o-HEAD y-terminal depletion in B = opposite direction)
   - Framework-echo (claim restates C1395+C1502+C1556+C1559 with dy as readout, no new mechanism)

4. **Ran crazy-expert's recommended test (B-side mirror + terminal-atom-matched null) instead of locked confirmation test.**
   - B-side mirror: B symmetric across o vs non-o (Mann-Whitney one-sided p=0.62) → A asymmetry IS A-specific (good — kills the substrate-level alternative)
   - A o vs non-o raw: p=0.013 looks significant
   - **Terminal-atom-matched permutation null: stratified diff -0.016, p=0.71 → o-content effect COLLAPSES**
   - Diagnostic decomposition: o-HEAD MIDDLEs ALSO dy-suppressed in A (mean 0.026); o-non-HEAD MIDDLEs dy-permitted (0.420); no-o MIDDLEs suppressed (0.040)
   - Real driver: terminal-atom phonotactics, not o-atom content

**The expert audit prevented Tier 2 registration of what would have been the 5th framework-echo trap of 2026-05.**

**Procedural lesson:**

Before locking pre-registration on a post-hoc-observed pattern, REQUEST EXPERT AUDIT of the proposed test design — not just the constraint text. The audit should specifically check:

1. Was the test design generated by inspection of the data it will be run on? If yes → post-hoc fig leaf. Mitigation: held-out scope, OR honest demotion to descriptive Tier 3.
2. What is the simplest null that the proposed test does NOT control for? Run that null FIRST. Frequency-matched is rarely enough — try terminal-atom-matched, HEAD-position-matched, section-matched.
3. Where is the mirror test? If asymmetry is the claim, the SYMMETRY case must be tested. If A vs B, the B-internal control. If section A vs section B, the within-section confound check.
4. Does the predicate match the framework? "Contains X anywhere" vs "X at HEAD" vs "X at TERM" — these are different claims and pick different mechanisms.
5. Does the proposed Tier 2 claim text use existing operational vocabulary cleanly with no new mechanism? If yes → framework-echo flag.

**Generalizable rule:** when the operational story (the words you'd use to explain it to a non-specialist) slots cleanly into existing framework vocabulary at this project stage (~2050 constraints), increase pre-registration discipline by one level. Expert audit on the design BEFORE running, not just on the registration text AFTER running.

**Two distinct expert roles validated as complementary:**
- Expert-advisor caught: post-hoc threshold-as-fig-leaf, frequency confound, predicate ambiguity, C1557 conflict, scoping
- Crazy-expert caught: B-side mirror missing (load-bearing), terminal-atom confound (not frequency), kal-typo data integrity, the "30% A-corpus proportion vs passive-registry framing" puzzle

Either alone would have missed something the other caught. Using both in parallel for design audit is the high-EV pattern.

Related: [[feedback-framework-as-null]] (the underlying discipline), [[feedback-five-mechanism-traps-may-2026]] (cumulative trap pattern this is #5 of — see PHASE_730 INDEX for full list), [[feedback-expert-predictions-are-pre-registrations]] (when experts make directional predictions, they're pre-registrations not facts; this case extends that to "when experts audit a design, they're pre-screening for confound discovery, not validating").

---

## Expert mechanism predictions are pre-registrations, not Tier 3 facts

*When an expert (yours or theirs) makes a directional structural prediction with confidence rating, that's a pre-registered discriminating test, not a load-bearing fact. Run it before treating the mechanism as scaffolding for downstream work. Two cycles documented (2026-05-15 to 2026-05-16): user's f66r-as-glossary overclaim caught by discriminating test; crazy-expert's positional-artifact prediction misfired with 70-30 confidence on late_term clustering, caught by the same discipline.*

## The rule

When an expert (the expert-advisor or crazy-expert agent, OR the user, OR yourself in
synthesis mode) makes a directional structural prediction with a confidence rating like
"70-30 X collapses under Y," that prediction is a **pre-registered discriminating test**,
not a Tier 3 mechanism fact.

- Run the test before using the prediction as scaffolding for downstream investigation.
- Treat the prediction's failure or confirmation as data, not as expert mispredition or
  confirmation per se.
- The same framework-as-null discipline that catches initial registration overclaims
  applies to expert mechanism predictions.

## Why

Two cycles documented in successive sessions:

**Cycle 1 (2026-05-15)**: I (user prompting) registered C1993 (f66r-as-glossary) on a
clean operational story built from existing atom-gloss vocabulary. Discriminating test
(M-marker dominance on cross-referenced labels) failed 0/4 top-1. C1993 retracted same
session. The framework-as-null discipline caught my overclaim.

**Cycle 2 (2026-05-16)**: Crazy-expert proposed (70-30 confidence) that the +0.038
late_term Voynich-wide adjacency excess was line-position artifact — "LATE-class tokens
land at line-finals per C539; clustering is driven by cross-line co-occurrence at
line-boundaries; within-line shuffle will collapse it to <+0.005." Within-line shuffle
test: late_term excess **+0.0365 (delta only +0.0026 vs within-paragraph)**. Genuine
adjacency, not positional. **Crazy-expert's confident structural prediction was wrong.**

Both cycles used the same methodology (pre-registered binary thresholds, run the test,
verdict follows mechanically). Both caught overclaims that fit existing operational
vocabulary cleanly.

## How to apply

**When an expert proposes a mechanism interpretation with confidence (70-30, "I bet X
collapses," "almost certainly Y"):**

1. **Treat as pre-registration.** The prediction is a falsifiable directional claim.
2. **Design the discriminating test before running it.** If the expert proposed the test
   structure ("within-line shuffle should collapse this"), use their test design.
3. **Lock thresholds before running.** What constitutes "collapse" vs "survives"? The
   expert's confidence rating implies a binary threshold — use it.
4. **Run the test promptly.** Don't let the prediction sit as load-bearing scaffolding
   for downstream work. Expert speculation is cheap; running the actual test is the
   bottleneck.
5. **Update the registration plan based on the test result.** A failed expert prediction
   is a clean discriminating control that sharpens the registration. A confirmed
   prediction adds corroboration.

**Specific anti-patterns this prevents:**

- **Cascading expert mechanism scaffolding.** Expert A proposes mechanism M for finding F.
  Expert B builds interpretation I on M. Without testing M, I inherits M's epistemic
  status (which is "untested speculation," not "validated mechanism").
- **Asymmetric trust by expert source.** Treating crazy-expert speculation as "weak prior"
  but expert-advisor speculation as "validated mechanism" — both are speculation until
  tested.
- **Letting expert confidence ratings substitute for test results.** "70-30 X" is a
  pre-registration, not a probability the proposed mechanism is true. The test is
  the probability.

## Why this matters at the current project stage

The project has ~2025 constraints. Expert agents now have rich operational vocabulary
loaded into their context. The same framework-as-null trap that catches user
registrations also catches expert speculations — both can build coherent operational
stories using the existing vocabulary without testing the mechanism.

The discriminating-test discipline is the protection. It applies to both sources of
speculation, regardless of which agent produced the candidate mechanism.

## Procedural codification

When consulting an expert and they offer a confident structural prediction:

```
Expert says: "X will Y under Z, confidence W%"
↓
Treat as: Pre-registered prediction with W% prior
↓
Action: Design test of Z, lock threshold for "collapse" vs "survives," run.
↓
If prediction confirmed: registration plan can use mechanism as load-bearing
If prediction failed: prediction is data (a clean negative discriminator), not
  mechanism. The structural fact survives or doesn't on its own merits.
```

## See also

- `feedback_operational_story_first_trap.md` — the original framework-as-null formalization
- `feedback_framework_as_null.md` — sharper framework-as-null discipline (2026-05-15)
- C1993 retraction narrative — Cycle 1 example
- C2027 retraction narrative — Cycle 2 example (crazy-expert prediction misfire)
- `phases/RECIPE_FOLIO_CORRESPONDENCE/results/c2027_two_discriminating_tests.json` — the test that falsified crazy-expert's prediction

---

## feedback-floor-vs-discriminator-metric-test

*"Before treating any new literature-borrowed statistical metric as an NL-discriminator, test a known non-NL structured-symbolic system (e.g., mensural notation) for floor-passing. If the non-NL system passes the metric's NL threshold, the metric is a floor (structured-vs-random), not a discriminator (NL-vs-non-NL). PHASE_706 established (2026-05-19)"*

When importing a statistical metric from the language-stats literature with the intent of testing whether Voynich is "natural-language-like," **always run the metric on a known non-NL structured-symbolic system first**. If that non-NL system passes the NL threshold, the metric is a **floor** (separating structured from random), not a **discriminator** (separating NL from non-NL structured systems).

Voynich passing a floor metric tells you "Voynich is structured-symbolic with topical organization" — which we already know. It does NOT tell you "Voynich is NL-like."

**The PHASE_706 case study (2026-05-19):**

Two literature-borrowed metrics tested:

| Metric | Reference | Threshold (NL-like) |
|--------|-----------|---------------------|
| Burstiness β (Weibull shape on inter-arrival times) | Altmann et al. 2009 PLOS ONE | β < 0.85 |
| DFA Hurst H on token-length time series | A Story of the Stone PLOS ONE | H > 0.55 |

Both metrics passed sanity floors (random null gives β≈1.0, H≈0.5; NL Latin Codicillus/Mesue/Brunschwig all pass NL thresholds).

Voynich Currier B results:
- β = 0.769 (inside NL Latin range 0.69-0.77, sanity floor passing)
- H = 0.652 (inside NL Latin range 0.60-0.70, sanity floor passing)

These looked like strong NL-like signals. But the **mensural notation control** (which is NOT NL — already falsified at C2032 cross-language test, 2026-05-16) showed:
- Mensural β = 0.653 (passes NL threshold with room)
- Mensural H = 0.823 (passes NL threshold with room above NL range)

**Mensural notation — a confirmed non-NL system — passes both NL-thresholds.** Therefore β and H are floors for any structured-symbolic system with topical/sectional organization. Voynich passing them is "Voynich is structured-symbolic," NOT "Voynich is NL."

**The discriminating test that ACTUALLY worked: C2032 (lag2/lag1).** Mensural at C2032 gives +0.18 (within NL Latin range). Voynich Section B gives -0.66 (extreme NL-divergence). C2032 cleanly separates Voynich from BOTH NL and mensural. That's a discriminator.

**Diagnostic test:**
1. Identify the candidate metric (e.g., burstiness β, Hurst H, MTLD, etc.)
2. Identify a CONFIRMED non-NL structured-symbolic system (mensural notation is the project's go-to; any structured non-language with topical organization works)
3. Run the metric on the non-NL system
4. **If non-NL passes NL threshold**: the metric is a FLOOR. Voynich passing it adds no information about NL-vs-non-NL.
5. **If non-NL fails NL threshold**: the metric is a DISCRIMINATOR. Voynich passing it is informative.

**Existing project discriminators (confirmed):**
- **C2032 lag2/lag1**: mensural +0.18 vs Voynich Section B -0.66 — clean discriminator
- **C2015 char-LM compression**: per `engineered_substrate_triad.md` calibration lesson, this is a FLOOR (mensural passes 1.857 bpc, within NL range 1.0-3.0). Use as exclusion gate only.
- **C2022 Markov plateau order**: per same lesson, this is a FLOOR (mensural plateau order = 2, within NL range 2-3). Use as exclusion gate only.

So even within the project's "substrate quintet," only C2032 actually discriminates. The other axes are floors. This was already documented in `engineered_substrate_triad.md` (2026-05-16 calibration lesson) but PHASE_706 establishes the **general principle** that floor-vs-discriminator testing is required for ALL imported literature metrics.

**How to apply:**
- When proposing new NL-detection metrics from literature, always include mensural notation (or another confirmed non-NL structured benchmark) in the comparison BEFORE interpreting Voynich result
- If the candidate metric is a floor, do NOT register Voynich-passing as "NL-like." Register as "structured-symbolic" at most
- Pre-register the floor-vs-discriminator check as a sanity criterion: "metric must fail on mensural notation to be considered a discriminator"
- If only floors are available, the test is uninformative for the NL-vs-non-NL question

**Connection to existing methodology lessons:**
- Refines `feedback_registration_calibration_lesson.md` (PHASE_698 mensural lesson) — that memory established that ONE specific axis (C2032) was the only discriminator. PHASE_706 generalizes the principle to ALL imported metrics.
- Complements `feedback_calibrate_thresholds_against_controls.md` (PHASE_697) — calibrate against in-distribution controls. PHASE_706 adds: calibrate against the alternative-class baseline too.
- Sister to `feedback_specific_vs_tautological_predictions.md` (PHASE_698) — distinguish floors from discriminators in pre-registered criteria.

**Failure-mode taxonomy update — 6 patterns:**

| # | Pattern | Diagnostic |
|---|---------|-----------|
| 1 | Invented threshold (C131) | non-reproducing value + null at observed + made-up threshold |
| 2 | Wrong denominator (C475) | N_possible vs N_attested on sparse graph |
| 3 | Wrong null test (C1068) | chi² against independence null with frequency-correlated factors |
| 4 | Broken baseline (C476) | null/baseline algorithm artifact doesn't represent alternative |
| 5 | Post-hoc claim-substitution (C481) | writeup labels VALIDATED while script JSON verification field reports False |
| 6 | **Floor metric mistaken for discriminator (PHASE_706)** | **Literature metric passes for structured-symbolic non-NL systems; Voynich passing it is uninformative about NL-likeness** |

**PHASE_706 takeaway:**
- No new constraint registered (β/H are floors, not informative for the question asked)
- Methodology lesson saved (this memory)
- Voynich exhibits expected structured-symbolic content clustering at folio level (~95% of β/H signal preserved by within-folio shuffle, consistent with folio=program framework)
- Substrate quintet's "non-NL" framing survives intact via C2032 which IS a discriminator (mensural fails it at +0.18 vs Voynich -0.66)
- PHASE_706 closes as INDEX-only; the productive output is this generalizable methodology principle

---

## At mature-framework stage, treat framework-fit as prior toward null (2026-05-15)

*When a finding fits existing tier-2 operational glosses cleanly, the operational vocabulary itself can produce the appearance of signal. New findings that slot neatly into existing framework deserve MORE skepticism, not less. Sharper than "run controls earlier."*

**The principle:**

The project has ~2000 constraints, six tiers, mature operational vocabulary (atom glosses per C1195, channel taxonomy per C1394, PREFIX classes per C1300/C1313/C1316/C1962, etc.). At this stage of a research program, **framework-fit is no longer evidence of confirmation — it's evidence of confirmation bias**.

The framework gives new findings a place to land. When a new pattern can be told as a clean operational story using existing vocabulary, that cleanness is partly the framework matching itself, not the data matching the framework.

**Why:** Crazy-expert formalization 2026-05-15 after f66r-as-glossary collapse (4th operational-story-first trap in one session window):

> "When a finding fits existing tier-2 operational glosses (C1195, C1394, C1300, etc.) and uses their interpretive language, treat the existing fit as a prior toward null — the operational vocabulary itself might be producing the appearance of signal in the data. This is the harshest form of 'framework as null' and I haven't been applying it. The strongest discoveries late in a research program are usually the ones that don't fit cleanly."

**How to apply:**

- **Vocabulary check:** If the proposed interpretation can be stated entirely in existing atom glosses, channel labels, and operational class names (qokedy=cycle, ch=adjust, sh=passive-monitor, etc.) without introducing new mechanism, it's probably a vocabulary echo, not a discovery. The vocabulary IS the hypothesis at this stage.

- **Surprise test:** Does the finding require something NEW (a new mechanism, a new constraint, a new structural relationship)? If everything in the finding was already nameable in the existing system, increase skepticism.

- **Three Outs procedural rule** (crazy-expert formalization):
  1. "What would this look like if I were wrong?" — Articulate the specific discriminating test in one sentence. If you can't, you're story-building.
  2. "Is my classification post-hoc?" — If the units being classified were selected based on the property being tested, the test is circular.
  3. "Does my framework predict the right SIZE of effect?" — Operational mechanisms predict large effects. Marginal p-values with operational stories should trigger within-folio shuffle null as control #1, not as a later check.

- **Cooling period** (expert-advisor formalization): When a structural anomaly survives a permutation null, do NOT propose an operational constraint in the same session. Enumerate simplest non-operational explanations first. Design discriminating test before writing operational interpretation.

**Discriminating-test orientation:**

The right pre-registration order:
1. Structural anomaly survives null test → register as Tier 2 anomaly fact (no interpretation)
2. STOP
3. Enumerate non-operational explanations
4. Design test that distinguishes anomaly from operational story
5. Run test
6. ONLY after test passes, propose operational interpretation at appropriate tier

**Concrete instances where this would have helped:**

- **C1993 / f66r-as-glossary:** Operational story (3-column glossary, atom-classifier M-column, named-procedure L-labels) was built on Tier 2 structural anomaly (C1992) before discriminating test. Discriminating test (M-marker dominance on cross-referenced labels) failed 0/4 top-1 when run later. The story used entirely existing vocabulary (atom glosses, prefix classes, operational types) — no new mechanism. Should have triggered framework-as-null skepticism.

- **C1965/C1988 cardinality generalization:** Individual anchors at f75r×4/×9 and f103r×8 are real (Tier 2 / individual Tier 3). The systematic "cardinality counting framework" generalization was framework-echo — assumed all matched recipes encode cardinality via similar mechanisms. Within-folio shuffle null killed it (mean z=+0.18 across matched folios). Memory note `project_cardinality_anchors_dont_generalize.md` records this correctly.

- **C1971 cluster readings:** 15/15 qualitative coherence claims used same atom-gloss dictionary at multiple scales — tautological confirmation. The vocabulary IS what fit; the data didn't independently validate.

**The trap pattern recurs because the framework rewards the trap:**

The more mature and consistent the framework, the easier it is to tell coherent operational stories about new data. The cleaner the story, the more it feels like discovery. The same vocabulary that enables description also enables overfitting.

**At this stage, registration discipline must include:** show what mechanism this finding requires that's NOT already in the framework. If the answer is "none — it's a clean fit," that's the warning, not the proof.

**Where this points:**

- New high-confidence findings late in the project lifecycle are most likely either (a) negative results / falsifications, (b) findings that introduce new structural relationships outside existing atom/channel vocabulary, or (c) findings that genuinely challenge an existing constraint. "Yet another clean operational story" is the lowest-EV category.

- Audit existing Tier 3 constraints for trap signature: was the operational interpretation registered before or after the discriminating test? If before, it's a candidate for re-audit even if currently uncontested.

**Related notes:**
- `feedback_operational_story_first_trap.md` — the original trap pattern
- `feedback_within_folio_shuffle_null_first.md` — what to run as control #1
- `feedback_measurement_vs_mechanism.md` — measurement is not the same as mechanism inference
- `feedback_atom_gloss_word_salad.md` — atom-decompositions read as word salad and shouldn't be primary evidence

---

## feedback-long-running-scripts-need-flush-and-interim-writes

*"Any script with expected runtime >5 min must use flush=True on per-iteration prints AND write interim JSON results, not just final. Otherwise zero visibility during 1-3 hour runs."*

PHASE_732 batch 2 audit (2026-05-28) ran for ~3 hours with **zero output visibility** — Python's stdout is block-buffered when redirected, and the script only wrote its JSON output at termination. User had to ask "how's it doing" multiple times across hours with only "CPU time climbing" as a signal.

## The fix is trivial

For any script with expected runtime >5 min:

1. **Use `print(..., flush=True)` on per-iteration prints.**
   ```python
   print(f'{i:>3} {pair_name:>20} {result:.4f}', flush=True)
   ```

2. **Write interim JSON after each iteration**, not just at the end:
   ```python
   for pair in pairs:
       result = audit_pair(pair)
       dispositions[pair.name] = result
       out_path.write_text(json.dumps(dispositions, indent=2))  # after EACH pair
   ```
   Costs ~1 ms per write (small JSON). Benefit: full crash-resilience + ability to read partial results.

3. **Optionally, log to a sidecar progress file** with timestamps:
   ```python
   with open('progress.log', 'a') as f:
       f.write(f'{time.time():.0f}: completed {pair.name} -> {result}\n')
   ```

## When this matters

- Any audit batch with N synthetic corpora >= 1000
- Any reverse-blind / matching test running across multiple folios
- Any 5-gram null with stratified N
- Any script you'd launch with `run_in_background: true`

## When it doesn't matter

- Scripts under 1-2 min total runtime (Python's atexit handlers flush)
- Pure data-load scripts (no iterative output to track)

## Cost-benefit

Adding `flush=True` and interim JSON writes is essentially free in development time and runtime cost. Skipping them costs hours of monitoring uncertainty when running a 1-3 hour batch.

## What this changes for future audits

All batch-runner scripts in `phases/PHASE_***_AUDIT_BATCH_*/scripts/` should:
- Use flush=True on per-iteration prints
- Write interim JSON after each constraint/pair (not just final)
- Optionally include a sidecar `progress.log` with timestamps

Apply retroactively if creating new batches; do NOT modify scripts mid-run (would invalidate locked pre-registration).

## Related memories

- [[feedback-mechanism-cycle-procedural-ceiling]] (audit batches are part of the procedural cycle; runtime hygiene is part of the discipline)

---

## feedback-made-up-threshold-audit

*"Three-part diagnostic for early-investigation Tier 2 constraint audit — (1) threshold provenance (cited or invented), (2) value reproducibility under current pipeline, (3) effect above within-line shuffle null. C131 failed all three; retracted (2026-05-19)"*

When auditing an early-investigation Tier 2 constraint (especially pre-2026-02 / pre-v2.42 era), apply this three-part diagnostic:

**(a) Threshold provenance:** Is the binary-classification threshold cited from a source (NL corpus baseline, validated reference value, peer-reviewed prior work) or invented for this test? Smoking gun for invented: source code contains threshold-adjustment comments like `# Adjusted threshold` set to a different value than the framing claims. C131's Phase X.5 source contains `# DSL signal if role consistency > 0.8` followed by `# Adjusted threshold` set to 0.5 — even before producing the verdict, the threshold was being adjusted post-hoc.

**(b) Value reproducibility:** Does the numerical value reproduce when re-run with current pipeline (H-only filter, post-v2.42 transcript handling, current constraint set)? A 2× discrepancy is the diagnostic signature of the pre-v2.42 transcriber filter bug (3.2× token inflation when non-H tracks were inadvertently included). C131's original 23.8% does not reproduce — current re-run gives 12.2%, half the original value.

**(c) Effect above within-line shuffle null:** Does the observed value exceed within-line shuffle null with z > 2? Within-line shuffle is the load-bearing first control per `feedback_within_folio_shuffle_null_first.md`. C131's 12.2% sits at null mean 12.0% with z = +0.69 — at noise floor.

If ALL THREE answers are negative (invented threshold + non-reproducing value + null at observed), the constraint is **retraction-eligible**, not demotion-eligible. Demotion preserves a measurement that has no informational content beyond the null; retraction with audit narrative is cleaner.

**Why retract not demote:** A Tier 3 constraint should be a real measurement at thin evidence or interpretation-tier candidate. A measurement at noise floor under proper null is not a Tier 3 finding — it's a methodologically-invalidated claim. Demotion misleads future readers into treating the metric as informative; retraction with narrative preserves the audit precedent.

**Implications for audit policy:**
- Pre-2026-02 Tier 2 constraints whose values are load-bearing (specific numbers crossing specific thresholds) are audit-eligible
- Constraints whose claims are "X correlates with Y" or "X is structurally distinct" are less vulnerable to the transcriber bug
- Expected retraction rate from systematic audit: 5-15% (crazy-expert estimate based on C131 being the first)
- Scope as routine maintenance, not multi-week phase — batch 3-5 retractions per commit
- Triage candidates: constraints citing absolute counts or rates from pre-v2.42 phases

**Connection to existing methodology lessons:**
- Distinct from `feedback_calibrate_thresholds_against_controls.md` (pre-registration calibration discipline) — that's about NEW threshold design; this is about OLD threshold audit
- Distinct from `feedback_framework_as_null.md` (mechanism interpretation overclaim at mature stage) — that's late-stage; this is early-stage
- Complements `feedback_within_folio_shuffle_null_first.md` (the load-bearing null discipline that catches this pattern)
- Complements `feedback_n_matching_for_within_scribe_comparisons.md` (N-matching as analogous late-stage discriminating control)

**The C131 case study:**
- Original (Phase X.5, ~Dec 2025): "Role consistency LOW (23.8%, threshold >80%)" — Tier 2 falsifier of DSL/language hypothesis
- Audit (2026-05-19): all three diagnostic axes failed
- Retraction outcome: Tier 1 with full audit narrative. Zero downstream collateral — language falsification independently supported by C130 (0.19% reference rate, 26× threshold separation, much stronger), C132, C173, substrate quintet, kernel architecture. C131 was always the weakest evidential leg in the language-falsification chain.
- Pattern parallel: C2027 retraction (heat-cycle adjacency framing falsified within 24h by family-stratified shuffle null) — same registration-overclaim-caught-by-discriminating-control structure.

---

## Cross-tier / decomposed information-theoretic measurements are observations, not mechanisms

*When a measurement (cross-tier MI z, autocorrelation tier collapse, residual-after-control, etc.) shows a pattern, the mechanism interpretation is a SEPARATE testable claim that requires its own pre-registered test. Phase 688 → 689 case: cross-tier MI z=−0.20 for qotar got labeled "morphological clustering" without testing whether adjacents are actually morphologically related (Phase 689 found same-stem density 1.7%, refuting the inference).*

**Rule:** Information-theoretic decomposition results (cross-tier MI, autocorrelation by stem-locality tier, conditional entropy stratifications, residual-after-control measurements) are MEASUREMENTS. The mechanism interpretation is a separate testable claim and requires its own pre-registered test before registration.

**Why:** Phase 688 measured qotar's cross-tier MI z and found −0.20 (collapse from overall +3.95). The intuitive interpretation was "morphological clustering" — qotar's high MI is qo-family co-occurrence around it. Phase 689 directly tested this and falsified it: qotar's same-stem density is 1.7%, not the 30%+ a morphological-clustering mechanism would predict. The cross-tier collapse measurement is real; the inferred mechanism was wrong.

**The pattern that creates this trap:**
- A novel decomposition produces a striking measurement
- The author has an intuitive interpretation ready (often the "obvious" reading)
- Pre-registration gets done on the measurement, not the mechanism
- The interpretation gets attached to the constraint as if it were tested
- A follow-up phase reveals the mechanism is something else

**How to apply:**
- When a decomposed measurement reveals something interesting, write down the inference SEPARATELY from the measurement before registering
- If the constraint claims a mechanism (X clusters because Y), the mechanism must be pre-registered and tested directly
- A measurement-only Tier 2 constraint should NOT include mechanism interpretation in the constraint text — only in the auxiliary narrative, clearly labeled as interpretation
- If you write "X is Y" where Y is a mechanism (clusters morphologically, propagates context, resets state), check whether you've actually tested Y or just measured something Y would also produce

**Examples of measurement-mechanism conflation in our project:**
- Phase 686 C1998: INFRA tokens have higher H_succ than RI was framed as INFRA-naming-misleading. The INFRA classification is structural; "infrastructure glue" was a mechanism inference that wasn't directly tested.
- Phase 687 C2000: daiin's MI z=+0.76 above median was framed as state-flush rejection. The "state-flush operator" was a mechanism inference; the test measured MI propagation (a related but distinct property).
- Phase 688 C2001 auxiliary: qotar's cross-tier z=−0.20 was framed as "morphological clustering." Phase 689 falsified.
- Phase 685 C1995: Section S = "operational compactness" was framed via three-tier near-relative dominance. The "compactness" interpretation IS a mechanism inference — it survived the three-tier test but wasn't directly tested at the operational-semantic level.

**The specific cross-tier MI case:**
- Cross-tier MI z = "MI conditional on (prev, next) being from operationally distinct token families"
- LOW cross-tier z does NOT mean "morphological clustering"
- LOW cross-tier z means "this token's predictive power requires same-family adjacency"
- WHY same-family adjacency matters needs separate test (same-stem density, family pooling, recipe positional, etc.)

**Red flag for future phases:** if the constraint text contains "X clusters by Y" or "X functions as Z" without a specific test of the Y/Z mechanism, the constraint is conflating measurement with mechanism. Either reword to remove the mechanism claim, or add a pre-registered mechanism test.

**Connection to existing constraints:**
- C1995 (S operational compactness) — was tested via three-tier near-relative test; the "operational" interpretation is grounded in the test, but the deeper mechanism (WHY S has dense same-stem runs) is a Tier 3/4 question
- C2002 (qotar mechanism FALSIFIED) — direct application: pre-registered mechanism, test failed
- C1998, C2000 — earlier examples of measurement-mechanism conflation in this same metric family

---

## Mechanism-discrimination cycle has a procedural ceiling — Tier 2 measurement / Tier 3 interpretation requires external grounding

*Today's session (2026-05-16) demonstrated a tight 3-hour mechanism-discrimination cycle (surface measurement → mechanism candidate → discriminating tests → sharpened mechanism → controls). Pattern reached methodological ceiling. Structural measurements reliably promote to Tier 2 with framework-as-null discipline + pre-registered binary criteria + within-folio shuffle null. But operational interpretations cannot exceed Tier 3 within the current procedure — they require external grounding (physical reconstruction, external corpus alignment, or independent source attribution) to promote to mechanism-tier facts.*

## The pattern

Across 2026-05-15 to 2026-05-16, the following discrimination cycle was applied multiple times:

1. **Surface measurement** observed (e.g., +0.0037 autocorr excess in matched-S, narrow-heat-cycle MIDDLE adjacency clustering)
2. **Operational mechanism candidate** proposed using existing framework vocabulary (e.g., "iteration encoding," "phase-switching," "sustainment")
3. **Discriminating tests** designed with pre-registered binary criteria
4. **Tests run; sharpened mechanism** emerges (e.g., "Section B operational tokens period-2 modulate e-depth; matched-S operational tokens are flat")
5. **Mandatory controls** (within-folio shuffle null, AX/operational decomposition)
6. **Refined measurement** registered at Tier 2; **operational interpretation** logged at Tier 3 in SPECULATIVE/

The cycle compressed from ~days (e.g., Phase 685 → 685-revised over weeks) to ~hours (single session). This is the framework-as-null discipline working at high velocity.

## The procedural ceiling

The cycle reliably produces:
- Tier 2 structural measurements (e.g., C2028, C2030, C2031)
- Tier 1 retractions of overclaimed mechanism interpretations (e.g., C2027)
- Tier 3 candidate operational interpretations in SPECULATIVE/

It **does NOT** produce Tier 2 mechanism-level claims. The reason: operational interpretation using existing framework vocabulary is framework-echo-suspect by construction (per `feedback_framework_as_null.md`). Even after discriminating tests, the gloss can be re-stated in multiple admissible operational readings, and the data alone cannot select among them without external grounding.

## External grounding paths to break the ceiling

Per crazy-expert consult 2026-05-16: "structural measurements promote to Tier 2; mechanism interpretations require physical reconstruction or external corroboration to exceed Tier 3."

Specific paths identified:

1. **Physical reconstruction**: Build the candidate apparatus (e.g., pelican alembic for reflux interpretation), run actual process, measure e-depth-equivalent control parameter, compare to Voynich pattern. Requires lab work + apparatus + cost.

2. **External corpus alignment with discriminating signature**: If trajectory-encoded vs instruction-encoded interpretation is real, test on Codicillus alchemy Latin (trajectory-expected) vs Mesue's Grabadin Latin (instruction-expected). If e-depth-analog period-2 appears in Codicillus operational verb sequences but not in Mesue compound preparations, interpretation strengthens. Requires source-side feature extraction tooling.

3. **Independent methodology cross-corroboration**: Multiple orthogonal measurements hitting the same operational target. C2027's atom-level + C1969's anchor-level + C1953's marker-level + today's class-adjacency level was the pattern that nearly worked — but the operational gloss still got demoted because all methodologies use the same framework vocabulary. Need a fundamentally different evidence class.

## How to apply

**During mechanism-discrimination cycles:**

- Run discriminating tests with pre-registered binary criteria. Both experts have learned to call these specifically.
- Register the surface measurement at Tier 2 within the same session if it passes the controls.
- Log the operational interpretation at Tier 3 in SPECULATIVE/.
- DO NOT register operational interpretation at Tier 2 within the same session as the measurement. Per `feedback_framework_as_null.md` 2026-05-15 sharpening.
- Document in the Tier 3 SPECULATIVE note: what would PROMOTE the interpretation to Tier 2 (the specific external-grounding test).

**At session-end:**

- If the day produced 2-3 Tier 2 measurements and 1-2 Tier 3 interpretations, that's the expected output rate of this procedure at the current project stage.
- If the day produced ANY Tier 2 mechanism-level claim using only existing framework vocabulary, re-audit with framework-as-null discipline. It's almost certainly overclaim.

**Strategic implication:**

If the project's next high-EV moves are at the operational-interpretation level (not the structural-measurement level), they require external grounding investments. The 3-hour cycle has reached diminishing returns for mechanism validation within the current framework. Internal-only mechanism work will produce Tier 3 candidates indefinitely.

This is consistent with `project_8d_features_redetect_regime_internal_frontier.md` (2026-05-15): "Strategic conclusion: don't run Phase 696. Next high-EV moves are external (acquire Antidotarium Nicolai / Mesue's Grabadin) or consolidation (synthesis writeup). Internal probing has hit diminishing returns."

## Session 2026-05-16 cycles documented

**Cycle 1 (morning):** C2027 retraction → C2028 measurement registration via family-stratified shuffle null. Crazy-expert's discriminating test fired before downstream work.

**Cycle 2 (afternoon):** C2031 candidate mechanism (sustain-vs-alternate) → multi-lag autocorrelation test passes pre-registered criteria 3/3 + 3/3 → alternation-slot follow-up reveals "phase-switching" framing wrong → e-depth sharper candidate proposed → e-depth oscillation test passes cleanly → within-folio shuffle null + AX/operational decomposition controls pass → asymmetric mechanism (Section B operational period-2 + matched-S operational flat) refined and registered at C2031 measurement-only. Trajectory-vs-instruction encoding interpretation deferred to SPECULATIVE.

Three retraction/registration events in 24 hours. Procedure scaling demonstrated.

## See also

- `feedback_operational_story_first_trap.md` — the original framework-as-null trap pattern
- `feedback_framework_as_null.md` — 2026-05-15 sharpening
- `feedback_expert_predictions_are_pre_registrations.md` — expert mechanism predictions discipline
- `feedback_within_folio_shuffle_null_first.md` — mandatory control #1
- C2031 registration body
- `SPECULATIVE/encoding_modes.md` — Tier 3 interpretation candidate from today
- `project_8d_features_redetect_regime_internal_frontier.md` — strategic context

---

## feedback-n-matching-for-within-scribe-comparisons

*"N-matched downsample controls are mandatory for substrate-metric comparisons across data subsets; bootstrap-ratio noise + N asymmetry produces framework-fit false positives (PHASE_702, 2026-05-19)"*

For substrate-metric comparisons (lag1, lag2, r21, e-depth autocorrelation) across data subsets where subset sizes differ, N-matched downsample controls are load-bearing — not optional.

**Why:** PHASE_702 within-Scribe-2 content comparison produced z = −2.05 on lag2−lag1 between botanical Q4-7 (N=2,296) and balneology Q13 (N=6,166). The raw z marginally cleared 2.0 and was framed as content-driven substrate flip — exactly the registration-overshoot pattern. Expert-advisor insisted on N-matched downsample control. After downsampling balneology to 2,296 (botanical's N) repeatedly, median z dropped to +1.73 with 80% CI [+0.89, +2.68] crossing zero. **The original z=−2.05 was driven entirely by the 2.7× N imbalance**, not by genuine content difference.

Same session's cross-scribe botanical test (Scribe 2 vs Scribe 3 botanical) showed N-matched median z = +0.47 (N-driven artifact). Matched-S vs unmatched-S within Q18 also collapsed under N-matching (median z = −0.42).

**Three failures in a single test session, all caught by N-matching.** Without the control, PHASE_702 would have registered "substrate signature is content-driven" as Tier 2 mechanism — false.

**How to apply:**
- When comparing substrate metrics (or any autocorrelation-based measurement) across subsets of differing N, ALWAYS include N-matched downsample as a control before locking interpretation
- Bootstrap-ratio metrics like r21 = lag2/lag1 are particularly fragile — they explode when lag1 samples near zero, inflating within-group variance
- Default: downsample the larger subset to the smaller's N, repeat ≥20 times with different random samples, report median z and 80% CI
- Decision rule: if N-matched 80% CI on z crosses zero, the raw finding is N-driven artifact regardless of how clean the raw z looks
- A z just above 2.0 with N asymmetry > 1.5× is the diagnostic signature of this trap

**Combined with `feedback_framework_as_null.md`:** N-matching is the discriminating test that distinguishes framework-echo from real signal when a finding fits the project's existing operational vocabulary too cleanly. This is the 5th documented case in 2026-05 of the framework-as-null discipline catching a registration overshoot.

Related: [[feedback-framework-as-null]], [[feedback-calibrate-thresholds-against-controls]], [[feedback-within-folio-shuffle-null-first]].

---

## feedback-no-time-or-fatigue-framing

*"Never invoke time, duration, or fatigue (\"we've been at this a while\", \"good stopping point\", \"it's late\", \"long session\", \"fresh next session\"). No concept of elapsed time — these framings are invented and annoying. User decides when to stop."*

# Never invoke time, duration, or fatigue

## Rule

Do NOT say any of: "we've been at this a while," "this is a good/natural stopping point," "it's late in the evening," "long session," "we've done a lot today," "pick this up fresh next session," "marathon," or any variant that references elapsed time, accumulated effort, or fatigue.

## Why

I have no concept of elapsed wall-clock time, how long a task took, what time of day it is, or whether the user is tired. Every such framing is invented — I'm pattern-matching to "this conversation has many turns" and converting it into a fake time/fatigue claim. The user finds it annoying and it's never accurate.

## How to apply

- The user decides when to stop and will say so explicitly ("I'll tell you when it's time to stop").
- Present next-step options purely on their merits: expected value, risk, what open question they resolve, what they cost in compute/tokens. Never on imagined time spent or effort expended.
- When offering "run now vs later," frame it as "resolve X now vs bank progress and continue" — a logical sequencing choice, NOT "we've done a lot, maybe stop." Drop the fatigue subtext entirely.
- "Number of turns in the conversation" is not evidence of elapsed time. A long thread might be minutes. Don't infer duration from turn count.

## Scope

This is a permanent communication-style rule, added to `C:\git\voynich\CLAUDE.md` under Communication Style (2026-05-28). Applies to all conversation with the user.

---

## Operational-story-first, controls-second is the dominant trap pattern when registering co-occurrence findings

*When a finding "fits the existing framework cleanly," that is a warning sign and not a confirmation. Four traps now documented (2026-05-11/12/13/15). The control burden scales with the coherence of the operational story. The framework itself produces apparent signal in mature research programs.*

When a finding fits the project's existing interpretive framework cleanly, the urge to register is strongest, but the control burden is also highest — exactly because confirmation bias is highest. Build operational stories AFTER the controls pass, not before.

**Update 2026-05-15 — the framework-as-null principle:**

After four traps in one session (the three below + f66r as glossary, C1993 retracted), the deeper diagnostic crazy-expert formalized: **at this stage of the project (1995+ constraints, six tiers, mature operational vocabulary), framework-fit is evidence of confirmation bias, not confirmation.** When a finding fits existing tier-2 operational glosses (C1195, C1394, C1300, etc.) and uses their interpretive language, **treat the existing fit as a prior toward null** — the operational vocabulary itself can produce the appearance of signal in the data by giving new findings a place to land.

This is sharper than "run controls earlier." It says: the strongest discoveries late in a research program are usually the ones that *don't* fit cleanly. New findings that slot neatly into existing vocabulary deserve MORE skepticism, not less.

**Concrete procedure (expert-advisor formalization):**
1. Identify the structural anomaly. Register at Tier 2 (anomaly fact only, no interpretation).
2. STOP. Do not propose an operational interpretation yet.
3. Enumerate the simplest non-operational explanations that could produce the anomaly.
4. Design and run the discriminating test that distinguishes anomaly from operational story.
5. Only after the discriminating test passes do you register the operational interpretation.

**The trap's recurring signature (now generalized):**
1. Real structural anomaly with strong null-test support
2. Cleanly-structured story that fits the anomaly using existing operational vocabulary
3. Cherry-picked corroborating test (one direction, one metric, no discriminating control)
4. Pre-registration partial-failure rationalized via post-hoc cross-folio specificity or similar
5. Discriminating test (run later, often by experts pushing back) kills the story

**Why:** Three identical traps in one session (2026-05-11/12), all with the same signature, all caught by expert-advisor on the same controls:

1. **K-prefix thermal regime co-occurrence (k-e-depth).** Story: three thermal regimes (bare-k = active heat, ke/kee/keee = balneum mariae, keeee = congelation). Surface evidence: matched-folio lift 1.59 for kee+keee, clean rank-table separation, length stratification consistent. Failed at within-folio shuffle null (z=+1.25, p=0.21).

2. **Triple-i ↔ iter-terminal co-occurrence.** Story: two iteration-encoding mechanisms (qok-class repetition for discrete cycles vs aiin-family extension for gradient depth), mutually exclusive across recipe types. Surface evidence: matched-folio ρ=+0.702 (p=0.001), corpus-wide ρ=+0.228 (p=0.003), joint zero on f75r+f103r (p=0.011), f108v independent prediction-confirmation. Failed at within-folio shuffle null (mean z=+0.06 across testable folios, f112v at z=-1.10).

3. **hh = intense monitoring on matched recipes.** Story: hh tokens mark observation-intensive operations (nigredo watch, mercury sublimation observation, ferment monitoring); absent from cycle-counted/process-driven/specification recipes. Surface evidence: 6/71 hh on matched folios (0.53 depletion ratio), 5 hh-bearing matched folios all observation-intensive, 10 hh-empty matched folios all "non-observation," f84r cthh cold-read note matching the interpretation. Expert verdict: same trap. Post-hoc 3-bucket disjunction unfalsifiable; n=6 statistically meaningless with f84r driving 33%; "independent" cold-read corroboration tautological (same atom dictionary at two scales).

4. **f66r as character-key / glossary page (2026-05-15, C1993 retracted).** Story: f66r is a three-column glossary — L-labels are named operations, M-column atoms classify them by operational type, R-body provides examples. Surface evidence: 88% short-start anomaly (z=11.11), atom-gloss correspondence d→da 5.4× and t→ot 3.7×, 11/15 labels corpus-singular + 4/15 heavily cross-referenced (qokal 96× in matched recipes, raiin 24×), qokal anchor test 1.44× sh enrichment in predicted direction. Failed three discriminating tests: (1) frequency-matched null PASSED (anomaly is real); (2) L1-L15 vs L16-L32 R-body equivalence FAILED at p=0.045 (two structurally distinct zones, not unified glossary); (3) M-marker dominance on cross-referenced labels FAILED at 0/4 top-1, 1/4 top-3 (M doesn't predict label's actual operational neighborhood). The "qokal as named procedure cataloged here" lexicon anchor: qokal's M=sh ranks 3rd in qokal's neighborhood (behind o, ch), not dominant. Cross-folio specificity (1/46 folios pass 2+ atom-gloss mappings) that originally justified Tier 3 reinterpreted as multiple-comparison artifact: f66r is structurally unique on many axes, uniquely passing any pattern test is unsurprising. The qokal "1.44× sh enrichment in predicted direction" was cherry-picked — proper test shows sh comes in 3rd, not 1st. Atom-decomposition glosses ("rary = end.yield.respond.end") generated readings, then matched to the pre-chosen frame. Classic operational-story-first.

**Common failure-mode signatures:**

- **Post-hoc classification dressed as pre-registered.** Creating a disjunctive category ("X is A OR B OR C") capacious enough to absorb every observation, then claiming the partition is meaningful. The hh trap used "cycle-counted OR process-driven OR specification" for non-observation matched folios — any zero-hh folio fits at least one.

- **Ratio-language masks small-n.** "6 observed vs 11.3 expected" sounds substantial; "we observed 6 events" exposes the actual evidence base. Always frame absolute counts before ratios.

- **Tautological "independent corroboration."** Cold-read interpretations derived from the C1394 atom dictionary (h=monitor, k=heat, etc.) are not independent confirmation of claims framed in those same atom semantics. The dictionary IS the hypothesis; applying it at two scales doesn't validate it.

- **"Fits framework cleanly" feels like confirmation but is the strongest warning sign.** The cleaner the operational story, the higher the prior that you're pattern-matching rather than discovering.

- **Aggregation scope does not exempt from within-folio control.** Folio-level claims are coarse-grained within-folio claims and shuffle null applies. Don't argue "this is folio-level so the line-level control doesn't apply" — reformulate the null at folio level (shuffle token identities across folios preserving per-folio token counts; recompute claimed rate).

**How to apply:**

- **Pre-register the operational classification BEFORE looking at the distribution.** If "observation-intensive recipe" is the claim, derive the classification from source-text criteria (e.g., "Pseudo-Lull chapter contains explicit color-change instruction") before counting Voynich tokens. If the classification comes from reading the Voynich pattern, the test is circular.

- **Run the discriminating control FIRST**, not after building the registration draft. For the hh case the discriminating control was single-h: does it show the same depletion as hh, or does hh depart from h-generally? That test should have preceded the operational story, not followed it.

- **The within-folio shuffle null is the load-bearing first control for ALL co-occurrence and density-correlation findings**, whether framed at line, paragraph, or folio level. See `feedback_within_folio_shuffle_null_first.md`.

- **When an operational story emerges cleanly, increase the control burden, don't decrease it.** Confirmation bias is highest when the story fits.

- **Three identical failures in one session is a calibration signal.** When the trap pattern repeats, the right response is to stop generating new findings and re-examine the methodology, not to push the next candidate through.

The C1197 mechanical count correction (71 P-placement hh / 85 H-track, not 9 — falsification clause tripped) remains valid as a bookkeeping fix. The operational hh-as-monitoring story does NOT register without the source-text pre-registration and single-h discriminator.

---

## peak-specificity-for-periods-geq-7

*"When testing periodic-structure hypotheses at periods ≥ 7, peak-specificity (target-lag rate minus neighborhood mean) discriminates better than raw z-score against shuffle null. For periods < 7, neighborhood window catches multiples; use C2032 lag2/lag1 methodology instead."*

When testing whether a corpus exhibits a cyclic period-P signature against alternative-class hypotheses (computus, lunaria, indiction, etc.), the right discriminator is **peak-specificity**, not raw lag-P z-score against shuffle null.

**Why:** PHASE_700 (2026-05-18). The pre-registered metric (lag-19 z-score vs within-paragraph shuffle null) had a Floor 2 fail: NL Mesue Latin showed period-19 z=5.6 — well above the z>3 threshold, indicating the metric wasn't computus-specific. Long-form prose accumulates topical autocorrelation at many lags, so a non-zero z-score at lag-P doesn't establish period-P cycle; it just establishes generic structured-text autocorrelation.

The peak-specificity metric resolves this:

```
peak_specificity(P) = agreement_rate(P) − mean(agreement_rate at lags P±1..±4)
```

True cyclic period-P signal: SHARP peak at lag-P with near-zero rates at neighboring lags. Synthetic computus shows specificity ≈ +1.0 (perfect peak by construction).

Generic topical autocorrelation in NL prose: UNIFORM elevation across many lags (no peak). NL Mesue shows specificity ≈ 0.0006 across periods 7, 12, 15, 19, 28, 30.

Voynich Section B + matched-S: peak-specificity 0.01%-0.36% of synthetic baselines across all 6 medieval alternative periods tested. Statistically indistinguishable from NL Mesue → all 6 alternative classes excluded.

**How to apply:**

1. For periodic-structure hypotheses at period P ≥ 7, use peak-specificity as the primary discriminator.
2. Pre-register threshold: target corpus ≥ 10% of synthetic baseline specificity → POSSIBLE class match. Below that → EXCLUDED.
3. Validate with synthetic positive control (peak-specificity at target period must be ≈ +1.0 by construction).
4. Validate with NL negative control (NL specificity should be ≈ 0, confirming metric isn't picking up topical autocorrelation).

**Scope limit (period < 7):**

Peak-specificity neighborhood (target lag ± 4) catches **secondary peaks** of short periods. For period-2, lags 2, 4, 6, 8 are all peaks. The lag-2 "neighborhood" includes lag-4 which is itself a peak, so the specificity underestimates the period-2 signal.

PHASE_700 example: Voynich Section B period-2 specificity = +0.0052 (0.86% of synthetic), looks like failure but is metric artifact. C2032 confirms Voynich Section B period-2 grammar via lag2/lag1 ratio methodology at z=6.7.

**Use C2032 lag2/lag1 ratio methodology for periods < 7.** Different metric, different mathematical structure. Don't apply peak-specificity to short periods.

**Related:** [[feedback-calibrate-thresholds-against-controls]] (metric refinement after pre-registered threshold issue is the correct response, not verdict flip), [[feedback-within-folio-shuffle-null-first]] (peak-specificity replaces raw z-score; shuffle null still required for the underlying rate computation).

---

## feedback-phantom-clustering-provenance-audit

*"Failure pattern #9 — a claim states 'cluster analysis reveals N groupings' but no clustering ran; the real provenance is a hardcoded pre-analysis dictionary. Verify the method actually ran before trusting taxonomy claims, especially early-phase ones with round counts + domain labels."*

# Failure pattern #9: discovered-method claim for an imposed-method result (phantom-clustering)

## The pattern

PHASE_732 (2026-05-28): C109's "5 hazard classes" were registered with evidence line *"Cluster analysis reveals 5 natural groupings."* Source-code investigation (crazy-expert read the derivation script; general-purpose agent traced the whole chain; I verified directly) found:

- `phase18_failure_typology.py` lines 61-87 **hardcode** a dictionary of 5 distillation-failure-mode names + keyword lists, written before any data analysis.
- Lines 392-411 sort the 17 forbidden transitions into the 5 classes by **keyword substring-matching** (`if kw in src or kw in tgt: score += 2`).
- **No clustering anywhere.** The only clustering in the phase 15-20 chain produced 1 cluster (phase15a internal_clusters=1), not 5. Phase 16 had a different 12-mode scheme.

The claim described a method (cluster analysis) that was never run. The real method was keyword-assignment to an a-priori taxonomy.

## Why it's distinct from the existing 8 patterns

Not invented-threshold (C131), not wrong-denominator (C475), not wrong-null (C1068), not broken-baseline (C476), not post-hoc-claim-substitution (C481), not Markov-reproducible (C1727). This is **the registered claim asserting a derivation method that the source code shows was never executed.** The taxonomy may even capture real structure (see below) — but the *provenance statement* is false.

## Diagnostic

When auditing a taxonomy / clustering / partition claim:
1. **Grep the claim file and its phase scripts** for "cluster analysis", "natural groupings", "k=N clusters", "emerged", "silhouette", "kmeans", "linkage".
2. **Verify a clustering algorithm actually ran AND selected N.** If the N appears only as `len(SOME_HARDCODED_DICT)` or a keyword-list count, the partition was imposed, not discovered.
3. **Elevated suspicion:** early-phase work (the project's phases 15-20 era), round small counts (4/5/6), and physical-domain labels (distillation failure modes, etc.). Same era as the C131 invented-threshold retraction.

## Separate the two questions (this is the key methodological lesson)

"Was the partition **discovered or imposed**?" and "Does the partition **capture real structure**?" are DIFFERENT questions. Don't let the first answer the second.

- Provenance can be IMPOSED (false "cluster analysis" claim) while the grouping still captures real structure (if the imposer had good domain intuitions encoded in the keywords).
- PHASE_732: the 5-class partition WAS imposed, AND empirical clustering showed it is atom-cohesive above random (z=−4.10) — but that cohesion is **near-circular** (the keyword lists are atom-ish proxies, so clustering on atom features trivially finds the imposed grouping cohesive). The load-bearing numbers were k_optimal=8, k=3≥k=5, ARI=0.42 → **the specific count is not data-preferred**, and a gloss-coherence check found one label (ENERGY_OVERSHOOT) internally contradicted by the project's own atom decomposition (`he→t` has no heat atom).

So the honest disposition was a SPLIT: existence-of-17-transitions survives (real), atom-territory structure survives (independently held by C1528-C1533), the specific 5-class taxonomy + physical labels demote to Tier 3-4, and the false "cluster analysis reveals" line is struck.

## How to test whether an imposed partition is real (the fair test)

1. Featurize the items by the features the partition claims to track (here: atom HEAD/TERM territory), INDEPENDENTLY of the imposition criterion.
2. Cluster; report silhouette-optimal k and whether the claimed N is preferred.
3. ARI between natural clustering and the imposed partition (>0.5 = substantial).
4. Per-class cohesion vs random partitions of the same size profile — BUT beware circularity if the imposition criterion correlates with the features (then high cohesion is near-tautological; weight the k-selection and ARI instead).
5. Gloss/semantic-coherence: does each class's label match what the items' atoms/glosses say? Internal contradiction (low-tier label vs high-tier instrument like the C1394 atomizer / C1448 hazard-frame map) is a legitimate, strong signal — stronger than two co-equal interpretations disagreeing.

## The meta-lesson

This was caught ONLY because an expert read the derivation source code rather than trusting the constraint text. Reinforces [[feedback_read_first_scripts_verify]] at the audit level: **when a constraint claims a method, read the script that produced it before accepting the claim.** Constraint text and source code can diverge; the source is authoritative for provenance.

## Related memories

- [[feedback_made_up_threshold_audit]] — pattern #1 (C131), same early-phase era, same audit-driven-correction shape
- [[feedback_post_hoc_claim_substitution]] — pattern #5 (C481), JSON vs writeup divergence; this is the method-vs-claim analog
- [[feedback_framework_as_null]] — the distillation-failure-mode labels are framework-echo; the gloss-contradiction is the tell
- [[feedback_read_first_scripts_verify]] — read the source, don't trust the writeup

---

## placement-filter-azc-contamination

*All-placement filter on MIDDLE inventory analyses contaminates paragraph-text frequency claims with AZC diagram-token singletons. Use P+L (paragraph + labels) as the defensible standard; P-only and P+L are equivalent.*

When running MIDDLE inventory analyses or per-folio frequency tests on Currier B, the placement filter choice matters and has a specific failure mode:

- **P-only**: Excludes labels (L), rings (R), stars (S), circles (C), and other non-paragraph placements. Narrower than necessary but safe — gives paragraph-text frequencies.
- **P+L (paragraph + labels)**: Adds label tokens. **Identical to P-only** for hapax cohort definition in PHASE_699 (Control A: both gave 6/8 paired sign-test FAIL, p=0.14). Labels alone do NOT change frequency distributions enough to flip verdicts.
- **All-placement (no filter)**: Adds AZC diagram tokens — R rings, S stars, C circles, X, Y, N, T placements. **Contaminates** the analysis with diagram-text MIDDLE singletons that have categorically different distributional behavior per AZC architecture (C300-series).

**Why:** PHASE_699 (2026-05-17/2026-05-18). H3 paired sign test (hapax > n_2_3 enrichment on top-decile folios) gave different verdicts under different placement filters:
- P-only: FAIL (6/8, p=0.14)
- P+L: FAIL (6/8, p=0.14) ← identical to P-only
- All-placement: PASS (7/8, p=0.035)

The flip from FAIL to PASS was driven by 46 MIDDLEs that appeared exactly once on diagram positions (R/S/C/X/Y/N/T) and nowhere else in paragraphs/labels. These "AZC diagram singletons" concentrated on diagram-heavy folios, inflating per-folio hapax enrichment ratios specifically there. The v2 H3 PASS was AZC contamination artifact, not real paragraph-text signal.

**How to apply:**

1. **Default filter for MIDDLE inventory and per-folio frequency analyses: P+L** (paragraph + labels). Excludes AZC diagram tokens.
2. If you specifically want to include diagram tokens (e.g., for AZC architecture analyses), use targeted filters per the AZC contracts (`azc_activation.act.yaml`), don't use "all placements" as a generic catch-all.
3. **Never use all-placement filter for "what's the corpus frequency of MIDDLE X" type questions** — it conflates paragraph-text MIDDLEs with diagram annotations that belong to different populations.
4. When a verdict depends on placement filter choice, run all three (P-only / P+L / all-placement) and report. If only all-placement passes, the result is AZC-contamination-driven.

**Diagnostic:** if your hapax cohort grows substantially (e.g., +5%+) when going from P+L to all-placement, the added hapaxes are AZC diagram singletons. Check if they concentrate on top-enriched folios — if so, your enrichment metric is contaminated.

**Related:** [[feedback-within-folio-shuffle-null-first]] (within-folio shuffle null is the next mandatory control after placement filter is correct), [[feedback-framework-as-null]] (placement-induced PASS verdicts that don't survive paragraph-text restriction are framework-echo candidates).

---

## feedback-post-hoc-claim-substitution

*"When a follow-up test or writeup labels a constraint \"VALIDATED\" with evidence that supports a DIFFERENT claim than the constraint registered, this is post-hoc claim-substitution — the writeup reframes the question silently to rescue the constraint number. Smoking gun: script outputs explicit verification field as False while writeup says \"VALIDATED.\" C481 audit established (2026-05-19)"*

When a follow-up phase tests a previously-registered constraint, the writeup may **silently substitute a weaker or different claim** for the original headline, then label the constraint "VALIDATED" or "supported." The constraint number persists in the registry, but readers checking it see what looks like confirmation of the original claim — when in fact the surviving observation is a different claim that the original framing wouldn't have predicted.

This is the **5th distinct audit failure pattern** identified in the 2026-05-19 audit session, distinct from:
1. Invented threshold (C131)
2. Wrong denominator (C475)
3. Wrong null test (C1068)
4. Broken baseline (C476)
5. **Post-hoc claim-substitution (C481, this memory)**

**The C481 case study (2026-05-19 audit):**

Original C481 claim: "AZC survivor sets are essentially unique per Currier A line (**0 collisions in 1,575 lines**), functioning as high-dimensional constraint fingerprints. **DETERMINISTIC**."

Follow-up phase `CLASS_COSURVIVAL_TEST` ran the verification. The script writes to JSON:

```json
{
  "a_record_count": 1579,
  "unique_survivor_sets": 1203,
  "c481_verified": false
}
```

That's **376 collisions in 1579 records (24% collision rate)** — not 0 collisions.

But the human-written FINDINGS.md in the same directory says:

> **C481 VALIDATED** — 1,203 unique class patterns confirms discrimination

This is **claim-substitution**. The original claim was "essentially unique" / "DETERMINISTIC" / "0 collisions." The FINDINGS.md substitutes "1,203 patterns = discrimination confirmed" — a different (weaker) claim labeled with the original constraint number.

The smoking gun is the contradiction between the script's `c481_verified: False` output and the FINDINGS.md "VALIDATED" verdict. Same directory, same data, opposite conclusions.

**Why this is dangerous:**

- The constraint number persists ("C481 Tier 2") so downstream constraints can cite it
- Readers checking "is C481 supported?" see "VALIDATED" in FINDINGS.md and assume the original claim holds
- The actual data (`c481_verified: False`) is buried in JSON
- Future audits may not check the JSON if the writeup says VALIDATED

**Diagnostic test for this failure pattern:**

1. For Tier 2 constraints with explicit follow-up phases (`*_TEST`, `*_VALIDATION`, etc.):
2. Check whether the follow-up phase's script output contains an explicit verification field (e.g., `c481_verified`, `passes_check`, `verified`).
3. If yes, check the value. If False, audit immediately.
4. Read the FINDINGS.md / synthesis writeup in the same directory.
5. If the writeup labels the constraint "VALIDATED" / "supported" / "confirmed" while the JSON says False, this is claim-substitution.
6. Compare: does the writeup's supporting evidence prove the **original claim** or a **different claim that uses the same constraint number**?

**Red flags in writeup language:**

- "X confirms discrimination" when original claim was "X is deterministic"
- "X provides evidence" when original claim was "X is uniquely identified"
- "X is supported by the data" when the metric supporting it is different from the original metric
- Any writeup conclusion that hedges the original headline ("essentially unique" → "patterns exist," "0 collisions" → "discrimination exists")

**How to apply:**

- When auditing a constraint, ALWAYS read the follow-up phase's JSON output before reading the FINDINGS.md or constraint text. The JSON output is generated by code; the writeup is written by humans and can drift from the data.
- If the JSON has an explicit verification field showing False, the constraint is audit-eligible regardless of what the writeup says.
- When writing constraint registrations: avoid "VALIDATED" labels in writeup if the test specifically failed verification. Use "RESULT" or "OUTCOME" to describe what the test found, even if it contradicts the original claim.
- When updating FINDINGS.md or similar files in audit response: explicitly note what claim was originally tested and what claim is supported by the surviving data.

**Audit policy implication:**

This pattern likely exists in other constraints. The diagnostic is mechanical (compare JSON verification fields to writeup verdicts) and should be incorporated into the audit-sweep tool — but it requires reading the per-constraint follow-up phase artifacts, not just the constraint description.

Add to audit-sweep target heuristics: constraints with named follow-up validation phases (Phase SSD, *_TEST, *_VALIDATION) where the follow-up JSON might contain explicit verification fields.

**Related methodology memories:**
- [[feedback-made-up-threshold-audit]] (C131 — invented threshold + non-reproducing value + null at observed; component pattern of C481)
- [[feedback-denominator-choice-sparse-cooccurrence]] (C475 — N_possible vs N_attested; component pattern of C481)
- [[feedback-broken-baseline-audit]] (C476 — broken null/baseline + directional inversion; component pattern of C481)
- [[feedback-chi2-vs-permutation-null-mismatch]] (C1068 — wrong null test; related but distinct)
- [[feedback-framework-as-null]] (mature-stage prior toward null)

**Failure-mode taxonomy now 5 patterns:**

| # | Pattern | Diagnostic | Action precedent |
|---|---------|-----------|------------------|
| 1 | Invented threshold (C131) | non-reproducing value + null at observed + made-up threshold | RETRACT |
| 2 | Wrong denominator (C475) | N_possible vs N_attested on sparse graph | DEMOTE if strong-form survives |
| 3 | Wrong null test (C1068) | chi² against independence null with frequency-correlated factors | DEMOTE with marginal-perm-null note |
| 4 | Broken baseline (C476) | null/baseline algorithm artifact doesn't represent alternative hypothesis | RETRACT if surviving measurement is wrong-direction |
| 5 | **Post-hoc claim-substitution (C481)** | **follow-up phase writeup labels VALIDATED while script JSON verification field shows False** | **RETRACT + update FINDINGS.md to reflect actual outcome** |

The C481 case demonstrated all 5 patterns can coexist in a single constraint (C481 hits patterns 1, 2, 4 in the constraint itself + pattern 5 in the FINDINGS.md reframe).

**2026-01-12 batch implication:**

The C475/C476/C481 cohort all share the post-hoc-rescue tendency in some form. Batch-sweep the remaining 2026-01-12 constraints (C478 AUDIT_PENDING, C479, C480, C755, C756) checking for the same patterns. Expected hit rate: high (3/3 so far).

---

## Read the folio/data directly first; scripts only verify

*For Voynich structural-pattern work, eyeball the raw transcript before writing aggregation scripts. Scripts that ask the wrong shape of question miss patterns that are obvious on direct reading.*

For any structural-pattern question on Voynich folios (count anchors, paragraph
shape, line-bounded clusters, sequence patterns), **read the raw transcript
line-by-line first**. Use scripts only to verify or quantify what eyeballing
already surfaced. Never the reverse.

**Why:** During the 2026-04-24 session, a script-based search for "identical-
token runs" capped the f75r count anchor at 4 (the corpus-singular qokedy run
on L13). The user pointed out a 9-token qok-class cluster across L37-L38 that
was obvious on visual inspection but invisible to my run-detection algorithm.
The 9-cluster is the encoding of `e aprés ix vegades` — a load-bearing anchor
for the Catalan-tradition source claim. Missing it nearly cost us the
strongest piece of Voynich-Testamentum evidence. Several other patterns that
night were similarly visible-when-read but missed-when-aggregated: f84r body
operational sequences, f78r line-initial structure, dar-cluster shapes.

**How to apply:**

1. **Before writing a script:** dump the relevant folio's raw lines (with
   paragraph markers if useful) and read them. State what patterns you see
   in plain language. Only then pick a script question.
2. **Aggregation traps to avoid:** "longest identical-token run" misses
   mixed-class clusters (qokedy + qokeedy interleaved). "Density per kchar"
   smears out positional structure. "Spearman rho across folios" destroys
   the per-pair structural alignment that's actually doing the work.
3. **The right shape of test for syntactic claims is reverse-prediction**,
   not aggregate correlation. Pick a structural anchor on an unmatched folio,
   predict what the source recipe must contain, search the corpus, see if
   it's there. That distinguishes "real rule" from "pattern matching" in a
   way correlation tests cannot. Phase 642 was a methodological dead-end
   for exactly this reason — wrong shape of question.
4. **When the user pushes back on aggregate results,** their intuition is
   probably right. Match it by reading the folio, not by adjusting the
   script's threshold or hyperparameters.

**Related self-check rules from the same session:**

- **Check memory before stating chains of fact confidently.** I had
  `project_sismel_authoritative.md` indexed and still misstated the 1566/SISMEL
  Latin/Catalan split chain twice in one session. Read the relevant memory
  files before answering source-tradition questions.
- **Do not restate a corrected position later in the same session as if
  the correction didn't happen.** When the user has already corrected a
  factual claim, that correction is binding for the rest of the session;
  re-asserting the original is gaslighting them. Track corrections.
- **For structural-pattern claims, "look at the folio directly" beats
  any amount of statistical apparatus.** Save the apparatus for verifying
  what direct reading already found.

---

## Recto/verso recipe-continuation claims need section-matched controls

*Phase 686 candidate (matched-recto verso P1 continues alchemy genre) PASSED naive baseline test (qo_rate vs all-Currier-B) at p<0.001 but FAILED section-matched control (Jaccard vs Section-B-only random pairs). Section B's intrinsic paragraph-1 vocabulary similarity (~0.13 Jaccard, per C361 adjacent-folio vocab sharing) fake-passes any bare baseline. Future r/v continuation claims must use section-matched random pairs as null.*

**Why:** On 2026-05-06, qo_rate-based test of "matched recipes continue onto verso P1" passed all 4 pre-reg criteria at p<0.01 vs Currier B baseline. Looked like a clean Tier 3 register. Expert consultation (both expert-advisor and crazy-expert) flagged section confound. Corrective test using token-Jaccard:
- Matched r/v P1 mean Jaccard: 0.126
- All-Currier-B random pair mean Jaccard: 0.059 (would falsely "confirm")
- **Section-B-only random pair mean Jaccard: 0.129** (kills the signal — matched pairs are at section baseline, not above)

The original qo_rate result was the same confound at single-feature level. Matched versos are alchemy-section folios, so they have alchemy qo_rate. The "signal" was section membership re-discovered.

**How to apply:**
- For ANY claim about recto-verso recipe spillover, paragraph-pair similarity, or matched-folio-cluster behavior — use section-matched random null, not all-Currier-B random null.
- Section B's intrinsic paragraph-1 vocabulary similarity (~0.13 Jaccard per pair) is the floor any "matched pair" claim has to clear.
- C361 documents adjacent-B-folio vocab sharing at 1.30× — this is the structural fact future tests must control for.
- qo_rate as alchemy-discriminator confounds with section membership; use recipe-distinctive features (e-depth gradient, ke/ek ratio, dar-distribution shape) for recipe-specific claims.

**What still survives from Phase 686 attempt:**
- f103v as hybrid folio (P1 alchemy → P2-P13 pharmacy) is still validated by direct reading — see project_f103v_hybrid_folio.md
- Per-pair pair-specific signals on f80r/v (rank 2/79) and f81r/v (rank 4/79) — these specific pairs show pair-specific Jaccard above what their section average would predict. Worth individual investigation if pursued.
- C1936 (f66r/v, f103r/v, f108r/v as sequential pairs) and C1947/C1948/C1953/C1954 (specific r/v pairs in matched catalog) are unaffected — they were already pair-specific findings, not generalizations.

**Connection to existing constraints:**
- C361 adjacent-folio vocabulary sharing — the floor that fake-passes naive baselines
- C1287 paragraph-1 MARKING enrichment — P1 has known enrichment effects, exacerbates baseline issues for any P1-vs-P1 test
- C1300 qo as 100% k-HEAD thermal channel — qo_rate is genre indicator (alchemy/non-alchemy), not recipe indicator
- C1808 section qo-rate baselines — H ≈ 0.10, B ≈ 0.20, S ≈ 0.15

**Per-pair follow-up (2026-05-06, after corpus-wide null):**

The corpus-wide test surfaced two pair-specific outliers (f80r/v rank 2/79, f81r/v rank 4/79). Direct drills with proper controls killed both:

**f81r/f81v: not a continuation.** Both folios are independently matched in C1971 (f81r→Ch.10 dissolution, f81v→III.18 potable gold). Pair similarity reflects two adjacent matched alchemy recipes, not one recipe across the leaf.

**f80r/f80v: not a continuation either, despite passing first-pass plausibility.** Three corrective controls (per crazy-expert) decisively rejected:

1. **Continuation vs genre-mate test (THE KILLER):** f80v P1 should be closer to f80r-LAST than f80r-FIRST if continuation. Result: f80v P1 is **2× closer to f80r FIRST** (0.27 vs 0.53). f80v starts at f80r's opening profile (qo=38%, fresh fire) not f80r's closing profile (qo=7%, fire dropped). f80v is opening a NEW recipe in the same calcination genre, not continuing f80r.

2. **dar=0 baseline check:** 56% of Currier B P1s have dar=0. f80v's dar=0 is the COMMON case, not distinctive evidence. The "no fresh material loading implies pre-loaded" argument was rhetorical filler.

3. **Pair-exclusive rare vocabulary baseline:** f80r/f80v shares 4 corpus-rare (n≤5) tokens. Median r/v pair shares 2. f80r/f80v ranks #9/33 — top 27% but NOT exceptional. f111r/v shares 7, f104r/v shares 6, f105r/v shares 6, f112r/v shares 6, f107r/v shares 5, f114r/v shares 5, f115r/v shares 5. Same-scribe-same-session r/v writing produces baseline rare-token sharing of 2-7. f80r/v's 4 is in normal range — codicological signature, not procedural continuation.

**Key methodological lessons:**

1. **The cleanest test for r/v continuation is the FIRST-vs-LAST atom comparison** of verso P1 against recto's first paragraph vs recto's last paragraph. If continuation, P1 should be closer to recto-LAST. If genre-mate (next recipe in same genre), P1 will be closer to recto-FIRST. Always run this test before claiming continuation.

2. **Pair-specific Jaccard rank from a failed null test is a weak prior, not evidence.** Outlier status from one test doesn't survive different framings. Always test with multiple orthogonal proxies before treating an outlier as a real signal.

3. **C1936 (3 documented r/v continuation pairs: f66r/v, f103r/v, f108r/v) is the limit of evidence.** Multiple attempts to extend the pattern beyond these three have failed. Future r/v continuation claims need either source-text alignment proving the recipe continues, OR the FIRST-vs-LAST atom test plus 2+ supporting features.

4. **Corpus-rare token co-occurrence on r/v pairs is a baseline scribal signature**, not evidence of recipe continuation. Median 2 tokens shared per r/v pair means same-scribe-same-session writing produces this baseline level of rare-token sharing without any recipe semantics.

**See also:**
- memory/project_f103v_hybrid_folio.md — the hybrid finding survives (P1 alchemy + P2-P13 pharmacy is structural observation independent of continuation question)
- memory/project_section_s_source_genre_gap.md — related sourcing-vs-analysis distinction
- C1936 — the documented r/v continuation pairs (limit of evidence)
- C1977-C1978 — r/v PREFIX profile coherence (cos 0.931 baseline that any pair-specific claim must beat)

---

## Pre-registered criteria must be discriminating, not loose floors — calibration lesson (2026-05-16)

*When pre-registering multi-axis binary criteria for a hypothesis test, every axis must be discriminating against the alternative being tested. Loose floors that "any structured system" passes are framework-echo waiting to happen; literal-verdict pass on those axes provides no evidential weight. Lesson came from the mensural hypothesis test where the literal pre-registration verdict said 2/3 PASS but only one of those three axes (C2032 lag2/lag1) actually discriminated Voynich-substrate from NL-baseline. The other two passes (C2015 entropy in [1.0, 3.0] bpc; C2022 Markov plateau at order 2-3) are satisfied by any moderate-vocabulary structured symbolic system. Future cross-corpus engineered-substrate tests should weight C2032 as load-bearing, with C2015/C2022 serving as exclusion floors only.*

## The lesson

Pre-registration discipline is supposed to prevent post-hoc goalpost-moving. But it can also produce false positives if the registered criteria aren't all discriminating against the alternative being tested.

**Mensural test (2026-05-16):** pre-registered three binary criteria, 2-of-3 pass threshold. Two of the three turned out to be non-discriminating in retrospect:

- C2015: "entropy in [1.0, 3.0] bpc" — any moderate-vocabulary structured symbol system satisfies this. The Latin corpora (Codicillus alchemy, Mesue pharmacy) would also pass. Mensural passed at 1.857.
- C2022: "Markov plateau at order 2 or 3" — any system with limited vocabulary + bigram/trigram structure satisfies this. Latin would also pass. Mensural passed at 2.
- C2032: "lag2/lag1 ratio magnitude > 0.4" — the ONLY axis that distinguished Voynich (±0.66) from Latin baselines (−0.17 to −0.22). Mensural failed at +0.18.

Literal verdict: 2/3 PASS. Substantive read: only discriminating axis failed.

## Why: necessary-but-not-sufficient floors masquerade as discriminating tests

C2015 and C2022 are necessary conditions for engineered-substrate-class behavior. Voynich passes them. But they are not sufficient — many systems pass them. Treating them as binary pass/fail criteria with equal weight to C2032 gave them undue evidential influence.

**The fix is at the pre-registration design stage:**

For each candidate criterion, ask:
- Does the alternative-hypothesis baseline (in this case: natural language Latin) ALSO pass this criterion?
- If yes → it's a floor, not a discriminator. Use it as an exclusion gate, not a vote.

Only criteria that the alternative-baseline FAILS should count toward the pass-threshold vote.

## How to apply

**For multi-axis cross-corpus tests:**

1. Pre-classify each criterion as DISCRIMINATOR or FLOOR before running.
2. FLOORs are pass-required-to-proceed gates (if mensural failed entropy entirely, that would be informative; passing it is not).
3. DISCRIMINATORs are the actual vote. Need ALL discriminators to pass (or pre-registered fraction of discriminators) for a substantive PASS verdict.
4. If only one axis turns out to be discriminating, that axis alone determines the verdict. "2/3 pass" with one discriminator is not "structural class match."

**For the engineered substrate triad specifically:**

- C2032 (lag2/lag1 ratio) is the load-bearing discriminator. Voynich's ±0.66 vs NL Latin's ±0.2 is order-of-magnitude separation.
- C2015 and C2022 are necessary floors. They confirm "this corpus has engineered-substrate-class structural sophistication" but don't separate Voynich from NL.
- Future tests with the triad: gate on C2015/C2022 passing as exclusion criteria, then evaluate verdict purely on C2032.

## Connection to other methodology notes

- `feedback_framework_as_null.md` — the umbrella discipline. This note is a specific instantiation: framework-echo can hide inside pre-registered criteria if those criteria aren't all discriminating.
- `feedback_operational_story_first_trap.md` — adjacent failure mode (story-first interpretation). This note covers the specific design failure of giving non-discriminating axes equal vote weight.
- `feedback_three_mechanism_demotion_trifecta_2026_05_16.md` (now quartet) — the mensural test was the fourth entry in the demotion log; this note formalizes WHY the literal verdict was misleading.

## See also

- `phases/MENSURAL_NOTATION_HYPOTHESIS/results/triad_measurement.json` — the test result that triggered this lesson
- `phases/MENSURAL_NOTATION_HYPOTHESIS/results/constrained_random_null.json` — the methodology validation showing C2032 measurement is sound
- `project_mensural_hypothesis_falsified.md` — companion project memory

---

## When a broad test gives mean rho +0.4-0.5, suspect scope conflation

*Recurring pattern across Phase 643, 645→647 — broad tests produce mixed/moderate aggregate signal because they include cases where the effect cannot exist by construction. Pre-classify by what the underlying data could plausibly support BEFORE running aggregate tests. The refined test almost always produces clean signal where the broad test produced noise.*

When a correlation/aggregation test on N units produces mean rho in the
+0.4 to +0.5 range with mixed individual significance (some hits, several
nulls), don't conclude "weak signal." Stop and ask: **could the effect
exist on every unit in this test, or only on a subset?**

If the test units include cases where the effect is structurally
impossible (uniform-heat recipes can't show heat-progression; theoretical-
exposition recipes can't show count-anchors at the same scale; etc.),
the broad aggregate is averaging real signal with structural zeros.
**Restrict to the subset where the effect could plausibly exist, lock
the classification before re-running, and the clean signal usually
emerges.**

**Why:** This pattern has now appeared three times in the project:

1. **Phase 643 (paragraph independence)** — C1399 measured corpus-aggregate
   state-coupling. Its phrasing extended that to "paragraphs are parallel
   subroutines, not sequential steps" — a stronger claim never tested.
   Test B restricted to matched folios with documented recipe-phase
   structure showed clean rho +0.81 vs the apparent corpus-aggregate null.

2. **Phase 642 → Phase 643 transition** — pre-registered Spearman rho on
   gloss feature rates returned 0/6 supported. Same data, restructured
   into per-folio reading + reverse-prediction, produced 4 confirmed
   matches at strict significance. Aggregate cross-folio correlation was
   the wrong shape of test for structural-positional syntax.

3. **Phase 645 → Phase 647** — heat-progression test on all 7 matches
   gave mean rho +0.484 with 1/7 strict significance. Pre-classifying
   recipes into heat-phase-distinct (5) vs heat-uniform (3) and re-running
   on phase-distinct only gave mean rho +0.71 with 5/5 positive direction.
   The heat-uniform nulls were structural (no heat progression to encode)
   not data-failure.

**How to apply:**

1. **Before running an aggregate test**, articulate what conditions each
   test unit must satisfy for the effect to be detectable. Pre-classify
   units that don't satisfy the conditions.
2. **If the broad test gives mean rho ~+0.5 with mixed direction**, don't
   register it as "weak support." Stop, identify the structural-zeros,
   pre-classify, re-run.
3. **Lock the pre-classification before re-testing** — pre-registration
   discipline prevents post-hoc selection of the convenient subset.
4. **Test the heat-uniform / non-applicable subset as a control** — its
   null result corroborates that the restriction is principled, not
   cherry-picked.
5. **Register the scope-restricted version**, not the broad version.
   Document the scope explicitly in the constraint phrasing.

**Failure mode this prevents:**

- Registering a watered-down version of a strong effect because the
  broad test averaged signal with structural zeros
- Running follow-up investigations on the wrong scope (overgeneralized
  null) and missing real findings
- Inheriting overstrong interpretive phrasings from constraints whose
  measurements were narrower than their phrasings suggested (the C1399
  pattern that crazy-expert flagged as a class issue)

**The diagnostic:** mean rho 0.4-0.5 with 1/N strict significance and
mixed direction is the signature of scope conflation. If 5/N show
positive direction at moderate strength but only 1/N reaches significance,
the data is telling you most units have signal — the underpowered
hits and the genuine nulls are mixing. Separate them.

**Related:**
- `feedback_read_first_scripts_verify.md` — read the data directly first
- `project_paragraph_independence_vs_enumeration.md` — concrete example
  of the constraint-system gap this pattern reveals
- `project_paragraph_layout_ordering_empirical.md` — what the refined
  test actually produced

---

## specific-vs-tautological-predictions

*Pre-registered prediction protocols must decompose into SPECIFIC (genuine discriminators) and TAUTOLOGICAL (genre-floor) predictions. Inflated N/N scores mask the actual discriminating power.*

When running a pre-registered prediction protocol against a candidate match (e.g., Voynich folio vs Latin recipe), decompose predictions into two classes BEFORE scoring:

- **SPECIFIC predictions** — predictions derived from recipe-specific content that would NOT verify on a near-miss recipe of the same operational class. Examples: specific cardinality anchors (×4, ×9, ×3), specific thermal arc shape (V-shape with crash to 0.18, fire-strengthening decreasing arc, balneum steady), specific material renewal pattern (back-loaded vs front-loaded), specific operational structure (reflux geometry, sublimation signature, cohobation recycling).

- **TAUTOLOGICAL predictions** — predictions that are true for nearly any operational folio of the same broad class. Examples: high qo-prefix dominance, multi-paragraph procedural structure, observation MIDDLEs present, elevated e-depth. These are floors — they tell you "this is an operational distillation folio" but don't discriminate which specific recipe.

**Why:** PHASE_698 (2026-05-17). The cold-read framework (C1971) reports "8/8 predictions verified" for f75r ↔ III.19. Reading the actual protocol shows 5 of the 8 are SPECIFIC and 3 are TAUTOLOGICAL. Near-miss negative controls (other distillation recipes) score 5/8 total — 2-3 SPECIFIC + 2-3 tautological — because they pass the floors but fail the discriminators. The 8/8 vs 0/7 framing inflates by including floors as discriminators. The underlying discrimination is at the SPECIFIC layer: 5/5 SPECIFIC for correct match vs 0-2/5 SPECIFIC for near-miss.

**How to apply:**

1. When pre-registering predictions, label each as SPECIFIC or TAUTOLOGICAL.
2. SPECIFIC predictions: derived from content that would change if the recipe were a different near-miss. Cite the recipe-specific feature each prediction is testing.
3. TAUTOLOGICAL predictions: derived from class-level features. Note them as floors — they're exclusion gates (a folio without them is wrong) but don't license positive identification.
4. Score correct match vs near-miss controls separately on SPECIFIC and TAUTOLOGICAL subsets.
5. Report verdict on SPECIFIC subset only; TAUTOLOGICAL count is corroborative not discriminating.

**Diagnostic:** if a pre-registered prediction would pass for a wrong-class control (e.g., "qo-prefix dominant" passes for any Currier B distillation folio), it's TAUTOLOGICAL.

**Related:** [[feedback-registration-calibration-lesson]] (gate on floors, verdict on discriminators), [[feedback-calibrate-thresholds-against-controls]] (calibrate numerical thresholds vs in-distribution controls). [[feedback-framework-as-null]] (the cold-read 8/8 framing was framework-echo until the SPECIFIC vs TAUTOLOGICAL decomposition).

---

## text-statistical-methods-generic-at-domain-level

*"Two consecutive cross-corpus text-statistical tests (8D matcher PHASE_718, substrate quintet stem-class PHASE_720) discriminate Voynich from Latin generally but NOT Latin subdomains. Distillation interpretation rests on architectural/dynamical evidence only."*

Two consecutive negative findings (2026-05-20) establish that **text-statistical cross-corpus methods don't have resolution to discriminate Latin subdomains at the project's current methodology stage**.

**PHASE_718:** 8D matcher (Codicillus pipeline) applied to Theophilus negative control. Matcher attracts Theophilus chapters to the same Voynich folios as Codicillus chapters at similar rates. Pre-registered failure criteria triggered. Matcher confirmed generic at text-feature level.

**PHASE_720:** Substrate-quintet C2032 stem-class autocorrelation applied to Rupescissa (distillation) vs Theophilus (metalwork). Both show similar small-magnitude lag excesses (~0.003-0.03 absolute), neither approaches Voynich's -0.66. Calibration gap discovered: Codicillus reproduction r21=-0.007 vs known -0.22. Pre-registered prediction failed.

**Why:** When stem-class lag1_excess is small (<0.05 absolute), r21 is bootstrap-fragile. Latin's word inventory and case morphology produce small same-class repetition rates across all domains. The substrate quintet's known Voynich -0.66 / Codicillus -0.22 / Mensural +0.18 differences are large at the Voynich-vs-NL level but compress within Latin to noise-floor magnitudes.

**How to apply:**
- Don't use text-statistical cross-corpus methods to claim domain-level discrimination within Latin
- Calibrate against the project's known reference values BEFORE running new cross-corpus tests
- If the reference value doesn't reproduce, the methodology has drifted (per `feedback_calibrate_thresholds_against_controls.md`)
- For domain-level discrimination questions, the test paths that survive: PWRE-1 structural narrowing (architectural physics-compatibility), within-text dynamics (PHYS, C1314, C645+C2045, C2042), NOT text-statistical resemblance to known-domain corpora

**The distillation interpretation specifically rests on:**
- PWRE-1 structural narrowing (excludes Theophilus-type irreversible-transformation metalwork, leaves circulatory thermal class)
- PHYS kernel dynamics (k/h excitation → e stability)
- C1314 qo-k/ok-e thermal cycling
- C645+C2045 hazard-recovery directional
- C2042 atom-monocategorical operational signature
- NOT on corpus-statistical resemblance to known distillation texts (matcher confirmed generic; substrate quintet generic within Latin)

**Strategic implication:** the project's surviving distillation evidence is architectural/dynamical, not corpus-statistical. External grounding for content-level claims requires non-text-statistical methods (physical reconstruction, architectural-alignment sharpening, archaeological context).

Per `feedback_mechanism_cycle_procedural_ceiling.md`: text-statistical methods exhausted at current resolution; further mechanism speculation needs external grounding.

---

## Mechanism-demotion quartet (2026-05-16) — operational interpretations at "middle layer" specificity all die within the procedural ceiling [UPDATED from trifecta to quartet 2026-05-16 evening]

*Single session, four mechanism-interpretation candidates, all failed at successively deeper levels of validation (Voynich-internal control → Voynich-internal extended test → cross-language external grounding → external-corpus discriminating test). Structural measurements survived every cycle. The pattern indicates the project has a stable "operational-specificity death zone" — interpretations at the "encodes X" / "represents Y" level reliably die under discriminating tests, while measurement-level structural facts and substrate-level claims survive. Tighten promotion discipline: Tier 3 → Tier 2 for mechanism claims now requires BOTH Voynich-internal discriminating test pass AND external-corpus validation, not just one.*

## The quartet (was trifecta, updated 2026-05-16 evening)

Single session-day (2026-05-16) produced four mechanism-interpretation candidates, all demoted:

### Cycle 1 — C2027 retraction (morning)

Original Tier 2 registration: "Heat-cycle MIDDLE-class adjacency chains UNIQUE to PL-matched Section S folios, corroborating iteration-encoding mechanism." Survived original Voynich-internal control (within-paragraph shuffle null).

**Failed at:** Pre-registered family-stratified shuffle null discriminating control (crazy-expert's "weaponize C2027 against itself"). Three of four pillars falsified: "matched-S unique" was wrong; "iteration-encoding mechanism" was wrong; distribution misread.

**Retracted to Tier 1.** Replaced by C2028/C2029/C2030 covering corrected scope.

### Cycle 2 — Sustain-vs-phase-switch interpretation death (afternoon)

Tier 2 candidate registered conceptually: "Section S sustains thermal intensity; Section B phase-switches between heat and cool." Survived initial multi-lag autocorrelation pre-registered binary test (3/3 sustain criteria for matched-S, 3/3 alternation criteria for Section B at narrow-heat-cycle class).

**Failed at:** Alternation-slot follow-up revealed Section B's i+1 position was mostly other-thermal-class tokens (chedy/shedy with single-`e` MIDDLE), not non-thermal. The "heat alternating with non-heat" framing was framework echo at the wrong class-boundary.

**Demoted before registration.** Sharpened to e-depth oscillation hypothesis.

### Cycle 3 — Trajectory-encoded interpretation death (evening, Codicillus cross-validation)

Tier 3 SPECULATIVE candidate registered in `encoding_modes.md`: "Section B alchemy is trajectory-encoded (thermal narrative IS sequential structure); matched-S Mercuriorum is instruction-encoded (self-contained operational specs)." Survived all Voynich-internal controls: multi-lag autocorrelation, within-folio shuffle null, AX/operational decomposition. The asymmetric outcome (Section B operational period-2 + matched-S operational NULL) ruled out pure-framework-vocabulary-echo.

**Failed at:** Codicillus cross-validation (external grounding). Both Latin alchemy (Codicillus) and Latin pharmacy (Mesue) showed near-zero sequential autocorrelation at all lags. The cross-language alchemy/pharmacy structural distinction predicted by the encoding-modes interpretation did NOT replicate. lag2/lag1 ratios: Codicillus +0.05, Mesue −0.17, vs Voynich's ±0.66 — order-of-magnitude separation with no overlap.

**Half-falsified.** Cross-language genre framing dies; Voynich-internal structural divergence (C2031) preserved. **The Voynich-vs-NL distinctness IS the substantive new finding** (registered as C2032, third axis of "engineered substrate triad" alongside C2015 and C2022).

### Cycle 4 — Mensural notation falsification (evening, external-corpus discriminating test)

Crazy-expert proposed: "Voynich tokens are MEASURE-units in a quasi-musical mensural notation, contemporary with the manuscript (Franco of Cologne ~1280, Ars Nova 1320s). Compatible with distillation content per C1971; explains the engineered substrate triad as scheduling rather than content."

Acquired Measuring Polyphony mensural corpus (64 motets, 30,375 notes, MEI format). Ran pre-registered binary triad test:
- C2015 entropy: 1.857 bpc PASS (loose floor)
- C2022 Markov plateau: order 2 PASS (loose floor)
- C2032 lag2/lag1: +0.18 **FAIL** (Voynich = ±0.66; mensural sits in NL Latin range)

Literal verdict: 2/3 PASS. Substantive verdict: only discriminating axis failed. Constrained-random null confirmed methodology floor (period-2 synthetic produces r21 = −1.0, qualitatively Voynich Section B shape — metric works).

**Falsified.** Music was the wrong analogy. Both experts independently retracted with no replacement musical-class hypothesis. The two-signature problem (Section B period-2 vs matched-S sustain) is fatal for any single-mechanism notational interpretation. See `project_mensural_hypothesis_falsified.md` and `feedback_registration_calibration_lesson.md`.

## What the pattern reveals

**The "middle layer" death zone.** Interpretations at the operational-specificity level — "encodes X procedurally," "represents Y operationally," "alchemy IS Z" — die reliably under discriminating tests at this project stage. What survives:

- **Lower layer**: measurement-level structural facts (C2028, C2029, C2030, C2031, C2032 all measurement-only)
- **Upper layer**: substrate-level claims that name an axis without committing to operational interpretation ("engineered sequential grammar"; "Voynich-vs-NL structural distinctness")

The middle layer is where framework-as-null applies hardest. Operational vocabulary at this project stage gives interpretations a place to land too cleanly; the data alone cannot select among admissible operational readings; external grounding either succeeds (rare) or fails (today's pattern).

## How to apply

**Tightened registration discipline (proposed):**

Tier 3 → Tier 2 for mechanism interpretations now requires BOTH:

1. **Voynich-internal discriminating test pass** with pre-registered binary criteria (existing rule)
2. **External-corpus validation** on a pre-registered prediction that distinguishes the proposed mechanism from natural-language baseline OR from alternative operational frames

Either alone is necessary but not sufficient. Today demonstrated that internal discriminating tests can be passed by mechanism interpretations that fail external validation.

**The exception**: substrate-level claims that don't commit to operational interpretation (today's C2032, the engineered substrate triad framing). These are measurement-level claims at the inter-corpus comparison level; they survive both internal and external tests because they don't propose an operational interpretation in the first place.

**For session-level discipline**: when three mechanism candidates die in one session, the next session should NOT propose more middle-layer operational interpretations. Either move to substrate-level claims (measurement convergence across axes) or move to external-grounding work (acquire new corpora, run cross-language tests, build apparatus reconstructions).

## Connection to other methodology notes

- `feedback_operational_story_first_trap.md` — the original framework-as-null trap pattern (the lower-resolution version of this rule)
- `feedback_framework_as_null.md` — 2026-05-15 sharpening
- `feedback_expert_predictions_are_pre_registrations.md` — expert mechanism predictions discipline
- `feedback_mechanism_cycle_procedural_ceiling.md` — yesterday's session-level rule about the discrimination cycle
- `feedback_within_folio_shuffle_null_first.md` — mandatory control #1

This note formalizes the three-strike confirmation of the procedural ceiling and proposes tighter promotion discipline for the next phase of the project.

## What the quartet produced in the end

- C2027 retraction → C2028 (Section S vs Section B heat-cycle MIDDLE-class divergence)
- Sustain-vs-phase-switch demoted → C2029 (daiin doesn't chain), C2030 (Voynich-wide late-term clustering), C2031 (e-depth asymmetry mechanism-level measurement)
- Trajectory-encoded demoted → C2032 (Voynich-vs-NL sequential structural distinctness)
- Mensural notation falsified → registration-calibration lesson (`feedback_registration_calibration_lesson.md`); mensural corpus now available as additional NL-baseline cross-corpus reference

Four substantive Tier 2 structural measurements registered. Four operational interpretations died. **The discipline produced more measurement-level findings by failing more operational interpretations.** This is the system working at the procedural ceiling.

The fourth cycle also produced a methodology refinement (the calibration lesson): in multi-axis pre-registered tests, all axes must be DISCRIMINATING against the alternative-hypothesis baseline. Loose floors that any structured system passes are not votes; they are exclusion gates only.

## See also

- `SPECULATIVE/engineered_substrate_triad.md` — synthesis of C2015 + C2022 + C2032 as the substrate-level survival
- `SPECULATIVE/encoding_modes.md` — the half-falsified Tier 3 interpretation that led to C2032's cross-language test
- C2027 retraction narrative in CLAIMS/INDEX.md
- C2028, C2029, C2030, C2031, C2032 — the surviving measurement registrations

---

## 8D matcher top-1 ratio-confidence mode is degenerate; use hypothesis-driven distance gating

*Phase 627/628 8D matcher (TUNED_DIMS) collapses to f34v for ~60% of input units regardless of corpus domain (Antidotarium 66%, Codicillus 58%, Brunschwig 60%). This is geometric-centrality property of the V-side feature space per C1366 (f34v is the top least-anomalous folio at 0.71). Top-1 ranking + ratio-confidence is therefore not a valid evaluation mode. Real C1971 matches use hypothesis-driven absolute-distance gating (d < 1.0 threshold).*

## The rule

When evaluating 8D matcher results on a new source corpus, do NOT use top-1 ranking + d2/d1 ratio-confidence as the evaluation method. The matcher's top-1 mode degenerates to f34v (or one of the 5 least-anomalous folios per C1366) for the majority of input units, regardless of whether the corpus is in-domain or out-of-domain.

The validated evaluation method is **hypothesis-driven absolute-distance gating**: pre-identify candidate Voynich folios for specific source units, compute pairwise distances, accept matches at d < 1.0 with secondary structural criteria (token/verb ratio, instruction count, fch positions, etc.).

**Why:** The 8D feature space has a geometric center where folios with low operational signal (low token counts, near-zero on most TUNED_DIMS) accumulate. f34v (115 tokens, REGIME_3, Section H) sits at that center per C1366 (least-anomalous at 0.71). Any source unit with weak or missing operational signal will default to that center under top-1 nearest-neighbor — not because the source matches f34v's content, but because f34v is closest to the all-zero "no signal" vector.

**How to apply:** 

- When testing a new source corpus, FIRST run the matcher on a validated in-domain control (Codicillus or a PL chapter subset). If the control's top-1 results don't recover its expected Section B alchemy matches, do NOT trust top-1 mode for the new corpus.
- For real corpus-corpus matching: build hypothesis-target pairs from external evidence (genre, period, specific operational claims) and test distance < 1.0 with structural co-criteria. C1943, C1955, C1990, C1992 are exemplars.
- The top-1 mode is informative as a **null-shape diagnostic**: if your corpus produces a different top-1 distribution than f34v-dominated, that's evidence the corpus has unusual signal worth investigating. Same distribution = corpus is uninformative under TUNED_DIMS.
- For corpus-class falsification (e.g., "is Section S genuinely pharmacy?"), top-1 cannot answer either way. You need absolute-distance comparisons against pre-identified candidate folios.

**Test cases that confirmed this (2026-05-15):**
- Antidotarium Nicolai (out-of-domain compound pharmacy, 124 recipes): 82/124 → f34v top-1
- Codicillus (in-domain PL alchemy companion text, 19 segments): 11/19 → f34v top-1
- Brunschwig 1512 (in-domain validated 20 compound recipes): 12/20 → f34v top-1
- All three: mean d2/d1 ratio at 1.0-1.1; 0 confident matches at ratio > 1.30; 5-7 unique top-1 folios out of 82

The matcher discriminates corpora through absolute distance levels (Antidotarium min d=1.06 worse than Codicillus 1.16 worse than Brunschwig 1.13), not through top-1 attractor patterns.

## Connection to existing constraints

- **C1366**: top-5 least-anomalous folios = f34v (0.71), f106r (0.67), f106v (0.65), f31r (0.62), f66v (0.62). These are the geometric attractors. f34v's overwhelming dominance suggests the matcher's distance metric is biased toward low-token-count folios.
- **C1943/C1955/C1990**: validated matches use d<1.0 hypothesis-driven gating, not top-1 ranking. f106v↔Ch40M at d=0.933 ratio=1.164 (not a high ratio, but the absolute distance is the load-bearing claim).
- **C2026**: the registering constraint documenting the baseline-fail observation.

## Anti-trap value

This is critical against the framework-echo trap. When a new corpus produces "interesting" top-1 attractor patterns that fit existing hypotheses (e.g., "Antidotarium pharmacy recipes attract Section S folios"), the right reaction is suspicion: top-1 mode is so degenerate that ANY pattern emerging from it could be artifact. The discipline is to ask "what does the absolute distance say, against an external prediction?" before any interpretive read.

---

## Within-folio shuffle null is the load-bearing first control for co-occurrence claims

*For any co-occurrence or density-correlation claim, run within-folio shuffle null BEFORE other refinements. Aggregate rho in the +0.15 to +0.65 range is the diagnostic signature of folio-composition shadow.*

For any co-occurrence or density-correlation claim, **within-folio shuffle null is the load-bearing first control**, not a late one. Aggregate Spearman rho in the +0.15 to +0.65 range is the diagnostic signature of folio-composition shadow when no within-folio null has been run.

**Why:** Demonstrated twice in one session (2026-05-11):

1. **K-prefix thermal regime co-occurrence (k-e-depth):** matched-folio pooled ρ = 1.59 lift for kee+keee co-occurrence, looked like clean 3-regime / 2-regime mechanism. Within-folio shuffle null killed it: z = +1.25 (p = 0.21), folio-composition shadow entirely.

2. **Triple-i ↔ iter-terminal co-occurrence:** matched-folio ρ = +0.702 (permutation p = 0.001), corpus-wide ρ = +0.228 (p = 0.003), clean folio-level rank segregation, f108v independent prediction-confirmation. Within-folio shuffle null killed it: mean z = +0.06 across testable folios, zero folios with z > +2, f112v (highest-triple-i folio) at z = −1.10. The matched-folio ρ was reading "folios with more triple-i also have more iter-terminal tokens overall" — exactly folio composition.

Both findings looked great descriptively. Both survived simple controls (permutation null on ρ, binomial test on extreme cases, rank-table inspection). Both died at within-folio shuffle null.

**How to apply:**

- Before claiming any line-level or paragraph-level co-occurrence pattern, run within-folio shuffle null as control #1. NOT control #4.
- Test: per folio, redistribute tokens across lines (preserving line lengths), recompute the statistic. If real exceeds null by z > 2, line-level co-occurrence is real. If real ≈ null, the apparent pattern is folio-composition shadow.
- Aggregate ρ across folios in the +0.15 to +0.65 range with no within-folio null = strong prior that what you have is composition shadow, not mechanism. The matched-folio enrichment (matched ρ > all-folio ρ) doesn't rescue this — it just means operationally-aligned folios have stronger composition signals.
- Section stratification, length stratification, placement filtering are second-order controls. They refine an already-validated finding. They cannot substitute for the within-folio null.
- Constraints are claims about the manuscript; methodology lessons are claims about how to investigate it. This rule generalizes beyond Voynich and belongs in MEMORY, not in the constraint table.

---

# Structural Contract Signatures

## CASC (Currier A Structural Contract)
**Meta:** v2.3, ACTIVE, Currier A, 114  # C272 folios

### Guarantees (5)
- LINE_ATOMIC: Each line is an independent unit [C233]
- POSITION_FREE: No token-to-token positional grammar within lines (but HEAD-type positional tendencies exist: o-HEAD leads, headless tra [C234, C1395]
- NON_SEQUENTIAL: No generative grammar exists [C225, C230, C231, C240]
- FLAT_REGISTRY: Not hierarchical between tokens (no sequential grammar); tokens are internally structured via HEAD+MOD*+TERM [C236, C1395]
- MIDDLE_INSTRUCTION_ENCODING: A MIDDLEs follow the same HEAD+MOD*+TERM instruction encoding as B (modifier ordering Fisher p=0.90, pair-lock 84.2%) [C1393, C1394, C1395]

### Sections -> Constraints
- record_types: C482, C484
- morphology: C235, C267, C268, C269, C277, C278, C291, C292, C293, C408, C412, C423, C466, C467, C475, C495, C498, C510, C511, C512, C513, C528, C529, C530, C831, C832, C833, C835, C836, C837, C838, C839, C1013, C1137, C1140, C1261, C1262, C1265, C1268, C1393, C1394, C1395, C1540, C1541, C1544
- line_structure: C233, C236, C240, C250, C422, C482, C484, C1393, C1394, C1395
- record_internal_grammar: C240, C1395
- paragraph_structure: C475, C476, C827, C834, C846, C847, C848, C849, C850, C854, C1039, C1040, C1041, C1263
- participation: C299, C384, C441, C442, C475, C481, C484, C502, C753, C824, C825, C826, C1013, C1014, C1016, C1018, C1020, C1134, C1135, C1136, C1137, C1138, C1139, C1140, C1141, C1146, C1147, C1148, C1264, C1695, C1696, C1701, C1702, C1705, C1706, C1709, C1711
- positional: C260, C346, C420, C421, C424, C484, C946, C1266

### Disallowed Interpretations (11)
- "A tokens map to B folios (context-free)" []
- "Repetition encodes quantity or ratio" []
- "A has sequential grammar (token-to-token)" []
- "Prefixes are semantic categories" []
- "A is lookup table for B" []
- "A encodes danger or hazard" []
- "Control operators are headers or section markers" []
- "A is generative or producible" []
- "B mode A/B distinction organizes A records" [C1267]
- "Prefix family (ch/sh) selects operational category context" [C1268]
- "A discrimination manifold clustering reflects structural features beyond frequency-weighted co-occurrence" [C1696, C1701]

---

## BCSC (Currier B Structural Contract)
**Meta:** v3.35, ACTIVE, 61.9% of tokens, 83 folios

### Guarantees (35)
- GRAMMAR_UNIVERSAL: 49-class grammar applies to all 83 folios without exception [C121, C124]
- FORTY_NINE_CLASS_OPTIMALITY: 49-class is the optimal resolution for transition dynamics; token-level Markov is 38% worse due to sparsity; suffix cond [C1004]
- TOTAL_COVERAGE: Every Currier B token parses; zero non-executable [C115, C124]
- CONVERGENT_ARCHITECTURE: Grammar targets single stable state (STATE-C) — reframed as AXM thematic dominance, not sequential convergence (C1403) [C074, C079, C084, C1403]
- HAZARD_TOPOLOGY_FIXED: 17 forbidden class-level transitions are directional (C783); the underlying MIDDLE-level forbidden pairs are predominant [C109, C783, C789, C1118, C2023]
- KERNEL_CENTRALITY: k, h, e form irreducible morphological core governing within-token construction [C089, C521, C522]
- LINE_FORMALITY: Lines are formal control blocks, not scribal wrapping [C357-C360]
- LINK_PHASE_MARKER: LINK marks boundary between monitoring and intervention [C366]
- DESIGN_ASYMMETRY: Hazard exposure clamped; recovery architecture free [C458]
- CONDITIONAL_ENTROPY_SYMMETRIC: Grammar constraints are bidirectional (H(X|past)=H(X|future)), but execution is directional (transition probabilities un [C391, C886, C1024]
- CLOSED_LOOP_ONLY: Execution is closed-loop control, not batch, decision tree, or state machine [C171]
- PROCESS_CONTROL_DIMENSIONALITY: Voynich B is a parameterized process control manual: PCA dimensionality (5 PCs/80%) matches modern distillation with dif [C1222, C1223, C1224]
- MACRO_AUTOMATON_COMPRESSION: 49 instruction classes compress to 6 macro-states (8.17x) with spectral gap 0.896; EN/AX merge, FL splits HAZ/SAFE; non- [C976, C977, C978, C1006, C1010, C1011, C1015, C1016, C1022, C1025]
- GENERATIVE_SUFFICIENCY_AND_NECESSITY: The 49-class first-order Markov transition matrix + 17 forbidden MIDDLE pair suppression is both SUFFICIENT (reproduces  [C1025, C1026]
- MACRO_STATE_DYNAMICS: 6-state macro-automaton has full 6×6 transition matrix: AXM is a massive attractor (self=0.697, gravitational pull=0.642 [C1015, C1016, C1017]
- FL_ROUTING_ASYMMETRY: FL_HAZ/FL_SAFE split is morphologically routed by PREFIX: da is the unique bi-directional FL router (5 HAZ, 5 SAFE, Fish [C1015, C586]
- PREFIX_MDL_OPTIMALITY: PREFIX is the MDL-optimal single morphological component for macro-state routing at corpus scale (N=16,054): rank 1/4, 3 [C1015]
- BRIDGE_CONDUIT_MECHANISM: Bridge MIDDLE backbone (85 MIDDLEs spanning A→B) mediates geometry→dynamics coupling at folio level: bridge-only manifol [C1016, C1017, C1018, C1020, C1013, C1014]
- FOLIO_DYNAMICAL_ARCHETYPES: 72 folios with sufficient transitions (N≥50) cluster into 6 dynamical archetypes organized along an AXM attractor streng [C1016, C1017, C1018]
- AFFORDANCE_BIN_SYSTEM: 972 MIDDLEs classify into 9 functional bins by affordance signature; chromatic number 3 for PREFIX-lane interaction; HUB [C995, C996, C997, C1000]
- PREFIX_DUAL_ENCODING: PREFIX simultaneously encodes content (lane, suffix compatibility) and line position; positional grammar is regime-invar [C1001]
- FOLIO_VOCABULARY_UNIQUENESS: 98.8% of folios contribute unique vocabulary appearing in no other folio [C531, C532]
- FOLIO_COUNT_STRUCTURAL: 83 folios determined by vocabulary coverage, not arbitrary [C535]
- CLASS_MEMBER_DIFFERENTIATION: Grammar universal at class level; differentiation occurs at token level within classes [C506.b, C537]
- EXECUTION_SYNTAX: Lines follow a positional role grammar: SETUP→WORK→CHECK→CLOSE [C556]
- AX_BEHAVIORAL_COLLAPSE: 19 AX classes collapse to ≤2 effective behavioral groups; position is the only differentiator [C572]
- AX_VOCABULARY_SCAFFOLD: AX is the scaffold layer of the shared cross-system vocabulary: 98.2% PP MIDDLEs, PREFIX-determined role [C567, C568, C571]
- MORPHOLOGICAL_COMPOSITIONALITY: Every token decomposes into [ARTICULATOR] + PREFIX + MIDDLE + [SUFFIX] with predictable combination rules [C267, C382, C383]
- PREFIX_INTERNAL_GRAMMAR: PREFIX uses 15 characters (identical inventory across A/B/AZC, Jaccard=1.000) in a three-tier positional grammar: 7 MODI [C1218, C1219, C1220, C1221, C1534, C1535, C1536, C1537, C1538, C1539]
- PAIRWISE_COMPOSITIONALITY: TOKEN information is fully captured by pairwise component interactions (PREFIX x MIDDLE, PREFIX x SUFFIX, MIDDLE x SUFFI [C1003]
- PREFIX_MIDDLE_SELECTIVITY: PREFIX selects MIDDLE family (102 forbidden combinations) and transforms MIDDLE behavior (within-MIDDLE between-PREFIX J [C911, C661, C1012, C1015, C1017]
- PARAGRAPH_EXECUTION_GRADIENT: Paragraph body lines follow a specification→execution gradient: early lines have rare/unique vocabulary (specification), [C932, C933, C934]
- PARAGRAPH_SUFFIX_CYCLING: 100% of paragraphs with 8+ body lines contain two suffix modes (k=2, silhouette 0.459). Mode A (THERMAL/MONITORING atoms [C1227, C1228, C1229, C1230, C1231, C1232, C1422, C1423, C1424]
- HT_OPERATIONAL_REDUNDANCY: HT/compound tokens contain operational content that is redundant with body simple MIDDLEs (71.6% atom hit rate vs 59.2%  [C404, C935]
- MIDDLE_INSTRUCTION_ENCODING: Compound MIDDLEs encode instructions as HEAD + MOD* + TERM: 18 atoms in 4 slot roles (5 HEAD, 6 MOD, 6 TERM, 2 dual). Fi [C1393, C1394, C1440, C1441, C1442, C1443, C1475, C1476, C1477, C1478, C1479, C1483, C1484, C1485, C1486, C1487, C1488, C1489, C1490, C1491, C1492, C1493, C1510, C1511, C1512, C1513, C1514, C1515]

### Invariants (23)
- grammar_universality: Same 49 classes apply to every folio [C124]
- convergence_dominance: Majority of programs terminate in STATE-C (AXM thematic dominance, not sequential convergence — C140 [C074, C084, C323, C1403]
- hazard_asymmetry: Most forbidden transitions are directional [C111]
- line_invariance: Grammar violations do not cross line boundaries [C360]
- constraint_symmetry: Grammar constraints are bidirectional; execution is directional. PREFIX routes symmetrically; MIDDLE [C391, C886, C1024]
- kernel_boundary_adjacency: Classes containing kernel characters tend to be hazard-involved [C107, C522]
- class_member_differentiation: Grammar is universal at class level, differentiation at token level [C506.b, C537]
- folio_vocabulary_minimality: 81/82 folios required for complete vocabulary coverage [C535]
- execution_syntax: Lines follow SPECIFICATION→THERMAL_WORK→CLOSURE positional grammar with category-level resolution [C556, C562, C1425, C1426, C1427, C1428, C1429, C1430]
- energy_flow_anticorrelation: ENERGY and FLOW roles are anticorrelated across sections [C551]
- ax_behavioral_collapse: 19 AX classes do not form distinct behavioral groups [C572]
- regime_syntax_invariance: Line syntax is INVARIANT across all four REGIMEs [C821]
- regime_cc_position_invariance: CC token positions are INVARIANT across REGIMEs [C822]
- regime_bigram_partial_variation: Bigram transition patterns show PARTIAL REGIME variation [C823]
- morphological_compositionality: TOKEN = [ARTICULATOR] + PREFIX + MIDDLE + [SUFFIX] is universal [C267, C382]
- prefix_middle_selectivity: PREFIX constrains which MIDDLE families are allowed (102 forbidden pairs) [C911]
- prefix_positional_grammar: PREFIX encodes line position independently of regime [C1001]
- prefix_base_modifier_grammar: PREFIX characters partition into three tiers: 7 MODIFIER (POS-0), 2 BASE (POS-1+), 6 DUAL (both); ba [C1218, C1219, C1534, C1535, C1536, C1537, C1538]
- suffix_mode_universality: Two suffix modes (specification/continuation) are universal across all paragraphs with sufficient bo [C1229, C1231, C1422, C1423]
- pairwise_interaction_sufficiency: Pairwise morphological component interactions capture all exploitable TOKEN structure; no three-way  [C1003]
- prefix_routing_regime_invariance: PREFIX macro-state routing magnitude is invariant across REGIMEs (range 0.785–0.832, ratio=1.06); RE [C1017]
- dwell_shape_regime_invariance: Weibull dwell shape (k=1.55) is invariant across REGIMEs; REGIME modulates scale only [C1006]
- generative_specification_bracketed: The grammar's minimal executable specification is bracketed: 49-class Markov + 17 forbidden pairs is [C1025, C1026]

### Sections -> Constraints
- grammar: C085, C121, C124, C411, C1004
- morphology: C267, C382, C383, C408, C506, C522, C588, C661, C662, C777, C787, C897, C911, C929, C935, C936, C1001, C1004, C1015, C1017, C1065, C1141, C1142, C1190, C1191, C1193, C1218, C1219, C1220, C1221, C1227, C1393, C1394, C1396, C1416, C1417, C1418, C1419, C1420, C1421
- middle_instruction_encoding: C1003, C1393, C1394, C1395, C1397, C1408, C1409, C1410, C1411, C1412, C1413, C1414, C1415, C1416, C1417, C1418, C1419, C1420, C1421, C1440, C1441, C1442, C1443, C1444, C1445, C1472, C1473, C1474, C1475, C1476, C1477, C1478, C1479, C1483, C1484, C1485, C1486, C1487, C1488, C1489, C1490, C1491, C1492, C1493, C1494, C1495, C1496, C1497, C1498, C1507, C1510, C1511, C1512, C1513, C1514, C1515, C1523, C1524, C1525, C1526, C1527, C1556, C1557, C1558, C1559, C1560, C1561, C1562, C1563, C1564
- role_taxonomy: C121, C366, C547, C550, C557, C558, C560, C562, C563, C567, C572, C573, C574, C575, C581, C582, C583, C584, C586, C587, C588, C591, C593, C594, C595, C597, C770, C777, C788, C791, C863, C864, C865, C866, C867, C868, C869
- kernel: C089, C103, C104, C105, C332, C333, C339, C521, C1225, C1226
- hazards: C109, C110, C111, C112, C386, C789, C1446, C1447, C1448, C1449, C1450, C1451, C1452, C1453, C1454, C1455, C1456, C1457, C1458, C1459, C1460, C1461, C1462, C1477, C1479, C1480, C1481, C1482, C1528, C1529, C1530, C1531, C1532, C1533, C1546, C1547, C1551, C1554, C2060
- program_structure: C178, C357, C358, C359, C360, C531, C535, C556, C557, C561, C562, C670, C673, C677, C777, C815, C840, C841, C842, C843, C845, C855, C856, C857, C858, C859, C860, C861, C862, C864, C870, C897, C932, C933, C935, C956, C957, C958, C959, C960, C961, C962, C963, C964, C965, C966, C971, C972, C975, C1121, C1221, C1227, C1228, C1229, C1230, C1231, C1232, C1233, C1236, C1237, C1256, C1258, C1259, C1260, C1288, C1308, C1309, C1310, C1311, C1312, C1378, C1396, C1398, C1399, C1400, C1410, C1422, C1423, C1424, C1425, C1426, C1427, C1428, C1429, C1430, C1434, C1435, C1436, C1437, C1438, C1439, C1451, C1463, C1464, C1465, C1466, C1467, C1468, C1469, C1470, C1471, C1566
- convergence: C079, C084, C323, C325, C1169, C1401, C1402, C1403, C1404, C1405, C1406, C1407, C1411, C1418, C1422, C1431, C1432, C1433
- link_operator: C340, C365, C366, C609, C804, C805, C806, C807, C808, C809, C810, C1170, C1171, C1172, C1173, C1174
- recovery: C105, C397, C398, C399, C601, C643, C645, C1457, C1458, C1459, C1462
- safety_buffer_architecture: C997, C1000, C1009, C1018
- axm_internal_architecture: C979, C1006, C1007, C1008, C1009, C1016, C1017, C1023
- macro_state_transition_matrix: C1015
- apparatus_response_architecture: C1636, C1638, C1639, C1640, C1646, C1652, C1666, C1667, C1670, C1709, C1710, C1711
- three_compression_architecture: C984, C986, C1000, C1003, C1004, C1010, C1013, C1019, C1020, C1021, C1139, C1141, C1190, C1191, C1499, C1500, C1501, C1503, C1504, C1505, C1506, C1507, C1508, C1509, C1690, C1691, C1695, C1696, C1701
- design_freedom: C121, C458, C929, C1016, C1017, C1018, C1163, C1165, C1169, C1179, C1180, C1181, C1182, C1183, C1184, C1185, C1186, C1187, C1188, C1189
- control_loop: C807, C810, C811, C813, C814, C815, C816, C873, C1204, C1205, C1225, C1226, C1234, C1235, C1237, C1238
- section_profiles: C551, C552, C553, C554, C555, C909, C1049, C1134
- process_characterization: C1222, C1223, C1224
- vocabulary_architecture: C121, C124, C506, C531, C532, C533, C535, C537, C959, C1013, C1016, C1035, C1134, C1135, C1136, C1137, C1139, C1140, C1146, C1149, C1150, C1151, C1152, C1153, C1154, C1155, C1156, C1157, C1158, C1159, C1160, C1161, C1162, C1163, C1164, C1165, C1166, C1167, C1168, C1169, C1431, C1432, C1433
- ht_un_integration: C209, C404, C405, C475, C740, C742, C743, C744, C746, C747, C794, C795, C812, C870, C871, C872, C935, C1028, C1065, C1134, C1137, C1138, C1141, C1142, C1143, C1144, C1145, C1146, C1147, C1148, C1175, C1176, C1177, C1178, C1254, C1255, C1499, C1500, C1501, C1502, C1505
- robustness: C328, C329, C330, C331, C506, C908, C910, C911
- operational_layer: C382, C588, C936, C1225, C1226, C1250, C1251, C1252, C1253
- category_execution: C601, C929, C1169, C1184, C1268, C1277, C1278, C1279, C1280, C1281, C1282, C1283, C1285, C1286, C1287, C1288, C1289, C1290, C1291, C1292, C1293, C1294, C1297, C1298, C1299, C1300, C1301, C1302, C1303, C1304, C1305, C1306, C1307

### Disallowed Interpretations (16)
- "B grammar varies by Currier A source" [C124]
- "B grammar varies by AZC context" [C121, C124]
- "Families are different grammars" [C141]
- "Grammar encodes semantic content" [C120]
- "Grammar is directional (narrative)" [C391]
- "Grammar is a decision tree or state machine" [C171]
- "AX classes represent distinct behavioral modes" [C572]
- "C559 FQ membership {9,20,21,23} is correct" [C583, C592]
- "HT tokens are non-operational (contain no operational content)" [C935, C404 (revised)]
- "PREFIX is a passive label with no behavioral effect" [C661, C911]
- "ok encodes a verb (seal/lock/close/cover) with MIDDLE as modifier" [C936 (revised)]
- "FL_SAFE is an absorbing or long-duration collection state" [C1015]
- "Prep PREFIXes (pch, tch, dch, te, lch) encode distinct physical operations" [C1221]
- "Apparatus families are discrete species with crisp boundaries" [C1640]
- "Manifold clustering is primarily structural beyond frequency effects" [C1696]
- "Atom morphological composition determines MIDDLE co-occurrence" [C1695]

---

## AZC-ACT (AZC Positional Classification Contract)
**Meta:** v1.5, ACTIVE, 

### Guarantees (11)
- VOCABULARY_ACTIVATED: AZC constraint activation is vocabulary-driven [C441]
- COMPATIBILITY_GROUPING: AZC folios group vocabulary by compatibility signature [C442]
- LEGALITY_CORRELATION: AZC positional vocabulary profiles correlate reliably with B behavior (28x escape rate difference) [C468]
- NO_CONTENT_MUTATION: AZC does not mutate A entry contents [C444]
- FAMILY_AGNOSTIC_MECHANISM: AZC legality mechanism is family-agnostic [C430-C436, C441-C443]
- ZONE_CATEGORY_SPECIALIZATION: AZC zones (R, C, S, P) have statistically distinct operational category profiles (V=0.084, p=0.000180) [C1269]
- FAMILY_CATEGORY_DIVERGENCE: Zodiac and A/C families have distinct category profiles (V=0.122, p=0.000001) despite family-agnostic mechanism [C1270]
- BRIDGE_DARK_ZONE_SORTING: AZC zones mediate bridge/dark category sorting; bridge sorted by category within zones (p=0.0003), dark not (p=0.198) [C1272]
- EXCLUSIVE_VOCABULARY_SPECIALIZED: 356 AZC-exclusive MIDDLEs are MARKING/THERMAL enriched, TRANSITION-depleted (V=0.382 vs bridge) [C1273]
- HEAD_DOMAIN_DIFFERENTIATION: AZC zones differentiate at HEAD domain level (chi2=112.3, V=0.115, p=5.81e-17) despite sharing raw atom proportions (C12 [C1516, C1517, C1518]
- ZONE_SYSTEM_PROXIMITY_PARTITION: AZC zones partition into B-proximate (R, P: lower o-HEAD, more bridge) and A-proximate (C, S, L: higher o-HEAD, more dar [C1522]

### Invariants (7)
- monotonicity: Survivor options never increase from earlier to later positions [C443, C444]
- position_independence: The SAME A-type can appear in any position; position determines legality, not content [C444]
- vocabulary_mediation: All A->B relationships are vocabulary-mediated, not addressable [C384, C441]
- scaffold_independence: Legality zones are independent of scaffold presentation [C430-C436]
- zone_atom_uniformity: AZC zones share the same raw atom-level (character) proportions (C1271) but differentiate at HEAD sl [C1271, C1516]
- no_spatial_coherence: Category assignment is spatially random within zones; organization is zone-grain not line-grain [C1275]
- pharma_atom_convergence: All AZC sections converge on Currier A Pharma section atom profile (r>0.916) [C1276]

### Sections -> Constraints
- category_organization: C1269, C1270, C1271, C1272, C1273, C1276, C1516, C1517, C1518, C1519, C1520, C1521, C1522, C1559
- inputs: C482, C484
- positional_zones: C306, C313, C317, C320, C432, C434, C435, C443
- transformations: C442, C443, C444, C469, C475, C481, C502
- persistence: C343, C444, C470
- morphological_binding: C471, C472, C473

### Disallowed Interpretations (8)
- "AZC owns vocabulary" [C441, CASC]
- "AZC selects procedures" [C473]
- "Position encodes meaning" [C313]
- "AZC is addressable lookup from A entries to B programs" [C384, C441]
- "AZC decides dynamically" [F-AZC-015]
- "AZC expands vocabulary beyond A specification" [C481, C502]
- "AZC diagram lines are thematically organized" [C1275]
- "AZC zones differ at raw atom (character frequency) level" [C1271, C1516]

---

## AZC-B-ACT (AZC-B Vocabulary Correlation Contract)
**Meta:** v1.5, ACTIVE, 

### Guarantees (6)
- LEGALITY_CORRELATION: Vocabulary classified at high-escape AZC positions produces high escape rates in B (28x difference); both determined by  [C468]
- RESTRICTION_PRESERVATION: MIDDLE restrictions transfer intact to B [C470]
- GRAMMAR_INDEPENDENCE: B grammar is unchanged by AZC legality [C121, C124]
- BLIND_EXECUTION: B executes without knowledge of upstream mechanics [C384, C468]
- CATEGORICAL_RESOLUTION: Resolution via vocabulary availability, not parameters [C469]
- CATEGORY_ESCAPE_CORRELATION: Operational category composition of AZC-shared vocabulary predicts B escape rate: THERMAL (rho=+0.780) high escape, TRAN [C1274]

### Invariants (5)
- vocabulary_mediated_correlation: AZC positional classification and B intervention dynamics co-vary via shared vocabulary properties [C468]
- restriction_correlation: Vocabulary restrictions correlate across AZC and B contexts [C470]
- grammar_stability: B grammar rules apply universally regardless of AZC source [C124]
- non_parametric: No numeric values are encoded; all distinctions are categorical [C469]
- no_token_transmission: No tokens are transmitted from Currier A to Currier B [C384, C281, C285, C343]

### Sections -> Constraints
- b_reception: (no constraint refs)
- inputs: C443, C468, C470
- correlation: C444, C468, C469, C470, C481, C502, C1134, C1137, C1140, C1146, C1148, C1274, C1277, C1280, C1281, C1285
- b_reception_architecture: C105, C397, C398, C458
- b_isolation: C384, C469

### Disallowed Interpretations (8)
- "B sees A entries" [C384]
- "B can infer AZC position" [C468]
- "AZC modifies B grammar" [C121, C124]
- "Recovery budget is a quantitative resource" [C469]
- "Legality is a state variable in B" [C468, C469]
- "Numeric thresholds are contractual" [C469]
- "AZC expands B vocabulary beyond A specification" [C481, C502]
- "Category composition is orthogonal to B escape dynamics" [C1274]

---

## HTSC (Human Track Structural Contract)
**Meta:** v1.1, ACTIVE, 

### Guarantees (17)
- POPULATION_IDENTITY: HT = UN (identical by definition); 4,421 types, 7,042 occurrences in B (30.5%) [C740]
- UNIFIED_VOCABULARY: Same HT prefix inventory across A, B, and AZC systems (Jaccard >= 0.947) [C452]
- SINGLE_LAYER: HT forms one coherent layer, not multiple overlapping systems [C168]
- OPERATIONAL_REDUNDANCY:  [C404, C405, C935]
- CAUSAL_DECOUPLING: HT presence does not alter subsequent grammar probabilities (V=0.10, negligible) [C405]
- NON_PREDICTIVE: HT does not improve prediction of subsequent content; MAE worsens by 0.003-0.005 [C415]
- DIRECTIONAL_DOWNSTREAM: Coupling is unidirectional: System->HT (V=0.324), HT->System (V=0.202), ratio 1.6x [C416]
- HAZARD_AVOIDANCE:  [C166, C169, C1078]
- LINE1_ENRICHMENT: Line-1 has 50.2% HT vs 29.8% on lines 2+ (+20.3 pp) [C747]
- LINE1_STEP_FUNCTION: Enrichment is confined to position 1 only: pos1=50.2%, pos2=31.7%, pos3+=27-33% [C748]
- OPENING_ONLY: No closing enrichment: last line 30.8% = interior 29.8% [C750]
- LINE1_COMPOSITE_HEADER:  [C794, C795, C799]
- COMPOSITIONAL_GENERATIVITY: HT follows Zipf distribution (exponent 0.892, R-sq=0.92) with 67.5% hapax rate [C406]
- COMPOUND_SPECIFICATION:  [C935, C1137, C1141]
- QUIRE_ORGANIZED: HT shows codicological clustering at the quire level [C450]
- ANTICIPATORY_COMPENSATION: HT anticipates B stress at quire level (r=0.343, p=0.0015) [C459]
- TAIL_CORRELATION: HT density tracks MIDDLE rarity (r=0.504, p=0.0045); tail_pressure explains 68% of R-sq=0.279 [C477, C461]

### Sections -> Constraints
- cross_system_manifestation: C341, C342, C344, C347, C348, C413, C419, C457, C459, C460, C488, C507, C747, C748, C749, C750, C794, C795, C796, C797, C798, C799, C800, C802, C806, C812, C844, C870, C924, C926, C927, C1137, C1138, C1146, C1147, C1148
- paragraph_header: C085, C801, C802, C803, C840, C842, C843, C851
- morphology: C347, C417, C418, C766, C935, C1138, C1141, C1142
- operational_status: C209, C221, C404, C405, C415, C792, C935, C1137, C1141
- two_axis_model: C461, C477, C488, C489, C935, C1080
- disallowed_interpretations: C166, C217, C221, C406, C414, C415, C416, C418, C452, C459, C611, C740, C935
- summary: (no constraint refs)

---

## PSC (Paragraph Structural Contract)
**Meta:** v1.2, ACTIVE, 

### Guarantees (16)
- OPERATIONAL_UNIT:  [C827, C834]
- GALLOWS_DELIMITED:  [C864, C841]
- HEADER_BODY:  [C840, C848, C854]
- COMPOUND_SPECIFICATION:  [C935, C848]
- PARALLEL_PROGRAMS:  [C855, C862]
- SELF_CONTAINMENT:  [C845]
- VOCABULARY_DISTRIBUTION:  [C856]
- FIRST_ORDINARINESS:  [C857]
- BODY_HOMOGENEITY:  [C963, C1295]
- POOL_RELATIONSHIP:  [C846]
- STRUCTURAL_PARALLEL:  [C854, C850, C853]
- SECTION_PARAMETERIZED:  [C860, C852]
- LINK_HAZARD_HT_NEUTRAL:  [C861, C1083]
- MACRO_DYNAMICS_NEUTRAL:  [C1022]
- TERMINATION_MEMORYLESS:  [C1295, C1296, C1237, C1239]
- CLUSTER_SELECTIVE:  [C1039, C1052]

### Sections -> Constraints
- cross_system_manifestation: C812, C840, C841, C842, C843, C844, C847, C848, C849, C850, C851, C852, C853, C863, C869, C881, C884, C893, C915, C932, C933, C934, C935, C944, C1039, C1040, C1041, C1052, C1054, C1258, C1259, C1260
- a_b_correspondence: C846, C854, C885
- folio_paragraph_organization: C855, C856, C857, C858, C859, C860, C861, C862
- stability_properties: C963, C1022, C1027, C1054
- disallowed_interpretations: C120, C171, C846, C855, C857, C858, C861, C862, C863, C963, C1027, C1295
- summary: C1239, C1296


---
