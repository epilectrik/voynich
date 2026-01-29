# B_FOLIO_TEMPORAL_PROFILE

**Status:** COMPLETE | **Constraints:** C664-C669 | **Scope:** B

## Objective

Characterize **within-folio temporal evolution** in Currier B programs. Prior work established micro-level structure (within-line: C556-C562) and macro-level structure (between-folio: C325, C161, C548). This phase measures the **meso-level**: how control statistics change from early to late lines within a single folio-program.

## Key Finding

**Programs are quasi-stationary with mild convergence signals.** 6 of 9 metrics are flat within folios. Three show significant positional evolution:

| Signal | Direction | Strength |
|--------|-----------|----------|
| AX scaffold fraction | Increases late (Q1=15.4% -> Q4=18.1%) | rho=+0.082, p<0.001 |
| QO lane fraction | Declines late (Q1=46.3% -> Q4=41.3%) | rho=-0.058, p=0.006 |
| Hazard proximity | Tightens late (Q1=2.75 -> Q4=2.45 tokens) | rho=-0.104, p<0.001 |

**Stationary dimensions:** CC, EN, FL, FQ role fractions; LINK density; kernel k/h/e rates; hazard-class token density; escape density.

## Interpretation

The controller maintains constant hazard exposure, monitoring intensity, and kernel contact throughout program execution. The three significant signals are consistent with convergence behavior: late-program lines accumulate scaffolding (AX), shift from energy-emphasis to stabilization-emphasis (QO->CHSH), and operate within a tighter risk envelope (hazard proximity). This is a thermostat approaching steady-state, not a recipe advancing through phases.

REGIME_4 (precision-constrained) is uniquely flat across all dimensions. REGIME_2 (steady-state vigilance) shows the strongest temporal evolution in lane balance (-9.9pp) and hazard proximity (-0.602 slope).

## Notable Discovery

Zero forbidden transition events across the entire H-track B corpus. The 17 token-level forbidden pairs (C109, phase18a) never occur literally. Hazard topology operates at the class level, not the specific token-pair level.

## Scripts

| Script | Tests | Output |
|--------|-------|--------|
| `folio_temporal_metrics.py` | T1: Role profile, T2: LINK density, T3: Kernel contact + clustering | `folio_temporal_metrics.json` |
| `folio_temporal_dynamics.py` | T4: Escape/hazard, T5: Lane balance, T6: Hazard proximity | `folio_temporal_dynamics.json` |

## Constraints

| # | Name | Key Result |
|---|------|------------|
| C664 | Role Profile Trajectory | AX increases late; EN marginal; regime-dependent EN/FL slopes |
| C665 | LINK Density Trajectory | Stationary (extends C365 to meso-level) |
| C666 | Kernel Contact Trajectory | k/h/e all stationary (extends C458 to within-folio) |
| C667 | Escape/Hazard Density Trajectory | Hazard flat; 0 forbidden events; Q4 escape efficiency decline |
| C668 | Lane Balance Trajectory | QO declines late; REGIME_2 strongest; REGIME_4 flat |
| C669 | Hazard Proximity Trajectory | Distance tightens late; QO tightens, CHSH static; REGIME_4 flat |

## Data Dependencies

- `phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json` (token -> 49 classes)
- `phases/REGIME_SEMANTIC_INTERPRETATION/results/regime_folio_mapping.json` (folio -> REGIME 1-4)
- `phases/15-20_kernel_grammar/phase18a_forbidden_inventory.json` (17 forbidden pairs)
- `scripts/voynich.py` (canonical transcript library)

## Cross-References

- C458: Execution design clamp (hazard clamped, recovery free) -- within-folio stationarity confirms
- C548: Gateway front-loading (rho=-0.368) -- operates at manuscript level, NOT within folios
- C556-C562: Within-line positional structure -- micro-level complements meso-level
- C643-C647: Lane mechanics -- lane balance now shown to drift CHSH-ward within folios
- C494: REGIME_4 precision axis -- uniquely flat across all meso-temporal dimensions
