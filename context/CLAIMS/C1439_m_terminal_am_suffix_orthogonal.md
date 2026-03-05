# C1439: m-Terminal MIDDLE and -am Suffix Are Orthogonal Systems

**Tier:** 2
**Scope:** B, MIDDLE, atom, m-terminal, suffix, -am, paragraph, line, closure, C1237, C1427, C1434, C1435, C1436
**Phase:** 521 (M_TERMINAL_ANOMALY)
**Date:** 2026-03-05

## Claim

m-terminal MIDDLE (289 tokens, 87.9% TRANSITION, body-line-final) and -am suffix (234 tokens, multi-category, paragraph-final) overlap at exactly 1 token (`amam`). They share an `m` character but operate at different grammar levels: m-terminal closes body lines, -am suffix closes paragraphs. Two-level closure architecture confirmed.

## Evidence

### System comparison

| Feature | -am Suffix (C1237) | m-Terminal MIDDLE |
|---------|-------------------|-------------------|
| N tokens | 234 | 289 |
| Overlap | 1 token | 1 token |
| Category profile | Multi-category (FLOW 34.6%, THERMAL 26.5%, MARKING 19.2%) | Near-pure TRANSITION (87.9%) |
| Line-final rate | 82.1% | 77.9% |
| Paragraph-final | 5.19x enriched | 0.31x DEPLETED |
| Scope | Paragraph termination | Body-line closure |

### Overlap analysis

The single overlapping token is `amam` — a token whose MIDDLE is `am` (m-terminal) and whose suffix is `-am`. This is 1/289 = 0.35% of m-terminal and 1/234 = 0.43% of -am suffix tokens. The two systems are effectively non-overlapping.

### Category divergence

The two systems have completely different category profiles:
- -am suffix: broadly distributed across FLOW (34.6%), THERMAL (26.5%), MARKING (19.2%), TRANSITION (7.3%)
- m-terminal MIDDLE: concentrated in TRANSITION (87.9%)

The -am suffix can attach to tokens from any category because it marks paragraph-level structure. The m-terminal MIDDLE IS a category-specific closure operator.

### Positional divergence

- -am suffix: enriched at paragraph-final (5.19x per C1237)
- m-terminal MIDDLE: depleted at paragraph-final (0.31x, C1435), enriched at body-line-final (10.45%)

These positional profiles are complementary, not overlapping.

## Interpretation

Currier B uses a two-level closure architecture:

1. **Body-line closure:** m-terminal MIDDLE (289 tokens). Closes individual operational lines within paragraph bodies. Near-pure TRANSITION, suffix-suppressed, hazard-excluded.

2. **Paragraph termination:** -am suffix (234 tokens). Closes entire paragraphs. Multi-category, broadly distributed, paragraph-final concentrated.

The shared `m` character is a surface coincidence — the two `m`s operate at different levels of the morphological grammar (MIDDLE terminal atom vs suffix component). This parallels the general principle of C1409 (atoms carry different information in different positions).

## Falsification Criteria

1. If overlap between m-terminal MIDDLE and -am suffix exceeds 10 tokens
2. If both systems show the same positional profile (both paragraph-final or both body-line-final)

## Method

- m-terminal: 289 tokens with MIDDLE terminal atom = m
- -am suffix: 234 tokens with suffix containing -am (from C1237)
- Overlap computed by token identity intersection

**Script:** `phases/M_TERMINAL_ANOMALY/scripts/m_terminal_analysis.py`
**Results:** `phases/M_TERMINAL_ANOMALY/results/m_terminal_analysis.json`

## Dependencies

- C1237 (paragraph termination by -am)
- C1427 (line-final transition profile)
- C1434 (m-terminal low-diversity closure)
- C1435 (m-terminal body-line exclusivity)
- C1436 (m-terminal near-pure TRANSITION)
- C1409 (suffix atoms diverge from MIDDLE-terminal atoms)
