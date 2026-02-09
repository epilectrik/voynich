# MIDDLE Frequency Distribution Analysis

**Tier:** 3 | **Status:** COMPLETE + SATURATED | **Date:** 2026-01-11

> **Saturation Note:** This analysis, together with the Perturbation Space Phase, represents the maximum achievable internal resolution for MIDDLE identification. The question "can we identify MIDDLEs by sharing patterns?" is CLOSED: behavioral independence/dependence can be determined, but entity semantics cannot. See [C461](../CLAIMS/C461_ht_middle_rarity.md), [C462](../CLAIMS/C462_universal_mode_balance.md).

> **Goal:** Test whether MIDDLE frequency distribution encodes physically interpretable structure from the apparatus perspective.

---

## Executive Summary

The MIDDLE frequency distribution shows **moderate evidence** for apparatus-centric structure. 3 of 6 tests confirmed the hypothesis that high-frequency MIDDLEs are "generalist" recognition points while low-frequency MIDDLEs are "specialist" edge cases.

**Key findings (10 tests total, 6 confirmed):**
- TWO generative processes confirmed (mixture model delta-AIC = 5,434)
- Volatile material classes generate broader variation (M-A/M-D ratio = 1.39)
- Tail MIDDLEs demand specific operational modes (confirmed)
- Rare MIDDLEs appear in high-hazard contexts (confirmed)
- Core MIDDLEs are universal across sections (confirmed)
- Rare MIDDLEs are context-dependent and brittle (p < 0.0001)

---

## Distribution Census

| Metric | Value |
|--------|-------|
| Total unique MIDDLEs | 1,184 |
| Core (top 30) | 30 MIDDLEs, 67.6% of usage |
| Tail | 1,154 MIDDLEs, 32.4% of usage |
| Singletons | 502 (42.4%) |
| Rare (count ≤ 3) | 850 (71.8%) |
| Entropy | 6.70 bits (65.6% efficiency) |

---

## Test Results

### Test 1: Core vs Long-Tail Behavioral Signatures

**Result: CONFIRMED**

| Metric | Core | Tail | Interpretation |
|--------|------|------|----------------|
| Sister preference deviation | 0.147 | 0.254 | Tail demands specific mode |
| Suffix entropy | 3.43 bits | 3.40 bits | Core slightly more flexible |
| Prefix exclusivity | 6.7% | 81.9% | Tail is class-specific |

**Interpretation:** Tail MIDDLEs exhibit stronger mode preference and are overwhelmingly prefix-exclusive. This confirms that rare variants require specific handling while common variants are more flexible.

---

### Test 2: Frequency-Sister Preference Correlation

**Result: NOT CONFIRMED**

| Metric | Value |
|--------|-------|
| MIDDLEs tested | 75 (N≥10 ch/sh tokens) |
| Spearman rho | -0.123 |
| p-value | 0.293 |

No significant correlation between MIDDLE frequency and sister preference deviation. The Test 1 result (Core vs Tail difference) is driven by group-level patterns, not a continuous frequency gradient.

---

### Test 3: Frequency-Hazard Context Correlation

**Result: CONFIRMED**

| Metric | Value |
|--------|-------|
| MIDDLEs tested | 121 |
| Spearman rho | -0.339 |
| p-value | 0.0001 |

**Strong finding:** Rare MIDDLEs appear disproportionately in high-hazard contexts (ch/sh/qo prefixes).

**Apparatus interpretation:** Edge-case recognition is concentrated where it matters most — in dangerous situations that require precise discrimination. Common situations can be handled with flexible recognition; dangerous edge cases require specific identification.

---

### Test 4: Distribution Shape Analysis

**Result: PARTIAL (Zipf-like with cutoff)**

| Fit | Parameter | Result |
|-----|-----------|--------|
| Zipf | s = 1.26 | Within Zipf range |
| Log-normal | KS p < 0.001 | Rejected |
| Exponential | KS p < 0.001 | Rejected |
| Cutoff | slope ratio = 0.67 | Cutoff detected |

The distribution is Zipf-like (s ≈ 1.26), which is typical for natural language. However, the curve steepens at high ranks, indicating a finite recognition space with cutoff.

**Interpretation:** The Zipf-like pattern suggests a generative process similar to language, but the cutoff suggests a bounded expert recognition system rather than open-ended vocabulary.

---

### Test 5: MIDDLE Entropy by Prefix Class

**Result: NOT CONFIRMED**

| Prefix | Hazard | N_MIDDLEs | Entropy |
|--------|--------|-----------|---------|
| ch | high | 433 | 6.32 |
| sh | high | 228 | 5.07 |
| qo | high | 277 | 5.27 |
| ok | medium | 142 | 4.95 |
| ot | medium | 138 | 5.16 |
| da | medium | 155 | 2.89 |
| ct | low | 92 | 3.11 |
| ol | low | 93 | 5.41 |

Hazard-entropy correlation: rho = 0.34, p = 0.41 (not significant)

No clear pattern between prefix hazard class and MIDDLE diversity. The ch-family has highest entropy, but ol (low hazard) also has high entropy.

---

### Test 6: Rank-Frequency Stability Across Sections

**Result: CONFIRMED**

| Section Pair | Rank Correlation (rho) | p-value |
|--------------|------------------------|---------|
| H vs P | 0.607 | < 0.0001 |
| H vs T | 0.555 | < 0.0001 |
| P vs T | 0.465 | < 0.0001 |

| Group | Rank Variance |
|-------|---------------|
| Core MIDDLEs | 364 |
| Tail MIDDLEs | 5,427 |

**Strong finding:** Core MIDDLEs maintain consistent ranks across sections (15x lower variance than Tail). This confirms that core MIDDLEs are **universal recognition points** that any practitioner encounters, while tail MIDDLEs are **context-dependent edge cases**.

---

## Bayesian Tests (Expert Framework)

Following expert guidance, four additional Bayesian-style tests were run to validate the apparatus-centric interpretation.

### Bayesian Test 1: Mixture Model on MIDDLE Frequencies

**Question:** Are MIDDLEs drawn from more than one generative process?

**Result: STRONGLY CONFIRMED**

| Model | AIC |
|-------|-----|
| Zipf | -1,863 |
| Geometric | -46,921 |
| **Mixture** | **-52,355** |

Delta-AIC = 5,434 strongly favors the two-component mixture model:
- **Head component:** ~66% of types, high reuse rate (p1 = 0.19)
- **Tail component:** ~34% of types, rare perturbations (p2 = 0.006)

**Interpretation:** The apparatus operates with a small basis of common behavioral modes plus a large perturbation space. This is textbook continuous physical process behavior.

---

### Bayesian Test 2: Conditional Entropy H(MIDDLE|PREFIX)

**Question:** How predictable is the variant space within each material class?

**Result: CONFIRMED**

| Material Class | Entropy (bits) | Unique MIDDLEs |
|----------------|----------------|----------------|
| M-A (volatile) | 6.08 | 452 |
| M-B (mobile) | 4.65 | 206 |
| M-C (distinct) | 3.58 | 166 |
| M-D (stable) | 4.37 | 124 |

**M-A / M-D entropy ratio:** 1.39 (95% CI: [1.34, 1.49])

**Interpretation:** Volatile/unstable material classes (M-A: ch/qo prefixes) generate broader behavioral variation than stable classes. This is a physical statement: more volatile materials produce more variant situations that must be recognized.

---

### Bayesian Test 3: MIDDLE-Decision Archetype Mutual Information

**Question:** Do certain variants correlate with specific decisions?

**Result: NOT CONFIRMED (but informative)**

| Group | MI (bits) | NMI |
|-------|-----------|-----|
| All MIDDLEs | 1.08 | 0.29 |
| Head (top 30) | 0.84 | 0.28 |
| Tail (rest) | 1.66 | 0.38 |

The Tail shows HIGHER mutual information than Head (opposite of prediction).

**Interpretation:** Rare variants are NOT situationally vague — they actually correlate MORE strongly with decision types. This suggests tail MIDDLEs trigger specific, predictable responses precisely because they are rare edge cases with clear handling requirements.

---

### Bayesian Test 4: Hazard/Risk Analysis on MIDDLEs

**Question:** Do rare MIDDLEs associate with higher operational risk?

**Result: CONFIRMED (p < 0.0001)**

| Metric | Head | Mid | Tail |
|--------|------|-----|------|
| Sister preference deviation | 0.29 | 0.29 | 0.33 |
| Section concentration | 0.63 | 0.61 | **0.80** |
| Suffix entropy | 1.61 | 1.31 | 0.67 |

Mann-Whitney U tests:
- Tail > Head sister deviation: p < 0.0001
- Tail > Head section concentration: p = 0.0001

**Key finding:** Rare MIDDLEs show:
1. **Higher section concentration** (context-dependent: appear in fewer sections)
2. **Lower suffix entropy** (more predictable decision: specific response required)
3. **Higher brittleness** (stronger mode preference)

**Interpretation:** Frontier variants are harder for the apparatus to handle and require context-specific, predictable responses. They represent edge cases where grammatical control is insufficient and human judgment dominates.

---

### Bayesian Tests Summary

| Test | Result | Apparatus Interpretation |
|------|--------|--------------------------|
| B1: Mixture Model | CONFIRMED | Two generative processes (modes + perturbations) |
| B2: Conditional Entropy | CONFIRMED | Volatile materials generate broader variation |
| B3: Mutual Information | NOT CONFIRMED | Rare variants trigger specific (not vague) decisions |
| B4: Hazard Analysis | CONFIRMED | Rare variants are context-dependent, brittle |

**Overall: 3/4 tests confirmed** (matching minimum success criteria)

---

## Synthesis

### What the Distribution Encodes

From the apparatus perspective, the MIDDLE frequency distribution reflects the **structure of expert recognition**:

| Frequency Tier | Recognition Role | Properties |
|----------------|------------------|------------|
| **Core (top 30)** | Universal situations | Mode-flexible, section-stable, cross-class |
| **Tail (~1,150)** | Edge-case situations | Mode-specific, section-variable, class-exclusive |

### Why Core MIDDLEs Are Mode-Flexible

Common situations can be handled in either precision mode (ch) or tolerance mode (sh) depending on context. The apparatus doesn't need to specify mode for routine variants — the operator chooses based on conditions.

### Why Tail MIDDLEs Demand Specific Modes

Rare edge cases require specific handling. A variant that appears only 2-3 times is likely a specialized situation that always requires either tight control (precision) or generous recovery (tolerance), but not both.

### Why Rare MIDDLEs Appear in High-Hazard Contexts

Edge cases cluster in dangerous situations because:
1. **Hazardous operations generate more variant scenarios** — energy transitions (ch/sh/qo) create more unusual situations than stable operations (ct/ol)
2. **Precision matters more in danger** — rare variants must be correctly identified when stakes are high
3. **Rare events trigger rare responses** — the apparatus needs fine discrimination exactly when things go wrong

---

## Apparatus-Centric Update

This analysis extends the CCM findings with a **frequency dimension**:

```
TOKEN = PREFIX     (what material class)
      + SISTER     (how carefully)
      + MIDDLE     (which variant — core vs edge)
      + SUFFIX     (what decision)
```

The MIDDLE component now has interpretable structure at two levels:

1. **Identity level:** ~1,184 distinct situational fingerprints
2. **Frequency level:** Core (universal) vs Tail (specialized)

---

## Constraint Implications

### Potential New Constraint (if elevated to Tier 2)

**C4xx: MIDDLE frequency encodes recognition universality**
- Core MIDDLEs (top 30, 67.6% of usage) are rank-stable across sections
- Tail MIDDLEs (32.4% of usage) cluster in high-hazard prefix classes
- Interpretation: Frequency reflects how common a situation is for any practitioner

*Status: Tier 3 pending validation*

---

## Perturbation Space Phase (Follow-up)

A follow-up phase tested whether MIDDLE tier correlates with B-layer operational complexity.

| Test | Result | Finding |
|------|--------|---------|
| HT Density | **CONFIRMED** | Tail has 1.58x higher HT markers (p < 0.0001) |
| Recovery Diversity | NOT CONFIRMED | Equal successor entropy (~4.3 bits) |
| Time-to-STATE-C | OPPOSITE | Tail stabilizes faster (2.05 vs 2.11 tokens) |

**Refined interpretation:** The system *recognizes* rare situations (A + HT) but *executes* them uniformly (B). HT anticipates recognition difficulty; B-layer applies uniform recovery.

See [../../phases/perturbation_space/PHASE_SUMMARY.md](../../phases/perturbation_space/PHASE_SUMMARY.md) for details.

---

## Limitations

1. **Test 2 did not confirm continuous gradient** — the Core/Tail distinction may be categorical rather than continuous
2. **Test 4 shows Zipf-like pattern** — this could indicate language-like generative process rather than apparatus-specific structure
3. **Test 5 showed no hazard-entropy correlation** — prefix hazard class does not predict MIDDLE diversity
4. **B-layer shows uniform execution** — perturbation handling is at recognition layer, not execution layer

---

## Files Generated

| File | Contents |
|------|----------|
| `phases/exploration/middle_frequency_analysis.py` | Original 6-test analysis |
| `archive/scripts/middle_bayesian_tests.py` | Expert-guided 4-test Bayesian analysis |
| `results/middle_frequency_analysis.json` | Original test results |
| `results/middle_bayesian_tests.json` | Bayesian test results |
| This document | Interpretation |

---

## Navigation

← [ccm_middle_classification.md](ccm_middle_classification.md) | ↑ [../CLAUDE_INDEX.md](../CLAUDE_INDEX.md) | → [apparatus_centric_semantics.md](apparatus_centric_semantics.md)
