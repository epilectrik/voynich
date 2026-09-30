# PHASE_775 — Is Currier B's word-boundary rule the key of a context-keyed cipher? (pre-registration)

**Status: DRAFT v1 for the lean-expert lock audit (not locked).** The certification criteria below were fixed before
the certification ran. After the lock nothing below may change without a new phase number.

## Origin
- **The human's challenge.** The human asked for a genuinely new test, text-only, "looking at things in a way a human
  cannot", following their idea that "the letters or tokens you pick change based on some criteria" (H-RC).
- **The idea.** B's strongest local rule couples a word's beginning to the previous word's ending (C1212/C1563) and
  routes the next word's class by that ending (C2082). A cipher whose alphabet is selected by the previous ciphertext
  word's ending (a context-keyed or "autokey-like" substitution) would leave exactly this fingerprint.
- **The key-removal algorithm ("rank decoding").** Replace every token by its frequency rank among the tokens that follow
  the same context. Under a context-keyed substitution, rank r in every context stands for the same hidden unit, so the
  hidden text's word order reappears among the ranks.
- **Prior work.** This is Friedman's column-alignment idea for polyalphabetic ciphers with the boundary rule as the key
  schedule. No registered test has asked whether B's boundary coupling acts as a key.

## Method
**Keys** (the context c_i of token i):
- **K0:** one context (global frequency rank; the reference).
- **K1:** the previous token's last glyph unit.
- **K2:** the previous token's last two glyph units.

Line-initial tokens and tokens after an uncertain-token blocker take the context '^'. Glyph units follow the PHASE_754
regular expression.

**Decoding.** Within each context, tokens are ranked by count (ties: global count, then token). The decoded symbol is the
rank, with ranks from 21 upward pooled into one symbol. The decoder is re-estimated on every corpus it is applied to,
null samples included.

**Statistics:**
- **S_K:** plug-in mutual information (bits) between consecutive decoded symbols within a line.
- **dS_K:** S_K − mean S_K over null samples.
- **Key gain G_K = dS_K − dS_K0,** with p_G = the share of null samples whose raw key gain (S_K − S_K0) is at least the
  corpus's.

**Null: header-aware EF.** The PHASE_774 exact within-folio permutation, here within folio × line type (paragraph-first
line or body line).
- Tokens are permuted among positions that share group, zone, first glyph unit and last two glyph units.
- EF keeps every position's K1 and K2 context exactly. It destroys which token fills a context's slot, which is where a
  context-keyed cipher carries its message.
- Line type keeps B's paragraph-first-line vocabulary from being mixed into body lines.
- The B run uses 1,000 permutations, seed 77500.

## Why the key gain (design calibration, controls only; `results/prelock_calib775_design.json`)
**Context-keyed ciphers** (B-like alphabets, true key K1 or K2) on segment 0 of Latin recipes, the Latin and Italian NTs,
Dante, the SISMEL Testamentum, and Mesue segments 0–1:

| Cipher | Key gain | p |
|---|---|---|
| True key K1 | G_K1 +0.0057 to +0.0230 | ≤ 0.005 |
| True key K2 | G_K2 +0.0043 to +0.0192, except Mesue segment 1 (−0.0005) | — |
| Two spellings per unit and context (Latin recipes, Latin NT) | G +0.0069 to +0.0109 | — |

**Every control without a keyed message had a negative key gain** (up to −0.0002; 36 runs):
- 28 B-fitted no-message runs: habit3, habit3b, section-fitted, habit2, M1 and habit;
- 6 shuffled-plaintext twins (the same key mechanism, no word order);
- 2 plain one-spelling word codes (−0.007 to −0.027: global ranks see a plain code better).

**Why no-key controls go negative.** Ranking within a context merges different tokens that share a rank. That throws
away token-identity habits unless the ranks really are the same hidden unit.

**The word-order index O** is the plaintext's own consecutive-rank mutual information minus its within-folio shuffle.
In the design: Mesue segment 0 0.010, Mesue segment 1 0.030, Latin recipes 0.045, SISMEL 0.093, Latin NT 0.095, Dante
0.125, Italian NT 0.147.

## Thresholds (`prelock_thresholds775.py` → `results/thresholds775.json`)
- **NEG_K** = max G_K over all 36 no-key design controls:
  - NEG_K1 = **−0.00022**;
  - NEG_K2 = **−0.00091**.
- **Scope:** plaintexts with O ≥ **O_S = 0.04**. This was chosen after the design: Mesue segment 1 (O 0.030) failed on K2.
- **POS_K** = min G_K over design ciphers with true key K, one spelling per unit and context, and O ≥ O_S:
  - POS_K1 = 0.00684;
  - POS_K2 = 0.00911.
- **τ_K** = (NEG_K + POS_K) / 2:
  - τ_K1 = **0.00331**;
  - τ_K2 = **0.00410**.

**The call on each arm K (K1 and K2 separately):**

| Call | Condition |
|---|---|
| **PRESENT** | G_K ≥ τ_K and p_G ≤ 0.005 (two arms, 0.01 family-wise) |
| **NONE** | G_K ≤ NEG_K, or p_G > 0.05 |
| **INDETERMINATE** | otherwise |

## Certification (`prelock_cert775.py`; set and criteria fixed before running; segments disjoint from the design)
**Set:**
- **One spelling per unit and context:**
  - true key K1: German NT 1; Spanish NT 2 and 4; English NT 3; Turkish NT 1; Mesue 2 and 3; SISMEL 1; Rupescissa 0;
    Italian NT 3;
  - true key K2: German NT 2; Italian NT 2; Mesue 4; SISMEL 2; Turkish NT 3; English NT 4.
- **Two spellings:** K1 English NT 2; K2 Spanish NT 3; K1 Mesue 5.
- **Twins:** K1 German NT 1; K2 Italian NT 2; K1 Mesue 2.
- **Plain codes:** Spanish NT 2; Mesue 3.
- **No-message runs (fresh seeds):** habit3 ×5, habit3b ×5, section-fitted habit3 ×3 and habit3b ×3, habit2 ×2, M1 ×2.

**Criteria:**

| Criterion | Requirement |
|---|---|
| R1 | every one-spelling keyed cipher with O ≥ 0.04 is PRESENT on its true key's arm |
| R2 | no two-spelling keyed cipher with O ≥ 0.04 is NONE on its true key's arm |
| R3 | no no-message run, twin or plain code is PRESENT on either arm, and at most 2 are INDETERMINATE |

PASS = R1, R2 and R3. A FAIL means redesign, with no re-tuning on these segments.

**Result:** *(filled in after the run)*

## Declared prior knowledge and exposure
- **B's facts relied on:**
  - boundary coupling (C1212/C1563, 0.22–0.26 bits shuffle-corrected at the glyph level);
  - word-ending routing (C2082);
  - token order near shuffle (C2085);
  - no recurring 5-token phrase (C2091).
- **B supplied:**
  - its skeleton (lines, lengths, blockers, sections, folios);
  - its paragraph-first-line flags (layout positions);
  - its within-line continuation lists per ending (adjacent pairs), used to make the positive controls' alphabets
    B-like;
  - the adjacent-token transitions, line-initial distribution and line-quintile unigrams of the habit generators
    (PHASE_768/774 precedent).
- **Not computed on B before the lock:** rank decoding, S, G, or any statistic of B's token order beyond adjacent
  pairs.
- **A point that could lower the leak concern.** Decoding is invariant to the choice of bijective alphabet. The B-like
  lists only make the controls' key sequences behave like B's; they cannot encode B's outcome.

## What each outcome means
**NONE on both arms.** B shows no key gain: re-labelling tokens by rank within the previous ending reveals no more order
than global labels do, as with every no-message model, twin and plain code tested.

It excludes a context-keyed substitution whose key is the previous token's last one or two glyph units, with one
spelling per unit and context, of any plaintext with O ≥ 0.04 (the tested recipe, alchemy and verse texts and New
Testaments). It rests on the design runs and the certification.

It does not exclude:
- keys defined otherwise (line position, the previous class, an external key sequence);
- more than one spelling per unit and context (two spellings were detected in the design for Latin recipes and NT, but
  this is not certified broadly);
- letter-level keyed ciphers (not tested);
- plaintexts with O < 0.04 (lists, low-order pharmacy segments);
- no-message processes.

It is not evidence of meaninglessness.

**PRESENT on an arm.** B's tokens, re-labelled by frequency rank within the previous token's ending, carry more
consecutive-order information than global labels do. No no-message run, twin or plain code showed that.
- It is consistent with a context-keyed cipher, or with another process in which the previous ending selects among
  interchangeable forms of shared underlying choices. Second-order no-message habits were not modelled.
- Any cipher reading is echo-class and needs an external test or the human's sign-off.
- A PRESENT would justify a follow-up phase that tries to align B's decoded rank stream with plaintext frequency
  profiles.

**INDETERMINATE.** Phase record only.

## Registry consequences (per arm)
| Outcome | Consequence |
|---|---|
| NONE on both arms | A Tier-2 negative-knowledge row with the scope above |
| PRESENT on an arm | A Tier-2 measurement row (the key gain, the arm and the controls' range); the interpretation is Tier 3 pending an external test |
| Otherwise | Phase record |
| Always | A methods row: rank decoding as a key-removal test, with its power map |

## Procedure
1. **Commit** this draft, the scripts and the design results.
2. **Run the certification** and write its result here.
3. **Lean-expert lock audit** and confirmation pass.
4. **`run775.py --checksums`**, commit, and tag `phase775-lock`.
5. **`run775.py`:**
   - verifies the tag, a clean `scripts/`, no untracked files and the input checksums;
   - logs versions;
   - runs B once (1,000 permutations);
   - commits the raw result before the write-up.
6. **The dry run** (`run775.py --dry`: a K1-keyed cipher of Latin NT segment 5, and habit3) runs before the lock.

## Caveats
- **O_S was chosen after the design runs** (see Thresholds). The certification tests it on disjoint segments.
- **Only first-order no-message models are in the negatives.** A no-message process with rank-level second-order habits
  could in principle produce a positive key gain.
- **The key gain is a lag-1 statistic on the top 20 ranks.** Plaintexts whose order lives in rare words are weakly seen.
- **The alphabets are bijective per context.** Homophony within a context dilutes the gain (tested at two spellings).
