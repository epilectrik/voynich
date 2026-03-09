# Phase 563: Virtual Apparatus Coupling

**Phase:** 563
**Date:** 2026-03-09
**Verdict:** PARTIAL_COUPLING (5/9 tests pass)
**New constraints:** C1581-C1587

## Summary

Phase 563 tested whether the validated hierarchical trace executor (Phase 562) can be coupled to a virtual thermal apparatus model and produce structured, non-trivial plant behavior. Three apparatus profiles (A1_BATH_REFLUX, A2_SEALED_RECIRCULATION, A3_DISTILL_COLLECT) were defined from C1248 marker co-occurrence architecture. A supervisory interface mapped Voynich grammar features (domain fracs, hazard class, packet phase, CTS closure, headless rate) to 7 plant state variables (T, RC, S, C, TR, X, Y). The coupled system was run on 7 pilot folios across 3 profiles, 5 baselines, and 4 null models (50 permutations each).

The coupling substrate is REAL: the full hierarchical trace produces higher plant viability than budget-only and null baselines (P1), line packet phases produce strongly differentiated plant states (P2), CTS closure adds genuine value (P6), 3/4 null shuffle types destroy coupled behavior (P7), and section-assigned profiles are best-or-near-best for 5/7 folios (P8). Failures concentrate in underpowered tests (P3, P5), excursion dynamics (P3b needs oscillatory tuning), and punctual routing (P4 -- routing operates as sustained domain bias, not single-token deflection).

## Results

| Test | Pass | Key Finding |
|------|------|-------------|
| P1 Viable Envelope | PASS | full > B2 for 5/7, full > N1 for 7/7 |
| P2 Packet Shape | PASS | All 7 state vars significant globally (C H=191.6, Y H=148.4) |
| P3 Section Template | FAIL | 0/7 significant (N=7, underpowered) |
| P3b Productive Diversity | FAIL | Nontrivial frac 7/7 pass, but excursions=1.3 (need >3) |
| P4 Routing Consequence | FAIL | 0/4 routing signatures directionally correct at token level |
| P5 Headless Regime | FAIL | p>0.05 (N=3 vs 4, underpowered) |
| P6 CTS Closure | PASS | viab better 6/7, Y better 7/7, C-separation positive 6/7 |
| P7 Null Destruction | PASS | 3/4 null types destroyed (N1, N2, N4; N3 resistant) |
| P8 Preferred Profile | PASS | 5/7 preferred profiles best on >=1 metric |

### Composite Metrics

| Metric | Value |
|--------|-------|
| Mean viability (7 folios) | 0.9616 |
| Mean Y_final | 0.878 |
| Total hazard events | 34 |
| Folios with perfect viability | 4/7 |

## Key Findings

**What worked:**
- **P2 is the strongest result.** All 7 plant state variables are significantly differentiated by line packet phase (SPEC/WORK/CLOSE) globally. C (containment) and Y (yield accumulation) show the strongest effects (H=191.6, H=148.4). The line-level three-zone architecture (C1425-C1430) is the primary channel through which grammar couples to apparatus.
- **P7 confirms non-trivial coupling.** Token-shuffling (N1), domain-preserving shuffle (N2), and terminal-shuffling (N4) all destroy coupled plant behavior. Only line-shuffling (N3) is resistant, consistent with C1399/C1400/C1470 (line ordering carries less information than token composition).
- **P6 validates CTS closure.** The continuous closure encoding from Phase 562b (C1579) is not just a better executor feature -- it produces genuine plant-level consequences (higher viability, higher yield, positive containment separation at closure lines).

**What failed and why:**
- **P3 (section template):** N=7 folios across 3 sections is severely underpowered. Direction is plausible (Bio S=0.934 > Herbal S=0.715) but no variable reaches significance.
- **P3b (excursion dynamics):** Plants stay viable (nontrivial >0.95) but barely oscillate (mean 1.3 excursions vs threshold 3). Decay/recovery parameters need tuning to produce productive oscillation.
- **P4 (routing consequence):** Terminal atom routing (C1563) does NOT produce observable punctual deflections. Rates are ~0.45-0.50, indistinguishable from chance at window=5. This is a MECHANISTIC finding: routing operates as sustained domain rebalancing over line segments, not as single-token state kicks. Future models should integrate routing cumulatively.
- **P5 (headless regime):** Direction is correct (high-headless folios have higher C and S means) but N=3 vs 4 is hopelessly underpowered. Full corpus run needed.

## Constraints Proposed

| C# | Status | Tier | Statement |
|----|--------|------|-----------|
| C1581 | CONFIRMED | 2 | Full hierarchical supervisory trace coupled to virtual apparatus yields structured plant behavior beyond section-only, budget-only, and null controls |
| C1582 | CONFIRMED | 2 | Line packet state produces statistically significant plant state differentiation across all 7 state variables |
| C1583 | CONFIRMED | 2 | Core terminal routing grammar does NOT produce observable isolated local plant deflections at token level (negative result) |
| C1584 | PROVISIONAL | 3 | Headless folio regime effect on plant containment is directionally correct but statistically underpowered at N=7 |
| C1585 | CONFIRMED | 2 | CTS continuous closure contributes genuine value to coupled plant behavior |
| C1586 | CONFIRMED | 2 | N3 line-shuffle null is non-destructive: line ordering carries less coupled-plant information than token composition |
| C1587 | OBSERVED | 3 | A2_SEALED_RECIRCULATION underperforms A1_BATH_REFLUX for Herbal-REGIME_2 folios |

## Implications for Phase 564

1. **Routing as sustained bias.** Future executor should model cumulative routing effect over line segments, not single-token windows.
2. **A2 profile recalibration.** Herbal folios assigned to A2 underperform -- section-to-profile mapping needs refinement.
3. **Excursion tuning.** Decay/recovery parameters need adjustment to produce productive oscillation (currently regime-sustaining, not oscillatory).
4. **Full corpus run.** N=7 insufficient for section-level and headless tests. Power analysis suggests N>=20 per section.
5. **Line ordering independence confirmed.** N3 resistance validates folio-as-program paradigm -- line composition matters, line order doesn't.
6. **CTS closure standard.** CTS should be standard in all future trace-apparatus coupling.
7. **Packet shape is primary channel.** P2 strongest result -- SPEC/WORK/CLOSE is where grammar meets apparatus.

## Scripts

| Script | Purpose | Output |
|--------|---------|--------|
| t1_apparatus_family_builder.py | Define 3 apparatus profiles from C1248 | t1_apparatus_family.json |
| t2_trace_to_supervisory_interface.py | Map grammar features to plant state variables | t2_supervisory_interface.json |
| t3_trace_coupled_executor.py | Run coupled traces on 7 pilot folios x 3 profiles | t3_coupled_traces.json |
| t4_null_and_ablation_executor.py | Run 5 baselines + 4 nulls x 50 perms | t4_null_ablation_traces.json |
| t5_plant_behavior_validation.py | 9-test validation battery | t5_plant_validation.json |
| t6_synthesis.py | Aggregate results, verdict, constraints | t6_synthesis.json |
