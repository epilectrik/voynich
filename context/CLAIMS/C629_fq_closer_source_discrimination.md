# C629: FQ_CLOSER Source Token Discrimination

**Tier:** 2 | **Status:** CLOSED | **Scope:** CURRIER_B | **Source:** FQ_CLOSER_BOUNDARY_HAZARD

## Statement

Forbidden sources (dy, l) within Class 23 are distinguished from non-forbidden tokens (y, am, s, r, d) by near-zero c9 restart rate, lower hazard successor rate, higher EN_CHSH successor rate, and section B over-representation. The class-level 23→9 restart enrichment (2.85x, C595) is carried almost entirely by s (48.6%) and r (25.9%); dy contributes 0%. dy functions as a generalist distributor (22 successor classes, entropy 4.179) rather than a restart specialist. Contextual divergence is moderate (JSD=0.219), with forbidden sources concentrating in section B (42% vs 22%).

## Evidence

### Successor Profile

| Token | Freq | Successors | c9% | EN_CHSH% | Hazard% | Forbidden? |
|-------|------|------------|-----|----------|---------|------------|
| dy | 109 | 51 | 0.0% | 3.9% | 15.7% | YES |
| y | 66 | 42 | 4.8% | 14.3% | 21.4% | no |
| am | 55 | 8 | 0.0% | 25.0% | 37.5% | no |
| s | 53 | 37 | 48.6% | 0.0% | 70.3% | no |
| r | 39 | 27 | 25.9% | 3.7% | 48.1% | no |
| l | 34 | 27 | 3.7% | 22.2% | 40.7% | YES |
| d | 6 | 4 | 0.0% | 0.0% | 0.0% | no |

### Aggregate Comparison

| Metric | Forbidden (dy, l) | Non-Forbidden | Direction |
|--------|-------------------|---------------|-----------|
| Hazard successor rate | 28.2% | 35.5% | Forbidden LOWER |
| EN_CHSH successor rate | 13.1% | 8.6% | Forbidden HIGHER |
| c9 restart rate | 1.8% | 15.9% | Forbidden NEAR-ZERO |
| Hazard predecessor rate | 20.1% | 46.8% | Forbidden LOWER |
| Section B rate | 42.0% | 21.9% | Forbidden HIGHER |
| Context JSD | 0.219 | — | Moderate divergence |

### Morphological Properties

All Class 23 tokens are morphologically bare (no prefix, suffix, or articulator). Forbidden sources are not morphologically distinct. l is a kernel primitive (C085); dy is not. Mean length: forbidden=1.5, non-forbidden=1.2 (not discriminative).

## Interpretation

The class-level restart enrichment (23→9 at 2.85x) masks extreme within-class heterogeneity: s is a dedicated restart operator (48.6% → c9) while dy is a generalist (0% → c9). This suggests Class 23 contains at least two functional sub-populations: restart specialists (s, r) and general distributors (dy, l, y). The forbidden-source tokens (dy, l) belong to the distributor sub-population, which has broader successor diversity but lower hazard concentration. The s→aiin bigram alone accounts for 18/28 = 64% of all c23→c9 transitions.

## Extends

- **C595**: Reveals within-class heterogeneity hidden by aggregate enrichment
- **C597**: Class 23 boundary dominance is carried by different tokens for different functions

## Related

C593, C595, C597, C627, C628, C630
