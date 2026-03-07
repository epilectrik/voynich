# C1559: o-HEAD Cross-System Gradient A>AZC>B with AZC Boundary Concentration

**Tier:** 2
**Scope:** CROSS, A, B, AZC, MIDDLE, atom, HEAD, o-HEAD, cross-system, gradient, AZC-zone, boundary, S-zone, R-zone, C1381, C1388, C1502, C1507, C1517, C1522, C1559
**Phase:** O_DOMAIN_DEEP_DIVE (Phase 548)
**Date:** 2026-03-06

## Claim

o-HEAD frequency follows a monotonic cross-system gradient: Currier A (28.5%, 3,181 tokens) > AZC (22.4%, 723 tokens) > Currier B (11.8%, 2,717 tokens). A/B ratio = 2.42x, AZC/B ratio = 1.90x. Within AZC zones: L (label) = 30.9%, S (boundary) = 29.3%, C (core) = 26.2%, P (text-proximate) = 19.1%, R (interior) = 17.7%. S/R ratio = 1.66x, confirming and extending C1517 (o-HEAD zone-graded). The gradient runs from A-proximate zones (S, C, L: high o-HEAD, arrangement-heavy) to B-proximate zones (R, P: lower o-HEAD, execution-heavy), precisely matching C1522 (AZC grades from A-like to B-like). A-enriched o-MIDDLEs include c-containing forms (oc 0.04x, otc 0.07x, okc 0.08x) -- forms associated with A's declarative register. B-enriched o-MIDDLEs are simpler operational forms (olk 3.27x, opch 2.07x).

## Evidence

### Cross-system o-HEAD rates

| System | o-HEAD Rate | Tokens | Types |
|---|---|---|---|
| Currier A | 28.5% | 3,181 | 264 |
| AZC | 22.4% | 723 | 196 |
| Currier B | 11.8% | 2,717 | 276 |

### AZC zone detail

| Zone | o-HEAD Rate | Interpretation |
|---|---|---|
| L (label) | 30.9% | Identification vocabulary |
| S (boundary) | 29.3% | Configuration at boundaries |
| C (core) | 26.2% | Core positions |
| P (text-proximate) | 19.1% | Near executable text |
| R (interior) | 17.7% | Interior operational positions |

### Cross-system MIDDLE enrichment (selected)

| MIDDLE | A/B Ratio | Interpretation |
|---|---|---|
| oc | 0.04x (B>>A) | B operational |
| otc | 0.07x | B operational |
| olk | 3.27x (A>>B) | A declarative |
| opch | 2.07x | Mixed |

## Interpretation

The cross-system gradient confirms C1507 (bridge HEAD redistributes: A selects o/headless, B selects e/k) at full token-level resolution. A's declarative register describes arrangements (high o-HEAD); B's execution grammar performs operations (low o-HEAD). AZC zones grade continuously between these poles, with boundary zones (S) being arrangement-heavy and interior zones (R) being execution-heavy. The AZC gradient mirrors the global A->AZC->B system gradient at zone resolution.

## Falsification Criteria

1. If o-HEAD rate in B exceeds A rate
2. If AZC zones show no systematic o-HEAD gradient
3. If the S/R enrichment ratio is shown to be a sampling artifact

## Source

`phases/O_DOMAIN_DEEP_DIVE/results/o_domain_deep_dive.json`
