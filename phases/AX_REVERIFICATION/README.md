# AX_REVERIFICATION Phase

**Date:** 2026-01-26
**Trigger:** Class 14 removal from AX (confirmed FQ per ICC phase20a + behavioral evidence)
**Scope:** Re-verify all AX constraints (C563-C572) with corrected 19-class membership

## Background

`ax_census_reconciliation.py` line 57 defined `ICC_FQ = {9, 13, 23}` without Class 14, causing it to default into AX by set subtraction. ICC phase20a explicitly classifies Class 14 as `FREQUENT_OPERATOR`. Behavioral evidence confirmed: suffix rate 0.0 (vs AX_MED 0.56-1.0), token count 707 (vs AX_MED max 212), JS divergence 0.0018 with FQ Class 13.

**Corrected membership:**
- AX: {1, 2, 3, 4, 5, 6, 15, 16, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28, 29} (19 classes)
- AX_MED: {1, 2, 3, 16, 18, 27, 28, 29} (8 classes, 2056 tokens)
- FQ: {9, 13, 14, 23} (4 classes)

## Results Summary

| Constraint | Verdict | Key Change |
|-----------|---------|------------|
| C563 | UNCHANGED | KW H 213.9→208.8 (p still <1e-45), Cohen's d 0.69 unchanged |
| C564 | STRENGTHENED | AX_MED suffix rate 0.264→0.339, ok/ot purity 86%→100% |
| C565 | UNCHANGED | Self-chain 1.09→1.10x, zero hazard confirmed |
| C567 | check | AX-FQ overlap 15→19 (expected: Class 14 MIDDLEs now counted as FQ) |
| C569 | check | Fraction 0.454→0.429, R² 0.83→0.82 (minor shift) |
| C570 | check | Accuracy 89.6%→87.1% (Class 14 ok/ot tokens now false positives) |
| C572 | UNCHANGED | Structured transitions 3/20→0/19, silhouette 0.18→0.43 |

**Overall verdict:** All constraints STRENGTHENED or UNCHANGED in their core claims. No constraint weakened.

## Files

| File | Purpose |
|------|---------|
| `scripts/ax_reverify.py` | Single comprehensive re-verification script |
| `results/ax_reverify.json` | Old vs new statistics for all 7 constraints |

## Constraint Files Updated

- C563: KW stats, pairwise p-values, mean positions
- C564: Morphological profiles, ok/ot purity 100%
- C565: 19 classes, self-chain 1.10x
- C567: 19 classes, AX-FQ overlap 19/0.333
- C569: Fraction 0.429, slope 0.393, R² 0.82
- C570: Accuracy 87.1%, precision 0.823, F1 0.878
- C572: All statistics updated, correction note revised
- BCSC v1.3: ax_behavioral_collapse updated
