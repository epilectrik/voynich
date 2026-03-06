# C1534: PREFIX Uses 15 Characters in Three-Tier Positional Classification Identical Across All Systems

**Tier:** 2
**Scope:** GLOBAL, PREFIX, atom, positional, inventory, MODIFIER, BASE, DUAL, cross-system, C1218, C1499, C1504
**Phase:** PREFIX_ATOM_TAXONOMY (Phase 544)
**Date:** 2026-03-06

## Claim

PREFIX decomposes into 15 characters organized in three positional tiers: 7 MODIFIER atoms {c,d,f,p,q,s,y} occupying position-0 (96-100%), 2 BASE atoms {e,h} occupying position-final (100%), and 6 DUAL atoms {a,k,l,o,r,t} occupying both positions. Character inventory is identical across all three systems (Jaccard=1.000 for A-B, A-AZC, B-AZC). No PREFIX-exclusive characters exist; all 15 are shared with MIDDLE. PREFIX is a strict 15-character subset of MIDDLE's 20-character alphabet. Length distribution: 94% two-character, 6% three-character, 0% singleton.

## Evidence

### Positional classification

| Tier | Characters | Position-0 Rate | Position-Final Rate | Count |
|---|---|---|---|---|
| MODIFIER | d, f, p, q, y | 100% | 0% | 5 categorical |
| MODIFIER | c | 79.3% | 0% (20.7% medial) | 1 near-categorical |
| MODIFIER | s | 97.5% | 0% (2.5% medial) | 1 near-categorical |
| BASE | e, h | 0% | 100% | 2 categorical |
| DUAL | a | 11.2% | 88.8% | mostly-final |
| DUAL | r | 10.8% | 89.2% | mostly-final |
| DUAL | k | 23.1% | 76.9% | mostly-final |
| DUAL | t | 31.9% | 68.1% | balanced-final |
| DUAL | l | 39.6% | 60.4% | balanced |
| DUAL | o | 48.6% | 51.4% | balanced |

### Cross-system identity

| Pair | Character Jaccard | Base JSD | Modifier JSD |
|---|---|---|---|
| A-B | 1.000 | 0.011 | 0.037 |
| A-AZC | 1.000 | 0.040 | 0.058 |
| B-AZC | 1.000 | 0.046 | 0.073 |

### Token counts

30,938 prefixed tokens analyzed (A=9,257, B=19,232, AZC=2,449). 35 unique PREFIX types across all systems.

## Interpretation

PREFIX has a MODIFIER+BASE compositional grammar distinct from MIDDLE's HEAD+MOD*+TERM structure but drawing from the same shared alphabet. The three-tier classification confirms C1218 with quantitative precision. Cross-system identity extends C1499 (shared substrate) and C1504 (modifier universality) to the PREFIX compositional layer. The absence of PREFIX-exclusive characters means PREFIX achieves its distinct function through COMBINATORIAL SELECTION from the shared pool, not through a private alphabet.

## Falsification Criteria

1. If any system uses a PREFIX character absent from the other two
2. If MODIFIER atoms appear at position-final at >5% rate
3. If BASE atoms appear at position-0 at >1% rate

## Source

`phases/PREFIX_ATOM_TAXONOMY/results/prefix_atom_taxonomy.json`
