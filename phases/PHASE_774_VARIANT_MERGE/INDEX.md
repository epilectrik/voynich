# PHASE_774 — Merged spellings: word- and MIDDLE-level phrase repeats under an exact edge-frame null

**Status: COMPLETE.**
- **Lock:** `phase774-lock` (0def12c): pre-registration v3.1, after a lean-expert lock audit (v1 NOT LOCKABLE), a
  re-certification on unscored segments (the M arm failed R2 and was redesigned as one-sided) and a confirmation pass
  (LOCKABLE WITH EDITS, applied).
- **Run:** one pass on Currier B, about 2 minutes at Idle priority. verify_lock passed (Python 3.11.4, numpy 2.3.2,
  numba 0.63.1).
- **Raw results committed before this write-up** (13cdb78): `results/phase774_results.json`, `run_log.txt`,
  `run_stdout.txt`.
- **Results check** by the lean-expert (calls against the locked rules): calls correct, wording fixes applied.
- **Registered:** **C2091** (T arm, negative knowledge) and **C2092** (methods).

## Question (the human's idea)
Could interchangeable spellings hide a message, so that the same thing written twice looks different? If the spelling
variants can be merged, the message's repeated phrases should reappear.

## Results on Currier B (H track, P text: 21,610 tokens, 2,299 lines, 80 folios; EF null, 1,000 permutations)
| Arm | Observed | EF null mean (sd) | Statistic | p | Call |
|---|---|---|---|---|---|
| **T** (whole-word codes; confirmatory) | **0** repeated 5-token windows | 0.04 (0.27) | D5 −0.04 | 1.0 | **NONE** |
| **M** (stem codes; one-sided) | 85 repeated 5-MIDDLE windows | 56.15 (11.9) | X5 1.505 | 0.012 | **not PRESENT** (uninformative on B; see below) |

**T arm.**
- B's TOK5 null mean (0.04) lies inside the no-message calibration range (0–0.13), so the arm's calibration carries
  over and its certified scope holds.
- No within-line 5-token sequence recurs anywhere in B's P-text. The B-fitted first-order no-message generators
  usually give 0 as well (range 0–4).

**M arm: its calibration does not transfer to B.**
- B's MID5 null mean (56.15) is 2.1 times the maximum of the B-like no-message runs (27.2), and above every
  section-fitted run (≤ 44.7).
- The pre-registered power assumption (a null mean of about 27 or less, O1) fails. So the M result says nothing in
  either direction, and X5 is not compared with calibration values.
- **Raw counts:**
  - 85 observed against 56.15 (excess about 29, p 0.012);
  - rarity-filtered (≥ 2 MIDDLEs outside the 20 most frequent): 0 against 0.18.
- All 40 repeated MIDDLE 5-grams are runs of frequent MIDDLEs (e, k, ke, l, ee, aiin, ol). The top example, "ke e l
  e e", occurs 4 times in 4 folios.
- **The cause of the high null mean is not identified.** Two hypotheses:
  - folio-level MIDDLE concentration (compare C531 and C2086);
  - tighter coupling between token edges and MIDDLEs than the generators have.

  Separating them (EF with zone-only or folio-only cells, calibrated on controls first) would be a new phase.

## Descriptives (pre-specified; no verdict)
| Measure | Observed / null | Statistic |
|---|---|---|
| TOK n = 3 | 181 / 109.5 | X 1.65, p 0.001 |
| TOK n = 4 | 4 / 1.26 | p 0.13 |
| TOK n = 6 | 0 / 0 | — |
| Interior-only TOK5 | 0 / 0.02 | — |
| EF with last-two-glyph edges | — | TOK D5 −0.01; MID X5 1.445 |
| MID n = 4 | 1,034 / 800.5 | X 1.29 |
| MID n = 6 | 4 / 2.8 | X 1.32, p 0.41 |
| Cross-folio MID5 | 77 / 52.7 | — |
| Interior-only MID5 | 54 / 37.0 | — |

## Reading
**What this says about the human's idea (interchangeable spellings):**
1. **One spelling per word is ruled out.** B is not a word-for-word code with one spelling per word of any text that
   repeats its phrases even modestly (P5 ≥ 8, C2091).
   - Every such control, in six languages and several genres, produces 8 or more repeated 5-token windows. B
     produces none.
   - This extends C1790 (no 4-grams in 3 or more folios) to n = 5, within and across folios, with a null and a
     certified scope.
2. **With interchangeable spellings, repeat statistics mostly go blind (C2092).**
   - Two unrelated spellings per word already hide a recipe text's phrases.
   - Merging recovers the hidden units only in special cases: a stem that stays fixed while the affixes vary (MIDDLE
     merge), or spellings frequent enough to cluster.
   - Even a perfect MIDDLE merge sees a stem code of low-repetition prose no better than B's own first-order habits.
   - On B itself, the MIDDLE arm is uninformative (the transfer failure above).
3. **What is left open:**
   - codes with two or more spellings per word;
   - stem codes of low-repetition text;
   - letter-level verbose ciphers;
   - lists, names and labels;
   - meaningless text.

   The NONE is **not evidence of meaninglessness**.
4. **For the crib programme.** Statistics without a key can exclude only the simplest encodings. Reading any
   remaining message needs an external anchor: known plaintext at a known place.

## Design history (controls only)
- **Stage 1: which merges recover hidden units** (`prelock_recovery.py`).
  - A MIDDLE merge recovers stem codes.
  - Exchange clustering recovered homophones in only one tested code (the 4-spelling Latin NT code).
  - None of the tested merges recovers Naibbe (best k1 0.41).
- **EF, an exact null**, replaces PHASE_768's non-converging MCMC (`ef774.py`).
- **Power prototypes.** Calibration ratios transfer only at matched marginals, so the controls are written in B's
  forms (saved as a feedback memory).
- **v1 calibration and certification** (`prelock_calib*.py`, `prelock_cert.py`) was superseded: every run reused one
  segment of each plaintext.
- **The lock audit** (`scripts/audit/`, `results/audit/`) led to v2: integer T boundaries, per-arm calls, honest
  scopes, and a re-certification defined before it ran.
- **The re-certification** (`prelock_recert.py`):
  - T arm: every criterion passed (P5 ≥ 12 ⇒ PRESENT, 31/31; P5 ≥ 8 ⇒ not NONE, 32/32; no-message runs ≤ 2
    windows).
  - M arm: R2 failed (a stem code of Latin NT segment 7 gave NONE).
  - v3 therefore made the M arm one-sided, with no re-tuning.
- **Confirmation pass:** its edits were applied as v3.1.

## Scripts
| Script | Role |
|---|---|
| `ef774.py` | the EF null and repeat statistics |
| `merge774.py` | merges and exchange clustering |
| `gen774.py` | control generators: stem codes, codebooks, B-form codes, section-fitted habits, segments |
| `prelock_recovery.py`, `prelock_power*.py`, `prelock_calib*.py`, `prelock_thresholds.py`, `prelock_cert.py`, `prelock_recert.py` | pre-lock calibration and certification |
| `run774.py` | the locked run |
| `audit/audit_stress.py`, `audit/audit_lengths.py` | the lock audit's control-only stress tests |

## Deviations
None from the locked v3.1 procedure. The design's own history (v1 → v2 → v3 → v3.1) is recorded in the
pre-registration.
