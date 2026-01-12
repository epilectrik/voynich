# Currier A Predictive Modeling Summary

**Date:** 2026-01-10
**Scope:** 4 modeling targets testing whether Currier A structure emerges from simple generative principles

---

## Executive Summary

| Target | Hypothesis | Result | Status |
|--------|-----------|--------|--------|
| T1: Token Generator | Factored model P(token) = P(PREFIX) * P(MIDDLE|PREFIX) * P(SUFFIX|PM) | 84.5% type, 98% token | PARTIAL |
| T2: Sister-Pair Classifier | ch/sh choice predictable from context | 70.9% max (75% target) | NULL |
| T3: Multiplicity Distribution | Simple stochastic model fits 3x-dominant pattern | KL=0.045, mode=2 | PARTIAL |
| T4: Clustering HMM | 2-state Markov explains clustering | r=0.236 exact match | SUCCESS |

---

## Target 1: Compositional Token Generator

**Hypothesis:** P(token) = P(PREFIX) * P(MIDDLE|PREFIX) * P(SUFFIX|PREFIX,MIDDLE)

**Results:**
- Type coverage: 84.5% (target >90%) - FAIL
- Token coverage: 98.0% (target >85%) - PASS
- Perplexity ratio: 13.8% (target <30%) - PASS
- Novel types: 0% (no over-generation)

**Interpretation:** The factored model explains the bulk of token frequency but misses some rare type combinations. The 98% token coverage demonstrates that component reuse (PREFIX + MIDDLE + SUFFIX) captures the productive structure. The 15.5% missing types are sparse combinations that the model cannot generate.

**Constraint implication:** C267-C282 (compositional morphology) are validated - the structure IS compositional.

---

## Target 2: Sister-Pair Classifier

**Hypothesis:** ch vs sh (ok vs ot) choice is determined by contextual features.

**Results:**
- Baseline accuracy: 68.5% (majority class = ch)
- Best single feature (SUFFIX): 70.9%
- MIDDLE alone: 69.1%
- Combined model: 54.3% (worse than baseline!)
- Target: >75%

**Feature hierarchy observed:** SUFFIX > MIDDLE > section (contradicts C410 which predicts MIDDLE > SUFFIX)

**Interpretation:** Sister-pair selection has substantial unexplained variance. The ~2% improvement over baseline indicates weak determinism. This is consistent with C407-410 characterizing sister-pairs as "equivalence classes" rather than strictly conditioned alternates.

**Constraint implication:** The "section-conditioned at quire level" (C410) does not produce strong predictability. Sister-pair selection may involve factors not captured in transcription data (visual layout, scribal preference).

---

## Target 3: Multiplicity Distribution

**Hypothesis:** The 3x-dominant repetition distribution fits a simple stochastic model.

**Observed distribution:**
- 1x: 567 (35.9%)
- 2x: 416 (26.3%)
- 3x: 424 (26.8%)
- 4x: 148 (9.4%)
- 5x: 20 (1.3%)
- 6x: 5 (0.3%)

**Best fit:** Shifted Poisson with lambda=1.15
- KL divergence: 0.0450 bits (PASS <0.05)
- Chi-square: p<0.001 (FAIL)
- Mode: 2x (FAIL, observed is 1x with 3x close behind)

**Key anomaly:** 3x count (424) slightly exceeds 2x count (416). This is unusual - memoryless distributions predict monotonic decay.

**Interpretation:** The 3x ≈ 2x pattern suggests a non-random constraint or cognitive bias toward "groups of three." The distribution is approximately Poisson but with anomalous 3x enhancement.

**Constraint implication:** C258 ("3x dominance reflects human counting bias") is supported - the distribution deviates from random in a way consistent with cognitive preference.

---

## Target 4: Entry Clustering HMM

**Hypothesis:** 35% clustering rate and 0.24 autocorrelation explained by 2-state Markov process.

**Estimated transition matrix:**
```
P(singleton|singleton) = 0.73
P(cluster|singleton) = 0.27
P(singleton|cluster) = 0.49
P(cluster|cluster) = 0.51
```

**Results:**
- Autocorrelation: Observed 0.236, Simulated 0.236 (exact match)
- Run-length KL: 0.0495 bits (PASS <0.1)
- Chi-square: 0.00 (PASS)

**Interpretation:** The clustering pattern is fully explained by local dynamics alone. The ~50% "persistence" probability (P(1|1) = 0.51) means clusters have roughly even chance of continuing or breaking. The 27% "initiation" probability (P(1|0) = 0.27) controls cluster frequency.

**Constraint implication:** C424 (clustered adjacency) is explained by a simple 2-parameter model. No higher-order structure required.

---

## Overall Conclusions

### What IS explained by simple models:
1. **Token composition** (98% token coverage) - PREFIX + MIDDLE + SUFFIX factorization
2. **Entry clustering** (exact autocorrelation match) - 2-state Markov process
3. **Multiplicity shape** (KL=0.045) - approximately Poisson

### What is NOT explained:
1. **Rare type combinations** (15.5% of types) - structural gaps in component space
2. **Sister-pair selection** - substantial unexplained variance
3. **3x enhancement** - non-random preference for triadic grouping

### Implications for Currier A understanding:

The modeling confirms that Currier A has:
1. **Compositional, productive morphology** - not atomic vocabulary
2. **Local clustering dynamics** - entries influence their neighbors, but only weakly
3. **Bounded enumeration** - repetition follows approximately Poisson with cognitive bias

The failures suggest:
1. **Sister-pairs are equivalence classes** - selection involves factors beyond transcription
2. **3x preference is real** - cognitive or structural constraint, not random

---

## Files Generated

- `results/currier_a_modeling_data.json` - Phase 1 data preparation
- `results/currier_a_token_generator_eval.json` - Target 1 results
- `results/currier_a_sister_pair_classifier.json` - Target 2 results
- `results/currier_a_multiplicity_fit.json` - Target 3 results
- `results/currier_a_clustering_hmm.json` - Target 4 results

---

## Scripts Created

- `archive/scripts/currier_a_modeling_prep.py` - Data preparation
- `archive/scripts/currier_a_token_generator.py` - Target 1 model
- `archive/scripts/currier_a_sister_pair_model.py` - Target 2 model
- `archive/scripts/currier_a_multiplicity_model.py` - Target 3 model
- `archive/scripts/currier_a_clustering_hmm.py` - Target 4 model
