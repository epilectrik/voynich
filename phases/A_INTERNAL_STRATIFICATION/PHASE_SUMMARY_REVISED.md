# A-INTERNAL-STRATIFICATION: Revised Summary

**Date:** 2026-01-20
**Status:** COMPLETE - FINDINGS REVISED
**Original Verdict:** PARTIAL STRATIFICATION (4/8 tests significant)
**Revised Verdict:** ENTRY STRUCTURE FINDING (different from original interpretation)

---

## Critical Discovery During Analysis

Multi-token entries in Currier A are **100% repetitions of the same token**.

Examples:
- `shol shol shol`
- `daiin daiin daiin daiin daiin daiin daiin`
- `chol chol chol chol chol chol chol`

**No entry ever mixes different MIDDLEs.** This is not about A-exclusive vs shared incompatibility - it's a fundamental property of Currier A entries.

---

## Revised Data Structure

| Entry Type | Count | % |
|------------|-------|---|
| Single-token | 5,920 | 84.0% |
| Multi-token (same token repeated) | 1,128 | 16.0% |
| Multi-token (different tokens) | **0** | **0.0%** |

---

## Original Findings: What Changed

### 1. "98.8% Opener" - CONFOUNDED

**Original:** A-exclusive tokens appear at opener position 98.8% of the time.

**Revised:** A-exclusive entries are **99.0% single-token** (vs 82.9% for shared). In single-token entries, the token is trivially at position 1. The opener concentration is explained by entry size, not positional preference.

| Class | Single-token entries | Multi-token entries |
|-------|---------------------|---------------------|
| A-exclusive | 472 (99.0%) | 5 (1.0%) |
| A/B-shared | 5,448 (82.9%) | 1,123 (17.1%) |

Chi-square: 83.94, p ≈ 0

### 2. "Zero Mixing" - EXPLAINED BY ENTRY STRUCTURE

**Original:** Zero entries mix A-exclusive and shared MIDDLEs (0 vs 157 expected).

**Revised:** **No entries mix ANY different MIDDLEs**, regardless of class. Entries are single-MIDDLE by design. The zero-mixing between classes is a consequence of this broader pattern, not class incompatibility.

### 3. Folio Spread - STILL VALID

**Original:** A-exclusive MIDDLEs spread 1.2 folios vs 7.7 for shared.

**Revised:** Still valid. A-exclusive MIDDLEs are folio-specific.

### 4. ct- Enrichment - STILL VALID

**Original:** ct-prefix is 5.1x enriched in A-exclusive (20.3% vs 4.0%).

**Revised:** Still valid. The 5 multi-token A-exclusive entries are 80% ct-prefix.

---

## New Finding: Single-Token Correlation

**A-exclusive MIDDLEs correlate with single-token entries.**

| Metric | A-exclusive | A/B-shared |
|--------|-------------|------------|
| Single-token rate | **99.0%** | 82.9% |
| Mean tokens/entry | 1.01 | 1.32 |
| Max tokens | 3 | 19 |
| Multi-token entries | 5 | 1,123 |

Mann-Whitney U test: p ≈ 0

**Interpretation:**
- A-exclusive MIDDLEs are **non-repeatable markers** (one instance per entry)
- A/B-shared MIDDLEs are **repeatable vocabulary** (can appear multiple times)

---

## What We Actually Learned

### About Currier A Entry Structure

1. **LINE_ATOMIC confirmed** - entries are single units
2. **No MIDDLE mixing** - entries use exactly one MIDDLE type
3. **Repetition = same token** - multi-token entries repeat identical tokens
4. **Repetition is class-specific** - shared vocabulary can repeat, A-exclusive (mostly) cannot

### About A-Exclusive Vocabulary

1. **Folio-specific** (mean 1.2 folios) - confirmed
2. **ct- enriched** (5.1x) - confirmed
3. **Non-repeatable** (99% single-token) - NEW FINDING
4. **Low frequency** (mean 1.4 occurrences) - confirmed as confound

### Functional Model (Revised)

| Class | Entry Role | Repeatable? | Folio Scope |
|-------|------------|-------------|-------------|
| A-exclusive | Type marker / classifier | No (99% single) | Local (1.2 folios) |
| A/B-shared | Discriminative content | Yes (17% multi) | Global (7.7 folios) |

---

## Implications

### For "Entry-Type Marker" Hypothesis

The original hypothesis (A-exclusive = entry classifiers) is **partially supported** but **differently than expected**:

- NOT because they appear at opener position (confounded)
- NOT because of incompatibility with shared MIDDLEs (all MIDDLEs don't mix)
- BUT because they are **non-repeatable** and **folio-specific**

### For Constraint Formalization

A weaker constraint is warranted:

**Proposed C498 (Revised):** A-exclusive MIDDLEs (349 types, 5.3% of tokens) are characterized by: (1) folio-specificity (mean 1.2 folios vs 7.7), (2) ct-prefix enrichment (5.1x), (3) non-repetition (99% single-token entries vs 83% for shared), and (4) low frequency (mean 1.4 vs 32.3). This profile is consistent with a **classifying or marking function** distinct from the repeatable discriminative vocabulary.

---

## Outstanding Questions

1. **Why no MIDDLE mixing in any entries?** This is a broader Currier A property not previously documented.

2. **What does repetition encode?** If not ratios (falsified C287-C290), then emphasis? Quantity? Certainty?

3. **Why can't A-exclusive repeat?** Is it functional (classifiers don't need emphasis) or structural (single-instance by design)?

4. **AZC participation still unknown** - data loading issue not resolved.

---

## Files

- `results/stratification_tests.json` - Original test results
- `results/incompatibility_test.json` - Incompatibility analysis
- `scripts/check_entry_sizes.py` - Entry size analysis
- `scripts/examine_multi_token.py` - Multi-token investigation
- `scripts/retest_position.py` - Position re-test with size control
