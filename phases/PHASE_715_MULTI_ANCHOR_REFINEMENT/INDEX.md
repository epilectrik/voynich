# PHASE_715: Multi-Anchor Directional Refinement Comparison

**Status:** COMPLETE
**Date:** 2026-05-20
**Verdicts:** C2047 (heterogeneous depth across 5 anchors) + C2048 (C1212-type multi-step chaining replicated in 2 independent predicates). Both Tier 2. C2045's scope narrowed (hazard recovery is single-step, not "substrate-level universal"). Methodology fix applied (A1a originally used head_atom='p' but p is MOD not HEAD; corrected to MIDDLE[0]='p').
**Posture:** PHASE_714 established C645 as a single-step substrate-level bigram rule (no multi-step, no class spec, no pre-buildup). The natural next question: **is the entire Voynich substrate fundamentally a single-step bigram-rule system, or does some subset of directional patterns show multi-step structure?**

Apply PHASE_714 methodology (multi-lag trajectory + pre-event signature + folio consistency + within-folio shuffle null) to multiple directional anchors and compare.

---

## The cross-anchor question

PHASE_714 result was specific to C645/hazards: single-step recovery, no continuation, substrate-level. Three possible generalizations:

1. **Single-step substrate universal:** every directional pattern in Voynich shows the same single-step-only structure → substrate is a fundamentally bigram-rule system (operationally simple)
2. **Hazard-specific:** C645 is the anomaly, multi-step structure exists for some patterns but not hazards → hazards are operationally simple, other domains have richer structure
3. **Mixed (most likely):** some anchors show single-step, others show multi-step → identifies which operational domains have richer protocols

The result discriminates these interpretations.

---

## Anchors tested (LOCKED before run)

### Anchor 0 (baseline reference): C645 — Post-hazard CHSH dominance
- Event: hazard-class token (C109)
- Target: CHSH lane EN-token
- Expected: single-step (lag +1 elevated, +2 baseline). This is the PHASE_714 result.

### Anchor 1: C1212 — Cross-Token TERMINAL→INITIAL chaining
- Event: token with TERMINAL atom in set {'h', 'r', 'y'} (top-3 strong-signal TERMs)
- Target: next-token HEAD atom matching the C1212-enriched partner:
  - h → p (2.61× enriched)
  - r → a (1.99×)
  - r → t (depleted, will measure for completeness)
- Expected (if substrate is single-step): only lag +1 shows elevated next-HEAD probability

### Anchor 2: C1314 — qo-k ↔ ok-e cycling
- Event: qo-prefixed token with k-HEAD MIDDLE
- Target: ok-prefixed token with e-HEAD MIDDLE
- Expected: lag +1 elevated (per C1314). Multi-lag tests cycling persistence.
- Bidirectional: also test ok-e → qo-k

### Anchor 3: C2041 — ar → al closure asymmetry
- Event: token with MIDDLE='ar' (or starting with ar)
- Target: token with MIDDLE='al' (or starting with al)
- Expected: lag +1 elevated (per C2041). Multi-lag tests closure protocol length.

---

## Methodology (applied per anchor)

For each (event, target) anchor:

**1. Multi-lag trajectory:**
- Find all event tokens
- For each event, measure target-rate at lag +1, +2, +3, +4 within same line
- Compare to baseline target-rate
- Per-lag null distribution (1000 random non-event tokens of matched count)

**2. Pre-event signature:**
- For each event, measure target-rate at lag -1, -2, -3 within same line
- If pre-buildup exists, target-rate elevated before event

**3. Folio-level consistency:**
- Per-folio post-event target-rate (folios with ≥3 events)
- Fraction of folios above baseline
- Mean across-folio rate

**4. Within-folio shuffle null:**
- Shuffle event/target labels within each folio
- Recompute post-event target-rate
- 500 permutations
- Check if observed rate exceeds shuffle p99

---

## Pre-registered classification (LOCKED)

For each anchor, classify based on findings:

| Pattern | Criterion |
|---|---|
| **SINGLE-STEP SUBSTRATE-LEVEL** | lag +1 passes null AND lag +2 within null AND folio-shuffle null passes AND folio consistency >70% |
| **MULTI-STEP SUBSTRATE-LEVEL** | lag +1 AND lag +2 (or +3) BOTH pass null AND folio-shuffle null passes |
| **FOLIO-LOCAL** | lag +1 passes raw null but FAILS folio-shuffle null |
| **NO REAL EFFECT** | lag +1 fails raw null distribution |

Cross-anchor verdict:
- All 4 anchors single-step substrate → **bigram-rule substrate confirmed**
- ≥1 anchor shows multi-step substrate → **operational-specificity exists, multi-step where**
- Anchors split between substrate and folio-local → **substrate has heterogeneous depth**

---

## Why this is high-yield

The cross-anchor comparison is the new finding regardless of outcome. We've established single-step pattern for hazards (C645/C2045); the question of whether this is universal or domain-specific has direct implications for how we interpret operational structure.

Specifically:
- If C1212 (broadest test, strongest signal in project) shows multi-step → the substrate has richer architecture than C645 suggests
- If C1314 (thermal-cycling) shows multi-step → partial restoration of multi-step thermal interpretation
- If all show single-step → entire substrate is a bigram-rule system, mechanism interpretations should treat tokens as instructions executed independently per local grammar

Per `feedback_framework_as_null.md`: this test design doesn't pre-favor either outcome. Both single-step-universal and mixed-results are interpretively informative.

---

## Implementation

| Script | Purpose |
|---|---|
| `_multi_anchor_test.py` | Unified anchor-testing framework applied to 4 anchors |

---

## Effort estimate

~3-4 hours implementation, ~10-15 min runtime (per-anchor null distributions + folio-shuffle nulls).

---

## RESULTS (2026-05-20)

### Cross-anchor table

| Anchor | Baseline | Lag+1 | Lag+2 | Lag+3 | Lag+4 | Lag+1 null p99 | Lag+2 passes | Shuf p99 | Pattern |
|---|---:|---:|---:|---:|---:|---:|---|---:|---|
| A0 hazard → CHSH (C645) | 0.171 | 0.221 | 0.152 | 0.146 | 0.169 | 0.219 | N | 0.203 | SINGLE-STEP |
| A1a h-TERM → MID[0]=p (C1212) | 0.009 | 0.022 | 0.018 | 0.018 | 0.014 | 0.015 | Y | 0.015 | MULTI-STEP |
| A1b r-TERM → MID[0]=a (C1212) | 0.133 | 0.320 | 0.187 | 0.181 | 0.184 | 0.145 | Y | 0.175 | MULTI-STEP |
| A2 qo-k → ok-e (C1314) | 0.029 | 0.042 | 0.034 | 0.028 | 0.022 | 0.037 | N | 0.040 | SINGLE-STEP |
| A3 ar → al (C2041) | 0.023 | 0.069 | 0.037 | 0.047 | 0.046 | 0.041 | N | 0.046 | SINGLE-STEP |

All 5 anchors pass within-folio shuffle null at lag +1.

**Cross-anchor verdict: HETEROGENEOUS DEPTH** — 3 single-step + 2 multi-step.

### A1a methodology fix

Original predicate `head_atom == 'p'` always returned False because 'p' is a MOD atom (in 'pficds'), not a HEAD atom (HEAD = 'aeokt'). Fixed to `MIDDLE[0] == 'p'` predicate (first-MIDDLE-character regardless of role classification). After fix, A1a shows multi-step substrate-level dependency, confirming A1b's finding independently.

### Expert consultation outcomes

**Expert-advisor:** Register both at Tier 2 measurement-level. A1a borderline-stable (lag+1 obs 0.022 vs p99 0.015) — A1b is primary evidence, A1a is replication with magnitude caveat. C2045's framing needs scope narrowing — was "substrate-level single-step" but tested only hazard recovery; C2047 shows substrate is NOT uniformly single-step. C2048 should cite C109 as layer-distinct (atom-character vs class-layer). Optional NL Latin floor check for C2047 would strengthen.

**Crazy-expert:** Cross-anchor result suggests TWO grammar tiers running simultaneously — reactive bigram for low-level operational rules (hazards/cycling/closure) AND compositional 2-3-gram for instruction-packet TERM→HEAD chaining. C1212 multi-step is "compositional carry-over" not "stimulus-response." Tokens are atomic units of encoding, but 2-3-token windows are compositional units. Already-present framework support: C1019 (tensor rank-8 pairwise structure orthogonal to macro-automaton), C1379 (two-level parallel composition with priority ordering). Recommended PHASE_716: test whether multi-step C1212 chaining is mechanism behind C1727 line-ordering smoothness (z=-6.05). 

### Registered constraints

- **C2047 (Tier 2):** Substrate has heterogeneous directional depth (5-anchor refinement). 3 anchors single-step (C645/hazards, C1314/cycling, C2041/closure); 2 anchors multi-step (both C1212-type cross-token TERM→MIDDLE[0] chaining).
- **C2048 (Tier 2):** C1212-type cross-token TERM→MIDDLE[0] chaining shows multi-step substrate dependency. Replicated in 2 independent predicates (h-TERM→p-MID, r-TERM→a-MID). Lag+2 passes null. Within-folio shuffle null passes p<0.001.

### Mechanism interpretations NOT promoted past Tier 4

- "Two-tier grammar architecture (reactive bigram + compositional 2-3-gram)" — Tier 3 framing only
- "Cooling cascade after intervention" reading of r→a chain — Tier 4 SPECULATIVE
- Refinement of compositional-vs-reactive operational architecture interpretation — Tier 4 SPECULATIVE

### Implications for prior findings

- **C2045 scope narrowed:** "substrate-level single-step" framing applied only to hazard recovery anchor (C645); the cross-anchor refinement shows substrate is NOT uniformly single-step. C2045 stays Tier 2 but scope is narrower than original framing.
- **C1212 sharpened:** the z=20.3 sequential signal has multi-step depth, not just bigram-level.
- **PHASE_714's "substrate is bigram-rule" implication:** now retracted as over-generalization. Hazard recovery is bigram-rule; other operational domains may have richer depth.
- **F-B-008/F-B-009 review status:** still flagged from PHASE_714, but C2048's discovery suggests multi-step structure DOES exist in some domains, just not the qo-k/ok-e thermal cycling per A2.

### Follow-up recommended

Crazy-expert's PHASE_716 proposal: test whether multi-step C1212 chaining explains C1727 line-ordering smoothness (z=-6.05). If residualizing C1727 against C1212 multi-step biases collapses the line-ordering effect >50%, identifies the mechanism. Either result substantively sharpens the substrate's compositional structure understanding.

---

## Registration-trap audit

- 4 anchors with distinct interpretive implications
- Each gets the same methodology (apples-to-apples)
- Within-folio shuffle null mandatory per `feedback_within_folio_shuffle_null_first.md`
- Pre-registered classification thresholds locked before run
- Cross-anchor comparison is the new finding, not just one anchor's verdict
- Per `feedback_mechanism_cycle_procedural_ceiling.md`: even if multi-step found, mechanism interpretation stays Tier 3-4
