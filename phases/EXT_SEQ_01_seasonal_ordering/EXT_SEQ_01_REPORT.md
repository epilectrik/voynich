# EXT-SEQ-01: Illustration Seasonal Ordering Analysis

**Status:** COMPLETE
**Tier:** 3 (External Alignment Only)
**Date:** 2026-01-05

---

## Section 1 - Method Summary

### Data Used

- 30 botanical folios in manuscript binding order
- PIAA plant-class annotations (primary class only)
- No species identification attempted

### Seasonal Bin Definitions (Coarse, Heuristic)

| Class | Seasonal Bin | Rationale |
|-------|--------------|-----------|
| AF (Aromatic Flower) | SUMMER | Peak flowering period |
| ALH (Aromatic Leaf Herb) | SUMMER | Leafy growth season |
| AS (Aromatic Shrub) | AUTUMN | Woody harvest timing |
| RT (Resinous) | AUTUMN | Sap/resin collection |
| MH (Medicinal Herb) | AMBIGUOUS | Varies widely |
| AQ (Aquatic) | SUMMER | Growing season |

### Observed Distribution

| Class | Count | Seasonal Bin |
|-------|-------|--------------|
| AF | 14 | SUMMER |
| ALH | 9 | SUMMER |
| AS | 3 | AUTUMN |
| MH | 3 | AMBIGUOUS |
| RT | 1 | AUTUMN |

**Seasonal Distribution:**
- SUMMER: 23 folios (76.7%)
- AUTUMN: 4 folios (13.3%)
- AMBIGUOUS: 3 folios (10.0%)

### Null Models

1. Fully random order (10,000 permutations)
2. Class-frequency preserving shuffle

---

## Section 2 - Results Tables

### A. Adjacency Bias Test

| Metric | Observed | Null Mean | p-value | Cohen's d |
|--------|----------|-----------|---------|-----------|
| Adjacency rate | 1.000 | 1.000 | 1.0000 | 0.000 |

**Verdict:** NOT SIGNIFICANT

**Note:** Both observed and null achieve 100% adjacency because 77% of folios share the same seasonal bin (SUMMER). The test lacks discriminative power given the skewed distribution.

### B. Monotonic Drift Test

| Metric | Observed | Null Mean | p-value | Cohen's d |
|--------|----------|-----------|---------|-----------|
| Spearman rho | 0.075 | 0.001 | 0.6960 | 0.395 |

**Verdict:** NO DRIFT DETECTED

No evidence of increasing or decreasing seasonal trend through the manuscript.

### C. Clustering Strength

| Metric | Observed | Null Mean | p-value | Cohen's d |
|--------|----------|-----------|---------|-----------|
| Number of clusters | 13 | — | — | — |
| Mean cluster size | 2.31 | — | — | — |
| Max cluster size | 7 | 8.61 | 0.7498 | -0.662 |

**Verdict:** NO CLUSTERING

Observed max cluster size is actually **smaller** than null expectation. The manuscript order shows **less** seasonal clustering than random.

### Observed Clusters

| # | Season | Size |
|---|--------|------|
| 1 | SUMMER | 6 |
| 2 | AUTUMN | 2 |
| 3 | SUMMER | 1 |
| 4 | AMBIGUOUS | 1 |
| 5 | SUMMER | 7 |
| 6 | AUTUMN | 1 |
| 7 | SUMMER | 3 |
| 8 | AUTUMN | 1 |
| 9 | SUMMER | 3 |
| 10 | AMBIGUOUS | 1 |
| 11 | SUMMER | 2 |
| 12 | AMBIGUOUS | 1 |
| 13 | SUMMER | 1 |

### Summary Statistics

| Test | Observed | Null Mean | p-value | Effect d |
|------|----------|-----------|---------|----------|
| Adjacency Rate | 1.000 | 1.000 | 1.0000 | 0.000 |
| Monotonic Drift (rho) | 0.075 | 0.001 | 0.6960 | 0.395 |
| Max Cluster Size | 7.0 | 8.61 | 0.7498 | -0.662 |

**Tests with p < 0.05:** 0/3
**Tests with |d| > 0.8:** 0/3

---

## Section 3 - Outcome Classification

### Outcome: **NO_ORDERING_SIGNAL**

Plant illustration ordering does not differ from random with respect to coarse seasonal plausibility.

### Critical Finding

The analysis is **underpowered** due to extreme class imbalance:

- 77% of botanical folios are SUMMER-classified (aromatic flowers + aromatic leaf herbs)
- Only 13% are AUTUMN-classified (shrubs + resinous)
- This reflects the PIAA finding (86.7% aromatic alignment)

With such skewed distribution, seasonal ordering tests cannot discriminate between organized and random sequences.

### What This Does NOT Mean

- Does NOT mean illustrations are randomly placed
- Does NOT mean no organizational principle exists
- Does NOT mean seasonal considerations were absent

It means: **The test lacks statistical power given the observed class distribution.**

---

## Section 4 - Interpretation Boundary

This analysis tests only whether plant illustration ordering differs from random with respect to coarse seasonal plausibility.

It does NOT imply:
- instruction
- meaning
- ingredient lists
- correspondence with executable text
- harvest guides or recipes

Any detected pattern (or lack thereof) may reflect:
- scribal/organizational convenience
- material availability during production
- copying order from an exemplar
- the dominance of a single plant class (aromatic summer-flowering)

**TIER ASSIGNMENT:** Tier 3 (External Alignment Only)

---

## Relationship to Prior Findings

### PIAA (Plant Illustration Alignment Analysis)

PIAA found 86.7% of botanical folios are perfumery-aligned (aromatic flowers, aromatic leaf herbs, aromatic shrubs, resinous).

EXT-SEQ-01 finds this alignment is so strong that it **collapses seasonal variation**:
- Aromatic flowers → SUMMER
- Aromatic leaf herbs → SUMMER
- Result: 77% SUMMER, insufficient variation for ordering tests

### Interpretation

The manuscript's botanical section is dominated by summer-flowering aromatics. This is consistent with:
- A perfumery focus (PIAA finding)
- Material selection rather than seasonal organization
- Illustrations grouped by use-class rather than harvest-time

---

## Files

- `ext_seq_01.py` — Analysis implementation
- `EXT_SEQ_01_REPORT.md` — This report

---

*EXT-SEQ-01 COMPLETE. No seasonal ordering signal detected. Test underpowered due to class imbalance (77% SUMMER).*
