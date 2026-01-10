# AZC System Constraints (C300-C322, C430-C436)

**Scope:** Astronomical/Zodiac/Cosmological hybrid system
**Status:** CLOSED (core C300-C322), ACTIVE (C430+ family architecture)

---

## Classification (C300-C305)

### C300 - 9,401 Tokens Unclassified
**Tier:** 2 | **Status:** CLOSED
7.7% of corpus (9,401 tokens in 30 folios) never classified by Currier as A or B.
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

### C304 - 25.4% Unique Vocabulary
**Tier:** 2 | **Status:** CLOSED
1,529 types absent from both A and B.
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

## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
