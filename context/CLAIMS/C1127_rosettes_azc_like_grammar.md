# C1127: Rosettes AZC-Like Grammar Profile

**Tier:** 2
**Status:** Active
**Scope:** Rosettes foldout
**Phase:** 402 (ROSETTES_SYSTEM_REVALIDATION)
**Supersedes:** C1088 (deleted — hybrid classification built on incomplete data)

## Finding

The Rosettes foldout grammar profile is **AZC-like**, not hybrid as previously classified. All entity types (ring, labels, paths, spiral, clock) show consistent AZC affinity:

- **Grammar coverage:** 42.0% overall (B reference: ~100%, AZC: ~50%)
- **Kernel density:** 29-41% across types (B: 53.8%, AZC: 44.1%)
- **LINK density:** Ring text 4.2% (B-like), all other types <2.1%
- **Morphological profile:** All entity types match AZC most closely (cosine 0.49-0.82 with AZC vs 0.25-0.67 with B)
- **Forbidden transitions:** 0/277 ring text bigrams violate B forbidden pairs
- **PP/RI composition:** ~50% PP, ~2% RI, ~48% unclassified — not A-like (would expect >15% RI)

The old hybrid classification (C1088) reflected data artifacts from the incomplete EVA transcript. With corrected data, the profile is consistently AZC-like with B-compliant transition grammar.

## Evidence

- Tests S1-S6 in Phase 402 battery
- 443 tokens across 6 sub-region types
- Reference baselines computed from full B, A, and AZC corpora

## Implication

The Rosettes foldout uses AZC-type morphology (prefix/suffix distributions, kernel density) while respecting B-type transition rules (zero forbidden violations). This is consistent with a positional encoding system (like AZC diagram positions) rather than executable programs (B) or registry entries (A).

## Provenance

- Source: Phase 402, Tests S1-S6
- Related: C757 (AZC zero kernel/LINK), C311 (AZC positional grammar)
