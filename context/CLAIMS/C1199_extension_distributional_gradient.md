# C1199: Extension Distributional Gradient

**Tier:** 2
**Scope:** B
**Phase:** ATOM_EXTENSIBILITY (Phase 425)
**Depends on:** C1197 (atom extensibility partition)

## Constraint

e/i extension rates are non-uniformly distributed across three structural dimensions:

### 1. Section Effect (strong)

| Section | Mean ee-rate | Mean ii-rate | n_folios |
|---------|-------------|-------------|----------|
| S (RECIPE/PHARMA) | 24.5% | 51.0% | 23 |
| C | 22.1% | 64.1% | 5 |
| H (HERBAL) | 15.3% | 67.4% | 32 |
| T | 15.9% | 59.4% | 2 |
| B (BIO) | 10.8% | 47.6% | 20 |

Between-section variance: p<0.001 (ee), p=0.014 (ii). RECIPE/PHARMA uses 2.3x the e-extension rate of BIO.

### 2. Paragraph Position Effect (significant)

| Position | Extension rate | Mean e-run | Mean i-run |
|----------|---------------|------------|------------|
| Header (par_initial) | 5.8% | 1.10 | 1.31 |
| Body | 13.7% | 1.20 | 1.55 |

Chi-squared=29.88, p<0.001. Headers are depleted in extensions; bodies carry proportional specification.

### 3. Folio-Level Variation (within section)

Within-section folio variance in ee-rate:
- HERBAL: CV=0.54 (high — individual folios differ substantially)
- BIO: CV=0.36
- RECIPE/PHARMA: CV=0.20
- C: CV=0.08

Folios are not interchangeable within sections. Individual folios have distinct extension preferences.

## Evidence

82 Currier B folios analyzed (>=30 tokens each), 23,096 tokens total. Extension rate = fraction of e-containing or i-containing MIDDLEs that have consecutive repetition (ee, ii).

Extreme folios: f94r (HERBAL, 0% ee) to f105v (RECIPE, 34.6% ee). This 35-percentage-point range is far larger than would be expected under uniform distribution.

## Interpretation

Extension rates are parameterized at both section and folio level. Sections set a baseline preference (RECIPE high, BIO low), but individual folios tune within that range. This is consistent with folio-level program parameterization where the "intensity" of proportional specification varies by procedure.

## Falsification

Would be falsified if section-level differences disappear under a more refined analysis controlling for MIDDLE vocabulary (i.e., if section differences are entirely driven by vocabulary composition rather than extension behavior).

## Provenance

- `phases/ATOM_EXTENSIBILITY/scripts/atom_extensibility_test.py` (T4, T5)
- `phases/ATOM_EXTENSIBILITY/results/atom_extensibility_results.json`
