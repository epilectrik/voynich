# C769: Compound Structure Context Prediction

## Constraint

Compound MIDDLE structure predicts token context: line position, folio vocabulary uniqueness, and instruction class. Compound usage is not random.

## Quantitative Evidence

### Line Position Effect
- Line-1 compound rate: **40.4%**
- Body compound rate: **35.4%**
- Difference: +5.0pp

For UN tokens specifically:
- Line-1 UN: 51.1% compound
- Body UN: 46.1% compound
- Difference: +5.0pp

### Folio Uniqueness Correlation
- Correlation (compound rate vs folio-unique rate): **r = 0.553**
- Strong positive: folios with more compound tokens have more unique vocabulary

### Folio Variation
- Mean compound rate across folios: 34.7%
- Standard deviation: 6.4%
- Range: 21.1% - 50.0%

### Class Variation
Compound rate varies dramatically by class:
- 21 classes: 0-5% compound (base-only)
- 3 classes: 85%+ compound (compound-heavy)
- Within roles: FL=0%, FQ=46.7% (46.7pp spread)

## Predictions

1. **Line-1 tokens are more compound** (+5pp) - identification layer
2. **High-compound folios have unique vocabulary** (r=0.55) - derivation serves identification
3. **FL uses base vocabulary** (0% compound) - flow control is primitive
4. **FQ uses derived vocabulary** (46.7% compound) - frequent operations are complex

## Implications

Compound structure is not noise - it carries structural information about:
- Token function (line-1 identification vs body operation)
- Folio identity (unique vocabulary via derivation)
- Grammatical role (FL vs FQ vocabulary split)

## Tier

**Tier 2** - Empirically validated structural relationship

## Source

- Phase: COMPOUND_MIDDLE_ARCHITECTURE
- Test: T5 (t5_compound_predictors.py)
- Data: 23,096 B tokens, 83 folios, 48 classes
