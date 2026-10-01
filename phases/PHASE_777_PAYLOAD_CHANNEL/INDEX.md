# PHASE_777 — Is one glyph position per word a message channel, with the rest of the word rule-built filler?

**Status: COMPLETE.**
- **Origin:** the human's idea (2026-09-30): "maybe one character in a token is important and the rest is generated
  from rules". The construction tested: each word carries one plaintext letter at a fixed glyph unit and the rest of
  the word is rule-built filler (the mechanics of a one-letter-per-word table cipher; a table that encodes the letter
  in the whole word is a word-level codebook, C2091's territory, not this test's).
- **Why untested before:** every null of PHASE_774–776 fixes each word's first glyph and last two glyphs and scrambles
  only the interiors. A payload in the edge glyphs was preserved in every null sample.
- **Lock:** `phase777-lock` (8cd8571), pre-registration v3 with the confirmation-pass edits. Post-lock integrity: the
  scripts at the run commit (d6bbf02) are unchanged from the lock tag and the inputs match the lock checksums
  (verify_lock ran first).
- **Run:** one pass on B (1,000 permutations per null, about 2 minutes at Idle priority).
- **Raw results committed before this write-up** (d6bbf02).
- **Results check by the lean-expert:** calls correct under the locked rules; the scope wording below follows its
  edits (channel named in every exclusion; plaintexts named, not "tested strength"; the F1 residual's source left
  unidentified; movable mass defined per channel).
- **Registered:** **C2095** (Tier 2, negative knowledge, bounded).

## Question
Does the first or second glyph unit of B's words carry one plaintext letter per word, with the rest of each word
filler built by the boundary rules? Statistic: repeated 7-runs of the position's symbol sequence within lines (RPT7,
z7) under an exact null that scrambles that position among words with the same ending following the same ending,
within folio × line type (EF-F), so the junction coupling (C1212/C1563) and the two-unit routing (C2082) are kept. A
natural-language letter stream repeats 7-letter runs far beyond any first-order chain.

## Result on Currier B (P-text skeleton: 21,610 certain tokens, 2,299 lines, 80 folios; R = 1,000; seed 77700)
| Channel (null; movable / effective) | RPT7 obs / null (sd) | z7 | p | Locked rule (NEG / τ) | Call |
|---|---|---|---|---|---|
| **F1** first unit, 28 symbols (EF-F; 0.587 / 0.532) | 177 / 122.9 (16.3) | **3.31** | 0.003 | 2.85 / 10.54 | **NOT PRESENT (residual band)** |
| **F2** second unit, 37 symbols (EF-F; 0.587 / 0.520) | 178 / 149.4 (17.8) | **1.60** | 0.067 | 3.13 / 10.46 | **NONE** |
| L1 last unit, 32 symbols (EF-L; 0.751 / 0.635) | 2045 / 1956.8 (38.9) | 2.27 | 0.012 | 3.95 / 5.05, descriptive | NONE |
| L2 second-to-last, 35 symbols (EF-L; 0.751 / 0.659) | 1455 / 1369.8 (43.9) | 1.94 | 0.040 | 3.94 / 4.53, descriptive | NONE |
| GAL first gallows, 9 symbols (EF-K2; 0.325 / 0.157) | 4772 / 4768.6 (30.3) | 0.11 | 0.48 | 2.63 / 2.46, descriptive | NONE |

Calls: PRESENT if p ≤ 0.005 and z7 ≥ τ; NONE if z7 ≤ NEG or p > 0.05; otherwise NOT PRESENT (residual band), which is
not a payload call. τ values come from the unrounded NEG and POS (F1 midpoint of 2.85 and 18.22 prints 10.54). POS
was set by the pharmacy text (Mesue) on every channel. "Movable" is the token-level figure (tokens in cells of size
≥ 2); "effective" is the share of tokens whose cell holds at least two distinct channel symbols, so that the symbol
can actually change. Tokens of ≤ 2 glyph units (10.7% of B's tokens) have their F1 symbol fixed by construction, and
tokens of ≤ 3 units (29.2%) their F2 symbol; the payload controls were built from B's own tokens, so they carry the
same blind spot.

**Summary: NO START-POSITION PAYLOAD.** Every payload control gave z7 ≥ 18 on its own arm (Mesue; the others
55–120); B's first unit gives 3.3 and its second 1.6.

- **F2 is a clean NONE on both clauses** (z7 below the design no-payload maximum; p 0.067).
- **F1 lies in the residual band** (above the design no-payload maximum, a third of the way to τ). The band was
  pre-registered as the expected outcome for B-like text: first-order B-like chains break within-cell
  exchangeability (3 of 96 no-payload F-arm calls in the design and v2 certification sets had p ≤ 0.005; 1 of 48
  fresh no-payload certification calls landed in the band, habit3b on F2 at 3.98; NEG is a maximum of 44 runs, so a
  few-percent exceedance rate is built in). **The residual's source is not identified.** The value is where an
  unmodelled no-payload habit lands, where a heavily corrupted payload could land, and where an F2 payload leaks into
  F1 (certification: 3.3–3.7); the last is excluded by F2's NONE, the first two the test does not separate.
- **Refined nulls (descriptive, gate not applicable).** F1 under EFq (line-position quintile added to the key;
  movable 0.388): z 1.11, p 0.15; under EFpar (paragraph × line-type groups; movable 0.317): z 2.04, p 0.027. The
  refined nulls move fewer symbols, so the fall does not decompose the residual; it is not read as "composition".
  F2: 0.62 and 0.06.
- **Composition (descriptive, computed only after the lock).** Line-entropy reduction against within-folio shuffles:
  F1 2.0% (z −7.7), F2 1.6% (z −8.6): B's start symbols are mildly line-homogeneous (cf. C1214). Paragraph χ²/df:
  F1 1.36, F2 1.33. For mapping only, with no inference: payload decoys and controls sit at −3.0% to −0.3%; the line
  palettes that read PRESENT at ≥ 14%; an α 20 line palette at 8% gave z7 3.3; paragraph palettes at PRESENT level
  give χ²/df about 7.
- **Every descriptive at nominal p < 0.05, pooled, uncorrected and not read:** F1 RPT5 z 5.5 (p 0.001, the
  resolution floor; RPT5 shares windows with RPT7 and is not a second test; no RPT5 threshold was locked, the
  prototype's "about 5" for no-payload generators is informal); F2 RPT5 2.06 (p 0.022); F1 EFpar (0.027); L1 (0.012);
  L2 (0.040). EF-L does not keep the two-unit routing, and B-fitted no-payload chains reach L1 z7 2–4, so L1/L2 are
  not payload evidence either way.

## Reading
- **What is excluded, by channel.**
  - **F2 (clean NONE):** one plaintext letter per word at the second glyph unit, written with the frequency-rank
    letter-to-symbol map and B-built filler, is excluded for every plaintext run as an F2 payload under the locked
    thresholds: Latin recipe (Codicillus), Latin NT, Mesue (pharmacy), Dante, the SISMEL Testamentum (design and v2
    certification), the Italian NT (v2 certification), and the German, Spanish, English and Turkish NTs and Rupescissa
    (v1 certification, same thresholds; all ≥ 18). Also with up to 10% of channel symbols replaced at random (audit:
    Mesue at 10% corruption reads F2 z7 7.3, above NEG; the Latin NT ≥ 35).
  - **F1 (residual band):** only noise-free payloads of those plaintexts are excluded; corrupted payloads are not.
  - The filler built with or without the junction rule (the "without" case rests on one prototype control, F1 z7
    79.5).
- **What is not excluded.** A payload in a subset of words (every second word, line-initial words) or spread over
  several positions; a payload carried only by tokens whose channel symbol the null fixes (short words: 10.7% of
  tokens for F1, 29.2% for F2); units larger than letters (syllables, words), where 7-runs would not repeat as letters
  do; homophonic spellings (only random corruption was tested, and homophony is not equivalent to corruption for
  exact 7-window repeats); letter-to-symbol maps not matched to B's symbol frequencies (the controls' maps leave 1–3%
  of B's channel mass unused); plaintexts with less 7-letter repetition than Mesue; end-of-word and gallows positions
  (descriptive only; L1 is 45% y; a strong end payload, z7 18–43 on NT or recipe text, would have shown, and a
  confirmatory end test needs a null keyed on the following ending).
- **The no-payload generators are first-order.** B's start symbols carry line homogeneity (C1214; 2.0% here) that
  they may not reproduce. This matters for a PRESENT (false positives), not for a NONE.
- **For the human's hypothesis:** "one glyph carries the message, the rest is rule-built noise" is excluded at the
  second glyph unit and, for uncorrupted payloads, at the first, for letter-sized messages of the tested kinds. The
  nulls of PHASE_774–776 already covered the interiors (C2091, C2093, C2094). The word end was not tested
  confirmatorily; no claim is made for it.
- **Differential note (lean-expert):** any reading of the F1 residual (composition, a first-glyph specification
  layer, a weak payload) rests on interpretation, not on these numbers.
- It is not evidence of meaninglessness.

## Design history (controls only; B blind until the lock)
1. **Prototype:** payload on F1 gives z7 18–93 on F1 and null elsewhere; twins at null; no-payload generators at most
   about 3 on any channel (RPT5 up to about 5 on the start channels, so RPT7 is primary).
2. **Design calibration** (seeds 7700+, five texts, five channels, 19 no-payload generators, 5 twins): thresholds
   NEG / POS / τ per channel (`results/thresholds777.json`).
3. **v1** (four confirmatory arms F1, F2, L1, L2, three-way calls) **failed its certification** on fresh seeds and
   texts: four no-payload arm calls INDETERMINATE against a limit of two, and an L1 payload read PRESENT on L2 and an L2
   payload on L1 (end positions are correlated within the word; thin margins).
4. **v2:** arms F1 and F2 only, two-way calls (PRESENT, or NOT PRESENT with a descriptive residual flag); L1, L2 and
   GAL descriptive; no threshold changed. Fresh certification (seeds 8100+, one new text plus five design texts at a
   third letter block) PASSED: 0 of 48 no-payload arm calls PRESENT (one in the residual band: habit3b, F2 3.98), no
   cross-arm PRESENT (F2 payloads leak into F1 at 3.3–3.7, residual band), 12 of 12 payloads PRESENT.
5. **Lock audit (lean-expert, controls only):** LOCKABLE WITH EDITS. Findings: payload power survives 5% channel
   corruption (Mesue F1 14.6) and falls below τ at 10% (10.0); no-payload *palette* plants (start symbols drawn from
   a per-paragraph or per-line-position palette at Dirichlet α 5) read PRESENT under EF-F (z7 14–20); two refined
   nulls (EFq: line-position quintile in the key; EFpar: paragraph × line-type groups) remove them while payloads keep
   power. v3 added those nulls as the interpretation gate for a PRESENT, the band-dependent scope with the noise
   figures, corrected null descriptions, and the exposure declarations.
6. **Confirmation pass:** α 7 *line* palettes pass both refined nulls (z7 13–16; EFq 8.5–9.4, EFpar 5.2–7.1) with a
   19% line-entropy reduction, while payloads sit at −3% to −0.3%; the gate gained the condition "line-entropy
   reduction below 8%", and a PRESENT failing it is labelled "payload-level or line palette".
7. **Dry run (four decoys, `results/dryrun/`):** the F1 payload decoy PRESENT and payload-level (z7 89.6; EFq 43.8,
   EFpar 35.8; reduction −2.9%); the edge chain NONE on both arms (0.6, −0.5); the paragraph-palette plant PRESENT
   under EF-F (17.0) and failing the gate as "consistent with a paragraph palette" (EFpar 1.07); the line-palette
   plant PRESENT (15.6), passing EFq/EFpar, labelled "payload-level or line palette" (reduction 19.3%). Composition
   plants alone raise z7 under EF-F to payload level.

## Methods notes
- **Exact edge nulls leave the edges untested.** Fixing each word's first and last glyphs (PHASE_774–776) preserves
  any payload written in them. Testing the edges needs a null that scrambles one edge while keeping the boundary rules:
  key the cell by the *other* edge and the neighbour's facing edge (EF-F: own ending plus preceding ending). Short
  tokens stay fixed; report the effective movable share per channel.
- **p does not carry specificity against B-like chains.** First-order habits break within-cell exchangeability at
  the 5-run level and occasionally at 7; thresholds calibrated on no-payload generators (τ) carry it, and a residual
  band on the real corpus must be pre-registered as an expected outcome whose source the test does not identify.
- **Palettes are the confound of a repeat statistic on a start channel.** Per-paragraph, per-line and per-position
  symbol palettes with no payload produce 7-run repeats at payload level. Refined nulls (position quintile, paragraph
  groups) remove two of the three; line palettes need a composition figure (within-line entropy against a shuffle).
- **End-of-word channels need a routing-preserving null of their own.** EF-L keeps only the next word's first unit,
  not the two-unit routing, so B-fitted chains read p ≤ 0.01 on L1; a confirmatory end-position test would need a
  null keyed on the following token's ending as well.

## Files
- `PRE_REGISTRATION.md` (v3 + confirmation pass; locked), `scripts/chan777.py` (channels, nulls EF-F/EF-L/EF-K2/EFq/
  EFpar, payload and palette constructions, composition figures), `scripts/prelock_proto777.py`,
  `scripts/prelock_calib777.py`, `scripts/prelock_thresholds777.py`, `scripts/prelock_cert777.py`,
  `scripts/run777.py`, `scripts/audit/` (audit777.py, audit777b.py, chaneff777.py, confirm777.py).
- Results: `results/run_log.txt`, `results/phase777_results.json` (the locked run); `results/thresholds777.json`;
  `results/prelock_proto777.json`, `results/prelock_calib777_design.json`, `results/prelock_cert777_v1.json` (failed
  v1), `results/prelock_cert777.json` (v2, PASSED); `results/audit/`; `results/dryrun/`; `results/input_checksums.json`.
