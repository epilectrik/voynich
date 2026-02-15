# C1039: A Paragraph Cluster Selectivity

**Tier:** 2
**Scope:** Currier-A
**Phase:** A_PARAGRAPH_COMBINATORICS (Phase 364)

## Constraint

A paragraphs draw preferentially from fewer C475 compatibility clusters than expected by random MIDDLE-to-cluster assignment. Paragraphs are cluster-selective but not cluster-exclusive.

## Evidence

Shannon entropy of paragraph cluster composition vectors (5-cluster GMM from t4 topology):

| Metric | Value |
|--------|-------|
| Observed mean entropy | 1.502 |
| Null mean entropy (shuffled) | 1.780 |
| z-score | -2.830 |
| p-value | 0.002 |
| Max entropy (by cluster proportion) | 1.926 |
| Paragraphs tested | 245 (>= 3 MIDDLEs with cluster assignment) |

Null model: shuffle MIDDLE-to-cluster mapping (1000 permutations), preserving cluster proportions.

## Interpretation

Paragraphs tend to specialize within the compatibility graph, exploring a subset of the cluster space. This is consistent with paragraphs representing distinct discrimination contexts within a folio. Combined with C1041 (diversification), this creates a picture where each paragraph covers a different "region" of the discrimination space while sampling broadly within that region.

## Supports

- **C475:** MIDDLE incompatibility operates at cluster level
- **C850:** A paragraph cluster taxonomy (5 types by size/RI)
- **C881:** A record paragraph structure

## Provenance

- Computed from 342 A paragraphs
- GMM k=5 clustering reproduced from t4_incompatibility_topology (same random_state=42)
- Data: `phases/A_PARAGRAPH_COMBINATORICS/results/a_paragraph_combinatorics.json`
