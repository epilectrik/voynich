# AZC System Constraints (C300-C322, C430-C444, C468-C470)

**Scope:** Astronomical/Zodiac/Cosmological hybrid system - decision-point grammar and compatibility filter
**Status:** CLOSED (all sections)

---

## Classification (C300-C305)

### C300 - 3,299 Tokens Unclassified
**Tier:** 2 | **Status:** CLOSED
8.7% of corpus (3,299 tokens in 30 folios) never classified by Currier as A or B.
**Note:** Corrected 2026-01-15 from 9,401 (all transcribers) to 3,299 (H primary only).
**Source:** AZC

### C301 - AZC is HYBRID
→ See [C301_azc_hybrid.md](C301_azc_hybrid.md)

### C302 - Distinct Line Structure
**Tier:** 2 | **Status:** CLOSED
Median 8 tokens/line (vs A=22, B=31). TTR 0.285 (vs A=0.137, B=0.096).
**Source:** AZC

### C303 - Elevated LINK Density
**Tier:** 2 | **Status:** CLOSED
7.6% LINK density — higher than A (3.0%) and B (6.6%). Most wait-heavy text.
**Source:** AZC

### C304 - 27.4% Unique Vocabulary
**Tier:** 2 | **Status:** CLOSED
903 types absent from both A and B.
**Note:** Corrected 2026-01-15 from 1,529 (all transcribers) to 903 (H primary only).
**Source:** AZC

### C305 - LABELING Signature
**Tier:** 2 | **Status:** CLOSED
AZC-unique vocabulary: 98% section-exclusive, 37% line-initial, 37% line-final, 65.9% hapax. Function = LABELING.
**Source:** AZC-PROBE

---

## Placement Coding (C306-C312)

### C306 - Placement-Coding Axis
**Tier:** 2 | **Status:** CLOSED
Finite placement classes: C (17.1%), P (11.0%), R1-R3, S-S2, Y. Orthogonal to morphology.
**Source:** AZC-PLACEMENT

### C307 - Placement × Morphology Dependency
**Tier:** 2 | **Status:** CLOSED
Cramer's V = 0.18 (PREFIX), 0.17 (SUFFIX). Weak but present.
**Source:** AZC-AXIS

### C308 - Ordered Subscripts
**Tier:** 2 | **Status:** CLOSED
R1>R2>R3 and S>S1>S2 in component length (monotonic decrease). Ordinal position encoding.
**Source:** AZC-AXIS

### C309 - Grammar-Like Placement Transitions
**Tier:** 2 | **Status:** CLOSED
99 forbidden bigrams, self-transitions enriched 5-26x.
**Source:** AZC-AXIS

### C310 - Placement Constrains Repetition
**Tier:** 2 | **Status:** CLOSED
P, S-series allow higher repetition (2.7-3.0); R-series lower (2.1-2.4).
**Source:** AZC-AXIS

### C311 - Positional Grammar
**Tier:** 2 | **Status:** CLOSED
S1, S2, X = boundary specialists (85-90% line-edge). R1, R2, R3 = interior specialists (3-9% boundary).
**Source:** AZC-AXIS

### C312 - Section × Placement Strong
**Tier:** 2 | **Status:** CLOSED
Cramer's V = 0.631. Z, A, C sections have distinct placement profiles.
**Source:** AZC-AXIS

---

## Positional Legality (C313-C320)

### C313 - Position Constrains LEGALITY
**Tier:** 2 | **Status:** CLOSED
219 forbidden token-placement pairs (z=13). Position defines what's ALLOWED, not what's LIKELY (only 14% prediction gain).
**Source:** AZC-AXIS

### C314 - Global Illegality + Local Exceptions
**Tier:** 2 | **Status:** CLOSED
Default-deny with explicit permits, not role-based permissions.
**Source:** AZC-AXIS

### C315 - Placement-Locked Operators
**Tier:** 2 | **Status:** CLOSED
9/18 restricted operators appear in exactly ONE placement.
**Source:** AZC-AXIS

### C316 - Phase-Locked Binding
**Tier:** 2 | **Status:** CLOSED
32.3pp binding drop under rotation. Token-placement anchored to absolute position.
**Source:** AZC-AXIS

### C317 - Hybrid Architecture
**Tier:** 2 | **Status:** CLOSED
C placement is rotation-tolerant (9.8% drop). P/R/S are phase-locked (40-78% drop). Topological core with positional frame.
**Source:** AZC-AXIS

### C318 - Folio-Specific Profiles
**Tier:** 2 | **Status:** CLOSED
V=0.507 for folio × placement. Different diagrams have different layouts.
**Source:** AZC-AXIS

### C319 - Zodiac Template Reuse
**Tier:** 2 | **Status:** CLOSED
f71r-f73v share identical placement profile. Reusable templates.
**Source:** AZC-AXIS

### C320 - S2 < S1 Ordering
**Tier:** 2 | **Status:** CLOSED
S2 appears earlier than S1 (p<0.0001). S-series marks ordered positions.
**Source:** AZC-AXIS

---

## Cycle Discriminator (C321-C322)

### C321 - Zodiac Vocabulary Isolated
**Tier:** 2 | **Status:** CLOSED
Mean consecutive Jaccard = 0.076. Each zodiac diagram has independent vocabulary.
**Source:** AZC-AXIS

### C322 - Season-Gated Workflow
**Tier:** 2 | **Status:** CLOSED
Only 5/25 placements have full zodiac coverage. AZC encodes workflow states whose availability is seasonally constrained.
**Source:** AZC-AXIS

---

## Refinement Notes

### AZC-NOTE-01: qo-Prefix Depletion (refines C301/C313)

AZC exhibits significant depletion of `qo-` prefixed forms (~2.8x lower than Currier B: 6.5% vs 18.0%), consistent with AZC's placement-constrained legality reducing reliance on B-style escape routing.

**Evidence:** Analysis on `interlinear_full_words.txt` (2026-01-09)
- B: qo- = 18.0%
- A: qo- = 9.4%
- AZC: qo- = 6.5%

**Interpretation:** Diagram annotations use direct positional labeling rather than escape-route control flow.

---

---

## Imported Constraints

### C326 - A-reference sharing within clusters: 1.31x enrichment (p<0.000001); material conditioning is real but SOFT and OVERLAPPING (silhouette=0.018); NOT a clean taxonomy (SEL-F, Tier 2)
**Tier:** 2 | **Status:** CLOSED
A-reference sharing within clusters: 1.31x enrichment (p<0.000001); material conditioning is real but SOFT and OVERLAPPING (silhouette=0.018); NOT a clean taxonomy (SEL-F, Tier 2)
**Source:** v1.8-import

### C327 - Cluster 3 (f75-f84) is locally anomalous: only contiguous cluster, 70% STATE-C, highest A-ref coherence (0.294); LOCAL observation, not organizational law (SEL-F, Tier 2)
**Tier:** 2 | **Status:** CLOSED
Cluster 3 (f75-f84) is locally anomalous: only contiguous cluster, 70% STATE-C, highest A-ref coherence (0.294); LOCAL observation, not organizational law (SEL-F, Tier 2)
**Source:** v1.8-import

---

## Folio Family Architecture (C430-C435)

### C430 - AZC Bifurcation
**Tier:** 2 | **Status:** CLOSED
AZC divides into two architecturally distinct folio families with no transitional intermediates:
- **Family 0 (Zodiac-dominated):** placement-stratified, ordered-subscript regime (13 folios: all 12 Z + f57v)
- **Family 1 (A/C-dominated):** placement-flat regime without ordered subscripts (17 folios: 8 A + 6 C + 2 H + 1 S)

Bootstrap stability = 0.947. Silhouette = 0.34.
**Source:** AZC-DEEP Phase 3

### C431 - Zodiac Family Coherence
**Tier:** 2 | **Status:** CLOSED | **Refines:** C319
All Zodiac folios form a single, highly homogeneous AZC family (JS similarity = 0.964; bootstrap = 0.947), confirming Zodiac pages are a distinct structural mode, not merely reused templates.

Feature profile:
- TTR: 0.54 (vs 0.47 in Family 1)
- AZC-unique rate: 0.28 (vs 0.23)
- Placement entropy: 2.25 (vs 1.24)
- Ordered subscript depth: 0.96 (vs 0.00)
**Source:** AZC-DEEP Phase 3

### C432 - Ordered Subscript Exclusivity
**Tier:** 2 | **Status:** CLOSED
Ordered placement subscripts (R1-R3, S1-S2) occur exclusively in the Zodiac AZC family and are entirely absent from the placement-flat AZC family. This is a **binary diagnostic feature**.
**Source:** AZC-DEEP Phase 3

### C433 - Zodiac Block Grammar
**Tier:** 2 | **Status:** CLOSED
Zodiac placement codes occur in extended contiguous blocks (mean 40-80 tokens, max 156), never as isolated singletons. Self-transition rate exceeds 98% for all major codes:
- R1→R1: 99.9% (1022/1023)
- R2→R2: 99.9% (823/824)
- S1→S1: 100% (602/602)
- S2→S2: 100% (472/472)

This is **stricter than Currier B grammar**. Once a placement starts, it locks for dozens of tokens.
**Source:** AZC-DEEP Phase 4a

### C434 - R-Series Strict Forward Ordering
**Tier:** 2 | **Status:** CLOSED
R-subscript transitions are strictly forward: R1→R2→R3 only.
- Backward transitions (R2→R1, R3→R2): **FORBIDDEN** (0 observed, 349 expected)
- Skip transitions (R1→R3): **FORBIDDEN** (0 observed, 139 expected)

No exceptions. The R-series implements a one-way progression through interior stages.
**Source:** AZC-DEEP Phase 4a

### C435 - S/R Positional Division
**Tier:** 2 | **Status:** CLOSED
Zodiac placement grammar has a strict two-layer structure:
- **S-series (boundary layer):** 95%+ at line edges (S0=100% initial, S1=79% initial, S2=84% initial)
- **R-series (interior layer):** 89-95% line-interior positions

S marks entry/exit. R fills the interior in ordered stages. They never mix roles.
**Source:** AZC-DEEP Phase 4a

### C436 - AZC Dual Rigidity Pattern
**Tier:** 2 | **Status:** CLOSED
Both AZC families exhibit extreme intra-folio placement rigidity (>=98% self-transition, zero singleton placements), but differ sharply in cross-folio consistency:
- **Zodiac family:** Instantiates a single uniform placement scaffold (0.945 similarity)
- **A/C family:** Instantiates folio-specific rigid scaffolds (0.340 similarity)

The contrast is **uniform-versus-varied rigidity**, not rigid-versus-permissive structure. AZC is not "one mode with variation" - it implements two distinct coordination strategies.
**Source:** AZC-DEEP Phase 4b

---

## Threading and Compatibility (C437-C442)

### C437 - AZC Folios Maximally Orthogonal
**Tier:** 2 | **Status:** CLOSED
AZC folios have nearly independent vocabularies: mean Jaccard similarity = 0.056 (lower than C321's 0.076 for consecutive zodiac). Most similar pair = 0.176. Each folio defines a distinct vocabulary space.
**Source:** F-AZC-011

### C438 - AZC Practically Complete Basis
**Tier:** 2 | **Status:** CLOSED
AZC collectively covers 83.2% (mean) of A-types used by individual B procedures (range: 72.5%-94.3%). Aggregate coverage is 52.7%, but per-folio coverage shows practical completeness for common vocabulary.
**Source:** F-AZC-012

### C439 - Folio-Specific HT Profiles
**Tier:** 2 | **Status:** CLOSED
Different AZC folios have distinct HT profiles:
- Escape rate variance: 18.1pp (0% to 18.13%)
- Zodiac folios: 2.4% mean escape
- Non-Zodiac folios: 7.6% mean escape
- 17 distinct clusters at threshold=3.0pp

Folio identity correlates with constraint profile.
**Source:** F-AZC-013

### C440 - Uniform B-to-AZC Sourcing
**Tier:** 2 | **Status:** CLOSED
Every B procedure draws vocabulary from 34-36 AZC folios (essentially ALL). Range is only 2 folios. B procedures do NOT concentrate on specific AZC sources; they span the full constraint space.
**Source:** F-AZC-011

### C441 - Vocabulary-Activated Constraints
**Tier:** 2 | **Status:** CLOSED
AZC constraint activation is vocabulary-driven:
- Core vocabulary (appears in 20+ folios): broadly legal, averaged constraints
- Specialized vocabulary (appears in 1-3 folios): activates specific folio's constraint profile
- 478 A-types (49%) appear in exactly 1 AZC folio
- 28 A-types appear in 20+ AZC folios

The vocabulary used determines which constraints apply.
**Source:** F-AZC-011

### C442 - AZC Compatibility Filter
**Tier:** 2 | **Status:** CLOSED
AZC folios function as compatibility filters: specialized vocabulary from one folio cannot be combined with specialized vocabulary from another. The 94% unique vocabulary per folio (C437) creates mutual exclusion. Incompatible A-registry entries are grammatically blocked from co-occurring.
**Source:** F-AZC-011, azc_a_navigation analysis

---

## Phase-Indexed Escape (C443-C444)

### C443 - Positional Escape Gradient
**Tier:** 2 | **Status:** CLOSED
Escape rates vary systematically by AZC position for A-types:
- Position P (interior): 11.6% escape
- Position P2: 24.7% escape (highest)
- Position R1→R2→R3: 2.0%→1.2%→0% (decreasing)
- Position S1, S2: 0% escape

Interior positions permit intervention; boundary positions forbid it.
**Source:** azc_a_navigation analysis

### C444 - A-Type Position Distribution
**Tier:** 2 | **Status:** CLOSED
A-types distribute across ALL AZC positions (14-21 unique placements per high-frequency type). No A-type is locked to specific positions. The SAME material can appear in high-escape or zero-escape positions; position determines legality, not content.
**Source:** azc_a_navigation analysis

---

## Pipeline Causality (C468-C470)

### C468 - AZC Legality Inheritance
**Tier:** 2 | **Status:** CLOSED
AZC folio escape/constraint profiles propagate causally into Currier B recovery dynamics. Tokens from high-escape AZC contexts (>=5%) show 28.6% escape rate in B; tokens from low-escape AZC contexts (<5%) show 1.0% escape rate in B. This 28x difference confirms causal constraint transfer.
**Source:** F-AZC-016

### C469 - Categorical Resolution Principle
**Tier:** 2 | **Status:** CLOSED
Operational conditions (temperature, pressure, material state) are represented categorically via token legality, not parametrically via encoded values. Resolution lives in vocabulary availability: short MIDDLEs (len=1) appear in 18.4 folios on average; long MIDDLEs (len=5) appear in 1.2 folios. 73.5% of MIDDLEs appear in only 1 AZC folio.
**Source:** F-AZC-015, F-AZC-016, azc_middle_resolution analysis

### C470 - MIDDLE Restriction Inheritance
**Tier:** 2 | **Status:** CLOSED
MIDDLEs restricted to 1-2 AZC folios remain restricted when manifested in Currier B. Mean B folio spread: restricted MIDDLEs = 4.0 folios; universal MIDDLEs = 50.6 folios. This 12.7x difference confirms constraint transfer is preserved across the pipeline.
**Source:** F-AZC-016

---

## Morphological Binding (C471-C473)

### C471 - PREFIX Encodes AZC Family Affinity
**Tier:** 2 | **Status:** CLOSED
PREFIX families show statistically significant bias toward AZC folio families: qo- and ol- are strongly enriched in A/C AZC folios (91% / 81%), while ot- is enriched in Zodiac folios (54%). Other PREFIX families (ch-, sh-, ok-) are broadly distributed. This affinity shapes which class of legality postures are likely to be activated by vocabulary use but does not constitute exclusive mapping.
**Source:** Integration Probe 1 (prefix_azc_affinity.py)

### C472 - MIDDLE Is Primary Carrier of AZC Folio Specificity
**Tier:** 2 | **Status:** CLOSED
PREFIX-exclusive MIDDLEs (77% of all MIDDLEs) exhibit near-zero AZC entropy (median = 0.0), typically appearing in exactly one AZC folio. In contrast, shared MIDDLEs span multiple folios (mean coverage 18.7% vs 3.3%). Thus, MIDDLE is the principal determinant of folio-level compatibility constraints; PREFIX alone does not confer folio specificity.
**Source:** Integration Probe 2 (middle_azc_exclusivity.py)

### C473 - Currier A Entry Defines a Constraint Bundle
**Tier:** 2 | **Status:** CLOSED
A Currier A entry does not encode an addressable object or procedure. Its morphological composition (PREFIX + MIDDLE + SUFFIX) implicitly specifies a compatibility signature that determines which AZC legality envelopes are applicable. Through this mechanism, each A entry functions as a constraint bundle governing which operational contexts are valid.
**Source:** Integration Probes 1-3 combined

---

## Pipeline Resolution & Morphological Binding: CLOSED

The A -> AZC -> B control pipeline is structurally, behaviorally, and morphologically validated.

**What each layer IS (final definitions):**

- **Currier A record** = Pre-execution compatibility declaration. Specifies which operational contexts are legal through morphological composition. Does not select procedures, specify timing, or encode quantities.

- **AZC folio** = Complete legality regime. A bundled set of phase-indexed permissions and recoveries. Answers: which MIDDLE-level distinctions may be active together, at which phases intervention is legal, how forgiving mistakes are. Does not choose, interpret, or predict.

- **Currier B program** = Blind execution. Sees only grammar + legal/illegal tokens + recovery budget. Operator chooses vocabulary -> activates constraint bundle -> AZC filters legality -> B grammar runs blindly.

**Evidence:**
- F-AZC-015: AZC is ambient legality field (70% of folios active per window)
- F-AZC-016: Constraint profiles transfer causally to B (28x escape rate difference)
- C468-C470: Causal transfer locked
- C471-C473: Morphological binding mechanism discovered and locked

**The binding logic:**
- PREFIX -> AZC family affinity (qo/ol -> A/C, ot -> Zodiac)
- MIDDLE -> AZC folio specificity (77% exclusive, median entropy = 0.0)
- Together: each vocabulary item carries a "compatibility signature"

**Future work is exploratory only. Do NOT reopen:**
- Entry-level A->B mapping (ruled out by pipeline mechanics)
- Dynamic AZC decision-making (F-AZC-015 closed this: Case B confirmed)
- Parametric variable encoding (no evidence exists; C287-C290)
- Semantic token meaning (all evidence converges against)
- Naming or meaning of AZC folios (they are legality regimes, not semantic categories)
- Aligning A entries to specific B programs (relationship is vocabulary-mediated)

---

## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
