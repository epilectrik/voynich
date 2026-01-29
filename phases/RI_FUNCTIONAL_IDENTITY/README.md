# RI_FUNCTIONAL_IDENTITY

**Status:** COMPLETE | **Constraints:** C710-C718 | **Scope:** A, A-B

## Objective

Determine RI's functional role in the A architecture. Five hypotheses tested:
- H1: Record-keeping (serial/reference numbers)
- H2: Sequential addressing (RI indexes B programs)
- H3: Constraint refinement (RI modifies PP filtering)
- H4: Independent content (RI is A's payload, PP is compatibility interface)
- H5: Structural scaffolding (RI marks boundaries/closure)

Extended with line-type comparison and activation model testing.

## Key Findings

**RI Function Tests (C710-C716): 3/7 PASS — MIXED.** H4 (independent content) best supported on independence tests, but RI is sparser than predicted (87.3% singletons). H2 (addressing) and H3 (refinement) firmly falsified.

**PP Line-Type Homogeneity (C717):** PP-pure lines (63.3%) and RI-bearing lines (36.7%) draw from the SAME PP vocabulary pool. RI-exclusive PP MIDDLEs are a sampling artifact (permutation test: null=9.4, observed=8.9, 106% explained by sampling).

**RI Pipeline Invisibility (C718):** PP-pure lines alone recover 90.1% of full folio B class survival. The 3.9 "RI-gated" classes per folio are random (different each time, zero gated in >25% of folios). RI is structurally invisible to the execution pipeline.

## Test Results

### RI Function Tests (T1-T7)

| Test | Constraint | Key Number | Result |
|------|-----------|------------|--------|
| T1: Positional complementarity | C710 | d=0.12 (too small) | FAIL |
| T2: RI vocabulary density | C711 | rho=0.419 (below PP's 0.588) | FAIL |
| T3: Singleton vs repeater | C712 | KS p=0.16 (same behavior) | PASS |
| T4: Adjacent line RI similarity | C713 | Jaccard 0.008 (near zero) | FAIL |
| T5: Line-final RI morphology | C714 | 143 unique/156 final (no specialization) | FAIL |
| T6: RI-PP independence | C715 | rho=-0.052, diversity 0.74 | PASS |
| T7: Cross-folio RI reuse | C716 | ratio 1.04x (independent of PP) | PASS |

### Activation Model Test

| Condition | Mean Classes | Recovery |
|-----------|-------------|----------|
| PP-pure lines only | 35.9/49 | 90.1% |
| + best single RI line | 38.3/49 | 96.4% |
| + average RI line | 37.2/49 | 93.4% |
| Full folio | 39.8/49 | 100% |

### RI-Gated Class Analysis

- 46 classes ever RI-gated, but none in >25% of folios
- 3.9 RI-gated classes per folio (random each time)
- Sampling artifact confirmed: permutation null=9.4 vs observed=8.9

## Scripts

| Script | Tests | Output |
|--------|-------|--------|
| `ri_functional_tests.py` | T1-T7 (C710-C716) | `ri_functional_tests.json` |
| `line_type_comparison.py` | PP-pure vs RI-bearing (8 tests) | `line_type_comparison.json` |
| `activation_model_test.py` | Activation model (C717-C718) | `activation_model_test.json` |
| `ri_gated_classes.py` | RI-gated class analysis | `ri_gated_classes.json` |

## Constraints

| # | Name | Key Result |
|---|------|------------|
| C710 | RI-PP Positional Complementarity | d=0.12, too small for structural complementarity |
| C711 | RI Vocabulary Density | rho=0.419, sparse (6.6 types/folio vs 35.3 PP) |
| C712 | Singleton-Repeater Equivalence | Same behavior (KS p=0.16) |
| C713 | Adjacent Line RI Similarity | Near-zero (Jaccard 0.008) |
| C714 | Line-Final RI Profile | No morphological specialization |
| C715 | RI-PP Independence | rho=-0.052, orthogonal |
| C716 | Cross-Folio RI Reuse Independence | Reuse independent of PP (ratio 1.04) |
| C717 | PP Homogeneity Across Line Types | Same PP pool; RI-exclusive PP is artifact |
| C718 | RI Pipeline Invisibility | 90.1% recovery without RI; RI invisible to B |

## Data Dependencies

- `scripts/voynich.py` (canonical transcript library)
- `phases/A_INTERNAL_STRATIFICATION/results/middle_classes.json` (RI/PP sets)
- `phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json` (token-to-class)

## Cross-References

- C498 (RI vocabulary track): Confirmed and quantified
- C509 (PP/RI dimensional separability): Confirmed behaviorally
- C526 (RI lexical layer): Weakened by pipeline invisibility
- C703 (PP folio homogeneity): Extended to line-type dimension
- C704-C709 (folio-level filtering): Baseline for activation model
