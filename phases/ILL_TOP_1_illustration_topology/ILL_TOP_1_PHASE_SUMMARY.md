# Phase ILL-TOP-1: Summary

**Phase:** ILL-TOP-1 | **Status:** COMPLETE | **Tier:** 3

**Date:** 2026-01-13

---

## VERDICT: MISMATCH

**Parallel indexing hypothesis is FALSIFIED.**

Visual similarity in illustrations does NOT predict MIDDLE constraint similarity. The illustrations and Currier A constraint structure are NOT parallel indices of the same domain organization at the detectable level.

---

## Test Results

| Test | Question | Result | Verdict |
|------|----------|--------|---------|
| A (PRIMARY) | Do visual clusters correlate with MIDDLE similarity? | rho=-0.03, p=0.58 | **FAIL** |
| B | Does section alignment exceed null? | All H section | **MOOT** |
| C | Do schematic illustrations correlate with hub density? | rho=0.02, p=0.93 | **FAIL** |
| D | Do dissimilar-compatible pairs cluster in hub regions? | Pairs exist, no hub concentration | **PARTIAL** |
| E | Do illustrations and A traverse same regime sequence? | LCS p=0.32 (hub), p=0.76 (diversity) | **FAIL** |
| F | Do visual regime shifts align with quire boundaries? | Odds ratio 0.5, p=0.53 | **FAIL** |
| G | Do visual "runs" show within-run constraint consistency? | Within=0.18, Between=0.19, p=0.68 | **FAIL** |
| H | Any fold/overlay/composite/periodic geometry signals? | All p>0.0125 (Bonferroni) | **NO_SIGNAL** |
| **NULL AUDIT** | Are plant folios (H) structurally distinguishable? | 8 metrics differ, but section-driven | **CLOSED_WITH_CAVEAT** |

---

## Test A: Primary Test (FAILED)

**Question:** When illustrations look visually similar, is the constraint space around them similar?

**Data:**
- 29 coded folios (all Currier A, Section H)
- 10 visual clusters
- 406 folio pairs analyzed

**Results:**

| Group | MIDDLE Overlap | N |
|-------|---------------|---|
| Same visual cluster | 0.183 | 45 pairs |
| Different visual cluster | 0.185 | 361 pairs |

**Statistics:**
- Effect size: -0.0018 (NEGATIVE)
- Mann-Whitney U p-value: 0.71
- Spearman rho: -0.028, p=0.58
- Permutation test p-value: 0.62

**Interpretation:** There is NO correlation between visual similarity and MIDDLE constraint similarity. Folios that look visually similar have essentially the same MIDDLE overlap as folios that look different.

**This falsifies the primary hypothesis.**

---

## Test B: Section-PREFIX Alignment (MOOT)

All 29 coded folios are Section H (Herbal). There is no section variance to test.

This test cannot discriminate with the available data.

---

## Test C: Schematic-Hub Correlation (FAILED)

**Question:** Do schematic illustrations correlate with hub-MIDDLE usage?

**Schematic Score Distribution:**
- Score 0 (specific): 16 folios, hub density 0.249
- Score 1 (mixed): 9 folios, hub density 0.243
- Score 2 (schematic): 4 folios, hub density 0.253

**Statistics:**
- Spearman rho: 0.018
- p-value: 0.93

**Interpretation:** No correlation. Schematic/generic illustrations do not use more hub MIDDLEs than specific illustrations.

---

## Test D: Mismatch as Evidence (PARTIAL)

**Question:** Do dissimilar-compatible pairs concentrate in hub regions?

**Pair Categorization:**
- Similar & Compatible: 17 pairs
- Similar & Incompatible: 28 pairs
- Dissimilar & Compatible: 186 pairs
- Dissimilar & Incompatible: 175 pairs

**The existence of 186 dissimilar-but-compatible pairs supports the REGIME model** (constraint compatibility is independent of visual similarity).

However, these pairs do NOT concentrate in hub regions:
- Dissimilar-Compatible hub density: 0.248
- Other pairs hub density: 0.249
- No significant difference (p=0.61)

**Interpretation:** Visual dissimilarity does not predict constraint dissimilarity (good for regime model), but hub concentration is not observed.

---

## Test E: Order-Preserving Regime Alignment (FAILED)

**Question:** Do illustrations and Currier A traverse the SAME regime sequence across the manuscript, possibly at different resolutions?

This test addresses a more subtle hypothesis than topology correspondence:
- Not: do similar images have similar constraints?
- But: do they traverse the same sequence in the same ORDER?

**Example of what this would look like:**
```
  Illustrations (coarse): R1  R2  R3  R4
  Currier A (fine):       R1 R1  R2 R2  R3 R3  R4 R4
```

**Method:**
1. Sort 29 folios by manuscript order
2. Extract visual cluster sequence (illustration regimes)
3. Extract constraint-derived regime sequences:
   - Hub regime (hub density bands: Low <0.20, Med 0.20-0.30, High >0.30)
   - Diversity regime (unique MIDDLE counts: Low <40, Med <55, High ≥55)
4. Test for order-preserving correlation using:
   - Raw Spearman correlation
   - Run-length encoding + Longest Common Subsequence (LCS)
   - Transition correlation (do regime changes co-occur?)

**Results - Hub Regime:**

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Raw Spearman rho | 0.18 | Weak positive |
| Raw Spearman p | 0.34 | Not significant |
| LCS ratio | 0.42 | 42% of shorter sequence |
| Mean random LCS | 0.38 | Expected by chance |
| LCS p-value | 0.32 | Not significant |
| Transition rho | 0.22 | Weak positive |
| Transition p | 0.25 | Not significant |

**Results - Diversity Regime:**

| Metric | Value | Interpretation |
|--------|-------|----------------|
| Raw Spearman rho | 0.06 | Near zero |
| Raw Spearman p | 0.75 | Not significant |
| LCS ratio | 0.46 | 46% of shorter sequence |
| Mean random LCS | 0.46 | Essentially chance |
| LCS p-value | 0.76 | Not significant |
| Transition rho | 0.07 | Near zero |
| Transition p | 0.74 | Not significant |

**Interpretation:** Neither hub density nor MIDDLE diversity regime definitions show order-preserving alignment with visual cluster sequence. The visual organization of illustrations across the manuscript does NOT track the constraint-structure organization of Currier A.

---

## Test F: Quire-Level Regime Articulation (FAILED)

**Question:** Do illustration regime shifts align with quire-level boundaries?

**Method:**
1. Assign each folio to its quire (A-G)
2. Identify visual cluster transitions (when adjacent folios have different clusters)
3. Identify quire boundaries (when adjacent folios are in different quires)
4. Test if transitions and boundaries co-occur more than chance

**Data:**
- 29 folios across 7 quires (A: 5, B: 5, C: 6, D: 4, E: 3, F: 3, G: 3)
- 25 visual transitions (high visual diversity)
- 6 quire boundaries in the dataset

**Results:**

| Co-occurrence | Count |
|---------------|-------|
| Both visual trans & quire bound | 5 |
| Visual trans only | 20 |
| Quire bound only | 1 |
| Neither | 2 |

**Statistics:**
- Fisher's exact odds ratio: 0.50
- Fisher's p-value: 0.53
- Spearman rho: -0.10, p=0.61

**Interpretation:** Visual regime shifts do NOT preferentially occur at quire boundaries. The odds ratio < 1 suggests visual transitions are actually *less* likely at quire boundaries than within quires (though not significantly so). This falsifies the hypothesis that illustrations are organized by physical manuscript structure.

---

## Test G: Multi-Folio Perceptual Scaffolding (FAILED)

**Question:** Do visual "runs" (consecutive folios in same visual cluster) show consistent within-run constraint patterns?

**Hypothesis:** Images establish visual regimes that persist across contiguous folios, with text providing discrimination *within* that regime.

**Data:**
- 26 visual runs identified
- Only 2 multi-folio runs: f11r-f11v (cluster 5), f38r-f38v-f42r (cluster 6)
- 4 within-run folio pairs
- 25 between-run adjacent folio pairs

**Results:**

| Measure | Value |
|---------|-------|
| Within-run MIDDLE similarity | 0.183 |
| Between-run MIDDLE similarity | 0.187 |
| Mann-Whitney U | 43.0 |
| p-value (one-sided) | 0.68 |
| Effect size | -0.005 |

**Interpretation:** No scaffolding effect detected. Within-run MIDDLE similarity is actually *slightly lower* than between-run (effect size negative). The visual cluster persistence does NOT predict constraint consistency. However, with only 2 multi-folio runs and 4 within-run pairs, statistical power is limited.

---

## Test H: Negative Geometric Test (NO SIGNAL)

**Purpose:** Explicitly document absence of fold/overlay/composite signals to pre-empt fringe interpretations.

### H1: Fold Symmetry Test
- **Question:** Does first half mirror reversed second half?
- **Fold matches:** 0/14
- **Expected by chance:** 1.4
- **p-value:** 1.00
- **Verdict:** NO FOLD SIGNAL

### H2: Overlay/Superposition Test
- **Question:** Do recto and verso pages show systematic differences?
- **Recto mean cluster:** 4.09
- **Verso mean cluster:** 4.67
- **p-value:** 0.70
- **Verdict:** NO SYSTEMATIC RECTO/VERSO DIFFERENCE

### H3: Composite/Assembly Test
- **Question:** Does page position predict visual cluster?
- **Spearman rho:** 0.13
- **p-value:** 0.50
- **Verdict:** NO POSITIONAL PATTERN

### H4: Modular/Periodic Test
- **Question:** Do visual clusters show periodicity at common periods (2,3,4,5)?

| Period | Kruskal H | p-value | Signal |
|--------|-----------|---------|--------|
| 2 | 0.03 | 0.86 | NO |
| 3 | 1.74 | 0.42 | NO |
| 4 | 0.56 | 0.90 | NO |
| 5 | 10.30 | 0.036 | marginal* |

*Period 5 shows marginal signal (p=0.036) but does NOT survive Bonferroni correction (threshold 0.0125 for 4 tests).

**Overall Interpretation:** No geometric patterns detected. The illustrations are not organized by any fold, overlay, composite, or periodic scheme we can detect. This strengthens the case that any relationship (if it exists) must be content-based, not geometry-based.

---

## Plant Folio Null Audit (CLOSURE VERIFICATION)

**Purpose:** Confirm that plant folios are statistically indistinguishable from non-plant folios across all existing structural metrics. This is closure verification, not hypothesis generation.

### Data

- **Plant folios:** Section H (129 folios, 57% of corpus)
- **Non-plant folios:** All other sections (98 folios)
- **Metrics tested:** 14 (HT, system pressure, B metrics)
- **Bonferroni-corrected threshold:** α = 0.0036

### Results

**8 metrics showed significant differences (p < 0.0036, |d| > 0.5):**

| Metric | Plant (H) | Non-Plant | p-value | Cohen's d |
|--------|-----------|-----------|---------|-----------|
| ht_density | 0.173 | 0.146 | 0.00013 | 0.51 |
| ht_percentile | 56.6 | 41.8 | 0.00013 | 0.53 |
| ht_z_score | 0.21 | -0.28 | 0.00014 | 0.51 |
| pressure.B | 0.65 | 0.42 | 0.00053 | 0.84 |
| pressure.HT | 0.57 | 0.42 | 0.00013 | 0.53 |
| B.escape_density | 0.10 | 0.19 | <0.00001 | -1.57 |
| B.cei_total | 0.61 | 0.52 | 0.00053 | 0.78 |
| B.recovery_ops | 5.9 | 22.5 | <0.00001 | -1.57 |

### Clarifying Analysis: Section-Driven vs Illustration-Driven

**Critical question:** Are these differences due to SECTION membership or ILLUSTRATION content?

**Section HT Density Ranking:**

| Rank | Section | Mean HT | n |
|------|---------|---------|---|
| 1 | A | 0.188 | 8 |
| 2 | C | 0.177 | 13 |
| **3** | **H** | **0.173** | **129** |
| 4 | T | 0.165 | 5 |
| 5 | P | 0.156 | 16 |
| 6 | S | 0.138 | 24 |
| 7 | Z | 0.137 | 12 |
| 8 | B | 0.111 | 20 |

**Key finding:** Section H is in the MIDDLE of the distribution (3rd/8), not at an extreme.

**Section-by-section comparisons:**
- H vs A: p=0.45 (not significant)
- H vs C: p=0.78 (not significant)
- H vs T: p=0.81 (not significant)
- H vs P: p=0.17 (not significant)
- H vs B: p<0.001 (significant)
- H vs S: p=0.006 (significant)
- H vs Z: p=0.030 (marginal)

**Interpretation:** H differs from LOW-HT sections (B, S, Z) but NOT from HIGH-HT sections (A, C, T, P). The original H-vs-nonH comparison was confounded by section heterogeneity.

### Verdict: CLOSED_WITH_CAVEAT

> Section H has distinct structural properties (higher HT density, lower escape rates in B programs). However, ILL-TOP-1 Tests A-H showed NO correlation between visual clusters and constraints WITHIN Section H (all 8 tests failed).
>
> **Therefore:**
> 1. Section H has section-inherent properties (like all sections)
> 2. Illustrations do NOT organize constraints within Section H
> 3. Illustrations remain EPIPHENOMENAL to grammar structure
>
> **Illustration question formally CLOSED.**

---

## What This Means

### The Parallel Indexing Model is FALSIFIED

The hypothesis that:
> "Illustrations and Currier A independently organize the same material domain at the category level"

is **not supported** by the data.

Visual similarity clusters in illustrations do NOT correspond to:
- MIDDLE constraint neighborhoods
- Hub/peripheral distributions
- PREFIX-based families

### What WAS Found

1. **Illustrations and constraints operate independently** - This is consistent with C137-C140 (swap invariance)

2. **Dissimilar plants can have compatible constraints** - This supports the regime-level (not identity-level) interpretation of Currier A

3. **Visual organization =/= constraint organization** - The illustrations are organized by visual/botanical similarity, but this does not map to processing constraint similarity

### What This Does NOT Mean

This result does NOT mean:
- Illustrations are meaningless
- Illustrations are later additions
- The manuscript is a hoax

It means:
- **Visual similarity =/= constraint similarity**
- The illustrations and text are organized by DIFFERENT principles
- If there is a relationship, it is not at the category level we tested

---

## Implications

### For the Overall Model

The manuscript appears to be:
- **Text:** Organized by processing constraints
- **Illustrations:** Organized by visual/botanical characteristics

These are **independent organizational schemes**, not parallel indices.

### For Future Work

1. The illustrations may serve a **human navigation** function unrelated to constraint structure
2. The relationship (if any) may be at a **different level** than visual similarity clusters
3. The illustrations may reflect **taxonomic** organization while text reflects **processing** organization

### What Remains True

This result does NOT contradict:
- MAT-PHY-1 (botanical chemistry topology match) - still valid
- APP-1 (apparatus behavioral match) - still valid
- The core model (closed-loop control programs) - still valid

It simply closes the question of whether illustrations parallel the constraint structure.

---

## Epistemic Status

This is a **clean negative result**:
- Pre-registered methodology
- Clear success criteria
- Unambiguous outcome
- Informative for the overall model

The parallel indexing hypothesis was worth testing and is now falsified.

---

## Files

| File | Content |
|------|---------|
| `phase_specification.md` | Pre-registration |
| `data_extraction.py` | MIDDLE extraction script |
| `execute_tests.py` | Tests A-D |
| `test_e_order_alignment.py` | Test E: Order-preserving alignment |
| `folio_middle_distributions.json` | Per-folio MIDDLE data |
| `folio_prefix_distributions.json` | Per-folio PREFIX data |
| `folio_metadata.json` | Combined metadata |
| `test_results.json` | Tests A-D results |
| `test_e_results.json` | Test E results |
| `test_f_g_h_remaining.py` | Tests F, G, H: Order/Geometry tests |
| `test_f_g_h_results.json` | Tests F, G, H results |
| `plant_folio_null_audit.py` | Null Audit: Section-driven vs illustration-driven |
| `plant_folio_null_results.json` | Null Audit results |

---

> *This phase compared organizational structures, not identities. It tested:*
> - *Topology correspondence (Tests A-D): Do visual clusters correlate with MIDDLE constraints?*
> - *Order-preserving alignment (Test E): Do both traverse the same regime sequence?*
> - *Quire-level articulation (Test F): Do visual shifts align with quire boundaries?*
> - *Perceptual scaffolding (Test G): Do visual runs show within-run constraint consistency?*
> - *Geometric patterns (Test H): Any fold/overlay/composite signals?*
> - *Null Audit: Are plant folios structurally distinguishable from non-plant folios?*
>
> *All hypotheses were falsified or showed no signal. The Null Audit found Section H differs from other sections (section-driven), but ILL-TOP-1 Tests A-H showed no within-section correlation with visual clusters (illustrations epiphenomenal). Visual similarity does not predict constraint similarity at ANY level tested. No identity-level claims were made. All findings are Tier 3.*
>
> **ILLUSTRATION QUESTION FORMALLY CLOSED.**

---

*Phase completed 2026-01-13*
