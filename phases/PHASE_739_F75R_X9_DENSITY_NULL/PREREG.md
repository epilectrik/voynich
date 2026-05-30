# PHASE 739 — Anchor Voynich-leg gate: C1889 4-run corpus-max density null — PRE-REGISTRATION v2

**Status:** PRE-REGISTERED v2 (REVISED after expert reconciliation; locked before run). Script NOT yet run.
**Date locked:** 2026-05-30
**Type:** Null-driven AUDIT of a Tier-2 constraint (C1889). Self-correcting → exempt from echo-gate; kill condition locked before the run.

## Why v2 (what the expert reconciliation changed)
v1 targeted **C1969** (the ≥9-qok-window) and claimed demoting it would void the 1/16,500. All three experts converged that this was **wrong on two counts**: (a) v1's within-folio self-shuffle tests *concentration* (→ C1965 idiom), not C1969's matched-pair specificity; (b) **the ≈1/16,500 = C1889 (4-identical-token run, 1/82) × C2034 (Catalan ×4+×9, 1/189)** — C1969 is a SEPARATE leg that does NOT enter the product. Therefore the anchor's only Voynich-internal, resamplable term is **C1889**, and the correct first gate tests C1889, not C1969.

## Question
Is f75r's 4-identical-consecutive-token run (C1889 — `qokedy ×4`, L13; the only Currier B folio of 82 reaching a ≥4 run) a genuine corpus-rare structural fact, or a **selection / order-statistic artifact** inflated by look-elsewhere across 82 folios? This is the Voynich leg of the 1/16,500 anchor.

## Why the off-books result is necessary but NOT sufficient
The off-books within-folio token-shuffle (this session: p=0.0049 identical-run / p=0.0003 qokedy-run) tests f75r against *its own* shuffle. It is **selected-on** — f75r was chosen as the corpus max-run folio — so it certifies "the 4-run is not a within-folio composition artifact of f75r" but does NOT pay the 82-folio look-elsewhere cost, i.e., does not establish the "1/82" corpus-rarity claim. The selection-safe **corpus-max** version (this phase) is required and registered.

## Statistic
Per Currier B folio (H-track, P-placement, exclude labels/uncertain — SAME filter as the off-books run): longest run of identical consecutive tokens (reading order, line-concatenated). **Corpus statistic = max over all 82 folios.** Observed: f75r = 4 (only folio at 4); 7/82 reach 3; corpus-max = 4.

## Null (corpus-max, type-frequency-preserving, selection-safe)
For each of N=10,000 iterations: within EACH folio, shuffle the token ORDER (a permutation — preserves the exact token-TYPE frequency multiset per folio, so reachability is automatic: a folio can only produce a 4-run if it has a type occurring ≥4×). Recompute each folio's longest identical run; take **corpus-max** that iteration. (Order-shuffle preserves type frequency exactly; a flat-count shuffle would understate the base rate and falsely inflate f75r — per lean/crazy-expert.)
`p_corpus` = fraction of iterations with corpus-max ≥ 4.

## Pre-registered thresholds (LOCKED)
- **KILL: p_corpus > 0.05** → a ≥4 run is reachable corpus-wide by chance → C1889's "1/82" is a selection / order-statistic artifact → **C1889 weakens** (demote/annotate) and the anchor's Voynich leg (the 1/82 in the 1/16,500) deflates.
- **HARDEN: p_corpus < 0.05** → a ≥4 run is corpus-rare beyond density → **C1889 hardens** with a registered selection-safe `p_corpus`; the 1/82 term is conservative-to-correct.
- Report also: per-folio observed longest run; under-null expected #folios reaching ≥4 and ≥3 (context); whether any folio other than f75r reaches ≥4 under the null.

## Scope — what this gate does and does NOT touch
- Tests ONLY **C1889** (the Voynich leg). A KILL deflates the 1/82 term of the 1/16,500; a HARDEN secures it.
- **C2034** (Catalan 1/189, external corpus census) — untouched by any Voynich null.
- **C1969** (≥9-window matched-pair) and **C1965** (cycle idiom) are SEPARATE legs tested by SEPARATE designs (see INDEX). A C1969/C1965 result NEVER deflates the anchor and is never to be reported as such.
- **Independence caveat (lean-expert):** the 1/16,500 multiplies C1889 × C2034 *assuming independence* (Voynich run-structure vs Catalan cardinality-phrasing). Plausible but asserted, not tested here. Out of scope for this gate; flagged as a known limitation of the product.

## Discipline
Null-driven demotion-capable → self-correcting, echo-gate-exempt; kill condition locked here before running. Token-order shuffle (composition control) is the correct null for a token-run/adjacency claim; the char-5-gram is the wrong instrument (C2066 window-blindness) and is not used. Complementary to the off-books within-folio test (which killed the composition-artifact alternative); this adds the selection-safe look-elsewhere correction.
