# C816: CC Positional Ordering

## Constraint

CC subtypes occupy distinct positions in the control loop sequence. **daiin initiates the loop** at mean position 0.413, significantly earlier than LINK (0.476), while ol and ol_derived are medial (0.511-0.515).

Complete ordering:
```
daiin (0.413) -> LINK (0.476) -> KERNEL (0.477) -> ol (0.511) -> ol_derived (0.515) -> FL (0.576)
```

## Evidence

| Phase | Mean Position | Count |
|-------|---------------|-------|
| daiin | 0.413 | 314 |
| LINK | 0.476 | 3,047 |
| KERNEL | 0.477 | 15,957 |
| ol | 0.511 | 421 |
| ol_derived | 0.515 | 288 |
| FL | 0.576 | 1,078 |

Statistical comparisons:
- daiin vs LINK: delta=-0.063, p=7.6e-4 ***
- daiin vs KERNEL: delta=-0.064, p=2.1e-4 ***
- daiin vs FL: delta=-0.163, p=1.2e-13 ***
- ol vs LINK: delta=+0.035, p=0.029 *

## Interpretation

CC is not a monolithic phase - it has internal temporal structure:
1. **daiin** is the loop INITIATOR - earliest control token
2. **ol/ol_derived** are MEDIAL - bridge to kernel operations
3. This extends C813 (LINK->KERNEL->FL) to: **daiin->LINK->KERNEL->ol->FL**

## Provenance

- Phase: CC_CONTROL_LOOP_INTEGRATION
- Script: t1_cc_positional_integration.py
- Related: C813 (canonical phase ordering), C557 (daiin line-initial trigger)

## Tier

2 (Validated Finding)
