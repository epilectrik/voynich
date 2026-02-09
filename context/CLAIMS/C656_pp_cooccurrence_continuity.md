# C656: PP Co-Occurrence Continuity

**Tier:** 2 | **Status:** CLOSED | **Scope:** A

## Finding

PP MIDDLEs (404 total, 203 with ≥3 A-record occurrences) form a continuous co-occurrence space with no discrete pools.

> **Aggregation Note (2026-01-30):** This constraint analyzes PP co-occurrence at line level
> (1,553 A records). Per C881, A records are paragraphs (342 units). Per C885, the
> operational unit for A-B vocabulary correspondence is the A FOLIO (114 units, 81% coverage).

Jaccard similarity matrix: 76.0% zero pairs, mean non-zero Jaccard=0.023, max=0.246. Hierarchical clustering (UPGMA, Ward) yields maximum silhouette of 0.016 across k=2..20 (threshold: 0.25). All 203 filtered PP form a single connected component. Within-Herbal analysis confirms (163 PP, sil=0.020). Section NMI=0.087 — section membership does not drive co-occurrence.

## Evidence

- 1553 A records with PP content, 404 PP MIDDLEs (201 appear in <3 records, excluded)
- 203×203 Jaccard matrix: 20,503 pairs, 15,584 zero (76.0%), 4,919 non-zero (24.0%)
- Non-zero Jaccard: mean=0.023, median=0.014, max=0.246
- UPGMA silhouette: k=2: 0.005, k=5: 0.005, k=10: 0.008, k=20: 0.016 — monotonically increasing but always < 0.025
- Ward silhouette: k=20: 0.018 — same pattern
- Complete linkage: degenerate (no valid silhouette)
- Baseline k=4 (material class): sil=0.005; k=2 (pathway): sil=0.005
- Within-Herbal: 163 PP, sil=0.020, consistency ARI with full data=0.406
- Degree stats: mean=48.5 partners, median=32, max=189, zero isolated

## Interpretation

PP co-occurrence in A records is extremely sparse and continuous. No natural partition of the PP vocabulary into discrete functional pools exists at the record level. The single connected component means all PP are reachable through chains of shared records, and the low Jaccard values (max 0.246) mean even the most tightly co-occurring pairs share only ~25% of their records. PP vocabulary is a continuous landscape, not a set of discrete bins.

## Cross-References

- C509: Only 72 distinct PP sets across 229 records — low-dimensional but still continuous
- C475: 95.7% MIDDLE incompatibility — high global sparsity is consistent
- C631: Within-class MIDDLE distributions mostly continuous (extended to cross-class PP)
- C642: A records actively mix material classes — consistent with gradient structure

## Provenance

PP_POOL_CLASSIFICATION, Script 1 (pp_cooccurrence_clustering.py), Tests 1-2, 4
