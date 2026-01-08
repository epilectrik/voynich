# Currier A Constraints (C224-C299)

**Scope:** Currier A disjunction, schema, multiplicity, morphology
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

---

## Navigation

← [INDEX.md](INDEX.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
