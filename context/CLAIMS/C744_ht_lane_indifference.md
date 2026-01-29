# C744: HT Lane Indifference

**Tier:** 2
**Phase:** HT_RECONCILIATION
**Test:** T5
**Scope:** B

## Statement

When HT tokens are adjacent to classified tokens within B lines, they show no preference for same-lane placement. The observed same-lane rate (37.7%) matches the marginal independence expectation (37.9%) with a lift of 0.994x. Permutation test: z=-1.66, p=0.053 (not significant).

## Evidence

| Metric | Value |
|--------|-------|
| Adjacent HT-Classified pairs (both with prefix) | 5,508 |
| Same lane | 2,074 (37.7%) |
| Expected under independence | 37.9% |
| Lift | 0.994x |
| HT->CL same-lane | 38.6% |
| CL->HT same-lane | 36.7% |

### Permutation (1000 shuffles)

| Metric | Value |
|--------|-------|
| Observed same | 2,074 |
| Null mean | 2,126.1 |
| Null std | 31.43 |
| Z-score | -1.66 |
| P(more same) | 0.952 |

## Interpretation

HT tokens are lane-neutral in their line-level placement. They neither seek nor avoid the lane of their classified neighbors. This is consistent with C404-C405 (HT non-operational) and supports the interpretation that HT tokens do not participate in lane-level control logic.

Note: This test uses sequential adjacency, which is constrained by C234 (POSITION_FREE). The finding is descriptive of lane membership, not positional grammar.

## Provenance

- Phase: HT_RECONCILIATION/results/ht_lane_participation.json
- Script: ht_lane_participation.py
- Related: C404-C405 (HT non-operational), C234 (position-free), C643-C654 (lane architecture)
