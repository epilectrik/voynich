# Phase 657: Numerical Cycle-Anchor Specificity Test (Stage B of Catalan utilization)

**Phase:** 657
**Status:** COMPLETE — VERDICT NULL (T1 INCONCLUSIVE; T3 NOT CONFIRMED)
**Started:** 2026-04-26
**Depends on:** Phase 656 (CONNECTIVE_CORPUS.json)

## Result summary

- **T1 matched-pair specificity:** 2/4 raw matches, p=0.49. After triviality filter (N=3 trivial at 78% folio coverage): 1/3 non-trivial matches. INCONCLUSIVE.
- **T3 f75r over-determination:** NOT CONFIRMED. Under the locked prefix-class cluster definition, f75r has neither a size-4 nor a size-9 qok-cluster. The L13 run is size 5 (qokain shares qok class); the L37-L38 sequence splits at `lol`.
- **Striking byproduct:** N=9 is corpus-impossible — no Currier B folio has any same-prefix-class cluster of size 9 (max=7). Any Catalan ×9 must be encoded outside single-cluster mechanisms.
- **No constraint changes.** f75r ↔ III.19 remains CONFIRMED at the original 5 independent levels.

See `results/FINDINGS.md` for full detail and methodological lessons.

---

## Why this exists

Phase 656 Stage A extracted 1012 connective instances from SISMEL Catalan
Practica + Mercuriorum. Of the 59 REPETITION-class instances, 10 carry an
explicit numerical count (`per quatre vegades`, `aprés ix vegades`,
`per .vii. vegades`, etc.). These are the cleanest possible
structural alignment signals: a Catalan recipe says "do this N times,"
and we can ask whether the matched VMS folio shows a token-class
cluster of size N.

Two of these ten Catalan numerical REPETITION markers fall in chapters
that are CONFIRMED-matched to specific folios:
- **III.19.0** (Catalan: `per quatre vegades` and `aprés ix vegades`)
  matches **f75r** (VMS: 4-token `qokedy` run on L13, 9-token qok-class
  cluster across L37-L38). This is the over-determined f75r anchor that
  Phase 636 confirmed.
- **III.11.0** (Catalan: `per .iii. vegades`) matches **f112r**
  (red mercury cohobation, per Phase 636 supported tier).

The remaining 8 numerical-REPETITION instances are in unmatched chapters
and become **negative controls**: their counts can be searched across
all 83 Currier B folios to test whether the cycle-cluster correspondence
is folio-specific or trivial.

This is the structural alignment test crazy-expert flagged as
decipherment-class — a sixth independent confirmation on f75r in
particular, and a falsifiable specificity test more broadly.

---

## What this phase does NOT claim to do

- **Not a single-folio position alignment.** The Catalan ×4 and ×9
  anchors are both clustered at the end of III.19.0 (chars 489 and 532
  of 546, ~90%+ relative position). The VMS ×4 and ×9 anchors are in
  different paragraphs (L13 vs L37-L38). The Catalan III.19.0 is a
  compressed summary; f75r expands the procedure across 9 paragraphs.
  Naive position-correspondence would fail. The cycle-count anchor test
  is robust to this expansion.

- **Not a translation claim.** Per C171, atom glosses describe operational
  function not natural-language plaintext. This phase tests whether
  numerical cycle markers correspond between the two notations — that
  is structural, not semantic.

- **Not a test of all Catalan connectives.** Only the numerical-REPETITION
  subset (10 instances). The remaining 49 REPETITION instances and the
  953 non-REPETITION connectives are not tested in this phase.

---

## Files

```
phases/PHASE_657_CYCLE_ANCHOR_ALIGNMENT/
  INDEX.md                          ← this file
  PRE_REGISTRATION.md               ← locked methodology + locked anchor extractions
  scripts/
    s1_extract_numerical_anchors.py ← Catalan numerical-count extractor
    s2_enumerate_vms_clusters.py    ← VMS cycle-cluster enumerator
    s3_run_specificity_test.py      ← matched vs random null distribution
  results/
    NUMERICAL_ANCHORS.json          ← Catalan-side counts (locked input to s3)
    VMS_CYCLE_CLUSTERS.json         ← VMS-side clusters per folio (locked input to s3)
    SPECIFICITY_TEST.json           ← test outcome (post-hoc, separate commit)
```

---

## Constraint expectations

| Outcome | Expected constraint |
|---|---|
| SUPPORTED (specificity p ≤ 0.05) | C-XXXX (Tier 2): Catalan numerical REPETITION counts correspond to VMS cycle-cluster sizes on matched folios at rate above chance |
| INCONCLUSIVE (p > 0.05) | Negative result registered descriptively; no constraint |
| FALSIFIED (matched-pair correspondence rate equal to or below random) | C-XXXX (Tier 1): Numerical cycle-count correspondence is not folio-specific |

If SUPPORTED on f75r specifically (the over-determined case), this becomes
the sixth independent confirmation of f75r ↔ III.19, alongside 8D distance,
×4 anchor, ×9 anchor, P9 alternation, atom predictions.
