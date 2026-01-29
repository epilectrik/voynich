# C803: Body HT Boundary Enrichment

## Constraint

Body HT is enriched at line boundaries. HT rates by position:
- First token: 45.8%
- Last token: 42.9%
- Middle tokens: 25.7%

First vs middle: chi2 = 236.9, p < 0.0001
Last vs middle: chi2 = 177.6, p < 0.0001

## Evidence

Position distribution (normalized 0-1):
| Bin | HT% | Non-HT% |
|-----|-----|---------|
| 0.0-0.2 | 27.9% | 18.6% |
| 0.2-0.4 | 18.9% | 20.2% |
| 0.4-0.6 | 16.8% | 20.1% |
| 0.6-0.8 | 16.3% | 20.6% |
| 0.8-1.0 | 20.1% | 20.5% |

Mean position: HT = 0.493, non-HT = 0.503 (slight early bias, p = 0.032)

## Interpretation

HT marks line boundaries (control block boundaries per C360). Combined with LINK proximity (C802), HT appears at structural junctions where monitoring occurs - both at line edges and near LINK operators within lines.

## Provenance

- Phase: PP_HT_AZC_INTERACTION
- Script: t7_body_ht_positions.py
- Dependencies: C360, C802

## Tier

2 (Validated Finding)
