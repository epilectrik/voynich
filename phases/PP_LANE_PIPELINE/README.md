# PP_LANE_PIPELINE Phase

**Status:** COMPLETE | **Constraints:** C652-C655 | **Tier:** 2

## Question

Does PP vocabulary composition shape B-side lane balance through the A->AZC->B pipeline?

## Answer

**No.** PP vocabulary carries lane-structured character composition (74.5% CHSH-predicting), and AZC filtering amplifies this bias (OR=0.48), but this structure has no functional consequence for execution-level lane selection. Non-EN PP composition does not predict EN lane balance (partial r=0.028, p=0.80), and PP adds zero incremental prediction beyond section and REGIME (incr R2=0.0005, p=0.81).

Lane identity is embedded in EN tokens via PREFIX->MIDDLE binding, not transmitted from the vocabulary landscape. The grammar compensates for vocabulary bias, selecting QO MIDDLEs at 2.2x the rate their PP presence would predict.

## Scripts

| Script | Tests | Verdict |
|--------|-------|---------|
| pp_lane_vocabulary_architecture.py | 1-3 | CHSH_BIASED, AZC_ASYMMETRIC, PATHWAY_UNIFORM |
| pp_pipeline_lane_prediction.py | 4-6 | NULL, DIVERGENT, PP_REDUNDANT |

## Findings

### Test 1: PP Character Census (C652)
PP vocabulary (404 MIDDLEs) classified by C649 initial character rule:
- **QO-predicting** (k/t/p): 60 types, 3962 tokens
- **CHSH-predicting** (e/o): 175 types, 8681 tokens
- **Neutral** (other): 169 types, 8999 tokens
- QO fraction: **25.5% type, 31.3% token** (binomial p < 3e-14)
- Material class: no modulation (chi2=2.4, p=0.49)

### Test 2: AZC Lane Filtering Asymmetry (C653)
Pipeline differentially retains CHSH vocabulary:
- **AZC-Med**: 19.7% QO (type), 30.6% QO (token)
- **B-Native**: 33.7% QO (type), 48.2% QO (token)
- Type: chi2=5.15, p=0.023, OR=0.48 [0.27, 0.88]
- Token: chi2=76.0, p < 1e-17, OR=0.47 [0.40, 0.56]

### Test 3: Discriminator Pathway Analysis
20 C646 discriminators: 17 AZC-Med (12 QO, 5 CHSH), 3 B-Native (3 QO, 0 CHSH).
- Fisher's exact: NS (p=0.54)
- Mean |r|: AZC-Med 0.126 vs B-Native 0.136 (MW p=0.62)
- All tested PP: B-Native mean |r|=0.095 vs AZC-Med 0.045 (MW p=0.099, marginal)

### Test 4: Non-EN PP -> EN Lane Balance (C654)
Non-tautological test (predictor excludes EN tokens):
- Bivariate: rho=0.108, p=0.34
- **Partial (section+REGIME): r=0.028, p=0.80** -- NULL
- Tautological sensitivity (includes EN): rho=0.678, partial r=0.645 -- massive
- Inflation factor: 22.7x (proves EN tokens carry the signal, not surrounding vocabulary)

### Test 5: A-Record Distribution vs B-Folio Balance (C655)
A-side PP predicts far less QO than B-side shows:
- A-record mean PP QO fraction: **0.187** (median=0.000)
- B-folio mean EN lane balance: **0.407** (median=0.412)
- KS D=0.554, p < 1e-10 -- completely divergent
- Within Herbal: same pattern (KS D=0.537, p < 1e-10)
- **Grammar compensates: 2.2x QO amplification** over vocabulary baseline

### Test 6: Incremental R-squared (C655)
PP adds nothing beyond section+REGIME:
- Null R2=0.366 (section + REGIME)
- +PP: R2=0.366, incr=0.0005, F=0.058, **p=0.81**
- +AZC-Med PP: incr=0.000, p=0.97
- +B-Native PP: incr=0.004, p=0.51

## Constraints Produced

| ID | Name | Finding |
|----|------|---------|
| C652 | PP Lane Character Asymmetry | 25.5% QO at type level (p < 3e-14) |
| C653 | AZC Lane Filtering Bias | AZC-Med 19.7% vs B-Native 33.7% QO (OR=0.48, p=0.023) |
| C654 | Non-EN PP Lane Independence | Partial r=0.028, p=0.80 (null) |
| C655 | PP Lane Balance Redundancy | Incremental R2=0.0005, F=0.058, p=0.81 |

## Structural Conclusion

The PP->Lane pipeline has architecture without function:
1. PP vocabulary IS lane-structured (C652) -- 3:1 CHSH bias
2. AZC filtering DOES amplify this bias (C653) -- OR=0.48
3. But this bias DOES NOT determine lane selection (C654, C655)
4. Grammar compensates by selecting QO MIDDLEs at 2.2x their vocabulary rate

This extends C506 (composition non-propagation) to lane balance: not only does PP composition fail to propagate to B class structure, it fails to propagate to lane behavior. Lane identity is an EN-internal property, determined by PREFIX->MIDDLE binding at the point of token selection.

## Data Dependencies

| File | Source Phase |
|------|-------------|
| class_token_map.json | CLASS_COSURVIVAL_TEST |
| en_census.json | EN_ANATOMY |
| middle_classes_v2_backup.json | A_INTERNAL_STRATIFICATION |
| pp_role_foundation.json | A_TO_B_ROLE_PROJECTION |
| pp_classification.json | PP_CLASSIFICATION |
| lane_pp_discrimination.json | LANE_CHANGE_HOLD_ANALYSIS |
| regime_folio_mapping.json | REGIME_SEMANTIC_INTERPRETATION |
