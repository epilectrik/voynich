# Constraint Index

**Total:** 1089 validated constraints | **Version:** 4.46 | **Date:** 2026-02-23

> **Architectural Context:** [../MODEL_CONTEXT.md](../MODEL_CONTEXT.md) - Read this FIRST to understand how constraints work

**How to find constraints:**
1. **By topic** - Browse category sections below, follow links to registry files for details
2. **By number** - Ctrl+F for "C###" in this file or the relevant registry
3. **Programmatic** - Use [../CONSTRAINT_TABLE.txt](../CONSTRAINT_TABLE.txt) for scripts/validation (TSV format, do NOT read in full)

---

## How to Use

1. **Find by number:** Ctrl+F for "C###"
2. **Find by topic:** Browse category sections below
3. **Full details:** Follow link to individual file or grouped registry

### Legend

- `→` = Individual file exists
- `⊂` = In grouped registry
- **Bold** = Tier 0 (frozen fact)

### System Scope Tags

| Tag | Meaning |
|-----|---------|
| **B** | Applies to Currier B execution grammar only |
| **A** | Applies to Currier A registry only |
| **AZC** | Applies to AZC diagram annotations only |
| **HT** | Applies to Human Track layer only |
| **A→B** | Discovered in A, instantiated in B |
| **GLOBAL** | Spans A/B/AZC systems |
| **A↔B** | Cross-system relationship |

### Adding New Constraints

Every new constraint MUST specify system scope:

**Validation checklist:**
- [ ] Scope tag assigned
- [ ] Evidence source matches scope (e.g., B requires B corpus evidence)
- [ ] If GLOBAL, evidence from multiple systems required
- [ ] If A→B, explicit note about where instantiated

---

## Executability (C072-C125)

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| **074** | Dominant convergence to stable states (57.8% STATE-C terminal) | 0 | B | → [C074_dominant_convergence.md](C074_dominant_convergence.md) |
| **079** | Only STATE-C essential | 0 | B | ⊂ tier0_core |
| **084** | System targets MONOSTATE (42.2% end in transitional) | 0 | B | ⊂ tier0_core |
| **115** | 0 non-executable tokens | 0 | B | ⊂ tier0_core |
| **119** | 0 translation-eligible zones | 0 | B | ⊂ tier0_core |
| **120** | PURE_OPERATIONAL verdict | 0 | B | ⊂ tier0_core |
| **121** | 49 instruction equivalence classes (9.8x compression) | 0 | B | → [C121_49_instruction_classes.md](C121_49_instruction_classes.md) |
| **124** | 100% grammar coverage | 0 | B | → [C124_grammar_coverage.md](C124_grammar_coverage.md) |

---

## Kernel Structure (C085-C108)

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| **085** | 10 single-character primitives (s,e,t,d,l,o,h,c,k,r) | 0 | B | ⊂ tier0_core |
| **089** | Core within core: k, h, e | 0 | B | ⊂ tier0_core |
| 090 | 500+ 4-cycles, 56 3-cycles (topological) | 2 | B | ⊂ grammar_system |
| 103 | k = ENERGY_MODULATOR | 2 | B | ⊂ grammar_system |
| 104 | h = PHASE_MANAGER | 2 | B | ⊂ grammar_system |
| 105 | e = STABILITY_ANCHOR (54.7% recovery paths) | 2 | B | ⊂ grammar_system |
| 107 | All kernel nodes BOUNDARY_ADJACENT to forbidden | 2 | B | ⊂ grammar_system |
| **521** | **Kernel Primitive Directional Asymmetry** (one-way valve: e→h=0.00, h→k=0.22, e→k=0.27 suppressed; h→e=7.00x, k→e=4.32x elevated; stabilization is absorbing) | 2 | B | ⊂ grammar_system |
| **522** | **Construction-Execution Layer Independence** (r=-0.21, p=0.07; character and class constraints are independent regimes sharing symbol substrate) | 2 | B | ⊂ grammar_system |

---

## Hazard Topology (C109-C114)

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| 109 | 5 failure classes (PHASE_ORDERING dominant 41%) | 2 | B | → [C109_hazard_classes.md](C109_hazard_classes.md) |
| 110 | PHASE_ORDERING 7/17 = 41% | 2 | B | ⊂ grammar_system |
| 111 | 65% asymmetric | 2 | B | ⊂ grammar_system |
| 112 | 59% distant from kernel | 2 | B | ⊂ grammar_system |

---

## Language Rejection (C130-C132)

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| 130 | DSL hypothesis rejected (0.19% reference rate) | 1 | B | → [CORE/falsifications](../CORE/falsifications.md) |
| 131 | Role consistency LOW (23.8%) | 2 | B | ⊂ grammar_system |
| 132 | Language encoding CLOSED | 1 | B | → [CORE/falsifications](../CORE/falsifications.md) |

---

## Illustration Independence (C137-C140)

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| 137 | Swap invariance confirmed (p=1.0) | 1 | B | → [CORE/falsifications](../CORE/falsifications.md) |
| 138 | Illustrations do not constrain execution | 1 | B | → [CORE/falsifications](../CORE/falsifications.md) |
| 139 | Grammar recovered from text-only | 2 | B | ⊂ grammar_system |
| 140 | Illustrations are epiphenomenal | 1 | B | → [CORE/falsifications](../CORE/falsifications.md) |

---

## Family Structure (C126-C144)

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| 126 | 0 contradictions across 8 families | 2 | B | ⊂ grammar_system |
| 129 | Family differences = coverage artifacts | 2 | B | ⊂ grammar_system |
| 141 | Cross-family transplant = ZERO degradation | 2 | B | ⊂ grammar_system |
| 144 | Families are emergent regularities | 2 | B | ⊂ grammar_system |

---

## Organizational Structure (C153-C177)

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| 153 | Prefix/suffix axes partially independent (MI=0.075) | 2 | B | ⊂ organization |
| 154 | Extreme local continuity (d=17.5) | 2 | B | ⊂ organization |
| 155 | Piecewise-sequential geometry (PC1 rho=-0.624) | 2 | B | ⊂ organization |
| 156 | Detected sections match codicology (4.3x quire alignment) | 2 | B | ⊂ organization |
| 157 | Circulatory reflux uniquely compatible (100%) | 3 | B | → [SPECULATIVE/](../SPECULATIVE/INTERPRETATION_SUMMARY.md) |
| 166 | Uncategorized: zero forbidden seam presence (0/35) | 2 | HT | ⊂ human_track |
| 167 | Uncategorized: 80.7% section-exclusive | 2 | HT | ⊂ human_track |
| 168 | Uncategorized: single unified layer | 2 | HT | ⊂ human_track |
| 169 | Uncategorized: hazard avoidance 4.84 vs 2.5 | 2 | HT | ⊂ human_track |
| 170 | Uncategorized: morphologically distinct (p<0.001) | 2 | HT | ⊂ human_track |
| 171 | Only continuous closed-loop process control survives | 2 | B | → [C171_closed_loop_only.md](C171_closed_loop_only.md) |

---

## OPS Findings (C178-C198)

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| 178 | 83 folios yield 33 operational metrics | 2 | B | ⊂ operations |
| 179 | 4 stable regimes (K-Means k=4, Silhouette=0.23) | 2 | B | ⊂ operations |
| 180 | All 6 aggressive folios in REGIME_3 | 2 | B | ⊂ operations |
| 181 | 3/4 regimes Pareto-efficient; REGIME_3 dominated | 2 | B | ⊂ operations |
| 182 | Restart-capable = higher stability | 2 | B | ⊂ operations |
| 187 | CEI manifold formalized | 2 | B | ⊂ operations |
| 188 | CEI bands: R2 < R1 < R4 < R3 | 2 | B | ⊂ operations |
| 190 | LINK-CEI r=-0.7057 | 2 | B | ⊂ operations |
| 196 | 100% match EXPERT_REFERENCE archetype | 2 | B | ⊂ operations |
| 197 | Designed for experts, not novices | 2 | B | ⊂ operations |

---

## External Findings (C199-C223)

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| 199 | Both mineral AND botanical survive | 3 | B | ⊂ operations |
| 209 | Attentional pacing wins (6/8) | 2 | HT | ⊂ human_track |
| 215 | BOTANICAL_FAVORED (8/8 tests, ratio 2.37) | 3 | B | ⊂ operations |
| 216 | Hybrid hazard model (71% batch, 29% apparatus) | 2 | B | ⊂ operations |
| 217 | 0 true HT near hazards | 2 | HT | ⊂ human_track |
| 221 | Deliberate skill practice (4/5) - NOT random mark-making | 2 | HT | ⊂ operations |

---

## Currier A Disjunction (C224-C240)

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| 224 | A coverage = 13.6% (threshold 70%) | 2 | A | ⊂ currier_a |
| 229 | A = DISJOINT | 2 | A | → [C229_currier_a_disjoint.md](C229_currier_a_disjoint.md) |
| 233 | A = LINE_ATOMIC | 2 | A | ⊂ currier_a |
| 234 | A = POSITION_FREE | 2 | A | ⊂ currier_a |
| 235 | 8+ mutually exclusive markers | 2 | A | ⊂ currier_a |
| 239 | A/B separation = DESIGNED (0.0% cross) | 2 | A↔B | ⊂ currier_a |
| 240 | A = NON_SEQUENTIAL_CATEGORICAL_REGISTRY | 2 | A | → [C240_currier_a_registry.md](C240_currier_a_registry.md) |

---

## Multiplicity Encoding (C250-C266) - INVALIDATED

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| 250 | ~~64.1% show repeating blocks~~ | 1 | A | **INVALIDATED** - transcriber artifact |
| 251-262 | Block-dependent constraints | 1 | A | **INVALIDATED** - depend on C250 |
| 266 | ~~Block vs non-block entry types~~ | 1 | A | **INVALIDATED** - depend on C250 |

**Note (2026-01-15):** All block repetition findings were artifacts of loading all transcribers instead of H (primary) only. With H-only data: 0% block repetition.

---

## Compositional Morphology (C267-C298)

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| 267 | Tokens are COMPOSITIONAL (PREFIX+MIDDLE+SUFFIX) | 2 | A→B | → [C267_compositional_morphology.md](C267_compositional_morphology.md) |
| **267.a** | **MIDDLE Sub-Component Structure** (218 sub-components reconstruct 97.8% of MIDDLEs; morphology extends to sub-MIDDLE level) | 2 | GLOBAL | ⊂ currier_a |
| 268 | 897 observed combinations | 2 | A→B | ⊂ morphology |
| 272 | A and B on COMPLETELY DIFFERENT folios | 2 | A↔B | ⊂ morphology |
| 278 | Three-axis HIERARCHY (PREFIX→MIDDLE→SUFFIX) | 2 | A→B | ⊂ morphology |
| 281 | Components SHARED across A and B | 2 | A↔B | ⊂ morphology |
| 291 | ~20% have optional ARTICULATOR forms | 2 | A | ⊂ morphology |
| 292 | Articulators = ZERO unique identity distinctions | 2 | A | ⊂ morphology |

---

## AZC System (C300-C327, C430-C436, C904)

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| 300 | 3,299 tokens (8.7%) unclassified by Currier | 2 | AZC | ⊂ azc_system |
| 301 | AZC is HYBRID (B=69.7%, A=65.4%) | 2 | AZC | → [C301_azc_hybrid.md](C301_azc_hybrid.md) |
| 306 | Placement-coding axis established | 2 | AZC | ⊂ azc_system |
| 313 | Position constrains LEGALITY not PREDICTION | 2 | AZC | ⊂ azc_system |
| 317 | Hybrid architecture (topological + positional) | 2 | AZC | ⊂ azc_system |
| 322 | SEASON-GATED WORKFLOW interpretation | 2 | AZC | ⊂ azc_system |
| 323 | 57.8% STATE-C terminal | 2 | B | ⊂ grammar_system |
| **430** | **AZC Bifurcation: two folio families** | 2 | AZC | ⊂ azc_system |
| **431** | **Zodiac Family Coherence (refines C319)** | 2 | AZC | ⊂ azc_system |
| **432** | **Ordered Subscript Exclusivity** | 2 | AZC | ⊂ azc_system |
| **433** | **Zodiac Block Grammar (98%+ self-transition)** | 2 | AZC | ⊂ azc_system |
| **434** | **R-Series Strict Forward Ordering** | 2 | AZC | ⊂ azc_system |
| **435** | **S/R Positional Division (boundary/interior)** | 2 | AZC | ⊂ azc_system |
| **436** | **Dual Rigidity: uniform vs varied scaffolds** | 2 | AZC | ⊂ azc_system |
| **496** | **Nymph-Adjacent S-Position Prefix Bias (o-prefix 75%)** | 2 | AZC | ⊂ azc_system |
| **904** | **-ry Suffix S-Zone Enrichment (3.18x; cross-validates C839 OUTPUT marker)** | 2 | AZC | → [C904_ry_szone_enrichment.md](C904_ry_szone_enrichment.md) |

---

## AZC-B Coupling Falsifications (C454-C456)

> **Summary:** C454-C456 establish that AZC does NOT modulate B execution and is NOT a simple circulatory cycle. AZC is a cognitive orientation scaffold with interleaved spiral topology.

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| **454** | **AZC-B Adjacency Coupling FALSIFIED** (no p<0.01 at any window) | 1 | AZC/B | -> [C454_azc_b_adjacency_falsified.md](C454_azc_b_adjacency_falsified.md) |
| **455** | **AZC Simple Cycle Topology FALSIFIED** (cycle_rank=5, CV=0.817) | 1 | AZC | -> [C455_azc_simple_cycle_falsified.md](C455_azc_simple_cycle_falsified.md) |
| **456** | **AZC Interleaved Spiral Topology** (R-S-R-S alternation) | 2 | AZC | -> [C456_azc_interleaved_spiral.md](C456_azc_interleaved_spiral.md) |

---

## Grammar Robustness (C328-C331)

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| 328 | 10% corruption = 3.3% entropy increase | 2 | B | ⊂ grammar_system |
| 329 | Top 10 token removal = 0.8% entropy change | 2 | B | ⊂ grammar_system |
| 330 | Leave-one-folio-out = max 0.25% change | 2 | B | ⊂ grammar_system |
| 331 | 49-class minimality WEAKENED but confirmed | 2 | B | ⊂ grammar_system |

---

## Line/Folio Structure (C345-C370)

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| 345 | A folios lack thematic coherence | 2 | A | ⊂ currier_a |
| 346 | A exhibits SEQUENTIAL COHERENCE | 2 | A | ⊂ currier_a |
| 421 | Section-boundary adjacency suppression (2.42x) | 2 | A | ⊂ currier_a |
| 422 | DA as internal articulation punctuation (75% separation) | 2 | A | ⊂ currier_a |
| 423 | PREFIX-BOUND VOCABULARY DOMAINS (80% exclusive MIDDLEs) | 2 | A | ⊂ currier_a |
| 357 | Lines 3.3x more regular than random | 2 | B | → [C357_lines_chunked.md](C357_lines_chunked.md) |
| 358 | Specific boundary tokens identified | 2 | B | ⊂ organization |
| 360 | Grammar is LINE-INVARIANT | 2 | B | ⊂ grammar_system |
| 361 | Adjacent B folios share 1.30x more vocabulary | 2 | B | ⊂ organization |
| 367 | Sections are QUIRE-ALIGNED (4.3x) | 2 | B | ⊂ organization |

---

## Paragraph Architecture (C840-C869)

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| 840 | B paragraph = mini-program (gallows-initial 89%, HT line-1 enriched) | 2 | B | → [C840_b_paragraph_mini_program_structure.md](C840_b_paragraph_mini_program_structure.md) |
| 841 | B paragraph gallows-initial pattern | 2 | B | → [C841_b_paragraph_gallows_initial.md](C841_b_paragraph_gallows_initial.md) |
| 842 | B paragraph step-function pattern | 2 | B | → [C842_b_paragraph_step_function.md](C842_b_paragraph_step_function.md) |
| 843 | B paragraph prefix markers | 2 | B | → [C843_b_paragraph_prefix_markers.md](C843_b_paragraph_prefix_markers.md) |
| 844 | Folio line-1 double header | 2 | B | → [C844_folio_line1_double_header.md](C844_folio_line1_double_header.md) |
| 845 | B paragraph self-containment | 2 | B | → [C845_b_paragraph_self_containment.md](C845_b_paragraph_self_containment.md) |
| 846 | A-B paragraph pool relationship | 2 | A↔B | → [C846_ab_paragraph_pool_relationship.md](C846_ab_paragraph_pool_relationship.md) |
| 847 | A paragraph size distribution | 2 | A | → [C847_a_paragraph_size_distribution.md](C847_a_paragraph_size_distribution.md) |
| 848 | A paragraph RI position variance | 2 | A | → [C848_a_paragraph_ri_position_variance.md](C848_a_paragraph_ri_position_variance.md) |
| 849 | A paragraph section profile | 2 | A | → [C849_a_paragraph_section_profile.md](C849_a_paragraph_section_profile.md) |
| 850 | A paragraph cluster taxonomy (5 clusters) | 2 | A | → [C850_a_paragraph_cluster_taxonomy.md](C850_a_paragraph_cluster_taxonomy.md) |
| 851 | B paragraph HT variance validation | 2 | B | → [C851_b_paragraph_ht_variance_validation.md](C851_b_paragraph_ht_variance_validation.md) |
| 852 | B paragraph section-role interaction | 2 | B | → [C852_b_paragraph_section_role_interaction.md](C852_b_paragraph_section_role_interaction.md) |
| 853 | B paragraph cluster taxonomy (5 clusters) | 2 | B | → [C853_b_paragraph_cluster_taxonomy.md](C853_b_paragraph_cluster_taxonomy.md) |
| 854 | A-B paragraph structural parallel | 2 | A↔B | → [C854_ab_paragraph_structural_parallel.md](C854_ab_paragraph_structural_parallel.md) |
| 855 | Folio role template (role cohesion 0.831) | 2 | B | → [C855_folio_role_template.md](C855_folio_role_template.md) |
| 856 | Vocabulary distribution (Gini 0.279, distributed) | 2 | B | → [C856_vocabulary_distribution.md](C856_vocabulary_distribution.md) |
| 857 | First paragraph ordinariness (predicts 11.8%) | 2 | B | → [C857_first_paragraph_ordinariness.md](C857_first_paragraph_ordinariness.md) |
| 858 | Paragraph count reflects complexity (rho 0.836) | 2 | B | → [C858_paragraph_count_complexity.md](C858_paragraph_count_complexity.md) |
| 859 | Vocabulary convergence (14%→39% overlap) | 2 | B | → [C859_vocabulary_convergence.md](C859_vocabulary_convergence.md) |
| 860 | Section paragraph organization (HERBAL 2.2 vs RECIPE 10.2) | 2 | B | → [C860_section_paragraph_organization.md](C860_section_paragraph_organization.md) |
| 861 | LINK/hazard paragraph neutrality (CV < 0.21) | 2 | B | → [C861_link_hazard_paragraph_neutrality.md](C861_link_hazard_paragraph_neutrality.md) |
| 862 | Role template verdict: hybrid model | 2 | B | → [C862_role_template_verdict.md](C862_role_template_verdict.md) |
| 863 | Paragraph-ordinal EN subfamily gradient (qo-early, ch-late) | 3 | B | → [C863_paragraph_ordinal_en_gradient.md](C863_paragraph_ordinal_en_gradient.md) |
| 864 | Gallows paragraph marker (81.5% gallows-initial) | 2 | B | → [C864_gallows_paragraph_marker.md](C864_gallows_paragraph_marker.md) |
| 865 | Gallows folio position (k/f front-biased, p/t distributed) | 2 | B | → [C865_gallows_folio_position.md](C865_gallows_folio_position.md) |
| 866 | Gallows morphological patterns (k uses e, f often bare) | 2 | B | → [C866_gallows_morphological_patterns.md](C866_gallows_morphological_patterns.md) |
| 867 | P-T transition dynamics (p stable 54%, t returns to p 50%) | 2 | B | → [C867_p_t_transition_dynamics.md](C867_p_t_transition_dynamics.md) |
| 868 | Gallows-QO/CHSH independence (0.3% variance explained) | 2 | B | → [C868_gallows_qochsh_independence.md](C868_gallows_qochsh_independence.md) |
| 869 | Gallows functional model (f/k openers, p/t modes) | 3 | B | → [C869_gallows_functional_model.md](C869_gallows_functional_model.md) |

---

## HT Token Identity (C870-C872)

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| 870 | Line-1 HT folio specificity (86% singletons, 1229 Line-1-only) | 2 | HT | → [C870_line1_ht_folio_specificity.md](C870_line1_ht_folio_specificity.md) |
| 871 | HT role cooccurrence pattern (enriched FL, depleted CC/FQ) | 2 | HT | → [C871_ht_role_cooccurrence_pattern.md](C871_ht_role_cooccurrence_pattern.md) |
| 872 | HT discrimination vocabulary interpretation | 3 | HT | -> [C872_ht_discrimination_vocabulary.md](C872_ht_discrimination_vocabulary.md) |

---

## B Control Flow Semantics (C873-C880)

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| 873 | Kernel positional ordering: e (0.404) < h (0.410) < k (0.443) | 3 | B | -> [C873_kernel_positional_ordering.md](C873_kernel_positional_ordering.md) |
| 874 | CC token functions: daiin=init (0.370), ol=continue (0.461) | 3 | B | -> [C874_cc_token_functions.md](C874_cc_token_functions.md) |
| 875 | Escape trigger grammar: 80.4% from hazard FL stages | 3 | B | -> [C875_escape_trigger_grammar.md](C875_escape_trigger_grammar.md) |
| 876 | LINK checkpoint function (position 0.405, routes to EN) | 3 | B | -> [C876_link_checkpoint_function.md](C876_link_checkpoint_function.md) |
| 877 | Role transition grammar: EN->EN 38.5%, CC->EN 37.7%, FQ->EN 29.5% | 2 | B | -> [C877_role_transition_grammar.md](C877_role_transition_grammar.md) |
| 878 | Section program variation: BIO high EN, HERBAL_B high FL/FQ | 2 | B | -> [C878_section_program_variation.md](C878_section_program_variation.md) |
| 879 | Process domain: batch processing, 59.2% forward bias | 3 | B | -> [C879_process_domain_verdict.md](C879_process_domain_verdict.md) |
| 880 | Integrated control model: batch processing with escape handling | 3 | B | -> [C880_integrated_control_model.md](C880_integrated_control_model.md) |

---

## Material Mapping V2 (C881-C884)

> **Summary:** Corrected methodology for A-record analysis at paragraph level. A records are paragraphs (not lines). Initial RI tokens in first line function as material identifiers. Distribution of handling types (66% CAREFUL, 11% STANDARD, 6% PRECISION) aligns with Brunschwig fire-degree distribution (60% degree-2, ~5% precision). PRECISION handling (ESCAPE+AUX) shows 3x elevated k+e kernel signature, validating animal material correspondence.

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| 881 | A Record Paragraph Structure (paragraphs not lines; RI in first line 3.84x baseline) | 2 | A | -> [C881_a_record_paragraph_structure.md](C881_a_record_paragraph_structure.md) |
| 882 | PRECISION Kernel Signature (ESCAPE+AUX shows k+e 3x baseline, suppressed h) | 2 | A | -> [C882_precision_kernel_signature.md](C882_precision_kernel_signature.md) |
| 883 | Handling-Type Distribution Alignment (66% CAREFUL matches 60% Brunschwig degree-2) | 3 | A | -> [C883_handling_distribution_alignment.md](C883_handling_distribution_alignment.md) |
| 884 | PRECISION-Animal Correspondence (6 paragraphs pass kernel validation as animal candidates) | 3 | A | -> [C884_precision_animal_correspondence.md](C884_precision_animal_correspondence.md) |

---

## A-B Correspondence Systematic (C885-C886)

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| 885 | A-B Vocabulary Correspondence (A folios provide 81% coverage for B paragraphs; single A paragraphs insufficient at 58%) | 2 | A-B | -> [C885_ab_vocabulary_correspondence.md](C885_ab_vocabulary_correspondence.md) |
| 886 | Transition Probability Directionality (P(A→B) uncorrelated with P(B→A), r=-0.055; symmetric constraints but directional execution) | 2 | B | -> [C886_transition_directionality.md](C886_transition_directionality.md) |

---

## Currier A Paragraph Structure (C887-C889) - Phase: CURRIER_A_STRUCTURE_V2

> **Summary:** Comprehensive characterization of Currier A paragraph-level structure. Key findings: (1) Two opening types: WITH-RI (62.9%) vs WITHOUT-RI (37.1%); (2) WITHOUT-RI shows backward reference to preceding paragraphs (1.23x asymmetry); (3) Section-specific functions: H=cross-referencing (ct 3.87x), P=safety protocols (qo/ok/ol enriched); (4) Reserved ct-ho vocabulary at PP level extends C837 linker signature. Builds on C881 (paragraph structure) and extends C832/C837 (RI separation/linker signature).

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| 887 | WITHOUT-RI Backward Reference (1.23x backward/forward asymmetry; highest overlap 0.228 when following WITH-RI) | 2 | A | -> [C887_without_ri_backward_reference.md](C887_without_ri_backward_reference.md) |
| 888 | Section-Specific WITHOUT-RI Function (H: ct 3.87x cross-ref; P: qo/ok/ol safety protocols) | 2 | A | -> [C888_section_specific_without_ri.md](C888_section_specific_without_ri.md) |
| 889 | ct-ho Reserved PP Vocabulary (MIDDLEs h/hy/ho 98-100% ct-prefixed; extends C837 to PP level) | 2 | A | -> [C889_ct_ho_reserved_vocabulary.md](C889_ct_ho_reserved_vocabulary.md) |

---

## Closed-Loop Orthogonality (C890-C896)

> **Summary:** Closed-loop control dimensions vary independently, revealing orthogonal structure that Brunschwig's linear recipe model cannot capture. Recovery RATE vs PATHWAY are independent (C890); ENERGY vs FREQUENT operators are inversely correlated (C891); post-FQ recovery enters via h (phase-check) not e (equilibration) (C892). Paragraph kernel signature predicts operation type with HIGH_K concentrating escape/recovery and HIGH_H concentrating active processing (C893). Phases: REVERSE_BRUNSCHWIG_TEST, BRUNSCHWIG_CLOSED_LOOP_DIMENSIONS.

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| 890 | Recovery Rate-Pathway Independence (FQ rate and post-FQ kernel vary independently; extends C458) | 2 | B | -> [C890_recovery_rate_pathway_independence.md](C890_recovery_rate_pathway_independence.md) |
| 891 | ENERGY-FREQUENT Inverse Correlation (rho=-0.80; high energy = low escape operators) | 2 | B | -> [C891_energy_frequent_inverse.md](C891_energy_frequent_inverse.md) |
| 892 | Post-FQ h-Dominance (h 24-36% post-FQ vs e 3-8%; recovery enters via phase-check) | 2 | B | -> [C892_post_fq_h_dominance.md](C892_post_fq_h_dominance.md) |
| 893 | Paragraph Kernel Signature Predicts Operation Type (HIGH_K=2x FQ p<0.0001; HIGH_H=elevated EN p=0.036; maps to Brunschwig operation categories) | 2 | B | -> [C893_paragraph_kernel_operation_mapping.md](C893_paragraph_kernel_operation_mapping.md) |
| 894 | REGIME_4 Recovery Specialization Concentration (33% recovery-specialized folios in REGIME_4 vs 0-3% other REGIMEs; chi-sq=28.41 p=0.0001; validates C494 precision interpretation at paragraph level) | 2 | B | -> [C894_regime4_recovery_concentration.md](C894_regime4_recovery_concentration.md) |
| 895 | Kernel-Recovery Correlation Asymmetry (k-FQ: r=+0.27; h-FQ: r=-0.29; e-FQ: n.s.; phase monitoring substitutes for recovery) | 2 | B | -> [C895_kernel_recovery_correlation.md](C895_kernel_recovery_correlation.md) |
| 896 | Process Mode Discrimination via Kernel Profile (HIGH_K_LOW_H=2.5x FQ; discriminates distillation from boiling/decoction) | 3 | B | -> [C896_process_mode_discrimination.md](C896_process_mode_discrimination.md) |
| 897 | Prefixed FL MIDDLEs as Line-Final State Markers (tokens contain FL TERMINAL MIDDLEs am/y/dy/ly per C777; 72.7% line-final; operation→state mapping extends FL state index) | 2 | B | -> [C897_apparatus_output_markers.md](C897_apparatus_output_markers.md) |

---

## A PP Internal Structure (C898-C899) - Phase: A_PP_INTERNAL_STRUCTURE

> **Summary:** Currier A PP vocabulary has significant internal organization that refines C234's aggregate "position-free" finding. PP tokens exhibit positional preferences (KS p<0.0001), with LATE-biased MIDDLEs (m, am, d, dy at 0.75-0.85) and EARLY-biased MIDDLEs (or at 0.35). Co-occurrence network shows scale-free hub structure (CV=1.69) with iin as mega-hub (degree 277). Shared MIDDLEs maintain consistent within-line positional roles across A and B (r=0.654, p<0.0001) - a corpus-level grammar property, not a folio-level mapping.

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| 898 | A PP Internal Structure (positional preferences p<0.0001; hub network CV=1.69; refines C234 aggregate position-freedom) | 2 | A | -> [C898_a_pp_internal_structure.md](C898_a_pp_internal_structure.md) |
| 899 | A-B Within-Line Positional Correspondence (shared MIDDLEs have consistent within-line positions across systems r=0.654 p<0.0001; corpus-level grammar property, not folio-level mapping) | 2 | A↔B | -> [C899_ab_positional_correspondence.md](C899_ab_positional_correspondence.md) |

---

## Prefix/Suffix Function (C371-C382, C495)

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| 371 | Prefixes have POSITIONAL GRAMMAR | 2 | B | ⊂ morphology |
| 372 | Kernel dichotomy (100% vs <5%) | 2 | B | ⊂ morphology |
| 373 | LINK affinity patterns | 2 | B | ⊂ morphology |
| 375 | Suffixes have POSITIONAL GRAMMAR | 2 | B | ⊂ morphology |
| 382 | MORPHOLOGY ENCODES CONTROL PHASE | 2 | GLOBAL | → [C382_morphology_control_phase.md](C382_morphology_control_phase.md) |
| **495** | **SUFFIX–REGIME Compatibility Breadth** (-r universal, -ar/-or restricted; V=0.159) | 2 | A→B | ⊂ morphology |

---

## Global Architecture (C383-C393)

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| 383 | GLOBAL MORPHOLOGICAL TYPE SYSTEM | 2 | GLOBAL | → [C383_global_type_system.md](C383_global_type_system.md) |
| 384 | NO TOKEN-LEVEL OR CONTEXT-FREE A-B LOOKUP | 2 | A↔B | → [C384_no_entry_coupling.md](C384_no_entry_coupling.md) |
| 384.a | CONDITIONAL RECORD-LEVEL CORRESPONDENCE PERMITTED | 2 | A↔B | → [C384a_conditional_correspondence.md](C384a_conditional_correspondence.md) |
| 385 | STRUCTURAL GRADIENT in Currier A | 2 | A | ⊂ currier_a |
| 389 | BIGRAM-DOMINANT local determinism (H=0.41 bits) | 2 | B | ⊂ grammar_system |
| 391 | CONDITIONAL ENTROPY SYMMETRY (H(X|past)=H(X|future); constraint symmetry, not transition symmetry - see C886) | 2 | B | ⊂ grammar_system |
| 392 | ROLE-LEVEL CAPACITY (97.2% observed) | 2 | B | ⊂ grammar_system |
| 393 | FLAT TOPOLOGY (diameter=1) | 2 | B | ⊂ grammar_system |

---

## Control Strategies (C394-C403)

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| 394 | INTENSITY-ROLE DIFFERENTIATION | 2 | B | ⊂ operations |
| 395 | DUAL CONTROL STRATEGY | 2 | B | ⊂ operations |
| 397 | qo-prefix = escape route (25-47%) | 2 | B | ⊂ grammar_system |
| 400 | BOUNDARY HAZARD DEPLETION (5-7x) | 2 | B | ⊂ grammar_system |
| 403 | 5 PROGRAM ARCHETYPES (continuum) | 2 | B | ⊂ operations |

---

## Human Track Closure (C404-C406, C413-C419)

> **Context-Sufficient Summary:** [HT_CONTEXT_SUMMARY.md](HT_CONTEXT_SUMMARY.md)

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| 404 | HT TERMINAL INDEPENDENCE (p=0.92) | 2 | HT | → [C404_ht_non_operational.md](C404_ht_non_operational.md) |
| 405 | HT CAUSAL DECOUPLING (V=0.10) | 2 | HT | ⊂ human_track |
| 406 | HT GENERATIVE STRUCTURE (Zipf=0.89) | 2 | HT | ⊂ human_track |
| 413 | HT prefix phase-class predicted by preceding grammar (V=0.319) | 2 | HT | → [C413_ht_grammar_trigger.md](C413_ht_grammar_trigger.md) |
| 414 | HT STRONG GRAMMAR ASSOCIATION (chi2=934) | 2 | HT | ⊂ human_track |
| 415 | HT NON-PREDICTIVITY (MAE worsens) | 1 | HT | ⊂ human_track |
| 416 | HT DIRECTIONAL ASYMMETRY (V=0.324 vs 0.202) | 2 | HT | ⊂ human_track |
| 417 | HT MODULAR ADDITIVE (no synergy, p=1.0) | 2 | HT | ⊂ human_track |
| 418 | HT POSITIONAL WITHOUT INFORMATIVENESS | 2 | HT | ⊂ human_track |
| 419 | HT POSITIONAL SPECIALIZATION IN A (entry-aligned) | 2 | A+HT | ⊂ human_track |

---

## Sister Pairs (C407-C412)

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| 407 | DA = INFRASTRUCTURE | 2 | GLOBAL | ⊂ morphology |
| 408 | ch-sh/ok-ot form EQUIVALENCE CLASSES | 2 | GLOBAL | → [C408_sister_pairs.md](C408_sister_pairs.md) |
| 409 | Sister pairs MUTUALLY EXCLUSIVE but substitutable | 2 | GLOBAL | ⊂ morphology |
| 410 | Sister choice is SECTION-CONDITIONED | 2 | B | ⊂ morphology |
| 412 | ch-preference anticorrelated with qo-escape density (rho=-0.33) | 2 | B | → [C412_sister_escape_anticorrelation.md](C412_sister_escape_anticorrelation.md) |

---

## SITD Findings (C411)

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| 411 | Grammar DELIBERATELY OVER-SPECIFIED (~40% reducible) | 2 | B | → [C411_over_specification.md](C411_over_specification.md) |

---

## B Design Space (C458)

> **Summary:** C458 establishes that B programs exhibit asymmetric design freedom - hazard exposure is tightly clamped while recovery architecture varies freely. Regimes partition design space cleanly.

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| **458** | **Execution Design Clamp vs Recovery Freedom** (CV 0.04-0.11 vs 0.72-0.82) | 2 | B | -> [C458_execution_design_clamp.md](C458_execution_design_clamp.md) |

**C458.a (sub-finding):** Hazard/LINK mutual exclusion surface (r = -0.945). Revisit after D2/D3.

---

## HT Cross-System Compensation (C459)

> **Summary:** C459 establishes that HT anticipates B stress at quire level, with the compensation pattern varying by regime.

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| **459** | **HT Anticipatory Compensation** (quire r=0.343, p=0.0015, HT precedes stress) | 2 | HT/B | -> [C459_ht_anticipatory_compensation.md](C459_ht_anticipatory_compensation.md) |

**C459.a (sub-finding):** REGIME_2 shows inverted compensation (high HT despite low tension).

**C459.b (sub-finding):** ~~Zero-escape -> max HT~~ **WITHDRAWN** (v2.12) - data error corrected. Zero-escape does NOT correlate with elevated HT.

---

## AZC Entry Orientation (C460)

> **Summary:** C460 establishes that AZC folios mark natural HT transition zones in the manuscript. HT is elevated before AZC pages and reduced after them, but this pattern resembles random positions more than A or B entries.

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| 460 | AZC Entry Orientation Effect (step-change p<0.002, decay R^2>0.86) | 2 | HT/AZC | -> [C460_azc_entry_orientation.md](C460_azc_entry_orientation.md) |

**Key finding:** AZC trajectory differs from A and B systems but NOT from random - suggests AZC is **placed at** transitions, not **causing** them.

---

## HT Threading (C450-C453, C457, C477)

> **Summary:** C450-C453 jointly establish HT as a manuscript-wide, codicologically clustered orientation layer with unified vocabulary and session-level continuity. C457 shows HT anchors preferentially to boundary positions within AZC.

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| 450 | HT Quire Clustering (H=47.20, p<0.0001, eta-sq=0.150) | 2 | HT/GLOBAL | -> [C450_ht_quire_clustering.md](C450_ht_quire_clustering.md) |
| 451 | HT System Stratification (A > AZC > B density) | 2 | HT/GLOBAL | -> [C451_ht_system_stratification.md](C451_ht_system_stratification.md) |
| 452 | HT Unified Prefix Vocabulary (Jaccard >= 0.947) | 2 | HT/GLOBAL | -> [C452_ht_unified_vocabulary.md](C452_ht_unified_vocabulary.md) |
| 453 | HT Adjacency Clustering (1.69x enrichment, stronger than C424) | 2 | HT/GLOBAL | -> [C453_ht_adjacency_clustering.md](C453_ht_adjacency_clustering.md) |
| **457** | **HT Boundary Preference in Zodiac AZC** (S=39.7% > R=29.5%, V=0.105) | 2 | HT/AZC | -> [C457_ht_boundary_preference.md](C457_ht_boundary_preference.md) |
| **477** | **HT Tail Correlation** (r=0.504, p=0.0045, R²=0.28) | 2 | HT/A | -> [C477_ht_tail_correlation.md](C477_ht_tail_correlation.md) |

---

## Survivor-Set Dimensionality (C479-C481)

> **Summary:** C479-C481 close the last open gap in A→AZC→HT integration. Survivor-set size scales discrimination responsibility (C479), survivor sets are unique constraint fingerprints (C481), and there is marginal evidence for B micro-variability correlation (C480, Tier 3).

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| **479** | **Survivor-Set Discrimination Scaling** (partial rho=0.395, p<10^-29) | 2 | A+AZC+HT | -> [C479_survivor_discrimination_scaling.md](C479_survivor_discrimination_scaling.md) |
| 480 | Constrained Execution Variability (rho=0.306, p=0.078, PROVISIONAL) | 3 | A→B | -> [C480_constrained_variability.md](C480_constrained_variability.md) |
| **481** | **Survivor-Set Uniqueness** (0 collisions in 1575 lines) | 2 | A+AZC | -> [C481_survivor_set_uniqueness.md](C481_survivor_set_uniqueness.md) |

---

## Batch Processing Semantics (C482-C484)

> **Summary:** C482-C484 close the last open questions about A→B operational semantics. A line multiplicity specifies compound input (C482); repetition is ordinal emphasis only (C483); A channel is bifurcated into registry entries and control operators (C484).

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| **482** | **Compound Input Specification** (B invariant to A line length, p=1.0) | 2 | A→B | -> [C482_compound_input_specification.md](C482_compound_input_specification.md) |
| **483** | **Ordinal Repetition Invariance** (magnitude has no downstream effect) | 2 | A | -> [C483_ordinal_repetition_invariance.md](C483_ordinal_repetition_invariance.md) |
| **484** | **A Channel Bifurcation** (registry entries + control operators, p<0.01) | 2 | A | -> [C484_a_channel_bifurcation.md](C484_a_channel_bifurcation.md) |

---

## Semantic Ceiling Extension (C485-C489)

> **Summary:** C485-C489 establish grammar minimality, bidirectional constraint coherence, A-registry memory optimization, and HT operational load predictions from the SEMANTIC_CEILING_EXTENSION phase.

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| **485** | **Grammar Minimality** (e-operator and h->k suppression are load-bearing) | 2 | B | -> [C485_grammar_minimality.md](C485_grammar_minimality.md) |
| 486 | Bidirectional Constraint Coherence (B behavior constrains A zone inference) | 3 | CROSS_SYSTEM | -> [C486_bidirectional_constraints.md](C486_bidirectional_constraints.md) |
| 487 | A-Registry Memory Optimization (z=-97 vs random, 0th percentile) | 3 | A | -> [C487_memory_optimization.md](C487_memory_optimization.md) |
| 488 | HT Predicts Strategy Viability (r=0.46 CAUTIOUS, r=-0.48 OPPORTUNISTIC) | 3 | HT | -> [C488_ht_strategy_prediction.md](C488_ht_strategy_prediction.md) |
| 489 | HT Zone Diversity Correlation (r=0.24, p=0.0006) | 3 | HT | -> [C489_ht_zone_diversity.md](C489_ht_zone_diversity.md) |

---

## Structural Topology Tests (C490-C492)

> **Summary:** C490-C492 establish categorical strategy exclusion and PREFIX phase-exclusive legality from the STRUCTURAL_TOPOLOGY_TESTS phase. C491 (Judgment-Critical Axis) remains Tier 3 interpretive.

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| **490** | **Categorical Strategy Exclusion** (20.5% of programs forbid AGGRESSIVE, not gradient but prohibition) | 2 | B | -> [C490_categorical_strategy_exclusion.md](C490_categorical_strategy_exclusion.md) |
| 491 | Judgment-Critical Program Axis (OPPORTUNISTIC orthogonal to caution/aggression) | 3 | B | ⊂ SPECULATIVE |
| **492** | **PREFIX Phase-Exclusive Legality** (ct PREFIX is 0% C/S-zones, 26% P-zone, invariant) | 2 | A→AZC | -> [C492_prefix_phase_exclusion.md](C492_prefix_phase_exclusion.md) |

---

## Brunschwig Template Fit (C493-C494)

> **Summary:** C493-C494 establish that Brunschwig distillation procedures can be expressed in Voynich grammar at the constraint level, and clarify the precision axis interpretation for REGIME_4.

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| **493** | **Brunschwig Grammar Embedding** (balneum marie procedure fits with 0 forbidden violations) | 2 | B | -> [C493_brunschwig_grammar_embedding.md](C493_brunschwig_grammar_embedding.md) |
| **494** | **REGIME_4 Precision Axis** (encodes precision-constrained execution, not intensity) | 2 | B | -> [C494_regime4_precision_axis.md](C494_regime4_precision_axis.md) |

---

## Currier A Positional (C420)

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| 420 | Folio-initial position permits otherwise illegal C+vowel variants (ko-, po-, to-) | 2 | A | -> [C420_folio_initial_exception.md](C420_folio_initial_exception.md) |

---

## Currier A Adjacency (C424)

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| 424 | Adjacency coherence is clustered, not uniform (~3-entry runs, autocorr r=0.80) | 2 | A | -> [C424_clustered_adjacency.md](C424_clustered_adjacency.md) |

---

## Currier A Meta-Structural Artifacts (C497)

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| **497** | **f49v Instructional Apparatus Folio** (26 L-labels alternating 1:1 with example lines, demonstrates morphology limits) | 2 | A | ⊂ currier_a |

---

## A-Exclusive Vocabulary Track (C498-C509)

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| **498** | **Registry-Internal Vocabulary Track** (61.8% A-exclusive MIDDLEs: ct-prefix 5.1×, suffix-less 3×, folio-localized; don't propagate to B) | 2 | A | ⊂ currier_a |
| **498.a** | **A∩B Shared Vocabulary Bifurcation** (154 AZC-Mediated + 114 B-Native Overlap; pipeline scope narrowed) | 2 | A | ⊂ currier_a |
| **498.b** | **RI Singleton Population** (~977 singletons, mean 4.82 chars; functional interpretation WEAKENED - see C498.d) | 2 | A | ⊂ currier_a |
| **498.c** | **RI Repeater Population** (~313 repeaters, mean 3.61 chars; functional interpretation WEAKENED - see C498.d) | 2 | A | ⊂ currier_a |
| **498.d** | **RI Length-Frequency Correlation** (rho=-0.367, p<10⁻⁴²; singleton rate: 2-char=48%, 6-char=96%; complexity gradient, not functional bifurcation) | 2 | A | ⊂ currier_a |
| 499 | Bounded Material-Class Recoverability (128 MIDDLEs with P(material_class) vectors; conditional on Brunschwig) | 3 | A | ⊂ currier_a |
| 500 | Suffix Posture Temporal Pattern (CLOSURE front-loaded 77% Q1, NAKED late 38% Q4, ratio 5.69×) | 3 | A | ⊂ currier_a |
| **501** | **B-Exclusive MIDDLE Stratification** (569 B-exclusive types: L-compounds 49, boundary closers, 80% singletons; elaboration not novelty) | 2 | B | ⊂ currier_a |
| **502** | **A-Record Viability Filtering** (Strict interpretation: ~96/480 B tokens legal per A; 13.3% mean B folio coverage; 80% filtered) | 2 | A+B | ⊂ currier_a |
| **502.a** | **Full Morphological Filtering Cascade** (PREFIX+MIDDLE+SUFFIX: 38 tokens legal (0.8%); MIDDLE 5.3%, +PREFIX 64% reduction, +SUFFIX 50% reduction, combined 85% beyond MIDDLE) | 2 | A+B | ⊂ currier_a |
| **503** | **Class-Level Filtering** (MIDDLE-only: 1,203 unique patterns, 6 always-survive classes, 32.3 mean; infrastructure classes vulnerable) | 2 | A+B | ⊂ currier_a |
| **503.a** | **Class Survival Under Full Morphology** (PREFIX+MIDDLE+SUFFIX: 6.8 mean classes (10.8%); 83.7% reduction from MIDDLE-only; ~7 classes = actual instruction budget) | 2 | A+B | ⊂ currier_a |
| **503.b** | **No Universal Classes Under Full Morphology** (C121's 49 classes: 0 universal; Class 9 highest at 56.1%; C503's "6 unfilterable" = 10-56% coverage; MIDDLE-only claim doesn't hold under full filtering) | 2 | A+B | ⊂ currier_a |
| **503.c** | **Kernel Character Coverage** (k/h/e are chars within tokens, not standalone; h=95.6%, k=81.1%, e=60.8%; union=97.6%; only 2.4% lack kernel access; kernel nearly universal) | 2 | A+B | ⊂ currier_a |
| **504** | **MIDDLE Function Bifurcation** (PP 86 types r=0.772 with survival; RI 1,293 types r=-0.046; 75% records have both) | 2 | A+B | ⊂ currier_a |
| **505** | **PP Profile Differentiation by Material Class** ('te' 16.1×, 'ho' 8.6×, 'ke' 5.1× in animal records; A-registry organization only) | 2 | A | ⊂ currier_a |
| **506** | **PP Composition Non-Propagation** (PP count r=0.715; composition cosine=0.995 with baseline; capacity not routing) | 2 | A+B | ⊂ currier_a |
| **506.a** | **Intra-Class Token Configuration** (Same classes, different PP: Jaccard=0.953; ~5% token variation; classes=types, tokens=parameterizations) | 2 | A+B | ⊂ currier_a |
| **506.a.i** | **PP Cross-Class Coordination Mechanism** (57% MIDDLEs span multiple classes; MIDDLE orthogonal to CLASS; selects coherent variant slice across grammar) | 2 | A+B | ⊂ currier_a |
| **506.b** | **Intra-Class Behavioral Heterogeneity** (Different-MIDDLE tokens: same position p=0.11, different transitions p<0.0001; 73% MIDDLE pairs have JS>0.4) | 2 | B | ⊂ currier_a |
| **507** | **PP-HT Partial Responsibility Substitution** (rho=-0.294, p=0.0015; PP 0-3 = 18.8% HT vs PP 6+ = 12.6% HT; HT TTR r=+0.40) | 2 | A+HT | ⊂ currier_a, human_track |
| **508** | **Token-Level Discrimination Primacy** (MIDDLE-only: Class Jaccard=0.391, Token Jaccard=0.700; 27.5% within-class mutual exclusion; fine discrimination at member level, not class level) | 2 | A→B | ⊂ currier_a |
| **508.a** | **Class-Level Discrimination Under Full Morphology** (REVISION: Full morph Class Jaccard=0.755, Token=0.961; 27% class mutual exclusion; "WHICH" now matters, not just "HOW MANY") | 2 | A→B | ⊂ currier_a |
| **509** | **PP/RI Dimensional Separability** (72 PP sets shared by records with different RI; 229 records (14.5%) share PP; 26 pure-RI, 399 pure-PP; dimensions orthogonal) | 2 | A | ⊂ currier_a |
| **509.a** | **RI Morphological Divergence** (RI: 58.5% PREFIX, 3.96-char MIDDLE; PP: 85.4% PREFIX, 1.46-char MIDDLE; RI is MIDDLE-centric, PP is template-balanced) | 2 | A | ⊂ currier_a |
| **509.b** | **PREFIX-Class Determinism** (Class P_xxx requires A-PREFIX 'xxx' with 100% necessity; sufficiency 72-100%; 27% mutual exclusion = PREFIX sparsity) | 2 | A→B | ⊂ currier_a |
| **509.c** | **No Universal Instruction Set** (0 classes in ALL records; BARE highest at 96.8%; 50 records lack BARE-compatible MIDDLEs; ~7 classes = ~2.5 PREFIXes + BARE + SUFFIXes) | 2 | A→B | ⊂ currier_a |
| **509.d** | **Independent Morphological Filtering** (PREFIX/MIDDLE/SUFFIX filter independently; 27% class ME = morphological sparsity not class interaction; SUFFIX classes 100% PREFIX-free) | 2 | A→B | ⊂ currier_a |
| **510** | **Positional Sub-Component Grammar** (41.2% constrained: 62 START, 14 END, 110 FREE; z=34.16, p<0.0001; grammar is permissive) | 2 | A | ⊂ currier_a |
| **511** | **Derivational Productivity** (Repeater MIDDLEs seed singletons at 12.67x above chance; 89.8% exceed baseline) | 2 | A | ⊂ currier_a |
| **512** | **PP/RI Stylistic Bifurcation** (100% containment but z=1.11 vs null - NOT significant; 8.3x section-invariance; composition PROVISIONAL) | 2 | GLOBAL | ⊂ currier_a |
| **512.a** | **Positional Asymmetry** (END-class 71.4% PP; START-class 16.1% PP; pattern: RI-START + PP-FREE + PP-END) | 2 | A | ⊂ currier_a |
| **513** | **Short Singleton Sampling Variance** (Jaccard=1.00 vs repeaters; singleton status at ≤3 chars is sampling, not function) | 2 | A | ⊂ currier_a |
| **514** | **RI Compositional Bifurcation** (17.4% locally-derived, 82.6% globally-composed; Section P highest local rate 26.1%) | 2 | A | ⊂ currier_a |
| **515** | **RI Compositional Mode Correlates with Length** (short RI = atomic/global; long RI = compound/local; rho=0.192, p<0.0001) | 2 | A | ⊂ currier_a |
| **515.a** | **Compositional Embedding Mechanism** (local derivation is additive - embedding local PP context requires more sub-components) | 2 | A | ⊂ currier_a |
| **516** | **RI Multi-Atom Observation** (99.6% multi-atom but trivially expected from lengths; intersection formula PROVISIONAL) | 2 | A | ⊂ currier_a |
| **517** | **Superstring Compression (GLOBAL)** (65-77% overlap, 2.2-2.7x compression; hinge letters are 7/8 kernel primitives; global substrate) | 3 | GLOBAL | ⊂ currier_a |
| **518** | **Compatibility Enrichment (GLOBAL)** (5-7x enrichment across all systems; extends C383 global type system) | 3 | GLOBAL | ⊂ currier_a |
| **519** | **Global Compatibility Architecture** (compression + enrichment = embedded compatibility relationships spanning A/B/AZC) | 3 | GLOBAL | ⊂ currier_a |
| **520** | **System-Specific Exploitation Gradient** (RI 6.8x > AZC 7.2x > PP 5.5x > B 5.3x; discrimination intensity varies) | 3 | GLOBAL | ⊂ currier_a |
| **523** | **Pharma Label Vocabulary Bifurcation** (jar labels Jaccard=0.000 with content; content 58.3% PP vs 33.5% baseline) | 2 | A | ⊂ currier_a |
| **524** | **Jar Label Morphological Compression** (7.1 vs 6.0 char mean; 5-8 PP atoms per MIDDLE; superstring packing) | 2 | A | ⊂ currier_a |
| **525** | **Label Morphological Stratification** (o-prefix 50% vs 20% text; qo-prefix ~0% vs 14%; 61% label-only vocabulary; within-group MIDDLE sharing) | 3 | A | ⊂ currier_a |
| **526** | **RI Lexical Layer Hypothesis** (609 unique RI as referential lexicon; 87% localized to 1-2 folios; PREFIX/SUFFIX global grammar vs RI extensions as substance anchors) | 3 | A | ⊂ currier_a |
| **527** | **Suffix-Material Class Correlation** (Animal PP: 0% -y/-dy, 78% -ey/-ol; Herb PP: 41% -y/-dy, 27% -ey/-ol; chi2=178, p<10^-40; fire-degree interpretation conditional on Brunschwig) | 3 | A | ⊂ currier_a |
| **528** | **RI PREFIX Lexical Bifurcation** (334 PREFIX-REQUIRED, 321 PREFIX-FORBIDDEN, 12 optional; 98.2% disjoint; PREFIX attachment lexically determined; section-independent; refines C509.a aggregate rate) | 2 | A | ⊂ currier_a |
| **529** | **Gallows Positional Asymmetry** (PP gallows-initial 30% vs RI 20%; RI gallows-medial 58% vs PP 39%; chi2=7.69 p<0.01; bench gallows cph 81% RI; parallel bifurcation to C528) | 2 | A | ⊂ currier_a |
| **530** | **Gallows Folio Specialization** (k-default 54%, t-specialized folios cluster; p/f never folio-dominant; 2-5x same-gallows co-occurrence RI↔PP in records) | 2 | A | ⊂ currier_a |
| **531** | **Folio Unique Vocabulary Prevalence** (98.8% of B folios have ≥1 unique MIDDLE; only f95r1 lacks unique vocabulary; mean 10.5 unique MIDDLEs per folio) | 2 | B | ⊂ currier_a |
| **532** | **Unique MIDDLE B-Exclusivity** (88% of unique B MIDDLEs are B-exclusive, not in A; 12% are PP; unique vocabulary is primarily B-internal grammar, not AZC-modulated) | 2 | B | ⊂ currier_a |
| **533** | **Unique MIDDLE Grammatical Slot Consistency** (75% of unique MIDDLE tokens share PREFIX/SUFFIX patterns with classified tokens; adjacent folios' unique MIDDLEs fill similar slots 1.30x vs non-adjacent) | 2 | B | ⊂ currier_a |
| 534 | Section-Specific Prefixless MIDDLE Profiles (prefixless unique MIDDLEs show section-specific distribution p=0.023; effect vanishes for prefixed tokens where PREFIX-section associations explain pattern; partial signal only) | 3 | B | ⊂ currier_a |
| **535** | **B Folio Vocabulary Minimality** (81/82 folios needed for complete MIDDLE coverage; redundancy ratio 1.01x; zero folio pairs exceed 50% Jaccard; each folio contributes mean 10.5 unique MIDDLEs) | 2 | B | ⊂ currier_a |
| **536** | **Material-Class REGIME Invariance** (Both animal AND herb material classes route to REGIME_4: animal 2.03x p=0.024, herb 2.09x p=0.011; REGIME encodes precision requirement, not material identity) | 2 | A->B | ⊂ currier_a |
| **537** | **Token-Level Material Differentiation** (Despite identical REGIME routing, 62% of token variants differ: overall Jaccard=0.382, per-class mean=0.371; confirms C506.b behavioral heterogeneity) | 2 | A->B | ⊂ currier_a |
| 538 | PP Material-Class Distribution (ANIMAL 15.6%, HERB 28.0%, MIXED 16.6%, NEUTRAL 39.9%; classification conditional on Brunschwig suffix alignment) | 3 | A | ⊂ currier_a |
| **539** | **LATE Prefix Morphological Class** (al/ar/or: V+L pattern, 3.78x line-final enrichment, 68-70% suffix-depleted, short MIDDLE preference) | 2 | B | -> [C539_late_prefix_class.md](C539_late_prefix_class.md) |

---

## Instruction Class Characterization (C540-C546)

> **Summary:** C540-C546 characterize the 49 instruction classes at role and class level, including kernel binding, hazard topology, positional grammar, and REGIME correlation.

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| **540** | **Kernel Primitives Are Bound Morphemes** (k, e, h never standalone; 0 occurrences each; intervention modifiers only) | 2 | MORPHOLOGY | -> [C540_kernel_bound_morpheme.md](C540_kernel_bound_morpheme.md) |
| **541** | **Hazard Class Enumeration** (only 6/49 classes participate in 17 forbidden transitions; 43 classes have 0% hazard involvement) | 2 | HAZARD_TOPOLOGY | -> [C541_hazard_class_enumeration.md](C541_hazard_class_enumeration.md) |
| **542** | **Gateway/Terminal Hazard Class Asymmetry** (Class 30 = pure gateway, Class 31 = pure terminal; 100% asymmetry) | 2 | HAZARD_TOPOLOGY | -> [C542_gateway_terminal_asymmetry.md](C542_gateway_terminal_asymmetry.md) |
| **543** | **Role Positional Grammar** (FLOW final-biased 0.68, CORE initial-biased 0.45; Class 40 = 69% line-final) | 2 | POSITIONAL_GRAMMAR | -> [C543_role_positional_grammar.md](C543_role_positional_grammar.md) |
| **544** | **ENERGY_OPERATOR Interleaving** (qo/ch-sh families alternate with 2.5x enrichment; Class 33 self-repeat 14.6%) | 2 | CO-OCCURRENCE | -> [C544_energy_interleaving.md](C544_energy_interleaving.md) |
| **545** | **REGIME Instruction Class Profiles** (REGIME_3 = 1.83x CORE_CONTROL; REGIME_1 = 52% qo-family; each REGIME has signature classes) | 2 | REGIME_INTERPRETATION | -> [C545_regime_class_profiles.md](C545_regime_class_profiles.md) |
| **546** | **Class 40 Safe Flow Operator** (daly/aly/ary: 4.22 avg distance from hazards, 0% hazard rate, 69% line-final; safe flow alternative) | 2 | HAZARD_TOPOLOGY | -> [C546_class40_safe_flow.md](C546_class40_safe_flow.md) |
| 547 | qo-Chain REGIME_1 Enrichment (1.53x enrichment, 51.4% of chains in REGIME_1; depleted in REGIME_2/3; thermal processing context) | 3 | B | -> [C547_qo_chain_regime_enrichment.md](C547_qo_chain_regime_enrichment.md) |
| **548** | **Manuscript-Level Gateway/Terminal Envelope** (90.2% folios have both; rho=0.499 count correlation; gateways front-loaded rho=-0.368; arc from entry to exit) | 2 | B | -> [C548_manuscript_level_envelope.md](C548_manuscript_level_envelope.md) |
| **549** | **qo/ch-sh Interleaving Significance** (56.3% vs 50.6% expected; z=10.27, p<0.001; grammatical preference for alternation; REGIME_3 highest 59.0%) | 2 | B | -> [C549_interleaving_significance.md](C549_interleaving_significance.md) |
| **550** | **Role Transition Grammar** (roles self-chain: FREQ 2.38x, FLOW 2.11x, ENERGY 1.35x; FLOW-FREQ bidirectional affinity 1.54-1.73x; ENERGY avoids other roles 0.71-0.80x; phrasal role structure) | 2 | B | -> [C550_role_transition_grammar.md](C550_role_transition_grammar.md) |
| **551** | **Grammar Universality and REGIME Specialization** (67% classes universal; CC most universal 0.836; ENERGY REGIME_1 enriched 1.26-1.48x; FLOW REGIME_1 depleted 0.40-0.63x; thermal/flow anticorrelation) | 2 | B | -> [C551_grammar_universality.md](C551_grammar_universality.md) |
| **552** | **Section-Specific Role Profiles** (Chi2=565.8, p<0.001; BIO +CC +EN thermal-intensive; HERBAL_B +FQ -EN repetitive; PHARMA +FL flow-dominated; RECIPE_B -CC autonomous; sections encode procedural types) | 2 | B | -> [C552_section_role_profiles.md](C552_section_role_profiles.md) |
| **553** | **BIO-REGIME Energy Independence** (BIO 70% REGIME_1; effects additive: baseline 27.5%, +6.5pp REGIME, +9.8pp section; both significant p<0.001; BIO+R1 reaches 48.9% ENERGY through independent combination) | 2 | B | -> [C553_bio_regime_independence.md](C553_bio_regime_independence.md) |
| **554** | **Hazard Class Clustering** (dispersion index 1.29, p<0.001; 93% lines have hazard classes, mean 3.1/line; gateway-terminal 1.06x confirms C548; hazard management is zone-concentrated not point-distributed) | 2 | B | -> [C554_hazard_clustering.md](C554_hazard_clustering.md) |
| **555** | **PHARMA Thermal Operator Substitution** (Class 33 0.20x depleted, Class 34 1.90x enriched in PHARMA; ~10x divergence; section-specific not REGIME-driven; ENERGY operators not interchangeable) | 2 | B | -> [C555_pharma_thermal_substitution.md](C555_pharma_thermal_substitution.md) |
| **556** | **ENERGY Medial Concentration** (ENERGY 0.45x initial, 0.50x final - medial-concentrated; FLOW/FREQ 1.65x final; UNCLASS 1.55x initial; lines have positional template; p=3e-89) | 2 | B | -> [C556_energy_medial_concentration.md](C556_energy_medial_concentration.md) |
| **557** | **daiin Line-Initial ENERGY Trigger** (27.7% line-initial rate, 2.2x CC average; 47.1% ENERGY followers; Class 10 singleton; RECIPE 36.3% initial; unique control signal) | 2 | B | -> [C557_daiin_line_opener.md](C557_daiin_line_opener.md) |
| **558** | **Singleton Class Structure** (only 3 singletons: Class 10/11/12; 2/3 CC classes are singletons; daiin initial-biased 27.7%, ol final-biased 9.5%; complementary control primitives) | 2 | B | -> [C558_singleton_class_structure.md](C558_singleton_class_structure.md) |
| ~~559~~ | ~~FREQUENT Role Structure~~ **SUPERSEDED by C583, C587** (used wrong FQ membership {9,20,21,23}; correct is {9,13,14,23} per ICC) | ~~2~~ | B | -> [C559_frequent_role_structure.md](C559_frequent_role_structure.md) |
| **560** | **Class 17 ol-Derived Control Operators** (9 tokens all PREFIX:ol + ENERGY-morph; BIO 1.72x enriched; PHARMA 0 occurrences; REGIME_3 1.90x; non-singleton CC is ol-derived) | 2 | B | -> [C560_class17_ol_derivation.md](C560_class17_ol_derivation.md) |
| **561** | **Class 9 or->aiin Directional Bigram** (87.5% of chains are or->aiin; zero aiin->aiin; directional grammatical unit; HERBAL 21.7% chain rate; refines C559 "self-chaining") | 2 | B | -> [C561_class9_or_aiin_bigram.md](C561_class9_or_aiin_bigram.md) |
| **562** | **FLOW Role Structure** (19 tokens, 4.7% corpus; final-biased 17.5%; Class 40 59.7% final, ary 100% final; PHARMA 1.38x enriched, BIO 0.83x; ENERGY inverse pattern) | 2 | B | -> [C562_flow_role_structure.md](C562_flow_role_structure.md) |
| **563** | **AX Internal Positional Stratification** (19 AX classes split into INIT/5, MED/8, FINAL/6; H=208.8 p=4.6e-46; 71.8% INIT-before-FINAL; Cohen's d=0.69; positional gradient not clusters) | 2 | B | -> [C563_ax_positional_stratification.md](C563_ax_positional_stratification.md) |
| **564** | **AX Morphological-Positional Correspondence** (AX_INIT: 17.5% articulator; AX_MED: ok/ot 88.8%; AX_FINAL: prefix-light 60.9%, zero articulators; prefix family predicts position) | 2 | B | -> [C564_ax_morphological_positional_correspondence.md](C564_ax_morphological_positional_correspondence.md) |
| **565** | **AX Execution Scaffold Function** (AX mirrors named role positions; 0% hazard; 1.09x self-chaining; AX_FINAL enriched R1 39.4% BIO 40.9%; structural frame not functional operations) | 2 | B | -> [C565_ax_scaffold_function.md](C565_ax_scaffold_function.md) |
| **566** | **UN Token Resolution** (7042 UN = 30.5% of B; 74.1% hapax, 74.8% single-folio; morphologically normal; cosurvival threshold artifact; NOT a separate role) | 2 | B | -> [C566_un_token_resolution.md](C566_un_token_resolution.md) |
| **567** | **AX-Operational MIDDLE Sharing** (57 AX MIDDLEs; 98.2% PP; 72% shared with operational roles; AX-EN Jaccard=0.400; 16 AX-exclusive; 78% PREFIX+ARTICULATOR differentiated) | 2 | B | -> [C567_ax_operational_middle_sharing.md](C567_ax_operational_middle_sharing.md) |
| **568** | **AX Pipeline Ubiquity** (97.2% of A records carry AX vocabulary; 0 zero-AX B contexts; classes 21,22 always survive; AX_FINAL 100%, all subgroups 95.6%) | 2 | B | -> [C568_ax_pipeline_ubiquity.md](C568_ax_pipeline_ubiquity.md) |
| **569** | **AX Proportional Scaling** (AX fraction 0.454 vs expected 0.455; R²=0.83; NOT pure byproduct; AX_INIT over-represented slope 0.130 vs 0.102; AX_FINAL under-represented) | 2 | B | -> [C569_ax_proportional_scaling.md](C569_ax_proportional_scaling.md) |
| **570** | **AX PREFIX Derivability** (89.6% binary accuracy; PREFIX is role selector; 22 AX-exclusive prefixes; F1=0.904; same MIDDLE becomes AX or operational via PREFIX) | 2 | B | -> [C570_ax_prefix_derivability.md](C570_ax_prefix_derivability.md) |
| **571** | **AX Functional Identity Resolution** (AX = PREFIX-determined default mode of pipeline vocabulary; same MIDDLEs serve as scaffold or operations; PREFIX selects role, MIDDLE carries material) | 2 | B | -> [C571_ax_functional_identity.md](C571_ax_functional_identity.md) |
| **572** | **AX Class Behavioral Collapse** | 2 | B | AX_CLASS_BEHAVIOR |
| **573** | **EN Definitive Count: 18 Classes** (ICC-based: {8, 31-37, 39, 41-49}; resolves BCSC=11 undercount; 7211 tokens = 31.2% of B; Core 6 = 79.5%, Minor 12 = 20.5%) | 2 | B | -> [C573_en_definitive_count.md](C573_en_definitive_count.md) |
| **574** | **EN Distributional Convergence** (k=2 silhouette 0.180; QO/CHSH identical positions, REGIME, context (JS=0.0024); but MIDDLE Jaccard=0.133, trigger chi2=134; grammatically equivalent, lexically partitioned; C276/C423 within single role) | 2 | B | -> [C574_en_behavioral_collapse.md](C574_en_behavioral_collapse.md) |
| **575** | **EN is 100% Pipeline-Derived** (64 unique MIDDLEs, all PP; 0 RI, 0 B-exclusive; even purer than AX's 98.2% PP; vocabulary entirely inherited from Currier A) | 2 | B | -> [C575_en_pipeline_derived.md](C575_en_pipeline_derived.md) |
| **576** | **EN MIDDLE Vocabulary Bifurcation by Prefix** (QO uses 25 MIDDLEs, CHSH uses 43; only 8 shared, Jaccard=0.133; PREFIX selects MIDDLE subvocabulary, not grammatical function) | 2 | B | -> [C576_en_middle_bifurcation.md](C576_en_middle_bifurcation.md) |
| **577** | **EN Interleaving is Content-Driven** (QO/CHSH same positions p=0.104; BIO 58.5%, PHARMA 27.5%; alternation is material-type selection, not positional) | 2 | B | -> [C577_en_interleaving_content_driven.md](C577_en_interleaving_content_driven.md) |
| **578** | **EN Has 30 Exclusive MIDDLEs** (46.9% of EN vocabulary; not shared with AX, CC, FL, or FQ; dedicated content subvocabulary within pipeline) | 2 | B | -> [C578_en_exclusive_middles.md](C578_en_exclusive_middles.md) |
| **579** | **CHSH-First Ordering Bias** (53.9% CHSH-first in mixed lines; p=0.010, n=1130; modest but significant asymmetry) | 2 | B | -> [C579_chsh_first_ordering.md](C579_chsh_first_ordering.md) |
| **580** | **EN Trigger Profile Differentiation** (CHSH triggered by AX 32.5%, CC 11%; QO triggered by EN-self 53.5%, boundary 68.8%; chi2=134, p<0.001) | 2 | B | -> [C580_en_trigger_profiles.md](C580_en_trigger_profiles.md) |
| **581** | **CC Definitive Census** (CC={10,11,12,17}; 1023 tokens, 4.4% of B; Classes 10,11 active, 12 ghost (zero tokens per C540), 17 ol-derived per C560) | 2 | B | -> [C581_cc_definitive_census.md](C581_cc_definitive_census.md) |
| **582** | **FL Definitive Census** (FL={7,30,38,40}; 1078 tokens, 4.7% of B; 4 classes confirmed vs BCSC=2; hazard pair {7,30} + safe pair {38,40}) | 2 | B | -> [C582_fl_definitive_census.md](C582_fl_definitive_census.md) |
| **583** | **FQ Definitive Census** (FQ={9,13,14,23}; 2890 tokens, 12.5% of B; supersedes C559's {9,20,21,23}; Classes 20,21 are AX per C563) | 2 | B | -> [C583_fq_definitive_census.md](C583_fq_definitive_census.md) |
| **584** | **Near-Universal Pipeline Purity** (CC/EN/FL/FQ all 100% PP; AX 98.2% per C567; pipeline vocabulary dominates all roles; operational roles pure, scaffold near-pure) | 2 | B | -> [C584_near_universal_pipeline_purity.md](C584_near_universal_pipeline_purity.md) |
| **585** | **Cross-Role MIDDLE Sharing** (EN-AX Jaccard=0.400; EN 30 exclusive MIDDLEs; CC/FL/FQ 0-5 exclusive; small roles share heavily with EN/AX; vocabulary partition follows role hierarchy) | 2 | B | -> [C585_cross_role_middle_sharing.md](C585_cross_role_middle_sharing.md) |
| **586** | **FL Hazard-Safe Split** (hazard {7,30} vs safe {38,40}; position p=9.4e-20; final rate p=7.3e-33; FL source-biased 4.5x; Class 30 gateway, Class 40 maximally hazard-distant) | 2 | B | -> [C586_fl_hazard_safe_split.md](C586_fl_hazard_safe_split.md) |
| **587** | **FQ Internal Differentiation** (4-way genuine structure, 100% KW significance; Class 9 medial self-chaining; 13/14 ok/ot-prefixed large medial; 23 minimal final-biased) | 2 | B | -> [C587_fq_internal_differentiation.md](C587_fq_internal_differentiation.md) |
| **588** | **Suffix Role Selectivity** (chi2=5063.2, p<0.001; EN 17 suffix types 61% suffixed; CC 100% suffix-free; FL/FQ ~93% suffix-free; AX intermediate 38%; three-tier suffix structure) | 2 | B | -> [C588_suffix_role_selectivity.md](C588_suffix_role_selectivity.md) |
| **589** | **Small Role Genuine Structure** (CC, FL, FQ all GENUINE_STRUCTURE; CC 75%, FL 100%, FQ 100% KW features significant; contrasts AX COLLAPSED and EN CONVERGENCE) | 2 | B | -> [C589_small_role_genuine_structure.md](C589_small_role_genuine_structure.md) |
| **590** | **CC Positional Dichotomy** (Class 10 daiin initial-biased mean=0.41; Class 11 ol medial-biased mean=0.51; p=2.8e-5; complementary control primitives) | 2 | B | -> [C590_cc_positional_dichotomy.md](C590_cc_positional_dichotomy.md) |
| **591** | **Five-Role Complete Taxonomy** (49 classes → 5 roles: EN=18, AX=19, FQ=4, CC=4, FL=4; complete partition; each role has distinct suffix, position, hazard, section, REGIME profile) | 2 | B | -> [C591_five_role_complete_taxonomy.md](C591_five_role_complete_taxonomy.md) |
| **592** | **C559 Membership Correction** (C559 used {9,20,21,23} for FQ; correct is {9,13,14,23}; C559 SUPERSEDED; downstream C550/C551/C552/C556 flagged for re-verification with corrected membership) | 2 | B | -> [C592_c559_membership_correction.md](C592_c559_membership_correction.md) |
| **593** | **FQ 3-Group Structure** ({9} connector, {13,14} prefixed-pair, {23} closer; k=3 silhouette 0.68; PC1=position 64.2%, PC2=morphology 28.2%; BARE=HAZARDOUS, PREFIXED=SAFE perfect overlap) | 2 | B | -> [C593_fq_3group_structure.md](C593_fq_3group_structure.md) |
| **594** | **FQ 13-14 Complete Vocabulary Bifurcation** (Jaccard=0.000, zero shared MIDDLEs; 13: {aiin,ain,e,edy,eey,eol} 18.2% suffixed; 14: {al,am,ar,ey,ol,or,y} 0% suffixed; sharper than EN C576) | 2 | B | -> [C594_fq_13_14_vocabulary_bifurcation.md](C594_fq_13_14_vocabulary_bifurcation.md) |
| **595** | **FQ Internal Transition Grammar** (chi2=111 p<0.0001; 23→9 enriched 2.85x; 9→13 ratio 4.6:1; all self-chain; 2×2 BARE/PREFIXED chi2=69.7; sequential structure not random mixing) | 2 | B | -> [C595_fq_internal_transition_grammar.md](C595_fq_internal_transition_grammar.md) |
| **596** | **FQ-FL Position-Driven Symbiosis** (chi2=20.5 p=0.015; hazard alignment p=0.33 NS; FL7→FQ9 medial, FL30→FQ13/14 final; symbiosis is positional not hazard-mediated) | 2 | B | -> [C596_fq_fl_position_driven_symbiosis.md](C596_fq_fl_position_driven_symbiosis.md) |
| **597** | **FQ Class 23 Boundary Dominance** (29.8% final rate, 39% of FQ finals despite 12.5% token share; 12.2% initial; mean run length 1.19, 84% singletons; boundary specialist) | 2 | B | -> [C597_fq_class23_boundary_dominance.md](C597_fq_class23_boundary_dominance.md) |
| **598** | **Cross-Boundary Sub-Group Structure** (8/10 pairs significant; FQ_CONN->EN_CHSH 1.41x, FQ_CONN->EN_QO 0.16x; sub-group routing visible across role boundaries) | 2 | B | -> [C598_cross_boundary_subgroup_structure.md](C598_cross_boundary_subgroup_structure.md) |
| **599** | **AX Scaffolding Routing** (chi2=48.3 p=3.9e-4; AX_FINAL avoids EN_QO 0.59x, feeds FQ_CONN 1.31x; AX is routing mechanism not neutral frame) | 2 | B | -> [C599_ax_scaffolding_routing.md](C599_ax_scaffolding_routing.md) |
| **600** | **CC Trigger Sub-Group Selectivity** (chi2=129.2 p=9.6e-21; daiin/ol trigger EN_CHSH 1.60-1.74x, avoid EN_QO 0.18x; ol-derived reverses: EN_QO 1.39x) | 2 | B | -> [C600_cc_trigger_subgroup_selectivity.md](C600_cc_trigger_subgroup_selectivity.md) |
| **601** | **Hazard Sub-Group Concentration** (19 events from 3 source sub-groups: FL_HAZ/EN_CHSH/FQ_CONN; EN_CHSH absorbs 58%; QO never participates) | 2 | B | -> [C601_hazard_subgroup_concentration.md](C601_hazard_subgroup_concentration.md) |
| **602** | **REGIME-Conditioned Sub-Role Grammar** (4/5 pairs REGIME-dependent; AX->FQ REGIME-independent; core routing invariant, magnitudes shift by REGIME) | 2 | B | -> [C602_regime_conditioned_subrole_grammar.md](C602_regime_conditioned_subrole_grammar.md) |
| **603** | **CC Folio-Level Subfamily Prediction** (CC_OL_D fraction->QO proportion rho=0.355 p=0.001; CC_DAIIN fraction->CHSH proportion rho=0.345 p=0.002; CC composition strongest predictor of EN subfamily balance) | 2 | B | -> [C603_cc_folio_level_subfamily_prediction.md](C603_cc_folio_level_subfamily_prediction.md) |
| **604** | **C412 REGIME Decomposition** (C412 rho=-0.304 partially REGIME-mediated, 27.6% reduction; vanishes within REGIME_1 rho=-0.075 and REGIME_2 rho=-0.051; EN subfamily 8.2% and CC composition 11.7% do not mediate) | 2 | B | -> [C604_c412_regime_decomposition.md](C604_c412_regime_decomposition.md) |
| **605** | **Two-Lane Folio-Level Validation** (lane balance predicts escape_density rho=-0.506 vs ch_preference rho=-0.301; adds independent info partial rho=-0.452 p<0.0001; two-lane model validated at folio level) | 2 | B | -> [C605_two_lane_folio_validation.md](C605_two_lane_folio_validation.md) |
| **606** | **CC->EN Line-Level Routing** (chi2=40.28 p<10^-6 V=0.246; CC_OL_D->QO 1.67x enrichment; same-lane pairs 1.81-1.83 tokens apart vs cross-lane 2.48-2.78; token-level routing confirmed) | 2 | B | -> [C606_cc_en_line_level_routing.md](C606_cc_en_line_level_routing.md) |
| **607** | **Line-Level Escape Prediction** (EN_CHSH->escape rho=-0.707 n=2240 p<10^-6, 2.3x stronger than folio C412 rho=-0.304; lane balance->escape rho=-0.363 n=409; escape is line-level phenomenon) | 2 | B | -> [C607_line_level_escape_prediction.md](C607_line_level_escape_prediction.md) |
| **608** | **No Lane Coherence / Local Routing** (coherence p=0.963, lines do not specialize; directionality diff=-0.008 CI[-0.151,0.141]; two-lane model is local token routing, not line-level identity) | 2 | B | -> [C608_no_lane_coherence.md](C608_no_lane_coherence.md) |
| **609** | **LINK Density Reconciliation** (true density 13.2%=3,047/23,096; legacy 6.6% and 38% not reproducible; LINK cuts all 5 ICC roles: AX 26.2%, EN 19.0%, CC 13.8%; 'ol' in MIDDLE 41.2%, PREFIX 28.7%) | 2 | B | -> [C609_link_density_reconciliation.md](C609_link_density_reconciliation.md) |
| **610** | **UN Morphological Profile** (7,042 tokens=30.5% B; 2x suffix rate 77.3% vs 38.7%; 5.3x articulator rate; 79.4% PP MIDDLEs, 0% RI; 90.7% novel MIDDLEs contain PP atoms; complexity is mechanism of non-classification) | 2 | B | -> [C610_un_morphological_profile.md](C610_un_morphological_profile.md) |
| **611** | **UN Role Prediction** (PREFIX assigns 99.2%; consensus 99.9%; EN 37.1%, AX 34.6%, FQ 22.4%, FL 5.9%, CC 0.0%; CC fully resolved; UN is morphological tail of EN/AX/FQ) | 2 | B | -> [C611_un_role_prediction.md](C611_un_role_prediction.md) |
| **612** | **UN Population Structure** (bifurcates k=2 silhouette=0.263; Cluster 0 high-suffix EN/AX, Cluster 1 lower-suffix FQ/AX; hapax longer 6.65 vs 5.84 p<0.0001; UN~TTR rho=+0.631***, UN~LINK rho=-0.524***; REGIME ns) | 2 | B | -> [C612_un_population_structure.md](C612_un_population_structure.md) |
| **613** | **AX-UN Boundary** (2,150 AX-predicted UN tokens; similar positions p=0.084; similar transition contexts; boundary continuous not categorical; if absorbed AX grows 17.9%->27.2% of B) | 2 | B | -> [C613_ax_un_boundary.md](C613_ax_un_boundary.md) |
| **614** | **AX MIDDLE-Level Routing** (MIDDLE predicts successor role: INIT V=0.167 p<0.001, MED V=0.147 p<0.001, FINAL n.s.; no priming; AX~EN diversity rho=+0.796***; Class 22 = extreme FINAL 62.2% line-final) | 2 | B | -> [C614_ax_middle_level_routing.md](C614_ax_middle_level_routing.md) |
| **615** | **AX-UN Functional Integration** (2,246 AX-predicted UN route identically all subgroups p>0.1; 89.3% classified AX MIDDLEs shared; 312 truly novel MIDDLEs; combined AX = 6,098 = 26.4% of B) | 2 | B | -> [C615_ax_un_functional_integration.md](C615_ax_un_functional_integration.md) |
| **616** | **AX Section/REGIME Conditioning** (section: transitions V=0.081, MIDDLE V=0.227; REGIME: transitions V=0.082, AX->EN varies 24.5-39.1% p=0.0006; AX->FQ REGIME-dependent p=0.003 refining C602) | 2 | B | -> [C616_ax_context_conditioning.md](C616_ax_context_conditioning.md) |
| **617** | **AX-LINK Subgroup Asymmetry** (AX_FINAL 35.3% LINK, AX_INIT 19.4%, AX_MED 3.3%; LINK concentrates at AX boundaries; line co-occurrence chi2=16.21 p<0.001; no folio-level correlation p=0.198) | 2 | B | -> [C617_ax_link_subgroup_asymmetry.md](C617_ax_link_subgroup_asymmetry.md) |
| **618** | **Unique MIDDLE Identity** (858 unique MIDDLEs are 100% UN, 99.7% hapax, MIDDLE length 4.55 vs 2.12 shared, 83.1% suffix rate, 88% B-exclusive, 95.7% contain PP atoms; morphological extreme tail of B) | 2 | B | -> [C618_unique_middle_identity.md](C618_unique_middle_identity.md) |
| **619** | **Unique MIDDLE Behavioral Equivalence** (unique vs shared UN transitions: successor V=0.070, predecessor V=0.051; UN-neighbor rate 54.6% vs 47.5%; unique density = UN proportion rho=+0.740***; H1 lexical tail CONFIRMED, H2/H3 REJECTED) | 2 | B | -> [C619_unique_middle_behavioral_equivalence.md](C619_unique_middle_behavioral_equivalence.md) |
| **620** | **Folio Vocabulary Network** (k=2 silhouette=0.055, ARI_section=0.497, ARI_REGIME=0.022; section-controlled adjacency 1.057x vs raw 1.179x; section H vs rest; no manuscript gradient in unique density p=0.676) | 2 | B | -> [C620_folio_vocabulary_network.md](C620_folio_vocabulary_network.md) |
| **621** | **Vocabulary Removal Impact** (removing 868 unique MIDDLE tokens: 96.2% survival, mean role shift 2.80 pp, max 7.04 pp, 1/82 folios lose ICC role; UN -2.71 pp; vocabulary minimality is type diversity, not functional necessity) | 2 | B | -> [C621_vocabulary_removal_impact.md](C621_vocabulary_removal_impact.md) |
| **622** | **Hazard Exposure Anatomy** (43 safe classes: 23 role-excluded (20 AX + 3 CC) + 20 sub-group-excluded (16 EN + 2 FL + 2 FQ); 0 incidental; safe classes route to hazard at 24.6%; FL_SAFE line-final mean=0.811 vs hazard FL 0.546 p<0.001) | 2 | B | -> [C622_hazard_exposure_anatomy.md](C622_hazard_exposure_anatomy.md) |
| **623** | **Hazard Token Morphological Profile** (18 forbidden tokens: 0% suffix, 0% articulator, 33% prefix; best discriminant 68.8% on n=32 baseline 56.2%; hazard participation is lexically specific, not morphologically predictable) | 2 | B | -> [C623_hazard_token_morphological_profile.md](C623_hazard_token_morphological_profile.md) |
| **624** | **Hazard Boundary Architecture** (17 forbidden pairs: 0 occurrences confirmed; 114 near-misses; FL/CC buffer enrichment 1.55x/1.50x; AX under-represented 0.84x; selectivity 6.4% of observed pairs; regime does not predict hazard density p=0.26) | 2 | B | -> [C624_hazard_boundary_architecture.md](C624_hazard_boundary_architecture.md) |
| **625** | **Hazard Circuit Token Mapping** (6/12 classifiable forbidden pairs are reverse-circuit flows; circuit topology explains 75% of classifiable pairs; 4 unclassified tokens trivial; Fisher p=0.193 odds ratio 2.44) | 2 | B | -> [C625_hazard_circuit_token_mapping.md](C625_hazard_circuit_token_mapping.md) |
| **626** | **Lane-Hazard MIDDLE Discrimination** (NULL: two-lane architecture does NOT predict hazard; forbidden MIDDLEs in neither lane 4/5; CC trigger p=0.866; QO contexts have 55% more hazard bigrams than CHSH) | 2 | B | -> [C626_lane_hazard_middle_discrimination.md](C626_lane_hazard_middle_discrimination.md) |
| **627** | **Forbidden Pair Selectivity** (no frequency bias rank 0.562; 0/17 reciprocal-forbidden; circuit topology explains 9/12=75%; FQ_CLOSER boundary tokens account for 3 unexplained; directional token-specific lookup table) | 2 | B | -> [C627_forbidden_pair_selectivity.md](C627_forbidden_pair_selectivity.md) |
| **628** | **FQ_CLOSER Positional Segregation Test** (dy→aiin positionally separated via 35.8% final bias p<0.000001; dy→chey genuine prohibition 1 adj to class but 0 to token; l→chol genuine prohibition 4 adj to class but 0 to token; boundary gap not discriminative) | 2 | B | -> [C628_fq_closer_positional_segregation.md](C628_fq_closer_positional_segregation.md) |
| **629** | **FQ_CLOSER Source Token Discrimination** (dy c9 restart rate 0% vs s 48.6%; forbidden sources lower hazard rate 28.2% vs 35.5%; higher EN_CHSH rate 13.1% vs 8.6%; JSD 0.219; class 23 contains restart specialists and general distributors) | 2 | B | -> [C629_fq_closer_source_discrimination.md](C629_fq_closer_source_discrimination.md) |
| **630** | **FQ_CLOSER Boundary Mechanism** (25% gap resolved: dy→aiin positional, l→chol frequency artifact P(0)=0.85, dy→chey likely genuine E=1.32; s→aiin 20x over-represented dominates restart loop; class 23 not unified mechanism) | 2 | B | -> [C630_fq_closer_boundary_mechanism.md](C630_fq_closer_boundary_mechanism.md) |
| **631** | **Intra-Class Clustering Census** (effective vocabulary 56 from 49 classes + 7 k=2 splits; 86% uniform; mean JSD 0.639 continuous not clustered; silhouette <0.25 in 34/36 classes; 480 types compress 8.6x) | 2 | B | -> [C631_intra_class_clustering_census.md](C631_intra_class_clustering_census.md) |
| **632** | **Morphological Subtype Prediction** (MIDDLE predicts clusters in 6/7 classes ARI=1.0; no significance at n=2-5; class 30 FL_HAZ morphologically opaque; PREFIX/ARTICULATOR zero power; MIDDLE-centric identity validated) | 2 | B | -> [C632_morphological_subtype_prediction.md](C632_morphological_subtype_prediction.md) |
| **633** | **Effective Vocabulary Census** (56 effective sub-types; FLOW_OPERATOR most diverse mean k=1.50; hazard 50% heterogeneous vs non-hazard 9% Fisher p=0.031; size inversely predicts k rho=-0.321 p=0.025; JSD continuous not discrete) | 2 | B | -> [C633_effective_vocabulary_census.md](C633_effective_vocabulary_census.md) |
| **634** | **Recovery Pathway Profiling** (0/13 KW tests significant; kernel absorption exit rate ~98-100% all REGIMEs; recovery path mean 3.76-4.78; post-kernel EN-dominated ~49-75%; recovery pathways NOT regime-stratified) | 2 | B | -> [C634_recovery_pathway_profiling.md](C634_recovery_pathway_profiling.md) |
| **635** | **Escape Strategy Decomposition** (0/9 per-folio KW significant; aggregate chi2 first-EN p=0.0003 but folio-level NS; JSD between REGIME fingerprints 0.031-0.082; escape strategies NOT regime-stratified) | 2 | B | -> [C635_escape_strategy_decomposition.md](C635_escape_strategy_decomposition.md) |
| **636** | **Recovery-Regime Interaction** (10/12 features FREE; 2/12 SUPPRESSOR: e_rate partial_p=0.0005 eta_sq=0.188, h_rate partial_p<0.0001 eta_sq=0.293; class composition masks kernel routing; recovery UNCONDITIONALLY FREE with latent e/h suppressor) | 2 | B | -> [C636_recovery_regime_interaction.md](C636_recovery_regime_interaction.md) |
| **637** | **B MIDDLE Sister Preference** (77 MIDDLEs, 22.9% of ch_preference variance from MIDDLE composition rho=0.479 p=0.000005; B less differentiated than A 0.140 vs 0.254; A-B cross-system rho=0.440 p=0.003; ok/ot near 50/50 less differentiated) | 2 | B | -> [C637_b_middle_sister_preference.md](C637_b_middle_sister_preference.md) |
| **638** | **Quire Sister Consistency** (quire KW H=32.002 p=0.0001 eta_sq=0.329; ICC(1,1)=0.362 FAIR; but CONFOUNDED with section Cramer's V=0.875; within section H quire NS p=0.665; section KW eta_sq=0.321 3.6x stronger than REGIME eta_sq=0.088) | 2 | B | -> [C638_quire_sister_consistency.md](C638_quire_sister_consistency.md) |
| **639** | **Sister Pair Variance Decomposition** (47.1% explained adj_R2=32.3%; 52.9% UNEXPLAINED free choice; shared variance 36.4% dominates; unique: quire 3.8%, lane balance 2.7%, MIDDLE 2.6%, REGIME 1.2%, section 0.4%; clean residuals no autocorrelation) | 2 | B | -> [C639_sister_pair_variance_decomposition.md](C639_sister_pair_variance_decomposition.md) |
| **640** | **PP Role Projection Architecture** (89/404 PP match B classes 22%; B has only 90 MIDDLEs from 480 types; B-Native 100% EN-dominant 8/8; AZC-Med AX 53.1% EN 40.7%; PP role dist differs from B shares chi2=42.37 p<0.0001; AX over-represented CC/FQ absent; frequency confound severe p<0.0001) | 2 | CROSS_SYSTEM | -> [C640_pp_role_projection_architecture.md](C640_pp_role_projection_architecture.md) |
| **641** | **PP Population Execution Profiles** (AZC-Med/B-Native differ: AX p=0.006, EN p=0.001; REGIME_2 p=0.0004, REGIME_3 p<0.0001; suffix diversity p<0.0001 frequency-confounded rho=0.795; EN subfamily partially independent of PREFIX rho=0.510; QO records smaller 5.5 vs 7.4, ANIMAL-enriched p=0.003) | 2 | CROSS_SYSTEM | -> [C641_pp_population_execution_profiles.md](C641_pp_population_execution_profiles.md) |
| **642** | **A Record Role & Material Architecture** (lattice 8.0% density 92% incompatibility; pair-level role heterogeneity at chance p=0.55; record-level role coverage below expected 1.91 vs 2.13 p=0.022; material consistency BELOW chance 0.6% vs 4.1% p=0.0006 active mixing; material-role NS V=0.122) | 2 | CROSS_SYSTEM | -> [C642_a_record_role_material_architecture.md](C642_a_record_role_material_architecture.md) |
| **643** | **Lane Hysteresis Oscillation** (EN alternation 0.563 vs null 0.494 p<0.0001; run lengths QO=1.46 CHSH=1.61 median 1.0; QO exits faster 60.0% vs CHSH 53.3%; section variation BIO=0.606 HERBAL_B=0.427; extends C549 within-line) | 2 | B | -> [C643_lane_hysteresis_oscillation.md](C643_lane_hysteresis_oscillation.md) |
| **644** | **QO Transition Stability** (QO mean stability=0.318 CHSH=0.278 p=0.0006 r=-0.039; entropy QO=4.08 CHSH=4.51; small effect; QO in more predictable contexts) | 2 | B | -> [C644_qo_transition_stability.md](C644_qo_transition_stability.md) |
| **645** | **CHSH Post-Hazard Dominance** (post-hazard EN: CHSH=75.2% QO=24.8%; QO enrichment 0.55x depleted; CHSH closer to hazard mean=3.81 vs 3.82 p=0.002 r=0.072; extends C601 continuous gradient) | 2 | B | -> [C645_chsh_post_hazard_dominance.md](C645_chsh_post_hazard_dominance.md) |
| **646** | **PP-Lane MIDDLE Discrimination** (20/99 PP MIDDLEs predict lane FDR<0.05 z=24.26; 15 QO 5 CHSH; QO=k/t ENERGY_OPERATOR 11/15; CHSH=o AUXILIARY 3/5; 17/20 EN-mediated caveat; 3 non-EN novel; no obligatory slots) | 2 | A/B | -> [C646_pp_lane_middle_discrimination.md](C646_pp_lane_middle_discrimination.md) |
| **647** | **Morphological Lane Signature** (QO k=70.7% CHSH e=68.7% V=0.654 p<0.0001; CC proximity shows no discrimination p=0.879; signature is MIDDLE-internal not positional; lanes built from different kernel-character vocabularies) | 2 | B | -> [C647_morphological_lane_signature.md](C647_morphological_lane_signature.md) |
| **648** | **LINK-Lane Independence** (QO 15.4% vs CHSH 14.7% LINK chi2=0.44 p=0.506 V=0.0095; excluding AX_FINAL 11.0% vs 11.1%; monitoring operates above lane identity) | 2 | B | -> [C648_link_lane_independence.md](C648_link_lane_independence.md) |
| **649** | **EN-Exclusive MIDDLE Deterministic Lane Partition** (22/30 exclusive MIDDLEs 100% lane-specific FDR<0.05; 13 QO-only k/t/p-initial 9 CHSH-only e/o-initial; absolute not probabilistic) | 2 | B | -> [C649_exclusive_middle_lane_partition.md](C649_exclusive_middle_lane_partition.md) |
| **650** | **Section-Driven EN Oscillation Rate** (section partial eta2=0.174 p=0.024 controlling REGIME; REGIME eta2=0.158 p=0.069 NS controlling section; BIO=0.593 HERBAL=0.457; material type drives oscillation) | 2 | B | -> [C650_section_driven_oscillation.md](C650_section_driven_oscillation.md) |
| **651** | **Fast Uniform Post-Hazard QO Recovery** (CHSH 75.2% first-EN post-hazard replicates C645; mean 0.77 CHSH before QO median=1.0; 45.1% immediate; no section/REGIME/class variation; unconditionally stable) | 2 | B | -> [C651_fast_post_hazard_recovery.md](C651_fast_post_hazard_recovery.md) |
| **652** | **PP Lane Character Asymmetry** (25.5% QO-predicting at type level p<3e-14; 31.3% token level; 3:1 CHSH bias in PP vocabulary; material class NS chi2=2.4 p=0.49) | 2 | GLOBAL | -> [C652_pp_lane_character_asymmetry.md](C652_pp_lane_character_asymmetry.md) |
| **653** | **AZC Lane Filtering Bias** (AZC-Med 19.7% QO vs B-Native 33.7% QO; OR=0.48 p=0.023; token-level OR=0.47 p<1e-17; pipeline suppresses QO vocabulary) | 2 | GLOBAL | -> [C653_azc_lane_filtering_bias.md](C653_azc_lane_filtering_bias.md) |
| **654** | **Non-EN PP Lane Independence** (partial r=0.028 p=0.80 controlling section+REGIME; tautological sensitivity r=0.645; lane is EN-internal not vocabulary-landscape; grammar compensates 2.2x) | 2 | B | -> [C654_non_en_pp_lane_independence.md](C654_non_en_pp_lane_independence.md) |
| **655** | **PP Lane Balance Redundancy** (incr R2=0.0005 F=0.058 p=0.81; AZC-Med incr=0.000 B-Native incr=0.004 both NS; A-record vs B-folio KS D=0.554 p<1e-10 divergent; section+REGIME fully account) | 2 | B | -> [C655_pp_lane_balance_redundancy.md](C655_pp_lane_balance_redundancy.md) |
| **656** | **PP Co-Occurrence Continuity** (max silhouette 0.016 across k=2..20; 76% zero-Jaccard; single connected component; within-Herbal sil=0.020; no discrete PP pools by co-occurrence) | 2 | A | -> [C656_pp_cooccurrence_continuity.md](C656_pp_cooccurrence_continuity.md) |
| **657** | **PP Behavioral Profile Continuity** (93 eligible PP; best sil=0.237 degenerate k=2: 2 vs 91; mean JSD=0.537; lane character ARI=0.010; no discrete behavioral clusters) | 2 | B | -> [C657_pp_behavioral_profile_continuity.md](C657_pp_behavioral_profile_continuity.md) |
| **658** | **PP Material Gradient** (36.2% entropy reduction as gradient not partition; NMI(pool,material)=0.129; chi2 p=0.002 V=0.392; pool 18 54% MIXED; all cross-axis NMI<0.15) | 2 | A | -> [C658_pp_material_gradient.md](C658_pp_material_gradient.md) |
| **659** | **PP Axis Independence** (co-occurrence vs behavior ARI=0.052; NMI material=0.129 pathway=0.032 lane=0.062 section=0.087; role eta2 mean=0.146; axes mutually independent; PP is high-dimensional continuous space) | 2 | A/B | -> [C659_pp_axis_independence.md](C659_pp_axis_independence.md) |
| **660** | **PREFIX x MIDDLE Selectivity Spectrum** (128 testable: 3.9% locked, 27.3% dominant, 22.7% bimodal, 46.1% promiscuous; QO 100% qo-locked; chi2=50.65 V=0.445; B wider than A Jaccard=0.484) | 2 | B | -> [C660_prefix_middle_selectivity_spectrum.md](C660_prefix_middle_selectivity_spectrum.md) |
| **661** | **PREFIX x MIDDLE Behavioral Interaction** (within-MIDDLE between-PREFIX JSD=0.425 vs between-MIDDLE JSD=0.436; effect ratio=0.975 computed / 0.792 vs C657; PREFIX transforms behavior; ckh JSD=0.710 max) | 2 | B | -> [C661_prefix_middle_behavioral_interaction.md](C661_prefix_middle_behavioral_interaction.md) |
| **662** | **PREFIX Role Reclassification** (mean 75% class reduction median 82%; EN PREFIX->EN class 94.1%; AX PREFIX->AX/FQ 70.8%; 50.4% of pairs reduce to <20% of MIDDLE's classes) | 2 | B | -> [C662_prefix_role_reclassification.md](C662_prefix_role_reclassification.md) |
| **663** | **Effective PREFIX x MIDDLE Inventory** (1190 observed, 501 effective pairs, 1.24x expansion; best sil=0.350 k=2 vs C657 0.237; k=3 degenerate; binary EN/non-EN split) | 2 | B | -> [C663_effective_prefix_middle_inventory.md](C663_effective_prefix_middle_inventory.md) |
| **664** | **Role Profile Trajectory** (AX increases late rho=+0.082 p<0.001 Q1=15.4% Q4=18.1%; EN marginal decline; CC/FL/FQ flat; EN slope regime-dependent KW p=0.038; folio trajectory clustering k=2 sil=0.451 two outliers) | 2 | B | -> [C664_role_profile_trajectory.md](C664_role_profile_trajectory.md) |
| **665** | **LINK Density Trajectory** (stationary within folios rho=+0.020 p=0.333 KW p=0.559; folio-scale stationarity independent of C365 line-level claim refuted by C805; REGIME_3 steepest +0.051 but NS) | 2 | B | -> [C665_link_density_trajectory.md](C665_link_density_trajectory.md) |
| **666** | **Kernel Contact Trajectory** (k/h/e all stationary within folios; e dominates ~29% flat; k rare ~0.2% flat; k/e ratio flat rho=-0.023 p=0.29; extends C458 between-folio clamping to within-folio) | 2 | B | -> [C666_kernel_contact_trajectory.md](C666_kernel_contact_trajectory.md) |
| **667** | **Escape/Hazard Density Trajectory** (hazard density flat rho=+0.009 p=0.650; 0 forbidden events in corpus; escape density flat; Q4 escape efficiency drops 0.579 vs 0.636; REGIME_2/3 late hazard increase) | 2 | B | -> [C667_escape_hazard_trajectory.md](C667_escape_hazard_trajectory.md) |
| **668** | **Lane Balance Trajectory** (QO fraction declines rho=-0.058 p=0.006 Q1=46.3% Q4=41.3%; REGIME_2 strongest -9.9pp; REGIME_4 flat +1.4pp; CHSH-ward drift = energy-to-stabilization shift) | 2 | B | -> [C668_lane_balance_trajectory.md](C668_lane_balance_trajectory.md) |
| **669** | **Hazard Proximity Trajectory** (mean distance-to-hazard tightens rho=-0.104 p<0.001 Q1=2.75 Q4=2.45; QO tightens rho=-0.082 p=0.003 CHSH static; REGIME_2 strongest -0.602; REGIME_4 flat -0.051) | 2 | B | -> [C669_hazard_proximity_trajectory.md](C669_hazard_proximity_trajectory.md) |
| **670** | **Adjacent-Line Vocabulary Coupling** (no coupling; Jaccard obs=0.140 perm=0.126 diff=+0.014; 0/79 folios sig; MIDDLEs selected independently per line) | 0 | B | -> [C670_adjacent_line_vocabulary_coupling.md](C670_adjacent_line_vocabulary_coupling.md) |
| **671** | **MIDDLE Novelty Shape** (front-loaded; 87.3% FL 0% BL; first-half frac=0.685 vs perm=0.653; vocabulary introduced early, reused late) | 0 | B | -> [C671_middle_novelty_shape.md](C671_middle_novelty_shape.md) |
| **672** | **Cross-Line Boundary Grammar** (grammar-transparent; H_boundary=4.284 H_within=4.628 ratio=0.926; chi2 p=0.187 not sig non-independent; 7.4% entropy reduction at boundaries) | 0 | B | -> [C672_cross_line_boundary_grammar.md](C672_cross_line_boundary_grammar.md) |
| **673** | **CC Trigger Sequential Independence** (no memory; self-transition 0.390 vs perm 0.395 p=1.0; CC trigger re-selected each line independently) | 0 | B | -> [C673_cc_trigger_sequential_independence.md](C673_cc_trigger_sequential_independence.md) |
| **674** | **EN Lane Balance Autocorrelation** (folio-driven; raw lag-1 rho=0.167 p<1e-6 but perm p=1.0; lag-2/3 stronger than lag-1; autocorrelation entirely explained by folio identity) | 0 | B | -> [C674_en_lane_balance_autocorrelation.md](C674_en_lane_balance_autocorrelation.md) |
| **675** | **MIDDLE Vocabulary Trajectory** (minimal drift; JSD Q1-Q4=0.081 ratio=1.078; 4/135 MIDDLEs positionally biased after Bonferroni; token identity position-invariant) | 0 | B | -> [C675_middle_vocabulary_trajectory.md](C675_middle_vocabulary_trajectory.md) |
| **676** | **Morphological Parameterization Trajectory** (PREFIX chi2 p=3.7e-9 suffix p=1.7e-7; qo PREFIX rho=-0.085 bare suffix rho=+0.095; morphological simplification late) | 0 | B | -> [C676_morphological_parameterization_trajectory.md](C676_morphological_parameterization_trajectory.md) |
| **677** | **Line Complexity Trajectory** (unique tokens rho=-0.196 p<1e-21; unique MIDDLEs rho=-0.174; mean token len rho=-0.093; TTR flat 0.962; lines shorten late, equally diverse per token) | 0 | B | -> [C677_line_complexity_trajectory.md](C677_line_complexity_trajectory.md) |
| **678** | **Line Profile Classification** (continuous; best KMeans sil=0.100 no discrete types; PC1=morphological complexity 12.1%; PC2=monitoring intensity 9.3%; 10 PCs for 68.3%) | 0 | B | -> [C678_line_profile_classification.md](C678_line_profile_classification.md) |
| **679** | **Line Type Sequencing** (weak coupling; adjacent cosine sim=0.675 vs random=0.641 diff=+0.031 p<0.001; 3.1% similarity elevation for consecutive lines) | 0 | B | -> [C679_line_type_sequencing.md](C679_line_type_sequencing.md) |
| **680** | **Positional Feature Prediction** (11/27 features position-correlated; 9/27 add beyond REGIME; line_length dR2=0.040 strongest; 16/27 position-independent) | 0 | B | -> [C680_positional_feature_prediction.md](C680_positional_feature_prediction.md) |
| **681** | **Sequential Coupling Verdict** (24/27 features lag-1 sig; SEQUENTIALLY_COUPLED but folio-mediated not sequential; top: line_length dR2=0.098 EN dR2=0.091 LINK dR2=0.063; lines = contextually-coupled independently-assessed) | 0 | B | -> [C681_sequential_coupling_verdict.md](C681_sequential_coupling_verdict.md) |
| **682** | **Survivor Distribution Profile** (mean 11.08/49 classes survive per A record; median=10 std=5.79; 1.2% zero-class; token survival mean=38.5/4889; right-skewed distribution) | 2 | A-B | -> [C682_survivor_distribution_profile.md](C682_survivor_distribution_profile.md) |
| **683** | **Role Composition Under Filtering** (FL most depleted 60.9%; CC 44.6%; FQ most resilient 12.5%; role entropy mean=1.611/2.322; asymmetric depletion hierarchy) | 2 | A-B | -> [C683_role_composition_under_filtering.md](C683_role_composition_under_filtering.md) |
| **684** | **Hazard Pruning Under Filtering** (83.9% full elimination of all 17 forbidden transitions; mean 0.21 active; max 5; filtering = natural hazard suppression) | 2 | A-B | -> [C684_hazard_pruning_under_filtering.md](C684_hazard_pruning_under_filtering.md) |
| **685** | **LINK and Kernel Survival Rates** (97.4% kernel union access h=95.5% k=81.0% e=60.7%; 36.5% lose all LINK tokens; monitoring capacity fragile) | 2 | A-B | -> [C685_link_kernel_survival_rates.md](C685_link_kernel_survival_rates.md) |
| **686** | **Role Vulnerability Gradient** (FL most fragile 2.3% at 0-2 PP; FQ most resilient 13.5%; vulnerability ordering FL>EN>AX>CC>FQ; all roles >0% in all PP bins) | 2 | A-B | -> [C686_role_vulnerability_gradient.md](C686_role_vulnerability_gradient.md) |
| **687** | **Composition-Filtering Interaction** (PURE_RI mean=0.44 classes near-zero; MIXED=PURE_PP p=0.997; only 9 PURE_RI records; composition binary divide PP vs RI) | 2 | A-B | -> [C687_composition_filtering_interaction.md](C687_composition_filtering_interaction.md) |
| **688** | **REGIME Filtering Robustness** (REGIME_2 most robust 0.222; REGIME_3 least 0.167; REGIMEs 1/2/4 clustered ~0.21; filtering severity A-record-driven not REGIME-driven) | 2 | A-B | -> [C688_regime_filtering_robustness.md](C688_regime_filtering_robustness.md) |
| **689** | **Survivor Set Uniqueness** (1525/1562 unique class sets = 97.6%; Jaccard mean=0.199; each A record = near-unique filter fingerprint) | 2 | A-B | -> [C689_survivor_set_uniqueness.md](C689_survivor_set_uniqueness.md) |
| **690** | **Line-Level Legality Distribution** (25/32 pairings >50% empty lines; median record makes 74-100% empty; no positional effect rho=0.005 p=0.87; max-classes = 7-27% empty) | 2 | A-B | -> [C690_line_level_legality_distribution.md](C690_line_level_legality_distribution.md) |
| **691** | **Program Coherence Under Filtering** (0-20% operational completeness; work group survives best up to 87%; close group is bottleneck; max gap = entire folio for most records) | 2 | A-B | -> [C691_program_coherence_under_filtering.md](C691_program_coherence_under_filtering.md) |
| **692** | **Filtering Failure Mode Distribution** (94.7% MIDDLE miss, 3.6% PREFIX, 1.7% SUFFIX; consistent across all roles 91-97% MIDDLE; MIDDLE = gatekeeper) | 2 | A-B | -> [C692_filtering_failure_mode_distribution.md](C692_filtering_failure_mode_distribution.md) |
| **693** | **Usability Gradient** (266x dynamic range; best=0.107 Max-classes; 78% pairings unusable >50% empty; single A record does NOT produce usable B program) | 2 | A-B | -> [C693_usability_gradient.md](C693_usability_gradient.md) |
| **694** | **RI Placement Non-Random** (Fisher combined KS p ~ 10^-306; inter-RI gaps deviate from geometric; Wald-Wolfowitz runs test p=0.78 ns) | 2 | A | |
| **695** | **PP-Run Length Distribution** (KS p ~ 10^-44; PP-pure runs non-geometric; 365 bundles, sizes 1-12, mean 2.71) | 2 | A | |
| **696** | **RI Line-Final Preference** (1.48x enrichment, p=1.26e-07; threshold artifact from strict RI definition vs C498's 1.76x) | 2 | A | |
| **697** | **PREFIX Clustering Within Lines** (observed entropy < shuffled, p < 10^-4; PREFIXes cluster within A lines) | 2 | A | |
| **698** | **Bundle-C424 Size Match** (INFORMATIONAL; bundles and C424 adjacency clusters are distinct constructs; KS p < 0.001) | 2 | A | |
| **699** | **Within-Bundle PP Coherence** (FALSIFIED; within=0.0973, between=0.0962, ratio 1.01x; no vocabulary coherence in bundles) | 1 | A | |
| **700** | **Bundle PP Exceeds Random** (MARGINAL; 1.02x effect, Fisher p < 10^-157 but median per-bundle p=0.512) | 2 | A | |
| **701** | **Bundle PP Diversity** (FALSIFIED; observed=0.7387 vs shuffled=0.7438, p=0.336; no structured diversity) | 1 | A | |
| **702** | **Boundary Vocabulary Discontinuity** (FALSIFIED; interior/boundary ratio 1.06x, p=0.207; no vocabulary cliff at RI boundaries) | 1 | A | |
| **703** | **PP Folio-Level Homogeneity** (PP MIDDLEs distribute uniformly within A folios; within-bundle = between-bundle Jaccard; RI = structural not vocabular) | 2 | A | -> [C703_pp_folio_level_homogeneity.md](C703_pp_folio_level_homogeneity.md) |
| **704** | **Folio PP Pool Size** (mean 35.3 MIDDLEs per folio, 7.0x record-level; range 20-88; folio = complete PP specification) | 2 | A | |
| **705** | **Folio-Level Class Survival** (mean 39.8/49 classes = 81.2%; 3.6x improvement over record-level 11.08/49; min 30/49) | 2 | A-B | -> [C705_folio_level_class_survival.md](C705_folio_level_class_survival.md) |
| **706** | **B Line Viability Under Folio Filtering** (13.7% empty lines vs 78% record-level; 76.3% pairings have <=20% empty) | 2 | A-B | |
| **707** | **Folio Usability Dynamic Range** (14.3x range vs 266x record-level; best=0.343 vs 0.107; worst nonzero=0.024) | 2 | A-B | |
| **708** | **Inter-Folio PP Discrimination** (PP Jaccard=0.274 discriminative; CLASS Jaccard=0.830 convergent; funnel topology) | 2 | A-B | -> [C708_inter_folio_pp_discrimination.md](C708_inter_folio_pp_discrimination.md) |
| **709** | **Section Invariance** (all sections H/P/T 100% viable; P=0.182, T=0.293 higher than H=0.085; no dead zones) | 2 | A-B | |

### RI Functional Identity (C710-C716) — Phase: RI_FUNCTIONAL_IDENTITY

| # | Constraint | Tier | Scope | Detail |
|---|------------|------|-------|--------|
| **710** | **RI-PP Positional Complementarity** (d=0.12, RI slightly later in lines; effect too small for structural complementarity) | 2 | A | |
| **711** | **RI Vocabulary Density** (rho=0.419 with folio size, below PP's 0.588; mean 6.6 RI types/folio vs 35.3 PP; RI is sparse) | 2 | A | |
| **712** | **RI Singleton-Repeater Behavioral Equivalence** (KS p=0.16; singletons and repeaters show same positional/final-rate behavior) | 2 | A | |
| **713** | **Adjacent Line RI Similarity** (ratio 2.25x but absolute Jaccard 0.008 near zero; no meaningful RI sharing between adjacent lines) | 2 | A | |
| **714** | **Line-Final RI Morphological Profile** (143 unique types in 156 final positions; no morphological difference from non-final RI) | 2 | A | |
| **715** | **RI-PP Independence** (rho=-0.052; RI diversity 0.74 within PP groups; RI content independent of PP context) | 2 | A | |
| **716** | **Cross-Folio RI Reuse Independence** (75 RI on 2+ folios; PP Jaccard ratio 1.045; reuse independent of PP context) | 2 | A | |

### PP Line-Type Homogeneity (C717-C718) — Phase: RI_FUNCTIONAL_IDENTITY

| # | Constraint | Tier | Scope | Detail |
|---|------------|------|-------|--------|
| **717** | **PP Homogeneity Across Line Types** (PP-pure and RI-bearing lines draw from same PP pool; RI-exclusive PP is sampling artifact, null=9.4 vs obs=8.9, 106% explained; PP-pure alone recovers 90.1% of B class survival) | 2 | A | |
| **718** | **RI Pipeline Invisibility** (3.9 "RI-gated" B classes per folio are random; zero classes gated in >25% of folios; RI structurally invisible to A-to-B execution pipeline) | 2 | A-B | |

### RI Binding Analysis (C719-C721) — Phase: RI_BINDING_ANALYSIS

| # | Constraint | Tier | Scope | Detail |
|---|------------|------|-------|--------|
| **719** | **RI-PP Functional Independence** (0/6 binding tests pass; shared RI does not predict PP similarity J=0.074 vs 0.065, PP consistency ratio 1.05, adjacent PP ratio 0.99; RI and PP are orthogonal discrimination axes) | 2 | A | |
| **720** | **RI Gallows Independence** (shared RI does not predict gallows domain; cosine 0.244 vs 0.244, ratio 0.998; within-record gallows enrichment C530 is folio-level not RI-mediated) | 2 | A | |
| **721** | **RI Section Sharing Trivial** (76.6% within-section vs 71.5% expected from section sizes; enrichment 1.07x trivially explained by 95/114 folios being Herbal) | 2 | A | |

### B Legality Gradient (C722-C727) — Phase: B_LEGALITY_GRADIENT

| # | Constraint | Tier | Scope | Detail |
|---|------------|------|-------|--------|
| **722** | **Within-Line Accessibility Arch** (B token accessibility follows nonlinear arch by within-line position; initial 0.279, medial 0.306, final 0.282; KW H=74.4, p=2.67e-15; mirrors C556 SETUP-WORK-CLOSE via morphological composition) | 2 | A-B | -> [C722_within_line_accessibility_arch.md](C722_within_line_accessibility_arch.md) |
| **723** | **Role Accessibility Hierarchy** (FQ 0.582 > EN 0.382 > AX 0.321 > CC 0.261 > FL 0.085; KW p=2.4e-10; FL and CC are near-exclusively B-internal grammar infrastructure) | 2 | A-B | -> [C723_role_accessibility_hierarchy.md](C723_role_accessibility_hierarchy.md) |
| **724** | **Within-Class Suffix Accessibility Gradient** (up to 19x accessibility variation within same class from SUFFIX alone; Class 33: qokaiin=0.675 vs qokeedy=0.035; confirms C502.a three-axis filtering at individual token resolution) | 2 | A-B | -> [C724_within_class_suffix_accessibility.md](C724_within_class_suffix_accessibility.md) |
| **725** | **Across-Line Accessibility Gradient** (later B folio lines have higher accessibility; rho=0.124, p=8.6e-10; 56/82 folios positive; first-third 0.276, last-third 0.306; consistent with C325 completion gradient) | 2 | B | -> [C725_across_line_accessibility_gradient.md](C725_across_line_accessibility_gradient.md) |
| **726** | **Role-Position Accessibility Interaction** (aggregate arch decomposes into role-specific trajectories; CC/AX increase toward final, EN/FQ decrease; non-unanimous but morphologically explained by C590/C564 composition effects) | 2 | A-B | -> [C726_role_position_accessibility_interaction.md](C726_role_position_accessibility_interaction.md) |
| **727** | **B Vocabulary Autonomy Rate** (69.3% of B token types have low-or-zero accessibility from A; 34.4% completely B-exclusive; 0% universally legal; B's structural scaffold is autonomously determined) | 2 | A-B | -> [C727_b_vocabulary_autonomy_rate.md](C727_b_vocabulary_autonomy_rate.md) |

### PP Line-Level Structure (C728-C732) — Phase: PP_LINE_LEVEL_STRUCTURE

| # | Constraint | Tier | Scope | Detail |
|---|------------|------|-------|--------|
| **728** | **PP Co-occurrence Incompatibility Compliance** (PP MIDDLE co-occurrence is non-random: 5,460 vs 5,669 null unique pairs, p<0.001; fully explained by MIDDLE incompatibility C475; 0 avoidance violations; legal-pair variance below null; lines are compatibility-valid subsets) | 2 | A | -> [C728_pp_cooccurrence_incompatibility_compliance.md](C728_pp_cooccurrence_incompatibility_compliance.md) |
| **729** | **C475 Record-Level Scope** (MIDDLE incompatibility operates perfectly at A record level; 0 violations across 19,576 pair occurrences; 15,518 within-folio avoidance pairs never appear on same line; extends C475 from AZC to A) | 2 | A | -> [C729_c475_record_level_scope.md](C729_c475_record_level_scope.md) |
| **730** | **PP PREFIX-MIDDLE Within-Line Coupling** (cross-token PREFIX-MIDDLE MI 0.133 vs null 0.121, p<0.001; MI ratio 2.79x between-line; may be mediated by C475 incompatibility) | 2 | A | -> [C730_pp_prefix_middle_line_coupling.md](C730_pp_prefix_middle_line_coupling.md) |
| **731** | **PP Adjacent Line Continuity** (adjacent lines share more PP MIDDLEs; Jaccard 0.102 vs 0.092 non-adjacent, ratio 1.10x, p=0.001; soft local sequential continuity) | 2 | A | -> [C731_pp_adjacent_line_continuity.md](C731_pp_adjacent_line_continuity.md) |
| **732** | **PP Within-Line Selection Uniformity** (no SUFFIX coherence 1.02x, no diversity anomaly effect=0.13, no folio position trajectory p=0.633; PP selection is uniform beyond incompatibility across SUFFIX/diversity/position dimensions) | 2 | A | -> [C732_pp_within_line_selection_uniformity.md](C732_pp_within_line_selection_uniformity.md) |
| **733** | **PP Token Variant Line Structure** (whole-token co-occurrence is non-random beyond MIDDLE assignment; variant shuffle p<0.001 for both unique pairs and variance; ~38% of word-level structure from PREFIX+SUFFIX coordination; reverses MIDDLE-level uniformity finding) | 2 | A | -> [C733_pp_token_variant_line_structure.md](C733_pp_token_variant_line_structure.md) |

### A-B Folio Specificity (C734-C739, C751-C752) — Phase: A_B_FOLIO_SPECIFICITY

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| **734** | **A-B Coverage Architecture** (per-A-folio C502.a coverage of B folios: mean 26.1%, range 2.6-79.3%; A folio identity explains 72.0% of variance, B folio 18.1%; routing architecture, not flat) | 2 | A<>B | -> [C734_ab_coverage_architecture.md](C734_ab_coverage_architecture.md) |
| **735** | **Pool Size Coverage Dominance** (A folio PP pool size predicts B coverage: Spearman rho=0.85, p=5e-33; pool range 20-88 MIDDLEs; relationship primarily quantitative) | 2 | A<>B | -> [C735_pool_size_coverage_dominance.md](C735_pool_size_coverage_dominance.md) |
| **736** | **B Vocabulary Accessibility Partition** (0 B tokens universally legal; 34.4% never legal under any A folio; median accessibility 3 A folios; tripartite: B-exclusive 34.4%, narrow-access 33.9%, broad-access 31.7%) | 2 | A<>B | -> [C736_b_vocabulary_accessibility_partition.md](C736_b_vocabulary_accessibility_partition.md) |
| **737** | **A-Folio Cluster Structure** (A folios cluster into ~6 groups by B-coverage profile; mean pairwise correlation 0.648; specificity ratio 1.544x null; dominant standard cluster n=62 plus 5 specialized groups) | 2 | A<>B | -> [C737_a_folio_cluster_structure.md](C737_a_folio_cluster_structure.md) |
| **738** | **Union Coverage Ceiling** (all 114 A folios combined reach ~83-89% B folio coverage, never 95%; 34.4% of B vocabulary permanently B-exclusive; represents B's autonomous grammar) | 2 | A<>B | -> [C738_union_coverage_ceiling.md](C738_union_coverage_ceiling.md) |
| **739** | **Best-Match Specificity** (every B folio has a strongly preferred A folio: all 82 show lift >1.5x, mean 2.43x, mean z=3.77; routing is directional: B folios are consumers, A folios are providers) | 2 | A<>B | -> [C739_best_match_specificity.md](C739_best_match_specificity.md) |
| **751** | **Coverage Pool-Size Confound** (raw best-match degenerate: 2 A folios serve all 82 B; coverage~pool r=0.883; folio length->pool r=0.584; residual reveals 24 distinct A folios with content specificity) | 2 | A<>B | -> [C751_coverage_pool_size_confound.md](C751_coverage_pool_size_confound.md) |
| **752** | **No Section-to-Section Routing** (permutation test: 27/82 same-section = null 26.7, z=0.08, p=0.57; section labels are physical organization, not routing addresses; routing is vocabulary-driven) | 2 | A<>B | -> [C752_no_section_routing.md](C752_no_section_routing.md) |
| **792** | **B-Exclusive = HT Identity** (100% of B-exclusive vocabulary is HT/UN; 0 classified tokens are B-exclusive; all 88 classified MIDDLEs are in PP; C736's "autonomous grammar" is HT layer, not classified) | 2 | A<>B/HT | -> [C792_b_exclusive_ht_identity.md](C792_b_exclusive_ht_identity.md) |
| **793** | **Residual Specificity = Vocabulary Coincidence** (the 24 residual-best A folios are those with best sample of common PP MIDDLEs; f42r dominates via 8 near-universal MIDDLEs; no content routing) | 2 | A<>B | -> [C793_residual_specificity_is_vocabulary_coincidence.md](C793_residual_specificity_is_vocabulary_coincidence.md) |

### HT Reconciliation (C740-C746) — Phase: HT_RECONCILIATION

> **Summary:** HT = UN (zero-delta identity, C740). HT tokens comply with C475 at classified-baseline rates (0.69% vs 0.63%, C742) but only 4.6% of HT MIDDLE types participate in the incompatibility graph (C741). Lane distribution is radically different from classified (p=4e-60, C743) but lane transitions are neutral (C744). Removing HT inflates coverage metrics but preserves routing architecture (r=0.85, C745). HT density is non-uniform across folios and anti-correlated with coverage (r=-0.376, C746). **C404-C405 (non-operational) confirmed.**

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| **740** | **HT/UN Population Identity** (HT = UN: 4,421 types, 7,042 occ, zero delta; both defined by exclusion from 479-type grammar) | 2 | B/HT | -> [C740_ht_un_population_identity.md](C740_ht_un_population_identity.md) |
| **741** | **HT C475 Minimal Graph Participation** (4.6% of HT MIDDLE types in C475 graph, but 38.5% of occurrences; 95.4% too rare to test) | 2 | B/HT | -> [C741_ht_c475_minimal_participation.md](C741_ht_c475_minimal_participation.md) |
| **742** | **HT C475 Line-Level Compliance** (0.69% violation rate vs 0.63% classified baseline; z=+1.74 marginal; compliance by structural sparsity) | 2 | B/HT | -> [C742_ht_c475_compliance.md](C742_ht_c475_compliance.md) |
| **743** | **HT Lane Segregation** (chi2=278.71, p=4e-60; OTHER +9.5pp, QO -7.7pp; HT skews toward non-standard prefixes) | 2 | B/HT | -> [C743_ht_lane_segregation.md](C743_ht_lane_segregation.md) |
| **744** | **HT Lane Indifference** (same-lane rate 37.7% = expected 37.9%, lift=0.994x; z=-1.66 ns; HT is lane-neutral in placement) | 2 | B/HT | -> [C744_ht_lane_indifference.md](C744_ht_lane_indifference.md) |
| **745** | **HT Coverage Metric Sensitivity** (coverage 31%->43% on HT removal; routing preserved r=0.85; metric artifact, not operational) | 2 | A<>B/HT | -> [C745_ht_coverage_metric_sensitivity.md](C745_ht_coverage_metric_sensitivity.md) |
| **746** | **HT Folio Compensatory Distribution** (density 15.5-47.2%, chi2=429.72; anti-correlated with coverage r=-0.376, p=0.0005) | 2 | B/HT | -> [C746_ht_folio_compensatory_distribution.md](C746_ht_folio_compensatory_distribution.md) |

### B Line-Position HT Structure (C747-C750, C794-C795) — Phase: B_LINE_POSITION_HT

> **Summary:** Opening lines of B folios are massively enriched in HT tokens (50.2% vs 29.8%, d=0.99, C747). The enrichment is a sharp step function confined to line position 1 (C748). First-line HT tokens are morphologically distinct from working-line HT (95.9% unique types, pch-prefix elevated, chi2=496, C749). The effect is opening-only — last lines are indistinguishable from interior (p=0.50, C750). B folio-programs have a one-line non-operational header. **Extension:** Line-1 HT is a composite header with two parts: PP component (68.3%) declaring A-folio context at 15.8x random prediction (C794-C795), and B-exclusive component (31.7%) serving as folio identification (94.1% folio-unique).

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| **747** | **Line-1 HT Enrichment** (50.2% HT vs 29.8% rest, +20.3pp, d=0.99, p<10^-6; 69/82 folios positive; permutation z=11.07) | 0 | B/HT | -> [C747_line1_ht_enrichment.md](C747_line1_ht_enrichment.md) |
| **748** | **Line-1 Step Function** (pos 1=50.2%, pos 2=31.7%, pos 3-10=27-33%; enrichment confined to single opening line) | 0 | B/HT | -> [C748_line1_step_function.md](C748_line1_step_function.md) |
| **749** | **First-Line HT Morphological Distinction** (95.9% unique types vs 62.8% working; pch prefix 7.0% vs 1.9%; articulator 13.0% vs 9.9%; chi2=496.37) | 2 | B/HT | -> [C749_line1_ht_morphological_distinction.md](C749_line1_ht_morphological_distinction.md) |
| **750** | **Opening-Only HT Asymmetry** (last line 30.8% HT = interior 29.8%, p=0.50; no closing HT enrichment) | 0 | B/HT | -> [C750_opening_only_asymmetry.md](C750_opening_only_asymmetry.md) |
| **794** | **Line-1 Composite Header Structure** (68.3% PP for A-context declaration, 31.7% B-exclusive for folio ID; PP predicts A at 15.8x random; B-exclusive 94.1% folio-unique) | 2 | B/A<>B | -> [C794_line1_composite_header.md](C794_line1_composite_header.md) |
| **795** | **Line-1 A-Context Prediction** (PP line-1 HT predicts best-match A folio: 13.9% correct vs 0.88% random baseline, lift=15.8x) | 2 | A<>B | -> [C795_line1_a_context_prediction.md](C795_line1_a_context_prediction.md) |

### B Paragraph Structure (C840-C845) — Phase: B_PARAGRAPH_STRUCTURE

> **Summary:** B paragraphs function as mini-programs within folios (C840). Each has a one-line header zone with +15.8pp HT enrichment over body (44.9% vs 29.1%), mirroring the folio-level pattern. 71.5% of paragraphs are gallows-initiated (C841), matching A paragraph structure. HT drops sharply at line 2 and stabilizes (C842) - same step function as folios. Prefixes pch- and po- (33.5% combined, 78-86% HT) serve as paragraph identification markers (C843). Folio line 1's elevated HT (50.2%) results from double-header overlap (C844). Unlike A's RI linkers, B paragraphs do NOT link to each other - they are self-contained (C845).

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| **840** | **B Paragraph Mini-Program Structure** (line 1: 44.9% HT vs body 29.1%, +15.8pp, d=0.72, p<10^-20; 76% of paragraphs show enrichment) | 2 | B | -> [C840_b_paragraph_mini_program_structure.md](C840_b_paragraph_mini_program_structure.md) |
| **841** | **B Paragraph Gallows-Initial Markers** (71.5% p/t/k/f initial; p=43.6%, t=19.3%, k=5.5%, f=3.1%; matches A paragraph structure) | 2 | B | -> [C841_b_paragraph_gallows_initial.md](C841_b_paragraph_gallows_initial.md) |
| **842** | **B Paragraph HT Step Function** (pos 1=45.2%, pos 2=26.5%, pos 3-5+=26-27%; -18.7pp drop at line 2; body flat) | 2 | B | -> [C842_b_paragraph_step_function.md](C842_b_paragraph_step_function.md) |
| **843** | **B Paragraph Prefix Markers** (pch- 16.9% + po- 16.6% = 33.5% of initiators; 78-86% HT; paragraph identification vocabulary) | 2 | B | -> [C843_b_paragraph_prefix_markers.md](C843_b_paragraph_prefix_markers.md) |
| **844** | **Folio Line 1 Double-Header** (50.2% HT = folio header + paragraph 1 header overlap; mid-folio paragraphs 43.6% HT) | 2 | B | -> [C844_folio_line1_double_header.md](C844_folio_line1_double_header.md) |
| **845** | **B Paragraph Self-Containment** (no inter-paragraph linking; 7.1% both-position rate vs A's 0.6%; no ct-ho signature; symmetric topology) | 2 | B | -> [C845_b_paragraph_self_containment.md](C845_b_paragraph_self_containment.md) |

### A-B Paragraph Correspondence (C846) — Phase: A_B_PARAGRAPH_CORRESPONDENCE

> **Summary:** No specific paragraph-to-paragraph correspondence between A and B. The A→B relationship is POOL-BASED, not ADDRESS-BASED. Only 39 unique A paragraphs serve as "best match" for 568 B paragraphs, with top 10 capturing 85.9%. Pool size dominates (rho=0.694). Raw lift 2.49x drops to 1.20x when controlling for pool size. Confirms C384, C502, C735 at paragraph granularity.

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| **846** | **A-B Paragraph Pool Relationship** (no specific A→B pairing; 39 A paragraphs serve 568 B; pool-size rho=0.694; raw lift 2.49x → 1.20x controlled; relationship is pool-based not address-based) | 2 | A<>B | -> [C846_ab_paragraph_pool_relationship.md](C846_ab_paragraph_pool_relationship.md) |

### Paragraph Internal Profiling (C847-C854) — Phase: PARAGRAPH_INTERNAL_PROFILING

> **Summary:** Both A and B paragraphs show parallel header-body architecture: line 1 enriched with marker vocabulary (A: RI 3.84x; B: HT +0.134 delta), body with operational vocabulary. Line counts are statistically indistinguishable (A: 4.8, B: 4.37, p=0.067). Both systems cluster into 5 natural paragraph types. Section P (A) has 2x higher RI/PP than H. Section RECIPE (B) dominates EN (44.5%), PHARMA dominates FQ (43.2%).

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| **847** | **A Paragraph Size Distribution** (mean 4.8 lines; "only" position = 11.79 lines; Cohen's d = 0.110 vs B) | 2 | A | -> [C847_a_paragraph_size_distribution.md](C847_a_paragraph_size_distribution.md) |
| **848** | **A Paragraph RI Position Variance** (middle 14.3% RI vs first 9.3%; Kruskal-Wallis p=0.001; RI line-1 concentration 3.84x) | 2 | A | -> [C848_a_paragraph_ri_position_variance.md](C848_a_paragraph_ri_position_variance.md) |
| **849** | **A Paragraph Section Profile** (P section: 17.2% RI, 67.5% PP vs H: 8.4% RI, 42% PP; p=0.0006) | 2 | A | -> [C849_a_paragraph_section_profile.md](C849_a_paragraph_section_profile.md) |
| **850** | **A Paragraph Cluster Taxonomy** (5 clusters: short-RI 34%, long-linker 8%, standard 58%; silhouette=0.337) | 2 | A | -> [C850_a_paragraph_cluster_taxonomy.md](C850_a_paragraph_cluster_taxonomy.md) |
| **851** | **B Paragraph HT Variance Validation** (delta +0.134; 76.8% positive; line 1 = 46.5% HT; validates C840) | 2 | B | -> [C851_b_paragraph_ht_variance_validation.md](C851_b_paragraph_ht_variance_validation.md) |
| **852** | **B Paragraph Section-Role Interaction** (RECIPE 44.5% EN; PHARMA 43.2% FQ; Kruskal-Wallis p<0.0001) | 2 | B | -> [C852_b_paragraph_section_role_interaction.md](C852_b_paragraph_section_role_interaction.md) |
| **853** | **B Paragraph Cluster Taxonomy** (5 clusters: single-line 9%, long-EN 10%, standard 81%; silhouette=0.237) | 2 | B | -> [C853_b_paragraph_cluster_taxonomy.md](C853_b_paragraph_cluster_taxonomy.md) |
| **854** | **A-B Paragraph Structural Parallel** (both header-body; line counts indistinguishable p=0.067; both k=5 clusters) | 2 | A<>B | -> [C854_ab_paragraph_structural_parallel.md](C854_ab_paragraph_structural_parallel.md) |

### AZC Reassessment (C753-C756) — Phase: AZC_REASSESSMENT

> **Summary:** A→B "routing" is reframed as **constraint propagation**, not content targeting. A folios are deliberately homogeneous (11x more similar than random, C756) to maximize vocabulary coverage, not discriminate B programs. Filtering is real and role-aware (CORE_CONTROL 95%+ survival, C754), but operates via vocabulary restriction, not content routing. The first 10 A folios cover 60% of all PP vocabulary.

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| **753** | **No Content-Specific A-B Routing** (partial r=-0.038 after size control; no granularity achieves discrimination; reframe as constraint propagation) | 2 | A<>B | -> [C753_no_content_routing.md](C753_no_content_routing.md) |
| **754** | **Role-Aware Infrastructure Filtering** (CORE_CONTROL 95%+ survival regardless of pool size; AUXILIARY 20% under small pools; McNemar p<0.0001) | 2 | A<>B | -> [C754_role_aware_filtering.md](C754_role_aware_filtering.md) |
| **755** | **A Folio Coverage Homogeneity** (real A folios at 0th percentile for discrimination vs random; deliberate coverage optimization) | 2 | A | -> [C755_a_folio_coverage_homogeneity.md](C755_a_folio_coverage_homogeneity.md) |
| **756** | **Coverage Optimization Confirmed** (11x higher pairwise similarity than random; first 10 folios cover 60% PP; hub MIDDLEs 100% PP) | 2 | A | -> [C756_coverage_optimization_confirmed.md](C756_coverage_optimization_confirmed.md) |

### AZC Folio Differentiation (C757-C765, C900) - Phase: AZC_FOLIO_DIFFERENTIATION, PTEXT_FOLIO_ANALYSIS

> **Summary:** AZC folios are vocabulary-specialized (70% MIDDLEs exclusive to single folio) but structurally uniform. Zero KERNEL/LINK tokens confirms AZC is outside execution layer. P-text is linguistically Currier A (0.97 cosine). Position within diagrams determines vocabulary (p<0.001). Zodiac and A/C families provide redundant B coverage (r=0.90). f57v R2 ring is 100% single characters with repeating ~27-char pattern - structurally non-Voynichese.

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| **757** | **AZC Zero Kernel/Link** (0 KERNEL, 0 LINK; ~50% OPERATIONAL, ~50% UN; AZC is outside execution layer) | 2 | AZC | -> [C757_azc_zero_kernel.md](C757_azc_zero_kernel.md) |
| **758** | **P-Text Currier A Identity** (PREFIX cosine 0.97 to A, 0.74 to diagram; 19.5% MIDDLE overlap with same-folio diagram) | 2 | AZC | -> [C758_ptext_currier_a_identity.md](C758_ptext_currier_a_identity.md) |
| **759** | **AZC Position-Vocabulary Correlation** (position affects PREFIX: chi2=112.6, p<0.001, V=0.21; S=56% ok+ot, C=28% ch) | 2 | AZC | -> [C759_azc_position_vocabulary.md](C759_azc_position_vocabulary.md) |
| **760** | **AZC Folio Vocabulary Specialization** (70% MIDDLEs exclusive to 1 folio; 13 universal MIDDLEs; no family pattern) | 2 | AZC | -> [C760_azc_folio_vocabulary_specialization.md](C760_azc_folio_vocabulary_specialization.md) |
| **761** | **AZC Family B-Coverage Redundancy** (Zodiac-A/C correlation r=0.90; 81/82 B folios balanced; both families contribute ~5-6 exclusive MIDDLEs per B) | 2 | AZC | -> [C761_azc_family_b_redundancy.md](C761_azc_family_b_redundancy.md) |
| **762** | **Cross-System Single-Char Primitive Overlap** (f49v/f76r/f57v share 4 chars d,k,o,r - all C085 primitives; spans PREFIX/MIDDLE/SUFFIX positions) | 2 | GLOBAL | -> [C762_cross_system_single_char_primitives.md](C762_cross_system_single_char_primitives.md) |
| **763** | **f57v R2 Single-Char Ring Anomaly** (100% single chars, 0% morphology; ~27-char repeating pattern with p/f variation; m,n unique terminators; diagram-integrated unlike margin labels) | 2 | AZC | -> [C763_f57v_r2_single_char_ring.md](C763_f57v_r2_single_char_ring.md) |
| **764** | **f57v R2 Coordinate System** (UNIQUE to f57v across 13 Zodiac folios; p/f at 27-pos apart mark ring halves; R1-R2 1:1 token correspondence; 'x' coord-only char never in R1) | 2 | AZC | -> [C764_f57v_coordinate_system.md](C764_f57v_coordinate_system.md) |
| **765** | **AZC Kernel Access Bottleneck** (AZC-mediated: 31.3% escape, 51.3% kernel; B-native: 21.5% escape, 77.8% kernel; AZC constrains B by limiting kernel access, not escape directly) | 2 | GLOBAL | -> [C765_azc_kernel_access_bottleneck.md](C765_azc_kernel_access_bottleneck.md) |
| **900** | **AZC P-Text Annotation Pages** (f65v/f66v are 100% P-text, linguistically A (0.941 cosine), flanking f66r zodiac; 60%+ vocabulary overlap confirms annotation role) | 2 | AZC | -> [C900_azc_ptext_annotation_pages.md](C900_azc_ptext_annotation_pages.md) |

---

### Compound MIDDLE Architecture (C766-C769) - Phase: COMPOUND_MIDDLE_ARCHITECTURE

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| **766** | **UN = Derived Identification Vocabulary** (UN 81.1% compound vs classified 35.2%; +45.9pp; 1,251 UN-only MIDDLEs at 84.3% compound; 0 classified-only MIDDLEs) | 2 | B | -> [C766_un_derived_vocabulary.md](C766_un_derived_vocabulary.md) |
| **767** | **Class Compound Bimodality** (21 base-only classes at 0-5% compound, 3 compound-heavy classes at 85%+; grammar has two functional vocabularies) | 2 | B | -> [C767_class_compound_bimodality.md](C767_class_compound_bimodality.md) |
| **768** | **Role-Compound Correlation** (FL=0% compound, FQ=46.7%; 46.7pp spread; FL uses 0 kernel chars k/h/e; role determines vocabulary type) | 2 | B | -> [C768_role_compound_correlation.md](C768_role_compound_correlation.md) |
| **769** | **Compound Context Prediction** (Line-1 +5pp more compound; folio-unique correlation r=0.553; class range 0%-100%; compound structure is informative) | 2 | B | -> [C769_compound_context_prediction.md](C769_compound_context_prediction.md) |

### FL Primitive Architecture (C770-C781) - Phase: FL_PRIMITIVE_ARCHITECTURE

> **Terminology:** "FL" = MIDDLE-based material state taxonomy (~25% of tokens).
> "FLOW_OPERATOR" or "FO" = 49-class behavioral role (classes 7/30/38/40, 4.7% of tokens).
> See [../TERMINOLOGY/fl_disambiguation.md](../TERMINOLOGY/fl_disambiguation.md).

> **Summary:** FL (Flow Operator) is a kernel-free state index ('i'=start, 'y'=end). EN is the **phase/stability operator** (h+e, 92% kernel) managing state transitions. FQ is the **phase-bypass escape** (k+e, **0% h**) - escape routes skip phase management entirely. Roles partition kernel responsibilities: FL=0%, EN=92% h+e, FQ=46% k+e, CC=25%, AX=57%. Forbidden pairs involve CC (20), FQ (10), EN (4); FL and AX are outside.

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| **770** | **FL Kernel Exclusion** (FL uses 0 kernel chars k/h/e; only role with complete kernel exclusion; 17 MIDDLEs, 1,078 tokens) | 2 | B | -> [C770_fl_kernel_exclusion.md](C770_fl_kernel_exclusion.md) |
| **771** | **FL Character Restriction** (FL uses exactly 9 chars: a,d,i,l,m,n,o,r,y; excludes c,e,h,k,s,t; mean MIDDLE length 1.58) | 2 | B | -> [C771_fl_character_restriction.md](C771_fl_character_restriction.md) |
| **772** | **FL Primitive Substrate** (FL provides substrate layer; other roles add kernel k/h/e then helpers c/s/t; EN 60.7% kernel-containing highest) | 2 | B | -> [C772_fl_primitive_substrate.md](C772_fl_primitive_substrate.md) |
| **773** | **FL Hazard-Safe Position Split** (Hazard FL 88.7% at mean pos 0.546 medial; Safe FL 11.3% at mean pos 0.811 line-final; 0.265 position gap) | 2 | B | -> [C773_fl_hazard_position_split.md](C773_fl_hazard_position_split.md) |
| **774** | **FL Outside Forbidden Topology** (FL classes not in any of 17 forbidden pairs; FL operates below hazard layer) | 2 | B | -> [C774_fl_outside_forbidden_topology.md](C774_fl_outside_forbidden_topology.md) |
| **775** | **Hazard FL Escape Driver** (Hazard FL 7/30 drive 98% of FL->FQ; safe FL 38/40 drive 2%; FL->FQ rate 22.5%) | 2 | B | -> [C775_hazard_fl_escape_driver.md](C775_hazard_fl_escape_driver.md) |
| **776** | **Post-FL Kernel Enrichment** (59.4% of post-FL tokens have kernel chars k/h/e; confirms FL -> kernel-modulated flow pattern) | 2 | B | -> [C776_post_fl_kernel_enrichment.md](C776_post_fl_kernel_enrichment.md) |
| **777** | **FL State Index** (FL MIDDLEs index material state; 'i'-forms at start (0.30), 'y'-forms at end (0.94); position range 0.64; 77% state change rate) | 2 | B | -> [C777_fl_state_index.md](C777_fl_state_index.md) |
| **778** | **EN Kernel Profile** (EN 91.9% kernel; dominant h+e (35.8%); h=59.4%, e=58.3%, k=38.6%; phase/stability operator not energy) | 2 | B | -> [C778_en_kernel_profile.md](C778_en_kernel_profile.md) |
| **779** | **EN-FL State Coupling** (EN 'h' rate drops 95%->77% as FL advances early->late; early states need phase management, late states stable) | 2 | B | -> [C779_en_fl_state_coupling.md](C779_en_fl_state_coupling.md) |
| **780** | **Role Kernel Taxonomy** (FL=0%, EN=92% h+e, FQ=46% k+e 0%h, CC=25%, AX=57%; roles partition kernel responsibilities) | 2 | B | -> [C780_role_kernel_taxonomy.md](C780_role_kernel_taxonomy.md) |
| **781** | **FQ Phase Bypass** (FQ has exactly 0% 'h'; escape routes bypass phase management using k+e only) | 2 | B | -> [C781_fq_phase_bypass.md](C781_fq_phase_bypass.md) |

### Control Topology Analysis (C782-C787) - Phase: CONTROL_TOPOLOGY_ANALYSIS

> **Summary:** Forbidden pair topology is **directional** (17 asymmetric, 0 symmetric). CC role bifurcates: classes 10,11 (0% kernel, hazard sources) vs class 17 (88% kernel, hazard target). FL and AX are **immune** to hazard topology (0 forbidden pair participation). FQ escape targets FL[MEDIAL] at 77%. FL state transitions are **forward-biased** (27% forward, 5% backward); LATE->EARLY is **forbidden** (0 occurrences).

| # | Constraint | Tier | Scope | Link |
|---|------------|------|-------|------|
| **782** | **CC Kernel Paradox** (Classes 10,11=0% kernel, class 17=88%; CC bifurcates into hazard sources vs hazard buffers) | 2 | B | -> [C782_cc_kernel_paradox.md](C782_cc_kernel_paradox.md) |
| **783** | **Forbidden Pair Asymmetry** (All 17 forbidden pairs are asymmetric/directional; 0 symmetric; hazard is directed graph) | 2 | B | -> [C783_forbidden_pair_asymmetry.md](C783_forbidden_pair_asymmetry.md) |
| **784** | **FL/AX Hazard Immunity** (FL and AX never appear in any forbidden pair; exempt from hazard topology) | 2 | B | -> [C784_fl_ax_hazard_immunity.md](C784_fl_ax_hazard_immunity.md) |
| **785** | **FQ Medial Targeting** (FQ->FL routes to MEDIAL at 77.2%; escape re-injects at mid-process, not start/end) | 2 | B | -> [C785_fq_medial_targeting.md](C785_fq_medial_targeting.md) |
| **786** | **FL Forward Bias** (FL state transitions: 27% forward, 68% same, 5% backward; 5:1 forward:backward ratio) | 2 | B | -> [C786_fl_forward_bias.md](C786_fl_forward_bias.md) |
| **787** | **FL State Reset Prohibition** (LATE->EARLY transition = 0 occurrences; full state reset is forbidden) | 2 | B | -> [C787_fl_state_reset_prohibition.md](C787_fl_state_reset_prohibition.md) |

### CC Mechanics Deep Dive (C788-C791) - Phase: CC_MECHANICS_DEEP_DIVE

> **Summary:** CC classes are singleton/near-singleton token sets: Class 10="daiin", Class 11="ol", Class 17=9 "ol-" tokens. Class 12="k" is a **structural ghost** (0 B occurrences). Forbidden pairs are **NOT absolute** - 34% of CC->FQ transitions violate them. CC shows positional gradient (Group A earlier, p=0.045). CC->EN is the dominant flow (3:1 over CC->FQ).

| # | Constraint | Tier | Scope | Link |
|---|------------|------|-------|------|
| **788** | **CC Singleton Identity** (Class 10=daiin, Class 11=ol, Class 12=k(absent), Class 17=9 ol- tokens; CC classes are specific tokens not broad categories) | 2 | B | -> [C788_cc_singleton_identity.md](C788_cc_singleton_identity.md) |
| **789** | **Forbidden Pair Permeability** (34% of CC->FQ transitions violate forbidden pairs; forbidden = disfavored, not prohibited) | 2 | B | -> [C789_forbidden_pair_permeability.md](C789_forbidden_pair_permeability.md) |
| **790** | **CC Positional Gradient** (Group A mean 0.469, Group B mean 0.515, p=0.045; sources earlier, targets later) | 2 | B | -> [C790_cc_positional_gradient.md](C790_cc_positional_gradient.md) |
| **791** | **CC-EN Dominant Flow** (CC->EN at 33% vs CC->FQ at 12%; CC primarily routes to kernel ops, not escape) | 2 | B | -> [C791_cc_en_dominant_flow.md](C791_cc_en_dominant_flow.md) |

### PP-HT-AZC Interaction (C796-C803) - Phase: PP_HT_AZC_INTERACTION

> **Summary:** HT density is controlled by two orthogonal factors: AZC mediation (negative: rho=-0.352) and escape activity (positive: rho=0.377). These are independent (AZC-FL correlation = -0.023 NS) and additive. Low AZC + High FL folios have 37% HT; High AZC + Low FL have 25% HT. Line-1 header structure (C794-C795) is AZC-independent — the A-context prediction mechanism operates uniformly regardless of AZC involvement. HT is not random padding but encodes **dual structural information**: vocabulary provenance (AZC axis) and operational intensity (escape axis). **Body HT (C800-C803):** The escape correlation is driven entirely by body HT (lines 2+), not line-1. Body HT uses primitive PP vocabulary (80.1% PP, top MIDDLEs are C085 primitives) and clusters at line boundaries (45.8%/42.9% first/last vs 25.7% middle) and near LINK tokens (2.53 vs 3.08 distance, p<0.0001), but NOT near FL tokens. HT marks monitoring/waiting zones, not escape points.

| # | Constraint | Tier | Scope | Link |
|---|------------|------|-------|------|
| **796** | **HT-Escape Correlation** (HT% correlates with FL%: rho=0.377, p=0.0005; high escape -> more HT; independent of AZC) | 2 | B/HT | -> [C796_ht_escape_correlation.md](C796_ht_escape_correlation.md) |
| **797** | **AZC-HT Inverse Relationship** (AZC% anti-correlates with HT%: rho=-0.352, p=0.0012; high AZC -> less HT; confounded by vocab size) | 2 | A<>B/HT | -> [C797_azc_ht_inverse.md](C797_azc_ht_inverse.md) |
| **798** | **HT Dual Control Architecture** (AZC and FL are orthogonal predictors of HT; effects additive; quadrant range 25%-37% HT) | 2 | GLOBAL/HT | -> [C798_ht_dual_control.md](C798_ht_dual_control.md) |
| **799** | **Line-1 AZC Independence** (Line-1 PP fraction and A-context prediction accuracy do NOT vary by AZC tertile; header is fixed structure) | 2 | B/HT | -> [C799_line1_azc_independence.md](C799_line1_azc_independence.md) |
| **800** | **Body HT Escape Driver** (Body HT drives escape correlation: rho=0.367, p=0.0007; line-1 HT is independent: rho=0.107, p=0.35) | 2 | B/HT | -> [C800_body_ht_escape_driver.md](C800_body_ht_escape_driver.md) |
| **801** | **Body HT Primitive Vocabulary** (80.1% PP, top MIDDLEs are C085 primitives e/ed/d/l/k/o; Jaccard overlap with line-1 = 0.122) | 2 | B/HT | -> [C801_body_ht_primitive_vocabulary.md](C801_body_ht_primitive_vocabulary.md) |
| **802** | **Body HT LINK Proximity** (HT clusters near LINK: 2.53 vs 3.08 distance, p<0.0001; NOT near FL: 4.04 vs 3.82, p=0.056 NS) | 2 | B/HT | -> [C802_body_ht_link_proximity.md](C802_body_ht_link_proximity.md) |
| **803** | **Body HT Boundary Enrichment** (HT rate: first=45.8%, last=42.9%, middle=25.7%; marks control block boundaries) | 2 | B/HT | -> [C803_body_ht_boundary_enrichment.md](C803_body_ht_boundary_enrichment.md) |

---

### LINK Operator Architecture (C804-C809) - Phase: LINK_OPERATOR_ARCHITECTURE

> **Summary:** LINK ('ol' in token, 13.2% of B) is characterized as a monitoring/waiting phase marker. Key findings: (1) C366 transition grammar claims are NOT reproducible with current role taxonomy - predecessor enrichment not confirmed, successor enrichment weak; (2) C365 spatial uniformity is REFUTED - LINK shows boundary enrichment like HT; (3) LINK-HT overlap is moderate (OR=1.50) driven by vocabulary composition; (4) LINK is INVERSELY related to FL (escape) - farther distance, negative correlation, depleted around FL; (5) 'ol' is a legitimate PP MIDDLE (in A vocabulary, 92.4% PP rate); (6) LINK is spatially separated from kernel (k,h,e) operations. Architecture: LINK marks monitoring zones distinct from both kernel processing and escape recovery.

| # | Constraint | Tier | Scope | Link |
|---|------------|------|-------|------|
| **804** | **LINK Transition Grammar Revision** (C366 predecessor claims not confirmed; successor enrichment weak; chi2=5.1 pred NS, chi2=48.2 succ p<0.001) | 2 | B | -> [C804_link_transition_grammar_revision.md](C804_link_transition_grammar_revision.md) |
| **805** | **LINK Positional Bias (C365 Refutation)** (Mean pos 0.476 vs 0.504; first=17.2%, last=15.3%, middle=12.4%; shares HT boundary pattern) | 2 | B | -> [C805_link_positional_bias.md](C805_link_positional_bias.md) |
| **806** | **LINK-HT Positive Association** (OR=1.50, p<0.001; 38.3% of LINK are HT; HT contains 'ol' at 16.6% vs 11.7%) | 2 | B/HT | -> [C806_link_ht_overlap.md](C806_link_ht_overlap.md) |
| **807** | **LINK-FL Inverse Relationship** (LINK farther from FL: 3.91 vs 3.38, p<0.0001; rho=-0.222; depleted around FL 0.67x/0.87x) | 2 | B | -> [C807_link_fl_inverse.md](C807_link_fl_inverse.md) |
| **808** | **LINK 'ol' is PP MIDDLE** ('ol' appears 759x as MIDDLE, in A vocabulary; LINK PP rate 92.4%) | 2 | B | -> [C808_link_ol_pp_middle.md](C808_link_ol_pp_middle.md) |
| **809** | **LINK-Kernel Separation** (LINK depleted of k/h/e: 0.82-0.93x; distance 1.31 vs 0.41, p<0.0001) | 2 | B | -> [C809_link_kernel_separation.md](C809_link_kernel_separation.md) |

---

### Control Loop Synthesis (C810-C815) - Phase: CONTROL_LOOP_SYNTHESIS

> **Summary:** Integration of KERNEL, LINK, and FL into unified control loop model. Key findings: (1) LINK-FL non-adjacency confirmed - direct transitions rare (0.70x); (2) FL chains at 2.11x - extended escape sequences, not single-token events; (3) HT uses novel MIDDLE combinations (11.19% novel pairs) but obeys C475 forbidden pairs (0.44% violation per C742) - distinct combinatorial space, not grammar violation; (4) Canonical ordering LINK(0.476)->KERNEL(0.482)->FL(0.576) - monitoring early, escape late; (5) KERNEL is strongest negative predictor of FL (rho=-0.528) - high kernel = stable program; (6) Phase positions significant (p<10^-73) but only 1.5% variance explained - temporally flexible, not rigidly positional.

| # | Constraint | Tier | Scope | Link |
|---|------------|------|-------|------|
| **810** | **LINK-FL Non-Adjacency** (Direct LINK->FL rare: 0.70x expected; confirms complementary phases) | 2 | B | -> [C810_link_fl_non_adjacency.md](C810_link_fl_non_adjacency.md) |
| **811** | **FL Chaining** (FL->FL enriched 2.11x; extended escape sequences; FL->KERNEL neutral 0.86x) | 2 | B | -> [C811_fl_chaining.md](C811_fl_chaining.md) |
| **812** | **HT Novel MIDDLE Combinations** (11.19% novel pairs; NOT C475 violation; HT in distinct combinatorial space) | 2 | B/HT | -> [C812_ht_c475_violation.md](C812_ht_c475_violation.md) |
| **813** | **Canonical Phase Ordering** (LINK 0.476 -> KERNEL 0.482 -> FL 0.576; monitoring early, escape late) | 2 | B | -> [C813_canonical_phase_ordering.md](C813_canonical_phase_ordering.md) |
| **814** | **Kernel-Escape Inverse** (KERNEL vs FL rho=-0.528; high kernel = low escape; strongest predictor) | 2 | B | -> [C814_kernel_escape_inverse.md](C814_kernel_escape_inverse.md) |
| **815** | **Phase Position Significance** (F=70.28, p<10^-73 but eta^2=0.015; phases flexible, not rigid) | 2 | B | -> [C815_phase_position_significance.md](C815_phase_position_significance.md) |

### CC Control Loop Integration (C816-C820) - Phase: CC_CONTROL_LOOP_INTEGRATION

> **Summary:** Integrates Core Control (CC) into the LINK-KERNEL-FL control loop. Key findings: (1) daiin initiates the loop at 0.413, significantly earlier than LINK (0.476) - complete ordering is daiin->LINK->KERNEL->ol->FL; (2) C600 lane routing CONFIRMED: daiin->CHSH 90.8%, ol_derived->QO 57.4%, but lane bias decays rapidly by offset +2; (3) "kernel paradox" RESOLVED: Class 17 (ol_derived) is the CC-KERNEL bridge layer with 88% kernel chars; (4) daiin is initial-biased (27.1%), ol/ol_derived are middle-concentrated (85%); (5) CC has ZERO forbidden transitions (0/700) - EN absorbs 99.8% of all hazard.

| # | Constraint | Tier | Scope | Link |
|---|------------|------|-------|------|
| **816** | **CC Positional Ordering** (daiin 0.413 -> LINK 0.476 -> KERNEL -> ol 0.511 -> FL 0.576; daiin initiates loop) | 2 | B | -> [C816_cc_positional_ordering.md](C816_cc_positional_ordering.md) |
| **817** | **CC Lane Routing** (C600 confirmed: daiin->CHSH 90.8%, ol_derived->QO 57.4%; rapid decay by +2) | 2 | B | -> [C817_cc_lane_routing.md](C817_cc_lane_routing.md) |
| **818** | **CC Kernel Bridge** (Class 17 = CC-KERNEL interface; 88% kernel chars; resolves C782 paradox) | 2 | B | -> [C818_cc_kernel_bridge.md](C818_cc_kernel_bridge.md) |
| **819** | **CC Boundary Asymmetry** (daiin initial 27.1%; ol/ol_derived medial 85%; unlike LINK 1.23x) | 2 | B | -> [C819_cc_boundary_asymmetry.md](C819_cc_boundary_asymmetry.md) |
| **820** | **CC Hazard Immunity** (0/700 forbidden; EN absorbs 99.8% hazard; CC is safe control layer) | 2 | B | -> [C820_cc_hazard_immunity.md](C820_cc_hazard_immunity.md) |

### REGIME Line Syntax Interaction (C821-C823) - Phase: REGIME_LINE_SYNTAX_INTERACTION

> **Summary:** Tests whether line-level execution syntax varies by REGIME. **NULL RESULT confirms grammar universality (C124).** All 5 roles show INVARIANT position by REGIME (p>0.4). REGIME explains only 0.13% of position variance (vs 1.5% for PHASE per C815). REGIME encodes execution requirements (what to do), not syntax structure (where to put it). One exception: or->aiin bigram shows frequency variation by REGIME (6x higher in REGIME_4), but this is frequency not position.

| # | Constraint | Tier | Scope | Link |
|---|------------|------|-------|------|
| **821** | **Line Syntax REGIME Invariance** (All 5 roles invariant; eta^2=0.13%; confirms C124 universality) | 2 | B | -> [C821_line_syntax_regime_invariance.md](C821_line_syntax_regime_invariance.md) |
| **822** | **CC Position REGIME Invariance** (REGIME affects CC frequency not placement; daiin initial-bias p=0.65) | 2 | B | -> [C822_cc_position_regime_invariance.md](C822_cc_position_regime_invariance.md) |
| **823** | **Bigram REGIME Partial Variation** (or->aiin varies 6x; daiin->CHSH invariant p=0.63) | 2 | B | -> [C823_bigram_regime_partial_variation.md](C823_bigram_regime_partial_variation.md) |

### A-Record B-Routing Topology (C824-C836) - Phase: A_RECORD_B_ROUTING_TOPOLOGY

> **Summary:** Tests A->B filtering mechanics, aggregation effects, repetition function, and RI internal structure. **KEY FINDINGS:** (1) C502 token-filtering model CORRECT: more PP = more token survival (rho=+0.734). Aggregation HELPS: line 11.2% -> paragraph 31.8% -> folio 50.0%. (2) Repetition is 100% PP, 0% RI - confirms functional bifurcation. (3) daiin (control loop trigger) accounts for 22% of all repeats. (4) **RI THREE-TIER STRUCTURE:** Singletons (95.3%), position-locked repeaters (~4%), linkers (0.6%). (5) **RI LINKER DISCOVERY:** 4 tokens create 12 directed links connecting 12 folios; 66.7% forward flow. (6) **ct-ho SIGNATURE:** Linkers show 75% ct-prefix + 75% h-MIDDLE (12-15x enrichment) marking "transferable outputs". (7) **INPUT/OUTPUT ASYMMETRY:** 12+ INPUT morphological markers vs 5 OUTPUT markers; -ry is strongest OUTPUT signal.

| # | Constraint | Tier | Scope | Link |
|---|------------|------|-------|------|
| **824** | **A-Record Filtering Mechanism** (81.3% filtering confirms C502; aggregation helps usability) | 2 | A/B | -> [C824_a_record_filtering_mechanism.md](C824_a_record_filtering_mechanism.md) |
| **825** | **Continuous Not Discrete Routing** (silhouette=0.124; no discrete clusters; 97.6% unique profiles) | 2 | A/B | -> [C825_continuous_not_discrete_routing.md](C825_continuous_not_discrete_routing.md) |
| **826** | **Token Filtering Model Validation** (C502 CORRECT: more PP = more survival rho=+0.734; aggregation 4.45x) | 2 | A/B | -> [C826_token_filtering_model_validation.md](C826_token_filtering_model_validation.md) |
| **827** | **Paragraph Operational Unit** (gallows-initial paragraphs: 31.8% survival, 2.8x better than lines) | 2 | A/B | -> [C827_paragraph_operational_unit.md](C827_paragraph_operational_unit.md) |
| **828** | **PP Repetition Exclusivity** (100% PP, 0% RI within-line repeats; p=2.64e-07; confirms C498 bifurcation) | 2 | A | -> [C828_pp_repetition_exclusivity.md](C828_pp_repetition_exclusivity.md) |
| **829** | **daiin Repetition Dominance** (22% of all repeats; CC trigger may encode control-loop cycle count) | 2 | A | -> [C829_daiin_repetition_dominance.md](C829_daiin_repetition_dominance.md) |
| **830** | **Repetition Position Bias** (late-biased 0.675; FINAL 12x higher than INITIAL; parameters follow identity) | 2 | A | -> [C830_repetition_position_bias.md](C830_repetition_position_bias.md) |
| **831** | **RI Three-Tier Population Structure** (singletons 95.3%, position-locked ~4%, linkers 0.6%) | 2 | A | -> [C831_ri_three_tier_structure.md](C831_ri_three_tier_structure.md) |
| **832** | **Initial/Final RI Vocabulary Separation** (Jaccard=0.010; only 4 words overlap; different PREFIX profiles) | 2 | A | -> [C832_initial_final_ri_separation.md](C832_initial_final_ri_separation.md) |
| **833** | **RI First-Line Concentration** (1.85x in paragraph first line; 1.03x at folio level - no structure) | 2 | A | -> [C833_ri_first_line_concentration.md](C833_ri_first_line_concentration.md) |
| **834** | **Paragraph Granularity Validation** (RI structure visible ONLY at paragraph level; validates record size) | 2 | A | -> [C834_paragraph_granularity_validation.md](C834_paragraph_granularity_validation.md) |
| **835** | **RI Linker Mechanism** (4 tokens, 12 links, 12 folios; 66.7% forward flow; f93v=5 inputs collector) | 2 | A | -> [C835_ri_linker_mechanism.md](C835_ri_linker_mechanism.md) |
| **836** | **RI Linker ct-Prefix Signature** (75% ct-prefix; ho/heo MIDDLE; may mark linkable outputs) | 2/3 | A | -> [C836_ri_linker_ct_prefix.md](C836_ri_linker_ct_prefix.md) |
| **837** | **ct-ho Linker Morphological Signature** (75% ct-prefix + 75% h-MIDDLE = 12-15x enrichment; unique signature) | 2/3 | A | -> [C837_ct_ho_linker_signature.md](C837_ct_ho_linker_signature.md) |
| **838** | **qo-Linker Exception** (qokoiiin doesn't follow ct-ho; may be different linkage mechanism) | 2 | A | -> [C838_qo_linker_exception.md](C838_qo_linker_exception.md) |
| **839** | **RI Input-Output Morphological Asymmetry** (12+ INPUT markers vs 5 OUTPUT markers; -ry strongest OUTPUT) | 2 | A | -> [C839_input_output_morphological_asymmetry.md](C839_input_output_morphological_asymmetry.md) |

---

**MIDDLE Sub-Component Grammar (C510-C520):** MIDDLEs have internal compositional structure. PP MIDDLEs are the generative substrate (99.1% of RI contains PP atoms). Positional grammar is permissive (58.8% free) with asymmetric PP distribution: PP dominates END-class (71.4%) while RI elaborations dominate START-class (16.1% PP). Architecture: `RI-START + PP-FREE + PP-END`. Short singletons are sampling variance, not distinct class. RI exhibits compositional bifurcation: 17.4% locally-derived (embeds same-record PP), 82.6% globally-composed. Local derivation correlates with length (rho=0.192): short RI = atomic global discriminators, long RI = compound local elaborators. Mechanism: embedding local context is additive. **RI is multi-atom compositional:** 85.4% of RI contain multiple PP atoms; 261 PP bases collapse 712 RI (2.7x); only 0.03% of theoretical combinations used. RI encodes **compatibility intersections** (PP₁ ∩ PP₂ ∩ ... ∩ modifier), not simple material variations. **GLOBAL COMPATIBILITY ARCHITECTURE (Tier 3):** Superstring compression (65-77% overlap) and compatibility enrichment (5-7x) are GLOBAL across all systems, extending C383. The morphological type system includes embedded compatibility relationships. RI exploits this architecture most intensively (6.8x) for discrimination; B shows baseline exploitation (5.3x) for execution elaboration.

**RI as Complexity Gradient (C498.b, C498.c, C498.d):** A MIDDLEs partition into PP (404, shared with B) + RI (609, A-exclusive). RI singleton/repeater status is strongly correlated with length (rho=-0.367): short MIDDLEs repeat more (combinatorially limited), long MIDDLEs are unique (combinatorially diverse). Previous "RI-D/RI-B" functional interpretations are WEAKENED to Tier 3. See currier_a.md.

**C498-CHAR-A-CLOSURE (Tier 3):** RI closure tokens — subset of C498 vocabulary shows line-final preference (29.5% vs 16.8%), 87% singletons, complementary to DA articulation (C422). Ergonomic bias, not grammar. See currier_a.md.

**C498-CHAR-A-SEGMENT (Tier 3):** RI closure operates hierarchically: 1.76× at line-final, 1.43× at segment-final. RI-RICH segments (>30% RI, 6.1%) are short, PREFIX-coherent, terminal-preferring. PREFIX does NOT predict segment RI profile (p=0.151) — RI concentration is positional, not PREFIX-bound. See currier_a.md.

**C498.a (Tier 2 Refinement):** A∩B shared vocabulary bifurcates into AZC-Mediated (154 MIDDLEs, true pipeline) and B-Native Overlap (114 MIDDLEs, B vocabulary with incidental A presence). Pipeline scope is narrower than "all A∩B shared" implies. See currier_a.md.

---

## MIDDLE Perturbation Space (C461-C462)

> **Summary:** C461-C462 establish behavioral structure in MIDDLE frequency tiers and material class sharing. The A-layer recognition space is partitioned into universal apparatus-generic situations vs class-specific perturbations. **This line of inquiry is SATURATED.**

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| 461 | HT density correlates with MIDDLE rarity (Tail 1.58x, chi2=180.56) | 3 | A→B | -> [C461_ht_middle_rarity.md](C461_ht_middle_rarity.md) |
| 462 | Universal MIDDLEs are mode-balanced (51% vs 87% precision, chi2=471.55) | 3 | A→B | -> [C462_universal_mode_balance.md](C462_universal_mode_balance.md) |

**Saturation note:** The shared MIDDLE identification question is CLOSED internally. MIDDLEs can be classified by behavioral independence/dependence but not by entity semantics.

---

## Grouped Registries

These files contain detailed constraint documentation. Constraint ranges are approximate - use [CONSTRAINT_TABLE.txt](../CONSTRAINT_TABLE.txt) for the authoritative complete list.

| File | Contents | Primary Ranges |
|------|----------|----------------|
| [tier0_core.md](tier0_core.md) | Tier 0 frozen facts | C074-C132 |
| [grammar_system.md](grammar_system.md) | Grammar and kernel structure | C085-C144, C328-C393 |
| [currier_a.md](currier_a.md) | Currier A registry | C224-C299, C345-C346, C420-C424, C475-C478, C498-C525 |
| [morphology.md](morphology.md) | Compositional morphology | C267-C298, C349-C410, C495 |
| [operations.md](operations.md) | OPS doctrine and control | C178-C223, C394-C403 |
| [human_track.md](human_track.md) | Human Track layer | C166-C172, C341-C348, C404-C419, C450-C453, C477, C507, C740-C750, C870-C872 |
| [azc_system.md](azc_system.md) | AZC hybrid system | C300-C327, C430-C436, C496 |
| [organization.md](organization.md) | Organizational structure | C153-C176, C323-C370 |

---

### Token Annotation Findings (C901-C903) - Phase: TOKEN_ANNOTATION_BATCH_11

> **Summary:** Systematic token-by-token annotation of all 114 Currier A folios (1,272+ lines) revealed previously invisible structural patterns. Extended e-sequences form a stability gradient (C901). Late Currier A (f100-f102) exhibits distinct register characteristics suggesting appendix content (C902). Prefix inventory shows rarity gradient with qk/qy marking exceptional entries (C903). C833 refined to note 50% non-L1 RI prevalence.

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| **901** | **Extended e Stability Gradient** (e→ee→eee→eeee forms stability depth continuum; quadruple-e in 11 folios concentrated late Currier A; odeeeey = maximum observed) | 2 | A | -> [C901_extended_e_stability_gradient.md](C901_extended_e_stability_gradient.md) |
| **902** | **Late Currier A Register** (f100-f102 show distinct characteristics: p/f-domain concentration, extended vowels, short lines, MONSTERS; suggests appendix/addendum content) | 2 | A | -> [C902_late_currier_a_register.md](C902_late_currier_a_register.md) |
| **903** | **Prefix Rarity Gradient** (Common ch/sh/qo vs rare ct vs very-rare qk (9 folios) vs extremely-rare qy (3 folios); rarity correlates with specialization) | 2 | A | -> [C903_prefix_rarity_gradient.md](C903_prefix_rarity_gradient.md) |

**Data sources:** `data/folio_notes.json`, `data/token_dictionary.json`, `data/annotation_progress.json`

---

### B Folio-Level Structure (C905) - Phase: B_PARAGRAPH_POSITION_STRUCTURE

> **Summary:** Testing paragraph-level structure in B folios confirmed the PARALLEL_PROGRAMS model (C855). Paragraph position has minimal structural significance. At the FOLIO level, TERMINAL FL concentrates in early lines (p=0.0005), interpreted as **input-state declaration** - early lines describe what state the input material is in. Cross-folio vocabulary chaining was NOT supported; instead, same-section folios share TERMINAL FL vocabulary (1.30x Jaccard) reflecting domain coherence.

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| **905** | **FL_TERMINAL Early-Line Concentration** (TERMINAL FL = input-state declaration, not completion marking; early>late gradient -3.7%, p=0.0005; same-section vocabulary sharing 1.30x, p<0.0001; cross-folio chaining NOT supported) | 2 | B | -> [C905_fl_terminal_early_concentration.md](C905_fl_terminal_early_concentration.md) |

**Phase findings:**
- C855 (PARALLEL_PROGRAMS) strongly supported
- C857 (P1 not special) strongly supported
- AX prefix: no significant folio-level gradient (p=0.52)
- Vocabulary overlap early vs late: Jaccard=0.305
- Cross-folio TERMINAL FL chaining: NOT supported (z=-0.61)
- Same-section domain coherence: SUPPORTED (1.30x Jaccard, p<0.0001)

---

### MIDDLE Coverage Analysis (C906-C907) - Phase: MIDDLE_COVERAGE_ANALYSIS

> **Summary:** Systematic analysis of unmapped MIDDLE tokens in Currier B revealed the **Vowel Primitive Suffix Saturation** pattern. Vowel cores (a, e, o) almost always require suffixes (~98%), but when the suffix is written as part of the MIDDLE string (e.g., `edy` vs `e`+`dy`), it's morphologically "absorbed" - equivalent operations with different notational forms. This discovery improved operational coverage from 19.1% to 57.3%. Secondary -hy infrastructure tokens were identified but their procedural connector hypothesis was falsified.

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| **906** | **Vowel Primitive Suffix Saturation** (Vowel MIDDLEs a/e/o + END-class suffix = closed compound that suppresses further suffixation; e→98.3% suffix, edy→0.4% suffix; explains 38% of unmapped tokens) | 2 | GLOBAL | → [C906_vowel_primitive_suffix_saturation.md](C906_vowel_primitive_suffix_saturation.md) |
| **907** | **-hy Consonant Cluster Infrastructure** (Tokens with -hy suffix form formulaic class: ch/sh prefix + consonant cluster MIDDLE + hy; 910 tokens (3.9%); connector hypothesis FALSIFIED - 0.99x boundary enrichment) | 4 | B | → [C907_hy_consonant_cluster_infrastructure.md](C907_hy_consonant_cluster_infrastructure.md) |

**Phase findings:**
- Coverage improved: 19.1% → 73.1% explained tokens
- e-family absorption: 5,266 tokens (22.8% of B)
- o-family absorption: 1,571 tokens (6.8% of B)
- a-family absorption: 2,675 tokens (11.6% of B)
- k-variants (ck, eck) are NOT absorption patterns - specialized formulaic constructions
- -hy tokens: procedural connector hypothesis falsified (0.99x baseline enrichment)

---

### MIDDLE Semantic Mapping (C908-C910) - Phase: MIDDLE_SEMANTIC_MAPPING

> **Summary:** Systematic analysis of MIDDLE distribution across kernel profiles, sections, and REGIMEs revealed strong functional clustering. MIDDLEs encode operational semantics along three independent axes: energy level (kernel), material type (section), and execution precision (REGIME). The strongest signal: `m` MIDDLE is 7.24x enriched in precision (REGIME_4) folios.

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| **908** | **MIDDLE-Kernel Correlation** (55% of MIDDLEs significantly correlate with kernel profile; k-MIDDLEs→HIGH_K, e-MIDDLEs→HIGH_E, ch/sh→HIGH_H) | 2 | B | → [C908_middle_kernel_correlation.md](C908_middle_kernel_correlation.md) |
| **909** | **Section-Specific MIDDLE Vocabularies** (96% of MIDDLEs section-specific; B=k-energy, H=k+h mixed, S=e-stability, T=h-monitoring, C=infrastructure) | 2 | B | → [C909_section_middle_vocabulary.md](C909_section_middle_vocabulary.md) |
| **910** | **REGIME-MIDDLE Clustering** (67% REGIME-specific; REGIME_4 precision shows extreme enrichment: m=7.24x, ek=3.79x, y=2.57x) | 2 | B | → [C910_regime_middle_clustering.md](C910_regime_middle_clustering.md) |

**Phase findings:**
- k-cluster (energy): k, ck, eck, ek, ke, lk, eek
- e-cluster (stability): e, ed, eed, eo, eeo, eod, eey
- h-cluster (monitoring): ch, sh, pch, opch, d
- Precision vocabulary: m, ek, y, d, s (extreme REGIME_4 enrichment)
- Balneological sections (B) use k-MIDDLEs (water heating)
- Recipe sections (S) use e-MIDDLEs (completed products)
- Text sections (T) use h-MIDDLEs (instructions)

---

### MIDDLE Semantic Deepening (C911-C912) - Phase: MIDDLE_SEMANTIC_DEEPENING

> **Summary:** Follow-up to MIDDLE_SEMANTIC_MAPPING focusing on morphological constraints. PREFIX and MIDDLE are NOT independent - each PREFIX class selects specific MIDDLE families (102 forbidden combinations). The precision vocabulary token `dam` is characterized as an anchor-class precision marker.

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| **911** | **PREFIX-MIDDLE Compatibility Constraints** (PREFIX selects MIDDLE family; qo→k-family 4.6x, da→infra 12.8x, ch/sh→e-family 2-3x; 102 forbidden combinations) | 2 | B | → [C911_prefix_middle_compatibility.md](C911_prefix_middle_compatibility.md) |
| **912** | **Precision Vocabulary - dam Token** (m MIDDLE 7.24x in REGIME_4; appears as `dam` 55% of cases; da- anchor prefix + no suffix; precision anchoring marker) | 2 | B | → [C912_precision_vocabulary_dam.md](C912_precision_vocabulary_dam.md) |

**Phase findings:**
- PREFIX × MIDDLE is constrained, not free combination
- qo- = energy prefix → k-MIDDLEs only
- da-/sa- = infrastructure prefix → iin/in/r/l only
- ch-/sh- = stability prefix → e-MIDDLEs
- `dam` is a specific lexical item for precision verification
- Paragraph-level co-occurrence is free; token-level is constrained

---

### RI Extension Mapping (C913-C915) - Phase: RI_EXTENSION_MAPPING

> **Summary:** Systematic analysis of RI (Registry-Internal) vocabulary revealed that RI is NOT independent vocabulary but is derivationally built from PP (Procedural Payload) through single-character extensions. 90.9% of RI MIDDLEs contain a PP MIDDLE as substring. Extensions encode instance-specificity, explaining why labels (which identify specific illustrated items) show 3.7x RI enrichment. Section P contains specialized pure-RI reference entries distinct from the linker system.

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| **913** | **RI Derivational Morphology** (90.9% of RI MIDDLEs contain PP as substring; extensions 71.6% single-char; 53% suffix, 47% prefix; position preferences: 'd' 89% suffix, 'h' 79% prefix, 'q' 100% prefix) | 2 | A | -> [C913_ri_derivational_morphology.md](C913_ri_derivational_morphology.md) |
| **914** | **RI Label Enrichment** (RI 3.7x enriched in labels (27.3%) vs text (7.4%); labels identify specific illustrated items requiring instance-specific vocabulary from PP+extension system) | 2 | A | -> [C914_ri_label_enrichment.md](C914_ri_label_enrichment.md) |
| **915** | **Section P Pure-RI Entries** (83% of pure-RI first-line paragraphs in Section P; 23/24 single-line; mean para 7.7; da/ot/sa prefixes NOT ct-; distinct from linker system) | 2 | A | -> [C915_section_p_pure_ri_entries.md](C915_section_p_pure_ri_entries.md) |

**Phase findings:**
- RI = PP + derivational extension (not independent vocabulary)
- True vocabulary divergence <3% when excluding linkers ('ho') and uncertain readings
- Top extensions: 'o' (16.8%), 'd' (12.3%), 'h' (11.5%), 's' (7.1%), 'e' (7.1%)
- Extension position preferences are character-specific (d->suffix, h->prefix)
- Labels need more RI because they point to specific instances
- Section P pharmaceutical content includes pure-RI reference entries

---

### RI Instance Identification System (C916) - Phase: RI_EXTENSION_MAPPING

> **Summary:** The RI derivational system functions as an **instance identification mechanism** that explains A's purpose. PP encodes general categories (shared with B execution); RI extends PP with single-character markers to identify specific instances. This resolves why A exists alongside B: A is an index that bridges general procedures to specific applications. Labels are 3.7x RI-enriched because they point to specific illustrated items, not general categories.

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| **916** | **RI Instance Identification System** (RI functions as instance identification via PP+extension derivation; PP=category, RI=specific instance; explains A as index bridging B procedures to specific applications; labels 3.7x RI-enriched for illustration identification) | 2 | A | -> [C916_ri_instance_identification_system.md](C916_ri_instance_identification_system.md) |

**Phase findings:**
- 225 PP MIDDLEs have dual use (direct AND as RI base)
- A shares 408 PP MIDDLEs with B
- A derives 324 RI MIDDLEs from PP bases
- Same conceptual vocabulary at different granularity levels
- Resolves "why does A exist if B is self-sufficient?"

---

### Extension Operational Alignment (C917-C919) - Phase: A_PP_EXTENSION_SEMANTICS

> **Summary:** RI extensions encode OPERATIONAL CONTEXT, not arbitrary identifiers. The h-extension has 82% ct-prefix correlation (vs 0% for all others, p=4.70e-90), mirroring B's ct+h linker signature. Similarly, k/t-extensions correlate with qo prefix. The d-extension is categorically distinct: it excludes -y suffixes (0% vs 46-83% for others), taking -iin/-al instead. This reveals A as an **operational configuration layer**: extensions specify which material variant to use in which operational context, parameterizing B's generic procedures.

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| **917** | **Extension-Prefix Operational Alignment** (h-extension→ct prefix 82% vs 0% for others; chi-square=404.9, p=4.70e-90; mirrors B's ct+h linker signature 75%; k/t→qo 30-46%; secondary: o→ct 5.1x, l→da 3.1x, s→sh 3.1x) | 2 | A↔B | -> [C917_extension_prefix_alignment.md](C917_extension_prefix_alignment.md) |
| **918** | **Currier A as Operational Configuration Layer** (A provides context-specific material variants via RI=PP+extension; extensions encode operational context: h=monitoring, k=energy, t=terminal, d=transition; A parameterizes B's generic procedures) | 2 | A↔B | -> [C918_currier_a_operational_configuration.md](C918_currier_a_operational_configuration.md) |
| **919** | **d-Extension Suffix Exclusion** (d-extension categorically excludes -y suffix family: 0% rate vs 46-83% for all other extensions; takes -iin/-al instead; indicates END-class grammatical behavior) | 2 | A | -> [C919_d_extension_suffix_exclusion.md](C919_d_extension_suffix_exclusion.md) |

**Phase findings:**
- h-extension EXCLUSIVELY with ct prefix (82.1%, all others 0%)
- Chi-square 404.9, p-value 4.70e-90 (extraordinarily significant)
- B grammar: ct+h = 75% (linker signature); A: h-ext→ct = 82%
- k/t extensions correlate with qo prefix (energy/terminal context)
- d-extension: NO_PREFIX (47%), excludes -y suffix (0%), takes -iin/-al
- Secondary PREFIX enrichments: o→ct 5.1x, l→da 3.1x, s→sh 3.1x, e→sh 2.9x
- Extensions are NOT arbitrary - they encode operational context
- SUPERSEDES C916's "index" interpretation with "configuration" model

---

### f57v R2 Extension Reference (C920-C922) - Phase: A_PURPOSE_INVESTIGATION

**Summary:** f57v R2 ring encodes extension-related reference with 12-character period and systematic h-exclusion.

| # | Summary | Tier | Scope | Link |
|---|---------|------|-------|------|
| **920** | **f57v R2 Extension Vocabulary Overlap** (92% of R2 chars are extension characters; only 'x' non-extension per C764; 'h' categorically absent) | 2 | AZC | -> [C920_f57v_r2_extension_vocabulary.md](C920_f57v_r2_extension_vocabulary.md) |
| **921** | **f57v R2 Twelve-Character Period** (exact 12-char period with 4 cycles + 2-char terminal; 10/12 positions invariant; only positions 7-8 variable: k/m and f/p) | 2 | AZC | -> [C921_f57v_r2_twelve_char_period.md](C921_f57v_r2_twelve_char_period.md) |
| **922** | **Single-Character AZC Ring h-Exclusion** (single-char rings 1.9% h vs multi-char 7.4%; Fisher p=0.023; systematic under-representation of monitoring context in reference content) | 2 | AZC | -> [C922_single_char_ring_h_exclusion.md](C922_single_char_ring_h_exclusion.md) |

**Phase findings:**
- f57v R2 vocabulary = 92% extension characters (minus 'x' coord marker)
- Exact 12-character repeating period on zodiac folio (4 cycles)
- Only 2 variable positions (7 and 8) across all cycles
- Single-char AZC content systematically excludes 'h' (p=0.023)
- 'h' = monitoring/linker context (C917) - excluded from scheduled/reference content
- Tier 4 speculation: 12-period may map to 12 months/zodiac signs

---

### Label Extension Bifurcation (C923) - Phase: EXTENSION_DISTRIBUTION_PATTERNS

**Summary:** Extensions bifurcate into identification (labels) and operational (text) categories.

| # | Summary | Tier | Scope | Link |
|---|---------|------|-------|------|
| **923** | **Label Extension Bifurcation (r/h Axis)** (r-extension 4.9x enriched in labels p<0.0001; h-extension 0% in labels across 11 folios p=0.0002; broader ID/OP groupings NOT confirmed - only r/h strongly differentiate; n=87 labels) | 2 | A | -> [C923_label_extension_bifurcation.md](C923_label_extension_bifurcation.md) |

**Phase findings (LABEL_INVESTIGATION validation):**
- Sample: 87 label extensions, 1,013 text extensions (3.5x larger than original)
- r-extension: 4.9x enriched in labels (17.2% vs 3.6%), p<0.0001 - STRONG
- h-extension: Categorically absent (0% across all 11 folios), p=0.0002 - STRONG
- a-extension: Moderately enriched (2.3x), p=0.012
- o, d, k, t: Do NOT differentiate - broader ID/OP grouping NOT confirmed
- Cross-folio: h-absence 100% consistent (11/11), r-enrichment 64% (7/11)
- Cramér's V = 0.136 (small effect due to o/d not bifurcating)

---

### HT-RI Shared Derivation (C924) - Phase: EXTENSION_DISTRIBUTION_PATTERNS

**Summary:** HT and RI share the same derivational morphology (PP + extension). Differentiation is at PREFIX level.

| # | Summary | Tier | Scope | Link |
|---|---------|------|-------|------|
| **924** | **HT-RI Shared Derivational Morphology** (HT MIDDLEs 97.9% contain PP; 15/16 extension chars overlap with RI; same derivational system, different PREFIX layer; HT_PREFIX + [PP+ext] vs A/B_PREFIX + [PP+ext]) | 2 | GLOBAL | -> [C924_ht_ri_shared_derivation.md](C924_ht_ri_shared_derivation.md) |

**Phase findings:**
- HT-only MIDDLEs: 97.9% contain PP (higher than RI's 90.9%)
- Extension vocabulary overlap: 15/16 characters shared with RI
- HT and RI use SAME derivational system for MIDDLEs
- PREFIX distinguishes function (HT vs A/B), MIDDLE encodes content
- Unifies RI and HT as two functional layers over shared PP substrate

---

### B Vocabulary Morphological Partition (C925) - Phase: EXTENSION_DISTRIBUTION_PATTERNS

**Summary:** B's vocabulary partitions by kernel density. B-exclusive (~66%) is pure-kernel; RI bases (~20%) are mixed composition.

| # | Summary | Tier | Scope | Link |
|---|---------|------|-------|------|
| **925** | **B Vocabulary Morphological Partition** (B-exclusive 66% has kernel density ~1.0; RI bases 20% have density 0.76; A's RI derivation draws selectively from lower-density subset; morphological not semantic partition per C522) | 2 | B, A↔B | -> [C925_b_vocabulary_morphological_partition.md](C925_b_vocabulary_morphological_partition.md) |

**Phase findings:**
- B-exclusive MIDDLEs: 885 (66.1% of B), pure kernel composition
- RI bases: 264 (19.7% of B), mixed composition
- A selectively derives from lower-density PP subset
- Per C522: composition ≠ semantic category (no "verbs vs nouns" claim)

---

### HT-RI Anti-Correlation (C926) - Phase: EXTENSION_DISTRIBUTION_PATTERNS

**Summary:** HT and RI anti-correlate at line level despite sharing derivational morphology.

| # | Summary | Tier | Scope | Link |
|---|---------|------|-------|------|
| **926** | **HT-RI Line-Level Anti-Correlation** (RI 0.48x in lines with HT; chi2=105.83 p<0.0001; same derivational system but partition space; HT tracks complexity, RI encodes instances; complementary not coordinated) | 2 | A | -> [C926_ht_ri_anti_correlation.md](C926_ht_ri_anti_correlation.md) |

**Phase findings:**
- RI rate 1.98% in lines WITH HT vs 4.16% WITHOUT HT
- Folio-level correlation weak (r=0.164, NS) - effect is positional
- Shared PP bases: Jaccard 0.060 (different bases in same folio)
- 31% dual-use PP bases confirms shared vocabulary access
- HT and RI are complementary modes, not coordinated layers

---

### HT Elevation in Labels (C927) - Phase: LABEL_INVESTIGATION

**Summary:** HT tokens are 2.42x enriched in label regions vs paragraph text, INCONSISTENT with C926's prediction.

| # | Summary | Tier | Scope | Link |
|---|---------|------|-------|------|
| **927** | **HT Elevation in Label Contexts** (HT 45.0% in labels vs 18.6% in paragraphs; 2.42x enrichment chi2=107.33 p<0.0001; INCONSISTENT with C926 prediction; labels use HT vocabulary for identification, not spare capacity) | 2 | A, HT | -> [C927_ht_label_elevation.md](C927_ht_label_elevation.md) |

**Phase findings:**
- HT rate 45.0% in labels vs 18.6% in paragraph text
- 2.42x enrichment is opposite direction from C926 prediction
- C926 anti-correlation applies to text lines, NOT label/text boundary
- Labels may use HT-derived vocabulary (PP + extension) for identification
- Supports dual origin model: RI and HT both derive from PP + extension

---

### Jar Label AX_FINAL Concentration (C928) - Phase: LABEL_INVESTIGATION

**Summary:** Jar label PP bases appear in B at 2.1x enrichment in AX_FINAL positions, suggesting jar labels identify materials deployed at maximum scaffold depth.

| # | Summary | Tier | Scope | Link |
|---|---------|------|-------|------|
| **928** | **Jar Label AX_FINAL Concentration** (jar PP bases 35.1% AX_FINAL vs 16.7% baseline; 2.1x enrichment chi2=30.15 p=4e-08; jar labels identify materials B deploys at boundary/completion positions; content labels show only 1.14x AX enrichment) | 2 | A, B, Labels | -> [C928_jar_label_ax_final_concentration.md](C928_jar_label_ax_final_concentration.md) |

**Phase findings:**
- Overall label AX enrichment is marginal (1.03x, not significant)
- JAR-SPECIFIC AX_FINAL is highly significant (2.1x, p=4e-08)
- Jar labels identify materials deployed at maximum scaffold depth
- Content labels (root/leaf) show moderate AX enrichment (1.14x)
- Supports C571: PREFIX selects role, MIDDLE carries material

---

### ch/sh Sensory Modality (C929) - Phase: GLOSS_RESEARCH

> **Summary:** ch and sh encode distinct sensory interaction modes. ch = active state testing (discrete checkpoint), sh = passive process monitoring (continuous observation). Supported by position delta (+0.120), suffix pairing (checkpoint 1.87x for ch), and operational context (sh precedes heat, ch precedes close/input/iterate). Aligns with Brunschwig's split between continuous fire monitoring and discrete product sampling.

| # | Summary | Tier | Scope | Link |
|---|---------|------|-------|------|
| **929** | **ch/sh Sensory Modality Discrimination** (ch=active test pos 0.515, sh=passive monitor pos 0.396, delta +0.120; ch+checkpoint suffix 1.87x; sh followed by heat 18.3% vs ch 10.6%; ch followed by input 1.98x, iterate 2.01x; maps to Brunschwig continuous monitoring vs discrete sampling) | 2 | B | -> [C929_ch_sh_sensory_modality.md](C929_ch_sh_sensory_modality.md) |

**Phase findings:**
- Position delta +0.120 (ch later, sh earlier) — largest prefix positional difference
- sh front-loaded: 33% in first 20% of line (monitoring starts early)
- ch checkpoint suffixes (-aiin/-ain) at 7.3% vs sh 3.9% (1.87x)
- sh -> heat (18.3%) vs ch -> heat (10.6%) — sh monitors fire
- ch -> close (1.53x), input (1.98x), iterate (2.01x) — ch gates actions
- ch/sh ratio highest in R2 (1.98x) — sealed balneum marie requires opening to test
- For folio-unique middles, delta widens to +0.156

---

### lk Section-S Apparatus Specificity (C930) - Phase: BRUNSCHWIG_APPARATUS_MAPPING

> **Summary:** lk prefix is 81.7% concentrated in section S (1.77x enrichment) — strongest section concentration of any common prefix. lk completely avoids core kernel MIDDLEs (k, t, ke = 0) and exclusively selects checkpoint/observation MIDDLEs (aiin 4.7x, ain 4.5x, ch 4.2x, ech 9.3x). Maps to Brunschwig's fire-method monitoring operations (MONITOR_DRIPS, REGULATE_FIRE), implying section S = fire-method distillation.

| # | Summary | Tier | Scope | Link |
|---|---------|------|-------|------|
| **931** | **Prefix Positional Phase Mapping** (pch 15.9x, tch 18.4x line-initial; ol 0.33x, lch 0.32x, ot 0.29x line-final; pch 25.5x par-initial; qo/ch 0.03-0.13x par-initial; temporal ordering PREP->PRE-TREAT->SEAL->EXECUTE->POST->STORE matches Brunschwig 7-phase workflow) | 2 | B | -> [C931_prefix_positional_phase_mapping.md](C931_prefix_positional_phase_mapping.md) |
| **930** | **lk Section-S Concentration and Fire-Method Specificity** (lk 81.7% in S, 1.77x enriched; 0.3% in H; avoids k/t/ke MIDDLEs completely; selects aiin 4.7x, ain 4.5x, ch 4.2x, ech 9.3x; Jaccard 0.18 vs ch/sh; never line-initial; maps to Brunschwig fire-method monitoring; implies S=fire distillation, B=balneum) | 2 | B | -> [C930_lk_section_s_concentration.md](C930_lk_section_s_concentration.md) |

**Phase findings:**
- lk section distribution: S=3.4%, C=1.2%, B=0.7%, T=0.6%, H=0.3%
- Top 6 lk folios all section S: f115v(7.8%), f111r(6.8%), f113r(6.2%), f107v(6.2%)
- MIDDLE binary partition: checkpoint MIDDLEs only, zero core kernel operators
- Jaccard similarity: lk-ch=0.18, lk-sh=0.18, ch-sh=0.82 (lk is distinct family)
- Positional: LINE_INITIAL 0.3% (never starts procedures)
- Apparatus hypothesis: S=fire methods (need drip/fire monitoring), B=balneum (need replenishment/finger test)

---

### Paragraph Execution Sequence (C932-C934) - Phase: PARAGRAPH_EXECUTION_SEQUENCE

> **Summary:** B paragraph bodies (lines 2+) show a specification-to-execution gradient. Early body lines contain rare/unique vocabulary (material parameters), late body lines contain universal vocabulary (generic control loops). Prep verbs (chop, strip, pound, gather) concentrate 2-3x in early lines. Heat operations appear before prep in 65% of paragraphs (avg position 0.079 vs 0.212), consistent with "light coals, then prep materials" parallel startup.

| # | Summary | Tier | Scope | Link |
|---|---------|------|-------|------|
| **932** | **Body Vocabulary Gradient** (RARE r=-0.97 early-to-late; UNIVERSAL r=+0.92; tokens/line 10.3->8.7 r=-0.97; terminal suffix r=-0.89; bare suffix r=+0.90; extends C842 flat-body finding to show vocabulary rarity gradient within body) | 2 | B | -> [C932_body_vocabulary_gradient.md](C932_body_vocabulary_gradient.md) |
| **933** | **Prep Verb Early Concentration** (te avg=0.394 Q0:Q4=2.7x; pch avg=0.429 Q0:Q4=2.8x; tch avg=0.424 Q0:Q4=1.9x; lch avg=0.445 Q0:Q4=1.3x; all four Brunschwig prep verbs front-load in paragraph body) | 2 | B | -> [C933_prep_verb_early_concentration.md](C933_prep_verb_early_concentration.md) |
| **934** | **Parallel Startup Pattern** (heat first 65%, prep first 27%, same line 8%; first heat avg pos=0.079, first prep avg pos=0.212; BOTH lines Q0=9.9% Q4=3.4% r=-0.94; consistent with "light coals first, prep materials while stabilizing") | 2 | B | -> [C934_parallel_startup_pattern.md](C934_parallel_startup_pattern.md) |
| **935** | **Compound Specification Dual Purpose** (line-1 compound atoms predict body simple MIDDLEs: 71.6% hit vs 59.2% random, 1.21x lift; HT compound rate 45.8% vs grammar 31.5%; 100% decomposable to core atoms; REVISES C404 "non-operational" to "operationally redundant"; weakens Tier 3 attention/practice interpretation) | 2 | B | -> [C935_compound_specification_dual_purpose.md](C935_compound_specification_dual_purpose.md) |

### ok Prefix as Vessel Domain Selector (C936) - Phase: GLOSS_RESEARCH Test 25-26

| # | Summary | Tier | Scope | Link |
|---|---------|------|-------|------|
| **936** | **ok = Vessel Domain Selector** (REVISED from "three-operation composite": ok selects vessel/apparatus as action target, MIDDLE provides action; 378 same-MIDDLE pairs confirm domain differentiation; late position mean 0.538; 15 hypotheses tested, vessel-target only coherent reading; C911 explained: vessel ops = e-family + infra, no direct heating; sister pair ok/ot = proactive/corrective apparatus management) | 2/3 | B | -> [C936_ok_three_operation_composite.md](C936_ok_three_operation_composite.md) |

**Phase findings:**
- B paragraph body is NOT flat in vocabulary composition (refines C842)
- Specification vocabulary (unique/rare MIDDLEs) concentrates in early body lines
- Execution vocabulary (universal MIDDLEs) concentrates in late body lines
- Prep verbs are specification, not execution — they front-load 2-3x
- Heat starts before prep (parallel startup), not after (sequential)
- Fire degree params (ke, kch) are uniformly distributed — ongoing, not one-time
- "Job card" model: early lines = what's different, late lines = standard loop
- **HT REVISION:** Line-1 "HT" tokens are compound operational specifications, not a non-operational layer
- HT compound MIDDLEs decompose to core atoms found in body (71.6% hit rate)
- C404 reframed: "non-operational" → "operationally redundant"
- Tier 3 attention/practice interpretation weakened

---

### MIDDLE Material Semantics (C937-C940) - Phase: MIDDLE_MATERIAL_SEMANTICS

> **Summary:** Tested whether tail MIDDLEs (rare, <15 folios) encode material-specific identity. **Verdict: WEAK** — Phase-position semantics confirmed; material-level identity NOT supported. 14 tests (4 SUPPORTED, 3 PARTIAL/WEAK, 6 NOT SUPPORTED, 1 ELABORATION). Discrimination tests (10-14) decisively favor operational interpretation: C619 holds within phases, 89.4% of zone-exclusive rare MIDDLEs are distance-1 compositional elaborations, no cross-folio material consistency. FL state marking ruled out as alternative explanation. Semantic ceiling (C120) stands with refinement.

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| **937** | **Rare MIDDLE Zone-Exclusivity** (55.1% vs 25.5% zone-exclusive, d=0.67, p=2.97e-15; rare MIDDLEs deploy in specific procedural phases; not hapax artifact) | 2 | B | -> [C937_rare_middle_zone_exclusivity.md](C937_rare_middle_zone_exclusivity.md) |
| **938** | **Section-Specific Tail Vocabulary** (42-66% section-exclusive, within/between ratio=1.40, p=1.29e-06; extends C909 to rare tail; section concentration 0.654 vs 0.438) | 2 | B | -> [C938_section_tail_vocabulary.md](C938_section_tail_vocabulary.md) |
| **939** | **Zone-Exclusive MIDDLEs Are Compositional Variants** (89.4% distance-1 from common MIDDLEs; 97.9% contain common atom; exclusive vs non-exclusive indistinguishable p=0.978; closes material-identity path) | 2 | B | -> [C939_zone_exclusive_compositional_variants.md](C939_zone_exclusive_compositional_variants.md) |
| **940** | **FL State Marking via Rare MIDDLEs FALSIFIED** (finish-exclusive FL rate=0.513 vs baseline=0.457, p=0.224; bimodal: half kernel-bearing, half FL; rules out C777 extension) | 1 | B | -> [C940_fl_rare_middle_falsification.md](C940_fl_rare_middle_falsification.md) |

**Phase findings:**
- Phase-position exclusivity is REAL (d=0.67) — different procedural phases use different operational variants
- Material-level identity NOT supported — discrimination tests (C619 retest, compositional distance, cross-folio sharing) all favor operational
- Zone-exclusive rare MIDDLEs are single-character elaborations of common MIDDLEs (89.4% distance-1)
- FL state marking ruled out as explanation for finish-zone vocabulary (bimodal, not enriched)
- Section-specific tail vocabulary extends C909 to the rare tail distribution
- C619 strengthened: unique MIDDLE behavioral equivalence holds within procedural phases
- Semantic ceiling (C120) confirmed: material encoding does NOT live in MIDDLE morphology

### Material Locus Search (C941-C948) - Phase: MATERIAL_LOCUS_SEARCH

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **941** | **Section Is the Primary Vocabulary Organizer** (ARI=0.40, NMI=0.53, p<0.0001; residual after section removal ~0; no sub-section material categories) | 2 | B | -> [C941_section_vocabulary_organizer.md](C941_section_vocabulary_organizer.md) |
| **942** | **Context-Dependent MIDDLE Successor Profiles** (45.8% significant by section after Bonferroni; section KL 2.0x > position KL; 100% MIDDLEs have section KL > position KL) | 2 | B | -> [C942_context_dependent_successors.md](C942_context_dependent_successors.md) |
| **943** | **Whole-Token Variant Coordination Carries Section Signal** (residual MI=0.105 bits after PREFIX conditioning, p=0.0; 60% persists; 97.6% MIDDLEs have V>0.2) | 2 | B | -> [C943_whole_token_variant_coordination.md](C943_whole_token_variant_coordination.md) |
| **944** | **Paragraph Kernel Sequence Stereotypy** (entropy p=0.004; section T=1.32 bits, S=2.79 bits; section-specific paragraph ordering patterns) | 2 | B | -> [C944_paragraph_kernel_sequence_stereotypy.md](C944_paragraph_kernel_sequence_stereotypy.md) |
| **945** | **No Folio-Persistent Rare MIDDLEs as Material Markers FALSIFIED** (0 rare MIDDLEs at >80% persistence; 81.8% confined to single paragraph; mean edit distance 1.33) | 1 | B | -> [C945_no_folio_persistent_material_markers.md](C945_no_folio_persistent_material_markers.md) |
| **946** | **A Folios Show No Material-Domain Routing FALSIFIED** (cosine similarity 0.997; ARI=-0.007; RI extension V=0.071; A is generic pool) | 1 | A | -> [C946_no_a_material_routing.md](C946_no_a_material_routing.md) |
| **947** | **No Specification Vocabulary Gradient FALSIFIED** (early 62.5% vs late 64.2%; difference -1.7pp; Wilcoxon p=0.632) | 1 | B | -> [C947_no_specification_vocabulary_gradient.md](C947_no_specification_vocabulary_gradient.md) |
| **948** | **Gloss Gap Paragraph-Start Enrichment** (4.03x at par_start; section H gap rate 8.6% vs B 2.4%; 16 distinct gaps all hapax) | 2 | B | -> [C948_gloss_gap_paragraph_start_enrichment.md](C948_gloss_gap_paragraph_start_enrichment.md) |

**Phase findings:**
- **Section IS the material coordinate** — vocabulary profiles, successor distributions, token variant coordination, and paragraph sequences all organize by section
- **No sub-section material markers exist** — no discrete tokens, morphological features, or positional slots carry material identity
- Material identity is **emergently encoded** in the section-level combinatorial vocabulary profile
- A folios are a generic pool (cosine 0.997) with no material-domain routing
- No specification gradient: early and late paragraph vocabulary discriminate section equally
- Gloss gaps enriched at paragraph starts (4.03x) but all distinct gaps are hapax
- Semantic ceiling (C120/C171) reinforced: material information is bound to section identity and cannot be recovered from individual tokens

### FL Resolution Test (C949-C955) - Phase: FL_RESOLUTION_TEST

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **949** | **FL Non-Executive Verdict** (6-test battery; variant NMI 97.1th pctile but fails 99.9th threshold; FL is deliberately low-impact ordered annotation layer, non-executive) | 2 | B | -> [C949_fl_non_executive_verdict.md](C949_fl_non_executive_verdict.md) |
| **950** | **FL Two-Dimensional Structure** (PREFIX x STAGE; PREFIX determines position KW p=10^-15; STAGE determines value; chi2 p=4.8x10^-82, V=0.349) | 2 | B | -> [C950_fl_two_dimensional_structure.md](C950_fl_two_dimensional_structure.md) |
| **951** | **FL-LINK Spatial Independence** (KS p=0.853; MWU p=0.289; no complementary zoning within lines; C813 is global tendency not local structure) | 2 | B | -> [C951_fl_link_independence.md](C951_fl_link_independence.md) |
| **952** | **FL Stage-Suffix Global Independence** (chi2 p=0.751; NMI p=0.657; Spearman rho=0.008; flat suffix distributions across all FL stages) | 2 | B | -> [C952_fl_suffix_independence.md](C952_fl_suffix_independence.md) |
| **953** | **ch-FL Precision Annotation Submode** (suffix NMI p=0.004, 7x global; ch-prefix FL interacts with execution morphology; sole surviving execution-level FL signal) | 2 | B | -> [C953_ch_fl_precision_submode.md](C953_ch_fl_precision_submode.md) |
| **954** | **Section T FL Enrichment** (28.4% FL vs S/B 21.2%; gradient anomaly NOT from suppression; T also shows suffix effect p=0.038) | 2 | B | -> [C954_section_t_fl_enrichment.md](C954_section_t_fl_enrichment.md) |
| **955** | **FL Killed Hypotheses Registry** (12 hypotheses falsified: active control, loops, routing, batch processing, cross-line state, testing criteria, assessment output) | 1 | B | -> [C955_fl_killed_hypotheses.md](C955_fl_killed_hypotheses.md) |

**Phase findings:**
- FL is a **non-executive annotation layer** — structurally real but largely ignored by execution grammar
- FL is **two-dimensional** (PREFIX = position, STAGE = value) with strong correlation (V=0.349)
- FL has **no control-loop role** — no LINK zoning, no suffix parameterization, no role prediction
- The sole execution-level signal is **ch-FL suffix coupling** (p=0.004), consistent with precision annotation submode
- Section T has **more FL, not less** — gradient anomaly has a different cause
- 12 execution-level hypotheses falsified with proper shuffle controls
- FL is deliberately low-impact by architectural necessity (C120, C171 compliance)

### Line Control Block Grammar (C956-C964) - Phase: LINE_CONTROL_BLOCK_GRAMMAR

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **956** | **Positional Token Exclusivity** (192/334 tokens zone-exclusive, 2.72x shuffle; 50% survive suffix-stripping; effect is STRUCTURAL per negative control) | 2 | B | -> [C956_positional_token_exclusivity.md](C956_positional_token_exclusivity.md) |
| **957** | **Token-Level Bigram Constraints** (26 mandatory, 9 forbidden; 2 genuinely token-specific: chey->chedy, chey->shedy both ENERGY; effect is STRUCTURAL) | 2 | B | -> [C957_token_bigram_constraints.md](C957_token_bigram_constraints.md) |
| **958** | **Opener Class Determines Line Length** (24.9% partial R^2 beyond folio+regime; folio+opener_token = 93.7% R^2; strongest token-level finding) | 2 | B | -> [C958_opener_determines_line_length.md](C958_opener_determines_line_length.md) |
| **959** | **Opener Is Role Marker, Not Instruction Header** (role accuracy 29.2% = 1.46x chance; token JSD not significant; free substitution within role) | 2 | B | -> [C959_opener_is_role_marker.md](C959_opener_is_role_marker.md) |
| **960** | **Boundary Vocabulary Is Open** (Gini 0.47 < 0.60; 663 tokens for 80% coverage; no closed boundary set) | 2 | B | -> [C960_boundary_vocabulary_open.md](C960_boundary_vocabulary_open.md) |
| **961** | **WORK Zone Is Unordered** (EN tau ~ 0, AX tau ~ 0; no systematic within-zone sequence; interior operations are parallel) | 2 | B | -> [C961_work_zone_unordered.md](C961_work_zone_unordered.md) |
| **962** | **Phase Interleaving Pattern** (KERNEL/LINK/FL weakly clustered, p<0.001; compliance 32.7% vs 21.7% shuffle; phases are tendencies not blocks) | 2 | B | -> [C962_phase_interleaving.md](C962_phase_interleaving.md) |
| **963** | **Paragraph Body Homogeneity** (only length progression rho=-0.23; no compositional change after length control; body lines are equivalent) | 2 | B | -> [C963_paragraph_body_homogeneity.md](C963_paragraph_body_homogeneity.md) |
| **964** | **Boundary-Constrained Free-Interior Grammar** (SYNTHESIS: grammar strength 0.500; boundaries constrained by role, interior free; system is role-complete) | 2 | B | -> [C964_boundary_constrained_free_interior.md](C964_boundary_constrained_free_interior.md) |

**Phase findings:**
- Currier B lines are **boundary-constrained control blocks with a free interior**
- **Boundaries** have positional exclusivity, mandatory bigrams, and opener-length coupling — but these are role-driven (negative control confirms)
- **Interior** (WORK zone) is unordered, phases interleave, paragraph bodies are homogeneous
- The system is **role-complete**: 49 instruction classes and 5 roles capture all syntactic structure
- Token-level effects are consequences of role membership, not independent grammatical constraints
- Only **2 genuine token-specific constraints** found: chey->chedy and chey->shedy forbidden (same ENERGY class)
- The system deliberately minimized lexical syntax to reduce cognitive load and error

### Paragraph State Collapse (C965) - Phase: PARAGRAPH_STATE_COLLAPSE

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **965** | **Body Kernel Composition Shift** (h-kernel fraction rises +0.10, e-kernel drops -0.086 through body; survives length control; composition shift not diversity collapse) | 2 | B | -> [C965_body_kernel_composition_shift.md](C965_body_kernel_composition_shift.md) |

**Phase findings:**
- **NO COLLAPSE** (0.0/7.0) — All 7 pre-registered collapse hypotheses falsified
- C963 body homogeneity comprehensively confirmed: entropy, distinct counts, rates ALL flat after length control
- Line length confound (C677) explains all raw diversity declines (rho=+0.75 with MIDDLE entropy)
- Only genuine positional signal: kernel composition shift (C965) — h-kernel rises, e-kernel drops
- The "quiet and rigid" appearance of late paragraphs is an optical illusion of line shortening

### Lane Oscillation Control Law (C966-C970) - Phase: LANE_OSCILLATION_CONTROL_LAW

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **966** | **EN Lane Oscillation First-Order Sufficiency** (markov_haz BIC=9166.3, 12 params; composite deviation 0.975 on 8 valid metrics; 2nd-order correction worsens fidelity; no hidden accumulator, no cross-line memory) | 2 | B | -> [C966_lane_oscillation_first_order_sufficiency.md](C966_lane_oscillation_first_order_sufficiency.md) |
| **967** | **Hazard Gate Duration Exactly One Token** (KL offset+1=0.098, offset+2=0.0005; chi2 offset+1 p<1e-21, offset+2 p=0.58; no class 7 vs 30 difference Fisher p=0.728; fixed 1-step pulse) | 2 | B | -> [C967_hazard_gate_one_token_duration.md](C967_hazard_gate_one_token_duration.md) |
| **968** | **Folio Drift Emergent Not Intrinsic** (Spearman rho=0.059 p=0.292; partial rho=0.030 p=0.590 controlling EN density; no REGIME shows significant drift; drift excluded from model) | 2 | B | -> [C968_folio_drift_emergent.md](C968_folio_drift_emergent.md) |
| **969** | **2nd-Order Alternation Bias Non-Load-Bearing** (CMI=0.012 bits; post-SWITCH epsilon=+0.062, post-STAY delta=-0.067; statistically significant but correction worsens composite deviation 1.427->1.495; asymmetric between lanes; soft stabilization bias) | 2 | B | -> [C969_second_order_non_load_bearing.md](C969_second_order_non_load_bearing.md) |
| **970** | **CC-Hazard Gate Priority** (hazard gate dominates when both active; Fisher p=0.36 co-occurrence; CC routing directional but subordinate; BIC penalizes CC gate delta=-32.2) | 2 | B | -> [C970_cc_hazard_gate_priority.md](C970_cc_hazard_gate_priority.md) |

**Phase findings:**
- EN lane oscillation is a **section-parameterized, first-order hysteretic two-lane control loop with transient hazard gating**
- Optimal model: section-specific Markov + 1-token hazard gate (12 parameters)
- Generative simulation reproduces 8/8 valid metrics within composite deviation 0.975
- 2nd-order alternation bias exists (CMI=0.012 bits) but is NOT generatively load-bearing
- CC routing is real but subordinate to hazard gating and not BIC-justified
- Folio drift is non-significant — excluded from model
- **Structural closure achieved**: no hidden accumulator, no cross-line memory, no regime switching

---

### Fingerprint Uniqueness (C971-C975) - Phase: FINGERPRINT_UNIQUENESS

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **971** | **Transition Asymmetry Structurally Rare** (18 depleted pairs, 100% asymmetric; p <= 0.0001 across density-matched, degree-matched, and random null ensembles N=10,000; bootstrap holdout Jaccard=0.072) | 2 | B | -> [C971_transition_asymmetry_rare.md](C971_transition_asymmetry_rare.md) |
| **972** | **Cross-Line Independence Stronger Than Random Markov** (MI=0.521 bits vs null 0.72-0.77; p=0.000 across all ensembles; first-order sufficiency and sharp gate non-discriminating at 49-class level) | 2 | B | -> [C972_cross_line_independence_rare.md](C972_cross_line_independence_rare.md) |
| **973** | **Compositional Sparsity Exceeds Low-Dimensional Models** (incompatibility 0.460 at B-line level; latent 3-5D models produce 0.001, p=0.000; hub savings 0.298 also unachievable by latent models) | 2 | B | -> [C973_compositional_sparsity_exceeds_latent.md](C973_compositional_sparsity_exceeds_latent.md) |
| **974** | **Suffix-Role Binding Structural Not Random** (chi2=3872.2; random class reassignment drops to 390, p=0.000; CC=100% suffix-less, EN=39% with 17 types; binding is class-structure property) | 2 | B | -> [C974_suffix_role_binding_structural.md](C974_suffix_role_binding_structural.md) |
| **975** | **Fingerprint Joint Uniqueness UNCOMMON** (Fisher p=7.67e-08, worst-case p=0.024; 4/11 properties discriminate universally; asymmetric depletion + hard line resets + role-suffix binding + positional role structure jointly distinctive) | 2 | B | -> [C975_fingerprint_joint_uncommon.md](C975_fingerprint_joint_uncommon.md) |

**Phase findings:**
- Voynich B 11-property statistical fingerprint is **UNCOMMON** among generic sparse categorical grammars
- Strongest discriminators: 100% transition asymmetry (F2), unusually low cross-line MI (F10)
- 4 of 11 properties non-discriminating at 49-class granularity (clustering, one-way kernel, first-order BIC, sharp gate) — these operate within roles, not across full class space
- Latent feature models (3-5D) totally fail to reproduce compositional sparsity (0.001 vs 0.460)
- Suffix-role binding confirmed as class-structure property, not frequency artifact
- Joint constellation is structurally distinctive; cannot be generated by random categorical grammars

### Minimal State Automaton (C976-C980) - Phase: MINIMAL_STATE_AUTOMATON

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **976** | **Transition Topology Compresses to 6 States** (49 classes → 6 states, 8.2x compression; preserves role integrity + depletion asymmetry; holdout-invariant 100/100 trials, ARI=0.939; generative fidelity 4/5 metrics) | 2 | B | -> [C976_transition_topology_6_states.md](C976_transition_topology_6_states.md) |
| **977** | **EN/AX Transitionally Indistinguishable at Topology Level** (38 EN/AX classes merge freely; split into S3-minor 6 classes and S4-major 32 classes by depletion constraint; AXm→AXM flow 24.4x stronger than reverse) | 2 | B | -> [C977_en_ax_transitional_merge.md](C977_en_ax_transitional_merge.md) |
| **978** | **Hub-and-Spoke Topology with Sub-2-Token Mixing** (S4/AXM universal attractor >56% from all states; spectral gap 0.894; mixing time 1.1 tokens; hazard/safe asymmetry 6.5x from operational mass) | 2 | B | -> [C978_hub_spoke_topology.md](C978_hub_spoke_topology.md) |
| **979** | **REGIME Modulates Transition Weights Not Topology** (global chi2=475.5 p=1.47e-48; 4/6 source states regime-dependent; FL_HAZ and FL_SAFE regime-independent p>0.10; R4 highest FQ scaffolding, R3 deepest AXM recurrence) | 2 | B | -> [C979_regime_modulates_weights.md](C979_regime_modulates_weights.md) |
| **980** | **Free Variation Envelope: 48 Eigenvalues, 6 Necessary States** (effective rank 48 at >0.01 threshold; constraint compression to 6 states; gap = parametric control space; S4 has 81 MIDDLEs, Gini=0.545, within-state JSD=0.365) | 2 | B | -> [C980_free_variation_envelope.md](C980_free_variation_envelope.md) |

**Phase findings:**
- Currier B execution grammar reduces to a minimal **6-state control topology** with state identities required by hazard asymmetry, FL ordering, CC routing, and REGIME-conditioned modulation
- EN and AX are **transitionally indistinguishable** at macro level — the 5-role taxonomy over-differentiates at topology layer but correctly captures morphological differences
- **Hub-and-spoke** architecture: AXM (68%) is universal attractor, FQ (18%) is secondary hub, mixing time ~1 token
- REGIME modulates **weights not structure**: same 6 states, different transition probabilities. FL markers are regime-invariant constants.
- **Three-layer architecture:** 6-state topology (control law) / 49-class grammar (instruction equivalence) / token-level MIDDLE (execution parameterization)
- Role taxonomy and dynamic constraints block the **same merges** — convergent boundary evidence
- 6-state count is **holdout-invariant** (100% of 100 trials); partition boundary instability confined to AXm/AXM split

---

### Discrimination Space Derivation (C981-C989) - Phase: DISCRIMINATION_SPACE_DERIVATION

> **Summary:** Full characterization of the MIDDLE discrimination space (972 MIDDLEs, C475 basis) through 12 tests (T1-T12). Spectral fingerprint is genuine (RARE under randomization, STABLE under bootstrap). ~101 dimensions, clustering 0.873 (+137σ). Hub eigenmode (λ₁=82) encodes frequency (ρ=-0.792); residual is a continuous curved manifold (not blocks). AZC folio cohesion is entirely hub-driven (27/27 → 0/27 after hub removal). B execution inhabits A's geometry at 37× token-level enrichment. The A→AZC→B pipeline is geometrically closed.

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **981** | **MIDDLE Discrimination Space Is a Structural Fingerprint** (972 MIDDLEs; 4/5 metrics anomalous under Configuration Model z=+17 to +137; CV < 0.055 at 20% removal; λ₁ degrades linearly; FINGERPRINT_CONFIRMED) | 2 | A | -> [C981_discrimination_space_fingerprint.md](C981_discrimination_space_fingerprint.md) |
| **982** | **Discrimination Space Dimensionality ~101** (median of 7 methods: CV-AUC plateau K=256, elbow K=96, NMF K=128, M-P 28, factored 86, PCA k_95=101; STRUCTURED_HIGH_DIMENSIONAL) | 2 | A | -> [C982_discrimination_dimensionality_101.md](C982_discrimination_dimensionality_101.md) |
| **983** | **Compatibility Is Strongly Transitive** (clustering 0.873 vs CM 0.253, z=+136.9; single most anomalous property; implies AND-style constraint intersection in structured feature space) | 2 | A | -> [C983_transitive_compatibility.md](C983_transitive_compatibility.md) |
| **984** | **Independent Binary Features Insufficient** (AND-model matches density/λ₁/eigencount/rank but clustering ceiling 0.49 vs target 0.87 at all K∈[20,200]; features must be correlated/hierarchical/block-structured) | 2 | A | -> [C984_independent_features_insufficient.md](C984_independent_features_insufficient.md) |
| **985** | **Character-Level Features Insufficient for Discrimination** (logistic AUC=0.71 vs spectral AUC=0.93; 29% gap structural; PREFIX enrichment 3.92× but spectral alignment NONE ARI=0.006; consistent with C120/C171) | 2 | A | -> [C985_character_features_insufficient.md](C985_character_features_insufficient.md) |
| **986** | **Hub Eigenmode Is Frequency Gradient** (λ₁=82.0, 4.3× next eigenvalue; hub-frequency Spearman ρ=-0.792, p≈0; hub loading monotonic with frequency band; hub axis = coverage axis C476/C755) | 2 | A | -> [C986_hub_eigenmode_frequency_gradient.md](C986_hub_eigenmode_frequency_gradient.md) |
| **987** | **Discrimination Manifold Is Continuous** (residual space: best k=5, silhouette 0.245 MIXED_BANDS, 865/972 in one cluster; gap statistic -0.014; negative silhouette at k≥12; continuous curved manifold, not blocks) | 2 | A | -> [C987_continuous_constraint_manifold.md](C987_continuous_constraint_manifold.md) |
| **988** | **AZC Folio Cohesion Is Hub-Driven** (full embedding: 27/27 coherent z=+13.26; residual: 0/27 coherent z=-2.68; folios sample frequency-coherent slices with diverse residual positions; zone C→R→S traces hub gradient) | 2 | AZC | -> [C988_azc_folio_cohesion_hub_driven.md](C988_azc_folio_cohesion_hub_driven.md) |
| **989** | **B Execution Inhabits A's Discrimination Geometry** (80.2% token-weighted A-compatible at 37× enrichment; residual cosine: compat +0.076, incompat -0.051; violations concentrate in rare MIDDLEs; section S isolated; geometric realization of C468) | 2 | A↔B | -> [C989_b_inhabits_a_geometry.md](C989_b_inhabits_a_geometry.md) |

**Phase findings (T1-T9):**
- The MIDDLE discrimination space is a **genuine structural fingerprint** — anomalous under randomization, stable under subsampling
- Dimensionality **~101** from 7 convergent methods — quantifies the "token-level parameterization" layer of C976's three-layer architecture
- **Clustering 0.873** is the killer finding — compatibility is far more transitive than degree-matched random graphs (0.25)
- **Independent binary features fail** — clustering ceiling 0.49 proves constraint features are correlated/hierarchical
- **Character features are partial** — AUC 0.71, with 29% structural gap to graph-based prediction

**Phase findings (T10-T12):**
- **Hub eigenmode = frequency gradient** — λ₁ encodes how many contexts a MIDDLE appears in, not which contexts
- **Continuous manifold** — residual space has fuzzy density bands, not discrete blocks; resolves C984's "correlated how?" question
- **AZC folio cohesion is hub-driven** — apparent folio structure (27/27 coherent) collapses entirely when frequency axis removed (0/27)
- **B inhabits A's geometry at 37× enrichment** — 80% of B's token-level execution respects A's compatibility boundaries
- **A→AZC→B pipeline is geometrically closed** — A defines the constraint surface, AZC navigates it by frequency tier, B executes within it

---

### Constraint Energy Functional (C990-C993) - Phase: CONSTRAINT_ENERGY_FUNCTIONAL

> **Summary:** Scalarization of the ~100D discrimination space into a per-line compatibility energy E(line) = mean pairwise residual cosine. B operates at elevated tension (E = -0.011, below random by 0.016, p = 10⁻¹⁰¹) — NOT minimizing energy but maintaining a specific tension level. Radial depth dominates (ρ=-0.517). e-kernel is the compatibility kernel (ρ=+0.309). REGIME_4 uniquely converges in energy (var ratio 0.28). Geometric closure established: escape rate is a projection of manifold position.

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **990** | **B Operates at Elevated Constraint Tension** (E=-0.011, shift -0.016 below random, p=10⁻¹⁰¹; EN density ρ=+0.216; QO > CHSH; R4 lowest; B does not minimize energy) | 2 | A↔B | -> [C990_elevated_constraint_tension.md](C990_elevated_constraint_tension.md) |
| **991** | **Radial Depth Dominates Line-Level Energy** (depth→E ρ=-0.517, p=10⁻¹⁶⁴; R3 deepest 1.74, C shallowest 1.45; escape→E ρ=+0.100; geometric closure triangle) | 2 | A↔B | -> [C991_radial_depth_energy_predictor.md](C991_radial_depth_energy_predictor.md) |
| **992** | **e-Kernel Is the Compatibility Kernel** (e→E ρ=+0.309, p=2×10⁻⁵⁴; k ρ=+0.103; h ρ=+0.054; high-e lines E=+0.001 vs low-e E=-0.018; confirms C105 geometrically) | 2 | A↔B | -> [C992_e_kernel_compatibility.md](C992_e_kernel_compatibility.md) |
| **993** | **REGIME_4 Uniquely Converges in Energy** (trend ρ=-0.90, p=0.037; var Q5/Q1=0.28; all other REGIMEs flat; lowest mean E=-0.014; precision = energy convergence) | 2 | B | -> [C993_regime4_energy_convergence.md](C993_regime4_energy_convergence.md) |

**Phase findings:**
- E(line) is **well-defined** (99.7% B-line coverage, properly normalized) but B runs at **elevated tension** — not minimized
- **Radial depth is the dominant predictor** (ρ=-0.517) — shallow manifold = compatible, deep = tense
- **e-kernel drives compatibility** (ρ=+0.309) — geometrically confirms e as stability anchor (C105)
- **REGIME_4 is the only REGIME that converges** — precision means progressive energy narrowing (var ratio 0.28)
- **Geometric closure**: escape rate → radial depth → energy form a coherent triangle; escape is a projection of manifold position
- B's elevated tension means constraint geometry is used **functionally**, not avoided — tension is an operating parameter

---

### B-Exclusive Geometric Integration (C994) - Phase: B_EXCLUSIVE_GEOMETRIC_INTEGRATION

> **Summary:** Binary-outcome micro-phase testing whether the 900 B-exclusive MIDDLEs (in B but not in A's 972-MIDDLE space) are geometrically subordinate or architecturally independent. All 5 tests converge to SUBORDINATE: 94% contain A atoms, 89% mean string coverage, 33× enrichment for A-compatible neighbors, 80% hapax, 81% single-folio, no material energy effect. B-exclusive MIDDLEs are morphological elaboration tails of A's discrimination geometry.

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **994** | **B-Exclusive MIDDLEs Are Geometrically Subordinate** (5/5 tests SUBORDINATE: 94% contain A atoms, 89% string coverage, 33× enrichment, 80% hapax, 81% single-folio, energy shift +0.0006 p=0.12; morphological tails not second geometry) | 2 | A↔B | -> [C994_b_exclusive_middles_subordinate.md](C994_b_exclusive_middles_subordinate.md) |

**Phase findings:**
- **94% of B-exclusive MIDDLEs contain A-space atoms** — they are superstring concatenations of A's building blocks (T1, T5)
- **String coverage 89%** — the overwhelming majority of each B-exclusive MIDDLE is composed of A atoms (T5)
- **Compatible topology** — B-exclusive co-occurrence shows 33× enrichment for A-compatible neighbors (T2)
- **Morphological tail** — 80% hapax, 94% compound, 81% single-folio (T3)
- **Energetically invisible** — no significant effect on line energy (shift +0.0006, p=0.12) (T4)
- **Expert prediction confirmed** (Possibility A: SUBORDINATE) — B-exclusive vocabulary is elaboration, not independence
- **Architecture complete** — A's 972-MIDDLE discrimination geometry is THE constraint surface; B's 900 additional MIDDLEs are morphological tails

---

### Affordance Bin Stress Test & Hazard Necessity (C995-C997) - Phases: AFFORDANCE_STRESS_TEST, BIN_HAZARD_NECESSITY

> **Summary:** Falsification-grade stress testing of 9 functional affordance bins (406 MIDDLEs) across hazard topology, lane dynamics, positional trajectory, and energy-recovery architecture. Bins show independent behavioral discrimination at p < 10^-30 on all dimensions. Forbidden topology concentrates at the HUB_UNIVERSAL↔STABILITY_CRITICAL interface (13/17 transitions involve HUB). Token-level ablation reveals 22 sparse safety buffer tokens (0.12% of corpus) that prevent forbidden pairs via lane-crossing insertion. The grammar operates in a sparse-critical-buffer regime: thick margins everywhere except 22 identified pressure points.

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **995** | **Affordance Bin Behavioral Coherence** (hazard KW H=351 p=4.6e-71; lane chi2=4556 p~0; position KW H=191 p=4.2e-37; regime chi2=887 p=8.4e-172; STABILITY_CRITICAL 0% QO; lane inertia anchors vs switchers; near-deterministic regime enrichment at MIDDLE level) | 2 | B | -> [C995_affordance_bin_behavioral_coherence.md](C995_affordance_bin_behavioral_coherence.md) |
| **996** | **Forbidden Topology at HUB-STABILITY Interface** (13/17 forbidden transitions involve HUB_UNIVERSAL; 5/17 involve STABILITY_CRITICAL; no other bin participates; 8/17 are HUB→HUB self-transitions; hazard zone = compatibility carrier meets stability commitment) | 2 | B | -> [C996_forbidden_topology_hub_stability.md](C996_forbidden_topology_hub_stability.md) |
| **997** | **Sparse Safety Buffer Architecture** (22/18085 interior tokens are safety-necessary; 0.12% buffer rate; 68% in HUB_UNIVERSAL; dominant pair chey→chedy buffered 9x; safety mechanism is QO lane-crossing in CHSH sequences; removing Bin 8 or Bin 0 induces forbidden pairs; grammar = sparse-critical-buffer regime) | 2 | B | -> [C997_sparse_safety_buffer_architecture.md](C997_sparse_safety_buffer_architecture.md) |

**Phase findings:**
- 9 affordance bins pass behavioral stress test on 5 independent dimensions — not statistical artifacts
- STABILITY_CRITICAL has absolute QO exclusion (0.0% across 3,905 tokens) with e_ratio 4x median
- Forbidden topology is a HUB↔STABILITY interface phenomenon — no other bins' MIDDLEs participate
- Lane inertia separates anchors (PRECISION 0.786, SETTLING 0.784) from switchers (ENERGY 0.396)
- Regime enrichment is near-deterministic at MIDDLE level (ENERGY=89% R1, SETTLING=93% R3, PRECISION=71% R4)
- 22 safety buffer tokens prevent forbidden pairs via lane-crossing; grammar operates with thick margins except at 22 narrow passes
- Ablation shows distributed structural importance (normalized degradation 2.28-3.50); no catastrophic single point of failure

---

### Thermal Plant Simulation (C998) - Phase: THERMAL_PLANT_SIMULATION

| # | Constraint | Tier | Scope | Details |
|---|-----------|------|-------|---------|
| **998** | **Analog Physics Does Not Force Voynich Grammar Topology** (minimal reflux simulation median 3/10 targets; null models score equally; spectral gap 1% hit rate, forbidden pairs 4%, post-overshoot cooling 2%; continuous thermal dynamics cannot produce 6-state hub-spoke topology; grammar requires discrete encoding layer beyond analog physics) | 2 | B | -> [C998_analog_physics_topology_divergence.md](C998_analog_physics_topology_divergence.md) |

**Phase findings:**
- 100 LHS-randomized thermal plant parameterizations achieve only median 3/10 Voynich targets (STRUCTURAL_DIVERGENCE)
- Null models (batch still, open heating) score equally or higher — no reflux-specific advantage
- Hardest features to produce physically: spectral gap (1%), post-overshoot cooling (2%), forbidden transitions (4%)
- Only oscillation variation (100%) and buffer rate (92%) match, both from generic P-controller dynamics
- Confirms grammar topology is convention-imposed (discrete instruction set), not physics-forced

---

### Categorical Discretization Test (C999) - Phase: CATEGORICAL_DISCRETIZATION_TEST

| # | Constraint | Tier | Scope | Details |
|---|-----------|------|-------|---------|
| **999** | **Categorical Discretization Does Not Bridge Voynich Topology Gap** (5 physical strategies + 1 random null across 100 parameterizations; best physical 3/9 metrics toward Voynich = random 3/9; zero forbidden transitions from any strategy; hub mass degrades under all strategies; spectral gap is discretization artifact; Voynich discreteness is engineered abstraction, not categorization artifact) | 2 | B | -> [C999_categorical_discretization_insufficient.md](C999_categorical_discretization_insufficient.md) |

**Phase findings:**
- Categorical discretization of THERMAL_PLANT_SIMULATION continuous data adds nothing over the continuous baseline (C998)
- No physical discretization strategy outperforms random label assignment
- Zero null-calibrated forbidden transitions from any of 600 strategy × parameterization combinations
- Legality imposition layer: physically-motivated rules are either tautological (lane_temp: 8/8 trivially absent) or violated (q_phase: 20.6% violation rate)
- Closes the "categorization might explain it" pathway — encoding layer must be hypothesized from grammar's internal structure

---

### HUB Role Decomposition (C1000) - Phase: HUB_ROLE_DECOMPOSITION

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1000** | **HUB_UNIVERSAL Decomposes Into Functional Sub-Roles** (23 HUB MIDDLEs → 4 sub-roles: HAZARD_SOURCE(6), HAZARD_TARGET(6), SAFETY_BUFFER(3), PURE_CONNECTOR(8); behaviorally homogeneous (0/14 KW sig) but functionally distinct; 17/17 forbidden transitions involve HUB (perm p=0.0000); PREFIX lane chi²=12957 V=0.689; safety buffers 3.8x qo-enriched; regime clustering sil=0.398 at k=4; corrects C996 from 13/17 to 17/17) | 2 | B | -> [C1000_hub_decomposable_subroles.md](C1000_hub_decomposable_subroles.md) |

**Phase findings:**
- HUB_UNIVERSAL is behaviorally homogeneous on affordance signatures but structurally decomposable by hazard participation
- ALL 17 forbidden transitions involve HUB MIDDLEs (corrects C996's 13/17 estimate)
- PREFIX creates dramatic lane separation within HUB (Cramér's V=0.689)
- `l` and `ol` serve triple role: HAZARD_SOURCE + HAZARD_TARGET + SAFETY_BUFFER
- Safety buffers are 81.6% QO lane at token level

---

### PP Information Decomposition (C1001) - Phase: PP_INFORMATION_DECOMPOSITION

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1001** | **PREFIX Dual Encoding — Content and Positional Grammar** (PREFIX encodes both content (lane, class, suffix) and line position; PREFIX R²=0.069 ≈ MIDDLE R²=0.062 for position; 20/32 PREFIXes non-uniform positional profiles; po=86% initial, ar=61% final; PREFIX positional grammar regime-invariant for 7/7 major PREFIXes; sh→qo enrichment +20.5σ reveals line sequencing; I(MIDDLE_t; PREFIX_{t+1})=0.499 bits cross-component dependency) | 2 | B | -> [C1001_prefix_dual_encoding.md](C1001_prefix_dual_encoding.md) |

**Phase findings:**
- MIDDLE is primary operator for suffix/regime; PREFIX is co-equal for position (51.3% dominance)
- PREFIX defines line zones: INITIAL (po, dch, so, tch, sh), CENTRAL (qo, ch, ok), FINAL (ar, al, or, BARE, ot)
- sh→qo is the strongest PREFIX sequence enrichment (+20.5σ) — lines open with sh, continue with qo
- Current MIDDLE strongly predicts next PREFIX (0.499 bits cross-component MI)
- PREFIX positional grammar is regime-invariant (REGIME main effect H=0.27, p=0.97)
- Full PP (PREFIX×MIDDLE interaction) explains 16.8% of position variance

---

### SUFFIX Positional and Sequential Grammar (C1002) - Phase: SUFFIX_POSITIONAL_STATE_MAPPING

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1002** | **SUFFIX Positional and Sequential Grammar** (8/22 suffixes non-uniform positional profiles vs PREFIX 20/32; R² suffix=0.027 vs PREFIX=0.069; extreme specialists am 88% line-final, om 88% final; SUFFIX sequential grammar chi²=2896 V=0.063 comparable to PREFIX V=0.060; edy→edy +14.3σ self-repetition dominance; I(SUFFIX; PREFIX_{t+1} \| MIDDLE) = -0.074 bits — zero cross-token signal; C932 category paragraph gradients do NOT decompose to individual suffixes) | 2 | B | -> [C1002_suffix_positional_sequential_grammar.md](C1002_suffix_positional_sequential_grammar.md) |

**Phase findings:**
- SUFFIX has positional grammar weaker than PREFIX but sequential grammar of comparable strength
- Extreme line-final specialists: am/om (88% Q5), ry (68%), ly (48%)
- Self-repetition dominates sequential structure (edy→edy +14.3σ, dy→dy +11.2σ)
- SUFFIX carries zero unique cross-token predictive signal beyond MIDDLE class
- Category-level paragraph gradients (C932) are emergent, not decomposable to individual suffixes

---

### TOKEN Pairwise Composite — No Three-Way Synergy (C1003) - Phase: PREFIX_MIDDLE_SUFFIX_SYNERGY

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1003** | **TOKEN is Pairwise Composite — No Three-Way Synergy** (Co-Information non-significant on all 4 targets; REGIME Co-I = -0.011 bits below 0.02 threshold; R² three-way increment = 0.0001; BUT token atomicity confirmed: full-token lookup beats naive Bayes by +0.097 bits/token, t=8.64, p=0.001; synergy uniform across suffix strata; TOKEN is atomic lookup unit for pairwise interactions, not three-way structure) | 2 | B | -> [C1003_token_pairwise_composite.md](C1003_token_pairwise_composite.md) |

**Phase findings:**
- Zero three-way synergy in Co-Information (best: REGIME -0.011 bits, below threshold)
- Zero three-way interaction in variance (R² increment = 0.0001)
- TOKEN IS an atomic lookup unit (+0.097 bits/token over independence) but through pairwise correlations
- Synergy uniform across EN/AX/depleted strata — not concentrated in suffix-rich tokens
- Models need only pairwise component interactions, not three-way terms

---

### 49-Class Sufficiency Confirmed (C1004) - Phase: FULL_TOKEN_TRANSITION_DEPTH

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1004** | **49-Class Sufficiency Confirmed — No Hidden Suffix State** (Token-level Markov 38% worse than 49-class; only 1/17 classes shows suffix-differentiated transitions (JSD); H reduction from suffix conditioning = 0.259 bits (5.6%) — present but modest; no fourth architectural layer; 49-class grammar is the correct resolution for transition dynamics) | 2 | B | -> [C1004_49class_sufficiency_confirmed.md](C1004_49class_sufficiency_confirmed.md) |

**Phase findings:**
- Token-level Markov (101 states) overfits: perplexity 39.73 vs 49-class 28.76
- 94% of testable classes show no suffix-differentiated transitions
- Suffix conditioning reduces entropy by 5.6% — real but insufficient to justify doubled state space
- Combined with C1002 (no cross-token signal) and C1003 (no three-way synergy): grammar is saturated
- 49-class instruction grammar captures all exploitable sequential structure

---

### Bubble-Point Oscillation Falsified (C1005) - Phase: BUBBLE_POINT_OSCILLATION_TEST

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1005** | **Bubble-Point Oscillation Falsified — Duty-Cycle Pattern** (QO run lengths do NOT decrease with REGIME intensity; alternation rate decreases rho=-0.44 p<0.0001; effect is section-driven T7 rho=0.011 p=0.924 after section control; modest REGIME residual only in double partial rho=0.278 p=0.016; REGIME_4 has anomalously long CHSH runs 2.19 consistent with C494 precision axis; eliminates physics-driven switching, supports operator-driven duty cycles) | 4 | B | -> [C1005_bubble_point_falsified.md](C1005_bubble_point_falsified.md) |

**Phase findings:**
- Bubble-point oscillation prediction falsified: hotter REGIMEs oscillate slower, not faster
- Section is the primary oscillation pace-setter (confirms C650), not REGIME
- REGIME_4 extended CHSH runs (2.19) = precision monitoring (C494, F-BRU-017)
- Distillation narrative unaffected: operator-driven duty cycles fit Brunschwig better than physics-driven switching

---

### REGIME Dwell Architecture (C1006-C1007) - Phase: REGIME_DWELL_ARCHITECTURE

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1006** | **Macro-State Dwell Non-Geometricity is Topology Artifact** (first-order Markov null reproduces AXM dwell KS D=0.020 p=0.074; simulated data also non-geometric chi2=5097; 49-class runs mean=1.054 nearly all length-1; compositional drift within AXM runs chi2=52.09 p=0.010; Weibull k=1.55 REGIME-invariant range=0.096; non-geometricity correlates with compression ratio: AXM 32-class strongest, FQ 4-class moderate, FL_HAZ 2-class geometric) | 2 | B | -> [C1006_dwell_topology_artifact.md](C1006_dwell_topology_artifact.md) |
| **1007** | **AXM Exit-Boundary Gatekeeper Subset** (specific classes 3-10x enriched at run exit boundaries chi2=178.21 p<0.0001; top enriched: class 22 at 9.58x, class 21 at 4.25x, class 15 at 3.08x; AXM exits to FQ 57.1%, enters from FQ 55.1%; FQ is principal interchange state) | 2 | B | -> [C1007_axm_gatekeeper_subset.md](C1007_axm_gatekeeper_subset.md) |

**Phase findings (T1-T8):**
- T1: REGIME selectively stretches AXm dwell only (rho=+0.306, p=0.007 section-controlled)
- T2: Longer dwell = lower hazard density (rho=-0.416, p=0.0001)
- T3: Shallower MIDDLEs = longer dwell (rho=-0.318, p=0.004), independent of REGIME
- T4: HT density null (p=0.109); LINK density positive (rho=+0.389, p=0.0003)
- T5+T5b: Non-geometric AXM dwell is topology artifact (first-order null reproduces)
- T6: Non-geometricity correlates with class compression (AXM>FQ>FL_HAZ)
- T6b: Compositional drift within AXM runs (C977 internal structure)
- T7: Weibull k=1.55 REGIME-invariant; REGIME modulates scale only (C979 reinforced)
- T8: Gatekeeper subset at AXM exit boundaries (chi2=178.21, p<0.0001)

---

### AXM Gatekeeper Investigation (C1008-C1009) - Phase: AXM_GATEKEEPER_INVESTIGATION

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1008** | **AXM Directional Gating Mechanism** (entry/exit asymmetry chi2=152.60 p<0.0001; 5 AUXILIARY classes {15,20,21,22,25} enriched 2-10x at exit only; lower transition entropy 4.12 vs 4.56 bits p=0.016; survives mid-line control p=0.002; not structural bridges betweenness p=0.514; REGIME-contextual class identity) | 2 | B | -> [C1008_axm_directional_gating.md](C1008_axm_directional_gating.md) |
| **1009** | **AXM Exit Hazard-Target Compositional Curvature** (HAZARD_TARGET density increases from ~10% at t-3 to ~16% at exit rho=-0.055 p=0.0001; no radial depth gradient p=0.098; exit sub-role composition different chi2=13.89 p=0.003; compositional not spectral mechanism) | 2 | B | -> [C1009_axm_exit_hazard_curvature.md](C1009_axm_exit_hazard_curvature.md) |

**Phase findings (T1-T9):**
- T1: Directional gating - entry/exit class asymmetry (chi2=152.60, p<0.0001)
- T2: No exit routing specificity (p=0.286) - gatekeepers are destination-agnostic
- T3: Mid-line positional control passed (chi2=58.42, p=0.002) - genuine gating
- T4: No duration prediction (KW p=0.128)
- T5: REGIME-variable gatekeeper identity (mean cross-rho=-0.245)
- T6: HAZARD_TARGET sub-role enriched at exit (chi2=13.89, p=0.003)
- T7: Lower gatekeeper entropy (4.12 vs 4.56 bits, p=0.016) - routing switches
- T8: Hazard-target compositional curvature toward exit (rho=-0.055, p=0.0001); no depth gradient
- T9: Gatekeepers are NOT structural bridges (betweenness p=0.514)
- T10: No constrained sub-role exit motif (pre-GK p=0.940, exit entropy matches baseline)
- T11: REGIME does NOT modulate curvature slope (rho=+0.800, p=0.200) - shape-invariant

---

### Macro-Automaton Necessity (C1010) - Phase: MACRO_AUTOMATON_NECESSITY

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1010** | **6-State Macro-Automaton is Minimal Invariant-Preserving Partition** (k<6 breaks role integrity and depletion separation: k=5 has 2 violations, k=4 has 5, k=3 has 9; AIC minimum at k=6 with ~110 point advantage over k=5; k>6 preserves constraints but adds no structural benefit; depletion gap persists at all k z=7-9 — 49-class phenomenon; independent spectral clustering ARI=0.059 — partition is structurally forced not spectrally natural) | 2 | B | -> [C1010_6state_minimal_invariant_partition.md](C1010_6state_minimal_invariant_partition.md) |

**Phase findings (T1-T6):**
- T1: Constraint retention = 1.0 at k>=6, degrades below (dep_cross: 0.789 at k=5, 0.263 at k=3)
- T2: AIC minimum at k=6 (91299); BIC minimum at k=3 (parsimony); LL jumps 70 points at k=6
- T3: k=5 first violation is FQ role merge + depletion (9,33); each k step adds distinct violations
- T4: Five 7-state alternatives all fail to close depletion gap (z=7.24-7.58)
- T5: Spectral clustering produces structurally different partitions (max ARI=0.081); role purity 0.0-0.5
- T6: Verdict STRUCTURALLY_FORCED

---

### Geometric Macro-State Footprint (C1011) — Phase: GEOMETRIC_MACRO_STATE_FOOTPRINT

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1011** | **Discrimination Manifold and Macro-Automaton are Geometrically Independent** (only 85/972 MIDDLEs (8.7%) bridge A manifold → B grammar; macro-state silhouette = -0.126 z=-0.96 p=0.843 — no geometric footprint; forbidden transitions not at geometric boundaries ratio=0.991 p=1.0; HUB MIDDLEs peripheral not central norm 2.31 vs 0.76 p≈0; HUB sub-roles not geometrically distinct p=0.577; 3/6 pre-registered predictions passed; manifold = A-level compatibility, automaton = B-level transition topology — complementary not redundant) | 2 | A→B | -> [C1011_geometric_independence.md](C1011_geometric_independence.md) |

**Phase findings (T1-T6):**
- T1: Eigenvector embedding of 972×972 compatibility matrix; hub eigenmode λ₁=81.98 removed; 100D residual space
- T2: 85 bridging MIDDLEs; silhouette -0.126 (z=-0.96, p=0.843); all per-state silhouettes negative except AXm (+0.12)
- T3: 2/17 forbidden transitions representable; distance ratio 0.991 (p=1.0) — not at geometric boundaries
- T4: HUB MIDDLEs farther from origin (2.31 vs 0.76, p=2.7e-16); sub-roles not distinct (p=0.577)
- T5: Affordance bins × macro-states = many-to-many; dominated by AXM (75% of mapped MIDDLEs)
- T6: Verdict GEOMETRIC_INDEPENDENCE — 3/6 predictions passed

---

### PREFIX Macro-State Enforcement (C1012) — Phase: PREFIX_MACRO_STATE_ENFORCEMENT

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1012** | **PREFIX is Macro-State Selector via Positive Channeling, Not Negative Prohibition** (76.7% entropy reduction z=1139 p≈0; many PREFIXes 100% single-state; but 102 prohibitions NOT cross-state targeted 23.2% vs 27.8% null z=-1.58; forbidden transitions not preferentially backed 38.9% vs 46.2% null; positional mediation 39.9%; EN PREFIXes 100% AXM+AXm; FL_HAZ+CC prohibition enrichment 2.14x; enforcement is inclusion-based not exclusion-based) | 2 | B | -> [C1012_prefix_macro_state_selectivity.md](C1012_prefix_macro_state_selectivity.md) |

**Phase findings (T1-T5):**
- T1: PREFIX macro-state entropy reduction 76.7% (chi2=31500, p≈0); I(PREFIX;macro-state)=0.876 bits; 10+ PREFIXes at 100% concentration
- T2: 56 classifiable prohibitions — 13 cross-state (23.2%), 14 within-state, 29 mixed; z=-1.58 below null
- T3: 7/18 depleted pairs morphologically backed (38.9%); null=46.2%; z=-0.61 — not enriched
- T4: I(position;macro-state)=0.0113 bits (z=44.78); PREFIX mediates 39.9%; AXM declines Q1→Q4
- T5: Verdict PARTIAL_ENFORCEMENT — 3/6 predictions passed

---

### Bridge MIDDLE Selection Mechanism (C1013) — Phase: BRIDGE_MIDDLE_SELECTION_MECHANISM

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1013** | A->B Vocabulary Bridge is a Topological Generality Filter | 2 | A->B | → [C1013_bridge_topological_selection.md](C1013_bridge_topological_selection.md) |

**Phase findings (T1-T6):**
- T1: 15/17 predictors significant (Bonferroni); frequency 55x, folio_spread 26x, compat_degree 12x, hub_loading 6x, length 0.55x
- T2: Frequency-only AUC = 0.978 — near-perfect prediction of bridge status
- T3: Full multivariate AUC = 0.904 on 125 valid MIDDLEs; structural features do not improve beyond frequency
- T4: Affordance bin chi2=479.5 (p=1.4e-97); HUB_UNIVERSAL 23/23=100% (11.44x); 4 bins at 0% (725 MIDDLEs)
- T5: Bridge profile: shorter (2.27 vs 4.11), atomic (67% vs 26%), AXM-dominated (75.3%)
- T6: Verdict TOPOLOGICAL_SELECTION — 5/6 predictions passed; bridging is a generality filter

---

### Survivor-Set Geometry Alignment (C1014) — Phase: SURVIVOR_SET_GEOMETRY_ALIGNMENT

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1014** | Discrimination Manifold Encodes Viability Structure via Bridge Backbone | 2 | A->B | -> [C1014_manifold_viability_alignment.md](C1014_manifold_viability_alignment.md) |

**Phase findings (T1-T6):**
- T1: MIDDLE Jaccard vs centroid cosine Spearman r=0.914 (Mantel p=0.001, z=-102.66); 1,528 records, 1.17M pairs
- T2: Hub-removed r=0.914 STRONGER than hub-included r=0.887 (ratio=1.031); viability in residual geometry not frequency
- T3: Size-controlled partial r=-0.916 (retention=100.1%); zero size confounding
- T4: Class-level Mantel r=0.622 (p=0.001, z=-51.72); propagates through MIDDLE->class mapping
- T5: Bridge-only r=0.905 (91% of signal), non-bridge r=0.194 (21%); viability mediated by bridge backbone
- T6: Verdict PARTIAL_ALIGNMENT — 4/6 predictions passed; manifold is viability landscape via bridge backbone

---

### PREFIX Composition State Routing (C1015) — Phase: PREFIX_COMPOSITION_STATE_ROUTING

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1015** | **PREFIX-Conditioned Macro-State Mutability with FL-Specific Routing Asymmetry** (da unique FL router OR=126.67 p≈0 routes both FL_HAZ+FL_SAFE 5:5; ar pure FL_SAFE selector 5/5 p≈0; 41.0% entropy reduction z=17.6 p≈0 operationalizes C661/C1012; mean purity 0.862 z=3.8 p=0.0001; 6×6 transition matrix: AXM attractor self=0.697 pull=0.642; FL_SAFE NOT absorbing self=0.023 return=117.7 steps; CC pure initiator self=0.041; spectral gap=0.896 mixing=1.1 steps; stationary≈empirical dev=0.012; MDL-optimal single component at corpus scale rank 1/4 33.9% compression) | 2 | B | -> [C1015_prefix_composition_state_routing.md](C1015_prefix_composition_state_routing.md) |

**Phase findings (T1-T8):**
- T1: State-change rate 77.8% vs 73.0% null (p=0.34) — FAIL (AXM dominance inflates null; informative)
- T2: PREFIX entropy reduction 41.0% (z=17.6, p≈0); operationalizes C661/C1012 at macro-state level
- T3: da unique FL router (OR=126.67, p≈0); 5:5 HAZ:SAFE; only PREFIX in both FL states
- T4: ar 100% FL_SAFE (5/5, binomial p≈0 vs 2.5% base rate)
- T5: Mean purity 0.862 vs 0.780 null (z=3.8, p=0.0001)
- T6: Full 6×6 transition matrix — AXM attractor (0.697), FL_SAFE fleeting (0.023), CC initiator (0.041), ergodic (gap=0.896)
- T7: MDL compression — PREFIX rank 1/4 at corpus scale (N=16,054); 33.9% compression; BIC-optimal single component
- T8: Generative sufficiency — FAIL (r=0.963 but R²=-4.04; PREFIX selects states but can't alone regenerate dynamics; C1003 pairwise interaction required)
- Verdict: COMPOSITION_ROUTING_CONFIRMED — 6/8 passed (T1/T8 informative nulls)

---

### Folio-Level Macro-Automaton Decomposition (C1016) — Phase: FOLIO_MACRO_AUTOMATON_DECOMPOSITION

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1016** | **Folio-Level Macro-Automaton Decomposition with Dynamical Archetypes** (6 dynamical archetypes cross-cut 4 REGIMEs ARI=0.065; forgiveness = AXM attractor strength rho=0.678 6 Bonferroni-significant features; REGIME+section explain only 33.7% of transition variance 66.3% program-specific; 72/82 folios with N≥50 transitions) | 2 | B | -> [C1016_folio_macro_automaton_decomposition.md](C1016_folio_macro_automaton_decomposition.md) |

**Phase findings (T1-T8):**
- T1: 72/82 folios with N≥50 transitions; 13,645 total matches C1015/T6; AXM occupancy CV=0.160, FL_SAFE CV=1.040
- T2: 6 archetypes (silhouette=0.185); ARI(REGIME)=0.065 (near-zero); ARI(section)=0.185 (weak); "strong attractor" (AXM self=0.82) to "active interchange" (AXM self=0.47)
- T3: C458 realization — FAIL (hazard CV=1.814, recovery CV=0.289; C458 clamping is aggregate-level not transition-level; informative)
- T4: Forgiveness decomposition — 6 Bonferroni-significant features: AXM occ (0.678), AXM self (0.651), FQ occ (-0.563), FQ→AXM (0.559), AXM→FQ (-0.522), FQ self (-0.453)
- T5: Restart signature — f57r FQ depressed z=-2.06 (constrained excursion space); f82v AXM elevated z=+1.93
- T6: Variance decomposition — REGIME eta²=0.149, section eta²=0.243, combined=0.337, residual=0.663
- T7: Geometry/topology independence — ARI(manifold clusters, archetypes)=0.163; LOO accuracy=0.444 vs 0.167 chance; vocabulary geometry weakly predicts but cannot determine archetypes
- T8: Bridge conduit test — bridge-only ARI=0.141 vs non-bridge ARI=0.037 (3.8x); bridge backbone carries most geometry→dynamics information; bridge density anti-correlated with AXM self (rho=-0.308)
- Verdict: FOLIO_DECOMPOSITION_CONFIRMED — 7/8 passed (T3 informative null)

---

### Macro-Dynamics Variance Decomposition (C1017) — Phase: MACRO_DYNAMICS_VARIANCE_DECOMPOSITION

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1017** | **Macro-State Dynamics Decompose into PREFIX Routing, Hazard Density, and Bridge Geometry** (78.7% within-MIDDLE entropy reduction z=65.59; 19.9% positional, 80.1% genuine routing; REGIME-invariant ratio=1.06; PREFIX+hazard ΔR²=0.115 beyond REGIME+section; bridge PC1 ΔR²=0.063 p=0.003; interaction ΔR²=0.030 weak per C1003; SUFFIX uncorrelated p=0.280 per C1004; 40.1% non-linear residual with archetype-specific slope profiles) | 2 | B | -> [C1017_macro_dynamics_variance_decomposition.md](C1017_macro_dynamics_variance_decomposition.md) |

**Phase findings (T1-T6, T5b, T5c):**
- T1: MIDDLE-conditioned PREFIX routing — 78.7% entropy reduction within same MIDDLE (z=65.59, p≈0); non-AXM spanning 85.9%
- T2: Positional null — 19.9% positional contribution; 80.1% genuine morphological routing (z=41.78, p≈0)
- T3: REGIME stratification — FAIL (ratio=1.06; PREFIX routing is REGIME-invariant; informative)
- T4: Bridge density constant at 1.0 (85/87 B MIDDLEs are bridges); hazard density differentiates archetypes (eta²=0.228, p=0.004); gatekeeper overlap 24.7%
- T5: Variance decomposition — REGIME+section R²=0.420; +PREFIX ΔR²=0.051; +hazard ΔR²=0.061; combined R²=0.534; interaction ΔR²=0.030 (weak)
- T5b: Archetype-stratified models — slopes differ across archetypes (β_PREFIX flips in arch.5, β_hazard flips in arch.6); mean within-archetype R²=0.230
- T5c: Geometric bridge feature — bridge PC1 rho=-0.459 (p=0.00005); ΔR²=0.063 (F=9.58, p=0.003); bridge geometry is load-bearing dynamics predictor
- T6: Residual — SUFFIX uncorrelated (p=0.280); archetype captures non-linear residual (F=6.71, p<0.0001)
- Verdict: DYNAMICS_DECOMPOSED — 8/9 passed (T3 informative null)

---

### Archetype Geometric Anatomy (C1018) — Phase: ARCHETYPE_GEOMETRIC_ANATOMY

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1018** | **Archetype Geometric Anatomy — Slope Anomalies, Bridge PC1 Decomposition, and HUB Sub-Role Differentiation** (archetype 5 PREFIX slope CI spans zero at n=7; archetype 6 SAFETY_BUFFER enriched 1.7x p=0.003; bridge PC1 partially redundant with hub frequency rho=0.568; PC1 = HUB_UNIVERSAL↔STABILITY_CRITICAL gradient; 8 discriminator features across 5 families; k_frac strongest F=15.81; archetypes 5/6 geometrically distinct p=0.006) | 2 | B | -> [C1018_archetype_geometric_anatomy.md](C1018_archetype_geometric_anatomy.md) |

**Phase findings (T1-T5):**
- T1: Archetype structural profiling — **PASS** (archetypes 5/6 NOT section-dominated; section×arch chi2=60.28 p=0.000006 V=0.457)
- T2: Bootstrap validation — FAIL (arch 5 PREFIX CI [-0.054,+0.203] spans zero; arch 6 hazard perm p=0.014 but CI spans zero; informative)
- T3: Bridge PC1 decomposition — MIXED (hub frequency rho=0.568 exceeds 0.5 threshold; PC1=HUB↔STABILITY gradient; ANOVA F=3.56 p=0.006)
- T4: Discriminator features — **PASS** (8 significant: k_frac F=15.81, SAFETY_BUFFER F=11.37, HAZARD_TARGET F=5.73, fl_ratio F=5.51, QO F=5.47)
- T5: Unified hypothesis — **SUPPORTED** (arch 5 vs 6 PC1: U=174 p=0.006; mediation weak)
- Verdict: ARCHETYPE_ANATOMY_UNIFIED — 5/7 passed (P2 sample size, P3 partial re-derivation)

### CP Factor Characterization (C1021) — Phase: CP_FACTOR_CHARACTERIZATION

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1021** | **CP Factor Characterization — Tensor Factors Are Frequency-Dominated, Rank Is Continuous, Tensor-Automaton Orthogonality Is Complete** (Factor 2 rho=-0.750 with AXM is frequency gradient rho=0.854; gatekeeper cosine=0.059; Factor 3 AXM-orthogonal captures frequency cosine=0.648; CV saturates at rank 4; constrained ARI=0.007 WORSE than unconstrained 0.050; z=-0.22 vs null) | 2 | B | -> [C1021_cp_factor_characterization.md](C1021_cp_factor_characterization.md) |

**Phase findings (Sub-1 + Sub-2 + Sub-3):**
- S1: Gatekeeper cosine — FAIL (0.059; Factor 2 does NOT encode C1007 gating)
- S2: Frequency null — FAIL (rho=0.854; Factor 2 IS a frequency gradient)
- S3: Factor 3 structural dimension — **PASS** (frequency cosine=0.648; captures AXM-orthogonal frequency)
- S4: PREFIX selectivity — **PASS** (mean Gini=0.803; strong factor-PREFIX correspondence)
- R1: Rank-8 boundary — FAIL (ΔR² ratio 8/6 = 1.023)
- R2: CV gap — FAIL (rank-8 minus rank-6 = 0.004)
- R3: Diminishing returns — **PASS** (ΔR² gap 10-8 = 0.023 < 0.03)
- R4: Compliance-rank — FAIL (Spearman=0.516)
- C1: Constrained ARI — FAIL (0.007 < unconstrained 0.050; constraint filtering makes it WORSE)
- C2: z-score — FAIL (-0.22; below null)
- C3: Reconstruction — **PASS** (variance=0.970)
- Verdict: FREQUENCY_ARTIFACT+FACTOR3_IDENTIFIED; RANK_CONTINUOUS; ORTHOGONAL_CONFIRMED — 4/11 passed

### Paragraph Macro-Dynamics (C1022) — Phase: PARAGRAPH_MACRO_DYNAMICS

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1022** | **Paragraph Macro-Dynamics — 6-State Automaton Does Not Differentiate Paragraph Structure** (Header AXM +2.8pp not CC/AXm, p=0.007; spec→exec delta +1.4pp sub-threshold p=0.037; gallows 100% AXM/AXm, zero CC; qo/chsh both >98% AXM; entropy decreases with ordinal rho=-0.215 p=0.007; AXM self-transition Spearman rho=0.207 p=0.011 but binary p=0.121) | 2 | B | -> [C1022_paragraph_macro_dynamics.md](C1022_paragraph_macro_dynamics.md) |

### Structural Necessity Ablation (C1023) — Phase: STRUCTURAL_NECESSITY_ABLATION

| ID | Description | Tier | Scope | Details |
|----|-------------|------|-------|---------|
| **1023** | **Structural Necessity Ablation — PREFIX Routing Is Sole Load-Bearing Macro Component** (PREFIX→state content routing: 78-81% of non-random structure destroyed by shuffle+reassignment; FL merge: -0.34% spectral gap; gatekeeper JSD=0.0014, z=-0.70 vs null; within-state routing: 0% structure loss; REGIME pooling: 1.1% gap difference; hierarchy: PREFIX routing >> FL ≈ gatekeepers ≈ REGIME; 3/6 pre-registered predictions correct on verdict, overall hierarchy confirmed) | 2 | B | -> [C1023_structural_necessity_ablation.md](C1023_structural_necessity_ablation.md) |

### Structural Directionality (C1024) — Phase: STRUCTURAL_DIRECTIONALITY

| ID | Description | Tier | Scope | Details |
|----|-------------|------|-------|---------|
| **1024** | **Structural Directionality — MIDDLE Carries Execution Asymmetry, PREFIX Is Symmetric Router** (MIDDLE asymmetry 0.070 bits, PREFIX 0.018 bits, ratio 0.25x; FL role highest per-class JSD 0.311; class-level bigram JSD=0.089 confirming C886; null control retains 64% of JSD from sparsity; resolves C391/C886 tension: PREFIX symmetric routing + MIDDLE directional execution = symmetric constraints with directional probabilities; 1/5 predictions correct) | 2 | B | -> [C1024_structural_directionality.md](C1024_structural_directionality.md) |

**Phase findings (6 tests):**
- T1: Header vs body — FAIL (AXM elevated +2.8pp, not CC/AXm; informative)
- T2: Spec vs exec — FAIL (direction correct but +1.4pp sub-threshold)
- T3: AXM self-transition by ordinal — FAIL (Spearman p=0.011 but binary p=0.121; underpowered)
- T4: Gallows CC enrichment — FAIL (gallows are 100% AXM/AXm scaffold; informative)
- T5: Entropy by ordinal — **PASS** (rho=-0.215, p=0.007; late paragraphs more concentrated)
- T6: qo/chsh macro-state — FAIL (both >98% AXM; C863 gradient is within-AXM; informative)
- Verdict: PARAGRAPH_MACRO_DYNAMICS_NEGATIVE — 1/6 passed. Paragraph dynamics operate within AXM, below the macro-automaton's resolution floor.

---

### Generative Sufficiency (C1025) — Phase: GENERATIVE_SUFFICIENCY

| ID | Description | Tier | Scope | Details |
|----|-------------|------|-------|---------|
| **1025** | **Generative Sufficiency — Class Markov + Forbidden Suppression Is Sufficient at M2 (80%)** (M0 i.i.d. passes 11/15=73% revealing most tests are marginal; M2 49-class Markov + forbidden suppression = sufficiency frontier at 12/15=80%; M4 compositional generation WORST at 9.4/15=63% from 4.2% hallucination rate; macro-automaton M3 ties M2, adds nothing; B4/C2 universally failed = test specification issues; 2/5 predictions correct) | 2 | B | -> [C1025_generative_sufficiency.md](C1025_generative_sufficiency.md) |

**Phase findings (5 models × 15 tests × 20 instantiations):**
- M0 (i.i.d.): 11.0/15 (73%) — token frequency alone satisfies most tests
- M1 (class Markov): 11.9/15 (79%) — adds B1 spectral gap
- M2 (M1 + forbidden): 12.0/15 (80%) — **sufficiency frontier**, adds B3
- M3 (6-state macro): 12.0/15 (80%) — ties M2, macro-automaton is lossy projection
- M4 (compositional): 9.4/15 (63%) — WORST; prefix×middle×suffix product > real vocabulary
- Verdict: GENERATIVE_SUFFICIENCY_AT_M2

---

### Grammar Component Necessity (C1026) — Phase: GRAMMAR_COMPONENT_NECESSITY

| ID | Description | Tier | Scope | Details |
|----|-------------|------|-------|---------|
| **1026** | **Grammar Component Necessity — Class Ordering and Forbidden Avoidance Are Load-Bearing; Token Identity Is Partial** (5 ablations x 100 shuffles x 10 metrics; class shuffle within state breaks 5/10 spectral gap z=8.85; forbidden injection 4/10; token shuffle 2/10 PARTIAL via MIDDLE forbidden leak z=3.51; c/d equivalent confirming state=role; 4/10 DISTRIBUTIONAL; 2 SEQUENTIAL 1 TOPOLOGICAL 3 COMPOUND) | 2 | B | -> [C1026_grammar_component_necessity.md](C1026_grammar_component_necessity.md) |

**Phase findings (5 ablation verdicts):**
- (a) Forbidden injection: LOAD_BEARING (4/10 breaks)
- (b) Subset forbidden: LOAD_BEARING (3/10 breaks)
- (c) Class shuffle in state: LOAD_BEARING (5/10 breaks, spectral gap z=8.85)
- (d) Class shuffle in role: LOAD_BEARING (5/10 breaks, equivalent to c)
- (e) Token shuffle in class: PARTIAL (2/10 breaks, MIDDLE-level forbidden leak)

---

### Hazard Violation Archaeology (C1027) — Phase: HAZARD_VIOLATION_ARCHAEOLOGY

| ID | Description | Tier | Scope | Details |
|----|-------------|------|-------|---------|
| **1027** | **Hazard Violation Archaeology — Forbidden Pair Violations Are Spatially Uniform but Structurally Conditioned** (84 class-level forbidden pairs violated at 26.5%; 717/2707 eligible; no folio/line/paragraph/REGIME clustering all p>0.05; violation lines longer +1.20 p<0.0001, kernel -0.064 p<0.0001, EN -0.064 p<0.0001; PREFIX borderline p=0.051; pair Gini=0.49; section borderline p=0.028) | 2 | B | -> [C1027_hazard_violation_archaeology.md](C1027_hazard_violation_archaeology.md) |

**Phase findings (10 tests):**
- (1) Folio clustering: UNIFORM (chi2 p=0.688, DI=0.038)
- (2) Line position: UNIFORM (KS p=0.221)
- (3) Paragraph position: UNIFORM (chi2 p=0.320)
- (4) REGIME specificity: UNIFORM (chi2 p=0.224)
- (5) PREFIX context: BORDERLINE (chi2 p=0.051; qo 1.89x, lsh 0.21x)
- (6) Pair variation: HIGH (Gini=0.49, CV=0.93; AX→FQ most common)
- (7) Violation neighborhood: **SYSTEMATIC** (longer lines, less kernel/EN dense)
- (8) Sequential context: Post-violation targets differ (JSD=1.0 by construction)
- (9) Section specificity: BORDERLINE (p=0.028; BIO 0.82x, RECIPE_B 1.10x)
- (10) Permutation: UNIFORM (folio p=0.28, regime p=0.27)
- Verdict: SPATIALLY_UNIFORM_STRUCTURALLY_CONDITIONED

---

### Vocabulary Curation Rule (C1028) — Phase: VOCABULARY_CURATION_RULE

| ID | Description | Tier | Scope | Details |
|----|-------------|------|-------|---------|
| **1028** | **Vocabulary Curation Rule — Pairwise Co-occurrence Is Necessary and Dominant** (productive product space 48,640; 419 existing = 0.9% occupancy; pairwise co-occurrence gate: 100% recall, 58.4% precision; depth-3 tree 99.4% CV using only pm_cooc + ms_cooc; no three-way compilation rule detectable; 718 pairwise-compatible → 419 exist; consistent with C1003 no three-way synergy) | 2 | B | -> [C1028_vocabulary_curation_rule.md](C1028_vocabulary_curation_rule.md) |

**Phase findings:**
- Pairwise co-occurrence is NECESSARY: 0 tokens exist without both PM and MS pair support
- Pairwise co-occurrence is DOMINANT: depth-3 tree learns only PM+MS rule (99.4% CV)
- 42% gap within pairwise-compatible space is consistent with finite-sample sparsity
- No higher-order "compiler rule" beyond pairwise compatibility
- Confirms C1003 (no three-way synergy) from vocabulary-existence angle
- Verdict: NO_HIDDEN_COMPILER_RULE

---

### Tensor Archetype Geometry (C1020) — Phase: TENSOR_ARCHETYPE_GEOMETRY

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1020** | **Tensor Archetype Geometry — Tensor Factors Encode Dynamics Through Graded Curvature, Not Macro-State Clustering** (7/8 CP factors correlate with AXM at |rho|>0.40, best rho=-0.738; archetypes don't cluster in CP space sil=-0.040; 100% bridge degeneracy; HUB rank 3 vs full rank 8; HUB PREFIX-diverse entropy 1.024>0.851) | 2 | B | -> [C1020_tensor_archetype_geometry.md](C1020_tensor_archetype_geometry.md) |

**Phase findings (Sub-A + Sub-B + synthesis):**
- A1: Silhouette — FAIL (sil=-0.040 but z=3.81 vs null; non-random but not compact clusters)
- A2: MANOVA — FAIL (archetype 1.47x REGIME, below 2x threshold)
- A3: AXM correlation — **PASS** (Factor 2 rho=-0.738 p<0.0001; 7/8 factors |rho|>0.40)
- A4: k-means — FAIL (ARI=0.124, near but below 0.15)
- B1: HUB ARI — FAIL (0.072; bridge degeneracy: 100% B MIDDLEs are bridges → HUB/non-HUB partition)
- B2: Non-HUB ARI — **PASS** (0.025 < 0.10)
- B3: HUB rank — **PASS** (rank 3 for 90% variance vs full rank 8)
- B4: HUB entropy — FAIL (1.024 > 0.851; HUB MIDDLEs are PREFIX-diverse)
- Verdict: TENSOR_GEOMETRY_ORTHOGONAL — 3/8 passed (tensor encodes dynamics as continuous gradient, not discrete categories)

---

### Morphological Tensor Decomposition (C1019) — Phase: MORPHOLOGICAL_TENSOR_DECOMPOSITION

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1019** | **Morphological Tensor Decomposition — Transition Tensor Has Rank-8 Pairwise Structure Orthogonal to 6-State Macro-Automaton** (rank 8 at 97.0% variance; CP ≥ Tucker confirming C1003; class factors ARI=0.053 vs C1010 — macro-automaton NOT a tensor projection; ΔR²=0.465 dynamical prediction 4x C1017; SUFFIX 2 SVD dims confirming C1004; HUB vs STABILITY cosine=0.574) | 2 | B | -> [C1019_morphological_tensor_decomposition.md](C1019_morphological_tensor_decomposition.md) |

**Phase findings (T1-T4 + synthesis):**
- T1: Tensor construction + rank selection — **PASS** (rank 8, 97.0% variance, 13,315 bigrams, 20×10×5×49)
- T2: Factor interpretation — MIXED (class ARI=0.053 FAIL; PREFIX rho=0.182 FAIL; bins HUB≠STAB PASS; SUFFIX 2 SVD dims PASS)
- T3: CP vs Tucker — **PASS** (Tucker 21% worse; pairwise sufficiency confirmed)
- T4: Controls — MIXED (marginalized ARI=0.050; shuffle ARI=0.080 PASS; cross-val congruence 0.882 stable; ΔR²=0.465)
- Verdict: TENSOR_NOVEL — 5/8 passed (macro-automaton is interpretive abstraction, not tensor projection)

---

### Section Grammar Variation + M2 Gap Decomposition (C1029-C1030) — Phase: SECTION_GRAMMAR_VARIATION

> **Summary:** Section modulates 49-class transition weights at the same scale as REGIME (mean pairwise JSD 0.325 vs 0.320, ratio 1.016x). Topology is shared across sections (zero section-only transitions; coverage varies 32-79% by sample size). 42.6% of classes show significant section-dependent transitions (p<0.05). Role self-loop ordering is section-dependent: BIO has EN > FQ > FL (thermal dominance); COSMO and STARS_RECIPE have FQ > FL > EN. Extends C979 to section dimension. **M2 gap decomposition:** Phase 348's B4 test is misspecified (M2 trivially reproduces real self-loop rates; real ordering is FQ > EN > FL not FQ > FL > EN). Corrected M2 pass rate: 13/15 = 86.7%. Remaining gap: B5 (forward-backward asymmetry, 3.85x overestimate, needs PREFIX routing) and C2 (CC 100% suffix-free, needs role-specific morphology) — independent mechanisms.

| ID | Description | Tier | Scope | Details |
|----|-------------|------|-------|---------|
| **1029** | **Section-Parameterized Grammar Weights** (mean pairwise JSD section=0.325 vs REGIME=0.320; zero section-only transitions; 42.6% classes section-dependent p<0.05; role ordering section-dependent: BIO EN>FQ>FL, COSMO FQ>FL>EN; extends C979 to section) | 2 | B | -> [C1029_section_grammar_parameterization.md](C1029_section_grammar_parameterization.md) |
| **1030** | **M2 Gap Decomposition — B4 Misspecified, Two Independent Mechanisms** (B4 trivially passes: M2 self-rates identical to real; corrected 13/15=86.7%; B5 asymmetry 3.85x overestimate needs PREFIX routing C1024; C2 CC 100% suffix-free needs role morphology; independent: C2 constant across sections, B5 varies) | 2 | B | -> [C1030_m2_gap_decomposition.md](C1030_m2_gap_decomposition.md) |

**Phase findings:**
- Section and REGIME modulate at same scale (JSD ratio 1.016x) — grammar has TWO orthogonal parameterization axes
- BIO section's EN self-loop dominance confirms C552 thermal-intensive profile at transition level
- B4 test misspecified in Phase 348: checks ordering property not match-to-real; M2 self-rates are matrix diagonal (identical by construction)
- B5 gap (0.178 vs 0.046): M2's single directional Markov chain overestimates asymmetry; real text has PREFIX symmetric routing (C1024)
- C2 gap: CC suffix-free rate is 100% (fully morphological constraint); EN suffix rate is 61% (highest); role-specific morphology is outside M2's scope
- Verdict: SECTION_COMPARABLE_TO_REGIME + GAP_TWO_INDEPENDENT_MECHANISMS

---

### FL Cross-Line Independence (C1031) — Phase: FL_CROSS_LINE_CONTINUITY

> **Summary:** FL stage (C777) does not propagate across line boundaries. Within-line FL coherence (68.2% SAME rate, C786) collapses to 27.9% at cross-line transitions. Backward transitions jump from 4.5% to 44.3%. Endpoint stage correlation is zero (rho=0.003, p=0.963 narrow; rho=0.032, p=0.216 broad). Marginal mean-stage correlation (rho=0.063, p=0.017) has negligible effect size and is consistent with folio-mediated coupling (C681). Each line independently samples its FL stages. Confirms C670/C681 for the FL dimension specifically.

| ID | Description | Tier | Scope | Details |
|----|-------------|------|-------|---------|
| **1031** | **FL Cross-Line Independence** (endpoint rho=0.003 narrow/0.032 broad, both ns; SAME rate collapses 68.2%→27.9% cross-line; backward jumps 4.5%→44.3%; mean gap equals null; marginal mean-stage rho=0.063 is folio-mediated C681; confirms C670 for FL dimension) | 2 | B | -> [C1031_fl_cross_line_independence.md](C1031_fl_cross_line_independence.md) |

**Phase findings:**
- FL state tracking is strictly within-line; each line is a complete, independent FL assessment cycle
- The within-line forward bias (5:1, C786) disappears entirely at line boundaries
- Cross-line transitions are approximately uniform with backward bias from within-line positional gradient
- No evidence of paragraph-level FL state tracking beyond shared folio context
- Verdict: FL_CROSS_LINE_INDEPENDENT

---

### B5 Asymmetry Mechanism (C1032) — Phase: PREFIX_ASYMMETRY_CORRECTION

> **Summary:** The M2 B5 failure (forward-backward JSD: 0.178 vs real 0.090) is caused by asymmetric forbidden transition suppression — 16 of 17 forbidden pairs are one-directional (C111). 15% detailed-balance blending corrects B5 to 0.111 (100% pass rate) but regresses B1 (spectral gap 0.770 vs 0.894, fails) and B3 (5 forbidden violations). Generic blending gains B5 but loses B1+B3 — net pass rate unchanged at 13/15. The real mechanism (PREFIX symmetric routing, C1024) achieves symmetry without reducing spectral structure. True B5 fix requires PREFIX-aware generation architecture.

| ID | Description | Tier | Scope | Details |
|----|-------------|------|-------|---------|
| **1032** | **B5 Asymmetry Mechanism — Forbidden Suppression + PREFIX Routing** (M2 B5=0.178 vs real 0.090; 16/17 forbidden pairs one-directional; alpha=0.15 blending fixes B5=0.111 but regresses B1 spectral gap 0.894->0.770 and B3 5 violations; C1024 PREFIX fraction 20.5% consistent with 15% blending; M2 stays 13/15=86.7%; true fix needs PREFIX-factored generation) | 2 | B | -> [C1032_b5_asymmetry_mechanism.md](C1032_b5_asymmetry_mechanism.md) |

**Phase findings:**
- B5 failure is real, caused by asymmetric forbidden suppression (not a mapping artifact)
- Generic detailed-balance blending at alpha=0.15 fixes B5 but regresses B1 and B3
- The 15% blending needed is consistent with C1024's 20.5% PREFIX MI fraction (ratio 0.73)
- Real data achieves low asymmetry AND high spectral gap simultaneously — generic blending cannot
- True M2.5 fix requires PREFIX-factored generation (PREFIX symmetric, MIDDLE directional)
- M2 pass rate remains 13/15 = 86.7%; projected 14/15 = 93.3% with PREFIX-aware generation

---

### C2 Test Misspecification (C1033) — Phase: C2_CC_SUFFIX_FREE

> **Summary:** The C2 test (CC suffix-free >= 99%) is misspecified. The test uses CC={10,11,12,17} (5-role taxonomy) but C588 established CC as 100% suffix-free using CC={10,11,12} (macro-state partition). Class 17 has 59% suffixed tokens (170/288 — olkeedy, olkeey, olkain, etc.), dragging the rate to 83.4%. Real data itself fails the test. M2 reproduces the real rate exactly (0.824 vs 0.834). Correcting C2 pushes M2 from 13/15 to 14/15 = 93.3%. Only B5 remains. C590's class 17 suffix=NONE claim is incorrect.

| ID | Description | Tier | Scope | Details |
|----|-------------|------|-------|---------|
| **1033** | **C2 Test Misspecification — CC Definition Mismatch** (test uses CC={10,11,12,17} but C588 used {10,11,12}; class 17 has 59% suffixed; real C2=0.834 fails 99% threshold; M2=0.824 matches real; corrected 14/15=93.3%; C590 class 17 suffix=NONE wrong; only B5 remains) | 2 | B | -> [C1033_c2_misspecification.md](C1033_c2_misspecification.md) |

**Phase findings:**
- C2 is misspecified like B4 (C1030): the test checks against a threshold the real data doesn't meet
- Class 17 has 4 suffix types: edy (68), eey (38), ain (33), aiin (31) — all on ol-prefixed compound tokens
- Two of three M2 failures (B4, C2) were test misspecifications, not model limitations
- M2 corrected pass rate: 14/15 = 93.3%. Only B5 (forward-backward asymmetry) is genuine
- C590 needs correction: class 17 suffix is NOT NONE

---

### Symmetric Forbidden B5 Fix (C1034) — Phase: PREFIX_FACTORED_DESIGN

> **Summary:** Bidirectional forbidden suppression (M5-SF) resolves M2's B5 failure while preserving B1 and B3. Under C1025 reference mapping (684 class pairs), M5-SF achieves B5 80% pass (0.132 vs real 0.090), B1 100% pass (0.873 vs 0.894), B3=0. This is the ONLY model passing all three. M2.5 blending fails B5 under this mapping (0%). PREFIX-factored generation is distributionally equivalent to M2 (doesn't help). The fix targets the root cause: asymmetric forbidden suppression. Projected M5-SF pass rate: 15/15 = 100%.

| ID | Description | Tier | Scope | Details |
|----|-------------|------|-------|---------|
| **1034** | **Symmetric Forbidden Suppression Fixes B5** (M5-SF: bidirectional forbidden, B5=0.132 80% pass, B1=0.873 100% pass, B3=0; M2.5 blending fails under C1025 mapping; PREFIX-factored distributionally equivalent to M2; projected 15/15=100% with B4+C2 corrections) | 2 | B | -> [C1034_symmetric_forbidden_b5_fix.md](C1034_symmetric_forbidden_b5_fix.md) |

**Phase findings:**
- M5-SF (symmetric forbidden) is the targeted B5 fix that C1032 identified as needed
- PREFIX-factored generation through conditional routing does NOT improve B5 (distributionally equivalent)
- Second-order class chain makes B5 WORSE (higher-order context amplifies directional patterns)
- Two key negative results: PREFIX routing cannot be accessed through generation factoring; blending fails under heavy forbidden mapping
- With B4 (C1030) + C2 (C1033) + B5 (this) corrections, M2 achieves 15/15 = 100%

---

### AXM Residual Irreducibility (C1035) — Phase: AXM_RESIDUAL_DECOMPOSITION

> Direct attack on C1017's 40% unexplained AXM self-transition variance. Six pre-registered folio-level predictors tested: paragraph count (C855), HT density (C800), gatekeeper fraction (C1007), QO fraction (C605), vocabulary size, line count. Clean negative result: 0/7 predictions passed. No predictor adds incremental R-squared beyond C1017 baseline. Random forest finds no non-linear signal. C1017 baseline moderately overfit (LOO gap 0.132). The residual is genuine program-specific free variation consistent with C458 recovery freedom.

| ID | Description | Tier | Scope | Details |
|----|-------------|------|-------|---------|
| **1035** | **AXM Residual Irreducible** (0/7 PASS; all 6 predictors dR2 < 0.013; RF CV R2 = -0.149; LOO gap 0.132; residual = free design space per C458/C980) | 2 | B | -> [C1035_axm_residual_irreducible.md](C1035_axm_residual_irreducible.md) |

**Phase findings:**
- All 6 predictors have strong raw AXM correlations (rho up to 0.446) but ZERO residual signal (all |rho| < 0.17)
- Predictors are entirely absorbed by existing model (REGIME, section, PREFIX entropy, hazard density, bridge PC1)
- C1017 baseline LOO CV R2 = 0.433 (training 0.564, gap 0.132) — true explained variance is ~43%
- Random forest negative (CV R2 = -0.149, permutation p = 0.42)
- The ~57% residual is the grammar's free design space

---

### Exit Pathway Neutrality (C1036) — Phase: EXIT_PATHWAY_PROFILING

> C458's hazard/recovery asymmetry does not manifest at the AXM macro-state boundary. Exit-conditional framing ("given AXM IS exited, where does it go?") shows CV inversely proportional to frequency (FQ < FL < CC < AXm) — the sampling theory prediction, not C458. Ingress and dwell duration show identical pattern. Structurally: exit pathways are independently routed (FL/CC uncorrelated, rho=-0.003 vs null -0.333), consistent with PREFIX-conditioned routing (C1023). C458 must live upstream: within-AXM dynamics, not boundary crossing.

| ID | Description | Tier | Scope | Details |
|----|-------------|------|-------|---------|
| **1036** | **AXM Exit Pathway Allocation Frequency-Neutral** (2/7 PASS; CV ranking FQ<FL<CC<AXm = frequency order; FL/CC uncorrelated rho=-0.003; ingress mirror identical; dwell CV same pattern; C458 localized to within-AXM dynamics) | 2 | B | -> [C1036_exit_pathway_neutrality.md](C1036_exit_pathway_neutrality.md) |

**Phase findings:**
- Exit allocation CV perfectly correlated with frequency (FQ 0.259, FL 0.557, CC 0.650, AXm 0.671)
- Ingress CV ranking identical (FQ 0.217, FL 0.531, CC 0.620, AXm 0.742)
- Dwell-before-exit CV ranking identical (FQ 0.227, FL 0.338, CC 0.411, AXm 0.443)
- FL/CC uncorrelated (rho=-0.003) — independent routing, not competitive allocation
- FL eta2(REGIME+section) = 0.198 — program-specific, not macro-organizational
- Eliminates exit proportions from C1035's 57% irreducible design freedom

---

### AXM Class Composition Redundancy (C1037) — Phase: AXM_CLASS_COMPOSITION

> Per-folio AXM class composition profiles (which of 32 AXM classes are active, in what proportions) do not decompose C1035's 57% irreducible residual. Class PCs produce LOO R² = -0.071 on residuals and add only +0.005 incremental LOO R² beyond C1017 baseline. Class composition is redundant with existing predictors (REGIME, section, PREFIX entropy, hazard density, bridge geometry). PREFIX and class composition are strongly coupled (rho = -0.55), confirming PREFIX routing (C1023) governs class activation. Third consecutive elimination: aggregate statistics (C1035), boundary transitions (C1036), class composition (C1037). Remaining candidate: micro-sequential dynamics within AXM runs.

| ID | Description | Tier | Scope | Details |
|----|-------------|------|-------|---------|
| **1037** | **AXM Class Composition Redundant** (2/6 PASS; class PCs LOO R²=-0.071 on residual; incremental LOO +0.005; PREFIX-class rho=-0.55; C458 not in class proportions; third elimination stratum) | 2 | B | -> [C1037_axm_class_composition_redundant.md](C1037_axm_class_composition_redundant.md) |

**Phase findings:**
- Class PCs predict AXM self-transition directly (LOO R²=0.463) but add only +0.005 beyond C1017
- Only 7/32 classes exceed multinomial overdispersion threshold (22%, not 50%)
- Hazard-adjacent vs non-hazard CV difference = -0.026 (below 0.05 threshold)
- PREFIX PC1 vs Class PC1 rho = -0.550 — strong coupling confirms C1023 routing
- Class entropy uncorrelated with AXM self-transition (rho = 0.070, p = 0.562)
- REGIME eta² < 0.30 on all PCs — class composition is program-specific

---

### AXM Run Entropy Convergence (C1038) — Phase: AXM_RUN_MICROSEQUENCE

> Conditional transition entropy within AXM runs decreases monotonically from H=3.84 bits (position 1) to H=2.52 bits (position 6), slope=-0.248 bits/position. Class repertoire narrows as runs extend — grammar-level invariant, not program-specific. Three micro-sequential measures (entropy gradient, per-folio JSD, per-folio CMI) tested for residual prediction: all collapse after sample-size control (JSD rho: -0.295→-0.149; CMI rho: +0.237→+0.082). Completes four-phase elimination (C1035/C1036/C1037/C1038): 57% residual confirmed as design freedom space (C458, C980).

| ID | Description | Tier | Scope | Details |
|----|-------------|------|-------|---------|
| **1038** | **AXM Run Entropy Convergence + Micro-Sequential Stratum Empty** (0/6 PASS after size control; entropy slope=-0.248 bits/pos; JSD/CMI size-confounded; four-phase elimination complete; residual = design freedom) | 2 | B | -> [C1038_axm_run_entropy_convergence.md](C1038_axm_run_entropy_convergence.md) |

**Phase findings:**
- AXM runs converge: H drops 3.84→2.52 bits over 6 positions (2,383 runs, 6,054 bigrams)
- Convergence rate uniform across archetypes (ANOVA p=0.117)
- Corpus JSD = 0.066 bits validates C1024 (0.070 bits) within-AXM-run scope
- CMI permutation test p=0.455 — between-folio CMI variance = random
- JSD confounded with sample size (rho=-0.675); CMI confounded (rho=+0.499)
- After size control: JSD incr LOO R²=-0.042; CMI incr=+0.009 (both noise)
- Four-phase elimination complete: residual IS the design freedom (C458 + C980)

---

### A Paragraph Combinatorial Grammar (C1039-C1041) — Phase: A_PARAGRAPH_COMBINATORICS

> Phase 364 tests whether A paragraph membership imposes MIDDLE compatibility constraints beyond line-level incompatibility (C475/C729). Three findings: (1) Paragraphs draw from fewer C475 clusters than random (entropy 1.50 vs 1.78, p=0.002). (2) Within-folio paragraph pairs have higher MIDDLE compatibility than between-folio (0.880 vs 0.811, p~0), surviving section matching. (3) Paragraphs have LOWER cross-line compatibility than random (z=-3.567) — they diversify rather than cluster compatible entries. RI linkers (C835) do not predict folio composition similarity (p=0.151). Paragraph composition adds marginal B coverage prediction (delta-R2=0.048, below 0.05 threshold).

| ID | Description | Tier | Scope | Details |
|----|-------------|------|-------|---------|
| **1039** | **A Paragraph Cluster Selectivity** (entropy 1.50 vs null 1.78, z=-2.83, p=0.002; paragraphs draw from fewer C475 clusters than random) | 2 | A | -> [C1039_paragraph_cluster_selectivity.md](C1039_paragraph_cluster_selectivity.md) |
| **1040** | **A Folio-Level Paragraph Compatibility Coherence** (within-folio 0.880 vs between-folio 0.811, p~0; survives section matching 0.810, p~0) | 2 | A | -> [C1040_folio_paragraph_compatibility.md](C1040_folio_paragraph_compatibility.md) |
| **1041** | **A Paragraph Complementary Diversification** (cross-line compatibility 0.700 vs null 0.707, z=-3.567; paragraphs diversify, not select for compatibility; extends C476 coverage optimality) | 2 | A | -> [C1041_paragraph_complementary_diversification.md](C1041_paragraph_complementary_diversification.md) |

**Phase findings:**
- Paragraphs are cluster-selective (H3 PASS) but not compositionally ordered (H4 FAIL, p=0.223)
- Folio is the unit of compatibility coherence (H5, H6 PASS), not paragraph
- Paragraphs diversify within their cluster subspace (H1 NEGATIVE, z=-3.567)
- RI linkers are narrow token-level bridges, not broad composition channels (H7 FAIL, p=0.151)
- Paragraph composition adds near-zero B coverage signal beyond PP pool size (H8 FAIL, delta-R2=0.048)

### Section-Parameterized Line Grammar (C1042-C1046) — Phase: SECTION_PARAMETERIZED_LINE_GRAMMAR

Tests whether section identity modulates the B line grammar at interior and boundary levels. 10 hypotheses, 6 pass. Verdict: **DEEP_PARAMETERIZATION** (3/5 Part A interior + 3/5 Part B boundary).

| # | Description | Tier | Scope | File |
|---|-------------|------|-------|------|
| **1042** | **Section-Conditional Positional Exclusivity Reduction** (C956 zone-exclusive tokens retain only 30-55% exclusivity within sections; global exclusivity partially a section composition effect; qualifies C956) | 2 | B | -> [C1042_section_exclusivity_reduction.md](C1042_section_exclusivity_reduction.md) |
| **1043** | **Role Self-Loop Section Dependence** (chi2=268.73, p<0.0001; FLOW_OPERATOR 5.17x, ENERGY_OPERATOR 3.57x, CORE_CONTROL 3.15x enrichment across sections) | 2 | B | -> [C1043_role_selfloop_section_dependence.md](C1043_role_selfloop_section_dependence.md) |
| **1044** | **Section-Dependent Phase Interleaving Rate** (KW=55.68, p<0.0001; B=0.796, C=0.808, H=0.742, S=0.770; alternation rate section-parameterized, sequential compliance universal) | 2 | B | -> [C1044_section_dependent_interleaving.md](C1044_section_dependent_interleaving.md) |
| **1045** | **Section-Dependent Boundary Role Composition** (openers: chi2=74.67, V=0.103; closers: chi2=56.15, V=0.090; boundary role distributions section-dependent) | 2 | B | -> [C1045_section_dependent_boundary_roles.md](C1045_section_dependent_boundary_roles.md) |
| **1046** | **Mandatory Bigram Section Modulation** (5/10 mandatory bigrams show section-dependent rates at Bonferroni alpha=0.005; extends C957 and C1029 to bigram level) | 2 | B | -> [C1046_mandatory_bigram_section_modulation.md](C1046_mandatory_bigram_section_modulation.md) |

**Phase findings:**
- Interior transitions are section-dependent (H1 PASS, JSD=0.337 vs null 0.281, p=0.000)
- Self-loop rates strongly section-modulated (H2 PASS, 3 roles with 3-5x enrichment)
- Phase interleaving rate is section-parameterized (H3 PASS), but compliance ordering is universal (p=0.308)
- Forbidden compliance rates vary significantly (p=0.001) but below magnitude threshold (ratio 1.39, need 1.5; H4 FAIL near-miss)
- EN token ordering remains free in all sections (H5 FAIL, strengthens C961)
- Opener and closer role distributions are section-dependent (H6, H7 PASS)
- Line length is section-insensitive (H8 FAIL, eta2=0.004; strengthens C958)
- Mandatory bigram rates are section-parameterized (H9 PASS, 5/10)
- Positional exclusivity breaks per section (H10 FAIL, 30-55% retention; qualifies C956)

### Section Residual Decomposition (C1047-C1048) — Phase: SECTION_RESIDUAL_DECOMPOSITION

Tests whether section x predictor interaction effects explain any of C1035's irreducible AXM residual. 5 hypotheses, 2 pass. Verdict: **SECTION_INTERACTIONS_CONFIRM_IRREDUCIBILITY**.

| # | Description | Tier | Scope | File |
|---|-------------|------|-------|------|
| **1047** | **Section-Dynamics Interaction Absent** (0/3 interaction terms significant; section modulates dynamics additively only; per-section LOO 0.037 vs global 0.412; strengthens C1035) | 2 | B | -> [C1047_section_dynamics_interaction_absent.md](C1047_section_dynamics_interaction_absent.md) |
| **1048** | **BIO Section Dynamical Coherence** (BIO LOO R²=0.754 vs HERBAL -0.242 and RECIPE -0.319; C1017 predictors explain 75% of BIO AXM variance; design freedom concentrated in non-BIO sections) | 2 | B | -> [C1048_bio_dynamical_coherence.md](C1048_bio_dynamical_coherence.md) |

**Phase findings:**
- Section x predictor interactions are universally absent (H1, H3 FAIL; all p>0.49)
- Per-section models overfit dramatically except BIO (H2 FAIL; BIO is uniquely predictable)
- Bridge geometry is section-orthogonal (H4 PASS; BIO PC1 cosine to global = 0.069) but doesn't improve prediction
- Conservation confirmed (H5 PASS; LOO=0.412, residual 58.8%)
- C1035 irreducibility strengthened: the residual is genuine design freedom (C458), not a section-averaged artifact
- AXM residual elimination sequence now complete (C1035-C1038 + C1047-C1048)

### A-B Section Correspondence (C1049-C1051) — Phase: A_B_SECTION_CORRESPONDENCE

> **Summary:** PP MIDDLE composition creates section-differential coverage through the A→B pipeline. Shared (A∩B) MIDDLEs are significantly less section-concentrated than B-only MIDDLEs (Herfindahl 0.70 vs 0.93), revealing the shared vocabulary as a section-universal substrate. PP composition quality (core_fraction) predicts section-specific coverage beyond pool size (partial r=0.33-0.46). The C708 funnel topology is section-dependent: BIO class Jaccard=0.794 vs RECIPE 0.824 (global=0.847). Verdict: PP_SECTION_SIGNAL (5/5).

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1049** | **Shared Vocabulary Section-Universal Substrate** (329 shared MIDDLEs: Herfindahl 0.70 vs 862 B-only: 0.93; MW p<10^-6; shared vocabulary IS the section-universal layer; explains C946 reach uniformity) | 2 | A<>B | -> [C1049_shared_vocabulary_section_universal.md](C1049_shared_vocabulary_section_universal.md) |
| **1050** | **PP Composition Section-Differential Coverage** (core_fraction partial r=0.33-0.46 with section coverage after pool-size control; ranking stability rho=0.81-0.86 across sections; composition quality matters beyond pool size) | 2 | A<>B | -> [C1050_pp_composition_section_differential.md](C1050_pp_composition_section_differential.md) |
| **1051** | **Section-Conditioned Class Convergence Asymmetry** (BIO class Jaccard=0.794, HERBAL=0.813, RECIPE=0.824 vs global=0.847; KW p=1.2×10^-102; funnel topology section-dependent; BIO aperture narrowest) | 2 | A<>B | -> [C1051_section_conditioned_class_convergence.md](C1051_section_conditioned_class_convergence.md) |

**Phase findings:**
- Shared (PP∩B) MIDDLEs are the section-universal substrate; B-only MIDDLEs are section-specific (86% concentrated vs 40%)
- C946 reach uniformity (cosine=0.997) is replicated and EXPLAINED: A covers all sections equally because shared vocabulary IS universal
- PP composition quality (how section-universal the MIDDLEs are) predicts coverage beyond pool size
- C708 funnel topology varies by section — BIO has narrowest aperture (most A-folio-sensitive class repertoire)
- A section (H vs P) creates slight but significant coverage proportion differences (H→more HERBAL, P→more RECIPE)
- Does NOT contradict C752/C753/C946 — extends constraint propagation interpretation with mechanistic detail

### Paragraph Gradient Combinatorics (C1052-C1053) — Phase: PARAGRAPH_GRADIENT_COMBINATORICS

> **Summary:** Tests whether B paragraph spec→exec gradient (C932) operates through C475 compatibility graph. 5 hypotheses, 2 pass. Verdict: COMPOUND_MEDIATED. B paragraphs ARE cluster-selective (replicating C1039 on B, z=-2.61, p=0.007). The key finding: compound atom prediction (C935) is C475-mediated — compatible atoms predict body MIDDLEs at 12x the rate of incompatible atoms (p=0.002). The gradient does NOT operate through compatibility at the line level (H2 fails), but compound specification DOES encode through compatibility neighborhoods. Cluster entropy DECREASES from specification to execution (opposite of prediction), meaning the execution loop converges on specific compatibility neighborhoods rather than sampling broadly.

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1052** | **B Paragraph Cluster Selectivity** (replicates C1039 on B; z=-2.61, p=0.007; execution zone more concentrated than specification zone; 73 paragraphs) | 2 | B | -> [C1052_b_paragraph_cluster_selectivity.md](C1052_b_paragraph_cluster_selectivity.md) |
| **1053** | **Compound Atom C475 Mediation** (compatible atoms hit body at 46.2% vs incompatible 3.9%; Wilcoxon p=0.002; C935 operates through compatibility graph) | 2 | B | -> [C1053_compound_atom_c475_mediation.md](C1053_compound_atom_c475_mediation.md) |

**Phase findings:**
- B paragraphs are cluster-selective (z=-2.61), replicating C1039 from Currier A on Currier B
- Cluster selectivity is concentrated in the EXECUTION zone (Q3-Q4), not specification zone (Q0-Q1)
- Cluster entropy decreases Q0→Q4 (rho=-0.80): execution converges on specific compatibility neighborhoods
- Compound atom specification (C935) is C475-mediated: compatible atoms predict body MIDDLEs at 12x rate
- Line-level Q0→Q3Q4 compatibility does NOT constrain execution vocabulary (H2 fails; near-ceiling rate 99.8%)
- Section funnel aperture weakly correlates with gradient steepness (rho=-0.5, n=3, direction matches C1051)

---

### Affordance Bin Paragraph Dynamics (C1054) — Phase: AFFORDANCE_BIN_PARAGRAPH_DYNAMICS

Tests whether the 9 affordance bins (C995-C1000) have distinct paragraph-gradient trajectories.

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1054** | **Affordance Bin Gradient Invariance** (HUB fraction ~64% at every quintile; 0/9 bins show gradient dependence; bin scaffold is static across spec→exec gradient; 73 paragraphs) | 2 | B | -> [C1054_affordance_bin_gradient_invariance.md](C1054_affordance_bin_gradient_invariance.md) |

**Phase findings:**
- Affordance bin composition is INVARIANT across the paragraph specification→execution gradient
- HUB_UNIVERSAL fraction remains ~64% at every quintile position (Spearman rho=-0.10, p=0.873)
- No individual non-HUB bin shows Bonferroni-significant gradient decline (0/8 bins)
- HUB sub-roles (HAZARD_SOURCE/TARGET/SAFETY_BUFFER/PURE_CONNECTOR) are also quintile-independent (0/4 significant)
- Bin-to-bin transition grammar barely differs between spec and exec zones (mean row-wise JSD=0.066)
- The gradient selects WHICH MIDDLEs within each bin, not which bins — functional scaffold is preserved

---

### Section-Specific M2 (C1055) — Phase: SECTION_SPECIFIC_M2

Capstone validation: does M2 generative sufficiency (C1025) hold per section independently?

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1055** | **M2 Near-Section-Decomposable** (per-section M2: BIO 78%, STARS_RECIPE 79%, HERBAL 70%; pooling advantage only +0.5 tests; topology preserved, distributional tests degrade cross-section) | 2 | B | -> [C1055_section_m2_near_decomposable.md](C1055_section_m2_near_decomposable.md) |

**Phase findings:**
- Per-section M2 reaches 78-79% for BIO and STARS_RECIPE (just below 80% global threshold)
- Same 3 universally-failing tests (B4, B5, C2) per-section as globally
- Pooling advantage is only +0.5 tests, confirming C1047 (no emergent cross-section structure)
- Global M2 tested per-section: D1 fails in 4/4 sections, B2 fails in 3/4, but B1 and B3 preserved
- Cross-section transfer does NOT correlate with C1029 pairwise JSD (rho=-0.24)
- 11/15 tests are section-invariant, 4 are section-sensitive (A2, B1, B5, D3)
- Sections parameterize a single grammar rather than implementing distinct grammars

---

### Brunschwig MIDPROCESS Absence (C1056) — Phase: BRUNSCHWIG_MIDPROCESS_ABSENCE

Formal characterization of why MIDPROCESS is structurally absent from Brunschwig's recipe-level encoding, and its impact on the Brunschwig-Voynich dimensional comparison.

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1056** | **MIDPROCESS Structural Absence / OJLM-1 Boundary** (0/245 v3 recipes have MIDPROCESS actions; 0/509 master materials have process monitoring; MIDPROCESS is tacit operator knowledge; Path C mechanically passable but circular; Voynich M2 residual parallels 2/3 dynamic/pairwise) | 2 | B | -> [C1056_midprocess_structural_absence.md](C1056_midprocess_structural_absence.md) |

**Phase findings:**
- MIDPROCESS absence confirmed across 5 independent data sources
- Brunschwig effective dimensionality: 5 active phases, 3 PCs for 80% (MIDPROCESS + STORAGE both zero-variance)
- Voynich-Brunschwig dimensional gap: 2 (Voynich 5/10 vs Brunschwig 3/5), 0.752 bits entropy gap
- Uniform MIDPROCESS fabrication reaches loading 0.571 but is circular (denominator-driven, not data-driven)
- M2 failing tests (B4, B5, C2) span 3 categories; 2/3 capture dynamic/pairwise structure (OJLM-1 partial parallel)
- MIDPROCESS represents tacit operator knowledge not codifiable in recipe-level specification

---

### Lane-Sister Orthogonal Axes (C1057) — Phase: RUPESCISSA_REVERSE_TEST

Lane balance and sister preference are independent folio-level control decisions (partial r=-0.064 after controlling QO density).

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1057** | **Lane-Sister Orthogonal Axes** (partial r=-0.064 controlling QO density; raw rho=0.210 vanishes; PCA Kaiser=2 PCs from 3 measures; ok/ot NOT independent third axis; 82 folios) | 2 | B | -> [C1057_lane_sister_orthogonal_axes.md](C1057_lane_sister_orthogonal_axes.md) |

**Phase findings:**
- Lane balance (QO/CHSH) and sister preference (ch/sh) are orthogonal after controlling QO density
- Raw correlation rho=0.210 (p=0.058) is a confound of shared QO component
- ok/ot preference is NOT a third independent axis (both correlations NS)
- Extends C412 (sister-QO anticorrelation) and C574 (EN distributional convergence)

---

### Suffix Sequential Grammar Genuine (C1058) — Phase: MORPHOLOGICAL_DEEP_STRUCTURE

Suffix bigram signal (C1002 V=0.063) survives 3-stage decomposition: role conditioning removes 4.1%, token repetition removes 2.7%, combined residual V=0.062 (6.2% total reduction). Genuine suffix-to-suffix grammar.

| # | Statement Summary | Tier | Scope | File |
|---|-----------|------|-------|----------|
| **1058** | **Suffix Sequential Grammar Genuine** (raw V=0.0662 → residual V=0.0621 after role+repeat decomposition; 6.2% artifact; 18 residual pairs |z|>3; section-universal V=0.079-0.195; top drivers dy→dy z=9.76, edy→edy z=9.13, ain→hy z=7.48) | 2 | B | -> [C1058_suffix_sequential_grammar_genuine.md](C1058_suffix_sequential_grammar_genuine.md) |

**Phase findings:**
- Suffix sequential grammar is 93.8% genuine, not role or repetition artifact
- Top pairs: dy→dy, edy→edy (self-repetition) and ain→hy (cross-suffix transition)
- Signal present in all 5 sections but section-modulated (stronger in T, C)
- Extends C1002; reconciles with C1004 (zero cross-token information at suffix level, not full-token level)

---

### Suffix-Role PREFIX Independent (C1059) — Phase: MORPHOLOGICAL_DEEP_STRUCTURE

Suffix carries independent role information beyond PREFIX. V *increases* 30.7% after PREFIX conditioning (anti-mediation).

| # | Statement Summary | Tier | Scope | File |
|---|-----------|------|-------|----------|
| **1059** | **Suffix-Role PREFIX Independent** (V_raw=0.2869, V_conditioned=0.3750, mediation=-30.7%; per-PREFIX V: ol=0.663, ok=0.655, da=0.611, ot=0.532, BARE=0.436, ch=0.129, sh=0.120; 16054 classified tokens) | 2 | B | -> [C1059_suffix_role_prefix_independent.md](C1059_suffix_role_prefix_independent.md) |

**Phase findings:**
- PREFIX does not mediate suffix-role association — it masks it (anti-mediation)
- Within individual PREFIX groups, suffix still strongly predicts role (V up to 0.66)
- Three-layer role encoding: PREFIX (primary), suffix (independent secondary), joint combination
- Extends C588, C556, C378

---

### Atom Position Grammar (C1060) — Phase: MORPHOLOGICAL_DEEP_STRUCTURE

Compound atoms have non-random positional preferences (V=0.333, p=3.8e-14).

| # | Statement Summary | Tier | Scope | File |
|---|-----------|------|-------|----------|
| **1060** | **Atom Position Grammar** (V=0.3331, chi²=201.1, p=3.8e-14; 5/37 atoms Bonferroni-significant; INITIAL: opch 14/15, eol 12/14, op 20/24; FINAL: ai 29/51, kc 12/14; kernel prediction k=0.292 vs e=0.332 MW p=0.054; 449 compounds) | 2 | B | -> [C1060_atom_position_grammar.md](C1060_atom_position_grammar.md) |

**Phase findings:**
- Atoms opch, eol, op are "gateway atoms" (almost exclusively compound-initial)
- Atoms ai, kc are "terminal atoms" (predominantly compound-final)
- Kernel prediction (k-early, e-late) marginally significant, directionally consistent with C521
- kc is FINAL despite k-content — k in its boundary/closure role
- Extends C521, C522, C935

---

### Atom Co-occurrence Structure (C1061) — Phase: MORPHOLOGICAL_DEEP_STRUCTURE

Compound atom pairs show structured co-occurrence (chi²=1830, p=3.6e-7). 10 enriched, 0 depleted.

| # | Statement Summary | Tier | Scope | File |
|---|-----------|------|-------|----------|
| **1061** | **Atom Co-occurrence Structure** (chi²=1829.9, p=3.6e-7; 10 enriched pairs z>3: eeo+eod z=7.51, al+lk z=6.10, al+lo z=4.74; 0 depleted; C475 compliance 100% but random=100% enrichment=1.0x; 449 compounds, 56 atoms) | 2 | B | -> [C1061_atom_cooccurrence_structure.md](C1061_atom_cooccurrence_structure.md) |

**Phase findings:**
- Enrichment driven by overlap-sharing (al+lk, eeo+eod) and kernel coherence (ech+ke)
- No forbidden atom pairs — construction grammar is generative not restrictive
- C475 incompatibility operates at token level, not atom-within-compound level
- Extends C475, C1053

---

### Compound Depth-Folio Specificity (C1062) — Phase: MORPHOLOGICAL_DEEP_STRUCTURE

Compound depth negatively correlates with folio spread (rho=-0.27, p=5.3e-23).

| # | Statement Summary | Tier | Scope | File |
|---|-----------|------|-------|----------|
| **1062** | **Compound Depth-Folio Specificity** (Spearman rho=-0.2698, p=5.3e-23; depth 0 mean=10.5 folios, depth 3+=1.0-1.2; max depth=5; UN mean=1.22 vs classified=0.52 MW p=5.5e-13; within-role KW p=0.50 NS; 1293 MIDDLE types) | 2 | B | -> [C1062_compound_depth_folio_specificity.md](C1062_compound_depth_folio_specificity.md) |

**Phase findings:**
- Depth functions as specialization gradient: deeper = more folio-specific
- Max depth = 5 with exponential decay (76 at depth 3, 8 at depth 4, 2 at depth 5)
- UN MIDDLEs are deeper than classified — they are the compositional vocabulary
- Depth is between-role (classified vs UN) not within-role
- Extends C769, C766, C767

---

### PREFIX-SUFFIX Compatibility (C1063) — Phase: MORPHOLOGICAL_JOINT_SPACE_ARCHITECTURE

17 forbidden PREFIX x SUFFIX pairs (fewer than C911's 102 PREFIX x MIDDLE). 16/17 genuinely novel.

| # | Statement Summary | Tier | Scope | File |
|---|-----------|------|-------|----------|
| **1063** | **PREFIX-SUFFIX Compatibility** (chi²=8703.4, V=0.138; 17 forbidden pairs vs C911's 102; 16/17 novel, 1 role-explained; 50 enriched, 57 depleted; LATE prediction failed; ch/sh 0 forbidden; 30 PREFIXes x 21 SUFFIXes) | 2 | B | -> [C1063_prefix_suffix_compatibility.md](C1063_prefix_suffix_compatibility.md) |

---

### PREFIX-SUFFIX Joint Role Encoding (C1064) — Phase: MORPHOLOGICAL_JOINT_SPACE_ARCHITECTURE

Joint PREFIX+SUFFIX predicts role +5.9pp better than PREFIX alone (88.5% vs 82.6%).

| # | Statement Summary | Tier | Scope | File |
|---|-----------|------|-------|----------|
| **1064** | **PREFIX-SUFFIX Joint Role Encoding** (joint 88.5% vs PREFIX 82.6% vs SUFFIX 45.9%; +5.9pp gain; QO-family within-PREFIX V=0.615, sister V=0.124; three-layer encoding: PREFIX + suffix + joint; 16054 classified tokens) | 2 | B | -> [C1064_prefix_suffix_joint_role_encoding.md](C1064_prefix_suffix_joint_role_encoding.md) |

---

### Atom Bigram Ordering Grammar (C1065) — Phase: MORPHOLOGICAL_JOINT_SPACE_ARCHITECTURE

Compound atoms follow a directed construction grammar (V=0.376). 21 asymmetric pairs, 15 at 100%.

| # | Statement Summary | Tier | Scope | File |
|---|-----------|------|-------|----------|
| **1065** | **Atom Bigram Ordering Grammar** (chi²=1898.8, p=1.8e-73, V=0.376; 21 asymmetric pairs >80%, 15 at 100%; k-before-e 58.7% p=0.036; e-before-h 43% NS; permutation null p=0.0000; 449 compounds, 659 pairs) | 2 | B | -> [C1065_atom_bigram_ordering_grammar.md](C1065_atom_bigram_ordering_grammar.md) |

---

### Construction-Execution Independence Confirmed (C1066) — Phase: MORPHOLOGICAL_JOINT_SPACE_ARCHITECTURE

Atom string position has zero correlation with token line position (rho=-0.004, n=11,525).

| # | Statement Summary | Tier | Scope | File |
|---|-----------|------|-------|----------|
| **1066** | **Construction-Execution Independence Confirmed** (Spearman rho=-0.004, p=0.647, n=11525; partial rho=0.007 p=0.455; all 19 per-PREFIX groups NS; confirms C522 at full power; construction and execution are completely separate systems) | 2 | B | -> [C1066_construction_execution_independence_confirmed.md](C1066_construction_execution_independence_confirmed.md) |

---

### Terminal Character Positional Bias (C1067) — Phase: MORPHOLOGICAL_JOINT_SPACE_ARCHITECTURE

Terminal character of atoms predicts compound position (V=0.231). Resolves kc paradox.

| # | Statement Summary | Tier | Scope | File |
|---|-----------|------|-------|----------|
| **1067** | **Terminal Character Positional Bias** (chi²=105.5, p=3.5e-12, V=0.231; 'c'-terminal FINAL 86%, 'p'-terminal INITIAL 83%; initial char V=0.164; kc FINAL 92.3% token-level; resolves kc paradox: 'c'-driven not k-driven; H3 line-position rejected MW p=1.0) | 2 | B | -> [C1067_terminal_character_positional_bias.md](C1067_terminal_character_positional_bias.md) |

---

### Multi-Layer Compatibility Architecture (C1068-C1072) — Phase: MULTI_LAYER_COMPATIBILITY_ARCHITECTURE

Integration of three forbidden/incompatibility layers (C475, C911, C1063). Tests independence, community structure, kernel correlation, hazard coverage, and terminal-character compatibility.

| # | Statement Summary | Tier | Scope | File |
|---|-----------|------|-------|----------|
| **1068** | **Cross-Layer Partial Coupling** (C475 x C911 NMI=0.185, frequency-mediated perm_p=0.13; C475 x C1063 NMI=0.005; C911 x C1063 NMI=0.002; MIDDLE-centric layers coupled, PREFIX-SUFFIX layer independent) | 2 | B | -> [C1068_cross_layer_partial_coupling.md](C1068_cross_layer_partial_coupling.md) |
| **1069** | **Weak Residual Community Structure** (3 communities after hub removal + frequency regression; Q_residual=0.125, Q_random=0.042, signal=0.082; weak but above-random; one community concentrates kernel-classified MIDDLEs) | 2 | B | -> [C1069_residual_community_structure.md](C1069_residual_community_structure.md) |
| **1070** | **Atom Ordering Grammar Independent of Kernel Directional Bias** (only 2/21 cross-class pairs; both mismatch C521; compound construction grammar has own rules not reducible to kernel physics) | 2 | B | -> [C1070_atom_ordering_kernel_independence.md](C1070_atom_ordering_kernel_independence.md) |
| **1071** | **Forbidden Transitions Operate Above Component-Level Rules** (only 4/17 C109 transitions blocked by C475/C911/C1063; 0 by C911 or C1063; 13/13 residual are C475-COMPATIBLE; confirms C627 token-specific directional mechanism) | 2 | B | -> [C1071_hazard_residual_above_components.md](C1071_hazard_residual_above_components.md) |
| **1072** | **Terminal Character Predicts Within-Group Compatibility** (5/17 groups >2x baseline p<0.01: 'n' x15.2, 'm' x8.2, 'y' x7.2, 'r' x2.3, 'l' x2.3; INITIAL-biased terminals 3.2x more compatible than FINAL-biased) | 2 | B | -> [C1072_terminal_character_compatibility_signal.md](C1072_terminal_character_compatibility_signal.md) |

### Terminal Compatibility Geography (C1073-C1077) — Phase: TERMINAL_COMPATIBILITY_GEOGRAPHY

Maps WHY terminal characters predict C475 compatibility. Cross-references terminal neighborhoods with C591 roles, C976 macro-states, C995 affordance bins, and clique structure. Key finding: terminal-role/state associations are frequency-mediated; affordance bin alignment and clique structure are genuine.

| # | Statement | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1073** | **Terminal-Role Association Is Frequency-Mediated** (V=0.4069, perm_p=0.582; null mean V=0.414; terminal-role profiles fully explained by frequency neighborhoods; C777 FL bias quantified; C770 k/h/e tautology flagged) | 2 | B | -> [C1073_terminal_role_frequency_mediated.md](C1073_terminal_role_frequency_mediated.md) |
| **1074** | **Terminal-State Association Is Frequency-Mediated** (non-AXM V=0.4165, perm_p=0.992; null mean V=0.5287; terminal-state profiles fully explained by frequency; FL_SAFE min expected cell=0.02; orthogonal to T1) | 2 | B | -> [C1074_terminal_state_frequency_mediated.md](C1074_terminal_state_frequency_mediated.md) |
| **1075** | **Compatibility Asymmetry Is Frequency-Dominated** (freq_sum +1.654 std coef dominates; INITIAL_match +0.089 below 0.10 threshold; INITIAL_x_FINAL +0.016 NS confirms C1003; shared_hinge +0.096; 271K pairs after singleton exclusion) | 2 | B | -> [C1075_compatibility_asymmetry_frequency_dominated.md](C1075_compatibility_asymmetry_frequency_dominated.md) |
| **1076** | **Terminal Character Predicts Affordance Bin Beyond Frequency** (non-BULK V=0.3247, perm_p=0.000; null mean V=0.2102; 10 bins confirmed; 'm' 50% FLOW_TERMINAL, 'e' 22% STABILITY_CRITICAL; first genuine terminal signal surviving frequency null) | 2 | B | -> [C1076_terminal_affordance_bin_genuine.md](C1076_terminal_affordance_bin_genuine.md) |
| **1077** | **Terminal Compatibility Groups Form Genuine Cliques** (3/5 elevated: 'n' 4.07x p=0.000, 'y' 3.40x p=0.001, 'l' 2.52x p=0.014; frequency-band-matched null; C983 global clustering 0.873 baseline exceeded) | 2 | B | -> [C1077_terminal_groups_genuine_cliques.md](C1077_terminal_groups_genuine_cliques.md) |

### HT Interaction Architecture (C1078-C1083) — Phase: HT_INTERACTION_ARCHITECTURE

Tests 4 HTSC V9 cross-guarantee predictions + HT oscillation wavelength + paragraph ordinal neutrality (negative control). Key finding: HT hazard avoidance is vocabulary-level not positional; line-1 exclusivity is a folio-specificity tautology; tail pressure predicts HT compound rate (specification model wins); LINK-HT prefix phase independent; oscillation is section-driven; paragraph ordinal neutral.

| # | Statement | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1078** | **HT Hazard Avoidance Is Vocabulary-Level** (only 5/7042 HT tokens in forbidden vocabulary; boundary vs interior MW p=1.00; C622 role-mediated avoidance confirmed) | 2 | B | -> [C1078_ht_hazard_avoidance_vocabulary_level.md](C1078_ht_hazard_avoidance_vocabulary_level.md) |
| **1079** | **Line-1 Exclusivity Is Folio-Specificity Tautology** (line-1 100% vs body 78.3% exclusive, p~0; singleton control: both 100%; C870 folio-specificity fully explains difference) | 2 | B | -> [C1079_line1_exclusivity_folio_specificity_tautology.md](C1079_line1_exclusivity_folio_specificity_tautology.md) |
| **1080** | **Tail Pressure Predicts HT Compound Rate** (rho=0.367, p=0.0007; POSITIVE direction supports C935 specification model; partial rho=0.425 controlling HT count; two-axis model prediction rejected) | 2 | B | -> [C1080_tail_compound_specification_correlation.md](C1080_tail_compound_specification_correlation.md) |
| **1081** | **LINK Adjacency Does Not Modulate HT Prefix Phase** (chi2=0.89, p=0.35, V=0.022; LINK-adjacent and non-adjacent HT have same EARLY/LATE ratio; confirms C804 weak transition bias) | 2 | B | -> [C1081_link_ht_prefix_phase_independent.md](C1081_link_ht_prefix_phase_independent.md) |
| **1082** | **HT Oscillation Is Section-Driven** (raw ACF significant at lags 1,2,4,6,20; section-residualized: only lag 7 survives; no lag 8-12 signal; resolves open question) | 2 | B | -> [C1082_ht_oscillation_section_driven.md](C1082_ht_oscillation_section_driven.md) |
| **1083** | **HT Density Is Paragraph-Ordinal Neutral** (rho=0.018, p=0.69; first vs last MW p=0.086 NS; confirms C855 parallel programs; negative control PASS) | 2 | B | -> [C1083_ht_paragraph_ordinal_neutral.md](C1083_ht_paragraph_ordinal_neutral.md) |

### Galenic Parallel Tests (C1084) — Phase: GALENIC_PARALLEL_TESTS

| # | Statement | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1084** | **Section-Specific AXM Attractor Ordering** (KW H=29.9, p<0.0001, eta-sq=0.355; B(0.754) > S(0.687) > C(0.635) > H(0.587); decomposes C1017 baseline; survives REGIME control) | 2 | B | -> [C1084_section_specific_axm_attractor_ordering.md](C1084_section_specific_axm_attractor_ordering.md) |

---

### Bio Domain Distinctiveness (C1085-C1087) — Phase: BIO_DOMAIN_DISTINCTIVENESS

> **Summary:** Bio section (f74-f84, 20 folios) is a structurally distinct operational mode within REGIME_1, not a generic subset. k-enriched kernel balance (34.1% vs 24.9%, surviving REGIME control), apparatus-hazard depletion (OR=0.680), and multidimensional divergence on 6/8 dimensions within REGIME_1. LINK depletion (0.63% vs 2.81%) indicates near-zero monitoring pauses. QO-dominant CC trigger routing (44.8%) drives the kernel shift through PREFIX-MIDDLE compatibility pathways. Multi-domain (medical) hypothesis rejected; balneum mariae (sustained heating stage) preferred at Tier 3.

| # | Statement | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1085** | **Bio Section Kernel-Balance Distinctiveness** (k=34.1% vs 24.9%, chi2=146.9, p=1.24e-32; REGIME-controlled: Bio-R1 k=34.1% vs non-Bio-R1 k=27.1%, chi2=86.6, p=1.57e-19; QO→k causal chain via C600/C911) | 2 | B | -> [C1085_bio_kernel_balance_distinctiveness.md](C1085_bio_kernel_balance_distinctiveness.md) |
| **1086** | **Bio Section Apparatus-Hazard Depletion** (apparatus hazards 24.4% vs 32.2%, OR=0.680, p<0.0001; COMPOSITION_JUMP elevated 36.3% vs 27.0%; shifted from apparatus failures to material-state failures) | 2 | B | -> [C1086_bio_apparatus_hazard_depletion.md](C1086_bio_apparatus_hazard_depletion.md) |
| **1087** | **Bio-REGIME_1 Multidimensional Divergence** (6/8 dimensions significant within R1; LINK 0.63% vs 2.81% p=0.003; AXM self 0.754 vs 0.677 p=0.010; lane balance NS; explains C1048 LOO R2=0.754) | 2 | B | -> [C1087_bio_regime1_multidimensional_divergence.md](C1087_bio_regime1_multidimensional_divergence.md) |

**Phase findings:**
- Bio is 100% REGIME_1 (20/20 folios) but structurally distinct from other REGIME_1 folios
- k-enrichment persists after REGIME control (chi2=86.6, not a REGIME artifact)
- LINK depletion (~20x below corpus average) indicates near-zero monitoring pauses
- QO CC triggers 44.8% (vs 13.0%) drive k-enrichment through QO→k PREFIX-MIDDLE pathway
- Multi-domain (medical treatment) hypothesis REJECTED — balneum mariae (Tier 3) preferred
- T4 CC trigger decomposition (chi2=272.4, V=0.373) folded into C1085 evidence, not separate constraint

---

### Bridge Dynamics & Stars Characterization (C1099-C1121) — Phases: BRIDGE_BACKBONE_MANUSCRIPT_SURVEY, SECTION_BRIDGE_DYNAMICS, STARS_RECIPE_CHARACTERIZATION, STARS_PARADOX_RESOLUTION

Bridge density varies massively by section (Phase 390), with Section H highest and Section T lowest. The REGIME effect on bridge density is a pure section confound (Phase 391). Stars section characterized through mirror tests and clamping falsification (Phase 392). Stars Paradox resolved as REGIME composition artifact (Phase 394).

| # | Statement | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1099** | **Bridge Density Section Gradient** (KW H=129.0, p≈0; H=0.697, B=0.603, P=0.564, C=0.536, Z=0.506, A=0.480, S=0.480, T=0.453; T is LOWEST not highest; viability backbone runs through Herbal) | 2 | GLOBAL | -> [C1099_bridge_density_section_gradient.md](C1099_bridge_density_section_gradient.md) |
| **1102** | **Bridge Density REGIME Dependence** (ANOVA F=16.1, p<0.0001; R2=0.738, R4=0.638, R1=0.578, R3=0.518; **RESOLVED by C1103**: pure section confound) | 2 | GLOBAL | -> [C1102_bridge_density_regime_dependence.md](C1102_bridge_density_regime_dependence.md) |
| **1103** | **REGIME-Bridge Density Is Section Confound** (partial r=0.0007, p=0.995 after section control; C1102 effect vanishes completely; C979 confirmed — REGIME modulates weights not topology) | 2 | GLOBAL | -> [C1103_regime_bridge_density_section_confound.md](C1103_regime_bridge_density_section_confound.md) |
| **1104** | **Bridge Density Enables Dynamical Freedom** (rho=+0.277, p=0.025: higher bridge density → MORE |c1017_residual|; H variance 0.0148 > B 0.0078 > S 0.0059; monotonic; mechanism for C458/C1048) | 2 | B | -> [C1104_bridge_density_enables_freedom.md](C1104_bridge_density_enables_freedom.md) |
| **1105** | **Bridge Geometry-Density Collinearity** (r=-0.805; delta-R²=0.007 NS beyond C1017; BIO LOO exception +0.071; same structural property, different measures) | 2 | B | -> [C1105_bridge_geometry_density_collinearity.md](C1105_bridge_geometry_density_collinearity.md) |
| **1106** | **Stars e-Stability Kernel Enrichment** (e=66.2% vs 57.4% NS, k=23.9% vs 32.5%; chi2=145, p=3.3e-32; survives REGIME_1 control chi2=89, p=4.7e-20; 5/8 dimensions diverge in R1) | 2 | B | -> [C1106_stars_e_stability_enrichment.md](C1106_stars_e_stability_enrichment.md) |
| **1107** | **Stars LINK Monitoring Concentration** (7.4x LINK density: 0.032 vs 0.004, p<0.0001, r=-0.913; opposite of Bio 4.7x LOWER; CC triggers CLOSE_FLOW/FQ_FREQUENT dominant, QO_ENERGY depleted) | 2 | B | -> [C1107_stars_link_monitoring_concentration.md](C1107_stars_link_monitoring_concentration.md) |
| **1108** | **Stars Vocabulary Clamping Falsified** (S7-S10: 0 PASS, 3 FAIL; no consistent intra-REGIME clamping, no e-mediation, no bridge mediation, vocabulary LESS homogeneous across REGIMEs; Stars Paradox remains open) | 2 | B | -> [C1108_stars_clamping_falsified.md](C1108_stars_clamping_falsified.md) |
| **1111** | **Stars Paradox is REGIME Composition Artifact** (Gate 1.2 FAIL: within-REGIME Stars not anomalous; R1 ratio=1.45 p=0.075, R3 ratio=0.60 wrong direction; 0/11 mechanism tests PASS; LINK/CC/paragraph/forbidden all comprehensively falsified; C979 strengthened) | 2 | B | -> [C1111_stars_paradox_regime_artifact.md](C1111_stars_paradox_regime_artifact.md) |
| **1116** | **Within-REGIME Section Parameterization** (Bio vs Stars within REGIME_1: 6/6 dimensions show consistent quantitative divergence — class V=0.239, PREFIX V=0.153, PERMANOVA F=4.16 p=0.019, macro-state V=0.090, vocab JSD=0.078, affordance V=0.038 — but 0 qualitative incompatibility; confirms C1029 at within-REGIME granularity; multi-domain stays Tier 3) | 2 | B | -> [C1116_within_regime_section_parameterization.md](C1116_within_regime_section_parameterization.md) |
| **1117** | **LTR Reading Direction Confirmed** (7-test battery: LTR 5, RTL 0, NEUTRAL 2; MIDDLE MI forward bias +0.070 bits z=17.0; PREFIX positional coherence 7-0 LTR vs RTL; 75.2% forbidden pairs are bidirectional adjacency constraints; spectral gap direction-invariant 0.896 vs 0.899; entropy bathtub profile falsifies boundary-inward; CC boundary-left; vocabulary gradient spec-to-exec under LTR) | 2 | B | -> [C1117_ltr_reading_direction_confirmed.md](C1117_ltr_reading_direction_confirmed.md) |
| **1118** | **Bidirectional Forbidden Co-occurrence Dominance** (75.2% of MIDDLE-level forbidden pairs 1244/1655 are bidirectional adjacency prohibitions; 24.8% direction-specific; explains C1034 symmetric forbidden model improvement; broader MIDDLE co-occurrence landscape is predominantly symmetric while 17 class-level transitions C783 are directional) | 2 | B | -> [C1118_bidirectional_forbidden_dominance.md](C1118_bidirectional_forbidden_dominance.md) |
| **1119** | **MIDDLE Forward Bias as Reading Direction Evidence** (MI_fwd=0.312 vs MI_bwd=0.242, asymmetry +0.070 bits z=17.0; PREFIX weak backward -0.018 z=-4.4; SUFFIX weak forward +0.018 z=5.5; confirms C1024 at raw MIDDLE resolution; MIDDLE predicts physical-right neighbor better — information flows left-to-right) | 2 | B | -> [C1119_middle_forward_bias.md](C1119_middle_forward_bias.md) |
| **1120** | **Lifecycle Domain Progression Falsified** (within-paragraph Bio-score rho=-0.068, Wilcoxon p=0.052; residualized rho=-0.067 p=0.065; 0/5 battery tests support lifecycle; slight negative trend explained by C932 spec-to-exec gradient; domain character determined at folio level ICC=0.393) | 2 | B | -> [C1120_lifecycle_domain_falsified.md](C1120_lifecycle_domain_falsified.md) |
| **1121** | **Folio-Level Domain Determination** (paragraph domain character Bio/Stars determined at folio level ICC=0.393, F(45,95)=2.98; within REGIME_1 section predicts Bio-score Bio=0.131 vs Stars=-0.027 diff=0.158; within-paragraph domain stable perm p=0.19; consistent with C1087 Bio divergence) | 2 | B | -> [C1121_folio_level_domain_determination.md](C1121_folio_level_domain_determination.md) |

**Phase 390 findings (Bridge Backbone Manuscript Survey):**
- Bridge density varies massively by section (KW H=129.0, p≈0) — Section H highest (0.697), Section T lowest (0.453)
- Section T has LOWEST bridge density (rank 8/8) — opposite of C299-based prediction
- Bridge density varies by REGIME (F=16.1, p<0.0001) — tension with C979, possibly section-confounded

**Phase 391 findings (Section-Bridge-Dynamics Triangle):**
- C1102 REGIME effect vanishes completely after section control (partial r=0.0007) — C979 confirmed
- Bridge density POSITIVELY correlates with |c1017_residual| (rho=+0.277) — opposite of prediction
- Herbal has highest AXM variance (0.0148 > B 0.0078 > S 0.0059) — most dynamical freedom
- Bridge density collinear with bridge_pc1 (r=-0.805) — delta-R²=0.007 NS beyond C1017
- BIO LOO exception: bridge density improves within-BIO prediction by +0.071
- Bridge vocabulary enables design freedom, not constrains it
- Overall: SECTION_MEDIATES (4 PASS, 2 FAIL)

**Phase 392 findings (Stars/Recipe Characterization):**
- Stars is e-stability enriched (66.2% e vs 57.4%, chi2=145, p~10^-32) — survives REGIME control
- Stars has 7.4x higher LINK density (0.032 vs 0.004) — opposite of Bio (4.7x lower)
- Stars uses CLOSE_FLOW/FQ_FREQUENT CC triggers; avoids QO_ENERGY — radically different control profile
- Stars diverges from non-Stars within REGIME_1 on 5/8 dimensions — NOT just a REGIME effect
- Vocabulary clamping hypothesis FALSIFIED: no consistent intra-REGIME clamping, no e-mediation, no bridge mediation
- Stars Paradox (most REGIME diversity, lowest AXM variance) remains unexplained
- Overall: STARS_DISTINCT_UNCLAMPED (3/4 mirror PASS, 0/4 clamping PASS)

**Constraint modifications:**
- C1102: Resolved by C1103 — pure section confound

**Phase 394 findings (Stars Paradox Resolution):**
- Stars Paradox is a REGIME-composition artifact: within-REGIME Stars is NOT anomalous
- REGIME_1: Stars var=0.00444 vs NS var=0.00643 (ratio 1.45, p=0.075, NS)
- REGIME_3: Stars var=0.00662 vs NS var=0.00396 (ratio 0.60 — non-Stars MORE convergent!)
- Stars (0.00525) and Bio (0.00590) have near-identical AXM variance — Herbal is the outlier (0.01303)
- All 4 alternative mechanisms comprehensively falsified (0/11 sub-tests PASS)
- LINK regulation: zero within-Stars correlation, +5% variance on removal
- CC channeling: Stars entropy HIGHER (wrong direction), routing WIDER (wrong direction)
- Paragraph constraint: Stars JSD HIGHER than Bio (wrong direction)
- De facto forbidden: Stars has FEWER zero-transitions (-25.5%, opposite prediction)
- Overall: PARADOX_NOT_CONFIRMED — REGIME system (C979) is sufficient
- C1084 qualified: section AXM ordering is REGIME-composition effect, not section-intrinsic

**Constraint modifications:**
- C979: Strengthened — no section-specific topology modifier needed
- C1084: Qualified — section AXM ordering is REGIME-composition effect
- C1108: Resolved — Stars Paradox and all untested mechanisms now addressed

---

### Rosettes System Revalidation (C1124-C1128) — Phase: ROSETTES_SYSTEM_REVALIDATION

Rosettes foldout revalidated from scratch using corrected ZL transcription data (`data/rosettes_annotated.json`). 13-test battery across 3 tiers confirms metalayer status with AZC-like grammar and universal Section T indexing. Supersedes all 21 deleted Rosettes constraints (C1088-C1098, C1100-C1101, C1109-C1115, C1122-C1123).

| # | Statement | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1124** | **Rosettes Bridge Enrichment (Revalidated)** (3.05x enrichment: 21.5% bridge MIDDLEs vs 7.0% B baseline; universal across entity types — ring 4.56x, inner_label 4.74x, outer_label 5.17x, spiral 3.55x, clock 7.11x; no type below 25%) | 2 | Rosettes | -> [C1124_rosettes_bridge_enrichment_v2.md](C1124_rosettes_bridge_enrichment_v2.md) |
| **1125** | **Rosettes Universal Section T Correlation** (all 9 rosettes correlate most strongly with Section T; Jaccard 0.083-0.183, consistently 2-3x higher than next-best section; section-level correlation is vocabulary-size artifact per C1133; foldout is general-purpose vocabulary hub) | 2 | Rosettes | -> [C1125_rosettes_section_t_universal.md](C1125_rosettes_section_t_universal.md) |
| **1126** | **Rosettes Metalayer Status (Revalidated)** (confirmed metalayer: AZC-like entity types, 3.05x bridge enrichment, universal Section T indexing, 2.2x MIDDLE compatibility; verdict ROSETTES_CONFIRMED_METALAYER) | 2 | Rosettes | -> [C1126_rosettes_metalayer_confirmed.md](C1126_rosettes_metalayer_confirmed.md) |
| **1127** | **Rosettes AZC-Like Grammar Profile** (grammar coverage 42.0%, kernel density 29-41%, LINK density <2.1% except ring 4.2%; morphological cosine 0.49-0.82 with AZC vs 0.25-0.67 with B; PP ~50%, RI ~2%; consistently AZC-like not hybrid) | 2 | Rosettes | -> [C1127_rosettes_azc_like_grammar.md](C1127_rosettes_azc_like_grammar.md) |
| **1128** | **Rosettes Generic (Not Specific) Indexing** (mean inter-rosette Jaccard of top-5 B folio sets = 0.322; f40v in top-5 for 8/9 rosettes; path tokens do not bridge endpoints; no spatial gradient; foldout is shared vocabulary hub not specific lookup table) | 2 | Rosettes | -> [C1128_rosettes_generic_indexing.md](C1128_rosettes_generic_indexing.md) |
| **1130** | **Ring Text Forbidden Compliance Without Transition Grammar** (0 forbidden violations in 277 MIDDLE bigrams; bigram entropy 7.92 bits vs B ~0.41; 252/277 unique bigrams; respects C783 hard constraints but has random transition structure; supersedes C1114/C1115) | 2 | Rosettes | -> [C1130_ring_text_forbidden_compliance.md](C1130_ring_text_forbidden_compliance.md) |

**Phase 402 findings (Rosettes System Revalidation):**
- Tier 1 (System Classification): All entity types classify as AZC-like — grammar coverage ~42%, kernel density 29-41%, zero B-forbidden violations, morphological profiles closest to AZC
- Tier 2 (Cross-Reference): Bridge enrichment 3.05x, all 9 rosettes → Section T, generic indexing (all rosettes target same B folios)
- Tier 3 (Spatial): Path bridging and adjacency gradient tests inconclusive (sparse tokens per entity)
- Overall verdict: ROSETTES_CONFIRMED_METALAYER — organizational layer above A/B/AZC systems; general-purpose vocabulary hub (C1133: Section T correlation is vocabulary-size artifact)

---

### P-Text/Rosettes Integration Revalidation (C1112, C1129) — Phase: ROSETTES_SYSTEM_REVALIDATION (Phase 403)

Revalidates unified indexing hypothesis from Phase 395 using corrected Rosettes data. 7-test battery: 4 synthesis tests (R1, R3, R4, R5) + 3 diagnostics (R2, R6, R7). Verdict: UNIFIED_CONFIRMED (4/4 PASS). Also re-registers C1112 (P-text bridge enrichment, evidence independent of Rosettes data).

| # | Statement | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1112** | **P-Text Bridge Enrichment** (45.5% bridge MIDDLEs, 55/121 unique, 100th percentile of A bootstrap; exceeds Rosettes 21.5% by 2.1x; evidence independent of Rosettes transcript) | 2 | A/AZC | -> [C1112_ptext_bridge_enrichment.md](C1112_ptext_bridge_enrichment.md) |
| **1129** | **P-Text/Rosettes Unified Indexing (Revalidated)** (UNIFIED_CONFIRMED 4/4: Jaccard=0.137 100th pctl, Spearman rho=0.576 p<<0.001, union cosine=0.876; grammar divergent — P-text A-like 0.964 vs Rosettes AZC-like 0.908; shared vocab section-general not T-specific; P-text more specific than Rosettes in B folio targeting) | 2 | GLOBAL | -> [C1129_ptext_rosettes_unified_indexing.md](C1129_ptext_rosettes_unified_indexing.md) |

**Phase 403 findings (P-Text/Rosettes Integration Revalidation):**
- R1 PASS: P-text bridge fraction 0.4545 (identical to Phase 395), 100th percentile of A
- R2 DIAGNOSTIC: P-text PREFIX cosine 0.964 to A, 0.493 to Rosettes; Rosettes 0.908 to AZC — unified vocabulary, divergent grammar
- R3 PASS: Jaccard 0.137 (36 shared MIDDLEs), ring text drives overlap (0.168)
- R4 PASS: Spearman rho=0.576, 552 paragraphs, p<<0.001
- R5 PASS: Unified index cosine 0.876 vs headers (better than either alone: P-text 0.810, Rosettes 0.813)
- R6 DIAGNOSTIC: Shared vocabulary is section-general (S=97.2%, B=H=94.4%, T=75.0%), not T-dominated
- R7 DIAGNOSTIC: P-text more specific (intra-overlap 0.253) than Rosettes (0.322); low cross-group overlap (0.101)

---

### Ring Text Register Characterization (C1131-C1132) — Phase: ROSETTES_SYSTEM_REVALIDATION (Phase 404)

Characterizes ring text (circumferential text on 9 rosettes) as a distinct register type. 12-test battery covering instruction classes, transition matrix, compound rates, PREFIX/SUFFIX profiles, per-rosette variation, and positional effects. Verdict: BRIDGE_VOCABULARY_INDEX.

| # | Statement | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1131** | **Ring Text Register Classification — BRIDGE_VOCABULARY_INDEX** (52.4% map to B grammar using 33/49 classes; AUXILIARY 42.7%, ENERGY 11.3%; bridge enrichment 32.1% > non-ring 25.5% > B p95 11.0%; 100% of classified MIDDLEs are bridge; no positional structure; structured class distribution JS=0.291 from uniform) | 2 | Rosettes | -> [C1131_ring_text_register_classification.md](C1131_ring_text_register_classification.md) |
| **1132** | **Ring Text Dual Population Structure** (classified: 150 tokens, 4.0 chars, 27.3% kernel, 22.6% compound, 100% bridge; unclassified: 136 tokens, 6.4 chars, 47.8% kernel, 49.5% compound, 22.1% bridge — two interleaved functional vocabularies) | 2 | Rosettes | -> [C1132_ring_text_dual_population.md](C1132_ring_text_dual_population.md) |

**Phase 404 findings (Ring Text Register Characterization):**
- A1: Structured class distribution (JS uniform=0.291, B=0.271); Class 2 enriched 26.4x, 9 enriched classes total
- A2: AUXILIARY dominates (42.7% vs B 25.4%), ENERGY depleted (11.3% vs B 45.8%)
- A3: Bridge 32.1% (100th percentile, elevated vs non-ring 25.5%)
- A4: Classified/unclassified bifurcation — length 4.0 vs 6.4, compound 22.6% vs 49.5%, bridge 100% vs 22.1%
- B1: 14 enriched transitions but not low-rank (19.7th percentile); overall entropy 7.92 bits
- B2: Compound rate 47.7% (B: 75.2%, non-ring: 59.6%)
- B3: PREFIX cosine AZC=0.867, inner_label=0.915, B=0.560; o-family 65.3%
- B4: SUFFIX cosine B=0.772, AZC=0.771; LINK-attr suffixes 44.3%, kernel-heavy 22.8%
- C1: Per-rosette Jaccard 0.237 (< C1128's 0.322 — ring text MORE diverse)
- C2: 81.5% hapax, 36.6% foldout-unique (75/205 types)
- C3: No positional gradient (kernel 34%→40%, PREFIX cosine 0.97)
- C4: Labels JS(class,B)=0.676-0.678 vs ring 0.271 — ring text much closer to B grammar

---

### Section Program Architecture / Rosettes Targeting (C1133) — Phase: ROSETTES_SYSTEM_REVALIDATION (Phase 405)

Decomposes the C1125 "Section T targeting" finding. 8-test battery covering per-folio overlap, bridge density, size-controlled bootstrap, section role profiles, kernel balance, and class distributions. Verdict: C1125 is a vocabulary-size artifact; f66r ranks #11/76 per-folio; bridge density anticorrelates with Rosettes overlap.

| # | Statement | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1133** | **Rosettes Targeting Decomposition** (C1125 Section T correlation is vocabulary-size artifact; f66r ranks #11/76 per-folio; top-10 are 9 S + 1 H; bridge density negatively correlates with overlap rho=-0.60; bridge triangle falsified; f66r overlap genuine but not unique — 100th percentile bootstrap) | 2 | Rosettes | -> [C1133_rosettes_targeting_decomposition.md](C1133_rosettes_targeting_decomposition.md) |

**Phase 405 findings (Section Program Architecture):**
- T1: Per-folio overlap — f66r ranks #11/76; top-10: 9 Section S + 1 Section H (f105r #1, Jaccard 0.181)
- T2: Per-folio bridge density — f66r ranks #66/76 (47.3%); H folios highest (mean 69.9%)
- T3: Overlap decomposition — 40 shared MIDDLEs (30 bridge, 10 non-bridge); 75% bridge-mediated
- T4: Size-controlled bootstrap — f66r at 100th percentile from all sections; SIZE_ARTIFACT confirmed at section level
- T5: Section bridge density — H 19.7% > B 18.7% > T 47.3% (single folio) > S 9.9%; negative correlation with overlap
- T6: Section class JS divergence — mean 0.091; sections are differentiated (confirms C552/C1029)
- T7: Section role profiles — T highest FLOW_OPERATOR (11.4%) and CORE_CONTROL (6.9%)
- T8: Section kernel balance — T unremarkable (k=18.5%, h=7.9%, e=35.9%)
- C1125 parenthetical corrected: Section T = "text-only" not "pharmaceutical"

---

### Cross-System Vocabulary Flow (C1134-C1136) — Phase: CROSS_SYSTEM_VOCABULARY_FLOW (Phase 406)

Resolves the C1049/C909 paradox: how does section-universal pipeline vocabulary produce section-specific B output? 6-test battery across 3 tiers. Core answer: frequency modulation of shared vocabulary, not B-exclusive additions.

| # | Statement | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1134** | **Section Specificity Is Frequency-Modulated** (PP drives 74% of section divergence through token frequency variation; B-exclusive JS=0.847 but only 5.8% of tokens; resolves C1049/C909 paradox) | 2 | B, A->B | -> [C1134_section_specificity_frequency_modulated.md](C1134_section_specificity_frequency_modulated.md) |
| **1135** | **Unmatched PP Dark Pipeline** (300/315 unmatched PP MIDDLEs present in B at low frequency: mean 5.7 tokens vs 224.8 matched; section-concentrated Herf=0.716; 66.7% compound; large HT/UN substrate) | 2 | A->B | -> [C1135_unmatched_pp_dark_pipeline.md](C1135_unmatched_pp_dark_pipeline.md) |
| **1136** | **A->B Flow: Uniform Pool, Concentration-Structured** (A-H/A-P cosine=0.9997; 12 A folios cover 100% classified grammar; f58v alone=60.7%; max A->B coverage ceiling 30.4%) | 2 | A->B | -> [C1136_ab_flow_uniform_concentrated.md](C1136_ab_flow_uniform_concentrated.md) |

**Phase 406 findings (Cross-System Vocabulary Flow):**
- A1: Frequency modulation — PP JS=0.124 accounts for 74% of all JS=0.167; B-exclusive JS=0.847 but 5.8% tokens
- A2: Source decomposition — PP token share 94.1%; B-exclusive maximally specific per-type but token-negligible
- B1: Unmatched PP — 300/315 B-present (95.2%); mean 5.7 tokens, 4.6 folios; Herf 0.716; compound 66.7%
- B2: A-section routing — bridge A-fractions: H=70.8%, P=21.2%, T=8.0%; P-enriched bridges favor ENERGY_OPERATOR
- C1: Coverage matrix — A-H vs A-P cosine 0.9997; all A sections cover B-H best; within-section cosine >0.998
- C2: Pipeline sufficiency — 12 folios for 100% classified grammar; f58v covers 60.7% alone; full B ceiling 30.4%

---

### Dark Pipeline Functional Test (C1137-C1139) — Phase: DARK_PIPELINE_FUNCTIONAL_TEST (Phase 407)

Tests the structural fate of 300 dark-pipeline PP MIDDLEs identified in Phase 406 (C1135). 5-test battery: classification trace, construction grammar, bridge overlap, paragraph position, section profile.

| # | Statement | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1137** | **Dark Pipeline = 100% HT/UN Substrate** (1,696 tokens from 300 MIDDLEs: 0.0% grammar-classified, 100.0% HT/UN; all 300 MIDDLEs pure-HT; mean 5.7 tokens/MIDDLE; positionally and sectionally indistinguishable from general HT) | 2 | B, A->B | -> [C1137_dark_pipeline_ht_substrate.md](C1137_dark_pipeline_ht_substrate.md) |
| **1138** | **Dark Pipeline Has Distinct Construction Grammar** (grammar-standard/extended PREFIX ratio 3.39 vs general HT 1.81; suffix rate 89.9% vs HT 77.3%; articulator rate 2.5% vs HT 10.1%; same MIDDLEs but different morphological wrapping than general HT) | 2 | B morphology | -> [C1138_dark_pipeline_construction_grammar.md](C1138_dark_pipeline_construction_grammar.md) |
| **1139** | **Dark Pipeline and Bridge Backbone Completely Disjoint** (0/300 dark-pipeline MIDDLEs overlap with 85 bridge MIDDLEs; separate A->B channels: bridges carry dynamical structure, dark pipeline carries identification vocabulary) | 2 | A->B | -> [C1139_dark_pipeline_bridge_disjoint.md](C1139_dark_pipeline_bridge_disjoint.md) |

**Phase 407 findings (Dark Pipeline Functional Test):**
- Test 1: 100% of dark-pipeline tokens are HT/UN (vs matched PP: 80.2% grammar); complete functional partition
- Test 2: DUAL_CONSTRUCTION — dark pipeline uses grammar-standard prefixes at 87% higher ratio than general HT; suffix-heavy, articulator-depleted
- Test 3: BRIDGE_DISJOINT — zero overlap between 300 dark-pipeline and 85 bridge MIDDLEs
- Test 4: HEADER_NEUTRAL — dark-pipeline line-1 concentration matches general HT (delta +0.4pp)
- Test 5: HT_ALIGNED — JS(dark,HT)=0.0005 vs JS(dark,grammar)=0.0109; 22x closer to HT

### PP Pipeline Atom Decomposition (C1140-C1142) -- Phase: PP_PIPELINE_ATOM_DECOMPOSITION (Phase 408)

Verifies the 404 PP MIDDLE partition and decomposes dark-pipeline compound MIDDLEs into atoms. Discovers that 96.5% of dark-pipeline compounds contain bridge atoms as building blocks.

| # | Statement | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1140** | **PP Pipeline Is a Complete Four-Way Partition** (85 bridge + 4 non-bridge matched + 300 dark pipeline + 15 phantom = 404; exhaustive and mutually exclusive; non-bridge matched are c/ch/cho/otc, AUXILIARY-dominant edge cases; phantoms all ch/sh-prefixed with 0 A tokens) | 2 | A->B | -> [C1140_pp_pipeline_complete_partition.md](C1140_pp_pipeline_complete_partition.md) |
| **1141** | **Dark Pipeline Compounds Built from Bridge Atoms** (86% of atom types are bridge MIDDLEs, 91.6% of occurrences; 96.5% of compounds contain >= 1 bridge atom; 50 unique atoms: 43 BRIDGE, 6 DARK_PIPELINE, 1 OTHER; mean 1.44 atoms/compound) | 2 | B morphology | -> [C1141_dark_pipeline_bridge_atom_substrate.md](C1141_dark_pipeline_bridge_atom_substrate.md) |
| **1142** | **Dark Pipeline Uses Modified Construction Grammar** (50% agreement with C1065 ordering; gateway/terminal positioning preserved; 25 dark-exclusive atoms extend grammar pool; section concentration NOT atom-driven, p=0.303) | 2 | B morphology | -> [C1142_dark_pipeline_modified_construction_grammar.md](C1142_dark_pipeline_modified_construction_grammar.md) |

**Phase 408 findings (PP Pipeline Atom Decomposition):**
- Test 1: PARTITION_COMPLETE -- 85 + 4 + 300 + 15 = 404, exhaustive, mutually exclusive
- Test 2: BRIDGE_ATOMS_PREVALENT -- 86% of atom types are bridges, 91.6% of occurrences, 96.5% compound coverage
- Test 3: OVERLAPPING_POOLS -- Jaccard(grammar,dark)=0.481; 25 shared, 25 dark-exclusive atoms
- Test 4: ATOM_SECTION_INDEPENDENT -- permutation p=0.303; section concentration not atom-driven
- Test 5: MODIFIED_GRAMMAR -- 50% agreement with C1065 pairs; gateway/terminal positioning preserved

---

### Dark Pipeline Internal Architecture (C1143-C1148) -- Phase: DARK_PIPELINE_INTERNAL_ARCHITECTURE (Phase 409)

Probes the internal structure of the 300 dark-pipeline MIDDLEs. 6-test battery: atom characterization, ordering divergence source, slot grammar, folio density regression, line position, frequency modulation decomposition.

| # | Statement | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1143** | **Dark-Exclusive and Shared Atoms Have Equivalent Section Profiles** (25 dark-exc vs 25 shared: MW U z=1.61, p=0.107; dark-exc rarer (15.2 vs 41.5 freq) and less spread (11.4 vs 22.1 folios) but same section Herfindahl) | 2 | B morphology | -> [C1143_dark_exclusive_atom_equivalence.md](C1143_dark_exclusive_atom_equivalence.md) |
| **1144** | **Dark Pipeline Ordering Divergence Is Genuine Grammar Modification** (Fisher exact on dark-exc presence x match/mismatch: OR=3.33, p=0.592; C1065 mismatches NOT explained by atom pool) | 2 | B morphology | -> [C1144_ordering_divergence_is_grammar_modification.md](C1144_ordering_divergence_is_grammar_modification.md) |
| **1145** | **Dark-Exclusive and Shared Atoms Occupy Equivalent Positional Slots** (chi-sq=1.74, df=2, p=0.421; INITIAL/MEDIAL/FINAL distribution indistinguishable between atom types in 77 multi-atom compounds) | 2 | B morphology | -> [C1145_atom_slot_uniformity.md](C1145_atom_slot_uniformity.md) |
| **1146** | **Dark Pipeline Token Density Anti-Correlates with Bridge Tokens** (r=-0.865 overall; within-section r=-0.82 to -0.88 in all 4 sections; section R²=0.193; 80.7% of variance within-section; complementary distribution) | 2 | B, A->B | -> [C1146_dark_pipeline_bridge_anticorrelation.md](C1146_dark_pipeline_bridge_anticorrelation.md) |
| **1147** | **Dark Pipeline Tokens Are Interior-Enriched Within Lines** (73.2% MIDDLE vs general HT 67.7%; chi-sq=23.2, p<0.0001; boundary rate 26.8% vs HT 32.3%; consistent across par line-1 and body) | 2 | B, line structure | -> [C1147_dark_pipeline_interior_positioned.md](C1147_dark_pipeline_interior_positioned.md) |
| **1148** | **Dark Pipeline Frequency Profiles Are Hyper-Modulated Across Sections** (mean JS=0.483, 3.9x C1134 baseline of 0.124; dark pipeline is primary vehicle for section-level vocabulary modulation) | 2 | B, section differentiation | -> [C1148_dark_pipeline_hyper_modulated.md](C1148_dark_pipeline_hyper_modulated.md) |

**Phase 409 findings (Dark Pipeline Internal Architecture):**
- Test 1: EQUIVALENT -- dark-exc and shared atoms same section concentration (MW p=0.107)
- Test 2: GRAMMAR_MODIFICATION -- C1065 mismatches not atom-pool driven (Fisher p=0.592)
- Test 3: SLOT_UNIFORM -- both atom types occupy same INITIAL/MEDIAL/FINAL slots (chi-sq p=0.421)
- Test 4: HT_COVARIATE -- dark-bridge anti-correlation r=-0.865; section R²=0.193
- Test 5: INTERIOR_ENRICHED -- 73.2% MIDDLE vs HT 67.7% (chi-sq p<0.0001)
- Test 6: HYPER_MODULATED -- mean JS=0.483, 3.9x C1134 baseline

---

### Folio Balance Characterization (C1149-C1151) -- Phase: FOLIO_BALANCE_CHARACTERIZATION (Phase 410)

Tests whether the bridge/dark folio balance axis (derived from C1146) is structurally informative. 5-test battery: section association, dynamical archetype independence, AXM uniformity, kernel profile coupling, paragraph count.

| # | Statement | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1149** | **Vocabulary Balance Is Orthogonal to Dynamical Archetypes** (ARI=-0.002, chi-sq p=0.807; Spearman rho=0.001 vs AXM; balance, dynamics, and section are three independent structural axes) | 2 | B, cross-system, dynamics | -> [C1149_balance_dynamics_independence.md](C1149_balance_dynamics_independence.md) |
| **1150** | **Dark-Dominant Folios Shift Kernel Profile Within Section** (k_frac drops 0.314→0.226 in dark-dominant; h_frac rises 0.100→0.135; survives within-section in RECIPE_B p=0.002) | 2 | B, kernel, section | -> [C1150_balance_kernel_coupling.md](C1150_balance_kernel_coupling.md) |
| **1151** | **Balance Distribution Is Section-Structured** (chi-sq=29.95, df=6, p<0.0001; BIO=bridge-dominant, PHARMA=dark-dominant, RECIPE_B=balanced-dominant, HERBAL_B=mixed) | 2 | B, section differentiation | -> [C1151_balance_section_profiles.md](C1151_balance_section_profiles.md) |

**Phase 410 findings (Folio Balance Characterization):**
- Test 1: SECTION_STRUCTURED -- balance distribution strongly associated with section (chi-sq p<0.0001)
- Test 2: ARCHETYPE_ORTHOGONAL -- balance orthogonal to dynamical archetypes (ARI=-0.002)
- Test 3: AXM_UNIFORM -- AXM self-transition identical across balance groups (KW p=0.967)
- Test 4: KERNEL_DIFFERENTIATED -- dark-dominant folios shift kernel profile (k p=0.002, survives RECIPE_B within-section)
- Test 5: PARAGRAPH_UNIFORM -- paragraph count not differentiated by balance (KW p=0.152)
- Overall: BALANCE_PARTIALLY_INFORMATIVE (2 of 5 tests differentiated)

---

### Section-Conditioned Generative Fidelity (C1152-C1154) -- Phase: SECTION_CONDITIONED_GENERATIVE_FIDELITY (Phase 411)

Tests whether section-conditioned M2 captures folio-level variation. 5-test battery comparing real inter-folio heterogeneity against section-M2 synthetic heterogeneity across class distributions, AXM dynamics, and kernel profiles.

| # | Statement | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1152** | **Section-M2 Captures Vocabulary Composition but Not Sequential Dynamics** (class dist ratio 1.48x near-captured; AXM spread 1.76x uncaptured; kernel profile 1.79x uncaptured; 87% folios improved by section-conditioning; vocabulary is section-determined, dynamics are program-specific) | 2 | B, section, generative | -> [C1152_vocabulary_dynamics_layer_separation.md](C1152_vocabulary_dynamics_layer_separation.md) |
| **1153** | **Generative Design Freedom Is ~40%** (32.4% class-dist + 43.2% AXM + 44.0% kernel uncaptured; aggregate 39.9%; AXM consistent with C1035's 57%; lower than C1016's 66.3% because class distribution IS section-captured) | 2 | B, generative, dynamics | -> [C1153_generative_design_freedom.md](C1153_generative_design_freedom.md) |
| **1154** | **k-Kernel and e-Kernel Variance Are Universally Program-Specific** (k ratio 1.82-2.32x, e ratio 1.76-2.21x across all sections; h-kernel section-determined in BIO/HERBAL/COSMO (0.74-1.29x) but program-specific in STARS_RECIPE (2.18x)) | 2 | B, kernel, section | -> [C1154_k_kernel_universally_program_specific.md](C1154_k_kernel_universally_program_specific.md) |

**Phase 411 findings (Section-Conditioned Generative Fidelity):**
- Test 1: SECTION_CAPTURES -- class distribution variance ratio 1.48x (near-captured)
- Test 2: AXM_UNCAPTURED -- AXM self-transition spread ratio 1.76x (BIO 2.56x, STARS_RECIPE 2.24x)
- Test 3: KERNEL_UNCAPTURED -- kernel profile variance ratio 1.79x (k/e ~2x, h variable)
- Test 4: SECTION_HELPS -- 87% of folios improved by section-conditioning
- Test 5: PARTIALLY_PROGRAM_SPECIFIC -- design freedom 39.9%
- Overall: SECTION_PARTIALLY_CAPTURES (2.5/5.0)

### Paragraph Kernel Dynamics (C1155) -- Phase: PARAGRAPH_KERNEL_DYNAMICS (Phase 412)

Tests whether within-folio paragraph kernel diversity mediates the C1035 AXM residual (57% irreducible). 5-test battery: kernel heterogeneity, trajectory slope diversity, type entropy, incremental R², within-section validation. All tests negative — paragraph dynamics are orthogonal to AXM residual.

| # | Statement | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1155** | **Paragraph Kernel Dynamics Do Not Mediate the AXM Residual** (kernel heterogeneity dR²=0.0012, trajectory slope variance dR²=0.0014, type entropy dR²=0.0002; all with negative LOO; within-section rho all <0.16; C1035 residual confirmed closed at paragraph level) | 2 | B, paragraph, kernel, AXM | -> [C1155_paragraph_kernel_dynamics_do_not_mediate_residual.md](C1155_paragraph_kernel_dynamics_do_not_mediate_residual.md) |

**Phase 412 findings (Paragraph Kernel Dynamics):**
- Test 1: UNCORRELATED -- composite heterogeneity vs AXM rho=-0.187, p=0.92
- Test 2: TRAJECTORY_NEUTRAL -- slope variance vs AXM rho=0.122, p=0.90
- Test 3: TYPE_ENTROPY_NEUTRAL -- type entropy vs AXM rho=0.138, p=0.90
- Test 4: RESIDUAL_IRREDUCIBLE_CONFIRMED -- best dR²=0.0014, all LOO negative
- Test 5: SECTION_CONFOUND_ONLY -- all within-section |rho| < 0.16
- Overall: PARAGRAPH_KERNEL_DYNAMICS_SIGNAL_MARGINAL

### Line Transition Dynamics (C1156-C1157) -- Phase: LINE_TRANSITION_DYNAMICS (Phase 413)

Tests whether within-line position structure constrains token transition dynamics and whether it mediates the C1035 AXM residual. 5-test battery: zone transition divergence, boundary spectral properties, position-conditioned generation, AXM residual regression, section invariance. **First predictor to break through the C1035 barrier.**

| # | Statement | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1156** | **Line Position Structures Class Transitions** (49×49 matrix differs by ENTRY/INTERIOR/EXIT zone; JSD 0.22-0.33, all p<0.001; AXM self-transition gradient 0.730→0.704→0.633; spectral gap shifts 0.939→0.883→0.900; section-dependent KW p<0.0001) | 2 | B, line, transitions | -> [C1156_line_position_structures_transitions.md](C1156_line_position_structures_transitions.md) |
| **1157** | **Boundary Divergence Mediates the AXM Residual** (per-folio boundary divergence adds dR²=0.0845, F=14.15, p=0.0004 to C1035 baseline; LOO improves 0.433→0.512; rho=-0.732 vs AXM self; first predictor to break C1035 barrier; position-conditioned M2 does NOT improve generation — descriptive not generative) | 2 | B, line, AXM residual | -> [C1157_boundary_divergence_mediates_axm_residual.md](C1157_boundary_divergence_mediates_axm_residual.md) |

**Phase 413 findings (Line Transition Dynamics):**
- Test 1: POSITION_STRUCTURED -- JSD(entry,interior)=0.224, all p<0.001 (1000 perms)
- Test 2: BOUNDARY_REGIME_SHIFT -- AXM self 0.730→0.633, spectral gap delta=0.055
- Test 3: POSITION_CONDITIONING_NEUTRAL -- M2p 0/3 metrics improved
- Test 4: POSITION_MEDIATES_RESIDUAL -- dR²=0.0845, F=14.15, p=0.0004, LOO 0.433→0.512
- Test 5: POSITION_SECTION_DEPENDENT -- KW H=54.54, p<0.0001
- Overall: LINE_POSITION_MEDIATES_RESIDUAL

### Boundary Divergence Decomposition (C1158-C1161) -- Phase: BOUNDARY_DIVERGENCE_DECOMPOSITION (Phase 414)

Decomposes the C1157 boundary divergence finding. 5-test battery: entry/exit decomposition, transition cell analysis, section independence, vocabulary mediation, gatekeeper mediation. **Key finding:** entry dominates (3.5× exit), effect is routing shifts not AXM persistence, section-confounded but independently predictive, gatekeeper-partial.

| # | Statement | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1158** | **Entry Divergence Dominates Boundary Divergence Effect** (entry dR²=0.098 vs exit dR²=0.028, 3.5×; entry is the "reset to base" intensity; contradicts gatekeeper hypothesis) | 2 | B, line, AXM | -> [C1158_entry_dominates_boundary_divergence.md](C1158_entry_dominates_boundary_divergence.md) |
| **1159** | **Boundary Divergence Is a Routing Shift, Not AXM Persistence Decay** (AXM→AXM only 3.2% of total delta; dominant: AXm→AXM +0.124, FQ→AXM +0.103 at entry; CC→AXM -0.296 at exit; inter-state routing, not self-transition) | 2 | B, line, transitions | -> [C1159_boundary_divergence_is_routing_shift.md](C1159_boundary_divergence_is_routing_shift.md) |
| **1160** | **Boundary Divergence Is Section-Confounded but Carries Independent Signal** (section R²=0.70 on BD; partial rho=-0.459 vs AXM controlling section; BD adds dR²=0.135 beyond section-only AXM model) | 2 | B, line, section | -> [C1160_boundary_divergence_section_confounded_but_independent.md](C1160_boundary_divergence_section_confounded_but_independent.md) |
| **1161** | **Gatekeeper Classes Partially Mediate Boundary Divergence** (excluding gatekeepers reduces dR² by 30.5%; effect survives: GK-free rho=-0.673, dR²=0.059, p=0.006; GK density uncorrelated with BD) | 2 | B, line, gatekeeper | -> [C1161_gatekeeper_partial_mediation.md](C1161_gatekeeper_partial_mediation.md) |

**Phase 414 findings (Boundary Divergence Decomposition):**
- Test 1: ENTRY_DOMINANT -- entry dR²=0.098 vs exit dR²=0.028 (3.5×)
- Test 2: ROUTING_SHIFT -- AXM→AXM only 3.2% of total; inter-state routing dominates
- Test 3: SECTION_CONFOUNDED -- R²=0.70 but partial rho=-0.459 still significant
- Test 4: VOCABULARY_INDEPENDENT -- zero coefficient shrinkage
- Test 5: GATEKEEPER_PARTIAL -- dR² drops 30.5% without gatekeepers
- Overall: BOUNDARY_DIVERGENCE_PARTIALLY_EXPLAINED

### Entry Reset Mechanism (C1162-C1165) -- Phase: ENTRY_RESET_MECHANISM (Phase 415)

Decomposes C1158's entry dominance finding: what opener properties drive entry divergence variation? 5-test battery: opener role distribution, PREFIX family distribution, opener-follower routing, entry divergence mediation, AXM residual extension. **Key finding:** AXM return rate at entry (rho=0.841 with AXM self-transition) is the single most powerful predictor; extends residual by dR²=0.111 beyond entry divergence, LOO 0.543→0.696.

| # | Statement | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1162** | **Opener Role Does Not Predict Entry Divergence** (R²=0.128; no role |rho|≥0.30; role entropy uncorrelated; entry mechanism operates below role-level identity) | 2 | B, line, opener | -> [C1162_opener_role_does_not_predict_entry_divergence.md](C1162_opener_role_does_not_predict_entry_divergence.md) |
| **1163** | **AXM Return Rate Dominates Entry Mechanism** (rho=0.841 with AXM self; rho=-0.510 with entry div; R²=0.318 on entry div; routing not identity drives entry reset) | 2 | B, line, opener, routing | -> [C1163_axm_return_rate_dominates_entry_mechanism.md](C1163_axm_return_rate_dominates_entry_mechanism.md) |
| **1164** | **Opener Routing Partially Mediates Entry Divergence** (shrinkage=0.406; entry div retains signal partial rho=-0.293 p=0.013; opener features dR²=0.159 vs entry div dR²=0.068; combined R²=0.815 LOO=0.669) | 2 | B, line, opener, AXM | -> [C1164_opener_routing_partially_mediates_entry_divergence.md](C1164_opener_routing_partially_mediates_entry_divergence.md) |
| **1165** | **AXM Return Rate Extends Residual Beyond Entry Divergence** (dR²=0.111, F=30.95, p<0.000001, LOO 0.543→0.696; total bundle dR²=0.180 vs C1035; irreducible ~57%→~32%) | 2 | B, folio, AXM residual | -> [C1165_axm_return_rate_extends_residual.md](C1165_axm_return_rate_extends_residual.md) |

**Phase 415 findings (Entry Reset Mechanism):**
- Test 1: ROLE_WEAK -- opener role R²=0.128 on entry divergence; no significant roles
- Test 2: PREFIX_WEAK -- prefix entropy rho=-0.493 (significant) but R²=0.292 under threshold
- Test 3: ROUTING_EXPLAINS -- AXM return rate rho=-0.510, R²=0.318
- Test 4: OPENER_PARTIAL_MEDIATION -- shrinkage=0.41; entry div retains independent signal
- Test 5: OPENER_EXTENDS_RESIDUAL -- AXM return rate dR²=0.111, LOO +0.153
- Overall: MULTI_FACETED_ENTRY_MECHANISM

### Exit Divergence Symmetry (C1166-C1168) -- Phase: EXIT_DIVERGENCE_SYMMETRY (Phase 416)

Tests whether exit boundary carries independent signal beyond the entry bundle (C1035 + entry_div + AXM_return). 5-test battery: exit divergence baseline, closer routing profile, gatekeeper exit mechanism, exit incremental signal, dual boundary architecture. **Key finding:** Exit JSD is redundant after entry control, but AXM departure rate (directional exit routing) carries independent signal (dR²=0.035, LOO +0.049). Dual model: R²=0.852, LOO=0.732, all sections benefit. Irreducible ~57%→~27%.

| # | Statement | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1166** | **Exit Divergence Redundant After Entry Control** (bivariate rho=-0.710 but partial rho=-0.097 p=0.101 after entry bundle; exit JSD collinear with entry JSD rho=0.697) | 2 | B, line, boundary, exit | -> [C1166_exit_divergence_redundant_after_entry_control.md](C1166_exit_divergence_redundant_after_entry_control.md) |
| **1167** | **AXM Departure Rate at Exit Extends Residual** (dR²=0.035, F=11.80, p=0.0012, LOO 0.696→0.745; closer features R²=0.338; AXM departure rho=0.509 with exit div) | 2 | B, folio, AXM residual, exit | -> [C1167_axm_departure_rate_extends_residual.md](C1167_axm_departure_rate_extends_residual.md) |
| **1168** | **Dual Boundary Architecture** (entry+exit independent channels; dual R²=0.852 LOO=0.732; exit dR²=0.039 LOO+0.036; all 3 sections benefit; irreducible ~57%→~27%) | 2 | B, folio, AXM residual, boundary | -> [C1168_dual_boundary_architecture.md](C1168_dual_boundary_architecture.md) |

**Phase 416 findings (Exit Divergence Symmetry):**
- Test 1: EXIT_REDUNDANT -- exit JSD partial rho=-0.097 after entry bundle control
- Test 2: CLOSER_STRUCTURED -- closer features R²=0.338, AXM departure rho=0.509
- Test 3: GATEKEEPER_PARTIAL -- GK exit + hazard exit R²=0.108
- Test 4: EXIT_EXTENDS -- AXM departure dR²=0.035, F=11.80, p=0.0012, LOO +0.049
- Test 5: DUAL_CHANNEL -- dual R²=0.852, LOO=0.732, all sections benefit
- Overall: EXIT_INDEPENDENT_CHANNEL

### Residual Freedom Characterization (C1169) -- Phase: RESIDUAL_FREEDOM_CHARACTERIZATION (Phase 417)

Tests whether the ~27% AXM residual from the dual boundary model (C1168, R²=0.852, LOO=0.732) is genuinely irreducible or contains unmeasured structure. 5-test exhaustive battery: 23-predictor univariate scan (Holm-Bonferroni), random forest nonlinearity detection (500 trees, 200-permutation test), spatial autocorrelation (manuscript order), design freedom profile (C458 asymmetry, regime homogeneity), gated OLS extension. **Result: RESIDUAL_GENUINELY_FREE.** Zero signal across all tests. AXM residual decomposition program (Phases 412-417) is CLOSED.

| # | Statement | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1169** | **AXM Residual Closed — ~27% Is Genuine Design Freedom** (23 candidates: 0 Holm-sig; RF CV R²=-0.14 perm p=0.375; lag-1 AC=0.102 p=0.378; KW regime p=0.998; C458 symmetric; T5 gated closed) | 2 | B, folio, AXM residual, closure | -> [C1169_axm_residual_closed_genuine_design_freedom.md](C1169_axm_residual_closed_genuine_design_freedom.md) |

**Phase 417 findings (Residual Freedom Characterization):**
- Test 1: UNIVARIATE_CLOSED -- 0/23 survive Holm-Bonferroni; strongest e_frac rho=-0.239
- Test 2: NONLINEAR_CLOSED -- RF CV R²=-0.141, permutation p=0.375
- Test 3: SPATIALLY_RANDOM -- lag-1=0.102, perm p=0.378, runs p=0.902
- Test 4: SYMMETRIC_FREEDOM -- no C458 asymmetry, KW regime p=0.998
- Test 5: RESIDUAL_CLOSED -- gated (T1+T2 both closed)
- Overall: RESIDUAL_GENUINELY_FREE

### LINK Functional Architecture (C1170-C1174) -- Phase: LINK_FUNCTIONAL_ARCHITECTURE (Phase 418)

5-test battery characterizing LINK (`ol` substring, 13.2% of B, 3,047 tokens, 801 types) as the last major uncharacterized token population. Tests: vocabulary stratification (role × ol_position), cross-role consistency, section decomposition, macro-automaton dynamics, boundary architecture. **Key finding: LINK_MORPHOLOGICAL_ARTIFACT.** The `ol` substring is a morphological component recruited differently by each role, not a unified functional layer. CC uses it as standalone operator, AX as prefix, EN within MIDDLE. BIO's 2× excess is SPAN-targeted (EN_SPAN 4.65×). Boundary enrichment is passive (no divergence correlation).

| # | Statement | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1170** | **LINK Vocabulary Stratified by Role** (chi2=1493, V=0.404; CC=1 type all MIDDLE; AX=49 types 59% PREFIX; EN=12 types MIDDLE/SPAN/SUFFIX; UN=735 types TTR=0.629) | 2 | B, LINK, vocabulary, role | -> [C1170_link_vocabulary_stratified_by_role.md](C1170_link_vocabulary_stratified_by_role.md) |
| **1171** | **LINK Behavior Is Role-Dominant** (4/4 roles sig different MW p<0.05; cross-role JSD LINK=0.014 ≈ non-LINK=0.013; no unified substrate) | 2 | B, LINK, cross-role, position | -> [C1171_link_behavior_role_dominant.md](C1171_link_behavior_role_dominant.md) |
| **1172** | **BIO LINK Excess Is SPAN-Targeted** (BIO 20.2%; EN_SPAN 4.65×, AX_SPAN 2.15×, UN_SPAN 1.88×; MIDDLE depleted 0.47×; section×role chi2=82.2 p<1e-9) | 2 | B, BIO, LINK, section | -> [C1172_bio_link_excess_span_targeted.md](C1172_bio_link_excess_span_targeted.md) |
| **1173** | **LINK Boundary Enrichment Is Passive** (entry 17.2% interior 12.4% exit 15.3% chi2=54.5; entry rho=-0.059 p=0.074; exit rho=-0.151 p=0.108; dynamics 1.09× boundary) | 2 | B, LINK, boundary, dynamics | -> [C1173_link_boundary_enrichment_passive.md](C1173_link_boundary_enrichment_passive.md) |
| **1174** | **LINK Is Morphological Artifact** (synthesis: STRATIFIED + ROLE_DOMINANT + PASSIVE → `ol` is morphological component not functional layer; revises C366/C609 interpretation) | 2 | B, LINK, synthesis | -> [C1174_link_is_morphological_artifact.md](C1174_link_is_morphological_artifact.md) |

**Phase 418 findings (LINK Functional Architecture):**
- Test 1: STRATIFIED -- V=0.404, CC=standalone `ol`, AX=59% PREFIX, 69% hapax
- Test 2: ROLE_DOMINANT -- 0/4 consistent, cross-role JSD≈baseline
- Test 3: BIO_TARGETED_ENRICHMENT -- EN_SPAN 4.65×, MIDDLE depleted in BIO
- Test 4: LINK_PASSIVE_PARTICIPANT -- 1.09× boundary, CC-dominated occupancy
- Test 5: BOUNDARY_ENRICHED_PASSIVE -- no divergence correlation
- Overall: LINK_MORPHOLOGICAL_ARTIFACT

### Dark Pipeline Combinatorics (C1175-C1178) -- Phase: DARK_PIPELINE_COMBINATORICS (Phase 419)

5-test battery investigating combinatorial rules governing dark-pipeline compound MIDDLEs (300 MIDDLEs, 200 compound, 50 atoms). **Key findings:** C475 is a necessary gate (100% recall) but only 7.9% of pair space occupied (C1175). Section hyper-modulation (3.9x) is atom-selection-dominated: multiplicative atom model R²=0.781 (C1176). Dark ordering grammar is consistent with C1065 (4/4 match, revises C1142's 50% from low-count noise, C1177). Phantom MIDDLEs are morphologically isolated ch/sh naming slots with no productive analogs in dark pipeline (C1178).

| # | Statement | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1175** | **Dark Compound Pair Space C475-Gated** (recall=1.000 precision=0.134; 71/903 pairs occupied 7.9%; parallels C1028 curation) | 2 | B, dark pipeline, combinatorics | -> [C1175_dark_compound_pair_space_c475_gated.md](C1175_dark_compound_pair_space_c475_gated.md) |
| **1176** | **Section Hyper-Modulation Atom-Selection-Dominated** (multiplicative model R²=0.781 pseudo-R²=0.677; atoms carry section signal, compounds inherit) | 2 | B, dark pipeline, section, atoms | -> [C1176_section_hyper_modulation_atom_selection_dominated.md](C1176_section_hyper_modulation_atom_selection_dominated.md) |
| **1177** | **Dark Ordering Consistent with C1065** (4/4 match 0 mismatch; revises C1142 50% from low-count noise; same grammar, sparse coverage) | 2 | B, dark pipeline, ordering grammar | -> [C1177_dark_ordering_consistent_with_c1065.md](C1177_dark_ordering_consistent_with_c1065.md) |
| **1178** | **Phantom MIDDLEs Morphologically Isolated** (0/15 valid-unfilled; 11 partial 4 invalid; ch/sh-initial MIDDLE is dead naming pattern) | 2 | B, dark pipeline, phantoms | -> [C1178_phantom_middles_morphologically_isolated.md](C1178_phantom_middles_morphologically_isolated.md) |

**Phase 419 findings (Dark Pipeline Combinatorics):**
- Test 1: WEAKLY_GATED -- C475 recall=1.0, precision=0.134, 7.9% occupancy
- Test 2: ATOM_SELECTION_DOMINATED -- R²=0.781, pseudo-R²=0.677
- Test 3: AMBIGUOUS -- intensity r=-0.215 > diversity r=-0.035
- Test 4: CONSISTENT_GRAMMAR -- 4/4 C1065 match, 100% agreement
- Test 5: MIXED_VALIDITY -- 0 valid, 11 partial, 4 invalid
- Overall: MULTI_MECHANISM_COMBINATORICS

### Sister-Pair Mechanism (C1179-C1187) -- Phase: SISTER_PAIR_MECHANISM (Phase 420)

Sister-pair choice (ch vs sh, C639 52.9% unexplained) is a boundary control knob, not free variation. Position mediates +12.8% variance, dynamics correlate (AXM -0.250, hazard +0.255), entry divergence coupled (rho=0.312). 8-test battery.

| # | Statement | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1179** | **Sister Choice Structured in Slot** (14/174 Bonferroni-significant MIDDLE+SUFFIX slots; aggregate chi2=709.8 p<0.0001) | 2 | B, sister pairs, within-class | -> [C1179_sister_choice_structured_in_slot.md](C1179_sister_choice_structured_in_slot.md) |
| **1180** | **Sister Choice Positionally Mediated** (delta-R2=0.128 LOO=0.097; ch=0.487 sh=0.395 gap=0.092; extends C929) | 2 | B, sister pairs, position | -> [C1180_sister_choice_positionally_mediated.md](C1180_sister_choice_positionally_mediated.md) |
| **1181** | **Sister Choice Dynamically Consequential** (AXM partial rho=-0.250 p=0.032; hazard +0.255 p=0.028; ch-heavy = higher hazard) | 2 | B, sister pairs, dynamics | -> [C1181_sister_choice_dynamically_consequential.md](C1181_sister_choice_dynamically_consequential.md) |
| **1182** | **Sister Concentration Moderate Consistency** (ICC=0.317; 32% folio-determined, 68% paragraph-variable; unimodal) | 2 | B, sister pairs, program structure | -> [C1182_sister_concentration_moderate_consistency.md](C1182_sister_concentration_moderate_consistency.md) |
| **1183** | **Sister Bridge/Dark Independent** (all partial rho <0.16 after section control; vocabulary pipeline orthogonal) | 2 | B, sister pairs, vocabulary | -> [C1183_sister_bridge_dark_independent.md](C1183_sister_bridge_dark_independent.md) |
| **1184** | **ch/sh and ok/ot Independent Axes** (partial rho=0.204 p=0.066; OPPOSITE positional asymmetries; two within-class dimensions) | 2 | B, sister pairs, within-class | -> [C1184_ch_sh_ok_ot_independent_axes.md](C1184_ch_sh_ok_ot_independent_axes.md) |
| **1185** | **Sister Successor Routing MIDDLE-Dependent** (global p=0.034; 5/102 strata significant; not universal; C121 preserved) | 2 | B, sister pairs, transitions | -> [C1185_sister_successor_middle_dependent.md](C1185_sister_successor_middle_dependent.md) |
| **1186** | **Sister Boundary Coupled** (entry JSD partial rho=0.312 p=0.004; opener ch frac rho=0.455; ch-heavy = divergent entries) | 2 | B, sister pairs, boundary | -> [C1186_sister_boundary_coupled.md](C1186_sister_boundary_coupled.md) |
| **1187** | **Sister Mechanism: BOUNDARY_CONTROL_KNOB** (synthesis: structured, positional, dynamical, boundary-coupled; reduces C639 unexplained from 52.9% to ~40%) | 2 | B, sister pairs, synthesis | -> [C1187_sister_mechanism_boundary_control_knob.md](C1187_sister_mechanism_boundary_control_knob.md) |

**Phase 420 findings (Sister-Pair Mechanism):**
- SP-0: STRUCTURED_IN_SLOT -- 14/174 slots significant, chi2=709.8
- SP-1: POSITIONAL_MEDIATION -- delta-R2=0.128, LOO confirmed
- SP-2: DYNAMICALLY_CONSEQUENTIAL -- AXM -0.250, hazard +0.255
- SP-3: MODERATE_CONSISTENCY -- ICC=0.317
- SP-4: BRIDGE_WEAK -- independent of pipeline
- SP-5: WEAK_COUPLING -- ch/sh and ok/ot independent
- SP-6: MIDDLE_DEPENDENT -- 5/102 strata, global p=0.034
- SP-7: BOUNDARY_COUPLED -- entry JSD rho=0.312
- Overall: BOUNDARY_CONTROL_KNOB

---

### Sister Entry Divergence Extension (C1188-C1189) -- Phase: SISTER_ENTRY_DIVERGENCE_EXTENSION (Phase 421)

Pre-registered minimal model comparison testing whether opener sister-pair composition independently predicts entry divergence beyond the existing boundary architecture. **Result: SISTER_ENTRY_LEVER_ABSENT.** opener_ch_frac adds ΔLOO-R²=-0.020 (below 0.02 threshold, actually hurts prediction). Coefficient sign NEGATIVE (wrong direction). All sections absent. AXM mediation absorbed. C1186's correlation is fully mediated by opener-routing features (C1163-C1165).

| # | Statement | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1188** | **Sister Entry Divergence Absent** (ΔLOO-R²=-0.020; dR²=0.0006 F=0.12 p=0.73; coefficient sign wrong; all sections negative) | 2 | B, sister pairs, boundary architecture | -> [C1188_sister_entry_divergence_absent.md](C1188_sister_entry_divergence_absent.md) |
| **1189** | **Sister Is Proxy Not Lever** (C1186 correlation mediated by C1163-C1165 opener-routing features; boundary architecture structurally complete; C1169 residual confirmed irreducible by sister) | 2 | B, sister pairs, boundary architecture, synthesis | -> [C1189_sister_proxy_not_lever.md](C1189_sister_proxy_not_lever.md) |

**Phase 421 findings (Sister Entry Divergence Extension):**
- T1: dR²(S vs B3) = 0.0006, F=0.12, p=0.73 — sister adds nothing to full-sample R²
- T2: ΔLOO-R² = -0.020 — sister HURTS cross-validation (SISTER_ABSORBED)
- T3: All sections negative (B: -0.40, H: -0.59, S: -0.24) (SECTION_ABSENT)
- T4: beta = -0.003, sign wrong, unstable under ablation (SIGN_WRONG)
- T5: AXM mediation ΔLOO = -0.014, F=0.32, p=0.57 (AXM_ABSORBED)
- Overall: SISTER_ENTRY_LEVER_ABSENT

### MIDDLE Behavioral Atomicity (C1190) -- Phase: COMPOUND_DECOMPOSITION

Single characters are genuine behavioral atoms of MIDDLE composition. Multi-character MIDDLEs inherit behavioral profiles by additive composition of component atoms. Validated by permutation test: r=0.754 (no-kernel), z=3.32, p<0.001, 0/1000 permutations. Scope corrected by Phase 422: additive composition is MIDDLE-specific; PREFIX and SUFFIX follow different compositional rules (see C1191).

| # | Statement | Tier | Scope | Link |
|---|-----------|------|-------|------|
| **1190** | **MIDDLE Behavioral Atomicity** (multi-character MIDDLEs inherit behavioral profiles from component single-char atoms by additive composition; r=0.754 no-kernel, z=3.32, p<0.001; 0/1000 permutations; scope: MIDDLE only, PREFIX/SUFFIX per C1191) | 2 | B, morphology, atomic composition | -> [C1190_middle_behavioral_atomicity.md](C1190_middle_behavioral_atomicity.md) |

### Position-Dependent Behavioral Composition (C1191) -- Phase: CROSSWORD_GLOSS_VALIDATION (Phase 422)

Atoms carry consistent behavioral IDENTITY across positions (15/18 CONSISTENT, CPC >= 0.7) but follow position-specific COMPOSITIONAL RULES. MIDDLE: additive (C1190). PREFIX: emergent (c, h, s, p degrade predictions; consistent with C929 PREFIX specialization). SUFFIX: systematic shift (r=0.892, all atoms shift behavior consistently). Near-identical behavioral pairs found: k-t (r=0.993), d-o (r=0.945).

| # | Statement | Tier | Scope | Link |
|---|-----------|------|-------|------|
| **1191** | **Position-Dependent Behavioral Composition** (atoms carry consistent identity across PREFIX/MIDDLE/SUFFIX but composition rules differ: MIDDLE=additive, PREFIX=emergent, SUFFIX=systematic shift r=0.892; 15/18 atoms cross-positionally consistent; c,h,s,p PREFIX-emergent; k-t near-identical r=0.993) | 2 | B, morphology, positional composition | -> [C1191_position_dependent_composition.md](C1191_position_dependent_composition.md) |

### Positional Atomicity (C1192-C1194) -- Phase: POSITIONAL_ATOMICITY (Phase 423)

Position-specific atom profiles reveal universal additive composition in SUFFIX (r=0.953, p=0.029), compositional duality in PREFIX (core prefixes emergent, extended prefixes additive), and discrimination of previously identical atom pairs (k-t, d-o, p-t, l-r all separate). Discrete role clustering found: PREFIX shifts cluster into 2 groups {a,d,o,q} vs rest; not a continuum.

| # | Statement | Tier | Scope | Link |
|---|-----------|------|-------|------|
| **1192** | **SUFFIX Additive Composition** (SUFFIX compounds compose additively from position-specific atom profiles; r=0.953, z=2.59, p=0.029; extends C1190 to SUFFIX; cross-position baseline r=0.676, improvement +0.277) | 2 | B, SUFFIX, composition | -> [C1192_suffix_additive_composition.md](C1192_suffix_additive_composition.md) |
| **1193** | **PREFIX Compositional Duality** (PREFIX compounds split into compositional class (ke/te/ka/po/pch, predictable from atom profiles) and emergent class (ch/sh/da/ot/ok/ol, opaque); maps to EXTENDED/CORE prefix classification; discrete role clustering k=2: {a,d,o,q} vs {c,e,f,h,k,l,p,r,s,t,y}) | 2 | B, PREFIX, composition | -> [C1193_prefix_compositional_duality.md](C1193_prefix_compositional_duality.md) |
| **1194** | **Position-Specific Pair Discrimination** (near-identical atom pairs separate under position-specific profiles: k-t 0.993->0.568, d-o 0.945->0.296, p-t 0.935->0.467, l-r 0.919->0.806; global identity was masking PREFIX distinctions; no true atom redundancy) | 2 | B, atoms, discrimination | -> [C1194_position_specific_pair_discrimination.md](C1194_position_specific_pair_discrimination.md) |

### Atom Gloss Audit (C1195-C1196) -- Phase: ATOM_GLOSS_AUDIT (Phase 424)

Validated atom glosses against compound evidence, assigned confidence tiers, generated autoglosses for 1144 compound MIDDLEs.

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1195** | **Atom Gloss Confidence Tiers** (18 atoms in 4 tiers: 8 LOCKED (k,e,h,y,i,n,a,m), 2 SOLID (d,t), 6 PLAUSIBLE (c,p,f,s,g,x), 3 WEAK (o,l,r); validated against 91 glossed compounds; 5 dictionary discrepancies fixed to match GLOSSING.md) | 2 | B, atoms, glossing | -> [C1195_atom_gloss_confidence_tiers.md](C1195_atom_gloss_confidence_tiers.md) |
| **1196** | **Autogloss Composition Coverage** (1144/1273 compound MIDDLEs auto-glossed from atom decomposition; confidence: 72 LOCKED, 86 SOLID, 289 PLAUSIBLE, 768 WEAK; 58 incomplete (q); 67.1% WEAK driven by 3 generic atoms o/l/r) | 2 | B, compounds, glossing | -> [C1196_autogloss_composition_coverage.md](C1196_autogloss_composition_coverage.md) |

### Atom Extensibility (C1197-C1199) -- Phase: ATOM_EXTENSIBILITY (Phase 425)

Only e and i support consecutive repetition; all other atoms are binary. Order within MIDDLEs is behaviorally irrelevant. Extension rates vary by section, paragraph position, and folio.

| # | Constraint | Tier | Scope | Location |
|---|-----------|------|-------|----------|
| **1197** | **Atom Extensibility Partition** (only e and i repeat consecutively at structural levels (1555/1554 tokens); 18 other atoms are binary (present once or absent); extends C901 from A to B; 129 ratio families exist) | 2 | B, atoms, extensibility | -> [C1197_atom_extensibility_partition.md](C1197_atom_extensibility_partition.md) |
| **1198** | **MIDDLE Order Irrelevance** (reordered MIDDLEs with identical composition show near-identical behavioral profiles: ke/ek r=0.999, kch/ckh r=0.995, eek/kee r=0.997; mean within-group r=0.967 vs between r=0.957; order does not alter distributional behavior) | 2 | B, composition, order | -> [C1198_middle_order_irrelevance.md](C1198_middle_order_irrelevance.md) |
| **1199** | **Extension Distributional Gradient** (ee-rate varies by section: S=24.5%, B=10.8%, p<0.001; headers depleted vs bodies 5.8% vs 13.7%, p<0.001; within-section folio variance substantial, HERBAL CV=0.54; extension parameterized at section, folio, and paragraph level) | 2 | B, extension, distribution | -> [C1199_extension_distributional_gradient.md](C1199_extension_distributional_gradient.md) |
| **1200** | **Order Encodes Procedural State** (atom ordering within MIDDLEs carries state: after k-terminal, 70.6% start with e vs 58.2% after e-terminal, p<0.001; ke chosen after cool predecessors, ek after hot; K-DOM alternates 1.94x, E-DOM persists 0.60x; carryover within-line +0.247 but resets at line boundaries +0.021) | 2 | B, order, state | -> [C1200_order_encodes_procedural_state.md](C1200_order_encodes_procedural_state.md) |
| **1201** | **PREFIX-Mediated Energy State Routing** (ch/sh prefixes route k/e energy state transitions; predecessor ch:sh=1.76:1 at k->e switches vs 0.98:1 at continuations, Fisher p=0.008; target PREFIX chi2=104.2; sh 2.06x and lsh 3.17x enriched at switches; qo 0.69x and ol 0.57x enriched at continuations) | 2 | B, prefix, energy, routing | -> [C1201_prefix_energy_state_routing.md](C1201_prefix_energy_state_routing.md) |
| **1202** | **H-Kernel MIDDLE No Transition Mediation** (h-kernel in MIDDLE does NOT mediate k/e transitions; mediator h-rate 5.5% at k->e vs 7.2% at k->k, delta=-0.016, perm p=0.852; function resides in PREFIX layer not MIDDLE; STARS_RECIPE only section with positive delta, confirming C1154) | 2 | B, h-kernel, negative | -> [C1202_h_kernel_middle_no_transition_mediation.md](C1202_h_kernel_middle_no_transition_mediation.md) |
| **1203** | **ch/sh MIDDLE Atom-Level Differentiation** (ch-prefix MIDDLEs have higher k-atom fraction (7.1% vs 5.9%) and prefer e-free MIDDLEs: dy 3.1x, k 3.1x, d 2.8x ch-biased; sh-prefix MIDDLEs are more e-enriched (35.1% vs 30.2%); both share core vocabulary but frequency distributions diverge along k/e axis) | 2 | B, prefix, atoms, ch, sh | -> [C1203_ch_sh_middle_atom_differentiation.md](C1203_ch_sh_middle_atom_differentiation.md) |
| **1204** | **i-Extension Inverted Gradient** (i-gradient inverted vs e: ii 53.7% > single-i 45.9%, unlike e where single-e 81.1% dominates; driven by aIn family where ii-form is 2x more common; HERBAL highest ii+ rate 67.6%, BIO lowest 46.7%) | 2 | B, i-atom, extension | -> [C1204_i_extension_inverted_gradient.md](C1204_i_extension_inverted_gradient.md) |
| **1205** | **i-Atom Orthogonal to k/e Energy System** (i operates on independent axis: no carryover z=-6.14 (anti-clusters), disjoint atom space chi2=2272, folio r(i,k)=-0.437 r(i,e)=-0.412, program-specific within/between=1.83, partial carryover interruption; all signals survive daiin removal) | 2 | B, i-atom, orthogonality, k/e | -> [C1205_i_ke_orthogonality.md](C1205_i_ke_orthogonality.md) |
| **1206** | **Paragraph Kernel Gradient** (h declines r=-0.920 through folio line quintiles while k rises r=+0.727 and e rises r=+0.881; early lines monitoring-heavy, later lines operation-heavy; extends C965 kernel composition shift) | 2 | B, paragraph, gradient, kernel | -> [C1206_paragraph_kernel_gradient.md](C1206_paragraph_kernel_gradient.md) |
| **1207** | **Atom Correlation Clusters** (~20 atoms organize into 5-6 correlated clusters at folio level; {a,i,n,r} iteration axis r=+0.81-0.83, {c,h} monitoring r=+0.75, {k,l} energy r=+0.54, {d,y} closure r=+0.48, {o,p} structural r=+0.41; 64/153 pairs FDR-significant; all survive daiin removal) | 2 | B, atoms, dimensionality, clusters | -> [C1207_atom_correlation_clusters.md](C1207_atom_correlation_clusters.md) |
| **1208** | **Atom Carryover Classification** (18 atoms classify into 3 carryover classes: POSITIVE state persistence {a,c,h,k,m,p,r,s,t} z=+2.5 to +9.6; NEGATIVE anti-clustering {e,i,n,y} z=-4.3 to -6.1; NEUTRAL {d,f,l,o,q}; e anti-clusters despite C1200 directional carryover; all survive daiin removal) | 2 | B, atoms, carryover, classification | -> [C1208_atom_carryover_classification.md](C1208_atom_carryover_classification.md) |
| **1209** | **MIDDLE Positional Grammar** (atoms occupy ordered slots within MIDDLEs: INITIAL {a,q,e,o} 86-57% initial; MEDIAL {c,i,p,d,f,s}; TERMINAL {n,y,m,r,h,l} 71-99% terminal; FREE {k,t} no preference; n 99.4% terminal, a 86.3% initial; all 18 atoms FDR-significant; k/t position-freedom consistent with kernel operator role) | 2 | B, atoms, position, grammar | -> [C1209_middle_positional_grammar.md](C1209_middle_positional_grammar.md) |
| **1210** | **MIDDLE Slot Syntax** (INITIAL and TERMINAL slots NOT independent: chi2=27,465, V=0.307, MI=1.071 bits; persists at length 4+ V=0.285; near-categorical forbidden combinations: a->y 0/796, e->n 1/813, k->n 0/135; n-terminal forbidden with all non-iteration INITIAL atoms; strong affinities follow C1207 clusters: k->e 7.94x, i->n 6.78x, d->y 3.18x) | 2 | B, atoms, syntax, slots | -> [C1210_middle_slot_syntax.md](C1210_middle_slot_syntax.md) |
| **1211** | **Sub-MIDDLE Pairwise Sufficiency** (INITIAL+MEDIAL+TERMINAL show REDUNDANCY not synergy: synergy=-0.827 bits; extends C1003 to sub-MIDDLE level; INITIAL explains 35.9% of TERMINAL entropy, MEDIAL 49.1%, both together 57.5%; pairwise interactions sufficient at both morphological levels) | 2 | B, atoms, synergy, pairwise | -> [C1211_sub_middle_pairwise_sufficiency.md](C1211_sub_middle_pairwise_sufficiency.md) |

### Cross-Token Chaining (C1212-C1213) -- Phase: CROSS_TOKEN_CHAINING (Phase 430)

| # | Description | Tier | Tags | Location |
|---|-------------|------|------|----------|
| **1212** | **Cross-Token Sequential Chaining** (TERMINAL(N)->INITIAL(N+1) is the strongest genuine sequential signal z=20.3; full 3x3 slot matrix shows MEDIAL->MEDIAL has highest raw MI=0.092 but lowest z=3.4 -- 80% co-occurrence not sequence; cross-token signal 6% of within-MIDDLE MI; enriched: h->p 2.61x, r->a 1.99x; depleted: r->t 0.25x; cross-line NOT weaker MI ratio=1.262; within-lane stratification confirms not purely PREFIX confound) | 2 | B, atoms, chaining, sequential | -> [C1212_cross_token_sequential_chaining.md](C1212_cross_token_sequential_chaining.md) |
| **1213** | **Axis-Switching Dominance** (programs switch C1207 axes between tokens 84.8% of the time; same-axis continuation 15.2% vs expected 13.2%, enrichment only 1.15x; ITERATION->ITERATION highest same-axis at 33.2%; STABILITY dominant target from all axes; programs interleave across operational channels) | 2 | B, atoms, axes, switching, programs | -> [C1213_axis_switching_dominance.md](C1213_axis_switching_dominance.md) |

### Line Compositional Modes (C1214) -- Phase: LINE_COMPOSITIONAL_MODES (Phase 431)

| # | Description | Tier | Tags | Location |
|---|-------------|------|------|----------|
| **1214** | **Line Compositional Homogeneity** (lines mildly more homogeneous than within-folio shuffled: z=-7.0, 3.8% entropy reduction; all slots equal INITIAL z=-8.1, MEDIAL z=-7.0, TERMINAL z=-8.2; PC1 36.2% CLOSURE vs ITERATION; section explains only 12.6% of PC1; no position gradient; explains C1212 MEDIAL co-occurrence as whole-token tuning; survives daiin exclusion z=-6.78) | 2 | B, lines, homogeneity, composition | -> [C1214_line_compositional_homogeneity.md](C1214_line_compositional_homogeneity.md) |

### Compound Slot Grammar (C1215-C1216) -- Phase: COMPOUND_SLOT_GRAMMAR (Phase 432)

| # | Description | Tier | Tags | Location |
|---|-------------|------|------|----------|
| **1215** | **Compound MIDDLE Slot Compliance** (compound MIDDLEs obey C1210 forbidden combinations: a->y 1/1422, e->n 1/3972, k->n 0/475; compound slot syntax weaker V=0.329 vs atomic V=0.416 reflecting greater INITIAL->TERMINAL diversity; forbidden rules are scale-invariant) | 2 | B, compounds, slots, compliance | -> [C1215_compound_slot_compliance.md](C1215_compound_slot_compliance.md) |
| **1216** | **Compound Junction Grammar** (junctions between embedded atoms within compounds show V=0.415, MI=1.636 bits -- 6x stronger than cross-token V=0.071; junction grammar recreates PREFIX bigrams c->h 11.7x, o->l 9.1x, s->h 8.1x as internal routing; DIFFERENT from cross-token grammar r=0.089; C1210 forbidden pairs strictly zero at junctions; 91% of compounds are 2-tile) | 2 | B, compounds, junctions, grammar, routing | -> [C1216_compound_junction_grammar.md](C1216_compound_junction_grammar.md) |

### Lane Atom Content Separation (C1217) -- Phase: ATOM_PROFILE_SYNTHESIS (Phase 433)

| # | Description | Tier | Tags | Location |
|---|-------------|------|------|----------|
| **1217** | **Lane vs Non-Lane Atom Content Separation** (QO/CHSH lane tokens carry ENERGY/STABILITY/MONITORING atoms; non-lane tokens carry ITERATION atoms 37.9% vs 4.3%; k 6.7x lane-enriched, t 7.7x lane-enriched, n 0.04x lane-depleted; two interleaved information streams: energy control loop vs parametric metadata; p<0.002 within-folio shuffle) | 2 | B, lanes, atoms, PREFIX, energy, iteration | -> [C1217_lane_atom_content_separation.md](C1217_lane_atom_content_separation.md) |

### PREFIX Atom Roles (C1218-C1221) -- Phase: PREFIX_ATOM_ROLES (Phase 434)

| # | Description | Tier | Tags | Location |
|---|-------------|------|------|----------|
| **1218** | **PREFIX Internal Positional Grammar** (PREFIX characters have strong positional preferences: dedicated modifiers q,d,f,p,y,s at POS-0, dedicated bases h,e at POS-1+, dual-role o,k,l,t,c,a,r; forms base-modifier grammar parallel to MIDDLE INITIAL/TERMINAL syntax; reinterprets C1193 low additivity as role-switching not non-compositionality) | 2 | B, PREFIX, atoms, grammar, positional | -> [C1218_prefix_positional_grammar.md](C1218_prefix_positional_grammar.md) |
| **1219** | **Base Character Determines MIDDLE Content** (final character of PREFIX predicts MIDDLE atom profile: within-base cosine 0.950 vs between-base 0.515, ratio 1.84; a-base=80% ITERATION, o-base=42% ENERGY, h-base=32% STABILITY+31% CLOSURE, e-base=53% CLOSURE; base defines operational domain, modifier selects variant) | 2 | B, PREFIX, atoms, base, MIDDLE | -> [C1219_base_character_determines_middle_content.md](C1219_base_character_determines_middle_content.md) |
| **1220** | **PREFIX Modifier Consistency Varies by Character** (cross-base modifier consistency ranges from high o=0.836, l=0.794, a=0.756 to low d=0.345, s=0.368, c=0.380; compositionality is partial and modifier-specific; consistent modifiers are genuine compositional elements, base-dependent modifiers function more as allomorphs) | 2 | B, PREFIX, atoms, modifier, compositionality | -> [C1220_modifier_consistency_varies.md](C1220_modifier_consistency_varies.md) |
| **1221** | **Prep PREFIX Similarity is Base-Driven** (prep PREFIXes pch,tch,dch,te,lch have mean cosine 0.963 but shuffle test p=0.998 shows not special; similarity from shared h-base; challenges F-BRU-012 distinct operation glosses; prep PREFIXes are h-base mode variants not independent action verbs) | 2 | B, PREFIX, prep, Brunschwig, base | -> [C1221_prep_prefix_similarity_base_driven.md](C1221_prep_prefix_similarity_base_driven.md) |

---

### Modern Distillation Dimensional Comparison (C1222) -- Phase: MODERN_DISTILLATION_DIMENSIONAL_COMPARISON (Phase 435)

| # | Description | Tier | Tags | Location |
|---|-------------|------|------|----------|
| **1222** | **Modern Distillation Dimensionality Closer to Voynich** (modern distillation 4 PCs for 80% vs Brunschwig 3, Voynich 5; entropy 2.334 bits 2.3× closer to Voynich; MIDPROCESS 34.5% of modern actions forming PC2 at 20.2% variance vs Brunschwig 0%; 7 active dimensions vs 5; process control vs recipe specification) | 2 | B, Brunschwig, modern, PCA, MIDPROCESS, dimensional | -> [C1222_modern_distillation_closer_to_voynich.md](C1222_modern_distillation_closer_to_voynich.md) |
| **1223** | **MIDPROCESS Sub-Type Split Matches Voynich Dimensionality** (splitting MIDPROCESS into 5 Voynich-aligned sub-types MONITORING/ENERGY/STABILITY/CLOSURE/STRUCTURAL increases modern distillation from 4 to 5 PCs for 80%, exactly matching Voynich; entropy 2.921 bits; 11 active dimensions vs Voynich 10; remaining gap from C1222 fully explained by material-specific process control parameterization) | 2 | B, modern, PCA, MIDPROCESS, dimensional, axes | -> [C1223_midprocess_subtype_dimensionality_match.md](C1223_midprocess_subtype_dimensionality_match.md) |

---

### Plant Distillation Profile Matching (C1224) -- Phase: PLANT_DISTILLATION_PROFILE_MATCHING (Phase 436)

| # | Description | Tier | Tags | Location |
|---|-------------|------|------|----------|
| **1224** | **Axis Distribution Transformation** (CORRECTED to paragraph-level: 479 paragraphs and 35 plants have same dimensionality 4 PCs, entropy 2.451 vs 2.369 bits, PC alignment NS p=0.30; Voynich inflates ITERATION 7.0x, CLOSURE 1.3x while deflating FREE 6.3x, MONITORING 2.3x; ITERATION inflation stable across units 25.1% par vs 25.2% folio confirming real transformation; encodes control program structure not direct distillation profiles; REGIME_1 captures 82% of ROOT-matching paragraphs; category adds 13.9% beyond section, up from 8.1% at folio level) | 2 | B, plants, PCA, axes, transformation, control program, paragraphs | -> [C1224_axis_distribution_transformation.md](C1224_axis_distribution_transformation.md) |

### KE Thermal Cycling Validation (C1225-C1226) -- Phase: KE_THERMAL_CYCLING_VALIDATION (Phase 437)

| # | Description | Tier | Tags | Location |
|---|-------------|------|------|----------|
| **1225** | **E-depth Suffix Parametricity** (ke-family e-count restructures suffix grammar: single-e 64% -edy/14% -y vs multi-e 12% -edy/37% -y, chi-squared p<0.0001; -s suffix exclusive to multi-e; e-depth is parametric axis modulating output specification not noise; e-depth does NOT vary by REGIME p=0.62 or section p=0.067) | 2 | B, ke-family, e-depth, suffix, parametric, MIDDLE | -> [C1225_edepth_suffix_parametricity.md](C1225_edepth_suffix_parametricity.md) |
| **1226** | **ke/ek Ratio Process-Context Conditioning** (k-e ordering conditioned by REGIME chi²=77.71 p<0.0001 and section chi²=138.50 p<0.0001; REGIME_1 18.6% ek vs REGIME_4 64.0% ek; HERBAL 79.1% ek vs BIO 19.7% ek; ke follows E-DOM predecessors 54.9% vs ek 22.5% OR=4.20; process-sensitivity marker; ke-family routes to QO not CHSH permutation p=0.9996 informative null) | 2 | B, ke-family, ek, REGIME, section, process-sensitivity, MIDDLE | -> [C1226_ke_ek_ratio_process_conditioning.md](C1226_ke_ek_ratio_process_conditioning.md) |

### Apparatus Transition Detection (C1227-C1229) -- Phase: APPARATUS_TRANSITION_DETECTION (Phase 438)

| # | Description | Tier | Tags | Location |
|---|-------------|------|------|----------|
| **1227** | **FL Cross-Line Reset Clustering** (36.4% of cross-line FL pairs show regression, dominated by LATE->MEDIAL 190/257=73.9%; regressions cluster at non-uniform paragraph positions KS p<0.0001; partial reset marks cycle boundaries within continuous process; section-stable 34.8-38.0%; LATE->EARLY forbidden within lines C787 but occurs 33 times between lines) | 2 | B, FL, paragraph, cross-line, reset, cycling | -> [C1227_fl_cross_line_reset_clustering.md](C1227_fl_cross_line_reset_clustering.md) |
| **1228** | **PREFIX Channel Switching Within Paragraphs** (73.2% of paragraphs have interior body line pairs with PREFIX JSD matching or exceeding header-body opening JSD; interior JSD mean 0.470 vs opening 0.504; operational mode routinely resets mid-paragraph; section-consistent 69.6-93.3%; combined with smooth kernel gradient 2.4% breakpoints indicates cycling not apparatus switching) | 2 | B, PREFIX, paragraph, channel, switching, cycling | -> [C1228_prefix_channel_switching.md](C1228_prefix_channel_switching.md) |
| **1229** | **Alternating Suffix Modes Within Paragraphs** (100% of paragraphs with 8+ body lines show two distinct suffix clusters k=2 silhouette 0.459; 80% interleaved not sequential; suffix gradient continuous with no discrete breakpoints 2.5-3.3% piecewise rate; FL resets do not coincide with suffix changes p=0.87; paragraph length does not predict suffix diversity rho=0.058; two modes alternate between specification-heavy and continuation-heavy throughout body) | 2 | B, suffix, paragraph, clustering, alternating, gradient | -> [C1229_alternating_suffix_modes.md](C1229_alternating_suffix_modes.md) |

### Extraction Cycling Validation (C1230-C1232) -- Phase: EXTRACTION_CYCLING_VALIDATION (Phase 439)

| # | Description | Tier | Tags | Location |
|---|-------------|------|------|----------|
| **1230** | **Suffix Mode MIDDLE Differentiation** (Mode A terminal-heavy lines have 1.62x k-family MIDDLEs p<0.000001, 2.86x prep MIDDLEs p=0.000034, 1.48x qo-PREFIX p<0.000001; Mode B bare-heavy lines have elevated e-family MIDDLEs p=0.000256; Mode A = energy + mechanical specification/agitation; Mode B = equilibration/continuation; partially lane-expressed r=0.256) | 2 | B, MIDDLE, PREFIX, suffix-mode, cycling, energy, extraction | -> [C1230_mode_middle_differentiation.md](C1230_mode_middle_differentiation.md) |
| **1231** | **Universal Suffix Mode Centroids** (55 paragraphs converge on two global centroids: Mode A terminal=0.430/bare=0.466, Mode B terminal=0.155/bare=0.741; global silhouette 0.293 paragraph-labels, 0.428 refit; F=4.56 between/within variance ratio; modes are universal grammar property not paragraph-specific noise) | 2 | B, suffix-mode, universal, paragraph, clustering | -> [C1231_universal_suffix_modes.md](C1231_universal_suffix_modes.md) |
| **1232** | **Paragraph Tail Product Signatures** (last 2 body lines cluster into k=3 distinct PREFIX+MIDDLE profiles silhouette 0.212; section-correlated chi2=31.73 p=0.0001; different paragraphs end with different operational signatures suggesting output product differentiation) | 2 | B, paragraph, tail, product, clustering, section | -> [C1232_paragraph_tail_product_signatures.md](C1232_paragraph_tail_product_signatures.md) |

### Control Loop Architecture (C1233-C1238) -- Phase: CONTROL_LOOP_ARCHITECTURE (Phase 441)

| # | Description | Tier | Tags | Location |
|---|-------------|------|------|----------|
| **1233** | **Cross-Line Independence** (cross-line FL regression, mode alternation, and channel switching are near-random entropy 97.8%, mutual info <1%; each line independently composed) | 2 | B, cross-line, independence, entropy | -> [C1233_cross_line_independence.md](C1233_cross_line_independence.md) |
| **1234** | **Iteration Two-Track System** (iin at line-initial 29.6% for cycle setup, aiin at penultimate 1.35x for bounded loop control; ii=formal bounded 92.6% n, i=open 52.9% n) | 2 | B, iteration, iin, aiin, loop, line-initial | -> [C1234_iteration_two_track_system.md](C1234_iteration_two_track_system.md) |
| **1235** | **Line-Final Routing Architecture** (line-final = routing not processing; m 29.77x enriched, k/e depleted 0.52-0.63x; 34.9% batch-close / 14.6% loop-check / 50.5% neutral) | 2 | B, line-final, routing, m, batch-close | -> [C1235_line_final_routing_architecture.md](C1235_line_final_routing_architecture.md) |
| **1236** | **Suffix Scope Markers** (terminal suffixes -edy Mode A specification 2.5-3.0x; checkpoint suffixes -aiin mode-independent; Mode A=36.1% terminal, Mode B=62.0% bare) | 2 | B, suffix, scope, terminal, checkpoint, mode | -> [C1236_suffix_scope_markers.md](C1236_suffix_scope_markers.md) |
| **1237** | **Paragraph Termination by -am** (-am 5.19x at paragraph-final; terminal suffixes are batch-close not termination; last lines shorter 7.3 vs 10.0, cooling-enriched; steady-state until -am) | 2 | B, paragraph, termination, -am, cooling | -> [C1237_paragraph_termination_by_am.md](C1237_paragraph_termination_by_am.md) |
| **1238** | **Kernel Initiation Order** (first-occurrence ordering e->k->h cool->process->monitor; e before k 64.6%, h before k only 28.3%; refines C873 mean-position ordering) | 2 | B, kernel, initiation, ordering, e, k, h | -> [C1238_kernel_initiation_order.md](C1238_kernel_initiation_order.md) |

### Paragraph Termination Mechanics (C1239-C1241) -- Phase: PARAGRAPH_TERMINATION_MECHANICS (Phase 442)

| # | Description | Tier | Tags | Location |
|---|-------------|------|------|----------|
| **1239** | **Paragraph Body Length Parameterization** (section-parameterized F=17.35 eta2=0.107, REGIME-parameterized F=12.55 eta2=0.061; within-section roughly memoryless HERBAL var/mean=0.92; BIO 6.15 lines, HERBAL 2.80; ~85% variance folio-specific; non-geometric is mixture artifact) | 2 | B, paragraph, length, section, REGIME, memoryless | -> [C1239_paragraph_length_parameterization.md](C1239_paragraph_length_parameterization.md) |
| **1240** | **Paragraph-Final -am Trigger Context** (qo prefix 0% at para-final vs 19.7% non-final; ch 2.81x, al 3.80x, e-MIDDLE 2.53x enriched; preceded by aiin/aiiin loop-check; cooling-verified shutdown not processing; n=31) | 2 | B, paragraph, termination, -am, trigger, cooling, shutdown | -> [C1240_am_trigger_context.md](C1240_am_trigger_context.md) |
| **1241** | **Header-Body Length Independence** (header complexity does not predict body length r=-0.039 tokens, -0.072 unique MIDDLEs; length externally determined; short and long paragraphs structurally identical) | 2 | B, paragraph, header, body, length, independence | -> [C1241_header_body_independence.md](C1241_header_body_independence.md) |

### EN Lane Cross-Prediction (C1242-C1245) -- Phase: EN_LANE_CROSS_PREDICTION (Phase 443)

| # | Description | Tier | Tags | Location |
|---|-------------|------|------|----------|
| **1242** | **Cross-Lane Content Prediction** (adjacent QO/CHSH pairs MI=1.0632 bits z_perm=13.42 GENUINE; within-lane ordering null z_wl=0.05; kernel routing z=49.12 CHSH→QO 2.2x stronger; cross-line null z=0.37; line-scoped co-occurrence not sequential) | 2 | B, cross-lane, MI, prediction, kernel, routing, line-scoped | -> [C1242_cross_lane_content_prediction.md](C1242_cross_lane_content_prediction.md) |
| **1243** | **sh/ch Cross-Lane Routing Split** (sh→QO(k) 32.0% vs ch→QO(k) 24.0% 1.34x; sh entropy 4.763 ch entropy 5.068; sh=monitor-pivot formulaic ch=checkpoint-gate varied; extends C929 with routing evidence) | 2 | B, sh, ch, routing, pivot, gate, C929-extension | -> [C1243_sh_ch_routing_split.md](C1243_sh_ch_routing_split.md) |
| **1244** | **aiin-ain Sequential Wind-Down** (aiin before ain 64.9% on co-occurring lines 98/151; adjacent aiin→ain 19 vs ain→aiin 11; loop-back 15.5% 2.05x baseline; 84.5% advance to different MIDDLE; sustained cycling to final pass) | 2 | B, suffix, aiin, ain, wind-down, iteration, ordering | -> [C1244_aiin_ain_wind_down.md](C1244_aiin_ain_wind_down.md) |
| **1245** | **Extensible Atom Scaling** (e-extension=intensity k>ke>kee; i-extension=duration i<ii; bare k 92.6% REGIME_2 ke 18.6% REGIME_1; aiin=sustained-cycling ain=final-pass per C1195 atoms not "check"; two independent control dimensions) | 3 | B, extensible, e, i, intensity, duration, regime, scaling | -> [C1245_extensible_atom_scaling.md](C1245_extensible_atom_scaling.md) |

**Phase 443 findings (EN Lane Cross-Prediction):**
- Cross-lane MIDDLE prediction genuine (z=13.42) but sequential ordering null (z=0.05)
- Kernel routing massive (z=49.12), CHSH→QO asymmetric (2.2x)
- sh = monitor-pivot (routes to heat 32%), ch = checkpoint-gate (routes to heat 24%, more varied)
- aiin→ain directional wind-down (64.9%): sustained cycling → final pass
- e = intensity dial (k/ke/kee), i = duration dial (i/ii): two independent scaling axes
- Cycle strictly line-scoped (cross-line null)

---

## Navigation

↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
