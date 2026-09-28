# PHASE_758 — e-run family gate: transcription reliability, segmentation, and e-run transitions (pre-registration)

**Locked:** 2026-09-27, before any analysis code for this phase was written or run. Design audited by the lean-expert
(first draft: REDESIGN Part B; Parts A and C LOCK WITH CHANGES). Every requested change is incorporated below.
**Origin:** STRATEGIC_REVIEW_2026-09-27 §3 #3 (units/orthography gate), continuing PHASE_754, which found the atom
constraints C1440/C1209/C1484/C1207/C521 partly orthographic and named the e-run family as next.
**Claims under test:**
- **C1225 (Tier 2):** within ke-family MIDDLEs, single-e tokens use -edy 62% / -y 14% while multi-e tokens use -edy
  12% / -y 35% (-s only multi-e); read as "e-depth is a parametric axis … different instruction types".
- **C1967 (Tier 2):** paragraph-channel e-depth gradient (qo > ch > sh on non-prefix tokens, p = 0.024).
- **C2031 (Tier 2, rescoped by PHASE_755):** Section B period-2 e-depth alternation, D = +0.028 (CI +0.008 to +0.047).
**Scope statement:** no Markov order separates "grammar" from "orthography"; this phase does not decide that
question. It measures (A) whether e-run length is read consistently across transcriptions, (B) whether C1225's
table is a segmentation artifact and what the unsegmented e-run transition facts are, and (C) whether the cross-token
e-depth claims survive a change of transcription track.
**Parser note:** C1957 (2026-04-05, commit a52ca08) blocked e-initial suffixes in `Morphology.extract()`. Under the
current parser "-edy" is not a suffix, so C1225's table cannot be recomputed with the current parser as written.
**Change control:** after lock nothing below may change without a new phase number.

## Data
Currier B, `P` placement, labels excluded, uncertain tokens excluded; H track primary; tracks F and C for Parts A, B5
and C. Glyph units: PHASE_754 tokenizer `c[tkpf]h|[cs]h|i+[nrlm]|.`. e-depth: `Morphology().atomize(token).e_depth`
(as in C2031/PHASE_755). e-run: a maximal run of `e`.

## Part A — cross-track consistency of e-run length (an upper bound on reliability)
Readers are not independent (later transcriptions may have been reconciled against earlier ones; F and C were
converted into EVA from their own alphabets), so agreement is an upper bound: a low value is informative, a high
value is weak evidence.
- **A0 (documentation, before interpreting A1–A3):** record from the transcription documentation how the F and C
  source alphabets encode e-sequences and whether the conversion to EVA can merge or split e-runs.
- **Alignment:** whole lines of Currier B `P` text present in both tracks are aligned token-by-token with an
  edit-distance alignment (difflib on token sequences); aligned pairs of certain tokens are kept. The equal-token-count
  rule is reported as a sensitivity, with its line retention rate and the e-run density of the dropped lines.
- **A1:** among aligned pairs identical after replacing every e-run by one marker, the agreement of e-run lengths by
  the H run length (1, 2, 3+), with the directional confusion counts (H e → F ee, H ee → F e, etc.).
- **A2:** for token e-depth class (0 / 1 / 2+) and for the 1-vs-2+ split (pairs where either track has e-depth ≥ 1):
  raw agreement, Cohen's κ, PABAK, directional confusion counts.
- **Classification** (H vs F, 1-vs-2+, κ, Landis–Koch conventions): CONSISTENT κ ≥ 0.80; MODERATE 0.60–0.80;
  FRAGILE κ < 0.60. A systematic one-way confusion (one direction ≥ 2× the other with ≥ 20 cases) is reported as
  DIRECTIONAL BIAS regardless of κ.

## Part B — C1225
- **B1 (replication, two parsers):** C1225's table with the original T7 definitions
  (`phases/KE_THERMAL_CYCLING_VALIDATION/scripts/ke_thermal_test.py`) using (i) the historical parser — `scripts/voynich.py`
  at the parent of commit a52ca08 (pre-C1957 suffix set, which includes e-initial suffixes such as -edy) — and (ii) the
  current parser. Reported: the tables and whether the published numbers reproduce.
- **B2 (segmentation migration — the artifact test):** for the tokens in C1225's single-e and multi-e classes (historical
  parser), the crosstab of segmented class against the unsegmented length of the e-run that follows k (1, 2, 3+).
  **Named flaw SEGMENTATION ARTIFACT** if ≥ 25% of the historical single-e tokens have an unsegmented run of ≥ 2 after k
  (e's moved into the suffix by the parser).
- **B3 (unsegmented table):** every token in which `k` is immediately followed by an e-run: run class (1 vs 2+) ×
  the glyph unit immediately after the run (END if the token ends). Units with < 10 occurrences in the real table are
  pooled into OTHER, and the same pooling map is applied to every null table. Statistic S = Miller–Madow-corrected
  mutual information (bits) between run class and next unit. S_real.
- **B4 (conditional-resampling nulls):** every real k + e-run occurrence and its preceding context are kept; only the
  next unit is resampled, 1,000 draws per model, from glyph-unit transition probabilities estimated on all primary B
  tokens: **order 1** P(next | e) (no memory of run length) and **order 2** P(next | previous two units), i.e. (k, e) for
  runs of 1 and (e, e) for runs of 2+, pooled over all heads. Reported: S_ord1 and S_ord2 distributions, and the
  fraction reproduced by order 2, F2 = (S̄_ord2 − S̄_ord1) / (S_real − S̄_ord1), with a 1,000-resample bootstrap CI
  over occurrences (seed 758).
  - **RUN-LENGTH EFFECT** if S_real > 99th percentile of S_ord1 (run length matters at all).
  - **k-SPECIFIC RESIDUAL** if S_real > 99th percentile of S_ord2 (beyond the generic e-run transition).
  - **GENERIC e-RUN TRANSITION** if RUN-LENGTH EFFECT holds and S_real ≤ 99th percentile of S_ord2.
- **B5 (homogeneity across heads):** the same run class × next unit table for e-runs after ch, sh, o and all other
  heads. Statistic: Miller–Madow MI between head class {k, ch, sh, o, other} and next unit, conditional on run class;
  null: head labels permuted within run class (1,000 permutations, seed 758). p ≥ 0.05 → **HOMOGENEOUS** (the
  "ke-family" specificity is not supported: a script-wide e-run rule); p < 0.05 → **HEAD-SPECIFIC**.
- **B6:** B3 and B4 repeated on track F (reported; TRACK-SENSITIVE if the verdict of B4 changes).

## Part C — track sensitivity of the cross-token e-depth claims (C1967, C2031)
Within-token transition structure cannot produce cross-token or paragraph-level structure; these claims face only the
track question.
- **N-matching:** H is recomputed on exactly the lines and paragraphs that F covers; F uses H's paragraph breaks
  (matched by locus).
- **C1:** PHASE_755's D (Section B, f75–f86; e-depth classes 0/1/2+; exact within-paragraph shuffle expectation;
  2,000 paragraph-bootstrap resamples, seed 758) on matched H and on F.
- **C2:** C1967's non-prefix gradient (qo-dominant minus sh-dominant paragraph means; 10,000 permutations, seed 758) in
  two variants: (i) H's channel classes with F's e-depth (isolates e-reading); (ii) all-F.
- **Verdicts (decided on the estimate):** TRACK-SENSITIVE if the F estimate flips sign or falls outside matched-H's
  95% CI; UNDERPOWERED if same sign, p ≥ 0.05 (or CI includes 0) and inside H's CI; TRACK-ROBUST if same sign and
  p < 0.05 (C1: CI excludes 0).

## Registry actions (locked)
- **C1225:** "parametric axis" and "different instruction types" are interpretations (C171); they are struck only on the
  named flaw SEGMENTATION ARTIFACT from B2. The Tier-2 row keeps only the glyph-level unsegmented table (B3) with its
  B4/B5 verdicts. If B1(i) does not reproduce the published table, that is recorded as well.
- **Part A FRAGILE or DIRECTIONAL BIAS:** every claim that distinguishes e-depth 1 from 2+ is annotated with κ and the
  confusion direction. The list is generated at run time by grep over `context/CLAIMS/INDEX.md` for `e_depth`,
  `e-depth`, `e-run`, `ee`, `multi-e`, `single-e` (the draft list C1225, C1967, C2031, C2032, C2053, C1394, C1972,
  C1197, C901, C1204, C1457, C1735, C1740 is a floor). MODERATE: annotated with κ. CONSISTENT: note only (upper bound).
- **Part C TRACK-SENSITIVE:** annotate "not reproduced on track F (matched)". UNDERPOWERED: annotate the F estimate.
