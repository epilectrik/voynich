# Phase: EXTENSION_DISTRIBUTION_PATTERNS

## Purpose

Test whether the extension operational context model (h=monitoring, k=energy, t=terminal, d=transition) predicts how extensions distribute across the manuscript.

## Background

From C917-C922, we established:
- RI = PP + extension (90.9% containment)
- Extensions encode operational context
- f57v R2 shows 92% extension vocabulary with h-exclusion
- Single-char AZC content systematically under-represents h (p=0.023)

## Tests

### 01. Extension Section Profile
**Question:** Do sections specialize by operation type as reflected in extension profiles?

**Prediction:** If extensions encode operational context and sections represent operation types, extension profiles should differ across sections.

### 02. Zodiac Folio Patterns
**Question:** Do other zodiac folios (f70v-f73v) show similar patterns to f57v?

**Prediction:** If f57v R2 is a zodiac-wide timing reference pattern, other zodiac folios should show:
- Extension vocabulary overlap
- h-exclusion from certain positions
- Periodicity in single-char content

### 03. Label Extension Profile
**Question:** Do labels (3.7x RI-enriched per C914) show different extension profiles than text?

**Prediction:** If labels identify specific instances and extensions encode operational context, labels may show different extension distributions.

## Results

See `results/` directory for JSON outputs.

## Deliverables

- Extension × Section matrix with enrichment statistics
- Zodiac folio comparison (match f57v pattern?)
- Label vs text extension comparison

## Success Criteria

- If extensions cluster by section meaningfully → supports operational context model
- If zodiac folios share h-exclusion patterns → strengthens calendar interpretation
- If labels have distinct profile → supports instance identification function
