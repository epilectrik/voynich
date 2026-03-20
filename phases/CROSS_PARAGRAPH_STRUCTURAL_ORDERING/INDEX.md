# Phase 613: CROSS_PARAGRAPH_STRUCTURAL_ORDERING

**Status:** COMPLETE
**Date:** 2026-03-20
**Verdict:** STRUCTURAL_ORDERING_CONFIRMED

## Research Question

Do paragraphs within a folio exhibit sequential structural ordering, given that
C1399 established no compositional ordering and C1400 established no state-dependent
ordering?

## Background

C1399 and C1400 proved that paragraph COMPOSITIONAL ordering (category profiles, thermal
state) is null within folios. C855 established that paragraphs are parallel programs
with role cohesion 0.831. But these tests addressed execution-level properties. Document
DESIGN properties (how the specification is organized for the human reader) were untested.

Phase 612 established that gallows are explicit paragraph-header labels of deployment
context (C1778-C1781). Exploratory analysis of gallows sequential properties revealed
that gallows transitions are non-random, gallows types have distinct positional signatures,
and line length shortens across paragraphs within folios. This phase formalizes those
findings with blocking tests.

## Method

Four test blocks on 501 paragraphs across 82 folios:

1. **T1: First-body-line length gradient** - Does the first body line (not header) of later
   paragraphs shorten? This separates cross-paragraph abbreviation from within-paragraph
   decline (C963) leaking upward.

2. **T2: Shuffle validation** - Shuffle paragraph order within folios 1000x. Does observed
   line-length gradient exceed shuffled null? This directly tests whether ordering matters.

3. **T3: Gallows transition matrix** - Are gallows type transitions non-random? What are the
   type-specific positional and sequential signatures?

4. **T4: Thermal state carryover** - Do thermal/energy state variables carry across paragraph
   boundaries after removing folio-level means?

## Key Findings

### T1: PASS - First-body-line length declines across paragraph ordinals

| Metric | rho | p | n |
|--------|-----|---|---|
| First body line (global) | -0.194 | 0.000012 | 501 |
| First body line (folio-residualized) | -0.225 | 0.000188 | 67 folios |
| Mean body line (folio-residualized) | -0.308 | 0.000001 | 67 folios |
| Header line (folio-residualized) | -0.037 | 0.599 | 67 folios |
| n_lines (global) | -0.013 | 0.765 | 501 |
| TTR (global) | +0.003 | 0.943 | 501 |

Body lines abbreviate; headers do NOT. Paragraph length (n_lines) does NOT decline.
Vocabulary diversity (TTR) is flat. The effect is progressive specification compression,
not simplification.

Consistent across all sections: Stars rho=-0.150, Bio rho=-0.232, Herbal rho=-0.267
(first body line).

Quintile view (first body line tokens): Q0=10.99, Q1=9.90, Q2=10.21, Q3=10.21, Q4=9.40.

### T2: PASS - Paragraph ordering carries structural information

| Test | Observed rho | Null mean | z | p |
|------|-------------|-----------|---|---|
| Mean body line length | -0.308 | -0.002 | -4.78 | <0.000001 |
| First body line length | -0.226 | +0.001 | -3.67 | <0.000001 |

76.1% of folios individually show negative line-length gradient.
Refines C1399: compositional ordering null, structural ordering real.

### T3: Gallows transitions non-random with type-specific signatures

Transition chi2=53.69, p<0.0001, V=0.209.

| Type | Self-rate | Mean position | Signature |
|------|-----------|---------------|-----------|
| k | 0.0% | 0.334 | One-shot intervention, positioned early, never self-follows |
| t | 46.9% | 0.535 | Self-clusters positionally, independent operational blocks |
| p | 56.2% | 0.507 | Sequential backbone, self-chains across folio body |
| f | 31.2% | 0.321 | Early-positioned like k, self-clusters (n=18, sparse) |

k positioned early (mean 0.334, median 0.193). k/f are openers (mean pos ~0.33); p/t are
body types (mean pos ~0.52). This aligns with C1780 opener/mode positional axis.

### T4: No thermal state carryover after folio residualization

| Chain | Feature | Raw r | Resid r | Resid p |
|-------|---------|-------|---------|---------|
| p-chain | thermal | +0.285 | +0.013 | 0.886 |
| p-chain | e_frac | +0.485 | +0.075 | 0.407 |
| all | thermal | +0.213 | -0.093 | 0.060 |
| all | e_frac | +0.330 | -0.035 | 0.482 |

Raw correlations are positive (shared folio context). After folio-mean removal, ALL
positive signals vanish. Residualized correlations are null or slightly negative
(anti-correlation/alternation). Each paragraph completes its thermal cycle independently.

## Architectural Reconciliation

C855 (parallel programs) and C1399 (no compositional ordering) remain fully valid.
C1782-C1783 reveal a DOCUMENT DESIGN property orthogonal to execution: later paragraphs
abbreviate for the READER, not the APPARATUS. The folio is sequential in reading but
parallel in execution. TTR is flat -- same vocabulary, just more concise delivery.

C1784 establishes that gallows types have distinct sequential roles: p as the recurring
backbone (main procedural thread), k as intervention (called once early), t as
self-contained operational blocks. C1785 confirms that despite this sequential structure,
no thermal state carries across paragraph boundaries -- consistent with C1399/C1400
at the compositional level.

The two-level execution architecture (C1569) gains a third ordering principle:
- Sections: no ordering
- Folios within section: no ordering
- Paragraphs within folio: SPECIFICATION ordering (line length abbreviation)
- Lines within paragraph: STRUCTURAL ordering (C1727, length-dominated)
- Tokens within line: SAFETY ordering (C1463, hazard gradient)

## Scripts

| Script | Runtime | Purpose |
|--------|---------|---------|
| `scripts/cross_paragraph_ordering.py` | ~15s | Consolidated T1-T4 analysis |

## Dependencies

- C855 (folio role template / parallel programs)
- C963 (paragraph body homogeneity, within-paragraph line shortening)
- C1399 (no preferred paragraph ordering -- compositional)
- C1400 (paragraph state-independent ordering)
- C1772-C1781 (Phase 611-612 gallows characterization)

## Constraints Produced

| ID | Claim | Tier | Scope |
|----|-------|------|-------|
| C1782 | First-body-line length declines across paragraph ordinals | 2 | B, paragraph, line, length, ordinal |
| C1783 | Paragraph structural ordering real via line length gradient | 2 | B, paragraph, ordering, line, shuffle |
| C1784 | Gallows transition matrix non-random with type-specific signatures | 2 | B, paragraph, gallows, transition, sequential |
| C1785 | No thermal state carryover after folio residualization | 2 | B, paragraph, thermal, carryover, independence |
