# PHASE_774 — Merged spellings: does Currier B repeat ordered phrases at the word or MIDDLE level beyond its local habits? (pre-registration)

**Status: DRAFT v2** (not locked). The lean-expert lock audit found v1 **NOT LOCKABLE**. Edits E1–E9 and the optional
O1–O2 are applied below. The re-certification (E4) is defined here before it runs. After the lock nothing below may
change without a new phase number.

## Origin
- **The human's idea (2026-09-29).** Some Voynich tokens may be interchangeable, so the same thing written twice can
  look completely different, with the spelling chosen by some criterion (a rule-driven homophonic cipher, H-RC).
- **The experts' proposal.** A variant-merge test, certified on H-RC output, is the one test that could give positive
  evidence of a message: merge the suspected spelling variants, then look for the message's repeated phrases.
- **PHASE_768 (never run on B).**
  - Exact token repeats cannot see a code with many spellings per unit.
  - Its MCMC null (N5j) did not converge at β = 2 and was too loose at β = 1.
  - The phase stopped at design.

This phase:
1. measures which merges can recover hidden units at all (controls only);
2. replaces N5j with an exact permutation null;
3. certifies two arms on controls before touching B.

## Stage 1 (done; controls only): which merges recover the hidden units
Measures:
- **k1:** the chance that a true repeat of a unit stays a visible repeat.
- **k0:** the chance collision rate.

Source: `results/prelock_recovery.json`, rerun with the final generator code.

| Cipher (Latin recipes unless noted) | TOK | MID | Exchange (Brown) clustering, 64–512 classes |
|---|---|---|---|
| Naibbe GV1 (letter chunks, about 12 spellings per unit) | k1 0.22 | k1 0.33, k0 0.030 | best BR64: k1 0.41, k0 0.006 |
| Stem code: fixed stem, affix frame chosen freely or by rule | k1 0.03–0.04 | **k1 0.67–0.72, k0 0.002** | k1 ≤ 0.045 |
| Whole-token code, 2 unrelated spellings per word | k1 0.50 | k1 0.51, k0 0.017 | k1 0.50 (see note) |
| Whole-token code, 4 unrelated spellings | k1 0.25 | k1 0.26, k0 0.013 | k1 0.26 (Latin NT: BR64 0.84) |

- **Note on the two-spelling code.** An earlier run of the same generator clustered it at k1 0.85. The rerun with the
  final code did not (k1 0.50). Exchange clustering of rare homophones is unstable.
- **Reading:**
  - A MIDDLE merge recovers a stem code (spelling varies only in the prefix and suffix frames).
  - Distributional clustering recovers homophones only sometimes, and only when every spelling is frequent. At B's
    size, only about 800–1,400 types occur 3 or more times.
  - Nothing recovers Naibbe-type letter ciphers.

## Declared prior knowledge
- **C1790:** B has no duplicate lines, only 10 token trigrams in 3 or more folios, and no such 4-grams. There is no
  null comparison.
  - **The audit showed C1790 does not make the T arm redundant.** B-fitted first-order generators give 8–18 trigrams
    and 0 such 4-grams. Whole-word codes of low-repetition segments match C1790 too: Codicillus-last and
    Rupescissa-last give 9 and 0, Mesue segment 1 gives 17 and 0.
  - C1790 excludes only repetitive plaintexts. The T arm adds the region of 5–10 repeated windows.
- **C2085 / PHASE_767:** order information is near shuffle (+0.02), matched by Naibbe; adjacent identical tokens occur
  at chance.
- **C2080:** Naibbe as published is excluded. **C2077:** Timm is excluded.
- **Not computed on B before the lock:** no repeat count of any length, no EF run, and no statistic of B's token order
  beyond adjacent pairs.

## B exposure before the lock (declared; E8)
- **B's skeleton:** lines, lengths, uncertain-token blockers, sections and folios.
- **B's marginals, for controls written in B's forms:** token counts, MIDDLE counts, P(frame | MIDDLE), and within-line
  frame-to-frame transition counts (adjacent pairs).
- **B's adjacent-token transitions, for the no-message generators:**
  - `habit`, `habit2`, `habit3` and `habit3b` (PHASE_768), and `M1` (PHASE_757);
  - also B's **line-initial token distribution** and **line-quintile unigrams** (habit2/3/3b);
  - and, for the section-fitted generators of the re-certification, **adjacent pairs within each section**.
- **The unseeded Timm control** draws each folio's first line from B's token marginal.
- **Leak test (lock audit).** habit3 and habit3b fitted to message-bearing controls do not inherit the source's
  repeats:
  - whole-word code of Mesue, source D5 19.8: D5 0–2;
  - stem-coded German NT, source X5 30: X5 0.7–1.9.

  So a B-fitted first-order ceiling is not a readout of B's own repeats.
- **The auditor checked that the thresholds depend on B only through:**
  - adjacent pairs, with the 20-successor threshold blocking replay of rare sequences;
  - the class map;
  - marginals.

## Data
- **B:** H track, P placement, labels excluded. 21,610 certain tokens in 2,299 lines on 80 folios, with 22 uncertain
  tokens kept as blockers (the PHASE_756 primary data, via `hr768.b_skeleton`).
- **Blockers count as line positions** when zones are assigned, identically in controls.
- **Controls** are laid into the same skeleton.
- **Plaintext segment k** = words [k·21,610, (k+1)·21,610); "last" is the final 21,610 words. The design used segment
  0 throughout. Calibration "seeds" of one plaintext re-drew the codebook on that same segment (E7).

## Representations
- **TOK:** the token.
- **MID:** the canonical MIDDLE (`scripts/voynich.py` Morphology; the token itself when there is none).
- **MIDn1** (MID with e-runs and i-runs collapsed): **descriptive only.**

## Null: the exact edge-frame permutation (EF)
- **The permutation.** Within each folio, tokens are permuted uniformly among positions that share a **cell** =
  (zone, first glyph unit, last glyph unit).
  - Zones: line-initial, medial, line-final (a one-token line counts as initial).
  - Blockers stay fixed.
- **Preserved exactly:**
  - every folio's token multiset;
  - the edge signature at every position, and so every last-glyph → first-glyph junction pair (C1212/C1563);
  - line-initial and line-final signatures, line lengths and blockers.
- **Destroyed:** which token, among those with the same edges in the same folio and zone, sits where.
- **Sampling is exact** (independent uniform permutations within cells). The lock audit checked the implementation.
- **B run:** 1,000 permutations, seed 77400.

## Statistics and per-arm calls (E3, E5)
RPT_n(rep) is the number of within-line windows of n certain tokens whose rep-sequence occurs at least twice in the
corpus. p = (1 + #{null ≥ obs}) / (1 + R).

| Arm | Question | Statistic | PRESENT | NONE | INDETERMINATE |
|---|---|---|---|---|---|
| **T** | a whole-word code (one spelling per word) | D5 = RPT5_TOK(obs) − mean RPT5_TOK(EF null) | D5 ≥ **7.5** and p ≤ 0.01 | D5 < **4.5**, or p > 0.05 | otherwise |
| **M** | a stem code (frames vary around a fixed MIDDLE) | X5 = (RPT5_MID + 1) / (mean null + 1) | X5 ≥ **7.60** and p ≤ 0.01 | X5 ≤ **2.82**, or p > 0.05 | otherwise |

**Where the numbers come from** (`prelock_thresholds.py`, `results/thresholds774.json` v2; design calibration, 53
no-message runs):
- **T arm.** The ceiling is at most 4 repeated windows (max D5 3.97).
  - D5 is an integer count minus a small null mean, so the boundaries sit at half-integers.
  - NONE_T_lt = ⌈3.97⌉ + 0.5 = 4.5.
  - τ_T = ⌊(3.97 + 11.6)/2⌋ + 0.5 = 7.5, where 11.6 is the minimum design whole-word code.
- **M arm.** NEG_M 2.82 is the maximum X5 of the no-message runs. τ_M = √(2.82 × 20.46), where 20.46 is the minimum
  design NT stem code.
- **p is a requirement, not the discriminator.** EF is a zero-order null within edge cells, and first-order habits
  alone push p below 0.01 in 18 of 53 no-message runs on the M arm.

**Each arm is called and registered separately (E5).** The overall line (either arm PRESENT / both NONE / otherwise)
is a summary only.

## Evidence so far (controls)
**Whole-word codes (CBB), D5.** Design, audit and v1 certification, grouped by plaintext segment:

| Text | Segments | D5 | T call |
|---|---|---|---|
| Mesue (pharmacy) | 7 | 10–141 | all PRESENT |
| SISMEL Testamentum (alchemy) | 3 | 30–48 | all PRESENT |
| Codicillus (recipes) | 2 | 8–15 | PRESENT |
| Rupescissa (alchemy) | 2 | 6–11 | segment 0 PRESENT; last **INDETERMINATE** (6.0) |
| Dante (verse) | 2 | 6–10 | segment 0 PRESENT; last **INDETERMINATE** (5.9) |
| New Testaments | 5 | ≥ 345 | all PRESENT |

**Stem codes in B's forms (HRCB-lem), X5:**
- Latin recipes: 1.34–1.99, and SISMEL 4.27 (both below the PRESENT bar of 7.60).
- New Testaments:
  - Gospel opening (segment 0): 20.5–39.1;
  - later segments: 4.6–16.2, of which 4 of 7 PRESENT and 3 INDETERMINATE.

**Not detected by either arm:**
- whole-word codes with **two** spellings per word (Latin recipes D5 0; Latin NT D5 4.0, which is NONE under E3);
- stem codes of recipe, pharmacy, alchemy or verse prose;
- Naibbe.

**No-message runs (73: 53 design plus 20 v1 certification):**
- T: D5 ≤ 3.97. M: X5 ≤ 2.82. None PRESENT.
- In the audit, 9 section-fitted runs gave T D5 ≤ 3.98 and M X5 ≤ 1.83. Their MID5 null means were 31–44, against
  14–27 in calibration.

**Twins** (the same machinery with the plaintext order shuffled within folio): all NONE.

## Re-certification on unscored segments (E4; defined before running; `prelock_recert.py`)
**Segments:** none of these has been scored by anyone.
- Mesue 7–12.
- Latin NT 1, 3, 4, 6 and 7.
- German NT 1, 2, 4 and 5.
- Spanish, Italian and English NT 1–6.
- Turkish NT 1 and 3.

Each is used both as a whole-word code and as a stem code (35 segments per family).

**Other runs:**
- No-message: section-fitted habit3 ×5 and habit3b ×5, plus corpus-wide habit3 ×5 and habit3b ×5, all on fresh
  seeds.
- Twins: CBB Mesue 7, CBB Latin NT 1, HRCB-lem German NT 1 and HRCB-lem Spanish NT 2.

**P5**, the plaintext's own repeated 5-word windows in B's layout, is recorded for every positive.

**Criteria:**

| Criterion | Requirement |
|---|---|
| R1a | every whole-word-code segment with P5 ≥ 12 is PRESENT on T |
| R1b | no whole-word-code segment with P5 ≥ 8 is NONE on T |
| R2 | no NT stem-code segment is NONE on M (the NONE scope); the share PRESENT is reported |
| R3 | none of the 20 no-message runs is PRESENT on either arm; at most 2 are INDETERMINATE |
| R4 | no twin is PRESENT |

**PASS = all five.** A FAIL means redesign; there is no re-tuning on these segments. The result file joins the locked
set.

## What each outcome means (scope; E1, E2, E6)
### T arm
**T NONE.** B has fewer than about 5 excess repeated 5-token windows, which is within B-fitted first-order habits.

It excludes a whole-word code with one spelling per word (any language, any word-to-token assignment) of a text with
about 8 or more repeated 5-word windows per 21,610 words. For reference:
- all tested pharmacy (Mesue), alchemy (SISMEL) and NT segments;
- the recipe segments (Codicillus, D5 8–15);
- the first segments of Rupescissa and Dante.

Low-repetition prose and verse sit just above the ceiling (Rupescissa-last and Dante-last, 6 windows). Those would
give INDETERMINATE, not NONE.

**T PRESENT.** B has 8 or more excess repeated 5-token windows.

### M arm
**M NONE.** Excludes a stem code (fixed MIDDLE, frames chosen freely or by local rule) of a text with NT-like
repetition: every NT segment tested gave X5 ≥ 4.6, against a NONE bound of 2.82. It excludes no prose genre.

**M PRESENT.** Certified only for repetition at the level of the Gospel opening.

### Both arms
**PRESENT wording (E6).** B repeats ordered 5-token or 5-MIDDLE sequences above every modelled no-message generator:
- first-order token and class models fitted to B, corpus-wide or section-wide;
- class Markov;
- copy-and-modify, seeded from the marginal.

**Unmodelled alternatives that a PRESENT cannot exclude:**
- second-order habits;
- folio- or paragraph-level formulae (for example header formulae);
- phrase-level copying at B's own statistics.

A PRESENT is consistent with a message or with such copying. It is not a reading; any interpretation is echo-class.

**False-PRESENT bound.** 0 of 73 no-message runs were PRESENT, which bounds the false-PRESENT rate at about 4% per arm
(95%, rule of three), for the modelled families only. It is about 8% family-wise with two arms. The 20
re-certification runs update this bound.

**Not excluded by any outcome:**
- codes with two or more spellings per word;
- stem codes of recipe, pharmacy, alchemy or verse prose;
- codes whose MIDDLE also varies;
- letter-level verbose ciphers;
- lists, names and labels;
- meaningless text.

**NONE is not evidence of meaninglessness.**

## Registry consequences (per arm; E5)
| Call | Consequence |
|---|---|
| T NONE | A Tier-2 negative-knowledge row with the T scope above. |
| T PRESENT | A Tier-2 measurement row with the E6 wording. |
| T INDETERMINATE | Phase record. |
| M NONE | A Tier-2 negative-knowledge row with the M scope. |
| M PRESENT | A Tier-2 measurement row with the E6 wording. |
| M INDETERMINATE | Phase record. |
| Always | A Tier-2 methods row for stage 1: which merges can and cannot recover interchangeable spellings. |

## Pre-specified descriptives (no verdict)
- TOK, MID and MIDn1 at n = 3, 4 and 6.
- Cross-folio (RPTx) and distinct-sequence (DIST) splits.
- Rarity-filtered repeats.
- EF with last-two-glyph edges.
- **Interior-only windows** (no line-initial or line-final token; O2).
- B's repeated 5-grams (TOK and MID), listed with folios.
- **Null means against the calibration ranges (O1):**
  - TOK5 no-message null means were 0–4.4;
  - MID5 null means were 14.6–27.2 (section-fitted 31–44).
  - The M-arm PRESENT power figures assume B's MID5 null mean is about 27 or less. A higher null compresses X5:
    conservative for NONE, lower power for PRESENT.

## Procedure (E9)
1. **Commit the auditor's scripts** (`scripts/audit/`) before tagging.
2. **Run the re-certification.** If it passes, write the result into this file.
3. **Get the lean-expert confirmation pass** on v2 with the result.
4. **`run774.py --checksums`**, commit, and tag `phase774-lock`.
5. **`run774.py`:**
   - verifies the tag, a clean `scripts/`, no untracked files and the input checksums;
   - logs the Python, numpy and numba versions;
   - runs B once.
6. **The dry run.** `run774.py --dry` has run every code path on two decoys (a whole-word code of Mesue: T PRESENT;
   habit3: NONE / NONE). It is re-run after these edits.

## Caveats
- **The ceilings are fitted to B's adjacent pairs** (declared). A no-message process with stronger or higher-order
  habits could exceed them (E6).
- **The T margin is narrow** at low-repetition prose and verse (6–8 windows against a ceiling of 4).
- **The M arm is an exclusion arm for NT-like repetition.** It is blind to prose stem codes.
- **B-form controls reproduce B's marginals** by construction (needed for ratios to transfer).
- **Lemma = first five letters.**
- **Stage-1 clustering** was tried with one algorithm only.

## Deviations
From v1: E1–E9 and O1–O2 of the lock audit. v1 certification (`prelock_cert.json`) is superseded by the
re-certification, because it reused the design segments. After the lock, any deviation is reported in INDEX.md.
