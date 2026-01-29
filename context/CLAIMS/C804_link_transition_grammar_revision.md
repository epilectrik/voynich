# C804: LINK Transition Grammar Revision

## Constraint

C366's transition grammar claims are NOT reproducible with current role taxonomy:

| C366 Claim | Actual | Verdict |
|------------|--------|---------|
| Preceded by AUXILIARY 1.50x | 1.03x | **NOT CONFIRMED** |
| Preceded by FLOW_OPERATOR 1.30x | 0.91x | **NOT CONFIRMED** |
| Followed by HIGH_IMPACT 2.70x | 1.16x (AX) | **WEAK** |
| Followed by ENERGY_OPERATOR 1.15x | 1.10x | **MARGINAL** |

Statistical tests:
- Predecessor distribution: chi2=5.1, p=0.41 (NOT significant)
- Successor distribution: chi2=48.2, p<0.001 (significant but weak)

## Evidence

LINK predecessor distribution matches baseline within noise:
- AUXILIARY: 18.3% vs 17.7% baseline (1.03x)
- ENERGY_OPERATOR: 33.9% vs 33.1% baseline (1.02x)
- FLOW_OPERATOR: 3.9% vs 4.3% baseline (0.91x)

LINK successor shows modest AUXILIARY enrichment:
- AUXILIARY: 19.6% vs 16.9% baseline (1.16x)
- ENERGY_OPERATOR: 36.6% vs 33.3% baseline (1.10x)

## Interpretation

C366's specific enrichment ratios (1.50x, 1.30x, 2.70x) were likely computed with a different role taxonomy or methodology. The current 5-role ICC system (CC, EN, FL, FQ, AX) shows no strong predecessor bias and only weak successor bias.

The qualitative claim that "LINK marks boundary between monitoring and intervention" may still hold, but the quantitative transition grammar requires revision.

## Provenance

- Phase: LINK_OPERATOR_ARCHITECTURE
- Script: t1_link_transition_grammar.py
- Revises: C366

## Tier

2 (Validated Finding)
