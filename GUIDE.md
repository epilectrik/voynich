# Understanding the Voynich Manuscript: A Guide

This document explains the project's findings for readers who want to understand what the Voynich Manuscript encodes without navigating 1,278 constraint files. Everything here is grounded in statistical evidence from the transcript data.

For the full constraint system and technical details, see `context/CLAUDE_INDEX.md`.

---

## The Short Version

The Voynich Manuscript is not a language. It is not a cipher. It is a **control system grammar** — a collection of structured programs whose architecture is consistent with maintaining a physical process within safe operating limits. Structural comparison with Brunschwig's distillation manual (1500) suggests reflux distillation as one plausible domain (Tier 3 interpretation).

The manuscript is organized into four structurally distinct layers, each serving a different function. Together they form a self-contained system: the structure itself encodes operational sequences, intervention points, and avoidance constraints without requiring external explanation.

---

## The Sheet Music Analogy

Imagine a researcher discovers a cache of documents written in an unknown notation. They can't read it. No dictionary helps. Translation fails completely.

But structural analysis reveals patterns: the notation uses a small set of symbols arranged in strict positional rules. Certain combinations are forbidden. The symbols cluster into families that correlate with mathematical ratios — ratios that turn out to match the harmonic series. The forbidden combinations correspond to dissonant intervals. The document structure matches the form of musical compositions.

The researcher hasn't "translated" anything. They can't tell you what the music *sounds like*. But they can prove, from internal structure alone, that the notation encodes music — because the structural constraints fit the physics of sound and no other domain.

**This is exactly what we are doing with the Voynich Manuscript.**

We are not trying to translate the text. We are proving that its internal structure — 49 instruction classes, 17 forbidden transitions organized into 5 hazard classes, kernel-centric convergence behavior, bounded recovery architecture, and a dimensionality that matches modern distillation manuals (5 principal components, 80% variance) — fits the domain of thermodynamic process control (specifically reflux distillation) and no other domain we've tested.

The forbidden transitions correspond to physical failure modes (phase contamination, thermal overshoot, containment breach). The convergence behavior matches the physics of distillation (energy in, stability out). The recovery architecture matches historical practice (Brunschwig's "no more than twice" reinfusion rule). The structure fits the domain the way sheet music fits harmonics — not because we decoded the meaning of individual tokens, but because the constraints map onto physical law.

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

**What it does:** Each program encodes a closed-loop control process — applying energy, monitoring state, checking for hazards, and recovering when things drift. The programs don't describe a process linearly; they encode adaptive responses to whatever state the system is in.

### How Tokens Work

Every Currier B token is compositional. It decomposes into parts that each carry structural information:

```
[ARTICULATOR] + [PREFIX] + MIDDLE + [SUFFIX]
```

- **PREFIX** selects the operational channel AND encodes line position. Internally, each PREFIX has a base-modifier positional grammar: [MODIFIER (position 0)] + [BASE (position 1)]. The base character (h, e, k, o, a) determines which family of core actions is grammatically legal — within-base MIDDLE cosine similarity is 0.950, while between-base similarity drops to 0.515 (C1218-C1219). Modifiers (q, d, f, p, y) occupy position 0 and refine the operational meaning. PREFIXes also encode where in the line the token appears — they cluster into initial, central, and final positional zones. There are 8 prefix families organized into functional groups. PREFIXes predict operational categories with structured selectivity (V=0.311, C1297) and read as two-atom instructions: [VERB]+[TARGET] — for example, ok = "operate heat," ot = "operate transfer," ch = "adjust watch." Sister pairs (ch/sh, ok/ot) achieve category divergence through vocabulary SELECTION — choosing different MIDDLEs — not by changing what any MIDDLE means. The positional axis (ch later, sh earlier) is orthogonal to the category axis (ch selects different operational themes than sh), giving each sister-prefixed token two independent pieces of information: WHEN to act and WHAT to act on (C1303-C1307).
- **MIDDLE** is the primary discriminative content — the specific action variant within the channel the prefix opened. MIDDLEs are themselves compositional, decomposing as **HEAD + MOD\* + TERM** (C1393-C1394):
  - **HEAD** (a, e, o, k, t) sets the operational domain — k=thermal, e=cooling, o=staging, a=yielding, t=transfer
  - **MOD stack** (p, c, i, f, d, s) parametrizes the action in a fixed internal order: p(pause)→f(flag)→i(iterate)→c(adjust)→d(mark)→s(sequence). The first modifier carries the most weight (66.5% decisive). Each modifier has a consistent category-shifting effect — `d` pulls toward OPERATION (V=0.657), `f` toward MARKING (76.4%), `i` toward TRANSITION (44.7%).
  - **TERM** (y, l, r, h, m, n) sets the exit condition — r=respond (99% FLOW), y=end (56% OPERATION), h=watch (transparent — lets HEAD+MODS determine category at V=0.988)
  - The frame (HEAD+TERM) predicts 64% of operational category; modifiers shift the remaining 36%. Approximately 30 core MIDDLEs handle 67.6% of all tokens, with a long tail of ~1,150 rarer variants. Headless compounds (20.6% of tokens) form a specialized subgrammar for infrastructure operations at boundary positions.
- **SUFFIX** is a parallel compositional domain using a 16-atom subset of MIDDLE's inventory (missing k, t, p, f, c — the action-specific atoms). Like MIDDLE, suffix decomposes as **HEAD + TERM**: the first atom selects operational category (V=0.277), the last atom selects line position/scope (R²=0.059). The same atom character carries different operational information in suffix vs MIDDLE position — the alphabet is shared but the semantics are position-dependent (C1408-C1409). Two alternating suffix modes cycle within every qualifying paragraph (C1229): Mode A uses THERMAL/MONITORING atoms {d, e, h, y} (specification lines), Mode B uses STAGING/FLOW atoms {a, i, l, m, n, o, r, s} (continuation lines). The modes interleave at 80%, creating an oscillating specification→continuation rhythm within the execution envelope (C1410).
- **ARTICULATOR** (q, y, s, d) is an optional line-position marker present on 4.41% of B tokens (C1416-C1421). Articulators are 6.48x enriched at line-initial position, strongly select for e-HEAD (stability) MIDDLEs while avoiding k-HEAD (thermal), and suppress suffix attachment (0.34–0.55x normal rate). Critically, they add zero information about operational category beyond what MIDDLE already provides (conditional MI = 0.000 bits) — they are orthogonal to the PREFIX→MIDDLE→SUFFIX content chain. The articulator marks *where* in the line a token sits, not *what* it does. There are 29 forbidden ARTICULATOR × PREFIX combinations, confirming PREFIX-locked deployment.

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

### How the Macro States Flow

The 6 states don't just classify tokens — they form a dynamic system with well-defined transition behavior. AXM is a massive attractor: 70% of the time, an AXM token is followed by another AXM token, and every other state returns to AXM as its dominant exit. FL_SAFE is the opposite — a fleeting excursion lasting barely one token before snapping back. CC (control change) is a pure initiator that fires once and immediately hands off. The whole system is ergodic, meaning every state can reach every other state, and transitions mix almost instantly.

### Folio-Level Dynamical Profiles

When you zoom into individual folios, each program tunes its own version of these macro dynamics. The 72 folios with enough data cluster into 6 dynamical archetypes — ranging from "strong attractor" programs (where AXM dominates with 82% self-transition and the system rarely leaves its home state) to "active interchange" programs (where AXM self-transition drops to 47% and the system spends much more time cycling through FQ operations and hazard states).

These archetypes are almost completely unrelated to the 4 REGIMEs that classify programs by aggregate behavior. REGIMEs describe *what* a program does overall; archetypes describe *how* its macro-automaton behaves moment to moment. REGIME and section membership together explain only about a third of the variation between folio transition profiles — the remaining two-thirds is program-specific tuning. Each folio individually configures its position within the shared 6-state topology.

### Eight Operational Categories

In addition to the 6-state macro grammar (which classifies tokens by their grammatical role), the system supports an orthogonal 8-category classification that captures what operational domain each token participates in:

| Category | What It Covers | Share |
|----------|---------------|-------|
| **THERMAL** | Heating, cooling, temperature control | 23.6% |
| **MARKING** | Labeling, identification, tagging | 8.1% |
| **FLOW** | Routing, transfer, movement | 19.2% |
| **OPERATION** | Active execution, work operations | 15.0% |
| **STAGING** | Setup, preparation, initialization | 12.5% |
| **TRANSITION** | State changes, phase shifts | 14.7% |
| **CONTAINMENT** | Enclosure, sealing, vessel management | 5.3% |
| **MONITORING** | Observation, checking, measurement | 1.7% |

These categories are assigned from MIDDLE-level behavioral profiles (not from PREFIX or suffix), and they organize all four systems:

- **In Currier A:** Records and paragraphs are category-themed. A THERMAL-heavy record doesn't randomly include MONITORING vocabulary (C1261, Cohen d=9.7). Paragraphs show even stronger specialization (C1263, d=12.5).
- **In AZC:** Positional zones partition vocabulary by category (C1269). AZC sorts bridge vocabulary by category (p=0.0003) but not dark pipeline vocabulary (p=0.198) — categories are the mechanism through which AZC zone structure connects to B execution dynamics (C1272).
- **In Currier B:** Categories predict escape dynamics — THERMAL vocabulary enables escape (rho=+0.780), TRANSITION suppresses it (rho=-0.598). Category adds 18.6% information beyond PREFIX for instruction class prediction (C1278). Categories are also structured in sequence: THERMAL→THERMAL and FLOW→TRANSITION are common, but THERMAL→TRANSITION is rare (C1286).

The category system is the first organizing principle shown to span all four manuscript systems through a single mechanism: A organizes its registry by operational theme, AZC sorts shared vocabulary by category into positional zones, and B executes programs whose dynamics are shaped by the category mix of their vocabulary.

### The Kernel: Three Core Operators

At the center of the grammar sit three irreducible operators, designated **k**, **h**, and **e**:

- **k** adjusts energy input (appears early in lines)
- **h** manages phase transitions (appears in the middle)
- **e** anchors stable state and drives recovery (appears late — tokens containing the e operator account for 36% of all B tokens)

These three operators define the grammar's backbone. They are bound morphemes — they never appear as standalone tokens, only as components within larger compositional words. The transition e-to-h is completely blocked (ratio 0.00), while h-to-k is strongly suppressed — the system acts as a one-way valve where energy flows toward stability but not back. Within token construction, the trigram e-e-e accounts for 97.2% of all kernel character sequences. The system overwhelmingly favors stability.

The ke and ek orderings are functionally distinct: ke = "heat burst then equilibrate" (energy-first, aggressive), ek = "check then heat" (stability-check-first, cautious). The ke/ek ratio is REGIME-conditioned (REGIME_1: 18.6% ek, REGIME_4: 64.0% ek) and section-conditioned (HERBAL 79.1% ek). The e-depth within a MIDDLE also restructures suffix grammar: single-e selects 64% -edy suffixes, while multi-e selects 37% -y suffixes (C1225-C1226). These are MIDDLE-internal parametric axes, independent of REGIME or section.

### Instruction Encoding Architecture

The MIDDLE layer — the core action of every token — is itself a compositional instruction (C1393-C1394). Each MIDDLE decomposes into:

```
HEAD + MOD* + TERM
```

- **HEAD** sets the operational domain: k=thermal (71% THERMAL), e=cooling (most versatile), o=staging, a=yielding (55% FLOW), t=transfer (65% FLOW)
- **MOD stack** parametrizes the action in a fixed order: p(pause)→f(flag)→i(iterate)→c(adjust)→d(mark)→s(sequence). The modifier closest to HEAD carries the most category weight (66.5% decisive). Each modifier has a consistent effect — `d` pulls toward OPERATION, `f` and `p` toward MARKING, `i` toward TRANSITION. Modifiers that avoid each other (c/i, c/s, d/f) encode incompatible parametrization paths.
- **TERM** sets the exit condition. Most terminals are **opaque** — they impose a category regardless of what precedes them (r→99% FLOW, m→87% TRANSITION). The terminal `h` ("watch") is **transparent** — it lets HEAD+MODS determine category (V=0.988), consistent with "keep monitoring whatever the HEAD specifies."

The frame (HEAD+TERM) predicts 64% of operational category. Modifiers shift the remaining 36%. Example readings (**Tier 3** — the structural decomposition is Tier 2, but the English glosses like "heat" and "cool" are interpretive labels, not proven translations):

| Token | PREFIX | MIDDLE | Decomposition | Category | Reading |
|-------|--------|--------|--------------|----------|---------|
| qokeedy | qo | keedy | k(heat) + ee(cool×2) + d(mark) + y(end) | THERMAL | energy channel: sustained cooling, mark completion |
| cholaiin | ch | olaiin | o(arrange) + l(state) + a(yield) + ii(iterate×2) + n(halt) | STAGING | monitor channel: arrange state, yield with repeated iteration, halt |
| okedy | ok | edy | e(cool) + d(mark) + y(end) | OPERATION | operate-heat channel: cool, mark, end |

The system also includes **headless compounds** (20.6% of tokens) — MIDDLEs that start with modifier or terminal atoms instead of a HEAD. These are not abbreviations; they form a specialized subgrammar for infrastructure and support operations (CONTAINMENT 10.4x, MARKING 5.3x enriched), concentrated at line boundaries and paragraph headers, and deployed primarily through a-base PREFIX channels (da, sa, ka, ta).

The e-atom shows a depth-dependent saturation gradient: single-e compounds are diverse across categories, but ee compounds are 84% THERMAL and eee compounds are 100% THERMAL — increasing cooling intensity saturates to pure thermal identity.

Only e and i can repeat in the modifier stack (C1197), and only `dy` is a hard-fused pair that never separates (O/E 5.75x). All other frequent pairs (ed, ol, ke, ch) are either soft-fused or simply adjacent slots following the grammar.

### Cross-Slot Interaction

The three morphological slots (PREFIX, MIDDLE, SUFFIX) are not independent — information flows through MIDDLE as a hub. PREFIX predicts MIDDLE HEAD atoms (V=0.414) and MIDDLE TERMINAL predicts suffix mode (V=0.503), but PREFIX barely predicts suffix directly (NMI=0.090). The chain is PREFIX→MIDDLE→SUFFIX, with MIDDLE mediating essentially all of PREFIX's influence on suffix selection (C1411-C1413). Sister PREFIX pairs (ch/sh, ok/ot) are nearly identical at the atom level (JSD=0.010) — their known category divergence comes from vocabulary selection, not from selecting different atoms. At the atom level, cross-slot co-occurrence shows specific rules: `d` repels itself across slots (0.203x expected), while `e` attracts itself (1.310x), and the terminals `l` and `r` absolutely block `e` from appearing in the suffix (C1414). There are also 83 forbidden PREFIX × MIDDLE HEAD combinations — structural gaps where common elements never co-occur (C1415).

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

Each folio is a program. Each line within a folio is a formal control block (3.3x more regular than random line breaks, mean 9.54 tokens, mode 10; C1425). Lines follow a three-zone gradient:

```
SPECIFICATION → THERMAL WORK → CLOSURE
```

Line-initial tokens are high-information specification markers: ARTICULATOR-enriched (3.93x), STAGING (1.57x) and MARKING elevated, setting up what the line will do (C1426). THERMAL operations peak at quarter Q1 — work follows specification, not the reverse (C1428). Line-final tokens are CLOSURE markers: TRANSITION enriched (1.63x), THERMAL depleted, with the m-terminal appearing 196x above baseline as a routing/halt signal (C1427). Token information follows a U-shape — boundaries carry the highest-entropy tokens (10.29 bits initial, 10.11 bits final vs 9.82 mid-line; C1430). Lines within a paragraph are statistically independent (MI < 0.032 bits between consecutive lines; C1429) — each is a self-contained control block, not a step in a sequence.

Lines group into paragraphs, which function as mini-programs with their own internal structure: a header line followed by body lines that execute operations. Header lines use distinctive vocabulary — 50.2% of first-line tokens come from a specialized identification vocabulary, compared to 29.8% in body lines. The structure suggests that headers specify what the paragraph will do, with body lines carrying out the operations in simpler individual tokens.

Within the body, two architectural layers operate simultaneously:

1. **Execution gradient (the envelope):** Terminal suffix fraction declines monotonically from top to bottom (r = -0.89), while bare suffix fraction increases (r = +0.90). This gradient tracks the shift from specification to execution.

2. **Suffix mode coexistence (the texture):** Within that envelope, every qualifying paragraph contains two universal suffix modes (silhouette 0.459, 80% of paragraphs contain both). At atom level (C1410), Mode A uses THERMAL/MONITORING suffix atoms {d, e, h, y} — an active specification phase concentrating k-family MIDDLEs (1.62x), preparation operations (2.86x), and energy PREFIXes (1.48x). Mode B uses STAGING/FLOW suffix atoms {a, i, l, m, n, o, r, s} — a continuation/equilibration phase elevating e-family MIDDLEs. These modes are universal across all qualifying paragraphs (global silhouette 0.428, F = 4.56; C1229-C1231, C1410). Crucially, mode is ~80% determined by each token's own MIDDLE content, not by sequential alternation — lines persist in a mode (60.6% same-mode) rather than oscillating, and the mechanism is MIDDLE TERMINAL gating, not a paragraph-level clock (C1422-C1424).

The final 2 body lines cluster into 3 distinct product signatures that correlate with section (chi2 = 31.73, p = 0.0001), suggesting paragraphs end with different output types (C1232).

### Recovery Architecture

When the system drifts toward a hazard, the grammar provides escape routes. The key design principle is:

- **Hazard exposure is globally constrained** — the same 17 forbidden transitions apply everywhere
- **Recovery strategy is locally variable** — each program can recover in its own way

This means the manuscript clamps risk uniformly while leaving operators free to adapt their recovery approach to local conditions. Recovery paths converge on the **e** operator (stable state) in 54.7% of cases.

At the macro-state level, the forgiveness mechanism has a concrete realization: forgiving programs have a strong AXM attractor — the system stays in AXM longer, leaves less often, and returns faster when it does leave. Brittle programs have a weaker attractor and spend more time cycling through FQ interchange operations. The "design freedom" in recovery is specifically the freedom to tune how strong the AXM attractor is — how readily the system leaves and returns to its dominant operational state.

### What B Cannot Tell You

The grammar is purely operational. It encodes control-flow structure but not the identity of what is being controlled. You can determine that a program applies energy, monitors state, and avoids contamination — but you cannot determine what substance is being processed. This is not a gap in the analysis — the system encodes process control without specifying what is being processed. The specific material knowledge would have been supplied externally, whether by a trained operator's judgment or by some other reference.

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

### A Records Are Category-Themed

A's registry is not just organized by morphological compatibility (C475) — it is organized by operational category. Individual records (folio, line) draw PP MIDDLEs from fewer operational categories than random assignment would produce (C1261, Cohen d=9.7, p<0.001). This effect is even stronger at the paragraph level (C1263, d=12.5): each A paragraph specializes in a subset of operational themes.

RI extensions (the identification markers within A records) are operationally coupled to the PP base categories in the same record (C1262, V=0.221). A record about THERMAL operations uses THERMAL-related RI markers, not arbitrary ones.

In A, sister pairs ch and sh are category-identical (C1268, V=0.021) — the distinction that emerges strongly in B (V=0.121) is invisible in A's simpler vocabulary structure. A sections show distinct atom-level signatures: Herbal is DYNAMIC/ENERGY-enriched, Pharma is STABILITY/STRUCTURAL-enriched (C1266).

### How A Relates to B

A and B share vocabulary but not structure:

- **No entry-level coupling**: A entries don't map to specific B folios through simple lookup
- **Shared vocabulary pool**: A and B draw from a common vocabulary (69.8% of B tokens use vocabulary shared with A), but neither references the other
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

### AZC Category Sorting

AZC positional zones don't just classify vocabulary by legality — they partition it by operational category (C1269, V=0.084). More importantly, AZC is the mechanism that sorts bridge and dark pipeline vocabulary into different category profiles (C1272, V=0.117). Bridge MIDDLEs are category-sorted by zone (p=0.0003), while dark pipeline MIDDLEs are not (p=0.198). This sorting propagates downstream: the category composition of AZC-shared vocabulary per B folio predicts B's escape dynamics — THERMAL vocabulary enables escape (rho=+0.780), TRANSITION vocabulary suppresses it (rho=-0.598, C1274).

All AZC sections (A, C, Zodiac) converge on the same atom profile: Currier A's Pharma section (r=0.916-0.928, C1276). AZC draws disproportionately from the stability/structural atom pool, consistent with its classification function.

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

**The bridge backbone connects A's vocabulary geometry to B's execution dynamics.** Of the 972 MIDDLEs in Currier A's discrimination space, 85 are "bridge" MIDDLEs that also appear in Currier B. These bridges carry nearly all of the information that connects vocabulary structure (which MIDDLEs a folio uses) to dynamical behavior (how that folio's macro-automaton operates). Non-bridge MIDDLEs contribute almost nothing to predicting a folio's dynamical profile. The bridge backbone is where vocabulary geometry and execution topology overlap — it's the concrete mechanism through which A's discrimination index constrains B's behavioral space. Notably, from B's perspective all 85 unique MIDDLEs are bridges (100% coverage; C1020) — "bridge vs non-bridge" partitions A's vocabulary space, not B's internal grammar.

**The 8 operational categories are the first organizing principle shown to span all four systems.** A organizes its registry by operational theme (C1261-C1263). AZC sorts shared vocabulary by category into positional zones (C1269, C1272). B's execution dynamics are predicted by the category composition of its vocabulary (C1274). The category system provides the missing link between A's discrimination structure and B's execution behavior — it is the dimension along which vocabulary structure, positional classification, and execution dynamics all align.

**The morphological type dichotomy also transfers across all systems:** kernel-heavy prefixes (ch, sh, ok) make ~100% kernel character contact and avoid LINK positions; kernel-light prefixes (da, sa) make less than 5% kernel contact and cluster near LINK positions. This division reflects control-flow participation and is universal across all four systems.

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
- **Illustration anchoring**: Root-emphasized plant illustrations correlate with preparation-class PREFIX operations (r = 0.366, p = 0.0007)

### Process Dimensionality

Direct dimensional comparison sharpens the Brunschwig relationship: Voynich requires 5 principal components to explain 80% of its variance — matching modern distillation manuals, not Brunschwig's recipes (which need only 3 PCs). The Voynich author's process control is more differentiated than Brunschwig's prose descriptions, particularly in its treatment of mid-process operations (MIDPROCESS sub-types map to 5 distinct Voynich parametric axes). The ITERATION dimension is inflated 7.0x compared to modern distillation, while FREE variation is deflated 6.3x — consistent with a parameterized process control manual rather than a recipe collection (C1222-C1224).

### Apparatus Vocabulary Classification

Different apparatus types (alembic, balneum marie, retort, sealed vessel) require different control vocabularies. Bottom-up profiling using Brunschwig-grounded marker MIDDLEs reveals 5 apparatus profiles (DISTILLATION, SEALED_VESSEL, SUSTAINED_HEAT, PRECISION, DIRECT_FIRE) that classify folios by their dominant operational vocabulary.

REGIME strongly predicts apparatus type: R1 and R3 are single-apparatus (97% and 95% distillation), while R2 and R4 mix apparatus types within the same fire degree — consistent with Brunschwig's description of applying the same temperature via different apparatus. The DISTILLATION and PRECISION profiles are strongly anti-correlated (rho = -0.666, p < 0.0001): folios specialize in one or the other.

The strongest single-MIDDLE discriminator is `aii` ("unseal"): 41x enriched in REGIME_3 relative to REGIME_1, appearing in 70% of R3 folios versus 3.1% of R1 folios. Line context shows a batch transition pattern: close/check → unseal → open/continue. This confirms R3 operates as a batch process requiring physical unsealing between runs, while R1 operates as continuous-run distillation.

Section H (Herbal) is the most apparatus-diverse section — the only section where no single apparatus profile dominates. In mixed-apparatus REGIMEs, non-distillation folios are overwhelmingly Herbal, reflecting the variety of botanical processing (gentle extraction, sustained maceration, precision control) versus the more uniform distillation of pharmaceutical preparations.

### What Doesn't Align

The comparison is not perfect. Some Brunschwig-derived predictions about line-level organization were not supported, and the manuscript's grammar is significantly more abstract than Brunschwig's prose recipes. The manuscript is a control system reference; Brunschwig is an instructional manual. They share domain and structure but differ in format and audience.

---

## The Galenic Framework Connection

Brunschwig (1500) isn't the only point of comparison. The project also tested against John of Rupescissa's *De consideratione quintae essentiae* (1351) — a 150-year-older text that uses the full Galenic classification framework: 4 qualities (hot, cold, dry, humid) x 4 degrees of intensity, producing a 16-cell combinatorial matrix for classifying materials.

This comparison is a **Tier 4 interpretation** — it requires accepting the Galenic framework as the organizational lens.

### What Was Tested

Phase 376 tested 4 structural predictions the Galenic framework makes about any system that implements it:

| Test | Prediction | Result |
|------|-----------|--------|
| Multi-axis hazard | Hazard operates across multiple quality axes, not just heat | **PASS** — 5 independent failure dimensions, only 1 thermal |
| Oppositional pairing | Exactly 2 orthogonal oppositional axes | **PASS** — lane split + sister pair, partial r = -0.064 |
| Degree ordering | Within each quality axis, degrees form an ordered progression | **PASS** — 4/6 PREFIX channels show significant ordering |
| Quality-degree factorization | Quality and degree are independently factored | **PARTIAL** — 58.1% follows block-diagonal structure |

### The Enhancement Pattern

Phase 377 synthesized how the Voynich's constraint system relates to the Galenic original across 6 structural dimensions. In every case, the Voynich preserves the organizational logic but enhances it in the same direction:

| Galenic Element | Voynich Enhancement | Ratio |
|----------------|---------------------|-------|
| 4 named qualities | 9 affordance bins defined by behavioral signatures | 2.25x categories |
| 4 discrete degrees | 14-63 frequency-ranked MIDDLEs per channel | 3.5-15.75x resolution |
| Additive compound properties | Compatibility-graph mediated compounds | 12x predictive differential |
| 12 named operations | 49 distributional equivalence classes | 4.1x operations |
| "Avoid degree 4" prohibition | Precision-constrained execution with safety buffers | Prohibition → engineering |
| "Use with caution" warnings | Topological forbidden graph (17 transitions, 5 classes) | Scalar → directed topology |

The consistent direction across all 6 axes — toward greater abstraction, higher resolution, and structural enforcement of what had been narrative guidelines — suggests a designer who understood the Galenic organizational logic and re-implemented it in a more precise notation system.

### From Material Matrix to Process Matrix (Tier 4)

The Galenic 4x4 matrix classifies **things** — what a material IS (hot, cold, dry, humid at degrees 1-4). The Voynich system classifies **actions** — what an operator DOES (energy input, monitoring, scaffolding, flow control at varying intensities). The organizational principle is the same (multi-axis classification with graduated intensity and hazard at the extremes), but the subject changed from materials to procedures.

The token morphology itself is this process matrix in action: PREFIX selects the operational axis (analogous to Galenic quality) and MIDDLE selects the specific operation within that axis (analogous to Galenic degree). C1019 confirmed mathematically that the morphological system has genuine multi-dimensional matrix structure (rank-8 tensor, 97% variance, pairwise-sufficient).

The transition wasn't a clean break — traces of the Galenic starting point survive. The following table is **illustrative, not tested** — the specific quality-to-channel mappings are plausible interpretive parallels, not statistically validated correspondences. What IS validated is the structural fact that only 6% of hazards are thermal (Tier 0) and that the organizational architecture aligns with Galenic logic (Phase 376, 3/4 PASS):

| Galenic axis | Possible Voynich parallel | Structural evidence |
|---|---|---|
| Hot | qo energy channel | ENERGY_OVERSHOOT hazard (6%) — the one dimension with direct Galenic overlap |
| Cold | ch/sh monitoring pair | Sensory assessment role (C929) — parallel to Galenic sensory quality testing |
| Dry | Phase/composition tracking | PHASE_ORDERING (41%), COMPOSITION_JUMP (24%) — no direct Galenic parallel |
| Humid | Flow/containment tracking | CONTAINMENT_TIMING (24%), RATE_MISMATCH (6%) — no direct Galenic parallel |

ENERGY_OVERSHOOT accounts for only 6% of all forbidden transitions — the one hazard dimension that maps to the Galenic temperature axis. The other 94% represents process-specific hazards (phase ordering, purity, containment, flow balance) that have no parallel in Galenic material classification. These hazards arise from the physics of phase transitions in sealed apparatus — failure modes that simply don't exist in open-bench pharmacy. Whether this 6% figure reflects direct Galenic inheritance or simply the rarity of thermal damage in distillation is an open question.

Brunschwig (1500) provides evidence of this transition in progress. He explicitly started from the Galenic framework but collapsed 4 quality axes to just 1 (fire degree) because heat is the only quality a distiller directly controls. But one axis proved too simple — it can't encode phase ordering or containment timing. The Voynich author went further: kept the multi-axis architecture, but rebuilt the axes around what a process operator actually needs to track.

Phase 378 confirmed the boundary: the Galenic framework predicts the organizational **shape** of the Voynich system (3/4 structural tests pass) but fails at the recipe **level** (0/3 physics tests pass). The architecture transferred; the specific content was rebuilt for a harder problem.

### Grammar-Level Tests (Phase 384)

Phase 384 pushed deeper, testing whether the Galenic framework left quantitative fingerprints in the grammar itself — not just organizational alignment, but specific predictions the Galenic system makes about how numbers should behave.

| Test | Galenic Prediction | Result |
|------|-------------------|--------|
| Degree-4 universality | Rare operations are universally dangerous | **FAIL** — opposite is true: COMMON operations are closest to hazards (rho=0.15-0.25 across all channels) |
| Elemental kernel grammar | k/h/e transitions follow potency gradient between tokens | **FAIL** — between-token transitions are flat; the one-way valve (C521) is a within-MIDDLE construction property |
| Concoction duration | Processing time scales non-linearly with material complexity | **FAIL** — paragraph length is perfectly linear with PP count (R2=0.997) |
| Section predicts dynamics | Subject matter shapes program style | **PASS** — section explains 35.5% of AXM variance: Bio programs most stable (0.754), Herbal most diverse (0.587) |

Score: **1/4 grammar-level Galenic predictions confirmed** — and the one that passed (section-dependent dynamics) isn't uniquely Galenic; any domain-spanning system would show it.

**The conclusion sharpened:** The Galenic framework is the author's *training background*, not the system's *design principle*. The author organized their work using Galenic categories (organizational alignment confirmed, 6/6 axes) but the control grammar they built transcended the Galenic framework at every quantitative level. Common operations cluster near hazards (pragmatic engineering, not degree theory). Processing scales linearly (efficient design, not concoction kinetics). The construction-layer asymmetry (C521) exists but doesn't propagate to execution-layer elemental ordering.

### Bio Section Distinctiveness (Phase 385)

Phase 385 tested whether the Bio section (f74-f84, the botanical folios with detailed plant illustrations) encodes a structurally distinct operational mode. Two competing hypotheses were pre-registered: (1) Bio encodes medical treatments alongside distillation (multi-domain), or (2) Bio encodes a specialized gentle heating stage (balneum mariae).

Results strongly favor the balneum mariae interpretation. Bio is k-enriched (34.1% kernel operations vs 24.9% elsewhere, surviving REGIME control), apparatus-hazard depleted (24.4% vs 32.2%), and LINK-depleted (0.63% vs 2.81% — almost no monitoring pauses). Within REGIME_1, Bio diverges on 6 of 8 tested dimensions. The QO-dominant CC trigger pattern (44.8% vs 13.0%) drives the kernel shift through known PREFIX-MIDDLE compatibility pathways.

The profile: continuously-engaged, energy-dominant, checkpoint-free, dynamically stable. This describes a process running under gentle sustained heat where thermal inertia (a water bath) eliminates the need for frequent monitoring — exactly what balneum mariae provides. The multi-domain medical hypothesis was rejected: medical treatment would predict more hazard-handling and endpoint operations, not more kernel activity.

### What This Means

A 670-year-old classification framework, developed for an entirely different purpose (pharmacological theory), independently predicts 3 of 4 structural properties of a system derived purely from computational analysis of the manuscript. The constraint system was built bottom-up with zero reference to medieval classification. The Galenic framework was applied top-down from historical sources. The convergence is non-trivial.

### Rosettes Foldout (Phases 387-405, Revalidated Phase 402)

The Rosettes foldout (f85-f86, 7 folios) is the manuscript's most structurally unusual section. Initial analysis (Phases 387-392) used the EVA H transcriber track, but Phase 402 revealed that the H track only captures ~33% of the foldout's text. Revalidation using Zandbergen (ZL) transcription with manual spatial annotation (`data/rosettes_annotated.json`) replaced all 21 original constraints with 10 new ones (C1124-C1133).

**Metalayer confirmed (C1126):** The Rosettes functions as an organizational metalayer sitting above the standard A/B/AZC systems. It is not a standard B program page, not a standard AZC positional page, but a meta-structural reference index.

**AZC-like grammar (C1127):** All entity types (ring text, labels, paths, spiral, clock) show consistent AZC-type morphology: grammar coverage ~42% (B: ~100%, AZC: ~50%), kernel density 29-41%, PP ~50%/RI ~2%. Not a hybrid — the old hybrid classification was a data artifact.

**Bridge enrichment (C1124):** 3.05x enrichment over B corpus (21.5% vs 7.0%). Universal across all sub-region types — ring 4.56x, labels 4.74-5.17x, clock 7.11x. The foldout preferentially samples the 85 cross-system vocabulary items that bridge A's discrimination manifold to B's execution grammar.

**Generic indexing (C1128):** All 9 rosettes point to approximately the same B folios (mean inter-rosette Jaccard of top-5 sets = 0.322; f40v in top-5 for 8/9 rosettes). The foldout is a shared vocabulary hub, not a specific lookup table. Any index function operates through vocabulary-mediated correlation (C384.a), not direct A-to-B addressing.

**Ring text structure (C1130-C1132):** Ring text has 0/277 forbidden transition violations but transition entropy 7.92 bits (vs B's ~0.41) — it respects hard constraints but ignores soft ones. It interleaves two populations: B-grammar bridge tokens (short, simple, 100% bridge) that serve as index entries, and unclassified identification tokens (long, complex, mostly non-bridge) that label foldout-specific concepts.

**Section targeting — qualified (C1125, C1133):** All 9 rosettes correlate most strongly with Section T at the section level, but this is a vocabulary-size artifact (C1133). Section T has only 1 non-Rosettes folio (f66r, 112 MIDDLEs); per-folio, f66r ranks only #11/76. The top 10 overlapping folios are 9 Section S + 1 Section H. Bridge density anticorrelates with overlap (rho = -0.60). The foldout indexes diverse, vocabulary-rich folios — not Section T specifically.

At Tier 3, the Rosettes functions as a **general-purpose vocabulary reference hub** — an organizational index that connects the manuscript's control vocabulary through bridge MIDDLEs. Its AZC-like grammar is consistent with a positional encoding system rather than executable programs or registry entries.

New constraints: C1124-C1133.

### Cross-System Vocabulary Flow (Phase 406)

Phase 406 resolved a key architectural paradox: shared pipeline vocabulary is type-universal across sections (Herfindahl 0.701, C1049) yet B output is 96% section-specific (C909). How does universal input produce specific output?

**Frequency modulation (C1134):** The same shared/PP MIDDLEs appear in all B sections but at section-specific token frequencies. PP vocabulary drives 74% of between-section JS divergence. B-exclusive vocabulary is maximally section-specific per-type but carries only 5.8% of tokens — negligible for section discrimination. The paradox resolves: vocabulary is type-universal but frequency-specific.

**Dark pipeline (C1135):** Of 404 PP MIDDLEs shared between A and B, only 89 match B grammar classes. The other 315 are overwhelmingly present in B (95.2%) but at dramatically lower frequency (mean 5.7 tokens vs 224.8 for matched). They are section-concentrated, mostly compound (66.7%), and constitute the HT/UN derivational substrate — the morphological bridge between A's registry and B's unclassified layer.

**Uniform flow (C1136):** A-Herbal and A-Pharmaceutical produce indistinguishable B coverage profiles (cosine 0.9997). The pipeline is section-blind. Pipeline grammar is highly concentrated: 12 A folios cover 100% of B's 89 classified MIDDLEs, with f58v alone covering 60.7%. But the full B inventory ceiling is only 30.4% from all 114 A folios — 70% of B vocabulary is completely B-internal.

New constraints: C1134-C1136.

### Dark Pipeline Characterization (Phases 470-473)

Further investigation revealed that the 315 dark pipeline MIDDLEs and the 85 bridge MIDDLEs constitute two structurally distinct vocabulary channels with different behaviors across every tested dimension:

- **Bridge channel** (85 MIDDLEs): Actively reshaped by B — amplifies THERMAL and OPERATION categories, suppresses STAGING and MONITORING (C1347). Bridge MIDDLEs are the grammar's working vocabulary.
- **Dark channel** (300 MIDDLEs): Preserves A's category distribution unchanged (rho=0.976, JSD=0.009; C1349). Dark MIDDLEs pass through without B reshaping them.

Dark MIDDLEs distribute atomistically — no co-occurrence groups, no clustering, random adjacency patterns (C1350). Each dark MIDDLE constrains the immediately following grammar token to a narrow set of instruction classes (successor entropy 2.59 bits vs 4.18 for bridge; C1351), and this constraint is MIDDLE-specific, not just PREFIX-mediated (C1356). However, this influence is strictly local: dark MIDDLEs affect only the next token, not line-level bridge-to-bridge transitions (C1354). The three-tier grammar model (dark=context → bridge=execution → suffix=mode) was tested and falsified — dark tokens are inline annotations with very localized ripple effects, not a grammar tier.

New constraints: C1347-C1357.

---

## What This Analysis Cannot Determine

Certain questions are structurally unanswerable from the manuscript's grammar:

- **What substance is being processed** — The grammar encodes operations, not materials
- **Who wrote it** — Nothing in the structure identifies an author or school
- **What individual tokens "mean"** — Operational roles are not word meanings; "this prefix selects heat operations" is not the same as "this prefix means heat"
- **What the illustrations depict** — Illustrations do not constrain text content (statistically proven)

These are not gaps in the analysis. They are properties of the system: a control grammar that works precisely because it is domain-general.

The remaining questions — authorship, specific materials, precise token-to-operation mappings — will likely be resolved through **archival research** (uncatalogued guild records, apothecary inventories, and teaching manuscripts from early 15th-century Central Europe) and **domain expertise** from historians of distillation or practitioners familiar with pre-industrial reflux technique. The computational analysis has narrowed the search space; the answers themselves are probably sitting in an archive in Vienna, Prague, or the Upper Rhine.

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

## How This Analysis Was Built

This project was built using AI-assisted computational analysis over 506 research phases. The primary development environment was [Claude Code](https://claude.ai/claude-code) (Anthropic), with independent cross-validation from GPT-5 (OpenAI) at key decision points.

The central methodological innovation is a **progressive context system**: a growing body of numbered, tiered, validated constraints that accumulates across research phases and is always available to the AI agents performing analysis. Every finding that survives statistical testing becomes a permanent constraint. Every falsified hypothesis is permanently closed. Each new phase starts with full knowledge of everything that came before.

This matters because no single analytical session — human or AI — could discover 49 instruction classes, 17 forbidden transitions, 6 macro states, 8 cross-system operational categories, an 18-atom instruction encoding architecture, and the Brunschwig alignment in one pass. But 506 phases, each building on validated prior work and never losing what was already proven, could. The constraint system is the project's memory, and its growth is what made the depth of analysis possible.

For technical details on the progressive context architecture, see the Methodology section in `README.md`.

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
| See the historical network | `phases/HISTORICAL_NETWORK/HISTORICAL_NETWORK.md` |
| Run the core analysis library | `scripts/voynich.py` (see `CLAUDE.md` for examples) |
| View a decoded folio | `python scripts/show_b_folio.py f76r -p` (paragraph view) |
| View control flow | `python scripts/show_b_folio.py f76r --flow` (macro states + FL stages) |
| View full metadata | `python scripts/show_b_folio.py f76r --detail 4` (all classification layers) |
| Decoder documentation | [`scripts/DECODER.md`](scripts/DECODER.md) (all 6 modes, flags, gloss pipeline) |
