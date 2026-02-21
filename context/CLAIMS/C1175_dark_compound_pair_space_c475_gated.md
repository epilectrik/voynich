# C1175: Dark Compound Pair Space Is C475-Gated but Sparsely Occupied

**Tier:** 2
**Scope:** B, dark pipeline, combinatorics
**Phase:** DARK_PIPELINE_COMBINATORICS (Phase 419)
**Depends on:** C475, C1028, C1061, C1065, C1141

## Statement

Of the 903 possible unordered atom pairs from 43 atoms used in multi-atom dark compounds, only 71 are observed (7.9% occupancy). C475 compatibility is a necessary gate: 100% recall (56/56 testable pairs are C475-compatible). However, precision is only 13.4% (71/528 C475-compatible pairs occupied), indicating C475 is necessary but far from sufficient. C1061 enriched pairs have 80% recall (8/10 enriched pairs appear in dark compounds). C1065 asymmetric ordering pairs have 70% recall (14/20 appear). 78.9% of observed pairs involve only bridge atoms.

## Evidence

### Pair Space
| Metric | Value |
|--------|-------|
| Atoms in multi-atom compounds | 43 |
| Total possible pairs | 903 |
| Observed pairs | 71 |
| Occupancy | 7.9% |

### Gate Analysis
| Gate | Recall | Precision |
|------|--------|-----------|
| C475 compatibility | 1.000 (56/56) | 0.134 (71/528) |
| C1061 enriched | 0.800 (8/10) | 0.113 |
| C1065 ordering | 0.700 (14/20) | 0.197 |

### Top Co-occurring Atom Pairs
| Pair | Count |
|------|-------|
| ek+ke | 4 |
| cth+eo | 3 |
| eo+ke | 3 |
| eo+ot | 3 |
| ke+ok | 3 |

## Interpretation

The dark pipeline follows the same curation pattern as the general vocabulary (C1028): pairwise compatibility is necessary (100% recall) but the space is far more occupied than predicted by compatibility alone. The 7.9% occupancy of atom-pair space parallels C1028's 0.9% occupancy of PREFIX×MIDDLE×SUFFIX space. Both indicate a naming/vocabulary system where only a fraction of possible combinations are instantiated — consistent with a finite material-specific vocabulary rather than a generative free-for-all.

## Provenance

- Phase 419 Test 1: ATOM_COOCCURRENCE_ACCEPTANCE
- Script: `phases/DARK_PIPELINE_COMBINATORICS/scripts/dark_pipeline_combinatorics.py`
- Results: `phases/DARK_PIPELINE_COMBINATORICS/results/dark_pipeline_combinatorics.json` -> test1_atom_cooccurrence_acceptance
