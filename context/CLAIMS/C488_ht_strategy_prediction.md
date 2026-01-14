# C488: HT Predicts Strategy Viability

**Tier:** 3 | **Status:** CLOSED | **Scope:** HUMAN_TRACK

## Statement

HT density strongly predicts which operator strategies are viable for a given B program. High-HT programs require cautious strategies; low-HT programs tolerate aggressive approaches.

## Evidence

### HT-Strategy Correlations

| Strategy | r with HT | p-value | Interpretation |
|----------|-----------|---------|----------------|
| CAUTIOUS | +0.459 | <0.0001 | High HT favors cautious |
| AGGRESSIVE | -0.432 | <0.0001 | High HT rejects aggressive |
| OPPORTUNISTIC | -0.481 | <0.0001 | High HT rejects opportunistic |

All correlations highly significant (p < 0.0001).

### Strategy Definitions

| Strategy | Description | Requirements |
|----------|-------------|--------------|
| CAUTIOUS | High intervention, frequent stabilizing | High link density, high intervention, low qo |
| AGGRESSIVE | Minimal intervention, fast throughput | Low link density, low intervention, high hazard |
| OPPORTUNISTIC | Escape-heavy, adaptive | High qo density, high recovery ops |

### Archetype-Strategy Matrix

| Archetype | n | CAUTIOUS | AGGRESSIVE | OPPORTUNISTIC |
|-----------|---|----------|------------|---------------|
| AGGRESSIVE_INTERVENTION | 6 | 0.17 (poor) | 0.67 (viable) | 0.67 (viable) |
| CONSERVATIVE_WAITING | 17 | 0.45 (poor) | 0.00 (poor) | 0.21 (poor) |
| ENERGY_INTENSIVE | 10 | 0.03 (poor) | 0.63 (viable) | 0.80 (viable) |
| MIXED | 50 | 0.39 (poor) | 0.36 (poor) | 0.29 (poor) |

## Interpretation

### What HT Tracks

HT density is not just "attention needed" - it specifically predicts **operational load profile**:

| HT Level | Implication | Strategy Fit |
|----------|-------------|--------------|
| High HT | Complex material handling, many decisions | CAUTIOUS only |
| Low HT | Simpler handling, fewer decision points | AGGRESSIVE/OPPORTUNISTIC viable |

### CONSERVATIVE_WAITING Programs

The 17 CONSERVATIVE_WAITING programs (high link density, high intervention) don't fit ANY named strategy well. They require **bespoke intervention profiles** - pre-defined strategies don't capture their complexity.

This is not a failure of the taxonomy - it's a finding: some programs are genuinely more complex than simple strategies can describe.

### Integration with HT Model

This extends the HT interpretive model:

| HT Property | What It Tracks | Evidence |
|-------------|---------------|----------|
| Density | Upcoming complexity (C477) | Tail pressure correlation |
| Morphology | Spare capacity | Inverse complexity correlation |
| **Strategy** | **Viable intervention modes** | **This constraint** |

## Related Constraints

- C477: HT tail correlation
- C459: HT anticipatory vigilance
- C458: Design freedom asymmetry

## Source

Phase: SEMANTIC_CEILING_EXTENSION
Test: 4A (operator_strategies.py)
Results: `results/operator_strategies.json`
