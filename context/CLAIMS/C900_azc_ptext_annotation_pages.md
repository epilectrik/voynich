# C900: AZC P-Text Annotation Pages

**Scope:** AZC
**Tier:** 2
**Status:** VALIDATED

---

## Claim

f65v and f66v are the only AZC folios with 100% P-text placement. They are linguistically Currier A (0.941 PREFIX cosine) and serve as annotation/specification pages for the adjacent f66r ring diagram.

---

## Evidence

### Test 28: P-Text Only Folio Census

| Folio | Tokens | P-text % | Cosine to A | Cosine to B |
|-------|--------|----------|-------------|-------------|
| f65v  | 44     | 100%     | **0.941**   | 0.847       |
| f66v  | 103    | 100%     | **0.941**   | 0.847       |

All other AZC folios have mixed P-text and diagram positions (C, R, S).

### Test 29: Physical Layout

```
f65v (P-text) | f66r (ring diagram) | f66v (P-text)
```

f66r contains 295 tokens, all in R (ring) placement - a zodiac-style diagram.

### Test 29: Vocabulary Overlap

| Comparison   | % of P-text MIDDLEs in f66r | Jaccard |
|--------------|------------------------------|---------|
| f65v ↔ f66r  | 63.3%                        | 0.261   |
| f66v ↔ f66r  | 59.0%                        | 0.240   |
| f65v ↔ f66v  | -                            | 0.524   |

High vocabulary overlap confirms content relationship, not accidental placement.

---

## Structural Interpretation

f65v and f66v are not misbound or misclassified pages. They are:

1. **Linguistically Currier A** - registry-style text, not diagram labels
2. **Physically flanking f66r** - positioned as annotation pages for the zodiac diagram
3. **Content-related to f66r** - 60%+ vocabulary overlap with the diagram
4. **Structurally unique** - the only 100% P-text folios in AZC

This pattern suggests **deliberate annotation** - A-style material specifications placed adjacent to AZC diagrams for which they provide context.

---

## Metadata Anomaly

- f65v: Currier = NA (standard for AZC)
- f66v: Currier = B (despite being linguistically A)

The f66v classification may be a transcription artifact.

---

## Provenance

- **Phase:** PTEXT_FOLIO_ANALYSIS
- **Scripts:** t27_f65v_investigation.py, t28_ptext_only_folios.py, t29_f65v_f66_context.py
- **Date:** 2026-01-31

---

## Related

- C758: P-text Currier A identity
- C486: P-text vocabulary correlates with high-escape B
- azc_system.md: P-text analytical reclassification
