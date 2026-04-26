# C1963: qo as Paragraph Operational Opener

**Tier:** 2
**Scope:** B, PREFIX, paragraph, ordering, qo, generic-precedence
**Phase:** PHASE_649_O_PREFIX_VALIDATION
**Date:** 2026-04-25
**Extends:** C1300 (qo near-pure THERMAL channel), C1316 (O-PREFIX categorical distinction), C1394 (HEAD+MOD*+TERM atom architecture)
**Refines:** C929 (ch/sh sensory modality — adds paragraph-scale temporal positioning)
**Relates to:** C1304 (ok/ot sister pair), C1561 (or→aiin directional bigram, 87.5%, precedent for Tier 2 directional pattern), C1808-C1812 (PREFIX as paragraph-level design parameter)

---

## Statement

When qo and any o-prefix (ok, ot, ol, or) appear in the same Currier B paragraph, **qo precedes the o-prefix in 77.9% of cases on average** (range 72.9-84.7%, n=209-394 per pair). The pattern is generic across qo-vs-o-prefix pairs, not pair-specific.

This positions **qo as the paragraph operational opener** for the o-prefix sequence: when an operation is described, the heat-application (qo) is mentioned first, with the operational-channel events (ok thermal-state, ot transfer, ol vessel-state, or outcome) following.

Sister-pair symmetry preserved (confirms C1304 sister structure).
ch/sh asymmetric: sh precedes ch in 61.2% of mixed paragraphs (refines C929 with paragraph-scale temporal positioning).

---

## Empirical evidence

### qo → o-prefix first-mention ordering

| Pair | A-first % | n |
|---|:---:|:---:|
| qo → ok | 72.9% | 391 |
| qo → ot | 73.6% | 394 |
| qo → ol | 80.5% | 343 |
| qo → or | 84.7% | 209 |
| **Mean** | **77.9%** | (spread 11.8pp) |

All four well above 50% null. Standard sign test against 50% null is significant for all four pairs (each p<0.001 by binomial; corpus-wide N too large for null to compete).

### Sister pair symmetry (predicted, confirms C1304)

| Pair | A-first % | n |
|---|:---:|:---:|
| ok → ot | 48.5% | 340 |
| ot → ok | 51.5% | 340 |
| ol → ot | 45.3% | 300 |
| ot → ol | 54.7% | 300 |

Sister pairs sit at ~50/50 — confirms C1304 (sister-pair structure has no first-mention preference) and confirms qo→o-prefix isn't an artifact of o-prefix internal ordering.

### ch/sh asymmetry (refines C929)

| Pair | A-first % | n |
|---|:---:|:---:|
| ch → sh | 38.8% | 399 |
| sh → ch | 61.2% | 399 |

sh (passive monitor) precedes ch (active test) in 61.2% of paragraphs where both appear. Operationally coherent: continuous watching comes first, then discrete event-checks. Effect-size below the 1.5× registration threshold but direction is forced and refines C929 modality split with a paragraph-scale temporal positioning fact.

### Surprising: qo precedes da (heat before material)

| Pair | A-first % | n |
|---|:---:|:---:|
| da → qo | 20.0% | 340 |
| qo → da | 80.0% | 340 |

qo precedes da in 80% of paragraphs where both appear — heat-setup is mentioned before material-introduction (per C1925 da = material introduction event). This is operationally coherent: "set the fire to gentle heat, then add the material to the vessel."

### Pattern across all tested pairs

Sister symmetry: ok-ot, ol-ot.
Strong ordering: qo→{ok,ot,ol,or} (77.9%), qo→da (80%), sh→ch (61%).
Strong reverse: ch→qo 33.1% (qo precedes ch in 67%; consistent with ch being paragraph-LATE per Phase 648).
ol → or: 68% (also strong; or is even more terminal-class than ol per C539).

---

## Mechanism

The 77.9% qo→o-prefix ordering is **grammatical precedence of the operational opener**, not pair-specific encoding:

- **C1300:** qo is the near-pure THERMAL channel — it carries the heat-application action that defines the operational frame.
- **C1316:** ok/ot/ol/or form a categorical scaffold (O-PREFIX distinction) — they're event-types that get tagged onto the operational frame qo establishes.
- **C1394:** HEAD+MOD*+TERM architecture — qo selects the operational HEAD, o-prefixes are categorical modifiers describing aspects of the operation.

**Thermal-mass-mediated lag was tested as an alternative mechanism** (Phase 649 T5/T6/T7) and found directionally supportive (rho ≈ +0.20 across three framings) but never significant (p ≥ 0.19). Section S reversal (rho -0.23) flagged as likely section-confound. Thermal-mass not registered; documented as Tier 4 hypothesis pending corpus expansion.

---

## Falsification

Would be falsified if:

1. The qo→o-prefix ordering rate drops to ≤55% under any well-powered stratification (we ran corpus-wide; section/regime stratification pending future test)
2. Sister-pair symmetry collapses (would falsify the "categorical scaffold" mechanism)
3. The ordering reverses on a non-trivial subset (recipe type, register, etc.) — directional consistency is the binding requirement

---

## Provenance

- `phases/PHASE_649_O_PREFIX_VALIDATION/scripts/s4_channel_run_analysis.py` (initial qo→ok 72.9% finding)
- `phases/PHASE_649_O_PREFIX_VALIDATION/scripts/s8_prefix_ordering_generalization.py` (Test A — generalization across all qo→o-prefix pairs and sister pairs)
- `phases/PHASE_649_O_PREFIX_VALIDATION/results/channel_runs.json`
- `phases/PHASE_649_O_PREFIX_VALIDATION/results/prefix_ordering_generalization.json`
