# Currier A Constraints (C224-C299, C345-C346, C420-C424, C475-C478, C498-C525)

**Scope:** Currier A disjunction, schema, multiplicity, morphology, positional, section boundary, DA articulation, vocabulary domains, MIDDLE compatibility, coverage, temporal trajectories, suffix posture
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

### C250 - Block Repetition Pattern
**Tier:** 1 | **Status:** INVALIDATED
**Original claim:** 64.1% of entries exhibit `[BLOCK] × N` repetition structure.
**Correction (2026-01-15):** This was an artifact of loading all transcribers instead of H (primary) only. With H-only data: **0% block repetition**. The apparent repetition was caused by interleaved transcriber readings being misinterpreted as intentional repetition.
**Source:** CAS-MULT (invalidated by transcriber filter audit)

### C251 - Repetition is Intra-Record Only
**Tier:** 1 | **Status:** INVALIDATED
**Depends on:** C250 (invalidated)
**Source:** CAS-MULT

### C252 - Repetition Bounded 2-6x
**Tier:** 1 | **Status:** INVALIDATED
**Depends on:** C250 (invalidated)
**Source:** CAS-MULT

### C253 - All Blocks Unique
**Tier:** 1 | **Status:** INVALIDATED
**Depends on:** C250 (invalidated)
**Source:** CAS-MULT

### C255 - Blocks 100% Section-Exclusive
**Tier:** 1 | **Status:** INVALIDATED
**Depends on:** C250 (invalidated)
**Source:** CAS-DEEP

### C258 - 3x Dominance Reflects Human Counting
**Tier:** 1 | **Status:** INVALIDATED
**Depends on:** C250 (invalidated)
**Source:** CAS-DEEP

### C261 - Token Order Non-Random
**Tier:** 1 | **Status:** INVALIDATED
**Depends on:** C250 (invalidated)
**Source:** CAS-DEEP-V

### C262 - Low Mutation Across Repetitions
**Tier:** 1 | **Status:** INVALIDATED
**Depends on:** C250 (invalidated)
**Source:** CAS-DEEP-V

---

### C250.a - Block-Aligned Repetition (Refinement)
**Tier:** 1 | **Status:** INVALIDATED
**Depends on:** C250 (invalidated)
**Source:** Exploration

**Note:** All block repetition findings (C250-C262, C250.a) were artifacts of transcriber interleaving. With H-only data, no block repetition patterns exist.

---

## Compositional Morphology (C267-C282)

### C267 - Tokens are COMPOSITIONAL
→ See [C267_compositional_morphology.md](C267_compositional_morphology.md)

### C267.a - MIDDLE Sub-Component Structure
**Tier:** 2 | **Status:** CLOSED | **Scope:** GLOBAL | **Source:** MIDDLE_SUBCOMPONENT_ANALYSIS (2026-01-23)

MIDDLEs themselves have internal compositional structure. A vocabulary of **218 sub-components** reconstructs **97.8%** of all MIDDLEs.

**Evidence:**

| Metric | Value |
|--------|-------|
| Total unique MIDDLEs | 3,105 |
| Sub-component vocabulary | 218 (96 3-grams + 104 2-grams + 18 chars) |
| Reconstruction coverage | 97.8% fully covered |
| RI-D avg segments | 2.4 |
| PP avg segments | 1.3 |

**Top sub-components by MIDDLE coverage:**
- 'ch': 24.5% of MIDDLEs, 7.99× expected (vs null model)
- 'he': 16.7% of MIDDLEs
- 'ee': 15.4% of MIDDLEs
- 'sh': 11.6% of MIDDLEs
- 'ol': 9.0% of MIDDLEs

**Positional grammar within MIDDLEs:**
- START-preferring: 'qc' (100%), 'qe' (94%), 'op' (85%)
- END-preferring: 'eg' (94%), 'hh' (79%), 'as' (79%)

**Cross-category consistency:**
Sub-components are **global** (same components appear in RI, PP, and shared MIDDLEs):
- Jaccard ALL vs RI: 0.74
- Jaccard ALL vs PP: 0.33

**Interpretation:**
The morphological hierarchy extends deeper than PREFIX/MIDDLE/SUFFIX:

```
TOKEN = PREFIX + MIDDLE + SUFFIX
                   ↓
              MIDDLE = SUB1 + SUB2 + [SUB3...]
```

This explains why longer MIDDLEs are more likely to be unique (C498.d): more sub-components → more possible combinations → higher combinatorial uniqueness.

**Relationship to C267:**
This **extends** C267 (compositional morphology) to a finer granularity. MIDDLEs are not atomic - they are themselves compositional.

**Cross-references:** C267 (compositional morphology), C498.d (length-frequency correlation), C509.a (RI morphological divergence)

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

### C241 - daiin A-enriched (1.62x), ol B-enriched (0.24x)
**Tier:** 2 | **Status:** CLOSED
daiin A-enriched (1.62x), ol B-enriched (0.24x)
**Source:** v1.8-import

### C242 - daiin neighborhood flip (content in A, grammar in B)
**Tier:** 2 | **Status:** CLOSED
daiin neighborhood flip (content in A, grammar in B)
**Source:** v1.8-import

### C243 - daiin-ol adjacent: 16 in B, 10 in A
**Tier:** 2 | **Status:** CLOSED
daiin-ol adjacent: 16 in B, 10 in A
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

### C266 - Block vs Non-Block Entry Types
**Tier:** 1 | **Status:** INVALIDATED
**Original claim:** Currier A has TWO content types: block entries (64.1%) have ONE marker class; non-block entries (35.9%) mix MULTIPLE classes.
**Depends on:** C250 (invalidated)
**Source:** v1.8-import

### C270 - Some middles are PREFIX-EXCLUSIVE (CT:-h-, DA:-i-, QO:-kch-); internal structure within classifier families (CAS-MORPH)
**Tier:** 2 | **Status:** CLOSED
Some middles are PREFIX-EXCLUSIVE (CT:-h-, DA:-i-, QO:-kch-); internal structure within classifier families (CAS-MORPH)
**Source:** v1.8-import

### C271 - Compositional structure explains low TTR and bigram reuse
**Tier:** 2 | **Status:** CLOSED
Compositional structure explains low TTR (0.137) and bigram reuse (14.0%); components combine predictably.
**Note:** Bigram reuse corrected 2026-01-15 from 70.7% (all transcribers) to 14.0% (H-only).
**Source:** CAS-MORPH

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

**CORRECTION (2026-01-24):** Re-analysis shows -ol is 0.35x B/A (A-enriched), NOT balanced as originally claimed. The "balanced" classification for -ol is incorrect. -aiin status not yet re-verified.

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

**C298.a (Extension):** L-compound compositional structure and positional behavior.
- 75.9% of L-compound MIDDLEs contain energy operator roots (ch/sh/k)
- `l` is a grammatical modifier: lch = l + ch, lk = l + k, lsh = l + sh
- `l` modifier shifts position earlier in line: lch mean 0.344 vs ch 0.483 (delta -0.139)
- 97.0% B-exclusive tokens, 85.9% B-exclusive MIDDLEs (fully B-internal)
- Contrast with LATE prefixes (C539): LATE applies B-prefix to PP vocabulary; L-compound uses B-exclusive vocabulary
**Source:** LINE_BOUNDARY_OPERATORS phase (2026-01-25)

### C299 - Section H vocabulary dominates B procedures (76/83 = 91.6%); Section P rare (7/83 = 8.4%); Section T absent (0/83 = 0%); chi² = 127.54, p < 0.0001; A sections have NON-UNIFORM mapping to B procedure applicability (CAS-XREF)
**Tier:** 2 | **Status:** CLOSED
Section H vocabulary dominates B procedures (76/83 = 91.6%); Section P rare (7/83 = 8.4%); Section T absent (0/83 = 0%); chi² = 127.54, p < 0.0001; A sections have NON-UNIFORM mapping to B procedure applicability (CAS-XREF)
**Source:** v1.8-import

### C299.a - Section T Measurement Clarification
**Tier:** 2 | **Status:** CLOSED (Clarification)
C299 measures the presence of *section-characteristic* vocabulary (discriminators enriched or exclusive to a Currier A section), not raw vocabulary overlap. Section T shows 0% presence in Currier B because it contains no section-distinctive vocabulary, despite its constituent tokens appearing ubiquitously across B as infrastructure (67.7% of Section T MIDDLEs appear in B vs 42.4% baseline; 100% of B folios contain Section T vocabulary). Section T (f1r, f58r, f58v) functions as foundational/template content using only generic infrastructure vocabulary.
**Source:** A_SECTION_T_CHARACTERIZATION (2026-01-21)

---

## A-Exclusive Vocabulary Track (C498)

### C498 - Registry-Internal Vocabulary Track
**Tier:** 2 | **Status:** CLOSED | **REVISED 2026-01-24**

A-exclusive MIDDLEs (60.1%, 609 types) form a morphologically distinct registry-internal vocabulary track that does not propagate through the A→AZC→B pipeline.

**METHODOLOGY NOTE (2026-01-24):** Regenerated with atomic-suffix parser (voynich.py). Counts: 609 RI, 404 PP, 1,013 total A MIDDLEs.

**Evidence:**
- 609 MIDDLEs appear in Currier A but never in Currier B
- ct-prefix enrichment: 5.1× (vs shared MIDDLEs)
- Suffix-lessness: enriched (no decision archetype needed)
- Folio-localization: 1.28 folios (vs 8.64 for shared)
- AZC presence: 8.9% (vs 57.5% for shared) - residue is noise, not distinct stratum

**Morphological signature interpretation:**
- ct-prefix (C492): Only legal in P-zone AZC, 0% in C/S-zones → morphologically incompatible with most AZC positions
- Suffix-less: No downstream execution routing required → these MIDDLEs terminate in A
- Folio-localized: Hyper-specialized discriminators for local registry organization

**Two vocabulary tracks in Currier A:**

| Track | MIDDLEs | Characteristics | Role |
|-------|---------|-----------------|------|
| **Pipeline-participating (PP)** | 404 (39.9%) | Standard prefixes, standard suffixes, broad folio spread | Flow through A→AZC→B |
| **Registry-internal (RI)** | 609 (60.1%) | ct-enriched, suffix-less, folio-localized | Stay in A registry |

**Note:** Of the 404 PP MIDDLEs, ~86-90 are "functional PP" with strong B survival correlation (r=0.772). The rest are shared MIDDLEs without that predictive relationship.

**Interpretation:**
Registry-internal MIDDLEs encode **within-category fine distinctions** that matter for A-registry organization but don't propagate because they are below the granularity threshold for execution. They help an expert navigate A's complexity frontier (C240) without burdening B with irrelevant precision.

**Relationship to existing constraints:**
- Refines C293 (MIDDLE primary discriminator): Both tracks discriminate; scope differs
- Instantiates C476 (hub rationing): Registry-internal track IS hub-rationing in action
- Explains C475 (95.7% incompatibility): Cross-track incompatibility is part of the 95.7%
- Consistent with C383 (global type system): Same morphology, different usage pattern

**Falsified alternative:**
The "AZC-terminal bifurcation" hypothesis (that 8.9% of A-exclusive MIDDLEs form a distinct AZC-stranded stratum) was tested and failed verification:
- Only 77.6% in AZC-unique vocabulary (not strict subset)
- 75% appear in legality zones, not predominantly peripheral
- Classification inconsistent across transcribers

The 8.9% residue is interface noise from systems sharing the same alphabet, not a structural mechanism.

**Source:** A_INTERNAL_STRATIFICATION phase (2026-01-20)

**External Validation (2026-01-20):**
Brunschwig reference-only materials (listed but no procedure documented) correlate with registry-internal MIDDLE membership at the folio level:
- HIGH-REFERENCE product types: 35.6% registry-internal ratio
- LOW-REFERENCE product types: 30.3% registry-internal ratio
- Mann-Whitney U: z = -2.602, **p = 0.01**, effect size r = 0.248

This confirms that the two-track structure reflects real discrimination complexity stratification with an orthogonal historical signal. See F-BRU-005 (amended), BRUNSCHWIG_2TRACK_STRATIFICATION phase.

### C498.a - A∩B Shared Vocabulary Bifurcation (Tier 2 Refinement)
**Tier:** 2 | **Status:** CLOSED

The A∩B shared MIDDLE vocabulary (originally labeled "Pipeline-Participating") comprises two structurally distinct subclasses.

**REVISED 2026-01-24:** Regenerated with atomic-suffix parser (404 shared MIDDLEs):

| Subclass | Count | % of Shared | % of A | Mechanism |
|----------|-------|-------------|--------|-----------|
| **AZC-Mediated** | 235 | 58.2% | 23.2% | A→AZC→B constraint propagation |
| **B-Native Overlap (BN)** | 169 | 41.8% | 16.7% | B operational vocabulary with incidental A presence |

**Evidence (regenerated with atomic-suffix parser):**
- Traced all 404 A+B MIDDLEs through Currier A, AZC folios, and Currier B
- 169 MIDDLEs appear in A and B but **never** in any AZC folio
- Zero-AZC MIDDLEs show B-heavy frequency ratios (e.g., `eck` 41 B folios, 0 AZC; `tch` 23 B folios, 0 AZC)
- Pattern consistent with B-native origin, not A→B transmission

**AZC-Mediated substructure:**

| AZC Presence | Count | Mean B Folio Spread |
|--------------|-------|---------------------|
| Universal (10+ AZC folios) | 28 | 54.8 folios |
| Moderate (3-9 AZC folios) | 69 | 15.4 folios |
| Restricted (1-2 AZC folios) | 117 | 6.3 folios |

**B-Native Overlap characteristics:**
- Mean B folio spread: 3.5 folios (flat, AZC-independent)
- Examples with high B spread: `eck` (41 B folios), `tch` (23), `pch` (22), `ka` (20)
- Execution-infrastructure vocabulary: boundary discriminators, stabilizers, orthographic variants

**Architectural implications:**
- Constraint inheritance (C468-C470) applies only to AZC-Mediated subclass
- Pipeline scope is narrower than "all A∩B shared" implies
- A's outbound vocabulary to pipeline is a subset of 404 shared MIDDLEs (39.9% of A vocabulary)

**Relationship to existing constraints:**
- Consistent with C384 (No Token-Level A-B Lookup): BN MIDDLEs demonstrate statistical, not referential, sharing
- Consistent with C383 (Global Type System): Shared morphology ≠ shared function
- Refines C468-C470: Pipeline model preserved but now precisely scoped

**Terminology correction:**
The original "Pipeline-Participating" label is misleading. Recommended terminology:
- **AZC-Mediated Shared** (214): Genuine pipeline participation via AZC
- **B-Native Overlap / BN** (198): Domain overlap, not pipeline flow

**Complete A MIDDLE hierarchy (REGENERATED 2026-01-24 with atomic-suffix parser):**
```
A MIDDLEs (1,013 total)
+-- RI: Registry-Internal (609, 60.1%)
|     A-exclusive, instance discrimination, folio-localized
|     Only 7.0% of A token instances
|
+-- Shared with B (404, 39.9%)
    +-- AZC-Mediated (214, 19.8% of A)
    |     True pipeline participation: A->AZC->B
    |     +-- Universal (10+ AZC folios): 28
    |     +-- Moderate (3-9 AZC folios): 69
    |     +-- Restricted (1-2 AZC folios): 117
    |
    +-- B-Native Overlap (198, 18.4% of A)
          Zero AZC presence, B execution vocabulary
          Incidental A appearance, not pipeline flow
```
**Methodology note:** Previous hierarchy (617 total, 349 RI, 268 shared) used flawed extraction (PREFIX required, SUFFIX kept). Corrected 2026-01-24 with v2 extraction (PREFIX optional, SUFFIX stripped).

**Source:** A_RECORD_STRUCTURE_ANALYSIS phase (2026-01-20)
**External validation:** Reviewed by domain expert; confirmed as architecture-strengthening refinement that sharpens pipeline scope without contradiction.

### C498.b - RI Singleton Population (Structural)
**Tier:** 2 | **Status:** CLOSED | **Scope:** A | **Source:** RI_POPULATION_BIFURCATION (2026-01-23)

RI singletons are MIDDLEs that appear exactly once in Currier A. This is primarily a **structural observation**, not a functional classification.

**Structural evidence (Tier 2):**

| Metric | RI Singletons |
|--------|---------------|
| Population | ~977 types (75.7% of RI) |
| Frequency | **Exactly 1** |
| Mean MIDDLE length | 4.82 characters |
| Median length | 5 characters |

**Example tokens:**
- 'fachys' (f1r line 1), 'kodalchy', 'tydlo', 'fochof', 'polyshy'

**Functional interpretation (Tier 3, WEAKENED):**

> **IMPORTANT:** Singleton status is strongly correlated with MIDDLE length (see C498.d). The singleton/repeater distinction may be primarily a **combinatorial artifact** of sub-component composition (see C267.a), not a functional bifurcation.

Previous interpretations ("section markers", "unique discriminators") are **PROVISIONAL**. The structural fact is that these MIDDLEs appear once; the functional significance is uncertain.

**The folio-first subset (41 tokens):**
41 singletons (4.2%) appear at folio-first position. The 'fachys' pattern is real but represents a small subset, not the typical singleton.

**What singletons do NOT encode:**
- Semantic content (per C171, C384)
- Material identity (irrecoverable per semantic ceiling)
- Addressable references (per C384)

**Cross-references:** C498.d (length-frequency correlation), C267.a (sub-component structure), C509 (PP/RI separability)

### C498.c - RI Repeater Population (Structural)
**Tier:** 2 | **Status:** CLOSED | **Scope:** A | **Source:** RI_POPULATION_BIFURCATION (2026-01-23)

RI repeaters are MIDDLEs that appear multiple times in Currier A while remaining A-exclusive. This is primarily a **structural observation**, not a functional classification.

**Structural evidence (Tier 2):**

| Metric | RI Repeaters |
|--------|--------------|
| Population | ~313 types (24.3% of RI) |
| Frequency | 2-38 occurrences |
| Mean MIDDLE length | 3.61 characters |
| Median length | 4 characters |
| Cross-folio | 81.2% appear in multiple folios |

**Example tokens and frequencies:**
- 'sh': 38×, 'och': 29×, 'tsh': 26×, 'cfh': 19×, 'ko': 18×

**Critical distinction from PP:**
RI repeaters are structurally similar to PP (short, repeating) but are **A-exclusive**. This is NOT due to section isolation, positional restriction, or morphological incompatibility (all tested and falsified).

**Functional interpretation (Tier 3, WEAKENED):**

> **IMPORTANT:** Repeater status is strongly correlated with short MIDDLE length (see C498.d). Shorter MIDDLEs have fewer sub-component combinations (see C267.a), making repetition more likely by combinatorics alone.

Previous interpretations ("boundary scaffolding", "registry structure markers") are **PROVISIONAL**. The structural fact is that these short MIDDLEs repeat; the functional significance is uncertain.

**Independence finding (preserved):**
Singletons and repeaters are **statistically independent** within records:
- Co-occurrence ratio: 1.05× expected (near-random)
- Chi-square p-value: 0.165 (not significant)
- Records can have either, both, or neither

This independence is notable but does not prove functional distinction - it may reflect length-based distribution patterns.

**Cross-references:** C498.d (length-frequency correlation), C267.a (sub-component structure), C509 (PP/RI separability)

### C498.d - RI Length-Frequency Correlation
**Tier:** 2 | **Status:** CLOSED | **Scope:** A | **Source:** RI_COMPLEXITY_ANALYSIS (2026-01-23)

RI singleton/repeater status strongly correlates with MIDDLE length. This suggests the distinction is primarily **combinatorial**, not functional.

**Evidence:**

| Length | Types | Singleton Rate | Mean Frequency |
|--------|-------|----------------|----------------|
| 2 chars | 89 | 48% | 3.45 |
| 3 chars | 223 | 55% | 2.72 |
| 4 chars | 362 | 73% | 1.84 |
| 5 chars | 318 | 82% | 1.35 |
| 6 chars | 169 | 96% | 1.04 |
| 8+ chars | 53 | 100% | 1.00 |

**Statistical measures:**
- Spearman correlation: rho = **-0.367**, p < 10⁻⁴²
- Mean length singletons: 4.82 chars
- Mean length repeaters: 3.61 chars
- t-test: t = 13.20, p < 10⁻³⁷

**Interpretation:**
The smooth gradient from short/repeating to long/unique is consistent with **combinatorial effects** from sub-component morphology (C267.a):
- Short MIDDLEs (1-2 sub-components) → fewer combinations → more likely to repeat
- Long MIDDLEs (3-4 sub-components) → many combinations → more likely to be unique

**168 short singletons exist** (≤3 chars, unique), indicating the relationship is not deterministic. These may be rare character combinations or may serve specific functions.

**Implication for RI taxonomy:**
The singleton/repeater distinction (C498.b, C498.c) may reflect a **complexity gradient** rather than two functionally distinct populations. RI is better understood as a single A-exclusive vocabulary with length-dependent uniqueness.

**Revised MIDDLE taxonomy:**

```
All A MIDDLEs
├── PP (~90 types) ────────────► Shared with B (capacity)
│
└── RI (A-exclusive, ~1,290 types)
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

**Cross-references:** C267.a (sub-component structure), C498.b (singletons), C498.c (repeaters), C509.a (RI morphological divergence)

---

### C498-CHAR-A-CLOSURE - RI Closure Tokens (Tier 3 Characterization)
**Tier:** 3 | **Status:** CLOSED

A subset of registry-internal MIDDLEs functions as **record-terminal closure discriminators**. These tokens show strong line-final preference, a small reusable kernel, and a large singleton tail providing instance-specific separation.

**Evidence:**
- Line-final enrichment: 29.5% of RI tokens appear line-final (vs 16.8% expected)
- Opener/closer vocabulary disjointness: Jaccard = 0.072 (near-disjoint)
- Closer singleton rate: 87.4% (104 of 119 closer MIDDLEs used exactly once)
- Core kernel: ho (10x), hod (4x), hol (3x), mo (3x), oro (3x), tod (3x) — all -o/-od/-ol morphology
- Average closer uses: 1.24 per MIDDLE

**Relationship to C234 (POSITION_FREE):**
This is **ergonomic bias**, not grammar. RI closers prefer line-final position but can appear elsewhere and do not constrain what can follow. C234 remains intact.

**Relationship to C422 (DA Articulation):**
These are **complementary mechanisms** at different structural levels:

| Layer | Mechanism | Scope | Function |
|-------|-----------|-------|----------|
| Internal segmentation | DA articulation (C422) | Within a record | Sub-unit boundary punctuation |
| Record termination | RI closers | End of a record | Completion + instance discrimination |

If DA is a comma, RI closers are a period — but one that often needs to be unique, because what matters is not just that something ended, but that it ended as *this* and not anything else.

**Why Tier 3 (not Tier 2):**
This is a distributional regularity with explanatory coherence, not a structural necessity. Currier A would satisfy all structural contracts even if RI closers were less singleton-heavy or slightly less end-biased.

**Source:** A_RECORD_STRUCTURE_ANALYSIS phase (2026-01-20)

---

### C498-CHAR-A-SEGMENT - Hierarchical RI Closure at Segment Level (Tier 3 Characterization)
**Tier:** 3 | **Status:** CLOSED

RI closer preference operates **hierarchically** across structural levels:

| Scale | RI Closer Preference | P-value |
|-------|---------------------|---------|
| Line-final | 1.76× | < 0.001 |
| Segment-final | 1.43× | < 0.001 |
| Segment interior | 0.86× (depleted) | - |

**RI-RICH Segments (>30% RI, 6.1% of all segments):**
- Short: mean 3.3 tokens
- PREFIX-coherent: diversity 2.66 vs 3.44 for other segments (p < 0.0001)
- Terminal-preferring: 78.8% are "only" or "last" segments in their line
- Structurally distinct: 5× more common than binomial chance would predict

**Critical Finding:** PREFIX does NOT predict segment RI profile (p=0.151), even though PREFIX partially predicts token-level RI/PP (V=0.183). This means **RI concentration is a positional-closure phenomenon independent of PREFIX vocabulary**.

**Two Orthogonal Organizational Axes:**
1. **PREFIX families** — what domain/material-class is being discriminated
2. **RI closure bursts** — where fine-grained instance discrimination happens

RI-RICH segments are "closure units" that can involve any PREFIX family. The registry concentrates instance-specific discrimination at terminal positions regardless of content domain.

**Relationship to C422 (DA Articulation):**
C422 describes the mechanism — DA separates PREFIX family runs. This characterization describes what happens within that structure. Both are valid; they operate at different descriptive levels.

**Relationship to C234 (POSITION_FREE):**
This remains **distributional characterization**, not grammar. RI tokens CAN appear anywhere; they exhibit statistical preferences for closure positions without imposing grammatical constraints.

**Source:** A_RECORD_STRUCTURE_ANALYSIS phase, DA segmentation sub-phases 1-3 (2026-01-20)

---

## Material-Class Prior Recoverability (C499)

### C499 - Bounded Material-Class Recoverability
**Tier:** 3 | **Status:** CLOSED | **Conditional on:** Brunschwig interpretive frame

While entity-level identity remains irrecoverable (semantic ceiling), **material-class probability vectors** are computable for registry-internal MIDDLEs via Bayesian inference through procedural context.

**Inference chain:**
```
token → folio appearances → product type distribution → P(material_class | token)
```

**Results (128 MIDDLEs analyzed):**
- 18 tokens with P(animal) = 1.00 (PRECISION-exclusive)
- Mean entropy: 1.08 bits (range 0.00 - 2.62)
- Dominant class distribution: herb (49.2%), hot_dry_herb (25.8%), animal (21.1%), cold_moist_flower (3.9%)

**Validation (ANIMAL_PRECISION_CORRELATION phase, 2026-01-21):**
All 18 P(animal)=1.00 tokens are **A-exclusive** - they never appear in Currier B. This confirms:
1. These ARE registry vocabulary (not pipeline-participating)
2. The material-class inference methodology correctly identifies precision-requiring materials
3. Animal distillation materials are catalogued in A but don't propagate to B execution

**Null model validation (1000 permutations):**
- 86% of testable tokens match random baseline
- Confirms "prior-dominated probabilistic shadows"
- Entropy structure comes from folio distribution, not hidden semantic structure

**Claim boundary table:**

| Level | Status | Example |
|-------|--------|---------|
| Entity identity | IRRECOVERABLE | "This token means lavender" |
| Material class | **PARTIALLY RECOVERABLE** | "P(flower) = 0.57" |
| Procedural context | RECOVERABLE | "Gentle distillation contexts" |

**What this means:**
1. Entity-level identity remains irrecoverable - we cannot say "this token means lavender"
2. Class-level priors are computable - we CAN say "P(flower-class) = 0.57"
3. The distinction is epistemological, not ontological - the system MAY encode specific materials, we just can't recover which

**Relationship to existing constraints:**
- Extends C498 (registry-internal track): Adds material-class priors to the "what we can know" about registry-internal MIDDLEs
- Respects C384 (no token-level lookup): Analysis is aggregate/statistical, not token-level
- Validates semantic ceiling gradient: Different recoverability levels for different claim types

**Source:** BRUNSCHWIG_CANDIDATE_LABELING phase (2026-01-20)

---

## Suffix Posture Temporal Structure (C500)

### C500 - Registry-Internal Suffix Posture Temporal Pattern
**Tier:** 3 | **Status:** CLOSED

Registry-internal MIDDLEs exhibit a **temporal stratification by suffix posture**: closure-suffixed entries are introduced early (foundational framework), while naked (suffix-less) entries are introduced late (final coverage push).

**Evidence:**

| Posture | Mean Intro | Q1 Share | Q4 Share |
|---------|------------|----------|----------|
| CLOSURE (-y) | 0.18 | **76.7%** | 6.7% |
| NAKED | 0.53 | 25.9% | **37.9%** |
| EXECUTION | 0.02 | ~100% | 0% |

**Statistical significance:**
- S-3 (Temporal): Z = -4.648, **r = 0.495 (medium)**
- S-4 (Tail pressure): Phi = 0.333 (medium), ratio = **5.69×**

**Interpretation:**
- CLOSURE suffixes (-y): Foundational discrimination framework, front-loaded
- NAKED (suffix-less): Late refinement, edge-case discriminators added during final coverage push
- EXECUTION suffixes: Earliest routing layer (mean intro 0.017)

This **reverses** the initial hypothesis (that naked = atomic foundation). The registry establishes explicit closure/execution scaffolding first, then adds atomic discriminators as needed for edge cases.

**What this constrains:**
- Suffix posture reflects *when* a MIDDLE entered the registry, not *what it means*
- No semantic content recoverable from suffix posture
- Further tests on suffix function unlikely to yield additional granularity

**Null findings (no discrimination):**
- S-1 (HT density): r = 0.152 (small, not significant)
- S-2 (Incompatibility isolation): All MIDDLEs in same component

**Cross-references:** C498 (Two-Track), C383 (Global Morphological System)
**Source:** BRUNSCHWIG_CANDIDATE_LABELING Phase 4 (2026-01-20)

---

## Meta-Structural Artifacts (C497)

> **The existence of a single instructional/reference page demonstrates that Currier A was actively used and taught, not that it contains pedagogical grammar or semantic encoding.**

### C497 - f49v Instructional Apparatus Folio
**Tier:** 2 | **Status:** CLOSED

Folio f49v constitutes a distinct instructional/reference apparatus written in Currier A form but *not functioning as registry content*. It is characterized by:
- 26 single-character L-placement labels (≈65% of manuscript total), **alternating one-to-one with full Currier A lines**
- Rare marginal ordinal numbers (1–5) used meta-structurally
- Unusually high concentration of phonotactically extreme yet structurally valid Currier A tokens (33 exclusive vocabulary types)

The folio **demonstrates Currier A morphology and variation limits for human training or reference**. Its labels are **meta-structural**, do not participate in A-registry semantics, and do not propagate into AZC or B. This folio represents **instructional use of the Currier A system itself, not an extension of its grammar**.

No parametric, numerical, or semantic encoding is implied or propagated.

**Contrast with f76r (Currier B):** Folio f76r also contains single-character lines (`s d q s o l k r s`), but these are **control-posture sentinels** - grammatical markers that gate execution behavior (covered by C121, C366, C382, C403). f76r's letters **propagate into grammar**; f49v's labels **do not**. This contrast confirms f49v's uniqueness: it is the only folio where single-letters function meta-structurally rather than operationally.

**Cross-references:** C233 (LINE_ATOMIC), C484 (Channel Bifurcation), C469 (Categorical Resolution)
**Source:** f49v-INVESTIGATION (2026-01-20)

---

## B-Exclusive MIDDLE Stratification (C501)

### C501 - B-Exclusive MIDDLE Stratification
**Tier:** 2 | **Status:** CLOSED

The set of B-exclusive MIDDLEs (569 types, 68% of B vocabulary) does **not** represent a distinct semantic or discriminative layer. Empirically, B-exclusive MIDDLEs stratify into three functionally distinct strata:

**1. True Grammar Operators (Small, Concentrated)**
- L-compound MIDDLEs: `lk` (30), `lkee` (15), `lched` (4), etc.
- 49 types, 111 tokens total
- Line-initial biased (37-50%)
- Genuine B-specific control operators (cf. C298)

**2. Boundary Closers (Small, Structural)**
- `-edy` (67% line-final), `-dy`, `-eeed` forms
- Line-final biased
- Structural termination markers

**3. Singleton Cloud (Large, Non-Operational)**
- 457/569 (80.3%) are hapax legomena
- 65.9% are edit-distance-1 variants of shared MIDDLEs
- Edit types: 59% insertion, 39% substitution, 2% deletion
- Longer than shared MIDDLEs (mean 4.40 vs 3.03 chars)
- Do not participate in execution grammar

**Key finding:** B-exclusive status primarily reflects **positional and orthographic realization under execution constraints**, not novel discriminative content. The 65.9% edit-distance-1 rate demonstrates that most B-exclusive vocabulary is morphological elaboration of shared MIDDLEs at boundary positions.

**Architectural implication:** B does not maintain a separate "boundary vocabulary" - it uses elaborated versions of shared MIDDLEs at boundary positions. The extra character(s) encode boundary-specific disambiguation without creating genuinely new discriminators.

**Cross-references:** C298 (L-compound operators), C358 (boundary tokens), C271 (compositional morphology), C383 (global type system)
**Source:** B_EXCLUSIVE_MIDDLE_ORIGINS phase (2026-01-21)

---

## A-Record Viability Filtering (C502)

### C502 - A-Record Viability Filtering
**Tier:** 2 | **Status:** CLOSED | **Scope:** A+B | **Source:** MEMBER_COSURVIVAL_TEST (2026-01-22)

Under the strict survivor-set interpretation, A records create differential B folio viability through vocabulary restriction. Only MIDDLEs present in the A record itself are legal for B execution; AZC provides compatibility grouping and escape modulation but does NOT expand vocabulary.

**Evidence:**
- Mean B folio coverage per A record: 13.3%
- (A record, B folio) pairs with <10% coverage: 38.8%
- Atomic core (8 tokens with MIDDLE=None): Only 5% of B folio content on average
- 53.7% of B folios have <5% atomic content (non-viable if stripped to core)

**Quantitative findings:**
- A record specifies MIDDLEs → ~96 of 480 B tokens legal (20%)
- ~384 B tokens filtered out per A context (80%)
- Coverage ranges from 0.8% to 57.8% depending on (A record, B folio) pair
- Matches C481's "~128-dimensional discrimination space"

**Mechanism:**
- Different B folios have different MIDDLE compositions
- Low-coverage folios are functionally "crippled" (most instructions vanish)
- High-coverage folios are "viable" for execution under that A context
- Viability is emergent from vocabulary restriction, not intentional selection

**Architectural interpretation:**
- A→B relationship is vocabulary-mediated, not addressable (per C384)
- The A record doesn't "know" which B folios it enables
- C384.a permits conditional record-level correspondence via multi-axis constraint composition
- This finding quantifies that correspondence

**Contrast with union model (REJECTED):**
- Union model: Legal = union of MIDDLEs from matched AZC folios → ~463 survivors (96%)
- Strict model: Legal = A-record MIDDLEs only → ~96 survivors (20%)
- Union model contradicts C481 and produces trivial filtering; strict model validated

**Cross-references:** C384.a (permits conditional correspondence), C481 (survivor-set uniqueness), C475 (MIDDLE incompatibility), C469 (categorical resolution)

### C502.a - Full Morphological Filtering Cascade
**Tier:** 2 | **Status:** NEW | **Scope:** A+B | **Source:** GALLOWS_B_COMPATIBILITY (2026-01-24)

The A→B filtering mechanism operates through three cascading morphological layers. All three components (PREFIX, MIDDLE, SUFFIX) contribute independently to vocabulary restriction.

**Filtering cascade (per A record, against 4889 B tokens):**

| Filter | Legal Tokens | % of B | Additional Reduction |
|--------|-------------|--------|---------------------|
| MIDDLE only | 257.3 | 5.3% | — |
| MIDDLE + PREFIX | 92.4 | 1.9% | 64.1% |
| MIDDLE + SUFFIX | 129.9 | 2.7% | 49.5% |
| **Full morphology** | **38.5** | **0.8%** | **85.0%** |

**Statistical significance:** All reductions are significant (paired t-test, p≈0).

**Mechanism:**
- MIDDLE is the primary filter (C472): determines folio-level compatibility
- PREFIX adds AZC family affinity filtering (C471): 64% additional reduction
- SUFFIX adds regime breadth filtering (C495): 50% additional reduction
- Combined: 85% reduction beyond MIDDLE alone

**Key insight:**
For a B token to be legal under an A record, all three morphological components must be compatible:
```
B token legal iff:
  - token.MIDDLE in A-record.MIDDLEs (primary filter)
  - token.PREFIX in A-record.PREFIXes OR token has no PREFIX
  - token.SUFFIX in A-record.SUFFIXes OR token has no SUFFIX
```

**Revision to C502:**
The original C502 measured MIDDLE-only filtering against 480 token types (20% legal / 80% filtered). This finding extends C502 to full morphological filtering: **0.8% of B tokens legal per A record** (~38 tokens).

**Relationship to C473:**
This quantifies what C473 describes qualitatively: "morphological composition (PREFIX + MIDDLE + SUFFIX) implicitly specifies a compatibility signature." The 85% additional reduction demonstrates all three axes contribute meaningfully.

**Gallows domain effect (secondary finding):**
Within the MIDDLE-filtered set, same-gallows-domain A-B pairs have 1.07x stronger vocabulary overlap (p<0.0001). This is a weak preference gradient, not a routing mechanism.

**Cross-references:** C502 (A-record viability filtering), C472 (MIDDLE primary carrier), C471 (PREFIX AZC affinity), C495 (SUFFIX regime breadth), C473 (constraint bundle)

---

## Class-Level Filtering (C503)

### C503 - Class-Level Filtering Under Strict Model
**Tier:** 2 | **Status:** CLOSED | **Scope:** A+B | **Source:** CLASS_COSURVIVAL_TEST (2026-01-22)

Under strict interpretation (C502), class-level filtering is meaningful, not trivial.

**Key metrics:**
| Metric | Union (WRONG) | Strict (CORRECT) |
|--------|---------------|------------------|
| Unique class patterns | 5 | **1,203** |
| All-49-classes records | 98.4% | **0%** |
| Mean classes surviving | 49 | **32.3** |
| Range | 47-49 | **6-48** |

**Unfilterable core (6 classes) — MIDDLE-only filtering:**
| Class | Type | Reason |
|-------|------|--------|
| 7, 11 | ATOMIC | MIDDLEs 'ar', 'al', 'ol' highly common |
| 9 | CORE_CONTROL | MIDDLEs 'aiin', 'or', 'o' highly common |
| 21, 22, 41 | AUXILIARY | MIDDLEs 'y', 'o', 'l', 'r', 'e' highly common |

**⚠️ REVISION (C503.b):** Under full morphology (PREFIX+MIDDLE+SUFFIX), NONE of these classes are universal. See C503.b for details.

**Infrastructure class vulnerability:**
| Class | Survival Rate |
|-------|---------------|
| 36 | 20.9% |
| 42 | 25.9% |
| 44 | 13.1% |
| 46 | 27.3% |

**Interpretation:**
- No A record gives full access to all 49 classes
- 34% of classes filtered on average
- Infrastructure classes require specific vocabulary contexts
- Only 6 classes form the "minimum viable instruction set"

**Cross-references:** C502 (strict interpretation), C481 (discrimination space), C411 (reducibility)

### C503.a - Class Survival Under Full Morphological Filtering
**Tier:** 2 | **Status:** NEW | **Scope:** A+B | **Source:** GALLOWS_B_COMPATIBILITY (2026-01-24)

C503 documents class survival under MIDDLE-only filtering (32.3 mean, 66%). Full morphological filtering (PREFIX+MIDDLE+SUFFIX) dramatically reduces class survival.

**Comparison:**
| Filter | Mean Classes | % of 63 | Reduction from MIDDLE |
|--------|-------------|---------|----------------------|
| MIDDLE only | 41.5 | 65.9% | — |
| Full morphology | **6.8** | **10.8%** | **83.7%** |

**Note:** The test used 63 classes (prefix-based classification), not exactly C121's 49. The proportional reduction is the key finding.

**Surviving class patterns:**
- **Always survive (100%):** Classes with universal MIDDLEs ('a', 'o', 'y', 'l', 'r', 'e') AND no PREFIX/SUFFIX requirements
- **Never survive (0%):** Classes requiring rare PREFIX/SUFFIX combinations
- **Rarely survive (<10%):** Many infrastructure-adjacent classes

**Architectural implication:**
Each A record doesn't just filter vocabulary — it constrains B execution to a **tiny subset of instruction classes**. The ~7 surviving classes form the actual "instruction budget" per A context, not the ~32 classes suggested by MIDDLE-only analysis.

**Cross-references:** C503 (MIDDLE-only baseline), C502.a (token-level filtering cascade), C121 (49 instruction classes)

### C503.b - No Universal Classes Under Full Morphology
**Tier:** 2 | **Status:** NEW | **Scope:** A+B | **Source:** CLASS_COMPATIBILITY_ANALYSIS (2026-01-25)

C503 claimed 6 classes are "unfilterable" under MIDDLE-only filtering. Under full morphology (C502.a), **NONE of these classes are universal**.

**Verification using C121's original 49 classes:**
| Class | C503 Claim | Full Morph Coverage | Universal? |
|-------|------------|---------------------|------------|
| 7 (ar, al) | "Always pass" | **14.0%** | NO |
| 11 (ol) | "Always pass" | **36.3%** | NO |
| 9 (aiin, or, o) | "Universal MIDDLEs" | **56.1%** | NO |
| 21 | "Universal MIDDLEs" | **18.1%** | NO |
| 22 | "Universal MIDDLEs" | **10.3%** | NO |
| 41 | "Universal MIDDLEs" | **38.1%** | NO |

**Why C503's claim fails under full morphology:**
1. **Classes 7, 11, 9 have MIDDLEs** — contrary to C503's "MIDDLE=None" claim, these tokens DO have MIDDLE components (ar, al, ol, aiin, or, o)
2. **MIDDLE must appear in PP vocabulary** — under full filtering, even "common" MIDDLEs aren't present in all A records
3. **Classes 21, 22, 41 have PREFIX/SUFFIX requirements** — some tokens require PREFIX or SUFFIX matches that aren't always present

**Key finding:**
0 out of 49 C121 classes appear in ALL 1,559 A records under full morphology. Even Class 9 (the highest) only achieves 56.1% coverage.

**Reconciliation with C509.c:**
- C509.c found 0 universal classes using 63 PREFIX-based classes
- C503.b confirms 0 universal classes using C121's 49 classes
- **Conclusion:** No universal instruction classes exist under full morphological filtering, regardless of taxonomy

**Cross-references:** C503 (original claim), C503.a (class survival), C509.c (63-class verification), C502.a (filtering cascade)

### C503.c - Kernel Character Coverage (Corrected)
**Tier:** 2 | **Status:** NEW | **Scope:** A+B | **Source:** CLASS_COMPATIBILITY_ANALYSIS (2026-01-25)

The kernel primitives (k, h, e) are **characters within tokens**, not standalone tokens. Class 12 (`k` standalone) has 0 occurrences in B text — it's a structural artifact, not a real token.

**Kernel character coverage (tokens CONTAINING k, h, or e):**
| Character | In B Vocabulary | A Record Coverage |
|-----------|-----------------|-------------------|
| h | 54.0% of tokens | **95.6%** |
| k | 31.8% of tokens | **81.1%** |
| e | 49.5% of tokens | **60.8%** |

**Union coverage:**
| Metric | Records | % |
|--------|---------|---|
| At least one kernel char | 1,521 | **97.6%** |
| All three kernel chars | 813 | 52.1% |
| NO kernel chars | 38 | **2.4%** |

**The kernel is nearly universal.** 97.6% of A records have access to at least one token containing k, h, or e. Only 38 edge-case records (2.4%) lack kernel character access.

**Edge cases (38 records with no kernel access):**
- Most have very few surviving tokens (0-6)
- 11 records have NO surviving B tokens at all
- These are minimal morphological profiles (1-2 MIDDLEs, narrow PREFIX/SUFFIX)

**Token survival distribution:**
| Surviving Tokens | Records | % |
|------------------|---------|---|
| 0 | 11 | 0.7% |
| 1-9 | 140 | 9.0% |
| 10-49 | 1,001 | 64.2% |
| 50+ | 407 | 26.1% |

**Architectural implication:**
The kernel (k, h, e) IS effectively universal through containing tokens like `ok`, `ch`, `she`, `chey`. The 2.4% without kernel access are edge cases with minimal morphological profiles, not a systematic gap.

**Cross-references:** C503.b (no universal classes), C502.a (filtering cascade), C085 (10 single-character primitives), C089 (kernel k/h/e)

---

## MIDDLE Function Bifurcation (C504)

### C504 - MIDDLE Function Bifurcation in A Records
**Tier:** 2 | **Status:** CLOSED | **Scope:** A+B | **Source:** AUX_COOCCURRENCE analysis (2026-01-22)

A-record MIDDLEs bifurcate into two functionally distinct populations based on downstream propagation behavior.

**Vocabulary composition:**
| Type | Count | Mean/Record | Function |
|------|-------|-------------|----------|
| **PP** (Pipeline-Participating) | 86 types | 4.41 | Constrain B vocabulary legality |
| **RI** (Registry-Internal) | 1,293 types | 1.55 | Enable A-internal discrimination |

**Record composition (n=1,579):**
| Composition | Count | % |
|-------------|-------|---|
| BOTH PP + RI | 1,185 | 75.0% |
| PP only | 367 | 23.2% |
| RI only | 27 | 1.7% |

**Critical correlation:**
| Predictor | Correlation with B class survival |
|-----------|-----------------------------------|
| PP MIDDLE count | **r = 0.772** (strong positive) |
| RI MIDDLE count | r = -0.046 (none) |

**Interpretation:**
- PP MIDDLEs function as **compatibility carriers** - their presence/absence determines which B instruction classes survive under strict filtering (C502)
- RI MIDDLEs function as **A-internal discriminators** - they enable fine-grained registry navigation but do not propagate downstream
- RI-only records (1.7%) survive with only 6 B classes (the unfilterable atomic core)
- The 86 PP types form a categorical legality vocabulary, not a parametric encoding (per C469)

**What this does NOT claim:**
- RI MIDDLEs do not encode "material identity" in a recoverable sense
- PP MIDDLEs do not encode "material properties" as semantic attributes
- Specific material identification remains irrecoverable (per C171, MODEL_CONTEXT)

**Mechanism:**
The r=0.772 correlation quantifies C502's strict filtering: more PP MIDDLEs in an A record → more B vocabulary remains legal → more instruction classes survive. This is categorical availability, not parametric encoding.

**Cross-references:** C498 (two-track vocabulary), C498.a (AZC-Mediated bifurcation), C502 (strict filtering), C469 (categorical resolution), C171 (pure operational)

---

## PP Profile Differentiation (C505)

### C505 - PP Profile Differentiation by Material Class (A-Registry Organization)
**Tier:** 2 | **Status:** CLOSED | **Scope:** A | **Source:** PP_PERMUTATION_TEST (2026-01-23)

A records containing material-class-associated RI MIDDLEs exhibit statistically significant enrichment of specific PP MIDDLEs compared to baseline records.

**Critical scope limitation (PP_B_EXECUTION_TEST, 2026-01-23):** PP profile differences are **A-side organizational markers only**. They do NOT propagate to B execution — see C506.

**Animal (PRECISION) - 13 records:**

| PP MIDDLE | Animal Rate | Baseline Rate | Enrichment | p-value |
|-----------|-------------|---------------|------------|---------|
| 'te' | 15.4% | 0.9% | **15.8x** | 0.0060 |
| 'ho' | 23.1% | 2.8% | **8.7x** | 0.0030 |
| 'ke' | 30.8% | 5.9% | **5.1x** | 0.0030 |

Combined signature: p < 0.0001

**Water_Gentle - 12 records:**

| PP MIDDLE | Rate | Enrichment vs Baseline |
|-----------|------|------------------------|
| 'te' | 16.7% | **19.2x** |
| 'yt' | 16.7% | 4.0x |
| 'os' | 16.7% | 3.8x |
| 'eo' | 25.0% | 2.7x |

Note: 'te' shared with Animal (~16% in both). Permutation test Animal vs Water_Gentle: p > 0.05 (not significant with n=12-13).

**Oil_Resin - 56 records:**
- Weak discrimination, no strong signature PP
- Top PP: 'o' (61%), 'i' (34%), 'e' (29%)
- No PP shows >2.5x enrichment vs baseline

**Methodological validation (Dilution Test, 2026-01-23):**

PP profile detection requires **procedural grounding** via reverse trace methodology (B folio constraint → A record convergence). Taxonomic classification via Bayesian class posteriors produces diluted signal:

| Method | Records | 'te' Enrichment | 'ho' Enrichment | 'ke' Enrichment |
|--------|---------|-----------------|-----------------|-----------------|
| C505 RI MIDDLEs | 13 | **15.8x** | **8.7x** | **5.1x** |
| Bayesian posteriors | 40 | 5.1x | 3.8x | 2.5x |
| Bayesian-only (extra 27) | 27 | **0.0x** | 1.4x | 1.2x |

The 27 Bayesian-only records show baseline enrichment (0.9x mean), confirming they are false positives. PP discrimination requires procedurally-grounded record identification, not taxonomic inference.

**What this does NOT predict:**
- Fire degree (thermal tolerance) — tested and falsified (see falsifications.md)
- Taxonomic category via Bayesian posteriors — tested and failed

**Interpretation:**
PP MIDDLEs function as compatibility carriers (C504), and their composition varies systematically by material class. This does NOT mean:
- PP encodes "material identity" (that's RI's role)
- PP encodes specific "properties" as semantic attributes
- Animal materials can be identified via PP alone

It DOES mean:
- PP profiles correlate with processing-relevant material categories
- Different material classes require different operational affordances
- PP vocabulary composition is not uniform across A records
- Some PP MIDDLEs ('te') are shared across material classes with similar handling requirements

**Semantic ceiling (C171, C469):**
The correlation is structural, not semantic. We observe that animal-associated records have elevated 'te', 'ho', 'ke' without claiming these PP "mean" fire tolerance, organic complexity, or special preparation. The correlation with Brunschwig processing properties remains Tier 4 speculative.

**Cross-references:** C504 (MIDDLE function bifurcation), C498 (two-track vocabulary), C499 (bounded material-class recoverability), C171 (closed-loop only), C506 (non-propagation)

---

## PP Functional Role Closure (C506)

### C506 - PP Composition Non-Propagation
**Tier:** 2 | **Status:** CLOSED | **Scope:** A+B | **Source:** PP_B_EXECUTION_TEST (2026-01-23)

PP MIDDLE composition within A records does NOT predict B class survival or composition. PP functions as a **capacity variable** (count matters), not a **routing variable** (composition irrelevant).

**Evidence:**

| Test | Result | Interpretation |
|------|--------|----------------|
| Survival count (animal vs baseline) | p=0.448 (NS) | No differential filtering pressure |
| Class composition | Cosine=0.995, JS=0.0019 | Nearly identical profiles |
| Per-class Fisher's exact | 0/49 significant | No individual class differs |
| PP count correlation | r=0.715, p<10^-247 | COUNT strongly predicts survival |

**PP count gradient (confirming C504):**

| PP Count | Mean B Classes | n |
|----------|----------------|---|
| 0-2 | 19.0 | 171 |
| 3-5 | 30.9 | 805 |
| 6-8 | 37.2 | 525 |
| 9-11 | 41.4 | 64 |
| 12-15 | 43.9 | 13 |

**Architectural interpretation:**

PP MIDDLEs function as **generic compatibility carriers**:
- More PP = larger B survivable space (capacity)
- Specific PP composition = irrelevant to B output (no routing)
- PP profile differences (C505) = A-side registry organization

This resolves the apparent paradox: C505 shows strong material-class PP differentiation, yet B-side tests show null effects. PP profiles are "registry ergonomics" — ways of expressing A-side variation without affecting B execution.

**Variable taxonomy:**

| Variable | System | Function | Constraint |
|----------|--------|----------|------------|
| **Routing** | AZC | Position-indexed legality | C443, C468 |
| **Differentiation** | RI | Identity exclusion | C475, C481 |
| **Capacity** | PP | Arena width, enablement | C504, C506 |

**What this closes:**
- PP composition → B execution pathway: **FALSIFIED**
- PP as routing variable: **FALSIFIED**
- PP functional characterization: **COMPLETE** (at class level; see C506.a for token level)

**What remains open:**
- PP × HT × AZC three-way interaction
- Regime-specific HT compensation patterns

**Cross-references:** C504 (PP count correlation), C505 (A-side profiles), C171 (semantic ceiling), C469 (categorical resolution), C384 (no A-B lookup)

---

### C506.a - Intra-Class Token Configuration
**Tier:** 2 | **Status:** CLOSED | **Scope:** A+B | **Source:** PP_TOKEN_CONFIGURATION_TEST (2026-01-23)

PP composition determines **intra-class token configuration** even when class survival patterns are identical. This refines C506: PP composition doesn't affect *which classes* survive, but it does affect *which tokens within those classes* are available.

**Evidence:**

986 pairs of A records with identical class survival but different PP composition:

| Metric | Value |
|--------|-------|
| Mean token Jaccard | **0.953** |
| Median token Jaccard | 0.971 |
| Range | 0.545 - 1.000 |
| Perfect overlap (>0.99) | 34.6% |

Distribution of token overlap:
| Jaccard Range | Pairs | % |
|---------------|-------|---|
| 0.8-1.0 | 626 | 63.5% |
| 0.6-0.8 | 37 | 3.8% |
| 0.4-0.6 | 2 | 0.2% |

**Two-level PP effect:**

| Level | What PP Determines | Evidence |
|-------|-------------------|----------|
| **Class** | Which instruction types survive | COUNT matters (r=0.715), COMPOSITION doesn't (cosine=0.995) |
| **Token** | Which variants within classes are available | COMPOSITION matters (Jaccard=0.953 < 1.0) |

**Architectural interpretation:**

This resolves the "480 token paradox" — why maintain 480 distinct tokens across 49 classes if class survival is all that matters?

Answer: **Classes are instruction types; tokens are parameterized variants.**

- The 49 classes provide the operational grammar (what instructions exist)
- The ~480 tokens provide the parameter space (which variants of each instruction are available)
- PP COUNT determines class survival breadth (how many instruction types)
- PP COMPOSITION determines intra-class configuration (which variants of each type)

**Material-class implication:**

Animal materials don't need different *classes* than plant materials — they need different *parameterizations* of the same classes. C505's PP profile differences ('te', 'ho', 'ke' enrichment in animal records) shape which token variants are available, not which classes survive.

The shared class survival ensures the same operational grammar; the PP composition ensures material-appropriate token variants.

**Relationship to C506:**

C506 remains correct at its level: PP composition doesn't affect class survival patterns. C506.a adds the token-level refinement: PP composition shapes intra-class token availability (~5% variation).

**Cross-references:** C506 (class-level non-propagation), C505 (material-class PP profiles), C503 (class-level filtering), C121 (49 instruction classes)

---

### C506.a.i - PP Cross-Class Coordination Mechanism
**Tier:** 2 | **Status:** CLOSED | **Scope:** A+B | **Source:** PP_CROSS_CLASS_TEST (2026-01-23)

PP MIDDLEs select **coherent execution-variant slices across multiple classes simultaneously**, not independent per-class effects. This explains *how* PP composition acts (C506.a), not just *whether* it acts.

**Evidence:**

Analysis of 90 unique MIDDLEs in B instruction tokens:

| Finding | Value |
|---------|-------|
| MIDDLEs spanning single class | 39 (43%) |
| MIDDLEs spanning multiple classes | **51 (57%)** |
| Maximum class span | MIDDLE 'o' → 21 classes |
| Second highest | MIDDLE 'e' → 20 classes |
| Third highest | MIDDLE 'a' → 20 classes |

Within-class token overlap between different MIDDLEs:

| Metric | Value |
|--------|-------|
| Pairwise Jaccard | **0.000** |
| Exclusive tokens (1 MIDDLE only) | 100% |
| Shared tokens (2+ MIDDLEs) | 0% |

**Structural insight:**

MIDDLE is **orthogonal to CLASS**:
- CLASS determines grammatical role (what instruction type)
- MIDDLE determines variant selection (which parameterization)
- Token identity = (CLASS × MIDDLE) joint index

When a PP MIDDLE is active, it selects tokens across *all* classes where that MIDDLE exists - a coordinated slice through the grammar, not independent per-class draws.

**Mechanistic interpretation:**

> **PP MIDDLEs do not choose operations; they choose a coherent behavioral variant of all operations that remain legal - across the entire grammar.**

This explains why the ~5% PP composition effect (C506.a) is structured rather than random: changing PP MIDDLE changes token availability in a *coordinated* way across multiple functional domains.

**Material-specific implication:**

Real materials require coordinated tuning across:
- energy handling
- recovery handling
- phase sensitivity
- intervention tolerance

A cross-class MIDDLE slice provides exactly this - material-specific behavioral variation without semantic encoding. The system achieves **differentiation without naming**.

**Terminology clarification (binding):**

| Term | Definition | Reaches B? |
|------|------------|------------|
| **RI** | A-exclusive MIDDLEs | ❌ Never |
| **PP** | MIDDLEs shared between A and B | ✅ Yes |

RI and PP are **disjoint subsets** of MIDDLEs. Only PP has execution effects.

**What this does NOT claim:**
- ❌ PP "selects modes" (too semantic, violates C384/C171)
- ❌ MIDDLE encodes material identity (that's RI's role, which doesn't reach B)
- ❌ New functional layer discovered (mechanism refinement only)

**Cross-references:** C506.a (token configuration effect), C506.b (behavioral heterogeneity), C384 (no A-B lookup), C171 (semantic ceiling)

---

### C506.b - Intra-Class Behavioral Heterogeneity
**Tier:** 2 | **Status:** CLOSED | **Scope:** B | **Source:** INTRACLASS_HETEROGENEITY_TEST (2026-01-23)

Tokens within the same class but with different MIDDLEs are **positionally compatible but behaviorally distinct**. They occupy similar grammatical positions but lead to different transition patterns.

**Evidence:**

Compared token pairs within same class (n=1,334 pairs with sufficient data):

| Dimension | Same-MIDDLE | Different-MIDDLE | p-value |
|-----------|-------------|------------------|---------|
| Positional JS divergence | 0.240 | 0.256 | 0.11 (NS) |
| Transition JS divergence | 0.479 | **0.523** | **<0.0001** |

MIDDLE-level aggregation (n=262 MIDDLE pairs):

| Threshold | MIDDLE pairs exceeding |
|-----------|------------------------|
| JS > 0.2 | **100%** |
| JS > 0.3 | 96.9% |
| JS > 0.4 | **73.3%** |
| JS > 0.5 | 37.0% |

**Examples of maximum divergence:**

| Class | Token 1 | Token 2 | Transition JS |
|-------|---------|---------|---------------|
| 27 | aiir (MIDDLE=aii) | teey (MIDDLE=e) | 0.743 |
| 6 | tain (MIDDLE=i) | kair (MIDDLE=i) | 0.731 |
| 35 | choty (MIDDLE=ot) | shar (MIDDLE=a) | 0.730 |
| 25 | olor (MIDDLE=o) | olky (MIDDLE=k) | 0.721 |

**"Chop vs Grind" Pattern:**

This confirms the user's insight: tokens can be positionally compatible (both valid in the same grammatical slot) while being behaviorally distinct (leading to different continuations). Like "chop" and "grind" in a recipe:
- Both appear after "then" and before an ingredient (positionally compatible)
- But they lead to different subsequent operations (behaviorally distinct)

**Architectural interpretation:**

The 49 classes define **grammatical equivalence** (what can substitute without breaking syntax), not **semantic equivalence** (what does the same thing). Tokens within a class share grammatical role but have different:
- Transition probabilities (what follows)
- Execution implications (what happens next)

**Implication for PP composition:**

The ~5% token variation from C506.a (Jaccard=0.953) is **behaviorally meaningful**:

```
PP composition → MIDDLE selection → transition pattern variation
                                  → execution flow differences
                                  (within fixed class structure)
```

When different PP compositions select different MIDDLEs within the same surviving classes:
- Grammatical positions remain the same
- But execution flows diverge based on transition patterns

This is how material-specific PP profiles (C505) translate into material-appropriate execution variants without changing the class inventory.

**Cross-references:** C506.a (token-level configuration), C506 (class-level non-propagation), C121 (49 instruction classes), C505 (material-class PP profiles)

---

## PP-HT Responsibility Substitution (C507)

### C507 - Partial Responsibility Substitution between PP and HT
**Tier:** 2 | **Status:** CLOSED | **Scope:** A+HT | **Source:** PP_HT_INTERACTION_TEST (2026-01-23)

PP capacity is weakly but significantly inversely correlated with HT density. Records with higher PP counts exhibit reduced HT frequency but increased HT morphological diversity.

**Primary correlation:**

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Pearson r | -0.229 | Weak negative |
| Spearman rho | **-0.294** | Moderate negative |
| p-value | **0.0015** | Highly significant |
| n (folios) | 113 | Adequate sample |

**HT density gradient by PP bin:**

| PP Mean | HT Density | n |
|---------|------------|---|
| 0-3 | **18.83%** | 12 |
| 3-4 | 15.16% | 15 |
| 4-5 | 14.43% | 35 |
| 5-6 | 13.54% | 32 |
| 6+ | **12.62%** | 19 |

**Secondary finding (HT morphological diversity):**

| Correlation | r | p |
|-------------|---|---|
| PP mean vs HT TTR | **+0.40** | <0.001 |

Higher PP count correlates with *less* HT but *more varied* HT vocabulary.

**Interpretation:**
PP and HT partially substitute in a "responsibility budget":
- Higher PP capacity → reduced HT frequency (grammatical freedom substitutes for human vigilance)
- Higher PP capacity → increased HT morphological diversity (when HT occurs, it is more varied)

This is NOT:
- Complete substitution (r = -0.29, not -0.8)
- HT tracking PP content (composition doesn't matter per C506)
- Causal relationship (correlation only)

**Two-axis HT model:**
1. **HT density axis** — how much HT appears (negatively correlated with PP)
2. **HT diversity axis** — how varied HT is when it appears (positively correlated with PP)

These axes are semi-independent, creating a 2D space for HT characterization.

**System-level framing:**
This partial substitution suggests that A-record PP count (how much B vocabulary is available) modulates the *need* for human attention markers. More execution freedom → less vigilance required, but when vigilance is required, it engages a broader morphological repertoire.

**Currier system breakdown:**

| System | n | PP-HT r | p |
|--------|---|---------|---|
| Currier A folios | 48 | -0.18 | 0.22 |
| Currier B folios | 65 | -0.31 | 0.01 |

The effect is stronger in Currier B folios, consistent with PP's role as an execution enabler (C504, C506).

**Cross-references:** C504 (PP count correlation), C506 (PP composition non-propagation), C341 (HT-program stratification), C344 (HT-A inverse coupling), C459 (HT anticipatory compensation)

---

## Token-Level Discrimination (C508)

### C508 - Token-Level Discrimination Primacy
**Tier:** 2 | **Status:** CLOSED | **Scope:** A→B | **Source:** PROCESS_TYPE_TEST (2026-01-23)

Fine-grained discrimination in the A→B pipeline operates at the TOKEN/MEMBER level, not the CLASS level. Class-level analysis yields coarse, universal patterns; token-level analysis reveals the actual differentiation.

**Key findings:**

| Analysis Level | Jaccard Distance | Mutual Exclusion | Interpretation |
|----------------|------------------|------------------|----------------|
| CLASS | 0.391 | 0% | Universal, coarse |
| TOKEN | 0.700 | **27.5%** | Discriminative, fine-grained |

**Class-level patterns (coarse):**
- All 49 classes can co-occur (no mutual exclusion)
- A records differ in HOW MANY classes survive, not WHICH classes
- Class profiles show continuous variation, not distinct clusters
- Functional role ratios (TERMINATOR/OPERATOR/CORE) are uniform across A records

**Token-level patterns (discriminative):**
- 27.5% of within-class token pairs are mutually exclusive
- Different A records activate different tokens within the same classes
- Token-level Jaccard (0.700) is significantly higher than class-level (0.391)
- The "action" happens at member level, not class level

**Methodological implication:**

> **Future discriminating tests must focus on token/member level, not class level.**
> Class co-occurrence is NOT the key to fine-grained refinements.
> Classes define the universal grammar; tokens encode the specific execution variants.

**What this means for interpretation:**
- "Processing vs distillation" distinctions, if they exist, would appear at token level
- Different A records don't select different process TYPES (classes uniform)
- They select different execution VARIANTS (tokens differentiated)
- The 27.5% mutual exclusion suggests tokens are alternatives, not complements

**Architectural summary:**

```
CLASS LEVEL (Coarse, Universal):
- 49 classes define the grammar
- All classes can co-occur
- A records select SCOPE (how many), not TYPE (which ones)

TOKEN LEVEL (Fine, Discriminative):
- ~480 tokens provide execution variants
- 27.5% within-class mutual exclusion
- A records select SPECIFIC VARIANTS within classes
```

**Cross-references:** C506.b (intra-class behavioral heterogeneity), C503 (class-level filtering), C121 (49 instruction classes), C171 (unified control architecture)

### C508.a - Class-Level Discrimination Under Full Morphology (REVISION)
**Tier:** 2 | **Status:** NEW | **Scope:** A→B | **Source:** GALLOWS_B_COMPATIBILITY (2026-01-25)

**C508's claim "HOW MANY not WHICH" is REVISED under full morphological filtering.**

The original C508 tested MIDDLE-only filtering (~32 classes surviving). Under full morphology (PREFIX+MIDDLE+SUFFIX, ~7 classes surviving), class-level discrimination becomes significant.

**Comparison:**

| Metric | MIDDLE-only (C508) | Full Morphology |
|--------|-------------------|-----------------|
| Class Jaccard | 0.345 | **0.755** |
| Token Jaccard | 0.700 | **0.961** |
| Class mutual exclusion | 0.2% | **27.0%** |
| Token mutual exclusion | 27.5% | **69.0%** |

**Key finding:**
- Class Jaccard more than doubles (0.345 → 0.755)
- 27% of class pairs are mutually exclusive (vs 0% under MIDDLE-only)
- Both class AND token levels are now highly discriminative

**Revised architectural summary:**

```
MIDDLE-ONLY FILTERING (~32 classes):
- Class level: coarse, universal (Jaccard 0.345, 0% ME)
- Token level: discriminative (Jaccard 0.700, 27.5% ME)
- "HOW MANY, not WHICH" - VALID

FULL MORPHOLOGY FILTERING (~7 classes):
- Class level: ALSO discriminative (Jaccard 0.755, 27% ME)
- Token level: highly discriminative (Jaccard 0.961, 69% ME)
- "BOTH HOW MANY AND WHICH" - class selection matters
```

**Implications:**
- Under full morphology, A records select BOTH class types AND token variants
- The "universal grammar" is not uniformly accessible - different A contexts access different class subsets
- Token-level primacy still holds (token Jaccard > class Jaccard), but class-level is no longer "coarse"

**Interpretive note (per C509.d):**
The 27% class mutual exclusion is explained by morphological sparsity (PREFIX/SUFFIX/MIDDLE independence), not complex class interactions. Classes are grammar positions; mutual exclusion reflects vocabulary filtering, not functional incompatibility.

**Cross-references:** C508 (original MIDDLE-only finding), C503.a (class survival under full morphology), C502.a (filtering cascade), C509.d (independent morphological filtering)

---

## PP/RI Dimensional Separability (C509)

### C509 - PP/RI Dimensional Separability
**Tier:** 2 | **Status:** CLOSED | **Scope:** A | **Source:** RI_PP_SHARING_TEST (2026-01-23)

A records decompose into separable PP and RI MIDDLE components. The same PP set can combine with different RI sets, demonstrating dimensional independence.

**Key metrics:**

| Metric | Value |
|--------|-------|
| PP sets shared by records with different RI | **72** |
| Records sharing PP with RI-different records | **229 (14.5%)** |
| Pure-RI records (no PP, no B effect) | 26 (1.6%) |
| Pure-PP records (no RI) | 399 (25.3%) |
| Average RI MIDDLEs per record | 1.5 |
| Average PP MIDDLEs per record | 4.5 |

**Notable sharing patterns:**

| PP Set | Records Sharing | Distinct RI Patterns |
|--------|-----------------|----------------------|
| {} (empty) | 26 | 26 (all unique) |
| {i, o} | 14 | 12 |
| {o} | 11 | 10 |
| {e, o} | 7 | 7 |

**Interpretation:**

A records are structurally decomposable into two orthogonal dimensions:

| Dimension | Function | Propagates to B? |
|-----------|----------|------------------|
| **RI** | Discrimination coordinates (within-A navigation) | ❌ Never |
| **PP** | Capacity carriers (class survival breadth) | ✅ Yes |

This separation means:
- Same "capacity envelope" (PP) can apply to structurally distinct records (different RI)
- Pure-RI records (26) function as discrimination-only entries with no B-side effect
- Pure-PP records (399) carry only capacity information without RI-based discrimination
- The dimensions are independent, not coupled

**What this is NOT:**

- NOT "material identity" vs "processing parameters" (semantic interpretation)
- NOT parameterization of execution (C469 categorical resolution applies)
- NOT implying RI encodes referents (C171, C384 semantic ceiling applies)

**Structural implication:**

The A-record space has two independent axes:
1. **RI axis**: Exclusion/discrimination coordinates (high cardinality, A-internal)
2. **PP axis**: Capacity/enablement carriers (lower cardinality, B-facing)

Records occupy positions in this 2D space. The 72 shared PP sets demonstrate that these axes are genuinely separable, not coupled.

**Cross-references:** C504 (MIDDLE function bifurcation), C506 (PP non-propagation), C508 (token-level discrimination primacy), C498 (A-exclusive vocabulary track)

### C509.a - RI Morphological Divergence
**Tier:** 2 | **Status:** CLOSED | **Scope:** A | **Source:** RI_PP_MORPHOLOGY_TEST (2026-01-23) | **REVISED 2026-01-24**

RI tokens exhibit dramatically different morphological profiles than PP tokens, suggesting the morphological apparatus serves different structural roles in each population.

**METHODOLOGY NOTE (2026-01-24):** Original values used flawed extraction (PREFIX required, SUFFIX kept). Corrected extraction (PREFIX optional, SUFFIX stripped) gives different values. The PP MIDDLE length discrepancy (1.46 vs 3.22) suggests original "PP" was the ~86 functional PP atoms, not all 412 shared MIDDLEs.

**Statistical evidence (REVISED):**

| Metric | RI Tokens | PP Tokens | Original RI | Original PP |
|--------|-----------|-----------|-------------|-------------|
| Has PREFIX | **54.0%** | 79.8% | 58.5% | 85.4% |
| Mean MIDDLE length | **4.73** chars | 3.22 chars | 3.96 | 1.46 |

**Note:** PREFIX rates are close to original (validates methodology direction). MIDDLE length differences reflect different population definitions - original PP was likely the ~86 functional atoms with short MIDDLEs.

**Original evidence (retained for reference):**

| Metric | RI Tokens | PP Tokens | Significance |
|--------|-----------|-----------|--------------|
| Has PREFIX | **58.5%** | 85.4% | p < 10⁻¹⁸³ |
| Has SUFFIX | 71.6% | 78.1% | p < 10⁻¹¹ |
| Mean MIDDLE length | **3.96** chars | 1.46 chars | **2.7× longer** |
| Mean token length | **6.39** chars | 4.59 chars | 40% longer |
| Fully structured (P+S) | 40.6% | **67.9%** | -27pp |
| SUFFIX-only (no PREFIX) | **31.0%** | 10.2% | +21pp |

**SUFFIX enrichment in RI:**

| Suffix | RI Enrichment |
|--------|---------------|
| 'm' | **3.19×** |
| 'dy' | **2.27×** |
| 'al' | **2.15×** |
| 'y' | 1.39× |

**Morphological profile characterization (REVISED):**

| Aspect | PP Tokens | RI Tokens |
|--------|-----------|-----------|
| Template | Balanced (P+M+S) | **MIDDLE-centric** |
| PREFIX | Near-mandatory (80%) | Optional (54%) |
| MIDDLE | Shorter, shared vocabulary | **Longer (4.73 chars), unique identifiers** |
| SUFFIX | Standard distribution | Enriched for m, dy, al, y |
| Structure | Template-distributed | Discrimination-concentrated |

**Interpretation:**

The morphological apparatus is **structurally repurposed** between token populations:

- **PP tokens** use balanced PREFIX + short MIDDLE + SUFFIX template where PREFIX encodes control-flow participation (articulation domains per C422-C424)
- **RI tokens** concentrate discriminative information in the MIDDLE itself, with PREFIX serving as optional structural scaffolding rather than mandatory articulation

This explains why RI and PP are dimensionally separable (C509): they use different morphological strategies. PP tokens participate in a shared template system; RI tokens carry their discrimination in extended MIDDLEs.

**What this is NOT (Tier 3 ceiling):**

- NOT claiming PREFIX is "meaningless" in RI (it may serve structural scaffolding)
- NOT establishing causality direction (MIDDLE-centric because PREFIX optional, or vice versa)
- NOT phonetic interpretation (no phonetic evidence available)

**Cross-references:** C509 (PP/RI dimensional separability), C498 (A-exclusive vocabulary track), C267 (compositional tokens), C293 (component essentiality hierarchy), C383 (global morphological type system)

### C509.b - PREFIX-Class Determinism
**Tier:** 2 | **Status:** NEW | **Scope:** A→B | **Source:** CLASS_COMPATIBILITY_ANALYSIS (2026-01-25)

Under full morphological filtering, class availability is determined by PREFIX match with near-perfect determinism.

**Necessity (class → A-PREFIX): 100%**
For all PREFIX classes (P_xxx), having the class REQUIRES having the matching A-PREFIX. No exceptions.

**Sufficiency (A-PREFIX → class): 72-100%**
Having the A-PREFIX usually (but not always) yields the class. Failures occur when MIDDLE doesn't match any P_xxx token despite PREFIX match.

**Example evidence:**
| Class | Has class | Has A-PREFIX | Both | Sufficiency | Necessity |
|-------|-----------|--------------|------|-------------|-----------|
| P_sh | 733 | 733 | 733 | 100% | 100% |
| P_ch | 1101 | 1106 | 1101 | 99.5% | 100% |
| P_da | 732 | 745 | 732 | 98.3% | 100% |
| P_ct | 276 | 380 | 276 | 72.6% | 100% |

**Implication:**
The "27% class mutual exclusion" (C508.a) is not evidence of complex class interactions. It's simply PREFIX sparsity: A records typically have 2-3 PREFIXes, so they can only access 2-3 PREFIX classes.

**Cross-references:** C508.a (class discrimination contextualized), C503.a (class survival explained), C471 (PREFIX AZC affinity)

### C509.c - No Universal Instruction Set
**Tier:** 2 | **Status:** NEW | **Scope:** A→B | **Source:** CLASS_COMPATIBILITY_ANALYSIS (2026-01-25)

Under full morphological filtering, NO class appears in all A records.

**Class coverage:**
| Coverage | Classes |
|----------|---------|
| >95% | 1 (BARE at 96.8%) |
| >75% | 1 |
| >50% | 2 |
| <10% | 41 |

**Why even BARE isn't universal:**
- BARE tokens require no PREFIX (only MIDDLE match)
- 50 records (3.2%) lack ANY BARE-compatible MIDDLE
- These records have narrow morphological profiles (mean 2.4 PP MIDDLEs vs 6.0)

**The ~7 classes per record explained:**
- Mean ~2.5 PREFIXes → ~2.5 PREFIX classes
- BARE (96.8%) → +1 class usually
- Mean ~3-4 SUFFIX matches → variable SUFFIX classes
- Total: 6-8 classes (confirms C503.a mean of 6.8)

**Cross-references:** C503.a (class survival), C509.b (PREFIX determinism), C502.a (filtering cascade)

### C509.d - Independent Morphological Filtering
**Tier:** 2 | **Status:** NEW | **Scope:** A→B | **Source:** CLASS_COMPATIBILITY_ANALYSIS (2026-01-25)

The three morphological filters (PREFIX, MIDDLE, SUFFIX) operate independently under C502.a filtering. Class mutual exclusion is fully explained by morphological sparsity rather than class interaction.

**Evidence breakdown for 27% class mutual exclusion:**

| Exclusion Type | Mechanism | % |
|----------------|-----------|---|
| PREFIX vs PREFIX (54 pairs) | A-PREFIX absence | 100% |
| SUFFIX vs SUFFIX (32 pairs) | A-SUFFIX absence | 41% |
| SUFFIX vs SUFFIX | No MIDDLE overlap | 31% |
| SUFFIX vs SUFFIX | PP sparsity at record level | 28% |

**Key structural finding:**
SUFFIX classes are **100% PREFIX-free**. All tokens in S_xxx classes have no PREFIX, forming a morphologically distinct subspace.

**Filtering model:**
```
PREFIX class P_xxx: Requires A-PREFIX 'xxx' + matching MIDDLE in PP
BARE class:         Requires matching MIDDLE in PP only
SUFFIX class S_yyy: Requires A-SUFFIX 'yyy' + matching MIDDLE in PP
                    (all S_yyy tokens are unprefixed)
```

**Implication for C508.a:**
The 27% class mutual exclusion documented in C508.a is explained by morphological sparsity (PREFIX/SUFFIX/MIDDLE independence), not complex class interactions. Classes are grammar positions; mutual exclusion reflects vocabulary filtering, not functional incompatibility.

**Cross-references:** C508.a (class discrimination contextualized), C509.b (PREFIX determinism), C509.c (no universal set), C502.a (filtering cascade), C471 (PREFIX AZC affinity), C472 (MIDDLE primary), C495 (SUFFIX regime breadth)

---

## MIDDLE Sub-Component Grammar (C510-C518)

The MIDDLE vocabulary exhibits internal compositional structure with systematic construction rules. These constraints extend C267.a (sub-component structure) by revealing the generative mechanisms.

### C510 - Positional Sub-Component Grammar
**Tier:** 2 | **Status:** CLOSED | **Scope:** A | **Source:** MIDDLE_SUBCOMPONENT_GRAMMAR (2026-01-23)

MIDDLE sub-components show significant positional preferences (z=34.16, p<0.0001 vs permuted baseline).

**Position class distribution (187 qualified components, ≥10 occurrences):**

| Class | Count | % | Top Examples |
|-------|-------|---|--------------|
| START-class (>70% initial) | 62 | 33.2% | opa, qe, of, dk |
| END-class (>70% final) | 14 | 7.5% | ch, d, e, g, h, s |
| MIDDLE-class (>70% medial) | 1 | 0.5% | qo |
| FREE-class (no preference) | 110 | 58.8% | o, he, ee, al |

**Interpretation:**
The grammar is PERMISSIVE - 58.8% of components can appear at any position. Position constraints exist (highly significant vs random) but do not form a strict slot-based grammar. This enables productive composition while maintaining boundary constraints.

**Cross-references:** C267.a (sub-component structure), C512.a (positional asymmetry)

### C511 - Derivational Productivity
**Tier:** 2 | **Status:** CLOSED | **Scope:** A | **Source:** MIDDLE_SUBCOMPONENT_GRAMMAR (2026-01-23)

Repeater MIDDLEs (short, frequent forms) seed singleton MIDDLEs (long, unique forms) at **12.67x above chance baseline**.

**Evidence:**
- 324 repeaters seed singletons
- Mean productivity ratio: 12.67x expected
- Median productivity ratio: 5.86x expected
- 89.8% of seeding relationships exceed chance levels
- Correlation: frequency vs productivity rho = 0.211, p = 0.0009

**Mechanism:** Short frequent forms are productively extended into longer unique forms. This provides the causal mechanism for C498.d: length predicts uniqueness because short forms are derivational bases.

**Cross-references:** C498.d (length-frequency correlation), C267.a (sub-component structure)

### C512 - PP/RI Stylistic Bifurcation
**Tier:** 2 | **Status:** REVISED | **Scope:** GLOBAL | **Source:** MIDDLE_SUBCOMPONENT_GRAMMAR (2026-01-23), PP_RI_RETEST (2026-01-24)

PP and RI MIDDLEs exhibit high substring overlap, but this is **statistically expected** given length distributions and limited alphabet. The functional distinction (PP participates in B pipeline, RI stays in A) remains structural; the compositional relationship is likely **stylistic**, not derivational.

**Quantitative Evidence (unchanged):**

| Metric | Value |
|--------|-------|
| PP MIDDLEs that are sub-components | 72.2% (65/90) |
| RI MIDDLEs containing PP as substring | 100% (609/609) |
| PP section-invariance (avg Jaccard H/P/T) | 0.729 |
| RI section-invariance (avg Jaccard H/P/T) | 0.088 |
| Invariance ratio | 8.3x |
| PP in ALL sections | 60.7% |
| RI in ALL sections | 2.6% |

**Null Model Findings (2026-01-24):**

| Test | Result |
|------|--------|
| Random 404-element MIDDLE sets | 100% containment (vocabulary saturated) |
| Length-matched random null | 99.0% containment |
| Real PP containment | 100% |
| Z-score vs length-matched null | **1.08** (not significant, threshold 3.0) |

**Structural Style Differences:**

| Feature | RI | PP |
|---------|----|----|
| Mean MIDDLE length | 4.56 chars | 3.11 chars |
| Complex digraphs ('ch','sh','cph') | Over-represented (2-3x) | Baseline |
| 'h'-initial MIDDLEs | 92% RI | 8% PP |
| 'e' glyph frequency | 11.9% | 16.4% |

**Revised Interpretation:**
The substring containment pattern is **not statistically significant** vs length-matched random baseline. The PP/RI distinction likely reflects **stylistic elaboration** rather than compositional derivation:
- PP = simpler, shorter MIDDLEs that B grammar accepts
- RI = more elaborate MIDDLEs (complex digraphs, longer cores) that only A uses
- The substring relationship is coincidental character overlap from limited alphabet

**What remains valid:**
- PP provides cross-section vocabulary (section-invariance 8.3x higher)
- RI provides section-specific discrimination (folio-localized)
- Only PP survives A→B pipeline (C384, C506 unchanged)

**What is now PROVISIONAL:**
- "Compositional derivation" interpretation (PP as atoms building RI)
- RI = PP₁ ∩ PP₂ ∩ ... formulation (see C516)

**Cross-references:** C267.a (sub-component structure), C509 (PP/RI separability), C504 (PP count correlation), C516 (multi-atom - REVISED)

### C512.a - Positional Asymmetry
**Tier:** 2 | **Status:** CLOSED | **Scope:** A | **Source:** MIDDLE_SUBCOMPONENT_GRAMMAR (2026-01-23)

PP atoms and non-PP sub-components occupy different positional niches.

**PP rate by position class:**

| Position Class | PP Rate | Interpretation |
|----------------|---------|----------------|
| END-class | 71.4% | PP atoms dominate terminators |
| FREE-class | 40.9% | PP atoms flexible in core |
| START-class | 16.1% | RI elaborations dominate initiation |

**PP terminators (END-class):** `ch`, `d`, `e`, `eos`, `ees`, `g`, `h`, `k`, `s`, `t`

**Characteristic MIDDLE architecture:**
```
[RI elaboration] + [PP flexible core] + [PP terminator]
   START-class        FREE-class          END-class
   (16.1% PP)         (40.9% PP)          (71.4% PP)
```

**Interpretation:**
RI elements provide discriminative elaboration at the start; PP atoms provide the flexible combinatorial core; PP terminators close the form. This is a generative morphology with systematic structure, not random composition.

**Cross-references:** C510 (positional grammar), C512 (PP as substrate)

### C513 - Short Singleton Sampling Variance
**Tier:** 2 | **Status:** CLOSED | **Scope:** A | **Source:** MIDDLE_SUBCOMPONENT_GRAMMAR (2026-01-23)

Short singleton MIDDLEs (≤3 characters) show no structural differentiation from short repeaters.

**Evidence:**
- Character inventory Jaccard: 1.00 (identical)
- Bigram inventory Jaccard: 0.49 (overlapping)
- Line-initial rate: no significant difference
- Section distribution: similar patterns

**Interpretation:**
Singleton status at short lengths reflects sampling variance within a homogeneous population, not functional distinction. The length-frequency relationship (C498.d) is a gradient phenomenon, not a categorical boundary.

This PROTECTS against over-interpretation of singleton status per C498.b/c. Short singletons are not a special class - they are repeaters that happened to appear once.

**Cross-references:** C498.b (RI singletons), C498.c (RI repeaters), C498.d (length-frequency correlation)

### C513-NOTE: Y-Initial Minimal MIDDLEs (Characterization)
**Tier:** 3 | **Status:** CLOSED | **Scope:** A | **Source:** MIDDLE_CLASS_V3 (2026-01-24)

A small set of RI MIDDLEs (n≈34) are y-initial but do not admit articulator parsing under the canonical morphology, because recognizing articulation would eliminate the MIDDLE entirely. Per C293, these forms are treated as atomic, non-articulated minimal discriminators. Their y-initial surface form is incidental rather than morphological.

**Examples:** `ysh`, `yqo`, `yee`, `yeee`, `yckho`, `ypc`, `ytch`

**Key points:**
- These are legitimate short MIDDLEs, not failures of articulator detection
- Articulator recognition is contingent on leaving a non-empty MIDDLE
- If articulator+prefix would eliminate MIDDLE → articulation is not recognized
- No special parser handling required

These y-initial minimal MIDDLEs cluster near the lower bound of MIDDLE length (≤3-4 chars), consistent with short-form sampling variance (C513) and not indicative of a distinct grammatical subclass.

**What this is NOT:**
- NOT failed articulations
- NOT a new subtype requiring special handling
- NOT evidence for "two prefixes" in RI tokens

**Cross-references:** C293 (MIDDLE primacy), C513 (short singleton variance), C498.d (length-frequency correlation), C291-C294 (articulator constraints)

### C513-NOTE-B: RI Orthogonal Feature Structure (Characterization)
**Tier:** 3 | **Status:** CLOSED | **Scope:** A | **Source:** RI_FEATURE_ANALYSIS (2026-01-24)

RI tokens encode multiple **independent features** that combine freely, rather than forming hierarchical subtypes. Statistical independence tests show observed/expected ratios near 1.0 for all feature pairs.

**Five Orthogonal Axes:**

| Axis | Feature | Rate | Function (speculative) |
|------|---------|------|------------------------|
| **DOMAIN** | Gallows presence (k/t/p/f) | 54.9% | Operational regime / fire degree |
| **POSITION** | Line-initial or line-final | 40.7% | Structural role: opener vs closer |
| **SCOPE** | Record-anchored vs independent | 57.5% / 42.5% | Context-bound vs universal discriminator |
| **EMPHASIS** | Articulator present | 2.7% | Attention marker (71.5% at boundaries) |
| **PREFIX** | Required vs forbidden (C528) | 50.1% / 48.1% | Lexically determined attachment |

**Independence Evidence:**

| Feature Pair | Expected | Observed | Ratio |
|--------------|----------|----------|-------|
| Articulator × Gallows | 11.5 | 10 | 0.87x |
| Gallows × Record-scope | 181.7 | 166 | 0.91x |
| Articulator × Record-scope | 8.9 | 9 | 1.01x |

All ratios ≈ 1.0 confirms statistical independence.

**Interpretation:**

RI tokens are **feature bundles**, not categorical types:
```
RI = [± gallows] × [± boundary] × [± record-anchored] × [± articulated] × [± prefix]
```

Each token carries multiple orthogonal signals. The apparent "RI types" (gallows-RI, articulated-RI, closure-RI) are projections onto single dimensions of a multi-dimensional encoding space.

**Terminology Note:**

"Record-anchored" (57.5%) differs from C514's "locally-derived" (17.4%):
- **C514 local:** RI contains PP atoms from same-folio sources (compositional origin)
- **Record-anchored:** RI shares PP vocabulary with same record (compatibility context)

Both are valid measurements of different properties.

**Brunschwig Alignment (Tier 4, speculative):**

If Currier A is a material registry:
- DOMAIN (gallows) → processing regime / apparatus configuration
- POSITION → ingredient marker (opener) vs result marker (closer)
- SCOPE → material-specific vs universal operations
- EMPHASIS → critical steps requiring attention

This extends the RI Lexical Layer Hypothesis (C526) by characterizing how multiple independent material/operational properties are encoded simultaneously.

**What this is NOT:**
- NOT hierarchical subtypes (H1, H2, H3)
- NOT mutually exclusive categories
- NOT proof of semantic content (features are distributional, not referential)

**Cross-references:** C498 (RI vocabulary track), C510 (positional sub-components), C514-C515 (compositional modes), C526 (lexical layer hypothesis), C528 (PREFIX bifurcation), C529-C530 (gallows patterns)

### C514 - RI Compositional Bifurcation
**Tier:** 2 | **Status:** CLOSED | **Scope:** A | **Source:** MIDDLE_SUBCOMPONENT_GRAMMAR (2026-01-23)

RI tokens exhibit two compositional modes based on PP derivation:

| Mode | Rate | Description |
|------|------|-------------|
| Locally-derived | 17.4% | Contains PP MIDDLE from same record |
| Globally-composed | 82.6% | Uses PP vocabulary from outside record |

**Key evidence:**
- Overall local match: 17.4% (vs ~7% chance baseline)
- Section P highest: 26.1% local (transformational content)
- Section H lowest: 13.5% local (primary categorization)

**Functional interpretation:**
- Locally-derived RI = context-anchored refinement (elaborates on PP already present)
- Globally-composed RI = stand-alone discrimination (independent specification)

**Cross-references:** C509 (PP/RI bifurcation), C512 (PP as substrate), C515 (length correlation)

### C515 - RI Compositional Mode Correlates with Length
**Tier:** 2 | **Status:** CLOSED | **Scope:** A | **Source:** MIDDLE_SUBCOMPONENT_GRAMMAR (2026-01-23)

RI compositional mode correlates with length: short RI operates as atomic global discriminators (0% local at len=2), while long RI embeds local PP context (25% local at len=6+).

**Evidence:**
| Length | Local Rate | Mode |
|--------|------------|------|
| 2 | 0.0% | Atomic/Global |
| 3 | 4.7% | Atomic/Global |
| 4 | 15.9% | Transitional |
| 5 | 22.6% | Compound/Local |
| 6+ | 25%+ | Compound/Local |

**Spearman correlation:** rho = 0.192, p < 0.0001

**Functional interpretation:**

| Short RI (2-3 chars) | Long RI (5+ chars) |
|---------------------|-------------------|
| Atomic | Compound |
| Global discriminator | Context-anchored |
| Stands alone in incompatibility lattice | Embeds local PP as sub-components |

**Cross-references:** C498.d (length-frequency), C514 (compositional bifurcation), C515.a (mechanism)

### C515.a - Compositional Embedding Mechanism
**Tier:** 2 | **Status:** CLOSED | **Scope:** A | **Source:** MIDDLE_SUBCOMPONENT_GRAMMAR (2026-01-23)

Local derivation in RI reflects sub-component embedding from same-record PP, requiring additional morphological material. **Embedding local context is additive, not reductive.**

**Mechanism:**
1. Short RI operates at the atomic level of the ~128-dimensional incompatibility lattice (C475)
2. Long RI achieves context-bound refinement by:
   - Starting with local PP context (defines "where you are")
   - Adding sub-components to specify "which variant"
   - The result is necessarily longer

**Consistency with existing constraints:**
- C267.a: MIDDLEs are compositional (218 sub-components) - local derivation adds components
- C498.d: Longer = rarer (combinatorial explosion) - embedding creates unique combinations
- C506.b: Intra-class behavioral heterogeneity via MIDDLE variation - local embedding implements this

**Cross-references:** C267.a (sub-components), C475 (incompatibility lattice), C498.d (length-frequency), C515 (length correlation)

### C516 - RI Multi-Atom Observation
**Tier:** 2 | **Status:** WEAKENED | **Scope:** A | **Source:** MIDDLE_SUBCOMPONENT_GRAMMAR (2026-01-23), PP_RI_RETEST (2026-01-24)

Registry-internal MIDDLEs contain multiple PP substrings, but this is **trivially expected** from length distributions. The "compatibility intersection" interpretation is now **PROVISIONAL**.

**Quantitative Evidence (unchanged):**
| Metric | Value |
|--------|-------|
| RI with PP match | 100% (retest: 609/609) |
| RI with multiple non-overlapping PP | 99.6% (retest) |
| PP bases used | 261 |
| Collapse ratio | 2.7x (712 RI → 261 bases) |
| Sparsity | 0.03% of theoretical combinations |

**Null Model Context (2026-01-24):**
The multi-atom pattern is **not diagnostic**:
- ANY set of ~400 short MIDDLEs achieves similar containment rates
- Length-matched random sets achieve 99.0% containment
- Multi-containment emerges naturally from: short strings + longer strings + limited alphabet

**PROVISIONAL Interpretation (requires further evidence):**

The intersection formulation may still be meaningful:
```
RI = PP₁ ∩ PP₂ ∩ PP₃ ∩ ... ∩ modifier (PROVISIONAL)
```
But the substring observation alone does not prove compositional derivation.

**What could validate the compositional interpretation:**
- Non-random positional placement of PP substrings within RI
- Semantic/functional correlation between PP atoms and RI behavior
- Evidence that specific PP combinations predict RI properties

**What remains valid:**
- 0.03% sparsity is real (RI space is sparse)
- 261 bases vs ~90 shared with B is real (A uses more discriminative vocabulary)
- C475 incompatibility constraints are real (pairs are illegal)

**What is now PROVISIONAL:**
- "Compatibility intersection" formulation
- PP atoms as meaningful compositional units (vs coincidental substrings)

**Cross-references:** C267.a (sub-components), C475 (incompatibility), C498.d (length correlation), C512 (PP/RI bifurcation - REVISED)

### C517 - Superstring Compression (GLOBAL)
**Tier:** 3 | **Status:** CLOSED | **Scope:** GLOBAL | **Source:** MIDDLE_SUBCOMPONENT_GRAMMAR (2026-01-23)

MIDDLEs across ALL systems are morphologically compressed superstrings over the PP sub-component inventory, exhibiting systematic overlap (65-77%) that reduces total string length while preserving recognizability. Originally discovered in RI, compression scan (Test 13) confirmed pattern is manuscript-wide.

**Evidence:**
| Population | Mean Overlap | Compression | High Overlap (>30%) |
|------------|--------------|-------------|---------------------|
| RI (A-exclusive) | 65% | 2.29x | 83.5% |
| B-exclusive | 77% | 2.65x | 91.2% |
| AZC | 70% | 2.44x | 87.3% |
| PP (shared) | 65% | 2.18x | 80.1% |

**Hinge letters:** o, e, h, c, a, s, k, l (7/8 are kernel primitives from C085)

**Interpretation:**
Superstring compression is the **morphological substrate** (extends C383). The same high-connectivity characters that mediate B transitions also serve as compression hinges in all systems. This is global infrastructure, not system-specific function.

**Cross-references:** C085 (kernel primitives), C267.a (sub-components), C383 (global type system), C516 (multi-atom), C519 (global compatibility)

### C518 - Compatibility Enrichment (GLOBAL)
**Tier:** 3 | **Status:** CLOSED | **Scope:** GLOBAL | **Source:** MIDDLE_SUBCOMPONENT_GRAMMAR (2026-01-23)

**REVISED (2026-01-23):** Originally discovered in RI (4.7x enrichment), Test 14 revealed enrichment is GLOBAL across all systems. Superstring co-presence enriches compatibility 5-7x in all populations, not just RI.

PP-shaped substrings that co-occur within the same superstring are enriched for mutual compatibility compared to random PP pairs. This extends C383: the global type system includes compatibility relationships, not just type markers.

**Evidence:**
| System | Enrichment | Z-score | Superstring Pairs |
|--------|------------|---------|-------------------|
| RI (A-exclusive) | 6.8x | 61.88 | 3,847 |
| B-exclusive | 5.3x | 48.2 | 2,156 |
| AZC | 7.2x | 31.4 | 892 |
| PP (shared) | 5.5x | 42.7 | 1,423 |

**Interpretation:**
Compatibility enrichment is **global infrastructure** baked into the morphological substrate itself. All systems inherit this - it's how the type system encodes compatibility relationships. See C519 for architecture, C520 for exploitation gradient.

**What this does NOT establish:** No semantic feature grammar. No A↔B lookup. No decomposable rules. No operator readability.

**Cross-references:** C383 (global type system), C475 (MIDDLE incompatibility), C517 (compression), C519 (architecture), C520 (gradient)

### C519 - Global Compatibility Architecture
**Tier:** 3 | **Status:** CLOSED | **Scope:** GLOBAL | **Source:** MIDDLE_SUBCOMPONENT_GRAMMAR (2026-01-23)

The superstring compression mechanism (C517) combined with compatibility enrichment (C518) constitutes a **global compatibility architecture** that spans all text systems. This extends C383: the global morphological type system includes embedded compatibility relationships, not just type markers.

**Architecture:**
1. **Substrate:** PP vocabulary forms atomic layer (C512)
2. **Compression:** All MIDDLEs compress PP atoms via shared hinge letters (C517)
3. **Compatibility:** Co-presence in superstring enriches compatibility 5-7x (C518)
4. **Scope:** Architecture applies to A, B, and AZC identically

**Key insight:** Compatibility relationships are encoded in the morphology itself, not computed separately. When constructing a valid MIDDLE, the compression pattern automatically encodes which other MIDDLEs it can co-occur with.

**Why this matters:** Explains how the manuscript maintains compatibility coherence across 37,957 tokens without explicit lookup tables. The constraint is structural, not procedural.

**Cross-references:** C383 (global type system), C475 (MIDDLE incompatibility), C512 (PP substrate), C517 (compression), C518 (enrichment)

### C520 - System-Specific Exploitation Gradient
**Tier:** 3 | **Status:** CLOSED | **Scope:** GLOBAL | **Source:** MIDDLE_SUBCOMPONENT_GRAMMAR (2026-01-23)

While the compatibility architecture (C519) is global, systems exploit it with different intensity. RI exploits compatibility encoding most intensively because material discrimination requires maximum coherence.

**Exploitation Gradient:**
| System | Enrichment | Purpose | Intensity |
|--------|------------|---------|-----------|
| RI (A-exclusive) | 6.8x | Material discrimination | HIGHEST |
| AZC | 7.2x | Zone coherence | HIGH |
| PP (shared) | 5.5x | Pipeline vocabulary | MEDIUM |
| B-exclusive | 5.3x | Execution elaboration | BASELINE |

**Interpretation:**
- **RI highest:** Discrimination tokens must encode precise compatibility intersections (C516)
- **AZC high:** Zone labels benefit from strong compatibility (limited vocabulary, high precision)
- **PP medium:** Shared vocabulary trades some enrichment for cross-system validity
- **B baseline:** Execution elaborations are constrained by grammar, not just compatibility

**Why RI leads:** RI tokens encode `PP₁ ∩ PP₂ ∩ ... ∩ modifier` - each atom adds compatibility constraints. More atoms = stricter compatibility requirements = higher enrichment when satisfied.

**Cross-references:** C516 (multi-atom composition), C519 (global architecture), C475 (incompatibility)

---

## Pharma Label Structure (C523-C524)

### C523 - Pharma Label Vocabulary Bifurcation
**Tier:** 2 | **Status:** CLOSED | **Scope:** A | **Source:** PHARMA_LABEL_ANALYSIS (2026-01-23)

Pharma section labels exhibit a two-tier vocabulary structure with complete disjunction between jar labels and content labels.

**Jar Labels (container identifiers):**
| Metric | Value |
|--------|-------|
| Total unique | 16 |
| In Currier A | 2 (12.5%) |
| In Currier B | 0 (0%) |
| In AZC | 1 |
| NOT in text | 14 (87.5%) |

**Content Labels (plant specimens):**
| Metric | Value |
|--------|-------|
| Total unique | 189 |
| In Currier A | 101 (53%) |
| PP-enriched | 58% (vs 33.5% baseline) |
| Chi-square | 28.3, p < 0.0001 |

**Key Finding:** Jar vs content token overlap = Jaccard 0.000 (zero shared tokens).

**Interpretation:**
- **Jar labels** = unique configuration identifiers (not part of working vocabulary)
- **Content labels** = shared discrimination profiles (reusable, PP-enriched)

Content labels being PP-enriched means they point to materials that propagate to B execution - "things that will be processed," not just identified. This confirms PP = pipeline participation (C504-C506).

**Cross-references:** C498 (PP/RI bifurcation), C504-C506 (PP execution role), C517 (superstring compression)

### C524 - Jar Label Morphological Compression
**Tier:** 2 | **Status:** CLOSED | **Scope:** A | **Source:** PHARMA_LABEL_ANALYSIS (2026-01-23)

Jar labels exhibit elevated morphological compression via PP sub-component packing, consistent with "configuration signature" encoding.

**Length Analysis:**
| Population | Mean Length |
|------------|-------------|
| Currier A tokens | 6.0 |
| Jar labels | 7.1 |

**Sub-Component Density:**
| Jar Label | MIDDLE | PP Atoms |
|-----------|--------|----------|
| yteoldy | yteol | 8 (yteo, yte, eol, teo, te, eo, yt, ol) |
| tsholdy | tshol | 6 (tsho, tsh, sho, sh, ts, ol) |
| keoraiiin | keorai | 5 (keo, or, eo, ai, ke) |
| okoldody | oldo | 3 (do, ol, ld) |

**Compression Mechanism:** Hinge-letter compression (ke→eo→or via shared letters 'e' and 'o').

**Shorter Base Forms in Vocabulary:**
- `okolky` contains: okol, kolky, olky, kol, olk, oko
- `tsholdy` contains: sholdy, tshol, shol, tsho, oldy, sho
- `yteoldy` contains: yteol, teol, oldy, teo, eol

**Interpretation:** Jar labels are dense superstrings encoding multiple specification components. Their absence from the vocabulary (87.5% unique) suggests they are one-time "configuration signatures" rather than reusable vocabulary. This is consistent with C267.a (MIDDLE sub-component structure) applied at higher density.

**Cross-references:** C267.a (sub-components), C517 (superstring compression), C523 (vocabulary bifurcation)

### C525 - Label Morphological Stratification

**Tier:** 3 (Structural Characterization)
**Scope:** A (pharmaceutical labels)
**Phase:** PHARMA_LABEL_ANALYSIS (2026-01-24)

AZC pharmaceutical labels exhibit morphological stratification distinct from text tokens, with systematic PREFIX/SUFFIX preferences and high vocabulary exclusivity.

**PREFIX Distribution Comparison:**

| PREFIX | PP Text | RI Text | Labels |
|--------|---------|---------|--------|
| o | 24% | 19% | **50%** |
| c | 20% | 24% | 13% |
| qo | 14% | 10% | **~0%** |
| s | 13% | 12% | 13% |
| d | 6% | 11% | 13% |

**Key Morphological Differences:**
- Labels show 2x elevation in o-prefix (50% vs 20-24% in text)
- Labels show near-complete suppression of qo-prefix (~0% vs 14% in PP text)
- Labels show elevated -y suffix concentration (38% vs 22-32% in text)
- GALLOW distribution (k > t > p > f) remains consistent across all categories

**Vocabulary Overlap:**
- 33% of labels are PP tokens (shared vocabulary)
- 6% of labels are RI tokens (A-exclusive)
- **61% of labels are NOT in text vocabulary** (label-only tokens)

**Within-Group Morphological Sharing:**
Grouped plants (same jar/folio region) show systematic sharing:
- Shared GALLOW letters (k, t, p, f) marking processing category
- Shared MIDDLE substrings (e.g., "dar", "ar", "ol") marking morphological features
- Example: f102r2 horizontal roots share "dar" in MIDDLE (koldarod, odalydary)

**Interpretation:**
1. **o-prefix elevation:** Labels preferentially use low-control-flow prefixes because they name things rather than commanding operations. Consistent with C466-C467 (PREFIX = control-flow participation).

2. **qo-prefix suppression:** qo- marks escape routes in control grammar (C397, C467). Labels don't participate in procedural escape - they identify specimens. This validates PREFIX function model.

3. **61% label-only vocabulary:** Labels occupy an even more specialized discrimination stratum than RI text tokens. They identify specific visual specimens, not constraint bundles for procedural text.

4. **Within-group MIDDLE sharing:** Similar specimens sharing MIDDLE substrings supports C293 (MIDDLE = primary discriminator). Shared components encode properties relevant to specimen similarity.

**Visual Correlation (observed):**
- PP labels correlate with processed/standardized materials (cut, interchangeable)
- RI labels correlate with unique specimens requiring specific identification
- Label-only tokens mark the most distinctive specimens

**Cross-references:** C293 (MIDDLE essentiality), C397 (qo-prefix escape), C466-C467 (PREFIX control-flow), C498 (vocabulary stratification), C517 (superstring compression), C523-C524 (pharma label structure)

### C526 - RI Lexical Layer Hypothesis

**Tier:** 3 (Structural Characterization)
**Scope:** A (RI vocabulary)
**Phase:** RI_STRUCTURE_ANALYSIS (2026-01-24)

RI extensions within MIDDLEs may function as a **lexical layer** that anchors abstract grammar to specific external substances, while PREFIX/SUFFIX/PP remain purely functional markers.

**The Grammar vs Lexicon Distinction:**

| Layer | Function | Semantic Content | Behavior |
|-------|----------|------------------|----------|
| **Grammar** (PREFIX, SUFFIX, PP) | Functional marking | None (abstract positions) | Combinatorial, global roles |
| **Lexicon** (RI extensions) | Referential anchoring | Points to substances | Arbitrary identifiers, localized |

**Evidence for Lexical Function (REVISED 2026-01-24):**

1. **Scale:** 609 unique RI MIDDLEs in Currier A (regenerated with atomic-suffix parser 2026-01-24)
2. **Localization:** 87.3% appear on only 1 folio (vocabulary-like distribution)
3. **Non-compositional:** Extensions don't decompose systematically (arbitrary identifiers)
4. **Variation:** Localized RI appear with multiple PREFIX/SUFFIX combinations (same referent, different grammar)

**Evidence for Grammar Layer Independence:**

1. **PREFIX versatility:** ch used with 57 different MIDDLEs, sh with 29, qo with 27
2. **SUFFIX versatility:** dy used with 40 different MIDDLEs, y with 34
3. **Global roles:** Same PREFIX/SUFFIX patterns apply across different RI MIDDLEs

**RI Distribution Pattern:**

| Category | Count | Avg Folios | Function |
|----------|-------|------------|----------|
| Strictly local (1 folio) | 123 | 1.0 | Specific material identifiers |
| Local (1-2 folios) | 144 | 1.4 | Material identifiers |
| Distributed (10+ folios) | 5 | 23.2 | Compatibility bridges (odaiin, ho, ols, eom, chol) |

**The ct+ho Pattern (MIDDLE-Specific Constraint):**

One exception to PREFIX universality: ho, hod, hol, heo appear ONLY with ct prefix. This suggests certain RI extensions may have PREFIX requirements beyond grammar.

**Semantic Ceiling Refinement:**

The lexical layer hypothesis refines C120 (PURE_OPERATIONAL):
- **Grammar:** No semantic content (C120 applies)
- **Lexicon:** REFERENTIAL content (points to THAT, not WHAT)

What IS recoverable: that 609 distinct substances/categories are distinguished
What is NOT recoverable: which substances they are

**Two-Layer Model:**

```
Word = PREFIX + MIDDLE + SUFFIX
       ↓        ↓        ↓
       Grammar  MIDDLE   Grammar
                ↓
        PP_atom + Extension
        ↓         ↓
        Grammar   Lexicon (referential)
```

**Interpretation:**

RI extensions behave like dictionary entries (arbitrary, localized, non-compositional) rather than grammar (systematic, global, combinatorial). This allows the system to reference ~609 specific external substances/categories while keeping all procedural/control information in abstract grammar. The grammar tells you WHAT TO DO; the lexicon tells you TO WHAT.

**Caveats:**
- Tier 3: Structural characterization, not semantic mapping
- Cannot identify WHICH substances (semantic ceiling)
- "Lexical" is functional description, not linguistic claim
- Does not enable material identification or translation

**Cross-references:** C120 (PURE_OPERATIONAL), C498 (RI vocabulary track), C475 (folio localization), C509 (PP/RI separability), C517 (superstring compression), C528 (RI PREFIX bifurcation - PREFIX attachment is lexically determined)

### C527 - Suffix-Material Class Correlation (Fire Degree)

**Tier:** 3 (Structural Characterization)
**Scope:** A (suffix patterns)
**Phase:** SUFFIX_MATERIAL_ANALYSIS (2026-01-24)

Within Currier A, suffix distribution correlates strongly with material class as indicated by PP atoms. Animal-associated PP (te, ho, ke per C505) shows dramatically different suffix patterns than herb PP.

**Evidence:**

| Suffix Group | Animal PP | Herb PP | Interpretation |
|--------------|-----------|---------|----------------|
| -y, -dy | 0% | 41% | LOW fire (gentle processing) |
| -ey, -ol | 78% | 27% | HIGH fire (strong processing) |

**Statistical Validation:**
- Chi-square: 178.34
- p-value: 1.12 x 10^-40 (highly significant)
- Length confounding: RULED OUT (effect persists at same MIDDLE length)
- Sample size: 181 animal PP tokens, 4,285 herb PP tokens

**Fire Degree Interpretation (Conditional on Brunschwig):**

Animal materials in Brunschwig's distillation manual require higher fire degrees than herbs. The suffix pattern is consistent with:
- -y, -dy = Gentle/low-fire processing (herbs)
- -ey, -ol = Strong/high-fire processing (animal materials)

**Two-Axis Suffix Model:**

Suffix operates on two orthogonal dimensions:

| Axis | Scope | Evidence | Tier |
|------|-------|----------|------|
| System role | A vs B enrichment | C283, C495 | 2 |
| Material class | Within A: animal vs herb | This finding | 3 |

This parallels the HT two-axis model (C477: density vs morphology).

**Relationship to C495:**

C495 establishes suffix correlates with REGIME compatibility breadth at the A/B boundary. C527 extends this into A-internal structure: suffix also correlates with material class within the registry.

**The -dy Puzzle:**
- C527: -dy is herb-associated (0% animal PP)
- C283: -dy is B-enriched (1.75x)

Both can be true: herbs prefer -dy in A registry, AND -dy appears frequently in B execution for different reasons (different axes).

**Caveats:**
- Fire-degree interpretation is conditional on Brunschwig alignment
- Associative, not causal (per C495 framing)
- Does not establish suffix "encodes" fire degree, only correlates with material class

**Cross-references:** C283 (suffix A/B enrichment - CORRECTED), C495 (suffix-regime breadth), C505 (animal PP enrichment), C506 (PP non-propagation)

### C528 - RI PREFIX Lexical Bifurcation

**Tier:** 2 (empirical split) / 3 (interpretation)
**Scope:** A (RI vocabulary)
**Phase:** RI_PREFIX_ANALYSIS (2026-01-24)

RI MIDDLEs split into two nearly-disjoint populations based on PREFIX behavior:

| Population | Count | % of RI |
|------------|-------|---------|
| **PREFIX-REQUIRED** | 334 | 50.1% |
| **PREFIX-FORBIDDEN** | 321 | 48.1% |
| **PREFIX-OPTIONAL** | 12 | 1.8% |

Only 12 MIDDLEs (1.8%) ever appear both with and without PREFIX. The rest are locked into one morphological pattern.

**Evidence:**

- 98.2% of RI MIDDLEs exclusively take or reject PREFIX
- PREFIX-REQUIRED examples: acp, afd, aiikh, aiind, akod, alda, alok
- PREFIX-FORBIDDEN examples: aiee, aiid, aiio, aikhe, cckh, cfaras, cfhod

**Section Independence (Tier 2):**

The split is NOT section-driven. Both populations show identical section distributions:

| Section | PREFIX Rate | PREFIX-REQ H-only | PREFIX-FORB H-only |
|---------|-------------|-------------------|-------------------|
| H | 53.7% | 65.3% | 68.8% |
| P | 54.8% | 29.0% | 27.7% |

The ~50/50 split holds within each section, confirming the distinction is substance-inherent.

**Interpretation (Tier 3):**

PREFIX attachment is **lexically determined** for RI, not grammatically optional:

- Some substance identifiers inherently require PREFIX marking
- Others inherently forbid it
- This creates two parallel substance vocabularies on each folio

**Relationship to C509.a:**

The aggregate 54% PREFIX rate in RI (C509.a) is now explained: it emerges from mixing two disjoint populations (~50% each), not from PREFIX being "optional" on all MIDDLEs.

**Relationship to C526:**

This **strengthens** the grammar vs lexicon model. PREFIX is grammatical globally, but its attachment to specific RI MIDDLEs is lexically encoded:

| Layer | PREFIX Behavior |
|-------|-----------------|
| Grammar (global) | Combinatorially free |
| Lexicon (RI) | Lexically fixed per entry |

**Possible Functional Interpretation (Tier 4, speculative):**

If PREFIX encodes control-flow participation (C466-C467), then:
- PREFIX-REQUIRED: substances that inherently engage control-flow marking
- PREFIX-FORBIDDEN: pure discrimination without control-flow marking

**Cross-references:** C509.a (RI morphological divergence), C526 (RI lexical layer), C466-C467 (PREFIX control-flow), C498 (RI vocabulary track), C529 (gallows positional asymmetry - parallel bifurcation)

### C529 - Gallows Positional Asymmetry in PP/RI

**Tier:** 2 | **Status:** NEW | **Scope:** A
**Phase:** GALLOWS_MIDDLE_ANALYSIS (2026-01-24)

Gallows letters (p, t, k, f) show significant positional asymmetry between PP and RI MIDDLEs:

| Position | PP | RI |
|----------|-----|-----|
| Gallows-initial | 30.4% | 20.1% |
| Gallows-medial | 39.3% | 57.8% |
| Gallows-final | 30.4% | 22.1% |

**Statistical significance:** Chi-square = 7.69, p < 0.01

**Evidence:**
- PP gallows are "atomic" - simple forms that START with gallows: `k`, `ka`, `t`, `fo`, `fch`
- RI gallows are "embedded" - longer forms with gallows in MIDDLE: `aiikh`, `cfaras`, `cfhod`, `alolk`
- 84% of gallows-RI are ≥4 chars; only 44% of gallows-PP are ≥4 chars

**Bench gallows (cXh patterns) are RI-enriched:**

| Pattern | RI | PP | % RI |
|---------|----|----|------|
| cph | 26 | 6 | 81% |
| ckh | 20 | 11 | 65% |
| cth | 13 | 9 | 59% |
| cfh | 4 | 3 | 57% |

This explains the 3-4x A-enrichment of bench gallows observed in gallows_distribution.json: they are RI-heavy, and RI is A-internal vocabulary.

**Discrimination heuristic:**
- Length ≥4 AND not gallows-initial → predict RI: 76.6% accuracy
- Short + gallows-initial → predict PP

**Interpretation:**
This is a **parallel bifurcation** to C528 (PREFIX attachment):
- C528: PREFIX attachment is lexically bifurcated (REQUIRED vs FORBIDDEN)
- C529: Gallows POSITION is bifurcated (PP-initial vs RI-medial)

PP provides atomic gallows building blocks; RI elaborates them into complex discriminators with embedded gallows.

**Cross-references:** C528 (PREFIX bifurcation), C509.a (morphological divergence), C511 (derivational productivity), C512.a (positional asymmetry in sub-components)

### C530 - Gallows Folio Specialization

**Tier:** 2 | **Status:** NEW | **Scope:** A
**Phase:** GALLOWS_MIDDLE_ANALYSIS (2026-01-24)

Currier A folios show gallows specialization patterns:

**Global distribution:**

| Gallows | % of total |
|---------|------------|
| k | 53.7% |
| t | 30.4% |
| p | 11.4% |
| f | 4.5% |

**Folio-level patterns:**
- k is the "default" gallows: 78/109 folios (72%) are k-dominant
- t-specialized folios cluster: f4r (69% t), f10r (74% t), f29v (71% t), f2v (70% t)
- **p and f are NEVER folio-dominant** - always minority markers

**RI-PP coherence within folios:**
- 62.2% of folios have same dominant gallows in both RI and PP
- Expected if independent: ~54%
- Modest but real within-folio coherence

**Record-level co-occurrence (Tier 3 interpretation):**
When RI contains gallows X, PP in the same record is enriched for X:

| Gallows | PP baseline | Observed | Enrichment |
|---------|-------------|----------|------------|
| k | 23.5% | 54.8% | 2.3x |
| t | 15.8% | 33.1% | 2.1x |
| p | 8.7% | 42.9% | 4.9x |
| f | 5.0% | 17.9% | 3.6x |

**Interpretation:**
Gallows letters may mark **categorical domains**:
- k = default/unmarked domain (most folios)
- t = alternative domain (cluster of specialized folios)
- p, f = rare specialized markers (never dominant)

This suggests thematic coherence: records and folios cluster around gallows "domains" where both RI and PP use the same gallows vocabulary.

**Cross-references:** C498 (RI folio localization), C529 (gallows positional asymmetry)

---

## B Folio Differentiation (C531-C534)

> **Summary:** B folios share the same 49-class grammar but each has unique vocabulary. 98.8% of B folios have at least one unique MIDDLE. This unique vocabulary is 88% B-exclusive (not in A, not AZC-filtered) and fills the same grammatical slots as classified tokens. Adjacent folios' unique MIDDLEs are grammatically similar (same slots, different words). Section-specific profiles exist but are partially confounded by PREFIX associations.

### C531 - Folio Unique Vocabulary Prevalence

**Tier:** 2 | **Status:** NEW | **Scope:** B
**Phase:** CLASS_COMPATIBILITY_ANALYSIS (2026-01-25)

B folios exhibit near-universal unique vocabulary:

| Metric | Value |
|--------|-------|
| Folios with unique MIDDLE | **81/82 (98.8%)** |
| Only folio without unique vocabulary | f95r1 |
| Mean unique MIDDLEs per folio | 10.5 |
| Total unique MIDDLEs | 858 |

**Evidence:**
- "Unique MIDDLE" = appears in exactly 1 B folio
- f95r1's 38 MIDDLEs are all shared with other folios
- Unique vocabulary is distinct from core vocabulary (41 MIDDLEs appearing in >50% of folios)

**Interpretation:**
Each B folio contributes unique vocabulary to the overall B grammar. Folios are not interchangeable copies - they are **specific procedures** using a shared grammar.

**Cross-references:** C501 (B-exclusive stratification), C121 (49-class grammar)

### C532 - Unique MIDDLE B-Exclusivity

**Tier:** 2 | **Status:** NEW | **Scope:** B
**Phase:** CLASS_COMPATIBILITY_ANALYSIS (2026-01-25)

Unique B MIDDLEs are overwhelmingly B-exclusive:

| Classification | Count | Percentage |
|----------------|-------|------------|
| **B-exclusive** (not in A) | 755 | 88.0% |
| PP (A-derived, AZC-filtered) | 103 | 12.0% |

**Evidence:**
- B-exclusive = MIDDLE appears in B but not in A
- PP = MIDDLE appears in both A and B (subject to A→B pipeline)
- Per-folio breakdown: mean 8.8 B-exclusive unique, mean 1.2 PP unique

**Implications:**
1. Unique vocabulary is primarily B-internal grammar, not A-derived
2. 88% of unique MIDDLEs are NOT subject to AZC filtering
3. Each folio's unique vocabulary is always locally available
4. AZC modulates shared PP vocabulary, not folio-specific identity

**Validates C501:** The B-exclusive stratification finding holds for unique vocabulary subset.

**Cross-references:** C501 (B-exclusive stratification), C470 (MIDDLE restriction inheritance), C502.a (morphological filtering cascade)

### C533 - Unique MIDDLE Grammatical Slot Consistency

**Tier:** 2 | **Status:** NEW | **Scope:** B
**Phase:** CLASS_COMPATIBILITY_ANALYSIS (2026-01-25)

Unique MIDDLEs fill the same grammatical slots as classified tokens:

| Metric | Value |
|--------|-------|
| Unique MIDDLE tokens with matching PREFIX/SUFFIX | **75%** |
| Classes used by unique MIDDLE tokens | 32 / 49 |
| Adjacent folio class overlap (Jaccard) | 0.196 |
| Non-adjacent folio class overlap | 0.150 |
| **Adjacent/non-adjacent ratio** | **1.30x** |

**Evidence:**
- Morphological signature = (PREFIX, SUFFIX) pair
- 75% of unique MIDDLE tokens have a signature that appears in classified tokens
- Inferred class = most common class for that signature in classified data
- Adjacent folios share class sets at 1.30x the rate of non-adjacent

**Interpretation:**
Unique MIDDLEs are grammatically equivalent to their classified counterparts. They fill the same slots but with different "words" - like synonyms in a grammar.

Adjacent folios' unique vocabulary serves similar grammatical functions: **different words, same role**.

**Note on containment:** 99.3% of unique MIDDLEs contain a core MIDDLE as substring. Per expert validation (C511, C512), this is trivially expected from string mathematics and compositional morphology, not a semantic "parent-child" relationship.

**Cross-references:** C121 (49 classes), C501 (orthographic elaboration), C511 (derivational productivity), C512 (stylistic bifurcation)

### C534 - Section-Specific Prefixless MIDDLE Profiles

**Tier:** 3 | **Status:** NEW (PARTIAL) | **Scope:** B
**Phase:** CLASS_COMPATIBILITY_ANALYSIS (2026-01-25)

Prefixless unique MIDDLEs show section-specific distribution, but effect is partially confounded:

**Overall test:** chi2=106.2, p=0.000059 (highly significant)

| Section | Over-represented Operators |
|---------|---------------------------|
| astro_cosmo | 'ke' 2.17x |
| herbal_A | 'ckh' 2.19x |
| herbal_B | 'sh' 2.01x |
| pharma | 'or' 2.10x, 'dy' 2.02x |
| recipe_stars | 'ai' 1.52x |

**PREFIX control test:**

| PREFIX Stratum | Section Differentiation |
|----------------|------------------------|
| NONE (prefixless) | **p=0.0230** (SURVIVES) |
| ch | p=0.151 (not significant) |
| qo | p=0.497 (not significant) |
| sh | p=0.176 (not significant) |

**Interpretation:**
- For **prefixless tokens** (~35% of unique MIDDLEs): Section effects are REAL
- For **prefixed tokens**: Section effects are explained by PREFIX-section associations (C374, C423)
- The overall highly-significant result is a **mix of real and confounded effects**

**Caveat:** Only ~35% of unique MIDDLEs are prefixless, so the independent section signal is partial.

**Cross-references:** C374 (section-specific PREFIX distributions), C423 (PREFIX-bound vocabulary domains)

### C535 - B Folio Vocabulary Minimality

**Tier:** 2 | **Status:** NEW | **Scope:** B
**Phase:** CLASS_COMPATIBILITY_ANALYSIS (2026-01-25)

B folios achieve near-minimal MIDDLE vocabulary coverage:

| Metric | Value |
|--------|-------|
| Total distinct MIDDLEs in B | 1,339 |
| Minimum folios for coverage (greedy) | **81** |
| Actual folios | **82** |
| Redundancy ratio | **1.01x** |

**Evidence:**

1. **Greedy set cover analysis:** Starting with the folio covering most MIDDLEs, iteratively adding folios that cover the most remaining MIDDLEs, 81 folios are needed to cover all 1,339 B MIDDLEs.

2. **Pairwise distinctiveness:** Zero folio pairs exceed 50% Jaccard overlap. Folios are highly distinct from each other.

3. **Unique contribution:** Each folio contributes vocabulary appearing in no other folio:
   - Mean: 10.5 unique MIDDLEs per folio
   - Only 1 folio (f95r1) has zero unique MIDDLEs
   - 858 total unique MIDDLEs (64% of all B MIDDLEs)

4. **Section distribution:**
   | Section | Folios | Unique MIDDLEs | % of Total Unique |
   |---------|--------|----------------|-------------------|
   | recipe_stars (f103+) | 23 | 446 | 52% |
   | herbal_A | 25 | 138 | 16% |
   | herbal_B | 20 | 146 | 17% |
   | pharma | 12 | 99 | 12% |
   | astro_cosmo | 2 | 29 | 3% |

**Interpretation:**

The 83-folio count is not arbitrary but **structurally determined** by vocabulary coverage:
- Each folio exists because it contributes vocabulary no other folio provides
- You cannot have fewer folios without losing MIDDLE vocabulary
- The 19:1 A:B ratio (1,559 A records : 82 B folios) emerges from this coverage requirement

**Note on procedural coverage:** Per C506.b, vocabulary coverage is a **lower bound** on procedural coverage. Different MIDDLEs within the same class enable different execution flows (73% of MIDDLE pairs have transition JS > 0.4). The structural minimum ensures access to all behavioral variants.

**Relationship to mastery horizon (X.1):** This finding grounds rather than replaces the Puff-Voynich 83:84 alignment. The "mastery horizon" becomes a consequence: you need ~83 units because that's what the domain requires for complete coverage, and that count happens to be learnable by experts.

**Cross-references:** C531 (unique vocabulary prevalence), C532 (B-exclusivity), C476 (A-side coverage optimality), C506.b (intra-class behavioral heterogeneity)

### C536 - Material-Class REGIME Invariance

**Tier:** 2 | **Status:** REVISED | **Scope:** A->B
**Phase:** MATERIAL_REGIME_MAPPING (2026-01-25)

Both animal AND herb material classes preferentially route to REGIME_4 (precision control):

| Material Class | REGIME_4 Enrichment | p-value | High-reception folios |
|----------------|---------------------|---------|----------------------|
| Animal | **2.03x** | 0.024 | 13/21 (62%) |
| Herb | **2.09x** | 0.011 | 14/22 (64%) |
| Baseline | 1.00x | - | 25/82 (30.5%) |

**Key finding:** REGIME routing is NOT material-class-specific. Both material classes prefer precision execution at nearly identical enrichment levels.

**Evidence:**

1. **Material classification:**
   - Animal markers: te/ho/ke PP (C505), ey/ol suffixes (C527)
   - Herb markers: keo/eok/ko/cho/to PP, y/dy suffixes
   - Animal high-confidence: 44 records
   - Herb high-confidence: 104 records

2. **Folio-level correlation:** r = 0.845 between animal and herb reception patterns. They route to the SAME folios, not different ones.

3. **REGIME distribution (both classes):**
   - REGIME_4: ~2x enriched
   - REGIME_1: <0.15x (strongly avoided)
   - REGIME_2/3: near baseline

**Interpretation:**

REGIME_4 encodes **execution precision requirements**, not material identity. Different materials can share execution requirements while differing in behavioral parameterization. This strengthens C494 (REGIME_4 = precision axis).

**Cross-references:** C494 (REGIME_4 precision axis), C537 (token-level differentiation), C506.b (behavioral heterogeneity)

---

### C537 - Token-Level Material Differentiation

**Tier:** 2 | **Status:** NEW | **Scope:** A->B
**Phase:** MATERIAL_REGIME_MAPPING (2026-01-25)

Despite identical REGIME routing (C536), material classes differentiate at token variant level:

| Metric | Value |
|--------|-------|
| Overall Jaccard (animal vs herb tokens) | **0.382** |
| Per-class mean Jaccard | **0.371** |
| Animal-only tokens | 198 (26.6%) |
| Herb-only tokens | 684 (55.6%) |
| Shared tokens | 546 (38.2%) |

**62% of token variants differ between animal and herb** despite routing to identical REGIMEs.

**Most differentiated classes (PREFIX groups):**
| Class | Jaccard | Description |
|-------|---------|-------------|
| ke | 0.037 | Near-zero overlap |
| fch | 0.111 | Strong differentiation |
| ol | 0.169 | Strong differentiation |
| qo | 0.322 | Moderate differentiation |

**Interpretation:**

The manuscript achieves material-appropriate execution NOT by routing to different procedures, but by **selecting different variants within a shared grammatical framework**. This confirms C506.b: tokens within same class are positionally compatible but behaviorally distinct.

**Combined model:**
```
Material Class -> REGIME: NO differentiation (both -> REGIME_4)
Material Class -> Folio: NO differentiation (r=0.845 correlation)
Material Class -> Token Variants: YES differentiation (Jaccard=0.38)
```

**Cross-references:** C536 (REGIME invariance), C506.b (intra-class behavioral heterogeneity), C506.a (token-level PP effects)

---

### C538 - PP Material-Class Distribution

**Tier:** 3 | **Status:** NEW | **Scope:** A
**Phase:** PP_CLASSIFICATION (2026-01-25)

PP MIDDLEs partition into material-class associations based on enrichment in animal vs herb suffix-signature records:

| Class | Count | % | Description |
|-------|-------|---|-------------|
| ANIMAL | 63 | 15.6% | >2x enriched in animal-suffix records |
| HERB | 113 | 28.0% | >2x enriched in herb-suffix records |
| MIXED | 67 | 16.6% | Present in both, no strong preference |
| NEUTRAL | 161 | 39.9% | Not enriched in either |

**Top animal-associated PPs:** pch (43x), opch (18x), octh (9x), cph (3.7x), kch (3.7x), ch (2.9x), h (2.5x)

**Top herb-associated PPs:** keo (66x), eok (52x), ko (33x), cho (33x), to (33x), eo (3.3x)

**RI Projection:**
- 95.9% of RI contain PP atoms (mean 4.36 atoms per RI)
- RI can be tentatively tagged through PP composition
- High-confidence: 16 animal RI, 57 herb RI
- High noise: 44.5% project as MIXED

**Caveat:** Classification is conditional on Brunschwig alignment (suffix patterns from C527). This is Tier 3, not Tier 2.

**Cross-references:** C505 (PP profile differentiation), C527 (suffix-material correlation), C516 (RI multi-atom composition)

---

## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
