# C1435: m-Terminal Body-Line Exclusivity

**Tier:** 2
**Scope:** B, MIDDLE, atom, m-terminal, line, paragraph, body, header, position, C1427, C1237, C1425
**Phase:** 521 (M_TERMINAL_ANOMALY)
**Date:** 2026-03-05

## Claim

m-terminal is a body-line-final signal: 10.45% rate at body-line-final (not paragraph-final), 0.00% at header-line-final, 3.26% at paragraph-final (Fisher exact p < 0.000001 vs body). m is categorically excluded from paragraph headers and depleted at paragraph boundaries. Scope is LINE BODY, not paragraph or folio.

## Evidence

### Positional rates

| Context | m-rate | N |
|---------|--------|---|
| Non-final position | 0.31% | 20,542 |
| Body-line-final (not par-final) | 10.45% | 1,971 |
| Non-header line-final | 9.12% | 2,052 |
| Header line-final | 0.00% | 502 |
| Paragraph-final | 3.26% | 583 |
| Folio-final | 3.61% | 83 |

### Critical contrasts

1. **ANTI-HEADER:** Zero m-terminal tokens at header line-final (0/502). m is categorically excluded from paragraph opening lines.
2. **ANTI-PARAGRAPH-FINAL:** m-rate at paragraph-final (3.26%) is significantly LOWER than at body-line-final (10.45%). Fisher exact p < 0.000001. This is the opposite of the -am suffix (C1237), which IS paragraph-final enriched at 5.19x.
3. **BODY-LINE specificity:** m marks the end of interior body lines within paragraphs, not headers, not paragraph ends.

### Paragraph position breakdown

| Position | m-closed lines | Non-m lines | m-fraction |
|----------|---------------|-------------|-----------|
| Header | 36 | 466 | 7.2% |
| Body | 158 | 1,251 | 11.2% |
| Last (par-final) | 17 | 459 | 3.6% |
| Single-line | 2 | 31 | 6.1% |

## Interpretation

m-terminal operates at a specific structural level: it closes individual body lines within paragraphs. It does not open paragraphs (0% header) and it avoids paragraph termination (depleted at par-final). The -am suffix (C1237) handles paragraph termination; the m-terminal MIDDLE handles body-line closure. These are complementary, non-overlapping systems (see C1439).

## Falsification Criteria

1. If m-terminal rate at header-line-final exceeds 3%
2. If paragraph-final rate exceeds body-line-final rate

## Method

- 23,096 Currier B tokens (H-track, labels excluded)
- Paragraph annotations from gallows-initial boundaries
- Header = first line of paragraph, Body = interior lines, Last = final line

**Script:** `phases/M_TERMINAL_ANOMALY/scripts/m_terminal_analysis.py`
**Results:** `phases/M_TERMINAL_ANOMALY/results/m_terminal_analysis.json`

## Dependencies

- C1427 (line-final transition profile)
- C1237 (paragraph termination by -am)
- C1425 (line length unimodal distribution)
- C840 (B paragraph mini-program structure)
