# C1354: Dark Grammar Influence Is Local, Not Contextual

**Tier:** 2
**Scope:** B
**Phase:** LAYERED_GRAMMAR_TEST (473)

## Constraint

Dark MIDDLEs constrain their immediate successor token (C1351: entropy 2.59 vs 4.18 bits) but do NOT alter line-level bridge-to-bridge transition statistics. Conditional MI(bridge_next; dark_presence | bridge_current) = 0.098 bits, indistinguishable from permutation null (0.101 bits, p=0.90). Removing dark tokens from lines does not change bridge transition entropy (conditional entropy difference = +0.73 bits, null = +0.72 bits, p=0.38). Dark MIDDLEs operate as local inline signals affecting the next token, not as context-setters for broader execution regimes.

## Evidence

From layered_grammar_test.py tests T3 and T5 (13,645 bridge-to-bridge transitions):

**T3: Dark presence does not condition bridge transitions:**

| Metric | Value |
|--------|-------|
| Transitions with dark on line | 6,337 |
| Transitions without dark | 7,308 |
| Transitions with dark between | 885 |
| Conditional MI(next; dark_pres | current) | 0.098 bits |
| Null mean MI | 0.101 bits |
| Perm p | 0.90 |

**T5: Dark removal does not genericize transitions:**

| Metric | Value |
|--------|-------|
| Conditional entropy, dark-between transitions | 3.754 bits |
| Conditional entropy, no-dark lines | 4.486 bits |
| Difference | +0.732 bits |
| Null mean difference | +0.720 bits |
| Perm p | 0.379 |

The 0.73-bit difference between dark-between and no-dark transitions exists but is entirely explained by baseline (null = 0.72 bits). Dark tokens happen to occur on lines with lower transition entropy, but they don't cause it.

## Interpretation

The three-tier grammar model (dark=context → bridge=execution → suffix=mode) is falsified in its strong form. Dark MIDDLEs influence grammar only at the immediate next-token level (C1351), not at the line-level transition regime. They are inline annotations — each dark token constrains what immediately follows it, but that constraint doesn't propagate further into the bridge-to-bridge transition chain.

This preserves C405 (HT causal decoupling) at the transition level while refining it: dark tokens have very local influence (next token) that does not constitute "grammar participation" in the transition-matrix sense.

## Provenance

- layered_grammar_test.json: tests T3, T5
- Extends: C1351 (dark successor entropy is narrow — confirmed, but shown to be LOCAL not CONTEXTUAL)
- Extends: C405 (HT causal decoupling — confirmed at transition level, dark presence doesn't alter transitions)
- Falsifies: strong three-tier grammar model (dark tokens are not a grammar tier)

## Status

CONFIRMED — dark grammar influence is local (next-token only), not contextual (line-level). The three-tier grammar model is falsified.
