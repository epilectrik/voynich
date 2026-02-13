# Understanding the Voynich Manuscript: A Guide

This document explains the project's findings for readers who want to understand what the Voynich Manuscript encodes without navigating 879 constraint files. Everything here is grounded in statistical evidence from the transcript data.

For the full constraint system and technical details, see `context/CLAUDE_INDEX.md`.

---

## The Short Version

The Voynich Manuscript is not a language. It is not a cipher. It is a **control system reference manual** — a collection of written programs that tell an operator how to maintain a physical process (most likely reflux distillation) within safe operating limits.

The manuscript is organized into four structurally distinct layers, each serving a different function. Together they form a system that works **in silence**: the operator never needs to read explanations because the structure itself encodes what to do, when to intervene, and what to avoid.

---

## The Four Layers at a Glance

| Layer | System | What It Does |
|-------|--------|-------------|
| **Execution** | Currier B | The programs themselves — adaptive control procedures |
| **Distinction** | Currier A | An independent registry of fine distinctions, organized by discrimination domains |
| **Context** | AZC | A positional lookup table classifying vocabulary by operational character |
| **Orientation** | HT (Human Track) | Keeps the human operator oriented during production |

These layers never explain each other. B doesn't reference A. A doesn't mention AZC. They interact through vocabulary constraints — what tokens are available in what positions — not through explicit cross-references.

---

## Currier B: The Execution Layer

**What it is:** 23,243 tokens across 83 folios (61.9% of the manuscript). Every folio is a complete, self-contained program. Every program uses the same grammar.

**What it does:** Each program guides an operator through a closed-loop control process — applying energy, monitoring state, checking for hazards, and recovering when things drift. The programs don't describe a process linearly; they encode adaptive responses to whatever state the system is in.

### How Tokens Work

Every Currier B token is compositional. It decomposes into parts that each carry structural information:

```
[ARTICULATOR] + [PREFIX] + MIDDLE + [SUFFIX]
```

- **PREFIX** selects the operational channel AND encodes line position. It determines which family of core actions is grammatically legal (one prefix selects energy operations, another selects monitoring) while simultaneously encoding where in the line the token appears — prefixes cluster into initial, central, and final positional zones. There are 8 prefix families organized into functional groups (including sister pairs ch/sh and ok/ot that function as equivalent mode selectors).
- **MIDDLE** is the primary discriminative content — the specific action variant within the channel the prefix opened. Approximately 30 core MIDDLEs handle 67.6% of all tokens, with a long tail of ~1,150 rarer variants.
- **SUFFIX** encodes context-dependent markers that relate to control flow — what happens next, how broad the operation's scope is.
- **ARTICULATOR** is an optional refinement layer that doesn't change the core meaning.

### The 49 Instruction Classes

All 479 distinct token types collapse into 49 instruction classes with zero loss of grammatical predictive power — a 9.8x compression ratio. This means the manuscript's apparent vocabulary diversity is compositional variation within a small, strict grammar, not a large open vocabulary.

The classes fall into five functional roles:

| Role | Classes | Share of B | Function |
|------|---------|-----------|----------|
| ENERGY_OPERATOR | 18 | 31.2% | Energy modulation |
| AUXILIARY | 19 | 16.6% | Scaffold and infrastructure support |
| FREQUENT_OPERATOR | 4 | 12.5% | Common control instructions |
| CORE_CONTROL | 4 | 4.4% | Execution boundaries |
| FLOW_OPERATOR | 4 | 4.7% | Flow control and escape routes |

### Six-State Macro Grammar

The 49 instruction classes further compress into just 6 macro states — the coarsest description of what any token is doing:

| State | What It Does | Share |
|-------|-------------|-------|
| **AXM** | Major scaffold — structural support | Largest group |
| **AXm** | Minor scaffold — infrastructure | |
| **FQ** | Frequency — common operations | |
| **CC** | Control change — execution boundaries | |
| **FL_HAZ** | Hazard flow — dangerous transitions | Smallest groups |
| **FL_SAFE** | Safe flow — escape routes | |

This compression preserves all structural invariants — role families, depletion separation, and hazard topology are intact at 6 states. Fine-grained depletion asymmetry (a 49-class-level phenomenon) is not captured. The macro grammar reveals that the majority of the manuscript is scaffold (structural support), with only a small fraction devoted to hazard exposure or active control changes. A researcher scanning a folio can immediately classify every token into one of these six categories to see the macro structure of the program.

### The Kernel: Three Core Operators

At the center of the grammar sit three irreducible operators, designated **k**, **h**, and **e**:

- **k** adjusts energy input (appears early in lines)
- **h** manages phase transitions (appears in the middle)
- **e** anchors stable state and drives recovery (appears late — tokens containing the e operator account for 36% of all B tokens)

These three operators define the grammar's backbone. They are bound morphemes — they never appear as standalone tokens, only as components within larger compositional words. The transition e-to-h is completely blocked (ratio 0.00), while h-to-k is strongly suppressed — the system acts as a one-way valve where energy flows toward stability but not back. Within token construction, the trigram e-e-e accounts for 97.2% of all kernel character sequences. The system overwhelmingly favors stability.

### Hazard Topology

The grammar enforces 17 forbidden transitions organized into 5 hazard classes:

| Class | What Goes Wrong |
|-------|----------------|
| PHASE_ORDERING | Material in the wrong phase location |
| COMPOSITION_JUMP | Impure fractions passing through |
| CONTAINMENT_TIMING | Overflow or pressure events |
| RATE_MISMATCH | Flow imbalance destabilizing the system |
| ENERGY_OVERSHOOT | Thermal damage to material |

Most hazards describe difficult-to-reverse failures — material contamination, phase disorder, or thermal damage. The grammar strongly disfavors these transitions (~65% compliance rate), though they are not absolutely prohibited. One hazard class (RATE_MISMATCH) describes recoverable imbalances rather than permanent damage. The entire grammar is organized around minimizing exposure to these transitions.

All 17 forbidden transitions are mediated through 23 "hub" MIDDLEs — the most connected vocabulary items that appear across all instruction classes. These hub MIDDLEs decompose into four functional sub-roles: hazard sources (6), hazard targets (6), safety buffers (3), and connectors (8). The hazard topology is entirely a hub phenomenon — non-hub MIDDLEs never participate in forbidden transitions.

### Program Structure

Each folio is a program. Each line within a folio is a formal control block (3.3x more regular than random line breaks). Lines follow a consistent execution pattern:

```
SETUP → WORK → CHECK → CLOSE
```

Lines group into paragraphs, which function as mini-programs with their own internal structure: a header line followed by body lines that execute operations. Header lines use distinctive vocabulary — 50.2% of first-line tokens come from a specialized identification vocabulary, compared to 29.8% in body lines. The structure suggests that headers specify what the paragraph will do, with body lines carrying out the operations in simpler individual tokens.

### Recovery Architecture

When the system drifts toward a hazard, the grammar provides escape routes. The key design principle is:

- **Hazard exposure is globally constrained** — the same 17 forbidden transitions apply everywhere
- **Recovery strategy is locally variable** — each program can recover in its own way

This means the manuscript clamps risk uniformly while leaving operators free to adapt their recovery approach to local conditions. Recovery paths converge on the **e** operator (stable state) in 54.7% of cases.

### What B Cannot Tell You

The grammar is purely operational. It encodes control-flow structure but not the identity of what is being controlled. You can determine that a program applies energy, monitors state, and avoids contamination — but you cannot determine what substance is being processed. This is not a gap in the analysis — the system was designed to work without encoding what is being processed. The operator's trained judgment supplies the meaning that the grammar deliberately omits.

---

## Currier A: The Distinction Layer

**What it is:** 11,415 tokens across 114 folios (30.5% of the manuscript). Completely separate from Currier B — zero shared folios.

**What it does:** Currier A is an **independent registry of fine distinctions**. It catalogs differences at a resolution far beyond what any execution grammar could track. Think of it as a discrimination index: where an execution system might have one instruction for "apply heat," A distinguishes between dozens of cases where that might mean subtly different things.

### Why A Exists

Currier A operates at a finer resolution than any execution grammar could support. Where an execution system tracks phase, energy, flow, and recovery at the class level, A catalogs case-by-case distinctions that are decision-relevant in practice.

The registry is organized around a **discrimination gradient** — operations requiring fine discrimination need far more vocabulary than stable reference operations. 95.7% of all MIDDLE pairs are illegal co-occurrences, enforcing strict boundaries between discrimination domains.

### How A Is Organized

Each line in Currier A is an independent record — there are no inter-line dependencies (mutual information = 0 across lines). Records follow a simple grammar:

```
[opener] + [prefixed content] + [closer]
```

99.4% of records are multi-token registry entries defining fine distinctions. The remaining 0.6% are single-token control operators that organize the registry itself.

A uses the same morphological system as B (PREFIX + MIDDLE + SUFFIX) but with different behavior. 60.1% of A's MIDDLEs never appear in B at all — they exist only within the registry, cataloging distinctions at a resolution the registry alone requires.

### How A Relates to B

A and B share vocabulary but not structure:

- **No entry-level coupling**: A entries don't map to specific B folios through simple lookup
- **Shared vocabulary pool**: A and B draw from a common vocabulary (69.8% overlap at the type level), but neither references the other
- **Massive filtering**: Where vocabulary overlaps, morphological compatibility rules restrict co-occurrence so heavily that 94.7%–99.2% of combinations are excluded

The most likely relationship is **construction-time, not runtime**: A served as a reference vocabulary when the B programs were originally written. The author consulted A's discrimination index, checked AZC's positional classification, and composed B programs from that vocabulary. Once written, B programs are fixed and self-contained — there is no active "compilation" from A data during execution. A may also have served as a lookup reference for an operator encountering an unfamiliar token while running a procedure.

This explains why the vocabulary overlap is clearly deliberate (69.8%) but no runtime coupling mechanism can be found — the coupling existed at authorship time, not execution time. (Tier 3 interpretation.)

### What A Is Not

- Not a glossary or translation table
- Not a list of ingredients or materials
- Not temporally ordered (no early/late sequence)
- Not semantically meaningful — it catalogs distinctions without identifying what they distinguish

---

## AZC: The Context Layer

**What it is:** 3,299 tokens across 30 folios (8.7% of the manuscript). These are the Zodiac, Astronomical, and Cosmological pages — the diagram-heavy folios with circular layouts, star charts, and concentric rings.

**What it does:** AZC is a **static lookup table** — a positional encoding where each PREFIX+MIDDLE combination maps to exactly one position. It doesn't execute procedures (that's B), catalog distinctions (that's A), or actively filter anything. AZC positions **reflect** the operational character of the vocabulary placed there; they don't cause it.

### Two Families

AZC splits into two architecturally distinct families with no intermediates:

**Zodiac Family (13 folios):** The 12 zodiac pages plus f57v. These use the same rigid template repeated 12 times — a uniform scaffold with ordered ring positions (R1 → R2 → R3, strictly forward, no backward transitions allowed). Cross-folio similarity: 0.945 (near-identical structure).

**A/C Family (17 folios):** The astronomical and cosmological pages. Each folio has its own unique rigid structure — a varied scaffold where every diagram enforces custom placement constraints. Cross-folio similarity: 0.340 (each diagram is architecturally distinct).

Both families are equally rigid (98%+ self-transition rates). The difference is whether the rigidity is uniform (Zodiac) or diagram-specific (A/C).

### What AZC Positions Mean

Each AZC position clusters vocabulary with a distinct operational character:

| Position | Character | Key Indicators |
|----------|-----------|----------------|
| **S-series** | Stabilization / boundary | Highest scaffold support (35-45%), lowest energy operations (6-12%) |
| **R-series** | Processing / interior | Balanced profile, moderate kernel contact |
| **C** | Core / central | Balanced across all operational axes |

Critically, **position has zero independent effect on behavior**. After controlling for which MIDDLEs appear at a position, the position itself adds no predictive power for how those tokens behave in Currier B. Position reflects what the vocabulary already is — it doesn't transform it.

### AZC and Currier B

AZC does not modify, filter, or constrain Currier B programs. B programs are fixed — each folio is a complete, pre-written program. AZC and B share vocabulary (69.7% overlap) because they draw from the same operational domain, not because AZC feeds into B.

The relationship is classificatory, not causal: AZC organizes vocabulary by operational character in diagram form, while B deploys the same vocabulary in sequential programs. 77% of MIDDLEs appear in only one AZC folio, and each PREFIX+MIDDLE combination maps to exactly one position — making AZC an unambiguous reference system.

### What AZC Rules Out

The extreme structural rigidity of AZC (98%+ self-transition rates, zero backward R-series motion, 40-150 token lock-ins) definitively excludes several hypotheses:

- **Not a calendar** — semantic systems like calendars don't tolerate 98%+ self-transition within a single zone
- **Not astrology** — the strict forward-only progression forbids retrograde motion
- **Not month-by-month recipes** — the lock-in periods are far too rigid
- **Not semantic labels on figures** — the vocabulary shows zero flexibility within zones

Control scaffolds tolerate these patterns. Semantic or communicative systems do not.

---

## HT: The Orientation Layer

**What it is:** 7,042 tokens distributed across the entire manuscript. HT tokens were originally defined by exclusion — they don't belong to the 479-type classified grammar. But recent analysis (C935) shows they are **enriched compound MIDDLEs** — longer, more complex tokens that decompose into the same core atoms found in simpler form throughout the paragraph body.

**What it does:** HT tokens are **compound operational specifications** that serve a dual purpose:

1. **Operational specification** — Each compound token encodes multiple operations compressed into a single word. For example, `opcheodai` decomposes into atoms (op, ch, e, od, ai) that each correspond to a core operation. 71.6% of these atoms appear as simple MIDDLEs in the paragraph body (vs 59.2% random baseline). The header compresses what the body unpacks.

2. **Program identification** — Because the specific combination of atoms in each compound is rare or unique, these tokens also function like technical part numbers — they identify *which specific program* this is. Two different compound headers can invoke similar generic control loops in the body while remaining distinguishable.

HT tokens are 1.46x more likely to be compound than classified grammar tokens (45.8% vs 31.5%), and their MIDDLEs average 2.64 characters vs 2.04 for the grammar. They are genuinely operational — just redundant with the body content.

### Operationally Redundant, Not Empty

Three independent tests prove that removing all HT tokens would not change any program's outcome (p = 0.92 for terminal independence). This isn't because HT is empty — it's because the paragraph body already contains the same operations in simpler form. The header is a compressed specification; the body unpacks it.

Line-1 HT tokens concentrate heavily: 50.2% of first-line tokens come from the HT vocabulary vs 29.8% in body lines. This concentration may still serve a human-facing function — giving the operator a quick reference for what the paragraph does — but the primary finding is that HT tokens are functional compound specifications, not a separate non-operational layer.

### Other Properties

- **Unified across systems:** The same HT prefixes appear in A, B, and AZC (Jaccard similarity >= 0.947)
- **Quire-organized:** Clustering follows physical production units (quires), not content organization
- **Phase-synchronized:** Different HT prefixes correlate with early vs. late procedural phases
- **Hazard-avoiding:** HT tokens cluster in positions where the operator would be waiting, not at forbidden transition points

---

## How the Layers Interact

The four layers are independent systems that share vocabulary but serve different functions:

| Layer | What It Does | How It Relates to the Others |
|-------|-------------|------------------------------|
| **Currier B** | Executes fixed programs | Shares vocabulary with A and AZC but operates independently |
| **Currier A** | Catalogs fine distinctions | Shares vocabulary pool with B; no entry-level coupling |
| **AZC** | Classifies vocabulary by position in diagrams | Reflects the same operational character that B deploys sequentially |
| **HT** | Compound specifications + operator orientation | Redundant with B body content; concentrated on first lines |

**These systems do not form a runtime pipeline.** B programs are fixed — they don't get compiled or filtered from A data during execution. The vocabulary overlap reflects a construction-time relationship: A was the reference vocabulary used when writing B programs. AZC classified that vocabulary by operational character. Once the programs were written, each layer became a self-contained view of the same underlying vocabulary. (Tier 3 interpretation.)

**A and B share types but not structure.** Both use the same morphological system (PREFIX + MIDDLE + SUFFIX) and the same kernel-heavy/kernel-light dichotomy. But A has no sequential grammar, no forbidden transitions, and no line structure. They're aligned through shared vocabulary, not through functional coupling.

**AZC and B share vocabulary but not organization.** AZC classifies tokens by operational character in positional diagrams. B deploys the same tokens in sequential control programs. The 69.7% vocabulary overlap reflects shared domain, not causal connection — AZC position has zero independent effect on B behavior after controlling for MIDDLE.

**The only structural element that transfers perfectly across all systems** is the morphological type dichotomy: kernel-heavy prefixes (ch, sh, ok) make ~100% kernel character contact and avoid LINK positions; kernel-light prefixes (da, sa) make less than 5% kernel contact and cluster near LINK positions. This division reflects control-flow participation and is universal across all four systems.

---

## The Brunschwig Connection

The strongest external corroboration for the "control system" interpretation comes from systematic comparison with Hieronymus Brunschwig's *Liber de arte distillandi* (1500) — the first printed manual on distillation.

This comparison is a **Tier 3 interpretation** (speculative but structurally grounded). The structural findings about grammar, hazards, and control flow are Tier 0-2 (proven). The identification of the specific domain as distillation is an inference from structural parallels, not a proof.

### What Aligns

Across four independent test suites (28 tests total):

- **Recovery architecture**: The manuscript's bounded recovery (mean escape chain: 1.19 tokens, 84.3% single-token) matches Brunschwig's explicit rule that a batch may be reinfused "no more than twice"
- **Fire degrees**: Brunschwig's 4 fire degrees (low flame to open flame) correlate with Voynich process stability metrics (rho = -0.457, p < 0.0001)
- **Material-apparatus separation**: Both systems encode procedures independently of the specific materials being processed
- **Sensory modalities**: Both use categorical sensory tests (look, smell, touch) without instruments
- **Illustration anchoring**: Root-emphasized plant illustrations correlate with POUND/CHOP operations (r = 0.366, p = 0.0007)

### What Doesn't Align

The comparison is not perfect. Some Brunschwig-derived predictions about line-level organization were not supported, and the manuscript's grammar is significantly more abstract than Brunschwig's prose recipes. The manuscript is a control system reference; Brunschwig is an instructional manual. They share domain and structure but differ in format and audience.

---

## What This Analysis Cannot Determine

Certain questions are structurally unanswerable from the manuscript's grammar:

- **What substance is being processed** — The grammar encodes operations, not materials
- **Who wrote it** — Nothing in the structure identifies an author or school
- **What individual tokens "mean"** — Operational roles are not word meanings; "this prefix selects heat operations" is not the same as "this prefix means heat"
- **What the illustrations depict** — Illustrations do not constrain text content (statistically proven)

These are not gaps in the analysis. They are properties of the system: a control grammar that works precisely because it is domain-general.

---

## Falsified Hypotheses

These interpretations have been structurally ruled out:

| Hypothesis | Why It Fails |
|-----------|-------------|
| Natural language | 0.19% reference rate to any known language; 49-class grammar with zero translation-eligible zones |
| Cipher or substitution | 0.19% reference rate (ciphers require consistent mapping) |
| Glossolalia / random text | 100% grammar coverage with strict forbidden transitions |
| Illustrations constrain text | Zero statistical coupling between illustration features and token selection |
| Calendar encoding (Zodiac) | 0/4 predictions met; 98%+ self-transition incompatible with semantic systems |
| Simple cycle topology (AZC) | Strict forward-only ordering in R-series |

---

## How to Explore Further

| If you want to... | Start here |
|-------------------|-----------|
| Read the full constraint system | `context/CLAUDE_INDEX.md` |
| Understand a specific constraint | `context/CLAIMS/INDEX.md` → search by number |
| See the Currier B grammar contract | `context/STRUCTURAL_CONTRACTS/currierB.bcsc.yaml` |
| See the Currier A registry contract | `context/STRUCTURAL_CONTRACTS/currierA.casc.yaml` |
| See AZC activation mechanics | `context/STRUCTURAL_CONTRACTS/azc_activation.act.yaml` |
| See the Brunschwig comparison | `context/SPECULATIVE/brunschwig_comparison.md` |
| Run the core analysis library | `scripts/voynich.py` (see `CLAUDE.md` for examples) |
| View a decoded folio | `python scripts/show_b_folio.py f76r -p` (paragraph view) |
| View control flow | `python scripts/show_b_folio.py f76r --flow` (macro states + FL stages) |
| View full metadata | `python scripts/show_b_folio.py f76r --detail 4` (all classification layers) |
