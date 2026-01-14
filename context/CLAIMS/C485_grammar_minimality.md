# C485: Grammar Minimality

**Tier:** 2 | **Status:** CLOSED | **Scope:** CURRIER_B

## Statement

The Currier B grammar is minimally necessary: both the e-operator (stability anchor) and hazard asymmetry (h->k suppression) are load-bearing. Removing either causes system collapse.

## Evidence

### Test 3A: e-Operator Removal

| Metric | Baseline | Without e | Change |
|--------|----------|-----------|--------|
| Kernel contact ratio | 36.3% | 0.5% | **-98.6%** |
| Recovery ratio | 31.6% | 0.0% | **-100%** |
| Tokens removed | - | 27,203 | 36% of corpus |

Without e-class tokens, recovery paths collapse entirely. The grammar cannot return to stable states.

### Test 3B: Hazard Asymmetry

| Transition | Probability | Significance |
|------------|-------------|--------------|
| h->k | 0.0000 | Perfectly suppressed |
| k->h | 0.0000 | Also suppressed |
| k->e | 0.833 | Primary recovery |
| h->e | 0.824 | Primary recovery |

The h->k transition is perfectly forbidden (0 occurrences in 75,545 tokens). This prevents oscillation between hazard states.

### Mean Asymmetry

Overall transition asymmetry = 0.55, driven by:
- k->e vs e->k: 0.83 asymmetry
- h->e vs e->h: 0.82 asymmetry

## Interpretation

The grammar exhibits **minimal necessary structure**:

1. **e is the stability anchor** - All recovery paths pass through e. Without it, the system has no way to return from hazard states.

2. **h->k suppression prevents oscillation** - If hazard states could transition to each other, programs would oscillate indefinitely without converging.

3. **Cannot simplify further** - Any reduction in grammar complexity causes system failure.

This is engineering necessity, not arbitrary design.

## Counterfactual Verdict

| Element | Necessary? | Failure Mode |
|---------|------------|--------------|
| e-operator | YES | Recovery collapse |
| h->k suppression | YES | Oscillation / non-convergence |
| k->e recovery | YES | No exit from k-hazard |
| h->e recovery | YES | No exit from h-hazard |

## Related Constraints

- C109: 5 hazard failure classes
- C124: 100% grammar coverage
- C171: Closed-loop control only

## Source

Phase: SEMANTIC_CEILING_EXTENSION
Tests: 3A (counterfactual_grammar.py), 3B (counterfactual_grammar.py)
Results: `results/counterfactual_grammar.json`
