# Plant Part Encoding Test - Verdict

**Phase:** SPEC-A (Addendum)
**Tier:** 2 (STRUCTURAL TEST)
**Date:** 2026-01-06

---

## Question

Do Currier A prefixes/suffixes encode **plant parts** (root, flower, leaf)?

---

## Tests Performed

### Test 1: Plant Type Correlation
- **Data:** 15 Currier A folios classified by plant TYPE (Aromatic Flower, Aromatic Leaf Herb, Aromatic Shrub, Medicinal Herb)
- **Tokens:** 3,748

| Result | Value |
|--------|-------|
| Chi-square | 106.32 |
| P-value | < 0.0001 |
| Cramér's V | 0.124 (small) |

**Finding:** Statistically significant WEAK association between PREFIX and plant type.

### Test 2: Plant Part Correlation
- **Data:** 28 Currier A folios classified by plant PART emphasis (Root, Flower, Leaf)
- **Tokens:** ~7,000

| Result | Value |
|--------|-------|
| Chi-square | 98.04 |
| P-value | < 0.0001 |
| Cramér's V | 0.100 (negligible/small boundary) |

**Finding:** Statistically significant but NEGLIGIBLE effect size.

---

## Prefix Differentials by Plant Part

| PREFIX | ROOT | FLOWER | LEAF | Max Differential |
|--------|------|--------|------|------------------|
| SH | 18.4% | 12.7% | 11.7% | **6.6%** |
| OT | 5.4% | 11.9% | 7.1% | **6.5%** |
| OK | 6.9% | 5.4% | 9.2% | 3.8% |
| QO | 12.8% | 14.0% | 15.2% | 2.4% |
| CH | 28.0% | 26.7% | 26.8% | 1.2% |
| DA | 16.9% | 16.7% | 17.4% | 0.7% |
| OL | 2.5% | 3.1% | 3.1% | 0.6% |
| CT | 9.2% | 9.4% | 9.5% | 0.4% |

**Maximum differential: 6.6%** (SH prefix)

---

## Interpretation

### What the Numbers Mean

- **Cramér's V = 0.100** is at the boundary between "negligible" and "small"
- **6.6% maximum differential** means prefix distributions are 93%+ similar across plant parts
- **Statistical significance with tiny effect** = real pattern but practically meaningless

### Comparison to Strong Encoding

If plant parts WERE encoded in prefixes, we'd expect:
- Cramér's V > 0.3 (medium to large effect)
- Differential > 20% for at least one prefix
- Clear "signature" prefixes for each plant part

We observe:
- V = 0.100 (negligible)
- Max differential = 6.6%
- No clear signatures

---

## Verdict

**PLANT PARTS ARE NOT MEANINGFULLY ENCODED in Currier A prefixes.**

The PREFIX system is largely **independent** of the botanical morphology shown in illustrations.

### What This Means

1. **PREFIX ≠ "root" vs "flower" vs "leaf"**
2. The compositional system classifies something OTHER than plant anatomy
3. Illustrations and text operate on different classification axes
4. This is consistent with the ILL phase finding (illustration independence)

### Possible PREFIX Meanings (Still Speculative)

If not plant parts, prefixes might encode:
- Processing states (fresh, dried, extracted)
- Product categories (waters, oils, powders)
- Material families (herbs, flowers, resins)
- Quality grades
- Usage contexts

---

## Constraint Update

**No new constraint added.** This test CONFIRMS existing findings:
- Constraint 137-140 (Illustration Independence) remains valid
- Illustrations are epiphenomenal to the classification system
- Text encodes something other than botanical morphology

---

## Caveats

1. Morphology classifications for Currier A are preliminary (need visual verification)
2. Sample size is limited (28 folios)
3. Classification is by emphasis, not absolute (most plants show multiple parts)

A more rigorous test would require:
- Blind morphology classification by multiple raters
- Larger sample with verified Currier A/section H overlap
- Control for folio adjacency effects

---

*Test performed with available data. Conclusion robust to reasonable classification errors.*
