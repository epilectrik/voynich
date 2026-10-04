# PHASE_781 — The head of the page: do the first lines of the herbal pages co-vary with their drawings?

**Status: STOPPED AT ITS PRE-REGISTERED GATE (Stage 1). Pre-registration v2 (after a lean-expert design audit,
LOCKABLE AFTER EDITS; A1–A8 and B1–B7 incorporated) tagged `phase781-prelock` (790cffbd) before Stage 1. No
Voynich first-line statistic was computed against the drawings. No constraint row (precedent PHASE_773). Lean-expert
results check: STOP RECORD SOUND AFTER EDITS (edits applied).**

> PHASE_781 stopped at its pre-registered gate: on the Brunschwig 1500 herbal, a head-of-page text–picture test at 91
> entries and the Voynich first-line lengths detected the herbal's own link in at most 18% of samples (Wilson
> 13–24%; bar 85%). The Voynich first lines were not tested against the drawings and remain unexposed. This is a fact
> about the test's power, not about the Voynich.

- **Question.** On the 91 hand-1 herbal pages (Currier A) coded blind in PHASE_780, do pages whose drawings are similar
  carry similar first lines (H1, glyph-unit trigrams) and first words (H2), beyond position, quire, sheet, layout,
  spelling dials, the initial gallows, style and length?
- **Why.** PHASE_780's positive control (Brunschwig 1500) lost most of its whole-entry link when plant names were
  masked, and the names open each entry.
- **Gate.** Before any Voynich first-line statistic, the same statistic was run on Brunschwig at the Voynich's size:
  91 entries, heads drawn at the Voynich first-line lengths (mean 7.8 tokens), codes degraded to the Voynich coding
  reliability, and the Voynich page structure for the three nulls (N-local, N-shift, N-sheet). The phase was to stop if
  fewer than 85% of 200 Brunschwig samples were detected.

## Result (Stage 1, Brunschwig only)

| Item | Value |
|---|---|
| z\*_BR,head (point 99th percentile, 2,000 replicates per setting) | 2.386 (Markov 2.386, quire-step 2.305; upper 90% bounds 2.466 and 2.336, descriptive) |
| **Gate genre power** (200 samples of 91 entries) | **0.18** (36 of 200; Wilson 0.13–0.24) |
| Per measure | H1 first line 0.115, H2 first word 0.09 |
| Median Z over the 200 samples | 1.59 (drift controls: median 0.16, 99th percentile 2.39) |
| Gate | **STOP** (0.18 < 0.85) |

- The STOP does not depend on the exact threshold: 85% of samples exceed Z 0.77, which about 25% of drift replicates
  also exceed; at the drift 95th percentile (about 1.7) the power is 0.43–0.45.
- The drift replicates use synthetic Brunschwig codes at Brunschwig's own coder disagreement, the gate rows codes
  degraded to the Voynich α (PHASE_780's convention, as pre-registered).

Descriptive rows (200 samples each, own seeds; none could reopen the gate):

| Brunschwig variant | Detected |
|---|---|
| Names masked (name-stem tokens removed before the head is drawn) | 0.01 (median Z 0.70) |
| Body-window comparison (same length, after the head) | 0.02 |
| Rubric name words included | 0.09 |
| First non-modifier token for H2 (Z over H1 and H2; H2 alone 0.09, as in the main row) | 0.18 |
| Main, at PHASE_780's z\* 2.957 (forecast of Stage 2) | 0.045 |

- A heading name stem was present in 90% of the drawn heads; 11 of 121 entries open with a colour or kind adjective.
- **What the stop says about Brunschwig and the test (not about the Voynich).** A heading name stem is in 90% of the
  drawn heads, yet the head-only statistic detects the herbal's link in 18% of samples at its own threshold (4.5% at
  2.957). The head carries some signal (median Z 1.59 against 0.16 in the drift controls) but too little per sample
  for this test at 91 entries. Masking the names removes most of it (0.01 detected; median Z 0.70), so what there is
  runs mainly through names. Text-only fact: 8 heading stems occur in two or more of the 121 entries (19 entries
  carry one, some of them generic words such as wurtz and wilde); most names belong to one entry. PHASE_780's
  whole-entry figure (0.61: about 83 tokens, 95 entries, two nulls, word and trigram measures) is not directly
  comparable, so this phase does not show how the whole-entry link divides between the head and the rest of the
  entry; PHASE_780's half-length row (0.24) shows power falling steeply as the text shortens under fixed machinery.
  "The link runs mostly through plant names" stands; a first-line-sized head alone does not carry enough of it for
  this test at this size.
- The rubric-included row is lower than the main row (0.09 against 0.18; different samples); descriptive only, no
  reading drawn.
- **PHASE_780 names-masked row (descriptive correction).** Brunschwig sets each entry's first letter as a decorated
  initial, which the transcription omits in about a sixth of the entries ("Mpfferwasser", "Grimonien"). PHASE_780's
  names-masked row matched full stems only, so it left 20 of the 98 name-bearing first words in place (78 match a full
  stem, 20 only without the first letter), so 0.27 overstates the detection of a link without names (by an amount not
  measured; not re-run), and the ratio derived from it in PHASE_780's INDEX (names masked 0.73) overstates the update
  against such a link (the true ratio is nearer 1). C2098's verdict and main figure (0.61) are unchanged; C2098 quotes
  the 27% and, under the pre-registered STOP rule, carries no note from this phase (a possible erratum, left to the
  human; STATUS_BRIEF §5).

## Binding stop
On this stop, no Voynich first-line × picture statistic is computed, descriptive or exploratory, in this phase or
later without a new phase with its own power gate (pre-registration A6). The Stage 2 script was drafted while Stage 1
ran, never run, and not committed. PHASE_780 and PHASE_781 are the planned family of text–picture tests on these 91
pages; PHASE_781 ran no test on the Voynich, so the family's false-positive budget was spent only by PHASE_780.
Exposure record: the whole-page text is exposed (C2098 and its companions, including the line-interior value); the
first lines are unexposed.

## Registry
No constraint row; no note on C2098 or any row. Recorded here, in STATUS_BRIEF (under the C2098 entry) and in
RESEARCH_AGENDA with the sentence above. A bracketed status note was added to PHASE_780's INDEX on the names-masked
figures (a phase document, not a registry row).

## Provenance
- Lean-expert design audit (LOCKABLE AFTER EDITS): A1 91 entries; A2 identical three nulls through the Voynich page
  structure; A3 2,000 replicates per setting, point 99th percentile; A5–A6 templates, exposure rule and binding stop;
  A7 the gallows removed in both measures; A8 pre-lock tag. Text-only facts checked before the tag: on all 91 pages
  the first P line opens the first paragraph; no uncertain tokens and no bare-gallows first words in first lines.
- Lean-expert results check: the STOP rule applied exactly as pre-registered (statistic, nulls, replicate rule,
  threshold, sample size, bar); write-up edits applied (the paragraph on the head and the whole entry narrowed; the
  threshold-robustness line and the names-masked ratio added). Its added figures were reproduced from the replicate
  file before entry.
- Compute: 5,000 replicates (two drift settings × 2,000, five rows × 200), about 16 s each at Idle priority on six
  workers.

## Files
`PRE_REGISTRATION.md` (v2, pre-lock) · `scripts/stage1_781.py` · `results/stage1_781.json` (summary and gate),
`results/stage1_781.jsonl` (every replicate), `results/stage1_log781.txt`.
