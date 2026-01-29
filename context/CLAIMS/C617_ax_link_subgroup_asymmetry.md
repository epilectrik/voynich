# C617: AX-LINK Subgroup Asymmetry

**Tier:** 2 | **Status:** CLOSED | **Scope:** CURRIER_B | **Source:** AX_BEHAVIORAL_UNPACKING

## Statement

AX tokens carry LINK at 13.3% (matching overall B density of 13.2%), but this distributes asymmetrically across subgroups: AX_FINAL=35.3%, AX_INIT=19.4%, AX_MED=3.3%. LINK concentrates at AX boundary positions (FINAL, INIT), not interior (MED). AX and LINK co-occur non-randomly at line level (chi2=16.21, p<0.001). Folio-level AX proportion does not predict LINK density (rho=+0.144, p=0.198).

## Evidence

### AX LINK Rates by Subgroup

| Subgroup | LINK tokens | Total | LINK rate | vs B average (13.2%) |
|----------|-------------|-------|-----------|---------------------|
| AX_INIT | 232 | 1,195 | 19.4% | 1.5x |
| AX_MED | 67 | 2,056 | 3.3% | 0.25x |
| AX_FINAL | 212 | 601 | 35.3% | 2.7x |
| **All AX** | **511** | **3,852** | **13.3%** | **1.0x** |

The asymmetry is extreme: AX_FINAL is 10.7x the LINK rate of AX_MED.

### LINK Proximity by Subgroup

| Subgroup | Mean distance to LINK | Median | % with LINK in line |
|----------|----------------------|--------|---------------------|
| AX_INIT | 2.47 | 2.0 | 73.6% |
| AX_MED | 2.99 | 2.0 | 66.5% |
| AX_FINAL | 2.01 | 1.0 | 80.9% |

AX_FINAL tokens are closest to LINK tokens (mean 2.01, median 1.0) because they often ARE LINK tokens.

### Line-Level Co-occurrence

| Combination | Lines | % |
|-------------|-------|---|
| AX + LINK | 1,383 | 57.1% |
| AX only | 580 | 24.0% |
| LINK only | 277 | 11.4% |
| Neither | 180 | 7.4% |

Chi-squared: chi2=16.21, p=0.000057. AX and LINK are positively associated at line level.

### Folio-Level Correlation

Spearman rho=+0.144, p=0.198. No significant folio-level coupling between AX proportion and LINK density. The association is structural (subgroup-internal), not distributional (folio-level).

## Interpretation

The LINK morpheme (`ol` substring) concentrates in AX boundary positions because AX_INIT and AX_FINAL prefixes include `ol`-containing forms (e.g., `ol`, `lol`). This is a morphological rather than functional association: LINK status is determined by substring presence, and certain AX prefixes naturally contain `ol`. AX_MED prefixes rarely contain `ol`, producing the 3.3% rate.

This supports C609's finding that LINK cuts across all ICC roles as a morphological property, not a role-specific function.

## Related

C563, C609, C614, C616

## Method

LINK detection: `'ol' in word` (C609 standard). Chi-squared for line-level co-occurrence. Spearman for folio-level correlation. LINK proximity: minimum absolute position distance to nearest LINK token in same line.
