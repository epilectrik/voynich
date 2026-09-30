# PHASE_775 — Is Currier B's word-boundary rule the key of a context-keyed cipher? (rank decoding)

**Status: COMPLETE.**
- **Lock:** `phase775-lock` (e27faf6), pre-registration v3.
- **Run:** one pass on B (1,000 EF permutations, about 1 minute at Idle priority). verify_lock ran first and passed.
- **Raw results committed before this write-up** (6e72b85).
- **Results check by the lean-expert:** calls correct, wording fixes applied.
- **Registered:** **C2093** (Tier 2, methods and measurement; no exclusion claim).

## Question (from the human's challenge: invent a new, text-only test)
B's strongest rule couples each word's beginning to the previous word's ending (C1212/C1563, C2082). If that rule were
the key of a cipher whose alphabet switches with the previous ending, re-labelling each word by its frequency rank among
the words that follow the same ending ("rank decoding", Friedman's alignment idea with the boundary rule as the key
schedule) would realign the hidden units.

## Result on Currier B (H track, P text; header-aware exact edge-frame null)
| Key | S (bits) | EF null | dS | z | p |
|---|---|---|---|---|---|
| K0 (global ranks) | 0.06117 | 0.05666 | +0.00451 | 2.9 | 0.004 |
| K1 (previous last glyph) | 0.02110 | 0.02111 | −0.00001 | 0.0 | 0.50 |
| K2 (previous last two glyphs) | 0.01825 | 0.01771 | +0.00054 | 0.5 | 0.31 |

- **ARM K1:** key gain G −0.00452 (p_G 0.994) → **not PRESENT**.
- **ARM K2:** G −0.00397 (p_G 0.980) → **not PRESENT**.
- Both lie within the no-key controls' range (−0.075 to +0.0007).
  - That range also contains keyed ciphers the test missed: Spanish NT 2 at −0.0043, and keyed B-like habit streams at
    −0.008 to +0.001.
  - So this is **no exclusion.**
- The lag-2 descriptive does not apply (no positive lag-1 gain).

**Post-hoc descriptives (not promised by the pre-registration).**
- **What stays fixed, and what is left.** Hold each position's first glyph, last two glyph units and zone fixed, within
  folio × line type. Neighbour dependence among B's 20 most frequent tokens is then small (+0.0045 bits, z 2.9, at K0
  resolution: top 20 ranks, the rest pooled). That is below the phase's B-fitted first-order generators (+0.007 to
  +0.021).
- **Within ending contexts it is at null** (dS_K1 −0.00001), below every no-message generator (+0.0005 to +0.008).
- **Hypothesis, untested.** The generators' larger values may come from pooled bigrams replaying folio-level
  co-occurrence as adjacency. The audit's folio-fitted habit3 (+0.007–0.008) points that way but still sits above B. A
  declared post-hoc rerun under a corpus-wide EF would test it.
- **Scope.** This does not contradict C549, C2056 or C2082, which were measured against nulls that do not fix glyph
  edges. It is consistent with C2081.

## What the test can and cannot see (power map)
- **Specificity:** no PRESENT in 98 no-key controls. These were 36 design runs, 25 certification runs, and the lock
  audit's 37 plants:
  - within-folio non-stationarity;
  - second-order habits;
  - folio-fitted habits;
  - boundary spelling with MIDDLE clustering.
- **Sensitivity: partial.**
  - Detected 8 of 12 held-out keyed natural-language ciphers.
  - It fails when contexts are dominated by the successors of particular preceding words; with B-like alphabets, the
    frequent units' tokens end in a few glyphs.
  - Missed 4 of 4 keyed B-like habit streams.
  - A keyed, line-clustered stream without word order was PRESENT in 2 of 15 audit runs.

## Design history (controls only)
1. **Prototype and design calibration** (`prelock_proto775.py`, `prelock_calib775.py`): every keyed cipher had a
   positive key gain, and every no-key control a negative one.
2. **Thresholds** (`prelock_thresholds775.py`): τ_K1 0.0033, τ_K2 0.0041, scope O ≥ 0.04.
3. **Certification on disjoint segments** (`prelock_cert775.py`, criteria fixed first) **failed R1.** v2 therefore made
   both arms one-sided, with no re-tuning.
4. **Lean-expert lock audit** (`scripts/audit/`, `results/audit/`, 3ada341): LOCKABLE WITH EDITS. It added 37 no-key
   plants, and none reached PRESENT. The edits went in as v3: wording, a lag-2 descriptive, counts and code fixes.

## Scripts
| Script | Role |
|---|---|
| `key775.py` | rank decoding, statistic, EF run |
| `gen775.py` | keyed ciphers in B's forms, line types, plaintext order index |
| `prelock_*.py` | calibration and certification |
| `run775.py` | the locked run |
