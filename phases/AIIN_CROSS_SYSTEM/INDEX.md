# AIIN_CROSS_SYSTEM — Phase 632

**Status:** COMPLETE
**Date:** 2026-04-01
**Verdict:** DUAL_LAYER_ARCHITECTURE (C1909-C1916)

## Purpose
Cross-system investigation of the aiin/daiin token family — the manuscript's most frequent token — at atom level across Currier A, Currier B, and AZC.

## Key Findings

1. **aiin absolute line-initial exclusion** (C1909): 0/469 across all three systems. Hard structural constraint, construction-layer.
2. **n-terminal lock is cross-system** (C1910): A=93.7%, B=94.7%, AZC=83.3%. Safety mechanism morphologically encoded at construction layer.
3. **HEAD anatomy diverges across systems** (C1911): a-HEAD rate for ii-tokens: A=19.2%, B=35.9%, AZC=36.0%. HEAD selection is execution-layer.
4. **ii/ee complementary domains cross-system** (C1912): a-HEAD uses ii, e-HEAD uses ee, in all systems. Two-strategy safety architecture is construction-layer.
5. **C1908 driven by aiin-family** (C1913): Summer+Winter vs Spring+Autumn aiin rate: p=0.0033. Seasonal i/d swap is specifically aiin vs ody.
6. **daiin anti-correlates with thermal complexity** (C1914): Folio-level rho=-0.324, p=0.0004. daiin is infrastructure alongside simpler content.
7. **AZC daiin-aiin co-occurrence attraction** (C1915): OR=5.04, p=0.003. Co-occur 3.3x more than expected in AZC only.
8. **Section-conditioned family composition** (C1916): Headed/headless ratio within aiin-family differs by section in A (p=0.003) and B (p<0.0001).

## Interpretation
The aiin/daiin family has dual-layer architecture. Terminal safety (n-lock) and domain complementarity (ii/ee) are construction-layer — morphologically hardwired. HEAD selection and positional grammar are execution-layer — system-specific. The notation enforces that iteration tokens always resolve to safe containment.

## Scripts
| Script | Purpose | Runtime |
|--------|---------|---------|
| s1_aiin_family_census.py | Full inventory across A/B/AZC with atom profiles | ~15s |
| s2_daiin_vs_aiin_split.py | Positional complementarity, co-occurrence, paragraph role | ~20s |
| s3_bigram_context.py | Predecessor/successor analysis, conditional entropy, wind-down chain | ~20s |
| s4_safety_architecture.py | ii-extension safety routing per system, ii/ee complementarity | ~30s |
| s5_seasonal_thermal.py | C1908 decomposition, thermal cluster correlation, section fingerprint | ~20s |

## Results
All in `results/` — JSON outputs from each script.
