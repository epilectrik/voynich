# Phase 733 — Class-Layer 5-gram Null: C2023 demoted, macro-automaton (C976-C978) vindicated

**Status:** COMPLETE (2026-05-28)
**Stakes:** load-bearing. C2023 grounds the class-layer; never 5-gram tested. Per PHASE_729 doctrine, shuffle-survivors (C1727, C645) have failed the sharper null.

---

## Outcome (one line)

C2023's **first-order scalar class-MI fails** the 5-gram null (it's morphology-reproducible) → **demote Tier 2→3**. But the **macro-state eigenstructure (C976-C978) SURVIVES** at the sharpest null it has ever faced → **vindicated**. The cascade STOPS at C2023. Tier 0 and the 49-class partition untouched.

---

## The chain of results (each control caught the previous confound)

### 1. Naive 5-gram test — FALSE POSITIVE
Real I(class;prev)=0.264 vs 5-gram synth I=0.221, z=+3.83, p=0.000. Looked like clean survival. **Artifact:** the synth has lower class diversity → lower raw MI AND lower own-shuffle floor. Comparing raw MIs measured composition-fidelity, not sequential structure.

### 2. Per-synth-own-shuffle control (the rigorous metric) — C2023 FAILS
Each synth's excess over its OWN shuffle null:
- BRIDGE: real excess +0.0485 vs synth +0.0421, z=+0.65, **p=0.21**
- BREAK-BIGRAM: real +0.1492 vs synth +0.1372, z=+0.76, **p=0.19**
- Coverage matched (synth unmapped 0.390 vs real 0.375), sanity reproduced (shuffle z +3.81 vs C2023's +3.91).

→ The first-order scalar class-MI excess IS reproduced by the 5-gram. **C2023 fails the null** — joins C1727/C645 as a shuffle-survivor that fails 5-gram.

### 3. Partition-ARI topology test — CONFOUNDED (uninformative)
Ran C976's constraint-preserving merge on 5-gram synth corpora, ARI vs canonical 6-state partition. 5-gram ARI 0.762, all 50 → 6 states. **But floor control:** within-line shuffle through the same merge → ARI 0.804; uniform-random matrix → 0.669; real → 0.937. The merge's hardcoded role-integrity + 18 depleted-pair constraints **force a 6-state ARI-0.67-0.80 partition even for structureless nulls.** Partition-ARI is role-constraint-dominated → can't discriminate. (Signal that survives the confound: 5-gram 0.762 sits BELOW shuffle floor 0.804, far below real 0.937 — pointing toward survival, but the metric is too contaminated to lean on.)

### 4. Spectral λ2 test — CLEAN, decisive: macro-automaton SURVIVES
λ2 of the raw 49×49 transition matrix (macro-state structure; bypasses the merge's role constraints entirely):
- REAL λ2 = 0.2063, λ3 = 0.1341
- 5-gram synth λ2 = 0.1194 ± 0.017, λ3 = 0.0765
- Shuffle floor λ2 = 0.1176 ± 0.009, λ3 = 0.0746
- 5-gram is **2% of the way** from shuffle floor to real.

→ The 5-gram reproduces NOTHING of the macro-state eigenstructure beyond the line-composition floor. Real λ2 stands far above. **Macro-automaton eigenstructure is above-Markov. SURVIVES.**

### 5. λ2 excess symmetry control — audit-proof
Per-synth-own-shuffle λ2 excess (same metric construction as test 2, for symmetry):
- REAL λ2 own-shuffle excess +0.0873
- 5-gram synth excess +0.0517 ± 0.0142, **z=+2.51, p=0.000**

→ Real λ2 excess significantly exceeds 5-gram (p=0.000) under the SAME metric where scalar-MI was reproduced (p=0.21). Clean, symmetric, decisive. (The synth reproduces ~60% of the λ2 excess — partly morphology-derivable — but the remaining ~40% is genuinely above-Markov, p=0.000.)

---

## The reconciliation: scalar MI reproduced, eigenstructure not

Two functionals of the same transition matrix, opposite verdicts, fully coherent (expert-confirmed):
- **Scalar I(class;prev)** = aggregate one-step predictability, dominated by high-mass LOCAL control bigrams (the qo→ch/sh-type transitions that SURVIVED 5-gram null in PHASE_731 at z=5.79). The 5-gram reproduces those, hence reproduces the scalar MI.
- **λ2** = global slow-mixing macro-state block structure. The 5-gram has no mechanism to reproduce which-classes-form-slow-mixing-communities (a relational pattern across many cells, not in any local n-gram window).

It is mathematically expected that a model can match the high-mass joint distribution (→ matched MI) while flattening the slow-mixing block structure (→ collapsed λ2). λ2 is the more sensitive, more discriminating measure of genuine macro-organization.

**Three-axis decomposition of class-sequential structure (the positive synthesis):**
1. **Local control bigrams** (PHASE_731 survivors) — REAL above-Markov.
2. **Macro-state eigenstructure** (λ2) — REAL above-Markov.
3. **Aggregate scalar first-order class-MI** (C2023) — the floor-dominated MIDDLE layer, morphology-reproducible.

---

## Dispositions

| Constraint | Verdict |
|---|---|
| **C2023** | DEMOTE Tier 2→3. Scalar first-order class-MI is 5-gram-reproducible (per-synth p=0.21). Shuffle finding preserved (above composition); not above local char-stats at scalar-MI level. Naive 5-gram FP documented as composition-fidelity artifact. |
| **C2061** (new, Tier 2) | Macro-state eigenstructure (raw-49 λ2) survives 5-gram null: real λ2=0.206, own-shuffle excess +0.087 vs 5-gram +0.052, p=0.000. Vindicates C976-C978 at the eigenstructure level. **Scoped to the raw-49 class operator — NOT a re-derivation of C978's 6-state 0.894 spectral gap (different operator).** |
| **C2062** (new, Tier 2) | Three-axis decomposition: local control bigrams + macro-state eigenstructure are real above-Markov; aggregate scalar first-order class-MI is the floor-dominated middle layer (morphology-reproducible). |
| **C976-C978** | SURVIVE / strengthened (via C2061). Faced the sharpest null available, passed at eigenstructure level. |
| **C1025 (M2)** | Scope-flag: M2's scalar/marginal generative metrics are partly 5-gram-floor (echoes C1025's own M0-passes-11/15); its topological metrics real. No demotion. |
| **C121/C124** (49-class partition) | UNTOUCHED — test consumed the partition as input. |
| **Tier 0** | UNTOUCHED. |

---

## Methodology lessons

- **Per-synth-own-shuffle (own-baseline) is mandatory** when comparing a structured metric across corpora with different composition. Raw real-vs-synth comparison conflates composition-fidelity with the structure under test. The naive z=+3.83 was a textbook composition-fidelity false positive.
- **Beware metrics computed through a constraint-laden algorithm** (the partition-ARI through run_merge): hardcoded constraints can dominate, making even structureless nulls score high. Always floor-control with shuffle + random through the same pipeline. Prefer a metric that bypasses the algorithm (λ2 of the raw matrix).
- **Scalar aggregate ≠ eigenstructure.** A 5-gram can reproduce the scalar one-step MI while failing the macro-state eigenstructure. Test the eigenstructure (λ2) directly for macro-organization claims.
- **Chained controls converged** — naive FP → C2023 fails → ARI confound → λ2 survival → symmetry confirm. Each control caught the previous layer's artifact.

---

## Scripts / results

- `scripts/_class_layer_5gram_null.py` — naive + per-synth (tests 1-2); `results/class_layer_5gram_null.json`
- `scripts/_middle_layer_control.py` — MIDDLE-layer 5-gram control; `results/middle_layer_control.json`
- `scripts/_controls_v2.py` — per-synth-own-shuffle excess (the rigorous C2023 metric); `results/controls_v2.json`
- `scripts/_topology_test.py` — partition-ARI through C976 merge; `results/topology_test.json`
- `scripts/_topology_floor_control.py` — shuffle + random floors (showed ARI confound); `results/topology_floor_control.json`
- `scripts/_spectral_topology_test.py` — λ2 clean topology test; `results/spectral_topology_test.json`
- `scripts/_lambda2_excess_symmetry.py` — per-synth-own-shuffle λ2 excess (audit-proof); `results/lambda2_excess_symmetry.json`

## Cross-reference

- C2023 (subject), C976-C978/C1010 (macro-automaton, vindicated), C1025 (M2, scope-flag), C2055 (5-gram surface-stat reproduction), C2056 (correction lanes survive), C549/C562 (PHASE_731 local-bigram survivors), C1727/C645 (prior shuffle-survivors that failed 5-gram — C2023 now joins on the scalar-MI axis).
