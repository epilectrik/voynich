# Phase 735 — C816 Cascade Audit (5-gram null on the CC-family)

**Status:** COMPLETE (2026-05-28)
**Scope:** the CC-family constraints flagged when C816 (CC positional ordering, "daiin initiates loop") demoted in PHASE_731: C558, C600, C817, C818, C819, C874.
**Method:** per-synth-own-shuffle excess (the PHASE_733 rigorous metric), 200 5-gram synth corpora, Bonferroni α=0.006 (8 metrics).

---

## Outcome

The C816 positional-ordering framework is **5-gram floor** (confirms C816). 3 demotions (C600, C817, C819), 1 partial (C558), 2 confirmed-floor (C816, C874 — already Tier 3). One honestly-flagged ambiguous bigram survivor (daiin→ch/sh) registered as measurement-only (C2064). Tier 0 and the 49-class system untouched.

## Results (per-synth-own-shuffle, p_emp over 200 synth)

| metric | constraint | real_exc | synth_exc | z | p_emp | verdict |
|--------|-----------|----------|-----------|----|----|--------|
| daiin→ch/sh-prefix | C600/C817 | +0.2272 | +0.1297 | 4.05 | 0.000 | above-Markov (measurement; mechanism ambiguous) |
| ol_medial | C819 | +0.0702 | +0.0324 | 2.57 | 0.000 | small-effect, NOT banked |
| daiin line-initial | C558/C819 | +0.1677 | +0.1296 | 1.69 | 0.040 | DEMOTE (fails Bonferroni; 77% Markov-reproduced) |
| ol→ch/sh-prefix | C817 | +0.1609 | +0.1488 | 0.60 | 0.250 | DEMOTE |
| ol_derived→qo-prefix | C600/C817 | +0.0787 | +0.0793 | -0.02 | 0.530 | DEMOTE (C817 itself called this NS) |
| daiin mean-pos | C874 | -0.0910 | -0.0662 | -1.34 | 0.900 | DEMOTE |
| ol mean-pos | C874 | +0.0112 | +0.0259 | -0.92 | 0.815 | DEMOTE |
| ol line-final | C558 | -0.0076 | +0.0042 | -0.70 | 0.735 | DEMOTE (already at-shuffle pre-test) |

## The daiin→CHSH survivor — measurement-only, mechanism ambiguous

daiin→ch/sh-prefix is genuinely above-5-gram (z=4.05). BUT two caveats make it measurement-only, NOT validation of C600/C817's routing claim:

1. **Denominator mismatch:** my metric is the UNCONDITIONAL daiin→ch/sh-prefix rate (47.9%), NOT C817's lane-conditional 90.8% (of next-tokens already in QO-or-CHSH, 90.8% CHSH). The lane-conditional magnitude is **untested** by this batch.
2. **Mechanism ambiguous (token-length artifact vs lane-routing):** daiin→CHSH survives (z=4.05) but the parallel ol→CHSH demotes (z=0.60), despite similar real rates. The daiin-survives/ol-demotes asymmetry is exactly what a token-length / char-signature artifact predicts: `daiin` is a long fixed token the 5-gram routes past poorly (same mechanism as qo→ch/sh in C549, +25pp residual per C2056); `ol` is short and char-reproducible → no residual. So the bigram is above-Markov, but the *reason* may be "char-5-gram can't route past long tokens," not "CC lane-routing is designed structure."

**Discriminating test (future work, pre-registered):** take a SHORT, char-reproducible source token that routes to CHSH at high rate; test whether ITS →CHSH transition survives. ≥2 short sources survive → general lane-attraction is real; <2 → char-signature artifact (and "→CHSH above-Markov" would be the trivial "long-token successor selection is hard for char-5-gram").

## Dispositions

| Constraint | Action |
|---|---|
| C816 (already Tier 3) | CONFIRMED floor — positional ordering is 5-gram-reproducible. No change. |
| C874 (already Tier 3) | CONFIRMED floor — both mean-pos metrics demote. No change. |
| C558 | Positional sub-claims (daiin-initial, ol-final) DEMOTE Tier 2→3 (ol-final was already at-shuffle). Non-positional "3 singletons / Class 10,11,12" structural-count claim NOT tested (wrong instrument), stands Tier 2. Annotate split. |
| C819 | DEMOTE Tier 2→3 (daiin-initial fails correction; ol_medial small-effect not banked). |
| C600 | DEMOTE Tier 2→3 (ol/ol_derived routing Markov-trivial; daiin bigram measurement-only/ambiguous, see C2064). |
| C817 | DEMOTE Tier 2→3 (lane-conditional 90.8% untested; ol/ol_derived trivial; daiin bigram ambiguous, see C2064). |
| C818 | UNTOUCHED Tier 2 — composition claim (Class 17 = ol-prefix tokens with kernel chars, 88% kernel-contact), not sequential/positional; 5-gram null is the wrong instrument; correctly excluded. |
| C2064 (NEW, Tier 2) | daiin→ch/sh bigram above-5-gram (z=4.05), measurement-only with mechanism-ambiguity + denominator caveats. |
| Tier 0, C121 (49-class system) | UNTOUCHED. |

## Synthesis

Reinforces C2062 (three-axis decomposition): the genuine above-Markov class-sequential signal is carried by specific control-transition bigrams (daiin→ch/sh, qo→ch/sh per C549, the C2056 correction-lane family), NOT by positional gradients. The C816 positional-ordering framework is floor. **Added discipline note:** the surviving bigram's mechanism is unresolved (lane-routing-design vs token-length char-signature artifact) — a real measurement, an ambiguous interpretation, and a weaker claim than the constraint (C817) it was filed under.

Expert prediction ("mostly demote") was correct. The one survivor is a bigram (measurement, ambiguous mechanism), not a positional-grammar survival.

## Methodology notes

- Multiple-comparison correction matters (8 metrics): daiin-initial flips from uncorrected-survive (p=0.040) to demote under Bonferroni (α=0.006). Apply correction in multi-metric batches.
- Token-length confound in transition-bigram 5-gram tests: long fixed source tokens (daiin, qo) survive partly because the char-5-gram routes past them poorly, independent of any designed routing. Distinguish with short-source controls before claiming a routing mechanism.
- Denominator discipline: unconditional prefix-transition rate ≠ lane-conditional rate. Test the claim's actual denominator before validating it.

## Scripts / results

- `scripts/_cascade_batch.py` — 8-metric per-synth-own-shuffle 5-gram batch; `results/cascade_batch.json`

## Cross-reference

C816 (subject, confirmed floor), C549/C2056 (parallel surviving transition bigrams), C2062 (three-axis decomposition), C558/C600/C817/C819/C874/C818 (cascade members), C121 (49-class system, untouched).
