# PHASE_762 — Testamentum audit: triage, and do the specific recipe-matching patterns survive a matched control? (pre-registration)

**Locked:** 2026-09-28, before any analysis code for this phase was written or run. Design audited by the lean-expert
(verdict LOCK WITH CHANGES; every requested change is incorporated below).
**Origin:** human request (2026-09-28) to audit the Testamentum work — the recto/verso adjacent chapters, the section
mapping, the sublimation and count patterns. Background:
- **C2052 (PHASE_718, pre-registered):** the 8D matcher failed its Theophilus negative control. Theophilus metalwork
  chapters match the same Voynich folios, beat random shuffles (p = 0.0000), and concentrate in Section B. The
  pre-registered consequence ("demote C1882–C1956 from operational correspondence to structural attraction") and the
  experts' per-constraint triage criterion were never applied.
- **C2035:** folio token similarity is uncorrelated with matched-chapter content similarity (Mantel).
- **P726 / P727:** recipe-side features are English-translation-mediated; 6 of 27 exact counts did not reproduce.
- **Named flaw found while preparing this phase:** the permutation test behind C1887 (`shared_628.permutation_test`)
  computes the distance matrix once, optimizes an assignment, and compares it with random, unoptimized assignments on the
  same matrix. Any distance matrix passes; the test carries no evidence of correspondence.
**Change control:** after lock nothing below may change without a new phase number.

## Part A — triage (applied now, independently of Part B)
C2052's consequence was pre-registered and has already fired; it is not made to wait on new tests. Every constraint in
C1882–C1899, C1925–C1956, C1958–C1975, and C2034 is classified with C2052's criterion:
1. **Pure corpus fact** (a count or rarity measured on the text alone) — stays; annotated "not evidence for a Testamentum
   correspondence".
2. **Matcher measurement** (8D distances, stability, replication rates) — stays Tier 2 as structural similarity to
   medieval procedural text; annotated with C2052; C1887 and C1956 additionally annotated with the named flaw.
3. **Content claim** — a specific chapter → folio correspondence, a section/book mapping, a gloss or function inferred from
   matched folios, a count coincidence, a cold read — → Tier 3 if currently Tier 2; annotated. Count clauses that P727 failed
   to reproduce are marked void.
4. **Already retracted or demoted** — unchanged.
Constraints in the range that are internal (not about the recipe matching) are listed as out of scope. The triage table
is shown to the human before it is applied. **No Part-B result reinstates or exempts a content claim;** a SPECIFIC
pattern can only add a new, separately worded measurement row, and reinstating any chapter → folio, section/book or gloss
claim is echo-class and needs explicit human sign-off.

## Part B — pipeline and sources
**Frozen pipeline:** `phases/RECIPE_FOLIO_CORRESPONDENCE/scripts/shared_628.py` — TUNED_DIMS (8D), `build_pl_vector` /
`build_v_vector`, PL-side sign flips, residual centering **on the set passed to the matcher** (for B1: the 16-chapter
subset; for B2/B3: the whole source), joint standardization, Euclidean distance; `residual_match` (greedy + pair swap).
**Primary configuration:** folio pool = all Currier B pages with operational profiles; feature-parity features (below);
the primary partitions below. **Sensitivity:** REGIME_1 pool; original PL features; attractor exclusion (B3).
**Sources:**
- **PL-PROC:** Testamentum chapters whose primary family is not "theoretical", with part (Practica / Mercuriorum / Furnis)
  and chapter number from the PL structural profile.
- **THEO:** Theophilus, *De diversis artibus* (English, Hendrie 1847), chapters from PHASE_718's segmentation, **merged
  within a book** into consecutive units until each reaches PL-PROC's median word count (length matching; a remainder
  shorter than half the median joins the previous unit).
- **CODI:** Codicillus, 19 segments — descriptive only (in-domain comparator, not a negative control; too few distinct
  16-subsets for percentiles).
- **Feature parity:** PL-PROC chapters are re-featurized from their English text (PL structural-profile line ranges in
  `testamentum_complete_english.txt`) with PHASE_718's `featurize_chapter` (the Codicillus keyword dictionaries); THEO
  units use the same function. The two English translations differ in style and period — a residual confound, recorded.
**α = 0.0167** (0.05 / 3 tests). A SPECIFIC verdict requires the primary configuration to pass AND the original-PL-features
run to show the same direction; if they disagree in direction, the verdict is INCONCLUSIVE. With one non-alchemical
comparator, **any SPECIFIC result is capped at "Tier 3 candidate"** ("PL-PROC differs from Theophilus", not "from
procedural text in general").

## Tests
- **B1 — correspondence against each source's own null.** For each source, 200 random 16-chapter subsets (seeds
  762000+). For each subset: the real optimized result (mean ratio = second-nearest / assigned distance; number confident,
  ratio > 1.15) and 100 **column-permutation nulls** — each TUNED_DIM permuted independently across the subset's chapters,
  then the same centering, standardization and optimization. Per subset: excess = real − null median, and a rank p. Per
  source: median excess and median rank p.
  - SPECIFIC: PL-PROC median rank p < 0.0167 AND PL-PROC median excess > THEO's 95th-percentile excess.
  - GENERIC: THEO median rank p < 0.0167 as well and PL-PROC's median excess ≤ THEO's 95th percentile.
  - NO CORRESPONDENCE: PL-PROC median rank p ≥ 0.0167.
  - INTERMEDIATE: otherwise.
- **B2 — leaf-mate adjacent chapters (the recto/verso claim), automated and similarity-matched.** Each page's nearest
  chapter (argmin distance). For each leaf with recto and verso in the pool: Δ = difference in chapter order within the
  same part/book (THEO: merged-unit order). **Adjacent = |Δ| = 1** (the claimed pairs are all Δ ≥ 1); **Δ = 0 (same
  chapter) is scored separately** as page similarity. Comparison set: non-leaf page pairs in the same section. Null: leaf
  labels permuted among all same-section page pairs **within deciles of page-to-page 8D distance**, 10,000 permutations
  (seed 762). Statistic: adjacency rate of leaf-mates minus the matched null mean, also expressed relative to the source's
  own chance rate. N of eligible leaves and MDE80 reported.
  - SPECIFIC: PL-PROC p < 0.0167 AND THEO p ≥ 0.05.
  - GENERIC: both p < 0.0167.
  - NO EFFECT: PL-PROC p ≥ 0.0167.
  - INTERMEDIATE: otherwise.
  Descriptive: how each of the six claimed recto/verso pairs was found (both sides matched independently vs a targeted
  scan of the other side of an already-matched leaf).
- **B3 — part → section mapping.** Each chapter's nearest page (argmin) and that page's section. **Primary partition:**
  PL-PROC Practica / Mercuriorum / Furnis; THEO Book I / II / III. Statistic: bias-corrected Cramér's V (Bergsma),
  expressed as z against the source's own permutation null (part labels permuted, 10,000; seed 762).
  - SPECIFIC: PL-PROC p < 0.0167 AND THEO p ≥ 0.05.
  - GENERIC: both p < 0.0167.
  - NO EFFECT: PL-PROC p ≥ 0.0167.
  - INTERMEDIATE: otherwise.
  Flagged secondary (the partition came from the matching itself, C1930): Mercuriorum ≤ 28 / ≥ 29; the fraction of
  Mercuriorum ≤ 28 in Section B is descriptive only. Also reported: the fraction of argmin assignments on attractor pages
  (the five pages receiving the most assignments, PL-PROC and THEO pooled) and the primary test with those five excluded.
- **B5 — the permutation-test flaw, demonstrated.** C1887's procedure on (a) 100 sets of 16 random Gaussian "chapter"
  vectors (seed 762500+) and (b) 100 random 16-unit THEO subsets. FLAW CONFIRMED if p < 0.01 in ≥ 95 of 100 for (a).
- **B4 — non-computational classification** (within the triage table) of the reverse-blind (C1935), count-match (C1925,
  C1944–C1955, C1972–C1975), cold-read (C1971) and gloss-from-match claims: blind or not, base rate or not, targeted search
  or not; P727 failures marked void first.

## What this phase does not do
It does not test the content reading with a new discriminative feature set (PHASE_723's blocked Phase 4), prospective
anchors, or the Catalan (SISMEL) text; it asks only whether the existing evidence is specific to the Testamentum.
