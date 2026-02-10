# C960: Boundary Vocabulary Is Open

**Tier:** 2 | **Scope:** B | **Phase:** LINE_CONTROL_BLOCK_GRAMMAR

## Statement

Line-initial and line-final positions draw from nearly the full Currier B vocabulary. Boundary positions are NOT governed by small closed token sets.

## Evidence

- Initial position: 1,145 unique token types, Gini = 0.470 (below 0.60 threshold)
- Final position: 1,127 unique types, Gini = 0.471
- Shuffle Gini: 0.506 (real is LESS concentrated than random, ratio 0.93x)
- 663 tokens needed to cover 80% of openers; 1,025 for 95%
- Top opener `daiin` covers only 3.5% of lines

## Interpretation

Any token of the appropriate role can open or close a line. There is no small "boundary vocabulary" — the system uses role-level routing, not lexical gatekeeping, to control line boundaries.

## Provenance

- `phases/LINE_CONTROL_BLOCK_GRAMMAR/scripts/05_opener_closer_constraint_sets.py`
- Related: C357, C543
