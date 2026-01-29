# C736: B Vocabulary Accessibility Partition

**Status:** VALIDATED | **Tier:** 2 | **Phase:** A_B_FOLIO_SPECIFICITY | **Scope:** A<>B

## Finding

B token types partition into distinct accessibility tiers under C502.a filtering. No B token is universally legal across all A folios, and 34.4% are permanently B-exclusive (never legal under any A folio).

### Accessibility Census

| Category | Count | % of B Types |
|----------|-------|--------------|
| Legal under ALL 114 A folios | 0 | 0.0% |
| Legal under 101-114 A folios | 42 | 0.9% |
| Legal under 51-100 A folios | 431 | 8.8% |
| Legal under 11-50 A folios | 1,074 | 22.0% |
| Legal under 1-10 A folios | 1,658 | 33.9% |
| Legal under NO A folio | 1,684 | 34.4% |
| **Total B token types** | **4,889** | **100%** |

### Distribution Statistics

| Metric | Value |
|--------|-------|
| Mean A folios per B token | 13.9 |
| Median | 3 |
| Q25 | 0 |
| Q75 | 17 |

### Union Coverage

| Metric | Value |
|--------|-------|
| B tokens legal under >= 1 A folio | 3,205 (65.6%) |
| B tokens never legal | 1,684 (34.4%) |

## Implication

B vocabulary has a tripartite structure:

1. **B-exclusive core** (34.4%): Never legal under any A folio. These tokens represent B's autonomous grammar — structural operators, control flow, kernel vocabulary. This is B's own machinery, independent of A input.

2. **Narrow-access vocabulary** (33.9%): Legal under 1-10 A folios. These tokens are domain-specific — they become available only when a matching A folio provides the right MIDDLE/PREFIX/SUFFIX components. This is the routing-sensitive layer.

3. **Broad-access vocabulary** (31.7%): Legal under 11+ A folios. These tokens are broadly shared and available regardless of which A folio is active. This is the common operational vocabulary.

The zero count at universal access and the median of 3 confirm that no B vocabulary escapes A-folio specificity entirely. Even the broadest-access tokens are excluded by at least some A folios.

## Provenance

- Script: `phases/A_B_FOLIO_SPECIFICITY/scripts/ab_specificity.py` (T9)
- Depends: C502.a (three-axis filtering)
- Extends: C384 (aggregate 99.8% sharing masks the per-folio partition)
