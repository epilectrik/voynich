# Phase 578: EVENT-LOCAL CLOSURE ADJUDICATOR

**Status:** COMPLETE
**Phase:** 578
**Constraints:** C1659-C1662
**Depends on:** Phase 576 (regime admission gate), Phase 574 (event bands), Phase 572 (apparatus)

## Purpose

Replace Phase 576's line-level morphological classifier with an event-level execution+anatomy classifier. Phase 577 falsified line-level strength as the missing precision variable (21.6% surrogate agreement). The expert diagnosis: closure legitimacy is event-local, not line-local. The key discriminator is burden resolution — whether the CLOSE event actually reduced max(|C-0.5|, |X-0.5|) — combined with event-level packet strength signals from Phase 574.

## Architecture

- **4 event classes:** AUTHENTIC_RESOLVER, PARTIAL_RESOLVER, NONRESOLVING_COUNTERFEIT, INERT_PSEUDO
- **Primary discriminator:** burden_frac_resolved (execution-derived, NOT Y_gain)
- **Secondary filter:** n_strong_signals >= 1 for AUTHENTIC (event-level, not line-level surrogates)
- **Gate table:** (event_class, burden_key, cts_band) → (admit, credit) — 24 entries
- **Apparatus:** Same ClosureAdmissionApparatus (Phase 576) — only lookup data and gate table change
- **5 configs:** LINE_CLASS_CONTROL, EVENT_CLASS_FULL, EVENT_CLASS_BINARY, BURDEN_RESOLVED_ONLY, CREDIT_ONLY_EVENT
- **Event classes are cached event-legitimacy priors** keyed by line_key (positional, M4f-invariant)

## Scripts

| Script | Purpose | Runtime |
|--------|---------|---------|
| `t0_event_local_classification.py` | Event feature extraction + burden-resolution classification | 0.08s |
| `t1_event_local_apparatus.py` | Apparatus verification with event classes | 0.3s |
| `t2_event_local_simulation.py` | Full simulation (5 configs x 76 folios x 6 runs) | 53.1s |
| `t3_event_local_anatomy.py` | Gate anatomy + decisive test (C1660) | 0.1s |
| `t4_event_local_landscape.py` | Post-gate landscape + migration | 0.0s |
| `t5_event_local_synthesis.py` | Integration + C1659-C1662 | 0.0s |

## Constraints

| ID | Subject | Verdict |
|----|---------|---------|
| C1659 | Event-Local Feature Coverage | COVERAGE_VALIDATED |
| C1660 | Event Legitimacy Gating (decisive) | EVENT_GATING_REJECTED |
| C1661 | Burden Resolution Discriminator | DISCRIMINATOR_WEAK |
| C1662 | Landscape Migration | MIGRATION_ABSENT |
