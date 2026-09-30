# PHASE_777 — Is one glyph position per word a message channel, with the rest of the word rule-built filler? (pre-registration)

**Status: DRAFT v2 for the lean-expert lock audit (not locked); v2 certification PASSED (below).**
- **v1** (four confirmatory arms F1, F2, L1, L2 with three-way calls) **failed its certification** on fresh seeds and
  texts (`results/prelock_cert777_v1.json`): C1 failed on the INDETERMINATE count (4 no-payload arm calls fell between
  the design no-payload maximum and τ, against a limit of 2; none was PRESENT), and C2 failed because an L1 payload
  read PRESENT on L2 and an L2 payload on L1 (end-of-word positions are correlated within the word and their margins
  are thin). C3 passed 24 of 24.
- **v2 is the redesign** the v1 rule requires, with no threshold changed: confirmatory arms **F1 and F2 only**, each
  called two ways (PAYLOAD PRESENT, or NOT PRESENT with a descriptive residual flag); L1, L2 and GAL descriptive; a
  fresh certification (seeds 8100+, fresh texts, third letter block) with criteria fixed before running.

After the lock nothing below may change without a new phase number.

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

**Confirmatory arms (v2): F1 and F2.** L1 and L2 are descriptive (v1 certification: correlated within the word,
thin margins, a no-payload run reached z7 4.6 on L1 against τ 5.05). GAL is descriptive: nine symbols cannot carry a
letter alphabet one letter per word without heavy many-to-one collapse, and in the design its Mesue payload control did
not separate from the no-payload maximum (z7 2.3 against 2.6). The descriptive channels are reported with their
design thresholds and carry no exclusion claim; a strong end-of-word payload (design controls: z7 18–43 on NT, recipe
and alchemy text; 5–7 on Mesue) would still be visible descriptively.

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

| Call on arm c (v2, two-way) | Condition |
|---|---|
| **PAYLOAD PRESENT** | p ≤ 0.005 and z7 ≥ τ_c |
| **NOT PRESENT** | otherwise; with the descriptive flag "residual above the design no-payload maximum" when z7 > NEG_c and p ≤ 0.05 |

Two arms are called separately (family-wise false-PRESENT about 1% at the p bar alone; τ carries the specificity).
The exclusion licensed by NOT PRESENT rests on C3: every payload control at the tested strength lies far above τ
(design minimum 18.2 on F1 and 17.8 on F2 against τ about 10.5).

| Arm | NEG (max no-payload z7, 44 controls) | POS (min payload z7, 5 texts) | τ |
|---|---|---|---|
| F1 | 2.85 | 18.2 (Mesue; others 55–105) | **10.54** |
| F2 | 3.13 | 17.8 (Mesue; others 55–96) | **10.46** |
| L1 | 3.95 | 6.1 (Mesue; others 27–43) | **5.05** |
| L2 | 3.94 | 5.1 (Mesue; others 18–41) | **4.53** |
| GAL (descriptive) | 2.63 | 2.3 (Mesue; others 10–13) | 2.46 |

The end-of-word arms have thin margins because their channels are skewed (L1: y 45%) and the pharmacy text (Mesue)
is the weakest payload; the certification tests them on fresh texts.

## v1 certification (failed; `results/prelock_cert777_v1.json`; fresh seeds, German/Spanish/English/Turkish NTs,
Rupescissa, Mesue's second letter block)
- C1 failed: 0 PRESENT but 4 INDETERMINATE no-payload arm calls (F1 3.38, F2 3.16 and 3.19, L1 4.60) against a limit
  of 2. C2 failed: L1 payload (Turkish NT) PRESENT on L2 (z7 6.3); L2 payload (German NT) PRESENT on L1 (6.7); F1 and
  F2 payloads leaked only as INDETERMINATE (L1 4.1; F1 4.3). C3 passed 24 of 24 (F1 18–120, F2 19–112, L1 7–46,
  L2 6–45). GAL payloads: 5.6–14.3.

## v2 certification (`prelock_cert777.py`; seeds 8100+; texts: Italian NT, Latin NT, SISMEL, Mesue, Codicillus,
Dante; third letter block; criteria fixed before running)
- **C1:** no no-payload run (19 generators, 5 twins) is PAYLOAD PRESENT on F1 or F2.
- **C2:** no payload control is PAYLOAD PRESENT on the other F arm.
- **C3:** of the 12 F-arm payload controls (6 plaintexts × F1/F2), at least 11 are PAYLOAD PRESENT on their own arm.
- L1 payload controls (6) and all L1/L2/GAL values are reported without a criterion.
- PASS = C1, C2 and C3. A FAIL means redesign, with no re-tuning on these seeds.

**Result** (`results/prelock_cert777.json`, run after the v2 draft was committed at 9347be9): **PASS.**

| Criterion | Result |
|---|---|
| C1 (no no-payload run PAYLOAD PRESENT on F1 or F2) | pass: 0 of 48 arm calls; max no-payload z7 F1 2.40, F2 3.98; one residual flag (F2) |
| C2 (no cross-arm PRESENT among F payloads) | pass |
| C3 (≥ 11 of 12 F-arm payload controls PRESENT) | pass: 12 of 12 (F1 and F2 both ≥ 18 on Mesue, higher on the others) |

L1 payload controls (descriptive): all six above the design L1 threshold (z7 8.3 Mesue; 18.5–44.6 the others), with
no leakage into L2 (z7 0.5–2.4). No-payload maxima on the descriptive channels: L1 3.4, L2 3.3, GAL 2.0.

**Dry run (v2 code):** the F1 payload decoy (Latin NT, third letter block) is PAYLOAD PRESENT on F1 (z7 89.6) and NOT
PRESENT on F2; the edge-only decoy is NOT PRESENT on both arms (F1 z7 0.6, F2 −0.5); all descriptive channels NONE in
both.

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
**NOT PRESENT on both arms.** Neither the first nor the second glyph position of B's words carries a
letter-by-letter payload of natural language at the tested strength: their 7-run repetition is far below every payload
control. It excludes a Trithemius-style one-letter-per-word cipher on the first or second position, for plaintexts in the tested languages,
with letters written one per word and the filler built with or without regard to the junction rule. It does not
exclude: a payload spread over more than one position; a payload of units larger than letters (syllables, words) on
one position, where 7-runs would not repeat as letters do; a payload written with homophones on the channel
(several symbols per letter); interleaved or non-consecutive payload positions; a payload confined to a subset of
words (e.g. line-initial). Not evidence of meaninglessness.

**PAYLOAD PRESENT on an arm.** That position's symbol sequence repeats 7-runs beyond what the boundary rules and
composition produce, at a level only letter-payload controls reached (no no-payload run in design or certification
did). The arm does not identify the position exactly: an F2 payload leaks into F1 as a residual. That is consistent with a letter channel and
also with any no-payload process that repeats sub-word runs at that position beyond first-order habits; any cipher
reading is echo-class and would justify a decipherment attempt on that channel as its own phase.

**INDETERMINATE.** Phase record.

## Registry consequences
| Outcome | Consequence |
|---|---|
| NOT PRESENT on both arms | A Tier-2 negative-knowledge row with the scope above (L1, L2, GAL reported descriptively, no exclusion for end positions) |
| PAYLOAD PRESENT on an arm | A Tier-2 measurement row; the cipher reading Tier 3 pending an external test |

## Procedure
1. Commit this draft, the scripts and the design results.
2. Run the certification; write its result here.
3. Lean-expert lock audit and confirmation pass.
4. `run777.py --checksums`, commit, tag `phase777-lock`.
5. `run777.py` (verify_lock first; 1,000 permutations per null; raw result committed before the write-up).
6. The dry run (`run777.py --dry`: an F1 payload of Latin NT letters, third block; an edge chain) runs before the lock.

## Deviations
- **From v1:** the certification failed C1 and C2; v2 restricts the confirmatory arms to F1 and F2 with two-way calls,
  and re-certifies on fresh seeds. No threshold changed.

## Caveats
- **The payload controls are one construction.** Letters mapped by frequency rank, filler drawn from B's pools. A
  cipher with a different letter-to-symbol map, or with homophones, gives weaker 7-run repetition; the NONE scope
  says so.
- **The L1 channel is skewed** (y 45%), so its chance repeats are many and its power lower (Mesue payload z7 about 5
  in the prototype).
- **The no-payload generators are first-order.** A no-payload process with higher-order sub-word habits at one
  position could read PRESENT; the descriptives (RPT5, DIST7) and the wording are limited accordingly.
