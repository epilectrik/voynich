# Currier A Constraints (C224-C299, C345-C346, C420-C424, C475-C478)

**Scope:** Currier A disjunction, schema, multiplicity, morphology, positional, section boundary, DA articulation, vocabulary domains, MIDDLE compatibility, coverage, temporal trajectories
**Status:** CLOSED

---

## Disjunction (C224-C232)

### C224 - A Coverage = 13.6%
**Tier:** 2 | **Status:** CLOSED
49-class grammar achieves only 13.6% coverage on Currier A (threshold 70%). 66.8% novel vocabulary.
**Source:** CAud

### C225 - A Transition Validity = 2.1%
**Tier:** 2 | **Status:** CLOSED
Only 2.1% of A transitions match B grammar patterns.
**Source:** CAud

### C226 - A Has 5 Forbidden Violations
**Tier:** 2 | **Status:** CLOSED
Currier A contains 5 violations of B's forbidden transitions (B has 0).
**Source:** CAud

### C227 - A LINK Density = 3.0%
**Tier:** 2 | **Status:** CLOSED
A LINK density is 3.0% vs B's 6.6%.
**Source:** CAud

### C228 - A Density = 0.35x B
**Tier:** 2 | **Status:** CLOSED
Token density in A is 0.35x that of B.
**Source:** CAud

### C229 - A = DISJOINT
→ See [C229_currier_a_disjoint.md](C229_currier_a_disjoint.md)

### C230 - A Silhouette = 0.049
**Tier:** 2 | **Status:** CLOSED
Near-zero silhouette indicates no grammatical structure in A.
**Source:** CAud

### C231 - A is REGULAR but NOT GRAMMATICAL
**Tier:** 2 | **Status:** CLOSED
A shows statistical regularity without sequential grammar.
**Source:** CAud

### C232 - A Section-Conditioned but Class-Uniform
**Tier:** 2 | **Status:** CLOSED
Section affects A vocabulary but not grammatical class distribution.
**Source:** CAud

---

## Schema Properties (C233-C240)

### C233 - A = LINE_ATOMIC
**Tier:** 2 | **Status:** CLOSED
Median 3 tokens/line, MI=0 across lines. Each line is independent unit.
**Source:** CAS

### C234 - A = POSITION_FREE
**Tier:** 2 | **Status:** CLOSED
Zero JS divergence between positions. No positional grammar.
**Source:** CAS

### C235 - 8+ Mutually Exclusive Markers
**Tier:** 2 | **Status:** CLOSED
8 marker prefix families (ch, sh, ok, ot, da, qo, ol, ct) are mutually exclusive categorical tags.
**Source:** CAS

### C236 - A = FLAT
**Tier:** 2 | **Status:** CLOSED
Zero vocabulary overlap between markers. Not hierarchical.
**Source:** CAS

### C237 - A = DATABASE_LIKE
**Tier:** 2 | **Status:** CLOSED
TTR=0.137, 70.7% bigram reuse indicates registry/database structure.
**Source:** CAS

### C238 - Global Schema, Local Instantiation
**Tier:** 2 | **Status:** CLOSED
Single schema applies globally with section-specific instantiation.
**Source:** CAS

### C239 - A/B Separation = DESIGNED
**Tier:** 2 | **Status:** CLOSED
Only 25/112,733 cross-transitions (0.0%). Deliberate separation.
**Source:** CAS

### C240 - A = NON_SEQUENTIAL_CATEGORICAL_REGISTRY
→ See [C240_currier_a_registry.md](C240_currier_a_registry.md)

---

## Multiplicity Encoding (C250-C266)

### C250 - 64.1% Show Repetition
**Tier:** 2 | **Status:** CLOSED
64.1% (1013/1580) of entries exhibit `[BLOCK] × N` repetition structure.
**Source:** CAS-MULT

### C251 - Repetition is Intra-Record Only
**Tier:** 2 | **Status:** CLOSED
No aggregation or arithmetic across entries.
**Source:** CAS-MULT

### C252 - Repetition Bounded 2-6x
**Tier:** 2 | **Status:** CLOSED
Distribution: 2x=416, 3x=424, 4x=148, 5x=20, 6x=5. Mean=2.79x.
**Source:** CAS-MULT

### C253 - All Blocks Unique
**Tier:** 2 | **Status:** CLOSED
100% unique blocks (0% cross-entry reuse).
**Source:** CAS-MULT

### C255 - Blocks 100% Section-Exclusive
**Tier:** 2 | **Status:** CLOSED
Zero cross-section reuse of block content.
**Source:** CAS-DEEP

### C258 - 3x Dominance Reflects Human Counting
**Tier:** 2 | **Status:** CLOSED
3x dominance (55%) reflects human counting bias, bounded for usability.
**Source:** CAS-DEEP

### C261 - Token Order Non-Random
**Tier:** 2 | **Status:** CLOSED
Shuffling destroys blocks (4.2% survive). Original order meaningful.
**Source:** CAS-DEEP-V

### C262 - Low Mutation Across Repetitions
**Tier:** 2 | **Status:** CLOSED
7.7% variation. Blocks similar but not identical.
**Source:** CAS-DEEP-V

---

### C250.a - Block-Aligned Repetition (Refinement)
**Tier:** 2 | **Status:** CLOSED | **Source:** Exploration

Within Currier A entries exhibiting DA articulation, repetition applies to entire DA-segmented content blocks rather than partial segments.

**Evidence:**
- 58.7% of multi-block entries have exact block repetition
- 91.5% show high block similarity (J >= 0.5)
- Non-adjacent blocks MORE similar (0.836) than adjacent (0.775)

**Interpretation:** DA delineates enumerated sub-records rather than modifying repetition semantics. The `[BLOCK] × N` pattern from C250 operates on DA-segmented units. Non-adjacent similarity suggests interleaved enumeration: A-DA-A-DA-B-DA-B.

**Note:** This is a refinement clarifying C250's scope, not a new structural law.

---

## Compositional Morphology (C267-C282)

### C267 - Tokens are COMPOSITIONAL
→ See [C267_compositional_morphology.md](C267_compositional_morphology.md)

### C268 - 897 Combinations
**Tier:** 2 | **Status:** CLOSED
897 observed PREFIX × MIDDLE × SUFFIX combinations.
**Source:** CAS-MORPH

### C269 - 7 Universal Suffixes
**Tier:** 2 | **Status:** CLOSED
7 suffixes appear across 6+ prefixes. 3 universal middles.
**Source:** CAS-MORPH

### C272 - A and B on Different Folios
**Tier:** 2 | **Status:** CLOSED
0 shared folios between A (114) and B (83). Physical separation.
**Source:** CAS-PHYS

### C276 - MIDDLE is PREFIX-BOUND
**Tier:** 2 | **Status:** CLOSED
28 middles exclusive to single prefix (V=0.674). Type-specific refinement.
**Source:** EXT-8

### C277 - SUFFIX is UNIVERSAL
**Tier:** 2 | **Status:** CLOSED
22/25 significant suffixes appear in 6+ prefix classes.
**Source:** EXT-8

### C278 - Three-Axis Hierarchy
**Tier:** 2 | **Status:** CLOSED
PREFIX (family) → MIDDLE (type-specific) → SUFFIX (universal form).
**Source:** EXT-8

### C281 - Components SHARED
**Tier:** 2 | **Status:** CLOSED
All 8 prefixes, all 27 suffixes appear in BOTH A and B.
**Source:** EXT-8

---

## Folio Organization (C345-C346)

### C345 - No Folio-Level Thematic Coherence
**Tier:** 2 | **Status:** CLOSED
Within-folio similarity (J=0.018) equals between-folio (J=0.017). p=0.997.
**Source:** CAS-FOLIO

### C346 - Sequential Coherence Exists
**Tier:** 2 | **Status:** CLOSED
Adjacent entries share 1.31x more vocabulary (p<0.000001).
**Source:** CAS-FOLIO

**C346.a (Refinement):** The 1.31x adjacency similarity is driven primarily by shared MIDDLE components (1.23x) and suffixes (1.18x), with weak contribution from marker prefixes (1.15x). Local ordering reflects similarity in internal subtype/property components rather than shared marker class.
**Source:** Exploration

**C346.b (Refinement): Component-Level Adjacency Drivers**
Follow-up analysis using articulation-masked and component-isolated representations shows that Currier A's adjacency coherence is not driven by shared MIDDLE vocabulary alone.
**Source:** Exploration

**Findings:**
- Removing DA articulation tokens increases measured adjacency coherence (+18.4%), confirming DA suppresses similarity metrics
- MIDDLE-only adjacency similarity is lower than full-token similarity, indicating MIDDLE functions as a source of controlled variation within prefix-defined domains
- PREFIX and SUFFIX continuity contribute more strongly to local adjacency coherence than MIDDLE overlap
- DA-segmented blocks within a single entry show extremely high internal coherence (~26.8x), confirming DA articulates sub-units within a single descriptive record

**Interpretation:** Currier A adjacency reflects domain-level continuity with item-level variation, consistent with registry organization rather than semantic chaining.

---

## Clustered Adjacency (C424)

### C424 - Clustered Adjacency
**Tier:** 2 | **Status:** CLOSED
→ See [C424_clustered_adjacency.md](C424_clustered_adjacency.md)

Currier A adjacency coherence is non-uniform and clustered. While ~69% of adjacent entry pairs share no vocabulary overlap, the remaining ~31% form contiguous runs of vocabulary-sharing entries with mean length ~3 entries (range 2-20) and strong autocorrelation (r=0.80).

**Evidence:**
- Autocorrelation exceeds section-controlled null (z=5.85)
- Clustering persists across all similarity representations (0.64-0.82)
- 51% of clusters are size-3+ (not pair-dominated)

**Interpretation:** Currier A is a flat registry whose entries are sometimes arranged into local, contiguous groupings without introducing hierarchical structure, categorical headers, or reusable group boundaries.

**Relationship to C346:** C424 explains the *shape* of C346's 1.31x effect - the mean is driven by clustered minority, not uniform distribution.

**Refinements:**
- **C424.a** - Structural correlates: Clustered entries differ from singletons across multiple metrics (token count, MIDDLE count, block count, DA count) independently of entry length. 68% vocabulary divergence between populations.
- **C424.b** - Run-size threshold: Runs of size 5+ exhibit qualitatively stronger adjacency coherence (J=0.36 vs J=0.08 for size-2) without implying group identity.
- **C424.c** - Section P inversion: Section P singletons concentrate at top of pages (76.7% in lines 1-5); line-1 entries are shorter with 57.8% exclusive vocabulary. Descriptive pattern only.

---

## Section Boundary (C421)

### C421 - Section-Boundary Adjacency Suppression
**Tier:** 2 | **Status:** CLOSED
Adjacent entries crossing section boundaries exhibit 2.42x lower vocabulary overlap than same-section adjacent entries (J=0.0066 vs J=0.0160, p<0.001).
**Source:** Exploration

**Interpretation:** Section boundaries (H/P/T) are the primary hard discontinuities in Currier A's organization, overriding local topical continuity.

---

## DA Internal Articulation (C422)

### C422 - DA as Internal Articulation Punctuation
**Tier:** 2 | **Status:** CLOSED
The DA prefix family functions as a structural articulation marker within Currier A entries.
**Source:** Exploration

**Evidence:**
- 75.1% of internal DA occurrences separate adjacent runs of different marker prefixes (3:1 ratio over same-prefix continuation)
- All DA tokens (daiin and non-daiin variants) exhibit the same separation behavior (74.9% vs 75.4%)
- Entries containing DA are significantly longer (25.2 vs 16.4 tokens) and more prefix-diverse (3.57 vs 2.01 families)
- DA-segmented regions form prefix-coherent blocks, consistent with record subdivision

**Section gradient:** Separation rate varies by section (H=76.9%, P=71.7%, T=65.0%) but direction is invariant. DA always separates more than continues.

**Interpretation:** DA does not encode category identity. It marks internal sub-record boundaries within complex registry entries, functioning as punctuation rather than a classifier.

**MIDDLE coherence note:** DA-segmented sub-records do NOT exhibit increased MIDDLE similarity (adjacent J=0.037 vs random J=0.039). DA separates structure, not vocabulary content.

---

## Vocabulary Domains (C423)

### C423 - PREFIX-BOUND VOCABULARY DOMAINS
**Tier:** 2 | **Status:** CLOSED
In Currier A, the MIDDLE component constitutes the primary vocabulary layer, with prefixes defining domain-specific vocabularies.
**Source:** Exploration

**Evidence:**
- 1,184 distinct MIDDLEs identified (full census)
- 80% (947) are PREFIX-EXCLUSIVE
- 20% (237) are shared across prefixes
- 27 UNIVERSAL middles appear in 6+ prefixes
- Top 30 MIDDLEs account for 67.6% of usage

**PREFIX vocabulary sizes:**
| Prefix | Exclusive MIDDLEs |
|--------|-------------------|
| ch | 259 (largest) |
| qo | 191 |
| da | 135 |
| ct | 87 |
| sh | 85 |
| ok | 68 |
| ot | 55 |
| ol | 34 (smallest) |

**Interpretation:** Prefixes define domain-specific vocabularies from which MIDDLEs are selected. Shared and universal middles form a small cross-domain core, while most distinctions are domain-internal.

**Entropy:** MIDDLE entropy = 6.70 bits (65.6% of maximum). Efficient but not maximally compressed, consistent with human-usable registry design.

---

## MIDDLE Compatibility (C475)

### C475 - MIDDLE ATOMIC INCOMPATIBILITY
**Tier:** 2 | **Status:** CLOSED | **Source:** MIDDLE_INCOMPATIBILITY probe (2026-01-12)

MIDDLE-level compatibility is extremely sparse. Only 4.3% of MIDDLE pairs can legally co-occur on the same specification line; 95.7% are statistically illegal.

**Evidence (line-level co-occurrence in AZC folios):**
- 1,187 unique MIDDLEs observed
- 703,891 total possible pairs
- 30,394 legal pairs (4.3%)
- 673,342 illegal pairs (95.7%)
- 155 trivially absent (rare MIDDLEs)
- Null model: frequency-matched shuffle (1000 permutations)
- Robustness: 97.3% overlap with 2-line sensitivity check

**Graph structure:**
- 30 connected components (fragmented discrimination regimes)
- Largest component: 1,141 MIDDLEs (96% of vocabulary)
- 20 isolated MIDDLEs (work with nothing)
- Hub MIDDLEs: 'a', 'o', 'e', 'ee', 'eo' (universal connectors)

**PREFIX clustering (H1 - SUPPORTED):**
- Within-PREFIX legal: 17.39%
- Cross-PREFIX legal: 5.44%
- MIDDLEs within same PREFIX family are 3.2x more compatible

**Interpretation:**
> **The MIDDLE vocabulary forms a hard incompatibility lattice - a globally navigable but locally forbidden discrimination space.**

This is the atomic discrimination layer. Everything above it (A entries, AZC folios, families, HT) is an aggregation of this graph.

**Key structural objects identified:**
1. **Universal connector MIDDLEs** ('a', 'o', 'e', 'ee', 'eo'): Compatibility basis elements that bridge otherwise incompatible regimes
2. **Isolated MIDDLEs** (20 total): Hard decision points - "if you specify this, you cannot specify anything else"
3. **PREFIX as soft prior, MIDDLE as hard constraint**: PREFIX increases odds of legality ~3x, MIDDLE applies near-binary exclusions

**Reconciliation with prior constraints:**
- **Quantifies C293**: MIDDLE is primary discriminator → now proven as 95.7% exclusion rate
- **Explains C423**: PREFIX-bound vocabulary domains → PREFIX is first partition, MIDDLE is sharper second partition
- **Resolves AZC size paradox (C437-C442)**: AZC folios are projections of this massive sparse graph onto positional decision scaffolds
- **Grounds HT behavior (C459, C461)**: HT ≈ local incompatibility density + rarity pressure (now testable)

**f116v note:** f116v folio-level isolation (from azc_entry_bridges.py) is explained by data sparsity (only 2 words in corpus), NOT by MIDDLE-level incompatibility.

---

## Coverage Optimality (C476)

### C476 - COVERAGE OPTIMALITY
**Tier:** 2 | **Status:** CLOSED | **Source:** COVERAGE_OPTIMALITY probe (2026-01-12)

Currier A achieves GREEDY-OPTIMAL coverage (100%) while using 22.3% FEWER hub tokens than a greedy strategy would require.

**Evidence:**
- Real A: 100% coverage, 31.6% hub usage
- Greedy: 100% coverage, 53.9% hub usage
- Hub savings: 22.3 percentage points
- Random baseline: 72% coverage
- Frequency-matched baseline: 27% coverage

**Interpretation:**
> **Currier A is not meant to be generated. It is meant to be maintained.**

The four residuals (PREFIX coherence, tail forcing, repetition structure, hub rationing) are ONE control objective: COVERAGE CONTROL.

---

## Temporal Trajectories (C478)

### C478 - TEMPORAL COVERAGE SCHEDULING
**Tier:** 2 | **Status:** CLOSED | **Source:** TEMPORAL_TRAJECTORIES probe (2026-01-12)

Currier A exhibits STRONG TEMPORAL SCHEDULING with pedagogical pacing: introduce vocabulary early, reinforce throughout, cycle between prefix domains.

**Evidence (4 signals, 5/5 support strong scheduling):**

1. **Coverage BACK-LOADED:**
   - 90% coverage reached 9.6% later than random permutation
   - Real A delays full coverage despite front-loading novelty

2. **Novelty FRONT-LOADED:**
   - Phase 1: 21.2% novelty rate
   - Phase 2: 9.4% novelty rate (trough)
   - Phase 3: 11.3% novelty rate
   - New MIDDLEs introduced early, then reinforced

3. **U-SHAPED tail pressure:**
   - Phase 1: 7.9% rare MIDDLEs
   - Phase 2: 4.2% rare MIDDLEs (dip)
   - Phase 3: 7.1% rare MIDDLEs
   - Difficulty wave: start hard, ease, ramp up again

4. **PREFIX CYCLING:**
   - 7 prefixes cycle throughout manuscript (164 regime changes)
   - Prefix entropy increases then stabilizes
   - Multi-axis traversal of discrimination space

**Interpretation:**
> **PEDAGOGICAL_PACING: Currier A is not just coverage-optimal, it is temporally scheduled to introduce, reinforce, and cycle through discrimination domains.**

**Reconciliation with C476:**
- C476 shows WHAT Currier A optimizes (coverage with hub rationing)
- C478 shows HOW it achieves this (temporal scheduling, not static ordering)

---

## Positional Exception (C420)

### C420 - Folio-Initial Positional Exception
→ See [C420_folio_initial_exception.md](C420_folio_initial_exception.md)

**Summary:** First-token position in Currier A permits otherwise illegal C+vowel prefix variants (ko-, po-, to-) that are morphologically compatible but do not occur elsewhere.

**Key evidence:**
- 75% failure rate at position 1 vs 31% at position 2-3
- C+vowel prefixes: 47.9% at position 1, 0% at positions 2-3
- Fisher exact p < 0.0001
- ko- shares 100% suffix compatibility with ok-

**Interpretation:** Positional tolerance at codicological boundaries. Does NOT imply headers, markers, or semantic categories.

---

## Structural Exhaustion

**Status: CURRIER A IS STRUCTURALLY EXHAUSTED**

As of 2026-01-10, Currier A has reached its structural analysis limit. The C424 refinements (a, b, c) represent the final characterization possible without:

1. **Semantic interpretation** of vocabulary differences (not within scope)
2. **External referent mapping** (no grounding available)
3. **Ontological claims** about entry types (methodologically prohibited)

All observed patterns (vocabulary divergence, positional inversion, run-size effects) are **descriptively complete**. They constrain what ordering structures exist without explaining why they exist.

No further purely structural analyses are expected to yield new Currier A constraints.

---

## Exploratory Note: A-B Correlation (2026-01-10)

### Observation
Initial testing found weak correlation between clustered-A vocabulary and B hazard metrics (rho~0.22, p~0.04).

### Robustness Testing (ALL FAILED)
| Test | Result | Status |
|------|--------|--------|
| Permutation control | p=0.111 | FAILED |
| Frequency matching | p=0.056 | FAILED |
| **Pre-registered low-freq MIDDLE** | **p=0.651** | **FAIL** |

### Conclusion
The apparent A-B hazard correlation is **entirely driven by token frequency**. High-frequency vocabulary appears in both complex A entries (which cluster) and complex B programs (which are hazardous). When frequency is controlled, no residual correlation exists.

### Unified Interpretation: Complexity-Frontier Registry (CFR)

Currier A externalizes regions of a shared control-space where operational similarity breaks down and fine discrimination is required.

This can be described equivalently as:
- a *variant discrimination registry* (craft view), or
- a *partitioning of continuous control space* (formal view)

> **Currier A does not encode danger, procedures, materials, or outcomes.**
> **It encodes where distinctions become non-obvious in a global type system shared with executable control programs.**

- **Currier B** provides sequences (how to act)
- **Currier A** provides discrimination (where fine distinctions matter)
- **AZC** constrains availability
- **HT** supports the human operator

**The relationship between A and B is structural and statistical, not addressable or semantic.**

### CLOSED TESTS (DO NOT RE-RUN)

The following tests are closed. Any future correlation must exceed frequency-matched baselines to be considered new evidence:

- Hazard density correlation - CLOSED (frequency-explained)
- Forgiveness/brittleness discrimination - CLOSED (inseparable from complexity)

**No new constraint warranted.** This exploratory finding does not meet Tier-2 evidential standards but establishes the CFR interpretation as the strongest surviving model.

---

---

## Imported Constraints

### C241 - daiin A-enriched (1.55x), ol B-enriched (0.21x)
**Tier:** 2 | **Status:** CLOSED
daiin A-enriched (1.55x), ol B-enriched (0.21x)
**Source:** v1.8-import

### C242 - daiin neighborhood flip (content in A, grammar in B)
**Tier:** 2 | **Status:** CLOSED
daiin neighborhood flip (content in A, grammar in B)
**Source:** v1.8-import

### C243 - daiin-ol adjacent: 54 in B, 27 in A
**Tier:** 2 | **Status:** CLOSED
daiin-ol adjacent: 54 in B, 27 in A
**Source:** v1.8-import

### C244 - Infrastructure reuse without semantic transfer
**Tier:** 2 | **Status:** CLOSED
Infrastructure reuse without semantic transfer
**Source:** v1.8-import

### C245 - MINIMAL vocabulary: exactly 2 tokens (daiin, ol)
**Tier:** 2 | **Status:** CLOSED
MINIMAL vocabulary: exactly 2 tokens (daiin, ol)
**Source:** v1.8-import

### C246 - 4 mandatory criteria for structural primitives
**Tier:** 2 | **Status:** CLOSED
4 mandatory criteria for structural primitives
**Source:** v1.8-import

### C247 - SP-01 (daiin): affects 30.2% A, 16.5% B
**Tier:** 2 | **Status:** CLOSED
SP-01 (daiin): affects 30.2% A, 16.5% B
**Source:** v1.8-import

### C248 - SP-02 (ol): affects 7.4% A, 17.7% B
**Tier:** 2 | **Status:** CLOSED
SP-02 (ol): affects 7.4% A, 17.7% B
**Source:** v1.8-import

### C249 - Scan COMPLETE: 11 candidates tested
**Tier:** 2 | **Status:** CLOSED
Scan COMPLETE: 11 candidates tested
**Source:** v1.8-import

### C254 - Multiplicity does NOT interact with B; isolated from operational grammar
**Tier:** 2 | **Status:** CLOSED
Multiplicity does NOT interact with B; isolated from operational grammar
**Source:** v1.8-import

### C256 - Markers at block END 60.3% (vs 44% start); marker is trailing tag (CAS-DEEP)
**Tier:** 2 | **Status:** CLOSED
Markers at block END 60.3% (vs 44% start); marker is trailing tag (CAS-DEEP)
**Source:** v1.8-import

### C257 - 72.6% of tokens MARKER-EXCLUSIVE; markers define distinct vocabulary domains (CAS-DEEP)
**Tier:** 2 | **Status:** CLOSED
72.6% of tokens MARKER-EXCLUSIVE; markers define distinct vocabulary domains (CAS-DEEP)
**Source:** v1.8-import

### C259 - INVERSE COMPLEXITY: higher repetitions have MORE diverse blocks (rho=0.248) (CAS-DEEP)
**Tier:** 2 | **Status:** CLOSED
INVERSE COMPLEXITY: higher repetitions have MORE diverse blocks (rho=0.248) (CAS-DEEP)
**Source:** v1.8-import

### C260 - Section vocabulary overlap 9.7% (Jaccard); sections are isolated domains (CAS-DEEP)
**Tier:** 2 | **Status:** CLOSED
Section vocabulary overlap 9.7% (Jaccard); sections are isolated domains (CAS-DEEP)
**Source:** v1.8-import

### C263 - Section-specific ceilings: H max=5x, P max=5x, T max=6x (CAS-DEEP-V)
**Tier:** 2 | **Status:** CLOSED
Section-specific ceilings: H max=5x, P max=5x, T max=6x (CAS-DEEP-V)
**Source:** v1.8-import

### C264 - Inverse-complexity is BETWEEN-MARKER effect (Simpson's paradox); within-marker rho<0 for all 8 markers (CAS-DEEP-V)
**Tier:** 2 | **Status:** CLOSED
Inverse-complexity is BETWEEN-MARKER effect (Simpson's paradox); within-marker rho<0 for all 8 markers (CAS-DEEP-V)
**Source:** v1.8-import

### C265 - 1,123 unique marker tokens across 8 classes; 85 core tokens (freq>=10); `daiin` dominates DA (51.7%), `ol` dominates OL (32.3%) (CAS-CAT)
**Tier:** 2 | **Status:** CLOSED
1,123 unique marker tokens across 8 classes; 85 core tokens (freq>=10); `daiin` dominates DA (51.7%), `ol` dominates OL (32.3%) (CAS-CAT)
**Source:** v1.8-import

### C266 - Currier A has TWO content types: block entries (64.1%) have ONE marker class (exclusive); non-block entries (35.9%) mix MULTIPLE classes (90.5% have 2-8 classes) (CAS-SCAN)
**Tier:** 2 | **Status:** CLOSED
Currier A has TWO content types: block entries (64.1%) have ONE marker class (exclusive); non-block entries (35.9%) mix MULTIPLE classes (90.5% have 2-8 classes) (CAS-SCAN)
**Source:** v1.8-import

### C270 - Some middles are PREFIX-EXCLUSIVE (CT:-h-, DA:-i-, QO:-kch-); internal structure within classifier families (CAS-MORPH)
**Tier:** 2 | **Status:** CLOSED
Some middles are PREFIX-EXCLUSIVE (CT:-h-, DA:-i-, QO:-kch-); internal structure within classifier families (CAS-MORPH)
**Source:** v1.8-import

### C271 - Compositional structure explains low TTR (0.137) and high bigram reuse (70.7%); components combine predictably (CAS-MORPH)
**Tier:** 2 | **Status:** CLOSED
Compositional structure explains low TTR (0.137) and high bigram reuse (70.7%); components combine predictably (CAS-MORPH)
**Source:** v1.8-import

### C273 - Section specialization NON-UNIFORM: CT is 85.9% Section H vs OK/OL at 53-55%; at least one prefix is specialized to one product line (EXT-8)
**Tier:** 2 | **Status:** CLOSED
Section specialization NON-UNIFORM: CT is 85.9% Section H vs OK/OL at 53-55%; at least one prefix is specialized to one product line (EXT-8)
**Source:** v1.8-import

### C274 - Co-occurrence UNIFORM: no prefix pair shows strong association (>1.5x) or avoidance (<0.5x) in compounds; prefixes can combine freely (EXT-8)
**Tier:** 2 | **Status:** CLOSED
Co-occurrence UNIFORM: no prefix pair shows strong association (>1.5x) or avoidance (<0.5x) in compounds; prefixes can combine freely (EXT-8)
**Source:** v1.8-import

### C275 - Suffix-prefix interaction SIGNIFICANT (Chi2 p=2.69e-05): different prefixes have different suffix preferences; EXCLUDES prefixes being processing states (EXT-8)
**Tier:** 2 | **Status:** CLOSED
Suffix-prefix interaction SIGNIFICANT (Chi2 p=2.69e-05): different prefixes have different suffix preferences; EXCLUDES prefixes being processing states (EXT-8)
**Source:** v1.8-import

### C279 - STRONG cross-axis dependencies: all three pairwise interactions p < 10⁻³⁰⁰; axes are HIERARCHICALLY RELATED, not independent dimensions (EXT-8)
**Tier:** 2 | **Status:** CLOSED
STRONG cross-axis dependencies: all three pairwise interactions p < 10⁻³⁰⁰; axes are HIERARCHICALLY RELATED, not independent dimensions (EXT-8)
**Source:** v1.8-import

### C280 - Section P ANOMALY: suffix -eol is 59.7% Section P (only axis value favoring P); suggests P involves specific output form (EXT-8)
**Tier:** 2 | **Status:** CLOSED
Section P ANOMALY: suffix -eol is 59.7% Section P (only axis value favoring P); suggests P involves specific output form (EXT-8)
**Source:** v1.8-import

### C282 - Component ENRICHMENT: CT is A-enriched (0.14x), OL/QO are B-enriched (5x/4x); -dy suffix 27x B-enriched, -or 0.45x A-enriched; usage patterns differ dramatically (EXT-8)
**Tier:** 2 | **Status:** CLOSED
Component ENRICHMENT: CT is A-enriched (0.14x), OL/QO are B-enriched (5x/4x); -dy suffix 27x B-enriched, -or 0.45x A-enriched; usage patterns differ dramatically (EXT-8)
**Source:** v1.8-import

### C283 - Suffixes show CONTEXT PREFERENCE: -or (0.67x), -chy (0.61x), -chor (0.18x) A-enriched; -edy (191x!), -dy (4.6x), -ar (3.2x) B-enriched; -ol, -aiin BALANCED (EXT-9)
**Tier:** 2 | **Status:** CLOSED
Suffixes show CONTEXT PREFERENCE: -or (0.67x), -chy (0.61x), -chor (0.18x) A-enriched; -edy (191x!), -dy (4.6x), -ar (3.2x) B-enriched; -ol, -aiin BALANCED (EXT-9)
**Source:** v1.8-import

### C284 - CT in B is CONCENTRATED in specific folios (48 folios); when CT appears in B it uses B-suffixes (-edy, -dy); registry materials take operational form in procedures (EXT-9)
**Tier:** 2 | **Status:** CLOSED
CT in B is CONCENTRATED in specific folios (48 folios); when CT appears in B it uses B-suffixes (-edy, -dy); registry materials take operational form in procedures (EXT-9)
**Source:** v1.8-import

### C285 - 161 BALANCED tokens (0.5x-2x ratio) serve as shared vocabulary; DA-family dominates; cross-reference points between A and B (EXT-9)
**Tier:** 2 | **Status:** CLOSED
161 BALANCED tokens (0.5x-2x ratio) serve as shared vocabulary; DA-family dominates; cross-reference points between A and B (EXT-9)
**Source:** v1.8-import

### C286 - Modal preference is PREFIX x SUFFIX dependent; CT consistently A-enriched across suffixes, OL consistently B-enriched; not simple suffix-determines-context (EXT-9)
**Tier:** 2 | **Status:** CLOSED
Modal preference is PREFIX x SUFFIX dependent; CT consistently A-enriched across suffixes, OL consistently B-enriched; not simple suffix-determines-context (EXT-9)
**Source:** v1.8-import

### C287 - Repetition does NOT encode abstract quantity, proportion, or scale; remains LITERAL ENUMERATION without arithmetic semantics (EXT-9B RETRACTION)
**Tier:** 2 | **Status:** CLOSED
Repetition does NOT encode abstract quantity, proportion, or scale; remains LITERAL ENUMERATION without arithmetic semantics (EXT-9B RETRACTION)
**Source:** v1.8-import

### C288 - 3x dominance (55%) reflects human counting bias and registry ergonomics, NOT proportional tiers; no cross-entry comparison mechanism exists (EXT-9B RETRACTION)
**Tier:** 2 | **Status:** CLOSED
3x dominance (55%) reflects human counting bias and registry ergonomics, NOT proportional tiers; no cross-entry comparison mechanism exists (EXT-9B RETRACTION)
**Source:** v1.8-import

### C289 - Folio-level uniformity reflects ENUMERATION DEPTH PREFERENCE (scribal convention, category density), NOT batch scale; no reference frame for ratios (EXT-9B RETRACTION)
**Tier:** 2 | **Status:** CLOSED
Folio-level uniformity reflects ENUMERATION DEPTH PREFERENCE (scribal convention, category density), NOT batch scale; no reference frame for ratios (EXT-9B RETRACTION)
**Source:** v1.8-import

### C290 - Same composition with different counts confirms count is INSTANCE MULTIPLICITY, not magnitude; "3x here" is not comparable to "3x there" due to section isolation (EXT-9B RETRACTION)
**Tier:** 2 | **Status:** CLOSED
Same composition with different counts confirms count is INSTANCE MULTIPLICITY, not magnitude; "3x here" is not comparable to "3x there" due to section isolation (EXT-9B RETRACTION)
**Source:** v1.8-import

### C291 - ~20% of Currier A tokens have OPTIONAL ARTICULATOR forms (yk-, yt-, kch-, etc.); MORE section-concentrated than core prefixes; 100% removable without identity loss; systematic refinement layer, not noise (EXT-9B)
**Tier:** 2 | **Status:** CLOSED
~20% of Currier A tokens have OPTIONAL ARTICULATOR forms (yk-, yt-, kch-, etc.); MORE section-concentrated than core prefixes; 100% removable without identity loss; systematic refinement layer, not noise (EXT-9B)
**Source:** v1.8-import

### C292 - Articulators contribute ZERO unique identity distinctions; ablation creates 0 collisions; purely EXPRESSIVE, not discriminative (CAS-POST)
**Tier:** 2 | **Status:** CLOSED
Articulators contribute ZERO unique identity distinctions; ablation creates 0 collisions; purely EXPRESSIVE, not discriminative (CAS-POST)
**Source:** v1.8-import

### C293 - Component essentiality hierarchy: MIDDLE (402 distinctions) > SUFFIX (13) > ARTICULATOR (0); PREFIX provides foundation (1387 base); MIDDLE is primary discriminator (CAS-POST)
**Tier:** 2 | **Status:** CLOSED
Component essentiality hierarchy: MIDDLE (402 distinctions) > SUFFIX (13) > ARTICULATOR (0); PREFIX provides foundation (1387 base); MIDDLE is primary discriminator (CAS-POST)
**Source:** v1.8-import

### C294 - Articulator density INVERSELY correlates with prefix count (15% at 0-1 prefix to 4% at 6 prefixes); articulators COMPENSATE for low complexity (CAS-POST)
**Tier:** 2 | **Status:** CLOSED
Articulator density INVERSELY correlates with prefix count (15% at 0-1 prefix to 4% at 6 prefixes); articulators COMPENSATE for low complexity (CAS-POST)
**Source:** v1.8-import

### C295 - Sections exhibit DISTINCT configurations: H=dense mixed (87% mixed, 8.2% art), P=balanced (48% exclusive, 5.1% art), T=uniform sparse (81% uniform, 2.57x mean rep) (CAS-POST)
**Tier:** 2 | **Status:** CLOSED
Sections exhibit DISTINCT configurations: H=dense mixed (87% mixed, 8.2% art), P=balanced (48% exclusive, 5.1% art), T=uniform sparse (81% uniform, 2.57x mean rep) (CAS-POST)
**Source:** v1.8-import

### C296 - CH appears in nearly all common prefix pairs (CH+DA, CH+QO, CH+SH); functions as UNIVERSAL MIXING ANCHOR (CAS-POST)
**Tier:** 2 | **Status:** CLOSED
CH appears in nearly all common prefix pairs (CH+DA, CH+QO, CH+SH); functions as UNIVERSAL MIXING ANCHOR (CAS-POST)
**Source:** v1.8-import

### C297 - -eol is ONLY suffix concentrated in section P (55.9% vs 41.3% H); all other suffixes favor H; P has distinct suffix profile (CAS-POST)
**Tier:** 2 | **Status:** CLOSED
-eol is ONLY suffix concentrated in section P (55.9% vs 41.3% H); all other suffixes favor H; P has distinct suffix profile (CAS-POST)
**Source:** v1.8-import

### C298 - L-compound middle patterns (lch-, lk-, lsh-) function as B-specific grammatical operators; 30-135x more common in B, largely absent from A; grammar-level specialization not covered by shared component inventory (B-MORPH)
**Tier:** 2 | **Status:** CLOSED
L-compound middle patterns (lch-, lk-, lsh-) function as B-specific grammatical operators; 30-135x more common in B, largely absent from A; grammar-level specialization not covered by shared component inventory (B-MORPH)
**Source:** v1.8-import

### C299 - Section H vocabulary dominates B procedures (76/83 = 91.6%); Section P rare (7/83 = 8.4%); Section T absent (0/83 = 0%); chi² = 127.54, p < 0.0001; A sections have NON-UNIFORM mapping to B procedure applicability (CAS-XREF)
**Tier:** 2 | **Status:** CLOSED
Section H vocabulary dominates B procedures (76/83 = 91.6%); Section P rare (7/83 = 8.4%); Section T absent (0/83 = 0%); chi² = 127.54, p < 0.0001; A sections have NON-UNIFORM mapping to B procedure applicability (CAS-XREF)
**Source:** v1.8-import


## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
