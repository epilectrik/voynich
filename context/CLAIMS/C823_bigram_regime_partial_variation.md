# C823: Bigram REGIME Partial Variation

## Constraint

Most key bigrams are REGIME-invariant, but **or->aiin shows significant REGIME variation** (chi2=24.56, p<0.0001):
- REGIME_1: 0.89 per 1000
- REGIME_2: 2.51 per 1000
- REGIME_3: 2.46 per 1000
- REGIME_4: 5.41 per 1000 (6.1x REGIME_1)

This is the **only significant REGIME effect** found in line syntax testing.

## Evidence

### Key Bigrams by REGIME

| Bigram | R1 rate | R2 rate | R3 rate | R4 rate | chi2 | p |
|--------|---------|---------|---------|---------|------|---|
| or->aiin | 0.89 | 2.51 | 2.46 | 5.41 | 24.56 | <0.0001 *** |
| ol->chedy | 1.51 | 0.36 | 0.55 | 0.34 | 5.99 | 0.11 NS |
| daiin->CHSH | 51.4% | 37.1% | 52.0% | 42.6% | 1.74 | 0.63 NS |

Rates are per 1000 bigrams.

### Interpretation

or->aiin is the strongest role-transition bigram (C561). Its REGIME variation suggests:
- REGIME_4 (precision mode) uses this transition 6x more than REGIME_1
- This may reflect REGIME_4's balanced, precise execution style
- But this is a FREQUENCY effect, not a POSITIONAL effect

The daiin->CHSH lane routing (C817) is REGIME-invariant (p=0.63), confirming that CC lane assignment is universal.

## Provenance

- Phase: REGIME_LINE_SYNTAX_INTERACTION
- Script: t4_bigram_by_regime.py
- Related: C561 (or->aiin bigram), C817 (CC lane routing)

## Tier

2 (Validated Finding)
