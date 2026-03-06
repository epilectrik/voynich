# C1460: e→y Early-Line Concentration with Final Avoidance

**Tier:** 2
**Scope:** B, MIDDLE, atom, e-HEAD, y-terminal, position, line, paragraph, C1425, C1427, C1428
**Phase:** 525 (EY_SAFE_PATHWAY)
**Date:** 2026-03-05

## Claim

e→y tokens show mild early-line bias (mean position 0.463 vs corpus 0.500) with strong line-final avoidance (0.55x). Q0-Q1 enriched (1.09-1.13x), Q4 depleted (0.76x). Within paragraphs, e→y rate increases from header (12.0%) to late body (17.5%), consistent with sustained operational work phase. e→y does thermal work in the line interior; line/paragraph closure is handled by other mechanisms (m-terminal, -am suffix).

## Evidence

### Line position profile

| Metric | e→y | Corpus | Enrichment |
|--------|-----|--------|------------|
| Mean position | 0.463 | 0.500 | -- |
| Line-initial rate | 9.5% | 10.5% | 0.91x |
| Line-final rate | 5.7% | 10.5% | 0.55x |
| Q0 (0-20%) | 23.6% | 21.7% | 1.09x |
| Q1 (20-40%) | 20.5% | 18.1% | 1.13x |
| Q4 (80-100%) | 18.4% | 24.1% | 0.76x |

### Paragraph depth gradient

| Position | e→y rate | Interpretation |
|----------|----------|----------------|
| Header lines | 12.0% | Lower at specification |
| Early body | 14.8% | Rising in work phase |
| Late body | 17.5% | Peak at sustained operation |

### Paragraph-level correlation

e→y rate vs AXM fraction: rho=+0.274, p<0.000001 (N=573 paragraphs).

## Interpretation

e→y concentrates in the thermal work zone (Q0-Q1) consistent with C1428 (THERMAL peak-then-decline gradient). Its line-final avoidance (0.55x) confirms functional separation from closure mechanisms: m-terminal handles line closure (C1434-C1435), -am suffix handles paragraph closure (C1237, C1439). The paragraph depth gradient (header 12% → late body 17.5%) shows e→y as an operational steady-state token — specification phases use other vocabulary, but once operations are running, e→y dominates the sustained work phase.

## Falsification Criteria

1. If e→y line-final enrichment exceeds 0.90x
2. If paragraph gradient inverts (header > late body)
3. If mean position exceeds 0.520

## Method

- 3,475 e→y tokens with line position (fractional 0-1)
- Quintile analysis of position distribution
- Paragraph structure via gallows-initial paragraph detection
- Body position classified as header/early body/late body

**Script:** `phases/EY_SAFE_PATHWAY/scripts/ey_safe_pathway.py`
**Results:** `phases/EY_SAFE_PATHWAY/results/ey_safe_pathway.json`

## Dependencies

- C1425 (Line length unimodal distribution)
- C1427 (Line-final transition profile)
- C1428 (THERMAL-peak-then-decline positional gradient)
- C1434-C1435 (m-terminal body-line closure)
- C1237 (Paragraph termination by -am)
