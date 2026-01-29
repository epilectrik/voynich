# C807: LINK-FL Inverse Relationship

## Constraint

LINK and FL (escape operators) are **inversely related**:

1. **Distance:** LINK is FARTHER from FL than non-LINK
   - LINK mean distance to FL: 3.91 tokens
   - Non-LINK mean distance to FL: 3.38 tokens
   - Mann-Whitney U: p < 0.0001

2. **Folio correlation:** LINK% and FL% are negatively correlated
   - rho = -0.222, p = 0.045

3. **Transition depletion:** LINK is depleted around FL tokens
   - Pre-FL LINK rate: 8.9% (0.67x baseline)
   - Post-FL LINK rate: 11.5% (0.87x baseline)

## Evidence

In lines containing FL tokens:
- LINK tokens: 982 (mean distance to FL: 3.91)
- Non-LINK tokens: 7,629 (mean distance to FL: 3.38)

Folio-level correlations:
- LINK% vs FL%: rho = -0.222, p = 0.045 (negative)
- LINK% vs HT%: rho = -0.524, p < 0.0001 (strongly negative)
- HT% vs FL%: rho = 0.150, p = 0.18 (not significant)

## Interpretation

LINK and FL represent **complementary phases**, not co-located operations:
- LINK = monitoring/waiting zones (C366)
- FL = active escape/recovery

This clarifies the architecture: HT correlates with escape at folio level (C796) but clusters near LINK (C802) because high-escape folios have more monitoring checkpoints. LINK and FL are spatially segregated.

## Provenance

- Phase: LINK_OPERATOR_ARCHITECTURE
- Script: t4_link_escape_path.py
- Related: C796, C802, C340

## Tier

2 (Validated Finding)
