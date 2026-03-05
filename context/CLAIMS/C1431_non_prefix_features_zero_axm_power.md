# C1431: Non-PREFIX features add zero predictive power for paragraph AXM

**Tier:** 2
**Scope:** B, paragraph, AXM, MIDDLE, suffix, articulator, line, design-freedom
**Phase:** 520 (PARAGRAPH_AXM_RESIDUAL)
**Date:** 2026-03-05

## Claim

41 features across 8 groups (HEAD atoms, TERMINAL atoms, suffix, line structure, articulators, kernel, MIDDLE properties, interactions) add zero predictive power for paragraph-level AXM self-transition beyond PREFIX composition. Full 41-feature model CV R2=0.707 vs PREFIX-only 0.711 (delta=-0.004). All 7 non-PREFIX groups show negative or zero delta in add-one analysis. Every non-PREFIX feature is either PREFIX-mediated (HEAD via C1411, suffix via C1422, articulators via C1418) or structurally irrelevant (line geometry, kernel fractions).

## Evidence

### Full model performance
- PREFIX only (10 features): CV R2 = 0.711, LOO R2 = 0.780
- Full model (41 features): CV R2 = 0.707, LOO R2 = 0.770
- Training R2: 0.838 (13% overfitting)
- 31 additional features DEGRADE cross-validated performance

### Drop-one group analysis (from full model)
- Drop PREFIX: R2 drops from 0.707 to 0.198 (delta = +0.508) -- PREFIX is sole load-bearing group
- Drop HEAD: R2 = 0.709 (delta = -0.002) -- removing HEAD IMPROVES performance
- Drop TERMINAL: R2 = 0.704 (delta = +0.002) -- negligible
- Drop SUFFIX: R2 = 0.709 (delta = -0.002) -- removing suffix IMPROVES performance
- Drop LINE: R2 = 0.711 (delta = -0.005) -- removing line structure IMPROVES performance
- Drop ARTICULATOR: R2 = 0.713 (delta = -0.006) -- removing articulators IMPROVES performance
- Drop KERNEL: R2 = 0.706 (delta = +0.000) -- kernel contributes zero
- Drop MIDDLE_PROPS: R2 = 0.710 (delta = -0.003) -- removing MIDDLE props IMPROVES performance

### Add-one analysis (each group added to PREFIX)
- HEAD: delta = -0.002
- TERMINAL: delta = -0.003
- SUFFIX: delta = +0.004 (negligible)
- LINE: delta = -0.002
- ARTICULATOR: delta = -0.003
- KERNEL: delta = -0.010 (harmful)
- MIDDLE_PROPS: delta = +0.013 (marginal, vanishes in full model)

### HEAD atom correlations (individually significant but PREFIX-mediated)
- k-initial: rho = +0.491, p = 1.5e-18
- a-initial: rho = -0.553, p = 4.7e-24
- e-initial: rho = +0.259, p = 1.0e-05
- o-initial: rho = -0.333, p = 9.1e-09
- t-initial: rho = +0.258, p = 1.1e-05
- headless_frac: rho = -0.054, p = 0.367 (NS)

All HEAD atom correlations are mediated by PREFIX (C1411 V=0.414).

## Method

- 283 paragraphs with 3+ body lines
- 23,096 Currier B tokens (H-track)
- 10-fold cross-validated Ridge regression (alpha=1.0)
- Leave-one-out R2 for validation
- 10 systematic tests (T1-T10)

## Provenance

- Script: `phases/PARAGRAPH_AXM_RESIDUAL/scripts/paragraph_axm_residual.py`
- Results: `phases/PARAGRAPH_AXM_RESIDUAL/results/paragraph_axm_residual.json`

## Dependencies

- C1405 (paragraph AXM driven by PREFIX)
- C1411 (PREFIX->MIDDLE HEAD selectivity)
- C1418 (PREFIX->ARTICULATOR)
- C1422 (MIDDLE->suffix mode)
- C1169 (AXM residual closed)
- C1035 (AXM residual irreducible)
