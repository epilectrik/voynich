# Phase QLA: Quire-Level Analysis

**Core Question:** How do structural boundaries (sections, A/B, regimes) align with physical quire boundaries?

**Answer:** Quires are ORGANIZATIONAL UNITS - sections, regimes, and vocabulary all show quire-level coherence

**Status:** CLOSED (4/5 tests show signal)

---

## Results Summary

| Test | Finding | Verdict |
|------|---------|---------|
| QLA-1 | 5 pure A, 3 pure B, 4 pure AZC, 6 mixed quires | **NULL** |
| QLA-2 | Section homogeneity 0.92 (4.3x random) | **SIGNAL** |
| QLA-3 | Regime clustering 2.20x within vs between quires | **SIGNAL** |
| QLA-4 | Vocabulary continuity 1.69x within quires (p<10^-243) | **SIGNAL** |
| QLA-5 | Boundary discontinuity 1.67x, 41% section changes | **SIGNAL** |

---

## Detailed Findings

### QLA-1: Currier A/B Quire Segregation

**Question:** Do Currier A and B segregate into different quires?

| Quire Type | Count | Examples |
|------------|-------|----------|
| Pure A | 5 | A, B, C, O, S |
| Pure B | 3 | M, N, T |
| Pure AZC | 4 | I, J, K, L |
| Mixed (A+B) | 6 | D, E, F, G, H, Q |

**Notable findings:**
- Quires I-L are **pure AZC** (no Currier A or B classification)
- Quire M is **pure B** (6,955 tokens, largest B quire)
- Quire T is **pure B** (10,680 tokens, section S)
- 6 quires show A/B mixing (27-73% ranges)

**Interpretation:** A/B separation is NOT purely quire-based. While 12 quires are "pure" (A, B, or AZC), 6 quires contain both A and B content. This is a **NULL** result for strict segregation but confirms quires have compositional tendencies.

---

### QLA-2: Section-Quire Alignment

**Question:** Do manuscript sections align with quire boundaries?

| Metric | Value |
|--------|-------|
| Single-section quires | 12/18 (67%) |
| Multi-section quires | 6/18 (33%) |
| Mean homogeneity | 0.923 |
| Expected (random) | 0.216 |
| Ratio | **4.3x** |

**Section distribution by quire:**
- Quire B-G: Pure section H (herbal)
- Quire K-L: Pure section Z (zodiac)
- Quire M: Pure section B (biological)
- Quire S: Pure section P (pharmaceutical)
- Quire T: Pure section S (stars/recipes)

**Interpretation:** Sections are strongly quire-aligned. This confirms and strengthens Constraint 156 ("Detected sections match codicology").

---

### QLA-3: Regime-Quire Association (Currier B only)

**Question:** Do control regimes cluster within quires?

| Metric | Value |
|--------|-------|
| Within-quire same-regime rate | 0.515 (280/544 pairs) |
| Between-quire same-regime rate | 0.234 (650/2777 pairs) |
| Ratio | **2.20x** |

**Notable quire-regime patterns:**
- Quire M: 17/20 folios are REGIME_1 (85% homogeneity)
- Quire G: 4/4 folios are REGIME_4 (100% homogeneity)
- Quire T: 13/23 folios are REGIME_1 (57% homogeneity)

**Interpretation:** Regimes are not randomly distributed - they cluster by quire. This suggests quires were organized by operational profile, not just content type.

---

### QLA-4: Vocabulary Continuity within Quires

**Question:** Do folios in the same quire share more vocabulary?

| Metric | Value |
|--------|-------|
| Within-quire pairs | 1,542 |
| Between-quire pairs | 23,658 |
| Within-quire mean Jaccard | 0.1015 |
| Between-quire mean Jaccard | 0.0601 |
| Ratio | **1.69x** |
| Mann-Whitney p-value | <10^-243 |

**Interpretation:** Massive vocabulary continuity effect. Folios in the same quire share 69% more vocabulary than folios in different quires. This is consistent with quires being composed/copied together.

---

### QLA-5: Quire Boundary Discontinuity

**Question:** Are there structural discontinuities at quire boundaries?

| Metric | Value |
|--------|-------|
| Adjacent pairs within quire | 207 |
| Adjacent pairs crossing boundary | 17 |
| Within-quire adjacent Jaccard | 0.1052 |
| Cross-boundary adjacent Jaccard | 0.0628 |
| Discontinuity ratio | **1.67x** |
| Section changes at boundaries | 7/17 (41%) |
| Language changes at boundaries | 7/17 (41%) |

**Interpretation:** Quire boundaries are **structural discontinuities**. Adjacent folios across quire boundaries are less similar than adjacent folios within quires. 41% of quire boundaries coincide with section or language changes.

---

## Synthesis

Quires are **organizational units**, not just physical bindings:

1. **Section coherence**: 4.3x more section-homogeneous than random
2. **Regime clustering**: 2.20x within-quire regime similarity
3. **Vocabulary continuity**: 1.69x within-quire vocabulary sharing
4. **Boundary discontinuities**: 1.67x vocabulary drop at boundaries

**Quire-level organization model:**
```
Quire = [Section] + [Regime tendency] + [Vocabulary cluster]
         67% pure    2.2x clustering     1.69x continuity
```

The one NULL result (QLA-1) shows A/B separation is NOT strictly quire-based - 6 quires contain both. But within those quires, there's still organizational structure.

---

## New Constraints

| # | Constraint | Evidence |
|---|------------|----------|
| 367 | Manuscript sections are QUIRE-ALIGNED: 12/18 quires are single-section, mean homogeneity 0.923 (4.3x random); strengthens Constraint 156 (QLA-2, Tier 2) |
| 368 | Control regimes CLUSTER within quires: within-quire same-regime rate 2.20x between-quire rate; quires were organized by operational profile (QLA-3, Tier 2) |
| 369 | Vocabulary shows QUIRE CONTINUITY: within-quire Jaccard 1.69x between-quire (p<10^-243); folios in same quire share vocabulary (QLA-4, Tier 2) |
| 370 | Quire boundaries are STRUCTURAL DISCONTINUITIES: 1.67x vocabulary drop, 41% section/language changes at boundaries (QLA-5, Tier 2) |

---

## Integration with Prior Findings

| Prior Constraint | QLA Finding | Integration |
|------------------|-------------|-------------|
| Constraint 156: Detected sections match codicology | QLA-2: 4.3x section-quire alignment | **STRENGTHENED** - quantified at 4.3x |
| Constraint 155: Piecewise-sequential geometry | QLA-5: Discontinuities at quire boundaries | **CONFIRMED** - boundaries are real |
| Constraint 361: Adjacent B folios share vocabulary | QLA-4: Within-quire 1.69x sharing | **COMPLEMENTARY** - quire effect + adjacency effect |

---

## What This Means

1. **Quires are not arbitrary** - physical bindings reflect organizational structure
2. **Composition was quire-aware** - vocabulary continuity suggests quires were composed/copied together
3. **Regimes have physical organization** - not just mathematical clustering
4. **The 15 punctuated transitions** (from Constraint 155) align with quire boundaries

---

## Codicological Implications

The Voynich manuscript's quire structure reflects its **logical organization**:

| Quire Block | Content | Character |
|-------------|---------|-----------|
| A-C | Pure Currier A, Section H | Herbal registry |
| D-G | Mixed A/B, Section H | Transitional herbal |
| H | Mixed, Sections H/T/C | Junction quire |
| I-L | Pure AZC, Sections A/Z/C | Astronomical/zodiac |
| M | Pure B, Section B | Biological procedures |
| N | B, Section C/T | Cosmological procedures |
| O | A, Sections H/P | Herbal/pharmaceutical |
| Q | Mixed A/B, Section H | Transitional |
| S | A, Section P | Pure pharmaceutical |
| T | Pure B, Section S | Recipe/stars procedures |

---

*Phase QLA CLOSED. 5 tests run, 4 SIGNAL, 1 NULL. Quires are organizational units with structural coherence.*
