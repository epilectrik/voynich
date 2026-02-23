# C1222: Modern Distillation Dimensionality Closer to Voynich

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** MODERN_DISTILLATION_DIMENSIONAL_COMPARISON (Phase 435)
**Extends:** C1056 (MIDPROCESS structural absence in Brunschwig)
**Relates to:** F-BRU-030 (MIDPROCESS absence characterization), F-BRU-031 (modern dimensional comparison)

---

## Statement

Modern distillation procedures, formalized into the same 7-phase taxonomy as Brunschwig (COLLECTION, PREPARATION, PRETREATMENT, DISTILLATION, MIDPROCESS, POSTPROCESS, STORAGE), have PCA dimensionality 2.3× closer to Voynich than Brunschwig. Modern distillation requires 4 PCs for 80% variance (vs Brunschwig 3, Voynich 5), has 7 active dimensions (vs Brunschwig 5, Voynich 10), and entropy 2.334 bits (vs Brunschwig 1.908, Voynich 2.660). The critical differentiator is MIDPROCESS: 34.5% of modern actions are process control steps (temperature monitoring, channeling detection, endpoint detection, cooling adjustment), forming a dedicated monitoring PC (PC2, 20.2% variance) — entirely absent from Brunschwig (0/228 recipes, 0.000 loading on all PCs).

### Dimensional Comparison

| Metric | Brunschwig | Modern | Voynich |
|--------|-----------|--------|---------|
| Active dimensions | 5 | 7 | 10 |
| n_for_80% | 3 | 4 | 5 |
| n_for_90% | 4 | 5 | 6 |
| Entropy (bits) | 1.908 | 2.334 | 2.660 |
| MIDPROCESS mean | 0.0% | 34.5% | present |
| MIDPROCESS max loading | 0.000 | 0.653 | present |

### Entropy Distance from Voynich

- Brunschwig: |1.908 - 2.660| = 0.752
- Modern: |2.334 - 2.660| = 0.326
- Modern is **2.3× closer** to Voynich

### PC-Count Distance from Voynich

- Brunschwig: |3 - 5| = 2
- Modern: |4 - 5| = 1
- Modern **halves** the dimensional gap

---

## Interpretation

The Voynich system's higher dimensionality vs Brunschwig is not anomalous — it reflects the difference between recipe-level specification (gather materials, process, distill) and process control specification (monitor, adjust, detect, intervene). Brunschwig tells you WHAT to do; the Voynich and modern distillation both encode HOW to control the process.

The remaining gap between modern (4 PCs) and Voynich (5 PCs) may reflect:
1. The Voynich's per-folio parameterization (69 programs vs 20 procedures) increasing variance
2. The Voynich encoding additional control dimensions beyond the 7-phase framework (its feature space has 10 dimensions, not 7)
3. Material-specific process physics creating richer internal differentiation

---

## Method

- 20 modern distillation procedures curated from published literature (PMC, FAO, university protocols, industry SOPs)
- 15 different plant materials, 6 distillation methods, 5 scales
- Each procedure coded into 7-phase taxonomy with explicit MIDPROCESS actions
- Feature matrix: recipe × phase proportions, StandardScaler → PCA
- Compared against 228 Brunschwig recipes (same methodology) and Voynich reference (69 folios, from F-BRU-030)

**Script:** `phases/MODERN_DISTILLATION_DIMENSIONAL_COMPARISON/scripts/modern_distillation_comparison.py`
**Results:** `phases/MODERN_DISTILLATION_DIMENSIONAL_COMPARISON/results/dimensional_comparison.json`
