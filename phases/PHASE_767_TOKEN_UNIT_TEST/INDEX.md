# PHASE_767 — Is Currier B's unit inventory as small as syllable-written text?

**Status:** COMPLETE. Locked verdict: **PLAIN-SYLLABLE EXCLUDED**.
- The call is certified on the controls, and the robustness checks (E8) hold.
- Every variant agrees.
- Registered as C2085 (Tier 2, negative knowledge).

**Pre-registration:** `PRE_REGISTRATION.md`, locked at commit caf7127 after a lean-expert audit (edits E1–E16). All
calibration, feature validation and certification used control texts only, before lock.

**Scripts:**
- `tu767.py` (corpora, features) and `syllabify.py` (frozen).
- `calibrate_controls.py`, `validate_features.py`.
- `prelock_controls.py` (16 min), `prelock_certify.py`.
- `token_unit_test.py` (42 s).

**Results:** `results/token_unit_test.json`, `results/run_log.txt`. Pre-lock: `calibration_controls.json`,
`prelock_controls.json`, `prelock_certification.json`.

**Corpora** (raw files in git-ignored `external/`):
- Gaskell & Bowern NTs;
- Vietnamese NT (1923, public domain);
- Chinese Union Version NT (1919, public domain), transliterated with Unicode Unihan kMandarin;
- Lahu Si NT (© WBT; used locally for aggregate statistics only).

## Question
- **Why this test:** the human proposed that the manuscript might write a language such as Chinese in an invented
  notation. The registry also listed "syllable-level codebooks" as an untested rival.
- **The test:** is B's inventory of units as small as that of text written one syllable per token, or in the range of
  word-written text?
- **Controls:**
  - the same five European Bibles written by word and split into syllables;
  - four natively syllable-written texts: two Mandarin Pinyin texts, Vietnamese and Lahu Si;
  - 15 other word-written languages.

## Result
| Text | Types per 20,000 tokens | VOCAB index (0 = word texts, 1 = syllable texts) |
|---|---|---|
| **B (ZL, uncertain spaces merged)** | **5,141** | **−0.34** (threshold 0.415) → PLAIN-SYLLABLE EXCLUDED |
| B, H track (V1) | 4,347 | −0.22 |
| B, uncertain spaces split (V2) | 4,248 | −0.22 |
| Word-written texts (20) | 1,130 (Maori) – 6,041 (Turkish) | −0.40 to +0.59 |
| Syllabified European texts (5) | 694–1,237 | 0.66–1.05 |
| Mandarin Pinyin (Matthew; CUV NT) | 729; 739 (toneless 347; 345) | 1.07; 1.05 (toneless 1.54) |
| Vietnamese | 1,338 | 0.61 |
| Lahu Si | 685 | 1.01 |
| Naibbe GV1 / Timm–Schinner (reference) | 4,255 / 7,557 | −0.11 / −0.78 |
| Currier A (reference, per 10,000 tokens) | 3,447 | −0.39 |

- **Certification (before lock):** no window of any native syllable-written text was called EXCLUDED, in every
  setting (20k and 10k windows, toneless, alternative syllabifier). 14 of 15 held-out word texts were called EXCLUDED;
  Maori was not.
- **Robustness (E8):**
  - In 40 of 40 random folio halves at 10,000 tokens, B was called EXCLUDED (VOCAB −0.35 to −0.29).
  - B's last 20,000 tokens: −0.34.
  - Every variant (V1–V6) was called EXCLUDED, with VOCAB between −0.36 and −0.22.
- **Spelling variation (k\*):** as syllables get more random spellings, the median VOCAB of the nine syllable texts
  falls:

  | Spellings per syllable (k) | 1 | 2 | 4 | 8 | 16 |
  |---|---|---|---|---|---|
  | Median VOCAB | 1.01 | 0.75 | 0.44 | 0.14 | −0.13 |

  B is at −0.34, so **k\* > 16**: a syllabic reading needs more than 16 interchangeable spellings per syllable.
- **Tail check (E9):** the V≥2 and T80 screen failed on Vietnamese, so the pre-registered caveat applies: the exclusion
  may rest partly on B's hapax tail (C566, C740).
  - B's types occurring at least twice number 1,449. The syllable-written controls reach at most 976; word texts span
    704–2,291.
  - B needs 1,295 types to cover 80% of its tokens. Syllable-written controls need at most 272; word texts 118–2,193.

**Descriptive (recorded as measurements; not read for or against syllables):**
- **Token-to-token predictability above a within-line shuffle** (held-out bigram gain minus its shuffle mean): B
  **+0.02**.
  - Every natural text, word- or syllable-written, sits at 0.12–0.35.
  - The generators: Naibbe +0.02, Timm 0.00.
  - B's pair coverage is 0.67, within the word-text range (0.58–0.93), so this is not a sparsity effect.
- **Identical adjacent repeats:** B **+0.03** (log observed/expected, i.e. at chance). Every control text avoids them
  (−4.4 to −0.6).
- **Boundary coupling:** 0.060, near Tagalog (0.057) and Lahu (0.052).
- **Near-repeats:** +0.08.

## Reading
- **What is excluded:**
  - B's tokens are not syllables written with one spelling each and a space after each. This holds for Chinese (Pinyin
    with or without tones), Vietnamese and Lahu, and for an invented syllabary applied to Latin, Italian, Spanish,
    German or English.
  - B has about four times the vocabulary of the richest syllable-written text. For Mandarin it is close to a counting
    fact: B has more types in 20,000 tokens than Mandarin has toned syllables in total (about 1,300; the Chinese NT
    uses 970).
- **What is not excluded:**
  - syllables written with heavy spelling variation (more than 16 spellings each on average, as in homophonic syllable
    codebooks);
  - morpheme-sized units;
  - word-level codebooks.
- **What this does not show:** that B's tokens are words or language. Any large-inventory unit system lands on the
  same side, and so do both generators.
- **Descriptively, B's sequencing is unlike every natural text of either unit size.**
  - Adjacent token identities barely predict each other beyond a shuffle, and identical neighbours occur at chance.
  - This matches the generator references and fits C2023 (MIDDLE adjacency at the shuffle null).
  - B's strong ordering lives at the glyph and class level (C1212/C1563, C549, C2082), not in which word follows
    which.
  - This is a measurement, not an interpretation.

## Deviations
- **Folio halves:** the pre-registration did not fix the token order inside each folio half. Manuscript order was
  used.
- **Prior expectation:** the expectation of 4,000–4,600 types came from H-track counts. With uncertain spaces merged,
  ZL gives 5,141. The H track gives 4,347, within the expectation. No rule is affected.
