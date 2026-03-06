# C1455: Quenching Modifier Partial i-Override

**Tier:** 2
**Scope:** B, MIDDLE, atom, i-modifier, quenching, co-occurrence, C1450, C1452
**Phase:** 524 (I_MODIFIER_HAZARD)
**Date:** 2026-03-05

## Claim

When i co-occurs with quenching modifiers {c,d,f,p,s} in the same MIDDLE, hazard drops from 22.6% (i-only) to 7.5% (both). Quenching dominates but does NOT reach zero as it does without i (quench-only = 5.9%). Co-occurrence is rare (N=40), making precise quantification uncertain. Neither modifier has 0% hazard baseline: i-only=22.6%, neither=28.0%.

## Evidence

### Four-group comparison

| Group | N | Hazard Rate |
|-------|---|-------------|
| Neither i nor quench | 17,309 | 28.0% |
| i only | 2,012 | 22.6% |
| Quench only | 3,735 | 5.9% |
| Both i + quench | 40 | 7.5% |

### Per-quencher co-occurrence

| Co-occurring | N | Hazard Rate |
|-------------|---|-------------|
| i+c | 12 | 0.0% |
| i+d | 10 | 20.0% |
| i+f | 7 | 0.0% |
| i+p | 10 | 10.0% |
| i+s | 8 | 0.0% |

### Effect ordering

Quenching effect: 28.0% -> 5.9% (reduction of 22.1pp)
i effect: 28.0% -> 22.6% (reduction of 5.4pp)
Combined: 28.0% -> 7.5% (reduction of 20.5pp)

Quenching dominates the combined effect. The residual 7.5% (vs 5.9% quench-only) may represent the i-modifier's frame-selection tendency toward FLOW-prone frames (C1453).

## Interpretation

The quenching mechanism (C1450) is the dominant hazard suppressor. When both i and a quenching modifier are present, quenching wins but with a small residual (~1.6pp above quench-only). This is consistent with C1453: i selects hazardous frames, and quenching modifiers suppress hazard within those frames but not quite as completely as in non-i frames. The N=40 sample limits confidence in the precise residual magnitude.

## Falsification Criteria

1. If co-occurrence hazard rate exceeds i-only rate (>22.6%)
2. If N increases above 100 and residual gap (co-occurrence minus quench-only) exceeds 10pp

## Method

- 23,096 tokens classified by presence of i-modifier and quenching modifiers {c,d,f,p,s}
- Four groups: neither, i-only, quench-only, both
- Per-quencher breakdown for co-occurrence tokens
- Hazard = FLOW + CONTAINMENT categories (C1280)

**Script:** `phases/I_MODIFIER_HAZARD/scripts/i_modifier_hazard.py`
**Results:** `phases/I_MODIFIER_HAZARD/results/i_modifier_hazard.json`

## Dependencies

- C1450 (Modifier quenching is categorical for c,d,f,p,s)
- C1452 (Non-monotonic i-extension hazard gradient)
- C1453 (i selects hazardous frames, not inherent hazard)
- C1280 (Hazard concentrates in FLOW/CONTAINMENT)
