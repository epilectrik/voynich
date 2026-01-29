# C654: Non-EN PP Lane Independence

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

## Finding

Non-EN PP vocabulary composition on B folios does not predict EN lane balance. Bivariate Spearman rho=0.108 (p=0.34); partial correlation controlling section and REGIME: r=0.028 (p=0.80). Sensitivity analysis including EN tokens (tautological): rho=0.678, partial r=0.645 (p < 1e-10). Lane identity is embedded in EN tokens via PREFIX->MIDDLE binding, not transmitted from the surrounding vocabulary landscape.

## Evidence

- 81 B folios with >= 10 EN tokens and >= 5 non-EN lane-predicting PP tokens
- Predictor: QO-character fraction of non-EN PP MIDDLEs (AX, CC, FL, FQ tokens)
- Outcome: EN lane balance (QO fraction of EN tokens)
- Bivariate: Spearman rho=0.1075, p=0.3396
- Partial (section + REGIME, 5 + 4 levels): r=0.0283, p=0.8022
- Tautological sensitivity (including EN tokens in predictor):
  - Spearman rho=0.6778, p < 1e-10
  - Partial r=0.6452, p < 1e-10
- Tautological inflation: 22.7x increase in effect size (0.028 -> 0.645)
- A-side predicted QO fraction: mean=0.187, but B-side observed: mean=0.407 (2.2x amplification)

## Interpretation

The vocabulary landscape surrounding EN tokens does not independently predict lane selection. EN tokens carry their own lane identity through PREFIX->MIDDLE binding (C649, C647). When EN tokens are excluded from the predictor, the correlation drops to near-zero. This means lane is not a folio-level property that pervades all vocabulary — it is an EN-specific property determined at the moment of token selection. The PP pipeline shapes vocabulary availability (C652, C653) but the grammar compensates, selecting QO MIDDLEs at 2.2x the rate their vocabulary presence would predict.

## Cross-References

- C649: EN-exclusive MIDDLE deterministic lane partition
- C647: QO=70.7% k-MIDDLE, CHSH=68.7% e-MIDDLE (massive effect, V=0.654)
- C652: PP vocabulary is CHSH-biased (25.5% QO)
- C653: AZC amplifies CHSH bias (OR=0.48)
- C655: PP adds zero incremental prediction (F=0.058, p=0.81)
- C522: Construction-execution independence (consistent: vocabulary character ≠ execution behavior)
- C506: PP composition doesn't propagate (cosine=0.995) — extended to lane balance

## Provenance

PP_LANE_PIPELINE, Script 2 (pp_pipeline_lane_prediction.py), Tests 4-6
