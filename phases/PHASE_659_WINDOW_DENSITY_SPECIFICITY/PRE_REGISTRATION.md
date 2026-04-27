# Phase 659 — Pre-Registration

**Locked:** 2026-04-26
**Type:** Confirmatory hypothesis test
**Prior:** 657 (contiguous prefix-class) NULL; 658 (contiguous lexeme) INCONCLUSIVE for ×4 only.

---

## Why this exists

Both Phase 657 and Phase 658 tested **contiguous-cluster** interpretations of the Phase 636 anchors. Both ruled out the ×9 anchor at zero folios because no folio has either a contiguous size-9 prefix-class run or a contiguous size-9 lexeme run.

The original Phase 636 ×9 claim was *not* a contiguous run. It was "9 qok-class tokens across L37-L38" — a window-density count. This phase tests whether that density-within-window pattern is folio-specific.

---

## Hypothesis

**H:** SISMEL Catalan REPETITION counts correspond to qok-class token density within a fixed line-window on their matched VMS folio at higher rate than random.

**Specifically for ×9:** f75r is the only Currier B folio with ≥9 qok-class tokens within any 2-consecutive-line window.

**H₀:** Window-density correspondence is independent of recipe-folio match.

---

## Locked decisions

### 1. Window definition

A "qok-density window" of size W on a folio is any sliding window of W consecutive lines on that folio. The qok-class token count within the window is the number of tokens in those W lines whose `word.startswith('qok')`.

Per pre-reg discipline: W locked at **2 lines** (matches the original L37-L38 anchor span). No other window sizes are tested in this phase.

### 2. Test statistic

For each Catalan numerical anchor (subrecipe S, count N):
- Match = "matched folio has at least one 2-line window with ≥N qok-class tokens"

This is an **inclusive (≥)** rule, same as Phase 658.

### 3. Inputs (locked)

- `phases/PHASE_657_CYCLE_ANCHOR_ALIGNMENT/results/NUMERICAL_ANCHORS.json` (8 items)
- All Currier B tokens via `scripts.voynich.Transcript().currier_b()`

### 4. Matched-pair table

Identical to Phase 657/658.

### 5. Null distribution

10,000 random shuffles. Within-recipe pairing preserved.

### 6. Triviality check

For each test count N, fraction of folios with ≥N qok-class tokens in any 2-line window. >50% → trivial.

### 7. Over-determination check (load-bearing)

**Q1:** Is f75r the only Currier B folio with ≥9 qok-class tokens in some 2-line window?
**Q2:** Is f75r the only folio with ≥4 qok-class tokens in some 2-line window? (likely trivial, reported only)

The size-≥9 question is the genuine test. If f75r is uniquely ≥9, it's a categorical specificity result.

### 8. Verdicts

| Verdict | Criterion |
|---|---|
| SUPPORTED | T1 non-trivial matches/total ≥ 2/3 AND p ≤ 0.05; OR T3-Q1 confirms uniqueness |
| DIRECTIONAL | T1 non-trivial matches/total ≥ 1/3 AND p ≤ 0.20 |
| INCONCLUSIVE | matches > 0 but doesn't reach DIRECTIONAL |
| FALSIFIED | matches = 0 |

T3-Q1 uniqueness alone is sufficient for SUPPORTED on the ×9 anchor specifically, even if T1 is INCONCLUSIVE — the over-determination check is categorical.

### 9. What this phase does NOT do

- Not test any window size other than W=2.
- Not relax the qok-class definition (must be `word.startswith('qok')`).
- Not include other prefix classes — qok specifically.
- Not allow window stride > 1.

---

## Honest expectation

The window-density count of qok-class tokens in 2-line windows across all 82 Currier B folios will produce a distribution. The question is whether f75r's L37-L38 window (which I expect to produce 9, matching the Phase 636 anchor) is the maximum or near-maximum, and how many other folios reach 9.

If many folios reach 9 in some 2-line window, the ×9 anchor is not folio-specific.

If only f75r reaches 9, that's a categorical specificity result that cleanly confirms the original Phase 636 anchor under a third independent methodology — and one that does NOT just re-confirm the documented ×4 fact.

This is the genuine test. Outcome unknown.
