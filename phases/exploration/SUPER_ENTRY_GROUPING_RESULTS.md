# Super-Entry Grouping Analysis Results

**Date:** 2026-01-10
**Status:** STRESS TESTS PASSED - READY FOR CONSTRAINT MINTING
**Constraint:** C424 (pending expert approval)

---

## Summary

Currier A entries show **strong super-entry clustering structure**. The 1.31x mean adjacent similarity is NOT uniformly distributed - it is driven by a MINORITY of highly similar pairs clustered together, while the MAJORITY of adjacent pairs have zero vocabulary overlap.

---

## Key Findings

### Phase 1: Similarity Run Analysis

| Test | Result | Interpretation |
|------|--------|----------------|
| **Autocorrelation** | r=0.80 at lag 1, r=0.58 at lag 5 (all p<0.000001) | High-similarity entries cluster into RUNS |
| **Wald-Wolfowitz Runs** | 576 observed vs 780.8 expected (z=-11.24, p<0.000001) | Fewer runs than random = CLUSTERING |

**Conclusion:** When entries share vocabulary, they tend to appear consecutively (not scattered).

### Phase 2: Extended Window Analysis

| Distance | Mean J | vs Baseline |
|----------|--------|-------------|
| 1 | 0.0345 | 1.97x |
| 2 | 0.0331 | 1.89x |
| 5 | 0.0285 | 1.63x |
| 10 | 0.0239 | 1.37x |

**Baseline (random same-section pairs):** J = 0.0175

**Coherence radius:** Not detected - similarity remains elevated beyond 10 entries.

### Phase 3: Cliff Detection

| Metric | Value |
|--------|-------|
| Threshold (25th percentile) | J = 0.0000 |
| Cliff rate | **69.3%** |
| Mean segment size | 2.0 entries |
| Median segment size | 2.0 entries |
| Max segment size | 19 entries |

**Segment Validation:**
- Within-segment mean J: **0.2158**
- Between-segment mean J: 0.0223
- **Ratio: 9.67x** (p < 0.000001)

---

## Structural Interpretation

The Currier A registry shows a **bimodal adjacency pattern**:

```
MAJORITY (~69%): Adjacent entries have ZERO vocabulary overlap (J=0)
         → Completely distinct records

MINORITY (~31%): Adjacent entries share vocabulary
         → When sharing occurs, it CLUSTERS (autocorr 0.80)
         → Forms tight groups of ~2 entries
         → Within-group similarity 9.67x higher than between-group
```

This explains the 1.31x average:
- Most pairs contribute 0
- A minority of highly similar pairs (J~0.22) pull the average up
- These similar pairs cluster together, not scattered randomly

---

## Organizational Model

```
ENTRY 1 (unique)         J=0
ENTRY 2 (unique)         J=0
ENTRY 3 ────┐            J=0.18  ← Cluster start
ENTRY 4 ────┘            J=0
ENTRY 5 (unique)         J=0
ENTRY 6 ────┐            J=0.25  ← Cluster start
ENTRY 7 ────┤            J=0.21
ENTRY 8 ────┘            J=0
ENTRY 9 (unique)         J=0
...
```

**Interpretation:** The registry contains:
1. **Singleton entries** - unique items with no related neighbors
2. **Paired/clustered entries** - 2-3 related items grouped together

This is consistent with a **materials catalog** where:
- Most entries describe distinct items
- Some entries describe variants/related items and are grouped
- The grouping is LOCAL (not folio-level, not section-level)

---

## Constraint Recommendation

### C424 - Currier A Shows Bimodal Adjacency Structure (Tier 2)

**Statement:**
69% of adjacent entry pairs have zero vocabulary overlap (J=0), while 31% share vocabulary. When sharing occurs, it clusters strongly (autocorrelation r=0.80), forming groups of ~2 entries with 9.67x higher within-group similarity than between-group.

**Evidence:**
- Autocorrelation r=0.80 at lag 1 (p<0.000001)
- Wald-Wolfowitz runs test z=-11.24 (p<0.000001)
- Within-segment / between-segment ratio: 9.67x
- 69.3% cliff rate (J=0 between adjacent entries)

**Relationship to C346:**
- C346 established 1.31x mean adjacent similarity
- C424 decomposes this: the mean is driven by clustered minority, not uniform distribution

---

## Files

- Analysis script: `phases/exploration/super_entry_grouping.py`
- This synthesis: `phases/exploration/SUPER_ENTRY_GROUPING_RESULTS.md`

---

---

## Stress Tests (Expert-Mandated Validation)

All three expert-mandated stress tests **PASSED**, confirming genuine structure:

### Test 1: Section-Controlled Null Model (REQUIRED)

| Metric | Observed | Null (100 perms) | Z-score |
|--------|----------|------------------|---------|
| Zero-overlap rate | 69.3% | 80.6% | **-14.02** |
| Mean Jaccard | 0.0345 | 0.0156 | **+17.09** |
| Autocorrelation | 0.80 | 0.14 | **+5.85** |

**VERDICT: PASSED** - Observed pattern exceeds section-isolated null.

### Test 2: Scale-Invariance

| Representation | Autocorrelation |
|----------------|-----------------|
| token_jaccard | 0.80 |
| middle_only | 0.64 |
| token_minus_da | 0.82 |
| prefix_stripped | 0.73 |

**VERDICT: PASSED** - Clustering persists across all representations (range 0.64-0.82).

### Test 3: Cluster-Size Distribution

| Size | Count | Percentage |
|------|-------|------------|
| 2 | 141 | 49.0% |
| 3 | 87 | 30.2% |
| 4 | 34 | 11.8% |
| 5+ | 26 | 9.0% |

- **51% of clusters are size 3+** (not pair-dominated)
- Mean cluster size: **2.95 entries**
- Max cluster size: **20 entries**

**VERDICT: PASSED** - Genuine multi-entry clusters, not just variant pairs.

---

## Final Verdict

**RECOMMENDATION: MINT C424**

All three stress tests passed. This represents genuine higher-order organizational structure, not variant pairing or copy proximity.

---

## Files

- Initial analysis: `phases/exploration/super_entry_grouping.py`
- Stress tests: `phases/exploration/super_entry_stress_tests.py`
- This synthesis: `phases/exploration/SUPER_ENTRY_GROUPING_RESULTS.md`
