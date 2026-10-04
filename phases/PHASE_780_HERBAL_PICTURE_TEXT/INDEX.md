# PHASE_780 — Does the herbal text co-vary with its drawings? (blind picture test, Brunschwig 1500 positive control)

**Status: COMPLETE. Locked verdict (tag `phase780-lock`, 6a9b75f; pre-registration v4 after a lean-expert design audit,
a confirmation pass and amendments 1–14): NOT DETECTED (unpowered). Registered as C2098 (Tier 2, scope A; a label,
not evidence of no link; filed with the tested, unresolved entries).**

- **Question.** On the 91 herbal pages written by Davis hand 1 (Currier A), do pages with similar plant drawings carry
  similar text, beyond page position, quire, bifolium, layout, spelling dials, drawing style and length? This is
  RESEARCH_AGENDA item 8's next step: a blind picture-coding test within one section and hand that does not assume a
  label is a word of the text.
- **Pictures.** A locator outlined each plant (polygons; writing outside the outline masked grey) and boxed each
  Brunschwig woodcut; two independent coder sets (opus agents, paraphrased codebooks) coded root, stem, leaf, flower and
  habit features from the masked images without access to the text; every coder transcript was audited (16 of 16
  batches used only their own images, codebook and output). Agreement gate: V-A1 passes with all 10 content features
  (α 0.73–0.99, coverage ≥ 0.96) over 5 organs.
- **Text.** T1 word-type tf–idf cosine; T2 within-word glyph-unit trigram tf–idf cosine (spelling-robust).
- **Statistic.** Partial correlation of the double-centred text and content similarity matrices over 4,095 page pairs,
  given quire-pair fixed effects, physical distance terms, same leaf and bifolium, length, layout (tokens per line,
  line-edge share with ZL drawing breaks, paragraphs), spelling dials (e-run 2+, minim 2+, k/t, ch/sh shares) and
  drawing style.
- **Nulls and threshold.** N-local (exact, within two-leaf blocks), N-shift, N-sheet (exact, within bifolium; added by
  the pre-registered rule when scattered writing sessions defeated the first two); decision Z = min of the three;
  z\* = 2.957 from four drift generators (including the strongest shared drift the picture data allow) and writing
  sessions anchored to the measured neighbour similarity (false-positive rate at z\* ≤ 0.006 in every setting).
- **Power.** Planted descriptor words are detected (80%) at about one word per coded feature per page (~10 of ~83
  tokens). Positive control: Brunschwig 1500 Part 2 (121 plant entries with hand-coloured woodcuts, coded by the same
  procedure, matched on features, coding reliability and page lengths) is detected in 61% of samples (Wilson 54–68%;
  an upper bound), and its link runs mostly through plant names at the head of each entry.

## Result on the hand-1 herbal pages (Currier A)

| Measure | S | z_local (p) | z_shift | z_sheet (p) | Z = min | z\* |
|---|---|---|---|---|---|---|
| T1 words | +0.024 | +1.30 (0.100) | +1.31 | +0.73 (0.237) | +0.73 | 2.957 |
| T2 glyph trigrams | +0.020 | +1.05 (0.150) | +1.20 | +0.11 (0.444) | +0.11 | 2.957 |

**NOT DETECTED (unpowered).** No co-variation was detected between the text of the hand-1 herbal pages and the coded
content of their drawings at the locked threshold. S is +0.024 (T1) and +0.020 (T2), within the null range under all
three nulls (z +0.11 to +1.31; exact p 0.10–0.44); its sign is not a finding (the raw, not double-centred, matrices give
S −0.018 and −0.028). This is a label, not evidence of no link: the same procedure detects the Brunschwig 1500
herbal's own text–picture link, at V-A1's page lengths, on the features coded in both corpora, at V's coding
reliability, in only 61% of samples. That is an upper bound on two grounds (Brunschwig was tested without the N-sheet
null, which it lacks, and on 95 entries against V's 91), and the Brunschwig link runs mostly through plant names at the
head of each entry.

**Genre control (Brunschwig 1500) and ablations** (genre power at z\* = 2.957, 200 samples of 95 entries each):

| Brunschwig variant | Genre power |
|---|---|
| Main (first n words, V page lengths) | 0.61 (Wilson 0.54–0.68) |
| Uses only (names and description removed) | 0.14 |
| Plant names masked | 0.27 |
| Half length | 0.24 |
| Word code in Voynich forms, one spelling per word | 0.42 |
| Word code in Voynich forms, four spellings per word | 0.15 |
| Random window instead of the opening | 0.01 |

**What the null can show** (from the binary verdict, as pre-registered; each row compares a link of that kind with
no link, and is not an update on the three-way odds): a non-detection lowers a names-headed herbal at one word per token
at most by a factor of about 0.4; a word code in Voynich forms with one spelling per word by about 0.58 (a moderate
update); names masked 0.73; half length 0.76; a word code with four spellings per word 0.85; uses-only text 0.86; a
random window 0.99. These ratios are not sharpened by placing the observed Z within Brunschwig's distribution (that
would choose a stronger statistic after seeing the result).

**Descriptive companions** (uncorrected; never registrable): without the style partial T1 Z +0.73, T2 +0.15 (no
style-linked note); raw matrices T1 −0.78, T2 −1.34; Spearman partial S T1 +0.030, T2 +0.025; single-plant pages
(N = 89) T1 +0.94, T2 +0.13. With line-initial and line-final tokens removed (a sensitivity pre-registered only as a
check on the layout path for a positive result), T1 gives S +0.051 (z_local +3.04, z_shift +2.89, z_sheet +2.50;
minimum +2.50) and T2 S +0.026 (minimum +0.87). The minimum is below z\* 2.957; this is one of twelve uncorrected
companion values (six companions × two measures) and its null was not calibrated by the drift and session controls, so
it is not a result. A later test of mid-line vocabulary on these 91 pages would not be independent of it. V-B2's
negative S (T1 −0.025, Z −1.16; T2 −0.026, Z −0.56; hand 2, N = 20) is descriptive only and is not cited for
C137/C140, whose population it shares; neither it nor the negative raw S is an anti-correlation.

**Interpretive reading (expert-advisor, as pre-registered).** No material change to the working odds: about
34 / 51 / 15 (made-for-show / working notation with word-sized items / hidden running text) from 31 / 52 / 17, within
the noise of those conversation-level priors. Made-for-show predicted the null outright (P(positive) ≈ 0.01); working
notation splits by what its items say about the plant (single-spelling plant identifiers ≈ 0.4–0.6, uses or
processing items ≈ 0.14, variable spellings ≈ 0.15; mixture likelihood ratio ≈ 0.80–0.90); hidden running text loses
most of its names-headed, one-spelling form (mixture ≈ 0.75–0.85). The one interpretive step is how much of each class
sits in the names-headed form. The line-interior companion and any reading of the drawings themselves were not used.
Pushing made-for-show above about 36% would need exactly the interpretive step the lean-expert warned about.

**Prior tests** on pictures and text: C2058 (o-HEAD rate against plant complexity, N = 29) and C2084 (fragment labels
on the herbal page of their plant, 13 pairs). They are listed, not stacked: narrow or unpowered nulls do not add up to
an exclusion.

**Wording-only deviation from the locked template.** The row says "no co-variation is detected at the locked
threshold" where the A3 template said "does not co-vary … at the locked threshold" (more conservative; no rule, number
or verdict changes).

## Provenance and harness notes
- Pre-lock amendments 1–14 are listed in `PRE_REGISTRATION.md`: the Brunschwig copy is hand-coloured (colour coded in
  both corpora); undefined pairs at the neutral value; reused woodcut blocks confirmed by eye (8 groups); text-flagged
  crops kept (mirror bleed-through, a cutter's mark); supplementary maximum-strength drift; N-sheet added by its
  pre-registered rule and all calibration rerun with the same seeds.
- Compute: calibration 14,600 replicates (3.5 h K1, 1.3 h K1-max, 1 h K2, 1.1 h binding extension, 3.4 h K3, K4) at
  Idle priority; the locked run 1 minute.
- Lean-expert: design audit (LOCKABLE AFTER EDITS), confirmation pass (LOCKABLE once A1–A5 applied), results check.

## Registry
- **C2098** (Tier 2, scope A): see `context/CLAIMS/INDEX.md`. No scope notes on other rows (the locked rules give
  an unpowered row none; the non-extension clause for C137/C138/C140 sits inside C2098). Not negative knowledge: an
  unpowered NOT DETECTED excludes nothing at the conventional level; it is filed with the tested, unresolved entries.

## Files
`PRE_REGISTRATION.md` (v4, locked) · `scripts/core780.py`, `scripts/calib780.py`, `scripts/run780.py`,
`scripts/build_sets780.py`, `scripts/features780.py`, `scripts/prepare_coding780.py`, `scripts/audit_coders780.py`,
`scripts/locate_batches780.py` · `data/` (page and entry lists, codebooks, codes, geometry, duplicates) ·
`results/calib780.json`, `results/calib_setup780.json`, `results/k1_780.jsonl`–`k4_780.jsonl`,
`results/verdict780.json`, `results/run_log780.txt`, `results/coder_audit780.json`. Images (scans, masks, crops) are
regenerable and kept outside the repository (`external/phase780_coding/`).
