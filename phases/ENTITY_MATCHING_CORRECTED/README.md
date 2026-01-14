# Phase: ENTITY_MATCHING_CORRECTED

**Date:** 2026-01-14 | **Status:** Tier 3 SPECULATIVE

---

## Purpose

Re-run the entity matching tests from TIER4_EXTENDED with two critical corrections:

1. **Corrected Degree-to-Regime Mapping:** Based on curriculum position, not regime number
2. **Proposed Folio Order:** Using the optimized sequence that recovers the pedagogical structure

---

## Background

The original entity matching tests (phases/TIER4_EXTENDED/exhaustive_entity_matching.py) used:

```python
# WRONG - based on regime NUMBER
DEGREE_TO_REGIME = {1: 'REGIME_1', 2: 'REGIME_2', 3: 'REGIME_3', 4: 'REGIME_4'}
```

The curriculum realignment discovery (v2.39) showed the correct mapping is based on curriculum POSITION:

| Brunschwig Degree | Material Type | Curriculum Position | CORRECT Regime |
|-------------------|---------------|---------------------|----------------|
| 1st degree | Flowers, delicate | EARLY | **REGIME_2** |
| 2nd degree | Standard herbs | MIDDLE | **REGIME_1** |
| 3rd degree | Roots, resins | LATE | **REGIME_3** |
| 4th degree | FORBIDDEN | N/A | REGIME_4 |

---

## Tests in This Phase

1. **entity_matching_corrected.py** - Full entity matching with corrected mapping
2. **positional_alignment_corrected.py** - T1 positional test with proposed order

---

## Expected Outcomes

If the curriculum hypothesis is correct:
- Puff 1st degree herbs should match REGIME_2 folios (low hazard, introductory)
- Puff 2nd degree herbs should match REGIME_1 folios (moderate hazard, core)
- Puff 3rd degree herbs should match REGIME_3 folios (high hazard, advanced)
- Overall matching score should exceed random significantly

---

## References

- Original test: `phases/TIER4_EXTENDED/exhaustive_entity_matching.py`
- Curriculum discovery: `context/SPECULATIVE/curriculum_realignment.md`
- Proposed order: `results/proposed_folio_order.txt`
- Brunschwig analysis: `results/brunschwig_realignment_test.json`
