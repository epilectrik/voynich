# PHASE_782 — Line position and the first glyph: Currier B against a book-length pseudo-script (Codex Seraphinianus)

**Status: COMPLETE. Locked verdict (tag `phase782-lock`, 5ce482e4; pre-registration v4 after a lean-expert design
audit, calibration, an E6 revision to 30-line chunks, an interpretive check by the expert-advisor and a confirmation
pass): UNRESOLVED, in the primary, in all three opposite-label variants and in all eleven sensitivities. Phase record
only (PHASE_764 precedent); no constraint row.**

> The Codex could not be placed relative to B at this resolution; no inference for the readings.

- **Question.** PHASE_764's strongest contrast with human gibberish was descriptive: Currier B's dependence of a
  word's first glyph unit on its line zone (initial, medial, final) far exceeded short volunteer gibberish samples.
  Does the body prose of the Codex Seraphinianus (Luigi Serafini, 1981), the best-known book-length pseudo-script, reach
  B's level?
- **Data.** B: ZL, Currier B paragraph text, true line positions, paragraph-first lines excluded (1,932 eligible lines,
  61 chunks of 30 lines within sections). Codex: Marco Ponzi's neural-network OCR transliteration (about 18% character
  error; stroke-level alphabet), body prose only, paragraph-first analogue excluded (5,463 eligible lines, 180
  chunks); kept outside the repository (the Codex is in copyright).
- **Statistic.** Per chunk of 30 lines: the mutual information between a word's first unit and its zone, on 30
  line-initial, 60 sampled medial and 30 line-final words, minus its mean under within-line permutation (the excess).
  Comparison by AUC over chunks with a moving-block bootstrap. B was also degraded with simulated OCR noise; the
  Codex was also read with its first unit as two characters, and "guarded" (one-character and fragment-initial
  tokens removed, against OCR edge artifacts).

## Result

| Condition | Comparison | AUC | 95% interval | Bar | Met |
|---|---|---|---|---|---|
| NOT REACHED (a) | B, heavy noise, vs Codex | 0.53 | 0.43–0.63 | lower bound ≥ 0.80 | no |
| NOT REACHED (b) | the same, Codex first unit as two characters | 0.49 | 0.40–0.59 | lower bound ≥ 0.80 | no |
| REACHED (a) | B clean vs Codex | 0.82 | 0.76–0.89 | upper bound ≤ 0.65 | no |
| REACHED (b) | B clean vs guarded Codex | 0.94 | 0.89–0.97 | upper bound ≤ 0.65 | no |

| Median excess per chunk (bits) | Value |
|---|---|
| B clean | 0.234 |
| B, simulated heavy noise (each unit redrawn with probability 0.30, about 0.26 of first units changed; splits and merges 0.05; 0.104 in calibration, seed variation) | 0.108 |
| Codex, as transliterated | 0.097 |
| Codex, first unit as two characters | 0.118 |
| Codex, guarded | 0.059 |

**UNRESOLVED.** The Codex as transliterated sits level with B degraded by heavy simulated noise (AUC 0.53) and below
clean B (AUC 0.82). Its transliteration noise (overall rate, first-character rate, and whether errors depend on line
position) is not known well enough to say where the fair comparison lies, or in which direction the transliteration
moves the Codex's value (uniform errors lower it; errors that depend on line position can raise it), so the test
cannot place it: the pre-registered plant ladder had shown that a Codex anywhere between about 0.02 and at least 0.15 bits
would land here. The label holds under top-8 binning, interior-medial words only, entropy normalisation, an iid
bootstrap, chunks of 40 or 60 lines, no paragraph exclusion, block-first exclusion only,
wide blocks, long lines or blocks coded 2/3 excluded, medial words beside `<->` dropped, Codex numerals included, and
the H-track transcription of B.

**For the working readings:** no change (pre-registered: UNRESOLVED moves nothing; the 34 / 51 / 15 odds are
conversation-level priors set by the expert-advisor, not measured probabilities).

## Descriptive (never verdict-bearing)
- **The Codex as transliterated carries a line-position dependence of its own.** Its excess is well above its
  within-line-shuffled controls (raw medians −0.007 to +0.001, calibration C4a; guarded central 90% −0.011 to +0.004,
  C5), including after probable OCR fragments and one-character words are removed (0.059; this drops 37% of eligible
  lines, selected by what sits at their edges). In both books it sits mostly at line starts (zone medians, initial /
  medial / final: Codex 0.049 / 0.018 / 0.022; B 0.132 / 0.061 / 0.033). The most zone-specific unit carries a median
  0.047 bits in the Codex and 0.082 in B (share of the chunk excess 0.54 and 0.33; the share is unstable in chunks
  with small excess). Permuting words only within word-length classes leaves most of it (Codex 0.078, B 0.173), so it
  is not only line-end space management. Whether it belongs to the script or to the transliteration is open: the C5
  guard covers left-edge truncation and splits only, and OCR accuracy may differ by line position (hand-label check,
  in-sample: first-character agreement 0.91 line-initial, 0.79 other).
- **Meaningful texts with original line breaks** (computed before the lock): Brunschwig 1500 print 0.042–0.048 bits
  (AUC against its own within-line shuffle 0.74, 0.72–0.77); Aberdeen Bestiary (c. 1200, Latin manuscript) 0.007 (not
  distinguishable from its own shuffle: AUC 0.52, 0.40–0.63). On this statistic the Codex (0.097 as transliterated,
  0.059 guarded) lies between those texts and B. This ordering was not a pre-registered comparison and no interval was
  computed for it. The values are not like for like: the anchors' first unit is a lower-cased Latin letter; both
  anchors drop every line with a word broken across an edge (Aberdeen: 150 selected pages, 38% of lines eligible),
  removing the lines where line-end conventions act; the Codex's value carries OCR noise of unknown direction. Reading
  the ordering (for example as "a pseudo-script produces more line-position structure than prose") is an echo-class
  interpretation left to the human; no odds or likelihood ratio is shifted by it.
- **Effect sizes:** B clean minus Codex 0.137 bits; B with matched noise minus Codex 0.053; B with heavy noise minus
  Codex 0.011.
- **B by section** (median excess; chunks): S 0.287 (25), H 0.223 (10), B 0.197 (20), T 0.171 (5), C 0.114 (1).
- **S1 boundary coupling** (PHASE_764's statistic, last unit of a word against the first unit of the next): B 0.164,
  Codex 0.067 (AUC 0.77, 0.69–0.84; the Codex's OCR noise moves it in an unknown direction: substitutions lower it;
  false word splits raise it, since a split junction is word-internal, cf. PHASE_761: 0.569 bits at B's uncertain
  spaces).
- **S4 adjacent repetition** under the within-line permutation null, eligible lines: B log O/E +0.08 (146 against 134
  expected), Codex −0.03 (271 against 279). Wagner 2026 reports 2.24× chance with chance defined as the sum of
  squared word frequencies over the whole corpus (his REPORT.md §3); the within-line null used here also absorbs a
  word's recurrence elsewhere in its own line, so the two figures answer different questions and are not compared.
  B's +0.08 agrees with C2085's +0.03.
- **Codex guard:** of 5,463 eligible lines, 1,421 open and 753 close with a one-character or fragment-initial token
  (179 both), so the guarded Codex keeps 3,468 lines (110 chunks, against 140 for the within-line-shuffled Codex):
  about 26% of eligible lines open with such a token, against at most about 17.5% of all tokens.
- **Line drops by cause:** B: paragraph-first 479, fewer than 3 positions 33, unreadable edge 34, eligible 1,932.
  Codex: paragraph-first analogue 1,399, fewer than 3 positions 189, uncertain edge 696, eligible 5,463.

## What this does and does not show
- It does not place the Codex above or below B. Simulated noise at the heavy setting (about 0.26 of first units
  changed, above the reported 0.18 character error) brings B level with the Codex as transliterated (AUC 0.53); at
  the "matched" setting B stays above it (median 0.150 against 0.097, closing about 60% of the gap to clean B). The
  Codex's first-character error rate is unknown, so the gap to clean B (AUC 0.82) cannot be assigned to the Codex or
  to its transliteration. The guarded comparison (AUC 0.94) sets clean B against 63% of the Codex's lines and has no
  noise-matched counterpart. The band the design could not separate (about 0.02 to at least 0.15 bits) also contains
  the Brunschwig print's value.
- It does not test meaning, and it is one book by one modern artist laid out like print.
- PHASE_764's descriptive contrast with volunteer gibberish stands as it was (descriptive); this phase neither
  confirms it at book scale nor removes it.
- A sharper test would first measure the transliteration's first-character error by line zone on a
  hand-transliterated sample outside Ponzi's training words, then degrade B to the measured zone-specific rates; or
  use a clean second book-length pseudo-script. Either needs a new pre-registered phase.

## Process and provenance
- Lean-expert design audit (v1 → LOCKABLE AFTER EDITS; E1–E10, N1–N8); calibration on B and within-line-shuffled
  Codex only; C4b (REACHED power) failed at 40-line chunks (0.605) and passed at 30 (1.00) under the pre-registered
  revision menu; expert-advisor interpretive check (likelihood ratios, templates); lean-expert confirmation pass
  (LOCKABLE AFTER EDITS; dry mode, lock assertions, interim writes, crash rule, plant ladder); dry run on the shuffled
  Codex; lock; one run (806 s).
- Lean-expert results check: RECORD SOUND AFTER EDITS (the verdict path matched v4 exactly; edits applied: guard
  counts corrected, the noise-gap sentence narrowed, OCR direction and anchor comparability qualified).
- Optional hand-label check (before the lock): first-character agreement 0.91 on line-initial and 0.79 on other words
  (Ponzi's 442 labelled training words); one fragment-type disagreement; did not block REACHED.
- Data: Codex transliteration from github.com/marcoponzi/codex_seraphinianus_ocr (commit 6bc7c93; no licence stated;
  not redistributed). Prior analysis: github.com/jackson-wxyz/codex-seraphinianus-analysis (Wagner 2026).

## Files
`PRE_REGISTRATION.md` (v4, locked) · `scripts/core782.py`, `scripts/calib782.py`, `scripts/run782.py`,
`scripts/anchor782.py`, `scripts/ladder782.py`, `scripts/handlabel782.py` · `results/verdict782.json`,
`results/run_log782.txt`, `results/input_checksums782.json`, `results/calib782.json`, `results/calib782_L30.json`
(with replicate files and logs), `results/anchors782.json`, `results/ladder782_L30.json`, `results/handlabel782.json`,
`results/dryrun/`.
