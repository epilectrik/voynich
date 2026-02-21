# C1184: ch/sh and ok/ot Are Largely Independent Sister Axes

**Tier:** 2
**Scope:** B, sister pairs, within-class variation
**Phase:** SISTER_PAIR_MECHANISM (Phase 420)
**Depends on:** C408, C410, C1057

## Statement

ch/sh and ok/ot sister preferences are weakly correlated (partial rho=0.204, p=0.066 after section control) — below the parallel-mechanism threshold. The two sister pairs show OPPOSITE positional asymmetries: ch is later than sh (gap=+0.092), while ok is earlier than ot (gap=-0.050). Both pairs have similar section-explained variance (ch: R2=0.361, ok: R2=0.364). ok_pref has higher variance (std=0.185 vs ch mean-centered). This extends C1057 (lane-sister orthogonality): not only are lane and sister different axes, the two sister pairs themselves are largely independent within-class variation dimensions.

## Evidence

| Metric | ch/sh | ok/ot |
|--------|-------|-------|
| Mean preference | 0.667 | 0.539 |
| Section R2 | 0.361 | 0.364 |
| Position gap | +0.092 (ch later) | -0.050 (ok earlier) |
| Cross-correlation (partial) | rho=0.204, p=0.066 |

n=81 folios with both ch_pref and ok_pref.

## Interpretation

The two sister pairs are governed by similar-strength section conditioning but show different positional patterns and are only weakly correlated. This suggests they encode different within-class control dimensions — ch/sh modulates one operational parameter (active testing vs passive monitoring, C929), while ok/ot modulates another (yet uncharacterized, with reversed positional polarity). The 49-class grammar has at least two semi-independent within-class variation axes.

## Provenance

- Phase 420 Test 5: OK_OT_PARALLEL
- Script: `phases/SISTER_PAIR_MECHANISM/scripts/sister_pair_mechanism.py`
- Results: `phases/SISTER_PAIR_MECHANISM/results/sister_pair_mechanism.json` -> test5_ok_ot_parallel
