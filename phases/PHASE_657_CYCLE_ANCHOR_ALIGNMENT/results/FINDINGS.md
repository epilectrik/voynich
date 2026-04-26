# Phase 657 — Findings

**Verdict (T1 matched-pair specificity):** INCONCLUSIVE
**Verdict (T3 f75r over-determination):** NOT CONFIRMED

The pre-registered specificity test on cycle-anchor correspondence between
SISMEL Catalan numerical REPETITION counts and Voynich prefix-class clusters
returns a **clean null**. Under the locked cluster definition (same-prefix-class,
not same-lexeme), neither anchor on f75r matches its predicted Catalan
numerical count. The 4-anchor primary set yields 2/4 matches (1/3 after
triviality filter), with permutation p=0.49 — uninformative.

---

## T1: Matched-pair specificity

| Catalan anchor | Folio | Match | Note |
|---|---|---|---|
| III.11.0 / ×3 | f112r | YES | TRIVIAL (78% of folios have size-3 clusters) |
| III.19.0 / ×4 | f75r | NO | f75r L13 cluster is size 5, not 4 (`qokain` shares qok class) |
| III.19.0 / ×9 | f75r | NO | No size-9 cluster anywhere in corpus (max=7) |
| III.28.0 / ×4 | f82v | YES | Specific match (N=4 has 36.6% folio coverage) |

Observed: 2/4 matches. Null mean: 1.5. **p = 0.49**.

After triviality filter: **1/3 non-trivial matches**. Below DIRECTIONAL threshold.

---

## T2: Negative-control triviality

| Count N | Folios with cluster of size N | % | Status |
|---|---|---|---|
| 3 | 64/82 | 78.0% | TRIVIAL |
| 4 | 30/82 | 36.6% | specific |
| 6 | 3/82 | 3.7% | highly specific |
| 7 | 1/82 | 1.2% | uniquely specific |
| 9 | **0/82** | **0.0%** | **corpus-impossible** |

The N=9 row is the most striking finding of the phase: **no Currier B folio
contains a size-9 same-prefix-class cluster anywhere**. The maximum observed
cluster size in any prefix-class is 7 (qo-class, single instance).

This is itself a structural finding about Currier B grammar:
- C268 disfavored transitions and C109 forbidden-transition class structure
  evidently put a ceiling on how long a same-prefix run can persist.
- The hazard-class architecture predicts that monoculture clusters cannot
  exceed ~6-8 tokens before the grammar requires a transition.
- The Catalan `ix vegades` (×9) cannot be encoded as a single 9-cluster on
  any folio — it must be encoded across multiple cluster segments OR
  outside the cluster mechanism entirely.

This is a constraint on what a single-cluster decoding can accomplish.

---

## T3: f75r over-determination check

**Pre-registered question:** Is f75r the only Currier B folio with BOTH a
qok-cluster of size exactly 4 AND a qok-cluster of size exactly 9?

**Answer:** NEITHER cluster exists on f75r under the locked definition.
- f75r L13 qok-cluster is size **5** (the four `qokedy` plus one `qokain`).
- f75r L37-L38 has a size-3 (L37) and a size-5 (L38) qok-cluster, separated
  by an interrupting `lol` token. No size-9 contiguous cluster exists.

The over-determination check is NOT CONFIRMED at the pre-registered specificity.

---

## Descriptive observations (NOT in pre-registration)

These are exploratory, Tier 4 at most, NOT load-bearing:

1. **f75r is the only Currier B folio with two size-5 qok-clusters on the
   same folio.** Under the locked definition, no other folio achieves this
   pattern. (Source: VMS_CYCLE_CLUSTERS.json.)

2. **f75r ranks #2 in total qok-class tokens within clusters** (13), behind
   only f108r (18). f108r has not been matched to any specific recipe in
   the constraint system, so this ordering is descriptive only.

3. **The lexeme-identity reading remains intact.** The original f75r ×4
   anchor was 4 IDENTICAL `qokedy` tokens (corpus-singular per Phase 636).
   This is a different signal than "size-4 prefix-class cluster." The
   present phase locked the prefix-class definition; a separate phase
   could test the lexeme-identity definition cleanly.

These observations do not modify the pre-registered verdict.

---

## Methodological lessons

1. **Pre-registration worked exactly as designed.** The locked exact-match
   rule and the locked cluster definition (same-prefix-class) produced a
   clean null on a hypothesis that *might* have looked like signal under
   a more permissive reading. This is what pre-registration is for.

2. **The "×4" and "×9" anchors are LEXEME signals, not prefix-class signals.**
   The Phase 636 confirmation of f75r ↔ III.19 was based on identical-token
   runs (`qokedy qokedy qokedy qokedy`) and qok-class density across L37-L38.
   The present phase tested whether prefix-class clusters of EXACTLY those
   sizes would correspond. They don't — under prefix-class, the L13 run is
   size-5 and the L37-L38 sequence splits at `lol`.

3. **The N=9 corpus-impossible result is informative.** Currier B grammar
   does not produce single-cluster runs of size 9 in any prefix-class on
   any folio. Any Catalan recipe demanding "×9" must be encoded otherwise
   (multi-cluster, paragraph spans, or cross-folio).

---

## What this phase does NOT change

- **f75r ↔ III.19 match remains CONFIRMED** at the original 5 independent
  levels: 8D distance, lexeme-identity ×4 anchor, qok-density ×9 anchor,
  P9 alternation, atom predictions. This phase tested for a 6th
  independent confirmation and did not find one *under the locked cluster
  definition*.

- **No constraint downgraded.** C1925-C1956 (recipe-folio correspondences)
  are unaffected. The Catalan utilization roadmap is unchanged.

- **Phase 656 connective corpus is unaffected.** The Catalan-side
  extraction is sound; this phase tested one specific use of it and
  returned null.

---

## Possible follow-ups

(Not committed; offered for user discretion.)

A. **Phase 658 candidate: Lexeme-identity cluster test.** Re-run the
   cycle-anchor specificity with cluster definition = "same-lexeme run"
   (e.g., `qokedy qokedy qokedy qokedy` is a size-4 lexeme-cluster,
   distinct from `qokedy qokain` at size 1+1). This tests a different
   hypothesis that might align better with the f75r anchor signal. Pre-reg
   needed.

B. **Phase 659 candidate: Multi-segment ×9 alignment.** Test whether the
   sum of multiple smaller qok-clusters across L37-L38 (size 3 + size 5 = 8,
   or with the gap-bridging `lol`-treatment-as-marker = 9) matches the
   Catalan ×9. This requires a different cluster-aggregation rule.

C. **No follow-up.** The pre-registered test is null; the existing 5
   confirmations on f75r are sufficient; the Catalan utilization
   continues with verb extraction or color/state transitions instead.
