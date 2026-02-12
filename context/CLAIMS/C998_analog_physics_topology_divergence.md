# C998: Analog Physics Does Not Force Voynich Grammar Topology

**Tier:** 2
**Scope:** B
**Phase:** THERMAL_PLANT_SIMULATION

## Constraint

A minimal reflux distillation simulation (100 LHS-randomized parameterizations × 10 runs, P-controller with 3-step operator delay, energy-balance ODE) achieves only **median 3/10** Voynich quantitative targets. Null models (batch still β=0, open heating α=0) score equally or higher (3 and 4 median hits respectively). The Voynich grammar's discrete topology — 6-state hub-spoke, spectral gap 0.894, 17 forbidden pairs, 75.2% post-overshoot cooling bias — cannot emerge from continuous thermal plant dynamics alone. The grammar requires a discrete encoding layer beyond analog physics.

## Evidence

### Simulation Design (Non-Circular)

| Component | Determined By | NOT By Voynich |
|-----------|--------------|----------------|
| Dynamics | Thermodynamics (energy balance) | Yes |
| Control policy | P-controller (generic control theory) | Yes |
| Material params | Random LHS within physical ranges | Yes |
| Noise | Physical variability | Yes |
| State count K | BIC model selection (K=2..12) | Yes |
| Lane definition | dT/dt sign (heating vs cooling) | Yes |
| Forbidden pairs | Null-calibrated (analytical expected counts) | Yes |
| Verdict metric | Median across 100 parameter sweep | Yes |
| Comparison targets | Voynich constraints | Comparison only |

### T3: Per-Metric Results

| Metric | Simulated (median) | Voynich Target | Hit Rate |
|--------|-------------------|----------------|----------|
| State count (K) | 10 | 5-7 (C978) | 17% |
| Hub mass | 0.558 | 0.60-0.70 (C978) | 6% |
| Spectral gap | 0.000 | >0.80 (C978) | 1% |
| Alternation rate | 0.462 | 0.50-0.60 (C643) | 26% |
| Alternation asymmetry | -0.002 | >0 (C643) | 46% |
| Post-overshoot cooling | 0.215 | >0.70 (C645) | 2% |
| Forbidden pairs | 0 | 10-25 (C783) | 4% |
| Safety buffer rate | 0.000 | <0.01 (C997) | 92% |
| Oscillation variation | 0.434 | >0.20 (C650) | 100% |
| Run-length median | (2, 2) | (1, 1) (C643) | 13% |

**Verdict: STRUCTURAL_DIVERGENCE** — median 3/10 hits across 100 parameterizations.

### T4: Null Model Comparison

| Model | Median Hits | Mean Hits |
|-------|-------------|-----------|
| Reflux (full model) | 3 | 3.07 |
| Batch Still (β=0, no reflux) | 3 | 2.88 |
| Open Heating (α=0, no phase change) | 4 | 4.26 |

**No reflux advantage.** Reflux-specific dynamics (vaporization + condensation) do not improve Voynich fidelity over generic P-controller oscillation.

### Hardest Features to Reproduce Physically

| Feature | Hit Rate | Interpretation |
|---------|----------|----------------|
| Spectral gap | 1% | Continuous dynamics → diffuse mixing, not rapid convergence |
| Post-overshoot cooling | 2% | Physical asymmetry too weak for 75% bias |
| Forbidden transitions | 4% | Smooth dynamics → no hard boundaries |
| Hub mass | 6% | GMM distributes mass across too many states |

These are the features most likely to be **convention-imposed** (designed into the instruction set) rather than physics-forced.

### Features That DO Match

| Feature | Hit Rate | Source |
|---------|----------|--------|
| Oscillation variation | 100% | Generic: any P-controller with delay |
| Buffer rate | 92% | Vacuously: simulation produces 0 forbidden pairs → 0 buffers needed |
| Alternation asymmetry | 46% | Weak: random chance level |

## Implications

1. **The grammar is not analog physics.** The manuscript's 6-state hub-spoke topology with sharp boundaries, fast mixing (spectral gap 0.894), and 17 forbidden transitions cannot be produced by integrating thermal ODEs. These features require explicit discrete encoding.

2. **Reflux adds no specificity.** The vaporization/condensation cycle contributes nothing beyond what a simple heater/cooler produces. If distillation is the subject matter, it is the *control program* that generates the grammar, not the physics.

3. **Supports the control program interpretation.** The frozen conclusion states the manuscript encodes "closed-loop, kernel-centric control programs." This phase confirms that the *program structure* (instruction set, transition rules, hazard gates) is the source of Voynich topology, not the physical process being controlled.

4. **Constrains interpretation:** Any physical interpretation must explain the discrete encoding layer. The 49 instruction classes, 17 forbidden transitions, and hub-spoke topology are properties of a *designed instruction set*, not emergent from analog dynamics.

## Related Constraints

- **C978** (Hub-Spoke Topology): Simulation fails to reproduce 6-state topology (median K=10)
- **C643** (Lane Hysteresis Oscillation): Alternation rate close (0.462 vs 0.549) but asymmetry absent
- **C645** (CHSH Post-Hazard Dominance): Post-overshoot cooling drastically too weak (21.5% vs 75.2%)
- **C650** (Section-Driven Oscillation): Oscillation variation is the one feature that matches — generic P-controller effect
- **C997** (Sparse Safety Buffer Architecture): Buffer rate matches vacuously (no forbidden pairs → no buffers needed)

## Provenance

- Phase: THERMAL_PLANT_SIMULATION
- Scripts: t1_thermal_simulation.py, t2_automaton_extraction.py, t3_voynich_comparison.py, t4_null_models.py
- Results: t3_voynich_comparison.json, t4_null_models.json
- Non-circularity: Expert-reviewed design with 3 contamination corrections (random LHS params, P-controller only, null-calibrated forbidden transitions)
