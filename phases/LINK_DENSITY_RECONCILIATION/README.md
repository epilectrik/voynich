# LINK_DENSITY_RECONCILIATION

**Status:** COMPLETE | **Date:** 2026-01-26 | **Constraints:** C609

## Purpose

Resolve the discrepancy between the documented LINK density figures: "Currier B: 6.6%" and "Overall B text: 38% (weighted by folio)" in link_metrics.md. Neither figure is reproducible from the canonical transcript using the canonical LINK definition (`'ol' in word`).

## Scripts

| Script | Purpose |
|--------|---------|
| `link_density_audit.py` | All 5 sections: token census, folio distribution, line coverage, ICC cross-classification, reconciliation |
| `link_zone_test.py` | Supplementary: proximity zone interpretation test |

## Key Findings

### True LINK Density: 13.2%

Token-level LINK density (`'ol' in word`) in Currier B is 3,047/23,096 = **13.2%**. This is neither 6.6% nor 38%.

### Section Densities Match C334

| Section | Measured | C334 |
|---------|----------|------|
| B | 20.2% | 19.6% |
| H | 9.3% | 9.1% |
| C | 11.6% | 10.1% |
| S | 10.3% | 9.8% |

### 38% Not Reproducible

No aggregation method matches:
- Token-level: 13.2%
- Folio mean: 12.5% (max folio: 30.0%)
- Line coverage: 68.6%
- Proximity zone d=1: 31.1%, d=2: 43.0%

### LINK Cuts Across All ICC Roles

| Role | % of LINK |
|------|-----------|
| UN | 38.3% |
| AX | 26.2% |
| EN | 19.0% |
| CC | 13.8% |
| FQ | 2.3% |
| FL | 0.3% |

57.3% of all CC tokens are LINK (class 11 = standalone `ol`).

## Constraints Produced

| # | Name | Key Evidence |
|---|------|-------------|
| C609 | LINK Density Reconciliation | True density 13.2%; legacy 6.6% and 38% unreproducible |

## Data Dependencies

| File | Source |
|------|--------|
| class_token_map.json | CLASS_COSURVIVAL_TEST |
| voynich.py | scripts/ |

## Verification

- Total B tokens: 23,096 (H-track, excl. labels/uncertain)
- LINK tokens: 3,047
- B folios: 82
- B lines: 2,420
- Section densities: within 1.5pp of C334 values
