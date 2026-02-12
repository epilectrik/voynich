# C989: B Execution Inhabits A's Discrimination Geometry

**Tier:** 2 | **Scope:** A↔B | **Phase:** DISCRIMINATION_SPACE_DERIVATION

## Statement

Currier B line-level MIDDLE co-occurrence massively respects A's compatibility boundaries: 80.2% of token-weighted B pair encounters are A-compatible (37× enrichment over A's baseline 2.2% density). Pair-level: 39.4% A-compatible at 18.1× enrichment (binomial p = 0.0). Residual-space cosine correctly separates: A-compatible B pairs +0.076, random +0.003, A-incompatible -0.051. B does not merely tolerate A's constraints — B actively selects within A's geometry.

## Evidence

### Compatibility Concordance (T12)

| Metric | Value |
|--------|-------|
| B MIDDLEs total | 1,293 |
| B MIDDLEs in A-space (972) | 393 (30.4%) |
| B-exclusive MIDDLEs | 900 |
| B co-occurring pairs | 8,587 |
| A-compatible pairs | 3,382 (39.4%) |
| A-incompatible pairs | 5,205 (60.6%) |
| A baseline compatibility rate | 2.2% |
| **Pair-level enrichment** | **18.1×** |
| **Token-weighted compatibility** | **80.2%** |
| **Token-level enrichment** | **37.0×** |
| Binomial p-value | 0.0 (underflow) |

### Residual Space Geometry (T12)

| Pair Type | Residual Cosine | Residual Euclidean |
|-----------|----------------|-------------------|
| A-compatible B pairs | +0.076 | 2.678 |
| A-incompatible B pairs | -0.051 | 2.150 |
| Random baseline | +0.003 | 1.467 |

Compatible pairs face the **same direction** in residual space (positive cosine); incompatible pairs face **opposite directions** (negative cosine). The geometry is correctly oriented.

### Violation Analysis (T12)

| Property | Compatible Pairs | Incompatible Pairs |
|----------|-----------------|-------------------|
| Mean frequency sum | 347.5 | 134.6 |
| Concentration | High-frequency MIDDLEs | Low-frequency MIDDLEs |

Violations concentrate in rare MIDDLEs where A had insufficient line-level coverage to establish compatibility — observation gap, not structural violation.

### B Section Differentiation (T12)

Section S (Stars) stands alone in residual space:
- Cosine similarity with other sections: 0.15-0.32
- Other section pairs: 0.73-0.87
- B inherits A's section-level manifold geography

### Interpretation

1. 80.2% token-level concordance means **most of what B actually does** respects A's boundaries
2. The 18× pair enrichment is not just frequency overlap — it's geometric alignment in residual space
3. Violations are an observation artifact (rare MIDDLEs) not a structural exception
4. B's execution grammar (C121, 49 classes) operates within A's constraint manifold
5. This is the geometric realization of C468 (legality inheritance): A defines the constraint surface, AZC selects regions, B executes within them

## Provenance

- T12 (B-side embedding concordance)
- Mechanizes C468 (legality inheritance) geometrically
- Consistent with C502 (filtering cascade A→AZC→B)
- Extends C983 (transitive compatibility) into B — B's co-occurrence graph respects A's transitivity
- Section S isolation consistent with C941 (section as vocabulary organizer)
