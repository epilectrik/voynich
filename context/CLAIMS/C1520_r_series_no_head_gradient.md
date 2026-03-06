# C1520: R-Series No HEAD Gradient

**Tier:** 2
**Scope:** AZC, R-series, HEAD, gradient, null, R4, C434
**Phase:** AZC_ZONE_ATOMIZATION (Phase 541)

## Claim

The R-series ordered subscripts (R1, R2, R3, R4) show NO significant HEAD gradient. Spearman correlations for all HEAD categories are non-significant (all p=0.600, N=4 positions). R1-R3 are HEAD-stable with pairwise JSD 0.001-0.009. R4 is anomalous: N=39 tokens, 51.3% headless (vs R1-R3 ~24-27%), e-HEAD collapsed to 10.3% (vs R1-R3 ~35-38%), HEAD JSD ~0.10 from other R positions. The R4 anomaly is likely a small-sample artifact (39 tokens vs 205-462 for R1-R3). The R-series forward ordering (C434) does NOT correspond to a progressive shift in HEAD domain composition. Whatever the R-series orders, it is not a domain progression.

## Evidence

- HEAD profiles across R-series:
  - R1 (N=462): a=18.4%, e=37.9%, o=16.7%, k=1.9%, t=0.9%, headless=24.2%
  - R2 (N=386): a=15.0%, e=35.0%, o=18.1%, k=2.1%, t=2.8%, headless=26.9%
  - R3 (N=205): a=18.0%, e=38.0%, o=18.0%, k=1.5%, t=0.5%, headless=23.9%
  - R4 (N=39): a=17.9%, e=10.3%, o=15.4%, k=2.6%, t=2.6%, headless=51.3%
- Spearman correlations (positions 1-4):
  - o: rho=-0.400, p=0.600
  - e: rho=-0.400, p=0.600
  - k: rho=+0.400, p=0.600
  - headless: rho=+0.400, p=0.600
- Pairwise HEAD JSD: R1-R2=0.006, R1-R3=0.001, R2-R3=0.009 (stable); R1-R4=0.100, R2-R4=0.081, R3-R4=0.106 (R4 divergent)

## Relationship to Prior Constraints

- **Extends C434**: R-series strict forward ordering is NOT reflected in HEAD domain progression
- **Extends C1271**: Null atom differentiation extends to R-series specifically at HEAD level
- **Extends C1516**: Zone HEAD differentiation is BETWEEN zones (R vs C vs S vs P), NOT within R-series subscripts
- **Note on R4**: N=39 makes any profile unstable; the anomaly should be treated as underpowered, not as evidence of R4 distinctiveness

## Source

`phases/AZC_ZONE_ATOMIZATION/results/azc_zone_atomization.json` (T7)
