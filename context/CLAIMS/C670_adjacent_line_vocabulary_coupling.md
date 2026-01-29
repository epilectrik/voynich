# C670: Adjacent-Line Vocabulary Coupling

**Status:** VALIDATED | **Tier:** 0 | **Phase:** B_LINE_SEQUENTIAL_STRUCTURE | **Scope:** B

## Finding

Adjacent lines within Currier B folios do **not** share elevated MIDDLE vocabulary. Mean Jaccard similarity of MIDDLE sets between consecutive lines = 0.1395, vs permuted baseline = 0.1257 (+0.0138 difference). Zero of 79 folios achieve p<0.05 on individual permutation tests (1000 shuffles).

## Method

For each folio (>=8 lines), compute Jaccard similarity of MIDDLE sets between every pair of adjacent lines. Permutation baseline: shuffle line order within folio 1000 times, recompute. Per-folio p-value = fraction of permuted means >= observed.

## Key Numbers

| Metric | Value |
|--------|-------|
| Grand observed Jaccard | 0.1395 |
| Grand permuted Jaccard | 0.1257 |
| Difference | +0.0138 |
| Significant folios (p<0.05) | 0/79 (0.0%) |

## Regime Stratification

| Regime | Obs | Perm | Diff | Sig |
|--------|-----|------|------|-----|
| REGIME_1 | 0.162 | 0.143 | +0.019 | 0/23 |
| REGIME_2 | 0.127 | 0.120 | +0.007 | 0/22 |
| REGIME_3 | 0.143 | 0.134 | +0.010 | 0/8 |
| REGIME_4 | 0.129 | 0.113 | +0.016 | 0/26 |

## Interpretation

Consecutive lines do not share vocabulary identity. Each line selects its MIDDLEs independently from the folio's available pool. Combined with C664-C669 (class proportions stationary), this confirms that the control loop's token selection is stateless at the vocabulary level: the grammar constrains class deployment, but specific token choice within those classes is independent per line.

## Provenance

- Script: `phases/B_LINE_SEQUENTIAL_STRUCTURE/scripts/line_sequential_coupling.py` (Test 1)
- Data: `phases/B_LINE_SEQUENTIAL_STRUCTURE/results/line_sequential_coupling.json`
- Extends: C506.b (73% within-class MIDDLE heterogeneity → now shown to be line-independent)
