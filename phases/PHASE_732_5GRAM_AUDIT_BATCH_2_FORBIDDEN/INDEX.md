# Phase 732 — Forbidden-Pair Audit + Hazard-Class Provenance Correction

**Status:** COMPLETE (2026-05-28)
**Methodology:** PHASE_731 audit framework + near-zero rail + clustering + gloss-coherence
**Outcome:** Forbidden-pair audit confirmatory of C2023 (wrong layer). User-prompted follow-up uncovered the major finding: **the 5 hazard classes were imposed by keyword-matching, not discovered by clustering.** Registered C2060; revised C109; demoted C216; cleaned public docs. Tier 0 untouched.

---

## HEADLINE FINDING: the 5 hazard classes were imposed, not discovered (C2060)

What started as a routine 5-gram audit of the 17 forbidden transitions became a provenance investigation when the user asked whether the 5 hazard classes were derived from the forbidden transitions. Three independent checks + two empirical tests:

1. **Provenance (triple-confirmed):** `phase18_failure_typology.py` hardcodes 5 distillation-failure-mode classes + keyword lists (lines 61-87); the 17 transitions are sorted by keyword substring-match (lines 392-411). No clustering. The only clustering in the phase 15-20 chain produced 1 cluster (phase15a), not 5. Phase 16 had a different 12-mode scheme. C109's "Cluster analysis reveals 5 natural groupings" is **false about its method.**

2. **Clustering test (ran the clustering nobody ran):** atom-territory clustering of the 17 transitions. Silhouette-optimal k=8; k=3 (0.40) ≥ k=5 (0.37); natural-vs-imposed ARI=0.42. **5 is not data-preferred.** Only PHASE_ORDERING (n=7, within-dist 0.154) is a tight cluster. CONTAINMENT_TIMING barely cohesive. Two singletons. Cohesion z=−4.10 vs random — but NEAR-CIRCULAR (keywords encode atom intuitions), not evidence for 5.

3. **Gloss-coherence check:** ENERGY_OVERSHOOT ("scorching") CONTRADICTED — sole member `he→t` has no k-HEAD heat atom (`he`=watch.cool; cf C1448 k-HEAD immunity). RATE_MISMATCH/COMPOSITION_JUMP labels unsupported. PHASE_ORDERING supports only a generic sequencing reading.

**Disposition:** C2060 registered (Tier 2, the provenance+clustering measurement). C109 revised to existence-only. C216 demoted Tier 2→3. C110/C111/C112 kept (taxonomy-independent or = the one real cluster). C1528-C1533 untouched (the rigorous atom-grounded layer that survives). Tier 0 frozen conclusion untouched. Public docs (GUIDE.md, WHAT_WE_CLAIM.md, BCSC) corrected. New failure pattern #9: phantom-clustering.

Scripts: `scripts/_hazard_class_clustering.py`, `_hazard_glosses.py` (in repo root), `_within_class_test_v2.py`. Results: `results/hazard_class_clustering.json`.

---

## ORIGINAL BATCH 2 (forbidden-pair 5-gram audit)

**Status:** COMPLETE — confirmatory of C2023 (tested the MIDDLE/token layer, which C2023 already characterized as co-occurrence-only).
**Methodology:** PHASE_731 audit framework + near-zero rail
**Stakes (as originally framed):** C109 hazard topology — but the audit hit the MIDDLE layer, not the load-bearing 49-class projection.

---

## Motivation

The "17 forbidden transitions" (C109) are part of the Tier 0 frozen conclusion's grounding. Crazy-expert flagged this as the highest-stakes outstanding test:

> "PHASE_731 batch 2 should test C109/C627 forbidden pairs individually under 5-gram null. If forbidden pairs split into 'above-Markov' (designed prohibition) vs 'Markov-trivial' (character-statistical artifact), the hazard topology framework gets sharpened to the genuinely-designed subset."

This batch tests all 17 forbidden pairs individually.

---

## The 17 Forbidden Transitions (from `phases/15-20_kernel_grammar/phase18c_failure_taxonomy.json`)

| # | Class | Source | Target | src n | tgt n | Real bigram | Phantom? |
|---|---|---|---|---|---|---|---|
| 1 | PHASE_ORDERING | shey | aiin | 204 | 351 | 0 | NO (both real) |
| 2 | PHASE_ORDERING | shey | al | 204 | 186 | 0 | NO |
| 3 | PHASE_ORDERING | shey | c | 204 | 2 | 0 | Target rare |
| 4 | PHASE_ORDERING | dy | aiin | 109 | 351 | 0 | NO |
| 5 | PHASE_ORDERING | dy | chey | 109 | 250 | 0 | NO |
| 6 | PHASE_ORDERING | chey | chedy | 250 | 491 | 0 | NO |
| 7 | PHASE_ORDERING | chey | shedy | 250 | 416 | 0 | NO |
| 8 | COMPOSITION_JUMP | chedy | ee | 491 | 0 | 0 | PHANTOM target |
| 9 | COMPOSITION_JUMP | c | ee | 2 | 0 | 0 | PHANTOM target + rare source |
| 10 | COMPOSITION_JUMP | shedy | aiin | 416 | 351 | 0 | NO |
| 11 | COMPOSITION_JUMP | shedy | o | 416 | 29 | 0 | NO |
| 12 | CONTAINMENT_TIMING | chol | r | 99 | 39 | 0 | NO |
| 13 | CONTAINMENT_TIMING | l | chol | 34 | 99 | 0 | NO |
| 14 | CONTAINMENT_TIMING | or | dal | 250 | 130 | 0 | NO |
| 15 | CONTAINMENT_TIMING | he | or | 0 | 250 | 0 | PHANTOM source |
| 16 | RATE_MISMATCH | ar | dal | 248 | 130 | 0 | NO |
| 17 | ENERGY_OVERSHOOT | he | t | 0 | 3 | 0 | PHANTOM source |

**Important correction:** The HAZARD_CLASS_ATOMIZATION REPORT claimed 11 of 17 involve phantom MIDDLEs (shey, chey, chedy, shedy, chol). Direct corpus check shows those tokens DO occur (204, 250, 491, 416, 99 occurrences). The actual phantoms are `he` (0), `ee` (0), and rare `c` (2), `t` (3). Only 4 of 17 pairs involve phantoms in source or target.

All 17 have real bigram count = 0. The question: does 5-gram synth produce these bigrams at meaningful rates (genuine prohibitions above Markov) or near-zero (character-statistically inevitable)?

---

## Pre-Registered Audit Criteria (LOCKED)

### Methodology

- Same-corpus training (per PHASE_731 calibration outcome)
- 5-gram null, N_synth = 500 (rare-event)
- Match line/token structure of full Currier B

### Verdict structure (near-zero rail extended per expert recommendation)

For each of the 17 pairs:
- Compute real bigram rate (will be 0% for all 17 per pre-check)
- Compute synth bigram rate (mean across 500 synth corpora)
- Apply:

| Condition | Verdict |
|---|---|
| real == 0, synth_mean ≥ 0.01 AND p_emp < 0.05 | **SURVIVES STRONG** — designed prohibition above Markov |
| real == 0, 0.001 ≤ synth_mean < 0.01 AND p_emp < 0.05 | **SURVIVES Tier 2** — weak above-Markov prohibition |
| real == 0, synth_mean < 0.001 | **DEMOTE Tier 2 → Tier 3** — Markov-trivial (character statistics already enforce; prohibition not designed) |
| Phantom source or target | **PHANTOM ANNOTATION** — prohibition reduces to "construction prevents the source/target token"; not a transition-rule claim |

### Aggregation rule

C109's claim is the structural existence of 17 forbidden transitions. Disposition by sub-distribution:

- **All 17 SURVIVE** → C109 Tier 0 frozen status holds completely; "17 forbidden transitions" structural fact strengthened
- **Mostly SURVIVE (≥12/17)** → C109 holds; minor sharpening to "X of 17 are designed prohibitions; Y are character-statistical"
- **Split (5-11 SURVIVE)** → C109 narrows from "17 forbidden transitions" to "N designed forbidden transitions plus M character-statistically rare bigrams"; significant scope sharpening
- **Mostly DEMOTE (<5 SURVIVE)** → C109 reduces to a near-vacuous claim; hazard-topology framework needs major reframe; would propagate to C110-C112, C216 and potentially destabilize Section 0.B of INTERPRETATION_SUMMARY.md
- **0 SURVIVE** → catastrophic; C109 reduces to "0 occurrences in corpus, character-statistically reproducible" — equivalent to demotion to descriptive Tier 3 fact

C109 itself is Tier 0 FROZEN. Demoting Tier 0 is unprecedented in this project's methodology and would require additional discriminating evidence beyond a single 5-gram null. The conservative path: if mostly-demote, register as candidate-for-Tier-0-reframe pending independent corroboration.

---

## Predictions to verify (expert-elicited, pre-locked)

Crazy-expert prediction: SPLIT result. Some pairs (likely categorical exclusions with morphological basis, e.g., he→t kernel-to-transfer) survive as designed; others (positional bigrams with rare-token denominators) demote.

Expert-advisor prediction: heavily phantom-driven — pairs with very low source/target counts will produce small synth values regardless; will appear to DEMOTE on near-zero rail because synth also near zero. Specifically: pairs 3 (shey→c), 8 (chedy→ee), 9 (c→ee), 15 (he→or), 17 (he→t) likely DEMOTE on phantom grounds.

Pre-locked baseline: ≥6 of 17 SURVIVE (above the "vacuous" threshold).

---

## Scripts

- `scripts/_batch2_run.py` — Top-level: 17 pre-registered measurements + verdicts. Writes `results/batch2_dispositions.json`.

---

## Expert pre-audit fixes applied (2026-05-28)

Both expert-advisor and crazy-expert independently flagged six critical fixes:

1. **REFRAMED:** C109 is Tier 0 STRUCTURAL EXISTENCE claim ("17 forbidden transitions, all real-rate = 0"). The audit tests MECHANISM (above 5-gram floor or not), not the structural claim. Verdict labels updated to `ABOVE_MARKOV_SUPPRESSION_STRONG/WEAK` and `MARKOV_TRIVIAL` (not "designed prohibition" — test doesn't establish design intent).

2. **PHANTOM correction:** only 4 actual phantoms (pairs 8, 9, 15, 17 with `he`/`ee` count=0). HAZARD_CLASS_ATOMIZATION REPORT's claim of "11 of 17 involve phantom MIDDLEs" was MIDDLE-vs-class confusion; shey/chey/chedy/shedy/chol DO exist at 99-491 counts. Documented and corrected.

3. **N_SYNTH stratified by denominator:** 500 for well-sampled (both src and tgt ≥200); 1000 for medium (30-200); 2000 for rare (<30). Denominator-invariant statistical power.

4. **THRESHOLDS in expected-count terms:** `expected_bigrams_per_synth = synth_rate × src_n`. STRONG ≥3.0, WEAK 0.3-3.0, DEMOTE <0.3. Denominator-invariant.

5. **C627 secondary prediction LOCKED:** ≥7 of 13 testable pairs as ABOVE_MARKOV_SUPPRESSION matches C627's "circuit topology explains 9/12" framing.

6. **NEGATIVE CONTROL added:** 17 random non-forbidden frequency-matched bigrams with real_count > 0. Tests whether 5-gram reproduces non-forbidden bigrams at rates comparable to real (methodology calibration).

## Crazy-expert per-pair predictions (locked pre-audit)

| # | Pair | Prediction | Reason |
|---|---|---|---|
| 4 | dy→aiin | DEMOTE | dy-followed-by-aiin char sequence is high-prob in 5-gram |
| 5 | dy→chey | DEMOTE | y-terminal→space→c is reachable in 5-gram |
| 6 | chey→chedy | SURVIVE STRONG | both high-frequency; if 5-gram avoids = real prohibition |
| 7 | chey→shedy | SURVIVE STRONG | parallel argument |
| 10 | shedy→aiin | SURVIVE STRONG | both common; cleanest test |
| 11 | shedy→o | SURVIVE STRONG | depends on bare-o vs compound |
| 14 | or→dal | SURVIVE STRONG | r-terminal→d-initial routing |
| 16 | ar→dal | SURVIVE STRONG | parallel to 14 |
| 12 | chol→r | DEMOTE | rare denominator |
| 13 | l→chol | DEMOTE | rare denominator |
| 1-3 | shey→aiin/al/c | UNCERTAIN | depends on 5-gram's character handling |
| 8,9,15,17 | phantoms | PHANTOM_FLAG | construction-level, not transition |

Predicted distribution: 6 STRONG, 4 DEMOTE, 4 PHANTOM, 3 UNCERTAIN. Crazy-expert probability: 35% baseline holds / 45% mixed / 20% catastrophic. Most likely outcome: messy middle.

## Crazy-expert outcome impact assessment

- **Mostly-survive (≥12/17):** cleanest result in months; Tier 0 holds strongly; warrants new constraint registering above-Markov forbidden-pair status
- **Mostly-demote (10+/17):** Tier 0 frozen conclusion HOLDS (Tier 0 is about closed-loop control, not load-bearing on hazard topology specifically). Direct impact on C109 mechanism framing + C783, C997, C996 cascade. 20-40 downstream constraints flagged for re-audit. Significant documentary cost.

---

## Status

- [x] Forbidden-pair list extracted and cross-checked against corpus
- [x] Phantom-status correction documented
- [x] Pre-registration criteria locked
- [x] Audit script written
- [x] Expert pre-audit completed (both expert-advisor + crazy-expert)
- [x] Critical fixes applied (6 + negative control)
- [ ] Audit run
- [ ] Dispositions written
- [ ] CLAIMS/INDEX.md updated
- [ ] Tier 0 impact assessment
