# C1232 - Paragraph Tail Product Signatures

**Tier:** 2 | **Scope:** B | **Phase:** EXTRACTION_CYCLING_VALIDATION (Phase 439)

## Statement

The final 2 body lines of paragraphs cluster into 3 distinct PREFIX+MIDDLE profiles (k=3, silhouette 0.212) that correlate with section (chi2=31.73, p=0.0001). Different paragraphs end with different operational signatures, suggesting the tail of a paragraph encodes the output product type or final processing mode.

## Evidence

### Tail clustering (276 paragraphs with 3+ body lines)

| k | Silhouette | Cluster sizes |
|---|-----------|---------------|
| 2 | 0.197 | [145, 131] |
| 3 | **0.212** | [75, 113, 88] |
| 4 | 0.203 | [80, 60, 76, 60] |

### Section correlation

| Metric | Value |
|--------|-------|
| Chi-squared (section x cluster) | 31.73 |
| p-value | 0.0001 |

### Key observations

1. **Three tail types**: k=3 is optimal, suggesting paragraphs end in one of three distinct operational modes
2. **Section-correlated**: The tail cluster assignment correlates with section (BIO, HERBAL, STARS), indicating section-level differences in output product or final processing
3. **Feature space**: Clustering uses 6 features — PREFIX domain fractions (energy, vessel, process) and MIDDLE family fractions (k-family, e-family, prep-family) — from the final 2 body lines

## Interpretation

Different paragraphs produce different outputs, and the final body lines encode what that output is. The three tail types may correspond to different product forms (e.g., liquid distillate, dry compound, aromatic water) or different final processing modes (e.g., collection, grinding, further refinement). The section correlation suggests that material type (botanical, biological, astronomical/pharmaceutical) influences the output product.

## Related constraints

- C1229: Alternating suffix modes (body-level cycling)
- C1230: Mode MIDDLE differentiation (functional distinction)
- C932: Body vocabulary gradient (spec->exec through body)
- F-BRU-020: Output category vocabulary signatures (OIL vs WATER markers)

## Provenance

- `phases/EXTRACTION_CYCLING_VALIDATION/scripts/extraction_cycling_test.py` (T7)
- `phases/EXTRACTION_CYCLING_VALIDATION/results/extraction_cycling_results.json`
