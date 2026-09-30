# PHASE_777 — Is one glyph position per word a message channel, with the rest of the word rule-built filler? (pre-registration)

**Status: DRAFT v1 for the lean-expert lock audit (not locked).** The certification criteria (in
`prelock_cert777.py` and below) were fixed before the certification ran. After the lock nothing below may change
without a new phase number.

## Origin
- **The human's idea (2026-09-30).** "What if they just intentionally inserted noise? Maybe one character in a token is
  important and the rest is generated from rules." This is the Trithemius *Ave Maria* construction (each plaintext
  letter written as a whole word chosen from a table, the ciphertext reading as fluent filler), which a table method
  makes teachable to several scribes and which produces fluent text with a per-section palette and no word-order
  structure in the filler.
- **Why it is untested.** Every null of PHASE_774–776 fixes each word's first glyph and last two glyphs in place and
  scrambles only the interiors. Those tests showed the interiors carry no sequence (C2091, C2093) and the class
  transitions reduce to the boundary rules (C2094). But a payload living in the edge glyphs was preserved in every
  null sample and never tested. This phase tests the edge channels with nulls that scramble them while keeping the
  boundary rules, and the interior channel (the gallows) under the PHASE_776 null.

## Channels (one symbol per certain token)
| Channel | Symbol | Symbols in B | Null |
|---|---|---|---|
| **F1** | first glyph unit | 28 | EF-F |
| **F2** | second glyph unit ('-' if none) | — | EF-F |
| **L1** | last glyph unit | 32 | EF-L |
| **L2** | second-to-last glyph unit ('-' if none) | — | EF-L |
| **GAL** (descriptive) | first gallows-family unit (k, t, p, f, ckh, cth, cph, cfh) or '0' | 9 | EF-K2 |

**Confirmatory arms: F1, F2, L1, L2.** GAL is descriptive: nine symbols cannot carry a letter alphabet one letter per
word without heavy many-to-one collapse, and in the design its Mesue payload control did not separate from the
no-payload maximum (z7 2.3 against 2.6). Its payload controls still run and are reported.

Glyph units follow the PHASE_754 regular expression.

## Statistic
- **RPT7:** the number of within-line windows of 7 consecutive certain tokens (no blocker) whose channel symbol
  sequence occurs at least twice in the corpus. **z7 = (RPT7(corpus) − mean RPT7(null)) / sd(null); p = (1 + #{null ≥
  observed}) / (1 + R).**
- Why 7-runs: a payload of natural-language letters repeats 7-letter runs (common words and endings) far beyond any
  first-order chain, while the rule-built filler's channels do not. RPT5 and DIST7 are descriptive.

## Nulls (exact; within folio × line type; every cell key invariant under the permutation)
- **EF-F** (start-of-word channels): cells = (group, zone, own last two units, preceding token's last two units).
  Every slot keeps its last two units, so every slot's preceding ending is invariant. Preserved: the junction
  coupling and the routing, as P(word start | own ending, preceding ending). Scrambled: the start-symbol sequence among
  words with the same ending that follow the same ending. Movable mass on B: 58.7% (structural exposure: adjacent
  edge-pair information).
- **EF-L** (end-of-word channels): cells = (group, zone, own first unit, following token's first unit). Every slot
  keeps its first unit, so every slot's following start is invariant. Preserved: P(word ending | own start, following
  start). Scrambled: the end-symbol sequence. Movable mass on B: 75.1%.
- **EF-K2** (interior channel): PHASE_776's null (cells = group, zone, first unit, last two units, preceding last two
  units). Movable mass on B: 32.5%.
- The B run uses 1,000 permutations per null, seed 77700.

## Controls (design calibration; `results/prelock_calib777_design.json`, R = 300)
- **POS, payload on channel c:** the plaintext (Codicillus recipes, the Latin NT, Mesue, Dante, the SISMEL
  Testamentum; letter block 0) as a letter stream, one letter per B slot, letters mapped to channel symbols by
  frequency rank (deficit matching onto B's channel marginal, many-to-one for rare letters); the filler is a B token
  with that symbol, drawn from B's continuations after the preceding ending when three or more exist (routing-aware),
  otherwise from all B tokens with that symbol. One control per (plaintext, channel): 25.
- **TWIN:** the same construction with the letter stream shuffled within folio: 5.
- **NEG:** no-payload generators fitted to B: edge chains (k = 2 ×4, k = 1 ×3), habit3 ×3, habit3b ×3, M1 ×2,
  section-fitted habit3b ×2, habit2 ×2: 19.

**Prototype (R = 200, `results/prelock_proto777.json`).** Payload on F1: z7 18–93 on F1, at null elsewhere. Payload
on L1: z7 5–34 on L1. Twins at null. No-payload generators: z7 at most about 3 on any channel; RPT5 up to about 5 on
the start channels (token-level habits leave small sub-word repeats beyond the exact nulls), which is why RPT7 is
primary.

## Thresholds (`prelock_thresholds777.py` → `results/thresholds777.json`)
Per channel c:
- **NEG_c** = max z7 over every design control with no payload on c (the no-payload generators, the twins, and the
  payload controls whose payload is on another channel).
- **POS_c** = min z7 over the design payload controls on c.
- **τ_c** = (NEG_c + POS_c) / 2.

| Call on channel c | Condition |
|---|---|
| **PRESENT** | p ≤ 0.005 and z7 ≥ τ_c |
| **NONE** | p > 0.05, or z7 ≤ NEG_c |
| **INDETERMINATE** | otherwise |

Four arms are called separately (family-wise false-PRESENT about 2% at the p bar alone; τ carries the
specificity).

| Arm | NEG (max no-payload z7, 44 controls) | POS (min payload z7, 5 texts) | τ |
|---|---|---|---|
| F1 | 2.85 | 18.2 (Mesue; others 55–105) | **10.54** |
| F2 | 3.13 | 17.8 (Mesue; others 55–96) | **10.46** |
| L1 | 3.95 | 6.1 (Mesue; others 27–43) | **5.05** |
| L2 | 3.94 | 5.1 (Mesue; others 18–41) | **4.53** |
| GAL (descriptive) | 2.63 | 2.3 (Mesue; others 10–13) | 2.46 |

The end-of-word arms have thin margins because their channels are skewed (L1: y 45%) and the pharmacy text (Mesue)
is the weakest payload; the certification tests them on fresh texts.

## Certification (`prelock_cert777.py`; fresh seeds; fresh plaintexts: German, Spanish, English and Turkish NTs,
Rupescissa, and Mesue's second letter block; criteria fixed before running)
- **C1:** no no-payload run (19 generators, 5 twins) is PRESENT on any arm, and at most 2 INDETERMINATE arm calls in
  all.
- **C2:** no payload control is PRESENT on an arm other than its payload channel.
- **C3:** of the 24 arm payload controls (6 plaintexts × 4 arms), at least 22 are PRESENT on their own arm and none is
  NONE. GAL's payload controls are reported without a criterion.
- PASS = C1, C2 and C3. A FAIL means redesign, with no re-tuning on these seeds.

**Result:** *(filled in after the run)*

## Declared prior knowledge and exposure
- **B's facts relied on:** the boundary coupling and routing (C1212/C1563, C2082); C2091, C2093, C2094 (interiors and
  classes carry no sequence beyond the boundary rules); the channel marginals (F1 28 symbols, dominated by o, q, ch,
  sh, d, a, l; L1 32 symbols, y 45%).
- **B supplied before the lock:** its skeleton and paragraph-first-line flags; its channel marginals and its tokens by
  (preceding ending, channel symbol) for the filler pools (adjacent-pair information); adjacent-pair transitions for
  the no-payload generators (PHASE_768/774/776 precedent); the movable-mass figures above.
- **Not computed on B before the lock:** any repeat count on any channel, any EF-F/EF-L/EF-K2 sample, or any order
  statistic beyond adjacent pairs.

## What each outcome means
**NONE on all four arms.** No edge glyph position of B's words (first, second, last, second-to-last unit) carries a
letter-by-letter payload of natural language: the 7-run repetition of each is what the boundary rules and folio
composition produce. It excludes a Trithemius-style one-letter-per-word cipher on any of the four positions, for plaintexts in the tested languages,
with letters written one per word and the filler built with or without regard to the junction rule. It does not
exclude: a payload spread over more than one position; a payload of units larger than letters (syllables, words) on
one position, where 7-runs would not repeat as letters do; a payload written with homophones on the channel
(several symbols per letter); interleaved or non-consecutive payload positions; a payload confined to a subset of
words (e.g. line-initial). Not evidence of meaninglessness.

**PRESENT on a channel.** That position's symbol sequence repeats 7-runs beyond what the boundary rules and
composition produce, at a level only letter-payload controls reached. That is consistent with a letter channel and
also with any no-payload process that repeats sub-word runs at that position beyond first-order habits; any cipher
reading is echo-class and would justify a decipherment attempt on that channel as its own phase.

**INDETERMINATE.** Phase record.

## Registry consequences
| Outcome | Consequence |
|---|---|
| NONE on all arms | A Tier-2 negative-knowledge row with the scope above (GAL reported descriptively) |
| PRESENT on a channel | A Tier-2 measurement row; the cipher reading Tier 3 pending an external test |
| Otherwise | Phase record |

## Procedure
1. Commit this draft, the scripts and the design results.
2. Run the certification; write its result here.
3. Lean-expert lock audit and confirmation pass.
4. `run777.py --checksums`, commit, tag `phase777-lock`.
5. `run777.py` (verify_lock first; 1,000 permutations per null; raw result committed before the write-up).
6. The dry run (`run777.py --dry`: an F1 payload of Latin NT letters, third block; an edge chain) runs before the lock.

## Caveats
- **The payload controls are one construction.** Letters mapped by frequency rank, filler drawn from B's pools. A
  cipher with a different letter-to-symbol map, or with homophones, gives weaker 7-run repetition; the NONE scope
  says so.
- **The L1 channel is skewed** (y 45%), so its chance repeats are many and its power lower (Mesue payload z7 about 5
  in the prototype).
- **The no-payload generators are first-order.** A no-payload process with higher-order sub-word habits at one
  position could read PRESENT; the descriptives (RPT5, DIST7) and the wording are limited accordingly.
