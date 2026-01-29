# RI_BINDING_ANALYSIS

**Status:** COMPLETE | **Constraints:** C719-C721 | **Scope:** A

## Objective

Determine whether RI tokens have semantic binding to co-occurring PP (Model B: RI describes items using PP vocabulary) or are independent labels with no PP relationship (Model A: RI is a pure discrimination marker).

## Key Finding

**Model A confirmed: 0/6 tests pass.** RI has zero functional relationship to co-occurring PP. RI is a folio-scoped discrimination coordinate that labels records without encoding any property of what those records describe.

## Test Results

| Test | Measure | Observed | Null | Ratio | p-value | Result |
|------|---------|----------|------|-------|---------|--------|
| T1: Cross-folio PP similarity | PP Jaccard for shared RI | 0.074 | 0.065 | 1.15 | 3.4e-04 | FAIL |
| T2: Section specificity | Within-section sharing | 76.6% | 71.5% | 1.07 | 7.3e-04 | FAIL |
| T3: PREFIX bifurcation x PP | Chi-squared top-30 PP | — | — | — | 0.28 | FAIL |
| T4: Gallows domain coherence | Cosine similarity | 0.244 | 0.244 | 1.00 | 0.52 | FAIL |
| T5: PP co-occurrence consistency | Mean pairwise Jaccard | 0.070 | 0.066 | 1.05 | 0.32 | FAIL |
| T6: Adjacent PP consistency | Most-common fraction | 0.437 | 0.440 | 0.99 | 0.61 | FAIL |

## Interpretation

RI tokens are inserted into A lines without affecting or being affected by the PP content. The PP on an RI-bearing line is drawn from the same folio-wide pool as PP-pure lines. RI provides 609 distinct discrimination coordinates that make folios maximally orthogonal (C437, Jaccard=0.056) but does not encode properties of what it labels.

C526's "substance anchor" interpretation is weakened: whether RI originally referenced specific substances is irrecoverable from internal structure. RI's structural function is purely discriminative.

C530's within-record gallows enrichment (2-5x) is reinterpreted: gallows coherence is folio-level, not RI-mediated. The folio imposes its gallows domain on all tokens; RI doesn't carry the signal.

## Scripts

| Script | Tests | Output |
|--------|-------|--------|
| `ri_binding_tests.py` | T1-T6 (C719-C721) | `ri_binding_tests.json` |

## Constraints

| # | Name | Key Result |
|---|------|------------|
| C719 | RI-PP Functional Independence | 0/6 binding tests; RI and PP are orthogonal axes |
| C720 | RI Gallows Independence | Gallows coherence is folio-level, not RI-mediated |
| C721 | RI Section Sharing Trivial | 1.07x enrichment explained by section size imbalance |

## Data Dependencies

- `scripts/voynich.py` (canonical transcript library)
- `phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json` (RI/PP classification)

## Cross-References

- C498 (RI vocabulary track): Confirmed — RI does not propagate to B
- C509 (PP/RI dimensional separability): Strengthened — behavioral independence confirmed
- C526 (RI lexical layer): Weakened — "substance anchor" no longer supportable
- C528 (PREFIX bifurcation): Bifurcation exists but does not differentiate PP profiles
- C530 (gallows folio specialization): Refined — enrichment is folio-driven, not RI-driven
- C710-C718 (RI_FUNCTIONAL_IDENTITY): Foundation phase
