# Phase 649: O-Prefix Validation

**Status:** COMPLETE
**Date:** 2026-04-25
**Constraints registered:** C1963 (Tier 2), C1964 (Tier 2). Refinement note on C929. Thermal-mass hypothesis NOT registered (Tier 4 directional, awaits expansion).

---

## Question

Phase 648 registered the 4-axis o-prefix runtime channel taxonomy (C1962, Tier 3) and the fire-side / vessel-side paragraph-level partition (C1961, Tier 2) as within-sample findings. Phase 649 runs eight follow-up tests to either confirm the architecture, falsify it, or refine its shape. Specifically:

1. Are the four o-prefixes carrying distinct content (T1) or are they allomorphs?
2. Does the predicted within-line control loop exist (T2)? Does mode-stratification recover it (T3)?
3. Where do channel transitions actually happen (T4)?
4. Does the qo→ok ordering encode physical thermal-mass lag (T5/T6/T7)?
5. Is the qo→ok ordering specific or part of a broader generic pattern (T8)?

---

## Method

### Scripts (executed in order)

1. `s1_middle_pool_comparison.py` — JS divergence + Jaccard on MIDDLE distributions per o-prefix
2. `s2_within_paragraph_sequencing.py` — within-line bigram enrichment for predicted control loop
3. `s3_mode_stratified_sequencing.py` — re-run of s2 stratified by Mode A vs Mode B
4. `s4_channel_run_analysis.py` — channel-run lengths + transition locations + first-mention ordering
5. `s5_thermal_mass_lag.py` — qo→ok token-distance vs vessel thermal tier
6. `s6_thermal_mass_multigrain.py` — multi-granularity thermal test (line-distance, iteration density, Mode B fraction)
7. `s7_mode_b_thermal_full.py` — Mode B fraction across all matched paragraphs vs thermal tier
8. `s8_prefix_ordering_generalization.py` — first-mention ordering for ALL prefix pairs (Test A, crazy-expert's discriminator)

---

## Findings summary

### Finding 1: 4-axis allomorph hypothesis FALSIFIED (T1)

JS divergence on MIDDLE distributions:
- ok ↔ ot: 0.049 (sister pair, near-identical vocabulary; matches C1304)
- All other pairs: 0.34-0.44 (clearly distinct channels)
- Position-bin stratification (early/mid/late): pattern stable

Jaccard top-20: ok-ot = 0.90 (sister); ol-or = 0.38 (most distinct).

**The 4 prefixes carry distinct content. The allomorph hypothesis is falsified.** ok-ot sister-pair structure preserved (C1304); ol and or are independently distinct.

### Finding 2: Within-line control loop NOT supported (T2/T3)

Predicted topology (qo→ol→ok→ot→ch/sh→qo): 2/12 strict-threshold hits, permutation p=0.020 (marginal).

Hits: sh→qo +0.62 (decision gate, predicted), ch→sh −0.59 (mode switch suppressed, predicted).
Misses: qo→o-prefix transitions all flat (~0); ol→ok and ol→ot flat.
Self-loops enriched: ot→ot +1.01, or→or +1.05, ol→ol +0.59, ok→ok +0.50 — relative enrichment, not absolute persistence.

Mode-stratified (T3): Mode A 3/12 hits, Mode B 2/12 hits. **Mode A/B and the o-prefix channels are parallel architectural axes** — mode does not recover the control loop. sh→qo actually stronger in Mode B (+0.78) than Mode A (+0.55).

### Finding 3: Channel transitions are within-line, not at line-breaks (T4)

Surprising result: 85.3% of prefix transitions occur WITHIN a line, not at line breaks. The original "line-as-statement" hypothesis is falsified.

**Run-length distribution (prefix-level):**
- Mean: 1.27 (median: 1, 80.8% singletons, max: 10)
- Channels INTERLEAVE rapidly within lines

**Run-length distribution (block-level fire/vessel):**
- Mean: 2.39 (50.3% singletons, 11.7% reach length 5, 2.4% reach length 10, max: 50)

**Paragraph purity:**
- Prefix-level: mean 37.3% (very mixed)
- Block-level: mean 69.6%, **46% of paragraphs >70% block-pure** (independent confirmation of C1961)

The architecture is **token-scoped at prefix level, block-scoped at fire/vessel level**. Lines are not channel-coherent units.

### Finding 4: qo as paragraph operational opener (T8)

Discriminating test (per crazy-expert): is qo→ok specific or generic?

| Pair | A-first % | n |
|---|---|---|
| qo → ok | **72.9%** | 391 |
| qo → ot | **73.6%** | 394 |
| qo → ol | **80.5%** | 343 |
| qo → or | **84.7%** | 209 |
| Mean | 77.9% | (spread 11.8pp) |

**qo→ok is NOT specific.** qo precedes every o-prefix at 73-85%. The pattern is **qo as paragraph operational opener**, not pair-specific encoding.

Sister pair symmetry confirmed:
- ok ↔ ot: 48.5% / 51.5% (sister pair, ~50/50)
- ol ↔ ot: 45.3% / 54.7% (sister pair, ~50/50)

ch/sh asymmetry:
- sh → ch: 61.2% (passive monitor before active test)
- Refines C929 modality split with paragraph-scale temporal positioning

Surprising: qo precedes da in 80.0% of mixed paragraphs (heat-setup before material-introduction; predicted da-first reading falsified).

### Finding 5: Thermal-mass directional but underpowered (T5/T6/T7)

Three test framings of thermal-mass-mediated qo→ok lag:

| Test | Metric | rho | p | Direction |
|---|---|---|---|---|
| T5 | token-distance | -0.20 | 0.80 | null |
| T6 | Mode B fraction (qo-ok subset) | +0.20 | 0.26 | predicted |
| T7 | Mode B fraction (full paragraphs) | +0.20 | 0.19 | predicted |
| T7 Section B | Mode B fraction (bath section only) | +0.24 | 0.20 | predicted |
| T7 Section S | Mode B fraction (recipes section) | -0.23 | — | REVERSED |

**Thermal-mass hypothesis: directional support across 3 framings (rho ≈ +0.20), no test reaches p<0.05. Section S reversal flagged as likely section-confound shadow per crazy-expert.**

Pre-registration note: T5 was the pre-registered thermal-mass test → null. T6/T7 were post-hoc alternative operationalizations after T5 returned null. All results reported transparently (including the failed T5). Per memory feedback `feedback_scope_restrict_before_broad_test`: this is honest scope-refinement when mean rho is +0.4-0.5; here mean is +0.20, below the diagnostic threshold for that pattern. Reported as directional-only, not registered as constraint.

---

## Constraints registered

### C1963 (Tier 2): qo as paragraph operational opener

When qo and any o-prefix appear in the same paragraph, qo precedes the o-prefix in 77.9% of cases (mean across qo→{ok,ot,ol,or}, range 72.9-84.7%, n=209-394 per pair). Sister pairs (ok↔ot, ol↔ot) are first-mention symmetric (~50/50), confirming C1304. ch/sh asymmetric: sh precedes ch in 61.2% of mixed paragraphs (refines C929 modality split with temporal positioning). qo precedes da in 80% of paragraphs (heat-setup before material-introduction).

**Mechanism:** Grammatical precedence of operational opener, consistent with C1300 (qo near-pure THERMAL channel) + C1316 (O-PREFIX categorical scaffold) + C1394 (HEAD+MOD*+TERM atom architecture). Not pair-specific encoding (thermal-mass tested separately, directional but not significant).

### C1964 (Tier 2): o-Prefix within-line interleaving dominance

The 4-axis o-prefix architecture (C1962) is token-scoped at the prefix level, NOT line-scoped. Within lines, prefixes interleave rapidly: mean run length 1.27, median 1, 80.8% singletons, 85% of transitions occur within-line not at line breaks. Falsifies "channels persist within lines" intuition.

Block-level coherence (fire vs vessel) is moderate: mean run 2.39, 46% of paragraphs >70% block-pure, 13% >85%. Refines C1962 with explicit scope-restriction: prefix-channel architecture operates at *token* + *block* scopes, line is not an architectural unit for this dimension.

### Refinement note on C929 (no new constraint)

sh precedes ch in 61.2% of paragraphs where both appear (n=399). Refines C929 modality split (active vs passive monitoring) with a paragraph-scale temporal positioning fact: passive observation tends to come before active testing in mixed paragraphs. Effect-size below 1.5× threshold but direction is forced and operationally coherent.

### Reinforcement of C1961 (no new constraint)

T4 channel-run analysis independently confirms the C1961 fire/vessel paragraph-level partition: 46% of paragraphs >70% block-pure, 13% >85%, with block-level run lengths reaching 50 tokens. The block-level coherence is genuine and not an artifact of within-line transitions.

### Tier 4 hypothesis (NOT registered as constraint)

Thermal-mass-mediated encoding hypothesis. Mode B fraction directionally correlates with vessel-thermal-mass tier (rho ≈ +0.20 across three test framings on the same matched-recipe corpus, n=17-21, no test reaches p<0.05). Section B subset shows predicted direction (rho +0.24); Section S reverses (rho -0.23). Crazy-expert flagged Section S reversal as likely section-confound shadow rather than coherent scope-restriction. Awaits matched-corpus expansion + within-section test (orthogonal physically-grounded prediction such as e-depth signature per F-B-007) before any future registration.

---

## Compatibility check with existing constraints

- **C1304** (ok/ot sister pair, position-independent): T1 confirms (JS=0.049, Jaccard=0.90). C1963 sister-pair symmetry preserved.
- **C1316** (O-PREFIX categorical distinction, ok/ot/ol/or sequential): C1963 is paragraph-level extension; mentions trigram qo→ok→ot but doesn't cover the qo→{any o-prefix} paragraph-ordering generalization.
- **C1300** (qo near-pure THERMAL channel): C1963 anchors mechanistically — qo as opener is consistent with qo being the operational HEAD selector.
- **C1394** (HEAD+MOD*+TERM atom architecture): C1964 confirms tokens are atomic instruction primitives; within-line interleaving signature consistent with token-as-atom rather than channel-as-stream.
- **C929** (ch/sh sensory modality): C1963 sh-before-ch finding refines C929 with paragraph-scale temporal positioning.
- **C1561** (or→aiin directional bigram, 87.5%): direct precedent for Tier 2 directional pattern with mechanism not fully identified.
- **C1722-C1726** (line ordering is i.i.d.-like, position-invariant): C1964 within-line interleaving consistent with these — tokens are independent samples, not sequential.
- **C1398** (paragraphs as parallel subroutines / operational gradient): C1964 block-coherence is C1398 at PREFIX resolution.
- **C1808-C1812** (PREFIX as paragraph-level design parameter): C1963 paragraph-level ordering is consistent with PREFIX being the load-bearing scale.
- **C1959** (paragraph layout-order tracks recipe-phase order): C1963 is *intra-paragraph* prefix ordering, distinct from C1959's cross-paragraph layout-ordering. Different scales of "ordered execution."

---

## Pending future work

1. **Within-section thermal-mass test on Section B alone** — distinguish thermal-mass mechanism from section-confound shadow. Requires matched-corpus expansion (current Section B subset is n=13).
2. **Orthogonal thermal-mass prediction** — F-B-007 e-depth signature (per crazy-expert): if thermal-mass is real, high-thermal-mass folios should show e-depth enrichment (gentle-heat signature) AND qo run-length elevation. Independent prediction from same physical hypothesis.
3. **Test A extension** — apply prefix-pair ordering to ch/sh and da pairs; the surprising qo-before-da and sh-before-ch patterns may extend to other directional structures.
4. **Block-pure paragraph operational signatures** (per crazy-expert) — for the 46% of paragraphs >70% block-pure, classify by which channel dominates and test enrichment in HEAD MIDDLE families, REGIME, section. Validates block = operational mode.

---

## Script runtimes

All scripts complete in <60s on a standard workstation. Total phase wall-time ~2 hours.

---

## Files

- `scripts/` — 8 Python scripts (s1–s8)
- `results/`
  - `middle_pool_comparison.json`
  - `sequencing_test.json`
  - `mode_stratified.json`
  - `channel_runs.json`
  - `thermal_mass_lag.json`
  - `thermal_mass_multigrain.json`
  - `mode_b_thermal_full.json`
  - `prefix_ordering_generalization.json`
