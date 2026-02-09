# AZC Pattern Audit

**Status:** COMPLETE
**Date:** 2026-02-02
**Result:** One new constraint (C904), one observation documented

---

## Summary

Following completion of AZC folio annotation, this phase audited the folio notes for patterns worth investigating. Two patterns were examined:

1. **F-character cluster** (reported in f71v-f73v) - NOT CONFIRMED as folio cluster, but S-zone enrichment found
2. **Output markers (-ry suffix) in S-zones** - CONFIRMED with 3.18x enrichment

---

## Investigation 1: F-Character Cluster

### Original Observation
F-character tokens appeared concentrated in late AZC folios (f71v-f73v).

### Finding: NOT CONFIRMED as Folio Cluster

| Location | F-tokens | Percentage |
|----------|----------|------------|
| f71v-f73v (late) | 25 | 43.1% |
| Earlier folios | 33 | 56.9% |

No strong folio concentration. F-tokens are distributed across AZC.

### Secondary Finding: S-Zone Position Enrichment

| Position | F-tokens | Percentage |
|----------|----------|------------|
| S-zones | 23 | 39.7% |
| R-zones | 15 | 25.9% |
| C (center) | 9 | 15.5% |
| Other | 11 | 19.0% |

- S-zone baseline: 15.3%
- F-token S-zone rate: 39.7%
- Enrichment: ~2.6x

### Morphological Pattern

- F in MIDDLE: 53/58 (91.4%)
- F in PREFIX: 5/58 (8.6%)
- F in SUFFIX: 0/58 (0%)

### Verdict

F-character S-zone enrichment is **independent of -ry pattern** (only 1 token overlaps: "yfary"). However, without an established functional role for f-character, this remains an observation rather than a constraint.

---

## Investigation 2: Output Markers (-ry Suffix)

### Original Observation
-ry suffix tokens appeared at boundary positions (S-zones).

### Finding: CONFIRMED - S-ZONE ENRICHMENT

| Metric | Value |
|--------|-------|
| -ry in S-zones | 19/39 (48.7%) |
| Baseline S-zone rate | 15.3% |
| **Enrichment** | **3.18x** |

### Cross-Validation

This finding connects two independent analyses:

1. **C839:** Identified -ry as strongest OUTPUT marker (5x OUTPUT bias)
2. **C435/C443:** S-zones have zero escape permission (commitment positions)

OUTPUT markers concentrating at commitment positions is structurally coherent.

### Token Details

Classification:
- PP: 28 (71.8%)
- INFRA: 9 (23.1%)
- UNKNOWN: 2 (5.1%)

Distribution across 20 folios (not concentrated in specific folios).

### Constraint Drafted

**C904: -ry Suffix S-Zone Enrichment**
- Tier 2 (statistical finding with structural coherence)
- Location: `context/CLAIMS/C904_ry_szone_enrichment.md`

---

## Independence Test

Checked whether f-character and -ry patterns overlap:

| Metric | Value |
|--------|-------|
| F-tokens in S-zones | 23 |
| -ry tokens in S-zones | 19 |
| Overlap (both f and -ry) | 1 (yfary) |
| F-only in S-zones | 22 (95.7%) |

The patterns are independent.

---

## Quantitative Summary

| Pattern | Finding | Enrichment | Action |
|---------|---------|------------|--------|
| F-character folio cluster | Not confirmed | N/A | None |
| F-character S-zone | Observed | 2.6x | Document only |
| -ry S-zone | **Confirmed** | **3.18x** | **C904 drafted** |

---

## New Constraint

### C904: -ry Suffix S-Zone Enrichment

-ry suffix tokens show 3.18x enrichment in S-zones (48.7% vs 15.3% baseline). This cross-validates C839 (OUTPUT marker identification) through spatial distribution in AZC diagrams.

**Interpretation:** S-zones function as output capture positions where processing results are committed. The -ry suffix marks tokens appropriate for these commitment points.

---

## Files

- `context/CLAIMS/C904_ry_szone_enrichment.md` - New constraint
- Investigation scripts in session scratchpad
