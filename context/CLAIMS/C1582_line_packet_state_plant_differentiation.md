# C1582: Line packet state produces statistically significant plant state differentiation

**Tier:** 2
**Phase:** 563 (VIRTUAL_APPARATUS_COUPLING)
**Scope:** B, virtual apparatus, line, packet, state, C1425, C1426, C1427, C1428, C1578

## Claim

Line packet state (SPEC/WORK/CLOSE phases from C1425-C1430 three-zone line architecture) produces statistically significant plant state differentiation across all 7 virtual apparatus state variables globally (Kruskal-Wallis p<0.003 for all 7). Strongest effects: C (containment) H=191.6, Y (yield accumulation) H=148.4. The line-level three-zone architecture is the primary channel through which grammar couples to apparatus.

## Evidence

- P2 packet shape: 7/7 state variables significant globally (Kruskal-Wallis)
- Strongest: C (containment) H=191.6, Y (yield) H=148.4
- Per-folio median: 6/7 state variables significant
- 7 state variables tested: T (temperature), RC (reflux cycling), S (stability), C (containment), TR (throughput rate), X (extraction progress), Y (yield accumulation)
- Effect consistent across all 7 pilot folios and 3 apparatus profiles

## Provenance

- T5: `phases/VIRTUAL_APPARATUS_COUPLING/scripts/t5_plant_behavior_validation.py`
- Builds on: C1425 (line length unimodal), C1426 (line-initial specification), C1427 (line-final transition), C1428 (THERMAL peak-then-decline), C1578 (E4 line-phase domain adjustment)
