# C1465: HIGH Frame Positional Heterogeneity

**Tier:** 2
**Scope:** B, MIDDLE, atom, HEAD, TERM, frame, hazard, position, line, heterogeneity, C1448, C1388, C1463
**Phase:** 528 (LINE_ZONE_FRAME_HAZARD)
**Date:** 2026-03-05

## Claim

The 7 HIGH-hazard frames are NOT positionally homogeneous within lines. Kruskal-Wallis among HIGH frames: H=68.8, p=1.83e-13, eta2=0.013. Two spatial clusters emerge: o-HEAD HIGH frames (o->bare mean=0.493, o->r mean=0.487) are position-neutral, while a/d-HEAD HIGH frames (a->l mean=0.602, d->y mean=0.581, a->r mean=0.551, a->n mean=0.532) are closure-biased. Positional spread among HIGH frames: 0.115 (o->r at 0.487 to a->l at 0.602).

## Evidence

### Per-Frame Positional Profiles

| Frame | N | Mean Pos | Q0 Enrich | Q4 Enrich | Character |
|-------|---|----------|-----------|-----------|-----------|
| o->bare | 1,164 | 0.493 | 1.102x | 1.031x | Position-neutral |
| o->r | 455 | 0.487 | 1.112x | 0.903x | Slightly initial-biased |
| a->n | 1,272 | 0.532 | 0.766x | 1.077x | Mildly closure-biased |
| a->r | 687 | 0.551 | 0.803x | 1.263x | Closure-biased |
| d->y | 677 | 0.581 | 0.604x | 1.257x | Strongly closure-biased |
| a->l | 527 | 0.602 | 0.515x | 1.371x | Most closure-biased |
| e->e | 151 | -- | -- | -- | Too small for profile |

### Two-Cluster Structure

| Cluster | Frames | Mean Pos | Q0 | Q4 | Character |
|---------|--------|----------|----|----|-----------|
| o-HEAD | o->bare, o->r | 0.491 | 1.10x | 0.98x | Present throughout |
| a/d-HEAD | a->l, a->r, a->n, d->y | 0.562 | 0.69x | 1.22x | Closure-concentrated |

### Statistical Test

| Test | Statistic | p-value | Effect Size |
|------|-----------|---------|-------------|
| Kruskal-Wallis (6 HIGH frames) | H=68.8 | 1.83e-13 | eta2=0.013 |

## Interpretation

The positional heterogeneity within HIGH frames connects to the atom-level operational glosses. o-HEAD = arrangement/domain operations (C1388: o = "arrange"); these carry hazard at ANY position because arranging materials is inherently risky regardless of when it happens. a-HEAD = yield/intake operations; d-HEAD = seal/containment operations. These carry hazard specifically at CLOSURE because sealing and yielding are end-of-cycle operations that occur after thermal processing is complete. The two-cluster structure means: (1) operational hazard (o-HEAD) is spatially diffuse, while (2) transitional hazard (a/d-HEAD) is spatially concentrated at line boundaries.

## Falsification Criteria

1. If KW among HIGH frames becomes non-significant (p > 0.01)
2. If o-HEAD HIGH frames become closure-biased (mean pos > 0.55)
3. If a/d-HEAD HIGH frames become position-neutral (mean pos < 0.51)

## Method

- 4,782 HIGH-hazard tokens from 23,090 Currier B corpus
- Decomposed into HEAD x TERMINAL frames via decompose_middle_hmt()
- Per-frame positional profiles computed across quintiles
- Kruskal-Wallis test among 6 HIGH frames with N >= 50
- Mean fractional position per frame

**Script:** `phases/LINE_ZONE_FRAME_HAZARD/scripts/line_zone_frame_hazard.py`
**Results:** `phases/LINE_ZONE_FRAME_HAZARD/results/line_zone_frame_hazard.json`

## Dependencies

- C1448 (HEAD x TERM frame hazard map -- 7 HIGH frames)
- C1388 (o-atom arrangement domain marker)
- C1463 (zone-hazard routing -- HIGH enriched at CLOSURE overall)
- C1427 (line-final transition profile)
