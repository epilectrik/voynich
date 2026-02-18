# C1094: Rosettes Exclusive Vocabulary Is Morphological Tail

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** AZC
**Phase:** ROSETTES_SYSTEM_CLASSIFICATION (Phase 388H)
**Extends:** C618 (unique MIDDLE identity: length 4.55, 99.7% hapax), C766 (UN = derived identification vocabulary)
**Relates to:** C498 (RI vocabulary track), C300 (AZC 3,299 unclassified tokens)

---

## Statement

79 MIDDLEs found in Rosettes appear nowhere else in the manuscript (not in A, B, or AZC). These exclusive MIDDLEs have mean length 4.91 characters, 98.7% hapax rate, and 78.5% are compound (contain core MIDDLEs as substrings). This profile matches the UN (unclassified) population structure (81.1% compound per C766) and the unique MIDDLE identity profile (C618).

---

## Evidence

### Exclusive MIDDLE Properties

| Property | Rosettes Exclusive | C618 Profile | C766 UN Profile |
|----------|-------------------|--------------|-----------------|
| Mean length | 4.91 | 4.55 | — |
| Hapax rate | 98.7% | 99.7% | — |
| Compound rate | 78.5% | — | 81.1% |

### Distribution

- 101 unique MIDDLEs in Rosettes not found in B body text (32.8% of Rosettes vocabulary)
- 79 of these appear in NO other system (A, B, or AZC)
- 18 appear in A but not B ("A-not-B MIDDLEs")
- 8 appear in AZC but not B ("AZC-not-B MIDDLEs")

---

## Interpretation

The exclusive vocabulary is a morphological tail — longer, rarer, more compound tokens that extend the core vocabulary through derivational processes. This is consistent with C766 (UN population as derived identification vocabulary) and suggests these exclusive terms are specialized reference identifiers that name categories or processes not directly expressed in running text. Their compound structure implies they are constructed from core vocabulary atoms, not arbitrary novel forms.

---

## Method

- Extract all MIDDLEs from Rosettes tokens via Morphology.extract()
- Cross-reference against A, B, AZC corpora
- Profile length, hapax rate, compound rate for exclusive subset

**Script:** `phases/ROSETTES_SYSTEM_CLASSIFICATION/scripts/rosettes_metalayer.py` (T3)
**Results:** `phases/ROSETTES_SYSTEM_CLASSIFICATION/results/rosettes_metalayer_results.json`

---

## Verdict

**MORPHOLOGICAL_TAIL**: Rosettes exclusive vocabulary (79 MIDDLEs) is a derived, compound extension of core vocabulary — consistent with identification/naming function rather than execution.
