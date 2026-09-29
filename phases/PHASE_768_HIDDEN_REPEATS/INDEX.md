# PHASE_768 — Hidden repeats: does Currier B repeat token sequences beyond its local rules?

**Status:** DESIGN STAGE, not locked. **No statistic has been computed on Currier B.** B supplied only its skeleton and,
for the local-rule generators, its transition frequencies. B therefore stays blind for any later design.

**Draft pre-registration:** `PRE_REGISTRATION.md` (DRAFT v1). A lean-expert audit returned "lock with changes, but not
lockable as drafted" (edits E1–E13, plus the optional E14). The follow-up control runs it required show the draft
cannot be certified (below).

## Question (as asked by the human)
If a message sits underneath many spellings, its repeated phrases should still recur as repeated sequences of the
underlying units. Does B show such repeats beyond what its local rules produce?

## What the control calibration established (controls only)
1. **Exact-repeat tests cannot see a code with many spellings per unit.**
   - The Naibbe GV1 cipher of real plaintext is invisible at 4 tokens (X4 0.9–2.5, not significant).
   - At 3 tokens it sits at X3 2.8–2.95, barely above what B's own first-order local habits produce with no message
     (habit3, X3 2.15–2.34).
   - With the answer key, the hidden message is plain (X4 9.7–24.4).
   - Homophones of one plaintext unit look nothing alike ("e" is written *chedy, dar, ar, lchedy, chckhy*). The most
     informative visible feature, the MIDDLE, carries 3.6 of the 6.75 bits of the hidden unit
     (`results/prelock_naibbe_feature_probe.json`).
   - A 16-spelling word text shows no 4-gram repeats at all.
2. **Word-level messages with one spelling per word are detected, but how strongly depends on genre.** Under the joint
   null (single chain), X4 was:

   | Genre | Texts | X4 |
   |---|---|---|
   | NT translations | 5 | 37–135 |
   | Latin alchemy | Testamentum 98; Rupescissa 17 | 17–98 |
   | Italian verse | Dante | 22 |
   | Turkish NT | 1 | 236 |
   | Latin pharmacy and recipes | Mesue 9.9; Codicillus 8.8 | 8.8–9.9 |
   | No-message generators fitted to B | 13 runs | at most 3.56 |

   In raw counts, a Latin recipe text in B's skeleton has 39 repeated 4-token windows; B's first-order local model has
   about 12.
3. **B-like local rules fool single-rule nulls.**
   - A generator with class and junction rules and no message reaches X3 3.7–4.6 under the glyph-junction null (N5g)
     and 2.9–3.9 under the class null (N5c).
   - The joint null (N5j), which preserves both, does not converge at β = 2: four chains give R-hat 1.22, ESS 14, even
     after a 6,000-sweep burn-in.
   - At β = 1 it converges but is too loose: L1/edges 0.39, and the no-message generator reaches X4 7.65.
4. **The Bible-based threshold fails held-out certification.** T4 = 11.49 misses the two Latin pharmacy and recipe
   texts, the genre closest to the manuscript's own subject matter. The audit rules this out for re-tuning; it requires
   a redesign.

## Reading
- **The human's question is out of reach of exact-repeat statistics without the key.** Whether there is a message
  under many spellings cannot be decided this way.
- **What a redesigned test could decide:** whether B is a word-level code with few spellings per word (an
  exclusion-only test).
- **What the redesign would need:** a convergent null that still preserves B's local rules, certification on fresh
  held-out texts, and B-form codebooks.
- **Expected strength:** the separation for the most relevant genre (Latin recipes) is only about 2–3×. The expected
  outcome is also partly predictable from C1790 (no 4-grams in 3 or more folios).

## Files
- **Scripts:** `hr768.py`, `hr768v2.py`, `prelock_calibrate*.py`, `prelock_heldout_probe.py`,
  `prelock_convergence_pilot.py`, and `run_b.py` (written, never run).
- **Results:** `results/prelock_*`, `results/heldout_probe/`, `results/convergence_pilot/`.
