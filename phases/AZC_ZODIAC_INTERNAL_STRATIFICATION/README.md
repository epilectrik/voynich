# AZC INTERNAL STRATIFICATION Phase

**Status:** COMPLETE | **Result:** FALSIFIED (both families) | **Date:** 2026-01-15

---

## Question

> Do different AZC folios preferentially admit different regions of Currier-A incompatibility space, and do those regions align with downstream B-inferred product families?

**Critical framing note:** This is NOT a test of "product routing through gates." AZC filters constraint bundles; product types are downstream inferences from B behavior.

---

## Background

**Zodiac family:**
- C321: Each Zodiac folio has independent vocabulary (Jaccard 0.076)
- C431: Zodiac folios are "structural clones" (0.964 similarity)
- C472: MIDDLE is the primary carrier of folio specificity

**A/C family:**
- C430: A/C family has LOW cross-folio consistency (0.340 vs Zodiac 0.945)
- Each A/C folio has its own scaffold

The question: Does vocabulary independence represent internal stratification of the legality manifold correlated with product types, or is it purely structural?

---

## Method

For both Zodiac and A/C families:

1. Extract product-associated MIDDLEs from B folios (by REGIME classification)
2. Map those MIDDLEs to AZC folios
3. Test for clustering via chi-squared test of independence

---

## Results

### Zodiac Family (13 folios: 12 zodiac + f57v)

**Data:** 75,173 B tokens, 3,368 Zodiac AZC tokens, 2,777 product-exclusive MIDDLEs

**Chi-squared test:**
- Statistic: 27.32
- Degrees of freedom: 36
- **P-value: 0.85**

**Distribution entropy:** All products show near-maximum entropy (spread across all folios)

**Enrichment:** No folio shows >23% of any product's MIDDLEs

### A/C Family (17 folios)

**Data:** 75,173 B tokens, 5,607 A/C AZC tokens, 2,777 product-exclusive MIDDLEs

**Chi-squared test:**
- Statistic: 46.67
- Degrees of freedom: 42
- **P-value: 0.29**

**Distribution entropy:** All products spread across folios (OIL_RESIN lower due to sparse data)

**Enrichment:** No folio shows >25% of any product's MIDDLEs

---

## Verdict

| Family | P-value | Verdict |
|--------|---------|---------|
| Zodiac | 0.85 | NO STRATIFICATION |
| A/C | 0.29 | NO STRATIFICATION |

**Both families show NO STRATIFICATION** (p >> 0.05)

The null hypothesis is strongly confirmed for both AZC families.

---

## Interpretation

> **AZC is uniformly product-agnostic. Neither Zodiac nor A/C families show internal stratification correlated with downstream product inference.**

**Zodiac:** Multiplicity exists purely for coverage optimality. The 12 Zodiac folios are structurally equivalent gates.

**A/C:** Scaffold diversity (consistency=0.340) does NOT correlate with product types. The variation exists for other structural reasons.

---

## Implications

1. **Validates existing model** — AZC folios filter constraint bundles uniformly
2. **No hidden routing** — Product differentiation is NOT encoded at the AZC level
3. **Coverage is the answer** — AZC needed multiple folios to cover the full MIDDLE space, not to stratify it
4. **A/C diversity is non-semantic** — Scaffold variation does not map to product categories

---

## Documentation

| Test | FIT | Result |
|------|-----|--------|
| Zodiac stratification | F-AZC-017 | FALSIFIED |
| A/C stratification | F-AZC-018 | FALSIFIED |

**Results files:**
- `results/zodiac_stratification.json`
- `results/ac_stratification.json`

---

## Scripts

| File | Purpose |
|------|---------|
| `zodiac_stratification_test.py` | Zodiac family test |
| `ac_stratification_test.py` | A/C family test |

---

*Phase completed 2026-01-15*
