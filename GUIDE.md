# Understanding the Voynich Manuscript: A Guide

This document explains the project's findings for readers who want to understand what the Voynich Manuscript encodes. Everything here is grounded in statistical evidence from the transcript data.

For the definitive technical reference, see **[ARCHITECTURE.md](phases/INSTRUCTION_WORD_FORMALISM/ARCHITECTURE.md)**. For claims and limits, see **[WHAT_WE_CLAIM.md](WHAT_WE_CLAIM.md)**.

### Key Terms

| Term | Meaning |
|------|---------|
| **Currier A / B** | Two scribal hands (or text types) identified by Prescott Currier in the 1970s. Used here as system labels — A and B occupy completely separate folios |
| **AZC** | The Astronomical, Zodiac, and Cosmological folios — a structurally distinct subsystem |
| **HT** | Human Track — compound tokens concentrated on first lines that serve as program identifiers |
| **PP** | Participation Pipeline — the subset of Currier A MIDDLEs that also appear in Currier B (404 of 972) |
| **RI** | Registry-Internal — the subset of Currier A MIDDLEs that stay within A and never enter B (609 of 972) |
| **MIDDLE** | The core discriminative component of each token (between PREFIX and SUFFIX) |
| **PREFIX** | The operational channel selector prepended to a MIDDLE |
| **REGIME** | One of four folio-level behavioral profiles in Currier B |

---

## The Short Version

The Voynich Manuscript is not a language. It is not a cipher. It is a **control grammar**, a collection of structured programs encoding operational procedures in a purpose-built notation. The structural analysis (49 instruction classes, 18-atom compositional grammar, 6-state macro-automaton, 17 disfavored transitions) is established at high confidence across 1,970 validated constraints. The leading interpretive hypothesis identifies the source tradition as Pseudo-Lullian alchemy (*Testamentum* Practica and Liber Mercuriorum), with 51 procedural chapters matched to 41 folios covering 96% of the *Testamentum*'s procedural content, validated by a 10-dimension permutation test (0/10,000 shuffles, p < 0.0001).

The manuscript reorganizes this content for workshop use: preparation procedures cluster in Herbal B, transmutation procedures cluster in Section S, and theoretical content is entirely absent. An 18-atom compositional architecture produces readable operational descriptions for every token (100% coverage), and cross-folio vocabulary analysis has identified specific tokens encoding material introduction (`dar`, 6/6 partition) and quality checking (`chekar`, 7/7 folios).

The manuscript is organized into four structurally distinct layers, each serving a different function. Together they form a self-contained system: the structure itself encodes operational sequences, intervention points, and avoidance constraints without requiring external explanation.

---

## The Sheet Music Analogy

Imagine discovering documents in an unknown notation. Translation fails. No dictionary helps.

But structural analysis reveals patterns: the notation uses a small set of symbols in strict positional rules. Certain combinations are strongly disfavored. The symbols cluster into families that correlate with mathematical ratios — ratios that match the harmonic series. The forbidden combinations correspond to dissonant intervals.

No one "translated" anything — but they proved, from internal structure alone, that the notation encodes music. The structure *is* the semantics.

**This is exactly what we are doing with the Voynich Manuscript.** We proved that its internal structure — 49 instruction classes, 17 disfavored transitions, kernel-centric convergence, bounded recovery, and dimensionality matching modern distillation manuals — fits the domain of thermodynamic process control and no other domain tested. The disfavored transitions correspond to physical failure modes. The convergence behavior matches distillation physics. The recovery architecture matches Brunschwig's historical practice.

---

## How the Layers Work Together

The four layers are independent systems that share vocabulary but serve different functions:

| Layer | What It Does | How It Relates to Others |
|-------|-------------|--------------------------|
| **Currier B** | Executes fixed programs | Shares vocabulary with A and AZC but operates independently |
| **Currier A** | Catalogs *what* operations exist | Determines vocabulary available to B; predicts B manifold position (r=0.42) |
| **AZC** | Classifies vocabulary by position | Reflects the same operational character that B deploys sequentially |
| **HT** | Compound specifications + orientation | Redundant with B body content; concentrated on first lines |

**These systems do not form a runtime pipeline.** B programs are fixed — they don't get compiled or filtered from A data during execution. The vocabulary overlap reflects a construction-time relationship: A served as the reference vocabulary when B programs were originally composed. AZC classified that vocabulary by operational character. Once written, each layer became a self-contained view of the same underlying vocabulary. (Tier 3 interpretation.)

**The bridge backbone connects vocabulary geometry to execution dynamics.** Of the 972 MIDDLEs in Currier A's discrimination space, 85 are "bridge" MIDDLEs that also appear in Currier B. These bridges carry nearly all the information connecting vocabulary structure to dynamical behavior. A folio's PP MIDDLE content predicts its B-side manifold position (Mantel r=0.42, p<0.0001), and this signal is bridge-dominant (bridge r=0.43 vs dark r=0.20). The 8 operational categories are the organizing principle that spans all four systems: A organizes its registry by operational theme, AZC sorts vocabulary by category into positional zones, and B's execution dynamics are predicted by the category composition of its vocabulary.

---

## The Four Layers at a Glance

| Layer | System | What It Does |
|-------|--------|-------------|
| **Execution** | Currier B | The programs themselves — adaptive control procedures |
| **Distinction** | Currier A | Vocabulary catalog — determines *what* operations each program can use |
| **Context** | AZC | A positional lookup table classifying vocabulary by operational character |
| **Orientation** | HT (Human Track) | Keeps the human operator oriented during production |

These layers never explain each other. B doesn't reference A. A doesn't mention AZC. They interact through vocabulary constraints — what tokens are available in what positions — not through explicit cross-references.

---

## Currier B: The Execution Layer

**What it is:** 23,243 tokens across 83 folios (61.9% of the manuscript). Every folio is a complete, self-contained program. Every program uses the same grammar.

**What it does:** Each program encodes a closed-loop control process — applying energy, monitoring state, checking for hazards, and recovering when things drift.

> **Tier note:** Structural findings below (grammar, classes, transitions, architecture) are Tier 0-2 — proven from the data. Category names like THERMAL and STAGING are Tier 2 structural labels for validated clusters. English glosses like "heat" and "cool" are Tier 3 interpretive labels consistent with the structural evidence but not proven translations.

### Token Composition

Every Currier B token decomposes into compositional parts:

```
[ARTICULATOR] + [PREFIX] + MIDDLE + [SUFFIX]
```

- **PREFIX** selects the operational channel and encodes line position. The base character (h, e, k, o, a) determines which family of core actions is legal — within-base MIDDLE similarity is 0.950, between-base drops to 0.515. PREFIXes read as two-atom instructions: [VERB]+[TARGET] — for example, ok = "operate heat," ch = "adjust watch." Sister pairs (ch/sh, ok/ot) diverge through vocabulary selection, not by changing what any MIDDLE means.
- **MIDDLE** is the primary discriminative content. MIDDLEs are themselves compositional, decomposing as **HEAD + MOD\* + TERM**: HEAD sets the operational domain (k=thermal, e=cooling, o=staging, a=yielding, t=transfer), the MOD stack parametrizes the action, and TERM sets the exit condition. The frame (HEAD+TERM) predicts 64% of operational category; modifiers shift the remaining 36%. Terminals follow a three-tier opacity gradient controlling suffix attachment: opaque terminals (m, n, y) suppress suffix; transparent h passes through at 98.7%.
- **SUFFIX** is a parallel compositional domain using a 16-atom subset of MIDDLE's inventory. Two alternating suffix modes cycle within every qualifying paragraph: Mode A uses THERMAL/MONITORING atoms (specification), Mode B uses STAGING/FLOW atoms (continuation). The modes interleave at 80%.
- **ARTICULATOR** is an optional line-position marker (4.41% of tokens) that marks *where* in the line a token sits, not *what* it does — zero information about operational category beyond what MIDDLE already provides.

### The 49 Instruction Classes

All 479 distinct token types collapse into 49 instruction classes with zero loss of grammatical predictive power — a 9.8x compression ratio. The manuscript's apparent vocabulary diversity is compositional variation within a small, strict grammar.

| Role | Classes | Share of B | Function |
|------|---------|-----------|----------|
| ENERGY_OPERATOR | 18 | 31.2% | Energy modulation |
| AUXILIARY | 19 | 16.6% | Scaffold and infrastructure |
| FREQUENT_OPERATOR | 4 | 12.5% | Common control instructions |
| CORE_CONTROL | 4 | 4.4% | Execution boundaries |
| FLOW_OPERATOR | 4 | 4.7% | Flow control and escape routes |

### Six-State Macro Grammar

The 49 classes further compress into 6 macro states. AXM is a massive attractor: 70% of the time, AXM is followed by another AXM token. FL_SAFE is fleeting — barely one token before snapping back. The majority of the manuscript is scaffold, with only a small fraction devoted to hazard exposure or active control changes.

Individual folios tune their own version of these dynamics, clustering into 6 dynamical archetypes — from "strong attractor" programs (AXM at 82% self-transition) to "active interchange" programs (AXM drops to 47%). These archetypes are almost completely unrelated to the 4 REGIMEs that classify programs by aggregate behavior — each folio individually configures its position within the shared topology.

### Eight Operational Categories

An orthogonal 8-category classification captures what operational domain each token participates in:

| Category | Share | | Category | Share |
|----------|-------|-|----------|-------|
| THERMAL | 23.6% | | STAGING | 12.5% |
| FLOW | 19.2% | | TRANSITION | 14.7% |
| OPERATION | 15.0% | | CONTAINMENT | 5.3% |
| MARKING | 8.1% | | MONITORING | 1.7% |

These categories span all four manuscript systems: A organizes its registry by operational theme, AZC sorts vocabulary by category into positional zones, and B's execution dynamics are shaped by the category mix. THERMAL vocabulary enables escape (rho=+0.780), TRANSITION suppresses it (rho=-0.598).

### The Kernel

At the grammar's center sit three irreducible operators: **k** (energy input, appears early), **h** (phase transitions, mid-line), and **e** (stable state and recovery, appears late — 36% of all B tokens). The transition e-to-h is completely blocked; h-to-k is strongly suppressed. The system acts as a one-way valve where energy flows toward stability but not back.

### Hazard Topology

The grammar disfavors 17 transitions (~65% compliance, C789) organized into 5 structural clusters (C109). The clustering is Tier 0 (proven from the data). The physical failure mode labels below are Tier 3 interpretations based on the distillation domain identification:

| Class | Interpretive Label (Tier 3) |
|-------|----------------|
| PHASE_ORDERING (41%) | Material in the wrong phase location |
| COMPOSITION_JUMP (24%) | Impure fractions passing through |
| CONTAINMENT_TIMING (24%) | Overflow or pressure events (zero corpus impact — theoretical only) |
| RATE_MISMATCH (6%) | Flow imbalance destabilizing the system |
| ENERGY_OVERSHOOT (6%) | Thermal damage to material |

All 17 disfavored transitions are mediated through 23 "hub" MIDDLEs. At the atom level, the k-HEAD atom has complete hazard immunity (0.0% across 3,100 tokens). The system is safe during specification (Mode A: zero violations) and only vulnerable during execution (Mode B: 100% of violations).

### Program Structure

Each folio is a program. Each line is a formal control block following a three-zone gradient (SPECIFICATION → THERMAL WORK → CLOSURE). Lines are statistically independent (MI < 0.032 bits) — each is a self-contained control block, not a step in a sequence. Lines group into paragraphs with header-body architecture: headers specify what the paragraph does, body lines execute.

When the system drifts toward a hazard, the grammar provides escape routes. Hazard exposure is globally constrained, but recovery strategy is locally variable — each program recovers in its own way. Recovery converges on the **e** operator in 54.7% of cases, through the e→y safe pathway (3,475 tokens at 0% hazard).

### Generative Sufficiency

A Markov model using the discovered grammar (M2.1: quintile-conditioned 49×49 transition matrices + symmetric disfavored-transition suppression) passes **21/21 structural metrics** — reproducing every measurable property of the real text. A null model with no sequential structure passes at most 14/21. The 7 tests M0 cannot pass require sequential structure, topological constraints, or positional awareness that frequency sampling cannot produce. For the full progression, see **[Markov Model Evolution](context/MARKOV_MODEL_EVOLUTION.md)**.

For the complete formal specification of all structures described above, see **[ARCHITECTURE.md](phases/INSTRUCTION_WORD_FORMALISM/ARCHITECTURE.md)**.

---

## Currier A: The Distinction Layer

**What it is:** 11,415 tokens across 114 folios (30.5% of the manuscript). Completely separate from Currier B — zero shared folios.

**What it does:** A vocabulary catalog that determines *what* operational vocabulary is available. Where B encodes *how* to execute control procedures, A encodes *what* those procedures operate on — distinguishing dozens of cases where a single B instruction might mean subtly different things. A operates at finer resolution than any execution grammar could support.

The registry is organized around a discrimination gradient — 95.7% of all MIDDLE pairs are illegal co-occurrences, enforcing strict boundaries between discrimination domains. Records are category-themed: a THERMAL-heavy record doesn't randomly include MONITORING vocabulary (Cohen d=9.7).

### Bridge and Dark Pipeline

Of the 972 distinct MIDDLEs in Currier A's vocabulary, 404 participate in Currier B (the "PP" or Participation Pipeline). These split into two completely disjoint channels:

- **Bridge MIDDLEs** (85): The dynamical backbone. These enter B programs directly and carry nearly all the information connecting A vocabulary to B execution dynamics. Bridge density per folio predicts B-side attractor strength (rho=-0.308).
- **Dark pipeline MIDDLEs** (300): The identification vocabulary. These produce exclusively HT (Human Track) tokens in B — compound specifications built from bridge atoms (86% of atom types) but sharing zero complete MIDDLEs with bridges. They are strongly section-specific (Herfindahl 0.716).

The remaining 609 MIDDLEs (60.1%) never appear in B at all — they encode within-A fine distinctions.

### A Parameterizes B

Each line is an independent record with no inter-line dependencies. A uses the same morphological system as B (same HEAD+MOD+TERM slot grammar) but with different terminal emphasis — A enriches state-describing terminals (l 1.84x), B enriches action-performing terminals (dy 144x).

Despite operating independently, A folio vocabulary content genuinely predicts B-side behavior. PP MIDDLE content predicts B-side operational similarity (partial rho=0.502, after controlling for pool size and section), and PP MIDDLE distance predicts B-side manifold position through a bridge-dominant pipeline (Mantel r=0.42). Three of ten B-side manifold axes respond to PP composition (headless infrastructure, sustained heat, direct fire). The other seven axes — encoding *how* B deploys its instructions — do not respond to A content at all.

The relationship is most likely construction-time, not runtime: A served as the reference vocabulary when writing B programs (Tier 3 interpretation). In the distillation interpretation, A catalogs *what apparatus configurations exist*; B encodes *how to run each one*.

For the full specification, see **[ARCHITECTURE.md](phases/INSTRUCTION_WORD_FORMALISM/ARCHITECTURE.md)**.

---

## AZC: The Context Layer

**What it is:** 3,299 tokens across 30 folios (8.7% of the manuscript). The Zodiac, Astronomical, and Cosmological pages.

**What it does:** A static lookup table (C313) — a positional encoding where each PREFIX+MIDDLE combination maps to exactly one position. AZC positions reflect the operational character of vocabulary placed there; they don't cause it.

AZC splits into two architecturally distinct families: the **Zodiac family** (13 folios, uniform template repeated 12 times, 0.945 cross-folio similarity) and the **A/C family** (17 folios, each with unique structure, 0.340 similarity). Both are equally rigid (98%+ self-transition rates).

Positional zones partition vocabulary by operational category, and this sorting propagates downstream: the category composition of AZC-shared vocabulary per B folio predicts B's escape dynamics. The extreme structural rigidity definitively excludes calendars, astrology, seasonal recipes, and semantic labels — control scaffolds tolerate these patterns; semantic systems do not.

For the full specification, see **[ARCHITECTURE.md](phases/INSTRUCTION_WORD_FORMALISM/ARCHITECTURE.md)**.

---

## HT: The Orientation Layer

**What it is:** 7,042 tokens distributed across the entire manuscript. HT tokens are enriched compound MIDDLEs — longer, more complex tokens that decompose into the same core atoms found in simpler form throughout the paragraph body.

**What it does:** HT tokens serve a dual purpose:

1. **Operational specification** — Each compound token encodes multiple operations compressed into a single word. 71.6% of their atoms appear as simple MIDDLEs in the paragraph body. The header compresses what the body unpacks.

2. **Program identification** — Because the specific combination of atoms is rare or unique, these tokens function like technical part numbers — identifying which specific program this is.

Three independent tests prove that removing all HT tokens would not change any program's outcome. This isn't because HT is empty — it's because the body already contains the same operations in simpler form.

**Other properties:** Unified across all systems (Jaccard >= 0.947). Quire-organized (follows physical production units). Phase-synchronized (different prefixes correlate with early vs. late phases). Hazard-avoiding (clusters where the operator would be waiting).

---

## How a Practitioner Would Use This

The manuscript is structured for a trained operator who already knows the materials and equipment. Each folio is a self-contained procedure: the operator finds the right page, reads the program top to bottom, and executes the control operations in sequence. The notation tells them *what to do* — apply energy, monitor state, avoid certain transitions — but never *what substance* they are processing.

The four layers serve distinct roles during use. Currier B contains the procedures themselves. Currier A functions as a reference vocabulary — the operator might consult it when encountering an unfamiliar token, the way a musician consults a chord dictionary. AZC provides a static lookup classifying which operations are legal in which contexts. HT tokens in paragraph headers give the operator quick identification of what each section does.

The operator would need natural-language literacy (to learn the notation) but not domain expertise encoded in the manuscript — the manuscript assumes domain knowledge and encodes only the operational control logic.

For the full usage model, see **[OPERATOR_MODEL.md](phases/OPERATOR_USAGE_MODEL/OPERATOR_MODEL.md)** (Tier 3 interpretation).

---

## What Kind of Document Is This?

Systematic comparison with 8 medieval document genres — recipe collections, herbals, laboratory notebooks, surgical manuals, alchemical treatises, materia medica, trade guild manuals, and mechanical treatises — found no adequate match. The best-fitting genre (laboratory notebooks) achieved only 2.5/7 on structural dimensions.

Three properties of the Voynich Manuscript have zero precedent in medieval documentation: a formal three-level safety architecture, multi-register organization (four independent layers addressing different aspects of the same domain), and a formal operational grammar with statistically disfavored transitions.

We propose a new analytical classification — **OPERATIONAL CONTROL CODEX** — defined as a closed-grammar technical control notation for encoding operational procedures with embedded safety constraints. This is a proposed analytical category derived from structural properties, not a recovered medieval native genre term. If this genre existed historically, the structural evidence suggests it would have appeared in Central European guild contexts during the pre-publication secrecy window (1350-1500).

For the full genre analysis, see **[GENRE_ANALYSIS.md](phases/HISTORICAL_GENRE_PLACEMENT/GENRE_ANALYSIS.md)** (Tier 3 interpretation).

---

## The Brunschwig Connection

The strongest external domain alignment comes from comparison with Hieronymus Brunschwig's *Liber de arte distillandi* (1500) — the first printed distillation manual. This is a **Tier 3 interpretation**: the structural grammar is proven (Tier 0-2); the identification of distillation as the specific domain is an inference from structural parallels.

Across 28 tests in 4 suites:

- **Recovery architecture** matches Brunschwig's "no more than twice" reinfusion rule
- **Fire degrees** correlate with Voynich stability metrics (rho=-0.457)
- **Material-apparatus separation** — both encode procedures independently of materials
- **Sensory modalities** — both use categorical sensory tests without instruments

The manuscript's radiocarbon date (1404-1438) places it in the pre-publication secrecy window — Brunschwig published in 1500 what practitioners had been keeping proprietary for generations. Full historical context: **[HISTORICAL_NETWORK.md](phases/HISTORICAL_NETWORK/HISTORICAL_NETWORK.md)**.

---

## The Pseudo-Lullian Source Tradition

The strongest external content alignment comes from the Pseudo-Lullian *Testamentum* — a 14th-15th century alchemical treatise in the tradition of Ramon Llull (though not written by Llull himself). This is **Tier 2-3**: the matching framework is statistically validated (Tier 2), individual chapter-folio assignments are interpretive (Tier 3).

### Recipe-Folio Matching (Phases 628-635)

An 8-dimensional residual feature system matches individual *Testamentum* chapters to individual Voynich folios:

- **Training:** 16 distillation chapters → 32 REGIME_1 folios. 9/16 confident matches.
- **Validation:** 10-dimension permutation test (0/10,000 shuffles, p<0.0001, C1956). Cross-family replication (features generalize to sublimation, fermentation, fixation, dissolution without retuning). Wrong-regime negative control (collapses to 1/16).
- **Expansion:** Full-spectrum scan of all 209 *Testamentum* chapters across all operation families. 51 procedural chapters matched to 41 folios (96% of procedural content).

### The Matched Folios

Three folios are **confirmed** with multiple independent structural validations:

| Folio | Chapter | Recipe | Key evidence |
|-------|---------|--------|-------------|
| f75r | Ch19 Merc | Aqua vitae composite (9x reflux with honey+wax) | Only 4+ consecutive identical token run in corpus; unique double-dar; Brunschwig cross-confirmation |
| f76r | Ch18 Pract | Element separation (silver-plate purity test) | Strongest monitoring gradient in corpus (rho=0.710, rank 1/13); ch→sh transition maps active→passive testing |
| f84r | Ch14 Pract | Gold dissolution (balneum mariae + putrefaction) | Dual-layer 12-header architecture; lowest distance in dataset; product chain input from f75r |

5 more are **confirmed via reverse-blind prediction** (recipe to predictions to scan to match): f103v (Ch27P, 6/7), f77r (Ch2+3+6M, 7/7 perfect), f39r (Ch7-10M, 6/7). Additional matches found via material-marker hard-filtering (fch=mercury, cs=gold) and recto/verso systematic scanning. In total, 51 procedural chapters map to 41 folios. Short related procedures are consolidated onto single folios (C1937); six recto/verso pairs encode sequential chapters on the same leaf (C1936). Individual folio documentation: `context/FOLIOS/`.

### Section-Level Correspondence

The manuscript's sections map to *Testamentum* book divisions:

- **Section B (f75-f84):** 8/11 folios match Liber Mercuriorum preparation chapters (Ch1-28)
- **Section S (f103-f116):** 6 folios match Mercuriorum transmutation/multiplication chapters (Ch40+)
- **Section T (f66r):** One fixation recipe encoded in ring-diagram format

The split is functional: preparation in Herbal B, transmutation in Section S. Global ordering does not follow book order (r=-0.179), suggesting the author reorganized by operational logic rather than copying sequentially. However, **local adjacency exists**: f75r, f76r, and f77v are three consecutive manuscript folios matching three chapters from the same Liber Mercuriorum section, with f75r and f76r adjacent in both texts (Ch19 and Ch18 — one chapter apart in the *Testamentum*, one folio apart in the manuscript). This implies the author placed related procedures together, preserving source proximity for closely related operations while reorganizing the broader sequence.

### Product Chain (Tier 3 — interpretive reconstruction)

The structural profiles of matched folios are consistent with a production chain, reconstructed via *Testamentum* chapter content. Each link depends on the correctness of the underlying recipe-folio assignment (itself Tier 3):

```
Lunaria → Quicksilver (f112v, Ch1M)
    → Fix and test (f116r, Ch4M)
    → Sublimate to elixir (f79r, Ch12M)
    → Composite ferments (f78v, Ch14M → f76v, Ch15M → f103r, Ch16M)
    → Potable gold (f81v, Ch18M)
    → Quintessence (f75r, Ch19M) ←──── feeds into ────→ Gold tincture (f84r, Ch14P)
    → Animal waters (f80r, Ch21-25M)
    → Furnace/vessel specs (f77v, Ch27M; f82v, Ch28M)
```

The f75r→f84r link is explicit: the *Testamentum*'s cipher key identifies "vegetable G" (Ch14's input) as the quintessence produced by Ch19. Two independently-matched folios connect through the source text's own cipher system.

### Manuscript Organization: Multi-Chapter Folios and Recto/Verso Pairing

The manuscript does not follow a "one chapter = one folio" rule. Related short procedures are combined onto a single folio, while complex single procedures occupy their own folio. f80r (441 tokens) encodes five short animal-extraction chapters (Ch21-25M), each only 1-2 sentences. f75r (412 tokens) encodes one complex 9-cycle recipe (Ch19M).

Recto/verso pairs on the same physical leaf encode **sequential or related procedures**:

| Leaf | Recto | Verso |
|------|-------|-------|
| f66 | Ch24P fixation (ring diagram) | Ch26P inceration / fusibility test |
| f103 | Ch16M ferment multiplication | Ch27P Mercury imbibition |
| f108 | Ch16P element separation | Ch10P silver balneum dissolution |

On f66, fixation (Ch24) and inceration (Ch26) are consecutive Practica operations — you fix the substance first, then incerate it for fusibility. The recto/verso pairing preserves the procedural sequence across the page turn. This suggests the manuscript was deliberately organized by operational logic, not by source text order.

### Cross-Folio Vocabulary

Specific tokens produce consistent operational readings across independently-matched folios:

- **`dar`** (da+r): material introduction. Present on all 4 folios matched to recipes introducing new materials; absent on both folios matched to cohobation/separation-only recipes. 6/6 partition. (C1925, Tier 2)
- **`chekar`** (ch+ek+ar): post-thermal quality check. Appears on 7/83 folios in structurally identical context: qo depleted 0.48x (check happens after heat), daiin enriched 3.7x (distillation context). 3/3 confirmed balneum folios. (C1926, Tier 2)
- **`dal`** (da+l): passive material transfer (output/settling). Complementary to dar.

### What This Does Not Establish

- The manuscript is not a **cipher** for the *Testamentum* text — it encodes the same operational CONTENT in a different notation system
- ~53 of 83 folios remain unmatched — they may correspond to other Pseudo-Lullian texts or workshop-specific procedures
- The **genealogical relationship** (direct derivation vs. shared tradition) cannot be determined from internal analysis
- **Material identity** is still not recoverable from tokens alone (C171) — dar marks "add material" but not which material

---

## The Galenic Framework

The project also tested against John of Rupescissa's *De consideratione quintae essentiae* (1351) — a text using the full Galenic classification: 4 qualities × 4 degrees of intensity. This comparison is **Tier 4** (exploratory).

The Galenic framework predicts the organizational *shape* of the Voynich system (3/4 structural tests pass) but fails at the recipe *level* (0/3 physics tests pass, 1/4 grammar-level tests pass). The architecture transferred; the specific content was rebuilt. In every case, the Voynich preserves Galenic organizational logic but enhances it:

| Galenic Element | Voynich Enhancement |
|----------------|---------------------|
| 4 named qualities | 9 affordance bins defined by behavioral signatures |
| 4 discrete degrees | 14-63 frequency-ranked MIDDLEs per channel |
| "Avoid degree 4" prohibition | Topological disfavored graph (17 transitions, 5 classes, ~65% compliance) |
| 12 named operations | 49 instruction classes |

The conclusion: the Galenic framework is the author's *training background*, not the system's *design principle*. The author organized their work using Galenic categories but built a control grammar that transcended the Galenic framework at every quantitative level. Bio section (f74-f84) is structurally distinct — k-enriched, LINK-depleted, dynamically stable — consistent with balneum mariae (gentle sustained water-bath heating).

The Rosettes foldout (f85-f86) functions as a general-purpose vocabulary reference hub, with 3.05× bridge enrichment and AZC-like grammar. The "dark pipeline" (315 MIDDLEs shared between A and B but outside B's grammar) preserves A's category distribution unchanged, acting as inline annotations with localized effects.

For detailed comparisons: `context/SPECULATIVE/rupescissa_comparative.md` (Galenic), `context/SPECULATIVE/brunschwig_comparison.md` (Brunschwig). For Rosettes: constraints C1124-C1133.

---

## What This Analysis Cannot Determine

Certain questions remain open:

- **What specific substance is referenced by a token** — The grammar encodes operational functions, not material names. `dar` means "add material" but not WHICH material. The *Testamentum* recipe context supplies material identity externally.
- **Who wrote it** — Nothing in the structure identifies an author or school. The historical network analysis identifies the Vienna-Padua academic corridor as the most likely context (Tier 4).
- **What individual tokens "translate to" in natural language** — Operational glosses (k=heat, e=cool) describe function within the control grammar. They are not word meanings in the linguistic sense.
- **What the illustrations depict** — Illustrations do not constrain text content (statistically proven, C138). However, some illustration-structure-product matches exist (f31r/rose/rosewater) at Tier 3-4.
- **What the remaining ~53 unmatched folios encode** — They use the same grammar and vocabulary as the matched folios but have not been mapped to specific historical source chapters.

These are not all permanent gaps. The *Testamentum* matching has already resolved some questions previously thought unanswerable — specific recipe identification, product chain reconstruction, and operational vocabulary functions. The remaining questions will likely be resolved through **alchemical historians** evaluating the recipe matches against the broader Pseudo-Lullian corpus, and **archival research** in uncatalogued Central European collections.

### Common Questions

**If this isn't a translation, what did you solve?** We recovered the formal structure: 49 instruction classes, their transition rules, disfavored states, compositional encoding, and the safety architecture that constrains them. This is analogous to proving documents contain sheet music without hearing a note played — the structural constraints themselves reveal what the notation encodes.

**Why do you think it isn't a language or cipher?** Natural languages show Zipf's law, flexible word order, and open-class vocabulary growth. The Voynich shows none of these — instead, 100% grammar coverage by 49 rigid classes, 17 disfavored transitions (~65% compliance), and zero translation-eligible zones (C132). Cipher tests returned 0/18 (C207).

**Why doesn't the inability to identify substances invalidate the model?** Because the system is designed to be substance-independent. A thermostat's control logic works regardless of what room it heats. The manuscript encodes what to do, when to intervene, and what to avoid — without specifying what is being processed. This is a feature, not a limitation.

---

## Falsified Hypotheses

These interpretations have been structurally ruled out:

| Hypothesis | Why It Fails |
|-----------|-------------|
| Natural language | 0.19% reference rate to any known language; 49-class grammar with zero translation-eligible zones |
| Cipher or substitution | 0.19% reference rate (ciphers require consistent mapping) |
| Glossolalia / random text | 100% grammar coverage with statistically disfavored transitions |
| Illustrations constrain text | Zero statistical coupling between illustration features and token selection |
| Calendar encoding (Zodiac) | 0/4 predictions met; 98%+ self-transition incompatible with semantic systems |
| Simple cycle topology (AZC) | Strict forward-only ordering in R-series |

---

## How This Analysis Was Built

This project was built using AI-assisted computational analysis over 664 research phases. The primary development environment was [Claude Code](https://claude.ai/claude-code) (Anthropic), with independent cross-validation from GPT-5 (OpenAI) at key decision points.

The central methodological innovation is a **progressive context system**: a growing body of numbered, tiered, validated constraints that accumulates across phases. Every finding that survives statistical testing becomes a permanent constraint. Every falsified hypothesis is permanently closed. Each new phase starts with full knowledge of everything that came before. 664 phases, each building on validated prior work, produced 1,970 constraints, a depth no single analytical session could achieve.

For methodology, tools, and repository structure, see **[METHODS_AND_TOOLS.md](METHODS_AND_TOOLS.md)**.

---

## How to Explore Further

| If you want to... | Start here |
|-------------------|-----------|
| Read the full constraint system | `context/CLAUDE_INDEX.md` |
| Understand a specific constraint | `context/CLAIMS/INDEX.md` → search by number |
| See the Currier B grammar contract | `context/STRUCTURAL_CONTRACTS/currierB.bcsc.yaml` |
| See the Currier A registry contract | `context/STRUCTURAL_CONTRACTS/currierA.casc.yaml` |
| See AZC activation mechanics | `context/STRUCTURAL_CONTRACTS/azc_activation.act.yaml` |
| See HT (Human Track) contract | `context/STRUCTURAL_CONTRACTS/humanTrack.htsc.yaml` |
| See paragraph structure contract | `context/STRUCTURAL_CONTRACTS/paragraph.psc.yaml` |
| See the Brunschwig comparison | `context/SPECULATIVE/brunschwig_comparison.md` |
| See the Rupescissa/Galenic comparison | `context/SPECULATIVE/rupescissa_comparative.md` |
| See the recipe-folio matching | `phases/RECIPE_FOLIO_CORRESPONDENCE/` (Phase 628) |
| See individual folio decode notes | `context/FOLIOS/INDEX.md` (48 documented folios) |
| See the PL Testamentum text | `sources/pseudo_lull_testamentum/testamentum_complete_english.txt` |
| See the glossing system | `context/GLOSSING.md` |
| See the historical network | `phases/HISTORICAL_NETWORK/HISTORICAL_NETWORK.md` |
| Run the core analysis library | `scripts/voynich.py` (see `METHODS_AND_TOOLS.md` for examples) |
| View a decoded folio | `python scripts/show_b_folio.py f76r -p` |
| Decoder documentation | [`scripts/DECODER.md`](scripts/DECODER.md) |
