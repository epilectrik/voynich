# LABEL_BRUNSCHWIG_ALIGNMENT Phase

**Date:** 2026-02-05
**Status:** COMPLETE
**Verdict:** WEAK (1/5 tests significant)
**Tier:** 3 (Semantic Interpretation)
**Prerequisite Phases:** LABEL_INVESTIGATION, REVERSE_BRUNSCHWIG_TEST, MATERIAL_MAPPING_V2

---

## Objective

Test whether label vocabulary correlates with Brunschwig material categories, connecting the LABEL_INVESTIGATION findings (labels → B pipeline) with the Brunschwig domain correspondence.

**Core question:** If labels identify materials, and Voynich corresponds to Brunschwig distillation, does label vocabulary cluster by Brunschwig-relevant dimensions?

---

## Background

### From LABEL_INVESTIGATION
- 97.9% of labels connect to B via PP bases
- Jar labels: 2.1x AX_FINAL enrichment (material specification positions)
- Content labels (root/leaf): moderate AX enrichment
- Labels use common B vocabulary, not specialized terms

### From Brunschwig Phases
- REGIME 1-4 ↔ Fire degree 1-4 (F-BRU-001)
- Handling types: 66% CAREFUL, 11% STANDARD, 6% PRECISION (C883)
- Preparation MIDDLEs: te=GATHER, pch=CHOP, lch=STRIP, tch=POUND (X.31)
- Animal materials → PRECISION handling, REGIME_4 (C884)

### Gap
No previous work has connected LABEL vocabulary to Brunschwig material categories.

---

## Critical Constraint: C384

**NO DIRECT RECIPE→ENTRY MAPPING**

We CANNOT claim "this jar label = this Brunschwig recipe." We CAN test:
- Statistical clustering by product type
- Handling signature correlation
- Folio-level material category enrichment

---

## Test Design

### Test 1: Jar MIDDLE → Brunschwig Product Type

**Question:** Do jar label MIDDLEs cluster by Brunschwig product type (WATER_GENTLE, WATER_STANDARD, OIL_RESIN, PRECISION)?

**Method:**
1. Extract jar MIDDLEs from PHARMA_LABEL_DECODING
2. For each MIDDLE, find its B folio distribution
3. Map B folios to REGIME (from existing profiles)
4. REGIME → Fire degree → Product type (from BRSC)
5. Test if jar MIDDLEs cluster by inferred product type

**Expected if Brunschwig-aligned:**
- Jar MIDDLEs should NOT distribute uniformly across product types
- Jars should cluster with their expected processing type

**Null hypothesis:** Jar MIDDLEs distribute uniformly across product types.

---

### Test 2: Content Label Material Category

**Question:** Do content labels (root vs leaf) correlate with Brunschwig material categories?

**Method:**
1. Separate root labels vs leaf labels from PHARMA_LABEL_DECODING
2. Extract MIDDLEs for each category
3. Compute handling signature for each (PREFIX profile → handling type)
4. Test if root vs leaf show different handling signatures

**Expected if Brunschwig-aligned:**
- Roots may show different processing (more POUND/CHOP) than leaves
- Leaves may show more GENTLE handling (delicate materials)

**Null hypothesis:** Root and leaf MIDDLEs have identical handling signatures.

---

### Test 3: Label-Rich Folios and Recipe Clusters

**Question:** Do A folios with high label density connect to B folios with specific Brunschwig recipe affinity?

**Method:**
1. Identify A folios with high label count (from PHARMA_LABEL_DECODING)
2. Trace label PP bases to B folio appearances
3. Compute Brunschwig recipe affinity for those B folios (from REVERSE_ACTIVATION)
4. Test if label-rich A folios → specific recipe cluster B folios

**Expected if Brunschwig-aligned:**
- Label-rich A folios should show concentrated B folio connections
- Those B folios should share recipe cluster affinity

**Null hypothesis:** Label-rich A folios connect uniformly to all B folios.

---

### Test 4: Section-Level Label Differentiation

**Question:** Do PHARMA labels differ from HERBAL labels in Brunschwig-relevant dimensions?

**Method:**
1. Compare label profiles across sections (if HERBAL labels exist)
2. Compute handling signature, REGIME affinity, preparation MIDDLE usage
3. Test for section-specific label vocabulary

**Expected if Brunschwig-aligned:**
- PHARMA labels → more processed/prepared materials
- HERBAL labels (if present) → more raw/simple materials

**Null hypothesis:** Label profiles identical across sections.

---

### Test 5: Preparation Operation Co-occurrence

**Question:** Do label MIDDLEs preferentially co-occur with specific preparation operations?

**Method:**
1. For each label MIDDLE, find B lines where it appears
2. Check if those lines contain preparation MIDDLEs (te, pch, lch, tch, ksh)
3. Compute which preparation operations each label MIDDLE associates with
4. Test for non-uniform distribution

**Expected if Brunschwig-aligned:**
- Root labels → CHOP (pch), POUND (tch)
- Leaf labels → STRIP (lch), GATHER (te)

**Null hypothesis:** Label MIDDLEs distribute uniformly across preparation operations.

---

## Data Sources

| File | Purpose |
|------|---------|
| phases/PHARMA_LABEL_DECODING/*.json | Label data (jar, root, leaf) |
| phases/LABEL_INVESTIGATION/results/label_b_pipeline.json | Label → PP base → B connections |
| data/brunschwig_curated_v3.json | 197 Brunschwig recipes |
| context/STRUCTURAL_CONTRACTS/brunschwig.brsc.yaml | Fire degree → REGIME mapping |
| phases/REVERSE_BRUNSCHWIG_TEST/results/*.json | Recipe-folio affinities |

---

## Scripts

| Script | Test | Output |
|--------|------|--------|
| 01_jar_product_type.py | Test 1 | jar_product_type.json |
| 02_content_material_category.py | Test 2 | content_material_category.json |
| 03_label_folio_recipe_cluster.py | Test 3 | label_folio_recipe_cluster.json |
| 04_section_label_differentiation.py | Test 4 | section_label_differentiation.json |
| 05_prep_operation_cooccurrence.py | Test 5 | prep_operation_cooccurrence.json |
| 06_integrated_verdict.py | Synthesis | integrated_verdict.json |

---

## Success Criteria

| Level | Criteria |
|-------|----------|
| STRONG | 4-5 tests show significant non-uniform distribution |
| MODERATE | 2-3 tests show significant effects |
| WEAK | 1 test shows significant effect |
| NULL | No tests show significant effects |

**Statistical thresholds:**
- Chi-square: p < 0.05
- Correlation: |r| >= 0.3, p < 0.05
- Effect size: Cramer's V >= 0.1 or Cohen's d >= 0.5

---

## Relationship to Prior Work

| Prior Finding | This Phase Tests |
|---------------|------------------|
| C928 (jar AX_FINAL) | Do those AX_FINAL positions encode Brunschwig-relevant material identity? |
| C883 (handling distribution) | Do label MIDDLEs match handling distribution? |
| X.31 (prep MIDDLEs) | Do labels co-occur with expected prep operations? |
| F-BRU-001 (product type) | Do jar labels cluster by product type? |

---

## Risk: Vocabulary Ubiquity

From LABEL_INVESTIGATION, label PP bases are common vocabulary appearing everywhere in B. This may dilute any signal. Mitigations:
- Focus on jar-specific MIDDLEs (more distinctive)
- Use folio-level aggregation (not token-level)
- Compare to null model (permutation tests)

---

## Results

### Test 1: Jar Product Type Clustering - **SIGNIFICANT**
- **Chi2 = 27.50, p < 0.0001**
- 81.2% of jar labels cluster with PRECISION product type
- Reinforces C928 (jar AX_FINAL concentration)

### Test 2: Root vs Leaf Handling Profiles - NOT SIGNIFICANT
- Chi2 = 1.17, p = 0.88, Cramer's V = 0.109
- Root and leaf labels show similar handling profiles
- MIDDLE overlap is low (Jaccard = 0.087) - distinct vocabulary, same handling

### Test 3: Label-Rich Folio B Concentration - NOT SIGNIFICANT
- T-test p = 0.60 (Gini concentration)
- Label-rich folios do NOT show more concentrated B connections
- B folio reach: high-label = 82, low-label = 27 (p = 0.053, marginal)

### Test 4: Section-Level Label Differentiation - NOT SIGNIFICANT
- Chi2 = 3.21, p = 0.52, Cramer's V = 0.168
- Labels do not differ by section in handling profile
- Limited power: 100 PHARMA labels vs 14 OTHER

### Test 5: Prep Operation Co-occurrence - NOT SIGNIFICANT
- Chi2 = 0.13, p = 1.00, Cramer's V = 0.005
- Label MIDDLEs are ubiquitous (96-100% of B lines)
- Brunschwig prediction (root=intensive, leaf=gentle): NOT SUPPORTED

---

## Verdict: WEAK

**Significant tests: 1/5**

| Test | Result | p-value |
|------|--------|---------|
| Test 1: Jar Product Type | PASS | < 0.0001 |
| Test 2: Root vs Leaf | FAIL | 0.88 |
| Test 3: B Folio Concentration | FAIL | 0.60 |
| Test 4: Section Differentiation | FAIL | 0.52 |
| Test 5: Prep Co-occurrence | FAIL | 1.00 |

---

## Key Insights

1. **Jar label clustering is real** - 81% map to PRECISION product type, confirming C928 interpretation that jars identify specific output products.

2. **Vocabulary ubiquity problem** - Label PP bases appear in nearly ALL B lines (96-100%), diluting any semantic signal from prep operation co-occurrence.

3. **Root/leaf distinction is visual, not procedural** - Despite distinct vocabulary (Jaccard = 0.087), root and leaf labels show identical handling profiles. The distinction may be visual (what the illustration shows) not procedural (how it's processed).

4. **Labels identify WHAT, not HOW** - The label->B pipeline exists at vocabulary level but does not encode Brunschwig processing categories. Labels name materials; procedures are encoded elsewhere.

---

## Constraint Implications

- **No new constraints** - Test 1 reinforces existing C928, other tests are null
- **C928 interpretation confirmed** - Jar labels identify output products
- **Brunschwig material categories** - Do not map directly to label types

---

*Phase completed: 2026-02-05*
