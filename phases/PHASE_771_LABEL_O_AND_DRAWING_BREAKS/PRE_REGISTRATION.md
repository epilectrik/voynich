# PHASE_771 — What is a label's initial o? Do line-edge forms follow the pen or the line?

**Status: LOCKED at the git tag `phase771-lock`.**
- This is v2 after the lean-expert lock audit and its confirmation pass (§9).
- The calibration is final and binding (§7).
- No statistic of either arm was computed on the test material before the lock. Design and calibration read only
  counts, lengths, positions and text references; the dry runs used decoy data.

**Origin.** Claude read five Currier A and four Currier B folios directly (2026-09-29), and three expert reviews
followed. Two cheap tests came out of that reading:
- **Arm L:** what a label's initial *o* corresponds to in running text. This is the crazy-expert's discriminator
  between three stories.
- **Arm E:** whether line-start and line-end forms reappear where a drawing interrupts a line. This is the
  expert-advisor's test of "units of writing motion versus units of content".

Both are ordinary measurements. Neither reads meaning.

---

## 1. Data
- **Source:** ZL 3b IVTFF (`data/transcriptions/reference/ZL_official.txt`).
  - Paragraph text is locus type P\*; labels are locus type L\*; AZC ring and circle text is locus type R\* / C\*
    (s7 only).
  - Drawing breaks are the `<->` markers inside a paragraph line.
  - Paragraph starts and ends are `<%>` and `<$>`.
  - Page variables $L (language), $I (section) and $H (hand) come from the page headers.
- **Text rules (PHASE_761):**
  - comments are removed;
  - `[a:b]` becomes a;
  - ligature braces are dropped;
  - rare-glyph codes are unreadable;
  - words are split at definite (`.`) and uncertain (`,`) spaces.

  A word is readable if it consists of EVA letters only.
- **Glyph units:** `c[tkpf]h | [cs]h | i+[nrlm] | .`. A benched gallows is one unit, and a minim group with its final
  is one unit.
- **Check transcription:** the H track, for Arm L only (H labels, placement L\*). H does not mark drawing breaks.
- **Pinned inputs:** `results/calib/input_checksums.json` records the SHA-256 of `ZL_official.txt`,
  `interlinear_full_words.txt` and `scripts/voynich.py`. The run asserts them.

## 2. Arm L — the label's initial o

**Background.** Labels start with *o* far more often than running text, and almost never with *qo* (C525, Tier 3:
o-prefix 50% vs 20%).

**Hypotheses.** Each is a prediction about the glyph unit that follows a label's initial *o*, at matched word
length:

| Code | Story | For a label o-word of L units, the unit after the o is distributed like… |
|---|---|---|
| L-qo | the o is text's *qo* without the q | the unit after *qo* in text qo-words of **L+1** units (R_qo) |
| L-o | labels are ordinary o-initial words | the unit after *o* in text o-words of **L** units (R_o) |
| L-add | an *o* is added in front of an ordinary word | the first unit of text words of **L−1** units (R_init) |

**Why length matching.** The audit showed that the qo-versus-o contrast depends on word length. Genuine text o-words
fitted against length-pooled references run from 1.00 "o" at 2 units down to 0.35 "qo" at 5 units. Labels are long
(C524), so without matching, a pure "ordinary o-words" sample can come out MIXED.

**Sample.**
- ZL label words that start with *o* but not *qo*, are readable, and have at least 2 units.
- Length strata: L = 2, 3, 4, 5, 6, 7+.
- Label counts per stratum: 5 / 33 / 130 / 153 / 161 / 126.
- Categories for the following unit: k, t, l, r, d, a, e, o, y, s, ch, sh, p/f, benched gallows, minim group, q,
  other.

**References.**
- Built from ZL paragraph text, A and B pooled, per stratum, with add-0.5 smoothing.
- The size of each reference is recorded in `results/calib/cal771.json` (`ref_sizes`).

**Statistic.**
- The mixture weights (w_qo, w_o, w_add) are shared across strata.
- They are fitted by grouped EM, in which each stratum uses its own length-matched components.

**Uncertainty.**
- Folio-cluster bootstrap: label folios resampled with replacement, 2,000 replicates.
- 95% percentile intervals.

**Decision (pre-registered):**

| Call | Rule |
|---|---|
| **o = qo without q** | lower 95% bound of w_qo ≥ 2/3 |
| **ordinary o-words** | lower 95% bound of w_o ≥ 2/3 |
| **o added to a word** | lower 95% bound of w_add ≥ 2/3 |
| **MIXED / UNRESOLVED** | otherwise; the weights and intervals are reported |

**Fit check.**
- A grouped G statistic against the fitted mixture.
- p comes from a clustered parametric bootstrap with 2,000 draws. Each draw is Dirichlet-multinomial per folio ×
  stratum cell at concentration α_fc = min(α_text, α_labels).
  - α_text is estimated from the folio clustering of text o-word continuations.
  - α_labels (`S.label_alpha`) is the smaller of two estimates from the labels' own counts: the cell-level
    (within-stratum) estimate and the folio-pooled one. See §7 for why a folio-pooled estimate alone was
    anti-conservative.
- If p < 0.01, the verdict carries the flag "[no mixture of the three fits]".

**Power at the labels' own clustering** (computed at run time, frozen seed):
- the power of the rule under each pure reference is simulated at α_labels (200 × 500);
- if the call is MIXED / UNRESOLVED and any of these powers is below 0.8, the verdict is **UNINFORMATIVE**;
- a pure call stands regardless of this diagnostic.

**Verdict assembly** (in `run771.py`):
- Start from the call. Apply UNINFORMATIVE as above. Append the fit flag.
- Append **[fragile: …]** if any pre-registered sensitivity analysis or label system (s1–s8) gives a *different pure*
  call. Only analyses whose references are large enough can do this: every component must have at least 50 words in
  every length group with L ≥ 4, a threshold fixed now.
  - The run records `min_ref_L4plus` and `feeds_fragile` for each analysis.
  - At the current corpus sizes, s1 (Currier A R_qo: 34), s2 (15) and s7 (17) are report-only. Every other analysis
    has at least 123.
  - The sizes split cleanly (at most 34 against at least 123), so the threshold is not load-bearing.

**What MIXED means.** Interior weights can arise from differences between label systems. In the audit, a pure but
different process in each system gave a pooled MIXED in 100% of runs. MIXED counts as evidence of a mixture *within*
labels only if all of these hold:
- the fit check passes;
- all three powers are ≥ 0.8;
- the s5 label systems share the same largest-weight reference.

Otherwise it is reported as "mixed across systems or unresolved".

**Sensitivity analyses.** These are reported. Those with large enough references feed the fragile flag (see
"Verdict assembly"); otherwise they do not change the verdict.
- **(s1)** Language-matched references: grouped by language × stratum. Labels on pages without a language (AZC) keep
  the pooled references.
- **(s2)** References from line-initial text words only, excluding paragraph-first lines. Their gallows openers would
  otherwise dominate R_init.
- **(s3)** Uncertain spaces merged, for labels and references.
- **(s4)** The H-track labels, against the pooled ZL references.
- **(s5)** Label systems, fitted separately:
  - astro/zodiac/cosmo (sections Z, C, A);
  - pharma/herbal (P, H);
  - bio (B).

  A system is fitted only if it has at least 20 label o-words. The few labels in other sections (e.g. T) are not fitted
  separately; they remain in the primary.
- **(s6)** R_init built without words that start with *o* or *q*. These carry about 0.36 of R_init's mass, and a
  literal "o + word" rarely produces *oo* or *oq*.
- **(s7)** Labels on AZC pages against references from AZC ring and circle text, with coarse strata
  {2–3, 4–5, 6+}.
- **(s8)** Type-weighted references, counting each word type once.

**Descriptive only (no verdict):**
- For each label o-word oX, the running-text counts of qoX, oX and X.
- The same counts for text o-words matched on family frequency, with each comparison word's own token removed.

## 3. Arm E — line-edge forms at drawing breaks

**Background.**
- Line-initial words favour certain first glyphs (articulated d/s/y forms and gallows openers: C1417, C1898;
  bare *aiin* is never line-initial, C1909).
- Line-final words favour *-m* (C1002, C1427).
- Where a drawing interrupts a line, the scribe lifted the pen and resumed on the other side of the drawing.

**Hypotheses:**
- **E-seg (pen):** the edge forms follow physical writing segments. The word after a break looks like the first word
  of a continuation line; the word before a break looks like the last word of a continuation line.
- **E-line (line):** the edge forms follow the logical line. Words at a break look like mid-line words at the same
  position.

**Sample.**
- ZL paragraph lines of Currier A and B that contain `<->`.
- For each break, the post-break word is the first word of the right segment, and the pre-break word is the last word
  of the left segment.
- Both sides must be non-empty and readable.

**Edge classes: continuation lines only** (audit edit E1).
- A post-break word can never open a paragraph, and a pre-break word can never close one. So the edge classes
  exclude paragraph-first line starts (start side) and paragraph-last line ends (end side), both in the edge models
  and in M_init / M_final.
- Without this, paragraph openers (gallows) inflate the start edge. A realistic pen-restart truth then gives A-start
  I = 0.80, with E-seg called in only 34 of 60 runs.

**Edge models.**
- Fitted on lines without a break, of the same language, with at least 3 words.
- LLR_start(u₁) = log P(u₁ | continuation-line start) − log P(u₁ | strictly interior word).
- LLR_end(u_last) is defined the same way, with continuation-line ends.
- Units seen fewer than 20 times are pooled; add-0.5 smoothing.
- **Cross-fitting:** folio halves by a seeded shuffle. The model is fitted on one half and the reference means are
  taken on the other; the two directions are averaged.

**Statistic.** The edge index for starts:

I_start = (mean LLR_start over post-break words − M_mid) / (M_init − M_mid)

- M_init is the mean over continuation-line starts of the same language and section.
- M_mid is the mean over matched mid-line words.
- **Matching:** same language and section, same token index from the line start (capped at 8), and the same "is also
  the line's last word" flag. When a cell has fewer than 10 reference words, the match falls back to coarser keys.

I_end is built the same way, from pre-break words and continuation-line ends, matched on the token index from the line
end.
- An index of 0 means the break words look like mid-line words; 1 means they look like continuation-line edges.

**Uncertainty.**
- Folio-cluster bootstrap over break folios and reference folios, resampled independently (conservative).
- 2,000 replicates; 95% percentile intervals.

**Decision** (pre-registered, per language A and B, separately for start and end):

| Call | Rule |
|---|---|
| **E-seg** | lower 95% bound of I ≥ 2/3 |
| **E-line** | upper 95% bound of I ≤ 1/3 |
| **PARTIAL** | the whole interval lies within [1/3, 2/3] |
| **UNRESOLVED** | otherwise |

**Rules applied to the calls:**
- **Precondition:** a cell is evaluable only if its calibrated power (§7) is ≥ 0.8 under both pure hypotheses.
  Otherwise its call is reported as "descriptive (…)".
- **Arm-level statement (multiplicity):** a statement about a side (start or end) is made only when both languages are
  evaluable and give the same call. Otherwise results are reported per language.
- **Fragile:** a cell's verdict carries "[fragile]" if any of t1–t5 gives the opposite call (E-seg against E-line).

**Sensitivity analyses** (reported; they do not otherwise change the verdict):
- **(t1)** Breaks where either adjacent word is a single glyph unit are excluded.
- **(t2)** Uncertain spaces merged.
- **(t3)** Matching on relative position (fifths of the line) instead of token index.
- **(t4)** Only lines with exactly one break.
- **(t5)** Breaks are excluded where pre + post joined is a word attested at least twice. "Attested" means occurring in
  unbroken Currier A/B paragraph lines of at least 3 words. The cause: 743 of 746 `<->` markers sit directly between
  letters, so the markup cannot show where a drawing cut a word.

**Descriptive only:**
- The library articulator rate (Morphology) for post-break words, continuation-line starts and mid-line words.
- The count of bare *aiin* as a post-break word, where C1909 predicts zero if breaks act like line starts.
- The *-m* rate for pre-break words, continuation-line ends and mid-line words.

## 4. What the verdicts would mean (fixed now)
**Arm L:**
- **o = qo without q:** after a label's o, the next unit is distributed like the unit after *qo* in text words of
  matched length. Reading this as "the q was dropped" is one Tier-3 interpretation, and this arm does not test it.
- **ordinary o-words:** the next unit is distributed like the unit after *o* in text o-words of matched length. The
  labels draw on the o-initial word family. Why labels favour o is not tested.
- **o added to a word:** the next unit is distributed like the first unit of ordinary words one unit shorter. The
  label's o behaves like an element attached in front of such words.
- **MIXED / UNRESOLVED:** see "What MIXED means" in §2.

None of these outcomes distinguishes meaning from no meaning.

**Arm E:**
- **E-seg:** the edge forms mark stretches of writing (a pen or segment convention). They are then weaker support for
  "the line as a content record".
- **E-line:** words at breaks carry no edge forms. This cannot distinguish "the scribe treated the line as a unit
  across the drawing" from "the scribe did not restart at the break at all". The second applies, for example, if the
  text was written before the drawing and the drawing then cut through it.
- **PARTIAL:** edge forms appear at breaks at intermediate strength.

Neither outcome reads meaning.

## 5. Calibration (before lock)
- **Arm L:**
  - the grouped rule under folio × stratum Dirichlet-multinomial draws with the real label length profile, at α_text
    and at α_text / 4;
  - the pure references, 50/50 mixtures, and w = 2/3 boundary truths (six);
  - the size of the grouped fit check at both concentrations, with α_fc taken as in the run.
- **Arm E:**
  - E-seg draws from continuation-line edges;
  - E-line draws from matched mid-line words, using the same folio where possible;
  - a 50/50 plant;
  - at the real number and positions of breaks.

## 6. Blinding
The design and calibration scripts read only:
- label counts and **label word lengths** (length strata; length does not reveal the unit after the o);
- break counts and within-line positions;
- references from paragraph text and unbroken lines.

The glyph after a label's o, and the glyphs of break-adjacent words, are first read by the locked run script. The dry
run uses a decoy copy of the data. The audit confirmed that blinding held through v1.

## 7. Calibration results
**Final calibration (pre-stated before it runs).** The lean-expert confirmation pass found that the fit-check-only
recomputation broke reproducibility of the Arm E section: the fit-check loop and Arm E share one random-number stream.
`cal771.py` is therefore re-run once in full with the final code:
- seed 7711;
- 200 Arm L simulations and **500** Arm E simulations per cell;
- `--fitcheck-only` removed.

**This run is final whatever it shows**, including the A-end precondition (E-line 0.82 against the 0.80 bar in the
earlier run). Its numbers replace the v2 numbers below.

### Final calibration: binding
Run `cal771.py`, final code, seed 7711; output in `results/calib/cal771.json`; runtime 3,133 s.

**Arm L.** The power sections are identical to v2, because they precede the fit-check loop in the random stream.

| Truth | at α_text | at α_text / 4 |
|---|---|---|
| qo | 1.00 | 0.99 |
| o | 1.00 | 0.97 |
| init | 1.00 | 1.00 |
| any 50/50 mixture (called MIXED) | 1.00 | 1.00 |

- **2/3 boundary truths** (pure call at a true weight of exactly 2/3): 0.005–0.035 at α_text and 0.000–0.045 at
  α_text / 4.
- **Fit-check size at nominal 0.01**, with the final `S.label_alpha`:
  - α_text: 0.01 (qo), 0.00 (o), 0.01 (init);
  - α_text / 4: 0.02, 0.02, 0.00.

**Arm E** (500 simulations per cell):

| Cell | E-seg correct | E-line correct | 50/50 plant | Evaluable |
|---|---|---|---|---|
| A start | 1.00 | 0.986 | PARTIAL 0.18, else UNRESOLVED | yes |
| A end | 0.952 | 0.828 | UNRESOLVED 1.00 | yes |
| B start | 1.00 | 0.998 | PARTIAL 0.22, UNRESOLVED 0.78, E-seg 0.002 | yes |
| B end | **0.646** | 1.00 | UNRESOLVED 1.00 | **no: descriptive** |

- No arm-level statement is possible for the end side.
- The start side can have one if A and B agree.

**Earlier (superseded) v2 numbers**, kept for the record:

### Arm L (grouped, length-matched)
- **Sample:** 608 label words on 53 folios; length profile 5 / 33 / 130 / 153 / 161 / 126 (L = 2…7+).
- **Text clustering:** α_text = 19.8.
- **Reference sizes:** listed in `ref_sizes`. The smallest primary components are R_qo at L = 7 (183) and at L = 2
  (222).

**Correct-call rates:**

| Truth | at α_text | at α_text / 4 |
|---|---|---|
| qo | 1.00 | 0.99 |
| o | 1.00 | 0.97 |
| init | 1.00 | 1.00 |
| any 50/50 mixture (called MIXED) | 1.00 | 1.00 |

**2/3 boundary truths** (a pure call at a true weight of exactly 2/3): 0.005–0.035 at α_text and 0.000–0.045 at
α_text / 4, close to the nominal 0.025.

**Fit-check size at nominal 0.01** (100 simulations each):
- **First version:** used α_labels taken from folio-pooled counts. At α_text / 4 its size was 0.17–0.43. Pooling a
  folio's labels over length strata hides cell-level dispersion, so the check was anti-conservative.
- **Fix:** α_labels = `S.label_alpha` is the smaller of the cell-level (within-stratum) and the folio-pooled estimates.
  With it, the size is 0.00–0.02 at α_text and 0.01–0.03 at α_text / 4. The median α_labels recovered in the
  simulations was 19–21 and 4.7–5.1, the true values.
- `run771.py` uses the same `S.label_alpha`, both for the fit check and for the power diagnostic.

### Arm E (continuation-line edges)
E-seg draws come from continuation-line edges; E-line draws from matched mid-line words, from the same folio where
possible.

| Cell | E-seg correct | E-line correct | 50/50 plant | I under E-seg / E-line | Evaluable |
|---|---|---|---|---|---|
| A start | 1.00 | 0.985 | PARTIAL 0.21, else UNRESOLVED | 1.00 / 0.02 | yes |
| A end | 0.945 | 0.82 | UNRESOLVED 0.995 | 1.03 / 0.05 | yes |
| B start | 1.00 | 1.00 | PARTIAL 0.26, else UNRESOLVED | 1.06 / 0.02 | yes |
| B end | **0.685** | 1.00 | UNRESOLVED 1.00 | 1.02 / −0.02 | **no: descriptive** |

Because B end is descriptive, no arm-level statement can be made for the end side.

### Dry run v2 (`results/dryrun/`)
Decoy data: the label o-words are replaced by random paragraph o-words, and the break words by random words of the
same language and section from random line positions.
- **Arm L:** the call is "ordinary o-words", as constructed. The fit check has p 0.65 and the powers are 1.0.
  - s2 (line-initial references) and s8 (type-weighted) give MIXED on the decoy, because their references differ from
    the token-sampled decoy.
  - The descriptive stem families agree with their control (0.32/0.46/0.22 against 0.29/0.45/0.26).
- **Arm E:** the decoy gives I = 0.06 (A start), −0.01 (A end), 0.26 (B start) and 0.13 (B end). These are E-line or
  UNRESOLVED calls, never E-seg.
- All code paths ran in 236 s. The final dry run on the final code (fragile-eligibility logic included) reproduced these
  decoy values. It flagged s1 (33), s2 (15) and s7 (17) as report-only; s3, s6 and s8 feed the flag.

**v1 (superseded):** computed with the unmatched references, the paragraph-edge classes and the cross-language decoy.
The v1 decoy note was an artifact.

## 8. Run procedure
- `python run771.py --checksums` writes the input checksums.
- Commit the phase (including the audit scripts in `scripts/audit/`) and tag `phase771-lock`.
- `python run771.py` asserts, before any data is loaded or the log is opened:
  - the tag;
  - an unchanged `scripts/`, `PRE_REGISTRATION.md` and `results/calib/`;
  - no untracked files under `scripts/` or `results/calib/`;
  - the input checksums.
- It runs at Idle priority, with 2,000 bootstrap replicates and 2,000 fit-check draws.
  - Power at label clustering uses 200 simulations × 500 replicates.
  - Seeds are 7712 (run) and 77120 (power).
- Raw results (`results/phase771_results.json`, `results/run_log.txt`) are committed before the registration review.

## 9. Audit record
**Lean-expert lock audit (v1): "not lockable as written; lockable with edits".** Blinding held. The required edits, all
applied in v2:

- **Arm L:**
  - **L1:** length-stratified references with grouped EM (primary). Recalibrate with the length profile and the 2/3
    boundary truths.
  - **L2:** the fit check uses α = min(α_text, α_labels).
  - **L3:** explicit verdict assembly (UNINFORMATIVE only for MIXED with low power; fit flag; pure calls stand).
  - **L4:** §4 wording (no appeal to C1563/C549; no "vocabulary choice"; MIXED defined).
  - Recommended and adopted: s6, s7, s8, and s2 without paragraph-first lines.
- **Arm E:**
  - **E1:** paragraph-first starts and paragraph-last ends excluded from the edge classes; calibration E-seg draws
    from continuation lines.
  - **E2:** the decoy is language- and section-matched, and the v1 decoy note is withdrawn. Its A-end 0.37 was a
    cross-language artifact.
  - **E3:** t5, the check for words cut by a drawing.
- **Other:**
  - multiplicity (the arm-level rule) and fragile flags;
  - pinned input checksums;
  - the §4 caveat that E-line cannot distinguish "planned line" from "no restart".

**Lean-expert confirmation pass (v2): "DO NOT LOCK yet".** The v1 edits are implemented correctly. Five small edits
were required, all applied:
- **(a)** A full re-run of `cal771.py` with the final code (seed 7711; 500 Arm E simulations), pre-stated as final;
  `--fitcheck-only` removed.
- **(b)** The fragile flag is fed only by analyses whose references have at least 50 words in every length group with
  L ≥ 4. s1, s2 and s7 are therefore report-only.
- **(c)** The s5 minimum of 20 labels is stated, together with how other-section labels are handled.
- **(d)** Two §7 numbers corrected.
- **(e)** The stale smoke-calibration file was removed.
- Optional hardening adopted:
  - `verify_lock` runs before any data is loaded;
  - untracked files under `scripts/` and `results/calib/` fail it;
  - §3 defines "attested" for t5.
- The confirmation checks are in `scripts/audit/audit_confirm.py`.
