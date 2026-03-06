# C1479: HEAD-Modifier Selectivity Partition

**Tier:** 2
**Scope:** B, MIDDLE, atom, HEAD, modifier, selectivity, partition, co-occurrence
**Phase:** HEAD_DOMAIN_DIFFERENTIATION (Phase 533)
**Date:** 2026-03-05

## Statement

Each HEAD atom selects a distinct modifier profile, creating a near-partition of the modifier space. a monopolizes i (4.08x, 78.5% i-rate), e monopolizes d (1.99x, 38.1% d-rate), o attracts p/f/c (3.51x/2.83x/1.42x), k/t are modifier-depleted (any_modifier: k=13.5%, t=20.5% vs baseline ~35%), and headless MIDDLEs are the universal modifier host (all 6 modifiers enriched 1.07-2.07x, any_modifier=57.8%). The modifier selectivity aligns with C1473 (frame incompatibility): a's i-monopoly and e's d-monopoly create non-overlapping modifier demands that explain 8/15 modifier pair avoidances. Overall any_modifier rates span 6x range: a=51.3%, headless=57.8% (modifier-rich) vs k=13.5%, t=20.5% (modifier-poor).

## Evidence

- **a-HEAD:** i=78.5% (4.08x), all others <1% each. any_modifier=51.3%
- **e-HEAD:** d=38.1% (1.99x), c=5.4% (0.59x), s=1.0% (0.42x). any_modifier=44.6%
- **o-HEAD:** p=9.7% (3.51x), c=13.1% (1.42x), f=2.7% (2.83x), d=10.6% (0.55x), i=6.1% (0.32x). any_modifier=31.3%
- **k-HEAD:** c=8.1% (0.88x), d=3.3% (0.17x). any_modifier=13.5%
- **t-HEAD:** c=13.1% (1.43x), d=6.0% (0.31x). any_modifier=20.5%
- **headless:** i=28.1% (1.46x), d=20.5% (1.07x), c=15.7% (1.71x), s=5.1% (2.07x), p=4.9% (1.75x), f=1.6% (1.69x). any_modifier=57.8%
- **Modifier monopolies:** i is 88.6% a-HEAD (C1473), d is 85.1% e-HEAD (C1473) — near-exclusive
- **Partition structure:** 3 monopolized (a-i, e-d, o-p), 2 depleted (k, t), 1 universal (headless)

## Relationship to Prior Constraints

- Directly explains C1473 (modifier avoidance is frame incompatibility) — incompatible HEADs drive modifier avoidance
- Extends C1472 (modifier co-occurrence avoidance dominates ordering) — avoidance emerges from HEAD partition
- Confirms C1474 (s-modifier universal connector) — s has broad HEAD distribution (entropy 1.909), consistent with no HEAD monopolizing s
- Connects to C1411 (PREFIX->MIDDLE selectivity hierarchy) — HEAD selects modifiers as MIDDLE selects suffix
- Links C1452-C1456 (i-modifier Simpson's paradox) — i's a-HEAD monopoly is the mechanism behind i's hazardous frame selection

## Falsifiable Prediction

If modifier selectivity is HEAD-determined, artificially swapping HEAD labels in compound MIDDLEs while preserving modifiers should produce forbidden or extremely rare combinations (e.g., k+i, e+p, a+d) at rates matching the observed avoidance structure.
