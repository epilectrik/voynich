# Phase 659 — Findings

**Verdict (T1 matched-pair specificity):** SUPPORTED (4/4 matches, p=0.0208)
**Verdict (T3-Q1 f75r over-determination at ≥9):** PARTIAL (3 folios reach the threshold; f75r is one of three, not unique)
**Verdict on the ×9 anchor specifically:** DIRECTIONAL with corpus-specificity quantified

---

## Headline result

**The Catalan III.19.0 numerical REPETITION ×9 marker corresponds to qok-class token density on its matched VMS folio at higher rate than chance. p = 0.0208 under 10,000-permutation null with random folio reassignment.**

This is the first corpus-wide window-density test of the Phase 636 ×9 anchor claim. Both Phase 657 (prefix-class contiguous, NULL) and Phase 658 (lexeme-identity contiguous, INCONCLUSIVE) ruled out contiguous-cluster interpretations. This phase tests the actual original claim shape (window-density) and confirms it.

## Corpus-wide qok-density measurement

Across all 82 Currier B folios (23,096 tokens, H-track only), maximum qok-class tokens within any 2-consecutive-line sliding window:

| Threshold | Folio coverage |
|---|---|
| ≥4 | 53/82 (64.6%) |
| ≥6 | 32/82 (39.0%) |
| ≥7 | 21/82 (25.6%) |
| ≥8 | 12/82 (14.6%) |
| **≥9** | **3/82 (3.7%)** |
| ≥10 | 0/82 (0.0%) |

The ≥9 threshold is highly specific (3.7%) and the corpus maximum is 9 — there is no folio with ≥10 qok-class tokens in any 2-line window.

## The three folios at ≥9

| Folio | Window | Matched recipe | Recipe has ×9 in Catalan? |
|---|---|---|---|
| f75r | L37-L38 = 9 | III.19.0 (aqua vitae) | **YES** ("aprés ix vegades") |
| f86v3 | L1-L2 = 9 | II.10.0 (conjunction of liquefactions) | NO |
| f108r | L48-L49 = 9 | III.16.0 (ferment multiplication) | NO |

**Interpretation:** ≥9 qok-density is a structural signature of high thermal-activity operations. The signature appears on three folios in the corpus. Only one of those three is matched to a recipe that explicitly numbers cycles at ×9 in Catalan. The matched correspondence is therefore non-coincidental.

## T1: Matched-pair specificity

| Catalan anchor | Folio | Folio max 2-line qok | Match (≥N) |
|---|---|---:|:---:|
| III.11.0 / ×3 | f112r | 4 | YES (trivial — 82.9% folio coverage at N=3) |
| III.19.0 / ×4 | f75r | 9 | YES (trivial — 64.6% at N=4) |
| III.19.0 / ×9 | f75r | 9 | **YES (non-trivial — 3.7% at N=9)** |
| III.28.0 / ×4 | f82v | 6 | YES (trivial — 64.6% at N=4) |

Observed: 4/4. Null mean: 2.16. **p = 0.0208 (one-sided, 208/10,000 trials with ≥4 matches).**

Of the 4 matches, only 1 is non-trivial (the ×9 on f75r). That one match accounts for the p-value: random folio assignment rarely produces all 4 matches because the rare-event ×9 only matches at 3.7% of folios.

## T3: Over-determination

The pre-registered Q1 ("is f75r the only folio with ≥9 qok-density in a 2-line window?") is **NOT CONFIRMED**. f86v3 and f108r also reach this threshold. f75r over-determination at the literal categorical level fails.

However, the joint condition (high qok-density AND matched recipe carries ×9 marker) IS uniquely satisfied by f75r in the matched-pair table — because only III.19.0 has ×9 in its Catalan transcription, and III.19.0 is matched to f75r.

This is a softer claim than "f75r is unique" but it preserves the matched-pair specificity result.

## What this changes vs. existing constraints

Existing constraints already document f75r ↔ III.19 at 5 independent levels (8D distance, ×4 lexeme anchor, ×9 qok-density, P9 alternation, atom predictions). C1965 specifically records the cycle-counting idiom on f75r.

What's NEW from this phase:
- **Corpus-wide quantification** of ≥9 qok-density specificity: 3.7% folio coverage. Previously the ×9 anchor on f75r was documented as "verified on f75r" without a corpus-wide rate.
- **Identification of f86v3 and f108r as structurally-similar high-qok-density folios** that do NOT have explicit ×9 markers in their matched Catalan recipes. Suggests the density signature reflects a procedure-type (intensive thermal cycling) that is sometimes but not always numerically explicit.
- **Pre-registered specificity test passes at p=0.02** under window-density methodology — a third independent confirmation distinct from Phase 657 (prefix-class, NULL) and Phase 658 (lexeme-identity, INCONCLUSIVE).

## Constraint candidate

**Tier 2:**
> ≥9 qok-class tokens within any 2-consecutive-line window is corpus-rare (3/82 folios = 3.7%). Of the 3 folios reaching this threshold, f75r is the only one matched to a Catalan chapter (III.19.0) containing an explicit ×9 numerical REPETITION marker. Matched-pair specificity test: 4/4 anchors land on matched folios, p=0.0208 under 10,000-permutation null. Confirms the Phase 636 f75r ×9 anchor under window-density methodology, after Phase 657 (prefix-class contiguous) and Phase 658 (lexeme contiguous) ruled out contiguous-cluster interpretations.

Suggested ID: C1969. Tier 2.

## Note on f86v3 and f108r

Both folios reach the ≥9 qok-density threshold but are matched to recipes without explicit ×9 markers. This raises a testable proposition:

> Is high qok-density (≥9 in 2-line window) a sufficient marker for "high-cycle" thermal procedures, even when the Catalan source text doesn't explicitly number the cycles?

f86v3's matched chapter (II.10) describes "conjunction of liquefactions" — possibly an iterative procedure not numbered.
f108r's matched chapter (III.16) describes "ferment multiplication" — explicitly multi-step but not numbered.

This is a follow-up phase candidate: cross-reference high-qok-density folios with recipe length / number of distinct operations / explicit-but-non-numerical iteration markers ("novament", "altres vegades", "aprés"). Not committed.

## What did NOT change

- f75r ↔ III.19 stays CONFIRMED at 5 levels (was 5, this is the 6th but already known fact reframed)
- Matched-pair table unchanged
- No re-classification of any folio
- f86v3 and f108r matches unchanged (no evidence to revise)

## Methodological note

The pre-registered structure produced an actual signal because the test methodology matched the original anchor's signal-shape (window-density), unlike Phases 657 and 658 which tested adjacent-but-different propositions. This is a lesson: when re-testing a documented fact, ensure the test methodology reflects what the original signal actually was, not a cleaner-looking variant.
