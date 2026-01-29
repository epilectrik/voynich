# C628: FQ_CLOSER Positional Segregation Test

**Tier:** 2 | **Status:** CLOSED | **Scope:** CURRIER_B | **Source:** FQ_CLOSER_BOUNDARY_HAZARD

## Statement

Of the 3 unexplained forbidden pairs from C627 (all originating from FQ_CLOSER Class 23), two show genuine positional overlap with their target classes while one is positionally segregated. dy→chey and l→chol have 1 and 4 adjacencies respectively to their target classes (c31, c8) but zero adjacency to the specific forbidden target tokens. dy→aiin has zero adjacency to ANY c9 token, explained by dy's extreme final-position bias (35.8% line-final, mean normalized position 0.738 vs 0.484 for non-forbidden sources, Mann-Whitney p<0.000001). Boundary gap probability does NOT discriminate forbidden from allowed pairs (forbidden mean=0.003, allowed mean=0.004).

## Evidence

### Per-Token Positional Profiles (Class 23)

| Token | Count | Mean Pos | Final% | Forbidden? |
|-------|-------|----------|--------|------------|
| dy | 109 | 0.738 | 35.8% | YES |
| y | 66 | 0.389 | 15.2% | no |
| am | 55 | 0.947 | 80.0% | no |
| s | 53 | 0.529 | 15.1% | no |
| r | 39 | 0.563 | 7.7% | no |
| l | 34 | 0.507 | 2.9% | YES |
| d | 6 | 0.292 | 16.7% | no |

### Position Overlap Test

| Forbidden Pair | Non-final | Tgt Class After | Adj to Class | Adj to Token | Verdict |
|----------------|-----------|-----------------|--------------|--------------|---------|
| dy→aiin | 70 | 5 | 0 | 0 | POSITIONALLY_SEPARATED |
| dy→chey | 70 | 8 | 1 | 0 | GENUINE_PROHIBITION |
| l→chol | 33 | 12 | 4 | 0 | GENUINE_PROHIBITION |

### Mann-Whitney Source Position Comparison

| Context | Forb Source | Forb Mean | Allowed Mean | p-value |
|---------|------------|-----------|--------------|---------|
| c23→c9 | dy | 0.738 | 0.484 | <0.000001 |
| c23→c31 | dy | 0.738 | 0.613 | 0.073 |
| c23→c8 | l | 0.507 | 0.598 | 0.104 |

## Interpretation

dy's extreme final bias places it in a different positional stratum than other Class 23 tokens. In the c23→c9 context, this fully explains the zero dy→aiin observations: dy simply cannot reach c9 tokens because it occupies line-final positions where no successor exists. In the c23→c31 context, dy CAN reach c31 (1 adjacency observed: dy→shey) but specifically avoids chey, indicating a genuine token-level prohibition beyond position. l is centrally positioned (mean 0.507) and freely reaches c8 (4 adjacencies: l→chedy×2, l→shedy×2) but never l→chol -- however this requires frequency analysis to evaluate (see C630).

## Extends

- **C597**: Confirms Class 23 boundary dominance is token-specific (dy=35.8% final, l=2.9% final)
- **C627**: Resolves positional component of 3 unexplained pairs

## Related

C597, C627, C629, C630
