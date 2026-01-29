# REVERSE_BRUNSCHWIG_TEST Phase

**Date:** 2026-01-29
**Status:** PLANNED
**Tier:** 3 (Semantic Interpretation)

---

## Objective

Test whether Voynich structural patterns ACTUALLY correspond to Brunschwig distillation procedures, not just whether they COULD theoretically encode them.

**Previous work (forward tests):**
- C493: Brunschwig balneum marie CAN embed in Voynich grammar (0 violations)
- F-BRU-001: Fire degree predicts PREFIX profile (86.8% compliance)
- ANIMAL_RECIPE_TRACE: Animal materials → REGIME_4 at 2.14x

**This phase (reverse tests):**
- Do actual B lines contain Brunschwig-like procedure sequences?
- Do section profiles match Brunschwig material categories?
- Does LINK density correlate with fire degree (more monitoring = lower fire)?

---

## Key Insight

From BRSC and C873:

| Brunschwig | Voynich | Evidence |
|------------|---------|----------|
| Fire degree 1-4 | REGIME 1-4 | F-BRU-002 |
| e→h→k = verify→align→heat | Kernel ordering (C873) | B_CONTROL_FLOW_SEMANTICS |
| Sensory monitoring protocol | LINK phase | C876 |
| 2 retry limit | FQ escape handler | C875 |
| 5 quality rejection tests | 5 hazard classes | C109 |
| Parametric recipes | Parametric entries | BRSC |

---

## Test Design

### Test 1: Kernel Sequence Inventory

**Question:** Do actual B lines contain e→h→k sequences matching Brunschwig's procedure order?

**Method:**
1. Extract all kernel-containing lines from B
2. Compute kernel ordering for each line (which comes first: e, h, or k?)
3. Compare to C873 prediction (e < h < k positionally)
4. Check if ordering varies by section (HERBAL_B vs BIO vs PHARMA)

**Expected if Brunschwig-compatible:**
- e→h→k ordering dominant (verify before heating)
- BIO may show different pattern (different procedure type)

---

### Test 2: Fire Degree → LINK Density

**Question:** Do Brunschwig fire degrees predict Voynich monitoring intensity?

**Method:**
1. Map Brunschwig recipes to fire degrees (from curated_v3.json)
2. Trace compatible MIDDLEs to B folios (via PP vocabulary)
3. Compute LINK density per folio
4. Test correlation: fire_degree vs LINK_density

**Expected if Brunschwig-compatible:**
- Fire degree 1 (gentle) → high LINK density
- Fire degree 3 (intense) → low LINK density
- Inverse correlation (r < -0.3)

---

### Test 3: Section → Material Category

**Question:** Do Voynich sections specialize by Brunschwig material category?

**Method:**
1. Classify Brunschwig recipes by material (herb, flower, root, animal)
2. Trace each category to compatible B folios
3. Compute section distribution for each material category
4. Test if distributions differ significantly (chi-square)

**Expected if Brunschwig-compatible:**
- HERBAL_B enriched for herb/flower materials
- BIO enriched for animal materials
- PHARMA enriched for root materials (if present)

---

### Test 4: Recovery Architecture Match

**Question:** Does Voynich FQ escape behavior match Brunschwig's 2-retry recovery?

**Method:**
1. Identify FQ chains in B lines (escape sequences)
2. Measure chain length distribution
3. Check if chains rarely exceed 2 tokens (matching 2-retry limit)
4. Test if FQ→EN recovery rate matches "cooling to processing" pattern

**Expected if Brunschwig-compatible:**
- FQ chains mostly 1-2 tokens
- FQ→EN transition rate high (recovery to processing)
- Rare 3+ token chains (beyond retry limit = failure)

---

### Test 5: Quality Rejection → Hazard Class

**Question:** Do Brunschwig's 5 quality tests map to Voynich's 5 hazard classes?

**Method:**
1. Extract hazard class distribution from B (C109)
2. Map Brunschwig quality tests to hazard semantics:
   - No taste → COMPOSITION_JUMP?
   - Wrong viscosity → RATE_MISMATCH?
   - Cloudiness → CONTAINMENT_TIMING?
   - Color/smell → PHASE_ORDERING?
   - Degradation → ENERGY_OVERSHOOT?
3. Test if hazard class frequencies match quality test importance

**Expected if Brunschwig-compatible:**
- PHASE_ORDERING most common (41% in Voynich, temperature most common warning in Brunschwig)
- ENERGY_OVERSHOOT least common (categorical prohibition = rare violation)

---

### Test 6: Parametric Correspondence

**Question:** Does Brunschwig's parameter→behavior structure match Voynich's?

**Method:**
1. For each Brunschwig recipe, extract: fire_degree, material_type, method
2. Map to Voynich: REGIME, PREFIX class, kernel pattern
3. Compute contingency tables
4. Test if mappings are consistent (chi-square, mutual information)

**Expected if Brunschwig-compatible:**
- Fire degree predicts REGIME (already shown in F-BRU-001)
- Material type predicts PREFIX class
- Method predicts kernel pattern (balneum marie → more e, less k)

---

## Scripts

| Script | Test | Output |
|--------|------|--------|
| 00_kernel_sequence_inventory.py | Test 1 | kernel_sequences.json |
| 01_fire_degree_link_density.py | Test 2 | fire_link_correlation.json |
| 02_section_material_category.py | Test 3 | section_material_mapping.json |
| 03_recovery_architecture.py | Test 4 | recovery_analysis.json |
| 04_hazard_quality_mapping.py | Test 5 | hazard_quality_mapping.json |
| 05_parametric_correspondence.py | Test 6 | parametric_analysis.json |
| 06_integrated_verdict.py | Synthesis | reverse_brunschwig_verdict.json |

---

## Expected Constraints

| # | Name | Hypothesis |
|---|------|------------|
| C881 | Kernel Sequence Distribution | e→h→k ordering prevalence in actual B lines |
| C882 | Fire-LINK Inverse Correlation | Lower fire degree = higher LINK density |
| C883 | Section-Material Specialization | Sections specialize by Brunschwig material category |
| C884 | Recovery Chain Length | FQ chains match 2-retry limit |
| C885 | Hazard-Quality Correspondence | 5 hazard classes map to 5 quality tests |
| C886 | Parametric Structure Verdict | Overall Brunschwig-Voynich correspondence level |

---

## Data Dependencies

| Source | Use |
|--------|-----|
| data/brunschwig_curated_v3.json | Fire degree, material type, procedures |
| context/STRUCTURAL_CONTRACTS/brunschwig.brsc.yaml | Protocol mappings |
| phases/B_CONTROL_FLOW_SEMANTICS/results/*.json | Kernel semantics, role profiles |
| data/voynich_transcript.csv | B tokens |
| phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json | LINK identification |

---

## Success Criteria

| Level | Criteria |
|-------|----------|
| STRONG | 5-6 tests show significant correspondence |
| MODERATE | 3-4 tests show significant correspondence |
| WEAK | 1-2 tests show significant correspondence |
| FAILURE | 0 tests show correspondence |

**Statistical thresholds:**
- Correlation: |r| >= 0.3, p < 0.05
- Chi-square: p < 0.05
- Effect size: Cohen's d >= 0.5

---

## Relationship to Forward Tests

| Forward Test | This Phase Validates |
|--------------|---------------------|
| C493 (grammar embedding) | Actual sequences match predicted |
| F-BRU-001 (fire→REGIME) | Correlation holds in reverse direction |
| ANIMAL_RECIPE_TRACE | Material routing generalizes to other categories |
| BRSC protocols | Protocols have structural reflexes in B |

---

## Verdict Interpretation

**If STRONG:**
> The Voynich Manuscript not only COULD encode Brunschwig-style procedures,
> it ACTUALLY contains structural patterns consistent with distillation
> protocols. The parametric correspondence suggests shared operational logic.

**If WEAK/FAILURE:**
> The Voynich grammar is compatible with distillation but does not show
> specific Brunschwig correspondence. The manuscript may encode a different
> domain or a more abstract control system.

---

## Files

```
phases/REVERSE_BRUNSCHWIG_TEST/
├── README.md (this file)
├── FINDINGS.md (to be generated)
├── scripts/
│   ├── 00_kernel_sequence_inventory.py
│   ├── 01_fire_degree_link_density.py
│   ├── 02_section_material_category.py
│   ├── 03_recovery_architecture.py
│   ├── 04_hazard_quality_mapping.py
│   ├── 05_parametric_correspondence.py
│   └── 06_integrated_verdict.py
└── results/
    ├── kernel_sequences.json
    ├── fire_link_correlation.json
    ├── section_material_mapping.json
    ├── recovery_analysis.json
    ├── hazard_quality_mapping.json
    ├── parametric_analysis.json
    └── reverse_brunschwig_verdict.json
```
