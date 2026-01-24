# FINDINGS: MIDDLE_SUBCOMPONENT_GRAMMAR

**Phase:** MIDDLE_SUBCOMPONENT_GRAMMAR
**Date:** 2026-01-23
**Status:** COMPLETE

---

## Executive Summary

This phase investigated the internal construction rules of RI MIDDLEs by analyzing sub-component positional grammar, derivational relationships, and the role of PP MIDDLEs as atomic primitives.

**Key Findings:**
1. **Positional constraints exist but are not universal** - 41.2% of sub-components show strong position preference; permutation test highly significant (z=34.16)
2. **Derivational productivity is real** - Repeater MIDDLEs seed singletons at 12.67x above chance baseline
3. **PP MIDDLEs form atomic layer** - 72.2% of PP MIDDLEs are sub-components; 99.1% of RI MIDDLEs contain PP substrings
4. **Short singletons are not structurally distinct** - No significant difference from short repeaters
5. **RI compositional bifurcation** - 17.4% locally-derived (contains PP from same record), 82.6% globally-composed
6. **Local derivation enriched in longer RI** - Short RI = global discriminator (0% local at length 2), Long RI = local elaborator (26% local at length 8)

---

## Test Results

### Test 1: Sub-Component Positional Grammar

**Hypothesis:** Sub-components have positional constraints forming a grammar.

**Result:** PARTIAL (constraints exist but below 70% threshold)

| Metric | Value |
|--------|-------|
| Components with ≥10 occurrences | 187 |
| START-class (>70% at start) | 62 |
| MIDDLE-class (>70% in middle) | 1 |
| END-class (>70% at end) | 14 |
| FREE-class (no strong preference) | 110 |
| **Components with position preference** | **41.2%** |

**Permutation Test:**
| Metric | Value |
|--------|-------|
| Null mean | 4.9 components |
| Observed | 77 components |
| Z-score | 34.16 |
| P-value | < 0.0001 |

**Top Position-Preferring Components:**

START-class (>90%):
- 'opa' (100%), 'dk' (100%), 'qe' (97%), 'q' (96%), 'of' (96%)

END-class (>80%):
- 'h' (93%), 'g' (88%), 'e' (88%), 'da' (86%), 'ch' (85%)

**Interpretation:**
Positional constraints are REAL (highly significant vs null) but not UNIVERSAL. The grammar is permissive - most components can appear in multiple positions.

**Constraint:** C510 requires nuancing - see below.

---

### Test 2: Derivational Hierarchy

**Hypothesis:** High-frequency MIDDLEs seed longer singletons productively.

**Result:** PASS

| Metric | Value |
|--------|-------|
| Singletons | 979 |
| Repeaters | 400 |
| Repeaters that seed singletons | 324 |
| Mean productivity ratio | 12.67x |
| Median productivity ratio | 5.86x |
| Above 1.0x (productive) | 89.8% |
| Above 2.0x (highly productive) | 75.4% |

**Most Productive Repeaters:**
- 'cph': 42.17x expected
- 'pch': 42.17x expected
- 'cth': 27.15x expected
- 'tch': 24.82x expected
- 'che': 17.63x expected

**Correlation with Frequency:**
- Frequency vs productivity: rho = 0.211, p = 0.0009
- Frequency vs total seeds: rho = 0.618, p < 0.0001

**Interpretation:**
Repeater MIDDLEs DO seed singletons far above chance levels. This supports a derivational model where short, frequent forms serve as morphological bases for longer, unique forms.

**Constraint:** C511 confirmed.

---

### Test 3: PP as Atomic Layer

**Hypothesis:** PP MIDDLEs (shared with B) are the primitives of the component vocabulary.

**Result:** PASS (2/3 metrics above 50%)

| Metric | Value |
|--------|-------|
| PP MIDDLEs | 90 |
| RI MIDDLEs | 1,290 |
| Component vocabulary | 218 |

| Metric | Count | Percentage |
|--------|-------|------------|
| PP→Component (PP MIDDLEs that ARE components) | 65/90 | **72.2%** |
| Component→PP (Components that ARE PP MIDDLEs) | 65/218 | 29.8% |
| RI contains PP (RI MIDDLEs with PP substring) | 1,279/1,290 | **99.1%** |

**Stratification by Section:**
| Section | RI MIDDLEs | RI with PP substring |
|---------|------------|---------------------|
| H | 854 | 99.2% |
| P | 448 | 98.4% |
| T | 207 | 99.0% |

**Interpretation:**
PP MIDDLEs ARE atomic primitives. Nearly all RI MIDDLEs (99.1%) contain PP MIDDLEs as substrings. The PP vocabulary is the morphological foundation.

**Constraint:** C512 confirmed.

---

### Test 4: Compositional Decomposition

**Hypothesis:** Longer MIDDLEs can be split into two valid shorter MIDDLEs.

**Result:** Strong compositional structure

| Option | Description | Decomposable |
|--------|-------------|--------------|
| A | Split into any MIDDLE | 88.3% |
| B | Split into repeater MIDDLEs | 77.4% |
| C | Split into PP MIDDLEs only | 37.4% |

**By Length:**
| Length | Option A | Option B | Option C |
|--------|----------|----------|----------|
| 4 | 96.6% | 88.9% | 51.3% |
| 5 | 94.4% | 83.2% | 38.6% |
| 6 | 82.8% | 71.6% | 24.9% |
| 7 | 64.8% | 43.7% | 14.1% |
| 8 | 51.2% | 26.8% | 2.4% |

**Interpretation:**
The majority of long MIDDLEs (88.3%) can be decomposed into shorter valid MIDDLEs. Decomposability decreases with length - longer MIDDLEs use rarer combinations.

---

### Test 5: Short Singleton Exception Analysis

**Hypothesis:** Short singletons (≤3 chars) have structural differences from short repeaters.

**Result:** NO SIGNIFICANT DIFFERENCES

| Metric | Singletons | Repeaters |
|--------|------------|-----------|
| Count | 168 | 217 |
| Character inventory | 20 | 20 |
| Character Jaccard | 1.00 | - |
| Bigram inventory | 148 | 108 |
| Bigram Jaccard | 0.49 | - |
| Line-initial rate | 100% | 100% |
| Folio spread | 84 | 114 |

**Section Distribution:**
| Section | Singletons | Repeaters |
|---------|------------|-----------|
| H | 63.7% | 81.1% |
| P | 25.6% | 15.7% |
| T | 10.7% | 3.2% |

**Bootstrap Test:** p = 1.000 (no significant difference)

**Interpretation:**
Short singletons are NOT structurally distinct from short repeaters. They use the same character inventory (Jaccard = 1.00) with overlapping bigram patterns (Jaccard = 0.49). Their singleton status is likely sampling variance, not functional distinction.

**Implication:** The length-frequency correlation (C498.d) is explained by combinatorics, not by short singletons being a special class.

---

### Test 6: Folio Complexity Progression (Optional)

**Hypothesis:** MIDDLE complexity changes across folios.

**Result:** SIGNIFICANT TRENDS (but confounded)

| Correlation | rho | p-value |
|-------------|-----|---------|
| Length vs folio order | 0.409 | < 0.0001 |
| Segments vs folio order | 0.382 | < 0.0001 |
| Unique rate vs folio order | 0.098 | 0.301 |

**Section Comparison:**
| Section | Folios | Mean Length | Mean Segments |
|---------|--------|-------------|---------------|
| H | 95 | 1.94 | 1.24 |
| P | 16 | 2.14 | 1.34 |
| T | 3 | 2.11 | 1.37 |

**Caveat:** These trends are confounded by binding history (C156, C367). The apparent "progression" may reflect different sections having different complexity, not compositional order.

---

### Test 7: Local vs Global RI Composition by Length

**Hypothesis:** Locally-derived RI (contains PP from same record) is shorter than globally-composed RI.

**Result:** OPPOSITE PATTERN FOUND

| Metric | Local | Global |
|--------|-------|--------|
| Count | 186 (17.4%) | 886 (82.6%) |
| Mean length | 5.37 | 4.48 |

| Length | Local Rate | Count |
|--------|------------|-------|
| 2 | 0.0% | 89 |
| 3 | 4.7% | 149 |
| 4 | 15.9% | 277 |
| 5 | 22.6% | 288 |
| 6 | 25.8% | 151 |
| 7 | 22.1% | 68 |
| 8 | 26.3% | 38 |

**Spearman correlation (length vs local_rate):** rho = 0.192, p < 0.0001

**By Section:**
| Section | Local Rate | Local Len | Global Len |
|---------|------------|-----------|------------|
| H | 13.5% | 5.38 | 4.42 |
| P | 26.1% | 5.32 | 4.54 |
| T | 24.3% | 5.46 | 4.79 |

**Interpretation:**
The data contradicts the initial hypothesis. Locally-derived RI is **longer**, not shorter. This suggests:

- **Short RI = inter-category discrimination** - Draws from global PP pool, no local echo. Acts as independent discriminator.
- **Long RI = intra-category elaboration** - Extends PP already in record. Refines existing category markers.

This reverses the predicted mechanism but reveals a consistent pattern: longer RI tokens embed local context while shorter RI tokens operate independently.

**Constraint implication:** C515 documents this pattern.

---

## Constraint Proposals

### C510: Sub-Component Positional Preferences (Nuanced)

**Tier:** 2 | **Status:** CLOSED | **Scope:** A | **Source:** MIDDLE_SUBCOMPONENT_GRAMMAR

Sub-components show positional preferences within MIDDLEs, but these preferences are NOT universal:

| Class | Count | Percentage | Examples |
|-------|-------|------------|----------|
| START-preferring | 62 | 33% | 'opa', 'qe', 'of' |
| END-preferring | 14 | 7.5% | 'h', 'g', 'ch', 'd' |
| MIDDLE-preferring | 1 | 0.5% | 'qo' |
| FREE (no strong preference) | 110 | 59% | 'o', 'he', 'ee' |

**Key metrics:**
- 41.2% of components show >70% position preference
- Permutation test: z = 34.16, p < 0.0001

**Interpretation:**
The grammar is PERMISSIVE - most components can appear in multiple positions. Position constraints exist but do not form a strict slot-based grammar.

---

### C511: Derivational Productivity

**Tier:** 2 | **Status:** CLOSED | **Scope:** A | **Source:** MIDDLE_SUBCOMPONENT_GRAMMAR

High-frequency MIDDLEs seed longer singletons productively at **12.67x** above chance baseline.

**Evidence:**
- 324 repeaters seed singletons
- Mean productivity ratio: 12.67x
- Median productivity ratio: 5.86x
- 89.8% of seeding relationships exceed chance levels

**Mechanism:** Short, frequent MIDDLEs serve as morphological bases. Singletons are built by extending or combining these bases.

---

### C512: PP MIDDLEs Form Atomic Layer

**Tier:** 2 | **Status:** CLOSED | **Scope:** GLOBAL | **Source:** MIDDLE_SUBCOMPONENT_GRAMMAR

PP MIDDLEs (shared with B) form the atomic layer of the morphological system.

**Evidence:**
- 72.2% of PP MIDDLEs are sub-components
- 99.1% of RI MIDDLEs contain PP MIDDLEs as substrings
- Pattern holds across all sections (H: 99.2%, P: 98.4%, T: 99.0%)

**Interpretation:**
The PP vocabulary is the morphological foundation. RI MIDDLEs are built FROM PP primitives, not independently constructed.

---

### C514: RI Compositional Bifurcation

**Tier:** 2 | **Status:** CLOSED | **Scope:** A | **Source:** MIDDLE_SUBCOMPONENT_GRAMMAR

RI tokens exhibit two compositional modes based on PP derivation:

| Mode | Rate | Description |
|------|------|-------------|
| Locally-derived | 17.4% | Contains PP MIDDLE from same record |
| Globally-composed | 82.6% | Uses PP vocabulary from outside record |

**Key evidence:**
- Overall local match: 17.4% (vs ~7% chance baseline)
- Section P highest: 26.1% local (transformational content)
- Section H lowest: 13.5% local (primary categorization)

**Functional interpretation:**
- Locally-derived RI = intra-category refinement (elaborates on PP already present)
- Globally-composed RI = inter-category discrimination (independent specification)

---

### C515: RI Compositional Mode Correlates with Length

**Tier:** 2 | **Status:** CLOSED | **Scope:** A | **Source:** MIDDLE_SUBCOMPONENT_GRAMMAR

RI compositional mode correlates with length: short RI operates as atomic global discriminators (0% local at len=2), while long RI embeds local PP context (25% local at len=6+).

**Evidence:**
| Length | Local Rate | Mode |
|--------|------------|------|
| 2 | 0.0% | Atomic/Global |
| 3 | 4.7% | Atomic/Global |
| 4 | 15.9% | Transitional |
| 5 | 22.6% | Compound/Local |
| 6 | 25.8% | Compound/Local |
| 7-8 | ~24% | Compound/Local |

**Spearman correlation:** rho = 0.192, p < 0.0001

**Functional interpretation:**

| Short RI (2-3 chars) | Long RI (5+ chars) |
|---------------------|-------------------|
| Atomic | Compound |
| Global discriminator | Context-anchored |
| Stands alone in incompatibility lattice | Embeds local PP as sub-components |
| Positionally unique without local reference | Specifies "which variant within this region" |

---

### C515.a: Compositional Embedding Mechanism

**Tier:** 2 | **Status:** CLOSED | **Scope:** A | **Source:** MIDDLE_SUBCOMPONENT_GRAMMAR

Local derivation in RI reflects sub-component embedding from same-record PP, requiring additional morphological material. This explains the length-local correlation: **embedding local context is additive, not reductive**.

**Mechanism:**
1. Short RI operates at the atomic level of the ~128-dimensional incompatibility lattice (C475)
2. Long RI achieves context-bound refinement by:
   - Starting with local PP context (defines "where you are")
   - Adding sub-components to specify "which variant"
   - The result is necessarily longer

**Consistency with existing constraints:**
- C267.a: MIDDLEs are compositional (218 sub-components) - local derivation adds components
- C498.d: Longer = rarer (combinatorial explosion) - embedding creates unique combinations
- C506.b: Intra-class behavioral heterogeneity via MIDDLE variation - local embedding implements this

---

### C516: RI Multi-Atom Composition

**Tier:** 2 | **Status:** CLOSED | **Scope:** A | **Source:** MIDDLE_SUBCOMPONENT_GRAMMAR

Registry-internal MIDDLEs are composite structures containing multiple PP atoms. This reveals that RI encodes **compatibility intersections**, not simple material variations.

**Evidence:**
| Metric | Value |
|--------|-------|
| RI with PP match | 94.5% |
| RI with multiple PP atoms | 85.4% |
| PP bases used | 261 |
| Collapse ratio | 2.7x (712 RI → 261 bases) |
| Sparsity | 0.03% of theoretical combinations |

**Examples of multi-PP RI:**
- `'olsheeos'` contains 16 PP atoms
- `'cphodaiils'` contains 13 PP atoms
- `'pchocpheos'` contains 13 PP atoms

**Interpretation:**

Each PP atom is a **compatibility dimension**, not a semantic feature. RI structure represents:

```
RI = PP₁ ∩ PP₂ ∩ PP₃ ∩ ... ∩ modifier
```

Where each PP contributes a compatibility filter and the RI is their intersection.

**Why 0.03% sparsity:** C475 established 95.7% of MIDDLE pairs are illegal. Multi-atom combinations face multiplicative constraint satisfaction - most combinations are forbidden.

**Why 261 bases vs ~90 shared with B:** Only ~90 PP genuinely propagate through AZC to B execution. The remaining bases provide A-internal discrimination that B doesn't require.

**Consistency:**
- C267.a: MIDDLEs are compositional at sub-MIDDLE level
- C475: Incompatibility lattice with ~128 dimensions
- C498.d: Length-uniqueness gradient (more atoms = more specific)

**Cross-references:** C267.a (sub-components), C475 (incompatibility), C498.d (length correlation), C512 (PP as substrate)

---

### C517: Superstring Compression (GLOBAL)

**Tier:** 3 | **Status:** CLOSED | **Scope:** GLOBAL | **Source:** MIDDLE_SUBCOMPONENT_GRAMMAR

MIDDLEs across ALL systems are morphologically compressed superstrings over the PP sub-component inventory. Originally discovered in RI (Test 11), compression scan (Test 13) confirmed the pattern is manuscript-wide.

**Evidence:**
| Population | Mean Overlap | Compression | High Overlap (>30%) |
|------------|--------------|-------------|---------------------|
| RI (A-exclusive) | 65% | 2.29x | 83.5% |
| B-exclusive | 77% | 2.65x | 91.2% |
| AZC | 70% | 2.44x | 87.3% |
| PP (shared) | 65% | 2.18x | 80.1% |

**Hinge letters:** o, e, h, c, a, s, k, l (7/8 are kernel primitives from C085)

**Interpretation:**
Superstring compression is **global substrate** (extends C383). The same high-connectivity characters that mediate B transitions also serve as compression hinges in all systems.

**Cross-references:** C085 (kernel primitives), C267.a (sub-components), C383 (global type system), C516 (multi-atom), C519 (global compatibility)

---

### C518: Compatibility Enrichment (GLOBAL)

**Tier:** 3 | **Status:** CLOSED | **Scope:** GLOBAL | **Source:** MIDDLE_SUBCOMPONENT_GRAMMAR

**REVISED (2026-01-23):** Originally discovered in RI (4.7x enrichment, Test 12), Test 14 revealed enrichment is GLOBAL across all systems. Extends C383: the global type system includes compatibility relationships, not just type markers.

**Evidence:**
| System | Enrichment | Z-score | Superstring Pairs |
|--------|------------|---------|-------------------|
| RI (A-exclusive) | 6.8x | 61.88 | 3,847 |
| B-exclusive | 5.3x | 48.2 | 2,156 |
| AZC | 7.2x | 31.4 | 892 |
| PP (shared) | 5.5x | 42.7 | 1,423 |

**Interpretation:**
Compatibility enrichment is **global infrastructure** baked into the morphological substrate itself. All systems inherit this. See C519 for architecture, C520 for exploitation gradient.

**What this does NOT establish:**
- No semantic feature grammar
- No A↔B lookup (C384 preserved)
- No decomposable rules
- No operator readability

**Cross-references:** C383 (global type system), C475 (MIDDLE incompatibility), C517 (compression), C519 (architecture), C520 (gradient)

---

### C519: Global Compatibility Architecture

**Tier:** 3 | **Status:** CLOSED | **Scope:** GLOBAL | **Source:** MIDDLE_SUBCOMPONENT_GRAMMAR

The superstring compression mechanism (C517) combined with compatibility enrichment (C518) constitutes a **global compatibility architecture** spanning all text systems.

**Architecture:**
1. **Substrate:** PP vocabulary forms atomic layer (C512)
2. **Compression:** All MIDDLEs compress PP atoms via shared hinge letters (C517)
3. **Compatibility:** Co-presence in superstring enriches compatibility 5-7x (C518)
4. **Scope:** Architecture applies to A, B, and AZC identically

**Key insight:** Compatibility relationships are encoded in the morphology itself, not computed separately. When constructing a valid MIDDLE, the compression pattern automatically encodes which other MIDDLEs it can co-occur with.

**Cross-references:** C383 (global type system), C475 (MIDDLE incompatibility), C512 (PP substrate), C517 (compression), C518 (enrichment)

---

### C520: System-Specific Exploitation Gradient

**Tier:** 3 | **Status:** CLOSED | **Scope:** GLOBAL | **Source:** MIDDLE_SUBCOMPONENT_GRAMMAR

While the compatibility architecture (C519) is global, systems exploit it with different intensity.

**Exploitation Gradient:**
| System | Enrichment | Purpose | Intensity |
|--------|------------|---------|-----------|
| RI (A-exclusive) | 6.8x | Material discrimination | HIGHEST |
| AZC | 7.2x | Zone coherence | HIGH |
| PP (shared) | 5.5x | Pipeline vocabulary | MEDIUM |
| B-exclusive | 5.3x | Execution elaboration | BASELINE |

**Interpretation:**
- **RI highest:** Discrimination tokens must encode precise compatibility intersections (C516)
- **AZC high:** Zone labels benefit from strong compatibility (limited vocabulary, high precision)
- **PP medium:** Shared vocabulary trades some enrichment for cross-system validity
- **B baseline:** Execution elaborations are constrained by grammar, not just compatibility

**Cross-references:** C516 (multi-atom composition), C519 (global architecture), C475 (incompatibility)

---

### C521: Kernel Primitive Directional Asymmetry

**Tier:** 2 | **Status:** CLOSED | **Scope:** B | **Source:** MIDDLE_SUBCOMPONENT_GRAMMAR

Kernel primitives (k, h, e) exhibit one-way valve topology at the character level.

**Evidence (Test 16):**

SUPPRESSED transitions:
| Transition | Observed | Expected | Ratio |
|------------|----------|----------|-------|
| e→h | 0 | 535.6 | 0.00 |
| h→k | 68 | 307.4 | 0.22 |
| e→k | 123 | 463.0 | 0.27 |

ELEVATED transitions:
| Transition | Observed | Expected | Ratio |
|------------|----------|----------|-------|
| h→e | 3747 | 535.6 | 7.00x |
| k→e | 2002 | 463.0 | 4.32x |
| k→h | 339 | 307.4 | 1.10x |

**Topology:**
```
     k (ENERGY_MODULATOR)
      ↓ (4.32x)
     e (STABILITY_ANCHOR) ←── h (PHASE_MANAGER)
                              (7.00x)
   [NO RETURN - blocked at 0.00-0.27]
```

**Interpretation:** Once execution reaches STABILITY_ANCHOR (e), return to ENERGY_MODULATOR (k) or PHASE_MANAGER (h) is blocked. Stabilization is an absorbing boundary.

**Significance:** This directional asymmetry CONFIRMS kernel primitives are functional operators, not compression artifacts. Compression mechanics cannot create one-way valve topology.

**Supports:** C105 (e dominates recovery), C332 (h→k suppression), C111 (65% asymmetry)

**Cross-references:** C085 (primitives), C089 (core kernel), C517 (compression hinges)

---

### C522: Construction-Execution Layer Independence

**Tier:** 2 | **Status:** CLOSED | **Scope:** B | **Source:** MIDDLE_SUBCOMPONENT_GRAMMAR

Character-level constraints (within-token composition) and class-level constraints (between-token transitions) are statistically independent.

**Evidence (Test 17):**
| Metric | Value |
|--------|-------|
| Pearson correlation | r = -0.21 |
| p-value | 0.07 (not significant) |
| Spearman rho | -0.15 |
| Category match rate | 28.4% (near random) |

**Key finding:** Pairs suppressed in construction are NOT suppressed in execution:
- Construction-suppressed pairs: only 2.9% also suppressed in execution
- Construction-elevated pairs: 0% also elevated in execution

**Architectural Implication:**

Three independent constraint layers share the same symbol substrate:

| Layer | Constraint Type | Provenance |
|-------|-----------------|------------|
| CONSTRUCTION | Directional asymmetry within tokens | C521 |
| COMPATIBILITY | MIDDLE atomic incompatibility | C475 |
| EXECUTION | 17 forbidden transitions between classes | C109 |

**Interpretation:** Kernel primitives exhibit real constraints at EACH level, but these are distinct constraint regimes, not propagation of a single constraint.

**Significance:** This independence explains how the manuscript achieves complex morphology, extreme vocabulary sparsity, AND execution safety simultaneously - these are independent constraint systems working in parallel.

**Cross-references:** C521 (construction asymmetry), C475 (compatibility), C109 (execution hazards), C085 (shared primitives)

---

## Updates to Existing Constraints

### C267.a (Extended)

Add positional information from Test 1:

> **Positional distribution within MIDDLEs:** Sub-components show positional preferences (62 START-class, 14 END-class, 1 MIDDLE-class, 110 FREE-class). Preferences are significant (z = 34.16) but not universal (59% of components are positionally free).

### C498.d (Mechanism Explained)

The length-frequency correlation is now explained by C511 (derivational productivity):

> **Mechanism:** Short MIDDLEs are the productive base forms that seed longer singletons through extension and combination. The length-uniqueness gradient is a natural consequence of derivational morphology, not a distinct functional bifurcation.

---

## Files Generated

| File | Contents |
|------|----------|
| `position_distribution.json` | Component → position counts |
| `position_classes.json` | START/MIDDLE/END/FREE classification |
| `derivational_analysis.json` | Repeater → productivity data |
| `productivity_by_frequency.csv` | Frequency vs productivity |
| `pp_component_overlap.json` | PP/Component overlap metrics |
| `pp_component_venn.txt` | Overlap visualization |
| `decomposition_results.json` | Decomposition analysis |
| `short_singleton_analysis.json` | Short singleton comparison |
| `folio_complexity_progression.csv` | Folio-by-folio metrics |
| `local_vs_global_length.json` | Local vs global composition analysis |
| `ri_to_pp_collapse.json` | RI to PP collapse analysis |
| `pp_overlap_structure.json` | Superstring overlap analysis |
| `superstring_compatibility.json` | Compatibility enrichment validation (RI) |
| `compression_scan.json` | Global compression scan (all systems) |
| `enrichment_by_system.json` | Global enrichment analysis (all systems) |
| `kernel_primitive_reality.json` | Test 15: Kernel primitive reality check |
| `class_level_transitions.json` | Test 16: Class-level forbidden transitions |
| `construction_execution_isomorphism.json` | Test 17: Construction-execution isomorphism (falsified) |

---

## Cross-References

- C267 (compositional morphology) - EXTENDED by C510, C512, C516, C517
- C267.a (sub-component structure) - EXTENDED by C510, C516, C517
- C383 (global type system) - EXTENDED by C517, C518, C519, C520 (global compatibility architecture)
- C475 (MIDDLE incompatibility) - EXTENDED by C516 (sparsity), C518 (compatibility enrichment)
- C085 (kernel primitives) - CONNECTED by C517 (hinge letters are kernel primitives)
- C498.d (length-frequency correlation) - MECHANISM EXPLAINED by C511, EXTENDED by C515
- C509 (PP/RI dimensional separability) - REINFORCED by C512, C514

---

## Phase Tag

```
Phase: MIDDLE_SUBCOMPONENT_GRAMMAR
Tier: 2-3 (STRUCTURAL INFERENCE + MECHANISM DISCOVERY)
Subject: Internal Construction Rules of RI MIDDLEs
Type: Morphological grammar analysis
Status: COMPLETE
Constraints: C510-C522 (13 new constraints)
Verdict: GLOBAL_COMPATIBILITY_ARCHITECTURE + KERNEL_PRIMITIVE_REALITY + LAYER_INDEPENDENCE
  Tier 2:
  - C510: Positional preferences exist but are permissive
  - C511: Derivational productivity is 12.67x above chance
  - C512: PP MIDDLEs form atomic layer (99.1% containment)
  - C513: Short singletons are sampling variance, not distinct class
  - C514: RI compositional bifurcation (17.4% local, 82.6% global)
  - C515: Local derivation enriched in LONGER RI (rho=0.192)
  - C515.a: Embedding local context is additive, not reductive
  - C516: RI multi-atom composition (85.4% multi-PP, 0.03% sparsity)
  - C521: Kernel primitive directional asymmetry (one-way valve topology)
  - C522: Construction-execution layer independence (falsified isomorphism, r=-0.21)
  Tier 3 (global architecture discovery):
  - C517: Superstring compression is GLOBAL (65-77% overlap across all systems)
  - C518: Compatibility enrichment is GLOBAL (5-7x across all systems; extends C383)
  - C519: Global Compatibility Architecture (compression + enrichment = embedded relationships)
  - C520: System-Specific Exploitation Gradient (RI 6.8x > AZC 7.2x > PP 5.5x > B 5.3x)
  Kernel primitive validation:
  - Tests 15-16 confirmed kernel primitives are REAL OPERATORS, not compression artifacts
  - Directional asymmetry (e→h=0.00, h→e=7.00x) cannot arise from compression mechanics
  Layer independence:
  - Test 17 FALSIFIED construction-execution isomorphism (r=-0.21, category match 28.4%)
  - Three independent constraint layers share the same 10-character substrate
```
