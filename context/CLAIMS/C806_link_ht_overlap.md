# C806: LINK-HT Positive Association

## Constraint

LINK and HT are positively associated:
- Odds ratio: 1.50 (p < 0.001)
- Observed LINK+HT: 1,168 tokens
- Expected under independence: 929 tokens
- Ratio: 1.26x excess

HT vocabulary contains 'ol' at 16.6% vs 11.7% in classified vocabulary.

## Evidence

Contingency table:
|          | HT     | Non-HT | Total  |
|----------|--------|--------|--------|
| LINK     | 1,168  | 1,879  | 3,047  |
| Non-LINK | 5,874  | 14,175 | 20,049 |
| Total    | 7,042  | 16,054 | 23,096 |

Fisher's exact: OR=1.50, p < 0.001
Chi-square: chi2=101.4, p < 0.001

38.3% of LINK tokens are HT.
16.6% of HT tokens are LINK.

## Interpretation

The LINK-HT overlap is real but moderate (OR=1.50). It's driven by vocabulary composition: HT vocabulary disproportionately contains 'ol' as a morphological component. This explains why LINK and HT share boundary enrichment patterns (C803, C805).

## Provenance

- Phase: LINK_OPERATOR_ARCHITECTURE
- Script: t3_link_ht_cooccurrence.py
- Related: C802, C803, C805

## Tier

2 (Validated Finding)
