# C1440: Three-Tier Terminal Opacity Gradient

**Tier:** 2
**Scope:** B, MIDDLE, atom, terminal, suffix, opacity, gradient, suppression, C1412, C1438, C1408
**Phase:** 522 (TWO_LEVEL_CLOSURE)
**Date:** 2026-03-05

## Claim

Terminal atoms form a three-tier suffix suppression gradient, not a binary opaque/transparent split. OPAQUE: n (0.84%), y (1.61%), m (4.15%) -- suppress suffix <5%. SEMI-TRANSPARENT: l (16.78%), r (19.52%) -- partial suppression ~17-20%. TRANSPARENT: h (98.68%) -- near-obligatory suffix attachment. Overall association V=0.753, chi2=7384.7, p=0.0. The opacity gradient is independent of category concentration (Spearman rho=0.086, p=0.87).

## Evidence

### Suffix rates by terminal

| Terminal | N tokens | Suffix Rate | Suppression Ratio vs 48.3% baseline |
|----------|----------|------------|--------------------------------------|
| n | 2,147 | 0.84% | 57.5x |
| y | 4,780 | 1.61% | 30.0x |
| m | 289 | 4.15% | 11.6x |
| l | 2,568 | 16.78% | 2.9x |
| r | 1,962 | 19.52% | 2.5x |
| h | 1,284 | 98.68% | 0.49x (ATTRACTS) |

### Tier boundaries

- OPAQUE to SEMI-TRANSPARENT gap: 12.6 percentage points (m 4.15% to l 16.78%)
- SEMI-TRANSPARENT to TRANSPARENT gap: 79.2 percentage points (r 19.52% to h 98.68%)
- Both gaps are unambiguous with no intermediate values

### Category independence

Each tier contains terminals from different category domains:
- OPAQUE: y(OPERATION 40.6%), m(TRANSITION 87.9%), n(TRANSITION 39.3%)
- SEMI-TRANSPARENT: l(STAGING 64.5%), r(FLOW 98.9%)
- TRANSPARENT: h(MARKING 30.0%, most distributed)

Suffix suppression vs category concentration: Spearman rho=0.086, p=0.87 (null).

## Interpretation

The terminal atom gates suffix access on a continuous gradient with three discrete tiers. OPAQUE terminals create self-contained instructions that encode all specification within the MIDDLE. TRANSPARENT terminals delegate specification to the suffix layer. SEMI-TRANSPARENT terminals can operate either way. This extends C1412 (MIDDLE dominates suffix determination, V=0.503) to show the mechanism is terminal-atom opacity.

## Falsification Criteria

1. If any terminal's suffix rate moves across a tier boundary by >5pp under different filtering
2. If opacity correlates significantly with category concentration (rho > 0.7)

## Method

- All 23,096 clean Currier B tokens classified by MIDDLE terminal atom
- Suffix rate = fraction of tokens with any suffix attachment
- Chi-squared contingency for overall TERMINAL x suffix-presence
- Spearman correlation of suffix rate vs category concentration

**Script:** `phases/TWO_LEVEL_CLOSURE/scripts/two_level_closure.py`
**Results:** `phases/TWO_LEVEL_CLOSURE/results/two_level_closure.json`

## Dependencies

- C1412 (MIDDLE dominates suffix determination)
- C1438 (m-terminal categorical suffix suppression)
- C1408 (suffix compositional structure)
- C1409 (suffix atoms diverge from MIDDLE-terminal atoms)
