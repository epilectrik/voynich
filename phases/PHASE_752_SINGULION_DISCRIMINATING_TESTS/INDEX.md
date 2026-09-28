# PHASE_752 — Singulion discriminating tests (Layfield & Davis 2026b)

> **v1 AUDIT CORRECTIONS (lean-expert, 2026-09-15; recorded 2026-09-27). Read before the sections below.**
> - **Withdrawn:** "in the herbal every currently adjacent same-language pair is elevated by about the same amount, whether or not it shares a sheet". Under the exhaustive **re-pairing null** (leaves, slots, adjacency, quire and language held fixed; only which leaves pair into sheets is randomized) the herbal pure-A sheet effect is significant at all four k (p≈0.001; Q13 p=0.0095; Q20 p=0.0033). Leaf-preserving slot permutation gives the double dissociation: conjugacy elevated in A and B; binding adjacency elevated in A only.
> - **Bug:** one facing pair per B section is also the innermost conjoint pair (f79v–f80r, f108v–f111r). Corrected facing−other is −0.004 (Q13) and −0.009 (Q20). Lacuna-spanning "facing" pairs (f108v–f111r across lost f109–110; f11v–f13r across lost f12) must be excluded.
> - The B arm is k-robust (run by the auditor); per-sheet sign tests do **not** reach 0.05 (Q13 4/4 testable, Q20 4/5); leave-one-sheet-out is robust. Distance and conjugacy can only be separated by residualization (the nested matching is the unique matching with distance multiset {1,3,…}); the outermost sheet is untestable for distance-adjusted statistics.
> - Best-of-N: use `p_best_ge_observed` (0.56 / 0.45 / 0.60) as primary. The current binding ranks 24/120 (Q13) and 41/120 (Q20 without 103|116) under the paper's own objective: not anomalously poor.
> - **Registration gate (locked):** register a bifolium-level constraint only if the re-pairing p<0.01 in ≥2 of 3 strata (herbal pure-A, Q13, Q20), on both transcription tracks (H + ZL3b), after length residualization.
> - **v2 plan (STRATEGIC_REVIEW_2026-09-27 §3 #7):** (1) pipeline negative control on the Aberdeen Bestiary (known collation, continuous text), prediction locked; (2) second track; (3) side-of-flat-sheet contrast (outer face Ar–Bv vs opposite-side pairs), sign-flip permutation within sheet, pooled across quires, central sheets and sheet 78|81 excluded.
> - **v2 step 1 DONE (PHASE_759, 2026-09-27): negative control SPECIFIC.** On the Aberdeen Bestiary the pipeline finds no sheet effect (residualized T_sheet p = 0.34, T_strat p = 0.44) but strong facing-page continuity (p = 0.0001), and detects a planted effect far smaller than the Voynich ones (MDE80 0.26 residual SD). With the residual model locked there (log page distance + contiguity + length + quire FE), the Voynich H-track results are: herbal pure-A p = 0.0007 (T_strat 0.004); Q13 p = 0.013; Q20 p = 0.017. Only one stratum meets p < 0.01, so the registration gate is not met on H even before step 2 (ZL3b).
> - The v1 verdicts on the paper stand: herbal conjoint>facing is A/B interleaving; the Q13/Q20 reorderings are best-of-N chance.


**Status:** v1 COMPLETE (verdicts on the paper stand); bifolium registration PENDING v2 per the locked gate above.
**Target:** Layfield & Davis, "Singulion Structure and the Voynich Manuscript," *Digital Medievalist* 19,
10 July 2026, DOI 10.4000/16k0a.
**Pre-registration:** `PRE_REGISTRATION.md`, locked and committed 2026-09-15 (b3588d6) before the run.
**Script:** `scripts/singulion_tests.py` (28 s). **Results:** `results/singulion_tests.json`.
**Pipeline:** page documents (H-track, placements P+R; f76r text is tagged R), TF-IDF fit on all 220 pages,
TruncatedSVD k=75 (their k), cosine. Robustness at k=50, k=100, raw TF-IDF. Seed 752.

## 0. Replication of their measurement (required before the controls mean anything)

Their pattern — conjoint ≈ confoliate > facing, opposite of normal codices — reproduces in our
independent toolchain (EVA H-track vs their ZL 2a):

| Unit | confoliate | facing | conjoint | other same-lang | theirs (conf / fac / conj) |
|---|---|---|---|---|---|
| Herbal Q1–Q7 pooled | 0.291 | 0.221 | 0.306 | 0.202 | 0.305 / 0.238 / 0.378 |
| Q13 | 0.836 | 0.722 | 0.828 | 0.718 | 0.530 / 0.460 / 0.603 |
| Q20 | 0.713 | 0.565 | 0.747 | 0.537 | 0.568 / 0.600 / 0.438 |

Absolute values differ (toolchain), the ordering does not. Length check: median min-token-count per
pair type within 7 % of each other in every arm; conjoint−other gap positive in all three
min-length tertiles. Length is not driving anything below.

## 1. Test 1 — Herbal A/B-interleaving confound

Null: page-label shuffle within quire AND within language class (10,000), which keeps every page's
language and destroys leaf/sheet structure.

| Statistic (k=75) | Herbal Q1–Q7 | Pure-A Q1–Q3 | Mixed Q4–Q7 |
|---|---|---|---|
| facing same-lang vs cross-lang | 0.275 vs 0.113 | — (all A) | 0.283 vs 0.113 |
| conjoint − facing (all) | +0.085, p=0.147 (null mean +0.061) | +0.041, p=0.134 | +0.117, p=0.332 (null mean +0.105) |
| conjoint − facing (same-lang only) | **+0.031, p=0.265** | **+0.041, p=0.134** | +0.020, p=0.492 |
| conjoint − other same-lang | +0.104, p=0.0002, z=+3.7 | +0.109, p=0.001 | +0.100, p=0.014 |
| confoliate − other same-lang | +0.089, p<0.0001, z=+4.6 | +0.065, p=0.003 | +0.105, p=0.0002 |

**Verdict (pre-registered): CONFOUND-EXPLAINS.** The conjoint>facing gap is not significant once
facing pairs are restricted to same-language pairs, and is not significant in the pure-A quires
where no confound exists. Under the language-preserving null the raw gap is *expected* to be
+0.061 (mixed quires: +0.105) from interleaving alone; the observed +0.085 is inside that null.
Robustness: k=100 and raw agree (p=0.175, 0.101); **k=50 dissents marginally** (conj−facing_same
+0.071, p=0.039). Primary verdict holds at the pre-registered k.

**Residual-bifolium clause fires but is not sheet-specific.** Conjoint pairs beat non-adjacent
same-language pages in the same quire (p=0.0002), BUT so do confoliate pairs (p<0.0001) and
same-language facing pairs (0.275 vs 0.202). In the herbal every *currently* adjacent same-language
pair is elevated by about the same amount, whether or not it shares a sheet. That is the known
Currier-A local coherence (C346 adjacent-entry coherence; C424 clustered ~3-entry runs), not a
singulion signature. Their herbal argument needs conjoint HIGH while facing is LOW; with language
controlled, facing is as high as conjoint.

Per-quire (k=75): conjoint>facing in Q1 (0.301 vs 0.252) and Q3 (0.358 vs 0.263), reversed in Q2
(0.259 vs 0.299) — same three-quire pattern as their Table 8 (Q2 reversed there too).

## 1b. B-section arm (Q13, Q20; no language confound; within-section shuffle null)

| Statistic (k=75) | Q13 | Q20 |
|---|---|---|
| conjoint − facing | +0.105, p=0.022 | +0.182, p=0.002 |
| conjoint − other | +0.110, p=0.007 | +0.210, p=0.0002 |
| confoliate − other | +0.118, p=0.0001 | +0.175, p<0.0001 |
| facing − other | +0.004 | +0.028 |
| conjoint_all (4 cross-leaf pairs) | 0.808 | 0.646 |

**In Currier B the singulion signature is real and toolchain-independent:** same-sheet pages
(and same-leaf pages) share vocabulary well beyond section baseline, while pages that face each
other in the *current* binding are no more similar than random pages of the section. All four
cross-leaf pairs of a sheet are elevated, not only the centre opening. n is small (5 and 6 sheets).

Interpretation limit (pre-registered): this is a **production-unit** measurement — each sheet
written as a unit, vocabulary drifting between sheets — and says nothing about reading order.
C1834 (paragraph = complete sequential reset) and C1839 (local coherence, no global gradient)
already deny the flowing-text premise that would turn "same sheet" into "read in sequence."

## 2. Test 2 — Best-of-N null for the Q13 / Q20 reorderings

Objective A = mean similarity over the n−1 joins (Bv_i, Ar_{i+1}) across all permutations;
"current" = mean facing score in the nested binding (their Table 14 choice). f116v absent → join
scores 0 (reproduces their 720 count). Null 1 = page-label shuffle within section (5,000);
Null 2 = exchangeable resample of the section's off-diagonal similarities.

| | Q13 (5 sheets, 120 perms) | Q20 (6 sheets, 720 perms) | Q20 drop 103\|116 |
|---|---|---|---|
| current facing | 0.722 | 0.565 | 0.594 |
| best objective A | 0.832 | 0.682 | 0.671 |
| **observed improvement** | **+15.2 %** | **+20.6 %** | +13.0 % |
| theirs (reported) | +12.1 % | +20 % | — |
| Null 1 improvement q05 / q50 / q95 | 3.5 / 14.0 / 24.8 % | 3.6 / 22.2 / 42.5 % | 4.3 / 22.6 / 43.3 % |
| **p (Null 1)** | **0.42** | **0.55** | 0.79 |
| p (Null 2) | 0.46 | 0.63 | 0.84 |
| p (best absolute score ≥ obs) | 0.56 | 0.45 | 0.60 |

Robustness (k=50 / k=100 / raw): Q13 p = 0.42 / 0.45 / 0.34; Q20 p = 0.64 / 0.61 / 0.52.

**Verdict (pre-registered): BEST-OF-N ARTIFACT, both sections.** Picking the best of 120 or 720
orderings of pages with NO ordering structure improves the mean join score by ~14 % (Q13) and
~22 % (Q20). Their +12.1 % and +20 % are at or below chance expectation. Consequence: P3/P4 of
the 2026-06-08 pre-registration STAND; no anomaly to reconcile with C1839 or the flat
Balneo/Stars within-section order results.

### Cross-toolchain scoring of THEIR sequences in OUR space

| Their sequence | rank in our space (k=75) | k=50 / k=100 / raw |
|---|---|---|
| Q20: 105\|114, 104\|115, 106\|113, 107\|112, 108\|111, 103\|116 | **1 / 720** | 1 / 1 / 1 |
| Q13 headline (+12.1 %): 77\|82, 78\|81, 75\|84, 76\|83, 79\|80 | 34 / 120 (top 28 %) | 37 / 30 / 32 |
| Q13 runner-up (+7.1 %): 76\|83, 77\|82, 79\|80, 75\|84, 78\|81 | **1 / 120** | 1 / 1 / 2 |

- **Q20: CROSS-TOOLCHAIN SUPPORT** for the sequence itself — a different transliteration and
  filtering produce the identical optimum. The page-pair similarity structure in Q20 is a stable
  property of the text. But its improvement is exactly what selection yields by chance, so a stable
  optimum is not evidence of an original order: every similarity matrix has a best ordering.
  Note the 103|116 mechanism: with 116v blank, any order not ending in 103|116 pays a zero join,
  which forces that sheet last in both toolchains ("ends with the blank 116v" is built in, not found).
- **Q13: headline NOT REPRODUCED** (rank 34/120). Their runner-up — the one they themselves
  floated as possibly "correct" on codicological grounds — is our optimum. A forum Held-Karp
  replication (ZL3b) produced a third order. Q13's optimum is toolchain-sensitive.

## 3. Scoring consequences for `phases/PREREG_LAYFIELD_DAVIS_PAPER2`

- P3 (Q13 no strong text-internal reordering) and P4 (Q20): the paper's claims exist but do not
  beat the best-of-N null → the pre-committed reconciliation is discharged in favour of P3/P4.
  Plain-reading scores (REFUTED / PARTIAL) remain as recorded; the *substantive* question is closed.
- M2 (conjugate-leaf similarity A-only) stays REFUTED, with the sharpening that in A it is generic
  adjacency coherence and in B it is sheet-specific.

## 4. Registrability

- Test 2 is null-driven (self-clearing). Test 1 herbal is a confound/null result (self-clearing).
- The **B-section sheet coherence** (§1b) is a NEW bifolium-layer measurement; the constraint base
  has zero bifolium-level constraints. Registrable as a Tier 2 *measurement* only ("Currier B pages
  on the same physical bifolium share vocabulary beyond section baseline; currently-facing pages do
  not"), null = within-section page-label shuffle. Not registered here: awaits the user's call and
  a lean-expert rigor pass (n = 5 and 6 sheets; single-transcriber; k-sensitivity documented).

## 5. What this phase does not say
Nothing about whether the sheets were physically produced/decorated before nesting (single-scribe
bifolia, gutter-crossing illustration are codicology, untouched). Only: the herbal text signal is
the A/B interleaving; the B text signal is real but production-level; the reorderings are chance.
