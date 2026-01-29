# C819: CC Boundary Asymmetry

## Constraint

CC subtypes show **asymmetric boundary behavior**, unlike LINK's uniform enrichment:
- **daiin**: Strongly initial-biased (27.1% first vs 10.4% baseline, 1.66x enrichment)
- **ol/ol_derived**: Middle-concentrated (85% middle, boundary-depleted 0.69-0.75x)
- **CC overall**: No net boundary effect (1.01x, NS)

This differs from LINK (1.23x boundary enrichment, C805).

## Evidence

Position distributions:

| Category | First | Middle | Last | Boundary Enrichment | p-value |
|----------|-------|--------|------|---------------------|---------|
| Baseline | 10.4% | 79.1% | 10.4% | 1.00x | - |
| CC (all) | 12.1% | 79.0% | 8.9% | 1.01x | NS |
| LINK | 13.6% | 74.3% | 12.1% | 1.23x | *** |
| daiin | 27.1% | 65.3% | 7.6% | 1.66x | *** |
| ol | 5.0% | 85.5% | 9.5% | 0.69x | *** |
| ol_derived | 6.2% | 84.4% | 9.4% | 0.75x | * |

## Interpretation

CC subtypes partition positional space:
1. **daiin** occupies line-initial SETUP position (triggers ENERGY per C557)
2. **ol/ol_derived** occupy medial WORK/CHECK positions
3. This confirms C590 (CC positional dichotomy) with quantified rates

The net CC effect (1.01x) is a cancellation: daiin's initial bias balanced by ol's middle concentration.

## Provenance

- Phase: CC_CONTROL_LOOP_INTEGRATION
- Script: t5_cc_boundary_behavior.py
- Related: C805 (LINK boundary enrichment), C590 (CC positional dichotomy)

## Tier

2 (Validated Finding)
