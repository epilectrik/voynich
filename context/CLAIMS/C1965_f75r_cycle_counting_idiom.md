# C1965: f75r Cycle-Counting + Per-Cycle Annotation Idiom

**Tier:** 3 (single-folio anchor; mechanism plausible but not statistically generalized)
**Scope:** B, f75r, qok-cycles, recipe-correspondence, atom-annotation
**Phase:** PHASE_650_CYCLE_COUNTING_IDIOM
**Date:** 2026-04-26
**Extends:** C929 (ch active-test, applied to per-cycle annotation), C1394 (HEAD+MOD*+TERM atom architecture, refined with MOD-subtype distinction), C1735 / F-B-007 (e-extensibility for thermal intensity)
**Relates to:** C1300 (qo near-pure THERMAL channel), C1958 (ot transfer/iteration), C1316 (O-PREFIX categorical scaffold), Phase 641-643 f75r anchor analysis
**Refines:** C1394 (MOD-atom class internal structure)

---

## Statement

On f75r, the recipe's two-phase reflux specification (× 4 vegades first, × 9 vegades after — III.19) is encoded as **line-localized closed-cycle clusters** at corpus-rare specificity. Closed cycles are tokens matching `qok+...+dy` (qok prefix + -dy closure suffix), representing complete fire-bounded operational passes per C1394 atom architecture.

| Phase | Recipe specification | Encoding location | Closed-cycle count | Corpus rarity |
|---|---|---|---|---|
| First phase | "× 4 vegades" | L13 (single line) | 4 | ~7 other 1-line windows |
| Second phase (n+1) | "× 9 vegades" + initial pass | L36-L38 (3-line window) | **10** | **Corpus-singular (only 3-line window in Currier B with 10 closed cycles)** |
| Second phase (n) | "× 9 vegades" alone | L37-L38 (2-line window) | 9 | **Corpus-singular** |

The ×9 anchor at L36-L38 is **the only such cluster in all of Currier B**. The cycle-counting interpretation accounts for it; chance does not.

---

## Per-cycle annotation finding

The 10-cycle L36-L38 cluster is composed of structurally distinguishable cycle tokens whose MOD-atom composition encodes per-cycle operational character:

| Cycle | Token | MOD atoms | Operational reading |
|---|---|---|---|
| 1 | qokeedy | k + e + e | initial pass at degree-2 stabilized heat (balneum mariae signature per F-B-007) |
| 2 | qokedy | k + e | degree-1 routine cycle |
| 3 | qokedy | k + e | degree-1 routine cycle |
| **4** | **qokchdy** | **k + ch** | **raw heat + ACTIVE TEST** (no e modifier; ch per C929) |
| **5** | **qokechdy** | **k + e + ch** | **degree-1 + ACTIVE TEST** |
| 6-7 | qokeedy ×2 | k + e + e | degree-2 routine cycles |
| 8-9 | qokedy ×2 | k + e | degree-1 routine cycles |
| 10 | qokeedy | k + e + e | degree-2 routine cycle |

**The two ch-marked test cycles (4-5) sit exactly at the recipe's phase boundary** between "× 4 vegades" and "× 9 vegades." Operationally coherent: hot-test (cycle 4: raw heat + ch verifies behavior at peak intensity), then cool-and-test (cycle 5: degree-1 + ch verifies cooled distillate), then resume routine. This corresponds to standard distillation practice (verify quality before committing to a second-phase reflux).

The ch-MOD-atom-inside-cycle-token annotation generalizes C929's `ch = active sampling/test` from a standalone-prefix observation to a **per-cycle annotation marker** within compound cycle tokens.

---

## Refinement of C1394 (MOD-atom class)

The HEAD+MOD*+TERM atom architecture (C1394) treats MOD as a single class. Phase 650 evidence requires distinguishing two operationally distinct subtypes:

| MOD subtype | Members (partial) | Semantics |
|---|---|---|
| **Continuous / extensible** | `e` (thermal intensity, F-B-007/C1735), `i` (duration, per existing notes) | Multiple instances modulate a continuous parameter (degree-1, degree-2, degree-3). Not "multiple discrete actions." |
| **Discrete / event** | `ch` (active test, C929), `d` (mark), `n` (halt/bind) | Presence vs. absence is the binary; depth not meaningful. |

Earlier loose readings conflating these (e.g., interpreting `qokeedy` as "fire + heat + cool + cool + end" treating each `e` as a discrete cool action) are corrected. The right reading: `qokeedy` = "fire-on + heat-at-degree-2-stabilized + close" — single thermal-regime spec, not action-sequence.

This refinement does NOT change C1394's grammatical claim (HEAD+MOD*+TERM still describes the slot architecture). It refines the gloss-level interpretation of MOD-atom semantics.

---

## Idiom does NOT generalize to small-count recipes

Tested on f82v (×4 vessel spec) and f112r (×3 cohobation):

| Folio | Recipe | Best line-window match | Corpus rarity |
|---|---|---|---|
| f82v | ×4 (n+1=5) | 5 cycles in 4-line window | 30 other corpus windows |
| f82v | ×4 (n=4) | 4 cycles in 3-line window | 64 other corpus windows |
| f112r | ×3 (n+1=4) | No 1-5 line window with 4 cycles | n/a |
| f112r | ×3 (n=3) | No 1-5 line window with 3 cycles | n/a |

Small iteration counts (×3, ×4) are structurally **indistinguishable from corpus noise** at line-window resolution. Many windows have those counts by chance. The cycle-counting idiom is **detectable only when the iteration count is large enough to be corpus-rare** (≥9 or so).

This is an epistemic limit, not a sample-size issue: you cannot detect "encoded ×3" in a corpus where dozens of windows have 3 closed cycles by chance. The idiom may still operate on small-count recipes, but evidence at that scale is structurally invisible.

---

## Why this is f75r-specific (and what would change that)

Two possibilities for the non-generalization:

1. **Coverage gap:** f75r is the only matched recipe with a sufficiently large iteration count for corpus-rare encoding to be detectable. Other recipes use the same idiom but their counts are below the noise floor.
2. **Genuinely f75r-specific:** the cycle-counting idiom is a feature of f75r's encoding specifically; other recipes use different mechanisms to specify cycle counts.

To distinguish: search the corpus for unmatched folios with corpus-rare closed-cycle line-windows (≥7 in 1-3 line window). If such folios cluster on procedures that *should* have large iteration counts (e.g., deep cohobation, multi-pass purification), idiom (1) is supported; we'd need new recipe matches at large iteration counts to confirm. If the rare windows are scattered without operational coherence, the idiom may be f75r-specific.

---

## Falsification

Would be falsified if:

1. The L36-L38 closed-cycle count is shown to be reproducible by a chance arrangement that doesn't depend on cycle-counting (e.g., a non-iterative grammatical pattern that incidentally produces 10 closed cycles in 3 lines)
2. The ch-marked cycles (4-5) on f75r are shown to be unrelated to the recipe's phase boundary (e.g., they appear in randomly distributed positions across cycle clusters elsewhere in the corpus)
3. A reverse search finds many folios with corpus-rare closed-cycle clusters but no plausible operational reason for large iteration counts

---

## Provenance

- `phases/PHASE_650_CYCLE_COUNTING_IDIOM/scripts/s4_line_window_closed_cycles.py` (final correct test)
- `phases/PHASE_650_CYCLE_COUNTING_IDIOM/scripts/s2_qok_runs_with_gaps.py` (sequential run analysis)
- `phases/PHASE_650_CYCLE_COUNTING_IDIOM/scripts/s3_closed_cycle_filter.py` (paragraph-level intermediate, retained for transparency)
- `phases/PHASE_650_CYCLE_COUNTING_IDIOM/results/line_window_closed_cycles.json`
- `phases/PHASE_650_CYCLE_COUNTING_IDIOM/results/qok_runs_with_gaps.json`
- Project memory note `f75r Crib Decode Session (2026-03-25, resolved 2026-04-24)`: original × 4 and × 9 anchors identified by direct folio reading, refined by user correction in Phase 650
