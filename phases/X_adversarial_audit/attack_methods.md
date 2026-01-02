# Adversarial Audit - Attack Methods

*Generated: 2025-12-31T22:32*

---

## Overview

This document defines the five falsification-first tests used to attack the Voynich control system model. Each attack targets a specific structural claim from Phases 15-22.

---

## Attack 1: Kernel Collapse Test

**Target Claim:** Kernel nodes (k, h, e) have special structural importance beyond frequency.

**Null Hypothesis:** Kernel centrality emerges inevitably from token frequency distributions.

**Method:**
1. Compute character-level frequency distribution from Voynich corpus
2. Compute bigram distribution from Voynich corpus
3. Build Markov chain preserving unigram and bigram statistics
4. Generate 100 surrogate corpora via Markov sampling
5. Compute centrality (sum of bigram weights) for each surrogate
6. Measure how often surrogates reproduce k, h, e as top-3 centrality nodes

**Success Criterion:** If >80% of surrogates reproduce kernel top-3 ranking, kernel is a frequency artifact.

**Rationale:** If kernel structure is real, it should NOT be reproducible by frequency-matched random text.

---

## Attack 2: Cycle Illusion Test

**Target Claim:** Universal 2-cycle structure (CV=0.00 across all folios).

**Null Hypothesis:** Cycle detection is an artifact of folio segmentation or line-breaking.

**Method:**
1. Detect dominant cycle period via autocorrelation in original folio segmentation
2. Randomly re-segment corpus (random chunk sizes 50-500 words)
3. Re-segment with fixed 100-word chunks
4. Re-segment at 10-word "line" boundaries
5. Compare dominant cycle across all segmentation schemes

**Success Criterion:** If dominant cycle changes with segmentation, cycle structure is an artifact.

**Rationale:** A true structural invariant should persist regardless of how we segment the text.

---

## Attack 3: Grammar Minimality Test

**Target Claim:** 49 instruction classes and 17 forbidden transitions provide meaningful structure.

**Null Hypothesis:** A much simpler model preserves all key metrics.

**Method:**
1. Compute legality rate (percentage of non-forbidden transitions) with full 17 constraints
2. Compute legality rate with zero constraints (trivial grammar)
3. Compute legality rate with only top-5 most violated constraints
4. Collapse instruction classes by first character only
5. Compare compression ratios

**Success Criterion:** If trivial grammar achieves same legality, constraints are overfit.

**Rationale:** A meaningful grammar should demonstrably exclude sequences that actually occur.

---

## Attack 4: Random Constraint System Baseline

**Target Claim:** Monostate convergence and 2-cycle regulation are specific behaviors.

**Null Hypothesis:** Any constraint system with similar parameters shows similar behavior.

**Method:**
1. Generate 100 random constraint systems with 49 tokens and 17 forbidden transitions
2. Simulate random walks (1000 steps each) respecting constraints
3. Measure monostate convergence rate (>50% in single state over final window)
4. Detect dominant cycle period in random walks

**Success Criterion:** If random systems show >90% monostate + dominant 2-cycle, behavior is generic.

**Rationale:** If claimed behaviors arise generically, they carry no information about Voynich specifically.

---

## Attack 5: Independence of Folios Test

**Target Claim:** 83 folios represent 8 distinct recipe families with meaningful variation.

**Null Hypothesis:** Folios are redundant samples from a single stochastic generator.

**Method:**
1. Compute approximate mutual information between folio pairs
2. Compute coefficient of variation for kernel ratios (k, h, e) across folios
3. Test length-coherence (do kernel ratios vary with length quintiles?)
4. Compute per-folio deviation from global Markov chain

**Success Criterion:** If MI > 0.3 AND CV < 0.1 AND deviation < 50, folios are redundant.

**Rationale:** Distinct recipes should produce statistically distinguishable signatures.

---

## Execution Notes

- All tests use the same input corpus: `interlinear_full_words.txt` (37,656 words, 227 folios)
- Random seeds not fixed to test robustness
- All metrics computed from scratch (no reliance on Phase 15-22 intermediates)
