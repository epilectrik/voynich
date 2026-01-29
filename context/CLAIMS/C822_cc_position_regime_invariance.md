# C822: CC Position REGIME Invariance

## Constraint

Despite REGIME_3 showing 1.83x CC enrichment (C545), CC positional behavior is **INVARIANT across REGIMEs**:
- daiin initial-bias: 22.7% - 33.9% (chi2=1.62, p=0.65 NS)
- daiin mean position: 0.38 - 0.45 (H=1.51, p=0.68 NS)
- ol mean position: 0.50 - 0.57 (H=2.06, p=0.56 NS)

REGIME affects CC FREQUENCY, not CC PLACEMENT.

## Evidence

### daiin Initial-Bias by REGIME

| REGIME | First Position | Rate |
|--------|---------------|------|
| REGIME_1 | 40/155 | 25.8% |
| REGIME_2 | 11/37 | 29.7% |
| REGIME_3 | 19/56 | 33.9% |
| REGIME_4 | 15/66 | 22.7% |

Chi-squared: 1.62, p=0.65 (NS)

### daiin Mean Position by REGIME

| REGIME | Mean | Std | n |
|--------|------|-----|---|
| REGIME_1 | 0.415 | 0.343 | 155 |
| REGIME_2 | 0.384 | 0.355 | 37 |
| REGIME_3 | 0.384 | 0.345 | 56 |
| REGIME_4 | 0.448 | 0.349 | 66 |

Kruskal-Wallis: H=1.51, p=0.68 (NS)

## Interpretation

C545 shows REGIME_3 is "Control without output" with 1.83x CC enrichment.
But this enrichment is achieved by using MORE CC tokens, not by MOVING CC tokens to different positions.

The control loop initiation pattern (daiin -> LINK -> KERNEL -> ol -> FL per C816) operates identically regardless of REGIME.

## Provenance

- Phase: REGIME_LINE_SYNTAX_INTERACTION
- Script: t1_cc_position_by_regime.py
- Related: C816 (CC positional ordering), C545 (REGIME class profiles)

## Tier

2 (Validated Finding)
