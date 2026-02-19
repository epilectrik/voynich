# C1123: Rosettes Section-Categorical Index Structure

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** GLOBAL
**Phase:** ROSETTES_B_VOCABULARY_TRACING (Phase 401)
**Extends:** C1091 (multi-target cross-reference), C1090 (Section T correlation)
**Relates to:** C1098 (structural index), C1109 (vocabulary-mediated), C1029 (section-parameterized grammar)

---

## Statement

Rosettes decomposes into two section-targeting vocabulary groups with zero overlap. The T-targeting group (CENTER+NORTH+NW, 15 informative MIDDLEs) points to Section T at 4.14x enrichment (F=19.37, p<0.0001). The S-targeting group (WEST+SW, 9 informative MIDDLEs) points to Section S at 2.04x enrichment (F=10.23, p<0.0001). The two groups share 0 informative MIDDLEs. Rosettes indexes B programs at the section-category level — each rosette contributes unique vocabulary pointing toward pharmaceutical/recipe sections, but the indexing does not resolve to individual B folios. Label regions discriminate among B sections more than ring-text regions (CV=1.14 vs 0.95).

---

## Evidence

### Dual Section-Targeting Groups

| Group | Rosettes | Informative MIDDLEs | Top Section | Enrichment | F-ratio | p-value |
|-------|----------|---------------------|-------------|------------|---------|---------|
| T-targeting | CENTER, NORTH, NW | 15 | T | 4.14x | 19.37 | <0.0001 |
| S-targeting | WEST, SW | 9 | S | 2.04x | 10.23 | <0.0001 |

Inter-group vocabulary overlap: 0 MIDDLEs shared.

### T-Group Informative MIDDLEs
dar, ea, ech, edaii, ir, ld, odai, ofai, og, opd, oqot, rai, ro, x, yp

### S-Group Informative MIDDLEs
ch, cphed, edsh, eed, eolk, oda, opaii, opchd, pai

### Section Enrichment Detail

T-group section means: T=5.5, S=2.435, C=1.4, B=0.85, H=0.562
S-group section means: S=1.565, T=1.0, B=0.5, C=0.4, H=0.406

Both groups point toward pharmaceutical sections (T and S). Section H (Herbal) is depleted in both (0.42x and 0.53x). This is consistent with C1091's finding that all label groups converge on pharmaceutical folios.

### Label vs Ring-Text Discrimination

Label vocabulary CV=1.14, ring-text CV=0.95. Labels carry more section-discriminative vocabulary, consistent with C1093's label-description bifurcation — labels are A-like index entries, descriptions are B-like generic skeletons.

### Interpretation

The Rosettes foldout is a section-categorical reference chart. Different rosettes index different pharmaceutical sections using non-overlapping vocabulary. The NW-NORTH-CENTER corridor (physically: the northern/central rosettes) indexes Section T. The WEST-SW corridor indexes Section S. The indexing is categorical (rosette → section type) not specific (rosette → particular B folio). This is consistent with C1098 (structural index, score 0.92) and extends it with section-targeting decomposition.

---

## Provenance

- Phase: 401 (ROSETTES_B_VOCABULARY_TRACING)
- Scripts: `phases/ROSETTES_B_VOCABULARY_TRACING/scripts/rosettes_b_tracing.py`, `rosettes_grouping_test.py`
- Results: `phases/ROSETTES_B_VOCABULARY_TRACING/results/rosettes_b_tracing_results.json`, `rosettes_grouping_results.json`
- Related: C1090, C1091, C1098, C1109, C1029, C1093
