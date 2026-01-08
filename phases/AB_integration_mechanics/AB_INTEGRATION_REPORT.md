# Direction C: A-B Integration Mechanics

**Phase:** AB_INTEGRATION
**Date:** 2026-01-07
**Status:** CLOSED

---

## Scope Constraints (Pre-Committed)

This analysis was BOUNDED to:
- 4 specific tests (C-1 through C-4)
- Hard stop on: integration < 5%, no pattern survives null
- Max 2 Tier 2 constraints
- No semantic interpretation of what tokens mean

---

## Executive Summary

| Test | Finding | Verdict |
|------|---------|---------|
| **C-1: A-vocabulary in B** | 69.8% of B tokens appear in A | SUBSTANTIAL |
| **C-2: Section source** | H=66.8%, P=27.1%, T=6.1% | H DOMINANT |
| **C-3: Access pattern** | Adjacent sim=0.548, Random=0.404; Similar-B=0.427 | BOTH SEQUENTIAL + SEMANTIC |
| **C-4: Predictive power** | Mean R-sq=0.050, but 9/10 tokens have significant correlations | WEAK OVERALL |

**Overall:** A and B share MASSIVE vocabulary (69.8% token overlap). Access pattern is HYBRID: both sequential (by manuscript order) and semantic (by program similarity). Direction C is now CLOSED.

---

## C-1: A-Vocabulary Presence in B Folios

**Question:** What percentage of B vocabulary overlaps with A?

### Results

| Metric | Value |
|--------|-------|
| B tokens in A vocabulary | 52,668 / 75,545 (69.7%) |
| B types in A vocabulary | 1,532 / 7,263 (21.1%) |
| Per-folio mean | 69.8% |
| Per-folio std | 6.1% |
| Per-folio range | 49.5% - 84.6% |

### Interpretation

**SUBSTANTIAL.** Nearly 70% of all B tokens also appear in A. This is dramatically higher than expected if A and B were truly "disjoint" in vocabulary.

**Key insight:** A and B share a COMMON VOCABULARY CORE. The "disjunction" is at the FOLIO level (no shared folios) and GRAMMAR level (different rules), not vocabulary level.

---

## C-2: A-Section Source Identification

**Question:** When A-vocabulary appears in B, which A-section does it come from?

### Results

| Section | Shared Tokens in B | % | A Baseline | Ratio |
|---------|-------------------|---|------------|-------|
| H | 35,165 | 66.8% | 71.8% | 0.93x |
| P | 14,276 | 27.1% | 21.3% | 1.27x |
| T | 3,227 | 6.1% | 7.0% | 0.88x |

Chi-square: p < 0.000001 (sections NOT proportional to baseline)

### Interpretation

**H DOMINANT** but Section P is slightly ENRICHED (1.27x vs baseline).

Section H vocabulary dominates B procedures, consistent with CAS-XREF finding (91.6% of B folios reference H-vocabulary). Section P shows modest enrichment - procedures use MORE P-vocabulary than expected from A's section distribution.

---

## C-3: Sequential vs Semantic Access Pattern

**Question:** Does A-reference correlate with B-folio adjacency (sequential access) or B-program similarity (semantic lookup)?

### Sequential Access Test

| Comparison | A-Reference Similarity |
|------------|----------------------|
| Adjacent B folios | 0.548 |
| Non-adjacent B folios | 0.404 |

Mann-Whitney test: p < 0.000001

**RESULT: SEQUENTIAL ACCESS DETECTED.** Adjacent B folios share more A-vocabulary than random pairs.

### Semantic Access Test

| Comparison | A-Reference Similarity |
|------------|----------------------|
| Similar B-signature folios | 0.427 |
| Dissimilar B-signature folios | 0.256 |

Mann-Whitney test: p = 0.009

**RESULT: SEMANTIC ACCESS DETECTED.** B folios with similar operational signatures share more A-vocabulary.

### Interpretation

**HYBRID ACCESS MODEL:** Operators use BOTH strategies:

1. **Sequential:** Working through B folios in order, each draws on nearby A-vocabulary
2. **Semantic:** Choosing B programs for similar tasks draws on similar A materials

This suggests the manuscript was designed for an operator who:
- Reads procedures in approximate sequence (not jumping randomly)
- Returns to similar procedures for similar materials (not random selection)

---

## C-4: Predictive Power (B-Signature to A-Reference)

**Question:** Can B operational signature predict which A-tokens appear?

### Results

| Metric | Value |
|--------|-------|
| Mean R-squared | 0.050 |
| Max R-squared | 0.687 |
| Min R-squared | 0.001 |
| Significant token correlations | 9/10 |

### Top Token Correlations

| Token | r(LINK) | p | r(kernel) | p |
|-------|---------|---|-----------|---|
| qokain | 0.453* | <0.0001 | 0.432* | <0.0001 |
| ol | 0.355* | 0.001 | 0.080 | 0.47 |
| qokaiin | 0.353* | 0.001 | 0.210 | 0.06 |
| chey | 0.278* | 0.01 | 0.278* | 0.01 |
| qokeey | 0.269* | 0.01 | 0.495* | <0.0001 |
| shedy | 0.146 | 0.19 | 0.488* | <0.0001 |
| qokedy | 0.167 | 0.13 | 0.481* | <0.0001 |
| chedy | 0.073 | 0.51 | 0.257* | 0.02 |
| or | 0.230* | 0.04 | -0.020 | 0.86 |
| aiin | 0.130 | 0.24 | 0.047 | 0.67 |

### Interpretation

**WEAK OVERALL but STRONG for specific tokens.** B-signature (LINK density, kernel contact) cannot predict the full A-reference pattern, but individual tokens show significant correlations:

- `ol` correlates with LINK density (0.355) - unsurprising since `ol` IS the LINK marker
- `qo`-family tokens correlate with kernel contact - these are procedurally significant
- `chey`, `shedy` correlate with both dimensions

The weak overall R-squared (0.050) means knowing a B-program's operational signature tells you little about WHICH specific A-tokens will appear. But it does tell you something about certain high-frequency tokens.

---

## What These Tests Prove

### A and B are NOT Vocabulary-Disjoint

1. **69.8% token overlap:** The majority of B execution uses A vocabulary
2. **Shared type pool:** 1,532 types appear in both
3. **All folios affected:** Range 49.5%-84.6% per folio

**Conclusion:** A and B are FOLIO-disjoint and GRAMMAR-disjoint, but VOCABULARY-integrated.

### Access is HYBRID (Sequential + Semantic)

1. **Sequential:** Adjacent B folios share more A-vocab (p < 0.000001)
2. **Semantic:** Similar B-programs share more A-vocab (p = 0.009)

**Conclusion:** Operators both read sequentially AND lookup by similarity. The manuscript supports BOTH navigation modes.

### B-Signature Has Limited Predictive Power

1. **Overall R-sq = 0.050:** Knowing operational signature doesn't determine A-vocabulary
2. **But 9/10 top tokens correlate significantly:** Individual token presence CAN be predicted
3. **Token-specific patterns:** `ol`, `qo`-family have strong B-signature correlations

**Conclusion:** A-reference is partially but not fully determined by B program characteristics.

---

## Constraints to Add

### Constraint 335 (Tier 2)
**A-B vocabulary integration:** 69.8% of B tokens appear in A vocabulary; A and B are FOLIO-disjoint and GRAMMAR-disjoint but VOCABULARY-integrated; 1,532 shared types across 83 B folios.

### Constraint 336 (Tier 2)
**Hybrid A-access pattern:** Adjacent B folios share more A-vocabulary (0.548 vs 0.404, p < 0.000001) AND similar B-programs share more A-vocabulary (0.427 vs 0.256, p = 0.009); operators use BOTH sequential reading and semantic lookup.

---

## Hard Stop Evaluation

| Condition | Status |
|-----------|--------|
| Integration < 5%? | NO (69.8%) |
| No pattern survives? | NO (both sequential and semantic detected) |
| Max 2 constraints? | YES (2 Tier 2) |

**STOP CONDITION 3 APPLIES:** 2 Tier 2 constraints found. Direction C is CLOSED.

---

## What This Changes

### Previous Understanding (CAS-XREF)
- A and B are on completely different folios (0 shared)
- Section H dominates B (91.6%)
- A is categorical registry, B is executable grammar

### New Understanding (AB_INTEGRATION)
- A and B share 69.8% TOKEN-level vocabulary despite folio separation
- Access is HYBRID: sequential (by manuscript order) + semantic (by program similarity)
- The "disjunction" is structural (grammar, folios) not lexical (vocabulary)

### Operational Model Revision
An operator using this manuscript would:
1. **Read B programs in approximate sequence** (sequential access supported)
2. **Return to similar programs for similar tasks** (semantic access supported)
3. **Draw on a shared vocabulary pool** that appears in both A catalog and B procedures
4. **But use different GRAMMAR** when in A (categorical) vs B (procedural)

---

## Direction C: CLOSED

All four tests complete. A-B integration investigation is now FINISHED.

**Outcome:** 2 Tier 2 constraints added. Vocabulary integration is substantial (69.8%), access is hybrid.

No further A-B integration investigation is warranted.

---

## Files

| File | Purpose |
|------|---------|
| `ab_integration_tests.py` | Test implementation |
| `ab_integration_results.json` | Raw results |
| `AB_INTEGRATION_REPORT.md` | This document |

---

*Direction C: CLOSED*
*Generated: 2026-01-07*
