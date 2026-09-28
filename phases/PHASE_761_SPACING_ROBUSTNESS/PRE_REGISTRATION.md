# PHASE_761 — Does boundary glyph coupling survive word-spacing uncertainty? (pre-registration)

**Locked:** 2026-09-28, before any analysis code for this phase was written or run (a marker count of the input file
was made to size the groups: ZL Currier B paragraph text has 18,856 definite and 1,634 uncertain spaces).
**Origin:** human-approved next step (2026-09-28). Boundary glyph coupling — the last glyph unit of token n predicting
the first glyph unit of token n+1 (C1212/C1563) — is now load-bearing: it is the strongest discriminator that excluded
the Naibbe cipher (C2080, D2) and part of what PHASE_756 holds fixed. Rozanova & Temerev (arXiv 2608.17096) report that
uncertain spaces are mostly word-internal. If part of the coupling sits at spaces that are not real word boundaries, it
is within-word structure, not a cross-token phenomenon.
**Change control:** after lock nothing below may change without a new phase number.

## Data
`data/transcriptions/reference/ZL_official.txt` — the Zandbergen–Landini IVTFF transliteration, version 3b
(2025-05-13), an independent second transcription relative to the project's H track. Pages with header `$L=B`
(Currier B); loci whose type starts with `P` (paragraph text). Line text is tokenized at `.` (definite space) and `,`
(uncertain space). `<->` (gap for a drawing) and line ends are not boundaries used here. Markup: comments `<!…>` and
`<%>`, `<$>` removed; `[a:b]` alternatives → first reading; `{…}` braces removed keeping content; `@nnn;` rare-glyph codes
and any token containing `?` make the token unreadable, and no boundary adjacent to an unreadable token is used.
Glyph units: PHASE_754 tokenizer `c[tkpf]h|[cs]h|i+[nrlm]|.`.

## Statistic
For a set of boundaries, C = plug-in mutual information (bits) between the last glyph unit of the left token and the first
glyph unit of the right token, minus its mean over 1,000 permutations of the right-hand first units within that set
(seed 761) — the shuffle-corrected coupling. p = (1 + #{perm ≥ observed}) / 1,001.
- **C_all:** all usable boundaries (definite + uncertain), tokens delimited by both markers.
- **C_def:** definite-space boundaries only (same tokenization).
- **C_unc:** uncertain-space boundaries only (same tokenization).
- **C_merged:** tokens merged across uncertain spaces (`,` treated as no space); coupling across the remaining definite
  spaces.
- **Size-matched comparison:** C_def recomputed on 1,000 random subsets of definite boundaries of the same size as the
  uncertain set, to compare C_unc with a same-N definite value (median and 95% range reported).
- **Reference (reported):** H-track value on the project data (the PHASE_757 D2 definition: within-line pairs, full
  within-line shuffle baseline) and the same D2 definition on ZL, as a second-transcription replication of C1212/C1563.

## Decision rules (locked)
- **ROBUST** — C_def ≥ 0.75 · C_all with p < 0.001, AND C_merged ≥ 0.75 · C_all with p < 0.001. The coupling is carried by
  definite word boundaries; the C1212/C1563/C2080 reliance on it stands.
- **SPACING-DEPENDENT** — C_def < 0.50 · C_all or C_merged < 0.50 · C_all. A large part of the coupling sits at doubtful
  boundaries. C1212, C1563 and C2080 are annotated; D2's role in C2080 is re-examined (C2080's verdict already holds
  without D2).
- **INTERMEDIATE** — anything else; the same rows are annotated with the numbers.
Reported without a verdict role: C_unc against the size-matched C_def (whether uncertain spaces behave like
within-word glyph transitions — stronger coupling — or like definite boundaries), and the ZL replication of D2.

## What this phase does not do
It does not measure physical space widths from the images (Rozanova & Temerev's method), and it does not re-segment the
H track. It uses the ZL transcribers' own judgement of which spaces are uncertain.
