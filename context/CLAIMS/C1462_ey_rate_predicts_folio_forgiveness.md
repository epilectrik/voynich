# C1462: e→y Rate Predicts Folio Forgiveness via AXM Attractor

**Tier:** 2
**Scope:** B, MIDDLE, atom, e-HEAD, y-terminal, AXM, forgiveness, folio, hazard, C105, C458, C980, C1169
**Phase:** 525 (EY_SAFE_PATHWAY)
**Date:** 2026-03-05

## Claim

Folio-level e→y rate is a powerful predictor of program forgiveness. e→y vs AXM self-transition: rho=+0.569, p<1e-7 (82 folios). e→y vs hazard rate: rho=-0.473, p=7e-6. Quartile analysis: Q1 (6.6% e→y) shows 40.6% AXM self-transition and 28.4% hazard; Q4 (21.1% e→y) shows 55.0% AXM self-transition and 22.1% hazard. Post-e→y, AXM rate increases to 77.0% (vs 67.6% pre-e→y, +9.4pp) — e→y acts as a one-way ratchet toward AXM. e→y tokens are AXM-enriched (1.16x) with complete exclusion from FL_HAZ, FL_SAFE, and CC macro-states.

## Evidence

### Folio-level correlations (N=82 folios)

| Correlation | rho | p-value |
|-------------|-----|---------|
| e→y vs AXM fraction | +0.471 | 8e-6 |
| e→y vs AXM self-transition | +0.569 | <1e-7 |
| e→y vs FQ rate | -0.369 | 6e-4 |
| e→y vs hazard rate | -0.473 | 7e-6 |

### Quartile analysis

| Quartile | Mean e→y | AXM rate | AXM self | FQ rate | Hazard rate |
|----------|----------|----------|----------|---------|-------------|
| Q1 (low) | 6.6% | 58.3% | 40.6% | 24.8% | 28.4% |
| Q2 | 11.0% | 63.0% | 45.5% | 21.0% | 25.6% |
| Q3 | 15.6% | 67.1% | 49.8% | 16.9% | 22.9% |
| Q4 (high) | 21.1% | 70.6% | 55.0% | 16.5% | 22.1% |

### Macro-state profile

| Macro-state | e→y rate | Corpus rate | Enrichment |
|-------------|----------|-------------|------------|
| AXM | 78.1% | 67.7% | 1.16x |
| FQ | 17.4% | 18.0% | 0.97x |
| AXm | 4.5% | 3.0% | 1.47x |
| CC | 0.0% | 4.6% | 0.00x |
| FL_HAZ | 0.0% | 6.0% | 0.00x |
| FL_SAFE | 0.0% | 0.8% | 0.00x |

### One-way ratchet

- Post-e→y AXM rate: 77.0%
- Pre-e→y AXM rate: 67.6%
- Delta: +9.4pp toward AXM
- e→y self-chaining rate: 18.7%
- Dominant post-e→y HEAD: k (817 tokens, 34.3%) — cool→end→heat again

## Interpretation

e→y fraction is the mechanical basis of the forgiveness gradient (C458, C980). Programs with more cooling/stabilization/ending operations spend more time in the AXM attractor and less time in hazardous transitions. The one-way ratchet effect (+9.4pp toward AXM after each e→y token) explains how e→y achieves stability anchoring without reactive deployment: each e→y token statistically increases the probability that the system stays in or returns to AXM, making high-e→y programs inherently more forgiving. The dominant e→y→k transition (cool→end→heat again) is the primary thermal cycling pathway.

## Falsification Criteria

1. If e→y vs AXM self-transition correlation drops below rho=+0.30
2. If e→y vs hazard rate correlation weakens to |rho|<0.20
3. If post-e→y AXM rate drops below pre-e→y rate (ratchet inverts)

## Method

- 82 B folios with e→y fraction computed
- Folio-level AXM self-transition, AXM fraction, FQ rate, hazard rate computed
- Spearman correlations between e→y fraction and each metric
- Quartile analysis by e→y rate
- Post-e→y transition analysis (what HEAD follows e→y tokens)

**Script:** `phases/EY_SAFE_PATHWAY/scripts/ey_safe_pathway.py`
**Results:** `phases/EY_SAFE_PATHWAY/results/ey_safe_pathway.json`

## Dependencies

- C105 (e = STABILITY_ANCHOR, 54.7% recovery paths)
- C458 (Execution design clamp vs recovery freedom)
- C980 (Free variation envelope: ~57% genuine design freedom)
- C1169 (AXM residual closed — ~27% genuine design freedom)
- C1448 (e→y largest safe frame, 3,475 tokens)
- C976 (6-state macro-automaton)
