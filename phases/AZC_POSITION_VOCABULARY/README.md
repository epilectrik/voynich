# Phase: AZC_POSITION_VOCABULARY

**Date:** 2026-01-31
**Status:** COMPLETE
**Verdict:** TIER 2 STRUCTURAL

---

## Summary

AZC positions are static vocabulary clusters. Each PREFIX+MIDDLE combination appears at exactly ONE AZC position. Position reflects the vocabulary's operational character, not a causal effect on execution.

**Key Finding:** Position has NO independent effect beyond vocabulary composition. The same MIDDLE shows identical B behavior regardless of AZC position.

---

## Critical Clarification

**AZC is NOT:**
- A filter that selects/blocks tokens
- A gate that controls execution flow
- A router that directs content
- An active transformation layer

**AZC IS:**
- A static lookup table (PREFIX+MIDDLE → position)
- A vocabulary classifier (position reflects operational character)
- A positional encoding (each token type has one fixed position)

---

## Evidence

### Test 1: PREFIX-MIDDLE Correlation (Script 15)

**Question:** Are PREFIX and MIDDLE correlated?

**Result:** Chi-squared = 13,916, p ≈ 0

**Finding:** PREFIX and MIDDLE are STRONGLY DEPENDENT. Knowing the MIDDLE predicts the PREFIX distribution.

| MIDDLE type | Dominant PREFIX | Overlap with other |
|-------------|-----------------|-------------------|
| qo-dominant | k, ke, kch, t, te, tch | 0% (Jaccard = 0.000) |
| chsh-dominant | od, ol, ody, ai | 0% (Jaccard = 0.000) |

**Implication:** "Escape rate" (qo/ct frequency) is entirely predictable from MIDDLE composition.

---

### Test 2: AZC Position Independent Effect (Script 16)

**Question:** Does AZC position affect PREFIX distribution independently of MIDDLE?

**Method:** For MIDDLEs appearing at multiple positions, test if PREFIX distribution varies by position.

**Result:** Only 5-10% of MIDDLEs show position effect (at p<0.05 threshold).

**Finding:** NO SIGNIFICANT POSITION EFFECT. PREFIX distribution is determined by MIDDLE, not position. AZC position "escape rates" are purely vocabulary composition effects.

---

### Test 3: S-Position Vocabulary (Script 17)

**Question:** What distinguishes S-position vocabulary?

**Result:**
| Position | ok/ot rate | qo/ct (escape) rate |
|----------|------------|---------------------|
| S0 | 42.1% | 0.5% |
| S1 | 43.2% | 0.5% |
| S2 | 45.2% | 0.0% |
| R-series | 28-31% | 1-2% |

**Finding:** S-series has distinct MIDDLE inventory (Jaccard S/R = 0.196). The vocabulary at S positions is intrinsically stabilization-oriented.

---

### Test 4: Position vs B Grammar (Script 18)

**Question:** Does AZC position predict B grammar behavior?

**Results:**

| Test | Chi-squared | p-value | Significant? |
|------|-------------|---------|--------------|
| Position × Class | 13,950 | <0.001 | Yes (confounded) |
| Position × REGIME | 327 | <0.001 | Yes (confounded) |
| Position × Hazard | 658 | <0.001 | Yes (confounded) |
| Position effect controlling for MIDDLE | 0/10 | n/a | **NO** |

**Finding:** All position effects are CONFOUNDED with MIDDLE composition. After controlling for MIDDLE, position adds ZERO predictive power for B behavior.

---

### Test 5: Position Vocabulary Signatures (Script 19)

**Question:** What do positions represent based on vocabulary character?

**IMPORTANT:** P (Paragraph) is NOT a diagram position - it is paragraph text that appears on AZC folios but is physically separate from the circular diagrams. See `azc_transcript_encoding.md`. P is included in raw data but should be excluded from diagram position analysis.

**Results (including P for comparison):**

| Position | N | Kernel% | EN% | AX% | ok/ot% | qo% |
|----------|---|---------|-----|-----|--------|-----|
| C | 635 | 28.0% | 23.9% | 29.4% | 20.5% | 1.1% |
| *P (not diagram)* | 398 | 31.4% | **36.2%** | 31.2% | 10.3% | **7.8%** |
| R1 | 483 | 37.1% | 21.5% | 27.9% | 30.4% | 2.3% |
| R2 | 413 | 29.3% | 22.3% | 21.9% | 28.6% | 1.0% |
| R3 | 208 | 38.0% | 22.0% | 22.0% | 30.8% | 0.0% |
| S | 505 | 26.7% | **12.5%** | **39.7%** | **41.4%** | 1.0% |
| S1 | 199 | 26.6% | 6.1% | **45.5%** | **43.2%** | 0.5% |
| S2 | 146 | 17.8% | 8.8% | 35.3% | **45.2%** | 0.0% |

**Diagram Position Vocabulary Signatures (C, R, S only):**

| Position | Character | Key Indicators |
|----------|-----------|----------------|
| **S-series** | Stabilization/boundary | Highest AX% (35-45%), highest ok/ot% (41-45%), lowest EN% (6-12%) |
| **R-series** | Processing/interior | Balanced profile, moderate kernel contact |
| **C** | Core/central | Balanced, moderate on all axes |

*P (Paragraph) is Currier A material, not diagram text - its distinct vocabulary (high EN%, high qo%) reflects A registry characteristics, not diagram position.*

---

## Conclusion

AZC **diagram** positions (C, R, S only) cluster vocabulary by operational character:

1. **S positions** = stabilization vocabulary (conservative, boundary-marking)
2. **R positions** = processing vocabulary (balanced, interior operations)
3. **C position** = core vocabulary (balanced)

*Note: P (Paragraph) is NOT a diagram position. It is Currier A text that appears on AZC folios but is physically separate from the circular diagrams.*

The position does NOT DO anything to the token. It REFLECTS the token's intrinsic operational nature. Position is a consequence of vocabulary type, not a cause of behavior.

---

## Constraints Affected

This analysis clarifies (not changes) existing constraints:

- **C441** (Vocabulary-Activated Constraints): Clarified - vocabulary activates positional encoding
- **C442** (Compatibility Filter): REFRAMED - "compatibility grouping" not "filter"
- **C443** (Positional Escape Gradient): Clarified - escape rate reflects vocabulary composition, not positional effect
- **C444** (A-Type Position Distribution): Confirmed - same material can appear at any position (it's the MIDDLE that determines typical position)

---

## Scripts

Evidence scripts are in `phases/A_PP_INTERNAL_STRUCTURE/scripts/`:

| Script | Test |
|--------|------|
| `15_prefix_middle_correlation.py` | PREFIX-MIDDLE dependency |
| `16_azc_position_middle_test.py` | Position independent effect |
| `17_s_position_analysis.py` | S-position vocabulary |
| `18_azc_position_b_grammar_test.py` | Position vs B grammar |
| `19_azc_position_vocabulary_analysis.py` | Position vocabulary signatures |

---

## Navigation

← [AZC_REASSESSMENT](../AZC_REASSESSMENT/) | [A_PP_INTERNAL_STRUCTURE](../A_PP_INTERNAL_STRUCTURE/) →
