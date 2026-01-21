# Constraint Index

**Total:** 339 validated constraints | **Version:** 2.46

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
| 130 | DSL hypothesis rejected (0.19% reference rate) | 1 | B | ⊂ falsified |
| 131 | Role consistency LOW (23.8%) | 2 | B | ⊂ grammar_system |
| 132 | Language encoding CLOSED | 1 | B | ⊂ falsified |

---

## Illustration Independence (C137-C140)

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| 137 | Swap invariance confirmed (p=1.0) | 1 | B | ⊂ falsified |
| 138 | Illustrations do not constrain execution | 1 | B | ⊂ falsified |
| 139 | Grammar recovered from text-only | 2 | B | ⊂ grammar_system |
| 140 | Illustrations are epiphenomenal | 1 | B | ⊂ falsified |

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
| 157 | Circulatory reflux uniquely compatible (100%) | 3 | B | ⊂ speculative |
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
| 199 | Both mineral AND botanical survive | 3 | B | ⊂ speculative |
| 209 | Attentional pacing wins (6/8) | 2 | HT | ⊂ human_track |
| 215 | BOTANICAL_FAVORED (8/8 tests, ratio 2.37) | 3 | B | ⊂ speculative |
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
| 384 | NO ENTRY-LEVEL A-B COUPLING | 2 | A↔B | → [C384_no_entry_coupling.md](C384_no_entry_coupling.md) |
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

## A-Exclusive Vocabulary Track (C498-C500)

| # | Constraint | Tier | Scope | Status |
|---|------------|------|-------|--------|
| **498** | **Registry-Internal Vocabulary Track** (56.6% A-exclusive MIDDLEs: ct-prefix 5.1×, suffix-less 3×, folio-localized; don't propagate to B) | 2 | A | ⊂ currier_a |
| **498.a** | **A∩B Shared Vocabulary Bifurcation** (154 AZC-Mediated + 114 B-Native Overlap; pipeline scope narrowed) | 2 | A | ⊂ currier_a |
| 499 | Bounded Material-Class Recoverability (128 MIDDLEs with P(material_class) vectors; conditional on Brunschwig) | 3 | A | ⊂ currier_a |
| 500 | Suffix Posture Temporal Pattern (CLOSURE front-loaded 77% Q1, NAKED late 38% Q4, ratio 5.69×) | 3 | A | ⊂ currier_a |

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
| [currier_a.md](currier_a.md) | Currier A registry | C224-C266, C345-C346, C420-C424, C475-C478, C497-C499 |
| [morphology.md](morphology.md) | Compositional morphology | C267-C298, C349-C410, C495 |
| [operations.md](operations.md) | OPS doctrine and control | C178-C223, C394-C403 |
| [human_track.md](human_track.md) | Human Track layer | C166-C172, C341-C348, C404-C419, C450-C453, C477 |
| [azc_system.md](azc_system.md) | AZC hybrid system | C300-C327, C430-C436, C496 |
| [organization.md](organization.md) | Organizational structure | C153-C176, C323-C370 |

---

## Navigation

↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
