# C887 - WITHOUT-RI Backward Reference

**Tier:** 2 | **Scope:** A | **Phase:** CURRIER_A_STRUCTURE_V2

## Statement

WITHOUT-RI paragraphs show backward reference to preceding paragraphs, with vocabulary overlap asymmetry of 1.23x (backward > forward). Highest overlap occurs when following a WITH-RI paragraph (Jaccard 0.228).

## Evidence

From CURRIER_A_STRUCTURE_V2 test 19:

**Backward vs Forward Overlap:**

| Direction | WITH-RI | WITHOUT-RI |
|-----------|---------|------------|
| BACKWARD (with PREV) | 0.189 | 0.202 |
| FORWARD (with NEXT) | 0.207 | 0.164 |
| **Asymmetry (back/forward)** | 0.91x | **1.23x** |

**By Predecessor Type:**

| Sequence | Jaccard | Interpretation |
|----------|---------|----------------|
| WITHOUT-RI after WITH-RI | **0.228** | Process applies to just-identified material |
| WITHOUT-RI after WITHOUT-RI | 0.169 | Lower overlap |
| WITH-RI after WITH-RI | 0.198 | Baseline |
| WITH-RI after WITHOUT-RI | 0.157 | Lowest |

## Cross-Folio Continuity

FIRST-position WITHOUT-RI paragraphs do NOT continue from previous folios:
- Cross-folio overlap: 0.209 (similar to WITH-RI's 0.223)
- Backward reference is primarily a within-folio phenomenon

## Mechanism

**Sequential convention:** WITHOUT-RI paragraphs reference the material identified in the preceding WITH-RI paragraph. The process instructions apply to the just-identified material.

This is NOT syntactic continuation (rejected by test 08) but semantic reference through shared vocabulary.

## Provenance

- `phases/CURRIER_A_STRUCTURE_V2/results/backward_reference_test.json`
- `phases/CURRIER_A_STRUCTURE_V2/results/crossfolio_continuity.json`
- Related: C881 (paragraph structure), C731 (PP adjacent line continuity)

## Status

CONFIRMED - Asymmetry measured across 85 WITHOUT-RI paragraphs with predecessors.
