# C653: AZC Lane Filtering Bias

**Tier:** 2 | **Status:** CLOSED | **Scope:** GLOBAL

## Finding

AZC-Mediated PP MIDDLEs are significantly more CHSH-biased than B-Native PP MIDDLEs. At type level, AZC-Med has 19.7% QO vs B-Native 33.7% QO (chi2=5.15, p=0.023, V=0.158, OR=0.48). At token level (B-frequency weighted), AZC-Med has 30.6% QO vs B-Native 48.2% QO (chi2=76.0, p < 1e-17, OR=0.47). The pipeline pathway (A->AZC->B) selectively retains CHSH-predicting vocabulary relative to B-native vocabulary.

## Evidence

- 235 AZC-Mediated PP: 27 QO, 110 CHSH (19.7% QO) at type level
- 169 B-Native PP: 33 QO, 65 CHSH (33.7% QO) at type level
- Type-level: chi2(Yates)=5.149, p=0.023, V=0.158
- Odds ratio=0.483 [0.267, 0.876] — AZC-Med about half as likely to be QO
- Token-level: AZC-Med 3694 QO / 8393 CHSH (30.6%); B-Native 268 QO / 288 CHSH (48.2%)
- Token-level: chi2=76.05, p < 1e-17, V=0.078, OR=0.473 [0.399, 0.561]
- Both type-level and token-level converge: AZC filtering is asymmetric

## Interpretation

The AZC pipeline pathway differentially retains CHSH-predicting PP vocabulary. AZC-Mediated MIDDLEs (those appearing in AZC folios and propagating A->AZC->B) are approximately half as likely to be QO-predicting as B-Native MIDDLEs (those present in B without AZC presence). This means the pipeline, as a filter, actively amplifies the CHSH bias already present in PP vocabulary (C652). However, this structural asymmetry does not functionally determine B-side lane balance (C654, C655).

## Cross-References

- C652: PP vocabulary is inherently CHSH-biased (25.5% QO)
- C498.a: AZC-Mediated vs B-Native PP partition (235/169)
- C640: AZC-Med frequency confound (median 9 vs 2) — both type and token levels tested to control
- C654: Non-EN PP does not predict lane balance despite asymmetry
- C655: PP adds zero incremental prediction beyond section/REGIME

## Provenance

PP_LANE_PIPELINE, Script 1 (pp_lane_vocabulary_architecture.py), Test 2
