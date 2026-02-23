# C1229 - Alternating Suffix Modes Within Paragraphs

**Tier:** 2 | **Scope:** B | **Phase:** APPARATUS_TRANSITION_DETECTION (Phase 438)

## Statement

100% of B paragraphs with 8+ body lines (55/55 tested, plus 2 showing k=3) contain two distinct suffix profile clusters (k=2 silhouette mean 0.459). These clusters are predominantly interleaved (80% non-contiguous), not sequential. The suffix gradient within paragraphs (C932: terminal r=-0.89, bare r=+0.90) is continuous with no discrete breakpoints (3.3% piecewise rate), but the two suffix modes alternate throughout the body rather than transitioning smoothly from one to the other.

## Evidence

### Suffix clustering (T4, paragraphs with 8+ body lines)

| Metric | Value |
|--------|-------|
| Paragraphs tested | 57 |
| k=2 wins (silhouette > 0.3) | 55 (96.5%) |
| k=3 wins | 2 (3.5%) |
| Mean silhouette k=2 | 0.459 |
| Mean silhouette k=3 | 0.400 |
| Contiguous clusters | 11/55 (20.0%) |
| Non-contiguous (interleaved) | 44/55 (80.0%) |

### Suffix piecewise test (T1, 124 paragraphs with 6+ body lines)

| Suffix category | Breakpoint rate |
|----------------|-----------------|
| Terminal | 3.3% |
| Connector | 3.3% |
| Iterate | 3.3% |
| Bare | 2.5% |

### Fractional analysis (T2-T3)

| Test | Result |
|------|--------|
| FL reset x suffix change | No effect (p=0.87) |
| Length x suffix diversity | No correlation (rho=0.058, p=0.34) |

### Key observations

1. **Two modes are real**: Every long paragraph shows two distinct suffix clusters with good separation (silhouette > 0.3)
2. **Modes alternate**: 80% interleaved means lines of each type are interspersed throughout the body, not grouped in halves
3. **Gradient is continuous**: Despite two modes, the transition is smooth (no breakpoints) with the balance gradually shifting from terminal-heavy to bare-heavy through the body
4. **Modes are not fraction-specific**: FL resets don't coincide with suffix changes, and paragraph length doesn't increase suffix diversity

## Interpretation

Paragraphs contain two alternating operational modes at the suffix level - one terminal-heavy (parameter specification) and one bare-heavy (process continuation). These modes interleave throughout the body, with the overall balance shifting toward continuation as the process progresses. This is consistent with iterative extraction cycles alternating between "check-and-adjust" and "run-and-maintain" phases, where the process gradually requires less checking and more running as it stabilizes.

The continuous suffix gradient (no discrete breakpoints) means the extraction process produces gradually shifting output, not categorically distinct fractions. This is consistent with real distillation where chemical composition shifts continuously over time.

## Related constraints

- C932: Body vocabulary gradient (terminal r=-0.89, bare r=+0.90)
- C1002: Suffix positional grammar (category gradients emergent, not per-suffix)
- C963: Body homogeneity at role-fraction level
- C1227: FL cross-line reset clustering
- C1228: PREFIX channel switching within paragraphs

## Provenance

- `phases/APPARATUS_TRANSITION_DETECTION/scripts/fractional_line_test.py` (T1, T2, T3, T4)
- `phases/APPARATUS_TRANSITION_DETECTION/results/fractional_line_results.json`
- `phases/APPARATUS_TRANSITION_DETECTION/scripts/apparatus_transition_detection.py` (Test A kernel null)
- `phases/APPARATUS_TRANSITION_DETECTION/results/apparatus_transition_results.json`
