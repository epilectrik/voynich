# C768: Role-Compound Correlation

## Constraint

Functional roles show strongly differentiated compound MIDDLE usage. FL (Flow Operator) uses 0% compound MIDDLEs; FQ (Frequent Operator) uses 46.7%. The spread is 46.7pp.

## Quantitative Evidence

| Role | Compound Rate | Tokens | Base-Only Classes | Compound-Heavy Classes |
|------|---------------|--------|-------------------|------------------------|
| FL | **0.0%** | 1,078 | 4 (all) | 0 |
| EN | 26.8% | 7,211 | 7 | 2 |
| CC | 34.0% | 1,023 | 1 | 1 |
| AX | 34.2% | 3,852 | 7 | 0 |
| FQ | **46.7%** | 2,890 | 2 | 0 |

## FL is 100% Base-Only

All 4 Flow Operator classes use zero compound MIDDLEs:
- Class 7: 0% compound (434 tokens)
- Class 30: 0% compound (522 tokens)
- Class 38: 0% compound (50 tokens)
- Class 40: 0% compound (72 tokens)

FL uses 17 unique MIDDLEs, **none containing kernel characters (k, h, e)**.

## Kernel Character Distribution by Role

| Role | k-containing | h-containing | e-containing |
|------|--------------|--------------|--------------|
| FL | **0** | **0** | **0** |
| FQ | 0 | 0 | 5 |
| CC | 2 | 2 | 1 |
| AX | 4 | 8 | 10 |
| EN | 18 | 6 | 23 |

## CC Polarization

Core Control shows extreme polarization:
- Class 11 (`ol` only): 0% compound - base primitive
- Class 10 (`iin` only): 100% compound - derived form

## Structural Interpretation

```
FL (0.0%) ────── PRIMITIVE LAYER (flow control at atomic level)
EN (26.8%) ──── MIXED LAYER (both primitives and compounds)
CC (34.0%)
AX (34.2%)
FQ (46.7%) ──── COMPOUND-BIASED LAYER (highest derived usage)
```

FL operates entirely outside kernel character space, suggesting flow control is the most primitive operation.

## Implications

1. **FL is ground truth** - operates only with atomic MIDDLEs
2. **Role determines vocabulary type** - not random distribution
3. **Kernel operators excluded from FL** - flow control is pre-kernel
4. **FQ favors derived forms** - frequent operations use compound vocabulary

## Tier

**Tier 2** - Empirically validated structural relationship

## Source

- Phase: COMPOUND_MIDDLE_ARCHITECTURE
- Test: T7 (t7_role_compound_correlation.py)
- Data: 5 roles, 48 classes, 16,054 classified tokens
