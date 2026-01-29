# C810: LINK-FL Non-Adjacency

## Constraint

Direct LINK→FL transitions are rare, confirming LINK and FL are complementary (non-adjacent) phases:

- LINK precedes FL: 8.9% (baseline 13.2%, enrichment 0.67x)
- FL follows LINK: 3.3% (baseline 4.7%, enrichment 0.70x)
- Direct LINK→FL: 88 observed vs 125 expected (0.70x)

## Evidence

What precedes FL tokens:
| Role | Count | Percentage |
|------|-------|------------|
| HT | 270 | 27.2% |
| ENERGY_OPERATOR | 256 | 25.8% |
| AUXILIARY | 176 | 17.7% |
| FREQUENT_OPERATOR | 167 | 16.8% |
| FLOW_OPERATOR | 88 | 8.9% |
| CORE_CONTROL | 37 | 3.7% |

What follows LINK tokens:
| Role | Count | Percentage |
|------|-------|------------|
| ENERGY_OPERATOR | 979 | 36.6% |
| HT | 688 | 25.7% |
| AUXILIARY | 526 | 19.6% |
| FREQUENT_OPERATOR | 309 | 11.5% |
| FLOW_OPERATOR | 88 | 3.3% |
| CORE_CONTROL | 87 | 3.2% |

## Interpretation

LINK (monitoring) and FL (escape) do not directly transition. There is typically an intervening phase (KERNEL processing or other operations) between monitoring and escape. This confirms C807's inverse relationship finding and supports the three-phase control model.

## Provenance

- Phase: CONTROL_LOOP_SYNTHESIS
- Script: t1_link_fl_interface.py
- Related: C807

## Tier

2 (Validated Finding)
