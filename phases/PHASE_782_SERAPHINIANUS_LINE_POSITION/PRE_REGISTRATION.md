# PHASE_782 — Line position and the first glyph: Currier B against a book-length pseudo-script (Codex Seraphinianus) (pre-registration)

**Status: v2 after the lean-expert design audit (v1: LOCKABLE AFTER EDITS; blocking edits E1–E10 and non-blocking
N1–N8 incorporated; drops applied). Nothing that conditions on line position has been computed on the real Codex
order. Calibration on controls follows; then a confirmation pass, an interpretive check by the expert-advisor
(templates and what each result can show), checksums, the lock tag and one run.**

## Origin
- PHASE_764 (human gibberish, MIXED / UNRESOLVED): its strongest contrast was descriptive. B's dependence of a word's
  first glyph unit on its line zone (S3: initial / medial / final) far exceeded volunteer gibberish (AUC 0.986), but
  the samples were short lab pieces of undocumented line-break provenance; a confirmatory test "would need data not
  used here" (RESEARCH_AGENDA Tier A #1 lead; STATUS_BRIEF §4 lists "improvisation in a practised script at book
  scale" as untested).
- The Codex Seraphinianus (Luigi Serafini, 1981) is the best-known book-length pseudo-script: its author has described
  the writing as having no meaning; Stanley 2010 (NCSU thesis) and Wagner 2026 (github.com/jackson-wxyz/
  codex-seraphinianus-analysis: no topic tracking, adjacent reduplication 2.24× chance, caption names unrelated to
  pictures) support that. It is a designed pseudo-script by an artist, not improvisation, so it bears on the
  STATUS_BRIEF gap only by analogy.
- A machine transliteration of its body prose exists (Marco Ponzi, neural-network OCR on word crops; about 18%
  character error on 431 validation characters, 12 of 44 validation words exact; a stroke-level alphabet: capitals are
  word-initial allographs, d/j/n/b terminal flourishes, Z a numeral stroke).

## What has been seen (exposure record, E10)
- The Wagner report (no line-position statistic in it).
- Codex marginals that ignore line position, computed for the design: 303 pages, 1,188 block headers, 7,747 lines,
  44,796 tokens; mean 5.8 tokens per line; 24 first characters (H 3.77 bits); 5.4% of tokens carry '?' or '.';
  per-character word-initial shares; the share of one-character tokens (8.4%) and of tokens starting with a fragment
  stroke (9.1%); block geometry (codes, lines per block, line lengths in characters); pages 79/80 (80 is empty).
- The lean-expert's design audit displayed about 60 lines of page 006 for format and computed the same kind of
  marginals; it computed nothing that conditions on line position, and from the hand-label file it counted only
  positions (86 of 442 labelled words are word 01), no labels.
- B: S3 in PHASE_764 (descriptive); B marginals (25 first units, H 3.28 bits; mean 8.7 tokens per line); B-only
  engine smoke tests on clean, degraded and within-line-shuffled B, and on within-line-shuffled Codex.

## Question
Does the body prose of the Codex Seraphinianus show Currier B's dependence of a word's first unit on its position in
the line?

**Scope (N8).** One book by one modern artist. A result says where B stands against this book, not against invented or
practised scripts in general. Not a meaning test: PHASE_764 did not measure S3 on meaningful text; on S1 (boundary
coupling), meaningful text sat about as far below B as gibberish.

## Data
- **B:** ZL 3b (`data/transcriptions/reference/ZL_official.txt`), Currier B, P placement, 2,478 lines; uncertain
  spaces (',') merged (PHASE_761 rule); glyph units (GLYPH_RE as PHASE_764). Sections from the page header `$I`
  (S 1,084 lines, B 745, H 377, T 198, C 74). **True line positions:** the line-initial word is the first token of the
  line, the line-final word the last; unreadable tokens ('?', '*', rare-glyph codes) are excluded from counts but do
  not create edges (PHASE_764's S3 split segments at unreadable tokens; this phase does not); words beside a drawing
  break `<->` are medial. **Paragraph-first lines** (`<%>`) excluded in the primary.
- **CS:** Ponzi's `CS_OCR_TRANSLITERATION.txt` (github.com/marcoponzi/codex_seraphinianus_ocr, commit 6bc7c93,
  sha256 a0df6dc7…c5a6; kept in `external/phase782_seraphinianus/`, not redistributed; the Codex is in copyright).
  Body prose only (Ponzi's pipeline skipped index pages, title pages, running heads, plate titles and captions).
  - **Parser (E1):** block headers are lines matching `^#\s+cs-` (1,188). Lines beginning `# DUPLICATED:` (2; Ponzi's
    alternate reading of the following line) are excluded and do not start a block; following lines belong to the
    block in progress.
  - Tokens containing '?' or '.' are uncertain, numeral-only tokens ('Z' only) are numerals: both excluded from counts
    without creating edges; a numeral or uncertain token at a line edge makes the line ineligible (E7).
  - **Paragraph-first analogue excluded (E2)** in the primary: block-first lines, and lines that follow a short line in
    the same block. A line is short if its character count is below 0.6 × its block's median; this is computed from
    line lengths only, before any statistic (425 of 7,747 lines). Ponzi's blocks are column segments (block codes 0/1
    cover 1,142 of 1,188; median 6 lines, maximum 35), so block-first lines under-detect paragraph starts.
  - Units: Ponzi's characters; the first unit is the first character (mostly a word-initial capital allograph).
- **Eligible line (both books):** at least 3 token positions, with a readable first and last token; otherwise the line
  is dropped. Drop counts by cause are reported after the run only (they condition on line edges).

## Statistic
- **Chunk:** L = 40 consecutive eligible lines in book order, non-overlapping. **B chunks are formed within sections**
  (leftover lines in a section are dropped; count reported); CS chunks run in page order. Tokens: the 40 line-initial
  words (zone I), the 40 line-final words (zone F), and K = 80 medial words (zone M) drawn without replacement from the
  chunk's readable medial positions (fixed per chunk by seed). Chunks with fewer than 80 readable medial positions are
  dropped (count reported). Fixed zone counts make the statistic independent of line length.
- **S** = I(F1; zone) in bits (plug-in). **Excess** = S − mean S over R = 500 within-line permutations: readable words
  are permuted among their line's readable positions; unreadable and excluded positions, zones and the sampled medial
  positions stay fixed (E7). The chunk value is the excess.
- **Comparison (E4):** AUC = P(excess of a B chunk > excess of a CS chunk) over all chunk pairs. 95% moving-block
  bootstrap (2,000 resamples): each book's chunk list is cut into consecutive blocks of 3 chunks, and blocks are
  resampled within each book. Degraded B uses 20 seeded noise realisations; each resample draws one at random, and the
  point AUC is the mean over realisations. The iid chunk bootstrap is a sensitivity.
- **Units in the primary:** raw first units (B 25, CS 24 symbols). Normalising by H(F1) is not a bias correction
  (with fixed zone counts the bound is H(zone) = 1.5 bits in both books); it is an opposite-label variant only.

## Transliteration noise
The CS transliteration has about 18% character error (on 431 characters, effectively 44 words; the first-character
rate is unknown) plus segmentation errors; noise weakens a dependence, so it biases a comparison toward "B exceeds".
B is therefore also run **degraded to OCR-like noise** before chunking: adjacent readable words in a line merged with
probability m, each word split at a random internal unit boundary with probability s, each unit substituted with
probability q (E7: a word's first unit from B's zone-pooled first-unit marginal; other units from the all-unit
marginal); line positions are re-read after the noise.
- clean: q = 0; matched: q = 0.18, s = m = 0.02; heavy: q = 0.30, s = m = 0.05.
- **Assumption (stated, unverifiable):** independent substitution shrinks the zone contrast by (1 − q); it is
  conservative against real OCR confusions unless those confusions merge exactly the distinctions that carry zone
  information.
- Splits cut both ways: a split fragment never lands in zone I, so splits also create an I-versus-others contrast.
  The split artifact is reported (within-line-shuffled B, then degraded; median excess) at each setting (N3).
- **Reverse confound** (OCR edge errors creating a CS dependence): handled by the guard in the REACHED rule and
  certified by C5.

## Verdict rule (E3)
Intervals are the 95% moving-block bootstrap intervals above.
- **NOT REACHED:** (a) AUC(B heavy vs CS) lower bound ≥ 0.80, and (b) the same with CS's first unit read as its first
  two characters (one-character tokens: the character plus `#`; per-chunk top 24 plus OTHER; B unchanged), lower
  bound ≥ 0.80.
- **REACHED:** otherwise, if (a) AUC(B clean vs CS) upper bound ≤ 0.65 and (b) the same on guarded CS, upper bound
  ≤ 0.65.
  - Guarded CS: one-character tokens, and tokens whose first character is a fragment stroke, are excluded from counts
    without creating edges. A line whose first or last readable token is so excluded is dropped.
  - A fragment stroke is a character whose share of word-initial occurrences, over all its occurrences in readable
    non-numeral CS tokens, is below 0.10. This uses no line position; on the current file it is G L O b d e f g i j l
    n r t u y (9.1% of tokens).
- **UNRESOLVED:** otherwise.
- **Opposite-label variants:** top-8 binning (both books); interior-medial (N1: medial words from positions 3…n−2
  only, lines with at least 5 positions, K = 40); excess / H(F1) of the chunk's sampled words. If any returns the
  opposite definite label under the same thresholds, the label becomes UNRESOLVED.
- Asymmetry for the record: REACHED shows that B's level can be reached (one example suffices); NOT REACHED is one
  book that falls short.

## Certification before the lock (B and within-line-shuffled CS only)
- **C1 (E5):** B clean chunks are split into halves by alternating blocks of 3 consecutive chunks; AUC(half 1 vs half
  2) with the same block bootstrap must have an interval that includes 0.5. No half-width bar (about 23 chunks per
  half give an iid null half-width of about 0.17; resolution is certified by C3–C5).
- **C2:** B clean against within-line-shuffled B, AUC ≥ 0.95.
- **C3:** B's median excess at each noise setting; AUC(B heavy vs within-line-shuffled B) lower bound ≥ 0.80; the split
  artifact reported (N3).
- **C4a:** NOT REACHED must be reachable when the Codex has no line dependence: AUC(B heavy vs within-line-shuffled
  CS) lower bound ≥ 0.80 under both conditions (a) and (b) of the NOT REACHED rule.
- **C4b:** REACHED must be reachable when the Codex has B's dependence: in within-line-shuffled CS, plants in zones I
  and F redraw the first character, with probability p, from non-fragment forms tilted by B's own I-versus-M and
  F-versus-M log-ratios (matched by frequency rank); p is chosen on controls so that the planted median excess equals B
  clean's; the two-condition REACHED rule must fire in at least 80% of 200 planted replicates.
- **C5 guard:** in within-line-shuffled CS (200 replicates per setting), plant (a) left-edge truncation (with
  probability t ∈ {0.05, 0.10, 0.20} the line-initial token of at least 2 characters loses its first character) and
  (b) splits at 0.05 (line positions re-read). The median over replicates of the guarded chunk-median excess must lie
  within the central 90% of the same quantity in 200 unplanted guarded shuffled replicates, at every setting. The
  unguarded median excess is reported relative to B clean's median. If C5 fails, REACHED is withdrawn before the lock.
- **Permitted revisions (E6):** if any of C2–C5 fails, the only permitted revisions are chosen on controls only and
  recorded before the lock: L ∈ {30, 40, 60}; raw units or top-8 binning as the primary (the other becomes an
  opposite-label variant); R = 1,000. If no combination passes, the affected label is declared unreachable and the
  phase stops without running on the real Codex order.
- **Optional hand-label check (E10),** before the lock, as a committed script whose output is limited to: aligned words
  per group (line-initial / other), first-character agreement per group, and the number of line-initial
  disagreements where the OCR token starts with a fragment stroke and the label does not. It can only block REACHED
  (line-initial agreement more than 10 points below the others, or at least 5 such disagreements). It cannot clear the
  edge confound: the 442 words carry augmentation rows, so the OCR output on them is in-sample.

## Sensitivities (cannot change the verdict label)
Paragraph-first analogue as block-first only; no paragraph exclusion in either book; words beside `<->` dropped;
H-track B; CS numerals included; L = 30 and 60; CS wide blocks excluded (block median above 70 characters; 646 lines),
lines above 1.6 × their block median excluded (64), blocks coded 2 or 3 excluded (44) (N2); the iid bootstrap.

## Descriptive (never verdict-bearing)
- Effect size in bits: the difference in median excess, B (each noise setting) minus CS; per-section B excess (N7).
- Each zone's contribution to the excess, and the share carried by the single most zone-specific unit, both books
  (N5): shows whether a CS excess comes from one typographic line-start form.
- A null that permutes words only within word-length classes (space management at line ends, N6).
- A meaningful text with original line breaks (N4): Brunschwig 1500 Part 2 as transcribed (`sources/brunschwig_1500/
  brunschwig_1500_corrected.txt`), print lines, lines with a hyphenated word at either edge ineligible, first unit
  the first letter lower-cased.
- S1 boundary coupling for B and CS with its own noise caveat; S4 adjacent repetition (CS's 2.24× is published).
- Optional (N2): a human count of lines on 3–5 wide-block pages in a printed copy (counts only, no reading of first
  glyphs), to check Ponzi's line segmentation there.

## Exposure rule
Before the lock, no statistic on the real CS order conditions on line position: no S, no zone frequency tables, no
initial-versus-medial counts, no drop counts by cause, no previews. Allowed: marginals, line lengths, block geometry,
within-line-shuffled CS, and the restricted hand-label check above. The engine refuses to chunk the real CS order
unless the locked run script sets its run flag.

## Templates (E9)
- **NOT REACHED:** "Currier B's dependence of a word's first glyph unit on its line position (initial, medial, final)
  exceeds that of the body prose of the Codex Seraphinianus, a book-length pseudo-script its author described as
  having no meaning, in Ponzi's machine transliteration (AUC {a}, 95% block-bootstrap interval {lo}–{hi}; B degraded
  by simulated noise: first-unit substitution 0.30 against a reported character error of about 0.18, splits and
  merges 0.05; also with the Codex's first unit read as two characters). One book by one modern artist: this does not
  show that invented or practised scripts in general fall below B, and it is not a test of meaning (no meaningful text
  with original line breaks has been measured on this statistic)."
- **REACHED:** "The body prose of the Codex Seraphinianus, a book-length pseudo-script by one modern artist, reaches
  Currier B's dependence of the first unit on line position (AUC {a} against noise-free B, 95% block-bootstrap
  interval {lo}–{hi}; also with probable transliteration fragments and one-character tokens removed). This statistic
  therefore does not separate B from at least one book-length pseudo-script. Not evidence that B is meaningless or
  was produced this way."
- **UNRESOLVED:** a phase record only (PHASE_764 precedent).
- What each result can show for the working readings is pre-registered at the lock after the expert-advisor's
  interpretive check (the lean-expert cleared nulls, denominators, power and bookkeeping only).

## Registry
NOT REACHED or REACHED: one Tier-2 row (scope B, external control). UNRESOLVED: phase record and a STATUS_BRIEF line.
