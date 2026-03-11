# Phase 580: Apparatus Response Manifold Synthesis

**Status:** COMPLETE
**Phase type:** Analytical synthesis
**Simulation budget:** 0 traces

## Goal

Build two related apparatus manifolds (response-surface vs realized-performance) for all 76 eligible Currier B folios. Derive geometry of family occupancy, landscape alignment, and accent reinterpretation.

## Target Constraints

| ID | Track | Verdict | Runtime |
|----|-------|---------|---------|
| C1667 | Manifold dimensionality | MANIFOLD_DIFFUSE | <1s |
| C1668 | Family geometry | FAMILY_GRADIENT | <1s |
| C1669 | Landscape alignment | LANDSCAPE_ALIGNED | <1s |
| C1670 | Machine-fit reinterpretation | ACCENT_IS_MANIFOLD_POSITION | <1s |

## Scripts

| Script | Purpose | Status |
|--------|---------|--------|
| t0_feature_matrix_assembly.py | Build Space A (76x11) and Space B (76x4), z-score, correlations | PASS |
| t1_manifold_embedding.py | PCA on both spaces, dimensionality diagnostics | PASS |
| t2_family_occupancy.py | Family centroids, LOO, silhouette, elongation, A3 bridge | PASS |
| t3_landscape_correspondence.py | SA/TD/FR mapping onto manifold regions | PASS |
| t4_accent_machine_fit.py | Accent vs manifold correlation, canonical CCA, partial | PASS |
| t5_synthesis.py | Write C1667-C1670, generate REPORT_580.md | PASS |

## Data Sources

| File | Fields |
|------|--------|
| PRODUCTIVE_DISRUPTION_EXPANSION/results/t1_full_scale_setup.json | F1-F5, profile, section |
| A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES/results/t1_mechanism_ablation.json | baseline DYE, ablation deltas |
| COUNTERFEIT_CLOSURE_THRESHOLD_RECOVERY_GATE_MAP/results/t4_landscape_model.json | z_margin, PEF, mean_CTS, classification |
| FOLIO_ACCENT_VECTOR/results/folio_accent_vector.json | accent PC1-3 (72 folios) |

## Two-Space Design

- **Space A (Response Surface, 76x11):** F1-F5, 5 ablation deltas, mean_CTS
- **Space B (Realized Performance, 76x4):** DYE_advantage, CCS1, z_margin, PEF

## Key Results

- Space A effective rank = 5.88, 5 PCs for 80% variance (diffuse manifold)
- Space B effective rank = 1.40, 1 PC for 80% (dominated by DYE/z_margin axis)
- Families separable by LOO (78%) but silhouette low (0.13) — gradient, not clusters
- A2 most elongated (ratio 1.36), A3 bridges A1-A2 (54% equidistant)
- Landscape classes align with Space A (2 sig KW PCs, B/W > 1)
- Accent strongly captured by manifold (canonical r1=0.87, incr R²=0.27)
