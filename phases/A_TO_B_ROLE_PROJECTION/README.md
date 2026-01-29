# A_TO_B_ROLE_PROJECTION

**Phase status:** COMPLETE | **Constraints:** C640-C642 | **Date:** 2026-01-26

## Objective

Project A's 404 PP (Pipeline-Participating) MIDDLEs onto B's 5-role, 49-class instruction system. Test whether AZC-Mediated and B-Native PP populations differ in B-side execution behavior, whether EN sub-family membership is predictable from A record composition, and whether A records show role heterogeneity or material class consistency.

## Key Findings

1. **PP role projection is sparse: 89/404 (22%) match** (C640). B's 480 token types contain only 90 distinct MIDDLEs. PP role distribution differs from B token shares (chi2=42.37, p<0.0001): AUXILIARY over-represented, CORE_CONTROL/FREQUENT_OPERATOR absent. B-Native matched PP is 100% EN-dominant (8/8); AZC-Med spans AX (53.1%), EN (40.7%), FL (4.9%).

2. **Populations differ in B-side behavior** (C641). AZC-Med and B-Native differ in role composition (AX p=0.006, EN p=0.001), REGIME distribution (REGIME_2 p=0.0004, REGIME_3 p<0.0001), and suffix diversity (p<0.0001, frequency-confounded rho=0.795). EN sub-family is partially independent of PREFIX (rho=0.510). QO-dominant A records are smaller (5.5 vs 7.4), have fewer PP, and are ANIMAL-enriched (p=0.003).

3. **A records have weak role coherence and active material mixing** (C642). Co-occurrence lattice: 8.0% density (92% incompatibility). Pair-level role heterogeneity at chance (p=0.55), but record-level role coverage below expected (1.91 vs 2.13, p=0.022). Material consistency BELOW chance (0.6% vs 4.1%, p=0.0006) — records deliberately combine different material classes. No material-role association (V=0.122, NS).

## Verdict

A's PP vocabulary maps non-uniformly onto B's role architecture, with AZC-Mediated MIDDLEs serving diverse B roles and B-Native MIDDLEs serving narrow EN functions. A records show weak role coherence (fewer distinct roles than expected) but actively mix material classes, consistent with multi-material specifications rather than material-specific records. The projection is fundamentally sparse (22% match rate), limiting statistical power for the matched-only comparisons.

## Scripts

| Script | Sections | Output |
|--------|----------|--------|
| `pp_role_foundation.py` | PP-to-role mapping, AZC-Med/B-Native split, role clustering test | `results/pp_role_foundation.json` |
| `population_profiles.py` | Role/hazard profiles, REGIME, suffix, EN sub-family prediction | `results/population_profiles.json` |
| `lattice_material_test.py` | Co-occurrence lattice, role heterogeneity permutation, material consistency permutation | `results/lattice_material_test.json` |

## Data Dependencies

- `scripts/voynich.py`
- `phases/A_INTERNAL_STRATIFICATION/results/middle_classes_v2_backup.json`
- `phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json`
- `phases/PP_CLASSIFICATION/results/pp_classification.json`
- `phases/EN_ANATOMY/results/en_census.json`
- `phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json`

## Critical Notes

- **Class 17 role correction:** class_token_map.json maps class 17 to AUXILIARY, but BCSC v1.4 (C560/C581) reassigns to CORE_CONTROL. Applied before all analyses.
- **22% match rate:** B's class system has only 90 distinct MIDDLEs from 480 token types. 315/404 PP MIDDLEs have no B-class assignment.
- **B-Native tiny sample:** Only 8 B-Native PP MIDDLEs match B classes (vs 81 AZC-Med). All matched-only comparisons are severely underpowered for B-Native.
- **Frequency confound:** AZC-Med median B-frequency = 9 vs B-Native median = 2 (p<0.0001). Suffix and diversity comparisons are confounded.
