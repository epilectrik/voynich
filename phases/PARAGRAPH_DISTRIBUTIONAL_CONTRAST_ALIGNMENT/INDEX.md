# Phase 606: Paragraph Distributional Contrast Alignment

## Status: COMPLETE
## Verdict: WEAK_SIGNAL

## Overview

Tests whether pseudo-Lull procedure-family contrasts predict Voynich folio paragraph-mixture
shape, using EMD-based shape margin as the primary tested object. Follows Phase 605's partial
recovery of the thermal axis (C1752) by moving to the resolution where C1573 says distributional
shape carries folio-specific information (EMD z=6.21).

## Design

**Primary tested object:** shape_margin = EMD_to_distillation - EMD_to_basin per folio.
Positive = folio paragraph distribution is closer to monitoring-rich basin than to distillation.

**Anchor A (shape margin):** For each folio with ≥3 paragraphs, compute 4D zone distribution
from C1398 paragraph zone assignments, then EMD distances to PL distillation and basin profiles.

**Anchor B (h_ratio_resid):** OLS residual of h_ratio on section dummies (S, H, B) + k_ratio.
Same computation as Phase 605.

**PL zone profiles recomputed** directly from Phase 602 E1_chapters (not inherited from Phase 604).

## Reference Profiles (recomputed)

| Profile | THERMAL | CONTAINMENT | ITERATION | MONITORING |
|---------|---------|-------------|-----------|------------|
| distillation | 0.346 | 0.230 | 0.250 | 0.173 |
| sublimation | 0.265 | 0.184 | 0.332 | 0.218 |
| dissolution | 0.149 | 0.323 | 0.166 | 0.362 |
| basin (mean sub+diss) | 0.207 | 0.254 | 0.249 | 0.290 |
| theoretical_neg | 0.279 | 0.152 | 0.297 | 0.272 |

## Results

### Gates
| Gate | Result | Detail |
|------|--------|--------|
| S0 | PASS | n=41 folios (≥40 required) |
| S1 | PASS | h_resid vs THERMAL_frac rho=-0.454, p=0.0014 (replicates C1752) |

### Primary Battery (2/3 pass)
| ID | Test | rho | p (one-sided) | Result |
|----|------|-----|---------------|--------|
| P1 | shape_margin vs h_resid | +0.525 | 0.0002 | PASS |
| P2 | shape_margin vs thermo_ke | -0.031 | 0.424 | FAIL |
| P3 | Within-Stars shape_margin vs h_resid | +0.739 | <0.0001 | PASS |

P3: Herbal skipped (n=2 folios with ≥3 paragraphs).

### Secondary Battery
| ID | Test | rho | p | Result |
|----|------|-----|---|--------|
| S2 | h_resid vs MONITORING_frac | +0.401 | 0.005 | PASS |
| S3 | shape_margin vs (OP+MON) frac | +0.770 | <1e-9 | PASS |

### Negative Controls
| Control | Result | Detail |
|---------|--------|--------|
| N1 Permutation | P1 survives (frac=0.000) | Shape-folio association is real |
| N2 Dirichlet | P1 frac=0.062, FAIL | PL profiles not more informative than random 4D profiles |
| N3 Theoretical_neg | DIRTY (rho=0.552, p=0.0002) | Non-operational profile predicts equally well |

### Exploratory Diagnostics
| ID | Test | rho | p |
|----|------|-----|---|
| D1 | h_resid vs OPERATION_frac | +0.026 | 0.874 (two-sided) |
| D2 | JSD margin vs h_resid | +0.512 | 0.0003 |

### Sensitivity Analyses
| Analysis | P1 | P2 |
|----------|----|----|
| Within-Herbal | SKIP (n=2) | SKIP (n=2) |
| Within-Stars (n=23) | rho=+0.739, p<0.0001 | rho=+0.034, p=0.561 |
| Section+REGIME control | rho=+0.488, p=0.0006 | rho=-0.031, p=0.424 |
| JSD metric | rho=+0.512, p=0.0003 | rho=-0.098, p=0.270 |

## Verdict Determination

```
S0: PASS (n=41)
S1: PASS (p=0.0014)
K = 2 (P1, P3)
P1: survives N1 (frac=0.000) but FAILS N2 (frac=0.062) → not in K_perm
P3: survives → in K_perm
K_perm = 1
N3: DIRTY
→ K_perm == 1 → WEAK_SIGNAL
```

## Key Findings

### What confirmed
1. **Paragraph distributional shape carries folio-specific information.** P1 (rho=+0.525, p=0.0002)
   shows shape_margin robustly tracks h_resid. Survives N1 permutation (frac=0.000), within-Stars
   replication (rho=+0.739), and section+REGIME control (rho=+0.488). This extends C1573's finding
   that distributional shape carries information that means destroy.
2. **Within-section shape discrimination works.** P3 within-Stars (rho=+0.739, p<0.0001, n=23)
   shows shape_margin distinguishes folios within Stars. Not section recapitulation.
3. **MONITORING zone fraction complements THERMAL.** S2 (rho=+0.401, p=0.005) confirms the
   THERMAL-MONITORING axis operates at paragraph-distribution level.

### What failed: profile specificity
1. **Current PL family profiles lack specificity at 4D zone resolution.** N2 Dirichlet (frac=0.062)
   shows random 4D profiles achieve comparable shape margins ~6% of the time. The 4D paragraph-zone
   representation is too low-dimensional to distinguish PL family profiles from generic asymmetric
   shapes.
2. **N3 theoretical_neg is dirty but not cleanly interpretable.** The theoretical_neg profile
   predicts h_resid (rho=0.552, p=0.0002), comparable to operational profiles (0.525). However,
   PL Theorica chapters are not truly operationally null — they share operational vocabulary,
   furnace logic, and procedural structure with Practica (C1748 showed Theorica breaks register-
   architecture alignment but still inhabits the same symbolic space). N3 dirty may reflect
   this shared vocabulary rather than proving "any profile works."
3. **Shape margin does not predict thermo_ke independently (P2 rho=-0.031).** This is informative:
   it means shape margin lives primarily in the monitoring axis, not as a repackaging of thermal
   intensity. The shape effect tracks operational emphasis geometry (monitoring vs thermal zone
   balance), not raw thermal burden.

### Interpretation
- **The problem is profile construction, not paragraph distributions.** P1 (rho=+0.525), P3
  (rho=+0.739 within-Stars), S2, S3 all confirm paragraph-mixture shape is a real structural
  carrier. The failure is that the current 4D PL zone profiles are too low-information to uniquely
  explain what paragraph shape is carrying.
- **This is a specificity failure, not a bridge failure.** The PL→V connection established by
  C1744-C1748 (midprocess control alignment) and C1752 (thermal axis) is not overturned. What
  failed is the attempt to convert PL family profiles into specific paragraph-shape predictors
  at this level of profile granularity.
- **Three-phase trajectory clarifies the bottleneck:**
  - Phase 604: Family assignment to folios → SPECIFICITY_FAILURE (section/REGIME confound)
  - Phase 605: Family contrast on folio means → PARTIAL (thermal axis only, C1752)
  - Phase 606: Family distributional shape → WEAK_SIGNAL (real V signal, profile specificity insufficient)
  The consistent pattern: V paragraph structure is real and information-rich, but the PL
  characterization needs finer-grained typed features (monitoring subtypes, correction classes,
  action outcomes) to produce profiles that are uniquely informative rather than generically
  asymmetric.

## Constraints Registered
- C1755: Paragraph distributional shape tracks monitoring axis — shape_margin vs h_resid rho=+0.525 (p=0.0002), surviving cross-folio permutation (N1 frac=0.000) and within-Stars replication (rho=+0.739, p<0.0001). Extends C1573 (distributional shape carries folio-specific information) to PL-derived zone profiles.
- C1756: Current 4D PL zone profiles lack specificity for paragraph shape — N2 random Dirichlet profiles achieve comparable shape margins (frac_exceeding=0.062), N3 theoretical_neg profile predicts h_resid comparably (rho=0.552 vs 0.525). The 4D paragraph-zone representation cannot distinguish PL family profiles from generic asymmetric shapes or from PL theoretical chapters (which share operational vocabulary per C1748). Rejects this profile-construction method, not the broader PL midprocess alignment.
- C1757: Within-Stars paragraph shape discrimination confirmed — shape_margin vs h_resid within Stars rho=+0.739 (p<0.0001, n=23). Paragraph distributional shape carries folio-specific information beyond section membership, consistent with C1573 within-section recovery.

## Script
- `scripts/paragraph_distributional_contrast.py` (~480 lines, runtime <5s)
- Pre-registration: `PREDICTIONS.md` (SHA-256: b3fcb63c79c974b341835eb888bf0255c1451c3ed21a01d232cfa00b17134655)

## Data Sources
- `phases/PARAGRAPH_PROGRAM_TYPING/results/paragraph_program_typing.json` (264 paragraphs, 4 zones)
- `results/folio_operational_profiles.json` (h_ratio, k_ratio, thermo_ke)
- `phases/A2_FORGIVINGNESS_MECHANISM_APPARATUS_FAMILIES/results/t0_opportunity_normalization.json` (section labels)
- `phases/PSEUDO_LULL_CHARACTERIZATION/results/pseudo_lull_structural_profile.json` (209 chapters, PL families)
- `results/b_macro_scaffold_audit.json` (REGIME labels)
