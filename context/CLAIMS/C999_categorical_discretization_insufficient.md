# C999: Categorical Discretization Does Not Bridge Voynich Topology Gap

**Tier:** 2
**Scope:** B
**Phase:** CATEGORICAL_DISCRETIZATION_TEST

## Constraint

Categorical discretization of continuous thermal plant simulation data does **not** improve Voynich topology fidelity beyond the continuous baseline (C998). Five physically-motivated discretization strategies and one random null were tested across 100 LHS-randomized parameterizations. The best physical strategy (lane_temp) moves only **3/9 metrics** toward Voynich — identical to random binning (3/9). Zero forbidden transitions emerge from any strategy. The Voynich grammar's discrete topology is an engineered symbolic abstraction, not a categorization artifact of continuous dynamics.

## Evidence

### Test Design (Non-Circular)

| Component | Determined By | NOT By Voynich |
|-----------|--------------|----------------|
| Input data | THERMAL_PLANT_SIMULATION T1 (100 parameterizations) | Yes |
| Strategy definitions | Physics/operational reasoning | Yes |
| State count K | Strategy-specific or BIC-selected | Yes |
| Legality rules | Physical impossibility constraints | Yes |
| Random null | K matched to best physical, random labels | Yes |
| Scoring | Direction-of-movement vs continuous baseline | Yes |
| Comparison targets | Voynich constraints | Comparison only |

### Strategies Tested

| Strategy | K | Method |
|----------|---|--------|
| lane_temp | 6 (effective 4) | 2 lanes (dT/dt sign) × 3 temperature zones (np.digitize) |
| operational | 6 (effective 4) | Hand-defined regimes (cold_start, heating, steady, overshoot, condensing, cooling) |
| gmm_bic | BIC-selected (median 10) | Gaussian mixture, K=2..12, BIC criterion |
| t_bins | 6 | Uniform temperature bins, K=4..8 best BIC |
| q_phase | 6 (effective 3) | 3 Q-action levels × 2 phase states |
| random | 6 | Random label assignment (null control) |

### T2: Direction-of-Movement Results

| Metric | Baseline | Best Physical | Random | Voynich |
|--------|----------|--------------|--------|---------|
| spectral_gap | 0.000 | 0.578 (lane_temp) | 0.940 | 0.894 |
| hub_mass | 0.558 | 0.360 (lane_temp) | 0.179 | 0.680 |
| n_forbidden | 0 | 0 (all) | 0 | 17 |
| alternation_rate | 0.462 | 0.462 (lane_temp) | 0.460 | 0.549 |
| asymmetry | -0.002 | -0.002 (lane_temp) | -0.019 | 0.043 |
| post_overshoot | 0.215 | 0.497 (lane_temp) | 0.479 | 0.752 |
| heat_run_median | 2.0 | 2.0 (lane_temp) | 2.0 | 1.0 |
| cool_run_median | 2.0 | 2.0 (lane_temp) | 1.0 | 1.0 |
| buffer_rate | 0.000 | 0.000 (all) | 0.000 | 0.0012 |

**Metrics toward Voynich:** lane_temp 3/9, operational 3/9, q_phase 3/9, random 3/9, gmm_bic 2/9, t_bins 2/9.

### Critical Findings

1. **Physical = Random.** No physical strategy outperforms random binning. Discretization has zero discriminative power for Voynich topology.

2. **Zero forbidden transitions universally.** All strategies (including physical and random) produce 0 null-calibrated forbidden pairs across all 100 parameterizations. Continuous dynamics produce fully-connected transition graphs regardless of discretization method.

3. **Spectral gap is a discretization artifact.** Random binning (0.940) exceeds Voynich (0.894). Any discretization of continuous data creates spectral gap — it is uninformative as a discriminator.

4. **Hub mass degrades.** Every strategy moves hub mass AWAY from Voynich (below baseline 0.558). Discretization fragments the dominant state rather than concentrating it.

5. **Legality rules are tautological.** lane_temp defines 8 physically-impossible transitions; all 8 are trivially absent (violation rate 0.0). These are constructive constraints, not emergent structure. q_phase defines 8 rules but only 6 hold (violation rate 20.6%).

### Verdict: DISCRETIZATION_INSUFFICIENT

Categorical discretization adds nothing over the continuous baseline. The 3/9 score matches THERMAL_PLANT_SIMULATION's 3/10 (C998). The missing Voynich features (17 forbidden arcs, concentrated hub mass, short run lengths, asymmetric alternation) require an engineered encoding layer — a designed instruction set — not physical categorization.

## Implications

1. **Voynich discreteness is designed, not emergent.** Two independent tests (continuous dynamics, discretized dynamics) both fail to produce Voynich topology. The grammar's discrete structure was imposed by a human designer creating an instruction set for process control.

2. **Closes the "categorization might explain it" pathway.** This was the natural follow-up to C998: if analog physics fails, does binning fix it? No. The architecture gap is not parametric (wrong bins) but structural (missing encoding rules).

3. **Strengthens the control program interpretation.** The 49 instruction classes, 17 forbidden transitions, and hub-spoke topology are properties of a designed notation system. The notation's structure encodes operational logic (what transitions are meaningful), not physics (what transitions are possible).

4. **Constrains future work.** Do not attempt to derive Voynich topology from physical simulation + discretization. The encoding layer must be hypothesized from the grammar's internal structure (constraint system) and operational reasoning.

## Related Constraints

- **C998** (Analog Physics Topology Divergence): Continuous baseline this phase extends; same 3/10 score
- **C978** (Hub-Spoke Topology): Hub mass degrades under all discretization strategies
- **C783** (Forbidden Transition Count): 0 forbidden from any strategy vs Voynich's 17
- **C997** (Sparse Safety Buffer): Buffer rate stays at 0 — no forbidden pairs means no buffers needed
- **C643** (Lane Hysteresis Oscillation): Alternation rate unchanged by discretization

## Provenance

- Phase: CATEGORICAL_DISCRETIZATION_TEST
- Scripts: t1_discretization_scoring.py, t2_verdict.py
- Results: t1_discretization_scoring.json, t2_verdict.json
- Non-circularity: Expert-reviewed design with 3 adjustments (direction-of-movement scoring, BIC-emergent K, legality imposition layer)
