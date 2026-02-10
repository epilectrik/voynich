# C952: FL Stage-Suffix Global Independence

**Tier:** 2 | **Scope:** B | **Phase:** FL_RESOLUTION_TEST

## Statement

FL stage does not affect the suffix morphology of co-occurring operational tokens globally. Suffix distributions are flat across all six FL stages.

## Evidence

- Chi-squared (stage x suffix): p = 0.751, V = 0.089
- Spearman (stage vs suffix length): rho = 0.008, p = 0.806
- NMI(stage, suffix) vs shuffle: 34.3th percentile, p = 0.657
- Per-role: EN p = 0.247, AX p = 0.975, FQ p = 0.687

## Exception

ch-prefixed FL shows a significant suffix effect (NMI p = 0.004, 7x global). See C953.

## Provenance

- `phases/FL_RESOLUTION_TEST/scripts/03_suffix_profile.py`
