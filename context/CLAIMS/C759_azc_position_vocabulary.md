# C759: AZC Position-Vocabulary Correlation

**Status:** VALIDATED | **Tier:** 2 | **Phase:** AZC_FOLIO_DIFFERENTIATION | **Scope:** AZC

## Finding

Position within AZC diagrams (R, S, C placements) significantly determines vocabulary selection.

### Evidence

Chi-squared test: chi2=112.59, df=12, **p<0.001**
Cramer's V: 0.208 (medium effect)

### PREFIX Profile by Position

| PREFIX | R-series (n=1326) | S-series (n=501) | C-series (n=629) |
|--------|-------------------|------------------|------------------|
| ch | 20.5% | 10.9% | **28.3%** |
| sh | 9.2% | 4.1% | 6.4% |
| ok | 14.0% | **29.2%** | 11.9% |
| ot | 24.3% | **27.2%** | 16.8% |

Key patterns:
- **S-positions (spoke/nymph):** 56% ok+ot - interior/boundary markers
- **C-positions (center):** 28% ch - convergence markers
- **R-positions (ring):** Mixed profile, ch+ot dominant

### Position Similarity

| Comparison | Cosine Similarity |
|------------|-------------------|
| R-S | 0.890 |
| R-C | 0.949 |
| S-C | 0.771 |

S-positions are most distinct from C-positions.

### R-Subscript Uniformity

| Comparison | Cosine Similarity |
|------------|-------------------|
| R1-R2 | 0.985 |
| R1-R3 | 0.989 |
| R2-R3 | 0.990 |

R1/R2/R3 are functionally identical - subscripts encode position, not vocabulary.

## Implication

1. **Position encodes semantic function within diagrams.** S-positions favor ok+ot (monitoring), C-positions favor ch (control).

2. **Supports "context-locking scaffold" interpretation.** Different diagram zones have different vocabulary constraints.

3. **R-subscripts are geometric, not semantic.** R1/R2/R3 differ only in physical location, not content.

## Provenance

- Phase: AZC_FOLIO_DIFFERENTIATION
- Script: t4_position_vocabulary.py
- Related: C433 (Block Grammar), C435 (S/R Division)
