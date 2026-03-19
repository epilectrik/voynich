# Phase 607: TYPED_SUBSET_ALIGNMENT — Pre-registered Predictions

## Frozen before execution

## Data Sources
1. `phases/PSEUDO_LULL_CHARACTERIZATION/results/pseudo_lull_structural_profile.json` (E1_chapters)
2. `results/folio_operational_profiles.json` (profiles list)
3. `phases/A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES/results/t0_opportunity_normalization.json` (covariates)
4. `results/b_macro_scaffold_audit.json` (features)

## PL Subset Definitions (from E1_chapters, 7 per-chapter rates)

### Conservative subset pair (Layer A)
- S_HM_hot: heat_rate > median AND monitoring_density < median
- S_HM_mon: monitoring_density > median AND heat_rate < median

### Bold subset (Layer B)
- S_T: termination_rate > median AND judgment_rate > median AND chain_rate < median

### Additional (discrimination only)
- S_R: correction_rate > P75
- S_M: monitoring_density > median AND termination_rate > median

## Feature Mapping (frozen a priori)
| PL Feature | V Feature | V Source | Primary? |
|-----------|-----------|----------|----------|
| heat_rate | thermo_ke | op_profiles | Yes (Layer A) |
| monitoring_density | h_ratio | op_profiles | Yes (both) |
| termination_rate | strong_close_fraction | t0_covariates | Yes (Layer B) |
| judgment_rate | checkpoint_rate | op_profiles | Yes (Layer B) |
| chain_rate | iteration_rate | op_profiles | Secondary |
| correction_rate | qo_density | scaffold | Not primary |
| operational_density | k_ratio | op_profiles | Secondary |

## V Surface: Stars only (n=23, section='S')

## Calibration Gates
- C0: All core subsets (S_HM_hot, S_HM_mon, S_T) have n >= 12 chapters
- C1a: S_T differs from remaining PL on >= 2 of 4 held-out features (monitoring_density, correction_rate, heat_rate, operational_density). Mann-Whitney p<0.05.
- C1b: A1 passes (anchor transfer)

## Layer A: Conservative Anchor
- A1: thermo_ke vs h_ratio negative in Stars (Spearman one-sided, p<0.05)

## Layer B: Threshold-Authenticity Mechanistic Probe
- P1: strong_close_fraction vs checkpoint_rate positive in Stars (Spearman one-sided, p<0.05)
- P2: h_ratio vs checkpoint_rate positive in Stars (Spearman one-sided, p<0.05)

## Secondary Battery
- S1: strong_close_fraction vs iteration_rate negative in Stars (demoted from primary)
- S2: S_HM_hot vs S_HM_mon differ on >= 3/7 features
- S3: All-PL co-variate transfer (same Layer B with 209 chapters)
- S4: PL-internal S_T co-variates (descriptive: term<>judg, term<>chain, mon<>judg)

## Negative Controls
- N1: Feature mapping shuffle (500 permutations of 5 V features). frac(K_shuffle >= K_obs) < 0.05.
- N2: Random PL subset (500 draws, same n as S_T). frac(K_random >= K_obs) < 0.05.

## Exploratory
- D1: Kruskal-Wallis on 7 features across all subsets
- D2: Per-prediction N1/N2 contribution

## Verdict Tree
```
C0 fails -> INSUFFICIENT_DATA
C1a fails -> PL_SUBSET_NOT_DISTINCT
C1b fails -> FRAMEWORK_INVALID

K = P1 + P2 passing
K_ctrl = those passing BOTH N1 AND N2

A1 + K_ctrl >= 2 -> COVARIATE_TRANSFER_CONFIRMED
A1 + K_ctrl = 1  -> PARTIAL_TRANSFER
A1 + K_ctrl = 0  -> ANCHOR_ONLY
```
