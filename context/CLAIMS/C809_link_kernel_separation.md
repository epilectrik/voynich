# C809: LINK-Kernel Separation

## Constraint

LINK is **spatially and morphologically separated** from kernel operators (k, h, e):

1. **Morphological depletion:** LINK tokens contain kernel primitives at lower rates
   - k: 0.86x baseline (18.8% vs 22.0%)
   - h: 0.93x baseline (25.4% vs 27.3%)
   - e: 0.82x baseline (25.4% vs 30.9%)

2. **Spatial separation:** LINK is farther from kernel tokens
   - LINK mean distance to kernel: 1.31 tokens
   - Non-LINK mean distance to kernel: 0.41 tokens
   - Mann-Whitney U: p < 0.0001

3. **Transition rates at baseline:** No enrichment of LINK around kernel
   - LINK rate after 'k': 12.9% (0.98x baseline)
   - LINK rate after 'h': 12.9% (0.98x baseline)
   - LINK rate after 'e': 12.3% (0.93x baseline)

## Evidence

Kernel enrichment in LINK vs non-LINK:
| Primitive | LINK% | Non-LINK% | Enrichment |
|-----------|-------|-----------|------------|
| k | 18.8% | 22.0% | 0.86x |
| h | 25.4% | 27.3% | 0.93x |
| e | 25.4% | 30.9% | 0.82x |

Distance analysis (tokens containing k/h/e but not 'ol'):
- LINK to kernel: 1.31 mean distance
- Non-LINK to kernel: 0.41 mean distance

## Interpretation

LINK occupies a distinct zone **away from both kernel operations and escape (FL)**:
- C807: LINK farther from FL
- C809: LINK farther from kernel

This supports C366's "monitoring/observation phase" characterization: LINK tokens mark waiting states that are neither actively processing (kernel) nor recovering (FL). The monitoring phase is morphologically and spatially distinct.

## Provenance

- Phase: LINK_OPERATOR_ARCHITECTURE
- Script: t6_link_kernel_contact.py
- Related: C366, C807

## Tier

2 (Validated Finding)
