# C1585: CTS continuous closure contributes genuine value to coupled plant behavior

**Tier:** 2
**Phase:** 563 (VIRTUAL_APPARATUS_COUPLING)
**Scope:** B, virtual apparatus, CTS, closure, line, paragraph, C1579, C1434, C1440, C1566

## Claim

CTS (Continuous Terminal Score) continuous closure encoding contributes genuine value to coupled plant behavior. Full trace outperforms no-CTS baseline (B3) on viability for 6/7 folios and Y_final for 7/7 folios. Closure C-separation (close lines having higher containment than work lines) is positive for 6/7 folios. CTS is not just a better executor feature -- it produces genuine plant-level consequences.

## Evidence

- P6 CTS closure: PASS
- Viability: full > B3 (no-CTS) for 6/7 folios
- Y_final: full > B3 for 7/7 folios
- C-separation (close > work containment): positive for 6/7 folios
- Extends Phase 562b finding (C1579) from executor LL improvement to plant-level coupling
- CTS captures q4_opaque_rate (r=0.81) and m-terminal line-final enrichment (C1434)

## Provenance

- T5: `phases/VIRTUAL_APPARATUS_COUPLING/scripts/t5_plant_behavior_validation.py`
- Builds on: C1579 (CTS continuous closure encoding), C1434 (m-terminal 196x line-final enrichment), C1440 (three-tier terminal opacity), C1566 (Q3->Q4 step discontinuity)
