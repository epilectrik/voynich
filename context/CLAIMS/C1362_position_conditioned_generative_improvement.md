# C1362: Position-Conditioned Model Improves Generation on All Metrics

**Tier:** 2
**Scope:** B, line, generative model, position
**Phase:** LINE_MICRO_GRAMMAR (Phase 474)
**Depends on:** C1025, C1156, C1358, C1359

## Statement

A position-conditioned Markov model (M2p: quintile-specific 49x49 transition matrices) outperforms the stationary M2 model on all 5 tested metrics. M2p reduces class distribution KL by 2.4x (0.156→0.064), transition JSD by 1.7x (0.213→0.126), positional entropy error by 1.6x (0.107→0.068), AXM self-transition error by 1.8x (0.045→0.025), and specialist-class positional accuracy by 2.5x (0.181→0.073). Verdict: 5/5 IMPROVEMENT.

## Evidence

| Metric | M2 | M2p | Improvement |
|--------|-----|-----|-------------|
| Per-quintile class KL | 0.156 | 0.064 | 2.4x |
| Per-quintile transition JSD | 0.213 | 0.126 | 1.7x |
| Per-class positional entropy | 0.107 | 0.068 | 1.6x |
| AXM self-transition match | 0.045 | 0.025 | 1.8x |
| Specialist-class accuracy | 0.181 | 0.073 | 2.5x |

**Generation protocol:** 1,000 synthetic lines per model, lengths sampled from real distribution (mean ~7.6 classified tokens per line). Transition matrices estimated from 1,890 lines with >=5 classified tokens.

## Structural Implication

The M2 model's primary blind spot was line position. Simply conditioning the same 49-class Markov chain on quintile position produces dramatically better synthetic lines across every measured dimension. This confirms that the transition gradient (C1359) is not just statistically significant but generatively important — it is the mechanism the stationary M2 model was missing. The improvement is achieved without adding new grammar rules; the grammar itself does not change by position (C1361), but the class FREQUENCIES from which it draws shift smoothly across the line (C1358).

## Caveat

M2p has not been tested against the original 15-test battery (C1025). The 5 metrics here are complementary, focused specifically on positional reproduction. Whether M2p improves on M2's existing 15-test pass rate requires separate validation.

**Results:** `phases/LINE_MICRO_GRAMMAR/results/line_micro_grammar.json`
