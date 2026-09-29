# PHASE_768 — Hidden repeats: does Currier B repeat word sequences beyond its local rules? (pre-registration)

**Status:** DRAFT v1 for lean-expert design audit (not yet locked). After lock nothing below may change without a new
phase number.

## Origin
- **Where things stood.** After PHASE_767, the human asked for the hidden-repeats test. Two readings were left:
  - a code whose units are written many ways (a message underneath);
  - disciplined pseudo-writing governed by local habits (no message).
- **The premise.** A real message repeats itself: formulae, repeated ingredients, repeated steps. Local habits create
  no ordered repeats beyond what the local rules themselves produce.
- **Question:** do ordered sequences of consecutive tokens within a line recur in Currier B more often than B's local
  rules produce?

## Prior knowledge (declared)
- **C1790 (Tier 2).** B has zero duplicate lines, only 10 token trigrams that occur in 3 or more folios, and no 4-grams
  that do. There is no null comparison, and within-folio repeats are not counted.
- **C2023 and PHASE_767.** Token-to-token predictability is near a within-line shuffle (+0.02, against 0.12–0.35 in
  every natural text). Identical adjacent tokens occur at chance.
- **Local rules:** boundary glyph coupling (C1212/C1563), qo/ch-sh alternation (C549), word-ending routing (C2082),
  positional zones (C956).
- **Not computed:** any repeat statistic on B relative to a null.
- **Before lock,** B supplied only:
  - its skeleton: lines, lengths, uncertain-token blockers, sections and folios;
  - for the local-rule generators, its class and token transition frequencies.

## Data and representations
- **B:** H track, P placement, labels excluded. 21,610 certain tokens in 2,299 lines. Uncertain tokens are blockers
  (the PHASE_756 primary data).
- **Controls:** every control corpus is laid into B's skeleton (same lines, lengths, blockers, sections and folios), so
  window counts are identical.
- **Primary representation:** TOK, the exact token.
- **Descriptive only:** MID (canonical MIDDLE; the token itself if there is none) and CLS (the 49-class grammar map,
  CLASS_COSURVIVAL_TEST; other tokens are UN). In calibration they had no power against a known cipher (Naibbe X3
  1.00–1.05), and they are strongly affected by local rules.

## Null
- **Primary null, N5j.** This is the PHASE_756 N5 chain:
  - within-line permutations of medial tokens, with line-initial tokens, line-final tokens and blockers fixed;
  - a soft penalty (β = 2) on per-section counts of junction pairs, where each junction unit is (class, edge glyph);
  - this preserves class bigrams, glyph junctions and their interaction together.
- **Chain settings:** shuffled start, 1,000 annealing sweeps, 2,000 burn-in sweeps, then 200 samples thinned by 10
  sweeps. Seeds are fixed.
- **Why N5j:** in calibration, the single-rule nulls N5g (glyphs) and N5c (classes) were each fooled by a generator
  with both kinds of rule (habit2: X3 3.7–4.6 under N5g and 2.9–3.9 under N5c). They are reported descriptively.
- **Mixing diagnostics:** L1/edges and fraction changed. On B-like controls, L1/edges was 0.106–0.116 and fraction
  changed 0.64–0.68.

## Statistic
- **RPT_n:** the number of within-line windows of n consecutive tokens (no blocker inside) whose TOK sequence occurs
  at least twice in the corpus.
- **Excess and p-value:** X_n = (obs + 1) / (null mean + 1); p = (1 + #{null ≥ obs}) / (1 + 200).
- **Splits:** interior (no line-initial or line-final token in the window) and cross-folio (the sequence occurs in 2
  or more folios).

## Calibration (controls only; `results/prelock_*`)
Values are TOK under N5j.

| Corpus | X3 | X4 |
|---|---|---|
| Word-written NTs: Latin, Italian, Spanish, German, English | 6.3–13.7 (p 0.005) | **37.1–134.6** (p 0.005) |
| Same NTs, 4 spellings per word (position-attached) | 15.0–27.5 | 4.85 (la), 9.48 (en), 12.2 (de), 20.5 (es), 21.0 (it); p 0.005 |
| Same NTs, 16 spellings per word | 0.95–4.13 | 1.00 (no repeats at all) |
| Naibbe GV1 cipher of real plaintext (recipes, Antidotarium, Dante) | **2.79–2.95** (p 0.005) | 0.88–2.54 (not significant) |
| Naibbe, answer key (plaintext chunk per token) | 2.3–3.1 | 9.7–24.4 |
| Class-rule generator (habit; 3 seeds) | 0.93–1.37 | 0.76–2.04 |
| Class + junction generator (habit2; 5 seeds) | 1.46–1.78 | 0.47–**3.56** |
| First-order token model fitted on B (habit3; 5 seeds) | **2.15–2.34** | 1.66–3.38 |
| Timm–Schinner (copies earlier words) | 1.33 | 1.66 |

**What calibration shows:**
- **At n = 4,** word-level messages (X4 ≥ 37) separate cleanly from every no-message generator (X4 ≤ 3.56). A cipher
  with letter-level homophones (Naibbe) is invisible at n = 4.
- **At n = 3,** the strongest local-rule reference (habit3, B's own first-order structure) reaches 2.34, while Naibbe
  reaches 2.79. That margin (×1.19) is too thin for a verdict, so n = 3 is descriptive.

## Primary verdict (TOK, n = 4, N5j)
- **Threshold:** T4 = √(max negative X4 × min word-text X4) = √(3.56 × 37.07) = **11.48**.

| Verdict | Condition |
|---|---|
| **WORD-LEVEL PHRASE REPEATS PRESENT** | X4 ≥ 11.48 and p ≤ 0.025; interior and cross-folio p ≤ 0.05 are reported as support |
| **NONE DETECTED** | X4 ≤ 3.56 (the local-rule ceiling), or p > 0.05 |
| **INDETERMINATE** | otherwise |

- **Certification (on controls, before lock):**
  - All five word-written NTs are PRESENT.
  - All 13 no-message generator runs are NONE.
  - With 4 spellings per word, three of five NTs are PRESENT and two are INDETERMINATE (Latin 4.85, English 9.48).
  - Naibbe is NONE, which is the test's stated blind spot.

## Descriptive (pre-specified)
- **n = 3 reading.** B's X3 under N5j is read against the local-rule reference and Naibbe:
  - X3 ≤ 2.34: within B-like first-order local structure;
  - 2.34 < X3 < 2.79: between;
  - X3 ≥ 2.79: at or above the Naibbe level, meaning structure beyond first-order local rules whose cause is not
    determined.

  No registry consequence follows from it by itself.
- **Other reported quantities:**
  - MID and CLS at n = 3 and 4;
  - N5g and N5c;
  - interior and cross-folio splits;
  - B's raw repeated windows and its most frequent repeated 4-grams (for inspection).

## Scope and asymmetry
- **NONE DETECTED:** B does not repeat word sequences beyond its local rules at the level any word-written message
  shows.
  - It excludes a message written word by word (in any language, or as a word-level code) with one spelling per word.
  - It also excludes most such messages with up to four spellings per word.
  - It does not exclude letter- or syllable-level ciphers with homophones (Naibbe type). At n = 4 the test is blind to
    them, and at n = 3 it cannot separate them from local rules.
  - It is not evidence of meaninglessness.
- **PRESENT:** B repeats ordered word sequences beyond its local rules at the scale of natural-language texts. That is
  consistent with phrase-level repetition of a message, or with systematic copying of phrases. It is not a
  translation, and any reading is echo-class.
- **INDETERMINATE:** phase record only.

## Registry consequences
| Verdict | Consequence |
|---|---|
| **NONE DETECTED** | A Tier-2 negative-knowledge row with the power statement above. STATUS_BRIEF §4: "a message written word by word, or a word-level code with few spellings per word: no phrase repetition beyond local rules (C####)". The untested list keeps letter- and syllable-level homophonic ciphers. |
| **PRESENT** | A Tier-2 measurement row. Any reading (message, copying) is echo-class and needs the human's sign-off. |
| **INDETERMINATE** | Phase record only. |

## Caveats
- **The NONE outcome is partly predictable** from C1790 (no 4-grams in 3 or more folios). This test adds the
  local-rule null, within-folio repeats and calibrated power.
- **The local-rule generators are fitted to B.** A richer B model could raise the local-rule ceiling. The 4-gram
  margin is wide (×3.2 on each side of T4).
- **N5j matches B-like junction counts only to within about 11%** (L1/edges 0.11; fraction changed about 0.65). Any
  local structure it leaves unmatched inflates X slightly. The calibration generators carry the same inflation, and
  their ceiling (3.56) sets the NONE threshold. B's diagnostics are reported and compared with theirs.
