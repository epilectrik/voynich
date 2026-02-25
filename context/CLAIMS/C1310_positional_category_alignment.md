# C1310: Positional Category Alignment Between Adjacent Mode Lines

**Tier:** 2
**Scope:** B
**Phase:** CROSS_MODE_CATEGORY_COUPLING (460)
**Date:** 2026-02-25

## Finding

At the same relative position within a line, adjacent Mode A and Mode B lines tend to share the same dominant category. Same-category rate = 21.4% vs 16.9% expected by chance (1.27x enrichment), permutation p=0.001 (1000 permutations, B-line shuffle).

Positional mutual information is consistent across all 5 position bins (NMI range 0.042-0.063), with a peak at MID-LATE (NMI=0.063). THERMAL->THERMAL is the strongest same-position pairing (7.6% of all pairings).

## Method

- 300 AB consecutive line pairs
- Tokens binned into 5 relative position bins (EARLY through LATE)
- Dominant category per bin compared between A and B lines
- Permutation: shuffle B lines among AB pairs, 1000 iterations

## Position-Resolved NMI

| Position | MI (bits) | H(B) | NMI | N |
|----------|-----------|-------|-----|---|
| EARLY | 0.127 | 2.683 | 0.047 | 282 |
| EARLY-MID | 0.113 | 2.668 | 0.042 | 300 |
| MID | 0.132 | 2.625 | 0.050 | 296 |
| MID-LATE | 0.170 | 2.711 | 0.063 | 300 |
| LATE | 0.143 | 2.726 | 0.052 | 300 |

## Interpretation

The two mode tracks show genuine but weak positional synchronization — like two instruments reading from the same measure of sheet music, each playing its own part but loosely coordinated on what operational domain is active at each point in the line. The NMI values (0.042-0.063) are very low — among the weakest cross-mode signals in the project — but the consistency across all 5 position bins and the permutation significance (p=0.001) confirm it is real rather than noise. This suggests a shared positional framework rather than tight note-by-note coupling.

## Extends

- C1308 (paragraph category coherence) — positional alignment refines paragraph-level coherence to within-line position
- C1258 (parallel mode tracks) — adds positional synchronization to the parallel tracks model
- C929 (PREFIX positional grammar) — position within line is already structurally meaningful; categories inherit this

## Falsifiability

Would be falsified if same-position same-category rate <= expected by chance (permutation p > 0.05).

## Evidence Files

- `phases/CROSS_MODE_CATEGORY_COUPLING/results/parallel_track_probe.json` (P1, P6)
