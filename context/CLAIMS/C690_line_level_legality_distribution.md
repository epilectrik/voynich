# C690: Line-Level Legality Distribution

**Status:** VALIDATED | **Tier:** 2 | **Phase:** A_RECORD_B_FILTERING | **Scope:** A-B

## Finding

A-record filtering renders **most B folio lines empty**. Across 32 representative (record, folio) pairings, 25/32 (78.1%) have >50% empty lines. Only the least restrictive A record (Max-classes, 38 surviving classes) keeps most lines populated (7-27% empty). The median record makes 74-100% of lines empty. **Legality does not vary with line position** (Spearman rho=0.005, p=0.87).

## Key Pairings

| Record Profile | PP | Classes | Empty Line % (across 4 folios) |
|---------------|----|---------|-----------------------------|
| Minimal-PP | 0 | 0 | 100% (all 4 folios) |
| Low-PP | 3 | 6 | 69-80% |
| Median-PP | 6 | 8 | 74-100% |
| High-PP | 11 | 24 | 38-55% |
| Max-classes | 14 | 38 | 7-27% |
| Min-classes | 2 | 1 | 94-100% |
| PURE_RI | 1 | 1 | 98-100% |

## Key Numbers

| Metric | Value |
|--------|-------|
| Pairings analyzed | 32 (8 records x 4 folios) |
| Pairings >50% empty | 25 (78.1%) |
| Position-legality correlation | rho=0.005, p=0.87 (none) |
| Best pairing mean legality | 25.9% (Max-classes, Largest) |
| Worst pairing mean legality | 0.0% (Minimal-PP, all folios) |

## Interpretation

A single A record acting on a B folio creates a **sparse residual program**. The typical A record (median PP=6, 8 classes) renders 74-100% of lines entirely empty. This is not a defect — it reflects the **high specificity** of A-B morphological filtering. Each A record selects a narrow vocabulary slice, and most B lines contain tokens outside that slice.

## Provenance

- Script: `phases/A_RECORD_B_FILTERING/scripts/instance_trace_analysis.py` (Test 9)
- Extends: C682 (population profile), C502.a (filtering algorithm)
