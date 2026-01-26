# REGIME_SEMANTIC_INTERPRETATION Phase

**Status:** ACTIVE
**Started:** 2026-01-25
**Predecessor:** LINE_BOUNDARY_OPERATORS

---

## Goal

Determine what REGIME classifications actually encode - why are some folios REGIME_1/3 (control-intensive) and others REGIME_2/4 (output-intensive)?

---

## Background

From LINE_BOUNDARY_OPERATORS phase:
- REGIME_1/3: Higher L-compound (1.2-1.6%), higher ENERGY (48-50%), lower LATE
- REGIME_2/4: Lower L-compound (0.7-1.0%), lower ENERGY (35-38%), higher LATE

From existing constraints:
- C179-C185: REGIME structure documentation
- C536: Material-Class REGIME Invariance (both animal AND herb route to REGIME_4)
- C537: Token-Level Material Differentiation

---

## Hypotheses

1. **Material Class Hypothesis:** REGIMEs encode material processing type (animal vs herb vs mixed)

2. **Complexity Hypothesis:** REGIMEs encode procedure complexity (simple vs compound)

3. **Procedure Type Hypothesis:** REGIMEs encode Brunschwig procedure categories (distillation vs extraction vs preparation)

4. **Precision Hypothesis:** REGIMEs encode precision requirements (per C494 precision axis)

---

## Test Plan

1. **Material class correlation**
   - Load PP material class assignments (C538)
   - Check if REGIME correlates with dominant material class per folio

2. **Brunschwig procedure correlation**
   - Load suffix patterns (C527 fire-degree)
   - Check if REGIME correlates with fire-degree distribution

3. **Folio content analysis**
   - Check what distinguishes REGIME_1/3 folios from REGIME_2/4
   - Look at illustration types, quire positions, etc.

4. **Precision axis test**
   - Check if REGIME_4 (precision-heavy per C494) has different morphology

---

## Key Questions

1. Why do REGIME_1/3 need more control infrastructure (L-compound)?
2. Why do REGIME_2/4 produce more output marking (LATE)?
3. Is there a procedural interpretation that fits both patterns?

---

## Scripts

- `regime_material_correlation.py` - Material class analysis
- `regime_brunschwig_correlation.py` - Procedure type analysis
- `regime_folio_characterization.py` - Folio content analysis
