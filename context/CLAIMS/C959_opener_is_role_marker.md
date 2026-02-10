# C959: Opener Is Role Marker, Not Instruction Header

**Tier:** 2 | **Scope:** B | **Phase:** LINE_CONTROL_BLOCK_GRAMMAR

## Statement

The opening token's ROLE modestly predicts line body composition (29.2% accuracy, 1.46x chance), but the specific opener TOKEN adds no predictive power beyond its role. Lines opened by `daiin` are body-indistinguishable from lines opened by other CORE_CONTROL tokens.

## Evidence

- Nearest Centroid classifier (LOO): role_level accuracy = 29.2% (chance = 20.0%)
- Below 40% PASS threshold but above chance
- Token-level JSD: all 5 top openers within 0.97-1.09x of shuffle mean; zero significant
- Opener tokens tested: daiin (85x), saiin (48x), dain (34x), sain (34x), qokeedy (31x)
- Confusion matrix: substantial cross-role confusion; ENERGY_OPERATOR best-classified (38.9%)

## Interpretation

The opener is a role marker, not a specific instruction header. Lines begin with "this kind of operation" (a role), not "this specific instruction." Token substitution within a role is free at the opener position.

## Provenance

- `phases/LINE_CONTROL_BLOCK_GRAMMAR/scripts/04_opener_instruction_header.py`
- Related: C557, C543
