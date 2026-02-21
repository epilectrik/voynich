# C1182: Sister Concentration Shows Moderate Folio-Level Consistency (ICC=0.317)

**Tier:** 2
**Scope:** B, sister pairs, program structure
**Phase:** SISTER_PAIR_MECHANISM (Phase 420)
**Depends on:** C639, C855, C862

## Statement

Sister-pair choice shows moderate folio-level consistency (ICC(1,1)=0.317) computed from 459 paragraphs across 74 folios with 2+ testable paragraphs. The per-folio ch_preference distribution is unimodal: median=0.660, IQR=[0.558, 0.783], with 18.3% extreme (>0.8 or <0.2) and only 2/82 near-deterministic (>0.9 or <0.1). Sister choice is partly a folio-level property and partly varies within programs.

## Evidence

| Metric | Value |
|--------|-------|
| ICC(1,1) | 0.317 |
| Testable paragraphs (n>=5 sister tokens) | 459 |
| Multi-paragraph folios | 74 |
| Median ch_pref | 0.660 |
| Q25-Q75 | 0.558-0.783 |
| Extreme fraction (>0.8 or <0.2) | 18.3% |
| Near-deterministic (>0.9 or <0.1) | 2/82 |

## Interpretation

ICC=0.317 means about 32% of paragraph-level sister variance is attributable to the folio (program identity), while 68% varies within programs. This is consistent with C855 (folio = parallel programs) and C862 (paragraph independence): each paragraph makes a semi-independent sister choice, but the folio provides a baseline tendency. Sister preference is neither fully determined at the folio level nor fully local — it's a program-wide bias with paragraph-level modulation.

## Provenance

- Phase 420 Test 3: CONCENTRATION_ICC
- Script: `phases/SISTER_PAIR_MECHANISM/scripts/sister_pair_mechanism.py`
- Results: `phases/SISTER_PAIR_MECHANISM/results/sister_pair_mechanism.json` -> test3_concentration_icc
