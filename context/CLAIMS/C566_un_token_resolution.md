# C566: UN Token Resolution

**Tier:** 2 (Structural Inference)
**Scope:** B
**Phase:** AUXILIARY_STRATIFICATION
**Status:** VALIDATED

## Claim

The 7,042 unclassified (UN) tokens in Currier B are not a separate role or structural gap. They are valid B tokens too rare for cosurvival-based class assignment, produced by productive morphological combination.

## Evidence

### Token Statistics

| Metric | Value |
|--------|-------|
| Total B tokens (H-track) | 23,096 |
| Classified (in class_token_map) | 16,054 (69.5%) |
| Unclassified (UN) | 7,042 (30.5%) |
| Unique UN types | 4,421 |
| Hapax legomena | 3,274 (74.1% of UN types) |
| Single-folio types | 3,306 (74.8% of UN types) |
| Uncertain readings (*) | 0 (0.0%) |

### Primary Cause: Insufficient Distributional Data

The cosurvival test requires tokens to appear in multiple folios for class assignment. UN tokens fail this requirement:

- 74.8% of UN types appear in exactly 1 folio
- For comparison, only 2.8% of classified types appear in 1 folio
- This is a methodological threshold effect, not a structural gap

### Morphological Normality

UN tokens have the same morphological distribution as classified tokens:

| Component | Top UN Values | Comparable to |
|-----------|---------------|---------------|
| Prefix | ch (13.9%), qo (12.3%), sh (10.4%) | EN prefix families |
| Middle | e, ed, d, l, k | Standard B middles |
| Suffix | edy (9.0%), dy (8.1%), ar (6.4%) | Standard B suffixes |
| Articulator rate | 10.1% | Within normal range |

### Nearest Class by Prefix

The most frequent UN tokens predict to existing classes by prefix similarity:
- ch-prefix UN tokens -> Class 34 (ENERGY)
- qo-prefix UN tokens -> Class 33 (ENERGY)
- ol-prefix UN tokens -> Class 17 (CC)
- ok-prefix UN tokens -> Class 13 (FQ)

### Folio Distribution

UN rate varies by folio (15.5% to 47.2%) but is present everywhere. No folio is UN-free. This is consistent with productive morphology generating rare forms uniformly.

## Interpretation

The 30.5% UN rate reflects the **productivity** of the morphological system, not a gap in analysis. Compositional morphology (PREFIX + MIDDLE + SUFFIX) generates a long tail of rare forms. The cosurvival test correctly classifies the frequent head of the distribution (69.5%) but cannot classify the rare tail due to insufficient co-occurrence data.

UN tokens would likely classify into existing classes if more data were available. This does not affect any structural findings, which are based on the classified 69.5%.

## Cross-References

- C121: 49-class grammar (based on cosurvival test)
- C267: Compositional morphology (explains UN generation mechanism)
- C293: TOKEN = [ARTICULATOR] + [PREFIX] + MIDDLE + [SUFFIX]
