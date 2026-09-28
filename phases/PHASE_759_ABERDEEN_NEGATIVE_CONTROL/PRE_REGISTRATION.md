# PHASE_759 — PHASE_752 v2 step 1: pipeline negative control on the Aberdeen Bestiary (pre-registration)

**Locked:** 2026-09-27, before any analysis code for this phase was written or run. Design audited by the lean-expert
(verdict LOCK WITH CHANGES; every requested change is incorporated below).
**Origin:** PHASE_752 audit (locked registration gate) and STRATEGIC_REVIEW_2026-09-27 §3 #7 / §9 (Malta video due
2026-11-09): "(1) pipeline negative control on the Aberdeen Bestiary (known collation, continuous text), prediction
locked; (2) second transcription track; (3) side-of-flat-sheet contrast".
**Question:** does the PHASE_752 similarity pipeline, with the re-pairing null and distance/length residualization,
report a same-sheet (bifolium) effect in a normal codex whose text runs continuously page to page? If it does — or if
it could not have detected an effect of the size seen in the Voynich strata — the Voynich bifolium results cannot be
registered from this pipeline.
**Assumption (production, not statistics):** Aberdeen was copied in gathering order, as a normal codex. This is
standard codicology and is not tested here.
**Change control:** after lock nothing below may change without a new phase number.

## Data
- **Aberdeen:** `sources/aberdeen_bestiary/aberdeen_pages.json` (University of Aberdeen digital edition, accessed
  2026-09-27) and `collation.json` (James's formula read with the site's quire and leaf marks; quire H undetermined and
  excluded from every stratum, even if later resolved). Documents: `latin_norm`. **Pages with < 20 words are absent**
  (blank leaves and full-page pictures). f45r (quire G) has no transcription on the site and is absent: leaf 45
  contributes 2 page pairs instead of 4 to its sheet, identically in the real matching and the null. The TF-IDF/SVD fit
  uses all Aberdeen text pages, including the lapidary (quires N end, O, P).
- **Voynich (comparison; nothing is registered here):** PHASE_752 v1 page documents (H track, placements P + R,
  uncertain excluded), strata herbal pure-A Q1–Q3, Q13, Q20, v1 collation and missing leaves, same < 20-word rule.

## Pipeline (identical to PHASE_752 v1)
TF-IDF (token pattern `\S+`) fit on all pages of the manuscript, TruncatedSVD k = 75 (primary; seed 759), cosine
similarity. Robustness: k = 50, 100 and raw TF-IDF cosine.

## Pair types and distances (within a quire)
- **Sheet pairs:** all page pairs across the two leaves of a conjugate pair (≤ 4 per sheet). Singletons are excluded
  from the re-pairing.
- **Facing:** (verso of leaf i, recto of the next surviving leaf), consecutive slots only; the centre opening (also a
  sheet pair) is excluded from facing.
- **Other:** all remaining cross-leaf page pairs (never sheet pairs).
- **Leaf distance** d = |slot_A − slot_B| (full slot scheme, wanting slots counted). **Page distance** = |p_A − p_B| with
  page position p = 2·(slot − 1) + (0 for recto, 1 for verso).

## Statistics
- **Residual model (primary):** OLS over all cross-leaf page pairs of the stratum: similarity ~ log(page distance) +
  1[page distance = 1] + log(min words) + log(max words) + quire fixed effects. It is fit without reference to sheet
  labels, so the re-pairing null stays exact. The v1-style linear-leaf-distance model is reported as a diagnostic only.
- **T_sheet:** mean residual over the real sheet pairs. **Re-pairing null:** within each quire, the leaves that belong
  to conjugate pairs are re-paired by a uniformly random perfect matching (slots, leaf order, pages and the fitted
  residuals fixed; only which leaves share a sheet changes); 10,000 joint draws across the stratum (seed 759).
  Upper-tail p_up = (1 + #{T_null ≥ T_sheet}) / 10,001; lower-tail p_low likewise. Per-quire exact p over all
  matchings is reported (floor 1/105; cannot decide alone).
- **T_strat:** within each quire and each leaf distance d ∈ {1, 3, 5} (d = 7 dropped: it contains only the sheet), the
  mean raw similarity of sheet page pairs minus the mean raw similarity of non-sheet cross-leaf page pairs at the same
  d; averaged over (quire, d) cells weighted by sheet page pairs. Null: within each (quire, d) cell, the sheet label is
  moved to a uniformly random leaf pair at that distance; 10,000 draws (seed 759); p_up and p_low.
- **T_face (sanity gate, not a power check):** mean raw similarity of facing pairs minus mean raw similarity of other
  pairs; null: page-label permutation within quire, 10,000 draws; one-sided.
- **Units:** effects are also expressed in per-pair residual-SD units (residual SD of the primary model).
- **Power (MDE):** MDE80 = (1.645 + 0.84) · SD of the null distribution, for T_sheet and for T_strat, in residual-SD
  units. Token-level plant (check that the SVD step does not distort a shift): for every real sheet, 10% of each page's
  length in tokens, drawn from the conjugate leaf's pages, is appended; TF-IDF/SVD rerun; the resulting T_sheet shift is
  reported next to the additive-shift expectation.
- **Length-matched runs:** for each Voynich stratum, each Aberdeen page is cut to a contiguous window whose length is
  drawn from that stratum's page-length distribution (whole page if shorter), 20 replicates (seeds 7590–7609); the
  full primary procedure is rerun; median p_up and median MDE80 are reported.

## Strata (Aberdeen)
- **Primary:** the six complete regular quires E, F, G, I, K, M (24 nested sheets).
- **Secondary:** all determined quires (A, B, C, D, E, F, G, I, K, L, M, N, O, P).

## Voynich comparison
Only if Aberdeen raises no MISSPECIFICATION flag: the same T_sheet and T_strat on the three Voynich strata, with effects
in residual-SD units. Registration still requires the second track (ZL3b) and the PHASE_752 gate (p < 0.01 in ≥ 2 of 3
strata); this phase does not register anything.

## Locked outcomes (primary stratum, k = 75)
1. **MISSPECIFICATION** — p_low < 0.05 for T_sheet or T_strat. The residual model produces a sign-flipped artifact on a
   continuous text; the model must be fixed (new phase) before any Voynich run; no Voynich comparison here.
2. **POSITIVE-CONTROL FAIL** — T_face p ≥ 0.01: the pipeline does not see page continuity; uninformative.
3. **NON-SPECIFIC** — p_up < 0.05 for T_sheet or T_strat (with T_face p < 0.01), or a length-matched median p_up < 0.01
   for either statistic in any of the three length regimes. No bifolium-level constraint may be registered from this
   pipeline; PHASE_752 is annotated.
4. **INCONCLUSIVE-UNDERPOWERED** — p_up ≥ 0.05 on both, but the Aberdeen MDE80 (primary, or the length-matched median
   MDE80 for the matching Voynich regime) exceeds the Voynich effect (residual-SD units) of any stratum that has
   re-pairing p < 0.01. Blocks Voynich registration, as NON-SPECIFIC does.
5. **SPECIFIC** — none of the above. Only statistics that pass here (T_sheet, T_strat) may be used at the Voynich gate.
Robustness (k = 50, 100, raw) and the secondary stratum are reported; a disagreement with the primary is named in the
reading but does not change the verdict.

## What this phase does not do
It does not test the side-of-flat-sheet contrast (v2 step 3), the second Voynich track (step 2), or any claim about how
the Voynich sheets were produced.
