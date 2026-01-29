# C703: PP Folio-Level Homogeneity

**Status:** VALIDATED | **Tier:** 2 | **Phase:** CONSTRAINT_BUNDLE_SEGMENTATION | **Scope:** A

## Finding

PP MIDDLE vocabulary distributes **homogeneously** within Currier A folios. Within-bundle PP Jaccard (0.0973) equals between-bundle PP Jaccard (0.0962), ratio 1.01x (Mann-Whitney p=0.356). RI-bearing lines create structural boundaries (non-random placement, Fisher KS p ~ 10^-306) but **not vocabulary boundaries**. There is no vocabulary cliff at RI boundaries (interior/boundary Jaccard ratio = 1.06x, p=0.207).

## Implication

Each line within an A folio samples from the same PP vocabulary pool. The folio-level PP union represents the complete vocabulary specification. Individual lines are redundant partial samples. This explains why individual A records are too restrictive for B filtering (C682: 11/49 classes) — they are fragments of the folio's vocabulary, not independent specifications.

## Key Numbers

| Metric | Value |
|--------|-------|
| Within-bundle PP Jaccard | 0.0973 |
| Between-bundle PP Jaccard | 0.0962 |
| Ratio | 1.01x (no difference) |
| PP diversity (observed vs shuffled) | 0.7387 vs 0.7438 (p=0.336) |
| Boundary discontinuity | 1.06x (p=0.207) |

## Provenance

- Script: `phases/CONSTRAINT_BUNDLE_SEGMENTATION/scripts/vocabulary_coherence.py` (T2.1, T2.3, T2.4)
- Falsifies: RI-bounded bundles as vocabulary coherence units
- Extends: C498 (RI as separate track), C512 (PP section invariance)
