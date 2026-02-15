# C1041: A Paragraph Complementary Diversification

**Tier:** 2
**Scope:** Currier-A
**Phase:** A_PARAGRAPH_COMBINATORICS (Phase 364)

## Constraint

A paragraphs have LOWER cross-line MIDDLE compatibility than random line shuffles within the same folio. Paragraphs group COMPLEMENTARY entries that cover different parts of the compatibility space, not redundant entries from the same compatibility neighborhood.

## Evidence

Cross-line compatibility density (fraction of MIDDLE pairs from different lines within a paragraph that are C475-legal):

| Metric | Value |
|--------|-------|
| Observed mean density | 0.6996 |
| Null mean density (shuffled) | 0.7071 |
| Null std | 0.0021 |
| z-score | -3.567 |
| p-value (for enrichment) | 1.000 |
| Paragraphs tested | 239 (>= 2 lines with indexed MIDDLEs) |

Null model: shuffle lines across paragraphs within same folio (1000 permutations), maintaining paragraph sizes.

PP MIDDLEs show less deficit (z_pp=-2.58 vs z_all=-3.57), consistent with RI MIDDLEs driving the diversification signal.

## Interpretation

This finding directly extends C476 (coverage optimality). The coverage optimization principle operates at paragraph level: paragraphs are constructed to maximize discrimination coverage, not to group co-processable items. Each line contributes a different facet of the discrimination space. Combined with C1039 (cluster selectivity), this creates a coherent picture: paragraphs select from a SUBSET of clusters (narrowing the space) but within that subset, they diversify across compatibility neighborhoods (maximizing coverage within the selected subspace).

## Supports

- **C233:** LINE_ATOMIC -- each line is an independent entry
- **C476:** Coverage optimality
- **C755:** A folio coverage homogeneity

## Note on H2

The PP vs RI decomposition (z_pp=-2.58 vs z_all=-3.57) suggests RI MIDDLEs contribute more to the below-random diversification signal. This is consistent with RI MIDDLEs being paragraph-specific (C831) while PP MIDDLEs are shared across the broader vocabulary pool.

## Provenance

- 239 paragraphs with >= 2 lines, 1000 permutations
- Data: `phases/A_PARAGRAPH_COMBINATORICS/results/a_paragraph_combinatorics.json`
