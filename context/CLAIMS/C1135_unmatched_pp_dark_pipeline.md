# C1135: Unmatched PP MIDDLEs Form a Dark Pipeline

**Tier:** 2
**Status:** Active
**Scope:** A->B
**Phase:** 406 (CROSS_SYSTEM_VOCABULARY_FLOW)

## Finding

Of 404 PP MIDDLEs (shared between A and B), only 89 match B's 49-class grammar. The remaining 315 "unmatched" PPs are overwhelmingly present in B (95.2%, 300/315) but at dramatically lower frequency and with distinct properties.

| Property | Matched PP (89) | Unmatched PP B-present (300) | Ratio |
|----------|-----------------|------------------------------|-------|
| Mean B tokens | 224.8 | 5.7 | 39.4x |
| Mean B folios | 39.0 | 4.6 | 8.5x |
| Mean Herfindahl | 0.410 | 0.716 | 1.7x more concentrated |
| Compound rate | — | 66.7% | High |

15 PP MIDDLEs (4.8%) are B-absent — they appear in the canonical shared list but not in actual B tokens (phantom sharing from morphological extraction edge cases).

Of the 300 B-present unmatched PPs:
- 66 (22.0%) are section-universal (Herfindahl < 0.5)
- 234 (78.0%) are section-concentrated (Herfindahl >= 0.5)

This is a **large, previously uncharacterized vocabulary substrate** — present in both A and B, carrying pipeline vocabulary outside classified grammar, mostly as HT/UN compounds. It is the morphological bridge between A's registry and B's unclassified identification layer.

## Interpretation

The unmatched PP population bridges A and B through **morphological composition**: 66.7% are compound MIDDLEs containing matched PP atoms as substrings. They do not directly participate in B's 49-class execution grammar but provide the derivational substrate from which HT/UN tokens are built (consistent with C924: 97.9% HT containment, and C994: 94.1% B-exclusive contain A-space atoms).

## Evidence

- 404 PP MIDDLEs from `middle_classes.json`
- 89 matched from `pp_role_foundation.json`
- B token counts, folio counts, section distributions computed from H-track transcript
- Compound detection via MiddleAnalyzer

## Provenance

- Source: Phase 406, Test B1
- Related: C498 (RI/PP bifurcation), C584 (pipeline purity), C792 (B-exclusive = HT), C924 (HT PP-atom containment)
