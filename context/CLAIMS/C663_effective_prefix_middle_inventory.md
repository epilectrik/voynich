# C663: Effective PREFIX x MIDDLE Inventory

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

## Finding

1,190 distinct (PREFIX, MIDDLE) pairs observed in B text; 501 effective pairs at >=5 tokens (1.24x expansion from 404 MIDDLEs). The space is 89.7% sparse (501 / 4,884 theoretical maximum from 33 PREFIXes x 148 MIDDLEs). PREFIX x MIDDLE pairs cluster better than MIDDLEs alone: best silhouette = 0.350 at k=2 (vs C657's 0.237 for MIDDLEs alone). Optimal k=3 with silhouette = 0.271, above the 0.25 threshold.

However, the k=3 structure is degenerate: one dominant cluster of 129 pairs, with two micro-clusters of 4 and 2 pairs. The k=2 split is the meaningful structure, likely separating EN-role pairs from non-EN-role pairs.

## Evidence

- Observed (PREFIX, MIDDLE) pairs: 1,190
- Effective pairs (>=5 tokens): 501
- Expansion factor from 404 MIDDLEs: 1.24x
- Effective PREFIXes: 33, Effective MIDDLEs: 148
- Theoretical max: 4,884 (33 x 148)
- Sparsity: 0.897
- Clustering (135 pairs with >=20 bigrams):
  - Best: k=2, silhouette=0.350
  - Optimal (highest k with sil>=0.25): k=3, silhouette=0.271
  - C657 MIDDLE-only reference: max silhouette=0.237
- Cluster structure at k=3:
  - Cluster 1: 4 pairs (ch+s, NONE+ar, ch+ar, ch+ee)
  - Cluster 2: 2 pairs (ch+eeo, yk+aiin)
  - Cluster 3: 129 pairs (dominant)

## Interpretation

PREFIX expands the effective PP vocabulary modestly (1.24x, from 404 to 501) because most PREFIX x MIDDLE combinations are too sparse to be effective. Only 501 of 1,190 observed pairs have sufficient frequency (>=5 tokens) to count as real inventory items.

The clustering improvement (0.350 vs 0.237) confirms that PREFIX x MIDDLE pairs are more behaviorally structured than MIDDLEs alone, but the structure is binary (k=2), not richly multi-clustered. The binary split likely reflects the EN/non-EN role dichotomy (C570, C662): EN-PREFIX pairs form one behavioral cluster, non-EN pairs form another.

The degenerate k=3 structure (129 + 4 + 2) suggests that beyond the EN/non-EN split, behavioral variation remains continuous — consistent with C656-C657's continuous landscape within each role regime.

## Cross-References

- C657: PP behavioral continuity (max sil=0.237) — C663 shows PREFIX x MIDDLE pairs improve to 0.350
- C656: PP co-occurrence continuity (sil=0.016) — C663 addresses the MIDDLE-level result with PREFIX
- C570: PREFIX predicts AX vs EN (87.1%) — likely drives the k=2 clustering
- C662: PREFIX reduces class membership by 75% — structural basis for improved clustering
- C661: PREFIX transforms behavior (ratio 0.79) — explains why pairs cluster better

## Provenance

PREFIX_MIDDLE_SELECTIVITY, Script 2 (prefix_middle_interaction.py), Test 7
