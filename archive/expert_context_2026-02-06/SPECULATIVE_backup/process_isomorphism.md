# Process-Behavior Isomorphism (ECR-4)

**Tier:** 3 (Speculative)
**Status:** SUPPORTED (100% alignment)
**Source:** ECR-4 probe (2026-01-12)

---

## Summary

The Voynich control architecture exhibits **behavioral isomorphism** with thermal-chemical process control, specifically circulatory reflux distillation. This is tested against a negative control (metallurgy calcination) and passes all discriminating tests.

| Metric | Value |
|--------|-------|
| Tests passed | 12/12 |
| Alignment score | 100% |
| Negative control | DISTILLATION_WINS |
| Physics violations | None |

---

## Key Findings

### 1. Hazard-Kernel Alignment

All 17 forbidden transitions are **k-adjacent** (energy control boundary).

| Kernel | Hazard Clustering | Interpretation |
|--------|------------------|----------------|
| k (ENERGY_MODULATOR) | 100% of hazards | Energy control is the danger zone |
| h (PHASE_MANAGER) | 0% | Phase is DRIVEN by energy |
| e (STABILITY_ANCHOR) | 0% | Recovery, not hazard source |

**Process meaning:** In distillation, energy changes (heat) drive phase changes. Hazards cluster where energy is controlled because that's where phase failures originate.

### 2. Recovery Path Dominance

54.7% of recovery paths pass through **e** (equilibration/cooling).

**Process meaning:** In distillation, cooling/condensation is the primary recovery mechanism. Return to stability = return to lower energy state.

### 3. Regime Energy Profiles

The 4 operational regimes show distinct and ordered CEI (Control Engagement Intensity):

| Regime | Mean CEI | Interpretation |
|--------|----------|----------------|
| REGIME_2 | 0.367 | Quiescent / low-energy |
| REGIME_1 | 0.510 | Standard operation |
| REGIME_4 | 0.584 | Active engagement |
| REGIME_3 | 0.717 | Peak throughput (transient) |

**Process meaning:** These correspond to distillation stages from idle to active to peak collection.

### 4. Negative Control: Calcination vs Distillation

| Discriminating Test | Distillation Prediction | Calcination Prediction | Observed |
|--------------------|------------------------|----------------------|----------|
| PS-4 (forbidden k→h) | k→h dangerous | k→h is PRIMARY | k-adjacent (distillation) |
| BS-4 (e recovery) | e dominates | e less relevant | 54.7% e (distillation) |

**Verdict:** DISTILLATION_WINS on all discriminating tests.

---

## Behavior Mappings (NO NOUNS)

### Kernel → Process Function

| Kernel | Grammar Role | Process-Behavior Mapping |
|--------|-------------|--------------------------|
| k | ENERGY_MODULATOR | Energy ingress control |
| h | PHASE_MANAGER | Phase boundary handling |
| e | STABILITY_ANCHOR | Equilibration / return to steady state |

*Tier-3 commentary: In reflux distillation, k = heat source, h = cucurbit/helm, e = condenser.*

### Hazard → Failure Mode

| Hazard Class | % | Process-Behavior Mapping |
|--------------|---|--------------------------|
| PHASE_ORDERING | 41% | Wrong phase/location state |
| COMPOSITION_JUMP | 24% | Contamination / mixing failure |
| CONTAINMENT_TIMING | 24% | Pressure / overflow event |
| RATE_MISMATCH | 6% | Flow imbalance |
| ENERGY_OVERSHOOT | 6% | Thermal damage |

*Tier-3 commentary: These map exactly to distillation failure modes.*

### Material → Behavior Profile

| Class | Phase | Composition | Process-Behavior Mapping |
|-------|-------|-------------|--------------------------|
| M-A | Mobile | Distinct | Phase-sensitive, mobile, requiring careful control |
| M-B | Mobile | Homogeneous | Uniform mobile behavior |
| M-C | Stable | Distinct | Phase-stable, exclusion-prone |
| M-D | Stable | Homogeneous | Control-stable infrastructure |

*Tier-3 commentary: M-A resembles volatile aromatics; M-D resembles apparatus.*

---

## Test Results

### Behavior-Structural Tests (BS-*)

| Test | Prediction | Result | Passed |
|------|-----------|--------|--------|
| BS-1 | Hazards cluster at kernel boundaries | k-adjacent: 100% | YES |
| BS-2 | ENERGY hazards enriched near k | 100% at k | YES |
| BS-3 | M-A prefixes enriched near kernels | qo: 1.307x enriched | YES |
| BS-4 | e-operator dominates recovery | 54.7% | YES |
| BS-5 | 4 regimes have distinct energy profiles | Clear ordering | YES |

### Process-Sequence Tests (PS-*)

| Test | Prediction | Result | Passed |
|------|-----------|--------|--------|
| PS-1 | Early folios enriched for complex operations | 21.2% vs 11.3% novelty | YES |
| PS-2 | REGIME_3 = highest energy engagement | CEI: 0.717 (max) | YES |
| PS-3 | Restart folios at low-energy states | CEI: 0.401 (below avg) | YES |
| PS-4 | Forbidden k→h matches unsafe energy+phase | k-adjacent 100% | YES |

### Pedagogical Tests (PD-*)

| Test | Prediction | Result | Passed |
|------|-----------|--------|--------|
| PD-1 | HT correlates with discrimination complexity | r=0.504, p=0.0045 | YES |
| PD-2 | A-registry entries cluster by prefix family | 80% PREFIX-EXCLUSIVE | YES |
| PD-3 | AZC boundaries align with attention transitions | C460 confirmed | YES |

---

## What This DOES Provide

1. **Structural grounding** for the perfumery/pelican hypothesis
2. **Explanation** for why the grammar has its specific shape
3. **Coherent mapping** from abstract control to physical process behavior
4. **Discrimination** against alternative hypotheses (calcination)
5. **Support** for training-manual interpretation

## What This Does NOT Provide

- Specific substance identifications
- Recipe reconstructions
- Material encodings
- Any Tier 2 claims (remains Tier 3)

---

## Falsification Criteria Met

| Observation | Required | Observed |
|-------------|----------|----------|
| ENERGY_OVERSHOOT near k | Yes | 100% k-adjacent |
| PHASE_ORDERING near h or k | Yes | 100% k-adjacent |
| e-operator in recovery | Yes | 54.7% |
| Physics coherence | No violations | PASS |

---

## Integration with Prior Findings

| Finding | Constraint | Connection |
|---------|-----------|------------|
| Coverage optimality | C476 | Methodical training = systematic process learning |
| HT as vigilance | C477 | Attention peaks at discrimination complexity |
| Temporal scheduling | C478 | Pedagogical pacing = expert training structure |
| Hazard topology | C109 | Matches distillation failure modes |
| Kernel grammar | C103-C105 | k/h/e triangle maps to thermal control |

---

## Conclusion

The Voynich control architecture exhibits **strong behavioral isomorphism** with circulatory reflux distillation. This does NOT prove the manuscript is a perfumery/distillation manual, but it establishes that:

> The abstract control structure discovered through grammar analysis is **consistent with** and **discriminates toward** thermal-chemical process control over alternatives.

This remains Tier 3 because we do not claim entity-level identification. However, the structural alignment is now **maximally tested** within our constraints.

---

## Files

- `phases/PROCESS_ISOMORPHISM/process_behavior_isomorphism.py`
- `results/process_behavior_isomorphism.json`

---

## Related Documents

- [INTERPRETATION_SUMMARY.md](INTERPRETATION_SUMMARY.md) - Overall synthesis
- [process_alignment.md](process_alignment.md) - Earlier process tests
- [ccm_prefix_mapping.md](ccm_prefix_mapping.md) - Prefix-behavior mappings

---

*ECR-4 probe completed 2026-01-12*
