# C738: Union Coverage Ceiling

**Status:** VALIDATED | **Tier:** 2 | **Phase:** A_B_FOLIO_SPECIFICITY | **Scope:** A<>B

## Finding

Even combining all 114 A folios, B folio coverage never reaches 100%. The union of all A folio legal sets covers approximately 83-89% of each B folio's vocabulary. No B folio achieves 95% coverage even with all A folios available.

### Union Coverage Statistics

| Metric | Value |
|--------|-------|
| Median A folios needed for 95% | 115 (unreachable) |
| Mean A folios needed for 95% | 112.4 |
| Min A folios needed for 95% | 8 |
| Median A folios needed for 100% | 115 (unreachable) |

### Coverage Ceiling per B Folio

| Metric | Value |
|--------|-------|
| Mean best-A coverage per B folio | 0.6269 |
| Min best-A coverage (f41r) | 0.4744 |
| Mean worst-A coverage per B folio | 0.0942 |
| Mean gap (best - worst) | 0.5327 |
| Max gap | 0.6707 |

### Greedy Union Samples

| B Folio | A Folios to 90% | Final Coverage | A Folios Used |
|---------|-----------------|----------------|---------------|
| f39v | 8 | 88.6% | 8 |
| f95v1 | 7 | 85.3% | 7 |
| f82r | 13 | 86.5% | 13 |
| f66r | 17 | 83.5% | 17 |
| f103r | 21 | 83.6% | 21 |
| f113r | 25 | 85.4% | 25 |

## Implication

The ~15-35% of B vocabulary that remains inaccessible even under the union of all A folios represents B's autonomous grammar. These tokens do not participate in the A-B filtering pipeline — they are B-exclusive by construction. This is consistent with B having its own structural operators (kernel, control flow, hazard tokens) that operate independently of A input.

The large gap between best and worst A folio per B folio (mean 0.533) confirms the routing architecture: the "right" A folio matters enormously for B execution feasibility.

## Provenance

- Script: `phases/A_B_FOLIO_SPECIFICITY/scripts/ab_specificity.py` (T6, T7)
- Depends: C734 (coverage architecture), C736 (34.4% never-legal)
- Extends: C502.a (filtering cascade), C384 (aggregate sharing)
