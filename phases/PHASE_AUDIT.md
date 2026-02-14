# Phase Directory Audit

**Date:** 2026-02-14 | **Total Directories:** 352

## Summary

| Category | Count | Description |
|----------|-------|-------------|
| **COMPLETE** | 157 | Both `scripts/` and `results/` subdirectories with files |
| **SCRIPT_ONLY** | 6 | Scripts present, no results files (all confirmed complete — console output documented in markdown) |
| **RESULTS_ONLY** | 20 | Results present, no scripts (17 orphans recovered from legacy `results/`, 3 pre-existing) |
| **DOCS_ONLY** | 66 | Have README/planning docs but no scripts or results subdirectories |
| **MIXED_LEGACY** | 103 | Have scripts/results/docs mixed directly in phase directory (predates subdirectory convention) |
| **TRULY_EMPTY** | 0 | — |

**Verdict:** No truly empty directories. All 352 phase directories contain something. The project is in reasonable shape — 266 phases (157 COMPLETE + 6 SCRIPT_ONLY + 103 MIXED_LEGACY) have analysis artifacts. The 66 DOCS_ONLY are planning/documentation phases. The 20 RESULTS_ONLY are orphaned results recovered from the legacy `results/` directory.

---

## Remediation Performed (2026-02-14)

22 files were copied from `results/` (legacy) into 19 phase directories. Originals preserved in `results/`.

| Phase Directory | File(s) Copied |
|----------------|----------------|
| A_BUNDLE_GENERATOR | a_bundle_generator.json |
| A_LABEL_INTERFACE_ROLE | label_interface_role.json |
| A_ORCHESTRATION_TEST | a_orchestration_test.json |
| COVERAGE_OPTIMALITY | coverage_optimality.json |
| CSM_control_signature | control_signatures.json |
| ENTITY_MATCHING_CORRECTED | entity_matching_corrected.json |
| GALLOWS_B_COMPATIBILITY | gallows_distribution.json |
| HT_VARIANCE_DECOMPOSITION | ht_variance_decomposition.json |
| INTEGRATION_PROBE | integration_probe_azc_unique.json, integration_probe_middle_azc.json, integration_probe_prefix_azc.json, integration_probe_synthesis.md |
| MIDDLE_AB | middle_ab_overlap.json |
| MIDDLE_INCOMPATIBILITY | middle_incompatibility.json |
| MIDDLE_ZONE_SURVIVAL | middle_zone_survival.json |
| perturbation_space | perturbation_space_analysis.json |
| PTEXT_FOLIO_ANALYSIS | test1_ptext_reclassification.json |
| SCIENTIFIC_CONFIDENCE | scientific_confidence_classification.json |
| SHARED_COMPLEXITY | shared_complexity.json |
| SURVIVOR_SET_COUNT | survivor_set_count.json |
| TEMPORAL_TRAJECTORIES | temporal_trajectories.json |
| TRANSCRIPT_AUDIT | transcript_audit.json |

---

## SCRIPT_ONLY Phases (6) — All Confirmed Complete

These phases use console output (print statements) and document results in README.md or RESULTS.md. No missing data.

| Phase | Scripts | Constraints Produced | Status |
|-------|---------|---------------------|--------|
| ACTION_SEQUENCE_TEST | 4 | C539 | CLOSED |
| AZC_PIPELINE_VALIDATION | 2 | Validated C502/C481 | CLOSED |
| CONTROL_LOOP_SYNTHESIS | 6 | C810-C814 | CLOSED |
| LINE_BOUNDARY_OPERATORS | 4 | Extended C298.a | CLOSED |
| LINK_OPERATOR_ARCHITECTURE | 6 | C804-C809 | CLOSED |
| MIDDLE_COVERAGE_ANALYSIS | 9 | C906-C907, F-BRU-014 | CLOSED |

---

## Category: DOCS_ONLY (66)

Phases with planning/documentation files but no scripts or results subdirectories. These are typically:
- Early phases documented inline before the subdirectory convention
- Planning phases that produced constraints documented elsewhere
- Phases whose analysis scripts are in `archive/scripts/`

<details>
<summary>Full list (66 phases)</summary>

A-ARCH_global_type_system, APP_1_apparatus_validation, AZC_PATTERN_AUDIT, AZC_astronomical_zodiac_cosmological, BPF_b_prefix_function, BRUNSCHWIG_COMPLEMENTARITY, BSA_boundary_sensitivity_audit, BSF_b_suffix_function, BVP_b_vocabulary_patterns, CAS_FOLIO_folio_coherence, CAS_XREF_cross_reference_structure, CDCE_cross_domain, DAI_daiin_analysis, EXT1_external_procedure_isomorphism, EXT2_historical_process_matching, EXT3_failure_hazard_alignment, EXT4_material_botanical_correlation, EXT5A_role_classification, EXT5B_use_context_mapping, EXT6_institutional_compatibility, EXT7_structural_parallel_search, FG_folio_gap_analysis, FMR_failure_mode_reconstruction, FM_PHY_1_failure_mode_alignment, HAV_hazard_avoidance, HISTORICAL_STRUCTURAL_MATCHING_II, HLL2_language_likeness, HOT_ordinal_hierarchy, HTCS_coordinate_semantics, HTC_ht_closure_tests, HTO_human_track_ordering, IMD_micro_differentiation, JAR_WORKING_SET_INTERFACE, LDF_link_distribution_folios, LINE_line_level_analysis, LRM_local_role_motifs, MAT_PHY_1_material_topology, MCS_coordinate_system, NESS_non_executable_systems, OJLM_1_operator_judgment, OLF_olfactory_craft, OPS7_operator_doctrine, OPS_R_abstraction_reconciliation, PAS_program_archetype_synthesis, PCC_product_class_convergence, PCIP_plant_context_intersection, PCI_process_class_isomorphism, PCI_purpose_class_inference, PIAA_plant_illustration, PIA_product_isolation, PPA_physics_plausibility, PPC_program_plant_correlation, PSP_product_space_plausibility, PWRE_1_physical_reverse_engineering, QLA_quire_level_analysis, RI_AZC_LINKING_INVESTIGATION, RRD_regime_role_differentiation, SEL_A_claim_inventory, SRP_speculative_reconstruction, SSD_PHY_1a, SSD_survivor_set_dimensionality, SSI_speculative_semantics, STRUCTURAL_TOPOLOGY_TESTS, SYM_CAP_TOPO_grammar_architecture, TRANS_transition_enrichment, UTC_uncategorized_token_analysis

</details>

---

## Category: MIXED_LEGACY (103)

Phases with scripts, results, and/or documentation mixed directly in the phase directory without `scripts/` and `results/` subdirectories. These predate the modern convention and are complete — just not organized per current standards. Reorganizing them would risk breaking references.

<details>
<summary>Full list (103 phases)</summary>

01-09_early_hypothesis, 10-14_domain_characterization, 15-20_kernel_grammar, 21-23_enumeration, AAZ_a_azc_coordination, AB_integration_mechanics, AC_INTERNAL_CHARACTERIZATION, ANN_annotation_analysis, APF_adversarial_process, ARE_apparatus_engineering, AZC_AXIS_axis_connectivity, AZC_COMPATIBILITY, AZC_INTERFACE_VALIDATION, AZC_POSITION_VOCABULARY, AZC_REACHABILITY_SUPPRESSION, AZC_TRAJECTORY_SHAPE, AZC_ZODIAC_INTERNAL_STRATIFICATION, AZC_constraint_hunting, A_BEHAVIORAL_CLASSIFICATION, A_REGIME_STRATIFICATION, BC_EXPLANATION_ENFORCEMENT, BRUNSCHWIG_BACKPROP_VALIDATION, BRUNSCHWIG_FULL_MAPPING, BRUNSCHWIG_REVERSE_ACTIVATION, BRUNSCHWIG_SEMANTIC_ANCHOR, BRUNSCHWIG_TEMPLATE_FIT, BRU_AUDIT, B_EXCL_ROLE, CAR_currier_a_reexamination, CAS_POST, CAS_currier_a_schema, CAud_currier_a_audit, CCF_circular_folios, COR_correlation_analysis, CUR_currier_analysis, CYCLE_semantics_analysis, EFFICIENCY_REGIME_TEST, ENT_entry_structure, EPM_exploratory_process, EXT8_prefix_taxonomy_compatibility, EXT9_cross_system_mapping, EXT_ECO_01_opportunity_loss_profile, EXT_ECO_02_hazard_class_discrimination, EXT_FILTER_01_alignment_conditioning, EXT_HF_01_attentional_doodling, EXT_HF_02_visual_layout, EXT_HF_03_procedural_fluency, EXT_MAT_01_material_discrimination, EXT_SEQ_01_seasonal_ordering, FSS_family_syntax, HCG_historical_comparison, HFM_human_factors, HTD_human_track_domain, ILL_TOP_1_illustration_topology, ILL_illustration_independence, KERNEL_ordering_constraints, L1L2_forward_inference, L3_material_class, L4_geometry, LATENT_AXES, LINK_temporal_state_space, MIXED_marker_entry_analysis, MULTI_LINE_RECORDS, NAI_naibbe_investigation, OPS1_folio_control_signatures, OPS2_control_strategy_clustering, OPS3_risk_time_stability_tradeoffs, OPS4_operator_decision_model, OPS5_control_engagement_intensity, OPS6A_human_navigation, OPS6_codex_organization, PCS_coordinate_system, PHARMA_LABEL_DECODING, PHYS_physics_stress_test, PMS_prefix_material, POST_CLOSURE_CHARACTERIZATION, PROCESS_ISOMORPHISM, PUFF_COMPLEXITY_CORRELATION, PUFF_STRUCTURAL_TESTS, ROBUST_grammar_robustness, SEL_F_contradiction_resolution, SEMANTIC_CEILING_BREACH, SEMANTIC_CEILING_EXTENSION, SENSORY_LOAD_ENCODING, SENSORY_MAPPING, SID01_global_residue_convergence, SID03_micro_cipher_stress_test, SID04_human_state_compatibility, SID05_attentional_discrimination, SISTER_sister_pair_analysis, SITD_shot_in_the_dark, SPEC_A_semantic_mapping, SP_structural_primitives, TIER4_EXTENDED, TRAJECTORY_SEMANTICS, TTDT_terminal_differentiation, VIS_visual_analysis, X_adversarial_audit, YALE_ALIGNMENT, ZOD_zodiac_analysis, ZONE_MATERIAL_COHERENCE, ZONE_MODALITY_VALIDATION, exploration

</details>

---

## Legacy `results/` Directory

**315 files** remain in the top-level `results/` directory. These are preserved as-is because:
1. Constraints and scripts reference `results/` paths
2. Many cannot be cleanly mapped to single phases (multi-phase analysis outputs)
3. Moving them risks breaking traceability

The `results/` directory is documented as LEGACY ONLY in CLAUDE.md. All new phase results go in `phases/PHASE_NAME/results/`.
