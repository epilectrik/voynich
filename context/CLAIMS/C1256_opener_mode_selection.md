# C1256: Opener Mode Selection

**Tier:** 2
**Scope:** B
**Phase:** SEQUENTIAL_CONTENT_PREDICTION (Phase 450)
**Date:** 2026-02-24

## Statement

The opener MIDDLE (first token of a body line) selects the line's suffix mode (A or B). Cramer's V = 0.30 (null 0.17, 1.76x, p=0.000). The opener does NOT predict kernel profile (p=0.096), FL stage distribution (p=0.85), or body MIDDLE vocabulary beyond marginal (1.03x, p=0.005). Furthermore, paragraph opening mode predicts internal composition: Mode-B-opening paragraphs have 28.9% Mode A lines vs 54.0% for Mode-A-opening paragraphs (p=0.000). The opener is a mode selector, not a content router.

## Key Findings

- Opener MIDDLE → suffix mode: Cramer's V = 0.2994, null = 0.1701, ratio = 1.76x, p = 0.000
- Opener MIDDLE → kernel profile: FAIL (variance ratio 1.24x, p = 0.096)
- Opener MIDDLE → FL distribution: FAIL (variance ratio 0.85x, p = 0.85)
- Opener MIDDLE → body vocabulary: marginal (Jaccard 0.123 vs 0.120, 1.03x, p = 0.005)
- 58.5% of paragraphs open Mode B, 41.1% open Mode A
- Opening mode is a paragraph type declaration, not a continuation signal
- No vocabulary inheritance from predecessor paragraph (Jaccard diff = -0.002, p = 0.601)
- Mode-B-opening paragraphs do not cluster later in folio (p = 0.662)

## Refines

- C959 (opener is role marker) → more specifically, opener is a MODE SELECTOR
- C1229 (alternating suffix modes) → the alternation is opened/declared by the first body line

## Method

1,881 opener-body pairs from Currier B body lines. Permutation null: shuffle opener assignments within folio (1000 permutations). Bonferroni correction across 9 tests (p < 0.0056). Follow-up continuation hypothesis test (5 questions, 1/5 PASS).

## Provenance

- Phase 450 main battery: T1 (marginal PASS), T2 (PASS), T3 (FAIL), T4 (FAIL)
- Phase 450 continuation follow-up: Q1-Q5 (1/5 PASS — Q5 only)
