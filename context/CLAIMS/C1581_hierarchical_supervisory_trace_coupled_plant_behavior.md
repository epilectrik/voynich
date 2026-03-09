# C1581: Full hierarchical supervisory trace coupled to virtual apparatus yields structured plant behavior

**Tier:** 2
**Phase:** 563 (VIRTUAL_APPARATUS_COUPLING)
**Scope:** B, virtual apparatus, hierarchy, trace, coupling, C1575, C1577, C1569

## Claim

Full hierarchical supervisory trace (section -> folio -> paragraph -> line -> token) coupled to a virtual thermal apparatus model yields structured plant behavior beyond section-only, budget-only, and null control baselines. Full trace outperforms budget-only baseline (B2) for 5/7 pilot folios and token-shuffle null (N1) for 7/7 folios. The coupling substrate is real and non-trivial.

## Evidence

- P1 viable envelope: full > B2 for 5/7 folios, full > N1 for 7/7 folios
- Mean viability across 7 pilot folios: 0.9616
- Mean Y_final (yield accumulation): 0.878
- Total hazard events: 34 across 7 folios (4/7 perfect viability)
- P7 null destruction: 3/4 null shuffle types destroy coupled behavior (N1 token-shuffle, N2 domain-preserve, N4 terminal-shuffle)
- 3 apparatus profiles tested: A1_BATH_REFLUX, A2_SEALED_RECIRCULATION, A3_DISTILL_COLLECT

## Provenance

- T5: `phases/VIRTUAL_APPARATUS_COUPLING/scripts/t5_plant_behavior_validation.py`
- T6: `phases/VIRTUAL_APPARATUS_COUPLING/scripts/t6_synthesis.py`
- Builds on: C1575 (hierarchical trace executor), C1577 (null models confirm hierarchy), C1569 (section-level parameterization)
