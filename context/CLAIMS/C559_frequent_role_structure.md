# C559: FREQUENT Role Structure

**Tier:** 2 | **Status:** SUPERSEDED | **Scope:** B

> **SUPERSEDED:** This constraint used incorrect FQ membership {9, 20, 21, 23} from CLASS_SEMANTIC_VALIDATION scripts. Classes 20 and 21 are AX per C563. Correct FQ membership is {9, 13, 14, 23} per ICC (C121). See **C583** (FQ Definitive Census) and **C587** (FQ Internal Differentiation) for corrected analysis. Downstream constraints C550, C551, C552, C556 are flagged for re-verification with corrected membership (see C592).

---

## Statement

> FREQUENT role (Classes 9, 20, 21, 23) captures morphologically minimal tokens with final-position bias. 35 token types produce 1301 occurrences (5.6% of corpus). Role is final-biased (19.6% final, 3.6x ENERGY), HERBAL-enriched (1.62x), BIO-depleted (0.85x). Class 9 (aiin, o, or) is exceptional: medial-biased (4.9% final), self-chaining (16.2%), distinct from other FQ classes.

---

## Evidence

**Test:** `phases/CLASS_SEMANTIC_VALIDATION/scripts/frequent_role_analysis.py`

### FREQUENT Class Composition

| Class | Tokens | Examples |
|-------|--------|----------|
| 9 | 3 | aiin, o, or |
| 20 | 15 | kal, pol, rol, tor, ldy... |
| 21 | 10 | lo, ty, key, ral, ram... |
| 23 | 7 | d, l, r, s, y, am, dy |

### Top FREQUENT Tokens by Frequency

| Token | Class | Count | Corpus Rank |
|-------|-------|-------|-------------|
| aiin | 9 | 351 | #4 |
| or | 9 | 250 | #10 |
| dy | 23 | 109 | #33 |
| y | 23 | 66 | #52 |
| am | 23 | 55 | #63 |

### Positional Patterns by Class

| Class | Total | Initial% | Final% |
|-------|-------|----------|--------|
| 9 | 630 | 3.2% | **4.9%** |
| 20 | 198 | 16.2% | **28.3%** |
| 21 | 111 | 4.5% | **39.6%** |
| 23 | 362 | 12.2% | **34.3%** |

Class 9 is NOT final-biased (4.9%); Classes 20, 21, 23 are strongly final-biased (28-40%).

### Role Position Comparison

| Role | Initial% | Final% |
|------|----------|--------|
| EN | 4.9% | 5.4% |
| FL | 8.1% | 17.5% |
| **FQ** | 7.8% | **19.6%** |

FREQUENT has highest final rate among semantic roles.

### Self-Chaining (Repetition)

| Class | Chains (2+) | In Chains | Chain Rate |
|-------|-------------|-----------|------------|
| 9 | 48 | 102 | **16.2%** |
| 20 | 4 | 8 | 4.0% |
| 21 | 0 | 0 | 0.0% |
| 23 | 4 | 9 | 2.5% |

Class 9 uniquely self-chains (aiin-aiin sequences).

### REGIME Distribution

| REGIME | FREQUENT % | Enrichment |
|--------|------------|------------|
| REGIME_1 | 4.7% | 0.83x |
| REGIME_2 | 6.5% | 1.16x |
| REGIME_3 | 5.7% | 1.01x |
| REGIME_4 | 5.9% | 1.05x |

REGIME_1 depleted (inverse of ENERGY enrichment).

### Section Distribution

| Section | FREQUENT % | Enrichment |
|---------|------------|------------|
| HERBAL | 9.1% | **1.62x** |
| BIO | 4.8% | 0.85x |
| PHARMA | 7.4% | 1.31x |
| RECIPE | 5.3% | 0.94x |

HERBAL enriched, BIO depleted (inverse of ENERGY pattern from C552).

---

## Interpretation

### Morphological Minimality

FREQUENT tokens are characteristically SHORT:
- Class 23: single characters (d, l, r, s, y) or minimal (am, dy)
- Class 9: simple vowel-based (aiin, o, or)
- Contrast with ENERGY: complex forms (qokeedy, chedy, etc.)

### Functional Hypothesis

FREQUENT may encode:
- **Grammatical markers** rather than semantic content
- **Closure signals** (final position bias)
- **Iteration markers** (Class 9 self-chaining)

### Class 9 Exception

Class 9 (aiin, o, or) differs from other FQ:
1. NOT final-biased (4.9% vs 28-40%)
2. Self-chains at 16.2% rate
3. Highest frequency (aiin #4, or #10 in corpus)

Class 9 may serve a distinct function: **continuation/iteration** rather than **closure**.

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C550 | Extended - FQ self-chains at 2.38x (highest role) |
| C551 | Contextualized - FQ depleted in REGIME_1 like FLOW |
| C552 | Complementary - FQ enriched in HERBAL (opposite of ENERGY in BIO) |
| C556 | Extended - FQ final preference quantified (19.6%) |

---

## Provenance

- **Phase:** CLASS_SEMANTIC_VALIDATION
- **Date:** 2026-01-25
- **Script:** frequent_role_analysis.py

---

## Navigation

<- [C558_singleton_class_structure.md](C558_singleton_class_structure.md) | [INDEX.md](INDEX.md) ->
