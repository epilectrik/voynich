# HT-THREAD: Global Human Track Threading Analysis
## Expert Report

**Analysis Date:** 2026-01-10
**Analyst:** Claude (Opus 4.5)
**Status:** COMPLETE
**Constraint Series:** C450-C453 (proposed)

---

## 1. Executive Summary

This investigation mapped the **global threading behavior** of the Human Track (HT) across the entire Voynich Manuscript. Prior work had characterized HT locally within each Currier system (A, B, AZC), but no manuscript-wide analysis existed.

### Principal Findings

1. **HT is a single unified notation layer** - The same 19 HT prefixes appear across all three systems with near-complete vocabulary overlap (Jaccard ≥ 0.947).

2. **HT density is quire-clustered** - HT is not uniformly distributed but organized at codicological boundaries (Kruskal-Wallis H=47.20, p<0.0001, η²=0.150).

3. **HT density is system-stratified** - Currier A (0.170) > AZC (0.162) > Currier B (0.149), with A vs B significantly different (p=0.0043 after Bonferroni correction).

4. **HT shows stronger adjacency clustering than Currier A** - Adjacent folios share 1.69x more HT vocabulary than non-adjacent folios (p<0.0001), exceeding Currier A's 1.31x enrichment (C424).

### Implication

HT represents a **continuous orientation layer** that threads through the entire manuscript, maintaining vocabulary unity while varying in density based on (a) codicological structure and (b) system context. This is consistent with HT serving as "waiting notation" or "placeholder markers" applied during a unified production process.

---

## 2. Background and Motivation

### 2.1 Prior HT Characterization

The Human Track had been characterized locally within each system:

| System | HT Behavior | Source |
|--------|-------------|--------|
| Currier A | Entry-boundary aligned, seam-avoiding | C419 |
| Currier B | Waiting-profile correlated, phase-synchronized | C341, C348 |
| AZC | Placement-synchronous | Phase analysis |

Additionally, HT was known to be:
- **Non-operational** (C404-406) - Not part of the control grammar
- **System-conditioned** - Varies by Currier system
- **Morphologically modular** - PREFIX + CORE + SUFFIX structure
- **80.7% section-exclusive** (C167)
- **Complete hazard avoider** (C166, C169, C217)

### 2.2 Gap in Understanding

No prior analysis addressed:
- Global HT density distribution across all 227 folios
- Whether HT follows codicological structure (quires)
- How HT behaves at system boundaries (A↔B, B↔AZC)
- Whether HT vocabulary crosses system boundaries (like C424 found for Currier A)

### 2.3 Research Questions

1. Is HT uniformly distributed or clustered?
2. Does HT density correlate with quire structure?
3. Does HT show discontinuity at system boundaries?
4. Do HT vocabulary types cross system boundaries?
5. Does HT exhibit adjacency clustering like Currier A?

---

## 3. Methodology

### 3.1 Data Source

- **Primary corpus:** `data/transcriptions/interlinear_full_words.txt`
- **Folios analyzed:** 227
- **System distribution:** Currier A (114), Currier B (83), AZC (30)
- **Total tokens:** ~37,000

### 3.2 HT Classification

Tokens were classified as HT based on the established 19-prefix vocabulary:

```
HT_PREFIXES = {
    'yk', 'op', 'yt', 'sa', 'so', 'ka', 'dc', 'pc',
    'do', 'ta', 'ke', 'al', 'po', 'ko', 'yd', 'ysh',
    'ych', 'kch', 'ks'
}
```

A token is classified as HT if it begins with any of these prefixes (matched longest-first to handle overlapping prefixes like 'y' vs 'yk').

### 3.3 System Classification

Folios were classified into Currier A, B, or AZC based on the `language` column in the transcription data:
- `language='A'` → Currier A
- `language='B'` → Currier B
- `language='NA'` → AZC (Astronomical/Zodiac/Cosmological)

For folios with mixed content, majority voting was applied.

### 3.4 Analysis Phases

| Phase | Analysis | Method |
|-------|----------|--------|
| 1 | Per-folio feature extraction | HT density, prefix distribution, positional rates |
| 2 | Distribution analysis | Runs test, autocorrelation, quire effects |
| 3 | Codicological alignment | Kruskal-Wallis by quire, within/between variance |
| 4 | Cross-system threading | Boundary discontinuity, vocabulary Jaccard |
| 5 | Adjacency patterns | Adjacent vs non-adjacent similarity, permutation test |
| 6 | Synthesis | Model construction, constraint formulation |

---

## 4. Detailed Findings

### 4.1 Phase 1: Per-Folio Features

**Output:** `results/ht_folio_features.json`

For each of 227 folios, we computed:

| Feature | Description |
|---------|-------------|
| `n_tokens` | Total tokens on folio |
| `n_ht` | HT token count |
| `ht_density` | HT / total tokens |
| `ht_unique_types` | Unique HT types |
| `ht_ttr` | HT type-token ratio |
| `ht_prefix_dist` | Distribution over 19 prefixes |
| `line_initial_rate` | % HT at line starts |
| `line_final_rate` | % HT at line ends |
| `system` | A / B / AZC |
| `quire` | Codicological quire (A-T) |

**Summary statistics:**

| Metric | Value |
|--------|-------|
| Mean HT density | 0.162 |
| Std HT density | 0.055 |
| Min HT density | 0.000 (f116v) |
| Max HT density | 0.333 (f65r) |

### 4.2 Phase 2: Distribution Analysis

**Output:** `results/ht_distribution_analysis.json`

#### 4.2.1 Runs Test for Randomness

The Wald-Wolfowitz runs test assesses whether HT density sequences are random or clustered.

| Statistic | Value |
|-----------|-------|
| Observed runs | 84 |
| Expected runs | 114.5 |
| Z-score | -5.66 |
| P-value | < 0.0001 |
| **Verdict** | **CLUSTERED** |

HT density is significantly non-random, with fewer runs than expected indicating spatial clustering.

#### 4.2.2 Autocorrelation Analysis

| Lag | Autocorrelation | Interpretation |
|-----|-----------------|----------------|
| 1 | 0.298 | Moderate positive (adjacent folios similar) |
| 2 | 0.201 | Weak positive |
| 3 | 0.156 | Weak positive |

Adjacent folios show similar HT densities, decaying with distance.

#### 4.2.3 System Differences

| System | Mean HT Density | Std | N |
|--------|-----------------|-----|---|
| Currier A | 0.170 | 0.049 | 114 |
| Currier B | 0.149 | 0.055 | 83 |
| AZC | 0.162 | 0.064 | 30 |

Kruskal-Wallis test: H=7.79, p=0.020 (significant)

Pairwise comparisons (Mann-Whitney U with Bonferroni correction α=0.0167):
- A vs B: p=0.0043 **significant**
- A vs AZC: p=0.489 (not significant)
- B vs AZC: p=0.372 (not significant)

### 4.3 Phase 3: Quire-Level Analysis

**Output:** Integrated into `results/ht_distribution_analysis.json`

#### 4.3.1 Quire Effect

| Statistic | Value |
|-----------|-------|
| Kruskal-Wallis H | 47.20 |
| P-value | 0.000063 |
| Eta-squared (η²) | 0.150 |
| **Verdict** | **SIGNIFICANT QUIRE EFFECT** |

The eta-squared of 0.150 indicates a **moderate effect size** - quire membership explains approximately 15% of HT density variance.

#### 4.3.2 Quire Rankings

**High HT density quires:**
| Quire | Mean HT Density |
|-------|-----------------|
| G | 0.193 |
| B | 0.189 |
| I | 0.186 |

**Low HT density quires:**
| Quire | Mean HT Density |
|-------|-----------------|
| M | 0.111 |
| K | 0.126 |
| T | 0.138 |

#### 4.3.3 Position Gradient

| Test | Result |
|------|--------|
| Correlation (position vs density) | r = -0.150 |
| Verdict | No significant linear gradient |

HT density does not systematically increase or decrease through the manuscript.

### 4.4 Phase 4: Cross-System Threading

**Output:** `results/ht_cross_system_analysis.json`

#### 4.4.1 System Boundaries Identified

30 system transitions were identified across the manuscript:
- A→B: 12 transitions
- B→A: 11 transitions
- B→AZC: 3 transitions
- AZC→B: 2 transitions
- A→AZC: 1 transition
- AZC→A: 1 transition

#### 4.4.2 Boundary Discontinuity Test

We compared HT density changes at system boundaries vs within-system adjacent folios:

| Measure | Value |
|---------|-------|
| Mean boundary change | 0.061 |
| Mean within-system change | 0.052 |
| Mann-Whitney U | 3491 |
| P-value | 0.049 |
| Effect size (r) | -0.187 |
| **Verdict** | **DISCONTINUOUS** |

HT density changes **more** at system boundaries than within systems, though the effect is modest.

#### 4.4.3 Vocabulary Crossing

We computed Jaccard similarity of HT prefix vocabularies between systems:

| Comparison | Jaccard | Overlap | Interpretation |
|------------|---------|---------|----------------|
| A ↔ B | **1.000** | 19/19 | Complete overlap |
| A ↔ AZC | 0.947 | 18/19 | Near-complete |
| B ↔ AZC | 0.947 | 18/19 | Near-complete |

**Key insight:** HT uses the **same prefix vocabulary** across all systems. The single missing prefix in AZC is likely due to sample size (AZC has only 30 folios vs 114 for A and 83 for B).

#### 4.4.4 Prefix Usage by System

| System | Top 3 Prefixes (rate) |
|--------|----------------------|
| Currier A | yk (0.116), do (0.113), yt (0.102) |
| Currier B | sa (0.109), al (0.105), yk (0.090) |
| AZC | yk (0.182), al (0.181), yt (0.135) |

While the vocabulary is unified, **prefix distribution varies by system**. This is consistent with HT being a single notation system used differently in different contexts.

### 4.5 Phase 5: Adjacency Analysis

**Output:** `results/ht_adjacency_analysis.json`

#### 4.5.1 Adjacent vs Non-Adjacent Similarity

We computed Jaccard similarity of HT vocabulary between adjacent folios (in manuscript order) vs non-adjacent folios:

| Measure | Adjacent | Non-Adjacent |
|---------|----------|--------------|
| Mean Jaccard | 0.0611 | 0.0361 |
| Std | 0.0511 | 0.0344 |
| N pairs | 225 | 492 |

#### 4.5.2 Enrichment Ratio

| Statistic | Value |
|-----------|-------|
| Enrichment ratio | **1.69x** |
| Permutation test p-value | **< 0.0001** |
| **Verdict** | **SIGNIFICANT ADJACENCY CLUSTERING** |

Adjacent folios share 69% more HT types than non-adjacent folios.

#### 4.5.3 Comparison to C424 (Currier A Adjacency)

| Analysis | Enrichment | P-value |
|----------|------------|---------|
| C424 (Currier A vocabulary) | 1.31x | < 0.000001 |
| HT vocabulary | **1.69x** | < 0.0001 |

**HT shows STRONGER adjacency clustering than Currier A vocabulary.**

This suggests HT was applied in continuous production sessions, with scribes maintaining vocabulary consistency across adjacent folios.

---

## 5. Proposed Constraints

Based on these findings, we propose 4 new constraints in the C450-C453 series:

### C450: HT Quire Clustering

**Tier:** 2 | **Status:** PROPOSED

> HT density exhibits significant quire-level clustering (Kruskal-Wallis H=47.20, p<0.0001, η²=0.150). HT is not uniformly distributed across the manuscript but organized at codicological boundaries.

**Evidence:**
- Runs test: 84 runs observed vs 114.5 expected (p<0.0001)
- Quire variance: η² = 0.150 (moderate effect)
- High quires: G (0.193), B (0.189); Low quires: M (0.111), K (0.126)

**Interpretation:** HT application was sensitive to quire boundaries, suggesting quires were treated as production units.

---

### C451: HT System Stratification

**Tier:** 2 | **Status:** PROPOSED | **Extends:** C341

> HT density is system-conditioned: Currier A (0.170) > AZC (0.162) > Currier B (0.149), with A vs B significantly different (Mann-Whitney p=0.0043 after Bonferroni correction).

**Evidence:**
- Kruskal-Wallis H=7.79, p=0.020
- A vs B: p=0.0043 (Bonferroni threshold: 0.0167)
- Consistent with HT as "waiting notation" - A has more waiting-heavy registry operations

**Interpretation:** HT density reflects functional differences between systems, not arbitrary variation.

---

### C452: HT Unified Prefix Vocabulary

**Tier:** 2 | **Status:** PROPOSED | **Refines:** C347

> HT prefix vocabulary is unified across all three systems (A, B, AZC) with near-complete overlap (Jaccard ≥ 0.947). However, HT density is discontinuous at system boundaries (p=0.049). HT is a SINGLE notation layer that varies in DENSITY, not VOCABULARY, across systems.

**Evidence:**
- A-B prefix overlap: Jaccard = 1.000 (complete)
- A-AZC prefix overlap: Jaccard = 0.947
- B-AZC prefix overlap: Jaccard = 0.947
- Boundary discontinuity: p=0.049

**Interpretation:** HT was a unified notation system applied throughout the manuscript, with context-dependent frequency modulation.

---

### C453: HT Adjacency Clustering

**Tier:** 2 | **Status:** PROPOSED | **Parallels:** C424

> HT vocabulary exhibits significant adjacency clustering (1.69x enrichment, p<0.0001), STRONGER than Currier A adjacency (1.31x per C424). Adjacent folios share more HT types than non-adjacent folios.

**Evidence:**
- Mean adjacent similarity: 0.0611
- Mean non-adjacent similarity: 0.0361
- Enrichment ratio: 1.69x
- Permutation test: p<0.0001

**Interpretation:** HT was produced in continuous sessions, with scribes maintaining vocabulary continuity across adjacent folios. This is stronger than the operational vocabulary continuity in Currier A.

---

## 6. Threading Model

### 6.1 Visual Model

```
MANUSCRIPT STRUCTURE
====================
       |<-------- Quire A -------->|<-------- Quire B -------->|
       +----+----+----+----+----+----+----+----+----+----+----+
       | A  | A  | B  | B  | B  | A  | A  | B  | B  | B  | AZC|
       +----+----+----+----+----+----+----+----+----+----+----+
HT     |####|####|##  |##  |##  |####|####|##  |##  |##  |### |
DENSITY|HIGH|HIGH|MED |MED |MED |HIGH|HIGH|MED |MED |MED |MED |
       +----+----+----+----+----+----+----+----+----+----+----+
                  ^                        ^
                  |                        |
              System boundary         System boundary
              (density shift)         (density shift)

LEGEND:
  ####  = High HT density (Currier A)
  ##    = Medium HT density (Currier B)
  ###   = Variable HT density (AZC)
```

### 6.2 Threading Behavior

1. **Quire-level clustering:** HT density clusters at quire boundaries (codicological production unit)
2. **System-boundary discontinuity:** HT density shifts at A/B/AZC transitions
3. **Vocabulary continuity:** Same 19 prefixes used everywhere
4. **Adjacency clustering:** Strong vocabulary overlap in adjacent folios (production sessions)

### 6.3 Architectural Integration

The 4-layer model remains valid, with HT now better characterized:

| Layer | System | Organization | This Analysis |
|-------|--------|--------------|---------------|
| Execution | Currier B | Adaptive per-folio | (confirmed) |
| Distinction | Currier A | Registry chains | (confirmed) |
| Context | AZC | Discrete scaffolds | (confirmed) |
| **Orientation** | **HT** | **Quire-clustered, system-conditioned** | **NEW** |

**Key refinement:** HT is not just "system-conditioned" (C341) but shows:
- Quire-level clustering (codicological organization)
- Unified vocabulary (single notation system)
- Strong adjacency effects (production continuity)

---

## 7. Limitations and Future Directions

### 7.1 Limitations

1. **Prefix-level analysis:** This study used HT prefixes as vocabulary proxies. Full type-level analysis would provide finer granularity.

2. **Sample size asymmetry:** AZC has only 30 folios (vs 114 A, 83 B), limiting power for AZC-specific comparisons.

3. **Quire assignment uncertainty:** Some folios have uncertain quire assignments due to manuscript binding history.

4. **No scribe identification:** We cannot distinguish multiple scribes from vocabulary patterns alone.

### 7.2 Future Directions (Tier 3+)

1. **Individual HT type tracking:** Map specific HT types (not just prefixes) across folios
2. **Grapheme-level analysis:** Examine rare grapheme usage in HT tokens
3. **Cross-session identification:** Detect potential scribe changes from vocabulary discontinuities
4. **Correlation with content:** Test if HT density correlates with illustrated vs non-illustrated folios

---

## 8. Files Generated

| File | Description |
|------|-------------|
| `results/ht_folio_features.json` | Per-folio HT features (227 folios × 12 features) |
| `results/ht_distribution_analysis.json` | Distribution tests and quire analysis |
| `results/ht_cross_system_analysis.json` | Cross-system threading analysis |
| `results/ht_adjacency_analysis.json` | Adjacency pattern analysis |
| `results/ht_threading_synthesis.md` | Synthesis summary |
| `phases/exploration/ht_folio_features.py` | Phase 1 script |
| `phases/exploration/ht_distribution_analysis.py` | Phase 2 script |
| `phases/exploration/ht_cross_system_analysis.py` | Phase 4 script |
| `phases/exploration/ht_adjacency_analysis.py` | Phase 5 script |

---

## 9. Conclusion

The HT-THREAD analysis reveals that the Human Track is a **single unified notation layer** that threads through the entire Voynich Manuscript. Unlike the operational vocabulary which is system-specific, HT maintains vocabulary unity while varying in density based on:

1. **Codicological structure** (quire-level clustering)
2. **System context** (A > AZC > B density gradient)
3. **Production continuity** (strong adjacency clustering)

This pattern is consistent with HT serving as orientation markers, waiting notation, or placeholder tokens applied during a continuous production process that respected both codicological boundaries (quires) and functional boundaries (Currier systems).

The finding that HT adjacency clustering (1.69x) exceeds Currier A vocabulary adjacency (1.31x) suggests HT was applied with even stronger session continuity than the operational text, possibly as a later-pass notation overlaid on existing content.

---

**Report prepared for expert review.**

*Generated: 2026-01-10 | HT-THREAD Analysis | Voynich Manuscript Project*
