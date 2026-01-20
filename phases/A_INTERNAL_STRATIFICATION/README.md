# Phase: A-INTERNAL-STRATIFICATION

**Date:** 2026-01-20
**Status:** IN PROGRESS
**Hypothesis:** A-exclusive MIDDLEs (never appear in B) and A/B-shared MIDDLEs may have different functional roles within Currier A itself.

## Background

Current model treats all Currier A tokens as "discrimination markers" uniformly. However:
- C383 establishes that same tokens have different functions in A vs B
- C443 shows position-indexed behavior differences in AZC
- f49v vs f76r shows single characters have different roles by context

**Question:** Is Currier A internally homogeneous, or does it contain functional stratification between A-exclusive and A/B-shared vocabulary?

## MIDDLE Classes

| Class | Count | Definition |
|-------|-------|------------|
| A-exclusive | 349 | MIDDLEs appearing in Currier A but never in Currier B |
| A/B-shared | 268 | MIDDLEs appearing in both Currier A and Currier B |

## Tests

| # | Test | Question | Method |
|---|------|----------|--------|
| 1 | Position | Openers vs closers vs interior? | Chi-square |
| 2 | Section | Concentrate in H, P, or T? | Chi-square |
| 3 | Folio | Cluster in specific folios? | KS test |
| 4 | Adjacency | Different clustering behavior? | Chi-square |
| 5 | Morphology | Different PREFIX/SUFFIX profiles? | Chi-square |
| 6 | AZC Presence | Appear in AZC at all? | Fisher's exact |
| 7 | Entry Composition | Pure vs mixed entries? | Chi-square |
| 8 | Frequency Control | Are effects frequency artifacts? | Partial correlation |

## Interpretation Thresholds

- Effect size (Cramér's V or Cohen's d) > 0.1 with p < 0.00625 (Bonferroni corrected)
- Effects must survive frequency control to be considered real

## Outcome Framework

| Outcome | Criteria | Implication |
|---------|----------|-------------|
| CONFIRMED | 5+ tests pass, survive frequency control | A has internal functional stratification |
| PARTIAL | 2-4 tests pass, inconsistent | Secondary distinction (Tier 3) |
| NULL | 0-1 tests pass | A is internally homogeneous |

## Constraints at Risk

None at Tier 0. May refine: C293, C383, C423, C475, C476.

## Files

- `scripts/prepare_middle_classes.py` - Establish A-exclusive vs shared classification
- `scripts/test_1_positional_distribution.py` - Position within entries
- `scripts/test_2_section_distribution.py` - Section concentration
- `scripts/test_3_folio_clustering.py` - Folio spread
- `scripts/test_4_adjacency_patterns.py` - Clustering behavior
- `scripts/test_5_morphological_profile.py` - PREFIX/SUFFIX distributions
- `scripts/test_6_azc_presence.py` - AZC participation
- `scripts/test_7_entry_composition.py` - Pure vs mixed entries
- `scripts/test_8_frequency_control.py` - Frequency confound analysis
- `scripts/synthesize_results.py` - Combine results
- `results/stratification_tests.json` - All test outputs
