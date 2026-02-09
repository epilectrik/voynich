# C921: f57v R2 Twelve-Character Period

## Status
- **Tier**: 2 (STRUCTURAL)
- **Scope**: AZC
- **Status**: CLOSED
- **Source**: Phase A_PURPOSE_INVESTIGATION

## Statement

f57v R2 exhibits an exact 12-character repeating period with 4 complete cycles plus a 2-character terminal. 10 of 12 positions (83%) are invariant across all cycles; only positions 7 and 8 carry variation.

## Evidence

### Sequence Analysis

Full R2 sequence (50 chars, asterisks removed):
```
oldrxkkftryc oldrxkmftryc oldrxkkptryc oldrxkkptryc rn
```

### Period Structure

| Cycle | Sequence | Pos 7 | Pos 8 |
|-------|----------|-------|-------|
| 1 | oldrxkkftryc | k | f |
| 2 | oldrxkmftryc | m | f |
| 3 | oldrxkkptryc | k | p |
| 4 | oldrxkkptryc | k | p |
| Terminal | rn | - | - |

### Position-by-Position Invariance

| Position | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 |
|----------|---|---|---|---|---|---|---|---|---|----|----|-----|
| Char | o | l | d | r | x | k | ? | ? | t | r | y | c |
| Status | INV | INV | INV | INV | INV | INV | VAR | VAR | INV | INV | INV | INV |

- **Invariant positions**: 10/12 (83%)
- **Variable positions**: 2/12 (17%) - positions 7 and 8 only
- **Position 7 values**: k, m
- **Position 8 values**: f, p

### Variation Pattern

| Cycle | Pos 7 | Pos 8 | Interpretation |
|-------|-------|-------|----------------|
| 1 | k | f | k-f combination |
| 2 | m | f | m-f combination |
| 3-4 | k | p | k-p combination (repeated) |

## Interpretation

The 12-character period on a zodiac folio is structurally consistent with a 12-month or 12-zodiac-sign reference. The high invariance (83%) with only 2 variable positions suggests a formula template rather than arbitrary content.

**Note**: The 12-month semantic interpretation is Tier 4 speculation. This constraint documents only the structural finding.

## Related Constraints

| Constraint | Relationship |
|------------|--------------|
| C763 | f57v R2 is 100% single-character tokens |
| C764 | f57v coordinate system, 'x' as coord marker |
| C920 | f57v R2 = 92% extension vocabulary |
| C922 | Single-char AZC rings exclude h |

## Falsification Criteria

Disproven if:
1. Alternative period analysis shows different structure
2. The 12-char period is an artifact of transcription errors
3. Variation positions are more numerous than documented
