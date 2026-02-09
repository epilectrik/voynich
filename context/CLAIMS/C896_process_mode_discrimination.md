# C896: Process Mode Discrimination via Kernel Profile

**Tier:** 3
**Scope:** B
**Phase:** BRUNSCHWIG_CLOSED_LOOP_DIMENSIONS (extended)

## Constraint

Kernel ratio profiles discriminate thermal processing modes. HIGH_K_LOW_H paragraphs (k>35%, h<20%) form a distinct minority (8/527 = 1.5%) with 2.5x higher FQ rate than HIGH_H paragraphs, consistent with non-distillation processing.

## Evidence

### Process Type Distribution

| Process Type | Criteria | Count | FQ Rate |
|--------------|----------|-------|---------|
| HIGH_K_LOW_H | k>35%, h<20% | 8 | **24.9%** |
| HIGH_K_MED_H | k>35%, h>=20% | 50 | 18.9% |
| HIGH_H | h>35% | 203 | 9.7% |
| HIGH_E | e>60% | 31 | 15.6% |
| BALANCED | other | 235 | 12.6% |

### Statistical Comparison

HIGH_K_LOW_H vs HIGH_H:
- FQ rate: 24.9% vs 9.7% (p=0.0007)
- EN rate: 29.1% vs 30.2% (p=0.95, n.s.)
- LINK rate: 2.7% vs 2.9% (p=0.97, n.s.)

The 2.5x FQ difference is highly significant while EN and LINK are identical.

## Interpretation (Tier 3 - Conditional on BRSC)

If h (PHASE_MANAGER) encodes drip timing specific to DISTILLATION:

| Process Type | Kernel Profile | Brunschwig Method |
|--------------|----------------|-------------------|
| HIGH_H | h>35% | DISTILLATION - requires drip monitoring |
| HIGH_K_LOW_H | k>35%, h<20% | BOILING/DECOCTION - fire control without phase transitions |
| HIGH_E | e>60% | EXTRACTION/FILTRATION - emphasis on equilibration |

### Brunschwig Method Alignment

BRSC lists 10 methods:
- 5 with fire (balneum marie, ash bath, sand bath, direct fire, alembic)
- 5 without fire (filtration, sunshine, ant hill, baker's oven, horse dung)

Not all are distillation. Decoction and infusion are documented historical practices that involve heating without vapor-liquid phase transitions.

## Why This Matters

1. **Distillation has built-in feedback** (drip rate) - reduces need for recovery
2. **Boiling/decoction lacks this feedback** - requires more recovery capacity
3. **This explains the h-FQ anti-correlation** (C895)

The Voynich appears to encode MULTIPLE thermal processes, not just distillation.

## Relationship to Existing Constraints

| Constraint | Relationship |
|------------|--------------|
| C895 | EXTENDS - provides process-type interpretation of h-FQ correlation |
| C104 | ALIGNS - h=PHASE_MANAGER is distillation-specific |
| C781 | EXPLAINS - FQ bypasses h because recovery is for non-distillation or failed distillation |
| BRSC | CONDITIONAL - interpretation depends on Brunschwig method mapping |

## Provenance

- Scripts: `process_type_discrimination.py`, `process_type_threshold_analysis.py`
- Data: 527 B paragraphs with kernel profiles
- Phase: BRUNSCHWIG_CLOSED_LOOP_DIMENSIONS (extended 2026-01-30)

## Status

SUPPORTED - Statistical evidence is Tier 2; process interpretation is Tier 3 (conditional on BRSC alignment)
