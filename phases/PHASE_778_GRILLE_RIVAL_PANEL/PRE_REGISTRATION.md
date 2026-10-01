# PHASE_778 — Rival-generator panel II: the table-and-grille method (pre-registration)

**Status: DRAFT v1 for the lean-expert design audit (not locked).** The harness gates have run (mechanics only); the
fit stage (surface statistics only, no panel statistic) is running and its output `results/fit778.json` becomes the
variant table and is locked with this document. No discriminator has been computed on any grille corpus beyond the
dry run's illustrative members.

**Origin.** `SYSTEM/RESEARCH_AGENDA.md` Tier A #2 and `STRATEGIC_REVIEW_2026-09-27` §3 #5: the rival-generator panel,
Naibbe first (PHASE_757, C2080, EXCLUDED), the Rugg grille second. With Timm & Schinner's copy-and-modify generation
excluded (C2077), the table-and-grille method is the remaining public mechanism for producing Voynich-like text
without content. The Tier-0 sentence's closing clause ("not reproduced by copy-and-modify generation or by the Naibbe
cipher as published") is what this phase would extend or qualify.

**Question.** Can the table-and-grille method — as published by Rugg (2004), described step by step by Hyde & Rugg
(2014, "Hoaxing the Voynich Manuscript, part 7: producing the text"), extended by Rugg & Taylor (2016) and analysed by
Zandbergen (2021) — generate Currier B's text, as measured by the PHASE_757 discriminator panel?

**Mechanism, not content.** The method is a production device. Zandbergen (2021) notes that the same device can be
used as an enumeration system to encode meaningful text; a NOT EXCLUDED result would therefore not say "meaningless",
and an EXCLUDED result does not say "meaningful" (framework-as-null; C2052).

**Change control:** after the lock nothing below (families, fit grid, fitted configurations, statistics, criterion,
N, seeds) may change without a new phase number.

## The generator under test (`scripts/grille778.py`)
There is no author code. The implementation follows the published description; the two public implementations found
(antenore/voynich-toolkit `rugg_test.py`; adequatelimited/voynich M5 `m5_grille.py`) both place the grille at random
for every word and are used only as cross-reads, not as authority.

Published mechanics implemented (quotations from Hyde & Rugg 2014 unless noted):
- **Table.** "The table is divided into sets of three columns. Each of those sets contains one column that contains
  prefixes, another column that contains roots, and another column that contains suffixes." R rows deep ("about forty
  rows deep … more than enough to generate a page"), G column sets across. "The easiest way to fill the table in is one
  category at a time" with frequencies "similar to the frequencies in Voynichese"; "Some of the cells are empty. That's
  deliberate."
- **Grille.** A card with three holes, one per column, at different heights: row offsets (0, o1, o2), o1, o2 ∈ {0, 1, 2}
  (Zandbergen: a three-row window gives the distinct grilles).
- **Movement.** "You now need to move the grille across the table to produce the next word. However, you can't simply
  move it three cells to the right horizontally … move three cells across and one row up to produce the next word, and
  then move three more cells across and two rows down … The key thing is not to have any regular pattern in those
  vertical moves." Implemented as: next column set, plus a vertical shift δ drawn uniformly from {−d, …, d} (or a
  uniformly random row, d = R).
- **Lines.** "If you reach the end of the line before you reach the end of the table … you just move your grille back
  to the first three columns of the table, a bit further down, and repeat the process." Implemented as: at each new
  line, column set 0 and a downward shift of 1–3 rows (`pos = reset`). If the last column set is reached before the
  line ends ("use the grille in some way to generate more words"), the walker continues from column set 0 one row
  down. The alternative `pos = continue` (no reset at line starts) is declared as a second line rule.
- **Repeats.** "One option is simply to write it down and keep going. Another option is to move the grille further up
  or down so that you get a different word" (`repeat = keep` / `avoid`).
- **Several tables and grilles.** "You'll eventually need to produce a different table"; assistants "using different
  tables and grilles". Implemented as: a table set per scope unit (whole corpus, section, or folio), n_tab tables per
  unit, a different table taken up at a paragraph start with probability 0.5, a different grille at a line start with
  probability s_gr.
- **Word fragments.** Rugg's columns rest on Stolfi's prefix–midfix–suffix decomposition (Zandbergen 2021). Two parsers
  of B's words into (prefix, root, suffix) are declared: the project's morphology (articulator + PREFIX | MIDDLE |
  SUFFIX; 2,392 tokens the morphology cannot rebuild are kept whole as a root) and a Stolfi-layer split (first gallows,
  else first ch/sh/ee, is the root; M5's rule).

Variants beyond the published description (**STEELMAN**, reported separately):
- **Real rows** (Zandbergen's page-table construction; M5b): each row is a real B word split in three, so that a grille
  with holes at equal height reproduces attested words.
- **Frequency-ordered and length-ordered rows** (Rugg & Taylor's "semi-systematic" filling by increasing length;
  Zandbergen's frequency-ordered rows).
- **Chain rows:** rows arranged so that consecutive column sets follow B's word-edge glyph preferences (the next
  entry's first glyph unit drawn in proportion to B's edge-bigram count after the previous entry's last unit, floor
  0.1). This uses B's adjacent edge-glyph bigram table, the same exposure class as the G-EDGE positive control.

Not implemented (declared out of scope): paragraph-initial gallows and the top-line f/p rule (Zandbergen calls them
"prohibitive" for the method and they are not in the discriminator panel); word-space uncertainty; making words up at
the end of the table.

## Harness gates (mechanics only; `scripts/gates778.py` → `results/gates778.json`) — PASSED
- **G1 page reproduction** (Zandbergen 2021): a table whose rows are folio f26r's words split in three, read with the
  published line rule and no vertical wandering, reproduces the folio verbatim; with a grille whose holes sit at
  heights (0, 1, 2) and the root and suffix columns shifted accordingly, it reproduces it again (grille/shift
  equivalence). Both true.
- **G2 binomial word length** (Zandbergen Tables 4–6): three wheels of 24 fragments with length counts 3/9/9/3 over
  lengths 0–3, 0–3 and 1–4 give over their 13,824 combinations exactly 27, 243, 972, 2268, 3402, 3402, 2268, 972,
  243, 27. True.

## Declared families (not fitted): 4 × 3 × 2 × 2 = 48
| Axis | Values | Status |
|---|---|---|
| Row arrangement `order` | random (published filling) · freq · length · **chain** | random published; freq/length Rugg & Taylor / Zandbergen; chain STEELMAN |
| Vertical wandering `d` | 2 · 5 · R (uniform row) | published ("arbitrary number of rows up or down") |
| Line rule `pos` | reset (back to the first column set) · continue | reset published |
| Repeat rule `repeat` | keep · avoid | both published options |

Each family is run with noise V0 and V1 (below): **96 variants**. Group **published** = orders random, freq, length
(72 variants); group **steelman** = order chain (24 variants).

## Fit stage (`scripts/fit778.py`; surface statistics only) → `results/fit778.json`
For each family, the fitted parameters are chosen from this grid to minimise the mean scaled distance between the
generated corpora's surface statistics (N_FIT = 3 members, seeds 778,500,000 + 100,000·family + 10·config + member)
and B's:

| Fitted parameter | Grid |
|---|---|
| parser | morph · stolfi |
| rows | indep (published: one category at a time) · real (STEELMAN) |
| scope (table set per …) | all · section · folio |
| (R, G) | all: (40,16) (120,16) (250,20) (500,20); section: (40,16) (120,16) (250,20); folio: (40,8) (40,16) (80,16) |
| draw exponent α (cell draw weight = frequency^α) | 0.5 · 1.0 |
| n_tab (tables per unit; switch at paragraph starts with p 0.5) | 1 · 3 |
| s_gr (grille change at a line start) | 0.05 · 0.3 |
| grille set | all nine offsets · (0,0) only |

640 configurations per family. Distance = mean over six statistics of |generated − B| / scale:

| Statistic | B (P-text, 21,610 tokens, 2,299 lines, 80 folios) | Scale |
|---|---|---|
| word types | 4,640 | 500 |
| hapax type fraction | 0.669 | 0.05 |
| Zipf slope (top 1,000) | −1.051 | 0.10 |
| mean token length | 5.169 | 0.30 |
| adjacent-folio type Jaccard | 0.138 | 0.02 |
| distant-folio type Jaccard (≥ 10 folios apart) | 0.099 | 0.02 |

The best configuration per family is that family's variant. The fit uses no adjacency or order statistic. Fit quality
is reported per family; a family whose best distance exceeds 2.0 (two scale units on average) is flagged "no surface
fit" and is still run (SELF_CITATION_HEAD_TO_HEAD precedent: a fit failure is itself a finding). The attested-word
fraction is descriptive.

## Target skeleton, noise, controls, discriminators (PHASE_757, unchanged)
- **Skeleton:** Currier B, H track, P placement, labels excluded, uncertain tokens as blockers: 2,299 lines, 21,610
  certain tokens, 80 folios; sections S 1,059 lines, B 716, H 372, C 118, T 34; 457 paragraph-first lines. Every
  generated corpus carries B's blockers.
- **Noise:** V0 none; V1 the PHASE_757 H–F model (ρ 0.0679; edit-distance-1 glyph-unit edits).
- **Positive controls:** M1 (50-state class Markov; builds in D5, D6) and G-EDGE (PHASE_753 N2 edge-glyph generator;
  builds in D2, D6), N = 1,000 each; B + V1 noise reference, N = 50. Re-run here (seeds 778,9xx,xxx) rather than
  inherited; the skeleton is asserted identical to PHASE_757's.
- **Discriminators** (`panel_stats.py`, unchanged): D2 edge-glyph MI, D3 adjacent repetition, D4 cross-folio trigram
  recurrence, D5 order information beyond edge coupling, D6 zone dependence. Descriptives: types, hapax fraction,
  Zipf slope, mean length, duplicate lines, max identical run, e-run lag-1, max qok window; empty-cell redraws.
- **Outside criterion:** B is outside ensemble X on discriminator j if B lies outside X's [min, max] and
  |B − mean| / sd > z\*, z\* = Φ⁻¹(1 − 0.005/k) (k = number of usable discriminators; sd = 0: the [min, max] leg alone).
- **Certification:** discriminator j is usable if B is not outside at least one positive control; record which
  control certified it and whether that control builds it in. k fixed at this step.
- **Exclusion:** a variant excludes if n_out ≥ 2 and at least one outside discriminator was certified by a control that
  does not build it in.
- N = 1,000 members per variant (seed 778,000,000 + 10,000·variant + member). **Rerun rule:** a variant that does not
  exclude is rerun once with a fresh seed block (+5,000,000), N = 1,000; it counts as non-excluding only if the rerun
  also fails to exclude.

## Decision rules (locked)
- **EXCLUDED** — every variant of both groups excludes. Registry: a Tier-2 negative-knowledge row "the table-and-grille
  method, as published and in the declared steelman forms, excluded as a generator of Currier B on {discriminators}";
  the Tier-0 sentence's closing clause extended ("… or by the table-and-grille method"); scope notes as for C2080.
  Not evidence for any content reading.
- **NOT EXCLUDED** — at least one variant fails to exclude after its rerun. Registry: a Tier-2 row naming the
  variant(s) and the k − n_out discriminators on which B is inside; the Tier-0 sentence is not extended; flag for human
  review of C120, C173 and the Tier-0 scope. If only steelman variants survive, the published method is reported
  EXCLUDED and the steelman NOT EXCLUDED, with what the steelman adds named.
- **PARTIAL** — reported alongside: outcomes per axis (order, d, pos, repeat, noise), per group, and the verdict with
  D2 removed. Never changes the verdict.
- **HARNESS-FAIL** — a gate fails; no verdict.

## What each outcome means
- **EXCLUDED.** No table-and-grille device within the declared families and fitted grids produces B's combination of
  word-boundary coupling (D2), chance-level adjacent repetition (D3), cross-folio trigram recurrence (D4), low order
  information beyond edge coupling (D5) and line-zone vocabulary (D6). Scope: the published method, its published
  options, and the declared steelman forms, with tables fitted to B's own fragment inventories and composition
  statistics (the strongest available form, not a strawman). Not excluded: a device with rules beyond these (for
  example position-aware tables, table rows fitted to B's transitions beyond edge glyphs, or hand-chosen moves that
  track the text), the three-wheel enumeration system as a cipher of meaningful text (Zandbergen), or any other
  production method. Not evidence of meaning.
- **NOT EXCLUDED.** A device of the named form reproduces B's profile on the panel. That would be the first
  content-free mechanism to do so (Timm and Naibbe failed), and it would require the Tier-0 scope and the
  engineered-substrate readings to be revisited by the human. It would not show that B is meaningless: the device can
  encode.

## Declared prior knowledge and exposure
- **B supplied before the lock:** its skeleton with sections and paragraph-first flags; its unigram token frequencies
  and the fragment inventories under both parsers (composition only); its six surface statistics above (composition);
  its adjacent edge-glyph bigram table (chain rows only; the G-EDGE exposure class); its D2–D6 values, known since
  PHASE_757 and recomputed in the controls stage, never used in the fit.
- **Not computed on B before the lock:** no new order statistic. The fit stage reads no adjacency, order or position
  statistic of B.

## Procedure
1. Gates (done); fit stage (running); this draft committed with `results/fit778.json`.
2. Lean-expert design audit; edits; confirmation pass.
3. `run778.py --checksums`, commit, tag `phase778-lock`.
4. `run778.py controls` (certification before any grille comparison is read), `run778.py panel`, `run778.py verdict`
   (rerun rule inside); raw results committed before the write-up; lean-expert results check.
5. Dry run (`run778.py --dry`, two variants × three members and the evaluation logic) runs before the lock.

**Dry run (pre-fit fallback variants, N = 3, illustrative only):** a published-style variant (random rows, d 5, reset,
keep, 40 × 16 table, V0) gave D2 0.07–0.08, D3 −0.4 to −0.6, D4 5.3–5.5, D5 3.5–3.7, D6 0.52–0.54; a chain variant
(d 2, V1) D2 0.02–0.03, D4 2.6–3.0, D5 1.7, D6 0.5–0.6; an M1 control member D2 0.007, D5 0.037, D6 0.042. All code
paths ran.

## Caveats
- **Our implementation of a prose description.** The movement, line and repeat rules are implemented as written by
  Hyde & Rugg; where the description leaves a choice (vertical shift range, line-start shift, end-of-table behaviour,
  grille and table changes) the choice is a declared axis or a fitted parameter. A reader who holds that the method
  means something else has a new test.
- **The fit gives the device B's composition.** Tables are drawn from B's own fragment inventories and sized to B's
  vocabulary statistics; this is deliberate (strongest form) and means the panel tests sequence and position
  structure, not vocabulary.
- **Runtime.** Fit about 3 h; controls about 25 min; panel 96 × 1,000 members at about 1–3 s each, about 6 h at Idle
  priority with 6 workers; rerun as needed.
