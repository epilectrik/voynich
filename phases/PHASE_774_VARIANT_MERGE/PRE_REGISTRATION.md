# PHASE_774 — Merged spellings: does Currier B repeat ordered phrases at the word or MIDDLE level beyond its local habits? (pre-registration)

**Status: DRAFT v1 for the lean-expert lock audit (not locked).** After the lock nothing below may change without a
new phase number.

## Origin
- **The human's idea (2026-09-29).** Some Voynich tokens may be interchangeable, so the same thing written twice can
  look completely different, with the spelling chosen by some criterion (a rule-driven homophonic cipher, H-RC).
- **The experts' proposal.** A variant-merge test, certified on H-RC output, is the one test that could give positive
  evidence of a message: merge the suspected spelling variants, then look for the message's repeated phrases.
- **PHASE_768 (never run on B).**
  - Exact token repeats cannot see a code with many spellings per unit.
  - Its null (N5j, an MCMC over within-line swaps) did not converge at β = 2 and was too loose at β = 1.
  - The phase stopped at design.

This phase:
1. measures which merges can recover hidden units at all (controls only);
2. replaces N5j with an exact permutation null;
3. certifies two arms on fresh controls before touching B.

## Stage 1 (done; controls only): which merges recover the hidden units
Measures:
- **I:** bits kept about the hidden unit.
- **H(M|U):** spelling noise left.
- **k1:** the chance that a true repeat of a unit stays a visible repeat.
- **k0:** the chance collision rate.

Source: `results/prelock_recovery.json` and `_log.txt`.

| Cipher (Latin recipes unless noted) | TOK | MID | Best exchange (Brown) clustering |
|---|---|---|---|
| Naibbe GV1 (letter chunks, ≈ 12 spellings per unit) | k1 0.22 | k1 0.33, k0 0.030 | BR64 k1 0.41, k0 0.006 |
| Stem code: fixed stem, affix frame chosen freely or by rule | k1 0.03–0.04 | **k1 0.71, k0 0.002** | k1 ≤ 0.04 |
| Whole-token code, 2 unrelated spellings per word | k1 0.50 | k1 0.51, k0 0.016 | BR64 k1 0.85, k0 0.003 |
| Whole-token code, 4 unrelated spellings | k1 0.25 | k1 0.26 | k1 ≤ 0.26 (NT: BR64 0.84) |

**Reading:**
- A MIDDLE merge recovers a stem code, where spelling varies only in the prefix and suffix frames.
- Distributional (exchange) clustering recovers homophones only when each spelling is frequent. At B's size, only
  about 800–1,400 types occur 3 or more times, so it fails for hapax-rich codes.
- Nothing recovers Naibbe-type letter ciphers.

## Declared prior knowledge
- **C1790:** B has no duplicate lines, only 10 token trigrams occurring in 3 or more folios, and no such 4-grams. There
  is no null comparison, and within-folio or two-folio repeats are not counted. **The T arm's NONE outcome is
  therefore partly predictable.**
- **C2085 / PHASE_767:** B's order information is near shuffle (+0.02 bits), matched by Naibbe. Identical adjacent
  tokens occur at chance.
- **C2080:** Naibbe as published is excluded. **C2077:** Timm is excluded.
- **PHASE_768:** exact 4-gram repeats separate word-written texts from local-rule generators, but it has no working
  null and was never run on B.
- **Not computed on B before the lock:** no repeat count of any length, no EF run, and no statistic of B's token order
  beyond adjacent pairs.

## B exposure before the lock (declared)
- **B's skeleton:** lines, lengths, uncertain-token blockers, sections and folios.
- **B's marginals, used to write message-present controls in B's forms:**
  - token counts and MIDDLE counts;
  - P(frame | MIDDLE);
  - the within-line frame-to-frame transition counts (adjacent pairs).
- **B's adjacent-token transition counts,** for the no-message habit generators.
  - This follows the PHASE_768 precedent: `habit`, `habit2`, `habit3` and `habit3b` from PHASE_768, and `M1` from
    PHASE_757.
  - They replay B's first-order habits. Their outputs show what those habits produce; they do not show B's
    higher-order repeats.
- **The unseeded Timm control** draws each folio's first line from B's token marginal instead of B's actual first
  line, so no sequence of B's tokens enters any control.

## Data
- **B:** H track, P placement, labels excluded. 21,610 certain tokens in 2,299 lines on 80 folios, with 22 uncertain tokens
  kept as blockers (the PHASE_756 primary data, via `hr768.b_skeleton`).
- **Controls:** laid into B's skeleton, so window counts are identical to B's.

## Representations
- **TOK:** the token.
- **MID:** the canonical MIDDLE from `scripts/voynich.py` Morphology (the token itself when there is none).
- **MIDn1:** MID with e-runs and i-runs collapsed. **Descriptive only.**

## Null: the exact edge-frame permutation (EF)
- **The permutation.** Within each folio, tokens are permuted uniformly among positions that share a **cell** =
  (zone, first glyph unit, last glyph unit).
  - The zones are line-initial, medial and line-final (a one-token line counts as initial).
  - Blockers stay fixed.
- **Preserved exactly:**
  - every folio's token multiset;
  - the edge signature at every position, and so every last-glyph → first-glyph junction pair (C1212/C1563);
  - line-initial and line-final signatures, line lengths and blockers.
- **Destroyed:** which token, among those with the same edges in the same folio and zone, sits where, and with it the
  order of token interiors (MIDDLEs).
- **Sampling is exact:** independent uniform permutations within cells, so there is no chain and no convergence
  question.
- **B run:** 1,000 permutations, seed 77400.
- **A robustness variant** (descriptive) uses the last two glyph units in the cell.

## Statistics and arms
RPT_n(rep) is the number of windows of n consecutive certain tokens within one line whose rep-sequence occurs at least
twice in the corpus. Its p-value is (1 + #{null ≥ obs}) / (1 + R).

| Arm | Question | Statistic | Why this statistic (calibration) |
|---|---|---|---|
| **T** | a whole-word code (one spelling per word) | **D5 = RPT5_TOK(obs) − mean RPT5_TOK(EF null)** | At n = 5 no-message generators make at most 4 repeated windows, and recipe-text codes make 12–15. X is unstable at null means of about 0–4, so the excess count is used. |
| **M** | a stem code (spelling varies in the frames around a fixed MIDDLE) | **X5 = (RPT5_MID + 1) / (mean null + 1)** | MID null means are about 20. At n = 4 chance repeats swamp everything; at n = 6 the no-message generators overlap the recipe codes. |

**On p-values:** EF is a zero-order null within edge cells. First-order habits alone therefore push p below 0.01 in
many no-message runs: 18 of 53 on the M arm and 4 of 53 on the T arm. **p is a requirement, not the discriminator. The
calibrated thresholds carry the decision.**

## Thresholds (fixed by `prelock_thresholds.py` from the design controls; `results/thresholds774.json`)

| | No-message ceiling (53 runs) | Design positive floor | Threshold |
|---|---|---|---|
| T arm | NEG_T = max D5 = **3.97** (habit3b) | POS_T = min D5 of the Latin-recipe and other design whole-word codes = **11.6** | **τ_T = 7.78** (midpoint) |
| M arm | NEG_M = max X5 = **2.82** (habit3b) | POS_M = min X5 of the design New Testament stem codes = **20.46** | **τ_M = 7.60** (geometric mean) |

**The per-arm call:**

| Call | Condition |
|---|---|
| **PRESENT** | statistic ≥ τ and p ≤ 0.01 |
| **NONE** | statistic ≤ the no-message ceiling, or p > 0.05 |
| **INDETERMINATE** | otherwise |

**The overall verdict:**

| Verdict | Condition |
|---|---|
| **PHRASE REPEATS PRESENT (T and/or M)** | either arm PRESENT |
| **NONE DETECTED** | both arms NONE |
| **INDETERMINATE** | otherwise |

## Calibration summary (controls; `results/prelock_calib*.json`)
**Whole-word codes in B's forms (CBB), D5:**
- Latin recipes (Codicillus, 5 seeds): 11.6–15.3.
- Alchemy (Testamentum, SISMEL): 47.5.
- NTs: 345–760.

**Stem codes in B's forms (HRCB-lem), X5:**
- Latin recipes (5 seeds): 1.34–1.99.
- SISMEL: 4.27.
- NTs: 20.5–36.0.

**Not detected by either arm:**
- whole-word codes with **two** spellings per word (Latin recipes D5 0, X5 0.54; Latin NT D5 4.0);
- stem codes of recipe, pharmacy, alchemy or verse prose (X5 1.2–4.3 against the ceiling of 2.82);
- Naibbe (stage 1).

**Twins** (the same machinery with the plaintext order shuffled within folio) are all NONE.

## Certification on fresh seeds (`prelock_cert.py`, criteria written into the script before it ran; `results/prelock_cert.json`)

| Criterion | Result |
|---|---|
| C1: held-out whole-word codes (Mesue, Rupescissa, Dante, German, Spanish and Turkish NTs; 2 new seeds each) ≥ 10/12 PRESENT on T, all of Mesue, Rupescissa, the German NT and the Turkish NT PRESENT | **12/12 PRESENT.** Dante D5 7.9 and 9.8, at the threshold. |
| C2: held-out NT stem codes (German, Spanish, Turkish; 2 seeds each) all PRESENT on M | **6/6** (X5 25.8–39.1) |
| C3: 20 fresh no-message runs (habit3 ×8, habit3b ×8, habit2 ×2, M1 ×2): none PRESENT, ≤ 2 INDETERMINATE | **0 PRESENT, 0 INDETERMINATE** (T D5 ≤ 0; M X5 ≤ 2.56) |
| C4: fresh twins: none PRESENT | **0/4** |

**Certification PASS.**

## What each outcome means (scope)
**NONE DETECTED.** B shows no phrase repetition beyond its first-order local habits at the level either arm is
certified for. It excludes:
- a **whole-word code with one spelling per word** (any language) of a text with at least the phrase repetition of
  the tested Latin pharmacy, alchemy and recipe prose, or of the NTs. Italian verse sits at the threshold;
- a **stem code** (fixed MIDDLE, frames chosen freely or by local rule) of a text as repetitive as a New Testament.

It does **not** exclude:
- whole-word codes with two or more spellings per word;
- stem codes of recipe, pharmacy, alchemy or verse prose;
- codes whose MIDDLE also varies;
- letter-level verbose ciphers (Naibbe type);
- lists, names or labels;
- meaningless text.

It is not evidence of meaninglessness.

**PHRASE REPEATS PRESENT.** B repeats ordered 5-token (T) or 5-MIDDLE (M) sequences beyond what its first-order
habits and edge rules produce, at a level only message-bearing controls reached. That is consistent with a message or
with systematic phrase-level copying. It is not a reading, and any interpretation is echo-class (it needs an external
test or the human's sign-off).

**INDETERMINATE.** Phase record only; report the arm values.

## Registry consequences
| Verdict | Consequence |
|---|---|
| NONE DETECTED | A Tier-2 negative-knowledge row with the scope above, plus a methods row for stage 1: which merges can and cannot recover interchangeable spellings. |
| PHRASE REPEATS PRESENT | A Tier-2 measurement row; any reading is echo-class. |
| INDETERMINATE | Phase record, plus the stage-1 methods row. |

## Pre-specified descriptives (no verdict)
- TOK, MID and MIDn1 at n = 3, 4 and 6.
- Cross-folio (RPTx) and distinct-sequence (DIST) splits.
- Rarity-filtered repeats (≥ 2 symbols outside the 20 or 50 most frequent).
- EF with last-two-glyph edges (T and M arms).
- B's repeated 5-grams (TOK and MID), listed with folios, for inspection after the verdict.

## Procedure
1. `python run774.py --checksums` records the SHA-256 of every input: the transcript, `scripts/voynich.py`, the
   PHASE_756 loader, the PHASE_768 and PHASE_757 modules, tu767 and the class map.
2. Commit and tag `phase774-lock`.
3. `python run774.py` verifies the tag, a clean `scripts/`, no untracked files under `scripts/` and the input
   checksums, then runs B once.
4. **Dry run.** `run774.py --dry` has already run every code path on two decoys:
   - a whole-word code of Mesue: T PRESENT, D5 19.75;
   - a habit3 run: NONE on both arms.

## Caveats
- **The habit generators are fitted to B's adjacent-token transitions** (declared). A no-message process with stronger
  first-order habits than habit3/habit3b could exceed the ceilings. B's own higher-order habits (position formulae,
  copying) would count as repeats, which is why a PRESENT reading includes copying.
- **The T-arm margin is narrow at Italian verse** (D5 7.9 against τ_T 7.78). The Latin prose margins are wider (D5
  10.5–22).
- **The M arm certifies only highly repetitive text.** It is blind to stem codes of recipe-type prose, where a message
  adds no more MIDDLE repeats than B's own first-order habits do.
- **B-form controls reproduce B's marginals by construction,** which the calibration needs (ratios transfer only at
  matched marginals).
- **Lemmas are approximated** by the first five letters of each word.
- **The stage-1 clustering is one algorithm** (exchange clustering at 64–512 classes, count floor 3). Other
  distributional methods were not tried.

## Deviations
None yet. Any deviation after the lock is reported in INDEX.md, and a changed analysis needs a new phase number.
