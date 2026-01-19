# ZONE_MODALITY_VALIDATION Phase

## Purpose

Rigorously test whether AZC zones ADDRESS sensory modalities through their structural affordances, with proper falsification criteria, enhanced sensory extraction, and a solution for the C-zone problem.

## Background

F-BRU-009 established correlations between AZC zones and sensory modalities:
- P-zone (intervention-permitting) → SIGHT (t=9.00, p<0.0001)
- R-zone (progressive restriction) → SOUND (t=3.97, p<0.001)
- S-zone (locked/boundary) → TOUCH (n=5, not significant)
- C-zone (setup/flexible) → ??? (not tested)

**Key Insight:** Zones don't ENCODE sensory categories; they ADDRESS them through structural affordances that align with monitoring requirements.

## Research Tracks

### Track 1: Enhanced Sensory Extraction
Expand keyword lists to capture missing SMELL/TOUCH instances.

### Track 2: C-Zone Structural Test
Test hypothesis that C-zone correlates with preparation verbs, not sensory modalities.

### Track 3: Statistical Strengthening
Add effect sizes (Cohen's d), permutation tests, Bonferroni correction.

### Track 4: Pre-Registered Falsification
Document falsification criteria before running tests.

## Scripts

| Script | Purpose |
|--------|---------|
| `enhanced_sensory_extraction.py` | Expand keyword lists, re-extract sensory content |
| `czone_structural_test.py` | Test C-zone against preparation verb density |
| `modality_zone_validation.py` | Full statistical validation with corrections |

## Constraints Respected

- **C384:** All tests aggregate, no entry-level mapping
- **C469:** Categorical zone assignment maintained
- **Tier 3:** Results remain characterization, not constraint

## Output Files

- `results/enhanced_sensory_extraction.json`
- `results/czone_structural_test.json`
- `results/modality_zone_validation.json`
- `ZONE_MODALITY_REPORT.md`
