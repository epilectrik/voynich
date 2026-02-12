# C976: Transition Topology Compresses to 6 States

**Tier:** 2 | **Scope:** B | **Phase:** MINIMAL_STATE_AUTOMATON

## Statement

The 49-class Currier B transition matrix compresses to a minimal 6-state automaton (8.2x compression) while preserving all structural constraints: role integrity, depleted-pair asymmetry, and FL ordering. The 6-state count is holdout-invariant (100/100 trials produce exactly 6 states, mean ARI = 0.939). This is transition-topology compression, not grammar simplification — the 49-class discrimination space remains high-dimensional.

## The 6 States

| State | Classes | Role(s) | Frequency | Function |
|-------|---------|---------|-----------|----------|
| S0: FL_HAZ | {7, 30} | FL | 5.9% | Hazard flow markers |
| S1: FQ | {9, 13, 14, 23} | FQ | 18.0% | Frequent operators (scaffold) |
| S2: CC | {10, 11, 12} | CC | 4.6% | Core control primitives |
| S3: AXm | {3, 5, 18, 19, 42, 45} | AX/EN | 3.0% | Minor execution group |
| S4: AXM | 32 classes | AX/EN | 67.7% | Major operational mass |
| S5: FL_SAFE | {38, 40} | FL | 0.8% | Safe flow markers |

## Evidence

- **Spectral analysis (T2):** 48/49 eigenvalues significant (>0.01), but NMF elbow at k=3 and spectral gap suggests 2 macro-states. High information content, low structural necessity.
- **Constraint-preserving merge (T3):** Agglomerative JSD-based merging with role integrity and depletion asymmetry verification at each step. 43 valid merges from 49→6 states. No further merges possible: 14 ROLE blocks + 8 DEPLETION blocks.
- **Generative validation (T4):** 6-state automaton reproduces 4/5 corpus metrics (Zipf z=+0.8, asymmetry z=-0.1, cross-line MI z=+1.3, active classes z=0.0). Only mismatch: depleted pair count (real 19 vs synthetic 3.8, z=+7.6) — depletion is within-state texture.
- **Holdout stability (T9):** 100 trials removing 5 random folios each. State count = 6 in 100% of trials. Mean ARI vs canonical = 0.939. Exact partition recovery = 46%. Instability is only at AXm/AXM boundary.

## Three-Layer Architecture

| Layer | What it encodes | Dimensionality |
|-------|----------------|----------------|
| 6-state automaton | Control topology (transition legality) | 6 |
| 49-class grammar | Instruction equivalence classes | 49 |
| Token-level MIDDLE | Execution parameterization | ~128 (C973) |

## Binding Constraints (What Prevents 5 States)

- FL_HAZ + FL_SAFE: FL ordering violation (C586, C773)
- FQ + CC: REGIME-conditioned routing destroyed (T8)
- FQ + AX/EN: ROLE integrity + depleted pairs (C13→5, C9→33)
- AXm + AXM: DEPLETION asymmetry violation (C5→34)
- FL + AX/EN: ROLE integrity

## Key Distinction

Role taxonomy constraints and dynamic transition constraints block the **same merges**. This convergence means the role system is not cosmetic — it tracks the same natural partitions that the dynamics require.

## Provenance

- Extends: C121 (49 instruction classes), C109 (forbidden pairs), C586 (FL HAZ/SAFE split)
- Confirmed by: T3 (merge), T4 (generation), T6 (topology), T9 (holdout)
- Results: `phases/MINIMAL_STATE_AUTOMATON/results/t3_merged_automaton.json`
