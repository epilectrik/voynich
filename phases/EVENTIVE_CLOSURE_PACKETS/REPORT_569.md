# Phase 569: EVENTIVE CLOSURE PACKETS

## Verdict: EVENTIVE_CLOSURE_INSUFFICIENT

## Summary
Phase 569 tested whether segmenting closure lines by event type improves discrimination between the full model and null models. Building on Phase 568's shared metrics module (WCU, SLR, UEB, CCY, WCP, EWP), this phase introduced an event taxonomy (E_opaque, E_opaque_decisive, E_compound, E_armed, E_cts50, E_mcb, E_decisive) grounded in the opacity grammar (C1440-C1445) and tested whether eventive closure packets -- closure events filtered by type and qualified by demand context -- discriminate better than aggregate E_any.

The validation battery comprises P2 (line packet shape recovery anchor) and 5 primary eventive tests (PT1-PT5). Result: **EVENTIVE_CLOSURE_INSUFFICIENT** -- P2 PASS, 1/5 PT pass (PT3 only). PT1, PT2, PT4, PT5 failed.

**Critical finding:** ERM axis inversion. The full model's ERM is negative for most event types while null ERM is strongly positive (~0.34-0.43). During closure events, the full model INCREASES process deviation rather than resolving it. Nulls appear to resolve excursion better because shuffled phases create regression-to-mean artifacts.

---

## Context
Phase 568 established three stable discrimination metrics: UEB (unresolved excursion burden), WCP (work-closure packet coherence), and EWP (edge waste penalty). These confirmed that the burden axis inversion from Phase 567 was a measurement artifact (C1612) and that packet coherence is a genuine property of supervised traces (C1614). However, EP1, EP2, EP4, EP7 failed, suggesting remaining discrimination gaps.

Phase 569 asked: can we improve discrimination by examining closure events selectively -- filtering by event type (opacity, compound structure, arming state) and qualifying by demand context (work-preceded events that create genuine excursion needing resolution)?

## What Changed
1. **Event Taxonomy (T1):** Classified all 463 closure lines across 83 Currier B folios into 7 overlapping event types based on opacity measures, compound token structure, MCB density, CTS threshold exceedance, decisive opacity, and arming state.

2. **Event Executor (T2):** Extended the shared_metrics plant simulator to compute per-event-type ERM (Excursion Resolution Metric), ESQ (Excursion Sequencing Quality), and EW (Excursion Waste) for each closure line, plus demand qualifiers (work_preceded).

3. **Null Event Executor (T3):** Ran 40 null shuffles per folio using the same event taxonomy and shared_metrics module, eliminating T1/T2 metric divergence.

4. **Event Validation (T4):** Five primary tests (PT1-PT5) plus 8 diagnostics (D1-D8) testing folio-level dominance, B10 comparison, anchor stability, type-selective discrimination, and demand qualification.

## Test Results

### P2: Line Packet Shape Recovery (Anchor)
**PASS** -- 7/5 SVs significant (n=2306 lines). 9th consecutive PASS.

| SV | rho | p | significant |
|----|-----|---|-------------|
| T | 0.82667 | 0.00000 | True |
| RC | 0.65111 | 0.00000 | True |
| S | -0.29295 | 0.00000 | True |
| C | -0.44742 | 0.00000 | True |
| TR | -0.46408 | 0.00000 | True |
| X | -0.12958 | 0.00000 | True |
| Y | 0.18324 | 0.00000 | True |

### Primary Eventive Tests (PT1-PT5)
| Test | Description | Result | Detail |
|------|-------------|--------|--------|
| PT1 | Full dominates null on >= 2/3 ERM metrics per folio (E_any) | **FAIL** | 5/18 folios (gate=12) |
| PT2 | Full ERM > B10 ERM (Cohen's d >= 0.35) | **FAIL** | d = -0.12777 (gate=0.35000) |
| PT3 | UEB + WCP anchors stable | **PASS** | UEB 15/14, WCP 19/14 |
| PT4 | >= 2 event types individually discriminating | **FAIL** | 0/2 types |
| PT5 | Demand-qualified ERM > null ERM (d >= 0.25) | **FAIL** | d = 0.14084 (gate=0.25000) |

**Score: P2 PASS + 1/5 PT pass**

### Diagnostics Summary (D1-D8)

**D1: Event Count Ratio (full vs null)**
| Event Type | Full Mean Count | Null Mean Count | Ratio |
|------------|-----------------|-----------------|-------|
| E_any | 6.15000 | 6.21750 | 0.98914 |
| E_opaque | 2.00000 | 2.17225 | 0.92070 |
| E_armed | 1.60000 | 1.81825 | 0.87997 |

**D2: Full vs Null ERM by Event Type (axis inversion diagnostic)**
| Event Type | n_folios | Full Mean ERM | Null Mean ERM | Cohen's d |
|------------|----------|---------------|---------------|-----------|
| E_any | 18 | -0.01077 | 0.33852 | -0.94200 |
| E_opaque | 13 | -0.09558 | 0.36472 | -0.80021 |
| E_opaque_decisive | 13 | -0.07188 | 0.37623 | -0.63379 |
| E_compound | 13 | 0.00145 | 0.37942 | -0.71703 |
| E_armed | 12 | -0.11704 | 0.37308 | -0.67529 |
| E_cts50 | 12 | -0.25000 | 0.35957 | -0.54214 |
| E_mcb | 10 | 0.29031 | 0.42329 | -0.78785 |
| E_decisive | 8 | 0.25243 | 0.42914 | -1.03566 |

**D3: Event Tier Distribution** -- E_any: 11 folios at tier 3 (highest), 2 at tier 0.

**D4: Full vs B10 ERM by Event Type** -- E_any: full mean ERM = -0.01077, B10 mean ERM = 0.05332, Cohen's d = -0.12777.

**D5: ERM-CCY Correlation** -- Pearson r = 0.02095 (n=18 folios). No meaningful correlation between event resolution and closure-conditioned yield.

**D6: Global vs Section-Normalized Thresholds** -- E_any global mean ERM = -0.01077, section-normalized mean ERM = -0.01077. No improvement from section normalization for E_any.

**D7: Phase-Native vs Structure-Native ERM** -- Phase-native mean ERM = 0.35053 (n=18), structure-native mean ERM = 0.29862 (n=18). Phase-native ERM is slightly higher, suggesting phase alignment helps but the gap is modest.

**D8: Demand-Qualified Event Resolution** -- work_preceded: 11 folios, 28 events, mean ERM = 0.36676. Demand-qualified events show positive ERM (0.367) vs overall E_any ERM (-0.011), confirming that work-preceded closure events resolve better, but the effect is too weak to pass PT5 (d=0.14084).

---

## Full Model Summary Values
| Metric | Mean |
|--------|------|
| PCV | 0.86537 |
| SAHB | 0.12685 |
| WCU | 0.51574 |
| SLR_mean | 0.15698 |
| UEB | 7.27500 |
| WCP | 0.85185 |
| EWP | 0.75056 |
| CCY | 0.25235 |
| QGY | 0.16925 |
| old_viability | 0.99883 |
| old_y_final | 0.64335 |
| n_tokens | 6225 |

### Event Type Summary (Pilot Folios)
| Event Type | Global Count | Global Fraction | Pilot Count | Pilot Mean ERM | Pilot EIR |
|------------|-------------|-----------------|-------------|----------------|-----------|
| E_any | 463 | 1.0000 | 123 | 0.02192 | 0.69919 |
| E_opaque | 148 | 0.3197 | 40 | -0.19385 | 0.67500 |
| E_opaque_decisive | 111 | 0.2397 | 33 | -0.09479 | 0.69697 |
| E_compound | 170 | 0.3672 | 40 | -0.04178 | 0.72500 |
| E_armed | 134 | 0.2894 | 32 | -0.11941 | 0.68750 |
| E_cts50 | 84 | 0.1814 | 23 | -0.24429 | 0.73913 |
| E_mcb | 57 | 0.1231 | 17 | 0.29957 | 0.76471 |
| E_decisive | 36 | 0.0778 | 12 | 0.28033 | 0.66667 |

---

## Cross-Phase Comparison
| Phase | Score | Key Result |
|-------|-------|------------|
| 563 | 5/9 | Baseline apparatus coupling |
| 563b | 3/9 | Sensitivity recalibration |
| 564 | 2/9 | Event-gated execution |
| 564b | 2/9 | Selective restoration |
| 565 | 2/9 | Permeability calibration |
| 566 | 1/9 | CLOSE recovery |
| 567 | P2 + 3/7 NP | PARTIAL: readout reform partially works |
| 568 | P2 + 3/7 EP | PARTIAL: controlled excursion metrics partially work |
| **569** | **P2 + 1/5 PT** | **EVENTIVE_CLOSURE_INSUFFICIENT** |

> **Note:** Phases 563-566 used P1-P9 tests. Phase 567 used P2 + NP1-NP7. Phase 568 uses P2 + EP1-EP7. Phase 569 uses P2 + PT1-PT5. Test batteries are not directly comparable but track the same underlying question: does the full model discriminate from nulls?

---

## Analysis

### What Worked
1. **PT3 PASS** -- UEB (15/14) and WCP (19/14) anchors stable. The Phase 568 wins are real and reproducible under the shared_metrics module.
2. **P2 PASS** -- 9th consecutive line packet shape recovery. The structural backbone of the model is robust.
3. **Shared metrics module** -- eliminated T1/T2 divergence by using identical plant simulation code across full and null executors. This is a process success, not a test result.
4. **Event taxonomy produced meaningful frequency distributions** -- E_opaque covers 32.0% of closure lines, E_opaque_decisive 24.0%, E_compound 36.7%, grounding the taxonomy in the opacity grammar (C1440-C1445).
5. **Demand-qualified events show positive ERM** -- work_preceded events have mean ERM = 0.367 vs overall E_any ERM = -0.011. Work-preceded closure events do resolve excursion, confirming that the qualifier concept is sound even if the effect is too weak for PT5.

### What Did Not Work
1. **PT1 FAIL** -- Only 5/18 eligible folios showed full-model dominance with E_any (gate = 12). The full model fails to dominate null models on event resolution metrics at the folio level.
2. **PT2 FAIL** -- Cohen's d = -0.12777 (gate = 0.35000). The full model's E_any ERM (mean = -0.01077) is actually WORSE than B10's ERM (mean = 0.05332). B10 has better event resolution than the full model.
3. **PT4 FAIL** -- 0/2 event types individually discriminating (gate = 2). No selective event type passed the d >= 0.35 threshold with >= 10 folios. All event types show negative Cohen's d (full ERM < null ERM).
4. **PT5 FAIL** -- d = 0.14084 (gate = 0.25000). Demand-qualified events are insufficient to overcome the overall ERM deficit.
5. **ERM axis inversion across all event types** -- Full model ERM is negative or near zero for E_opaque (-0.09558), E_armed (-0.11704), E_cts50 (-0.25000), E_opaque_decisive (-0.07188), while null ERM is consistently positive (~0.34-0.43).

### Why INSUFFICIENT
The fundamental finding is **ERM axis inversion**: during closure events, the full model's plant dynamics increase process deviation rather than resolving it. Null models appear to resolve excursion better because:

1. Under shuffled phases, "CLOSE" labels land on random lines, creating regression-to-mean artifacts that look like resolution.
2. The full model's CLOSE lines are placed where genuine excursion exists, making resolution harder because the plant faces real deviation.
3. The plant's close recovery channels (R1-R5) may not be strong enough to overcome the ongoing excursion at those specific positions.

This means the remaining discrimination gap is **not** a readout/averaging problem (which phases 567-569 tested). It is a **plant dynamics** problem: the apparatus needs stronger or differently-tuned close recovery channels at the specific positions where closure events occur.

With P2 PASS + only 1/5 PT pass, the result falls below the 2/5 threshold for PARTIAL and is therefore INSUFFICIENT.

---

## Provisional Constraints

### Confirmed from Phase 568
- **C1612: Unresolved excursion burden inverts SAHB** -- Confirmed. PT3 PASS shows UEB discriminates (15/14 folios), meaning the CLOSE-phase burden restriction is a genuine property.
- **C1614: Packet coherence discriminates supervised traces** -- Confirmed. PT3 PASS shows WCP discriminates (19/14 folios), meaning phase-aware coherence is a real structural property.

### New Constraints from Phase 569
None. With verdict INSUFFICIENT, no new constraints are validated.

---

## Lessons and Implications

1. **ERM inversion is diagnostic.** The fact that full model ERM < null ERM tells us the plant is failing at CLOSE-line resolution, not that the readout was wrong. This inverts the blame from measurement framework (phases 567-568) to plant dynamics.

2. **Anchors hold.** UEB and WCP (from 568) are confirmed stable across a different test battery and a different executor architecture. These are durable properties, not phase-specific artifacts.

3. **Eventive taxonomy is structurally sound but the plant cannot exploit it.** The event types (E_opaque, E_opaque_decisive, E_compound, E_armed) are well-grounded in constraints (C1440-C1445). The problem is not with the classification of closure events but with the plant's inability to resolve them.

4. **Demand qualification partially works.** Work-preceded events show positive ERM (0.367) while overall E_any ERM is negative (-0.011). The concept of demand-driven closure is sound, but the plant's recovery during demand-qualified events is still insufficient to discriminate from nulls at the required effect size.

5. **Section-normalized thresholds do not help.** D6 shows no improvement from section-aware event classification (E_any: global ERM = -0.01077, section-normalized ERM = -0.01077). The problem is below the classification layer.

6. **Phase-native vs structure-native ERM.** D7 shows phase-native ERM (0.351) is slightly higher than structure-native ERM (0.299), suggesting phase alignment helps modestly but is not the bottleneck.

7. **No single event type reaches Tier 2 threshold.** Only E_any had >= 10 folios with events. The 20-pilot-folio set is too small for selective event types that appear in fewer folios.

---

## Next Phase Recommendations

1. **Diagnose CLOSE-phase plant dynamics.** Why does the full model INCREASE deviation during CLOSE? Examine R1-R5 channel behavior during specific closure events. The ERM inversion is the central diagnostic target.

2. **Plant law modification.** If CLOSE recovery channels are too weak, consider gain amplification, zone boundary adjustment, or adding new recovery pathways. The plant's close-phase behavior is the bottleneck, not the measurement framework.

3. **Eventive taxonomy should be retained.** The event types and demand qualifiers are well-defined; the problem is the plant, not the measurement framework. Future phases that modify plant dynamics should reuse this taxonomy.

4. **Expand pilot set.** 20 folios is insufficient for selective event types. Consider 40+ folios to achieve >= 10 folios per event type for selective discrimination testing.

5. **Next-phase fork:** The remaining discrimination gap is confirmed as a plant dynamics problem, not further readout refinement. Plant law modification is the next step.

---

*Generated by t5_synthesis.py | Phase 569 | 2026-03-10 13:25 UTC*
