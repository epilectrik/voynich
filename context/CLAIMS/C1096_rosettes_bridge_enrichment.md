# C1096: Rosettes Bridge MIDDLE Enrichment

**Tier:** 2 (STRUCTURAL INFERENCE)
**Scope:** ROSETTES
**Phase:** ROSETTES_STRUCTURAL_VALIDATION (Phase 389)
**Strengthens:** C1095 (metalayer status), C1089 (near-complete coverage)
**Extends:** C1013 (bridge topological selection), C1014 (viability alignment)

---

## Statement

The Rosettes foldout is massively enriched for bridge MIDDLEs — the 85 vocabulary items (C1013) that cross from A's discrimination manifold into B's 49-class grammar. Rosettes bridge rate = 24.4% vs B corpus baseline = 7.0%, yielding 3.46x enrichment (Fisher's exact p = 6.9e-16, OR = 4.25). This is the strongest quantitative signal distinguishing Rosettes from normal B text.

---

## Evidence

### Overall Enrichment

| Corpus | Bridge MIDDLEs | Total Unique MIDDLEs | Bridge Rate | Enrichment |
|--------|----------------|---------------------|-------------|------------|
| B corpus | 85 | 1,208 | 7.0% | 1.0x (baseline) |
| Rosettes | 75 | 308 | 24.4% | 3.46x |

Fisher's exact test (one-sided): p = 6.9e-16, odds ratio = 4.25

### Per Region Type (C1093 bifurcation)

| Region Type | Bridges | Total MIDDLEs | Bridge Rate | Enrichment |
|-------------|---------|---------------|-------------|------------|
| LABEL (A-like) | 22 | 49 | 44.9% | 6.38x |
| DESCRIPTION (B-like) | 30 | 46 | 65.2% | 9.27x |

Both region types show extreme enrichment. DESCRIPTION regions are even more bridge-heavy than LABEL regions.

### Per Folio

| Folio | Bridges | Total | Rate | Enrichment |
|-------|---------|-------|------|------------|
| f85r1 | 45 | 103 | 43.7% | 6.21x |
| f85r2 | 41 | 65 | 63.1% | 8.96x |
| f85v2 | 36 | 78 | 46.2% | 6.56x |
| f86v3 | 45 | 79 | 57.0% | 8.10x |
| f86v4 | 46 | 79 | 58.2% | 8.28x |
| f86v5 | 51 | 88 | 58.0% | 8.24x |
| f86v6 | 57 | 120 | 47.5% | 6.75x |

All 7 folios show 6-9x enrichment. No folio is at baseline.

---

## Implication

Bridge MIDDLEs are by definition the most general, compatible vocabulary — they span A's discrimination space into B's execution grammar (C1013: frequency 55x, folio spread 26x, compatibility degree 12x higher than non-bridges). The Rosettes preferentially uses this cross-system connective vocabulary, consistent with its role as a structural index (C1095) that references across A/B/AZC boundaries.

Per C1014, bridge MIDDLEs carry 91% of the viability signal in the discrimination manifold. By concentrating bridges, the Rosettes indexes the vocabulary that carries almost all functional meaning.

---

## Provenance

- Phase: 389 (ROSETTES_STRUCTURAL_VALIDATION), Test V2
- Script: `phases/ROSETTES_STRUCTURAL_VALIDATION/scripts/rosettes_structural_validation.py`
- Results: `phases/ROSETTES_STRUCTURAL_VALIDATION/results/rosettes_structural_validation.json`
- Related: C1013, C1014, C1089, C1095, C1098
