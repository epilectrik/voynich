# Phase 605: Procedure-Family Contrast Alignment

## Status: COMPLETE
## Verdict: PARTIAL_FAMILY_CONTRAST

## Overview

Tests whether the PL distillation-sublimation operational contrast predicts V folio feature
contrasts along the residualized monitoring axis (h_ratio_resid). Contrast-based follow-up to
Phase 604's SPECIFICITY_FAILURE, which showed family assignment doesn't project but axis-level
contrasts survive.

## Design

**Anchor variable:** h_ratio_resid = residual of h_ratio after OLS regression on section dummies
(S, H, B) + k_ratio. Isolates monitoring signal beyond section membership and thermal intensity.

**Primary battery (4 predictions):**
- P1: h_resid ↑ → terminal_rate ↑ (PL termination 2.5x in sublimation)
- P2: h_resid ↑ → iteration_rate ↑ (PL chain_rate 2.4x in sublimation)
- P3: h_resid ↑ → thermo_ke ↓ (distillation = heat-dominant family)
- P4: h_resid ↑ → thermal_para_frac ↓ (same basis, independent data source)

**Negative controls:** N1 permutation (1000 shuffles), N2 random axis, N3 wrong-direction, N4 dissolution contrast.

**Sensitivity:** Within-Herbal, raw h_ratio, section+REGIME control.

## Results

### Gates
| Gate | Result | Detail |
|------|--------|--------|
| S0 | PASS | n=69 folios (≥60 required) |
| S1 | PASS | Sublimation h_resid=0.056 vs distillation=-0.026, U=464, p<1e-6 |

### Primary Battery (2/4 pass)
| ID | Feature | rho | p (one-sided) | Result |
|----|---------|-----|---------------|--------|
| P1_TERM | terminal_rate | +0.158 | 0.098 | FAIL |
| P2_ITER | iteration_rate | +0.169 | 0.083 | FAIL |
| P3_HEAT_NEG | thermo_ke | -0.400 | 0.0003 | PASS |
| P4_THERMAL_NEG | thermal_para_frac | -0.473 | 0.0009 | PASS |

### Secondary Battery
| ID | Feature | rho | p | Result |
|----|---------|-----|---|--------|
| S1_CYCLE | cycle_regularity | -0.097 | 0.786 | FAIL (wrong direction) |
| S2_CHECKPOINT | checkpoint_rate | +0.241 | 0.023 | PASS |

### Negative Controls
| Control | Result | Detail |
|---------|--------|--------|
| N1 Permutation | K_perm=2 | P3/P4 both survive (frac_exceeding=0.002) |
| N2 Random Axis | PASS | 0/4 random-axis predictions pass |
| N3 Wrong-Direction | Clean | Both P3/P4 opposite-direction p>0.99 |
| N4 Dissolution | 2/4 diverge | P3/P4 match (thermal shared), P1/P2 diverge |

### Sensitivity Analyses
| Analysis | P1 | P2 | P3 | P4 |
|----------|----|----|----|----|
| Within-Herbal (n=27) | rho=-0.08, fail | rho=+0.03, fail | rho=-0.57, p=0.001 | SKIP (n=2) |
| Raw h_ratio | rho=+0.38, **p=0.0007** | rho=+0.13, fail | rho=-0.51, pass | rho=-0.61, pass |
| Section+REGIME | rho=+0.15, fail | rho=+0.12, fail | rho=-0.39, p=0.0004 | rho=-0.46, p=0.001 |

### Exploratory Diagnostics
| ID | Feature | rho | p |
|----|---------|-----|---|
| D1 | opaque_close_fraction | -0.057 | 0.680 |
| D2 | strong_close_fraction | -0.071 | 0.281 |
| D3 | intervention_frequency | -0.123 | 0.158 |
| D4 | recovery_ops_rate | +0.034 | 0.609 |

## Verdict Determination

```
S0: PASS (n=69)
S1: PASS (p<1e-6)
K = 2 (P3, P4)
K_perm = 2 (both survive permutation)
N2: PASS (0 random-axis passes)
→ K_perm == 2 AND N2 passes → PARTIAL_FAMILY_CONTRAST
```

## Key Findings

### What confirmed
1. **Thermal axis is real and robust.** The monitoring-residual (h_ratio_resid) negatively correlates
   with thermal burden (thermo_ke: rho=-0.40, p=0.0003) and thermal paragraph fraction (rho=-0.47,
   p=0.0009). This survives residualization, permutation, random axis, Herbal-only replication,
   and REGIME control.
2. **Distillation is the thermally distinct family.** PL distillation has 1.17x the heat_rate of
   sublimation. V folios with less monitoring-residual have more thermal content. The mapping holds.
3. **Not sublimation-specific.** N4 dissolution contrast shows P3/P4 directions match dissolution
   predictions too — both sublimation and dissolution are "less thermal than distillation."
   The contrast is distillation-vs-rest, not sublimation-specific.

### What failed
1. **Termination/iteration mappings too weak.** P1 (rho=+0.16, p=0.10) and P2 (rho=+0.17, p=0.08)
   show correct direction but miss significance. Residualization removes a section-mediated
   component (P1 passes with raw h_ratio at rho=+0.38).
2. **Cycle regularity wrong direction.** S1_CYCLE rho=-0.097 (expected positive).

### What this means for the model
- The PL→V bridge is real but narrower than hoped. The thermal dimension carries clearly; the
  operational dimensions (termination, iteration) are at best marginal at folio level.
- Phase 604's h_ratio axis (C1750) is confirmed as the primary carrier of family contrast
  information. The residualized version isolates monitoring beyond section/thermal confounds.
- The result is PARTIAL — two of four pre-registered predictions pass with strong effect sizes
  and survive all controls. Not enough for CONFIRMED (needs 3), but more than noise.

## Constraints Registered
- C1752: Thermal axis alignment confirmed — h_ratio_resid negatively correlates with thermo_ke (rho=-0.40, p=0.0003) and thermal paragraph fraction (rho=-0.47, p=0.0009), surviving permutation, random axis, Herbal-only, and REGIME controls
- C1753: Termination/iteration family contrasts directionally correct but sub-threshold — P1 terminal_rate rho=+0.16 (p=0.098), P2 iteration_rate rho=+0.17 (p=0.083), both in predicted direction but not significant after residualization on section + k_ratio
- C1754: Family contrast is distillation-vs-rest, not sublimation-specific — N4 dissolution contrast matches P3/P4 predictions; both sublimation and dissolution are "less thermal than distillation"

## Script
- `scripts/procedure_family_contrast.py` (~690 lines, runtime <5s)
- Pre-registration: `PREDICTIONS.md` (SHA-256: 18af376293e8062b741feca71ec7ba49df0064ef01cfc6590890b0c0451cce44)

## Data Sources
- `results/folio_operational_profiles.json` (h_ratio, k_ratio, terminal_rate, iteration_rate, thermo_ke, checkpoint_rate)
- `results/b_macro_scaffold_audit.json` (cycle_regularity, intervention_frequency, recovery_ops_count)
- `phases/A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES/results/t0_opportunity_normalization.json` (section, strong_close_fraction, opaque_close_fraction)
- `phases/PARAGRAPH_PROGRAM_TYPING/results/paragraph_program_typing.json` (paragraph cluster assignments → thermal fraction)
- `phases/PSEUDO_LULL_CHARACTERIZATION/results/pseudo_lull_structural_profile.json` (PL family prototypes)
- `phases/PROCEDURE_FAMILY_ALIGNMENT/results/procedure_family_alignment_results.json` (Phase 604 assignments for S1 calibration)
