# C1436: m-Terminal Near-Pure TRANSITION Category

**Tier:** 2
**Scope:** B, MIDDLE, atom, m-terminal, category, TRANSITION, C1250, C1427, C1393
**Phase:** 521 (M_TERMINAL_ANOMALY)
**Date:** 2026-03-05

## Claim

m-terminal MIDDLEs are 87.9% TRANSITION (5.86x enrichment), the most category-concentrated terminal atom. Five categories are completely absent (THERMAL, MONITORING, FLOW, CONTAINMENT, MARKING). m accounts for 7.4% of all TRANSITION tokens despite being only 1.25% of corpus.

## Evidence

### Category distribution

| Category | m-terminal % | Overall % | Enrichment |
|----------|-------------|-----------|------------|
| TRANSITION | 87.9% | 15.0% | 5.86x |
| OPERATION | 9.0% | 14.2% | 0.63x |
| STAGING | 3.1% | 12.8% | 0.24x |
| THERMAL | 0.0% | 23.9% | 0.00x |
| MONITORING | 0.0% | 4.8% | 0.00x |
| FLOW | 0.0% | 19.0% | 0.00x |
| CONTAINMENT | 0.0% | 4.8% | 0.00x |
| MARKING | 0.0% | 7.8% | 0.00x |

### Per-MIDDLE category assignment

- `am` (174 tokens): TRANSITION
- `m` (76 tokens): TRANSITION
- `om` (25 tokens): OPERATION
- `im` (8 tokens): STAGING
- All singletons: TRANSITION (faim, kam, eam, fam) or OPERATION (opom) or STAGING (lm)

### Concentration comparison across terminals

m is the most category-concentrated terminal atom. No other terminal achieves >70% in any single category. m's 87.9% TRANSITION is unmatched.

## Interpretation

m is functionally monovalent — it does one thing (state change/closure) and nothing else. Its near-perfect TRANSITION purity, combined with its low diversity (C1434) and body-line exclusivity (C1435), makes it a dedicated body-line closure operator. The complete absence of 5/8 categories (including THERMAL and FLOW) means m never participates in the two primary operational modes of the grammar.

## Falsification Criteria

1. If TRANSITION fraction drops below 70%
2. If more than 2 of the currently absent categories appear at >2% each

## Method

- 289 m-terminal tokens classified by CategoryClassifier
- Category enrichment computed vs overall corpus rates

**Script:** `phases/M_TERMINAL_ANOMALY/scripts/m_terminal_analysis.py`
**Results:** `phases/M_TERMINAL_ANOMALY/results/m_terminal_analysis.json`

## Dependencies

- C1250 (gloss category structural coherence — 8-category system)
- C1393 (compound MIDDLE composition grammar)
- C1427 (line-final transition profile)
