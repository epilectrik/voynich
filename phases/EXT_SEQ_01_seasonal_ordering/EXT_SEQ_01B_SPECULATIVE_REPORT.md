# EXT-SEQ-01B: Speculative Plant Identification & Finer-Grained Seasonal Analysis

**Status:** COMPLETE
**Tier:** 4 (SPECULATIVE)
**Date:** 2026-01-05

---

## Epistemic Warning

**THIS ANALYSIS USES SPECULATIVE PLANT IDENTIFICATIONS**

The plant identifications in this report are hypotheses based on:
- PIAA morphological descriptions
- Historical availability in 15th-century Central Europe / Northern Italy
- Aromatic/perfumery relevance

Individual identifications may be incorrect. Results should be interpreted with caution.

---

## Section 1 - Speculative Plant Identifications

### Methodology

1. Started with PIAA morphological descriptions (leaf shape, flower form, root emphasis)
2. Cross-referenced with plants documented in medieval aromatic practice:
   - Brunschwig's *Liber de Arte Distillandi* (1500)
   - Medieval monastery garden records
   - Historical perfumery sources
3. Assigned peak flowering/harvest month based on botanical references
4. Classified by confidence (VERY HIGH, HIGH, MEDIUM, LOW)

### Sources Consulted

- [Perfume Society - Orris Root](https://perfumesociety.org/ingredients-post/orris-root/)
- [Wikipedia - Orris Root](https://en.wikipedia.org/wiki/Orris_root)
- [RHS - Fennel Growing Guide](https://www.rhs.org.uk/herbs/fennel/grow-your-own)
- [English Heritage - Medieval Herb Garden](https://www.english-heritage.org.uk/visit/inspire-me/blog/blog-posts/grow-medieval-herb-garden/)
- [Medievalists.net - Monastery Gardens](https://www.medievalists.net/2025/03/what-grew-medieval-monastery-garden/)
- [Carrément Belle - Perfume Middle Ages](https://carrementbelle.com/blog/en/2019/10/02/perfume-middle-ages/)

### Identification Table

| Folio | Best Guess | Conf | 2nd Choice | Peak Month | Season |
|-------|------------|------|------------|------------|--------|
| f2r | Angelica | MED | Lovage | July | SUMMER |
| f3v | Globe Thistle | MED | Sea Holly | Aug | SUMMER |
| f5r | **Violet** | HIGH | Cyclamen | Apr | EARLY_SPRING |
| f5v | **Geranium** | HIGH | Herb Robert | June | LATE_SPRING |
| f9r | **Fennel** | HIGH | Dill | July | SUMMER |
| f9v | **Larkspur** | HIGH | Aconite | June | LATE_SPRING |
| f11r | **Lavender** | HIGH | Thyme | July | SUMMER |
| f11v | **Bay Laurel** | HIGH | Myrtle | May | LATE_SPRING |
| f17r | **Borage** | HIGH | Comfrey | July | SUMMER |
| f18r | Nigella | MED | Carrot family | June | LATE_SPRING |
| f19r | **Dill** | HIGH | Fennel | July | SUMMER |
| f21r | Valerian | MED | Primrose | June | LATE_SPRING |
| f22r | Speedwell | MED | Germander | June | LATE_SPRING |
| f22v | **Chicory** | HIGH | Borage | July | SUMMER |
| f24v | Hemp | MED | Mallow | Aug | SUMMER |
| f25r | **Mallow** | HIGH | Ground Ivy | July | SUMMER |
| f29v | Solomon's Seal | MED | Lily of Valley | May | LATE_SPRING |
| f30v | **Juniper** | HIGH | Cypress | Oct | AUTUMN |
| f32v | Clary Sage | MED | Woad | July | SUMMER |
| f35v | Cranesbill | MED | Potentilla | June | LATE_SPRING |
| f36r | Tansy | MED | Feverfew | Aug | SUMMER |
| f37v | **Myrtle** | HIGH | Bay Laurel | June | LATE_SPRING |
| f38r | **Iris/Orris** | V.HIGH | Flag Iris | May | LATE_SPRING |
| f38v | **Sage** | HIGH | Lemon Balm | June | LATE_SPRING |
| f42r | Elecampane | MED | Comfrey | Aug | SUMMER |
| f45v | **Cardoon** | HIGH | Thistle | Aug | SUMMER |
| f47v | Ground Ivy | MED | Ivy | May | LATE_SPRING |
| f49v | **Cornflower** | HIGH | Knapweed | July | SUMMER |
| f51v | Blessed Thistle | MED | Milk Thistle | Aug | SUMMER |
| f56r | Germander | MED | Scullcap | July | SUMMER |

**HIGH confidence**: 17/30 (57%)
**Notable identifications**: f38r (Iris/Orris) = VERY HIGH confidence based on unmistakable rhizome morphology

---

## Section 2 - Finer Seasonal Distribution

### Bimonthly Bins

| Season | Count | % |
|--------|-------|---|
| EARLY_SPRING (Mar-Apr) | 1 | 3.3% |
| LATE_SPRING (May-Jun) | 12 | 40.0% |
| SUMMER (Jul-Aug) | 16 | 53.3% |
| AUTUMN (Sep-Oct) | 1 | 3.3% |
| WINTER (Nov-Feb) | 0 | 0.0% |

### Monthly Distribution

| Month | Count | Plants |
|-------|-------|--------|
| April | 1 | Violet |
| May | 4 | Bay Laurel, Solomon's Seal, Iris, Ground Ivy |
| June | 8 | Geranium, Larkspur, Nigella, Valerian, Speedwell, Cranesbill, Myrtle, Sage |
| July | 10 | Angelica, Fennel, Lavender, Borage, Dill, Chicory, Mallow, Clary Sage, Cornflower, Germander |
| August | 6 | Globe Thistle, Hemp, Tansy, Elecampane, Cardoon, Blessed Thistle |
| October | 1 | Juniper |

**Peak concentration: May-August (93.3%)**
**Single month peak: July (33%)**

---

## Section 3 - Ordering Tests (Finer Bins)

### A. Adjacency Bias Test

| Metric | Value |
|--------|-------|
| Observed adjacency rate | 0.931 |
| Null mean (shuffled) | 0.934 |
| Effect size (Cohen's d) | -0.075 |
| p-value | 1.0000 |
| **Verdict** | NOT SIGNIFICANT |

### B. Monotonic Drift Test

| Metric | Value |
|--------|-------|
| Observed Spearman rho | 0.170 |
| Null mean | -0.001 |
| Effect size (Cohen's d) | 0.922 |
| p-value | 0.3718 |
| **Verdict** | NO DRIFT |

Note: Positive rho (0.17) suggests weak early-to-late trend, but not statistically significant.

### C. Clustering Test

| Metric | Value |
|--------|-------|
| Number of clusters | 21 |
| Max cluster size | 3 |
| Null mean max size | 4.65 |
| Effect size (Cohen's d) | -1.232 |
| p-value | 0.3578 |
| **Verdict** | NOT SIGNIFICANT |

**Critical finding**: Observed clustering is LESS than random expectation (d = -1.23).

### Summary

| Test | Observed | Null | p-value | Effect d |
|------|----------|------|---------|----------|
| Adjacency (bimonthly) | 0.931 | 0.934 | 1.0000 | -0.08 |
| Monotonic Drift (monthly) | 0.170 | -0.001 | 0.3718 | 0.92 |
| Max Cluster (bimonthly) | 3.0 | 4.65 | 0.3578 | -1.23 |

**Tests with p < 0.05: 0/3**

---

## Section 4 - Outcome Classification

### Outcome: **NO_ORDERING_SIGNAL**

Even with:
- Speculative plant identification
- Finer bimonthly seasonal bins
- Monthly resolution for drift analysis

The botanical folio ordering **does not differ significantly from random** with respect to seasonal timing.

### Key Finding: Concentration Without Ordering

The analysis reveals:
- **93% of plants concentrated in May-August** (aromatic flowering season)
- **NO sequential ordering** (early→late or vice versa)
- **LESS clustering than random** (folios actively interleave seasonal types)

This pattern is consistent with:
- **Material selection**: Documenting peak-season aromatics, not year-round harvest
- **Non-instructional organization**: No calendar logic to the sequence
- **Possibly deliberate mixing**: Avoiding seasonal clustering (organizational choice?)

---

## Section 5 - Interpretation Boundary

This analysis tests only whether plant illustration ordering differs from random with respect to finer-grained seasonal timing.

**It does NOT imply:**
- Harvest calendar
- Recipe ingredients
- Instructional sequence
- Correspondence with executable text
- Species-level identification (all IDs are speculative)

**Even if patterns existed, they might reflect:**
- Material availability during manuscript production
- Copying order from an exemplar
- Organizational convenience
- Coincidence

**TIER ASSIGNMENT:** Tier 4 (SPECULATIVE)

---

## Section 6 - Comparison with EXT-SEQ-01 (Coarse Analysis)

| Aspect | EXT-SEQ-01 (Coarse) | EXT-SEQ-01B (Fine) |
|--------|---------------------|---------------------|
| Bins | 3 seasonal | 5 bimonthly |
| Resolution | Season level | Month level |
| Adjacency p | 1.0000 | 1.0000 |
| Drift p | 0.6960 | 0.3718 |
| Cluster p | 0.7498 | 0.3578 |
| Outcome | NO_ORDERING_SIGNAL | NO_ORDERING_SIGNAL |

Finer resolution did not reveal hidden patterns. Both analyses converge on the same conclusion.

---

## Files

- `ext_seq_01.py` — Original coarse analysis
- `speculative_plant_identifications.py` — Finer-grained analysis with speculative IDs
- `EXT_SEQ_01_REPORT.md` — Original report
- `EXT_SEQ_01B_SPECULATIVE_REPORT.md` — This report (speculative)

---

*EXT-SEQ-01B COMPLETE. No seasonal ordering signal detected even with finer resolution. The botanical section documents peak-season aromatics without calendar organization.*
