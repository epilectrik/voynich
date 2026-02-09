# C922: Single-Character AZC Ring h-Exclusion

## Status
- **Tier**: 2 (STRUCTURAL)
- **Scope**: AZC
- **Status**: CLOSED
- **Source**: Phase A_PURPOSE_INVESTIGATION

## Statement

Single-character AZC ring content has significantly lower 'h' character frequency (1.9%) compared to multi-character ring content (7.4%). Fisher's exact test: p = 0.023.

## Evidence

### h-Rate by Content Type

| Ring Content Type | h Count | Total Chars | h Rate |
|-------------------|---------|-------------|--------|
| Single-char (>75%) | 2 | 106 | 1.9% |
| Multi-char (<25%) | 368 | 4,960 | 7.4% |

### Statistical Significance

- Fisher's exact test: p = 0.023
- Effect: 3.9x reduction in h-rate for single-char content
- Conclusion: Single-char rings systematically under-represent 'h'

### Specific Examples

**Rings with 0% h (n >= 20 chars):**
- f57v R2: 50 chars, 100% single-char, 0% h
- f72v1 R3: 50 chars, 0% single-char, 0% h

**f57v Ring Comparison:**

| Ring | h Count | Total | h Rate | Single-char % |
|------|---------|-------|--------|---------------|
| R1 | 8 | 162 | 4.9% | 27% |
| R2 | 0 | 50 | 0.0% | 100% |
| R3 | 6 | 103 | 5.8% | 32% |
| R4 | 2 | 56 | 3.6% | 76% |

Note: f57v R2 alone has p = 0.14 (not independently significant), but is consistent with the corpus-wide pattern.

### Corpus-Wide Ring h-Rates

| Ring Position | h Count | Total | h Rate |
|---------------|---------|-------|--------|
| R1 | 172 | 2,420 | 7.1% |
| R2 | 135 | 1,811 | 7.5% |
| R3 | 74 | 993 | 7.5% |
| R4 | 3 | 107 | 2.8% |

## Interpretation

When AZC diagrams present content as single characters (reference/alphabet format), they systematically exclude or under-represent 'h'. Per C917, h-extension encodes monitoring/linker context. This suggests single-character references list materials/operations that don't require active monitoring.

## Related Constraints

| Constraint | Relationship |
|------------|--------------|
| C917 | h-extension = monitoring/linker context (82% ct-prefix) |
| C920 | f57v R2 = 92% extension vocabulary |
| C921 | f57v R2 twelve-character period |
| C763 | f57v R2 is 100% single-character tokens |

## Falsification Criteria

Disproven if:
1. Expanded analysis shows no significant h-rate difference
2. The pattern is explained by folio/section confounding
3. Single-char content identified with high h-rate
