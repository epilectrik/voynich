# C1438: m-Terminal Categorical Suffix Suppression

**Tier:** 2
**Scope:** B, MIDDLE, atom, m-terminal, suffix, suppression, C1420, C1408, C1394
**Phase:** 521 (M_TERMINAL_ANOMALY)
**Date:** 2026-03-05

## Claim

m-terminal tokens have 4.2% suffix rate vs 48.3% overall (11.5x suppression ratio). This is the most extreme suffix suppression of any MIDDLE terminal atom. m-terminal MIDDLEs are self-contained operators that do not accept suffix parameterization.

## Evidence

### Suffix rates

| Measure | m-terminal | Overall |
|---------|-----------|---------|
| Suffix rate | 4.2% | 48.3% |
| Bare rate | 95.9% | 51.7% |
| Suppression ratio | 11.5x | -- |

### Suffixed m-terminal tokens (exhaustive)

Only 12 m-terminal tokens carry any suffix: 3 -dy, 3 -om, 2 -y, and singletons. The sample is too small for suffix mode analysis (5 Mode A, 7 Mode B).

### Comparison to other suppression effects

- ARTICULATOR suffix suppression: 38.1% vs 64.3% (C1420) = 1.69x suppression
- m-terminal suffix suppression: 4.2% vs 48.3% = 11.5x suppression
- m's suppression is 6.8x stronger than ARTICULATOR suppression

### Mechanism

The m atom acts as a self-contained closure signal that resists suffix attachment. This is consistent with m's near-pure TRANSITION category (C1436) — TRANSITION vocabulary is inherently suffix-poor because state-change operations do not need parametric suffix modulation.

## Interpretation

m-terminal is the most suffix-resistant MIDDLE terminal in the grammar. The 95.9% bare rate means m-terminal MIDDLEs function as unmodified closure operators. They encode a fixed operation (body-line closure) without the suffix variation that other terminals use for parametric specification (Mode A) or continuation markers (Mode B).

## Falsification Criteria

1. If m-terminal suffix rate exceeds 15%

## Method

- 289 m-terminal tokens checked for suffix presence via Morphology
- Overall suffix rate computed across all 23,096 B tokens

**Script:** `phases/M_TERMINAL_ANOMALY/scripts/m_terminal_analysis.py`
**Results:** `phases/M_TERMINAL_ANOMALY/results/m_terminal_analysis.json`

## Dependencies

- C1420 (ARTICULATOR suffix suppression)
- C1408 (suffix has HEAD->TERM compositional structure)
- C1394 (instruction encoding architecture)
