# C684: Hazard Pruning Under Filtering

**Status:** VALIDATED | **Tier:** 2 | **Phase:** A_RECORD_B_FILTERING | **Scope:** A-B

## Finding

A-record filtering **eliminates all 17 forbidden transitions** in 83.9% of records. Filtering is a natural hazard suppression mechanism: by restricting the B vocabulary, most records remove the specific token pairs that constitute hazard transitions. The remaining 16.1% retain a mean of only 1.3 active transitions (max 5).

## Key Numbers

| Metric | Value |
|--------|-------|
| Forbidden transitions (unfiltered) | 17 |
| Full elimination (0/17 active) | 1,311 / 1,562 (83.9%) |
| Mean active per record | 0.21 |
| Median active | 0.0 |
| Max active | 5 |

### Distribution of Active Forbidden Transitions

| Active | Records | % |
|--------|---------|---|
| 0 | 1,311 | 83.9% |
| 1 | 194 | 12.4% |
| 2 | 45 | 2.9% |
| 3 | 9 | 0.6% |
| 4 | 2 | 0.1% |
| 5 | 1 | 0.1% |

## Interpretation

Hazard elimination is a **side effect** of vocabulary restriction, not a design goal. The 17 forbidden pairs (Phase 18A) involve specific tokens; when filtering removes either the source or target, the transition becomes impossible. This means A records that admit more B tokens also retain more hazard exposure — a tradeoff between program richness and hazard risk.

## Provenance

- Script: `phases/A_RECORD_B_FILTERING/scripts/survivor_population_profile.py` (Test 3)
- Data: `phases/15-20_kernel_grammar/phase18a_forbidden_inventory.json`
- Extends: C109-C114 (forbidden transitions), C682 (filtering profile)
