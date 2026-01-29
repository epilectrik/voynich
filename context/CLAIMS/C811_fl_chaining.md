# C811: FL Chaining (Extended Escape Sequences)

## Constraint

FL→FL transitions are enriched at 2.11x baseline, indicating extended escape sequences rather than single-token recovery events.

- FL follows FL: 9.9% (baseline 4.7%)
- Enrichment: 2.11x
- FL→KERNEL: 59.4% (baseline 69.1%, 0.86x) - neutral loop closure

## Evidence

What follows FL tokens:
| Role | Count | Percentage | Enrichment |
|------|-------|------------|------------|
| HT | 257 | 28.8% | — |
| ENERGY_OPERATOR | 224 | 25.1% | — |
| AUXILIARY | 149 | 16.7% | — |
| FREQUENT_OPERATOR | 143 | 16.0% | — |
| FLOW_OPERATOR | 88 | 9.9% | 2.11x |
| CORE_CONTROL | 31 | 3.5% | — |

Kernel type distribution after FL:
- 'h' follows FL: 38.6%
- 'e' follows FL: 37.7%
- 'k' follows FL: 23.7%

## Interpretation

Escape is not a single-token event. FL tokens chain together (2.11x enrichment), suggesting multi-step recovery sequences. The loop closure to KERNEL is neutral (0.86x), meaning FL returns to processing at baseline rates - the loop is neither strongly closed nor strongly open.

## Provenance

- Phase: CONTROL_LOOP_SYNTHESIS
- Script: t2_loop_closure.py
- Related: C770-C777

## Tier

2 (Validated Finding)
