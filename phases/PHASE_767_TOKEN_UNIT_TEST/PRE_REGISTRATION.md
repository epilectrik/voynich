# PHASE_767 — Is Currier B's unit inventory as small as syllable-written text? (pre-registration)

**Status:** LOCKED (v2, 2026-09-28). Draft v1 went to a lean-expert design audit (verdict "LOCK WITH CHANGES"). This
version incorporates its edits:
- E1–E13, required;
- E14–E16, recommended: E14 adds two native texts, E15 and E16 are statements.

Nothing below may change after lock without a new phase number.

## Question (E1)
Is Currier B's unit inventory as small as that of text written one syllable per token (native or syllabified)? Or is
it in the range of word-written text? Sequencing (F3) and F4–F6 are reported descriptively.

## Origin
- **An explicitly untested rival.** STATUS_BRIEF §4 and CORE/falsifications list "syllable- or word-level codebooks"
  as untested. What is excluded is natural language written one token per word (C132, C2015, C2022).
- **The rival:** a language written syllable by syllable, with a space after each syllable. Two cases:
  - a monosyllabic language such as Chinese (Stolfi's proposal, 1997–2000);
  - an invented syllabary for a European language.
- **The human raised the Chinese idea.**
- **(E2) The PHASE_765 cue is not evidence for syllables.** In this phase's calibration, tolerance of identical adjacent
  repeats (F4) fails validation, because 8 of 15 held-out word-written texts repeat as freely. The phase is motivated by
  the untested-rival listing and the human's proposal, not by that match.
- **Not the same as C2036** (Tier 1), which excluded a different claim: a closed, Chinese-character-style lexicon of
  80–150 MIDDLEs. This phase applies the same inventory logic at token level, with native controls.

## Prior knowledge (declared; E3)
- **Known B facts fix the vocabulary dimension in advance:**
  - 4,889 types in the H track (C2077);
  - TTR 0.212, hapax types 67.2%, hapax tokens 14.2%, top-100 coverage 47.5% (C2055);
  - 7,042 HT/UN tokens, 74.1% hapax (C566), and 4,421 HT/UN types (C740).
- **Implied expectation:**
  - At 20,000 tokens these facts imply roughly 4,000–4,600 types. The native syllable-written texts have 685–1,338 (345–347 without tones).
  - VOCAB_B is expected far on the word side.
  - **The VOCAB call is a calibrated restatement of a known count, not a blind prediction.**
- **Known B facts bearing on F3:**
  - positional zones (C956);
  - line compositional homogeneity (C1214);
  - boundary glyph coupling (C1212, C1563; uncertain spaces are word-internal-like, 0.569 bits, PHASE_761);
  - qo/ch-sh alternation (C549);
  - word-ending routing (C2082);
  - MIDDLE-level adjacency at the within-line-shuffle null (C2023).
- **Not yet computed:** B's features under this phase's definitions.

## Corpora
| Class | Corpora | Role |
|---|---|---|
| WORD (training) | Gaskell & Bowern NTs: Latin (Nova Vulgata), Italian (Diodati 1649), Spanish (Sagradas Escrituras 1569), German (Luther 1545), English (KJV 1611); words as written | axis pole |
| SYL (training) | The same five texts split into syllables by `scripts/syllabify.py` (rule-based, orthographic; SHA-256 6bbbbe03…df516a0), one token per syllable | axis pole |
| Native syllable-written (validation) | Gaskell & Bowern Pinyin Matthew (machine, character by character, tone marks, NFC; 28,372 syllables); Chinese Union Version NT (1919, public domain, eBible `cmn-cu89s`), each Han character given its first Unihan kMandarin reading (223,135 syllables; E14); Vietnamese NT (1923, eBible `vie1934`, public domain; 211,962 syllables); Lahu Si NT (eBible `lhi`, © WBT, used locally for aggregate statistics only; 381,527 syllables; E14) | validation |
| Held-out word-written (validation) | 15 Gaskell & Bowern NTs: French (Martin), Greek (TR), Russian (Marianus), Anglo-Saxon (Hatton), Flemish, Arabic, Hebrew, Maori, Swahili, Tagalog, Turkish, Esperanto, Interlingua, Neo-Quenya, Volapük | validation |
| **B** | ZL 3b Currier B P text (PHASE_761/764 loader; 21,445 tokens), normalised as in E15 | test |
| Reference (not in the verdict; E11) | Naibbe GV1 and Timm–Schinner output in B's skeleton, one seed each (PHASE_765 generators; seeds 767001, 767101); Currier A (ZL; 10,424 tokens; N = 10,000 only) | descriptive |

- **Cleaning:** European texts as in PHASE_764 (NFD, letters only, lower case); native texts keep their diacritics
  (NFC letters).
- **E15, B's normalisation:** ZL 3b lower-case EVA.
  - ZL comments are removed; the first reading of each alternate is kept; ligature braces are dropped.
  - Rare-glyph codes become unreadable. Tokens containing `?` or `*` are dropped and split their line.
  - Uncertain spaces (`,`) are merged.
  - The apostrophe variant mark (45 occurrences) is kept as written.
  - Units are glyph units. F1 and F2 depend only on token identity, not on the unit choice.
  - V1 (H track) bounds the effect of the transliteration.

## Windows and features
- **Re-wrapping and windows:**
  - Every corpus is re-wrapped to B's line-length distribution (PHASE_765 rule).
  - Windows are exactly N = 20,000 consecutive tokens, up to 5 per corpus.
  - Re-wrapping does not reorder tokens, so F1 and F2 do not depend on it.
- **Corpus values:**
  - A control corpus's value is the median over its windows.
  - B's primary value comes from its first 20,000 tokens in manuscript order.

| Feature | Definition | Role |
|---|---|---|
| F1 | log10(types in the window) | **verdict (VOCAB)** |
| F2 | log10(V(20,000) / mean V(2,000) over the window's ten 2,000-token blocks) | **verdict (VOCAB)** |
| F3 | held-out bigram gain: 5 contiguous folds, Witten–Bell bigram vs Jeffreys unigram over within-line test pairs whose tokens occur in training; 1 − H_bi/H_uni | descriptive (SEQ) |
| F4–F6 | identical adjacent repeats; boundary coupling; near-repeats (PHASE_765 definitions) | descriptive |
| X_vge2, X_t80 | log10 of types occurring ≥ 2 times; log10 of the number of types covering 80% of tokens (E9) | descriptive, tail check |
| pair coverage; F3 − shuffle | share of F3 test pairs with both tokens in training; F3 minus its mean over 20 within-line shuffles (first window) | descriptive (E5) |

## Syllable index, validation and sequencing
**Sequencing (E4):**
- **When the rule was written.** Rule (a)–(c) was drafted in working notes before the calibration run, but first
  written to a file after the calibration was seen. Its pre-calibration wording cannot be verified from the
  repository. Feature selection is therefore calibrated on controls, not blind to control outcomes.
- **Blind to B.** No B statistic under this phase's definitions was computed before lock. B was read only for its
  line-length distribution, and the facts under Prior knowledge were already known.
- **Controls only.** All changes made after the calibration, including every audit edit, use control texts only.
- **Hashes.** The calibration outputs are committed in the lock commit. SHA-256 as written (LF):

  | File | SHA-256 |
  |---|---|
  | `calibration_controls.json` | 2d03beba…8e3e |
  | `prelock_controls.json` | ed54edd9…60e5 |
  | `prelock_certification.json` | 00fa463e…297c |

  The replay of the calibration inside `prelock_controls.py` reproduced all 28 frozen medians exactly.

**Syllable index:** s_f(x) = (x − m_W) / (m_S − m_W), where m_W and m_S are the medians of the five WORD and five SYL
training texts. Validation rule: all three must hold.
- (a) SYL − WORD has the same sign in all five pairs.
- (b) Every native text has s_f > 0.5.
- (c) At least 12 of the 15 held-out word-written texts have s_f < 0.5.

**Validation at N = 20,000,** with four natives (`results/prelock_certification.json`):

| Feature | (b) G&B Pinyin / CUV Pinyin / Vietnamese / Lahu | (c) | Valid |
|---|---|---|---|
| F1 | 0.98 / 0.97 / 0.55 / 1.03 | 14/15 (Maori 0.67) | yes |
| F2 | 1.15 / 1.13 / 0.67 / 1.00 | 14/15 (Maori 0.51) | yes |
| F3 | 0.50 / **0.48** / 0.82 / 2.28 | 15/15 | **no** |
| F4 | 1.22 / 1.29 / 0.87 / 0.96 | **8/15** | no |
| F5 | **0.37** / **0.49** / **0.28** / 0.67 | 14/15 | no |
| F6 | 0.69 / **0.496** / 1.19 / 0.72 | **11/15** | no |
| X_vge2 | 0.85 / 0.86 / **0.37** / 1.06 | 14/15 | no |
| X_t80 | 0.80 / 0.82 / **0.41** / 1.10 | 14/15 | no |

- **Toneless natives (V3):** F1 and F2 are valid (Pinyin 1.51/1.58); F3 is not (−0.05 and −0.18).
- **At N = 10,000:**
  - F2 is valid.
  - F1 fails (b) for Vietnamese only (0.491).
  - F3, X_vge2 and X_t80 fail.

## Verdict dimension (E5)
- **One verdict dimension:** VOCAB = mean(clip(s_F1), clip(s_F2)), each clipped to [−1, 2]. This is one construct
  (type richness) measured twice, not two lines of evidence.
- **SEQ = s_F3 is descriptive only,** for these reasons, fixed before lock:
  1. Pinyin passes rule (b) by 0.002 in its only window. The full Chinese NT fails it (0.48).
  2. Toneless Pinyin is on the word side, so F3 tracks how tightly syllables bind inside polysyllabic words, not
     whether a unit is a syllable.
  3. F3 has no within-line-shuffle baseline in the verdict, so in B it can absorb known non-syllabic structure
     (C956, C1214, C1212/C1563, C549, C2082).
  4. Pair coverage differs by class (0.58–0.93 in word texts, the top being Maori; 0.93–0.99 in syllable texts).
- **What is reported for SEQ:** raw F3, F3 − shuffle and pair coverage, for every corpus. No SEQ value is read for or
  against syllables.

## Primary statistic and verdict (E6)
- **Margin:** m_V is the median, over the 10 training corpora, of the window-to-window SD of VOCAB. At N = 20,000,
  m_V = 0.0427.
- **Calls, with thresholds 0.415 and 0.585:**

  | Call | Condition |
  |---|---|
  | **PLAIN-SYLLABLE EXCLUDED** | VOCAB_B < 0.5 − 2m_V |
  | **SYLLABLE-SIZED INVENTORY** | VOCAB_B > 0.5 + 2m_V |
  | **INDETERMINATE** | otherwise |

- **Conditions for a call to stand:** E7 certified it, and E8 holds. Otherwise the call is INDETERMINATE.

## Certification (E7; done before lock on controls only)
The E6 rule was applied to every single window of every native text (no medians), and to the median window of each
held-out word text.
- **PLAIN-SYLLABLE EXCLUDED is certified** if no native window is called EXCLUDED and at least 12 of the 15 held-out
  word texts are.
- **SYLLABLE-SIZED INVENTORY is certified** if every native window is called SYLLABLE-SIZED.

| Setting | m_V | EXCLUDED certified | SYLLABLE-SIZED certified | Native windows |
|---|---|---|---|---|
| N = 20,000 | 0.0427 | **yes** (14/15 held-out; Maori 0.59 not) | no (Vietnamese 0.561 INDETERMINATE) | Pinyin 1.07; CUV 1.05–1.11; Lahu 0.98–1.06; Vietnamese 0.56–0.64 |
| N = 20,000, V3 toneless | 0.0427 | **yes** | yes | 1.54–1.55 |
| N = 20,000, V4 syllabifier | 0.0464 | **yes** | no (Vietnamese) | Vietnamese 0.59–0.67 |
| N = 10,000 | 0.0353 | **yes** | no (Vietnamese 0.537) | Vietnamese 0.54–0.61 |
| N = 10,000, V4 | 0.0330 | **yes** | yes | Vietnamese 0.57–0.65 |

- **Leave-one-pair-out on VOCAB alone:** 10/10 correct under the E6 rule.
- **The drafted two-dimension rule is withdrawn.** On the calibration it returns INDETERMINATE for Pinyin (SEQ 0.50),
  and word-written Maori (VOCAB 0.59) could only come out MIXED or INDETERMINATE.
- **Consequence:** a SYLLABLE-SIZED call for B would not be certified at N = 20,000 and would be reported as
  INDETERMINATE.

## Robustness (E8)
The folio jackknife is dropped: removing one folio leaves at least 96% of the window unchanged, so it cannot fail. A
call must also hold in both of the following, otherwise it is INDETERMINATE:
- **(i) At N = 10,000,** with the N = 10,000 axes, margin (m_V = 0.0353) and certification above, in both halves of
  each of 20 random folio bipartitions of B.
  - Bipartition i (i = 0…19): folios in random order (seed 767800 + i).
  - The first half takes folios until it holds at least half of B's tokens; the rest form the second half.
  - Each half is re-wrapped (seed 767900 + i) and scored on its first 10,000 tokens.
- **(ii) On B's last 20,000 tokens.**

V1, V2 and V6 are reported. Any variant that flips the call is stated in any registry row.

## Variants (reported; the primary verdict stands)
| Variant | Change |
|---|---|
| V1 | B from the H track (P placement; uncertain tokens split lines) |
| V2 | B with uncertain spaces split (ZL `,` treated as a space) |
| V3 | Toneless Pinyin natives (certified, above) |
| V4 | Alternative syllabifier (no onset clusters; certified, above) |
| V5 | N = 10,000, B's two windows (certified, above; also used in E8) |
| V6 | No re-wrap. VOCAB is identical by construction; reported for SEQ only |

## Tail check (E9)
- **Screen result:** X_vge2 and X_t80 fail the (a)–(c) screen. Vietnamese sits at 0.37 and 0.41, so neither
  statistic separates a large syllable inventory from word text.
- **Consequence:** any registry row states that the exclusion may rest partly on B's hapax tail (C566, C740).
- **Reported for B:** its raw V≥2 and T80, beside the largest syllable-written control.

## Spelling-variation control (E10; controls computed before lock)
- **Construction:** every syllable type of each syllabified training text and each toned native text gets k distinct
  spellings, one drawn uniformly per token.
- **Results (types at 20,000, VOCAB, SEQ):**

  | k | European syllabified (5) | Native (4) |
  |---|---|---|
  | 1 | 694–1,237 types, VOCAB 0.66–1.05 | 685–1,338 types, VOCAB 0.61–1.07 |
  | 2 | 1,161–1,984, VOCAB 0.41–0.77, SEQ −0.19–0.31 | 1,143–2,181, VOCAB 0.38–0.76 |
  | 4 | 1,861–3,064, VOCAB 0.17–0.52, SEQ −1.21 to −0.81 | 1,889–3,404, VOCAB 0.13–0.50 |
  | 8 | 2,901–4,522, VOCAB −0.05–0.28, SEQ −1.96 to −1.66 | 3,001–5,023, VOCAB −0.11–0.23 |
  | 16 | 4,371–6,436, VOCAB −0.27–0.04, SEQ −2.33 to −2.11 | 4,519–7,096, VOCAB −0.34 to −0.02 |

- **Two consequences:**
  - Random spelling variation carries a syllable text across the whole word range of VOCAB.
  - It also drives SEQ far below word text, as expected: gain ≈ I/(H + log2 k), with sparser bigrams.
- **After unblinding, k\*:** the value of k at which the median VOCAB of the nine syllable texts (k = 1, 2, 4, 8, 16)
  equals VOCAB_B, found by linear interpolation in log2 k. If VOCAB_B lies below the k = 16 median, k\* is reported as
  "> 16".

## Reference generators (E11)
- **What is reported:** Naibbe GV1 (sub-word units written with homophonic variation) and Timm–Schinner output, on
  VOCAB, X_vge2, SEQ and F3 − shuffle.
- **Not in the verdict.** Any registry row states where they fall.
- **Floor check:** if either lands on the syllable side of SEQ, the phase record states that F3 is a floor.

## Outcome names and scope (E12)
- **PLAIN-SYLLABLE EXCLUDED means only this:** B's unit inventory is too large for writing one spelling per syllable
  with a space after each, in every tested language, native or syllabified. The languages tested are Mandarin (with
  and without tones, in two texts), Vietnamese, Lahu and the five European syllabifications.
  - It does not say B's tokens are words or language: any unit system with a large inventory reaches the same side
    (E10, E11).
  - It does not exclude syllables written with spelling variation (a syllabic reading needs about k\* spellings per
    syllable), morpheme-sized units, or codebooks with homophones.
- **SYLLABLE-SIZED INVENTORY** would mean only that B's inventory is as small as syllable-written text.
  - Word-written Maori also reaches that side (VOCAB 0.59), so it does not establish sub-word units and identifies no
    language.
  - It is not certified at N = 20,000.
- **Struck:** the MIXED outcome, and the sentence linking word-like vocabulary with syllable-like sequencing to
  syllables written with spelling variation.
  - Random variation lowers F3 (E10).
  - B's known adjacent-token dependencies could produce syllable-like SEQ without syllables.

## Registry consequences (E13)
**PLAIN-SYLLABLE EXCLUDED:**
- **The row:** a Tier-2 negative-knowledge row in E12's wording. It states:
  - B's V(20,000) beside the largest syllable-written control;
  - k\* (E10);
  - the tail-check caveat (E9);
  - where the E11 generators fall;
  - any variant that flips the call.

  It cross-references C2036 (the same inventory logic at MIDDLE level, for a closed lexicon).
- **STATUS_BRIEF §4 and CORE/falsifications** get this text: "Syllable writing, or a syllable codebook, with one
  spelling per syllable: tested and excluded on unit inventory (C####). Untested: syllables written with spelling
  variation (including homophonic syllable codebooks), morpheme-sized units, word-level codebooks, modified verbose
  ciphers, the Rugg grille, and improvisation in a practised script at book scale."
- **Caveat:** excluding a rival is not evidence for the working interpretation.

**Other outcomes:**
- **SYLLABLE-SIZED INVENTORY** (certified only in the settings above): a Tier-2 measurement row. Any reading (a
  syllabary, Chinese, a named language) is echo-class and needs the human's sign-off and an external test.
- **INDETERMINATE:** a phase record plus a STATUS_BRIEF §4 note, "tested at 20,000 tokens: inconclusive (reason)", so
  the untested listing is corrected in every outcome.

**In every outcome:**
- SEQ and F4–F6 are recorded as measurements.
- Neither direction of them changes any status or adds anything to RESEARCH_AGENDA.

## Caveats (E16)
- **The VOCAB call is predictable from declared counts** (E3).
- **Few native texts:**
  - Native texts are few: four, in three languages.
  - The Gaskell & Bowern Pinyin has one window.
  - The two Chinese texts are machine transliterations, character by character.
- **Untested unit sizes:** morpheme-sized units are untested and may fall near the 0.5 line.
- **Maori:** word-written Maori reaches the syllable side of VOCAB.
- **Syllabifier:** it is orthographic and rule-based (V4 tests its sensitivity).
- **Vietnamese** carries some legacy encoding artifacts in names.
- **B is one 20,000-token window.** The margin and E8 bound its noise.
