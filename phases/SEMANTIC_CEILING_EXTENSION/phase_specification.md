# Semantic Ceiling Extension Testing Phase

**Status:** IN PROGRESS
**Date:** 2026-01-13
**Tier:** 3-4 (Exploratory)

---

## Epistemic Safeguard

> **All tests in this phase remain Tier 3/4 exploratory. Results strengthen or weaken interpretive plausibility but do NOT enable semantic decoding, do NOT promote to Tier 2 without independent corroboration, and do NOT reopen frozen structural constraints.**

---

## Overview

Seven tests organized into five categories, designed to push the semantic ceiling through inversion, temporal, and counterfactual analysis without reopening Tier 0-2 constraints.

---

## Test 2A: Temporal Trajectories Within B Programs

**Pre-Registered Question:**
> "Do B programs share a conserved temporal hazard trajectory?"

**Method:**
1. Divide each B program into early/mid/late segments (thirds)
2. Track per-segment: hazard class distribution, role-class usage, escape density
3. Cluster programs by trajectory shape
4. Test for conserved phase archetypes

**Success Criteria:**
- Significant clustering of trajectory shapes (p < 0.05)
- At least 2 distinct temporal archetypes identified

**Failure Criteria:**
- No significant clustering
- Trajectories random within programs

---

## Test 1A: B->A Discriminator Back-Inference

**Pre-Registered Question:**
> "Given distinctive B regime behaviors, what MIDDLE zone cluster constraints must have been active upstream?"

**Method:**
1. Select B folios by distinctive behaviors (brittleness, hazard density, escape reliance)
2. For each behavior profile, identify compatible MIDDLE zone clusters (P/S/C/R)
3. Test whether narrowed option space is significantly smaller than random

**Success Criteria:**
- Compatibility matrix shows non-random restriction (p < 0.05)
- At least one B behavior type restricts zone options by >50%

**Failure Criteria:**
- All zone clusters equally compatible with all B behaviors
- No significant narrowing of option space

---

## Test 3A: Remove e (Stability Anchor)

**Pre-Registered Question:**
> "How minimally necessary is the e operator for grammar viability?"

**Method:**
1. Re-run grammar viability metrics with e tokens removed
2. Measure: convergence rate collapse, hazard spike magnitude, recovery path availability
3. Identify which hazard classes spike first

**Success Criteria:**
- Significant degradation in at least one metric (>20% change)
- Clear identification of e's structural role

**Failure Criteria:**
- Grammar remains viable without e
- No significant metric changes

---

## Test 3B: Force Symmetric Hazards

**Pre-Registered Question:**
> "Is hazard asymmetry (65%) architecturally necessary or merely empirical?"

**Method:**
1. Randomize forbidden transition asymmetry (make all bidirectional or all unidirectional)
2. Re-run convergence analysis
3. Test whether monostate convergence collapses

**Success Criteria:**
- Convergence collapses under symmetric hazards
- Asymmetry demonstrated as necessary, not accidental

**Failure Criteria:**
- Convergence survives symmetrization
- Asymmetry is merely empirical artifact

---

## Test 1B: HT->A Back-Pressure

**Pre-Registered Question:**
> "Does HT morphology correspond to apparatus vs material pressure dominance?"

**Method:**
1. Categorize folios by HT density (high/medium/low)
2. Map to MIDDLE zone profiles active in those folios
3. Test whether HT complexity correlates with zone cluster diversity

**Success Criteria:**
- Significant correlation (p < 0.05) between HT and zone diversity
- Clear differentiation of apparatus vs material pressure

**Failure Criteria:**
- No correlation
- HT independent of zone profiles

---

## Test 4A: Operator Strategy Viability

**Pre-Registered Question:**
> "Which B programs tolerate which operator strategies?"

**Method:**
1. Define three strategy types: cautious, aggressive, opportunistic
2. Simulate each strategy against program archetypes
3. Map viable strategy-archetype combinations
4. Test whether HT density predicts strategy viability

**Success Criteria:**
- Non-uniform viability matrix (some strategies fail in some archetypes)
- HT density correlates with strategy tolerance

**Failure Criteria:**
- All strategies viable in all archetypes
- No HT-strategy correlation

---

## Test 5A: Memory Decay Optimality

**Pre-Registered Question:**
> "Is A-registry ordering optimal under realistic memory decay models?"

**Method:**
1. Introduce forgetting model (rare MIDDLEs decay faster)
2. Measure expected forgetting under manuscript ordering
3. Compare to random and frequency-sorted alternatives

**Success Criteria:**
- Manuscript ordering outperforms random significantly
- Evidence of deliberate pedagogical structure

**Failure Criteria:**
- Manuscript ordering no better than random
- No optimization signal

---

## Data Sources

| Test | Primary Data |
|------|--------------|
| 2A | `folio_analysis/hazard_maps/*.json`, `folio_analysis/kernel_trajectories/*.json` |
| 1A | `results/b_macro_scaffold_audit.json`, `results/middle_zone_survival.json` |
| 3A | `results/canonical_grammar.json`, `currierB.bcsc.yaml` |
| 3B | `context/METRICS/hazard_metrics.md` |
| 1B | HT density data, zone cluster assignments |
| 4A | `context/OPERATIONS/program_taxonomy.md`, `results/b_design_space_cartography.json` |
| 5A | MIDDLE frequency data, temporal scheduling data |

---

## Implementation Order

1. Test 2A (Temporal Trajectories)
2. Test 1A (B->A Back-Inference)
3. Test 3A (Remove e)
4. Test 3B (Symmetric Hazards)
5. Test 1B (HT->A)
6. Test 4A (Strategy Viability)
7. Test 5A (Memory Decay)

---

## Interpretation Rules

### If test PASSES:
Document as Tier 3 finding. Add to INTERPRETATION_SUMMARY.md with appropriate caveats.

### If test FAILS:
Document as informative negative result. Negative results are equally valuable - they constrain the interpretation space.

---

*Phase pre-registered 2026-01-13*
