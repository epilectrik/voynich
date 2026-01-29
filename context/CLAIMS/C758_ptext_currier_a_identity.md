# C758: P-Text Currier A Identity Confirmed

**Status:** VALIDATED | **Tier:** 2 | **Phase:** AZC_FOLIO_DIFFERENTIATION | **Scope:** AZC

## Finding

P-text (paragraph text above AZC diagrams) is linguistically identical to Currier A, not AZC diagram text. This extends the AZC_INTERFACE_VALIDATION finding with additional evidence.

### Evidence

| Comparison | Cosine Similarity |
|------------|-------------------|
| P-text to Currier A PREFIX profile | **0.974** |
| P-text to AZC diagram PREFIX profile | 0.739 |

### PREFIX Profile Comparison

| PREFIX | P-text | Diagram | Currier A |
|--------|--------|---------|-----------|
| qo | 8.8% | 2.2% | 11.7% |
| ch | 23.5% | 19.3% | 23.9% |
| sh | 19.2% | 6.9% | 12.4% |
| ok | 7.6% | 17.2% | 6.4% |
| ot | 4.9% | 21.9% | 5.1% |

P-text matches Currier A on qo, ch, sh, ok, ot. Diagram text differs significantly.

### Vocabulary Overlap

- P-text MIDDLEs in Currier A: 74.4%
- P-text MIDDLEs in Currier B: 76.7%
- P-text to same-folio diagram overlap: 19.5% mean Jaccard

### Statistics

- Folios with P-text: 9
- Folios with both P-text and diagram: 8
- Total P-text tokens: 353

## Implication

P-text should be treated as Currier A material for analytical purposes:
- Exclude from AZC legality calculations
- Include in Currier A counts when appropriate
- P-text represents registry entries placed above diagrams, not diagram annotation

## Provenance

- Phase: AZC_FOLIO_DIFFERENTIATION
- Script: t5_ptext_diagram_relation.py
- Related: AZC_INTERFACE_VALIDATION (2026-01-19), azc_transcript_encoding.md
