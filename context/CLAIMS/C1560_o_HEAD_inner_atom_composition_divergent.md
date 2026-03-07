# C1560: o-HEAD Inner Atom Composition Divergent

**Tier:** 2
**Scope:** B, MIDDLE, atom, HEAD, o-HEAD, inner-atom, composition, divergent, y-depletion, l-enrichment, p-enrichment, CHANNELED, terminal, C1388, C1475, C1484, C1487, C1556, C1560
**Phase:** O_DOMAIN_DEEP_DIVE (Phase 548)
**Date:** 2026-03-06

## Claim

The internal composition of o-HEAD compounds (excluding the initial o atom itself) dramatically diverges from the corpus baseline. The y-atom depletion at 0.023x is the most extreme single-atom divergence in the entire atom system. l-enrichment at 2.739x and r-enrichment at 2.292x show o-HEAD compounds are built from a CHANNELED terminal vocabulary (l, r, h) while categorically excluding the OPERATION terminal (y) and the CONTAINMENT/TRANSITION terminal (n at 0.193x). Executive modifiers p (4.674x) and f (3.650x) are strongly enriched inside compounds, paralleling the modifier enrichment (C1558) and showing executive atoms are attracted to o-HEAD at both the modifier AND inner-atom levels.

## Evidence

### Inner atom enrichment (o-HEAD compounds vs corpus baseline)

| Atom | o-HEAD Rate | Corpus Rate | Enrichment |
|---|---|---|---|
| p | 7.0% | 1.5% | 4.674x |
| f | 1.9% | 0.5% | 3.650x |
| l | 23.2% | 8.5% | 2.739x |
| r | 12.6% | 5.5% | 2.292x |
| h | 9.0% | 4.0% | 2.237x |
| d | 7.6% | 14.0% | 0.543x |
| i | 4.4% | 11.9% | 0.368x |
| n | 1.1% | 5.9% | 0.193x |
| **y** | **0.4%** | **15.8%** | **0.023x** |

### Compound length distribution

| Length | Count | % |
|---|---|---|
| 1-atom (bare o) | 388 | 14.3% |
| 2-atom | 1,629 | 59.9% |
| 3-atom | 220 | 8.1% |
| 4-atom | 329 | 12.1% |

Overwhelmingly 2-atom (59.9%), with a secondary peak at 4-atom compounds (opch-type constructions).

### Connection to terminal taxonomy

C1487 defines three terminal tiers: LOCKED (r, m), CHANNELED (l, y, n), DIFFUSE (h). o-HEAD selects CHANNELED l-terminal and LOCKED r-terminal while avoiding CHANNELED y-terminal and n-terminal. This creates a distinctive terminal vocabulary that is neither LOCKED-dominant nor DIFFUSE-dominant but a specific CHANNELED subset.

## Interpretation

o-HEAD compounds use a restricted atom palette that is functionally coherent with arrangement semantics. The avoidance of y (operation-ending), n (containment/iteration-binding), and i (iteration) means arrangement compounds do not encode endings, binding, or iteration. The enrichment of l (staging/state), r (flow), and executive modifiers p/f means arrangement compounds describe configurations, flow patterns, and flagged/paused states.

## Falsification Criteria

1. If y-atom depletion in o-HEAD is shown to be a sampling artifact
2. If another HEAD atom shows more extreme inner-atom divergence from corpus baseline
3. If o-HEAD compound composition converges with corpus baseline in a larger corpus

## Source

`phases/O_DOMAIN_DEEP_DIVE/results/o_domain_deep_dive.json`
