# Phase BVP: B-Folio Vocabulary Patterns

**Core Question:** How do B folios relate to each other vocabularily?

**Answer:** B folios show STRUCTURED vocabulary patterns - sequential, regime-based, and with identifiable hubs

**Status:** CLOSED (3/4 tests show signal)

---

## Results Summary

| Test | Finding | Verdict |
|------|---------|---------|
| BVP-1 | Adjacent folios share 1.30x more vocabulary (p<0.000001, d=0.76) | **SIGNAL** |
| BVP-2 | Same-regime folios share 1.29x more vocabulary (p=0.002) | **SIGNAL** |
| BVP-3 | Stability/LINK profiles show ratio ~1.05 (not significant) | NULL |
| BVP-4 | 3 outliers detected, 3,368 unique tokens (68% of vocabulary) | **SIGNAL** |

---

## Detailed Findings

### BVP-1: Adjacent vs Non-Adjacent Vocabulary Sharing

**Question:** Do consecutive B folios share more vocabulary than random pairs?

| Metric | Value |
|--------|-------|
| Adjacent pairs | 81 |
| Non-adjacent samples | 981 |
| Adjacent mean Jaccard | 0.138 |
| Non-adjacent mean Jaccard | 0.107 |
| Ratio | **1.30x** |
| Mann-Whitney p-value | <0.000001 |
| Effect size (Cohen's d) | **0.757** |

**Interpretation:** Adjacent B folios share significantly more vocabulary than random pairs. This indicates sequential composition or reading pattern - operators would encounter familiar vocabulary when progressing through adjacent folios.

---

### BVP-2: Regime-Based Vocabulary Clustering

**Question:** Do programs in the same control regime share more vocabulary?

| Regime | Folios |
|--------|--------|
| REGIME_1 | 31 |
| REGIME_2 | 10 |
| REGIME_3 | 16 |
| REGIME_4 | 25 |

| Metric | Value |
|--------|-------|
| Within-regime pairs | 930 |
| Between-regime pairs | 2,391 |
| Within-regime mean | 0.126 |
| Between-regime mean | 0.097 |
| Ratio | **1.29x** |
| Permutation p-value | 0.002 |

**Interpretation:** Regimes are not just operationally defined (by control parameters) but vocabularily distinct. Each regime has its own vocabulary fingerprint. This suggests regimes reflect underlying procedural categories, not just mathematical clustering artifacts.

---

### BVP-3: Stability Profile Vocabulary Clustering

**Question:** Do folios with similar stability or LINK profiles share vocabulary?

| Profile Type | Within/Between Ratio |
|--------------|---------------------|
| Stability quartiles | 1.059 |
| LINK profiles | 1.050 |

**Interpretation:** Neither stability profile nor LINK density predicts vocabulary sharing. This is a **null result** - vocabulary is independent of operational intensity. Stability and waiting are emergent from token patterns, not from selecting different vocabularies.

---

### BVP-4: Vocabulary Uniqueness Distribution

**Question:** How is vocabulary distributed across folios? Are there vocabulary "hubs"?

| Metric | Value |
|--------|-------|
| Folios analyzed | 82 |
| Total unique tokens | 4,946 |
| Core tokens (in ≥50% of folios) | 41 |
| Unique tokens (in only 1 folio) | 3,368 (68%) |
| Mean vocabulary size | 180.6 |
| Vocabulary size std | 90.3 |

**Outliers detected:**
- **f113r**: Large vocabulary (z > 2)
- **f66v, f105v**: High uniqueness (z > 2)

**Interpretation:** Vocabulary distribution is hub-peripheral:
- Only 41 tokens appear in ≥50% of folios (core vocabulary)
- 3,368 tokens (68%) appear in only one folio (highly specialized)
- Three folios are vocabulary outliers - may serve special functions

---

## Synthesis

B folios are **vocabularily structured** across multiple dimensions:

1. **Sequential continuity**: Adjacent folios share more vocabulary (d=0.76), supporting compositional or reading order

2. **Regime fingerprints**: Each of the 4 regimes has distinct vocabulary (1.29x within/between), suggesting regimes are categorical, not just parametric

3. **Not operational**: Stability and LINK profiles don't predict vocabulary - these are emergent from token patterns, not from vocabulary selection

4. **Hub-peripheral structure**: 41 core tokens vs 3,368 folio-unique tokens; 3 vocabulary outliers detected

**Structural model update:**
```
B Vocabulary Structure:
├── Core vocabulary (41 tokens, universal)
├── Regime-specific vocabulary (4 clusters)
├── Sequential locality (adjacent sharing)
└── Folio-unique vocabulary (3,368 tokens)
```

---

## New Constraints

| # | Constraint | Evidence |
|---|------------|----------|
| 361 | Adjacent B folios share 1.30x more vocabulary than non-adjacent (p<0.000001, d=0.76); supports sequential composition/reading (BVP-1, Tier 2) |
| 362 | Control regimes (REGIME_1-4) have distinct vocabulary fingerprints: within-regime 1.29x more similar than between-regime (p=0.002); regimes are categorical not just parametric (BVP-2, Tier 2) |
| 363 | Vocabulary is INDEPENDENT of stability and LINK profiles (ratio ~1.05); operational intensity emerges from token patterns, not vocabulary selection (BVP-3, Tier 2) |
| 364 | B vocabulary is hub-peripheral: 41 core tokens (in ≥50% of folios), 3,368 unique tokens (68%, in only 1 folio); 3 vocabulary outliers (f113r, f66v, f105v) (BVP-4, Tier 2) |

---

## Integration with Prior Findings

| Prior Constraint | BVP Finding | Integration |
|------------------|-------------|-------------|
| Constraint 336: Adjacent B share more A-vocab | BVP-1: Also share more B-vocab | **CONFIRMED** - both layers show sequential coherence |
| Constraint 179-180: 4 regimes exist | BVP-2: Regimes have vocabulary fingerprints | **ENHANCED** - regimes are vocabularily distinct |
| Constraint 341: HT density varies by waiting profile | BVP-3: Vocabulary independent of waiting | **COMPLEMENTARY** - HT tracks waiting, vocabulary doesn't |

---

## What This Means

1. **Operators could learn regime-specific vocabulary** - each regime uses somewhat different tokens
2. **Sequential reading is supported** - adjacent folios share vocabulary, reducing cognitive load
3. **Core vocabulary is minimal** - only 41 tokens are truly universal across B
4. **Most vocabulary is specialized** - 68% appears in only one folio, reflecting diverse procedural contexts

---

## Outlier Documentation

Three vocabulary outliers were detected in BVP-4. Detailed analysis follows.

### f113r - Large Vocabulary Outlier

**Why outlier:** Vocabulary size z = +2.09 (369 tokens vs median 172)

| Property | Value | Notes |
|----------|-------|-------|
| Section | S | |
| Regime | REGIME_1 | Standard regime |
| Token count | 518 | Also above median (304) |
| Lines | 51 | Dense folio |
| LINK density | 0.400 | Moderate-high |
| Terminal state | STATE-C | Normal convergence |
| Unique tokens | 118 (32.0%) | Also high uniqueness |
| Rare tokens (<=5 folios) | 196 (53.1%) | Over half vocabulary is rare |

**Interpretation:** f113r is a **long, vocabulary-dense folio** in Section S. Its large vocabulary is partly explained by length (518 tokens), but it also has high uniqueness (32.0%). This folio uses 369 distinct tokens where a typical folio uses 172 - suggesting either:
1. A specialized procedure requiring diverse terminology
2. Lower repetition rate (less reuse of standard patterns)
3. A compilation of multiple sub-procedures

**Sample unique tokens:** `qoteoor`, `yraiin`, `lkeches`, `shoaiin`, `tchoarorshy`

---

### f66v - High Uniqueness Outlier

**Why outlier:** Uniqueness z = +2.48 (36.6% vs median 21.2%)

| Property | Value | Notes |
|----------|-------|-------|
| Section | H | |
| Regime | REGIME_4 | High-intensity regime |
| Token count | 113 | Below median |
| Vocabulary size | 93 | Below median |
| Lines | 13 | Short folio |
| LINK density | 0.376 | Moderate |
| Terminal state | STATE-C | Normal convergence |
| Unique tokens | 34 (36.6%) | **Highest in corpus** |
| Stability | 0.273 | Low stability |
| Risk | 0.517 | Moderate-high risk |

**Interpretation:** f66v is a **short, highly specialized folio** in Section H. Despite having below-median vocabulary size (93), over a third of its tokens appear NOWHERE ELSE in the corpus. Combined with:
- REGIME_4 (high-intensity)
- Low stability (0.273)
- Moderate-high risk (0.517)

This suggests f66v represents a **specialized high-intensity procedure** with unique terminology not shared with other programs.

**Sample unique tokens:** `shckhhd`, `qokeos`, `yteeod`, `opch`, `chekeor`, `ychoopy`

---

### f105v - High Uniqueness Outlier

**Why outlier:** Uniqueness z = +2.05 (33.9% vs median 21.2%)

| Property | Value | Notes |
|----------|-------|-------|
| Section | S | |
| Regime | REGIME_2 | Moderate regime |
| Token count | 390 | Above median |
| Vocabulary size | 283 | Above median |
| Lines | 38 | |
| LINK density | 0.536 | **High waiting** |
| Terminal state | STATE-C | Normal convergence |
| Unique tokens | 96 (33.9%) | Second-highest in corpus |
| Stability | 0.614 | **High stability** |
| Risk | 0.276 | Low risk |

**Interpretation:** f105v is a **long, high-waiting, high-stability folio** in Section S. Its profile is unusual:
- High LINK density (0.536) = lots of waiting
- High stability (0.614) = conservative operation
- Low risk (0.276) = minimal hazard exposure
- Yet 34% unique vocabulary

This suggests f105v represents a **specialized conservative procedure** - perhaps a delicate or valuable process requiring:
1. Extended waiting periods
2. Terminology specific to this material/process
3. Low-risk operational profile despite specialized vocabulary

**Sample unique tokens:** `lfcheedy`, `ofaiis`, `aiil`, `qoeedeody`, `polairy`, `ysheod`

---

## Outlier Synthesis

| Folio | Primary Character | Section | Regime | Key Insight |
|-------|-------------------|---------|--------|-------------|
| f113r | Large vocabulary | S | R1 | Dense, diverse procedure |
| f66v | Highest uniqueness | H | R4 | Specialized high-intensity |
| f105v | High uniqueness + waiting | S | R2 | Specialized conservative |

**Common patterns:**
- All three have STATE-C terminal state (normal convergence)
- f113r and f105v are both in Section S
- f66v and f105v both have highly specialized vocabulary despite different operational profiles

**What this suggests:**
1. Some procedures require **specialized terminology** not shared with others
2. Specialization correlates with **different operational profiles**:
   - f66v: Specialized + high-intensity + risky
   - f105v: Specialized + conservative + careful
   - f113r: Specialized + diverse + long
3. Section S contains both vocabulary outliers (f113r, f105v) - may contain more procedural diversity

---

*Phase BVP CLOSED. 4 tests run, 3 SIGNAL, 1 NULL. B folios show structured vocabulary patterns.*
