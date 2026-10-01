# PHASE_778 — Rival-generator panel II: the table-and-grille method (pre-registration)

**Status: v3, for lock.** The lean-expert design audit (LOCKABLE WITH EDITS, fifteen edits) and its confirmation
pass (LOCKABLE once eight further edits are in; no further audit pass needed) are both incorporated. The fit stage
with its declared extension, the pre-lock controls C1–C5 and the per-variant banding have run; C2 failed as declared
and the FITTED bar is calibrated on that control as ruled. No discriminator has been computed on
any grille corpus beyond the dry run's illustrative members and the pre-lock controls declared here.

**Origin.** `SYSTEM/RESEARCH_AGENDA.md` Tier A #2 and `STRATEGIC_REVIEW_2026-09-27` §3 #5: the rival-generator panel,
Naibbe first (PHASE_757, C2080, EXCLUDED), the Rugg grille second. With copy-and-modify generation (C2077) and the
Naibbe cipher as published (C2080) excluded, the table-and-grille method is the next rival named in the strategic
review. It is not the only untested mechanism for producing text without a message: improvisation in a practised
script at book scale is untested (STATUS_BRIEF §4; PHASE_764 unresolved at folio scale). The Tier-0 sentence's closing
clause ("not reproduced by copy-and-modify generation or by the Naibbe cipher as published") is what this phase would
propose to extend, for human sign-off, if the PUBLISHED tier is EXCLUDED. A NOT EXCLUDED result leaves the clause
unchanged and adds the method to the not-excluded rivals in STATUS_BRIEF §4.

**Question.** Does any declared variant of the table-and-grille method, with its composition fitted to Currier B,
produce an ensemble whose D2–D6 values contain B's? The panel measures five line- and junction-level statistics.
Containing B on them is necessary, not sufficient, for generating B's text.

**Mechanism, not content.** The method is a production device. Zandbergen (2021) notes that the same device can be
used as an enumeration system to encode meaningful text; a NOT EXCLUDED result would therefore not say "meaningless",
and an EXCLUDED result does not say "meaningful" (framework-as-null; C2052). An EXCLUDED result does not exclude table
devices with other filling, placement or movement rules, and does not say that B carries a message.

**Change control:** after the lock nothing below (families, tiers, fit grid, fitted configurations, statistics,
criterion, N, seeds) may change without a new phase number.

## The generator under test (`scripts/grille778.py`)
There is no author code. The implementation follows the published description; the two public implementations found
(antenore/voynich-toolkit `rugg_test.py`; adequatelimited/voynich M5 `m5_grille.py`) both place the grille at random
for every word; that placement rule is declared as a variant below (EXTENDED), with those implementations cited as its
source, not as authorities. **Quote check:** every Hyde & Rugg (2014) quotation below was verified verbatim against
the source page before the lock (`results/hyde_rugg_2014_part7.html`, fetched 2026-09-30).

Published mechanics implemented (quotations from Hyde & Rugg 2014, "Hoaxing the Voynich Manuscript, part 7:
producing the text"):
- **Table.** "The table is divided into sets of three columns. Each of those sets contains one column that contains
  prefixes, another column that contains roots, and another column that contains suffixes." R rows deep ("If your
  table is about forty rows deep, that's usually more than enough to generate a page of text"), G column sets across.
  "The easiest way to fill the table in is one category at a time"; "Their relative frequencies are similar to the
  frequencies in Voynichese"; "Some of the cells are empty. That's deliberate."
- **Grille.** A card with three holes, one per column, at different heights: row offsets (0, o1, o2). PUBLISHED reads
  Hyde & Rugg's "different heights" as three distinct heights (`distinct`: o1, o2 ∈ {1, …, 4}, o1 ≠ o2; 12 grilles
  within a five-row window). Grilles with exactly two holes level, and the same-height grille, belong to the `all` and
  `same` sets and are EXTENDED.
- **Movement.** "You now need to move the grille across the table to produce the next word. However, you can't simply
  move it three cells to the right horizontally." "So, for example, you might move three cells across and one row up
  to produce the next word, and then move three more cells across and two rows down"; "The key thing is not to have
  any regular pattern in those vertical moves". Implemented as: next column set, plus a vertical shift drawn uniformly
  from {−d, …, d}.
- **Lines.** "you just move your grille back to the first three columns of the table, a bit further down, and repeat
  the process." Implemented as: at each new line, column set 0 and a downward shift of 1–3 rows (`pos = reset`). If
  the last column set is reached before the line ends ("One is to use the grille in some way to generate more
  words"), the walker continues from column set 0 one row down.
- **Repeats.** "One option is simply to write it down and keep going. Another option is to move the grille further up
  or down so that you get a different word" (`repeat = keep` / `avoid`).
- **Several tables and grilles.** "You'll eventually need to produce a different table"; assistants "using different
  tables and grilles". Implemented as: a table set per scope unit (whole corpus, section, or folio), n_tab tables per
  unit, a different table taken up at a paragraph start with probability 0.5, a different grille at a line start with
  probability s_gr (or at every word, `s_gr = word`).
- **Word fragments.** Rugg's columns rest on Stolfi's prefix–midfix–suffix decomposition (Zandbergen 2021). Two parsers
  of B's words into (prefix, root, suffix) are declared: the project's morphology (articulator + PREFIX | MIDDLE |
  SUFFIX; 2,392 tokens the morphology cannot rebuild are kept whole as a root, 243 distinct) and a Stolfi-layer split
  (first gallows, else first ch/sh/ee, is the root; M5's rule).

**Ensemble definition.** Each member draws fresh tables (fragment sampling, row order, cell fill) and a fresh walk. A
variant is a family of devices, not one table. Rows are never placed in transcript order; the G1 reading-order table
is a harness gate only.

Declared beyond the published description:
- **EXTENDED** (published sources beyond the Hyde & Rugg description): frequency-ordered and length-ordered rows
  (Rugg & Taylor's "semi-systematic" filling; Zandbergen's frequency-ordered rows); uniform vertical wandering
  (d = R); the `continue` line rule; real rows, each a real B word split in three (Zandbergen 2021's page-table
  construction; M5b); the same-height grille (holes at one height, `same`, with which a real row is a word); per-word
  random placement (a uniformly random row and column set for every word, `d = RP`, the public implementations'
  rule); a new grille at every word (`s_gr = word`). A table per page is `scope = folio` with n_tab 1; tables per
  hand are approximated by `scope = section`, since the Davis hands fall along section lines.
- **STEELMAN-EXPOSED** (built from B's adjacent edge-glyph bigram table, the G-EDGE exposure class; D2 built in):
  **chain rows** (rows arranged so that consecutive column sets follow B's word-edge glyph preferences: the next
  entry's first glyph unit drawn in proportion to B's edge-bigram count after the previous entry's last unit, floor
  0.1) and **junction redraw** ("After placing the grille, accept the word with probability P_B(first unit | previous
  last unit) / max over first units; otherwise shift the grille vertically (within ±d) and redraw, at most 10 tries,
  then keep": the Hyde & Rugg licence to move the grille for a better word, extended to junctions).

Out of scope, with consequences stated:
- Line-edge conventions (paragraph-initial gallows, the top-line f/p rule, line-final -m; Zandbergen: "prohibitive"
  for the method): D6 and line-edge results for `continue` and per-word-placement variants say nothing about a hoaxer
  who adds line-start or line-end conventions.
- Filling the table from B's own page in reading order presupposes B's text; copying is C2077's ground. The
  admissible form, real rows from B's words in non-transcript order, is in EXTENDED.
- Word-space uncertainty; making words up at the end of the table.

## Harness gates (mechanics only; `scripts/gates778.py` → `results/gates778.json`) — PASSED
- **G1 page reproduction** (Zandbergen 2021): a table whose rows are folio f26r's words split in three, read with the
  published line rule and no vertical wandering, reproduces the folio verbatim; with holes at heights (0, 1, 2) and
  the root and suffix columns shifted accordingly, it reproduces it again (grille/shift equivalence). Both true.
- **G2 binomial word length** (Zandbergen Tables 4–6): three wheels of 24 fragments with length counts 3/9/9/3 over
  lengths 0–3, 0–3 and 1–4 give over their 13,824 combinations exactly 27, 243, 972, 2268, 3402, 3402, 2268, 972,
  243, 27. True.

## Tiers, families and variants
| Tier | Row arrangement `order` | Walk (d, pos) | repeat | redraw | Fit grid | Families |
|---|---|---|---|---|---|---|
| **PUBLISHED** | random | (2, reset), (5, reset) | keep, avoid | no | restricted: rows indep, grilles distinct | 4 |
| **EXTENDED** | random, freq, length | (2, reset), (2, continue), (5, reset), (5, continue), (R, reset), (R, continue), (RP, continue) | keep, avoid | no | full | 42 |
| **STEELMAN-EXPOSED** | chain (walks without RP) | the seven walks | keep | no | full | 6 |
| | random | the seven walks | keep | yes | full | 7 |
| | chain (walks without RP) | the six walks | keep | yes | full | 6 |

65 families × noise {V0, V1} = **130 variants**. (The four PUBLISHED families also appear in EXTENDED under the full
fit grid; if the full fit selects the restricted configuration the two variants coincide and are reported once.)

## Fit stage (`scripts/fit778.py`; surface statistics only) → `results/fit778.json`
**Fit groups.** The surface statistics depend on the walk (d, pos, repeat, redraw) but not on the row arrangement:
the walk visits the same cells whatever is written in them, and over a corpus its row distribution is uniform. One
fit per (d, pos, repeat, redraw) group is therefore shared by that group's random / freq / length / chain families
(the panel's descriptives verify this per variant). 25 fits: 21 full-grid groups and 4 restricted PUBLISHED groups.

| Fitted parameter | Grid |
|---|---|
| parser | morph · stolfi |
| rows | indep (published: one category at a time) · real (EXTENDED) |
| scope (table set per …) | all · section · folio |
| (R, G) | all: (40,16) (120,16) (500,20); section: (40,16) (120,16) (250,20); folio: (40,8) (40,16) (80,16) |
| draw exponent α (cell draw weight = frequency^α) | 0.5 · 1.0 |
| n_tab (tables per unit; switch at paragraph starts with p 0.5) | 1 · 3 |
| s_gr (grille change at a line start, or at every word) | 0.05 · 0.3 · word |
| grille set | distinct (12) · all nine offsets within three rows · same (0,0) |

1,296 configurations (216 restricted) in the base grid, plus the extension below. Distance = mean over nine composition statistics of |generated − B| / scale,
N_FIT = 2 members per configuration (seeds 778,500,000 + 100,000·group + 10·config + member); the selected
configuration is re-evaluated on 10 fresh seeds (778,600,000 + 1,000·group + member) and that distance is the one
reported and banded (winner's curse). **Scales are declared tolerances, not sampling SDs.** The variant table reports
each statistic's raw deviation; a fit whose distance owes more than half its value to one statistic is flagged.

| Statistic | B (P-text, 21,610 tokens, 2,299 lines, 80 folios) | Scale |
|---|---|---|
| word types | 4,640 | 500 |
| hapax type fraction | 0.669 | 0.05 |
| Zipf slope (top 1,000) | −1.051 | 0.10 |
| mean token length (EVA characters) | 5.169 | 0.30 |
| adjacent-folio type Jaccard (folio order, C361; not token order) | 0.138 | 0.02 |
| distant-folio type Jaccard (≥ 10 folios apart) | 0.099 | 0.02 |
| Jensen–Shannon divergence of the token-length (glyph units) distribution from B's | 0 | 0.02 bits |
| Jensen–Shannon divergence of the first-glyph-unit distribution | 0 | 0.02 bits |
| Jensen–Shannon divergence of the last-glyph-unit distribution | 0 | 0.02 bits |

**Fit bands.** FITTED: fresh distance (10 seeds) ≤ 1.165, the larger of the two positive controls' distances on the
same nine statistics and scales (M1 1.165; G-EDGE 0.933; control C2). **This bar is calibrated on the M1 control.**
It replaces the declared tolerance of 1.0, which C2 failed: no with-replacement resampler of B reaches B's hapax
share or type count. The bar was set after the grille fit distances were seen, and was not rounded for that reason
(the code uses the control's unrounded value, 1.1647). PARTIAL ≤ 2.0 remains a declared tolerance; > 2.0 UNFITTED.
Tier labels are reported under both bars (declared 1.0 and calibrated 1.165). Matching M1's total distance is not
the same as matching where it matters: M1 fails on the frequency tail (hapax share, type count), the grille on the
Zipf slope, the first-glyph-unit divergence and the adjacent-folio Jaccard; a composition-attribution table (below)
answers "excluded because of composition" descriptively, and cannot carry a D2 shortfall of 0.2 bits (a 0.027-bit
first-glyph divergence does not cap a shuffle-corrected mutual information near 0.001). **Bands are assigned per
variant** (`scripts/band778.py` → `results/variant_bands778.json`): configurations are selected per walk group and
shared across row arrangements, but with small vertical moves and the line reset the walk visits only part of the
rows, so freq-, length- and chain-ordered rows place different content in the visited cells, and V1 noise edits
tokens; each variant is banded on its own fresh 10-seed distance with its own row arrangement and noise level.
UNFITTED variants are run and reported but do not count toward a panel EXCLUDED. If no variant in a tier is FITTED or
PARTIAL, that tier is recorded as "EXCLUDED ON SURFACE (no declared configuration reaches B's composition)", a
separate and weaker category than panel exclusion. The attested-word fraction is descriptive. **Extension-selected
groups:** the selection follows the declared N_FIT rule; where the kept base selection has a slightly higher fresh
distance than the extension's candidate (one group, 1.18 against 1.15), the candidate's fresh distance is recorded as
a descriptive value and the selection is not switched.

**Grid extension (`scripts/fit_extend778.py`; declared after the base fit, before the lock, composition only).** The
base fit left every group short on hapax share and type count (a device re-reads its cells). To give the device its
best shot, the grid was extended toward richer tables: a larger per-folio table (250 × 20) at all three draw
exponents, and a flatter exponent α 0.25 at every scope and size (864 new configurations per full group, 144 per
restricted group; seeds offset by 20,000 configurations). A group's selection is replaced when a new configuration has
a lower N_FIT distance; the base selection is kept in the record alongside. The extension replaced the selection in 6
of 25 groups.

**Fit results (final; `results/fit778.json`).** Every group is PARTIAL. The selection chooses the Stolfi-layer
parser, real rows (EXTENDED) wherever the grid allows them, draw exponent 1.0 everywhere, and section- or folio-scope
tables; the restricted PUBLISHED groups (independent columns, holes at distinct heights) sit at 1.51–1.56, the full
groups at 1.12–1.33. The dominant deviations are type count or hapax share (the device trades one for the other), the
Zipf slope (about −0.85 against B's −1.05, two scale units), the adjacent-folio Jaccard, and the first-glyph-unit
distribution (about 0.027 bits). Per group:

| Fit group (d / line rule / repeat / redraw / grid) | Selected configuration | Base fresh | Extension fresh | Final | Dominant deviation (share) |
|---|---|---|---|---|---|
| d2/reset/avoid/noredraw/restricted | stolfi / indep / section 120×16 / α 1.0 / n_tab 1 / s_gr 0.05 / distinct | 1.56 | 1.59 | **1.56 PARTIAL** | hapax 0.31 |
| d2/reset/keep/noredraw/restricted | stolfi / indep / section 250×20 / α 1.0 / n_tab 3 / s_gr word / distinct | 1.55 | 1.57 | **1.55 PARTIAL** | types 0.31 |
| d5/reset/avoid/noredraw/restricted | stolfi / indep / section 40×16 / α 1.0 / n_tab 3 / s_gr 0.05 / distinct | 1.51 | 1.56 | **1.51 PARTIAL** | hapax 0.32 |
| d5/reset/keep/noredraw/restricted | stolfi / indep / section 250×20 / α 1.0 / n_tab 1 / s_gr 0.05 / distinct | 1.54 | 1.56 | **1.54 PARTIAL** | hapax 0.21 |
| d2/continue/avoid/noredraw/full | stolfi / real / all 500×20 / α 1.0 / n_tab 1 / s_gr word / all | 1.18 | 1.18 | **1.18 PARTIAL** | hapax 0.21 |
| d2/continue/keep/noredraw/full | stolfi / real / all 500×20 / α 1.0 / n_tab 1 / s_gr 0.05 / all | 1.12 | 1.15 | **1.12 PARTIAL** | hapax 0.38 |
| d2/continue/keep/redraw/full | stolfi / real / all 500×20 / α 1.0 / n_tab 1 / s_gr word / all | 1.30 | 1.25 | **1.30 PARTIAL** | hapax 0.22 |
| d2/reset/avoid/noredraw/full | stolfi / real / folio 250×20 / α 1.0 / n_tab 3 / s_gr word / all | 1.17 | 1.18 (selected) | **1.18 PARTIAL** | types 0.35 |
| d2/reset/keep/noredraw/full | stolfi / real / folio 80×16 / α 1.0 / n_tab 1 / s_gr word / all | 1.20 | 1.16 | **1.20 PARTIAL** | types 0.33 |
| d2/reset/keep/redraw/full | stolfi / real / folio 40×16 / α 1.0 / n_tab 3 / s_gr word / all | 1.28 | 1.25 | **1.28 PARTIAL** | types 0.25 |
| d5/continue/avoid/noredraw/full | stolfi / real / folio 250×20 / α 1.0 / n_tab 1 / s_gr word / all | 1.16 | 1.14 (selected) | **1.14 PARTIAL** | types 0.36 |
| d5/continue/keep/noredraw/full | stolfi / real / folio 250×20 / α 1.0 / n_tab 1 / s_gr word / all | 1.16 | 1.15 (selected) | **1.15 PARTIAL** | types 0.36 |
| d5/continue/keep/redraw/full | stolfi / real / section 40×16 / α 1.0 / n_tab 3 / s_gr 0.05 / all | 1.26 | 1.25 | **1.26 PARTIAL** | hapax 0.36 |
| d5/reset/avoid/noredraw/full | stolfi / real / section 250×20 / α 1.0 / n_tab 3 / s_gr word / all | 1.18 | 1.15 | **1.18 PARTIAL** | types 0.30 |
| d5/reset/keep/noredraw/full | stolfi / real / folio 250×20 / α 1.0 / n_tab 3 / s_gr word / all | 1.22 | 1.14 (selected) | **1.14 PARTIAL** | types 0.37 |
| d5/reset/keep/redraw/full | stolfi / real / folio 250×20 / α 1.0 / n_tab 1 / s_gr word / all | 1.34 | 1.26 (selected) | **1.26 PARTIAL** | types 0.26 |
| dR/continue/avoid/noredraw/full | stolfi / real / section 250×20 / α 1.0 / n_tab 3 / s_gr word / all | 1.13 | 1.18 | **1.13 PARTIAL** | types 0.35 |
| dR/continue/keep/noredraw/full | stolfi / real / section 120×16 / α 1.0 / n_tab 3 / s_gr 0.3 / all | 1.20 | 1.20 | **1.20 PARTIAL** | types 0.28 |
| dR/continue/keep/redraw/full | stolfi / real / section 120×16 / α 1.0 / n_tab 3 / s_gr word / all | 1.27 | 1.27 | **1.27 PARTIAL** | js_first 0.27 |
| dR/reset/avoid/noredraw/full | stolfi / real / folio 250×20 / α 1.0 / n_tab 1 / s_gr word / all | 1.21 | 1.17 (selected) | **1.17 PARTIAL** | types 0.37 |
| dR/reset/keep/noredraw/full | stolfi / real / section 120×16 / α 1.0 / n_tab 1 / s_gr 0.05 / all | 1.19 | 1.17 | **1.19 PARTIAL** | hapax 0.41 |
| dR/reset/keep/redraw/full | stolfi / real / all 500×20 / α 1.0 / n_tab 3 / s_gr 0.3 / all | 1.33 | 1.27 | **1.33 PARTIAL** | js_first 0.26 |
| dRP/continue/avoid/noredraw/full | stolfi / real / section 40×16 / α 1.0 / n_tab 3 / s_gr 0.05 / all | 1.20 | 1.16 | **1.20 PARTIAL** | hapax 0.36 |
| dRP/continue/keep/noredraw/full | stolfi / real / section 250×20 / α 1.0 / n_tab 3 / s_gr word / all | 1.16 | 1.19 | **1.16 PARTIAL** | types 0.35 |
| dRP/continue/keep/redraw/full | stolfi / real / section 250×20 / α 1.0 / n_tab 3 / s_gr 0.05 / all | 1.27 | 1.26 | **1.27 PARTIAL** | js_first 0.27 |

Consequence under the decision rules: no tier has a FITTED variant, so the strongest available verdict is "EXCLUDED
(PARTIAL FITS ONLY)"; a NOT EXCLUDED verdict remains reachable from any PARTIAL variant.

## Target skeleton, noise, controls, discriminators (PHASE_757, unchanged)
- **Skeleton:** Currier B, H track, P placement, labels excluded, uncertain tokens as blockers: 2,299 lines, 21,610
  certain tokens, 80 folios; sections S 1,059 lines, B 716, H 372, C 118, T 34; 457 paragraph-first lines. Every
  generated corpus carries B's blockers.
- **Noise:** V0 none; V1 the PHASE_757 H–F model (ρ 0.0679; edit-distance-1 glyph-unit edits).
- **Positive controls:** M1 (50-state class Markov; builds in D5, D6) and G-EDGE (PHASE_753 N2 edge-glyph generator;
  builds in D2, D6), N = 1,000 each, re-run here (seeds 778,9xx,xxx); B + V1 noise reference, N = 50. The skeleton is
  asserted identical to PHASE_757's.
- **Discriminators** (`panel_stats.py`, unchanged): D2 edge-glyph MI, D3 adjacent repetition, D4 cross-folio trigram
  recurrence, D5 order information beyond edge coupling, D6 zone dependence.
- **PHASE_757 certification table** (`controls_certification.json`; the controls stage here re-certifies with new
  seeds and the independently certified set is fixed at that step):

| Discriminator | B | M1 mean (z_B) | G-EDGE mean (z_B) | Certified by | Independently certified (certifier does not build it in) |
|---|---|---|---|---|---|
| D2 | 0.228 | 0.009 (+141) | 0.238 (−1.7) | G-EDGE | no |
| D3 | 0.015 | 0.299 (−3.7) | 0.107 (−1.0) | G-EDGE | **yes** |
| D4 | 2.474 | 0.690 (+2.5) | 0.515 (+2.9) | M1, G-EDGE | **yes** |
| D5 | 0.040 | 0.040 (+0.1) | 0.020 (+4.2) | M1 | no |
| D6 | 0.172 | 0.048 (+36) | 0.186 (−2.4) | G-EDGE | no |

  D6 is certified only by a control that builds it in, so it cannot be the independently certified outside
  discriminator; an exclusion needs D3 or D4 outside. For `pos = reset` variants, D5 and D6 count as one discriminator
  in n_out if the column-lock control (C3) puts D5 above the M1 ensemble's 99th percentile (under the reset rule each
  line position is locked to one column set's vocabulary, which can push D5 and D6 outside together).
- **Counted discriminators:** PUBLISHED and EXTENDED, the usable set (k = 5, z\* = 3.09); STEELMAN-EXPOSED, the usable
  set without D2 (k = 4, z\* = 3.02), since D2 is built in from B's junction table.
- **Outside criterion:** B is outside ensemble X on discriminator j if B lies outside X's [min, max] and
  |B − mean| / sd > z\*, z\* = Φ⁻¹(1 − 0.005/k) (sd = 0: the [min, max] leg alone).
- **Exclusion:** a variant excludes if n_out ≥ 2 (after the D5/D6 merge where it applies) and at least one outside
  discriminator is independently certified (D3 or D4).
- **N and the pooled rerun:** N = 1,000 members per variant (seed 778,000,000 + 10,000·variant + member). A variant not
  excluded at N = 1,000 is rerun with a fresh seed block (+5,000,000; N = 1,000), and the decision is taken on the
  pooled N = 2,000 ensemble (outside = beyond the pooled [min, max] and |z| > z\*). Both runs are reported. For every
  variant and discriminator the report gives B's z and B's rank among members. Any tier verdict that rests on a
  variant with B's |z| between z\* and 4.0 on a counted outside discriminator is labelled BORDERLINE.
- **D5 NaN rule.** The numerical warning in D5's held-out gain was classified before the lock: it arises when a
  training fold has no hapax (Good–Turing UNK mass n1/N = 0) and a held-out token is unseen, so the held-out event has
  zero model probability under both models and that member's D5 is undefined (not a 0·log 0 term). A variant's D5
  envelope uses non-NaN members only if the NaN rate is ≤ 5%; above 5%, D5 is dropped for that variant, k falls by one
  and z\* is recomputed. NaN counts are reported for every variant. Members are never imputed.
- **Composition-attribution table (descriptive, no role in the verdict).** For each excluded variant, its outside
  discriminators are listed beside the deviations of the composition statistics most closely tied to them, with the
  mapping fixed now: first-glyph-unit divergence ↔ D2; Zipf slope, type count and hapax share ↔ D3, D4;
  adjacent- and distant-folio Jaccard ↔ D4.
- **Descriptives (no verdict role):** types, hapax fraction, Zipf slope, mean length, duplicate lines, max identical
  run, e-run lag-1, max qok window; the number of repeated within-line 5-token windows (C2091's statistic; B's known
  value 0, no new computation on B); the share of generated tokens that combine a whole-word root (one the morphology
  could not split) with non-empty affixes; empty-cell, repeat and junction redraw counts.

## Pre-lock controls (`scripts/prelock_controls778.py` → `results/prelock_controls778.json`; generated corpora and
PHASE_757's control ensembles only)
- **C1 self-consistency (false-exclusion rate).** The best-fit variant of each tier plus four randomly chosen declared
  variants; for each, an ensemble of 500 members and 50 held-out members of the same variant (V1 against V1); each
  held-out member is tested with the exclusion rule against its own ensemble. **Pass: at most 2% excluded overall.**
  Otherwise the outside rule is miscalibrated for grille ensembles and must be fixed before the lock. (500 rather
  than 1,000 members makes the envelope narrower and the estimate conservative.)
- **C2 surface-band sanity.** The nine-statistic distance for 10 M1 and 10 G-EDGE members; both must be FITTED
  (≤ 1.0); each statistic's share reported.
- **C3 column-lock control.** Tokens drawn i.i.d. from the best PUBLISHED fit's column-set vocabulary at each token's
  column set under the reset line rule (no walk, no memory), 20 corpora; D5 and D6 reported; the D5/D6 merge for
  reset variants applies if the control's mean D5 lies above PHASE_757's M1 ensemble 99th percentile.
- **C4 near-fit sensitivity (post-lock stage `nearfit`; rule locked now).** Per walk group, the top 3 configurations
  by fit distance, or all within +0.1 of the best (within the recorded top 5), run on the group's representative
  variant (its random-order V0 family) at N = 200. If any alternate is inside, every family of that walk group is
  labelled UNSTABLE-TO-FIT in the report and the registered row; the verdict rule is unchanged. With the recorded
  top-5 lists, 100 alternates run (four per group).
- **C5 steelman plant check.** Chain rows and junction redraw at their most favourable settings (d = 0, `continue`,
  same-height grille): each must reach at least 50% of PHASE_757's G-EDGE mean D2 (0.238; threshold 0.119; the
  reference is G-EDGE, not B). A generator that fails is relabelled "junction plant did not transmit" and its D2
  shortfall is reported as an implementation fact, not a fact about the method.

**Results (`results/prelock_controls778.json`, generated corpora and PHASE_757 ensembles only):**
- **C1 PASS.** 0 of 350 held-out members excluded (seven variants: the best-fit variant of each tier and four random
  draws, 500-member ensembles, 50 held-out each): the outside/exclusion rule does not falsely exclude grille members.
- **C2 FAIL as declared.** Mean nine-statistic distance: M1 1.165 (PARTIAL), G-EDGE 0.933 (FITTED). The
  deviations are the resampling effect: M1 hapax share 0.395 against B's 0.669 (5.5 scale units), types 3,426
  against 4,640 (2.4), distant-folio Jaccard 0.130 against 0.099 (1.6); G-EDGE hapax 0.467 (4.1),
  types 3,651 (2.0), distant Jaccard 0.129 (1.5); every other statistic within half a scale unit. Any
  generator that redraws B's tokens with replacement collapses B's long tail and blurs its folio vocabulary.
  **Proposed recalibration (a pre-lock change prompted by this control; subject to the confirmation pass):** FITTED
  ≤ 1.2, the distance of B's own class-conditional resampler (M1) rounded up, since a device cannot be required to
  reach a composition that B's own resampler does not; PARTIAL ≤ 2.0 unchanged. Consequence for the fit table: the
  fourteen full no-redraw groups (1.12–1.20) become FITTED; the redraw groups (1.26–1.33) and the restricted
  PUBLISHED groups (1.51–1.56) stay PARTIAL. The PUBLISHED tier therefore has no FITTED variant under either bound.
- **C3: no merge.** Column-lock control D5 0.029, D6 0.032; PHASE_757's M1 D5 99th percentile 0.051. D5 and D6
  count separately for all variants.
- **C5 PASS.** Chain rows D2 0.437, junction redraw D2 0.174, threshold 0.119 (half of G-EDGE's
  0.238): both steelmen transmit junction coupling.
- A numerical warning in D5's held-out gain (a zero probability inside log2) appears on some grille corpora; D5 was
  finite on all 15 fitted-variant corpora checked, and the verdict reports the non-NaN member count per variant.

## Decision rules (locked)
Per tier:
- **EXCLUDED** if every FITTED or PARTIAL variant excludes on the pooled ensemble and at least one variant in the tier
  is FITTED. Registered as Tier-2 negative knowledge, scoped to "the table-and-grille method as implemented here from
  Rugg (2004) and Hyde & Rugg (2014), at the declared families, fitted to B's composition". If PUBLISHED and EXTENDED
  are both EXCLUDED, propose for human sign-off the Tier-0 clause "… not reproduced by copy-and-modify generation, by
  the Naibbe cipher as published, or by the table-and-grille method as implemented from its published description."
  If only PUBLISHED is EXCLUDED, the proposed clause reads "… as described by Hyde & Rugg (2014)", and the EXTENDED
  survivors are named. STEELMAN-EXPOSED never enters Tier-0 wording.
- **EXCLUDED (PARTIAL FITS ONLY)** if every FITTED or PARTIAL variant of a tier excludes but none is FITTED. This is
  registered as Tier-2 negative knowledge, with the qualifier and the tier's best distance in the row. For the Tier-0
  proposal, a PUBLISHED result of EXCLUDED (PARTIAL FITS ONLY) counts as EXCLUDED only if EXTENDED is fully EXCLUDED;
  the qualifier is then quoted in the proposal for human sign-off.
- **EXCLUDED ON SURFACE** if no family in the tier is FITTED or PARTIAL.
- **NOT EXCLUDED** if any FITTED or PARTIAL variant has n_out ≤ 1, or no independently certified outside
  discriminator, on the pooled ensemble. Registered as "not excluded by the PHASE_757 panel", naming the variant, its
  fitted configuration and the discriminators on which B is inside. This is not evidence that B was produced by the
  method, nor that B is meaningless. Human review flag: C119, C120, C173, STATUS_BRIEF §4.
- **PARTIAL** — reported alongside: outcomes per axis (order, d, pos, repeat, redraw, noise) and the tier verdicts
  with D2 removed, with D6 removed, and without the D5/D6 merge. Never changes a verdict.
- **HARNESS-FAIL** — a gate or a pre-lock control fails; no verdict.

## What the panel can and cannot claim
It can claim: "A table-and-grille generator, given B's skeleton, fragment inventories, unigram and folio composition
(and, in the steelman tier, B's junction table), does / does not produce ensembles containing B on D2–D6." It cannot
claim anything about table devices outside the declared families, anything about meaning (C2052), or that a NOT
EXCLUDED variant produced B: being inside on five line- and junction-level statistics is necessary, not sufficient.

## Declared prior knowledge and exposure
- **B supplied before the lock:** its skeleton with sections and paragraph-first flags; its unigram token frequencies
  and the fragment inventories under both parsers (composition only; real rows use B's word types and frequencies at
  corpus, section or folio scope, never in transcript order); its nine surface statistics above (composition; the
  folio Jaccards use folio adjacency, C361, not token order); its adjacent edge-glyph bigram table (chain rows and
  junction redraw only; computed in PHASE_757's exposure class); its D2–D6 values, known since PHASE_757 and
  recomputed in the controls stage, never used in the fit; PHASE_757's M1 and G-EDGE ensembles for C3 and C5.
- **Not computed on B before the lock:** no new order statistic. The fit stage reads no adjacency, order or position
  statistic of B.

## Partial-unblinding disclosure
D2–D6 were computed on fitted-variant members in control C1 while B's PHASE_757 values were known. The designer saw,
before the lock: EXTENDED D2 ≈ 0.001 and D5 0.01–0.02; PUBLISHED (restricted) D5 0.20–0.25; junction redraw D2
0.17–0.21. The FITTED bar was recalibrated after this. No other rule changed after these values were seen. The
registered row carries this disclosure (C2090 precedent, PHASE_772).

## Dry-run disclosure
The dry run (`run778.py --dry`) showed the designer D2–D6 for two fallback variants (N = 3 each): a published-style
variant (random rows, d 2, reset, keep, 40 × 16 table, V0): D2 0.06–0.07, D3 −0.5 to −0.6, D4 4.6–5.0, D5 3.2,
D6 0.52–0.55; a junction-redraw variant with per-word placement (V1): D2 0.21, D3 −0.25 to +0.56, D4 0.0, D5 0.002,
D6 −0.04 to −0.06; an M1 member D2 0.007, D5 0.037, D6 0.042. A pre-audit smoke test also showed one member each of
five configurations (recorded in the session log, not in the record). **Axes declared before the dry run:** order
{random, freq, length, chain}, d {2, 5, R}, pos {reset, continue}, repeat {keep, avoid}, the fit grid (parser, rows,
scope, size, α, n_tab, s_gr ∈ {0.05, 0.3}, grilles {all nine, (0,0)}), the six surface statistics. **Added after it,
from the design audit:** d = RP, junction redraw, the grille sets (distinct / same), s_gr = word, the three tiers with
the restricted PUBLISHED fit, the three Jensen–Shannon fit statistics, the fit bands and the fresh-seed
re-evaluation, the pooled rerun, the D5/D6 merge, the sensitivities, the descriptives (repeated 5-windows, whole-root
share), and controls C1–C5.

## Procedure
1. Gates (done); fit stage; pre-lock controls; this draft committed with `results/fit778.json` and
   `results/prelock_controls778.json`.
2. Lean-expert confirmation pass (done: LOCKABLE with eight edits, all applied; per-variant banding run).
3. `run778.py --checksums`, commit, tag `phase778-lock`.
4. `run778.py controls` (certification before any grille comparison is read), `run778.py panel`, `run778.py nearfit`,
   `run778.py verdict` (pooled rerun inside); raw results committed before the write-up; lean-expert results check.

## Caveats
- **Our implementation of a prose description.** Where the description leaves a choice (vertical shift range,
  line-start shift, end-of-table behaviour, grille and table changes) the choice is a declared axis or a fitted
  parameter. A reader who holds that the method means something else has a new test.
- **The fit gives the device B's composition deliberately** (strongest form), so the panel tests sequence and position
  structure, not vocabulary. An EXCLUDED verdict holds at the composition optimum, which is arbitrary with respect to
  sequence; control C4 reports whether neighbouring fits behave differently.
- **Runtime.** Fit about 1.5 h; pre-lock controls about 30 min; controls about 25 min; panel 130 × 1,000 members at
  about 1–3 s each, about 7 h at Idle priority with 6 workers; near-fit and rerun as needed.
