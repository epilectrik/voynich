# PHASE_727 — Exact-count reproduction audit of the recipe-match anchors

**Run:** 2026-05-21 (scripts + result on disk; INDEX written and registered 2026-09-27 during the registry reconciliation).
**Status:** COMPLETE — reproducibility finding, no new constraint. Annotations placed on C1944, C1947, C1948, C1953, C1955.

## Question
Do the exact token counts cited as recipe correspondences in the Pseudo-Lull match catalogue reproduce under the current parser?

## Result (`results/exact_count_audit.json`)
27 counts checked; **21 reproduce (78%, Wilson 95% CI 59–89%), 6 do not**:

| Count | Claimed | Actual | Row |
|---|---|---|---|
| f84v cs | 2 | 3 | C1947 (dar=4, dal=1 reproduce) |
| f115v lch | 4 | 5 | C1948 |
| f115v eed | 7 | 8 | C1948 |
| f114r eed | 8 | 10 | C1953 |
| f113r fch | 4 | 2 | C1944 |
| f106r eed | 2 | 3 | C1955 |

Five of the six failures drift upward (all four eed counts), which points to a systematic change in count definitions (consistent with C1957's revision of e-initial suffix handling) rather than random miscounting. The joint-specificity block in the JSON also shows the multi-feature signatures are not folio-unique for several anchors (e.g. f111r's dar=2 ∧ dal=2 matches 4 folios).

## Disposition (lean-expert, 2026-09-27)
- Annotate the affected rows and strike each count-correspondence clause that fails (done in INDEX.md).
- Going forward, every count is stored with its matching rule (exact / starts-with / contains; cf. C1939) and its parser version, plus a sensitivity band; a correspondence that holds under only one definition is a forking path.
