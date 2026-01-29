# C708: Inter-Folio PP Discrimination

**Status:** VALIDATED | **Tier:** 2 | **Phase:** FOLIO_LEVEL_FILTERING | **Scope:** A-B

## Finding

A folios maintain **PP MIDDLE discrimination** despite folio-level pooling. Mean inter-folio PP Jaccard = 0.274 (range 0.067-0.500). Different folios specify different PP vocabularies. However, at the B CLASS level, Jaccard = 0.83 — different PP vocabularies converge on similar class compositions. This two-level discrimination (token-divergent, class-convergent) is consistent with the Tier 0 conclusion that B programs maintain a narrow viability regime.

## Key Numbers

| Level | Mean Jaccard | Interpretation |
|-------|-------------|----------------|
| PP MIDDLE (A input) | 0.274 | Discriminative (folios select different MIDDLEs) |
| Legal B TOKEN | — | Mediated by C502.a filtering |
| Legal B CLASS | 0.830 | Convergent (folios produce similar class sets) |

## References

| Comparison | Jaccard | Context |
|------------|---------|---------|
| C437 AZC folio orthogonality | 0.056 | AZC is maximally discriminative |
| C689 single-record fingerprints | 0.199 | Records are more discriminative than folios |
| This constraint (folio PP) | 0.274 | Folios pool toward shared vocabulary |
| This constraint (folio CLASS) | 0.830 | But converge at class level |

## Interpretation

The A→B filtering architecture has **funnel topology**: diverse PP inputs (Jaccard 0.274) converge through C502.a morphological filtering to produce similar B class repertoires (Jaccard 0.830). This convergence is the mechanism that enforces the narrow viability regime. Individual A folios specify different vocabulary slices, but the B grammar's class structure ensures that most folios enable similar operational capability.

## Provenance

- Script: `phases/FOLIO_LEVEL_FILTERING/scripts/folio_level_filtering.py` (T3.5)
- Extends: C437 (AZC orthogonality), C689 (record fingerprints)
