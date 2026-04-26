# C1962 Out-of-Sample Validation: Pending Candidates

**Date generated:** 2026-04-26
**Status:** Exploratory — narrative concordance checked, not statistically validated
**Future work:** Run Phase 628 8D matching infrastructure on these candidates

---

## What's here

`c1962_candidate_search.py` — script that identifies unmatched Currier B folios with strong o-prefix dominance (top rel-enrichment ≥ +0.5) and matches them against unmatched PL Testamentum chapters using crude keyword classification.

`c1962_out_of_sample_candidates.json` — 37 candidate unmatched folios with their dominant o-prefix and 153 unmatched chapters classified by content keywords.

## Why pending

The keyword-based classification of chapter content is too crude for proper out-of-sample validation. Multiple folios within a channel-class point to the same top chapters because the keyword scoring doesn't discriminate within-class. Narrative concordance is suggestive but not statistically confirmable.

A proper out-of-sample test requires:
1. Running Phase 628's 8D feature-space matching on these 37 candidate folios against the 153 unmatched chapters
2. Computing actual structural distance (Euclidean, with locked feature weights)
3. Verifying C1962's predicted matches survive 8D scoring at significance threshold

Estimated effort: half-day research phase. Not run in this exploratory pass.

## What was learned (narrative-level)

For each channel-class, top-3 candidate matches show consistent themes:

- **ol-dominant folios** (vessel-content state): top matches are recipes about multi-vessel coordination (introducing form to pearls, liquefaction, water unity)
- **ot-dominant folios** (transfer/iteration): top matches are iteration/transfer recipes (mercury inquisition, washing operation, multi-element preparation)
- **or-dominant folios** (outcome/completion): top matches are outcome/tincture recipes (stone colors, universal art summary, tincture branches)
- **ok-dominant folios** (thermal regime): top matches are fire-management recipes (most common chapter class — 56% of unmatched chapters)

The narrative concordance is real. The statistical test isn't yet rigorous enough to register.

## Use case for future work

When a future phase wants to do proper C1962 out-of-sample validation, start here:
1. Take the 37 candidate folios from this list
2. Run them through Phase 628 8D matching against the 153 unmatched chapters
3. Pre-register predictions: each X-dominant folio should match an X-content chapter
4. Score directional concordance with permutation null
