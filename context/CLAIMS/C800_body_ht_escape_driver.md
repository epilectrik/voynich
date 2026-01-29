# C800: Body HT Escape Driver

## Constraint

Body HT (lines 2+) drives the HT-escape correlation (C796). Line-1 HT is independent of escape rate.

## Evidence

Spearman correlations with folio FL%:
- Body HT vs FL%: rho = 0.367, p = 0.0007
- Line-1 HT vs FL%: rho = 0.107, p = 0.35

Correlation difference test: z = 1.88, p = 0.06

## Interpretation

Line-1 HT serves the header/declaration function (C794-C795) and operates independently of body execution intensity. Body HT tracks operational complexity and escape activity.

## Provenance

- Phase: PP_HT_AZC_INTERACTION
- Script: t5_body_ht_escape.py
- Dependencies: C796, C794, C795

## Tier

2 (Validated Finding)
