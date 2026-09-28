# Claim to Phase Mapping

**Purpose:** Find which phase produced a specific constraint

---

## How to Use

Look up constraint number to find source phase.

> **Status note (v7.25):** this map records **provenance only** (which phase produced a number); it does not give a constraint's current status. Look status up in the generated `context/CONSTRAINT_TABLE.txt` (a number missing from it is dead; Tier 3 means demoted or speculative) and the reason in `context/CLAIMS/INDEX.md`. Ranges here include numbers that were never registered. Rows containing demoted or dead constraints are annotated below; what is withdrawn as structure is listed in SYSTEM/STATUS_BRIEF.md §3. The map stops at C1035; later numbers are in CLAIMS/INDEX.md.

---

## Early core block (C074-C132) — formerly headed "Tier 0 Core"; after the 2026-09-28 restatement only C121 and C124 of this block are Tier 0 (others Tier 1/2/3 or superseded)

| Constraint | Phase |
|------------|-------|
| C074 | Phase 13-14, SEL-F (now Tier 2, occupancy measurement only) |
| C079 | Phase 13-14 (demoted to Tier 3) |
| C084 | Phase 13-14, SEL-F (demoted to Tier 3) |
| C085-C108 | Phase 15, 17 (C085, C103–C105 demoted to Tier 3; C089 superseded by C2082) |
| C109-C114 | Phase 18 (C109 scoped: class level demoted C783, taxonomy imposed C2060, zeros reduce C2081) |
| C115 | Phase 19 (demoted to Tier 3) |
| C119-C124 | Phase 19, 20 (C120 demoted to Tier 3; C119 Tier 2; C121, C124 Tier 0) |
| C130-C132 | Phase X.5 (C130's 0.19% figure is tainted, not relied on — see STATUS_BRIEF §4) |

---

## Family/Illustration (C126-C144)

| Constraint | Phase |
|------------|-------|
| C126, C129 | Phase FSS |
| C137-C140 | Phase ILL |
| C141, C144 | Phase FSS |

---

## Organizational (C153-C177; some demoted or dead — see rows)

| Constraint | Phase |
|------------|-------|
| C153-C156 | Phase 20, QLA |
| C157-C159 | Phase 16 (C157 demoted to Tier 3) |
| C160-C165 | OPS, PIAA, PPC |
| C166-C170 | UTC, MCS, NESS |
| C171-C177 | PCI, various (C171 demoted to Tier 3; C172 superseded, dead) |

---

## OPS/EXT (C178-C223; some demoted — see rows)

| Constraint | Phase |
|------------|-------|
| C178-C198 | OPS-1 to OPS-7 [v7.26 status: C181, C182, C183, C184, C185, C186, C189, C198 demoted to Tier 3 (OPS model built on withdrawn hazard/recovery composites); C196, C197 demoted to Tier 3 (invented archetype)] |
| C199-C223 | EXT-1 to EXT-9, SID, EXT-MAT, EXT-ECO, EXT-HF (C199, C215, C216 demoted to Tier 3) |

---

## Currier A (C224-C299)

| Constraint | Phase |
|------------|-------|
| C224-C232 | CAud |
| C233-C240 | CAS |
| C241-C249 | SP |
| C250-C266 | CAS-MULT, CAS-DEEP |
| C267-C272 | CAS-MORPH, CAS-PHYS |
| C273-C282 | EXT-8 |
| C283-C290 | EXT-9, EXT-9B |
| C291-C299 | CAS-POST, B-MORPH, CAS-XREF |

---

## AZC (C300-C322) [v7.26 status: C309, C311, C320 demoted to Tier 3 (transcription-order statistic, like retracted C433-C435)]

| Constraint | Phase |
|------------|-------|
| C300-C305 | AZC, AZC-PROBE |
| C306-C312 | AZC-PLACEMENT, AZC-AXIS [v7.26 status: C309, C311 demoted to Tier 3 (transcription-order statistic, like retracted C433-C435)] |
| C313-C322 | AZC-AXIS-A, AZC-AXIS-B, AZC-AXIS-CD [v7.26 status: C320 demoted to Tier 3 (transcription-order statistic, like retracted C433-C435)] |

---

## SEL-F and Integration (C323-C346) [v7.26 status: C325 demoted to Tier 3 (section confound (C1401))]

| Constraint | Phase |
|------------|-------|
| C323-C327 | SEL-F [v7.26 status: C325 demoted to Tier 3 (section confound (C1401))] |
| C328-C331 | ROBUST |
| C332-C334 | KERNEL, LINK |
| C335-C340 | AB_INTEGRATION, MIXED, PHYS |
| C341-C344 | HTD, AAZ |
| C345-C346 | CAS-FOLIO |

---

## Morphology (C347-C382; C365 dead — see rows)

| Constraint | Phase |
|------------|-------|
| C347-C348 | HT-MORPH, HT-STATE |
| C349-C356 | MORPH-CLOSE, FG |
| C357-C370 | LINE, BVP, QLA (C365 refuted by C805, dead; C366 revised by C804) |
| C371-C382 | BPF, BSF, MSTAB [v7.26 status: C382 demoted to Tier 3 (kernel contact is a spelling identity; monitoring reading withdrawn)] |

---

## Architecture (C383-C411) [v7.26 status: C383 demoted to Tier 3 (kernel contact is a spelling identity; monitoring reading withdrawn)]

| Constraint | Phase |
|------------|-------|
| C383-C385 | A-ARCH [v7.26 status: C383 demoted to Tier 3 (kernel contact is a spelling identity; monitoring reading withdrawn)] |
| C386-C393 | TRANS, SYM, CAP, TOPO |
| C394-C402 | RRD, HAV, BSA, LRM |
| C403 | PAS |
| C404-C406 | HTC |
| C407-C411 | SISTER, SITD |

---

## AZC Deep + Pipeline (C430-C473; some retracted or demoted — see rows)

| Constraint | Phase |
|------------|-------|
| C430-C444 | AZC-DEEP (C433–C435 retracted PHASE_742, dead: serialization/transcription artifacts) |
| C450-C462 | INTRA-ROLE, HT-AZC (C458, C461, C462 demoted to Tier 3) |
| C466-C467 | PREFIX-ROLE |
| C468-C470 | PIPELINE-RESOLUTION (C470 demoted to Tier 3: frequency confound) |
| C471-C473 | INTEGRATION-PROBE (Morphological Binding) |
| C637-C639 | SISTER_PAIR_CHOICE_DYNAMICS |
| C640-C642 | A_TO_B_ROLE_PROJECTION |
| C643-C647 | LANE_CHANGE_HOLD_ANALYSIS |
| C648-C651 | LANE_FUNCTIONAL_PROFILING |
| C652-C655 | PP_LANE_PIPELINE |
| C656-C659 | PP_POOL_CLASSIFICATION |
| C660-C663 | PREFIX_MIDDLE_SELECTIVITY |
| C664-C669 | B_FOLIO_TEMPORAL_PROFILE |
| C670-C681 | B_LINE_SEQUENTIAL_STRUCTURE |
| C682-C693 | A_RECORD_B_FILTERING |
| C694-C703 | CONSTRAINT_BUNDLE_SEGMENTATION |
| C704-C709 | FOLIO_LEVEL_FILTERING |
| C710-C718 | RI_FUNCTIONAL_IDENTITY |
| C719-C721 | RI_BINDING_ANALYSIS |
| C722-C727 | B_LEGALITY_GRADIENT |
| C728-C733 | PP_LINE_LEVEL_STRUCTURE |
| C734-C739, C751-C752 | A_B_FOLIO_SPECIFICITY |
| C740-C746 | HT_RECONCILIATION |
| C747-C750, C794-C795 | B_LINE_POSITION_HT |
| C751-C752, C792-C793 | A_B_FOLIO_SPECIFICITY |
| C753-C756 | AZC_REASSESSMENT (C755, C756 demoted to Tier 3) |
| C757-C763 | AZC_FOLIO_DIFFERENTIATION |
| C764 | F57V_COORDINATE_RING |
| C765 | AZC_B_CONSTRAINT_MECHANISM |
| C766-C769 | COMPOUND_MIDDLE_ARCHITECTURE |
| C770-C781 | FL_PRIMITIVE_ARCHITECTURE |
| C782-C787 | CONTROL_TOPOLOGY_ANALYSIS (C783 demoted to Tier 3: class-level forbidden transitions) |
| C788-C791 | CC_MECHANICS_DEEP_DIVE |
| C792-C793 | A_B_FOLIO_SPECIFICITY |
| C794-C795 | B_LINE_POSITION_HT |
| C796-C803 | PP_HT_AZC_INTERACTION |
| C804-C809 | LINK_OPERATOR_ARCHITECTURE |
| C810-C815 | CONTROL_LOOP_SYNTHESIS |
| C816-C820 | CC_CONTROL_LOOP_INTEGRATION (C816, C817, C819 demoted to Tier 3) |
| C821-C823 | REGIME_LINE_SYNTAX_INTERACTION |
| C824-C839 | A_RECORD_B_ROUTING_TOPOLOGY (C836, C837 at Tier 2/3 in INDEX — shown as Tier 3, demoted, in the generated table) |
| C840-C845 | B_PARAGRAPH_STRUCTURE |
| C846 | A_B_PARAGRAPH_CORRESPONDENCE |
| C847-C854 | PARAGRAPH_INTERNAL_PROFILING |
| C855-C862 | FOLIO_PARAGRAPH_ARCHITECTURE |
| C863-C869 | FOLIO_PARAGRAPH_ARCHITECTURE (C863, C869 demoted to Tier 3) |
| C870-C872 | HT_TOKEN_INVESTIGATION (C872 demoted to Tier 3) |
| C900-C904 | AZC_PLACEMENT_REASSESSMENT, A_MORPHOLOGY_DEEP_DIVE |
| C905-C955 | Various (FL, MIDDLE, section, vocabulary phases) (C907 Tier 4, C936 Tier 3 — demoted/speculative) |
| C956-C964 | B_TOKEN_LEVEL_SYNTAX (C957 superseded by C2081, dead) |
| C965 | PARAGRAPH_STATE_COLLAPSE [v7.26 status: C965 demoted to Tier 3 (not replicated (C1259))] |
| C966-C970 | LANE_OSCILLATION_CONTROL_LAW |
| C971-C975 | FINGERPRINT_UNIQUENESS (C973 demoted to Tier 3: broken baseline + sparsity) |
| C976-C980 | MINIMAL_STATE_AUTOMATON |
| C995-C997 | AFFORDANCE_STRESS_TEST, BIN_HAZARD_NECESSITY |
| C998 | THERMAL_PLANT_SIMULATION |
| C999 | CATEGORICAL_DISCRETIZATION_TEST |
| C1000 | HUB_ROLE_DECOMPOSITION |
| C1001 | PP_INFORMATION_DECOMPOSITION |
| C1002 | SUFFIX_POSITIONAL_STATE_MAPPING |
| C1003 | PREFIX_MIDDLE_SUFFIX_SYNERGY |
| C1004 | FULL_TOKEN_TRANSITION_DEPTH |
| C1005 | BUBBLE_POINT_OSCILLATION_TEST (Tier 4 in the generated table — speculative, not demoted structure) |
| C1006 | REGIME_DWELL_ARCHITECTURE |
| C1007 | REGIME_DWELL_ARCHITECTURE |
| C1008 | AXM_GATEKEEPER_INVESTIGATION |
| C1009 | AXM_GATEKEEPER_INVESTIGATION |
| C1010 | MACRO_AUTOMATON_NECESSITY |
| C1011 | GEOMETRIC_MACRO_STATE_FOOTPRINT |
| C1012 | PREFIX_MACRO_STATE_ENFORCEMENT |
| C1013 | BRIDGE_MIDDLE_SELECTION_MECHANISM |
| C1014 | SURVIVOR_SET_GEOMETRY_ALIGNMENT (demoted to Tier 3: construction tautology) |
| C1015 | PREFIX_COMPOSITION_STATE_ROUTING |
| C1016 | FOLIO_MACRO_AUTOMATON_DECOMPOSITION |
| C1017 | MACRO_DYNAMICS_VARIANCE_DECOMPOSITION |
| C1018 | ARCHETYPE_GEOMETRIC_ANATOMY |
| C1019 | MORPHOLOGICAL_TENSOR_DECOMPOSITION |
| C1020 | TENSOR_ARCHETYPE_GEOMETRY |
| C1021 | CP_FACTOR_CHARACTERIZATION |
| C1022 | PARAGRAPH_MACRO_DYNAMICS |
| C1023 | STRUCTURAL_NECESSITY_ABLATION |
| C1024 | STRUCTURAL_DIRECTIONALITY |
| C1025 | GENERATIVE_SUFFICIENCY [v7.26 status: C1025 demoted to Tier 3 (reduced by C2063)] |
| C1026 | GRAMMAR_COMPONENT_NECESSITY |
| C1027 | HAZARD_VIOLATION_ARCHAEOLOGY |
| C1028 | VOCABULARY_CURATION_RULE |
| C1029 | SECTION_GRAMMAR_VARIATION |
| C1030 | SECTION_GRAMMAR_VARIATION |
| C1031 | FL_CROSS_LINE_CONTINUITY |
| C1032 | PREFIX_ASYMMETRY_CORRECTION |
| C1033 | C2_CC_SUFFIX_FREE |
| C1034 | PREFIX_FACTORED_DESIGN |
| C1035 | AXM_RESIDUAL_DECOMPOSITION |

---

## Navigation

← [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md) | [phase_to_claim.md](phase_to_claim.md) →
