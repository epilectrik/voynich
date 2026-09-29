# PHASE_769 — Is the e-run "dial" set per folio or per procedure? (pre-registration)

**Status:** LOCKED (v2, 2026-09-29). Draft v1 went to a lean-expert design audit, which returned "LOCK WITH CHANGES"
with edits E1–E12. All the edits are incorporated, and the design was recalibrated on controls only. Nothing below may
change after lock without a new phase number.

## Origin
- **The human's reading.** The extensible glyphs (ke / kee / keee) looked "programmatic, not cipher-like" to the human,
  who reads e-run depth as a heat level (a Tier-3 gloss).
- **The reviews.** Two lean-expert reviews (Opus 5.5 and Fable 5.1) agreed that the extensible glyphs alone do not
  discriminate notation, cipher or pseudo-writing. They recommended a precondition: with the word frame and position
  fixed, does the e-run length carry a setting shared across words at the scale of a folio or a procedure (paragraph)?
- **What follows from the precondition:**
  - If there is no such setting, there is nothing for the pictures to track.
  - If there is one, a blind picture-coding test becomes worth running.

## Prior knowledge (declared)
- **PHASE_758.** e-run 1 vs 2+ is read consistently across tracks: κ 0.95–0.96. This is an upper bound, and track F
  reads 4.7% of H's 2+ runs as 1.
- **C1197.** Only e and i extend.
- **C1199.** The long-e rate varies by section and between header and body. It is not controlled for frame.
- **C1225 (rescoped).** Run length conditions the following glyph. This is a generic effect.
- **C1977.** Recto and verso of one leaf have correlated e-depth. Not controlled for frame.
- **C1967.** Paragraph-channel gradient. Not controlled for frame.
- **C2077 K4.** Lag-1 e-depth correlation of +0.035, reproduced by a class Markov model.
- **C2031/C2032.** Rescoped as length-confounded.
- **Not computed on B before lock:** any folio- or paragraph-level run-length statistic under frame control. B
  supplied only:
  - its token, cell, folio and paragraph structure;
  - its H–F alignment;
  - its cell rates, which carry no folio information.

## Data
- **Primary: the H track.** Currier B, P placement, labels excluded, uncertain tokens dropped.
  - 21,610 tokens, 80 folios, 459 paragraphs, with paragraph starts from the H-track paragraph-initial flag.
  - Section × hand, with hands taken from ZL $H: S/3, B/2, H/2, C/2, H/5, H/3, S/?, T/2.
  - 9,927 e-runs, of which 5,851 are informative (their cell spans 2 or more folios).
- **Transcription check: ZL 3b.** Uncertain spaces merged, paragraph starts from `<%>`, 5,736 informative e-runs.
  - ZL reads the same pages, so it is a transcription check, not a replication (E7).
- **H–F alignment** (the PHASE_758 rule) gives:
  - a folio legibility score: the share of H tokens not matched by an aligned F token of the same e-collapsed form;
  - the S3-cons subset: runs that H and F read the same, which is 92% of informative runs.
  - F covers 79 of the 80 folios. The one folio without F takes the median legibility.

## Occurrences, cells, null
- **Occurrence.** One run of the glyph unit e inside a token (glyph units `c[tkpf]h|[cs]h|i+[nrlm]|.`).
- **Frame.** The token with every e-run collapsed to one e, together with the run's index.
- **Outcome.** y = 1 if the run has 2 or more e's.
- **Cell.** Frame × run index × line zone × header line × paragraph-length tercile (token counts, cut points from
  pooled B) × section × hand.
- **Null.** y is permuted among the occurrences of the same cell across folios. Only informative occurrences enter.
- **Residual.** r = y − cell mean.
- **Splits (E1).** 50 random halvings of the set of collapsed-token strings (seed 7690). They are fixed once and
  reused in every permutation, and all runs of a multi-run token fall in the same half.
- **S1** is labelled anti-conservative for multi-run tokens.

## Statistics
**Folio arm, primary: S3c (E2).** For each folio, compute the mean residual of the A-frames in the top half of its
lines and of the B-frames in its bottom half.
- Each of the two means is regressed, weighted by n, on four folio covariates: log lines, mean tokens per line,
  number of paragraphs, and H–F legibility (standardised, with an intercept). The same regression is applied in every
  permutation.
- The two sets of residuals are then correlated across folios with at least 5 occurrences in each region.
- The same is done with A and B swapped, and the result is averaged over the 50 splits.

**Paragraph arm, co-primary: S3P (E9).**
- Uses paragraphs of 4 or more lines.
- A-frames in the first half of the lines against B-frames in the second half, with the middle line dropped.
- Statistic: Σ_p (Σ r_A) (Σ r_B), over the same splits with swaps. No minimum counts.
- Null: the primary null (across folios). It therefore detects settings at the paragraph scale or coarser.
- S3P-within, with permutation within cell × folio, isolates settings specific to paragraphs. It is reported.

**Secondary and descriptive statistics:**

| Statistic | What it is |
|---|---|
| S3 | S3c without covariate adjustment |
| S3far | first quarter against last quarter of a folio's lines; for drift (E4) |
| S3-dis | Σ_f Σ r_i r_j over top/bottom pairs whose collapsed tokens are 3 or more glyph-unit edits apart; for copying (E3) |
| S3-int | S3c excluding token-final runs (0.2% of runs) |
| S3-cons | S3c on H–F-consistent runs only (E5) |
| S3c-k | S3c on runs after k only (E10; 32% of runs) |
| S1 | Σ_f n_f · mean(r \| f)² |

**Permutations:** 2,000 on B. p = (1 + #{null ≥ obs}) / (1 + valid permutations).

**Rationale (E6).** S3c holds the frame fixed and uses different frames in regions far apart. It therefore cannot be
produced by:
- exact reuse of one word's spelling;
- lag-1 persistence;
- covariate-borne folio shape;
- legibility.

Copying with mutation and slow drift can produce it. These are handled by E3, E4 and the calibration below.

## Calibration (controls only)
- **Settings:** 200 replicates per condition, 1,000 permutations, 50 splits, synthetic y on B's cell structure (E8).
- **Tables:** power at α 0.01 / 0.05, with 95% Wilson intervals in `results/prelock_calibration_summary.json`.

| Condition | S3c | S3far | S3-dis | S3P | S3P-within | S1 |
|---|---|---|---|---|---|---|
| No setting (size) | 0.01 / 0.06 | 0.01 / 0.04 | 0.01 / 0.04 | 0.00 / 0.01 | 0.01 / 0.03 | 0.02 / 0.04 |
| Folio setting σ 0.25 | 0.33 / 0.61 | 0.11 / 0.28 | 0.46 / 0.66 | 0.21 / 0.40 | 0.01 / 0.06 | 0.78 / 0.90 |
| Folio setting σ 0.35 | **0.78** / 0.93 | 0.48 / 0.70 | 0.85 / 0.93 | 0.62 / 0.77 | 0.02 / 0.06 | 0.99 / 1.00 |
| Folio setting σ 0.5 | **0.99** / 1.00 | 0.82 / 0.94 | 0.99 / 1.00 | 0.89 / 0.94 | 0.01 / 0.07 | 1.00 / 1.00 |
| Paragraph setting σ 0.35 | 0.04 / 0.08 | | | 0.52 / 0.74 | 0.10 / 0.20 | |
| Paragraph setting σ 0.5 | 0.07 / 0.16 | | | **0.94** / 0.99 | 0.42 / 0.58 | |
| Paragraph setting σ 0.7 | 0.10 / 0.17 | | | 1.00 / 1.00 | 0.79 / 0.91 | |
| k-only setting σ 0.35 | 0.03 / 0.09 | | | | | S3c-k 0.22 / 0.42 |
| Word-specific σ 1.0 | 0.03 / 0.06 | | 0.08 / 0.12 | 0.07 / 0.12 | | 0.81 / 0.92 |
| Local persistence φ 3.0 | 0.03 / 0.10 | 0.03 / 0.10 | 0.07 / 0.19 | 0.09 / 0.18 | 0.03 / 0.04 | 0.74 / 0.92 |
| Drift (folio SD 0.35) | **0.68** / 0.85 | **0.10** / 0.23 | 0.86 / 0.93 | 0.89 / 0.96 | | 1.00 |
| Copy c 0.1 / 0.2 | 0.03 / 0.01 (α 0.01) | | 0.03 / 0.04 | 0.03 / 0.07 | | 0.06 / 0.27 |

Under folio settings of σ 0.25 / 0.35 / 0.5, the ZL check (S3c on ZL) had power 0.25 / 0.74 / 0.98 at α 0.01 and
0.55 / 0.91 / 0.99 at α 0.05.

**Negative texts (2,000 permutations):**
- Naibbe GV1: S3c p 0.56.
- habit3b, three seeds: S3c p 0.074 / 0.54 / 0.68.
- Timm–Schinner: S3c p 0.065, but S3-dis p 0.001 and S3P p 0.0005. Multi-step copying defeats S3-dis and S3P, but not
  S3c at α 0.01.

**Readings of the calibration:**
- **Specificity of S3c.** At α 0.01, S3c rejects in at most 3% of runs under word-specific effects, local persistence,
  1-edit copying, the habit generators and Naibbe.
- **Slow drift mimics a setting,** but S3far separates the two:

  | Condition | mean S3far / mean S3c |
  |---|---|
  | Constant folio setting | 0.70–0.72 |
  | Drift | 0.33 |
- **The paragraph arm** also responds to folio settings, drift and multi-step copying. S3P-within is specific to
  paragraphs but weak (MDE80 about 0.7).
- **ZL rule (E7).** The ZL check's power at σ 0.35 (α 0.05) is 0.91, with a Wilson interval of 0.86–0.94. The folio
  arm's ZL check is therefore p ≤ **0.05**. The paragraph arm's ZL check comes from the ZL S3P power at σ 0.45, which is 0.965 at α
  0.05 (0.99 at 0.10; `results/calib/ZL_PARA_0.45.json`). It is therefore also p ≤ **0.05**.
- **i-runs (E12).** The H–F minim-count agreement (1 vs 2+ minims) is κ **0.42**. F reads 879 of 1,428 of H's
  single-minim groups as 2+, while only 8 of 2,124 go the other way. Minim counts are not reliably transcribed, so the
  i-runs are **not analysed** in this phase. The κ is reported as a finding.

**Verdict probabilities for the folio arm (joint H + ZL; 200 replicates):**

| True σ | P(PRESENT) | P(NO) | P(INDETERMINATE) |
|---|---|---|---|
| 0 | 0.00 | 0.875 | 0.125 |
| 0.25 | 0.195 | 0.21 | 0.595 |
| 0.35 | 0.705 | 0.005 | 0.29 |
| 0.5 | 0.99 | 0.00 | 0.01 |

- **The NO bound** is P(not NO) ≥ 0.8 for σ ≥ 0.25 (0.79 at 0.25; 0.995 at 0.35). At B's base rate of about 20%,
  σ 0.25 is a folio long-e rate with an SD of about 4 percentage points.

## Decision rules (E7, E9; each arm at α 0.01, family-wise ≤ 0.02)
| Arm | PRESENT | NO | Otherwise |
|---|---|---|---|
| **Folio** | **FOLIO-LEVEL COMPONENT PRESENT:** S3c p ≤ 0.01 on H, and ZL S3c p ≤ 0.05 | **NO FOLIO-LEVEL COMPONENT (bounded):** S3c p > 0.05 on H and on ZL | INDETERMINATE |
| **Paragraph** | **SETTING AT PARAGRAPH SCALE OR COARSER:** S3P p ≤ 0.01 on H, and ZL S3P p ≤ 0.05 | **NONE AT PARAGRAPH SCALE (bounded):** S3P p > 0.05 on H and on ZL | INDETERMINATE |

**Picture gate:** the picture test starts only if an arm is PRESENT **and** S3-dis, S3-int and S3-cons all reach
p ≤ 0.05.

**Descriptive, reported under every verdict:**
- S3far against S3c: a ratio near 0.7 reads as a constant setting, near 0.33 as drift;
- S3P-within, to tell a paragraph-specific setting from a coarser one;
- S3c-k, S1 and unadjusted S3;
- S3c by stratum (S/3, B/2, other) and the informative share;
- the leaf correlation of folio propensities under frame control (C1977).

## Scope (E11)
**FOLIO-LEVEL COMPONENT PRESENT:**
- Among recurrent frames (5,851 of 9,927 runs), the choice between one e and 2+ has a folio-level component shared
  across frames. It holds beyond frame, run index, zone, header, paragraph length, section, Davis hand and folio
  covariates.
- Its source is not identified. Candidates:
  - content;
  - a writing session or drift;
  - a pen;
  - an unrecognised hand;
  - legibility;
  - copying.

  The S3-dis, S3-int, S3-cons and S3far results are stated alongside.
- "Folio" includes leaf and quire.

**NO FOLIO-LEVEL COMPONENT:**
- There is no folio-level shared component among recurrent frames. P(not NO) ≥ 0.8 for σ ≥ 0.25, about a 4-point
  folio SD.
- This does not bound:
  - paragraph-level dials (a separate arm);
  - k-restricted dials (S3c-k MDE80 above 0.5);
  - smaller effects;
  - rare or folio-unique frames;
  - heat carried by word choice.

**Paragraph arm:** the same framing at paragraph scale or coarser.

**Under any verdict:**
- The heat gloss stays Tier 3. NO records only that the per-folio (or per-paragraph) version is unsupported.
- Not evidence of meaninglessness.

## Registry consequences
| Verdict | Consequence |
|---|---|
| **PRESENT (either arm)** | A Tier-2 measurement row in the E11 wording, with no reading. The picture test becomes the next phase only if the picture gate passes. |
| **NO (both arms)** | A Tier-2 negative-knowledge row with the bounds above. STATUS_BRIEF note: e-run length carries no folio- or paragraph-level setting shared across words among recurrent frames. |
| **Mixed or INDETERMINATE** | Phase record, stating each arm. |

**Also recorded:** the minim κ 0.42 H–F, as a transcription-reliability finding for i-run rows (C1204, C1910).

## Guards (E12)
- The list of the ten folios with the highest and lowest propensity is descriptive. It is never used to choose
  picture-test folios; that test codes every folio of one section and hand, blind.
- No REGIME contrasts of propensity are reported (C1715, C2070).
- i-runs are not analysed (κ 0.42).

## Design history (controls only)
- **v1** used S3 without covariates, 40 replicates, and the paragraph S1/S2.
- **Round 1** showed S2 fooled by local persistence (habit3b p 0.031). S3 was then added.
- **The audit** added:
  - S3c, with legibility and folio-shape covariates;
  - the COPY, DRIFT, SHARED-K, SHARED-PARA and LOCAL controls;
  - S3-dis, S3-int, S3-cons and S3far;
  - the paragraph arm S3P;
  - 200 replicates with Wilson intervals;
  - the symmetric decision rule.
- **Blind to B throughout.** No B run-length statistic by folio or paragraph was computed at any stage.
