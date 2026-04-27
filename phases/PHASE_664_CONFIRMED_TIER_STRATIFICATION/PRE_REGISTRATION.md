# Phase 664 — Pre-Registration

**Locked:** 2026-04-26
**Type:** Confirmatory hypothesis test (match-tier stratification)
**Motivation disclosure:** Phase 663's pre-registered sensitivity check produced an incidental observation: CONFIRMED-match paragraphs (n=12, mean ke/ek=9.74) vs supported-match paragraphs (n=83, mean=5.03). This phase tests that observation as a primary hypothesis with locked methodology.

This is **borderline HARKing** in spirit (the partition is chosen because the prior sensitivity check suggested it). Mitigation: methodology is locked before run; failure mode is specified; transparent disclosure that motivation came from a sensitivity-check observation. This is acceptable per pre-registration discipline IF the test result is reported honestly regardless of outcome.

---

## Context

Phases 661+662+663 established that verb-corpus partition tests at folio-binary or paragraph-distribution resolution don't produce constraints. Phase 663's REVERSED-NULL was driven (per sensitivity check) by within-positive heterogeneity: CONFIRMED-match paragraphs cluster at higher ke/ek than supported-match paragraphs.

**This phase tests whether the CONFIRMED tier itself has structurally distinct paragraph-level signatures from the supported tier.**

If supported, the implication is methodologically important: match-tier should stratify partition tests on this corpus. CONFIRMED-tier matches share a structural signature that supported-tier matches don't reliably reproduce. Future verb-corpus tests should restrict to CONFIRMED matches as a primary partition.

---

## Hypothesis

**T1 (primary):** CONFIRMED-match paragraphs (n=12) show higher ke/ek ratio than supported-match paragraphs (n=83) within the existing matched-pair table.

**H₀:** No difference between match-tier paragraph distributions.

**Falsification:** REVERSED direction OR no significance.

---

## Locked decisions

### 1. Partition (locked)

**Positive group:** Paragraphs from CONFIRMED matches.
- f75r (matched III.19, aqua vitae, CONFIRMED)
- f76r (matched II.18, element separation, CONFIRMED)
- f84r (matched II.14, gold dissolution, CONFIRMED)

Total expected: 12 paragraphs (per Phase 663 extraction with min 8-token threshold).

**Negative group:** Paragraphs from supported matches that are also superclass-positive (i.e., contained at least one thermal-iteration verb in matched Catalan chapter, per Phase 662 partition).
- f112r, f82v, f79r, f82r, f103r, f81v, f112v, f116r, f107r

Total expected: 83 paragraphs.

**Excluded:** superclass-negative folios (f76v, f77v) — they would dilute the test by adding folios with NO thermal-iteration verbs at all.

### 2. Test signature (locked)

**Primary endpoint:** ke/ek ratio per paragraph (same metric as Phases 661/662/663). Single candidate, no exploration.

### 3. Statistical test (locked)

One-sided permutation Mann-Whitney U (10,000 perms). Predicted direction: CONFIRMED > supported.

### 4. Effect-size threshold (locked)

Cohen's d on the paragraph distributions:
- d ≥ 0.5 required for SUPPORTED verdict (medium effect)
- d ≥ 0.3 for DIRECTIONAL

The original sensitivity check showed mean difference 9.74 - 5.03 = 4.71 in raw ke/ek, but variances within each group were not reported. Cohen's d will reveal whether the mean difference reflects signal or distributional overlap.

### 5. Verdicts

| Verdict | Criterion |
|---|---|
| SUPPORTED | predicted direction + p ≤ 0.05 + Cohen's d ≥ 0.5 |
| DIRECTIONAL | predicted direction + p ≤ 0.20 + d ≥ 0.3 |
| INCONCLUSIVE | predicted direction but p > 0.20 OR d < 0.3 |
| REVERSED-NULL | OPPOSITE direction p ≤ 0.10 |
| FALSIFIED | OPPOSITE direction p ≤ 0.05 |

### 6. What this phase does NOT do

- No additional signature exploration (single candidate: ke/ek)
- No expansion of CONFIRMED tier (only f75r, f76r, f84r per existing C1925/C1959 references)
- No re-categorization of folios after testing
- No constraint registration without ALSO requiring the effect to survive a corpus-wide sanity check (T2 secondary)

### 7. T2 secondary (corpus-wide sanity check, locked)

To address the concern that CONFIRMED matches were SELECTED for being well-matched (potentially circular), report a third comparison:

**T2:** CONFIRMED-match paragraph mean ke/ek vs corpus-wide Currier B paragraph mean ke/ek (all unmatched paragraphs from all 82 folios with ≥8 tokens).

If CONFIRMED paragraphs are simply at the corpus-wide mean (no special elevation), the T1 finding is just "supported-tier matches happen to be below average" — interesting but limited.

If CONFIRMED paragraphs are ELEVATED above corpus-wide mean AND above supported-tier mean, the finding is more substantive: CONFIRMED matches share a high-ke/ek signature that's both rare in the broader corpus AND not present in supported-tier matches.

T2 is descriptive, not load-bearing on T1's verdict.

---

## Honest expectation

T1 likely SUPPORTED based on the sensitivity-check observation, but small N (12 paragraphs) means even a strong effect may not reach p≤0.05.

T2 is the load-bearing question: does the CONFIRMED signature stand out from the corpus, or are CONFIRMED matches just at average and supported matches below average? The interpretation differs significantly between these two readings.

If T1 SUPPORTED and T2 shows CONFIRMED above corpus mean: real finding worth registering as match-tier-specific signature constraint (Tier 2-3).

If T1 SUPPORTED but T2 shows CONFIRMED at corpus mean: pattern is real but less interesting (just a methodological caveat about supported-tier).

If T1 INCONCLUSIVE/null: the sensitivity-check pattern was noise, and we close out the entire verb-corpus partition arc.
