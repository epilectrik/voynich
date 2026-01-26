# Archived Temp Scripts: 2026-01-23

**Date:** January 22-23, 2026
**Total Scripts:** 87
**Total Lines:** ~16,710
**Context:** Intensive research sprint on PP/RI structure, Brunschwig cross-validation, and pharma label analysis

---

## Categories

### PP (Product Properties) Analysis (19 files)
Scripts investigating PP token behavior, correlations, and structural properties.

| Script | Purpose |
|--------|---------|
| temp_pp_action_test.py | PP action correlation testing |
| temp_pp_b_execution.py | PP behavior in Currier B execution |
| temp_pp_b_profile_test.py | PP profile in B system |
| temp_pp_class_specificity.py | PP class-specific patterns |
| temp_pp_cluster_geometry.py | PP clustering analysis |
| temp_pp_count_correlation.py | PP count correlation |
| temp_pp_entropy_collapse.py | PP entropy analysis |
| temp_pp_fire_correlation.py | PP correlation with fire degrees |
| temp_pp_from_survivors.py | PP extraction from survivor sets |
| temp_pp_ht_interaction.py | PP and Human Track interaction |
| temp_pp_ht_proper.py | PP-HT proper analysis |
| temp_pp_only_analysis.py | PP-only token analysis |
| temp_pp_permutation_test.py | PP permutation significance testing |
| temp_pp_property_test.py | PP property validation |
| temp_pp_scope.py | PP scope analysis |
| temp_pp_sharing_structure.py | PP sharing structure |
| temp_pp_token_test.py | PP token testing |
| temp_pp_token_test2.py | PP token testing (v2) |
| temp_multiclass_pp_test.py | Multi-class PP testing |

### RI/MIDDLE Analysis (16 files)
Scripts analyzing RI (A-exclusive) tokens and MIDDLE morphology.

| Script | Purpose |
|--------|---------|
| temp_ri_complexity_test.py | RI complexity metrics |
| temp_ri_cooccurrence.py | RI co-occurrence patterns |
| temp_ri_pp_distribution.py | RI vs PP distribution |
| temp_ri_pp_morphology_comparison.py | RI/PP morphological comparison |
| temp_ri_pp_sharing.py | RI-PP sharing analysis |
| temp_ri_prefix_test.py | RI prefix patterns |
| temp_ri_repeats.py | RI repetition patterns |
| temp_ri_structure_analysis.py | RI structural analysis |
| temp_ri_token_survival.py | RI token survival rates |
| temp_rid_position_check.py | RID positional analysis |
| temp_rid_token_uniqueness.py | RID token uniqueness |
| temp_middle_decomposition.py | MIDDLE decomposition |
| temp_middle_subcomponent_analysis.py | MIDDLE sub-component analysis |
| temp_first_token_ri.py | First-token RI patterns |
| temp_find_by_middle.py | Find tokens by MIDDLE |
| temp_verify_token_middle.py | Token-MIDDLE verification |

### Brunschwig Cross-Validation (8 files)
Scripts comparing Voynich structure to Brunschwig pharmaceutical sources.

| Script | Purpose |
|--------|---------|
| temp_brunschwig_properties.py | Brunschwig property extraction |
| temp_brunschwig_sequences.py | Brunschwig sequence analysis |
| temp_brunschwig_stats.py | Brunschwig statistics |
| temp_check_late_balneum.py | Late balneum verification |
| temp_check_riech.py | Riech reference checking |
| temp_dilution_validation.py | Dilution pattern validation |
| temp_water_gentle_pp.py | Water/gentle processing patterns |
| temp_verify_fachys.py | Fachys reference verification |

### Pharma Label Analysis (5 files)
Scripts analyzing pharmaceutical section labels (jars, roots, leaves).

| Script | Purpose |
|--------|---------|
| temp_jar_compression_check.py | Jar label compression analysis |
| temp_jar_content_compatibility.py | Jar-content PP compatibility |
| temp_jar_label_check.py | Jar label vocabulary check |
| temp_label_constraint_validation.py | Label constraint validation |
| temp_label_in_currier_a.py | Labels in Currier A vocabulary |
| temp_pharma_label_analysis.py | Pharma label PP analysis |

### Class/Classification (6 files)
Scripts testing classification and class structure.

| Script | Purpose |
|--------|---------|
| temp_class_analysis.py | Class structure analysis |
| temp_class_breakdown.py | Class breakdown |
| temp_class_overlap.py | Class overlap testing |
| temp_classify_sensory.py | Sensory classification |
| temp_intraclass_heterogeneity.py | Intra-class heterogeneity |
| temp_product_types.py | Product type analysis |

### Sensory/Material Analysis (6 files)
Scripts extracting and analyzing sensory properties.

| Script | Purpose |
|--------|---------|
| temp_search_sensory.py | Sensory property search |
| temp_sensory_analysis.py | Sensory analysis |
| temp_sensory_extract.py | Sensory extraction |
| temp_sensory_manual_review.py | Manual sensory review |
| temp_find_animals.py | Animal material identification |
| temp_find_validated_materials.py | Validated material search |

### Fire Degree Validation (3 files)
Scripts verifying fire degree patterns.

| Script | Purpose |
|--------|---------|
| temp_fire_degree_audit.py | Fire degree audit |
| temp_fire_pp_test.py | Fire-PP correlation test |
| temp_verify_fire_degrees.py | Fire degree verification |

### Section/Boundary Analysis (6 files)
Scripts analyzing section and boundary structure.

| Script | Purpose |
|--------|---------|
| temp_boundary_function.py | Boundary function analysis |
| temp_boundary_section_test.py | Boundary-section testing |
| temp_boundary_section_test2.py | Boundary-section testing (v2) |
| temp_section_progression.py | Section progression |
| temp_section_signatures.py | Section signatures |
| temp_section_spans.py | Section span analysis |

### Process/Procedural Analysis (5 files)
Scripts analyzing procedural structure.

| Script | Purpose |
|--------|---------|
| temp_analyze_procedures.py | Procedure analysis |
| temp_procedural_structure.py | Procedural structure |
| temp_process_type_test.py | Process type testing |
| temp_token_operation_test.py | Token operation testing |
| temp_token_process_test.py | Token process testing |

### Miscellaneous (13 files)
Other verification and analysis scripts.

| Script | Purpose |
|--------|---------|
| temp_action_to_pp.py | Action-to-PP mapping |
| temp_aux_cooccurrence.py | Auxiliary co-occurrence |
| temp_aux_middle_requirements.py | Auxiliary MIDDLE requirements |
| temp_azc_filtering_test.py | AZC filtering test |
| temp_extract_lines.py | Line extraction |
| temp_folio_coverage.py | Folio coverage analysis |
| temp_legality_viz.py | Legality visualization |
| temp_legality_viz2.py | Legality visualization (v2) |
| temp_prefix_check.py | PREFIX checking |
| temp_prefix_pattern_analysis.py | PREFIX pattern analysis |
| temp_reference_vs_operation.py | Reference vs operation |
| temp_verify_177.py | C177 verification |

---

## Articulator/Extraction Correction Session (Jan 24, 2026)

Additional ~59 scripts added from methodology correction session:

### Key Scripts

| Script | Purpose |
|--------|---------|
| temp_correct_extraction.py | Proper articulator-before-prefix handling |
| temp_closure_token_check.py | Closure token (SUFFIX-only) classification |
| temp_closure_middle_check.py | MIDDLE extraction from closure tokens |
| temp_articulator_check.py | Articulator pattern verification |
| temp_articulator_middle_sharing.py | Articulator/MIDDLE sharing analysis |
| temp_prefixless_position.py | Prefix-less token positional analysis |
| temp_prefixless_structure.py | Prefix-less token internal structure |
| temp_y_initial_class.py | Y-initial MIDDLE class analysis |

### RI Extraction Verification

| Script | Purpose |
|--------|---------|
| temp_ri_analysis.py, temp_ri_count.py | RI count verification |
| temp_ri_definitive_count.py | Definitive RI count |
| temp_ri_localization.py | RI folio localization |
| temp_ri_prefix_section_test.py | RI prefix by section |
| temp_ri_proper_extraction.py | Corrected RI extraction |
| temp_ri_length_*.py | RI length distribution analysis |

### Suffix/Prefix Analysis

| Script | Purpose |
|--------|---------|
| temp_suffix_*.py (8 files) | Suffix position, pairing, validation |
| temp_prefix_*.py (4 files) | Prefix overlap, behavior analysis |

### Constraint Verification

| Script | Purpose |
|--------|---------|
| temp_c498a_reverification.py | C498.a re-verification |
| temp_c499_*.py (3 files) | C499 coverage and consistency |

### Outcome

This session led to creation of canonical `scripts/voynich.py` library.

---

## Associated JSON Results

Located in `archive/reports/`:
- temp_pp_cluster_results.json
- temp_ri_pp_sharing_results.json
- temp_sensory_result.json
- temp_c498a_results.json
- temp_middle_classes_v2.json
- temp_ri_definitive_results.json

---

## Notes

- Scripts use `PROJECT_ROOT = Path(__file__).parent` - paths may need adjustment if running from archive
- Most scripts filter to `transcriber == 'H'` (primary track) per project convention
- Scripts are preserved for reference and reproducibility, not necessarily for re-running
