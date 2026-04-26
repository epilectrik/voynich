# Phase 658 — Pre-Registration

**Locked:** 2026-04-26 (commit hash to be recorded post-commit)
**Type:** Confirmatory hypothesis test
**Prior:** Phase 657 returned NULL under prefix-class cluster definition. This phase tests the **lexeme-identity** definition that more closely matches the original f75r anchor signal.

---

## Why this exists

Phase 657 FINDINGS exposed a methodological gap: the f75r ×4 anchor in
the Phase 636 confirmation was a run of **4 identical `qokedy` tokens**
on L13 (corpus-singular per memory). Phase 657 tested same-prefix-class
clusters and ruled out that reading. The lexeme-identity reading — what
the original anchor actually was — remained untested.

This phase tests it.

---

## Hypothesis

**H:** SISMEL Catalan REPETITION connectives with explicit numerical counts
correspond to runs of N consecutive identical tokens (same `word`) on
their matched VMS folio at higher rate than random.

**H₀:** Lexeme-identity cluster correspondence is independent of the
recipe-folio match.

**Falsifiable:** If observed matches do not exceed null distribution at
p ≤ 0.05, claim rejected.

---

## Locked decisions (binding)

### 1. Lexeme-identity cluster definition

A lexeme-identity cluster of size N on a folio is:
- A **maximal consecutive run** of N tokens within a single line OR
  spanning at most 1 line break, where every token has the **identical
  `word` field** (case-sensitive, exact string match).
- Inclusion: N >= 2 (size-1 is trivially the whole corpus).

**Implementation:** scan token sequence per folio; advance `i` from start
to end; from each position, extend `j` while `token[j].word == token[i].word`
AND `lines_crossed <= 1`; if `j-i >= 2`, emit cluster of size `j-i`.

**Token filter:** Currier B, H-only, exclude labels, exclude uncertain
(via `Transcript.currier_b()` defaults).

### 2. Catalan-side input (already locked)

Reuse Phase 657 `results/NUMERICAL_ANCHORS.json` (8 items, N≥3). No
re-extraction.

### 3. Matched-pair table (locked, identical to Phase 657)

| Catalan chapter | Folio | Tier |
|---|---|---|
| III.19 | f75r | CONFIRMED |
| III.11 | f112r | supported |
| III.28 | f82v | supported |
| (II.17, II.20, III.17, III.29) | unmatched | negative control |

### 4. Test statistic

Match = "matched folio contains at least one lexeme-identity cluster of
size >= N" for the Catalan count N. Using **size >= N** (not exact),
because:
- A run of 4 identical tokens trivially contains a size-3 sub-run.
- The Catalan ×3 says "at least 3 times" semantically; we honor the
  inclusive reading here.
- This is the ONE deliberate divergence from Phase 657's exact-match
  rule, and it is locked here before any test runs.

**Observed matches:** count of (in-set primary anchor, matched folio)
pairs satisfying the rule.

### 5. Null distribution

10,000 random shuffles. Within-recipe pairing preserved (III.19's two
anchors land on the same randomly-chosen folio together). Without
replacement across chapters per trial.

p-value (one-sided): fraction with matches >= observed.

### 6. Triviality check

For each numerical count N in the test set, count how many of 82 folios
contain ≥1 lexeme cluster of size ≥ N. If ≥ 50% of folios match, that N
is TRIVIAL and the matched test for that N is degraded (does not count
toward SUPPORTED).

### 7. Over-determination check (locked, f75r)

Q: Is f75r the only Currier B folio with BOTH a lexeme-identity cluster
of size ≥ 4 AND ≥ 9?

(Note: under lexeme-identity, ×9 may be corpus-impossible in the same
way prefix-class ×9 was. We expect this and report transparently.)

If size-9 lexeme cluster doesn't exist anywhere, the over-determination
check is reported as **DEGENERATE** (the question is corpus-vacuous), not
as confirming or denying.

### 8. Verdicts

| Verdict | Criterion |
|---|---|
| SUPPORTED | non-trivial matches/total >= 2/3 AND p <= 0.05 |
| DIRECTIONAL | non-trivial matches/total >= 1/3 AND p <= 0.20 |
| INCONCLUSIVE | doesn't reach DIRECTIONAL but matches > 0 |
| FALSIFIED | matches = 0 |

### 9. What this phase does NOT do

- No fuzzy lexeme matching (`qokedy` vs `qokeedy` are distinct).
- No prefix-class counting (Phase 657 did that).
- No relaxation of the locked rules after seeing results.
- No additional test items beyond the 8 in NUMERICAL_ANCHORS.json.

---

## Honest expectation

The ×4 anchor is expected to match on f75r (4-qokedy run on L13 is
documented in memory as corpus-singular). The ×9 anchor is unlikely to
match anywhere — under lexeme-identity it would require 9 identical
tokens, which the corpus probably does not contain. III.28.0/×4 may or
may not match on f82v. III.11.0/×3 likely matches trivially.

If observed = 2/4 with N=9 corpus-vacuous and N=3 trivial, the
non-trivial matches reduce to 1/3 (the ×4 on f75r). That's
DIRECTIONAL at best, requires p ≤ 0.20.

The over-determination check is the load-bearing test: if f75r is
uniquely the only folio with a size-≥4 identical-token cluster of
`qokedy` specifically, that's a categorical specificity result.

If the test returns null on both T1 and T3, the conditional-grammar
approach to Catalan utilization is exhausted at this resolution and we
pivot.
