# C1434: m-Terminal Low-Diversity Closure Specialization

**Tier:** 2
**Scope:** B, MIDDLE, atom, m-terminal, closure, diversity, C1393, C1394, C1427
**Phase:** 521 (M_TERMINAL_ANOMALY)
**Date:** 2026-03-05

## Claim

m-terminal MIDDLE atom has only 10 types (289 tokens, 1.25% of B). Two MIDDLEs (`am` 60.2%, `m` 26.3%) account for 86.5%. Vocabulary diversity is the lowest of any terminal atom (10 types vs y: 33, l: 48, r: 49, h: 188). 95.9% bare (no suffix). m is a structurally specialized closure terminal with minimal internal diversification.

## Evidence

### Inventory

| MIDDLE | Count | % | Category | HEAD |
|--------|-------|---|----------|------|
| am | 174 | 60.2% | TRANSITION | a |
| m | 76 | 26.3% | TRANSITION | (none) |
| om | 25 | 8.7% | OPERATION | o |
| im | 8 | 2.8% | STAGING | (none) |
| faim | 1 | 0.3% | TRANSITION | (none) |
| lm | 1 | 0.3% | STAGING | (none) |
| kam | 1 | 0.3% | TRANSITION | k |
| eam | 1 | 0.3% | TRANSITION | e |
| opom | 1 | 0.3% | OPERATION | o |
| fam | 1 | 0.3% | TRANSITION | (none) |

### Terminal atom diversity comparison

| Terminal | Types | Tokens | Types/100 tokens |
|----------|-------|--------|-----------------|
| m | 10 | 289 | 3.5 |
| y | 33 | 4,780 | 0.7 |
| l | 48 | 2,568 | 1.9 |
| r | 49 | 1,963 | 2.5 |
| h | 188 | 1,283 | 14.7 |
| n | 42 | 2,148 | 2.0 |

Even adjusting for sample size, m has the lowest diversity of any terminal.

### MOD stack

Only 3/289 tokens have a modifier between HEAD and m (faim, opom, fam). m operates as a near-bare terminal — HEAD + m with no intermediate structure.

## Interpretation

m is the most structurally constrained terminal atom. It forms a tiny, closed vocabulary of closure operators. The a-HEAD dominance (60.2%) produces `am` as the canonical closure MIDDLE, with bare `m` as the next option. The near-absence of modifiers and extreme suffix suppression (C1438) make m-terminal MIDDLEs self-contained closure signals.

## Falsification Criteria

1. If m-terminal vocabulary exceeds 20 distinct types
2. If suffix rate exceeds 15%

## Method

- 23,096 Currier B tokens (H-track, labels excluded)
- Terminal atom extracted from MIDDLE decomposition per C1393-C1394
- Diversity compared across all 8 terminal atoms

**Script:** `phases/M_TERMINAL_ANOMALY/scripts/m_terminal_analysis.py`
**Results:** `phases/M_TERMINAL_ANOMALY/results/m_terminal_analysis.json`

## Dependencies

- C1393 (compound MIDDLE composition grammar)
- C1394 (instruction encoding architecture)
- C1427 (line-final transition profile — source of 196x finding)
