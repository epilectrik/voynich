# C1458: e→y Categorical Safety with OPERATION Enrichment

**Tier:** 2
**Scope:** B, MIDDLE, atom, e-HEAD, y-terminal, hazard, safety, category, OPERATION, TRANSITION, C1280, C1446, C1448
**Phase:** 525 (EY_SAFE_PATHWAY)
**Date:** 2026-03-05

## Claim

e→y has a hazard rate of 0.06% (2/3,475 tokens) vs corpus baseline 23.9% — a 400x hazard reduction. e→y is categorically enriched in OPERATION (3.94x) and TRANSITION (1.73x), with near-total exclusion from hazardous categories: FLOW 0.003x, CONTAINMENT 0.00x, MARKING 0.004x. Among e-HEAD frames, only e→l (0%), e→bare (0%), and e→y (0.06%) are safe; e→d has 64.7% hazard, e→k has 35.6%, e→t has 16.4%, e→h has 14.3%.

## Evidence

### Category profile

| Category | e→y rate | Corpus rate | Enrichment |
|----------|----------|-------------|------------|
| OPERATION | 55.8% | 14.2% | 3.94x |
| TRANSITION | 25.6% | 14.8% | 1.73x |
| THERMAL | 18.6% | 23.4% | 0.79x |
| FLOW | 0.06% | 19.2% | 0.003x |
| CONTAINMENT | 0.0% | 4.8% | 0.00x |
| MARKING | 0.03% | 7.7% | 0.004x |

### e-HEAD frame comparison

| Frame | Hazard rate | N tokens |
|-------|------------|----------|
| e→d | 64.7% | -- |
| e→k | 35.6% | -- |
| e→t | 16.4% | -- |
| e→h | 14.3% | -- |
| e→y | 0.06% | 3,475 |
| e→l | 0.0% | -- |
| e→bare | 0.0% | -- |

## Interpretation

The y-terminal transforms e-HEAD from variable hazard (0-65% depending on terminal) into categorical safety. The combination of cooling (e) with ending (y) produces operations and transitions that are inherently non-hazardous. The 2 FLOW-classified tokens (0.06%) are edge cases at the category classifier boundary. This confirms C1448's identification of e→y as the largest safe frame and reveals that e-HEAD safety is terminal-dependent, not inherent.

## Falsification Criteria

1. If e→y hazard rate exceeds 2%
2. If FLOW fraction of e→y exceeds 5%
3. If OPERATION enrichment drops below 2.0x

## Method

- 3,475 e→y tokens classified by operational category (CategoryClassifier)
- Hazard defined as FLOW + CONTAINMENT (C1280)
- Comparison with all other e-HEAD frames

**Script:** `phases/EY_SAFE_PATHWAY/scripts/ey_safe_pathway.py`
**Results:** `phases/EY_SAFE_PATHWAY/results/ey_safe_pathway.json`

## Dependencies

- C1280 (Hazard concentrates in FLOW/CONTAINMENT)
- C1446 (k-HEAD complete hazard immunity — parallel safe frame)
- C1448 (HEAD x TERM frame hazard map)
- C1250 (Gloss category structural coherence)
