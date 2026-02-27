# C1356: Dark MIDDLE Identity Adds Information Beyond PREFIX

**Tier:** 2
**Scope:** B
**Phase:** LAYERED_GRAMMAR_TEST (473)

## Constraint

Within each PREFIX group, dark MIDDLE identity significantly predicts successor instruction class beyond what PREFIX alone determines (conditional MI = 2.761 bits observed vs 2.683 bits null, Z=4.50, perm p<0.001). Across 13 PREFIX groups, dark MIDDLE identity carries MI ranging from 1.44 bits (so PREFIX) to 3.11 bits (sh PREFIX). The dark MIDDLE is not merely a PREFIX-carrier — its compound structure (C1141: 66.7% compound, mean 1.44 atoms) encodes specific grammar-successor constraints that PREFIX cannot explain.

## Evidence

From layered_grammar_test.py test T2 (980 dark→classified successor observations, 13 PREFIX groups):

| PREFIX | MI(dark_MID; succ_class) | N | MIDDLEs | Classes |
|--------|--------------------------|---|---------|---------|
| sh | 3.107 | 107 | 61 | 27 |
| ok | 3.067 | 28 | 20 | 16 |
| ch | 3.055 | 160 | 62 | 43 |
| BARE | 2.994 | 239 | 91 | 41 |
| ol | 2.900 | 35 | 20 | 21 |
| qo | 2.416 | 198 | 53 | 37 |
| ot | 2.126 | 27 | 11 | 19 |
| so | 1.444 | 31 | 8 | 14 |

| Metric | Value |
|--------|-------|
| Observed conditional MI | 2.761 bits |
| Null mean (permuted) | 2.683 bits |
| Z-score | 4.496 |
| Perm p | <0.001 |

## Interpretation

C1138 showed dark tokens use grammar-standard PREFIXes at 3.39x the rate of general HT. This raised the possibility that PREFIX alone accounts for dark tokens' grammar interaction. T2 falsifies this: dark MIDDLE identity carries genuine successor information beyond PREFIX. The compound structure of dark MIDDLEs (atoms like 'eed', 'lk', 'kee') specifies which grammar classes follow in ways that PREFIX cannot predict.

However, this is a local effect (T3/C1354 shows it doesn't propagate to line-level transitions). The dark MIDDLE constrains the immediate next grammar token, and this constraint is MIDDLE-specific (not just PREFIX-mediated), but the constraint is exhausted after one step.

## Provenance

- layered_grammar_test.json: test T2
- Extends: C1138 (dark uses grammar PREFIXes — but MIDDLE adds info beyond PREFIX)
- Extends: C1351 (dark successor entropy narrow — the narrowness is partly MIDDLE-driven, not just PREFIX)
- Bounded by: C1354 (local not contextual — the MIDDLE-specific effect doesn't propagate)

## Status

CONFIRMED — dark MIDDLE identity adds significant successor information beyond PREFIX (Z=4.50, perm p<0.001). The effect is MIDDLE-specific and local.
