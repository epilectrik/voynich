# Research Phase: MIDDLE_SUBCOMPONENT_GRAMMAR

## Summary

Investigate the internal construction rules of RI MIDDLEs by analyzing sub-component positional grammar, derivational relationships, and the role of PP MIDDLEs as atomic primitives.

**Background:** C267.a established that 218 sub-components reconstruct 97.8% of MIDDLEs. C498.d established that length predicts uniqueness (rho=-0.367). This phase investigates the *mechanism* behind these patterns.

---

## Research Questions

1. Do sub-components have positional constraints (start-class, middle-class, end-class)?
2. Are longer MIDDLEs derived from shorter base forms?
3. Are PP MIDDLEs the atomic layer of the component vocabulary?
4. What explains the 168 "short singletons" that violate the length-frequency pattern?

---

## Test Suite

### PRIMARY TESTS (Must Run)

#### Test 1: Sub-Component Positional Grammar
**Hypothesis:** Sub-components have positional constraints forming a grammar.

**Method:**
1. For each of the 218 sub-components, compute positional distribution (start/middle/end of MIDDLE)
2. Calculate position exclusivity score: max(start%, middle%, end%)
3. Classify components into position classes (threshold: 70%)
4. **Baseline:** Permutation test - shuffle components across MIDDLEs 1000x to establish null distribution

**Pass criteria:** >70% of components show strong position preference (exclusivity > 0.7)

**Output:**
- `position_distribution.json` - component → {start: N, middle: N, end: N}
- `position_classes.json` - {start_class: [...], middle_class: [...], end_class: [...]}

**Potential constraint:** C510 (Sub-components have positional constraints)

---

#### Test 2: Derivational Hierarchy
**Hypothesis:** High-frequency MIDDLEs "seed" longer singletons productively.

**Method:**
1. For each repeater MIDDLE (freq > 1), count how many singletons contain it as:
   - Prefix (singleton starts with repeater)
   - Suffix (singleton ends with repeater)
   - Infix (singleton contains repeater internally)
2. Compute "productivity ratio" = actual derivations / expected derivations
3. **Baseline (CRITICAL):** Expected derivations based on character frequency (longer strings appear as substrings more often by chance)

**Pass criteria:** Productivity ratio significantly > 1.0 for high-frequency MIDDLEs

**Output:**
- `derivational_analysis.json` - repeater → {prefix_seeds: N, suffix_seeds: N, infix_seeds: N, productivity_ratio: X}
- `productivity_by_frequency.csv` - frequency vs productivity correlation

**Potential constraint:** C511 (High-frequency MIDDLEs seed longer singletons productively)

---

#### Test 3: PP as Atomic Layer
**Hypothesis:** PP MIDDLEs (shared with B) are the primitives of the component vocabulary.

**Method:** Compute three metrics:
1. **PP→Component:** % of PP MIDDLEs that ARE sub-components
2. **Component→PP:** % of sub-components that ARE PP MIDDLEs
3. **RI contains PP:** % of RI MIDDLEs containing PP MIDDLE as substring

**Pass criteria:** High overlap (>50%) in at least two metrics

**Output:**
- `pp_component_overlap.json` - {pp_are_components: X%, components_are_pp: X%, ri_contains_pp: X%}
- `pp_component_venn.txt` - visualization of overlap

**Potential constraint:** C512 (PP MIDDLEs form atomic morphological layer)

---

### SECONDARY TESTS

#### Test 4: Compositional Decomposition
**Hypothesis:** Longer MIDDLEs can be split into two valid shorter MIDDLEs.

**Method:**
1. For each 4+ char MIDDLE, test all split points
2. Check if both halves are valid MIDDLEs under THREE definitions:
   - **Option A:** Any MIDDLE in corpus
   - **Option B:** Any MIDDLE with frequency > 1
   - **Option C:** Any PP MIDDLE only

**Output:**
- `decomposition_results.json` - {option_a: X%, option_b: X%, option_c: X%}
- Examples of successful decompositions

---

#### Test 5: Short Singleton Exception Analysis
**Hypothesis:** The 168 short singletons (≤3 chars) have structural or contextual differences from short repeaters.

**Method:**
1. Compare component inventories used by short singletons vs short repeaters
2. Compare positional distributions (line-initial rate, folio context)
3. **Baseline:** Bootstrap 1000x to establish confidence intervals (168 samples marginal)

**Output:**
- `short_singleton_analysis.json` - component differences, positional differences
- Statistical significance with bootstrap CIs

---

### OPTIONAL TEST

#### Test 6: Folio Complexity Progression
**Hypothesis:** MIDDLE complexity changes across Currier A folios.

**Method:** Plot mean MIDDLE length and segment count by folio order.

**Caveat:** Confounded by binding history (C156, C367). Results should be interpreted cautiously.

**Output:**
- `folio_complexity_progression.csv`

---

## Stratification

**ALL tests must be stratified by section (H/P/T)** to catch section-specific patterns.

Compute each metric for:
- All sections combined
- Herbal (H) only
- Pharmaceutical (P) only
- Text (T) only

---

## Directory Structure

```
phases/MIDDLE_SUBCOMPONENT_GRAMMAR/
├── DESIGN.md
├── scripts/
│   ├── test1_positional_grammar.py
│   ├── test2_derivational_hierarchy.py
│   ├── test3_pp_atomic_layer.py
│   ├── test4_compositional_decomposition.py
│   ├── test5_short_singleton_analysis.py
│   └── test6_folio_progression.py (optional)
└── results/
    ├── FINDINGS.md
    ├── position_distribution.json
    ├── position_classes.json
    ├── derivational_analysis.json
    ├── pp_component_overlap.json
    ├── decomposition_results.json
    └── short_singleton_analysis.json
```

---

## Expected Constraints

| Constraint | Test | Tier | Statement |
|------------|------|------|-----------|
| C510 | Test 1 | 2 | Sub-components have positional constraints |
| C511 | Test 2 | 2 | High-frequency MIDDLEs seed longer singletons productively |
| C512 | Test 3 | 2 | PP MIDDLEs form atomic morphological layer |

**Extensions to existing:**
- C267.a (positional rules added)
- C498.d (mechanism explained)

---

## Risk Assessment

Guard against these invalidation scenarios:

1. **Sub-component inventory instability** - Verify the 218 components are reproducible before running tests
2. **Substring coincidence** - Frequency baselines for Tests 2 and 4 are CRITICAL
3. **PREFIX/SUFFIX contamination** - Exclude known PREFIX/SUFFIX strings from sub-component analysis
4. **Random combinatorics masquerading as grammar** - Test 1's positional analysis is the key discriminator

---

## Verification Plan

After running all tests:

1. **Reproducibility check:** Re-run with different random seeds for permutation/bootstrap tests
2. **Cross-check against C267.a:** Ensure 218 components and 97.8% coverage are reproduced
3. **Constraint consistency:** New constraints must not conflict with C267, C498.d, C509
