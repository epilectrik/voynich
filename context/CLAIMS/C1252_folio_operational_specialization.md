# C1252: Folio Operational Specialization

**Tier:** 2 (ESTABLISHED)
**Scope:** B
**Phase:** PARAGRAPH_OPERATIONAL_CLASSIFICATION (Phase 447)
**Extends:** C1041 (folio = program), C1250 (gloss category structural coherence)
**Relates to:** C827 (paragraph = operational unit), C678 (line-level continuous)

---

## Statement

Paragraphs within a folio share more similar operational gloss profiles than paragraphs from different folios within the same section. Within-folio Jensen-Shannon divergence (0.263) is significantly lower than between-folio JSD (0.294), p=0.000 (1000 within-section permutations, 74 multi-paragraph folios).

This demonstrates **folio-level operational specialization**: each folio (= program) concentrates on a characteristic mix of operational categories rather than sampling uniformly from the section's category distribution. The delta (0.031) is modest but highly significant, consistent with folios having focused operational identities within the continuous category space.

---

## Interpretation

Folios are not just structural programs (C1041) — they are operationally specialized. A folio focused on thermal operations has paragraphs that consistently emphasize THERMAL category tokens; a folio focused on flow operations has paragraphs emphasizing FLOW. This specialization operates within the continuous category space (no discrete types exist per T2: sil=0.192), meaning folios occupy characteristic positions in operational space rather than falling into discrete clusters.

---

## Method

- 466 paragraphs with >=5 classified body tokens (line 2+ only, excluding header per C840)
- Body gloss profile: 8-category fraction vector from classified tokens using C1250 categories
- Pairwise JSD between all paragraph pairs within each multi-paragraph folio (within-folio) vs between folios within same section (between-folio)
- Null model: permute paragraph-folio assignments within section (1000 permutations)
- 74 folios with 2+ qualifying paragraphs

**Script:** `phases/PARAGRAPH_OPERATIONAL_CLASSIFICATION/scripts/paragraph_operational_classification.py`
**Results:** `phases/PARAGRAPH_OPERATIONAL_CLASSIFICATION/results/paragraph_operational_classification.json`
