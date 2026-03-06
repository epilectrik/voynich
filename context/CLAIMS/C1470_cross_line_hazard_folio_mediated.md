# C1470: Cross-Line Hazard Correlation is Folio-Mediated

**Tier:** 2
**Scope:** B, line, hazard, cross-line, folio, independence, C1429, C681, C1463
**Phase:** 530 (CROSS_LINE_HAZARD)
**Date:** 2026-03-05

## Claim

Cross-line hazard frame correlation (MI=0.0172 bits, rho=0.238) is ENTIRELY explained by folio-level shared environment. Within-folio shuffled controls produce equivalent MI (p=0.212) and equivalent rho (p=0.098). The cross-line hazard MI is 0.54x of C1429's category MI (0.032 bits) -- hazard frames carry LESS cross-line information than operational categories. Autocorrelation at lags 1-4 (rho=0.207-0.233) all collapse under within-folio permutation (p=0.115-0.535). Within-paragraph (rho=0.233) and cross-paragraph (rho=0.207) pairs show equivalent correlation, confirming no paragraph-boundary effect. This EXTENDS C1429 from category/suffix-mode resolution to hazard-frame resolution: lines are i.i.d. samples from folio hazard profiles.

## Evidence

### Cross-Line Hazard MI vs C1429 Category MI

| Metric | Cross-line hazard (this) | C1429 category | C1429 suffix mode |
|--------|-------------------------|----------------|-------------------|
| MI (bits) | 0.0172 | 0.032 | 0.003 |
| Ratio to category | 0.54x | 1.00x | 0.09x |

Hazard frames sit between suffix mode and category in cross-line information, but below category.

### Folio-Shuffle Control

| Metric | Real | Shuffled mean | p-value |
|--------|------|---------------|---------|
| Dominant hazard MI | 0.0172 bits | 0.0145 bits | 0.212 |
| HIGH fraction rho | 0.238 | 0.216 | 0.098 |

Neither metric survives within-folio shuffling at alpha=0.05.

### Autocorrelation Lag Structure

| Lag | N pairs | Spearman rho | Parametric p | Permutation p |
|-----|---------|-------------|-------------|---------------|
| 1 | 2,322 | 0.233 | <0.0001 | 0.115 |
| 2 | 2,243 | 0.222 | <0.0001 | 0.248 |
| 3 | 2,164 | 0.217 | <0.0001 | 0.306 |
| 4 | 2,085 | 0.208 | <0.0001 | 0.535 |

All lags show flat rho (~0.22) that is entirely folio-mediated. No decay with increasing lag confirms no sequential structure -- pure shared environment.

### Mode-Stratified Analysis

| Mode transition | N | HIGH rho | ZERO rho | MI (bits) |
|----------------|---|----------|----------|-----------|
| A->A | 590 | 0.162 | 0.090 | 0.017 |
| A->B | 552 | 0.214 | 0.227 | 0.017 |
| B->A | 539 | 0.263 | 0.181 | 0.058 |
| B->B | 631 | 0.228 | 0.224 | 0.016 |

Despite C1451 (Mode B carries 100% of forbidden violations), B->B pairs do NOT show elevated hazard coupling vs A->A. The correlation is uniform across all mode transitions.

### Within-Paragraph vs Cross-Paragraph

| Context | N | HIGH rho | MI (bits) |
|---------|---|----------|-----------|
| Within-paragraph | 2,026 | 0.233 | 0.018 |
| Cross-paragraph | 312 | 0.207 | 0.014 |
| Difference | -- | 0.027 | 0.004 |

Negligible difference. Paragraph boundaries do not modulate hazard correlation.

## Interpretation

Lines draw their hazard profile from the folio's overall hazard budget, not from what the previous line did. The moderate raw correlations (rho~0.23) are real but reflect folio-level thematic consistency -- high-hazard folios produce high-hazard lines throughout, low-hazard folios produce low-hazard lines throughout. There is no sequential hazard structure: no line "responds to" the hazard exposure of its predecessor. This is consistent with C1429 (cross-line category independence), C681 (sequential coupling is folio-mediated), and C1399/C1400 (paragraph ordering null). Safety enforcement happens within each line independently (C1463, C1469), not across lines.

## Falsification Criteria

1. If within-folio permutation p drops below 0.01 for MI or rho
2. If lag-1 rho significantly exceeds lag-4 rho after folio control (would indicate genuine sequential decay)
3. If within-paragraph rho exceeds cross-paragraph rho by >0.10 after folio control

## Method

- 2,338 consecutive line pairs across 82 Currier B folios
- Per-line hazard profiles from C1448 frame hazard map (HIGH/LOW/ZERO/IMMUNE)
- Mutual information of dominant hazard class between consecutive lines
- Spearman correlation of per-class hazard fractions
- 500 within-folio shuffle permutations for all metrics
- 2,000 random permutations for MI significance test
- Autocorrelation at lags 1-4 with within-folio permutation control

**Script:** `phases/CROSS_LINE_HAZARD/scripts/cross_line_hazard.py`
**Results:** `phases/CROSS_LINE_HAZARD/results/cross_line_hazard.json`

## Dependencies

- C1429 (cross-line category independence MI=0.032 bits -- base comparison)
- C1463 (line-level zone-hazard routing -- within-line safety architecture)
- C681 (sequential coupling is folio-mediated -- general principle confirmed here)
- C1448 (HEAD x TERM frame hazard map -- hazard classification used)
- C1451 (Mode B exclusive forbidden carrier -- tested for mode-stratified effect)
- C1399 (paragraph ordering null -- paragraph boundary shows no effect)
