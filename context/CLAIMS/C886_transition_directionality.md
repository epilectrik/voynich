# C886: Transition Probability Directionality

**Tier:** 2
**Scope:** B
**Phase:** A_B_CORRESPONDENCE_SYSTEMATIC

## Constraint

Transition probabilities P(A→B) and P(B→A) are uncorrelated (r = -0.055). Individual bigram frequencies are directional - knowing how often class A precedes class B provides no information about how often B precedes A. This is distinct from conditional entropy symmetry (C391) and indicates the grammar has symmetric constraints but directional execution paths.

## Evidence

Empirical test comparing forward vs reversed transition matrices:

| System | KL Divergence | Transition Correlation |
|--------|--------------|----------------------|
| **Voynich B** | **89.2** | **-0.055** |
| Procedural (synthetic) | 9.8 | 0.999 |
| Narrative (synthetic) | 13.3 | 0.991 |
| Shuffled random | 89.3 | -0.140 |

**Methodology:**
- Built 49x49 transition matrix from Voynich B instruction classes
- Computed correlation between P(A→B) and P(B→A) for all class pairs
- Compared to synthetic procedural text (loop-based), narrative text (directional), and shuffled baseline

## Interpretation

The combination of C391 (symmetric conditional entropy) and C886 (uncorrelated transition probabilities) is diagnostic:

| Property | Voynich | Natural Language | Procedural Text |
|----------|---------|------------------|-----------------|
| Conditional entropy symmetry | Yes (1.00) | No (~0.85) | ~0.9 |
| Transition probability correlation | **Near-zero** | High (~0.99) | High (~0.99) |

**What this means:**
- Grammar constraints work bidirectionally (you can check validity from either direction)
- Actual execution paths are directional (A→B and B→A have different functional meanings)
- This excludes both natural language (which has correlated transitions due to syntax) and simple procedural text (which has correlated transitions due to operational pairings)

**Control system interpretation:**
A control loop has symmetric physics (temperature can rise or fall) but asymmetric execution (heating and cooling cycles have different frequency patterns). The grammar specifies what transitions are *legal*; the execution determines which are *used*.

## Relationship to C391

C391 and C886 are complementary, not contradictory:

| Constraint | Measures | Finding |
|------------|----------|---------|
| C391 | Predictability symmetry | Equal from past or future |
| C886 | Frequency symmetry | Not equal - directional |

Together they characterize a **constraint-satisfaction grammar with directional execution** - rules are symmetric, usage is asymmetric.

## What This Excludes

1. **Natural language** - has asymmetric entropy AND correlated transitions
2. **Simple procedural text** - has ~symmetric entropy AND correlated transitions
3. **Symmetric Markov chains** - would have correlated transitions
4. **Random shuffled text** - would have uncorrelated transitions BUT also asymmetric entropy

Voynich's combination (symmetric entropy + uncorrelated transitions) is rare and diagnostic.

## Provenance

- Script: `phases/A_B_CORRESPONDENCE_SYSTEMATIC/scripts/112_time_reversal_test.py`
- Depends: C391 (conditional entropy symmetry)
- Related: C389 (bigram-dominant local determinism)

## Status

CONFIRMED - Empirical test with synthetic baselines establishes directional execution within symmetric constraint grammar.
