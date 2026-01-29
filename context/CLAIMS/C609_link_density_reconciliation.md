# C609: LINK Density Reconciliation

**Tier:** 2 (STRUCTURAL INFERENCE)
**Status:** CLOSED
**Source:** Phase LINK_DENSITY_RECONCILIATION
**Scope:** B_INTERNAL | LINK | METRICS

## Statement

Token-level LINK density (`'ol' in word`) in Currier B is **13.2%** (3,047/23,096 tokens). The documented figures of "6.6%" and "38% weighted by folio" in link_metrics.md are **not reproducible** from the canonical transcript (H-track) using the canonical LINK definition. No aggregation method (token-level, folio mean, line coverage, line mean, proximity zone) reproduces either legacy figure. Both should be treated as superseded.

## Evidence

### Token-Level Census

| Metric | Value |
|--------|-------|
| Total B tokens (H-track, excl. labels/uncertain) | 23,096 |
| LINK tokens (`'ol' in word`) | 3,047 |
| Token-level density | **13.2%** |
| Unique LINK types | 801 |
| Most common: standalone `ol` | 421 (13.8% of LINK) |

### Section Densities (C334 Verification)

| Section | Measured | C334 Reference |
|---------|----------|---------------|
| B (Biological) | 20.2% | 19.6% |
| H (Herbal-B) | 9.3% | 9.1% |
| C | 11.6% | 10.1% |
| S (Stars) | 10.3% | 9.8% |
| T | 11.0% | --- |

All section densities match C334 within measurement noise. Section B remains the highest at ~20%. No section approaches 38%.

### Folio-Level Distribution

| Statistic | Value |
|-----------|-------|
| B folios | 82 |
| Mean folio density | 12.5% |
| Median folio density | 11.0% |
| Std | 6.2% |
| Min | 1.0% |
| **Max** | **30.0%** |
| Folios with >=1 LINK | 100% (82/82) |
| Folios > 20% density | 14.6% (12 folios) |
| Folios > 30% density | 0% (0 folios) |

Mean of per-folio densities is 12.5%, not 38%. No folio exceeds 30%.

### Line-Level Coverage

| Metric | Value |
|--------|-------|
| Total B lines | 2,420 |
| Lines with >=1 LINK | 1,660 (68.6%) |
| Mean line density | 13.6% |
| Mean density (LINK lines only) | 19.9% |

Line coverage is 68.6%, not 38%.

### Proximity Zone Test

| Zone radius | % tokens in zone |
|-------------|-----------------|
| d=0 (LINK only) | 13.2% |
| d=1 | 31.1% |
| d=2 | 43.0% |
| d=3 | 51.2% |

The 38% figure falls between d=1 (31.1%) and d=2 (43.0%) but matches neither.

### LINK-ICC Cross-Classification

LINK tokens distribute across all 5 ICC roles:

| Role | LINK count | % of LINK | % of role |
|------|-----------|-----------|-----------|
| AX | 799 | 26.2% | 19.3% |
| EN | 578 | 19.0% | 8.0% |
| CC | 421 | 13.8% | 57.3% |
| FQ | 71 | 2.3% | 2.5% |
| FL | 10 | 0.3% | 0.9% |
| UN | 1,168 | 38.3% | 16.6% |

Class 11 (standalone `ol`) = 421 tokens, the only ICC class that IS the LINK token itself. All other LINK tokens are members of other classes that happen to contain 'ol'.

### Morphological Position of 'ol'

| Position | Count | % of LINK |
|----------|-------|-----------|
| MIDDLE | 1,254 | 41.2% |
| PREFIX | 875 | 28.7% |
| SPAN (cross-boundary) | 579 | 19.0% |
| SUFFIX | 377 | 12.4% |

## Reconciliation Verdict

| Candidate metric | Value | Distance from 38% |
|-----------------|-------|-------------------|
| Token-level | 13.2% | 24.8pp |
| Folio mean | 12.5% | 25.5pp |
| Folio median | 11.0% | 27.0pp |
| Line coverage | 68.6% | 30.6pp |
| Line mean density | 13.6% | 24.4pp |

**No measurement reproduces 38%.** The legacy figure appears to originate from an early analysis with undocumented methodology and has propagated through the documentation without verification. The 6.6% figure in link_metrics.md is similarly unreproducible (closest candidate: 13.2% token-level).

## Corrective Action

1. `link_metrics.md` "Currier B: 6.6%" should be corrected to **13.2%**
2. `link_metrics.md` "Overall B text: 38% (weighted by folio)" should be corrected to **13.2% (token-level)** or **12.5% (folio mean)**
3. CLAUDE_INDEX.md "LINK operator (38% of text = deliberate waiting)" should be corrected to reflect actual density
4. Section B (Biological) has genuinely elevated LINK density at 20.2%, consistent with C334

## Related

- C334 (LINK by section - densities confirmed within noise)
- C340 (LINK-escalation complementarity)
- C359 (LINK at boundaries)
- C365 (LINK spatial uniformity)
- C366 (LINK context)
- C377 (LINK morphological property)
