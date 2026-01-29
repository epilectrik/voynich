# CONTROL_LOOP_SYNTHESIS Phase

## Objective

Synthesize the three characterized control zones (KERNEL, LINK, FL) into a unified control loop model. Test integration, transitions, and predictive power.

## Key Findings

### LINK-FL Non-Adjacency (C810)

Direct LINK→FL transitions are rare (0.70x expected), confirming LINK and FL are complementary phases:
- LINK precedes FL: 8.9% (baseline 13.2%, 0.67x)
- FL follows LINK: 3.3% (baseline 4.7%, 0.70x)

There is typically intervening processing between monitoring and escape.

### FL Chaining (C811)

FL chains at 2.11x enrichment - escape is multi-step, not single-token:
- FL→FL: 9.9% (baseline 4.7%)
- FL→KERNEL: 59.4% (baseline 69.1%, 0.86x neutral)

Extended escape sequences, with neutral loop closure.

### HT Novel MIDDLE Combinations (C812)

HT uses MIDDLE combinations distinct from classified tokens:
- 11.19% of HT-HT pairs use "novel" combinations (both MIDDLEs in classified, pair not seen)
- Only 14.4% of HT-HT pairs are also seen in classified adjacencies
- 90.7% of HT MIDDLEs are exclusive to HT vocabulary

**Note:** This is NOT a C475 violation. C742 confirms HT obeys C475 forbidden pairs at 0.44%. C812 measures a different thing: HT uses different combinations than classified tokens, but doesn't violate the forbidden pair rules.

### Canonical Phase Ordering (C813)

Within lines, phases follow a canonical order:

**LINK (0.476) → KERNEL (0.482) → FL (0.576)**

- LINK earliest (monitoring setup)
- KERNEL middle (processing)
- FL latest (escape if needed)

FL is significantly later than both LINK and KERNEL (p < 0.0001).

### Kernel-Escape Inverse (C814)

KERNEL density is the strongest negative predictor of FL:
- KERNEL vs FL: rho = -0.528, p < 0.0001
- High kernel = stable program (low escape)
- Low kernel = unstable (high escape needed)

### Phase Position Significance (C815)

Phases have significant positional preferences:
- ANOVA F = 70.28, p < 10⁻⁷³

But effect is weak:
- Eta² = 0.015 (only 1.5% variance explained)
- Prediction improvement: 0.8%

The control loop is **temporally flexible**, not rigidly positional.

## Scripts

| Script | Purpose | Key Finding |
|--------|---------|-------------|
| t1_link_fl_interface.py | LINK-FL transitions | 0.70x both directions |
| t2_loop_closure.py | FL→KERNEL path | Neutral (0.86x), FL chains 2.11x |
| t3_ht_c475_compliance.py | HT grammar compliance | 11.19% novel combinations |
| t4_line_phase_sequence.py | Phase ordering | LINK→KERNEL→FL |
| t5_folio_program_profiles.py | Folio predictors | KERNEL rho=-0.528 |
| t6_sequence_prediction.py | Position prediction | 1.5% variance explained |

## Constraints Produced

| # | Name | Finding |
|---|------|---------|
| C810 | LINK-FL Non-Adjacency | Direct transitions rare (0.70x) |
| C811 | FL Chaining | Extended escape sequences (2.11x) |
| C812 | HT Novel MIDDLE Combinations | 11.19% novel pairs (not C475 violation) |
| C813 | Canonical Phase Ordering | LINK→KERNEL→FL |
| C814 | Kernel-Escape Inverse | rho=-0.528 |
| C815 | Phase Position Significance | Significant but weak (1.5%) |

## Architectural Interpretation

The control loop model:

```
[LINK monitoring] → [KERNEL processing] → [FL escape if needed]
     (early)            (throughout)           (late)
```

Key insights:
1. **Phases are complementary, not adjacent**: LINK-FL don't directly transition
2. **Escape is extended**: FL chains (2.11x), not single-token recovery
3. **HT is combinatorially distinct**: Obeys C475 forbidden pairs but uses different MIDDLE combinations
4. **Kernel predicts stability**: High kernel = low escape need
5. **Flexible timing**: Phases have preferences but overlap extensively

## Dependencies

- C804-C809 (LINK architecture)
- C770-C781 (FL architecture)
- C089, C103-C105 (Kernel)
- C475 (MIDDLE incompatibility)
- C360 (Line = control block)

## Data Sources

- `phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json`
- `scripts/voynich.py` (Transcript, Morphology)
