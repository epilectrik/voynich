# C1437: m-Terminal Complete Hazard Exclusion

**Tier:** 2
**Scope:** B, MIDDLE, atom, m-terminal, hazard, FLOW, CONTAINMENT, C1280, C1427
**Phase:** 521 (M_TERMINAL_ANOMALY)
**Date:** 2026-03-05

## Claim

m-terminal has 0% tokens in hazard categories (FLOW, CONTAINMENT). 31.8% of m-terminal tokens are preceded by FLOW-category tokens, suggesting m closes sequences that include flow operations. m is never a hazard source, target, or buffer.

## Evidence

### Hazard category presence

| Measure | m-terminal | Overall |
|---------|-----------|---------|
| FLOW + CONTAINMENT | 0.0% | ~23.9% |
| FLOW alone | 0.0% | ~19.0% |
| CONTAINMENT alone | 0.0% | ~4.8% |

### Predecessor analysis

| Category | Rate among m-terminal predecessors |
|----------|------------------------------------|
| FLOW | 27.4% |
| TRANSITION | 19.4% |
| THERMAL | 14.2% |
| STAGING | 13.9% |
| OPERATION | 10.1% |

FLOW is the most common predecessor category (27.4%), well above its overall rate (~19%). m frequently closes sequences that include FLOW operations — it follows hazard-bearing tokens but never IS one.

### Successor analysis

Cross-line successors (after m-closed lines) show no preferential routing to any category. The next line is drawn from the folio's overall profile, consistent with C1429 cross-line independence.

## Interpretation

m occupies a structurally safe position: it closes body lines without ever entering the hazard topology. Its predecessors include FLOW tokens (27.4%), meaning m terminates sequences that may have involved hazardous operations. This is consistent with a "batch-close" function — m signals the end of an operational line, including lines that contained hazard-bearing flow operations.

## Falsification Criteria

1. If m-terminal tokens appear in FLOW or CONTAINMENT at >2%

## Method

- 289 m-terminal tokens checked against CategoryClassifier
- Predecessor/successor categories computed for all m-terminal tokens

**Script:** `phases/M_TERMINAL_ANOMALY/scripts/m_terminal_analysis.py`
**Results:** `phases/M_TERMINAL_ANOMALY/results/m_terminal_analysis.json`

## Dependencies

- C1280 (hazard concentrates in FLOW/CONTAINMENT)
- C1427 (line-final transition profile)
- C1429 (cross-line category independence)
