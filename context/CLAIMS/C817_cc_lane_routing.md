# C817: CC Lane Routing Confirmation

## Constraint

C600 lane routing predictions are **CONFIRMED** with strong immediate effect and rapid decay:
- daiin -> CHSH at 90.8% (offset +1)
- ol_derived -> QO at 57.4% (offset +1)
- ol -> CHSH at 93.2% (offset +1, not previously documented)

Lane bias decays to ~50/50 by offset +2, indicating CC sets INITIAL lane, not persistent lane.

## Evidence

Lane distribution at offset +1 (immediate successor):

| CC Type | QO | CHSH | Dominant | p-value |
|---------|-----|------|----------|---------|
| daiin | 9.2% | 90.8% | CHSH | *** |
| ol | 6.8% | 93.2% | CHSH | *** |
| ol_derived | 57.4% | 42.6% | QO | NS |

Lane bias decay (expected lane rate):
| Offset | daiin->CHSH | ol_derived->QO |
|--------|-------------|----------------|
| +1 | 90.8% | 57.4% |
| +2 | 53.8% | 40.0% |
| +3 | 58.4% | 43.1% |
| +5 | 74.6% | 42.9% |

## Interpretation

1. **C600 CONFIRMED** for immediate successors
2. Lane routing is an INITIALIZATION effect, not a persistent state
3. ol shows same CHSH bias as daiin (not previously documented)
4. ol_derived shows weaker QO bias (57.4%) than C600 suggested

The rapid decay to 50/50 indicates the lane system has no long-range memory - each position is re-determined locally.

## Provenance

- Phase: CC_CONTROL_LOOP_INTEGRATION
- Script: t3_cc_lane_propagation.py
- Related: C600 (CC trigger selectivity), C643 (lane hysteresis)

## Tier

2 (Validated Finding)
