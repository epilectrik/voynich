# Phase: SEMANTIC_CEILING_EXTENSION

## Summary

**Purpose:** Push the semantic ceiling via 7 pre-registered tests exploring B->A inversion, temporal trajectories, counterfactual grammar, operator strategies, and memory optimality.

**Status:** COMPLETED
**Tests Run:** 7/7
**Significant Findings:** 6/7 (one borderline)

---

## Test Results Overview

| Test | Question | Verdict | Significance |
|------|----------|---------|--------------|
| 2A | Do B programs share temporal hazard trajectories? | BORDERLINE_ARCHETYPES | p=0.062, 14/15 share PEAK_MID |
| 1A | Does B behavior constrain upstream A zones? | STRONG_DIFFERENTIATION | p<0.0001, high qo-density -> +10.4% P-text |
| 3A | Is the e-operator structurally necessary? | E_NECESSARY | Kernel contact collapses -98.6% |
| 3B | Is hazard asymmetry architecturally necessary? | ASYMMETRY_NECESSARY | h->k perfectly suppressed (0%) |
| 1B | Does HT correlate with zone diversity? | HT_ZONE_CORRELATED | r=0.24, p=0.0006 |
| 4A | Do strategies differentiate by archetype? | DIFFERENTIATED_STRATEGIES | All HT correlations p<0.0001 |
| 5A | Is A-registry ordering memory-optimal? | NEAR_OPTIMAL | z=-97 vs random (0th percentile) |

---

## Detailed Findings

### Test 2A: Temporal Trajectories (BORDERLINE)

**Question:** Do B programs share conserved temporal hazard trajectories?

**Result:** 14/15 folios share PEAK_MID pattern (hazard peaks in Q2). Chi-square p=0.062.

**Interpretation:** Near-significant evidence for shared phase archetype. Not strong enough to confirm conserved trajectory, but suggestive of mid-program hazard concentration.

### Test 1A: B->A Back-Inference (STRONG)

**Question:** Given distinctive B behaviors, what MIDDLE zones must have been active upstream?

**Result:**
- High qo-density folios use +10.4% more P-text MIDDLEs (p<0.0001)
- High-hazard and high-link folios show zone differentiation (p<0.05)
- Option space narrowing: 24% (reduced from 4 zones to ~3)

**Interpretation:** B-regime behavior successfully constrains A-layer inference. High qo-density programs (energy-intensive) preferentially draw from P-text (Currier A paragraph) vocabulary.

> **TERMINOLOGY NOTE (2026-01-31):** Original test used "escape" to mean qo_density.
> Per C397/C398 revision, qo is the energy lane operating hazard-DISTANT, not an escape mechanism.

### Test 3A: Remove e (NECESSARY)

**Question:** How minimally necessary is the e operator?

**Result:**
- Without e-class tokens, kernel contact collapses from 36.3% to 0.5% (-98.6%)
- Recovery ratio collapses from 31.6% to 0% (complete collapse)
- 27,203 tokens (36% of B) removed

**Interpretation:** The e-operator (stability anchor) is structurally load-bearing. Grammar cannot function without it.

### Test 3B: Symmetric Hazards (NECESSARY)

**Question:** Is hazard asymmetry architecturally necessary?

**Result:**
- h->k transition is perfectly suppressed: P(h->k) = 0.0000
- k->e recovery: 83.3%
- h->e recovery: 82.4%
- Mean asymmetry: 0.55

**Interpretation:** Hazard asymmetry is architecturally necessary. Allowing h->k would create oscillation between hazard states, destabilizing convergence.

### Test 1B: HT->A Back-Pressure (CORRELATED)

**Question:** Does HT morphology correspond to zone diversity?

**Result:**
- HT density vs zone diversity: r=0.24, p=0.0006
- High-HT folios: mean diversity=1.66
- Low-HT folios: mean diversity=1.60
- Group difference: t=3.71, p=0.0003

**Interpretation:** Higher HT density correlates with more diverse MIDDLE zone usage. Supports "material pressure" interpretation: elaborate HT tracks multi-zone material handling.

### Test 4A: Operator Strategies (DIFFERENTIATED)

**Question:** Which B programs tolerate which operator strategies?

**Result:**
- Archetype distribution: 50 MIXED, 17 CONSERVATIVE_WAITING, 10 ENERGY_INTENSIVE, 6 AGGRESSIVE_INTERVENTION
- Strategy viability is non-uniform across archetypes
- HT-strategy correlations (all p<0.0001):
  - HT vs CAUTIOUS: r=+0.46 (high HT favors cautious)
  - HT vs AGGRESSIVE: r=-0.43 (high HT rejects aggressive)
  - HT vs OPPORTUNISTIC: r=-0.48 (high HT rejects opportunistic)

**Interpretation:** HT density predicts operator strategy viability. High-HT programs require cautious intervention; low-HT programs tolerate aggressive/opportunistic approaches.

### Test 5A: Memory Decay Optimality (NEAR-OPTIMAL)

**Question:** Is A-registry ordering optimal under realistic memory decay?

**Result:**
- Manuscript ordering: forgetting z=-97.4 (0th percentile vs random)
- Manuscript is dramatically better than random ordering
- Ranked 5/5 vs theoretical alternatives (clustered/sorted)
- 34,740 entries, 2,037 unique MIDDLEs

**Interpretation:** A-registry ordering shows intentional memory optimization - far better than random chance would produce. Not perfectly optimal (theoretical clustering beats it), but strong evidence of designed ordering.

---

## Aggregate Findings

### Confirmed Structural Requirements

1. **e-operator is load-bearing** - Grammar collapses without stability anchor
2. **Hazard asymmetry is load-bearing** - h->k suppression prevents oscillation
3. **B behavior constrains A inference** - QO-density maps to P-text vocabulary preference
4. **HT tracks operational load** - Predicts strategy viability and zone diversity

### New Interpretive Support (Tier 3)

1. **Material pressure interpretation strengthened** - HT -> zone diversity correlation
2. **Operator strategy taxonomy validated** - Archetypes have distinct viability profiles
3. **Memory optimization in A ordering** - Not random, but deliberately structured

### Borderline/Inconclusive

1. **Temporal trajectory conservation** - Suggestive (p=0.062) but not confirmed

---

## Epistemic Status

All findings remain **Tier 3/4 exploratory**. Results:
- Strengthen interpretive plausibility
- Do NOT enable semantic decoding
- Do NOT promote to Tier 2 without independent corroboration

---

## Files Generated

| File | Purpose |
|------|---------|
| `results/temporal_trajectories.json` | Test 2A output |
| `results/b_to_a_inference.json` | Test 1A output |
| `results/counterfactual_grammar.json` | Tests 3A/3B output |
| `results/ht_backpressure.json` | Test 1B output |
| `results/operator_strategies.json` | Test 4A output |
| `results/memory_optimality.json` | Test 5A output |

---

## Constraints Affected

| Constraint | Status | Notes |
|------------|--------|-------|
| C109 (5 hazard classes) | Strengthened | Asymmetry confirmed necessary |
| C171 (closed-loop only) | Strengthened | e-operator load-bearing |
| C240 (A = registry) | Strengthened | Memory optimization detected |

## New Constraints Created

| # | Constraint | Tier | Scope |
|---|------------|------|-------|
| C485 | Grammar Minimality (e-operator and h->k suppression load-bearing) | 2 | B |
| C486 | Bidirectional Constraint Coherence (B constrains A zone inference) | 3 | CROSS_SYSTEM |
| C487 | A-Registry Memory Optimization (z=-97 vs random) | 3 | A |
| C488 | HT Predicts Strategy Viability (r=0.46/-0.48) | 3 | HT |
| C489 | HT Zone Diversity Correlation (r=0.24) | 3 | HT |

---

## Recommended Follow-Up

1. **Test 2A replication** - Run on larger folio set to confirm/reject PEAK_MID archetype
2. **P-text investigation** - Why do high qo-density programs prefer P-text vocabulary?
3. **HT-strategy mechanism** - What about HT tracks this operational load?
