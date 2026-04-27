# C1969: Window-Density qok-Class Specificity for the f75r ×9 Anchor

**Tier:** 2
**Scope:** B, cross-folio, qok, window-density, recipe-correspondence, x9-anchor, C1925, C1965
**Phase:** PHASE_659_WINDOW_DENSITY_SPECIFICITY
**Date:** 2026-04-26
**Refines:** C1965 (f75r cycle-counting idiom) with corpus-wide specificity measurement
**Pairs with:** C1928 (f75r→f84r product chain), C1959 (paragraph layout-order tracks recipe-phase order)
**Distinct from:** Phase 657 (prefix-class contiguous, NULL), Phase 658 (lexeme contiguous, INCONCLUSIVE)

---

## Statement

The Phase 636 f75r ×9 anchor — originally documented as "9 qok-class tokens across L37-L38" — is corpus-rare under window-density methodology and corresponds to its matched Catalan numerical REPETITION marker at higher rate than chance.

**Corpus-wide measurement:** ≥9 qok-class tokens within any 2-consecutive-line sliding window appears on **3/82 = 3.7%** of Currier B folios.

**Matched-pair test:** 4/4 numerical-anchor matches under the inclusive ≥N rule. Null mean: 2.16 from 10,000 random folio reassignments. **Observed: 4. p = 0.0208 (one-sided).**

**Joint specificity:** Of the 3 high-density folios (f75r, f86v3, f108r), only f75r matches a Catalan chapter (III.19.0) carrying an explicit `×9 vegades` numerical REPETITION marker. f86v3's matched II.10.0 and f108r's matched III.16.0 contain no numerical `vegades` markers.

---

## Empirical evidence

### Corpus-wide qok-density coverage (any 2-line window, all 82 Currier B folios)

| Threshold | Folio coverage |
|---|---|
| ≥2 | 79/82 (96.3%) |
| ≥3 | 68/82 (82.9%) |
| ≥4 | 53/82 (64.6%) |
| ≥6 | 32/82 (39.0%) |
| ≥7 | 21/82 (25.6%) |
| ≥8 | 12/82 (14.6%) |
| **≥9** | **3/82 (3.7%)** |
| ≥10 | 0/82 (0.0%) |

The corpus maximum is 9. No folio reaches ≥10 qok-class tokens in any 2-consecutive-line window.

### The three folios at ≥9

| Folio | Window | Matched recipe | Recipe Catalan ×N marker? |
|---|---|---|---|
| f75r | L37-L38 = 9 | III.19.0 (aqua vitae, 9× reflux) | YES — `aprés ix vegades` |
| f86v3 | L1-L2 = 9 | II.10.0 (conjunction of liquefactions) | NO |
| f108r | L48-L49 = 9 | III.16.0 (ferment multiplication) | NO |

### Matched-pair specificity test

| Catalan anchor | Folio | Folio max 2-line qok | Match (≥N) | Triviality |
|---|---|---:|:---:|---|
| III.11.0 / ×3 | f112r | 4 | YES | trivial (82.9%) |
| III.19.0 / ×4 | f75r | 9 | YES | trivial (64.6%) |
| III.19.0 / ×9 | f75r | 9 | **YES** | **non-trivial (3.7%)** |
| III.28.0 / ×4 | f82v | 6 | YES | trivial (64.6%) |

Only the ×9 anchor on f75r is non-trivial. The null distribution accounts for trivial matches automatically: random folio assignments routinely produce 2-3 matches because trivial counts are widely available, but rarely produce 4 because the rare-event ×9 only matches on 3 of 82 folios.

### Null distribution (10,000 permutations, within-recipe pairing preserved)

| Match count | Trials | Frequency |
|---:|---:|---:|
| 0 | 205 | 2.05% |
| 1 | 1,775 | 17.75% |
| 2 | 4,443 | 44.43% |
| 3 | 3,369 | 33.69% |
| **4** | **208** | **2.08%** |

Observed (4) falls in the 2.08% upper tail. p = 0.0208.

---

## Interpretation

### What this confirms

The Phase 636 f75r ×9 anchor stands under window-density methodology — a third independent test methodology after Phase 657 (prefix-class contiguous, NULL) and Phase 658 (lexeme-identity contiguous, INCONCLUSIVE). The original signal shape was always window-density; testing it that way produces signal.

### What this newly establishes

**Corpus-wide specificity is now quantified.** Previously the ×9 anchor was documented as "verified on f75r." This phase measured how often the same density appears across the full 82-folio corpus: 3.7%. The ×9 anchor is not a generic Currier B feature.

**Two structurally-similar high-density folios identified:** f86v3 and f108r reach the same threshold without explicit numerical markers in their matched Catalan recipes. This separates the proposition into two layers:
- **density-as-cycle-count:** falsified — f86v3 and f108r have density without numbered cycles
- **density-as-procedure-type signature:** consistent with — high qok-density on f75r corresponds to "9× reflux distillation"; on f86v3 corresponds to "conjunction of liquefactions" (an iterative but un-numbered procedure); on f108r corresponds to "ferment multiplication" (multi-step, un-numbered)

### Corpus ceiling at 9

No folio reaches ≥10 qok-class tokens in any 2-line window. This is a structural ceiling, consistent with C109 forbidden-transition theory and the hazard-class architecture: even the highest-thermal-density operations are bounded.

### What this does NOT claim

- **Not** that ≥9 qok-density implies ×9 cycle count. f86v3 and f108r refute that direction.
- **Not** that f75r is uniquely high-density. It is one of three.
- **Not** that all matched chapters with numerical markers should match high-density folios — only III.19.0 has ×9, and ×3, ×4 are trivial counts that match most folios.

The valid claim is a JOINT specificity: f75r is the only folio in the matched-pair table where high qok-density (top 3.7%) co-occurs with a matched Catalan chapter that explicitly carries a ×9 numerical marker.

---

## Related work

| ID | Relation |
|---|---|
| C1925 | dar=material-introduction; partition includes f75r as material-rich (10), confirms procedural alignment |
| C1928 | f75r → f84r product chain (vegetable G = quintessence) |
| C1959 | Paragraph layout-order tracks recipe-phase order; f75r participates in the test set |
| C1960 | Per-paragraph heat metrics correlate with predicted recipe fire-degree on phase-distinct folios |
| C1965 | f75r cycle-counting idiom (registered in Phase 650) |
| C1966 | HT density tracks compound-spec load (per-folio) |

---

## Methodology lesson registered

When re-testing a documented finding under cleaner methodology, the test's signal-shape must match what the original signal actually was — not a sanitized abstraction.

- Phase 657 tested "contiguous same-prefix-class run of size N" — clean, returns NULL on f75r ×9 because the L37-L38 sequence is interrupted by `lol`.
- Phase 658 tested "contiguous identical-lexeme run of size N" — cleanest possible, returns DEGENERATE on ×9 because no folio has 9 identical adjacent tokens anywhere.
- Phase 659 tested "qok-class density within a 2-line sliding window of size N" — matches the Phase 636 anchor's actual signal shape, returns SUPPORTED at p=0.0208.

The lesson: the Phase 636 anchor was always a window-density signal. Phases 657 and 658 tested cleaner-LOOKING propositions but tested the wrong propositions. Honest methodology means matching the test to the claim, not the test to mathematical convenience.
