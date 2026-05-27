# Phase 729: 5-gram Markov Null Battery

**Status:** COMPLETE
**Started:** 2026-05-26
**Completed:** 2026-05-26
**Goal:** Test the project's strongest architectural evidence against a character-level 5-gram Markov null trained on Currier B. Separate signal that survives Markov from signal that is a Markov artifact.

## Background

Two earlier session-day discoveries drove this phase:
1. Voynich's surface statistics (Zipf, TTR, hapax %, coverage curve, cell-fill 71% at 4-7 char range) are all reproducible from a character 5-gram trained on Currier B within sampling noise.
2. PHASE_691's existing markov_showdown.py result showed character 3-gram beats the 4.8M-parameter transformer on bpc (1.95 vs 2.79). Interpretation in the original phase mis-stated "shallow structure" — the n-gram actually *beats* the transformer by 30%.

These results forced a sharp question: which of the project's architectural-tier findings survive a 5-gram null, and which are local-character-statistic artifacts?

## Sub-phases

- **729.1** ✅ — Surface-statistics battery: TTR, hapax %, Zipf slope, coverage curves, cell-fill rates (4-7 char window), morpheme combinatorics. Result: 5-gram fully reproduces at order ≥ 4.
- **729.2** ✅ — C1727 line-ordering smoothness: real z = -3.83, synthetic z = -3.71. **Markov-trivial.**
- **729.3** ✅ — C2032 lag2/lag1 r21: real -4.21, synthetic +0.22. **Survives decisively.**
- **729.4** ✅ — Reverse-blind matches (f77r, f39r, f103v, f115r, f43v) against 5-gram null with per-target held-out training + negative control unmatched folio. Result: **f77r p=0.000, f39r p=0.002 survive; f103v p=0.227, f115r p=0.225 fail (tautological); f43v p=0.011 marginal.**
- **729.5** ✅ — Synthetic folio operational profiles: 100% in real Mahalanobis cloud with half variance. **Matcher generic at typical case (refines C2052).**
- **729.6** ✅ — C1314 narrow form (qo-k → ok-e): real +41.6%, synthetic +18.1%. **Partial survival (+23 pp residual).**
- **729.7** ✅ — Correction-lane family (qo-k → ok / ot / ch / sh / ok-e): 5 lanes, all 17-30 pp residual beyond Markov. **Strong survival; broadens C1314.**
- **729.8** ✅ — C645+C2045 post-hazard CHSH recovery: real +19.6 pp, synthetic +17.3 pp, residual +2.3 pp. **Markov-trivial despite previous within-folio shuffle null pass.**
- **729.9** ✅ — C2042 atom categorical signature: not 5-gram-testable (atom inventory preserved by construction). Verified count 13/20 OP-pure vs Latin 26%; zero-count non-OP asymmetry survives adversarial re-gloss.

## Aggregate findings

| Evidence axis | Verdict | Residual / metric |
|---------------|---------|-------------------|
| C2032 sequential structure (lag2/lag1) | SURVIVES decisively | real -4.21 vs synth +0.22 |
| Correction-lane family (5 transitions) | SURVIVES strongly | +17-30 pp across 5 lanes |
| f77r reverse-blind | SURVIVES | p_emp = 0.000 |
| f39r reverse-blind | SURVIVES | p_emp = 0.002 |
| C1314 narrow form (ok-e only) | PARTIAL | +23 pp residual |
| C2042 atom monocategorical | STANDS (not Markov-testable) | 13/20 OP, 0 non-OP, vs Latin 26%/74% |
| **C1727 line-ordering smoothness** | **Markov-trivial** | residual ~0 |
| **C645+C2045 post-hazard CHSH** | **Markov-trivial** | +2.3 pp residual |
| **f103v / f115r reverse-blind** | **Markov-trivial** | tautological predictions |
| **f43v reverse-blind** | **Marginal** | p_emp = 0.011 |
| **Folio operational profiles** | **Markov-trivial** | 100% in Markov cloud |

## Constraints registered

- **C2055** — 5-gram surface statistics match (Voynich is character-Markov at 5-gram order). Tier 2 measurement.
- **C2056** — Correction-lane family: post-heat polymorphic correction window. Tier 2; supersedes narrow C1314, references C1313/C645/C2045/C929.

## Constraint dispositions

- **C1727** — Tier 2 → Tier 3. Scope sharpened to "surface-statistic property, not evidence of intentional folio-level ordering."
- **C645+C2045** — Sharpen scope. Measurement preserved (post-hazard CHSH bias at lag+1 is real). Mechanism interpretation ("thermal damage control") retracted to Tier 4 SPECULATIVE.
- **C2052** — Add 100%-Mahalanobis-cloud finding as evidence; no separate constraint.
- **C1314** — Marked SUPERSEDED by C2056 correction-lane family; narrow form preserved as historical predecessor.
- **C929 / C1313** — Reference-linked to C2056 as predecessor measurements within the same architectural unit.
- **f77r catalog entry** — annotated "validated against 5-gram null, p_emp = 0.000."
- **f39r catalog entry** — annotated "validated against 5-gram null, p_emp = 0.002. **Non-distillation match** (pearl-making Ch.7-10M) — broadens framework from 'distillation grammar' to 'Pseudo-Lull workshop notation.'"
- **f103v + f115r catalog entries** — annotated "FAILED 5-gram null."
- **f43v** — annotated "MARGINAL on 5-gram null (p=0.011)."

## Methodology memory registered

- **feedback_5gram_markov_null_for_surface_patterns.md** — 5-gram null is the appropriate floor for surface-pattern claims (smoothness, bigram-rate predictions, character-level distributional facts). Complementary to within-folio shuffle null (catches folio-composition shadow); 5-gram null catches local-character-statistic shadow. Should be the **first** null run for any sequence-pattern claim going forward.

## Failure-mode taxonomy update

- **Pattern 8** added: "structural finding reproducible by appropriate-order local-statistics null." Demonstrated by C1727 and C645+C2045 demotions in this phase. Diagnostic: passing within-folio shuffle null at high significance does NOT guarantee survival of 5-gram null. The two tests answer different questions.

## Strength estimates after phase

- **Operational DSL / control notation generally:** 9/10 (correction-lane family + C2032 + C2042 form load-bearing trio)
- **Pseudo-Lull procedural notation:** 6/10 (f77r + f39r robust; bulk catalog suspect pending audit)
- **Distillation specifically:** 4-5/10 (correction-lane family supports thermal control; f39r non-distillation broadens framing; catalog generic at Latin-subdomain level)

## Outstanding audit work (flagged for future batches)

Crazy-expert estimates 15-25% of Tier 2 positional/sequential constraints could be Markov-trivial. Suspect zone: C547-C562 (line-level execution syntax), C597 (Class 23 boundary), C601 (hazard sub-group), C816 (CC positional ordering), and similar constraints validated only against within-folio or positional shuffle null. Estimated ~120 candidate constraints; expected 40-60% demotion rate under 5-gram null. Not run in this phase — flagged for routine audit batches.

## Files

- `scripts/_test1_c1727_null.py` — line-ordering smoothness 5-gram null
- `scripts/_test2_c2032_null.py` — lag2/lag1 5-gram null
- `scripts/_test3_reverse_blind.py` — reverse-blind matches 5-gram null + negative control
- `scripts/_test4_synthetic_folios.py` — folio profile Mahalanobis cloud test
- `scripts/_test5_c1314_null.py` — C1314 narrow (qo-k → ok-e) null
- `scripts/_test6_correction_lanes.py` — correction-lane family (5 lanes)
- `scripts/_test7_hazard_recovery.py` — C645+C2045 hazard recovery null
- `scripts/_test8_c2042_categorical.py` — C2042 verification + adversarial re-gloss
- `scripts/_trigram_test.py` — surface-statistics battery against 2/3/4/5-gram
- `scripts/_zipf_compare.py` — coverage curves and Zipf slopes vs reference corpora
- `scripts/_cell_fill_compare.py` — cell-fill rate vs NL / mensural / programming languages
- `scripts/_cell_fill_extended.py` — extended cell-fill including mensural notation
- `scripts/_morpheme_combinatorics.py` — slot grammar combinatorial fill
- `scripts/_hapax_check.py`, `_hapax_compare.py` — token-reuse / hapax baselines

## Cross-references

- **PHASE_691_VOYNICH_CHARLM** — markov_showdown.py result was the entry point. The 3-gram beats transformer finding had been mis-interpreted as "shallow structure" when it actually indicates n-gram decisively wins.
- **C2052** — refined by 729.5 (Mahalanobis cloud finding)
- **feedback_framework_as_null.md** — directly applicable to the demoted reverse-blind matches
- **feedback_specific_vs_tautological_predictions.md** — applied to f103v / f115r demotions
- **feedback_within_folio_shuffle_null_first.md** — now complemented by 5-gram null memory
