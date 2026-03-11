# Phase 580: Apparatus Response Manifold Synthesis

## Executive Summary

Two-space manifold analysis of 76 eligible Currier B folios across 3 apparatus families (A1=21, A2=18, A3=37). Space A (response surface, 11 features) captures what kind of apparatus each folio is; Space B (realized performance, 4 features) captures how each folio actually performs.

### Constraint Verdicts

| ID | Track | Verdict |
|----|-------|---------|
| C1667 | Response-surface manifold (Space A, 11 apparatus features) h... | **MANIFOLD_DIFFUSE** |
| C1668 | Apparatus families (A1=21, A2=18, A3=37) show LOO accuracy 0... | **FAMILY_GRADIENT** |
| C1669 | Landscape classes (SA/TD/FR) show 2 significant KW PCs in Sp... | **LANDSCAPE_ALIGNED** |
| C1670 | Folio accent vs manifold position: canonical r1=0.871, max i... | **ACCENT_IS_MANIFOLD_POSITION** |

## Two-Space Design Rationale

Per expert revision, we split features into two manifolds to avoid a self-repackaging PCA that rediscovers known verdict variables:

- **Space A (Response Surface):** F1-F5 apparatus fits, 5 ablation deltas, mean_CTS. These describe *what kind of apparatus* a folio has.
- **Space B (Realized Performance):** DYE_advantage, CCS1, z_margin, PEF. These describe *how the folio actually performs*.

## Feature Matrices and Correlations

- Space A: 11 features, effective rank = 4
- Space B: 4 features, effective rank = 1

High correlations (|r| > 0.7) in Space A:

- abl_CROSS_COUPLING ~ abl_TR_TO_Y: r=0.8989
- abl_CLOSE_RECOVERY ~ abl_CONTAINMENT: r=0.9165

## Space A Dimensionality and PC Interpretation

- Effective rank: 5.88
- PCs for 70%: 4
- PCs for 80%: 5
- PCs for 90%: 7
- Scree elbow: PC1

### PC Loadings (Space A)

- **PC1:** abl_CLOSE_RECOVERY(+0.445), F1(-0.430), abl_TR_TO_Y(-0.406), abl_CONTAINMENT(+0.396)
- **PC2:** abl_CROSS_COUPLING(+0.477), abl_TR_TO_Y(+0.412), F3(-0.365), mean_CTS(+0.335)
- **PC3:** abl_Y_SENSITIVITY(-0.517), abl_CONTAINMENT(-0.469), mean_CTS(+0.439), abl_CLOSE_RECOVERY(-0.342)
- **PC4:** F4_raw(-0.717), F5(+0.562), F3(+0.251), F2(+0.237)
- **PC5:** F2(+0.856), mean_CTS(+0.411), abl_Y_SENSITIVITY(+0.241), F4_raw(+0.134)

**C1667: MANIFOLD_DIFFUSE** -- Space A effective rank = 5.88, PCs for 80% = 5

## Space B Dimensionality

- Effective rank: 1.40
- PCs for 80%: 1

## Family Geometry

- LOO accuracy: 0.78
- Silhouette: 0.1342
- Permutation p: 0.0010
- Wrong centroid: 16/76

### Between-family distances

- A1-A2: 3.7462
- A1-A3: 2.5502
- A2-A3: 2.51

### Family elongation

- A1: ratio=1.34, direction=PC1:-0.147, PC2:0.314, PC3:-0.133
- A2: ratio=1.36, direction=PC1:-0.792, PC2:0.476, PC3:-0.103
- A3: ratio=1.16, direction=PC1:-0.837, PC2:0.454, PC3:-0.279
- Most elongated: **A2**

### A3 bridge analysis

- Bridge fraction: 20/37 (0.54)
- Spanning ratio: 5.31
- Mean dist to A1: 3.6855
- Mean dist to A2: 3.5741

**C1668: FAMILY_GRADIENT** -- LOO accuracy = 0.78, silhouette = 0.13

## Landscape Correspondence

### Space A
- Significant KW PCs: 2
- Classification accuracy: 0.70
- B/W ratio: 1.07

- PC1: H=19.75, p=0.0001 ***
- PC2: H=0.72, p=0.6987
- PC3: H=11.43, p=0.0033 ***
- PC4: H=2.51, p=0.2853
- PC5: H=0.20, p=0.9032

### Space B
- Significant KW PCs: 1
- Classification accuracy: 0.87
- B/W ratio: 5.36

### Cross-space comparison
- Better space for landscape: **B**

### Cross-space correlations (|r| > 0.3)

- PC1_vs_DYE_advantage: -0.3418
- PC1_vs_z_margin: -0.3345
- PC1_vs_PEF: -0.4309
- PC2_vs_CCS1: 0.5475
- PC3_vs_DYE_advantage: 0.4383
- PC3_vs_z_margin: 0.3612
- PC3_vs_PEF: 0.3347

**C1669: LANDSCAPE_ALIGNED** -- Space A: 2 significant PCs, three-pole reproduced (B/W=1.07)

## Accent Reinterpretation

- Canonical correlations: [0.8713, 0.7453, 0.4764]
- Incremental R² for CCS1: 0.1684
- Incremental R² for DYE: 0.2677
- Within-A2 R²: 0.9457

### Top Spearman correlations

- accent_PC1_vs_manifold_PC1: -0.8025
- accent_PC3_vs_manifold_PC4: 0.4837
- accent_PC1_vs_manifold_PC3: -0.4232
- accent_PC3_vs_manifold_PC2: 0.3926
- accent_PC2_vs_manifold_PC4: -0.3923
- accent_PC1_vs_manifold_PC2: -0.3469

### Forgiving-edge distance

- accent_PC1_vs_FR_dist: 0.6039
- accent_PC2_vs_FR_dist: 0.0335
- accent_PC3_vs_FR_dist: -0.0467

### Stubborn folios in manifold

| Folio | Class | FR distance | PC scores |
|-------|-------|-------------|-----------|
| f39v | STRUCTURAL_ENDPOINT | 1.091 | PC1=3.45, PC2=-0.20, PC3=-0.67, PC4=-0.44, PC5=-0.92 |
| f55v | STRUCTURAL_ENDPOINT | 4.889 | PC1=5.61, PC2=-3.15, PC3=1.00, PC4=1.23, PC5=0.53 |
| f86v5 | STRUCTURAL_ENDPOINT | 3.352 | PC1=3.56, PC2=1.53, PC3=-3.89, PC4=-0.91, PC5=1.05 |
| f95r2 | STRUCTURAL_ENDPOINT | 2.682 | PC1=4.98, PC2=-0.82, PC3=-1.87, PC4=-0.36, PC5=-1.80 |
| f40r | PARAMETER_ACHIEVABLE | 3.841 | PC1=4.12, PC2=-0.25, PC3=1.46, PC4=0.96, PC5=-2.28 |
| f50v | PARAMETER_ACHIEVABLE | 2.800 | PC1=2.00, PC2=1.70, PC3=-2.55, PC4=0.40, PC5=1.13 |
| f85r2 | PARAMETER_ACHIEVABLE | 2.128 | PC1=2.54, PC2=1.17, PC3=-2.73, PC4=-0.69, PC5=0.58 |
| f86v6 | PARAMETER_ACHIEVABLE | 2.238 | PC1=1.19, PC2=-1.20, PC3=-1.34, PC4=-0.44, PC5=-0.06 |

Point-biserial (SE=0 vs PA=1):

- manifold_PC1: -0.6547
- manifold_PC2: 0.2182
- manifold_PC3: 0.0
- manifold_PC4: 0.1091
- manifold_PC5: 0.1091

**C1670: ACCENT_IS_MANIFOLD_POSITION** -- Canonical r1=0.871, max incr R²=0.268, max partial r=0.520

## Tier-3 Interpretation Freeze

> Currier B's productive closure advantage is broadly real but apparatus-conditioned. Regime-admission gating suppresses the main counterfeit-closure mechanism, especially in A2, but a residual forgiving pole remains. That pole is not a distinct hidden subfamily, not an opportunity artifact, and not recoverable by modest folio-specific retuning. It represents the forgiving edge of a continuous apparatus-response manifold, dominated by the same close-recovery channels that define A2 more generally. Folio accent and residual variance are therefore best understood as machine-fit positions on a real response surface, not as noise or decipherment failure.

## Constraints C1667-C1670

| ID | Claim | Verdict | Tier | Scope |
|----|-------|---------|------|-------|
| C1667 | Response-surface manifold (Space A, 11 apparatus features) has effective rank 5.88 and requires 5 PCs for 80% variance. | MANIFOLD_DIFFUSE | 2 | B_APPARATUS |
| C1668 | Apparatus families (A1=21, A2=18, A3=37) show LOO accuracy 0.78 and silhouette 0.13 in response-surface manifold. | FAMILY_GRADIENT | 2 | B_APPARATUS |
| C1669 | Landscape classes (SA/TD/FR) show 2 significant KW PCs in Space A with between/within ratio 1.07. | LANDSCAPE_ALIGNED | 2 | B_APPARATUS |
| C1670 | Folio accent vs manifold position: canonical r1=0.871, max incremental R²=0.268, max partial |r|=0.520. | ACCENT_IS_MANIFOLD_POSITION | 2 | B_APPARATUS, ACCENT |
