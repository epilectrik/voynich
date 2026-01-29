# C689: Survivor Set Uniqueness

**Status:** VALIDATED | **Tier:** 2 | **Phase:** A_RECORD_B_FILTERING | **Scope:** A-B

## Finding

Each A record produces a **near-unique** filter fingerprint: 1,525 unique surviving class sets from 1,562 records (97.6% uniqueness ratio). Pairwise Jaccard similarity is low (mean 0.199), confirming that different A records create substantially different B vocabulary restrictions. The most common set is the empty set (18 records, 1.2%).

## Key Numbers

| Metric | Value |
|--------|-------|
| Total records | 1,562 |
| Unique class sets | 1,525 |
| Uniqueness ratio | 97.6% |
| Pairwise Jaccard (1000 pairs) | mean=0.199, median=0.182, std=0.131 |
| Set size distribution | mean=11.08, median=10.0, std=5.79 |

## Most Common Sets

| Set | Size | Count | % |
|-----|------|-------|---|
| {} (empty) | 0 | 18 | 1.2% |
| {10, 26} | 2 | 5 | 0.3% |
| {10, 26, 28, 36} | 4 | 3 | 0.2% |

## Interpretation

The 97.6% uniqueness confirms that A records function as **individual configuration tokens**, not categorical selectors from a small set of profiles. Each A record creates its own distinct B vocabulary landscape. The low Jaccard (0.199) means typical records share only ~20% of their surviving classes — high differentiation.

## Provenance

- Script: `phases/A_RECORD_B_FILTERING/scripts/structural_reshape_analysis.py` (Test 8)
- Extends: C503 (cosurvival analysis), C682 (distribution profile)
