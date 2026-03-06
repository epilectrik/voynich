# C1457: e→y Narrow Vocabulary Dominance

**Tier:** 2
**Scope:** B, MIDDLE, atom, e-HEAD, y-terminal, vocabulary, dominance, C1393, C1394, C1448
**Phase:** 525 (EY_SAFE_PATHWAY)
**Date:** 2026-03-05

## Claim

The e→y frame (HEAD=e, TERMINAL=y, including extended ee→y) comprises 3,475 tokens (15.0% of the corpus) from only 7 unique MIDDLEs. Three forms dominate: edy (1,938 tokens, 55.8%), ey (889, 25.6%), eey (644, 18.5%), accounting for 99.9% of the population. e→y constitutes 49.6% of all e-HEAD tokens — half of all cooling-initiated operations terminate with the y (end) terminal. e-depth distribution: single-e = 2,831 tokens (81.5%), double-e = 644 tokens (18.5%). The d-modifier dominates (edy = 55.8%).

## Evidence

### MIDDLE inventory

| MIDDLE | Count | Fraction | Category |
|--------|-------|----------|----------|
| edy | 1,938 | 55.8% | OPERATION |
| ey | 889 | 25.6% | TRANSITION |
| eey | 644 | 18.5% | THERMAL |
| eody/echy/ecty | 4 | 0.1% | various |

### Population statistics

- Total e→y tokens: 3,475 (15.0% of 23,096 B tokens)
- Unique MIDDLEs: 7
- Top-3 coverage: 99.9%
- e→y as fraction of e-HEAD: 49.6%
- Single-e: 2,831 (81.5%), double-e: 644 (18.5%)

## Interpretation

The e→y frame is the single most common instruction frame in the grammar, yet uses an extremely narrow vocabulary. The d-modifier's dominance (creating edy = OPERATION) aligns with d as the containment/seal modifier (C1195) — the most common cooling operation is "cool-seal-end." The low vocabulary diversity despite high token count confirms e→y as a formulaic, highly stereotyped instruction.

## Falsification Criteria

1. If e→y drops below 10% of corpus
2. If more than 15 unique MIDDLEs appear in the e→y frame
3. If edy drops below 40% of e→y tokens

## Method

- 23,096 clean Currier B tokens decomposed via HEAD+MOD*+TERM encoding (C1393-C1394)
- e→y identified as HEAD={e, ee, eee...} with TERMINAL=y
- CategoryClassifier atom-level category assignment

**Script:** `phases/EY_SAFE_PATHWAY/scripts/ey_safe_pathway.py`
**Results:** `phases/EY_SAFE_PATHWAY/results/ey_safe_pathway.json`

## Dependencies

- C1393-C1394 (HEAD+MOD*+TERM instruction encoding)
- C1448 (HEAD x TERM frame hazard map — identified e→y as largest safe frame)
- C1195 (Atom gloss confidence tiers — d = seal/containment)
- C1197 (Only e and i repeat consecutively)
