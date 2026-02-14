# C1025: Generative Sufficiency — Class Markov + Forbidden Suppression Is Sufficient at M2 (80%)

**Tier:** 2 (Structural Inference)
**Scope:** B
**Phase:** GENERATIVE_SUFFICIENCY (Phase 348)
**Depends on:** C121 (49 instruction classes), C109 (forbidden transitions), C978 (spectral gap), C1010 (6-state macro-automaton), C267 (compositional morphology), C1023 (PREFIX routing), C1024 (MIDDLE directionality)

---

## Finding

Generative sufficiency testing with 5 models (M0-M4), 15-test battery, and 20 instantiations each reveals that the sufficiency frontier sits at **M2** (49-class Markov chain + 17 forbidden transition suppression), passing 12/15 tests (80%). The most surprising result: **M0 (i.i.d. token frequency sampling) passes 11/15 tests (73%)**, demonstrating that most structural tests measure marginal (distributional) properties, not sequential structure. The compositional model M4 (PREFIX-routed generation) performs **worst** at 9.4/15 (63%) due to hallucination from the prefix×middle×suffix product space exceeding the real vocabulary.

Only 2/5 pre-registered predictions were correct (P3: M2 adds ≤1 over M1; P5: no model achieves 15/15).

---

## Results

### Model Performance

| Model | Mechanism | Mean Pass | Pass Rate |
|-------|-----------|-----------|-----------|
| M0 | Token frequency (i.i.d.) | 11.0/15 | 73.3% |
| M1 | 49-class Markov | 11.9/15 | 79.3% |
| **M2** | **M1 + forbidden suppression** | **12.0/15** | **80.0%** |
| M3 | 6-state macro Markov + class emission | 12.0/15 | 80.0% |
| M4 | PREFIX-routed compositional | 9.4/15 | 62.7% |

### Per-Test Pass Rates

| Test | Real Value | M0 | M1 | M2 | M3 | M4 |
|------|-----------|----|----|----|----|-----|
| A1 class KL | 0.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| A2 hapax rate | 0.026 | 1.0 | 1.0 | 1.0 | 1.0 | 0.0 |
| A3 active classes | 48 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| A4 type count | 468 | 1.0 | 1.0 | 1.0 | 1.0 | 0.0 |
| B1 spectral gap | 0.894 | 0.0 | 1.0 | 1.0 | 1.0 | 0.4 |
| B2 AXM self-transition | 0.698 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| B3 forbidden violations | 13 | 0.0 | 0.0 | 1.0 | 0.0 | 0.0 |
| B4 role rank order | false | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| B5 fwd-rev JSD | 0.090 | 1.0 | 0.9 | 0.0 | 1.0 | 1.0 |
| C1 suffix rate | 0.369 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| C2 CC suffix-free | 0.834 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| C3 PREFIX entropy reduction | 0.592 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| D1 stationary distribution | — | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| D2 AXM dwell | 2.509 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| D3 cross-line MI | 0.521 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |

### Predictions

| # | Prediction | Result | Correct? |
|---|-----------|--------|----------|
| P1 | M0 passes ≤3/15 | M0 passes 11/15 | NO |
| P2 | M1 passes 5-8/15 | M1 passes 11.9/15 | NO |
| P3 | M2 adds ≤1 test over M1 | M2 adds 0.1 tests | **YES** |
| P4 | M4 is sufficiency frontier (≥12) | M4 worst at 9.4/15 | NO |
| P5 | No model achieves 15/15 | Best is 12/15 | **YES** |

---

## Key Findings

### 1. Most structural tests are marginal

M0 (i.i.d. token frequency) passes 11/15 tests with zero sequential structure. This means 73% of the test battery measures distributional properties that are satisfied by matching token frequencies alone. The genuinely discriminative tests are:

- **B1 (spectral gap)**: Requires sequential class-class transitions
- **B3 (forbidden violations)**: Requires explicit forbidden pair suppression
- **B4 (role rank order)**: No model passes — specification issue (tests raw rates not enrichment)
- **C2 (CC suffix-free)**: No model passes — class 17 contains suffixed tokens

### 2. Compositional generation is worse than direct sampling

M4 (PREFIX-routed compositional generation) produces novel tokens at a 4.2% hallucination rate. The prefix×middle×suffix product space is larger than the real vocabulary (583 mean types vs 468 real), causing A2 (hapax rate: 12.5% vs 2.6% real) and A4 (type count) failures. The real vocabulary is a **constrained subset** of the compositional product space — not every valid prefix+middle+suffix combination is a real token.

### 3. Sufficiency frontier at M2

The 49-class Markov chain with forbidden pair suppression captures the maximum measurable structure. Adding the 6-state macro layer (M3) ties M2 but adds nothing, confirming the macro-automaton is a **lossy projection** of the class-level chain (consistent with C1010's 8.17x compression).

### 4. Three universally-failed tests reveal test battery limitations

- **B4 (role rank order)**: Real value is `false` — the test specification checks a condition the real corpus doesn't satisfy
- **C2 (CC suffix-free = 100%)**: Real value is 83.4% — CC role contains class 17 which has suffixed tokens
- **B3 (forbidden violations)**: Real corpus has 13 violations; only M2 (which hard-suppresses) achieves 0

These failures indicate test battery calibration issues, not model inadequacies.

---

## Structural Implications

1. **The characterization is generatively sufficient at the class-Markov level.** A 49×49 transition matrix + 17 forbidden exclusions reproduces 80% of measurable structure.

2. **Token-level composition is NOT a simple product.** The real vocabulary is a curated subset of possible prefix+middle+suffix combinations. Direct token sampling outperforms compositional assembly.

3. **The macro-automaton adds no discriminative power** beyond what the 49-class Markov chain already provides, consistent with it being a derived projection (C1010).

4. **Remaining 20% likely requires**: (a) better test specifications (B4, C2 calibration), (b) within-class token selection rules, and (c) multi-line structure beyond cross-line MI.

---

## Evidence

- Script: `phases/GENERATIVE_SUFFICIENCY/scripts/generative_sufficiency.py`
- Results: `phases/GENERATIVE_SUFFICIENCY/results/generative_sufficiency.json`
- 5 models × 15 tests × 20 instantiations = 1,500 test evaluations
- Verdict: GENERATIVE_SUFFICIENCY_AT_M2
