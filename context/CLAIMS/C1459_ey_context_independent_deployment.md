# C1459: e→y Context-Independent Deployment (Not Recovery-Specific)

**Tier:** 2
**Scope:** B, MIDDLE, atom, e-HEAD, y-terminal, context, recovery, deployment, ambient, C105, C458, C1448
**Phase:** 525 (EY_SAFE_PATHWAY)
**Date:** 2026-03-05

## Claim

e→y appears at the same rate (~15%) regardless of whether the preceding token is hazardous or safe. Post-hazard e→y rate = 14.75%, post-safe = 15.35% (Mann-Whitney p=0.310, NS). Pre-e→y hazard rate = 23.0% and post-e→y hazard rate = 22.9%, both matching the corpus baseline of 23.9%. e→y is an ambient safety substrate deployed at a constant rate, not a reactive recovery mechanism.

## Evidence

### Context-independence

| Context | e→y rate | Enrichment | p-value |
|---------|----------|------------|---------|
| Overall | 15.05% | 1.00x | -- |
| Post-hazard token | 14.75% | 0.98x | -- |
| Post-safe token | 15.35% | 1.02x | -- |
| Post-forbidden-source | 16.45% | 1.09x | -- |
| Mann-Whitney (hazard vs safe) | -- | -- | p=0.310 (NS) |

### Surrounding hazard rates

| Metric | Rate |
|--------|------|
| Pre-e→y hazard rate | 23.0% |
| Post-e→y hazard rate | 22.9% |
| Corpus baseline | 23.9% |

## Interpretation

C105 established that 54.7% of recovery paths converge on e. This finding reveals the mechanism: e→y achieves stability anchoring not by being deployed in response to danger, but by pervading the grammar as omnipresent safe infrastructure. Recovery convergence on e is a property of the grammar's topology (e→y tokens are everywhere), not a reactive deployment strategy. This reframes C105 from "e is used for recovery" to "e→y is always present, so recovery naturally routes through it."

## Falsification Criteria

1. If post-hazard e→y rate diverges from overall by >5pp (currently 0.3pp)
2. If Mann-Whitney p < 0.01
3. If post-e→y hazard rate diverges from pre-e→y by >5pp

## Method

- Each B token classified as e→y or non-e→y
- Preceding token context classified as hazardous or safe (FLOW/CONTAINMENT = hazard)
- Mann-Whitney U test comparing e→y rates in post-hazard vs post-safe contexts
- Pre/post hazard rates computed by examining neighbors of e→y tokens

**Script:** `phases/EY_SAFE_PATHWAY/scripts/ey_safe_pathway.py`
**Results:** `phases/EY_SAFE_PATHWAY/results/ey_safe_pathway.json`

## Dependencies

- C105 (e = STABILITY_ANCHOR, 54.7% recovery paths)
- C458 (Execution design clamp vs recovery freedom)
- C1280 (Hazard concentrates in FLOW/CONTAINMENT)
- C1448 (e→y identified as largest safe frame)
