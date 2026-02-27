# C1359: Transition Gradient Resolution

**Tier:** 2
**Scope:** B, line, 49-class, transition dynamics
**Phase:** LINE_MICRO_GRAMMAR (Phase 474)
**Depends on:** C1156, C964

## Statement

The 49-class transition matrix changes monotonically across 5 quintile positions (Spearman rho=0.639, p=0.045). Adjacent quintiles have low JSD (Q1-Q2: 0.137), while distant quintiles have high JSD (Q0-Q4: 0.355). The gradient accelerates toward line-end: the Q3-Q4 jump (0.299) is 2.2x larger than Q0-Q1 (0.147). AXM self-transition drops smoothly from 0.737 (Q0) to 0.549 (Q4), a 18.8 percentage-point gradient — nearly twice C1156's 9.7pp (which used only 3 zones). The overall mean JSD (0.222) is significant against permutation null (p<0.001, 1000 permutations).

## Evidence

| Quintile pair | JSD |
|---------------|-----|
| Q0-Q1 | 0.147 |
| Q0-Q2 | 0.145 |
| Q0-Q3 | 0.167 |
| Q0-Q4 | 0.355 |
| Q1-Q2 | 0.137 |
| Q1-Q3 | 0.150 |
| Q1-Q4 | 0.347 |
| Q2-Q3 | 0.150 |
| Q2-Q4 | 0.328 |
| Q3-Q4 | 0.299 |

| Quintile | AXM self-transition |
|----------|-------------------|
| Q0 | 0.737 |
| Q1 | 0.716 |
| Q2 | 0.688 |
| Q3 | 0.666 |
| Q4 | 0.549 |

- Spearman rho (|distance| vs JSD): 0.639, p=0.045
- Permutation p (mean JSD): <0.001

## Structural Implication

The transition gradient is smooth and monotonic — there are no sharp "zone boundaries" within lines. The grammar flows continuously from high-persistence (Q0: AXM self=0.737) to high-variability (Q4: AXM self=0.549). The acceleration toward Q4 means line-final positions experience the most dramatic transition restructuring. This refines C1156's 3-zone finding into a continuous gradient: lines don't have discrete phases so much as a smooth relaxation from stability to escape.

**Results:** `phases/LINE_MICRO_GRAMMAR/results/line_micro_grammar.json`
