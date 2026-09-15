# PHASE_752 — Pre-registration: two discriminating tests on Layfield & Davis (2026b), "Singulion Structure and the Voynich Manuscript"

**Locked:** 2026-09-15, before any script was run.
**Target paper:** Layfield & Davis, *Digital Medievalist* 19 (2026), published 10 July 2026, DOI 10.4000/16k0a.
**Relation to prior registration:** `phases/PREREG_LAYFIELD_DAVIS_PAPER2/PRE_REGISTRATION.md` (locked 2026-06-08).
Preliminary scoring gave P3 REFUTED / P4 PARTIAL / P8 REFUTED / M2 REFUTED. The locked protocol
pre-commits: "REFUTED P3 or P4 ... treat as a real anomaly, not noise; run their claimed ordering
against our within-section permutation framework." Test 2 discharges that obligation. Test 1 is the
external-critique test named in conversation (A/B-interleaving confound on the herbal signal).

## Shared pipeline (mirrors their method where it matters, project filters where it doesn't)

- **Documents = pages** (folio sides). Text = H-track, placements starting with `P` or `R`, non-empty,
  no `*` tokens. `R` is included because f76r's paragraph text is tagged `R` in this transcript (page
  has no illustration). Labels and diagram placements excluded.
- **LSA:** TF-IDF on whitespace tokens, fit on ALL page documents of the manuscript; TruncatedSVD
  k = 75 (their stated k); cosine similarity between page vectors. Robustness: k = 50, k = 100, and raw
  TF-IDF cosine (no SVD). Primary verdicts read from k = 75.
- **Toolchain independence:** they use ZL 2a; we use the project's EVA H-track. Numbers will not match
  theirs to the third decimal; the PATTERN (conjoint ≈ confoliate > facing) is what must reproduce.
- **Collation (standard, voynich.nu):** Q1 f1–8; Q2 f9–16 (f12 missing); Q3 f17–24; Q4 f25–32;
  Q5 f33–40; Q6 f41–48; Q7 f49–56; Q13 f75–84; Q20 f103–116 (f109–110 missing; f116v blank).
  Bifolium k of a quire of n leaves = leaf k | leaf n+1−k.
- **Pair types (current nested binding):** confoliate = (Xr, Xv); facing = (Xv, next-present-leaf r)
  within the quire; conjoint = (Av, Br) for bifolium A|B (the singulion centre opening, per their
  Table 12 definition); robustness `conjoint_all` = mean of the 4 cross-leaf pairs.
  "Other" = within-quire page pairs that are none of the above and not on the same bifolium.

## Test 1 — Herbal A/B-interleaving confound (Q1–Q7)

**Claim under test:** the herbal "singulion signature" (conjoint > facing) is produced by
single-scribe bifolia + language-tracks-scribe, because facing pairs can cross an A/B boundary and
conjoint pairs never do (C239 A/B folio-disjoint).

Statistics (all at k = 75; permutation nulls = page-label shuffle WITHIN quire and WITHIN language
class, 10,000 shuffles, which preserves each page's language and destroys leaf/bifolium structure):
1. Replication: pooled mean conjoint − mean facing (all facing pairs). Per-quire table.
2. Confound size: mean facing(same-language) vs mean facing(cross-language).
3. Confound-controlled gap: mean conjoint − mean facing(same-language only); and the same gap in
   the pure-A quires Q1–Q3 where no confound is possible.
4. Residual bifolium effect: mean conjoint − mean other(same-language) with the shuffle null.
5. Length check: token counts by pair type; if pair-type medians differ by > 20 %, add a
   min-length-stratified re-run.

**Pre-registered verdicts**
- **CONFOUND-EXPLAINS** if (1) > 0 but (3) ≤ 0 or p ≥ 0.05 in both the same-language-facing
  restriction and the pure-A quires.
- **CONFOUND-PARTIAL** if (3) shrinks by ≥ 50 % relative to (1) but stays p < 0.05.
- **CONFOUND-DOES-NOT-EXPLAIN** if (3) retains ≥ 50 % of (1) at p < 0.05.
- Independently: **RESIDUAL-BIFOLIUM-EFFECT** if (4) > 0 at p < 0.05 — this would be a NEW
  bifolium-layer measurement (the constraint base has zero bifolium-level constraints), registrable
  only as a measurement ("pages on the same physical sheet share vocabulary beyond language"), not
  as a reading-order mechanism.
- **B-section arm (Q13, Q20, no language confound):** same statistic (4) with within-section
  shuffle null. Same registrability rule.

## Test 2 — Best-of-N null for the Q13 / Q20 reorderings

**Claim under test:** their reported improvements (Q13: facing 0.461 → 0.517, +12.1 %, best of 120;
Q20: 0.438 → 0.526, +20 %, best of 720) exceed what selection of the best permutation yields by chance.

Objective (their Table 14, reconstructed): bifolium read as Ar, Av, Br, Bv (lower folio first, no
flipping); **objective A** = mean similarity over the n−1 joins (Bv_i, Ar_{i+1}); **objective B** =
mean over joins + the n conjoint centre openings. "Current" baseline = mean facing score in the
current nested order (their choice); second baseline = objective A evaluated on the current bifolium
order. f116v is blank/absent: joins touching it score 0 (this reproduces their 720-permutation count,
which implies 103|116 was kept); robustness run drops 103|116 (5 bifolia, 120 perms).

Null 1 (primary): shuffle page labels within the section 5,000 times; recompute current, best-of-N,
improvement ratio each time; p = fraction of null improvements ≥ observed.
Null 2 (robustness): symmetric matrix refilled by resampling the section's off-diagonal similarities.

Cross-toolchain: score THEIR sequences in OUR space —
Q13 best: 77|82, 78|81, 75|84, 76|83, 79|80; Q13 second: 76|83, 77|82, 79|80, 75|84, 78|81;
Q20: 105|114, 104|115, 106|113, 107|112, 108|111, 103|116 — and report each sequence's percentile
rank among all permutations under objective A.

**Pre-registered verdicts**
- **BEST-OF-N ARTIFACT** if observed improvement has p ≥ 0.05 under Null 1 (per section).
  Consequence: P3/P4 stand; the paper's reordering claims are selection effects; no reconciliation
  needed with our flat within-section order results.
- **REAL ORDER SIGNAL** if p < 0.05 under Null 1. Consequence (pre-committed 2026-06-08): treat as a
  real anomaly; reconcile with C1839 / the flat Balneo–Stars order results; do NOT snap to prior.
- **CROSS-TOOLCHAIN SUPPORT** if their sequence ranks in the top 5 % of permutations in our space;
  otherwise **NOT REPRODUCED** (their sequence is toolchain-specific).

## What this phase does NOT claim
No verdict on whether the manuscript was physically produced as singulions (that is codicology:
single-scribe bifolia, gutter-crossing illustration). Only: (a) whether the herbal text signal
survives the language confound, and (b) whether the reorderings beat chance.
