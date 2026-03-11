# Phase 578: EVENT-LOCAL CLOSURE ADJUDICATOR

## Summary

Replaces Phase 576's line-level morphological classifier with an event-level execution+anatomy classifier. Phase 577 falsified line-level strength as the missing precision variable (21.6% surrogate agreement). The expert diagnosis: closure legitimacy is event-local, not line-local. The key discriminator is burden resolution — whether the CLOSE event actually reduced max(|C-0.5|, |X-0.5|) — combined with event-level packet strength signals from Phase 574.

**Best gate configuration:** LINE_CLASS_CONTROL
**SSI:** 63.5040
**A2 delta advantage:** 0.0635
**Strong-band preserved:** 58.7%

## Constraint Verdicts

| ID | Subject | Verdict |
|----|---------|---------  |
| C1659 | Event-Local Feature Coverage | COVERAGE_VALIDATED |
| C1660 | Event Legitimacy Gating (decisive) | EVENT_GATING_REJECTED |
| C1661 | Burden Resolution Discriminator | DISCRIMINATOR_WEAK |
| C1662 | Landscape Migration | MIGRATION_ABSENT |

## T0: Event-Local Classification

- Events classified: 463
- Total lines: 2323
- Classes populated: 3/4

### Class Distribution

| Class | Count | % |
|-------|-------|---|
| AUTHENTIC_RESOLVER | 128 | 27.6% |
| PARTIAL_RESOLVER | 174 | 37.6% |
| NONRESOLVING_COUNTERFEIT | 161 | 34.8% |
| INERT_PSEUDO | 0 | 0.0% |

### Burden Resolution Distribution

- Min: -3.4565, Max: 0.9960
- p25: 0.0, p50: 0.3588, p75: 0.6783

### Resolution Coherence

- **AUTHENTIC_RESOLVER**: 68.8% coherent (88/128)
- **PARTIAL_RESOLVER**: 65.5% coherent (114/174)
- **NONRESOLVING_COUNTERFEIT**: 7.5% coherent (12/161)

## T1: Apparatus Verification

- identity_check: PASS
- full_rejection_check: PASS
- no_strength_check: PASS
- strength_effect_check: FAIL
- credit_only_check: PASS
- burden_conditioning: PASS

## T2: Full Simulation

- Configurations: 5
- Total runs: 2280
- Elapsed: 53.09s

### Profile Summary (best: LINE_CLASS_CONTROL)

- **A1_BATH_REFLUX**: delta_adv=-0.0010, CCS1_red=3.8%, null_wins=0->0
- **A2_SEALED_RECIRCULATION**: delta_adv=0.0635, CCS1_red=66.2%, null_wins=7->2
- **A3_DISTILL_COLLECT**: delta_adv=0.0073, CCS1_red=30.9%, null_wins=1->0

## T3: Gate Anatomy + Decisive Test

### SSI per Config

| Config | SSI | A2 delta | Strong% | Null wins |
|--------|-----|----------|---------|-----------|
| LINE_CLASS_CONTROL | 63.5040 | 0.0635 | 58.7% | 2 |
| EVENT_CLASS_FULL | 0.0000 | -0.0185 | 64.8% | 8 |
| EVENT_CLASS_BINARY | 0.0000 | -0.0253 | 61.6% | 9 |
| BURDEN_RESOLVED_ONLY | 0.0000 | -0.0094 | 65.9% | 8 |
| CREDIT_ONLY_EVENT | 0.0000 | -0.0174 | 63.6% | 8 |

### C1660 Decisive Test: EVENT_GATING_REJECTED

- EVENT_CLASS_FULL beats LINE_CLASS_CONTROL: False
- Strong >= 80%: False
- Null wins <= LCC: False

### C1661 Burden-DYE Discriminator: DISCRIMINATOR_WEAK

- AUTHENTIC mean DYE_adv: 0.119078
- COUNTERFEIT mean DYE_adv: 0.098315
- Direction (AUTH > CF): True
- Cohen's d: 0.2669 (>= 0.3: False)

### Config Robustness

- Beat LINE_CLASS_CONTROL: 0/3
- Beat CREDIT_ONLY_EVENT: 1/3
- Weak guardrail safe: False
- Architecture robust: False

### Phase 576 Comparison

- Phase 576 best (AMB_PESSIMISTIC): A2 delta=0.0635
- Phase 578 best (LINE_CLASS_CONTROL): A2 delta=0.0635
- Improvement: +0.0000

## T4: Landscape + Migration

- A2 FORGIVING: 8 -> 8 (0.0% reduction)
- Migrating folios: 0
- New A1/A3 FORGIVING: 0

- Phase 576 A2 FORGIVING gated: 8
- Phase 578 A2 FORGIVING gated: 8

## Tier 3 Interpretation

> Tier 3 interpretation NOT frozen. Non-validated: C1660=EVENT_GATING_REJECTED, C1661=DISCRIMINATOR_WEAK, C1662=MIGRATION_ABSENT. Strong-band preservation=58.7% (target >=80%, Phase 576 baseline=58.7%). Further investigation needed.

*Generated: 2026-03-11T14:08:09.229987+00:00*
