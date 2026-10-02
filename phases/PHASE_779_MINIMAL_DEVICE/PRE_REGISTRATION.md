# PHASE_779 — The minimal device: which of Currier B's registered regularities follow from page vocabulary, line-position vocabulary and two-unit junction routing? (pre-registration)

**Status: DRAFT v1 for the lean-expert design audit (not locked).** No value of any prediction statistic has been
computed on Currier B. The device has no tuned parameter.

**Origin.** PHASE_774–778 reduced B's measurable sequence to its word-boundary rules and page composition (C2091,
C2093, C2094) and excluded the two published content-free production methods (C2077 copy-and-modify; C2096 the
table-and-grille as described). That leaves a specification any production method must meet: a page-specific word
stock, line-position vocabulary, and junction routing. The question the user set: can the method be recovered in
reverse? The first step is to ask how much of what the registry records about B beyond those three rules is a
consequence of them, and how much is an extra layer. STATUS_BRIEF §4 and RESEARCH_AGENDA Tier B.

**Question.** Take the simplest sampler of the three rules (MIN-D, below). Which of eleven registered regularities,
none of which the device is given, does it reproduce, and which does it not? The answer is a layer map: regularities
that follow from the rules (registered as rule-derivable), and regularities that are extra conventions (registered
as layers, with the measured gap).

**What this is not.** Not a claim about hands or devices: MIN-D is a sampler of statistical rules, not a recipe a
scribe followed. Not a test of meaning (C2052). A regularity reproduced by the sampler is explained by the rules under
either reading; one not reproduced is a design element both readings must account for.

**Change control:** after the lock nothing below (device, rungs, statistics, criterion, N, seeds) may change without
a new phase number.

## The device (`scripts/mind779.py`)
- **Page stock.** Each page's own tokens (its multiset of certain P-text tokens); words are drawn from the stock
  without replacement, so each generated page has exactly B's composition for that page. The variant `w` draws with
  replacement from the page's frequencies (composition noise).
- **Zone.** Each candidate word is weighted by P_B(zone | word), zone = line-initial / medial / line-final,
  estimated corpus-wide with additive smoothing 0.5 (the specification's line-position vocabulary: D6, C956).
- **Routing.** Each candidate word is weighted by P_B(first glyph unit | previous word's last two glyph units),
  corpus-wide, smoothed toward the first-unit marginal (the two-unit ending routing C2082; the junction coupling
  C1212/C1563). Rung R2a uses the previous word's last unit only; rung R3 routes the next word's first two units.
- The next word is drawn with probability proportional to stock count × zone weight × routing weight (a product of
  the three rules); if every weight is zero, the stock count alone. No paragraph state, no line memory, no interior
  rule, no repeat rule.
- **Ladder (rungs, without replacement):** R0 page stock only (a within-page shuffle); R1 + zone; R2a + one-unit
  routing; R2 + two-unit routing; R3 + two-unit-to-two-unit routing. Variants R2w and R3w with replacement.
- **Plant (positive control for the paragraph predictions):** R2+H, in which paragraph-first lines weight each word
  by a glyph-level header propensity (P_B(header | first unit) × P_B(header | last unit) / P_B(header), clipped to
  1) and by B's paragraph-first-line zone weights, and body lines by the complement and the body-line zone weights
  (a header rule the device is otherwise denied; glyph-level so that rare words inherit their glyphs' conventions).
  It must move P3–P5 if those statistics have power.
- Eight variants × N = 1,000 members (seed 779,000,000 + 10,000·variant + member) on B's skeleton (2,299 lines,
  21,610 certain tokens, 80 folios, 457 paragraph-first lines; blockers kept).

## Step 1 — does the device meet the specification? (the PHASE_757 panel)
D2 edge-glyph coupling, D3 adjacent repetition, D4 cross-folio trigram recurrence, D5 order information beyond edge
coupling, D6 line-zone dependence (`panel_stats.py`, unchanged; B's values recomputed in the run). B is **outside** a
variant on a statistic if it lies beyond the ensemble [min, max] and |z| > z\* = Φ⁻¹(1 − 0.005/5) = 3.09. A rung
**passes the panel** if B is outside on none of the five. **MIN-D** = the lowest rung that passes. If no rung passes,
the specification as sampled here is **INCOMPLETE** on the named statistics (its own result), and the predictions are
read on every rung anyway.

## Step 2 — the predictions (fixed now; B's values computed only in the locked run)
Each statistic is computed identically on B and on every member. B is REPRODUCED by a variant if it is not outside
(same criterion, z\* = Φ⁻¹(1 − 0.005/11) = 3.26); otherwise NOT REPRODUCED, with direction, z and B's rank.

| | Statistic | Registered relative | Encoded in the device? |
|---|---|---|---|
| P1 | Line homogeneity: mean within-line token entropy, percent reduction against 20 within-page shuffles | C1214 (3.8% at atom level, z −7) | no (no line memory) |
| P2 | Paragraph PREFIX composition: mean within-folio JSD between paragraphs' PREFIX distributions (paragraphs ≥ 10 tokens) ÷ mean between-folio JSD of folio PREFIX distributions | C1811 (within 1.37× between) | no (no paragraph state) |
| P3 | Line-final m by line type: share of m-final tokens among line-final tokens, paragraph-first lines minus body lines | C1435 (0% header, 10.45% body) | no paragraph state; zone encodes line-final m overall |
| P4 | Paragraph-initial gallows: share of gallows-initial first words, paragraph-first lines minus other lines | C1898 (openers line-initial) | no |
| P5 | Top-line f/p: share of tokens containing p, f, cph or cfh, paragraph-first lines minus body lines | Zandbergen 2021's "prohibitive" feature | no |
| P6 | Forbidden token bigrams: count of the nine C957 zero-count forward bigrams | C957 (B 0; shuffle 0.6 ± 0.8) | no (routing is glyph-level) |
| P7 | e-run lag-1 agreement: share of adjacent pairs whose e-run classes (0 / 1 / 2+) agree | PHASE_757 descriptive (B 0.455); C2086/C2087 relatives | no (interior) |
| P8 | qo / ch-sh alternation: among adjacent pairs where both words start with qo or with ch/sh, the share that alternate | C549 (56.3% vs 50.6%), C2056 | partly, through routing |
| P9 | Max count of qok-initial tokens in any 10-token window of a folio | PHASE_757 descriptive (B 8) | partly, through page stock |
| P10 | Hapax dispersion: variance-to-mean ratio of per-line counts of corpus-hapax tokens | — (the "hapax spread") | no |
| P11 | e-run position gradient: JSD between the line-quintile distribution of tokens with an e-run of 2+ and that of all tokens | C1671 (e most position-sensitive) | partly, through the three zones |

Consistency descriptives (no verdict role): repeated within-line 5-token windows (C2091; B 0), duplicate lines
(B 0), max identical run (B 4).

P8, P9 and P11 are partly encoded: a REPRODUCED there says the rules carry the regularity, a NOT REPRODUCED says the
rules carry only part of it. The plant R2+H encodes P3–P5 by construction and is reported as the power check for
them, not as a prediction.

## Decision rules (locked)
- **Step 1 result:** MIN-D named, or INCOMPLETE with the outside statistics named per rung.
- **Step 2 result, per prediction, on MIN-D (and reported on every rung):** REPRODUCED or NOT REPRODUCED (direction,
  z, rank). The layer map lists both sets.
- **Registry:** one Tier-2 measurement row (the layer map, with the ladder result). For each REPRODUCED regularity
  with a registered relative, a scope note on that constraint: "derivable from page stock + zone + routing (PHASE_779)"
  where the statistic matches the registered one closely enough, otherwise "its PHASE_779 relative is derivable". For
  each NOT REPRODUCED, a scope note: "not derivable from the three rules; gap of {value} ({z})". No Tier-0 change.
- **Power:** a prediction counts as tested only if the plant (for P3–P5) or the ladder spread (for the others: the
  statistic differs between R0 and the top rung by more than its ensemble sd) shows the statistic responds to a rule;
  otherwise it is reported as UNPOWERED and carries no scope note.
- **HARNESS-FAIL:** a code failure; no verdict.

## What each outcome means
- **A regularity REPRODUCED** by MIN-D is a consequence of page composition plus the two boundary rules. It stops
  being an independent design fact and becomes a corollary (as C2061/C2067 did under C2094). Under either reading of
  the text it is explained.
- **A regularity NOT REPRODUCED** is an extra layer: a convention or structure the three rules do not generate, with
  its size measured. The layer map is the specification's remainder, and the shortlist for any future method search
  (PHASE_778's follow-up) or content test.
- **INCOMPLETE at Step 1** means a sampler of the three rules, with B's own page stocks, does not reproduce the
  discriminators the rules were abstracted from; the named statistics are then the first layer.
- Not evidence of meaning or of its absence.

## Declared prior knowledge and exposure
- **B supplied before the lock:** its skeleton with paragraph-first flags; its per-page token multisets
  (composition); P_B(zone | word) (position composition); the two-unit routing tables (adjacent-pair glyph
  statistics, the G-EDGE exposure class); the registered values of the relatives above, as recorded in the registry.
- **Not computed on B before the lock:** none of the eleven prediction statistics as implemented here, nor the
  consistency descriptives; B's D2–D6 are known (PHASE_757/778) and are recomputed in the run.
- **Dry run:** two members per variant and the outside logic against a member standing in for B; no B value read.

## Procedure
1. Commit this draft, the scripts and the dry run. Lean-expert design audit; edits; confirmation pass if required.
2. `run779.py --checksums`, commit, tag `phase779-lock`.
3. `run779.py run` (B's values and 8 × 1,000 members, about 1 h at Idle priority), `run779.py verdict`; raw results
   committed before the write-up; lean-expert results check; write-up; registration.

## Caveats
- **One sampler, one implementation of the rules.** A different sampler (with replacement, a different smoothing, a
  routing table at the word level) could differ; the ladder and the `w` variants bound the sensitivity to the two
  choices that matter most.
- **The device is given B's page compositions exactly.** It therefore says nothing about how a page's vocabulary
  arose, only about what follows once it exists.
- **Tautology guard.** P3–P5 are paragraph-level and the device has no paragraph state, so their outcome is known in
  direction (the device predicts no header/body difference); what the run measures is the size of the layer, and the
  plant shows the statistics can see it.
