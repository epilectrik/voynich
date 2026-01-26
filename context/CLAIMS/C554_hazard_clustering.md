# C554: Hazard Class Clustering

**Tier:** 2 | **Status:** CLOSED | **Scope:** B

---

## Statement

> Hazard-adjacent classes cluster within lines (dispersion index 1.29, p<0.001) rather than dispersing. 93% of lines contain hazard-adjacent classes with mean 3.1 per line. Gateway-terminal pairing is near-baseline (1.06x), confirming C548 manuscript-level envelope. Hazard management is zone-concentrated, not point-distributed.

---

## Evidence

**Test:** `phases/CLASS_SEMANTIC_VALIDATION/scripts/hazard_class_cooccurrence.py`

### Hazard Class Presence

| Metric | Value |
|--------|-------|
| Lines with hazard-adjacent class | 2,240 (93%) |
| Lines with 2+ hazard classes | 1,856 (77%) |
| Mean hazard classes per line | 3.07 |

### Distribution of Hazard Count per Line

| Count | Lines | % |
|-------|-------|---|
| 0 | 180 | 7.4% |
| 1 | 384 | 15.9% |
| 2 | 497 | 20.5% |
| 3 | 435 | 18.0% |
| 4 | 393 | 16.2% |
| 5+ | 531 | 21.9% |

### Dispersion Test

| Metric | Value |
|--------|-------|
| Observed variance | 3.943 |
| Expected variance (Poisson) | 3.067 |
| **Dispersion index** | **1.29** |
| Chi-square | 3109.5 |
| p-value | < 0.001 |

**Result:** CLUSTERED (dispersion > 1.2)

### Gateway-Terminal Pairing

| Metric | Value |
|--------|-------|
| Observed co-occurrence | 136 lines |
| Expected | 128.4 lines |
| Enrichment | 1.06x |
| p-value | 0.50 (not significant) |

### Significant Pairings

| Pair | Classes | Observed | Expected | Enrichment |
|------|---------|----------|----------|------------|
| 8-32 | ENERGY | 272 | 201.1 | **1.35x** |
| 32-33 | PHASE_ORDERING | 335 | 294.4 | 1.14x |

---

## Interpretation

### Zone-Concentrated Hazard Management

The grammar **does not** manage hazards by dispersing hazard-adjacent classes across lines. Instead:

1. **Clustering:** Lines that contain hazard operations tend to contain multiple hazard-adjacent classes
2. **Pervasive:** 93% of lines are in "hazard zones" with at least one hazard-adjacent class
3. **Concentration:** Modal line has 2-4 hazard classes, not 0-1

### Why Clustering?

Hazard-adjacent operations likely require:
- **Nearby stabilization:** Thermal operations need local control
- **Context continuity:** ENERGY operations chain together (C550)
- **Zone semantics:** Lines are "thermal zones" or "flow zones", not mixed

### Gateway-Terminal Independence

The near-baseline gateway-terminal pairing (1.06x) confirms:
- C548's manuscript-level envelope is NOT implemented at line level
- Gateway and terminal are structurally independent within lines
- The arc from entry to exit spans folios, not lines

### ENERGY Class Affinity

Class 8-32 enrichment (1.35x) aligns with C550 (ENERGY self-chaining). ENERGY operators cluster because thermal operations require sustained attention.

---

## Cross-References

| Constraint | Relationship |
|------------|--------------|
| C548 | Confirmed - envelope is manuscript-level, not line-level |
| C550 | Related - ENERGY clustering explains 8-32 pairing |
| C109 | Extended - hazard classes from failure topology cluster |
| C541 | Contextualized - hazard enumeration now has spatial pattern |

---

## Provenance

- **Phase:** CLASS_SEMANTIC_VALIDATION
- **Date:** 2026-01-25
- **Script:** hazard_class_cooccurrence.py

---

## Navigation

<- [C553_bio_regime_independence.md](C553_bio_regime_independence.md) | [INDEX.md](INDEX.md) ->
