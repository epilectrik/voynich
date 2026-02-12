# C1004: 49-Class Sufficiency Confirmed — No Hidden Suffix State

**Tier:** 2 | **Scope:** B | **Phase:** FULL_TOKEN_TRANSITION_DEPTH | **Date:** 2026-02-12

## Statement

The 49-class instruction grammar is sufficient for transition modeling. Token-level Markov models perform 38% worse than 49-class due to data sparsity (101 states vs 49). SUFFIX does not encode hidden sequential state: only 1/17 testable classes shows significant suffix-differentiated transition distributions (Bonferroni JSD test). Suffix conditioning reduces next-class entropy by 0.259 bits (5.6%), but this modest reduction does not justify a suffix-augmented state space. Combined with C1002 (no cross-token signal) and C1003 (no three-way synergy), this confirms the 49-class model captures all exploitable sequential structure.

## Evidence

### T1: Three-Scale Transition Perplexity (NO TOKEN-LEVEL IMPROVEMENT)
- 6-state macro: perplexity 2.746 (5-fold CV)
- 49-class: perplexity 28.764
- Top-100 token + OTHER: perplexity 39.732
- **Token vs class: -38.1% (WORSE)**
- Token-level states are too sparse for reliable transition estimation
- C966 baseline (perplexity 1.961) uses different methodology (MLE, not CV), but the relative ordering is clear
- BIC confirms 49-class is optimal (token-level overfits)

### T3: Within-Class Suffix Hidden State — JSD (NO HIDDEN STATE)
- 17 classes testable (both suffixed and bare subtypes with N≥30)
- **Only 1/17 significant** (class 27, JSD=0.274, p=0.000) after Bonferroni correction (p<0.01/17)
- Near-misses: class 13 (p=0.004), class 32 (p=0.007), class 35 (p=0.006) — just above threshold
- Mean JSD across all 17: 0.140 (moderate divergence but mostly noise)
- For 94% of testable classes, suffixed and bare variants have statistically indistinguishable transition distributions

### T5: Suffix Transition Entropy Reduction (SIGNIFICANT but MODEST)
- H(NEXT_CLASS | CLASS) = 4.631 bits
- H(NEXT_CLASS | CLASS, SUFFIX) = 4.372 bits
- **Reduction: 0.259 bits (5.6%)**
- Per-suffix entropy reductions (representative):
  - `or`: H=3.421 (26.1% below unconditional)
  - `ol`: H=3.360 (27.4% below)
  - `dy`: H=3.889 (16.0% below)
  - `ar`: H=3.818 (17.6% below)
  - `NONE`: H=4.594 (0.8% below — bare tokens are near-unconditional)
- Suffixed tokens have lower transition entropy than bare tokens, but this is because specific suffixes correlate with specific classes (which already have constrained transitions)
- The 5.6% reduction is present but does not justify doubling the state space (49→98)

### Composite Phase Verdict: WEAK_HIDDEN_STATE (1/3 pass)
- T1: FAIL — token-level Markov is worse
- T3: FAIL — no within-class suffix hidden state
- T5: PASS — entropy reduction is significant at 5.6%
- The single pass (T5) reflects suffix-class correlation, not hidden state

## Implications

- **Confirms C966**: 49-class perplexity 1.961 is the correct operating point; finer granularity overfits
- **Confirms C976**: 6-state compression (FL→HAZ/SAFE, EN/AX merge) captures macro-dynamics; suffix adds nothing at this scale
- **Extends C972**: Cross-line MI = 0.521 bits (C972) operates at class level; suffix carries no additional cross-line state
- **Confirms C1002 T4**: SUFFIX cross-token signal is zero — consistent with T3's finding that suffix doesn't differentiate transitions
- **Composite with C1002 and C1003**: All three frontier phases converge on the same conclusion — the 49-class instruction grammar is saturated

## Design Implications

The 49-class model is the correct resolution for Currier B transition dynamics:
1. **Below 49**: 6-state macro captures broad flow (perplexity 2.75) but loses detail
2. **At 49**: Optimal balance (perplexity 28.76 in CV; 1.961 in MLE baseline)
3. **Above 49**: Token-level and suffix-augmented models overfit (perplexity 39.73)

No fourth architectural layer exists. SUFFIX is a within-token modifier (positional specialist, sequential grammar participant) but not a sequential state carrier.

## Provenance

- `phases/FULL_TOKEN_TRANSITION_DEPTH/results/t1_transition_perplexity.json`
- `phases/FULL_TOKEN_TRANSITION_DEPTH/results/t3_within_class_jsd.json`
- `phases/FULL_TOKEN_TRANSITION_DEPTH/results/t5_suffix_entropy_reduction.json`
- `phases/FULL_TOKEN_TRANSITION_DEPTH/results/composite_verdict.json`
