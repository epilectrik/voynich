# Rupescissa Comparative Analysis

**Date:** 2026-02-15 | **Phase:** 375 | **Tier:** 3/4

---

## Purpose

Three-way comparative analysis across the medieval distillation tradition: Rupescissa (~1351) -> Brunschwig (1500) -> Voynich (15th c.). Framed as **shared tradition convergence**, not evolutionary lineage (no direct transmission evidence).

Phase 374 curated Rupescissa into structured JSON. Brunschwig was curated in Phase 355 (v3). This phase compares the three systems on three axes: degree systems, action vocabularies, and concealment doctrine.

**Prior work:** Brunschwig->Voynich comparison (brunschwig_comparison.md, Phases 355-371). Novel contribution: Rupescissa->Brunschwig mapping.

---

## Sources

| Text | Date | Data File | Key Properties |
|------|------|-----------|----------------|
| Rupescissa | ~1351 | `data/rupescissa_curated_v1.json`, `data/rupescissa_materials_v1.json` | 12 actions, 4-quality x 4-degree, 131 materials |
| Brunschwig | 1500 | `data/brunschwig_curated_v3.json` | 36+ actions across 7 phases, fire degree 1-4, 245 recipes |
| Voynich | 15th c. | Structural contracts (BCSC, CASC) | 49 classes (C121), 5 roles (C591), 17 forbidden transitions (C109), 4 regimes (C179) |

---

## Analysis 1: Degree System Evolution (Tier 3)

### The Three Systems

**Rupescissa (16-cell matrix):** 4 qualities (hot/cold/dry/humid) x 4 degrees = 16 cells. Materials have COMPOUND properties (e.g., pepper = hot 3 + dry 2). Degree 4 in all qualities marked dangerous.

**Brunschwig (4-level fire degree):** Collapsed to 1 axis (fire/heat intensity only). D1=62 (25.3%), D2=147 (60.0%), D3=36 (14.7%), D4=0 (0.0% -- CATEGORICAL_PROHIBITION per BRSC).

**Voynich (4 regimes, C179):** NOT a continuation of prohibition. C494: REGIME_4 = precision-constrained execution. C490: 20.5% of programs forbid AGGRESSIVE strategy.

### Dimensional Collapse

Rupescissa operates in a 4-quality space (hot/cold/dry/humid), each with 4 degrees. Brunschwig collapses this to a single axis: fire (heat intensity). The reason is practical -- distillation requires only thermal control. Cold/dry/humid are material properties, not process parameters. Brunschwig operates on heat, the only quality the distiller directly controls.

The Voynich has 4 regimes (C179) but these encode PROCEDURAL COMPLETENESS (Section X.14), not material quality. The dimensional correspondence is structural, not semantic.

### Degree Distribution Alignment

| Degree | Rupescissa (hot) | Brunschwig (fire) |
|--------|-----------------|-------------------|
| D1 | 8 (18.6%) | 62 (25.3%) |
| D2 | 15 (34.9%) | 147 (60.0%) |
| D3 | 14 (32.6%) | 36 (14.7%) |
| D4 | 6 (14.0%) | 0 (0.0%) |

Both peak at D2, confirming the moderate-intensity center of gravity. The concentration at D2 intensified from 34.9% to 60.0% over 150 years -- distillation practice narrowed toward moderate heat. Degree 4 went from dangerous-but-documented (14.0%) to categorically prohibited (0.0%).

### Prohibition Transformation

This is the key finding: Rupescissa's degree-4 prohibition was **transformed**, not preserved.

| Text | Stance | Degree-4 Treatment |
|------|--------|-------------------|
| Rupescissa | AVOID | Dangerous but documented -- materials listed with warnings. Ch. XXI: "USE WITH EXTREME CAUTION. These can burn the stomach." |
| Brunschwig | RESTRICT | Almost never -- 0/245 recipes at D4. BRSC: "nature rejects all coercion." |
| Voynich | ENGINEER | Precision-constrained execution (C494). Hazard-aware but not forbidden. |

This is a progression from avoidance to controlled access: PROHIBIT -> RESTRICT -> ENGINEER.

### Falsification Result

**PASS.** Both distributions peak at D2. Rupescissa D4 fraction = 14.0% (under 15% threshold). The alignment is structural (shared emphasis on moderate intensity, extreme-end avoidance) though distribution shapes differ in concentration.

### Constraints Referenced

C179, C494, C490, C109, F-BRU-002

---

## Analysis 2: Action Vocabulary Evolution (Tier 3)

### The 12 -> 36 -> 49 Growth

| Text | Count | Type | Abstraction Level |
|------|-------|------|-------------------|
| Rupescissa | 12 | Named physical operations | Theory-level (what to do in principle) |
| Brunschwig | 36+ | Named practical operations | Recipe-level (specific German craft terms) |
| Voynich | 49 | Abstract distributional classes (C121) | Grammar-level (9.8x compression, not human-named) |

The qualitative shift is critical: Rupescissa and Brunschwig use named operations (DISTILL, GRIND, SEAL). The Voynich encodes 49 distributional equivalence classes (C121) -- NOT named operations but co-occurrence patterns. This is the jump from craft vocabulary to abstract grammar.

### Rupescissa -> Brunschwig Mapping (Novel)

| Rupescissa Action | Brunschwig Equivalent(s) | Mapping Type |
|-------------------|--------------------------|--------------|
| DISTILL | DISTILL, REDISTILL | DIRECT |
| CIRCULATE | (none; REDISTILL partial) | ABSENT |
| RECTIFY | RECTIFY | DIRECT |
| SUBLIME | (absent -- metallic) | ABSENT |
| PUTREFY | FERMENT, DIGEST | SPLIT |
| CALCINE | (absent -- metallic) | ABSENT |
| DISSOLVE | (absent -- metallic) | ABSENT |
| GRIND | GRIND, POUND, POWDER | EXPANDED |
| SEAL | SEAL, SEAL_VESSEL | EXPANDED |
| HEAT_DUNG | (replaced by water bath) | REPLACED |
| SEPARATE | STRAIN, FILTER, SETTLE | EXPANDED |
| COLLECT | COLLECT | DIRECT |

**Mapping type summary:**
- 3 DIRECT (core operations preserved)
- 4 ABSENT (metallic/alchemical operations dropped in plant distillation)
- 1 SPLIT (generic -> differentiated)
- 3 EXPANDED (single -> multiple specialized)
- 1 REPLACED (technological evolution: dung heat -> water bath)

### Phase Coverage

Rupescissa maps overwhelmingly to core distillation phases:

| Brunschwig Phase | Actions | Covered by Rupescissa | Coverage |
|------------------|---------|-----------------------|----------|
| Distillation | 2 | 2 | 100% |
| Post-Distillation | 7 | 5 | 71.4% |
| Pre-Treatment | 5 | 2 | 40.0% |
| Preparation | 12 | 3 | 25.0% |
| Storage | 4 | 1 | 25.0% |
| Collection | 3 | 0 | 0% |
| Mid-Process | 9 | 0 | 0% |

Core distillation coverage: 64.3% vs non-core: 14.3%.

### What Brunschwig Adds

Six categories of additions beyond Rupescissa:

1. **Material-specific preparation** (9 actions: BORE, BREAK, CHOP, CLEAN, CRUSH, KILL, PLUCK, STRIP, WASH) -- Rupescissa is theory-level, doesn't specify how to prepare specific plants
2. **Mid-process monitoring** (9 actions: COOL, COVER, LUTE_JOINTS, LUTE_THERMAL, MONITOR_DRIPS, MONITOR_TEMP, PLUG, REGULATE_FIRE, REPLENISH) -- absent from BOTH texts as per-recipe instructions (OJLM-1 tacit knowledge boundary, Phase 371/C1056)
3. **Field collection** (3 actions: GATHER, HARVEST_TIMING, SELECT) -- Rupescissa starts at laboratory level
4. **Storage protocol** (3 actions: LABEL, RENEW, STORE) -- commercial/institutional concern absent from theoretical text
5. **Additional pre-treatment** (3 actions: DRY, MACERATE, MIX) -- refinements beyond generic putrefaction
6. **Additional post-distillation** (2 actions: MELT, POUR) -- handling operations

### Brunschwig -> Voynich (Prior Work)

Already mapped in F-BRU-011 (Three-Tier MIDDLE), F-BRU-012 (Preparation Mapping), Section X.31 (5 preparation MIDDLEs). Not re-derived here.

### Falsification Result

**PASS.** Core distillation coverage (64.3%) exceeds non-core (14.3%). Rupescissa maps to the procedural core (Distillation, Post-Distillation, Pre-Treatment), not peripheral phases.

### Constraints Referenced

C121, C591, C171, C935, F-BRU-011, F-BRU-012

---

## Analysis 3: Concealment Doctrine (Tier 4 -- Exploratory)

### Critical Framing

This analysis does NOT claim Voynich structural features "implement" concealment strategies. That would contradict:
- C120 (PURE_OPERATIONAL -- not language, cipher, or code)
- C119 (0 translation-eligible zones)
- C130/C132 (language/DSL encoding CLOSED)
- C207 (0/18 micro-cipher tests passed)

Instead: **Rupescissa documents the concealment culture of the tradition. The Voynich's non-semantic design is CONSISTENT WITH an artifact produced within this culture, but its structural properties have independent structural explanations.**

### Rupescissa's 7 Concealment Strategies

Extracted from the source text (145 total keyword hits across all chapters):

| Strategy | Hits | Example |
|----------|------|---------|
| Multiple names | 60 | 3 public names + 1 secret name for quintessence: aqua ardens, anima vini, aqua vitae + "quinta essentia" |
| Vocabulary obfuscation | 31 | "when you wish to CONCEAL it, call it quinta essentia" (Ch. V) |
| Audience restriction | 24 | "FOR THE SAINTS ALONE" / "Evangelical men" (Author's Intention) |
| Active denial | 17 | "not permit this book to come into the hands of the UNWORTHY" |
| Coded transmission | 5 | "no philosopher wrote the truth except FICTIVELY and under PARABLES" (Ch. XLIV) |
| Knowledge as danger | 4 | "how great an evil it would be" / "perverse use" / "persevere longer in evil" |
| Silence on highest | 4 | "I SHALL BY NO MEANS REVEAL" transmutation (Ch. XLIV) |

### Distribution by Chapter Type

| Chapter Type | Total Hits | Dominant Strategy |
|--------------|------------|-------------------|
| REMEDY | 60 | multiple_names (34), vocabulary_obfuscation (14) |
| THEORY | 42 | active_denial (12), audience_restriction (10) |
| PROCESS | 24 | multiple_names (13), vocabulary_obfuscation (6) |
| EXTRACTION | 12 | multiple_names (6), vocabulary_obfuscation (4) |
| DEGREE_CATALOG | 0 | -- |
| PHARMACOLOGICAL | 0 | -- |
| APPARATUS | 0 | -- |

Pattern: Concealment language concentrates in THEORY (doctrinal justification) and REMEDY (practical obfuscation through naming). DEGREE_CATALOG, PHARMACOLOGICAL, and APPARATUS chapters contain zero concealment language -- factual content is not concealed, only naming and access are controlled.

### Consistency Assessment (NOT Causal Mapping)

| Rupescissa Principle | Voynich Property | Consistent? | Independent Explanation |
|---------------------|-----------------|-------------|------------------------|
| Knowledge for practitioners only | Expert-reference archetype | Yes | C196/C197: 100% EXPERT_REFERENCE is a grammar property |
| Operational, not theoretical | PURE_OPERATIONAL | Yes | C120: Tier 0 structural fact, not concealment |
| Multiple names / obfuscation | Non-semantic notation | Yes | C119: zero translation-eligible zones follows from operational design |
| "Fictively and under parables" | Non-readable by outsiders | Yes | C130/C132 close language/DSL encoding; C207: 0/18 cipher tests |
| Degree-4 danger awareness | Hazard topology | Yes | C109: physical failure modes (F-BRU-023: THERMODYNAMIC_COHERENCE) |

**5/5 consistent, but ALL have independent structural explanations.**

### C476 Tension

C476 (COVERAGE_OPTIMALITY) states the Voynich system optimizes for complete discrimination coverage -- maximizing the ability to distinguish between instruction classes. This is the OPPOSITE of concealment (which would minimize discriminability).

**Resolution:** The system is optimized for INTERNAL discrimination (operators can distinguish all 49 classes) while being EXTERNALLY opaque (outsiders cannot read it). This is consistent with a guild-knowledge artifact: clear to insiders, opaque to outsiders. Rupescissa explicitly describes this model: "FOR THE SAINTS ALONE" -- knowledge should be accessible to the worthy, not obscured from everyone.

### Brunschwig as Anti-Pattern

Brunschwig (1500) is the historical anti-pattern to concealment:

| Dimension | Rupescissa | Brunschwig |
|-----------|-----------|------------|
| Audience | "Evangelical men" only | Anyone who can read German |
| Pedagogy | Assumes existing knowledge | Teaches from furnace construction (novice) |
| Transparency | "conceal it, call it quinta essentia" | Names everything in German, Latin, Greek, Arabic |
| Distribution | Manuscript (controlled copy) | Printed book (mass distribution) |

Brunschwig represents the "unsealing" -- making public what was previously restricted. The Voynich sits chronologically between Rupescissa's concealment doctrine and Brunschwig's public disclosure.

### Contraindications (Documented Per Expert Requirement)

- C120 (PURE_OPERATIONAL) is a grammar property, not concealment
- C119 (no translation zones) follows from non-semantic design
- C121 (49 classes) is distributional compression, not obfuscation
- C109 (hazard topology) encodes physical failure modes, not forbidden knowledge

### Falsification Result

**PASS with tension.** 5/5 consistent, but C476 creates genuine tension. The system optimizes for internal discrimination -- consistent with guild-knowledge (clear to insiders) but inconsistent with pure concealment (opaque to everyone). Documented, not resolved.

### Constraints Referenced

C120, C119, C121, C130, C132, C207, C109, C196, C197, C476, F-BRU-023

---

## Overall Assessment

Rupescissa establishes the intellectual and cultural context in which a document like the Voynich would be designed: operational focus, practitioner restriction, concealment awareness, degree-based classification. The Voynich's structural properties are consistent with this tradition but have independent structural explanations.

Three structural convergences documented (Phase 375):
1. **Degree-2 centrality** -- moderate intensity dominates in all three systems
2. **Core distillation preservation** -- the procedural core (distill, rectify, separate, collect) persists while periphery proliferates
3. **Concealment culture consistency** -- Voynich design is consistent with practitioner-restricted knowledge tradition

Four Galenic structural predictions tested (Phase 376): 3/4 PASS, 1 PARTIAL.

The lineage is cultural-intellectual, not direct textual. No direct transmission evidence exists.

### Convergent Validation Significance

The Voynich constraint system (923 constraints) was built entirely bottom-up from distributional statistics over token co-occurrence patterns. No constraint references medieval classification theory. The 5 hazard classes (C109) were discovered from zero-count bigrams. The lane split (C574) was discovered from EN subfamily analysis. Sister anticorrelation (C412) was discovered from folio-level correlation. The within-PREFIX frequency-complexity gradient was not even noticed until the Rupescissa question was asked.

Rupescissa's Galenic framework (1351) is completely independent of this computational derivation. The fact that it predicts multi-axis hazard (correct), exactly 2 orthogonal oppositions (correct, r=-0.064), ordered within-quality intensity (correct in 4/6 channels), and partial block-diagonal factorization (58.1%) constitutes convergent validation from an independent source. Individual test results may be "expected" from within the constraint system, but the overall fit between a 670-year-old classification framework and a computationally-derived structural analysis is non-trivial.

---

## Phase 376: Reverse Rupescissa Test (Galenic Framework Alignment)

**Date:** 2026-02-15 | **Tier:** 4 | **Result:** 3/4 PASS, 1 PARTIAL

Does Rupescissa's Galenic 4-quality x 4-degree organizational framework make structural predictions about the Voynich that survive falsification? Expert-advisor dropped 2 proposed tests as circular, restructured 2, added 2 novel tests.

### Test Results

| Test | Prediction | Result | Key Data |
|------|-----------|--------|----------|
| 1. Multi-Axis Hazard | >=3 independent failure axes | **PASS** | 5 dimensions: temporal, purity, spatial, flow, thermal. Only ENERGY_OVERSHOOT (6%) is thermal. |
| 2. Quality-Degree Factorization | Block-diagonal PREFIX x MIDDLE | **PARTIAL** | 58.1% of classifiable forbidden combos follow block structure (50-80% range). 158/201 combos unclassifiable (MIDDLEs outside defined families). |
| 3. Oppositional Pairing | Exactly 2 orthogonal axes | **PASS** | Lane split (QO/CHSH) and sister pair (ch/sh) have partial correlation r=-0.064 (near-perfect orthogonality). Kaiser: 2 PCs. ok/ot is NOT a 3rd independent axis. |
| 4. Degree Ordering | Ordered intensity within PREFIX channels | **PASS** | 4/6 channels show significant rank-intensity correlation (qo, ch, da, ot). sh and ok fail. Rarer MIDDLEs tend to be longer (rho=+0.25 to +0.37 in passing channels). |

### Key Findings

**Test 1** is the strongest result: 4/5 hazard classes are non-thermal (PHASE_ORDERING, COMPOSITION_JUMP, CONTAINMENT_TIMING, RATE_MISMATCH). Brunschwig collapsed to fire-only; the Voynich retains multi-axis hazard structure closer to Rupescissa's multi-quality model. Caveat: F-BRU-023 glosses are Tier 4.

**Test 3** reveals near-perfect orthogonality between the lane axis and sister axis (partial r=-0.064 controlling for QO density). This matches Rupescissa's requirement of 2 independent oppositional pairs (hot/cold, dry/humid). The raw correlation (rho=0.210) disappears when the shared QO component is controlled for.

**Test 2** is honestly PARTIAL. The block-diagonal model explains 58.1% of classifiable forbidden combos, but 78.6% (158/201) of total forbidden combos involve MIDDLEs outside the 4 defined families. The Voynich's 922 unique MIDDLEs resist simple 4-family classification -- the system is higher-dimensional than Rupescissa's 4-quality model.

**Test 4** shows within-PREFIX intensity ordering in 4/6 channels. Rarer MIDDLEs are systematically longer in qo (rho=0.248), ch (rho=0.365), and suffix-heavier in da (rho=0.589), ot (rho=0.528). This parallels Rupescissa's degree ordering within each quality. sh and ok show no significant ordering.

### Constraints Referenced

C109, C541, C622-C625, C911, C647, C574, C412, C929, C639, C605, C1001, C293, C267, F-BRU-023

---

## Result Files

### Phase 375

| File | Content |
|------|---------|
| `phases/RUPESCISSA_COMPARATIVE/results/degree_evolution.json` | Full degree system comparison |
| `phases/RUPESCISSA_COMPARATIVE/results/action_evolution.json` | Action vocabulary evolution |
| `phases/RUPESCISSA_COMPARATIVE/results/concealment_doctrine.json` | Concealment analysis |
| `phases/RUPESCISSA_COMPARATIVE/results/comparative_summary.json` | Combined findings |

**Script:** `phases/RUPESCISSA_COMPARATIVE/scripts/rupescissa_compare.py`

### Phase 376

| File | Content |
|------|---------|
| `phases/RUPESCISSA_REVERSE_TEST/results/test1_hazard_dimensionality.json` | Multi-axis hazard test |
| `phases/RUPESCISSA_REVERSE_TEST/results/test2_factorization.json` | Quality-degree factorization |
| `phases/RUPESCISSA_REVERSE_TEST/results/test3_oppositional_pairing.json` | Oppositional pairing |
| `phases/RUPESCISSA_REVERSE_TEST/results/test4_degree_ordering.json` | Degree ordering |
| `phases/RUPESCISSA_REVERSE_TEST/results/galenic_test_summary.json` | Combined results |

**Script:** `phases/RUPESCISSA_REVERSE_TEST/scripts/rupescissa_reverse_test.py`

---

## Phase 377: Galenic Enhancement Analysis (Synthesis)

**Date:** 2026-02-15 | **Tier:** 4 | **Type:** Synthesis (no new computation)

### Framing

Phase 376 confirmed the Voynich aligns with Rupescissa's Galenic framework (3/4 PASS). This phase asks: HOW did the Voynich enhance the original system?

Both systems solve the same structural problem: classifying operations and constraining hazardous transitions. Rupescissa's categories are SEMANTIC (hot, cold, dry, humid — named physical qualities). The Voynich's categories are DISTRIBUTIONAL (affordance bins, instruction classes — defined by co-occurrence patterns). The enhancement is: same problem, higher abstraction, greater precision.

The Brunschwig intermediate (1500) is included where it illuminates the trajectory.

### Enhancement Summary

| Axis | Galenic System | Voynich System | Enhancement | Key Constraint |
|------|---------------|----------------|-------------|----------------|
| 1. Classification | 4 named qualities | 9 affordance bins | 2.25x categories; named → distributional | C995 |
| 2. Degree granularity | 4 discrete degrees | 14-63 MIDDLEs/channel | 3.5-15.75x resolution; ordered spectra | C911, C982 |
| 3. Compound mechanism | Additive properties | Compatibility-graph mediation | 12x predictive differential | C475, C1053 |
| 4. Operation encoding | 12 named operations | 49 distributional classes | 4.1x count; semantic → distributional | C121 |
| 5. Hazard management | Binary prohibition | Precision engineering | PROHIBIT → ENGINEER | C494, C997 |
| 6. Hazard architecture | Narrative warnings | Topological forbidden graph | 1 axis → 5 dimensions; scalar → directed | C109 |

### Axis 1: Classification Resolution (4 → 9)

**Galenic:** Rupescissa classifies materials along 4 quality axes (hot, cold, dry, humid). Each quality is a named physical property. Classification is by sensory/theoretical assessment.

**Voynich:** 9 functional affordance bins (C995) with independent behavioral discrimination at p < 10^-30 on every tested dimension (hazard distance, lane distribution, within-line position, regime concentration, radial depth). Each bin has a multi-dimensional signature:
- STABILITY_CRITICAL: 0% QO (absolute exclusion), 79.4% CHSH, close to hazard (2.07)
- ENERGY_SPECIALIZED: 47.7% QO, distant from hazard (2.71), 89% REGIME_1
- PRECISION_SPECIALIZED: most distant from hazard (3.58), 71% REGIME_4

**Enhancement:** The Voynich doesn't just have more categories (9 vs 4) — each category is defined by a multi-dimensional behavioral fingerprint, not a named quality. This is a shift from ontological classification (what something IS) to functional classification (what something DOES in context).

### Axis 2: Degree Granularity (4 → 14-63)

**Galenic:** Each quality has 4 discrete degrees (1 = mild, 4 = extreme). Pepper is "hot in the 3rd degree." The degrees are ordinal labels assigned by authority.

**Voynich:** Within each PREFIX channel, MIDDLEs form frequency-ranked spectra with 14-63 distinct types. Phase 376 Test 4 confirmed rank-complexity ordering in 4/6 channels:
- qo: 63 MIDDLEs, rho=0.248 (rank vs length, p=0.05); rho=-0.287 (rank vs suffix, p=0.02)
- ch: 60 MIDDLEs, rho=0.365 (rank vs length, p=0.004)
- da: 14 MIDDLEs, rho=0.589 (rank vs suffix, p=0.027)
- ot: 25 MIDDLEs, rho=0.528 (rank vs suffix, p=0.007)

Rarer MIDDLEs are systematically longer or suffix-heavier — a frequency-complexity gradient.

**Enhancement:** 4 fixed labels → high-resolution ordered discrete spectrum. The degrees are not assigned by authority but emerge from distributional frequency. The ordering is statistical, not categorical. This is consistent with a system designed for finer discrimination than 4 levels can provide, within the same quality-axis framework.

### Axis 3: Compound Mechanism (Additive → Graph-Mediated)

**Galenic:** Compound properties combine by addition. Pepper = hot-3 + dry-2. Any quality can combine with any other at any degree. The rules are: add the properties; warn if any reaches degree 4.

**Voynich:** Compound MIDDLEs (C935) contain atoms that predict body vocabulary at 71.6% hit rate. But this prediction is mediated by the C475 compatibility graph (C1053): atoms that are mutually C475-compatible predict body MIDDLEs at **46.2%**, while incompatible atoms predict at only **3.9%** — a 12x differential (Wilcoxon p=0.002).

**Enhancement:** The combination rules are not "anything goes" — they are structurally constrained by a compatibility graph. A compound MIDDLE's atoms must be compatible (per C475) to contribute to paragraph body content. This is the difference between "list your ingredients" (Galenic) and "specify ingredients that can legally co-occur in this structural context" (Voynich). The graph mediates combination.

### Axis 4: Operation Encoding (12 Named → 49 Distributional)

**Galenic:** 12 named physical operations (DISTILL, CIRCULATE, RECTIFY, SUBLIME, PUTREFY, CALCINE, DISSOLVE, GRIND, SEAL, HEAT_DUNG, SEPARATE, COLLECT). Each is a specific physical action with a named referent.

**Brunschwig:** 36+ named operations. Growth comes from differentiation (PUTREFY → FERMENT + DIGEST) and expansion (GRIND → GRIND + POUND + POWDER). Still named, still referential.

**Voynich:** 49 distributional equivalence classes (C121, Tier 0). 479 unique token types compress to 49 classes preserving transition structure (9.8x compression). Classes are defined by co-occurrence patterns, not named operations. The encoding is abstract: what matters is which tokens can follow which, not what any token "means."

**Enhancement:** This is the deepest qualitative shift. Rupescissa and Brunschwig name their operations in human language. The Voynich encodes its operations in a distributional grammar. The 49 classes are not "49 named operations" but "49 positions in a co-occurrence network." The growth from 12 → 36 (Rupescissa → Brunschwig) is quantitative (more names). The growth from 36 → 49 (Brunschwig → Voynich) is qualitative (names → distributional structure).

Phase 375 showed the trajectory: Rupescissa covers 64.3% of core distillation actions vs 14.3% non-core. The Voynich achieves 100% coverage of its operational grammar (C124) — every token participates.

### Axis 5: Hazard Management (Prohibition → Engineering)

**Galenic:** "USE WITH EXTREME CAUTION. These can burn the stomach." (Ch. XXI). Degree 4 is dangerous-but-documented: 6/43 hot materials (14%) are degree 4. The management strategy is: warn, advise caution, document danger.

**Brunschwig:** Categorical prohibition. 0/245 recipes at D4. "Nature rejects all coercion." The management strategy is: eliminate the dangerous category entirely.

**Voynich:** Precision-constrained execution (C494, Tier 3). REGIME_4 appears in 25/83 folios — too frequent to be prohibition. It encodes tight control: lowest qo_density (gentle processing), highest LINK ratio (25% monitoring overhead), forbidden HIGH_IMPACT (no aggressive intervention). Safety buffers (C997): 22 tokens at 0.12% buffer rate, concentrated at HUB↔STABILITY interface, using lane-crossing as a structural safety mechanism.

**Enhancement:** The progression PROHIBIT → RESTRICT → ENGINEER (Phase 375) is the key finding. The Galenic system says "this is dangerous." Brunschwig says "don't do this." The Voynich says "do this with precision constraints and structural safety buffers." The hazard is not avoided — it is managed through grammar-level enforcement (C458: hazard clamped CV 0.04-0.11, recovery free CV 0.72-0.82).

### Axis 6: Hazard Architecture (Narrative → Topological)

**Galenic:** Warnings are per-material, scalar (degree of danger), and narrative ("USE WITH EXTREME CAUTION"). The architecture is a list of materials with danger ratings.

**Voynich:** 17 forbidden transitions across 5 failure classes (C109, Tier 0):
- PHASE_ORDERING (7, 41%) — material sequencing errors
- COMPOSITION_JUMP (4, 24%) — purity crossover
- CONTAINMENT_TIMING (4, 24%) — overflow/pressure
- RATE_MISMATCH (1, 6%) — flow balance
- ENERGY_OVERSHOOT (1, 6%) — thermal damage

65% of forbidden transitions are asymmetric (C111): A→B forbidden does not imply B→A forbidden. The hazard system is a directed graph, not a scalar rating. Safety buffers (C997) are sparse (0.12%) and concentrated at the HUB↔STABILITY interface, using lane-crossing tokens (QO-articulated) to break dangerous CHSH→CHSH sequences.

**Enhancement:** One dimension (degree of danger) → five independent failure dimensions. Scalar warning → directed graph with asymmetric forbidden transitions. Per-material rating → topology-level enforcement embedded in the grammar. Phase 376 Test 1 confirmed only 1/5 hazard classes (ENERGY_OVERSHOOT, 6%) is thermal — the other 4 are non-thermal, matching Rupescissa's multi-quality model but far exceeding it in structural precision.

### The Enhancement Pattern

Across all 6 axes, a consistent pattern emerges:

1. **Abstraction increase:** Named → distributional. Every Galenic category defined by a human-assigned name (hot, degree 3, DISTILL) becomes a Voynich category defined by distributional behavior (affordance bin signature, frequency-rank spectrum, co-occurrence class).

2. **Resolution increase:** Coarse → fine. 4 qualities → 9 bins. 4 degrees → 14-63 MIDDLEs. 12 operations → 49 classes. The Voynich consistently operates at higher granularity within the same structural framework.

3. **Constraint formalization:** Narrative → structural. Warnings → forbidden transitions. Prohibition → precision engineering. Additive combination → compatibility graph. Every Galenic guideline expressed in human language becomes a Voynich constraint enforced by grammar.

4. **Dimensionality preservation with enhancement:** The Galenic framework's key structural properties (multi-axis classification, compound description, ordered degrees, oppositional pairs, hazard awareness) are ALL preserved. But each is enhanced: more axes, finer granularity, structural enforcement, graph-mediated combination.

This pattern is consistent with a designer who understood the Galenic organizational LOGIC and re-implemented it in a more precise notation system. The enhancement is systematic, not random — it affects every structural dimension in the same direction (toward greater abstraction, resolution, and formal constraint).

### What This Does NOT Claim

1. **No historical transmission.** The Galenic framework is the intellectual context, not a source text. No direct textual lineage is claimed.

2. **No semantic recovery.** The enhancements are STRUCTURAL. Saying "the Voynich enhanced 4 qualities to 9 bins" does not reveal what the 9 bins encode substantively. C120 (PURE_OPERATIONAL) and C119 (0 translation-eligible zones) remain Tier 0.

3. **No decipherment implications.** Understanding the enhancement pattern does not decode the manuscript. The distributional grammar is abstract — C121's 49 classes are not "49 named operations" waiting to be translated.

4. **No claim of unique fit.** Other organizational frameworks might also show structural parallels. The Galenic framework is tested because Rupescissa sits in the same tradition as Brunschwig, which already shows alignment (Phases 355-371). The fit is tested, not asserted.

5. **Tier 4 throughout.** Every enhancement mapping requires accepting the Galenic interpretive frame. The Voynich-side constraints (C109, C121, C475, C995, C997, C982, C1053) are Tier 0-2. The MAPPING to Galenic categories is Tier 4.

---

## Phase 378: Galenic Recipe Physics Prediction (3-Test Battery)

**Phase:** 378 | **Tier:** 4 | **Date:** 2026-02-15

### Purpose

Tests whether the Galenic framework makes specific, falsifiable *physics* predictions about the Voynich — not just structural correspondence (F-RUP-001) but recipe-level mapping. Three tests, each with pre-registered falsification criteria. Expert-advisor designed (dropped 3 originally proposed tests as pre-answered by existing constraints).

### Results

| Test | Prediction | Verdict | Key Metric |
|------|-----------|---------|------------|
| T1: Degree-Hazard Correlation | Rare (high-degree) MIDDLEs are dangerous | **FAIL** | All 23 HUB MIDDLEs in Q1 (most frequent) |
| T2: Quality Opposition Directionality | Cross-quality transitions are disproportionately forbidden | **FAIL** | 7/8 cross-quality but p=0.177 (permutation) |
| T3: Galenic Degree Recovery Residual | Galenic intensity explains AXM residual beyond REGIME | **FAIL** | Partial rho=0.022, p=0.854 |

**Overall: 0/3 PASS, 0/3 PARTIAL, 3/3 FAIL**

### What the FAILs Reveal

**T1: Hazard is topological, not scalar.** In Galenic medicine, danger scales with intensity — degree 4 is rare and extreme. In the Voynich, danger is *hub-mediated* (C1000): ALL 23 HUB MIDDLEs are in the most-frequent quartile. Hazard isn't about rarity; it's about connectivity. The forbidden transitions go through the network's most-trafficked nodes, not its rarest. This is the clearest break from Galenic degree logic.

**T2: Quality assignment is dominated by STABILITY.** 13/23 HUB MIDDLEs are CHSH-dominant (assigned STABILITY quality). With such skew, 9/17 forbidden pairs have at least one unclassifiable MIDDLE (c, he, edy are non-HUB), and of the 8 valid pairs, the cross-quality rate (87.5%) doesn't exceed the permutation null (p=0.177). The Voynich doesn't distribute MIDDLEs evenly across 4 quality axes — the CHSH lane dominates HUB. This is consistent with C1000's finding that PREFIX creates lane separation (Cramér's V=0.689), but the lane separation doesn't map to 4 equal Galenic qualities.

**T3: Galenic degree adds nothing to recovery.** The Galenic intensity score has near-zero correlation with AXM residual (raw rho=-0.007, partial rho=0.022). Galenic degree is not even strongly confounded with REGIME (rho=0.153, p=0.200). The 57% irreducible residual (C1035) remains genuinely irreducible — it's not Galenic degree hiding behind REGIME.

### Structural Implications

The 3 FAILs together map the **boundary of the Galenic analogy**:

1. **Framework-level alignment holds** (F-RUP-001: 6/6 directional enhancement axes). The Voynich's *organizational architecture* aligns with Galenic logic.

2. **Recipe-level prediction fails** (Phase 378: 0/3 tests). The Voynich's *specific physics* (which MIDDLEs are dangerous, which transitions are forbidden, how folios recover) do NOT follow Galenic rules.

3. **The break point is topology vs. scalar.** The Galenic system is fundamentally scalar (4 qualities × 4 degrees = 16 cells). The Voynich system is fundamentally topological (23 hub nodes, 17 forbidden transitions, 5 failure classes, compatibility graphs). The organizational *frame* transferred; the operational *mechanism* did not.

### Files

- Script: `phases/GALENIC_RECIPE_PREDICTION/scripts/galenic_recipe_prediction.py`
- T1: `phases/GALENIC_RECIPE_PREDICTION/results/t1_degree_hazard.json`
- T2: `phases/GALENIC_RECIPE_PREDICTION/results/t2_quality_directionality.json`
- T3: `phases/GALENIC_RECIPE_PREDICTION/results/t3_degree_recovery.json`
- Summary: `phases/GALENIC_RECIPE_PREDICTION/results/galenic_recipe_summary.json`
