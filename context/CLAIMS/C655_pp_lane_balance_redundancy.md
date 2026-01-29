# C655: PP Lane Balance Redundancy

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

## Finding

PP character composition adds zero predictive power for B-folio lane balance beyond section and REGIME. Null model (section + REGIME dummies): R2=0.366. Adding non-EN PP QO fraction: incremental R2=0.0005 (F=0.058, p=0.81). AZC-Med PP adds nothing (incr R2=0.000, p=0.97). B-Native PP adds nothing (incr R2=0.004, p=0.51). A-record PP character distribution diverges sharply from B-side lane balance (KS D=0.554, p < 1e-10).

## Evidence

- 81 B folios in regression (5 section levels, 4 REGIME levels, 7 null predictors)
- Null model R2=0.3658 (section + REGIME explain 36.6% of lane balance variance)
- Combined PP model: R2=0.3663, incremental R2=0.0005
  - F-test: F=0.058, p=0.8110, df=(1,72)
- AZC-Med only: R2=0.3659, incremental R2=0.0000, F=0.002, p=0.9659
- B-Native only: R2=0.3755, incremental R2=0.0042, F=0.435, p=0.5117
- No pathway differential: AZC-Med and B-Native both add nothing
- A-record distribution vs B-folio:
  - A-record PP QO fraction: mean=0.187, median=0.000
  - B-folio EN lane balance: mean=0.407, median=0.412
  - KS D=0.5538, p < 1e-10 — distributions completely divergent
  - Within Herbal: KS D=0.5373, p < 1e-10 — same divergence

## Interpretation

Section and REGIME fully account for inter-folio lane balance variation. PP vocabulary composition — whether measured by character content, AZC pathway, or B-Native content — contributes nothing beyond these structural factors. The pipeline carries vocabulary with lane-structured characters (C652, C653), but this structure is irrelevant to execution-level lane selection. Lane balance is determined by B-internal grammar, not by upstream vocabulary composition. The A-side prediction of ~18.7% QO vs the observed ~40.7% QO demonstrates that the grammar actively compensates, selecting QO MIDDLEs at rates far exceeding their vocabulary presence.

## Cross-References

- C650: Section-driven oscillation rate (section partial eta2=0.174)
- C652: PP vocabulary CHSH-biased (25.5% QO at type level)
- C653: AZC amplifies CHSH bias (OR=0.48)
- C654: Non-EN PP does not predict lane (partial r=0.028)
- C506: PP composition doesn't propagate to B classes (cosine=0.995) — extended to lane balance
- C384: No entry-level A-B coupling — consistent

## Provenance

PP_LANE_PIPELINE, Script 2 (pp_pipeline_lane_prediction.py), Tests 5-6
