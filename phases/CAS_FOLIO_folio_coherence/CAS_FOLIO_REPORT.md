# Phase CAS-FOLIO: Currier A Folio Coherence Test

**Phase ID:** CAS-FOLIO
**Tier:** 2 (STRUCTURAL INFERENCE)
**Status:** COMPLETE
**Date:** 2026-01-07
**Updated:** 2026-01-16 (H-only transcriber filter verified)

---

## Executive Summary

> **Currier A folios are physical containers, not organizational units. Sequential coherence exists without folio-level structure.**

This phase tested whether Currier A entries exhibit within-folio thematic coherence (vocabulary clustering). The answer is definitively NO at the folio level, but YES at the sequential level.

---

## Test Battery

### T1: Within-Folio vs Between-Folio Vocabulary Similarity

**Method:** Compare Jaccard similarity of entry pairs within the same folio vs entry pairs across folios (within same section).

| Metric | Value |
|--------|-------|
| Within-folio similarity | J = 0.018 |
| Between-folio similarity | J = 0.017 |
| Mann-Whitney U | p = 0.997 |

**Verdict:** NO_COHERENCE - within-folio similarity equals between-folio similarity.

---

### T2: Folio Exclusivity vs Section Exclusivity

**Method:** Compare the proportion of entries unique to their folio vs unique to their section.

| Level | Exclusivity |
|-------|-------------|
| Folio-exclusive entries | 0.0% |
| Section-exclusive entries | 100% |

**Verdict:** SECTION_DRIVEN - organization exists at section level, not folio level.

---

### T3: Adjacent Entry Similarity

**Method:** Compare vocabulary similarity of adjacent entries (consecutive line numbers) vs non-adjacent entries within the same folio.

| Metric | Value |
|--------|-------|
| Adjacent pairs similarity | 0.047 |
| Non-adjacent pairs similarity | 0.036 |
| Ratio | 1.31x |
| Mann-Whitney U | p < 0.000001 |

**Verdict:** SEQUENTIAL_COHERENCE - adjacent entries share 31% more vocabulary than non-adjacent entries.

---

### T4: Marker Concentration

**Method:** Test if specific marker classes concentrate within specific folios.

| Metric | Value |
|--------|-------|
| Folio-level Cramer's V | 0.138 |

**Verdict:** WEAK_SPECIALIZATION - some marker preference exists at folio level, but weak.

---

## Synthesis

| Finding | Status |
|---------|--------|
| Folio = organizational unit | FALSIFIED |
| Sequential coherence | CONFIRMED |
| Section-level organization | CONFIRMED (prior) |

Currier A entries cluster locally (adjacent entries share vocabulary) but folio boundaries have no thematic significance. The folio is a physical container (parchment page), not a logical grouping.

---

## New Constraints

| # | Constraint |
|---|------------|
| 345 | Currier A folios lack thematic coherence: within-folio vocabulary similarity (J=0.018) equals between-folio similarity (J=0.017); folio boundaries are physical containers, not organizational units (CAS-FOLIO, Tier 2) |
| 346 | Currier A exhibits SEQUENTIAL COHERENCE: adjacent entries share 1.31x more vocabulary than non-adjacent entries (p<0.000001); local clustering exists without folio-level structure (CAS-FOLIO, Tier 2) |

---

## Implications

1. **For historical interpretation:** The scribe wrote entries sequentially without regard to page boundaries. Adjacent entries likely relate to the same ongoing activity or classification session.

2. **For structural analysis:** Section-level organization (H, P, T) remains the primary grouping. Folio-level analysis is not warranted.

3. **For registry model:** Consistent with categorical enumeration - the scribe recorded things as they were encountered/classified, creating local clusters but no page-level themes.

---

## Files Generated

- `archive/scripts/cas_folio_coherence_test.py` - Test implementation
- `phases/CAS_FOLIO_folio_coherence/CAS_FOLIO_REPORT.md` - This report

---

## Phase Tag

```
Phase: CAS-FOLIO
Tier: 2 (STRUCTURAL INFERENCE)
Subject: Currier A Folio Coherence
Type: Organizational structure test
Status: COMPLETE
Verdict: NO_FOLIO_ORGANIZATION + SEQUENTIAL_COHERENCE
```
