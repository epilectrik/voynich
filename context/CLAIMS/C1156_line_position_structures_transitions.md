# C1156: Line Position Structures Class Transitions

**Tier:** 2
**Scope:** B, line, transition dynamics
**Phase:** LINE_TRANSITION_DYNAMICS (Phase 413)
**Depends on:** C964, C961, C972

## Statement

The 49-class transition matrix differs significantly across line positions. Three transition zones — ENTRY (opener→second), INTERIOR (non-boundary), EXIT (penultimate→closer) — produce pairwise JSD of 0.224 (entry-interior), 0.217 (interior-exit), and 0.333 (entry-exit), all significant at p<0.001 against 1000 within-line permutations. At the 6-state macro level, AXM self-transition drops from 0.730 (entry) to 0.704 (interior) to 0.633 (exit), a 9.7% absolute gradient. Spectral gap also shifts (0.939→0.883→0.900).

## Evidence

| Zone pair | JSD | Null mean | Null p |
|-----------|-----|-----------|--------|
| Entry vs Interior | 0.2243 | (permuted) | <0.001 |
| Interior vs Exit | 0.2175 | (permuted) | <0.001 |
| Entry vs Exit | 0.3332 | (permuted) | <0.001 |

**6-state AXM self-transition by zone:**
| Zone | AXM self | Spectral gap | Stationary π(AXM) |
|------|----------|-------------|-------------------|
| ENTRY | 0.730 | 0.939 | 0.721 |
| INTERIOR | 0.704 | 0.883 | 0.672 |
| EXIT | 0.633 | 0.900 | 0.597 |

**Data:** 2,362 lines, 13,645 transitions (ENTRY: 2,362; INTERIOR: 9,006; EXIT: 2,277). 16,054 classified tokens (69% of B tokens; remaining 31% are hapax/rare types not in 479-type class map).

## Structural Implication

C964 established boundary-constrained free-interior grammar at the role/token level. C1156 extends this to transition dynamics: the sequential coupling between consecutive tokens is position-dependent. Lines begin with high AXM persistence (0.730), which relaxes through the interior and drops sharply at exit (0.633). This gradient was invisible at C964's resolution because C964 tested role distributions and token exclusivity, not pairwise transition structure.

The position effect is section-dependent (Kruskal-Wallis p<0.0001): BIO and STARS_RECIPE show moderate position sensitivity (0.67-0.70), while smaller sections show higher sensitivity (1.2-1.7), likely a sample-size artifact.
