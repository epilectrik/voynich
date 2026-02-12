# C971: Transition Asymmetry Structurally Rare

**Tier:** 2 | **Scope:** B | **Phase:** FINGERPRINT_UNIQUENESS

## Statement

Among random sparse directed graphs on 49 nodes, the Voynich class-transition matrix's combination of depleted-pair count and 100% asymmetry is structurally rare (p <= 0.0001 across all null ensembles).

## Evidence

- **18 depleted transitions** (obs/exp < 0.2, min expected >= 5) identified in Currier B class-to-class matrix
- **100% asymmetric**: every depleted pair A->B has non-depleted reverse B->A. No symmetric depletions exist.
- Depletion ratio criterion used (not zero-count) per C789: forbidden transitions are ~65% compliant, not absolute zeros
- Bootstrap holdout validation: avg Jaccard = 0.072 across 20 splits (specific depleted pairs vary, but asymmetry property persists)

## Null Ensembles (N=10,000 each)

| Ensemble | Description | p(asymmetry >= 100%) | p(joint) |
|----------|-------------|---------------------|----------|
| NULL-A | Density-matched (same zero-fraction) | 0.0000 | 0.0000 |
| NULL-B | Degree-matched (preserved in/out degree) | 0.0000 | 0.0000 |
| NULL-C | Fully random 49x49 | 0.0001 | 0.0001 |

## Interpretation

100% asymmetry means depletion is directional — it suppresses flow in one direction while permitting the reverse. This is consistent with engineered one-way constraints (valves, not walls). Random graphs with matched density produce ~70% asymmetry; 100% is extreme.

## Provenance

- Refines: C109 (forbidden transition pairs), C111 (asymmetric forbidding)
- Method: `phases/FINGERPRINT_UNIQUENESS/scripts/t1_transition_structure.py`
- Results: `phases/FINGERPRINT_UNIQUENESS/results/t1_transition.json`
