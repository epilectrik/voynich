# Phase HTD: Human-Track Domain Analysis

**Status:** COMPLETE
**Date:** 2026-01-07
**Tier:** 2 (Structural)

---

## Executive Summary

| Test | Question | Finding | Verdict |
|------|----------|---------|---------|
| **HTD-1** | Run length clustering? | Longer than shuffle, non-exponential | **OUTCOME A: Intentional** |
| **HTD-2** | LINK-HT coupling? | r = 0.010 (essentially zero) | **LOOSE** |
| **HTD-4** | Program-type association? | p < 0.0001 across waiting profiles | **SIGNIFICANT** |

**Overall Finding:** HT is **behaviorally stratified by program type**, not coupled to LINK tokens. This supports **single-domain operation with program-level variation**, not multi-domain mixing.

---

## Key Discovery: Decoupled Hierarchies

The combination of HTD-2 (LOOSE: r≈0) and HTD-4 (SIGNIFICANT: p<0.0001) reveals a **hierarchical independence**:

```
PROGRAM-LEVEL:  HT correlates with WAITING_PROFILE (categorical)
                EXTREME > HIGH > MODERATE > LOW
                (r² with profile explains ~28% of variance)

TOKEN-LEVEL:    HT does NOT correlate with LINK tokens (continuous)
                r = 0.010, p = 0.93
                (LINK density explains ~0% of variance)
```

**Interpretation:** HT is a **program characteristic**, not a token-level response. Operators in HIGH-waiting programs write more overall, but their writing doesn't track individual LINK positions.

---

## HTD-1: Run Length Distribution

### Data

| Metric | Value |
|--------|-------|
| Total strict HT tokens | 6,584 (8.7% of corpus) |
| Total HT runs | 5,666 |
| Mean run length | 1.16 |
| Max run length | 10 |
| Runs of length 1 | 86.8% |
| Runs of length 2+ | 13.2% |

### Dual Baseline Results

**Shuffle Baseline:**
- Observed mean: 1.163
- Shuffled mean: 1.096 (95% CI: [1.088, 1.103])
- P(shuffled >= observed): **0.0000**
- Verdict: **LONGER_THAN_SHUFFLE**

**Exponential Fit:**
- KS test: Rejects exponential (p ≈ 0)
- Tail ratio: 0.57 (observed is LESS heavy than exponential)
- Verdict: **NON_EXPONENTIAL**

### Outcome: A (Intentional Extended Writing)

| Criterion | Result |
|-----------|--------|
| Longer than shuffle? | YES |
| Non-exponential? | YES (but compressed tail, not heavy) |

**Interpretation:** HT shows deliberate clustering beyond random, but runs are SHORT (mode=1, mean=1.16). This suggests **brief intentional marks** rather than sustained doodling sessions.

**Note:** The tail is COMPRESSED (not heavy) - runs rarely exceed 2-3 tokens. This is consistent with **punctuated practice** (brief marks between actions) rather than **sustained writing** (long sessions during wait periods).

---

## HTD-2: LINK-HT Coupling

### Correlation Analysis

| Statistic | Value | p-value |
|-----------|-------|---------|
| Pearson r | -0.002 | 0.986 |
| Spearman ρ | 0.010 | 0.929 |

**Verdict: LOOSE** (r ≈ 0)

### What This Means

The **complete independence** of HT and LINK at the folio level is striking:

- Folios with HIGH LINK density don't have more HT
- Folios with LOW LINK density don't have less HT
- The "more waiting = more doodling" hypothesis is **NOT supported** at token level

### Outliers

5 folios show unusually high HT given their LINK density:

| Folio | HT Density | LINK Density | Profile | Note |
|-------|------------|--------------|---------|------|
| f57r | 16.3% | 10.1% | HIGH | **RESTART folio** |
| f66v | 16.0% | 28.1% | MODERATE | |
| f85v2 | 16.6% | 22.5% | EXTREME | |
| f105r | 15.8% | 26.2% | EXTREME | |
| f105v | 20.3% | 36.2% | EXTREME | |

**Observation:** f57r (the restart folio) is an outlier - high HT, low LINK. This is consistent with its special operational role.

---

## HTD-4: Program-Type Association

### HT Density by Waiting Profile

| Profile | Mean HT | Std | n |
|---------|---------|-----|---|
| **EXTREME** | 15.9% | 3.4% | 4 |
| **HIGH** | 10.4% | 2.5% | 23 |
| **MODERATE** | 8.5% | 2.7% | 50 |
| **LOW** | 5.7% | 1.6% | 6 |

**Kruskal-Wallis H = 23.76, p < 0.0001**

### HT Density by Intervention Style

| Style | Mean HT | n |
|-------|---------|---|
| CONSERVATIVE | 12.7% | 12 |
| BALANCED | 8.6% | 65 |
| AGGRESSIVE | 7.9% | 6 |

**Kruskal-Wallis H = 14.78, p = 0.0006**

### Verdict: SIGNIFICANT

Programs with **more waiting** have **more HT**. This is a clear monotonic relationship that survives non-parametric testing.

**Key insight:** The waiting profile is a CATEGORICAL program-level property, while LINK density is a token-level measurement. HT correlates with the former but not the latter. This suggests HT is determined by **what type of program is running**, not by **how many LINK tokens appear**.

---

## Synthesis: What HTD Shows

### Single Domain, Behaviorally Stratified

The findings are consistent with **single-domain operation** where:

1. Different PROGRAMS have different waiting requirements
2. Programs with more waiting have operators who write more
3. But HT is NOT a direct response to individual LINK tokens
4. HT is a **program-level behavioral trait**

### Against Multi-Domain Hypothesis

The multi-domain hypothesis predicted:
- **Bimodal** run length distribution → NOT found (unimodal, mode=1)
- **Low correlation** (r < 0.5) → FOUND (r ≈ 0) but explained by hierarchy
- **Significant program differences** → FOUND but monotonic, not categorical

The monotonic relationship (EXTREME > HIGH > MODERATE > LOW) suggests a **continuous spectrum** of program intensities, not discrete domain types.

### Refined HT Model

```
PROGRAM CHARACTERISTICS:
- Waiting profile determines HT RATE (program-level)
- EXTREME/HIGH programs: 10-16% HT density
- MODERATE/LOW programs: 6-8% HT density

TOKEN PLACEMENT:
- HT placement is NOT synchronized with LINK tokens
- Operators write at program-appropriate RATES
- But NOT in response to specific LINK positions
```

---

## Constraints

### Constraint 341 (Tier 2)

**HT-program stratification:** HT density varies monotonically by waiting profile (EXTREME 15.9% > HIGH 10.4% > MODERATE 8.5% > LOW 5.7%; Kruskal-Wallis p < 0.0001); HT is a program-level characteristic, not a token-level response; operators in high-waiting programs write more overall.

### Constraint 342 (Tier 2)

**HT-LINK decoupling:** HT density is independent of LINK density at folio level (Spearman ρ = 0.010, p = 0.93); the "more LINK = more doodling" hypothesis is falsified; HT is not synchronized with LINK token positions.

---

## Implications for Farming/Greenhouse Hypothesis

These findings are **compatible with both interpretations** but don't discriminate:

| Interpretation | Compatibility |
|----------------|---------------|
| **Distillation** | HIGH-waiting = long reflux runs = more time to write |
| **Greenhouse** | HIGH-waiting = slow-growth crops = more monitoring shifts |

Both interpretations predict program-level variation in waiting requirements, and thus in HT density. The key finding (HT-LINK decoupling) applies equally to both.

**What HTD does NOT show:**
- Evidence for multiple distinct domains
- Evidence for periodic task structure
- Distinction between distillation and greenhouse timescales

---

## Files

| File | Purpose |
|------|---------|
| `htd_tests.py` | Test implementation |
| `htd_results.json` | Raw results |
| `HTD_REPORT.md` | This document |

---

*Phase HTD: COMPLETE. 2 Tier 2 constraints added (341-342).*
*Generated: 2026-01-07*
