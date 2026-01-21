# Currier A Constraints (C224-C299, C345-C346, C420-C424, C475-C478, C498-C500)

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

### C299.a - Section T Measurement Clarification
**Tier:** 2 | **Status:** CLOSED (Clarification)
C299 measures the presence of *section-characteristic* vocabulary (discriminators enriched or exclusive to a Currier A section), not raw vocabulary overlap. Section T shows 0% presence in Currier B because it contains no section-distinctive vocabulary, despite its constituent tokens appearing ubiquitously across B as infrastructure (67.7% of Section T MIDDLEs appear in B vs 42.4% baseline; 100% of B folios contain Section T vocabulary). Section T (f1r, f58r, f58v) functions as foundational/template content using only generic infrastructure vocabulary.
**Source:** A_SECTION_T_CHARACTERIZATION (2026-01-21)

---

## A-Exclusive Vocabulary Track (C498)

### C498 - Registry-Internal Vocabulary Track
**Tier:** 2 | **Status:** CLOSED

A-exclusive MIDDLEs (56.6%, 349 types) form a morphologically distinct registry-internal vocabulary track that does not propagate through the A→AZC→B pipeline.

**Evidence:**
- 349 MIDDLEs appear in Currier A but never in Currier B
- ct-prefix enrichment: 5.1× (vs shared MIDDLEs)
- Suffix-lessness: 3× enriched (no decision archetype needed)
- Folio-localization: 1.34 folios (vs 7.96 for shared)
- AZC presence: 8.9% (vs 57.5% for shared) - residue is noise, not distinct stratum

**Morphological signature interpretation:**
- ct-prefix (C492): Only legal in P-zone AZC, 0% in C/S-zones → morphologically incompatible with most AZC positions
- Suffix-less: No downstream execution routing required → these MIDDLEs terminate in A
- Folio-localized: Hyper-specialized discriminators for local registry organization

**Two vocabulary tracks in Currier A:**

| Track | MIDDLEs | Characteristics | Role |
|-------|---------|-----------------|------|
| **Pipeline-participating** | 268 (43.4%) | Standard prefixes, standard suffixes, broad folio spread | Flow through A→AZC→B |
| **Registry-internal** | 349 (56.6%) | ct-enriched, suffix-less, folio-localized | Stay in A registry |

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

The A∩B shared MIDDLE vocabulary (originally labeled "Pipeline-Participating") comprises two structurally distinct subclasses:

| Subclass | Count | % of Shared | Mechanism |
|----------|-------|-------------|-----------|
| **AZC-Mediated** | 154 | 57.5% | A→AZC→B constraint propagation |
| **B-Native Overlap (BN)** | 114 | 42.5% | B operational vocabulary with incidental A presence |

**Evidence:**
- Traced all 268 A∩B MIDDLEs through Currier A, AZC folios, and Currier B
- 114 MIDDLEs appear in A and B but **never** in any AZC folio
- Zero-AZC MIDDLEs show B-heavy frequency ratios (e.g., `eck` A=2, B=85; `ect` A=2, B=46)
- Pattern consistent with B-native origin, not A→B transmission

**AZC-Mediated substructure:**

| AZC Presence | Count | Mean B Folio Spread |
|--------------|-------|---------------------|
| Universal (10+ AZC folios) | 17 | 48.7 folios |
| Moderate (3-10 AZC folios) | 45 | 20.1 folios |
| Restricted (1-2 AZC folios) | 92 | 6.8 folios |

**B-Native Overlap characteristics:**
- Mean B folio spread: 4.0 folios (flat, AZC-independent)
- B-heavy (B > 2×A): 67 MIDDLEs (58.8%)
- A-heavy (A > 2×B): 12 MIDDLEs (10.5%)
- Execution-infrastructure vocabulary: boundary discriminators, stabilizers, orthographic variants

**Architectural implications:**
- Constraint inheritance (C468-C470) applies only to AZC-Mediated subclass
- Pipeline scope is narrower than "all A∩B shared" implies
- A's outbound vocabulary to pipeline is 154 MIDDLEs (25% of A vocabulary), not 268 (43.4%)

**Relationship to existing constraints:**
- Consistent with C384 (No Entry-Level A-B Coupling): BN MIDDLEs demonstrate statistical, not referential, sharing
- Consistent with C383 (Global Type System): Shared morphology ≠ shared function
- Refines C468-C470: Pipeline model preserved but now precisely scoped

**Terminology correction:**
The original "Pipeline-Participating" label is misleading. Recommended terminology:
- **AZC-Mediated Shared** (154): Genuine pipeline participation
- **B-Native Overlap / BN** (114): Domain overlap, not pipeline flow

**Complete A MIDDLE hierarchy:**
```
A MIDDLEs (617 total)
├── RI: Registry-Internal (349, 56.6%)
│     A-exclusive, instance discrimination, folio-localized
│
└── Shared with B (268, 43.4%)
    ├── AZC-Mediated (154, 25.0% of A vocabulary)
    │     A→AZC→B constraint propagation
    │     ├── Universal (17) - 10+ AZC folios
    │     ├── Moderate (45) - 3-10 AZC folios
    │     └── Restricted (92) - 1-2 AZC folios
    │
    └── B-Native Overlap (114, 18.5% of A vocabulary)
          Zero AZC presence, B-dominant frequency
          Execution-layer vocabulary with incidental A appearance
```

**Source:** A_RECORD_STRUCTURE_ANALYSIS phase (2026-01-20)
**External validation:** Reviewed by domain expert; confirmed as architecture-strengthening refinement that sharpens pipeline scope without contradiction.

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
- Respects C384 (no entry-level coupling): Analysis is aggregate/statistical, not entry-level
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

## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
