# REGIME_LINE_SYNTAX_INTERACTION Phase

## Objective

Test whether the line-level execution syntax (SETUP->WORK->CHECK->CLOSE per C556) varies by REGIME. This addresses a gap: C545 shows REGIME affects class frequencies, but no prior work tested whether REGIME affects WHERE roles appear within lines.

## Key Finding

**LINE SYNTAX IS REGIME-INVARIANT**

All 5 roles (CC, EN, FL, FQ, AX) show no significant positional variation by REGIME. REGIME explains only 0.13% of position variance (vs 1.5% for PHASE per C815).

This CONFIRMS C124 (grammar universality). REGIME encodes execution requirements (what to do), not syntax structure (how to organize instructions).

## Results Summary

### T1: CC Position by REGIME
- daiin initial-bias: 22.7% - 33.9% across REGIMEs (p=0.65 NS)
- daiin mean position: 0.38 - 0.45 across REGIMEs (p=0.68 NS)
- **Verdict: INVARIANT**

### T2: FL Position by REGIME
- FL mean position: 0.55 - 0.60 across REGIMEs (p=0.41 NS)
- FL final-bias: 13.3% - 19.1% across REGIMEs (p=0.58 NS)
- **Verdict: INVARIANT**

### T3: ENERGY Position by REGIME
- EN mean position: 0.476 - 0.487 across REGIMEs (p=0.59 NS)
- EN_QO and EN_CHSH both invariant
- **Verdict: INVARIANT**

### T4: Bigrams by REGIME
- Most bigrams invariant
- **or->aiin shows significant variation** (p<0.0001): REGIME_4 uses 6x more than REGIME_1
- But this is frequency, not position
- daiin->CHSH lane routing invariant (p=0.63)

### T5: Full Line Syntax Profile
- All 5 roles: p > 0.4 (INVARIANT)
- **Verdict: LINE SYNTAX IS REGIME-INVARIANT**

### T6: Variance Decomposition
- Mean eta^2 = 0.0013 (0.13%)
- Compare C815: 1.5% (PHASE effect)
- REGIME explains 11x less variance than PHASE
- **Verdict: REGIME is not a syntax axis**

## Scripts

| Script | Purpose | Key Finding |
|--------|---------|-------------|
| t1_cc_position_by_regime.py | CC positional invariance | All NS |
| t2_fl_position_by_regime.py | FL positional invariance | All NS |
| t3_energy_position_by_regime.py | EN positional invariance | All NS |
| t4_bigram_by_regime.py | Bigram frequency | or->aiin varies |
| t5_line_syntax_profile.py | Full role profile | 5/5 INVARIANT |
| t6_syntax_variance_decomposition.py | Variance analysis | 0.13% explained |

## Constraints Produced

| # | Name | Finding |
|---|------|---------|
| C821 | Line Syntax REGIME Invariance | All roles invariant, confirms C124 |
| C822 | CC Position REGIME Invariance | REGIME affects frequency, not placement |
| C823 | Bigram REGIME Partial Variation | or->aiin varies, daiin->CHSH invariant |

## Architectural Interpretation

REGIME operates on a **different axis** than line syntax:

```
REGIME axis: WHAT to do (class enrichment)
  - REGIME_1: More ENERGY operations
  - REGIME_3: More CC operations (1.83x)
  - REGIME_4: Balanced operations

LINE SYNTAX axis: WHERE to put it (position template)
  - Universal: SETUP -> WORK -> CHECK -> CLOSE
  - Independent of REGIME
```

This clean separation supports the model that:
1. Grammar is universal (C124)
2. REGIMEs are execution requirement specifications
3. The control loop template is invariant

## Dependencies

- C124 (grammar universality)
- C545 (REGIME class profiles)
- C556 (line syntax template)
- C815 (phase position significance)
- C816-C820 (CC control loop integration)

## Data Sources

- `results/regime_folio_mapping.json`
- `phases/CLASS_COSURVIVAL_TEST/results/class_token_map.json`
- `scripts/voynich.py` (Transcript, Morphology)
