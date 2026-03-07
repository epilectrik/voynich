# The Voynich Instruction Word: Complete Control Architecture

**Phase 550 | Version 1.0 | 2026-03-06**

**Status:** DEFINITIVE SYNTHESIS -- derived from 1,410 validated constraints across 549 prior phases.

---

## Purpose

This document formalizes the complete instruction word structure, safety architecture, organizational model, and cross-register document stack of the Voynich Manuscript's Currier B control grammar. It is a self-contained specification: readable without looking up individual constraints, though constraint numbers are cited throughout for traceability.

Every claim below is Tier 0 or Tier 2 (structurally validated). No Tier 3-4 interpretations appear in the formal specification sections. An interpretive appendix at the end maps structural findings to the best-fit historical model.

---

## I. The Instruction Word

Every Currier B token is a single executable instruction. The 23,243 tokens in 83 folios decompose without remainder into four positional slots:

```
TOKEN = [ARTICULATOR] + [PREFIX] + MIDDLE + [SUFFIX]
```

Brackets indicate optional slots. MIDDLE is the only mandatory component. Together, these four slots encode a complete instruction that specifies an operational domain, a risk profile, an action within that domain, and an outcome annotation -- all in a single word.

### I.1 ARTICULATOR (Optional Entry Marker)

**Frequency:** ~4.4% of tokens (C1416)
**Inventory:** y-dominant; the same y-atom that serves as a terminal in MIDDLE position (C1562 confirmation)

The articulator is a line-entry orientation marker. It does not carry independent category information -- its category profile is fully determined by the MIDDLE it precedes (C1421, category JSD=0.030).

**Structural properties:**
- Concentrates 4.5x at line-initial position (C1417)
- Requires ch/sh PREFIX; categorically excluded with bare or qo prefixes (C1418)
- Selects toward e-HEAD MIDDLEs (1.81x) and away from k-HEAD (0.10x) (C1419)
- Suppresses suffix attachment to 0.55x baseline rate (C1420)

**Function:** The articulator marks a token as a line-entry point within the ch/sh (testing/monitoring) operational channel. It is an allomorphic variant of the PREFIX system, not an independent information carrier. A token with an articulator says the same thing as one without -- it just signals "I am at or near line start in a monitoring context."

---

### I.2 PREFIX (Routing and Safety Header)

**Frequency:** Present on the majority of tokens
**Inventory:** 15 characters in a three-tier positional classification (C1534):

| Tier | Characters | Position in PREFIX | Function |
|------|------------|-------------------|----------|
| **MODIFIER** | q, d, f, p, y, s | Position 0 (96-100%) | Selects variant within base domain |
| **BASE** | h, e | Position 1+ only | Defines core operational domain |
| **DUAL** | o, k, l, t, c, a, r | Either position | Context-dependent role |

The PREFIX is an internal base-modifier grammar (C1218, C1219, C1220) that operates parallel to the MIDDLE's own HEAD+MOD+TERM structure. The base character (final character of PREFIX) determines which MIDDLE family the token accesses:

| Base | MIDDLE Domain | Enrichment | Example PREFIXes |
|------|---------------|------------|------------------|
| o-base | Arrangement (o-HEAD) | STAGING/OPERATION | qo, po, do, so |
| k-base | Thermal (k-HEAD) | THERMAL | ok, qk |
| h-base | Monitoring (e/h-HEAD) | STABILITY/CLOSURE | ch, sh, pch, dch |
| e-base | Stability (e-HEAD) | STABILITY | te |
| a-base | Headless compounds | OPERATION/TRANSITION | da, sa, ta |

**Key routing rules:**
- **q-modifier activates THERMAL on o-base** at 64% k-HEAD rate, providing ~7x hazard protection vs other o-modifiers (C1538, C1549). This is the strongest single-PREFIX safety mechanism.
- **a-base is the universal headless gateway** at 94-96% headless rate regardless of modifier (C1537). The da/sa/ta PREFIXes are headless-exclusive across all three systems (C1524).
- **i-atom is categorically excluded from PREFIX** (C1535). Iteration is MIDDLE-internal only.
- **Sister pairs** are same-base (ch/sh) or same-modifier (ok/ot) variants with HEAD JSD<0.01 (C1539). They are operational mode selectors -- how carefully an operation is performed -- not different operations.

**Hazard routing chain (PREFIX to risk):**
PREFIX base determines HEAD selection (V=0.478, C1536), HEAD determines hazard immunity (binary: headed=0% source, headless=24.5% source, C1546), and TERMINAL determines hazard class type (categorical, C1547). The full chain: base -> HEAD -> immunity -> TERMINAL -> class type. PREFIX is the entry point to the entire safety architecture.

**Function:** PREFIX is a routing and safety header. It selects the operational channel (which family of MIDDLEs), the risk profile (how much hazard exposure), and the line-positional context (where in the line this instruction belongs). It does NOT determine what specific action occurs -- that is MIDDLE's job.

---

### I.3 MIDDLE (Core Instruction)

**Frequency:** Mandatory on every token
**Structure:** HEAD + MOD* + TERM (C1393, C1394)

The MIDDLE is the core instruction -- what action this token encodes. It decomposes into three sub-slots with 18 atoms distributed across them:

#### I.3.1 HEAD (Position 0) -- Domain Selector

Five headed domains plus a sixth headless domain:

| HEAD | Domain | Category Profile | Hazard | Self-Transition | Key Property |
|------|--------|-----------------|--------|-----------------|--------------|
| **k** | THERMAL | 90.3% THERMAL | 0% intrinsic immunity (C1476) | 16.7% (switching) | Pure heating/energy |
| **t** | FLOW | 87.0% FLOW | 0% (headed) | 9.1% (rare) | k's terminal mirror (C1478) |
| **e** | STABILITY | Balanced multi-category | 0% (headed) | 28.5% (persistent) | Primary stability anchor |
| **o** | ARRANGEMENT | Terminal-deterministic (C1556) | 0% source AND 0% target (C1561) | 13.6% (switching) | Channeled through terminal |
| **a** | ITERATION | 66% forbidden rate | 0% (headed) | 25.2% (persistent) | Primary hazard carrier (C1477) |
| **--** | HEADLESS | OPERATION/TRANSITION | 24.5% source rate | 28.4% (persistent) | Sixth domain (C1488) |

The HEAD atom is the primary domain selector. It determines category (operational type), hazard exposure (binary: headed = safe, headless = potentially hazardous), modifier compatibility (C1479), and terminal structure -- all in a single atom choice (C1475).

**Critical distinction:** HEAD *presence* gates whether a token can be a hazard source (binary). HEAD *identity* determines operational domain (categorical). These are two independent information channels carried by one atom position.

The headless domain is not a grab-bag -- the pseudo-HEAD (first atom in a headless MIDDLE) differentiates functionally: d=OPERATION, i=TRANSITION, l=STAGING (C1489, V=0.511). Headless compounds shift terminal preferences toward transparent h (2.98x enriched) and channeled n (2.45x), while avoiding category-imposing locked terminals r/m (6.2x depleted, C1490).

#### I.3.2 MOD (Optional Modifiers) -- Operation Parameterization

| Modifier | Primary Affiliation | Function | Hazard Effect |
|----------|---------------------|----------|---------------|
| **i** | a-HEAD (89%, C1480) | Iteration control | Simpson's paradox: SELECTS hazardous frames but PROTECTS within them (C1452-C1456) |
| **d** | e-HEAD stability | Sealing/marking | Quenches hazard to 0% (C1450) |
| **c** | Slot-switcher (C1542) | Context-dependent | Quenches hazard to 0% |
| **p** | o-HEAD arrangement (C1543) | Marking/pause | Quenches hazard to 0% |
| **f** | o-HEAD arrangement (C1543) | Flagging | Quenches hazard to 0%; lowest bridge rate (C1545) |
| **s** | Universal connector (C1474) | Connects across frames | Quenches hazard to 0% |

Modifiers are governed by **co-occurrence avoidance**, not stacking order (C1472). Eight of fifteen modifier pairs never co-occur -- the grammar restricts WHICH modifiers combine, not HOW they stack. This is a selectional grammar: compatible subsets, not sequential layers.

The modifier count matters more than modifier order. Key gradient for i-modifier:
- No i: 79% forbidden rate in a-HEAD frames
- Single i: 69% forbidden (reduced via r-terminal collapse 84x, C1481)
- Double ii: 0% forbidden (locked to n-terminal at 94%, C1482)

All modifiers except i quench hazard categorically to 0% when present (C1450). Modifiers are parametric refinements that almost always make instructions safer.

#### I.3.3 TERM (Final Position) -- Exit Gate

| Terminal | Opacity | Category Specificity | Suffix Rate | Key Routing |
|----------|---------|---------------------|-------------|-------------|
| **r** | LOCKED | FLOW 98.9% | 17-20% (semi-transparent) | r -> a-HEAD 2.23x (C1563) |
| **m** | LOCKED | TRANSITION 87.9% | <5% (opaque) | m -> o-HEAD 1.55x |
| **y** | CHANNELED | OPERATION context-dep | <5% (opaque) | y -> k-HEAD 1.60x |
| **n** | CHANNELED | CONTAINMENT/TRANSITION | <5% (opaque) | n -> (neutral) |
| **l** | CHANNELED | STAGING context-dep | 17-20% (semi-transparent) | l -> e-HEAD 1.25x |
| **h** | DIFFUSE | TRANSPARENT (V=0.988 passthrough) | >98% (transparent) | h -> t-HEAD 1.89x |
| bare | -- | -- | -- | (neutral) |

The terminal atom is a **dual-function linchpin** (C1562, C1563). It simultaneously:

1. **Gates suffix attachment** via a three-tier opacity gradient (C1440-C1445): opaque terminals (m, n, y) suppress suffixes below 5%; semi-transparent (l, r) allow 17-20%; transparent h allows >98%. This is an active exclusion grammar (chi-squared=7,385, V=0.753, C1441), not frequency correlation.

2. **Routes the next token's HEAD domain** via terminal-to-HEAD preference links (C1563). When a token ends with r, the next token is 2.23x more likely to have an a-HEAD. When it ends with h, the next is 1.89x more likely to have a t-HEAD.

3. **Determines hazard class type** categorically (C1547): y -> PHASE_ORDERING, l -> CONTAINMENT_TIMING, bare -> RATE_MISMATCH, h -> ENERGY_OVERSHOOT.

Terminal and suffix carry **complementary, not redundant** information (only 8.2% redundancy, C1443). Opacity is independent of category concentration (C1444) -- suffix suppression and category imposition are orthogonal mechanisms operating through the same atom.

---

### I.4 SUFFIX (Outcome/Condition Annotation)

**Frequency:** ~40% of tokens
**Structure:** Attenuated HEAD+TERM parallel to MIDDLE (C1510)

The suffix is a backward-facing annotation that records outcomes or conditions -- never actions. It uses only 13 of 18 atoms, categorically excluding {k, t, p, f, c} -- the "instruction-only tier" (C1511, C1541). This is the sharpest functional partition in the atom system: MIDDLE encodes what to DO, suffix encodes what RESULTED or what CONDITIONS apply.

**Suffix first-atom** selects category at 53% of MIDDLE HEAD strength (V=0.277, C1510). **Suffix last-atom** selects positional scope at 1.68x MIDDLE TERM strength (R-squared=0.059). Suffix is a compositional domain parallel to MIDDLE but attenuated in discriminative power.

**Suffix carries zero forward information** (C1564, JSD=0.0021). The next token's HEAD distribution is identical whether the current token has a suffix or not. Suffix scope terminates at the token edge -- it annotates the current instruction only, never influencing what comes next. This extends the pairwise compositionality principle (C1003) to the cross-token boundary.

**Two suffix modes** emerge from token composition (C1229, C1341):
- **Mode A:** THERMAL/MONITORING specification. Terminal-suffix dominant (-edy, -eey). Medial position.
- **Mode B:** FLOW/STAGING continuation. Bare or boundary-biased. Carries 100% of forbidden violations (C1451).

Mode is ~80% determined by token identity and ~20% by context (PREFIX 50%, environment 29%, position 12%, opener 8%, C1346). Both modes appear in every paragraph of sufficient length (8+ body lines, C1229). They are not sequential phases but parallel operational tracks (C1258).

---

### I.5 The Cross-Token Instruction Chain

Individual tokens do not exist in isolation. The terminal atom of one token preferentially selects the HEAD domain of the next, creating directional instruction phrases:

```
... TERM(n) --> HEAD(n+1) --> MOD*(n+1) --> TERM(n+1) --> HEAD(n+2) ...
              |                              |
              suffix(n)                      suffix(n+1)
              [dead end]                     [dead end]
```

The suffix branch is a dead end -- it carries zero forward information (C1564). The cross-token chain flows exclusively through TERM -> HEAD routing (C1563):

| Terminal | Routes To | Enrichment | Interpretation |
|----------|-----------|------------|----------------|
| r (FLOW) | a-HEAD (ITERATION) | 2.23x | Flow completion hands to iteration |
| h (transparent) | t-HEAD (FLOW) | 1.89x | Transparent passthrough hands to flow |
| y (OPERATION) | k-HEAD (THERMAL) | 1.60x | Operation completion hands to thermal safety |
| m (TRANSITION) | o-HEAD (ARRANGEMENT) | 1.55x | Transition closure hands to arrangement |
| l (STAGING) | e-HEAD (STABILITY) | 1.25x | Staging hands to stability |
| bare | -- | neutral | No routing preference |

These are probabilistic enrichments, not deterministic rules. They create a directional grain in the instruction flow without imposing rigid sequence. The system "prefers" certain domain transitions but does not mandate them.

---

## II. The Safety Architecture

Safety is enforced at three independent levels that compose multiplicatively. A hazard can only occur when all three levels simultaneously fail to prevent it.

### II.1 Level 1: Construction Exclusion (Token Inventory)

The vocabulary itself prevents certain dangerous combinations from ever being assembled:

**The ch/sh bigram partition (C1553):** ch and sh are PREFIX-domain bigrams that categorically never appear at MIDDLE-initial position in compounds of length 3+. The ratio is 5,821 PREFIX occurrences to 0 MIDDLE-initial occurrences. Individual atoms c, s, h all appear freely in MIDDLE position -- the prohibition operates at bigram granularity, not atom level.

**Phantom MIDDLEs (C1554):** Five of nine hazard-source MIDDLEs (chey, shey, chedy, shedy, chol) have exactly zero corpus tokens. They are structurally conceivable -- every atom is in a legal slot -- but the ch/sh bigram partition prevents their construction. The forbidden transition topology (Level 3) covers these phantom MIDDLEs anyway, providing defense-in-depth: vocabulary exclusion plus transition prohibition equals two independent safety layers.

**Instruction-only tier (C1541):** The five atoms {k, t, p, f, c} are categorically excluded from suffix position. Suffixes encode outcomes and conditions, never actions or parameters. This prevents action atoms from "leaking" into annotation position where they might be misinterpreted.

**c+h positional selectivity (C1555):** 49 of 55 c-initial compounds contain h, but h is always at position 2+ (c+[k/t/f/p]+h pattern). c+h adjacency at positions 0-1 is categorically absent, maintaining the bigram partition even within compounds.

### II.2 Level 2: Hazard Source Typing (Token-Level Binary Gate)

Every token is typed as safe or potentially hazardous based on a single binary feature: HEAD presence.

**The HEAD gate (C1546):** All 16,819 headed tokens (those with a HEAD atom from {a, e, o, k, t} at position 0) have exactly 0% hazard source rate. Zero exceptions across the entire corpus. Hazard sources come exclusively from the 6,277 headless tokens, of which 24.5% are sources.

This is the strongest single safety mechanism in the system. It means that any instruction with a recognized domain selector is categorically incapable of initiating a hazardous transition. Only infrastructure/identification tokens (headless compounds) can be hazard sources.

**k-HEAD special status (C1476):** k-HEAD tokens have 0% hazard in ALL compositional contexts -- not just as sources but as targets. This is intrinsic immunity that holds regardless of modifier, terminal, or PREFIX. k-HEAD is the "safe thermal zone" of the grammar.

**o-HEAD double immunity (C1561):** o-HEAD tokens have 0% hazard as both sources AND targets across all 2,717 tokens. Combined with y-terminal depletion to 0.007x (C1557), o-HEAD is structurally immune to the dominant hazard class (PHASE_ORDERING).

**Modifier quenching (C1450):** Within headless tokens, modifiers {c, d, f, p, s} quench hazard categorically to 0%. Only unmodified or i-modified headless tokens carry hazard. The i-modifier is special: it selects hazardous frames (a-HEAD at 89%) but protects within those frames (net effect -0.069, C1480).

### II.3 Level 3: Transition Prohibition (Sequential Grammar)

Seventeen forbidden transitions between instruction classes define the hazard topology (C109). These are directional (C783) and disfavored at ~65% compliance (C789), not absolute prohibitions.

**Five hazard classes (C109, C1528):**

| Class | Frequency | Atom Signature | Mechanism |
|-------|-----------|----------------|-----------|
| PHASE_ORDERING | 41% (dominant) | headless y-terminal (dy) -> a-HEAD | Sequencing failure: completion (y) followed by iteration (a) |
| CONTAINMENT_TIMING | 24% | l/r semi-transparent terminals | Container timing: STAGING/FLOW terminals in wrong sequence |
| RATE_MISMATCH | 18% | bare terminal | Rate control failure |
| ENERGY_OVERSHOOT | 12% | h-terminal | Energy excess through transparent terminal |
| FLOW_CHAOS | 6% | mixed | Flow disruption |

**Spatial routing (C1463-C1466):** The line-level position of hazardous tokens is not random. ZERO-hazard (e->y frame) concentrates at line-initial SPECIFICATION zone (1.236x). k-IMMUNE tokens concentrate at THERMAL_WORK zone Q1-Q3 with sharp Q1 peak (1.311x). HIGH-hazard concentrates at CLOSURE zone Q4 (1.134x). The line grammar ROUTES hazard to line-final where closure mechanisms contain it. This pattern is invariant across line lengths (V=0.081-0.091, C1466).

**Defense-in-depth summary:**

```
Level 1 (Construction):    Can this token exist?          --> 5 phantom MIDDLEs blocked
Level 2 (Typing):          Can this token be hazardous?   --> All headed tokens: NO
Level 3 (Transition):      Can this sequence be hazardous? --> 17 forbidden transitions
```

Each level operates independently. A dangerous event requires: a token that passes Level 1 (exists in vocabulary), that is hazardous at Level 2 (headless, unmodified or i-only), that participates in a forbidden transition at Level 3. The probability compounds multiplicatively.

---

## III. The Organizational Model

### III.1 The Line: Complete Safety Envelope

The line is the fundamental unit of safe execution. Every structural safety mechanism operates at line scope with no cross-line memory.

**Two-step line architecture (C1566):**

```
Q0 (SPECIFICATION)    -->  Q1-Q3 (WORK ZONE)    -->  Q4 (CLOSURE)
                             |                         |
mild HEAD shift          uniform HEAD composition    sharp HEAD break (26x JSD jump)
ARTICULATOR 3.93x        THERMAL peak at Q1         m-terminal 196x enriched
STAGING 1.57x            k-IMMUNE onset             TRANSITION 1.63x
MARKING 1.42x            steady-state work          batch-close routing
```

The transition from WORK to CLOSURE is a hard step, not a gradient (C1566). HEAD JSD jumps 26x and TERM JSD jumps 20x at the Q3->Q4 boundary. The interior work zone Q1-Q3 is compositionally homogeneous (JSD<0.003 between adjacent quintiles).

**Information U-shape (C1430):** Token information content follows a U-shape across line position: Q0=10.29 bits, Q1-Q3~9.6 bits, Q4=10.11 bits. Boundaries carry specification and routing information; the interior is routine thermal work.

**Line-local safety (C1470-C1471):** Cross-line hazard correlation does NOT exist beyond folio-level shared environment. Within-folio shuffle collapses all apparent sequential signal (MI p=0.212). Hazard MI=0.0172 bits -- less than category MI (0.032 bits). There is no compensatory safe opening after high-hazard lines: e->y is DEPLETED 0.82x after high-hazard lines, not enriched (C1471). Each line independently opens safe, works hot, and closes dangerous with zero memory of the previous line.

**Cross-line independence confirmed (C1233, C670):**
- Adjacent lines share no more vocabulary than random (Jaccard obs=0.140)
- Suffix mode MI=0.003 bits, category MI=0.032 bits between adjacent lines (C1429)
- FL cross-line regression near-random entropy at 97.8% (C1233)
- CC trigger type re-selected independently each line (permutation p=1.0, C673)

### III.2 The Paragraph: Operational Unit

Paragraphs are gallows-delimited multi-line execution blocks (C864, PSC). They are the natural operational unit -- a coherent set of related control cycles.

**Header-body architecture:**
- **Header (line 1):** Modifier-divergent. Paragraph specification operates through modifier selection (p 3.66x, f 3.90x enriched in headers) not HEAD domain (HEAD JSD=0.008 between header and body, C1565). Headers are MARKING-enriched (2.44x) and STAGING-enriched (1.45x) while THERMAL is suppressed (0.46x, C1287). HT density: 46.5% at paragraph line 1, dropping to ~27% by line 2 (step function, C842).
- **Body (lines 2+):** Homogeneous execution (C963). Suffix mode cycling: two universal modes alternate (specification vs continuation) in every paragraph with 8+ body lines (C1229). The body exhibits a mild specification-to-execution gradient: rare vocabulary front-loaded, universal vocabulary increases late (C932).

**Self-containment (C845):** Paragraphs do not link to each other. No inter-paragraph linking detected; 7.1% both-position rate is symmetric (not directional like A's linker system). Each paragraph is a self-contained program.

**No preferred ordering (C1399):** Paragraphs have no preferred sequence within folios. Seven of eight ordering tests fail. Transition matrix shows zone INERTIA (self-transition O/E=2.02) but no sequential ramp (monotonicity rho=-0.052). Paragraphs are genuinely parallel subroutines, not sequential steps.

**State-independent (C1400):** Terminal physical state does not predict next paragraph zone. Folio-residualized thermal correlation FLIPS to -0.161 (compensatory cycling). Paragraphs are independently composed within the folio's thematic envelope.

**Four operational gradient zones (C1398):** Paragraphs form a continuous operational variation space (silhouette 0.113), not discrete types. The four zones -- THERMAL-QO, CONTAINMENT-Sealing, OPERATION-Iteration, MONITORING-Phase -- represent operational emphasis, not material or procedural differences. Same material, same equipment, different subroutines (dark-pipeline Jaccard 0.972 across zones, C1378).

### III.3 The Folio: Complete Program

Each of the 83 Currier B folios is a complete executable program (C531, C535).

**Program identity:**
- 98.8% of folios have at least one unique MIDDLE appearing nowhere else (C531)
- 88% of unique MIDDLEs are B-exclusive, not from Currier A (C532)
- Folio vocabulary minimality: 81/82 folios required for complete coverage (C535)

**Program parameterization:**
- REGIME (apparatus mode) is folio-level (C1325): each folio operates under a consistent thermal regime
- Sections (BIO, HERBAL, STARS_RECIPE, COSMO) determine REGIME composition and operational emphasis (C1404)
- AXM self-transition rate (the "how strongly does this program orbit its dominant mode" metric) is ~43% explained by structural predictors and ~27% genuine design freedom (C1169)
- PREFIX composition explains 94.4% of theoretical max AXM variance at paragraph level (C1431) -- near-deterministic

**No convergence narrative (C1401-C1403):** The early finding that programs "converge to STATE-C" (C325) is a section confound -- within every section the completion gradient collapses to zero. AXM is the dominant operational mode at section-determined rates (59-75%), not a terminal state that programs approach over time. MONOSTATE means thematic dominance, not sequential convergence.

---

## IV. The Document Stack (Cross-Register Architecture)

The manuscript comprises four structurally distinct systems sharing a global morphological type system (C383) and a unified atom ontology (C1499, min Jaccard 0.895 across all systems).

### IV.1 Currier A: Declarative Specification Registry

**114 folios, 11,415 tokens, folio-disjoint from B (C272)**

Currier A is a non-sequential categorical registry (C240). Each folio contains entries that specify constraints, materials, and configuration parameters -- what EXISTS and what DIFFERS -- without encoding execution sequences.

**Atom profile:** o-HEAD enriched at 28.5% (C1559), headless enriched at 39.0% vs B's 27.2% (C1523). A's declarative register naturally inflates arrangement and headless proportions because it describes situations rather than executing operations.

**Instruction encoding:** A MIDDLEs follow the same HEAD+MOD*+TERM grammar as B (Fisher p=0.90, C1395). Bridge MIDDLEs show 100% category stability across A and B (C1508). A records read as [arrangement(o-HEAD)] -> [parameters(e/k)] -> [identity(headless)] -- a situation description language encoding what things ARE, not what to DO (C1395).

**A-B relationship:** A does not map to B (C384). There is no token-level or context-free A-B lookup. Vocabulary sharing (69.8%, C335) exists because both systems describe the same operational domain, not because A entries "refer to" B programs. What A provides is constraint filtering: the PP (pipeline-participating) MIDDLEs shared between A and B determine which instruction classes survive in B contexts (C502, C504).

### IV.2 AZC: Configuration and Legality Bridge

**36 folios, 3,299 tokens, hybrid between A and B vocabularies (C301)**

AZC is a static positional lookup table that classifies vocabulary by legality zone (C313). Each PREFIX+MIDDLE has one fixed position reflecting its operational character.

**Atom profile:** o-HEAD zone-graded from A-like boundaries (S=29.3%) to B-like interiors (R=17.7%, C1517). HEAD dominates TERMINAL 5.2x in zone differentiation (C1518). AZC grades continuously from A-like (declarative, arrangement-heavy, dark-enriched) to B-like (executable, thermal/action-heavy, bridge-dominated, C1522).

**Function:** AZC encodes WHEN intervention is legal versus when outcomes must be accepted (C443). Position constrains legality, not prediction (C313). The legality gradient from R-series interior (restricted) to S-series boundary (permissive) creates positional escape gradients without encoding decisions.

### IV.3 Currier B: Executable Control Grammar

**83 folios, 23,243 tokens, 49 instruction classes at 100% coverage (C121, C124)**

Currier B is the execution layer. Every token is an instruction. Every line is a safety envelope. Every paragraph is an operational unit. Every folio is a complete program. The grammar enforces safety by construction: the topology of forbidden transitions, the HEAD-based hazard gate, and the vocabulary exclusion system together guarantee that most instruction sequences are safe without requiring the operator to evaluate risk.

**Atom profile:** e/k-HEAD enriched relative to A (C1507). Bridge MIDDLEs (85 types) form the executable backbone, carrying the dynamical structure that both A and B share (C1139, C1500).

### IV.4 Human Track (HT): Operator Orientation Layer

**7,042 tokens in B, 30.5% of B corpus (C740)**

HT tokens are morphologically normal compound tokens that fall below the classification threshold for the 49-class grammar (C610). They are NOT non-operational -- they contain operational content redundant with body simple MIDDLEs (71.6% atom hit rate vs 59.2% random, C935).

**Function:** HT serves as anticipatory vigilance (C459) -- preparing the operator for upcoming demands. HT density correlates with MIDDLE rarity (r=0.504, C477): where the task is hard (rare discriminators needed), HT frequency increases. HT is concentrated at line-1 of folios (50.2% vs 29.8% body, C747) and paragraph headers, providing folio-level and paragraph-level orientation.

**Independence:** HT does not alter subsequent grammar probabilities (V=0.10, C405) and does not improve prediction of subsequent content (C415). Coupling is unidirectional: system -> HT, not HT -> system (C416).

### IV.5 Dark Pipeline: Nominalized Identification Vocabulary

**300 MIDDLEs, 1,696 tokens, 100% HT/UN substrate (C1137)**

The dark pipeline is the identification layer -- A MIDDLEs that appear in B at low frequency (mean 5.7 tokens, C1135) and are MARKING-dominant (36.0%, C1505). Dark pipeline compounds are built from bridge atoms (96.5% contain at least one bridge atom, C1141) but use modified construction grammar (grammar-standard/extended PREFIX ratio 3.39 vs general HT 1.81, C1138).

**Function:** Dark MIDDLEs nominalize instruction atoms for identification purposes (C1505). They anti-correlate with bridge tokens (r=-0.865, C1146) -- where the executable backbone is dense, identification vocabulary is sparse, and vice versa. They are the primary vehicle for section-level vocabulary modulation (mean JS=0.483, 3.9x baseline, C1148).

---

## V. The Shared Atom Substrate

All four systems plus the dark pipeline draw from a single atom ontology of 18 characters (C1499). What differs between systems is not which atoms are available but how they are deployed across slots:

| Differentiation Axis | Mechanism | Evidence |
|----------------------|-----------|----------|
| HEAD selection | A emphasizes o/headless; B emphasizes e/k | C1507, C1523 |
| TERMINAL ecology | Bridge MIDDLEs have the most constrained terminal ecology | C1501 |
| MOD grammar | Universal (JSD<0.007 across non-bridge channels) | C1504 |
| Channel proportion | Bridge = executable backbone; Dark = nominalization | C1500, C1505 |

Atoms carry DIFFERENT information in different positions (C1513). All 12 atoms shared between MIDDLE and suffix are behaviorally divergent (mean JSD=0.526). e is most positionally stable (JSD=0.202); n is most divergent (JSD=1.000, complete categorical inversion from CONTAINMENT in MIDDLE to boundary-scope in suffix). Same alphabet, different semantics by position.

Cross-system suffix is identical: A and B both use exactly 13 atoms with JSD=0.050 (C1514). B enriches d/e/i (execution markers), A enriches o/h/l/s (arrangement/state markers) -- same atoms, different emphasis, paralleling the MIDDLE-level A/B split.

---

## VI. What the Operator Supplies

The manuscript is designed for experts, not novices (C197). It encodes everything that CAN be encoded about safe process control. What it deliberately omits are the 13+ types of judgment that cannot be reduced to notation:

| Category | Examples | Why Not Encoded |
|----------|----------|-----------------|
| **Material identity** | Which plant, mineral, compound | Grammar is domain-general; same control logic applies to any feedstock |
| **Sensory evaluation** | Taste, color, consistency | Requires real-time perceptual judgment |
| **MIDPROCESS handling** | What to do between documented steps | Tacit knowledge from apprenticeship (C1056) |
| **Hazard recognition** | Physical signs of failure approaching | Requires embodied expertise |
| **Timing judgment** | When to stop, when to proceed | No clock or duration encoding exists |
| **Material selection** | What to process, what order | External to the execution grammar |

The manuscript controls WHAT happens (through its grammar) and HOW MUCH risk is acceptable (through its safety architecture). The operator supplies WHEN, WITH WHAT, and WHETHER TO CONTINUE. This is design integrity, not incompleteness -- the omissions are deliberate acknowledgment that some knowledge cannot be encoded (C1056).

---

## VII. Generative Sufficiency

The grammar's minimal executable specification is fully characterized (C1025, C1034, C1365):

**Model M2.1:** 49-class first-order Markov transition matrix + symmetric forbidden suppression + quintile-conditioned class frequencies.

**Score:** 21/21 generative tests passed (C1365), after correcting three test specification errors (B4 misspecified for non-stationary data, C2 wrong CC class definition, B5 required symmetric suppression).

**What this means:** The grammar is generatively closed. A 49-class Markov chain that avoids forbidden transitions and shifts class frequencies by line position reproduces all measurable structural properties of the corpus. No hidden state, no accumulator, no cross-line memory, no three-way interactions are needed. The remaining variance is stochastic noise within the design freedom envelope (~27% at folio level, C1169).

---

## Appendix A: Historical Alignment (Tier 3-4)

*Everything below this line is speculative interpretation, consistent with but not proven by the structural findings above. It is included for completeness and is fully discardable.*

The structural architecture aligns most closely with late-medieval circulatory reflux distillation control (100% compatibility, C157, C171). The manuscript's radiocarbon date (1404-1438) places it in the peak era of guild pharmaceutical secrecy, between Rupescissa's theoretical framework (1351) and Brunschwig's first printed distillation manual (1500).

The alignment is architectural, not textual:
- 49 instruction classes map to Brunschwig's 4 degrees of fire at REGIME level
- 17 forbidden transitions map to "Fourth degree coerces -- reject it"
- The SETUP -> WORK -> CHECK -> CLOSE line cycle maps to fire-degree management
- The expert-oriented design maps to guild training models
- MIDPROCESS absence matches the structurally documented gap in all pre-1500 sources

The Puff-Voynich-Brunschwig triangle represents three orthogonal projections of a single late-medieval distillation curriculum: Puff catalogs materials (nouns), Voynich enforces safe execution (verbs), Brunschwig explains method (pedagogy).

---

## Appendix B: Notation Conventions

| Symbol | Meaning |
|--------|---------|
| HEAD, MOD, TERM | Positional slots within MIDDLE |
| C#### | Constraint number (see CONSTRAINT_TABLE.txt) |
| V= | Cramer's V effect size |
| JSD | Jensen-Shannon Divergence |
| x (as in 2.23x) | Fold enrichment relative to baseline |
| -> | Transition or routing direction |
| Q0-Q4 | Line position quintiles (Q0=initial, Q4=final) |

---

*Phase 550: Complete Control Architecture -- The Voynich Instruction Word*
*Synthesis of 1,410 constraints from 549 analytical phases*
*Generated 2026-03-06*
