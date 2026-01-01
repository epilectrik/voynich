# Family Coherence Analysis

## Question
Do folios within the same recipe family share similar control-signatures?

## Results

**Families Analyzed:** 8
**F-ratio:** 2.54
**Discriminability:** HIGH

### Intra-Family Variance
(Mean distance from family centroid)

- Family 1: 54.861
- Family 2: 491.845
- Family 3: 326.255
- Family 4: 128.249
- Family 5: 190.632
- Family 6: 0.0
- Family 7: 0.0
- Family 8: 78.819

**Mean Intra-Family Variance:** 158.833
**Inter-Family Variance:** 403.467

### Best Discriminating Dimensions

1. **total_length**: variance = 88667.483
1. **hazard_adjacency_count**: variance = 34063.912
1. **cycle_count**: variance = 1555.716
1. **near_miss_count**: variance = 52.448
1. **recovery_ops_count**: variance = 43.404

## Interpretation

Families are **control-coherent** - signature similarity within families exceeds similarity between families. Recipe families represent distinct operational programs.