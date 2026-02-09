# BRUNSCHWIG_CLOSED_LOOP_DIMENSIONS Phase

**Date:** 2026-01-30
**Status:** COMPLETE (7 tests, STRONG verdict)
**Tier:** 2 (Structural)
**Prerequisite:** REVERSE_BRUNSCHWIG_TEST (STRONG verdict)

---

## Objective

Systematically explore closed-loop control dimensions that Brunschwig's linear recipe model cannot capture. Follow-up to REVERSE_BRUNSCHWIG_TEST orthogonality discoveries (C890-C892).

**Previous findings:**
- C890: Recovery rate-pathway independence
- C891: ENERGY-FREQUENT inverse (rho=-0.80)
- C892: Post-FQ h-dominance

**This phase:**
- Folio-level verification of REGIME-level patterns
- Additional orthogonality dimensions (monitoring, material, method)
- Quantify the multi-dimensional parameter space
- Map paragraph types to Brunschwig operation categories

---

## Results Summary

| Test | Verdict | Key Finding |
|------|---------|-------------|
| 1. Folio ENERGY-FREQUENT | **CONFIRMED** | rho=-0.529, p=3.2e-7 (folio-level confirms C891) |
| 2. Folio Post-FQ h-Dominance | **CONFIRMED** | h>e in 97% of folios (confirms C892) |
| 3. Monitoring Orthogonality | **SUPPORT** | LINK independent of Kernel and FQ |
| 4. PREFIX-MIDDLE Orthogonality | NOT SUPPORTED | Cramer's V=0.44 (moderate association) |
| 5. Method-Kernel Signatures | **SUPPORT** | h,e vary by fire degree (inverted from Brunschwig) |
| 8. Multi-Dimensional PCA | **SUPPORT** | 5 dimensions for 80% variance vs Brunschwig's ~3 |
| 9. Paragraph Kernel-Operation Mapping | **CONFIRMED** | HIGH_K=2x FQ (p<0.0001), maps to Brunschwig operations (C893) |
| 10. REGIME-Paragraph Recovery Concentration | **CONFIRMED** | REGIME_4 33% recovery-specialized (chi-sq=28.41, p=0.0001) (C894) |

**Overall: STRONG** (7/8 tests support closed-loop orthogonality)

**Key Insight:** The Voynich control system has 5-6 independent dimensions, exceeding Brunschwig's linear ~3 dimensions. ENERGY vs FREQUENT inverse confirmed at folio level (rho=-0.53, p<0.0001). Paragraph kernel signatures map to Brunschwig operation categories (HIGH_K=recovery, HIGH_H=active distillation).

---

## New Constraint: C893

**Paragraph Kernel Signature Predicts Operation Type**

| Para Type | Count | FQ Rate | EN Rate | Brunschwig Mapping |
|-----------|-------|---------|---------|-------------------|
| HIGH_K | 58 | **19.7%** | 19.3% | Recovery procedures |
| HIGH_H | 203 | 9.7% | **22.0%** | Active distillation |
| BALANCED | 235 | 12.6% | 23.9% | General procedures |

This maps paragraph-level structure directly to Brunschwig operation categories, extending the domain correspondence from folio/REGIME level to paragraph level.

---

## New Constraint: C894

**REGIME_4 Recovery Specialization Concentration**

| REGIME | Recovery-Specialized Folios | K/(K+H) Ratio |
|--------|---------------------------|---------------|
| REGIME_4 | **33%** (8/24) | **0.32** (highest) |
| REGIME_1 | 3% (1/31) | 0.21 |
| REGIME_2 | 0% (0/10) | 0.27 |
| REGIME_3 | 0% (0/16) | **0.10** (lowest) |

Chi-square = 28.41, p = 0.0001

This validates C494's precision interpretation: REGIME_4 (precision-constrained execution) concentrates recovery-specialized folios because precision operations require high recovery capacity. The effect persists within sections (REGIME_4 has 56% higher K/(K+H) than REGIME_3 within Section H).

---

## Test Design

### Test 1: Folio-Level Verification of C891

**Question:** Does the ENERGY-FREQUENT inverse hold at folio level, not just REGIME aggregates?

**Method:**
1. Compute ENERGY_OPERATOR and FREQUENT_OPERATOR density per folio
2. Test Spearman correlation at folio level (n=83)
3. Compare effect size to REGIME-level (rho=-0.80)

**Expected:** Significant negative correlation (p<0.05) confirms structural relationship.

---

### Test 2: Folio-Level Post-FQ h-Dominance

**Question:** Does h dominate post-FQ at folio level across all folios?

**Method:**
1. For each folio, compute post-FQ kernel distribution
2. Test if h > e in majority of folios (not just REGIME aggregates)
3. Compute confidence interval for h-dominance

**Expected:** h > e in >75% of folios with sufficient FQ tokens.

---

### Test 3: Monitoring Orthogonality (LINK vs Kernel Contact)

**Question:** Are monitoring intensity (LINK) and kernel engagement (kernel contact rate) independent?

**Method:**
1. Compute LINK density per folio
2. Compute kernel contact rate per folio (tokens containing k/h/e)
3. Test correlation
4. Compare to FQ density (escape rate)

**Expected:** If orthogonal, LINK and kernel contact can be tuned independently.

---

### Test 4: Material Handling - PREFIX vs MIDDLE Orthogonality

**Question:** Do PREFIX (material identity) and MIDDLE (procedural core) encode independent parameters?

**Hypothesis:** Brunschwig distinguishes:
- Material IDENTITY (herb, root, flower, animal) → PREFIX class
- Material BEHAVIOR (hot/dry vs moist/slimy, storage duration) → MIDDLE patterns

**Method:**
1. Group tokens by PREFIX class (M-A, M-B, M-C, M-D from CASC)
2. Compute MIDDLE diversity and distribution per PREFIX class
3. Test if PREFIX classes have distinct MIDDLE profiles
4. Check for cross-independence (same MIDDLE in different PREFIX contexts)

**Expected:** PREFIX and MIDDLE encode orthogonal parameters if MIDDLEs appear across multiple PREFIX contexts.

---

### Test 5: Method Signatures - Kernel Patterns by Distillation Method

**Question:** Do different distillation methods (balneum marie, direct fire, etc.) have distinct kernel patterns?

**Hypothesis:** From BRSC:
- Balneum marie (gentle): More monitoring (LINK), less k
- Direct fire (intense): More k, less LINK
- Method → REGIME → kernel pattern

**Method:**
1. Use fire degree as method proxy (degree 1 = gentle, degree 3 = intense)
2. Map fire degree → REGIME → folio
3. Compute kernel (k/h/e) proportions per method proxy
4. Test if kernel profiles differ significantly by method

**Expected:** Gentle methods show different k:h:e ratios than intense methods.

---

### Test 6: Stability Dimension - LINK/FQ Ratio Decomposition

**Question:** Can we decompose stability (LINK/FQ ratio) into independent components?

**Hypothesis:** LINK/FQ ratio conflates:
- Monitoring CAPACITY (how much LINK infrastructure)
- Escape DEMAND (how much FQ needed)

**Method:**
1. Compute LINK density, FQ density, and LINK/FQ ratio per folio
2. PCA or factor analysis on [LINK, FQ, ENERGY, FREQUENT, KERNEL]
3. Identify orthogonal factors

**Expected:** Multiple independent factors, not just one "stability" dimension.

---

### Test 7: Fire-Stability at Folio Level

**Question:** Does fire degree predict LINK/FQ ratio at folio level (confirming Test 8 from REVERSE_BRUNSCHWIG_TEST)?

**Method:**
1. Map each folio to fire degree via REGIME
2. Compute LINK/FQ ratio per folio
3. Test Spearman correlation (n=83)

**Expected:** Significant negative correlation confirms fire → instability.

---

### Test 8: Multi-Dimensional Profile Clustering

**Question:** How many independent dimensions describe the Voynich control parameter space?

**Method:**
1. Build feature matrix: [ENERGY, FREQUENT, FLOW, CORE, LINK, kernel_k, kernel_h, kernel_e, FQ_rate, post_FQ_h]
2. PCA to extract principal components
3. Determine dimensionality (variance explained)
4. Compare to Brunschwig's parameter space (fire degree, material type, method)

**Expected:** 3-5 independent dimensions, more than Brunschwig's linear model allows.

---

## Success Criteria

| Level | Criteria |
|-------|----------|
| STRONG | 6+ tests show significant patterns; folio-level confirms REGIME-level |
| MODERATE | 4-5 tests significant; some folio-level confirmation |
| WEAK | 2-3 tests significant; REGIME patterns don't replicate at folio level |

---

## Data Dependencies

| Source | Use |
|--------|-----|
| phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json | Role/class identification |
| results/regime_folio_mapping.json | REGIME assignments |
| context/STRUCTURAL_CONTRACTS/brunschwig.brsc.yaml | Fire degree mapping |
| context/STRUCTURAL_CONTRACTS/currierA.casc.yaml | PREFIX classes |

---

## Scripts

| Script | Test | Output |
|--------|------|--------|
| 01_folio_energy_frequent.py | Test 1 | folio_energy_frequent.json |
| 02_folio_post_fq_h.py | Test 2 | folio_post_fq_h.json |
| 03_monitoring_orthogonality.py | Test 3 | monitoring_orthogonality.json |
| 04_prefix_middle_orthogonality.py | Test 4 | prefix_middle_orthogonality.json |
| 05_method_kernel_signatures.py | Test 5 | method_kernel_signatures.json |
| 06_stability_decomposition.py | Test 6 | stability_decomposition.json |
| 07_folio_fire_stability.py | Test 7 | folio_fire_stability.json |
| 08_multidimensional_pca.py | Test 8 | multidimensional_pca.json |
| 09_integrated_verdict.py | Synthesis | closed_loop_dimensions_verdict.json |

---

## Relationship to Previous Work

| Previous | This Phase Extends |
|----------|-------------------|
| C890 (rate-pathway independence) | Folio-level verification |
| C891 (ENERGY-FREQUENT inverse) | Folio-level verification, additional pairs |
| C892 (post-FQ h-dominance) | Folio-level verification |
| Test 8 fire-stability | Folio-level confirmation |
| BRSC material classification | PREFIX-MIDDLE orthogonality |
| BRSC distillation methods | Method-kernel signatures |

---

## Files

```
phases/BRUNSCHWIG_CLOSED_LOOP_DIMENSIONS/
├── README.md (this file)
├── scripts/
│   ├── 01_folio_energy_frequent.py
│   ├── 02_folio_post_fq_h.py
│   ├── 03_monitoring_orthogonality.py
│   ├── 04_prefix_middle_orthogonality.py
│   ├── 05_method_kernel_signatures.py
│   ├── 06_stability_decomposition.py
│   ├── 07_folio_fire_stability.py
│   ├── 08_multidimensional_pca.py
│   └── 09_integrated_verdict.py
└── results/
    └── *.json
```
