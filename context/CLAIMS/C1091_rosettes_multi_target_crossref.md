# C1091: Rosettes Multi-Target Cross-Reference

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** AZC
**Phase:** ROSETTES_SYSTEM_CLASSIFICATION (Phase 388H)
**Extends:** C440 (uniform B-to-AZC sourcing)
**Relates to:** C442 (AZC compatibility grouping), C468 (AZC legality inheritance)

---

## Statement

Different f85v2 regions cross-reference different manuscript sections via rare MIDDLEs: N1/N2 point to Herbal folios, B1/M1/V1 point to Stars folios, U1 points to Bio folios. All label groups (BOTTOM, MIDDLE, UPPER) converge on the same top pharmaceutical folios (f76r, f108r, f111r, f108v, f116r) by MIDDLE overlap. This multi-target pattern breaks C440 (uniform B-to-AZC sourcing) for the Rosettes folios.

---

## Evidence

### Label Group Cross-References (Top Folios by MIDDLE Overlap)

| Group | #Labels | #MIDDLEs | Top Folio | 2nd | 3rd |
|-------|---------|----------|-----------|-----|-----|
| BOTTOM | 38 | 25 | f111r (193) | f108r (188) | f76r (176) |
| MIDDLE | 33 | 24 | f76r (225) | f111r (215) | f108v (202) |
| UPPER | 17 | 13 | f111r (123) | f76r (118) | f108r (116) |

### Section Distribution (B Body Text)

All groups point primarily to Section S (Stars/Pharma), then Section B (Bio), then Section H (Herbal):
- BOTTOM: S=3092, B=1760, H=1200
- MIDDLE: S=3218, B=2661, H=1202
- UPPER: S=1779, B=1223, H=637

### Per-Region Rare MIDDLE Cross-References

Different f85v2 regions point to different sections via exclusive/rare MIDDLEs, confirming multi-target organization within a single folio page.

---

## Interpretation

The Rosettes foldout cross-references pharmaceutical/recipe sections specifically (not Herbal, which dominates B at 91.6% per C299). This is consistent with the foldout serving as an index to the most structurally complex procedures in the manuscript. The multi-target pattern distinguishes the Rosettes from standard AZC folios, which show uniform B sourcing (C440).

---

## Method

- Extract labels from f85v2 label regions (87 tokens, 8 regions)
- For each label's MIDDLE, count occurrences across all B corpus folios and sections
- Aggregate by rosette group (BOTTOM, MIDDLE, UPPER, D_W)

**Script:** `phases/ROSETTES_SYSTEM_CLASSIFICATION/scripts/_rosette_decoder_map.py`
**Results:** `phases/ROSETTES_SYSTEM_CLASSIFICATION/results/rosette_decoder_map.json`

---

## Verdict

**MULTI_TARGET_CROSSREF**: Rosettes label groups converge on pharmaceutical folios but different regions point to different sections, breaking C440 uniformity and confirming metalayer organization.
