# Constraint Index

**Total:** 419 validated constraints | **Version:** 2.82

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

## AZC System (C300-C327, C430-C436)

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
| 391 | TIME-REVERSAL SYMMETRY | 2 | B | ⊂ grammar_system |
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
| **563** | **AX Internal Positional Stratification** (20 AX classes split into INIT/5, MED/9, FINAL/6; H=213.9 p=3.6e-47; 71.8% INIT-before-FINAL; Cohen's d=0.69; positional gradient not clusters) | 2 | B | -> [C563_ax_positional_stratification.md](C563_ax_positional_stratification.md) |
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
| [human_track.md](human_track.md) | Human Track layer | C166-C172, C341-C348, C404-C419, C450-C453, C477, C507 |
| [azc_system.md](azc_system.md) | AZC hybrid system | C300-C327, C430-C436, C496 |
| [organization.md](organization.md) | Organizational structure | C153-C176, C323-C370 |

---

## Navigation

↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
