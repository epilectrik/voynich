# C1402: No Sequential Convergence to AXM at Any Scale

**Tier:** 2 (ESTABLISHED)
**Scope:** B, convergence, paragraph, line, AXM
**Phase:** STATE_C_CONVERGENCE_REVISIT (Phase 513)
**Reframes:** C074 (dominant convergence), C084 (MONOSTATE)
**Extends:** C1399 (paragraph ordering null), C1400 (state-independent ordering)
**Relates to:** C976 (6-state automaton), C1038 (AXM entropy convergence), C666 (kernel contact stationarity)

---

## Statement

Sequential convergence toward AXM (STATE-C) is **not detected at any temporal scale**: neither across paragraphs within folios nor across lines within paragraphs. Adjacent paragraphs' AXM terminal rates are fully independent (rho=0.001, permutation p=0.983). AXM dominance is a folio-level thematic property determined by section, not a sequential dynamical process.

### Cross-Paragraph (T3): No Sequential Convergence

| Metric | Value |
|--------|-------|
| Folios tested (2+ paragraphs) | 46 |
| Increasing (later paras more AXM) | 16 |
| Decreasing | 15 |
| Flat | 14 |
| Mean within-folio rho | -0.007 |
| Global rho | -0.019 |
| Global p | 0.780 |

Diagnostic quintiles of paragraph position vs AXM rate: Q0=0.649, Q1=0.717, Q2=0.659, Q3=0.652, Q4=0.642. Flat.

### Cross-Paragraph (T4): Full Independence

| Metric | Value |
|--------|-------|
| Adjacent pairs | 173 |
| Adjacent rho | 0.001 |
| Adjacent p | 0.989 |
| Shuffle mean rho (1000 perms) | 0.016 |
| Permutation p | 0.983 |

### Within-Paragraph (T6): No Line-Level Convergence

| Metric | Value |
|--------|-------|
| Paragraphs tested | 260 |
| Mean rho (line position vs AXM) | -0.016 |
| Wilcoxon p (rho != 0) | 0.535 |
| First half mean AXM | 0.690 |
| Second half mean AXM | 0.681 |
| Mann-Whitney p | 0.830 |

No section shows significant within-paragraph convergence (B: +0.015, H: -0.045, S: -0.046).

### Folio Theme Sufficiency (T5)

| Model | MSE |
|-------|-----|
| Folio-mean baseline | 0.110 |
| Position-aware model | 0.143 (-29.6% worse) |

Knowing paragraph position within the folio adds zero useful information. The folio's overall AXM rate is the best predictor of any paragraph's terminal state.

---

## Consistency with C1038

C1038 showed entropy convergence *within* AXM runs (3.84 → 2.52 bits). This is not contradicted — C1038 describes narrowing of class vocabulary within the AXM macro-state, not convergence *toward* AXM from other states. The grammar narrows within AXM; it does not progressively enter AXM.

---

## Falsification Criteria

1. If a finer-grained state representation (token-level rather than line-level) shows monotonic AXM increase within paragraphs, the line-level resolution was too coarse
2. If a specific section shows rho > 0.3 (p < 0.01) for within-paragraph convergence, convergence may be section-specific
3. If conditioning on REGIME reveals convergence in specific REGIME types, the signal may be REGIME-masked

---

## Method

- 264 paragraphs across 82 folios (3+ body lines per paragraph)
- 6-state classification via C976 partition applied to 49-class assignments
- T3: Per-folio Spearman of paragraph ordinal vs terminal AXM rate
- T4: Adjacent paragraph AXM correlation + 1000-permutation shuffle within folio
- T5: MSE comparison of folio-mean baseline vs position-aware OLS
- T6: Per-paragraph Spearman of line position vs AXM rate; first-half vs second-half split
- Random seed 42

**Script:** `phases/STATE_C_CONVERGENCE_REVISIT/scripts/state_c_revisit.py`
**Results:** `phases/STATE_C_CONVERGENCE_REVISIT/results/state_c_revisit.json` (T3-T6)
