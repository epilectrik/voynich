# C1587: A2_SEALED_RECIRCULATION underperforms A1_BATH_REFLUX for Herbal folios

**Tier:** 3
**Phase:** 563 (VIRTUAL_APPARATUS_COUPLING)
**Scope:** B, virtual apparatus, profile, Herbal, assignment, C1248, C1249, C1380

## Claim

Virtual apparatus profile A2_SEALED_RECIRCULATION underperforms A1_BATH_REFLUX for Herbal folios assigned to A2: f55r viability 0.742 (A2) vs 1.000 (A1), f40v viability 0.991 (A2) vs 1.000 (A1). 2/2 A2-assigned Herbal folios would achieve better coupled-plant behavior under A1. Suggests section-to-profile assignment needs refinement for Herbal REGIME_2 folios.

## Evidence

- P8 preferred profile detail: f55r preferred=A2 but A1 dominates on viab/haz/Y
- f55r: A2 viability 0.742 vs A1 viability 1.000
- f40v: A2 viability 0.991 vs A1 viability 1.000
- 2/2 Herbal A2-assigned folios prefer A1 on primary metrics
- Overall P8 PASS: 5/7 preferred profiles best on >=1 metric
- A2 profile defined from C1248 sealed/sustained apparatus marker co-occurrence

## Provenance

- T5: `phases/VIRTUAL_APPARATUS_COUPLING/scripts/t5_plant_behavior_validation.py`
- T6: `phases/VIRTUAL_APPARATUS_COUPLING/scripts/t6_synthesis.py`
- Builds on: C1248 (apparatus-marker co-occurrence architecture), C1249 (section-conditioned apparatus diversity), C1380 (apparatus profile partially explains AXM residual)
