# C1257: Consecutive Paragraph Vocabulary Coupling

**Tier:** 2
**Scope:** B
**Phase:** SEQUENTIAL_CONTENT_PREDICTION (Phase 450)
**Date:** 2026-02-24

## Statement

Consecutive paragraphs within a folio share more MIDDLE vocabulary than non-consecutive paragraphs (Jaccard 0.226 vs 0.199, diff = 0.027, p = 0.000). However, this coupling is vocabulary-only: kernel profiles do NOT autocorrelate (e: rho=0.358, p=0.012, not Bonferroni-significant; k, h: p>0.4), and suffix mode composition does NOT autocorrelate (rho=0.053, p=0.714). Adjacent paragraphs share what words they use but not how they use them.

## Key Findings

- Consecutive Jaccard: 0.2258, non-consecutive: 0.1990, diff = 0.0267, p = 0.000
- Kernel k autocorrelation: rho = 0.241, p = 0.41 (FAIL)
- Kernel e autocorrelation: rho = 0.358, p = 0.012 (borderline, not Bonferroni)
- Suffix mode autocorrelation: rho = 0.053, p = 0.714 (FAIL)
- 485 paragraphs across 55 folios with 3+ paragraphs

## Qualifies

- C845 (paragraph self-containment) → self-containment holds at operational level, but vocabulary selection is weakly coupled
- C855 (role template + vocabulary independence) → vocabulary is not fully independent; shared MIDDLE selection exists between consecutive paragraphs
- C670 (no adjacent-line coupling) → line-level independence confirmed, but paragraph-level vocabulary coupling exists

## Interpretation

Adjacent paragraphs operate on the same equipment (shared MIDDLEs) but run operationally independent programs (no kernel/mode coupling). The vocabulary coupling is contextual (same folio = same apparatus) rather than sequential (one paragraph continuing another).

## Method

Pairwise MIDDLE Jaccard between consecutive vs non-consecutive paragraph pairs within each folio. Permutation null: shuffle paragraph order within folio (1000 permutations). 55 folios with 3+ paragraphs.

## Provenance

- Phase 450 main battery: T7 (PASS), T8 (FAIL), T9 (FAIL)
