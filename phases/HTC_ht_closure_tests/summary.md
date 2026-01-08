# Phase HTC: Human Track Closure Tests

## Core Question

> **Can we close the HT interpretation question with definitive structural tests?**

Three final discriminator tests to determine if any alternative to "calligraphy practice / attention maintenance" gains support.

## Test Results

### TEST 1: HT × Terminal State

**Question**: Do high-HT folios end in different terminal grammar states?

| Metric | High HT (41 folios) | Low HT (41 folios) | Difference |
|--------|---------------------|--------------------|-----------:|
| ENERGY_OPERATOR | 34.1% | 36.6% | -2.4% |
| FREQUENT_OPERATOR | 24.4% | 17.1% | +7.3% |
| CORE_CONTROL | 17.1% | 19.5% | -2.4% |
| HIGH_IMPACT | 12.2% | 9.8% | +2.4% |
| AUXILIARY | 7.3% | 7.3% | +0.0% |
| FLOW_OPERATOR | 4.9% | 9.8% | -4.9% |

**Statistics**:
- Chi-square: χ² = 1.41, p = 0.9234, dof = 5
- HT density × ENERGY terminal correlation: ρ = 0.013, p = 0.904

**Verdict**: **NO EFFECT** — HT density does not predict terminal state.

### TEST 2: HT → Following Token Prediction

**Question**: Given the same local grammar context, does HT presence alter subsequent token probabilities?

| Context | With HT | Without HT | Notable Differences |
|---------|---------|------------|---------------------|
| ENERGY_OPERATOR | 1132 | 207 | HIGH_IMPACT +8.4% |
| CORE_CONTROL | 584 | 137 | ENERGY_OP -16.5% |
| HIGH_IMPACT | 292 | 50 | FREQUENT -22.8% |
| FREQUENT_OPERATOR | 278 | 79 | ENERGY_OP -7.1% |
| FLOW_OPERATOR | 233 | 48 | ENERGY_OP -9.0% |
| AUXILIARY | 233 | 49 | ENERGY_OP +12.8% |

**Statistics**:
- Overall chi-square: χ² = 32.93, p = 0.0000, dof = 5
- **Effect size (Cramér's V): 0.100** (very weak)

**Interpretation**: The p-value is significant due to large sample size (3,322 transitions), but the effect size is negligible (V = 0.10). Context-specific differences exist but are not systematic.

**Verdict**: **NO PREDICTIVE EFFECT** — HT has no causal/advisory role.

### TEST 3: HT Type Internal Structure

**Question**: Do HT types show Zipf-like distribution? Motor practice signatures?

**Zipf Analysis**:
- Zipf exponent: **0.892** (ideal = 1.0)
- R² of log-log fit: 0.923
- Verdict: **ZIPF-LIKE** (natural language signature)

**Distribution Statistics**:
- Total HT tokens: 19,791
- Unique HT types: 4,897
- Hapax rate: **67.5%** (3,307 types appear only once)
- Mean length: 5.29 ± 1.70 characters

**Motor Practice Signatures**:
- 75.4% have no character repetition (1-run)
- 22.7% have 2-character runs
- 1.9% have 3-character runs

**Top Starting Characters**:
| Char | Count | % |
|------|-------|---|
| o | 4,569 | 23.1% |
| q | 3,777 | 19.1% |
| s | 2,581 | 13.0% |
| c | 2,454 | 12.4% |

**Top 2-char Prefixes**:
| Prefix | Tokens | Types | % |
|--------|--------|-------|---|
| qo | 3,681 | 522 | 18.6% |
| ch | 2,299 | 632 | 11.6% |
| sh | 2,028 | 361 | 10.2% |
| ot | 1,363 | 228 | 6.9% |
| ok | 1,215 | 212 | 6.1% |

**Comparison to Grammar Tokens**:
- Grammar Zipf exponent: 1.098
- HT Zipf exponent: 0.892
- Grammar hapax rate: 0.0%
- HT hapax rate: 67.5%
- Verdict: Different distribution shapes — HT is more generative

**Verdict**: **GENERATIVE/COMPOSITIONAL** — Not random noise (would be flatter), not memorized templates (would have lower hapax).

## Overall Verdict

| Test | Result | Interpretation |
|------|--------|----------------|
| 1. HT × Terminal State | NO EFFECT (p=0.92) | Non-operational |
| 2. HT → Following Prediction | NO EFFECT (V=0.10) | No causal role |
| 3. HT Internal Structure | Zipf=0.89, 67.5% hapax | Generative |

**HT is CONFIRMED NON-OPERATIONAL**:
- Does not influence terminal states
- Does not predict subsequent grammar tokens
- Has generative/productive internal structure

The "calligraphy practice" or "attention maintenance" interpretation remains the best fit. HT is a human-facing layer with no causal role in the operational grammar.

## Tier Status

| Aspect | Tier | Status |
|--------|------|--------|
| Structural properties | Tier 2 | CONFIRMED |
| Interpretation (practice/attention) | Tier 3-4 | REMAINS UNPROVABLE |
| Alternative interpretations | — | NONE GAIN SUPPORT |

## Constraints Added

**Constraint 404**: HT TERMINAL INDEPENDENCE: HT density does not predict terminal grammar state (chi2=1.41, p=0.92; correlation rho=0.013, p=0.90); high-HT and low-HT folios have statistically indistinguishable outcome distributions; confirms HT has no influence on program completion (HTC, Tier 2)

**Constraint 405**: HT CAUSAL DECOUPLING: HT presence does not alter subsequent grammar token probabilities beyond phase correlation; chi2 significant (p=0.0000) but effect size negligible (Cramer's V=0.10); HT has no advisory or predictive role in grammar execution (HTC, Tier 2)

**Constraint 406**: HT GENERATIVE STRUCTURE: HT types follow Zipf distribution (exponent 0.892, R²=0.92) with 67.5% hapax rate; consistent with productive compositional system, not random noise (flatter) or memorized templates (lower hapax); supports practice/exploration interpretation (HTC, Tier 2)

## Files

- `archive/scripts/ht_closure_tests.py` - All three tests

## Status

**CLOSED** - 3 constraints established (404-406)

HT interpretation is now as constrained as possible by internal structural analysis. The "calligraphy practice during waiting" interpretation remains the best fit, but the specific intent (practice vs attention vs habit) cannot be determined from structure alone.

**This question is permanently closed at Tier 3-4 for interpretation.**
