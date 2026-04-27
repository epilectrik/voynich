# Phase 658 — Findings

**Verdict (T1 matched-pair specificity):** INCONCLUSIVE (1/4, p=0.11)
**Verdict (T3 f75r over-determination):** DEGENERATE on the conjoined question (size>=9 corpus-vacuous); size>=4 alone confirms f75r uniqueness.

---

## Honest summary

This phase **re-confirms** a previously-documented fact under cleaner methodology. It does **not** produce new constraints or new alignments.

The Phase 636 memory note states the f75r ×4 anchor is "4-qokedy identical-token run on L13 (corpus-singular in Currier B)." Phase 658 verifies that statement under a pre-registered, exact-string-match methodology against all 23,096 Currier B tokens:

- Total size-≥4 lexeme-identity clusters in the corpus: **1**
- That single cluster: `qokedy × 4` on f75r L13
- Folio coverage: 1/82 = 1.2%
- Catalan III.19.0 (the matched chapter) explicit count: ×4 ("per quatre vegades")

This is **reproducibility hygiene**, not a new finding. The verbal "corpus-singular" is now a quantitative 1.2% bound with a reproducible script.

---

## T1: Matched-pair specificity (>= rule)

| Catalan anchor | Folio | Folio max lexeme cluster | Match (size>=N) |
|---|---|:---:|:---:|
| III.11.0 / ×3 | f112r | 2 | NO |
| III.19.0 / ×4 | f75r | 4 | **YES** |
| III.19.0 / ×9 | f75r | 4 | NO |
| III.28.0 / ×4 | f82v | 2 | NO |

Observed: 1/4. Null mean: 0.11. **p = 0.11**.

The N=4 result is the only match, and the p-value reflects that even a single match against an extremely-rare cluster size (1/82 folios) doesn't cross α=0.05 with N=4 test items.

## T2: Triviality

| N | folio coverage | status |
|---|---|---|
| 3 | 7/82 (8.5%) | specific |
| 4 | 1/82 (1.2%) | highly specific |
| 6 | 0/82 | corpus-vacuous |
| 7 | 0/82 | corpus-vacuous |
| 9 | 0/82 | corpus-vacuous |

Lexeme-identity is corpus-vacuous for N≥6. This is a structural result: Currier B does not produce identical-token runs of size ≥6 anywhere.

## T3: f75r over-determination

Pre-registered question: is f75r the only folio with both size-≥4 AND size-≥9 lexeme clusters?

- size≥9 cluster: 0 folios in corpus → DEGENERATE on conjoined question
- size≥4 cluster: 1 folio (f75r) → unique
- The unique cluster is `qokedy` specifically, not any other lexeme

The conjoined check cannot be answered (vacuous), but the disjunctive size-≥4 check confirms f75r uniqueness.

---

## What this changes

- **Nothing in the constraint system.** No new constraint, no tier change.
- **Memory note updated below** to reference Phase 658 as the verification source.
- **f75r ↔ III.19 stays CONFIRMED** at the original 5 levels.

## Memory note revision (recommended)

The "corpus-singular" claim in `f75r Crib Decode Session` memory now has explicit provenance:

> × 4 anchor: 4-qokedy identical-token run on L13 (corpus-singular in Currier B; verified Phase 658 = 1/82 folios, the only size-≥4 lexeme-identity cluster in the entire 23,096-token Currier B corpus).

---

## What remains untested

The original Phase 636 ×9 anchor was *not* a contiguous run — it was "9 qok-class tokens across L37-L38" (a window-density claim). Both Phase 657 (prefix-class contiguous) and Phase 658 (lexeme contiguous) ruled this out at zero folios. A **window-density specificity test** has not been run.

If f75r is uniquely the only Currier B folio with ≥9 qok-class tokens within a 2-line window, that would be a genuine specificity result — different from the ×4 anchor (which is a literal identical-token run), different from contiguous-cluster tests (which both ran null), and different from what's currently documented.

This is the next testable proposition.
