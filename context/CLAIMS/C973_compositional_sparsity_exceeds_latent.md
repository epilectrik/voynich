# C973: Compositional Sparsity Exceeds Low-Dimensional Models

**Tier:** 2 | **Scope:** B | **Phase:** FINGERPRINT_UNIQUENESS

## Statement

MIDDLE co-occurrence incompatibility (0.460 at B-line level, 85 MIDDLEs) cannot be reproduced by latent feature models with 3-5 dimensions (null incompatibility: 0.001, p = 0.000). Low-dimensional semantic grouping is insufficient to explain the observed sparsity.

## Evidence

- Incompatibility = fraction of MIDDLE pairs that never co-occur in the same line
- Observed: 0.460 (85 unique MIDDLEs across 2,488 B lines)
- Hub savings: 0.298 (actual hub usage 31.6% vs 53.9% greedy baseline)

| Ensemble | Incomp mean | p(incomp) | p(hub) | p(joint) |
|----------|------------|-----------|--------|----------|
| NULL-G (token shuffle) | 0.453 | 0.093 | 0.143 | 0.012 |
| NULL-H (class reassign) | 0.460 | 1.000 | 1.000 | 0.000 |
| NULL-I d=3 (latent) | 0.001 | 0.000 | 0.000 | 0.000 |
| NULL-I d=4 (latent) | 0.001 | 0.000 | 0.000 | 0.000 |
| NULL-I d=5 (latent) | 0.001 | 0.000 | 0.000 | 0.000 |

## Dimensional Necessity

Latent feature models with 3-5 binary features produce near-zero incompatibility (0.001 vs 0.460 observed). This confirms C475's implication that MIDDLE co-occurrence structure requires high-dimensional constraints, not low-dimensional grouping.

## Scope Note

C475 reports 95.7% incompatibility at A-scope record level with ~1,187 MIDDLEs. This test measures 46.0% at B-line level with 85 MIDDLEs. Different scope, but null-model comparison is apples-to-apples within B.

## Provenance

- Refines: C475 (MIDDLE incompatibility), C476 (hub rationing)
- Method: `phases/FINGERPRINT_UNIQUENESS/scripts/t3_compositional_sparsity.py`
- Results: `phases/FINGERPRINT_UNIQUENESS/results/t3_composition.json`
