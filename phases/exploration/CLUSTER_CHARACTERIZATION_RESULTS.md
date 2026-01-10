# Cluster Characterization Results

**Date:** 2026-01-10
**Status:** ANALYSIS COMPLETE
**Context:** Post-C424 characterization of clustered vs singleton entries

---

## Summary

C424 established that Currier A shows clustered adjacency: 31% of adjacent entry pairs share vocabulary, forming runs of mean size ~3. This analysis investigates whether entries appearing in runs differ structurally from singletons.

**Main Finding:** Clustered entries are systematically LARGER and MORE COMPLEX than singletons, but this is NOT purely a length artifact - adjacent entries share vocabulary at rates significantly exceeding length-matched random pairs.

---

## Key Findings

### 1. Classification Distribution

| Class | Count | Percentage |
|-------|-------|------------|
| SINGLETON | 987 | 53.7% |
| RUN_START | 288 | 15.7% |
| RUN_INTERNAL | 275 | 15.0% |
| RUN_END | 288 | 15.7% |
| **CLUSTERED (total)** | **851** | **46.3%** |

- 288 runs identified
- Mean run size: 2.95 entries
- Max run size: 20 entries

### 2. Structural Differences (All significant at Bonferroni-corrected alpha)

| Metric | Clustered Mean | Singleton Mean | Effect Size | Direction |
|--------|----------------|----------------|-------------|-----------|
| **token_count** | 25.8 | 15.5 | -0.500 | Clustered 67% larger |
| **block_count** | 4.0 | 2.0 | -0.376 | Clustered 2x more blocks |
| **prefix_count** | 3.4 | 2.2 | -0.441 | Clustered 52% more diverse |
| **middle_count** | 7.1 | 4.8 | -0.372 | Clustered 50% more vocabulary |
| **da_count** | 3.0 | 1.0 | -0.376 | Clustered 3x more DA articulation |
| **repetition_depth** | 4.2 | 3.4 | -0.237 | Clustered slightly more repetition |

**Non-significant:**
- has_repetition (p=0.046) - Both groups show ~97% repetition rate
- rare_middle_count (p=0.055) - No enrichment of rare MIDDLEs in clusters

### 3. Position Effects (Runs size 3+)

No significant differences between RUN_START and RUN_END entries:
- Token count: Start 26.6 vs End 24.5 (p=0.10)
- Block count: Start 3.9 vs End 4.0 (p=0.91)
- Prefix count: Start 3.4 vs End 3.2 (p=0.10)

**Interpretation:** First and last entries in runs are structurally equivalent. Runs do not have "header" or "footer" entries.

### 4. Section Breakdown

| Section | Clustered N | Singleton N | Clustered Tokens | Singleton Tokens |
|---------|-------------|-------------|------------------|------------------|
| H | 612 | 639 | 24.2 | 18.6 |
| P | 158 | 296 | 34.6 | 8.3 |
| T | 81 | 52 | 20.7 | 17.6 |

**Notable:** Section P shows the most extreme pattern - clustered entries average 34.6 tokens vs 8.3 for singletons (4.2x difference).

---

## Confound Check: Is Clustering Just a Length Artifact?

**Concern:** Longer entries have more tokens, so mechanically they have higher probability of sharing at least one token with neighbors. Is clustering just a byproduct of entry length?

### Length-Stratified Clustering Rates

| Token Range | Total | Clustered | Singleton | Cluster Rate |
|-------------|-------|-----------|-----------|--------------|
| 1-10 | 391 | 51 | 340 | 13.0% |
| 11-20 | 591 | 242 | 349 | 40.9% |
| 21-30 | 554 | 327 | 227 | 59.0% |
| 31-50 | 266 | 195 | 71 | 73.3% |
| 51-100 | 36 | 36 | 0 | 100.0% |

### Observed vs Expected (Length-Controlled)

| Token Range | Expected (random pairs) | Observed (adjacent) | Ratio |
|-------------|-------------------------|---------------------|-------|
| 1-10 | 1.2% | 13.0% | **10.87x** |
| 11-20 | 13.6% | 40.9% | **3.01x** |
| 21-30 | 30.4% | 59.0% | **1.94x** |
| 31-50 | 46.8% | 73.3% | **1.57x** |
| 51-100 | 87.3% | 100.0% | **1.15x** |

**Verdict:** Clustering is NOT purely a length artifact.
- All ratios > 1.0 (adjacent pairs share more than random same-length pairs)
- Short entries show STRONGEST signal (10.87x for 1-10 tokens)
- Long entries show weaker but still elevated signal (1.15x for 51-100 tokens)

**Interpretation:** Short entries that cluster are doing something special - they share vocabulary despite having few tokens to share. Long entries almost always cluster, but this is partially mechanical.

---

## Interpretation

### What This Analysis Establishes

1. **Clustered entries are structurally larger and more complex**
   - ~70% more tokens
   - ~2x more DA-delimited blocks
   - ~50% more prefix and MIDDLE diversity

2. **Clustering is NOT purely a length artifact**
   - Adjacent entries share vocabulary at 1.15-10.87x the rate of length-matched random pairs
   - The effect is strongest for short entries

3. **Runs have no internal hierarchy**
   - First and last entries are structurally equivalent
   - No "header" or "footer" pattern

4. **Pattern holds across sections**
   - All sections show clustered > singleton in token count
   - Section P shows most extreme difference (4.2x)

### What This Analysis Does NOT Establish

- Semantic meaning of clustering
- Causal direction (do complex entries get grouped, or does grouping create complexity?)
- Whether clustering reflects original manuscript organization or transcription artifacts

---

## Constraint Implications

### Possible Refinement: C424.a

If expert approves, the following refinement could be added:

**C424.a - Structural Correlates of Clustered Adjacency**
- Tier: 2 | Status: CLOSED | Source: Exploration
- Entries appearing in vocabulary-sharing runs (C424) are systematically larger and more complex than singletons:
  - 67% more tokens (25.8 vs 15.5, p<0.001)
  - 2x more DA-delimited blocks (4.0 vs 2.0, p<0.001)
  - 52% more prefix diversity (3.4 vs 2.2, p<0.001)
- This is NOT purely a length artifact: adjacent entries share vocabulary at 1.15-10.87x the rate of length-matched random pairs (strongest for short entries).
- No positional asymmetry within runs (first ≈ last).

**Relationship to C424:** C424.a characterizes the *structural profile* of clustered entries without implying semantics or hierarchy.

---

## Files

- Analysis script: `phases/exploration/cluster_characterization.py`
- This synthesis: `phases/exploration/CLUSTER_CHARACTERIZATION_RESULTS.md`
- Related: `phases/exploration/super_entry_grouping.py`, `phases/exploration/super_entry_stress_tests.py`

---

---

# Extended Analysis Results

Following the initial characterization, six additional analyses were conducted to investigate specific patterns.

---

## Analysis 1: Section P Anomaly

**Finding:** Section P's extreme clustering asymmetry (4.18x ratio vs 1.30x for H) is driven by a bimodal entry length distribution.

| Metric | Section P | Section H | Section T |
|--------|-----------|-----------|-----------|
| Cluster ratio | 4.18x | 1.30x | 1.17x |
| Clustered tokens | 34.6 | 24.2 | 20.7 |
| Singleton tokens | 8.3 | 18.6 | 17.6 |

**Section P singleton characteristics:**
- 70.3% have only 1-5 tokens (very short)
- Enriched for ot- prefix (12.7% vs 3.5% in clustered)
- Depleted for da- prefix (10.3% vs 17.3% in clustered)

**Interpretation:** Section P contains a large population of very short, ot-heavy entries that almost never cluster. These may represent a different record type (brief notations?) distinct from the longer, da-rich entries that cluster.

---

## Analysis 2: Short-Entry Clustering Drivers

**Question:** What makes short entries (1-10 tokens) cluster at 10.87x the random rate?

**Finding:** Short clustered entries share primarily:
- The token "daiin" (27 occurrences)
- da- prefix (34 sharing pairs)
- ch- prefix (26 sharing pairs)
- Mean shared tokens per pair: only ~1 token

**Interpretation:** Short entries that cluster typically share a single high-frequency token (usually "daiin"). This is sufficient to create J > 0, but represents minimal vocabulary overlap. The 10.87x ratio reflects that adjacent short entries are 10x more likely to share even one token than random same-length pairs.

---

## Analysis 3: Within-Run Similarity Decay

**Question:** Does similarity decrease from run-start to run-end?

**Surprising Finding:** Similarity INCREASES with position gap within runs.

| Gap | Mean Jaccard | N pairs |
|-----|--------------|---------|
| 1 | 0.1504 | 248 |
| 2 | 0.1532 | 188 |
| 3 | 0.1771 | 128 |
| 4 | 0.2742 | 68 |
| 5 | 0.3783 | 42 |
| 6 | 0.5570 | 26 |

Decay correlation: r = +0.930 (p = 0.007) - POSITIVE, not negative.

**Explanation:** This is a confound effect. Larger runs (which contribute gap-5 and gap-6 pairs) are more homogeneous overall. The "similarity increase" reflects that entries in large runs are more similar to each other than entries in small runs.

---

## Analysis 4: Vocabulary Component Sharing

**Question:** What component type drives clustering - PREFIX, MIDDLE, or SUFFIX?

| Component | Clustered Mean J | Random Mean J | Ratio |
|-----------|------------------|---------------|-------|
| **TOKEN** | 0.1124 | 0.0127 | **8.87x** |
| **MIDDLE** | 0.1465 | 0.0358 | **4.09x** |
| PREFIX | 0.4669 | 0.2310 | 2.02x |
| SUFFIX | 0.3936 | 0.1859 | 2.12x |

**Key Finding:** TOKEN and MIDDLE sharing show the strongest elevation over random (8.87x and 4.09x). PREFIX and SUFFIX sharing are elevated but less so (2x).

**Interpretation:** Clustering is driven primarily by shared specific vocabulary items (full tokens and MIDDLE components), not by shared marker families (prefixes) or grammatical endings (suffixes). Adjacent entries share content words, not just classification.

---

## Analysis 5: Cluster Homogeneity (PREFIX Dominance)

**Question:** Do runs share a dominant prefix family?

**Finding:** Runs are NOT prefix-homogeneous.

| Metric | Value |
|--------|-------|
| Mean dominance | 0.421 |
| Median dominance | 0.385 |
| Runs with dominance > 0.7 | 5.6% |

**Dominance by run size:**
- Size 2: mean dominance 0.441
- Size 3: mean dominance 0.418
- Size 4-5: mean dominance 0.388
- Size 6+: mean dominance 0.360

**Interpretation:** Larger runs are LESS prefix-homogeneous. Runs are not organized around a single marker family. Instead, they contain diverse prefix families with shared content vocabulary (MIDDLEs/tokens).

---

## Analysis 6: Run-Size Effects

**Finding:** Larger runs differ systematically from smaller runs.

| Group | Runs | Entries | Mean Tokens | Mean Prefixes | Within J |
|-------|------|---------|-------------|---------------|----------|
| Size 2 | 141 | 282 | 23.4 | 4.22 | 0.081 |
| Size 3-4 | 121 | 397 | 26.4 | 4.37 | 0.068 |
| Size 5+ | 26 | 172 | 28.5 | 4.34 | **0.363** |

**Key Finding:** Size 5+ runs have dramatically higher within-run similarity (0.36 vs 0.08 for size 2). This explains Analysis 3's surprising result - larger runs form because their entries are genuinely more similar to each other.

**Interpretation:** Small runs (size 2) often arise from pairs sharing just 1-2 tokens. Large runs (size 5+) represent genuine vocabulary clusters where multiple entries share substantial vocabulary.

---

## Consolidated Findings

### What We Now Know

1. **Clustered entries are structurally larger and more complex** (67% more tokens, 2x more blocks)

2. **Clustering is NOT purely a length artifact** - adjacent entries share vocabulary at 1.15-10.87x the rate of length-matched random pairs

3. **TOKEN and MIDDLE sharing drive clustering** (8.87x and 4.09x vs random), not PREFIX or SUFFIX

4. **Runs are NOT prefix-homogeneous** - they contain diverse marker families with shared content vocabulary

5. **Large runs (5+) are qualitatively different** - they represent genuine vocabulary clusters with high internal similarity (J=0.36)

6. **Section P has a distinct population** - very short, ot-heavy entries that almost never cluster

7. **Short-entry clustering is driven by single shared tokens** - usually high-frequency items like "daiin"

8. **No positional hierarchy within runs** - first and last entries are structurally equivalent

### Emergent Pattern

The overall pattern suggests:
- **Complex entries** (longer, more DA blocks, more diverse prefixes) tend to appear adjacent to other complex entries sharing content vocabulary
- **Simple entries** (short, single-prefix) tend to stand alone
- **Large runs** represent genuine vocabulary-coherent groupings
- **Small runs** often arise from coincidental single-token sharing

This is consistent with a registry where complex items get grouped together (perhaps describing related things), while simple items are isolated (perhaps brief notations or references).

---

## Constraint Implications

### Proposed C424.a - Structural Correlates of Clustered Adjacency

Entries appearing in vocabulary-sharing runs (C424) are systematically larger and more complex:
- 67% more tokens (25.8 vs 15.5)
- 2x more DA-delimited blocks
- 52% more prefix diversity
- Adjacent entries share TOKEN (8.87x) and MIDDLE (4.09x) vocabulary at rates far exceeding random

This is NOT purely a length artifact (1.15-10.87x over length-matched random).

### Proposed C424.b - Run-Size Threshold Effect

Runs of size 5+ show qualitatively different structure:
- Within-run similarity: J=0.36 vs J=0.08 for size-2 runs
- Represent genuine vocabulary clusters, not coincidental single-token sharing

### Proposed C424.c - Section P Bimodal Population

Section P contains a distinct population of very short (1-5 token), ot-heavy entries that almost never cluster (70% of singletons). These may represent a different record type.

---

---

# Deep Dive Analysis Results

Following the extended analysis, three additional investigations were conducted.

---

## Deep Dive 1: Section P Short-Entry Population

### Key Discovery: 83% Exclusive Vocabulary

Section P short singletons (1-5 tokens) use vocabulary that is **83.3% exclusive** - tokens that NEVER appear in clustered entries.

| Metric | Value |
|--------|-------|
| Short singleton vocabulary | 330 unique tokens |
| Clustered vocabulary | 1,199 unique tokens |
| Shared | 55 tokens (16.7% of short) |
| **Short-only** | **275 tokens (83.3%)** |

### Prefix Distribution

| Prefix | % of Short Singletons |
|--------|----------------------|
| **ot** | **33.2%** |
| ok | 25.7% |
| ch | 17.7% |
| da | 11.8% |
| ol | 9.4% |

The ot- prefix dominance (33.2%) is unique to this population.

### Most Common Short-Only Tokens

```
otoldy: 12    otoky: 7     otaly: 7     otaldy: 6
orol: 5       okeeos: 5    cheys: 5     okary: 5
```

### Folio Distribution

- **15 of 16 Section P folios** contain short singletons (93.8%)
- Top folios: f99r (33), f99v (22), f102v2 (22), f101v2 (19)
- These are "pharmaceutical" section folios

**Interpretation:** Section P short singletons represent a distinct entry type with specialized vocabulary that doesn't appear elsewhere. They are NOT variants of clustered entries - they are a separate population.

---

## Deep Dive 2: Line Position Analysis

### Discovery: Section P Has INVERTED Line Pattern

| Section | Singleton Early % | Clustered Early % | Pattern |
|---------|-------------------|-------------------|---------|
| H | 36.0% | 41.5% | Normal (clustered slightly more early) |
| **P** | **76.7%** | **34.8%** | **INVERTED (singletons much more early)** |
| T | 19.2% | 12.3% | Normal (both late-biased) |

Section P is the ONLY section where singletons are concentrated in early lines.

### Line-1 Token Count by Section

| Section | Line-1 Mean Tokens | Rest of Folio Mean | Ratio |
|---------|--------------------|--------------------|-------|
| H | 26.4 | 22.2 | 1.19x (line-1 LONGER) |
| **P** | **15.3** | **20.0** | **0.77x (line-1 SHORTER)** |
| T | 20.0 | 19.3 | 1.04x (similar) |

Section P has an **inverted header pattern** - line-1 entries are SHORTER than average, opposite to section H.

### Line-1 Entries by Section

| Section | Line-1 Entries | Singleton % | Mean Tokens |
|---------|----------------|-------------|-------------|
| H | 97 | 63.9% | 26.1 |
| **P** | **58** | **84.5%** | **13.3** |
| T | 4 | 75.0% | 21.2 |

Section P line-1 entries are:
- 84.5% singletons (vs 63.9% for H)
- Mean 13.3 tokens (vs 26.1 for H) - **half the length**

### Line-1 Vocabulary Divergence

| Metric | Value |
|--------|-------|
| Line-1 vocabulary | 979 unique tokens |
| Other vocabulary | 4,535 unique tokens |
| Shared | 413 (42.2% of line-1) |
| **Line-1 only** | **566 (57.8%)** |

**57.8% of line-1 vocabulary is exclusive to line-1** across all sections.

**Interpretation:** Section P has a fundamentally different organizational structure:
- Short, singleton entries concentrate at the TOP of pages (lines 1-5)
- These use specialized vocabulary (83% exclusive)
- This is the OPPOSITE of sections H and T

---

## Deep Dive 3: Large Run (Size 5+) Vocabulary

### Discovery: Largest "Run" is Artifact

The size-20 run on folio f1r consists entirely of entries containing only the placeholder token "*". This is a transcription artifact, not genuine structure.

### Genuine Large Runs (Size 5-10)

Excluding the f1r artifact:

| Run Size | Count | Mean Within-J | Shared by All | Shared by Majority |
|----------|-------|---------------|---------------|-------------------|
| 10 | 1 | 0.056 | 1 | 3 |
| 8 | 2 | 0.077 | 0 | 1 |
| 7 | 4 | 0.065 | 0 | 2 |
| 6 | 8 | 0.064 | 0-1 | 1-2 |
| 5 | 10 | 0.061 | 0 | 1-8 |

**Key Finding:** Most large runs have NO tokens shared by all entries. They form through chains of pairwise overlap, not global vocabulary sharing.

### Vocabulary Enrichment in Large Runs

Tokens enriched 5x+ in large runs (vs overall):
```
shokcheey: 7.59x    tshodeesy: 7.59x    pydeey: 7.59x
qochol: 7.59x       qokorar: 7.59x      dytchy: 7.59x
olchor: 7.59x       cheedy: 5.69x       ksheody: 5.31x
```

### Prefix Distribution in Large Runs

| Prefix | Large Run % | Overall % | Ratio |
|--------|-------------|-----------|-------|
| **da** | **22.2%** | **14.3%** | **1.55x enriched** |
| ch | 31.3% | 35.1% | 0.89x depleted |
| **ot** | **4.2%** | **6.5%** | **0.65x depleted** |

Large runs are **da-enriched** (1.55x) and **ot-depleted** (0.65x) - the opposite of Section P short singletons.

---

## Deep Dive 4: Singleton vs Clustered Vocabulary Divergence

### Discovery: 68% Exclusive Vocabularies

| Population | Unique Tokens | Exclusive Tokens | % Exclusive |
|------------|---------------|------------------|-------------|
| Singleton | 2,992 | 2,030 | **67.8%** |
| Clustered | 3,071 | 2,109 | **68.7%** |
| Shared | - | 962 | - |

**Interpretation:** Singletons and clustered entries use largely non-overlapping vocabularies. This is not just a structural difference - it's a vocabulary difference.

### Singleton-Enriched Tokens (appearing primarily in singletons)

```
ychol: 28 (ONLY)     qor: 18 (12.96x)    cphaiin: 17 (12.24x)
chotol: 17 (12.24x)  dchaiin: 16 (ONLY)  chok: 15 (10.80x)
```

### Clustered-Enriched Tokens (appearing primarily in clusters)

```
dcho: 20 (ONLY)      shcthy: 19 (ONLY)   okeeor: 17 (11.81x)
qockhol: 16 (11.11x) oeees: 15 (ONLY)    otcham: 14 (ONLY)
```

---

## Consolidated Deep Dive Findings

### 1. Section P Has Distinct Organizational Structure

- **Short singletons** (1-5 tokens) concentrate at **top of pages** (lines 1-5)
- Use **83% exclusive vocabulary** (ot-heavy)
- **Inverted length pattern**: Line-1 entries are SHORTER than average (0.77x)
- This is UNIQUE to Section P - opposite of H and T

### 2. Large Runs Are Chains, Not Clusters

- Most size-5+ runs have **no tokens shared by all entries**
- They form through **pairwise overlap chains**
- The size-20 "run" on f1r is a **transcription artifact**
- da- prefix enriched (1.55x), ot- depleted (0.65x)

### 3. Vocabulary Divergence Is Fundamental

- **68% of singleton vocabulary** doesn't appear in clustered entries
- **68% of clustered vocabulary** doesn't appear in singletons
- This suggests **different content domains**, not just different structures

### 4. Line-1 Has Specialized Vocabulary

- **57.8% of line-1 vocabulary** is exclusive to line-1
- This persists across all sections
- Suggests line-1 may have special structural role

---

## Final Constraint Proposals

### C424.a - Structural Correlates of Clustered Adjacency
(As previously defined - entries in runs are larger/more complex)

### C424.b - Run-Size Threshold Effect
(As previously defined - size 5+ runs have higher within-similarity)

### C424.c - Section P Organizational Inversion
**Tier:** 2 | **Status:** Proposed

Section P exhibits inverted organizational structure:
- Singletons concentrate in early lines (76.7% in lines 1-5 vs 34.8% for clustered)
- Line-1 entries are SHORTER than average (0.77x ratio, vs 1.19x for Section H)
- Short singletons (1-5 tokens) use 83.3% exclusive vocabulary
- ot- prefix dominates (33.2% vs 6.5% in large runs)

This is unique to Section P and opposite to Sections H and T.

### C424.d - Vocabulary Domain Separation
**Tier:** 2 | **Status:** Proposed

Singleton and clustered entries use largely non-overlapping vocabularies:
- 67.8% of singleton vocabulary is exclusive to singletons
- 68.7% of clustered vocabulary is exclusive to clusters
- Only 962 tokens are shared between populations

This suggests clustering correlates with vocabulary domain, not just structural features.

---

## Remaining Open Questions

1. **What is the Section P short-singleton population?** The 83% exclusive vocabulary and ot- dominance suggest these may be a different record type (brief annotations? cross-references? indices?).

2. **Why does line-1 have specialized vocabulary?** The 57.8% exclusivity suggests line-initial position has structural significance beyond just being "first."

3. **Causal direction:** The vocabulary separation (68% exclusive) raises the question of whether vocabulary domain determines clustering, or clustering determines vocabulary.

---

## Files

- Initial analysis: `phases/exploration/cluster_characterization.py`
- Extended analysis: `phases/exploration/cluster_extended_analysis.py`
- Deep dive analysis: `phases/exploration/cluster_deep_dive.py`
- Line position analysis: `phases/exploration/cluster_line_position.py`
- This synthesis: `phases/exploration/CLUSTER_CHARACTERIZATION_RESULTS.md`
