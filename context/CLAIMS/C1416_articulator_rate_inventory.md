# C1416: ARTICULATOR Rate and Inventory

**Tier:** 2
**Scope:** B
**Phase:** 517 (ARTICULATOR_DEEP_DIVE)
**Date:** 2026-03-05

## Claim

ARTICULATOR slot is occupied in 4.41% of B tokens (1,019/23,096). Nine articulators: y (51.2%), d (11.6%), l (11.4%), r (7.0%), p (5.4%), t (5.2%), k (3.5%), s (3.3%), f (1.4%). Section-dependent: COSMO 8.31% highest, BIO 3.64% lowest.

## Evidence

- Script: `phases/ARTICULATOR_DEEP_DIVE/scripts/articulator_deep_dive.py` (T1)
- Results: `phases/ARTICULATOR_DEEP_DIVE/results/articulator_deep_dive.json`
- N = 23,096 Currier B tokens (H-track, text, no labels, no uncertain)

## Relationship to Existing Constraints

- Confirms C291 (~20% have optional ARTICULATOR forms) -- C291's "20%" likely counted at token-type level; 4.41% is the token occurrence rate
- Confirms C294 (articulator density inversely correlates with prefix count)
- Extends C292 (articulators = zero unique identity distinctions) with quantitative census
