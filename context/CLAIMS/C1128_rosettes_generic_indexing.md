# C1128: Rosettes Generic (Not Specific) Indexing

**Tier:** 2
**Status:** Active
**Scope:** Rosettes foldout
**Phase:** 402 (ROSETTES_SYSTEM_REVALIDATION)

## Finding

The 9 rosettes function as a **generic** vocabulary index — all rosettes point to approximately the same set of B folios rather than each rosette targeting distinct folios.

Evidence:
- Top-5 most-overlapping B folios per rosette show high convergence: mean inter-rosette Jaccard of top-5 sets = 0.322
- f40v appears in the top-5 for 8/9 rosettes (all except EAST)
- f95r2, f94r, f40r, f95v2 also appear repeatedly across rosettes
- MIDDLE compatibility: 9.6% pairwise (2.2x baseline), indicating moderate but not exceptional vocabulary coherence

Spatial tests showed no significant structure:
- Path tokens do not bridge endpoint rosette vocabularies (P1: mean Jaccard 0.021, same as random)
- Vocabulary similarity does not decay with spatial distance (P2: Spearman rho = -0.185, not significant at n=36)

## Evidence

- Tests X3, P1, P2 in Phase 402 battery
- 9 rosettes x 83 B folios = 747 Jaccard comparisons
- 36 rosette pairs for adjacency gradient analysis

## Implication

The Rosettes foldout vocabularies all sample from the same shared pool, concentrated in Section T folios. Individual rosettes do not discriminate specific B folios or topics. The foldout functions more as a shared vocabulary hub for pharmaceutical content than as a specific lookup table mapping rosettes to target folios.

## Provenance

- Source: Phase 402, Tests X3, P1, P2
- Related: C1124 (bridge enrichment), C1125 (Section T correlation)
