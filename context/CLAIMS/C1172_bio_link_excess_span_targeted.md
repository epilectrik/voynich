# C1172: BIO LINK Excess Is SPAN-Targeted

**Tier:** 2
**Scope:** B, BIO, LINK, section
**Phase:** LINK_FUNCTIONAL_ARCHITECTURE (Phase 418)
**Depends on:** C334, C609, C1170

## Statement

Section B (BIO) has 2× average LINK density (20.2% vs ~10% in other sections), confirming C334. This excess is NOT uniformly distributed across role × ol_position cells. BIO enrichment is targeted at SPAN-position tokens where `ol` crosses morphological boundaries: EN_SPAN (4.65×), AX_SPAN (2.15×), UN_SPAN (1.88×). MIDDLE-position LINK tokens are actually DEPLETED in BIO (EN_MIDDLE 0.47×, AX_MIDDLE 0.48×, UN_MIDDLE 0.46×). Section × role composition chi-square: chi2=82.2, p<1e-9. Enrichment CV=0.817 (high heterogeneity).

## Evidence

### Section Densities
| Section | Total | LINK | Density |
|---------|-------|------|---------|
| B (BIO) | 6,850 | 1,385 | 20.2% |
| C | 1,480 | 172 | 11.6% |
| H | 2,611 | 251 | 9.6% |
| S | 10,671 | 1,099 | 10.3% |
| T | 662 | 73 | 11.0% |

### BIO Enrichment by Role × ol_position
| Cell | BIO count | non-BIO count | Enrichment |
|------|-----------|---------------|------------|
| EN_SPAN | 117 | 29 | **4.65×** |
| AX_SPAN | 101 | 54 | **2.15×** |
| UN_SPAN | 175 | 107 | **1.88×** |
| FL_MIDDLE | 6 | 4 | 1.73× |
| AX_SUFFIX | 38 | 27 | 1.62× |
| CC_MIDDLE | 233 | 184 | 1.46× |
| AX_PREFIX | 253 | 208 | 1.40× |
| EN_SUFFIX | 39 | 62 | 0.72× |
| UN_PREFIX | 143 | 242 | 0.68× |
| UN_SUFFIX | 52 | 120 | 0.50× |
| FQ_MIDDLE | 21 | 50 | 0.48× |
| AX_MIDDLE | 29 | 69 | 0.48× |
| EN_MIDDLE | 94 | 228 | 0.47× |
| UN_MIDDLE | 84 | 211 | 0.46× |

### Section × Role Composition
| Metric | Value |
|--------|-------|
| Chi-square | 82.2 |
| p-value | 1.65e-9 |
| Enrichment CV | 0.817 |

## Interpretation

BIO's LINK excess is concentrated in morphological SPAN tokens — tokens where the `ol` substring crosses the boundary between morphological components (e.g., PREFIX-MIDDLE or MIDDLE-SUFFIX). This is a composition shift, not a uniform frequency modulation. BIO programs specifically overuse boundary-crossing `ol` morphologies while depleting simple MIDDLE-positioned `ol` tokens. This is consistent with BIO using more morphologically complex `ol`-containing words rather than simply using more LINK tokens of all types.

## Provenance

- Phase 418 Test 3: LINK_SECTION_DECOMPOSITION
- Script: `phases/LINK_FUNCTIONAL_ARCHITECTURE/scripts/link_functional_architecture.py`
- Results: `phases/LINK_FUNCTIONAL_ARCHITECTURE/results/link_functional_architecture.json` → test3_section_decomposition
