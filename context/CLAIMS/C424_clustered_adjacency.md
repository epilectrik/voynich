# C424: Clustered Adjacency in Currier A

**Tier:** 2 | **Status:** CLOSED | **Scope:** A

---

## Statement

Currier A adjacency coherence is **non-uniform and clustered**. While ~69% of adjacent entry pairs share no vocabulary overlap, the remaining ~31% form contiguous runs of vocabulary-sharing entries. These runs have a mean length of approximately 3 entries (range 2-20) and exhibit strong positive autocorrelation (r = 0.80).

This clustering persists across multiple similarity representations (full tokens, MIDDLE-only, DA-stripped, prefix-stripped) and exceeds section-controlled null models.

**Interpretation:** Currier A is a flat registry whose entries are sometimes arranged into local, contiguous groupings without introducing hierarchical structure, categorical headers, or reusable group boundaries.

---

## Refinements

### C424.a: Structural Correlates of Clustering

Clustered entries differ from singletons across multiple structural metrics, independently of entry length:

| Metric | Clustered | Singleton | Effect Size | Confound-Controlled |
|--------|-----------|-----------|-------------|---------------------|
| Token count | 14.2 | 8.9 | d=0.52 | 1.15x over length-matched |
| MIDDLE count | 5.2 | 3.2 | d=0.55 | 10.87x over length-matched |
| Block count | 3.8 | 2.6 | d=0.48 | 2.14x over length-matched |
| DA count | 2.2 | 1.4 | d=0.44 | 3.56x over length-matched |

**Vocabulary divergence:** 68% of singleton vocabulary never appears in clustered entries, and 68% of clustered vocabulary never appears in singletons. This suggests two distinct compositional regimes within the same grammatical system.

**Component sharing:** TOKEN sharing (8.87x random) and MIDDLE sharing (4.09x random) drive clustering, while PREFIX and SUFFIX sharing contribute less (2.02x and 2.12x respectively).

### C424.b: Run-Size Threshold Effect

Runs of size 5+ exhibit qualitatively stronger adjacency coherence (mean J=0.36) compared to size-2 runs (mean J=0.08), without implying group identity or categorical boundaries.

| Run Size | Mean Internal J | N Runs |
|----------|-----------------|--------|
| 2 | 0.08 | 141 |
| 3-4 | 0.15 | 121 |
| 5+ | 0.36 | 26 |

This is a continuous gradient, not a discrete threshold.

### C424.c: Section P Organizational Inversion

Section P exhibits an inverted ordering regime: singleton entries concentrate at the top of pages (76.7% in lines 1-5, vs 29.1% for clustered), while clustered entries distribute more evenly. Line-1 entries in Section P are shorter than average (0.77x ratio) and use 57.8% exclusive vocabulary.

This is a descriptive observation about positional distribution in Section P. No claims are made about record types, functional categories, or semantic interpretation.

---

## Evidence

### Primary Analysis

| Metric | Value |
|--------|-------|
| Adjacent pairs with J=0 | 69.3% |
| Adjacent pairs with vocabulary sharing | 30.7% |
| Autocorrelation (lag-1) | r = 0.80 |
| Autocorrelation (lag-5) | r = 0.58 |
| Wald-Wolfowitz runs test | z = -11.24 (p < 0.000001) |

### Stress Test 1: Section-Controlled Null Model

| Metric | Observed | Null (n=100) | Z-score |
|--------|----------|--------------|---------|
| Autocorrelation | 0.80 | 0.14 | **+5.85** |
| Mean Jaccard | 0.0345 | 0.0156 | +17.09 |
| Zero-rate | 69.3% | 80.6% | -14.02 |

**Verdict:** Observed clustering far exceeds section-isolated null.

### Stress Test 2: Scale-Invariance

| Representation | Autocorrelation |
|----------------|-----------------|
| Full tokens | 0.80 |
| MIDDLE-only | 0.64 |
| Token-minus-DA | 0.82 |
| Prefix-stripped | 0.73 |

**Verdict:** Clustering persists across all representations (range 0.64-0.82).

### Stress Test 3: Cluster-Size Distribution

| Size | Count | Percentage |
|------|-------|------------|
| 2 | 141 | 49.0% |
| 3 | 87 | 30.2% |
| 4 | 34 | 11.8% |
| 5+ | 26 | 9.0% |

- Mean cluster size: 2.95 entries
- Median cluster size: 3 entries
- Max cluster size: 20 entries
- **51% of clusters are size 3+**

**Verdict:** Genuine multi-entry runs, not pair-dominated.

---

## What This Constraint Claims

- Adjacency coherence is **clustered**, not uniform
- Clusters exceed pair size (mean ~3, max 20)
- Clustering exceeds section-controlled null
- Clustering is representation-invariant
- Clusters are contiguous runs

---

## What This Constraint Does NOT Claim

- "Super-entries" or "higher-level units"
- Fixed group sizes
- Categorical or topical groupings
- Parsing boundaries or delimiters
- Hierarchical structure
- Folio-level subgroups

This is **ordering structure**, not grouping structure.

---

## Relationship to Other Constraints

| Constraint | Relationship |
|------------|--------------|
| **C346** | C424 explains the *shape* of C346's 1.31x effect |
| **C345** | C424 is consistent (no folio-level coherence) |
| **C420** | C424 is consistent (first tokens still unique) |
| **C253** | C424 is consistent (100% block uniqueness maintained) |

C424 refines **ordering**, not ontology.

---

## Limit of Structural Inference

C424 and its refinements represent the **structural exhaustion point** for Currier A analysis. Further characterization would require:

1. **Semantic interpretation** of vocabulary differences (not within scope)
2. **External referent mapping** (no grounding available)
3. **Ontological claims** about entry types (methodologically prohibited)

The observed patterns (vocabulary divergence, positional inversion, run-size effects) are **descriptively complete**. They constrain what ordering structures exist without explaining why they exist.

**Status:** Currier A is structurally exhausted. No further purely structural analyses are expected to yield new constraints.

---

## Phase Documentation

Research conducted: 2026-01-10

Scripts:
- `phases/exploration/super_entry_grouping.py` - Initial clustering analysis
- `phases/exploration/super_entry_stress_tests.py` - Stress tests
- `phases/exploration/cluster_characterization.py` - Structural comparison
- `phases/exploration/cluster_extended_analysis.py` - Extended analysis
- `phases/exploration/cluster_deep_dive.py` - Vocabulary investigation
- `phases/exploration/cluster_line_position.py` - Line position analysis

Results:
- `phases/exploration/SUPER_ENTRY_GROUPING_RESULTS.md`
- `phases/exploration/CLUSTER_CHARACTERIZATION_RESULTS.md`

---

## Navigation

<- [INDEX.md](INDEX.md) | ^ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
