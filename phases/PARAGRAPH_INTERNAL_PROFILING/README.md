# PARAGRAPH_INTERNAL_PROFILING

**Status:** COMPLETE
**Date:** 2026-01-29
**Constraints:** C847-C854

## Purpose

Profile internal variation within A paragraphs (A-A) and B paragraphs (B-B) to understand paragraph types and cross-system structural parallels.

## Key Finding

Both A and B paragraphs exhibit **parallel header-body architecture**:
- Line 1 enriched with marking vocabulary (A: RI 3.84x; B: HT +0.134 delta)
- Body zone dominated by operational vocabulary
- Line counts statistically indistinguishable (A: 4.8, B: 4.37, p=0.067)
- Both systems cluster into 5 natural paragraph types

## Scripts

| Script | Purpose |
|--------|---------|
| 00_build_paragraph_inventory.py | GATE: Build paragraph inventories |
| 01_a_size_density_profile.py | A size/density metrics |
| 02_a_ri_profile.py | A RI composition |
| 03_a_pp_composition.py | A PP composition |
| 04_a_position_section_effects.py | A position/section effects |
| 05_b_size_density_profile.py | B size/density metrics |
| 06_b_ht_variance.py | B HT variance |
| 07_b_gallows_markers.py | B gallows/markers |
| 08_b_role_composition.py | B role composition |
| 09_b_section_effects.py | B section effects |
| 10_cross_system_summary.py | A-B comparison |
| 11_paragraph_clustering.py | Clustering analysis |

## Dependencies

- C827: Paragraph operational unit
- C831: RI three-tier structure
- C840-C845: B paragraph structure
- C552: Section-role profiles

## Results

See `FINDINGS.md` for detailed analysis.
