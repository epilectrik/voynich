# C562: FLOW Role Structure

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> FLOW role (Classes 7, 30, 38, 40) contains 19 tokens producing 1078 occurrences (4.7% of corpus). FLOW is final-biased (17.5%) with internal hierarchy: Class 40 (59.7% final) > Class 38 (52.0%) > Class 30 (14.8%) > Class 7 (9.9%). Token "ary" is 100% line-final. FLOW shows PHARMA enrichment (1.38x), BIO depletion (0.83x), and REGIME_1 depletion (0.91x) - inverse of ENERGY pattern. Morphologically unified by ar/al/da prefixes.

---

## Evidence

**Test:** `phases/CLASS_SEMANTIC_VALIDATION/scripts/flow_role_analysis.py`

### FLOW Class Composition

| Class | Tokens | Examples |
|-------|--------|----------|
| 7 | 2 | al, ar |
| 30 | 5 | dar, dal, dam, dain, dair |
| 38 | 6 | aral, aram, arol, arody, aldy, daim |
| 40 | 6 | aly, ary, daly, dary, dan, daiir |

### Top FLOW Tokens by Frequency

| Token | Class | Count | Corpus Rank |
|-------|-------|-------|-------------|
| ar | 7 | 248 | #12 |
| dar | 30 | 188 | #15 |
| al | 7 | 186 | #16 |
| dal | 30 | 130 | #24 |
| dain | 30 | 113 | #31 |

### Positional Hierarchy

| Class | Initial% | Final% | Bias |
|-------|----------|--------|------|
| 7 (al, ar) | 0.5% | 9.9% | Final |
| 30 (dar, dal...) | 15.7% | 14.8% | Neutral |
| 38 (aral...) | 0.0% | **52.0%** | Strong final |
| 40 (aly, ary...) | 4.2% | **59.7%** | Strong final |

**FLOW overall:** 8.1% initial, 17.5% final

### Class 40 Token Analysis

| Token | Total | Initial% | Final% |
|-------|-------|----------|--------|
| ary | 16 | 0.0% | **100.0%** |
| dary | 13 | 0.0% | 61.5% |
| aly | 17 | 0.0% | 52.9% |
| daly | 17 | 0.0% | 52.9% |
| dan | 2 | 0.0% | 50.0% |
| daiir | 7 | 42.9% | 0.0% |

**ary is a pure line-closer** (100% final, 0% initial).

### REGIME Distribution

| REGIME | FLOW % | Enrichment |
|--------|--------|------------|
| REGIME_1 | 4.2% | **0.91x** |
| REGIME_2 | 5.3% | 1.13x |
| REGIME_3 | 4.6% | 0.99x |
| REGIME_4 | 4.6% | 0.99x |

### Section Distribution

| Section | FLOW % | Enrichment |
|---------|--------|------------|
| PHARMA | 6.4% | **1.38x** |
| HERBAL | 6.0% | 1.28x |
| RECIPE | 4.8% | 1.02x |
| BIO | 3.9% | **0.83x** |

### ENERGY/FLOW Ratio by REGIME

| REGIME | ENERGY | FLOW | EN/FL Ratio |
|--------|--------|------|-------------|
| REGIME_1 | 2490 | 329 | **7.57** |
| REGIME_2 | 1229 | 331 | 3.71 |
| REGIME_3 | 403 | 80 | 5.04 |
| REGIME_4 | 1610 | 338 | 4.76 |

REGIME_1 has 2x higher EN/FL ratio than REGIME_2.

### Morphological Pattern

| Class | PREFIX pattern |
|-------|----------------|
| 7 | None (pure MIDDLE: al, ar) |
| 30 | da- (dar, dal, dam, dain, dair) |
| 38 | ar-/al-/da- (aral, aram, aldy, daim) |
| 40 | al-/ar-/da- (aly, ary, daly, dary) |

**Common elements:** ar, al, da throughout.

### Self-Chaining

| Class | Chains (2+) | Chain Rate |
|-------|-------------|------------|
| 7 | 34 | **16.1%** |
| 30 | 9 | 3.4% |
| 38 | 0 | 0.0% |
| 40 | 0 | 0.0% |

Class 7 (al, ar) self-chains at similar rate to Class 9 (16.2%).

---

## Interpretation

### FLOW as ENERGY Inverse

FLOW shows inverted patterns relative to ENERGY:

| Dimension | ENERGY | FLOW |
|-----------|--------|------|
| Position | Medial (0.45x initial) | Final (17.5%) |
| REGIME_1 | Enriched (1.26x) | Depleted (0.91x) |
| BIO | Enriched (1.72x) | Depleted (0.83x) |
| PHARMA | Depleted (Class 33: 0.20x) | Enriched (1.38x) |

This supports thermal/flow anticorrelation from C551.

### Class Hierarchy

FLOW has internal functional hierarchy:
1. **Class 7 (al, ar):** Atomic flow markers, self-chaining, medial-to-final
2. **Class 30 (da-family):** Position-neutral, line-initial capable
3. **Class 38/40:** Strong line-closers (52-60% final)

### ary as Pure Terminator

Token "ary" at 100% line-final is a **pure closure signal**, distinct from other FLOW tokens. Compare to ol (9.5% final) from CORE_CONTROL.

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C546 | Confirmed - Class 40 safe flow operator, 59.7% final |
| C551 | Extended - FLOW/ENERGY anticorrelation quantified |
| C556 | Complementary - FLOW final 17.5% vs ENERGY medial |
| C559 | Parallel - Class 7 self-chains (16.1%) like Class 9 (16.2%) |

---

## Provenance

- **Phase:** CLASS_SEMANTIC_VALIDATION
- **Date:** 2026-01-25
- **Script:** flow_role_analysis.py

---

## Navigation

<- [C561_class9_or_aiin_bigram.md](C561_class9_or_aiin_bigram.md) | [INDEX.md](INDEX.md) ->
