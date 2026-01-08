# Constraint Index

**Total:** 411 validated constraints | **Version:** 1.8

---

## How to Use

1. **Find by number:** Ctrl+F for "C###"
2. **Find by topic:** Browse category sections below
3. **Full details:** Follow link to individual file or grouped registry

### Legend

- `→` = Individual file exists
- `⊂` = In grouped registry
- **Bold** = Tier 0 (frozen fact)

---

## Executability (C072-C125)

| # | Constraint | Tier | Status |
|---|------------|------|--------|
| **074** | Dominant convergence to stable states (57.8% STATE-C terminal) | 0 | → [C074_dominant_convergence.md](C074_dominant_convergence.md) |
| **079** | Only STATE-C essential | 0 | ⊂ tier0_core |
| **084** | System targets MONOSTATE (42.2% end in transitional) | 0 | ⊂ tier0_core |
| **115** | 0 non-executable tokens | 0 | ⊂ tier0_core |
| **119** | 0 translation-eligible zones | 0 | ⊂ tier0_core |
| **120** | PURE_OPERATIONAL verdict | 0 | ⊂ tier0_core |
| **121** | 49 instruction equivalence classes (9.8x compression) | 0 | → [C121_49_instruction_classes.md](C121_49_instruction_classes.md) |
| **124** | 100% grammar coverage | 0 | → [C124_grammar_coverage.md](C124_grammar_coverage.md) |

---

## Kernel Structure (C085-C108)

| # | Constraint | Tier | Status |
|---|------------|------|--------|
| **085** | 10 single-character primitives (s,e,t,d,l,o,h,c,k,r) | 0 | ⊂ tier0_core |
| **089** | Core within core: k, h, e | 0 | ⊂ tier0_core |
| 090 | 500+ 4-cycles, 56 3-cycles (topological) | 2 | ⊂ grammar_system |
| 103 | k = ENERGY_MODULATOR | 2 | ⊂ grammar_system |
| 104 | h = PHASE_MANAGER | 2 | ⊂ grammar_system |
| 105 | e = STABILITY_ANCHOR (54.7% recovery paths) | 2 | ⊂ grammar_system |
| 107 | All kernel nodes BOUNDARY_ADJACENT to forbidden | 2 | ⊂ grammar_system |

---

## Hazard Topology (C109-C114)

| # | Constraint | Tier | Status |
|---|------------|------|--------|
| 109 | 5 failure classes (PHASE_ORDERING dominant 41%) | 2 | → [C109_hazard_classes.md](C109_hazard_classes.md) |
| 110 | PHASE_ORDERING 7/17 = 41% | 2 | ⊂ grammar_system |
| 111 | 65% asymmetric | 2 | ⊂ grammar_system |
| 112 | 59% distant from kernel | 2 | ⊂ grammar_system |

---

## Language Rejection (C130-C132)

| # | Constraint | Tier | Status |
|---|------------|------|--------|
| 130 | DSL hypothesis rejected (0.19% reference rate) | 1 | ⊂ falsified |
| 131 | Role consistency LOW (23.8%) | 2 | ⊂ grammar_system |
| 132 | Language encoding CLOSED | 1 | ⊂ falsified |

---

## Illustration Independence (C137-C140)

| # | Constraint | Tier | Status |
|---|------------|------|--------|
| 137 | Swap invariance confirmed (p=1.0) | 1 | ⊂ falsified |
| 138 | Illustrations do not constrain execution | 1 | ⊂ falsified |
| 139 | Grammar recovered from text-only | 2 | ⊂ grammar_system |
| 140 | Illustrations are epiphenomenal | 1 | ⊂ falsified |

---

## Family Structure (C126-C144)

| # | Constraint | Tier | Status |
|---|------------|------|--------|
| 126 | 0 contradictions across 8 families | 2 | ⊂ grammar_system |
| 129 | Family differences = coverage artifacts | 2 | ⊂ grammar_system |
| 141 | Cross-family transplant = ZERO degradation | 2 | ⊂ grammar_system |
| 144 | Families are emergent regularities | 2 | ⊂ grammar_system |

---

## Organizational Structure (C153-C177)

| # | Constraint | Tier | Status |
|---|------------|------|--------|
| 153 | Prefix/suffix axes partially independent (MI=0.075) | 2 | ⊂ organization |
| 154 | Extreme local continuity (d=17.5) | 2 | ⊂ organization |
| 155 | Piecewise-sequential geometry (PC1 rho=-0.624) | 2 | ⊂ organization |
| 156 | Detected sections match codicology (4.3x quire alignment) | 2 | ⊂ organization |
| 157 | Circulatory reflux uniquely compatible (100%) | 3 | ⊂ speculative |
| 166 | Uncategorized: zero forbidden seam presence (0/35) | 2 | ⊂ human_track |
| 167 | Uncategorized: 80.7% section-exclusive | 2 | ⊂ human_track |
| 168 | Uncategorized: single unified layer | 2 | ⊂ human_track |
| 169 | Uncategorized: hazard avoidance 4.84 vs 2.5 | 2 | ⊂ human_track |
| 170 | Uncategorized: morphologically distinct (p<0.001) | 2 | ⊂ human_track |
| 171 | Only continuous closed-loop process control survives | 2 | → [C171_purpose_class.md](C171_purpose_class.md) |

---

## OPS Findings (C178-C198)

| # | Constraint | Tier | Status |
|---|------------|------|--------|
| 178 | 83 folios yield 33 operational metrics | 2 | ⊂ operations |
| 179 | 4 stable regimes (K-Means k=4, Silhouette=0.23) | 2 | ⊂ operations |
| 180 | All 6 aggressive folios in REGIME_3 | 2 | ⊂ operations |
| 181 | 3/4 regimes Pareto-efficient; REGIME_3 dominated | 2 | ⊂ operations |
| 182 | Restart-capable = higher stability | 2 | ⊂ operations |
| 187 | CEI manifold formalized | 2 | ⊂ operations |
| 188 | CEI bands: R2 < R1 < R4 < R3 | 2 | ⊂ operations |
| 190 | LINK-CEI r=-0.7057 | 2 | ⊂ operations |
| 196 | 100% match EXPERT_REFERENCE archetype | 2 | ⊂ operations |
| 197 | Designed for experts, not novices | 2 | ⊂ operations |

---

## External Findings (C199-C223)

| # | Constraint | Tier | Status |
|---|------------|------|--------|
| 199 | Both mineral AND botanical survive | 3 | ⊂ speculative |
| 209 | Attentional pacing wins (6/8) | 2 | ⊂ human_track |
| 215 | BOTANICAL_FAVORED (8/8 tests, ratio 2.37) | 3 | ⊂ speculative |
| 216 | Hybrid hazard model (71% batch, 29% apparatus) | 2 | ⊂ operations |
| 217 | 0 true HT near hazards | 2 | ⊂ human_track |
| 221 | Practice-leaning (4/5) | 4 | ⊂ speculative |

---

## Currier A Disjunction (C224-C240)

| # | Constraint | Tier | Status |
|---|------------|------|--------|
| 224 | A coverage = 13.6% (threshold 70%) | 2 | ⊂ currier_a |
| 229 | A = DISJOINT | 2 | → [C229_currier_a_disjoint.md](C229_currier_a_disjoint.md) |
| 233 | A = LINE_ATOMIC | 2 | ⊂ currier_a |
| 234 | A = POSITION_FREE | 2 | ⊂ currier_a |
| 235 | 8+ mutually exclusive markers | 2 | ⊂ currier_a |
| 239 | A/B separation = DESIGNED (0.0% cross) | 2 | ⊂ currier_a |
| 240 | A = NON_SEQUENTIAL_CATEGORICAL_REGISTRY | 2 | → [C240_currier_a_registry.md](C240_currier_a_registry.md) |

---

## Multiplicity Encoding (C250-C266)

| # | Constraint | Tier | Status |
|---|------------|------|--------|
| 250 | 64.1% show repeating blocks | 2 | ⊂ currier_a |
| 253 | All blocks unique (0% cross-entry reuse) | 2 | ⊂ currier_a |
| 255 | 100% section-exclusive blocks | 2 | ⊂ currier_a |
| 261 | Token order NON-RANDOM | 2 | ⊂ currier_a |

---

## Compositional Morphology (C267-C298)

| # | Constraint | Tier | Status |
|---|------------|------|--------|
| 267 | Tokens are COMPOSITIONAL (PREFIX+MIDDLE+SUFFIX) | 2 | → [C267_compositional_morphology.md](C267_compositional_morphology.md) |
| 268 | 897 observed combinations | 2 | ⊂ morphology |
| 272 | A and B on COMPLETELY DIFFERENT folios | 2 | ⊂ morphology |
| 278 | Three-axis HIERARCHY (PREFIX→MIDDLE→SUFFIX) | 2 | ⊂ morphology |
| 281 | Components SHARED across A and B | 2 | ⊂ morphology |
| 291 | ~20% have optional ARTICULATOR forms | 2 | ⊂ morphology |
| 292 | Articulators = ZERO unique identity distinctions | 2 | ⊂ morphology |

---

## AZC System (C300-C327)

| # | Constraint | Tier | Status |
|---|------------|------|--------|
| 300 | 9,401 tokens (7.7%) unclassified by Currier | 2 | ⊂ azc_system |
| 301 | AZC is HYBRID (B=69.7%, A=65.4%) | 2 | → [C301_azc_hybrid.md](C301_azc_hybrid.md) |
| 306 | Placement-coding axis established | 2 | ⊂ azc_system |
| 313 | Position constrains LEGALITY not PREDICTION | 2 | ⊂ azc_system |
| 317 | Hybrid architecture (topological + positional) | 2 | ⊂ azc_system |
| 322 | SEASON-GATED WORKFLOW interpretation | 2 | ⊂ azc_system |
| 323 | 57.8% STATE-C terminal | 2 | ⊂ grammar_system |

---

## Grammar Robustness (C328-C331)

| # | Constraint | Tier | Status |
|---|------------|------|--------|
| 328 | 10% corruption = 3.3% entropy increase | 2 | ⊂ grammar_system |
| 329 | Top 10 token removal = 0.8% entropy change | 2 | ⊂ grammar_system |
| 330 | Leave-one-folio-out = max 0.25% change | 2 | ⊂ grammar_system |
| 331 | 49-class minimality WEAKENED but confirmed | 2 | ⊂ grammar_system |

---

## Line/Folio Structure (C345-C370)

| # | Constraint | Tier | Status |
|---|------------|------|--------|
| 345 | A folios lack thematic coherence | 2 | ⊂ currier_a |
| 346 | A exhibits SEQUENTIAL COHERENCE | 2 | ⊂ currier_a |
| 357 | Lines 3.3x more regular than random | 2 | → [C357_line_structure.md](C357_line_structure.md) |
| 358 | Specific boundary tokens identified | 2 | ⊂ organization |
| 360 | Grammar is LINE-INVARIANT | 2 | ⊂ grammar_system |
| 361 | Adjacent B folios share 1.30x more vocabulary | 2 | ⊂ organization |
| 367 | Sections are QUIRE-ALIGNED (4.3x) | 2 | ⊂ organization |

---

## Prefix/Suffix Function (C371-C382)

| # | Constraint | Tier | Status |
|---|------------|------|--------|
| 371 | Prefixes have POSITIONAL GRAMMAR | 2 | ⊂ morphology |
| 372 | Kernel dichotomy (100% vs <5%) | 2 | ⊂ morphology |
| 373 | LINK affinity patterns | 2 | ⊂ morphology |
| 375 | Suffixes have POSITIONAL GRAMMAR | 2 | ⊂ morphology |
| 382 | MORPHOLOGY ENCODES CONTROL PHASE | 2 | → [C382_phase_encoding.md](C382_phase_encoding.md) |

---

## Global Architecture (C383-C393)

| # | Constraint | Tier | Status |
|---|------------|------|--------|
| 383 | GLOBAL MORPHOLOGICAL TYPE SYSTEM | 2 | → [C383_global_type_system.md](C383_global_type_system.md) |
| 384 | NO ENTRY-LEVEL A-B COUPLING | 2 | → [C384_no_entry_coupling.md](C384_no_entry_coupling.md) |
| 385 | STRUCTURAL GRADIENT in Currier A | 2 | ⊂ currier_a |
| 389 | BIGRAM-DOMINANT local determinism (H=0.41 bits) | 2 | ⊂ grammar_system |
| 391 | TIME-REVERSAL SYMMETRY | 2 | ⊂ grammar_system |
| 392 | ROLE-LEVEL CAPACITY (97.2% observed) | 2 | ⊂ grammar_system |
| 393 | FLAT TOPOLOGY (diameter=1) | 2 | ⊂ grammar_system |

---

## Control Strategies (C394-C403)

| # | Constraint | Tier | Status |
|---|------------|------|--------|
| 394 | INTENSITY-ROLE DIFFERENTIATION | 2 | ⊂ operations |
| 395 | DUAL CONTROL STRATEGY | 2 | ⊂ operations |
| 397 | qo-prefix = escape route (25-47%) | 2 | ⊂ grammar_system |
| 400 | BOUNDARY HAZARD DEPLETION (5-7x) | 2 | ⊂ grammar_system |
| 403 | 5 PROGRAM ARCHETYPES (continuum) | 2 | ⊂ operations |

---

## Human Track Closure (C404-C406)

| # | Constraint | Tier | Status |
|---|------------|------|--------|
| 404 | HT TERMINAL INDEPENDENCE (p=0.92) | 2 | → [C404_HT_non_operational.md](C404_HT_non_operational.md) |
| 405 | HT CAUSAL DECOUPLING (V=0.10) | 2 | ⊂ human_track |
| 406 | HT GENERATIVE STRUCTURE (Zipf=0.89) | 2 | ⊂ human_track |

---

## Sister Pairs (C407-C410)

| # | Constraint | Tier | Status |
|---|------------|------|--------|
| 407 | DA = INFRASTRUCTURE | 2 | ⊂ morphology |
| 408 | ch-sh/ok-ot form EQUIVALENCE CLASSES | 2 | → [C408_sister_pairs.md](C408_sister_pairs.md) |
| 409 | Sister pairs MUTUALLY EXCLUSIVE but substitutable | 2 | ⊂ morphology |
| 410 | Sister choice is SECTION-CONDITIONED | 2 | ⊂ morphology |

---

## SITD Findings (C411)

| # | Constraint | Tier | Status |
|---|------------|------|--------|
| 411 | Grammar DELIBERATELY OVER-SPECIFIED (~40% reducible) | 2 | → [C411_deliberate_overspecification.md](C411_deliberate_overspecification.md) |

---

## Grouped Registries

| File | Contents | Constraints |
|------|----------|-------------|
| [tier0_core.md](tier0_core.md) | Tier 0 frozen facts | C074-C125 (core) |
| [grammar_system.md](grammar_system.md) | Grammar and kernel structure | C085-C144, C328-C393 |
| [currier_a.md](currier_a.md) | Currier A registry | C224-C266, C345-C346 |
| [morphology.md](morphology.md) | Compositional morphology | C267-C298, C371-C410 |
| [operations.md](operations.md) | OPS doctrine and control | C178-C198, C394-C403 |
| [human_track.md](human_track.md) | Human Track layer | C166-C170, C209, C217, C341-C348, C404-C406 |
| [azc_system.md](azc_system.md) | AZC hybrid system | C300-C322 |
| [organization.md](organization.md) | Organizational structure | C153-C165, C357-C370 |

---

## Navigation

↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md)
