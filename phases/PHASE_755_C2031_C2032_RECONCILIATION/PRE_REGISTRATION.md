# PHASE_755 — C2031 / C2032 reconciliation (pre-registration)

**Locked:** 2026-09-27, before this phase's script was written or run.
**Origin:** STRATEGIC_REVIEW_2026-09-27 §3 #4 (lean-expert round 2, item 3).

## Known before locking (disclosed, not blind)
1. The June 2026 off-books note (`PHASE_691/NL_SYLLABLE_TEST_RESULTS.md`) reported r21 = +0.70 on **all of Currier B**
   with the heat-cycle MIDDLE-class metric. C2031 never claimed −0.66 for all of Currier B; it concerns Section B
   (balneological, f75–f86) against matched Section S folios.
2. The canonical e-depth-class re-run of 2026-05-16 (`MENSURAL_NOTATION_HYPOTHESIS/results/length_stratified_c2031.json`,
   never registered) gives aggregate r21 −0.60 for matched-B and for **all** of Section B, +0.56 for matched-S — but its
   pre-registered length-stratified test FAILED ("LENGTH CONFOUND CONFIRMED"): period-2 appears in 60–120-token
   paragraphs (r21 ≈ −0.94) but not at 30–60 tokens (matched-B +0.58, all Section B +0.17).
This phase formalizes the question with a statistic that does not divide by a near-zero lag-1, bootstrap intervals,
and a like-for-like length comparison.

## Data and definitions (canonical C2031 method)
Paragraphs: H track, language B, placement P, uncertain tokens excluded, split at `par_initial`
(`MENSURAL_NOTATION_HYPOTHESIS/scripts/_length_stratified_c2031.py`). Token class = e-depth class 0 / 1 / 2+ from
`Morphology.atomize(token).e_depth`. For lag L: same-class rate over within-paragraph pairs at distance L, minus the
exact within-paragraph shuffle expectation Σ n_c(n_c−1) / (n(n−1)).
**Period-2 index D = excess(lag 2) − excess(lag 1).** D > 0 is oscillation (lag-1 dissimilar, lag-2 similar).
Populations: Section B all (f75–f86), matched-B (C2031's 15 folios), Section S all (f103–f116), matched-S
(C2031's 17 folios), all Currier B. Length strata by paragraph token count: 3–29, 30–59, 60–119, 120+.
Intervals: paragraph bootstrap, 2,000 resamples, seed 755. Group differences use the bootstrap of each group
independently (difference of means of resampled D).

## Decision rules (locked)
- **SECTION EFFECT SURVIVES LENGTH CONTROL** if in ≥ 2 strata with ≥ 8 paragraphs in both Section B all and
  Section S all, D_B − D_S > 0 with the 95% bootstrap interval excluding 0.
- **LENGTH-CONFOUNDED** if that holds in ≤ 1 stratum while the pooled (all-lengths) D_B − D_S interval excludes 0.
- **NO SECTION EFFECT** if the pooled interval includes 0.
- Separately, report whether Section B all shows D > 0 (interval excluding 0) pooled and within each stratum, and
  the same for all of Currier B.

## Consequences
- LENGTH-CONFOUNDED or NO SECTION EFFECT: rescope C2031(a) and the "Section B −0.66" in C2032/C2053 to a
  paragraph-length-dependent property; drop the section-divergence discriminator (D4) from the rival-panel list or
  require length matching; flag r21 as a noise-floor ratio.
- SECTION EFFECT SURVIVES: keep C2031 with D and length control as the reported statistic; D4 stays a candidate
  discriminator subject to the invariance gate.
