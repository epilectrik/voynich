# C569: AX Proportional Scaling

**Tier:** 2 (Structural Inference)
**Phase:** AX_FUNCTIONAL_ANATOMY
**Scope:** Currier B grammar / pipeline behavior
**Status:** VALIDATED (re-verified 2026-01-26 with 19 AX classes)

## Claim

AX class count scales proportionally with total pipeline vocabulary on average (fraction = 0.429 vs expected 0.428, deviation < 0.001), but the composition of surviving AX classes has independent structure beyond proportional scaling (R² = 0.82).

## Evidence

### Proportional Fraction
- Actual mean AX fraction: 0.4291
- Expected weighted fraction (by survival rates): 0.4283
- Deviation: +0.0009 (essentially zero)

### Linear Model
- AX_count = 0.3929 * total_count + offset
- R² = 0.8211 (Pearson r = 0.9062)
- NOT pure byproduct (R² < 0.9 threshold)

### Subgroup Asymmetry
- AX_INIT: slope 0.1295 (R² = 0.62)
- AX_MED: slope 0.1706 (R² = 0.66)
- AX_FINAL: slope 0.0928 (R² = 0.50)

## Interpretation

AX volume is what you'd expect from the pipeline (the fraction is nearly exact), but WHICH AX classes survive shows independent structure. AX_INIT is over-represented relative to expectation, AX_FINAL is under-represented. This means the pipeline preferentially preserves frame-opening classes while frame-closing classes rely on universal MIDDLEs (classes 21, 22).

## Dependencies

- C563: AX subgroups
- C567: AX-operational MIDDLE sharing
- C568: AX pipeline ubiquity
