# Constraint Index

**Total:** 1410 validated constraints | **Version:** 5.39 | **Date:** 2026-03-06

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
| **1195** | **Atom Gloss Confidence Tiers** (18 atoms in 4 tiers: 8 LOCKED (k,e,h,y,i,n,a,m), 6 SOLID (d,t,l,o,c,p), 5 PLAUSIBLE (f,s,g,x,r), 0 WEAK; validated against 91 glossed compounds; upgraded by Phases 496-500) | 2 | B, atoms, glossing | -> [C1195_atom_gloss_confidence_tiers.md](C1195_atom_gloss_confidence_tiers.md) |
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

### EN Lane Cross-Prediction (C1242-C1244) -- Phase: EN_LANE_CROSS_PREDICTION (Phase 443)

| # | Description | Tier | Tags | Location |
|---|-------------|------|------|----------|
| **1242** | **Cross-Lane Content Prediction** (adjacent QO/CHSH pairs MI=1.0632 bits z_perm=13.42 GENUINE; within-lane ordering null z_wl=0.05; kernel routing z=49.12 CHSH→QO 2.2x stronger; cross-line null z=0.37; line-scoped co-occurrence not sequential) | 2 | B, cross-lane, MI, prediction, kernel, routing, line-scoped | -> [C1242_cross_lane_content_prediction.md](C1242_cross_lane_content_prediction.md) |
| **1243** | **sh/ch Cross-Lane Routing Split** (sh→QO(k) 32.0% vs ch→QO(k) 24.0% 1.34x; sh entropy 4.763 ch entropy 5.068; sh=monitor-pivot formulaic ch=checkpoint-gate varied; extends C929 with routing evidence) | 2 | B, sh, ch, routing, pivot, gate, C929-extension | -> [C1243_sh_ch_routing_split.md](C1243_sh_ch_routing_split.md) |
| **1244** | **aiin-ain Sequential Wind-Down** (aiin before ain 64.9% on co-occurring lines 98/151; adjacent aiin→ain 19 vs ain→aiin 11; loop-back 15.5% 2.05x baseline; 84.5% advance to different MIDDLE; sustained cycling to final pass) | 2 | B, suffix, aiin, ain, wind-down, iteration, ordering | -> [C1244_aiin_ain_wind_down.md](C1244_aiin_ain_wind_down.md) |

**Phase 443 findings (EN Lane Cross-Prediction):**
- Cross-lane MIDDLE prediction genuine (z=13.42) but sequential ordering null (z=0.05)
- Kernel routing massive (z=49.12), CHSH→QO asymmetric (2.2x)
- sh = monitor-pivot (routes to heat 32%), ch = checkpoint-gate (routes to heat 24%, more varied)
- aiin→ain directional wind-down (64.9%): sustained cycling → final pass
- Extensible atom scaling (e=intensity, i=duration) documented as fit F-B-007
- Cycle strictly line-scoped (cross-line null)

### EN Cross-Lane Pairing (C1245-C1246) -- Phase: EN_CROSS_LANE_PAIRING (Phase 444)

| # | Description | Tier | Tags | Location |
|---|-------------|------|------|----------|
| **1245** | **Cross-Lane Selectivity Gradient** (QO MIDDLEs span 1.773-bit entropy range in CHSH partner selection; rare=selective common=promiscuous rho=0.665; 4 enriched pairs survive Bonferroni; e-depth matched at category OR=2.625 complementary within e-subset rho=-0.262; pair frequencies domain-specific refines C821) | 2 | B, cross-lane, selectivity, entropy, e-depth, pairing | -> [C1245_cross_lane_selectivity_gradient.md](C1245_cross_lane_selectivity_gradient.md) |
| **1246** | **Mode-Differentiated Cross-Lane Pairing** (Mode A/B lines use different QO-CHSH pairings JSD z=4.60; Mode A MI=1.425 Mode B MI=0.978; A enriches energy+specific-measurement B enriches sustained+passive-monitoring; extends C1229/C1230 to cross-lane level) | 2 | B, cross-lane, mode, pairing, specification, execution | -> [C1246_mode_differentiated_pairing.md](C1246_mode_differentiated_pairing.md) |

**Phase 444 findings (EN Cross-Lane Pairing):**
- Selectivity gradient: rare QO MIDDLEs lock to few CHSH partners, common ones are promiscuous
- E-depth matched at category level (OR=2.625) but complementary within e-subset (rho=-0.262)
- i-atom control null (C1205 confirmed)
- Pair frequencies are domain-specific (refines C821: topology invariant, frequencies not)
- Mode A (specification) has tighter heat-measure coupling than Mode B (execution)

### Apparatus Vocabulary Classification (C1247-C1249) -- Phase: APPARATUS_VOCABULARY_CLASSIFICATION (Phase 445)

| # | Description | Tier | Tags | Location |
|---|-------------|------|------|----------|
| **1247** | **aii REGIME_3 Specificity** (aii "unseal" is 41x enriched in R3 vs R1; 14/20 R3 folios contain aii vs 1/32 R1; line context shows close→unseal→open transition; R3 = open-cycle batch apparatus) | 2 | B, REGIME, aii, apparatus, batch | -> [C1247_aii_regime3_specificity.md](C1247_aii_regime3_specificity.md) |
| **1248** | **Apparatus-Marker Co-occurrence Architecture** (t+eol co-occur OR=16.27 p=0.0001; ke+eeol co-occur OR=inf p=0.0003; DISTILLATION vs PRECISION rho=-0.666; R1/R3=single-apparatus R2/R4=mixed-apparatus REGIMEs) | 2 | B, apparatus, co-occurrence, REGIME, profile | -> [C1248_apparatus_marker_cooccurrence.md](C1248_apparatus_marker_cooccurrence.md) |
| **1249** | **Section-Conditioned Apparatus Diversity** (Herbal is most apparatus-diverse section; R2-SEALED 100% Herbal; R4-SEALED/SUSTAINED 100% Herbal; Section B overwhelmingly distillation 0.293 vs H 0.134; weakest signatures all Herbal) | 2 | B, section, apparatus, diversity, Herbal | -> [C1249_section_apparatus_diversity.md](C1249_section_apparatus_diversity.md) |

**Phase 445 findings (Apparatus Vocabulary Classification):**
- REGIME encodes apparatus type: R1=continuous distillation, R3=batch distillation with unsealing, R2/R4=mixed
- aii (unseal) at 41x R3/R1 enrichment is the strongest single-MIDDLE REGIME discriminator
- Distillation cycle signature: t+eol co-occurrence OR=16.27; sustained heat cycle: ke+eeol always co-occur
- DISTILLATION vs PRECISION profiles anti-correlate strongly (rho=-0.666)
- Herbal section is apparatus-diverse; other sections are distillation-dominant
- Initial top-down PCA approach (5-test battery) returned APPARATUS_VOCABULARY_NOT_SUPPORTED; bottom-up profile scoring found the real signal

### Gloss Scale Validation (C1250-C1251) -- Phase: GLOSS_SCALE_VALIDATION (Phase 446)

| # | Description | Tier | Tags | Location |
|---|-------------|------|------|----------|
| **1250** | **Gloss Category Structural Coherence** (8 operational categories on 90 MIDDLEs: 5/7 permutation tests PASS p<0.01; behavioral silhouette z=3.5, kernel alignment V=0.675, line position F=29.9 30x, apparatus rho=0.758, within-line MI 9x; affordance-family and REGIME-direction fail; v2 redesigned null models) | 2 | B, gloss, category, validation, corpus-scale | -> [C1250_gloss_category_structural_coherence.md](C1250_gloss_category_structural_coherence.md) |
| **1251** | **Atom Gloss Compositional Validation** (atom->gloss validates through composition not position; composed atom glosses predict MIDDLE categories p=0.008; atoms differentiate REGIMEs 37x; 4/6 directional tests fail: line position rho=0.53, suffix mode rho=-0.06, kernel affinity 5/12, paragraph rho=0.17; confirms C1191 morphological grammar independent of semantic content) | 2 | B, atom, gloss, composition, C1191, positional-grammar | -> [C1251_atom_gloss_compositional_validation.md](C1251_atom_gloss_compositional_validation.md) |

**Phase 446 findings (Gloss Scale Validation):**
- MIDDLE-level: 8 operational categories structurally coherent at corpus scale (5/7 COHERENT)
- Atom-level: glosses validate through compositional chain (atom -> MIDDLE -> category -> structure), not direct positional prediction
- Morphological grammar (C1191) governs atom position/co-occurrence independently of semantic content
- V1 null model failure diagnosed: shuffling among same 90 MIDDLEs too conservative; v2 uses dual null models
- Three affinity groups emerge from kernel co-occurrence: E-affiliated (y,d,o,t,l), K-affiliated (i), H-affiliated (p,f,c,s,r)

### Paragraph Operational Classification (C1252-C1253) -- Phase: PARAGRAPH_OPERATIONAL_CLASSIFICATION (Phase 447)

| # | Description | Tier | Tags | Location |
|---|-------------|------|------|----------|
| **1252** | **Folio Operational Specialization** (within-folio paragraph JSD 0.263 < between-folio 0.294, p=0.000; folios specialize operationally — paragraphs within a folio share similar gloss profiles; 74 multi-paragraph folios; extends C1041 folio=program) | 2 | B, folio, paragraph, specialization, gloss, JSD | -> [C1252_folio_operational_specialization.md](C1252_folio_operational_specialization.md) |
| **1253** | **Paragraph-Level Apparatus Correlation** (THERMAL fraction at paragraph level correlates with apparatus score rho=0.409 p=0.000; weaker than token-level 0.758 due to aggregation; confirms C1250 T6 scales to paragraph unit; shuffled null 0.257) | 2 | B, paragraph, apparatus, THERMAL, correlation | -> [C1253_paragraph_apparatus_correlation.md](C1253_paragraph_apparatus_correlation.md) |

**Phase 447 findings (Paragraph Operational Classification):**
- 2/7 WEAK overall; gallows-gloss primary test (T1) fails — C869 remains Tier 3
- Gallows type does NOT predict body gloss profile (V=0.032, p=0.539); gallows mark boundaries, not operational content
- Paragraphs form continuous distribution (sil=0.192), not discrete operational types
- Folio operational specialization confirmed (T4): paragraphs within folios share similar profiles
- Apparatus correlation persists at paragraph level (T7): rho=0.409, attenuated from token-level 0.758
- Gloss adds nothing to REGIME prediction beyond section (T3: -1.9pp increment)
- Ordinal trends suggestive but sub-Bonferroni (MONITORING declines rho=-0.202, TRANSITION increases rho=0.165)
- -am termination test underpowered (n=23)

### Dark Pipeline Characterization (C1254) -- Phase: DARK_PIPELINE_CHARACTERIZATION (Phase 448)

| # | Description | Tier | Tags | Location |
|---|-------------|------|------|----------|
| **1254** | **Dark Pipeline Category Generalization** (8 categories partially generalize to 1,144 dark MIDDLEs via atom plurality vote; 3/6 PASS; coverage 88.6%→99.5%; line position 10.8x, within-line MI 1.5x; behavioral silhouette FAIL overall but LOCKED+SOLID tier p=0.001; section divergence FAIL; confidence stratification is key: trust LOCKED/SOLID, WEAK atoms add noise) | 2 | B, dark-pipeline, gloss, generalization, HT, atom, coverage | -> [C1254_dark_pipeline_category_generalization.md](C1254_dark_pipeline_category_generalization.md) |

**Phase 448 findings (Dark Pipeline Characterization):**
- 8-category system PARTIALLY_GENERALIZES to dark pipeline (3/6 tests pass)
- Auto-assignment via atom plurality vote covers 95.2% of dark MIDDLEs (zero ties)
- Total B token coverage: 88.6% → 99.5% (only 127 q-tokens remain uncovered)
- Line position differentiation (10.8x) and within-line MI (1.5x) confirm structural reality
- Behavioral silhouette fails overall but LOCKED+SOLID tier passes (p=0.001) — confidence stratification critical
- Section divergence fails: dark categories don't concentrate by section (selection-level, not category-level modulation)
- Atom-level operational encoding penetrates HT layer — more fundamental than 49-class grammar boundary
- Q-MIDDLEs (58 types, 127 tokens): insufficient data for 9th category test, no structural divergence from auto-assigned

### Category Section Vocabulary (C1255) -- Phase: CATEGORY_SECTION_VOCABULARY (Phase 449)

| # | Description | Tier | Tags | Location |
|---|-------------|------|------|----------|
| **1255** | **Category-Section Universal Vocabulary** (8 categories are section-universal in vocabulary but section-parameterized in frequency; 2/5 WEAK_SIGNAL; Jaccard 0.676≈null 0.669 shared vocab; 34.3% MIDDLEs section-enriched >2x p=0.001; LOO section classification 76.8% +37.8pp p=0.001; conditioned JS adds nothing 1.13x p=0.603; WEAK dark compounds J=0.894 section-specific vs LOCKED/SOLID J=0.343 universal; unifies C1134+C1148+C1176) | 2 | B, section, category, vocabulary, frequency, universal, dark-pipeline | -> [C1255_category_section_universal_vocabulary.md](C1255_category_section_universal_vocabulary.md) |

**Phase 449 findings (Category Section Vocabulary):**
- Operational categories are section-universal: same MIDDLEs used across all sections (Jaccard null)
- Section identity encoded through frequency modulation (34.3% enriched, 76.8% classification accuracy)
- Category conditioning orthogonal to section divergence (conditioned JS 1.13x, below null)
- Dark compounds (WEAK tier) are section-specific (J=0.894 nearly disjoint); core grammar is universal (J=0.343)
- MONITORING and MARKING most section-specific (55% and 48% enrichment rates)
- Unifies C1134 (frequency modulation), C1148 (dark hyper-modulation), C1176 (atom-selection) into single picture

### Sequential Content Prediction (C1256-C1258) -- Phase: SEQUENTIAL_CONTENT_PREDICTION (Phase 450)

| # | Description | Tier | Tags | Location |
|---|-------------|------|------|----------|
| **1256** | **Opener Mode Selection** (opener MIDDLE selects line suffix mode A/B; Cramer's V=0.30 1.76x p=0.000; does NOT predict kernel profile p=0.096 or FL distribution p=0.85; Mode-B-opening paragraphs have 28.9% Mode A lines vs 54.0% for Mode-A-opening; opener is mode selector not content router; refines C959) | 2 | B, opener, suffix-mode, paragraph-type, mode-selection | -> [C1256_opener_mode_selection.md](C1256_opener_mode_selection.md) |
| **1257** | **Consecutive Paragraph Vocabulary Coupling** (consecutive paragraphs share elevated MIDDLE vocabulary Jaccard 0.226 vs 0.199 p=0.000; but NO kernel autocorrelation p>0.4 and NO suffix mode autocorrelation p=0.714; vocabulary-only coupling; qualifies C845 self-containment; adjacent paragraphs share equipment vocabulary not operational state) | 2 | B, paragraph, vocabulary, sequential, self-containment | -> [C1257_consecutive_paragraph_vocabulary.md](C1257_consecutive_paragraph_vocabulary.md) |
| **1258** | **Parallel Mode Tracks** (Mode A and B form coupled parallel sequential tracks within paragraphs; 5/5 tests PASS; Mode B = continuous track with vocabulary p=0.000 kernel p=0.000 FL p=0.001 continuity; Mode A = specification injections with weak/no within-track continuity; cross-mode coupling bidirectional A->B rho=0.189 B->A rho=0.208 both p=0.000; within-mode > cross-mode coupling Jaccard 0.188 vs 0.164 p=0.000; counterpoint architecture; resolves C670 adjacent-line null) | 2 | B, suffix-mode, parallel-tracks, counterpoint, line-structure, vocabulary, kernel, FL | -> [C1258_parallel_mode_tracks.md](C1258_parallel_mode_tracks.md) |

**Phase 450 findings (Sequential Content Prediction):**
- Opener is a mode selector: predicts suffix mode (1.76x) but not kernel or FL content
- Paragraph opening mode declares paragraph type (specification-heavy vs continuation-heavy)
- Consecutive paragraphs share vocabulary (Jaccard +0.027) but not operational profile
- Termination is abrupt: penultimate lines differ (2.45x) but no monotonic trajectory (confirms C1237)
- **Major finding:** Mode A and B lines form coupled parallel tracks (counterpoint architecture)
- Mode B carries continuity (vocabulary, kernel, FL); Mode A injects specification
- Cross-mode coupling is bidirectional: A influences B and B influences A
- C670's adjacent-line null explained: it measured across voices, not within them

### Gradient Decomposition (C1259-C1260) -- Phase: GRADIENT_DECOMPOSITION (Phase 451)

| # | Description | Tier | Tags | Location |
|---|-------------|------|------|----------|
| **1259** | **Gradient Decomposition by Suffix Mode** (Mode A proportion FLAT across paragraph body rho=-0.027 p=0.449; C933 prep verb concentration is ARTIFACT of Mode A vocabulary 77%; C1227 FL resets GENUINE within B-track B->B 49.7% > cross-mode 40.5%; C676 suffix trajectory GENUINE in Mode B bare rho=0.072 p=0.008; C1228 PREFIX switching MIXTURE within<cross p=0.002; C932 C965 NOT REPLICATED in aggregate) | 2 | B, gradient, suffix-mode, decomposition, mode-proportion, artifact, genuine | -> [C1259_gradient_decomposition.md](C1259_gradient_decomposition.md) |
| **1260** | **Mode B Thermal State Tracking** (energy balance propagates through B-track: e_frac rho=0.376 ke_ratio rho=0.228 qo_frac rho=0.186 k_frac rho=0.139 all p=0.000; FL stage does NOT propagate rho=0.026 p=0.56; no ordinal progression in energy variables; ke_ratio lag-1 autocorrelation survives permutation p=0.002; B-track carries thermal context but independently assesses material state; line shortening rho=-0.243) | 2 | B, mode-b, thermal, state-tracking, energy-balance, propagation, FL, steady-state | -> [C1260_mode_b_thermal_state_tracking.md](C1260_mode_b_thermal_state_tracking.md) |

**Phase 451 findings (Gradient Decomposition):**
- Mode A proportion is flat across paragraph body -- mode-proportion shift is NOT a confound
- Prep verb early concentration (C933) is an artifact of prep verbs being Mode A tokens
- FL resets (C1227) are genuine B-track internal phenomena (B->B rate highest)
- Suffix trajectory (C676) is genuine within Mode B (bare fraction increases)
- PREFIX switching (C1228) is a mixture of mode alternation and within-track process
- C932 and C965 could not be replicated in aggregate (methodology concern)
- **Mode B thermal state tracking:** energy balance propagates (e_frac, ke_ratio, qo_frac, k_frac)
- FL stage does NOT propagate -- material state independently assessed each cycle
- No ordinal drift in energy variables -- steady-state thermal operation, not progressive ramp
- Lines shorten monotonically through the B-track (rho=-0.243)

### A Category Scattershot (C1261-C1268) -- Phase: A_CATEGORY_SCATTERSHOT (Phase 452)

| # | Description | Tier | Tags | Location |
|---|-------------|------|------|----------|
| **1261** | **A Record Category Coherence** (A records draw PP MIDDLEs from fewer operational categories than random; mean entropy 1.810 vs null 1.886; d=9.7 p<0.001; 1539 records 10382 tokens; extends C475 into category dimension) | 2 | A, category, record, coherence, entropy | -> [C1261_a_record_category_coherence.md](C1261_a_record_category_coherence.md) |
| **1262** | **RI Extension Character Category Coupling** (RI extension character associated with PP base category; chi2=165.2 V=0.221 perm p=0.001; 486 decompositions 16 ext chars 8 categories; h-ext MARKING 50% k-ext OPERATION 42% o-ext MONITORING 26%; extensions are operationally coupled not arbitrary) | 2 | A, RI, extension, category, coupling, C913 | -> [C1262_ri_extension_category_coupling.md](C1262_ri_extension_category_coupling.md) |
| **1263** | **A Paragraph Category Specialization** (A paragraphs specialize by operational category; entropy 2.533 vs null 2.623; d=12.5 p<0.001; 242 paragraphs; extends C1039 cluster selectivity into category space) | 2 | A, paragraph, category, specialization, entropy | -> [C1263_a_paragraph_category_specialization.md](C1263_a_paragraph_category_specialization.md) |
| **1264** | **Bridge vs Dark Pipeline Category Divergence** (bridge and dark pipeline MIDDLEs have different category profiles; chi2=73.0 V=0.441 perm p=0.001; bridges TRANSITION-enriched 20% vs 2%; dark MARKING-dominated 36% vs 11%; survives length control short p=0.0002 medium p=0.001) | 2 | A->B, bridge, dark-pipeline, category, divergence | -> [C1264_bridge_dark_category_divergence.md](C1264_bridge_dark_category_divergence.md) |
| **1265** | **A Record Atom-Profile Coherence Independent of Category** (within-record AXIS cosine 0.272 vs null 0.238 d=11.6 p<0.001; same-category pairs 0.529 vs null 0.238; atom coherence persists after category control; C1207 AXIS and C1250 categories are complementary organizational axes) | 2 | A, atom, coherence, AXIS, independent, record | -> [C1265_a_record_atom_coherence.md](C1265_a_record_atom_coherence.md) |
| **1266** | **A Section Atom-Level Differentiation** (5/7 AXIS clusters differentiate H/P/T sections at Bonferroni; STABILITY H=30.2 FREE H=20.9 ENERGY H=20.2 MONITORING H=16.7 CLOSURE H=12.9; H CLOSURE/MONITORING-heavy P STABILITY/ENERGY-heavy T ITERATION/ENERGY-heavy; breaks C946 cosine-0.997 barrier at atom resolution) | 2 | A, section, atom, differentiation, AXIS, C946 | -> [C1266_a_section_atom_differentiation.md](C1266_a_section_atom_differentiation.md) |
| **1267** | **Mode A/B Distinction is B-Execution Only** (B mode affinity does not cluster in A records; concentration 0.692 vs null 0.690 d=0.85 p=0.204; A is mode-agnostic; mode assignment happens at B execution time not A registry) | 2 | A, B, mode, null, orthogonality | -> [C1267_mode_distinction_b_only.md](C1267_mode_distinction_b_only.md) |
| **1268** | **PREFIX Track and Category Track Orthogonal** (ch/sh contexts have identical category distributions; chi2=6.52 V=0.021 JSD=0.0002 p=0.480; 8669 ch-context vs 5473 sh-context tokens; prefix choice does not select category; confirms C410 scope) | 2 | A, prefix, category, orthogonal, ch, sh, null | -> [C1268_prefix_category_orthogonality.md](C1268_prefix_category_orthogonality.md) |

**Phase 452 findings (A Category Scattershot):**
- A's registry is organized by operational category at record (C1261, d=9.7) and paragraph (C1263, d=12.5) scales
- RI extensions are operationally coupled to PP base categories (C1262, V=0.221) -- not arbitrary markers
- Bridge vs dark pipeline channels carry different category profiles (C1264, V=0.441) -- pipeline is category-structured
- Atom coherence within records is independent of category (C1265, residual +0.291) -- AXIS and category are complementary
- Atom decomposition breaks C946's MIDDLE-level uniformity barrier (C1266, 5/7 axes significant)
- Mode A/B distinction does NOT propagate backward into A (C1267, null) -- mode is B-execution only
- Prefix family (ch/sh) does NOT select category context (C1268, null) -- prefix and category are orthogonal

### AZC Category Scattershot (C1269-C1276) -- Phase: AZC_CATEGORY_SCATTERSHOT (Phase 453)

| # | Description | Tier | Tags | Location |
|---|-------------|------|------|----------|
| **1269** | **AZC Zone Category Specialization** (AZC zones R/C/S/P have distinct category distributions; chi2=52.18 V=0.084 p=0.000180; R TRANSITION/FLOW-heavy C TRANSITION/OPERATION P TRANSITION/STAGING S TRANSITION/FLOW; position encodes category bias not just legality) | 2 | AZC, zone, category, specialization, C313 | -> [C1269_azc_zone_category_specialization.md](C1269_azc_zone_category_specialization.md) |
| **1270** | **AZC Family Category Divergence** (Zodiac vs A/C families differ in category profile; chi2=40.23 V=0.122 p=0.000001; Zodiac TRANSITION/FLOW/THERMAL-enriched; A/C TRANSITION/STAGING/OPERATION-enriched; mechanism family-agnostic but content category-biased) | 2 | AZC, family, category, zodiac, divergence | -> [C1270_azc_family_category_divergence.md](C1270_azc_family_category_divergence.md) |
| **1271** | **AZC Zone Atom-Level Uniformity** (AZC zones do NOT differentiate at atom level; 1/8 AXIS clusters at p<0.05 0/8 at Bonferroni; contrasts A sections C1266 5/7 axes; category-level zone differences not driven by atom composition) | 2 | AZC, zone, atom, uniformity, null, AXIS | -> [C1271_azc_zone_atom_uniformity.md](C1271_azc_zone_atom_uniformity.md) |
| **1272** | **AZC Mediates Bridge-Dark Category Sorting** (bridge and dark MIDDLEs occupy different AZC zones; chi2=33.45 V=0.117 p<0.001; bridge R-dominated 47.5% dark S-shifted 26.9%; category predicts zone within bridge p=0.0003 but NOT within dark p=0.198; AZC sorts bridge vocabulary by category) | 2 | AZC, A->B, bridge, dark-pipeline, sorting, zone | -> [C1272_azc_mediates_bridge_dark_sorting.md](C1272_azc_mediates_bridge_dark_sorting.md) |
| **1273** | **AZC-Exclusive Vocabulary is MARKING/THERMAL Enriched** (356 UNK MIDDLEs assigned by atom vote; MARKING 27.2% THERMAL 27.0% TRANSITION 6.5%; divergent from bridge V=0.382 dark V=0.210 PP V=0.192; AZC has categorically specialized private vocabulary) | 2 | AZC, exclusive, vocabulary, MARKING, THERMAL | -> [C1273_azc_exclusive_vocabulary_profile.md](C1273_azc_exclusive_vocabulary_profile.md) |
| **1274** | **AZC Category Composition Predicts B Escape Rate** (THERMAL rho=+0.780 p<0.001 predicts high escape; TRANSITION rho=-0.598 p<0.001 predicts low escape; CONTAINMENT rho=-0.399 MARKING rho=-0.349; 82 B folios; category mix of AZC-shared vocabulary predicts B escape dynamics) | 2 | AZC, A->B, category, escape, THERMAL, TRANSITION, qo-prefix | -> [C1274_azc_category_predicts_b_escape.md](C1274_azc_category_predicts_b_escape.md) |
| **1275** | **No Within-Zone Spatial Category Coherence** (AZC diagram lines have no within-unit category clustering; entropy 1.464 vs null 1.461 d=-0.173 p=0.568; 264 groups 2626 tokens; category structure is zone-grain not line-grain; contrasts A record coherence C1261 d=9.7) | 2 | AZC, spatial, coherence, null, entropy | -> [C1275_no_within_zone_spatial_coherence.md](C1275_no_within_zone_spatial_coherence.md) |
| **1276** | **AZC Sections Converge on A Pharma Atom Profile** (all AZC sections closest to A Pharma; AZC-A/P r=0.920 AZC-C/P r=0.916 AZC-Z/P r=0.928; no diverse mapping; AZC draws from Pharma-like atom pool; internal JSD=0.013) | 2 | AZC, A, section, atom, Pharma, convergence | -> [C1276_azc_sections_converge_on_pharma.md](C1276_azc_sections_converge_on_pharma.md) |

**Phase 453 findings (AZC Category Scattershot):**
- AZC zones specialize by operational category (C1269, V=0.084) but NOT at atom level (C1271, 0/8 Bonferroni)
- Zodiac and A/C families have different category emphases (C1270, V=0.122) -- content diverges despite mechanism being family-agnostic
- AZC positional zones mediate bridge/dark category sorting (C1272, V=0.117) -- bridge sorted by category (p=0.0003), dark not (p=0.198)
- AZC-exclusive vocabulary is MARKING/THERMAL enriched, TRANSITION-depleted (C1273, V=0.382 vs bridge)
- THERMAL vocabulary predicts high escape, TRANSITION predicts low escape in B (C1274, rho=+0.780/-0.598) -- category is cross-system organizing principle
- No spatial coherence within diagram lines (C1275, null) -- organization is at zone grain, not line grain
- All AZC sections converge on A Pharma atom profile (C1276, r>0.916) -- atom-uniform internally

### Category B Execution (C1277-C1284) -- Phase: CATEGORY_B_EXECUTION (Phase 454)

| # | Description | Tier | Tags | Location |
|---|-------------|------|------|----------|
| **1277** | **THERMAL Escape is PREFIX-Mediated** (THERMAL->escape rho=+0.780 fully mediated by qo-PREFIX; THERMAL 44.1% qo-prefixed vs 9.5% baseline; partial rho=-0.081 after control; chain: THERMAL->qo->QO lane->escape; category x PREFIX chi2=5845 V=0.291) | 2 | B, A->B, THERMAL, escape, PREFIX, qo, mediation | -> [C1277_thermal_escape_prefix_mediation.md](C1277_thermal_escape_prefix_mediation.md) |
| **1278** | **Category Predicts Instruction Class Beyond PREFIX** (category reduces class entropy 1.207 bits 24.7%; adds 0.906 bits 18.6% BEYOND PREFIX; PREFIX 53.1% category 24.7% together 71.7%; complementary axes; perm p=0.001 d=1051; 16054 tokens) | 2 | B, category, instruction-class, entropy, PREFIX | -> [C1278_category_class_prediction.md](C1278_category_class_prediction.md) |
| **1279** | **Mode A/B Lines Differ by Category** (Mode A THERMAL-enriched 28.9% vs 19.9% MONITORING 2.2x; Mode B TRANSITION-enriched 17.4% vs 11.3% STAGING 1.3x; chi2=536.7 V=0.153 p<0.001; Mode A injects escape-capable vocabulary Mode B maintains transition baseline) | 2 | B, mode, category, THERMAL, TRANSITION | -> [C1279_mode_category_differentiation.md](C1279_mode_category_differentiation.md) |
| **1280** | **Hazard Concentrates in FLOW/CONTAINMENT** (hazard MIDDLEs 50.4% FLOW vs 8.8% safe; 11.5% CONTAINMENT vs 2.5%; THERMAL 2.6% vs 30.8% hazard-immune; chi2=7227.5 V=0.560; FLOW-hazard rho=+0.558 THERMAL-hazard rho=-0.602 at folio level) | 2 | B, hazard, FLOW, CONTAINMENT, THERMAL, category | -> [C1280_hazard_category_concentration.md](C1280_hazard_category_concentration.md) |
| **1281** | **TRANSITION Anti-Escape is PREFIX-Independent** (TRANSITION-escape rho=-0.582 survives ch/sh control partial=-0.586 p<0.001; TRANSITION ch/sh rate 25.7% = baseline 25.1%; hazard rate 24.2% moderate; mechanism unknown but real and strong) | 2 | B, TRANSITION, escape, PREFIX-independent, anti-escape | -> [C1281_transition_independent_anti_escape.md](C1281_transition_independent_anti_escape.md) |
| **1282** | **Category Predicts B Section Membership** (section x category chi2=759.8 V=0.106 p<0.001; 6/8 categories differentiate at Bonferroni; B=THERMAL-heavy C=FLOW-heavy H=FLOW/TRANSITION S=THERMAL/FLOW; compresses C1134 frequency modulation) | 2 | B, section, category, differentiation | -> [C1282_category_section_differentiation.md](C1282_category_section_differentiation.md) |
| **1283** | **Category Differentiates Entry vs Exit Zones** (entry THERMAL-enriched 24.4% vs exit 17.1%; exit TRANSITION-enriched 20.2% vs entry 13.9%; entry vs exit chi2=183.6 V=0.141 p<0.001; lines begin thermal specification end transition convergence) | 2 | B, boundary, entry, exit, THERMAL, TRANSITION | -> [C1283_category_boundary_divergence.md](C1283_category_boundary_divergence.md) |
| **1284** | **Kernel-Category Calibration** (CALIBRATION not discovery; THERMAL-k +0.646 THERMAL-e +0.668 TRANSITION-k -0.606 MONITORING-h +0.378; 9/24 sig; expected by C1250 construction; confirms consistency) | 2 | B, kernel, calibration, category, circularity | -> [C1284_kernel_category_calibration.md](C1284_kernel_category_calibration.md) |

**Phase 454 findings (Category B Execution):**
- THERMAL escape is fully PREFIX-mediated: THERMAL->qo (44.1%)->QO lane->escape (C1277, partial collapses to -0.081)
- Category adds 18.6% instruction class information BEYOND PREFIX (C1278) -- complementary axes
- Mode A lines inject THERMAL/escape-capable vocabulary; Mode B lines carry TRANSITION/escape-restrictive vocabulary (C1279, V=0.153)
- Hazard concentrates in FLOW (50.4%) and CONTAINMENT (11.5%); THERMAL is hazard-immune (2.6%) (C1280, V=0.560)
- TRANSITION anti-escape is PREFIX-independent and NOT hazard-mediated (C1281, partial=-0.586) -- mechanism unknown
- Category predicts section (6/8 Bonferroni) (C1282), and entry vs exit zones (V=0.141) (C1283)
- Kernel calibration confirms consistency (C1284, not scored)

### Category Mechanism Decomposition (C1285-C1290) -- Phase: CATEGORY_MECHANISM_DECOMPOSITION (Phase 455)

| # | Description | Tier | Tags | Location |
|---|-------------|------|------|----------|
| **1285** | **TRANSITION Anti-Escape via Role Redirection** (TRANSITION sources redirect successors to AUX 1.24x/FQ 1.13x enriched; EN successor rate 0.403 vs 0.476 baseline 0.85x; EN->EN self-loop 0.474 vs 0.517; rejects self-loop hypothesis; per-token mechanism; chi2=47.7 V=0.057 p<0.001) | 2 | B, TRANSITION, anti-escape, role-redirection, AUX, FQ | -> [C1285_transition_role_redirection.md](C1285_transition_role_redirection.md) |
| **1286** | **Category Transition Grammar is Structured** (8x8 category transition matrix chi2=526.1 V=0.060 p=3.75e-81; self-loops enriched MARKING +10.4 THERMAL +6.0 FLOW +4.6; FLOW->TRANSITION +6.7 OPERATION->THERMAL +6.5; THERMAL->TRANSITION -3.4 FLOW->THERMAL -7.3; directional operational sequencing) | 2 | B, category, transition-matrix, sequential, grammar | -> [C1286_category_transition_grammar.md](C1286_category_transition_grammar.md) |
| **1287** | **Paragraph Headers are MARKING-Enriched** (header vs body chi2=128.0 V=0.075 p<0.001; MARKING 2.44x enriched headers 18.3% vs body 7.5%; STAGING 1.45x; THERMAL 0.46x suppressed; three-level hierarchy: paragraph=marking, line-entry=thermal, body=flow/transition) | 2 | B, paragraph, header, MARKING, STAGING, specification | -> [C1287_paragraph_header_marking_enrichment.md](C1287_paragraph_header_marking_enrichment.md) |
| **1288** | **Within-Folio Paragraphs Share Category Profiles** (within-folio JSD=0.1086 vs null=0.1217 z=-4.92 p<0.001; across-folio JSD=0.1223; ratio=0.888; folio imposes category theme on paragraphs; N=484 paragraphs 74 folios) | 2 | B, paragraph, folio, coherence, category, JSD | -> [C1288_within_folio_paragraph_coherence.md](C1288_within_folio_paragraph_coherence.md) |
| **1289** | **Category Predicts AXM Self-Transition Rate** (THERMAL rho=+0.520 p<0.001 TRANSITION rho=-0.519 p<0.001; both Bonferroni; THERMAL=high AXM dwell TRANSITION=low AXM dwell; partially explains C1169 27% residual; N=82 folios) | 2 | B, AXM, category, THERMAL, TRANSITION, dwell, macro-state | -> [C1289_category_predicts_axm_dwell.md](C1289_category_predicts_axm_dwell.md) |
| **1290** | **Paragraph Category Predicts Mode** (Mode A=THERMAL 28.8% TRANSITION 11.5%; Mode B=THERMAL 21.0% TRANSITION 16.7%; chi2=300.4 V=0.114 p<0.001; confirms C1279 at paragraph level; N=175 A 309 B paragraphs) | 2 | B, paragraph, mode, category, THERMAL, TRANSITION | -> [C1290_paragraph_category_mode_prediction.md](C1290_paragraph_category_mode_prediction.md) |

**Phase 455 findings (Category Mechanism Decomposition):**
- TRANSITION anti-escape solved: role redirection to AUX/FQ, not EN self-loop (C1285)
- Category transition grammar is strongly structured (C1286, chi2=526, operational sequencing: heat->heat, flow->close, no heat->close)
- Paragraph headers are MARKING-enriched (2.44x), THERMAL-suppressed (0.46x) (C1287) -- contrasts line entries (THERMAL-enriched)
- Within-folio paragraphs share category profiles (C1288, z=-4.92) -- folio imposes thematic coherence
- THERMAL/TRANSITION predict AXM dwell (C1289, rho=+/-0.52) -- partially resolves 27% AXM residual
- Paragraph mode A=THERMAL-heavy, B=TRANSITION-heavy (C1290, V=0.114) -- confirms C1279 at paragraph level
- FAIL: TRANSITION does NOT cluster within lines (T2) -- anti-escape is per-token, not sequential
- FAIL: Forbidden transitions are cross-category (T3, 2/17 same-category) -- MARKING-dominated targets

### Category-REGIME Integration (C1291-C1294) -- Phase: CATEGORY_REGIME_INTEGRATION (Phase 456)

| # | Description | Tier | Tags | Location |
|---|-------------|------|------|----------|
| **1291** | **Category-REGIME Association is Kernel-Mediated** (chi2=526 V=0.106 p=5.5e-98; but after kernel residualization Fisher p=0.061; THERMAL kernel R2=0.779 TRANSITION=0.546 FLOW=0.409; association runs through k/h/e atoms shared by both systems; N=72 folios) | 2 | B, category, REGIME, kernel, circularity, mediation | -> [C1291_category_regime_kernel_mediation.md](C1291_category_regime_kernel_mediation.md) |
| **1292** | **Section-Independent Category-REGIME Association** (within-section stratified chi2=216.4 dof=49 p<1e-20; H chi2=67.4 S chi2=116.9 C chi2=32.1; section is not sole mediator; kernel is primary pathway) | 2 | B, category, REGIME, section, stratified | -> [C1292_section_independent_regime_category.md](C1292_section_independent_regime_category.md) |
| **1293** | **Categories Discriminate Beyond Role Profiles** (category JSD > role JSD in 5/6 REGIME pairs; role-residualized Fisher p=7.5e-8; 4/8 categories significant; mean JSD: role=0.0145 category=0.0228; categories not redundant with roles) | 2 | B, category, role, REGIME, resolution, discrimination | -> [C1293_category_discriminates_beyond_roles.md](C1293_category_discriminates_beyond_roles.md) |
| **1294** | **Category Fractions Do Not Extend C1169 AXM Model** (all 8 Spearman |rho|<0.14 with C1169 residuals; none Holm-significant; C1169 replication R2=0.853 LOO=0.726; 27% residual not reducible to categories; validates C1169 closure; N=65 folios) | 2 | B, AXM, category, C1169, residual, validation, negative | -> [C1294_categories_do_not_extend_c1169.md](C1294_categories_do_not_extend_c1169.md) |

**Phase 456 findings (Category-REGIME Integration):**
- Category-REGIME association exists (chi2=526, V=0.106) but is kernel-mediated (C1291) -- T3 circularity gate FAILED
- Association survives section control (C1292) but not kernel residualization -- kernel atoms are the primary pathway
- Categories add genuine resolution beyond role profiles (C1293, Fisher p=7.5e-8) -- not a relabeling of known structure
- Categories do NOT extend C1169 AXM model (C1294) -- 27% residual validated as irreducible design freedom
- REGIME_1=THERMAL-dominant (29.7%), REGIME_2=FLOW-dominant (28.1%), REGIME_4=OPERATION/TRANSITION-dominant
- Overall: CATEGORY_REGIME_PARTIAL (4 PASS, 2 FAIL, 1 SKIP)

---

### Paragraph Termination Trigger (C1295-C1296) -- Phase: PARAGRAPH_TERMINATION_TRIGGER (Phase 457)

| # | Description | Tier | Tags | Location |
|---|-------------|------|------|----------|
| **1295** | **Paragraph Termination is Memoryless** (7/7 trigger hypotheses FAIL at Bonferroni p<0.00625: thermal level Fisher p=0.236, B-track Fisher p=0.178, thermal step perm p=0.822, thermal budget within-folio rho=-0.007 p=0.930, mode gate chi2=1.19 p=0.276, category shift perm p=0.400, folio prediction F-test p=0.365; no line-level feature predicts termination; -am is marker not trigger; N=257 paragraphs 3+ body lines) | 2 | B, paragraph, termination, memoryless, thermal, negative | -> [C1295_paragraph_termination_memoryless.md](C1295_paragraph_termination_memoryless.md) |
| **1296** | **Tail Type Category Divergence** (3 tail product types C1232 have distinct 8-category profiles chi2=139.1 p<1e-22 perm p=0.001; Cluster 0 TRANSITION-enriched 20.1%, Cluster 2 THERMAL-dominant 33.5%; tail FORM covaries with category but tail TIMING does not C1295; N=257 paragraphs) | 2 | B, paragraph, termination, tail, category, divergence | -> [C1296_tail_type_category_divergence.md](C1296_tail_type_category_divergence.md) |

**Phase 457 findings (Paragraph Termination Trigger):**
- **TERMINATION_MEMORYLESS (1/8 PASS, 7/8 FAIL)** -- no line-level feature predicts when a paragraph terminates
- All thermal hypotheses fail: no level trigger, no B-track signature, no thermal step, no thermal budget
- No mode gate (suffix mode independent of termination) and no category shift (body homogeneous to the end)
- T1 e_frac signal is entirely a C963 length confound (vanishes after n_toks stratification)
- T4 definitive: within-folio mean e_frac vs body length rho=-0.007 -- no thermal budget governs duration
- Sole PASS (T8): tail product types have distinct category profiles -- the FORM of shutdown varies but the DECISION to stop does not
- Extends C963 body homogeneity from role fractions to thermal/category grain
- Overall: termination is folio-programmed (C1239), not state-triggered

---

### PREFIX Category Anatomy (C1297-C1302) -- Phase: PREFIX_CATEGORY_ANATOMY (Phase 458)

| # | Description | Tier | Tags | Location |
|---|-------------|------|------|----------|
| **1297** | **PREFIX-Category Structured Association** (32 x 8 contingency table chi2=15,598 dof=217 p~0 V=0.311; 32 qualifying PREFIXes N>=30; qo=59% THERMAL, ct=90% MONITORING, da=56% STAGING, ch/sh=OPERATION; structured selectivity not monolithic; N=23,086 tokens) | 2 | B, PREFIX, category, contingency | -> [C1297_prefix_category_structured_association.md](C1297_prefix_category_structured_association.md) |
| **1298** | **ok-ot Category Divergence** (sister pair ok/ot diverge in 8-category profiles chi2=32.0 dof=7 p=4.0e-5 V=0.105 JSD=0.008; ok THERMAL-enriched 24.7% vs 20.2% and MONITORING 2.52x; ot OPERATION-enriched 17.3% vs 12.5%; different operational emphasis despite shared FLOW dominance; N=2,924) | 2 | B, PREFIX, sister pair, ok, ot, category, divergence | -> [C1298_ok_ot_category_divergence.md](C1298_ok_ot_category_divergence.md) |
| **1299** | **ch-sh B-Specific Category Divergence** (ch/sh diverge in B chi2=85.7 p=9.4e-16 V=0.121 despite A-identical C1268 V=0.021; survives section control Fisher p=3.4e-10 and position control; ch selects broader MIDDLE vocabulary FLOW/CONTAINMENT/MARKING; sh concentrates OPERATION/THERMAL; mechanism is MIDDLE-level not artifact; N=5,821) | 2 | B, PREFIX, sister pair, ch, sh, category, divergence, system-dependent | -> [C1299_ch_sh_b_category_divergence.md](C1299_ch_sh_b_category_divergence.md) |
| **1300** | **qo Near-Pure THERMAL Channel** (qo is 59.0% THERMAL 2.50x corpus baseline 23.6% rank 1/32 binomial p~0; only PREFIX exceeding 50% in single category; secondary FLOW 20.1%; OPERATION 3.2% TRANSITION 1.5% strongly suppressed; primary thermal injection channel; N=4,069) | 2 | B, PREFIX, qo, THERMAL, channel, purity | -> [C1300_qo_near_pure_thermal_channel.md](C1300_qo_near_pure_thermal_channel.md) |
| **1301** | **PREFIX Category Information Beyond Base Group** (conditional MI I(CAT;PREFIX|BASE)=0.058 bits 2.1% of H(CAT)=2.742; Fisher-combined within-base p~0; t-base V=0.891 ct vs ot; o-base V=0.217 qo-driven; PREFIX is not tautological with base group; N=23,086 across 9 base groups) | 2 | B, PREFIX, base group, tautology, information theory, conditional MI | -> [C1301_prefix_category_beyond_base_group.md](C1301_prefix_category_beyond_base_group.md) |
| **1302** | **BARE Distinctive Category Profile** (BARE vs prefixed chi2=1,368 p~10^-291 V=0.243; BARE is FLOW-enriched 29.4% 1.68x STAGING-enriched 20.7% 1.83x THERMAL-depleted 4.1% 0.15x; inverse of qo C1300; bypasses base-MIDDLE-category chain; PREFIX slot is primary thermal injection mechanism; N=23,086) | 2 | B, PREFIX, BARE, category, THERMAL depletion, FLOW | -> [C1302_bare_distinctive_category_profile.md](C1302_bare_distinctive_category_profile.md) |

**Phase 458 findings (PREFIX Category Anatomy):**
- **PARTIAL_ANATOMY (5 PASS, 2 WEAK, 1 CONTROL_VIOLATED)** -- PREFIX predicts category with structured selectivity
- T6 tautology gate PASSED: PREFIX adds 0.058 bits (2.1%) beyond base group, concentrated in t-base (V=0.891) and o-base (V=0.217)
- qo is near-pure THERMAL channel (59.0%, rank 1/32); ct is near-pure MONITORING (90.0%)
- ok/ot sister pair diverges (V=0.105): ok THERMAL-enriched, ot OPERATION-enriched
- ch/sh diverge in B (V=0.121) but not A (C1268 V=0.021) -- system-dependent effect, survives section/position controls
- BARE tokens are THERMAL-depleted (4.1% vs 27.5%) and FLOW/STAGING-enriched -- PREFIX is primary thermal injection mechanism
- WEAK: da/sa divergence (p=0.013, sub-Bonferroni); base-category alignment 27.6% (below 40% threshold)
- Channel symmetry: EN channel (ch/sh + qo) parallels AX channel (ok/ot + ct) -- sister pair + specialized third member

---

### Sister Category Mechanism (C1303-C1307) -- Phase: SISTER_CATEGORY_MECHANISM (Phase 459)

Tests whether sister pair category divergence (C1298, C1299) is driven by positional placement or genuine categorical selection. Decomposes the mechanism into position control, MIDDLE-level category stability, and cross-lane cargo routing.

| # | Description | Tier | Tags | Location |
|---|-------------|------|------|----------|
| **1303** | **ch/sh Category Divergence Is Position-Independent** (V retention 98.3%; Fisher-combined p=1.17e-4; within-zone V stable 0.094-0.102 across EARLY/MID/LATE; CATEGORY_GENUINE; positional axis C929 orthogonal to categorical axis; N=5,821) | 2 | B, PREFIX, sister pair, ch, sh, category, position | -> [C1303_chsh_position_independent_category.md](C1303_chsh_position_independent_category.md) |
| **1304** | **ok/ot Category Divergence Is Position-Independent** (V retention 124.1%; Fisher-combined p=4.62e-5; position was SUPPRESSING divergence; EARLY V=0.207 strongest; CATEGORY_GENUINE; ok STAGING-enriched, ot MARKING-enriched within zones; N=2,924) | 2 | B, PREFIX, sister pair, ok, ot, category, position | -> [C1304_okot_position_independent_category.md](C1304_okot_position_independent_category.md) |
| **1305** | **MIDDLE Determines Category** (0/33 qualifying MIDDLEs shift dominant category between ch/sh; binom p=1.0; sister pairs diverge via vocabulary SELECTION not TRANSFORMATION; MIDDLE category is intrinsic; mechanism is differential MIDDLE deployment) | 2 | B, PREFIX, MIDDLE, sister pair, category, mechanism | -> [C1305_middle_determines_category.md](C1305_middle_determines_category.md) |
| **1306** | **Cross-Lane Cargo Divergence** (ch->QO vs sh->QO cargo V=0.122 chi2=33.29 p=2.34e-5; ch routes STAGING 20.6% vs 12.9%; sh routes THERMAL 53.6% vs 45.0%; sister identity shapes downstream QO-lane category composition; N=2,220 transitions) | 2 | B, PREFIX, sister pair, ch, sh, QO lane, cross-lane, category | -> [C1306_cross_lane_cargo_divergence.md](C1306_cross_lane_cargo_divergence.md) |
| **1307** | **No Sister x Category x Position Interaction** (ch/sh V range=0.009 perm p=1.0; ok/ot V range=0.114 perm p=1.0; sister category effect is additive with position, not interactive; same category information regardless of line position) | 2 | B, PREFIX, sister pair, position, category, interaction | -> [C1307_no_sister_position_category_interaction.md](C1307_no_sister_position_category_interaction.md) |

**Phase 459 findings (Sister Category Mechanism):**
- **PARTIAL_MODE_SELECTION (4 PASS, 2 FAIL)** -- sister category divergence is genuine and position-independent
- ch/sh V retention 98.3%: position explains almost none of the category divergence (CATEGORY_GENUINE)
- ok/ot V retention 124.1%: position was MASKING divergence; true signal stronger than raw measurement
- 0/33 MIDDLEs shift category between ch/sh: mechanism is vocabulary SELECTION not TRANSFORMATION
- Cross-lane cargo diverges: ch routes STAGING to QO lane, sh routes THERMAL (V=0.122)
- No three-way interaction: sister category effect is constant across position zones

---

### Cross-Mode Category Coupling (C1308-C1312) -- Phase: CROSS_MODE_CATEGORY_COUPLING (Phase 460)

Tests whether Mode A and Mode B parallel tracks show structured category coupling — sequential zig-zag, positional alignment, or token-level interleaving. Discovers positional synchronization and B->A thermal feedback while ruling out sequential dependency.

| # | Summary | Tier | Tags | Link |
|---|---------|------|------|------|
| **1308** | **Within-Paragraph Category Coherence** (within-para A-B JSD=0.141 < cross-para JSD=0.170 p=7.4e-6; both modes share paragraph's category key; 258 paragraphs with both modes) | 2 | B, paragraph, mode, category, coherence | -> [C1308_within_paragraph_category_coherence.md](C1308_within_paragraph_category_coherence.md) |
| **1309** | **Mode Category Specialization** (A=THERMAL 32.5% MONITORING 2.6x; B=STAGING 1.37x TRANSITION 1.64x FLOW 1.22x; complementarity is mode-level not pair-specific; coverage perm p=1.0) | 2 | B, mode, category, specialization, THERMAL, TRANSITION | -> [C1309_mode_category_specialization.md](C1309_mode_category_specialization.md) |
| **1310** | **Positional Category Alignment** (same-position same-category rate 21.4% vs 16.9% chance = 1.27x enrichment; perm p=0.001; NMI 0.042-0.063 across 5 position bins; THERMAL->THERMAL strongest at 7.6%) | 2 | B, mode, position, category, alignment, parallel tracks | -> [C1310_positional_category_alignment.md](C1310_positional_category_alignment.md) |
| **1311** | **B-to-A Thermal Feedback Signal** (ke_ratio->MARKING rho=-0.198 p=0.0006; ke_ratio->THERMAL rho=+0.176 p=0.002; effect sizes small-to-moderate; feedback is B->A only, A->B shows no signal p>0.3; BA handoff TRANSITION->THERMAL at 12.0%; 300 BA pairs) | 2 | B, mode, thermal, feedback, cross-mode, MARKING | -> [C1311_b_to_a_thermal_feedback.md](C1311_b_to_a_thermal_feedback.md) |
| **1312** | **No Cross-Line Sequential Category Coupling** (zig-zag WEAKER than null Z=-3.39 perm p=0.999; no A->B prediction V=0.170 p=0.146; no cross-line transition grammar; 0 cross-line forbidden transitions; all interleaving ratios increase entropy; same-mode > cross-mode coupling AA r=0.463 vs BA r=0.328) | 2 | B, mode, cross-line, sequential, independence, forbidden | -> [C1312_no_cross_line_sequential_coupling.md](C1312_no_cross_line_sequential_coupling.md) |

**Phase 460 findings (Cross-Mode Category Coupling):**
- **WEAK_ZIGZAG_ARTIFACT_SUSPECT (2 PASS, 1 WEAK, 5 FAIL)** + parallel track probe
- Paragraphs provide a shared category "key" for both modes (within < cross JSD, p=7.4e-6)
- Mode A = specification voice (THERMAL/MONITORING), Mode B = execution voice (FLOW/STAGING/TRANSITION)
- Positional synchronization: same-category at same position 1.27x enriched (perm p=0.001)
- B->A thermal feedback: hot B lines suppress MARKING in next A line (rho=-0.198)
- No sequential coupling: zig-zag, interleaving, transition grammar, and forbidden transitions all negative
- BA handoff dominated by TRANSITION->THERMAL (12.0%) — B exits through transition, A re-enters with thermal

---

### Distillation Terminology Mapping (C1313-C1316) -- Phase: DISTILLATION_TERMINOLOGY_MAPPING (Phase 461)

Tests whether distillation physics maps to the manuscript's structural patterns. 10 tests with negative controls: two-channel thermal model, overshoot-correct cycling, MIDPROCESS action mapping, REGIME profile discrimination, luting, cooling modes, monitoring, o-prefix differentiation, thermal shock, bang-bang rate. 9/10 pass. Tier 3-4 interpretive mapping with Tier 2 structural byproducts.

| # | Summary | Tier | Tags | Link |
|---|---------|------|------|------|
| **1313** | **Two-Channel Thermal Atom Separation** (qo k-frac=0.510 vs ok k-frac=0.001; ok e-frac=0.282 vs qo e-frac=0.102; MW p=0.0 both; perm p=0.0; sa neutral control p=0.999) | 2 | B, PREFIX, thermal, atom, qo, ok, separation | -> [C1313_two_channel_thermal_atom_separation.md](C1313_two_channel_thermal_atom_separation.md) |
| **1314** | **Overshoot-Correct Bigram Enrichment** (qo-k->ok-e: 103 obs vs 72.0 null = 43% above chance p=0.0; reverse: 112 obs vs 72.1 null = 55% above chance p=0.0; da->sa neg ctrl p=0.996) | 2 | B, PREFIX, thermal, sequencing, bigram, cycling | -> [C1314_overshoot_correct_bigram_enrichment.md](C1314_overshoot_correct_bigram_enrichment.md) |
| **1315** | **REGIME B Token Profile Discrimination** (6/7 metrics KW p<0.01 for B tokens by REGIME; A tokens 0/7 significant; B-specific discrimination in k-frac, e-frac, h-frac, THERMAL, MONITORING, CONTAINMENT rates) | 2 | B, REGIME, discrimination, category, atom, A-control | -> [C1315_regime_b_token_profile_discrimination.md](C1315_regime_b_token_profile_discrimination.md) |
| **1316** | **O-PREFIX Categorical Distinction** (ok/ot/ol/or 4x8 chi-sq p<0.001; ok->ot asymmetry 1.18x vs 1.04x; trigram qo->ok->ot preferred; ok +4.4% THERMAL, ot +4.9% OPERATION; 3/4 distinct dominant category) | 2 | B, PREFIX, o-prefix, ok, ot, ol, or, category, sequential | -> [C1316_o_prefix_categorical_distinction.md](C1316_o_prefix_categorical_distinction.md) |

**Phase 461 findings (Distillation Terminology Mapping):**
- **9/10 tests pass** (T10 fails: alternation ordering reversed)
- Two-channel thermal atom separation: qo = k-dominant (0.510), ok = e-dominant (0.282), completely non-overlapping
- Overshoot-correct cycling: qo-k to ok-e transitions 43% above chance within lines
- REGIME discrimination: 6/7 metrics significant for B, 0/7 for A — B-specific
- O-PREFIX distinction: ok/ot/ol/or all categorically separable; ok->ot sequential ordering (1.18x)
- 13 modern MIDPROCESS actions all map to distinguishable PREFIX+category patterns (cosine 0.73 vs 0.003 random)
- 5 Fits registered (F-B-008 through F-B-012)
- Token coverage: 99.5% of B tokens receive a distillation mapping
- Post-phase: ok = thermal verification (coarse), ot = operational verification (fine); control flow sh->qo->ok->ot

---

### Visual Text Block Parallel Operators (C1317-C1320) -- Phase: TEXT_BLOCK_PARALLEL_OPERATORS (Phase 462)

Tests whether visual text blocks (physical text clumps on folios) group complementary parallel operators. 7-test battery: block census, thermal convergence, PREFIX divergence, category convergence, operational coverage, block-initial enrichment, section architecture. 4/7 pass. Key finding: blocks maximize internal diversity — paragraphs within a block specialize in different operations (PREFIX), different thermal profiles (kernel), and different categories. Block-initial paragraphs serve as headers.

| # | Summary | Tier | Tags | Link |
|---|---------|------|------|------|
| **1317** | **Visual Text Block Census** (91.5% multi-block, 485 blocks/82 folios; S=12.4, B=4.6, H=2.3 blocks/folio; KW H=56.8/123.5 both p<0.001) | 2 | B, block, census, section, layout | -> [C1317_visual_text_block_census.md](C1317_visual_text_block_census.md) |
| **1318** | **Block PREFIX Complementarity** (within-block JSD=0.276 > between-block 0.225; MW z=6.12 p<0.001; perm p=0.000; confirmed 4/5 sections: B p=0.006, C p=0.030, H p=0.017, S p<0.001) | 2 | B, block, PREFIX, complementarity, divergence, parallel | -> [C1318_block_prefix_complementarity.md](C1318_block_prefix_complementarity.md) |
| **1319** | **Block-Initial Paragraph Enrichment** (HT: 7.3% vs 4.9% z=7.07 p<0.001; MARKING: 9.4% vs 7.0% z=4.81 p<0.001; 484 initial vs 190 internal paragraphs) | 2 | B, block, HT, MARKING, enrichment, header | -> [C1319_block_initial_enrichment.md](C1319_block_initial_enrichment.md) |
| **1320** | **Block Internal Diversity** (kernel cosine: within 0.888 vs between 0.920, p=0.104; category Jaccard: within 0.667 vs between 0.731, z=-3.96 p<0.001; thermal envelope hypothesis falsified; blocks maximize internal diversity) | 2 | B, block, kernel, category, diversity, falsified | -> [C1320_block_internal_diversity.md](C1320_block_internal_diversity.md) |

**Phase 462 findings (Text Block Parallel Operators):**
- **4/7 tests pass** (T2, T4 reversed — blocks diversify rather than converge; T5 marginal p=0.021)
- Block census: 91.5% multi-block, 485 total, section-specific architecture (S=12.4 vs H=2.3 blocks/folio)
- PREFIX complementarity: within-block JSD > between-block (p<0.001), confirmed in 4/5 sections independently
- Block-initial enrichment: HT 7.3% vs 4.9% (z=7.07), MARKING 9.4% vs 7.0% (z=4.81) — header pattern
- Thermal envelope hypothesis FALSIFIED: within-block kernel similarity NOT higher than between-block
- Category envelope hypothesis FALSIFIED: within-block category overlap significantly LOWER than between-block
- Revised model: blocks are self-contained processing stages that maximize internal operational diversity
- Structural hierarchy confirmed: token < line < paragraph < block < folio

---

### Block Gallows Ordering (C1321-C1322) -- Phase: BLOCK_GALLOWS_ORDERING (Phase 463)

Tests whether gallows letters encode paragraph operator roles within blocks and whether blocks have internal ordered execution structure. 5-test battery: gallows-category association, gallows-kernel association, gallows ordering within blocks, within-block position gradient, block position in folio. 1/5 pass. Key finding: gallows encode paragraph PHASE (when in block), not TYPE (what it does). t-gallows clusters late (position 0.700), k/f/p cluster early (0.255-0.319). Universal k/f/p→t transition flow.

| # | Summary | Tier | Tags | Link |
|---|---------|------|------|------|
| **1321** | **Gallows Within-Block Ordering** (t mean pos=0.700 vs k/f/p 0.255-0.319; transition chi-sq=64.88 df=9 p<0.001; perm p=0.002; k→t 77%, p→t 74%, t→t 72%; 131 blocks, 186 transitions) | 2 | B, gallows, block, ordering, transition, t-late | -> [C1321_gallows_within_block_ordering.md](C1321_gallows_within_block_ordering.md) |
| **1322** | **Gallows-Category Independence** (0/8 categories KW p<0.01 across gallows types; 1/3 kernel fracs sig but only 1 section; category range across gallows <0.024; gallows encode position not type) | 2 | B, gallows, category, independence, kernel, falsified | -> [C1322_gallows_category_independence.md](C1322_gallows_category_independence.md) |

**Phase 463 findings (Block Gallows Ordering):**
- **1/5 tests pass** (T1/T2 fail: gallows don't predict operational type; T4/T5 fail: no position gradients)
- Gallows within-block ordering: t clusters late (0.700), k/f/p cluster early (0.255-0.319)
- Transition matrix highly non-uniform (chi-sq=64.88, p<0.001): universal k/f/p→t flow
- t self-continues at 72% within blocks — sustained execution/continuation marker
- Gallows-category independence: 0/8 categories significantly predicted by gallows letter
- Gallows encode WHEN in the block (phase), not WHAT it does (type)
- C869 (Tier 3) partially supported (k/f early) but revised: split is k/f/p vs t, not k/f vs p/t
- PREFIX encodes operational specialization (C1318), gallows encodes positional phase — orthogonal axes

---

### Block Execution Cycle (C1323-C1326) -- Phase: BLOCK_EXECUTION_CYCLE (Phase 464)

Tests whether visual text blocks form complete execution cycles with cross-block restart, block-final termination signatures, and REGIME inheritance.

| # | Summary | Tier | Tags | Link |
|---|---------|------|------|------|
| **1323** | **Cross-Block Gallows Restart** (block-final t=39.8%, block-initial k/f/p=72.3%; chi-sq=14.82 df=3 p=0.002; 403 transitions; gallows cycle restarts at block boundaries) | 2 | B, gallows, block, restart, cross-block | -> [C1323_cross_block_gallows_restart.md](C1323_cross_block_gallows_restart.md) |
| **1324** | **Block-Final Termination Absence** (block-final -am DEPLETED 0.36x; suffix mode identical 58.9%=58.9%; 0/8 category shifts; boundaries are gallows-level not vocabulary-level) | 2 | B, block, termination, -am, suffix-mode, falsified | -> [C1324_block_final_termination_absence.md](C1324_block_final_termination_absence.md) |
| **1325** | **Folio REGIME Homogeneity** (within-folio block distance 0.056 < between-folio 0.065; MW z=-8.62 p<0.001; perm p<0.001; folio sets REGIME, blocks inherit) | 2 | B, block, folio, REGIME, kernel, homogeneity | -> [C1325_folio_regime_homogeneity.md](C1325_folio_regime_homogeneity.md) |
| **1326** | **Cross-Block Category Continuity** (cross-block JSD 0.071 < within-block 0.136; z=-8.98 p<0.001; block boundaries smooth not discontinuous; reinforces C1320 within-block diversity) | 2 | B, block, category, continuity, cross-block, diversity | -> [C1326_cross_block_category_continuity.md](C1326_cross_block_category_continuity.md) |

**Phase 464 findings (Block Execution Cycle):**
- **2/8 tests pass** (A1 gallows restart, C1 REGIME homogeneity)
- Gallows cycle restarts at block boundaries: k/f/p-enriched at block-initial, t-enriched at block-final
- Block-final paragraphs show NO termination signatures: -am depleted (0.36x), suffix mode identical, 0/8 category shifts
- Folio REGIME homogeneity: blocks within a folio share thermal character (kernel distance 0.056 < 0.065)
- Cross-block category continuity: adjacent blocks more categorically similar than within-block paragraphs (JSD 0.071 < 0.136)
- Block boundaries are gallows-level structural markers (C845), not vocabulary-level content markers
- Outcome matches predicted: "cross-block transitions confirmed but block-final signatures weak"
- Block architecture: folio = REGIME container, block = processing stage, paragraph = specialized operator

---

### Section S Block Architecture (C1327-C1329) -- Phase: SECTION_S_BLOCK_ARCHITECTURE (Phase 465)

Tests whether Section S's anomalous single-paragraph blocks (12.4/folio, 1.17 paras/block) are parallel monitoring stations or ordered processing stages. Parallel stations hypothesis falsified (1/6 pass).

| # | Summary | Tier | Tags | Link |
|---|---------|------|------|------|
| **1327** | **Section S Ordinal Progression** (OPERATION rho=-0.169 p<0.001; THERMAL rho=+0.123 p=0.003; TRANSITION rho=+0.160 p=0.002; 3/12 metrics significant; early=OPERATION, late=THERMAL/TRANSITION; falsifies exchangeability) | 2 | B, section-S, ordinal, category, progression, falsified | -> [C1327_section_s_ordinal_progression.md](C1327_section_s_ordinal_progression.md) |
| **1328** | **Section S p-Gallows Dominance** (p=59.8% of S blocks; p->p 69% self-continuation; chi-sq=61.58 p<0.001; distinct from k/f/p->t pattern in non-S; all "running mode") | 2 | B, section-S, gallows, p-dominance, transition | -> [C1328_section_s_p_gallows_dominance.md](C1328_section_s_p_gallows_dominance.md) |
| **1329** | **Section S Block Diversity** (within-folio block JSD 0.069 > non-S 0.052; z=7.20 p<0.001; S blocks MORE diverse, not less; kernel distance also higher than B/C; reverses parallel prediction) | 2 | B, section-S, block, diversity, category, REGIME, falsified | -> [C1329_section_s_block_diversity.md](C1329_section_s_block_diversity.md) |

**Phase 465 findings (Section S Block Architecture):**
- **1/6 tests pass** — parallel stations hypothesis falsified
- S blocks show ordinal progression: OPERATION→THERMAL/TRANSITION shift with block position (C1327)
- S has unique p-gallows dominance: p→p self-continuation at 69%, no k/f/p→t cycle (C1328)
- S blocks are MORE categorically diverse than non-S, not less (C1329)
- S blocks ARE vocabulary-independent (Jaccard 0.327 < non-S 0.438), but operationally ordered
- lk distribution marginal ordinal trend (p=0.010) — monitoring may increase toward later blocks
- Section S = ordered monitoring sequence through operationally diverse checkpoints, not parallel stations

### Block Vocabulary Drift (C1330-C1331) -- Phase: BLOCK_VOCABULARY_DRIFT (Phase 466)

| # | Constraint | Tier | Tags | Ref |
|---|-----------|------|------|-----|
| **1330** | **Block Vocabulary Narrowing** (later blocks use fewer distinct MIDDLEs; median rho=-0.248 perm p<0.001; 39/56 folios negative; universal across sections B/C/H/S; coverage of block 0 MIDDLEs drops to ~0.40 by block 3) | 2 | B, block, vocabulary, MIDDLE, ordinal, narrowing | -> [C1330_block_vocabulary_narrowing.md](C1330_block_vocabulary_narrowing.md) |
| **1331** | **Iterative Refinement Falsified** (blocks do NOT show directional drift toward target: k not decreasing rho=+0.026 p=0.600; Mode A not decreasing rho=-0.038 p=0.199; FL not advancing rho=+0.021 p=0.435; only e marginal at p=0.033; section-specific sub-Bonferroni signals do not constitute universal mechanism) | 1 | B, block, refinement, falsified, kernel, suffix-mode, FL | -> [C1331_iterative_refinement_falsified.md](C1331_iterative_refinement_falsified.md) |

**Phase 466 findings (Block Vocabulary Drift):**
- **1/4 tests pass** — iterative refinement hypothesis falsified
- Vocabulary narrowing is universal: later blocks use fewer distinct MIDDLEs (C1330)
- No k→e kernel drift, no Mode A→B shift, no FL stage progression across blocks (C1331)
- Section-specific signals: B/C show partial refinement, H reversed, S flat — no universal mechanism
- C1326 (cross-block similarity) is NOT explained by convergence — blocks share REGIME, not a target

### Multiplexed Procedure Test (C1332-C1333) -- Phase: MULTIPLEXED_PROCEDURE_TEST (Phase 467)

| # | Constraint | Tier | Tags | Ref |
|---|-----------|------|------|-----|
| **1332** | **Block-0 Marking Enrichment** (block-0-unique MIDDLEs are MARKING 2.48x enriched and MONITORING 1.57x enriched; OPERATION 0.65x and TRANSITION 0.64x depleted; STAGING+CONTAINMENT flat at 0.92x; chi2=212, V=0.136; holds in 3/3 sections; "setup block" prediction falsified) | 2 | B, block, MARKING, MONITORING, category, vocabulary, block-0 | -> [C1332_block0_marking_enrichment.md](C1332_block0_marking_enrichment.md) |
| **1333** | **Kernel Most Stable Dimension** (within-folio inter-block kernel distance 0.027 < category JSD 0.052 < PREFIX JSD 0.145; kernel lowest in all 5 sections; kernel < category in 36/56 folios MW p=0.007; kernel < PREFIX in 56/56 folios p<0.001) | 2 | B, block, kernel, stability, REGIME, dimension | -> [C1333_kernel_most_stable_dimension.md](C1333_kernel_most_stable_dimension.md) |

**Phase 467 findings (Multiplexed Procedure Test):**
- **2/4 tests pass** — block 0 IS special but NOT as a "setup" block
- Block-0-unique vocabulary is MARKING/MONITORING-enriched, not STAGING/CONTAINMENT (C1332)
- Kernel is the most stable inter-block dimension in every section (C1333)
- No significant block size gradient (token rho=-0.050, p=0.251) — later blocks not reliably shorter
- Vocabulary containment asymmetry exists (6.2pp, p=0.004) but below 10pp threshold
- Block 0 provides marking/annotation context; later blocks focus on operational execution
- Strict multiplexing model (shared apparatus setup) NOT confirmed; "marking context" model emerges

### A Paragraph Category Architecture (C1334-C1337) -- Phase: A_PARAGRAPH_CATEGORY_ARCHITECTURE (Phase 468)

| # | Constraint | Tier | Tags | Ref |
|---|-----------|------|------|-----|
| **1334** | **A Paragraph Dominance Structure** (43.6% of A paragraphs are STAGING-dominant at 1.89x base rate; CONTAINMENT/MONITORING/MARKING rarely or never dominate paragraphs; mean dominance 0.299 vs null 0.281, perm p<0.001; section-structured: H→STAGING, P→THERMAL, T→FLOW) | 2 | A, paragraph, category, dominance, STAGING, section | -> [C1334_a_paragraph_dominance_structure.md](C1334_a_paragraph_dominance_structure.md) |
| **1335** | **A Paragraph Category Taxonomy** (5 distinct category-based paragraph types: STAGING:105, FLOW:48, TRANSITION:42, THERMAL:33, OPERATION:12; within-type JSD 0.074 < between-type 0.108, MW z=-45.67 p<0.001; gap 0.034 vs null 0.0002; independent of C850 structural taxonomy) | 2 | A, paragraph, category, taxonomy, type | -> [C1335_a_paragraph_category_taxonomy.md](C1335_a_paragraph_category_taxonomy.md) |
| **1336** | **MARKING Paragraph-Initial Concentration** (MARKING mean position 0.429 in A paragraphs, deviation 0.071, perm p<0.001; first-token MARKING rate 15.5% vs base 7.5% = 2.07x; sole exception to paragraph-level position-free behavior; parallels B C1287 header and C1332 block-0 enrichment) | 2 | A, paragraph, MARKING, positional, cross-system | -> [C1336_marking_paragraph_initial_concentration.md](C1336_marking_paragraph_initial_concentration.md) |
| **1337** | **A Folio Paragraph Category Independence** (consecutive paragraph JSD 0.104 vs random 0.096, perm p=0.850; first-paragraph JSD from rest = 0.004, max enrichment 1.25x; confirms C240 NON_SEQUENTIAL extends to paragraph categories; contrasts with B C1326 block continuity and C1332 block-0 distinctness) | 2 | A, paragraph, folio, category, independence, NON_SEQUENTIAL | -> [C1337_a_folio_paragraph_category_independence.md](C1337_a_folio_paragraph_category_independence.md) |

**Phase 468 findings (A Paragraph Category Architecture):**
- **2/4 tests pass, 1 weak, 1 fail** — A paragraph category architecture characterized
- STAGING dominates the A registry: 43.6% of paragraphs are STAGING-dominant (C1334)
- 5 distinct paragraph types exist, complementing C850's structural taxonomy (C1335)
- MARKING is the sole exception to position-free paragraph behavior — front-loaded at 0.429 (C1336)
- No folio-level paragraph sequencing — A paragraphs are categorically independent within folios (C1337)
- Section specialization: H is STAGING-centric, P is THERMAL-centric, T is FLOW-centric
- Cross-system MARKING pattern: front-loaded in A paragraphs (C1336), enriched in B headers (C1287), enriched in B block 0 (C1332)

### Suffix Mode Assignment (C1338-C1341) -- Phase: SUFFIX_MODE_ASSIGNMENT (Phase 469)

| # | Constraint | Tier | Tags | Ref |
|---|-----------|------|------|-----|
| **1338** | **MIDDLE Suffix Selectivity** (I(MIDDLE; suffix_cat) = 0.697 bits, 11.57x more than I(line_mode; suffix_cat) = 0.060; 60% of frequent MIDDLEs suffix-locked at >80%; 37.1% bare-locked, 22.9% terminal-locked; suffix is a MIDDLE property not a line property) | 2 | B, suffix, mode, MIDDLE, identity, mutual-information | -> [C1338_middle_suffix_selectivity.md](C1338_middle_suffix_selectivity.md) |
| **1339** | **MIDDLE Mode Flexibility** (only 7.7% of frequent MIDDLEs mode-locked >80%; 34.6% flexible 40-60%; MIDDLEs freely appear in both modes; THERMAL MIDDLEs lean Mode B 0.406 despite THERMAL enrichment in Mode A — suffix behavior not token selection) | 2 | B, suffix, mode, MIDDLE, flexibility, category | -> [C1339_middle_mode_flexibility.md](C1339_middle_mode_flexibility.md) |
| **1340** | **Suffix Stability Across Modes** (same MIDDLE carries same suffix regardless of mode; median cross-mode JSD 0.020; only 12.1% show significant shift p<0.01; small real context effect perm p=0.003 mean JSD 0.035 vs null 0.026) | 2 | B, suffix, mode, stability, context | -> [C1340_suffix_stability_across_modes.md](C1340_suffix_stability_across_modes.md) |
| **1341** | **Suffix Mode Is Emergent Property** (token-identity-predicted mode matches actual 80.0% accuracy; baseline 59.7% lift 1.34x; Mode A recall 89.4%; mode emerges from token composition ~80%, contextual modulation ~20%; resolves C1256 opener mechanism and C1259 flat mode proportion) | 2 | B, suffix, mode, emergent, generative, identity | -> [C1341_mode_emergent_property.md](C1341_mode_emergent_property.md) |

**Phase 469 findings (Suffix Mode Assignment):**
- **1/4 PASS, 1 FAIL, 2 MIXED** — suffix mode mechanism resolved
- MIDDLE identity determines suffix 11.57x more than line mode (C1338) — suffix is a token property
- MIDDLEs are NOT mode-locked (92.3% flexible), freely appearing in both modes (C1339)
- Same MIDDLE keeps its suffix across modes (median JSD 0.020, 87.9% stable) (C1340)
- Line mode is 80% predictable from token composition alone (C1341) — mode is emergent, not imposed
- The generative model: MIDDLEs bring intrinsic suffix preferences → aggregate profile → line mode emerges
- ~20% contextual modulation accounts for the "low selectivity" MIDDLEs and mode-level coordination
- Resolves: C1256 (opener seeds profile), C1259 (flat proportion = position-independent vocabulary)

### Suffix Mode Context (C1342-C1346) -- Phase: SUFFIX_MODE_CONTEXT (Phase 470)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| **1342** | **PREFIX Modulates Suffix Choice** (PREFIX is dominant contextual suffix modulator for flexible MIDDLEs; conditional MI 0.097 bits 2.82x null perm p=0.001; V=0.23; da→93% bare qo→41% terminal ok_group→52% terminal BARE→41% bare; resolves C1339 THERMAL paradox) | 2 | B, PREFIX, suffix, modulation, context | -> [C1342_prefix_suffix_modulation.md](C1342_prefix_suffix_modulation.md) |
| **1343** | **Category Environment Suffix Effect** (THERMAL-rich line neighborhoods push flexible MIDDLEs toward terminal suffix; terminal tokens have mean 26.6% THERMAL neighbors vs 23.3% for bare; Mann-Whitney Z=5.87 p<0.001; conditional MI 0.057 bits) | 2 | B, category, environment, suffix, THERMAL | -> [C1343_category_environment_suffix_effect.md](C1343_category_environment_suffix_effect.md) |
| **1344** | **Position Suffix Modulation** (MID-line position boosts terminal suffix for flexible MIDDLEs; MID 40.6% terminal vs EARLY 34.6%; V=0.058 p<0.001; Spearman rho=0.095; conditional MI 0.024 bits; specification peaks at mid-line) | 2 | B, position, suffix, modulation | -> [C1344_position_suffix_modulation.md](C1344_position_suffix_modulation.md) |
| **1345** | **Opener Mode Weak Propagation** (paragraph opener mode weakly propagates to flexible MIDDLE suffix; A-opened 38.8% terminal vs B-opened 36.1%; V=0.048 p=0.018; conditional MI 0.016 bits; section-heterogeneous: Section C V=0.185 drives effect) | 2 | B, opener, mode, paragraph, propagation | -> [C1345_opener_mode_weak_propagation.md](C1345_opener_mode_weak_propagation.md) |
| **1346** | **Contextual Modulation Decomposition** (20% contextual residual decomposes: PREFIX 0.097 bits 50% → environment 0.057 bits 29% → position 0.024 bits 12% → opener 0.016 bits 8%; factors largely non-redundant MI 0.003-0.006 bits between pairs; modulation is probabilistic not deterministic) | 2 | B, context, decomposition, PREFIX, suffix, mode | -> [C1346_contextual_modulation_decomposition.md](C1346_contextual_modulation_decomposition.md) |

**Phase 470 findings (Suffix Mode Context):**
- **3/5 PASS, 1 MIXED, 1 INCONCLUSIVE** — contextual residual decomposed
- PREFIX is the dominant contextual channel (C1342: 0.097 bits, 50% of total contextual MI)
- da PREFIX suppresses suffixation (93% bare), qo/ok bias toward terminal (C1342)
- THERMAL-rich neighborhoods independently push toward terminal suffix (C1343: Z=5.87)
- MID-line position has highest terminal fraction (C1344: 40.6% vs EARLY 34.6%)
- Opener mode barely reaches individual token suffix (C1345: V=0.048, section-heterogeneous)
- Factors are non-redundant and distributed — PREFIX dominates but doesn't account for everything (C1346)
- Resolves: C1339 THERMAL paradox, extends C1297/C1302 from category to suffix domain

### A-B Category Flow (C1347-C1349) -- Phase: A_B_CATEGORY_FLOW (Phase 471)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| **1347** | **B Reshapes Bridge Category Usage** (Bridge MIDDLEs carry same category in A and B but B reshapes usage; A delivers STAGING-heavy 25.0% B consumes THERMAL-heavy 23.7%; amplifies THERMAL 1.72x OPERATION 1.58x suppresses MONITORING 0.27x STAGING 0.54x; JSD=0.026 rho=0.64; consumption matches B total JSD=0.004; mode correlation Z=3.45 p=0.0004) | 2 | cross-system, bridge, category, reshaping, THERMAL | -> [C1347_bridge_category_reshaping.md](C1347_bridge_category_reshaping.md) |
| **1348** | **A Sections Differentiate at Category Level** (Despite C1136 MIDDLE-level uniformity cosine 0.9997 A sections differentiate at category level chi2=380 V=0.144 perm p=0.001; P is THERMAL-heavy 25.1% T is FLOW-heavy 22.9% H is STAGING-heavy 26.0%; cross-system T→T rho=0.85 p=0.016; category-level parameterization via frequency weighting of shared MIDDLEs) | 2 | cross-system, section, category, differentiation | -> [C1348_section_category_differentiation.md](C1348_section_category_differentiation.md) |
| **1349** | **Dark Pipeline Preserves Category Structure** (Dark pipeline 300 MIDDLEs preserves category structure A→B almost perfectly JSD=0.009 rho=0.976 p=0.005; MARKING dominates both sides A 40.0% B 33.1%; section-modulated in B chi2=184 V=0.166 perm p=0.001; bridge-dark category independence rho=0.19 p=0.57; dual-channel architecture confirmed) | 2 | cross-system, dark, category, preservation, independence | -> [C1349_dark_pipeline_category_preservation.md](C1349_dark_pipeline_category_preservation.md) |

**Phase 471 findings (A-B Category Flow):**
- **2 MIXED, 1 SECTION_FLOW, 1 PRESERVED** — dual-channel category architecture quantified
- B actively reshapes bridge category delivery: amplifies THERMAL/OPERATION, suppresses STAGING/MONITORING (C1347)
- Bridge consumption perfectly integrates into B's category landscape: JSD(consumption, B_total) = 0.004 (C1347)
- A sections differentiate at category level despite MIDDLE-level uniformity (C1348: V=0.144, perm p=0.001)
- Category-level parameterization: A sends same MIDDLEs at different rates, creating section-specific category signatures (C1348)
- Dark pipeline preserves category structure near-perfectly across systems (C1349: rho=0.976, JSD=0.009)
- Bridge and dark carry independent category information per B section (C1349: rho=0.19)
- Extends: C918 (A parameterizes B — now quantified at category level), C1136 (section-blind MIDDLEs — overturned at category level), C1272 (dark not category-sorted — explains preservation)

### Dark Pipeline Structure (C1350-C1353) -- Phase: DARK_PIPELINE_STRUCTURE (Phase 472)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| **1350** | **Dark MIDDLEs Atomistically Distributed** (No within-section co-occurrence structure 0/5 sections significant; dark-dark adjacency ratio=1.024 p=0.76 random; no combinatorial groups no material-list behavior; each dark MIDDLE operates independently) | 2 | B, dark, co-occurrence, adjacency, atomistic | -> [C1350_dark_atomistic_distribution.md](C1350_dark_atomistic_distribution.md) |
| **1351** | **Dark Successor Entropy Is Narrow** (Dark MIDDLEs have significantly narrower successor entropy than bridge; median 2.59 vs 4.18 bits Z=-7.45 p<0.001; each dark token constrains local grammar continuation to restricted instruction classes; contra material-referent prediction; consistent with context-setting parameters) | 2 | B, dark, entropy, successor, grammar, context | -> [C1351_dark_successor_constraint.md](C1351_dark_successor_constraint.md) |
| **1352** | **Dark Folio Span Frequency-Matched** (78.3% of reliable dark MIDDLEs span folios within ±2σ of frequency-controlled null; 21.7% concentrated 0% dispersed; no bimodal staples-vs-specialists split; unimodal median 8 folios mean 10.8; span is consequence of abundance not role) | 2 | B, dark, span, frequency, distribution | -> [C1352_dark_span_frequency_matched.md](C1352_dark_span_frequency_matched.md) |
| **1353** | **Dark Weak Positional Bias** (Dark tokens precede bridge 52.7% Z=3.0 perm p=0.004 but effect size trivial 2.7% above null; section-uniform 49-57%; no dedicated syntactic slot; freely interleaved with grammar tokens) | 2 | B, dark, position, ordering, weak | -> [C1353_dark_weak_positional_bias.md](C1353_dark_weak_positional_bias.md) |

**Phase 472 findings (Dark Pipeline Structure):**
- **1 NARROW, 3 MIXED, 1 RANDOM** — dark pipeline is neither material referents nor process identifiers
- Dark MIDDLEs are atomistic: no co-occurrence groups, no adjacency clustering (C1350)
- Dark successor entropy is significantly narrower than bridge (C1351: Z=-7.45) — each dark token constrains grammar continuation
- Folio span matches frequency expectation, no staples-vs-specialists split (C1352)
- Weak positional bias (52.7% before bridge) but no syntactic slot (C1353)
- Overall: dark pipeline = **context-setting parameters** that independently constrain local execution, not material referents or process labels
- Falsifies: material-referent interpretation (no co-occurrence groups, no wide entropy, no clustering)
- Extends: C1349 (dark preserves A's category structure — the preserved content is parameterization context)

### Layered Grammar Test (C1354-C1357) -- Phase: LAYERED_GRAMMAR_TEST (Phase 473)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| **1354** | **Dark Grammar Influence Is Local Not Contextual** (Dark presence does NOT condition bridge-to-bridge transitions MI=0.098 null=0.101 perm p=0.90; dark removal does not genericize transitions entropy diff 0.73 null 0.72 p=0.38; three-tier grammar model FALSIFIED; dark influence is next-token only) | 2 | B, dark, grammar, local, falsification | -> [C1354_dark_local_not_contextual.md](C1354_dark_local_not_contextual.md) |
| **1355** | **Dark Entropy Difference Partially Frequency-Mediated** (Dark-bridge successor entropy difference survives frequency matching Z=-5.60 p<0.001 but collapses under subsampling to equal n Z=-0.55 p=0.50; dark MIDDLEs have restricted environments rather than inherently narrow entropy; C1351 magnitude is partially sampling artifact) | 2 | B, dark, entropy, frequency, artifact | -> [C1355_dark_entropy_frequency_ambiguous.md](C1355_dark_entropy_frequency_ambiguous.md) |
| **1356** | **Dark MIDDLE Identity Beyond PREFIX** (Within each PREFIX group dark MIDDLE identity significantly predicts successor class conditional MI=2.761 null=2.683 Z=4.50 perm p<0.001; compound structure encodes specific grammar constraints PREFIX cannot explain; 13 PREFIX groups MI range 1.44-3.11 bits) | 2 | B, dark, PREFIX, MIDDLE, information | -> [C1356_dark_middle_beyond_prefix.md](C1356_dark_middle_beyond_prefix.md) |
| **1357** | **Dark Proximity Weakly Boosts Terminal Suffix** (Bridge tokens adjacent to dark have higher terminal rate 25.2% vs 20.7% Z=3.51 p<0.001 V=0.042; survives PREFIX control 12/16 groups show boost; effect real but tiny; dark proximity biases toward specification mode) | 2 | B, dark, suffix, terminal, proximity | -> [C1357_dark_proximity_suffix_boost.md](C1357_dark_proximity_suffix_boost.md) |

**Phase 473 findings (Layered Grammar Test):**
- **Gates PASS, all 3 core tests FAIL** — three-tier grammar model falsified
- Dark successor entropy survives frequency matching but collapses under subsampling (C1355)
- Dark MIDDLE identity adds info beyond PREFIX (C1356: Z=4.50) — genuine but local
- Dark presence does NOT condition line-level bridge transitions (C1354: p=0.90)
- Dark removal does NOT genericize bridge transitions (C1354: p=0.38)
- Dark proximity weakly boosts terminal suffix (C1357: V=0.042) — detectable but tiny
- Overall: dark MIDDLEs have very local grammar influence (next-token) but are NOT a grammar tier
- Falsifies: three-tier grammar model (dark=context → bridge=execution → suffix=mode)
- Preserves: binary model with refinement — dark tokens are grammar-adjacent, not grammar-participating

### Line Micro-Grammar (C1358-C1362) -- Phase: LINE_MICRO_GRAMMAR (Phase 474)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| **1358** | **Class Positional Specialization** (24/48 classes are positional specialists at quintile level p<0.001; FL_SAFE classes 38,40 peak Q4 entropy 1.38-1.81; AXM classes 4,26 peak Q0; half specialist half generalist; extends C556 role-level to full 49-class) | 2 | B, line, position, 49-class | -> [C1358_class_positional_specialization.md](C1358_class_positional_specialization.md) |
| **1359** | **Transition Gradient Resolution** (49x49 matrix changes monotonically across 5 quintiles rho=0.639 p=0.045; Q0-Q4 JSD=0.355 vs Q0-Q1=0.147; AXM self drops 0.737→0.549; gradient accelerates at line-end; perm p<0.001; extends C1156 from 3 zones to smooth gradient) | 2 | B, line, transition, gradient, position | -> [C1359_transition_gradient_resolution.md](C1359_transition_gradient_resolution.md) |
| **1360** | **Forbidden Transition Violations Dispersed and Rare** (11 violations in 20,676 transitions 0.053% rate; KS=0.232 p>=0.05 vs uniform; 10/11 are dy→aiin; hazard avoidance uniform across line positions; forbidden pairs nearly absolute at MIDDLE level) | 2 | B, line, forbidden, position | -> [C1360_forbidden_transition_dispersed.md](C1360_forbidden_transition_dispersed.md) |
| **1361** | **No Positional Motifs** (1/1556 class bigrams significant after Bonferroni; class-class transitions not locked to positions; grammar same everywhere; positional gradient arises from shifting class FREQUENCIES not position-specific rules; confirms C964 free interior at 49-class) | 2 | B, line, bigrams, position, motifs | -> [C1361_no_positional_motifs.md](C1361_no_positional_motifs.md) |
| **1362** | **Position-Conditioned Generative Improvement** (M2p quintile-conditioned wins 5/5 metrics vs stationary M2; class KL 2.4x better, transition JSD 1.7x, positional entropy 1.6x, AXM self 1.8x, specialist accuracy 2.5x; position is M2's primary blind spot; grammar unchanged but class frequencies shift across line) | 2 | B, line, generative, M2p, position | -> [C1362_position_conditioned_generative_improvement.md](C1362_position_conditioned_generative_improvement.md) |

**Phase 474 findings (Line Micro-Grammar):**
- Half the grammar (24/48 classes) has positional anchor points; the other half distributes freely (C1358)
- Transition structure changes as a smooth monotonic gradient Q0→Q4, not discrete zones (C1359)
- AXM self-transition drops 18.8pp from line-start to line-end (0.737→0.549)
- Forbidden transitions are nearly absolute (0.053% violation) and position-independent (C1360)
- No stereotyped class bigrams at specific positions — grammar rules are the same everywhere (C1361)
- Position-conditioned M2p model improves on ALL 5 generative metrics vs stationary M2 (C1362)
- **Key insight:** The positional gradient arises from shifting class frequencies, not position-specific grammar rules. The grammar is invariant; only the vocabulary it draws from changes across the line.

---

### Gradient Steepness (C1363) -- Phase: GRADIENT_STEEPNESS (Phase 475)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| **1363** | **Gradient Steepness Universal** (within-line AXM self gradient 0.737→0.549 does not vary by folio; slope variance does not exceed permutation null p=0.105; delta-R²=0.010 beyond C1168; REGIME KW p=0.22; section KW p=0.13; gradient is universal property of shared grammar not tunable program parameter) | 2 | B, line, folio, gradient | -> [C1363_gradient_steepness_universal.md](C1363_gradient_steepness_universal.md) |

**Phase 475 findings (Gradient Steepness):**
- Per-folio gradient slope variance does not exceed noise (T1 gate: p=0.105) — GATE CLOSED (C1363)
- Gradient steepness adds negligible info beyond C1168 dual boundary architecture (T2 gate: delta-R²=0.010) — GATE CLOSED
- REGIME does not predict steepness (KW p=0.22), nor does section (KW p=0.13)
- **Clean null:** The line gradient is a universal property of the shared 49-class grammar, not a tunable program parameter. Extends C821 (line syntax REGIME-invariant at role level) to class-frequency level.

---

### Position-Conditioned Generation (C1364) -- Phase: POSITION_CONDITIONED_GENERATION (Phase 476)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| **1364** | **Position-Conditioned Generation M2.1** (quintile-conditioned 49-class Markov + symmetric forbidden passes 16/18 generative metrics; gains P1 P2 P3 with zero regressions vs M2-SF 13/18; P1 class KL 2.2x better P2 trans JSD 2.0x P3 specialist 2.4x; remaining failures B4 C2 are morphological not sequential; M2.1 is new generative frontier at 88.9%) | 2 | B, generative, position, M2.1 | -> [C1364_position_conditioned_generation.md](C1364_position_conditioned_generation.md) |

**Phase 476 findings (Position-Conditioned Generation):**
- M2.1 passes 16/18 vs M2-SF baseline 13/18 — gains all 3 positional metrics, zero regressions (C1364)
- Quintile class KL: 0.066→0.029 (2.2x improvement)
- Quintile transition JSD: 0.299→0.146 (2.0x improvement)
- Specialist positional accuracy: 0.149→0.062 (2.4x improvement)
- B5 (fwd-rev JSD) passes at 90% confirming C1034 symmetric forbidden fix
- Remaining failures: B4 (role rank order) and C2 (CC suffix-free) — morphological, not sequential
- **Key result:** Position conditioning is the single largest improvement available to M2. Line position was the primary blind spot and is fully correctable by quintile-conditioning transition matrices.

---

### Corrected Evaluation (C1365) -- Phase: CORRECTED_EVALUATION (Phase 477)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| **1365** | **Corrected Evaluation Full Pass** (M2.1 passes 21/21 after correcting B4 test spec C1030 and C2 test spec C1033; adds C2a macro-CC C2b role-CC X1 PREFIX symmetry X2 MIDDLE asymmetry; PREFIX factoring proven unnecessary C1034; 49-class grammar generatively closed; remaining variance is stochastic not structural) | 2 | B, generative, evaluation, M2.1 | -> [C1365_corrected_evaluation_full_pass.md](C1365_corrected_evaluation_full_pass.md) |

**Phase 477 findings (Corrected Evaluation):**
- M2.1 passes **21/21** corrected metrics (mean 20.0 per run, some runs achieve perfect 21/21)
- B4 correction (C1030): real ordering is EN>FQ>AX>FL>CC, not FQ>FL>EN. M2.1 reproduces it at 70%.
- C2 correction (C1033): split into C2a (macro CC=100% bare, passes 100%) and C2b (role CC matches real within 3pp, passes 70%)
- X1 PREFIX symmetry: M2.1 reproduces PREFIX near-symmetry (0.036 vs real 0.051, within 50%)
- X2 MIDDLE asymmetry: M2.1 reproduces MIDDLE directionality (0.094 vs real 0.126, within 50%)
- PREFIX-factored generation confirmed unnecessary (C1034: distributionally equivalent to M2)
- **Key result:** The 49-class grammar is generatively closed. M2.1 reproduces all measurable structural properties.

---

### Generative Gap Characterization (C1366) -- Phase: GENERATIVE_GAP_CHARACTERIZATION (Phase 479)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| **1366** | **M2.1 Generative Gap Characterization** (Per-folio accent concentrates in class distribution and sequential dynamics, not positional structure or vocabulary composition; 11/31 features show systematic gaps mean\|z\|>1.5; BIO most anomalous section, Archetype 1 highest anomaly; C458 asymmetry not confirmed at generative resolution; 76.5% feature-folio pairs within \|z\|<2) | 2 | B, folio, M2.1, design freedom, accent | -> [C1366_generative_gap_characterization.md](C1366_generative_gap_characterization.md) |

**Phase 479 findings (Generative Gap Characterization):**
- 72 real folios x 100 M2.1 synthetic counterparts, 31 features, z-score analysis
- The folio accent is **macro-automaton operating point**: AXM fraction (mean|z|=2.14), class concentration (2.03), AXM self-transition (2.03), FQ fraction (1.92), mean word length (1.91)
- NOT in: positional features, dark/bridge fractions, spectral gap
- BIO section has HIGHEST anomaly (1.691) — internally coherent (C1048) AND externally distinctive
- Archetype 1 (strong attractor) has highest anomaly (2.034)
- C458 hazard/recovery asymmetry does not manifest at generative gap resolution (ratio=0.96)
- Top 5 most anomalous: f77r, f82r, f83v, f77v, f82v (all BIO)

---

### Folio Accent Vector Analysis (C1367) -- Phase: FOLIO_ACCENT_VECTOR (Phase 480)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| **1367** | **Folio Accent Vector Analysis** (Accent is low-dimensional PC1=58.9%; weakly correlated with archetypes \|rho\|=0.274 → NEW_STRUCTURE; THERMAL category predicts accent beyond kernel partial rho=0.588; BIO accent section-intrinsic p=0.019; archetype 1 = BIO at maximum accent strength) | 2 | B, folio, accent, PCA, category, archetype | -> [C1367_folio_accent_vector.md](C1367_folio_accent_vector.md) |

**Phase 480 findings (Folio Accent Vector):**
- PC1 (59%) = AXM dynamics intensity; PC2 (21%) = sequential complexity; PC3 (9%) = morphological texture
- **Gating test: NEW_STRUCTURE** — accent captures 67% independent structure beyond archetypes
- THERMAL category fraction survives kernel control (partial rho=0.588, p<0.0001); FLOW vanishes after kernel control
- BIO accent persists within REGIME_1 (1.573 vs 1.234, MW p=0.019) — section-intrinsic
- Archetype 1: 8/10 are BIO, mean sign agreement 0.88, driven by class_concentration (4.67) and axm_fraction (4.14)

### Accent PC2/PC3 Decomposition (C1368) -- Phase: ACCENT_PC23_DECOMPOSITION (Phase 481)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| **1368** | **Accent PC2/PC3 Decomposition** (PC2 sequential complexity predicted by THERMAL + folio position LOO R²=0.267; PC3 morphological texture dominated by STARS section eta²=0.457 + CONTAINMENT + sister pair LOO R²=0.496; 0/5 expert predictions confirmed; THERMAL extends accent across PC1+PC2 = 79.4% of variance) | 2 | B, folio, accent, PCA, section, category, sister pair | -> [C1368_accent_pc23_decomposition.md](C1368_accent_pc23_decomposition.md) |

**Phase 481 findings (Accent PC2/PC3 Decomposition):**
- PC2 (20.5%): THERMAL (kernel-residualized) + folio position → LOO R² = 0.267
- PC3 (8.9%): STARS section (eta²=0.457) + CONTAINMENT (residualized) + sister pair ch_preference → LOO R² = 0.496
- Section predicts PC3 (morphological), NOT PC2 (sequential) — reversed expert prediction
- THERMAL is pervasive accent predictor: dominates PC1 (C1367) AND enters PC2 first
- Folio position enters PC2 model — but see C1369: section confound
- 0/5 pre-registered predictions confirmed — accent dimensions behave differently than expected

### Accent Spatial Structure (C1369) -- Phase: ACCENT_SPATIAL_STRUCTURE (Phase 482)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| **1369** | **Accent Spatial Structure** (folio_position in C1368 PC2 is section confound, partial R²=0.010; within-section local coherence: Bio p=0.039, Stars p=0.024; no manuscript gradient; archetypes 1-2 spatially clustered via section concentration; boundary ratio 1.18 moderate) | 2 | B, folio, accent, spatial, section, archetype | -> [C1369_accent_spatial_structure.md](C1369_accent_spatial_structure.md) |

**Phase 482 findings (Accent Spatial Structure):**
- **GATE: SECTION_CONFOUND** — PC2 position partial R²=0.010 < 0.02 after section control
- Within-section local coherence: adjacent Bio folios (p=0.039) and Stars folios (p=0.024) have more similar accents
- 0/9 lag autocorrelations significant — local coherence is weak
- Section boundaries show moderate discontinuity (ratio 1.18), not dramatic
- Archetypes 1-2 spatially clustered (p=0.005, 0.026) — section-driven
- C1368 amendment: folio_position term in PC2 model is section-mediated, not genuine manuscript-order structure

### Category Pipeline Trace (C1370) -- Phase: CATEGORY_PIPELINE_TRACE (Phase 483)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| **1370** | **Category Pipeline Trace A→AZC→B** (WEAKLY_RESHAPED pipeline JS=0.026; THERMAL +72% OPERATION +58% amplified A→B; STAGING -47% MONITORING -73% attenuated; AZC intermediate closer to A; BIO=max THERMAL 2.03x HERBAL=THERMAL-neutral 0.98x; dark 3x more stable than bridge; rank rho=0.644; 4/7 predictions confirmed) | 2 | A, AZC, B, cross-system, category, bridge, dark pipeline | -> [C1370_category_pipeline_trace.md](C1370_category_pipeline_trace.md) |

**Phase 483 findings (Category Pipeline Trace):**
- Pipeline is WEAKLY_RESHAPED: same vocabulary, different frequency emphasis (JS A↔B=0.026)
- B amplifies execution categories (THERMAL +72%, OPERATION +58%), attenuates specification (STAGING -47%, MONITORING -73%)
- AZC is intermediate and closer to A; TRANSITION peaks in AZC (28.7%)
- BIO = maximum THERMAL amplification (2.03x); HERBAL = THERMAL-neutral (0.98x), amplifies CONTAINMENT instead
- Dark pipeline 3x more categorically stable than bridge (JS 0.009 vs 0.026)
- Per-MIDDLE rank rho=0.644; "edy" (OPERATION) is top gainer, "hy" (MONITORING) is top loser

### Position-Conditioned Category Grammar (C1371) -- Phase: POSITION_CONDITIONED_CATEGORY_GRAMMAR (Phase 484)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| **1371** | **Position-Conditioned Category Grammar** (Category transitions position-conditioned chi² p=4.5e-65 V=0.102; Q5 most deviant JS=0.016; THERMAL self-loops erode Q1→Q5 32.4%→19.1%; FLOW monotonic gradient rho=0.900 p=0.037; section-position additive confirming C1047; 5/8 self-transition rates vary; 4/6 predictions confirmed) | 2 | B, line, category, positional, transition | -> [C1371_position_conditioned_category_grammar.md](C1371_position_conditioned_category_grammar.md) |

**Phase 484 findings (Position-Conditioned Category Grammar):**
- Category transitions ARE position-conditioned (chi² p=4.5e-65, V=0.102)
- Line-final (Q5) is the most distinctive position — THERMAL drops, FLOW/TRANSITION spike
- THERMAL self-loop erosion: 32.4% (Q1) → 19.1% (Q5) — thermal bursts decay across line
- FLOW is the only significant monotonic gradient (rho=0.900, p=0.037, increasing toward line end)
- Section-position interaction absent (mean profile corr=0.617) — C1047 extends to categories
- "Thermal arc": heat loads at front, disperses through middle, resolves to flow/transition at end

### Thermodynamic Arc Validation (C1372) -- Phase: THERMODYNAMIC_ARC_VALIDATION (Phase 485)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| **1372** | **Thermodynamic Arc Validation** (First-principles thermodynamic ordering model FAILS 0/7 tests; rho=0.286 p=0.493; 2/8 shapes correct; MSE 2.8x worse than uniform null; 6/7 directional predictions confirmed but partially circular; PREFIX confound COLLAPSES signal; CONTAINMENT is LATE not early; category gradient mediated by PREFIX positional grammar C1001) | 2 | B, line, category, positional, interpretation, PREFIX | -> [C1372_thermodynamic_arc_validation.md](C1372_thermodynamic_arc_validation.md) |

**Phase 485 findings (Thermodynamic Arc Validation):**
- Thermodynamic ordering model (STAGING < MARKING < CONTAINMENT < THERMAL < ... < TRANSITION) fails all 7 formal tests
- Directional predictions 6/7 confirmed but 3/6 are circular with C1371 known findings
- T3 GATE CLOSED: thermodynamic model 2.8x WORSE than uniform null at predicting shapes
- CONTAINMENT is the LATEST category (COM=2.235), not early as predicted — reframes as "collection" not "preparation"
- PREFIX confound control: signal COLLAPSES after controlling for PREFIX positional grammar (C1001)
- Constrains Tier 3 distillation interpretation: process ordering does not independently predict category position

### PREFIX Category-Position Decomposition (C1373) -- Phase: PREFIX_CATEGORY_POSITION_DECOMPOSITION (Phase 486)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| **1373** | **PREFIX Category-Position Decomposition** (Thermal arc NOT a PREFIX artifact; ch chi²=75.9 p=3e-6 THERMAL rho=-0.900; sh chi²=61.2 p=3e-4 rho=-0.800; 11/27 PREFIXes |rho|>0.50; weighted avg rho=-0.720; removing specialists STRENGTHENS gradient; qo creates Q2 bump; BARE anchors Q5 THERMAL depletion; H3 compositional artifact FALSIFIED; C1372 amendment) | 2 | B, PREFIX, line, category, positional, sister pair | -> [C1373_prefix_category_position_decomposition.md](C1373_prefix_category_position_decomposition.md) |

**Phase 486 findings (PREFIX Category-Position Decomposition):**
- **H3 FALSIFIED**: Thermal arc exists WITHIN individual PREFIXes, not just between them
- ch and sh both show significant within-PREFIX category-position gradients (THERMAL declines Q1→Q5)
- Removing positional specialists (5.7% of tokens) STRENGTHENS the gradient (rho -0.400 → -0.900)
- qo (59% THERMAL, peaks Q2) creates non-monotonic Q2 bump; removing qo yields monotonic decline
- BARE tokens anchor Q5: concentrate at line-final (rho=1.000), near-zero THERMAL, high FLOW
- ok/ot contribute +3.3pp FLOW+TRANSITION at Q5 (line-final resolution specialists)
- **C1372 amendment**: PREFIX confound control was too aggressive; within-PREFIX gradient is genuine
- Verdict: H1+H2 HYBRID — gradient from major PREFIXes covering >85% of tokens

### Within-PREFIX MIDDLE Positional Selection (C1374) -- Phase: WITHIN_PREFIX_MIDDLE_POSITION (Phase 487)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| **1374** | **Within-PREFIX MIDDLE Positional Selection** (MIDDLE selection changes by position within every PREFIX 7/7 p<0.001; within ch top 2 MIDDLEs eey+eol explain 100% THERMAL decline; position specialists are PREFIX-generalists breadth 15.3 vs 8.3 p=0.0004; BARE equal positional selection JSD rank 14/27; ch/sh parallel moderate rho=0.468; QO/CHSH lane orthogonal to position; gradient is MIDDLE-level property not PREFIX-level) | 2 | B, PREFIX, MIDDLE, line, positional, category, sister pair | -> [C1374_within_prefix_middle_position.md](C1374_within_prefix_middle_position.md) |

**Phase 487 findings (Within-PREFIX MIDDLE Positional Selection):**
- MIDDLE distributions change by line position within EVERY major PREFIX (7/7 significant)
- Within ch: just 2 MIDDLEs (eey + eol, both THERMAL) explain 100% of the THERMAL decline
- Position specialists are PREFIX-generalists (appear under 15.3 PREFIXes vs 8.3 for flat MIDDLEs)
- BARE shows equal positional MIDDLE selection — position is independent of PREFIX routing
- sh has 9 EARLY specialists, ot/ok/BARE have late specialists — matches thermal arc direction
- ch/sh parallel gradient moderate (rho=0.468, p=0.007) — shared direction but different magnitudes
- QO lane vs CHSH lane partition does NOT predict positional behavior (p=0.120)
- Thermal arc is a MIDDLE-level positional grammar property, not PREFIX-level

### Hebrew Cipher Cross-Validation (C1375) -- Phase: HEBREW_CIPHER_CROSS_VALIDATION (Phase 488)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| **1375** | **Hebrew Cipher Cross-Validation** (Gatta Hebrew cipher decode INCREASES entropy +0.218 bits DECREASES MI -0.755 bits opposite of decipherment; 0/8 categories show Hebrew coherence ratio=0.991; 1/35 PREFIXes match Hebrew morpheme; T2 class clustering z=-15.5 is morphological confound; 3/7 control program 1/7 cipher 3/7 ambiguous = STRONG FALSIFICATION at grammar layer) | 2 | B, cross-validation, external, cipher, Hebrew, information theory | -> [C1375_hebrew_cipher_cross_validation.md](C1375_hebrew_cipher_cross_validation.md) |

**Phase 488 findings (Hebrew Cipher Cross-Validation):**
- Gatta (voynich-toolkit) proposes EVA→Hebrew consonantal, RTL, with context-sensitive mapping
- Their decode INCREASES character bigram entropy (+0.218 bits) — opposite of correct decipherment
- Their decode DECREASES token MI (-0.755 bits) — destroys structural signal, consistent with C130
- Our 8 operational categories show ZERO Hebrew-space coherence (C171 semantic ceiling holds)
- Only 1/35 PREFIXes (ch→kaf=ke-) exactly matches a Hebrew morpheme
- T2 within-class clustering (z=-15.5) is a confound: EVA morphological similarity survives any char transform
- Verdict: STRONG FALSIFICATION of cipher at grammar layer; Gatta's patterns may exist below grammar level

### EVA Character-Level Asymmetry Decomposition (C1376) -- Phase: EVA_CHAR_ASYMMETRY_DECOMPOSITION (Phase 489)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| **1376** | **Character-Level RTL Signal Is Grammar-Internal** (within-token RTL z=36.8 replicated; MIDDLE slot syntax INITIAL→MEDIAL→TERMINAL fully explains signal; slot-preserving shuffle preserves 102% of asymmetry z=-2.6; coarse 4-category explains 48.9% fine-grained slot structure explains rest; kernel opposes main gradient -10.3%; gallows reduce asymmetry -35.7%; no encoding design feature beyond C1209 grammar) | 2 | B, directionality, character-level, slot syntax, external, grammar | -> [C1376_char_level_rtl_is_grammar.md](C1376_char_level_rtl_is_grammar.md) |

**Phase 489 findings (EVA Character-Level Asymmetry Decomposition):**
- Gatta's character-level RTL finding REPLICATED at z=36.8 (within-token bigram conditional entropy)
- Signal is FULLY EXPLAINED by C1209's INITIAL→MEDIAL→TERMINAL slot syntax
- Slot-preserving shuffle preserves the asymmetry (z=-2.6 from observed); random shuffle destroys it (z=79.8)
- Reconciles C1117 (LTR at token level) with RTL at character level: different structural layers
- Kernel transitions (C521) actually OPPOSE the RTL gradient (-10.3%), creating LTR bias for kernel pairs
- No Phase 490 needed: no residual signal beyond grammar

### Puff-Voynich Structural Revisit (C1377) -- Phase: PUFF_VOYNICH_STRUCTURAL_REVISIT (Phase 490)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| **1377** | **Puff-Voynich Structural Revisit (NULL)** (21 folios, 3 material types, category pseudo-F=0.90 p=0.51, apparatus pseudo-F=1.62 p=0.15; ceiling confirmed with modern tools) | 2 | B, Puff, material type, category, apparatus, NULL, ceiling | -> [C1377_puff_structural_revisit_null.md](C1377_puff_structural_revisit_null.md) |

**Phase 490 findings (Puff-Voynich Structural Revisit):**
- Revisits early Puff connection (v2.20-2.62) with 8-category profiles and 5-apparatus profiles
- 21 Currier B herbal folios classified by PPC blind morphology (8 ROOT, 7 FLOWER, 6 HERB)
- Pre-registered assignments, permutation-based p-values (10,000), Bonferroni p<0.0033
- Test D (8 categories): pseudo-F=0.90, eta²=0.091, p=0.51 — ROOT/FLOWER/HERB indistinguishable
- Test A (5 apparatus): pseudo-F=1.62, eta²=0.153, p=0.15 — no material-type differentiation
- Test B (Puff→Brunschwig→REGIME triangulation): SKIPPED (requires D+A signal)
- Early evidential ceiling CONFIRMED: Puff connection is not structurally diagnostic at folio level

### Paragraph-Level Material Differentiation (C1378) -- Phase: PARAGRAPH_MATERIAL_DIFFERENTIATION (Phase 492)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| **1378** | **Paragraph-Level Material Differentiation (NULL)** (72 folios, dark-pipeline Jaccard within=0.972 between=0.963 ratio=1.009x p=0.98; header diversity PASS p=0.0001 ratio=1.11x; semantic ceiling extends to paragraph granularity) | 2 | B, paragraph, material, dark-pipeline, MIDDLE, NULL, header, ceiling | -> [C1378_paragraph_material_differentiation_null.md](C1378_paragraph_material_differentiation_null.md) |

**Phase 492 findings (Paragraph-Level Material Differentiation):**
- Tests whether paragraphs within a folio encode different plant materials (Brunschwig multi-material batch processing)
- T1 (All MIDDLEs): NULL, within-folio paragraphs MORE similar (0.786 vs 0.719, p=0.997)
- T2 (Dark-pipeline KEY TEST): NULL, near-identical within vs between (0.972 vs 0.963, p=0.980)
- T3 (Bridge control): PASS — bridge vocabulary is folio-coherent as expected
- T4 (Header vs body): PASS p=0.0001 — headers 1.11x more diverse than bodies (new finding)
- T5 (Paragraph counts): Exploratory, section-driven (H=4.2, S=12.5)
- Semantic ceiling (C171) confirmed at paragraph granularity; material identity irrecoverable

### Two-Level Parallel Composition (C1379) -- Phase: PARALLEL_MONITORING_TRACKS (Phase 494)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| **1379** | **Two-Level Parallel Composition with Priority Ordering** (macro-atom r=0.797 vs individual r=0.760, z=5.98 p<0.001; 9 fused pairs from C1210; atom removal ratio 1.375 <1.5 PASS but initial dominates Kruskal p=0.004; reversed/different JSD ratio 0.904 rejects pure parallelism; T→I MI=0.079 > SET MI=0.025; T5 channel separation: ke/ct/ck 1.9-2.9x Mode A enriched, in 0.54x Mode B, thermal p=0.0000; macro-atoms have functional channel assignments) | 2 | B, MIDDLE, composition, macro-atom, parallel, priority, channel, suffix-mode, C1190, C1210, C1229 | -> [C1379_two_level_parallel_composition.md](C1379_two_level_parallel_composition.md) |

**Phase 494 findings (Parallel Monitoring Tracks):**
- T1 (KEY TEST): Macro-atom decomposition using C1210 high-affinity pairs improves C1190's behavioral composition from r=0.760 to r=0.797 (z=5.98, p<0.001 vs 1000 random pairings)
- T2: Reversed MIDDLE pairs (same atoms, different order) are NOT significantly more similar than different-set pairs (ratio 0.904, p=0.146) — atom ORDER matters, pure parallelism rejected
- T3: Cross-token coupling flows through TERMINAL→INITIAL (MI=0.079) not full SET (MI=0.025); INITIAL→INITIAL at 75% of T→I shows entry state persistence
- T4: All positions contribute (removal ratio 1.375 < 1.5) but INITIAL dominates (Kruskal p=0.004); medial drops first — consistent with expert-oriented elision
- T5 (EXTENSION): Macro-atoms split by suffix mode channel — ke (2.68x), ct (2.87x), ck (1.91x) concentrate in Mode A (thermal specification); in (0.54x) concentrates in Mode B (continuation). qo PREFIX 1.91x Mode A enriched (p=0.0000). Macro-atoms have functional channel assignments.
- Refined model: two-channel parallel composition with priority ordering — fused macro-atoms serve different instruction streams (specification vs continuation)

### Apparatus Parameterization in AXM Residual (C1380) -- Phase: PARALLEL_MONITORING_TRACKS (Phase 494)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| **1380** | **Apparatus Profile Partially Explains AXM Residual** (Mantel r=0.224 p=0.002 5K perms; eta²=0.083 p=0.034; raw r=0.243 p=0.0002; SEALED_VESSEL +0.022 most repetitive, SUSTAINED_HEAT -0.018 most varied; ~8% of C1169 residual is apparatus parameterization, ~92% remains free) | 2 | B, AXM, residual, apparatus, design-freedom, Mantel, C1169, C1248 | -> [C1380_apparatus_parameterization_in_residual.md](C1380_apparatus_parameterization_in_residual.md) |

**Phase 494 findings (Apparatus Parameterization):**
- Pairwise apparatus profile similarity predicts AXM residual similarity (Mantel r=0.224, p=0.002)
- Dominant apparatus group clusters in residual space (eta²=0.083, p=0.034)
- Sealed-vessel folios are more self-repetitive (+0.022), distillation/sustained-heat more varied (-0.011/-0.018)
- C1169 missed this because it tested univariate regression, not pairwise similarity
- Qualifies C1169: ~8% of "design freedom" is actually apparatus input parameterization

---

### o-Initial MIDDLE AZC Enrichment (C1381) -- Phase: GLOSS_PREDICTION_TESTS (Phase 495)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| **1381** | **o-Initial MIDDLE Enrichment in AZC** (AZC 22.4% vs B 11.8%, ratio=1.9x, chi2=281.3 p<0.0001; B-shared 13.5% vs B-exclusive 9.8%; Section C highest at 18.9%; smooth gradient from apparatus layer into execution layer) | 2 | CROSS, AZC, MIDDLE, atom, o-initial, apparatus, C496, C1269, C1273, C1274 | -> [C1381_o_initial_middle_azc_enrichment.md](C1381_o_initial_middle_azc_enrichment.md) |

**Phase 495 findings (Gloss Prediction Tests):**
- Crazy-expert proposed 8 testable predictions from Tier 4 gloss analysis; 5 already confirmed by existing constraints, 3 tested here
- P6 (n-terminal at mode boundaries): INVERTED — n-terminal MIDDLEs depleted at transitions (0.81x, p<0.0001), consistent with n as steady-state marker
- P7 (o-initial in AZC): CONFIRMED — 1.9x enrichment with smooth gradient (new constraint C1381)
- P8 (f-atoms in REGIME_3): WRONG DIRECTION — f peaks in REGIME_4/REGIME_2, not REGIME_3; distribution is non-uniform (chi2=90.6) but prediction target was wrong
- Crazy-expert overall: 6/8 confirmed, 1 inverted, 1 wrong direction

### k/a Atom-Initial Suffix Mode Polarization (C1382) -- Phase: GLOSS_PREDICTION_TESTS (Phase 495)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| **1382** | **k/a Atom-Initial Suffix Mode Polarization** (k-initial 0.583x depleted in Mode B vs Mode A, chi2=245 p<0.0001, all 5 sections consistent; a-initial 2.034x Mode B enriched; e-initial neutral 0.986x; atom-initial predicts suffix mode along same axis as C1309 THERMAL/TRANSITION) | 2 | B, MIDDLE, atom, suffix-mode, k-initial, a-initial, C1229, C1309, C908, C1381 | -> [C1382_k_a_atom_suffix_mode_polarization.md](C1382_k_a_atom_suffix_mode_polarization.md) |

**Phase 495 findings (Gloss Prediction Tests, batch 2: P9-P11):**
- P9 (n-terminal at line-final): INVERTED — n-terminal MIDDLEs depleted at line-final (0.694x, p=0.000005); second n-terminal inversion confirms n as steady-state mid-line atom
- P10 (k-initial in Mode B): CONFIRMED — 0.583x depleted, all sections consistent; a-initial shows symmetric opposite (2.034x Mode B); new constraint C1382
- P11 (bridge simpler than dark): MIXED — raw depth not significant (p=0.24) but frequency-matched depth significant (0.754x, p=0.000009) and character length strongly confirms (0.682x)
- Crazy-expert cumulative: 7/11 confirmed, 2 inverted, 1 wrong direction, 1 mixed

### n-Terminal MIDDLE Boundary Avoidance (C1383) -- Phase: GLOSS_PREDICTION_TESTS (Phase 495)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| **1383** | **n-Terminal MIDDLE Boundary Avoidance** (depleted at mode transitions 0.81x p<0.0001; depleted at line-final 0.694x p=0.000005; 4/5 sections consistent; mean position 0.479 vs 0.502; n is interior/steady-state, avoids all tested boundary types) | 2 | B, MIDDLE, atom, n-terminal, boundary, position, mode, C1208, C1209, C1210, C1382 | -> [C1383_n_terminal_boundary_avoidance.md](C1383_n_terminal_boundary_avoidance.md) |

**C1383 rationale:** Two independent predictions (P6, P9) that n-terminal MIDDLEs would be enriched at boundaries both inverted significantly. The consistent direction (depletion, not enrichment) establishes n as a steady-state interior atom. Documented to prevent future boundary-role predictions for n.

### k-Initial MIDDLE Fraction Predicts AXM Dwell (C1384) -- Phase: GLOSS_PREDICTION_TESTS (Phase 495)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| **1384** | **k-Initial MIDDLE Fraction Predicts AXM Self-Transition** (rho=+0.620 p<0.0001 72 folios; k is ONLY positive atom-initial; a=-0.503 o=-0.427 d=-0.411 all negative; survives within-section B rho=+0.496 H rho=+0.407; four-level chain: k-initial → Mode A → THERMAL → AXM dwell) | 2 | B, MIDDLE, atom, k-initial, AXM, dwell, folio, C1382, C1289, C1309, C1208 | -> [C1384_k_initial_axm_dwell_correlation.md](C1384_k_initial_axm_dwell_correlation.md) |

**Phase 495 findings (Gloss Prediction Tests, batch 3: P12-P14):**
- P12 (h-terminal CHSH enrichment): INVERTED — h-terminal depleted in CHSH (0.767x, p=0.0002); complementary distribution, not resonance
- P13 (e/k vs AXM): HALF CONFIRMED — k-initial rho=+0.620 confirmed; e-initial inverted (rho=+0.350, positive not negative); true axis is k vs {a,o,d}, not k vs e; new constraint C1384
- P14 (y-terminal paragraph-final): NULL — 0.950x, p=0.14, dead flat
- Crazy-expert cumulative: 8/14 confirmed, 3 inverted, 1 wrong direction, 1 mixed, 1 null

### l-Terminal State/Condition Marker (C1385) -- Phase: L_ATOM_SEMANTIC_DEEP_DIVE (Phase 496)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| **1385** | **l-Terminal State/Condition Marker** (68.9% post-state-change rate vs 47.2% baseline; 77% kernel-before-l ordering on mixed lines; kernel contact rho=-0.197 p<0.000001; Mode B locked 72%; category redirection 0/5 match; STAGING 9.7x; 450 CHSH+l compositional tokens; 15-round investigation, 10 hypotheses falsified; upgrades l from WEAK to SOLID; German: Lage) | 2 | B, MIDDLE, atom, l-terminal, state, gloss, C1195, C1207, C1209, C1250, C1386 | -> [C1385_l_terminal_state_condition_marker.md](C1385_l_terminal_state_condition_marker.md) |

### ACTOR/RESPONDER Terminal-Atom Timing Split (C1386) -- Phase: L_ATOM_SEMANTIC_DEEP_DIVE (Phase 496)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| **1386** | **ACTOR/RESPONDER Terminal-Atom Timing Split** (terminal atoms partition by macro-state transition timing: ACTORS {e=18.4%, h=29.1%, k=31.8%, t=30.4%} precede changes; NEUTRAL {d=38.3%, o=42.4%, y=43.9%, i=48.7%}; RESPONDERS {n=63.6%, l=68.9%, r=72.6%, m=78.2%} follow changes; baseline 47.2%; orthogonal to C1208 carryover and C1209 positional grammar) | 2 | B, MIDDLE, atom, timing, macro-state, transition, C1200, C1209, C1208, C976 | -> [C1386_actor_responder_timing_split.md](C1386_actor_responder_timing_split.md) |

**Phase 496 findings (L-Atom Semantic Deep Dive):**
- 15-round hypothesis-test investigation of atom l using crazy-expert agent
- 10 hypotheses tested and falsified: let-flow, release, arrange, level, specifier, redirect, continue, nominalizer, hold, free, product
- Final interpretation: l = "state/condition marker" (SOLID confidence) — converts operations to status readings
- Key evidence: 68.9% post-state-change (21.7pp above baseline), 77% kernel-before-l, kernel avoidance rho=-0.197, Mode B locked
- ACTOR/RESPONDER timing split discovered as independent structural finding (C1386)
- CHSH + l compositional reading confirmed: ch+ol = "checkpoint the vessel-state" (450 tokens)
- C1195 updated: l upgraded from WEAK ("frame") to SOLID ("state")

### r-Terminal Hazard-Response Partitioning (C1387) -- Phase: R_ATOM_SEMANTIC_DEEP_DIVE (Phase 497)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| **1387** | **r-Terminal Hazard-Response Partitioning** (ar monopolizes FL_HAZ 248:0 vs or, 4.910x enrichment chi-sq=1473.71; or concentrates in FQ 70.5%; only r/l/n at FL_HAZ = RESPONDER-exclusive; r anti-cycling rho=-0.334 p=0.003; r→a forward chain 2.142x; r exists only as ar and or; 10-round investigation, 4 hypotheses falsified; upgrades r from WEAK to PLAUSIBLE; gloss: respond) | 2 | B, MIDDLE, atom, r-terminal, FL_HAZ, macro-state, hazard, respond, C1195, C1207, C1208, C1386, C976 | -> [C1387_r_terminal_hazard_response_partitioning.md](C1387_r_terminal_hazard_response_partitioning.md) |

**Phase 497 findings (R-Atom Semantic Deep Dive):**
- 10-round hypothesis-test investigation of atom r using crazy-expert agent
- 4 hypotheses tested: return/reflux (Rücklauf), flow/run (rinnen), ripen/mature (reifen), repeat (repetieren) — all falsified or partially falsified
- 0 fully confirmed predictions across 10 tests (vs l-atom Phase 496: 15 tests, multiple confirmations)
- Key structural discovery: r exists ONLY as "ar" and "or" (extreme compound selectivity)
- ar monopolizes FL_HAZ (248 tokens, zero or) at 4.910x enrichment (chi-sq=1473.71)
- Only RESPONDER atoms {r, l, n} appear at FL_HAZ — consistent with C1386
- r anti-cycling: rho=-0.334, p=0.003 (more r = less mode alternation)
- r→a forward chain at 2.142x (strongest sequential dependency in iteration axis)
- Final interpretation: r = "respond" (PLAUSIBLE confidence)
- PLAUSIBLE ceiling: a/o initial confound prevents full isolation of r's contribution
- C1195 updated: r upgraded from WEAK ("input") to PLAUSIBLE ("respond"); tier counts 8/3/7/1

### o-Atom Arrangement Domain Marker (C1388) -- Phase: O_ATOM_SEMANTIC_DEEP_DIVE (Phase 498)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| **1388** | **o-Atom Arrangement Domain Marker** (o=arrange/ordnen; STAGING 2.49x OPERATION 1.78x THERMAL 0.105x depleted; #1 anti-AXM (rho=-0.614) #1 kernel interleaver (52.1%); C874 convergence — ol=LINK from structural analysis independently confirmed by o(arrange)+l(state) = 100% STAGING 7.68x; 100% compound determinism ol=STAGING ok=CONTAINMENT or=FLOW ot=MONITORING; temporal ordering falsified (48.6% chance) — domain marker not sequential verb; 23-test battery 8/23 confirmed; upgrades o from WEAK to SOLID; German: ordnen) | 2 | B, MIDDLE, atom, o-initial, o-terminal, arrange, ordnen, STAGING, OPERATION, anti-AXM, interleaving, domain-marker, C874, C1195, C1207, C1381, C1384, C1386, C1190, C1305 | -> [C1388_o_atom_apparatus_management_profile.md](C1388_o_atom_apparatus_management_profile.md) |

**Phase 498 findings (O-Atom Semantic Deep Dive):**
- 23-test investigation across three batteries: vessel/Ofen (12 tests, 3 pass), ordnen/arrange (8 tests, 4 pass), tiebreakers (3 tests, 1 pass)
- Vessel/CONTAINMENT prediction falsified (CONTAINMENT 0.835x) — actual categories: STAGING 2.49x, OPERATION 1.78x
- Ordnen/arrange hypothesis confirmed through convergent evidence:
  - C874 convergence: ol independently established as LINK operator from structural analysis; compositional decomposition independently yields o(arrange)+l(state) = 100% STAGING (7.68x). Two methods, zero shared assumptions, same conclusion.
  - 100% compound determinism: ol=STAGING (762 tokens), ok=CONTAINMENT (70), or=FLOW (446), ot=MONITORING (46). Contrast: al=FLOW vs ol=STAGING — same l, different first atom → proves o carries independent semantic content.
  - Anti-THERMAL 0.105x (most extreme single-category depletion of any atom)
  - Anti-AXM #1 of all 20 atoms; kernel interleaver #1 among NEUTRAL atoms
  - CHSH+o STAGING 4.77x (strongest category signal in CHSH compounds)
- Temporal ordering falsified: o does NOT precede k within lines (48.6%, chance). o is a domain marker, not a sequential action verb.
- German candidate: ordnen (to arrange), consistent with K=Kochen, E=Erkalten, D=Dichten, T=Treiben pattern
- C1195 updated: o upgraded from WEAK ("work") to SOLID ("arrange"); tier counts now 8/4/7/0 (zero WEAK atoms remaining)

### c-Atom Main-Loop Modifier Profile (C1389) -- Phase: C_ATOM_SEMANTIC_DEEP_DIVE (Phase 499)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1389 | c-atom main-loop modifier profile | 2 | B | c=adjust upgraded PLAUSIBLE->SOLID; 6/6 compositional convergence, 93.5% AXM-confined, MONITORING 12.237x, 100% compound determinism across 61 c-MIDDLEs, CHSH+c MONITORING 23.09x, order-sensitive (ck=OPERATION vs kc=CONTAINMENT) |

**Phase 499 findings (C-Atom Semantic Deep Dive):**
- 19-test investigation across three batteries: initial cross-token (4/12), compound decomposition (2/4), tiebreakers (2/3) = 8/19 total
- Category identity confirmed: MONITORING 12.237x (#1 enriched), MARKING 2.916x, anti-THERMAL 0.055x (near-zero)
- c is 93.5% AXM — most macro-state-confined atom in the system. Zero FL_HAZ, FQ, CC
- 100% compound determinism: ck=OPERATION (197 tokens), ckh=CONTAINMENT (127), ct=MONITORING (95), cth=MARKING (49), cph=MONITORING (36), cfh=MARKING (9)
- CHSH+c: MONITORING 23.09x enrichment — most extreme PREFIX+atom signal observed. MARKING 6.02x
- Key discovery: c->h obligatory junction (C1216: 380/380) is INTRA-token (compound formation), NOT cross-token (0 c-terminal->h-initial instances). The {c,h} cluster reflects compound co-occurrence, not sequential execution
- **Decisive evidence (Phase 499b/c):** 6/6 compositional convergence — every independently glossed c-compound matches CategoryClassifier when decomposed through c(adjust)+X. MON+MARK injection +43.2pp (5/5 bases). Order sensitivity: ck=OPERATION vs kc=CONTAINMENT (100% category flips). h-suffix category transformation (p<0.000001). Folio coverage exceeds all controls
- ACTOR timing: 31.6% post-state-change (proactive, not reactive). "Correct" hypothesis falsified (0/2)
- German candidate: justieren (to adjust/calibrate)
- C1195 updated: c upgraded from PLAUSIBLE ("adjust") to SOLID ("adjust"); tier counts now 8/5/6/0

### p-Atom Marking Pause Profile (C1390) -- Phase: P_ATOM_SEMANTIC_DEEP_DIVE (Phase 500)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1390 | p-atom marking pause profile | 2 | B | p=pause upgraded PLAUSIBLE->SOLID; #1 MARKING atom (12.033x, 93.63%), #1 carryover (8.126x), 3/4 compositional convergence, 4/4 MARKING injection +68.3pp, op gateway 95.5% INITIAL/TRANSITION, CHSH+p MON+MARK 87.4%, AXM 88.7%, line-boundary reset; 12-test battery 10/12 |

**Phase 500 findings (P-Atom Semantic Deep Dive):**
- 12-test investigation scored 10/12 (Cycle 1: 4/4, Cycle 2: 3/4, Cycle 3: 3/4)
- p is the #1 MARKING atom in the entire system: 12.033x enrichment, 93.63% of all p-initial tokens classify as MARKING
- p is the #1 carryover atom: 8.126x consecutive pair enrichment, ZERO cross-line pairs (line-boundary reset)
- AXM 88.7% (enriched 1.311x), FL_HAZ 0.000x — main-loop, not hazard-associated. Less confined than c (93.5%)
- Compositional convergence 3/4: op=TRANSITION (match), cph=MONITORING (match), cp=MARKING (match); ep=MARKING (miss, expected THERMAL — p dominates e)
- MARKING injection: +68.3pp across all 4 testable bases (universal, strongest single-category injection of any atom)
- op gateway compound: 95.5% INITIAL (210/220), 100% TRANSITION, 63 folios (76.8% corpus). Process restart/transition point
- CHSH+p: MON+MARK 87.4%, MARKING 11.86x — higher than CHSH+c's known extreme signal
- p->c junction: 11.02x intra-compound (306 tokens), cross-token depleted 0.78x — same intra-compound pattern as c->h
- cp and pc both 100% MARKING — p's dominance prevents order sensitivity (unique behavior among tested atoms)
- ACTOR timing: 26.7% (proactive, not reactive). Post-hazard depleted (0.56x)
- Section gradient: MARKING rho=+0.657, but best tracker is FLOW rho=+0.714 (minor miss)
- German candidate: pausieren. Consistent with REGIME 2: "seal->heat->PAUSE->cool overnight->unseal->collect"
- C1195 updated: p upgraded from PLAUSIBLE ("pause") to SOLID ("pause"); tier counts now 8/6/5/0

### s-Atom Staging Sequence Profile (C1391) -- Phase: S_ATOM_SEMANTIC_DEEP_DIVE (Phase 501)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1391 | s-atom staging sequence profile | 2 | B | s=sequence remains PLAUSIBLE; #1 STAGING atom (6.721x, 87.50%), 6/6 compound determinism at 100% purity, FQ macro-state (3.59x), sh compound-suffix (13.16x s->h junction), modifier cosine 0.966 (SM-8); combined 11/20 across Phases 501+503 |

**Phase 501 findings (S-Atom Semantic Deep Dive, standard battery 6/12):**
- s is #1 STAGING atom: 6.721x enrichment, 87.50%, perfect compound determinism (6/6 at 100% purity)
- FQ macro-state (64.6%, 3.59x) — cycling, not AXM-confined; sh compound-suffix 13.16x junction
- Bifurcated: sh-family = MONITORING, non-h compounds = OPERATION/STAGING/MARKING
- H1 "sequence" best (3/4); H2 "sift" rejected (MONITORING 2.84% standalone)

**Phase 503 findings (S-Atom Modifier Battery, 5/8):**
- SM-8 (DECISIVE): s is PREDICTABLE modifier — cosine 0.966 across corpus halves (all 5 compounds >= 0.925)
- SM-2: s shifts partner category (4/5 Xs compounds change primary category, each 100% purity)
- SM-3: s-modifier PREFIXes amplify base selectivity (sa beats 2/3 a-base, sh beats ch)
- SM-4: s changes suffix distributions (sh-initial 100% bare, es chi2=822 p<0.001)
- SM-7: sh routes differently from ch (chi2=211.2, p~0, replicates C1243 at 1.74x)
- SM-1 (INFORMATIVE FAIL): h-junction not universal — tsh=FLOW, psh=MARKING override
- Combined 11/20 — below SOLID threshold. s is a predictable base-dependent sequencing modifier
- C1195 reviewed: s remains PLAUSIBLE ("sequence"); tier counts unchanged 8/6/5/0

### f-Atom Marking Flag Profile (C1392) -- Phase: F_ATOM_SEMANTIC_DEEP_DIVE (Phase 502)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1392 | f-atom marking flag profile | 2 | B | f=flag remains PLAUSIBLE; #2 MARKING atom (12.009x), 100% HT/UN (never enters 49-class grammar), 90.9% compound MARKING uniformity, f->c junction 10.28x, CHSH+f 82.8% MARKING, H1 'flag' 4/4 discriminants, 5/5 convergence; 12-test battery 6/12 (data ceiling) |

**Phase 502 findings (F-Atom Semantic Deep Dive):**
- 12-test investigation scored 6/12 (6 PASS, 4 FAIL, 1 INCONCLUSIVE, 1 N/A)
- f is the #2 MARKING atom in the system: 12.009x enrichment, behind only p (12.033x)
- KEY STRUCTURAL FINDING: f-initial vocabulary is 100% HT/UN — never enters 49-class execution grammar
- f is the purest identification/annotation atom: operates exclusively in the Human Track layer
- All f-compounds are uniformly MARKING (90.9%) — strongest compound uniformity of any tested atom
- f->c junction 10.28x enrichment: fch is a compound unit (like sh in s-atom)
- CHSH+f 82.8% MARKING (11.75x enrichment), comparable to CHSH+p's 87.4%
- H1 "flag" wins 4/4 discriminants: NEUTRAL timing 100%, R4 1.58x, pos 0.466, line-1 enrichment 7.00x (27.9%)
- 5/5 compositional convergence — no h-junction diversification (all compounds uniformly MARKING)
- Failures are data-driven: 215 total tokens, sparse compounds, no testable reversed forms
- f remains PLAUSIBLE — data ceiling prevents SOLID despite qualitatively strong evidence
- C1195 reviewed: f remains PLAUSIBLE ("flag"); tier counts unchanged 8/6/5/0

### Compound MIDDLE Composition Grammar (C1393) -- Phase: GLOSS_PREDICTION_TESTS (Phase 504)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1393 | compound MIDDLE composition grammar | 2 | B, grammar, composition | Head-initial three-slot grammar (V=0.593): HEAD (a,e,o) + MODIFIER (p,c,i,f,d,s) + TERMINAL (l,r,h,y,m,n) + FREE (k,t). First atom predicts category 74-76%. k/t role-dual: actor under qo, target under ch/sh. Replicates C1209 (15/19). Channel-specific slot modulation. |

**Phase 504 findings (Compound MIDDLE Composition Grammar, 6 tests):**
- T1: Head-initial structure — first atom determines category at 76.4%/74.2% (PREFIX/direct), token-weighted 85.9%/78.3%
- T2: Four-role partition — HEAD/MODIFIER/TERMINAL/FREE (chi2=30,868, V=0.593). a=86.4% first, n=99.4% last. Replicates C1209 independently (15/19 match)
- T3: k/t role duality — k-first=98.4% THERMAL (actor), k-last=88.3% MONITORING (target). JSD=0.717, HIGHER than HEAD atom e (0.593). FREE = positionally mobile with role duality
- T4: Terminal carry-over — within-line chi2=1144 p~10^-118 V=0.077 (real but weak). Across-line p=0.209 (resets at boundary, consistent with C1200/C1233). Strongest: r->a 1.98x
- T5: Action vs channel distinction — atom glosses predict intrinsic FUNCTION, PREFIX predicts deployment CHANNEL. Two independent readable layers
- T6: Channel-specific slot grammar — universal skeleton (y,n,m,h always terminal, head-initial 93.5%) + channel-specific assignment (k 90.5% FIRST under qo, 2.0% under ch; i exclusive to a-base channels; d enriched in monitoring)
- Composition reading rule: [HEAD=domain] + [MODIFIER(s)=how] + [TERMINAL=state], PREFIX = channel. k/t = process variable nouns
- Open questions: l-anomaly (shifts to INITIAL under some channels), modifier stacking order, 2-atom vs 3+ behavior

### Instruction Encoding Architecture (C1394) -- Phase: INSTRUCTION_ENCODING_MAP (Phase 505)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1394 | instruction encoding architecture | 2 | GLOBAL, grammar, composition | HEAD+MOD*+TERM with variable-length ordered modifier stack (p→f→i→c→d→s). Frame predicts 64% of category; modifiers shift 36%. Fusion gradient: only dy hard-fused, most "macro-atoms" are adjacent slots. Suffix confirmed independent layer (entropy 1.475 bits). Scope upgraded to GLOBAL by C1395 (Phase 507). |

**Phase 505 findings (Instruction Encoding Architecture, 7 tests):**
- T1: Suffix boundary — suffix is independent layer (77.1% of MIDDLEs take 3+ suffixes, entropy 1.475 bits), not an artifact of terminal atoms
- T2: Fusion gradient — dy is only hard-fused pair; ed/ol/op/ck/ch/in are soft-fused; ke/ee/od/ey are just adjacent slots
- T3: Pair-locked atoms — 9/18 atoms are pair-locked (<10% standalone): all 5 MOD atoms, HEAD a/o, TERMINAL n/h
- T4: Modifier ordering — fixed internal order p(0.22)→f(0.40)→i(0.52)→c(0.53)→d(0.70)→s(0.71); co-occurrence avoidance (c/i 0.40x, c/s 0.48x)
- T5: HEAD×TERM frame matrix — o→l 98.1% STAGING, a→r 99.4% FLOW, k→_ 69.1% THERMAL; HEAD+TERM predicts 64% of category
- T6: Modifier effects — d(V=0.657 +56% OPERATION), f(+76% MARKING, most concentrated), i(+45% TRANSITION), c(+30% MARKING), p(+46% MARKING), s(weakest)
- T7: Size distribution — 1-mod compounds are 47% of tokens (workhorses); 0-mod=24%; 2+=29%
- Instruction encoding model: PREFIX(channel) + HEAD(domain) + MOD*(ordered parametrization) + TERM(exit state) + SUFFIX(context marker)

**Phase 506 findings (Instruction Encoding Refinement, 4 tests resolving open questions):**
- T8: Headless compounds — specialized subgrammar (V=0.568), 20.6% of tokens, CONTAINMENT/MARKING/MONITORING enriched, a-base PREFIX concentrated (da 2213x), boundary-position enriched (paragraph-initial 2.16x)
- T9: h-terminal transparency — NOT chaotic; HEAD+MODS predict at V=0.988. h="watch" is transparent (lets HEAD signal through). PREFIX compensates +0.166 V
- T10: Modifier ordering — morphological convention (71% same category on reversal); first modifier dominates (66.5%); multi-stage stacking collapses to MARKING (97-100%); suffix mode coupling V=0.260
- T11: e-atom domain specificity — genuine domain, NOT default. o is real versatility champion (entropy 2.396). e-depth saturation: ee=84% THERMAL, eee=100%. e has LOWEST modifier dominance (V=0.672)

### Cross-System Instruction Encoding (C1395) -- Phase: INSTRUCTION_ENCODING_MAP (Phase 507)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1395 | cross-system instruction encoding | 2 | GLOBAL, grammar, composition | HEAD+MOD*+TERM architecture is manuscript-wide: A-exclusive MIDDLEs follow same slot grammar (Fisher p=0.90, pair-lock 84.2%, V=0.114). Bridge MIDDLEs 100% category stable (V=0.562). A enriched in state terminals (l 1.84x), B in action terminals (dy 144x). A records show positional grammar: o-HEAD leads, headless trails. |

**Phase 507 findings (Cross-System Instruction Encoding, 7 tests):**
- T1: A-exclusive slot grammar — 579 A-exclusive MIDDLEs follow same encoding (modifier ordering Fisher p=0.90, pair-lock 84.2% agreement, atom distribution V=0.114). VERDICT: SHARED_GRAMMAR
- T2: Headless HEAD recovery — REJECTED (cosine 0.220, accuracy 9.1% vs 25.2% baseline). Headless compounds are genuinely headless, not abbreviated
- T3: A record HEAD coherence — DOMAIN_COHERENT (z=-17.4, 7.7% entropy reduction). A records more coherent than B lines (7.7% vs 5.2%). o-HEAD leads (37.5% first), headless trails (55.5% last)
- T4: Cross-system HEAD stability — 100% category match for all 85 bridge MIDDLEs. HEAD×Category V=0.562. PREFIX wrapping tracks HEAD cross-system (cosine 0.675-0.998)
- T5: A-exclusive frames — only 2 A-exclusive frames (k+n, k+t); 17 B-only execution frames. dy cliff: 144x B-enriched. A=state descriptions (l 1.84x), B=action instructions (dy 14.4%)
- T6: A record → B folio prediction — statistically significant (z=+8.60) but practically flat (R²<5%). Near-saturation: each A record → ~81/82 B folios. Confirms C1136/C484 pool relationship
- T7: Situation description tests — P8 CONFIRMED (within-folio Jaccard 1.22x, z=+20.9), P10 CONFIRMED (positional grammar all p≈0), P6 PARTIAL (confounded by record length)

---

### Prep PREFIX Profiling (C1396) -- Phase: PREP_PREFIX_PROFILING (Phase 508)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1396 | prep PREFIX structural differentiation | 2 | B, PREFIX, prep, position, REGIME, suffix, atom | Prep PREFIXes share MIDDLE content (C1221) but differentiate on 7/8 non-content dimensions: position, paragraph, suffix, REGIME, section, context, vocabulary. pch=paragraph-opener (41.2%), dch=line-initial (71.2%), lch=sustainer (REGIME_1 70.5%, 81.3% bare, 0% par-initial). Atom glosses align: pch=stage-test, tch=transfer-test, dch=mark-test, lch=hold-test. Revises C1221 collapse to generic "process." |

**Phase 508 findings (Prep PREFIX Profiling, 8 tests):**
- T1: Line position — DIFFERENTIATED (9/10 KS pairs significant; dch 71.2% line-initial, lch mean 0.530)
- T2: Sequential context — DIFFERENTIATED (predecessor chi2=212.3, V=0.308, p=0.007)
- T3: Suffix patterns — DIFFERENTIATED (bare rates: pch 50.6%, lch 81.3%; chi2=183.4, V=0.202)
- T4: REGIME distribution — DIFFERENTIATED (lch 70.5% R1, pch/tch 40-44% R3; chi2=138.7, V=0.203)
- T5: MIDDLE vocabulary — PARTIAL (mean Jaccard 0.306; top MIDDLEs overlap but vocabulary sets only 31% shared)
- T6: Paragraph position — DIFFERENTIATED (pch 41.2% par-initial vs lch 0%; 8/10 KS pairs significant)
- T7: Section distribution — DIFFERENTIATED (lch 40% Section B; chi2=127.3, V=0.168)
- T8: Bare ch comparison — DIFFERENTIATED (27/35 dimension-prefix pairs significant; pch/tch diverge on all 7)

---

### Headless Compound Functional Grammar (C1397) -- Phase: HEADLESS_COMPOUND_GRAMMAR (Phase 509)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1397 | headless compound functional grammar | 2 | B, MIDDLE, headless, grammar, composition | Headless compounds (20.6%, 3,288 tokens) are NOT homogeneous infrastructure. Initial atom acts as pseudo-HEAD: d=CONTAINMENT 84%, p=MARKING 92%, f=MARKING 91%, i=STAGING 66%, r=FLOW 61%. V=0.503 category, V=0.459 PREFIX channels. Suffix bifurcation: d/i bare (85-93%) vs c/p/f suffixed (93-97%). da enrichment is i-initial specific, not generic headless. Same modifier ordering (61.9% vs 70.1%). q-initial (104 tokens) is non-grammar artifact. |

**Phase 509 findings (Headless Compound Grammar, 10 tests):**
- T1: Census — 467 types, 3,288 tokens. All 6 MOD atoms lead; 5/6 TERM atoms lead (n absent). MOD-initial 77.4%, TERM-initial 19.4%
- T2: Functional profiles — DIFFERENTIATED (chi2=5,601, V=0.503). d=84% CONTAINMENT, p=92% MARKING, f=91% MARKING, i=66% STAGING, r=61% FLOW, c=32% OPERATION (most diverse), l=28% STAGING (most versatile)
- T3: Positional — DIFFERENTIATED (23/45 KS pairs). r extreme line-final (44.3%), i line-initial (29.3%), c interior-locked (2.9% initial)
- T4: PREFIX channels — DIFFERENTIATED (chi2=6,199, V=0.459). i→da (54%), c→ch (53%), p→qo (71%), f→qo (61%), r→BARE (39%). da enrichment is i-initial specific
- T5: Suffix bifurcation — DIFFERENTIATED (chi2=3,645, V=0.352). d/i bare (85-93%), c/p/f suffixed (93-97%). Binary ops vs parametric ops
- T6: Length — headless 2.65 vs headed 2.76 chars (slightly shorter)
- T7: REGIME — MODERATE (V=0.157). l=65% R1, p=50% R3, s=34% R4
- T8: Modifier ordering — SAME_GRAMMAR (61.9% vs 70.1%). c atom is primary violator
- T9: HT association — q-initial only (100% HT). All other headless types 0.0-0.1% HT
- T10: Sequential context — embedded in normal sequences (54.3% preceded by headed, 16.9% headless→headless)

---

### Paragraph Operational Gradient (C1398) -- Phase: PARAGRAPH_PROGRAM_TYPING (Phase 510)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1398 | paragraph operational gradient | 2 | B, paragraph, clustering, section, REGIME | Paragraphs form a continuous operational variation space (silhouette 0.113), NOT discrete types. 4 gradient zones: THERMAL-QO (n=87, BIO/R1), CONTAINMENT-Sealing (n=68, HERBAL), OPERATION-Iteration (n=75, STARS_RECIPE/R3), MONITORING-Phase (n=34, STARS_RECIPE/R3). Section V=0.408, REGIME V=0.371. 50% of folios multi-type. Connects to C1378 (NULL material differentiation): same material, different operational emphases. |

**Phase 510 findings (Paragraph Program Typing, 8 tests):**
- T1: Clustering — CONTINUOUS (silhouette 0.113, best k=4, all k=2-8 below 0.25)
- T2: Zone interpretation — 4 gradient zones: THERMAL-QO (qo/k-kernel enriched), CONTAINMENT-Sealing (dy/headless_d enriched), OPERATION-Iteration (OPERATION/bare/headless_i enriched), MONITORING-Phase (h-kernel/MONITORING enriched)
- T3: Section — STRONG (chi2=131.9, V=0.408). BIO→Zone 0, HERBAL→Zone 1, STARS_RECIPE→Zones 2-3
- T4: REGIME — STRONG (chi2=108.8, V=0.371). R1→Zone 0, R3→Zones 2-3, R2→Zone 1
- T5: Folio composition — 50% multi-type (mean 1.68 zones/folio). Folios combine operational emphases
- T6: Feature importance — dy_frac (0.532) top discriminator, then h_kernel (0.442), MONITORING (0.428)
- T7: Stability — MODERATE (ARI=0.765, std=0.179). Real tendencies, fuzzy boundaries
- T8: Length — SIGNIFICANT (F=8.40, p<0.0001). Zone 0 longest (7.0 lines), Zone 3 shortest (3.9 lines)

---

### Paragraph Ordering Within Folios (C1399) -- Phase: PARAGRAPH_ORDERING_WITHIN_FOLIOS (Phase 511)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1399 | paragraph ordering null | 2 | B, paragraph, ordering, folio, sequence | Paragraphs have NO preferred ordering within folios. 7/8 tests FAIL for sequential structure. Transition matrix (T4) is structured (V=0.424) but reveals zone INERTIA (self-transition O/E=2.02), not sequence. THERMAL↔MONITORING mutual avoidance (O/E=0.12/0.20). No monotonic ramp (rho=-0.052). Section-controlled: all FAIL. Folio specifies WHAT concerns and HOW MUCH, not in WHAT ORDER. |

**Phase 511 findings (Paragraph Ordering, 8 tests):**
- T1: Zone ordinal position — FAIL (KW H=3.76, p=0.289, all zones at ~0.5)
- T2: First-paragraph zone — FAIL (chi2=2.63, p=0.452)
- T3: Last-paragraph zone — FAIL (p=0.470)
- T4: Transition matrix — PASS (chi2=99.1, V=0.424). Structure is INERTIA: self-transitions O/E=2.02
- T5: Bigram enrichment — Z3→Z3 O/E=3.01, Z1→Z1 O/E=2.75, Z0→Z0 O/E=1.96. THERMAL→MONITORING O/E=0.12 (most depleted)
- T6: Monotonicity — FAIL (rho=-0.052, p=0.611). No thermal→monitoring ramp
- T7: First-half vs second-half — FAIL (chi2=3.12, p=0.374). MONITORING 1.70x enriched in FIRST half (opposite of sequence)
- T8: Section-controlled — ALL FAIL (all p>0.17). Genuine absence, not section confound

---

### Paragraph State-Independent Ordering (C1400) -- Phase: PARAGRAPH_STATE_DEPENDENT_ORDERING (Phase 512)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1400 | paragraph state-independent ordering | 2 | B, paragraph, ordering, thermal, state | Terminal physical state does NOT predict next paragraph zone. 0/8 tests PASS after disambiguation. Raw thermal continuity (rho=+0.230) is entirely folio-level shared environment (shuffle p=0.565, adjacent≈non-adjacent p=0.690). Folio-residualized correlation flips to -0.161 (thermal anti-correlation). Folio-mode baseline (0.685) dominates all models. Combined state model DEGRADES prediction. |

**Phase 512 findings (State-Dependent Ordering, 8+4 tests):**
- T1-T4: Terminal kernel/category/cross-zone/thermal-gradient — ALL FAIL. No state feature predicts next zone
- T5: Raw thermal continuity rho=+0.230 — DISAMBIGUATED as shared environment (shuffle p=0.565, lag gradient flat, adjacent≈non-adjacent)
- T6: Tail product → next zone — FAIL (chi2=10.11, p=0.120)
- T7: Combined model — FAIL (0.484 vs zone-only 0.566, state HURTS)
- T8: Section-controlled — FAIL (state features DEGRADE within-section models)
- Disambiguation T2: Folio-residualized e_frac rho=-0.161 (p=0.029) — thermal anti-correlation within folio's thermal budget
- Folio-mode baseline (0.685) crushes all models. Paragraphs independently composed within folio's thematic envelope

---

### STATE-C Convergence Revisit (C1401-C1403) -- Phase: STATE_C_CONVERGENCE_REVISIT (Phase 513)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1401 | C325 completion gradient is section confound | 2 | B, convergence, section, position | Raw folio-position vs AXM rate (rho=+0.226, p=0.041) collapses to zero within every section (B: -0.012, H: +0.084, S: -0.008; all p>0.6). Gradient arises because section B (74.5% AXM) occupies later manuscript positions (section-position rho=+0.391). C325 QUALIFIED. |
| 1402 | no sequential convergence to AXM at any scale | 2 | B, convergence, paragraph, line, AXM | Neither cross-paragraph (rho=-0.019, p=0.78; 16 increasing/15 decreasing/14 flat) nor within-paragraph (rho=-0.016, Wilcoxon p=0.535) shows sequential convergence. Adjacent paragraph AXM rates uncorrelated (rho=0.001, perm p=0.983). Position-aware model 29.6% WORSE than folio-mean baseline. AXM dominance is thematic, not sequential. |
| 1403 | MONOSTATE is thematic dominance not sequential convergence | 2 | B, convergence, MONOSTATE, AXM, reframe | C084's MONOSTATE describes AXM as dominant operational mode (59-75% by section), not sequential convergence endpoint. Folio ICC=0.286 (71% paragraph-level variation). Reframes C074/C079/C084 without contradicting Tier 0 facts — statistical findings remain true, dynamical "convergence" interpretation replaced by static "thematic dominance". |

**Phase 513 findings (STATE-C Convergence Revisit, 7 tests):**
- T1: C325 completion gradient — SECTION_CONFOUND (within-section rho collapses to zero; section-position rho=+0.391)
- T2: Paragraph terminal AXM — MIXED (mean 65.3%; folio ICC=0.286, 71% paragraph-level variation)
- T3: Sequential convergence across paragraphs — FAIL (rho=-0.019, p=0.78; 16 up/15 down/14 flat)
- T4: Adjacent paragraph independence — CONFIRMED (rho=0.001, perm p=0.983)
- T5: Folio theme sufficiency — CONFIRMED (position-aware model 29.6% worse than folio mean)
- T6: Within-paragraph convergence — FAIL (rho=-0.016, Wilcoxon p=0.535; first/second half AXM identical)
- T7: Synthesis — FULL_REFRAME: "convergence to STATE-C" is AXM thematic dominance at section level, not sequential dynamics

---

### Section and Paragraph AXM Drivers (C1404-C1407) -- Phase: SECTION_PARAGRAPH_AXM_DRIVERS (Phase 514)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1404 | Section structural differentiation is REGIME-dominated | 2 | B, section, REGIME, macro-state, kernel, hazard, morphology | REGIME composition V=0.573, 7.4x next effect (macro-state V=0.077). Section B=100% R1. Transition entropy 3.09-4.47 bits. Sections are primarily REGIME mixtures with modest independent kernel/morphological effects. |
| 1405 | Paragraph AXM driven by PREFIX not section | 2 | B, paragraph, AXM, PREFIX, variance decomposition | PREFIX alone CV R2=0.736; section alone -0.027. Full model 0.760, section marginal +0.017. Top: qo_frac +0.576, bare_frac -0.515, chsh_frac +0.508. 24% residual = design freedom. Extends C1023 (PREFIX routing load-bearing) to paragraph level. |
| 1406 | Section is REGIME composition at paragraph level | 2 | B, section, REGIME, paragraph, PREFIX | Chain: section -> REGIME (V=0.573) -> PREFIX availability -> AXM (CV R2=0.736). Neither section (-0.027) nor REGIME (-0.092) has positive paragraph-level CV R2. Section adds zero beyond PREFIX. Sections are REGIME allocation policies. |
| 1407 | PREFIX-AXM relationship universal across sections | 2 | B, PREFIX, AXM, section, universality | 6/7 features show consistent sign across all sections. Only transition_frac inconsistent. Section modulates magnitude not direction. Extends C821 (syntax REGIME invariance) to paragraph-section interaction. |

**Phase 514 findings (Section and Paragraph AXM Drivers, 12 tests):**
- A1: Macro-state profiles — chi2=384.8, V=0.077; B highest AXM (74.4%), H highest FQ (24.0%)
- A2: Morphological signatures — B qo-dominated, T sh>ch inversion, mean PREFIX JSD=0.033
- A3: Kernel profiles — chi2=142.8, V=0.071; B k-enriched (24.2%), T h-enriched (9.7%)
- A4: Hazard profiles — B lowest FL_HAZ (4.4%, 0 violations); C/T highest (8.2%)
- A5: REGIME distribution — V=0.573 (dominant), B=100% R1, H diverse, T no R1
- A6: Transition entropy — T tightest (3.09 bits), S loosest (4.47 bits)
- B1: Morphological predictors — CV R2=0.747 (21 features); top: qo_frac +0.576
- B2: Paragraph length — weak (rho=+0.139, p=0.019)
- B3: PREFIX channel — qo +0.576, chsh +0.508, BARE -0.515
- B4: Kernel balance — k +0.432, e +0.273, h +0.173
- B5: Hazard density — FL_HAZ rho=-0.440 (survives length control)
- B6: Variance decomposition — PREFIX 0.736, section -0.027, full 0.760, section marginal +0.017
- C3: Interaction — 6/7 features sign-consistent across sections; PREFIX-AXM universal

---

### Suffix Atom Decomposition (C1408-C1410) -- Phase: SUFFIX_ATOM_DECOMPOSITION (Phase 515)

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1408 | suffix has HEAD→TERM compositional structure | 2 | B, suffix, atom, compositional, structure | 16-atom subset of MIDDLE inventory (missing k,t,p,f,c). Strong HEAD→TERM ordering: 76.6% HEAD-initial, 100% TERM-terminal, zero violations. First atom predicts category (V=0.277), last atom predicts position (R²=0.059). Parallels MIDDLE's HEAD→MOD→TERM at reduced scale. |
| 1409 | suffix atoms diverge from MIDDLE-terminal atoms | 2 | B, suffix, atom, MIDDLE, cross-position, divergence | 0/12 shared atoms maintain identical category profiles across suffix vs MIDDLE-terminal position. JSD range: h=0.004 (most stable) to m=0.560 (most divergent). Three tiers: near-stable (h,y,d), moderate shift (l,n,e,r,o,s), strong divergence (a,i,m). Same alphabet, position-dependent semantics. |
| 1410 | suffix modes are atom-level category partitions | 2 | B, suffix, atom, mode, paragraph, cycling | C1229's two modes decompose at atom level: Mode A (specification) = {d,e,ee,h,y} THERMAL/MONITORING atoms (1.68-2.38x enrichment). Mode B (continuation) = {a,i,ii,l,m,n,o,r,s} STAGING/TRANSITION/FLOW atoms. Near-equal balance (51.8%/48.2%). Not arbitrary clusters — operationally grounded atom partitions. |

**Phase 515 findings (Suffix Atom Decomposition, 9 tests):**
- T1: Inventory — 16 atoms, 35 suffix types, 11,151 suffixed tokens (48.3% of B)
- T2: Positional grammar — STRONG HEAD→TERM ordering (76.6% HEAD-initial, 100% TERM-terminal, zero violations)
- T3: Category — V=0.174; e/ee→THERMAL, h→MONITORING/CONTAINMENT, s→TRANSITION, o→STAGING
- T4: Macro-state — V=0.155 (weak); only m notable (20.5% AXm)
- T5: Line position — only m (0.926, line-final) and ee (0.416, early) are specialists
- T6: Cross-position divergence — 0/12 shared atoms stable; h most stable (JSD=0.004), m most divergent (JSD=0.560)
- T7: Compositional structure — YES: first atom V=0.277 (category), last atom R²=0.059 (position)
- T8: Mode decomposition — Mode A={d,e,ee,h,y} THERMAL; Mode B={a,i,ii,l,m,n,o,r,s} STAGING/FLOW
- T9: Synthesis — suffix is parallel compositional domain: same alphabet, HEAD→TERM structure, position-dependent semantics

---

### Cross-Slot Interaction Grammar (C1411-C1415) -- Phase: CROSS_SLOT_INTERACTION (Phase 516)

> **Summary:** Tests how PREFIX, MIDDLE, and SUFFIX constrain each other within tokens at atom resolution. The instruction encoding chain is PREFIX -> MIDDLE -> SUFFIX (not three-way): PREFIX selects MIDDLE HEAD atom (V=0.414), MIDDLE determines suffix via TERM atom (V=0.503 > PREFIX V=0.169), PREFIX-SUFFIX is the most independent pair (NMI=0.090, mediated through MIDDLE). Sister pairs select identical MIDDLE atoms (JSD=0.010). Cross-slot atom co-occurrence reveals exclusion rules (d O/E=0.203, e O/E=1.310) and 2 absolute prohibitions (l/r-TERM x e-SUFFIX HEAD = 0). 83 forbidden PREFIX x MIDDLE HEAD combinations quantify atom-level channeling.

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1411 | PREFIX->MIDDLE selectivity hierarchy with sister pair atom identity | 2 | B, PREFIX, MIDDLE, atom, sister pair, selectivity | PREFIX->MIDDLE HEAD V=0.414 (MI=1.089 bits). Sister pairs nearly identical: ch/sh JSD=0.010, ok/ot JSD=0.010. BASE predicts HEAD better than modifier (V=0.494 vs 0.295). Sisters select same atoms, differ only in manner. |
| 1412 | MIDDLE dominates suffix determination via terminal atom | 2 | B, MIDDLE, suffix, atom, selectivity, terminal | Full MIDDLE->suffix mode V=0.678, MIDDLE TERM->mode V=0.503, PREFIX->mode V=0.169. MIDDLE TERM outpredicts PREFIX 3x. MIDDLE reduces suffix entropy 1.767 bits (45.1%) vs PREFIX 0.283 bits (7.2%). TERM is the suffix gatekeeper. |
| 1413 | PREFIX-SUFFIX coupling is MIDDLE-mediated | 2 | B, PREFIX, MIDDLE, suffix, independence, mediation | PREFIX-SUFFIX NMI=0.090 (weakest pair) vs MIDDLE-SUFFIX NMI=0.451, PREFIX-MIDDLE NMI=0.481. Three-way synergy: +0.047 bits mode, +0.009 bits identity (negligible). Instruction chain: PREFIX->MIDDLE->SUFFIX, confirming C1003 at atom level. |
| 1414 | Cross-slot atom co-occurrence exclusion rules | 2 | B, MIDDLE, suffix, atom, co-occurrence, exclusion | d REPELS (O/E=0.203, p=7.1e-81), a REPELS (0.465), h REPELS (0.509); e ATTRACTS (1.310, p=3.8e-50). Absolute: l-TERM x e-SUF_HEAD = 0 (exp=37), r-TERM x e-SUF_HEAD = 0 (exp=46). Complementary information principle; stability accumulates. |
| 1415 | 83 forbidden PREFIX x MIDDLE HEAD combinations at atom level | 2 | B, PREFIX, MIDDLE, atom, forbidden, combinations | 83 pairs with O/E < 0.10: qo x e (0.061), qo x o (0.037), ok x k (0.000), da x e (0.000), ch x i (0.000). Each PREFIX defines narrow atom window. Extends C911 to sub-MIDDLE atom level. |

**Phase 516 findings (Cross-Slot Interaction Grammar, 9 tests):**
- T1: PREFIX->MIDDLE HEAD V=0.414, MI=1.089 bits; sister pairs JSD=0.010 (identical atoms)
- T2: PREFIX->suffix PRESENCE V=0.489; qo 90.4% suffixed vs ok/ot 28%
- T3: MIDDLE->suffix mode V=0.678; MIDDLE TERM alone V=0.503 > PREFIX V=0.169
- T4: Three-way synergy +0.047 bits (mild); pairwise dominates (confirms C1003)
- T5: Slot independence: MIDDLE-SUFFIX NMI=0.451, PREFIX-MIDDLE NMI=0.481, PREFIX-SUFFIX NMI=0.090
- T6: d REPELS across slots (0.203), e ATTRACTS (1.310); n near-zero co-occurrence
- T7: BASE V=0.494 vs modifier V=0.295 for MIDDLE HEAD; base dominates (confirms C1219)
- T8: MIDDLE reduces suffix entropy 6.2x more than PREFIX; MIDDLE TERM 2.5x more than HEAD
- T9: 83 depleted PREFIX x HEAD pairs; 2 absolute TERM x SUF_HEAD prohibitions (l/r x e = 0)

### ARTICULATOR Deep Dive (C1416-C1421) -- Phase: ARTICULATOR_DEEP_DIVE (Phase 517)

> **Summary:** Comprehensive analysis of the ARTICULATOR slot `[ARTICULATOR] + PREFIX + MIDDLE + [SUFFIX]`. Articulators are rare (4.41% of B tokens), dominated by y (51.2%), and concentrate at line-initial position (17.3% vs 2.7% medial = 6.48x). They categorically exclude BARE tokens and qo-PREFIX, lock to sh-family PREFIXes, select e-HEAD MIDDLEs (76-90% vs 40% baseline), and suppress suffix attachment (0.34-0.55x). Category information is 100% MIDDLE-mediated (I(ART;CAT|MIDDLE) = 0.000 bits). ARTICULATOR is a peripheral line-opening specification marker, not a fourth independent morphological axis.

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1416 | ARTICULATOR rate and inventory | 2 | B | 4.41% of B tokens (1,019/23,096). y=51.2%, d=11.6%, l=11.4%, r=7.0%, p=5.4%, t=5.2%, k=3.5%, s=3.3%, f=1.4%. Section-dependent: COSMO 8.31% highest, BIO 3.64% lowest. |
| 1417 | ARTICULATOR line-initial concentration | 2 | B, line, position | 17.3% at line-initial vs 2.7% medial (6.48x). Paragraph headers 4.11x enriched. Two sub-groups: INITIAL (d,k,p,s,t,y at Q0 2.4-4.2x) and FINAL (l,r at Q4 2.4-2.6x). V=0.092, p < 1e-115. |
| 1418 | ARTICULATOR PREFIX-locked with BARE/qo exclusion | 2 | B, PREFIX, ARTICULATOR | 29 forbidden ART x PREFIX pairs. BARE: 0/3,864 (zero). qo: 3/4,069 (0.07%). sh-locked: t 94%, k 94%, d 72%. y distributes across ch/te/ta/sh. V=0.196, p < 1e-300. |
| 1419 | ARTICULATOR e-HEAD selectivity and k-HEAD exclusion | 2 | B, MIDDLE, ARTICULATOR, atom | 76-90% e-initial MIDDLE vs 40% baseline (1.9-2.3x). k-HEAD excluded from d,k,t (4 forbidden pairs). PREFIX mediates 68.3%. Articulators mark cooling not heating. |
| 1420 | ARTICULATOR suffix suppression | 2 | B, SUFFIX, ARTICULATOR | Suffix rate 16.7-27.2% vs 49.3% baseline (0.34-0.55x). Only p matches baseline (58.2%). Specification context suppresses execution-mode marking. |
| 1421 | ARTICULATOR category full MIDDLE mediation | 2 | B, ARTICULATOR, category | I(ART;CAT\|MIDDLE) = 0.000 bits. Raw V=0.042 entirely MIDDLE-mediated. MI: ART-PREFIX 0.111 > ART-MIDDLE 0.060 > ART-SUFFIX 0.015 bits, all 10-100x below main chain. |

**Phase 517 findings (ARTICULATOR Deep Dive, 10 tests):**
- T1: 4.41% rate, y dominant, COSMO 2.3x BIO rate
- T2: V(ART,PREFIX)=0.196; BARE/qo categorically excluded; sh-family dominates
- T3: e-HEAD 76-90% vs 40% baseline; k-HEAD excluded; PREFIX mediates 68.3%
- T4: Suffix rate 0.34-0.55x; p-articulator sole exception
- T5: V(ART,CAT)=0.042; I(ART;CAT|MIDDLE) = 0.000 bits (full mediation)
- T6: MI hierarchy ART-PREFIX 0.111 > ART-MIDDLE 0.060 > ART-SUFFIX 0.015 bits (10-100x below chain)
- T7: Line-initial 17.3% vs 2.7% medial (6.48x); V=0.092 p<1e-115
- T8: Paragraph headers 4.11x enriched; par-final depleted
- T9: 29 forbidden ART x PREFIX pairs; 4 forbidden ART x HEAD pairs
- T10: q is NOT an articulator; qo confirmed as PREFIX compound

---

### Suffix Mode Cycling Mechanism (C1422-C1424) -- Phase: SUFFIX_MODE_CYCLING_MECHANISM (Phase 518)

> **Summary:** Investigates what drives the alternation between suffix Mode A ({d, e, ee, h, y} -- THERMAL/MONITORING) and Mode B ({a, i, ii, l, m, n, o, r, s} -- STAGING/FLOW) within paragraphs. Token-level mode is ~80% MIDDLE-determined (C1412) with NO sequential dependency. Lines show mild mode PERSISTENCE (60.6% same-mode), not interleaving. C1229's "80% interleaved" refers to paragraph classification (fraction containing mixed modes), not consecutive-line switch rate (which is 39.4%, BELOW random). TERMINAL switching does not drive mode switching -- mode switch rate is identical regardless of whether dominant TERMINAL changed.

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1422 | suffix mode is MIDDLE-determined without sequential dependency | 2 | B, suffix, mode, MIDDLE, sequential, token-level | Joint token features (PREFIX+HEAD+TERM) explain 21.4% of mode entropy (accuracy 0.682, 1.33x). Previous token mode adds only 1.64% beyond features (CMI=0.016 bits). Raw sequential MI (0.003 bits, 0.3%) fully absorbed by token identity. No token-level sequential cycling mechanism. |
| 1423 | line-level mode persistence with weak inertia | 2 | B, suffix, mode, line, sequential, persistence | Consecutive lines: 60.6% same-mode (vs 50% random). CMI(prev_mode; curr_mode \| dom_TERM) = 0.029 bits (2.89% of H). 4/8 TERMINAL strata significant. Lines persist in mode, not alternate. C1229 "80% interleaved" = paragraph classification, not line-pair switch rate. |
| 1424 | mode switching is TERMINAL-independent at line level | 2 | B, suffix, mode, line, TERMINAL, independence | Switch rate 39.1% when same dominant TERMINAL vs 39.4% when different (delta 0.3pp, NS). TERMINAL determines each line's mode independently. Below-random interleaving (39.4% vs 49.9%) 100.6% captured by TERMINAL vocabulary effects. No TERMINAL alternation driver. |

**Phase 518 findings (Suffix Mode Cycling Mechanism, 10 tests):**
- T1: TERMINAL switch rate 0.734, switch-to-expected 0.938 (self-chain enriched: t 2.15x, k 1.96x, h 1.89x)
- T2: TERMINAL->mode V=0.503 (replicates C1412); h=91.2%A, r=96.7%B, k=67.0%A, y=62.5%B
- T3: Line mode prediction: TERMINAL acc=0.582 (1.11x baseline); position alternation acc=0.505 (below baseline)
- T4: HEAD MI=0.091 bits (9.1%); HEAD-TERMINAL MI=0.935 bits (strongly coupled)
- T5: PREFIX MI=0.028 bits (2.8%)
- T6: Joint features 21.4% of H; CMI(prev_mode|features) = 1.64% -- NO token sequential dependency
- T7: Line CMI(prev|TERM) = 2.89%; 4/8 strata significant (y, l, n, h) -- WEAK genuine line inertia
- T8: 0 forbidden TERMINAL pairs; self-chain enriched for Mode A terminals
- T9: Cross-line token switch 43.7% vs within-line 46.4% (p=0.037); line boundaries mildly suppress switching
- T10: Line interleave rate 0.3935, BELOW random 0.499; TERMINAL switching does NOT drive mode switching (39.1%=39.4%)

---

### Line-Level Architecture (C1425-C1430) -- Phase: LINE_LEVEL_ARCHITECTURE (Phase 519)

> **Summary:** Systematic profiling of the Currier B line as a structural unit: length distribution, boundary profiles, internal category gradients, PREFIX positional grammar validation, internal transitions, cross-line independence, information content, line types, and boundary marking hierarchy. 10 tests across 23,096 tokens in 2,420 lines. Lines are self-contained execution units with three zones: SPECIFICATION (Q0), THERMAL WORK (Q1-Q3), CLOSURE (Q4).

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1425 | line length unimodal distribution | 2 | B, line, length, distribution | Mean=9.54, median=10, CV=0.340. Mode at 10 tokens (19.9%). 94.7% within 3-13. Header 1.097x longer than body. BIO shortest (8.97), COSMO longest (11.65). Continuous unimodal, not discrete. |
| 1426 | line-initial specification profile | 2 | B, line, position, initial, specification | ARTICULATOR 3.93x, STAGING 1.57x, MARKING 1.42x. PREFIXes po/dch/so/to 5-8x enriched. Head atom e-dominant (53.7%). Lines open with specification vocabulary. Top words: daiin (3.5%), saiin (2.0%). |
| 1427 | line-final transition profile | 2 | B, line, position, final, transition, closure | TRANSITION 1.63x, THERMAL 0.56x depleted. Terminal m atom 196x increase pos1->final. Suffix -m 9.54x, -am 7.83x enriched. PREFIXes ar/al/or 3.4-4.6x. Lines close with state-change/closure vocabulary. |
| 1428 | THERMAL-peak-then-decline positional gradient | 2 | B, line, position, gradient, category, THERMAL | THERMAL peaks Q1 (29.4%) not Q0 (24.3%) because Q0 is specification zone. Declines to 17.6% Q4. FLOW rises monotonically (17.6%->22.6%). TRANSITION jumps Q4 (14.1%->19.1%). BARE rises Q0->Q4 (14.3%->21.9%). |
| 1429 | cross-line category independence | 2 | B, line, independence, category, cross-line | Suffix mode MI=0.003, category MI=0.032 bits, vocabulary Jaccard=0.153. Line length r=0.406 (folio-mediated). Extends C670/C673/C674/C1233. Lines are i.i.d. samples conditioned on folio identity. |
| 1430 | information U-shape at line boundaries | 2 | B, line, information, position, boundary | Token info U-shape: Q0=10.29, Q1-Q3=9.58-9.62, Q4=10.11 bits. Boundaries more informative than interior. Initial=specification (folio-specific), final=routing (closure markers), interior=routine thermal. |

**Phase 519 findings (Line-Level Architecture, 10 tests):**
- T1: Mean=9.54, median=10, CV=0.340. 94.7% in 3-13 range. Header/body ratio 1.097x
- T2: ARTICULATOR 3.93x line-initial. po/dch/so/to 5-8x enriched. STAGING 1.57x, MARKING 1.42x
- T3: TRANSITION 1.63x line-final, THERMAL 0.56x depleted. -m 9.54x, -am 7.83x. ar/al/or 3.4-4.6x
- T4: THERMAL peaks Q1 (29.4%), FLOW rises Q0->Q4, TRANSITION jumps Q4, ARTICULATOR drops sharply after Q0
- T5: 33 PREFIXes: 12 INITIAL, 8 FINAL, 13 CENTRAL. sh=0.396 < ch=0.515. Validates C1218-C1219
- T6: Category self-transition 0.185. THERMAL->THERMAL 0.277 strongest. Mean entropy 2.806 bits (weakly constrained)
- T7: INDEPENDENT. Category MI=0.032, suffix MI=0.003, length r=0.406 (folio-mediated)
- T8: U-shaped info: Q0=10.29 > Q1-Q3~9.6 < Q4=10.11 bits. Boundaries more informative
- T9: Body 52.2% THERMAL-dominant. Headers 15.4% MARKING. BIO 58.5% THERMAL, COSMO 32.5% FLOW
- T10: Cross-line entropy 0.984x within-line. LINE=PARAGRAPH boundary strength. -m 9.54x final

---

### Paragraph AXM Residual (C1431-C1433) -- Phase: PARAGRAPH_AXM_RESIDUAL (Phase 520)

> **Summary:** Systematic decomposition of the ~24% paragraph AXM variance unexplained by PREFIX composition (C1405). 10 tests across 41 features, 283 paragraphs, 23,096 tokens. No non-PREFIX feature adds predictive power. The residual decomposes as 25.2% measurement noise + 4.2% genuine design freedom. PREFIX is the sole dynamical control point at paragraph level.

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1431 | non-PREFIX features add zero predictive power for paragraph AXM | 2 | B, paragraph, AXM, MIDDLE, suffix, articulator, line, design-freedom | 41 features across 8 groups (HEAD, TERMINAL, suffix, line, articulator, kernel, MIDDLE props, interactions) all show negative or zero delta beyond PREFIX. Full model CV R2=0.707 vs PREFIX-only 0.711. All non-PREFIX features are PREFIX-mediated (C1411, C1418, C1422) or irrelevant. |
| 1432 | paragraph AXM residual is 85% measurement noise | 2 | B, paragraph, AXM, noise, design-freedom, C1169, C1405 | 29.4% residual = 25.2% binomial sampling noise + 4.2% genuine freedom. Noise = 85.5% of residual. Theoretical max R2=0.748; PREFIX achieves 0.706 (94.4% of max). Residuals normal (Shapiro-Wilk p=0.152), section-neutral (p=0.061), REGIME-neutral (p=0.444). Refines C1169. |
| 1433 | PREFIX-AXM mediation chain is complete at paragraph level | 2 | B, paragraph, AXM, PREFIX, mediation, C1405, C1411, C1418, C1422 | PREFIX is sole load-bearing predictor. Complete mediation: PREFIX->HEAD (C1411), PREFIX->ART (C1418), MIDDLE->suffix (C1422). No interaction or structural feature carries independent signal. 4.2% genuine freedom is irreducible per-program variation. |

**Phase 520 findings (Paragraph AXM Residual, 10 tests):**
- T1: HEAD atoms explain 26.0% alone but add -0.5% beyond PREFIX. k-initial rho=+0.491, a-initial rho=-0.553. Fully PREFIX-mediated.
- T2: Suffix features add -0.3% beyond PREFIX. Suffix rate rho=+0.380 but doubly mediated.
- T3: Line structure (count, mean/std length) adds +0.04% beyond PREFIX. Irrelevant.
- T4: Articulator features add -0.2% beyond PREFIX. PREFIX-determined per C1418.
- T5: Full 41-feature model DEGRADES vs PREFIX-only: CV delta=-0.004, LOO delta=-0.011.
- T6: Drop-one shows PREFIX is sole load-bearing group (delta=+0.508). All others negative or zero.
- T7: Residuals normal, unstructured. No section/REGIME/position pattern.
- T8: PREFIX-MIDDLE interactions produce overfitting. 60 terms: delta=-0.155. 3 key: delta=-0.006.
- T9: Headless compound fraction NS (rho=-0.054, p=0.367). Compound fraction mediated by PREFIX.
- T10: Noise floor 25.2%. Genuine freedom 4.2%. PREFIX achieves 94.4% of theoretical maximum.

---

### m-Terminal Anomaly (C1434-C1439) -- Phase: M_TERMINAL_ANOMALY (Phase 521)

> **Summary:** Deep characterization of the m-terminal MIDDLE atom, which shows 196x enrichment from line-initial to line-final (C1427). 10 tests plus 5 deep-dives across 289 m-terminal tokens. m is a dedicated body-line closure operator: 10 types (lowest diversity), 87.9% TRANSITION (most concentrated), 0% hazard categories, 4.2% suffix rate (most suppressed), body-line-exclusive (0% header, depleted par-final). The -am suffix and m-terminal MIDDLE are orthogonal systems (1 token overlap) operating at different grammar levels.

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1434 | m-terminal low-diversity closure specialization | 2 | B, MIDDLE, atom, m-terminal, closure, diversity | 10 types, 289 tokens, 1.25% of B. `am` 60.2% + `m` 26.3% = 86.5%. Lowest diversity of any terminal (10 vs y:33, l:48, r:49, h:188). 95.9% bare. Near-zero MOD stack. |
| 1435 | m-terminal body-line exclusivity | 2 | B, MIDDLE, atom, m-terminal, line, paragraph, body, header, position | 10.45% body-line-final, 0.00% header-line-final, 3.26% par-final (Fisher p<0.000001). Categorically excluded from headers, depleted at paragraph boundaries. Scope = LINE BODY. |
| 1436 | m-terminal near-pure TRANSITION category | 2 | B, MIDDLE, atom, m-terminal, category, TRANSITION | 87.9% TRANSITION (5.86x). Most category-concentrated terminal atom. 5 categories absent (THERMAL, MONITORING, FLOW, CONTAINMENT, MARKING). 7.4% of all TRANSITION tokens. |
| 1437 | m-terminal complete hazard exclusion | 2 | B, MIDDLE, atom, m-terminal, hazard, FLOW, CONTAINMENT | 0% FLOW, 0% CONTAINMENT. 31.8% preceded by FLOW tokens -- closes hazard-containing sequences without being hazardous. Never source, target, or buffer. |
| 1438 | m-terminal categorical suffix suppression | 2 | B, MIDDLE, atom, m-terminal, suffix, suppression | 4.2% suffix vs 48.3% overall = 11.5x suppression. Most extreme of any terminal. 6.8x stronger than ARTICULATOR suppression (C1420). Self-contained closure operators. |
| 1439 | m-terminal MIDDLE and -am suffix are orthogonal systems | 2 | B, MIDDLE, atom, m-terminal, suffix, -am, paragraph, line, closure | 1 token overlap (`amam`). m-terminal: 289 tokens, TRANSITION 87.9%, body-line-final. -am suffix: 234 tokens, multi-category, par-final 5.19x. Two-level closure: m closes body lines, -am closes paragraphs. |

**Phase 521 findings (m-Terminal Anomaly, 10 tests + 5 deep-dives):**
- T1: 289 tokens, 10 types. `am` 60.2%, `m` 26.3%. Lowest terminal diversity.
- T2: Exponential ramp from 0.04% (pos 1) to 8.8% (final). 7.0x concentration index (next: l 1.1x).
- T3: Body-line-final 10.45%, header 0%, par-final 3.26%. Body-line exclusive.
- T4: ch/sh 0.16-0.17x, qo 0.02x depleted. ar/al/or 4.6-6.5x, da 3.7x enriched. LATE/BARE channel.
- T5: 4.2% suffix rate (11.5x suppression). 95.9% bare. Self-contained operators.
- T6: 87.9% TRANSITION (5.86x). 5 categories absent. Most concentrated terminal.
- T7: Within-line successor broadly distributed. Cross-line successor neutral. Pure closure, no routing.
- T8: 0% FLOW/CONTAINMENT. 31.8% preceded by FLOW. Closes hazard sequences safely.
- T9: m most concentrated (7.0x), most initial-depleted (0.04%). Extreme positional polarity.
- T10: m-closed lines longer (10.9 vs 9.4). TRANSITION elevated (1.44x). Anti-correlated with Bio section (3.2% vs Cosmo 18.3%).
- A1-A5: -am suffix and m-terminal MIDDLE overlap at 1 token. Orthogonal closure systems at different grammar levels.

---

### Two-Level Closure Architecture (C1440-C1445) -- Phase: TWO_LEVEL_CLOSURE (Phase 522)

> **Summary:** Characterizes the two-level closure architecture where MIDDLE terminal atoms and suffix atoms encode complementary information at the token boundary. 10 tests across 16,925 tokens with terminal classification. Key findings: three-tier terminal opacity gradient (OPAQUE y/m/n <5% suffix, SEMI-TRANSPARENT l/r 17-20%, TRANSPARENT h 99%) is an active grammar rule not distributional artifact (y O/E=0.159, m O/E=0.105, n O/E=0.168 in matched body-line-final population). TERMINAL carries 3.6x more category information than suffix head (1.261 vs 0.347 bits) with only 8.2% redundancy -- position-invariant (3.2-3.5x across all quintiles). 17 forbidden TERMINAL x suffix-head pairs; e-suffix universally blocked by non-h terminals (h is exclusive e-suffix gateway). Self-atom cross-layer repulsion for y (0.028x), n (0.000x), r (0.486x). Paragraph-level m-terminal/suffix anticorrelation (rho=-0.199, p=0.00001).

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1440 | three-tier terminal opacity gradient | 2 | B, MIDDLE, atom, terminal, suffix, gradient, opacity | OPAQUE (n 0.84%, y 1.61%, m 4.15%), SEMI-TRANSPARENT (l 16.78%, r 19.52%), TRANSPARENT (h 98.68%). V=0.753, chi2=7384.7. NOT binary. |
| 1441 | active terminal-suffix exclusion grammar rule | 2 | B, MIDDLE, atom, terminal, suffix, exclusion, grammar, rule | y O/E=0.159, m O/E=0.105, n O/E=0.168 in matched body-line-final non-par-final population (N=1,439, baseline 45.8%). m/am Fisher p=0.000012. Active grammar rule, not distributional artifact. |
| 1442 | TERMINAL-suffix category information complementarity | 2 | B, MIDDLE, atom, terminal, suffix, information, complementarity, mutual-information, category | TERMINAL 1.261 bits vs suffix-head 0.347 bits (3.6x ratio). Joint 1.252 bits, redundancy 0.112 bits (8.2%). 88.5% of TERM x suffix-head pairs have different top categories. Layer ratio stable 3.2-3.5x across all line positions. |
| 1443 | 17 forbidden TERMINAL x suffix-head pairs | 2 | B, MIDDLE, atom, terminal, suffix, forbidden, co-occurrence, exclusion | e-suffix blocked by all non-h terminals (5 pairs). r-terminal excludes 5 suffix heads. l-terminal excludes 4. h-terminal excludes 5. 8 enriched pairs (>3.0x): o-suffix universal attractor for l/r/m terminals. |
| 1444 | self-atom cross-layer repulsion | 2 | B, MIDDLE, atom, terminal, suffix, self-repulsion, cross-layer | y O/E=0.028 (Fisher p=0.0), n O/E=0.000 (p=0.0), r O/E=0.486 (p=0.0). l weak (0.621). h neutral (0.843). m neutral (1.048). Strongest repulsion at most opaque terminals. |
| 1445 | m-terminal and suffix anticorrelation at paragraph level | 2 | B, MIDDLE, atom, m-terminal, suffix, paragraph, anticorrelation, section | rho=-0.199, p=0.00001 across 486 paragraphs. Mean m-term 1.27%, suffix 49.7%, both 0.06%. Bio lowest m-term (0.57%), Stars/Recipe highest suffix (52.0%). Two closure layers are partial substitutes at paragraph scale. |

**Phase 522 findings (Two-Level Closure, 10 tests):**
- T1: 6x13 TERMINAL x suffix-head contingency table. 17 forbidden pairs (O/E<0.1). e-suffix blocked by all non-h terminals. 8 enriched (>3.0x).
- T2: Three-tier opacity gradient. OPAQUE (y/m/n <5%), SEMI-TRANSPARENT (l/r 17-20%), TRANSPARENT (h 99%). V=0.753, chi2=7384.7.
- T3: Self-atom repulsion. y 0.028x, n 0.000x, r 0.486x across MIDDLE-terminal to suffix-head boundary. Strongest at most opaque terminals.
- T4: Category complementarity. TERMINAL 1.261 bits vs suffix-head 0.347 bits, 3.6x ratio. 8.2% redundancy. 88.5% of pairs different top categories.
- T5: h-terminal suffix composition. h-terminal tokens freely take all suffix types -- transparent gating.
- T6: Enriched pair catalog. y+l 8.4x, n+y 8.2x, l+o 5.4x, y+d 3.8x, m+o 3.7x, r+o 3.5x, y+s 3.1x, y+r 3.0x.
- T7: Category MI by position quintile. Ratio stable 3.2-3.5x across Q0-Q4.
- T8: Position-invariant complementarity confirmed. Neither layer gains or loses dominance.
- T9: Paragraph-level m-terminal/suffix anticorrelation. rho=-0.199, p=0.00001. Bio lowest m-term, Stars/Recipe highest suffix.
- T10: Active exclusion test in matched population (body-line-final, non-par-final, N=1,439). y 0.159x, m 0.105x, n 0.168x vs 45.8% baseline. m/am Fisher p=0.000012.

---

### Hazard Atom-Level Decomposition (C1446-C1451) -- Phase: HAZARD_ATOM_DECOMPOSITION (Phase 523)

> **Summary:** Decomposes the 17 forbidden transitions (C109, Tier 0) at atom-level resolution using HEAD+MOD*+TERM instruction encoding (C1393-C1394). 10 tests across 23,096 tokens and 20,676 adjacency pairs. Key findings: k-HEAD is completely hazard-immune (0.0% across 3,100 tokens, all frames neutralized to 0%). Terminal atom hazard partition: HIGH (r 92.58%, n 38.97%, l 30.88%), LOW (e 16.49%, y 15.82%), ZERO (k, m, h 0%). 7 high-hazard frames account for >95% of hazard. Sister pairs show hazard parity (ok/ot 1.04x, ch/sh 1.29x). SEMI_TRANSPARENT opacity tier concentrates hazard at 56.5% (2.5x OPAQUE). Mode B carries 100% of forbidden violations (11/11). All 5 standard modifiers {c,d,f,p,s} quench hazard to 0%; i-modifier boosts 1.69x.

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1446 | k-HEAD complete hazard immunity | 2 | B, MIDDLE, atom, k-initial, hazard, HEAD, immunity | 0.0% hazard across 3,100 k-HEAD tokens. Zero source, zero target. All k-frames 0% including k+r (15 tokens). Kernel atoms collectively safest: k=0%, e=2.2%, h=3.1%. |
| 1447 | terminal atom hazard partition | 2 | B, MIDDLE, atom, terminal, hazard, partition, FLOW | HIGH (>30%): r 92.58%, n 38.97%, l 30.88%. LOW (1-20%): e 16.49%, y 15.82%. ZERO: k, m, h 0%. r-terminal is dominant hazard concentrator. Cross-cuts C1440 opacity gradient. |
| 1448 | HEAD x TERM frame hazard map with k-neutralization | 2 | B, MIDDLE, atom, HEAD, TERM, frame, hazard, k-neutralization | 7 high-hazard frames (>50%): o→bare 100%, d→y 99.7%, a→l 98.9%, a→r 98.5%, o→r 98.0%, e→e 75.5%, a→n 65.6%. k neutralizes ALL terminal combinations. e→y safe pathway (3,475 tokens, 0%). |
| 1449 | PREFIX channel hazard with sister parity | 2 | B, PREFIX, hazard, sister pair, ch, sh, ok, ot, channel | ok/ot 1.04x (32.1% vs 30.7%), ch/sh 1.29x (12.8% vs 9.9%). Sister choice NOT hazard mechanism. ch carries 45% of forbidden violations (5/11). qo safe at 17.8%. |
| 1450 | opacity tier hazard gradient | 2 | B, MIDDLE, atom, terminal, hazard, opacity, gradient, suffix | SEMI_TRANSPARENT 56.5% (2.5x OPAQUE 22.8%). TRANSPARENT (h) 0%. Suffixed 14.6% vs unsuffixed 35.6% (2.44x). Suffix attachment = hazard reduction mechanism. |
| 1451 | Mode B exclusive forbidden violation concentration | 2 | B, suffix, mode, hazard, forbidden, violation, Mode-B | Mode B: 30.8% hazard, 11/11 violations (100%). Mode A: 9.5% hazard, 0 violations. Mode A kernel-dominant (k+e=55.6%), Mode B yield-dominant (a+o=28.6%). Specification safe, execution hazardous. |

**Phase 523 findings (Hazard Atom Decomposition, 10 tests):**
- T1: Hub MIDDLE atom decomposition. HAZARD_SOURCE: r/y-terminal dominant. HAZARD_TARGET: a-HEAD concentrated. SAFETY_BUFFER: k/o-HEAD. PURE_CONNECTOR: e-HEAD dominant (4/8).
- T2: Hazard class atom signatures. PHASE_ORDERING: y-terminal sources, a-HEAD targets. COMPOSITION_JUMP: r-terminal sources. CONTAINMENT_TIMING: h/e sources, o-enriched targets.
- T3: k-HEAD complete hazard immunity (0.0%, 3,100 tokens). All kernel atoms hazard-depleted: k=0%, e=2.2%, h=3.1%.
- T4: Terminal atom hazard partition. HIGH: r 92.58%, n 38.97%, l 30.88%. LOW: e 16.49%, y 15.82%. ZERO: k, m, h 0%.
- T5: 7 high-hazard frames dominate. k as HEAD neutralizes ALL terminals to 0%. e→y (3,475 tokens) is massive safe pathway.
- T6: PREFIX hazard variation 3.3-73.0%. Sister parity: ok/ot 1.04x, ch/sh 1.29x. ch carries 45% of forbidden violations.
- T7: Hazard rises line-initial to line-final (+7.4pp). Forbidden violations concentrate line-final (4/11 = 36%).
- T8: SEMI_TRANSPARENT tier 56.5% hazard (2.5x OPAQUE). Suffixed tokens 2.44x safer than unsuffixed.
- T9: Mode B carries 100% of forbidden violations (11/11). Mode A 9.5% vs Mode B 30.8% hazard.
- T10: All 5 modifiers {c,d,f,p,s} quench hazard to 0%. i-modifier boosts 1.69x. Length 3 and 5+ MIDDLEs near-zero hazard.

---

### i-Modifier Hazard Anomaly (C1452-C1456) -- Phase: I_MODIFIER_HAZARD (Phase 524)

> **Summary:** Phase 524 investigates WHY the i-modifier boosts hazard (C1450 found i boosts 1.69x while all other modifiers quench to 0%). 10 tests across 2,052 i-modified tokens (8.9% of corpus). Key findings: the hazard boost is a Simpson's paradox -- i selects into hazardous HEAD+TERM frames (61.8% in high-hazard frames vs 14.0% non-i) but REDUCES hazard within those frames (weighted delta -0.407, 12/19 frames protective). Non-monotonic extension gradient: single-i=39.8% hazard, double-ii=0.0% (aiin has exactly 0% hazard across 834 tokens). i is categorically anti-thermal (THERMAL 0.05%, 0.002x baseline), operating exclusively in STAGING/TRANSITION/FLOW space. Quenching modifiers partially override i (22.6% -> 7.5%). i-tokens are 90.6% suffix-free and 95.7% Mode B due to n-terminal structure.

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1452 | Non-monotonic i-extension hazard gradient | 2 | B, MIDDLE, atom, i-modifier, extension, hazard, non-monotonic | no-i=24.1%, single-i=39.8%, double-ii=0.0%. Single-i STAGING 53.3% + FLOW 39.8%. Double-ii TRANSITION 92.6% with zero FLOW. aiin (834 tokens) = 0% hazard. |
| 1453 | i-modifier frame selection, not inherent hazard | 2 | B, MIDDLE, atom, i-modifier, hazard, frame-selection | Marginal i-effect NEGATIVE (-0.0175). Within-frame weighted delta -0.407. 12/19 frames protective. i in (a,n) frame: 33.5% vs non-i 100%. Simpson's paradox. |
| 1454 | i-modifier anti-thermal category profile | 2 | B, MIDDLE, atom, i-modifier, category, anti-thermal | THERMAL 0.05% (0.002x baseline). STAGING 33.0% (2.58x), TRANSITION 41.0% (2.78x). qo/ch/sh avoid i (0.087-0.097x). da/sa/ok/or concentrate i (2.4-3.8x). |
| 1455 | Quenching modifier partial i-override | 2 | B, MIDDLE, atom, i-modifier, quenching, co-occurrence | i-only=22.6%, both i+quench=7.5%, quench-only=5.9%. Quenching dominates. N=40 co-occurrence. Residual ~1.6pp above quench-only. |
| 1456 | i-modifier suffix depletion | 2 | B, MIDDLE, atom, i-modifier, suffix, mode, n-terminal | Suffix rate 9.4% (vs 52.1% non-i, 0.18x). 95.7% Mode B. 90.5% n-terminal structure preempts suffix attachment. |

**Phase 524 findings (i-Modifier Hazard Anomaly, 10 tests):**
- T1: Single-i vs double-ii hazard split. Single-i=39.8%, double-ii=0.0%. Non-monotonic gradient.
- T2: i vs non-i in same HEAD groups. Within HEAD a: i=32.6% vs non-i=71.2%. Within HEAD o: i=4.1% vs non-i=23.0%. i REDUCES within-frame hazard.
- T3: Extension gradient. no-i=24.1%, single-i=39.8%, double-ii=0.0%. Single-i is STAGING/FLOW, double-ii is TRANSITION.
- T4: Category profile. THERMAL 0.05% (0.002x). STAGING 33.0% (2.58x). TRANSITION 41.0% (2.78x). Anti-thermal.
- T5: PREFIX avoidance. qo 0.089x, ch 0.087x, sh 0.097x. da 3.51x, sa 3.59x, or 3.77x, ok 2.43x.
- T6: Section distribution. Bio 0.64x, Stars/Recipe 1.19x. Thermal sections avoid i.
- T7: Suffix depletion. 9.4% suffix rate (0.18x non-i). 95.7% Mode B. 90.5% n-terminal.
- T8: Quenching override. i-only=22.6%, both=7.5%, quench-only=5.9%. Quenching dominates.
- T9: Macro-state interaction. i-tokens in AXM: 59.5% (vs 62.8% non-i). No strong macro-state effect.
- T10: Simpson's paradox decomposition. Marginal delta=-0.0175. Frame selection +0.390. Within-frame -0.407. 12/19 frames protective.

---

### e→y Safe Pathway (C1457-C1462) -- Phase: EY_SAFE_PATHWAY (Phase 525)

> **Summary:** Phase 525 investigates the e→y frame (HEAD=e, TERMINAL=y), identified in C1448 as the largest safe frame in the grammar at 3,475 tokens (15.0% of corpus). 10 tests across 3,475 e→y tokens plus 82 folios. Key findings: e→y is NOT a reactive recovery mechanism — it is an ambient safety substrate deployed at a constant ~15% rate regardless of local context (Mann-Whitney p=0.310). Hazard rate 0.06% (400x below baseline). Categorically OPERATION-enriched (3.94x), CHSH-channel with sh enrichment (2.45x), qo/BARE categorically excluded. Line-final depleted (0.55x). e→y rate is the strongest single predictor of folio-level program forgiveness (rho=+0.569 with AXM self-transition, rho=-0.473 with hazard rate). Post-e→y, AXM rate increases +9.4pp (one-way ratchet). Together, k-HEAD and e→y account for ~5,558 tokens (24% of corpus) at effectively zero hazard — the grammar's thermal safety envelope.

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1457 | e→y narrow vocabulary dominance | 2 | B, MIDDLE, atom, e-HEAD, y-terminal, vocabulary, dominance | 3,475 tokens (15.0% of corpus) from only 7 MIDDLEs. edy 55.8%, ey 25.6%, eey 18.5% = 99.9%. 49.6% of all e-HEAD tokens. d-modifier dominant. |
| 1458 | e→y categorical safety with OPERATION enrichment | 2 | B, MIDDLE, atom, e-HEAD, y-terminal, hazard, safety, category, OPERATION | 0.06% hazard (2/3,475) vs corpus 23.9% — 400x reduction. OPERATION 3.94x, TRANSITION 1.73x. FLOW/CONTAINMENT/MARKING categorically excluded. Among e-HEAD frames, only e→l, e→bare, e→y are safe. |
| 1459 | e→y context-independent deployment (not recovery-specific) | 2 | B, MIDDLE, atom, e-HEAD, y-terminal, context, recovery, ambient | Post-hazard 14.75%, post-safe 15.35% (Mann-Whitney p=0.310 NS). Pre/post-e→y hazard both match corpus baseline (23%). Ambient safety substrate, not reactive recovery mechanism. |
| 1460 | e→y early-line concentration with final avoidance | 2 | B, MIDDLE, atom, e-HEAD, y-terminal, position, line, paragraph | Mean line position 0.463 (vs 0.500). Line-final 0.55x. Q0-Q1 enriched 1.09-1.13x. Paragraph: header 12.0% → late body 17.5%. Thermal work zone, not closure. |
| 1461 | e→y CHSH-channel with sh enrichment and qo/BARE exclusion | 2 | B, PREFIX, MIDDLE, atom, e-HEAD, y-terminal, channel, sh, qo | sh 2.45x, ch 1.74x; ch/sh ratio 1.07 vs corpus 1.50 (sh-biased). qo 0.04x, BARE 0.002x, da 0.00x. Monitoring/verification channels, not heat source. |
| 1462 | e→y rate predicts folio forgiveness via AXM attractor | 2 | B, MIDDLE, atom, e-HEAD, y-terminal, AXM, forgiveness, folio, hazard | e→y vs AXM self-transition rho=+0.569, p<1e-7. e→y vs hazard rho=-0.473, p=7e-6. Q1 (6.6% e→y) = 40.6% AXM self; Q4 (21.1%) = 55.0%. Post-e→y AXM +9.4pp (one-way ratchet). Mechanical basis of forgiveness gradient. |

**Phase 525 findings (e→y Safe Pathway, 10 tests):**
- T1: 3,475 tokens, 7 MIDDLEs. edy 55.8%, ey 25.6%, eey 18.5%. 49.6% of e-HEAD.
- T2: 0.06% hazard (400x reduction). OPERATION 3.94x, TRANSITION 1.73x. FLOW/CONTAINMENT/MARKING excluded.
- T3: NOT recovery-specific. Post-hazard=14.75%, post-safe=15.35%, Mann-Whitney p=0.310. Ambient substrate.
- T4: Mean position 0.463. Line-final 0.55x. Q0-Q1 enriched. Thermal work zone.
- T5: sh 2.45x, ch 1.74x. qo 0.04x, BARE 0.002x. CHSH monitoring channel.
- T6: Suffix rate 0.46% (0.01x corpus). Categorically Mode B. y-terminal suppresses suffix.
- T7: AXM 78.1% (1.16x). FL_HAZ/FL_SAFE/CC = 0%. Post-e→y AXM +9.4pp. Self-chaining 18.7%.
- T8: 21 safe frames with N>=100. k→bare (2,083), e→bare (867), l→bare (855), o→l (777), ee→y (644).
- T9: Paragraph header 12.0% → late body 17.5%. Paragraph e→y rate vs AXM rho=+0.274.
- T10: Folio e→y vs AXM self-transition rho=+0.569. vs hazard rho=-0.473. Q1→Q4: 40.6%→55.0% AXM self.

---

### Line Zone x Frame Hazard Interaction (C1463-C1466) -- Phase: LINE_ZONE_FRAME_HAZARD (Phase 528)

> **Summary:** Phase 528 tests the interaction between the three-zone line model (C1425-C1430: SPECIFICATION/THERMAL_WORK/CLOSURE) and the frame hazard classification (C1448: 7 HIGH, 3 ZERO, k-IMMUNE). The two independently discovered systems are NOT independent -- they interact with a structured routing pattern. Safe (ZERO) frames enrich at SPECIFICATION (1.236x), immune (k-HEAD) frames enrich at THERMAL_WORK (1.165x, peaking at Q1=1.311x), and hazardous (HIGH) frames enrich at CLOSURE (1.134x). The pattern is universal across line lengths and sections. HIGH frames are NOT positionally homogeneous: o-HEAD HIGH is position-neutral while a/d-HEAD HIGH is closure-biased.

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1463 | Zone-hazard routing at line level | 2 | B, line, position, zone, hazard, frame, routing | Chi2=336.3, V=0.085. ZERO enriched 1.236x at SPEC, IMMUNE 1.165x at WORK, HIGH 1.134x at CLOSURE. Monotonic hazard gradient across line. |
| 1464 | k-IMMUNE THERMAL_WORK onset concentration | 2 | B, MIDDLE, atom, k-HEAD, IMMUNE, line, position, zone | Q1 peak 1.311x, 63.1% in work zone. Mean pos 0.484. Energy modulator concentrates at onset of thermal work. |
| 1465 | HIGH frame positional heterogeneity | 2 | B, MIDDLE, atom, HEAD, TERM, frame, hazard, position, heterogeneity | KW H=68.8, p=1.83e-13, eta2=0.013. o-HEAD HIGH neutral (mean 0.491), a/d-HEAD HIGH closure-biased (mean 0.562). Spread 0.115. |
| 1466 | Zone-hazard pattern line-length invariance | 2 | B, line, position, zone, hazard, frame, length, invariance | V=0.081-0.091 across short/medium/long. Same enrichment pattern in all groups. Minor closure interaction: long lines +4pp HIGH at closure. |

**Phase 528 findings (Line Zone x Frame Hazard, 6 tests + 1 extra):**
- T1: Quintile x hazard. Chi2=371.8, V=0.073. KW eta2=0.010. Mean pos: HIGH=0.536, ZERO=0.444.
- T2: Zone x hazard. Chi2=336.3, V=0.085. SPEC-CLOSURE V=0.135. WORK-CLOSURE V=0.106.
- T3: e→y mean pos 0.463. Q4 depleted 0.762x. Mann-Whitney vs HIGH p=5.7e-26, r=0.136.
- T4: k-HEAD Q1 peak 1.311x. Work zone 63.1% (1.165x). Mean pos 0.484.
- T5: Among 6 HIGH frames: KW H=68.8, p=1.83e-13. o->bare=0.493, a->l=0.602. Spread 0.115.
- T6: V invariant: short=0.091, medium=0.089, long=0.081. Closure hazard: short 22.7%, long 26.7%.
- T-Extra: All 5 sections show SPEC→WORK→CLOSURE hazard increase (except C which is uniformly high).

---

### Paragraph-Level Hazard Gradient (C1467-C1469) -- Phase: PARAGRAPH_HAZARD_GRADIENT (Phase 529)

> **Summary:** Phase 529 tests whether the line-level hazard gradient (C1463: safe operations first, hazardous last) repeats at paragraph scale. The answer is NO -- the paragraph and line levels implement COMPLEMENTARY architectures with comparable effect sizes (V=0.071 vs V=0.085, ratio 0.84) but DIFFERENT topologies. Paragraph headers concentrate LOW/infrastructure vocabulary (1.130x), not ZERO/safe vocabulary (0.784x depleted). Safe/immune vocabulary concentrates in the paragraph BODY (ZERO 1.077x, IMMUNE 1.121x). HIGH hazard concentrates at TAIL (1.134x). The line-level hazard gradient operates independently within ALL paragraph zones (V=0.079-0.094). Safety is enforced at line level; paragraphs enforce specification-first ordering.

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1467 | Paragraph zone x hazard interaction (non-fractal) | 2 | B, paragraph, zone, hazard, frame, routing | Chi2=233.9, V=0.071. LOW-first (HEADER 1.130x), HIGH-last (TAIL 1.134x). DIFFERENT topology from line-level SAFE-first pattern. |
| 1468 | Header infrastructure-first composition | 2 | B, paragraph, header, hazard, LOW, ZERO, composition | HEADER LOW 51.6% (1.130x), ZERO 15.8% (0.784x depleted). e->y 0.796x at HEADER. Headers specify with infrastructure, not safety vocabulary. |
| 1469 | Line hazard gradient paragraph-independent | 2 | B, line, paragraph, zone, hazard, independence, nested | Within-zone line V: HEADER 0.079, BODY 0.094, TAIL 0.091. Line gradient persists independently in all paragraph zones. Two-level safety architecture. |

**Phase 529 findings (Paragraph Hazard Gradient, 8 tests + 2 extra):**
- T1: Zone x hazard. Chi2=233.9, V=0.071. HEADER vs BODY V=0.101 (strongest). LOW 1.130x at HEADER, ZERO+IMMUNE in BODY, HIGH at TAIL.
- T2: e->y. HEADER 0.796x depleted, BODY 1.077x enriched. Para position 0.492 (later).
- T3: k-IMMUNE. HEADER 0.793x depleted, BODY 1.121x enriched.
- T4: HIGH. HEADER 1.057x, BODY 0.936x, TAIL 1.134x. Absolute: H=21.9%, B=19.4%, T=23.5%.
- T5: No monotonic gradient. Spearman rho=0.600, p=0.285 (NS). First/last ratio 1.073.
- T6: Fractal comparison. V=0.071 vs C1463 V=0.085, ratio 0.84. COMPARABLE magnitude, DIFFERENT topology.
- T7: Length interaction. Long (6+) TAIL HIGH 1.274x vs short (2-3) 1.014x. Pattern strengthens with length.
- T8: Header LOW-dominant (51.6% vs 43.8% body). Within-zone line gradients: Q4/Q0 ratio HEADER=1.16, BODY=1.42, TAIL=1.51.
- T-Extra nested: Line gradient within zones: HEADER V=0.079, BODY V=0.094, TAIL V=0.091. All p<10^-11.
- T-Extra sections: TAIL>HEADER HIGH rate in 4/5 sections. V=0.039-0.119 per section.

---

### Cross-Line Hazard Continuity (C1470-C1471) -- Phase: CROSS_LINE_HAZARD (Phase 530)

> **Summary:** Phase 530 tests whether one line's closing hazard predicts the next line's opening safety. C1429 established cross-line category independence (MI=0.032 bits) and suffix mode independence (MI=0.003 bits). C1451 showed Mode B carries 100% of forbidden violations. C1463 showed lines route hazard to line-final. Does this create cross-line hazard memory? NO. Cross-line hazard MI is 0.0172 bits (0.54x of category MI), and ALL correlation (rho=0.238) collapses under within-folio shuffling (MI p=0.212, rho p=0.098). Autocorrelation is flat at ~0.22 across lags 1-4, confirming pure folio-level shared environment with zero sequential structure. Mode-stratified analysis shows B->B pairs (which carry 100% of forbidden violations per C1451) have NO elevated coupling vs A->A. The e->y safe pathway is DEPLETED (0.82x) after high-hazard lines, not enriched -- a folio composition effect, not an anti-recovery mechanism. Lines are independently composed safety units: each opens safe and closes hazardous without reference to predecessors.

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1470 | Cross-line hazard correlation is folio-mediated | 2 | B, line, hazard, cross-line, folio, independence | MI=0.0172 bits (0.54x category). Shuffle p=0.212 MI, p=0.098 rho. Lags 1-4 flat ~0.22. B->B = A->A. |
| 1471 | No compensatory safe opening after hazardous closure | 2 | B, line, hazard, cross-line, e->y, recovery, compensatory | e->y DEPLETED 0.82x after above-median HIGH (Fisher p=0.0001). IMMUNE 0.78x. Folio composition effect. |

**Phase 530 findings (Cross-Line Hazard Continuity, 7 tests + shuffle control):**
- T1: Cross-line hazard MI=0.0172 bits, 0.54x of C1429 category MI (0.032). HIGH rho=0.238. p=0.0005 raw but collapses under folio shuffle.
- T2: Mode-stratified: A->A rho=0.162, A->B=0.214, B->A=0.263, B->B=0.228. B->B MI=0.016 = A->A MI=0.017. No Mode B elevation.
- T3: Closure-to-opening bridge V=0.042. Q4 HIGH -> Q0 ZERO rho=-0.019 (NS). Q4 HIGH -> Q0 HIGH rho=+0.059.
- T4: After HIGH-ending line: ZERO 0.251 vs 0.262 baseline (0.96x). IMMUNE 0.108 vs 0.119 (0.91x). V=0.030.
- T5: e->y at Q0 after above-median HIGH: 0.223 vs 0.271 (0.82x, Fisher p=0.0001). IMMUNE 0.103 vs 0.133 (0.78x). DEPLETION not enrichment.
- T6: Within-paragraph rho=0.233, cross-paragraph rho=0.207. Difference 0.027 (negligible). No paragraph boundary effect.
- T7: Autocorrelation lags 1-4: rho 0.233/0.222/0.217/0.208. Flat profile. Permutation p: 0.115/0.248/0.306/0.535. All folio-mediated.
- Shuffle: MI p=0.212, rho p=0.098. Neither survives within-folio permutation at alpha=0.05.

---

### Modifier Stacking Order (C1472) -- Phase: MODIFIER_STACKING_ORDER (Phase 531)

> **Summary:** Phase 531 resolves C1393's open question on modifier internal ordering. Tested all 15 pairwise orderings of 6 modifier atoms {p,f,i,c,d,s} in 464 MIDDLE types with 2+ modifiers (2,466 tokens). Co-occurrence avoidance is the dominant constraint: 8/15 pairs NEVER co-occur in the modifier slot. Among 7 testable pairs, 0 are strict (100%) or near-strict (>=95%). Three moderate (75-90%) orderings all involve s as late element. The d,s pair is REVERSED vs C1393 gradient (s precedes d 60.9%). Best-fit ordering p->f->c->s->d->i achieves 68.8% type accuracy vs C1393 gradient's 65.9%. 3+ modifier compliance is only 42.6%. Refines C1394 T4 "fixed stacking order" to "statistical preference with co-occurrence avoidance as primary constraint."

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1472 | Modifier co-occurrence avoidance dominates ordering | 2 | B, grammar, composition | 8/15 pairs empty. 0 strict, 3 moderate (all s-late). d,s reversed. Best: p->f->c->s->d->i (68.8%). 3+ compliance 42.6%. |

**Phase 531 findings (Modifier Stacking Order, 9 analyses):**
- A1: 464 MIDDLE types with 2+ mod atoms (2,466 tokens). 349 2-mod, 98 3-mod, 16 4-mod, 1 5-mod.
- A2: 8/15 modifier pairs never co-occur: {p,f}, {p,i}, {p,c}, {p,d}, {f,c}, {f,d}, {i,c}, {i,d}. p avoids all non-s modifiers.
- A3: 7 testable pairs. 3 moderate: p<s (89.7%, p=1.95e-5), f<s (81.8%, p=0.065), c<s (78.8%, p=0.00094). 3 weak: f<i, i<s, c<d. 1 reversed: d,s.
- A4: d,s reversed: s precedes d 60.9% types, 64.5% tokens (p=0.14 NS). C1393 predicts d<s.
- A5: Best type ordering p->f->c->s->d->i (68.8%) beats C1393 gradient (65.9%). Token: 75.9% vs 69.4%. Unique winner.
- A6: 1 transitivity violation in {c,d,s}: c<d and c<s but d>s.
- A7: 3+ modifier compliance with C1393 gradient: 49/115 = 42.6%.
- A8: Per-modifier mean positions (multi-mod only): p=0.261, f=0.408, c=0.508, i=0.532, d=0.589, s=0.631.
- A9: 63 i-repeat types (1,556 tokens), dominated by aiin (834) and iin (560).

---

### Modifier Functional Grouping (C1473-C1474) -- Phase: MODIFIER_FUNCTIONAL_GROUPING (Phase 532)

> **Summary:** Phase 532 explains WHY specific modifier pairs avoid each other (C1472). Tested three hypotheses: (A) discrete functional groups {p,f,i} vs {c,d} vs {s}, (B) redundancy, (C) frame incompatibility. Result: Hypothesis A REJECTED (separation ratio 0.997), Hypothesis B REJECTED (0/5 redundancy signals), Hypothesis C SUPPORTED (5/5 incompatibility signals). Mechanism: modifiers with narrow HEAD selectivity (d=85.1% e-HEAD, i=88.6% a-HEAD) avoid each other because no single HEAD satisfies both demands. s is universal connector via behavioral centrality (lowest mean JSD 0.1176), broad HEAD, and FQ macro-state context. Modifier x HEAD V=0.545, Modifier x TERM V=0.498.

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1473 | Modifier avoidance is frame incompatibility | 2 | B, MIDDLE, atom, modifier, co-occurrence, avoidance, frame, HEAD, TERMINAL | HEAD selectivity conflict: d(85% e), i(89% a), p(79% o) narrow; c,s broad. 5/5 incompatibility, 0/5 redundancy. |
| 1474 | s-modifier universal connector | 2 | B, MIDDLE, atom, modifier, s, co-occurrence, universality | s co-occurs with all 5 others. Lowest mean JSD (0.1176), broad HEAD (entropy 1.909), FQ macro-state (64.6%). |

**Phase 532 findings (Modifier Functional Grouping, 10 analyses):**
- T1: Per-modifier profiles across 6 dimensions (position, category, HEAD, TERMINAL, frame hazard, section) for 9,786 modifier-bearing tokens.
- T2: Pairwise JSD matrix for all 15 modifier pairs. Closest: c-s (0.018), farthest: d-i (0.298).
- T3: Avoiding pairs mean JSD 0.182 > co-occurring 0.151 (1.21x). Avoiding pairs are LESS similar, not more.
- T4: Hypothesis A separation ratio 0.997 -- within-group = between-group behavioral distance. No discrete grouping.
- T5: Folio Jaccard: avoid 0.941 vs cooc 0.963. HEAD Jaccard: avoid 0.900 vs cooc 0.971. Both favor incompatibility.
- T6: Avoiding pairs have higher HEAD JSD (0.409 vs 0.292, 1.40x) and category JSD (0.238 vs 0.144, 1.65x).
- T7: s universality: mean distance 0.1176 (centroid), HEAD entropy 1.909, FQ macro-state 64.6%.
- T8: Modifier x HEAD chi2=7,929 V=0.545. Modifier x TERMINAL chi2=13,372 V=0.498. Both strongly structured.
- T9: HEAD selectivity: d=85.1% e, i=88.6% a (narrow non-overlapping); c entropy 2.076, s entropy 1.909 (broad).
- T10: Category alignment: avoid pairs more likely same-category (37.5% vs 14.3%) -- MARKING modifiers compete for same niche.

---

### HEAD Domain Differentiation (C1475-C1479) -- Phase: HEAD_DOMAIN_DIFFERENTIATION (Phase 533)

> **Summary:** Phase 533 characterizes the 5 HEAD atoms {a, e, o, k, t} as categorically distinct operational domains and resolves the mechanism of k-HEAD hazard immunity. Each HEAD defines a primary domain with extreme specialization: k=THERMAL (90.3%, 3.80x), t=FLOW (87.0%, 4.47x), a=FLOW+TRANSITION (54.2%+41.4%), e=THERMAL+OPERATION (34.7%+32.2%), o=STAGING+OPERATION (32.4%+25.6%), headless=CONTAINMENT+MARKING+STAGING. k-HEAD immunity is INTRINSIC (0% with or without modifiers) not compositional. a-HEAD is the primary hazard carrier (66.0%) and the ONLY HEAD where modifier quenching fails. k and t are terminal-identical (JSD=0.0017) but categorically opposed (JSD=0.784) -- parallel channels with opposite content. Each HEAD selects a distinct modifier profile creating a near-partition: a monopolizes i (4.08x), e monopolizes d (1.99x), o attracts p/f/c, k/t are modifier-depleted, headless is the universal modifier host.

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1475 | HEAD atom domain taxonomy | 2 | B, MIDDLE, atom, HEAD, category, domain, taxonomy | k=THERMAL 90.3%, t=FLOW 87.0%, a=FLOW+TRANSITION, e=THERMAL+OPERATION, o=STAGING+OPERATION. Category JSD 0.111-0.412. |
| 1476 | k-HEAD immunity is intrinsic not compositional | 2 | B, MIDDLE, atom, HEAD, k, hazard, immunity, intrinsic, modifier | k bare 0/2,682; k with modifier 0/418; all 6 frames zero. Only HEAD immune independent of composition. |
| 1477 | a-HEAD is the primary hazard carrier | 2 | B, MIDDLE, atom, HEAD, a, hazard, forbidden, modifier, quench-resistant | 66.0% forbidden (2,032/3,079). ONLY HEAD where quench fails (52.8% with mod). a->l 98.9%, a->r 98.5%, a->n 65.6%. |
| 1478 | k/t terminal mirror with category opposition | 2 | B, MIDDLE, atom, HEAD, k, t, terminal, category, mirror, PREFIX | Terminal JSD=0.0017, Category JSD=0.784. Both bare-dominant, qo-selected, high suffix rate. Parallel channels. |
| 1479 | HEAD-modifier selectivity partition | 2 | B, MIDDLE, atom, HEAD, modifier, selectivity, partition, co-occurrence | a monopolizes i (4.08x), e monopolizes d (1.99x), o attracts p/f/c. k/t modifier-depleted. Headless universal. |

**Phase 533 findings (HEAD Domain Differentiation, 12 analyses):**
- T1: Category profiles per HEAD. k THERMAL 3.80x, t FLOW 4.47x, a dual FLOW+TRANSITION, e multi-category, o STAGING+OPERATION.
- T2: Modifier compatibility. a: i=78.5% (4.08x). e: d=38.1% (1.99x). o: p=3.51x, f=2.83x. k/t modifier-depleted.
- T3: Terminal distributions. k/t bare-dominant (92.5%/90.2%), JSD=0.0017. a: n=41.3%, r=22.3%. e: y=49.6%, bare=42.9%.
- T4: Frame hazard. k=0.0% all frames. a=66.0% (a->l 98.9%, a->r 98.5%). t=62.5%. o=30.7%.
- T5: Line position. a most final (0.582), e most initial (0.451). k/o central.
- T6: PREFIX selectivity. k/t both qo-selected (4.66x/5.00x). a ok/ot-selected. e ch/sh-selected.
- T7: Suffix rates. k=96.9%, t=95.8% (highest). a=48.6% (lowest headed).
- T8: e-depth. e-HEAD mean depth 1.217. Extended e (ee+) = 33.3% of e-HEAD tokens.
- T9: Headless comparison. 6,277 tokens (27.2%). CONTAINMENT 2.70x, MARKING 2.51x, STAGING 2.38x. Universal modifier host.
- T10: Population census. e=7,002 (30.3%), headless=6,277 (27.2%), k=3,100 (13.4%), a=3,079 (13.3%), o=2,717 (11.8%), t=921 (4.0%).
- T11: k-immunity mechanism. k bare 0/2,682, k+mod 0/418, 0/6 frames nonzero, 0 forbidden pairs. INTRINSIC.
- T12: Pairwise distances. Most distant: k vs a (0.494). Most similar: o vs headless (0.161).

---

### i-Modifier Paradox Resolution (C1480-C1482) -- Phase: I_MODIFIER_PARADOX (Phase 534)

> **Summary:** Phase 534 fully resolves the i-modifier Simpson's paradox (C1452-C1456). i selects a-HEAD at 88.6% of headed tokens (C1479), and a-HEAD is the primary hazard carrier (C1477). Full Oaxaca-Blinder decomposition: total marginal effect = -0.069 (i is NET SAFER), selection effect = +0.319 (a-HEAD inflates), conditional effect = -0.388 (protective within each HEAD). The crude 1.69x ratio (C1452) compared i to ALL non-i tokens including unmodified safe-HEAD tokens; properly matched comparison shows i is 28% safer (17.9% vs 24.8%). Within a-HEAD, i produces a COMPLETE TERMINAL TRANSFORMATION: n-terminal goes from 1.2% to 82.1% (70x), category shifts from FLOW (78.1%) to TRANSITION (66.2%). Double-ii achieves 0.0% hazard (N=887) via terminal-locked TRANSITION through n-terminal (94.0%). Monotonic i-count gradient within a-HEAD: no-i=79.3%, single-i=68.6%, double-ii=0.0%.

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1480 | i-modifier Simpson's paradox full resolution | 2 | B, MIDDLE, atom, i-modifier, Simpson, hazard, HEAD, selection, resolution | Total=-0.069 (i safer). Selection=+0.319, Conditional=-0.388. CF: avg HEAD dist → 10.1%. Within a-HEAD: 5/5 protective, delta=-0.536. |
| 1481 | i-modifier terminal transformation within a-HEAD | 2 | B, MIDDLE, atom, i-modifier, a-HEAD, terminal, transformation, TRANSITION | n-term 1.2%→82.1% (70x). r-term 43.8%→0.5% (84x). FLOW→TRANSITION. Position 0.627→0.536. Category redirection not terminal avoidance. |
| 1482 | Double-ii safety via TRANSITION-locked n-terminal | 2 | B, MIDDLE, atom, i-modifier, double-ii, safety, n-terminal, TRANSITION, gradient | Gradient: no-i=79.3%, single-i=68.6%, ii=0.0% (N=887). ii is 94.0% n-terminal, 94.0% TRANSITION. All 5 terminals 0% hazard. |

**Phase 534 findings (i-Modifier Paradox Resolution, 8 analyses):**
- T1: Causal chain. i→a-HEAD 53.15% (88.6% of headed). a-HEAD hazard 54.2%. Chain confirmed.
- T2: Counterfactual. i actual 17.9%, with avg HEAD dist 10.1%, non-i modified 24.8%. HEAD selection inflates 7.8pp.
- T3: Within a-HEAD protection. 5/5 frames protective. Weighted delta -0.536. a→n dominant: 1,254 tokens, delta -0.665.
- T4: Double-ii gradient. no-i=79.3%, single-i=68.6%, ii=0.0%. n-terminal progressive lock-in.
- T5: Modifier comparison in a-HEAD. Bare=83.6%, i=28.8%, c=17.9%, d=11.1%, f=0%, p=11.1%, s=6.3%. i dominant but not strongest.
- T6: Decomposition. Total -0.069, selection +0.319, conditional -0.388. Exact reconstruction.
- T7: Operational profile. i converts a-HEAD from line-final FLOW (ar,al) to medial TRANSITION (aiin,ain).
- T8: Mechanism. Category redirection TRUE, terminal redirection FALSE. ii creates exclusive safe frame.

---

### TERMINAL Functional Taxonomy (C1483-C1487) -- Phase: TERM_FUNCTIONAL_TAXONOMY (Phase 535)

> **Summary:** Phase 535 characterizes the 6 TERMINAL atoms {y, l, r, h, m, n} comprehensively across 12 dimensions, paralleling the HEAD domain taxonomy (C1475-C1479). TERMINAL x CATEGORY Cramer's V=0.463 -- terminals are the second strongest category determinant after HEAD. The 6 terminals form three functional tiers: LOCKED (r=FLOW 98.9%, m=TRANSITION 87.9%), CHANNELED (l=STAGING 64.5%, y=OPERATION 40.6%, n=TRANSITION 39.3%), DIFFUSE (h=MARKING 30.0% across 6 categories, bare=THERMAL 43.2%). Modifier selection is near-perfectly terminal-gated: n exclusively takes i (8.606x, all others 0.0x), y exclusively takes d (2.868x), h takes {c,p,f,s} (5-9x), l/r/m resist modification (<5%). HEAD-TERMINAL affinity creates compositional frames: e locks to y (72.7% of y tokens), a locks to n/m (59-60%), k/t categorically avoid n/m. The hazard circuit is directional: y-terminal sources 90.9% of violations, n-terminal absorbs 90.9%. Opacity and category specificity are orthogonal design axes (r is SEMI-TRANSPARENT but LOCKED; h is TRANSPARENT but DIFFUSE).

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1483 | TERMINAL category specificity gradient | 2 | B, MIDDLE, atom, terminal, category, specificity, gradient, V=0.463 | V=0.463 (2nd after HEAD). r=FLOW 98.9% (norm_ent=0.036, 1 sig cat). m=TRANSITION 87.9% (0.211, 2 sig). l=STAGING 64.5% (0.456, 3 sig). y=OPERATION 40.6% (0.631, 4 sig). n=TRANSITION 39.3% (0.652, 4 sig). h=MARKING 30.0% (0.844, 6 sig). bare=THERMAL 43.2% (0.818, 6 sig). |
| 1484 | TERMINAL modifier exclusivity partition | 2 | B, MIDDLE, atom, terminal, modifier, exclusivity, partition, C1472, C1479 | n: i=8.606x, all others 0.0x (3,553 i-mod, 0 others). y: d=2.868x, all <0.03x. h: c=9.1x, p=7.7x, f=6.4x, s=5.0x; i/d 0.1x. l/r/m: mod_rate <5%. HEAD+TERM jointly gate modifier palette. |
| 1485 | TERMINAL HEAD affinity partition | 2 | B, MIDDLE, atom, terminal, HEAD, affinity, partition, frame | e->y: 72.7% (2.40x, 3,475 tokens). a->n: 59.3% (4.44x). a->m: 60.2% (4.52x). o->l: 30.3% (2.57x). a->r: 35.0% (2.63x). h: no dominant HEAD (45.6% headless). k/t avoid n,m categorically (0-1 tokens). |
| 1486 | m-terminal line-final closure confirmation | 2 | B, MIDDLE, atom, terminal, m, line-final, closure, C1434 | mean_pos=0.903 (all others <0.52). 73.7% line-final. 87.9% TRANSITION. 10 unique MIDDLEs only. 4.2% suffix rate (OPAQUE). Structural singularity. Confirms C1434-C1439. |
| 1487 | Six-terminal functional taxonomy | 2 | B, MIDDLE, atom, terminal, taxonomy, LOCKED, CHANNELED, DIFFUSE, opacity, orthogonal | Three tiers: LOCKED (r, m: 1-2 cats), CHANNELED (l, y, n: 3-4 cats), DIFFUSE (h, bare: 5-6 cats). Opacity orthogonal: r SEMI but LOCKED, h TRANSPARENT but DIFFUSE. Hazard axis: y sources 90.9%, n absorbs 90.9%. Symmetric counterpart to HEAD taxonomy (C1475). |

**Phase 535 findings (TERMINAL Functional Taxonomy, 12 analyses):**
- T1: Category profile. r=FLOW 98.9%, m=TRANSITION 87.9%, l=STAGING 64.5%, y=OPERATION 40.6%, n=TRANSITION 39.3%, h=6 categories.
- T2: Opacity confirmation. m=4.2%, n=0.4%, y=0.3% (OPAQUE). l=17.1%, r=19.3% (SEMI). h=98.7%, bare=89.0% (TRANSPARENT).
- T3: HEAD compatibility. e->y 3,475 tokens (72.7%). a->n/m 59-60%. k/t avoid n,m categorically (0-1 each).
- T4: Modifier exclusivity. n takes ONLY i (8.606x). y takes ONLY d (2.868x). h takes {c,p,f,s}. l/r/m resist mods.
- T5: Hazard. y=90.9% source violations (10/11). n=90.9% target violations (10/11). h/l/m/bare = 0 source.
- T6: Line position. m=0.903 mean (outlier). All others 0.458-0.514. y most initial-biased.
- T7: PREFIX selectivity. r strongly qo/ok/ot (3.5-4.5x). m strongly da (3.8x). n BARE dominated (2.56x).
- T8: Census. y=4,784, n=3,567, h=2,703, l=1,213, m=547, r=1,554, bare=8,728.
- T9: Bare comparison. bare most similar to h (JSD=0.220). Both diffuse multi-category.
- T10: Pairwise distances. Most distant: m vs r (JSD=0.977). Most similar: bare vs h (0.220).
- T11: Determination power. Overall V=0.463. r norm_entropy=0.036 (near-deterministic). h=0.844 (diffuse).
- T12: HEAD x TERM frame matrix. 35 frames characterized, confirming C1448 at full resolution.

---

### Headless Compound Subgrammar (C1488-C1493) -- Phase: HEADLESS_COMPOUND_SUBGRAMMAR (Phase 536)

> **Summary:** Phase 536 characterizes the ~20.5% of Currier B compound MIDDLE tokens whose initial atom is NOT a HEAD atom {a,e,o,k,t}. These "headless" compounds (3,312 tokens, 469 types) form a structurally coherent functional domain (verdict: HEADLESS_IS_COHERENT_DOMAIN). The initial atom acts as a PSEUDO-HEAD with V=0.511 category differentiation: d=CONTAINMENT 84%, i=STAGING 67%, p=MARKING 92%, f=MARKING 91%, r=FLOW 61%, c=OPERATION 32%. Terminal profile shifts systematically: h enriched 2.98x, n enriched 2.45x, while LOCKED tier (r+m) depleted 6.2x -- structural hazard avoidance. PREFIX selectivity is near-absolute: da 2284x enriched, sa/ta exclusive to headless, ok/ot near-absent. Suffix bifurcation: d/i bare (binary ops, <15% suffix) vs c/p/f suffixed (parametric ops, >93%). Same modifier ordering grammar applies (61.9% vs 70.1% compliance). 35.7% of headless types contain HEAD atoms in non-initial positions ("displaced HEAD"). The headless aggregate is categorically distinct from all 5 HEAD domains (nearest: o at JSD=0.302).

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1488 | Headless compound population structure | 2 | B, MIDDLE, headless, population, census, compound | 3,312 tokens (20.5%), 469 types. MOD-initial 77.5% (2,568), TERM-initial 19.3% (638), OTHER 3.2% (106). Top: i=918, d=805, c=612, l=428. Mean length 2.64 atoms. |
| 1489 | Headless pseudo-HEAD category differentiation | 2 | B, MIDDLE, headless, atom, category, pseudo-HEAD, domain | V=0.511, chi2=5872, p=0.0. d=CONTAINMENT 84.0%, i=STAGING 66.9%, p=MARKING 91.7%, f=MARKING 90.9%, r=FLOW 60.7%, c=OPERATION 32.2%. CONTAINMENT 10.6x, THERMAL 0.11x vs headed. |
| 1490 | Headless terminal profile shift | 2 | B, MIDDLE, headless, atom, terminal, profile, enrichment, hazard | h 2.98x (16.2% vs 5.4%), n 2.45x (25.0% vs 10.2%). l 0.076x, r 0.153x, m 0.21x. LOCKED tier 1.7% vs 10.7% (6.2x depletion). C1484 compliance: n=100%, h=99.6%, y=99.6%. |
| 1491 | Headless da-PREFIX near-exclusivity | 2 | B, MIDDLE, headless, PREFIX, da, selectivity, sa, ta | da 2284x enriched (17.8% vs ~0.008%). sa: 197 tokens 100% headless. ta: 107 tokens 100% headless. ok: 0.5% vs 7.5% headed. ot: 0.8% vs 7.2% headed. |
| 1492 | Headless suffix bifurcation | 2 | B, MIDDLE, headless, suffix, bifurcation, binary, parametric | BARE: d=14.9%, i=9.3% (binary ops). SUFFIXED: c=96.2%, p=96.8%, f=93.2% (parametric ops). Aggregate 47.5% vs headed 35.7%. Ordering grammar: 61.9% vs 70.1%. |
| 1493 | Headless internal structure with displaced HEAD | 2 | B, MIDDLE, headless, internal, structure, displaced, HEAD | MT 46.7%, T-only 19.3%, MMT 16.3%, MMMT+ 5.1%. 35.7% contain HEAD atoms in non-initial position. Nearest HEAD: o (JSD=0.302). Farthest: a (JSD=0.665). |

**Phase 536 findings (Headless Compound Subgrammar, 12 analyses):**
- T1: Census. 3,312 headless tokens (20.5%), 469 types. MOD-initial 77.5%, TERM-initial 19.3%.
- T2: Terminal shift. h 2.98x, n 2.45x enriched. r 0.153x, l 0.076x depleted. LOCKED 6.2x depletion.
- T3: C1484 compliance. n=100% (828/828), h=99.6% (535/537), y=99.6% (772/775).
- T4: Modifier distribution. i=27.7%, d=24.3%, c=18.5% dominant.
- T5: Category. V=0.511. d=CONTAINMENT 84%, i=STAGING 67%, p=MARKING 92%, f=MARKING 91%.
- T6: Hazard. r-terminal 1.4% vs 9.1% (0.153x). LOCKED tier 1.7% vs 10.7%.
- T7: Position. Mean 0.491 vs 0.494. No dramatic headless-specific spatial pattern.
- T8: PREFIX. da 2284x enriched. sa/ta exclusive. ok/ot near-absent.
- T9: Suffix. d/i bare (<15%) vs c/p/f suffixed (>93%). Binary vs parametric split.
- T10: JSD to HEADs. o=0.302, k=0.327, e=0.373, t=0.618, a=0.665.
- T11: Internal structure. MT 46.7% dominant. 35.7% displaced HEAD atoms.
- T12: Length. Mean 2.64 atoms (headless) vs 2.75 (headed). Practically similar.

---

### Displaced HEAD Grammar (C1494-C1498) -- Phase: DISPLACED_HEAD_GRAMMAR (Phase 537)


> **Summary:** Phase 537 resolves C1493's finding that 35.7% of headless compound MIDDLEs contain HEAD atoms {a,e,o,k,t} at non-initial positions. The verdict is HEAD_SET_CHARACTER_NOT_FUNCTIONING_AS_HEAD: displaced HEAD-set atoms are NOT functioning as domain selectors. The pseudo-HEAD (first atom) predicts category 2.68x better than the displaced HEAD (35.1% vs 13.1%, N=1,084). 0/5 displaced HEADs match their canonical category dominant. k/t are enriched 5.3x/6.9x (functioning as TERMINALS per C1478), e is depleted 0.26x (almost never terminal). c-modifier is the primary displacement context (87.1%), with ck/ct as the structural backbone. Suffix rate is extreme (89.8% vs 24.0% genuine headless). n/y-terminals categorically exclude displacement (0.36-0.39% rate). There is no alternative MOD+HEAD+TERM compositional order -- the headless domain is genuinely headless.

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1494 | Displaced HEAD k/t enrichment with inverted frequency | 2 | B, MIDDLE, headless, displaced, HEAD, k, t, e, frequency, inversion | k 5.31x enriched (42.0% vs 7.9% canonical), t 6.90x (18.5% vs 2.7%), e 0.26x depleted (12.2% vs 47.8%). 1,182 tokens, 334 types. Maps to k/t dual-role (C1478). |
| 1495 | HEAD-set atoms do not function as domain selectors when displaced | 2 | B, MIDDLE, headless, displaced, HEAD, category, pseudo-HEAD, domain, prediction | Pseudo-HEAD accuracy 35.1% vs displaced HEAD 13.1% (2.68x ratio). 0/5 match canonical dominant. Same-pseudo-HEAD JSD=0.510 < same-HEAD JSD=0.529. No alternative MOD+HEAD+TERM order. |
| 1496 | c-modifier primary displacement context | 2 | B, MIDDLE, headless, displaced, HEAD, c-modifier, k, t, ck, ct, context | c-initial 87.1% displacement rate (533/612). c+k=365, c+t=167. Dominant MIDDLEs: ck=197, ckh=127, ct=95, cth=49. i-initial only 2.3%. c's modifier-terminal affinity (h-compatible) vs i's (n-exclusive) explains split. |
| 1497 | Displaced HEAD extreme suffix rate | 2 | B, MIDDLE, headless, displaced, HEAD, suffix, rate, morphology | 89.8% suffix rate vs canonical 35.7% (2.51x) vs genuine headless 24.0% (3.74x). k-displaced 96.8%, t 95.4%. Driven by bare-terminal transparency (C1440). PARAMETRIC not BINARY (C1492). |
| 1498 | n/y-terminal categorical displacement exclusion | 2 | B, MIDDLE, headless, displaced, HEAD, terminal, n, y, bare, exclusion, gate | n 0.36% (3/828), y 0.39% (3/775) displacement rate. bare 83.9% (908/1082). 200x+ range. n/y exclusive modifier partnerships (C1484) leave no slot for HEAD atoms. |

**Phase 537 findings (Displaced HEAD Grammar, 12 analyses):**
- T1: Census. 1,182 displaced-HEAD tokens (35.7% of headless), 334 types. k=42.0%, t=18.5%, o=14.6%, a=12.6%, e=12.2%.
- T2: Preceding context. M(modifier) 52.0%, T(terminal) 32.7%, H(HEAD) 9.6%. c=38.5% dominant preceding atom.
- T3: Patterns. MH 28.9%, MHT 16.4%, TH 12.3%. 125 unique patterns. H-final 50.3%.
- T4: HEAD enrichment. k 5.31x, t 6.90x enriched. e 0.26x, a 0.54x depleted. Inverted vs canonical.
- T5: Category. JSD displaced vs canonical 0.347. JSD displaced vs genuine 0.345. 0/5 same dominant.
- T6: PREFIX. Displaced closer to canonical (JSD=0.378) than genuine headless (JSD=0.410). ch/sh/qo dominated.
- T7: Position. Mean displaced 0.512, canonical 0.498, genuine 0.504. Not significant (p=0.187).
- T8: Hazard. Displaced 0.08% high-frame vs 28.9% canonical. Categorically safe.
- T9: Suffix. Displaced 89.8% vs canonical 35.7% vs genuine 24.0%. Strongest morphological signature.
- T10: Predictors. c=87.1%, i=2.3% displacement rate. bare-terminal 83.9%, n/y <0.4%.
- T11: Category prediction. Pseudo-HEAD 35.1% vs displaced HEAD 13.1% (2.68x). PSEUDO_HEAD_DOMINATES.
- T12: Detailed comparison. 0/5 HEAD matches. 3/10 pseudo-HEAD matches. Pseudo controls category.

---

### Cross-Layer Atom Decomposition (C1499-C1505) -- Phase: CROSS_LAYER_ATOM_DECOMPOSITION (Phase 538)

> **Summary:** Phase 538 tests whether the HEAD+MOD*+TERM atom grammar (C1393-C1394) is manuscript-wide or B-local, and whether bridge and dark pipeline MIDDLEs differ at atom-level slot composition. 10 tests across 7 pipeline channels: bridge (85), dark (300), a_exclusive (579), b_only (900), all_A (972), all_B (1293), all_AZC (617). Verdict: SHARED_SUBSTRATE_GRADED_SLOTS -- the atom grammar is manuscript-wide (minimum pairwise atom Jaccard 0.895, modifier JSD < 0.007 between non-bridge channels). Channels differentiate through slot PROPORTIONS, not slot INVENTORIES. Bridge is the systematic outlier across all three slot dimensions (HEAD, TERMINAL, MODIFIER), reflecting its unique dual-system role as dynamical backbone. Dark pipeline uses the same atoms in identification-optimized proportions: o-HEAD dominant (28.7% vs bridge 16.5%), bare/h-terminal dominant (74.7%/15.7%), full modifier complement. AZC shows strongest o-HEAD enrichment (31.8%, 2.70x vs B baseline). Bridge MIDDLEs undergo dramatic morphological redistribution between A and B contexts (suffix -edy ~50x B-enriched, PREFIX ct ~12x A-enriched). Predictions: 4/5 confirmed (P3 FAIL: dark prefers bare+DIFFUSE, not CHANNELED terminals).

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1499 | Atom ontology manuscript-wide shared substrate | 2 | GLOBAL, MIDDLE, atom, substrate, cross-system, Jaccard | Min pairwise Jaccard 0.895. HEAD JSD mean 0.0197 between non-bridge channels. All 7 channels share 18 core atoms. MOD JSD < 0.007. |
| 1500 | Bridge-dark HEAD domain differentiation | 2 | B, A->B, MIDDLE, atom, bridge, dark, HEAD, differentiation | Bridge e/k/t 37.6% vs dark 31.0%. Dark o+headless 63.3% vs bridge 51.8%. HEAD JSD bridge-dark: 0.0237. Bridge = balanced execution; dark = arrangement/identification. |
| 1501 | Bridge terminal tier outlier | 2 | B, A->B, MIDDLE, atom, bridge, terminal, tier, outlier | Bridge LOCKED 8.2%, CHANNELED 23.5%, bare 58.8%. Dark bare 74.7%, DIFFUSE/h 15.7%. TERM JSD bridge-to-others 0.039-0.082 (5-20x non-bridge). Dark uses transparent terminals for identification. |
| 1502 | AZC o-HEAD domain enrichment (2.70x) | 2 | AZC, MIDDLE, atom, o-HEAD, enrichment, arrangement | o-HEAD 31.8% vs 11.8% B baseline (2.70x). k-HEAD 0.314x, t-HEAD 0.488x depleted. Extends C1381 to type level. AZC = arrangement-dominated, execution-depleted. |
| 1503 | Bridge atom redistribution across A/B | 2 | GLOBAL, A->B, MIDDLE, atom, bridge, redistribution, suffix, PREFIX | Same 85 bridge MIDDLEs wrapped differently: -edy ~50x B-enriched, ct ~12x A-enriched, qo ~2x B-enriched. HEAD JSD A-vs-B weighted: 0.0767. |
| 1504 | Modifier grammar universality across channels | 2 | GLOBAL, MIDDLE, atom, modifier, universality, cross-system | All channels same 6 modifiers {p,c,i,f,d,s}. c dominant everywhere. MOD JSD non-bridge < 0.007. Bridge outlier at 0.074-0.088 (lower rate 77.7%, f absent). |
| 1505 | Dark pipeline MARKING-dominant category profile | 2 | B, A->B, MIDDLE, atom, dark, pipeline, category, MARKING, bridge, balanced | Bridge balanced V=0.4427 across 8 categories. Dark MARKING-dominant 36.0%, FLOW 20.2%, TRANSITION depleted 2.1%. Confirms C1264 at atom level. |

**Phase 538 findings (Cross-Layer Atom Decomposition, 10 analyses):**
- T-a: HEAD domain profiles. Bridge enriched in executable HEADs e/k/t (37.6%) vs dark (31.0%). Dark enriched in o-HEAD (28.7% vs 16.5%, 1.74x). AZC strongest o-HEAD (31.8%, 2.70x).
- T-b: Terminal tier profiles. Bridge is TERM outlier (LOCKED 8.2%, CHANNELED 23.5%, bare 58.8%). Dark prefers bare (74.7%) + DIFFUSE/h (15.7%). TERM JSD bridge-to-others: 0.039-0.082.
- T-c: Modifier profiles. All channels use same 6 modifiers. c dominant everywhere. MOD JSD between non-bridge: 0.002-0.007. Bridge outlier (0.074-0.088).
- T-d: Headless rates. Bridge 35.3%, dark 34.7% -- virtually identical. A-exclusive highest 44.7%. AZC lowest 25.9%.
- T-e: Category stability. Bridge balanced V=0.4427. Dark MARKING-dominant 36.0% with FLOW 20.2%, depleted TRANSITION 2.1%.
- T-f: Bridge redistribution. Same MIDDLEs undergo dramatic morphological redistribution A vs B. -edy ~50x B-enriched, ct ~12x A-enriched. HEAD JSD=0.0767.
- T-g: AZC HEAD enrichment. o-HEAD 2.70x, k-HEAD 0.314x, t-HEAD 0.488x. Confirms C1381, extends to type level.
- T-h: JSD matrices. Bridge outlier in all three (HEAD, TERM, MOD). Non-bridge cluster tightly.
- T-i: Compound depth. Bridge mean 2.27 atoms (simplest). Dark 3.33, a_exclusive 4.52, b_only 4.50.
- T-j: Atom Jaccard similarity. Min pairwise 0.895. All channels share same 18-atom core.

---

### Bridge Atom Stability Across A and B (C1506-C1509) -- Phase: BRIDGE_ATOM_STABILITY (Phase 539)

> **Summary:** Phase 539 tests whether the 85 bridge MIDDLEs preserve atom-role behavior across Currier A and Currier B. 11 tests (T1-T11) plus a 10-prediction scorecard. Each bridge MIDDLE decomposed via HEAD+MOD*+TERM into slot dimensions. Token collections from A (9,391) and B (19,998) compared at each slot dimension plus PREFIX/SUFFIX ecology, category profiles, and per-atom behavioral correlations. Verdict: PARTIAL_STABILITY -- internal structure preserved (mean JSD 0.046), deployment channels shifted (mean JSD 0.113). TERMINAL is the most stable slot (JSD=0.014), HEAD the least stable (JSD=0.077). Categories are INTRINSIC (100% match rate, same category for same MIDDLE in both systems) but token-weighted distribution shifts: THERMAL +10.1pp in B, STAGING -11.1pp in B. A is o-HEAD/HEADLESS dominant (arrangement); B is e/k-HEAD dominant (execution). Individual atoms partition into three behavioral stability tiers: 8 stable (r/s/t/l/a/m/o/g, corr>0.90), 6 moderate (k/c/p/i/e/n, corr 0.70-0.90), 3 unstable (y/h/d, corr<0.70). d is extreme outlier (corr=0.062). Predictions: 5/10 confirmed.

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1506 | Bridge terminal atom stability across A and B | 2 | GLOBAL, A->B, MIDDLE, atom, bridge, terminal, stability, cross-system | TERMINAL JSD=0.014, most stable slot. Tier JSD=0.005. y-terminal 1.54x B-enriched, h-terminal 0.54x. All 7 terminals shared. |
| 1507 | Bridge HEAD redistribution A vs B | 2 | GLOBAL, A->B, MIDDLE, atom, bridge, HEAD, redistribution, arrangement, execution | A: HEADLESS 38.6%, o 28.1%. B: e 31.1%, k 14.2%. HEAD JSD=0.077, least stable internal slot. A-enriched vs B-enriched population HEAD JSD=0.591. |
| 1508 | Bridge category redistribution A vs B | 2 | GLOBAL, A->B, MIDDLE, atom, bridge, category, redistribution, THERMAL, STAGING | 100% category match (intrinsic). Token-weighted shift: THERMAL +10.1pp B, STAGING -11.1pp B. Category JSD=0.037. e-HEAD most unstable per-HEAD (JSD=0.166). |
| 1509 | Three-tier atom behavioral stability across A and B | 2 | GLOBAL, A->B, MIDDLE, atom, behavioral, stability, correlation, cross-system | 8 stable (corr>0.90: r/s/t/l/a/m/o/g), 6 moderate (0.70-0.90: k/c/p/i/e/n), 3 unstable (<0.70: y/h/d). d=0.062 extreme outlier. Mean=0.789. |

**Phase 539 findings (Bridge Atom Stability, 11 analyses):**
- T1: Frequency redistribution. All 85 bridges in both systems. 30 A-enriched, 52 B-enriched, 3 balanced. Extremes: hy 0.077x, edy 277x, k 6.2x.
- T2: Slot stability ranking. TERMINAL 0.014 > CATEGORY 0.037 > MODIFIER 0.048 > HEAD 0.077. Internal mean 0.046 vs external mean 0.113 (2.4x ratio).
- T3: HEAD redistribution. A: HEADLESS+o dominant (66.7%). B: e+k dominant (45.3%). HEAD JSD A-enriched vs B-enriched = 0.591.
- T4: Category intrinsicness. 100% match rate (same MIDDLE same category in both systems). Token-weighted JSD=0.037. THERMAL +10.1pp, STAGING -11.1pp.
- T5: Per-HEAD category stability. o-HEAD JSD=0.004 (most stable), e-HEAD JSD=0.166 (most unstable, driven by edy 277x B-enrichment).
- T6: PREFIX ecology. JSD=0.072, cosine=0.919. All PREFIXes shared except pe (1 B-only token). More similar than expected.
- T7: SUFFIX ecology. JSD=0.153. Driven by -edy 50x B-enrichment. Most divergent external dimension.
- T8: Terminal tier preservation. Tier JSD=0.005. Three-tier taxonomy (LOCKED/CHANNELED/DIFFUSE) preserved across systems.
- T9: Terminal atom detail. y-terminal 1.54x B-enriched, h-terminal 0.54x (A-enriched). m-terminal 0.69x, r-terminal 0.80x.
- T10: Atom behavioral tiers. 8 stable, 6 moderate, 3 unstable. Structural atoms (r/s/t/l/a/m/o) system-invariant; operational atoms (k/e/h) and boundary atoms (d/y) system-sensitive.
- T11: Cross-system top-category agreement. 10/17 atoms same top category in both systems. 7 mismatches in Tier 2-3 atoms.

---

### Suffix Atom Taxonomy (C1510-C1515) -- Phase: SUFFIX_ATOM_TAXONOMY (Phase 540)

> **Summary:** Phase 540 decomposes the suffix layer at atom-level resolution using CategoryClassifier (8 categories) and morphological decomposition. 12 analyses (T1-T12) on 11,151 suffixed B tokens (35 unique suffixes, 13 single-char atoms). Verdict: suffix is a PARALLEL compositional domain -- same HEAD+TERM grammar as MIDDLE, but with compressed inventory (13 vs 18 atoms, missing k/t ACTION HEADs and p/f/c EXECUTIVE MODs), attenuated HEAD category selectivity (V=0.277, 53% of MIDDLE HEAD's 0.520), and amplified TERM positional signal (R2=0.059, 1.68x MIDDLE TERM). MIDDLE terminal atom dominates suffix content selection (V=0.513, 1.68x stronger than MIDDLE HEAD at V=0.305). ALL 12 shared atoms carry DIFFERENT category information in suffix vs MIDDLE position (mean JSD=0.526; e most stable 0.202, n most divergent 1.000). Cross-system suffix atom inventory is IDENTICAL (A=B=13 atoms, JSD=0.050); B enriches execution atoms (d,e,i), A enriches arrangement atoms (o,h,l,s). Suffix modes confirmed at full 8-category resolution: Mode A = THERMAL/MONITORING/OPERATION/CONTAINMENT (medial), Mode B = FLOW/STAGING/TRANSITION (boundary-biased).

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1510 | Suffix parallel HEAD+TERM decomposition | 2 | B, suffix, atom, decomposition, HEAD, TERM, parallel | First-atom V=0.277 (53% of MIDDLE HEAD 0.520), last-atom R2=0.059 (1.68x MIDDLE TERM 0.035). 5 terminal atoms only: y 53.5%, n 19.5%, r 13.1%, l 10.8%, m 3.1%. m-terminal 7.89x line-final. |
| 1511 | Suffix excludes ACTION HEAD and EXECUTIVE MOD atoms | 2 | B, suffix, atom, missing, HEAD, MOD, exclusion | Missing {k,t} = 2 ACTION HEADs + {p,f,c} = 3 EXEC MODs. All 5 also 0 TERMINAL in MIDDLE. Suffix is systematically action-free and executive-free. |
| 1512 | MIDDLE terminal dominates suffix content (V=0.513) | 2 | B, MIDDLE, suffix, atom, terminal, gating, content | V(MIDDLE TERM x suffix first-atom) = 0.513 vs V(MIDDLE HEAD) = 0.305 (1.68x). h-terminal: 98.7% suffix, e-first 59.4%. r-terminal: a-first 72.8%. l-terminal: o-first 36.9%. |
| 1513 | Suffix atoms universally divergent from MIDDLE atoms | 2 | B, suffix, MIDDLE, atom, behavioral, divergence, JSD | 12/12 atoms divergent, mean JSD=0.526. Most stable: e (0.202). Most divergent: n (1.000, TRANSITION->FLOW inversion). Same alphabet, different category semantics. |
| 1514 | Cross-system suffix atom identity (A=B=13, JSD=0.050) | 2 | GLOBAL, suffix, atom, cross-system, identity | A=B=13 atoms, 0 exclusive. B enriches d (0.50x), e (0.41x), i (0.35x). A enriches o (3.31x), h (1.71x), l (1.67x), s (2.01x). Extends C1499 to suffix. |
| 1515 | Suffix mode category anatomy with positional asymmetry | 2 | B, suffix, mode, category, positional, THERMAL, FLOW | Mode A: MONITORING 5.08x, CONTAINMENT 2.93x, OPERATION 2.95x, THERMAL 1.20x; medial (0.491). Mode B: FLOW 2.13x, STAGING 2.15x, TRANSITION 2.17x; boundary (0.514). |

**Phase 540 findings (Suffix Atom Taxonomy, 12 analyses):**
- T1: Census. 11,151 suffixed tokens (48.3%), 35 unique suffixes, top: -edy (1972), -dy (1000), -aiin (949). Atom-lengths: 1-atom 14.7%, 2-atom 51.7%, 3-atom 33.6%.
- T2: Inventory. 13 atoms in suffix, missing {c,f,k,p,t}. 3 doubled: ee, ii, oo. All 5 missing have 0 TERMINAL in MIDDLE.
- T3: First-atom category. V=0.277 (53% of MIDDLE HEAD 0.520). Top: a (36.1% THERMAL-dom), e (26.7% THERMAL-dom), d (10.5% OPERATION-dom).
- T4: Last-atom position. R2=0.059 (1.68x MIDDLE TERM). 5 terminals: y 53.5%, n 19.5%, r 13.1%, l 10.8%, m 3.1%. m: mean pos 0.924, 7.89x final.
- T5: PARALLEL_DECOMPOSITION verdict. First=category (V>last), last=position (R2>first). Ratios >1.3x on both axes.
- T6: MIDDLE HEAD -> suffix first-atom. V=0.305. k-HEAD: a-first (1109), e-first (921). e-HEAD: a-first (735), e-first (705).
- T7: MIDDLE TERMINAL -> suffix first-atom. V=0.513 (1.68x HEAD). h-term 98.7% suffix (e-first 59.4%). y-term 1.6%, n-term 0.8%.
- T8: Mode A (N=5676): THERMAL 42.9%, MONITORING 5.8%, OPERATION 14.8%, CONTAINMENT 5.5%. Mode B (N=5454): FLOW 22.7%, STAGING 11.4%, TRANSITION 8.8%.
- T9: Missing atoms = 2 ACTION HEADs {k,t} + 3 EXEC MODs {p,f,c}. Suffix = action-free, executive-free.
- T10: A=B=13 atoms, JSD=0.050. B enriches e/i/d (execution). A enriches o/h/l/s (arrangement).
- T11: All 12 atoms divergent MIDDLE vs suffix. Mean JSD=0.526. Most stable: e (0.202). Most divergent: n (1.000).
- T12: Suffix atom pairwise JSD. Mean=0.108. Closest: ii-l (0.005). Most distant: ee-h (0.416). h maximally isolated.

### AZC Zone-Level Atomization (C1516-C1522) -- Phase: AZC_ZONE_ATOMIZATION (Phase 541)

> **Summary:** Phase 541 tests whether AZC internal zones differentiate at HEAD+MOD*+TERM slot level (C1394), given that C1271 found null at raw atom level using AXIS clusters (C1207). 12 tests on 3,227 AZC tokens decomposed into HEAD/MOD/TERM slots. Key finding: HEAD domain differentiation IS significant (chi2=112.3, V=0.115, p=5.81e-17) -- zones differ in domain selection, not raw character inventory. o-HEAD enrichment is zone-graded (R=17.7% to S=29.3%, vs B=11.8%). HEAD is 5.2x more discriminating than TERMINAL across zones. AZC zones partition into B-proximate (R, P -- lower o-HEAD, more bridge) and A-proximate (C, S, L -- higher o-HEAD, more dark/exclusive). R-series shows no HEAD gradient. Zodiac HEAD is uniform; A/C is 2.0x more internally diverse.

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1516 | AZC HEAD domain differentiation across zones | 2 | AZC, zone, HEAD, atom, differentiation, V=0.115, C1271-refinement, C1394 | chi2=112.3, V=0.115, p=5.81e-17 across 4 major zones. Refines C1271: differentiation at HEAD slot, not raw character level. |
| 1517 | o-HEAD enrichment is zone-graded not uniform | 2 | AZC, zone, o-HEAD, graded, arrangement, C1502, C1381, C1388 | R=17.7% (1.51x B), P=19.1% (1.63x), C=26.2% (2.23x), S=29.3% (2.49x), L=30.9% (2.63x). Overall 1.90x B at HEAD-slot level. |
| 1518 | HEAD differentiation dominates TERMINAL across zones | 2 | AZC, zone, HEAD, TERMINAL, JSD, domain-selection, C1487, C1501 | Mean pairwise HEAD JSD=0.0254, TERMINAL JSD=0.0049. HEAD 5.2x more discriminating. Zones select WHAT domain, not HOW to close. |
| 1519 | Zodiac HEAD uniformity vs A/C internal diversity | 2 | AZC, family, zodiac, AC, HEAD, diversity, C436, C1270 | Between-family HEAD JSD=0.0158. Internal: Zodiac=0.0617, A/C=0.1265 (2.0x ratio). Extends C436 to atom level. |
| 1520 | R-series no HEAD gradient | 2 | AZC, R-series, HEAD, gradient, null, R4-anomalous, C434 | All Spearman p=0.600 (N=4). R1-R3 stable (JSD 0.001-0.009). R4 anomalous (N=39, 51.3% headless) but underpowered. |
| 1521 | AZC zone pipeline composition varies | 2 | AZC, zone, pipeline, bridge, dark, exclusive, o-HEAD, C1139, C1272, C1500, C1505 | S-zone most dark/exclusive (16.8%/21.4%). P-zone most bridge (80.4%). Dark MIDDLEs 1.84x o-HEAD vs bridge across all zones. |
| 1522 | AZC zones partition B-proximate vs A-proximate by HEAD JSD | 2 | AZC, zone, HEAD, JSD, B, A, proximity, partition, C301, C1507, C1517 | R/P closer to B (JSD 0.029-0.042). C/S/L closer to A (JSD 0.036-0.084). B-proximate = lower o-HEAD + more bridge. |

**Phase 541 findings (AZC Zone-Level Atomization, 12 analyses):**
- T1: Zone census. 3,227 tokens (H-track, cleaned). R=1326 (41.1%), C=629 (19.5%), S=501 (15.5%), P=397 (12.3%), L=68 (2.1%), OTHER=306 (9.5%).
- T2: HEAD profiles. chi2=112.3, V=0.115, p=5.81e-17. Refines C1271 null: differentiation at HEAD slot, not raw character level.
- T3: TERMINAL profiles. Stable across zones (bare ~50%). No zone differentiation at TERMINAL level.
- T4: Modifier profiles. AZC s-modifier 2.44x B, d-modifier 0.60x B. S-zone highest modifier load (138.7%).
- T5: Headless rates. Zone-uniform (21-33%), close to B (27.2%). P highest (33.0%), S lowest (21.2%).
- T6: Zodiac vs A/C. Between-family HEAD JSD=0.0158. A/C internal diversity 2.0x Zodiac. Extends C436 to atom level.
- T7: R-series. No gradient (all Spearman p=0.600, N=4). R1-R3 stable (JSD 0.001-0.009). R4 anomalous (N=39, 51.3% headless).
- T8: HEAD vs TERMINAL. Mean pairwise HEAD JSD=0.0254, TERMINAL JSD=0.0049. HEAD 5.2x more discriminating across zones.
- T9: Pipeline by zone. S-zone most dark/exclusive (16.8%/21.4%). P-zone most bridge (80.4%). Dark MIDDLEs 1.84x o-HEAD vs bridge.
- T10: System proximity. R/P closer to B (JSD 0.029-0.042). C/S/L closer to A (JSD 0.036-0.084). AZC overall near-equidistant.
- T11: Labels vs P-text. HEAD JSD=0.029. Labels more o-HEAD (30.9% vs 19.1%), less k-HEAD (1.5% vs 6.0%).
- T12: o-domain deep dive. o as HEAD 22.4% (1.90x B). Zone-graded: R=17.7%, P=19.1%, C=26.2%, S=29.3%, L=30.9%. o as TERM=0.0%.

---

### Headless Cross-System Distribution (C1523-C1527) -- Phase: HEADLESS_CROSS_SYSTEM (Phase 542)

> **Summary:** Phase 542 tests whether headless compound properties documented in B (C1488-C1498) are universal across Currier A, Currier B, and AZC. 10 tests (T1-T10) on 37,497 tokens (A=11,174, B=23,096, AZC=3,227). Key findings: A has 1.43x higher headless rate than B/AZC (39.0% vs 27.2%/27.9%, chi2=504.49, C1523); B and AZC are statistically indistinguishable. da/sa/ta PREFIX exclusivity is UNIVERSAL (da enrichment A=844.6x, B=1,448.3x, AZC=132.7x, C1524). Headless suffix rate is LOWER than headed in all systems (A=0.73x, B=0.86x, AZC=0.61x, C1525). Category profile is near-identical cross-system (THERMAL 0.6-1.1%, STAGING 30.9-35.2%, cross-system JSD=0.023-0.035 vs within-system 0.226-0.317, C1526). 69 triple-shared headless types cover 88-89% of tokens despite 63-68% type exclusivity (C1527). B-specific dark headless enrichment (1.47x) does not hold in A or AZC. Verdict: headless is a MANUSCRIPT-WIDE structural domain following SHARED_SUBSTRATE_GRADED_SLOTS architecture (C1499).

| # | Constraint | Tier | Tags | Details |
|---|-----------|------|------|---------|
| 1523 | Currier A headless rate 1.43x higher than B/AZC | 2 | GLOBAL, cross-system, headless, A, B, AZC, HEAD, rate, enrichment, C1488, C1507, C1519 | A=39.0%, B=27.2%, AZC=27.9%. A vs B chi2=487.73, p=4.44e-108. B vs AZC p=0.428 (NS). A pseudo-HEAD: i-dominant (21.3%). B: l/d-dominant (20.4%/18.2%). |
| 1524 | da/sa/ta PREFIX exclusivity universal across systems | 2 | GLOBAL, cross-system, headless, PREFIX, da, sa, ta, exclusivity, universal, C1491, C1394 | da enrichment: A=844.6x, B=1,448.3x, AZC=132.7x. sa >98.2% headless, ta >94.4% headless in all systems. Manuscript-wide grammar rule. |
| 1525 | Headless suffix depletion universal across systems | 2 | GLOBAL, cross-system, headless, suffix, rate, depletion, universal, C1440, C1490, C1492 | A=0.73x headed, B=0.86x, AZC=0.61x. All p<1e-22. AZC strongest effect. Terminal opacity mechanism (C1440). |
| 1526 | Headless category profile universal across systems | 2 | GLOBAL, cross-system, headless, category, THERMAL, STAGING, MARKING, universal, C1488, C1489, C1505 | THERMAL: A=0.8%, B=1.1%, AZC=0.6%. STAGING: A=35.2%, B=30.9%, AZC=32.4%. Cross-system JSD=0.023-0.035, 6.7-13.8x smaller than within-system. |
| 1527 | Headless functional core shared: 69 types cover 88-89% | 2 | GLOBAL, cross-system, headless, MIDDLE, overlap, shared, functional-core, type-exclusive, C1499, C1488 | Types: A=395, B=484, AZC=160. Triple-shared=69. Token coverage=88-89%. A-exclusive=63.3%, B-exclusive=68.0%. B dark headless 1.47x bridge (B-specific). |

**Phase 542 findings (Headless Cross-System Distribution, 10 analyses):**
- T1: Headless rates. A=39.0%, B=27.2%, AZC=27.9%. Omnibus chi2=504.49, p=2.82e-110. A enriched 1.43x. B and AZC indistinguishable (p=0.428).
- T2: Pseudo-HEAD profiles. A: i=21.3% (TRANSITION), y=16.4%. B: l=20.4% (STAGING), d=18.2% (OPERATION). AZC: y=22.1% (OPERATION). Category profiles nearly identical cross-system (JSD=0.023-0.035).
- T3: da/sa/ta universality. da enrichment: A=844.6x, B=1,448.3x, AZC=132.7x. sa headless fraction: A=99.2%, B=99.7%, AZC=98.2%. ta: A=98.6%, B=100%, AZC=94.4%.
- T4: Suffix rates. Headless LOWER than headed in all systems: A=0.73x, B=0.86x, AZC=0.61x. All chi2>92, all p<1e-21.
- T5: AZC zones. Modest variation (V=0.075). S lowest (21.2%), P/L highest (~33%). Not a strong differentiator.
- T6: Pipeline. B: dark 1.47x bridge headless (chi2=114.5, p=1.0e-26). A: dark 0.90x bridge. AZC: dark 0.73x bridge. B-specific dark-headless affinity.
- T7: Terminal profiles. Cross-system headless terminal JSD=0.012-0.038. Universal shifts: bare depleted 0.56-0.58x, n enriched 1.55-3.15x, h enriched 1.36-2.66x.
- T8: Category profiles. Near-zero THERMAL (0.6-1.1%), high STAGING (30.9-35.2%). Cross-system headless JSD 6.7-13.8x smaller than within-system headless-vs-headed JSD.
- T9: MIDDLE length. Headless shorter in all systems. A: 1.93 vs 2.30. B: 1.87 vs 2.33. AZC: 1.71 vs 2.60. All p<1e-92.
- T10: Type overlap. 69 triple-shared types. Token coverage: A=88.0%, B=89.0%, AZC=88.1%. Type exclusivity: A=63.3%, B=68.0%, AZC=39.4%. Jaccard: A&B=0.183.

### Phase 543: Hazard-Class Atomization (HAZARD_CLASS_ATOMIZATION)

| C# | Claim | Tier | Scope | Key Metrics |
|---|-----------|------|------|---------|
| 1528 | Hazard classes map to near-orthogonal atom HEAD territories | 2 | B, MIDDLE, atom, HEAD, TERM, hazard, failure-class, territory, orthogonal, C109, C1446, C1447, C1448, C1475 | PHASE_ORDERING=headless(57.1%), CONTAINMENT_TIMING=o-HEAD(50%), COMPOSITION_JUMP=e-HEAD(50%), RATE_MISMATCH=a-HEAD(100%), ENERGY_OVERSHOOT=e-HEAD(100%). 7/10 pairwise Jaccard=0. |
| 1529 | PHASE_ORDERING is headless y-terminal to a-HEAD transition failure | 2 | B, MIDDLE, atom, HEAD, TERM, hazard, PHASE_ORDERING, headless, y-terminal, a-HEAD, violation, C109, C1397, C1446, C1477, C1528 | 10/11 corpus violations are dy->aiin (PHASE_ORDERING). Source: headless y-terminal (57.1%). Target: a-HEAD n-terminal (57.1%). Cross-domain boundary failure. |
| 1530 | CONTAINMENT_TIMING is l/r-terminal SEMI_TRANSPARENT class with 100% avoidance | 2 | B, MIDDLE, atom, TERM, hazard, CONTAINMENT_TIMING, l-terminal, r-terminal, SEMI_TRANSPARENT, avoidance, C109, C1440, C1447, C1487 | Source 75% l/r-terminal. Target 100% l/r-terminal. 1,129 source appearances, 0 violations (100% avoidance). Strictest class. |
| 1531 | Forbidden MIDDLEs include 5 phantom types absent from corpus | 2 | B, MIDDLE, hazard, forbidden, phantom, construction, grammar, C109, C1178, C1394, C1528, C1529 | shey, chey, chedy, shedy, chol = 0 occurrences. 11/17 transitions involve phantom. Construction-level prohibition. |
| 1532 | Hazard classes partition by line position (setup-early to closure-late) | 2 | B, MIDDLE, hazard, failure-class, line, position, zone, gradient, C109, C1463, C1464, C1465, C1528 | Chi2=46.6, p=0.000079, V=0.066. COMPOSITION_JUMP=0.402, ENERGY_OVERSHOOT=0.473, CONTAINMENT_TIMING=0.510, RATE_MISMATCH=0.551, PHASE_ORDERING=0.581. |
| 1533 | PHASE_ORDERING is CHSH-channel specific (28.4% CHSH, 7/11 violations) | 2 | B, MIDDLE, atom, PREFIX, hazard, PHASE_ORDERING, CHSH, channel, violation, C109, C929, C1449, C1451, C1529 | CHSH=28.4% of PO sources vs 0-12.2% other classes. 7/11 violations CHSH-prefixed. QO=0 violations. Other classes BARE-dominant. |

**Phase 543 findings (Hazard-Class Atomization, 4 test dimensions, 5/7 predictions confirmed):**
- Dimension A (HEAD x TERM frame): Hazard classes occupy near-orthogonal HEAD territories (7/10 pairwise Jaccard=0). PHASE_ORDERING=headless, CONTAINMENT_TIMING=o-HEAD, COMPOSITION_JUMP=e-HEAD, RATE_MISMATCH=a-HEAD, ENERGY_OVERSHOOT=e-HEAD. k-HEAD immunity confirmed universal across all 5 classes.
- Dimension B (modifier quenching): All 5 modifiers {c,d,f,p,s} quench ALL classes to 0%. Only 2 modified forbidden MIDDLEs exist in the entire list (chedy, shedy — both phantoms). Modifier quenching is trivially complete.
- Dimension C (PREFIX channel): PHASE_ORDERING uniquely CHSH-dominant (28.4%). Other classes BARE-dominant (34.5-100%). QO maintains zero participation across all 5 classes. 7/11 corpus violations in CHSH context.
- Dimension D (line position): Classes partition early-to-late (chi2=46.6, p=0.000079). COMPOSITION_JUMP=0.402 (setup), PHASE_ORDERING=0.581 (closure). Gradient is physically coherent.
- Phantom finding: 5 forbidden MIDDLEs (shey, chey, chedy, shedy, chol) have 0 corpus occurrences. 11/17 transitions involve phantoms. Forbidden list partially encodes construction-level prohibitions.
- PHASE_ORDERING anatomy: 10/11 corpus violations are dy->aiin. Headless y-terminal to a-HEAD n-terminal = cross-domain boundary failure at closure. Concentrates in CHSH sensory checkpoint context.
- CONTAINMENT_TIMING: Strictest class — 1,129 source appearances, 0 violations. l/r SEMI_TRANSPARENT terminals. Grammar enforces absolute avoidance.

### Phase 544: PREFIX Atom Taxonomy (PREFIX_ATOM_TAXONOMY)

| C# | Claim | Tier | Scope | Key Metrics |
|---|-----------|------|------|---------|
| 1534 | PREFIX uses 15 characters in three-tier positional classification identical across all systems | 2 | GLOBAL, PREFIX, atom, positional, inventory, three-tier, MODIFIER, BASE, DUAL, C1218, C1499 | 15 chars: 7 MODIFIER {c,d,f,p,q,s,y}, 2 BASE {e,h}, 6 DUAL {a,k,l,o,r,t}. Cross-system Jaccard=1.000. Positional chi2=14,327.8, V=0.547. |
| 1535 | i-atom categorically excluded from PREFIX — iteration absent from channel selection | 2 | GLOBAL, PREFIX, MIDDLE, atom, i-atom, exclusion, iteration, C1197, C1204, C1394, C1499, C1511 | PREFIX uses 15 of MIDDLE's 20 chars, excluding {i,m,n,g,x}. i is the ONLY MIDDLE MOD absent from PREFIX. PREFIX-MIDDLE Jaccard=0.750. |
| 1536 | Base-to-HEAD selection V=0.478 — each base selects a distinct operational domain | 2 | GLOBAL, PREFIX, atom, base, HEAD, domain, V=0.478, C1218, C1219, C1475, C1507 | Chi2=21,946.2, V=0.478 (89% of C1475 V=0.511). o→THERMAL(k 57%), h→STABILITY(e 66%), a→HEADLESS(96%), k/t→STABILITY+CONTAINMENT. |
| 1537 | a-base is the universal headless gateway (94-96% headless regardless of modifier) | 2 | GLOBAL, PREFIX, atom, base, a-base, headless, gateway, modifier-independent, C1488, C1491, C1524, C1536 | da=95.9%, sa=96.0%, ka=94.5%, ta=95.8%. Spread=1.5pp. Generalizes C1491 from da to entire a-base family. |
| 1538 | q-modifier uniquely activates THERMAL channel on o-base (64% k-HEAD vs 5-19% other modifiers) | 2 | B, PREFIX, atom, modifier, q, o-base, THERMAL, k-HEAD, compositional, qo, C1300, C1313, C1536, C1537 | qo=64.0% k-HEAD, so=18.5%, to=15.7%, po=8.1%, do=4.8%. 3.5x gap. o-base is modifier-SENSITIVE (75pp spread). qo is compositionally transparent. |
| 1539 | Sister pairs decompose into SAME_BASE (ch/sh, da/sa) and SAME_MOD (ok/ot) structural types | 2 | GLOBAL, PREFIX, atom, sister-pair, ch, sh, ok, ot, da, sa, SAME_BASE, SAME_MOD, C408, C1478, C1534, C1536 | All HEAD JSD<0.01 (content-equivalent). ch/sh non-content divergence: suffix 12.3pp, articulator 9.3pp. ok/ot and da/sa: near-identical on all dimensions. |

**Phase 544 findings (PREFIX Atom Taxonomy, 13 analysis steps, 8 key findings):**
- PREFIX inventory: 15 characters, identical across A/B/AZC (Jaccard=1.000). Three-tier positional classification: MODIFIER (POS-0 only: c,d,f,p,q,s,y), BASE (POS-1+ only: e,h), DUAL (both positions: a,k,l,o,r,t). Extends C1218 with positional chi2=14,327.8, V=0.547.
- Cross-slot exclusion: PREFIX excludes {i,m,n,g,x} from MIDDLE. i is the only MIDDLE MOD atom absent from PREFIX — iteration is MIDDLE-internal, not channel-selectable. Suffix excludes {k,t,p,f,c} (C1511). Three slots partition functional information complementarily.
- Base→HEAD domain selection: V=0.478 (89% of C1475 V=0.511). o-base→THERMAL(k), h-base→STABILITY(e), a-base→HEADLESS, k/t-base→STABILITY+CONTAINMENT, l-base→mixed THERMAL/STABILITY, r-base→CONTAINMENT+ARRANGEMENT.
- a-base headless gateway: All a-base PREFIXes (da, sa, ka, ta) produce 94-96% headless. Modifier identity has NO effect (1.5pp spread). Generalizes C1491 da-exclusivity to entire a-base family.
- q-modifier thermal activation: On o-base, q produces 64% k-HEAD (next highest: s at 18.5%, 3.5x gap). Without q, o-base defaults to 65-87% headless. q fundamentally transforms o-base from headless to thermal channel. qo is compositionally transparent.
- Sister pair atom architecture: ch/sh and da/sa are SAME_BASE (shared base, different modifiers). ok/ot is SAME_MOD (shared modifier o, different bases k/t). All HEAD JSD<0.01. SAME_BASE pairs show non-content divergence (ch/sh: suffix 12.3pp, articulator 9.3pp). SAME_MOD pair is near-identical on all dimensions.
- Cross-system substrate: Base distribution nearly identical across A/B/AZC (JSD 0.011-0.046). PREFIX atom grammar is truly manuscript-wide (extends C1499 shared substrate).
- Base×Terminal interaction: chi2=12,798.8, V=0.308. h-base MIDDLEs strongly prefer y-terminal (48.3%), a-base prefers n-terminal (44.1%), o-base distributes across y/l/r. Extends C1485 HEAD×TERM affinity to PREFIX base level.

### Phase 545: Executive Atom Instability (EXECUTIVE_ATOM_INSTABILITY)

| C# | Claim | Tier | Scope | Key Metrics |
|---|-----------|------|------|---------|
| 1540 | p/f/c behavioral non-divergence vs stable MODs | 2 | GLOBAL, atom, cross-system, instability, JSD, behavioral, C1509, C1499 | Mean JSD UNSTABLE=0.0110 vs STABLE_MOD=0.0319, ratio 0.35x. p=0.0074, c=0.0116, f=0.0141. d most divergent at 0.0567. |
| 1541 | Suffix exclusion defines instruction-only atom tier | 2 | GLOBAL, atom, suffix, exclusion, instruction, tier, C1509, C1511, C1540 | {k,t,p,f,c} = 0 suffix occurrences across all systems. Partition: 13 OUTCOME-accessible + 5 INSTRUCTION-ONLY. Exactly equals ACTION HEADs + UNSTABLE MODs. |
| 1542 | c-atom slot-switching between PREFIX and MIDDLE | 2 | B, MIDDLE, PREFIX, atom, c, slot-switching, HEAD, headless, e-HEAD, C1389, C1496, C1542 | PREFIX: 61.0% e-HEAD, 21.2% headless. MIDDLE: 17.9% e-HEAD, 46.4% headless. JSD HIGH. Top MIDDLEs: ck(197), kch(148), ckh(127). |
| 1543 | p/f are o-HEAD arrangement-affiliated atoms | 2 | B, MIDDLE, atom, p, f, o-HEAD, arrangement, headless, C1388, C1502, C1543 | p: 36.6-41.2% o-HEAD (stable A->B). f: 33.0-34.8% o-HEAD. vs i: 3.1-4.1% o-HEAD, 26.5-53.2% a-HEAD. Arrangement vs iteration modifier split. |
| 1544 | Unstable atoms increase Mode A suffix rate A->B | 2 | B, MIDDLE, atom, suffix, mode, UNSTABLE, Mode A, THERMAL, specification, C1509, C1515, C1229 | c +25.3pp (58.2->83.4%), f +22.3pp (32.2->54.4%), p +15.5pp (41.4->56.9%). Stable MODs: i +0.7pp, d -3.4pp. |
| 1545 | f-atom anomalous B-exclusive vocabulary affinity | 2 | B, MIDDLE, atom, f, bridge, dark-pipeline, B-exclusive, vocabulary, rarity, C1139, C1499 | f bridge rate 49.3% (lowest MOD). B-only 50.7%. Only 215 B tokens (rarest MOD, next: s=560). Top: fch(23), ofch(17), f(17). |

**Phase 545 findings (Executive Atom Instability, 9 research questions, 8 analysis dimensions):**
- MAJOR SURPRISE: C1509's "unstable" atoms {p,f,c} have LOWER cross-system behavioral divergence (JSD=0.0110) than "stable" MODs {i,d,s} (JSD=0.0319). Ratio 0.35x. Instability is functional niche specialization, not behavioral divergence.
- Suffix exclusion partition: The 5 suffix-excluded atoms {k,t,p,f,c} exactly equal ACTION HEADs {k,t} + UNSTABLE MODs {p,f,c}. These atoms encode INSTRUCTIONS only; the 13 suffix-accessible atoms can additionally encode OUTCOMES and CONDITIONS.
- c-atom slot-switching: Unique among MOD atoms. In PREFIX position, c selects e-HEAD at 61% (CHSH monitoring channel). In MIDDLE position, c concentrates in headless compounds at 46.4% and distributes broadly across HEAD domains. Explains C1496 displacement context.
- p/f arrangement affiliation: Both 33-41% o-HEAD (arrangement domain, C1388). Contrasts sharply with i at 53% a-HEAD (iteration domain). p/f are ARRANGEMENT modifiers, i is an ITERATION modifier. Different domain affiliations explain different stability profiles.
- Mode A enrichment gradient: All three unstable atoms shift TOWARD Mode A (specification/THERMAL) when moving from A to B. c: +25.3pp, f: +22.3pp, p: +15.5pp. Stable MODs show near-zero shift. B's execution grammar makes unstable atoms MORE specification-oriented.
- f vocabulary anomaly: f has the lowest bridge rate of any MOD atom (49.3% shared, 50.7% B-exclusive). Also the rarest (215 tokens). f disproportionately participates in B's autonomous identification vocabulary (dark pipeline).
- Expert predictions: c parameterization CONFIRMED (slot-switching, arrangement role). p/f register-sensitivity PARTIALLY CONFIRMED (Mode A shift, o-HEAD affiliation). Behavioral divergence prediction INVERTED (less divergent, not more).

---

### Phase 546: Hazard x PREFIX Integration (HAZARD_PREFIX_INTEGRATION)

| C# | Claim | Tier | Scope | Key Metrics |
|---|-----------|------|------|---------|
| 1546 | Universal HEAD atom hazard source immunity | 2 | B, MIDDLE, atom, HEAD, hazard, immunity, universal, source, C1446, C1475, C1476, C1528 | ALL 5 HEADs at 0% source rate: e=0/7002, o=0/2717, a=0/3079, k=0/3100, t=0/921. Total headed: 0/16819. chi2=4411.9, V=0.219. HEADLESS: 1537/6277=24.49%. |
| 1547 | TERMINAL atom determines hazard class type (stronger than HEAD) | 2 | B, MIDDLE, atom, terminal, hazard, class, PHASE_ORDERING, CONTAINMENT_TIMING, y, l, C1447, C1483, C1487, C1528 | chi2=8622.5, V=0.306 (vs HEAD V=0.219, 1.40x). y->PHASE_ORDERING 675/675, l->CONTAINMENT_TIMING 855/855, bare->RATE_MISMATCH 5/5, h->ENERGY_OVERSHOOT 2/2. |
| 1548 | PREFIX base-level hazard differentiation | 2 | B, PREFIX, base, hazard, source, enrichment, C1536, C1475, C1546 | chi2=2038.0, V=0.133. e-base 3.37x (22.4%), a-base 2.00x (13.3%), o-base 1.20x (8.0%), h-base 0.71x (4.7%), k-base 0.30x (2.0%). |
| 1549 | q-modifier hazard protection on o-base (~7x vs other modifiers) | 2 | B, PREFIX, modifier, q, o-base, hazard, protection, qo, C1538, C1546, C1548, C1452 | qo 4.15% (0.52x base) vs do 51.6%, so 28.0%, to 30.4%, po 27.2%, ko 31.3%. Protection via 64% k-HEAD routing (C1538). |
| 1550 | Sister pair hazard source asymmetry | 2 | B, PREFIX, sister pair, hazard, asymmetry, ch, sh, ok, ot, da, sa, C1449, C1539, C1187 | ch/sh 1.804x (ch 4.73% vs sh 2.76%). ok/ot 0.664x INVERTED (ok 6.09% vs ot 9.17%). da/sa 1.537x. da/ta 1.354x. da/ka 1.529x. |
| 1551 | PHASE_ORDERING exclusively headless y-terminal dy; CONTAINMENT_TIMING exclusively l-terminal | 2 | B, MIDDLE, hazard, PHASE_ORDERING, CONTAINMENT_TIMING, headless, y-terminal, l-terminal, dy, l, C1529, C1530, C1547 | dy=675 tokens across 10+ PREFIXes (100% PHASE_ORDERING). l=855 tokens across 12+ PREFIXes (100% CONTAINMENT_TIMING). Both MIDDLE-intrinsic not PREFIX-induced. |
| 1552 | 5/9 hazard source MIDDLEs are phantom types absent from corpus | 2 | B, MIDDLE, hazard, phantom, forbidden, corpus, chey, shey, chedy, shedy, chol, C1531, C1178 | chey=0, shey=0, chedy=0, shedy=0, chol=0. All ch/sh-initial dead naming pattern. 4 corpus-present sources (dy,l,c,he) carry 100% of actual hazard. |
| 1553 | ch/sh-initial compound MIDDLE categorical absence | 2 | B, MIDDLE, atom, ch, sh, compound, positional-partition, PREFIX, C1178, C1394, C1534, C1552 | 0 ch/sh-initial compound MIDDLEs (3+ chars) in entire corpus. PREFIX:MIDDLE ratio 5,821:0. c-initial compounds: 55 types/291 tokens. s-initial: 12/14. ch/sh bigram is PREFIX-domain only. |
| 1554 | Phantom MIDDLEs are atom-legal but construction-dead (defense-in-depth) | 2 | B, MIDDLE, phantom, atom, slot, construction, defense-in-depth, hazard, C1552, C1553, C1178, C1209, C1546 | All 5 phantoms pass atom slot legality, PREFIX compatibility (22-27 each), suffix compatibility. Prohibition at BIGRAM level (C1553) not atom level. Forbidden topology covers vocabulary-excluded MIDDLEs. |
| 1555 | c-initial compound second-atom selectivity (c+h adjacency absent) | 2 | B, MIDDLE, atom, c-initial, h-atom, second-atom, selectivity, C1389, C1553, C1472 | 49/55 c-initial compounds (89.1%) contain h, but h ALWAYS at position 2+ (c+[k/t/f/p]+h). c+h at positions 0-1 = 0 types. Bigram-level prohibition, not atom-level. |

**Phase 546 findings (Hazard x PREFIX Integration, 7 research questions, 11 analysis dimensions):**
- STRONGEST FINDING: Universal HEAD atom hazard source immunity (C1546). ALL 5 HEAD atoms {a,e,o,k,t} have exactly 0% source rate across 16,819 headed tokens. EXTENDS C1446 from k-only to entire HEAD class. HEAD presence vs absence is the PRIMARY binary safety gate. Three-way base x HEAD x hazard decomposition confirms immunity is HEAD-INTRINSIC, not base-mediated.
- TERMINAL > HEAD for hazard class selection: TERMINAL atom V=0.306 vs HEAD V=0.219 (1.40x). HEAD gates WHETHER hazard occurs (binary), TERMINAL selects WHAT TYPE (categorical). y->PHASE_ORDERING, l->CONTAINMENT_TIMING, bare->RATE_MISMATCH, h->ENERGY_OVERSHOOT. Two complementary information channels.
- PREFIX base hazard gradient: e-base most enriched (3.37x, 22.4%), k-base most depleted (0.30x, 2.02%). Partly HEAD-mediated (bases with more headed tokens = lower aggregate hazard) and partly independent (headless hazard rates differ across bases from 2% to 22%).
- q-modifier STRONGEST single-PREFIX protection: qo 4.15% vs other o-modifiers 27-52% (~7x safer). Mechanism: q activates k-HEAD at 64% on o-base (C1538); k-HEAD is categorically immune (C1546). Contrast: kch on h-base has 21.65% hazard — k as MODIFIER does not provide HEAD immunity. Slot position determines function.
- Sister pair asymmetry predictable from atom structure: Same-base pairs (ch/sh, da/sa) diverge by modifier effect. Same-modifier pairs (ok/ot) diverge by base effect. ok/ot INVERTS ch/sh direction because the base difference (k vs t) dominates.
- PHASE_ORDERING = exclusively headless y-terminal 'dy'; CONTAINMENT_TIMING = exclusively l-terminal 'l'. Both spread across 10-12+ PREFIXes. Hazard is MIDDLE-intrinsic, not PREFIX-induced. PREFIX modulates RATE, not EXISTENCE.
- Conservative forbidden topology: 5/9 source MIDDLEs are phantom (0 corpus tokens). Grammar defines safety net broader than vocabulary requires. Defense-in-depth architecture.
- COMPLETE hazard routing chain now established: PREFIX base -> HEAD selection -> hazard immunity (binary) -> TERMINAL atom -> hazard class type (categorical).

**Phase 547 findings (Phantom MIDDLE Mechanism, 4 hypotheses tested, 10 analytical tests):**
- PRIMARY MECHANISM: D_LEXICAL_CURATION confirmed. ch/sh is a PREFIX-domain bigram that categorically does not extend to MIDDLE-initial position for compounds of length 3+ (C1553). PREFIX:MIDDLE ratio 5,821:0. Individual atoms c, s, h all appear freely in MIDDLE position -- prohibition is at bigram level.
- SECONDARY MECHANISM: C_SAFETY_PRUNING contributing. All 5 phantom MIDDLEs are hazard sources involved in 2-3 forbidden pairs each. Forbidden transition topology provides defense-in-depth: vocabulary exclusion (C1553) + transition prohibition (C109) = two independent safety layers.
- REJECTED: A_CONSTRUCTION_PROHIBITION (all atoms legal in assigned slots per C1209/C1210) and B_SELECTIONAL_COLLAPSE (22-27 compatible PREFIXes each, suffix-compatible terminals).
- c-initial compound second-atom selectivity (C1555): 49/55 c-initial compounds contain h, but h is ALWAYS at position 2+ (c+[k/t/f/p]+h pattern). c+h adjacency at positions 0-1 is categorically absent. Confirms bigram-level prohibition.
- Defense-in-depth architecture confirmed (C1554): Phantom MIDDLEs pass every atomic legality test but are excluded by the ch/sh positional partition. The forbidden topology covers MIDDLEs that the vocabulary system already makes impossible -- structural insurance against revival of the dead naming pattern.

---

### Phase 548: o-Domain Deep Dive (O_DOMAIN_DEEP_DIVE)

| C# | Claim | Tier | Scope | Key Metrics |
|---|-----------|------|------|---------|
| 1556 | o-HEAD terminal-to-category deterministic mapping | 2 | B, MIDDLE, atom, HEAD, o-HEAD, terminal, category, deterministic, STAGING, FLOW, OPERATION, C1388, C1475, C1483, C1485, C1487 | ol=100% STAGING (762 tokens), or=100% FLOW (446), bare o=100% OPERATION (388). l-terminal=92.9% STAGING (N=820), r-terminal=88.6% FLOW (N=508). Sharpest terminal-category coupling for any HEAD. |
| 1557 | o-HEAD y-terminal near-complete depletion (0.007x) | 2 | B, MIDDLE, atom, HEAD, o-HEAD, y-terminal, depletion, safety, PHASE_ORDERING, hazard, C1388, C1475, C1546, C1551 | ~19/2717 y-terminal tokens. 0.007x enrichment. Strongest single-terminal depletion for any HEAD. Structural PHASE_ORDERING immunity via y-avoidance. |
| 1558 | o-HEAD p/f executive modifier enrichment with i/d depletion | 2 | B, MIDDLE, atom, HEAD, o-HEAD, modifier, p, f, i, d, enrichment, depletion, arrangement, C1388, C1475, C1479, C1543 | p 3.51x (9.7%), f 2.83x (2.7%) enriched; i 0.32x (6.1%), d 0.55x (10.6%) depleted. p=strongest modifier enrichment for any single HEAD. |
| 1559 | o-HEAD cross-system gradient A(28.5%)>AZC(22.4%)>B(11.8%) with AZC S/R=1.66x | 2 | CROSS, A, B, AZC, MIDDLE, atom, HEAD, o-HEAD, cross-system, gradient, AZC-zone, boundary, C1381, C1388, C1502, C1507, C1517, C1522 | A/B ratio 2.42x. AZC zones: L=30.9%, S=29.3%, C=26.2%, P=19.1%, R=17.7%. A-proximate zones high, B-proximate zones low. |
| 1560 | o-HEAD inner atom composition divergent (y 0.023x, l 2.74x, p 4.67x) | 2 | B, MIDDLE, atom, HEAD, o-HEAD, inner-atom, composition, divergent, y-depletion, l-enrichment, p-enrichment, CHANNELED, terminal, C1388, C1475, C1484, C1487, C1556 | y 0.023x = most extreme single-atom divergence in system. l 2.74x, r 2.29x, h 2.24x, p 4.67x, f 3.65x enriched. n 0.19x, i 0.37x depleted. |
| 1561 | o-HEAD empirical hazard immunity (0% source AND 0% target) | 2 | B, MIDDLE, atom, HEAD, o-HEAD, hazard, immunity, source, target, double-protection, C1388, C1446, C1546, C1551, C1557 | 0/2717 in either direction. 3 theoretical forbidden pairs never fire (1 phantom source, 2 vanishingly rare). Safest HEAD domain. |

**Phase 548 findings (o-Domain Deep Dive, 10 research questions, 13 analytical tests):**
- STRONGEST FINDING: o-HEAD terminal-to-category deterministic mapping (C1556). Within o-HEAD MIDDLEs (2,717 tokens), the terminal atom deterministically selects category: ol=100% STAGING, or=100% FLOW, bare o=100% OPERATION. Sharpest terminal-category coupling for any HEAD atom. RESOLVES C1388's vague "arrangement" label: o-HEAD is an arrangement domain BECAUSE it uses different terminals for different arrangement ASPECTS.
- y-terminal near-complete depletion at 0.007x (C1557) -- strongest single-terminal depletion for any HEAD. Creates structural PHASE_ORDERING immunity since y-terminal is the exclusive PHASE_ORDERING hazard vector (C1551). Combined with C1546 (HEAD source immunity) = double protection.
- Executive modifier enrichment: p 3.51x and f 2.83x are strongest modifier enrichments for any single HEAD (C1558). i depleted 0.32x. Confirms C1543 (p/f are o-HEAD arrangement-affiliated modifiers) quantitatively.
- Cross-system A>AZC>B gradient (C1559): A=28.5%, AZC=22.4%, B=11.8% (A/B=2.42x). AZC zones grade from arrangement-heavy boundaries (S=29.3%) to execution-heavy interiors (R=17.7%), matching C1522 (A-proximate vs B-proximate zones).
- Inner atom composition: y at 0.023x is the most extreme single-atom divergence in the entire atom system (C1560). o-HEAD compounds built from CHANNELED terminal vocabulary (l, r, h) while excluding y and n.
- Empirical hazard immunity: 0% source AND 0% target across 2,717 tokens (C1561). Three theoretical forbidden pairs involving o-HEAD MIDDLEs never fire in practice.
- Additional (not constraint-worthy): o-HEAD is positionally flat in B lines (mean=0.497), contrasting with AZC boundary concentration. Self-transition rate 0.136 (1.14x, moderate). Suffix rate 0.480 (near baseline). Mode A rate 0.253 (below baseline). Compounds overwhelmingly 2-atom (59.9%). Category JSD vs e-HEAD = 0.365 (LARGE) -- maximally different operational domains.

---

### Phase 549: Atom Architecture Cleanup (ATOM_ARCHITECTURE_CLEANUP)

| C# | Claim | Tier | Scope | Key Metrics |
|---|-----------|------|------|---------|
| 1562 | HEAD self-transition rate hierarchy | 2 | B, MIDDLE, atom, HEAD, self-transition, sequential, hierarchy, persistence, switching, C1212, C1384, C1475, C1478, C1521 | Three-tier: PERSISTENT (e 28.5%, headless 28.4%, a 25.2%), SWITCHING (k 16.7%, o 13.6%), RARE (t 9.1%). e->k 1.493x, a->k 0.528x. |
| 1563 | Terminal-to-next-HEAD cross-token routing grammar | 2 | B, MIDDLE, atom, terminal, HEAD, routing, cross-token, sequential, instruction-phrases, C1212, C1440, C1475, C1483, C1484, C1487 | r->a 2.231x, y->k 1.597x, h->t 1.892x, l->e 1.246x, m->o 1.554x, bare neutral. TERM is dual-function: suffix-gating + HEAD routing. |
| 1564 | Suffix carries zero forward information to next HEAD | 2 | B, suffix, HEAD, cross-token, information, null, compositionality, C1003, C1510, C1412, C1422 | JSD=0.0021 (smallest in phase). Suffix scope terminates at token edge. Extends C1003 to cross-token boundary. |
| 1565 | Paragraph header modifier divergence exceeds HEAD divergence 10x | 2 | B, paragraph, header, atom, modifier, HEAD, divergence, specification, executive, C1287, C1396, C1468, C1479, C1543 | MOD JSD=0.085 vs HEAD JSD=0.008 (10.6x ratio). p 3.66x, f 3.90x enriched in headers; i 0.51x depleted. h-terminal 2.35x enriched. |
| 1566 | Line position Q3-Q4 step discontinuity | 2 | B, line, position, gradient, quintile, closure, step, discontinuity, specification, work-zone, C1425, C1426, C1427, C1428, C1429, C1430, C1434, C1463 | Q3->Q4 HEAD JSD=0.0185 (26x Q2->Q3), TERM JSD=0.0200 (20x Q2->Q3). Q1-Q3 interior JSD<0.003. Two-step line architecture. |

**Phase 549 findings (Atom Architecture Cleanup, 4 research questions, 17 sub-analyses):**
- Q1 (ARTICULATORS): All 6 sub-analyses CONFIRM existing constraints C1416-C1421 at higher resolution. Articulator rate 4.41% in B (C1416 exact match), line-initial 4.518x (C1417), BARE/qo excluded (C1418), e-HEAD 1.807x enriched / k-HEAD 0.098x excluded (C1419), suffix suppression 0.548x (C1420), category JSD=0.030 confirming MIDDLE mediation (C1421). No new constraints from Q1.
- Q2 (SEQUENTIAL COUPLINGS): Three new findings. HEAD self-transition hierarchy (C1562) reveals three-tier persistence: stability/identification domains sustain runs, thermal/arrangement domains switch quickly. Terminal-to-next-HEAD routing grammar (C1563) completes the cross-token instruction chain at atom resolution: TERM is a dual-function atom that simultaneously gates suffix attachment (C1440) and routes the next token's HEAD domain. Suffix zero forward information (C1564) -- JSD=0.0021 between suffixed and bare tokens' next-HEAD distributions, extending C1003 (pairwise compositionality) to the cross-token boundary.
- Q3 (PARAGRAPH SIGNATURES): One new finding. Header modifier divergence 10x HEAD divergence (C1565) -- paragraphs specify through MODIFIER selection (p 3.66x, f 3.90x enriched) not HEAD domain (JSD=0.008). Resolves C1287 (MARKING-enriched header) mechanism. Convergence test extends C1402: late body lines are MORE divergent from headers (ratio 1.393), not convergent.
- Q4 (LINE-POSITION GRADIENT): One new finding. Q3->Q4 step discontinuity (C1566) -- HEAD JSD jumps 26x at closure boundary while Q1-Q3 interior remains homogeneous (JSD<0.003). Refines C1425-C1430 three-zone model to TWO-STEP architecture: mild specification shift at Q0->Q1, uniform work zone Q1-Q3, sharp closure break at Q3->Q4. Additional confirmations: THERMAL Q1 peak (C1428), k-HEAD Q1 onset (C1464), m-terminal extreme Q4 enrichment (C1434).

---

### Phase 550: Complete Control Architecture -- The Voynich Instruction Word (SYNTHESIS)

**Date:** 2026-03-06 | **Type:** SYNTHESIS (no new data analysis) | **Constraints added:** 0

This is the capstone synthesis of the characterization program. No new empirical analysis was performed and no new constraints were added. The output is `phases/INSTRUCTION_WORD_FORMALISM/ARCHITECTURE.md`, a self-contained specification document (~4,500 words) that integrates findings from Phases 1-549 into a definitive architectural reference.

**Seven sections formalized:**
1. **The Instruction Word** -- Complete TOKEN = [ART] + [PFX] + MIDDLE + [SUF] decomposition at atom resolution, including the HEAD+MOD*+TERM internal MIDDLE grammar, six HEAD domains, three-tier terminal taxonomy, and suffix parallel compositional domain.
2. **Safety Architecture** -- Three-level defense-in-depth: Level 1 (construction exclusion via ch/sh bigram partition, C1553-C1555), Level 2 (hazard source typing via HEAD atom, C1446/C1476/C1546), Level 3 (transition prohibition via 17 forbidden pairs, C109/C789). Multiplicative composition explains 0.053% realized hazard rate (C1360).
3. **Organizational Model** -- Line = safety envelope (SPECIFICATION->THERMAL_WORK->CLOSURE, C1425-C1430), Paragraph = operational unit (gallows-delimited, self-contained, C845/C864), Folio = program (unique vocabulary, C531). Paragraphs unordered within folios (C1399-C1400). Line-level hazard gradient persists independently in all paragraph zones (C1469).
4. **Document Stack** -- Currier A (declarative registry, C240), AZC (legality bridge grading A-like to B-like, C1522), Currier B (executable grammar, C121), HT (operator orientation, C935), Dark Pipeline (nominalized identification, C1137/C1505). All registers over shared atom substrate (C1499).
5. **Shared Atom Substrate** -- 18-atom universal ontology with min Jaccard 0.895 across all systems (C1499). Same HEAD+MOD*+TERM grammar everywhere. Channels differentiate through slot proportions, not inventories (C1504). Bridge MIDDLEs are the executable backbone (C1500-C1501).
6. **What the Operator Supplies** -- 13 types of non-encodable judgment (C197/C1056). Hazard clamped (CV 0.04-0.11), recovery free (CV 0.72-0.82) per C458.
7. **Generative Sufficiency** -- M2.1 (position-conditioned 49-class Markov + symmetric forbidden suppression) passes 21/21 tests (C1365). Grammar is generatively closed.

**Key integrative findings (not new constraints, but cross-constraint connections):**
- Terminal atom is TRIPLE-function linchpin: suffix gating (C1440-C1445) + hazard class typing (C1547) + next-HEAD routing (C1563)
- Safety levels compose MULTIPLICATIVELY: hazard requires simultaneous failure at construction, typing, AND transition levels
- Cross-token chain is exclusively TERM->HEAD: suffix is a dead-end branch (C1564), PREFIX has no cross-token role
- A and B are REGISTERS (declarative vs executable) over the same atom substrate, not lookup tables or translations (C1499-C1527)
- Operator boundary is a DESIGN CHOICE: encodes everything procedurable, excludes everything requiring embodied judgment (C1056, C197, C458)

**Verdict:** The characterization program is COMPLETE. No structural question about the formal architecture remains open at the level addressable by internal analysis. What remains requires external evidence (who, what institution, what materials, what language).

---

### Phase 551: Operator/Document-Usage Model (SYNTHESIS)

**Date:** 2026-03-06 | **Type:** SYNTHESIS (no new data analysis) | **Constraints added:** 0

Tier 3 interpretive synthesis describing how a trained medieval practitioner would navigate and use the Voynich Manuscript's four-register document stack during a work session. Output is `phases/OPERATOR_USAGE_MODEL/OPERATOR_MODEL.md`, a practitioner-facing narrative (~4,500 words) translating structural findings into a usage model.

**Nine sections covering:**
1. **Who Is the Operator** -- Expert profile: what they know (materials, equipment, sensory cues, hazard recognition) and what the manuscript assumes (C197, C1056, C109)
2. **What the Manuscript Contains** -- Four registers from the operator's perspective: A (specification registry, C240), AZC (legality bridge, C313/C443), B (execution grammar, C121/C531), HT (orientation layer, C740/C935)
3. **A Work Session** -- Eight-step reconstruction: program selection (C531) -> configuration check (C502/C443) -> header reading (C747) -> paragraph choice (C1399/C864) -> line execution (C1425-C1430) -> between-line judgment (C1056) -> between-paragraph choice (C1399-C1400) -> completion
4. **What Makes This Different** -- Not a recipe book, not a prose manual, not a codebook/cipher; control system specification analogy (C132, C130, C207)
5. **The Responsibility Architecture** -- System handles safety (C109), specification (C121), legality (C313), hazard clamping (C458), discrimination (C475), orientation (C459). Operator supplies material identity (C120), sensory evaluation (C1056), timing, hazard recognition, monitoring, program selection, paragraph ordering (C1399-C1400), completion judgment, recovery strategy (C458)
6. **The Dark Pipeline** -- 300 dark MIDDLEs as identification vocabulary within execution (C1137, C1141, C1146, C1505). Operator reads cues, supplies referents
7. **Multiple Operators** -- Parallel subroutine execution from paragraph self-containment (C845), ordering null (C1399), within-folio coherence (C1288). Workshop setting interpretation
8. **What the Operator Does NOT Need** -- No literacy (C132), no math (C287), no sequential memory (C1470-C1471), no cross-folio reference (C531), no grammar knowledge (C121)
9. **Summary** -- Integrated four-register model with design philosophy

**Key integrative findings (not new constraints):**
- Four registers form a coordinated working environment navigated as-needed, not sequentially
- Eight-step session model emerges from combining program selection, configuration, execution, and judgment findings
- Negative space (Section 8) shows notation designed for maximum operational accessibility
- Parallel execution model: multiple operators can work from same folio simultaneously (C845, C1399-C1400, C1288)

**Verdict:** Operator usage model COMPLETE. Complements Phase 550 (technical specification) with a practitioner-facing view of the same architecture.

---

### Phase 552: Historical Genre Placement (SYNTHESIS)

**Date:** 2026-03-06 | **Type:** SYNTHESIS (no new data analysis) | **Constraints added:** 0

Tier 3 interpretive synthesis placing the VMS within the landscape of medieval technical document genres based on 1,410 validated structural constraints. Output is `phases/HISTORICAL_GENRE_PLACEMENT/GENRE_ANALYSIS.md`, a genre comparison document (~5,000 words) evaluating 8 medieval document genres against the VMS structural profile across 7 assessment dimensions.

**Eight genres compared:**
1. Receptaria (recipe collections) -- e.g., *Mappae Clavicula*, *Compositiones variae*: 1/7 match
2. Kunstbucher (craft manuals) -- e.g., Theophilus, Cennini: 0/7 match
3. Distillation manuals -- e.g., Brunschwig: 1.5/7 match
4. Pharmacopeias -- e.g., *Antidotarium Nicolai*: 1.5/7 match
5. Alchemical treatises -- e.g., Pseudo-Geber, Ripley: 0.5/7 match
6. Pattern/model books -- e.g., Villard de Honnecourt: 1.5/7 match
7. Tally/accounting systems -- e.g., Exchequer tally sticks: 2/7 match
8. Laboratory notebooks -- guild workshop records: 2.5/7 match (best match)

**Seven assessment dimensions:** notation type, audience, safety encoding, material reference, structural complexity, compositional principle, operational specificity.

**Key findings (not new constraints):**
- No existing medieval genre scores above 2.5/7 compatibility with the VMS structural profile
- Three VMS features have NO historical precedent: structural safety architecture (C109), multi-register architecture (C1499), formal operational grammar (C121/C124)
- The fundamental genre gap is between DESCRIPTION (all existing genres) and EXECUTION (VMS): all medieval technical documents describe procedures in natural language; the VMS encodes operational states in a formal notation system
- Proposed genre classification: OPERATIONAL CONTROL CODEX -- purpose-built non-linguistic operational notation encoding parameterized control programs with structural safety enforcement and multi-register architecture
- The genre gap explains the decipherment failure: the VMS was never natural language (C132), so all cipher/language approaches are structurally misdirected
- The VMS and Brunschwig serve opposite purposes: one executes (proprietary notation, pre-1500), the other explains (pedagogical publication, 1500)
- The proposed genre's predicted rarity is structurally motivated: proprietary notation, enormous investment, publication obsolescence, minimal copies

**Verdict:** Historical genre placement COMPLETE. VMS occupies a unique position in medieval document-design space: the intersection of non-linguistic notation, operational specificity, and formal grammar that no surveyed genre shares.

---

## Navigation

↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)

↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
