# C676: Morphological Parameterization Trajectory

**Status:** VALIDATED | **Tier:** 0 | **Phase:** B_LINE_SEQUENTIAL_STRUCTURE | **Scope:** B

## Finding

While class proportions and MIDDLE identity are position-stable (C664, C675), the **morphological parameterization** of tokens evolves significantly across folio position. PREFIX profile (chi2 p=3.7e-9) and suffix profile (chi2 p=1.7e-7) both shift. Late-program lines have more bare tokens (+4.7pp), fewer e_family suffixes (-3.7pp), and fewer qo-prefixed tokens (-3.2pp).

## PREFIX Trajectory

| PREFIX | rho | p | Direction |
|--------|-----|---|-----------|
| qo | -0.085 | 3.1e-5 | Declines late |
| da | -0.048 | 0.020 | Declines late |
| ot | -0.045 | 0.028 | Declines late |
| other | +0.057 | 0.005 | Rises late |
| ch, sh, ol, ok, ct, None | ns | >0.05 | Flat |

PREFIX overall chi2 = 92.86, dof=27, p=3.71e-9.

## Suffix Trajectory

| Suffix | rho | p | Direction |
|--------|-----|---|-----------|
| bare | +0.095 | 3.5e-6 | Rises Q1=47.6%→Q4=52.3% |
| e_family | -0.087 | 2.0e-5 | Declines Q1=20.8%→Q4=17.1% |
| ol | -0.070 | 6.4e-4 | Declines |
| y | -0.051 | 0.012 | Declines |
| aiin, other | ns | >0.05 | Flat |

Suffix overall chi2 = 61.01, dof=15, p=1.69e-7.

## Articulator Rate

Overall articulator rate is flat (rho=-0.020, p=0.330). Per-type: 'd' (rho=+0.248, p=0.008) and 'r' (rho=+0.259, p=0.033) increase late, but on small samples (n=115, n=68).

## Interpretation

The control system shifts its morphological mode across folio position while maintaining constant class deployment. Late-program lines use simpler morphological forms (bare tokens, fewer prefixes), consistent with C668's QO lane decline and C669's hazard proximity tightening. The qo PREFIX decline mirrors the QO class fraction decline (C668: rho=-0.058). This confirms that morphological parameterization tracks the same convergence dynamics visible at the class level, but with higher signal strength.

## Provenance

- Script: `phases/B_LINE_SEQUENTIAL_STRUCTURE/scripts/line_token_trajectory.py` (Tests 7-9)
- Extends: C664-C669 (class-level stationarity), C668 (QO decline), C267 (PREFIX/MIDDLE/SUFFIX structure)
