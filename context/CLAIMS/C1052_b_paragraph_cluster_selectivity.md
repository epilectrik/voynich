# C1052: B Paragraphs Show Cluster Selectivity

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** B
**Phase:** PARAGRAPH_GRADIENT_COMBINATORICS (Phase 368)
**Extends:** C1039 (A paragraph cluster selectivity)
**Relates to:** C475 (MIDDLE incompatibility), C932 (body vocabulary gradient)

---

## Statement

B paragraphs draw preferentially from fewer C475 compatibility clusters than expected by random MIDDLE-to-cluster assignment, replicating C1039 (established on Currier A) on Currier B.

| Metric | Value |
|--------|-------|
| Observed mean entropy | 1.512 |
| Null mean entropy | 1.824 |
| z-score | -2.614 |
| p-value | 0.007 |
| B paragraphs tested | 73 (8+ lines) |

B paragraph cluster selectivity (z=-2.61) is comparable to A paragraph selectivity (C1039: z=-2.83). Both systems constrain paragraph MIDDLE composition within the C475 compatibility graph.

---

## Gradient Decomposition

Cluster selectivity is NOT uniformly distributed across the paragraph body. The specification zone (Q0-Q1) shows HIGHER entropy (1.379) than the execution zone (Q3-Q4, entropy 1.291). Execution-zone MIDDLEs are more cluster-concentrated than specification-zone MIDDLEs.

| Zone | Cluster Entropy | Interpretation |
|------|----------------|----------------|
| Specification (Q0-Q1) | 1.379 | Broader cluster sampling |
| Execution (Q3-Q4) | 1.291 | More concentrated |

This means the "generic execution loop" (C932) is not generic in the sense of sampling broadly — it converges on specific compatibility neighborhoods.

---

## Method

- 73 B paragraphs with 8+ lines, sections B/H/S
- 5-cluster GMM on spectral embedding of 972×972 compatibility matrix (same as Phase 364)
- Cluster sizes: {0: 23, 1: 106, 2: 130, 3: 351, 4: 362}
- Null: shuffle MIDDLE→cluster mapping (1000 permutations)
- Coverage: 250/542 B MIDDLEs in A-derived matrix (46.1%)

**Script:** `phases/PARAGRAPH_GRADIENT_COMBINATORICS/scripts/paragraph_gradient_combinatorics.py`
**Results:** `phases/PARAGRAPH_GRADIENT_COMBINATORICS/results/paragraph_gradient_combinatorics.json`
