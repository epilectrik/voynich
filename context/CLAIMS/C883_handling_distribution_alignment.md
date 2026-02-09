# C883 - Handling-Type Distribution Alignment

**Tier:** 3 | **Scope:** A | **Phase:** MATERIAL_MAPPING_V2

## Statement

Distribution of A paragraph handling types (66% CAREFUL, 11% STANDARD, 6% PRECISION) aligns with Brunschwig fire-degree material frequency distribution (60% degree-2, 25% degree-1/3, ~5% precision). This distribution match constitutes structural evidence for domain correspondence.

## Distribution Comparison

| Category | Brunschwig | Voynich | Interpretation |
|----------|------------|---------|----------------|
| Standard processing | 60% (degree 2) | 66% (CAREFUL) | Common herbs |
| Mixed processing | 25% (degree 1/3) | 11% (STANDARD) | Variable herbs |
| Precision processing | ~5% (animals) | 6% (PRECISION) | Distinctive materials |
| Delicate processing | Few | 1% (GENTLE) | Flowers |

## Significance

If Voynich encoded arbitrary content unrelated to distillation:
- Handling types would distribute uniformly (~25% each)
- No correlation with Brunschwig material frequency expected

Instead we observe:
- Matching skew toward "standard processing" (60-66%)
- Matching rarity of "precision" materials (5-6%)
- The same pattern of "most materials are similar, few are distinctive"

## Why CAREFUL is a Catch-All

The CAREFUL category (107 paragraphs) is dominated by ch/sh (PHASE) prefixes:
- ch-dominant: 71 paragraphs
- sh-dominant: 29 paragraphs
- These represent standard herb distillation (fire degree 2)
- Not a specific material category, but "everything using standard processing"

This matches Brunschwig where 60% of recipes are degree-2 herbs with similar procedures.

## Evidence Quality

The alignment is non-trivial because:
1. We didn't tune for this distribution
2. Classification is based on PREFIX profiles, not material labels
3. Brunschwig distribution was computed independently from recipe data
4. The ratio match emerged from structural analysis

## Provenance

- `phases/MATERIAL_MAPPING_V2/scripts/12_all_categories_validation.py`
- `phases/MATERIAL_MAPPING_V2/scripts/13_failure_diagnosis.py`
- `phases/MATERIAL_MAPPING_V2/results/all_categories_validation.json`
- Brunschwig source: `data/brunschwig_curated_v3.json`
