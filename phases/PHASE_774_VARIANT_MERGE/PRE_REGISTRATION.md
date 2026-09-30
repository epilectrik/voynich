# PHASE_774 — Merged spellings: does Currier B repeat ordered phrases at the word or MIDDLE level beyond its local habits? (pre-registration)

**Status: v3.1, for lock.** The lean-expert confirmation pass returned LOCKABLE WITH EDITS. Its edits (E1–E5) and
the optional O-a, O-b and O-c are applied below.
- **v1:** the lean-expert lock audit found it **NOT LOCKABLE**.
- **v2:** applied edits E1–E9 and O1–O2, and defined a re-certification on unscored segments before running it.
- **The re-certification failed on one criterion (R2).** A stem code of one Latin NT segment was called NONE on the M
  arm.
- **v3 is the redesign that the v2 rule requires,** with no re-tuning:
  - **the T arm stays confirmatory,** since every criterion that bears on it passed;
  - **the M arm becomes one-sided:** a PRESENT is registrable, and anything else is descriptive, with no exclusion
    claim;
  - **all thresholds are unchanged.**

After the lock nothing below may change without a new phase number.

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

- **Note on the two-spelling code.**
  - The v1 draft cited k1 0.85 for its exchange clustering. That value came from a first, uncommitted run made with an
    earlier generator version, which built the codebook from the whole text.
  - `prelock_recovery.py` is seeded and deterministic. Its committed run with the final code gives **0.50**.
  - No stability claim is made either way.
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
| **T** (confirmatory) | a whole-word code (one spelling per word) | D5 = RPT5_TOK(obs) − mean RPT5_TOK(EF null) | D5 ≥ **7.5** and p ≤ 0.01 | D5 < **4.5**, or p > 0.05 | otherwise |
| **M** (one-sided, v3) | a stem code (frames vary around a fixed MIDDLE) | X5 = (RPT5_MID + 1) / (mean null + 1) | X5 ≥ **7.60** and p ≤ 0.01 | *(no NONE claim; v3)* | *(not PRESENT: descriptive only)* |

**M-arm reporting (v3).** The script prints PRESENT or "not PRESENT". The v2 three-way range (NONE-range /
INDETERMINATE-range) is logged as a description only, with no exclusion scope.

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
| Mesue (pharmacy) | 13 (segments 0–12, incl. re-certification) | 4–194 | 10 PRESENT, 2 INDETERMINATE (P5 6), 1 NONE (P5 4) |
| SISMEL Testamentum (alchemy) | 3 | 30–48 | all PRESENT |
| Codicillus (recipes) | 2 | 8–15 | PRESENT |
| Rupescissa (alchemy) | 2 | 6–11 | segment 0 PRESENT; last **INDETERMINATE** (6.0) |
| Dante (verse) | 2 | 6–10 | segment 0 PRESENT; last **INDETERMINATE** (5.9) |
| New Testaments (Latin, Italian, Spanish, German, English, Turkish) | 35 (incl. re-certification) | 10–605 (≥ 345 at the Gospel opening) | all PRESENT |

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
- In the audit, 9 section-fitted runs gave T D5 ≤ 3.98 and M X5 ≤ 1.83. Their MID5 null means were 31.4–44.7,
  against 14.6–27.2 for the B-like corpus-wide generators.

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

### Re-certification result (`results/prelock_recert.json`; run after the v2 commit 3b1bde3)
| Criterion | Result |
|---|---|
| R1a (P5 ≥ 12 ⇒ T PRESENT) | **PASS**, 31/31 |
| R1b (P5 ≥ 8 ⇒ T not NONE) | **PASS**, 32/32 |
| R2 (no NT stem code NONE on M) | **FAIL:** Latin NT segment 7 (P5 10) gave X5 1.81, which is NONE |
| R3 (20 no-message runs: none PRESENT, ≤ 2 INDETERMINATE) | **PASS:** max D5 1.99, max X5 2.54, 0 INDETERMINATE |
| R4 (twins not PRESENT) | **PASS** |

**T arm, whole-word codes.** D5 tracked the plaintext's own repetition closely (D5 ≈ P5 − null mean):

| Segment | P5 | D5 | Call |
|---|---|---|---|
| Mesue 12 | 4 | 4.0 | NONE |
| Mesue 10 and 11 | 6 | 5.9–6.0 | INDETERMINATE |
| Latin NT 7 | 10 | 10.0 | PRESENT |

Every other segment had P5 ≥ 19 and was PRESENT.

**M arm, stem codes.** NT segments: 25 of 29 PRESENT, 3 INDETERMINATE (X5 4.3–4.9) and 1 NONE (Latin NT 7).

| Mesue segment | X5 | Call |
|---|---|---|
| 8 | 15.8 | PRESENT |
| 7 | 7.09 | INDETERMINATE |
| 9–12 | 0.8–2.3 | NONE |

**Redesign (v3).** The M arm's NONE scope ("excludes NT-like repetition") is refuted by an unscored segment, so the M
arm keeps no exclusion claim.

**Post-hoc, not certified.** In these runs, stem codes of plaintexts with P5 ≤ 19 gave X5 ≤ 2.30. P5 51–76 gave
4.3–7.1, and P5 ≥ 93 gave 8.0 or more. This mapping is **derived from the failed certification set.** It may be
reported as context, never as a scope.

## What each outcome means (scope; E1, E2, E6)
### T arm
**T NONE.** B has fewer than about 5 excess repeated 5-token windows, which is within B-fitted first-order habits.
The re-certification confirmed the scope in plaintext terms:
- every whole-word code of a segment with P5 ≥ 8 was not NONE (32/32);
- every one with P5 ≥ 12 was PRESENT (31/31).

**What D5 measures (O-a).** For a one-spelling code, D5 is essentially arithmetic: P5 (the plaintext's own repeated
5-word windows counted in B's line skeleton), plus a few windows from many-to-one merges, minus the EF null mean.
- That null mean was ≤ 0.11 for every positive with P5 ≤ 10, and ≤ 1.13 up to P5 76.
- The certification's content is therefore the null mean together with the no-message ceiling (≤ 4 windows).

**What a T NONE excludes.** A whole-word code with one spelling per word, written with a frequency-matched (deficit)
assignment of plaintext words to B's token profile, of a plaintext with **P5 ≥ 8** in B's skeleton.
- Other assignments were not tested; seeds varied only the tie-breaks.
- Languages tested: Latin (Codicillus, Mesue, Rupescissa, the SISMEL Testamentum, the Vulgate NT), Italian (Dante, the
  Diodati NT), and the Spanish, German, English and Turkish NTs.
- For reference, a T NONE excludes 12 of the 13 Mesue segments (not segment 12, P5 4) and every NT, SISMEL and
  Codicillus segment tested. Segment 0 of Rupescissa and of Dante is excluded. Their last segments (P5 6) fall below the certified range and are
  not claimed.
- Nothing is claimed below P5 8. At P5 8–11 a PRESENT is knife-edge and is not claimed either.

Low-repetition prose and verse sit just above the ceiling (Rupescissa-last and Dante-last, 6 windows). Those would
give INDETERMINATE, not NONE.

**T PRESENT.** B has 8 or more excess repeated 5-token windows.

### M arm
**M not PRESENT (v3).** Descriptive only: report X5 and the null mean. There is no exclusion claim, because the v2 NONE
scope failed re-certification (a stem code of Latin NT segment 7 was NONE).

**M PRESENT.** B repeats ordered 5-MIDDLE sequences above every modelled no-message generator (see below).
- *Post-hoc context, from the failed re-certification set, not a scope:* control stem codes reached this level at P5
  of about 90 or more. P5 counts whole words, whereas the stem codes are lemma-coded.
- The false-PRESENT side is certified: 0 of 102 no-message runs reached X5 7.60 (maximum 2.82).

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

**False-PRESENT bound (O-c).** 0 of 102 no-message runs were PRESENT on either arm:
- 73 design and v1;
- 20 re-certification;
- the lock audit's 9 section-fitted runs.

19 of the 102 are section-fitted. The rule of three gives about 2.9% per arm at 95%, and about 5.9% family-wise across
the two arms, for the modelled families only.

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
| M PRESENT | A Tier-2 measurement row with the E6 wording. |
| M not PRESENT | Phase record and the methods row: the X5 value, described, with no exclusion claim (v3). |
| Always | A Tier-2 methods row covering stage 1 (which merges can and cannot recover interchangeable spellings) and the M-arm lesson (a stem code of low-repetition text adds no more MIDDLE repeats than B-like first-order habits). |

## Pre-specified descriptives (no verdict)
- TOK, MID and MIDn1 at n = 3, 4 and 6.
- Cross-folio (RPTx) and distinct-sequence (DIST) splits.
- Rarity-filtered repeats.
- EF with last-two-glyph edges.
- **Interior-only windows** (no line-initial or line-final token; O2).
- B's repeated 5-grams (TOK and MID), listed with folios.
- **Null means against the calibration ranges (O1):**
  - TOK5 no-message null means were **0–0.13** (102 runs). The 4.4 in v2 was a whole-word positive, not a
    no-message run.
  - MID5 null means were **14.6–27.2** for the B-like corpus-wide generators (timmU, which is not B-like, gave
    0.2–0.3) and **31.4–44.7** section-fitted.
  - The M-arm PRESENT power figures assume B's MID5 null mean is about 27 or less. A higher null compresses X5 and
    lowers the power for PRESENT.

## Procedure (E9)
1. **Commit the auditor's scripts** (`scripts/audit/`) before tagging.
2. **The re-certification ran** (3b1bde3 → aba5b0e). It failed R2, and v3 is the redesign.
3. **The lean-expert confirmation pass** on v3 returned LOCKABLE WITH EDITS, applied here as v3.1.
4. **`run774.py --checksums`**, commit (with the v3 dry-run outputs), and tag `phase774-lock`.
5. **`run774.py`:**
   - verifies the tag, a clean `scripts/`, no untracked files and the input checksums;
   - logs the Python, numpy and numba versions;
   - runs B once.
6. **The dry run.** `run774.py --dry` has run every code path on two decoys. With the v3 code:
   - the whole-word code of Mesue gave T PRESENT, M not PRESENT;
   - habit3 gave T NONE, M not PRESENT.

   It is re-run once more after v3.1, because the labels and ranges changed.

## Caveats
- **The ceilings are fitted to B's adjacent pairs** (declared). A no-message process with stronger or higher-order
  habits could exceed them (E6).
- **The T margin is narrow** at low-repetition prose and verse (6–8 windows against a ceiling of 4).
- **The M arm is one-sided (v3).** A PRESENT is registrable. A not-PRESENT excludes nothing: stem codes of
  low-repetition text (including one NT segment) add no more MIDDLE repeats than B-like first-order habits.
- **B-form controls reproduce B's marginals** by construction (needed for ratios to transfer).
- **Lemma = first five letters.**
- **Stage-1 clustering** was tried with one algorithm only.

## Deviations
- **From v1:** E1–E9 and O1–O2 of the lock audit. The v1 certification (`prelock_cert.json`) is superseded by the
  re-certification, because it reused the design segments.
- **From v2:**
  - the re-certification failed R2;
  - the M arm becomes one-sided (PRESENT only), with no NONE claim;
  - the T arm and all thresholds are unchanged.
- **After the lock:** any deviation is reported in INDEX.md.
