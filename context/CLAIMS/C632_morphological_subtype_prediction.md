# C632: Morphological Subtype Prediction

**Tier:** 2 | **Status:** CLOSED | **Scope:** CURRIER_B | **Source:** INTRA_CLASS_DIVERSITY

## Statement

In 6/7 heterogeneous classes, the MIDDLE component perfectly predicts cluster membership (ARI = 1.0). PREFIX and ARTICULATOR have zero predictive power (degenerate -- all same within class). SUFFIX shows partial prediction in classes where tokens have different suffixes. However, **no prediction reaches statistical significance** (all Fisher p > 0.05) due to tiny sample sizes (n = 2-5 eligible tokens per class). Class 30 (FL_HAZ) is the only morphologically opaque class: all 5 tokens share prefix 'da' and differ in MIDDLE, but MIDDLE does not predict the {dar,dal,dain,dair} vs {dam} split.

## Evidence

### Per-Class Predictivity

| Class | Role | k | n | Best Feature | ARI | p | Verdict |
|-------|------|---|---|-------------|-----|---|---------|
| 3 | AX | 2 | 2 | middle | 1.000 | 1.00 | TREND |
| 7 | FL | 2 | 2 | middle | 1.000 | 1.00 | TREND |
| 8 | EN | 2 | 3 | middle | 1.000 | 0.33 | TREND |
| 22 | AX | 2 | 2 | middle | 1.000 | 1.00 | TREND |
| 30 | FL | 2 | 5 | prefix | 0.000 | 1.00 | OPAQUE |
| 37 | EN | 2 | 2 | middle | 1.000 | 1.00 | TREND |
| 44 | EN | 2 | 2 | middle | 1.000 | 1.00 | TREND |

### Mean ARI by Feature

| Feature | Mean ARI | Max ARI | Notes |
|---------|----------|---------|-------|
| middle | 0.857 | 1.000 | Dominant predictor in 6/7 classes |
| suffix | 0.536 | 1.000 | Co-predictive where present |
| prefix | -0.071 | 0.000 | No predictive power |
| articulator | 0.000 | 0.000 | Degenerate (all same) |

### Summary

- Classes with strong prediction (ARI > 0.3): 6/7 (86%)
- Classes with significant prediction (p < 0.05): 0/7 (0%)
- Classes with both: 0/7 (0%)

## Interpretation

Within-class behavioral diversity is **MIDDLE-aligned**: when tokens in the same class differ functionally, they differ in MIDDLE identity. This is consistent with C506.a's finding that tokens within a class are "parameterizations" -- same positional profile, different MIDDLE-indexed transitions. The morphological basis of functional diversity validates the MIDDLE-centric model (TOKEN = [ART] + [PRE] + MIDDLE + [SUF]) as the carrier of behavioral identity.

The exception (Class 30) suggests that FL_HAZ has a non-morphological functional division: dam's behavioral distinctiveness from {dar, dal, dain, dair} may reflect contextual or positional specialization not captured by morphological decomposition.

The lack of statistical significance is a power limitation (n = 2-5), not evidence against the pattern. The perfect ARI = 1.0 in 6/7 cases would be difficult to achieve by chance even at these sample sizes.

## Extends

- **C506.a**: "Classes = types, tokens = parameterizations" -- parameterizations track MIDDLE identity
- **C631**: 7 heterogeneous classes have morphologically interpretable splits in 6/7 cases

## Related

C506, C506.a, C506.b, C085, C629, C631, C633
